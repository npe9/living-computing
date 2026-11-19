#!/usr/bin/env python3
"""verify_ax4b_148_immediate_indexed_listing.py -- jb_ax4b "I-Box 4",
routine 148's "CHECK INDEXING IMMEDIATE LOAD" block
(../decks/ax4b_148_immediate_indexed.strap) against the machine code
the listing prints beside each source line: PDF pp.146-148, octal
011067.00-011165.40, and the bit table on PDF p.191, 013054.00-
013103.00.  The sheets carry no printed page number; cite PDF pages.

WHY IT MATTERS.  This is the FIRST IBM listing row this project has
with a nonzero index field on an immediate VFL operation:

    LI(BU,64,8),0($X3)        0.00 83 400000.20 50     (011072.00)

"83": bits 24-27 = 1000 (the VFL/connective full-word tag), bits 28-31
= 0011, I = 3.  "400000.20": bits 32-34 = 100, P = 4, immediate.  Before
it, the indexed-immediate rule (decks/vfl_immediate_indexed.strap) rested
on the Reference Manual alone: 936 immediates in 812 assembled decks,
none indexed.

WHAT IT CHECKS: 149 rows and 8 symbols.  21 driver rows (p.146), the
24-entry error table (4 half-words per entry, 96 rows, 011102.00-
011161.40 on pp.146-148), 8 tail rows (p.148) and BIT0-BIT23 (24 XW
rows, p.191).  Every one of the 96 table rows prints the same code
(1310.00 80 / 1304.10 00 / 11077.10 00 / 0.30 00), read on each of the
three page images, so they are generated below rather than spelled
out; the locations are 011102.00 + 2k words for bit k, as printed.
Rows marked (ext) name SSIP's SEN/SENO/SERS/SSW or IC248, given by SYN
(or substitute halts) at the printed addresses, so they check opcode
and modifier bits only.  BIT0 and BIT23 ARE transcribed here (p.191),
so LVI,$X1,BIT0 and V+,$X13,BIT23 are real address checks.

PROVEN DISCRIMINATING, 2026-11-18, each injected into strap_asm.py in
the worktree, run, restored from a saved copy (cmp IDENTICAL),
__pycache__ removed.  OBSERVED failure sets:

  enc_vfl_full drops i1 (always 0)
      011072.00 LI(BU,64,8),0($X3) -> '000000.00 80 400000.20 50'
                                                       (1 row)
  enc_vfl_full writes the P field as 0 (immediate lost)
      011072.00 LI(BU,64,8),0($X3) -> '000000.00 83 000000.20 50'
                                                       (1 row)
  The model-side injections (bit 0 and bit 18 named by SEN) are in the
  deck's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_148_immediate_indexed.strap").read())

ROWS = [
    # ---- PDF p.146, the driver ----
    ('011067.00', '13054.03 01', 'I4841 LVI,$X1,BIT0'),
    ('011067.40', '11102.05 01', 'LVI,$X2,I4844'),
    ('011070.00', '30.03 02', 'LCI,$X1,24'),
    ('011070.40', '11076.45 D0', 'I48412 SVA,$X2,I4842'),
    ('011071.00', '11071.43 D0', 'SVA,$X1,$+.32'),
    ('011071.40', '0.06 30', 'LV,$X3,0'),
    ('011072.00', '0.00 83 400000.20 50', 'LI(BU,64,8),0($X3)  I=3, P=4'),
    ('011073.00', '0.30 00', 'NOP'),
    ('011073.40', '0.30 00', 'NOP'),
    ('011074.00', '0.30 00', 'NOP'),
    ('011074.40', '11.06 10', 'LX,$X3,$R'),
    ('011075.00', '11075.43 D0', 'SVA,$X1,$+.32'),
    ('011075.40', '0.06 90', 'KV,$X3,0'),
    ('011076.00', '11077.32 C2', 'BXE,$+1.0'),
    ('011076.40', '0.10 00', 'I4842 $B,0'),
    ('011077.00', '1.03 08', 'I4843 C-I,$X1,1'),
    ('011077.40', '11162.30 42', 'BXCZ,I4844A'),
    ('011100.00', '1.03 05', 'V+I,$X1,1.0'),
    ('011100.40', '2.05 05', 'V+I,$X2,2.0'),
    ('011101.00', '11070.44 00', 'BD,I48412   bit 18 set'),
    ('011101.40', '0.30 00', 'CNOP        emits one NOP'),
]

# ---- the error table, PDF p.146 (bits 0-6), p.147 (7-15), p.148 (16-23)
for k in range(24):
    w = 0o11102 + 2 * k
    pg = 146 if k < 7 else 147 if k < 16 else 148
    ROWS += [
        (f'{w:06o}.00', '1310.00 80', f'SIC,SEN  bit {k} (ext) p.{pg}'),
        (f'{w:06o}.40', '1304.10 00', f'B,SERS   bit {k} (ext) p.{pg}'),
        (f'{w + 1:06o}.00', '11077.10 00', f'B,I4843  bit {k} p.{pg}'),
        (f'{w + 1:06o}.40', '0.30 00', f'NOP      bit {k} p.{pg}'),
    ]

ROWS += [
    # ---- PDF p.148, the exit and the continuity update ----
    ('011162.00', '11163.10 00', 'I4844A B,$+1.0'),
    ('011162.40', '11067.04 00', 'BD,I4841'),
    ('011163.00', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('011163.40', '1301.10 00', 'B,SSW (ext)'),
    ('011164.00', '11164.44 00', 'BD,$+.32'),
    ('011164.40', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('011165.00', '13103.32 B0', 'V+,$X13,BIT23'),
    ('011165.40', '11306.33 10', 'SX,$X13,IC248 (ext)'),
]

# ---- PDF p.191, BIT0-BIT23, value fields as printed ----
BITS = ['400000.00', '200000.00', '100000.00', '40000.00', '20000.00',
        '10000.00', '4000.00', '2000.00', '1000.00', '400.00', '200.00',
        '100.00', '40.00', '20.00', '10.00', '4.00', '2.00', '1.00',
        '0.40', '0.20', '0.10', '0.04', '0.02', '0.01']
for k, v in enumerate(BITS):
    ROWS.append((f'{0o13054 + k:06o}.00', f'{v} 00 000000.00 00', f'BIT{k} XW p.191'))

SYMBOLS = {
    'I4841':  '011067.00',
    'I48412': '011070.40',
    'I4842':  '011076.40',
    'I4843':  '011077.00',
    'I4844':  '011102.00',
    'I4844A': '011162.00',
    'BIT0':   '013054.00',
    'BIT23':  '013103.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 I4841 '))
