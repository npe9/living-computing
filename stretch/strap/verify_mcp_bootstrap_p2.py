#!/usr/bin/env python3
"""verify_mcp_bootstrap_p2.py -- MCP's IPL bootstrap, printed page 2
(programs/mcp_bootstrap_p2.strap) against the listing's own printed
machine code.  docs/MCP_Mar63_001-249.pdf PDF p.9, header "PAGE
NUMBER 2".

CITED BY PRINTED PAGE AND CHECKED BY PDF PAGE.  This listing's
PDF->printed offset is NOT constant -- volume 1 duplicates pp.1-2 and
carries three blanks, volume 2 runs +249 at PDF 60 and +250 at PDF
160 -- so every citation here was read off the page's own "PAGE
NUMBER" header rather than computed (docs/NEXT.md 5i).

SIXTEEN ROWS CARRY MACHINE CODE and all sixteen are checked.  The
rest of the page is the banner, the listing-control pseudo-ops and
the comment rows, none of which emit anything.

THE MACHINE CODE WAS READ AT 600 DPI, cropped to the BINARY OUTPUT
column alone.  A 200 dpi read of a different deck once misread an
address digit and cost a session (docs/NEXT.md).
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("programs/mcp_bootstrap_p2.strap").read())

# The six symbols this page defines, at the locations it prints in its
# LOCATION column.  These are genuine: the assembler places them from
# the instruction stream, nothing SYNs them.
SYMBOLS = {
    "XIPLBS": "000041.00",
    "XVERFY": "000043.00",
    "XBEGIN": "000043.40",
    "XLOOP":  "000044.40",
    "XCLIND": "000046.40",
    "XCLSTO": "000050.40",
}

ROWS = [
    ("000040.00", "000041.00+ 000 000560 000001",
     "line 17  CW(CR),X IPL BS,X BS END-X IPL BS,1 -- the IPL control "
     "word; count 0o560 = 368 words, refill 1"),
    ("000041.00", "000043.44 00",
     "line 24  X IPL BS  BD,X BEGIN  -DISABLE AND START IPL"),
    ("000041.40", "000000.00+",
     "line 25  VF,0  -SLOT FOR TAPE CW"),
    ("000042.00", "000000.00+ 000 000000 000000",
     "line 26  XW,0  -SLOT FOR DISK CW"),
    ("000043.40", "000547.36 10",
     "line 28  X BEGIN  LX,$15,XW SR  - INITIALIZE TO CLEAR LOWER REGISTERS"),
    ("000044.00", "000000.22 00",
     "line 29  Z,0.0"),
    ("000044.40", "000002.22 0F",
     "line 30  X LOOP  Z,2.0($15)  -CLEAR LOWER REGESTERS"),
    ("000045.00", "000044.77 4C",
     "line 31  CBR+,$15,X LOOP"),
    ("000045.40", "000547.40 80 000000.20 50",
     "line 32  L(BU),XW SR+.32  -DONE CLEAR C AND D REGISTERS"),
    ("000046.40", "000047.00 46",
     "line 33  X CL IND  BMKZ,$+.32"),
    ("000047.00", "000046.63 80 006000.22 80",
     "line 34  M+I(BU,6),X CL IND+.19  -CLEAR NON MASKABLE INDIC"),
    ("000050.00", "000046.76 48",
     "line 35  CB,$15,X CL IND"),
    ("000050.40", "000000.22 0F",
     "line 36  X CLSTO  Z,0.0($15)  -CLEAR ONE WORD"),
    ("000051.00", "000052.10 46",
     "line 37  BADZ,$+1.0  -IF DONE CLEARING STORAGE"),
    ("000051.40", "000050.77 48",
     "line 38  CB+,15,XCLSTO  -ADVANCE AND RETURN"),
    ("000052.00", "000546.37 30",
     "line 39  SV,15,X S ROOF  -TEMPORARILY SAVE 7030 SIZE"),
]

# NOT CHECKED, and it cannot be: line 27's (A*)DD(BU,32,8),C911* is
# an IBM BCD message and strap_asm has no BCD table (C28-6129
# Appendix C).  The listing prints NO machine code for that row and
# its own comment calls it a "SLOT FOR DATE OF SOURCE TAPE", so there
# is nothing to compare against even if the table existed.  What the
# substitution must preserve is its WIDTH, and the rows after it --
# X BEGIN at 000043.40 onward -- are what prove it does.

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.2 "))
