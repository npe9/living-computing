#!/usr/bin/env python3
"""verify_mcp_bootstrap_p39.py -- SERVICE ROUTINES TO EXTRACT
INFORMATION FROM SYSTEM CARDS, printed page 39
(../decks/mcp_bootstrap_p39.strap).
docs/MCP_Mar63_001-249.pdf PDF p.46, header "PAGE NUMBER 39".
AGENTS.md rule 3.

Fifty-three printed rows with binary output -- every row on the page
that compiles anything -- and twenty-five symbol locations.

>>> THREE OF PRINTED p.38's FOURTEEN PREDICTIONS LAND HERE, ON THE
VERY NEXT PAGE. <<<

  Y JCBC   002213.00   p.38 line 30's "BXEZ,Y JCBC"   -- line 4
  Y TCPGO  002214.40   p.38 line 31's "BXLZ,Y TCPGO"  -- line 7
  Y LIMC   002246.00   p.38 line 33's "BXEZ,Y LIMC"   -- line 44

AND Y TCPGO WAS THE SHARPEST.  p.38 line 31 prints "002214.72 46",
whose ".72" has BIT 18 SET -- the half-word selector -- so the
address is 002214.40 and not 002214.00.  Line 7 here is 002214.40.
A reading that ignored bit 18 would have been half a word wrong and
would have failed here, on a page transcribed afterwards.

AND IT CONFIRMS SIX MORE, from three earlier pages, by USING them:

  S ROOF   002162.00   printed p.37 line 37   -- line 20 reads it
  Y USB8C  002200.00   printed p.38 line 21   -- line 30 reads it
  Y NLST   001775.40   printed p.36 line 31   -- line 34 compares
  Y NOPUN  001775.40   printed p.36 line 31   -- line 40 compares
  Y UER    002311.00   p.38's prediction      -- lines 6, 17, 18
  Y UCBF2  002337.00   p.38's prediction      -- lines 9, 33, 39,
                                                 51, 53

>>> AND "SF" WAS FOUND HERE.  See the deck's header: line 52's
"SF(BU,18,3),$12" prints a trailing F0 (CM, Connect to Memory) with
connective function 0101, so SF is CM0101 -- the mirror of LF's
C0011, because a connective's four bits are a truth table over
(accumulator, memory) and 0011/0101 are the two operand-selecting
functions.  Lines 51 and 52 are adjacent rows doing exactly that. <<<

THREE ROWS NEEDED A SECOND LOOK AND THE DECK WAS RIGHT ABOUT ALL
THREE.  Recorded because all three are reading faults this project
already has names for:

  line 25  Its LOCATION is 002231.40, which a 200 dpi read made
           002231.00.  The tell was arithmetic, not typography: line
           24 is a FULL-WORD VFL instruction, so line 25 cannot be
           half a word after it.  (A full word at an ODD half word
           is normal here and p.38 line 6 does it too.)

  line 43  The code column prints "002313.5C  C0" and BOTH of those
           glyphs are digit zeros: 002313.50 00.  THE OCTAL FIELD
           PROVES IT -- ".5C" cannot be octal -- and the same row
           settles the hex byte, because the two glyphs are the same
           shape.  listing_typography.md 13, and 13a's
           self-disagreeing field one level up: "001000.00 F0" on
           the row ABOVE prints its zeros round.

  line 55  The binary is "005465.70 90", not ".70 50".  A 200 dpi
           read made the 9 a 5, which decoded to LC instead of KV --
           and the STATEMENT column says KV in crisp 900 dpi
           glyphs.  600 dpi for octal and 900 for hex is the rule
           and 200 dpi is not evidence; the two columns never
           actually disagreed.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p39.strap").read())

SYMBOLS = {
    # The six this page DEFINES.
    "YJCBC":  "002213.00",
    "YTCPGO": "002214.40",
    "YTOPCM": "002232.40",
    "YTOPCG": "002233.40",
    "YLIMC":  "002246.00",
    "YLL2":   "002247.40",
    # The nineteen it uses.  Six are confirmations of earlier pages
    # (S ROOF, Y USB8C, Y NLST, Y NOPUN, Y UER, Y UCBF2); the rest
    # are this page's own predictions, each read off its binary.
    "YNORR":  "002313.40",
    "YUER":   "002311.00",
    "YUCBF2": "002337.00",
    "YGOMK":  "002354.00",
    "YCOMMK": "002362.00",
    "YCNGMK": "002363.00",
    "YUPDAT": "002365.00",
    # TWO BIT ADDRESSES INSIDE ONE WORD, and they are different
    # symbols: printed p.37 line 11 puts S COM RG at 002151.00 and
    # calls it "THE SYSTEM WORD FLAG", while line 18 here reads a bit
    # at 002151.10 (bit 8) and line 19 clears one at 002151.03
    # (bit 3).  Read off the binary rather than assumed from the
    # similar spelling.
    "SYSMCD": "002151.10",
    "SCORG":  "002151.03",
    "SROOF":  "002162.00",
    "YLOL2":  "005464.40",
    "YLOL1":  "005465.00",
    "YBCRD":  "005464.00",
    "YUSB8C": "002200.00",
    "YNLST":  "001775.40",
    "YNOPUN": "001775.40",
    "YUCX12": "002322.00",
    "STERMI": "005465.40",
    "YUCLLC": "002262.00",
}

ROWS = [
    ("002213.00", "000001.32 9E", "line 4   Y JCBC  KV,$13,1.0($14)"),
    ("002213.40", "002313.72 C6", "line 5   BXEZ,Y NORR"),
    ("002214.00", "002311.10 00", "line 6   B,Y UER"),
    ("002214.40", "000034.22 00",
     "line 7   Y TCPGO  Z,$12  -GO - SET COUNT FIELD TO PROPER"),
    ("002215.00", "000004.31 02",
     "line 8   LCI,$12,(2)00100  -VALUE + GO TO NORMAL RETURN"),
    ("002215.40", "002340.00 80  060000.20 50", "line 9   L(BU,48),Y UCBF2+1.0"),
    ("002216.40", "002354.00 80  060000.21 10", "line 10  K(BU,48),Y GOMK"),
    ("002217.40", "002313.76 C2", "line 11  BAE,Y NORR"),
    ("002220.00", "002362.00 80  060000.21 10", "line 12  K(BU,48),Y COMMK"),
    ("002221.00", "002232.76 C2", "line 13  BAE,Y TOPCM"),
    ("002221.40", "002363.00 80  060000.21 10", "line 14  K(BU,48),Y CNGMK"),
    ("002222.40", "002233.76 C2", "line 15  BAE,Y TOPCG"),
    ("002223.00", "002365.00 80  060000.21 10", "line 16  K(BU,48),Y UPDAT"),
    ("002224.00", "002311.36 C0", "line 17  BZAE,Y UER"),
    # A BRANCH ON A BIT AT 002151.10, which is inside the word
    # printed p.37 calls S COM RG.
    ("002224.40", "002151.10 80  002311.34 00", "line 18  BZB,S YSMCD,Y UER"),
    ("002225.40", "002151.03 80  001000.00 F0", "line 19  CM0000(BU,1),S CORG"),
    # READS S ROOF, which printed p.37 line 37 defines at 002162.00
    # and printed p.15 line 23 writes the machine's size into.
    ("002226.40", "002162.32 30", "line 20  LV,$13,S ROOF"),
    ("002227.00", "005464.73 30", "line 21  SV,$13,Y LOL2"),
    ("002227.40", "000035.22 00", "line 22  Z,$13"),
    ("002230.00", "005465.33 30", "line 23  SV,$13,Y LOL1"),
    # Y LOL1 + .25 prints 005465.31, and 0o31 is 25 -- so this row
    # confirms line 23's reading of Y LOL1 independently.
    ("002230.40", "005465.31 80  001000.36 F0", "line 24  CM1111(BU,1),Y LOL1+.25"),
    ("002231.40", "005464.10 00", "line 25  B,Y BCRD"),
    ("002232.00", "002311.10 00", "line 26  B,Y UER"),
    ("002232.40", "000023.31 02", "line 27  Y TOPCM  LCI,$12,(2)10011"),
    ("002233.00", "002234.10 00", "line 28  B,Y TOPCG+.32"),
    ("002233.40", "000013.31 02", "line 29  Y TOPCG  LCI,$12,(2)01011"),
    ("002234.00", "002200.36 50", "line 30  LC,$15,Y USB8C"),
    ("002234.40", "000002.37 0A", "line 31  KCI,$15,2.0"),
    ("002235.00", "002313.73 40", "line 32  BZXH,Y NORR"),
    ("002235.40", "002342.00 80  060000.20 50", "line 33  L(BU,48),Y UCBF2+3.0"),
    ("002236.40", "001775.40 80  060000.21 10", "line 34  K(BU,48),Y NLST"),
    ("002237.40", "002241.36 C0", "line 35  BZAE,$+1.32"),
    ("002240.00", "000034.54 80  001000.00 F0", "line 36  CM0000(BU,1),$12+.44"),
    ("002241.00", "000003.37 0A", "line 37  KCI,$15,3.0"),
    ("002241.40", "002313.73 40", "line 38  BZXH,Y NORR"),
    ("002242.00", "002343.00 80  060000.20 50", "line 39  L(BU,48),Y UCBF2+4.0"),
    ("002243.00", "001775.40 80  060000.21 10", "line 40  K(BU,48),Y NOPUN"),
    ("002244.00", "002313.76 C0", "line 41  BZAE,Y NORR"),
    ("002244.40", "000034.55 80  001000.00 F0", "line 42  CM0000(BU,1),$12+.45"),
    # THE ROW THE LISTING PRINTS AS "002313.5C  C0".  Both glyphs are
    # digit zeros and the octal field proves it.
    ("002245.40", "002313.50 00", "line 43  B,Y NORR"),
    ("002246.00", "002322.30 10",
     "line 44  Y LIMC  LX,$12,Y UCX12  -LIM CARD- CONVERT BCD ZEROS"),
    # (2)001010 IS THE SAME BCD ZERO printed p.24 line 13 writes with
    # "LFI(BU,4),(2)1010,46" -- four bits there, six here, same
    # nibble, and the boot run's X LR IN ends full of it.
    ("002246.40", "120000.00 80  406000.20 50",
     "line 45  LI(BU,6),(2)001010  -TO TRUE ZEROS"),
    ("002247.40", "000000.06 8C  106000.15 70",
     "line 46  Y LL2  CT0110(V+I)(BU,6),.6($12)  -IS THIS BYTE A BCD ZERO"),
    ("002250.40", "002252.34 C4", "line 47  BZRZZ,$+1.32  -IF NOT TEST NEXT BYTE"),
    # A NEGATIVE DISPLACEMENT, printed as all ones: -.6 in a
    # twenty-four bit address field is 777777.72.
    ("002251.00", "777777.72 8C  006000.00 F0",
     "line 48  CM0000(BU,6),-.6($12)  -IF SO, REPLACE BY TRUE ZERO"),
    ("002252.00", "002247.70 4C", "line 49  CBR,$12,Y LL2"),
    ("002252.40", "002247.63 40", "line 50  BZXF,Y LL2"),
    ("002253.00", "002340.00 80  044600.06 70",
     "line 51  LF(BU,36,6),Y UCBF2+1.0  -LIMITS TO"),
    # LF IS C0011 AND SF IS CM0101, adjacent rows, the two
    # operand-selecting connectives.
    ("002254.00", "000034.00 80  022300.12 F0",
     "line 52  SF(BU,18,3),$12  -BINARY, PUT IN $12"),
    ("002255.00", "002341.00 80  044600.06 70", "line 53  LF(BU,36,6),Y UCBF2+2.0"),
    ("002256.00", "000034.34 80  022300.12 F0", "line 54  SF(BU,18,3),$12+.28"),
    ("002257.00", "005465.70 90", "line 55  KV,$12,S TERMI"),
    ("002257.40", "002262.32 42", "line 56  BXL,Y UCLLC"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.39 ")
finish(fails)
