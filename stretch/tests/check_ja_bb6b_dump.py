#!/usr/bin/env python3
"""check_ja_bb6b_dump.py -- the pass/fail judge for IBM's JA BB6B worst-
pattern test (../decks/ja_bb6b_worst_pattern.strap), reading the output
of run_ja_bb6b.sh: where the run stopped, and a core dump.

WHAT THE PROGRAM ITSELF CALLS PASS AND FAIL (writeup, PDF pp.1-2):
  - "If an error is encountered, the program will stop.  Refer to the
    listing and neons to determine the nature of the failure.  No error
    print-out is provided." (p.1, 2.2)  The stop is a hang on one of
    the four "BRGZ,$ -IF HANG UP,ADDR. AT M6AZZ IS NOT 1- S" rows (PDF
    pp.6, 14), right after CT1100 / CT0011 of the word under check.
  - "Index Reg 14 is used as a pass counter.  Stepping of Index 14
    indicates success." (p.2, 3.3)
So this judge reads, in order: the PC where the run ended (a hang names
its BRGZ and decodes M6AZZ / M6AZZ2, which hold X2 one word past the
failing word), X14 (word 30), and then every word of core.

INDEPENDENTLY OF THE PROGRAM, every word of core from 32 up is compared
with the image computed from the program's own steps, written from the
listing and the Reference Manual, not from the model (expected()):
  - generate(): CM1111 / CM0000 (BU,64,8) store a whole word of ones /
    zeros through X2 with V+ICR progressive indexing (value +1, count
    -1, refill at zero); CBR on X1 after each store switches the store
    every n words (n = 8, CTLA1; 4, CTLA2); the store that empties X2's
    count goes to BR1 (BXCZ) without the CBR, and BR1 SWAPIs the two
    stores and restarts at PHnA with X1 as it was.  The complement
    round starts afresh (LX X1) with the stores swapped.
  - The check (CT, then four CM1100 on the same word) leaves core
    unchanged when nothing is wrong.
  - inject(): PHnC/PHnD store ones (SX,$X8 after CM1111 on $X8) / zero
    (Z) through X2's value; KV against the split / limit and BXEZ leave
    without the CBR; BR8 loads the second region and PHnE (zeros) /
    PHnF (ones) carry on with X1 as it was.  The complement round
    swaps C with D and E with F.
  - single_check(): BR11 inverts each word once per CBR count of X1 --
    X1's leftover count at the first word, n at every other -- so only
    an odd leftover changes core (it is 6 in Part I, 2 in Part II);
    BR12's CM0011 rewrites each word unchanged.
  - The resets (CBR+ over CTLI1 / CTLI2) zero every tested word, the
    saves and restores are plain T's, and M6AZZ / M6AZZ2 (written by
    SX,$X2 on every check iteration) are not computed, so neither they
    nor any copy of them is compared.
  Part I: T 500 words START2 -> START1+500., test 100000-277013,
          T them back.  Part II: T 900 words 100 -> START2+500., test
          100-77777, T them back, M+1 on X14, BD,PH1.

MEASURED ON THE MODEL (2026-11-26): CHECK, INJECT and PASS all PASS --
no hang, X14 = 1 << 29 after one pass, and every reached word as
expected (65,035 upper words in CHECK and INJECT; 31,963 lower and
63,923 upper in PASS).

INJECTION RECORD (2026-11-26).  Injected in StretchMemory.bsv's mkMBCU:
every store to 150000-150777 has IBM bit 20 (64'h1 << 43) forced to 0,
a stuck-at-0 data bit in part of one memory box:
    units[unitOf(q.addr)].request(q.write, indexOf(q.addr),
      (q.write && q.addr >= 'o150000 && q.addr < 'o151000)
        ? (q.data & ~(64'h1 << 43)) : q.data, q.tag);
`./run_ja_bb6b.sh CHECK` then printed, OBSERVED (21m53s wall at a load
average near 300):
    FAIL: step cap (40000000) reached without halting
    FAIL PC (half-word address) = 1091 (0x443), expected 1139 (0x473)
    FAIL ja_bb6b CHECK: THE PROGRAM HUNG at PDF p.6, CK1A's BRGZ,$
         (half-word 1091 ...); ... the failing word is 150000, which
         holds 1777777577777777777777
    FAIL ja_bb6b CHECK: the run did not stop at its STOPAT point
    PASS ja_bb6b CHECK: X14, the pass counter, = 0
    PASS ja_bb6b CHECK lower 000040-077777: all 288 words ... as expected
    FAIL ja_bb6b CHECK upper 100000-277777: 65035 of 65035 words differ
         (the run stopped in round 1's check: model all ones, expected
         the zeros of the stop point)
That is, IBM's own program found the fault -- the first word of the injected range,
read back with bit 20 off -- and stopped where its listing says it stops;
the checker named the word.  The injection was reverted with
`git apply -R` of the exact patch; StretchMemory.bsv compared equal
(cmp) to the saved original and `git diff stretch/bsv/` was empty.
"""

