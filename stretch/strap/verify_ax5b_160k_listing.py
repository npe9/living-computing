#!/usr/bin/env python3
"""verify_ax5b_160k_listing.py -- jb_ax5b "I-Box 5", routine 1260's
constants (programs/ax5b_160k_constants.strap) against the listing's
printed machine code, PDF p.86, octal 023042.00-023070.00.

WHY THIS BLOCK.  It is the harness the p.71 comparison driver needs,
and it settles three things earlier transcriptions had to leave open:

  160K7 IS THE ILLEGAL OP.  ax5b_16082_op_ad.strap SYN'd it from p.41
  and listed under "NOT TRACED": "WHAT 160K7 CONTAINS.  Only its
  address is printed here ... reads like self-modifying code planting
  an invalid operation code ... Nothing on these pages says so."
  p.86 says so: "160K7 %8@DD%BU,32,8@,3740  -ILLEGAL OP, NO. 31."

  160K16 IS "BD,16086A", confirming ax5b_16086_ds.strap's external.

  THE INTERRUPT TABLE IS 64 WORDS, STATED.  160IT is
  "DR%BU,64,8@,64" at 023201.00 and 160DMP sits at 023301.00, 0o100
  words later.  run_tests.sh's interruption section had REASONED to
  64; the DR row states it.

160K12 is the table's default entry -- "BD,16010A" twice, so every
interruption disables and branches to p.71's "-ALL INTRPTS EXCEPT AD
ENTER HERE."  160XW1 (count 64, refill 160IT) is what the comparison
driver's CB+ loop walks to fill all 64 slots.

AND IT EXPOSED AN ASSEMBLER GAP, the third this routine has found.
"C+I,$X1,160DMP" prints "23301.03 00" -- the label's WORD address in
bits 0-17 -- and count-type immediates were evaluating a label to a
BIT address, which wrapped.  They now use eval_addr_field with shift
6, as XW's refill already did; bare-integer counts are unchanged.

PROVEN DISCRIMINATING.  Observed failure sets:

  count-immediates back to eval_expr (a label as a bit address)
      023044.00 -- the C+I row that found it              (1 row)
  IMM_INDEX_CODES["C+I"] 0b0000 -> 0b0001
      023044.00                                           (1 row)
  UNCOND_BRANCH_CODES["BD"] 0b001 -> 0b010
      023046.00, 023046.40, 023047.00, 023051.00,
      023055.00, 023055.40, 023061.00, 023061.40,
      023062.00, 023062.40                               (10 rows)
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_160k_constants.strap").read())

ROWS = [
    ('023042.00', '777777.60 00 000000.00 00',
     'L160K1 XW,(8)777777.60,0,0'),
    ('023043.00', '23301.03 10',
     'L160K2 SX,$X1,L160DMP    (ext)'),
    ('023043.40', '0.30 00',
     'NOP'),
    ('023044.00', '23301.03 00',
     'L160K3 C+I,$X1,L160DMP   (ext) label = WORD address'),
    ('023044.40', '0.30 00',
     'NOP'),
    ('023045.00', '23301.03 30',
     'L160K4 SV,$X1,L160DMP    (ext)'),
    ('023045.40', '0.30 00',
     'NOP'),
    ('023046.00', '14642.04 00',
     'L160K5 BD,L16035         (ext)'),
    ('023046.40', '14642.04 00',
     'BD,L16035         (ext)'),
    ('023047.00', '21512.44 00',
     'L160K6 BD,L16090         (ext)'),
    ('023047.40', '0.30 00',
     'NOP'),
    ('023050.00', '00000003740',
     'L160K7 DD(BU,32,8),(8)3740   "-ILLEGAL OP, NO. 31."'),
    ('023050.40', '0.30 00',
     'NOP'),
    ('023051.00', '22072.04 00',
     'L160K8 BD,L16097         (ext)'),
    ('023051.40', '0.30 00',
     'NOP'),
    ('023052.00', '1.00 80 000000.00 00',
     'L160K9 XW,-1.0,0,0'),
    ('023053.00', '1.00 00 000020.00 00',
     'L160K10 XW,1.0,1,0'),
    ('023054.00', '3.00 80 001760.00 00',
     'L160K11 XW,-3.0,63,0'),
    ('023055.00', '22371.44 00',
     'L160K12 BD,L16010A       (ext) the table default entry'),
    ('023055.40', '22371.44 00',
     'BD,L16010A               (ext)'),
    ('023056.00', '0.30 00',
     'L160K13 NOP'),
    ('023056.40', '0.30 00',
     'NOP'),
    ('023057.00', '0.01 80 000000.00 00',
     'L160K14 XW,-0.1,0,0'),
    ('023060.00', '777777.60 80 000000.00 00',
     'L160K15 XW,-(8)777777.60,0,0'),
    ('023061.00', '21372.44 00',
     'L160K16 BD,L16086A       (ext) 16086 SYNs this'),
    ('023061.40', '21372.44 00',
     'BD,L16086A               (ext)'),
    ('023062.00', '22372.04 00',
     'L160K17 BD,L160107       (ext)'),
    ('023062.40', '22372.04 00',
     'BD,L160107               (ext)'),
    ('023063.00', '0.30 00',
     'L160AD1 NOP              the first-interrupt flags'),
    ('023063.40', '0.30 00',
     'L160AD2 NOP'),
    ('023064.00', '0.30 00',
     'L160AD3 NOP'),
    ('023064.40', '0.30 00',
     'NOP'),
    ('023065.00', '0.00 00 002000.46 81',
     'L160XW1 XW,0,64,L160IT   (ext) count 64, refill the table'),
    ('023066.00', '0.00 00 001400.00 00',
     'L160XW2 XW,0,48,0'),
    ('023067.00', '101.00 00 000000.00 00',
     'L160XW3 XW,(8)101.0,0,0'),
    ('023070.00', '0.00 00 001760.46 81',
     'L160XW4 XW,0,63,L160IT   (ext)'),
]

SYMBOLS = {'L160K7': '023050.00', 'L160K12': '023055.00',
           'L160K16': '023061.00', 'L160XW1': '023065.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 K '))
