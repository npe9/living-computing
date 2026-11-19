#!/usr/bin/env python3
"""verify_ax4b_4_fp_18bit_listing.py -- jb_ax4b "I-Box 4", routine 148's
TEST 4 ("18 BIT FLOATING POINT MODIFICATION", ../decks/ax4b_4_fp_18bit.strap)
against the machine code the listing prints beside each source line:
PDF p.141, octal 010715.40-010736.00; the constants 148K24, 148XW2,
148XW3 and 148ER1 on PDF p.153; and BIT13 on PDF p.191.  The sheets
carry no printed page number; cite PDF pages.

WHY IT MATTERS.  Floating-point addresses are 18 bits (word only); the
index value's bits 18-23 must not reach them:

    L(N),0($X1)             0.00 61      (010722.00)  X1 = BIT13+.32
    L(U),0($X1)             0.40 61      (010726.00)  X1 = 148K24+.63

WHAT IT CHECKS: 39 rows and 7 symbols, every row on p.141 plus the five
data words.  Rows marked (ext) name SSIP's SEN/SENO/SERS/SSW, IC248,
BIT20 or I4833, given by SYN (or substitute halts) at the printed
addresses, so they check opcode and modifier bits only.  BIT13, 148K24,
148XW2/3 and 148ER1 are transcribed, so their rows are address checks;
148XW2/3's values (13071.40, 11351.77) check the "+.32"/"+.63" bit
arithmetic of the XW value field.

PROVEN DISCRIMINATING, 2026-11-18, each injected into the assembler in
the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written (PYTHONDONTWRITEBYTECODE=1).  OBSERVED failure sets:
  enc_fp writes the unnormalized bit as 0
      010726.00 L(U),0($X1) -> '000000.00 61'                  (1 row)
  The model-side injections are in the deck's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_4_fp_18bit.strap").read())

ROWS = [
    ('010715.40', '11372.02 10', 'LX,$X1,148ER1'),
    ('010716.00', '10721.70 42', 'BXCZ,I4832'),
    ('010716.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('010717.00', '1304.10 00', 'B,SERS (ext)'),
    ('010717.40', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('010720.00', '13100.32 B0', 'V+,$X13,BIT20 (ext)'),
    ('010720.40', '11306.33 10', 'SX,$X13,IC248 (ext)'),
    ('010721.00', '10736.50 00', 'B,I4833 (ext)'),
    ('010721.40', '11362.02 10', 'I4832 LX,$X1,148XW2'),
    ('010722.00', '0.00 61', 'L(N),0($X1)'),
    ('010722.40', '10.02 10', 'LX,$X1,$L'),
    ('010723.00', '13071.02 90', 'KV,$X1,BIT13'),
    ('010723.40', '10725.73 42', 'BXH,$+2.0'),
    ('010724.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('010724.40', '1304.10 00', 'B,SERS (ext)'),
    ('010725.00', '10732.50 00', 'B,I48321'),
    ('010725.40', '11363.02 10', 'LX,$X1,148XW3'),
    ('010726.00', '0.40 61', 'L(U),0($X1)'),
    ('010726.40', '10.02 10', 'LX,$X1,$L'),
    ('010727.00', '11351.02 90', 'KV,$X1,148K24'),
    ('010727.40', '10730.72 C2', 'BXE,$+1.0'),
    ('010730.00', '10731.50 00', 'B,$+1.32'),
    ('010730.40', '11351.03 90', 'KC,$X1,148K24'),
    ('010731.00', '10732.72 C2', 'BXE,$+1.32'),
    ('010731.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('010732.00', '1304.10 00', 'B,SERS (ext)'),
    ('010732.40', '10733.50 00', 'I48321 B,$+1.0'),
    ('010733.00', '10721.44 00', 'BD,I4832'),
    ('010733.40', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('010734.00', '1301.10 00', 'B,SSW (ext)'),
    ('010734.40', '10735.04 00', 'BD,$+.32'),
    ('010735.00', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('010735.40', '13100.32 B0', 'V+,$X13,BIT20 (ext)'),
    ('010736.00', '11306.33 10', 'SX,$X13,IC248 (ext)'),
    # ---- PDF p.153 ----
    ('011351.00', '123456.76 02 471340.00 00', '148K24'),
    ('011362.00', '13071.40 00 000000.00 00', '148XW2 XW,BIT13+.32,0,0'),
    ('011363.00', '11351.77 00 000000.00 00', '148XW3 XW,148K24+.63,0,0'),
    ('011372.00', '0.00 00 000000.00 00', '148ER1 XW,0,0,0'),
    # ---- PDF p.191 ----
    ('013071.00', '20.00 00 000000.00 00', 'BIT13 XW'),
]

SYMBOLS = {
    'I4832':  '010721.40',
    'I48321': '010732.40',
    'I48K24': '011351.00',
    'I48XW2': '011362.00',
    'I48XW3': '011363.00',
    'I48ER1': '011372.00',
    'BIT13':  '013071.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST4 '))
