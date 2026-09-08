#!/usr/bin/env python3
"""verify_fp_arith_f215a_listing.py -- F215 "LOAD FACTOR TEST",
sub-block F215A "ARITHMETIC CHECKS" (programs/fp_arith_f215a.strap)
against jb_af1c p.144.

The block that adds LFT (opcode 1001010) to the model.  Ref. Manual
p.98: the addressed operand goes to factor register FT (word 14) bits
0-59, the sign-modified sign to FT bit 60, FT bits 61-63 to zero, and
the accumulator does not participate.

Each sub-test fills the accumulator's RIGHT word with the value it
expects and then XORs FT against it with a 60-bit CT0110 at offset 4 --
offset 4 is IBM 64-123, the right word's own bits 0-59.  The sign bit
sits outside that field and is checked separately with BZB/BB on
$FT+.60.  A3 reaches the same answer by loading FT from itself.

TRANSCRIPTION NOTE: the scan prints A2's LFT at 020200.00, which
cannot be -- the L above it is a full word at 020177.40.  At 020200.40
all nineteen following rows land on their printed addresses, and the
assembled PASS lands on 020213.40, the listing's own "BD,$+1.0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f215a.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"
BSER = "1304.10 00"
CTFT = "16.00 80 074002.15 70"      # CT0110(BU,60), $FT, 4

CODE_ROWS = [
    # A1 -- zeros.
    ("020172.00", "22005.00 80 000000.20 50", "A1 L(BU), FPK0"),
    ("020173.00", "22005.44 A0",              "A1 LFT(U), FPK0"),
    ("020173.40", CTFT,                       "A1 CT0110(BU,60), $FT, 4   test $FT0-59 +0"),
    ("020174.40", SIC, "A1 SIC"), ("020175.00", BRGZ, "A1 BRGZ"),
    ("020175.40", "16.74 80 020177.74 00",    "A1 BZB, $FT+.60, $+2.0     test sign bit +0"),
    ("020176.40", SIC, "A1 SIC"), ("020177.00", BSER, "A1 B, SERS"),

    # A2 -- ones.
    ("020177.40", "22006.00 80 000000.20 50", "A2 L(BU), FPK1"),
    ("020200.40", "22006.44 A0",              "A2 LFT(U), FPK1            (scan misprints .00)"),
    ("020201.00", CTFT,                       "A2 CT0110(BU,60), $FT, 4   test $FT0-59 +1 s"),
    ("020202.00", SIC, "A2 SIC"), ("020202.40", BRGZ, "A2 BRGZ"),
    ("020203.00", "16.74 80 020205.34 02",    "A2 BB, $FT+.60, $+2.0      test sign bit +1"),
    ("020204.00", SIC, "A2 SIC"), ("020204.40", BSER, "A2 B, SERS"),

    # A3 -- FT loaded from FT itself.
    ("020205.00", "22006.00 80 000000.20 50", "A3 L(BU), FPK1"),
    ("020206.00", "16.00 80 000000.36 F0",    "A3 CM1111(BU,64), $FT"),
    ("020207.00", "16.44 A0",                 "A3 LFT(U), $FT"),
    ("020207.40", CTFT,                       "A3 CT0110(BU,60), $FT, 4   test $FT 0-59 +1 s"),
    ("020210.40", SIC, "A3 SIC"), ("020211.00", BRGZ, "A3 BRGZ"),
    ("020211.40", "16.74 80 020213.74 02",    "A3 BB, $FT+.60, $+2.0      test sign bit +1"),
    ("020212.40", SIC, "A3 SIC"), ("020213.00", BSER, "A3 B, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
