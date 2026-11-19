#!/usr/bin/env python3
"""verify_ax4b_1b_fp_load_listing.py -- jb_ax4b "I-Box 4", routine 148's
TEST 1B ("BASIC TEST OF FLOATING POINT LOAD.",
../decks/ax4b_1b_fp_load.strap) against the machine code the listing
prints beside each source line: PDF p.121, octal 007671.00-007721.00;
148ER1 (p.153, 011372.00), 100Z and 1000 (p.190, 013034.00-013035.00)
and BIT24 (p.191, 013104.00).  The sheets carry no printed page number;
cite PDF pages.

WHY IT MATTERS.  The FP loads TEST 4 and the later FP index tests rely
on, each with its own printed code:

    L(U),1000      13035.40 60     (007671.00)
    L(N),BIT24     13104.00 60     (007703.00)

WHAT IT CHECKS: 53 rows and 6 symbols, every row typed from the page
image (no template).  Rows marked (ext) name SSIP's SEN/SENO/SERS/SSW,
IC248, BIT4 or I4810, given by SYN (or substitute halts) at the printed
addresses, so they check opcode and modifier bits only.

PROVEN DISCRIMINATING, measured 2026-11-19; each
injected into the assembler in the worktree, run, restored from a saved
copy (cmp IDENTICAL), no __pycache__ written.  OBSERVED failure sets:
  enc_fp writes the unnormalized (U) bit as 0 -> 3 FAIL, exactly the
    three L(U) rows: 007671.00 L(U),I000 ('013035.00 60' vs '013035.40
    60'), 007674.40 L(U),I00Z, 007706.00 L(U),BIT24.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_1b_fp_load.strap").read())

ROWS = [
    # ---- PDF p.121 ----
    ('007671.00', '13035.40 60', 'I486 L(U),1000'),
    ('007671.40', '10.02 10', 'LX,$X1,$L'),
    ('007672.00', '13035.02 90', 'KV,$X1,1000'),
    ('007672.40', '7674.72 C2', 'BXE,$+2.0'),
    ('007673.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('007673.40', '1304.10 00', 'B,SERS (ext)'),
    ('007674.00', '7711.10 00', 'B,I487'),
    ('007674.40', '13034.40 60', 'L(U),100Z'),
    ('007675.00', '10.02 10', 'LX,$X1,$L'),
    ('007675.40', '7677.71 42', 'BXVZ,$+2.0'),
    ('007676.00', '1310.00 80', 'SIC,SEN (ext)'),
    ('007676.40', '1304.10 00', 'B,SERS (ext)'),
    ('007677.00', '7711.10 00', 'B,I487'),
    ('007677.40', '13035.00 60', 'L(N),1000'),
    ('007700.00', '10.02 10', 'LX,$X1,$L'),
    ('007700.40', '13035.02 90', 'KV,$X1,1000'),
    ('007701.00', '7703.32 C2', 'BXE,$+2.0'),
    ('007701.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('007702.00', '1304.10 00', 'B,SERS (ext)'),
    ('007702.40', '7711.10 00', 'B,I487'),
    ('007703.00', '13104.00 60', 'L(N),BIT24'),
    ('007703.40', '10.02 10', 'LX,$X1,$L'),
    ('007704.00', '7706.31 40', 'BZXVZ,$+2.0'),
    ('007704.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('007705.00', '1304.10 00', 'B,SERS (ext)'),
    ('007705.40', '7711.10 00', 'B,I487'),
    ('007706.00', '13104.40 60', 'L(U),BIT24'),
    ('007706.40', '10.02 10', 'LX,$X1,$L'),
    ('007707.00', '7712.71 42', 'BXVZ,I488'),
    ('007707.40', '1310.00 80', 'SIC,SEN (ext)'),
    ('007710.00', '1304.10 00', 'B,SERS (ext)'),
    ('007710.40', '7711.10 00', 'B,I487'),
    ('007711.00', '11372.02 10', 'I487 LX,$X1,148ER1'),
    ('007711.40', '777777.03 00', 'C+I,$X1,(8)777777'),
    ('007712.00', '11372.03 10', 'SX,$X1,148ER1'),
    ('007712.40', '7713.50 00', 'I488 B,$+1.0'),
    ('007713.00', '7717.04 00', 'BD,I489'),
    ('007713.40', '1311.40 80', 'SIC,SENO+.32 (ext)'),
    ('007714.00', '1301.10 00', 'B,SSW (ext)'),
    ('007714.40', '7715.04 00', 'BD,$+.32'),
    ('007715.00', '11306.32 10', 'LX,$X13,IC248 (ext)'),
    ('007715.40', '13060.32 B0', 'V+,$X13,BIT4 (ext)'),
    ('007716.00', '11306.33 10', 'SX,$X13,IC248 (ext)'),
    ('007716.40', '7721.44 00', 'BD,I4810 (ext)'),
    ('007717.00', '11372.02 10', 'I489 LX,$X1,148ER1'),
    ('007717.40', '20.22 00', 'Z,$X0'),
    ('007720.00', '21.00 B0', 'V+,$X0,$X1'),
    ('007720.40', '11372.01 10', 'SX,$X0,148ER1'),
    ('007721.00', '7671.10 00', 'B,I486'),
    # ---- PDF p.153 / p.190 / p.191 ----
    ('011372.00', '0.00 00 000000.00 00', '148ER1 XW,0,0,0 p.153'),
    ('013034.00', '0.00 00 000000.00 00', '100Z XW,0,0,0,0 p.190'),
    ('013035.00', '1777777777777777777777', '1000 DD(BU,64,8) all ones p.190'),
    ('013104.00', '0000000010000000000000', 'BIT24 (8)DD(BU) p.191'),
]

SYMBOLS = {
    'I486':   '007671.00',
    'I487':   '007711.00',
    'I488':   '007712.40',
    'I489':   '007717.00',
    'I48ER1': '011372.00',
    'BIT24':  '013104.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='148 TEST1B '))
