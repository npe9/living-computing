#!/usr/bin/env python3
"""verify_ax5b_162_test3a_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), TEST 3A (../decks/ax5b_162_test3a.strap) against
the listing's printed machine code, PDF pp.107-108, octal
024136.00-024151.00.  23 half-words, entry label I62100.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

WHAT TEST 3A CHECKS.  Reference Manual printed p.50 (PDF p.53):
"Pseudo-instruction counters may occupy any of the index registers as
well as main core storage locations but cannot occupy locations
addressed between 0 and 15."  The test builds a legal pseudo-IC, copies
it into WORD 9 -- $R, the right half of the accumulator -- and issues
"EXIC,$R".  Its three error messages are the contract:

  (a) "-NO INTERRUPT WHEN PSEDUO IC / -OF EXIC LESS THAN 15."
      at 024145.40-024146.00, reached by FALLING THROUGH the EXIC, so
      the error is that no interruption happened.  "PSEDUO" is the
      listing's own typo; p.108 spells it "PSEUDO" twice.
  (b) "-AD NOT SET WHEN PSEUDO IC / -OF EXIC LESS THAN 15."
      at 024147.00-024147.40, reached from I62103 when "BADZ,$+1.32"
      finds AD off.
  (c) "-INSTRUCT NOT NOPED WHEN PSEUDO / -IC OF EXIC LESS THAN 15."
      at 024150.40-024151.00.  "Z,$X1" zeroes index register 1 first
      and the subject at I62EXI is "LVI,$X1,%8@777777.40" (024332.00,
      PDF p.110), so a nonzero index value means the subject ran.

THE MANUAL AND THE DECK DISAGREE AT THE BOUNDARY and this test does not
settle it: "between 0 and 15" against three messages saying "LESS THAN
15".  The pseudo-IC here is word 9, illegal under either reading.

ONE ROW IS NOT EXPLAINED BY THESE PAGES.  024144.40 holds
"%8@DD%BU,32,8@,3740 -ILLEGAL OP.", the same 00000003740 word 1260's
I60K7 prints at 023050.00 under "-ILLEGAL OP, NO. 31."  It stands in
the straight-line path one half-word before the EXIC, and nothing here
says why.  It is systematic, not a slip: TEST 3B repeats the identical
"Z,$X1 / DD / EXIC" triple at 024155.00/.40/024156.00.  Recorded the
way ax5b_16082_op_ad.strap records what it could not trace; the row's
ENCODING is settled regardless, and that is what is checked below.

NOTHING HERE IS A FIRST for this assembler.  EXIC came in with TEST 2B
(verify_ax5b_162_exic_listing.py), BADZ's trailing-Z clear bit with
I6086B and SIP17, BZXVZ with 2B, "$+1.32" with ibox3_sva_full's BXE
rows, $IA with I6086.  What TEST 3A adds is a SECOND, independent
listing witness for EXIC -- and the first with a SYSTEM SYMBOL operand,
"EXIC,$R" at 024145.00, where 2B only ever wrote "EXIC,I62PSI".

AND IT UPGRADES TEST 2B'S WEAKEST CLAIM.  That file's header says of
I62ITE/I62PSI/I62SUB: "No label row defining any 162* symbol appears on
PDF p.101; each address comes from an OPERAND field."  PDF p.109
defines them in its own LABEL column, read at 600 dpi: I62INT
"DR%BU,64,8@,64  -INTRPT TABLE." at 024220.00, I62ITE "BD,$  -ALL
INTERRUPTS ENTER HERE." at 024320.00, I62PSI "LX,$X0,0  -PSEUDO IC." at
024323.00, I62SUB "XW,0,0,0  -SUBJ INST." at 024324.00; PDF p.110
defines I62EXI at 024332.00.  All five agree with the operand fields
transcribed here.

BUT THE SYN'd ROWS ARE STILL NOT THE WITNESS -- the caveat
verify_ax5b_16082_16083_listing.py makes about I6088.  Every SYN in
the program file is an INPUT to this check: it makes the address field
come out right by construction, so those rows prove only that this
assembler places every OTHER field where the listing places it.  Two
tiers of corroboration exist and neither converts an input into a
witness: I62INT/I62ITE/I62PSI/I62SUB/I62EXI are confirmed by a
separately read page's own label column (pp.109-110, above), while
SEN/SERS/I60SX1/I60S1 rest on other verify files in this repo
(verify_ax5b_16087_listing.py gives I60SX1 = 023041.00 and I60S1 =
022741.00), not on an independent page read for this block.

THE BLOCK'S GENUINE ADDRESS WITNESSES are TWO, not three, and both
were self-checked by decoding BIT 18 out of the printed octal pair and
matching the page's own label column.  I62100 is deliberately NOT
counted: the program's SLC sets the counter to 024136.0 and I62100 is
the first label after it, so that check tests the SLC against the
number this transcription handed the SLC.  It is asserted below as the
block's anchor; it is not evidence.

  024142.00  "LVI,$X1,I62103" -> 24146.43 01.  Octal pair 43 = 100011,
             bit 18 = 1, so the half-word is .40: 024146.40 -- which is
             exactly where p.108 prints the label I62103.
  024146.40  "BADZ,$+1.32"    -> 24150.10 46.  Pair 10 = 001000, bit 18
             = 0, so .00: 024150.00.  And 024146.40 + 1 word + 32 bits
             = 024146.40 + 96 bits = 024150.00, the "LX,$X1,$X1" row.
             This is the one row in the block whose address comes from
             neither a SYN nor a label, so it is the location counter's
             own witness.

Two more bit-18 decodes, for rows whose target is external, to show the
half-word select is being placed and not assumed:

  024137.00  "LVI,$X1,I62SUB" -> 24324.03 01: pair 03 = 000011, bit 18
             = 0 -> 024324.00, and p.109's label column puts I62SUB at
             024324.00.
  024146.00  "BD,SERS"        -> 1304.04 00: pair 04 = 000100, bit 18
             = 0 -> 001304.00 = SERS.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted -- each
injection was made with __pycache__ cleared on BOTH sides of the run:

  MISC_CODES["EXIC"] 0b011 -> 0b111
      024145.00                                             (1 row)
  INDICATOR_BITS["AD"] 16 -> 17
      024146.40  BADZ -> "24150.10 C6"                      (1 row)
      Note WHERE it shows: the octal pair is UNCHANGED and only the
      hex byte moves, because 16 and 17 differ solely in the bit that
      lands at 24.  A check reading only the octal field would miss it.
  enc_branch_ind drops the `clear` bit (clear -> 0)
      024146.40  BADZ -> "24150.10 42"                      (1 row)
      The one field nothing else in this block exercises: BADZ is the
      block's only branch-on-indicator with the trailing Z.
  UNCOND_BRANCH_CODES["BD"] 0b001 -> 0b010
      024146.00, 024147.40                                  (2 rows)
  IMM_INDEX_CODES["LVI"] 0b0001 -> 0b1001
      024137.00, 024142.00, 024143.00                       (3 rows)
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_162_test3a.strap").read())

ROWS = [
    ('024136.00', '23041.00 80',
     'I62100 SIC,I60SX1   (ext) "-TEST 3A, PSEUDO IC LESS THAN 15."'),
    ('024136.40', '22741.10 00',
     'B,I60S1              (ext) clear indicators 0-19'),
    ('024137.00', '24324.03 01',
     'LVI,$X1,I62SUB       (ext) p.109 label column: 024324.00'),
    ('024137.40', '24323.03 D0',
     'SVA,$X1,I62PSI       (ext) aim the pseudo-IC at the subject'),
    ('024140.00', '24332.02 10',
     'LX,$X1,I62EXI        (ext) the IMMED IX subject, p.110'),
    ('024140.40', '24324.03 10',
     'SX,$X1,I62SUB        (ext)'),
    ('024141.00', '24323.02 10',
     'LX,$X1,I62PSI        (ext)'),
    ('024141.40', '11.03 10',
     'SX,$X1,$R             THE TEST: pseudo-IC into word 9'),
    ('024142.00', '24146.43 01',
     'LVI,$X1,I62103       in-range label; bit 18 -> 024146.40'),
    ('024142.40', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext) plant the handler'),
    ('024143.00', '24220.03 01',
     'LVI,$X1,I62INT       (ext) the 64-word table'),
    ('024143.40', '2.03 30',
     'SV,$X1,$IA            the Interruption Address register'),
    ('024144.00', '21.22 00',
     'Z,$X1                 so a subject that ran shows up'),
    ('024144.40', '00000003740',
     'DD(BU,32,8),(8)3740   "-ILLEGAL OP."  -- see the header'),
    ('024145.00', '11.16 00',
     'EXIC,$R               EXIC with a SYSTEM SYMBOL operand'),
    ('024145.40', '1310.00 80',
     'SIC,SEN               (ext) "-NO INTERRUPT WHEN PSEDUO IC"'),
    ('024146.00', '1304.04 00',
     'BD,SERS               (ext) "-OF EXIC LESS THAN 15."'),
    ('024146.40', '24150.10 46',
     'I62103 BADZ,$+1.32   self-relative: +96 bits -> 024150.00'),
    ('024147.00', '1310.00 80',
     'SIC,SEN               (ext) "-AD NOT SET WHEN PSEUDO IC"'),
    ('024147.40', '1304.04 00',
     'BD,SERS               (ext) "-OF EXIC LESS THAN 15."'),
    ('024150.00', '21.02 10',
     'LX,$X1,$X1            the BADZ target'),
    ('024150.40', '1310.00 80',
     'SIC,SEN               (ext) "-INSTRUCT NOT NOPED WHEN PSEUDO"'),
    ('024151.00', '1304.31 40',
     'BZXVZ,SERS            (ext) "-IC OF EXIC LESS THAN 15."'),
]

# Only the two labels DEFINED inside the transcribed range belong here;
# a SYN'd external would be checking this file against itself.  Of
# these two only I62103 is evidence -- see the docstring on I62100.
SYMBOLS = {'I62100': '024136.00', 'I62103': '024146.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 3A '))
