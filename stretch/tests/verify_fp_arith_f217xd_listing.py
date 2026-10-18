#!/usr/bin/env python3
"""verify_fp_arith_f217xd_listing.py -- F217-XD "INDICATOR TESTS"
(../decks/fp_arith_f217xd.strap) against jb_af1c p.164.

R/'s version of F217D3-D6: the left zeros counter and the partial
field indicator, with the operands interchanged.  Each row uses the
same PAIR of constants as its F217D counterpart and expects the same
LZC, which is the point -- LZC records the excess of divisor shift
over dividend shift, a property of the pair rather than of where each
operand sits.

XD3 checks no PF, exactly as F217D5 does not.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/fp_arith_f217xd.strap").read())

CONST_ROWS = [
    ("022005.00", "0000000000000000000000", "FPK0"),
    ("022071.00", "0001024713560247135620", "FPK52"),
    ("022104.00", "0001051627340516273440", "FPK64"),
    ("022235.00", "1000024713560247135620", "FK59"),
    ("022264.00", "1002051627340516273440", "FK83"),
    ("022271.00", "1577624713560247135620", "FK88"),
    ("022272.00", "1000251627340516273440", "FK89"),
    ("022274.00", "0000000000000000000002", "FK91"),
]

CODE_ROWS = [
    ('021214.40', '7.21 80 007000.00 F0', 'XD1 CM0000(BU,7), $LZC'),
    ('021215.40', '22274.00 80 000000.20 50', 'XD1 L(BU,64), FK91'),
    ('021216.40', '22071.40 60', 'XD1 L(U), FPK52   (divisor)'),
    ('021217.00', '021217.53 C6', 'XD1 BPFZ, $+.32'),
    ('021217.40', '22104.43 E0', 'XD1 R/(U), FPK64   (dividend)'),
    ('021220.00', '7.21 80 007000.15 70', 'XD1 CT0110(BU,7), $LZC'),
    ('021221.00', '1310.00 80', 'XD1 SIC'),
    ('021221.40', '1304.35 42', 'XD1 BRGZ'),
    ('021222.00', '1310.00 80', 'XD1 SIC'),
    ('021222.40', '1304.13 C0', 'XD1 BZPF, SERS'),
    ('021223.00', '7.21 80 007000.00 F0', 'XD2 CM0000(BU,7), $LZC'),
    ('021224.00', '22005.00 80 000000.20 50', 'XD2 L(BU,64), FPK0'),
    ('021225.00', '22104.40 60', 'XD2 L(U), FPK64   (divisor)'),
    ('021225.40', '021226.13 C6', 'XD2 BPFZ, $+.32'),
    ('021226.00', '22071.43 E0', 'XD2 R/(U), FPK52   (dividend)'),
    ('021226.40', '7.21 80 007000.15 70', 'XD2 CT0110(BU,7), $LZC'),
    ('021227.40', '1310.00 80', 'XD2 SIC'),
    ('021230.00', '1304.35 42', 'XD2 BRGZ'),
    ('021230.40', '1310.00 80', 'XD2 SIC'),
    ('021231.00', '1304.13 C2', 'XD2 BPF, SERS'),
    ('021231.40', '7.21 80 007000.00 F0', 'XD3 CM0000(BU,7), $LZC'),
    ('021232.40', '22274.00 80 000000.20 50', 'XD3 L(BU,64), FK91'),
    ('021233.40', '22235.40 60', 'XD3 L(U), FK59   (divisor)'),
    ('021234.00', '021234.53 C6', 'XD3 BPFZ, $+.32'),
    ('021234.40', '22264.43 E0', 'XD3 R/(U), FK83   (dividend)'),
    ('021235.00', '7.21 80 007000.15 70', 'XD3 CT0110(BU,7), $LZC'),
    ('021236.00', '1310.00 80', 'XD3 SIC'),
    ('021236.40', '1304.35 42', 'XD3 BRGZ'),
    ('021237.00', '7.21 80 007000.00 F0', 'XD4 CM0000(BU,7), $LZC'),
    ('021240.00', '22005.00 80 000000.20 50', 'XD4 L(BU,64), FPK0'),
    ('021241.00', '22272.40 60', 'XD4 L(U), FK89   (divisor)'),
    ('021241.40', '021242.13 C6', 'XD4 BPFZ, $+.32'),
    ('021242.00', '22271.43 E0', 'XD4 R/(U), FK88   (dividend)'),
    ('021242.40', '7.21 80 007000.15 70', 'XD4 CT0110(BU,7), $LZC'),
    ('021243.40', '1310.00 80', 'XD4 SIC'),
    ('021244.00', '1304.35 42', 'XD4 BRGZ'),
    ('021244.40', '1310.00 80', 'XD4 SIC'),
    ('021245.00', '1304.13 C2', 'XD4 BPF, SERS'),
]

if __name__ == "__main__":
    fails = check_rows(prog, CONST_ROWS, label="constants")
    fails += check_rows(prog, CODE_ROWS, label="code")
    finish(fails)
