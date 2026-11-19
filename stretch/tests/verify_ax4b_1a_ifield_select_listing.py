#!/usr/bin/env python3
"""verify_ax4b_1a_ifield_select_listing.py -- jb_ax4b "I-Box 4",
routine 148's TEST 1A ("I-FLD IX SELN.", ../decks/ax4b_1a_ifield_select.strap)
against the machine code the listing prints beside each source line:
PDF pp.114-120, octal 007441.00-007670.40; 148S1/148S2 on PDF p.152
(011310.00-011320.00); the CNOP and 148K0-148K15 on PDF p.153
(011320.40-011340.40); 148ER1 (p.153, 011372.00), 148DMP (p.154,
011373.00) and 100VO (p.190, 013036.00).  The sheets carry no printed
page number; cite PDF pages.

WHY IT MATTERS.  The I field of every index register, 0-15, on a
half-word store whose index VALUE is the store's own target:

    SX,$X5,0($X5)          0.13 15          (007530.00)

and the I = 0 case, where the same store must NOT be indexed:

    SX,$X0,0($X0)          0.01 10          (007454.00)

WHAT IT CHECKS: 341 rows and 10 symbols.  I481 and the IX 0 block (31
rows, p.114), the fifteen IX 1-15 blocks (15 rows each, 225 rows), the
four exits and continuity updates (8 rows each, 32 rows), 148S1/148S2
(17 rows), the CNOP fill and 148K0-148K15 (33 rows), 148ER1, 148DMP,
100VO (3 rows).  The fifteen IX blocks print the same code apart from
the register number, the 148Kn address and the BZRZ target, so they are
generated below from the printed pattern; every generated row was then
compared with the page images (pp.114-120), row for row.  The first
draft of the template had the BZRZ target one word short (the block's
own LX,$X1,100VO); the oracle failed all fifteen rows, and the images
show the branch skips to the NEXT block (7471.34 C0 at 007466.40), so
the template was wrong, not the deck.  The block for
IX n starts at 007461.00 + 8(n-1) words + 4 words per completed group
(the exits); the printed LX codes are 113(21+n).(2n) 10, the SX codes
0.(2n+1) 1n (hex n).  Rows marked (ext) name SSIP's SEN/SENO/SERS/SSW or
IC248/BITk, given by SYN (or substitute halts) at the printed
addresses, so they check opcode and modifier bits only.  The CNOP at
011320.40 prints "0.30 00" (it fills a half-word); 148Kn's NOPs print
the same.

PROVEN DISCRIMINATING, measured 2026-11-19; each
injected into the assembler in the worktree, run, restored from a saved
copy (cmp IDENTICAL), no __pycache__ written.  OBSERVED failure sets:
  enc_dir_index writes the I field as 0 -> 15 FAIL, exactly the fifteen
    "SX,$Xn,0($Xn)" rows, n = 1..15 (007464.00 ... 007660.00), each
    assembled with I = 0 where the listing prints n (e.g. '000000.03 10'
    vs '000000.03 11').  n = 0 is not caught: its I is 0 either way.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_1a_ifield_select.strap").read())


def o(w, h=0):
    return f'{w:06o}.{"40" if h else "00"}'


ROWS = [
    # ---- PDF p.114, I481 and the IX 0 block ----
    ('007441.00', '11372.22 00', 'I481 Z,148ER1'),
    ('007441.40', '11320.00 80', 'I482 SIC,148S2'),
    ('007442.00', '11310.10 00', 'B,148S1'),
]
hw = 0o7442 * 2 + 1
for n in range(16):
    ROWS.append((o(hw // 2, hw % 2), f'{0o11321 + n:o}.{2 * n:02o} 10', f'LX,$X{n},148K{n}'))
    hw += 1
for code, note in [('11373.22 00', 'Z,148DMP'), ('0.30 00', 'NOP'),
                   ('0.30 00', 'NOP'), ('0.01 10', 'SX,$X0,0($X0)  I = 0'),
                   ('0.30 00', 'NOP'), ('0.30 00', 'NOP')]:
    ROWS.append((o(hw // 2, hw % 2), code, note))
    hw += 1
ROWS += [
    ('007455.40', '11373.00 80 000000.20 50', 'L(BU),148DMP'),
    ('007456.40', '7461.34 C2', 'BRZ,$+2.32'),
    ('007457.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('007457.40', '1304.10 00', 'B,SERS (ext)'),
    ('007460.00', '13036.02 10', 'LX,$X1,100VO'),
    ('007460.40', '11372.03 10', 'SX,$X1,148ER1'),
]

# ---- the IX 1-15 blocks, PDF pp.114-120 ----
GROUP_LABEL = {0: 0o7441, 1: 0o7515, 2: 0o7561, 3: 0o7625}   # BD targets
GROUP_LABEL_H = {0: 1, 1: 0, 2: 0, 3: 0}
start = 0o7461
for n in range(1, 16):
    # the page each block STARTS on; IX 2's block runs onto p.115, which
    # holds only its last six rows (007475.40-007500.40)
    pg = {1: 114, 2: '114-115', 3: 116, 4: 116, 5: 116, 6: 117, 7: 117, 8: 117,
          9: 118, 10: 118, 11: 118, 12: 119, 13: 119, 14: 119, 15: 120}[n]
    s = start
    ROWS += [
        (o(s), '11320.00 80', f'SIC,148S2  IX {n} p.{pg}'),
        (o(s, 1), '11310.10 00', f'B,148S1  IX {n}'),
        (o(s + 1), f'{0o11321 + n:o}.{2 * n:02o} 10', f'LX,$X{n},148K{n}'),
        (o(s + 1, 1), '11373.22 00', 'Z,148DMP'),
        (o(s + 2), '0.30 00', 'NOP'),
        (o(s + 2, 1), '0.30 00', 'NOP'),
        (o(s + 3), f'0.{2 * n + 1:02o} 1{n:X}', f'SX,$X{n},0($X{n})'),
        (o(s + 3, 1), '0.30 00', 'NOP'),
        (o(s + 4), '0.30 00', 'NOP'),
        (o(s + 4, 1), '11373.00 80 000000.20 50', f'L(BU),148DMP  IX {n}'),
        (o(s + 5, 1), f'{s + 8:o}.34 C0', 'BZRZ,$+2.32  (to the next block)'),
        (o(s + 6), '1310.00 80', 'SIC,SEN (ext)'),
        (o(s + 6, 1), '1304.10 00', 'B,SERS (ext)'),
        (o(s + 7), '13036.02 10', 'LX,$X1,100VO'),
        (o(s + 7, 1), '11372.03 10', 'SX,$X1,148ER1'),
    ]
    start += 8
    if n % 4 == 3:
        g = n // 4
        e = start
        lab = f'{GROUP_LABEL[g]:o}.{"44" if GROUP_LABEL_H[g] else "04"} 00'
        ROWS += [
            (o(e), f'{e + 1:o}.10 00', f'B,$+1.0  exit {g}'),
            (o(e, 1), lab, f'BD,I48{g + 2}'),
            (o(e + 1), '1311.40 80', 'SIC,SENO+.32 (ext)'),
            (o(e + 1, 1), '1301.10 00', 'B,SSW (ext)'),
            (o(e + 2), f'{e + 2:o}.44 00', 'BD,$+.32'),
            (o(e + 2, 1), '11306.32 10', 'LX,$X13,IC248 (ext)'),
            (o(e + 3), f'{0o13054 + g:o}.32 B0', f'V+,$X13,BIT{g} (ext)'),
            (o(e + 3, 1), '11306.33 10', 'SX,$X13,IC248 (ext)'),
        ]
        start += 4

# ---- PDF p.152, 148S1 / 148S2 ----
for i, n in enumerate([0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 2]):
    ROWS.append((o(0o11310 + i // 2, i % 2), f'{16 + n:o}.22 00', f'148S1 Z,$X{n} p.152'))
ROWS.append(('011320.00', '0.10 00', '148S2 $B,0'))

# ---- PDF p.153, the CNOP fill and 148K0-148K15 ----
ROWS.append(('011320.40', '0.30 00', 'CNOP p.153'))
for n in range(16):
    ROWS.append((o(0o11321 + n), f'11373.{2 * n + 1:02o} 10', f'148K{n} SX,$X{n},148DMP'))
    ROWS.append((o(0o11321 + n, 1), '0.30 00', 'NOP'))

ROWS += [
    ('011372.00', '0.00 00 000000.00 00', '148ER1 XW,0,0,0 p.153'),
    ('011373.00', '0.00 00 000000.00 00', '148DMP XW,0,0,0 p.154'),
    ('013036.00', '777777.77 80 000000.00 00', '100VO XW,(8)-777777.77,0,0 p.190'),
]

SYMBOLS = {
    'I481':   '007441.00',
    'I482':   '007441.40',
    'I483':   '007515.00',
    'I484':   '007561.00',
    'I485':   '007625.00',
    'I48S1':  '011310.00',
    'I48K0':  '011321.00',
    'I48ER1': '011372.00',
    'I48DMP': '011373.00',
    'I00VO':  '013036.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST1A '))
