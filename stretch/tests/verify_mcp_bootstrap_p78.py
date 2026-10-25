"""MCP INITIALIZATION, printed p.78 -- CONVERT THE CHANNEL FIELDS.

Fifty-six lines, forty-five of which compile, under one boxed
heading.  It builds the mounting message printed p.76 holds the
buffers for: the channel number and unit number converted to IQS
characters, the reel number through the same conversion routine
printed p.77 calls, and the tape's mounted/verify/scratch bits.
decks/mcp_bootstrap_p78.strap carries the derivations.

>>> FOUR ROWS CARRY A `$` BEFORE THE OPERATION, AND THIS DECK DOES
NOT WRITE IT.  READ THIS BEFORE TRUSTING LINES 9-12. <<<

The cards read "$L,T ABSCH(T XB),-60", "$-(BU,18),T CHSXW,-60",
"$SF(BU,18),T IPL+1,-60" and "$CV(BU,18),0.0,-32" -- confirmed at
1200 dpi, the "$" being the first character of the OPERATION field,
on four consecutive rows and nowhere else on the page.  This deck
writes L, -, SF and CV.  Why:

1. NO SOURCE THIS PROJECT HAS DESCRIBES IT.  C28-6129 printed
   pp.3-4 give all TWELVE STRAP-II symbolic instruction formats and
   not one has a prefix on the operation; its April 1963 bulletin
   lists no such addition; c22_6531_appendix_a.md's footnotes are
   all about SUFFIXES, its only "$" rule being that a SYSTEM SYMBOL
   must be prefixed by "$" (which is the $L on line 13, an
   operand); and C22-6729's Appendix B -- the complete list of
   additional instructions and pseudo-ops STRAP II accepts -- and
   its Appendix D have nothing.

2. A COPROCESSOR DOES NOT EXPLAIN IT.  C22-6729 printed p.180 lets
   Pass 1 hand an ILLEGAL OPERATION CODE to an installation
   subroutine, which would admit an undocumented operation.  But
   that is an ERROR path and STRAP II would have flagged the row.
   These four compiled to correct machine code with no error
   indication: STRAP II UNDERSTOOD THEM.

3. AND THE PREFIX CONTRIBUTES NOTHING TO THE BITS -- MEASURED, FOUR
   FOR FOUR.  Each row assembled from the UNPREFIXED mnemonic
   reproduces the printed row: 022042.20 50, 022042.30 10,
   022042.12 F0 and 022060.21 B0.  Two operation classes, four
   different second-group bytes, and line 10 is a written minus
   carrying its ".30".  One row matching would be a coincidence;
   four across three encodings is a measurement.

So the deck is bit-exact and says nothing about what "$" means.  If
the meaning turns up, LINES 9-12 ARE THE ROWS TO REVISIT.

THE NEGATIVE OFFSETS, HOWEVER, ARE FULLY EXPLAINED.  C28-6129
printed p.3's format 7 is "OP(dds), A24(I), OF7(I')" -- the offset
field is SEVEN BITS and therefore signed.  "-60" compiles to 042:
minus sixty halved is minus thirty, and minus thirty in six bits
two's complement is 0o42.  Nothing about the minus needed the
prefix.

A THIRD INSTANCE OF TWO OPERATIONS SHARING A BYTE: line 12's CV
compiles ".21 B0" and printed p.73 line 55's M+1 compiles ".22 B0".
CV is VFL operation 27 and M+1 is 43; the low four bits are the
byte's high nibble (1011 for both) and the high bits sit in bits
22-23 of the second group, 16 for CV and 32 for M+1.  printed p.72's
"*" and "M+" were the first such pair; this is the third, and the
model has not needed a change since p.73.

T P5A and T IPLB2 were ALREADY STAND-INS -- printed p.77 line 38
branches to T P5A at 004511.00, and p.77's T IPLB1 is this page's
T IPLB2's twin, both "BE,$+.32  -MODIFIED BY IPL" -- and both agree.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  Line 14's odd offset 5 becomes 4 -- 1 FAIL at 004520.00, reading
  402002.06 70 for 402002.46 70.  ONLY BIT 18 MOVES, which is the
  whole of the finding: the VFL offset is SEVEN bits, bits 12-17 of
  the second group holding offset>>1 and bit 18 holding offset&1.
  Four and five share their high six bits and differ only there,
  so this injection is the seven-bit field demonstrated in one row.
  Line 9's offset -60 becomes +60 -- 1 FAIL at 004513.00, reading
  022036 for 022042.  Sixty halved is 030 and minus sixty in seven
  bits two's complement is 68, halved 042; the printed field
  carries the sign.
  Line 12's CV becomes M+1 -- 1 FAIL at 004516.00, reading
  022060.22 B0 for 022060.21 B0.  THE BYTE DOES NOT MOVE.  CV is
  operation 27 and M+1 is 43; both have 1011 in their low four
  bits, so both print B0, and the 16 and the 32 are bits 23 and 22
  of the second group.  One bit apart, third instance of that shape
  after printed p.72's * and M+.
  Line 10's written minus becomes a plus -- 1 FAIL at 004514.00,
  reading 022042.20 for 022042.30.
  T CHANX's stand-in loses the dds printed p.76 gives it -- 1 FAIL
  at 004522.00, reading 000000 for 030000.  The length comes from
  the SYMBOL, not the card, exactly as C22-6531 printed p.31 says,
  and p.76 line 15's "(IQS*)DD(BU,24,8)" is where it comes from.
  T LBL's byte size 6 becomes 8 -- 1 FAIL at 004532.00, reading
  006030 for 006630.
  Line 13's $L operand becomes $R -- 1 FAIL at 004517.00, reading
  000011 for 000010.  The two halves of the accumulator are words
  8 and 9, adjacent, and this is the row that reads one of them as
  memory.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p78.strap").read())

SYMBOLS = {
    # The address printed p.77 line 38 branches to.
    "TP5A":   "004511.00",
    # Labels this page defines.
    "TP5A1":  "004513.00",
    "TP5A2":  "004534.40",
    "TP5A3":  "004537.00",
    "TIPLB2": "004540.40",
    "TPSCR":  "004551.00",
}

ROWS = [
    ("004511.00", "000000.24 1F",
     "line 5   T P5A  LX,TCTWDX,0.0($15)"),
    ("004511.40", "004513.23 40",
     "line 6   BZXF,TP5A1"),
    ("004512.00", "003370.05 04",
     "line 7   KVI,TXA,TPURFT"),
    ("004512.40", "004575.72 C0",
     "line 8   BZXE,TP3"),
    ("004513.00", "000000.56 83  022042.20 50",
     "line 9   T P5A1  $L,TABSCH(TXB),-60"),
    ("004514.00", "002152.00 80  022042.30 10",
     "line 10  $-(BU,18),TCHSXW,-60"),
    ("004515.00", "003266.01 80  022042.12 F0",
     "line 11  $SF(BU,18),TIPL+1,-60"),
    ("004516.00", "000000.00 80  022060.21 B0",
     "line 12  $CV(BU,18),0.0,-32"),
    ("004517.00", "000010.24 80  014400.46 70",
     "line 13  LF(BU,12,4),$L+.20,1"),
    ("004520.00", "600000.00 80  402002.46 70",
     "line 14  LFI(BU,2),3,5"),
    ("004521.00", "600000.00 80  402006.46 70",
     "line 15  LFI(BU,2),3,13"),
    ("004522.00", "004440.10 80  030000.12 F0",
     "line 16  CM0101,TCHANX"),
    ("004523.00", "000000.07 83  003000.46 70",
     "line 18  C0011,TABSUN(TXB),1"),
    ("004524.00", "600000.00 80  402002.46 70",
     "line 19  LFI(BU,2),3,5"),
    ("004525.00", "004441.20 80  010000.12 F0",
     "line 20  CM0101(BU,8,8),TUNITX"),
    ("004526.00", "000000.50 84  001000.36 F0",
     "line 23  CM1111,TVER(TXC)"),
    ("004527.00", "000000.34 83  022027.06 70",
     "line 24  LF,TFREEL(TXB),46"),
    ("004530.00", "004551.34 C2",
     "line 25  BRZ,TPSCR"),
    ("004530.40", "000011.12 30",
     "line 26  LV,TIXZ,$R"),
    ("004531.00", "000000.00 85  060600.06 70",
     "line 28  C0011(BU,48,6),TREELN(TIXZ)"),
    ("004532.00", "004630.74 80  006630.23 10",
     "line 29  KF,TLBL,48"),
    ("004533.00", "004534.76 C2",
     "line 30  BAE,TP5A2"),
    ("004533.40", "000000.50 84  001000.00 F0",
     "line 31  CM0000,TVER(TXC)"),
    ("004534.40", "004460.37 10",
     "line 33  T P5A2  SX,$15,TPSAV"),
    ("004535.00", "004456.00 80  000000.12 F0",
     "line 34  SF(BU,64,8),TP5IN"),
    ("004536.00", "004537.37 01",
     "line 35  LVI,$15,TP5A3"),
    ("004536.40", "002366.04 00",
     "line 36  BD,SA8IQS"),
    ("004537.00", "004456.00+",
     "line 37  T P5A3  VF,TP5IN"),
    ("004537.40", "000010",
     "line 38  CF,8"),
    ("004540.00", "004457.00+",
     "line 39  VF,TP5OUT"),
    ("004540.40", "004541.00 00",
     "line 40  T IPLB2  BE,$+.32"),
    ("004541.00", "004457.00 80  000000.06 70",
     "line 41  LF(BU,64,8),TP5OUT"),
    ("004542.00", "004435.50 80  050000.12 F0",
     "line 42  SF(BU,40,8),TREELX"),
    ("004543.00", "004460.36 10",
     "line 43  LX,$15,TPSAV"),
    ("004543.40", "004431.00 80  000040.06 70",
     "line 45  C0011,TMBLK,64"),
    ("004544.40", "004436.20 80  030040.12 F0",
     "line 46  CM0101(BU,24,8),TREELX+.40,64"),
    ("004545.40", "000000.33 84  001000.00 F0",
     "line 47  CM0000,TFDISP(TXC)"),
    ("004546.40", "000000.32 84  001000.36 F0",
     "line 48  CM1111,STATI(TXC)"),
    ("004547.40", "000000.00 85  060600.06 70",
     "line 49  LF(BU,48,6),TREELN(TIXZ)"),
    ("004550.40", "004556.50 00",
     "line 50  B,TP4"),
    ("004551.00", "000000.32 84  002000.07 70",
     "line 52  T PSCR  CT0011(BU,2),STATI(TXC)"),
    ("004552.00", "004575.74 C2",
     "line 53  BRZ,TP3"),
    ("004552.40", "004444.00 80  000000.06 70",
     "line 54  C0011,TSCRAT"),
    ("004553.40", "004435.50 80  000000.12 F0",
     "line 55  CM0101,TREELX"),
    ("004554.40", "004631.02 80  006634.06 70",
     "line 56  C0011(BU,6,6),TNOP,56"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.78 ")
finish(fails)
