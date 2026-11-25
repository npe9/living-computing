#!/usr/bin/env python3
"""io_reads.py -- compare the SoC co-simulation's device reads with the
reference boot's (fpga/sim/run_soc.sh).

The reference model (tools/p9coreboot.py record) writes one `D N ADDR
VALUE` line to boot.rec for every architectural read of a non-RAM word,
N being the 1-based record that made it.  The SoC top logs every read it
forwards off the core (`R ADDR DATA RETIRED`, soc_main.cpp SOC_IOLOG).
A device read is a side effect, so the two lists must be the same reads:
the core must neither repeat nor speculate one.

    python3 io_reads.py boot.rec io.log ref.hri [--max N]

Each forwarded read is paired, in order, with the reference's next read
of the same word at a record no earlier than the one retiring when the
read was forwarded (a forwarded read precedes its instruction's
retirement).  An unpaired read is classified:

  merge    the next forwarded access to the word is a write, and the
           record that made that write stores fewer than four bytes
           (HRI mask != 0f): the old word read for a sub-word store
  other    anything else (a repeated or speculative read)

and an unpaired reference read is "missing".  Prints the counts and the
first few of each kind; exits 1 unless every count but "paired" is 0.
"""
import sys
from collections import defaultdict, deque

# A forwarded read is logged with the count of records retired when it was
# made; the instruction that made it retires within the pipeline's depth
# after that (observed: up to 2 records later).
AHEAD = 8


def main():
    args = sys.argv[1:]
    show = 5
    if "--max" in args:
        i = args.index("--max")
        show = int(args[i + 1])
        del args[i:i + 2]
    rec, iolog, hri = args
    ref = defaultdict(deque)
    nref = 0
    for line in open(rec):
        if line.startswith("D "):
            _, n, a, v = line.split()
            ref[int(a, 16)].append((int(n, 16), int(v, 16)))
            nref += 1
    io = []
    for line in open(iolog):
        f = line.split()
        if len(f) >= 4 and f[0] in ("R", "W"):
            io.append((f[0], int(f[1], 16), int(f[2], 16), int(f[3])))
    masks = {}
    want = set()
    for k, (kind, a, d, n) in enumerate(io):
        if kind == "W":
            want.add(n)
    with open(hri) as h:
        for i, line in enumerate(h, 1):
            if i in want:
                m = line.split("mask=")[1].split()[0] if "mask=" in line else "0f"
                masks[i] = m
    paired = 0
    kinds = defaultdict(list)
    for k, (kind, a, d, n) in enumerate(io):
        if kind != "R":
            continue
        q = ref[a & ~3]
        while q and q[0][0] < n + 1:      # the reference read an earlier
            kinds["missing"].append((q[0][0], a, q[0][1]))  # one we never did
            q.popleft()
        if q and q[0][0] <= n + AHEAD:
            q.popleft()
            paired += 1
            continue
        nxt = None
        for kind2, a2, d2, n2 in io[k + 1:]:
            if (a2 & ~3) == (a & ~3):
                nxt = (kind2, n2)
                break
        if nxt and nxt[0] == "W" and masks.get(nxt[1], "0f") != "0f":
            kinds["merge"].append((n, a, d))
        else:
            kinds["other"].append((n, a, d))
    for a, q in ref.items():
        for n, v in q:
            kinds["missing"].append((n, a, v))
    nio = sum(1 for x in io if x[0] == "R")
    print("io_reads: %d forwarded reads, %d reference device reads, %d paired"
          % (nio, nref, paired))
    bad = 0
    for kind in ("merge", "other", "missing"):
        v = kinds[kind]
        bad += len(v)
        print("  %-8s %d" % (kind, len(v)))
        for n, a, d in sorted(v)[:show]:
            print("      at record %d: %08x = %08x" % (n, a, d))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
