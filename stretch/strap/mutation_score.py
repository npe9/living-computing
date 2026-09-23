#!/usr/bin/env python3
"""mutation_score.py -- does the suite actually NOTICE when the model is
wrong?

WHY.  audit_indicator_coverage.py and audit_opcode_coverage.py both
answer "is anything completely untouched", and both say no.  Neither
answers the question that matters: WOULD ANY PROGRAM NOTICE IF THE MODEL
WERE WRONG.  That distinction is not academic here -- a model setting all
five index result indicators unconditionally to 1 passed 300+ sections,
because every check anywhere branched IF ON.

This applies single-point mutations to the model, runs the suite against
each with FAIL_FAST=1, and reports which ones SURVIVE.  A survivor is a
specific wrong model that every program in the suite calls correct, and
each one is either a missing test or a genuinely unobservable detail.

READING THE RESULT.  A caught mutant costs seconds; a survivor costs a
full run, so the wall-clock is dominated by survivors -- which is the
right way round.  The score is not a grade: mutations here are chosen by
hand to be REAL defects (behaviour some primary source contradicts), not
sampled uniformly, so it measures the suite against faults worth
catching, not against arbitrary edits.

EQUIVALENT MUTANTS are the trap.  A mutation that cannot change any
observable behaviour survives by definition and means nothing.  Each
entry below therefore records WHAT WOULD GO WRONG in the real machine,
so a survivor can be triaged as "missing test" versus "unobservable".

LATEST CAMPAIGN, 2026-09-21, first run under --jobs 12: 32/33, survivor
still ad-bound-off-by-one.  All four interruption entries caught, each
by the block written for it.  53 minutes wall against 233 serial.

EARLIER THAT DAY, after the interruption mechanism: 31/32,
survivor still ad-bound-off-by-one.  Both new entries were caught by
the section written for them, in ~3.3 minutes, which is essentially the
rebuild floor -- see the cost note at the end of this docstring.

AND ONE RESULT THAT IS A TICK IN THE COUNT AND A DEGRADATION IN THE
EVIDENCE.  prot-carve-out-as-or used to be caught by "Storage
protection: the address boundary registers", by its deliberate store to
word 4 -- a named-address check written for exactly that mutation.  It
is now caught 3.2 minutes in by the SIBLING section, "Storage
protection, gated on the interrupt enable bit", and by a different
mechanism: since both protection programs now report violations through
an interruption routine whose marker lives in word 6, the mutation
makes that marker store signal, so the machine interrupts forever and
the run dies at the step cap.

That is a worse witness than the one it replaced -- a loop instead of a
named row -- and it means the boundary program's word-4 store is no
longer what catches this mutant.  The count did not move; the evidence
did.  Recorded here rather than left to be rediscovered, because "31/32"
on its own would hide it.

CAMPAIGN COST, and a figure I got wrong before measuring it.  Every
mutant edits the model, so every mutant pays a full core
re-elaboration.  Split, in an isolated tree: bsc -g (elaborate,
schedule, generate C++) 119s CPU; bsc -e (compile 8.8MB of generated
C++ and link) 24s; Bluesim execution 0.31s.  bsc is SINGLE-THREADED --
119s user against 172s real.

I wrote "32 mutants cost ninety minutes" here, in bsv/README.md and in
a commit message, from that ~2.5 min/mutant floor.  IT WAS AN ESTIMATE
PRESENTED AS A MEASUREMENT, and it was wrong by a factor of 2.4:
summing the per-mutant times of the 2026-09-21 serial run gives 220
minutes for 32 mutants, plus a ~13 minute baseline -- near four hours,
not ninety minutes.  The floor is a floor; most mutants are caught well
past it, and the ones that run the whole suite take 13-16 minutes each.

MEASURED, BOTH MODES, 33 mutants on a 16-core machine:
  serial    220 min of mutants + 13 min baseline  = ~233 min
  --jobs 12 53 min wall, 183 min CPU              = 4.4x faster
The 183/53 = 3.4x effective parallelism is not 12x, and the reason is
structural rather than a tuning problem: the baseline is one serial
suite run (13 min), and the tail is the SLOWEST SINGLE MUTANT -- the
survivor, at 25.6 min, because a survivor is exactly the mutant that
runs the whole suite to the end.  So in parallel mode the campaign
costs baseline + slowest survivor, and adding cores past that buys
nothing.  The docstring above says the wall-clock "is dominated by
survivors -- which is the right way round"; in parallel that stops
being a tendency and becomes the actual formula.

CAMPAIGN 2026-09-19, after the address boundary registers:
29/30, and the only survivor is still ad-bound-off-by-one, the expected
one.  The table has tripled since the second campaign and the score has
not moved off "everything but the documented survivor", which is the
result to want: new mutations are being added for new subsystems rather
than to pad a number.

READ THE SECTION COLUMN AS "FIRST TO FAIL", NOT "THE CATCHER".  This
was wrong in this file and in docs/NEXT.md until 2026-09-23, and the
wrongness produced confident, false conclusions.  Each mutant runs
with FAIL_FAST=1, so run_tests.sh stops at the FIRST failing section
-- which for a broad fault is whatever broad test runs earliest, not
the test that covers the rule.  Measured:

  imm-count-low-bits   reported "bsv smoke test".  With FAIL_FAST off
                       it fails TEN sections, four of them named for
                       the very instructions the rule governs:
                       IBOX-1 KCI, IBOX-3 LRI, IBOX-1 C+I, C-I.
  vfl-length-zero-is-zero  reported "bsv smoke test".  With FAIL_FAST
                       off it fails THIRTY-EIGHT, most of them FP and
                       VFL sections on its own subsystem.

Both had been recorded as "near misses" -- mutants caught far from
home, implying the rule had no witness of its own.  Both in fact have
many.  So a catch attributed to an unrelated section proves NOTHING
about coverage; it usually just means that section runs early.

WHAT THE COLUMN IS STILL GOOD FOR: spotting when a mutant's first
failure is suspiciously early or in a section that shares a resource
with it (that is how the /tmp race was found -- see run_*.sh).  WHAT
IT IS NOT GOOD FOR: deciding a rule is under-tested.  For that,
re-run the one mutant with FAIL_FAST unset and read the whole list of
failing sections, which is what the two measurements above did.

The SURVIVOR list is unaffected by any of this and remains the
campaign's real signal: a mutant nothing caught is a rule nothing
tests.

SECOND CAMPAIGN, after closing the three survivors: 9/10, and the one
survivor is the EXPECTED one -- ad-bound-off-by-one, the SIC read-bail
guard already shown to be an optimisation rather than a correctness
requirement (the AD branch downstream suppresses the store anyway).  An
independent confirmation of that reading rather than a restatement of
it.  The three former survivors are now caught in ~2.4 minutes each, by
the test written for each, instead of 10.9 minutes by an unrelated one:
WHERE and HOW FAST a mutant is caught is the signal that the catch is
deliberate.

FIRST CAMPAIGN, 2026-09-18: 5/8 scored, 2 skipped on stale patterns
(both since fixed -- a SKIP is the harness admitting it did not test
anything, which is the right failure mode and easy to overlook in a
summary line).  Three survivors, all real missing tests, all now closed:

  xvlz-ignores-zero        no program loaded a NEGATIVE ZERO index word
  cmp-leaves-flag          the compares' XF, a bug the model's own
                           comment records as previously FIXED -- a
                           documented fix with no regression test
  branch-target-unmodified not one program in 160+ branched through an
                           index register, so the whole address-
                           modification path for branch targets was
                           unexercised

And one CAUGHT result that was worse news than a survivor:
index-flag-from-count was caught 300 sections later by an I/O test, by
accident.  Every index word in every purpose-written index-indicator
program had flag == (count == 0) -- the deck's three seed constants,
inherited without checking whether the two fields varied independently.
A confounded input makes a whole family of tests blind, and only
mutation shows it: the suite was green, the audits were empty, and the
tests could not tell the flag from the count.  WHERE A MUTANT IS CAUGHT
MATTERS AS MUCH AS WHETHER IT IS.

Usage:  python3 mutation_score.py [--list] [--only NAME]
"""
import atexit, os, re, shutil, signal, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# (name, file, old, new, what it breaks)
MUTATIONS = [
    ("index-flag-from-count", "bsv/StretchExecute.bsv",
     "  Word64 i1 = setBit(ind, ind_XF,   x.flag);",
     "  Word64 i1 = setBit(ind, ind_XF,   pack(x.count == 0));",
     "XF reports the count field instead of the index flag (p.24)."),

    ("xvlz-ignores-zero", "bsv/StretchExecute.bsv",
     "  Word64 i3 = setBit(i2,  ind_XVLZ, pack(x.sign == 1 && !z));",
     "  Word64 i3 = setBit(i2,  ind_XVLZ, pack(x.sign == 1));",
     "A negative ZERO value reports value-less-than-zero (p.24)."),

    ("cmp-leaves-flag", "bsv/StretchExecute.bsv",
     "  Word64 i0 = setBit(ind, ind_XF, x.flag);",
     "  Word64 i0 = ind;",
     "KV/KC leave XF stale; p.24 says the compares set the index flag."),

    ("refill-gate-off-by-15", "bsv/StretchExecute.bsv",
     "              function Bool refillLegal(Bit#(18) rf) =\n"
     "                (rf == 0) || (rf >= 16);",
     "              function Bool refillLegal(Bit#(18) rf) =\n"
     "                True; // INJECTED",
     "Refill accepts addresses 1-15; p.26 restricts it to 16.0 and above."),

    # THE BUG THIS MUTANT REPRODUCES WAS REAL, and shipped.  Until
    # 2026-09-22 the decoder matched sub-ops 010 (Transmit) and 110
    # (Swap) in one condition and recorded neither, so a forward SWAP
    # executed as a one-word Transmit -- silently, with no indicator --
    # while bsv/README.md claimed it set OP.  Nothing could express a
    # SWAP in STRAP until the assembler gained TRANSMIT_CODES, so
    # nothing could catch it.  Dropping bit 57 again is exactly that
    # bug; programs/transmit_scope.strap block 2 fails at 004102.40 --
    # verified by injecting exactly that decoder edit, not assumed.
    ("transmit-swap-ignored", "bsv/StretchDecode.bsv",
     "                              swap: w[6:6], i2: w[3:0] };",
     "                              swap: 1'b0, i2: w[3:0] };",
     "A forward SWAP decodes as a Transmit and executes as one, the way it did before 2026-09-22 (pocket card: sub-op 110 vs 010; Ref. Manual pp.30-31 'bit 57 = bidirectional').  Closed by programs/transmit_scope.strap block 2."),

    ("sva-width-18-for-19", "bsv/StretchDecode.bsv",
     "       : (h[5:4] == 2'b10)     ? {v[23:6], h[13:0]}  // 18, case 2",
     "       : (h[5:4] == 2'b10)     ? {v[23:5], h[12:0]}  // INJECTED",
     "SVA replaces 19 address bits where the FP format has 18 (jb_ax3a p.140)."),

    ("bb-modifier-on-taken-only", "bsv/StretchExecute.bsv",
     "          Bit#(2) mod = bb.modAbc[2:1];\n          if (mod != 2'b00) begin",
     "          Bit#(2) mod = bb.modAbc[2:1];\n          if (mod != 2'b00 && tested == bb.modAbc[0]) begin",
     "BB changes the bit only when it branches; p.41 says whether or not."),

    ("ad-bound-off-by-one", "bsv/StretchExecute.bsv",
     "          if (o.taken && ha >= 32 && prefetchCount < o.readsUsed + 1) begin",
     "          if (o.taken && ha >= 31 && prefetchCount < o.readsUsed + 1) begin",
     "SIC's valid-address bound is 15.32 instead of 16.0 (p.42).  NOTE: the"
     " AD branch downstream may mask this -- a survivor here is expected and"
     " is recorded in run_tests.sh as an optimisation, not a correctness bug."),

    ("seop-ignored-on-rd", "bsv/StretchCore.bsv",
     "      if (rem1 == 0) begin\n        if (!x.suppressEop) cw.eop = 1;",
     "      if (rem1 == 0) begin\n        cw.eop = 1; // INJECTED",
     "A READ SEOP sets the EOP status bit; p.121 says it must not."),

    # THE SEOP RULE HAS SIX COPIES.  "if (!seop) cw.eop = 1" is written
    # out six times -- normal completion, the end-exception path, CTL
    # REWIND, BACKSPACE BLOCK's two sub-cases, and REL.  Three are now
    # driven (io_reader_printer's W/REL, io_tape's RD/CTL REWIND).
    # These ask about the other three, following the effAddr lesson:
    # one rule, many copies, one witness each.
    ("seop-ignored-on-end-exception", "bsv/StretchCore.bsv",
     "      ControlWord cw = ioDev.readChanCW(x.ch);\n      cw.ee = 1;\n      if (!x.suppressEop) cw.eop = 1;",
     "      ControlWord cw = ioDev.readChanCW(x.ch);\n      cw.ee = 1;\n      cw.eop = 1;",
     "A transfer that runs out of material sets EOP even under SEOP"
     " (p.121); this is the End Exception path, a separate copy."
     "  Closed by io_tape.strap step 15 (CCWP)."),

    ("seop-ignored-on-backspace-at-load-point", "bsv/StretchExecute.bsv",
     "                    cw.epgk = 1;\n                    if (!seop) cw.eop = 1;",
     "                    cw.epgk = 1;\n                    cw.eop = 1;",
     "BACKSPACE BLOCK rejected at the load point sets EOP under SEOP"
     " (p.136 for the reject, p.121 for SEOP); a separate copy."
     "  Closed by io_tape.strap step 12 (CCWM)."),

    ("seop-ignored-on-backspace", "bsv/StretchExecute.bsv",
     "                    io.setTapePos(io.tapePos() - 1);\n                    if (!seop) cw.eop = 1;",
     "                    io.setTapePos(io.tapePos() - 1);\n                    cw.eop = 1;",
     "A successful BACKSPACE BLOCK sets EOP under SEOP; a separate copy."
     "  Closed by io_tape.strap step 14 (CCWO).  All SIX copies of this"
     " one rule now have a witness; three survived until these."),

    ("store-zero-spares-indicators", "bsv/StretchExecute.bsv",
     "                ind = ind & 64'hFFFFF00000000000;",
     "                ind = ind;",
     "Z,$IND stops clearing the settable indicator bits (p.41)."),

    # THE 0-31 CARVE-OUT IN STORAGE PROTECTION.  p.31: "The monitoring
    # of references to locations 0-31 is INDEPENDENT of the contents of
    # the boundary registers... References to locations 0 and 4 through
    # 31, inclusive, never cause an address monitoring signal."  Written
    # as "permanently protected OR in/outside the area", a SET boundary
    # control bit makes every special register 4-31 signal, because they
    # lie outside any area a program can name.  That is not a cosmetic
    # difference: 43 of the 64 st.writeWord sites write a constant
    # address in 4-31 and carry no protection check at all, on exactly
    # this sentence.  The mutant silently invalidates that argument, and
    # nothing but storage_protection_boundary.strap's word-4 store can
    # see it -- which is why it is worth a slot here rather than only an
    # injection line in run_tests.sh.
    ("prot-carve-out-as-or", "bsv/StretchExecute.bsv",
     "  Bool signalled = (a < 32) ? (a >= 1 && a <= 3)\n"
     "                            : ((ctl == 1) ? !inArea : inArea);",
     "  Bool signalled = (a >= 1 && a <= 3)\n"
     "                            || ((ctl == 1) ? !inArea : inArea);",
     "The special registers 4-31 signal a protection violation when the"
     " boundary control bit is set; p.31 says they never signal."),

    # THE MASK, IN THE INTERRUPTION MECHANISM.  p.48: "interruption
    # requires the mask bit to be 1, the indicator bit to be 1, and the
    # mechanism to be enabled."  Dropping the mask takes an interruption
    # on any actuated indicator, and takes it on the wrong one whenever
    # an unmasked indicator sits further left than a masked one.
    #
    # THIS ENTRY EXISTS BECAUSE THE MUTATION SURVIVED.  The first
    # version of interrupt_pg0.strap turned on exactly one indicator and
    # masked exactly that one, so "indicators & mask" and "indicators"
    # could not be told apart, and the injection passed clean.  The
    # program now leaves PG0 actuated and UNMASKED beside a masked PG2.
    # Kept here so the campaign notices if that second block is ever
    # weakened back.
    ("int-mask-ignored", "bsv/StretchStorage.bsv",
     "    Word64 pending = indicators & mask;",
     "    Word64 pending = indicators;",
     "An interruption is taken on an indicator whose mask bit is zero;"
     " p.48 requires the mask bit, the indicator bit and the enable."),

    # THE BRANCH CLAUSE OF THE INTERRUPTION.  p.48 packs two rules into
    # one sentence: the instruction counter "is stepped neither before
    # nor during the execution of the instruction at the effective
    # interruption address; however, the instruction counter can be
    # replaced as the result of a successful branching operation."  A
    # model can honour either and break the other, invisibly, because
    # each is tested by a different kind of interruption routine.  This
    # mutation keeps the counter standing even when the routine
    # branches, which strands the program at the instruction the
    # interruption displaced -- p.48-49's whole correction-routine
    # pattern, "entered by STORE-INSTRUCTION-COUNTER-IF-BRANCH-DISABLED
    # and returned by BRANCH ENABLED", stops working.
    #
    # Only block 3 of interrupt_pg0.strap can see it; blocks 1 and 2
    # use a routine that falls through and pass the mutant clean.
    ("int-branch-never-replaces-ic", "bsv/StretchCore.bsv",
     "        if (taken) pcReg <= next;   // \"replaced as the result of a",
     "        if (False && taken) pcReg <= next;   // \"replaced as the result of a",
     "A branching interruption instruction leaves the instruction counter"
     " where it was; p.48 says a successful branch replaces it."),

    # LEFTMOST PRIORITY.  p.48: "a mechanism develops the number of the
    # LEFTMOST actuated indicator whose mask bit is one", and the
    # programming note explains the consequence -- "the leftmost one
    # identification defines the relative priority of actuated
    # indicators if more than one has its corresponding mask bit turned
    # on".  Scanning the other way takes the lowest-priority pending
    # interruption first, which on a real machine means a machine check
    # waits behind a program indicator.
    #
    # Only block 4 of interrupt_pg0.strap can see it.  Blocks 1-3 each
    # actuate exactly ONE masked indicator, so leftmost and rightmost
    # pick the same one and the mutant passes them clean.
    ("int-rightmost-not-leftmost", "bsv/StretchStorage.bsv",
     "    for (Integer i = 63; i >= 0; i = i - 1)",
     "    for (Integer i = 0; i <= 63; i = i + 1)",
     "The interruption is taken on the RIGHTMOST masked indicator;"
     " p.48 says the leftmost, and calls that the priority rule."),

    # REGRESSION MUTATIONS: bugs the project already fixed, reverted, to
    # ask whether the fix would survive being undone.  cmp-leaves-flag
    # above started as one of these and SURVIVED -- a documented fix with
    # no test.  These two come from the same seam, the model's own "used
    # to" comments.
    ("mask-boundary-0-15", "bsv/StretchStorage.bsv",
     "      addrMask: mask <= {20'hFFFFF, v[43:16], 16'h0000};   // IBM 0-19 = 1, 48-63 = 0 always",
     "      addrMask: mask <= {16'hFFFF, v[47:16], 16'h0000};",
     "The mask register forces only IBM 0-15, the pre-fix boundary; the"
     " comment on that fix says it was never caught by a test."),

    ("index-spare-bits-zeroed", "bsv/StretchTypes.bsv",
     "  return { x.addr, x.sign, x.flag, x.spare, x.count, x.refill };",
     "  return { x.addr, x.sign, x.flag, 2'b00, x.count, x.refill };",
     "packIndexWord drops IBM bits 26-27, so an LX/SX round trip rewrites"
     " them -- the bug I-Box 3 routine 1222 (jb_ax3a p.144) once caught."),

    # FP AND VFL INTERNALS.  The first two campaigns probed index,
    # branch and I/O; most of the model's complexity is in floating
    # point, and it is driven by jb_af1c, the most heavily transcribed
    # tape.  These ask whether that transcription discriminates.
    # DISAMBIGUATED 2026-09-22, and the change is PROVABLY INERT: the
    # old bare pattern and the new context-carrying one produce
    # BYTE-IDENTICAL output, both mutating line 732 (checked by
    # applying each and comparing).  So the campaign result that
    # caught these two before the change carries over unchanged, and
    # re-running 53 minutes to re-establish it would have told us
    # nothing.  These two used the bare
    # "r.zm = normalized && zero && (e > -1024);" line, which occurs
    # TWICE -- fpMul (single multiply) and fpMulDouble (D*) -- so
    # replace(...,1) sent both to fpMul and fpMulDouble's copy of the
    # rule was never mutated.  Each pattern now carries the preceding
    # line, which differs between the two functions, and each site has
    # its own pair.  The _ambiguous guard above now refuses a repeat.
    ("zm-drops-normalized-term", "bsv/StretchFP.bsv",
     """    r.res = res; r.generated = gen;
    r.zm = normalized && zero && (e > -1024);""",
     """    r.res = res; r.generated = gen;
    r.zm = zero && (e > -1024);""",
     "fpMul: MULTIPLY's zero-multiply indicator ignores the normalization modifier; p.99 gives ZM the normalized term for * but NOT for *+.  Closed by programs/fp_zm_terms.strap case 2."),

    ("zm-exponent-bound", "bsv/StretchFP.bsv",
     """    r.res = res; r.generated = gen;
    r.zm = normalized && zero && (e > -1024);""",
     """    r.res = res; r.generated = gen;
    r.zm = normalized && zero && (e >= -1024);""",
     "fpMul: ZM's exponent bound is off by one: p.99 says GREATER THAN -1024.  Closed by programs/fp_zm_terms.strap case 3."),

    # THE COPY THE TABLE WAS BLIND TO.  p.99's ZM rule is implemented
    # twice; until 2026-09-22 nothing mutated or tested fpMulDouble's.
    # Measured that day: injecting the exponent-bound fault at
    # fpMulDouble and running the WHOLE suite gave 3059 PASS, 0 FAIL.
    # programs/fp_zm_terms_double.strap is the witness these two need.
    #
    # BOTH VERIFIED INDIVIDUALLY, applied through this table's own
    # `old`/`new` rather than retyped, each landing on line 929 and
    # each caught by the case its description names:
    #   zm-double-drops-normalized-term -> halt 003304.00 (case 2)
    #   zm-double-exponent-bound        -> halt 003306.40 (case 3)
    # The commit that added them said they were "proven by the
    # injection above"; that was true of the exponent bound only, and
    # the normalized term was verified afterwards.
    ("zm-double-drops-normalized-term", "bsv/StretchFP.bsv",
     """    r.generated = gen;
    r.zm = normalized && zero && (e > -1024);""",
     """    r.generated = gen;
    r.zm = zero && (e > -1024);""",
     "fpMulDouble: D*'s zero-multiply indicator ignores the normalization modifier (p.99).  Closed by programs/fp_zm_terms_double.strap case 2."),

    ("zm-double-exponent-bound", "bsv/StretchFP.bsv",
     """    r.generated = gen;
    r.zm = normalized && zero && (e > -1024);""",
     """    r.generated = gen;
    r.zm = normalized && zero && (e >= -1024);""",
     "fpMulDouble: D*'s ZM exponent bound is off by one (p.99).  Closed by programs/fp_zm_terms_double.strap case 3 -- the fault that survived the entire suite before that program existed."),

    # ZM's CLEAR, two of sixteen copies.  Representatives only: the
    # copies are uniform and fp_zm_cleared.strap walks ten of them, so
    # two here keep the campaign honest without ten 11-minute runs.
    # R/'s copy is deliberately NOT here -- it is unreachable while ZM
    # is on (the divisor is the accumulator, which a ZM-setting
    # multiply leaves at zero), so mutating it would be an EQUIVALENT
    # MUTANT and would survive for a reason that says nothing about the
    # suite.  See fp_zm_cleared.strap's header.
    # NOTE ON THE SHAPE OF THESE TWO.  They REMOVE the arm's clear.  An
    # earlier version INSERTED "ZM := 1" at the top of each arm instead,
    # and both survived -- because the arm's own clear runs afterwards
    # and undoes the insert.  Two equivalent mutants, built by me, of
    # exactly the kind this file's header warns about: a mutation whose
    # effect a later statement overwrites cannot change anything.
    # Removing the behaviour is the reliable shape; inserting a wrong
    # value is only safe when nothing downstream rewrites it.
    ("zm-not-cleared-by-load", "bsv/StretchExecute.bsv",
     "        ind = setRangeIndicators(ind, fpRangeBits(v, gen, !gen && v.ef == 1));\n"
     "        ind = setBit(ind, ind_ZM, 0);\n      end\n      fpop_LFT:",
     "        ind = setRangeIndicators(ind, fpRangeBits(v, gen, !gen && v.ef == 1));\n"
     "      end\n      fpop_LFT:",
     "LOAD leaves ZM set; ZM is a multiply-only indicator and every"
     " other arm must clear it (p.99)."),

    ("zm-not-cleared-by-e-plus", "bsv/StretchExecute.bsv",
     "        ind = setRangeIndicators(ind, fpRangeBits(vind, gen, prop));\n"
     "        ind = setBit(ind, ind_ZM, 0);\n      end\n      default:",
     "        ind = setRangeIndicators(ind, fpRangeBits(vind, gen, prop));\n"
     "      end\n      default:",
     "ADD TO EXPONENT leaves ZM set; a different copy of the same rule."),

    ("noisy-fill-zeros", "bsv/StretchFP.bsv",
     "      if (noisy) w = w | ((96'b1 << nz) - 1);",
     "      if (False) w = w | ((96'b1 << nz) - 1);",
     "Noisy mode stops entering ones on normalization (p.84); F219 turns"
     " noisy mode on for its whole run."),

    ("lc-takes-index-count", "bsv/StretchExecute.bsv",
     "                                            count:h[31:14], refill:x.refill};",
     "                                            count:h[17:0], refill:x.refill};",
     "LOAD COUNT takes the wrong 18 bits of the addressed half-word;"
     " p.24 says the count field comes from its TOP 18 bits."),

    ("imm-count-low-bits", "bsv/StretchExecute.bsv",
     "      Bit#(18) imm18 = ii.imm[18:1];",
     "      Bit#(18) imm18 = ii.imm[17:0];",
     "Count-type immediates take the bottom 18 bits of the address field"
     " instead of the top 18 (p.25)."),

    # ADDRESSING AND COUNTING.  Rules stated by the manual as exact bit
    # positions, which is where an off-by-a-power-of-two hides.
    ("cb-half-adds-a-word", "bsv/StretchExecute.bsv",
     "                          2'b01: 32;",
     "                          2'b01: 64;",
     "Count-and-Branch H adds a WORD where p.41 says a half-word -- 'add"
     " one in bit position 18', which is 32 bits of bit address, not 64."),

    ("effaddr-ignores-index-sign", "bsv/StretchExecute.bsv",
     "    return (x.sign == 1) ? (raw - x.addr) : (raw + x.addr);",
     "    return raw + x.addr;",
     "Address modification always ADDS, ignoring the index value's sign;"
     " p.20-21 says the SIGNED value field is added.  Closed by"
     " programs/index_negative_modifier.strap -- note effAddr19 keeps a"
     " SEPARATE copy of the sign test, closed by branch_index_modified."),

    # THE THIRD COPY.  Address modification's sign test is written out
    # independently in effAddr18 (FP), effAddr19 (branches) and
    # effAddr24 (bit-addressed).  Two are now pinned; this asks about
    # the third.  Suggested directly by the pair above -- when a rule
    # has more than one implementation, each needs its own witness.
    # UNITS, not sign.  These two revert the helpers to adding the index
    # value STRAIGHT to a word / half-word address, which is what they
    # did until p.20-21 was read properly: the instruction's short
    # address is extended with low-order zeros into the 24-bit domain
    # and the value goes in as-is, so one word is 64 and one half-word
    # is 32.  Distinct from the sign mutations below -- a test can pin
    # the sign and still say nothing about the units, which is exactly
    # what fp_negative_modifier did for months.
    ("effaddr19-wrong-units", "bsv/StretchExecute.bsv",
     "    BitAddr base = {raw, 5'b0};        // 19-bit half-word address -> bits 0-18\n"
     "    BitAddr ea   = (x.sign == 1) ? (base - x.addr) : (base + x.addr);\n"
     "    return ea[23:5];                   // only the applicable part",
     "    Bit#(19) m = truncate(x.addr);\n"
     "    return (x.sign == 1) ? (raw - m) : (raw + m);",
     "The BRANCH address helper adds the index value straight to a"
     " half-word address -- 32x too far (p.20-21)."),

    ("effaddr18-wrong-units", "bsv/StretchExecute.bsv",
     "    BitAddr base = {raw, 6'b0};        // 18-bit word address -> bits 0-17\n"
     "    BitAddr ea   = (x.sign == 1) ? (base - x.addr) : (base + x.addr);\n"
     "    return ea[23:6];                   // only the applicable part",
     "    Bit#(18) m = truncate(x.addr);\n"
     "    return (x.sign == 1) ? (raw - m) : (raw + m);",
     "The FLOATING-POINT address helper adds the index value straight to"
     " a word address -- 64x too far (p.20-21)."),

    ("effaddr19-ignores-index-sign", "bsv/StretchExecute.bsv",
     "    BitAddr ea   = (x.sign == 1) ? (base - x.addr) : (base + x.addr);\n"
     "    return ea[23:5];",
     "    BitAddr ea   = base + x.addr;\n"
     "    return ea[23:5];",
     "The BRANCH address helper ignores the index value's sign (p.20-21)."
     "  This one existed only after an audit: branch_index_modified.strap"
     " originally used a POSITIVE index, which cannot tell raw-m from"
     " raw+m, so the claim that all three effAddr copies were pinned was"
     " false for effAddr19."),

    ("effaddr18-ignores-index-sign", "bsv/StretchExecute.bsv",
     "    BitAddr ea   = (x.sign == 1) ? (base - x.addr) : (base + x.addr);\n"
     "    return ea[23:6];",
     "    BitAddr ea   = base + x.addr;\n"
     "    return ea[23:6];",
     "The FLOATING-POINT address helper ignores the index value's sign"
     " (p.20-21); effAddr18 is a third independent copy of that test."
     "  Closed by programs/fp_negative_modifier.strap."),

    ("vfl-length-zero-is-zero", "bsv/StretchExecute.bsv",
     "        Bit#(7) len_ = effLength(vi.a.length);",
     "        Bit#(7) len_ = zeroExtend(vi.a.length);",
     "A VFL length field of 0 means 0 bits instead of 64 (the LENGTH"
     " field's documented '0 means 64' convention)."),

    ("branch-target-unmodified", "bsv/StretchExecute.bsv",
     "        o.target = effAddr19(st, bm.addr, bm.idx);",
     "        o.target = zeroExtend(bm.addr);",
     "Unconditional branches ignore index modification of the target (p.20)."),
]


