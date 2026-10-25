"""MCP INITIALIZATION, printed p.77 -- SCAN THE PP REF TABLE FOR NEW
ASSIGNMENTS.

Forty-one lines, thirty-two of which compile, under one boxed
heading.  decks/mcp_bootstrap_p77.strap carries the derivations.

>>> IT IS T SCRIB, AND printed p.75 BRANCHES TO IT FOUR TIMES. <<<
Line 6 is 004461.00 = T SCRIB, and FOUR of p.75's ten dispatch exits
-- T D, T F, T G and T K -- are "B,T SCRIB".  Four ways for ASSIGN
to finish, one place to go afterwards, and this page is what happens
there.

>>> printed p.47's LINKAGE FORMAT, USED FOR REAL. <<<  p.47 compiles
nothing and is THE DECODE PROGRAM LINKAGE FORMAT written out as a
worked call.  Lines 17-24 are that call in live code: SX,$15,T PSAV
/ LVI,$15,T P6A / BD,S A8IQS / VF,T P5IN / CF,8 / VF,T P5OUT /
BE,$+.32 / LF(BU,64,8),T P5OUT.  VF, CF, VF -- first word address
in, count, first word address out -- is p.47's block exactly, and
$15 is the linkage register p.59 names.  THE DOCUMENTATION PAGE AND
THE CALL SITE ARE THIRTY PAGES APART and agree field for field.

AND "BD,S A8IQS" IS A BRANCH, NOT A HALT.  printed p.75 has five
"BD,$" rows that stop the machine only because the target is the
instruction's own address; here the same operation enters a
subroutine with interruptions off.

>>> AN `E` READ AS AN `L`, AND THE GLYPH IS THE LAST WITNESS. <<<
Line 23 prints "BL,$+.32" at 1800 dpi -- a vertical stroke and a
bottom bar, no top bar, no middle bar.  It is BE.  (1) BL is not a
mnemonic: the unconditional branch family is B, BD, BE, BEW, BR,
NOP.  (2) "BE,$+.32" at 004474.00 produces 004474.40 00, the printed
row exactly.  (3) printed p.78 line 40 is the twin, "T IPLB2
BE,$+.32", same operation, same J field 0000, same comment "-MODIFIED
BY IPL".  So the stroke-dropping artifact is not about digits.
listing_typography.md 13i carries it.

T IPLB1 was already a stand-in at 004474.00 and this page places it.
Its comment says the IPL MODIFIES that row -- a branch the loader
patches -- which is why it has a name at all.  T XA, T XB and T XC
are printed p.76's SYN cards: the data page feeds this one
immediately.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  Line 23's BE becomes BD -- 1 FAIL at 004474.00, reading
  004474.44 00 for 004474.40 00.  ONE BIT, bit 23, separates the
  enabled branch from the disabled one, which is why the glyph
  could not be trusted and the assembled value could.
  Line 23's "$+.32" becomes "$+.40" -- SURVIVES, and the survival
  is a fact about the encoding: a branch address is nineteen bits,
  word plus half-word selector, so EVERY offset from 32 to 63 bits
  names the same target.  The deck could have written .32, .40 or
  .50 and the listing could not tell them apart; .32 is what the
  card says.
  T PNAME's byte size 6 becomes 8 -- 1 FAIL at 004467.00, reading
  060000 for 060600.  The byte size is three bits at 2^6 in the
  second group, so a 6 prints 600 and an 8 prints 000 (eight is
  zero modulo eight -- C28-6129 printed p.16).
  Line 21's count field 8 becomes 10 -- 1 FAIL at 004473.00,
  reading 000012 for 000010.  The CF row prints its value in octal
  with no address or byte, which is what makes the linkage block
  legible at all.
  Line 19's BD becomes a plain B -- 1 FAIL at 004472.00, reading
  002366.10 00 for 002366.04 00.  The J field moves from 0001 to
  0100; the "halt-shaped" operation and the ordinary branch differ
  only there.
  Line 38's BZB1 becomes BZB -- 1 FAIL at 004506.00, reading
  004511.34 00 for 004511.34 0C.  The same pair printed p.74 line
  38 got wrong first.
  Line 35's LV takes T XB where the row names T XC -- 1 FAIL at
  004504.00, reading 33 for 34.  The index modifier is the opcode
  byte's low nibble and nothing else on the row moves.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p77.strap").read())

SYMBOLS = {
    # The address four of printed p.75's dispatch exits branch to.
    "TSCRIB": "004461.00",
    # Labels this page defines.
    "TP6":    "004461.40",
    "TP6A":   "004472.40",
    "TIPLB1": "004474.00",
    "TP5":    "004477.00",
    "TP5Z":   "004500.40",
}

ROWS = [
    ("004461.00", "003315.04 10",
     "line 6   T SCRIB  LX,TXA,TPPRUN"),
    ("004461.40", "000000.47 82  004600.34 02",
     "line 7   T P6  BB,TLPPEN(TXA),TP1"),
    ("004462.40", "000000.44 82  004576.34 02",
     "line 8   BB,TJBPRO(TXA),TP2"),
    ("004463.40", "000000.45 82  004576.34 02",
     "line 9   BB,TRJECT(TXA),TP2"),
    ("004464.40", "000000.06 32",
     "line 11  LV,TXB,TCRREF(TXA)"),
    ("004465.00", "000000.34 82  010027.20 50",
     "line 12  L,TUNCT(TXA),46"),
    ("004466.00", "000011.06 50",
     "line 13  LC,TXB,$R"),
    ("004466.40", "004576.30 42",
     "line 14  BXCZ,TP2"),
    ("004467.00", "000001.00 82  060600.06 70",
     "line 15  LF,TPNAME(TXA)"),
    ("004470.00", "004456.00 80  000000.12 F0",
     "line 16  SF(BU,64,8),TP5IN"),
    ("004471.00", "004460.37 10",
     "line 17  SX,$15,TPSAV"),
    ("004471.40", "004472.77 01",
     "line 18  LVI,$15,TP6A"),
    ("004472.00", "002366.04 00",
     "line 19  BD,SA8IQS"),
    ("004472.40", "004456.00+",
     "line 20  T P6A  VF,TP5IN"),
    ("004473.00", "000010",
     "line 21  CF,8"),
    ("004473.40", "004457.00+",
     "line 22  VF,TP5OUT"),
    ("004474.00", "004474.40 00",
     "line 23  T IPLB1  BE,$+.32"),
    ("004474.40", "004457.00 80  000000.06 70",
     "line 24  LF(BU,64,8),TP5OUT"),
    ("004475.40", "004460.36 10",
     "line 25  LX,$15,TPSAV"),
    ("004476.00", "004450.00 80  000000.12 F0",
     "line 26  SF,TPID"),
    ("004477.00", "000000.22 83  004500.74 00",
     "line 28  T P5  BZB,TLAST(TXB),TP5Z"),
    ("004500.00", "003373.07 01",
     "line 29  LVI,TXB,TIOREQ"),
    ("004500.40", "000000.00 83  004575.74 00",
     "line 30  T P5Z  BZB,TASGNI(TXB),TP3"),
    ("004501.40", "000000.03 83  004575.74 00",
     "line 31  BZB,TTYPE(TXB),TP3"),
    ("004502.40", "000000.56 83  022027.20 50",
     "line 33  L,TABSCH(TXB),46"),
    ("004503.40", "000011.10 30",
     "line 34  LV,TXC,$R"),
    ("004504.00", "000000.10 34",
     "line 35  LV,TXC,0.0(TXC)"),
    ("004504.40", "000000.07 83  003027.20 50",
     "line 36  L,TABSUN(TXB),46"),
    ("004505.40", "000011.10 B0",
     "line 37  V+,TXC,$R"),
    ("004506.00", "000000.02 83  004511.34 0C",
     "line 38  BZB1,TPRINT(TXB),TP5A"),
    ("004507.00", "000000.76 84  004575.74 00",
     "line 40  BZB,TUNRES(TXC),TP3"),
    ("004510.00", "000000.02 83  004575.74 06",
     "line 41  BBZ,TPRINT(TXB),TP3"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.77 ")
finish(fails)
