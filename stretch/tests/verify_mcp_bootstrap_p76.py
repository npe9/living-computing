"""MCP INITIALIZATION, printed p.76 -- A PRINT SUB-ROUTINE THAT WILL
PRINT ASSIGNMENTS.

Thirty-seven lines, of which thirty compile and SEVEN print any
machine code at all.  It is a data page: the message buffers the
assignment printer fills in, three hexadecimal constants, five SYN
cards, four one-bit flags and three index words.
decks/mcp_bootstrap_p76.strap carries the derivations.

>>> FOUR OF ITS LABELS WERE ALREADY STAND-INS, AND ALL FOUR AGREE.
<<<  T BUFB1 (004432.00), T MESSY (004451.00, printed p.74 line 55's
LVI), T SBHDI (004455.01) and YSCRBT (004455.03, printed p.75 line
37's BBZ -- and the stand-in gives the BIT).

>>> THE COUNTING IS THE CHECK, AND IT CHECKS SEVENTEEN TIMES. <<<
The listing prints no binary for character data, so no character
code is checked or can be.  What is checked is the counting, and on
a page that is almost all character data the counting is the whole
page: seventeen labels, each landing on its printed location, and
ONE wrong character anywhere shifts every label after it.  All
seventeen landed on the first assembly.

AND THE ADVANCE IS THE DATUM'S CHARACTER COUNT, NOT THE DECLARED
ITEM LENGTH.  Line 16 is "(IQS*)DD(BU,36,8), UNIT *" -- six
characters -- and advances FORTY-EIGHT bits.  Line 14 declares 64
and advances 96 for twelve characters; line 15 declares 24 and
advances 24 for three.

THE ONE THING THE PAGE CANNOT CHECK is where a datum's blanks sit.
A total of forty with a thirty-four character core leaves six
blanks, and the locations cannot say how they split.  Those were
MEASURED at 1800 dpi against the character pitch and are recorded as
measurement, not as proof.

>>> A HEX LITERAL IS THE ONE FIELD WHERE THE C/ZERO RULE HAS NO
INTERNAL ANSWER -- AND THE COMPILED OCTAL IS THE AUTHORITY. <<<
listing_typography.md 13e turns on octal having no C.  Hexadecimal
does, so the field cannot rule it out, and this page has three such
literals.  Line 11 prints "(16)C C 0 F 9 D B 6 8 B C D 9 1 9 1" with
THREE open-C shapes and ONE closed zero among its four zeros; its
compiled datum 0000174733321303310621 is 000F9DB68B0D9191, so all
four are zeros.  Nothing in the statement could have said so.

Line 19 is sharper: "(16)8993151193000000" prints its six trailing
zeros as C 0 C 0 C 0, ALTERNATING, and its compiled datum proves all
six are zeros.  printed p.74 line 10's "CM0000" prints C M O C O C
-- the same alternation in the opposite phase.  THE SHAPE ALTERNATES
WITH THE COLUMN, NOT WITH THE DIGIT.

Line 18 was misread a third way: its sixth hex digit was read 0 and
is D.  The compiled octal said so before the 1800 dpi render
confirmed it.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  Line 11's hex literal takes its C glyphs literally -- 1 FAIL at
  004432.00, reading 1400174733321363310621 for
  0000174733321303310621.  A LEADING C PUTS 1100 IN THE TOP FOUR
  BITS and the printed octal opens "14" instead of "00", which is
  exactly how the compiled value settles a literal the field cannot.
  Line 19's six trailing zeros taken as the C,0,C,0,C,0 they print
  -- 1 FAIL at 004443.00, reading 1046230521062360140300.
  Line 18's sixth hex digit read 0, as it was at 600 dpi -- 1 FAIL
  at 004442.00, reading 0000270410142500105617.
  Line 9's message loses ONE of its four trailing blanks -- 11
  FAILS.  Every label from T MBLK on is EIGHT BITS early, which is
  the counting check doing the only job it can do on a page whose
  character code is never printed.
  T MESSY's text loses its final period -- 7 FAILS, every label from
  T HEAD on.
  Line 16's declared item length 36 becomes 48 -- SURVIVES, and the
  survival is the point: the counter is driven by the DATUM's
  character count and not by the declared item length, so 36 and 48
  produce the same forty-eight bits for six characters.  Recorded
  because an injection that survives says something true about the
  test.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p76.strap").read())

SYMBOLS = {
    "TBUF01": "004424.00",
    "TMBLK":  "004431.00",
    "TBUFB1": "004432.00",
    "TREELX": "004435.50",
    "TCHANX": "004440.10",
    "TUNITX": "004441.20",
    "TSCRAT": "004444.00",
    "TSUBHD": "004445.00",
    "TPID":   "004450.00",
    "TMESSY": "004451.00",
    "THEAD":  "004455.00",
    "TSBHDI": "004455.01",
    "TNGATE": "004455.02",
    "YSCRBT": "004455.03",
    "TP5IN":  "004456.00",
    "TP5OUT": "004457.00",
    "TPSAV":  "004460.00",
}

ROWS = [
    ("004423.40", "000000.30 00",
     "line 8   CNOP"),
    ("004432.00", "0000174733321303310621",
     "line 11  T BUFB1  DD(BU),(16)000F9DB68B0D9191"),
    ("004442.00", "0000270730142500105617",
     "line 18  DD(BU),(16)00171D8315008B8F"),
    ("004443.00", "1046230521062300000000",
     "line 19  DD(BU),(16)8993151193000000"),
    ("004456.00", "000000.00+ 000 000000 000000",
     "line 35  T P5IN  XW"),
    ("004457.00", "000000.00+ 000 000000 000000",
     "line 36  T P5OUT  XW"),
    ("004460.00", "000000.00+ 000 000000 000000",
     "line 37  T PSAV  XW"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.76 ")
finish(fails)
