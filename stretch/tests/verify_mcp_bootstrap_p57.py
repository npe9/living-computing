"""MCP INITIALIZATION, printed p.57 -- THE IOREQ SEARCH AND SORT.

Thirty-eight lines and all thirty-eight compile -- no comment rows on
the page at all.  decks/mcp_bootstrap_p57.strap carries the
derivations; this file carries the rows and what the injections did.

IT RUNS STRAIGHT INTO printed p.58.  Line 38 is "B,L NORM" at
003237.00 compiling 003237.50 00, and 003237.40 is p.58 line 5.

THE LAST SEVEN LINES ARE p.58's ERROR TAIL TO THE BIT (p.57 lines 32,
33, 34, 35 and 37 equal p.58 lines 31, 33, 34, 35 and 38), differing
only in line 36's branch target.  And line 32 is the row that gives
T LPPEN its dds: it writes "CM0000(BU,1),T LPPEN(L XPP)" where p.58
line 31 writes the operation BARE, and both compile
000000.47 84 001000.00 F0.

THREE OF p.58's FIVE NEW SYMBOLS ARE CONFIRMED HERE from different
rows: T IOREQ (lines 14 and 25), T LAST (lines 13 and 24) and LASTPP
(line 33).

ALL THIRTY-EIGHT ROWS WERE BIT-EXACT ON THE FIRST RUN, including the
negative bit address, both (V+I) forms, the "$-1." location-counter
arithmetic and LVE's B0.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  L RLCT (8)2607.0 -> (8)2610.0 -- 2 FAIL, lines 1 and 10, the two
  rows that name it.
  L SEARA (8)3205.0 -> (8)3204.0 -- 1 FAIL, line 30.  This is the
  one symbol pointing BACKWARD off the page, onto printed p.56.
  T UIORQ (8)3514.0 -> (8)3515.0 -- 2 FAIL, lines 17 and 28.
  Line 5's "-0.8" loses its sign -- 1 FAIL, reading 000000.10 for
  777777.70.  The sign is the whole row: it steps the search DOWN
  one byte, which is what "-ACC LOW-- SWITCH RLCT" says.
  Line 6's "$-1." becomes "$" -- 1 FAIL, reading 003212.23 for
  003211.23.  The row stands at 003212.00, so the operand and the
  location counter check each other.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p57.strap").read())

SYMBOLS = {
    "LSEARB": "003207.40",
    "LSEARC": "003212.40",
    "LSEARD": "003216.40",
    "LSEARF": "003221.40",
    "LSEARE": "003224.00",
    "LSEARG": "003230.40",
    "LSKIP":  "003231.40",
    "LFIN3":  "003232.00",
}

ROWS = [
    ("003206.00", "002607.23 01",
     "line 1   LVI,L XNT,L RLCT"),
    ("003206.40", "000000.10 83  110027.20 50",
     "line 2   L(V+I)(BU,8),0.8(L IODX),46  -ENTER FIRST RLCT."),
    ("003207.40", "000000.10 83  110027.23 10",
     "line 3   L SEARB  KF(V+I)(BU,8),0.8(L IODX),46  -INNER LOOP"),
    ("003210.40", "003212.76 44",
     "line 4   BZALZ,L SEARC  -ACC. NOT LOW----STEP DOWN."),
    ("003211.00", "777777.70 83  010027.20 50",
     "line 5   L(BU,8),-0.8(L IODX),46  -ACC LOW-- SWITCH RLCT"),
    ("003212.00", "003211.23 B0",
     "line 6   LVE,L XNT,$-1.  -PUT PROPER ADDRESS IN XC VF."),
    ("003212.40", "003207.46 48",
     "line 7   L SEARC  CB,L IODX,L SEARB  -LOOP BACK ON NON ZERO CF."),
    ("003213.00", "000011.06 50",
     "line 8   LC,L IODX,$R  -LOAD XB CF."),
    ("003213.40", "000000.00 89  010000.00 F0",
     "line 9   CM0000(BU,8),0.0(L XNT),0.0  -ZERO PROPER RLCT SLOT."),
    ("003214.40", "002607.23 0D",
     "line 10  V-I,L XNT,L RLCT  -READY XC FOR RLSYM SEARCH."),
    ("003215.00", "000032.06 30",
     "line 11  LV,L IODX,L WORKX  -LOAD XB VF."),
    ("003215.40", "002614.00 89  010000.20 50",
     "line 12  L(BU,8),L CT(L XNT),0.0  -LOAD HIGH RLSYM."),
    ("003216.40", "000000.22 83  003221.74 00",
     "line 13  L SEARD  BZB,T LAST(L IODX),L SEARF  -IS THIS END OF TABLE"),
    ("003217.40", "003373.07 01",
     "line 14  LVI,L IODX,T IOREQ  -  YES ... INITIALIZE"),
    ("003220.00", "000000.37 05",
     "line 15  V+I,$15,0.0  -TO TEST FOR NOT OVERLAP MODE"),
    ("003220.40", "003221.70 42",
     "line 16  BXCZ,L SEARF  -OVERLAP MODE"),
    ("003221.00", "003514.07 01",
     "line 17  LVI,L IODX,T UIORQ  -IF NOT OVERLAP MODE"),
    ("003221.40", "000000.13 83  007000.23 10",
     "line 18  L SEARF  KF(BU,7),.11(L IODX)  -  NO....INNER SEARCH LOOP."),
    ("003222.40", "003224.36 C6",
     "line 19  BAEZ,L SEARE  -FOUND----STEP DOWN."),
    ("003223.00", "000001.07 05",
     "line 20  V+I,L IODX,1.0  -NOT FOUND----STEP XB VF."),
    ("003223.40", "003216.50 00",
     "line 21  B,L SEARD  -GO BACK AND TRY AGAIN."),
    ("003224.00", "000000.00 8A  000000.02 E3",
     "line 22  L SEARE  SWAPI,1,0.0(L WORKX),0.0(L IODX)  -SWAP IOREQ SLOTS."),
    ("003225.00", "000001.25 05",
     "line 23  V+I,L WORKX,1.0  -STEP XA VF."),
    ("003225.40", "000000.22 8A  003230.74 00",
     "line 24  BZB,T LAST(L WORKX),L SEARG  -IS THIS END OF IOREQ TABLE"),
    ("003226.40", "003373.25 01",
     "line 25  LVI,L WORKX,T IOREQ  -YES...INITIALIZE"),
    ("003227.00", "000000.37 05",
     "line 26  V+I,$15,0.0  -CHECK MODE"),
    ("003227.40", "003230.70 42",
     "line 27  BXCZ,L SEARG  -IF OVERLAP"),
    ("003230.00", "003514.25 01",
     "line 28  LVI,L WORKX,T UIORQ  -IF NOT OVERLAP MOAD"),
    ("003230.40", "003216.47 48",
     "line 29  L SEARG  CB+,L IODX,L SEARD  -  LOOP BACK ON NON-ZERO CF."),
    ("003231.00", "003205.24 48",
     "line 30  CB,L WORKX,L SEARA  -END OF SWAP AND SORT."),
    ("003231.40", "002605.22 10",
     "line 31  L SKIP  LX,L XNT,L PUT  -RESTORE LXNT INDEX."),
    ("003232.00", "000000.47 84  001000.00 F0",
     "line 32  L FIN3  CM0000(BU,1),T LPPEN(L XPP)"),
    ("003233.00", "002613.11 10",
     "line 33  SX,L XPP,LASTPP  -SAVE ADR. OF LAST PP ENTERED"),
    ("003233.40", "000002.11 07",
     "line 34  V+ICR,L XPP,2.0  -STEP PPREF INDEX."),
    ("003234.00", "000000.47 84  001000.36 F0",
     "line 35  CM1111(BU,1),T LPPEN(L XPP)  -TURN ON LPPEN BIT"),
    ("003235.00", "002601.62 80  003237.74 04",
     "line 36  BZBZ,L OVBIT,L NORM  -IF OVERLAP MODE"),
    ("003236.00", "002720.00 80  000024.06 E0",
     "line 37  SWAPI,3,L NOSAV,L XPP  -RESET INDEXES TO OVERLAP MODE"),
    ("003237.00", "003237.50 00",
     "line 38  B,L NORM  -NORMAL RETURN."),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.57 ")
finish(fails)
