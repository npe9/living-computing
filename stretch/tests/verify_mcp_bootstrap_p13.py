#!/usr/bin/env python3
"""verify_mcp_bootstrap_p13.py -- MCP's IPL bootstrap, printed page 13
(../decks/mcp_bootstrap_p13.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.20, header "PAGE NUMBER 13".  AGENTS.md rule 3.

THE PAGE THAT DEFINES WHAT THE OTHERS HAVE BEEN SYN-ING.  X S ROOF
and XW SR were SYN'd from this page by printed p.2's transcription,
the first MCP page this project read, and X ERR AD by pp.3 through 6.
Here they are placed by the assembler from the instruction stream
instead, which is the difference between an input to a check and a
witness.

TWO HALVES: lines 1-21 are the last three error messages, X MSG 27,
28 and 29, finishing the area pp.9-12 begin (so the same caveat
applies -- the listing prints no bytes for an (IQS*)DD row and only
the counting is checked); lines 22-38 are BOOTSTRAP DEFINITIONS and
IPL BOOTSTRAP PARAMETERS, which DO print, as control words and a VF.

X IPL K SETTLES THE TWO-NUMBER QUESTION docs/mcp_tape_manufacture.md
2.1 raises.  Printed p.2's IPL control word counts 0o560 = 368 words,
X BS END - X IPL BS, the record the tape holds.  X IPL K is
"1.0 + X BS END - X IPLBS" and comes out 000561.00 = 369, one more,
"SIZE OF BOOTSTRAP" including its own control word.  Both numbers are
right and this is the listing's own arithmetic saying which is which.

LINE 38, "X BUFER SYN,X IN END+ 2000.0", IS A REAL CHECK because
X IN END comes from the page that defines it -- printed p.98 line 36,
"X IN END SYN,$" at 005466.00, eighty-five pages away and still the
same assembly (printed p.15 line 5's "PUNID,11C11IPL" changes what is
punched into the cards, not the assembly).  0o5466 + 2000 words comes
out 011406.00, which is what the page prints, and the arithmetic also
settles that "2000.0" is DECIMAL: an octal reading would need the
difference to be 0o3720.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p13.strap").read())

SYMBOLS = {
    "XMSG27": "000526.00",
    "XMSG28": "000533.00",
    "XMSG29": "000540.00",
    "XSROOF": "000546.00",
    "XWSR":   "000547.00",
    "XWIND":  "000550.00",
    "XERRAD": "000551.00",
    # X IPL K is a SYN whose value is a WORD ADDRESS, and the listing
    # prints it in the LOCATION column exactly as it prints a label's:
    # 000561.00+.
    "XIPLK":  "000561.00",
    # Likewise X BUFER: a SYN row prints its resolved VALUE in the
    # LOCATION column, 011406.00+, on a page whose own counter is
    # running 000526 through 000551.
    "XBUFER": "011406.00",
}

ROWS = [
    ("000526.00", "375", "line 3   X MSG 27  -CONTROL CODE * CARRIAGE RETURN"),
    ("000526.10", "002", "line 4   X MSG 27  -RED$"),
    ("000532.70", "376", "line 7   X MSG 27  -CONTROL CODE *END OF MESSAGE"),
    ("000533.00", "375", "line 10  X MSG 28  -CONTROL CODE * CARRIAGE RETURN"),
    ("000533.10", "002", "line 11  X MSG 28  -RED$"),
    ("000537.40", "376", "line 14  X MSG 28  -CONTROL CODE *END OF MESSAGE"),
    ("000540.00", "375", "line 17  X MSG 29  -CONTROL CODE * CARRIAGE RETURN"),
    ("000540.10", "002", "line 18  X MSG 29  -RED$"),
    ("000545.40", "376", "line 21  X MSG 29  -CONTROL CODE *END OF MESSAGE"),
    ("000546.00", "000000.00+ 000 000000 000000",
     "line 26  X S ROOF  XW,0  -TEMP STORE FOR SIZE OF 7030"),
    # THE COUNT FIELD IS IN WORDS.  Line 35 writes 29 as a bare
    # integer and the listing prints 000035; line 36 writes 20 as
    # "20.0" and the listing prints 000024.  Before this page the
    # assembler shifted neither and line 36 came out 0002400.
    ("000547.00", "000000.00+ 000 000035 000550",
     "line 35  XW SR  XW,0.0,29,XW IND  -XW FOR CLEARING LR AND TW"),
    ("000550.00", "000622.00+ 000 000024 000000",
     "line 36  XW IND  XW,X IPLK+33.0,20.0  -XW FOR CLEARING NON "
     "MASKABLE INDIC"),
    ("000551.00", "000000.00+",
     "line 37  X ERR AD  VF,0  -LOCATION OF ERROR +1.0"),
]

# X EE EOP is a five-bit DATUM, not an address: the listing's LOCATION
# column reads 000000.00+ and its value +00000006.  A location check
# would be meaningless, so its VALUE is asserted here instead.
assert prog.symtab["XEEEOP"] == 0o6, prog.symtab["XEEEOP"]
print("PASS MCP p.13 X EE EOP  SYN(BU,5),(2)00110 -- value 6, "
      "listing +00000006  - EOF STATUS BITS")

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.13 "))
