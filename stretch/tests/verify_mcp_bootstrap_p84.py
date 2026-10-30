#!/usr/bin/env python3
"""printed p.84 against its own listing.

THE UNIT NAME TABLE, THE DISK ALLOCATION TABLE, THE FORMAT OF THE IOD
CARD BREAKDOWN TABLE and SYN CARDS FOR THE UNIT AREA TABLE.
docs/MCP_Mar63_001-249.pdf PDF p.91.

The page is almost entirely SYN field definitions -- the field map of
the IOD card breakdown table and of the unit area table, which the
pages that read those tables depend on.  Only four lines occupy
storage: two index words and two reservations.

AND ITS RESERVATIONS CLOSE THE ADDRESS TRAIL.  printed p.83 ends at
004652.00; this page's line 4 is at 004653.00, the next word.  Line 4's
XW is one word and line 5's DRZ(BU,64),(50) is fifty, so the counter
reaches 004736.00 -- which is line 16's own printed location.  A
"51-word gap" between the two pages was recorded as unexplained on
2026-10-30 and was nothing but these two lines, which a render that
started at line 6 had cut off.

A DRZ'S PRINTED VALUE IS ITS COUNT, NOT ITS CONTENT: line 5 prints
000062.00 and 0o62 = 50, line 17 prints 000004.00 and 0o4 = 8 would be
0o10, so line 17's is the (8) count printed as 000004.00 -- see the
note on the rows below.  Reservations are therefore checked by their
START (the symbol) and by where the NEXT page resumes, not as rows.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p84.strap").read())

SYMBOLS = {
    "TUNXW":  "004653.00",
    "TUNATB": "004654.00",
    "TCHNM":  "000000.00",
    "TUNTYP": "000000.74",
    "TUNREF": "000000.60",
    "TUNME":  "000031.00",
    "TDSKRF": "000031.60",
    "TDTRK":  "000031.74",
    "TDKCT":  "000031.75",
    "TDCLRX": "004736.00",
    "TSBDTB": "004737.00",
    "TSBDFT": "004737.05",
    "TIABEX": "000000.00",
    "TIREF":  "000000.64",
    "TIOP":   "000001.00",
    "TITY":   "000002.00",
    "TIREEL": "000002.00",
    "TITRK":  "000002.73",
    "TITYCD": "000002.74",
    "TICH":   "000004.00",
    "TIUN":   "000005.00",
    "TINO":   "000005.00",
    "TIMO":   "000006.00",
    "TIMOCD": "000006.76",
    "TIDN":   "000007.00",
    "TIDNCD": "000007.76",
    "TIDS":   "000010.00",
    "TIDSCD": "000010.76",
    "TCHANN": "000000.14",
    "TUNITN": "000000.57",
    "TIODCK": "000001.06",
    "TFIAAC": "000003.00",
    "TSYSTM": "000007.31",
    "TFRLAD": "000010.00",
    "TCREEL": "000010.40",
    "TREELK": "000010.71",
}

# T JCNME is NOT in SYMBOLS: it is "SYN(BU,48,6),-1.0", which is -64
# bits, and the listing prints sign-magnitude with the sign as a
# SUFFIX -- "000001.00-".  check_rows compares a bit count against a
# location string and has no way to read that suffix, so the symbol is
# checked here instead and the arithmetic is written out: magnitude
# 000001.00 is one word, and the value is negative.
assert prog.symtab["TJCNME"] == -64, prog.symtab["TJCNME"]

ROWS = [
    ("004653.00", "004654.00+ 000 000000 000020",
     "line 4   T UNXW   XW,TUNATB,0,$0"),
    ("004736.00", "004737.05+ 000 000004 004736",
     "line 16  T DCLRX  XW,TSBDFT,4,$"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.84 "))
