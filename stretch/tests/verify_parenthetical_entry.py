#!/usr/bin/env python3
"""verify_parenthetical_entry.py -- STRAP's PARENTHETICAL INTEGER
ENTRY MODE, "(.n)A" (../decks/parenthetical_entry.strap).

C28-6129 Section II, printed pp.25-26 (PDF 29-30), heading "Field
Entry Mode", read first-hand 2026-10-22 BEFORE a line of this was
written (AGENTS.md rule 4).  The specification, quoted:

  "A final STRAP entry mode that is used as a field entry mode is the
   parenthetical integer entry mode.  This mode permits any integer
   or pattern of bits to be stored in any bit position of an
   instruction or pseudo operation that produces binary output.  The
   general format for this entry mode is:  (.n)A(n+1)
   The symbol .n represents the BIT ADDRESS OF THE RIGHTMOST BIT of
   the field into which the integer or bit pattern is to be entered.
   The integer A(n+1) is formed as an unsigned field, n+1 bits in
   length (because of the 7030 custom of addressing bits starting
   with zero), and inserted into the leftmost n+1 bits of the
   addressed instruction or data entry field by means of a LOGICAL OR
   type operation.  Logical OR is used so that the parenthetical
   entry may be combined with the existing contents of the particular
   field addressed or with other parenthetical entries."

and the rules that go with it, all on those two pages:

  - "in the case of an instruction, the position of the entry is
     determined by counting bits from the beginning of the
     instruction, starting with bit zero, NO MATTER IN WHICH SUBFIELD
     of the instruction the integer entry may be written."
  - "the parenthetical entry must follow all other information in the
     field in which it does appear."
  - "<= 31 in a half word instruction, or 63 in a full word
     instruction... a maximum of 24 significant bits can be converted
     in a parenthetical entry."
  - "evaluated modulo 2**(n+1).  All parenthetical fields are regarded
     as unsigned by STRAP, so that a negative number is compiled as
     the complement, re 2**(n+1), of the magnitude of the number."
  - "This entry mode must appear in a statement that compiles space in
     storage.  Therefore, this mode cannot be used in pseudo
     operations that give instructions to the compiler but result in
     no binary output (SCL, DDI, END, etc.)."

>>> THE FEATURE EXISTS BECAUSE TWO MCP ROWS NEED IT, and one of them
had been WORKED AROUND for four months.
decks/mcp_bootstrap_p7_p8.strap's "substitution (a)" wrote printed
p.8 line 34's "CW,X ZEROS,3,X MSG CW(.25)1" as "CW(CCR),X ZEROS,3,X
MSG CW", saying in as many words that "inventing their general
semantics from one row is what AGENTS.md rule 4 forbids".  That was
correct.  The semantics are now printed, the row is verbatim, and
CHECK C6 is the equality the old note asserted. <<<

>>> IT CANNOT DISTURB ANYTHING THAT EXISTS.  Before the splitter was
switched on, its regular expression was run over every statement
field of every deck in decks/: 24,073 fields parsed, ZERO matches.
The only rows the mode can reach are the ones written for it. <<<
"""
import sys

from strap_asm import assemble, AssemblerError
from listing_oracle import word_at

prog = assemble(open("../decks/parenthetical_entry.strap").read())
fails = 0


def check(name, got, want, note):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} pent {name}: {note}: "
          f"assembled {got:#018x}, expected {want:#018x}")


def full(sym):
    return word_at(prog, prog.symtab[sym])


def half(sym):
    return (full(sym) >> 32) & 0xFFFFFFFF


# C1.  THE MANUAL'S OWN INSTRUCTION EXAMPLE, printed p.25: "In the
# following instruction: E+I, (.8)41 the integer 41 is converted to
# binary and OR'ed into the first nine bits of the E+I instruction."
# "E+I, 0" alone compiles 0x00002760 -- every bit of the first nine
# is zero -- so the expected word is that opcode with 41 placed with
# its rightmost bit AT BIT 8, i.e. shifted left by 32-9.
check("C1", half("M1"), 0x00002760 | (41 << (32 - 9)),
      "E+I, (.8)41 -- the manual's own example, 41 in bits 0-8")

# C2/C3.  printed p.26 writes the same word two ways: "+(BU),
# DATA(.23)4, 20" and "+(BU), DATA, 20(.23)4".  "In either use the
# result would be the same" -- because .n counts from the start of
# the INSTRUCTION and not from the field the entry is written in.
BASE = 0x0010008000029010          # "+(BU), DATA, 20", DATA = 0o100.0
check("C2", full("M2"), BASE | (4 << (64 - 24)),
      "+(BU), DATA(.23)4, 20 -- entry on the address field")
check("C3", full("M3"), BASE | (4 << (64 - 24)),
      "+(BU), DATA, 20(.23)4 -- same word, entry on the offset field")

# >>> C2 AND C3 ARE ALSO THE "OR, NOT STORE" CHECK, which is the
# whole reason the manual specifies a logical OR.  Bits 0-23 already
# hold DATA = 001000; the entry adds 4 and the field must read
# 001004.  A store would leave 000004 and lose the address. <<<
# DATA is SYN'd to (8)100.0, and a VFL address field holds a 24-bit
# BIT address, so the field reads 0o100 * 64 = 4096 and the entry
# adds 4 to it.
check("C2b", (full("M2") >> 40) & 0xFFFFFF, (0o100 * 64) | 4,
      "the 24-bit address field is DATA OR 4, not 4")

