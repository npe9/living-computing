"""MCP INITIALIZATION, printed p.66 -- THE REQUEST-COUNT CHECK AND
THE I/O REQUEST SCAN.

Fifty-six lines, forty-four of which compile.
decks/mcp_bootstrap_p66.strap carries the derivations.

IT PICKS UP EXACTLY WHERE printed p.65 LEFT OFF: p.65's last line
branches to T C1 and its line 37 to T A2; line 3 here is T C1 at
003733.40 and line 19 is T A2 at 003743.40.  Both were stand-ins in
that deck.

LINE 1 IS A HALT, the fourth transcribed: "BD,$" at 003733.00,
commented "-ILLEGAL REQUEST - MCP ERROR".  The other three (printed
p.6 line 1, p.54 line 55, p.55 line 12) are all table overflows;
this one is not.

>>> NINE BARE VFL STATEMENTS, AND THREE TAKE THEIR dds FROM A `DD`
LABEL RATHER THAN A SYN. <<<  Lines 22, 39 and 44 are
"CM0000,T INDD", "CM0000,T MODE" and "CM1111,T MODE", all bare, all
compiling 001000 -- length ONE.  T MODE and T INDD are NOT SYNs:
printed p.61 lines 22 and 26 define them with "DD(BU,1),0".  So a
label defined by a DD carries its dds the same way, and C22-6531
printed p.31's sentence is about the SYMBOL, not about the card that
made it.

FORTY-THREE OF FORTY-FOUR ROWS WERE BIT-EXACT ON THE FIRST RUN.  The
one that was not is line 5's opcode byte, transcribed 40 and actually
4C -- A C MISREAD AS A ZERO, which is the MIRROR of
listing_typography.md 13 and the first time that pair has gone this
way.  At 1800 dpi the glyph is an open curve against the closed ovals
of the same row's three zeros, and the corpus settles it without the
assembler: "CBR" prints 4C in two already-transcribed rows
(002252.00 and 002272.40) where plain "CB+" prints 48.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T MODE loses its (BU,1) -- 2 FAIL, lines 39 and 44, each reading
  000000 for 001000.  T MODE is a DD label, not a SYN, so this is
  the dds rule checked on a symbol printed p.61 made with
  "DD(BU,1),0".
  T SETAC (8)3726.0 -> (8)3727.0 -- 1 FAIL, line 5.  That label is
  printed p.65 line 49's.
  Line 35's "T LAST+1.0" loses its word -- 1 FAIL, reading
  000000.22 for 000001.22.  The word part and the bit part move
  independently and the printed pair shows both.
  Line 36's "T IOREQ-1" loses its bit -- 1 FAIL, reading 003373.11
  for 003372.51.  BOTH the word AND the half-word bit change,
  because LVI's address field is nineteen bits and one bit back from
  003373.0 lands at 003372.63, which that field holds as 003372 with
  the half-word bit set.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p66.strap").read())

SYMBOLS = {
    # printed p.65's two stand-ins, placed here.
    "TC1":    "003733.40",
    "TA2":    "003743.40",
    # Labels this page defines and uses itself.
    "TCHEK":  "003735.40",
    "TCONT":  "003741.40",
    "TA2A":   "003745.00",
    "TA2B":   "003750.00",
    "TB2":    "003756.40",
    "TB2Z":   "003760.00",
    "TA2D":   "003761.00",
    "TA2DB":  "003764.40",
    "TA2DC":  "003765.40",
    "TC2B":   "003770.40",
    "TC2BA":  "003772.40",
    "TC2BC":  "003773.40",
}

ROWS = [
    ("003733.00", "003733.04 00",
     "line 1   BD,$"),
    ("003733.40", "000000.20 8A  010000.22 B0",
     "line 3   T C1  M+1"),
    ("003734.40", "000032.02 00",
     "line 4   R,T X1"),
    ("003735.00", "003726.11 4C",
     "line 5   CBR+"),
    ("003735.40", "000000.20 8A  010000.06 70",
     "line 9   T CHEK  LF"),
    ("003736.40", "003741.74 C2",
     "line 10  BRZ,T CONT"),
    ("003737.00", "000000.10 8A  010000.23 10",
     "line 11  KF,T MCAD"),
    ("003740.00", "003741.77 40",
     "line 12  BZAH,T CONT"),
    ("003740.40", "000000.45 83  001000.36 F0",
     "line 13  CM1111"),
    ("003741.40", "003650.24 D0",
     "line 14  T CONT  V+C"),
    ("003742.00", "003735.70 40",
     "line 15  BZXCZ,T CHEK"),
    ("003742.40", "000000.45 83  004360.34 02",
     "line 16  BB,T AREJX"),
    ("003743.40", "003265.22 00",
     "line 19  T A2  Z,T CTEMP"),
    ("003744.00", "003273.24 80  004000.00 F0",
     "line 20  CM0000(BU,4)"),
    ("003745.00", "000000.12 10",
     "line 21  T A2A  LX,$Z"),
    ("003745.40", "003273.27 80  001000.00 F0",
     "line 22  CM0000,T INDD"),
    ("003746.40", "003273.31 80  003750.34 00",
     "line 23  BZB,T INDZ"),
    ("003747.40", "004417.50 00",
     "line 24  B,T C"),
    ("003750.00", "000000.00 84  003761.34 00",
     "line 28  T A2B  BZB"),
    ("003751.00", "000000.03 84  003756.74 00",
     "line 29  BZB,T TYPE"),
    ("003752.00", "000000.13 84  007020.20 50",
     "line 30  L,T RLSYM,32"),
    ("003753.00", "003756.74 C2",
     "line 31  BRZ,T B2"),
    ("003753.40", "000000.56 84  022027.06 70",
     "line 32  C0011,T ABSCH"),
    ("003754.40", "000000.07 84  003000.06 70",
     "line 33  C0011,T ABSUN"),
    ("003755.40", "003265.00 80  000000.20 D0",
     "line 34  ST(BU,64)"),
    ("003756.40", "000001.22 84  003760.34 00",
     "line 35  T B2  BZB"),
    ("003757.40", "003372.51 01",
     "line 36  LVI,T IOREQ-1"),
    ("003760.00", "003745.11 48",
     "line 37  T B2Z  CB+"),
    ("003760.40", "004176.10 00",
     "line 38  B,T A8"),
    ("003761.00", "003273.23 80  001000.00 F0",
     "line 39  T A2D  CM0000"),
    ("003762.00", "003656.22 10",
     "line 40  LX,T X2,T YSCAN"),
    ("003762.40", "000000.24 1F",
     "line 41  LX,T CTWDX"),
    ("003763.00", "003764.63 42",
     "line 42  BXF,T A2DB"),
    ("003763.40", "000000.01 84  003765.74 00",
     "line 43  BZB,T UNOBT"),
    ("003764.40", "003273.23 80  001000.36 F0",
     "line 44  T A2DB  CM1111"),
    ("003765.40", "000000.03 84  003775.34 02",
     "line 45  T A2DC  BB"),
    ("003766.40", "004020.63 42",
     "line 49  BXF,T A7"),
    ("003767.00", "003315.24 10",
     "line 50  LX,T X1,T PPRUN"),
    ("003767.40", "000000.47 8A  004423.34 02",
     "line 51  BB,T LPPEN,T P"),
    ("003770.40", "000000.45 8A  003772.74 02",
     "line 52  T C2B  BB"),
    ("003771.40", "000000.44 8A  003773.74 00",
     "line 53  BZB,T JBPRO"),
    ("003772.40", "000002.25 07",
     "line 54  T C2BA  V+ICR"),
    ("003773.00", "003770.50 00",
     "line 55  B,T C2B"),
    ("003773.40", "000032.06 90",
     "line 56  T C2BC  KV"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.66 ")
finish(fails)
