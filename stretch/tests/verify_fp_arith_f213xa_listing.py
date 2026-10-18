#!/usr/bin/env python3
"""verify_fp_arith_f213xa_listing.py -- F213-X "ADD TO EXPONENT
IMMEDIATE TEST", sub-block F213XA "ARITHMETIC CHECKS"
(../decks/fp_arith_f213xa.strap) against jb_af1c pp.133-134, plus its
constants against the pools pp.176-178.

The immediates are the substance here.  E+I's addend is bits 0-11 of
the effective address -- EF, a ten-bit magnitude, then ES, at address
bits 17, 16-7 and 6 -- so the five distinct values in this block print
as their own address fields and decode straight back:

    +2047  777600    ef 1, magnitude 1023, es 0
    +1023  377600    ef 0, magnitude 1023, es 0
    -1791  677700    ef 1, magnitude  767, es 1
    -1023  377700    ef 0, magnitude 1023, es 1
       +2  000400    ef 0, magnitude    2, es 0

An out-of-range magnitude keeps its LOW TEN BITS with EF marking the
overflow, which is the same representation fpMakeExp stores.

XA1-XA7 are a uniform eight words each, so their base addresses run
017426, 017436, ... 017506; XA8 carries an extra full-word CM1111 in
front and ends the block at 017527.00, where the page has "BD,$+1.0".

XA8's CM1111 addresses DIN+.12, and its printed first half "17520.54"
confirms where DIN lands: word 017520 bit 44 octal 54, so DIN itself
is at 017520.40 and the patched field is address bits 5-0 -- the six
below the twelve the exponent occupies.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f213xa.strap").read())

CONST_ROWS = [
    ("022007.00", "1777777777777777777760", "FPK2"),
    ("022045.00", "0001177777777777777760", "FPK32"),
    ("022064.00", "0200377777777777777760", "FPK47"),
    ("022103.00", "0002177777777777777760", "FPK62"),
    ("022172.00", "1577452525252525252520", "FK24"),
    ("022173.00", "1577777777777777777760", "FK25"),
    ("022206.00", "1000177777777777777760", "FK36"),
    ("022211.00", "0777625252525252525240", "FK39"),
    ("022223.00", "1000377777777777777760", "FK49"),
    ("022232.00", "1777225252525252525240", "FK56"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"
EXP  = "80 014072.15 70"     # CT0110(BU,12), <k>, 116
HI   = "80 060042.15 70"     # CT0110(BU,48), <k>+.12, 68
LO   = "80 060012.15 70"     # CT0110(BU,48), <k>+.12, 20
IN   = "80 060012.06 70"     # C0011(BU,48),  <k>+.12, 20
A = {"FPK2":"22007","FPK32":"22045","FPK47":"22064","FPK62":"22103","FK24":"22172",
     "FK25":"22173","FK36":"22206","FK39":"22211","FK49":"22223","FK56":"22232"}
IMM = {2047:"777600", 1023:"377600", -1791:"677700", -1023:"377700", 2:"000400"}

# (sub-test, base word octal, accumulator, immediate, exponent compare)
XA = [("XA1", 0o17426, "FK24",  2047,  "FK24"),
      ("XA2", 0o17436, "FK36",  1023,  "FK36"),
      ("XA3", 0o17446, "FK24", -1791,  "FK24"),
      ("XA4", 0o17456, "FK39", -1023,  "FK56"),
      ("XA5", 0o17466, "FPK32",    2,  "FPK62"),
      ("XA6", 0o17476, "FK49", -1023,  "FK49"),
      ("XA7", 0o17506, "FPK2", -1791,  "FPK2")]

CODE_ROWS = []
for name, w, acc, iv, cmp_ in XA:
    CODE_ROWS += [
        (f"{w:06o}.00",   A[acc] + ".44 60",        f"{name} DL(U), {acc}"),
        (f"{w:06o}.40",   A[acc] + ".14 " + IN,     f"{name} C0011(BU,48), {acc}+.12, 20"),
        (f"{w+1:06o}.40", IMM[iv] + ".47 60",       f"{name} E+I(U), {iv:+d}"),
        (f"{w+2:06o}.00", A[cmp_] + ".00 " + EXP,   f"{name} CT0110(BU,12), {cmp_}, 116"),
        (f"{w+3:06o}.00", SIC, f"{name} SIC"), (f"{w+3:06o}.40", BRGZ, f"{name} BRGZ"),
        (f"{w+4:06o}.00", A[acc] + ".14 " + HI,     f"{name} CT0110(BU,48), {acc}+.12, 68"),
        (f"{w+5:06o}.00", SIC, f"{name} SIC"), (f"{w+5:06o}.40", BRGZ, f"{name} BRGZ"),
        (f"{w+6:06o}.00", A[acc] + ".14 " + LO,     f"{name} CT0110(BU,48), {acc}+.12, 20"),
        (f"{w+7:06o}.00", SIC, f"{name} SIC"), (f"{w+7:06o}.40", BRGZ, f"{name} BRGZ"),
    ]

# XA8 -- the self-modifying one, with a full-word CM1111 ahead of it.
CODE_ROWS += [
    ("017516.00", "17520.54 80 006000.36 F0", "XA8 CM1111(BU,6,8), DIN+.12"),
    ("017517.00", "22064.44 60",              "XA8 DL(U), FPK47"),
    ("017517.40", "22064.14 " + IN,           "XA8 C0011(BU,48), FPK47+.12, 20"),
    ("017520.40", "677700.47 60",             "XA8 DIN  E+I(U), -1791"),
    ("017521.00", "22173.00 " + EXP,          "XA8 CT0110(BU,12), FK25, 116"),
    ("017522.00", SIC, "XA8 SIC"), ("017522.40", BRGZ, "XA8 BRGZ"),
    ("017523.00", "22064.14 " + HI,           "XA8 CT0110(BU,48), FPK47+.12, 68"),
    ("017524.00", SIC, "XA8 SIC"), ("017524.40", BRGZ, "XA8 BRGZ"),
    ("017525.00", "22064.14 " + LO,           "XA8 CT0110(BU,48), FPK47+.12, 20"),
    ("017526.00", SIC, "XA8 SIC"), ("017526.40", BRGZ, "XA8 BRGZ"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
