#!/usr/bin/env python3
"""check_ja_bp6a_dump.py -- THE SCOPE, for IBM's JA BP6A memory-pattern
test (../decks/ja_bp6a_memory_patterns.strap).

JA BP6A compares nothing: "This program operates continuously with no
error indications.  It relies on scoping to detect errors" (writeup,
PDF p.1, section 2).  On the floor the CE watched the memory circuits
while the patterns rippled through.  Here the harness stops the run at
a chosen point (run_ja_bp6a.sh, gen_tb's STOPAT), dumps all of core
from word 32 up (DUMP=), and this script compares EVERY word against
the image the program must have produced by then.

THE EXPECTED IMAGE IS COMPUTED FROM THE PROGRAM'S OWN STEPS, written
out below from the listing, not from the model:
  Part I  (MPATA, low core): T 50 words MPATB -> MPST1 (note: MPST1
          reserves 25, so the save overruns FINM1 through 001115);
          then for each pattern k: TI puts MPTDx1 at 100000 and
          "T,$X1,32768.,32769." count 65535 ripples it to 277777;
          then T 50 words MPST1 -> MPATB, B MPATB.
  Part II (MPATB, 100000): T 562 words from 100 -> MPST2 (100033,
          which lies INSIDE the 50 words Part I restored); per pattern
          TI puts MPTDx2 at 40 and "T,$X1,32.,33." count 32735 ripples
          it to 77777; T 562 words back to 100; B MPATA.
Every T here is a forward, non-overlapping-source copy word by word,
which for the ripple is exactly "each word = the one below it".

Usage: run_program.sh ... | check_ja_bp6a_dump.py STAGE
  STAGE is  B<k>   -- Part I with k patterns rippled (k = 1..5)
            A<k>   -- Part II with k patterns rippled (k = 1..5)
            LOOP   -- one whole loop, then the next pass's first pattern
Prints one PASS/FAIL line per region and exits non-zero on any FAIL.
"""

import re
import sys

from strap_asm import assemble
from verify_ja_bp6a_listing import image_source

O = lambda s: int(s, 8)
TOP = 98304                      # installed words (six 16K units)
FIRST = 32                       # = octal 40; words 0-31 are registers, not dumped


class Core(list):
    """Expected core: None where nothing has been loaded or stored yet.
    (Bluesim starts its BRAMs at AAAA...AAAA, not zero; a word the
    program has not yet reached has no expected value and is not
    compared.)"""


def program_image():
    prog = assemble(image_source())
    mem = Core([None] * TOP)
    for a, w in prog.words.items():
        mem[a] = w
    return mem, prog.symtab


def transmit(mem, src, dst, n):
    for i in range(n):
        mem[dst + i] = mem[src + i]


def part1(mem, sym, k):
    """Part I with k patterns rippled; k == 6 also restores MPATB."""
    mpst1, mpatb = sym["MPST1"] // 64, sym["MPATB"] // 64
    transmit(mem, mpatb, mpst1, 50)                    # LCI 50; T MPATB->MPST1
    pat0 = sym["MPTDA1"] // 64
    for p in range(k):
        mem[O("100000")] = mem[pat0 + p]               # TI,1,MPTDA1($X1),32768.
        for a in range(O("100001"), O("100000") + 65535 + 1):
            mem[a] = mem[a - 1]                         # T,$X1,32768.,32769.
    if k == 6:
        transmit(mem, mpst1, mpatb, 50)                # T MPST1->MPATB


def part2(mem, sym, k):
    mpst2 = sym["MPST2"] // 64
    transmit(mem, O("100"), mpst2, 562)                # T,$X2,64.0,MPST2
    pat0 = sym["MPTDA2"] // 64
    for p in range(k):
        mem[O("40")] = mem[pat0 + p]                   # TI,1,MPTDA2($X1),32.0
        for a in range(O("41"), O("40") + 32735 + 1):
            mem[a] = mem[a - 1]                         # T,$X1,32.,33.
    if k == 6:
        transmit(mem, mpst2, O("100"), 562)            # T,$X2,MPST2,64.0


def expected(stage):
    mem, sym = program_image()
    if stage.startswith("B"):
        part1(mem, sym, int(stage[1:]))
    elif stage.startswith("A"):
        part1(mem, sym, 6)
        part2(mem, sym, int(stage[1:]))
    elif stage == "LOOP":
        # One whole loop, then the next pass's save and its FIRST
        # pattern (zeros) through the B boxes: run_ja_bp6a.sh stops at
        # the 8th arrival at MPAT1, the first point after the loop at
        # which no transmit is still draining (see that script).  So the
        # A boxes hold Part II's last pattern, the ones-ECC word, and the
        # restored low program; the B boxes hold zeros again.
        part1(mem, sym, 6)
        part2(mem, sym, 6)
        before = list(mem)
        transmit(mem, sym["MPATB"] // 64, sym["MPST1"] // 64, 50)
        # The save rewrites MPST1 with the words already there.
        assert mem == before, "the second save is not idempotent"
        mem[O("100000")] = mem[sym["MPTDA1"] // 64]
        for a in range(O("100001"), TOP):
            mem[a] = mem[a - 1]
    else:
        raise SystemExit(f"unknown stage {stage!r}")
    return mem


REGIONS = [
    ("A boxes 000040-077777", O("40"), O("100000")),
    ("B boxes 100000-277777", O("100000"), TOP),
]


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    stage = sys.argv[1]
    want = expected(stage)
    got = {}
    stopped = None
    for line in sys.stdin:
        if not line.startswith("MEMDUMP"):
            sys.stdout.write(line)
        m = re.match(r"MEMDUMP (\d+) ([0-9a-fA-F]+)", line)
        if m:
            got[int(m.group(1))] = int(m.group(2), 16)
        elif line.startswith("STOPPED DELIBERATELY"):
            stopped = line.strip()
    fails = 0
    if stopped is None:
        print(f"FAIL ja_bp6a {stage}: the run did not stop at its STOPAT point")
        fails += 1
    missing = [a for a in range(FIRST, TOP) if a not in got]
    if missing:
        print(f"FAIL ja_bp6a {stage}: {len(missing)} words not dumped "
              f"(first {missing[0]:06o})")
        fails += 1
    for name, lo, hi in REGIONS:
        known = [a for a in range(lo, hi) if want[a] is not None]
        bad = [a for a in known if a in got and got[a] != want[a]]
        if bad:
            fails += 1
            print(f"FAIL ja_bp6a {stage} {name}: {len(bad)} of {len(known)} "
                  f"words differ (first {bad[0]:06o}, last {bad[-1]:06o})")
            for a in bad[:6]:
                print(f"     {a:06o}: model {got[a]:022o}  expected {want[a]:022o}")
        else:
            print(f"PASS ja_bp6a {stage} {name}: all {len(known)} words "
                  f"the program has reached are as expected")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
