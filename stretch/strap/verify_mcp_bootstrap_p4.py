#!/usr/bin/env python3
"""verify_mcp_bootstrap_p4.py -- MCP's IPL bootstrap, printed page 4
(programs/mcp_bootstrap_p4.strap) against the listing's own printed
machine code.  docs/MCP_Mar63_001-249.pdf PDF p.11, header "PAGE
NUMBER 4".  AGENTS.md rule 3.

THIRTY-SEVEN ROWS CARRY MACHINE CODE and all thirty-seven are
checked, including the page's `LVS` -- the first in this corpus.

LVS's ADDRESS FIELD IS A REGISTER MASK, and that is settled by
arithmetic on two listing rows rather than by reading prose:

  printed p.4  line 23   000050.03 0B   LVS,$1,$12,$14
  printed p.15 line 17   000150.23 0B   LVS,$9,$12,$11,$14

X22-6533's IMMEDIATE INDEX ARITHMETIC format is ADDRESS(0-18),
J(19-22), then 10000 and the four-bit OP in 23-31, and LVS is
100001011.  Both rows carry exactly that nine-bit field.  Both carry
their written destination in J: 0001 and 1001.  And in both, the
bits set in the 19-bit ADDRESS field are precisely the numbers of the
source registers the statement names --

  p.4  bits 12 and 14 set, for $12 and $14
  p.15 bits 11, 12 and 14 set, for $12, $11 and $14

-- five distinct selections across two rows, matching in every
position, with bits 16-18 zero in both.  Register n is bit n of a
sixteen-bit mask at bits 0-15.

THE HEX BYTE IS 0B, NOT CB.  This scan renders digit zero with a
visible gap at the right, so a leading 0 reads as C: the same page
prints `000050.C3` where the octal field can only be `03`.  The
arithmetic decides it, as it decided p.3 line 10's B0 -- with CB the
operation field would be 111001011, which is no operation on the
pocket card at all.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("programs/mcp_bootstrap_p4.strap").read())

# The twelve symbols this page defines.  The ten SYN'd externals are
# NOT here: a SYN makes its own address come out right by
# construction, and each is cited in the program header from the page
# that defines it.
SYMBOLS = {
    "X9A":    "000104.00",
    "X9A1":   "000105.00",
    "XERR07": "000106.00",
    "XERR08": "000107.00",
    "X9ACCW": "000110.00",
    "XERR09": "000111.00",
    "X9A3":   "000114.00",
    "X9A3A":  "000114.40",
    "X9A4":   "000115.00",
    "X9A5":   "000121.40",
    "XDONE":  "000125.40",
    "XERR10": "000126.40",
}

ROWS = [
    # ---- FETCH PROSA ----
    ("000104.00", "000000.00 8F 000552.11 00",
     "line 5   X9 A  RD(SEOP),0.0($15),X PROSA  -FETCH PROSA"),
    # The listing writes this one WITHOUT blanks, "SIC,XERRAD", and the
    # next but one WITH them, "SIC,X ERR AD".  Identical machine code.
    ("000105.00", "000551.00 80",
     "line 6   X9 A 1  SIC,XERRAD"),
    ("000105.40", "000133.03 46",
     "line 7   BEKJZ,X ERROR- EXCHANGE ERROR"),
    ("000106.00", "000551.00 80",
     "line 8   X ERR 07  SIC,X ERR AD"),
    ("000106.40", "000133.03 C6",
     "line 9   BUNRJZ,X ERROR  -IF UNIT NOT READY REJECT"),
    ("000107.00", "000551.00 80",
     "line 10  X ERR 08  SIC,X ERR AD"),
    ("000107.40", "000133.04 46",
     "line 11  BCBJZ,X ERROR  -IF CHANNEL BUSY REJECT"),
    ("000110.00", "000000.00 8F 000041.21 00",
     "line 12  X9 A CCW  CCW,0($15),X IPL BS"),
    ("000111.00", "000551.00 80",
     "line 13  X ERR 09  SIC,X ERR AD"),
    ("000111.40", "000133.03 46",
     "line 14  BEKJZ,X ERROR  -IF EXCHANGE ERROR FOR CCW"),
    ("000112.00", "000041.30 80 000110.34 02",
     "line 15  BB,X IPL BS+.24,X9ACCW  -TRY AGAIN IF BUSY"),
    ("000113.00", "000041.23 80 005000.07 70",
     "line 16  CT0011(BU,5),X IPL BS+.19"),
    ("000114.00", "000125.74 C0",
     "line 17  X9 A 3  BZRZ,X DONE  -SUCCESSFUL"),
    ("000114.40", "000115.10 00",
     "line 18  X9 A 3A  B,X9A4  -RETURN AFTER IO TEST"),
    # ---- take the record apart ----
    ("000115.00", "011407.30 10",
     "line 19  X9 A 4  LX,$12,X BUFER+1.0  - GET DICTIONARY"),
    ("000115.40", "000034.31 50",
     "line 20  SC,$12,$12"),
    ("000116.00", "011411.34 10",
     "line 21  LX,$14,X BUFER + 3.0  -GET INDEX"),
    ("000116.40", "000036.35 50",
     "line 22  SC,$14,$14"),
    # THE FIRST LVS IN THIS CORPUS -- see the module docstring.  The
    # 19-bit address field is 80, i.e. bits 12 and 14 set, for the two
    # source registers the statement names.
    ("000117.00", "000050.03 0B",
     "line 23  LVS,$1,$12,$14  -WORDS PRECEEDING MCP"),
    ("000117.40", "011413.26 10",
     "line 24  LX,$11,X BUFER+5.0  - GET IPL"),
    ("000120.00", "000033.27 50",
     "line 25  SC,$11,$11"),
    ("000120.40", "011415.24 10",
     "line 26  LX,$10,X BUFER+7.0  -GET MCP SIZE"),
    ("000121.00", "000032.25 50",
     "line 27  SC,$10,$10"),
    ("000121.40", "011406.00 81 000621.26 20",
     "line 28  X9 A 5  T,$11,X BUFER($1),X BS END  -MOVE MCP IPL"),
    # INDEX REGISTER ZERO, and the machine code says so: 80 here where
    # line 38's "($15)" prints 8F.
    ("000122.40", "000000.00 80 000000.33 00",
     "line 29  REL(SEOP),0.0($0)  -RELEASE DISK"),
    ("000123.40", "000631.03 C2",
     "line 30  BUNRJ,X ERR 12"),
    ("000124.00", "377777.01 02",
     "line 31  LCI,0,(8)377777.0"),
    ("000124.40", "000124.40 48",
     "line 32  CB,0,$"),
    ("000125.00", "000622.10 00",
     "line 33  B,X 10  -TO MCPIPL"),
    # ---- end of the PROSA file ----
    ("000125.40", "000041.25 80 000127.74 02",
     "line 34  X DONE  BB,X IPL BS+.21,X DONE+2.0"),
    ("000126.40", "000551.00 80",
     "line 35  X ERR 10  SIC,X ERR AD"),
    ("000127.00", "000133.10 00",
     "line 36  B,X ERROR  -OTHER STATUS BITS ON"),
    ("000127.40", "000020.31 80 001000.36 F0",
     "line 37  CM1111(BU,1),$0 +.25  -END OF PROSA FILE"),
    ("000130.40", "000000.00 8F 000000.33 00",
     "line 38  REL(SEOP),0.0($15)  - CLEAR STATUS BITS"),
    ("000131.40", "000066.40 80",
     "line 39  SIC,X7 3"),
    ("000132.00", "000057.50 00",
     "line 40  B,X7 1  - IO TEST"),
    ("000132.40", "000114.50 00",
     "line 41  B,X9 A 3A"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.4 "))
