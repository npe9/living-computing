#!/usr/bin/env python3
"""verify_ax5b_160s1_listing.py -- jb_ax5b "I-Box 5", routine 1260's
I60S1 (../decks/ax5b_160s1_clr_inds.strap) against the listing's
printed machine code, PDF pp.83-84, octal 022741.00-023021.00.

THE ROUTINE docs/NEXT.md MYTHOLOGISED.  The file opened with
"Prerequisite: SSIP's I60S1/I60SX1 save/restore harness, reported at
ax5b pp.41-44.  Nothing from 1260 can run without it."  Every clause
was wrong: it is local to routine 1260, not SSIP's; it CLEARS
INDICATORS 0-19 rather than saving and restoring anything; it is at
pp.83-84, not 41-44; and four blocks of 1260 were transcribed without
it.  What it is genuinely needed for is the p.71 COMPARISON driver,
which calls it.

THE SHAPE, once per indicator: branch-on-indicator-and-zero to skip if
already clear, then TI,1,11.0,$X1 -- Transmit Immediate one word FROM
word 11, the indicator register, INTO $X1 -- then KVI against that
indicator's mask and a branch to SERS naming it.  MK, IK, IJ, EK, TS,
CPUS, EKJ, UNRJ, CBJ, EPGK, UK, EE, EOP, CS, then "IND NO. 14".

FIFTEEN USES OF TRANSMIT IMMEDIATE, every one "13.00 80 000021.02 A0",
each a FULL WORD at an ODD half-word.

AND IT FOUND AN ASSEMBLER BUG.  Its one XW row at 023016.00 was the
single mismatch in 45: expected flag byte 46, produced 06.  XW's
fourth operand is THREE bits (IBM 25-27, the index flag plus two
spare) and strap_asm.py masked it to one.  p.114's BIT table settles
it -- BIT25 is "XW,0,0,0,4", BIT26 ",2", BIT27 ",1" -- and the fix is
in strap_asm.py's XW arm.

PROVEN DISCRIMINATING.  Observed failure sets:

  enc_transmit's A1 evaluated as a half-word address (shift 5)
      all fifteen TI rows                              (15 rows)
  INDICATOR_BITS["MK"] 0 -> 1
      022741.40 BMKZ                                   (1 row)
  XW's fourth operand masked back to one bit (& 0x1)
      023016.00 -- the row that found the bug          (1 row)
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_160s1_clr_inds.strap").read())

ROWS = [
    ('022741.00', '23301.03 10',
     'I60S1 SX,$X1,I60DMP (ext) "-SUBROUTINE TO CLR INDS 0-19,"'),
    ('022741.40', '22742.00 46',
     'BMKZ,$+.32            "-AND CHK THAT THEY ARE CLRD."'),
    ('022742.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1         indicators -> $X1'),
    ('022743.00', '400000.03 04',
     'KVI,$X1,(8)400000.0   MK'),
    ('022743.40', '22745.32 42',
     'BXL,$+1.32'),
    ('022744.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022744.40', '1304.10 00',
     'B,SERS                (ext) "-UNABLE TO CLEAR MK."'),
    ('022745.00', '22745.40 C6',
     'BIKZ,$+.32'),
    ('022745.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022746.40', '200000.03 04',
     'KVI,$X1,(8)200000.0   IK'),
    ('022747.00', '22750.72 42',
     'BXL,$+1.32'),
    ('022747.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022750.00', '1304.10 00',
     'B,SERS                (ext) "-UNABLE TO CLR IK OR ABOVE IND."'),
    ('022750.40', '22751.01 46',
     'BIJZ,$+.32'),
    ('022751.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022752.00', '100000.03 04',
     'KVI,$X1,(8)100000.0   IJ'),
    ('022752.40', '22754.32 42',
     'BXL,$+1.32'),
    ('022753.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022753.40', '1304.10 00',
     'B,SERS                (ext) "-UNABLE TO CLR IJ OR ABOVE IND."'),
    ('022754.00', '22754.41 C6',
     'BEKZ,$+.32'),
    ('022754.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022755.40', '40000.03 04',
     'KVI,$X1,(8)40000.0    EK'),
    ('022756.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022756.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR EK OR ABOVE IND."'),
    ('022757.00', '777777.43 01',
     'LVI,$X1,(8)777777.40'),
    ('022757.40', '1.03 30',
     'SV,$X1,1.0'),
    ('022760.00', '22760.42 46',
     'BTSZ,$+.32'),
    ('022760.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022761.40', '20000.03 04',
     'KVI,$X1,(8)20000.0    TS'),
    ('022762.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022762.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR TS OR ABOVE IND."'),
    ('022763.00', '22763.50 00',
     'B,$+.32'),
    ('022763.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022764.40', '10000.03 04',
     'KVI,$X1,(8)10000.0    CPUS'),
    ('022765.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022765.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR CPUS OR ABOVE"'),
    ('022766.00', '22766.43 46',
     'BEKJZ,$+.32'),
    ('022766.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022767.40', '4000.03 04',
     'KVI,$X1,(8)4000.0   EKJ'),
    ('022770.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022770.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR EKJ OR ABOVE IND."'),
    ('022771.00', '22771.43 C6',
     'BUNRJZ,$+.32'),
    ('022771.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022772.40', '2000.03 04',
     'KVI,$X1,(8)2000.0   UNRJ'),
    ('022773.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022773.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR UNRJ OR ABOVE IND."'),
    ('022774.00', '22774.44 46',
     'BCBJZ,$+.32'),
    ('022774.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('022775.40', '1000.03 04',
     'KVI,$X1,(8)1000.0   CBJ'),
    ('022776.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('022776.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR CBJ OR ABOVE IND."'),
    ('022777.00', '22777.44 C6',
     'BEPGKZ,$+.32'),
    ('022777.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023000.40', '400.03 04',
     'KVI,$X1,(8)400.0   EPGK'),
    ('023001.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023001.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR EPGK OR ABOVE IND."'),
    ('023002.00', '23002.45 46',
     'BUKZ,$+.32'),
    ('023002.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023003.40', '200.03 04',
     'KVI,$X1,(8)200.0   UK'),
    ('023004.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023004.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR UK OR ABOVE IND."'),
    ('023005.00', '23005.45 C6',
     'BEEZ,$+.32'),
    ('023005.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023006.40', '100.03 04',
     'KVI,$X1,(8)100.0   EE'),
    ('023007.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023007.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR EE OR ABOVE IND."'),
    ('023010.00', '23010.46 46',
     'BEOPZ,$+.32'),
    ('023010.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023011.40', '40.03 04',
     'KVI,$X1,(8)40.0   EOP'),
    ('023012.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023012.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR EOP OR ABOVE IND."'),
    ('023013.00', '23013.46 C6',
     'BCSZ,$+.32'),
    ('023013.40', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023014.40', '20.03 04',
     'KVI,$X1,(8)20.0   CS'),
    ('023015.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023015.40', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR CS OR ABOVE IND."'),
    ('023016.00', '23017.07 46 000000.30 00',
     'XW,$+1.07,(8)300000,(8)014000,4   the 3-bit flag field'),
    ('023017.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023020.00', '10.03 04',
     'KVI,$X1,(8)10.0       ind 14'),
    ('023020.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023021.00', '1304.32 40',
     'BZXL,SERS             (ext) "-UNABLE TO CLR IND NO. 14 OR ABOVE IND."'),
]

SYMBOLS = {'I60S1': '022741.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 S1 '))
