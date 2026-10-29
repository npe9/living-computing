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

BR is implemented from Reference Manual printed p.40, and
../decks/br_relative.strap pins it.  (It formerly set OP instead of
branching wrongly, pinned by a br_unimplemented.strap that
run_tests.sh's own note says br_relative.strap replaced.)

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
    "DCV",                                # radix conversion
    # LCV moved to ENCODING_ONLY on 2026-10-18 (MCP printed p.17).
    # CV and LTRCV moved there on 2026-10-21 (MCP printed p.24).
    "KE", "KFE", "KFR",                   # compare variants
    # KF moved to ENCODING_ONLY on 2026-10-18 (MCP printed p.17).
    "LTRS",                               # load transit and set
    # M+1 moved to ENCODING_ONLY on 2026-10-17: still unimplemented,
    # but MCP's bootstrap uses it, so it is no longer UNUSED.
    #
    # LOC AND LOCSEOP LEFT EVERY CATEGORY ON THIS PAGE, 2026-10-18,
    # and the way they left is the thing to read.  LOC was in this set
    # (unimplemented) and LOCSEOP was in ENCODING_ONLY (encoded by a
    # transcription, not executable).  The disk gave both of them a
    # real arm: on a disk channel LOCATE is a SEEK -- Reference Manual
    # printed p.160, "the right effective address... specifies the arc
    # address" -- and decks/io_disk.strap executes it.
    #
    # THE NUANCE THIS PAGE CANNOT EXPRESS, written down rather than
    # lost: LOC is only HALF implemented.  On an EXCHANGE channel it
    # is SELECT UNIT (C22-6531 Appendix A printed p.57 lists them as
    # one operation) and still sets Operation Code Invalid, because
    # this model has one unit per channel and no selection hierarchy.
    # MCP's ERROR ROUTINE uses that form (printed p.5 line 36) and
    # would still be refused.  A mnemonic is the unit this audit
    # counts in, and "implemented for one device kind" is finer than a
    # mnemonic -- so the honest record is here, in the file that
    # stopped tracking it.
}
# UNIMPLEMENTED IN THE MODEL BUT EXERCISED FOR ITS ENCODING.  This
# category exists because EXIC forced it, and the distinction it draws
# is real: KNOWN_GAP below means "expected to be UNUSED", while
# UNIMPLEMENTED above is documented as "the model sets OP for these".
# Those two properties coincided until a TRANSCRIPTION used an
# instruction the model cannot execute.
#
# THE CATEGORY HAS BEEN FORCED THREE TIMES, by three unrelated
# transcriptions, which is why it is a category and not a special case.
# THE CATEGORY HAS NOW BEEN FORCED A FOURTH TIME, by MCP itself.
# ONE of the four is still here:
#
#   RNX   ../decks/ibox4_rnx_nop.strap -- jb_ax4b routine 1244, the
#         refill-address NOP gate.  The FIRST listing witness for RNX
#         anywhere in this repo; before it, the name appeared only in
#         opcodes.py's table, this audit, and two comments.
#
#   M+1 ARRIVED AND LEFT ON THE SAME DAY, 2026-10-17, and the round
#         trip is the clearest illustration of what this category is
#         for.  MCP's bootstrap (../decks/mcp_bootstrap_p2.strap,
#         printed p.2 line 34) pinned its ENCODING bit-exactly, which
#         moved it here out of UNIMPLEMENTED.  That made visible what
#         had been invisible: the model set Operation Code Invalid on
#         the FOURTH instruction of IBM's operating system, so
#         docs/boot_plan.md M3 could transcribe the bootstrap and
#         still never run it.  A sixth VFL integer arm beside L, ST,
#         +, M+ and K closed it, driven by
#         ../decks/vfl_m_plus_one.strap, and M+1 now belongs in no
#         category on this page -- like EX and EXIC before it.
#
# In each case the assembler emits the operation, the model decodes it
# and then sets Operation Code Invalid, and the program is never run.
# So each is USED and must leave KNOWN_GAP or the ratchet fails -- but
# none is implemented, and listing them here says so rather than
# letting their absence from UNIMPLEMENTED imply otherwise.
#
# EX LEFT THIS SET ON 2026-09-25 AND EXIC LEFT IT ON 2026-09-29, and
# the direction of those moves is the one this category was built to
# make visible.  EX used to be here for ../decks/ax5b_162_test1cc.strap
# -- routine 1262 TEST 1CC, 81 rows, more EX rows than the rest of the
# repo together -- which pinned its ENCODING and nothing else.  EXIC
# used to be here for ../decks/ax5b_162_exic_classes.strap (routine
# 1262 TEST 2B, 43 rows) and ax5b_162_test3a/3b, for the same reason.
# The model now EXECUTES both: EX through StretchExecute.bsv's EX arm,
# mkEBox's subject swap and the EXE suppression in the five branch
# arms, driven by ex_subject/ex_exe/ex_exe_bind/ex_monitor.strap; EXIC
# through its own arm (two bail-outs, one per indirection), mkEBox's
# pseudo-instruction-counter step and the two address restrictions,
# driven by exic_subject.strap and exic_addr.strap.  So each belongs in
# no category on this page at all: not UNIMPLEMENTED, because it is
# implemented; not UNEXERCISED, because programs run it; not
# ENCODING_ONLY, because that name means "used for its encoding only",
# and leaving either here would make the ratchet say something false.
#
# EXPECT THIS SET TO KEEP GROWING, and do not read growth as progress.
# A name moving from UNIMPLEMENTED to ENCODING_ONLY means a listing now
# pins its ENCODING.  It says nothing whatever about execution, and the
# two are separately earned -- which is exactly why a name leaving the
# set, as EX and EXIC have now both done, is the move that means
# something.  RNX is recorded in docs/NEXT.md as out of scope.
#
#   LOCSEOP ARRIVED 2026-10-17, from MCP printed p.5 line 36, and it
#         arrived for a reason worth reading twice.  The ERROR
#         ROUTINE does not know which channel the console is on, so
#         it walks all 32 channels of the basic exchange asking each
#         one what it is: a deliberately invalid CTL to see which
#         answer at all, then LOC(SEOP) to see which are TAPE, then
#         GONG to find the console.  So LOCATE is not an exotic
#         instruction MCP happens to touch -- it is how the operating
#         system identifies a device, and the model sets Operation
#         Code Invalid on it (StretchExecute.bsv:3376, explicit).
#         docs/NEXT.md item 5 already had LOC on its list; this is
#         the listing witness that was missing.
#
#         NOTE WHAT THIS AUDIT CANNOT SEE.  SPFL and GONG are not
#         opcodes -- they assemble to CTLSEOP with control codes 077
#         and 177 -- so a CONTROL FUNCTION the model rejects does not
#         show up here at all.  The bootstrap already uses both.  The
#         gap is real and this page is the wrong instrument for it;
#         docs/mcp_tape_manufacture.md carries that table.
#   KF AND LCV ARRIVED TOGETHER ON 2026-10-18, from MCP printed p.17,
#         "PROCESS IOCD CARDS SETTING UP CST AND LST" -- the page
#         where MCP reads its own machine configuration off punched
#         cards.  Line 30 is "KF(BU,48),X IOCD", the compare that
#         decides whether a card IS an IOCD card, and line 34 is
#         "LCV(DU,8,4),$LZC+.3,46", the radix conversion that turns
#         the Hollerith channel digits into a binary channel number.
#         So the two operations the model cannot execute are the two
#         that stand between MCP and knowing what devices it has.
#         Both were in UNIMPLEMENTED until this transcription used
#         them.
#
#         **BOTH ARE BUILT.**  KF on 2026-10-19 (RefMan printed
#         p.65, decks/compare_field.strap) and LCV on 2026-10-20
#         (printed pp.71-73, decks/load_converted.strap).
#
#         LCV looked like the harder of the two and was not.  The
#         note here said "the model sets OP on vi.m.decimal == 1
#         across the whole VFL case.  Building it means building
#         decimal mode, not one arm."  That was wrong about what the
#         bit means: printed p.71 says the radix modifier "describes
#         the format of the ORIGINAL field and also determines the
#         type of conversion", so on a radix conversion it selects a
#         DIRECTION, not decimal arithmetic.  Letting code 000011
#         past that one guard was most of the work.  Decimal
#         arithmetic remains unimplemented and still refused.
ENCODING_ONLY = {
    "RNX",
    # CV AND LTRCV ARRIVED TOGETHER ON 2026-10-21, from MCP printed
    # p.24's TIME CONVERSION, which is the only program in the corpus
    # that needs either.  Lines 25-29 divide the 26-bit time clock by
    # sixty twice and then convert each piece to decimal:
    #
    #     CV(BU),$L,16              -CONVERT HOURS TO DECIMAL
    #     LTRCV(BU,6),$RM+.54       - CONVERT MINUTES TO DECIMAL
    #     LTRCV(BU,6),0.24($1)      -CONVERT SECONDS
    #
    # The ratchet caught the change on the first full run after the
    # page was transcribed, which is what it is for: both were in
    # UNIMPLEMENTED, meaning "expected to be UNUSED", and a deck
    # started using them.  THE MODEL STILL REFUSES BOTH -- they reach
    # setOpInvalid -- so this page is transcribed and checked but
    # cannot be executed, the same standing as every other page from
    # printed p.20 on.  Building them is what would let the time
    # conversion run.
    # LOCSEOP left on 2026-10-18 with LOC -- see the note in
    # UNIMPLEMENTED above.
    # KF left on 2026-10-19: built, and driven by its own deck.
    # LCV left on 2026-10-20: built (RefMan printed pp.71-73,
    # decks/load_converted.strap).  With it, BOTH operations that
    # stood between MCP and knowing what devices it has are
    # implemented -- docs/boot_plan.md A2 is closed.
}
# IMPLEMENTED BUT UNEXERCISED -- the model has real arms for these and
# nothing drives them.  This is the actionable list: each is a test
# someone could write today.
# EMPTY.  Every operation STRAP can emit that the model implements is now
# driven by at least one program.  What is left unused is exactly the
# unimplemented set above.  How the list emptied, in order:
#   BZB1/BZBN/BZBZ -> ../decks/bb_branch_if_off.strap
#   WSEOP/RELSEOP  -> never actually missing; io_reader_printer.strap
#                     drives both, spelling them W(SEOP) and REL(SEOP),
#                     and the audit was counting only the base mnemonic
#                     (see used_mnemonics)
#   RDSEOP/CTLSEOP -> ../decks/io_tape.strap, steps 10-11
# The "reference, not discrimination" caveat still applies: this says
# nothing is untouched, not that anything is well tested.
# ---------------------------------------------------------------------
# A BLIND SPOT THIS AUDIT HAS, FOUND 2026-10-19 AND NOT YET CLOSED
# ---------------------------------------------------------------------
# **M+MG WAS USED BY A DECK, WAS NOT IN UNIMPLEMENTED, AND SET
# OPERATION CODE INVALID EVERY TIME IT RAN.**  The ratchet was
# satisfied and the operation did not work.  M+MG itself is fixed
# (2026-10-19, decks/m_plus_mg.strap, RefMan printed p.62), but the
# blind spot that hid it is not, and "+MG" is still in it.
#
# decks/mcp_bootstrap_p5_p6.strap lines 15 and 17 are
# "M+MG(BU,48,8)" and "M+MG(BU,8,8)" -- the two adds that fill MCP's
# error address into its console message -- and a four-line scratch
# reproduced the OP on either alone.  StretchExecute's VFL arm then
# implemented six codes (L, ST, +, M+, K, M+1); the MG forms, "+MG"
# and "M+MG", were not among them and fell to the default.  M+MG is
# now the seventh arm, and "+MG" the eighth (2026-10-19,
# decks/plus_mg.strap, RefMan printed p.60 and Figure 12 on p.61).
#
# **THE BLIND SPOT IS STILL OPEN EVEN THOUGH BOTH ARE BUILT.**  This
# audit compares what the assembler can EMIT against what some deck
# USES; it says nothing about what the model EXECUTES.  Nothing here
# changed to let it see the next one.  What would close it is a check
# that every operation a deck emits executes WITHOUT setting OP --
# running something rather than reading source.
#
# WHY THE AUDIT CANNOT SEE IT.  This file compares two sets: what the
# assembler can EMIT and what some deck USES.  Neither says anything
# about what the model EXECUTES.  UNIMPLEMENTED is a hand-kept list,
# and an operation that is used by a deck never has to appear on it.
# The ENCODING_ONLY category exists for exactly this case and is also
# hand-kept, so it only catches the ones somebody noticed.
#
# WHAT WOULD CLOSE IT: a check that every operation a deck emits is
# executed WITHOUT setting OP, which means running something rather
# than reading source -- a different instrument from this one.  The
# MCP boot section is the first place a real program exposed it, and
# it did so only because that section asserts the indicator register
# EXACTLY.  Recorded here rather than in a commit message because the
# next person to trust this PASS should see it.
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
    for f in sorted(glob.glob(os.path.join(HERE, os.pardir, 'decks', '*.strap'))):
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
