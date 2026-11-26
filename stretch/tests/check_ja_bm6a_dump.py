#!/usr/bin/env python3
"""check_ja_bm6a_dump.py -- the pass/fail judge for IBM's JA BM6A
unique-address test (../decks/ja_bm6a_unique_adr.strap), reading a
core dump taken by run_ja_bm6a.sh.

WHAT THE PROGRAM ITSELF CALLS PASS AND FAIL (writeup, PDF pp.1-2):
  - "Errors encountered will be printed out on the typewriter, giving
    the memory box in error, the memory location tested, and the
    location actually obtained." (p.1, 2.2)
  - "Continuous operation with print out O.K. every 100 passes
    indicates success." (p.2, 3.3)

THE TYPEOUT CANNOT BE READ ON THE MODEL (run_ja_bm6a.sh: the program's
TYPE is channel 39, the model's console is 35, so every W is a Unit Not
Ready reject).  But the error routine BUILDS the message in core before
it writes it, and that is what is checked here, PDF pp.5-6 and 8-10:
ERROR1/ERROR2 store the box digit into MSGC1/MSGC2, the tested
address's six octal digits into MSGD1/MSGD2 and the obtained address's
into MSGE1/MSGE2, from the binary copies in ERADP1/ERADP2; and SIC
writes the return into EXIT1/EXIT2 only when the BRGZ to the error
routine is taken (Reference Manual printed pp.41-42: the store "is
executed if and only if the associated branching is successful", and
the stored counter addresses the instruction after the branch).  None of those words is written on the no-error path.
So "the program found no error" is: every one of them still holds its
assembled value.  If one does not, the message is decoded and printed.

THE 100-PASS "O.K." IS NOT REACHED.  One pass is ~13 instructions over
98,240 words; see run_ja_bm6a.sh for the measured clocks.  The suite
stops after one pass; the O.K. path (100023.00 onward) is not run.

INDEPENDENTLY OF THE PROGRAM, every word of core from 32 up is
compared with the image computed from the program's own steps, written
from the listing and the Reference Manual, not from the model:
  The word stored at address A ("the address of each location is
  stored into that location, along with the complement of the address
  and padding bits", writeup PDF p.2, 4):
    SX,$X3,$R puts X3 -- value field A.00, everything else zero (Z,
    then LVI) -- into the right accumulator word, so its bits 0-17 are
    A.  C1100(BU,18,8),$R,14 connects that 18-bit field with the
    accumulator field whose right end is 14 bits from the right end of
    the accumulator (Reference Manual printed p.56: the offset
    "specifies the number of bits by which the right end of the
    accumulator operand is offset from the right end of the
    accumulator"), i.e. right-word bits 32-49; connective 1100 over
    (memory, accumulator) = 00,01,10,11 (Reference Manual printed p.76,
    Figure 20's bit order; StretchExecute.bsv's connective comment) is
    NOT memory, so those bits become ~A.  ST(BU,64,8),0($X4) stores the 64-bit accumulator field
    at offset 0 -- the right word -- at A.  +I(BU,18,8),1.,46 adds 1
    to the field ending 46 bits from the right, right-word bits 0-17.
    So  word(A) = A in bits 0-17, ~A in bits 32-49, zeros elsewhere.
  Part I  (low core): T 100 words PHA2 -> PHA1+100. (001152), write
          word(A) for A = 100000-277777, check, T them back to PHA2.
  Part II (100000): T 612 words 100 -> PHA2+100. (100144), write
          word(A) for A = 100-77777, check, T them back to 100.
  The next pass begins with Part I's 100-word save again.

MEASURED ON THE MODEL (2026-11-25): UPPER and PASS both PASS -- no
error message, and every reached word as expected (65,051 upper words;
32,219 lower in PASS).

INJECTION RECORD (discriminating; measured 2026-11-25, then reverted by
the inverse patch and `git diff` confirmed clean).  StretchMemory.bsv's
route rule made address 200005 decode as 200001 for reads and writes
alike (the same unit, so canAccept is unchanged) -- an address-decode
alias, the fault this test exists to find:
  UPPER  FAIL  the program took its error path -- ERADP1, MSGC1, MSGD1,
               MSGE1, EXIT1 changed; its message decodes as
               "BOX NO. 4  ADDR 200001  THE ADDR OBTAINED IS 200005"
         FAIL  lower: 5 of 169 words differ (001070 EXIT1, 001104
               MSGC1, 001105 MSGD1, 001111 MSGE1, 001115 ERADP1)
         FAIL  upper: 6 of 65051 words differ -- 200001 (it holds
               200005's word) and 101134-101161, Part II's saved copy of
               those same five words
  PASS   FAIL  the same message, the same five changed words
         FAIL  lower: 5 of 32219 words differ (the same five)
         FAIL  upper: 6 of 65051 words differ (the same six)
         (the run stopped at 46,944,892 clocks; 35,388,608 clean)
Nothing else failed.  The alias is invisible at 200005 itself: its
reads go to 200001, which holds 200005's word.
A SECOND INJECTION, IN THE LOWER MEMORIES (same day, same revert): 040005
decoding as 040001 (one unit, above the 612-word save area):
  UPPER  PASS  (Part I never reaches it)
  PASS   FAIL  the program took its error path -- ERADP2, MSGC2, MSGD2,
               MSGE2, EXIT2 changed; its message decodes as
               "BOX NO. 2  ADDR 040001  THE ADDR OBTAINED IS 040005"
         FAIL  lower: 6 of 32219 words differ -- 040001, and 001241-
               001265, the next pass's 100-word save of those five words
         FAIL  upper: 5 of 65051 words differ (100067 EXIT2, 100076
               MSGC2, 100077 MSGD2, 100103 MSGE2, 100113 ERADP2)
Nothing else failed.
THE BOX DIGIT, AN OPEN QUESTION: for 200001 (low bits 01) the message
says 4.  L(BU,2,2),$X4+.16 takes the address's low two bits and
ST(BU,2,8),$X8+.18 stores them at bits 18-19 of the character pointer,
i.e. in units of TWO characters, and Part I then adds PLS02 = 16 bits
(PDF p.5): digit = 2b + 2, so 2, 4, 6 and, for b = 3, a byte past the
NOCOM2 table.  Part II, with no PLS02, gave 2 for 040001 (b = 1):
digit = 2b.  A numbering of the B boxes 2-5 would want b + 2.
Whether the 7030 stores a length-2 field with byte size 8 differently
from this model's reading is not settled here.

Usage: run_program.sh ... | check_ja_bm6a_dump.py STAGE
  STAGE is  UPPER -- Part I done, Part II's save done
            PASS  -- one whole pass, and the next pass's save
Prints PASS/FAIL lines and exits non-zero on any FAIL.
"""