import re
import sys

from strap_asm import assemble
from verify_ja_bb6b_listing import image_source

O = lambda s: int(s, 8)


def loc_hw(loc):
    """'001041.40' -> its half-word address."""
    w, b = loc.split(".")
    return int(w, 8) * 2 + (1 if b == "40" else 0)
TOP = 98304                      # installed words (six 16K units)
FIRST = 16                       # dump from the index registers up
ONES = (1 << 64) - 1


def program_image():
    prog = assemble(image_source())
    mem = [None] * TOP           # None: never loaded or stored, not compared
    for a, w in prog.words.items():
        mem[a] = w
    return mem, prog.symtab


def transmit(mem, src, dst, n):
    for i in range(n):
        mem[dst + i] = mem[src + i]


def swap(mem, a, b, n):
    for i in range(n):
        mem[a + i], mem[b + i] = mem[b + i], mem[a + i]


class Half:
    """One half of the test (Part I, upper memories, or Part II, lower):
    the constants the listing gives it."""
    def __init__(self, sym, part):
        w = lambda name: sym[name] // 64
        if part == 1:
            self.n = 8                                  # CTLA1 XW,0.,8
            self.r1 = (O("100000"), 32768)              # CTLB1
            self.r2 = (O("200000"), 32268)              # CTLC1
            self.reset = (O("100000"), 65036)           # CTLI1
            self.pa, self.pb = w("PH1A"), w("PH1B")
            self.ca, self.cb = w("CK1A"), w("CK1B")
            self.pc, self.pd = w("PH1C"), w("PH1D")
            self.pe, self.pf = w("PH1E"), w("PH1F")
        else:
            self.n = 4                                  # CTLA2 XW,0.,4
            self.r1 = (O("100"), 16320)                 # CTLB2
            self.r2 = (O("40000"), 16384)               # CTLC2
            self.reset = (O("100"), 32704)              # CTLI2
            self.pa, self.pb = w("PH2A"), w("PH2B")
            self.ca, self.cb = w("CK2A"), w("CK2B")
            self.pc, self.pd = w("PH2C"), w("PH2D")
            self.pe, self.pf = w("PH2E"), w("PH2F")


def generate(mem, h, a_is_ones):
    """PH1A/PH1B (PH2A/PH2B): CM1111 / CM0000 (V+ICR) through X2, CBR on
    X1 every store, BXCZ to BR1 when X2's count runs out (the store that
    emptied it is not counted on X1); BR1 swaps PH1A and PH1B at the
    split and resumes at PH1A.  Returns nothing; writes mem."""
    x1 = h.n
    slot = {"A": ONES if a_is_ones else 0, "B": 0 if a_is_ones else ONES}
    pc = "A"
    for region in (h.r1, h.r2):
        a0, cnt = region
        for i in range(cnt):
            mem[a0 + i] = slot[pc]
            if i == cnt - 1:
                break                       # BXCZ,BR1: X1 not counted
            x1 -= 1
            if x1 == 0:
                x1 = h.n
                pc = "B" if pc == "A" else "A"   # A falls into B; B,PHnA
        # BR1 at the split (and at the end, BR1 -> BR2): swap PHnA/PHnB
        slot["A"], slot["B"] = slot["B"], slot["A"]
        pc = "A"
    # the swap at the end is BR2's restore: the slots are as they began


def check_inversions(mem, h):
    """The check loop's four CM1100 on each checked word invert it four
    times: no net change.  Nothing to do to the image."""


