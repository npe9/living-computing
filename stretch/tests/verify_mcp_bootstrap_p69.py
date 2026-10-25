"""MCP INITIALIZATION, printed p.69 -- THE UNIT TABLE SCAN AND THE
RESERVED-UNIT SEARCH.

Fifty-six lines, forty-five of which compile.
decks/mcp_bootstrap_p69.strap carries the derivations.

IT PLACES printed p.68's LAST TWO FORWARD REFERENCES: line 2 is
T A3CB at 004064.40 and line 5 is T C3Z at 004065.00.

>>> A BARE WRITTEN MINUS, AND IT IS ONLY THE SECOND IN THE CORPUS.
<<<  Line 48 is "-,T ABSUN(T IXM),46" -- the OPERATION is a single
minus sign.  The only other is MCP printed p.18 line 35, which is
the row that found fieldToSM returning sign 0 for every unsigned
field and dropping the negative sign modifier: every unsigned
subtract in the model was an addition.

AND THE LISTING SHOWS THE MODIFIER.  Line 47 is
"L,T UNITK(T X1),46" compiling 004027.20 50; line 48 is the minus
compiling 003027.30 10.  The second group's ".20" becomes ".30" --
one bit, which is Reference Manual printed p.57's "Unsigned, use -"
and p.60's "whether the sign of the storage operand is taken as-is
or is inverted".

TEN BARE VFL STATEMENTS, AND THREE TAKE THEIR dds FROM `DD` LABELS
(T ONE, T INDC, T INDZ -- printed p.61 lines 21, 25 and 28).
printed pp.66 and 67 each found one such symbol; this page has
three, so the shape is now confirmed on five symbols across three
pages.

ALL FORTY-FIVE ROWS AND ALL TWELVE SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  Line 48's bare minus becomes a plus -- 1 FAIL, reading
  003027.20 for 003027.30.  EXACTLY ONE BIT, the negative-sign
  modifier, and it is the only thing that distinguishes the two
  operations in the compiled word.  That is the fix of 2026-10-19
  checked from a second row, four months of listing later.
  T ONE loses its (BU,1) -- 1 FAIL, line 23, reading 000000 for
  001000.  T ONE is a DD label (printed p.61 line 21), not a SYN.
  STATI 0.26 -> 0.25 -- 1 FAIL, line 24.  The one symbol new on this
  page, read off that row alone.
  T IXM $8 -> $7 -- 6 FAIL, in the J field (lines 40, 41) and in the
  opcode byte's low nibble (lines 43, 48, 51, 52) alike.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p69.strap").read())

SYMBOLS = {
    # printed p.68's last two stand-ins, placed here.
    "TA3CB": "004064.40",
    "TC3Z":  "004065.00",
    # Labels this page defines and uses itself.
    "TC3":   "004065.40",
    "TC3A":  "004066.00",
    "TA4A":  "004075.40",
    "TA4BA": "004103.00",
    "TA4CM": "004104.40",
    "TA4B":  "004106.00",
    "TA4C":  "004107.40",
    "TA4CA": "004110.00",
    "TA4CB": "004115.00",
    "TA4CC": "004126.00",
}

ROWS = [
    ("004064.40", "004060.65 48",
     "line 2   T A3CB  CB+"),
    ("004065.00", "003270.15 10",
     "line 5   T C3Z  SX"),
    ("004065.40", "003270.14 10",
     "line 6   T C3  LX"),
    ("004066.00", "000000.34 86  004127.34 02",
     "line 7   T C3A  BB"),
    ("004067.00", "003273.31 80  001000.00 F0",
     "line 8   CM0000,T INDZ"),
    ("004070.00", "000000.35 86  004127.34 00",
     "line 12  BZB,T UNASG"),
    ("004071.00", "000000.76 86  002000.07 70",
     "line 13  CT0011(BU,2)"),
    ("004072.00", "004075.74 C2",
     "line 14  BRZ,T A4A"),
    ("004072.40", "003273.23 80  004127.34 00",
     "line 15  BZB,T MODE"),
    ("004073.40", "000000.76 86  004127.34 02",
     "line 16  BB,T UNRES"),
    ("004074.40", "000000.01 84  004107.74 02",
     "line 17  BB,T UNOBT"),
    ("004075.40", "003273.31 80  001000.00 F0",
     "line 18  T A4A  CM0000"),
    ("004076.40", "003273.27 80  004137.34 02",
     "line 19  BB,T INDD"),
    ("004077.40", "000000.34 84  022000.06 70",
     "line 20  LF,T FREEL"),
    ("004100.40", "004106.34 C2",
     "line 21  BRZ,T A4B"),
    ("004101.00", "000000.33 86  004137.34 02",
     "line 22  BB,T FDISP"),
    ("004102.00", "003273.22 80  001000.06 70",
     "line 23  LF,T ONE"),
    ("004103.00", "000000.32 86  001000.23 10",
     "line 24  T A4BA  KF"),
    ("004104.00", "004137.36 C2",
     "line 25  BAE,T A5A"),
    ("004104.40", "003273.26 80  001000.36 F0",
     "line 26  T A4CM  CM1111"),
    ("004105.40", "004127.10 00",
     "line 27  B,T B3"),
    ("004106.00", "000000.33 86  004104.74 02",
     "line 28  T A4B  BB"),
    ("004107.00", "004103.10 00",
     "line 29  B,T A4BA"),
    ("004107.40", "000023.24 10",
     "line 34  T A4C  LX"),
    ("004110.00", "000002.25 07",
     "line 35  T A4CA  V+ICR"),
    ("004110.40", "000000.47 8A  004127.34 02",
     "line 36  BB,T LPPEN"),
    ("004111.40", "000000.44 8A  004110.34 02",
     "line 37  BB,T JBPRO"),
    ("004112.40", "000000.34 8A  010027.20 50",
     "line 38  L,T UNCT,46"),
    ("004113.40", "004110.34 C2",
     "line 39  BRZ,T A4CA"),
    ("004114.00", "000011.20 50",
     "line 40  LC,T IXM,$R"),
    ("004114.40", "000000.20 3A",
     "line 41  LV,T IXM"),
    ("004115.00", "000000.56 88  022027.20 50",
     "line 43  T A4CB  L"),
    ("004116.00", "000011.04 90",
     "line 44  KV,T X3,$R"),
    ("004116.40", "004126.32 C0",
     "line 45  BZXE,T A4CC"),
    ("004117.00", "000011.24 30",
     "line 46  LV,T X1,$R"),
    ("004117.40", "000000.73 8A  004027.20 50",
     "line 47  L,T UNITK,46"),
    ("004120.40", "000000.07 88  003027.30 10",
     "line 48  -,T ABSUN,46"),
    ("004121.40", "000011.15 90",
     "line 49  KC,T IXJ,$R"),
    ("004122.00", "004126.32 C0",
     "line 50  BZXE,T A4CC"),
    ("004122.40", "000000.00 88  001000.00 F0",
     "line 51  CM0000,T ASGNI"),
    ("004123.40", "000000.02 88  001000.00 F0",
     "line 52  CM0000,T PRINT"),
    ("004124.40", "000000.46 8A  001000.00 F0",
     "line 53  CM0000,T ASGNP"),
    ("004125.40", "004142.50 00",
     "line 54  B,T A5MA"),
    ("004126.00", "004115.21 48",
     "line 55  T A4CC  CB+"),
    ("004126.40", "004110.10 00",
     "line 56  B,T A4CA"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.69 ")
finish(fails)
