#!/usr/bin/env python3
"""verify_mcp_bootstrap_p50.py -- the count table and the INTERNAL
DECODE TABLES, printed page 50 (../decks/mcp_bootstrap_p50.strap).
docs/MCP_Mar63_001-249.pdf PDF p.57, header "PAGE NUMBER 50".
AGENTS.md rule 3.

Thirty-one printed rows with binary output and six symbol locations.

>>> THREE OF PRINTED p.48's STAND-INS LAND HERE: L SYMU 002620.00,
L SYMC 002660.00, L NTPU 002700.00. <<<

They are the three tables p.48 lines 15-17 and 26-28 build refilling
index words over, and each one's SIZE is what puts the next where
p.48 said it would be -- so this page checks p.48's arithmetic as
much as its own.  L DISK, p.48's fourth stand-in at 002723.00, is
still forward.

>>> AND THE LISTING PRINTS A SYMBOL'S CLASSIFICATION. <<<

Lines 37 and 40 are both one-bit SYNs and their values go in
DIFFERENT COLUMNS:

    line 37  000000.61+                 L RLBIT  SYN(BU,1),0.49
    line 40  000000.00+   +00000077     L ZBIT   SYN(BU,1),63

A BIT ADDRESS goes in the LOCATION column (0o61 is 49); an INTEGER
goes in the INTEGER column (0o77 is 63) with the location left at
zero.  That is C22-6531 printed p.31's "its bit address or INTEGER
CLASSIFICATION" shown rather than stated -- the same distinction
printed p.48 forced strap_asm.py to learn one page earlier, when a
count SYNned to 80 was scaled as a bit address and came out as one.
The listing had been printing the answer all along, in a column this
project had no reason to read until the bug made one.

THE COUNT TABLE IS CHECKED BYTE BY BYTE, all thirty-one of them, at
their own addresses -- which also pins the two DD rows' lengths (16
values then 15) without either row printing a length.

TWO INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  Line 36's "(32)" -> "(31)" -- 2 FAILs HERE, L SYMC and L NTPU,
  and nothing on the count table moves: the three tables are a chain
  and this is the link.  AND THE BETTER HALF IS IN THE MERGE, which
  is where the cross-page claim lives: mcp_image dies with "LNTPU:
  printed p.48 SYNs bit 94208, printed p.50 places it at bit 94144".
  One page's reservation size against another page's stand-in, which
  no single verifier can see.
  Line 17's list shortened by one value (31 dropped) -- 1 FAIL, the
  last byte's row, and NO symbol moves: the CNOP on line 35 rounds
  the eight-bit shortfall away before L SYMU, which is the printed
  p.44 shape again and is why the table is checked byte by byte
  rather than by what follows it.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p50.strap").read())

SYMBOLS = {
    "LCT":    "002614.00",
    # >>> printed p.48's THREE STAND-INS.
    "LSYMU":  "002620.00",
    "LSYMC":  "002660.00",
    "LNTPU":  "002700.00",
}

ROWS = [
    ("002614.00", "001", "line 1  L CT byte 1", 8),
    ("002614.10", "002", "line 2  L CT byte 2", 8),
    ("002614.20", "003", "line 3  L CT byte 3", 8),
    ("002614.30", "004", "line 4  L CT byte 4", 8),
    ("002614.40", "005", "line 5  L CT byte 5", 8),
    ("002614.50", "006", "line 6  L CT byte 6", 8),
    ("002614.60", "007", "line 7  L CT byte 7", 8),
    ("002614.70", "010", "line 8  L CT byte 8", 8),
    ("002615.00", "011", "line 9  L CT byte 9", 8),
    ("002615.10", "012", "line 10 L CT byte 10", 8),
    ("002615.20", "013", "line 11 L CT byte 11", 8),
    ("002615.30", "014", "line 12 L CT byte 12", 8),
    ("002615.40", "015", "line 13 L CT byte 13", 8),
    ("002615.50", "016", "line 14 L CT byte 14", 8),
    ("002615.60", "017", "line 15 L CT byte 15", 8),
    ("002615.70", "020", "line 16 L CT byte 16", 8),
    ("002616.00", "021", "line 17 L CT byte 17", 8),
    ("002616.10", "022", "line 18 L CT byte 18", 8),
    ("002616.20", "023", "line 19 L CT byte 19", 8),
    ("002616.30", "024", "line 20 L CT byte 20", 8),
    ("002616.40", "025", "line 21 L CT byte 21", 8),
    ("002616.50", "026", "line 22 L CT byte 22", 8),
    ("002616.60", "027", "line 23 L CT byte 23", 8),
    ("002616.70", "030", "line 24 L CT byte 24", 8),
    ("002617.00", "031", "line 25 L CT byte 25", 8),
    ("002617.10", "032", "line 26 L CT byte 26", 8),
    ("002617.20", "033", "line 27 L CT byte 27", 8),
    ("002617.30", "034", "line 28 L CT byte 28", 8),
    ("002617.40", "035", "line 29 L CT byte 29", 8),
    ("002617.50", "036", "line 30 L CT byte 30", 8),
    ("002617.60", "037", "line 31 L CT byte 31", 8),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.50 ")

# ---------------------------------------------------------------------
# THE TWO ONE-BIT SYNs, whose VALUES the listing prints in different
# columns -- a bit address in the location column, an integer in the
# integer column.  Neither is an address in storage, so neither can
# go in SYMBOLS.
# ---------------------------------------------------------------------
for name, want, what in (("LRLBIT", 49, "a BIT ADDRESS, 0.49, printed as location 000000.61"),
                         ("LZBIT", 63, "an INTEGER, 63, printed as +00000077")):
    got = prog.symtab.get(name)
    if got == want:
        print(f"PASS MCP p.50 {name} = {got}, {what}")
    else:
        print(f"FAIL MCP p.50 {name} = {got!r}, want {want} ({what})")
        fails += 1

finish(fails)
