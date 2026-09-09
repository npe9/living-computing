#!/usr/bin/env python3
"""verify_fp_arith_f217d_listing.py -- F217 "DIVIDE TEST ROUTINE",
sub-block F217D "TESTS OF INDICATORS" (programs/fp_arith_f217d.strap)
against jb_af1c pp.156-157.

Drives everything F217A left untouched: ZD and the data flags (D1),
the arithmetic result indicators surviving a suppressed division (D2),
and the LEFT ZEROS COUNTER and PARTIAL FIELD indicator (D3-D6), which
no earlier block has ever read.

The LZC check clears word 7 bits 17-23 with a CM0000, loads the
expected value into the accumulator's right word (FK91 = 2, FPK0 = 0)
so it lands in IBM 121-127, and XORs the two seven-bit fields.

A BPFZ before each division clears PF, for the same reason F216D1
opens with a BPSHZ: PF is class P and no operation clears it.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/fp_arith_f217d.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022042.00", "0000400000000000000000", "FPK29"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022104.00", "0001051627340516273440", "FPK64"),
    ("022106.00", "0000400000000000000007", "FPK66"),
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022264.00", "1002051627340516273440", "FK83"),
    ("022271.00", "1577624713560247135620", "FK88"),
    ("022272.00", "1000251627340516273440", "FK89"),
    ("022274.00", "0000000000000000000002", "FK91"),
]

SIC   = "1310.00 80"
BRGZ  = "1304.35 42"
CMLZC = "7.21 80 007000.00 F0"
CTLZC = "7.21 80 007000.15 70"

CODE_ROWS = [
    # D1 -- zero divisor with flag bits set
    ("020717.00", "22071.40 60", "D1 L(U), FPK52"),
    ("020717.40", "13.22 00",    "D1 Z, $IND"),
    ("020720.00", "22106.41 E0", "D1 /(U), FPK66"),
    ("020720.40", SIC, "D1 SIC"),
    ("020721.00", "1304.14 40",  "D1 BZZD, SERS   error if ZD off"),
    ("020721.40", SIC, "D1 SIC"),
    ("020722.00", "1304.21 C0",  "D1 BZTF, SERS   error if TF off"),
    ("020722.40", SIC, "D1 SIC"),
    ("020723.00", "1304.22 40",  "D1 BZUF, SERS   error if UF off"),
    ("020723.40", SIC, "D1 SIC"),
    ("020724.00", "1304.22 C0",  "D1 BZVF, SERS"),
    # D2 -- result indicators unchanged across a suppressed division
    ("020724.40", "20725.10 00", "D2 B, $+.32"),
    ("020725.00", "13.22 00",    "D2 Z, $IND"),
    ("020725.40", "22071.40 60", "D2 L(U), FPK52   turns on RGZ"),
    ("020726.00", "22042.41 E0", "D2 /(U), FPK29"),
    ("020726.40", SIC, "D2 SIC"),
    ("020727.00", "1304.35 40",  "D2 BZRGZ, SERS   error if RGZ off"),
    ("020727.40", SIC, "D2 SIC"),
    ("020730.00", "1304.34 42",  "D2 BRLZ, SERS    error if others on"),
    ("020730.40", SIC, "D2 SIC"),
    ("020731.00", "1304.34 C2",  "D2 BRZ, SERS"),
    ("020731.40", SIC, "D2 SIC"),
    ("020732.00", "1304.35 C2",  "D2 BRN, SERS"),
    # D3 -- LZC ++2, PF on
    ("020732.40", "20733.10 00", "D3 B, $+.32"),
    ("020733.00", CMLZC,         "D3 CM0000(BU,7), $LZC"),
    ("020734.00", "22274.00 80 000000.20 50", "D3 L(BU,64), FK91"),
    ("020735.00", "22104.40 60", "D3 L(U), FPK64"),
    ("020735.40", "20736.13 C6", "D3 BPFZ, $+.32"),
    ("020736.00", "22071.41 E0", "D3 /(U), FPK52"),
    ("020736.40", CTLZC,         "D3 CT0110(BU,7), $LZC   test LZC ++2"),
    ("020737.40", SIC, "D3 SIC"), ("020740.00", BRGZ, "D3 BRGZ"),
    ("020740.40", SIC, "D3 SIC"),
    ("020741.00", "1304.13 C0",  "D3 BZPF, SERS"),
    # D4 -- LZC ++0, PF off
    ("020741.40", "20742.10 00", "D4 B, $+.32"),
    ("020742.00", CMLZC,         "D4 CM0000(BU,7), $LZC"),
    ("020743.00", "22005.00 80 000000.20 50", "D4 L(BU,64), FPK0"),
    ("020744.00", "22071.40 60", "D4 L(U), FPK52"),
    ("020744.40", "20745.13 C6", "D4 BPFZ, $+.32"),
    ("020745.00", "22104.41 E0", "D4 /(U), FPK64"),
    ("020745.40", CTLZC,         "D4 CT0110(BU,7), $LZC   test LZC ++0"),
    ("020746.40", SIC, "D4 SIC"), ("020747.00", BRGZ, "D4 BRGZ"),
    ("020747.40", SIC, "D4 SIC"),
    ("020750.00", "1304.13 C2",  "D4 BPF, SERS"),
    # D5 -- LZC ++2 with flagged exponents
    ("020750.40", "20751.10 00", "D5 B, $+.32"),
    ("020751.00", CMLZC,         "D5 CM0000(BU,7), $LZC"),
    ("020752.00", "22274.00 80 000000.20 50", "D5 L(BU,64), FK91"),
    ("020753.00", "22264.40 60", "D5 L(U), FK83   exp ++1028"),
    ("020753.40", "20754.13 C6", "D5 BPFZ, $+.32"),
    ("020754.00", "22235.41 E0", "D5 /(U), FK59   exp ++1024"),
    ("020754.40", CTLZC,         "D5 CT0110(BU,7), $LZC   test LZC ++2"),
    ("020755.40", SIC, "D5 SIC"), ("020756.00", BRGZ, "D5 BRGZ"),
    # D6 -- LZC ++0, both operands XFN
    ("020756.40", "20757.10 00", "D6 B, $+.32"),
    ("020757.00", "20757.53 C6", "D6 BPFZ, $+.32"),
    ("020757.40", CMLZC,         "D6 CM0000(BU,7), $LZC"),
    ("020760.40", "22005.00 80 000000.20 50", "D6 L(BU,64), FPK0"),
    ("020761.40", "22271.40 60", "D6 L(U), FK88   exp +-1791"),
    ("020762.00", "22272.41 E0", "D6 /(U), FK89   exp +-1024"),
    ("020762.40", CTLZC,         "D6 CT0110(BU,7), $LZC   check LZC ++0"),
    ("020763.40", SIC, "D6 SIC"), ("020764.00", BRGZ, "D6 BRGZ"),
    ("020764.40", SIC, "D6 SIC"),
    ("020765.00", "1304.13 C2",  "D6 BPF, SERS"),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
