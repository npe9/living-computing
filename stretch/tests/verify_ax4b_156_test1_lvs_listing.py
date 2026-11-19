#!/usr/bin/env python3
"""verify_ax4b_156_test1_lvs_listing.py -- jb_ax4b "I-Box 4", routine
1256 ("LVE AND LVS CHECK."), its prologue and TEST 1
(../decks/ax4b_156_test1_lvs.strap) against the machine code the
listing prints beside each source line: PDF pp.173-181, octal
012272.00-012531.40; IC256 (p.189, 012774.00); 156K1 and 1000 (p.190,
012776.00, 013035.00); BIT0-BIT15 (p.191, 013054.00-013073.00).  The
sheets carry no printed page number; cite PDF pages.

WHY IT MATTERS.  IBM's own test of LOAD VALUE WITH SUM, which until now
had only the Reference Manual (printed p.28) behind it.  The mask rows:

    LVS,$X15,$X0                               400000.37 0B   (012305.40)
    LVS,$X0,$0,$1,...,$15                      777774.01 0B   (012362.00)
    $LVS,$X1,0                                 400000.03 0B   (012523.40)

The last one's "0" is index register 0, so its mask is bit 0, which
SVA,$X6,$+.32 then zeroes at run time.

WHAT IT CHECKS: 337 rows and 9 symbols.  The prologue (6 rows,
p.173); TEST 1A (15 LX, the X15 block of 5, fifteen LVS/KV/SIC/BZXE
blocks of 4, 8 exit and continuity rows: 88 rows, pp.173-175); TEST 1B
(16 LX, sixteen 12-row LVS-of-all blocks, the 8-row zero-mask check,
8 exit and continuity rows: 224 rows, pp.176-181); IC256, 156K1, 1000
and BIT0-BIT15 (19 rows).  The repeated blocks print the same code
apart from the register number, so they are generated below from the
printed pattern; every generated row was then compared with the page
images (pp.173-181), row for row.  Rows marked (ext) name SSIP's
SEN/SENO/SERS/SSW/RET/DPET13/IDF1, placed at the addresses PDF p.193's
SYN table prints, so they check opcode and modifier bits only.

PROVEN DISCRIMINATING, measured 2026-11-19: injected into the assembler
in the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written.  OBSERVED failure set:
  the LVS encoder shifts each mask bit one place right ("1 << (17 - n)"
    for "1 << (18 - n)") -> 33 FAIL, exactly the 33 LVS rows: TEST 1A's
    16 (e.g. 012305.40 '200000.37 0B' vs '400000.37 0B'), TEST 1B's 16
    LVS-of-all rows and the $LVS at 012523.40.  Nothing else moves.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_156_test1_lvs.strap").read())


def o(hw):
    return f'{hw // 2:06o}.{"40" if hw % 2 else "00"}'


ROWS = [
    # ---- PDF p.173, the prologue ----
    ('012272.00', '12275.02 10', 'I56 LX,$X1,156ID  -UPDATE IDENT.'),
    ('012272.40', '1437.03 10', 'SX,$X1,DPET13 (ext)'),
    ('012273.00', '1306.40 80', 'SIC,RET (ext)'),
    ('012273.40', '1443.10 00', 'B,IDF1 (ext)  -PRINT ID.'),
    ('012274.00', '12774.22 00', 'Z,IC256'),
    ('012274.40', '12276.04 00', 'BD,I561'),
]
# ---- PDF p.173, TEST 1A: LX,$Xk,BITk, k = 0..14 ----
hw = 0o12276 * 2
for k in range(15):
    ROWS.append((o(hw), f'{0o13054 + k:o}.{2 * k:02o} 10', f'LX,$X{k},BIT{k} p.173'))
    hw += 1
ROWS += [
    ('012305.40', '400000.37 0B', 'LVS,$X15,$X0'),
    ('012306.00', '13054.36 90', 'KV,$X15,BIT0'),
    ('012306.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('012307.00', '1304.32 C0', 'BZXE,SERS (ext)  IX 0'),
    ('012307.40', '13073.36 10', 'LX,$X15,BIT15'),
]
hw = 0o12310 * 2
for k in range(1, 16):
    pg = 173 if k < 3 else 174 if k < 11 else 175
    ROWS += [
        (o(hw), f'{0o400000 >> k:o}.01 0B', f'LVS,$X0,$X{k} p.{pg}'),
        (o(hw + 1), f'{0o13054 + k:o}.00 90', f'KV,$X0,BIT{k}'),
        (o(hw + 2), '1310.00 80', 'SIC,SEN (ext)'),
        (o(hw + 3), '1304.32 C0', f'BZXE,SERS (ext)  IX {k}'),
    ]
    hw += 4
ROWS += [
    # ---- PDF p.175, exit and continuity ----
    ('012346.00', '12347.10 00', 'B,$+1.0'),
    ('012346.40', '12276.04 00', 'BD,I561'),
    ('012347.00', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('012347.40', '1301.10 00', 'B,SSW (ext)  -TO SSIP.'),
    ('012350.00', '12350.44 00', 'BD,$+.32'),
    ('012350.40', '12774.32 10', 'LX,$X13,IC256'),
    ('012351.00', '13054.32 B0', 'V+,$X13,BIT0'),
    ('012351.40', '12774.33 10', 'SX,$X13,IC256'),
]
# ---- PDF p.176, TEST 1B: LX,$Xk,BITk, k = 0..15 ----
hw = 0o12352 * 2
for k in range(16):
    ROWS.append((o(hw), f'{0o13054 + k:o}.{2 * k:02o} 10', f'LX,$X{k},BIT{k} p.176'))
    hw += 1
# ---- PDF pp.176-181, the sixteen LVS-of-all groups ----
for k in range(16):
    pg = (176 if k < 2 else 177 if k < 5 else 178 if k < 8 else
          179 if k < 11 else 180 if k < 14 else 181)
    ix = f'{0o20 + k:o}'
    ROWS += [
        (o(hw), f'777774.{2 * k + 1:02o} 0B', f'LVS,$X{k},$0,...,$15 p.{pg}'),
        (o(hw + 1), f'12776.{2 * k:02o} 90', f'KV,$X{k},156K1'),
        (o(hw + 2), '1310.00 80', 'SIC,SEN (ext)'),
        (o(hw + 3), '1304.32 C0', f'BZXE,SERS (ext)  IX {k:02d}'),
        (o(hw + 4), f'{ix}.{2 * k:02o} 10', f'LX,$X{k},$X{k}'),
        (o(hw + 5), '1310.00 80', 'SIC,SEN (ext)'),
        (o(hw + 6), '1304.30 40', 'BZXCZ,SERS (ext)  COUNT FIELD'),
        (o(hw + 7), f'{ix}.{2 * k + 1:02o} 70', f'SR,$X{k},$X{k}'),
        (o(hw + 8), f'{ix}.{2 * k:02o} 10', f'LX,$X{k},$X{k}'),
        (o(hw + 9), '1310.00 80', 'SIC,SEN (ext)'),
        (o(hw + 10), '1304.31 40', 'BZXVZ,SERS (ext)  REFILL FIELD'),
        (o(hw + 11), f'{0o13054 + k:o}.{2 * k:02o} 10', f'LX,$X{k},BIT{k}'),
    ]
    hw += 12
ROWS += [
    # ---- PDF p.181, the zero mask, exit and continuity ----
    ('012522.00', '13035.02 10', 'LX,$X1,1000  -CHK ZEROS IN 0-15 CLRS IX REG.'),
    ('012522.40', '26.22 00', 'Z,$X6'),
    ('012523.00', '12523.55 D0', 'SVA,$X6,$+.32'),
    ('012523.40', '400000.03 0B', '$LVS,$X1,0'),
    ('012524.00', '21.00 10', 'LX,$X0,$X1'),
    ('012524.40', '12526.31 42', 'BXVZ,$+1.32'),
    ('012525.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('012525.40', '1304.10 00', 'B,SERS (ext)'),
    ('012526.00', '12527.10 00', 'B,$+1.0'),
    ('012526.40', '12352.04 00', 'BD,I562'),
    ('012527.00', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('012527.40', '1301.10 00', 'B,SSW (ext)  -TO SSIP.'),
    ('012530.00', '12530.44 00', 'BD,$+.32'),
    ('012530.40', '12774.32 10', 'LX,$X13,IC256'),
    ('012531.00', '13055.32 B0', 'V+,$X13,BIT1'),
    ('012531.40', '12774.33 10', 'SX,$X13,IC256'),
    # ---- PDF pp.189-191, constants ----
    ('012774.00', '0.00 00 000000.00 00', 'IC256 XW,0,0,0 p.189'),
    ('012776.00', '777774.00 00 000000.00 00', '156K1 XW,(8)777774.00,0,0 p.190'),
    ('013035.00', '1777777777777777777777', '1000 DD(BU,64,8) all ones p.190'),
]
BITS = ['400000.00', '200000.00', '100000.00', '40000.00', '20000.00',
        '10000.00', '4000.00', '2000.00', '1000.00', '400.00', '200.00',
        '100.00', '40.00', '20.00', '10.00', '4.00']
for k, v in enumerate(BITS):
    ROWS.append((f'{0o13054 + k:06o}.00', f'{v} 00 000000.00 00', f'BIT{k} XW p.191'))

SYMBOLS = {
    'I56':    '012272.00',
    'I561':   '012276.00',
    'I562':   '012352.00',
    'IC256':  '012774.00',
    'I56K1':  '012776.00',
    'I000':   '013035.00',
    'BIT0':   '013054.00',
    'BIT15':  '013073.00',
    'RET':    '001306.40',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='156 TEST1 '))