# RESTORE MUST SURVIVE A SIGNAL.  The try/finally below restores the
# model after each mutation, but a SIGTERM during the subprocess run
# skips it and leaves the tree MUTATED -- demonstrated by killing a
# campaign mid-run, which left an XVLZ mutation sitting in
# StretchExecute.bsv looking exactly like a normal edit.  A mutated file
# mistaken for real work is the worst failure this script can have, so
# the pending restore is registered globally and replayed on exit and on
# a signal.
_PENDING = {}   # path -> original contents


def _restore_all(*_):
    for path, src in list(_PENDING.items()):
        try:
            open(os.path.join(ROOT, path), 'w').write(src)
        except OSError:
            pass
        _PENDING.pop(path, None)


atexit.register(_restore_all)
for _sig in (signal.SIGTERM, signal.SIGINT, signal.SIGHUP):
    try:
        signal.signal(_sig, lambda s, f: (_restore_all(), sys.exit(128 + s)))
    except (ValueError, OSError):
        pass


def check_tree_clean():
    """Refuse to start on an already-modified model: a leftover mutation
    from a killed run would otherwise be scored as if it were the real
    thing, and every result would be quietly wrong."""
    r = subprocess.run(["git", "diff", "--name-only", "--", "bsv/"],
                       cwd=ROOT, capture_output=True, text=True)
    dirty = [f for f in r.stdout.split() if f.strip()]
    if dirty:
        print("refusing to run: the model has uncommitted changes:", file=sys.stderr)
        for f in dirty:
            print(f"  {f}", file=sys.stderr)
        print("A leftover mutation would be scored as the real model.",
              file=sys.stderr)
        return False
    return True