def inject(mem, h, c_is_ones):
    """CK1C..CK1D (CK2C..CK2D): X1 = 8 (4), PH1C/PH1D store X8 = ones / 0
    through X2's value, KV against the split, BXEZ to BR8 (X1 not
    counted); BR8 loads the second region and PH1E/PH1F carry on with
    X1 where it was.  Returns X1's count when the upper limit is met."""
    x1 = h.n
    c = ONES if c_is_ones else 0
    slot = {"C": c, "D": ONES ^ c, "E": ONES ^ c, "F": c}
    pc = "C"
    for k, region in enumerate((h.r1, h.r2)):
        a0, cnt = region
        if k == 1:
            pc = "E"
        for i in range(cnt):
            mem[a0 + i] = slot[pc]
            if i == cnt - 1:
                break                       # BXEZ: X1 not counted
            x1 -= 1
            if x1 == 0:
                x1 = h.n
                pc = {"C": "D", "D": "C", "E": "F", "F": "E"}[pc]
    return x1


def single_check(mem, h, x1):
    """CK1D: BR11 inverts each word (CM1100) until CBR on X1 runs out --
    X1's leftover count at the first word, 8 (4) at every other -- then
    BR12 rewrites every word unchanged (CM0011).  An odd count leaves
    the first word inverted."""
    a0 = h.reset[0]
    if x1 % 2:
        mem[a0] ^= ONES


def run_half(mem, h):
    # double-error part: pattern, check, complement, check
    generate(mem, h, True)
    generate(mem, h, False)


def zero_reset(mem, h, upto=None):
    a0, cnt = h.reset
    for i in range(cnt if upto is None else upto):
        mem[a0 + i] = 0