# C4.  "Logical OR is used so that the parenthetical entry may be
# combined ... with OTHER PARENTHETICAL ENTRIES."  Two in a row, in
# different bits: (.23)4 is a one in bit 21, so the second is written
# at bit 20 -- with both at 21 the check would pass if either were
# dropped.
check("C4", full("M4"), BASE | (4 << (64 - 24)) | (1 << (64 - 21)),
      "20(.23)4(.20)1 -- consecutive entries OR together")

# C5.  "All parenthetical fields are regarded as unsigned by STRAP,
# so that a negative number is compiled as the complement, re
# 2**(n+1), of the magnitude of the number."  -1 in (.3) is a 4-bit
# field of ones.
check("C5", half("M5"), 0x00002760 | (0xF << (32 - 4)),
      "E+I, 0(.3)-1 -- complement re 2**4, four ones in bits 0-3")

# C6.  MCP printed p.8 line 34 and printed p.30 line 27 are both
# "CW,...,X ... CW(.25)1".  C28-6129 printed p.14's CCR, "Chain
# Counts Within Record", is chain 1 / multiple 0 / skip 0 -- the same
# three bits.  THE TWO SPELLINGS MUST COMPILE THE IDENTICAL WORD, and
# that equality was asserted in a deck comment for four months before
# anything could check it.
ccr = assemble("        SLC, (8)1004.0\n"
               "X       CW(CCR), (8)1037.0, 3, (8)1574.0\n"
               "        END, X\n")
check("C6", full("M6"), word_at(ccr, ccr.symtab["X"]),
      "CW,...(.25)1 compiles what CW(CCR),... compiles")

# C7.  And that word is the one MCP's listing prints on p.30 line 27:
# 001037.00+ 100 000003 001574.  The flag group is "100": bit 25 on,
# 26 and 27 off.
check("C7", (full("M6") >> (64 - 28)) & 0b111, 0b100,
      "the flag group of the compiled control word is 100")

# ---------------------------------------------------------------
# REFUSALS.  Each is a sentence of the manual, and each must FAIL.
# ---------------------------------------------------------------
REFUSALS = [
    ("R1", "(.63) in a half-word statement",
     "        SLC, (8)1000.0\nH       E+I, 0(.63)1\n        END, H\n",
     "needs 64 bits but this statement compiles only 32"),
    ("R2", "more than 24 significant bits",
     "        SLC, (8)1000.0\nH       +(BU), 0(.63)16777216\n        END, H\n",
     "more than the 24 significant bits"),
    ("R3", "in SLC, which compiles no storage",
     "        SLC, (8)1000.0(.25)1\nH       E+I, 0\n        END, H\n",
     "produces no binary output"),
    ("R4", "in END, which compiles no storage",
     "        SLC, (8)1000.0\nH       E+I, 0\n        END, H(.25)1\n",
     "produces no binary output"),
    ("R5", "an entry with no value after it",
     "        SLC, (8)1000.0\nH       E+I, 0(.25)\n        END, H\n",
     "has no value after it"),
]
for name, note, src, fragment in REFUSALS:
    try:
        assemble(src)
        print(f"FAIL pent {name}: {note}: assembled, should have been refused")
        fails += 1
    except AssemblerError as e:
        ok = fragment in str(e)
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} pent {name}: {note}: refused with {e}")

# R6.  The bound is the STATEMENT's size, not a constant: (.63) is
# legal on a full word and lands in the last bit.
legal = assemble("        SLC, (8)1000.0\nH       +(BU), 0(.63)1\n        END, H\n")
check("R6", word_at(legal, legal.symtab["H"]),
      0x0000008000001010 | 1,
      "(.63)1 IS legal on a full-word statement and sets bit 63")

# ---------------------------------------------------------------
# R7-R10.  AN ENTRY AT THE MAXIMUM WIDTH, WITH SOMETHING AFTER IT.
#
# Image.or_into marks the bits it touches in Image._written, the same
# bookkeeping deposit() uses to refuse two statements overlapping.
# That is what catches a misplaced entry (see run_tests.sh's I5 and
# I7) -- and it means a LEGITIMATE entry spanning a statement's whole
# storage must still leave the NEXT statement able to deposit.  Every
# check above is on a deck whose last row is the widest one, so none
# of them tests that.  These do.
# ---------------------------------------------------------------
SPANS = [
    ("R7", "(.63)1 on a full word, with a successor statement",
     "        SLC, (8)1000.0\nH       +(BU), 0(.63)1\nK       +(BU), 0\n        END, H\n",
     {0o1000: 0x0000008000001011, 0o1001: 0x0000008000001010}),
    ("R8", "(.31)1 on a half word, with a successor half word",
     "        SLC, (8)1000.0\nH       E+I, 0(.31)1\nK       E+I, 0\n        END, H\n",
     {0o1000: 0x0000276100002760}),
    ("R9", "the same pair starting in the SECOND half word",
     "        SLC, (8)1000.40\nH       E+I, 0(.31)1\nK       E+I, 0\n        END, H\n",
     {0o1000: 0x0000000000002761, 0o1001: 0x0000276000000000}),
    ("R10", "an entry written in place of a whole field",
     "A       SYN, (8)200.0\nB       SYN, (8)300.0\n        SLC, (8)1000.0\n"
     "H       TI, (.31)1, A, B\n        END, H\n",
     {0o1000: 0x00200081003000A0}),
]
for name, note, src, want in SPANS:
    try:
        got = assemble(src).words
    except AssemblerError as e:
        print(f"FAIL pent {name}: {note}: refused with {e}")
        fails += 1
        continue
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} pent {name}: {note}: "
          f"assembled { {k: '%016X' % v for k, v in sorted(got.items())} }")

if fails:
    print(f"{fails} TEST(S) FAILED")
    sys.exit(1)
print("ALL TESTS PASSED")