import re
import sys

from strap_asm import assemble
from verify_ja_bm6a_listing import image_source

O = lambda s: int(s, 8)
TOP = 98304                      # installed words (six 16K units)
FIRST = 32                       # = octal 40; words 0-31 are registers, not dumped
M18 = (1 << 18) - 1


def word_for(a):
    return (a << 46) | (((~a) & M18) << 14)


def program_image():
    prog = assemble(image_source())
    mem = [None] * TOP           # None: never loaded or stored, not compared
    for a, w in prog.words.items():
        mem[a] = w
    return mem, prog.symtab


def transmit(mem, src, dst, n):
    for i in range(n):
        mem[dst + i] = mem[src + i]


def expected(stage):
    mem, sym = program_image()
    w = lambda name: sym[name] // 64
    pha1, pha2 = w("PHA1"), w("PHA2")
    # Part I
    transmit(mem, pha2, pha1 + 100, 100)
    for a in range(O("100000"), TOP):
        mem[a] = word_for(a)
    transmit(mem, pha1 + 100, pha2, 100)
    # Part II's save
    transmit(mem, 64, pha2 + 100, 612)
    if stage == "UPPER":
        return mem, sym
    # Part II
    for a in range(64, 32768):
        mem[a] = word_for(a)
    transmit(mem, pha2 + 100, 64, 612)
    # the next pass's save
    transmit(mem, pha2, pha1 + 100, 100)
    if stage == "PASS":
        return mem, sym
    raise SystemExit(f"unknown stage {stage!r}")


