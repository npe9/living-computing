#!/usr/bin/env python3
"""gen_ipl_file_tb.py -- boot from a tape image held in a HOST FILE,
with an image larger than the sixteen-word register tape.

docs/boot_plan.md M0 step 1 plus M1, together.  The difference from
gen_ipl_tb.py is what is NOT here: no tape_image= argument, because
the harness does not load the tape at all.  mkTapeSourceFile reads
$STRETCH_TAPE through BDPI, so the image arrives from disk exactly as
it will from an SD card later.

THE IMAGE IS WRITTEN BY mktape.py, not by this file, so the format
under test is the committed one rather than a copy of it.
"""
import os
import subprocess
import sys

from gen_tb import generate
from strap_asm import assemble, AssemblerError

# Resolved against this file's own location: mktape.py lives in
# ../strap/ and this generator is run from tests/, but a bare name
# here breaks the moment either moves (it did, on 2026-10-18).
MKTAPE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      os.pardir, "strap", "mktape.py")

PROGRAM = "../decks/ipl_boot_big.strap"


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

    out = os.environ.get("STRETCH_TAPE")
    if not out:
        print("error: set STRETCH_TAPE to the image path", file=sys.stderr)
        sys.exit(1)
    r = subprocess.run([sys.executable, MKTAPE, PROGRAM, out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    lo = min(prog.words)
    result = prog.symtab["RESULT"] // 64
    result2 = prog.symtab["RESULT2"] // 64
    marker = prog.symtab["MARKER"] // 64
    halt_pc = prog.symtab["HALT"] // 32

    # See gen_ipl_tb.py: STRAP's bare operand in LVI is a HALF-WORD
    # address and an index word's value field holds a BIT address.
    checks = [
        ("ipl_file_program_executed", str(result), (1234 * 32) << 40),
        ("ipl_file_second_store", str(result2), (4321 * 32) << 40),
        ("ipl_file_loaded_entry_word", str(lo), prog.words[lo]),
        # THE CEILING CHECK.  MARKER is word 18 of a 19-word image, so
        # it is past where a sixteen-word tape would have stopped.  A
        # path that silently truncated would fail here and nowhere
        # else -- every check above it would still pass.
        ("ipl_file_past_16_words", str(marker), prog.words[marker]),
    ]

    print(generate(module_name, prog, checks,
                   pc_check=halt_pc,
                   cycle_bound=1200,
                   step_cap=4000,
                   ipl=True))


if __name__ == "__main__":
    main()
