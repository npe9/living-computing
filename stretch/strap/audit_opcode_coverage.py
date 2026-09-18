#!/usr/bin/env python3
"""audit_opcode_coverage.py -- which operations can STRAP emit that no
program ever uses?

COMPANION TO audit_indicator_coverage.py, same question one level up:
not "which indicators does nothing look at" but "which OPERATIONS does
nothing exercise".  Wired into the suite as a RATCHET.

IT ALREADY EARNED ITS KEEP.  The first run found BR -- BRANCH RELATIVE
-- listed in bsv/README.md among the implemented unconditional branches
and implemented by the model as an ABSOLUTE branch identical to B.  Two
primary sources say that is wrong:

  * X22-6533 pocket card, UNCONDITIONAL BRANCHING: B is 010000000 and
    BR is 011000000 -- a different operation code -- and BR is named
    "Branch Relative".
  * Reference Manual p.42: "A simple storage of the instruction counter
    without branching action is accomplished by STORE INSTRUCTION
    COUNTER IF BRANCH RELATIVE with a branch address of 0."  An address
    of 0 producing NO BRANCHING ACTION only works if it is a
    displacement.  The old absolute reading would have branched to 0.0,
    which p.39 separately calls an invalid branching address.

BR now sets OP instead of branching wrongly, and programs/
br_unimplemented.strap pins that.  A silent wrong answer became a
visible unimplemented one.

WHAT THIS DOES NOT TELL YOU, same caveat as the indicator audit: it is
a REFERENCE audit.  A mnemonic appearing in a program is not evidence
the program exercises it meaningfully, only that nothing is completely
untouched.  And it screens what the ASSEMBLER can emit -- an operation
neither the assembler nor any program knows about is invisible to it.

The parse comes from strap_asm.iter_statements, the assembler's own
statement parser, deliberately: the indicator audit needed three
corrections because it re-invented parsing that already existed.
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from strap_asm import iter_statements
import opcodes

OP_TABLES = ["BB_CODES", "CB_CODES", "DIR_INDEX_CODES", "FP_CODES",
             "IMM_INDEX_CODES", "IO_OP", "MISC_CODES",
             "UNCOND_BRANCH_CODES", "VFL_INT_CODES"]

# Every mnemonic below is emittable by STRAP and used by no program.
# Each needs a REASON, and the reasons are not interchangeable.
#
# UNIMPLEMENTED -- the model reaches setOpInvalid for these, and
# bsv/README.md's "Decoded but not executed" section says so.  Only five
# VFL integer arms exist (L, ST, +, M+, K), which accounts for the ten
# compare/convert codes here.
UNIMPLEMENTED = {
    "CV", "DCV", "LCV", "LTRCV",          # radix conversion
    "KE", "KF", "KFE", "KFR",             # compare variants
    "M+1", "LTRS",                        # add-one-to-memory, load transit and set
    "EX", "EXIC",                         # execute
    "RNX",                                # rename
    "LOC", "LOCSEOP",                     # locate
}
# IMPLEMENTED BUT UNEXERCISED -- the model has real arms for these and
# nothing drives them.  This is the actionable list: each is a test
# someone could write today.
UNEXERCISED = {
    "BZB1", "BZBN", "BZBZ",               # BB family: branch-if-off with
                                          #   set-to-one / invert / set-to-zero
    "RDSEOP", "WSEOP", "CTLSEOP", "RELSEOP",  # I/O Suppress-End-Of-Op forms
}
KNOWN_GAP = UNIMPLEMENTED | UNEXERCISED


def known_mnemonics():
    out = {}
    for tname in OP_TABLES:
        for m in getattr(opcodes, tname):
            out.setdefault(m.upper(), set()).add(tname)
    return out


def used_mnemonics():
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'programs', '*.strap'))):
        for st in iter_statements(open(f).read()):
            if st.op:
                out.setdefault(st.op.upper(), set()).add(os.path.basename(f))
    return out


def main():
    known, used = known_mnemonics(), used_mnemonics()
    gap = sorted(set(known) - set(used))

    print(f"mnemonics STRAP can emit      : {len(known)}")
    print(f"used by at least one program  : {len(set(known) & set(used))}")
    print(f"unused                        : {len(gap)}")
    print()
    print(f"  unimplemented (sets OP)     : {len(UNIMPLEMENTED)}")
    print(f"  implemented, unexercised    : {len(UNEXERCISED)}  <- the actionable list")
    print(f"    {', '.join(sorted(UNEXERCISED))}")
    print()

    new_gap  = sorted(set(gap) - KNOWN_GAP)
    now_used = sorted(KNOWN_GAP - set(gap))
    if new_gap:
        print(f"FAIL: newly unused operation(s): {', '.join(new_gap)}")
        print("Either exercise them or add them to KNOWN_GAP with a reason.")
        return 1
    if now_used:
        print(f"FAIL: {', '.join(now_used)} now used -- remove from KNOWN_GAP.")
        return 1
    print(f"PASS: the unused set is exactly the {len(KNOWN_GAP)} known and categorised.")
    print()
    print("Reference, not discrimination: a mnemonic appearing in a program")
    print("is not evidence that the program exercises it. See the header.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
