#!/usr/bin/env python3
"""verify_ax4b_5i_prog_ix_x0_listing.py -- jb_ax4b "I-Box 4", routine
148's TEST 5I ("PROG IX WITH IX 0", ../decks/ax4b_5i_prog_ix_x0.strap)
against the machine code the listing prints beside each source line:
PDF p.152, octal 011270.00-011320.00 (TEST 5I, routine 148's
continuity update and check, IC248/ICK248, the clear-all-index
subroutine 148S1 and its return 148S2), and the constants 148K25 and
148XW4 on PDF p.153.  The sheets carry no printed page number; cite PDF
pages.

WHY IT MATTERS.  "NOT PROG IX WITH I FLD ZERO USES IX 0 TO GENERATE
EFFECT ADR": $X0 is loaded with a nonzero value (148XW4 -> 148K25,
count 1) and then

    L(BU),0                 0.00 80 000000.20 50     (011271.40)

with I = 0 must load word 0 (zero), not word 148K25.

WHAT IT CHECKS: 48 rows and 6 symbols, every row on p.152 plus the two
p.153 words.  Rows marked (ext) name SSIP's SEN/SENO/SERS/SSW, BIT3 or
I50, given by SYN (or substitute halts) at the printed addresses, so
they check opcode and modifier bits only.  IC248 and ICK248 ARE
transcribed here, so the continuity rows are real address checks.

PROVEN DISCRIMINATING, 2026-11-18, each injected into the assembler in
the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written (PYTHONDONTWRITEBYTECODE=1).  OBSERVED failure sets:
  MISC_CODES "Z" 0b100 -> 0b101
      the sixteen Z rows of 148S1, 011310.00-011317.40       (16 rows)
  (enc_vfl_full dropping i1, enc_fp's unnorm and LR's code each leave
  this file passing: it has no indexed VFL, FP or LR row.)
  The model-side injections are in the deck's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_5i_prog_ix_x0.strap").read())

ROWS = [
    ('011270.00', '11320.00 80', 'I4848 SIC,148S2'),
    ('011270.40', '11310.10 00', 'B,148S1'),
    ('011271.00', '11364.00 10', 'LX,$X0,148XW4'),
    ('011271.40', '0.00 80 000000.20 50', 'L(BU),0   I=0'),
    ('011272.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('011273.00', '1304.34 C0', 'BZRZ,SERS (ext)'),
    ('011273.40', '11274.50 00', 'B,$+1.0'),
    ('011274.00', '11270.04 00', 'BD,I4848'),
    ('011274.40', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('011275.00', '1301.10 00', 'B,SSW (ext)'),
    ('011275.40', '11276.04 00', 'BD,$+.32'),
    ('011276.00', '11306.32 10', 'LX,$X13,IC248'),
    ('011276.40', '34.33 50', 'SC,$X13,$X12'),
    ('011277.00', '13057.30 B0', 'V+,$X12,BIT3 (ext)'),
    ('011277.40', '34.32 50', 'LC,$X13,$X12'),
    ('011300.00', '11306.33 10', 'SX,$X13,IC248'),
    ('011300.40', '11306.32 10', 'LX,$X13,IC248'),
    ('011301.00', '11307.32 90', 'KV,$X13,ICK248'),
    ('011301.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('011302.00', '1304.32 C0', 'BZXE,SERS (ext)'),
    ('011302.40', '35.33 50', 'SC,$X13,$X13'),
    ('011303.00', '11307.30 10', 'LX,$X12,ICK248'),
    ('011303.40', '34.31 50', 'SC,$X12,$X12'),
    ('011304.00', '34.32 90', 'KV,$X13,$X12'),
    ('011304.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('011305.00', '1304.32 C0', 'BZXE,SERS (ext)'),
    ('011305.40', '11424.04 00', 'BD,I50 (ext)'),
    ('011306.00', '0.00 00 000000.00 00', 'IC248 XW,0,0,0'),
    ('011307.00', '777777.77 0F 000000.00 00', 'ICK248 XW,(8)777777.77,(8)740000,0'),
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
    # ---- PDF p.153 ----
    ('011352.00', '123456.70 00 000000.00 00', '148K25 XW,(8)123456.70'),
    ('011364.00', '11352.00 00 000020.00 00', '148XW4 XW,148K25,1,0'),
]

SYMBOLS = {
    'I4848':  '011270.00',
    'IC248':  '011306.00',
    'I48S1':  '011310.00',
    'I48S2':  '011320.00',
    'I48K25': '011352.00',
    'I48XW4': '011364.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST5I '))
