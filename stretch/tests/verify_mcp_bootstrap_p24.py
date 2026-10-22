#!/usr/bin/env python3
"""verify_mcp_bootstrap_p24.py -- MCP INITIALIZATION, printed page 24
(../decks/mcp_bootstrap_p24.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.31, header "PAGE NUMBER 24".  AGENTS.md rule 3.

Thirty-seven printed rows with binary output.

>>> THIS PAGE SETTLES PRINTED p.23's PREDICTION.  p.22 line 35 loads
an immediate X VTIME = 001242.02 and p.23 line 15 loads X VDATE =
001242.70, so the two constants had to sit 0o70 bits apart in one
word region.  Lines 50 and 51 DEFINE them, at 001242.02 and
001242.70 exactly -- and the prediction was committed before this
page was opened. <<<

AND FOUR MORE FORWARD REFERENCES LAND: X VZER at 001204.40, X VZER 1
at 001207.00, X VNOTM at 001211.40 and X VTDER at 001225.40 were all
SYN'd on pp.22-23 from those pages' binary output.  This page defines
every one of them at the address that was read off an instruction.

THE ASSEMBLER GAINED "DRZ" FOR LINE 52, "X VSTOR DRZ(BU),100", whose
binary output prints 000144.00 -- 0o144 is a hundred, so it reserves
a hundred WORDS and the printed value is the SIZE.  DR and DRZ are
the pair C22-6531 and C28-6129 both carry, "with and without
zeroing"; only DR existed here.

ROWS DELIBERATELY ABSENT, as on printed p.21: the (IQS*)DD rows print
nothing; the DRZ row prints its SIZE, not a word; and line 45's SYN
prints its VALUE, checked as X VTMST == 000006.00 in SYMBOLS.

LINE 44's CNOP IS IN THE TABLE, though, and the other three are not:
it is the one that had to PAD, and it prints 000000.30 00 -- a NOP
half word.  That is the difference between a CNOP that rounds and a
CNOP that finds itself already rounded, visible in the listing.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p24.strap").read())

SYMBOLS = {
    "XIO3":   "001174.40",
    "XIO4":   "001176.00",
    "XIO5":   "001177.40",
    "XIO6":   "001202.00",
    "XVZER":  "001204.40",
    "XVZER1": "001207.00",
    "XVNOTM": "001211.40",
    "XVTDER": "001225.40",
    "XVMESS": "001231.00",
    "XVTMST": "000006.00",
    "XVTMCW": "001237.00",
    "XVTCW":  "001240.00",
    "XVCLOK": "001241.00",
    "XVTIME": "001242.02",
    "XVDATE": "001242.70",
    "XVSTOR": "001243.50",
    "XIOCW":  "001410.00",
    "XIOCW1": "001411.00",
    "XIOSTA": "001412.00",
}

_CM28 = "000000.34 8E 001000.36 F0"   # CM1111(BU,1),.28($14)
_BXIO1 = "001153.50 00"               # B,X IO 1
_LFI = "500000.00 80 404027.06 70"    # LFI(BU,4),(2)1010,46
_ST4 = "777777.74 81 004027.20 D0"    # ST(BU,4),-.4($1),46
_DIV = "740000.00 80 406042.21 D0"    # /I(BU,6),60,-60

ROWS = [
    ("001174.40", _CM28, "line 1   X IO 3  CM1111(BU,1),.28($14)  -UNIT TO NOT AVAILABLE"),
    ("001175.40", _BXIO1,                    "line 2   B,X IO 1"),
    ("001176.00", _CM28, "line 3   X IO 4  CM1111(BU,1),.28($14)  -UNIT NOT AVAILABLE"),
    ("001177.00", _BXIO1,                    "line 4   B,X IO 1"),
    ("001177.40", "000000.73 8E 004027.20 50",
     "line 5   X IO 5  L(BU,4),.59($14),46  - GET UNIT COUNT"),
    ("001200.40", "000011.24 50",            "line 6   LC,$10,$R"),
    ("001201.00", "001153.70 42",
     "line 7   BXCZ,X IO 1  IF NO UNITS ON CHANNEL (DEAD CHANNEL)"),
    ("001201.40", "000000.34 3E",            "line 8   LV,$14,0.0($14)  -GET UST BASE"),
    ("001202.00", _CM28, "line 9   X IO 6  CM1111(BU,1),.28($14)  -UNIT TO NOT AVAILABLE"),
    ("001203.00", "000001.35 05",            "line 10  V+I,$14,1.0"),
    ("001203.40", "001202.24 48",            "line 11  CB,$10,X IO6  -IF ALL UNITS KILLED"),
    ("001204.00", _BXIO1,                    "line 12  B,X IO 1  - RETURN FOR MORE OPTIONS"),
    ("001204.40", _LFI,
     "line 13  XVZER  LFI(BU,4),(2)1010,46  - BCD ZERO"),
    ("001205.40", _ST4,                      "line 14  ST(BU,4),-.4($1),46"),
    ("001206.40", "001076.10 00",            "line 15  B,XVCONS"),
    ("001207.00", _LFI,
     "line 16  XVZER1  LFI(BU,4),(2)1010,46  - BCD ZERO"),
    ("001210.00", _ST4,                      "line 17  ST(BU,4),-.4($1),46"),
    ("001211.00", "001132.50 00",            "line 18  B,XVCONT"),
    ("001211.40", "000001.34 80 032042.20 50",
     "line 19  XV NOTM  L(BU,26),$TC,-60  - GET TIME"),
    ("001212.40", "001243.43 01",            "line 20  LVI,$1,XVSTOR"),
    ("001213.00", _DIV,                      "line 21  /I(BU,6),60,-60"),
    ("001214.00", "000015.66 80 006000.06 70",
     "line 22  C0011(BU,6),$RM+.54  -SECONDS IN RM IN BINARY"),
    ("001215.00", "000000.30 81 006000.12 F0",
     "line 23  CM0101(BU,6),0.24($1)  - SAVE BINARY SECONDS"),
    ("001216.00", _DIV,
     "line 24  /I(BU,6),60,-60  -COMPUTE HOUR AND MINUTES"),
    ("001217.00", "000010.00 80 000010.21 B0",
     "line 25  CV(BU),$L,16  -CONVERT HOURS TO DECIMAL"),
    ("001220.00", "000015.66 80 006000.22 30",
     "line 26  LTRCV(BU,6),$RM+.54  - CONVERT MINUTES TO DECIMAL"),
    ("001221.00", "000017.64 80 010004.06 70", "line 27  C0011(BU,8),$TR+.52,8"),
    ("001222.00", "000000.30 81 006000.22 30",
     "line 28  LTRCV(BU,6),0.24($1)  -CONVERT SECONDS"),
    ("001223.00", "000017.64 80 010000.06 70", "line 29  C0011(BU,8),$TR+.52"),
    ("001224.00", "001034.00 80 030000.20 D0", "line 30  ST(BU,24),XLRIN"),
    ("001225.00", "001072.50 00",            "line 31  B,XVBACK"),
    ("001225.40", "000000.00 8F 001237.13 00",
     "line 32  XVTDER  W(SEOP),0.0($15),XVTMCW  -WRITE OUT ERROR MESSAGE."),
    ("001226.40", "000066.40 80",            "line 33  SIC,X73"),
    ("001227.00", "000057.50 00",            "line 34  B,X 71  - I/O TEST"),
    ("001227.40", "001672.23 80 001000.00 F0",
     "line 35  CM0000(BU,1),XVSWCH+.19"),
    ("001230.40", "001152.10 00",            "line 36  B,XV IORP"),
    ("001231.00", "375",
     "line 38  XVMESS  DD(BU,8),(2)1111 1101  -CONTROL CODE FOR CARRAIGE RETURN"),
    ("001231.10", "002",                     "line 39  DD(BU,8),(2)00000010  -RED $"),
    ("001236.20", "375",                     "line 42  DD(BU,8),(2) 1111 1101  -CARRAIGE RETURN"),
    ("001236.30", "376",                     "line 43  DD(BU,8),(2) 1111 1110  -END OF MESSAGE"),
    ("001236.40", "000000.30 00",            "line 44  CNOP  (the one that had to PAD)"),
    ("001237.00", "001034.00+ 100 000003 001240",
     "line 46  XVTMCW  CW,XLRIN,3,XVTCW(.25)1"),
    ("001240.00", "001231.00+ 000 000006 000000",
     "line 47  XVTCW  CW,XVMESS,XVTMST"),
    ("001410.00", "001034.00+ 100 000003 001411",
     "line 53  XICCW  CW,XLRIN,3,XIOCW1(.25)1"),
    ("001411.00", "001412.00+ 000 000005 000000",
     "line 54  X IO CW1  CW,X IO STA,X IO STK  -CW USED TO REQUEST IO STATUS"),
    ("001412.00", "375",
     "line 56  X IO STA  DD(BU,8),(2)1111 1101  -CONTROL CODE CARRIAGE RETURN"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.24 "))
