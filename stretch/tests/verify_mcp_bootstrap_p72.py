"""MCP INITIALIZATION, printed p.72 -- MACHINE CONFIGURATION CHANGE:
ADJUST THE NECESSARY TABLES.

Fifty-six lines, forty-nine of which compile -- the densest page of
the ASSIGN program.  decks/mcp_bootstrap_p72.strap carries the
derivations.

>>> LINE 4 IS T ASIGN'S FORWARD BRANCH, AND THE BOOT RUN HAS BEEN
STOPPING ON IT. <<<  printed p.65 line 9 is "BZXVZ,T A9" commented
"-IF A MACH CNF CHANGE", and the PC trail has ended at 004215.00
ever since p.65 landed.  Line 4 is that address and the heading
three lines above it names what it is for.

>>> A MULTIPLY, THE FIRST IN THIS CORPUS. <<<  Line 19 is
"*(BU,24),T COMBO,40" -- the operation is a bare asterisk.  It
compiles 030024.21 90 and line 26's "M+,T DISK(T IXG)" compiles
010000.20 90: the SAME opcode byte, told apart by bit 23 of the
second group.

>>> AND A FIFTH WRITTEN MINUS, TWO LINES BELOW IT. <<<  Line 20 is
"-(BU,24),T 2COMB,20" with the familiar ".30".  The pair on lines
19-20 is the sharpest instance yet, because each operand is the
other half of one constant: printed p.63 line 21 is "T COMBO
VF,T TYBC+T MACBC+T REQBC" and line 22 is "T 2COMB VF,T TYBC+T
MACBC".  Multiply by the three-field width, subtract the two-field
width -- a computation in which a wrong sign would have produced a
different table offset in silence.

TWO IMMEDIATE VALUES THAT PROVE THEIR OWN FIELD POSITION: line 36's
"KFI(BU,4),2" compiles 100000.00 and line 44's "KFI(BU,4),5"
compiles 240000.00.  A four-bit immediate left-justified in the
eighteen-bit address field is the value times 2^14, and the two
rows differ only in the value.  Their comments read "-LOOK FOR
CONSOLE" and "-LOOK FOR A PRINTER", equipment codes 2 and 5, which
is printed p.64's REQUEST VALIDITY CHECK TABLE read back.

A SIXTH dds FROM A `DD` LABEL, AND THE FIRST FROM AN ENTRY-MODE DD.
Line 26's "M+,T DISK(T IXG)" writes no dds and compiles 010000.20 90
-- length EIGHT -- from T DISK, which printed p.64 line 6 defines as
"(8)DD(BU,8),1,1,0", the first row of the REQUEST VALIDITY CHECK
TABLE.  pp.66, 67 and 69 found this shape on plain "DD(BU,1),0"
labels; an octal entry-mode DD carries its dds identically.  THE
DECK HAD IT WRONG FIRST: that was the one row of forty-nine that
failed.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  Line 19's multiply becomes an add -- 1 FAIL, reading
  030024.20 10 for 030024.21 90.  BOTH the opcode byte and bit 23
  move, which is what separates * from +.
  Line 20's minus becomes a plus -- 1 FAIL, 030012.20 for
  030012.30.  One bit, as on printed pp.69 and 70.
  T DISK loses its (BU,8) -- 1 FAIL, line 26, reading 000000 for
  010000.
  Line 44's immediate 5 becomes 4 -- 1 FAIL, reading 200000.00 for
  240000.00.  Four times 2^14 is 0o200000 and five times is
  0o240000, so the printed octal scales with the value and pins the
  field's position.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p72.strap").read())

SYMBOLS = {
    # The address printed p.65 line 9 branches to.
    "TA9":   "004215.00",
    # Labels this page defines and uses itself.
    "TCM9":  "004221.40",
    "TA9A":  "004225.00",
    "T9M":   "004236.00",
    "TA9B":  "004243.00",
    "TA9BA": "004244.00",
    "TB9":   "004246.00",
    "TB9A":  "004254.40",
    "TB9B":  "004261.40",
}

ROWS = [
    ("004215.00", "002152.24 10",
     "line 4   T A9  LX"),
    ("004215.40", "000000.00 8F  030000.00 F0",
     "line 5   CM0000(BU,24)"),
    ("004216.40", "002153.20 30",
     "line 6   LV,SBAMCP"),
    ("004217.00", "004767.00 80  000003.02 A8",
     "line 7   TI,1,T DSIO"),
    ("004220.00", "004770.00 80  000011.02 A8",
     "line 8   TI,1,T DSIO+1."),
    ("004221.00", "003647.20 10",
     "line 9   LX,T TYARA"),
    ("004221.40", "000000.10 88  010000.00 F0",
     "line 10  T CM9  CM0000"),
    ("004222.40", "003650.20 D0",
     "line 11  V+C,T COMBO"),
    ("004223.00", "004221.70 40",
     "line 12  BZXCZ,T CM9"),
    ("004223.40", "003273.00 80  022000.00 F0",
     "line 14  CM0000,T LUCT"),
    ("004224.40", "003655.04 10",
     "line 15  LX,T MUCTX"),
    ("004225.00", "000000.24 82  004000.00 F0",
     "line 16  T A9A  CM0000"),
    ("004226.00", "000000.64 8A  004024.20 50",
     "line 17  L,T EQUIP,40"),
    ("004227.00", "004261.74 C2",
     "line 18  BRZ,T B9B"),
    ("004227.40", "003650.00 80  030024.21 90",
     "line 19  *(BU,24)"),
    ("004230.40", "003650.40 80  030012.30 10",
     "line 20  -(BU,24)"),
    ("004231.40", "000011.00 80  000012.20 50",
     "line 21  L(BU,64),$R,20"),
    ("004232.40", "000011.20 30",
     "line 22  LV,T IXG,$R"),
    ("004233.00", "400000.00 80  401000.20 50",
     "line 23  LI(BU,1),1"),
    ("004234.00", "000000.64 8A  004236.34 00",
     "line 24  BZB,T EQUIP"),
    ("004235.00", "000000.73 8A  004000.20 50",
     "line 25  L,T UNITK"),
    ("004236.00", "003652.00 88  010000.20 90",
     "line 26  T 9M  M+"),
    ("004237.00", "000000.33 8A  004275.74 02",
     "line 27  BB,T MULTI"),
    ("004240.00", "000000.31 8A  004243.34 02",
     "line 28  BB,T CHAVL"),
    ("004241.00", "000000.40 8A  004244.34 02",
     "line 29  BB,T CHOWN"),
    ("004242.00", "000000.34 8A  004246.34 00",
     "line 30  BZB,T UNAVL"),
    ("004243.00", "000000.35 8A  004422.34 00",
     "line 31  T A9B  BZB"),
    ("004244.00", "004246.03 01",
     "line 32  T A9BA  LVI"),
    ("004244.40", "000000.76 8A  002000.07 70",
     "line 33  CT0011(BU,2)"),
    ("004245.40", "004320.34 C0",
     "line 34  BZRZ,T A10"),
    ("004246.00", "000000.64 8A  004000.06 70",
     "line 35  T B9  LF"),
    ("004247.00", "100000.00 80  404000.23 10",
     "line 36  KFI(BU,4),2"),
    ("004250.00", "004254.76 C0",
     "line 37  BZAE,T B9A"),
    ("004250.40", "000032.20 30",
     "line 38  LV,T IXG,T IXF"),
    ("004251.00", "000030.30 80  001000.36 F0",
     "line 39  CM1111(BU,1)"),
    ("004252.00", "002152.20 B0",
     "line 40  V+,S XCHAN"),
    ("004252.40", "000011.21 30",
     "line 41  SV,T IXG,$R"),
    ("004253.00", "002156.02 80  021027.12 F0",
     "line 42  SF(BU,17)"),
    ("004254.00", "004261.50 00",
     "line 43  B,T B9B"),
    ("004254.40", "240000.00 80  404000.23 10",
     "line 44  T B9A  KFI,5"),
    ("004255.40", "004261.76 C0",
     "line 45  BZAE,T B9B"),
    ("004256.00", "000032.20 30",
     "line 46  LV,T IXG,T IXF"),
    ("004256.40", "000030.30 80  001000.36 F0",
     "line 47  CM1111(BU,1)"),
    ("004257.40", "002152.20 B0",
     "line 48  V+,S XCHAN"),
    ("004260.00", "000011.21 30",
     "line 49  SV,T IXG,$R"),
    ("004260.40", "002156.42 80  021027.12 F0",
     "line 50  SF(BU,17)"),
    ("004261.40", "004225.25 48",
     "line 51  T B9B  CB+"),
    ("004262.00", "000000.45 0D",
     "line 55  V-I,T IXH,0.32"),
    ("004262.40", "003660.05 10",
     "line 56  SX,T RCHSC"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.72 ")
finish(fails)