def expected(stage):
    mem, sym = program_image()
    w = lambda name: sym[name] // 64
    start1, start2 = w("START1"), w("START2")
    up, lo = Half(sym, 1), Half(sym, 2)
    # PART I: save 500 words of START2 at START1+500.
    transmit(mem, start2, start1 + 500, 500)
    generate(mem, up, True)
    generate(mem, up, False)
    # SX,$X2,M6AZZ writes the check's X2 into M6AZZ on every check
    # iteration (and Part II likewise M6AZZ2), and the saves and
    # restores carry that word about: it is not computed, so neither it
    # nor any copy of it is compared.
    mem[w("M6AZZ")] = None
    if stage == "CHECK":
        # stopped at BR5's second Z: the swaps restored, one word zeroed
        zero_reset(mem, up, 1)
        return mem, sym
    zero_reset(mem, up)
    x1 = inject(mem, up, True)
    single_check(mem, up, x1)
    x1 = inject(mem, up, False)
    single_check(mem, up, x1)
    if stage == "INJECT":
        zero_reset(mem, up, 1)
        return mem, sym
    zero_reset(mem, up)
    transmit(mem, start1 + 500, start2, 500)
    # PART II: save 900 words from 100 (octal) at START2+500.
    transmit(mem, 64, start2 + 500, 900)
    generate(mem, lo, True)
    generate(mem, lo, False)
    mem[w("M6AZZ2")] = None
    zero_reset(mem, lo)
    x1 = inject(mem, lo, True)
    single_check(mem, lo, x1)
    x1 = inject(mem, lo, False)
    single_check(mem, lo, x1)
    zero_reset(mem, lo)
    transmit(mem, start2 + 500, 64, 900)
    if stage == "PASS":
        return mem, sym
    raise SystemExit(f"unknown stage {stage!r}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    stage = sys.argv[1]
    want, sym = expected(stage)
    got = {}
    stopped = None
    pc = None
    for line in sys.stdin:
        if not line.startswith("MEMDUMP"):
            sys.stdout.write(line)
        m = re.match(r"MEMDUMP (\d+) ([0-9a-fA-F]+)", line)
        if m:
            got[int(m.group(1))] = int(m.group(2), 16)
        elif line.startswith("STOPPED DELIBERATELY"):
            stopped = line.strip()
        m = re.match(r"(?:PASS|FAIL) PC \(half-word address\) = (\d+)", line)
        if m:
            pc = int(m.group(1))
    fails = 0
    # 1. THE PROGRAM'S OWN VERDICT.  "If an error is encountered, the
    # program will stop" (writeup PDF p.1, 2.2): it hangs on one of the
    # four BRGZ,$ after a CT, with the address under check in M6AZZ
    # (Part I) or M6AZZ2 (Part II).  In the complement round the 3-word
    # SWAPI has exchanged the two BRGZ of a half, so the hang is a
    # two-instruction loop between them, not a self-branch.
    hang_at = {
        loc_hw("001041.40"): ("PDF p.6, CK1A's", "M6AZZ", "NOT 1-S"),
        loc_hw("001052.40"): ("PDF p.6, CK1B's", "M6AZZ", "NOT 0-S"),
        loc_hw("100022.40"): ("PDF p.14, CK2A's", "M6AZZ2", "NOT 1-S"),
        loc_hw("100033.40"): ("PDF p.14, CK2B's", "M6AZZ2", "NOT 0-S"),
    }
    if pc in hang_at:
        where, cell, what = hang_at[pc]
        x2 = got.get(sym[cell] // 64)
        addr = "?" if x2 is None else f"{(x2 >> 46) - 1:06o}"
        bad = got.get(int(addr, 8)) if addr != "?" else None
        print(f"FAIL ja_bb6b {stage}: THE PROGRAM HUNG at {where} BRGZ,$ "
              f"(half-word {pc}; printed \"ADDR. AT {cell} IS {what}\", "
              f"which names the unswapped code); {cell} holds X2, one word "
              f"past the word that failed, so the failing word is {addr}"
              + ("" if bad is None else f", which holds {bad:022o}"))
        fails += 1
    if stopped is None:
        print(f"FAIL ja_bb6b {stage}: the run did not stop at its STOPAT point"
              + (f" (PC half-word {pc})" if pc is not None else ""))
        fails += 1
    elif pc is not None and pc not in hang_at:
        print(f"PASS ja_bb6b {stage}: no hang -- the run reached its stop point")
    # 2. THE PASS COUNTER.  "Index Reg 14 is used as a pass counter.
    # Stepping of Index 14 indicates success." (writeup PDF p.2, 3.3).
    # BR14A's M+1(DU,18,4),$X14+0.17 adds a decimal one to the 18-bit
    # field at bits 17-34 of X14 (word 30).  Reference Manual printed
    # pp.62-63 (PDF 65-66): ADD ONE TO MEMORY adds +1 to the storage
    # field; printed p.75 (PDF 78): a field that is not a multiple of
    # the byte size has its SHORT byte at the HIGH-order end.  So the
    # one lands in the low-order byte, bits 31-34, and one pass leaves
    # bit 34 set: X14 = 1 << 29 (its count field reads 2048).
    x14 = got.get(30)
    want14 = (1 << 29) if stage == "PASS" else 0
    if x14 is None:
        print(f"FAIL ja_bb6b {stage}: X14 (word 30) not dumped")
        fails += 1
    elif x14 != want14:
        print(f"FAIL ja_bb6b {stage}: X14 = {x14:022o}, expected {want14:022o}")
        fails += 1
    else:
        print(f"PASS ja_bb6b {stage}: X14, the pass counter, = {x14:022o}")
    # M6AZZ / M6AZZ2: SX,$X2 writes the address under check into them on
    # every check iteration; they are reported, not compared.
    for n in ("M6AZZ", "M6AZZ2"):
        a = sym[n] // 64
        if a in got:
            print(f"     {n} ({a:06o}) = {got[a]:022o}")
        want[a] = None
    regions = [("lower 000040-077777", 32, O("100000")),
               ("upper 100000-277777", O("100000"), TOP)]
    for name, lo, hi in regions:
        known = [a for a in range(lo, hi) if want[a] is not None]
        bad = [a for a in known if a in got and got[a] != want[a]]
        missing = [a for a in known if a not in got]
        if missing:
            fails += 1
            print(f"FAIL ja_bb6b {stage} {name}: {len(missing)} words not dumped")
        if bad:
            fails += 1
            print(f"FAIL ja_bb6b {stage} {name}: {len(bad)} of {len(known)} "
                  f"words differ (first {bad[0]:06o}, last {bad[-1]:06o})")
            for a in bad[:6]:
                print(f"     {a:06o}: model {got[a]:022o}  expected {want[a]:022o}")
        else:
            print(f"PASS ja_bb6b {stage} {name}: all {len(known)} words "
                  f"the program has reached are as expected")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
