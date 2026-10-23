#!/usr/bin/env python3
"""verify_mcp_bootstrap_p42.py -- BCD TO IQS CONVERSION ROUTINE,
printed page 42 (../decks/mcp_bootstrap_p42.strap).
docs/MCP_Mar63_001-249.pdf PDF p.49, header "PAGE NUMBER 42".
AGENTS.md rule 3.

Twenty-five printed rows with binary output and nine symbol
locations.  A fourth source deck, card sequence 15000001.

>>> ITS LAST DATUM ENDS EXACTLY AT S CA6. <<<

printed p.38 line 12 is "BD,S CA6" and its binary puts S CA6 at
002422.00 -- a prediction made four pages before anything near that
address was opened, and the address the boot run's PC trail has been
stopping at ever since p.38 joined the image.

THIS PAGE'S LAST ROW IS 21 CHARACTERS OF IQS DATA STARTING AT
002417.30, AND 21 TIMES 8 BITS LANDS ON 002422.00 TO THE BIT.  The
assembler's highest compiled word is 0o2421, the one before it.

That checks the whole character-count chain at once.  Lines 32-38
print NO BINARY except the two radix-2 bytes, so no character code is
checked or can be -- but every string's LENGTH is pinned by the
address of the row after it, and the last one is pinned by a symbol a
different deck predicted:

  line 32  002412.00  "/1234567890="      12 chars -> 002413.40
  line 33  002413.40  one byte, prints 052        -> 002413.50
  line 34  002413.50  "/// /STUVWXYZ"     13 chars -> 002415.20
  line 35  002415.20  one byte, prints 165        -> 002415.30
  line 36  002415.30  ",(///-JKLMNOPQR"   15 chars -> 002417.20
  line 37  002417.20  "/"                  1 char  -> 002417.30
  line 38  002417.30  "$*///+ABCDEFGHI/.)///"  21  -> 002422.00

LINE 38'S ENTRY MODE IS "(IQSY)", terminated by Y rather than the "*"
the others use, BECAUSE THE DATUM CONTAINS AN ASTERISK -- the same
reason printed p.36 writes "(IQSX)".  C28-6129 printed p.16 makes the
terminator the programmer's choice, and these two pages are why.

THE PAGE IS SELF-CONTAINED: every symbol it mentions it also defines,
so it makes no predictions and needs no stand-in SYNs.  First page
since printed p.37 for which that is true.

LINE 24 IS listing_typography.md 13 AT ITS THICKEST.  At 200 dpi the
row reads "C00CC1.5C  CF"; at 900 dpi every one of those glyphs is a
digit zero and the row is "000001.50  0F".  The decode settles it
without the re-render: printed p.40 lines 37 and 41 are the same
instruction shape, "B,2.32($14)", and print "000002.50 0E" -- a
branch through an index gives 0 in the high nibble and the index in
the low one, so "CF" is not an operation this machine has.

THE DECK BOUNDARY IS "SLC,$" AND IT ROUNDS.  Line 4 is "SLC,$" at
002365.60 -- printed p.41's last mask is 48 bits at 002365.00 and
ends there -- and line 5 is at 002366.00, so setting the location
counter to "$" rounds up to the next word.  This deck states
002366.00 outright, as every page deck here does.  The sixteen-bit
gap is INSIDE word 002365, which p.41 compiles, so
`mcp_ipl_image()`'s contiguity check sees no hole: it counts words,
and that word is present.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p42.strap").read())

SYMBOLS = {
    "SA8IQS": "002366.00",
    "SA6IQS": "002367.40",
    "GKRUH":  "002374.00",
    "GSKOK":  "002376.00",
    "GPRYC":  "002401.00",
    "GOSMI":  "002403.00",
    "GSEST":  "002405.00",
    "GULOZX": "002407.00",
    # THE TABLE'S BASE.  Everything after it is character data the
    # listing prints no binary for, so this address plus the seven
    # string lengths is the only thing holding 002422.00 in place.
    "GRADA":  "002412.00",
}

ROWS = [
    ("002366.00", "002403.00 80  002374.04 A0",
     "line 5   S A8IQS  TI,2,G OSMI,G KRUH  -SET LOOP FOR 8BIT BCD"),
    ("002367.00", "002370.50 00", "line 6   B,$+1.32"),
    ("002367.40", "002405.00 80  002374.04 A0",
     "line 7   S A6IQS  TI,2,G SEST,G KRUH  -SET LOOP FOR 6BIT BCD"),
    ("002370.40", "002407.33 10",
     "line 8   SX,$13,G ULOZX  -SAVE ORIGINAL INDEX REGISTERS"),
    ("002371.00", "002410.35 10", "line 9   SX,$14,G ULOZX+1.0"),
    ("002371.40", "002411.37 10", "line 10  SX,$15,G ULOZX+2.0"),
    ("002372.00", "000000.34 3F", "line 11  LV,$14,0.0($15)  -PUT *IN* IN VF OF $14"),
    ("002372.40", "000000.74 5F", "line 12  LC,$14,.32($15)  -PUT *N* IN CF OF $14"),
    ("002373.00", "002401.30 42", "line 13  BXCZ,G PRYC"),
    ("002373.40", "000001.32 3F", "line 14  LV,$13,1.0($15)  -PUT *OUT* IN VF OF $13"),
    # Line 16's DRZ prints its SIZE and not a word, so it is checked
    # by G SKOK landing two words later -- 002374.00 + 2 = 002376.00.
    ("002376.00", "000011.36 30",
     "line 17  G SKOK  LV,$15,$R  -PUT BIT ADDRESS*8 IN $15"),
    ("002376.40", "002412.00 8F  010000.20 50",
     "line 18  L(BU,8),G RADA($15)  -LOAD 8BIT CODE IQS CHARACTER"),
    ("002377.40", "000000.10 8D  110000.20 D0",
     "line 19  ST(V+I)(BU,8),.8($13)  -STORE SAME"),
    ("002400.40", "002374.34 48", "line 20  CB,$14,G KRUH"),
    ("002401.00", "002407.32 10",
     "line 21  G PRYC  LX,$13,G ULOZX  -RESTORE INDEX REGISTERS"),
    ("002401.40", "002410.34 10", "line 22  LX,$14,G ULOZX+1.0"),
    ("002402.00", "002411.36 10", "line 23  LX,$15,G ULOZX+2.0"),
    # THE ROW THE SCAN PRINTS AS "C00CC1.5C  CF".
    ("002402.40", "000001.50 0F", "line 24  B,1.32($15)"),
    ("002403.00", "000000.10 8E  110025.60 50",
     "line 26  G OSMI  L(V+I)(BU,8),.8($14),43  -FOR 8BIT BCD"),
    ("002404.00", "000000.00 80  002030.40 70", "line 27  C0000(BU,2),0.0,49"),
    ("002405.00", "000000.06 8E  106025.60 50",
     "line 28  G SEST  L(V+I)(BU,6),.6($14),43  -FOR 6BIT BCD"),
    ("002406.00", "002376.10 00", "line 29  B,G SKOK"),
    ("002406.40", "000000.30 00", "line 30  NOP"),
    # Line 31's DRZ (3) is checked by G RADA landing three words
    # later: 002407.00 + 3 = 002412.00.
    #
    # THE TWO RADIX-2 BYTES, which are the only binary the table
    # prints.  They also verify the deck's one substitution: the
    # listing writes the radix as a statement prefix,
    # "(2)DD(BU,8,8),00101010", and the deck writes it on the operand,
    # "DD(BU,8,8), (2)00101010".  0o52 is 00101010 and 0o165 is
    # 01110101, so the substitution is checked and not asserted.
    ("002413.40", "052", "line 33  DD(BU,8,8),(2)00101010  -QUOTATION", 8),
    ("002415.20", "165", "line 35  DD(BU,8,8),(2)01110101  -COLON", 8),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.42 ")
finish(fails)
