#!/usr/bin/env python3
"""verify_ax4b_1246_transmit_swap_listing.py -- jb_ax4b "I-BOX 4",
routine 1246 ("TEST TRANSMIT AND SWAP"), checked against the machine
code the listing prints beside each source line.  Four blocks, 102
printed rows, plus 17 symbol-table assertions:

  PDF p.99   006736.00-006740.40   the routine's preamble       6 rows
  PDF p.100  006742.00-006771.40   TEST 1A, EXT MEM TO EXT MEM 44 rows
  PDF p.112  007372.40-007421.40   TEST 2C, the modifier bit   41 rows
  PDF p.112  007422.00-007433.00 ) the routine's constants     11 rows
  PDF p.113  007434.00            )

WHERE THIS STOPS, precisely.  TEST 1B ("EXT MEM TO IX STG", label
I462/I4611) begins at octal 006772.00 on PDF p.101 and is NOT
transcribed.  Sub-tests 1B through 1I occupy one listing page each,
PDF pp.101-108, 006772.00 through 007271.40, and TESTs 2A and 2B
occupy PDF pp.109-111, 007272.00 through 007372.00.  All of those are
left for a later pass.  Their headings were read first-hand so that
this statement is not a guess:

    PDF p.109  -TEST 2. CHECK MODIFIER BITS.
               -TEST 2A.
      I4620    -TEST FORWARD-BACKWARD MODIFIER,     007272.00
               -START WITH FOWARD OPERATION.
    PDF p.111  -TEST 2B.
      I4623    -TEST DIRECT-INNEDIATE MODIFIER.
    PDF p.112  -TEST 2C.
      I4626    -TEST TRANSMIT-SWAP MODIFIER.        007372.40

("FOWARD" and "INNEDIATE" are the page's own spellings, quoted as
printed.)  TEST 2A is where I46XW1/I46XW2/I46XW3 -- the three index
words transcribed below and checked but named by no transcribed row --
are actually USED: p.109 loads them into $X1/$X2/$X3 and stores them
into I46D4/I46D5/I46D6.  TEST 2B is where TI reappears, with BIT44
rather than BIT45 for its count.  The four blocks above are contiguous in
themselves and self-consistent: every label the transcribed rows name,
except the twelve SYN'd externals listed below, is defined inside
them.

CITED BY PDF PAGE, AND ONLY BY PDF PAGE.  jb_ax4b's LISTING sheets
carry no printed folio anywhere -- pp.99, 100, 112 and 113 were
rendered at 400 and 600 dpi for this transcription and their top
strip, bottom strip and both edges read.  The front WRITE-UP is
different: it does print "-1-", "-2-", and where this file quotes the
write-up it cites those printed numbers.  Reference Manual 22-6530-2
is cited by PRINTED page, and PDF page = printed page + 3 for it, the
offset verify_ax5b_162_test3a_listing.py already records.  C22-6531's
offset is +1 (printed p.10 is PDF p.11, footer "10").

=====================================================================
THE BANNER, PDF p.99, read first-hand at 600 dpi, VERBATIM -- and the
two "TWO BASIC ROUTINES" lines are a CORRECTION to the brief for this
transcription, which omitted them:

    ----1246---TEST TRANSMIT AND SWAP.

    -THIS TEST IS COMPOSED OF TWO BASIC
    -ROUTINES WHICH CHECK THE FOLLOWING.

            -1. CHECKS THE NINE POSSIBILITIES
                -OF ADDRESS COMBINATIONS.

            -2. CHECKS THE THREE MODIFIER BITS,

                -A. FORWARD OR BACKWARD.
                -B. DIRECT OR IMMEDIATE
                -C. TRANSMIT OR SWAP.

EVERY ERROR MESSAGE IN THE TRANSCRIBED RANGE, VERBATIM, with the octal
location of the SIC that reports it.  Each is a two-half-word pair,
"SIC,SEN" then "B,SERS", and the printed comment sits beside the pair.

  PDF p.100, TEST 1A:
    006746.40  -TRANSMIT 1 WD EXT MEM TO
               -EXT MEM DROPS ALL BITS.
    006751.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 0-24.
    006753.40  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 28-45.
    006756.00  -ABOVE TYPE TRANSMIT LOSES SOME
               -OF BITS 46 TO 63.
    006760.00  -ABOVE TYPE TRANSMIT LOSES
               -BIT 25.
    006765.00  -ABOVE TYPE TRANSMIT PICKS
               -UP SOME BITS 0-63.

  PDF p.112, TEST 2C:
    007377.00  -TRANSMIT DESTROYS ORIGINAL WORD
               -AND THEREFORE ACTS LIKE SWAP.
    007402.00  -RECEIVING LOCATION DOES NOT GET
               -FIRST WORD FROM SENDING LOCN.
    007407.40  -SWAP FAILS TO ALTER ORIGINAL WD
               -AND THEREFORE ACTS LIKE TRANSMIT
    007412.40  -RECEIVING LOCATION DOES NOT GET
               -FIRST WORD FROM SENDING LOCN.
    007421.00  -CONTINUITY ERROR.

  (The "-AND THEREFORE ACTS LIKE TRANSMIT" line really does end
  without a period on the page; its three siblings end with one.)

Non-error printed comments in range, also verbatim: "-UPDATE IDENT.",
"-PRINT ID.", "-TEST 1. NINE ADDRESS COMBINATIONS.", "-TEST 1A, EXT
MEM TO EXT MEM.", "-CHECK FOR SPURIOUS BITS.", "-TO SSIP.", "-UPDATE
CONTINUITY CHECK.", "-TEST 2C.", "-TEST TRANSMIT-SWAP MODIFIER.",
"-UPDATE CONTINUITY.", "-CONTINUITY REG 1246."

BRANCH POLARITY, because an error message names the ANOMALY.  B<IND>
branches when the indicator is ON, BZ<IND> when it is OFF; so the
BRANCH is the OK path and the FALL-THROUGH is the error pair.  At
006746.00 "BZRZ,$+2.0" takes the OK path when Result Zero is OFF --
the all-ones word did arrive -- and falls into "TRANSMIT ... DROPS ALL
BITS." when it is ON.  At 006764.40 "BRZ,$+1.32" is the mirror image:
OK when Result Zero is ON, error "PICKS UP SOME BITS 0-63." when it is
off.  Nothing here requires an indicator to be set; the requirement is
always the branch.

=====================================================================
T AND SWAP: THE FIRST WITNESSES IN THIS REPOSITORY FOR EITHER.

Before this file, `grep` over every verify_*.py found exactly one
transcribed TRANSMIT-family row anywhere in the project, and it was
TI: jb_ax5b p.45's "TI,1,BIT0(X1),$IND" and "TI,1,BIT0(X1),$MASK"
(verify_ax5b_16087_listing.py), plus the same TI form re-used in
verify_ax5b_160105_listing.py and sixteen times in
verify_ax5b_160s1_listing.py.  opcodes.TRANSMIT_CODES said so in its
own comment: "WITNESSED: only TI. ... The other seven are from the
card alone and have no listing row in this project yet."  Plain T,
TB, TBI and all four SWAP forms had none.  This block supplies T
(three rows) and SWAP (one row), so three of the eight mnemonics are
now witnessed and five -- TB, TBI, SWAPI, SWAPB, SWAPBI -- remain
card-only.

T AND SWAP ARE THE ONLY FIRSTS HERE, and that was measured, not
assumed: every other mnemonic in the block was grepped across the
other verify_*.py files before the claim was written.  KC already has
rows in verify_ibox4_prog_ix_v_listing.py (011221.00, "KC,$X1,BIT17");
BXF already has rows in verify_ibox1_bind_listing.py (004024.00) and
verify_ibox1_listing.py (005443.40); SR, KV, KVI, BXE, BRZ, BZRZ, V+,
Z, LX, SX, B, BD, SIC and L(BU) all appear in between two and
twenty-seven other files.  An earlier draft of this paragraph called
KC and BXF firsts; the grep says otherwise and the grep wins.

AND THE MATCHED PAIR IS THE ENCODING ORACLE.  Two rows on PDF p.112,
thirty half-words apart, same J, same A1, same A2, same indices:

    007374.40  T,$X1,I46D1,I46D4     7424.00 80 007427.02 20
    007405.00  SWAP,$X1,I46D1,I46D4  7424.00 80 007427.02 60

One printed hex digit differs, 2 -> 6, and that is IBM bit 57.
Reference Manual printed p.30 (PDF p.33, footer "30  IBM 7030"), read
first-hand: "The choice between unidirectional and bidirectional
transmission is specified by modifier bit 57.  A zero specifies
unidirectional transmission; a one specifies bidirectional
transmission."  The LISTING supplies both sides of that bit, from one
page, with every other field held constant -- which is a stronger
oracle than the RNX pair in verify_ibox4_rnx_nop_listing.py, where the
two rows differ in their operands as well.

The full decomposition of the SWAP word against pocket card X22-6533's
"TRANSMIT OPERATIONS" diagram (the one opcodes.TRANSMIT_CODES carries):

    |   ADDRESS   |1000| I |   ADDRESS   | J |FD|BI|10| I |
    0            18  24   28  32          51  55    58 60 63

  bits 0-23   = 007424.00 as a BIT address       -> "7424.00"
  bits 24-27  = 1000, the literal shared with SIC and BRANCH ON BIT
  bits 28-31  = I1 = 0                           -> hex "80"
  bits 32-50  = 007427.00 as a HALF-WORD address -> "007427" + bit 50
  bits 51-54  = J = 1, index register 1          )
  bit  55     = 0, FORWARD                       ) -> octal pair "02"
  bit  56     = 0, DIRECT count                  )
  bit  57     = 1, SWAP (0 = Transmit)           )
  bits 58-59  = 10, the format literal           ) -> hex "60"
  bits 60-63  = I2 = 0                           )

and all three of the banner's modifier bits are therefore READ OFF
these two rows: bit 55 = 0 forward, bit 56 = 0 direct, bit 57 the one
that moves.  The deck's own TEST 2A and 2B (PDF pp.109-111, not
transcribed) are where bits 55 and 56 are exercised as VARIABLES; here
they are witnessed only at zero.

THE COUNT COMES FROM BIT45, and that is not a guess either.  Every
T/SWAP row in this block is preceded by "LX,$X1,BIT45", and BIT45 is
the common constant at 013131.00 with bit 45 set.  Reference Manual
printed p.30: "In direct count operations, the field J, bits 51-54,
specifies an index register.  The count field, bits 28-45, of the
index word in this register is used as a full word count."  Bit 45 is
the low-order bit of that field, so X1's count is one and the
instruction moves one word -- which is what the printed comment
"-TRANSMIT 1 WD EXT MEM TO EXT MEM" says in English.

=====================================================================
BIT-18 SELF-CHECKS.  The listing prints each half-word as bits 0-17 in
six octal digits, "." , bits 18-23 in two octal digits, then bits
24-31 in two hex digits.  Bit 18 is the TOP bit of the octal pair and
selects the half-word of a 19-bit branch address.  Every row below
whose operand is a label or a self-relative was decoded that way and
read back against the page's own label column.

  PREAMBLE (PDF p.99):
    006740.40  BD,I461       -> 6742.04 00.  04 = 000100, bit 18 = 0
               -> 006742.00, where PDF p.100 prints the label I461.

  TEST 1A (PDF p.100):
    006746.00  BZRZ,$+2.0    -> 6750.34 C0.  34 = 011100, bit 18 = 0
               -> 006750.00, and 006746.00 + 2 words = 006750.00.
    006747.40  B,I4610       -> 6761.10 00.  10 = 001000, bit 18 = 0
               -> 006761.00, where p.100 prints the label I4610.
    006751.00  BXE,$+1.32    -> 6752.72 C2.  72 = 111010, BIT 18 = 1
               -> 006752.40, and 006751.00 + 1 word + 32 bits is
               006752.40.
    006753.00  BXE,$+1.32    -> 6754.72 C2.  BIT 18 = 1 -> 006754.40.
    006755.40  BXE,$+1.32    -> 6757.32 C2.  32 = 011010, bit 18 = 0
               -> 006757.00 (the odd-half start carries the +32 into
               the next word, so this one does NOT set bit 18).
    006757.40  BXF,$+1.32    -> 6761.23 42.  23 = 010011, bit 18 = 0
               -> 006761.00 = I4610.
    006764.40  BRZ,$+1.32    -> 6766.34 C2.  bit 18 = 0 -> 006766.00.
    006766.00  B,$+1.0       -> 6767.10 00.  bit 18 = 0 -> 006767.00.
    006766.40  BD,I461       -> 6742.04 00.  04 = 000100, bit 18 = 0
               -> 006742.00, where p.100 prints the label I461.
    006770.00  BD,$+.32      -> 6770.44 00.  44 = 100100, BIT 18 = 1
               -> 006770.40, and 006770.00 + 32 bits = 006770.40.

  TEST 2C (PDF p.112) -- five rows with BIT 18 SET, against three in
  TEST 1A:
    007376.40  BRZ,$+2.0     -> 7400.74 C2.  74 = 111100, BIT 18 = 1
               -> 007400.40, and 007376.40 + 2 words = 007400.40.
    007400.00  B,I4627       -> 7403.10 00.  bit 18 = 0 -> 007403.00,
               where p.112 prints the label I4627.
    007401.40  BRZ,$+1.32    -> 7403.34 C2.  bit 18 = 0 -> 007403.00.
    007407.00  BZRZ,$+2.0    -> 7411.34 C0.  bit 18 = 0 -> 007411.00.
    007410.40  B,I4628       -> 7413.50 00.  50 = 101000, BIT 18 = 1
               -> 007413.40, where p.112 prints the label I4628.
    007412.00  BRZ,I4628     -> 7413.74 C2.  74 = 111100, BIT 18 = 1
               -> 007413.40 = I4628.
    007413.40  B,$+1.0       -> 7414.50 00.  BIT 18 = 1 -> 007414.40.
    007414.00  BD,I4626      -> 7372.44 00.  44 = 100100, BIT 18 = 1
               -> 007372.40, where p.112 prints the label I4626.
    007415.40  BD,$+.32      -> 7416.04 00.  bit 18 = 0 -> 007416.00.
    007421.40  BD,I48        -> 7435.04 00.  bit 18 = 0 -> 007435.00,
               where PDF p.113 prints routine 1248's label I48.

AND THE NON-BRANCH LABEL ROWS, because the brief asks for EVERY row
whose operand is a label and the list above is branches only.  A
DirIndex row's 19-bit address field is the same field with the same
bit 18, and sixteen rows here put a label in it:
    "Z,I46D2" (006742.00, 006761.00), "SX,$X1,I46D4" (006743.00,
    007373.40, 007404.00), "Z,IC246" (006740.00), "LX,$X2,I46D2"
    (006750.00), "Z,I46D4" (006761.40), "Z,I46D1" (007372.40,
    007403.00), "LX,$X13,IC246" (006770.40, 007416.00, 007417.40),
    "SX,$X13,IC246" (006771.40, 007417.00), "KV,$X13,ICK246"
    (007420.00)
and in EVERY one of them bit 18 is ZERO: the printed pairs are 22,
03, 04, 32 and 33, all less than octal 40, so the pair's top bit --
which IS bit 18 -- is zero in each.  The reason
is arithmetic, not luck: every label they name is a full WORD in the
routine's own constant block (007422.00-007434.00, all .00
addresses), so the half-word select cannot be anything else.  Bit 18
is witnessed at ONE only by the branches listed above; the DirIndex
rows witness it at zero.  Said out loud rather than left implied.

TWO ROW SHAPES IN THIS BLOCK ARE NOT HALF-WORD SELECTS AT ALL, and
both need saying:

  1. SIC's operand is a 24-bit BIT address in bits 0-23 (Reference
     Manual printed p.41), so its octal pair is a bit OFFSET inside the
     word.  "SIC,RET" at 006737.00 prints 1306.40 80: the 40 is bit
     32 of word 001306, not bit 18 and a half-word select.  Likewise
     "SIC,SENO+.32" at 006767.00 and 007414.40 (1311.40 80).

  2. T and SWAP carry BOTH kinds in ONE instruction word, which is
     what makes them worth transcribing.  The FIRST group holds A1, a
     24-bit BIT address, so "7424.00" + pair "00" is word 007424 bit
     0 and its octal pair is a bit offset -- the SIC caveat again.
     The SECOND group holds A2, a 19-bit HALF-WORD address at bits
     32-50, and there the half-word select is BIT 50, the top bit of
     the SECOND group's octal pair.  So the bit-18 rule applies to
     neither group of a T/SWAP row: the first has no half-word select
     and the second's lives twelve bits away.

  AND A MEASURED NULL FOLLOWS FROM THAT.  All four T/SWAP rows print
  "02" for bits 50-55, so bit 50 = 0 in every one of them.  The reason
  is arithmetic, not luck: I46D2 and I46D4 are word-aligned constants,
  so their half-word select is zero, and this block contains no
  Transmit whose A2 is odd.  Bit 50 is therefore witnessed at ZERO
  only; nothing here would catch an encoder that dropped it.  Same
  shape as the LRI null recorded in verify_ibox4_rnx_nop_listing.py.

=====================================================================
WITNESS TIERING.  EVERY SYN IS AN INPUT, NOT A WITNESS.

  SYN'd (address supplied to the assembler from the very rows that
  print it -- these rows check opcode and modifier bits only):
      DPET13 001437.00, RET 001306.40, IDF1 001443.00, SEN 001310.00,
      SENO 001311.00, SERS 001304.00, SSW 001301.00, I00O 013035.00,
      BIT0 013054.00, BIT11 013067.00, BIT45 013131.00, I48 007435.00.
  I48 has a second, independently read page behind it -- PDF p.113
  prints "I48" in its own label column at 007435.00 -- and I00O sits
  between I00Z (013034.00) and I00VO (013036.00), which this repo
  already reads off PDF p.190.  That is corroboration; it does not
  turn an input into a witness.
  I46ID is also a SYN, for a different reason: PDF p.99 prints its
  location, 006741.00, and NO machine code, so the location counter is
  SLC'd across it rather than a word being invented.  It is asserted
  nowhere below.

  ANCHORS, not witnesses -- each is the first label after an SLC, so
  checking it checks this transcription against the number this
  transcription handed the SLC:
      I46 006736.00, I461 006742.00, I4626 007372.40, IC246 007422.00.
  They are asserted below because a wrong one would silently mis-place
  a whole block, not because they are evidence.  The same caveat
  verify_ibox4_rnx_nop_listing.py makes about I4412.

  GENUINE WITNESSES -- defined inside the transcribed range at
  addresses the location counter computes, and named by rows whose
  printed address field therefore checks placement:
      I4610 006761.00   (named by "B,I4610" at 006747.40)
      I4627 007403.00   (named by "B,I4627" at 007400.00)
      I4628 007413.40   (named by "B,I4628" at 007410.40 and
                         "BRZ,I4628" at 007412.00 -- and BOTH have
                         bit 18 set)
      ICK246 007423.00  (named by "KV,$X13,ICK246" at 007420.00)
      I46D1 007424.00   (named by the T at 007374.40 and the SWAP at
                         007405.00, in the A1 BIT-address field, and
                         by four Z/L(BU) rows)
      I46D2 007425.00   (named by the two TEST 1A T rows in the A2
                         HALF-WORD field, and by four more rows)
      I46D4 007427.00   (named in the A1 field twice and the A2 field
                         twice -- once in each kind of address field,
                         which is why it is the strongest of them)
      I46D3, I46D5, I46D6, I46XW1, I46XW2, I46XW3 -- defined by the
                         location counter, checked by the symbol
                         assertions below, named by no transcribed row.
  IC246 appears on both lists: it is SLC-anchored, but "Z,IC246" at
  006740.00 is four blocks away from that SLC and reaches it through
  the assembler's symbol table, so a wrong SLC shows up there too.

=====================================================================
SUBSTITUTIONS, four, all mechanical, none touching a bit; the .strap
header states them at length.  "%8@" -> "(8)"; "L%BU@" -> "L(BU)";
T/SWAP's J field "$X1" -> "1" (Reference Manual printed p.30: "the
field J, bits 51-54, specifies an index register", and the printed J
field IS 1, so the substitution is CHECKED by the oracle, not
assumed); and the un-encodable ident row is SLC'd across, as above.

LABELS ARE LETTER-I, NOT DIGIT-1, AND THAT CORRECTS THIS REPOSITORY.
At 600 dpi this printer's letter I is a bare stroke 9-13 px wide and
its digit 1 has a top-left flag and measures 31-34 px.  Both occur in
ONE printed row on PDF p.99 -- "BD,I461" segments as I(10) 4(47) 6(42)
1(31) -- so the reading rests on one ink and one pass, not a
cross-page comparison.  C22-6531 printed p.10 (PDF p.11, footer "10")
says why: "A symbol is any sequence of six or fewer alphabetic and
numeric characters conforming to the following conditions:  1. It
contains only alphameric characters.  2. Its first character is
specifically alphabetic."  A STRAP-1 label cannot begin with a digit.
Earlier files in this repo read these as digits and added an "L"
prefix (L14412, L144D1, L146); no check was wrong, because all of them
were SYN'd externals or anchors, but the reading was.  No L-prefix
appears here.

OTHER GLYPHS SETTLED BY MEASUREMENT rather than house style (letter O
49-51 px, digit 0 42-45 px at 600 dpi): I00O ends in a 49 px letter O;
SENO's O is round and wide, letter O; I4610 ends in a 40 px DIGIT
zero; I46ID has 10-13 px letter I at positions 1 and 4 while I461 one
row above has a 31 px digit 1 at position 4.

=====================================================================
PROVEN DISCRIMINATING.  Observed failure sets, never predicted.  Every
injection was made with __pycache__ removed on BOTH sides of the run,
and opcodes.py and strap_asm.py were restored afterwards from
byte-for-byte copies taken before the first one -- both md5s matched
the originals and `git diff` was empty at the end.  The first five are
aimed at the T/SWAP modifier field and move BOTH printed columns
between them; the sixth is aimed at the A1/A2 address-kind asymmetry
this file's format note asserts.

  opcodes.TRANSMIT_CODES["SWAP"] (0,0,1) -> (0,0,0)  -- bit 57, swap
      007405.00  SWAP -> "007424.00 80 007427.02 20"      (1 row)
      HEX BYTE ONLY, 60 -> 20, and it makes the SWAP row print
      EXACTLY what the T row fourteen rows earlier on the same page
      prints.  This is the matched pair proving itself: the only thing
      separating Transmit from Swap in this deck is that digit.

  opcodes.TRANSMIT_CODES["T"] (0,0,0) -> (0,0,1)     -- bit 57, the
  other way
      006744.00  T    -> "007427.00 80 007425.02 60"      (3 rows)
      006762.40  T    -> "007427.00 80 007425.02 60"
      007374.40  T    -> "007424.00 80 007427.02 60"
      HEX BYTE ONLY, 20 -> 60, three rows on two different pages.

  opcodes.TRANSMIT_CODES["T"] (0,0,0) -> (0,1,0)     -- bit 56, the
  direct/immediate count bit
      006744.00  T    -> "007427.00 80 007425.02 A0"      (3 rows)
      006762.40  T    -> "007427.00 80 007425.02 A0"
      007374.40  T    -> "007424.00 80 007427.02 A0"
      HEX BYTE ONLY, 20 -> A0.  Bit 56 is the top bit of the byte.

  opcodes.TRANSMIT_CODES["T"] (0,0,0) -> (1,0,0)     -- bit 55, the
  forward/backward bit
      006744.00  T    -> "007427.00 80 007425.03 20"      (3 rows)
      006762.40  T    -> "007427.00 80 007425.03 20"
      007374.40  T    -> "007424.00 80 007427.03 20"
      OCTAL PAIR ONLY, 02 -> 03, hex byte unchanged at 20.  Bit 55 is
      the LAST bit of bits 50-55 and so the bottom of the octal pair --
      the same field the other two injections cannot reach.  Between
      these three the whole "ab" modifier pair and the swap bit are
      exercised, in both printed columns.

  opcodes.DIR_INDEX_CODES["KC"] 0b11001 -> 0b01001   -- the code's
  TOP bit
      006752.40  KC,$X2,I00O -> "013035.04 90"            (1 row)
      OCTAL PAIR ONLY, 05 -> 04, because the top bit of the 5-bit
      direct-index code is IBM bit 23 and bit 23 is the bottom bit of
      the printed octal pair.  Note WHAT it collides with: 0b01001 is
      DIR_INDEX_CODES["KV"], and the KV row three lines up prints
      exactly "13035.04 90".  A block that checked only the opcode
      NAME could not tell these two apart; the listing can.

  strap_asm.enc_transmit's A1 field -- "(bitaddr24, 24)" in its cat()
  changed to "(bitaddr24 >> 5, 24)", i.e. A1 encoded as a HALF-WORD
  address like A2 instead of the 24-bit BIT address the pocket card
  gives it
      006744.00  T    -> "000170.56 80 007425.02 20"      (4 rows)
      006762.40  T    -> "000170.56 80 007425.02 20"
      007374.40  T    -> "000170.50 80 007427.02 20"
      007405.00  SWAP -> "000170.50 80 007427.02 60"
      FIRST GROUP ONLY, every digit of it, with the second group
      untouched -- which is the asymmetry measured rather than
      asserted.  The arithmetic: I46D4 at 007427.00 is 0o742700 bits,
      and 0o742700 >> 5 = 0o17056 = 7726, whose top 18 bits print
      0o170 and whose low 6 print 0o56.  These four are the only rows
      in the block carrying a 24-bit bit address in the FIRST
      half-word of a full word -- SIC's bit address occupies a
      half-word of its own -- so nothing else can move, and nothing
      else does.

AND ONE INJECTION THIS BLOCK DOES *NOT* CATCH, measured and recorded
because a negative measured is worth more than a positive assumed:

  strap_asm.enc_transmit's A2 field -- "(addr19, 19)" in its cat()
  changed to "(addr19 & 0x7FFFE, 19)", i.e. bit 50, the A2 half-word
  select, forced to zero
      NO ROW CHANGES.  The run stays green.
      The reason is arithmetic: all four T/SWAP rows in this block
      address word-aligned constants (I46D2 at 007425.00, I46D4 at
      007427.00), so bit 50 is already zero in every one of them.
      Only a Transmit whose A2 is an ODD half-word could catch it, and
      routine 1246 contains none.  This is the same shape as the LRI
      null in verify_ibox4_rnx_nop_listing.py.

=====================================================================
NOT SETTLED, listed so that nothing above is taken for more than it
is.  No check below depends on any of these.

  1. The ident row's last operand, printed "I246" at 006741.00.  The
     leading glyph measures 10 px, which is this printer's letter I
     (digit 1 measures 31-34), so it is read as a letter -- but
     "I246" is not a symbol defined anywhere in this deck that could
     be found, and a 64-bit unsigned datum whose value was the
     routine number 1246 would read just as naturally.  MEASURED as a
     letter, SEMANTICALLY UNEXPLAINED.  It sits in a comment; the row
     emits no machine code and is SLC'd across.
  2. The banner's "----1246---" was read visually, not measured.  The
     risk is nil -- the write-up's typeset PROGRAM PHILOSOPHY table
     independently prints "1246" as digits -- but the reason it is
     believed differs from item 1's, and the two should not be
     conflated.
  3. "%IQSZ@DD%BU,64,8@" is not understood.  It is presumably a
     compiler directive or macro this project has no form for.
     Routine 1248 prints the identical shape at 007440.00.  Not
     encoded, not checked.
  4. The claim that the OTHER decks' labels in this repo are also
     letter-I is an INFERENCE, not sixteen measurements.  "I4412" on
     PDF p.90 was measured; the rest (the labels earlier files spell
     I44D1, I44XW1, I46) follow from C22-6531's rule that a
     symbol's first character must be alphabetic.  The inference is
     near-airtight but it is an inference, and no file other than
     this one has been changed.
  5. The 007372.00 endpoint given above for TESTs 2A-2B is
     ARITHMETIC: 007272.00 (TEST 2A's first row) and 007372.40 (TEST
     2C's first row) were both read first-hand off the pages; the
     boundary between them is the difference.
  6. Bits 50, 55 and 56 are witnessed at ZERO only, by every T/SWAP
     row in the block.  TESTs 2A and 2B, not transcribed, are where
     the deck varies bits 55 and 56.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax4b_1246_transmit_swap.strap").read())

# ---------------------------------------------------------------------
# PDF p.99, 006736.00-006740.40.  The preamble.  The ident row at
# 006741.00 prints a location and NO machine code and is not here.
# ---------------------------------------------------------------------
PREAMBLE_ROWS = [
    ('006736.00', '6741.02 10',  'I46 LX,$X1,I46ID   "-UPDATE IDENT."  (I46ID SYN-fed)'),
    ('006736.40', '1437.03 10',  'SX,$X1,DPET13      (ext)'),
    ('006737.00', '1306.40 80',  'SIC,RET            (ext) pair 40 is a BIT OFFSET'),
    ('006737.40', '1443.10 00',  'B,IDF1             (ext) "-PRINT ID."'),
    ('006740.00', '7422.22 00',  'Z,IC246            reaches the constants block'),
    ('006740.40', '6742.04 00',  'BD,I461            bit 18 = 0 -> 006742.00'),
]

# ---------------------------------------------------------------------
# PDF p.100, 006742.00-006771.40.  TEST 1A, EXT MEM TO EXT MEM.
# ---------------------------------------------------------------------
TEST1A_ROWS = [
    ('006742.00', '7425.22 00',  'I461 Z,I46D2       "-TEST 1A, EXT MEM TO EXT MEM."'),
    ('006742.40', '13035.02 10', 'LX,$X1,I00O        (ext) the all-ones constant'),
    ('006743.00', '7427.03 10',  'SX,$X1,I46D4       all ones into the receiving word'),
    ('006743.40', '13131.02 10', 'LX,$X1,BIT45       (ext) count field = 1'),
    ('006744.00', '7427.00 80 007425.02 20',
                                 'T,$X1,I46D4,I46D2  T WITNESS 1: A1 BIT addr, A2 HALF-WORD'),
    ('006745.00', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2        read the destination back'),
    ('006746.00', '6750.34 C0',  'BZRZ,$+2.0         OK when Result Zero is OFF'),
    ('006746.40', '1310.00 80',  'SIC,SEN            (ext) "-TRANSMIT 1 WD EXT MEM TO"'),
    ('006747.00', '1304.10 00',  'B,SERS             (ext) "-EXT MEM DROPS ALL BITS."'),
    ('006747.40', '6761.10 00',  'B,I4610            bit 18 = 0 -> 006761.00'),
    ('006750.00', '7425.04 10',  'LX,$X2,I46D2'),
    ('006750.40', '13035.04 90', 'KV,$X2,I00O        (ext) compare value fields'),
    ('006751.00', '6752.72 C2',  'BXE,$+1.32         BIT 18 SET -> 006752.40'),
    ('006751.40', '1310.00 80',  'SIC,SEN            (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('006752.00', '1304.10 00',  'B,SERS             (ext) "-OF BITS 0-24."'),
    ('006752.40', '13035.05 90', 'KC,$X2,I00O        (ext) compare COUNT fields'),
    ('006753.00', '6754.72 C2',  'BXE,$+1.32         BIT 18 SET -> 006754.40'),
    ('006753.40', '1310.00 80',  'SIC,SEN            (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('006754.00', '1304.10 00',  'B,SERS             (ext) "-OF BITS 28-45."'),
    ('006754.40', '22.05 70',    'SR,$X2,$X2         word 18 = index register 2'),
    ('006755.00', '777777.05 04', 'KVI,$X2,(8)777777.0   octal marker load-bearing'),
    ('006755.40', '6757.32 C2',  'BXE,$+1.32         bit 18 = 0 -> 006757.00'),
    ('006756.00', '1310.00 80',  'SIC,SEN            (ext) "-ABOVE TYPE TRANSMIT LOSES SOME"'),
    ('006756.40', '1304.10 00',  'B,SERS             (ext) "-OF BITS 46 TO 63."'),
    ('006757.00', '22.04 10',    'LX,$X2,$X2'),
    ('006757.40', '6761.23 42',  'BXF,$+1.32         bit 18 = 0 -> 006761.00'),
    ('006760.00', '1310.00 80',  'SIC,SEN            (ext) "-ABOVE TYPE TRANSMIT LOSES"'),
    ('006760.40', '1304.10 00',  'B,SERS             (ext) "-BIT 25."'),
    ('006761.00', '7425.22 00',  'I4610 Z,I46D2      "-CHECK FOR SPURIOUS BITS."'),
    ('006761.40', '7427.22 00',  'Z,I46D4'),
    ('006762.00', '13131.02 10', 'LX,$X1,BIT45       (ext)'),
    ('006762.40', '7427.00 80 007425.02 20',
                                 'T,$X1,I46D4,I46D2  T WITNESS 2: FULL WORD at an ODD half-word'),
    ('006763.40', '7425.00 80 000000.20 50',
                                 'L(BU),I46D2        also full-word at an odd half-word'),
    ('006764.40', '6766.34 C2',  'BRZ,$+1.32         OK when Result Zero is ON'),
    ('006765.00', '1310.00 80',  'SIC,SEN            (ext) "-ABOVE TYPE TRANSMIT PICKS"'),
    ('006765.40', '1304.10 00',  'B,SERS             (ext) "-UP SOME BITS 0-63."'),
    ('006766.00', '6767.10 00',  'B,$+1.0'),
    ('006766.40', '6742.04 00',  'BD,I461            bit 18 = 0 -> 006742.00'),
    ('006767.00', '1311.40 80',  'SIC,SENO+.32       (ext) pair 40 is a BIT OFFSET'),
    ('006767.40', '1301.10 00',  'B,SSW              (ext) "-TO SSIP."'),
    ('006770.00', '6770.44 00',  'BD,$+.32           BIT 18 SET -> 006770.40'),
    ('006770.40', '7422.32 10',  'LX,$X13,IC246      "-UPDATE CONTINUITY CHECK."'),
    ('006771.00', '13054.32 B0', 'V+,$X13,BIT0       (ext) TEST 1A"s continuity bit'),
    ('006771.40', '7422.33 10',  'SX,$X13,IC246'),
]

# ---------------------------------------------------------------------
# PDF p.112, 007372.40-007421.40.  "-TEST 2C."  The transmit/swap
# modifier bit, then the routine's tail.
# ---------------------------------------------------------------------
TEST2C_ROWS = [
    ('007372.40', '7424.22 00',  'I4626 Z,I46D1      "-TEST TRANSMIT-SWAP MODIFIER."'),
    ('007373.00', '13035.02 10', 'LX,$X1,I00O        (ext)'),
    ('007373.40', '7427.03 10',  'SX,$X1,I46D4       all ones into the receiving word'),
    ('007374.00', '13131.02 10', 'LX,$X1,BIT45       (ext) count field = 1'),
    ('007374.40', '7424.00 80 007427.02 20',
                                 'T,$X1,I46D1,I46D4  T WITNESS 3 -- pair with the SWAP below'),
    ('007375.40', '7424.00 80 000000.20 50',
                                 'L(BU),I46D1        read the SENDING word back'),
    ('007376.40', '7400.74 C2',  'BRZ,$+2.0          BIT 18 SET -> 007400.40'),
    ('007377.00', '1310.00 80',  'SIC,SEN            (ext) "-TRANSMIT DESTROYS ORIGINAL WORD"'),
    ('007377.40', '1304.10 00',  'B,SERS             (ext) "-AND THEREFORE ACTS LIKE SWAP."'),
    ('007400.00', '7403.10 00',  'B,I4627            bit 18 = 0 -> 007403.00'),
    ('007400.40', '7427.00 80 000000.20 50',
                                 'L(BU),I46D4        read the RECEIVING word back'),
    ('007401.40', '7403.34 C2',  'BRZ,$+1.32         bit 18 = 0 -> 007403.00'),
    ('007402.00', '1310.00 80',  'SIC,SEN            (ext) "-RECEIVING LOCATION DOES NOT GET"'),
    ('007402.40', '1304.10 00',  'B,SERS             (ext) "-FIRST WORD FROM SENDING LOCN."'),
    ('007403.00', '7424.22 00',  'I4627 Z,I46D1      the SWAP half, same setup'),
    ('007403.40', '13035.02 10', 'LX,$X1,I00O        (ext)'),
    ('007404.00', '7427.03 10',  'SX,$X1,I46D4'),
    ('007404.40', '13131.02 10', 'LX,$X1,BIT45       (ext)'),
    ('007405.00', '7424.00 80 007427.02 60',
                                 'SWAP,$X1,I46D1,I46D4  THE REPO"S FIRST SWAP ROW: bit 57'),
    ('007406.00', '7424.00 80 000000.20 50',
                                 'L(BU),I46D1        read the SENDING word back'),
    ('007407.00', '7411.34 C0',  'BZRZ,$+2.0         OK when Result Zero is OFF'),
    ('007407.40', '1310.00 80',  'SIC,SEN            (ext) "-SWAP FAILS TO ALTER ORIGINAL WD"'),
    ('007410.00', '1304.10 00',  'B,SERS             (ext) "-AND THEREFORE ACTS LIKE TRANSMIT"'),
    ('007410.40', '7413.50 00',  'B,I4628            BIT 18 SET -> 007413.40'),
    ('007411.00', '7427.00 80 000000.20 50',
                                 'L(BU),I46D4'),
    ('007412.00', '7413.74 C2',  'BRZ,I4628          BIT 18 SET -> 007413.40'),
    ('007412.40', '1310.00 80',  'SIC,SEN            (ext) "-RECEIVING LOCATION DOES NOT GET"'),
    ('007413.00', '1304.10 00',  'B,SERS             (ext) "-FIRST WORD FROM SENDING LOCN."'),
    ('007413.40', '7414.50 00',  'I4628 B,$+1.0      BIT 18 SET -> 007414.40'),
    ('007414.00', '7372.44 00',  'BD,I4626           BIT 18 SET -> 007372.40'),
    ('007414.40', '1311.40 80',  'SIC,SENO+.32       (ext) pair 40 is a BIT OFFSET'),
    ('007415.00', '1301.10 00',  'B,SSW              (ext)'),
    ('007415.40', '7416.04 00',  'BD,$+.32           bit 18 = 0 -> 007416.00'),
    ('007416.00', '7422.32 10',  'LX,$X13,IC246      "-UPDATE CONTINUITY."'),
    ('007416.40', '13067.32 B0', 'V+,$X13,BIT11      (ext) TEST 2C"s continuity bit'),
    ('007417.00', '7422.33 10',  'SX,$X13,IC246'),
    ('007417.40', '7422.32 10',  'LX,$X13,IC246      "-UPDATE CONTINUITY CHECK."'),
    ('007420.00', '7423.32 90',  'KV,$X13,ICK246     against the expected mask'),
    ('007420.40', '1310.00 80',  'SIC,SEN            (ext)'),
    ('007421.00', '1304.32 C0',  'BZXE,SERS          (ext) "-CONTINUITY ERROR."'),
    ('007421.40', '7435.04 00',  'BD,I48             (ext) on to routine 1248'),
]

# ---------------------------------------------------------------------
# PDF p.112 (007422.00-007433.00) and PDF p.113's first row
# (007434.00).  Eleven contiguous words behind ONE SLC.
# ---------------------------------------------------------------------
CONST_ROWS = [
    ('007422.00', '0.00 00 000000.00 00',
     'IC246 XW,0,0,0        "-CONTINUITY REG 1246."'),
    ('007423.00', '777700.00 00 000000.00 00',
     'ICK246 XW,(8)777700.00,0,0   the expected continuity mask'),
    ('007424.00', '0.00 00 000000.00 00', 'I46D1 XW,0,0,0'),
    ('007425.00', '0.00 00 000000.00 00', 'I46D2 XW,0,0,0'),
    ('007426.00', '0.00 00 000000.00 00', 'I46D3 XW,0,0,0'),
    ('007427.00', '0.00 00 000000.00 00', 'I46D4 XW,0,0,0'),
    ('007430.00', '0.00 00 000000.00 00', 'I46D5 XW,0,0,0'),
    ('007431.00', '0.00 00 000000.00 00', 'I46D6 XW,0,0,0'),
    ('007432.00', '777777.77 00 000000.00 00',
     'I46XW1 XW,(8)777777.77,0,0   VALUE = all 24 address bits'),
    ('007433.00', '0.00 0F 777760.00 00',
     'I46XW2 XW,0,(8)777777,0      COUNT = all 18 bits, 28-45'),
    ('007434.00', '0.00 00 000017.77 FF',
     'I46XW3 XW,0,0,(8)777777      REFILL = all 18 bits, 46-63 (PDF p.113)'),
]

# Anchors (I46, I461, I4626, IC246) are the first label after an SLC
# and are asserted, not evidence -- see the docstring's witness
# tiering.  The rest fall out of the location counter.  I46ID is a SYN
# and is deliberately absent.
SYMBOLS = {
    'I46': '006736.00',
    'I461': '006742.00', 'I4610': '006761.00',
    'I4626': '007372.40', 'I4627': '007403.00', 'I4628': '007413.40',
    'IC246': '007422.00', 'ICK246': '007423.00',
    'I46D1': '007424.00', 'I46D2': '007425.00', 'I46D3': '007426.00',
    'I46D4': '007427.00', 'I46D5': '007430.00', 'I46D6': '007431.00',
    'I46XW1': '007432.00', 'I46XW2': '007433.00', 'I46XW3': '007434.00',
}

if __name__ == "__main__":
    fails = check_rows(prog, [], SYMBOLS, label='1246 ')
    fails += check_rows(prog, PREAMBLE_ROWS, label='1246 pre  ')
    fails += check_rows(prog, TEST1A_ROWS, label='1246 T1A  ')
    fails += check_rows(prog, TEST2C_ROWS, label='1246 T2C  ')
    fails += check_rows(prog, CONST_ROWS, label='1246 kons ')
    finish(fails)
