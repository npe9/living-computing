#!/usr/bin/env python3
"""gen_disk_tb.py -- driver for ../decks/io_disk.strap.

Same reason for existing as gen_tape_tb.py: the control words in the
.strap source are zero-initialized placeholders, patched here with
real dataAddr/count values, after which the expected results are
derived by walking the disk chapter's own rules.

NOTHING IS CHECKED THROUGH A DISK PEEK, and that is deliberate.  Every
assertion below is either a core-storage word the program read BACK
off the platter or a control word a COPY CONTROL WORD left in core.
A peek method would check that the model wrote what the model wrote;
a read-back checks that a WRITE and a READ agree about where an arc
starts, which is the thing the arc register exists to get right.

Usage: gen_disk_tb.py ModuleName > ../bsv/ModuleName.bsv
"""
import sys

from strap_asm import assemble, AssemblerError
from gen_tb import generate

PROGRAM = "../decks/io_disk.strap"


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

    ctlw = {n: word_addr(prog, f"CTLW{n}") for n in range(0, 7)}
    ccw = {c: word_addr(prog, f"CCW{c}") for c in "ABCDEFG"}
    src1 = word_addr(prog, "SRC1")
    src2 = word_addr(prog, "SRC2")
    dest1 = word_addr(prog, "DEST1")
    dest2 = word_addr(prog, "DEST2")
    dest3 = word_addr(prog, "DEST3")
    dest4 = word_addr(prog, "DEST4")
    src0 = word_addr(prog, "SRC0")

    # CTLW1 CARRIES FLAGS THE DISK MUST THROW AWAY.  Reference Manual
    # printed p.158: "No use is made of control word flag bits or
    # refill field and they are discarded... Only the data word
    # address field and word count field of the control word are
    # retained and used by the disk synchronizer."  On the Exchange
    # this exact control word would CHAIN -- count reaches zero with
    # chain set, Figure 36's "Chain and continue" row -- and refill
    # from CTLW2, transferring twice.  On the disk it must transfer
    # once and CCWA must come back with all four fields zero.
    prog.words[ctlw[1]] = pack_cw(dataAddr=src1, count=3,
                                  chain=1, multiple=1, skip=1,
                                  refill=ctlw[2])
    prog.words[ctlw[2]] = pack_cw(dataAddr=src2, count=2)
    prog.words[ctlw[3]] = pack_cw(dataAddr=dest1, count=5)
    prog.words[ctlw[4]] = pack_cw(dataAddr=dest2, count=4)
    prog.words[ctlw[5]] = pack_cw(dataAddr=dest3, count=1)
    prog.words[ctlw[6]] = pack_cw(dataAddr=dest4, count=3)
    prog.words[ctlw[0]] = pack_cw(dataAddr=src0, count=5)

    # ---- expected control words -----------------------------------
    # A disk transfer runs until the count reaches zero, full stop
    # (p.158: no chaining, no multiple, no skip), so each of these is
    # dataAddr advanced by the count and the count at zero.  eop is 1
    # because none of the four is a SEOP form; unitReady carries
    # through from the control word the program supplied.
    exp_ccwA = pack_cw(dataAddr=src1 + 3, eop=1, count=0)
    exp_ccwB = pack_cw(dataAddr=src2 + 2, eop=1, count=0)
    exp_ccwC = pack_cw(dataAddr=dest1 + 5, eop=1, count=0)
    exp_ccwD = pack_cw(dataAddr=dest2 + 4, eop=1, count=0)
    # ---- steps 6-7: the LOCATE arm's own copy of the SEOP rule ----
    # The RD(SEOP) adopts a control word whose eop is 0 and suppresses
    # the one it would otherwise set, so the word ends with eop 0 and
    # seop cleared at completion.  A LOC(SEOP) then must leave it
    # alone, and a plain LOC must turn eop on and change nothing else
    # -- LOCATE's right effective address is an arc, not a
    # control-word address (p.160), so dataAddr and count carry
    # forward exactly as they do across a tape CTL.
    exp_ccwE = pack_cw(dataAddr=dest3 + 1, eop=0, count=0)
    exp_ccwF = pack_cw(dataAddr=dest3 + 1, eop=1, count=0)
    # ---- step 8: End Exception, nothing transferred ---------------
    # "the unit runs out of material" (printed p.121).  The arc is
    # past the end of the source, so the FIRST word already fails the
    # capacity test and the control word is whatever the program
    # supplied, with ee and eop added: dataAddr not advanced, count
    # not decremented.
    exp_ccwG = pack_cw(dataAddr=dest4, count=3, ee=1, eop=1)

    D = [0xD15C0001, 0xD15C0002, 0xD15C0003]
    E = [0xD15C1001, 0xD15C1002]

    checks = [
        # ---- step 4: arc 0 read back ----
        # The first three prove LOCATE+WRITE and LOCATE+READ agree
        # about where arc 0 begins.  A model carrying a word position
        # forward like a tape would return the wrong words here.
        ("DISK_arc0_word0", str(dest1 + 0), D[0]),
        ("DISK_arc0_word1", str(dest1 + 1), D[1]),
        ("DISK_arc0_word2", str(dest1 + 2), D[2]),
        # The next two are the zero-filled tail of the short write
        # (p.160), AND THEY DISCRIMINATE because of step 0: arc 0 was
        # written with FIVE words of 0xBAD0000n before the three-word
        # write, so a fill that never ran leaves 0xBAD00004 and
        # 0xBAD00005 here.  (DEST1 is also pre-filled with all-ones in
        # the deck, which catches the other failure -- a transfer that
        # moved nothing at all.)
        ("DISK_arc0_fill3", str(dest1 + 3), 0),
        ("DISK_arc0_fill4", str(dest1 + 4), 0),
        # ---- step 5: arc 1, reached without a LOCATE ----
        # These are the ones that prove the arc address register
        # advanced by itself when arc 0 completed (p.161).  Step 3's
        # WRITE named no arc.
        ("DISK_arc1_word0", str(dest2 + 0), E[0]),
        ("DISK_arc1_word1", str(dest2 + 1), E[1]),
        ("DISK_arc1_fill2", str(dest2 + 2), 0),
        ("DISK_arc1_fill3", str(dest2 + 3), 0),
        # ---- the control words ----
        ("DISK_CCWA_flags_discarded", str(ccw["A"]), exp_ccwA),
        ("DISK_CCWB", str(ccw["B"]), exp_ccwB),
        ("DISK_CCWC", str(ccw["C"]), exp_ccwC),
        ("DISK_CCWD", str(ccw["D"]), exp_ccwD),
        # ---- the LOCATE arm's SEOP rule, both ways ----
        # DEST3 reads arc 1 word 0 again: step 5's four-word READ left
        # the arc register on arc 1, because reading four words of a
        # 512-word arc does not complete it (p.161).
        ("DISK_seop_reread", str(dest3), E[0]),
        ("DISK_CCWE_locseop_leaves_eop", str(ccw["E"]), exp_ccwE),
        ("DISK_CCWF_plain_loc_sets_eop", str(ccw["F"]), exp_ccwF),
        # ---- step 8: End Exception ----
        # DEST4 keeps the all-ones the deck loaded it with: the
        # transfer never moved a word.
        ("DISK_EE_dest_untouched", str(dest4), 0xFFFFFFFFFFFFFFFF),
        ("DISK_CCWG_end_exception", str(ccw["G"]), exp_ccwG),
    ]

    # A WRITE costs its count plus the zero-filled remainder of its
    # arc -- 512 cycles per short write here -- so the cap has to
    # clear roughly 1,100 transfer cycles on top of the program.
    print(generate(module_name, prog, checks, step_cap=20000))


if __name__ == "__main__":
    main()
