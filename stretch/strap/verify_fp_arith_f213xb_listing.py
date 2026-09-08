#!/usr/bin/env python3
"""verify_fp_arith_f213xb_listing.py -- F213-X "ADD TO EXPONENT
IMMEDIATE TEST", sub-block F213-XB "TEST SIGN AND MOD COMBS"
(programs/fp_arith_f213xb.strap) against jb_af1c pp.135-136, plus its
constants against the pools pp.176-179.

Four spellings, differing in exactly the two modifier bits:

    E+I    .47 60    100111 -> unnorm 1, absSign 0, invSign 0
    E+AI   .67 60    110111 -> unnorm 1, absSign 1, invSign 0
    E-I    .57 60    101111 -> unnorm 1, absSign 0, invSign 1
    E-AI   .77 60    111111 -> unnorm 1, absSign 1, invSign 1

These are the one family whose modifier letters sit INSIDE the
mnemonic, since the "I" belongs to the operation, so strap_asm needed
an explicit rule for each -- the generic trailing-N/A suffix cannot
reach a name ending in I.

The six distinct immediates print as their own 18-bit address fields
and decode back through the same EF / ten-bit magnitude / ES layout:

    +6    001400        +7    001600        +250  076400
    -5    001300        -7    001700        -250  076500

Every sub-test is three words -- DL and the E+I variant as half words,
then a full-word compare and a SIC/branch pair -- so the sixteen base
addresses run 017531, 017534, ... 017606 at a uniform stride of 3, and
PASS lands on 017611.00 where the page has "BD,$+1.0".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f213xb.strap").read())

CONST_ROWS = [
    ("022011.00", "0000452525252525252520", "FPK4"),
    ("022020.00", "0003001252525252525240", "FPK11"),
    ("022022.00", "0003400525252525252520", "FPK13"),
    ("022023.00", "0006400005252525252520", "FPK14"),
    ("022070.00", "0003201252525252525240", "FPK51"),
    ("022204.00", "0200377777777777777770", "FK34"),
    ("022332.00", "0011000000000000000000", "FK121"),
]

SIC  = "1310.00 80"
BRGZ = "1304.35 42"
CMP  = "80 014072.15 70"
A    = {"FPK4":"22011","FPK11":"22020","FPK13":"22022","FPK14":"22023",
        "FPK51":"22070","FK34":"22204","FK121":"22332"}
MOD  = {"E+I":".47 60", "E+AI":".67 60", "E-I":".57 60", "E-AI":".77 60"}
IMM  = {6:"001400", 7:"001600", 250:"076400", -5:"001300", -7:"001700", -250:"076500"}

# (sub-test, base word octal, accumulator, spelling, immediate, compare)
XB = [("XB1", 0o17531,"FPK13","E+I",   6,"FPK14"), ("XB2", 0o17534,"FPK13","E+AI",  6,"FPK14"),
      ("XB3", 0o17537,"FPK13","E-I",   6,"FPK4"),  ("XB4", 0o17542,"FPK13","E-AI",  6,"FPK4"),
      ("XB5", 0o17545,"FPK51","E+I",   7,"FPK4"),  ("XB6", 0o17550,"FPK51","E+AI",  7,"FPK4"),
      ("XB7", 0o17553,"FPK51","E-I", 250,"FK34"),  ("XB8", 0o17556,"FPK51","E-AI",250,"FK34"),
      ("XB9", 0o17561,"FPK14","E+I",  -7,"FPK11"), ("XB10",0o17564,"FPK14","E+AI", -5,"FK121"),
      ("XB11",0o17567,"FPK14","E-I",  -5,"FK121"), ("XB12",0o17572,"FPK14","E-AI", -7,"FPK11"),
      ("XB13",0o17575,"FPK51","E+I",-250,"FK34"),  ("XB14",0o17600,"FPK51","E+AI", -7,"FPK4"),
      ("XB15",0o17603,"FPK51","E-I",  -7,"FPK4"),  ("XB16",0o17606,"FPK51","E-AI",-250,"FK34")]

CODE_ROWS = []
for name, w, acc, sp, iv, cmp_ in XB:
    CODE_ROWS += [
        (f"{w:06o}.00",   A[acc] + ".44 60",       f"{name} DL(U), {acc}"),
        (f"{w:06o}.40",   IMM[iv] + MOD[sp],       f"{name} {sp}(U), {iv:+d}"),
        (f"{w+1:06o}.00", A[cmp_] + ".00 " + CMP,  f"{name} CT0110(BU,12), {cmp_}, 116"),
        (f"{w+2:06o}.00", SIC,  f"{name} SIC, SEN"),
        (f"{w+2:06o}.40", BRGZ, f"{name} BRGZ, SERS"),
    ]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
