#!/usr/bin/env python3
"""verify_strap2_chm102633945.py -- CHM 102633945, a page of a STRAP
assembler's own code (../decks/strap2_chm102633945.strap), checked
against the machine code printed beside it.  Read in the ink at 600 dpi.

The deck's header covers what the page is, which values come from the
page itself, and the ink readings that needed 600 dpi.

40 checks: 8 symbols (the page's own labels, at the locations its third
column prints) and 32 printed rows, all but the cut first and faint last
statement.  The 25?.10 row is checked as 253.10; see the deck header.

The four CV marks and the one "*" are listing marks, not memory, and
are not checked.

PROVEN DISCRIMINATING: the injections and their observed failure sets
are in tests/run_tests.sh beside this test's entry.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap_asm import assemble                              # noqa: E402
from listing_oracle import check_rows, finish               # noqa: E402

prog = assemble(open(os.path.join(HERE, "..", "decks",
                                  "strap2_chm102633945.strap")).read())

ROWS = [
    ('000246.40', '000001.35 83 000201.34 00', 'BZB,ZIFBSF($3),KZ'),
    ('000247.40', '000002.73 83 004000.20 50', 'L,ZIDDSB($3)'),
    ('000250.40', '000253.10 00', 'B,KFNA (third digit faint; see deck)'),
    ('000251.00', '000001.33 83 000201.34 00', 'KFN BZB,ZIFFLF($3),KZ'),
    ('000252.00', '000002.65 83 006000.20 50', 'L,ZIDDSF($3)'),
    ('000253.00', '000256.34 C2', 'KFNA BRZ,KF1'),
    ('000253.40', '000002.40 83 022000.21 90', '*(BU,18),ZINFLD($3)'),
    ('000254.40', '000004.00 83 030012.20 D0', 'ST(BU,24),ZIOTPT($3),20'),
    ('000255.40', '000201.10 00', 'B,KZ'),
    ('000256.00', '000002.40 83 022067.20 50', 'KF1 L,ZINFLD($3),-18  (CV)'),
    ('000257.00', '000004.00 83 030064.20 D0', 'ST(BU,24),ZIOTPT($3),-24  (CV)'),
    ('000260.00', '000201.10 00', 'B,KZ'),
    ('000260.40', '000000.54 85 000276.74 00', 'KFA BZB,ZODR($5),KFP'),
    ('000261.40', '000004.22 13', 'LX,$9,ZIOTPT($3)'),
    ('000262.00', '000201.30 C2', 'BXVLZ,KZ'),
    ('000262.40', '000000.05 89 000266.74 02', 'BB,.05($9),KFA1'),
    ('000263.40', '000031.00 80 030000.20 50', 'L(BU,24),$9'),
    ('000264.40', '000037.00 80', 'SIC,$15'),
    ('000265.00', '000065.10 00', 'B,MORVAL  (*)'),
    ('000265.40', '000004.22 13', 'LX,$9,ZIOTPT($3)'),
    ('000266.00', '000272.50 00', 'B,KFA2'),
    ('000266.40', '000002.65 83 006000.20 50', 'KFA1 L,ZIDDSF($3)'),
    ('000267.40', '000274.34 C2', 'BRZ,KFA3'),
    ('000270.00', '000000.06 89 030000.21 90', '*(BU,24),.06($9)'),
    ('000271.00', '000004.00 83 031112.10 D0', 'STN(B,25),ZIOTPT($3),20'),
    ('000272.00', '000201.10 00', 'B,KZ'),
    ('000272.40', '000002.31 83 001000.00 F0', 'KFA2 CM0000,ZIFALL($3)'),
    ('000273.40', '000201.10 00', 'B,KZ'),
    ('000274.00', '000000.06 89 030064.20 50', 'KFA3 L(BU,24),.06($9),-24  (CV)'),
    ('000275.00', '000004.00 83 031161.10 D0', 'STN(B,25),ZIOTPT($3),-30  (CV)'),
    ('000276.00', '000201.10 00', 'B,KZ'),
    ('000276.40', '000000.57 85 000160.34 00', 'KFP BZB,ZOEXT($5),KEAA'),
]

SYMBOLS = {'KFN': '000251.00', 'KFNA': '000253.00', 'KF1': '000256.00',
           'KFA': '000260.40', 'KFA1': '000266.40', 'KFA2': '000272.40',
           'KFA3': '000274.00', 'KFP': '000276.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='CHM 102633945 '))
