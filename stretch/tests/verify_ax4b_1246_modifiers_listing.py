#!/usr/bin/env python3
"""verify_ax4b_1246_modifiers_listing.py -- jb_ax4b "I-BOX 4", routine
1246 ("TEST TRANSMIT AND SWAP"), sub-tests TEST 2A and TEST 2B,
checked against the machine code the listing prints beside each source
line.  119 printed rows, contiguous, plus 6 symbol assertions:

  PDF p.109  007272.00-007314.00  TEST 2A, I4620, forward   35 rows
  PDF p.110  007314.40-007343.00  TEST 2A, I4621, backward  44 rows
  PDF p.111  007343.40-007372.00  TEST 2B, I4623/I4624      40 rows

WHERE THIS STARTS AND STOPS.  The range is CONTIGUOUS: p.109's last
printed row is 007314.00 and p.110's first is 007314.40; p.110's last
is 007343.00 and p.111's first is 007343.40.  One SLC covers all
three pages.  The row BEFORE 007272.00 is 007271.40, the last row of
TEST 1I on PDF p.108, not transcribed anywhere yet; the row AFTER
007372.00 is 007372.40, the first row of TEST 2C, which IS
transcribed, in verify_ax4b_1246_transmit_swap_listing.py.  So this
file and its sibling now abut exactly.

PREMISE CHECKED BEFORE A LINE WAS WRITTEN, because the brief's premise
had twice been wrong this session.  `grep` over all 172 verify_*.py
files for any asserted row in 0072xx or 0073xx found NONE; the only
hits on these addresses anywhere in the repo are PROSE in
verify_ax4b_1246_transmit_swap_listing.py, which says in its own
header that "TESTs 2A and 2B occupy PDF pp.109-111, 007272.00 through
007372.00 ... left for a later pass" and prints the two headings it
had read first-hand.  This is that later pass.  Both of that file's
first-hand readings are confirmed here: the label at 007272.00 is
I4620 and the heading is "-TEST FORWARD-BACKWARD MODIFIER,"; the
label on p.111 is I4623 and its heading is "-TEST DIRECT-INNEDIATE
MODIFIER.".  Its item 5 -- that the 007372.00 endpoint was ARITHMETIC,
not read -- is now a MEASUREMENT: 007372.00 is the printed location of
p.111's last row, "SX,$X13,IC246".

CITED BY PDF PAGE, AND ONLY BY PDF PAGE.  jb_ax4b's LISTING sheets
carry no printed folio anywhere.  Reference Manual 22-6530-2 is cited
by PRINTED page; PDF page = printed page + 3 (printed p.30 is PDF
p.33, footer "30  IBM 7030", rendered and read for this file).
C22-6531's offset is +1.

=====================================================================
THE HEADINGS, PDF pp.109 and 111, read first-hand at 600 dpi,
VERBATIM, with the octal location of the row they sit beside:

  PDF p.109:
             -TEST 2. CHECK MODIFIER BITS.        (no location)
             -TEST 2A.                            (no location)
    I4620    -TEST FORWARD-BACKWARD MODIFIER,     007272.00
             -START WITH FOWARD OPERATION.        007272.40
  PDF p.110:
    I4621    -DO A BACKWARD OPERATION.            007314.40
  PDF p.111:
             -TEST 2B.                            (no location)
    I4623    -TEST DIRECT-INNEDIATE MODIFIER.     007343.40

TEST 2A's heading ends in a COMMA and TEST 2B's in a PERIOD; both are
as printed.

EVERY ERROR MESSAGE IN RANGE, VERBATIM, with the octal location of the
SIC that reports it.  Each is a two-half-word pair, "SIC,SEN" then
"B,SERS", and the printed comment sits beside the pair.

  PDF p.109, TEST 2A, the FORWARD half:
    007301.40  -RECEIVING ADDRESS GOING BACKWARD
               -ON A FORWARD OPERATION.
    007304.00  -RECEIVING LOCATION DOES NOT GET
               -FIRST WORD FROM SENDING LOCN.
    007306.40  -SENDING ADDRESS GOING BACKWARD
               -ON A FORWARD OPERATION.
    007310.40  -SENDING ADDRESS NOT STEPPED ON
               -A FORWARD OPERATION.
    007313.40  -NO WORD GOES TO SECOND RECEIVING
               -LOCATION ON A FORWARD OPERATION.

  PDF p.110, TEST 2A, the BACKWARD half:
    007324.00  -RECEIVING ADDRESS GOING FORWARD
               -ON A BACKWARD OPERATION.
    007326.40  -RECEIVING LOCATION DOES NOT GET
               -FIRST WORD FROM SENDING LOCN.
    007332.00  -SENDING ADDRESS GOING FORWARD ON
               -A BACKWARD OPERATION.
    007334.40  -SENDING ADDRESS NOT STEPPED ON
               -A BACKWARD OPERATION.
    007336.40  -NO WORD GOES TO SECOND RECEIVING
               -LOCATION ON A BACKWARD OPERATION.

  PDF p.111, TEST 2B:
    007351.00  -TRANSMIT IMMEDIATE USES
               -A DIRECT COUNT.
    007354.00  -RECEIVING LOCATION DOES NOT GET
               -FIRST WORD FROM SENDING LOCN.
    007362.40  -TRANSMIT DIRECT USES
               -AN IMMEDIATE COUNT.
    007365.40  -RECEIVING LOCATION DOES NOT GET
               -FIRST WORD FROM SENDING LOCN.

  Note the line break moves between the two "SENDING ADDRESS GOING
  ..." messages: p.109 breaks after "BACKWARD", p.110 after "FORWARD
  ON".  Quoted as printed.  Note also that "-TRANSMIT IMMEDIATE USES"
  and "-TRANSMIT DIRECT USES" are the page's own short first lines;
  they are not truncations made here.

Non-error printed comments in range, also verbatim: "-TEST 2. CHECK
MODIFIER BITS.", "-TEST 2A.", "-TEST FORWARD-BACKWARD MODIFIER,",
"-START WITH FOWARD OPERATION.", "-DO A BACKWARD OPERATION.", "-OK",
"-TO SSIP.", "-UPDATE CONTINUITY.", "-TEST 2B.", "-TEST
DIRECT-INNEDIATE MODIFIER."

BRANCH POLARITY, AND THE DECK SAYS IT ITSELF.  B<IND> branches when
the indicator is ON, BZ<IND> when it is OFF; the BRANCH is the OK path
and the FALL-THROUGH is the error pair, whose comment names the
ANOMALY, never the requirement.  PDF p.110, 007336.00, prints the
comment "-OK" beside "BZXVZ,I4622".  That is the deck labelling the
branch as the good path in its own hand -- first-hand evidence for the
rule rather than inherited convention, and the only "-OK" in either
1246 file.  Every one of the fourteen error pairs above is reached by
falling through a branch, and every branch target is either $+2.0
(over the pair) or a label past it.

=====================================================================
BITS 55 AND 56: WHAT THIS BLOCK ADDS, AND WHAT IT DOES NOT.

Reference Manual 22-6530-2, printed p.30 (PDF p.33, footer
"30  IBM 7030"), "Data Transmission", rendered at 400 dpi and read
first-hand for this file:

    "Bits 55-57 of the data transmission instructions are used as
     modifiers.  The choice between unidirectional and bidirectional
     transmission is specified by modifier bit 57.  A zero specifies
     unidirectional transmission; a one specifies bidirectional
     transmission.  The choice between an immediate or a direct count
     is specified by modifier bit 56.  A zero specifies a direct
     count; a one specifies an immediate count.  The choice between
     forward and backward transmission is specified by modifier bit
     55.  A zero specifies forward transmission; a one specifies
     backward transmission."

    "In direct count operations, the field J, bits 51-54, specifies an
     index register.  The count field, bits 28-45, of the index word
     in this register is used as a full word count."

    "In immediate count operations, the full word count is specified
     by instruction bits 51-54.  A zero count field indicates the
     maximum count of 16 full words."

    "In forward transmission, the sending and receiving addresses of
     each successive word transmitted are obtained by incrementing the
     previous addresses by one. ...  In backward transmission, the
     sending and receiving addresses of each successive word
     transmitted are obtained by decrementing the previous addresses
     by one."

BIT 55 IS NOW WITNESSED SET.  It was not before: the sibling file
records bits 55 and 56 at ZERO only in its range, and a grep over all
172 verify_*.py files finds no other transcribed row that could carry
bit 55 at one -- the only mnemonics that can are TB, TBI, SWAPB and
SWAPBI, and before this file all four were CARD-ONLY, named in
opcodes.TRANSMIT_CODES and in prose and in no asserted row anywhere.
The witness is a MATCHED PAIR across two pages, both re-read at 600
dpi for this file:

    007277.00  T,$X2,I46D5,I46D2   7430.00 80 007425.04 20  (p.109)
    007321.40  TB,$X2,I46D5,I46D2  7430.00 80 007425.05 20  (p.110)

Same A1, same A2, same J, same hex byte.  ONE OCTAL DIGIT differs,
04 -> 05, and that is IBM bit 55.  Note where the TB row SITS: at
007321.40, an ODD half-word, so the repository's first TB is also a
full-word instruction straddling a word boundary and exercises
strap_asm.Image.deposit_word_instr as well as bit 55 -- the same
property the sibling annotates on its own 006762.40 row.  The octal
pair spans bits 50-55, so
bit 55 is its BOTTOM bit; 04 = 000100 and 05 = 000101, and J (bits
51-54) is 0010 = 2 in both.  This is the structural twin of the
sibling's T/SWAP pair for bit 57, but it moves the OCTAL column where
that one moves the HEX column.  Between the two files all three of the
banner's modifier bits are now pinned by a matched pair, each from the
deck's own printing with every other field held constant.

BIT 56 IS ALSO WITNESSED SET HERE -- and it is NOT a first, and these
two rows are NOT a matched pair:

    007346.40  TI,1,I46D4,I46D1    7427.00 80 007424.02 A0  (p.111)
    007360.00  T,$X2,I46D4,I46D1   7427.00 80 007424.04 20  (p.111)

Their J fields differ as well (1 against 2), so BOTH printed columns
move and neither bit is isolated.  Said out loud rather than glossed.
Bit 56 SET was already witnessed in this repository by every existing
TI row -- 021377.40 and 021400.40 in verify_ax5b_16087_listing.py,
022365.40 in verify_ax5b_160105_listing.py, 022742.00 and its
repetitions in verify_ax5b_160s1_listing.py -- and all of them print
hex A0, the same byte.  This TI is the first in the ax4b deck and
corroboration for the repo, not a first.

FULL DECOMPOSITION of the TB word against pocket card X22-6533's
"TRANSMIT OPERATIONS" diagram, the one opcodes.TRANSMIT_CODES carries,
and against the Reference Manual's own format figure on printed p.30:

    |   ADDRESS   |1000| I |   ADDRESS   | J |FD|BI|10| I |
    0            18  24   28  32          51  55    58 60 63

  bits 0-23   = 007430.00 as a BIT address       -> "7430.00"
  bits 24-27  = 1000, the literal shared with SIC and BRANCH ON BIT
  bits 28-31  = I1 = 0                           -> hex "80"
  bits 32-50  = 007425.00 as a HALF-WORD address -> "007425" + bit 50
  bits 51-54  = J = 2, index register 2          )
  bit  55     = 1, BACKWARD  (0 = forward)       ) -> octal pair "05"
  bit  56     = 0, DIRECT count                  )
  bit  57     = 0, TRANSMIT (1 = swap)           )
  bits 58-59  = 10, the format literal           ) -> hex "20"
  bits 60-63  = I2 = 0                           )

THE COUNTS ARE BIT44 AND BIT45, AND THE DECK USES THE DIFFERENCE.  In
TEST 2A both halves do "LX,$X2,BIT44" before the T/TB: BIT44 is the
common constant at 013130.00 with bit 44 set, bit 44 is the
second-lowest bit of the 28-45 count field, so X2's count is TWO and
each transmission moves two words -- which is why the sub-test can ask
what happened to a SECOND receiving location.  TEST 2B is sharper
still.  Its immediate half loads BIT44 (a DIRECT count of 2) into $X1
and then issues "TI,1,...", whose IMMEDIATE count is 1; only one word
may move, and the error if two do is "-TRANSMIT IMMEDIATE USES A
DIRECT COUNT."  Its direct half loads BIT45 (a direct count of 1) into
$X2 and issues "T,$X2,...", whose J field is 2; a machine that read
the count immediately would move TWO, and the error is "-TRANSMIT
DIRECT USES AN IMMEDIATE COUNT."  The same four bits mean two
different things under bit 56, and the sub-test is built on exactly
that.  BIT44 at 013130.00 sits one word below BIT45 at 013131.00,
which the sibling already SYNs.  (A DIFFERENT BIT44 exists in this
repo at 017402.00, a local constant of the I-Box 2 deck; it is not
this one and is not cross-cited.)

AND THE DECK SPELLS THE J FIELD BOTH WAYS WITHIN THREE PAGES.
"T,$X2,..." and "TB,$X2,..." on pp.109-110, but "TI,1,..." on p.111.
That is not inconsistency: for T and TB the count is DIRECT, so bits
51-54 name an index register; for TI it is IMMEDIATE, so bits 51-54
ARE the count.  The printed octal pairs confirm it -- 04 -> 2 for the
T/TB rows, 02 -> 1 for the TI row.  This is first-hand evidence that
the sibling file's "$X1" -> "1" substitution is what IBM's assembler
did with the field, not a convention this project invented.

=====================================================================
BIT-18 SELF-CHECKS.  The listing prints each half-word as bits 0-17 in
six octal digits, ".", bits 18-23 in two octal digits, then bits 24-31
in two hex digits.  BIT 18 IS THE TOP BIT OF THE OCTAL PAIR and
selects the half-word of a 19-bit branch address.  Every row below
whose operand is a label or a self-relative was decoded that way and
read back against the page's own label column.

  PDF p.109, TEST 2A forward -- six rows with BIT 18 SET:
    007301.00  BRZ,$+2.0     -> 7303.34 C2.  34 = 011100, bit 18 = 0
               -> 007303.00, and 007301.00 + 2 words = 007303.00.
    007302.40  B,I4621       -> 7314.50 00.  50 = 101000, BIT 18 = 1
               -> 007314.40, where PDF p.110 prints the label I4621.
               Three more rows print the identical word: 007305.00,
               007307.40, 007311.40.
    007303.40  BZXCZ,$+2.0   -> 7305.70 40.  70 = 111000, BIT 18 = 1
               -> 007305.40, and 007303.40 + 2 words = 007305.40.
    007306.00  BXVZ,$+2.0    -> 7310.31 42.  31 = 011001, bit 18 = 0
               -> 007310.00 (the even-half start keeps the +2 words
               in the even half).
    007310.00  BXCZ,$+2.0    -> 7312.30 42.  30 = 011000, bit 18 = 0
               -> 007312.00.
    007313.00  BZXVZ,I4621   -> 7314.71 40.  71 = 111001, BIT 18 = 1
               -> 007314.40 = I4621.  The page's own label column on
               p.110 is the read-back.

  PDF p.110, TEST 2A backward -- eight rows with BIT 18 SET:
    007323.40  BRZ,$+2.0     -> 7325.74 C2.  74 = 111100, BIT 18 = 1
               -> 007325.40, and 007323.40 + 2 words = 007325.40.
               Contrast 007301.00's BRZ,$+2.0 above: same mnemonic,
               same operand, bit 18 opposite, because the ODD-half
               start carries the +2 words into an odd half.
    007325.00  B,I4622       -> 7337.50 00.  BIT 18 = 1 -> 007337.40,
               where p.110 prints the label I4622 four rows later.
               Also at 007327.40, 007333.00, 007335.40.
    007326.00  BZXCZ,$+2.0   -> 7330.30 40.  30 = 011000, bit 18 = 0
               -> 007330.00.  Mirror of 007303.40's BZXCZ.
    007331.40  BXVZ,$+2.0    -> 7333.71 42.  71 = 111001, BIT 18 = 1
               -> 007333.40.
    007334.00  BXCZ,$+2.0    -> 7336.30 42.  bit 18 = 0 -> 007336.00.
    007336.00  BZXVZ,I4622   -> 7337.71 40.  BIT 18 = 1 -> 007337.40
               = I4622.  This is the "-OK" row.
    007337.40  B,$+1.0       -> 7340.50 00.  BIT 18 = 1 -> 007340.40,
               and 007337.40 + 1 word = 007340.40.
    007340.00  BD,I4620      -> 7272.04 00.  04 = 000100, bit 18 = 0
               -> 007272.00, where p.109 prints the label I4620.
    007341.40  BD,$+.32      -> 7342.04 00.  bit 18 = 0 -> 007342.00,
               and 007341.40 + 32 bits = 007342.00.

  PDF p.111, TEST 2B -- five rows with BIT 18 SET:
    007350.40  BRZ,$+2.0     -> 7352.74 C2.  74 = 111100, BIT 18 = 1
               -> 007352.40.
    007352.00  B,I4624       -> 7355.10 00.  10 = 001000, bit 18 = 0
               -> 007355.00, where p.111 prints the label I4624.
    007353.40  BZRZ,I4624    -> 7355.34 C0.  34 = 011100, bit 18 = 0
               -> 007355.00 = I4624.
    007362.00  BRZ,$+2.0     -> 7364.34 C2.  bit 18 = 0 -> 007364.00.
    007363.40  B,I4625       -> 7366.50 00.  BIT 18 = 1 -> 007366.40,
               where p.111 prints the label I4625.
    007365.00  BZRZ,I4625    -> 7366.74 C0.  BIT 18 = 1 -> 007366.40
               = I4625.
    007366.40  B,$+1.0       -> 7367.50 00.  BIT 18 = 1 -> 007367.40.
    007367.00  BD,I4623      -> 7343.44 00.  44 = 100100, BIT 18 = 1
               -> 007343.40, where p.111 prints the label I4623.
    007370.40  BD,$+.32      -> 7371.04 00.  bit 18 = 0 -> 007371.00.

  THE NON-BRANCH LABEL ROWS, because the brief asks for EVERY
  label-valued operand and the list above is branches only.  A
  DirIndex row's 19-bit address field is the same field with the same
  bit 18, and THIRTY-FIVE rows here put an internally-defined label in
  it (counted row by row off the three tables below, not estimated):
      "Z,I46D1"/"Z,I46D2"/"Z,I46D3" (TEN rows), "LX,$X1,I46XW1",
      "LX,$X2,I46XW2", "LX,$X3,I46XW3", "SX,$X1,I46D4",
      "SX,$X2,I46D5", "SX,$X3,I46D6", "LX,$X1,I46D1"/"I46D2"/"I46D3",
      "SX,$X1,I46D5", "LX,$X13,IC246", "SX,$X13,IC246".
  In EVERY one of them bit 18 is ZERO: the printed pairs are 22, 02,
  03, 04, 05, 06, 07, 32 and 33, all less than octal 40, so the pair's
  top bit -- which IS bit 18 -- is zero in each.  The reason is
  arithmetic, not luck: every label they name is a full WORD in the
  routine's own constant block (007422.00-007434.00, all .00
  addresses), so the half-word select cannot be anything else.  Bit 18
  is witnessed at ONE only by the NINETEEN branch rows listed above --
  nineteen ROWS in thirteen listed ENTRIES, because "B,I4621" folds
  four rows into one entry and "B,I4622" folds four more; the
  per-page counts (six, eight, five) are rows.  The DirIndex rows
  witness bit 18 at zero.

  TWO ROW SHAPES HERE ARE NOT HALF-WORD SELECTS AT ALL, and the
  sibling file makes the same two points:

    1. SIC's operand is a 24-bit BIT address in bits 0-23 (Reference
       Manual printed p.41), so its octal pair is a bit OFFSET inside
       the word.  "SIC,SEN" at fourteen locations prints 1310.00 80 --
       the 00 is bit 0 of word 001310.  "SIC,SENO+.32" at 007340.40
       and 007367.40 prints 1311.40 80: the 40 is BIT 32 of word
       001311, not bit 18 and a half-word select.

    2. T, TB and TI carry BOTH kinds in ONE instruction word.  The
       FIRST group holds A1, a 24-bit BIT address, so "7430.00" + pair
       "00" is word 007430 bit 0 and its octal pair is a bit offset --
       the SIC caveat again.  The SECOND group holds A2, a 19-bit
       HALF-WORD address at bits 32-50, and there the half-word select
       is BIT 50, the TOP bit of the SECOND group's octal pair.  So
       the bit-18 rule applies to neither group of a transmit row: the
       first has no half-word select, and the second's lives twelve
       bits away.  All four transmit rows here print "007425." or
       "007424." with six digits in the second group, which is the
       19-bit address's 18-bit word part; the nineteenth bit is the
       top of the "04"/"05"/"02" that follows.

  AND THE SIBLING'S MEASURED NULL SURVIVES, RE-MEASURED.  All four
  transmit rows print 02, 04 or 05 for bits 50-55, so bit 50 = 0 in
  every one of them.  The reason is arithmetic, not luck: every A2 in
  this block is I46D1 (007424.00) or I46D2 (007425.00), both
  word-aligned constants, so their half-word select is zero, and this
  block contains no transmit whose A2 is an odd half-word.  Bit 50 is
  therefore still witnessed at ZERO only, and the sibling's A2-mask
  null is confirmed rather than broken.  The injection table below
  records the re-measurement.

=====================================================================
WITNESS TIERING.  EVERY SYN IS AN INPUT, NOT A WITNESS.

  SYN'd (address supplied to the assembler from the very rows that
  print it -- these rows check opcode and modifier bits only):
      SEN 001310.00, SENO 001311.00, SERS 001304.00, SSW 001301.00,
      I00O 013035.00, BIT9 013065.00, BIT10 013066.00,
      BIT44 013130.00, BIT45 013131.00.
  BIT9, BIT10 and BIT11 are three CONSECUTIVE words and they are this
  routine's continuity bits for TEST 2A, TEST 2B and TEST 2C in that
  order -- BIT11 at 013067.00 is the one the sibling file already SYNs
  for TEST 2C.  The numbering corroborates the sub-test ordering
  independently of the headings.  That is corroboration; it does not
  turn an input into a witness.

  INPUT, NOT ASSERTED AT ALL -- the routine's constant block
  (007422.00-007434.00, PDF pp.112-113).  Its ten symbols are named by
  seventy-odd rows here, so giving them by SYN would make every
  transmit operand an input.  Instead the .strap re-lays the block from
  its own SLC as unasserted source, and the location counter computes
  IC246, ICK246, I46D1-I46D6 and I46XW1-I46XW3.  A wrong SLC or a
  wrong ordering would break the printed A1/A2 fields of the four
  transmit rows, so those symbols ARE checked here -- by the transmit
  rows, not by rows of their own.  NONE of the block's own printed rows
  is asserted below; verify_ax4b_1246_transmit_swap_listing.py asserts
  them and this file does not duplicate it.

  ANCHOR, not a witness -- I4620 at 007272.00 is the first label after
  this block's SLC, so asserting it checks this transcription against
  the number this transcription handed the SLC.  It is asserted below
  because a wrong one would silently mis-place all 119 rows, not
  because it is evidence.  It is ALSO named by "BD,I4620" at 007340.00,
  sixty-six rows later, which reaches it through the symbol table -- so
  the anchor is not purely circular, the same caveat the sibling makes
  about IC246.

  GENUINE WITNESSES -- defined inside the transcribed range at
  addresses the location counter computes, and named by rows whose
  printed address field therefore checks placement:
      I4621 007314.40  (named by "B,I4621" at 007302.40, 007305.00,
                        007307.40 and 007311.40, and by "BZXVZ,I4621"
                        at 007313.00 -- five rows, all with bit 18 SET)
      I4622 007337.40  (named by "B,I4622" at 007325.00, 007327.40,
                        007333.00 and 007335.40, and by "BZXVZ,I4622"
                        at 007336.00 -- five rows, all with bit 18 SET)
      I4623 007343.40  (named by "BD,I4623" at 007367.00, bit 18 SET)
      I4624 007355.00  (named by "B,I4624" at 007352.00 and
                        "BZRZ,I4624" at 007353.40, both bit 18 = 0)
      I4625 007366.40  (named by "B,I4625" at 007363.40 and
                        "BZRZ,I4625" at 007365.00, both bit 18 SET)
  I4624 is the only one of the five whose witnesses all have bit 18
  zero, which is why it and I4621 are worth naming separately: between
  them the label-valued branches exercise the half-word select in both
  states against a label the location counter computed.

=====================================================================
FIRSTS FOR THIS REPOSITORY, and every claim was knocked at with grep
over all 172 verify_*.py files before it was written.  A previous
agent on this deck claimed four firsts and grep eliminated all four.

  TB -- A GENUINE FIRST, one row, 007321.40.  Before this file `grep`
  found "TB" in exactly one verify_*.py, the sibling
  verify_ax4b_1246_transmit_swap_listing.py, and there only in PROSE
  ("TB, TBI, SWAPI, SWAPB, SWAPBI -- remain card-only").  No asserted
  row anywhere.  opcodes.TRANSMIT_CODES said the same in its own
  comment.  With this file FOUR of the eight transmit mnemonics have
  listing rows -- T, TI, SWAP from before, plus TB -- and four remain
  card-only: TBI, SWAPI, SWAPB, SWAPBI.

  AND THAT IS THE ONLY FIRST.  Knocked out by grep, every one:
    TI    -- verify_ax5b_16087_listing.py 021377.40 and 021400.40,
             verify_ax5b_160105_listing.py 022365.40,
             verify_ax5b_160s1_listing.py 022742.00 and repetitions.
             First in the ax4b DECK, not in the repo.
    BXVZ  -- verify_ax5b_1274_truncation_listing.py,
             verify_ax5b_160_test7_compare_listing.py,
             verify_ax5b_160_test8c_listing.py and others.
    BZXVZ -- verify_ax5b_1258_test1_listing.py,
             verify_ax5b_1258_test2_listing.py,
             verify_ax5b_1274_truncation_listing.py and others.
    BXCZ  -- verify_ibox1_listing.py, verify_ibox1_bind_listing.py,
             verify_ibox2_kv_kvi_listing.py,
             verify_ibox2_load_index_listing.py.
    BZXCZ -- verify_ibox1_listing.py, verify_ibox1_bind_listing.py,
             verify_ax5b_162_test1b_listing.py.
             An earlier draft of this paragraph called all four of
             these firsts; the grep says otherwise and the grep wins.
    BZRZ, BRZ, B, BD, SIC, SR, LX, SX, Z, V+, L(BU) -- between two and
             twenty-seven other files each, including the sibling.
  BIT 55 SET is a first (see above) and it rides on TB; BIT 56 SET is
  NOT, and the TI rows that already witness it are named above.

=====================================================================
PROVEN DISCRIMINATING.  Observed failure sets, never predicted.  Every
injection was made with __pycache__ removed on BOTH sides of the run
-- stale bytecode has replayed a previous injection's answer in this
repo before -- and opcodes.py and strap_asm.py were restored
afterwards from byte-for-byte copies taken before the first one; both
md5s matched the originals and `git diff` was empty at the end.  The
first four are aimed at BITS 55 AND 56, which is what this block is
for; the fifth moves a third printed column in a third opcode family;
the sixth separates bit 55 from bit 57 on the TB row.

(A SEVENTH ATTEMPT IS RECORDED AS A PROCESS NOTE, because it is the
exact failure mode the brief warns about.  The first edit of [1] used
a sed pattern whose spacing did not match opcodes.py, so nothing was
patched -- and the run then printed "ALL TESTS PASSED", which would
have read as a NON-discriminating result had the patched file not been
re-read before believing it.  Every injection below was confirmed
APPLIED by printing the patched lines before the run.)

  [1] opcodes.TRANSMIT_CODES["TB"] (1,0,0) -> (0,0,0)   -- bit 55
      cleared, i.e. TB encoded as plain T
      007321.40  TB -> "007430.00 80 007425.04 20"        (1 row)
      OCTAL PAIR ONLY, 05 -> 04, hex byte unchanged at 20.  And it
      makes the TB row print EXACTLY what the p.109 T row prints.
      This is the matched pair proving itself: the only thing
      separating forward from backward in this deck is that digit.

  [2] opcodes.TRANSMIT_CODES["T"] (0,0,0) -> (1,0,0)    -- bit 55 set,
      the other way
      007277.00  T  -> "007430.00 80 007425.05 20"        (2 rows)
      007360.00  T  -> "007427.00 80 007424.05 20"
      OCTAL PAIR ONLY, 04 -> 05, two rows on two different pages, and
      the p.109 row becomes an exact copy of the p.110 TB row.  The
      pair proving itself from the other side.

  [3] opcodes.TRANSMIT_CODES["TI"] (0,1,0) -> (0,0,0)   -- bit 56
      cleared, i.e. TI encoded as plain T
      007346.40  TI -> "007427.00 80 007424.02 20"        (1 row)
      HEX BYTE ONLY, A0 -> 20, octal pair unchanged at 02.  Bit 56 is
      the TOP bit of the hex byte, and this injection cannot touch the
      octal column at all -- the complement of [1] and [2].

  [4] opcodes.TRANSMIT_CODES["TI"] (0,1,0) -> (1,1,0)   -- bit 55 set
      on the IMMEDIATE row
      007346.40  TI -> "007427.00 80 007424.03 A0"        (1 row)
      OCTAL PAIR ONLY, 02 -> 03, hex unchanged at A0.  Bits 55 and 56
      live in different printed columns of the same half-word and this
      pair of injections separates them: [3] moves the hex and not the
      octal, [4] moves the octal and not the hex, on the same row.

  [5] opcodes.INDICATOR_BITS["XCZ"] 48 -> 49            -- the index
      Count Zero indicator renumbered onto XVLZ's bit
      007303.40  BZXCZ -> "007305.70 C0"                  (4 rows)
      007310.00  BXCZ  -> "007312.30 C2"
      007326.00  BZXCZ -> "007330.30 C0"
      007334.00  BXCZ  -> "007336.30 C2"
      HEX BYTE ONLY, 40 -> C0 and 42 -> C2, on four branch rows and
      nothing else -- a THIRD printed column and a third opcode
      family, well away from the transmit word.  The byte's TOP bit is
      what moves, not a low one, which is not what a first guess would
      have said and is why the number above is the observed one.  Note
      WHAT it collides with: bit 49 is INDICATOR_BITS["XVLZ"], so a
      block that checked only the indicator NAME could not tell XCZ
      from XVLZ; the listing can.

  [6] opcodes.TRANSMIT_CODES["TB"] (1,0,0) -> (1,0,1)   -- bit 57 set
      on the BACKWARD row, i.e. TB encoded as SWAPB
      007321.40  TB -> "007430.00 80 007425.05 60"        (1 row)
      HEX BYTE ONLY, 20 -> 60, octal pair unchanged at 05.  Paired
      with [1], which moves the octal and not the hex on the SAME ROW,
      this separates bit 55 from bit 57 on the single row that carries
      both -- the mirror of what [3] and [4] do for bits 56 and 55 on
      the TI row.

AND ONE INJECTION THIS BLOCK DOES *NOT* CATCH, measured and recorded
because a measured negative is worth more than an assumed positive.
The sibling file records the same null and the brief asked whether
this block breaks it.  IT DOES NOT:

  [7] strap_asm.enc_transmit's A2 field -- "(addr19, 19)" in its cat()
      changed to "(addr19 & 0x7FFFE, 19)", i.e. bit 50, the A2
      half-word select, forced to zero
      NO ROW CHANGES.  The run stays green.
      The reason is arithmetic: all four transmit rows in this block
      address word-aligned constants (I46D1 at 007424.00, I46D2 at
      007425.00), so bit 50 is already zero in every one of them.
      Only a transmit whose A2 is an ODD half-word could catch it, and
      routine 1246 contains none in either file's range -- eight
      transmit rows across the two files now, and all eight are
      word-aligned in A2.  The null is CONFIRMED, not broken, and it
      is now a stronger statement than the sibling could make alone.

=====================================================================
GLYPHS, and the two garbles adjudicated by MEASUREMENT.

  "INNEDIATE" (PDF p.111, 007343.40) -- DECK TYPO.
  On that one printed line the two N's of "INNEDIATE" measure 45 and
  44 px at 600 dpi and the M of "MODIFIER" seven glyphs later on the
  SAME LINE measures 49 px.  Width alone would be weak; the SHAPE is
  not.  Both N's carry a single diagonal between two full-height
  verticals, unbroken, with no stray ink where an M's second diagonal
  would be; the M carries two diagonals meeting in a V that stops
  mid-height.  Every stroke of all three glyphs is solid, none ragged.
  A damaged M does not grow a clean single diagonal.  The author typed
  N twice.

  "FOWARD" (PDF p.109, 007272.40) -- DECK TYPO, a DROPPED LETTER.
  Measured by PITCH rather than by shape, because a missing character
  has no glyph to inspect.  On the line ABOVE, "-TEST FORWARD-BACKWARD
  MODIFIER,", FORWARD occupies seven cells whose ink starts at x =
  4523, 4580, 4640, 4703, 4761, 4823, 4881 -- 402 px for 7 cells, 57.4
  px each.  On the line below, FOWARD occupies six cells at 4883,
  4938, 5003, 5061, 5123, 5186 -- 346 px for 6 cells, 57.7 px each.
  Identical pitch, one fewer cell, and no gap anywhere in the run.
  Scan damage degrades a glyph in place; it does not delete a
  character and close the 57-px hole behind it.  The R was never
  typed.  (The sibling file quotes "FOWARD" as the page's spelling but
  does not adjudicate it; this is the measurement.)

  LETTER I, NOT DIGIT 1 -- an INDEPENDENT second and third data point
  for the reading the sibling established on PDF p.99, offered because
  the question is under active investigation:
    "B,I4621"  PDF p.109, 007302.40, measured at 600 dpi.  Segments as
               B(43) ,(25) I(12) 4(48) 6(43) 2(40) 1(31).  LETTER I
               AND DIGIT 1 IN ONE PRINTED ROW -- one ink, one pass,
               no cross-page comparison.  The third glyph is a bare
               stroke 12 px wide; the seventh is a flagged 1 of 31 px.
               The sibling measured letter I at 9-13 px and digit 1 at
               31-34 px on p.99; this row lands at 12 and 31 on a
               DIFFERENT page of the same deck.
    "LX,$X1,I00O"  PDF p.111, 007344.40.  $X1's 1 measures 34 px and
               the leading I of I00O measures 11 px, again both in one
               row.  The trailing glyph measures 48 px against 41 and
               42 for the two zeros before it, so I00O reads
               letter-I / digit-0 / digit-0 / LETTER O, confirming the
               sibling's p.99 reading on a second page.
    "Z,I46D1"  PDF p.111, 007343.40.  Z(42) ,(24) I(12) 4(45) 6(41)
               D(45) 1(34).  A third same-row I-versus-1 pair.
    The absolute widths on these pages run 1-3 px under the sibling's
    p.99 figures across the board (its letter O 49-51 and digit 0
    42-45; here 48 and 41-42).  The CONTRAST carries the reading and
    it is 3-4x, not marginal.
    C22-6531 printed p.10 (PDF p.11, footer "10") is why a digit is
    not even admissible: "A symbol is any sequence of six or fewer
    alphabetic and numeric characters conforming to the following
    conditions:  1. It contains only alphameric characters.  2. Its
    first character is specifically alphabetic."

=====================================================================
SUBSTITUTIONS, three, all mechanical, none touching a bit; the .strap
header states them at length.  "L%BU@" -> "L(BU)" (nine rows); the J
field written "$X2" on pp.109-110 written "2" here, which the oracle
CHECKS because the printed octal pair carries it; and nothing else --
every one of the 119 printed rows carries machine code, so no SLC
steps over anything and no word is invented.

=====================================================================
NOT SETTLED, listed so that nothing above is taken for more than it
is.  No check below depends on any of these.

  1. The FIELD each of TEST 2A's five probes is reading -- value,
     count or refill -- is CONJECTURE from the index-word layout and
     from which of I46XW1/XW2/XW3 landed where.  What is NOT
     conjecture is the printed indicator mnemonic, the printed error
     text, the branch polarity and the encoding, and only the encoding
     is asserted.
  2. "SR,$X1,$X2" and "LX,$X2,$X2" assemble against word 18 (octal
     22), which is index register 2's own location.  The sibling file
     transcribes the same shape at 006754.40 and 006757.00 without
     explaining it either.  The rows are checked; the idiom is not
     understood.
  3. "-OK" at 007336.00 is read as the deck's own label for the
     branch-is-the-good-path rule.  That reading is an INFERENCE from
     one two-character comment, however natural; the encoding check
     does not rest on it.
  4. This block bears on none of the Reference Manual's SWAP-specific
     claims (printed p.43's Figure 11 suppression footnote, printed
     p.51's protected-address items), for the same reason the sibling
     gives: no SWAP appears here, no boundary register is set, and no
     DS/DF/IF indicator is branched on anywhere in the 119 rows.
  5. Bit 50 is witnessed at ZERO only, by all four transmit rows, for
     the arithmetic reason given above.  So is bit 57, at zero, by all
     four -- TEST 2C in the sibling file is where it moves.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_1246_modifiers.strap").read())

# ---------------------------------------------------------------------
# PDF p.109, 007272.00-007314.00.  TEST 2A, the FORWARD half, at I4620.
# ---------------------------------------------------------------------
TEST2A_FWD_ROWS = [
    ('007272.00', '7424.22 00',  'I4620 Z,I46D1     "-TEST FORWARD-BACKWARD MODIFIER,"'),
    ('007272.40', '7425.22 00',  'Z,I46D2           "-START WITH FOWARD OPERATION."'),
    ('007273.00', '7426.22 00',  'Z,I46D3'),
    ('007273.40', '7432.02 10',  'LX,$X1,I46XW1     the VALUE-field index word'),
    ('007274.00', '7433.04 10',  'LX,$X2,I46XW2     the COUNT-field index word'),
    ('007274.40', '7434.06 10',  'LX,$X3,I46XW3     the REFILL-field index word'),
    ('007275.00', '7427.03 10',  'SX,$X1,I46D4'),
    ('007275.40', '7430.05 10',  'SX,$X2,I46D5'),
    ('007276.00', '7431.07 10',  'SX,$X3,I46D6'),
    ('007276.40', '13130.04 10', 'LX,$X2,BIT44      (ext) direct count = 2 words'),
    ('007277.00', '7430.00 80 007425.04 20',
                                 'T,$X2,I46D5,I46D2   bit 55 = 0 FORWARD; pair with the TB below'),
    ('007300.00', '7424.00 80 000000.20 50',
                                 'L(BU),I46D1       read back the word BELOW the target'),
    ('007301.00', '7303.34 C2',  'BRZ,$+2.0         OK when Result Zero is ON'),
    ('007301.40', '1310.00 80',  'SIC,SEN           (ext) "-RECEIVING ADDRESS GOING BACKWARD"'),
    ('007302.00', '1304.10 00',  'B,SERS            (ext) "-ON A FORWARD OPERATION."'),
    ('007302.40', '7314.50 00',  'B,I4621           BIT 18 SET -> 007314.40'),
    ('007303.00', '7425.02 10',  'LX,$X1,I46D2'),
    ('007303.40', '7305.70 40',  'BZXCZ,$+2.0       BIT 18 SET -> 007305.40; OK when XCZ is OFF'),
    ('007304.00', '1310.00 80',  'SIC,SEN           (ext) "-RECEIVING LOCATION DOES NOT GET"'),
    ('007304.40', '1304.10 00',  'B,SERS            (ext) "-FIRST WORD FROM SENDING LOCN."'),
    ('007305.00', '7314.50 00',  'B,I4621           BIT 18 SET -> 007314.40'),
    ('007305.40', '7426.02 10',  'LX,$X1,I46D3'),
    ('007306.00', '7310.31 42',  'BXVZ,$+2.0        bit 18 = 0 -> 007310.00; OK when XVZ is ON'),
    ('007306.40', '1310.00 80',  'SIC,SEN           (ext) "-SENDING ADDRESS GOING BACKWARD"'),
    ('007307.00', '1304.10 00',  'B,SERS            (ext) "-ON A FORWARD OPERATION."'),
    ('007307.40', '7314.50 00',  'B,I4621           BIT 18 SET -> 007314.40'),
    ('007310.00', '7312.30 42',  'BXCZ,$+2.0        bit 18 = 0 -> 007312.00'),
    ('007310.40', '1310.00 80',  'SIC,SEN           (ext) "-SENDING ADDRESS NOT STEPPED ON"'),
    ('007311.00', '1304.10 00',  'B,SERS            (ext) "-A FORWARD OPERATION."'),
    ('007311.40', '7314.50 00',  'B,I4621           BIT 18 SET -> 007314.40'),
    ('007312.00', '22.03 70',    'SR,$X1,$X2        word 18 = index register 2'),
    ('007312.40', '22.04 10',    'LX,$X2,$X2'),
    ('007313.00', '7314.71 40',  'BZXVZ,I4621       BIT 18 SET -> 007314.40 = I4621'),
    ('007313.40', '1310.00 80',  'SIC,SEN           (ext) "-NO WORD GOES TO SECOND RECEIVING"'),
    ('007314.00', '1304.10 00',  'B,SERS            (ext) "-LOCATION ON A FORWARD OPERATION."'),
]

# ---------------------------------------------------------------------
# PDF p.110, 007314.40-007343.00.  TEST 2A, the BACKWARD half, at
# I4621, and the sub-test's tail.
# ---------------------------------------------------------------------
TEST2A_BKW_ROWS = [
    ('007314.40', '7424.22 00',  'I4621 Z,I46D1     "-DO A BACKWARD OPERATION."'),
    ('007315.00', '7425.22 00',  'Z,I46D2'),
    ('007315.40', '7426.22 00',  'Z,I46D3'),
    ('007316.00', '7432.02 10',  'LX,$X1,I46XW1'),
    ('007316.40', '7433.04 10',  'LX,$X2,I46XW2'),
    ('007317.00', '7434.06 10',  'LX,$X3,I46XW3'),
    ('007317.40', '7427.03 10',  'SX,$X1,I46D4'),
    ('007320.00', '7430.05 10',  'SX,$X2,I46D5'),
    ('007320.40', '7431.07 10',  'SX,$X3,I46D6'),
    ('007321.00', '13130.04 10', 'LX,$X2,BIT44      (ext) direct count = 2 words'),
    ('007321.40', '7430.00 80 007425.05 20',
                                 'TB,$X2,I46D5,I46D2  THE REPO"S FIRST TB ROW, bit 55 = 1, FULL WORD at an ODD half-word'),
    ('007322.40', '7426.00 80 000000.20 50',
                                 'L(BU),I46D3       read back the word ABOVE the target'),
    ('007323.40', '7325.74 C2',  'BRZ,$+2.0         BIT 18 SET -> 007325.40'),
    ('007324.00', '1310.00 80',  'SIC,SEN           (ext) "-RECEIVING ADDRESS GOING FORWARD"'),
    ('007324.40', '1304.10 00',  'B,SERS            (ext) "-ON A BACKWARD OPERATION."'),
    ('007325.00', '7337.50 00',  'B,I4622           BIT 18 SET -> 007337.40'),
    ('007325.40', '7425.02 10',  'LX,$X1,I46D2'),
    ('007326.00', '7330.30 40',  'BZXCZ,$+2.0       bit 18 = 0 -> 007330.00'),
    ('007326.40', '1310.00 80',  'SIC,SEN           (ext) "-RECEIVING LOCATION DOES NOT GET"'),
    ('007327.00', '1304.10 00',  'B,SERS            (ext) "-FIRST WORD FROM SENDING LOCN."'),
    ('007327.40', '7337.50 00',  'B,I4622           BIT 18 SET -> 007337.40'),
    ('007330.00', '7424.02 10',  'LX,$X1,I46D1'),
    ('007330.40', '22.03 70',    'SR,$X1,$X2'),
    ('007331.00', '22.04 10',    'LX,$X2,$X2'),
    ('007331.40', '7333.71 42',  'BXVZ,$+2.0        BIT 18 SET -> 007333.40'),
    ('007332.00', '1310.00 80',  'SIC,SEN           (ext) "-SENDING ADDRESS GOING FORWARD ON"'),
    ('007332.40', '1304.10 00',  'B,SERS            (ext) "-A BACKWARD OPERATION."'),
    ('007333.00', '7337.50 00',  'B,I4622           BIT 18 SET -> 007337.40'),
    ('007333.40', '7424.02 10',  'LX,$X1,I46D1'),
    ('007334.00', '7336.30 42',  'BXCZ,$+2.0        bit 18 = 0 -> 007336.00'),
    ('007334.40', '1310.00 80',  'SIC,SEN           (ext) "-SENDING ADDRESS NOT STEPPED ON"'),
    ('007335.00', '1304.10 00',  'B,SERS            (ext) "-A BACKWARD OPERATION."'),
    ('007335.40', '7337.50 00',  'B,I4622           BIT 18 SET -> 007337.40'),
    ('007336.00', '7337.71 40',  'BZXVZ,I4622       "-OK"  BIT 18 SET -> 007337.40 = I4622'),
    ('007336.40', '1310.00 80',  'SIC,SEN           (ext) "-NO WORD GOES TO SECOND RECEIVING"'),
    ('007337.00', '1304.10 00',  'B,SERS            (ext) "-LOCATION ON A BACKWARD OPERATION."'),
    ('007337.40', '7340.50 00',  'I4622 B,$+1.0     BIT 18 SET -> 007340.40'),
    ('007340.00', '7272.04 00',  'BD,I4620          bit 18 = 0 -> 007272.00 = I4620'),
    ('007340.40', '1311.40 80',  'SIC,SENO+.32      (ext) pair 40 is a BIT OFFSET'),
    ('007341.00', '1301.10 00',  'B,SSW             (ext) "-TO SSIP."'),
    ('007341.40', '7342.04 00',  'BD,$+.32          bit 18 = 0 -> 007342.00'),
    ('007342.00', '7422.32 10',  'LX,$X13,IC246     "-UPDATE CONTINUITY."'),
    ('007342.40', '13065.32 B0', 'V+,$X13,BIT9      (ext) TEST 2A"s continuity bit'),
    ('007343.00', '7422.33 10',  'SX,$X13,IC246'),
]

# ---------------------------------------------------------------------
# PDF p.111, 007343.40-007372.00.  "-TEST 2B."  The direct/immediate
# count modifier, and the sub-test's tail.
# ---------------------------------------------------------------------
TEST2B_ROWS = [
    ('007343.40', '7424.22 00',  'I4623 Z,I46D1     "-TEST DIRECT-INNEDIATE MODIFIER."'),
    ('007344.00', '7425.22 00',  'Z,I46D2'),
    ('007344.40', '13035.02 10', 'LX,$X1,I00O       (ext) the all-ones constant'),
    ('007345.00', '7427.03 10',  'SX,$X1,I46D4'),
    ('007345.40', '7430.03 10',  'SX,$X1,I46D5      pair 03, not 05: this is $X1'),
    ('007346.00', '13130.02 10', 'LX,$X1,BIT44      (ext) a DIRECT count of 2, deliberately'),
    ('007346.40', '7427.00 80 007424.02 A0',
                                 'TI,1,I46D4,I46D1  bit 56 = 1 IMMEDIATE, count = 1'),
    ('007347.40', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2       the word a count of 2 would have reached'),
    ('007350.40', '7352.74 C2',  'BRZ,$+2.0         BIT 18 SET -> 007352.40'),
    ('007351.00', '1310.00 80',  'SIC,SEN           (ext) "-TRANSMIT IMMEDIATE USES"'),
    ('007351.40', '1304.10 00',  'B,SERS            (ext) "-A DIRECT COUNT."'),
    ('007352.00', '7355.10 00',  'B,I4624           bit 18 = 0 -> 007355.00'),
    ('007352.40', '7424.00 80 000000.20 50',
                                 'L(BU),I46D1       the word the count of 1 DID reach'),
    ('007353.40', '7355.34 C0',  'BZRZ,I4624        bit 18 = 0 -> 007355.00 = I4624'),
    ('007354.00', '1310.00 80',  'SIC,SEN           (ext) "-RECEIVING LOCATION DOES NOT GET"'),
    ('007354.40', '1304.10 00',  'B,SERS            (ext) "-FIRST WORD FROM SENDING LOCN."'),
    ('007355.00', '7424.22 00',  'I4624 Z,I46D1     the DIRECT half, same setup'),
    ('007355.40', '7425.22 00',  'Z,I46D2'),
    ('007356.00', '13035.02 10', 'LX,$X1,I00O       (ext)'),
    ('007356.40', '7427.03 10',  'SX,$X1,I46D4'),
    ('007357.00', '7430.03 10',  'SX,$X1,I46D5'),
    ('007357.40', '13131.04 10', 'LX,$X2,BIT45      (ext) a DIRECT count of 1'),
    ('007360.00', '7427.00 80 007424.04 20',
                                 'T,$X2,I46D4,I46D1  J = 2, so an immediate reading would move TWO'),
    ('007361.00', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2'),
    ('007362.00', '7364.34 C2',  'BRZ,$+2.0         bit 18 = 0 -> 007364.00'),
    ('007362.40', '1310.00 80',  'SIC,SEN           (ext) "-TRANSMIT DIRECT USES"'),
    ('007363.00', '1304.10 00',  'B,SERS            (ext) "-AN IMMEDIATE COUNT."'),
    ('007363.40', '7366.50 00',  'B,I4625           BIT 18 SET -> 007366.40'),
    ('007364.00', '7424.00 80 000000.20 50',
                                 'L(BU),I46D1'),
    ('007365.00', '7366.74 C0',  'BZRZ,I4625        BIT 18 SET -> 007366.40 = I4625'),
    ('007365.40', '1310.00 80',  'SIC,SEN           (ext) "-RECEIVING LOCATION DOES NOT GET"'),
    ('007366.00', '1304.10 00',  'B,SERS            (ext) "-FIRST WORD FROM SENDING LOCN."'),
    ('007366.40', '7367.50 00',  'I4625 B,$+1.0     BIT 18 SET -> 007367.40'),
    ('007367.00', '7343.44 00',  'BD,I4623          BIT 18 SET -> 007343.40 = I4623'),
    ('007367.40', '1311.40 80',  'SIC,SENO+.32      (ext) pair 40 is a BIT OFFSET'),
    ('007370.00', '1301.10 00',  'B,SSW             (ext) "-TO SSIP."'),
    ('007370.40', '7371.04 00',  'BD,$+.32          bit 18 = 0 -> 007371.00'),
    ('007371.00', '7422.32 10',  'LX,$X13,IC246     "-UPDATE CONTINUITY."'),
    ('007371.40', '13066.32 B0', 'V+,$X13,BIT10     (ext) TEST 2B"s continuity bit'),
    ('007372.00', '7422.33 10',  'SX,$X13,IC246     the last row before TEST 2C'),
]

# I4620 is the first label after this block's SLC -- an anchor, not
# evidence, though "BD,I4620" at 007340.00 reaches it through the
# symbol table.  The other five fall out of the location counter and
# are named by fifteen branch rows between them (I4621 by five,
# I4622 by five, I4623 by one, I4624 by two, I4625 by two).  The constant
# block's ten symbols are INPUT here and are asserted by
# verify_ax4b_1246_transmit_swap_listing.py; they are deliberately
# absent.
SYMBOLS = {
    'I4620': '007272.00',
    'I4621': '007314.40',
    'I4622': '007337.40',
    'I4623': '007343.40',
    'I4624': '007355.00',
    'I4625': '007366.40',
}

if __name__ == "__main__":
    fails = check_rows(prog, [], SYMBOLS, label='1246m ')
    fails += check_rows(prog, TEST2A_FWD_ROWS, label='1246 T2A-F ')
    fails += check_rows(prog, TEST2A_BKW_ROWS, label='1246 T2A-B ')
    fails += check_rows(prog, TEST2B_ROWS, label='1246 T2B   ')
    finish(fails)
