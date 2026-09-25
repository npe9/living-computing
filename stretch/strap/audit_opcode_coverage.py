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

AND IT STILL NEEDED A FOURTH.  Using the assembler's parser is not the
same as using the assembler's NAME RESOLUTION.  An I/O operation has two
spellings that assemble identically -- "W(SEOP)" and "WSEOP" -- and
programs use the modifier form, so the first version reported WSEOP and
RELSEOP as unexercised while io_reader_printer.strap was driving both.
Checking a suspicious result against the program that supposedly does
not exist is what caught it, again.  Before writing a test for anything
this names, GREP FOR THE OTHER SPELLING.
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
    "LOC", "LOCSEOP",                     # locate
}
# UNIMPLEMENTED IN THE MODEL BUT EXERCISED FOR ITS ENCODING.  This
# category exists because EXIC forced it, and the distinction it draws
# is real: KNOWN_GAP below means "expected to be UNUSED", while
# UNIMPLEMENTED above is documented as "the model sets OP for these".
# Those two properties coincided until a TRANSCRIPTION used an
# instruction the model cannot execute.
#
# THE CATEGORY HAS NOW BEEN FORCED THREE TIMES, by three unrelated
# transcriptions, which is why it is a category and not a special case:
#
#   EXIC  programs/ax5b_162_exic_classes.strap -- jb_ax5b routine 1262
#         TEST 2B, 43 rows.  Also ax5b_162_test3a/3b.
#   EX    programs/ax5b_162_test1cc.strap -- routine 1262 TEST 1CC, 81
#         rows.  More EX rows than the rest of the repo together; the
#         block is the specification for the EXE indicator.
#   RNX   programs/ibox4_rnx_nop.strap -- jb_ax4b routine 1244, the
#         refill-address NOP gate.  The FIRST listing witness for RNX
#         anywhere in this repo; before it, the name appeared only in
#         opcodes.py's table, this audit, and two comments.
#
# In each case the assembler emits the operation, the model decodes it
# and then sets Operation Code Invalid, and the program is never run.
# So each is USED and must leave KNOWN_GAP or the ratchet fails -- but
# none is implemented, and listing them here says so rather than
# letting their absence from UNIMPLEMENTED imply otherwise.
#
# EXPECT THIS SET TO KEEP GROWING, and do not read growth as progress.
# A name moving from UNIMPLEMENTED to ENCODING_ONLY means a listing now
# pins its ENCODING.  It says nothing whatever about execution, and the
# two are separately earned.  docs/NEXT.md item 4a is the open work for
# EX/EXIC; RNX is recorded there as out of scope.
ENCODING_ONLY = {
    "EXIC",
    "EX",
    "RNX",
}
# IMPLEMENTED BUT UNEXERCISED -- the model has real arms for these and
# nothing drives them.  This is the actionable list: each is a test
# someone could write today.
# EMPTY.  Every operation STRAP can emit that the model implements is now
# driven by at least one program.  What is left unused is exactly the
# unimplemented set above.  How the list emptied, in order:
#   BZB1/BZBN/BZBZ -> programs/bb_branch_if_off.strap
#   WSEOP/RELSEOP  -> never actually missing; io_reader_printer.strap
#                     drives both, spelling them W(SEOP) and REL(SEOP),
#                     and the audit was counting only the base mnemonic
#                     (see used_mnemonics)
#   RDSEOP/CTLSEOP -> programs/io_tape.strap, steps 10-11
# The "reference, not discrimination" caveat still applies: this says
# nothing is untouched, not that anything is well tested.
UNEXERCISED = set()
KNOWN_GAP = UNIMPLEMENTED | UNEXERCISED


def known_mnemonics():
    out = {}
    for tname in OP_TABLES:
        for m in getattr(opcodes, tname):
            out.setdefault(m.upper(), set()).add(tname)
    return out


IO_BASE_OPS = {"RD", "W", "CTL", "LOC", "REL"}


def used_mnemonics():
    """{MNEMONIC: {files}} -- every operation any program actually emits.

    An I/O operation has TWO spellings that assemble identically:
    "W(SEOP)" and "WSEOP" (strap_asm.py: `lookup = op + 'SEOP' if
    seop_mod and op in IO_BASE_OPS`).  Programs use the modifier form, so
    counting only `st.op` reported WSEOP and RELSEOP as unexercised while
    io_reader_printer.strap was driving both -- the fourth blind spot
    this pair of audits has had, after branch-on-bit, $<IND> symbols and
    comments.  Normalising here mirrors what the assembler does.
    """
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'programs', '*.strap'))):
        for st in iter_statements(open(f).read()):
            if not st.op:
                continue
            op = st.op.upper()
            seop = bool(st.mods) and st.mods[0].strip().upper() == 'SEOP'
            if seop and op in IO_BASE_OPS:
                op += 'SEOP'
            out.setdefault(op, set()).add(os.path.basename(f))
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
    print(f"  unimplemented but ENCODED by a transcription : "
          f"{len(ENCODING_ONLY)}  ({', '.join(sorted(ENCODING_ONLY))})")
    print("    used, so not a gap; not executable, so not implemented.")
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
