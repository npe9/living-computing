#!/usr/bin/env python3
"""verify_fp_arith_f214b_listing.py -- F214 "MULTIPLY TEST ROUTINE",
sub-block F214B "TESTS OF SIGN AND MODIFIER COMBINATIONS"
(programs/fp_arith_f214b.strap) against jb_af1c p.138.

Five branch targets (F214B1 and POR1-POR5) are named in the listing at
017674.00, 017701.40, 017707.00, 017714.40, 017722.00 and 017727.00,
and all six fall out of this transcription's instruction lengths rather
than being placed -- which is the strongest check the block offers,
since a single wrong length would move every later one.

The multiply spellings differ in the two modifier bits alone:

    *       .41 A0    100001 -> unnorm 1, absSign 0, invSign 0
    *N      .51 A0    101001 -> unnorm 1, absSign 0, invSign 1
    *NA     .71 A0    111001 -> unnorm 1, absSign 1, invSign 1

and both need no assembler rule, the generic trailing-N/A suffix
stripping them to `*`.  Note that F214A5's "*%N" is a different thing
entirely -- the NORMALIZED modifier on a bare `*`, printed .01 -- so
the printed code, not the source spelling, is what distinguishes them.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f214b.strap").read())

CONST_ROWS = [
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022122.00", "0000500000000000000010", "FPK82"),
    ("022123.00", "0000500000000000000000", "FPK84"),
    ("022162.00", "0001412345670123456700", "FK16"),
]

SIC   = "1310.00 80"
BRGZ  = "1304.35 42"
BSERS = "1304.10 00"
R60   = "22162.00 80 074042.15 70"   # CT0110(BU,60), FK16, 68

CODE_ROWS = [
    # B1 -- memory sign negative, no modifiers.
    ("017673.40", "17674.10 00",              "B1 B, $+.32"),
    ("017674.00", "22071.40 60",              "B1 L(U), FPK52"),
    ("017674.40", "22122.41 A0",              "B1 *(U), FPK82"),
    ("017675.00", R60,                        "B1 CT0110(BU,60), FK16, 68"),
    ("017676.00", SIC, "B1 SIC"), ("017676.40", BRGZ, "B1 BRGZ"),
    ("017677.00", "12.04 80 017701.74 02",    "B1 BB, 10.4, POR1"),
    ("017700.00", SIC, "B1 SIC"), ("017700.40", BSERS, "B1 B, SERS"),

    # B2 -- both signs negative.
    ("017701.00", "17701.50 00",              "B2 B, $+.32"),
    ("017701.40", "22071.50 60",              "B2 POR1  LN(U), FPK52"),
    ("017702.00", "22122.41 A0",              "B2 *(U), FPK82"),
    ("017702.40", R60,                        "B2 CT0110(BU,60), FK16, 68"),
    ("017703.40", SIC, "B2 SIC"), ("017704.00", BRGZ, "B2 BRGZ"),
    ("017704.40", "12.04 80 017707.34 00",    "B2 BZB, 10.4, POR2"),
    ("017705.40", SIC, "B2 SIC"), ("017706.00", BSERS, "B2 B, SERS"),

    # B3 -- N inverts a positive memory sign.
    ("017706.40", "17707.10 00",              "B3 B, $+.32"),
    ("017707.00", "22071.40 60",              "B3 POR2  L(U), FPK52"),
    ("017707.40", "22123.51 A0",              "B3 *N(U), FPK84"),
    ("017710.00", R60,                        "B3 CT0110(BU,60), FK16, 68"),
    ("017711.00", SIC, "B3 SIC"), ("017711.40", BRGZ, "B3 BRGZ"),
    ("017712.00", "12.04 80 017714.74 02",    "B3 BB, 10.4, POR3"),
    ("017713.00", SIC, "B3 SIC"), ("017713.40", BSERS, "B3 B, SERS"),

    # B4 -- N+A on an already-positive sign: blind to A.
    ("017714.00", "17714.50 00",              "B4 B, $+.32"),
    ("017714.40", "22071.40 60",              "B4 POR3  L(U), FPK52"),
    ("017715.00", "22123.71 A0",              "B4 *NA(U), FPK84"),
    ("017715.40", R60,                        "B4 CT0110(BU,60), FK16, 68"),
    ("017716.40", SIC, "B4 SIC"), ("017717.00", BRGZ, "B4 BRGZ"),
    ("017717.40", "12.04 80 017722.34 02",    "B4 BB, 10.4, POR4"),
    ("017720.40", SIC, "B4 SIC"), ("017721.00", BSERS, "B4 B, SERS"),

    # B5 -- N+A on a NEGATIVE sign: the row that carries A.
    ("017721.40", "17722.10 00",              "B5 B, $+.32"),
    ("017722.00", "22071.50 60",              "B5 POR4  LN(U), FPK52"),
    ("017722.40", "22122.71 A0",              "B5 *NA(U), FPK82"),
    ("017723.00", R60,                        "B5 CT0110(BU,60), FK16, 68"),
    ("017724.00", SIC, "B5 SIC"), ("017724.40", BRGZ, "B5 BRGZ"),
    ("017725.00", "12.04 80 017727.34 00",    "B5 BZB, 10.4, POR5"),
    ("017726.00", SIC, "B5 SIC"), ("017726.40", BSERS, "B5 B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
