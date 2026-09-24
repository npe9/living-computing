#!/usr/bin/env python3
"""verify_ax1a_bew_listing.py -- ja_ax1a "I-BOX 1", the %BEW% and
%SIC-BEW% blocks (programs/ax1a_bew.strap) against the listing's
printed machine code, PDF p.58, octal 006027.40-006047.00.

WHY THIS BLOCK.  BEW is the halt idiom every program in this suite
ends with, and nothing here had ever checked its ENCODING against a
listing.  The SIC prefix on a BEW is a combination no transcription
here covers at all.

AND IT CORRECTS docs/NEXT.md, which said this block drove BEW "from
the interval timer and fall through".  It does not.  Reference Manual
printed p.40: "the instruction counter contents are replaced with bits
0-18 of the effective address of the operation as in BRANCH ENABLED.
However, no further instruction will be executed until after an
interruption occurs."  BEW BRANCHES, then waits -- and the "BD,$"
after each BEW sits at the FALL-THROUGH address, which is the hang a
machine that failed to branch would reach:

  ISBE37  BEW,ISBE38   6031.60 00   at 006030.40
          BD,$         6031.04 00   at 006031.00
  ISBE38  BD,$+.32     6032.04 00   at 006031.40

0o60 has bit 18 set, so the target is 006031.40 -- two half-words past
the hang.

A NOTE ON THE STANDARD.  This is a strong ENCODING oracle and could
only ever be a weak run test: because BEW always branches, control
reaches the target whether the WAIT is modelled or not.  Seeing the
wait needs the interval timer to tick, which this model does not do.
Stated here so the section is not mistaken for evidence about the wait.

PROVEN DISCRIMINATING.  Observed failure sets -- and note each names a
DIFFERENT set, which is what makes them four checks rather than one:

  UNCOND_BRANCH_CODES["BEW"] 0b100 -> 0b101
      006030.40, 006033.40, 006037.00, 006042.00, 006045.40  (5 rows)
  UNCOND_BRANCH_CODES["BE"] 0b000 -> 0b010
      006030.00, 006033.00, 006036.40, 006041.40, 006044.40  (5 rows)
  UNCOND_BRANCH_CODES["NOP"] 0b110 -> 0b111
      006034.40                                              (1 row)
  enc_sic's literal 1000 -> 1001 (Ref. Manual p.41, bits 24-27)
      006045.00                                              (1 row)

THE FIRST ATTEMPT AT THESE WAS WRONG AND SAID SO ONLY BY ACCIDENT.
Run without clearing __pycache__ between injections, all three
reported the SAME five rows -- the FIRST injection's answer, replayed
from stale bytecode, because cp-restore within one second leaves the
.pyc newer than the source.  The tell was that a restored tree still
failed while "git diff" showed nothing.  Clear __pycache__ on BOTH
sides of every injection; this project's NEXT.md has carried that trap
since the DS work and it still bit.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax1a_bew.strap").read())

ROWS = [
    ('006027.40', '1.03 30',      'SV,$X1,$IT            -FOR'),
    ('006030.00', '6030.40 00',   'BE,$+.32              -BEW TEST'),
    ('006030.40', '6031.60 00',   'ISBE37 BEW,ISBE38     -BEW TILL I. T. SIGNAL'),
    ('006031.00', '6031.04 00',   'BD,$                  the fall-through hang'),
    ('006031.40', '6032.04 00',   'ISBE38 BD,$+.32       -SET UP'),
    ('006032.00', '1.03 01',      'LVI,$X1,1.0           -FOR'),
    ('006032.40', '1.03 30',      'SV,$X1,$IT            -NEXT'),
    ('006033.00', '6033.40 00',   'BE,$+.32              -BEW TEST'),
    ('006033.40', '6035.20 00',   'ISBE39 BEW,ISBE40     -BEW TILL I. T. SIGNAL'),
    ('006034.00', '6034.04 00',   'BD,$'),
    ('006034.40', '525252.30 00', 'NOP,(8)525252.0       -OFFSET IN Y REGS'),
    ('006035.00', '6035.44 00',   'ISBE40 BD,$+.32       -SET UP'),
    ('006035.40', '1.03 01',      'LVI,$X1,1.0           -FOR'),
    ('006036.00', '1.03 30',      'SV,$X1,$IT            -NEXT'),
    ('006036.40', '6037.00 00',   'BE,$+.32              -BEW TEST'),
    ('006037.00', '6040.20 00',   'ISBE41 BEW,ISBE42     -BEW TILL I. T. SIGNAL'),
    ('006037.40', '6037.44 00',   'BD,$'),
    ('006040.00', '6040.44 00',   'ISBE42 BD,$+.32       -SET UP'),
    ('006040.40', '1.03 01',      'LVI,$X1,1.0           -FOR'),
    ('006041.00', '1.03 30',      'SV,$X1,$IT            -NEXT'),
    ('006041.40', '6042.00 00',   'BE,$+.32              -BEW TEST'),
    ('006042.00', '6043.20 00',   'ISBE43 BEW,ISBE44     -BEW TILL I. T. SIGNAL'),
    ('006042.40', '6042.44 00',   'BD,$'),
    ('006043.00', '6043.44 00',   'ISBE44 BD,$+.32       -SET UP'),
    ('006043.40', '1.03 01',      'LVI,$X1,1.0           -FOR'),
    ('006044.00', '1.03 30',      'SV,$X1,$IT            -SIC,BEW'),
    ('006044.40', '6045.00 00',   'BE,$+.32              -TEST'),
    ('006045.00', '6046.40 80',   'ISBE45 SIC,ISBE46+.32'),
    ('006045.40', '6046.60 00',   'BEW,ISBE46+.32        -SIC + BEW TILL I.T. SIGNAL'),
    ('006046.00', '6047.04 00',   'ISBE46 BD,$+1.0'),
    ('006046.40', '6046.44 00',   'BD,$                  -BD,$+1.0 + BD, ISBE 46'),
    ('006047.00', '1.03 01',      'LVI,$X1,1.0           -SETS UP'),
]

SYMBOLS = {'ISBE37': '006030.40', 'ISBE38': '006031.40',
           'ISBE39': '006033.40', 'ISBE40': '006035.00',
           'ISBE41': '006037.00', 'ISBE42': '006040.00',
           'ISBE43': '006042.00', 'ISBE44': '006043.00',
           'ISBE45': '006045.00', 'ISBE46': '006046.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='BEW '))
