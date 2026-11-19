#!/usr/bin/env python3
"""verify_ax4b_3_halfword_19bit_listing.py -- jb_ax4b "I-Box 4", routine
148's TEST 3 ("CHECK I-BOX HALF WORD 19 BIT MODIFICATION",
../decks/ax4b_3_halfword_19bit.strap) against the machine code the
listing prints beside each source line: PDF pp.139-140, octal
010623.40-010715.00; 148S1/148S2 on PDF p.152 (011310.00-011320.00);
148XW1 on PDF p.153 (011361.00); 148DMP on PDF p.154 (011373.00); and
100Z/1000 on PDF p.190 (013034.00-013035.00).  The sheets carry no
printed page number; cite PDF pages.

WHY IT MATTERS.  An I-box instruction with a 19-bit (half-word)
address, indexed by a value whose bits 19-23 are all ones:

    LR,$X0,0($X1)           0.00 71      (010626.00)  X1 = 148DMP+.63

Only bits 0-18 of the effective address may be used; bits 19-22 must
not leak into the J field ("GATING BIT nn SPUR." for each of X1-X15)
nor bit 23 elsewhere.

WHAT IT CHECKS: 121 rows and 7 symbols, every row on pp.139-140, the
16-row clear subroutine and the four data words.  The fourteen
"L(BU),$Xn / BRZ / SIC / B,SERS / B,I4831" groups for X2-X15 print the
same shape, 3.0 words apart from 010633.40, and are generated below;
each was read on the page images (pp.139-140).  Rows marked (ext) name
SSIP's SEN/SENO/SERS/SSW, IC248 or BIT19, given by SYN (or substitute
halts) at the printed addresses, so they check opcode and modifier bits
only.

PROVEN DISCRIMINATING, 2026-11-18, each injected into the assembler in
the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written (PYTHONDONTWRITEBYTECODE=1).  OBSERVED failure sets:
  DIR_INDEX_CODES "LR" 0b00111 -> 0b00110
      010626.00 LR,$X0,0($X1) -> '000000.00 61'                (1 row)
  MISC_CODES "Z" 0b100 -> 0b101
      the sixteen Z rows of 148S1, 011310.00-011317.40       (16 rows)
  The model-side injections are in the deck's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_3_halfword_19bit.strap").read())

ROWS = [
    # ---- PDF p.139 ----
    ('010623.40', '13035.02 10', 'I4830 LX,$X1,1000'),
    ('010624.00', '11373.03 10', 'SX,$X1,148DMP'),
    ('010624.40', '11320.00 80', 'SIC,148S2'),
    ('010625.00', '11310.10 00', 'B,148S1'),
    ('010625.40', '11361.02 10', 'LX,$X1,148XW1'),
    ('010626.00', '0.00 71', 'LR,$X0,0($X1)'),
    ('010626.40', '20.00 80 000000.20 50', 'L(BU),$X0'),
    ('010627.40', '10711.74 C0', 'BZRZ,I4831'),
    ('010630.00', '13034.02 30', 'LV,$X1,100Z'),
    ('010630.40', '21.00 80 000000.20 50', 'L(BU),$X1'),
    ('010631.40', '10633.74 C2', 'BRZ,$+2.0'),
    ('010632.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('010632.40', '1304.10 00', 'B,SERS (ext)  bit 22'),
    ('010633.00', '10711.50 00', 'B,I4831'),
]
for n in range(2, 16):
    w = 0o10633 + 3 * (n - 2)            # group start, .40
    pg = 139 if n < 9 else 140
    ROWS += [
        (f'{w:06o}.40', f'{0o20 + n:o}.00 80 000000.20 50', f'L(BU),$X{n} p.{pg}'),
        (f'{w + 1:06o}.40', f'{w + 3:o}.74 C2', f'BRZ,$+2.0 X{n} p.{pg}'),
        (f'{w + 2:06o}.00', '1310.00 80', f'SIC,SEN (ext) X{n}'),
        (f'{w + 2:06o}.40', '1304.10 00', f'B,SERS (ext) X{n}'),
        (f'{w + 3:06o}.00', '10711.50 00', f'B,I4831 X{n}'),
    ]
ROWS += [
    # ---- PDF p.140, after the X15 group ----
    ('010705.40', '11373.02 10', 'LX,$X1,148DMP'),
    ('010706.00', '21.03 70', 'SR,$X1,$X1'),
    ('010706.40', '10710.71 42', 'BXVZ,$+2.0'),
    ('010707.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('010707.40', '1304.10 00', 'B,SERS (ext)  bit 23'),
    ('010710.00', '10711.50 00', 'B,I4831'),
    ('010710.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('010711.00', '1304.10 00', 'B,SERS (ext)  bits 0-18'),
    ('010711.40', '10712.50 00', 'I4831 B,$+1.0'),
    ('010712.00', '10623.44 00', 'BD,I4830'),
    ('010712.40', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('010713.00', '1301.10 00', 'B,SSW (ext)'),
    ('010713.40', '10714.04 00', 'BD,$+.32'),
    ('010714.00', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('010714.40', '13077.32 B0', 'V+,$X13,BIT19 (ext)'),
    ('010715.00', '11306.33 10', 'SX,$X13,IC248 (ext)'),
    # ---- PDF p.152, 148S1 / 148S2 ----
    ('011310.00', '20.22 00', '148S1 Z,$X0'),
    ('011310.40', '21.22 00', 'Z,$X1'),
]
for n, loc in zip([3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 2],
                  ['011311.00', '011311.40', '011312.00', '011312.40',
                   '011313.00', '011313.40', '011314.00', '011314.40',
                   '011315.00', '011315.40', '011316.00', '011316.40',
                   '011317.00', '011317.40']):
    ROWS.append((loc, f'{16 + n:o}.22 00', f'Z,$X{n}'))
ROWS += [
    ('011320.00', '0.10 00', '148S2 $B,0'),
    # ---- PDF p.153 / p.154 / p.190 ----
    ('011361.00', '11373.77 00 000000.00 00', '148XW1 XW,148DMP+.63,0,0'),
    ('011373.00', '0.00 00 000000.00 00', '148DMP XW,0,0,0'),
    ('013034.00', '0.00 00 000000.00 00', '100Z XW,0,0,0,0'),
    ('013035.00', '1777777777777777777777', '1000 DD(BU,64,8) all ones'),
]

SYMBOLS = {
    'I4830':  '010623.40',
    'I4831':  '010711.40',
    'I48S1':  '011310.00',
    'I48S2':  '011320.00',
    'I48XW1': '011361.00',
    'I48DMP': '011373.00',
    'I000':   '013035.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST3 '))
