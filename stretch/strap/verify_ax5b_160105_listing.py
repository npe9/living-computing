#!/usr/bin/env python3
"""verify_ax5b_160105_listing.py -- jb_ax5b "I-Box 5", routine 1260
TEST 7's COMPARISON DRIVER (programs/ax5b_160105_compare.strap)
against the listing's printed machine code, PDF p.71, octal
022346.40-022401.00.

THE BLOCK docs/NEXT.md ITEM 1 HAS WANTED SINCE THE SCOUTING PASS.
pp.65 and 68 test whether the boundary REGISTERS HOLD THEIR BITS.
This one tests whether the COMPARISON FIRES: it sets bounds, ENABLES,
fetches outside them, and expects an address-monitoring interruption.
The deck's own summary:

    -TEST THE COMPARE CKTS, SETUP INTERRUPT TABLE.  UB HAS X, LB HAS
    -X-2.  FETCH FROM X+1 TO CHK UB COMP, FROM X-3 TO CHK LB COMP,
    -AND FROM X-1 TO CHECK WITHIN RANGE OF X IS FROM 000040 THRU
    -777777 OCTAL.

Upper bound X, lower bound X-2, three fetches -- above, below, inside
-- swept across the address range, landing at the deck's own two
labelled entries: I60107 "-AD INTRPTS ENTER HERE." and I6010A "-ALL
INTRPTS EXCEPT AD ENTER HERE."

IT USES TRANSMIT IMMEDIATE.  "TI,1,BOUND1,3.0" moves one word into
word 3 -- the boundary register itself -- as a FULL WORD at an ODD
half-word (022365.40 straddling into 022366.00), the same shape as
p.45's two TIs.  Until TRANSMIT_CODES landed this block could not have
been assembled; this is TI's first use outside the page it came from.

ENCODING ONLY, for a specific reason: it cannot run without I60S1's
body (SSIP's save/restore at 022741.00, still not transcribed), the
interruption table I60IT at 023201.00, and BOUND0/BOUND1 at
023302/023303.  That is the harness item 1 has always needed, and this
block is where the need is real rather than assumed.

PROVEN DISCRIMINATING.  Observed failure sets:

  enc_transmit's immediate-count bit forced to 0
      022365.40 -- the TI row                           (1 row)
  UNCOND_BRANCH_CODES["BD"] 0b001 -> 0b010
      every BD row: 022361.00, 022370.00, 022371.00,
      022371.40, 022372.00, 022377.40, 022401.00        (7 rows)
  BB_CODES["BZB"] (0b00,0) -> (0b01,0)
      022357.00 -- the one branch-on-bit                (1 row)
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_160105_compare.strap").read())

ROWS = [
    ('022346.40', '23065.02 10',
     'I60105 LX,$X1,I60XW1  (ext) "-TEST THE COMPARE CKTS, SETUP"'),
    ('022347.00', '23055.04 10',
     'LX,$X2,I60K12        (ext) "-INTERRUPT TABLE.  UB HAS X, LB HAS"'),
    ('022347.40', '23201.05 11',
     'SX,$X2,I60IT($X1)    (ext) build the interruption table'),
    ('022350.00', '22347.43 48',
     'CB+,$X1,$-.32         the build loop'),
    ('022350.40', '1353.03 01',
     'LVI,$X1,INT           (ext)'),
    ('022351.00', '23067.04 10',
     'LX,$X2,I60XW3        (ext)'),
    ('022351.40', '23302.22 00',
     'Z,BOUND0              (ext)'),
    ('022352.00', '24613.32 10',
     'LX,$X13,BIT57         (ext) the control bit'),
    ('022352.40', '23303.33 10',
     'SX,$X13,BOUND1        (ext)'),
    ('022353.00', '22372.07 01',
     'LVI,$X3,I60107       the AD landing'),
    ('022353.40', '23211.07 D0',
     'SVA,$X3,I60IT+16     (ext) table entry 16'),
    ('022354.00', '23041.00 80',
     'SIC,I60SX1           (ext) "-CLEAR INDS 0-19"'),
    ('022354.40', '22741.10 00',
     'B,I60S1              (ext) SSIP save/restore'),
    ('022355.00', '23063.22 00',
     'Z,I60AD1             (ext) "-CLEAR FIRST INTERRUPT INDICATORS"'),
    ('022355.40', '23064.22 00',
     'Z,I60AD3             (ext)'),
    ('022356.00', '22372.47 01',
     'I60106 LVI,$X3,I60107+.32'),
    ('022356.40', '22372.07 D0',
     'SVA,$X3,I60107'),
    ('022357.00', '4.74 80 022506.74 00',
     'BZB,4.60,I60122   (ext) full word'),
    ('022360.00', '22376.47 01',
     'LVI,$X3,I60109'),
    ('022360.40', '22371.47 D0',
     'SVA,$X3,I6010A'),
    ('022361.00', '22361.44 00',
     'BD,$+.32'),
    ('022361.40', '14.22 00',
     'Z,$MASK               "-SETUP UB + LB."'),
    ('022362.00', '23302.45 30',
     'SV,$X2,BOUND0+.32     (ext) "-LOWER BOUND"'),
    ('022362.40', '23303.45 30',
     'SV,$X2,BOUND1+.32     (ext)'),
    ('022363.00', '2.05 05',
     'V+I,$X2,2.0'),
    ('022363.40', '23302.05 30',
     'SV,$X2,BOUND0         (ext) "-UPPER BOUND"'),
    ('022364.00', '23303.05 30',
     'SV,$X2,BOUND1         (ext)'),
    ('022364.40', '13.22 00',
     'Z,$IND'),
    ('022365.00', '22365.52 46',
     'BDFZ,$+.32'),
    ('022365.40', '23303.00 80 000003.02 A0',
     'TI,1,BOUND1,3.0   (ext) FULL WORD at an ODD half-word'),
    ('022366.40', '2.03 70',
     'SR,$X1,$IA'),
    ('022367.00', '22367.40 00',
     'BE,$+.32              enable'),
    ('022367.40', '0.32 12',
     'LX,$X13,0($X2)        "-FETCH FROM UB, BC IS 1."'),
    ('022370.00', '22370.44 00',
     'BD,$+.32'),
    ('022370.40', '2.03 30',
     'SV,$X1,$IA'),
    ('022371.00', '22376.44 00',
     'BD,I60109'),
    ('022371.40', '22372.04 00',
     'I6010A BD,$+.32      "-ALL INTRPTS EXCEPT AD ENTER HERE."'),
    ('022372.00', '22372.44 00',
     'I60107 BD,$+.32      "-AD INTRPTS ENTER HERE."'),
    ('022372.40', '2.03 30',
     'SV,$X1,$IA'),
    ('022373.00', '23063.32 30',
     'LV,$X13,I60AD1       (ext) "-DID WE INTRPT LAST TIME THRU."'),
    ('022373.40', '22375.31 42',
     'BXVZ,I60108'),
    ('022374.00', '3.36 10',
     'LX,$X15,3.0           save the boundary registers'),
    ('022374.40', '22506.50 00',
     'B,I60122             (ext)'),
    ('022375.00', '777777.73 05',
     'I60108 V+I,$X13,(8)777777.40'),
    ('022375.40', '23063.33 30',
     'SV,$X13,I60AD1       (ext)'),
    ('022376.00', '22414.10 00',
     'B,I60111             (ext) "-UB FROM AD."'),
    ('022376.40', '22401.52 46',
     'I60109 BDFZ,I60110  (ext)'),
    ('022377.00', '22400.10 00',
     'B,$+1.0'),
    ('022377.40', '22356.04 00',
     'BD,I60106            round again'),
    ('022400.00', '1311.40 80',
     'SIC,SEN0+.32          (ext)'),
    ('022400.40', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP."'),
    ('022401.00', '22506.44 00',
     'BD,I60122            (ext) "-TERMINATE."'),
]

SYMBOLS = {'I60105': '022346.40', 'I60106': '022356.00',
           'I60107': '022372.00', 'I6010A': '022371.40',
           'I60108': '022375.00', 'I60109': '022376.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 T7c '))
