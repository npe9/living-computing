#!/usr/bin/env python3
"""verify_ax4b_5a_p_field_000_listing.py -- jb_ax4b "I-Box 4", routine
148's TEST 5A ("CHKS P FIELD OF 000", ../decks/ax4b_5a_p_field_000.strap)
against the machine code the listing prints beside each source line:
PDF p.142, octal 010736.40-010767.00, and the constant 148K24 on PDF
p.153, 011351.00.  The sheets carry no printed page number; cite PDF
pages.

WHY IT MATTERS.  The direct-address (P = 000) member of TEST 5's eight
P codes, with a nonzero I on an index register holding ZERO:

    L(BU),148K24($X1)       11351.00 81 000000.20 50     (010737.00)

then "LX,$X0,$R" (11.00 10): an LX INTO $X0, read back by KV/KC/KVI on
$X0 (J = 0 prints ".00"/".01").

WHAT IT CHECKS: 46 rows and 5 symbols, every row on p.142 plus
148K24.  Rows marked (ext) name SSIP's SEN/SENO/SERS/SSW, IC248 or
BIT21, given by SYN (or substitute halts) at the printed addresses, so
they check opcode and modifier bits only.

PROVEN DISCRIMINATING, 2026-11-18, each injected into the assembler in
the worktree, run, restored from a saved copy (cmp IDENTICAL), no
__pycache__ written (PYTHONDONTWRITEBYTECODE=1).  OBSERVED failure sets:
  enc_vfl_full drops i1 (always 0)
      010737.00 L(BU),148K24($X1) -> '011351.00 80 000000.20 50' (1 row)
  MISC_CODES "Z" 0b100 -> 0b101
      010736.40 Z,$X1 -> '000021.26 00'                        (1 row)
  The model-side injections are in the deck's header.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_5a_p_field_000.strap").read())

ROWS = [
    ('010736.40', '21.22 00', 'I4833 Z,$X1'),
    ('010737.00', '11351.00 81 000000.20 50', 'L(BU),148K24($X1)  I=1, P=0'),
    ('010740.00', '11.00 10', 'LX,$X0,$R'),
    ('010740.40', '11351.00 90', 'KV,$X0,148K24'),
    ('010741.00', '10742.32 C2', 'BXE,$+1.0'),
    ('010741.40', '10746.50 00', 'B,I4834'),
    ('010742.00', '11351.01 90', 'KC,$X0,148K24'),
    ('010742.40', '10743.72 C2', 'BXE,$+1.0'),
    ('010743.00', '10746.50 00', 'B,I4834'),
    ('010743.40', '21.00 80 000000.20 50', 'L(BU),$X1'),
    ('010744.40', '10763.74 C2', 'BRZ,I4835'),
    ('010745.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('010745.40', '1304.10 00', 'B,SERS (ext)'),
    ('010746.00', '10763.50 00', 'B,I4835'),
    ('010746.40', '11351.01 04', 'I4834 KVI,$X0,148K24'),
    ('010747.00', '10751.32 C0', 'BZXE,$+2.0'),
    ('010747.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('010750.00', '1304.10 00', 'B,SERS (ext)'),
    ('010750.40', '10763.50 00', 'B,I4835'),
    ('010751.00', '20.00 80 000000.20 50', 'L(BU),$X0'),
    ('010752.00', '10753.34 C2', 'BRZ,$+1.0'),
    ('010752.40', '10757.50 00', 'B,I4836'),
    ('010753.00', '21.00 80 000000.20 50', 'L(BU),$X1'),
    ('010754.00', '10756.34 C2', 'BRZ,$+2.0'),
    ('010754.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('010755.00', '1304.10 00', 'B,SERS (ext)'),
    ('010755.40', '10763.50 00', 'B,I4835'),
    ('010756.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('010756.40', '1304.10 00', 'B,SERS (ext)'),
    ('010757.00', '10763.50 00', 'B,I4835'),
    ('010757.40', '21.00 80 000000.20 50', 'I4836 L(BU),$X1'),
    ('010760.40', '10762.74 C2', 'BRZ,$+2.0'),
    ('010761.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('010761.40', '1304.10 00', 'B,SERS (ext)'),
    ('010762.00', '10763.50 00', 'B,I4835'),
    ('010762.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('010763.00', '1304.10 00', 'B,SERS (ext)'),
    ('010763.40', '10764.50 00', 'I4835 B,$+1.0'),
    ('010764.00', '10736.44 00', 'BD,I4833'),
    ('010764.40', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('010765.00', '1301.10 00', 'B,SSW (ext)'),
    ('010765.40', '10766.04 00', 'BD,$+.32'),
    ('010766.00', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('010766.40', '13101.32 B0', 'V+,$X13,BIT21 (ext)'),
    ('010767.00', '11306.33 10', 'SX,$X13,IC248 (ext)'),
    # ---- PDF p.153 ----
    ('011351.00', '123456.76 02 471340.00 00', '148K24 XW,(8)123456.76,(8)123456,0'),
]

SYMBOLS = {
    'I4833':  '010736.40',
    'I4834':  '010746.40',
    'I4835':  '010763.40',
    'I4836':  '010757.40',
    'I48K24': '011351.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST5A '))
