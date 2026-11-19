#!/usr/bin/env python3
"""verify_ax5b_160_test2_ia_listing.py -- jb_ax5b "I-Box 5", routine 1260
("CHECK MASK, INDICATOR, AND INTERRUPT."), its TEST 2, "-TEST 2, CHK
DATA IN IA." (../decks/ax5b_160_test2_ia.strap), against the machine
code the listing prints beside each source line: PDF pp.22-23, octal
014556.00-014625.40, plus the p.114 constants it reads.  The sheets
carry no printed page number; cite PDF pages.

WHY IT MATTERS.  IBM's own test of the INTERRUPT ADDRESS register
(word 2, $IA): eighteen passes, each storing BITk's value field into
IA with SV and comparing it back with KV.  The rows that address IA:

    SV,$X3,$IA          2.07 30      (014560.00)
    KV,$X3,$IA          2.06 90      (014561.40)

WHAT IT CHECKS: 83 rows and 6 symbols.  TEST 2's code (13 rows, p.22), its eighteen-entry error
table (54 rows, pp.22-23), the exit and continuity (8 rows, p.23), the
clearing loop that falls into TEST 3 (5 rows, p.23), and the p.114
constants it reads (BIT0, BIT3, BIT17).  The error-table entries print
the same three rows apart from the comment, so they are generated
below from the printed pattern; every generated row was then compared
with the page images (pp.22-23), row for row.  Rows marked (ext) name
SSIP's SEN/SENO/SERS/SSW, at the addresses jb_ax4b PDF p.193's SYN
table prints (and which these pages print too: 1310.00, 1311.40,
1304.04, 1301.10), so they check opcode and modifier bits only.

The three p.114 rows take their printed code from
verify_ax5b_bit_table_listing.py, which checked them against p.114.

PROVEN DISCRIMINATING, measured 2026-11-19: injected into the assembler
in the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written.  OBSERVED failure set:
  opcodes.py's $IA system symbol moved a word ('"IA":  (2, 0),' ->
    '(3, 0),') -> 2 FAIL, exactly the two rows that address IA
    (014560.00 SV '000003.07 30' vs '000002.07 30'; 014561.40 KV
    '000003.06 90' vs '000002.06 90').  Nothing else moves.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_160_test2_ia.strap").read())


def o(hw):
    return f'{hw // 2:06o}.{"40" if hw % 2 else "00"}'


ROWS = [
    # ---- PDF p.22, TEST 2 ----
    ('014556.00', '0.03 01', '16041 LVI,$X1,0.0  -TEST 2, CHK DATA IN IA.'),
    ('014556.40', '22.03 02', 'LCI,$X1,18'),
    ('014557.00', '0.05 01', 'LVI,$X2,0.0'),
    ('014557.40', '24522.06 31', '16041A LV,$X3,BIT0(X1)'),
    ('014560.00', '2.07 30', 'SV,$X3,$IA'),
    ('014560.40', '0.30 00', 'NOP'),
    ('014561.00', '0.30 00', 'NOP'),
    ('014561.40', '2.06 90', 'KV,$X3,$IA'),
    ('014562.00', '14563.32 C2', 'BXE,$+1.0'),
    ('014562.40', '14564.50 02', 'B,160B6(X2)'),
    ('014563.00', '1.45 05', '16042 V+I,$X2,1.32'),
    ('014563.40', '14557.43 48', 'CB+,$X1,16041A'),
    ('014564.00', '14617.44 00', 'BD,16043'),
]
# ---- PDF pp.22-23, error table 160B6: bits 0-17, three rows each ----
hw = 0o14564 * 2 + 1
for k in range(18):
    pg = 22 if k < 9 else 23
    ROWS += [
        (o(hw), '1310.00 80', f'SIC,SEN (ext)  -IA DATA FAILURE, BIT {k}. p.{pg}'),
        (o(hw + 1), '1304.04 00', 'BD,SERS (ext)'),
        (o(hw + 2), '14563.04 00', 'BD,16042'),
    ]
    hw += 3
ROWS += [
    # ---- PDF p.23, exit, continuity, and the clearing loop ----
    ('014617.40', '14620.50 00', '16043 B,$+1.0'),
    ('014620.00', '14556.04 00', 'BD,16041'),
    ('014620.40', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('014621.00', '1301.10 00', 'B,SSW (ext)  -TO SSIP.'),
    ('014621.40', '14622.04 00', 'BD,$+.32'),
    ('014622.00', '22737.32 10', 'LX,$X13,IC260  -UPDATE CONTINUITY CHECK.'),
    ('014622.40', '24525.32 B0', 'V+,$X13,BIT3'),
    ('014623.00', '22737.33 10', 'SX,$X13,IC260'),
    ('014623.40', '14624.04 00', 'BD,$+.32'),
    ('014624.00', '20.03 02', 'LCI,$X1,16.0'),
    ('014624.40', '0.03 01', 'LVI,$X1,0.0'),
    ('014625.00', '0.22 01', 'Z,0.0(X1)'),
    ('014625.40', '14625.03 48', 'CB+,$X1,$-.32'),
    # ---- PDF p.114, the constants the run reads ----
    ('024522.00', '400000.00 00 000000.00 00', 'BIT0 p.114'),
    ('024525.00', '40000.00 00 000000.00 00', 'BIT3 p.114'),
    ('024543.00', '1.00 00 000000.00 00', 'BIT17 p.114'),
]

SYMBOLS = {
    'I6041':  '014556.00',
    'I6041A': '014557.40',
    'I6042':  '014563.00',
    'I60B6':  '014564.40',
    'I6043':  '014617.40',
    'BIT0':   '024522.00',
}

print(f"INFO {len(ROWS)} rows, {len(SYMBOLS)} symbols")
finish(check_rows(prog, ROWS, SYMBOLS, label='160 TEST2 '))