# The words only the error path writes (see the docstring).
ERROR_WORDS = [
    ("ERADP1", 1), ("MSGC1", 1), ("MSGD1", 1), ("MSGE1", 1), ("EXIT1", 1),
    ("ERADP2", 1), ("MSGC2", 1), ("MSGD2", 1), ("MSGE2", 1), ("EXIT2", 1),
]


def digits(word):
    """The six characters the error routine stores in bytes 0-5, decoded
    through NOCOM2's table (60 62 64 66 68 6A 6C 6E = 0-7)."""
    out = ""
    for i in range(6):
        b = (word >> (56 - 8 * i)) & 0xFF
        out += str((b - 0x60) // 2) if 0x60 <= b <= 0x6E and b % 2 == 0 else f"[{b:02X}]"
    return out


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    stage = sys.argv[1]
    want, sym = expected(stage)
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
        print(f"FAIL ja_bm6a {stage}: the run did not stop at its STOPAT point")
        fails += 1
    missing = [a for a in range(FIRST, TOP) if a not in got]
    if missing:
        print(f"FAIL ja_bm6a {stage}: {len(missing)} words not dumped "
              f"(first {missing[0]:06o})")
        fails += 1

    # 1. THE PROGRAM'S OWN VERDICT: did it compose an error message?
    changed = [(n, sym[n] // 64) for n, _ in ERROR_WORDS
               if sym[n] // 64 in got and got[sym[n] // 64] != want[sym[n] // 64]]
    if changed:
        fails += 1
        print(f"FAIL ja_bm6a {stage}: the program took its error path -- "
              f"{', '.join(n for n, _ in changed)} changed")
        for part in ("1", "2"):
            c, d, e = (got.get(sym[f"MSG{x}{part}"] // 64) for x in "CDE")
            if any(got.get(sym[n] // 64) != want[sym[n] // 64]
                   for n in (f"MSGC{part}", f"MSGD{part}", f"MSGE{part}")):
                # ST(BU,8,8),MSGCn puts the box character in byte 0.
                print(f"     ERROR{part} message: BOX NO. {digits(c)[0:1] if (c >> 56) in range(0x60, 0x6F, 2) else '?'}"
                      f" (byte {(c >> 56) & 0xFF:02X})"
                      f"  ADDR {digits(d)}  THE ADDR OBTAINED IS {digits(e)}")
    else:
        print(f"PASS ja_bm6a {stage}: no error message composed (ERADP, "
              f"MSGC/D/E and EXIT of both halves hold their assembled words)")

    # 2. THE WHOLE IMAGE.
    regions = [("lower 000040-077777", FIRST, O("100000")),
               ("upper 100000-277777", O("100000"), TOP)]
    for name, lo, hi in regions:
        known = [a for a in range(lo, hi) if want[a] is not None]
        bad = [a for a in known if a in got and got[a] != want[a]]
        if bad:
            fails += 1
            print(f"FAIL ja_bm6a {stage} {name}: {len(bad)} of {len(known)} "
                  f"words differ (first {bad[0]:06o}, last {bad[-1]:06o})")
            for a in bad[:6]:
                print(f"     {a:06o}: model {got[a]:022o}  expected {want[a]:022o}")
        else:
            print(f"PASS ja_bm6a {stage} {name}: all {len(known)} words "
                  f"the program has reached are as expected")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
