#!/usr/bin/env python3
"""gen_ipl_tb.py -- the testbench for ../decks/ipl_boot.strap: boot the
model from a tape image, with nothing pre-loaded into core storage.

docs/boot_plan.md M1's exit test.  The harness loads ONLY the tape
device, then calls core.iplStart() -- Reference Manual printed p.126's
INITIAL PROGRAM LOAD key plus the channel signal -- and lets the
machine fetch its own program.

THE TAPE IMAGE IS BUILT THE SAME WAY mktape.py BUILDS A FILE, from the
same function, so this testbench and the on-disk image format cannot
drift apart: one control word, then the program's words, no tape mark
and no label (ka_ul1).

WHY NOTHING IS PRE-LOADED.  gen_tb.generate(ipl=True) suppresses the
program-word load rule entirely.  If it did not, every check below
would pass even with the IPL read moving nothing -- the point is that
core storage starts at zero and the tape fills it.
"""
import sys

from gen_tb import generate
from mktape import pack_control_word
from strap_asm import assemble, AssemblerError

PROGRAM = "../decks/ipl_boot.strap"


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} ModuleName", file=sys.stderr)
        sys.exit(1)
    module_name = sys.argv[1]

    try:
        prog = assemble(open(PROGRAM).read())
    except AssemblerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    lo, hi = min(prog.words), max(prog.words)
    count = hi - lo + 1
    body = [prog.words.get(a, 0) for a in range(lo, hi + 1)]
    # Word 0 of the tape IS a control word: p.126's fixed word reads
    # exactly one word into location 4 and then refills FROM location
    # 4, so the first thing off the tape becomes the control word that
    # loads everything else.
    tape_image = [pack_control_word(lo, count, refill=1)] + body

    assert len(tape_image) <= 16, (
        f"tape image is {len(tape_image)} words; StretchIO's TapeWords "
        f"is 16 (boot_plan.md M0 step 2 widens it)")

    result = prog.symtab["RESULT"] // 64
    entry = prog.symtab["IPLBS"] // 64
    halt_pc = prog.symtab["HALT"] // 32   # half-word address

    # WHAT "LVI, $X1, 1234" ACTUALLY LEAVES IN THE INDEX WORD, because
    # the first draft of this file got it wrong and the test caught it.
    # STRAP's bare operand there is a HALF-WORD ADDRESS, and an index
    # word's value field (IBM bits 0-23, i.e. w[63:40]) holds a BIT
    # address -- so 1234 half-words is 1234 * 32 = 39,488 bits, and SX
    # stores 0x9a400000000000.  Expecting a plain 1234 was a
    # misreading of the assembler's convention, not a model fault:
    # every other check in this file passed on that run, including
    # both loaded-word checks and the halt PC.
    LVI_HALFWORDS = 1234
    expect_result = (LVI_HALFWORDS * 32) << 40

    checks = [
        # The program ran: it put its value where it said it would.
        # This is the end-to-end check -- it can only pass if the tape
        # was read, the chain refilled, the words landed in core, and
        # the CPU started at the right place.
        ("ipl_program_executed", str(result), expect_result),
        # The tape actually wrote core storage, at the address the
        # refilled control word named.  Distinguishes "the program ran
        # from somewhere" from "the program was loaded where p.126
        # says".
        ("ipl_loaded_entry_word", str(entry), prog.words[lo]),
        ("ipl_loaded_second_word", str(entry + 1), prog.words[lo + 1]),
    ]

    print(generate(module_name, prog, checks,
                   tape_image=tape_image,
                   pc_check=halt_pc,
                   # 237 measured: the fixed control word's one-word
                   # read, the refill from location 4, three more
                   # words, and four instructions.
                   cycle_bound=300,
                   step_cap=2000,
                   ipl=True))


if __name__ == "__main__":
    main()
