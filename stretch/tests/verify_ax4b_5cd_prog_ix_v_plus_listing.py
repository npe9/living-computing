#!/usr/bin/env python3
"""verify_ax4b_5cd_prog_ix_v_plus_listing.py -- jb_ax4b "I-Box 4", routine 148's
TESTs 5C and 5D ("CHK PROG IX V+I" / "CHK PROG IX V+IC",
../decks/ax4b_5cd_prog_ix_v_plus.strap) against the machine code the listing prints
beside each source line: PDF p.149, octal 011166.00-011213.40; routine
148's constants on PDF p.153 (011352.00-011371.00); BIT17 on PDF p.191
(013075.00).  The sheets carry no printed page number; cite PDF pages.

WHY IT MATTERS.  Two progressive-indexing VFL loads, codes V+I and
V+IC:

    L(V+I)(BU,64,8),1.0($X1)   1.00 81 100000.20 50   (011166.40)
    L(V+IC)(BU,64,8),1.0($X1)   1.00 81 200000.20 50   (011177.00)

each followed by IBM's four checks: the operand (KV $X2 vs 148K25), the
index value (KV $X1 vs 148K28), the count (KC $X1 vs BIT17) and the
refill (SR / LX / BZXVZ).  Routine 148's TESTs 5E/5F (V+ICR, V-I) are
ibox4_prog_ix_v.strap.

WHAT IT CHECKS: 53 rows and 6 symbols, every row on p.149, the
ten p.153 constants and BIT17.  Rows marked (ext) name SSIP's
SEN/SENO/SERS/SSW, IC248 or BIT0, given by SYN (or substitute halts)
at the printed addresses, so they check opcode and modifier bits only.

PROVEN DISCRIMINATING, 2026-11-18, each injected into the assembler in
the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written (PYTHONDONTWRITEBYTECODE=1).  OBSERVED failure sets:
  PROG_CODES "V+IC" 2 -> 3 and "V-ICR" 7 -> 6 (one build, both decks)
      011177.00 L(V+IC) -> '000001.00 81 300000.20 50'                              (1 row)
  enc_xw writes the refill field as 0
      011366.00 148XW6 -> '011352.00 00 000020.00 00'
      011371.00 148XW9 -> '011354.00 00 000020.00 00'          (2 rows)
  The model-side injections are in the deck's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_5cd_prog_ix_v_plus.strap").read())


def test_rows(h0, xw_addr, p):
    """One TEST's 16 rows, starting at half-word h0 (octal word*2+half)."""
    seq = [
        (f'{xw_addr}.02 10', 'LX,$X1,148XWn', 1),
        (f'1.00 81 {p}00000.20 50', 'L(prog)(BU,64,8),1.0($X1)', 2),
        ('11.04 10', 'LX,$X2,$R', 1),
        ('11352.04 90', 'KV,$X2,148K25', 1),
        ('1310.00 80', 'SIC,SEN (ext)', 1),
        ('1304.32 C0', 'BZXE,SERS (ext)', 1),
        ('11355.02 90', 'KV,$X1,148K28', 1),
        ('1310.00 80', 'SIC,SEN (ext)', 1),
        ('1304.32 C0', 'BZXE,SERS (ext)', 1),
        ('13075.03 90', 'KC,$X1,BIT17', 1),
        ('1310.00 80', 'SIC,SEN (ext)', 1),
        ('1304.32 C0', 'BZXE,SERS (ext)', 1),
        ('21.03 70', 'SR,$X1,$X1', 1),
        ('21.02 10', 'LX,$X1,$X1', 1),
        ('1310.00 80', 'SIC,SEN (ext)', 1),
        ('1304.31 40', 'BZXVZ,SERS (ext)', 1),
    ]
    r, h = [], h0
    for code, what, n in seq:
        r.append((f'{h // 2:06o}.{"40" if h % 2 else "00"}', code, what))
        h += n
    return r


ROWS = test_rows(0o11166 * 2, '11364', '1') + test_rows(0o11176 * 2 + 1, '11365', '2')
ROWS += [
    ('011207.00', '11210.10 00', 'B,$+1.0'),
    ('011207.40', '11166.04 00', 'BD,I4845'),
    ('011210.00', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('011210.40', '1301.10 00', 'B,SSW (ext)'),
    ('011211.00', '11211.44 00', 'BD,$+.32'),
    ('011211.40', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('011212.00', '34.33 50', 'SC,$X13,$X12'),
    ('011212.40', '13054.30 B0', 'V+,$X12,BIT0 (ext)'),
    ('011213.00', '34.32 50', 'LC,$X13,$X12'),
    ('011213.40', '11306.33 10', 'SX,$X13,IC248 (ext)'),
    # ---- PDF p.153 ----
    ('011352.00', '123456.70 00 000000.00 00', '148K25 XW,(8)123456.70'),
    ('011353.00', '765432.10 00 000000.00 00', '148K26 XW,(8)765432.10'),
    ('011354.00', '123456.70 00 000000.00 00', '148K27 XW,(8)123456.70'),
    ('011355.00', '11353.00 00 000020.00 00', '148K28 XW,148K26,1,0'),
    ('011364.00', '11352.00 00 000020.00 00', '148XW4 XW,148K25,1,0'),
    ('011365.00', '11352.00 00 000040.00 00', '148XW5 XW,148K25,2,0'),
    ('011366.00', '11352.00 00 000020.22 ED', '148XW6 XW,148K25,1,148K28'),
    ('011367.00', '11354.00 00 000020.00 00', '148XW7 XW,148K27,1,0'),
    ('011370.00', '11354.00 00 000040.00 00', '148XW8 XW,148K27,2,0'),
    ('011371.00', '11354.00 00 000020.22 ED', '148XW9 XW,148K27,1,148K28'),
    # ---- PDF p.191 ----
    ('013075.00', '1.00 00 000000.00 00', 'BIT17 XW'),
]

SYMBOLS = {
    'I4845': '011166.00',
    'I48K25': '011352.00',
    'I48K28': '011355.00',
    'I48XW4': '011364.00',
    'I48XW9': '011371.00',
    'BIT17':  '013075.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST5C5D '))
