#!/usr/bin/env python3
"""verify_mcp_bootstrap_p36.py -- MCP INITIALIZATION, printed page 36:
"SYSTEM COMMAND OPS FOR STARTING MODE", the console messages, the
bounds words, the IPL message block and the operating-mode card
codes (../decks/mcp_bootstrap_p36.strap).
docs/MCP_Mar63_001-249.pdf PDF p.43, header "PAGE NUMBER 36".
AGENTS.md rule 3.

Twenty-six printed rows with binary output and twenty symbol
locations -- every row on the page.

>>> TWELVE ADDRESSES EARLIER PAGES ALREADY COMPILED LAND HERE, and
that is what this page checks.  Each was decoded out of an
instruction on a page transcribed BEFORE this one was opened, and
this page is where the program defines it:

  X BYPAS  001757.00   printed p.33 line 47
  X ON LIN 001761.00   printed p.33 line 21
  X OF LIN 001763.00   printed p.33 line 45
  X RDR MG 001765.00   printed p.32 line 46
  X RDR CR 001771.50   printed p.32 lines 42-43
  X MSG    001773.00   printed p.27 line 23
  X MSG CR 001774.00   printed p.27 line 24
  X BOUND  001777.00   printed p.33 line 51
  X MSG BK 002000.00   printed pp.27, 32 and 34
  X ON OV  002144.00   printed p.31 line 12
  X OF OV  002145.00   printed p.31 line 14
  X BYPS   002146.00   printed p.31 line 16

and line 34's "S LR BU SYN, S BA PP" gives 002155.00, which printed
pp.28 and 30 had already compiled.  NONE of the thirteen is read off
this page; they are measurements of nine earlier transcriptions. <<<

>>> AND THEY ARE MEASURED BY WHAT IS BETWEEN THEM.  Each address
here is where it is because of how much storage the datum before it
takes -- a thirty-five character IQS message, a seven character one
in a different entry mode, a hundred-word reservation, a one-bit
flag.  Nothing in this deck states an address except the SLC at the
top; every other one is counted. <<<

THE ASSEMBLER GAINED A BARE "VF".  Line 31 is "Y NLST  VF" with no
operand at all, printing 000000.00+.  C22-6531 printed p.7: "A
MAJOR FIELD MAY BE NULL... a null field is always compiled as a
zero."  C28-6129 printed p.4: "missing fields are compiled by
STRAP-II as if they contained zeros AND WERE ADDED AT THE END OF THE
STATEMENT" -- which is the sentence that covers an operand left off
entirely rather than written as a bare comma.

THREE ENTRY MODES ON ONE PAGE: (A*) at byte size 6 for the system
command strings, (IQS*) at 8 for the reader-channel message, and
(IQSX) for the message prefix -- terminated by "X" because the datum
"MCPIPL*" CONTAINS an asterisk.  C28-6129 printed p.16 makes the
terminator the programmer's choice, and this page is why.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p36.strap").read())

SYMBOLS = {
    "XBYPAS": "001757.00",
    "XONLIN": "001761.00",
    "XOFLIN": "001763.00",
    "XRDRMG": "001765.00",
    "XRDRCR": "001771.50",
    "XMSG":   "001773.00",
    "XMSGCR": "001774.00",
    "YTBIT":  "001775.00",
    "YNLST":  "001775.40",
    "YNOPUN": "001775.40",
    "SIOLOC": "000000.00",
    "SLRBU":  "002155.00",
    "XARCK":  "001776.00",
    "XBOUND": "001777.00",
    # The reservation's own extent is the check on the DR: a hundred
    # words from 002000.00 is 002144.00, and that is where the
    # listing puts X ON OV.
    "XMSGBK": "002000.00",
    "XONOV":  "002144.00",
    "XOFOV":  "002145.00",
    "XBYPS":  "002146.00",
    "XNOR":   "002146.30",
    "XABN":   "002146.74",
}

ROWS = [
    ("001756.40", "000000.30 00", "line 4   CNOP"),
    # Lines 5, 7, 9 and 14 and 24 are alphabetic data and the listing
    # prints no binary for them.  What they occupy is checked by the
    # addresses of everything after them.
    ("001760.40", "000000.30 00", "line 6   CNOP"),
    ("001762.40", "000000.30 00", "line 8   CNOP"),
    ("001764.40", "000000.30 00", "line 11  CNOP"),
    ("001765.00", "375",
     "line 12  X RDR MG  DD(BU,8),(2)1111 1101  -CARRIAGE RETURN", 8),
    ("001765.10", "002", "line 13  DD(BU,8),(2)00000010  -RED $", 8),
    ("001771.50", "140",
     "line 16  X RDR CR  DD(BU,8,8),(2)01100000,...  -DUMMY IQS SLOTS, CR", 8),
    ("001771.60", "140", "line 17  (2)01100000", 8),
    ("001771.70", "375", "line 18  (2)11111101", 8),
    ("001772.00", "376", "line 19  (2)11111110", 8),
    ("001772.40", "000000.30 00", "line 22  CNOP"),
    ("001773.00", "002", "line 23  X MSG  DD(BU,8),(2)00000010  -RED $", 8),
    ("001774.00", "0000000000000000176776",
     "line 26  X MSG CR  DD(BU,64,8),(2)1111110111111110  -MSL CR AND END RETURN"),
    ("001775.00", "0",
     "line 30  YTBIT  DD(BU,1),0  -FLAG USED BY THE UNCODE ROUTINE", 1),
    ("001775.40", "000000.00+",
     "line 31  Y NLST  VF  - NOT USED IN UNCODE FOR IPL  (a bare VF)"),
    ("001776.00", "000000.00+",
     "line 36  X ARC K  VF,0.0  -ACCUMULATED PROSA ARCS"),
    ("001776.40", "000000.30 00", "line 37  CNOP"),
    ("001777.00", "000041.00+", "line 39  X BOUND  VF,33.0"),
    ("001777.40", "000040.00+",
     "line 40  VF,32.0  -BOUNDS AND BOUNDARY CONTROL BIT"),
    ("002144.00", "20102020",
     "line 45  X ON OV  DD(BU,24),(8)20102020  -ON IN CARD CODE", 24),
    ("002144.40", "000000.30 00", "line 46  CNOP"),
    ("002145.00", "20104010",
     "line 47  X OF OV  DD(BU,24),(8)20104010  -OF IN CARD CODE", 24),
    ("002145.40", "000000.30 00", "line 48  CNOP"),
    ("002146.00", "42001002",
     "line 49  X BYPS  DD(BU,24),(8)42001002  -BY IN CARD CODE", 24),
    ("002146.30", "202020102001",
     "line 50  X NOR  DD(BU,36),(8)202020102001  - UPL MODE * NORMAL", 36),
    ("002146.74", "440042002020",
     "line 51  X ABN  DD(BU,36),(8)440042002020  - IPL MODE * ABNORMAL", 36),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.36 ")

# ---------------------------------------------------------------
# THE PAGE EXERCISES ONE OF THE TWO SHAPES A NULL VALUE FIELD HAS,
# and the manuals describe the other.  "VF" with nothing after it
# parses to NO fields; "VF," -- C22-6531 printed p.7's "nothing but
# the comma denoting the field termination is written" -- parses to
# ONE EMPTY field.  p.36 writes the first.  Without this check the
# second arm of the condition is dead code that no row reaches, and
# an injection deleting it would survive.
# ---------------------------------------------------------------
from listing_oracle import render  # noqa: E402

BARE = [
    ("V1", "VF",  "no operand at all -- printed p.36 line 31's shape"),
    ("V2", "VF,", "a bare comma -- C22-6531 printed p.7's shape"),
]
for name, stmt, note in BARE:
    p2 = assemble("        SLC, (8)1000.0\nH       %s\n        END, H\n" % stmt)
    got = render(p2, "001000.00", "000000.00+")
    ok = got == "000000.00+" and p2.symtab["H"] == 0o1000 * 64
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} MCP p.36 {name}: {stmt!r}, {note}: "
          f"compiled {got!r} at bit {p2.symtab['H']}")

finish(fails)
