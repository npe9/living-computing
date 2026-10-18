#!/usr/bin/env python3
"""verify_fp_arith_f213d5_9_listing.py -- F213 "ADD TO EXPONENT TEST",
sub-block F213D "INDICATOR TESTS" part two, the exponent range
indicators D5-D9 (../decks/fp_arith_f213d5_9.strap) against jb_af1c
pp.130-132.  This completes F213.

The branch-on-bit rows address the indicator register directly rather
than by mnemonic: "13.34" is word 11 (13 octal), bit 28 (34 octal),
which is XPFP, and the five indicators run 28-32 with ZM at 33 --
13.34, 13.35, 13.36, 13.37, 13.40, 13.41.  BB prints its second half
with 02 and BZB with 00, the branch-on-one versus branch-on-zero bit.

Every sub-test is exactly fourteen words: a head of four (B, DL,
Z,$IND, E+), a full-word BB with its SIC/branch pair, then two words
for each of the five BZB checks.  So the five base addresses run
017313, 017331, 017347, 017365 and 017403 at a uniform stride of 16
octal, and PASS lands on 017421.00 where the page has "BD,$+1.0" --
which is what checks the transcription's lengths.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f213d5_9.strap").read())

CONST_ROWS = [
    ("022041.00", "0200177777777777777760", "FPK28"),
    ("022146.00", "0143177777777777777760", "FK4"),
    ("022151.00", "0001017777777777777760", "FK7"),
    ("022167.00", "1777403777777777777760", "FK21"),
    ("022170.00", "0400177777777777777760", "FK22"),
    ("022203.00", "0000525252525252524400", "FK33"),
    ("022210.00", "0777572525252525252520", "FK38"),
    ("022211.00", "0777625252525252525240", "FK39"),
]

SIC   = "1310.00 80"
BSERS = "1304.10 00"
ADDR  = {"FPK28":"22041","FK4":"22146","FK7":"22151","FK21":"22167",
         "FK22":"22170","FK33":"22203","FK38":"22210","FK39":"22211"}
ALL   = [28, 29, 30, 31, 32, 33]

# (sub-test, base word octal, accumulator, operand, the bit that must be ON)
SUB = [("D5", 0o17313, "FK21",  "FK22",  28),
       ("D6", 0o17331, "FK38",  "FK33",  29),
       ("D7", 0o17347, "FPK28", "FPK28", 30),
       ("D8", 0o17365, "FK4",   "FK7",   31),
       ("D9", 0o17403, "FK39",  "FK39",  32)]

CODE_ROWS = []
for name, w, acc, mem, on in SUB:
    CODE_ROWS += [
        (f"{w:06o}.00",   f"{w:05o}.50 00",              f"{name} B, $+.32"),
        (f"{w:06o}.40",   ADDR[acc] + ".44 60",          f"{name} DL(U), {acc}"),
        (f"{w+1:06o}.00", "13.22 00",                    f"{name} Z, $IND"),
        (f"{w+1:06o}.40", ADDR[mem] + ".45 60",          f"{name} E+(U), {mem}"),
        (f"{w+2:06o}.00", f"13.{on:o} 80 {w+4:06o}.34 02", f"{name} BB, 11.{on}, $+2.0"),
        (f"{w+3:06o}.00", SIC,   f"{name} SIC, SEN"),
        (f"{w+3:06o}.40", BSERS, f"{name} B, SERS"),
    ]
    k = 0
    for off in ALL:
        if off == on:
            continue
        b = w + 4 + 2 * k
        CODE_ROWS += [
            (f"{b:06o}.00",   f"13.{off:o} 80 {b+2:06o}.34 00", f"{name} BZB, 11.{off}, $+2.0"),
            (f"{b+1:06o}.00", SIC,   f"{name} SIC, SEN"),
            (f"{b+1:06o}.40", BSERS, f"{name} B, SERS"),
        ]
        k += 1

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
