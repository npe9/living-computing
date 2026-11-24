#!/usr/bin/env python3
"""Classify the `cyc` differences between the reference run and the core.

Read-only analysis over the two HRI logs a `bsv/run_p9host.sh` run leaves
behind (`ref.hri` from `tools/p9run.py`, `core.log` from the core).  The
records are paired exactly as `tools/p9trace_cmp.py` pairs them (the
kernel-page stub records dropped from the core's side), and every
one-parcel jump (JMP 0x03 and the conditional jumps 0x04..0x07, Table
1-15 p. 1-22) is described from the *reference* stream alone:

* `host`   -- the parcel count of the record immediately before it, if
  that record is the instruction physically before the jump (pc + 2*len
  == jump pc), else "-" (the jump was reached by a transfer);
* `fold`   -- whether the p. 4-7 rule lets the jump fold into that
  record: a previous one- or three-parcel instruction, not a jump, not a
  one-parcel opcode 0x00..0x07, not a three-parcel monadic (opcode 0);
* `pred`   -- the static prediction, Y (0x05 JMPFY, 0x07 JMPTY) or N
  (p. 1-33);
* `taken`  -- whether the next reference record is not at pc + 2;
* `dist`   -- records since the last CMPEQ/CMPGT/CMPHI (one-parcel
  0x10..0x13, three/five-parcel 0x1d..0x1f), 0 = immediately after;
  the reference model's own Table 4-35 index.

Each disagreement is then given a cause:

* `five-parcel host`  -- the core folded a branch into a five-parcel
  instruction.  p. 4-7 limits folding to "a previous one- or
  three-parcel instruction", so the reference's unfolded 1 is the
  printed reading.
* `folded mispredict, dist d` -- a mispredicted *folded* branch whose
  compare is d+1 instructions back: the core charges a flat 3, the
  reference Table 4-35's row for that distance (3/2/1, or the folded
  "4 or more" 0).
* `after a trap's return` -- an unfolded mispredicted jump that is the
  first instruction after an unimplemented-instruction trap (1e's
  floating point, emulated by the kernel).  The core's EU_S1 resets its
  compare distance to 0 at every redirect, so it charges 3; the
  reference indexes Table 4-35 by the last CMP it saw, several records
  back, and charges 1.  PSW.F here is the kernel's (the emulated
  floating compare), so Table 4-35 has no row for either reading.
* `unexplained` -- anything else.  The tool exits 1 if there is one, so
  a new kind of disagreement cannot hide inside a known count.

    python3 tools/cyc_classify.py ref.hri core.log [--kpage c00:e00]
        [--all] [--examples N]

`--all` also prints the joint distribution over every conditional jump
(agreeing or not), which is what shows the core's rule rather than only
its exceptions.
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from p9trace_cmp import records  # noqa: E402

# The one-parcel jumps: the four conditional ones and, since 2026-11-24,
# the unconditional JMP (0x03), which folds by the same p. 4-7 rule and
# is "predicted" taken and always taken.  zc frexp.c has 11,772 JMPs the
# core folds into a five-parcel host (ref 1, core 0) that the first
# version, conditional jumps only, did not see.
COND = {0x03: ("JMP", True), 0x04: ("JMPFN", False), 0x05: ("JMPFY", True),
        0x06: ("JMPTN", False), 0x07: ("JMPTY", True)}
# Table 4-35, printed p. 4-5.
T435_INCORRECT = {0: 3, 1: 2, 2: 1}
T435_INCORRECT_4 = {True: 0, False: 1}       # folded, unfolded


def plen(p0):
    """Parcel count from the first parcel (Table 1-14, p. 1-21)."""
    if p0 & 0x8000 == 0:
        return 1
    return 3 if (p0 & 0xC000) == 0x8000 else 5


def rec_len(insn):
    p0, p1 = insn >> 16, insn & 0xFFFF
    if p0 == 0x2C00:                   # CPU escape + its instruction (p. 3-14)
        return 1 + plen(p1)
    return plen(p0)


def is_compare(insn):
    p0 = insn >> 16
    n = plen(p0)
    if n == 1:
        return 0x10 <= (p0 >> 10) & 0x1F <= 0x13
    return (p0 >> 8) & 0x3F in (0x1D, 0x1E, 0x1F)


def foldable(insn):
    """p. 4-7: can a one-parcel branch fold into this instruction?"""
    p0 = insn >> 16
    if p0 == 0x2C00:
        return False
    n = plen(p0)
    if n == 1:
        return (p0 >> 10) & 0x1F >= 0x08
    if n == 3:
        return (p0 >> 8) & 0x3F != 0x00
    return False


def cond_op(insn):
    p0 = insn >> 16
    if p0 & 0x8000:
        return None
    return COND.get((p0 >> 10) & 0x1F)


def describe(ref, i, last_cmp):
    (f, cyc, _raw) = ref[i]
    pc, insn = f[0], f[1]
    name, pred = cond_op(insn)
    host = "-"
    fold = False
    after_trap = i > 0 and ref[i - 1][0][10] == 1
    if i > 0:
        pf = ref[i - 1][0]
        n = rec_len(pf[1])
        if pf[0] + 2 * n == pc and pf[10] == 0:
            host = n
            fold = foldable(pf[1])
    taken = None
    if i + 1 < len(ref):
        taken = ref[i + 1][0][0] != pc + 2
    dist = None if last_cmp is None else i - last_cmp - 1
    return dict(i=i, pc=pc, name=name, pred=pred, taken=taken, host=host,
                fold=fold, dist=dist, after_trap=after_trap)


def cause(d, rc, cc):
    mis = d["taken"] is not None and d["taken"] != d["pred"]
    if (not mis and d["host"] == 5 and rc == 1 and cc == 0):
        return "five-parcel host (core folds; p. 4-7: one- or three-parcel only)"
    if mis and d["fold"] and cc == 3 and d["dist"] is not None:
        want = (T435_INCORRECT[d["dist"]] if d["dist"] in T435_INCORRECT
                else T435_INCORRECT_4[True])
        if rc == want:
            return "folded mispredict, dist %d (core flat 3, Table 4-35 %d)" % (
                d["dist"], want)
    if (mis and not d["fold"] and d["after_trap"] and rc == 1 and cc == 3):
        return ("after a trap's return (core: redirect resets the compare "
                "distance to 0; reference: last CMP; no printed row)")
    return "unexplained"


def analyse(ref, dut, klo, khi):
    user = [r for r in dut if not klo <= r[0][0] < khi]
    rows = []
    last_cmp = None
    for i, r in enumerate(ref):
        if i < len(user) and user[i][0] == r[0] and cond_op(r[0][1]):
            d = describe(ref, i, last_cmp)
            d["ref"], d["core"] = r[1], user[i][1]
            rows.append(d)
        if is_compare(r[0][1]) and r[0][10] == 0:
            last_cmp = i
    return rows


def key_all(d):
    mis = d["taken"] is not None and d["taken"] != d["pred"]
    dist = d["dist"]
    db = "-" if dist is None else (str(dist) if dist < 3 else ">=3")
    return ("mis" if mis else "ok", "fold" if d["fold"] else "nofold",
            "host%s" % d["host"], "dist%s" % db)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("ref")
    ap.add_argument("dut")
    ap.add_argument("--kpage", default="c00:e00")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--examples", type=int, default=0)
    a = ap.parse_args(argv)
    lo, hi = (int(x, 16) for x in a.kpage.split(":"))
    ref, dut = records(a.ref), records(a.dut)
    rows = analyse(ref, dut, lo, hi)
    diffs = [d for d in rows if d["ref"] != d["core"]]
    print("one-parcel jumps (JMP and conditional): %d, cyc differs on %d"
          % (len(rows), len(diffs)))
    by = {}
    for d in diffs:
        c = cause(d, d["ref"], d["core"])
        by.setdefault((d["ref"], d["core"], c), []).append(d)
    for (rc, cc, c), ds in sorted(by.items(), key=lambda kv: -len(kv[1])):
        print("  ref %d core %d  %5d  %s" % (rc, cc, len(ds), c))
        for d in ds[:a.examples]:
            print("      record %d pc=%x %s pred=%s taken=%s host=%s dist=%s"
                  % (d["i"], d["pc"], d["name"], "YN"[not d["pred"]],
                     d["taken"], d["host"], d["dist"]))
    if a.all:
        joint = {}
        for d in rows:
            joint.setdefault(key_all(d), {}).setdefault(
                (d["ref"], d["core"]), 0)
            joint[key_all(d)][(d["ref"], d["core"])] += 1
        print("all one-parcel jumps (prediction, p. 4-7 fold, host parcels,"
              " compare distance): (ref, core) x count")
        for k in sorted(joint):
            print("  %-4s %-6s %-6s %-7s %s" % (k + (", ".join(
                "(%d,%d)x%d" % (rc, cc, n)
                for (rc, cc), n in sorted(joint[k].items())),)))
    unexplained = sum(len(v) for (_, _, c), v in by.items()
                      if c == "unexplained")
    return 1 if unexplained else 0


if __name__ == "__main__":
    sys.exit(main())
