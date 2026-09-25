#!/usr/bin/env python3
"""verify_ax5b_160_test8c_listing.py -- jb_ax5b "I-Box 5", routine 1260
TEST 8C cases 3 and 4 (programs/ax5b_160_test8c.strap) against the
listing's printed machine code, PDF pp.80-83, octal
022640.40-022733.40.  119 rows, one unbroken half-word run.

THIS IS THE DECK ORACLE FOR DF AND IF, and it corrects a claim this
project built on.  docs/NEXT.md and archival_inventory.md both said
"DF and IF have no deck oracle anywhere read so far"; DF was then
implemented from Reference Manual p.32 alone while this test sat
thirty pages earlier in a document already read.  The false claim came
from correctly disproving that routine 1268 was the oracle and then
widening that result past what it showed.

THE HEADER'S LINE 1 IS A TYPO, settled 2026-09-24 by transcribing
cases 1 and 2 (verify_ax5b_160_test8c_disabled_listing.py).  It reads
"IND" where the code requires the indicator NOT set: cases 1 and 2's
indicator branches are bit-identical in polarity, the failure text
inverts only at case 3, and line 2 of the same header spells DISABL as
"DIAABL".  Build against the code.

TEST 8C's own title, PDF p.76 at 022546.00:

  I60127 LVI,$X1,I60AD1  -TEST 8C CHECKS DF + IF UNDER 4 CONDS,
                         -1. DISABL MASK 0 FETCH OK IND NO INT
                         -2. DIAABL MASK 1 FETCH OK NO IND NO INT
                         -3. ENABLE MASK 0 FETCH OK IND ON NO INT
                         -4. ENABLE MASK 1 NO FETCH IND ON INTRPT

CASES 3 AND 4 ARE THE MASK-DEPENDENT PAIR.  Both enable the system;
case 3 runs with the mask bit ZERO and case 4 with it ONE, which is
exactly p.32's rule -- mask 0 and the operation proceeds, mask 1 and
it is suppressed.  The two cases' error messages are the contract read
against each other: case 3 fails with "WAS NOPED" (it must have
fetched), case 4 with "WAS EXECUTED" (it must not have).

CNOP IS ALIGNMENT-DEPENDENT and is why the cases differ in length.  On
p.80 the preceding BE sits on a .40 half-word, so the next half-word
is already word-aligned and CNOP emits NOTHING -- the address column
steps straight from 022662.40 to 022663.00.  On p.82 the preceding BE
sits on .00, so CNOP emits a filler NOP (0.30 00) at 022722.40.  Case
3 is 56 source lines / 55 code rows; case 4 is 56 / 56.  The assembler
already reproduces both from the same source, which is why the program
keeps CNOP rather than hand-expanding it.

FOUR MORE CONFIRMATIONS OF THE BIT TABLE: 024522 + n gives BIT14 ->
024540, BIT20 -> 024546, BIT21 -> 024547, BIT57 -> 024613.  And since
the deck sets mask bit 20 for the DF half and mask bit 21 for the IF
half, this block is the DECK'S OWN statement that DF is 20 and IF is
21 -- numbering this project had taken from the Reference Manual.

PROVEN DISCRIMINATING.  Observed failure sets:

  INDICATOR_BITS["IF"] 21 -> 22
      022664.00, 022724.00                                   (2 rows)
  INDICATOR_BITS["DF"] 20 -> 19
      022651.40, 022710.40                                   (2 rows)
  the p.80 CNOP hand-expanded to NOP in the source
      4 symbols + every row after it                      (72 rows)

AND THE INJECTION I FIRST WROTE HERE WAS THE WRONG ONE, which is worth
keeping because it is the whole CNOP point in miniature.  I predicted
that hand-expanding the p.82 CNOP would shift case 4 and fail ~12
rows.  Measured: it fails NOTHING.  On p.82 the CNOP already emits a
NOP, so writing NOP instead is the same program.  The discriminating
injection is the p.80 one, where CNOP emits nothing and a hand-written
NOP inserts a half-word that shifts four labels and every row after
it.  Record the observed set, never the predicted one.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_160_test8c.strap").read())

ROWS = [
    ('022640.40', '23063.03 01',
     'I60137 LVI,$X1,I60AD1   (ext) "-TEST 8C,CASE 3."'),
    ('022641.00', '24613.04 10',
     'LX,$X2,LBIT57          (ext)'),
    ('022641.40', '3.05 10',
     'SX,$X2,3.0             boundary control word'),
    ('022642.00', '23064.22 00',
     'Z,I60AD3              (ext)'),
    ('022642.40', '14.22 00',
     'Z,$MASK                 mask 0 for this case'),
    ('022643.00', '23041.00 80',
     'SIC,I60SX1            (ext)'),
    ('022643.40', '22741.10 00',
     'B,I60S1               (ext) SSIP save/restore'),
    ('022644.00', '13.22 00',
     'Z,$IND'),
    ('022644.40', '777777.47 01',
     'LVI,$X3,(8)777777.40'),
    ('022645.00', '1353.11 01',
     'LVI,$X4,LINT           (ext)'),
    ('022645.40', '23201.11 03',
     'LRI,$X4,I60IT         (ext) the 64-word table'),
    ('022646.00', '22653.53 01',
     'LVI,$X5,I60138'),
    ('022646.40', '22372.13 D0',
     'SVA,$X5,I60107        (ext) plant the handler'),
    ('022647.00', '3.03 30',
     'SV,$X1,$UB              upper boundary'),
    ('022647.40', '2.11 70',
     'SR,$X4,$IA'),
    ('022650.00', '22650.40 00',
     'BE,$+.32                enable'),
    ('022650.40', '23064.06 30',
     'LV,$X3,I60AD3         (ext) THE FETCH ABOVE UB'),
    ('022651.00', '22651.44 00',
     'BD,$+.32'),
    ('022651.40', '22653.12 46',
     'BDFZ,$+1.32             DF must be ON'),
    ('022652.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH ABOVE UB, ENABLED, MASK 0,"'),
    ('022652.40', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES DF NOT TO BE SET, NO INT."'),
    ('022653.00', '22654.44 00',
     'BD,$+1.32'),
    ('022653.40', '1310.00 80',
     'I60138 SIC,SEN        (ext) "-INT ON DF, ENABLED, MASK 0, FETCHED"'),
    ('022654.00', '1304.10 00',
     'B,SERS                 (ext) "-ABOVE UB."'),
    ('022654.40', '2.11 30',
     'SV,$X4,$IA'),
    ('022655.00', '23.06 10',
     'LX,$X3,$X3'),
    ('022655.40', '22657.31 42',
     'BXVZ,$+1.32             the fetch must have LANDED'),
    ('022656.00', '1310.00 80',
     'SIC,SEN                (ext) "-UNABLE TO FETCH ABOVE UB WITH"'),
    ('022656.40', '1304.10 00',
     'B,SERS                 (ext) "-MASK 0, SYSTEM ENABLED."'),
    ('022657.00', '22666.05 01',
     'LVI,$X2,I60140'),
    ('022657.40', '3.45 30',
     'SV,$X2,$LB              lower boundary := I60140'),
    ('022660.00', '22666.05 01',
     'LVI,$X2,I60140'),
    ('022660.40', '22372.05 D0',
     'SVA,$X2,I60107        (ext)'),
    ('022661.00', '2.11 70',
     'SR,$X4,$IA'),
    ('022661.40', '777777.05 01',
     'LVI,$X2,(8)777777.0'),
    ('022662.00', '3.05 30',
     'SV,$X2,$UB'),
    ('022662.40', '22663.00 00',
     'BE,$+.32'),
    ('022663.00', '0.04 10',
     'LX,$X2,0               BELOW LB: the monitored fetch'),
    ('022663.40', '22664.04 00',
     'I60139 BD,$+.32'),
    ('022664.00', '22667.12 C6',
     'BIFZ,I60141            IF must be ON'),
    ('022664.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCH BELOW LB FAILS TO"'),
    ('022665.00', '1304.10 00',
     'B,SERS                 (ext) "-SET IF, NO INT, MASK 0, ENABLED."'),
    ('022665.40', '22667.04 00',
     'BD,I60141'),
    ('022666.00', '1310.00 80',
     'I60140 SIC,SEN        (ext) "-INSTRUCT FETCH BELOW LB CAUSES INT,"'),
    ('022666.40', '1304.10 00',
     'B,SERS                 (ext) "-MASK 0, SYSTEM ENABLED."'),
    ('022667.00', '2.11 30',
     'I60141 SV,$X4,$IA'),
    ('022667.40', '22.04 10',
     'LX,$X2,$X2'),
    ('022670.00', '22671.71 42',
     'BXVZ,$+1.32             mask 0: the fetch PROCEEDS'),
    ('022670.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCHED BELOW LB, ENABLED,"'),
    ('022671.00', '1304.10 00',
     'B,SERS                 (ext) "-MASK 0, WAS NOPED."'),
    ('022671.40', '22672.50 00',
     'B,$+1.0'),
    ('022672.00', '22640.44 00',
     "BD,I60137              loop back to case 3's head"),
    ('022672.40', '1311.40 80',
     'SIC,LSEN0+.32          (ext)'),
    ('022673.00', '1301.10 00',
     'B,LSSW                 (ext) "-TO SSIP."'),
    ('022673.40', '22674.04 00',
     'BD,$+.32'),
    ('022674.00', '22737.32 10',
     'LX,$X13,IC260         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('022674.40', '24540.32 B0',
     'V+,$X13,LBIT14         (ext) case 3 done = bit 14'),
    ('022675.00', '22737.33 10',
     'SX,$X13,IC260         (ext)'),
    ('022675.40', '23063.03 01',
     'I60142 LVI,$X1,I60AD1   (ext) "-TEST 8C, CASE 4."'),
    ('022676.00', '24613.04 10',
     'LX,$X2,LBIT57          (ext)'),
    ('022676.40', '3.05 10',
     'SX,$X2,3.0'),
    ('022677.00', '23064.22 00',
     'Z,I60AD3              (ext)'),
    ('022677.40', '22700.04 00',
     'BD,$+.32'),
    ('022700.00', '14.22 00',
     'Z,$MASK'),
    ('022700.40', '23041.00 80',
     'SIC,I60SX1            (ext)'),
    ('022701.00', '22741.10 00',
     'B,I60S1               (ext)'),
    ('022701.40', '13.22 00',
     'Z,$IND'),
    ('022702.00', '777777.47 01',
     'LVI,$X3,(8)777777.40'),
    ('022702.40', '1353.11 01',
     'LVI,$X4,LINT           (ext)'),
    ('022703.00', '23201.11 03',
     'LRI,$X4,I60IT         (ext)'),
    ('022703.40', '22713.53 01',
     'LVI,$X5,I60143'),
    ('022704.00', '22372.13 D0',
     'SVA,$X5,I60107        (ext)'),
    ('022704.40', '3.03 30',
     'SV,$X1,$UB'),
    ('022705.00', '2.11 70',
     'SR,$X4,$IA'),
    ('022705.40', '24546.14 10',
     "LX,$X6,LBIT20          (ext) DF's mask bit"),
    ('022706.00', '14.15 10',
     'SX,$X6,$MASK            MASK 1 for the DF half'),
    ('022706.40', '22707.00 00',
     'BE,$+.32'),
    ('022707.00', '23064.06 30',
     'LV,$X3,I60AD3         (ext) THE FETCH ABOVE UB'),
    ('022707.40', '0.30 00',
     'NOP'),
    ('022710.00', '22710.44 00',
     'BD,$+.32'),
    ('022710.40', '22712.52 46',
     'BDFZ,$+2.0'),
    ('022711.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH ABOVE UB, ENABLED, MASK 1,"'),
    ('022711.40', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES NO INT, DF NOT SET."'),
    ('022712.00', '22713.44 00',
     'BD,I60143'),
    ('022712.40', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH ABOVE UB, ENABLED, MASK 1,"'),
    ('022713.00', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES NO INT, DF SET."'),
    ('022713.40', '2.11 30',
     'I60143 SV,$X4,$IA'),
    ('022714.00', '23.06 10',
     'LX,$X3,$X3'),
    ('022714.40', '22716.31 40',
     'BZXVZ,$+1.32            mask 1: the fetch is SUPPRESSED'),
    ('022715.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCHED ABOVE UB WITH MASK 1"'),
    ('022715.40', '1304.10 00',
     'B,SERS                 (ext) "-AND SYSTEM ENABLED."'),
    ('022716.00', '22727.05 01',
     'LVI,$X2,I60146'),
    ('022716.40', '3.45 30',
     'SV,$X2,$LB'),
    ('022717.00', '22372.05 D0',
     'SVA,$X2,I60107        (ext)'),
    ('022717.40', '2.11 70',
     'SR,$X4,$IA'),
    ('022720.00', '777777.05 01',
     'LVI,$X2,(8)777777.0'),
    ('022720.40', '3.05 30',
     'SV,$X2,$UB'),
    ('022721.00', '24547.14 10',
     "LX,$X6,LBIT21          (ext) IF's mask bit"),
    ('022721.40', '14.15 10',
     'SX,$X6,$MASK            MASK 1 for the IF half'),
    ('022722.00', '22722.40 00',
     'BE,$+.32'),
    ('022722.40', '0.30 00',
     'CNOP                    HERE it emits a NOP; on p.80 it emits nothing'),
    ('022723.00', '0.04 10',
     'LX,$X2,0               BELOW LB'),
    ('022723.40', '22724.04 00',
     'BD,$+.32'),
    ('022724.00', '22726.12 C6',
     'I60144 BIFZ,I60145'),
    ('022724.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCH BELOW LB CAUSES NO"'),
    ('022725.00', '1304.10 00',
     'B,SERS                 (ext) "-INT IF NOT SET, MASK 1, SYSTEM"'),
    ('022725.40', '22727.04 00',
     'BD,I60146              (cont) "-ENABLED."'),
    ('022726.00', '1310.00 80',
     'I60145 SIC,SEN        (ext) "-INSTRUCT FETCH BELOW LB CAUSES NO"'),
    ('022726.40', '1304.10 00',
     'B,SERS                 (ext) "-INT, IF ON, MASK 1, SYSTEM ENABLED."'),
    ('022727.00', '2.11 30',
     'I60146 SV,$X4,$IA'),
    ('022727.40', '22.04 10',
     'LX,$X2,$X2'),
    ('022730.00', '22731.71 40',
     'BZXVZ,$+1.32            mask 1: the fetch is SUPPRESSED'),
    ('022730.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCHED BELOW LB, ENABLED,"'),
    ('022731.00', '1304.10 00',
     'B,SERS                 (ext) "-MASK 1, WAS EXECUTED."'),
    ('022731.40', '22732.50 00',
     'B,$+1.0'),
    ('022732.00', '22675.44 00',
     "BD,I60142              loop back to case 4's head"),
    ('022732.40', '1311.40 80',
     'SIC,LSEN0+.32          (ext)'),
    ('022733.00', '1301.10 00',
     'B,LSSW                 (ext) "-TO SSIP."'),
    ('022733.40', '22734.04 00',
     'BD,$+.32'),]

SYMBOLS = {'I60137': '022640.40', 'I60138': '022653.40',
           'I60139': '022663.40', 'I60140': '022666.00',
           'I60141': '022667.00', 'I60142': '022675.40',
           'I60143': '022713.40', 'I60144': '022724.00',
           'I60145': '022726.00', 'I60146': '022727.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 8C '))
