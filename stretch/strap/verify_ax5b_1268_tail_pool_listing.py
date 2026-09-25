#!/usr/bin/env python3
"""verify_ax5b_1268_tail_pool_listing.py -- jb_ax5b "I-Box 5", routine
1268's TAIL AND CONSTANT POOL (PDF p.111, octal 024376.00-024411.00,
21 rows) and its ENTRY (PDF p.110, octal 024333.00-024335.40, 6 rows),
from programs/ax5b_1268_tail_pool.strap, against the listing's printed
machine code.  27 checked rows, 5 symbol assertions, 1 absence
assertion.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering.  Every verify_ax5b_*.py here says
"PDF p.NN".  Reference Manual pages are given both ways; that PDF has
no text layer and PDF page = printed page + 3, so every quotation
below was read off a rendered page image.

====================================================================
PREMISE CHECK, run before anything was written, because this project
has handed out ranges that turned out already covered.

Every octal address in both target ranges was grepped against every
strap/verify_*.py and every strap/programs/*.strap.  RESULT: NEITHER
RANGE HAS ANY ROWS COVERAGE.  The three committed 1268 files stop at
024375.40 and start at 024337.00:

    verify_ax5b_1681_listing.py          024337.00-024344.00 (test 1A)
    verify_ax5b_1268_test1bc_listing.py  024344.40-024363.00 (1B/1C)
    verify_ax5b_1683_listing.py          024363.40-024375.40 (test 2)

The distinction the brief asked for, spelled out, because a bare grep
hit on "024405" would otherwise look like coverage:

  * 024405.00 / 024406.00 / 024407.00 / 024410.00 / 024411.00 appear
    in verify_ax5b_1268_test1bc_listing.py's DOCSTRING (lines 180-186,
    206-217, 389-390) and in the SYN blocks of
    ax5b_1268_test1bc.strap and ax5b_1683_df_close_to_ds.strap.
    Every one of those is an INPUT.
  * 024405.00 / 024407.00 / 024410.00 additionally appear in
    programs/ax5b_1268_test1bc.strap as PLACED SUBSTITUTIONS (labels
    CREG, K1, K2, each after its own SLC), written there so the block
    could be run.  They are in no ROWS list and nothing checks them.
  * 024376.00 appears only in ax5b_1683_df_close_to_ds.strap's prose,
    as the address of that file's substituted "BEW,$" exit.
  * 024404.00 and 024411.00 appear only in ax5b_1274_truncation's
    prose and header.
  * 024333.00 / 024335.00 / 024336.00 appear only in prose, in
    verify_ax5b_162_test3b_listing.py, ax5b_162_test3b.strap and
    ax5b_1268_test1bc.strap.
  * 024377.40, 024400.00-024403.40 appear in exactly one prose
    sentence each, or not at all.

Both ranges transcribed here are new ROWS coverage, and routine 1268
is complete except for the ident word at 024336.00, which the listing
prints with no machine code (see below).

====================================================================
THE RESULT WORTH MORE THAN THE ROW COUNT: ICK268 = 600000 OCTAL.

Read off its own row at 024406.00, which prints

    ICK268  XW,%8¤600000.00,0,0    600000.00 00 000000.00 00

600000 octal in bits 0-17 is 110 000 000 000 000 000 -- BITS 0 AND 1
SET and nothing else in the 64-bit word.  ROUTINE 1268 CLAIMS EXACTLY
TWO SUB-TESTS.

THAT IS NOT A DISCREPANCY WITH THE SIX SUB-TESTS THE DECK NAMES (1A,
1B, 1C, 2A, 2B, 2C), and it is not reported as one.  The continuity
register counts "V+" UPDATES, and routine 1268 performs exactly two,
both now transcribed and both checked:

    024362.40  V+,$X13,BIT0   24522.32 B0   verify_..._test1bc (bit 0)
    024401.00  V+,$X13,BIT1   24523.32 B0   THIS FILE           (bit 1)

The routine's banner on p.110 says the same in words -- "-THIS TEST
IS COMPOSED OF TWO ROUTINES" -- and its own headings group the six
sub-tests into those two: 1A/1B/1C are TEST 1 across the three
memories, 2A/2B/2C are TEST 2 across the same three.  So three rows
close a loop: the two bit numbers the routine sets, and the constant
it then compares against, all agree at two.

The project's two earlier readings survive and sharpen.  ICK260 =
777774 = bits 0-15 = sixteen, for a routine with sixteen NUMBERED
sub-tests.  ICK258 = 600000 = two, for a routine with two tests each
having sub-parts -- structurally identical to 1268.  The constant
counts CONTINUITY BITS; bits map to tests, not to sub-tests.  Where
the two coincide (1260) the count looks like a sub-test count; where
they do not (1258, 1268) it does not.

====================================================================
BRANCH POLARITY IN THESE ROWS: THE MINORITY SHAPE, READ OUT OF THE
PRINTED BITS.  "SIC,SEN" comes FIRST and the conditional branch goes
TO "SERS":

    024403.00  SIC,SEN        1310.00 80
    024403.40  BZXE,SERS      1304.32 C0    -CONTINUITY ERROR.

Reference Manual printed p.40 (PDF p.43), BRANCH ON INDICATOR: "This
operation causes the specified indicator to be tested.  If its value
matches that of bit 30 of the instruction, bits 0-18 of the effective
address replace the instruction counter contents."  Hex C0 =
11000000, bit 30 = 0, so the branch is taken when XE is OFF.  The
"KV,$X13,ICK268" one half-word earlier sets XE on EQUAL, so XE OFF
means the continuity register did NOT match -- and the branch target
is the error reporter.  Indicator number = bits 19-24 = 110101 = 53 =
XE.  Contrast the BXVZ rows in 1268's other blocks: hex 42 =
01000010, bit 30 = 1, branch when the indicator is ON.

Reference Manual printed p.41 (PDF p.44), STORE INSTRUCTION COUNTER
IF: "This instruction may always be prefixed to one of the half-word
branching instructions.  It is executed if and only if the associated
branching is successful."  So the SIC/BZXE pair is ONE full-word
instruction that reports only on mismatch.

THIS BLOCK USES THE SIC-FIRST, BRANCH-TO-SERS SHAPE -- the same one
routine 1274 and 1268's own 1B/1C rows use, not the "branch to the OK
label" shape most 160/162 blocks use.  Determined from these rows'
own hex bytes, not from any file's prose.

====================================================================
HEADINGS, ANNOTATIONS AND ERROR MESSAGES, VERBATIM, WITH OCTAL
LOCATIONS.  EXACTLY ONE of these is an error message.

  ERROR MESSAGE -- printed beside the branch that reports it:

    024403.40  -CONTINUITY ERROR.

  ANNOTATIONS -- they label the row they sit beside and no branch
  reports them:

    024377.40  -TO SSIP
    024400.40  -UPDATE CONTINUITY CHECK.
    024405.00  -CONTINUITY REG 1268.
    024333.00  -UPDATE IDENT.
    024334.40  -PRINT IDENT.

  "-TO SSIP" AT 024377.40 CARRIES NO PERIOD.  MEASURED HERE at 500
  dpi by segmenting ink runs across the comment field, not inherited
  from another file and not eyeballed.  Character pitch on these
  pages is ~48 px.

    p.111, 024377.40, comment field x 1900-4300, band y 2655-2705:
      1993-2034  -      2046-2082  T      2094-2135  O
      2196-2233  S      2243-2280  S      2309-2319  I  (11 px)
      2346-2382  P
      ...then NO INK AT ALL until x 4207, which is the machine-code
      column -- 1825 px, about 37 character cells, past the P.

    p.110, 024361.00, the identical row one loop earlier, band
    y 5328-5362:
      1985-2028  -      2053-2062  T      2088-2129  O
      2188-2227  S      2235-2275  S      2303-2314  I  (12 px)
      2340-2375  P      2395-2419  .   <- an EIGHTH glyph, 25 px
                                          wide, in the very next
                                          character cell

  So the two rows differ by one printed character and the difference
  is a whole glyph in the adjacent cell, not a speck.  This
  corroborates, from the other side and by an independent
  measurement, the contrast verify_ax5b_1268_test1bc_listing.py
  flagged.

  INCIDENTAL, reported as evidence and NOT acted on: the I of SSIP
  measures 11 px on p.111 and 12 px on p.110 in the same rows, while
  the S, O, P and T beside it run 37-44 px.  That sits inside the
  letter-I population docs/listing_typography.md calibrates (10-18
  px at 600 dpi; these are 500 dpi, so the bound scales down) and
  nowhere near the digit population (never below 24 px).  It is one
  more same-row instance of the kind §3 of that document collects.
  No rename is started here and no conclusion is drawn from it.

  THE BANNER is on p.110 above 024333.00, is not in either checked
  range, and is quoted in full with its measured dash counts in
  programs/ax5b_1268_test1bc.strap.  It is not re-quoted and that
  file is not edited.

====================================================================
BIT-18 SELF-CHECKS.  Print format: bits 0-17 as 6 octal digits, ".",
bits 18-23 as 2 OCTAL digits, then bits 24-31 as 2 HEX digits.  BIT
18 IS THE TOP BIT OF THE OCTAL PAIR.  Four classes of operand appear
in these 27 rows and only two of them put a half-word select there.
WHICH CLASS AN OPERAND IS IN COMES FROM THE REFERENCE MANUAL, NOT
FROM THE LISTING.

(a) BRANCH TARGETS -- bit 18 IS the half-word select.  CHECKED.

    Reference Manual printed p.39 (PDF p.42): "The address field,
    bits 0-18, represents the branch address.  Unconditional
    branching is specified by bits 19-27, where bits 19-21, the OP
    field, select the particular operation.  Bits 28-31 name the
    index register used for address modification."  Same page, on the
    instruction counter: "When the nineteenth bit is a one, the full
    word taken from storage will start at bit 32 of the addressed
    location and continue to bit 31 of the next higher location.
    When the nineteenth bit is a zero, the full word will start at
    bit 0 and continue to bit 63 of the addressed location."  The
    nineteenth bit is bit 18.

    loc        source       printed      pair     b18  decoded
    024376.00  B,$+1.0      24377.10 00  001000    0   024377.00
    024376.40  BD,I683      24363.44 00  100100    1   024363.40
    024377.40  B,SSW        1301.10 00   001000    0   001301.00
    024400.00  BD,$+.32     24400.44 00  100100    1   024400.40
    024403.40  BZXE,SERS    1304.32 C0   011010    0   001304.00
    024404.00  BD,I74       24412.04 00  000100    0   024412.00
    024334.40  B,IDF1       1443.10 00   001000    0   001443.00
    024335.40  BD,I681      24337.04 00  000100    0   024337.00
    024335.00  Z,IC268      24405.22 00  010010    0   024405.00

    The last row is not a branch, but STORE ZERO goes through the
    same encoder (strap_asm.enc_branch_or_misc, the MISC branch) and
    its bit 18 is the same half-word select.  It is also the
    CROSS-PAGE corroboration of the pool: p.110's machine code names
    024405.00, the address this file derived on p.111.

    ONE HONEST GAP IN THIS TABLE'S EMPIRICAL COVER.  Injection 1
    below patches enc_branch_or_misc and discriminates the rows that
    go through it (2 observed failures, the two odd-half-word
    targets).  BZXE goes through enc_branch_ind instead, and its
    target 001304.00 is an EVEN half-word, so NO operand in this
    block could have exposed an error in BZXE's own bit 18.  Its
    bit-18 entry above is a decode, not a discriminated check;
    injection 6 discriminates its bit 30 but not its address field.

    READ BACK AGAINST THE PAGE'S OWN LABEL COLUMN.  p.111 prints
    I683's row at 024363.40 -- an ODD half-word -- and that row's
    bit 18 is 1.  p.110 prints I681's row at 024337.00 -- an EVEN
    half-word -- and that row's bit 18 is 0.  024412.00 is routine
    1274's first row on PDF p.112 and is that file's own SLC address.
    The two self-relative rows carry the same information without any
    label at all: "B,$+1.0" at 024376.00 targets 024377.00 with bit
    18 = 0, while the SAME SOURCE TEXT at 024357.40 in the 1B/1C
    block targets 024360.40 and prints bit 18 = 1 (pair 50).

    WHY THIS IS A CHECK AND NOT A RESTATEMENT: bits 19-23 are
    constant per mnemonic across all eight rows (01000 for B, 00100
    for BD, 11010 for BZXE), so bit 18 is the ONLY bit in the pair
    that moves, and it moves exactly with the target's half-word
    parity.

(b) LX AND SX -- bit 18 is NOT a half-word select.  EXCLUDED, with
    the manual's reason, which is NOT the reason SIC is excluded.

    Reference Manual printed p.23 (PDF p.26), "Direct Index
    Arithmetic".  The format diagram's tick marks read ADDRESS 0,
    J 19, OP. 23, I 28, 31, and the text says: "In the majority of
    these operations, 19 bits of the effective address are used in
    order to permit addressing of half-words.  The two exceptions use
    only 18 bits of the effective address because they require
    full-word operands.  The index field J specifies the index
    register upon which the operation is performed."  Printed p.23:
    "Load Index (LX).  The index word specified by J is replaced by
    the full-word specified by bits 0-17 of the effective address."
    Printed p.24 (PDF p.27): "Store Index (SX).  The index word
    specified by J is stored in the full-word memory location
    specified by bits 0-17 of the effective address."  And the
    programming note closing that section: "The LOAD INDEX and STORE
    INDEX operations involve transmission of full words.  In all
    other operations the effective operand address refers to a
    half-word."

    LX AND SX ARE THE TWO EXCEPTIONS.  Their bit 18 is a low-order
    address bit forced to zero.  verify_ax5b_160_test6_listing.py
    reached the same reading from the same pages.

    What their pairs DO carry, checked instead -- bit 18 = 0, bits
    19-22 = J, bit 23 = the top bit of the 5-bit op code:

      024400.40  LX,$X13,IC268   24405.32 10   0|1101|0   J=13, LX
      024401.40  SX,$X13,IC268   24405.33 10   0|1101|1   J=13, SX
      024402.00  LX,$X13,IC268   24405.32 10   identical to the first
      024333.00  LX,$X1,I68ID    24336.02 10   0|0001|0   J=1,  LX
      024333.40  SX,$X1,DPET13   1437.03 10    0|0001|1   J=1,  SX

    The 32/33 contrast on two rows naming the SAME symbol isolates
    bit 23 alone: DIR_INDEX_CODES["LX"] = 0b00001 and ["SX"] =
    0b10001 differ in exactly that bit.  This corroborates, with a
    second J value, the note verify_ax5b_1268_test1bc_listing.py
    makes about "pair 33 vs the LX row's 32".  And the J placement is
    falsified by the printed digits themselves: if J sat at bits
    18-21, $X13 = 1101 would put a 1 at the top of the pair and print
    64-77 octal.  It prints 32.

(c) V+ AND KV -- bit 18 IS the half-word select.  CHECKED.  These are
    NOT the two exceptions.

    Reference Manual printed p.24 (PDF p.27): "Add to Value (V+).
    The address part, bits 0-24, of the half-word addressed by bits
    0-18 of the effective address is added to the address part, bits
    0-24, of the index word specified by J."  And: "Compare Value
    (KV).  The address part, bits 0-24, of the half-word addressed by
    bits 0-18 of the effective address is compared with the address
    part, bits 0-24, of the index word specified by J."

      024401.00  V+,$X13,BIT1    24523.32 B0   b18=0 -> 024523.00
      024402.40  KV,$X13,ICK268  24406.32 90   b18=0 -> 024406.00

    Read back: p.111's label column prints ICK268 at 024406.00, an
    EVEN half-word, and the pair's bit 18 is 0.  BIT1's defining row
    is on p.114 and is on neither of these pages -- see THE BIT
    TABLE.

(d) SIC -- EXCLUDED, and this is the trap the print format sets.

    Reference Manual printed p.41 (PDF p.44), "Storage of Instruction
    Counter": "Bits 0-23 constitute the storage address.  Bits 24-27,
    together with the half-word branch instruction operation code,
    specify the full-word operation.  Bits 28-31 name the index
    register used for storage address modification.  Bits 32-63
    specify the half-word branch instruction used."  The diagram's
    tick marks read ADDRESS 0 .. 18 .. 24 | 1000 | 28 I | 32 HALF
    LENGTH BRANCH INSTRUCTION 63.

    So SIC's operand is a 24-BIT BIT ADDRESS: bits 18-23 are a BIT
    OFFSET WITHIN THE WORD, not a half-word select.

      024377.00  SIC,SEN0+.32   1311.40 80
      024403.00  SIC,SEN        1310.00 80
      024334.00  SIC,RET        1306.40 80

    THE DIGITS CANNOT TELL THE TWO READINGS APART, because 32 bits is
    ALSO exactly one half-word: pair 40 octal = 32 decimal, and a
    "bit 18 = 1" reading would also render ".40".  THE ARITHMETIC
    SETTLES IT, not the digits.  The first row's source writes
    "+.32" -- a count of THIRTY-TWO BITS -- and the pair is 40 octal
    = 32 decimal, i.e. the whole six-bit field is carrying that
    number.  Under a half-word reading only bit 18 would be used and
    bits 19-23 would have to mean something else; the manual leaves
    them nothing else to mean, because it assigns bits 0-23 entire to
    the address and starts the next field at bit 24.  The 1306.40 of
    "SIC,RET" is the same field doing the same job with NO "+.32"
    written anywhere: RET is itself the bit address 001306.40, and
    PDF p.116's SYN table prints "RET SYN,%8@1306.40".

====================================================================
WITNESS TIERING.  EVERY "SYN" IS AN INPUT, NOT A WITNESS: its value
was read off a printed column and handed to the assembler, so a row
naming it can only hand the number back.  A LABEL PLACED BY AN "SLC"
IS AN ANCHOR, not evidence, for the same reason.

GENUINELY WITNESSED BY THIS FILE -- ALL FIVE POOL ADDRESSES.

There is ONE SLC for the whole tail, at 024376.0, taken from the
printed location column of the block's first row, and the block runs
unbroken to 024411.00.  Every pool label's value therefore falls out
of the assembler's own size accounting from that single anchor:

    024376.0 + 14 half-words          = 024404.40
    CNOP rounds up (one NOP emitted)  = 024405.00   IC268
    + one full word                   = 024406.00   ICK268
    + one full word                   = 024407.00   I68K1
    + two half-words                  = 024410.00   I68K2
    + two half-words                  = 024411.00   I68K3

Each is then checked against TWO INDEPENDENT PRINTED COLUMNS:

  1. the LOCATION column on the right of p.111 -- the five SYMBOLS
     assertions below, which compare the DERIVED value against the
     number the page prints beside each label;
  2. the MACHINE-CODE column of rows that NAME them -- "24405" on
     four separate rows (024400.40, 024401.40, 024402.00 on p.111 and
     024335.00 on p.110) and "24406" on one (024402.40).

That second check reaches ACROSS PAGES: p.110's "Z,IC268" at
024335.00 prints "24405.22 00", so a different page's machine-code
column corroborates the address this file derived on p.111.  Nothing
in this file told the assembler where IC268 is.

ALL THREE EXISTING 1268 FILES CURRENTLY TAKE THESE FIVE AS SYN'D
INPUTS.  This file converts them to witnessed addresses.

ANCHORS, not witnesses, and not asserted: L1268T (this file's own
name for the tail's first row -- the listing's LABEL COLUMN IS EMPTY
for all fourteen tail rows) and I68 at 024333.00 (a real printed
label, but placed by this file's second SLC; asserting it would check
the SLC against the number this transcription gave the SLC).

NOT WITNESSED, named so it is not mistaken for one: I68ID at
024336.00.  SYN'd -- deliberately from the LOCATION column, NOT from
"LX,$X1,I68ID"'s machine code, which would make the 024333.00 row a
tautology.  Taken from the location column, that row's printed
"24336" becomes a real cross-check of one printed column against the
other.

====================================================================
THE BIT TABLE -- stated precisely rather than claimed.

The rule is BIT<n> = the word at octal 024522 + n.  "V+,$X13,BIT1" at
024401.00 prints "24523.32 B0", i.e. the assembler resolved BIT1 to
word 024523 = 024522 + 1, a data point at n = 1.

THIS FILE DOES NOT WITNESS THE TABLE.  BIT1 is SYN'd in the .strap,
and the SYN's value came from this very row's machine code, so the
check re-derives its own input -- an INPUT under the rule stated
above.

What the row IS: a SECOND, INDEPENDENT INSTANCE of a value this
repository already recorded once.  programs/ax5b_1258_test2.strap
line 162 carries "BIT1  SYN, (8)24523.0   ! from V+,$X13,BIT1 =
24523.32 B0", read off ROUTINE 1258 on PDF p.5.  Different routine,
different page, same number, same printed pair.  That is
corroboration, not a new witness.

WHAT WOULD WITNESS THE TABLE is p.114's own label column, where
BIT0-BIT35 are defined.  GREPPED, BEFORE CLAIMING: NO verify_*.py in
this repository has a ROWS entry on p.114's BIT table.  It is quoted
in prose in ax5b_162_test1cc.strap ("BIT0 XW,%8@400000.00,0,0" at
024522.00), in ax5b_1258_test2.strap ("BIT1 XW,(8)200000.00,0,0") and
in ax5b_1274_truncation.strap, and SYN'd in several files, but it is
checked nowhere.  It remains an open transcription target.

====================================================================
CNOP -- KEPT VERBATIM, NEVER HAND-EXPANDED, AND THE PAGE SHOWS BOTH
OF ITS BRANCHES, one in each of this file's two ranges.

  024404.40, PDF p.111: the CNOP row prints machine code "0.30 00"
  AND the location 024404.40.  "BD,174" sits at 024404.00, so the
  counter is mid-word and CNOP fills the gap with a NOP before the
  full-word XW at 024405.00.  CHECKED as a row below.

  between 024335.40 and 024336.00, PDF p.110: the CNOP row prints
  NEITHER A LOCATION NOR MACHINE CODE.  "BD,I681" sits at 024335.40,
  the second half of word 024335, so the counter is already on the
  word boundary 024336.00 and CNOP has nothing to fill.  There is no
  row to check; the silence is the observation.

WHICH OF THE TWO IS LOAD-BEARING WAS MEASURED, NOT ASSUMED, AND THE
MEASUREMENT CORRECTED WHAT THIS SECTION FIRST SAID.

  The 024404.40 CNOP IS load-bearing.  Deleting the "CNOP" line from
  the .strap leaves 024404.40 assembling as an all-zero half-word,
  "000000.00 00" against the page's "000000.30 00" -- one observed
  failure, nothing else.  The automatic gap filler does NOT cover it:
  assemble() records a rounding gap only when the statement that
  forced the rounding is an INSTRUCTION, and strap_asm.py's own test
  excludes XW ("is_instruction = stmt.op.upper() not in ('DD', 'VF',
  'XW', 'END', 'SYN', 'SLC')").  The full-word XW at 024405.00 still
  ALIGNS the counter, which is why the five pool addresses do not
  move -- but nothing fills the half-word it skipped.  Injection 5
  below reaches the same row from the assembler side.
  So this file DOES witness CNOP's NOP emission; it does NOT witness
  CNOP's round-up, because XW's own alignment would do that anyway.

  The p.110 CNOP is NOT load-bearing.  Deleting it leaves ALL TESTS
  PASSED.  Arithmetic reason, recorded rather than discarded: the
  counter is already on a word boundary when it is reached, so it has
  no gap to fill, and an SLC follows it, so nothing downstream
  depends on where it left the counter.  The page's silence is the
  evidence there; this file only fails to contradict it.

verify_ax5b_160_test8c_disabled_listing.py is the file that witnesses
both CNOP branches from assembled output, and
programs/ax5b_1258_test1.strap records the same caveat about a
transcript that cuts at an SLC.

====================================================================
WHERE THE LISTING PRINTS A LOCATION AND NO MACHINE CODE, NO WORD IS
FABRICATED.  p.110's row at 024336.00 reads, in full:

    I68ID   %IQSZ¤DD%BU,64,8¤,1268   Z             024336.00

-- a label, a print macro this assembler does not implement, and an
EMPTY machine-code column.  The entry block therefore stops at
024335.40 with the CNOP, I68ID is SYN'd from the printed LOCATION
column, and nothing is placed at 024336.00.  check_absent() below
asserts that word 024336 is ABSENT from the assembled image, so the
claim is checked rather than promised.

ax5b_1258_test1.strap and ax5b_1274_truncation.strap exclude the
corresponding ident rows for the same reason, and §7 of
docs/listing_typography.md notes that the ident word is the one place
where a disputed glyph would be ENCODED rather than merely named --
had one been transcribed, the digit-1 reading would have become a
real encoding error.  It was not.

====================================================================
FIRSTS FOR THIS REPO: NONE.  Every mnemonic in both ranges was
grepped against every other programs/*.strap and verify_*.py BEFORE
any claim was made, and every candidate was knocked out:

    KV    27 .strap /  23 verify      V+    26 /  23
    BZXE  17 /  16                    CNOP  35 /  21
    XW    58 /  43                    LVI   44 /  23
    BD   117 /  76                    SIC  155 / 137
    B, LX, SX, NOP, Z: ubiquitous.

Nothing here is a first and nothing is reported as one.

====================================================================
GLYPHS.  docs/listing_typography.md settles by measurement that the
leading glyph of these labels is the LETTER I (letter I 10-18 px at
600 dpi, digit 1 never below 24 px and 99% at 30+, with a flag and a
base serif; populations that do not overlap on ~16 000 glyphs).  The
page's true spellings are therefore I68, I681, I683, I68ID, I68K1-3,
IC268, ICK268, I74 and the banner "----I268---".

THAT RENAME HAS SINCE BEEN MADE REPO-WIDE, so the page's spellings and
this file's are now one and the same.  THIS FILE FOLLOWS THE EXISTING
1268 FILES and starts no second convention: the measured letter-I
names in the assembler source, in the note column and in the prose
alike, exactly as verify_ax5b_1681_listing.py,
verify_ax5b_1268_test1bc_listing.py and verify_ax5b_1683_listing.py
now do.

WHEN THIS FILE WAS WRITTEN those three still carried the earlier
misreading -- a digit read for the letter, with an "L" prefixed to
make the name legal for this assembler -- so routine 1274's entry
label at 024412.00 had to be called out as the ONE exception: it is
written I74 in the .strap because programs/ax5b_1274_truncation.strap
already defines exactly that symbol at exactly that address, and
writing L174 would have invented a spelling no file in this repository
uses.  It is no longer an exception.

NO NEW GLYPH MEASUREMENT WAS MADE IN THIS SESSION, and no measurement
is claimed.

====================================================================
PROVEN DISCRIMINATING.  ELEVEN measurements against opcodes.py,
strap_asm.py and this block's own source.  EVERY FAILURE SET BELOW IS
OBSERVED OUTPUT, copied from the run; not one is predicted.

DISCIPLINE, because this project has been burned by both failure
modes.  `rm -rf __pycache__` was run in stretch/strap BEFORE AND
AFTER every injection -- stale bytecode has replayed a previous
injection's answer here and produced a false result.  And EVERY
INJECTION WAS CONFIRMED APPLIED BEFORE THE RUN: the patcher asserts
the target string occurs exactly once, rewrites it, and the patched
line is printed as a unified diff; a `sed` that silently fails to
match prints ALL TESTS PASSED, which reads exactly like a legitimate
measured null.  For the two source-side measurements (7 and 8) the
.strap is a NEW, UNTRACKED file, so `git diff` prints nothing for it
and could not serve as the confirmation; those two were confirmed by
the patcher's occurrence assertion plus a printed post-edit count.
Each injection was reverted by reversing the exact patch and `git
diff` confirmed clean afterwards.  THREE of the eleven are genuine
NULLS and are recorded with their arithmetic reason rather than
dropped, along with two attempts that aborted the assembler and
therefore measured nothing.

  1. strap_asm.enc_branch_or_misc: "(addr19, 19)" -> "(addr19 & ~1,
     19)", clearing bit 18 of every unconditional branch target.
     OBSERVED: exactly 2 failures, and they are exactly the two rows
     whose target is an ODD half-word --
       024376.40  '024363.44 00' -> '024363.04 00'
       024400.00  '024400.44 00' -> '024400.04 00'
     The other six branch rows target EVEN half-words, so their bit
     18 is already 0 and clearing it changes nothing.  0 symbol
     failures, 0 index rows, 0 SIC rows.  This is the bit-18 claim of
     section (a) made executable, and the split between the two
     failing rows and the six silent ones is the claim itself.

  2. opcodes.DIR_INDEX_CODES["SX"] 0b10001 -> 0b00001 (clears bit 23,
     making SX encode as LX).
     OBSERVED: exactly 2 failures, both SX rows, both moving only the
     OCTAL PAIR --
       024401.40  '024405.33 10' -> '024405.32 10'
       024333.40  '001437.03 10' -> '001437.02 10'
     0 symbol failures.  The 33-vs-32 contrast, isolated to one bit.

  3. strap_asm.enc_dir_index: field order "(addr19,19),(j,4),(code,5),
     (idx,4)" -> "(addr19,19),(code,5),(j,4),(idx,4)", i.e. J moved
     out of bits 19-22.
     OBSERVED: exactly 7 failures -- every LX, SX, V+ and KV row in
     both ranges, and nothing else --
       024400.40  '024405.32 10' -> '024405.01 D0'
       024401.00  '024523.32 B0' -> '024523.13 D0'
       024401.40  '024405.33 10' -> '024405.21 D0'
       024402.00  '024405.32 10' -> '024405.01 D0'
       024402.40  '024406.32 90' -> '024406.11 D0'
       024333.00  '024336.02 10' -> '024336.01 10'
       024333.40  '001437.03 10' -> '001437.21 10'
     0 symbol failures, 0 branch rows, 0 SIC rows, and the "Z,IC268"
     row at 024335.00 is untouched because Z is not a direct-index
     operation.  This is the empirical half of section (b): the
     printed pairs are incompatible with J anywhere but bits 19-22.

  4. strap_asm XW packing: "(mag << 40)" -> "(mag << 41)".
     OBSERVED: exactly 1 failure --
       024406.00  '600000.00 00 ...' -> '400000.00 00 ...'
     600000 octal shifted left one bit is 1400000, whose top bit
     falls out of the 64-bit word, leaving 400000 -- BIT 1 LOST, bit
     0 kept.  The other two XW rows (024405.00, 024411.00) are
     MEASURED NULLS with an arithmetic reason: their value operand is
     0, and 0 shifted is 0.  The sub-test count rests entirely on the
     one row that moved.

  5. strap_asm.statement_size, CNOP: "return FULL, 0" -> "return
     0, 0" (the round-up disabled).
     OBSERVED: exactly 1 failure --
       024404.40  '000000.30 00' -> '000000.00 00'
     0 symbol failures and NO pool address moved, because the
     full-word XW at 024405.00 aligns the counter on its own.  So the
     CNOP row witnesses the NOP, not the alignment.

  6. strap_asm.enc_branch_ind: the branchOn argument replaced by the
     literal 1 (bit 30 forced on).
     OBSERVED: exactly 1 failure, in the HEX BYTE only --
       024403.40  '001304.32 C0' -> '001304.32 C2'
     0 symbol failures.  The polarity claim made executable: the deck
     prints C0, bit 30 = 0, branch-when-OFF.

  7. SOURCE SIDE -- the "CNOP" line deleted from
     programs/ax5b_1268_tail_pool.strap before the pool.
     OBSERVED: exactly 1 failure, the same row as injection 5 --
       024404.40  '000000.30 00' -> '000000.00 00'
     This is the measurement that CORRECTED this file's first draft,
     which had claimed the row would still pass.  It does not: the
     automatic gap filler skips XW (see the CNOP section).

  8. SOURCE SIDE -- the silent p.110 "CNOP" line deleted.
     OBSERVED: A MEASURED NULL -- 0 failures, ALL TESTS PASSED.
     ARITHMETIC REASON: the counter is already on a word boundary at
     024336.00, so there is no gap to fill, and an SLC follows, so
     nothing downstream depends on it.  Recorded, not smoothed.

  9. strap_asm.enc_sic: the 24-bit bit address read as a 19-bit
     half-word address instead --
       "((addr24 & 0xFFFFFF) << 8)" -> "(((addr24 >> 5) & 0x7FFFF)
       << 13)".
     OBSERVED: A MEASURED NULL -- 0 failures, ALL TESTS PASSED, with
     the patched line printed as a diff before the run.
     ARITHMETIC REASON, and this is THE trap section (d) names: all
     three SIC operands in these ranges have a bit offset of 0 or 32
     (SEN at .00, SEN0+.32, and RET which is itself 1306.40).  Under
     the bit-address reading the offset field holds 0 or 40 octal;
     under the half-word reading bit 18 holds 0 or 1 and bits 19-23
     hold 0 -- WHICH IS THE SAME SIX BITS.  Thirty-two bits is also
     exactly one half-word, so no operand in this block can tell the
     two readings apart.  THE LISTING CANNOT SETTLE THIS AND THIS
     FILE DOES NOT PRETEND TO: it is settled by Reference Manual
     printed p.41 (PDF p.44) assigning bits 0-23 entire to the
     address, quoted in section (d).  A block containing a SIC with
     an offset that is not a multiple of 32 would discriminate it;
     this one does not, and injection 10 shows only that the field is
     live, not which reading of it is right.

 10. strap_asm.enc_sic: "(addr24 & 0xFFFFFF)" -> "((addr24 + 1) &
     0xFFFFFF)".
     OBSERVED: exactly 3 failures, all three SIC rows --
       024377.00  '001311.40 80' -> '001311.41 80'
       024403.00  '001310.00 80' -> '001310.01 80'
       024334.00  '001306.40 80' -> '001306.41 80'
     0 symbol failures.  This rules out the SIC rows being vacuous:
     the low-order bits of that field ARE checked, even though
     injection 9 shows the block cannot choose between the two
     readings of them.

 11. SOURCE SIDE, and the one that makes the file's headline claim
     executable -- TWO EXTRA "NOP" LINES inserted after "BD, I74",
     i.e. a transcription that got the row count wrong by one word.
     (The substituted "SLC, (8)24412.0 / PASS2 BEW, $" pair was
     removed for this one measurement, because a shifted pool
     otherwise collides with it and the assembler aborts instead of
     reporting.  Both edits were confirmed applied by occurrence
     count before the run and both reverted afterwards.)
     OBSERVED: 16 failures, and ALL FIVE SYMBOL ASSERTIONS ARE AMONG
     THEM --
       IC268  at 024405.00: assembled bit 672128, listing bit 672064
       ICK268 at 024406.00: assembled bit 672192, listing bit 672128
       I68K1  at 024407.00: assembled bit 672256, listing bit 672192
       I68K2  at 024410.00: assembled bit 672320, listing bit 672256
       I68K3  at 024411.00: assembled bit 672384, listing bit 672320
     -- each exactly 64 bits, one full word, too high.  Eleven rows
     fail with them, including the CROSS-PAGE one:
       024335.00  '024405.22 00' -> '024406.22 00'   (p.110's Z,IC268)
       024400.40  '024405.32 10' -> '024406.32 10'   (p.111's LX)
       024402.40  '024406.32 90' -> '024407.32 90'   (p.111's KV)
     So the five pool addresses are DERIVED from the row count, and
     a one-word error in that count is caught by the printed location
     column AND, independently, by the machine-code column of two
     different pages.  That is the witness claim, measured.

  TWO FURTHER SIZE INJECTIONS, and what they actually showed, stated
  without upgrading it.  Both made the assembler REFUSE TO BUILD
  rather than produce a mismatch:

    statement_size XW "return FULL, FULL" -> "return FULL, HALF"
      AssemblerError: internal: two statements deposited overlapping
      bits in word 10502 (= 024406 octal = ICK268).
    statement_size bare NOP "return HALF, HALF" -> "return HALF, FULL"
      AssemblerError: ... in word 10506 (= 024412 octal = routine
      1274's first word).

  THESE TWO MEASURED NOTHING about the pool addresses and are not
  claimed to.  The cause is mechanical: strap_asm emits each
  statement with a fixed deposit width, so changing a statement's
  SIZE without changing its emission makes it overlap its neighbour,
  and the overlap detector fires before any row is compared.  Two
  further attempts in the same family (branch/misc alignment forced
  to FULL; XW and CNOP alignment both removed) aborted the same way.
  Injection 11 is what actually reaches the symbol assertions,
  because it changes the row COUNT rather than a row's size.

  One more recorded null, because it is informative about WHY the
  pool is hard to move: strap_asm's SLC handler "loc = new_loc" ->
  "loc = new_loc + 32", shifting every block by one half-word.
  OBSERVED: 21 failures -- every transcribed row, plus the ABSENT
  assertion at 024336.00 firing (which incidentally shows that check
  is live) -- but ZERO SYMBOL FAILURES.  ARITHMETIC REASON: the
  full-word alignment of the XW at 024405.00 absorbs a half-word
  shift entirely, so the pool labels land on the same addresses.
  Only a whole-word change moves them, which is what injection 11
  does.

====================================================================
WHAT THIS FILE CANNOT SEE.  The ident word at 024336.00 and the
%IQSZ macro's expansion.  Routine 1274's body beyond its first
address.  p.114's BIT table.  Whether any of this EXECUTES: SSIP's
SEN/SEN0/SERS/SSW/RET/IDF1/DPET13 are substituted hangs and scratch
words, and this session was instructed not to run bsc,
run_program.sh, run_tests.sh or mutation_score.py.  This is an
ENCODING oracle and it is not wired into run_tests.sh.
"""
import sys

