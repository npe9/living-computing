#!/usr/bin/env python3
"""verify_fp_arith_f213b_listing.py -- F213 "ADD TO EXPONENT TEST",
sub-block F213B "TESTS OF SIGN AND MODIFIER VARIATIONS"
(../decks/fp_arith_f213b.strap) against jb_af1c pp.128-129, plus its
constants against the pools pp.176-178.

The four E+ spellings differ in exactly the two modifier bits, and the
printed code is the evidence for the assembler's new E-/E-A rules:

    E+%U    .45 60    100101 -> unnorm 1, absSign 0, invSign 0
    E+A%U   .65 60    110101 -> unnorm 1, absSign 1, invSign 0
    E-%U    .55 60    101101 -> unnorm 1, absSign 0, invSign 1
    E-A%U   .75 60    111101 -> unnorm 1, absSign 1, invSign 1

so E- is E+ with N and E-A with both, the seventh written-minus
mnemonic after M-, -MG, M-MG, D-, D-MG and F-.

Every sub-test is exactly three words -- DL and E+ as half words, then
a full-word compare and a SIC/branch pair -- so the sixteen base
addresses run 017163, 017166, ... 017240 at a uniform stride of 3, and
the block's exit lands on 017243.00 where the page has "BD,$+1.0".
That regularity is what checks the transcription's lengths.

See the program header for B12's operand address, which the page
prints as "22056" where FPK49 sits at 022066.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f213b.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022015.00", "0002005252525252525240", "FPK8"),
    ("022020.00", "0003001252525252525240", "FPK11"),
    ("022022.00", "0003400525252525252520", "FPK13"),
    ("022023.00", "0006400005252525252520", "FPK14"),
    ("022025.00", "0011400000052525252520", "FPK16"),
    ("022031.00", "0015177777752525252520", "FPK20"),
    ("022032.00", "0031177777777777777767", "FPK21"),
    ("022041.00", "0200177777777777777760", "FPK28"),
    ("022062.00", "0027377777777777777760", "FPK45"),
    ("022063.00", "0057377777777777777760", "FPK46"),
    ("022064.00", "0200377777777777777760", "FPK47"),
    ("022065.00", "1577777777777777777770", "FPK48"),
    ("022066.00", "0026377777777777777760", "FPK49"),
    ("022067.00", "0031377777777777777760", "FPK50"),
    ("022070.00", "0003201252525252525240", "FPK51"),
    ("022173.00", "1577777777777777777760", "FK25"),
    ("022200.00", "1577617777777777777760", "FK30"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"
CMP  = "80 014072.15 70"     # CT0110(BU,12), <k>, 116

MOD = {"E+": ".45 60", "E+A": ".65 60", "E-": ".55 60", "E-A": ".75 60"}
A   = {"FPK0":"22005","FPK8":"22015","FPK11":"22020","FPK13":"22022","FPK14":"22023",
       "FPK16":"22025","FPK20":"22031","FPK21":"22032","FPK28":"22041","FPK45":"22062",
       "FPK46":"22063","FPK47":"22064","FPK48":"22065","FPK49":"22066","FPK50":"22067",
       "FPK51":"22070","FK25":"22173","FK30":"22200"}

# (sub-test, base word octal, accumulator, E+ spelling, operand, compare)
B = [("B1", 0o17163,"FPK13","E+", "FPK16","FPK20"), ("B2", 0o17166,"FPK13","E+A","FPK16","FPK20"),
     ("B3", 0o17171,"FPK16","E-", "FPK11","FPK14"), ("B4", 0o17174,"FPK16","E-A","FPK11","FPK14"),
     ("B5", 0o17177,"FPK51","E+", "FPK16","FPK14"), ("B6", 0o17202,"FPK51","E+A","FPK16","FPK14"),
     ("B7", 0o17205,"FPK47","E-", "FPK0", "FPK47"), ("B8", 0o17210,"FPK47","E-A","FPK0", "FPK47"),
     ("B9", 0o17213,"FPK0", "E+", "FPK47","FPK47"), ("B10",0o17216,"FPK28","E+A","FPK48","FK30"),
     ("B11",0o17221,"FPK28","E-", "FPK48","FK30"),  ("B12",0o17224,"FPK21","E-A","FPK46","FPK49"),
     ("B13",0o17227,"FPK47","E+", "FPK48","FK25"),  ("B14",0o17232,"FPK45","E+A","FPK50","FPK8"),
     ("B15",0o17235,"FPK45","E-", "FPK50","FPK8"),  ("B16",0o17240,"FPK47","E-A","FPK48","FK25")]

CODE_ROWS = []
for name, w, acc, sp, op, cmp_ in B:
    CODE_ROWS += [
        (f"{w:06o}.00",   A[acc] + ".44 60",        f"{name} DL(U), {acc}"),
        (f"{w:06o}.40",   A[op]  + MOD[sp],         f"{name} {sp}(U), {op}"),
        (f"{w+1:06o}.00", A[cmp_] + ".00 " + CMP,   f"{name} CT0110(BU,12), {cmp_}, 116"),
        (f"{w+2:06o}.00", SIC,                      f"{name} SIC, SEN"),
        (f"{w+2:06o}.40", BRGZ,                     f"{name} BRGZ, SERS"),
    ]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
