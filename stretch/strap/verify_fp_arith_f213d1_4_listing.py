#!/usr/bin/env python3
"""verify_fp_arith_f213d1_4_listing.py -- F213 "ADD TO EXPONENT TEST",
sub-block F213D "INDICATOR TESTS" part one, the arithmetic result
indicators D1-D4 (programs/fp_arith_f213d1_4.strap) against jb_af1c
p.130.

The branch-on-indicator encodings decode consistently with the numbers
the assembler already carried (RLZ 56, RZ 57, RGZ 58, RN 59): the
printed field is indicator//2 plus the target's half-word bit,
indicator%2 picks the 40 or C0 series, and branch-on adds 2 --

    BZRLZ .34 40    BRLZ .34 42    BZRZ  .34 C0    BRZ  .34 C2
    BZRGZ .35 40    BRGZ .35 42    BZRN  .35 C0    BRN  .35 C2

which is the same table F212D's verifier established, reached here
through a different instruction.

Z,$IND prints "13.22 00": $IND is word 11 decimal, 13 octal.

FAE5 is the listing's own label at 017265.00; D4's last row is at
017312.40 and F213D5 begins at 017313.00, where this program halts.

TRANSCRIPTION NOTE: the page prints the first row of D2 and of D4 at
the same address as the preceding sub-test's last BRGZ (017272.00 and
017305.00).  A SIC and its branch are one word, so those BRGZ rows own
the .00 half and the following DL/DLN starts at .40.  The derivation is
confirmed on the far side: D2's Z,$IND is printed at 017273.00 and
D4's at 017306.00, exactly one half word after the DL that must
precede them.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f213d1_4.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022010.00", "0000125252525252525240", "FPK3"),
    ("022041.00", "0200177777777777777760", "FPK28"),
]

SIC = "1310.00 80"
Z   = "13.22 00"

CODE_ROWS = [
    # F213D1 -- XFN accumulator, nonzero negative result.
    ("017265.00", "22006.44 60", "DL(U), FPK1"),
    ("017265.40", Z,             "Z, $IND"),
    ("017266.00", "22010.45 60", "E+(U), FPK3"),
    ("017266.40", SIC, "SIC, SEN"), ("017267.00", "1304.34 40", "BZRLZ, SERS"),
    ("017267.40", SIC, "SIC, SEN"), ("017270.00", "1304.35 C0", "BZRN, SERS"),
    ("017270.40", SIC, "SIC, SEN"), ("017271.00", "1304.34 C2", "BRZ, SERS"),
    ("017271.40", SIC, "SIC, SEN"), ("017272.00", "1304.35 42", "BRGZ, SERS"),

    # F213D2 -- negative zero: RN without RLZ.
    ("017272.40", "22005.54 60", "DLN(U), FPK0"),
    ("017273.00", Z,             "Z, $IND"),
    ("017273.40", "22005.45 60", "E+(U), FPK0"),
    ("017274.00", SIC, "SIC, SEN"), ("017274.40", "1304.35 C0", "BZRN, SERS"),
    ("017275.00", SIC, "SIC, SEN"), ("017275.40", "1304.34 C0", "BZRZ, SERS"),
    ("017276.00", SIC, "SIC, SEN"), ("017276.40", "1304.34 42", "BRLZ, SERS"),
    ("017277.00", SIC, "SIC, SEN"), ("017277.40", "1304.35 42", "BRGZ, SERS"),

    # F213D3 -- positive zero.
    ("017300.00", "22005.44 60", "DL(U), FPK0"),
    ("017300.40", Z,             "Z, $IND"),
    ("017301.00", "22005.45 60", "E+(U), FPK0"),
    ("017301.40", SIC, "SIC, SEN"), ("017302.00", "1304.34 C0", "BZRZ, SERS"),
    ("017302.40", SIC, "SIC, SEN"), ("017303.00", "1304.34 42", "BRLZ, SERS"),
    ("017303.40", SIC, "SIC, SEN"), ("017304.00", "1304.35 C2", "BRN, SERS"),
    ("017304.40", SIC, "SIC, SEN"), ("017305.00", "1304.35 42", "BRGZ, SERS"),

    # F213D4 -- nonzero positive.
    ("017305.40", "22041.44 60", "DL(U), FPK28"),
    ("017306.00", Z,             "Z, $IND"),
    ("017306.40", "22041.45 60", "E+(U), FPK28"),
    ("017307.00", SIC, "SIC, SEN"), ("017307.40", "1304.35 40", "BZRGZ, SERS"),
    ("017310.00", SIC, "SIC, SEN"), ("017310.40", "1304.34 42", "BRLZ, SERS"),
    ("017311.00", SIC, "SIC, SEN"), ("017311.40", "1304.35 C2", "BRN, SERS"),
    ("017312.00", SIC, "SIC, SEN"), ("017312.40", "1304.34 C2", "BRZ, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