from strap_asm import assemble
from listing_oracle import check_rows, finish, loc_bits

prog = assemble(open("programs/ax5b_1268_tail_pool.strap").read())

# Rows marked (ext) name a symbol given by SYN from a printed column;
# see WITNESS TIERING.  Rows with no (ext) name a symbol DERIVED
# inside the transcribed range, or nothing at all.
TAIL_ROWS = [
    # ---- loop once, return to SSIP ---------------------------------
    ('024376.00', '24377.10 00',
     'B,$+1.0               self-relative: pair 10, bit 18 -> 024377.00'),
    ('024376.40', '24363.44 00',
     'BD,I683               (ext) pair 44, bit 18 = 1 -> 024363.40'),
    ('024377.00', '1311.40 80',
     'SIC,SEN0+.32          (ext) pair 40 = a BIT offset of 32'),
    ('024377.40', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP"  -- NO period here'),
    ('024400.00', '24400.44 00',
     'BD,$+.32              self-relative: +32 bits -> 024400.40'),
    # ---- the continuity register, test 2's bit ---------------------
    ('024400.40', '24405.32 10',
     'LX,$X13,IC268         "-UPDATE CONTINUITY CHECK."  IC268 derived'),
    ('024401.00', '24523.32 B0',
     'V+,$X13,BIT1          (ext) test 2 done = bit 1; 24522 + 1'),
    ('024401.40', '24405.33 10',
     'SX,$X13,IC268         pair 33 vs the LX row"s 32: bit 23'),
    # ---- the continuity CHECK --------------------------------------
    ('024402.00', '24405.32 10',
     'LX,$X13,IC268         read it back for the compare'),
    ('024402.40', '24406.32 90',
     'KV,$X13,ICK268        against the expected word; ICK268 derived'),
    ('024403.00', '1310.00 80',
     'SIC,SEN               (ext) bit address, NOT a half-word select'),
    ('024403.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-CONTINUITY ERROR."  hex C0: bit 30 = 0'),
    # ---- fall through into routine 1274 ----------------------------
    ('024404.00', '24412.04 00',
     'BD,I74                (ext) bit 18 = 0 -> 024412.00, PDF p.112'),
    ('024404.40', '0.30 00',
     'CNOP                  the page prints a LOCATION and "0.30 00"'),
    # ---- the constant pool -----------------------------------------
    ('024405.00', '0.00 00 000000.00 00',
     'IC268 XW,0,0,0        "-CONTINUITY REG 1268."'),
    ('024406.00', '600000.00 00 000000.00 00',
     'ICK268 XW,%8*600000.00,0,0   bits 0 AND 1: TWO sub-tests'),
    ('024407.00', '22.22 00',
     'I68K1 Z,$X2           the OLD instruction tests 1A/1B/1C plant'),
    ('024407.40', '0.30 00',
     'NOP                   I68K1"s right half'),
    ('024410.00', '777777.45 01',
     'I68K2 LVI,$X2,%8*777777.40   the NEW one; pair 45, bit 18 = 1'),
    ('024410.40', '0.30 00',
     'NOP                   I68K2"s right half'),
    ('024411.00', '0.00 00 000000.00 00',
     'I68K3 XW,0,0,0        test 2A"s scratch word'),
]

ENTRY_ROWS = [
    ('024333.00', '24336.02 10',
     'I68 LX,$X1,I68ID     (ext) "-UPDATE IDENT."  24336 vs the'
     ' printed location column'),
    ('024333.40', '1437.03 10',
     'SX,$X1,DPET13         (ext) pair 03 vs the LX row"s 02: bit 23'),
    ('024334.00', '1306.40 80',
     'SIC,RET               (ext) RET is itself the bit address 1306.40'),
    ('024334.40', '1443.10 00',
     'B,IDF1                (ext) "-PRINT IDENT."'),
    ('024335.00', '24405.22 00',
     'Z,IC268               p.110 corroborates p.111"s pool address'),
    ('024335.40', '24337.04 00',
     'BD,I681               (ext) bit 18 = 0 -> 024337.00'),
    # The CNOP that follows prints NEITHER a location NOR machine
    # code, so there is no row for it.  See check_absent().
]

# Derived inside BLOCK A from the single SLC at 024376.0, and checked
# here against the LOCATION COLUMN printed on the right of PDF p.111.
# These five are the witnesses this file adds; all three existing 1268
# files currently take them as SYN'd inputs.
SYMBOLS = {
    'IC268':  '024405.00',
    'ICK268': '024406.00',
    'I68K1':  '024407.00',
    'I68K2':  '024410.00',
    'I68K3':  '024411.00',
}


def check_absent(prog, octal_loc, why):
    """Assert the assembled image has NO word at octal_loc.  The
    listing prints a location there and an EMPTY machine-code column,
    so fabricating a word would be the error this checks for."""
    word = loc_bits(octal_loc) // 64
    ok = word not in prog.words
    print(f"{'PASS' if ok else 'FAIL'} 1268 tail {octal_loc} ABSENT "
          f"({why}): assembled {'nothing' if ok else hex(prog.words[word])}")
    return not ok


fails = check_rows(prog, TAIL_ROWS, SYMBOLS, label='1268 tail ')
fails += check_rows(prog, ENTRY_ROWS, label='1268 entry ')
fails += check_absent(prog, '024336.00',
                      'the ident row: a location, no machine code')
finish(fails)
