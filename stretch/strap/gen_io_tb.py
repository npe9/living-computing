#!/usr/bin/env python3
"""gen_io_tb.py -- driver for programs/io_reader_printer.strap.

This assembler's DD statement can't resolve a label to a numeric
address (parse_dd_literal only accepts decimal / (radix)digits, not
symbols -- see strap_asm.py), so a control word whose data-address
field must equal another label's own address (DEST, SRC) can't be
written directly in STRAP source here. This script assembles the
program with those control words as zero-initialized placeholders,
looks up the real addresses from the assembled symbol table, computes
the correctly packed control-word values in Python (pack_cw below,
which mirrors StretchTypes.bsv's packControlWord field-for-field), and
patches them into the assembled image before handing it to gen_tb.py --
the same "derive the expected result with a small Python script that
mirrors the hardware's own packing logic" approach already used for
Reference Manual Figure 7's expected memory contents (see
run_tests.sh).

Usage: gen_io_tb.py ModuleName > ../bsv/ModuleName.bsv
"""
import sys

from strap_asm import assemble, AssemblerError
from gen_tb import generate

PROGRAM = "programs/io_reader_printer.strap"

# StretchIO.bsv: chanReader=32, chanPrinter=33. Reference Manual p.111:
# the 7-bit channel number occupies instruction bits 12-18 of the
# 24-bit channel-address field, not its low bits -- see the .strap
# file's own header for the full derivation.
CHAN_READER_SCALED = 32 << 5   # 1024
CHAN_PRINTER_SCALED = 33 << 5  # 1056

READER_IMAGE = [0xAAAA1111, 0xBBBB2222, 0xCCCC3333]


def pack_cw(dataAddr, unitReady=1, epgk=0, uk=0, ee=0, eop=0, cs=0, seop=0,
            chain=0, multiple=0, skip=0, count=0, refill=0):
    """Mirrors StretchTypes.bsv's packControlWord exactly (Figure 35)."""
    v = (dataAddr & 0x3FFFF) << 46
    v |= (unitReady & 1) << 45
    v |= (epgk & 1) << 44
    v |= (uk & 1) << 43
    v |= (ee & 1) << 42
    v |= (eop & 1) << 41
    v |= (cs & 1) << 40
    v |= (seop & 1) << 39
    v |= (chain & 1) << 38
    v |= (multiple & 1) << 37
    v |= (skip & 1) << 36
    v |= (count & 0x3FFFF) << 18
    v |= (refill & 0x3FFFF)
    return v


def word_addr(prog, label):
    bits = prog.symtab[label]
    assert bits % 64 == 0, f"{label} is not word-aligned"
    return bits // 64


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} ModuleName", file=sys.stderr)
        sys.exit(1)
    module_name = sys.argv[1]

    with open(PROGRAM) as f:
        src = f.read()
    try:
        prog = assemble(src)
    except AssemblerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    dest = word_addr(prog, "DEST")
    src = word_addr(prog, "SRC")
    ctlw1 = word_addr(prog, "CTLW1")
    ctlw2 = word_addr(prog, "CTLW2")
    ccwa = word_addr(prog, "CCWA")
    ccwb = word_addr(prog, "CCWB")
    ccwc = word_addr(prog, "CCWC")
    ccwd = word_addr(prog, "CCWD")

    # Patch the two input control words with their real dataAddr/count.
    prog.words[ctlw1] = pack_cw(dataAddr=dest, count=3)
    prog.words[ctlw2] = pack_cw(dataAddr=src, count=2)

    # Expected results, derived from Reference Manual p.124's own
    # control-word-update rules -- READ: dataAddr=A_i+N, count=C_i-N;
    # this model's WRITE deviates from the manual's A_i+N+2 (no
    # double-buffer to reproduce -- see StretchIO.bsv) and instead also
    # uses A_i+N, count=C_i-N.
    exp_ccwa = pack_cw(dataAddr=dest + 3, unitReady=1, eop=1, count=0)
    exp_ccwb = pack_cw(dataAddr=src + 2, unitReady=1, eop=1, count=0)
    # Wrong-unit RD given to the printer (p.113): the printer's CW as of
    # CCWB (already eop=1), with epgk added.
    exp_ccwc = pack_cw(dataAddr=src + 2, unitReady=1, epgk=1, eop=1, count=0)
    # REL on the reader channel: same as CCWA -- REL resets only
    # epgk/uk/ee/cs/seop (already 0) and sets eop (already 1);
    # dataAddr/count/refill/chain/multiple/skip are untouched.
    exp_ccwd = exp_ccwa

    checks = [
        ("DEST0", str(dest), READER_IMAGE[0]),
        ("DEST1", str(dest + 1), READER_IMAGE[1]),
        ("DEST2", str(dest + 2), READER_IMAGE[2]),
        ("CCWA_after_RD", str(ccwa), exp_ccwa),
        ("CCWB_after_W", str(ccwb), exp_ccwb),
        ("CCWC_wrong_unit_EPGK", str(ccwc), exp_ccwc),
        ("CCWD_after_REL", str(ccwd), exp_ccwd),
        # ind_UNRJ (StretchTypes.bsv, indicator 7) is the only indicator
        # bit anything in this program touches -- the final RD to
        # channel 0 (no device installed) is the only reject in the
        # whole run. weight = 1 << (63-7) = 1 << 56.
        ("UNRJ_indicator", "11", 1 << 56),
    ]
    printer_checks = [
        ("PRINTER0", 0, 111),
        ("PRINTER1", 1, 222),
    ]

    print(generate(module_name, prog, checks, reader_image=READER_IMAGE,
                    printer_checks=printer_checks))


if __name__ == '__main__':
    main()
