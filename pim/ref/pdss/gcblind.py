#!/usr/bin/env python3
"""Compare transcripts with the garbage collector's reports taken out.

    gcblind.py GOLDENDIR GOTDIR [JOB ...]

A conformance transcript (conformance.sh) includes each GC report
("GC-n ... GC Time: N msec", six lines) where the collection happened,
which may be in the middle of an output line.  This removes every report
block and the line break it introduced, then compares.  It separates a
difference in *when* the collector ran (heap accounting) from a
difference in what the program computed.  Prints one line per job that
still differs; exit 1 if any does.
"""
import os
import re
import sys

BLOCK = re.compile(r"\n?GC-\d+ +KL1-Data.*?\nGC Time: N msec\n", re.S)


def blind(text):
    return BLOCK.sub("", text)


def main():
    gold, got = sys.argv[1], sys.argv[2]
    jobs = sys.argv[3:] or sorted(f[:-4] for f in os.listdir(gold) if f.endswith(".out"))
    bad = 0
    for j in jobs:
        g = os.path.join(gold, j + ".out")
        o = os.path.join(got, j + ".got")
        if not os.path.exists(o):
            continue
        a, b = blind(open(g, encoding="latin-1").read()), blind(open(o, encoding="latin-1").read())
        if a != b:
            bad += 1
            al, bl = a.split("\n"), b.split("\n")
            for i, (x, y) in enumerate(zip(al, bl)):
                if x != y:
                    print("%s: line %d\n  < %s\n  > %s" % (j, i + 1, x[:160], y[:160]))
                    break
            else:
                print("%s: length %d vs %d lines" % (j, len(al), len(bl)))
    print("gcblind: %d of %d differ" % (bad, len(jobs)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
