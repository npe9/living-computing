#!/usr/bin/env python3
"""verify_ax4b_1246_memories_listing.py -- jb_ax4b "I-BOX 4", routine
1246 ("TEST TRANSMIT AND SWAP"), the MEMORY-PAIRING sub-tests of
TEST 1, "THE NINE POSSIBILITIES OF ADDRESS COMBINATIONS", checked
against the machine code the listing prints beside each source line.
Four blocks, 176 printed rows, plus 8 symbol-table assertions:

  PDF p.101  006772.00-007021.40  TEST 1B, EXT MEM TO IX STG  44 rows
  PDF p.102  007022.00-007051.40  TEST 1C, EXT MEM TO INT MEM 44 rows
  PDF p.103  007052.00-007101.40  TEST 1D, IX STG TO EXT MEM  44 rows
  PDF p.106  007162.00-007211.40  TEST 1G, INT MEM TO EXT MEM 44 rows

COMPLETENESS, proved independently of the run, because check_rows only
checks the rows it is HANDED -- a row present in the .strap but left
out of a ROWS list would pass silently and leave the coverage short.
Each sub-test spans 24 words = 48 half-word slots, and each contains
exactly four TWO-slot instructions (two T and two L(BU)), so
48 - 4 = 44 printed rows.  All four spans were checked against the
listing's own location column and are 24 words: 006772.00-007021.40,
007022.00-007051.40, 007052.00-007101.40, 007162.00-007211.40.
4 x 44 = 176 rows, plus 8 symbol assertions = the 184 PASS lines the
script prints.  No row was skipped.

WHAT THIS ADDS TO THE TWO SIBLINGS, which must be read first:
verify_ax4b_1246_transmit_swap_listing.py has the preamble, TEST 1A
and TEST 2C and the constants; verify_ax4b_1246_modifiers_listing.py
has TESTs 2A and 2B.  Neither touches 006772.00-007271.40.  That was
checked by grep over every tests/verify_*.py and decks/*.strap
before a line of this file was written: the range appears only in
PROSE in both siblings ("TEST 1B ... begins at octal 006772.00 ... and
is NOT transcribed"), never in a ROWS entry, and no .strap SLC lands
inside it.  The premise held.

WHERE THIS STOPS, precisely, and why there.  The nine sub-tests of
TEST 1 are a 3x3 of sending x receiving memory, one listing page each:

        receiving ->   EXT (I46D2)   IX ($X3)      INT ($R)
  sending EXT (I46D4)  1A p.100      1B p.101      1C p.102
  sending IX  ($X4)    1D p.103      1E p.104      1F p.105
  sending INT ($L)     1G p.106      1H p.107      1I p.108

WITHIN ROUTINE 1246 -- the scope matters, and NOT SETTLED item 5 below
says why -- a new operand kind first appears in exactly four cells:
1B is the routine's first index register in TRANSMIT's A2 19-bit
half-word field, 1C its first internal-memory register in either
field, 1D its first index register in TRANSMIT's A1 24-bit BIT field,
1G its first internal-memory register in A1.  Repo-wide none of that
is a first; jb_ax5b's routine 160 got there with TI.  Those four are
here.  NOT transcribed, with their
octal addresses so a later pass can pick them up:

  TEST 1E  007102.00-007131.40  PDF p.104  I465 / I4614  IX  -> IX
  TEST 1F  007132.00-007161.40  PDF p.105  I466 / I4615  IX  -> INT
  TEST 1H  007212.00-007241.40  PDF p.107  I468 / I4617  INT -> IX
  TEST 1I  007242.00-007271.40  PDF p.108  I469 / I4618  INT -> INT

Each is a cross-product of operand kinds both of whose halves are
already witnessed below, in the identical 44-row shape; all four pages
were read first-hand at 400 dpi so that this statement is not a guess.
TESTs 2A/2B (007272.00-007372.00) and 2C (007372.40-007421.40) belong
to the two siblings.

=====================================================================
THE VERDICT ON "1B-1I ARE MORE ROWS, NOT MORE KINDS".

The 1A transcriber wrote, when skipping them, that 1B "is a near-clone
of 1A with $X3 for I46D2 and adds rows, not kinds."  Tested against
the pages, that is HALF RIGHT, and the half that is wrong is the
interesting half.

RIGHT ABOUT MNEMONICS, and this was measured, not assumed: every
operation in the 176 rows below -- Z, LX, SX, T, L(BU), BZRZ, SIC, B,
KV, KC, BXE, SR, KVI, BXF, BRZ, BD, V+ -- already has a row in TEST 1A
in the sibling file.  NOT ONE mnemonic here is a first for this
repository.  TB, TBI, TI, SWAPI, SWAPB, SWAPBI are still where they
were: TI witnessed in jb_ax5b and in 1246's own TEST 2B, the other
five card-only.  Right about the shape too: the 44 rows are in the
same order as 1A's, with the same six error pairs, the same branch
offsets relative to the block, and the same count constant BIT45.

WRONG THAT NOTHING IS NEW.  The substitution changes the KIND of the
operand, not only its value.  In TEST 1A both of TRANSMIT's address
fields name external-memory constants (I46D2 007425.00, I46D4
007427.00).  Here they name REGISTERS:

    A1 (24-bit BIT address, bits 0-23)   $X4 = word 0o24  (TEST 1D)
                                         $L  = word 0o10  (TEST 1G)
    A2 (19-bit half-word addr, 32-50)    $X3 = word 0o23  (TEST 1B)
                                         $R  = word 0o11  (TEST 1C)

and so do eleven DirIndex rows per page -- "Z,$X3", "Z,$R", "Z,$L",
"Z,$X4", "SX,$X1,$X4", "SX,$X1,$L", "LX,$X2,$X3", "LX,$X2,$R",
"L(BU),$X3", "L(BU),$R".  Those are a REAL check and not a SYN-fed
one, because $X3/$X4/$R/$L are not SYN'd here: they come from the
assembler's own tables, and the listing's printed word numbers check
those tables against IBM's assembler.

  $X0..$X15 -> strap_asm.eval_system_symbol's "(16 + n) * 64", from
  Reference Manual printed p.23 (PDF p.26, footer "Operand
  Designation  23"), READ FIRST-HAND for this file: "the corresponding
  index word X1-X15 will be used in the operation.  These words are in
  storage locations 17-31.  When the field J is 0, storage location 16
  is used in the operation.  This location is named X0."  So $X3 =
  word 19 = 0o23 and $X4 = word 20 = 0o24 -- and the page prints
  000023 and 24.
  $R, $L -> opcodes.SYSTEM_SYMBOLS, entered in this repo from C22-6531
  Appendix A as "R": (9, 0) "Right Half of Accumulator" and "L":
  (8, 0) "Left Half of Accumulator".  So $R = word 9 = 0o11 and $L =
  word 8 = 0o10 -- and the page prints 000011 and 10.  (Those two
  entries are NOT new witnesses, and an earlier draft that said so was
  wrong: see NOT SETTLED item 5, where grep names the three other
  files that already have $R and $L rows.  They are new witnesses in a
  TRANSMIT address field, which is a smaller claim.)

So: MORE ROWS, NO NEW MNEMONICS, BUT A NEW ADDRESS-OPERAND KIND IN
BOTH OF TRANSMIT'S ADDRESS FIELDS -- new to ROUTINE 1246, whose own
transmits named only memory until these pages; NOT new to this
repository, where verify_ax5b_160_test6_listing.py's "TI,1,$IND,$X1"
got there first.  The deck's own name for that kind is in the
headings: "IX STG" and "INT MEM" against 1A's "EXT
MEM".  The 1A transcriber's judgement was sound as a reason not to
grind through all eight; it was not sound as a claim that the eight
witness nothing.

AND THE A2 ODD-HALF-WORD QUESTION, ANSWERED: NO.  Every T row across
PDF pp.101-108 -- all sixteen of them, two per sub-test -- prints "02"
for bits 50-55, so bit 50 = 0 in every one.  The reason is arithmetic,
not luck: the only three A2 operands in TEST 1 are I46D2 (007425.00, a
word-aligned constant), $X3 (word 0o23) and $R (word 0o11), and a word
address has half-word select zero by construction.  The MEASURED NULL
both siblings record therefore survives and gets three times as many
rows behind it, but it is NOT broken: routine 1246 contains no
Transmit with an odd-half-word A2, and nothing in this file would
catch an encoder that dropped bit 50.  The injection is re-run and
recorded as a null below.

=====================================================================
CITED BY PDF PAGE, AND ONLY BY PDF PAGE.  jb_ax4b's listing sheets
carry NO printed folio anywhere; pp.101-108 were rendered at 400 dpi
for this transcription and their top strip, bottom strip and both
edges read.  Reference Manual 22-6530-2 is cited by PRINTED page and
PDF page = printed page + 3, confirmed first-hand twice here (printed
p.23 is PDF p.26, footer "Operand Designation  23"; printed p.41 is
PDF p.44, footer "Instruction Sequencing  41").

LABELS ARE LETTER-I, NOT DIGIT-1, per docs/listing_typography.md and
the repo-wide rename: I462, I4611, I463, I4612, I464, I4613, I467,
I4616, I46D2, I46D4, IC246.  The TEST NUMBERS in the headings ("TEST
1B", "TEST 1C") are DIGIT one -- a different glyph, with the top-left
flag, in the same rows.

=====================================================================
EVERY HEADING AND ERROR MESSAGE IN THE TRANSCRIBED RANGE, VERBATIM,
with the octal location of the SIC that reports it.  Each error is a
two-half-word pair, "SIC,SEN" then "B,SERS".

  PDF p.101, TEST 1B, I462 at 006772.00:
    heading    -TEST 1B,EXT MEM TO IX STG.
    006776.40  -TRANSMIT 1 WD EXT MEM TO
               -IX STG DROPS ALL BITS,        <- COMMA; deck typo
    007001.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 0-24.
    007003.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 28-45.
    007006.00  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 46 TO 63.
    007010.00  -ABOVE TYPE TRANSMIT LOSES
               -BIT 25.
    007015.00  -ABOVE TYPE TRANSMIT PICKS
               -UP SOME BITS 0-63.
    I4611 007011.00  -CHECK FOR SPURIOUS BITS.
    007017.40  -TO SSIP.
    007020.40  -UPDATE CONTINUITY CHECK.

  PDF p.102, TEST 1C, I463 at 007022.00:
    heading    -TEST 1C, EXT MEM TO INT MEM.
    007026.40  -TRANSMIT 1 WD EXT MEM TO
               -INT MEM DROPS ALL BITS.
    007031.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 0-24.
    007033.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 28-45.
    007036.00  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 46 TO 63.
    007040.00  -ABOVE TYPE TRANSMIT LOSES
               -BIT 25.
    007045.00  -ABOVE TYPE TRANSMIT PICKS
               -UP SOME BITS 0-63.
    I4612 007041.00  -CHECK FOR SPURIOUS BITS.
    007047.40  -TO SSIP.
    007050.40  -UPDATE CONTINUITY CHECK.

  PDF p.103, TEST 1D, I464 at 007052.00:
    heading    -TEST 1D, IX STG TO, EXT MEM.  <- stray comma; deck typo
    007056.40  -TRANSMIT 1 WD IX CORE STG TO
               -EXT MEM DROPS ALL BITS.
    007061.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 0-24.
    007063.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 28-45.
    007066.00  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 46 TO 63.
    007070.00  -ABOVE TYPE TRANSMIT LOSES
               -BIT 25.
    007075.00  -ABOVE TYPE TRANSMIT PICKS
               -UP SOME BITS 0-63.
    I4613 007071.00  -CHECK FOR SPURIOUS BITS.
    007077.40  -TO SSIP.
    007100.40  -UPDATE CONTINUITY CHECK.

  PDF p.106, TEST 1G, I467 at 007162.00:
    heading    -TEST 1G, INT MEM TO EXT MEM.
    007166.40  -TRANSMIT 1 WD INT MEM TO
               -EXT MEM DROPS ALL BITS.
    007171.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 0-24.
    007173.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 28-45.
    007176.00  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 46 TO 63.
    007200.00  -ABOVE TYPE TRANSMIT LOSES
               -BIT 25.
    007205.00  -ABOVE TYPE TRANSMIT PICKS
               -UP SOME BITS 0-63.
    I4616 007201.00  -CHECK FOR SPURIOUS BITS.
    007207.40  -TO SSIP.
    007210.40  -UPDATE CONTINUITY CHECK.

TYPO vs SCAN DAMAGE, decided by comparing the suspect glyph with a
correct instance of the same character on the same or an adjacent
line.  Damage leaves a ragged CORRECT letter; a typo prints a clean
WRONG one.  Two verdicts inside the transcribed range:

  1. PDF p.101, 006777.00: "-IX STG DROPS ALL BITS,"  DECK TYPO.
     The terminator has the period's round bowl AND a tail descending
     below the baseline -- the shape of the commas in "-TEST 1B,EXT
     MEM TO IX STG." on the same page and in "SIC,SEN" beside it.
     The period two lines below, in "-OF BITS 0-24.", is a bare round
     bowl with no tail, and so is p.102's "-INT MEM DROPS ALL BITS.",
     the identical sentence one sub-test later.  Every stroke is clean;
     nothing is ragged.  A clean WRONG character.

  2. PDF p.103, 007052.00: "-TEST 1D, IX STG TO, EXT MEM."  DECK
     TYPO.  The comma after "TO" is identical in shape, weight and
     baseline offset to the legitimate comma after "1D" eight
     characters earlier on the SAME LINE, so it is a comma and not a
     damaged period; the line's final period is a bare bowl.  The
     other eight TEST 1 headings read "<FROM> TO <TO>." with no comma
     there.  A clean WRONG character.

  No DROPPED-LETTER case arises inside this range, so the pitch test
  (px-per-cell against a known-good word on the line above) was not
  needed here.

Two more, on pages this file does NOT transcribe, recorded so they
are not re-discovered:
  - PDF p.104 heading: "-TEST 1E,IX STG TO IX STGZ."  DECK TYPO.  The
    trailing Z is a clean, fully-formed Z whose diagonal and both
    horizontals are as solid as the Z's in "BZRZ" at 007106.00 and
    "Z,$X3" at 007102.00 on the SAME page.  Nothing is ragged, so it
    is not damage; a struck-over character was typed.
  - PDF p.108, 007270.40, prints "-UPDATE CONTINUITY." where pp.101
    through 107 all print "-UPDATE CONTINUITY CHECK."  There is no
    ghost, no smear and no pitch gap after the period: a real textual
    variation in the deck.  (TEST 2A and 2B print "-UPDATE
    CONTINUITY." too, per the modifiers sibling, so 1I's wording is
    the one the deck drifts toward, not a one-off.)

A CORRECTION TO THE BRIEF THIS FILE WAS WRITTEN FROM, in the spirit of
the sibling's "TWO BASIC ROUTINES" correction: the brief describes
TEST 1A as "the ninth, EXT-to-EXT".  The pages say 1A is the FIRST of
the nine, at 006742.00 on PDF p.100, and the sub-tests run 1A..1I in
address order across pp.100-108.  Nothing below depends on this; it is
recorded so the next reader does not inherit it.

BRANCH POLARITY.  B<IND> branches when the indicator is ON, BZ<IND>
when it is OFF, and BOTH error shapes exist in these decks -- 1246's
own TEST 2A carries "-OK" on a BZXVZ, the deck labelling the branch as
the good path in its own hand.  THESE 176 rows are uniformly of that
shape: the BRANCH is the OK path and the FALL-THROUGH is the error
pair.  "BZRZ,$+2.0" at 006776.00 skips the SIC/B pair when Result Zero
is OFF -- the all-ones word did arrive -- and falls into "-TRANSMIT 1
WD EXT MEM TO -IX STG DROPS ALL BITS," when it is ON.  "BRZ,$+1.32"
at 007014.40 is the mirror image: OK when Result Zero is ON, error
"-ABOVE TYPE TRANSMIT PICKS -UP SOME BITS 0-63." when it is off.  The
three BXE and one BXF per sub-test are the same shape.  Nothing here
requires an indicator to be SET; the requirement is always the branch.

=====================================================================
BIT-18 SELF-CHECKS.  The listing prints each half-word as bits 0-17 in
six octal digits, ".", bits 18-23 in two octal digits, then bits 24-31
in two hex digits.  BIT 18 IS THE TOP BIT OF THE OCTAL PAIR, so a pair
of octal 40 or more has it set.  Every row below whose operand is a
label or a self-relative was decoded that way and read back against
the page's own label column.

THE EXCLUSION HAS FOUR CLASSES, NOT TWO, and they have four different
reasons:

  (a) HALF-WORD SELECT, decodable.  Branch targets, and the DirIndex
      19-bit address fields (Z, V+, KV, KC, SR, KVI, L(BU)'s A1 is
      NOT one of these -- see (c)).  Bit 18 is the half-word select of
      a 19-bit effective address.
  (b) LX and SX are EXCLUDED, and not for the same reason as (c)/(d).
      Reference Manual printed p.23 (PDF p.26), read first-hand:
      "In the majority of these operations, 19 bits of the effective
      address are used in order to permit addressing of half-words.
      The two exceptions use only 18 bits of the effective address
      because they require full-word operands."  The two exceptions
      are LOAD INDEX and STORE INDEX; p.23's own LX paragraph repeats
      it -- "The index word specified by J is replaced by the full-
      word specified by bits 0-17 of the effective address."  So in
      "LX,$X1,BIT45" -> 13131.02 10 the pair 02 is NOT a half-word
      select; bit 18 is simply not part of the address.
  (c) SIC is EXCLUDED because its operand is a 24-bit BIT address in
      bits 0-23, so the octal pair is a BIT OFFSET inside the word.
      Reference Manual printed p.41 (PDF p.44, footer "Instruction
      Sequencing  41"), read first-hand: STORE INSTRUCTION COUNTER IF
      "causes the instruction counter contents to be stored in bits
      0-18 of the half-word specified by bits 0-18 of the effective
      storage address."  "SIC,SENO+.32" prints 1311.40 80: the 40 is
      bit 32 of word 001311, a bit offset that happens to coincide
      numerically with a set bit 18.
  (d) TRANSMIT's A1 is EXCLUDED for the same reason as (c) but in a
      different place: A1 is a 24-bit BIT address in bits 0-23 of the
      FIRST group, so "7427.00" + pair "00" is word 007427 bit 0.  Its
      A2, in the SECOND group, IS a half-word address -- but its
      select is BIT 50, the top bit of the SECOND group's octal pair,
      twelve bits away from bit 18.  Neither group of a T row obeys
      the bit-18 rule.

  BRANCHES WITH BIT 18 SET -- three per sub-test, twelve in all:
    TEST 1B (p.101)
      007001.00  BXE,$+1.32  -> 7002.72 C2.  72 = 111010, BIT 18 = 1
                 -> 007002.40, and 007001.00 + 1 word + 32 bits is
                 007002.40.
      007003.00  BXE,$+1.32  -> 7004.72 C2.  BIT 18 = 1 -> 007004.40.
      007020.00  BD,$+.32    -> 7020.44 00.  44 = 100100, BIT 18 = 1
                 -> 007020.40, and 007020.00 + 32 bits = 007020.40.
    TEST 1C (p.102)  007031.00 -> 7032.72 C2, 007033.00 -> 7034.72 C2,
                     007050.00 BD,$+.32 -> 7050.44 00.
    TEST 1D (p.103)  007061.00 -> 7062.72 C2, 007063.00 -> 7064.72 C2,
                     007100.00 BD,$+.32 -> 7100.44 00.
    TEST 1G (p.106)  007171.00 -> 7172.72 C2, 007173.00 -> 7174.72 C2,
                     007210.00 BD,$+.32 -> 7210.44 00.

  BRANCHES WITH BIT 18 CLEAR -- and the third BXE is the instructive
  one, because it is the SAME instruction at an ODD half-word:
    TEST 1B (p.101)
      006776.00  BZRZ,$+2.0  -> 7000.34 C0.  34 = 011100, bit 18 = 0
                 -> 007000.00, and 006776.00 + 2 words = 007000.00.
      006777.40  B,I4611     -> 7011.10 00.  10 = 001000, bit 18 = 0
                 -> 007011.00, where p.101 prints the label I4611.
      007005.40  BXE,$+1.32  -> 7007.32 C2.  32 = 011010, bit 18 = 0
                 -> 007007.00.  The odd-half start carries the +32
                 into the next word, so this one does NOT set bit 18 --
                 the same pair of readings the sibling records for
                 006751.00 and 006755.40 in TEST 1A.
      007007.40  BXF,$+1.32  -> 7011.23 42.  23 = 010011, bit 18 = 0
                 -> 007011.00 = I4611.
      007014.40  BRZ,$+1.32  -> 7016.34 C2.  bit 18 = 0 -> 007016.00.
      007016.00  B,$+1.0     -> 7017.10 00.  bit 18 = 0 -> 007017.00.
      007016.40  BD,I462     -> 6772.04 00.  04 = 000100, bit 18 = 0
                 -> 006772.00, where p.101 prints the label I462.
    TEST 1C (p.102)  007026.00 -> 7030.34 C0; 007027.40 B,I4612 ->
      7041.10 00 = 007041.00 = I4612; 007035.40 -> 7037.32 C2;
      007037.40 BXF -> 7041.23 42 = I4612; 007044.40 BRZ -> 7046.34 C2;
      007046.00 -> 7047.10 00; 007046.40 BD,I463 -> 7022.04 00 =
      007022.00 = I463.
    TEST 1D (p.103)  007056.00 -> 7060.34 C0; 007057.40 B,I4613 ->
      7071.10 00 = 007071.00 = I4613; 007065.40 -> 7067.32 C2;
      007067.40 BXF -> 7071.23 42 = I4613; 007074.40 BRZ -> 7076.34 C2;
      007076.00 -> 7077.10 00; 007076.40 BD,I464 -> 7052.04 00 =
      007052.00 = I464.
    TEST 1G (p.106)  007166.00 -> 7170.34 C0; 007167.40 B,I4616 ->
      7201.10 00 = 007201.00 = I4616; 007175.40 -> 7177.32 C2;
      007177.40 BXF -> 7201.23 42 = I4616; 007204.40 BRZ -> 7206.34 C2;
      007206.00 -> 7207.10 00; 007206.40 BD,I467 -> 7162.04 00 =
      007162.00 = I467.

  AND THE NON-BRANCH LABEL AND REGISTER ROWS, class (a), because the
  brief asks for EVERY row whose operand is a label or self-relative
  and the lists above are branches only.  Eight distinct shapes occur:
    "Z,I46D2"  -> 7425.22 00      "Z,I46D4"  -> 7427.22 00
    "Z,$X3"    ->   23.22 00      "Z,$R"     ->   11.22 00
    "Z,$L"     ->   10.22 00      "Z,$X4"    ->   24.22 00
    "KV,$X2,I00O" -> 13035.04 90  "KC,$X2,I00O" -> 13035.05 90
    "SR,$X2,$X2"  ->    22.05 70  "KVI,$X2,(8)777777.0" -> 777777.05 04
    "V+,$X13,BIT1" -> 13055.32 B0 (and BIT2/BIT3/BIT6 the same shape)
  and in EVERY one of them bit 18 is ZERO: the printed pairs are 22,
  04, 05, 32 and 33, all less than octal 40.  The reason is arithmetic,
  not luck.  Every operand named is a WORD: the routine's constants sit
  at .00 addresses in the block at 007422.00-007434.00, the common
  constants at 013035.00 / 013055.00 / 013131.00, and the registers at
  words 0o10, 0o11, 0o22, 0o23, 0o24.  A word address has half-word
  select zero by construction, so these rows CANNOT witness bit 18 at
  one.  Bit 18 is witnessed at ONE only by the twelve branches above,
  and at ZERO by everything else.  Said out loud rather than implied.

  AND THE BIT-50 NULL, again, measured and not assumed.  All eight T
  rows below print "02" for bits 50-55.  I46D2 is word-aligned, $X3 is
  word 0o23, $R is word 0o11 -- three word addresses, so bit 50 is
  zero in every one.  The A2-mask injection is therefore a NULL here
  exactly as in both siblings, and is recorded as one.

=====================================================================
WITNESS TIERING.  EVERY SYN IS AN INPUT, NOT A WITNESS.  AN SLC-PLACED
LABEL IS AN ANCHOR, NOT EVIDENCE.

  SYN'd (address supplied to the assembler from the very rows that
  print it -- these rows check opcode and modifier bits only):
      SEN 001310.00, SENO 001311.00, SERS 001304.00, SSW 001301.00,
      I00O 013035.00, BIT1 013055.00, BIT2 013056.00, BIT3 013057.00,
      BIT6 013062.00, BIT45 013131.00.
  BIT1/BIT2/BIT3/BIT6 have corroboration that does not turn them into
  witnesses: they are four of twelve CONSECUTIVE words, 013054.00
  through 013067.00, one per sub-test in heading order -- BIT0 for
  TEST 1A and BIT9/BIT10/BIT11 for TESTs 2A/2B/2C are already SYN'd by
  the two siblings, and pp.104/105/107/108 print BIT4 013060, BIT5
  013061, BIT7 013063, BIT8 013064 for 1E/1F/1H/1I.  That twelve-word
  run matches ICK246 = (8)777700.00 exactly: as an 18-bit field it is
  bits 0-11, TWELVE bits, and the deck's own expected-continuity
  constant therefore says TEST 1 has NINE sub-tests -- independently of
  the headings.  Corroboration, not evidence.

  ANCHORS, not witnesses -- each is the first label after an SLC, so
  checking it checks this transcription against the number this
  transcription handed the SLC:
      I462 006772.00 (SLC (8)6772.0) and I467 007162.00 (SLC
      (8)7162.0).  They are asserted below because a wrong one would
      silently mis-place a whole block, not because they are evidence.
      The same caveat the siblings make about I46/I461/I4620.

  GENUINE WITNESSES -- defined inside a transcribed block at addresses
  the location counter computes, and named by rows whose printed
  address field therefore checks placement:
      I4611 007011.00  (named by "B,I4611" at 006777.40 and
                        "BXF,$+1.32" resolving to it at 007007.40)
      I463  007022.00  (named by "BD,I463" at 007046.40 -- and reached
                        from the SAME SLC as I462, 20 words on, so it
                        is a location-counter value, not an anchor)
      I4612 007041.00  (named by "B,I4612" at 007027.40)
      I464  007052.00  (named by "BD,I464" at 007076.40)
      I4613 007071.00  (named by "B,I4613" at 007057.40)
      I4616 007201.00  (named by "B,I4616" at 007167.40)
  The constants block (IC246, I46D2, I46D4, ...) is INPUT here, not a
  witness: it is re-laid behind its own SLC at (8)7422.0 exactly as
  ../decks/ax4b_1246_modifiers.strap does, so that the ten symbols are
  location-counter values rather than ten more SYNs.  None of its rows
  is asserted by this file; verify_ax4b_1246_transmit_swap_listing.py
  asserts them.  What IS checked here is that the block's internal
  ORDER puts I46D2 three words and I46D4 five words past IC246 -- get
  either wrong and every T, Z, LX and SX row naming them moves.

SUBSTITUTIONS, three, all mechanical, none touching a bit; the .strap
header states them at length.  "%8@" -> "(8)"; "L%BU@" -> "L(BU)";
T's J field "$X1" -> "1" (Reference Manual printed p.30: "the field J,
bits 51-54, specifies an index register", and the printed J field IS 1,
so the substitution is CHECKED by the oracle, not assumed).  No row in
this range prints a location without machine code, so nothing is SLC'd
across and no word is invented.

=====================================================================
PROVEN DISCRIMINATING.  Observed failure sets, transcribed from the
runs, never predicted.  Every injection was made with __pycache__
removed on BOTH sides of the run; every patch was PRINTED BACK from
the file on disk before the run, so that a patch which silently failed
to match could not masquerade as a measured null (the patcher refuses
outright unless the target text occurs exactly once, and prints the
patched line with its line number); opcodes.py and strap_asm.py were
restored afterwards from byte-for-byte copies taken before the first
injection, both md5s matched the originals
(opcodes.py 4a0d0827de3d07057fc6ef116905de38,
strap_asm.py 664b99cf613d99cacd1f64ece96bb5d7) and `git status` on the
tree showed only this file and its .strap as new, nothing modified.

  1. strap_asm.eval_system_symbol's index-register rule,
     "return n if reg_context else (16 + n) * 64"
     -> "return n if reg_context else (17 + n) * 64"  (line 499)
     -- Reference Manual p.23's "storage locations 17-31" base, moved
     by one word
       19 ROWS.  Every $X-in-an-address-field row in all four blocks:
       006772.00 Z,$X3     '000024.22 00'              vs 000023.22 00
       006774.00 T A2      '007427.00 80 000024.02 20' vs ...000023...
       006775.00 L(BU),$X3 '000024.00 80 000000.20 50' vs 000023...
       007000.00 LX,$X2,$X3'000024.04 10'              vs 000023.04 10
       007004.40 SR,$X2,$X2'000023.05 70'              vs 000022.05 70
       007007.00 LX,$X2,$X2'000023.04 10'              vs 000022.04 10
       007011.00, 007012.40, 007013.40 repeat the first four shapes
       007034.40, 007037.00 (T1C) and 007064.40, 007067.00 (T1D) and
       007174.40, 007177.00 (T1G) are the SR/LX $X2 pair again
       007053.00 SX,$X1,$X4'000025.03 10'              vs 000024.03 10
       007054.00 T A1      '000025.00 80 007425.02 20' vs 000024...
       007071.40 Z,$X4     '000025.22 00'              vs 000024.22 00
       007072.40 T A1      '000025.00 80 007425.02 20' vs 000024...
       THE SIGNATURE INJECTION.  It moves BOTH of TRANSMIT's address
       fields -- A2 in TEST 1B, A1 in TEST 1D -- and the DirIndex rows
       that name the same registers, and NEITHER sibling file can
       produce it: neither has a register in an address field
       anywhere.  It leaves every $R and $L row untouched, which is
       the two symbol tables being separate, MEASURED rather than
       asserted.

  2. opcodes.SYSTEM_SYMBOLS["R"] (9, 0) -> (13, 0)  (line 333) -- $R
     aimed at word 13, the Remainder, instead of the accumulator's
     right half
       7 ROWS, TEST 1C ONLY:
       007022.00 Z,$R      '000015.22 00'              vs 000011.22 00
       007024.00 T A2      '007427.00 80 000015.02 20' vs ...000011...
       007025.00 L(BU),$R  '000015.00 80 000000.20 50' vs 000011...
       007030.00 LX,$X2,$R '000015.04 10'              vs 000011.04 10
       007041.00, 007042.40, 007043.40 repeat the first three shapes
       TESTs 1B, 1D and 1G do not move at all, because $R appears
       nowhere in them.  0o11 -> 0o15 is exactly word 9 -> word 13.
       Not the first listing row behind SYSTEM_SYMBOLS's "R" -- grep
       found verify_ax5b_1683_listing.py's "Z,$R" at 024372.40 and
       verify_ax5b_162_test1b_listing.py's "L(BU),$R" first -- but
       the first inside a TRANSMIT address field.

  3. opcodes.SYSTEM_SYMBOLS["L"] (8, 0) -> (7, 0)  (line 323)
       4 ROWS, TEST 1G ONLY:
       007163.00 SX,$X1,$L '000007.03 10'              vs 000010.03 10
       007164.00 T A1      '000007.00 80 007425.02 20' vs 000010...
       007201.40 Z,$L      '000007.22 00'              vs 000010.22 00
       007202.40 T A1      '000007.00 80 007425.02 20' vs 000010...
       The mirror of injection 2, and between them the listing
       separates the two halves of the accumulator: a block that
       checked only the opcode NAME could not tell $L from $R, and
       these two runs show that this one can.

  4. strap_asm.enc_transmit's A1 field -- "cat((bitaddr24, 24), ..."
     -> "cat((bitaddr24 >> 5, 24), ..."  (line 382), i.e. A1 encoded
     as a HALF-WORD address like A2 instead of the 24-bit BIT address
     the pocket card gives it
       8 ROWS, every T row and nothing else:
       006774.00 '000170.56 80 000023.02 20' vs 007427.00 80 000023...
       007012.40 '000170.56 80 000023.02 20' vs 007427.00 80 ...
       007024.00 '000170.56 80 000011.02 20' vs 007427.00 80 ...
       007042.40 '000170.56 80 000011.02 20' vs 007427.00 80 ...
       007054.00 '000000.50 80 007425.02 20' vs 000024.00 80 ...
       007072.40 '000000.50 80 007425.02 20' vs 000024.00 80 ...
       007164.00 '000000.20 80 007425.02 20' vs 000010.00 80 ...
       007202.40 '000000.20 80 007425.02 20' vs 000010.00 80 ...
       FIRST GROUP ONLY, second group untouched -- the A1/A2
       address-kind asymmetry measured rather than asserted, and here
       with REGISTER A1s, where the arithmetic checks by hand: $X4 is
       word 0o24 = 0o2400 bits, 0o2400 >> 5 = 40 decimal = 0o50, which
       prints as top-18 000000 and low-6 50; $L is word 0o10 = 0o1000
       bits, >>5 = 0o20.

  5. opcodes.MISC_CODES["Z"] 0b100 -> 0b101  (line 217), the Z opcode's
     BOTTOM bit
       12 ROWS, exactly the twelve Z rows and nothing else:
       006772.00, 007011.00 '000023.26 00' vs 000023.22 00
       007011.40, 007041.40 '007427.26 00' vs 007427.22 00
       007022.00, 007041.00 '000011.26 00' vs 000011.22 00
       007052.00, 007071.00, 007162.00, 007201.00
                            '007425.26 00' vs 007425.22 00
       007071.40           '000024.26 00' vs 000024.22 00
       007201.40           '000010.26 00' vs 000010.22 00
       OCTAL PAIR ONLY, 22 -> 26.  The three-bit misc code sits at IBM
       bits 19-21, inside the printed octal pair, so this moves the
       one digit no other injection here touches, and it moves it in
       every Z row across all four sub-tests while leaving the
       identically-addressed LX, SX and T rows alone.

  6. strap_asm.enc_branch_ind's address field -- "cat((addr19, 19), ..."
     -> "cat((addr19 & 0x7FFFE, 19), ..."  (line 355), i.e. BIT 18,
     the branch target's half-word select, forced to zero on
     BRANCH ON INDICATOR only
       8 ROWS, and they are EXACTLY the eight branch-on-indicator rows
       this file's bit-18 section lists as having bit 18 SET:
       007001.00 BXE '007002.32 C2' vs 007002.72 C2
       007003.00 BXE '007004.32 C2' vs 007004.72 C2
       007031.00 BXE '007032.32 C2' vs 007032.72 C2
       007033.00 BXE '007034.32 C2' vs 007034.72 C2
       007061.00 BXE '007062.32 C2' vs 007062.72 C2
       007063.00 BXE '007064.32 C2' vs 007064.72 C2
       007171.00 BXE '007172.32 C2' vs 007172.72 C2
       007173.00 BXE '007174.32 C2' vs 007174.72 C2
       The other BXE (at an ODD half-word, pair 32), every BXF, BRZ
       and BZRZ, and both B and BD forms stay green -- BXF/BRZ/BZRZ
       because their bit 18 is already zero, B/BD because they go
       through a different encoder.  This is the bit-18 decoding in
       the section above being CHECKED rather than merely asserted.

  7. strap_asm.enc_branch_or_misc's address field -- the same
     "& 0x7FFFE" (line 361), which is the OTHER branch encoder
       4 ROWS, exactly the four self-relative BD rows:
       007020.00 BD,$+.32 '007020.04 00' vs 007020.44 00
       007050.00 BD,$+.32 '007050.04 00' vs 007050.44 00
       007100.00 BD,$+.32 '007100.04 00' vs 007100.44 00
       007210.00 BD,$+.32 '007210.04 00' vs 007210.44 00
       Not one B, BD-to-a-label or Z row moves: every one of those
       names a WORD, so its bit 18 is already zero and masking it
       changes nothing.  Injections 6 and 7 together cover both
       encoders and all twelve bit-18-set rows in the file.

AND TWO INJECTIONS THIS BLOCK DOES *NOT* CATCH, both measured and
recorded, because a negative measured is worth more than a positive
assumed.  Both were confirmed to have APPLIED by printing the patched
line back from disk before the run:

  A. strap_asm.enc_transmit's A2 field -- "(addr19, 19)"
     -> "(addr19 & 0x7FFFE, 19)"  (line 383), i.e. BIT 50, the A2
     half-word select, forced to zero
       NO ROW CHANGES.  The run stays green: "ALL TESTS PASSED".
       The reason is arithmetic, not a gap in the transcription.  The
       three A2 operands in the whole of TEST 1 are I46D2 (007425.00,
       a word-aligned constant), $X3 (word 0o23) and $R (word 0o11).
       All three are WORD addresses, so bit 50 is already zero in all
       eight T rows here and in all sixteen across pp.101-108.  This
       is the same null both siblings record, now measured over three
       times as many transmit rows and over two operand kinds they do
       not have.  Transcribing 1E, 1F, 1H and 1I would not break it
       either: pp.104-108 were read for this file and their A2
       operands are the same three.  For TESTs 2A/2B/2C, pp.109-112,
       the statement is the SIBLINGS' first-hand reading and not
       mine -- their own rows show A2 = I46D1/I46D2/I46D4, all
       word-aligned.  Put together, routine 1246 contains no Transmit
       with an odd-half-word A2; only a deck that has one can catch
       this.

  B. strap_asm.enc_branch_on_bit's A1 field -- "(bitaddr24, 24)"
     -> "(bitaddr24 >> 5, 24)"  (line 395)
       NO ROW CHANGES.  The run stays green.
       The reason is coverage, not arithmetic: this block contains no
       BRANCH ON BIT row at all.  Recorded because enc_branch_on_bit
       and enc_transmit have textually IDENTICAL A1 clauses, and a
       reader patching "the cat() with bitaddr24 in it" will hit the
       wrong one -- as happened here on the first attempt, and the
       green run that followed is exactly the false null the method
       is meant to catch.  Injection 4 is the right line, 382.

NOT SETTLED, listed so that nothing above is taken for more than it is.
No check below depends on any of these.

  1. "IX CORE STG" in the p.103 error text ("-TRANSMIT 1 WD IX CORE
     STG TO") is the deck's own wording and differs from the heading's
     "IX STG"; pp.104 and 105 use "IX CORE STG" in their error text
     too.  Whether "CORE" distinguishes anything -- the index words
     live in the same 32-word fast bank as $L/$R on a 7030 -- is NOT
     established from any primary source here.  Transcribed as
     printed, unexplained.
  2. The mapping "INT MEM" = $L/$R and "IX STG" = $X3/$X4 is read off
     the headings against the operands in the same rows.  That is the
     deck's own pairing and it is what the octal proves ($L word 8,
     $R word 9, $X3 word 19, $X4 word 20).  Why the deck picked $X3
     and $X4 rather than any other index register, and why the
     receiving index register is always $X3 while the sending one is
     always $X4, is not stated anywhere read.
  3. TEST 1E/1F/1H/1I were read but not transcribed, so their row
     counts (44 each, by the same 24-words-spanned arithmetic) are
     computed rather than checked by the oracle.  Their labels
     I465/I4614, I466/I4615, I468/I4617, I469/I4618 were read off the
     label column at 400 dpi.
  4. Bits 50, 55, 56 and 57 are witnessed at ZERO only by every T row
     here, as in TEST 1A.  TESTs 2A/2B/2C, in the siblings, are where
     55, 56 and 57 vary; bit 50 varies nowhere in routine 1246.
  5. NOTHING HERE IS A REPO FIRST, and grep knocked out three claims
     an earlier draft of this file made.  Recorded in full, because
     every agent on this deck that has claimed a first has had grep
     eliminate it, and the eliminations are worth more than the claims:
       - NO MNEMONIC is a first.  Z, LX, SX, T, L(BU), BZRZ, SIC, B,
         KV, KC, BXE, SR, KVI, BXF, BRZ, BD and V+ each appear in
         between 3 and 138 other verify_*.py files.
       - $R AND $L ALREADY HAVE LISTING ROWS behind
         opcodes.SYSTEM_SYMBOLS.  verify_ax5b_1683_listing.py prints
         "Z,$R" -> 11.22 00 at 024372.40 and "SX,$X1,$R" -> 11.03 10;
         verify_fp_arith_f204c_listing.py prints "Z,$L" -> 10.22 00 at
         012617.00; verify_ax5b_162_test1b_listing.py has both
         "L(BU),$R" and "L(BU),$L".  The draft claimed those entries
         were unwitnessed.  They were not.
       - REGISTERS IN TRANSMIT'S ADDRESS FIELDS ARE NOT NEW EITHER.
         verify_ax5b_160_test6_listing.py prints "TI,1,$IND,$X1"
         (word 11 -> index word 1) eight times and "TI,1,I00O,$IND";
         verify_ax5b_16087_listing.py prints "TI,1,BIT0($X1),$IND".
     What survives the grep is narrow and is stated as such: these are
     the first PLAIN T rows -- direct count, unidirectional, bit 56 =
     0 -- with a register in either address field, every earlier
     register-address transmit in the repo being a TI (immediate
     count, bit 56 = 1); and $R and $L have not appeared in a TRANSMIT
     address field before.  Both are facts about one mnemonic's
     operands, not new kinds, and they are worth less than the verdict
     at the top of this docstring.  They also STRENGTHEN that verdict:
     at the level of the whole repository "more rows, not more kinds"
     is very nearly right, and the kind-change is a change within
     ROUTINE 1246, whose own transmits had only memory operands until
     these four pages.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_1246_memories.strap").read())

# ---------------------------------------------------------------------
# PDF p.101, 006772.00-007021.40.  TEST 1B, EXT MEM TO IX STG.
# The receiving operand is $X3, index register 3 = word 0o23, in
# TRANSMIT's A2 19-bit half-word field.
# ---------------------------------------------------------------------
TEST1B_ROWS = [
    ('006772.00', '23.22 00',    'I462 Z,$X3        "-TEST 1B,EXT MEM TO IX STG."'),
    ('006772.40', '13035.02 10', 'LX,$X1,I00O       (ext) the all-ones constant'),
    ('006773.00', '7427.03 10',  'SX,$X1,I46D4      all ones into the sending word'),
    ('006773.40', '13131.02 10', 'LX,$X1,BIT45      (ext) count field = 1'),
    ('006774.00', '7427.00 80 000023.02 20',
                                 'T,$X1,I46D4,$X3   A2 = $X3, an INDEX REGISTER'),
    ('006775.00', '23.00 80 000000.20 50',
                                 'L(BU),$X3         read the index register back'),
    ('006776.00', '7000.34 C0',  'BZRZ,$+2.0        OK when Result Zero is OFF'),
    ('006776.40', '1310.00 80',  'SIC,SEN           (ext) "-TRANSMIT 1 WD EXT MEM TO"'),
    ('006777.00', '1304.10 00',  'B,SERS            (ext) "-IX STG DROPS ALL BITS," TYPO'),
    ('006777.40', '7011.10 00',  'B,I4611           bit 18 = 0 -> 007011.00'),
    ('007000.00', '23.04 10',    'LX,$X2,$X3        the index register as an operand'),
    ('007000.40', '13035.04 90', 'KV,$X2,I00O       (ext) compare value fields'),
    ('007001.00', '7002.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007002.40'),
    ('007001.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007002.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 0-24."'),
    ('007002.40', '13035.05 90', 'KC,$X2,I00O       (ext) compare COUNT fields'),
    ('007003.00', '7004.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007004.40'),
    ('007003.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007004.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 28-45."'),
    ('007004.40', '22.05 70',    'SR,$X2,$X2        word 0o22 = index register 2'),
    ('007005.00', '777777.05 04', 'KVI,$X2,(8)777777.0   octal marker load-bearing'),
    ('007005.40', '7007.32 C2',  'BXE,$+1.32        bit 18 = 0 -> 007007.00'),
    ('007006.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007006.40', '1304.10 00',  'B,SERS            (ext) "-OF BITS 46 TO 63."'),
    ('007007.00', '22.04 10',    'LX,$X2,$X2'),
    ('007007.40', '7011.23 42',  'BXF,$+1.32        bit 18 = 0 -> 007011.00 = I4611'),
    ('007010.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES"'),
    ('007010.40', '1304.10 00',  'B,SERS            (ext) "-BIT 25."'),
    ('007011.00', '23.22 00',    'I4611 Z,$X3       "-CHECK FOR SPURIOUS BITS."'),
    ('007011.40', '7427.22 00',  'Z,I46D4'),
    ('007012.00', '13131.02 10', 'LX,$X1,BIT45      (ext)'),
    ('007012.40', '7427.00 80 000023.02 20',
                                 'T,$X1,I46D4,$X3   FULL WORD at an ODD half-word'),
    ('007013.40', '23.00 80 000000.20 50',
                                 'L(BU),$X3         also full-word at an odd half-word'),
    ('007014.40', '7016.34 C2',  'BRZ,$+1.32        OK when Result Zero is ON'),
    ('007015.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT PICKS"'),
    ('007015.40', '1304.10 00',  'B,SERS            (ext) "-UP SOME BITS 0-63."'),
    ('007016.00', '7017.10 00',  'B,$+1.0'),
    ('007016.40', '6772.04 00',  'BD,I462           bit 18 = 0 -> 006772.00'),
    ('007017.00', '1311.40 80',  'SIC,SENO+.32      (ext) pair 40 is a BIT OFFSET'),
    ('007017.40', '1301.10 00',  'B,SSW             (ext) "-TO SSIP."'),
    ('007020.00', '7020.44 00',  'BD,$+.32          BIT 18 SET -> 007020.40'),
    ('007020.40', '7422.32 10',  'LX,$X13,IC246     "-UPDATE CONTINUITY CHECK."'),
    ('007021.00', '13055.32 B0', 'V+,$X13,BIT1      (ext) TEST 1B"s continuity bit'),
    ('007021.40', '7422.33 10',  'SX,$X13,IC246'),
]

# ---------------------------------------------------------------------
# PDF p.102, 007022.00-007051.40.  TEST 1C, EXT MEM TO INT MEM.
# The receiving operand is $R, the accumulator's right half = word
# 0o11, in TRANSMIT's A2 field.
# ---------------------------------------------------------------------
TEST1C_ROWS = [
    ('007022.00', '11.22 00',    'I463 Z,$R         "-TEST 1C, EXT MEM TO INT MEM."'),
    ('007022.40', '13035.02 10', 'LX,$X1,I00O       (ext)'),
    ('007023.00', '7427.03 10',  'SX,$X1,I46D4'),
    ('007023.40', '13131.02 10', 'LX,$X1,BIT45      (ext) count field = 1'),
    ('007024.00', '7427.00 80 000011.02 20',
                                 'T,$X1,I46D4,$R    A2 = $R, INTERNAL MEMORY word 9'),
    ('007025.00', '11.00 80 000000.20 50',
                                 'L(BU),$R          read the accumulator half back'),
    ('007026.00', '7030.34 C0',  'BZRZ,$+2.0        OK when Result Zero is OFF'),
    ('007026.40', '1310.00 80',  'SIC,SEN           (ext) "-TRANSMIT 1 WD EXT MEM TO"'),
    ('007027.00', '1304.10 00',  'B,SERS            (ext) "-INT MEM DROPS ALL BITS."'),
    ('007027.40', '7041.10 00',  'B,I4612           bit 18 = 0 -> 007041.00'),
    ('007030.00', '11.04 10',    'LX,$X2,$R'),
    ('007030.40', '13035.04 90', 'KV,$X2,I00O       (ext)'),
    ('007031.00', '7032.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007032.40'),
    ('007031.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007032.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 0-24."'),
    ('007032.40', '13035.05 90', 'KC,$X2,I00O       (ext)'),
    ('007033.00', '7034.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007034.40'),
    ('007033.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007034.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 28-45."'),
    ('007034.40', '22.05 70',    'SR,$X2,$X2'),
    ('007035.00', '777777.05 04', 'KVI,$X2,(8)777777.0'),
    ('007035.40', '7037.32 C2',  'BXE,$+1.32        bit 18 = 0 -> 007037.00'),
    ('007036.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007036.40', '1304.10 00',  'B,SERS            (ext) "-OF BITS 46 TO 63."'),
    ('007037.00', '22.04 10',    'LX,$X2,$X2'),
    ('007037.40', '7041.23 42',  'BXF,$+1.32        bit 18 = 0 -> 007041.00 = I4612'),
    ('007040.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES"'),
    ('007040.40', '1304.10 00',  'B,SERS            (ext) "-BIT 25."'),
    ('007041.00', '11.22 00',    'I4612 Z,$R        "-CHECK FOR SPURIOUS BITS."'),
    ('007041.40', '7427.22 00',  'Z,I46D4'),
    ('007042.00', '13131.02 10', 'LX,$X1,BIT45      (ext)'),
    ('007042.40', '7427.00 80 000011.02 20',
                                 'T,$X1,I46D4,$R    FULL WORD at an ODD half-word'),
    ('007043.40', '11.00 80 000000.20 50',
                                 'L(BU),$R'),
    ('007044.40', '7046.34 C2',  'BRZ,$+1.32        OK when Result Zero is ON'),
    ('007045.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT PICKS"'),
    ('007045.40', '1304.10 00',  'B,SERS            (ext) "-UP SOME BITS 0-63."'),
    ('007046.00', '7047.10 00',  'B,$+1.0'),
    ('007046.40', '7022.04 00',  'BD,I463           bit 18 = 0 -> 007022.00'),
    ('007047.00', '1311.40 80',  'SIC,SENO+.32      (ext) pair 40 is a BIT OFFSET'),
    ('007047.40', '1301.10 00',  'B,SSW             (ext) "-TO SSIP."'),
    ('007050.00', '7050.44 00',  'BD,$+.32          BIT 18 SET -> 007050.40'),
    ('007050.40', '7422.32 10',  'LX,$X13,IC246     "-UPDATE CONTINUITY CHECK."'),
    ('007051.00', '13056.32 B0', 'V+,$X13,BIT2      (ext) TEST 1C"s continuity bit'),
    ('007051.40', '7422.33 10',  'SX,$X13,IC246'),
]

# ---------------------------------------------------------------------
# PDF p.103, 007052.00-007101.40.  TEST 1D, IX STG TO EXT MEM.
# The SENDING operand is $X4 = word 0o24, in TRANSMIT's A1 24-bit BIT
# field -- the mirror of TEST 1B.
# ---------------------------------------------------------------------
TEST1D_ROWS = [
    ('007052.00', '7425.22 00',  'I464 Z,I46D2      "-TEST 1D, IX STG TO, EXT MEM." TYPO'),
    ('007052.40', '13035.02 10', 'LX,$X1,I00O       (ext)'),
    ('007053.00', '24.03 10',    'SX,$X1,$X4        all ones into INDEX REGISTER 4'),
    ('007053.40', '13131.02 10', 'LX,$X1,BIT45      (ext) count field = 1'),
    ('007054.00', '24.00 80 007425.02 20',
                                 'T,$X1,$X4,I46D2   A1 = $X4, a register BIT address'),
    ('007055.00', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2       read the destination back'),
    ('007056.00', '7060.34 C0',  'BZRZ,$+2.0        OK when Result Zero is OFF'),
    ('007056.40', '1310.00 80',  'SIC,SEN           (ext) "-TRANSMIT 1 WD IX CORE STG TO"'),
    ('007057.00', '1304.10 00',  'B,SERS            (ext) "-EXT MEM DROPS ALL BITS."'),
    ('007057.40', '7071.10 00',  'B,I4613           bit 18 = 0 -> 007071.00'),
    ('007060.00', '7425.04 10',  'LX,$X2,I46D2'),
    ('007060.40', '13035.04 90', 'KV,$X2,I00O       (ext)'),
    ('007061.00', '7062.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007062.40'),
    ('007061.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007062.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 0-24."'),
    ('007062.40', '13035.05 90', 'KC,$X2,I00O       (ext)'),
    ('007063.00', '7064.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007064.40'),
    ('007063.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007064.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 28-45."'),
    ('007064.40', '22.05 70',    'SR,$X2,$X2'),
    ('007065.00', '777777.05 04', 'KVI,$X2,(8)777777.0'),
    ('007065.40', '7067.32 C2',  'BXE,$+1.32        bit 18 = 0 -> 007067.00'),
    ('007066.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007066.40', '1304.10 00',  'B,SERS            (ext) "-OF BITS 46 TO 63."'),
    ('007067.00', '22.04 10',    'LX,$X2,$X2'),
    ('007067.40', '7071.23 42',  'BXF,$+1.32        bit 18 = 0 -> 007071.00 = I4613'),
    ('007070.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES"'),
    ('007070.40', '1304.10 00',  'B,SERS            (ext) "-BIT 25."'),
    ('007071.00', '7425.22 00',  'I4613 Z,I46D2     "-CHECK FOR SPURIOUS BITS."'),
    ('007071.40', '24.22 00',    'Z,$X4             zero the INDEX REGISTER'),
    ('007072.00', '13131.02 10', 'LX,$X1,BIT45      (ext)'),
    ('007072.40', '24.00 80 007425.02 20',
                                 'T,$X1,$X4,I46D2   FULL WORD at an ODD half-word'),
    ('007073.40', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2'),
    ('007074.40', '7076.34 C2',  'BRZ,$+1.32        OK when Result Zero is ON'),
    ('007075.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT PICKS"'),
    ('007075.40', '1304.10 00',  'B,SERS            (ext) "-UP SOME BITS 0-63."'),
    ('007076.00', '7077.10 00',  'B,$+1.0'),
    ('007076.40', '7052.04 00',  'BD,I464           bit 18 = 0 -> 007052.00'),
    ('007077.00', '1311.40 80',  'SIC,SENO+.32      (ext) pair 40 is a BIT OFFSET'),
    ('007077.40', '1301.10 00',  'B,SSW             (ext) "-TO SSIP."'),
    ('007100.00', '7100.44 00',  'BD,$+.32          BIT 18 SET -> 007100.40'),
    ('007100.40', '7422.32 10',  'LX,$X13,IC246     "-UPDATE CONTINUITY CHECK."'),
    ('007101.00', '13057.32 B0', 'V+,$X13,BIT3      (ext) TEST 1D"s continuity bit'),
    ('007101.40', '7422.33 10',  'SX,$X13,IC246'),
]

# ---------------------------------------------------------------------
# PDF p.106, 007162.00-007211.40.  TEST 1G, INT MEM TO EXT MEM.
# The SENDING operand is $L, the accumulator's left half = word 0o10,
# in TRANSMIT's A1 24-bit BIT field.
# ---------------------------------------------------------------------
TEST1G_ROWS = [
    ('007162.00', '7425.22 00',  'I467 Z,I46D2      "-TEST 1G, INT MEM TO EXT MEM."'),
    ('007162.40', '13035.02 10', 'LX,$X1,I00O       (ext)'),
    ('007163.00', '10.03 10',    'SX,$X1,$L         all ones into INTERNAL word 8'),
    ('007163.40', '13131.02 10', 'LX,$X1,BIT45      (ext) count field = 1'),
    ('007164.00', '10.00 80 007425.02 20',
                                 'T,$X1,$L,I46D2    A1 = $L, a register BIT address'),
    ('007165.00', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2'),
    ('007166.00', '7170.34 C0',  'BZRZ,$+2.0        OK when Result Zero is OFF'),
    ('007166.40', '1310.00 80',  'SIC,SEN           (ext) "-TRANSMIT 1 WD INT MEM TO"'),
    ('007167.00', '1304.10 00',  'B,SERS            (ext) "-EXT MEM DROPS ALL BITS."'),
    ('007167.40', '7201.10 00',  'B,I4616           bit 18 = 0 -> 007201.00'),
    ('007170.00', '7425.04 10',  'LX,$X2,I46D2'),
    ('007170.40', '13035.04 90', 'KV,$X2,I00O       (ext)'),
    ('007171.00', '7172.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007172.40'),
    ('007171.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007172.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 0-24."'),
    ('007172.40', '13035.05 90', 'KC,$X2,I00O       (ext)'),
    ('007173.00', '7174.72 C2',  'BXE,$+1.32        BIT 18 SET -> 007174.40'),
    ('007173.40', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007174.00', '1304.10 00',  'B,SERS            (ext) "-OF BITS 28-45."'),
    ('007174.40', '22.05 70',    'SR,$X2,$X2'),
    ('007175.00', '777777.05 04', 'KVI,$X2,(8)777777.0'),
    ('007175.40', '7177.32 C2',  'BXE,$+1.32        bit 18 = 0 -> 007177.00'),
    ('007176.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('007176.40', '1304.10 00',  'B,SERS            (ext) "-OF BITS 46 TO 63."'),
    ('007177.00', '22.04 10',    'LX,$X2,$X2'),
    ('007177.40', '7201.23 42',  'BXF,$+1.32        bit 18 = 0 -> 007201.00 = I4616'),
    ('007200.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT LOSES"'),
    ('007200.40', '1304.10 00',  'B,SERS            (ext) "-BIT 25."'),
    ('007201.00', '7425.22 00',  'I4616 Z,I46D2     "-CHECK FOR SPURIOUS BITS."'),
    ('007201.40', '10.22 00',    'Z,$L              zero INTERNAL word 8'),
    ('007202.00', '13131.02 10', 'LX,$X1,BIT45      (ext)'),
    ('007202.40', '10.00 80 007425.02 20',
                                 'T,$X1,$L,I46D2    FULL WORD at an ODD half-word'),
    ('007203.40', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2'),
    ('007204.40', '7206.34 C2',  'BRZ,$+1.32        OK when Result Zero is ON'),
    ('007205.00', '1310.00 80',  'SIC,SEN           (ext) "-ABOVE TYPE TRANSMIT PICKS"'),
    ('007205.40', '1304.10 00',  'B,SERS            (ext) "-UP SOME BITS 0-63."'),
    ('007206.00', '7207.10 00',  'B,$+1.0'),
    ('007206.40', '7162.04 00',  'BD,I467           bit 18 = 0 -> 007162.00'),
    ('007207.00', '1311.40 80',  'SIC,SENO+.32      (ext) pair 40 is a BIT OFFSET'),
    ('007207.40', '1301.10 00',  'B,SSW             (ext) "-TO SSIP."'),
    ('007210.00', '7210.44 00',  'BD,$+.32          BIT 18 SET -> 007210.40'),
    ('007210.40', '7422.32 10',  'LX,$X13,IC246     "-UPDATE CONTINUITY CHECK."'),
    ('007211.00', '13062.32 B0', 'V+,$X13,BIT6      (ext) TEST 1G"s continuity bit'),
    ('007211.40', '7422.33 10',  'SX,$X13,IC246'),
]

# I462 and I467 are the first label after an SLC and are ANCHORS, not
# evidence -- see the docstring's witness tiering.  The other six fall
# out of the location counter and are real address checks.  The
# constants block is INPUT here and is deliberately not asserted.
SYMBOLS = {
    'I462': '006772.00', 'I4611': '007011.00',
    'I463': '007022.00', 'I4612': '007041.00',
    'I464': '007052.00', 'I4613': '007071.00',
    'I467': '007162.00', 'I4616': '007201.00',
}

if __name__ == "__main__":
    fails = check_rows(prog, [], SYMBOLS, label='1246 ')
    fails += check_rows(prog, TEST1B_ROWS, label='1246 T1B  ')
    fails += check_rows(prog, TEST1C_ROWS, label='1246 T1C  ')
    fails += check_rows(prog, TEST1D_ROWS, label='1246 T1D  ')
    fails += check_rows(prog, TEST1G_ROWS, label='1246 T1G  ')
    finish(fails)
