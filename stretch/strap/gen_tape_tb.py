#!/usr/bin/env python3
"""gen_tape_tb.py -- driver for programs/io_tape.strap.

Same reason for existing as strap/gen_io_tb.py: this assembler's DD
statement can't resolve a label to a numeric address, so the tape
program's control words are zero-initialized placeholders in the
.strap source, patched here with real dataAddr/count values computed
in Python (pack_cw mirrors StretchTypes.bsv's packControlWord
field-for-field), after which the expected-result derivation follows
the exact position transitions io_tape.strap's own header comment
walks through step by step.

Usage: gen_tape_tb.py ModuleName > ../bsv/ModuleName.bsv
"""
import sys

from strap_asm import assemble, AssemblerError
from gen_tb import generate

PROGRAM = "programs/io_tape.strap"

# StretchIO.bsv: chanTape=34. Reference Manual p.111: the 7-bit channel
# number occupies instruction bits 12-18 of the 24-bit channel-address
# field -- see io_tape.strap's own header for the full derivation.
CHAN_TAPE_SCALED = 34 << 5  # 1088

TAPE_WORDS = 16  # StretchIO.bsv's TapeWords -- deliberately small, see
                  # its file header.

# A recognizable pattern distinct from io_reader_printer.strap's own
# reader image, so a check failure's actual value makes it obvious
# which device supplied it. "7A9E" evokes "tape".
TAPE_IMAGE = [0x7A9E0000 + i for i in range(TAPE_WORDS)]


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

    block1 = word_addr(prog, "BLOCK1")
    block2 = word_addr(prog, "BLOCK2")
    block3 = word_addr(prog, "BLOCK3")
    block4 = word_addr(prog, "BLOCK4")
    src_addr = word_addr(prog, "SRC")
    dest_ee = word_addr(prog, "DEST_EE")
    ctlw = {n: word_addr(prog, f"CTLW{n}") for n in range(1, 7)}
    ccw = {c: word_addr(prog, f"CCW{c}") for c in "ABCDEFGHIJ"}

    # Patch the six input control words with their real dataAddr/count
    # -- see io_tape.strap's header for what each step is testing.
    prog.words[ctlw[1]] = pack_cw(dataAddr=block1, count=4)
    prog.words[ctlw[2]] = pack_cw(dataAddr=block2, count=4)
    prog.words[ctlw[3]] = pack_cw(dataAddr=src_addr, count=2)
    prog.words[ctlw[4]] = pack_cw(dataAddr=block3, count=2)
    prog.words[ctlw[5]] = pack_cw(dataAddr=block4, count=1)
    prog.words[ctlw[6]] = pack_cw(dataAddr=dest_ee, count=20)

    # Expected control-word values, derived by walking the exact same
    # position transitions io_tape.strap's header comment describes.
    # Position starts at 0.
    exp_ccwA = pack_cw(dataAddr=block1 + 4, unitReady=1, eop=1, count=0)
    # position: 0 -> 4
    exp_ccwB = pack_cw(dataAddr=block2 + 4, unitReady=1, eop=1, count=0)
    # position: 4 -> 8
    exp_ccwC = pack_cw(dataAddr=src_addr + 2, unitReady=1, eop=1, count=0)
    # position: 8 -> 10
    # REWIND touches only eop (already 1 from CCWC) -- dataAddr/count
    # are NOT control-word-address fields for CTL, so they carry
    # forward unchanged from whatever RD/W last set them to. The real
    # proof REWIND worked is BLOCK3's content below, not this CW.
    exp_ccwD = pack_cw(dataAddr=src_addr + 2, unitReady=1, eop=1, count=0)
    # position: 10 -> 0 (REWIND)
    exp_ccwE = pack_cw(dataAddr=block3 + 2, unitReady=1, eop=1, count=0)
    # position: 0 -> 2
    # BACKSPACE BLOCK (position 2, nonzero): touches only eop (already
    # 1 from CCWE); dataAddr/count carry forward unchanged, same as CCWD.
    exp_ccwF = pack_cw(dataAddr=block3 + 2, unitReady=1, eop=1, count=0)
    # position: 2 -> 1 (BACKSPACE BLOCK)
    exp_ccwG = pack_cw(dataAddr=block4 + 1, unitReady=1, eop=1, count=0)
    # position: 1 -> 2
    # REWIND again: same "touches only eop" rule as CCWD/CCWF.
    exp_ccwH = pack_cw(dataAddr=block4 + 1, unitReady=1, eop=1, count=0)
    # position: 2 -> 0 (REWIND)
    # BACKSPACE BLOCK at position 0 (load point): Exchange Program
    # Check (p.136) -- epgk newly set, position stays 0. This IS a
    # genuinely distinguishing check (epgk=1 wasn't in any prior CW).
    exp_ccwI = pack_cw(dataAddr=block4 + 1, unitReady=1, epgk=1, eop=1, count=0)
    # position: 0 -> 0 (rejected)
    # RD count=20 against a 16-word tape, position 0: transfers exactly
    # TapeWords=16 words (dataAddr/count reflect that), then End
    # Exception on the 17th cycle -- ee newly set, epgk reset to 0
    # (this RD adopts a fresh control word, epgk defaults to 0), count
    # shows 20-16=4 words never transferred.
    exp_ccwJ = pack_cw(dataAddr=dest_ee + 16, unitReady=1, ee=1, eop=1, count=4)
    # position: 0 -> 16 (exhausted)

    checks = [
        ("BLOCK1_0", str(block1), TAPE_IMAGE[0]),
        ("BLOCK1_1", str(block1 + 1), TAPE_IMAGE[1]),
        ("BLOCK1_2", str(block1 + 2), TAPE_IMAGE[2]),
        ("BLOCK1_3", str(block1 + 3), TAPE_IMAGE[3]),
        # The core distinguishing test: BLOCK2 must be the NEXT 4
        # words, not BLOCK1 again -- proof tape position persisted
        # across two separate RD instructions.
        ("BLOCK2_0_position_persisted", str(block2), TAPE_IMAGE[4]),
        ("BLOCK2_1_position_persisted", str(block2 + 1), TAPE_IMAGE[5]),
        ("BLOCK2_2_position_persisted", str(block2 + 2), TAPE_IMAGE[6]),
        ("BLOCK2_3_position_persisted", str(block2 + 3), TAPE_IMAGE[7]),
        ("CCWA_after_RD1", str(ccw["A"]), exp_ccwA),
        ("CCWB_after_RD2", str(ccw["B"]), exp_ccwB),
        ("CCWC_after_W", str(ccw["C"]), exp_ccwC),
        ("CCWD_after_REWIND", str(ccw["D"]), exp_ccwD),
        # BLOCK3 must match the tape's ORIGINAL first 2 words -- proof
        # REWIND actually reset position to 0, not just set the CW's
        # EOP bit.
        ("BLOCK3_0_after_REWIND", str(block3), TAPE_IMAGE[0]),
        ("BLOCK3_1_after_REWIND", str(block3 + 1), TAPE_IMAGE[1]),
        ("CCWE_after_RD3", str(ccw["E"]), exp_ccwE),
        ("CCWF_after_BACKSPACE", str(ccw["F"]), exp_ccwF),
        # BLOCK4 must equal the tape's original word[1] -- proof
        # BACKSPACE BLOCK moved position back by exactly one (position
        # was 2 after BLOCK3's RD; backspaced to 1; this RD reads
        # index 1, the word BLOCK3 already read once before).
        ("BLOCK4_0_after_BACKSPACE", str(block4), TAPE_IMAGE[1]),
        ("CCWG_after_RD4", str(ccw["G"]), exp_ccwG),
        ("CCWH_after_REWIND2", str(ccw["H"]), exp_ccwH),
        ("CCWI_after_BACKSPACE_at_load_point_EPGK", str(ccw["I"]), exp_ccwI),
        ("CCWJ_after_EE", str(ccw["J"]), exp_ccwJ),
        # DEST_EE spot checks: first 8 words are the tape's original
        # content (never overwritten); words 8-9 are what the W step
        # wrote (999, 888) -- persisting through two REWINDs proves
        # REWIND only moves position, never touches tape content;
        # words 10-15 are original content again.
        ("DEST_EE_0", str(dest_ee), TAPE_IMAGE[0]),
        ("DEST_EE_7", str(dest_ee + 7), TAPE_IMAGE[7]),
        ("DEST_EE_8_write_persisted", str(dest_ee + 8), 999),
        ("DEST_EE_9_write_persisted", str(dest_ee + 9), 888),
        ("DEST_EE_15", str(dest_ee + 15), TAPE_IMAGE[15]),
    ]
    tape_checks = [
        # Direct proof the W step actually wrote tape content, decoupled
        # from the later EE test's transitive re-read of the same words.
        ("TAPE_8_direct_after_W", 8, 999),
        ("TAPE_9_direct_after_W", 9, 888),
    ]

    print(generate(module_name, prog, checks, tape_image=TAPE_IMAGE,
                    tape_checks=tape_checks))


if __name__ == '__main__':
    main()
