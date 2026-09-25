#!/usr/bin/env python3
"""verify_ax5b_1274_truncation_listing.py -- jb_ax5b "I-Box 5", ROUTINE
1274 ("TRUNCATION OF ADDRESSES"), the whole routine
(programs/ax5b_1274_truncation.strap) against the listing's printed
machine code, PDF pp.112-114, octal 024412.00-024500.00.  99 checked
rows, entry label I74.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering.  The only printed page numbers are in
the front write-up, which is scanned 2-up (PDF p.2 = printed pp.1-2).
Every verify_ax5b_*.py here already says "PDF p.NN".

THE PAGE SPAN, established first-hand rather than taken on trust.  PDF
p.111 ends routine 1268 with "BD,I74" at 024404.00 printed "24412.04
00", then 1268's own constants through 024411.00; the 1274 banner is
the first thing on PDF p.112.  The routine's last row is "I74PSI
XW,0,0,0" at 024500.00, four rows into PDF p.114, and the very next
row there is the header "-COMMON CONSTANTS FOR FETCH ONLY" over the
deck's SHARED pool (I00LC 024501.00 ... BIT0 024522.00 ... BIT35
024565.00).  PDF p.115 is the rest of that pool (BIT36..BIT63,
024566.00-024621.00) and PDF p.116 is the deck's SYN table and its
END.  So routine 1274's checks do NOT run to PDF p.116; they end on
PDF p.114.

THE BANNER, verbatim, PDF p.112 (three comment rows, blank location
column):

    ----I274---TRUNCATION OF ADDRESSES.
    -THIS PROGRAM CHECKS THOSE INSTRUCTIONS WHICH
    -USE ONLY PART OF THEIR ADDRESS FIELD.

THE WRITE-UP, verbatim, PDF p.2 (printed p.2), section 4.0 PROGRAM
PHILOSOPHY:

    1274   Checks that those instructions which can have a 19 bit
           address but use only 18 bits do in fact truncate the
           nineteenth bit.

and printed p.1, section 1 PURPOSE: "The I-Box 5 Program provides the
maintenance engineer with a test of the time clock, interval timer,
mask and indicator registers, interrupt system, boundary control,
execute instructions, Look-Ahead forwarding, and the proper truncation
of addresses for those instructions which use only part of their
address field."

THE SEVEN ERROR MESSAGES, verbatim, each with the octal location of
the row it is printed beside:

    024421.40  BXVZ,SERS    -LX FAILS TO TRUNCATE BIT 19.
    024430.00  BXVZ,SERS    -SX FAILS TO TRUNCATE BIT 19.
    024436.00  BXVZ,SERS    -REFILL FAILS TO TRUNCATE BIT 19.
    024442.40  BXVZ,SERS    -EXIC FAILS TO TRUNCATE BIT 19.
    024447.00  BZXVZ,SERS   -STORE ZERO FAILS TO TRUNCATE BIT 19.
    024453.40  BXVZ,SERS    -TRANSMIT FAILS TO TRUNCATE LHW BIT 19.
    024457.40  BXVZ,SERS    -TRANSMIT FAILS TO TRUNCATE RHW BIT 19.

The other comments on these pages, verbatim: "-UPDATE IDENT."
(024412.00), "-PRINT IDENT." (024413.40), "-TO SSIP" (024461.40),
"-UPDATE CONTINUITY CHECK" (024462.40), "-LOOP" (024464.40, 024465.40,
024467.00), "-CONTINUE" (024467.40), "-CONTINUITY REG I274."
(024470.00).

"THE NINETEENTH BIT" IS IBM BIT 18.  Reference Manual printed p.20
(PDF p.23) diagrams the instruction half-word as ADDRESS 0..18, OP. at
24, I at 28: nineteen address bits numbered from zero end at 18, and
bit 18 is the half-word select.  Every subject here addresses a FULL
WORD, so bit 18 is what must be discarded.  The deck plants it the
same way seven times -- "LVI,$Xn,<word>+.32" (a value of 32 bits = one
half-word) followed by "SVA,$Xn,<target>", which copies 19 bits of the
value into the target instruction's own address field.

BRANCH POLARITY.  This block does not use the "branch to the OK path,
fall through to SIC,SEN / B,SERS" shape at all.  Every check is
"SIC,SEN" and THEN a conditional branch TO SERS, so the branch is
taken on FAILURE and the message names the anomaly -- the same shape
verify_ax5b_162_test3a_listing.py already records.  The proof that
this reading is right is the odd one out: six checks end BXVZ (branch
if index Value Zero is ON) because a correct truncation leaves the
checked word holding I74K1's all-ones value; the STORE ZERO check at
024447.00 ends BZXVZ (branch if XVZ is OFF) because its subject WRITES
ZERO, so success means the value IS zero.  A polarity that cannot
explain that flip is the wrong polarity.

BIT-18 SELF-CHECKS.  Every row below whose operand is a label or a
self-relative had bit 18 decoded out of the printed octal pair (the
pair is bits 18-23; bit 18 is its TOP bit) and read back against the
page's own label column.  Decoded in full:

  024414.40 BD,I741       -> 24416.04 00: 04 = 000100, bit 18 = 0, so
                             024416.00, where p.112 prints "I741".
  024416.00 LVI,I74K1+.32 -> 24471.43 01: 43 = 100011, bit 18 = 1, so
                             024471.40 -- I74K1 (024471.00) + 32 bits.
  024416.40 SVA,$X1,I742  -> 24420.43 D0: 43, bit 18 = 1 -> 024420.40,
                             where p.112 prints "I742".
  024422.40 LVI,I74K2+.32 -> 24472.45 01: 45 = 100101, bit 18 = 1 ->
                             024472.40 = I74K2 + 32 bits.
  024423.00 SVA,$X2,I743  -> 24425.05 D0: 05 = 000101, bit 18 = 0 ->
                             024425.00, where p.112 prints "I743".
  024432.40 SVA,$X2,$+.32 -> 24433.05 D0: bit 18 = 0 -> 024433.00, the
                             "R,0" row one half-word along.  This is
                             the location counter's own witness: the
                             subject it patches carries no label.
  024440.00 LVI,I74PSI+.32-> 24500.45 01: bit 18 = 1 -> 024500.40.
  024440.40 SVA,$X2,$+.32 -> 24441.05 D0: bit 18 = 0 -> 024441.00, the
                             EXIC row.
  024443.00 LVI,I74K2+.32 -> 24472.43 01: bit 18 = 1 -> 024472.40.
  024443.40 SVA,$X1,I744  -> 24445.43 D0: 43, bit 18 = 1 -> 024445.40,
                             where p.113 prints "I744" on an ODD
                             half-word.
  024447.40 LVI,$X1,0.32  -> 0.43 01: bit 18 = 1 -> half-word 1, i.e.
                             a value of exactly 32 bits.
  024460.00 B,$+1.0       -> 24461.10 00: 10 = 001000, bit 18 = 0 ->
                             024461.00, one WORD on from 024460.00.
  024460.40 BD,I741       -> 24416.04 00: bit 18 = 0 -> 024416.00.
  024462.00 BD,$+.32      -> 24462.44 00: 44 = 100100, bit 18 = 1 ->
                             024462.40, the next row.
  024462.40 LX,$X13,BIT0  -> 24522.32 10: 32 = 011010, bit 18 = 0 ->
                             024522.00 (BIT0; but see WITNESS TIERING).
  024463.00 SX,$X13,IC274 -> 24470.33 10: 33 = 011011, bit 18 = 0 ->
                             024470.00, where p.113 prints "IC274".
  024466.40 KV,I00LC+.32  -> 24501.42 90: 42 = 100010, bit 18 = 1 ->
                             024501.40.
  024477.00 LX,$X0,I74K6  -> 24476.00 10: 00, bit 18 = 0 -> 024476.00,
                             where p.113 prints "I74K6".
  024477.40 LV,I74K6+.32  -> 24476.40 30: 40 = 100000, bit 18 = 1 ->
                             024476.40.

TWO ROWS ARE DELIBERATELY EXCLUDED from that decode, because their
octal pair is NOT a half-word select:

  024413.00 "SIC,RET"      -> 1306.40 80 and
  024461.00 "SIC,SEN0+.32" -> 1311.40 80.
  SIC's operand is a 24-BIT BIT ADDRESS (bits 0-23; Reference Manual
  p.41 / strap_asm's enc_sic), so "40" there is a bit OFFSET WITHIN
  THE WORD -- octal 40 = 32 bits.  It happens to equal one half-word,
  which is why RET's own SYN row on PDF p.116 reads "RET
  SYN,%8@1306.40", but the field means bits, not a half-word select.

  024451.00 and 024455.00, the two TRANSMITs, are full words and their
  FIRST printed pair is likewise a bit offset: A1 is a 24-bit bit
  address (pocket card X22-6533 "TRANSMIT OPERATIONS", the layout in
  opcodes.TRANSMIT_CODES).  Their SECOND pair is a real half-word
  field and is decoded: 024451.00's "024473.02" has 02 = 000010, bit
  18-equivalent (bit 50) = 0, so A2 = 024473.00 = I74K3; 024455.00's
  "024472.02" gives A2 = 024472.00 = I74K2.  The remaining bits of
  those pairs are J = 1 (the immediate count) at bits 51-54.

WITNESS TIERING.  EVERY SYN IN THE PROGRAM FILE IS AN INPUT TO THIS
CHECK, NOT A WITNESS -- a SYN makes the address field come out right
by construction, so a row naming one proves only that every OTHER
field lands where the listing puts it.  Ten symbols are SYN'd and
every one is an input:

  ASSUMED (inputs).  SEN (001310.00), SEN0 (001311.00), SERS
  (001304.00), RET (001306.40), SSW (001301.00), IDF1 (001443.00),
  DPET13 (001437.00) -- all seven are printed by this deck's OWN SYN
  table on PDF p.116, read here at 300 dpi: "SSW SYN,%8@1301.0 / ERS
  SYN,%8@1302.0 / SERS SYN,%8@1304.0 / RET SYN,%8@1306.40 / RET1
  SYN,%8@1307.0 / RET2 SYN,%8@1307.40 / SEN SYN,%8@1310.0 / SEN0
  SYN,%8@1311.0 / DPET13 SYN,%8@1437.0 / INT SYN,%8@1353.0 / IDF1
  SYN,%8@1443.0 / IDF2 SYN,%8@1444.40", with "END,%8@14000.0" at
  024622.00.  Corroboration, not promotion.  I00LC (024501.00) and
  BIT0 (024522.00) come from PDF p.114's label column.  I74ID
  (024415.00) is defined INSIDE the range and SYN'd anyway -- see the
  next paragraph.

  WITNESSED.  Thirteen symbols are defined inside the range by rows
  that print machine code, so their addresses are this assembler's own
  location-counter arithmetic over every preceding row and are checked
  below: I741, I742, I743, I744, IC274, I74K1, I74K2, I74K3, I74K4,
  I74K5, I74K6, I74K7, I74PSI.  Plus four self-relative operands that
  name no symbol at all (024432.40, 024440.40, 024460.00, 024462.00).
  I74 is asserted as the block's anchor but is NOT evidence: the SLC
  sets the counter to 024412.0 and I74 is the first label after it.
  (PDF p.111 does corroborate it -- 1268's "BD,I74" at 024404.00
  prints "24412.04 00" -- but that is another page's row.)

  THE BIT TABLE.  This block names exactly one entry, BIT0, and SYNs
  it, so it does NOT witness "BIT<n> = 024522 + n".  That rule rests
  on PDF pp.114-115's own label column, read here: BIT0 at 024522.00
  running unbroken to BIT63 at 024621.00, and 0o24621 - 0o24522 = 0o77
  = 63.

ONE ROW HAS A LOCATION AND NO MACHINE CODE and is not fabricated.  PDF
p.112 prints "I74ID  %IQSZ@DD%BU,64,8@,I274   Z" at 024415.00 with a
BLANK machine-code column -- the routine's printed identifier, in an
entry mode this assembler does not implement.  The program file SYNs
I74ID and SLCs across the word; the row is not in ROWS.  So
"LX,$X1,I74ID" at 024412.00 is an input, not a witness.  The "CNOP"
one row above it is kept verbatim: the counter is already at a word
boundary when it is reached, so it compiles nothing, matching the
page, which prints nothing for it.

GLYPHS, MEASURED at 600 dpi (ink bounding-box width in pixels, from a
connected-column scan of the rendered page).  NOTHING IN THE CHECK
DEPENDS ON ANY OF THIS: the .strap file defines and uses each name
consistently, so the oracle would be identical under every spelling
below.  It is recorded because the names are what a reader compares
against the page.

  LETTER I vs DIGIT 1 -- this print train gives digit 1 a base serif
  and an upper-left flag and letter I a bare stroke, and they are far
  apart.  On 024463.40, "LX,$X1,%8@103.0", the two digit 1's measure
  36 and 39 px.  On 024464.00, "KV,$X1,I00LC", the operand's leading
  character measures 17 px -- the same as the I of "LVI" (13 px) and
  of "SIC" (14 px).  Label "I741" at 024416.00 measures 14 px leading
  and 36 px trailing: letter then digit, inside four characters.  So
  EVERY routine-1274 symbol that looks like it begins with "1" begins
  with LETTER I: I74, I74ID, I741..I744, I74K1..I74K7, I74PSI, IC274,
  and the pool's I00LC.  The BANNER's own character was measured too,
  not assumed from the labels: the glyph before "274" in
  "----I274---TRUNCATION OF ADDRESSES." is a 13 px bare stroke, so the
  banner really does print a letter I, as do the ident datum "I274" at
  024415.00 and the comment "-CONTINUITY REG I274." at 024470.00.
  That is the one semantically surprising instance and it was measured
  on its own.

  A SOURCED RULE, where this docstring used to call it only a
  supporting argument: these names are legal STRAP symbols unaided,
  which is why this file needs no "L" prefix.  The paragraph said the
  claim behind that -- that a STRAP symbol cannot begin with a digit
  -- was inferred from THIS repo's assembler (strap_asm reads a
  leading digit as a number) and from the decks' own practice, because
  C22-6531 has no text layer and the symbol-formation page had not
  been located.  It has been: printed p.10 (PDF p.11) reads "A symbol
  is any sequence of six or fewer alphabetic and numeric characters
  conforming to the following conditions: 1. It contains only
  alphameric characters.  2. Its first character is specifically
  alphabetic."  The manual grounds the reading rather than merely
  corroborating it, and its six-character limit is what condemned the
  "L" prefixes in the first place -- L160107 is seven characters,
  I60107 is six.  The files that applied "L" to "160S1"/"162100" have
  since been corrected to I60S1/I62100 (docs/listing_typography.md).

  LETTER O vs DIGIT 0 -- also separable here, which CORRECTED
  programs/ax5b_1258_test2.strap's note that "This printer's letter O
  and digit 0 are the same glyph"; that file now records the
  correction rather than the claim.  The comparison that carries the
  argument is WITHIN ONE ROW, 024461.00: the fourth character of
  "SIC,SEN0+.32" measures 45 px and the digit 0 of that same row's
  machine code "1311.40 80" measures 45 px.  So the symbol that row
  names is SEN0, with a DIGIT.  Corroboration across rows: digit 0
  measures 43-48 px in "0.30 00", "24501.02 90" and "%8@45000.0",
  letter O 50 px in "-TO SSIP" at 024461.40.  ("NOP" at 024417.00
  gives 58 px for its O, but that band caught a rule line and the
  figure is not relied on.)  By the same measurement "BIT0" ends in a
  digit (46 px) and "I00LC" is letter-I-zero-zero (17, 43, 43 px on
  p.113; 12, 43, 45 px where p.114 prints its label row).

  AND THE DECK HAS BOTH SPELLINGS, which is why the earlier note read
  the row as meaningless.  PDF p.114's constant pool prints
  "SENO   SYN,SEN0": the LABEL's fourth character measures 54 px and
  the OPERAND's fourth measures 42 px, against 43 and 45 px for the
  two digit zeros of "I00LC" on the very next row.  So it is not the
  self-SYN "SENO SYN,SENO" that ax5b_1258_test2.strap describes -- it
  is an ALIAS, letter-O SENO defined as digit-zero SEN0.  PDF p.116's
  SYN table, measured the same way, spells the real symbol with the
  digit: its label's fourth character is 42 px and the digit 0 ending
  that row's own "%8@1311.0" is 42 px.  Both rows are outside the
  transcribed range and both are inputs here either way.

FIRSTS FOR THIS REPO.  ONE, and it was arrived at by grepping every
verify_*.py and programs/*.strap, which knocked out four candidates
that looked like firsts on inspection:

  * TRANSMIT WITH THE INDEX ON A2 -- 024455.00, "TI,1,I74K1,I74K2(X1)"
    -> "24471.00 80 024472.02 A1", where I2 (bits 60-63) is 1 and I1
    (bits 28-31) is 0.  Every other TRANSMIT this project has
    transcribed leaves I2 zero: ax5b_16087_walk's two TI rows index A1
    ("BIT0($X1)"), and ax5b_160s1_clr_inds' fifteen and
    ax5b_160105_compare's one index neither.  So bits 60-63 of a
    Transmit have never before been pinned against a printed word --
    and 024451.00, the block's other TRANSMIT, pins I1 in the same two
    rows, which is what makes injection D move a different printed
    half-word in each.

  NOT firsts, with the file that already witnessed each -- recorded
  because each one looked like a first until it was checked:
    "R" (REFILL)  -- verify_ibox4_r_extmem_listing.py ("R, I38RFL" ->
        "5627.02 00") and verify_ibox4_refill_nop_listing.py ("R, $X0"
        -> "20.02 00").  024433.00's "R,0" -> "0.02 00" is a third.
    "LV"          -- verify_ibox1_cpi_chain_listing.py, and
        verify_ax5b_160102_listing.py's "LV,$X3,BIT0($X1)".
    A LABEL IN XW'S REFILL FIELD -- verify_ax5b_160k_listing.py's
        "I60XW1 XW,0,64,I60IT" and "I60XW4 XW,0,63,I60IT".
        024474.00's "I74K4 XW,0,0,I74K1" -> "0.00 00 000000.51 39" is
        a SECOND, independent listing witness for strap_asm's ">> 6"
        bit-address-to-word-address conversion there (bits 46-63 =
        0o24471 = I74K1's word address), which is what injection F
        moves; a second witness, not a new one.
    SVA, KV, KC, SR, EXIC, SIC, CNOP, BXVZ, BZXVZ, BZXE -- all
        witnessed by earlier ax5b and ibox blocks.

DOES THIS DECK BEAR ON StretchExecute.bsv's "THE ADDITION HAPPENS IN
THE 24-BIT BIT-ADDRESS DOMAIN"?  YES, at one row; and the rest of the
block bears on the sentence after it.

Five of the seven subjects are NOT INDEXED -- bit 18 reaches their
address fields from SVA, not from index arithmetic -- so they test
Reference Manual printed p.21 (PDF p.24): "The effective address which
results from an indexing operation always has 24 numeric bits and a
sign.  Depending upon the operation, a full-word, half-word, or
bit-address may be required.  In each case, only the applicable part
of the effective address is used.  The non-applicable part is
ignored."  In this model that is the "ea[18:1]" narrowing, not
effAddr19's alignment.

024451.00, the LEFT-half Transmit, indexes a 24-bit BIT address with
X1 = 32: that is effAddr24, the case the comment itself says "was
always right, because for it the instruction address is already a bit
address and there is nothing to align."  Corroboration, not
discrimination.

024455.00, the RIGHT-half Transmit, IS discriminating.  A2 is a 19-bit
HALF-WORD address (bits 32-50) and its index I2 (bits 60-63) is X1 =
32 bits.  Under printed p.20's rule -- "The length of the address
field depends upon the instruction class.  The missing low-order bits,
if any, are always assumed to be zero" -- the half-word address is
extended with low-order zeros into the 24-bit domain first, so
024472.00 + 32 bits = 024472.40, whose word part is still 024472 =
I74K2, the word the next rows read back.  Under the straight-add the
comment records as the bug nothing caught ("previously added the value
STRAIGHT to a word or half-word address, which is wrong by 64x and 32x
respectively"), 32 would be 32 HALF-WORDS and the store would land at
word 024512; I74K2 would stay zero, XVZ would come on, and the check
would report "-TRANSMIT FAILS TO TRUNCATE RHW BIT 19."

THE MODEL SIDE WAS READ, not assumed, because opcodes.TRANSMIT_CODES
warns that "StretchExecute.bsv's Transmit arm moves exactly ONE word
and ignores both `immCount` and `j`", which left it open whether it
consults i2 at all.  It does, and it uses exactly the helper this
claim is about.  StretchDecode.bsv's Transmit arm keeps "addr2:
w[31:13] ... i2: w[3:0]", and StretchExecute.bsv's Transmit arm reads

    WordAddr srcBase = baWord(effAddr24(st, t.addr1, t.i1));
    WordAddr dstBase = (effAddr19(st, t.addr2, t.i2))[18:1];

-- A1 through effAddr24 (the case the comment calls always-right) and
A2 through effAddr19, whose body is the "{raw, 5'b0}" alignment, the
add, and "ea[23:5]".  So 024455.00 is an oracle for effAddr19
specifically, and 024451.00 for effAddr24; the deck exercises the two
helpers in two adjacent rows, with the same index value in both.

That partly corrects docs/archival_inventory.md, which rejected
routine 1274 as "untestable by construction ... BSV's fixed-width
arithmetic makes representing an address wider than architecturally
valid impossible."  True of the five unindexed subjects.  NOT true of
024455.00, whose failure mode is a wrong SCALING inside a perfectly
legal 19-bit address -- no type width forbids that.  Stated as
reasoning from the page and from reading the arm: this file is an
ENCODING check, it does not run the model, and nothing here was
confirmed in simulation.

WHERE THIS BELONGS IN THE REGRESSION SUITE.  This file is not wired
into strap/run_tests.sh -- that file was off limits to the session
that wrote this one.  The line to add, beside the other
verify_ax5b_*.py entries:

    run "I-Box 5 routine 1274 TRUNCATION OF ADDRESSES, 99 rows (jb_ax5b PDF pp.112-114)" python3 verify_ax5b_1274_truncation_listing.py

It takes well under a second and needs no Bluespec build.

RULE 4, DECLARED RATHER THAN SIDESTEPPED.  AGENTS.md: "Encodings and
semantics come from primary sources ... Never infer an instruction's
meaning from listing usage alone."  Two claims in this file ARE
sourced: the indexing rule (Reference Manual printed pp.20-21, quoted
above) and SVA's address-field replacement (printed p.29, quoted in
StretchExecute.bsv's dixop_SVA arm: "The first 18, 19, or 24 bits of
the value field of the index word specified by J replace the address
field of the instruction specified by the effective address", with the
width taken from the target).

The story of WHAT EACH SUBJECT DOES -- Refill reloading an index word
from its refill field, EXIC running a pseudo-IC, Store Zero clearing a
word, Transmit resolving A1/A2 to word addresses -- is CONJECTURE from
listing usage.  No primary-source statement for any of those four was
located for this file; for Refill, note that
docs/microarchitecture_plan.md's own summary reads differently ("put
the effective address's word into J, replace X0's refill with bits
0-17 of the effective address"), which is a second reason not to treat
the narrative above as settled.  NOTHING IN THE CHECK RESTS ON IT: the
ROWS below compare printed bit patterns against assembled ones, and
every encoding used comes from opcodes.py, whose own citations are the
pocket card and the Reference Manual.  The narrative is orientation
for a reader, and it is flagged here as such.

PROVEN DISCRIMINATING.  Six injections; the failure sets below are the
OBSERVED ones, copied from the runs, not predicted.  Every injection
was applied by patch and reverted by writing the original file back,
with "rm -rf __pycache__" on BOTH sides of every run -- stale bytecode
has replayed a previous injection's answer in this project before.
"git status" was clean after all six.

  A. strap_asm.enc_dir_index -- drop IBM BIT 18 from the 19-bit
     direct-index address field: "cat((addr19, 19), ...)" becomes
     "cat((addr19 & ~1, 19), ...)".  Bit 18 is the LSB of that field
     because cat packs MSB-first, and it is the exact bit this
     routine is about.
         024416.40  SVA,$X1,I742      '024420.43 D0' -> '024420.03 D0'
         024443.40  SVA,$X1,I744      '024445.43 D0' -> '024445.03 D0'
         024466.40  KV,$X1,I00LC+.32  '024501.42 90' -> '024501.02 90'
         024477.40  LV,$X0,I74K6+.32  '024476.40 30' -> '024476.00 30'
                                                            (4 rows)
     Exactly the four direct-index rows whose target is an odd
     half-word, and NOT the three SVA rows at 024423.00 / 024432.40 /
     024440.40, whose targets are even.  Only the OCTAL PAIR moves,
     and only its top bit; the hex byte is untouched, so a check
     reading the hex column alone would see nothing.

  B. strap_asm.enc_dir_index -- narrow the same field to 18 bits from
     the other end, dropping IBM bit 0: "addr19 & 0x3FFFF".
         NULL RESULT: all 113 checks still pass.
     Measured, and recorded with its arithmetic reason rather than
     discarded: the largest direct-index address in the block is
     I00LC+.32 = 024501.40, half-word number 0o24501*2 + 1 = 10561,
     and IBM bit 0 of a 19-bit field carries weight 2**18 = 262144.
     Nothing in routine 1274 addresses high enough to set it, so
     narrowing the field at the top cannot change a printed column.
     A width injection that DOES bite has to come off the bottom --
     which is injection A, and which is the deck's own subject.

  C. opcodes.DIR_INDEX_CODES["SVA"] 0b11101 -> 0b11100.
         024416.40  '024420.43 D0' -> '024420.43 C0'
         024423.00  '024425.05 D0' -> '024425.05 C0'
         024432.40  '024433.05 D0' -> '024433.05 C0'
         024440.40  '024441.05 D0' -> '024441.05 C0'
         024443.40  '024445.43 D0' -> '024445.43 C0'
                                                            (5 rows)
     The complement of A: every SVA row and only SVA rows, and this
     time the HEX BYTE moves while the octal pair does not.  A and C
     together move the two printed columns independently.

  D. strap_asm.enc_transmit -- exchange I1 (bits 28-31) and I2 (bits
     60-63).
         024451.00  '024471.00 81 024473.02 A0'
                 -> '024471.00 80 024473.02 A1'
         024455.00  '024471.00 80 024472.02 A1'
                 -> '024471.00 81 024472.02 A0'
                                                            (2 rows)
     Exactly the two TRANSMIT rows, and the change lands in a
     DIFFERENT printed half-word in each -- 024451.00 indexes A1 and
     024455.00 indexes A2.  Transcribing both is what makes this
     injection bite in two places instead of one.

  E. strap_asm.enc_imm_index -- the OTHER address encoder, same bit:
     "cat((imm19, 19), ...)" becomes "cat((imm19 & ~1, 19), ...)".
         024416.00  '024471.43 01' -> '024471.03 01'
         024422.40  '024472.45 01' -> '024472.05 01'
         024432.00  '024472.45 01' -> '024472.05 01'
         024440.00  '024500.45 01' -> '024500.05 01'
         024443.00  '024472.43 01' -> '024472.03 01'
         024447.40  '000000.43 01' -> '000000.03 01'
         024476.00  '777777.43 01' -> '777777.03 01'
                                                            (7 rows)
     Every LVI in the block whose operand carries the "+.32" that
     plants bit 18 -- the six that set up the seven checks, plus the
     constant I74K6.  Disjoint from A's four rows, which is the point:
     the two encoders write the same field and this block pins both.

  F. strap_asm's XW REFILL conversion -- "eval_addr_field(...,
     loc, 6, ...)" becomes "..., loc, 0, ...", i.e. a label's bit
     address is no longer scaled to a word address.
         024474.00  I74K4 XW,0,0,I74K1
                    '000000.00 00 000000.51 39'
                 -> '000000.00 00 000011.16 40'
                                                            (1 row)
     The only row in the block with a symbol in XW's refill field, and
     the only row that moves.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_1274_truncation.strap").read())

# (octal location, printed machine code, note).  "(SYN)" marks a row
# whose address field came from a SYN -- an input, not a witness.
ROWS = [
    # ---- PDF p.112: entry -----------------------------------------
    ('024412.00', '24415.02 10', 'I74 LX,$X1,I74ID  (SYN) -UPDATE IDENT.'),
    ('024412.40', '1437.03 10',  'SX,$X1,DPET13     (SYN)'),
    ('024413.00', '1306.40 80',  'SIC,RET           (SYN) 40 = a BIT offset'),
    ('024413.40', '1443.10 00',  'B,IDF1            (SYN) -PRINT IDENT.'),
    ('024414.00', '24470.22 00', 'Z,IC274           in range'),
    ('024414.40', '24416.04 00', 'BD,I741           bit 18 = 0 -> 024416.00'),
    # 024415.00: the ident word, location printed, no machine code.
    # ---- 1. LX ----------------------------------------------------
    ('024416.00', '24471.43 01', 'I741 LVI,$X1,I74K1+.32  bit 18 = 1'),
    ('024416.40', '24420.43 D0', 'SVA,$X1,I742      bit 18 = 1 -> 024420.40'),
    ('024417.00', '0.30 00',     'NOP'),
    ('024417.40', '22.22 00',    'Z,$X2             word 18'),
    ('024420.00', '0.30 00',     'NOP'),
    ('024420.40', '0.04 10',     'I742 LX,$X2,0     THE SUBJECT'),
    ('024421.00', '1310.00 80',  'SIC,SEN           (SYN)'),
    ('024421.40', '1304.31 42',  'BXVZ,SERS  -LX FAILS TO TRUNCATE BIT 19.'),
    # ---- 2. SX ----------------------------------------------------
    ('024422.00', '24471.02 10', 'LX,$X1,I74K1'),
    ('024422.40', '24472.45 01', 'LVI,$X2,I74K2+.32  bit 18 = 1'),
    ('024423.00', '24425.05 D0', 'SVA,$X2,I743      bit 18 = 0 -> 024425.00'),
    ('024423.40', '0.30 00',     'NOP'),
    ('024424.00', '24472.22 00', 'Z,I74K2'),
    ('024424.40', '0.30 00',     'NOP'),
    ('024425.00', '0.03 10',     'I743 SX,$X1,0     THE SUBJECT'),
    ('024425.40', '0.30 00',     'NOP'),
    ('024426.00', '0.30 00',     'NOP'),
    ('024426.40', '23.22 00',    'Z,$X3             word 19'),
    ('024427.00', '24472.06 10', 'LX,$X3,I74K2'),
    ('024427.40', '1310.00 80',  'SIC,SEN           (SYN)'),
    ('024430.00', '1304.31 42',  'BXVZ,SERS  -SX FAILS TO TRUNCATE BIT 19.'),
    # ---- 3. REFILL ------------------------------------------------
    ('024430.40', '24474.02 10', 'LX,$X1,I74K4      refill field = I74K1'),
    ('024431.00', '24472.03 10', 'SX,$X1,I74K2'),
    ('024431.40', '24473.22 00', 'Z,I74K3'),
    ('024432.00', '24472.45 01', 'LVI,$X2,I74K2+.32'),
    ('024432.40', '24433.05 D0', 'SVA,$X2,$+.32     -> 024433.00, no label'),
    ('024433.00', '0.02 00',     'R,0               THE SUBJECT (repo first)'),
    ('024433.40', '0.30 00',     'NOP'),
    ('024434.00', '0.30 00',     'NOP'),
    ('024434.40', '24.22 00',    'Z,$X4             word 20'),
    ('024435.00', '24472.10 10', 'LX,$X4,I74K2'),
    ('024435.40', '1310.00 80',  'SIC,SEN           (SYN)'),
    ('024436.00', '1304.31 42',  'BXVZ,SERS  -REFILL FAILS TO TRUNCATE BIT 19.'),
    # ---- PDF p.113: 4. EXIC ---------------------------------------
    ('024436.40', '24477.02 10', 'LX,$X1,I74K7'),
    ('024437.00', '24500.03 10', 'SX,$X1,I74PSI'),
    ('024437.40', '21.22 00',    'Z,$X1             word 17'),
    ('024440.00', '24500.45 01', 'LVI,$X2,I74PSI+.32  bit 18 = 1'),
    ('024440.40', '24441.05 D0', 'SVA,$X2,$+.32     -> 024441.00'),
    ('024441.00', '24500.16 00', 'EXIC,I74PSI       THE SUBJECT'),
    ('024441.40', '21.02 10',    'LX,$X1,$X1        set indicators from X1'),
    ('024442.00', '1310.00 80',  'SIC,SEN           (SYN)'),
    ('024442.40', '1304.31 42',  'BXVZ,SERS  -EXIC FAILS TO TRUNCATE BIT 19.'),
    # ---- 5. STORE ZERO (the inverted check) -----------------------
    ('024443.00', '24472.43 01', 'LVI,$X1,I74K2+.32  bit 18 = 1'),
    ('024443.40', '24445.43 D0', 'SVA,$X1,I744      bit 18 = 1 -> 024445.40'),
    ('024444.00', '24471.02 10', 'LX,$X1,I74K1'),
    ('024444.40', '24472.03 10', 'SX,$X1,I74K2      I74K2 := all ones'),
    ('024445.00', '22.22 00',    'Z,$X2'),
    ('024445.40', '0.22 00',     'I744 Z,0          THE SUBJECT'),
    ('024446.00', '24472.04 10', 'LX,$X2,I74K2'),
    ('024446.40', '1310.00 80',  'SIC,SEN           (SYN)'),
    ('024447.00', '1304.31 40',  'BZXVZ,SERS  -STORE ZERO FAILS TO TRUNCATE BIT 19.'),
    # ---- 6. TRANSMIT, left half-word ------------------------------
    ('024447.40', '0.43 01',     'LVI,$X1,0.32      bit 18 = 1: 32 bits'),
    ('024450.00', '24472.22 00', 'Z,I74K2'),
    ('024450.40', '24473.22 00', 'Z,I74K3'),
    ('024451.00', '24471.00 81 024473.02 A0',
     'TI,1,I74K1($X1),I74K3   full word; A1 indexed (I1 = 1)'),
    ('024452.00', '22.22 00',    'Z,$X2'),
    ('024452.40', '24473.04 10', 'LX,$X2,I74K3'),
    ('024453.00', '1310.00 80',  'SIC,SEN           (SYN)'),
    ('024453.40', '1304.31 42',  'BXVZ,SERS  -TRANSMIT FAILS TO TRUNCATE LHW BIT 19.'),
    # ---- 7. TRANSMIT, right half-word -----------------------------
    ('024454.00', '24472.22 00', 'Z,I74K2'),
    ('024454.40', '24473.22 00', 'Z,I74K3'),
    ('024455.00', '24471.00 80 024472.02 A1',
     'TI,1,I74K1,I74K2($X1)   full word; A2 indexed (I2 = 1) -- repo first'),
    ('024456.00', '22.22 00',    'Z,$X2'),
    ('024456.40', '24472.04 10', 'LX,$X2,I74K2'),
    ('024457.00', '1310.00 80',  'SIC,SEN           (SYN)'),
    ('024457.40', '1304.31 42',  'BXVZ,SERS  -TRANSMIT FAILS TO TRUNCATE RHW BIT 19.'),
    # ---- loop once, return to SSIP --------------------------------
    ('024460.00', '24461.10 00', 'B,$+1.0           -> 024461.00 (one WORD)'),
    ('024460.40', '24416.04 00', 'BD,I741           bit 18 = 0'),
    ('024461.00', '1311.40 80',  'SIC,SEN0+.32      (SYN) 40 = a BIT offset'),
    ('024461.40', '1301.10 00',  'B,SSW             (SYN) -TO SSIP'),
    ('024462.00', '24462.44 00', 'BD,$+.32          bit 18 = 1 -> 024462.40'),
    # ---- continuity register and the loop-count block -------------
    ('024462.40', '24522.32 10', 'LX,$X13,BIT0      (SYN) -UPDATE CONTINUITY CHECK'),
    ('024463.00', '24470.33 10', 'SX,$X13,IC274     bit 18 = 0 -> 024470.00'),
    ('024463.40', '103.02 10',   'LX,$X1,(8)103.0   absolute word 0o103'),
    ('024464.00', '24501.02 90', 'KV,$X1,I00LC      (SYN)'),
    ('024464.40', '45000.32 C0', 'BZXE,(8)45000.0   -LOOP'),
    ('024465.00', '24501.03 90', 'KC,$X1,I00LC      (SYN)'),
    ('024465.40', '45000.32 C0', 'BZXE,(8)45000.0   -LOOP'),
    ('024466.00', '21.03 70',    'SR,$X1,17.0       word 17 = $X1'),
    ('024466.40', '24501.42 90', 'KV,$X1,I00LC+.32  (SYN) bit 18 = 1'),
    ('024467.00', '45000.32 C0', 'BZXE,(8)45000.0   -LOOP'),
    ('024467.40', '57000.10 00', 'B,(8)57000.0      -CONTINUE'),
    ('024470.00', '0.00 00 000000.00 00',
     'IC274 XW,0,0,0    -CONTINUITY REG I274.'),
    # ---- the routine's own constants ------------------------------
    ('024471.00', '777777.77 00 000000.00 00',
     'I74K1 XW,(8)777777.77,0,0   the all-ones value'),
    ('024472.00', '0.00 00 000000.00 00', 'I74K2 XW,0,0,0'),
    ('024473.00', '0.00 00 000000.00 00', 'I74K3 XW,0,0,0'),
    ('024474.00', '0.00 00 000000.51 39',
     'I74K4 XW,0,0,I74K1   refill bits 46-63 = 0o24471 (repo first)'),
    ('024475.00', '0.00 00 000000.00 00', 'I74K5 XW,0,0,0'),
    ('024476.00', '777777.43 01', 'I74K6 LVI,$X1,(8)777777.40'),
    # ---- PDF p.114 ------------------------------------------------
    ('024476.40', '0.03 01',     'LVI,$X1,0'),
    ('024477.00', '24476.00 10', 'I74K7 LX,$X0,I74K6   bit 18 = 0'),
    ('024477.40', '24476.40 30', 'LV,$X0,I74K6+.32   bit 18 = 1 (repo first)'),
    ('024500.00', '0.00 00 000000.00 00', 'I74PSI XW,0,0,0'),
]

# Only labels DEFINED inside the transcribed range by a row that
# prints machine code belong here; a SYN'd external (or I74ID, whose
# row prints no code) would be checking this file against itself.
# I74 is the block's anchor, asserted but not evidence -- see the
# docstring's WITNESS TIERING.
SYMBOLS = {
    'I74':    '024412.00',
    'I741':   '024416.00',
    'I742':   '024420.40',
    'I743':   '024425.00',
    'I744':   '024445.40',
    'IC274':  '024470.00',
    'I74K1':  '024471.00',
    'I74K2':  '024472.00',
    'I74K3':  '024473.00',
    'I74K4':  '024474.00',
    'I74K5':  '024475.00',
    'I74K6':  '024476.00',
    'I74K7':  '024477.00',
    'I74PSI': '024500.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1274 '))
