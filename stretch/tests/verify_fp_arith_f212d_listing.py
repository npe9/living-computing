#!/usr/bin/env python3
"""verify_fp_arith_f212d_listing.py -- F212D "INDICATOR TESTS"
(../decks/fp_arith_f212d.strap) against jb_af1c pp.120-121, plus its
constants against the pools pp.176-178.  This closes F212.

The branch-on-indicator encodings are the substance of this block, and
they decode consistently with the indicator numbers the assembler
already carried (RLZ 56, RZ 57, RGZ 58, RN 59, LC 22): the printed
field is indicator//2 plus the target's half-word bit, indicator%2
picks the 40 or C0 series, branch-on adds 2 and clear adds 4.  So

    BZLC   .13 40    LC,  branch when OFF
    BLCZ   .53 46    LC,  branch when ON, and clear (target $+.32,
                     whose half-word bit adds the 40 to the field)
    BZLCZ  .13 44    LC,  branch when OFF, and clear
    BZRLZ  .34 40    BRLZ  .34 42    BZRZ .34 C0    BRZ  .34 C2
    BZRGZ  .35 40    BRGZ  .35 42    BZRN .35 C0    BRN  .35 C2

That is what settles D2's third row as BRZ (".34 C2") rather than any
other spelling, and it is why D2's SHF(U),3 is worth noting: ".47 20"
is the only shift in all of F212 carrying NEITHER sign modifier, so
its direction comes from address bit 11 alone.

FSF5 is the listing's own label at 016606.00 and the block's exit sits
at 016644.00 where the page has "BD,$+1.0"; both fall out of the
transcription rather than being placed, so the instruction lengths in
between are checked.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f212d.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022006.00", "1777777777777777777777", "FPK1"),
    ("022167.00", "1777403777777777777760", "FK21"),
    ("022231.00", "1777617777777777777770", "FK55"),
    ("022347.00", "0000100000000000000000", "FK134"),
]

CODE_ROWS = [
    # F212D1 -- lost carry, all three sub-cases, in full.
    ("016606.00", "16606.53 46", "BLCZ, $+.32"),
    ("016606.40", "22006.00 80 000040.36 70", "C1111(BU,64), FPK1, 64"),
    ("016607.40", "22006.00 80 000000.36 70", "C1111(BU,64), FPK1"),
    ("016610.40", "200.67 20", "SHFL(U), 1"),
    ("016611.00", "1310.00 80", "SIC, SEN"),
    ("016611.40", "1304.13 40", "BZLC, SERS"),
    ("016612.00", "16612.53 46", "BLCZ, $+.32"),
    ("016612.40", "22347.40 60", "L(U), FK134"),
    ("016613.00", "200.67 20", "SHFL(U), 1"),
    ("016613.40", "1310.00 80", "SIC, SEN"),
    ("016614.00", "1304.13 40", "BZLC, SERS"),
    ("016614.40", "16615.13 46", "BLCZ, $+.32"),
    ("016615.00", "22347.40 60", "L(U), FK134"),
    ("016615.40", "400.67 20", "SHFL(U), 2"),
    ("016616.00", "1310.00 80", "SIC, SEN"),
    ("016616.40", "1304.13 44", "BZLCZ, SERS"),

    # F212D2 -- RLZ and RN; the only plain SHF in F212.
    ("016617.00", "22231.44 60", "DL(U), FK55"),
    ("016617.40", "13.22 00", "Z, $IND"),
    ("016620.00", "600.47 20", "SHF(U), 3"),
    ("016620.40", "1310.00 80", "SIC, SEN"),
    ("016621.00", "1304.34 40", "BZRLZ, SERS"),
    ("016622.00", "1304.35 C0", "BZRN, SERS"),
    ("016623.00", "1304.34 C2", "BRZ, SERS"),
    ("016624.00", "1304.35 42", "BRGZ, SERS"),

    # F212D3 -- negative zero: RN and RZ on, RLZ and RGZ off.
    ("016624.40", "22005.54 60", "DLN(U), FPK0"),
    ("016625.00", "13.22 00", "Z, $IND"),
    ("016625.40", "0.67 20", "SHFL(U), 0"),
    ("016626.40", "1304.35 C0", "BZRN, SERS"),
    ("016627.40", "1304.34 C0", "BZRZ, SERS"),
    ("016630.40", "1304.34 42", "BRLZ, SERS"),
    ("016631.40", "1304.35 42", "BRGZ, SERS"),

    # F212D4 -- positive zero.
    ("016632.00", "22005.44 60", "DL(U), FPK0"),
    ("016633.00", "0.67 20", "SHFL(U), 0"),
    ("016634.00", "1304.34 C0", "BZRZ, SERS"),
    ("016635.00", "1304.34 42", "BRLZ, SERS"),
    ("016636.00", "1304.35 C2", "BRN, SERS"),
    ("016637.00", "1304.35 42", "BRGZ, SERS"),

    # F212D5 -- RGZ.
    ("016637.40", "22167.44 60", "DL(U), FK21"),
    ("016640.40", "1200.67 20", "SHFL(U), 5"),
    ("016641.40", "1304.35 40", "BZRGZ, SERS"),
    ("016642.40", "1304.34 42", "BRLZ, SERS"),
    ("016643.40", "1304.35 C2", "BRN, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
