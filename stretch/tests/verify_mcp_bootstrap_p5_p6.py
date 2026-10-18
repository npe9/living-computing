#!/usr/bin/env python3
"""verify_mcp_bootstrap_p5_p6.py -- MCP's IPL bootstrap, printed pages
5 and 6 (../decks/mcp_bootstrap_p5_p6.strap), against the listing's
own printed machine code.  docs/MCP_Mar63_001-249.pdf PDF pp.12-13,
headers "PAGE NUMBER 5" and "PAGE NUMBER 6".  AGENTS.md rule 3.

TWO PAGES, ONE FILE, FOR AN EVIDENCE REASON.  They are mutually
recursive -- p.5 branches to X 1B ERR and X 1D ERR, which p.6
defines; p.6 branches to X 1A ERR and X6 ERR, which p.5 defines.
Transcribed separately, each file would have to SYN the other's
labels from the very rows being checked, and a SYN is an input to a
check rather than a witness.  Together, all fourteen labels are
placed by the assembler from the instruction stream, and every one of
the fifty-three machine-code rows is a real check.

FIFTY-THREE ROWS, ALL FIFTY-THREE CHECKED.

WHAT THIS PAGE ADDED TO THE ASSEMBLER, and the asymmetry is the
point: `GONG` is new, `LF` only looked new.

  GONG -- Reference Manual printed p.150 gives the IBM 7152
  Operator's Console's entire CONTROL table as four codes, 016, 017,
  116 and "177 Sound Gong.  This function causes a clearly audible
  gong to sound a single stroke"; p.5 line 45 prints 000177 in the
  code field with .15 = CTLSEOP.  Two independent sources, the same
  standard SPFL met.  (177 is Backspace File on the 729 IV: same
  octal, different device.)

  LF -- not a missing instruction but the connective C0011, which
  this assembler has always encoded.  See NEXT.md 6d; the tell was
  that the decoded modifier bits contradicted the written (BU),
  because for a connective bits 51-54 are the connective function.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p5_p6.strap").read())

# The fourteen labels the two pages define between them.  The six
# SYN'd externals are not here; each is cited in the program header
# from the page that defines it (pp.8, 13 and 37).
SYMBOLS = {
    "XERROR": "000133.00",
    "XERRSH": "000134.00",
    "X1ERR":  "000136.00",
    "X1AERR": "000144.00",
    "X1EERR": "000151.00",
    "X2ERR":  "000152.40",
    "X2AERR": "000157.00",
    "X3ERR":  "000161.00",
    "X4ERR":  "000164.40",
    "X5ERR":  "000166.00",
    "X6ERR":  "000166.40",
    "X7ERR":  "000170.00",
    "X1BERR": "000171.40",
    "X1CERR": "000173.00",
    "X1DERR": "000175.40",
}

ROWS = [
    # ---- printed p.5: find the error code in the table ----
    ("000133.00", "000245.04 10",
     "p.5 line 5   X ERROR  LX,$2,X ERR IN  -INITIALIZE WITH BASE AND SIZE"),
    ("000133.40", "000551.02 30",
     "p.5 line 7   LV,$1,X ERR AD  -GET BIASED ERROR ADDRESS"),
    ("000134.00", "000000.02 92",
     "p.5 line 8   X ERR SH  KV,$1,0.0($2)  -TEST AGAINST TABLE CODE"),
    ("000134.40", "000136.32 C2",
     "p.5 line 9   BXE,X 1 ERR  -IF CODES ARE EQUAL"),
    ("000135.00", "000134.05 48",
     "p.5 line 10  CB+,$2,X ERR SH  -TO TEST NEXT CODE"),
    ("000135.40", "000135.44 00",
     "p.5 line 11  BD,$  -IPL CONTAMINATED"),
    # LF IS THE CONNECTIVE C0011.  Bits 51-59 are 001100111 = the
    # pocket card's C (xxxx00111) with xxxx = 0011.
    ("000136.00", "000551.00 80 025300.46 70",
     "p.5 line 12  X1 ERR  LF(BU,21,3),X ERR AD,1  -BREAK ADDRESS INTO "
     "EIGHT BIT BYTES"),
    ("000137.00", "000000.44 32",
     "p.5 line 14  LV,$2,.32($2)  -GET ADDRESS OF MESSAGE"),
    ("000137.40", "000000.20 82 060004.22 90",
     "p.5 line 15  M+MG(BU,48,8),.8+.8($2),8  -SKIPPING OVER CONTROL CODES"),
    ("000140.40", "000001.00 82 010000.22 90",
     "p.5 line 17  M+MG(BU,8,8),.8+.48+.8($2)  -FORM HALF WORD PORTION"),
    ("000141.40", "000247.05 D0",
     "p.5 line 18  SVA,$2,XMSG CW  -INITIALIZE CW"),
    # S YCOCH is defined eighty-five printed pages away, on p.37,
    # under a different PUNID -- but it is the SAME ASSEMBLY, not a
    # different deck.  Printed p.15 line 5 is the statement
    # "PUNID,11C11IPL", which changes what is punched into the cards
    # and does not end the assembly.  The first version of this
    # comment said "a DIFFERENT DECK"; see the program file.
    ("000142.00", "002156.02 30",
     "p.5 line 19  LV,$1,S YCOCH  -GET CONSOLE CHANNEL SLOT CONTENT"),
    ("000142.40", "000157.31 40",
     "p.5 line 20  BZXVZ,X 2A ERR  -IF CHANNEL NUMBER PRESENT"),
    ("000143.00", "000020.03 01",
     "p.5 line 21  LVI,$1,(8)20.0  -NO* ENTER FIRST CHANNEL OF BASIC EXCHANGE"),
    ("000143.40", "000040.03 02",
     "p.5 line 23  LCI,$1,32.  -GET MAXIMUM SIZE OF BASIC EXCHANGE"),
    ("000144.00", "000175.40 80",
     "p.5 line 25  X1A ERR  SIC,X 1D ERR"),
    ("000144.40", "000171.50 00",
     "p.5 line 26  B,X 1B ERR  -TO CLEAR OUT OLD CHANNEL STATUS BITS"),
    ("000145.00", "000000.00 81 000000.15 00",
     "p.5 line 28  CTL(SEOP),0.0($1),0.0  -ILLEGAL IO CONTROL CODE"),
    ("000146.00", "000166.43 42",
     "p.5 line 29  BEKJ,X6 ERR  -EXHAUSTED ALL CHANNELS OR EXCHANGE ERROR"),
    ("000146.40", "000175.40 80",
     "p.5 line 31  SIC,X1DERR"),
    ("000147.00", "000171.44 46",
     "p.5 line 32  BCBJZ,X 1B ERR  -BUSY"),
    ("000147.40", "000166.03 C6",
     "p.5 line 33  BUNRJZ,X5 ERR  -CONTROL UNIT OR UNIT NOT READY"),
    ("000150.00", "000175.40 80",
     "p.5 line 34  SIC,X 1D ERR"),
    ("000150.40", "000171.50 00",
     "p.5 line 35  B,X1B ERR  - TO RELEASE STATUS BIT"),
    ("000151.00", "000000.00 81 000000.17 00",
     "p.5 line 36  X 1E ERR  LOC(SEOP),0.0($1),0.0  -TEST IF TAPE CHANNEL"),
    ("000152.00", "000166.43 42",
     "p.5 line 37  BEKJ,X6ERR"),
    ("000152.40", "000000.00 81 000253.21 00",
     "p.5 line 39  X 2 ERR  CCW,0.0($1),XERR CW  -GET CW"),
    ("000153.40", "000166.43 42",
     "p.5 line 40  BEKJ,X6 ERR"),
    ("000154.00", "000253.30 80 000152.74 02",
     "p.5 line 41  BB,X ERR CW+.24,X 2 ERR  -TEST SEOP BIT"),
    ("000155.00", "000253.23 80 000166.34 00",
     "p.5 line 42  BZB,X ERR CW+.19,X 5 ERR  -TEST IF TAPE UNIT"),
    ("000156.00", "000175.40 80",
     "p.5 line 43  SIC,X 1D ERR"),
    ("000156.40", "000171.50 00",
     "p.5 line 44  B,X1B ERR  -NON TAPE *RELEASE STATUS BIT"),
    # THE FIRST GONG IN THE CORPUS.  000177 is RefMan p.150's
    # "Sound Gong"; .15 = CTLSEOP, so the mnemonic IS a CONTROL.
    ("000157.00", "000000.00 81 000177.15 00",
     "p.5 line 45  X 2A ERR  GONG(SEOP),0.0($1)  - ISSUE CONSOLE COMMAND"),
    ("000160.00", "000166.43 42",
     "p.5 line 46  BEKJ,X 6 ERR"),
    ("000160.40", "000166.03 C6",
     "p.5 line 47  BUNRJZ,X 5 ERR  -REFERENCED UNIT NOT READY"),
    ("000161.00", "000000.00 81 000253.21 00",
     "p.5 line 48  X 3 ERR  CCW,0.0($1),X ERR CW  -GET GONG CW"),
    ("000162.00", "000166.43 42",
     "p.5 line 49  BEKJ,X6ERR  -IF EXCHANGE ERROR"),
    ("000162.40", "000253.30 80 000161.34 02",
     "p.5 line 50  BB,X ERR CW+.24,X3 ERR  -TEST SEOP BIT"),
    ("000163.40", "000253.23 80 000166.34 02",
     "p.5 line 51  BB,X ERR CW+.19,X 5 ERR  -IF CONSOLE * NO EPGK"),
    ("000164.40", "000000.00 81 000246.13 00",
     "p.5 line 52  X4 ERR  W(SEOP),0.0($1),X MS CW1  -CONSOLE"),
    ("000165.40", "000166.50 00",
     "p.5 line 53  B,X 6 ERR"),
    ("000166.00", "000144.02 C8",
     "p.5 line 54  X 5 ERR  CBH,$1,X 1A ERR  -NOT DONE TESTING"),
    ("000166.40", "000551.00 80 000011.02 A0",
     "p.5 line 56  X6 ERR  TI,1,X ERR AD,$R  -DISPLAY ERROR ADDRESS IN "
     "CE CONSOLE"),
    # ---- printed p.6, twelve lines long ----
    ("000167.40", "000167.44 00",
     "p.6 line 1   BD,$  -LOOP"),
    ("000170.00", "000175.40 80",
     "p.6 line 3   X 7 ERR  SIC,X 1D ERR"),
    ("000170.40", "000171.50 00",
     "p.6 line 4   B,X 1B ERR - TO RELEASE STATUS BIT"),
    ("000171.00", "000144.10 00",
     "p.6 line 5   B,X 1A ERR  -TO LOCATE AGAIN"),
    ("000171.40", "000000.00 81 000000.33 00",
     "p.6 line 7   X1B ERR  REL(SEOP),0.0($1)  -CLEAR OUT OLD STATUS BITS"),
    ("000172.40", "000166.43 42",
     "p.6 line 8   BEKJ,X6 ERR"),
    ("000173.00", "000000.00 81 000253.21 00",
     "p.6 line 9   X1C ERR  CCW,0.0($1),X ERR CW"),
    ("000174.00", "000166.43 42",
     "p.6 line 10  BEKJ,X6 ERR"),
    ("000174.40", "000253.30 80 000173.34 02",
     "p.6 line 11  BB,X ERR CW+.24,X1C ERR  -IF RELEASED"),
    ("000175.40", "000000.10 00",
     "p.6 line 12  X1D ERR  B,0.0  -YES*BACK"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP pp.5-6 "))
