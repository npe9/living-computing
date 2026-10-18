#!/usr/bin/env python3
"""verify_ax5b_162_test2b_head_tail_listing.py -- jb_ax5b "I-Box 5",
routine 1262 ("TEST EX AND EXIC"), TEST 2B
(../decks/ax5b_162_test2b_head_tail.strap) against the listing's printed
machine code.  THE TWO ENDS OF TEST 2B AROUND THE MIDDLE THAT IS ALREADY
TRANSCRIBED:

    023742.40-023767.40 (PDF p.101) is verify_ax5b_162_exic_listing.py.
    THIS FILE is the two ends around it --
        HEAD  023705.00-023742.00, PDF p.99 whole plus the five rows
              that spill onto PDF p.100.  59 half-words.
        TAIL  023770.00-024000.00, PDF p.102.  17 half-words.
    76 rows here + 43 rows there = 119, and 023705.00 through 024000.00
    inclusive is 119 half-words.  TEST 2B and its exit are transcribed
    end to end with nothing left behind.

THE TWO FILES DO NOT OVERLAP, AND THAT WAS CHECKED ON THE ASSEMBLED
IMAGE, not on the row lists.  The second "SLC, (8)23770.00" jumps
forward over 026 half-words, so the question is whether SLC merely
moves the counter or fills the gap.  It moves it: assembling this
program writes 39 words, and of the words between the two segments only
023742 exists at all -- because this file's LAST head row, 023742.00
"BD,I6266", is that word's LEFT half.  Its right half, 023742.40, is
the sibling's FIRST row and assembles here as 00000000; words
023743-023767 are absent from the image entirely.  Nothing this file
writes is a location the sibling also claims.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.


WHAT THE "THREE RULES PER CLASS" ACTUALLY ARE
---------------------------------------------
Established from these pages, not from a block map.  TEST 2B's entry
label is I6260 at 023705.00; its header comment is
"-TEST 2B, CHK EXIC OF NON BRANCH / -CLASS INSTRUCTIONS, DIR IX."  It
sweeps five classes -- DIR IX, IMMED IX, MISC, FLT PT, FULL WD VFL --
each identified by the "LX,$X1,<subject>" row of its setup, and checks
three rules per class, each with its own error entry:

  (a) EXIC to that class must NOT INTERRUPT.  The setup plants the
      class's own error label in the interrupt-table entry
      ("LVI,$X1,I626n / SVA,$X1,I62ITE"), zeroes $IND and $MASK, and
      issues "EXIC,I62PSI".  An interruption lands on
      "I626n SIC,SEN / B,SERS" -- "-INT WHEN EXIC TO / -A <class>
      INSTR."  No interruption and the straight-line "BD,I626n+1"
      skips the entry.
  (b) The subject instruction must have EXECUTED.  "LX,$X1,<reg>"
      reloads what the subject was supposed to change, then
      "SIC,SEN / B{Z}XVZ,SERS" -- "-SUBJ INST WAS <class> / -AND WAS
      NOT EXECUTED."
  (c) The PSEUDO-INSTRUCTION COUNTER must have been STEPPED BY THE
      SUBJECT'S LENGTH.  "KV,$X2,I62PSI / SIC,SEN / BZXE,SERS" --
      "-PSEUDO IC NOT STEPPED <n> CORRECTLY / -WHEN SUBJ INST WAS
      <class>."

(c) IS THE WHOLE DIFFERENCE FROM TEST 1B, AND THE DIFFERENCE IS
STRUCTURAL, not an extra check bolted on.  TEST 1B
(verify_ax5b_162_test1b_listing.py) sweeps the same five classes for
plain EX with only (a) and (b), because plain EX HAS NO PSEUDO-IC.
Reference Manual printed p.50 (PDF p.53; PDF page = printed page + 3),
read first-hand at 400 dpi for this file:

    EXECUTE (EX): "Bits 0-18 of the effective address form the address
    of the location of a subject instruction that is fetched and
    executed.  Subject instructions of EXECUTE may occupy any
    addressable location."

    EXECUTE INDIRECT AND COUNT (EXIC): "Bits 0-18 of the full-word
    addressed by bits 0-17 of the effective address are used as a
    pseudo-instruction counter.  The contents of the pseudo-instruction
    counter address the location of a subject instruction that is
    fetched and executed.  After the subject instruction has been
    fetched but prior to its execution, the pseudo-instruction counter
    is stepped.  If the subject instruction is half-length, the
    pseudo-instruction counter is stepped once; if full-length, twice."

AND THE DECK MAKES "ONCE / TWICE" EXECUTABLE.  The four half-length
classes check .32 (one half-word); the FULL WD VFL class, whose subject
I62EXV is the full-word "L(BU),I00O" (PDF p.109,
verify_ax5b_162_int_entry_listing.py), checks 1.0 (one full word):

    023733.00  V+I,$X2,0.32   0.45 05    "-PSEUDO IC NOT STEPPED .32"
    023772.40  V+I,$X2,1.0    1.05 05    "-PSEUDO IC NOT STEPPED 1.0"

THE SAME PAGE SETS A TYPOGRAPHIC TRAP, recorded in this project and
re-confirmed here at 400 dpi.  The left column of PDF p.53 ends
"...but cannot occupy locations addressed between 0 and" and the RIGHT
column OPENS with "15.  Subject instructions of EXECUTE INDIRECT AND
COUNT may occupy any available locations with addresses 32.00 and
greater."  That "15." is the TAIL of the left column's sentence, not a
list number.  A skimming reader mis-parses it.

TWO IDIOMS FOR RULE (c), AND BOTH ARE PRINTED IN THIS FILE'S ROWS.
DIR IX, the first class, checks the pseudo-IC ABSOLUTELY -- it never
saves the "before" value and builds the expected "after" from the
label: "LVI,$X1,I62SUB+.32 / KV,$X1,I62PSI" at 023720.40/023721.00.
The other four check it RELATIVELY -- "LV,$X2,I62PSI" before the EXIC,
"V+I,$X2,<step>" after it, "KV,$X2,I62PSI".  DIR IX is therefore the
only class whose (c) needs no $X2 at all.

THE HALF-WORD DIFFERENCE, recorded because it is easy to "tidy" away:
each class zeroes exactly what its subject writes.  DIR IX and IMMED IX
do "Z,$X1"; MISC does not (its subject IS "Z,$X1"); FLT PT does
"Z,$L / Z,$R"; FULL WD VFL does "Z,$R" only.  p.101's MISC rule-(b) row
is BZXVZ for exactly that reason.


BRANCH POLARITY, SETTLED BY ARITHMETIC ON THE PRINTED HEX BYTE
--------------------------------------------------------------
A committed file in this repo once had this inverted and survived every
check, because prose is not executable.  So: not prose.  strap_asm's
enc_branch_ind lays out bits 24-31 as 1000 (the identifying literal,
bits 25-28) then clear (29), branchOn (30), idx (31), with bit 24 the
low bit of the 6-bit indicator number.  Both error shapes are in this
file's rows and the printed byte discriminates them:

    BXVZ,SERS  -> 1304.31 42.  Pair 31 = 011001: bit 18 = 0, indicator
                  bits 19-23 = 11001.  Hex 42 = 0 1000 0 1 0, so
                  indicator bit 24 = 0 (number 110010 = 50 = XVZ),
                  clear = 0, BRANCHON = 1, idx = 0.
                  BRANCHES WHEN XVZ IS ON.
    BZXE,SERS  -> 1304.32 C0.  Pair 32 = 011010: bits 19-23 = 11010.
                  Hex C0 = 1 1000 0 0 0, so indicator bit 24 = 1
                  (number 110101 = 53 = XE), clear = 0, BRANCHON = 0.
                  BRANCHES WHEN XE IS OFF.

And that is the right way round for the rules.  Reference Manual
printed p.23 (PDF p.26), read at 300 dpi for this file: "Index Value
Zero (XVZ).  This indicator is set to one when the value field is
zero."  "Index Equal (XE).  This indicator is set to one when the field
in the index specified by J is equal to the comparand."  So rule (b)
errors when the reloaded index value IS zero (the subject never ran)
and rule (c) errors when the KV comparison came out UNEQUAL.

THE TRAILING Z IN "BXVZ" IS PART OF THE INDICATOR NAME, NOT A CLEAR.
XVZ *is* the indicator ("Index Value Zero", p.23 above), and the clear
bit is 0 in the printed byte -- 0x42 and 0xC0 both have bit 29 = 0.
strap_asm.classify_branch_indicator tries the "BZ" prefix first, so
"BXVZ" parses as B + XVZ and "BZXE" as BZ + XE; a genuine clearing
branch would print bit 29 = 1.  Nothing in this file's rows clears.


BIT-18 SELF-CHECKS
------------------
Print format (listing_oracle.fmt_half): bits 0-17 as 6 octal digits,
".", bits 18-23 as 2 octal digits, bits 24-31 as 2 hex digits.  BIT 18
IS THE TOP BIT OF THE OCTAL PAIR.

THE FIELD LAYOUT IS A CITATION, NOT AN INFERENCE.  Reference Manual
printed p.23 (PDF p.26), the Direct Index Arithmetic format diagram,
read at 300 dpi for this file: ADDRESS 0 | J 19 | OP. 23 | I 28 | 31.
Its text: "In the majority of these operations, 19 bits of the
effective address are used in order to permit addressing of half-words.
THE TWO EXCEPTIONS USE ONLY 18 BITS OF THE EFFECTIVE ADDRESS BECAUSE
THEY REQUIRE FULL-WORD OPERANDS."  The two exceptions are LX and SX --
"Load Index (LX): The index word specified by J is replaced by the
full-word specified by BITS 0-17 of the effective address", against
"Load Value (LV): ... is replaced by bits 0-24 of the half-word
specified by BITS 0-18 of the effective address", same page.

The exclusion therefore has FOUR CLASSES WITH THREE DIFFERENT REASONS.
Rows here fall into all four:

  1. HALF-WORD SELECT -- decoded below.  Branch targets (B, BD, BXVZ,
     BZXE) and the 19-bit value-field ops (LVI, LV, SVA, KV, V+, V+I).
  2. LX / SX -- EXCLUDED, 18 bits, p.23 above.  All 11 LX/SX rows here
     (7 LX, 4 SX) print a pair whose TOP BIT is 0 -- 24322.02, 24324.03,
     24332.02, 24331.02, 24171.32, 24171.33, 21.02, 11.02 -- and that
     bit is not a half-word select.  See the MEASURED NULL below, which
     tests the claim empirically rather than asserting it.
  3. SIC -- EXCLUDED, its operand is a 24-bit BIT address and the pair
     is a BIT OFFSET within the word, not bits 18-23 of a half-word
     address.  Rows: 023712.40 "SIC,I60SX1" -> 23041.00 80,
     023775.40 "SIC,SEN0+.32" -> 1311.40 80, and the six "SIC,SEN" ->
     1310.00 80.
     A MEASURED NULL OF THE DISCRIMINATION ITSELF, stated because the
     trap is real: 40 octal = 32 decimal, and 32 bits is ALSO exactly
     one half-word, so "1311.40" reads identically under the wrong
     interpretation.  This block contains NO SIC whose offset is not a
     multiple of 32, so its rows cannot separate the two readings; the
     bit-offset reading comes from the encoder and the pocket card, not
     from these rows.  The arithmetic that WOULD separate them is an
     offset such as +.8, which would print .10 as a bit offset and be
     unrepresentable as a half-word address.
  4. TRANSMIT's A1 -- the fourth excluded class, a 24-bit BIT address
     in a full-word instruction.  NO TRANSMIT APPEARS IN THIS BLOCK, so
     the class is named for completeness and exercises nothing here.

DECODES, each read back against the page's own label column or against
arithmetic on the location counter.  ADDRESS WITNESSES first -- labels
DEFINED inside the transcribed range, printed in the listing's own name
field, and reached by an operand whose octal pair this file decodes:

  023706.00  "LVI,$X1,I6261"  -> 23716.03 01.  Pair 03 = 000011, bit 18
             = 0, so .00: 023716.00 -- where p.99 prints I6261.
  023707.00  "LVI,$X1,I6262"  -> 23717.03 01.  Bit 18 = 0: 023717.00 --
             where p.99 prints I6262.
  023715.40  "BD,I6262"       -> 23717.04 00.  Pair 04 = 000100, bit 18
             = 0: 023717.00.  The SAME target as the row above by a
             different instruction class, so the two agree independently.
  023722.40  "LVI,$X1,I6263"  -> 23730.43 01.  Pair 43 = 100011, BIT 18
             = 1, so .40: 023730.40 -- where p.99 prints I6263.  Note
             the pair differs from 023706.00's 03 ONLY in bit 18.
  023730.00  "BD,I6264"       -> 23731.44 00.  Pair 44 = 100100, BIT 18
             = 1: 023731.40 -- where p.99 prints I6264.

SELF-RELATIVE ROWS, the location counter's own witnesses:

  023774.40  "B,$+1.0"        -> 23775.50 00.  Pair 50 = 101000, BIT 18
             = 1: 023775.40.  And 023774.40 + 1 word (64 bits) is
             023775.40, the "BD,I6260" row.
  023776.40  "BD,$+.32"       -> 23777.04 00.  Pair 04, bit 18 = 0:
             023777.00.  And 023776.40 + 32 bits is 023777.00, the
             "LX,$X13,IC262" row.

THE ONE ROW WHERE BIT 18 IS THE WHOLE POINT.  I62PSI and I62BR1 are the
two halves of the SAME WORD, 024323, and the listing distinguishes them
by nothing but bit 18:

  023707.40  "SVA,$X1,I62BR1" -> 24323.43 D0.  Pair 43 = 100011, BIT 18
             = 1: 024323.40.
  023711.00  "SVA,$X1,I62PSI" -> 24323.03 D0.  Pair 03 = 000011, bit 18
             = 0: 024323.00.
  Same word address, same J, same op byte; the pairs differ in one bit.
  PDF p.109's label column (verify_ax5b_162_int_entry_listing.py) prints
  I62PSI at 024323.00 and I62BR1 at 024323.40.  Two pages agree.

LABEL-PLUS-OFFSET, where bit 18 carries the arithmetic:

  023720.40  "LVI,$X1,I62SUB+.32" -> 24324.43 01.  Pair 43, BIT 18 = 1:
             024324.40.  I62SUB is 024324.00, and +32 bits is 024324.40
             -- the expected pseudo-IC after a half-length subject.
             Compare 023710.40's plain "LVI,$X1,I62SUB" -> 24324.03 01,
             bit 18 = 0.  One source token, one bit.

EXTERNAL-TARGET DECODES, which show the half-word select is being
PLACED and not merely assumed to be zero:

  023705.00  "LVI,$X1,I62INT" -> 24220.03 01: bit 18 = 0 -> 024220.00.
  023706.40  "SVA,$X1,I62ITE" -> 24320.03 D0: bit 18 = 0 -> 024320.00.
  023710.00  "SVA,$X1,I62BR2" -> 24325.03 D0: bit 18 = 0 -> 024325.00.
  023713.00  "B,I60S1"        -> 22741.10 00: pair 10 = 001000, bit 18
             = 0 -> 022741.00.  docs/listing_typography.md measured the
             label I60S1 at 022741.00 on PDF p.83 for a different
             purpose entirely; the number agrees.
  023716.40  "B,SERS"         -> 1304.10 00: bit 18 = 0 -> 001304.00.
  023721.00  "KV,$X1,I62PSI"  -> 24323.02 90: pair 02 = 000010, bit 18
             = 0 -> 024323.00.  J = 0001 = $X1; the other four classes
             print 04 = 000100, J = 0010 = $X2.
  023727.00  "LV,$X2,I62PSI"  -> 24323.04 30: bit 18 = 0 -> 024323.00.
  023733.00  "V+I,$X2,0.32"   -> 0.45 05: pair 45 = 100101, BIT 18 = 1
             -> 000000.40 = 32 bits.  The immediate IS a 19-bit address
             quantity and bit 18 is carrying its whole value.
  023772.40  "V+I,$X2,1.0"    -> 1.05 05: pair 05 = 000101, bit 18 = 0
             -> 000001.00 = 64 bits.  Same J, same op byte, one word up.
  023735.00  "LVI,$X1,I6265"  -> 23742.43 01: BIT 18 = 1 -> 023742.40.
  023742.00  "BD,I6266"       -> 23743.44 00: BIT 18 = 1 -> 023743.40.
             Both are cross-page: p.101's label column prints I6265 at
             023742.40 and I6266 at 023743.40.
  023775.00  "BD,I6260"       -> 23705.04 00: bit 18 = 0 -> 023705.00 --
             this file's own SLC, so an anchor and not evidence.
  023776.00  "B,SSW"          -> 1301.10 00: bit 18 = 0 -> 001301.00.
  023777.40  "V+,$X13,BIT5"   -> 24527.32 B0: pair 32 = 011010, bit 18
             = 0 -> 024527.00.  verify_ax5b_bit_table_listing.py puts
             BIT5 at 024527.00 off PDF pp.114-115.  Two pages agree.


WITNESS TIERING -- NOT INFLATED
-------------------------------
EVERY "SYN" IN THE .strap IS AN INPUT, NOT A WITNESS.  SEN, SERS, SEN0,
SSW, I60S1, I60SX1, I62INT, I62ITE, I62EX, I62PSI, I62BR1, I62SUB,
I62BR2, I62EXM, I62EXI, IC262, BIT5, I6265, I6266 all take their value
from a number this transcription supplied, so their rows come out right
by construction and prove only that the assembler places every OTHER
field where the listing places it.

AN "SLC"-PLACED LABEL IS AN ANCHOR, NOT EVIDENCE.  I6260 (023705.00) is
the first label after the head SLC and I6269 (023770.00) is the first
after the tail SLC.  Both are asserted below; neither is evidence, and
"BD,I6260" at 023775.00 traces its target straight back to that same
SLC.  (Its own LOCATION is evidence -- it is right only if all 59 head
rows and the first 11 tail rows were sized right.)

  TIER 1, REAL ADDRESS WITNESSES (4): I6261, I6262, I6263, I6264.
    Each is defined inside the range, printed in p.99's own name field,
    and reached by an operand whose octal pair is decoded above.
  TIER 2, NEAR-TRIVIAL (1): I6270 at 023771.00.  Defined inside the
    range and printed in p.102's name field, but NOTHING in this file
    references it -- its only reference, "BD,I6270" at 023767.40, is in
    verify_ax5b_162_exic_listing.py's range.  Within this file it is
    the tail SLC plus two half-words of row sizing.  Asserted anyway;
    labelled for what it is.
  TIER 3, ANCHORS (2): I6260, I6269.
  TIER 4, CROSS-PAGE CORROBORATION, which is not a witness for THESE
    rows but does remove the worry that a SYN was a number chosen to
    fit: I6265/I6266 against PDF p.101's label column; I62PSI, I62BR1,
    I62BR2, I62ITE, I62EX, I62SUB, I62EXM, I62INT against PDF p.109's
    label column (verify_ax5b_162_int_entry_listing.py); I62EXI against
    PDF p.110 (verify_ax5b_162_test3b_listing.py); I60S1 against
    docs/listing_typography.md's own 600 dpi measurement on PDF p.83;
    BIT5 against verify_ax5b_bit_table_listing.py on PDF p.114.


TYPO vs SCAN DAMAGE: NEITHER.  NOT ONE GARBLED GLYPH IN 76 ROWS
---------------------------------------------------------------
Read at 600 dpi.  Every character in every error message is a clean,
well-inked print: no letter is ragged (which is what damage leaves) and
none is a clean wrong letter in a word whose other instances on the
same or an adjacent line are right (which is what a typo leaves).  No
letter is dropped, so the pitch test was not needed.  Said plainly
rather than forced into the binary.

What the block DOES have is three CLEAN-PRINT DECK-AUTHORING
inconsistencies, which are a different thing:

  1. 023771.40 "-SUBJ INST WAS FLT PT" stands in the FULL WD VFL class.
     The class's own pseudo-IC message two rows later WAS updated --
     "-WHEN SUBJ INST WAS VFL FULL WD." -- and this one was not.  The
     clone-and-edit runs the other way on p.101, where the MISC and
     FLT PT pseudo-IC messages still say "IMMED IX".  DO NOT READ THE
     CLASS OFF THE ERROR TEXT anywhere in routine 1262.
  2. 023735.00 "-MISC" carries NO trailing period where every sibling
     class heading does ("-IMMED IX.", "-FLT PT.", "-FULL WD VFL.").
     Confirmed on a tight crop: nothing follows the C.
  3. 023732.00 "-SUBJ INST WAS IMMED IX," ends in a COMMA.  Settled by
     the DESCENDER, comparing against a correct instance on the
     adjacent line: the glyph hangs below the baseline, while
     "-AN IMMED IX INST." one row above ends in a period that does not.

THE ONE GLYPH THAT NEEDED MEASURING, MEASURED HERE AND NOT INHERITED.
023775.40's operand is "SEN" plus one round glyph.  This repo has read
that glyph both ways in the past.  verify_ax5b_162_test3b_listing.py
measured it on PDF p.108; this is an INDEPENDENT measurement on PDF
p.102, at 600 dpi, by segmenting glyph bounding boxes from pixel-column
ink profiles:

  calibration, PDF p.102 row 023773.40, ONE printed comment line
  ("-PSEUDO IC NOT STEPPED 1.0 CORRECTLY") carrying both characters:
      letter O  50, 50, 50 px  (PSEUDO, NOT, CORRECTLY)
      digit  0  44 px          (the "1.0")
      digit  1  33 px, letter I 23 px -- the I/1 gulf, incidentally
  second calibration, PDF p.102 row 023776.00 ("-TO SSIP."):
      letter O  51 px
  digit calibration on 023775.40's OWN row and OWN y-band, machine-code
  column "1311.40 80":
      digit  0  44 px, 44 px
  MEASURED, the glyph after SEN at 023775.40:  43 px.

43 against 44 for the digit and 50-51 for the letter.  IT IS THE DIGIT.
This file spells the symbol SEN0, agreeing with p.108's independent
reading.


NO MNEMONIC HERE IS A FIRST FOR THE REPO, and that was checked by grep,
not assumed.  Counts are OTHER verify_*.py files whose text contains the
mnemonic token, so they are lower bounds and every one is >= 5:
LX 42, SIC 41, BD 36, SX 35, SV 26, V+ 24, KV 23, LV 21, LVI 20, SVA 19,
BZXE 14, BXVZ 13, V+I 10, EXIC 5.  The EXIC five are named because it is
the scarce one: verify_ax5b_1274_truncation_listing.py,
verify_ax5b_162_int_entry_listing.py, verify_ax5b_162_exic_listing.py
(TEST 2B's middle), verify_ax5b_162_test3a_listing.py and
verify_ax5b_162_test3b_listing.py.  This file adds three more printed
EXIC rows -- 023715.00, 023727.40, 023741.40 -- all "EXIC,I62PSI".
One candidate first was chased down and KNOCKED OUT: "V+I with a
word-granular immediate" is NOT new -- "V+I,$X2,1.0", "V+I,$X14,1.0",
"V+I,$X15,2.0" and "V+I,$X2,2.0" are all already printed in other
verify files here.  What this block adds is not a mnemonic but a pair:
0.32 and 1.0 in the SAME field of the SAME instruction six rows apart in
one routine, which is the Reference Manual's "once / twice" as a diff.


PROVEN DISCRIMINATING
---------------------
Five injections, each into strap/opcodes.py, each CONFIRMED APPLIED by
printing the patched line before the run (a sed that silently fails to
match produces "ALL TESTS PASSED", which reads exactly like a legitimate
measured null; that has happened in this project twice).
"rm -rf __pycache__" on BOTH sides of every injection.  Failure sets are
OBSERVED, not predicted:

  1. MISC_CODES["EXIC"] 0b011 -> 0b111
         023715.00, 023727.40, 023741.40                  (3 rows)
     All three EXIC rows in this file's range and nothing else.  The
     block's reason to exist.
  2. INDICATOR_BITS["XVZ"] 50 -> 14
         023720.00, 023732.40, 023772.00                  (3 rows)
     All three BXVZ rows, one per class, INCLUDING the one in the tail
     segment.  14 and not a one-bit flip on purpose: 51 is XVGZ and 48
     is XCZ, so a neighbour would have been a table collision rather
     than a clean perturbation.  14 is the only number in 0-63 that
     INDICATOR_BITS does not hold (verified by reading the table, not
     inherited from verify_ax5b_162_test1b_listing.py's claim).
  3. INDICATOR_BITS["XE"] 53 -> 14
         023722.00, 023734.40, 023774.00                  (3 rows)
     All three BZXE rows, and the XVZ rows are untouched -- the two
     indicator fields are independent.
  4. UNCOND_BRANCH_CODES["BD"] 0b001 -> 0b111
         023715.40, 023730.00, 023742.00, 023775.00,
         023776.40                                        (5 rows)
     Every BD row, spanning BOTH segments, which forecloses any worry
     that the tail SLC's rows are not really being exercised.  0b111 is
     free in UNCOND_BRANCH_CODES; note "B" rows are untouched, so the
     two unconditional-branch codes are separately pinned.
  5. DIR_INDEX_CODES["SV"] 0b10011 -> 0b10010
         023705.40                                        (1 row)
     The single SV in the whole block, "SV,$X1,$IA" -- TEST 2B's second
     printed row, the one that stores the interrupt-table address into
     $IA.  A one-row discriminator, and 0b10010 is not any other
     direct-index code.

  MEASURED NULL, WITH ITS ARITHMETIC AND WITH A LIVENESS PROOF.
  Sixth injection, into strap_asm.py's DIR_INDEX emit case (line 1445),
  making the assembler ENFORCE p.23's 18-bit rule for LX/SX by masking
  bit 18 off:

      ... int_shift=1 if op in ('LX','SX') else 0) & 0x7FFFF
   -> ... int_shift=1 if op in ('LX','SX') else 0) & (0x7FFFE if op in
                                          ('LX','SX') else 0x7FFFF)

  CONFIRMED APPLIED by diffing the file against a saved copy before the
  run, and reverted by restoring that copy (sha256 equal afterwards).
      OBSERVED: 0 of the 11 LX/SX rows changed.  (The other 72 row
      checks and all 7 symbol assertions are not reachable by a
      DIR_INDEX mask at all; the honest denominator is 11.)  The script
      still ends "ALL TESTS PASSED".
  That is the CORRECT result and the reason is arithmetic, not a dead
  patch: every LX/SX operand in this block is WORD-ALIGNED -- I62EX
  024322.00, I62SUB 024324.00, I62EXI 024332.00, I62EXM 024331.00,
  IC262 024171.00, $X1 000021.00 ($X1 is storage location 17, p.23),
  $R 000011.00 -- so the bit the patch clears is already 0 in all 11
  rows.
  LIVENESS PROVEN SEPARATELY, because "no change" is exactly what a
  patch that did not apply also produces.  Under the SAME patch, a
  one-off "LX,$X1,I62SUB+.32 / SX,$X1,I62SUB+.32" assembled to
  024324.02 10 / 024324.03 10; UNPATCHED the same two rows assemble to
  024324.42 10 / 024324.43 10.  The encoder moved by exactly bit 18;
  this block's data does not see it.
  AND THE INJECTION FOUND SOMETHING, recorded here rather than acted on
  because this file may not edit the assembler: strap_asm does NOT
  currently enforce the p.23 18-bit rule.  Unpatched, "LX,$X1,<label at
  a .40>" happily encodes bit 18 = 1, which no 7030 LX could mean.  It
  bites nothing today, and that was MEASURED rather than assumed: a
  sweep of every verify_*.py ROWS tuple in this directory parses 446
  LX/SX rows and finds ZERO whose printed octal pair has bit 18 set.
  A latent gap, worth a line in the assembler's TODO rather than a
  silent fix from a transcription file.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_162_test2b_head_tail.strap").read())

ROWS = [
    # ================================================================
    # HEAD -- PDF p.99.  TEST 2B entry and the DIR IX class setup.
    # ================================================================
    ('023705.00', '24220.03 01',
     'I6260 LVI,$X1,I62INT (ext) "-TEST 2B, CHK EXIC OF NON BRANCH"'),
    ('023705.40', '2.03 30',
     'SV,$X1,$IA            "-CLASS INSTRUCTIONS, DIR IX."'),
    ('023706.00', '23716.03 01',
     'LVI,$X1,I6261         in-range label: bit 18 = 0 -> 023716.00'),
    ('023706.40', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) plant the rule-(a) handler'),
    ('023707.00', '23717.03 01',
     'LVI,$X1,I6262         in-range label: bit 18 = 0 -> 023717.00'),
    ('023707.40', '24323.43 D0',
     'SVA,$X1,I62BR1      (ext) BIT 18 SET -> 024323.40'),
    ('023710.00', '24325.03 D0',
     'SVA,$X1,I62BR2      (ext) bit 18 = 0 -> 024325.00'),
    ('023710.40', '24324.03 01',
     'LVI,$X1,I62SUB      (ext) bit 18 = 0 -> 024324.00'),
    ('023711.00', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext) bit 18 = 0 -> 024323.00; cf 023707.40'),
    ('023711.40', '24322.02 10',
     'LX,$X1,I62EX        (ext) the DIR IX subject; 18-bit, see header'),
    ('023712.00', '24324.03 10',
     'SX,$X1,I62SUB       (ext) 18-bit'),
    ('023712.40', '23041.00 80',
     'SIC,I60SX1          (ext) 24-bit BIT address, offset 00'),
    ('023713.00', '22741.10 00',
     'B,I60S1             (ext) bit 18 = 0 -> 022741.00'),
    ('023713.40', '13.22 00',
     'Z,$IND'),
    ('023714.00', '14.22 00',
     'Z,$MASK'),
    ('023714.40', '21.22 00',
     'Z,$X1                 the subject will make it nonzero'),
    ('023715.00', '24323.16 00',
     'EXIC,I62PSI         (ext) the instruction this block exists for'),
    ('023715.40', '23717.04 00',
     'BD,I6262              in-range label: bit 18 = 0 -> 023717.00'),
    # ---- DIR IX, rule (a) ------------------------------------------
    ('023716.00', '1310.00 80',
     'I6261 SIC,SEN        (ext) "-INT WHEN EXIC TO"'),
    ('023716.40', '1304.10 00',
     'B,SERS                (ext) "-A DIR IX INSTR."'),
    # ---- DIR IX, rules (b) and (c) ---------------------------------
    ('023717.00', '21.02 10',
     'I6262 LX,$X1,$X1     reload the index the subject wrote'),
    ('023717.40', '1310.00 80',
     'SIC,SEN               (ext) "-DIR IX WAS SUBJ INST."'),
    ('023720.00', '1304.31 42',
     'BXVZ,SERS             (ext) branches when XVZ is ON; see header'),
    ('023720.40', '24324.43 01',
     'LVI,$X1,I62SUB+.32  (ext) BIT 18 SET -> 024324.40, the ABSOLUTE'
     ' idiom'),
    ('023721.00', '24323.02 90',
     'KV,$X1,I62PSI       (ext) J = $X1 here, $X2 in the other classes'),
    ('023721.40', '1310.00 80',
     'SIC,SEN               (ext) "-PSEUDO IC NOT STEPPED .32 CORRECTLY"'),
    ('023722.00', '1304.32 C0',
     'BZXE,SERS             (ext) branches when XE is OFF'
     '; "-WHEN SUBJ INST WAS DIR IX."'),
    # ---- IMMED IX class: the setup ---------------------------------
    ('023722.40', '23730.43 01',
     'LVI,$X1,I6263         "-IMMED IX."; BIT 18 SET -> 023730.40'),
    ('023723.00', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext)'),
    ('023723.40', '24324.03 01',
     'LVI,$X1,I62SUB      (ext)'),
    ('023724.00', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext)'),
    ('023724.40', '24332.02 10',
     'LX,$X1,I62EXI       (ext) the IMMED IX subject'),
    ('023725.00', '24324.03 10',
     'SX,$X1,I62SUB       (ext)'),
    ('023725.40', '13.22 00',
     'Z,$IND'),
    ('023726.00', '14.22 00',
     'Z,$MASK'),
    ('023726.40', '21.22 00',
     'Z,$X1'),
    ('023727.00', '24323.04 30',
     'LV,$X2,I62PSI       (ext) the RELATIVE idiom: pseudo-IC BEFORE'),
    ('023727.40', '24323.16 00',
     'EXIC,I62PSI         (ext)'),
    ('023730.00', '23731.44 00',
     'BD,I6264              in-range label: BIT 18 SET -> 023731.40'),
    # ---- IMMED IX, rule (a) ----------------------------------------
    ('023730.40', '1310.00 80',
     'I6263 SIC,SEN        (ext) "-INT WHEN EXIC TO"'),
    ('023731.00', '1304.10 00',
     'B,SERS                (ext) "-AN IMMED IX INST."'),
    # ---- IMMED IX, rules (b) and (c) -------------------------------
    ('023731.40', '21.02 10',
     'I6264 LX,$X1,$X1'),
    ('023732.00', '1310.00 80',
     'SIC,SEN               (ext) "-SUBJ INST WAS IMMED IX," -- COMMA,'
     ' settled by the descender'),
    ('023732.40', '1304.31 42',
     'BXVZ,SERS             (ext) "-AND WAS NOT EXECUTED."'),
    ('023733.00', '0.45 05',
     'V+I,$X2,0.32          BIT 18 SET: the immediate IS 32 bits'),
    ('023733.40', '24323.04 90',
     'KV,$X2,I62PSI       (ext) the pseudo-IC after'),
    ('023734.00', '1310.00 80',
     'SIC,SEN               (ext) "-PSEUDO IC NOT STEPPED .32 CORRECTLY"'),
    ('023734.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-WHEN SUBJ INST WAS IMMED IX."'),
    # ---- MISC class: the setup; its error entries are on PDF p.101 --
    ('023735.00', '23742.43 01',
     'LVI,$X1,I6265       (ext) "-MISC" (no period, sic); BIT 18 SET'),
    ('023735.40', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext)'),
    ('023736.00', '24324.03 01',
     'LVI,$X1,I62SUB      (ext)'),
    ('023736.40', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext)'),
    ('023737.00', '24331.02 10',
     'LX,$X1,I62EXM       (ext) the MISC subject, itself "Z,$X1"'),
    ('023737.40', '24324.03 10',
     'SX,$X1,I62SUB       (ext)'),
    # ---- PDF p.100 prints these five rows and nothing else ---------
    ('023740.00', '13.22 00',
     'Z,$IND                  PDF p.100 begins'),
    ('023740.40', '14.22 00',
     'Z,$MASK                 no Z,$X1: the MISC subject IS Z,$X1'),
    ('023741.00', '24323.04 30',
     'LV,$X2,I62PSI       (ext)'),
    ('023741.40', '24323.16 00',
     'EXIC,I62PSI         (ext)'),
    ('023742.00', '23743.44 00',
     'BD,I6266            (ext) BIT 18 SET -> 023743.40, PDF p.101'),

    # ================================================================
    # TAIL -- PDF p.102.  023742.40-023767.40 in between is
    # verify_ax5b_162_exic_listing.py.
    # ================================================================
    ('023770.00', '1310.00 80',
     'I6269 SIC,SEN        (ext) "-INT WHEN EXIC TO A"'),
    ('023770.40', '1304.10 00',
     'B,SERS                (ext) "-FULL WD VFL INSTR."'),
    ('023771.00', '11.02 10',
     'I6270 LX,$X1,$R      $R = word 11 octal; the VFL subject wrote it'),
    ('023771.40', '1310.00 80',
     'SIC,SEN               (ext) "-SUBJ INST WAS FLT PT" -- STALE, this'
     ' is the VFL class'),
    ('023772.00', '1304.31 42',
     'BXVZ,SERS             (ext) "-AND WAS NOT EXECUTED."'),
    ('023772.40', '1.05 05',
     'V+I,$X2,1.0           ONE FULL WORD: the subject is full-length'),
    ('023773.00', '24323.04 90',
     'KV,$X2,I62PSI       (ext)'),
    ('023773.40', '1310.00 80',
     'SIC,SEN               (ext) "-PSEUDO IC NOT STEPPED 1.0 CORRECTLY"'),
    ('023774.00', '1304.32 C0',
     'BZXE,SERS             (ext) "-WHEN SUBJ INST WAS VFL FULL WD."'),
    # ---- routine 1262's TEST 2B exit -------------------------------
    ('023774.40', '23775.50 00',
     'B,$+1.0               computed target 023775.40; BIT 18 SET'),
    ('023775.00', '23705.04 00',
     'BD,I6260              back to TEST 2B entry; anchor, not evidence'),
    ('023775.40', '1311.40 80',
     'SIC,SEN0+.32        (ext) 24-bit BIT address: offset 40 = 32 bits'),
    ('023776.00', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP."'),
    ('023776.40', '23777.04 00',
     'BD,$+.32              self-relative: +32 bits -> 023777.00'),
    # ---- the continuity bridge -------------------------------------
    ('023777.00', '24171.32 10',
     'LX,$X13,IC262       (ext) "-UPDATE CONTINUITY CHECK."; 18-bit'),
    ('023777.40', '24527.32 B0',
     'V+,$X13,BIT5        (ext) TEST 2B done = bit 5, NOT bit 8'),
    ('024000.00', '24171.33 10',
     'SX,$X13,IC262       (ext) 18-bit; cf the LX two rows up, 24171.32'),
]

# TIER 1 (real witnesses): I6261, I6262, I6263, I6264 -- defined in
# range, printed in p.99's own name field, each reached by an operand
# decoded in the docstring.
# TIER 2 (near-trivial): I6270 -- defined in range and printed in
# p.102's name field, but nothing HERE references it.
# TIER 3 (anchors, not evidence): I6260, I6269 -- each the first label
# after an SLC.
SYMBOLS = {
    'I6261': '023716.00', 'I6262': '023717.00',
    'I6263': '023730.40', 'I6264': '023731.40',
    'I6270': '023771.00',
    'I6260': '023705.00', 'I6269': '023770.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 2B ends '))
