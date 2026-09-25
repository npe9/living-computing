#!/usr/bin/env python3
"""verify_ax5b_162_exic_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), TEST 2B (programs/ax5b_162_exic_classes.strap)
against the listing's printed machine code, PDF p.101, octal
023742.40-023767.40.  43 half-words.

WHY THIS BLOCK.  Routine 1262 is the deck oracle for EX/EXIC, the
highest-leverage unimplemented instruction in this model -- four
already-located transcription targets wait on it (routine 1268 cases
1B/1C, routine 1260 blocks 16084/16085).  These rows are the first
listing witness in this suite for EXIC's encoding, and for BZXVZ and
BZXE.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

TEST 2B sweeps five instruction classes (DIR IX, IMMED IX, MISC, FLT
PT, FULL WD VFL) from its header at 023705.00 on PDF p.99, checking
three rules per class, each with its own error entry: EXIC to that
class must not interrupt; the subject must actually execute; and the
PSEUDO-IC must be stepped by the SUBJECT'S LENGTH.

THE PSEUDO-IC RULE IS LITERAL.  p.101 shows only ".32", which alone
cannot tell "stepped by the subject's length" from "always .32".  PDF
p.102 settles it -- the FULL WD VFL class checks with "V+I,$X2,1.0"
against "-PSEUDO IC NOT STEPPED 1.0 CORRECTLY / -WHEN SUBJ INST WAS
VFL FULL WD."

DO NOT READ THE CLASS OFF THE ERROR TEXT.  The messages are
clone-and-edit artifacts in BOTH directions: "-WHEN SUBJ INST WAS
IMMED IX." appears below under MISC and under FLT PT, copied from the
IMMED IX block on p.99 where it is correct; and on p.102 the VFL
block's pseudo-IC message was updated while its execute-check message
still says "-SUBJ INST WAS FLT PT".  Class identity comes from the
header comment and the "LX,$X1,<reg>" row.

BZXVZ vs BXVZ IS SEMANTIC and must not be normalised.  MISC does no
Z,$X1/Z,$L/Z,$R beforehand and expects the subject to have zeroed the
index value, so NONZERO is the error (BZXVZ); FLT PT and VFL clear
$L/$R and expect a nonzero result, so ZERO is the error (BXVZ).

THE 162* SYMBOLS ARE INPUTS, NOT WITNESSES -- the same caveat
verify_ax5b_16082_16083_listing.py makes about I6088.  No label row
defining any of them appears on PDF p.101; every address comes from an
OPERAND field.

BUT THEY ARE CORROBORATED ON ANOTHER PAGE, found 2026-09-24 while
transcribing TEST 3A and verified first-hand at 300 dpi.  PDF p.109
carries 1262's constants area and DOES define them in its LABEL
column -- "I62INT DR%BU,64,8@,64  -INTRPT TABLE." among them, the same
64-word shape routine 1260 writes as "I60IT DR%BU,64,8@,64".  That
does not turn an input into a witness for THESE rows, which still make
their addresses come out right by construction; what it does is remove
the worry that a SYN was merely a number chosen to fit.  Two
independent readings of two different pages agree.  Genuinely witnessed by the page's own label column:
I6267 at 023755.40 and I6268 at 023756.40, each confirmed by bit 18
of the row that names it (23755.43 -> .40, 23756.44 -> .40).

PROVEN DISCRIMINATING.  Observed failure sets:

  MISC_CODES["EXIC"] 0b011 -> 0b111
      023754.40, 023767.00                                   (2 rows)
  MISC_CODES["Z"] 0b100 -> 0b101
      023752.00, 023752.40, 023753.40, 023754.00,
      023765.00, 023765.40, 023766.40                        (7 rows)
  DIR_INDEX_CODES["SVA"] one bit
      023747.40, 023750.40, 023762.40, 023763.40             (4 rows)
  INDICATOR_BITS["XVZ"] 50 -> 51
      023744.40, 023757.40                                   (2 rows)
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_exic_classes.strap").read())

ROWS = [
    ('023742.40', '1310.00 80',
     'I6265 SIC,SEN         (ext) "-INT WHEN EXIC TO"'),
    ('023743.00', '1304.10 00',
     'B,SERS                (ext) "-A MISC INSTRUCT."'),
    ('023743.40', '21.02 10',
     'I6266 LX,$X1,$X1'),
    ('023744.00', '1310.00 80',
     'SIC,SEN               (ext) "-SUBJ INST WAS MISC"'),
    ('023744.40', '1304.31 40',
     'BZXVZ,SERS            (ext) "-AND WAS NOT EXECUTED."'),
    ('023745.00', '0.45 05',
     'V+I,$X2,0.32'),
    ('023745.40', '24323.04 90',
     'KV,$X2,I62PSI       (ext) the pseudo-IC after'),
    ('023746.00', '1310.00 80',
     'SIC,SEN               (ext) "-PSEUDO IC NOT STEPPED .32"'),
    ('023746.40', '1304.32 C0',
     'BZXE,SERS             (ext) message is STALE, see header'),
    ('023747.00', '23755.43 01',
     'LVI,$X1,I6267       "-FLT PT."'),
    ('023747.40', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) plant the handler'),
    ('023750.00', '24324.03 01',
     'LVI,$X1,I62SUB      (ext)'),
    ('023750.40', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext) aim the pseudo-IC'),
    ('023751.00', '24330.02 10',
     'LX,$X1,I62EXF       (ext) the FLT PT subject'),
    ('023751.40', '24324.03 10',
     'SX,$X1,I62SUB       (ext)'),
    ('023752.00', '13.22 00',
     'Z,$IND'),
    ('023752.40', '14.22 00',
     'Z,$MASK'),
    ('023753.00', '24323.04 30',
     'LV,$X2,I62PSI       (ext) pseudo-IC BEFORE the EXIC'),
    ('023753.40', '10.22 00',
     'Z,$L'),
    ('023754.00', '11.22 00',
     'Z,$R'),
    ('023754.40', '24323.16 00',
     'EXIC,I62PSI         (ext)'),
    ('023755.00', '23756.44 00',
     'BD,I6268'),
    ('023755.40', '1310.00 80',
     'I6267 SIC,SEN        (ext) "-INT WHEN EXIC TO"'),
    ('023756.00', '1304.10 00',
     'B,SERS                (ext) "-A FLT PT INSTRUCT."'),
    ('023756.40', '10.02 10',
     'I6268 LX,$X1,$L'),
    ('023757.00', '1310.00 80',
     'SIC,SEN               (ext) "-SUBJ INST WAS FLT PT"'),
    ('023757.40', '1304.31 42',
     'BXVZ,SERS             (ext) "-AND WAS NOT EXECUTED."'),
    ('023760.00', '0.45 05',
     'V+I,$X2,0.32'),
    ('023760.40', '24323.04 90',
     'KV,$X2,I62PSI       (ext)'),
    ('023761.00', '1310.00 80',
     'SIC,SEN               (ext) "-PSEUDO IC NOT STEPPED .32"'),
    ('023761.40', '1304.32 C0',
     'BZXE,SERS             (ext) message is STALE'),
    ('023762.00', '23770.03 01',
     'LVI,$X1,I6269       (ext) "-FULL WD VFL."'),
    ('023762.40', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext)'),
    ('023763.00', '24324.03 01',
     'LVI,$X1,I62SUB      (ext)'),
    ('023763.40', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext)'),
    ('023764.00', '24327.02 10',
     'LX,$X1,I62EXV       (ext) the VFL subject'),
    ('023764.40', '24324.03 10',
     'SX,$X1,I62SUB       (ext)'),
    ('023765.00', '13.22 00',
     'Z,$IND'),
    ('023765.40', '14.22 00',
     'Z,$MASK'),
    ('023766.00', '24323.04 30',
     'LV,$X2,I62PSI       (ext)'),
    ('023766.40', '11.22 00',
     'Z,$R                    no Z,$L: a VFL full word writes $R'),
    ('023767.00', '24323.16 00',
     'EXIC,I62PSI         (ext)'),
    ('023767.40', '23771.04 00',
     'BD,I6270            (ext) PDF p.102'),]

SYMBOLS = {'I6267': '023755.40', 'I6268': '023756.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 2B '))
