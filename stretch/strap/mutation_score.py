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
import os, re, subprocess, sys, time

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

    ("store-zero-spares-indicators", "bsv/StretchExecute.bsv",
     "                ind = ind & 64'hFFFFF00000000000;",
     "                ind = ind;",
     "Z,$IND stops clearing the settable indicator bits (p.41)."),

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
    ("effaddr18-ignores-index-sign", "bsv/StretchExecute.bsv",
     "    Bit#(18) m = truncate(x.addr);\n    return (x.sign == 1) ? (raw - m) : (raw + m);\n  end\nendfunction\n\n// readHW",
     "    Bit#(18) m = truncate(x.addr);\n    return raw + m;\n  end\nendfunction\n\n// readHW",
     "The FLOATING-POINT address helper ignores the index value's sign"
     " (p.20-21); effAddr18 is a third independent copy of that test."
     "  Closed by programs/fp_negative_modifier.strap.  All THREE copies"
     " survived until each got its own program."),

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


def apply(path, old, new):
    full = os.path.join(ROOT, path)
    src = open(full).read()
    if old not in src:
        return None, f"pattern absent in {path}"
    out = src.replace(old, new, 1)
    if out == src:
        return None, "replacement changed nothing"
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
