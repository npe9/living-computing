#!/usr/bin/env python3
"""Check PDSS's own test/ programs against their header comments.

Every test/*.kl1 begins with a comment block that is the output the
program should print: a title line, then one line per instruction
group with one letter per passed check ('*' marks a failed check).
This compares that block with the console output in a conformance
transcript (golden/t_<name>.out, or a .got file), and prints one line
per test that differs.  It is independent of any PDSS build: it says
whether the reference build itself passes ICOT's tests.

    check_headers.py TESTDIR TRANSCRIPTDIR [--expect headers_expected.txt]

-q prints only the summary.
"""
import os
import sys


def header(path):
    out = []
    with open(path, encoding="latin-1") as f:
        for line in f:
            line = line.rstrip()
            if not out and line.startswith("/*"):
                continue        # a few tests open with a Japanese note
            if not line.startswith("%"):
                break
            out.append(line)
    return out


def console(path, title):
    """Lines printed by go/0: from the title line to the stat line."""
    lines = open(path, encoding="latin-1").read().split("\n")
    out, on = [], False
    for line in lines:
        if not on:
            if line.endswith(title):
                on = True
                out.append(title)
            continue
        if line.startswith(("Total of ", "| ?-", "exit ")):
            break
        out.append(line.rstrip())
    while out and out[-1] == "":
        out.pop()
    return out


def main():
    tdir, gdir = sys.argv[1], sys.argv[2]
    expect = set()
    if "--expect" in sys.argv:
        for line in open(sys.argv[sys.argv.index("--expect") + 1]):
            if line.strip() and not line.startswith("#"):
                expect.add(line.split()[0])
    bad = []
    n = 0
    for fn in sorted(os.listdir(tdir)):
        if not fn.endswith(".kl1"):
            continue
        name = fn[:-4]
        g = os.path.join(gdir, "t_%s.out" % name)
        if not os.path.exists(g):
            continue
        n += 1
        want = header(os.path.join(tdir, fn))
        got = console(g, want[0])
        if got != want:
            bad.append(name)
            if "-q" in sys.argv:
                continue
            print("header mismatch: %s" % name)
            for i in range(max(len(want), len(got))):
                w = want[i] if i < len(want) else "<none>"
                h = got[i] if i < len(got) else "<none>"
                if w != h:
                    print("  want: %s\n  got : %s" % (w, h))
    unexpected = sorted(set(bad) - expect)
    gone = sorted(expect - set(bad))
    print("headers: %d tests, %d match their header, %d differ%s"
          % (n, n - len(bad), len(bad),
             (" (" + ",".join(bad) + ")") if bad else ""))
    if unexpected or gone:
        print("headers: FAIL (unexpected: %s; expected but passing: %s)"
              % (",".join(unexpected) or "-", ",".join(gone) or "-"))
        sys.exit(1)


if __name__ == "__main__":
    main()
