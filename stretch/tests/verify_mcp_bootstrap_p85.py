#!/usr/bin/env python3
"""printed p.85 against its own listing.

SYN CARDS FOR FILE AREA TABLE, THE FORMAT OF THE REEL POOL, and THE
TYPE SCAN TABLES.  docs/MCP_Mar63_001-249.pdf PDF p.92.

>>> THE TYPE SCAN TABLE IS THE PRINTED SOURCE OF MCP'S TYPE CODES. <<<
Lines 32-47 pair each equipment name with its code -- CONSOLE 2,
DISK 1, READER 3, PUNCH 4, PRINTER 5, IQS 6, TRACK (2)10001, TAPE 8 --
and that is exactly the row order of the configuration table checked by
gen_mcp_boot_tb.py's mcp_conf_table_word0/1/2, and the source of the
TTYPE=3 in the READER request that ASSIGN satisfies in
run_mcp_assign_test.sh.  Those codes were read out of MCP's behaviour
before this page was transcribed; here they are in print.

TWO KINDS OF SYN PRINT DIFFERENTLY, and only one is a location:

  * "SYN(BU,7),0.12" is an ADDRESS and prints 000000.14 in the
    LOCATION column -- 0o14 = 12 bits.
  * "SYN(BU,6),7" is a VALUE: the LOCATION column prints 000000.00 and
    the number appears in the BINARY column as +00000007.

So a bare-integer SYN cannot be checked against the location column.
Its value is asserted directly below.  The same shape appears on
printed p.84 as "T UNLGN SYN(BU,6),9", printing +00000011 = 9.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p85.strap").read())

# The bare-integer SYNs: value, not address.  See the note above.
assert prog.symtab["TFLLGN"] == 7, prog.symtab["TFLLGN"]

SYMBOLS = {
    "TIODRN": "000000.00",
    "TTOELO": "000002.00",
    "TDENMD": "000002.33",
    "TREELD": "000002.35",
    "TFMCDE": "000002.60",
    "TORARC": "000005.06",
    "TMXARC": "000005.46",
    "TCUARC": "000006.06",
    "TRENTY": "000000.31",
    "TREPR":  "000000.32",
    "TRELB":  "000000.33",
    "TRENME": "000000.42",
    "TSCIX1": "004743.00",
    "TSCBK1": "004744.00",
    "TSCAN1": "004744.31",
}

ROWS = [
    ("004743.00", "004744.31+ 000 000010 000000",
     "line 29  T SCIX1  XW,TSCAN1,8,0"),
    ("004744.00", "000000.05-",
     "line 30  T SCBK1  VF,-5"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.85 "))