def check_baseline_green(env0):
    """Refuse to score against a suite that is ALREADY failing.

    Learned the hard way.  A program was edited while a campaign ran, so
    one section failed unconditionally; under FAIL_FAST every remaining
    mutation stopped at THAT section and was scored "caught".  The run
    reported 26/26 and meant nothing -- a pre-existing failure is
    indistinguishable from a catch, and it masks every mutation after
    it.  One unmutated run up front costs ~11 minutes and makes the
    whole campaign trustworthy; without it the campaign can only ever
    over-report.
    """
    print("baseline: running the suite unmutated ...", flush=True)
    p = subprocess.run(["./run_tests.sh"], cwd=HERE, env=env0,
                       capture_output=True, text=True, timeout=3600)
    if p.returncode != 0 or "TEST(S) FAILED" in p.stdout:
        print("refusing to run: the suite is not green BEFORE any mutation.",
              file=sys.stderr)
        for ln in p.stdout.splitlines():
            if ln.startswith("FAIL") or "FAIL_FAST" in ln:
                print(f"  {ln}", file=sys.stderr)
        print("Every mutation would be 'caught' by that failure.", file=sys.stderr)
        return False
    print("baseline: green.", flush=True)
    return True


# ---------------------------------------------------------------------
# A PATTERN MUST MATCH EXACTLY ONCE, and this guard exists because it
# once did not.  Both `apply` paths below used `src.replace(old, new,
# 1)`, which silently mutates the FIRST occurrence when a pattern
# matches several.  p.99's ZM rule is implemented twice in
# StretchFP.bsv -- fpMul and fpMulDouble -- in character-for-character
# identical lines, and BOTH the zm-drops-normalized-term and
# zm-exponent-bound mutants used that line as their pattern.  So both
# mutated fpMul, both were reported "caught" by the ZM section, and
# fpMulDouble's copy of the rule was never touched by the campaign at
# all.  Measured 2026-09-22: injecting the same fault directly into
# fpMulDouble and running the whole suite gave 3059 PASS, 0 FAIL -- a
# rule with no witness anywhere, hidden behind a 32/33 score.
#
# A duplicate pattern is therefore a TOOLING BUG, not a mutant: it
# makes the table claim coverage of a site it does not touch.  Reported
# loudly, with the line numbers, so the fix is to disambiguate the
# pattern rather than to wonder why a mutant survived.
# ---------------------------------------------------------------------
def _ambiguous(path, old, src):
    lines = src.split("\n")
    first = old.strip().split("\n")[0]
    hits = [i + 1 for i, l in enumerate(lines) if first in l]
    return (f"AMBIGUOUS pattern in {path}: matches {src.count(old)} times "
            f"(lines {hits}) -- replace(...,1) would mutate only the first, "
            f"so this mutant cannot witness the others.  Disambiguate it "
            f"with surrounding context, and give each copy its own mutant.")


