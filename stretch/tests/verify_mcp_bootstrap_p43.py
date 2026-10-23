#!/usr/bin/env python3
"""verify_mcp_bootstrap_p43.py -- HOLLERITH TO BCD CONVERSION,
printed page 43 (../decks/mcp_bootstrap_p43.strap).
docs/MCP_Mar63_001-249.pdf PDF p.50, header "PAGE NUMBER 43".
AGENTS.md rule 3.

Forty-three printed rows with binary output and fifteen symbol
locations.

>>> LINE 5 IS S CA6, AT 002422.00. <<<

printed p.38 line 12 is "BD,S CA6" and its binary put S CA6 at
002422.00 -- a prediction made five pages before this one was
opened.  printed p.42's last datum ends at 002422.00 to the bit.
And line 5 here is "S CA6  Z,$R" at 002422.00.

THIS IS THE ROUTINE THE BOOT RUN HAS BEEN STOPPING AT: the PC trail
has read half-word 2596 since p.38 joined the image, and 2596 is
this address.

>>> "TAIL" APPEARS, AND docs/NEXT.md 5x PREDICTED IT WOULD BE
INERT. <<<

Line 9 is "TAIL,A".  C28-6129 printed p.37 makes TAIL name mangling
for cross-program link safety, not lexical scoping -- definitions
and references are mangled alike -- so a single-program assembly is
bit-identical with or without it.  5x wrote that analysis down on
2026-10-17, before any page using TAIL had been opened.  THIS PAGE
IS THE FIRST TEST OF IT and it passes: the deck writes "TAIL,A" as
printed, strap_asm.py's LISTING_CONTROL discards it, and every row
below matches the listing.

AND LINE 6 IS THE CASE 5x SAID TO WATCH FOR -- a reference from
OUTSIDE the tail block to a symbol defined INSIDE it:

    002422.40   002424.10 00    $B,Q GO$A

C28-6129 printed p.37: "When tailing is used, the last two
characters of the basic symbol are used for a special character that
indicates tailing is being used and a character to represent the
tail symbol."  So "Q GO$A" IS the mangled name, spelled out by hand
because from outside the block the plain name would not resolve.
With no mangling at all the reference and the definition match for
the same reason they would have matched mangled, and the compiled
row says so.

THE "$" IN FRONT OF THE "B" IS NOT EXPLAINED, and is recorded rather
than guessed at.  p.37 accounts for the "$A" and says nothing about
a "$" on an OPERATION.  It is in the statement column and not the
name column -- checked at 600 dpi against "S CA8" and "LI(BU,24)" on
the row below.  The compiled row is a plain unconditional branch:
line 50's "B,Q CHK" prints 002454.10 00 and line 34's "B,Q CK"
prints 002447.50 00, the same shape with no "$".

A SECOND SWAP.  Line 53 is "Q FIN  SWAPI,6,Q SAV,$1  -RESTORE
INDEXES" -- six words, where printed p.40's two SWAPs were three --
and line 10 is its matched "TI,6,$1,Q SAV  -SAVE THE INDICES", the
same six words the other way, A0 against E0.  So the instruction
p.40 gave a documented caller has a second caller here, in the same
save-and-restore shape.

TWO ROWS ARE listing_typography.md 13 AGAIN, and both are the shape
printed p.42 line 24 already settled: lines 48 and 54 are branches
through an index, printed "C1" and "CF", and both high glyphs are
digit zeros -- 01 and 0F.  THE DECODE SETTLES IT and the page
carries its own control: printed p.40 lines 37 and 41 print
"000002.50 0E" for the identical shape with a round zero, and here
line 53 prints "002472.00 80" one row above line 54's "0CCCC1.5C",
the same digit in two renderings on adjacent rows.

$LZC IS NOT A STAND-IN BUT A REGISTER the assembler already had:
strap/opcodes.py puts Left Zeros Count at word 7, bits 17-23, and
lines 20 and 28 print 000007.21 -- word 7, bit 0o21, which is 17.
The table and the listing agree with nothing added.

AND "Q" IS A ONE-CHARACTER SYMBOL (line 47), which C22-6531 printed
p.10 allows ("six or fewer alphabetic and numeric characters") and
which is the shortest name this project has transcribed.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p43.strap").read())

SYMBOLS = {
    # THE ONE THE WHOLE PAGE IS FOR.
    "SCA6":  "002422.00",
    "SCA8":  "002423.00",
    "QGO":   "002424.00",
    "QP":    "002427.40",
    "QNO":   "002442.00",
    "QNOZ":  "002444.40",
    "QER":   "002446.40",
    "QCK":   "002447.40",
    "QST":   "002451.40",
    "QCHK":  "002454.00",
    "QFIN":  "002454.40",
    # The four it predicts, each read off this page's own binary.
    "QSAV":  "002472.00",
    "QFLD":  "002456.00",
    "Q":     "002465.00",
    "QTB":   "002500.00",
}

ROWS = [
    ("002422.00", "000011.22 00", "line 5   S CA6  Z,$R  -SET UP FOR A-6 CONVERSION"),
    # THE TAILED REFERENCE, written "$B,Q GO$A" in the listing.
    ("002422.40", "002424.10 00", "line 6   B,Q GO"),
    ("002423.00", "000001.40 80  430024.20 50",
     "line 8   S CA8  LI(BU,24),1.32,40  -SETUP FOR A-8 TYPE CONVERSION"),
    # "TAIL,A" is line 9 and compiles nothing.
    ("002424.00", "000021.00 80  002472.14 A0",
     "line 10  Q GO  TI,6,$1,Q SAV  -SAVE THE INDICES"),
    ("002425.00", "000000.11 BF", "line 11  LVE,$4,0($15)"),
    ("002425.40", "000011.02 30", "line 12  LV,$1,$R"),
    ("002426.00", "000000.50 5F", "line 13  LC,$4,.32($15)"),
    ("002426.40", "002454.70 42", "line 14  BXCZ,Q FIN"),
    ("002427.00", "000001.12 3F", "line 15  LV,$5,1.0($15)"),
    ("002427.40", "000000.03 84  103000.07 70",
     "line 19  Q P  CT0011(V+I)(BU,3),.3($4)"),
    # $LZC, Left Zeros Count: word 7 bit 0o21 = 17, which is what
    # strap/opcodes.py already had.
    ("002430.40", "000007.21 80  007026.60 50", "line 20  L(BU,7),$LZC,45"),
    ("002431.40", "000011.04 30", "line 21  LV,$2,$R"),
    ("002432.00", "000007.44 50", "line 22  LC,$2,7.32"),
    ("002432.40", "000000.11 84  111000.06 70", "line 23  LF(V+I)(BU,9),.9($4)"),
    ("002433.40", "000000.05 00", "line 24  C+I,$2,0"),
    ("002434.00", "002446.70 40", "line 25  BZXCZ,Q ER  -YES"),
    ("002434.40", "002500.04 32", "line 26  LV,$2,Q TB($2)"),
    ("002435.00", "000007.46 50", "line 27  LC,$3,7.32"),
    ("002435.40", "000007.21 80  007026.46 70", "line 28  LF(BU,7),$LZC,45"),
    ("002436.40", "000011.06 30", "line 29  LV,$3,$R"),
    ("002437.00", "002447.70 42", "line 30  BXCZ,Q CK  -IF NO TRIPLE OR MORE PUNCHES"),
    ("002437.40", "102000.00 80  411000.23 10",
     "line 31  KFI(BU,9),(2)001000010  -CHECK FOR AN 8-3 COMBO"),
    ("002440.40", "002442.36 C0", "line 32  BZAE,Q NO  -NO"),
    ("002441.00", "000005.07 01", "line 33  LVI,$3,5.0"),
    ("002441.40", "002447.50 00", "line 34  B,Q CK"),
    ("002442.00", "042000.00 80  411000.23 10",
     "line 36  Q NO  KFI(BU,9),(2)000100010  -CHECK FOR AN 8-4 COMBO"),
    ("002443.00", "002444.76 C0", "line 37  BZAE,Q NOZ  -NO"),
    ("002443.40", "000005.47 01", "line 38  LVI,$3,5.32"),
    ("002444.00", "002447.50 00", "line 39  B,Q CK"),
    ("002444.40", "202000.00 80  411000.23 10",
     "line 41  Q NOZ  KFI(BU,9),(2)010000010  -CHECK FOR AN 8-I COMBO"),
    ("002445.40", "000006.07 01", "line 42  LVI,$3,6.0"),
    ("002446.00", "002447.76 C2", "line 43  BAE,Q CK  -OK MUST BE A COLON"),
    ("002446.40", "000006.07 01", "line 44  Q ER  LVI,$3,6.0"),
    ("002447.00", "000000.05 01", "line 45  LVI,$2,0"),
    ("002447.40", "002456.15 B3", "line 46  Q CK  LVE,$6,Q FLD($3)"),
    # THE ONE-CHARACTER SYMBOL.
    ("002450.00", "002465.00 86  006600.06 70", "line 47  LF(BU,6,6),Q($6)"),
    # listing_typography.md 13: the listing prints "C1".
    ("002451.00", "002451.50 01", "line 48  B,Q ST($1)"),
    ("002451.40", "000000.06 85  106600.20 D0", "line 49  Q ST  ST(V+I)(BU,6,6),.6($5)"),
    ("002452.40", "002454.10 00", "line 50  B,Q CHK"),
    ("002453.00", "000000.10 85  110000.20 D0", "line 51  ST(V+I)(BU,8,8),.8($5)"),
    ("002454.00", "002427.50 48", "line 52  Q CHK  CB,$4,Q P"),
    # >>> THE SECOND SWAP, matched by line 10's TI three rows into
    # the page.  E0 here, A0 there, six words both ways.
    ("002454.40", "002472.00 80  000021.14 E0",
     "line 53  Q FIN  SWAPI,6,Q SAV,$1  -RESTORE INDEXES"),
    # listing_typography.md 13 again: the listing prints "CF", and
    # line 53 one row above prints its zeros round.
    ("002455.40", "000001.50 0F", "line 54  B,1.32($15)  -AND RETURN"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.43 ")
finish(fails)
