#!/usr/bin/env python3
"""Count a 1e program's *architectural* reads outside its segments.

The Bluespec run's `P9HOST EXIT` line counts the read requests the core
makes to addresses in no segment (bsv/p9host.c, `p9h_request`).  That
count mixes two things: reads the program's own instructions make, and
reads made on behalf of instructions that never retire (the predicted
path of a conditional jump that mispredicted; PRM p. 2-3).  This tool
measures the first on the reference model, which executes only the
retiring path: it runs the program with tools/p9run.py's `run` and counts
every word `sem/hobbit_sem.py` reads from memory (`_memory_word`, i.e.
behind the stack cache) outside the segments the recording declares --
the kernel page, [0x1000, page(brk)) and the user stack below USTKTOP.

A non-zero result means a *retired* instruction read an unmapped word,
which would be a fault in the program or in the model.  Zero, with the
core reporting N, means all N of the core's reads were off the retiring
path (docs/conformance_1to1.md 1c).

    python3 tools/p9archreads.py --root TREE [--cwd DIR] BINARY [ARG ...]

`--no-stack` drops the stack segment from the legal set: a control that
the count sees the reads at all (it must then be large).

Only `run`'s public behaviour is used; p9run.py is not modified.
"""

import argparse
import collections
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sem"))
import hobbit_sem      # noqa: E402
import p9run           # noqa: E402


def count(binary, args, root, cwd="", stack=True):
    pages = collections.Counter()      # w >= 0x1000, by page
    low = collections.Counter()        # page 0 holds KPAGE: by word
    orig = hobbit_sem._memory_word

    def wrapped(state, reader, w):
        if w < 0x1000:
            low[w] += 1
        else:
            pages[w >> 12] += 1
        return orig(state, reader, w)

    hobbit_sem._memory_word = wrapped
    try:
        status, steps, k, _ops = p9run.run(
            binary, [os.path.basename(binary)] + list(args), root,
            50_000_000, open(os.devnull, "wb"), cwd=cwd)
    finally:
        hobbit_sem._memory_word = orig
    page = lambda a: (a + 0xFFF) & ~0xFFF
    ranges = [p9run.KPAGE, (0x1000, page(k.max_brk))]
    if stack:
        ranges.append((p9run.USTKTOP - p9run.USTKSIZE, p9run.USTKTOP))
    outside = sum(n for w, n in low.items()
                  if not any(lo <= w < hi for lo, hi in ranges))
    for pg, n in pages.items():
        a = pg << 12
        # Every segment but KPAGE is whole pages (page() above, USTKSIZE).
        if any(lo <= a and a + 0x1000 <= hi for lo, hi in ranges):
            continue
        if any(lo < a + 0x1000 and a < hi for lo, hi in ranges):
            raise SystemExit("p9archreads: page 0x%x straddles a segment "
                             "boundary; count it by word" % a)
        outside += n
    return status, steps, ranges, outside


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", required=True)
    ap.add_argument("--cwd", default="")
    ap.add_argument("--no-stack", action="store_true")
    ap.add_argument("binary")
    ap.add_argument("args", nargs=argparse.REMAINDER)
    a = ap.parse_args(argv)
    status, steps, ranges, outside = count(a.binary, a.args, a.root, a.cwd,
                                           stack=not a.no_stack)
    print("p9archreads: %s: %s after %d instructions; segments %s; "
          "architectural reads outside them: %d"
          % (os.path.basename(a.binary), status, steps,
             " ".join("%x-%x" % r for r in ranges), outside))
    return 0 if status.startswith("exits(") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