def apply(path, old, new):
    full = os.path.join(ROOT, path)
    src = open(full).read()
    if old not in src:
        return None, f"pattern absent in {path}"
    if src.count(old) != 1:
        return None, _ambiguous(path, old, src)
    out = src.replace(old, new, 1)
    if out == src:
        return None, "replacement changed nothing"
    _PENDING[path] = src
    open(full, 'w').write(out)
    return src, None


# ---------------------------------------------------------------------
# PARALLEL MODE (--jobs N).  Why it exists, and why it is also SAFER.
#
# The serial loop below runs one mutant at a time, and each mutant pays
# a full core re-elaboration before its first test: measured 119s CPU
# for `bsc -g`, 24s for `bsc -e`, 0.31s for the simulation itself (see
# bsv/README.md item 9).  bsc is SINGLE-THREADED -- 119s user against
# 172s real -- so a 33-mutant campaign used one core of sixteen for an
# hour and a half.  Nothing about the work is large; it was queued up
# single file.
#
# Each mutant gets its own CLONED tree instead.  On APFS `cp -c` is a
# copy-on-write clone: the whole bsv/ + strap/ pair is ~6 MB and clones
# in about a millisecond, so the copies cost neither time nor disk.  A
# worker needs only those two directories -- `docs/` appears in this
# tree only inside comments, checked before relying on it.
#
# AND THE REAL TREE IS NEVER MUTATED.  The serial path edits the model
# in place and restores it afterwards, guarded by atexit and a signal
# handler because a killed campaign once left an XVLZ mutation sitting
# in StretchExecute.bsv looking exactly like real work.  In parallel
# mode that failure mode does not exist: the source of truth is only
# ever read.
# ---------------------------------------------------------------------

