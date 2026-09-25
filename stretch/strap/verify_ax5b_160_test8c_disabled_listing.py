#!/usr/bin/env python3
"""verify_ax5b_160_test8c_disabled_listing.py -- jb_ax5b "I-Box 5",
routine 1260 TEST 8C cases 1 and 2
(programs/ax5b_160_test8c_disabled.strap) against the listing's printed
machine code, PDF pp.76-78, octal 022546.00-022636.40.  114 rows, one
unbroken half-word run.  (This deck's listing pages carry no printed
page numbers; citations here are by PDF page.)

THE CONTROLS FOR THE DF/IF DECK ORACLE.
verify_ax5b_160_test8c_listing.py holds cases 3 and 4, which run the
interruption system ENABLED and are the mask-dependent pair.  These two
run it DISABLED and check that neither indicator sets and no interrupt
is taken -- the negative half of the same contract.

TEST 8C's own title, PDF p.76 at 022546.00, verbatim:

  I60127 LVI,$X1,I60AD1  -TEST 8C CHECKS DF + IF UNDER 4 CONDS,
                         -1. DISABL MASK 0 FETCH OK IND NO INT
                         -2. DIAABL MASK 1 FETCH OK NO IND NO INT
                         -3. ENABLE MASK 0 FETCH OK IND ON NO INT
                         -4. ENABLE MASK 1 NO FETCH IND ON INTRPT

LINE 1'S "IND" IS WRONG -- the code requires the indicator NOT set,
and this transcription settles a question that was open in the project.
The decisive evidence is case 1 read against case 2, not case 1 alone:

  * The two cases' indicator branches are bit-identical in polarity --
    case 1 BZDFZ "22560.12 44" / BZIFZ "22574.12 C4", case 2 BZDFZ
    "22615.52 44" / BZIFZ "22632.12 C4".  Same 44 / C4 low byte, same
    branch-on-zero bit.  Whatever BZ's polarity is, the two cases
    assert the SAME thing about the indicator -- so "IND" on line 1
    cannot be right unless "NO IND" on line 2 is also wrong.
  * The failure text inverts exactly where the expectation inverts.
    Cases 1 and 2 both print "-CAUSES DF TO BE SET, NO INT."; case 3,
    whose header line says "IND ON", prints "-CAUSES DF NOT TO BE SET,
    NO INT."  SIC,SEN / B,SERS is an error report, so the text names
    the anomaly.
  * The header block is demonstrably typo-prone: line 2 spells DISABL
    as "DIAABL".  Line 1 is missing its "NO".

Independently: the mnemonic grammar is B[Z]<indicator>[Z], the leading
Z branches when the indicator is OFF, and in both cases the branch is
the OK path while the fall-through is the error.

CASES 1 AND 2 ARE NOT REDUNDANT.  Disabled, the deck asserts the mask
bit is IRRELEVANT.  Case 2 sets DF's and IF's mask bits to ONE and
still demands the fetch proceed ("-UNABLE TO FETCH ABOVE UB WITH /
-MASK 1, SYSTEM DISABLED.", "-INSTRUCT FETCHED BELOW LB, DISABLED, /
-MASK 1, WAS NOPED."), where case 4 -- enabled, mask 1 -- demands the
same fetch be suppressed.

CNOP IS ALIGNMENT-DEPENDENT, AND HERE IT IS INVERTED RELATIVE TO CASES
3 AND 4.  In case 1 SV,$X2,$UB sits at 022567.00, the next half-word
022567.40 is not word-aligned, and CNOP EMITS a filler NOP (0.30 00)
there: 57 source lines / 57 code rows.  In case 2 SV,$X2,$UB sits at
022625.40, 022626.00 is already aligned, and CNOP EMITS NOTHING -- the
address column steps straight from 022625.40 to 022626.00: 58 source
lines / 57 code rows.  In cases 3 and 4 the silent CNOP was the
EARLIER case; here it is the LATER one.  The assembler reproduces both
from the same source, which is why the program keeps CNOP rather than
hand-expanding it.

THE INDICATOR NUMBERS ARE IN THE PRINT, straddling the two fields
(bits 19-24: bits 18-23 are the octal pair, bit 24 is the top bit of
the hex pair).
  BZDFZ "12 44": 001010 / 0x44=01000100 -> bits 19-24 = 010100 = 20
  BZIFZ "12 C4": 001010 / 0xC4=11000100 -> bits 19-24 = 010101 = 21
DF is 20 and IF is 21, said by the deck -- matching the mask bits
(BIT20, BIT21) case 2 loads, and matching the sibling file.

A FIFTH BIT-TABLE CONFIRMATION: 024522 + 12 = 024536, printed at
022601.40 as "24536.32 B0".  The sibling file confirmed BIT14, BIT20,
BIT21 and BIT57 the same way.

WHAT IS AND IS NOT CHECKED HERE.  A SYN IS AN INPUT TO THE CHECK, NOT
A WITNESS.  Every SYN in the program was derived by reading bit 18 out
of the octal pair of the row that names it, so those rows re-verify
only the opcode and modifier bits; they are marked "(ext)" below.  The
rows that really check address placement are the ones naming I60127
.. I60136, which are defined INSIDE the transcribed range.  Twelve
such references resolve to in-range labels, and each was read off bit
18 against the page's own label column:

  case 1  LVI,$X5,I60128  022554.00 -> 22560.53, pair 53, bit18=1
                                     -> 022560.40 = label I60128
          LVI,$X2,I60129  022564.00 -> 22571.05, pair 05, bit18=0
                                     -> 022571.00 = label I60129
          LVI,$X2,I60130  022565.00 -> 22573.05, pair 05, bit18=0
                                     -> 022573.00 = label I60130
          BZIFZ,I60131    022571.00 -> 22574.12, pair 12, bit18=0
                                     -> 022574.00 = label I60131
          BD,I60131       022572.40 -> 22574.04, pair 04, bit18=0
                                     -> 022574.00 = label I60131
          BD,I60127       022577.00 -> 22546.04, pair 04, bit18=0
                                     -> 022546.00 = label I60127
  case 2  LVI,$X5,I60133  022611.40 -> 22616.13, pair 13, bit18=0
                                     -> 022616.00 = label I60133
          LVI,$X2,I60134  022621.40 -> 22627.05, pair 05, bit18=0
                                     -> 022627.00 = label I60134
          LVI,$X2,I60135  022623.40 -> 22631.05, pair 05, bit18=0
                                     -> 022631.00 = label I60135
          BZIFZ,I60136    022627.00 -> 22632.12, pair 12, bit18=0
                                     -> 022632.00 = label I60136
          BD,I60136       022630.40 -> 22632.04, pair 04, bit18=0
                                     -> 022632.00 = label I60136
          BD,I60132       022635.00 -> 22602.44, pair 44, bit18=1
                                     -> 022602.40 = label I60132

PROVEN DISCRIMINATING.  Observed failure sets -- measured, not
predicted:

  INDICATOR_BITS["IF"] 21 -> 22
      022571.00  got '022574.13 44', want '022574.12 C4'
      022627.00  got '022632.13 44', want '022632.12 C4'   (2 rows)
  INDICATOR_BITS["DF"] 20 -> 19
      022556.40  got '022560.11 C4', want '022560.12 44'
      022614.00  got '022615.51 C4', want '022615.52 44'   (2 rows)
  UNCOND_BRANCH_CODES["NOP"] 0b110 -> 0b111
      022567.40 (the case-1 CNOP filler), 022570.40, 022626.40
      each got '000000.34 00' for '000000.30 00'           (3 rows)
  UNCOND_BRANCH_CODES["BD"] 0b001 -> 0b101
      022550.00 022560.00 022572.40 022577.00 022600.40
      022602.40 022605.00 022615.40 022630.40 022635.00
      022636.40  -- every BD in the block                 (11 rows)

THE NOP INJECTION IS ALSO THE CNOP CROSS-CHECK.  It fails three rows,
not two: the two written NOPs and the CNOP filler at 022567.40, which
proves the case-1 CNOP really does route through the NOP encoding.
Case 2's CNOP contributes nothing to the failure set, because on that
alignment it emits nothing at all.  That asymmetry inside a single
injection is the alignment rule measured rather than asserted.

ONE TRANSCRIPTION NOTE.  PDF p.77's 022600.40 prints its source as
"BD,$+.32." with a trailing period.  The encoding 22601.04 00 resolves
to 022601.00, i.e. plain $+.32, so the period is not part of the
operand and the program writes "BD, $+.32".
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_160_test8c_disabled.strap").read())

ROWS = [
    # ---- CASE 1: disabled, mask 0 (PDF pp.76-77) ----
    ('022546.00', '23063.03 01',
     'I60127 LVI,$X1,I60AD1   (ext) "-TEST 8C CHECKS DF + IF UNDER 4 CONDS,"'),
    ('022546.40', '24613.04 10',
     'LX,$X2,LBIT57          (ext)'),
    ('022547.00', '3.05 10',
     'SX,$X2,3.0             boundary control word'),
    ('022547.40', '23064.22 00',
     'Z,I60AD3              (ext)'),
    ('022550.00', '22550.44 00',
     'BD,$+.32                DISABLE the interruption system'),
    ('022550.40', '14.22 00',
     'Z,$MASK                 mask 0 for this case'),
    ('022551.00', '23041.00 80',
     'SIC,I60SX1            (ext)'),
    ('022551.40', '22741.10 00',
     'B,I60S1               (ext) SSIP save/restore'),
    ('022552.00', '13.22 00',
     'Z,$IND'),
    ('022552.40', '777777.47 01',
     'LVI,$X3,(8)777777.40'),
    ('022553.00', '1353.11 01',
     'LVI,$X4,LINT           (ext)'),
    ('022553.40', '23201.11 03',
     'LRI,$X4,I60IT         (ext) the 64-word table'),
    ('022554.00', '22560.53 01',
     'LVI,$X5,I60128'),
    ('022554.40', '22372.13 D0',
     'SVA,$X5,I60107        (ext) plant the handler'),
    ('022555.00', '3.03 30',
     'SV,$X1,$UB              upper boundary'),
    ('022555.40', '2.11 70',
     'SR,$X4,$IA'),
    ('022556.00', '23064.06 30',
     'LV,$X3,I60AD3         (ext) THE FETCH ABOVE UB'),
    ('022556.40', '22560.12 44',
     'BZDFZ,$+1.32            DF must be OFF (indicator 20)'),
    ('022557.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH ABOVE UB, DISABLED, MASK 0,"'),
    ('022557.40', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES DF TO BE SET, NO INT."'),
    ('022560.00', '22561.44 00',
     'BD,$+1.32'),
    ('022560.40', '1310.00 80',
     'I60128 SIC,SEN        (ext) "-ENTER HERE FROM INT."'),
    ('022561.00', '1304.10 00',
     'B,SERS                 (ext) "-INT ON DF, DISABLED MASK 0, FETCH"'),
    ('022561.40', '2.11 30',
     'SV,$X4,$IA              (the "-ABOVE UB." line prints no code)'),
    ('022562.00', '23.06 10',
     'LX,$X3,$X3'),
    ('022562.40', '22564.31 42',
     'BXVZ,$+1.32             the fetch must have LANDED'),
    ('022563.00', '1310.00 80',
     'SIC,SEN                (ext) "-UNABLE TO FETCH ABOVE UB WITH"'),
    ('022563.40', '1304.10 00',
     'B,SERS                 (ext) "-MASK 0, SYSTEM DISABLED."'),
    ('022564.00', '22571.05 01',
     'LVI,$X2,I60129'),
    ('022564.40', '3.45 30',
     'SV,$X2,$LB              lower boundary := I60129'),
    ('022565.00', '22573.05 01',
     'LVI,$X2,I60130'),
    ('022565.40', '22372.05 D0',
     'SVA,$X2,I60107        (ext)'),
    ('022566.00', '2.11 70',
     'SR,$X4,$IA'),
    ('022566.40', '777777.05 01',
     'LVI,$X2,(8)777777.0'),
    ('022567.00', '3.05 30',
     'SV,$X2,$UB'),
    ('022567.40', '0.30 00',
     'CNOP                    HERE it emits a NOP; in case 2 it emits nothing'),
    ('022570.00', '0.04 10',
     'LX,$X2,0               BELOW LB: the monitored fetch'),
    ('022570.40', '0.30 00',
     'NOP'),
    ('022571.00', '22574.12 C4',
     'I60129 BZIFZ,I60131   IF must be OFF (indicator 21)'),
    ('022571.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCH BELOW LB SETS"'),
    ('022572.00', '1304.10 00',
     'B,SERS                 (ext) "-IF, NO INT, MASK 0, DISABLED."'),
    ('022572.40', '22574.04 00',
     'BD,I60131'),
    ('022573.00', '1310.00 80',
     'I60130 SIC,SEN        (ext) "-INSTRUCT FETCH BELOW LB CAUSES"'),
    ('022573.40', '1304.10 00',
     'B,SERS                 (ext) "-INT, MASK 0, DISABLED."'),
    ('022574.00', '2.11 30',
     'I60131 SV,$X4,$IA'),
    ('022574.40', '22.04 10',
     'LX,$X2,$X2'),
    ('022575.00', '22576.71 42',
     'BXVZ,$+1.32             disabled: the fetch PROCEEDS'),
    ('022575.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCHED BELOW LB, DISABLED,"'),
    ('022576.00', '1304.10 00',
     'B,SERS                 (ext) "-MASK 0, WAS NOPED."'),
    ('022576.40', '22577.50 00',
     'B,$+1.0'),
    ('022577.00', '22546.04 00',
     "BD,I60127              loop back to case 1's head"),
    ('022577.40', '1311.40 80',
     'SIC,LSEN0+.32          (ext)'),
    ('022600.00', '1301.10 00',
     'B,LSSW                 (ext)'),
    ('022600.40', '22601.04 00',
     'BD,$+.32                the page prints "BD,$+.32." -- period not encoded'),
    ('022601.00', '22737.32 10',
     'LX,$X13,IC260         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('022601.40', '24536.32 B0',
     'V+,$X13,LBIT12         (ext) case 1 done = bit 12'),
    ('022602.00', '22737.33 10',
     'SX,$X13,IC260         (ext)'),
    # ---- CASE 2: disabled, mask 1 (PDF p.78) ----
    ('022602.40', '22603.04 00',
     'I60132 BD,$+.32        "-TEST 8C, CASE 2."'),
    ('022603.00', '23063.03 01',
     'LVI,$X1,I60AD1        (ext)'),
    ('022603.40', '24613.04 10',
     'LX,$X2,LBIT57          (ext)'),
    ('022604.00', '3.05 10',
     'SX,$X2,3.0'),
    ('022604.40', '23064.22 00',
     'Z,I60AD3              (ext)'),
    ('022605.00', '22605.44 00',
     'BD,$+.32                DISABLE'),
    ('022605.40', '24546.04 10',
     "LX,$X2,LBIT20          (ext) DF's mask bit"),
    ('022606.00', '14.05 10',
     'SX,$X2,$MASK            MASK 1 for the DF half'),
    ('022606.40', '23041.00 80',
     'SIC,I60SX1            (ext)'),
    ('022607.00', '22741.10 00',
     'B,I60S1               (ext)'),
    ('022607.40', '13.22 00',
     'Z,$IND'),
    ('022610.00', '777777.47 01',
     'LVI,$X3,(8)777777.40'),
    ('022610.40', '1353.11 01',
     'LVI,$X4,LINT           (ext)'),
    ('022611.00', '23201.11 03',
     'LRI,$X4,I60IT         (ext)'),
    ('022611.40', '22616.13 01',
     'LVI,$X5,I60133'),
    ('022612.00', '22372.13 D0',
     'SVA,$X5,I60107        (ext)'),
    ('022612.40', '3.03 30',
     'SV,$X1,$UB'),
    ('022613.00', '2.11 70',
     'SR,$X4,$IA'),
    ('022613.40', '23064.06 30',
     'LV,$X3,I60AD3         (ext) THE FETCH ABOVE UB'),
    ('022614.00', '22615.52 44',
     'BZDFZ,$+1.32            DF must be OFF even with mask 1'),
    ('022614.40', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH ABOVE UB, DISABLED, MASK 1,"'),
    ('022615.00', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES DF TO BE SET, NO INT."'),
    ('022615.40', '22617.04 00',
     'BD,$+1.32'),
    ('022616.00', '1310.00 80',
     'I60133 SIC,SEN        (ext) "-FETCH ABOVE UB, DISABLED, MASK 1, CAUSES"'),
    ('022616.40', '1304.10 00',
     'B,SERS                 (ext) "-INTERRUPT."'),
    ('022617.00', '2.11 30',
     'SV,$X4,$IA'),
    ('022617.40', '23.06 10',
     'LX,$X3,$X3'),
    ('022620.00', '22621.71 42',
     'BXVZ,$+1.32             disabled: the fetch LANDS even at mask 1'),
    ('022620.40', '1310.00 80',
     'SIC,SEN                (ext) "-UNABLE TO FETCH ABOVE UB WITH"'),
    ('022621.00', '1304.10 00',
     'B,SERS                 (ext) "-MASK 1, SYSTEM DISABLED."'),
    ('022621.40', '22627.05 01',
     'LVI,$X2,I60134'),
    ('022622.00', '3.45 30',
     'SV,$X2,$LB              lower boundary := I60134'),
    ('022622.40', '24547.04 10',
     "LX,$X2,LBIT21          (ext) IF's mask bit"),
    ('022623.00', '14.05 10',
     'SX,$X2,$MASK            MASK 1 for the IF half'),
    ('022623.40', '22631.05 01',
     'LVI,$X2,I60135'),
    ('022624.00', '22372.05 D0',
     'SVA,$X2,I60107        (ext)'),
    ('022624.40', '2.11 70',
     'SR,$X4,$IA'),
    ('022625.00', '777777.05 01',
     'LVI,$X2,(8)777777.0'),
    ('022625.40', '3.05 30',
     'SV,$X2,$UB              (the CNOP that follows prints NO code row)'),
    ('022626.00', '0.04 10',
     'LX,$X2,0               BELOW LB'),
    ('022626.40', '0.30 00',
     'NOP'),
    ('022627.00', '22632.12 C4',
     'I60134 BZIFZ,I60136   IF must be OFF even with mask 1'),
    ('022627.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCH BELOW LB SETS"'),
    ('022630.00', '1304.10 00',
     'B,SERS                 (ext) "-IF, NO INT, MASK 1, DISABLED."'),
    ('022630.40', '22632.04 00',
     'BD,I60136'),
    ('022631.00', '1310.00 80',
     'I60135 SIC,SEN        (ext) "-INSTRUCT FETCH BELOW LB CAUSES"'),
    ('022631.40', '1304.10 00',
     'B,SERS                 (ext) "-INT, MASK 1, DISABLED."'),
    ('022632.00', '2.11 30',
     'I60136 SV,$X4,$IA'),
    ('022632.40', '22.04 10',
     'LX,$X2,$X2'),
    ('022633.00', '22634.71 42',
     'BXVZ,$+1.32             disabled: the fetch PROCEEDS'),
    ('022633.40', '1310.00 80',
     'SIC,SEN                (ext) "-INSTRUCT FETCHED BELOW LB, DISABLED,"'),
    ('022634.00', '1304.10 00',
     'B,SERS                 (ext) "-MASK 1, WAS NOPED."'),
    ('022634.40', '22635.50 00',
     'B,$+1.0'),
    ('022635.00', '22602.44 00',
     "BD,I60132              loop back to case 2's head"),
    ('022635.40', '1311.40 80',
     'SIC,LSEN0+.32          (ext)'),
    ('022636.00', '1301.10 00',
     'B,LSSW                 (ext) "-TO SSIP."'),
    ('022636.40', '22637.04 00',
     'BD,$+.32'),]

SYMBOLS = {'I60127': '022546.00', 'I60128': '022560.40',
           'I60129': '022571.00', 'I60130': '022573.00',
           'I60131': '022574.00', 'I60132': '022602.40',
           'I60133': '022616.00', 'I60134': '022627.00',
           'I60135': '022631.00', 'I60136': '022632.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 8C-D '))
