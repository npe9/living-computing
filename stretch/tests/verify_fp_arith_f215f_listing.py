#!/usr/bin/env python3
"""verify_fp_arith_f215f_listing.py -- F215 "LOAD FACTOR TEST",
sub-block F215F "TEST NORM MOD" (../decks/fp_arith_f215f.strap)
against jb_af1c p.146.

The block that covers LFT's normalized path, which every LFT in F215A
and F215B (all %U) left untested.  F1 and F2 are the suppression rule
-- p.98, "When the operand is a value in the XFP or XFN ranges,
normalization, if specified, is suppressed" -- and neither is vacuous:
FK21's fraction has five leading zeros and FK30's three, so both would
shift if the range test were missing.

F3 is an exact-equality check across the whole 64-bit word: FPK10 is
+5 with fraction 055555555555, and normalizing it five places gives
aaaaaaaaaaa0 at exponent +0, which is FPK9 bit for bit.

LFT(N) prints .04 where LFT(U) prints .44 -- the normalization
modifier is the instruction's bit 18.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f215f.strap").read())

CONST_ROWS = [
    ("022016.00", "0000125252525252525000", "FPK9"),
    ("022017.00", "0002402525252525252520", "FPK10"),
    ("022167.00", "1777403777777777777760", "FK21"),
    ("022200.00", "1577617777777777777760", "FK30"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"
CTFT = "16.00 80 000000.15 70"      # CT0110(BU,64), $FT

CODE_ROWS = [
    ("020272.40", "22167.00 80 000000.20 50", "F1 L(BU,64), FK21"),
    ("020273.40", "22167.04 A0",              "F1 LFT(N), FK21   exponent in XFP range"),
    ("020274.00", CTFT,                       "F1 CT0110(BU,64), $FT   error if normalized"),
    ("020275.00", SIC, "F1 SIC"), ("020275.40", BRGZ, "F1 BRGZ"),

    ("020276.00", "22200.00 80 000000.20 50", "F2 L(BU,64), FK30"),
    ("020277.00", "22200.04 A0",              "F2 LFT(N), FK30   exponent in XFN range"),
    ("020277.40", CTFT,                       "F2 CT0110(BU,64), $FT   error if normalized"),
    ("020300.40", SIC, "F2 SIC"), ("020301.00", BRGZ, "F2 BRGZ"),

    ("020301.40", "22016.00 80 000000.20 50", "F3 L(BU,64), FPK9"),
    ("020302.40", "22017.04 A0",              "F3 LFT(N), FPK10  exponent in N range"),
    ("020303.00", CTFT,                       "F3 CT0110(BU,64), $FT   error if not normalized"),
    ("020304.00", SIC, "F3 SIC"), ("020304.40", BRGZ, "F3 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