def _clone_tree(dest):
    """A worker tree: bsv/ + strap/, APFS-cloned so it is effectively free."""
    os.makedirs(dest, exist_ok=True)
    for d in ("bsv", "strap"):
        subprocess.run(["cp", "-c", "-R", os.path.join(ROOT, d), dest + os.sep],
                       check=True)


def _run_one(spec, dest, env):
    """Apply one mutation inside its own tree and run the suite there."""
    name, path, old, new, why = spec
    _clone_tree(dest)
    full = os.path.join(dest, path)
    src = open(full).read()
    if old not in src:
        return (name, "SKIP", 0.0, why, "pattern absent in " + path)
    if src.count(old) != 1:
        return (name, "SKIP", 0.0, why, _ambiguous(path, old, src))
    out = src.replace(old, new, 1)
    if out == src:
        return (name, "SKIP", 0.0, why, "replacement changed nothing")
    open(full, "w").write(out)
    t0 = time.time()
    p = subprocess.run(["./run_tests.sh"], cwd=os.path.join(dest, "strap"),
                       env=env, capture_output=True, text=True, timeout=7200)
    dt = time.time() - t0
    where = ""
    m = re.search(r"FAIL_FAST: stopping at first failing section \((.*)\)", p.stdout)
    if m:
        where = m.group(1)
    return (name, "caught" if p.returncode != 0 else "SURVIVED", dt, why, where)


