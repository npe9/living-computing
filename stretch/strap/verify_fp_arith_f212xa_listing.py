#!/usr/bin/env python3
"""verify_fp_arith_f212xa_listing.py -- F212-X "ADD TO FRACTION
ROUTINE", sub-block F212XA "ARITHMETIC CHECKS"
(programs/fp_arith_f212xa.strap) against jb_af1c pp.122-123, plus its
constants against the pools pp.176-178.

F+ is the new instruction here, and its printed code checks out
field-for-field against the FP encoding the assembler already used for
every other op in this diagnostic.  "22172.45 20" is address 022172
(FK24), then bits 18-23 as two octal digits and bits 24-31 as two hex:

    .45 = 100101 -> unnorm 1, absSign 0, invSign 0, code[0:2] 101
     20 = 00100000 -> code[3:6] 0010, index 0

so code = 1010010 = F+, unnormalized -- which is the opcode
opcodes.py already carried and StretchExecute did not implement.  DL
alongside it prints ".44 60" = 1000110, and the two differ in exactly
the bits that distinguish the two mnemonics.

SAP14 is the listing's own label at 016651.00 and the block's exit
sits at 016740.00 where the page has "BD,$+1.0"; both fall out of the
transcription rather than being placed, so the instruction lengths in
between are checked -- 9 sub-tests of 9 half-word-and-full-word rows
each, plus XA6's extra LC test.

OCR NOTE: on p.123 the two connective rows of XA8 (016724.40 and
016730.00) print their third field as "30" where the other 34 rows of
the identical instruction all print "80".  80 is taken as correct; a
"30" there would be a different VFL offset field on an instruction
whose every other occurrence in the block, XA7's and XA9's included,
is byte-identical.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f212xa.strap").read())

CONST_ROWS = [
    ("022007.00", "1777777777777777777760", "FPK2"),
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022047.00", "0001000000000000000020", "FPK34"),
    ("022050.00", "0001125252525252525240", "FPK35"),
    ("022053.00", "0031052525252525252520", "FPK38"),
    ("022107.00", "0001000000000000000000", "FPK67"),
    ("022167.00", "1777403777777777777760", "FK21"),
    ("022170.00", "0400177777777777777760", "FK22"),
    ("022171.00", "1777525252525252525240", "FK23"),
    ("022172.00", "1577452525252525252520", "FK24"),
    ("022173.00", "1577777777777777777760", "FK25"),
    ("022207.00", "0737577777777777777760", "FK37"),
    ("022210.00", "0777572525252525252520", "FK38"),
    ("022223.00", "1000377777777777777760", "FK49"),
    ("022224.00", "1746777777777777777760", "FK50"),
]

DL   = lambda a: (a + ".44 60")
FPL  = lambda a: (a + ".45 20")
CIN  = "80 060012.06 70"      # C0011(BU,48), <k>+.12, 20
COUT = "80 060012.15 70"      # CT0110(BU,48), <k>+.12, 20
CHI  = "80 074042.15 70"      # CT0110(BU,60), <k>, 68
SIC  = "1310.00 80"
BRGZ = "1304.35 42"

CODE_ROWS = [
    # F212XA1 -- exps in XFP rng; accumulator flagged, no addition.
    ("016651.00", DL("22171"),      "DL(U), FK23"),
    ("016651.40", "22170.14 " + CIN,  "C0011(BU,48), FK22+.12, 20"),
    ("016652.40", FPL("22172"),     "F+(U), FK24"),
    ("016653.00", "22171.00 " + CHI,  "CT0110(BU,60), FK23, 68"),
    ("016654.00", SIC,              "SIC, SEN"),
    ("016654.40", BRGZ,             "BRGZ, SERS"),
    ("016655.00", "22170.14 " + COUT, "CT0110(BU,48), FK22+.12, 20"),
    ("016656.00", SIC,              "SIC, SEN"),
    ("016656.40", BRGZ,             "BRGZ, SERS"),

    # F212XA2 -- exps in XFP + N rngs.
    ("016657.00", DL("22171"),      "DL(U), FK23"),
    ("016657.40", "22170.14 " + CIN,  "C0011(BU,48), FK22+.12, 20"),
    ("016660.40", FPL("22210"),     "F+(U), FK38"),
    ("016661.00", "22171.00 " + CHI,  "CT0110(BU,60), FK23, 68"),
    ("016662.00", SIC,              "SIC, SEN"),
    ("016662.40", BRGZ,             "BRGZ, SERS"),
    ("016663.00", "22170.14 " + COUT, "CT0110(BU,48), FK22+.12, 20"),
    ("016664.00", SIC,              "SIC, SEN"),
    ("016664.40", BRGZ,             "BRGZ, SERS"),

    # F212XA3 -- exps in XFP + XFN rngs.
    ("016665.00", DL("22171"),      "DL(U), FK23"),
    ("016665.40", "22170.14 " + CIN,  "C0011(BU,48), FK22+.12, 20"),
    ("016666.40", FPL("22007"),     "F+(U), FPK2"),
    ("016667.00", "22171.00 " + CHI,  "CT0110(BU,60), FK23, 68"),
    ("016670.00", SIC,              "SIC, SEN"),
    ("016670.40", BRGZ,             "BRGZ, SERS"),
    ("016671.00", "22170.14 " + COUT, "CT0110(BU,48), FK22+.12, 20"),
    ("016672.00", SIC,              "SIC, SEN"),
    ("016672.40", BRGZ,             "BRGZ, SERS"),

    # F212XA4 -- exps in N + XFP rngs; the addition IS performed.
    ("016673.00", DL("22050"),      "DL(U), FPK35"),
    ("016673.40", "22045.14 " + CIN,  "C0011(BU,48), FPK32+.12, 20"),
    ("016674.40", FPL("22172"),     "F+(U), FK24"),
    ("016675.00", "22045.00 " + CHI,  "CT0110(BU,60), FPK32, 68"),
    ("016676.00", SIC,              "SIC, SEN"),
    ("016676.40", BRGZ,             "BRGZ, SERS"),
    ("016677.00", "22045.14 " + COUT, "CT0110(BU,48), FPK32+.12, 20"),
    ("016700.00", SIC,              "SIC, SEN"),
    ("016700.40", BRGZ,             "BRGZ, SERS"),

    # F212XA5 -- exps in N rng.
    ("016701.00", DL("22050"),      "DL(U), FPK35"),
    ("016701.40", "22045.14 " + CIN,  "C0011(BU,48), FPK32+.12, 20"),
    ("016702.40", FPL("22053"),     "F+(U), FPK38"),
    ("016703.00", "22045.00 " + CHI,  "CT0110(BU,60), FPK32, 68"),
    ("016704.00", SIC,              "SIC, SEN"),
    ("016704.40", BRGZ,             "BRGZ, SERS"),
    ("016705.00", "22045.14 " + COUT, "CT0110(BU,48), FPK32+.12, 20"),
    ("016706.00", SIC,              "SIC, SEN"),
    ("016706.40", BRGZ,             "BRGZ, SERS"),

    # F212XA6 -- exps in N + XFN rngs; the 96-bit fraction overflows
    # and the carry is lost, so LC must come on.
    ("016707.00", DL("22047"),      "DL(U), FPK34"),
    ("016707.40", "22045.14 " + CIN,  "C0011(BU,48), FPK32+.12, 20"),
    ("016710.40", FPL("22007"),     "F+(U), FPK2"),
    ("016711.00", "22107.00 " + CHI,  "CT0110(BU,60), FPK67, 68"),
    ("016712.00", SIC,              "SIC, SEN"),
    ("016712.40", BRGZ,             "BRGZ, SERS"),
    ("016713.00", "22045.14 " + COUT, "CT0110(BU,48), FPK32+.12, 20"),
    ("016714.00", SIC,              "SIC, SEN"),
    ("016714.40", BRGZ,             "BRGZ, SERS"),
    ("016715.00", SIC,              "SIC, SEN"),
    ("016715.40", "1304.13 40",     "BZLC, SERS"),

    # F212XA7 -- exps in XFN + XFP rngs; accumulator flagged.
    ("016716.00", DL("22173"),      "DL(U), FK25"),
    ("016716.40", "22173.14 " + CIN,  "C0011(BU,48), FK25+.12, 20"),
    ("016717.40", FPL("22167"),     "F+(U), FK21"),
    ("016720.00", "22173.00 " + CHI,  "CT0110(BU,60), FK25, 68"),
    ("016721.00", SIC,              "SIC, SEN"),
    ("016721.40", BRGZ,             "BRGZ, SERS"),
    ("016722.00", "22173.14 " + COUT, "CT0110(BU,48), FK25+.12, 20"),
    ("016723.00", SIC,              "SIC, SEN"),
    ("016723.40", BRGZ,             "BRGZ, SERS"),

    # F212XA8 -- exps in XFN + N rngs.  (See the OCR note above for
    # the two connective rows the page prints with "30".)
    ("016724.00", DL("22173"),      "DL(U), FK25"),
    ("016724.40", "22173.14 " + CIN,  "C0011(BU,48), FK25+.12, 20"),
    ("016725.40", FPL("22207"),     "F+(U), FK37"),
    ("016726.00", "22173.00 " + CHI,  "CT0110(BU,60), FK25, 68"),
    ("016727.00", SIC,              "SIC, SEN"),
    ("016727.40", BRGZ,             "BRGZ, SERS"),
    ("016730.00", "22173.14 " + COUT, "CT0110(BU,48), FK25+.12, 20"),
    ("016731.00", SIC,              "SIC, SEN"),
    ("016731.40", BRGZ,             "BRGZ, SERS"),

    # F212XA9 -- exps in XFN rng.
    ("016732.00", DL("22223"),      "DL(U), FK49"),
    ("016732.40", "22223.14 " + CIN,  "C0011(BU,48), FK49+.12, 20"),
    ("016733.40", FPL("22224"),     "F+(U), FK50"),
    ("016734.00", "22223.00 " + CHI,  "CT0110(BU,60), FK49, 68"),
    ("016735.00", SIC,              "SIC, SEN"),
    ("016735.40", BRGZ,             "BRGZ, SERS"),
    ("016736.00", "22223.14 " + COUT, "CT0110(BU,48), FK49+.12, 20"),
    ("016737.00", SIC,              "SIC, SEN"),
    ("016737.40", BRGZ,             "BRGZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
