#!/usr/bin/env python3
"""verify_ax5b_162_test1b_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), TEST 1B (../decks/ax5b_162_test1b.strap) against
the listing's printed machine code, PDF pp.90-91, octal
023373.40-023442.00.  76 rows, entry label I6212.

THIS IS THE ACCEPTANCE TEST FOR EX.  Its twin TEST 2B
(verify_ax5b_162_exic_listing.py) brought EXIC into this suite; every
other mnemonic on these two pages is already witnessed elsewhere here
-- SR by verify_ax5b_160_test8b/8c, BZXCZ and BXCZ by
verify_ibox1_listing, BRZ and L(BU) by verify_ax5b_160_test8b, BZXVZ
and BZXE by TEST 2B, SVA/KV/LV/V+ throughout.  EX is the one bit
pattern nothing in this suite had printed before, and it appears five
times below.  Checked, not assumed: grepping every strap/*.py and every
../decks/*.strap for MISC_CODES["EX"] and for a bare "EX," operand
finds no occurrence outside these two new files -- the only other
mention anywhere is ax5b_1681_if_close_to_ds.strap's header line "1B
and 1C need EX, deferred in docs/NEXT.md section 5", which is exactly
the gap this file closes.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

WHAT TEST 1B DOES.  It sweeps the five instruction classes of TEST 2B
-- DIR IX, IMMED IX, MISC, FLT PT, FULL WD VFL -- in the same order,
asking TWO questions of each, not three: did the subject instruction
take effect, and did EX leave the subject word intact?  The second is
checked against a master copy, with LV/KV in the DIR IX block and KV
alone in the other four.

WHY ONLY TWO.  2B's third rule is "EXIC to this class must not
interrupt", reached by planting a handler address in the interrupt
entry I62ITE.  1B plants an address in I62ITE too, but in all five
classes it is the row IMMEDIATELY AFTER the EX -- 023377.00 -> I6213 at
023377.40, 023406.40 -> I6214 at 023407.00, 023415.00 -> I6215 at
023415.40, 023423.40 -> I6216 at 023424.00, 023432.40 -> I6217 at
023433.00.  An interruption and an ordinary fall-through land in the
same place, so no separate "-INT WHEN EX TO" message is possible.  Each
of those five is a bit-18 decode confirmed against the page's own label
column; they are listed again under THE FIVE ADDRESS WITNESSES.

THE REPORTED ERROR TEXT IS INCONSISTENT AND IS NOT NORMALISED.  Read
first-hand off the comment column at 600 dpi:

  DIR IX    "-UNABLE TO EX DIR IX INST."      "-EX DESTROYED SUBJ INST."
  IMMED IX  "-UNABLE TO EX IMMED IX INSTR."   "-EX DESTROYED SUBJ INST."
  MISC      "-UNABLE TO EX MISC INSTR."       "-EX DESTROYED SUBJ INSTR."
  FLT PT    "-UNABLE TO EX FP INST."          "-EX DESTROYED SUBJ INST."
  FULL WD   "-UNABLE TO EX FULL WD VFL INST." "-EX DESTROYS SUBJ INST."

"INST." against "INSTR.", "DESTROYED" against "DESTROYS", inside one
block of one routine.  The class headers vary the same way: "-IMMED
IX.", "-MISC." and "-FULL WD." carry a period, "-FLT PT" does not, and
"-TO SSIP" at 023440.00 has none where the same row on PDF p.110 prints
"-TO SSIP.".

BZXVZ PLAYS TWO OPPOSITE ROLES.  In DIR IX and IMMED IX it SKIPS the
error: "BZXVZ,$+2.0 / BZXCZ,$+1.32" both land on the check-(b) row
(023402.00 and 023411.40 -- decoded below), jumping over the two-row
error entry when the index value or count came out non-zero.  In MISC
it is the jump TO the error.  The polarity is TEST 2B's argument
transferred: MISC does no "Z,$X1" of its own and its subject
(I62EXM = "Z,$X1", PDF p.109) is meant to zero the value, so there a
non-zero value is the failure.

THE Z,$R / Z,$L ORDER INVERTS between the two accumulator classes, and
the rows below print it as the page does: FLT PT clears $R (023422.40)
then $L (023423.00); FULL WD VFL clears $L (023431.40) then $R
(023432.00).  Both orders assemble to the same two encodings, so this
check would pass if they were swapped -- which is why the order is
stated.

NO CNOP IN THIS RANGE.  Both full-word L(BU) rows fall on word
boundaries by ordinary flow, 023424.00 and 023433.00, so no alignment
pseudo-op was needed.  PDF p.109's constants area is full of CNOPs;
pp.90-91 have none.

THE SUBJECT CONSTANTS ARE DEFINED ON PDF pp.109-110, whose label column
was read at 600 dpi for this file and confirms eight SYNs: I62ITE
"BD,$  -ALL INTERRUPTS ENTER HERE." 024320.00; I62EXT "XW,0,0,0"
024321.00; I62EX "LX,$X1,I00O" 024322.00; I62XW1 "XW,0,64,I62INT"
024326.00; I62EXV "L%BU@,I00O  -VFL FULL WD." 024327.00; I62EXF
"L%U@,I00O  -FLT PT." 024330.00; I62EXM "Z,$X1  -MISC." 024331.00; and
on p.110's top line I62EXI "LVI,$X1,%8@777777.40  -IMMED IX."
024332.00.  "I00O" is a symbol, not one thousand -- it is the
constant-pool name ../decks/ax5b_160_test8b.strap's header already
places at 024503.00, the address those three rows actually print.

BUT THE SYN'd ROWS ARE STILL NOT THE WITNESS -- the caveat
verify_ax5b_16082_16083_listing.py makes about I6088.  Every SYN in
the program file is an INPUT: it makes the address field come out right
by construction, so those rows prove only that this assembler places
every OTHER field where the listing places it.  Three tiers, and none
of them converts an input into a witness:

  * I62ITE/I62EXT/I62EX/I62XW1/I62EXV/I62EXF/I62EXM/I62EXI -- confirmed
    by a separately read page's own label column (pp.109-110, above).
  * SEN 001310.00, SERS 001304.00, SEN0 001311.00, SSW 001301.00,
    BIT1 024523.00 -- rest on other verify/program files in this repo
    (ax5b_160_test8b.strap gives LSEN0/LSSW; ax5b_1258_test2.strap
    places BIT1 at 024523 from PDF p.114), not on a page read for this
    block.  SEN0 and SSW do get an incidental second printing on PDF
    p.110, read at 600 dpi for this file: "SIC,SENO+.32" prints
    "1311.40 80" at 024360.40 and "B,SSW" prints "1301.10 00" at
    024361.00, bit for bit what 023437.40 and 023440.00 print here.
    A GLYPH CAVEAT THAT CHANGES NO BIT: the fourth character of SEN0
    reads as a letter O on both pages, so the symbol may really be
    "SENO" -- ../decks/ax5b_160_test8b.strap measured it at 54 px on
    PDF p.114 and kept the digit spelling anyway.  Kept as SEN0 here
    for the same reason, and harmless either way: it is a SYN taken
    from the row that names it.
  * IC262 024171.00 -- rests on nothing but the operand field of
    023441.00/023442.00 on these pages.  Said plainly rather than
    lumped in with the rest.

THE FIVE ADDRESS WITNESSES are the labels DEFINED inside the
transcribed range, I6213 through I6217, each one decoded out of the
printed octal pair by BIT 18 and matched against the page's own label
column.  That is a far richer set than TEST 3A's two.

  023374.00  "LVI,$X2,I6213" -> 23377.45 01.  Pair 45 = 100101, bit 18
             = 1, so .40: 023377.40 -- where p.90 prints I6213.
  023404.40  "LVI,$X2,I6214" -> 23407.05 01.  Pair 05 = 000101, bit 18
             = 0, so .00: 023407.00 -- where p.90 prints I6214.
  023413.00  "LVI,$X1,I6215" -> 23415.43 01.  Pair 43 = 100011, bit 18
             = 1, so .40: 023415.40 -- where p.90 prints I6215.
  023420.40  "LVI,$X1,I6216" -> 23424.03 01.  Pair 03 = 000011, bit 18
             = 0, so .00: 023424.00 -- where p.91 prints I6216.
  023427.40  "LVI,$X1,I6217" -> 23433.03 01.  Pair 03 = 000011, bit 18
             = 0, so .00: 023433.00 -- where p.91 prints I6217.

I6212 is deliberately NOT a sixth.  The program's SLC sets the counter
to 023373.40 and I6212 is the first label after it, so asserting it
checks the SLC against the number this transcription handed the SLC.
It is asserted below as the block's anchor; it is not evidence.  Nor is
"BD,I6212" at 023437.00 an independent address witness: its own
LOCATION is one (it is right only if all 69 preceding rows were sized
right), but its TARGET traces straight back to that same SLC.  Its
decode is recorded anyway because it is the only backward branch here:
23373.44 00, pair 44 = 100100, bit 18 = 1 -> 023373.40.

FOUR MORE BIT-18 DECODES, for the self-relative rows whose addresses
come from neither a SYN nor a label -- the location counter's own
witnesses:

  023400.00  "BZXVZ,$+2.0"  -> 23402.31 40.  Pair 31 = 011001, bit 18
             = 0 -> 023402.00, and 023400.00 + 2 words = 023402.00,
             the "LV,$X1,I62EXT" row.
  023400.40  "BZXCZ,$+1.32" -> 23402.30 40.  Pair 30 = 011000, bit 18
             = 0 -> 023402.00.  The same target as the row above it:
             both skips land on the check-(b) row.
  023407.40  "BZXVZ,$+2.0"  -> 23411.71 40.  Pair 71 = 111001, bit 18
             = 1 -> 023411.40, the IMMED IX "KV,$X2,I62EXT" row.  Note
             the pair differs from 023400.00's 31 ONLY in bit 18: the
             indicator number is identical, the half-word select is
             not.
  023436.40  "B,$+1.0"      -> 23437.50 00.  Pair 50 = 101000, bit 18
             = 1 -> 023437.40, the "SIC,SEN0+.32" row.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted -- each
injection was made into strap/opcodes.py with __pycache__ cleared on
BOTH sides of the run:

  MISC_CODES["EX"] 0b010 -> 0b110
      023377.00, 023406.40, 023415.00, 023423.40, 023432.40  (5 rows)
      The block's reason to exist: all five EX rows, one per class.
  DIR_INDEX_CODES["SR"] 0b10111 -> 0b10110
      023375.40  SR,$X2,$IA -> "2.05 60"                     (1 row)
      The one field nothing else in this block exercises; SR appears
      exactly once, in the DIR IX setup.
  INDICATOR_BITS["XCZ"] 48 -> 49
      023400.40, 023410.00                                   (2 rows)
      Both BZXCZ rows, and only those -- XVZ (50) rows are untouched.
  INDICATOR_BITS["RZ"] 57 -> 14
      023425.40, 023434.40  BRZ -> "1304.07 42"              (2 rows)
      The two BRZ rows, the FP and VFL execute-checks.  14 and not a
      one-bit flip on purpose: every single-bit neighbour of 57 is
      already some other indicator's number (56 RLZ, 59 RN, 61 AE, 41
      PG0, 25 IR), and a duplicate value would have been a table
      collision rather than a clean perturbation.  14 is the one number
      in 0-63 that INDICATOR_BITS does not hold.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_162_test1b.strap").read())

ROWS = [
    # ---- DIR IX, PDF p.90 -------------------------------------------
    ('023373.40', '21.22 00',
     'I6212 Z,$X1          "-TEST 1B, CHK EX OF EACH TYPE OF"'),
    ('023374.00', '23377.45 01',
     'LVI,$X2,I6213        "-INSTRUCTION, DIR IX."; bit 18 -> 023377.40'),
    ('023374.40', '24320.05 D0',
     'SVA,$X2,I62ITE       (ext) plant the post-EX row as the handler'),
    ('023375.00', '24326.04 10',
     'LX,$X2,I62XW1        (ext) p.109: XW,0,64,I62INT'),
    ('023375.40', '2.05 70',
     'SR,$X2,$IA            the Interruption Address register'),
    ('023376.00', '24322.04 10',
     'LX,$X2,I62EX         (ext) the DIR IX subject, p.109'),
    ('023376.40', '24321.05 10',
     'SX,$X2,I62EXT        (ext) into the subject slot'),
    ('023377.00', '24321.12 00',
     'EX,I62EXT            (ext) THE INSTRUCTION UNDER TEST'),
    ('023377.40', '21.02 10',
     'I6213 LX,$X1,$X1     (a) did the subject take effect?'),
    ('023400.00', '23402.31 40',
     'BZXVZ,$+2.0           self-relative: +2 words -> 023402.00'),
    ('023400.40', '23402.30 40',
     'BZXCZ,$+1.32          +1 word +32 bits -> 023402.00, same target'),
    ('023401.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023401.40', '1304.10 00',
     'B,SERS                (ext) "-UNABLE TO EX DIR IX INST."'),
    ('023402.00', '24321.02 30',
     'LV,$X1,I62EXT        (ext) (b) is the subject word intact?'),
    ('023402.40', '24322.02 90',
     'KV,$X1,I62EX         (ext) compare against the master copy'),
    ('023403.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023403.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-EX DESTROYED SUBJ INST."'),
    # ---- IMMED IX ---------------------------------------------------
    ('023404.00', '21.22 00',
     'Z,$X1                 "-IMMED IX."'),
    ('023404.40', '23407.05 01',
     'LVI,$X2,I6214        bit 18 -> 023407.00'),
    ('023405.00', '24320.05 D0',
     'SVA,$X2,I62ITE       (ext)'),
    ('023405.40', '24332.04 10',
     'LX,$X2,I62EXI        (ext) the IMMED IX subject, PDF p.110'),
    ('023406.00', '24321.05 10',
     'SX,$X2,I62EXT        (ext)'),
    ('023406.40', '24321.12 00',
     'EX,I62EXT            (ext)'),
    ('023407.00', '21.02 10',
     'I6214 LX,$X1,$X1'),
    ('023407.40', '23411.71 40',
     'BZXVZ,$+2.0           bit 18 = 1 here -> 023411.40'),
    ('023410.00', '23411.70 40',
     'BZXCZ,$+1.32          -> 023411.40, same target'),
    ('023410.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023411.00', '1304.10 00',
     'B,SERS                (ext) "-UNABLE TO EX IMMED IX INSTR."'),
    ('023411.40', '24321.04 90',
     'KV,$X2,I62EXT        (ext) $X2 still holds the master copy'),
    ('023412.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023412.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-EX DESTROYED SUBJ INST."'),
    # ---- MISC -------------------------------------------------------
    ('023413.00', '23415.43 01',
     'LVI,$X1,I6215        "-MISC."; bit 18 -> 023415.40'),
    ('023413.40', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext)'),
    ('023414.00', '24331.04 10',
     'LX,$X2,I62EXM        (ext) the subject is itself "Z,$X1", p.109'),
    ('023414.40', '24321.05 10',
     'SX,$X2,I62EXT        (ext)'),
    ('023415.00', '24321.12 00',
     'EX,I62EXT            (ext)'),
    ('023415.40', '21.02 10',
     'I6215 LX,$X1,$X1'),
    ('023416.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023416.40', '1304.31 40',
     'BZXVZ,SERS            (ext) "-UNABLE TO EX MISC INSTR."; polarity'),
    ('023417.00', '24321.04 90',
     'KV,$X2,I62EXT        (ext)'),
    ('023417.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023420.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-EX DESTROYED SUBJ INSTR."  (INSTR.)'),
    # ---- FLT PT, PDF p.91 -------------------------------------------
    ('023420.40', '23424.03 01',
     'LVI,$X1,I6216        "-FLT PT" (no period); bit 18 -> 023424.00'),
    ('023421.00', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext)'),
    ('023421.40', '24330.04 10',
     'LX,$X2,I62EXF        (ext) "L%U@,I00O", p.109'),
    ('023422.00', '24321.05 10',
     'SX,$X2,I62EXT        (ext)'),
    ('023422.40', '11.22 00',
     'Z,$R                  $R FIRST in this class -- see the docstring'),
    ('023423.00', '10.22 00',
     'Z,$L'),
    ('023423.40', '24321.12 00',
     'EX,I62EXT            (ext)'),
    ('023424.00', '10.00 80 000000.20 50',
     'I6216 L(BU),$L       FULL WORD: read $L back, 64 bits BU'),
    ('023425.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023425.40', '1304.34 C2',
     'BRZ,SERS              (ext) "-UNABLE TO EX FP INST."'),
    ('023426.00', '24321.04 90',
     'KV,$X2,I62EXT        (ext)'),
    ('023426.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023427.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-EX DESTROYED SUBJ INST."'),
    # ---- FULL WD VFL ------------------------------------------------
    ('023427.40', '23433.03 01',
     'LVI,$X1,I6217        "-FULL WD."; bit 18 -> 023433.00'),
    ('023430.00', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext)'),
    ('023430.40', '24327.04 10',
     'LX,$X2,I62EXV        (ext) "L%BU@,I00O", p.109'),
    ('023431.00', '24321.05 10',
     'SX,$X2,I62EXT        (ext)'),
    ('023431.40', '10.22 00',
     'Z,$L                  $L FIRST here -- the inverse of FLT PT'),
    ('023432.00', '11.22 00',
     'Z,$R'),
    ('023432.40', '24321.12 00',
     'EX,I62EXT            (ext)'),
    ('023433.00', '11.00 80 000000.20 50',
     'I6217 L(BU),$R       FULL WORD: read $R back, 64 bits BU'),
    ('023434.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023434.40', '1304.34 C2',
     'BRZ,SERS              (ext) "-UNABLE TO EX FULL WD VFL INST."'),
    ('023435.00', '24321.04 90',
     'KV,$X2,I62EXT        (ext)'),
    ('023435.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023436.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-EX DESTROYS SUBJ INST."  (DESTROYS)'),
    # ---- exit and continuity ----------------------------------------
    ('023436.40', '23437.50 00',
     'B,$+1.0               self-relative: +1 word -> 023437.40'),
    ('023437.00', '23373.44 00',
     'BD,I6212             the loop back; bit 18 -> 023373.40'),
    ('023437.40', '1311.40 80',
     'SIC,SEN0+.32          (ext) SEN0 + 32 bits -> 001311.40'),
    ('023440.00', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP" (no period; p.110 has one)'),
    ('023440.40', '23441.04 00',
     'BD,$+.32              self-relative: +32 bits -> 023441.00'),
    ('023441.00', '24171.32 10',
     'LX,$X13,IC262         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('023441.40', '24523.32 B0',
     'V+,$X13,BIT1          (ext)'),
    ('023442.00', '24171.33 10',
     'SX,$X13,IC262         (ext)'),
]

# Only the labels DEFINED inside the transcribed range belong here; a
# SYN'd external would be checking this file against itself.  Of these
# six, five are evidence -- see the docstring on I6212.
SYMBOLS = {'I6212': '023373.40', 'I6213': '023377.40',
           'I6214': '023407.00', 'I6215': '023415.40',
           'I6216': '023424.00', 'I6217': '023433.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 1B '))
