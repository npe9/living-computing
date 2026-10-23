#!/usr/bin/env python3
"""verify_mcp_bootstrap_p41.py -- RETURNS, MASKS, TEMPORARY STORAGE
FOR UNCODE, printed page 41 (../decks/mcp_bootstrap_p41.strap).
docs/MCP_Mar63_001-249.pdf PDF p.48, header "PAGE NUMBER 41".
AGENTS.md rule 3.

Eleven printed rows with binary output and sixteen symbol locations.

>>> FOURTEEN PREDICTIONS LAND ON ONE PAGE. <<<

printed pp.38, 39 and 40 between them SYN'd forty-three symbols they
did not define, every address read off their own binary output.
THIS PAGE DEFINES FOURTEEN OF THEM, every one at the address those
pages said:

  Y NORR   002313.40   p.39 lines 5/11/32/43, p.40 lines 13/29
  Y IDX12  002321.00   p.40 line 14
  Y UCX12  002322.00   p.39 line 44
  Y UX SAV 002324.00   p.38 line 4; p.40 lines 24/28/33/38
  Y UCBF1  002327.00   p.38 lines 15 and 18
  Y UCBF2  002337.00   p.38 line 20, p.39 five rows, p.40 line 36
  Y UTOE   002334.64   p.40 line 20
  Y GOMK   002354.00   p.39 line 10
  Y TYPMK  002355.00   p.38 line 26
  Y REL MK 002360.00   p.38 line 39
  Y COMMK  002362.00   p.39 line 12
  Y CNGMK  002363.00   p.39 line 14
  Y BLWD4  002364.00   p.40 line 26
  Y UPDAT  002365.00   p.39 line 16

Y UTOE IS THE ONE THAT COULD NOT HAVE BEEN GUESSED.  p.40 line 20 is
"LF(BU,60,6),Y UTOE", whose VFL left half prints 002334.64 -- a BIT
address, word 0o2334 bit 0o64 -- and line 37 here is
"Y UTOE  SYN,Y UCBF1+.372", a DECIMAL bit offset from a symbol three
rows above.  002327.00 plus 372 bits is 002334.64 exactly.  Two
pages, two notations, one bit.

AND IT USES Y TBIT, which printed p.36 line 30 defines at 001775.00
-- line 5's "CM0000(BU,1),Y TBIT" reads it five pages later.

THE THREE RESERVATIONS ARE CHECKED BY WHAT FOLLOWS THEM, not by
their printed size.  printed p.24's verifier established that a
DR/DRZ row prints its SIZE rather than a word, so it is not a
storage row and is not row-checked.  Here the sizes are pinned
harder than the print would pin them, because three symbols land on
the far side of them:

  Y UX SAV  DRZ (3)   002324.00 + 3  = 002327.00 = Y UCBF1
  Y UCBF1   DRZ (8)   002327.00 + 8  = 002337.00 = Y UCBF2
  Y UCBF2   DRZ (13)  002337.00 + 13 = 002354.00 = Y GOMK

and all three of those symbols are themselves predictions made by
earlier pages.  A wrong reservation size moves a prediction.

THE MASKS ARE EIGHT CHARACTERS EACH AND THE COLUMN SAYS SO.  Lines
18-36 are ten "(AX)DD(BU,48,6)" masks and the listing prints NO
binary for any of them, as it prints none for printed p.37's two
(AX) rows or pp.9-12's (IQS*) messages -- so no character code is
checked or can be.  What is checked is the counting: 48 bits at a
byte size of 6 is EIGHT characters, and every mask is blank-padded
to exactly eight.  The proof is column alignment at 600 dpi, every
end-of-statement "X" in one column, and LINE 32 IS THE CONTROL:
"COMPILGOX" puts its X one position earlier than all the others,
because "COMPILGO" is eight characters and leaves no room for a
blank.  A datum of any other length would have moved its X.

A FIFTH XW OPERAND IS THE FLAG FIELD.  Line 14's
"XW,Y UCBF2+2.0,6,0,7" prints "002341.00+ 111 000006 000000" --
value, FLAGS 111, count 6, refill 0 -- so the fifth operand is the
three flag bits at 25-27 (Reference Manual Figure 35, the same
positions a control word's chain/multiple/skip occupy), and lines 12
and 13 leave them zero by omission.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p41.strap").read())

SYMBOLS = {
    # THE FOURTEEN PREDICTIONS, in the order the page defines them.
    "YNORR":  "002313.40",
    "YIDX12": "002321.00",
    "YUCX12": "002322.00",
    "YUXSAV": "002324.00",
    "YUCBF1": "002327.00",
    "YUCBF2": "002337.00",
    "YGOMK":  "002354.00",
    "YTYPMK": "002355.00",
    "YRELMK": "002360.00",
    "YCOMMK": "002362.00",
    "YCNGMK": "002363.00",
    "YBLWD4": "002364.00",
    "YUPDAT": "002365.00",
    # A BIT address, and the sharpest of the fourteen: printed p.40
    # read it off a VFL left half as 002334.64, and line 37 computes
    # it as Y UCBF1 plus 372 DECIMAL bits.
    "YUTOE":  "002334.64",
    # The two this page uses.
    "YTBIT":  "001775.00",
    "YUSB8C": "002200.00",
}

ROWS = [
    ("002313.40", "000000.31 1E",
     "line 4   Y NORR  SX,$12,0.0($14)  -PUT INFORMATION IN CALLING"),
    # READS Y TBIT, which printed p.36 line 30 defines at 001775.00.
    ("002314.00", "001775.00 80  001000.00 F0", "line 5   CM0000(BU,1),Y TBIT"),
    ("002315.00", "002324.00 80  000033.06 A0", "line 6   TI,3,Y UX SAV,$11  -SEQUENCE"),
    ("002316.00", "000002.37 BE", "line 7   LVE,$15,2.0($14)"),
    ("002316.40", "002200.36 50", "line 8   LC,$15,Y USB8C  -TRANSMIT BROKEN OUT"),
    ("002317.00", "002320.71 42", "line 9   BXVZ,$+1.32  -CARD TO REQUESTED AREA"),
    # A direct-count TRANSMIT whose count register is written without
    # its "$", printed p.4 line 28's convention.
    ("002317.40", "002337.00 80  000000.36 2F", "line 10  T,$15,Y UCBF2,0.0($15)"),
    ("002320.40", "000003.10 0E", "line 11  B,3.0($14)  -RETURN"),
    # THE THREE INDEX WORDS.  Line 12's VALUE is Y UTOE, the bit
    # address printed p.40 predicted; line 13's REFILL is "$+1.0" and
    # prints 002323, one word past the 002322 the row occupies.
    ("002321.00", "002334.64+ 000 000012 000000", "line 12  Y IDX12  XW,Y UTOE,10,0"),
    ("002322.00", "002340.00+ 000 000006 002323",
     "line 13  Y UCX12  XW,Y UCBF2+1.0,6,$+1.0"),
    # THE FIFTH OPERAND IS THE FLAG FIELD: 7 prints as 111.
    ("002323.00", "002341.00+ 111 000006 000000", "line 14  XW,Y UCBF2+2.0,6,0,7"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.41 ")
finish(fails)