def run_parallel(specs, jobs, workroot):
    """Results are collected out of order and REPORTED IN TABLE ORDER, so
    the output does not depend on which worker happened to finish first."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    env = dict(os.environ, FAIL_FAST="1")
    print(f"running {len(specs)} mutants {jobs} at a time, "
          f"each in its own cloned tree under {workroot}", flush=True)
    done = {}
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futs = [pool.submit(_run_one, sp, os.path.join(workroot, sp[0]), env)
                for sp in specs]
        # Print as they land, so a long campaign shows progress...
        for f in as_completed(futs):
            name, verdict, dt, why, where = f.result()
            done[name] = (name, verdict, dt, why, where)
            print(f"{verdict:9} {name:28} {dt/60:5.1f} min  first-fail: {where}", flush=True)
    # ... but REPORT in table order, so the summary does not depend on
    # which worker happened to finish first.
    return [done[sp[0]] for sp in specs if sp[0] in done]


def report(results):
    """One summary shape for both modes.  Entries are (name, verdict,
    seconds, why, ...) -- the parallel path carries a fifth field."""
    print()
    survivors = [r for r in results if r[1] == "SURVIVED"]
    scored = [r for r in results if r[1] in ("caught", "SURVIVED")]
    if scored:
        print(f"mutation score: {len(scored)-len(survivors)}/{len(scored)} caught")
    for r in survivors:
        print(f"  SURVIVED {r[0]}: {r[3]}")
    return 0


def main():
    if "--list" in sys.argv:
        for n, f, _, _, why in MUTATIONS:
            print(f"{n:28} {os.path.basename(f):22} {why}")
        return 0
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]
    jobs = 1
    if "--jobs" in sys.argv:
        jobs = int(sys.argv[sys.argv.index("--jobs") + 1])

    if not check_tree_clean():
        return 2
    if not check_baseline_green(env0=dict(os.environ)):
        return 3

    specs = [m for m in MUTATIONS if not only or m[0] == only]

    if jobs > 1:
        workroot = os.path.join(tempfile.gettempdir(), "stretch-mutants")
        shutil.rmtree(workroot, ignore_errors=True)
        os.makedirs(workroot, exist_ok=True)
        results = run_parallel(specs, jobs, workroot)
        shutil.rmtree(workroot, ignore_errors=True)
        return report(results)

    env = dict(os.environ, FAIL_FAST="1")
    results = []
    for name, path, old, new, why in MUTATIONS:
        if only and name != only:
            continue
        saved, err = apply(path, old, new)
        if err:
            print(f"SKIP    {name}: {err}", flush=True)
            results.append((name, "SKIP", 0.0, why))
            continue
        t0 = time.time()
        try:
            p = subprocess.run(["./run_tests.sh"], cwd=HERE, env=env,
                               capture_output=True, text=True, timeout=3600)
            caught = (p.returncode != 0)
            where = ""
            m = re.search(r"FAIL_FAST: stopping at first failing section \((.*)\)", p.stdout)
            if m:
                where = m.group(1)
        finally:
            open(os.path.join(ROOT, path), 'w').write(saved)
            _PENDING.pop(path, None)
        dt = time.time() - t0
        verdict = "caught" if caught else "SURVIVED"
        print(f"{verdict:9} {name:28} {dt/60:5.1f} min  first-fail: {where}", flush=True)
        results.append((name, verdict, dt, why))

    return report(results)


if __name__ == "__main__":
    sys.exit(main())
