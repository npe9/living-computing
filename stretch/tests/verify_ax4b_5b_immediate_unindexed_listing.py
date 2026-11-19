#!/usr/bin/env python3
"""verify_ax4b_5b_immediate_unindexed_listing.py -- jb_ax4b "I-Box 4",
routine 148's TEST 5B ("CHKS P FIELD OF 100" / "IMMEDIATE MODE, Z TO
LA TEST", ../decks/ax4b_5b_immediate_unindexed.strap) against the
machine code the listing prints beside each source line: PDF pp.143-
145, octal 010767.40-011066.40, and the bit table on PDF p.191,
013054.00-013103.00.  The sheets carry no printed page number; cite PDF
pages.

WHY IT MATTERS.  The unindexed companion of routine 148's indexed walk:

    LI(BU,64,8),0               0.00 80 400000.20 50     (010773.40)

I = 0, P = 4 (immediate), and a FULL-WORD instruction at an ODD
half-word ("F" in the margin), its address field written at run time by
"SVA,$X3,$+.32" (10773.47 D0) -- an SVA aimed at the next half-word,
i.e. INTO the first half of the full-word instruction about to run.

WHAT IT CHECKS: 150 rows and 8 symbols.  22 driver rows (p.143), the
24-entry error table (4 half-words per entry, 96 rows, 011003.00-
011062.40 on pp.143-145), 8 tail rows (p.145) and BIT0-BIT23 (24 XW
rows, p.191; the sheet routine 148's verifier also checks, kept so this
file stands alone).  Every one of the 96 table rows prints the same
code (1310.00 80 / 1304.10 00 / 11000.50 00 / 0.30 00), read on each
of the three page images, so they are generated below rather than
spelled out; the locations are 011003.00 + 2k words for bit k, as
printed.  Rows marked (ext) name SSIP's SEN/SENO/SERS/SSW or IC248,
given by SYN (or substitute halts) at the printed addresses, so they
check opcode and modifier bits only.  The CNOP at 011002.40 prints no
code of its own (BD,I4837 fills that half-word, I4839 is 011003.00).

PROVEN DISCRIMINATING, 2026-11-18, each injected into the assembler in
the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written (PYTHONDONTWRITEBYTECODE=1).  OBSERVED failure sets:
  enc_vfl_full writes the P field as 0 (immediate lost)
      010773.40 LI(BU,64,8),0 -> '000000.00 80 000000.20 50'   (1 row)
  MISC_CODES "Z" 0b100 -> 0b101
      010771.00 Z,$X0 -> '000020.26 00'                        (1 row)
  The model-side injections are in the deck's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_5b_immediate_unindexed.strap").read())

ROWS = [
    # ---- PDF p.143, the driver ----
    ('010767.40', '13054.03 01', 'I4836A LVI,$X1,BIT0'),
    ('010770.00', '11003.05 01', 'LVI,$X2,I4839'),
    ('010770.40', '30.03 02', 'LCI,$X1,24'),
    ('010771.00', '20.22 00', 'I4837 Z,$X0'),
    ('010771.40', '11000.05 D0', 'SVA,$X2,I4838'),
    ('010772.00', '10772.43 D0', 'SVA,$X1,$+.32'),
    ('010772.40', '0.06 10', 'LX,$X3,0'),
    ('010773.00', '10773.47 D0', 'SVA,$X3,$+.32'),
    ('010773.40', '0.00 80 400000.20 50', 'LI(BU,64,8),0  I=0, P=4, odd half'),
    ('010774.40', '0.30 00', 'NOP'),
    ('010775.00', '0.30 00', 'NOP'),
    ('010775.40', '0.30 00', 'NOP'),
    ('010776.00', '11.06 10', 'LX,$X3,$R'),
    ('010776.40', '10777.03 D0', 'SVA,$X1,$+.32'),
    ('010777.00', '0.06 90', 'KV,$X3,0'),
    ('010777.40', '11000.72 C2', 'BXE,$+1.0'),
    ('011000.00', '0.10 00', 'I4838 $B,0'),
    ('011000.40', '1.03 08', 'I4838A C-I,$X1,1'),
    ('011001.00', '11063.30 42', 'BXCZ,I4840'),
    ('011001.40', '1.03 05', 'V+I,$X1,1.0'),
    ('011002.00', '2.05 05', 'V+I,$X2,2.0'),
    ('011002.40', '10771.04 00', 'BD,I4837'),
]

# ---- the error table, PDF p.143 (bits 0-5), p.144 (6-14), p.145 (15-23)
for k in range(24):
    w = 0o11003 + 2 * k
    pg = 143 if k < 6 else 144 if k < 15 else 145
    ROWS += [
        (f'{w:06o}.00', '1310.00 80', f'SIC,SEN   bit {k} (ext) p.{pg}'),
        (f'{w:06o}.40', '1304.10 00', f'B,SERS    bit {k} (ext) p.{pg}'),
        (f'{w + 1:06o}.00', '11000.50 00', f'B,I4838A  bit {k} p.{pg}'),
        (f'{w + 1:06o}.40', '0.30 00', f'NOP       bit {k} p.{pg}'),
    ]

ROWS += [
    # ---- PDF p.145, the exit and the continuity update ----
    ('011063.00', '11064.10 00', 'I4840 B,$+1.0'),
    ('011063.40', '10767.44 00', 'BD,I4836A'),
    ('011064.00', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('011064.40', '1301.10 00', 'B,SSW (ext)'),
    ('011065.00', '11065.44 00', 'BD,$+.32'),
    ('011065.40', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('011066.00', '13102.32 B0', 'V+,$X13,BIT22'),
    ('011066.40', '11306.33 10', 'SX,$X13,IC248 (ext)'),
]

# ---- PDF p.191, BIT0-BIT23, value fields as printed ----
BITS = ['400000.00', '200000.00', '100000.00', '40000.00', '20000.00',
        '10000.00', '4000.00', '2000.00', '1000.00', '400.00', '200.00',
        '100.00', '40.00', '20.00', '10.00', '4.00', '2.00', '1.00',
        '0.40', '0.20', '0.10', '0.04', '0.02', '0.01']
for k, v in enumerate(BITS):
    ROWS.append((f'{0o13054 + k:06o}.00', f'{v} 00 000000.00 00', f'BIT{k} XW p.191'))

SYMBOLS = {
    'I4836A': '010767.40',
    'I4837':  '010771.00',
    'I4838':  '011000.00',
    'I4838A': '011000.40',
    'I4839':  '011003.00',
    'I4840':  '011063.00',
    'BIT0':   '013054.00',
    'BIT22':  '013102.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST5B '))
