#!/usr/bin/env python3
"""verify_ax5b_160102_listing.py -- jb_ax5b "I-Box 5", routine 1260's
TEST 7 continued: "CHK LOWER BOUNDARY DATA." and "CHK BOUNDARY CONTROL
BIT."  (../decks/ax5b_160102_lb_ctl.strap) against the listing's
printed machine code, PDF p.68, octal 022264.40-022306.40.

The upper-boundary half is verify_ax5b_16099_listing.py (p.65).  This
is the rest of TEST 7: the other register, and the control bit.

THE LOWER LOOP MIRRORS THE UPPER with three differences: it stores
through $LB (word 3 bits 32-49), indexes its error table with $X2, and
that table is I60B18 at 022313.40 -- whose entries pp.69-70 print as
"LOWER BOUNDARY DATA FAILURE, BIT 32" upward.

THE CONTROL-BIT TEST sets word 3 bit 57 from BIT57, reads word 3 back,
moves the refill field with "SR,$X1,$X1" and compares against BIT11 --
bit 57 sits at refill position 57-46 = 11 -- then clears word 3 with
"Z,$UB" and compares against I00Z.

A FOURTH CONFIRMATION OF THE BIT TABLE: BIT57 prints 24613 and BIT11
prints 24535; 024522 + 57 = 024613 and 024522 + 11 = 024535.  The rule
read off p.114 holds at 0, 11, 17, 18 and 57.

PROVEN DISCRIMINATING (encoding).  Observed failure sets:

  DIR_INDEX_CODES["SR"] 0b10111 -> 0b10110
      022300.00, 022305.00 -- both SR rows              (2 rows)
  SYSTEM_SYMBOLS["LB"] (3,32) -> (3,31)
      022267.00, 022271.40 -- the $LB store and load    (2 rows)

AND ONE THIS FILE CANNOT SEE, found by trying the obvious injection
first and watching it survive.  Moving $LB WITHIN its half-word --
(3,32) -> (3,33), (3,40), even (3,63) -- fails NOTHING.  A direct-index
address is 19 bits: an 18-bit word number plus a one-bit HALF-WORD
select, so the bit offset inside the half-word is not represented at
all.  Measured: (3,33) 0 rows, (3,40) 0 rows, (3,63) 0 rows, but
(3,31) 2 rows (it crosses into the other half-word) and (4,32) 2 rows
(different word).

So this oracle pins $LB to word 3's SECOND HALF-WORD and no further.
That bits 32-49 specifically are the lower boundary comes from the
pocket card's special-storage table and Reference Manual p.31, not
from anything checked here.
  INDICATOR_BITS["XE"] 53 -> 52
      022272.40 BXE, 022301.40 and 022306.40 BZXE       (3 rows)

AND THE RUN LOCALISES A FAULT TO THE BIT.  Measured, with
StretchStorage.bsv's boundary write masked:
  drop IBM bit 49 (bottom of the lower boundary)
      halts at 18890 = 022313.40 + 17*1.32, the error table's
      "LOWER BOUNDARY DATA FAILURE, BIT 49" entry
  drop IBM bit 57 (the control bit)
      halts at 1416 = 001304.00 = SERS, via the first BZXE --
      "UNABLE TO SET BNDRY CNTRL TO 1."
Both addresses were computed BEFORE the runs and both were hit.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_160102_lb_ctl.strap").read())

ROWS = [
    ('022264.40', '0.03 01',     'I60102 LVI,$X1,0.0   "-CHK LOWER BOUNDARY DATA."'),
    ('022265.00', '22.03 02',    'LCI,$X1,18            eighteen bits, 32-49'),
    ('022265.40', '0.05 01',     'LVI,$X2,0.0           the error-table index'),
    ('022266.00', '14.22 00',    'I60103 Z,$MASK'),
    ('022266.40', '24522.06 31', 'LV,$X3,BIT0($X1)      (ext)'),
    ('022267.00', '3.47 30',     'SV,$X3,$LB            word 3 bits 32-49'),
    ('022267.40', '0.30 00',     'NOP'),
    ('022270.00', '0.30 00',     'NOP'),
    ('022270.40', '0.30 00',     'NOP'),
    ('022271.00', '0.30 00',     'NOP'),
    ('022271.40', '3.46 30',     'LV,$X3,$LB            read back'),
    ('022272.00', '24522.06 91', 'KV,$X3,BIT0($X1)      (ext)'),
    ('022272.40', '22273.72 C2', 'BXE,$+1.0'),
    ('022273.00', '22313.50 02', 'B,I60B18($X2)        (ext) "-DATA ERROR."'),
    ('022273.40', '1.45 05',     'I60104 V+I,$X2,1.32'),
    ('022274.00', '22266.03 48', 'CB+,$X1,I60103'),
    ('022274.40', '24613.02 10', 'LX,$X1,BIT57          (ext) "-CHK BOUNDARY CONTROL BIT."'),
    ('022275.00', '3.03 10',     'SX,$X1,$UB'),
    ('022275.40', '0.30 00',     'NOP'),
    ('022276.00', '0.30 00',     'NOP'),
    ('022276.40', '0.30 00',     'NOP'),
    ('022277.00', '0.30 00',     'NOP'),
    ('022277.40', '3.02 10',     'LX,$X1,$UB'),
    ('022300.00', '21.03 70',    'SR,$X1,$X1            move the refill field'),
    ('022300.40', '24535.02 90', 'KV,$X1,BIT11          (ext) bit 57 = refill position 11'),
    ('022301.00', '1310.00 80',  'SIC,SEN               (ext)'),
    ('022301.40', '1304.32 C0',  'BZXE,SERS             (ext) "-UNABLE TO SET BNDRY CNTRL TO 1."'),
    ('022302.00', '3.22 00',     'Z,$UB                 clear word 3'),
    ('022302.40', '0.30 00',     'NOP'),
    ('022303.00', '0.30 00',     'NOP'),
    ('022303.40', '0.30 00',     'NOP'),
    ('022304.00', '0.30 00',     'NOP'),
    ('022304.40', '3.02 10',     'LX,$X1,$UB'),
    ('022305.00', '21.03 70',    'SR,$X1,$X1'),
    ('022305.40', '24502.02 90', 'KV,$X1,I00Z          (ext) the zero index word'),
    ('022306.00', '1310.00 80',  'SIC,SEN               (ext)'),
    ('022306.40', '1304.32 C0',  'BZXE,SERS             (ext) "-UNABLE TO SET BNDRY CNTRL TO 0."'),
]

SYMBOLS = {'I60102': '022264.40', 'I60103': '022266.00', 'I60104': '022273.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 T7b '))
