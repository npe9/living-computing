"""MCP INITIALIZATION, printed p.74 -- MACHINE CONFIGURATION CHANGE,
THE RESERVED BIT IS ON AND THE CHAN AND/OR UNIT IS DOWN.

Fifty-six lines, forty-five of which compile, under ONE boxed
heading.  Lines 22-24 and line 40 are blank comment cards inside rule
boxes with NO TEXT -- the first page in this corpus to box nothing.
decks/mcp_bootstrap_p74.strap carries the derivations.

>>> THIS PAGE IS WHERE pp.72 AND 73 BOTH BRANCH. <<<  p.72 line 34's
"BZRZ,T A10" is 004320.34 C0 and lands on line 6; p.73 line 35's
"BZRZ,T C10" is 004322.74 C0 and lands on line 10.  It defines the
generation after p.72-73's T A9/T B9/T C9: T A10, T C10, T A10A,
T B10A, T B10, T B10B, T A11, T A11A, T A11B, T B11C and T AREJX.

>>> AND IT RENAMED TWO SYMBOLS IN TWO FINISHED DECKS. <<<  Those two
branches were transcribed "T A1C" and "T C1C", and at 1800 dpi both
final glyphs ARE open curves.  Line 10 settles it in ONE TOKEN: the
statement is "CM0000", its code 001000.00 F0 puts zero in the
connective field, and at 1800 dpi it prints C M O C O C -- the same
digit four times, twice closed and twice open, in one word of one
impression.  listing_typography.md 13g carries it.

EVERY SYMBOL THIS PAGE USES WAS ALREADY PLACED, and every value was
derived from THIS page's code before it was looked up: the index
fields gave T IXD = $7, T IXE = $3 and T IXI = $5, the second groups
gave the field lengths 8 (T UNCT), 3 (T ABSUN) and 18 (T ABSCH), and
the ".bb" pairs gave the offsets.  All eighteen agreed with printed
pp.61-64.  Only T MESSY (004451.0) is forward, and its NAME is
confirmed at 1200 dpi because nothing else can confirm it.

A SIXTH WRITTEN MINUS: line 32's "-,T ABSUN(T IXI),46" compiles
003027.30 10, the ".30" sign modifier, after printed p.18 line 35 and
printed pp.69, 70 and 72.

A THIRD DELIBERATE HALT: line 39 is "BD,$" at 004345.00, branch
disabled to its own address, commented "-MCP OR MACHINE ERROR", after
printed p.6 line 1 and printed p.52 line 55.

THREE BYTES THE ASSEMBLER DISPUTED, AND THE INK AGREED WITH THE
ASSEMBLER THREE TIMES OUT OF THREE.  Line 36 read C7 and is 07 (the
row's own octal field prints 00CC02, a 13d row); line 38 read 00 and
is 0C (a CLOSED oval and an OPEN curve side by side INSIDE ONE BYTE
-- they cannot both be zeros); line 47 read C2 and is 02.  Each was
settled by re-rendering THAT BYTE at 1800 dpi before it was adopted.
That the ink agreed three times running is a calibration fact about
THE CORPUS, not a licence to skip the render.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  Line 38's BZB1 becomes a plain BZB -- 1 FAIL at 004344.00, reading
  004326.34 00 for 004326.34 0C.  THAT IS THE BYTE I FIRST READ AS
  00, and the injection writes exactly the wrong row.
  Line 36's V+ICR loses its refill -- 1 FAIL at 004343.00, reading
  000002.17 06 for 07.  One bit, and it is the R.
  Line 32's written minus becomes a plus -- 1 FAIL at 004340.40,
  reading 003027.20 for 003027.30, as on printed pp.69, 70 and 72.
  T UNCT's stand-in dds drops from eight bits to four -- 1 FAIL at
  004330.00, reading 004027 for 010027.  Eight times 512 is 0o10000
  and four times is 0o4000, so the printed field scales with the
  length and pins the derivation that produced it.
  T LOOP's bit offset is read as DECIMAL instead of octal -- 3 FAILS,
  at 004325.00, 004344.00 and 004353.40, every row that names it,
  each reading 003273.26 for 003273.32.  The stand-in is written
  "(8)3273.32" and the octal entry mode governs the BIT field too;
  0o32 is 26 decimal, which is exactly the number the mistake
  produces.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p74.strap").read())

SYMBOLS = {
    # The two addresses printed pp.72 and 73 branch to.
    "TA10":   "004320.00",
    "TC10":   "004322.40",
    # Labels this page defines.
    "TA10A":  "004324.40",
    "TB10A":  "004326.00",
    "TA11":   "004333.00",
    "TA11B":  "004334.40",
    "TB10B":  "004342.40",
    "TB10":   "004343.00",
    "TA11A":  "004345.40",
    "TB11C":  "004356.00",
    "TAREJX": "004360.00",
}

ROWS = [
    ("004320.00", "000000.76 8A  001000.00 F0",
     "line 6   T A10  CM0000"),
    ("004321.00", "000000.77 8A  001000.00 F0",
     "line 7   CM0000,T OVRES"),
    ("004322.00", "004324.50 00",
     "line 8   B,T A10A"),
    ("004322.40", "000000.76 88  001000.00 F0",
     "line 10  T C10  CM0000"),
    ("004323.40", "000000.77 88  001000.00 F0",
     "line 11  CM0000,T OVRES"),
    ("004324.40", "003315.16 10",
     "line 13  T A10A  LX"),
    ("004325.00", "003273.32 80  001000.00 F0",
     "line 14  CM0000,T LOOP"),
    ("004326.00", "000000.47 87  000000.34 03",
     "line 15  T B10A  BB"),
    ("004327.00", "000000.44 87  004343.34 02",
     "line 16  BB,T JBPRO"),
    ("004330.00", "000000.34 87  010027.20 50",
     "line 17  L,T UNCT,46"),
    ("004331.00", "004343.34 C2",
     "line 18  BRZ,T B10"),
    ("004331.40", "000000.12 57",
     "line 19  LC,T CRREF"),
    ("004332.00", "000025.13 50",
     "line 20  SC,T IXI,T IXI"),
    ("004332.40", "000011.12 50",
     "line 21  LC,T IXI,$R"),
    ("004333.00", "000000.22 85  004334.74 00",
     "line 25  T A11  BZB"),
    ("004334.00", "003373.13 01",
     "line 26  LVI,T IOREQ"),
    ("004334.40", "000000.56 85  022027.20 50",
     "line 27  T A11B  L"),
    ("004335.40", "000011.24 90",
     "line 28  KV,T IXF,$R"),
    ("004336.00", "004342.72 C0",
     "line 29  BZXE,T B10B"),
    ("004336.40", "000000.03 85  004345.74 00",
     "line 30  BZB,T TYPE"),
    ("004337.40", "000000.73 8A  004027.20 50",
     "line 31  L,T UNITK,46"),
    ("004340.40", "000000.07 85  003027.30 10",
     "line 32  -,T ABSUN,46"),
    ("004341.40", "000011.21 90",
     "line 33  KC,T IXG,$R"),
    ("004342.00", "004345.72 C2",
     "line 34  BXE,T A11A"),
    ("004342.40", "004333.13 48",
     "line 35  T B10B  CB+"),
    ("004343.00", "000002.17 07",
     "line 36  T B10  V+ICR"),
    ("004343.40", "004326.30 40",
     "line 37  BZXCZ,T B10A"),
    ("004344.00", "003273.32 80  004326.34 0C",
     "line 38  BZB1,T LOOP"),
    ("004345.00", "004345.04 00",
     "line 39  BD,$"),
    ("004345.40", "000000.46 87  001000.00 F0",
     "line 41  T A11A  CM0000"),
    ("004346.40", "000000.00 85  001000.00 F0",
     "line 42  CM0000,T ASGNI"),
    ("004347.40", "000000.56 85  022000.00 F0",
     "line 43  CM0000,T ABSCH"),
    ("004350.40", "000000.07 85  003000.00 F0",
     "line 44  CM0000,T ABSUN"),
    ("004351.40", "000000.02 85  001000.00 F0",
     "line 45  CM0000,T PRINT"),
    ("004352.40", "000000.01 85  001000.36 F0",
     "line 46  CM1111,T UNOBT"),
    ("004353.40", "003273.32 80  004342.74 02",
     "line 47  BB,T LOOP"),
    ("004354.40", "003651.16 90",
     "line 48  KV,T VALVF"),
    ("004355.00", "004356.32 40",
     "line 49  BZXL,T B11C"),
    ("004355.40", "003651.17 30",
     "line 50  SV,T VALVF"),
    ("004356.00", "003272.16 30",
     "line 51  T B11C  LV"),
    ("004356.40", "004342.72 40",
     "line 52  BZXL,T B10B"),
    ("004357.00", "003272.17 10",
     "line 53  SX,T SAV"),
    ("004357.40", "004342.50 00",
     "line 54  B,T B10B"),
    ("004360.00", "004451.25 01",
     "line 55  T AREJX  LVI"),
    ("004360.40", "000000.25 33",
     "line 56  SV,T X1,0.0(T IXE)"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.74 ")
finish(fails)
