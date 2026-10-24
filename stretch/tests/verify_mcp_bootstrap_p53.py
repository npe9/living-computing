#!/usr/bin/env python3
"""verify_mcp_bootstrap_p53.py -- the end of the initialization
routine and the IOD CARD ROUTINE, printed page 53
(../decks/mcp_bootstrap_p53.strap).
docs/MCP_Mar63_001-249.pdf PDF p.60, header "PAGE NUMBER 53".
AGENTS.md rule 3.

Fifty-one printed rows with binary output and nine symbol locations.

>>> IT CONFIRMS BOTH OF printed p.52's DERIVED STAND-INS. <<<

L OOPN is at 002775.40 (line 4) and L IODRN at 003021.40 (line 37).
Both were read off p.52 from ONE OCTAL DIGIT: "BXVZZ,L OOPN+1."
prints 002776.71 and "BAEZ,L IODRN" prints 003021.76, and in both
cases bit 18 is SET, which puts the target on the .40 half word.
Transcribing them as .00 was p.52's first draft and three rows
failed; this page says the corrected reading was right.

>>> AND IT SETTLES A NAME printed p.48 FLAGGED. <<<

Line 28 is "CM0000(BU,9),L IOSCR,0.0  -SET IODSQ COUNTER TO 1.".
p.48 line 46 defines that symbol at 002601.40 as "DRZ(BU,9),(1)",
and p.48's deck recorded that the name came off a row where the drum
had lost several glyphs -- "L ICSCR ... -ICDSQ COLNTER" -- with NO
COMPILED BIT depending on the spelling, and said the next page that
referenced it would decide.  At 900 dpi line 28 reads L IOSCR and
the dds (BU,9) matches.  The flag comes down.

A SECOND "$" IN FRONT OF AN OPERATION, AND IT IS STILL INERT.  Line
14 is "$TI,1,-1.0(L IODX),1.0(L XPP)" and the row compiles as a
plain TI, 777777.00 83 / 000001.02 A4.  printed p.43 line 6's
"$B,Q GO$A" was the first.  Two instances in two source decks, both
inert; C28-6129 printed p.37 accounts for a "$" on an OPERAND and
says nothing about one on an OPERATION.  Recorded, not guessed at.

A dds TRAVELS THROUGH A SYN TWICE MORE.  Lines 37-41 are four bare
operations with no data description written -- "M+1,T IODCT(L XPP)",
"L,L IREF(L IODX),0.0", "K,T LREFN(L XPP)", "ST,T LREFN(L XPP)" --
and every one prints a length of 014000, TWELVE.  L IREF is printed
p.48 line 5's "SYN(BU,12),0.52".

AND THE LISTING DISTINGUISHES A FIELD SYMBOL FROM AN ADDRESS, which
is printed p.50's lesson in use: L IREF, T IODCT and T LREFN are BIT
OFFSETS inside a table entry -- 0.52, 0.52 and 0.40 -- not storage
addresses, and the index register supplies the entry.

TWO ZEROS-AS-C ROWS, 13e's page-wide shape again: line 3's
"002700.22 C0" is 00 and line 11's "001000.36 FC" is F0, both
settled by rows already checked in this corpus.

TWO INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  T LREFN's stand-in moved from 0.40 to 0.41 -- 2 FAILs, lines 39
  and 41, the only two rows that use it, and no symbol moves.
  L IREF's stand-in dds dropped, "SYN(BU,12)" -> "SYN" -- 1 FAIL,
  line 38, reading 000000.20 50 where the listing prints 014000.20
  50.  Lines 37, 39 and 41 still pass because T IODCT and T LREFN
  keep theirs, which is the cross-page dds isolated to one symbol.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p53.strap").read())

SYMBOLS = {
    # >>> printed p.52's TWO DERIVED STAND-INS, both read off bit 18.
    "LOOPN":  "002775.40",
    "LIODRN": "003021.40",
    "LINITB": "003003.40",
    "LINBB":  "003012.00",
    "LINITC": "003015.40",
    "LIODA":  "003027.00",
    "LIOFUL": "003030.40",
    "LIOD1":  "003032.00",
    "LTYPR":  "003036.00",
}

ROWS = [
    ("002774.00", "002677.23 0D",
     "line 1   V-I,L XNT,L NTPU-1.  -CLEAR NON-TAPE"),
    ("002774.40", "000031.22 50",
     "line 2   LC,L XNT,L XNT"),
    ("002775.00", "002700.22 00",
     "line 3   Z,L NTPU  [listing prints C0]"),
    ("002775.40", "002700.22 09",
     "line 4   L OOPN  Z,L NTPU(L XNT)"),
    ("002776.00", "002775.63 C8",
     "line 5   CB-,L XNT,L OOPN"),
    ("002776.40", "000000.44 84  001000.20 50",
     "line 6   L(BU,1),T JBPRO(L XPP)  -IS PP REF TBL AVAILABLE"),
    ("002777.40", "003003.74 C4",
     "line 7   BZRZZ,L INITB  - YES----STEP"),
    ("003000.00", "000000.00 84  022000.20 50",
     "line 8   L(BU,18),T CRREF(L XPP)  -IS PP REF SLOT AVAIL"),
    ("003001.00", "003003.74 C6",
     "line 9   BRZZ,L INITB  - YES----STEP"),
    ("003001.40", "000001.37 02",
     "line 10  LCI,$15,1.0  -NO -- ERROR FLAG 1."),
    ("003002.00", "002601.51 80  001000.36 F0",
     "line 11  CM1111(BU,1),L FINB,0.0  -SET FINAL BIT  [listing FC]"),
    ("003003.00", "003262.50 00",
     "line 12  B,L ERR4"),
    ("003003.40", "000000.22 04",
     "line 13  L INITB  Z,0.0(L XPP)  -CLEAR SLOT."),
    ("003004.00", "777777.00 83  000001.02 A4",
     "line 14  $TI,1,-1.0(L IODX),1.0(L XPP)  -STORE PP ID"),
    ("003005.00", "000000.47 84  001000.36 F0",
     "line 15  CM1111(BU,1),T LPPEN(L XPP)"),
    ("003006.00", "000001.00 83  030000.20 50",
     "line 16  L(BU,24),1.0(L IODX)  -LOOK FOR REJ END COMBO"),
    ("003007.00", "003170.34 C2",
     "line 17  BRZ,L FINAL  -( IF SO"),
    ("003007.40", "002734.00 80  030000.21 10",
     "line 18  K(BU,24),L IOD  -IS THE FIRST CARD AN IOD"),
    ("003010.40", "003012.36 C2",
     "line 19  BAE,L INBB  -YES"),
    ("003011.00", "000010.37 02",
     "line 20  LCI,$15,8.0  -NO  SEND ERROR FLAG"),
    ("003011.40", "003241.10 00",
     "line 21  B,L ERROR"),
    ("003012.00", "002601.62 80  003015.34 02",
     "line 22  L INBB  BB,L OVBIT,L INITC-.32"),
    ("003013.00", "000000.00 85  000000.20 50",
     "line 23  L(BU,64),0.0(L XIO),0.0  -IS IOREQ SLOT AVAILABLE"),
    ("003014.00", "003015.74 C6",
     "line 24  BRZZ,L INITC  - YES----STEP"),
    ("003014.40", "003030.50 00",
     "line 25  B,L IOFUL  - NO----TO SPECIAL ROUTINE"),
    ("003015.00", "000000.22 05",
     "line 26  Z,0.0(L XIO)"),
    ("003015.40", "000000.13 34",
     "line 27  L INITC  SV,L XIO,0.0(L XPP)  -PUT CRREF IN PPREF SLOT"),
    ("003016.00", "002601.40 80  011000.00 F0",
     "line 28  CM0000(BU,9),L IOSCR,0.0  -SET IODSQ COUNTER TO 1."),
    ("003017.00", "002601.40 80  011000.22 B0",
     "line 29  M+1(BU,9),L IOSCR"),
    ("003020.00", "002601.31 80  007000.00 F0",
     "line 30  CM0000,L TAPEC  -SET REEL COUNT TO ZERO"),
    ("003021.00", "002750.10 00",
     "line 31  B,L FWA  -BRANCH TO TEST"),
    ("003021.40", "000000.64 84  014000.22 B0",
     "line 37  L IODRN  M+1,T IODCT(L XPP)  -STEP IOD COUNTER"),
    ("003022.40", "000000.64 83  014000.20 50",
     "line 38  L,L IREF(L IODX),0.0  -COMPARE FOR LARGEST"),
    ("003023.40", "000000.50 84  014000.21 10",
     "line 39  K,T LREFN(L XPP)  - PP REFERENCE NUMBER"),
    ("003024.40", "003027.36 46",
     "line 40  BALZ,L IODA  -THIS NO. IS LOW"),
    ("003025.00", "000000.50 84  014000.20 D0",
     "line 41  ST,T LREFN(L XPP)  -HIGH.... REPLACE BY"),
    ("003026.00", "002601.62 80  003031.74 02",
     "line 42  BB,L OVBIT,L IOD1-0.32"),
    ("003027.00", "000000.00 85  000000.20 50",
     "line 43  L IODA  L(BU,64),0.0(L XIO),0.0"),
    ("003030.00", "003032.34 C6",
     "line 44  BRZZ,L IOD1  - YES----STEP"),
    ("003030.40", "000002.37 02",
     "line 45  L IOFUL  LCI,$15,2.0  -NO -- ERROR FLAG 2."),
    ("003031.00", "003262.50 00",
     "line 46  B,L ERR4"),
    ("003031.40", "000000.22 05",
     "line 47  Z,0.0(L XIO)"),
    ("003032.00", "000002.00 83  060000.20 50",
     "line 48  L IOD1  L(BU,48),2.0(L IODX),0.0  -IS TYPE TAPE."),
    ("003033.00", "002733.00 80  060000.21 10",
     "line 49  K(BU,48),L TAPE,0.0"),
    ("003034.00", "003077.36 C6",
     "line 50  BAEZ,L IODTP  - YES----TO TAPE"),
    ("003034.40", "002601.52 80  001000.36 F0",
     "line 51  CM1111(BU,1),L NTB,0.0  - NO----SET NON-TAPE"),
    ("003035.40", "002570.24 10",
     "line 52  LX,L WORKX,L XTYPE  -DECODE TYPE AND ENTER"),
    ("003036.00", "000002.00 83  060000.20 50",
     "line 53  L TYPR  L(BU,48),2.0(L IODX)  -IO REQUEST SLOT"),
    ("003037.00", "000000.00 8A  060000.21 10",
     "line 54  K(BU,48),.0(L WORKX)"),
    ("003040.00", "003042.36 C2",
     "line 55  BAE,L CODE  -TYPE FOUND"),
    ("003040.40", "003036.25 48",
     "line 56  CB+,L WORKX,L TYPR  -NO TRY AGAIN"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.53 ")
finish(fails)
