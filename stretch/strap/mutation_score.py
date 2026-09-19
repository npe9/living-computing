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
import atexit, os, re, signal, subprocess, sys, time

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
    ("zm-drops-normalized-term", "bsv/StretchFP.bsv",
     "    r.zm = normalized && zero && (e > -1024);",
     "    r.zm = zero && (e > -1024);",
     "MULTIPLY's zero-multiply indicator ignores the normalization"
     " modifier; p.99 gives ZM the normalized term for * but NOT for *+."
     "  Closed by programs/fp_zm_terms.strap case 2."),

    ("zm-exponent-bound", "bsv/StretchFP.bsv",
     "    r.zm = normalized && zero && (e > -1024);",
     "    r.zm = normalized && zero && (e >= -1024);",
     "ZM's exponent bound is off by one: p.99 says GREATER THAN -1024."
     "  Closed by programs/fp_zm_terms.strap case 3."),

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


def apply(path, old, new):
    full = os.path.join(ROOT, path)
    src = open(full).read()
    if old not in src:
        return None, f"pattern absent in {path}"
    out = src.replace(old, new, 1)
    if out == src:
        return None, "replacement changed nothing"
    _PENDING[path] = src
    open(full, 'w').write(out)
    return src, None


def main():
    if "--list" in sys.argv:
        for n, f, _, _, why in MUTATIONS:
            print(f"{n:28} {os.path.basename(f):22} {why}")
        return 0
    only = None
    if "--only" in sys.argv:
        only = sys.argv[sys.argv.index("--only") + 1]

    if not check_tree_clean():
        return 2
    if not check_baseline_green(env0=dict(os.environ)):
        return 3
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
        print(f"{verdict:9} {name:28} {dt/60:5.1f} min  {where}", flush=True)
        results.append((name, verdict, dt, why))

    print()
    survivors = [r for r in results if r[1] == "SURVIVED"]
    scored = [r for r in results if r[1] in ("caught", "SURVIVED")]
    if scored:
        print(f"mutation score: {len(scored)-len(survivors)}/{len(scored)} caught")
    for name, _, _, why in survivors:
        print(f"  SURVIVED {name}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
