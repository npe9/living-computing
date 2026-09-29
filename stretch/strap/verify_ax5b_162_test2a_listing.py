#!/usr/bin/env python3
"""verify_ax5b_162_test2a_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), TEST 2A (programs/ax5b_162_test2a.strap) against
the listing's printed machine code.  THE WHOLE SUB-TEST, END TO END:
entry I6247 at 023576.40 through 023704.40, PDF pp.96, 97 and 98.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

EXTENT AND PAGE SPAN, ESTABLISHED FIRST-HAND AT 500 dpi.  PDF p.95's
last three printed rows are TEST 1D's continuity bridge -- 023575.00
"LX,$X13,IC262" / 023575.40 "V+,$X13,BIT3" / 023576.00 "SX,$X13,IC262"
-- and the first row on PDF p.96 is 023576.40 with I6247 in the name
field.  PDF p.98's last printed row is 023704.40 "SX,$X13,IC262"; below
it the page is blank fanfold rule.  Three pages, no more and no less.

CLOSURE ARITHMETIC, the way the sibling states 76 + 43 = 119.
023576.40 through 023704.40 inclusive is (0o23704 - 0o23576) * 2 + 1 =
70 * 2 + 1 = 141 half-words.  FOUR printed rows are full-word VFL loads
(023630.00, 023641.40, 023663.40, 023675.00), each occupying two
half-words, so the pages print 141 - 4 = 137 rows.  ROWS below has 137
entries, there is one SLC and it is the first statement, and no row is
listed twice.

THE UNCOVERED-RANGE PREMISE WAS RE-CHECKED HERE, not taken on trust.
A sweep parsing every ROWS tuple in every verify_*.py in this directory
finds exactly TWO files with any octal location inside
023576.40-023704.40, and NEITHER is this deck:
    verify_pau_chkssr2_listing.py  32 rows, e.g. 023636.40
        "24205.10 80 004070.20 50   CHKSS2 L(BU,4), SMANR4+.8, 112"
    verify_pau_srte30_listing.py    7 rows, e.g. 023666.40
        "24122.00 80 001042.20 50   SR30 L(BU,1), WRDB, 68"
CONFIRMED BY OPENING THEM, not assumed from the filename: both headers
say they are checked against **jb_af1c** pp.195/199-200, the PAU GATES
ROUTINE's square-root sequence -- a DIFFERENT DECK that happens to load
at the same octal addresses.  No routine-1262 file touches this range.


WHAT "MUST NOT RELINQUISH CONTROL" ACTUALLY MEANS IN THESE ROWS
---------------------------------------------------------------
docs/NEXT.md's block map calls TEST 2A "EXIC must not relinquish
control".  That phrase is second-hand and it undercounts.  Read off
these three pages, the claim is: AFTER AN "EXIC" THE INSTRUCTION
COUNTER MUST GO ON IN THE MAIN PROGRAM AT THE HALF-WORD FOLLOWING THE
"EXIC" ITSELF, and the deck tests THREE distinct ways that can fail,
plus the interruption case, by PLANTING A TRAP AT EACH PLACE control
could wrongly land and checking that none fired.

  (0) NOT to the interruption address.  "SVA,$X1,I62ITE" writes the
      pass's own error label into the interrupt-table entry; $IND and
      $MASK are zeroed.  Error text at 023606.40/023624.00/023657.40.

  (1) NOT to the half-word AFTER THE PSEUDO-IC.  "SVA,$X1,I62BR1"
      writes the error label into the "$BD,0" that PDF p.109 prints at
      024323.40 -- the RIGHT half of the same word 024323.00 that holds
      the pseudo-IC.  Error: "-EXIC RELINQUISHES CONTROL TO INSTRUCT /
      -FOLLOWING PSEUDO IC."

  (2) NOT to the half-word AFTER THE SUBJECT.  "SVA,$X1,I62BR2" writes
      it into the "$BD,0" at 024325.00.  THE ARITHMETIC, SHOWN RATHER
      THAN ASSERTED, because it is what makes trap 2 readable: the
      subject slot I62SUB is 024324.00; the subject planted in it is
      I62EXV, which PDF p.109 prints as "L(BU),I00O" with the two-word
      machine code "24503.00 80 000000.20 50", i.e. FULL LENGTH; a
      full-length instruction at 024324.00 occupies 024324.00 AND
      024324.40, two half-words; so the next instruction location is
      024324.40 + 32 bits = 024325.00, which is exactly where p.109
      prints I62BR2.  Had the subject been half-length the trap would
      have had to sit at 024324.40 instead.  Error:
      "-EXIC RELINQUISHES CONTROL TO INSTRUCT / -FOLLOWING INSTRUCT
      ADDRESSED BY PSIC."

  (3) NOT INTO THE PSEUDO-IC WORD ITSELF, and this one is not in the
      block map at all.  PDF p.109
      (verify_ax5b_162_int_entry_listing.py) prints I62PSI at 024323.00
      as "LX,$X0,0" -- A REAL INSTRUCTION whose address field the SVA
      fills in.  Read as data it is a pseudo-instruction counter;
      EXECUTED it would load word I62SUB into $X0.  So the deck zeroes
      $X0 before the EXIC and reads it back after:
        023614.40  Z,$X0
        023641.40  L(BU),$X0
        023643.00  BZRZ,SERS   "-INST AT PSIC WAS EXECUTED."
      THREE control-flow violations, not two.

The two "$BD,0" trap words are the mechanism, and they are not inferred
here: verify_ax5b_162_int_entry_listing.py already transcribes
024323.40 "I62BR1 BD,0" -> "0.04 00" and 024325.00 "I62BR2 BD,0" ->
"0.04 00" off PDF p.109, and this block's SVA rows print 24323.43 D0
and 24325.03 D0, which are those two addresses.


THE PRIMARY SOURCE, READ FIRST-HAND FOR THIS FILE AT 400 dpi
------------------------------------------------------------
Reference Manual 22-6530-2, PRINTED p.49 (PDF p.52; PDF page = printed
page + 3, verified by the "Instruction Sequencing   49" folio at the
foot of PDF p.52):

    "In either of the execution instructions, the subject instruction
    may be of any type and is performed according to the normal rules
    for an operation of its type.  HOWEVER, IN ORDER THAT THE MAIN
    PROGRAM MAY HAVE FULL CONTROL AT ALL TIMES, THE SUBJECT
    INSTRUCTION IS NOT ALLOWED TO CHANGE THE STATE OF THE INTERRUPTION
    SYSTEM OR REPLACE THE CONTENTS OF THE INSTRUCTION COUNTER."

That is the sentence the block map compresses to six words, and it
pairs one-to-one with the deck's traps.  Same printed page:

    "...EXECUTE INDIRECT AND COUNT, specifies a location which imitates
    the instruction counter, a pseudo-instruction counter.  The
    pseudo-instruction counter addresses the location of a single
    subject instruction, which is fetched and executed.  After the
    subject instruction has been fetched, but prior to its execution,
    the pseudo-instruction counter is stepped."

    "When an execution operation is initiated in the main program, the
    instruction counter is stepped in normal fashion as in all
    operations of the main program.  However, it is never stepped
    during the execution of any subject instruction even if the subject
    instruction is again one of the execution instructions."

PRINTED p.50 (PDF p.53), read first-hand at 400 dpi:

    "Execute Indirect and Count (EXIC).  Bits 0-18 of the full-word
    addressed by BITS 0-17 of the effective address are used as a
    pseudo-instruction counter."

    "Any actuated indicator whose mask bit is on may cause interruption
    at the completion, termination, or suppression of an execution
    operation."

PRINTED p.23 (PDF p.26), read first-hand at 400 dpi, for the index-word
field layout the deck's checks 2-4 walk and for the 18-bit exception:

    "The direct index arithmetic operations make use of the format
    shown below.  The format includes two index fields.  The rightmost
    field, marked I, is used in standard fashion to produce an
    effective operand address.  IN THE MAJORITY OF THESE OPERATIONS,
    19 BITS OF THE EFFECTIVE ADDRESS ARE USED IN ORDER TO PERMIT
    ADDRESSING OF HALF-WORDS.  THE TWO EXCEPTIONS USE ONLY 18 BITS OF
    THE EFFECTIVE ADDRESS BECAUSE THEY REQUIRE FULL-WORD OPERANDS."

    "Index Equal (XE).  This indicator is set to one when the field in
    the index specified by J is equal to the comparand.  It is set to
    zero when the index field is lower or higher than the comparand."

C22-6531 "STRAP-1", APPENDIX A "STRAP-1 MNEMONICS", PRINTED p.56 (PDF
p.57; the folio "56" is printed at the foot of that page), read
first-hand at 400 dpi.  EVERY system symbol this block names is in its
"Word No. / Bit Address" columns, so none of the register addresses
below is taken from the assembler's table on trust:

    $   IA    1   Interruption Address          2    0-17
    $   IND   1   Indicators                   11    0-63
    $   MASK  1   Mask                         12   21-49
    $   L     1   Left Half of Accumulator      8    0-63
    $   R     1   Right Half of Accumulator     9    0-63
    $   X0    1   Index Zero                   16    0-63
    $   X2    1   Index Two                    18    0-63
    $   X13   1   Index Thirteen               29    0-63
    $   X14   1   Index Fourteen               30    0-63
    $   X15   1   Index Fifteen                31    0-63
    $   RZ    2   Result Zero                  11      57
    $   XE    2   Index Equal                  11      53

Decimal 2, 11, 12, 8, 9, 16, 18, 29, 30, 31 are octal 2, 13, 14, 10,
11, 20, 22, 35, 36, 37 -- and those are exactly the address fields this
block prints for "SVA,$X1,$IA" (2.03 D0), "Z,$IND" (13.22 00),
"Z,$MASK" (14.22 00), "Z,$L" (10.22 00), "Z,$R" (11.22 00), "Z,$X0"
(20.22 00), "EXIC,$X2" (22.16 00), "SC,$X14,$X14" (36.35 50) and
"SC,$X15,$X15" (37.37 50).  AND THE SAME PAGE IS THE PRIMARY SOURCE
FOR RZ = 57 AND XE = 53, which this file's branch-polarity arithmetic
rests on; they no longer come to this project only through the
X22-6533 Reference Card by way of bsv/StretchTypes.bsv.


THE BLOCK'S STRUCTURE, AND WHETHER "SEVEN MEMORY COMBINATIONS" HAS AN
ANALOGUE HERE -- IT DOES, AND IT IS TWO
---------------------------------------------------------------------
TEST 1A is described in the block map as "EX must not relinquish
control; seven memory combinations".  TEST 2A says its own number out
loud, in its header comment:

    023576.40  I6247  LVI,$X1,I62INT  "-TEST 2A, CHECK THAT EXIC WILL NOT"
    023577.00         SVA,$X1,$IA     "-RELINQUISH CONTROL,AND THE TWO"
    023577.40         LVI,$X1,I6248   "-POSSIBLE MEMORY COMBINATIONS."

TWO, and the deck names them:

    023612.40  "-TEST MEMORY COMBOS."  "-EXIC IN MAIN."
    023613.40                          "-PSIC IN MAIN."  "-SUBJ IN MAIN."
    023645.40                          "-EXIC IN MAIN."
    023646.00                          "-PSIC IN IX STG." "-SUBJ IN MAIN."

ONLY THE PSEUDO-IC MOVES.  The EXIC is in the main program both times
(it is the instruction under test) and the subject is in main storage
both times -- p.50 says subject instructions of EXIC "may occupy any
available locations with addresses 32.00 and greater", which rules
index storage out.  The pseudo-IC is the one participant free to sit in
either, so TWO is the whole count.  The second combination is made by
one extra row and one changed operand:
    023654.00  LX,$X2,I62PSI   24323.04 10   copy the PSIC into index 2
    023656.40  EXIC,$X2        22.16 00      ...and point the EXIC there
against pass 1's
    023623.00  EXIC,I62PSI     24323.16 00

SO THE BLOCK IS THREE PASSES, NOT THREE TESTS:

  PASS 0   023576.40-023612.00   THE BARE RELINQUISH TEST.  PSIC in
           main.  Plants the interrupt entry and both traps, runs one
           EXIC, and checks NOTHING ELSE -- it never zeroes $X0, $R,
           $L, $IND or $MASK, so it CANNOT check execution or stepping.
           Three error entries (I6248/I6249/I6250), no body.
  PASS 1   023612.40-023645.00   "-TEST MEMORY COMBOS."  THE SAME
           memory configuration as pass 0, re-run with the full
           six-check verification body.  I6252/I6253/I6254, body I6255.
  PASS 2   023645.40-023704.40   PSIC IN INDEX STORAGE.
           I6256/I6257/I6258, body I6259, then the exit and continuity.

PASSES 1 AND 2 ARE THE SAME SHAPE, ROW FOR ROW.  SAYING SO IS PART OF
THE ANSWER: after the first two passes this block introduces no new
idea, it re-runs one with the pseudo-IC moved.  The differences are
seven, all small, all transcribed rather than normalised:
  a. "EXIC,I62PSI" vs "EXIC,$X2";
  b. pass 2 carries the extra "LX,$X2,I62PSI" at 023654.00;
  c. the stepping check reads "LX,$X1,I62PSI" (023643.40, 24323.02 10)
     in pass 1 and "LX,$X1,$X2" (023677.00, 22.02 10) in pass 2;
  d. the clear-indicators call is "BD,I60S1" (023620.40, 22741.04 00)
     in pass 1 and "B,I60S1" (023653.40, 22741.10 00) in pass 2 -- and
     pass 0's is "B,I60S1" too (023601.00).  THREE CALLS TO ONE
     SUBROUTINE, TWO DIFFERENT BRANCH OPS.  Per-check, not per-block;
     the printed op byte is 00 in all three and the codes differ in the
     octal pair, 04 against 10;
  e. the SC pair and the SR pair are in OPPOSITE ORDER (below);
  f. pass 1 has the "-TEST MEMORY COMBOS." heading line and pass 2 has
     none, so pass 2's three class comments sit one row higher;
  g. pass 1's interruption message says "ON MAIN" where every sibling
     says "IN MAIN" -- a DECK TYPO, measured below.

THE VERIFICATION BODY (I6255 at 023630.00, I6259 at 023663.40), SIX
CHECKS IN PRINTED ORDER:
  1. "L(BU),$R / SIC,SEN / BRZ,SERS"    "-EXIC SUBJ INST NOT EXECUTED."
  2. "LX,$X14,I62EXV / LX,$X15,I62SUB / KV / SIC,SEN / BZXE,SERS"
                                        "-BITS 0-24 OF SUBJ INST CHNGD."
  3. "SC / SC / KV / SIC,SEN / BZXE"    "-BITS 28-45 OF SUBJ INST CHNGD."
  4. "SR / SR / KV / SIC,SEN / BZXE"    "-BITS 46-63 OF SUBJ INST CHNGD."
  5. "L(BU),$X0 / SIC,SEN / BZRZ,SERS"  "-INST AT PSIC WAS EXECUTED."
  6. "LX,$X1,<psic> / KVI,$X1,I62SUB / SIC,SEN / BXE,SERS"
                                        "-PSEUDO IC UNCHANGED BY EXIC."

CHECKS 2-4 ARE ONE IDEA IN THREE MOVEMENTS, and the arithmetic is the
proof.  The master subject I62EXV and the working copy in I62SUB are
both loaded AS INDEX WORDS, and the three comparisons walk the three
index fields: VALUE 0-24, COUNT 28-45, REFILL 46-63 (p.23's index-word
layout; bits 25-27 are unused, which is exactly why the deck's three
messages read 0-24, 28-45 and 46-63 and name nothing in between).  "KV"
compares only the VALUE field, so "SC,$X15,$X15" -- store index 15's
COUNT into the word at location $X15, which IS index 15 -- rotates the
count field into the value field where the same KV can see it; "SR"
does the same for the refill.  THE DECK COMPARES A 64-BIT INSTRUCTION
WORD USING AN INSTRUCTION THAT ONLY COMPARES 25 BITS, THREE TIMES.

WHAT THE PARALLEL EXIC IMPLEMENTATION MOST NEEDS FROM THIS BLOCK:
  * TEST 2A CHECKS ONE THING TEST 2B DOES NOT.  Check 5, "the
    pseudo-IC word must not itself have been executed", appears nowhere
    in TEST 2B (verify_ax5b_162_test2b_head_tail_listing.py /
    verify_ax5b_162_exic_listing.py).
  * TEST 2A'S STEPPING CHECK IS STRICTLY WEAKER THAN 2B'S AND THE
    OPPOSITE POLARITY.  2B does "V+I,$X2,<step> / KV,$X2,I62PSI /
    BZXE" -- the pseudo-IC must have stepped by EXACTLY the subject's
    length.  2A does "KVI,$X1,I62SUB / BXE" -- error when the
    pseudo-IC is still EQUAL to where it started.  2A only demands that
    it CHANGED.  Do not read 2B's contract out of 2A's rows.


BRANCH POLARITY, SETTLED PER CHECK BY ARITHMETIC ON THE PRINTED HEX
-------------------------------------------------------------------
Not prose.  strap_asm's enc_branch_ind lays bits 24-31 out as the low
bit of the 6-bit indicator number (24), the identifying literal 1000
(25-28), clear (29), branchOn (30), idx (31).  FOUR SHAPES ARE PRINTED
IN THIS ONE BLOCK AND TWO OF THEM ARE THE SAME INDICATOR BOTH WAYS
ROUND, which is the point: polarity is a per-check property.

  BRZ,SERS  -> 1304.34 C2.  Pair 34 = 011100, so bit 18 = 0 and
               indicator bits 19-23 = 11100.  Hex C2 = 1 1000 0 1 0:
               indicator bit 24 = 1, giving number 111001 = 57 = RZ;
               clear = 0; BRANCHON = 1.  BRANCHES WHEN RZ IS ON.
  BZRZ,SERS -> 1304.34 C0.  Same indicator 57 = RZ; BRANCHON = 0.
               BRANCHES WHEN RZ IS OFF.
  BZXE,SERS -> 1304.32 C0.  Pair 32 = 011010, bits 19-23 = 11010; hex
               C0 gives indicator bit 24 = 1, number 110101 = 53 = XE;
               BRANCHON = 0.  BRANCHES WHEN XE IS OFF.
  BXE,SERS  -> 1304.32 C2.  Same indicator 53 = XE; BRANCHON = 1.
               BRANCHES WHEN XE IS ON.

Each pairing is right for the check it guards, and they do not agree
with each other, which is why they had to be decided one at a time:

  RZ ON is the error at 023631.40/023665.00: $R was zeroed by
    "Z,$R" and the subject "L(BU),I00O" is supposed to have made it
    nonzero, so Result Zero still on means "-EXIC SUBJ INST NOT
    EXECUTED."
  RZ OFF is the error at 023643.00/023676.40: $X0 was zeroed by
    "Z,$X0" and nothing legitimate writes it, so Result Zero off means
    the pseudo-IC word "LX,$X0,0" ran -- "-INST AT PSIC WAS EXECUTED."
  XE OFF is the error at the three "CHNGD." rows: the KV compared the
    master subject against the working copy and they came out UNEQUAL.
  XE ON is the error at 023645.00/023700.40: the KVI compared the
    pseudo-IC against where it started and they came out EQUAL, i.e.
    "-PSEUDO IC UNCHANGED BY EXIC."

NOTHING IN THIS BLOCK CLEARS.  Bit 29 is 0 in every one of the twelve
branch-on-indicator rows (C2 and C0 both have bit 29 = 0).  The Z in
"BZRZ" and "BZXE" is the BZ prefix, and the Z in "RZ" is part of the
indicator name; strap_asm.classify_branch_indicator tries "BZ" first,
so "BZRZ" parses as BZ + RZ and "BRZ" as B + RZ.

RZ = 57 is the one indicator number here whose NARRATIVE definition
this file did not find in the Reference Manual.  It reached this
project from the X22-6533 Reference Card's "INDICATOR LIST" by way of
bsv/StretchTypes.bsv, and verify_ax5b_160_test8b_listing.py is the deck
witness for it ("BRZ" printing "22532.34 C2", bits 19-24 = 111001).
This block reproduces that number in twelve more printed rows and adds
the first BZRZ/BRZ pair in routine 1262.  Listed under WHAT I AM NOT
SURE OF at the foot of this file.


BIT-18 SELF-CHECKS
------------------
Print format (listing_oracle.fmt_half): bits 0-17 as 6 octal digits,
".", bits 18-23 as 2 octal digits, bits 24-31 as 2 hex digits.  BIT 18
IS THE TOP BIT OF THE OCTAL PAIR.

THE EXCLUSION HAS FOUR CLASSES WITH THREE REASONS, and this block adds
a FIFTH class with a reason of its own.  Rows here fall into all five.

  1. HALF-WORD SELECT -- decoded below.  Branch targets (B, BD) and the
     19-bit value-field ops (LVI, SVA, KVI, V+).
  2. LX / SX -- EXCLUDED, 18 bits, p.23 quoted above.  The two
     exceptions require full-word operands, so their bit 18 is not a
     half-word select.  Rows here: 24327.02/.34, 24324.03/.36,
     24323.02/.04, 24171.32/.33, 37.37, 36.35, 22.02 -- every one with
     a top pair bit of 0.  The MEASURED NULL below tests this
     empirically instead of asserting it.
  3. SIC -- EXCLUDED, its operand is a 24-bit BIT address and the pair
     is a BIT OFFSET within the word.  Rows: the twenty-four
     "SIC,SEN" -> 1310.00 80, the three "SIC,I60SX1" -> 23041.00 80,
     and 023702.00 "SIC,SEN0+.32" -> 1311.40 80.
     AND THE TRAP IS LIVE IN THIS BLOCK TOO: 40 octal = 32 decimal, and
     32 bits is ALSO exactly one half-word, so "1311.40" reads
     identically under the wrong interpretation.  Arithmetic settles it
     and the digits do not.  THIS BLOCK CONTAINS NO SIC WHOSE OFFSET IS
     NOT A MULTIPLE OF 32, so its rows cannot separate the two
     readings; the bit-offset reading comes from the encoder and the
     pocket card, not from here.  What WOULD separate them is an offset
     such as "+.8", which prints .10 as a bit offset and is
     unrepresentable as a half-word address.
  4. TRANSMIT's A1 -- the fourth excluded class, a 24-bit BIT address
     in a full-word instruction.  NO TRANSMIT APPEARS IN THIS BLOCK, so
     the class is named for completeness and exercises nothing here.
  5. EXIC -- A FIFTH CLASS, NOT ONE OF THE ABOVE FOUR, with its own
     citation.  Printed p.50: the pseudo-IC is "the full-word addressed
     by BITS 0-17 of the effective address".  So for EXIC bit 18 is not
     a half-word select either, for the same substantive reason as
     LX/SX but under a different sentence on a different page.  The
     three EXIC rows (023605.40 and 023623.00 -> 24323.16 00,
     023656.40 -> 22.16 00) all print bit 18 = 0 and both targets are
     word-aligned, so THEY ARE NOT COUNTED AS BIT-18 WITNESSES HERE --
     they are a measured null, and the liveness proof below shows what
     it would take to move them.
  KVI IS *NOT* EXCLUDED.  It is not in opcodes.IMM_INDEX_COUNT_OPS, so
  its operand is a 19-bit value-field address quantity and bit 18 is
  live; both KVI rows are decoded below as class 1.

ADDRESS WITNESSES -- labels DEFINED inside the transcribed range,
printed in the listing's own name field, and reached by an operand
whose octal pair this file decodes.  TWELVE of them, and bit 18 is
exercised in BOTH STATES through BOTH the LVI and the BD path:

  023577.40  "LVI,$X1,I6248" -> 23606.43 01.  Pair 43 = 100011, BIT 18
             = 1, so .40: 023606.40 -- where p.96 prints I6248.
  023602.40  "LVI,$X1,I6249" -> 23610.03 01.  Pair 03 = 000011, bit 18
             = 0: 023610.00 -- where p.96 prints I6249.  Note the pair
             differs from the row above ONLY in bit 18.
  023603.40  "LVI,$X1,I6250" -> 23611.43 01.  BIT 18 = 1: 023611.40 --
             where p.96 prints I6250.
  023612.40  "LVI,$X1,I6252" -> 23624.03 01.  Bit 18 = 0: 023624.00.
  023615.00  "LVI,$X1,I6253" -> 23625.43 01.  BIT 18 = 1: 023625.40.
  023617.00  "LVI,$X1,I6254" -> 23627.03 01.  Bit 18 = 0: 023627.00 --
             and that is CROSS-PAGE, the first row of PDF p.97.
  023645.40  "LVI,$X1,I6256" -> 23657.43 01.  BIT 18 = 1: 023657.40.
  023650.00  "LVI,$X1,I6257" -> 23661.03 01.  Bit 18 = 0: 023661.00 --
             cross-page again, the first row of PDF p.98.
  023652.00  "LVI,$X1,I6258" -> 23662.43 01.  BIT 18 = 1: 023662.40.
  023606.00  "BD,I6251"      -> 23612.44 00.  Pair 44 = 100100, BIT 18
             = 1: 023612.40 -- where p.96 prints I6251.  Printed three
             times (023606.00, 023607.40, 023611.00), identically.
  023623.40  "BD,I6255"      -> 23630.04 00.  Pair 04 = 000100, bit 18
             = 0: 023630.00 -- where p.97 prints I6255.  Three times.
  023657.00  "BD,I6259"      -> 23663.44 00.  BIT 18 = 1: 023663.40 --
             where p.98 prints I6259.  Three times.
  SIX of the twelve sit at a .40 and six at a .00, and the SAME SOURCE
  TOKEN SHAPE ("LVI,$X1,I62xx", "BD,I62xx") produces both.  This is
  twelve real address witnesses against the sibling TEST 2B file's
  four.

SELF-RELATIVE ROWS, the location counter's own witnesses -- AND THE
CLEANEST DEMONSTRATION IN THE BLOCK THAT BIT 18 IS COMPUTED:

  023701.00  "B,$+1.0"  -> 23702.10 00.  Pair 10 = 001000, bit 18 = 0:
             023702.00.  And 023701.00 + 1 word (64 bits) = 023702.00.
  023703.00  "BD,$+.32" -> 23703.44 00.  Pair 44 = 100100, BIT 18 = 1:
             023703.40.  And 023703.00 + 32 bits = 023703.40.
  THE SIBLING PRINTS THE SAME TWO SOURCE TOKENS WITH THE OPPOSITE BITS.
  verify_ax5b_162_test2b_head_tail_listing.py has "B,$+1.0" at
  023774.40 printing 23775.50 00 (BIT 18 = 1) and "BD,$+.32" at
  023776.40 printing 23777.04 00 (bit 18 = 0).  Same two tokens, both
  bits flipped, purely because of where the row sits in the word.  A
  copied constant could not do that.

THE ROW WHERE BIT 18 IS THE WHOLE POINT.  I62PSI and I62BR1 are the two
halves of the SAME WORD, 024323, and nothing but bit 18 tells them
apart -- which is also exactly why trap 1 is where it is:

  023603.00  "SVA,$X1,I62BR1" -> 24323.43 D0.  Pair 43, BIT 18 = 1:
             024323.40.
  023602.00  "SVA,$X1,I62PSI" -> 24323.03 D0.  Pair 03, bit 18 = 0:
             024323.00.
  Same word address, same J, same op byte; one bit apart.  PDF p.109's
  label column (verify_ax5b_162_int_entry_listing.py) prints I62PSI at
  024323.00 and I62BR1 at 024323.40.  Two pages agree.

EXTERNAL-TARGET DECODES, which show the half-word select being PLACED
and not merely assumed zero:

  023576.40  "LVI,$X1,I62INT" -> 24220.03 01: bit 18 = 0 -> 024220.00.
  023577.00  "SVA,$X1,$IA"    -> 2.03 D0: bit 18 = 0 -> 000002.00, the
             interruption address register.  C22-6531 Appendix A,
             printed p.56, read first-hand: "$ IA 1 Interruption
             Address 2 0-17".  NOT Reference Manual p.23 -- that page
             carries the 18-bit rule and XE, not the symbol table.
  023600.00  "SVA,$X1,I62ITE" -> 24320.03 D0: bit 18 = 0 -> 024320.00.
  023601.00  "B,I60S1"        -> 22741.10 00: pair 10, bit 18 = 0 ->
             022741.00.  docs/listing_typography.md measured the label
             I60S1 at 022741.00 on PDF p.83 for a different purpose
             entirely; the number agrees.
  023601.40  "LVI,$X1,I62SUB" -> 24324.03 01: bit 18 = 0 -> 024324.00.
  023604.00  "SVA,$X1,I62BR2" -> 24325.03 D0: bit 18 = 0 -> 024325.00.
  023607.00  "BD,SERS"        -> 1304.04 00: bit 18 = 0 -> 001304.00.
  023620.40  "BD,I60S1"       -> 22741.04 00: bit 18 = 0 -> 022741.00.
             The same target as 023601.00's "B,I60S1", by a different
             branch op -- the two agree independently.
  023644.00  "KVI,$X1,I62SUB" -> 24324.03 04: bit 18 = 0 -> 024324.00.
             Class 1, not excluded: KVI is not an IMM_INDEX_COUNT_OP,
             so its operand is a 19-bit value-field address.
  023702.40  "B,SSW"          -> 1301.10 00: bit 18 = 0 -> 001301.00.
  023704.00  "V+,$X13,BIT4"   -> 24526.32 B0: pair 32 = 011010, bit 18
             = 0 -> 024526.00.  verify_ax5b_bit_table_listing.py puts
             BIT0 at 024522.00, so BIT4 is 024526.00.  AND THE BLOCK
             MAP IS CORROBORATED FOR FREE: PDF p.95 ends TEST 1D on
             BIT3 (24525.32 B0), p.98 ends TEST 2A on BIT4, and p.102
             ends TEST 2B on BIT5 -- three pages, three consecutive
             continuity bits, exactly NEXT.md's "1A=BIT0 ... 2D=BIT7".
  023701.40  "BD,I6247"       -> 23576.44 00: BIT 18 = 1 -> 023576.40 --
             this file's own SLC, so an ANCHOR and not evidence.


WITNESS TIERING -- NOT INFLATED
-------------------------------
EVERY "SYN" IN THE .strap IS AN INPUT, NOT A WITNESS.  SEN, SERS, SEN0,
SSW, I60S1, I60SX1, I62INT, I62ITE, I62PSI, I62BR1, I62SUB, I62BR2,
I62EXV, IC262 and BIT4 all take their value from a number this
transcription supplied, so their rows come out right by construction
and prove only that the assembler places every OTHER field where the
listing places it.

AN "SLC"-PLACED LABEL IS AN ANCHOR, NOT EVIDENCE.

  TIER 1, REAL ADDRESS WITNESSES (12): I6248, I6249, I6250, I6251,
    I6252, I6253, I6254, I6255, I6256, I6257, I6258, I6259.  Each is
    defined inside the range, printed in the listing's own name field,
    and reached by at least one operand whose octal pair is decoded
    above.  Each one's LOCATION is the cumulative sizing of every row
    before it, so the twelve together pin the whole 137-row block
    end to end -- including the four straddling/full-word rows, since
    I6259 at 023663.40 sits after two of them.
  TIER 2, NEAR-TRIVIAL: none.  Every in-range label is referenced from
    inside the range.
  TIER 3, ANCHORS (1): I6247 at 023576.40, the first label after the
    SLC.  "BD,I6247" at 023701.40 traces its target straight back to
    that SLC, so it corroborates nothing about placement -- but the
    row's OWN LOCATION, 023701.40, is evidence, because it is right
    only if all 130 rows before it were sized right.
  TIER 4, CROSS-PAGE CORROBORATION, which witnesses nothing about THESE
    rows but does remove the worry that a SYN was a number chosen to
    fit: I62PSI, I62BR1, I62SUB, I62BR2, I62ITE, I62EXV, I62INT against
    PDF p.109's label column (verify_ax5b_162_int_entry_listing.py);
    IC262 and the BIT table against PDF pp.114-115
    (verify_ax5b_bit_table_listing.py); I60S1 against
    docs/listing_typography.md's own 600 dpi measurement on PDF p.83.


DECK TYPO vs SCAN DAMAGE -- ONE TYPO, TWO NON-EVENTS, ZERO DAMAGE
------------------------------------------------------------------
1. 023624.00 "-INT ON EXIC TO PSIC ON MAIN TO" is a DECK TYPO, and the
   control is the same word on a parallel line.  023606.40 prints the
   identical message with "IN MAIN".  Measured at 500 dpi by segmenting
   glyph bounding boxes from pixel-column ink profiles:
     023606.40, the glyph before "N MAIN":  11 px bare stroke = I.
                letter O elsewhere on THAT SAME ROW ("ON EXIC", "TO",
                "TO"):  44, 44, 44 px.
     023624.00, the glyph in the SAME word position:  44 px round.
                letter O elsewhere on ITS OWN ROW:  42 ("ON EXIC"),
                45 ("TO").
   44 against 44/42/45 on its own line and against 11 on the parallel
   line.  It is a CLEAN, fully formed, correctly inked letter O standing
   where the word is "IN" -- a clean wrong letter, which is a TYPO.
   Damage would have left a RAGGED I; nothing on that row or its
   neighbours is ragged or broken.  TRANSCRIBED AS PRINTED.

2. 023577.00 "-RELINQUISH CONTROL,AND THE TWO" has NO SPACE after the
   comma.  Settled by PITCH, because a missing space and a dropped
   character look alike.  Cell pitch from the well-formed word CONTROL
   on that same row: glyph starts at x = 2605, 2654, 2704, 2755, 2807,
   2854, 2905 px -> steps 49, 50, 51, 52, 47, 51, mean 50.0 px/cell.
   A WORD GAP on the same row is 101 px (H 2504 -> C 2605), 100 px
   (D 3108 -> T 3208) and 99 px (E 3309 -> T 3408) -- two cells.  The
   comma's cell begins at 2955 (L at 2905 plus one 50 px cell) and the
   A of AND begins at 3006, which is 51 px, ONE cell.  Adjacent cells:
   nothing was dropped by the scan, the deck printed no space.  AN
   AUTHORING QUIRK, NOT A GARBLE -- said plainly rather than forced
   into the binary.

3. 023657.40 "-INT ON EXIC TO PSIC IN IX STG" ends with no period and
   its sentence's "TO" is carried onto the next line ("-TO VFL LOAD IN
   MAIN.").  Checked on the ink profile: after the G at x 3443 (w 40)
   there is NO INK AT ALL before the machine-code column at x 4202.
   Not a dropped period -- the parallel row 023606.40 likewise ends
   "IN MAIN TO" with no period, because in both cases the sentence runs
   on.  Non-event.

4. "INSTRUCT" for "instruction" (four times) and "CHNGD." for "changed"
   (six times) are the deck's own abbreviations, printed identically
   every time.  Not drops; no pitch test needed.

NOTHING IN 137 ROWS IS SCAN-DAMAGED.  Every character on pp.96-98 is a
clean, well-inked print; no letter is ragged and no stroke is broken.

THE LABEL GLYPH, RE-MEASURED ON THIS BLOCK'S OWN PAGE at 500 dpi rather
than inherited from docs/listing_typography.md.  Row 023576.40:
    name field "I6247":  I 10 | 6 39 | 2 36 | 4 42 px
    operand "LVI,$X1,I62INT", SAME ROW:
        L 37 | V 30 | I 10 | , 25 | $ 36 | X 38 | 1 31 | , 23 |
        I 11 | 6 37 | 2 34 | I 12 | N 38
Three letter-I glyphs (10, 11, 12 px) and one digit 1 (31 px) in one
printed row.  The populations do not touch.  Spellings used here are
the corrected ones: I6247, I62INT, IC262.


A FULL-WORD INSTRUCTION AT AN ODD HALF-WORD, TWICE, AND NO CNOP
---------------------------------------------------------------
023641.40 "L(BU),$X0" and 023663.40 "L(BU),$R" each START on a .40 and
STRADDLE into the next word: the listing's own next printed addresses
are 023642.40 and 023664.40, two half-words on.  The other two
full-word rows (023630.00 and 023675.00) are word-aligned.  THE LISTING
PRINTS NO CNOP ANYWHERE IN THE BLOCK, and the printed address column
proves there is no gap, so none is written.
TESTED BEFORE THE FILE WAS WRITTEN, not assumed: assembling
"SLC,(8)23641.00 / B,SERS / L(BU),$X0 / SIC,SEN / BD,SERS" puts the
VFL load's halves at 023641.40 and 023642.00 and the SIC at 023642.40,
matching the page; strap_asm does not word-align instructions.
AND IT IS NOT A REPO FIRST, which was checked rather than claimed: a
sweep of every ROWS tuple in every verify_*.py in this directory parses
656 full-word rows, of which 216 are at a .40 (ax4b_1246_memories,
ax5b_160_test6, ax5b_160s1 and others).


NO MNEMONIC HERE IS A FIRST FOR THE REPO, and that was checked by
scanning every OTHER verify_*.py in this directory for the token
followed by a comma (the listing's own operand separator), not by eye:
SIC 140, B 122, BD 79, LX 57, Z 57, SX 42, L(BU) 32, KV 26, V+ 26,
LVI 25, SVA 22, SR 20, BZXE 17, BXE 15, BRZ 11, SC 9, KVI 9, BZRZ 8,
EXIC 7.  EXIC is the scarce one and its seven are named because the
sibling's docstring says five -- two files have been added since:
verify_ax5b_1274_truncation_listing.py, verify_ax5b_160s1_tail_listing.py,
verify_ax5b_162_exic_listing.py, verify_ax5b_162_int_entry_listing.py,
verify_ax5b_162_test2b_head_tail_listing.py,
verify_ax5b_162_test3a_listing.py, verify_ax5b_162_test3b_listing.py.
This file adds three more printed EXIC rows and the eighth such file.
Three candidate firsts were chased and ALL THREE KNOCKED OUT:
  * "SC with the index as its own effective address" -- NOT new;
    verify_ax5b_1258_test1_listing.py prints "SC,$X0,$X3" and the
    ibox1 chain files print "SC,$X1,ISTOY" 20+ times.
  * "a full-word VFL instruction at an odd half-word" -- NOT new; 216
    such rows already exist (above).
  * "EXIC with a register operand" -- "EXIC,$X2" at 023656.40 is a
    shape no other file has, but the MNEMONIC is not new (five files)
    and the encoding path is the same BranchOrMisc emit.  Reported as a
    new ROW SHAPE, not as a new mnemonic.
What this block genuinely adds is not a mnemonic but a PAIR: BRZ and
BZRZ, and BXE and BZXE, in the SAME block on the SAME indicator --
twelve branch-on-indicator rows covering all four polarities of two
indicators.


PROVEN DISCRIMINATING
---------------------
Five injections, each into strap/opcodes.py, each CONFIRMED APPLIED by
printing the patched line (a sed that silently fails to match produces
"ALL TESTS PASSED", which reads exactly like a legitimate measured
null; that has happened in this project twice, once because two
encoders had textually identical A1 clauses).  "rm -rf __pycache__" on
BOTH sides of every injection.  Each injection is applied only to a
PRISTINE opcodes.py (sha256 checked equal to a saved copy before the
patch) and reverted by restoring that copy (sha256 checked equal
after).  Failure sets below are OBSERVED, copied out of the runs.

  INJECTIONS AND THEIR OBSERVED FAILING ROWS
  ------------------------------------------
  1. MISC_CODES["EXIC"]  0b011 -> 0b111
         023605.40, 023623.00, 023656.40                  (3 rows)
     All three EXIC rows and nothing else -- including "EXIC,$X2",
     whose operand is a register, so the two operand shapes are pinned
     together.  The block's reason to exist.
  2. INDICATOR_BITS["RZ"]  57 -> 14
         023631.40, 023643.00, 023665.00, 023676.40       (4 rows)
     BOTH POLARITIES: the two BRZ rows and the two BZRZ rows.  14 is
     the only number in 0-63 that INDICATOR_BITS does not hold, and
     that was verified by reading the table here, not inherited.
  3. INDICATOR_BITS["XE"]  53 -> 14
         023634.00, 023636.40, 023641.00, 023645.00,
         023667.40, 023672.00, 023674.40, 023700.40       (8 rows)
     All six BZXE rows and both BXE rows, and the RZ rows are
     untouched: the two indicator fields are independent.
  4. DIR_INDEX_CODES["SC"]  0b10101 -> 0b10100
         023634.40, 023635.00, 023670.00, 023670.40       (4 rows)
     All four SC rows, two per pass, and the SR rows do not move --
     0b10100 is free in DIR_INDEX_CODES and the two store-field codes
     are separately pinned.
  5. DIR_INDEX_CODES["SR"]  0b10111 -> 0b10110
         023637.00, 023637.40, 023672.40, 023673.00       (4 rows)
     All four SR rows; SC untouched.

  MEASURED NULL, WITH ITS ARITHMETIC AND WITH A LIVENESS PROOF, and it
  is a BLOCK-SPECIFIC one rather than a repeat of the sibling's LX/SX
  mask.  Sixth injection, into strap_asm.py's BranchOrMisc emit case
  (the "else" arm at line 1433), making the assembler ENFORCE p.50's
  "bits 0-17" for EXIC by masking bit 18 off its address:

      image.deposit_half(loc // 32, enc_branch_or_misc(addr19,
                                        MISC_CODES[op], True, idx))
   -> image.deposit_half(loc // 32, enc_branch_or_misc(addr19 &
          (0x7FFFE if op == 'EXIC' else 0x7FFFF),
                                        MISC_CODES[op], True, idx))

  CONFIRMED APPLIED by DIFFING the file on disk against a saved copy --
  the run printed the two-line unified diff above before assembling
  anything -- and reverted by restoring that copy (sha256 equal
  afterwards).
      OBSERVED: 0 of the 3 EXIC rows changed.  The script still ends
      "ALL TESTS PASSED".
  That is the CORRECT result and the reason is arithmetic, not a dead
  patch: I62PSI is 024323.00 and $X2 is 000022.00, both word-aligned,
  so the bit the patch clears is already 0 in all three rows.
  LIVENESS PROVEN SEPARATELY AND MEASURED, because "no change" is
  exactly what a patch that did not apply also produces.  A constructed
  "SLC,(8)23605.40 / EXIC,I62BR1" with I62BR1 = 024323.40 -- a genuine
  .40 target, which this block's data never contains -- assembles
      UNPATCHED  to  024323.56 00   (pair 56 = 101110, BIT 18 = 1)
      PATCHED    to  024323.16 00   (pair 16 = 001110, bit 18 = 0)
  The encoder moves by exactly bit 18 under the patch; this block's
  three EXIC rows do not see it because both their targets are
  word-aligned.  THE NULL IS THE DATA'S, NOT THE PATCH'S.


WHY EACH PASS RE-PLANTS THE SUBJECT, AND WHY THE BODY IS NOT RE-ENTRANT
----------------------------------------------------------------------
Recorded because an implementer reading checks 2-4 could otherwise
think I62SUB is being restored, and it is not.  All three passes do
"LX,$X1,I62EXV / SX,$X1,I62SUB" (023604.40/023605.00,
023616.00/023616.40, 023651.00/023651.40) -- but nothing in the body
ever damages I62SUB.  WHAT THE BODY DESTROYS IS $X14 AND $X15: the
"SC,$Xn,$Xn" and "SR,$Xn,$Xn" rows overwrite each index's own VALUE
field in place, so after check 4 neither index holds what it loaded.
The re-plant is the setup's own bookkeeping, not a repair.
AND THE ACCUMULATOR IS LEFT DIRTY BY THE PREVIOUS PASS.  Pass 0 runs
an EXIC whose subject is a VFL load into the accumulator and never
zeroes $R or $L beforehand -- which is precisely why pass 0 cannot ask
"did the subject execute?" -- so when pass 1 reaches its "Z,$R / Z,$L"
at 023622.00/023622.40 those registers hold whatever pass 0's subject
left in them.  The zeroing is a PRECONDITION of check 1, not
decoration; the five "Z," rows in each setup are not boilerplate.


THE EXIT IS NOT THE SAME EXIT ITS TWO SIBLINGS HAVE
---------------------------------------------------
023701.00-023704.40 is the same five-row exit plus continuity bridge
that TEST 2B ends with at 023774.40 and TEST 3B at 024162.40, but FIVE
fields differ and two of those are bit 18:

  here 023701.00  B,$+1.0   23702.10 00   bit 18 = 0 (row word-aligned)
  2B   023774.40  B,$+1.0   23775.50 00   BIT 18 = 1 (row at a .40)
  here 023703.00  BD,$+.32  23703.44 00   BIT 18 = 1
  2B   023776.40  BD,$+.32  23777.04 00   bit 18 = 0
  here 023701.40  BD,I6247      2B 023775.00  BD,I6260
  here 023704.00  V+,$X13,BIT4  2B 023777.40  V+,$X13,BIT5
  here 023703.40  "-UPDATE CONTINUITY CHECK."   3B 024165.00
                                "-UPDATE CONTINUITY."
Do not merge the three.


WHAT I AM NOT SURE OF is listed at the foot of this file.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_test2a.strap").read())

ROWS = [
    # ================================================================
    # PASS 0 -- PDF p.96.  The bare relinquish test, no body.
    # ================================================================
    ('023576.40', '24220.03 01',
     'I6247 LVI,$X1,I62INT (ext) "-TEST 2A, CHECK THAT EXIC WILL NOT"'),
    ('023577.00', '2.03 D0',
     'SVA,$X1,$IA           "-RELINQUISH CONTROL,AND THE TWO"'),
    ('023577.40', '23606.43 01',
     'LVI,$X1,I6248         in-range label: BIT 18 SET -> 023606.40'),
    ('023600.00', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) plant the no-interrupt error entry'),
    ('023600.40', '23041.00 80',
     'SIC,I60SX1          (ext) 24-bit BIT address, offset 00'),
    ('023601.00', '22741.10 00',
     'B,I60S1             (ext) 1260 clear-indicators; cf 023620.40 BD'),
    ('023601.40', '24324.03 01',
     'LVI,$X1,I62SUB      (ext) bit 18 = 0 -> 024324.00'),
    ('023602.00', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext) bit 18 = 0 -> 024323.00'),
    ('023602.40', '23610.03 01',
     'LVI,$X1,I6249         in-range label: bit 18 = 0 -> 023610.00'),
    ('023603.00', '24323.43 D0',
     'SVA,$X1,I62BR1      (ext) BIT 18 SET -> 024323.40, TRAP 1'),
    ('023603.40', '23611.43 01',
     'LVI,$X1,I6250         in-range label: BIT 18 SET -> 023611.40'),
    ('023604.00', '24325.03 D0',
     'SVA,$X1,I62BR2      (ext) bit 18 = 0 -> 024325.00, TRAP 2'),
    ('023604.40', '24327.02 10',
     'LX,$X1,I62EXV       (ext) the full-word subject; 18-bit, see hdr'),
    ('023605.00', '24324.03 10',
     'SX,$X1,I62SUB       (ext) 18-bit'),
    ('023605.40', '24323.16 00',
     'EXIC,I62PSI         (ext) the instruction this block exists for'),
    ('023606.00', '23612.44 00',
     'BD,I6251              BIT 18 SET -> 023612.40; "-PSIC IS PSEUDO IC."'),
    # ---- pass 0, the interruption trap -----------------------------
    ('023606.40', '1310.00 80',
     'I6248 SIC,SEN        (ext) "-INT ON EXIC TO PSIC IN MAIN TO"'),
    ('023607.00', '1304.04 00',
     'BD,SERS               (ext) "-VFL LOAD IN MAIN."  BD, not B'),
    ('023607.40', '23612.44 00',
     'BD,I6251'),
    # ---- pass 0, TRAP 1: control after the pseudo-IC ---------------
    ('023610.00', '1310.00 80',
     'I6249 SIC,SEN        (ext) "-EXIC RELINQUISHES CONTROL TO INSTRUCT"'),
    ('023610.40', '1304.04 00',
     'BD,SERS               (ext) "-FOLLOWING PSEUDO IC."'),
    ('023611.00', '23612.44 00',
     'BD,I6251'),
    # ---- pass 0, TRAP 2: control after the subject -----------------
    ('023611.40', '1310.00 80',
     'I6250 SIC,SEN        (ext) "-EXIC RELINQUISHES CONTROL TO INSTRUCT"'),
    ('023612.00', '1304.04 00',
     'BD,SERS               (ext) "-FOLLOWING INSTRUCT ADDRESSED BY PSIC."'
     '  no BD,I6251: falls through'),

    # ================================================================
    # PASS 1 -- PDF pp.96-97.  Same configuration, full body.
    # ================================================================
    ('023612.40', '23624.03 01',
     'I6251 LVI,$X1,I6252  "-TEST MEMORY COMBOS."  bit 18 = 0'),
    ('023613.00', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) "-EXIC IN MAIN."'),
    ('023613.40', '24324.03 01',
     'LVI,$X1,I62SUB      (ext) "-PSIC IN MAIN."'),
    ('023614.00', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext) "-SUBJ IN MAIN."'),
    ('023614.40', '20.22 00',
     'Z,$X0                 check 5 witness: the PSIC word must not run'),
    ('023615.00', '23625.43 01',
     'LVI,$X1,I6253         in-range label: BIT 18 SET -> 023625.40'),
    ('023615.40', '24323.43 D0',
     'SVA,$X1,I62BR1      (ext) TRAP 1'),
    ('023616.00', '24327.02 10',
     'LX,$X1,I62EXV       (ext)'),
    ('023616.40', '24324.03 10',
     'SX,$X1,I62SUB       (ext)'),
    ('023617.00', '23627.03 01',
     'LVI,$X1,I6254         in-range label: bit 18 = 0 -> 023627.00,'
     ' which is the FIRST row of PDF p.97'),
    ('023617.40', '24325.03 D0',
     'SVA,$X1,I62BR2      (ext) TRAP 2'),
    ('023620.00', '23041.00 80',
     'SIC,I60SX1          (ext)'),
    ('023620.40', '22741.04 00',
     'BD,I60S1            (ext) BD here; passes 0 and 2 use B.  Not a typo'),
    ('023621.00', '13.22 00',
     'Z,$IND'),
    ('023621.40', '14.22 00',
     'Z,$MASK'),
    ('023622.00', '11.22 00',
     'Z,$R                  check 1 witness: the subject must write it'),
    ('023622.40', '10.22 00',
     'Z,$L'),
    ('023623.00', '24323.16 00',
     'EXIC,I62PSI         (ext)'),
    ('023623.40', '23630.04 00',
     'BD,I6255              in-range label: bit 18 = 0 -> 023630.00'),
    # ---- pass 1, the interruption trap -----------------------------
    ('023624.00', '1310.00 80',
     'I6252 SIC,SEN        (ext) "-INT ON EXIC TO PSIC ON MAIN TO"'
     ' -- "ON MAIN", DECK TYPO, measured'),
    ('023624.40', '1304.04 00',
     'BD,SERS               (ext) "-VFL LOAD IN MAIN."'),
    ('023625.00', '23630.04 00',
     'BD,I6255'),
    # ---- pass 1, TRAP 1 --------------------------------------------
    ('023625.40', '1310.00 80',
     'I6253 SIC,SEN        (ext) "-EXIC RELINQUISHES CONTROL TO INSTRUCT"'),
    ('023626.00', '1304.04 00',
     'BD,SERS               (ext) "-FOLLOWING PSEUDO IC."'),
    ('023626.40', '23630.04 00',
     'BD,I6255              last row of PDF p.96'),
    # ---- pass 1, TRAP 2 -- PDF p.97 begins -------------------------
    ('023627.00', '1310.00 80',
     'I6254 SIC,SEN        (ext) "-EXIC RELINQUISHES CONTROL TO INSTRUCT"'
     '  PDF p.97 begins'),
    ('023627.40', '1304.04 00',
     'BD,SERS               (ext) "-FOLLOWING INSTRUCT ADDRESSED BY PSIC."'),
    # ---- pass 1, the verification body -----------------------------
    ('023630.00', '11.00 80 000000.20 50',
     'I6255 L(BU),$R       FULL WORD, word-aligned; read $R back as one'
     ' 64-bit BU field'),
    ('023631.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023631.40', '1304.34 C2',
     'BRZ,SERS              (ext) branches when RZ is ON;'
     ' "-EXIC SUBJ INST NOT EXECUTED."'),
    ('023632.00', '24327.34 10',
     'LX,$X14,I62EXV      (ext) the MASTER subject, as an index word'),
    ('023632.40', '24324.36 10',
     'LX,$X15,I62SUB      (ext) the WORKING COPY, as an index word'),
    ('023633.00', '37.34 90',
     'KV,$X14,$X15          VALUE fields, bits 0-24'),
    ('023633.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023634.00', '1304.32 C0',
     'BZXE,SERS             (ext) branches when XE is OFF;'
     ' "-BITS 0-24 OF SUBJ INST CHNGD."'),
    ('023634.40', '37.37 50',
     'SC,$X15,$X15          COUNT -> VALUE so KV can see it.  X15 FIRST'),
    ('023635.00', '36.35 50',
     'SC,$X14,$X14          pass 2 prints this pair the other way round'),
    ('023635.40', '37.34 90',
     'KV,$X14,$X15          COUNT fields, bits 28-45'),
    ('023636.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023636.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-BITS 28-45 OF SUBJ INST CHNGD."'),
    ('023637.00', '37.37 70',
     'SR,$X15,$X15          REFILL -> VALUE.  X15 FIRST'),
    ('023637.40', '36.35 70',
     'SR,$X14,$X14'),
    ('023640.00', '37.34 90',
     'KV,$X14,$X15          REFILL fields, bits 46-63'),
    ('023640.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023641.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-BITS 46-63 OF SUBJ INST CHNGD."'),
    ('023641.40', '20.00 80 000000.20 50',
     'L(BU),$X0            FULL WORD STRADDLING 023641.40 / 023642.00'),
    ('023642.40', '1310.00 80',
     'SIC,SEN               (ext) the page resumes at .40, two half-words'
     ' on -- the straddle, printed'),
    ('023643.00', '1304.34 C0',
     'BZRZ,SERS             (ext) branches when RZ is OFF;'
     ' "-INST AT PSIC WAS EXECUTED."'),
    ('023643.40', '24323.02 10',
     'LX,$X1,I62PSI       (ext) the pseudo-IC word itself; 18-bit'),
    ('023644.00', '24324.03 04',
     'KVI,$X1,I62SUB      (ext) 19-bit value field: bit 18 = 0 -> 024324.00'),
    ('023644.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023645.00', '1304.32 C2',
     'BXE,SERS              (ext) branches when XE is ON -- the OPPOSITE'
     ' polarity to the three rows above;'
     ' "-PSEUDO IC UNCHANGED BY EXIC."'),

    # ================================================================
    # PASS 2 -- PDF pp.97-98.  PSIC in index storage.
    # ================================================================
    ('023645.40', '23657.43 01',
     'LVI,$X1,I6256         "-EXIC IN MAIN."; BIT 18 SET -> 023657.40.'
     '  No "-TEST MEMORY COMBOS." heading in this pass'),
    ('023646.00', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) "-PSIC IN IX STG."'),
    ('023646.40', '24324.03 01',
     'LVI,$X1,I62SUB      (ext) "-SUBJ IN MAIN."'),
    ('023647.00', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext) the PSIC word is still filled in in MAIN'),
    ('023647.40', '20.22 00',
     'Z,$X0'),
    ('023650.00', '23661.03 01',
     'LVI,$X1,I6257         bit 18 = 0 -> 023661.00, the FIRST row of'
     ' PDF p.98'),
    ('023650.40', '24323.43 D0',
     'SVA,$X1,I62BR1      (ext) TRAP 1'),
    ('023651.00', '24327.02 10',
     'LX,$X1,I62EXV       (ext)'),
    ('023651.40', '24324.03 10',
     'SX,$X1,I62SUB       (ext)'),
    ('023652.00', '23662.43 01',
     'LVI,$X1,I6258         BIT 18 SET -> 023662.40'),
    ('023652.40', '24325.03 D0',
     'SVA,$X1,I62BR2      (ext) TRAP 2'),
    ('023653.00', '23041.00 80',
     'SIC,I60SX1          (ext)'),
    ('023653.40', '22741.10 00',
     'B,I60S1             (ext) B here; pass 1 uses BD.  Not a typo'),
    ('023654.00', '24323.04 10',
     'LX,$X2,I62PSI       (ext) THE COMBINATION: the PSIC into index 2'),
    ('023654.40', '13.22 00',
     'Z,$IND'),
    ('023655.00', '14.22 00',
     'Z,$MASK'),
    ('023655.40', '11.22 00',
     'Z,$R'),
    ('023656.00', '10.22 00',
     'Z,$L'),
    ('023656.40', '22.16 00',
     'EXIC,$X2              the pseudo-IC IN INDEX STORAGE -- the only'
     ' instruction difference between the two combinations'),
    ('023657.00', '23663.44 00',
     'BD,I6259              BIT 18 SET -> 023663.40'),
    # ---- pass 2, the interruption trap -----------------------------
    ('023657.40', '1310.00 80',
     'I6256 SIC,SEN        (ext) "-INT ON EXIC TO PSIC IN IX STG"'
     ' -- no period, the sentence runs on'),
    ('023660.00', '1304.04 00',
     'BD,SERS               (ext) "-TO VFL LOAD IN MAIN."'),
    ('023660.40', '23663.44 00',
     'BD,I6259              last row of PDF p.97'),
    # ---- pass 2, TRAP 1 -- PDF p.98 begins -------------------------
    ('023661.00', '1310.00 80',
     'I6257 SIC,SEN        (ext) "-EXIC RELINQUISHES CONTROL TO INSTRUCT"'
     '  PDF p.98 begins'),
    ('023661.40', '1304.04 00',
     'BD,SERS               (ext) "-FOLLOWING PSEUDO IC."'),
    ('023662.00', '23663.44 00',
     'BD,I6259'),
    # ---- pass 2, TRAP 2 --------------------------------------------
    ('023662.40', '1310.00 80',
     'I6258 SIC,SEN        (ext) "-EXIC RELINQUISHES CONTROL TO INSTRUCT"'),
    ('023663.00', '1304.04 00',
     'BD,SERS               (ext) "-FOLLOWING INSTRUCT ADDRESSED BY PSIC."'),
    # ---- pass 2, the verification body -----------------------------
    ('023663.40', '11.00 80 000000.20 50',
     'I6259 L(BU),$R       FULL WORD STRADDLING 023663.40 / 023664.00'),
    ('023664.40', '1310.00 80',
     'SIC,SEN               (ext) the page resumes at .40 -- the straddle'),
    ('023665.00', '1304.34 C2',
     'BRZ,SERS              (ext) RZ ON; "-EXIC SUBJ INST NOT EXECUTED."'),
    ('023665.40', '24327.34 10',
     'LX,$X14,I62EXV      (ext)'),
    ('023666.00', '24324.36 10',
     'LX,$X15,I62SUB      (ext)'),
    ('023666.40', '37.34 90',
     'KV,$X14,$X15'),
    ('023667.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023667.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-BITS 0-24 OF SUBJ INST CHNGD."'),
    ('023670.00', '36.35 50',
     'SC,$X14,$X14          X14 FIRST here -- pass 1 prints X15 first'),
    ('023670.40', '37.37 50',
     'SC,$X15,$X15'),
    ('023671.00', '37.34 90',
     'KV,$X14,$X15'),
    ('023671.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023672.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-BITS 28-45 OF SUBJ INST CHNGD."'),
    ('023672.40', '36.35 70',
     'SR,$X14,$X14          X14 FIRST here -- pass 1 prints X15 first'),
    ('023673.00', '37.37 70',
     'SR,$X15,$X15'),
    ('023673.40', '37.34 90',
     'KV,$X14,$X15'),
    ('023674.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023674.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-BITS 46-63 OF SUBJ INST CHNGD."'),
    ('023675.00', '20.00 80 000000.20 50',
     'L(BU),$X0            FULL WORD, word-aligned here'),
    ('023676.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023676.40', '1304.34 C0',
     'BZRZ,SERS             (ext) RZ OFF; "-INST AT PSIC WAS EXECUTED."'),
    ('023677.00', '22.02 10',
     'LX,$X1,$X2            the pseudo-IC IN INDEX STORAGE; pass 1 reads'
     ' I62PSI here instead'),
    ('023677.40', '24324.03 04',
     'KVI,$X1,I62SUB      (ext) bit 18 = 0 -> 024324.00'),
    ('023700.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('023700.40', '1304.32 C2',
     'BXE,SERS              (ext) XE ON; "-PSEUDO IC UNCHANGED BY EXIC."'),
    # ---- routine 1262's TEST 2A exit -------------------------------
    ('023701.00', '23702.10 00',
     'B,$+1.0               self-relative: +1 word -> 023702.00; bit 18'
     ' = 0 because the row is word-aligned.  Cf 2B 023774.40, bit 18 = 1'),
    ('023701.40', '23576.44 00',
     'BD,I6247              BIT 18 SET -> 023576.40, this file\'s own SLC:'
     ' an anchor, not evidence'),
    ('023702.00', '1311.40 80',
     'SIC,SEN0+.32        (ext) 24-bit BIT address: offset 40 = 32 bits'),
    ('023702.40', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP."'),
    ('023703.00', '23703.44 00',
     'BD,$+.32              self-relative: +32 bits -> 023703.40; BIT 18'
     ' SET.  Cf 2B 023776.40, bit 18 = 0'),
    # ---- the continuity bridge -------------------------------------
    ('023703.40', '24171.32 10',
     'LX,$X13,IC262       (ext) "-UPDATE CONTINUITY CHECK."; 18-bit'),
    ('023704.00', '24526.32 B0',
     'V+,$X13,BIT4        (ext) TEST 2A done = bit 4'),
    ('023704.40', '24171.33 10',
     'SX,$X13,IC262       (ext) 18-bit; cf the LX two rows up, 24171.32'),
]

# TIER 1 (real witnesses, 12): I6248..I6259.  Each is defined inside the
# range, printed in the listing's own name field, and reached by an
# operand whose octal pair is decoded in the docstring.  Six of them sit
# at a .40 and six at a .00.
# TIER 3 (anchor, not evidence, 1): I6247 -- the first label after the
# SLC.  Its LOCATION is trivially right; what is NOT trivial is that
# 023701.40's "BD,I6247" row lands where it does, which needs all 130
# rows before it to have been sized correctly.
SYMBOLS = {
    'I6248': '023606.40', 'I6249': '023610.00', 'I6250': '023611.40',
    'I6251': '023612.40', 'I6252': '023624.00', 'I6253': '023625.40',
    'I6254': '023627.00', 'I6255': '023630.00', 'I6256': '023657.40',
    'I6257': '023661.00', 'I6258': '023662.40', 'I6259': '023663.40',
    'I6247': '023576.40',
}

assert len(ROWS) == 137, len(ROWS)

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 2A '))

# ---------------------------------------------------------------------
# WHAT I AM NOT SURE OF
# ---------------------------------------------------------------------
# 1. RZ = 57.  THE NAME AND THE BIT NUMBER ARE NOW FIRST-HAND -- C22-6531
#    Appendix A, printed p.56, reads "$ RZ 2 Result Zero 11 57", and
#    that page was read at 400 dpi for this file.  WHAT IS STILL NOT
#    READ FIRST-HAND is the NARRATIVE paragraph saying what sets it --
#    i.e. which operations' results actuate Result Zero, and on which
#    field.  XE has such a paragraph (Reference Manual printed p.23,
#    quoted above) and RZ's equivalent was not located in 22-6530-2 in
#    the pages searched (printed 23, 32, 44-45, 49-50, 56).  It does
#    not affect any encoding here; it affects only the PROSE reason
#    given for BRZ/BZRZ polarity, which is otherwise settled by the
#    printed hex byte and by what the surrounding rows zero.
# 2. The SEMANTICS of "SC,$X15,$X15" are read here as "store index 15's
#    count field into the word at location $X15, which is index 15
#    itself, so the count lands in the value field".  That reading is
#    what makes checks 3 and 4 coherent and it matches the deck's own
#    "BITS 28-45" / "BITS 46-63" messages, but the Reference Manual's
#    STORE COUNT paragraph was not read first-hand for this file.  The
#    ENCODING is not in doubt (DIR_INDEX_CODES["SC"] = 0b10101 is
#    exercised by injection 4 and by 20+ existing rows elsewhere).
# 3. WHY PASS 0 EXISTS AT ALL, given pass 1 re-runs the identical
#    memory configuration with strictly more checking.  Two halves of
#    this are NOT in doubt and are argued from the rows above: pass 0
#    cannot check execution or stepping (it never zeroes $R, $L or $X0
#    first), and pass 1 must re-zero the accumulator because pass 0's
#    subject dirtied it.  WHAT REMAINS AN INFERENCE ABOUT INTENT is the
#    COUNTING: that the header's "TWO POSSIBLE MEMORY COMBINATIONS"
#    counts passes 1 and 2 and not pass 0.  The deck's own
#    "-TEST MEMORY COMBOS." heading appears on pass 1 and not on pass 0,
#    which supports it; nothing states it.
# 4. THE SUBJECT IS THE SAME IN ALL THREE PASSES -- I62EXV, the
#    full-word "L(BU),I00O".  TEST 2A never varies the instruction
#    CLASS; that is TEST 2B's job.  I did not find a row anywhere in
#    023576.40-023704.40 that loads a different subject, but I did not
#    re-read pp.99-102 to confirm the division of labour is exactly
#    that clean.
# 5. "-PSIC IS PSEUDO IC." at 023606.00 is read as a legend explaining
#    the deck's own abbreviation.  It sits on the "BD,I6251" row, which
#    is a branch and has nothing to do with the pseudo-IC, so it is
#    almost certainly a comment-column note rather than a comment on
#    that instruction.  Recorded as printed.
