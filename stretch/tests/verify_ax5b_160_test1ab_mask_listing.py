#!/usr/bin/env python3
"""verify_ax5b_160_test1ab_mask_listing.py -- jb_ax5b "I-Box 5", routine
1260 ("CHECK MASK, INDICATOR, AND INTERRUPT."), its prologue and TESTs 1A
and 1B (../decks/ax5b_160_test1ab_mask.strap) against the machine code
the listing prints beside each source line: PDF pp.8-13, octal
014064.00-014253.00.  The sheets carry no printed page number; cite PDF
pages.

WHY IT MATTERS.  IBM's own test of the mask register's fixed bits
(Reference Manual Figure 11, printed p.43, PDF p.46: the Mask column is
1 for indicators 0-19, settable for 20-47, 0 for 48-63).  The rows that touch the mask register (word 12, octal 14)
are TRANSMIT (TI) full words:

    TI,1,0,12.0         0.00 80 000014.02 A0      (014071.00)
    TI,1,12.0,$X0      14.00 80 000020.02 A0      (014072.00)
    TI,1,12.0,$X1      14.00 80 000021.02 A0      (014104.00)
    TI,1,$X2,12.0      22.00 80 000014.02 A0      (014172.00)
    TI,1,12.0,$X2      14.00 80 000022.02 A0      (014174.00)

WHAT IT CHECKS: 240 rows and 18 symbols.  The prologue (6 rows, p.8);
TEST 1A's code (35 rows, p.9), its twenty-entry error table (80 rows,
pp.9-11) and exit (8 rows, p.11); TEST 1B's code (31 rows, p.12), its
sixteen-entry error table (64 rows, pp.12-13) and exit (8 rows, p.13);
and 8 of the p.114 constants the run reads (I00Z, I00O, the zero word
at 024521.00, BIT0-BIT3, BIT24).
The error-table entries print the same four rows apart from the comment,
so they are generated below from the printed pattern; every generated
row was then compared with the page images (pp.9-13), row for row.  Rows
marked (ext) name SSIP's SEN/SENO/SERS/SSW/RET/DPET13/IDF1, placed at
the addresses jb_ax4b PDF p.193's SYN table prints (and which these
pages print too: 1310.00, 1304.10, 1301.10, 1306.40, 1437.03, 1443.10),
so they check opcode and modifier bits only.

PROVEN DISCRIMINATING, measured 2026-11-19: injected into the assembler
in the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written.  OBSERVED failure set:
  enc_transmit's A2 field gets its word-address low bit flipped
    ("(addr19 ^ 2, 19)" for "(addr19, 19)") -> 5 FAIL, exactly the five
    TI rows (014071.00, 014072.00, 014104.00, 014172.00, 014174.00;
    e.g. 014071.00 '000000.00 80 000015.02 A0' vs '000000.00 80
    000014.02 A0').  Nothing else moves.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_160_test1ab_mask.strap").read())


def o(hw):
    return f'{hw // 2:06o}.{"40" if hw % 2 else "00"}'


ROWS = [
    # ---- PDF p.8, the prologue ----
    ('014064.00', '14067.02 10', 'I60 LX,$X1,160ID  -UPDATE IDENT.'),
    ('014064.40', '1437.03 10', 'SX,$X1,DPET13 (ext)'),
    ('014065.00', '1306.40 80', 'SIC,RET (ext)'),
    ('014065.40', '1443.10 00', 'B,IDF1 (ext)  -PRINT ID.'),
    ('014066.00', '22737.22 00', 'Z,IC260'),
    ('014066.40', '14070.04 00', 'BD,1601'),
    # ---- PDF p.9, TEST 1A ----
    ('014070.00', '24502.00 10', '1601 LX,$X0,I00Z  -TEST 1A'),
    ('014070.40', '14.01 10', 'SX,$X0,12.0'),
    ('014071.00', '0.00 80 000014.02 A0', 'TI,1,0,12.0'),
    ('014072.00', '14.00 80 000020.02 A0', 'TI,1,12.0,$X0'),
    ('014073.00', '24552.00 90', 'KV,$X0,BIT24'),
    ('014073.40', '14100.33 42', 'BXH,1602'),
    ('014074.00', '1310.00 80', 'SIC,SEN (ext)  -BIT 24 OF MASK REG STUCK ON 1'),
    ('014074.40', '1304.10 00', 'B,SERS (ext)'),
    ('014075.00', '22737.32 10', 'LX,$X13,IC260  -UPDATE CONTINUITY CHECK.'),
    ('014075.40', '24522.32 B0', 'V+,$X13,BIT0'),
    ('014076.00', '24523.32 B0', 'V+,$X13,BIT1'),
    ('014076.40', '24524.32 B0', 'V+,$X13,BIT2'),
    ('014077.00', '22737.33 10', 'SX,$X13,IC260'),
    ('014077.40', '14556.04 00', 'BD,16041'),
    ('014100.00', '24521.22 00', '1602 Z,BIT0-1.0  -BITS 0-19.'),
    ('014100.40', '24521.01 01', 'LVI,$X0,BIT0-1.0'),
    ('014101.00', '14105.01 D0', 'SVA,$X0,1603'),
    ('014101.40', '1.01 05', 'V+I,$X0,1.00'),
    ('014102.00', '14105.41 D0', 'SVA,$X0,1603+.32'),
    ('014102.40', '24.05 02', 'LCI,$X2,20'),
    ('014103.00', '14113.01 01', 'LVI,$X0,160B1'),
    ('014103.40', '14106.41 D0', '1605 SVA,$X0,1604'),
    ('014104.00', '14.00 80 000021.02 A0', 'TI,1,12.0,$X1'),
    ('014105.00', '0.02 B0', '1603 V+,$X1,0'),
    ('014105.40', '0.02 90', 'KV,$X1,0'),
    ('014106.00', '14107.32 40', 'BZXL,$+1.0'),
    ('014106.40', '0.10 00', '1604 $B,0'),
    ('014107.00', '1.05 08', 'C-I,$X2,1.0'),
    ('014107.40', '14163.30 42', 'BXCZ,1606'),
    ('014110.00', '2.01 05', 'V+I,$X0,2.0'),
    ('014110.40', '14105.44 30', 'LV,$X2,1603+.32'),
    ('014111.00', '14105.05 D0', 'SVA,$X2,1603'),
    # "0D", read at 400 dpi (at 150 dpi the D looks like a 0)
    ('014111.40', '1.05 0D', 'V-I,$X2,1.0  -SUB TO INCCREMENT, BIT 24 IS 2.'),
    ('014112.00', '14105.45 D0', 'SVA,$X2,1603+.32'),
    ('014112.40', '14103.50 00', 'B,1605'),
]
# ---- PDF pp.9-11, error table 160B1: bits 00-19, four rows each ----
hw = 0o14113 * 2
for k in range(20):
    pg = 9 if k < 4 else 10 if k < 14 else 11
    ROWS += [
        (o(hw), '1310.00 80', f'SIC,SEN (ext)  -BIT {k:02d} OF MASK REG NOT ONE. p.{pg}'),
        (o(hw + 1), '1304.10 00', 'B,SERS (ext)'),
        (o(hw + 2), '14163.10 00', 'B,1606'),
        (o(hw + 3), '0.30 00', 'NOP'),
    ]
    hw += 4
ROWS += [
    # ---- PDF p.11, exit and continuity ----
    ('014163.00', '14164.10 00', '1606 B,$+1.0'),
    ('014163.40', '14070.04 00', 'BD,1601'),
    ('014164.00', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('014164.40', '1301.10 00', 'B,SSW (ext)'),
    ('014165.00', '14165.44 00', 'BD,$+.32'),
    ('014165.40', '22737.32 10', 'LX,$X13,IC260  -UPDATE CONTINUITY CHECK.'),
    ('014166.00', '24522.32 B0', 'V+,$X13,BIT0'),
    ('014166.40', '22737.33 10', 'SX,$X13,IC260'),
    # ---- PDF p.12, TEST 1B ----
    ('014167.00', '24525.01 01', '1607 LVI,$X0,BIT3  -TEST 1B'),
    ('014167.40', '14202.01 D0', 'SVA,$X0,1608'),
    ('014170.00', '14207.41 01', 'LVI,$X0,160B2'),
    ('014170.40', '14203.01 D0', 'SVA,$X0,1609'),
    ('014171.00', '20.03 02', 'LCI,$X1,16'),
    ('014171.40', '24503.04 10', '1607B LX,$X2,1000'),
    ('014172.00', '22.00 80 000014.02 A0', 'TI,1,$X2,12.0'),
    ('014173.00', '0.30 00', 'NOP'),
    ('014173.40', '0.30 00', 'NOP'),
    ('014174.00', '14.00 80 000022.02 A0', 'TI,1,12.0,$X2'),
    ('014175.00', '22.05 70', 'SR,$X2,$X2'),
    ('014175.40', '0.30 00', 'NOP'),
    ('014176.00', '3.07 02', 'LCI,$X3,3.0  -DELETE ANY BITS IN 0 AND 1.'),
    ('014176.40', '24524.04 90', '1607A KV,$X2,BIT2'),
    ('014177.00', '14202.33 40', 'BZXH,1608'),
    ('014177.40', '24523.04 B0', 'V+,$X2,BIT1'),
    ('014200.00', '14176.46 48', 'CB,$X3,1607A'),
    ('014200.40', '1310.00 80', 'SIC,SEN (ext)  -BITS 0 AND 1 OF IX 2 CANT BE'),
    ('014201.00', '1304.10 00', 'B,SERS (ext)  -FORCED TO 00 CONDITION.'),
    ('014201.40', '14247.50 00', 'B,16010  -TERMINATE.'),
    ('014202.00', '0.04 90', '1608 KV,$X2,0'),
    ('014202.40', '14203.72 42', 'BXL,$+1.0'),
    ('014203.00', '0.10 00', '1609 $B,0'),
    ('014203.40', '1.03 08', 'C-I,$X1,1.0'),
    ('014204.00', '14247.70 42', 'BXCZ,16010'),
    ('014204.40', '14202.06 30', 'LV,$X3,1608'),
    ('014205.00', '1.07 0D', 'V-I,$X3,1.0  -SUB TO INCREMENT, BIT 24 IS 1.0'),
    ('014205.40', '14202.07 D0', 'SVA,$X3,1608'),
    ('014206.00', '2.01 05', 'V+I,$X0,2.0'),
    ('014206.40', '14203.01 D0', 'SVA,$X0,1609'),
    ('014207.00', '14171.50 00', 'B,1607B'),
]
# ---- PDF pp.12-13, error table 160B2: bits 48-63, four rows each ----
hw = 0o14207 * 2 + 1
for k in range(48, 64):
    pg = 12 if k < 53 else 13
    ROWS += [
        (o(hw), '1310.00 80', f'SIC,SEN (ext)  -BIT {k} OF MASK REG NOT ZERO. p.{pg}'),
        (o(hw + 1), '1304.10 00', 'B,SERS (ext)'),
        (o(hw + 2), '14247.50 00', 'B,16010'),
        (o(hw + 3), '0.30 00', 'NOP'),
    ]
    hw += 4
ROWS += [
    # ---- PDF p.13, exit and continuity ----
    ('014247.40', '14250.50 00', '16010 B,$+1.0'),
    ('014250.00', '14167.04 00', 'BD,1607'),
    ('014250.40', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('014251.00', '1301.10 00', 'B,SSW (ext)  -TO SSIP'),
    ('014251.40', '14252.04 00', 'BD,$+.32'),
    ('014252.00', '22737.32 10', 'LX,$X13,IC260  -UPDATE CONTINUITY CHECK.'),
    ('014252.40', '24523.32 B0', 'V+,$X13,BIT1'),
    ('014253.00', '22737.33 10', 'SX,$X13,IC260'),
    # ---- PDF p.114, the constants the run reads ----
    ('024502.00', '0.00 00 000000.00 00', 'I00Z XW,0,0,0,0 p.114'),
    ('024503.00', '1777777777777777777777', '1000 DD(BU,64,8) all ones p.114'),
    ('024521.00', '0000000000000000000000', 'BIT0-1.0: the last pool zero word p.114'),
    ('024522.00', '400000.00 00 000000.00 00', 'BIT0 p.114'),
    ('024523.00', '200000.00 00 000000.00 00', 'BIT1 p.114'),
    ('024524.00', '100000.00 00 000000.00 00', 'BIT2 p.114'),
    ('024525.00', '40000.00 00 000000.00 00', 'BIT3 p.114'),
    ('024552.00', '0000000010000000000000', 'BIT24 DD(BU) p.114'),
]

SYMBOLS = {
    'I60':    '014064.00',
    'I601':   '014070.00',
    'I602':   '014100.00',
    'I605':   '014103.40',
    'I603':   '014105.00',
    'I604':   '014106.40',
    'I60B1':  '014113.00',
    'I606':   '014163.00',
    'I607':   '014167.00',
    'I607B':  '014171.40',
    'I607A':  '014176.40',
    'I608':   '014202.00',
    'I609':   '014203.00',
    'I60B2':  '014207.40',
    'I6010':  '014247.40',
    'I00Z':   '024502.00',
    'I00O':   '024503.00',
    'BIT24':  '024552.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='160 TEST1AB '))
