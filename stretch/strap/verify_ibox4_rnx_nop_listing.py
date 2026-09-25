#!/usr/bin/env python3
"""verify_ibox4_rnx_nop_listing.py -- jb_ax4b "IBOX-4", routine 1244
("RENAME CHECK"), TEST 4 (programs/ibox4_rnx_nop.strap) against the
listing's printed machine code: the driver at labels I4412-I4422, PDF
pp.90-91, octal 006470.00-006523.40, the two data words that close the
routine (006524.00-006525.00), and the "-CONSTANTS FOR 1244." block on
PDF p.98 (006726.00-006735.00).  56 code rows, 10 data rows.

CITED BY PDF PAGE, AND THAT IS A CORRECTION.  jb_ax4b's listing pages
carry NO printed page numbers.  PDF p.90 was rendered at 300 dpi and
its top strip, bottom strip, left edge and right edge were all read --
there is no folio anywhere on the sheet, and the front write-up carries
none either.  What fixes which pages to read is content, and it agrees
at offset ZERO with every number this repo already uses for this deck:
PDF p.85 is the 1244 header, PDF p.90 this block, PDF p.93 error table
1's entries 11-21, PDF p.190 the I00Z/I00VO constants at
013034.00/013036.00 that programs/ibox4_refill_nop.strap already cites
as "p.190".  So "p.NN" for jb_ax4b means the PDF's own page, as it
already did in verify_ibox4_listing.py.  The printed-to-PDF offset is 0
because there is nothing to offset from.

WHAT TEST 4 CHECKS.  Routine 1244's header (PDF p.85), item 4, verbatim:

    -4. CHECK THAT THE INSTRUCTION IS
        -NO OPPED WHEN EITHER THE
        -OLD OR THE NEW REFILL FIELD
        -OF IX REG 0 LIES IN THE
        -RANGE OF 1 TO 37 OCTAL.

That is a SECOND refill-address no-op rule over a DIFFERENT range from
the one routine 1238 establishes for R/RCZ.  1238's header says "NOPING
IF RF IS FROM 1 TO 15" and its test 2 pins that boundary from both
sides (verify_ibox4_refill_nop_listing.py).  1244 says 1 to 37 octal --
1 to 31 decimal -- for RNX.  Two instructions, two ranges, one deck:
the rule for one is not the rule for the other by symmetry.

The Reference Manual gives RNX the wider range and disagrees with the
deck at the bottom end.  22-6530-2, printed p.27 (PDF p.30 -- footer
"Operand Designation  27"; the +3 offset for this manual is the one
verify_ax5b_162_test3a_listing.py already records), section "Rename
(RNX)", read first-hand at 150 dpi:

  "The index word in the index register specified by the field J is
  stored in the location addressed by the refill field of X0.  The
  refill field of X0 is then replaced by bits 0-17 of the effective
  address.  The remaining bits of X0 remain unchanged.  Next, the index
  word specified by J is replaced by the word in core storage addressed
  by the new refill field of X0.  When either the old or the new name
  of the index refers to one of the locations 0-31, the instruction is
  executed as no-operation and indicator AD is set."

Manual: 0-31.  Deck header: 1 to 37 octal.  That paragraph is also why
TEST 4 has two halves with an error table each: the OLD name is index
0's refill field (set by the patched "LRI,$X0,0.0" at 006477.00), the
NEW name is "bits 0-17 of the effective address" (supplied by the
patched "RNX,$X1,I4418" at 006505.00).  The tables' own words, "IX 0
INITIAL REFILL ADDRESS" and "EFFECTIVE ADDRESS", are the manual's two
names for those two things.

AND THE SAME PAGE PRINTS THE FIELD BOUNDARY the RNX rows rest on.
Directly above that paragraph the manual gives RENAME's format, tick
marks at ADDRESS 0, J 19, OP. 23, I 28, 31 -- so the direct-index
operation code is bits 23-27, five bits straddling the printed octal
pair and the printed hex byte.  The decomposition used below is read
off that diagram, not inferred from two samples.

AND THE DECK KNOWS IT.  PDF p.98's constants block carries both
answers, checked row for row below:

    I44XW1  XW,I44B1,0,0        6530.00 00 000000.00 00   006730.00
    I44XW2  XW,I44B2,0,0        6630.00 00 000000.00 00   006731.00
    I44XW3  XW,1.0,31,0            1.00 00 000760.00 00   006732.00
            -IF 0 BECOMES ILLEGAL FOR RNX, USE THE
            -FOLLOWING THREE INDEX WORDS TO REPLACE
            -THOSE DIRECTLY ABOVE.
    I44XWA  XW,I44B1A,0,0       6526.00 00 000000.00 00   006733.00
    I44XWB  XW,I44B2A,0,0       6626.00 00 000000.00 00   006734.00
    I44XWC  XW,0.0,32,0            0.00 00 001000.00 00   006735.00

As shipped the walk starts at 1.0 with a count of 31 and covers 1
through 37 octal, matching the routine header.  The spare triple starts
at 0.0 with a count of 32 and points at the "ADDRESS IS 0." entries of
both error tables, to be swapped in "IF 0 BECOMES ILLEGAL FOR RNX" --
i.e. if the machine turns out to match the manual's "0-31".  The zero
boundary was an open question to the people who wrote the test, and
they shipped the patch instead of choosing.  Both triples are checked.

THE TWO ERROR TABLES are printed on these pages and their text is the
contract.  Read first-hand at 100 dpi, PDF pp.92-94 and pp.95-97:

    -ERROR BRANCH TABLE 1.
    -YOU CAME TO THIS ERROR TABLE FROM I4416
  I44B1A  SIC,SEN        -RNX FAILS TO NOP WHEN IX 0 INITIAL REFILL
          B,SERS         -ADDRESS IS 0.
          V+I,$X10,1.0
          B,I4417
  I44B1   ...            -ADDRESS IS 1.  ... through -ADDRESS IS 31.

    -ERROR BRANCH TABLE 2.
    -YOU CAME TO THIS ERROR TABLE FROM I4419
  I44B2A  SIC,SEN        -RNX FAILS TO NOP WHEN EFFECTIVE
          B,SERS         -ADDRESS IS 0.
          V+I,$X10,1.0
          B,I4420
  I44B2   ...            -ADDRESS IS 1.  ... through -ADDRESS IS 31.

Table 1 runs 006526.00-006625.40, table 2 runs 006626.00-006725.40, 32
entries of 2 words each.  An entry reports, bumps the error counter
$X10 and BRANCHES BACK INTO THE LOOP -- I4417 for table 1, I4420 for
table 2 -- so a failure is counted, not fatal.

BOTH TABLES ARE STUBBED, NOT TRANSCRIBED.  Sixty-four entries of four
identical half-words would add nothing this file does not already
check.  Each table gets eight bare "BEW,$" halts at its own address:
enough to define I44B1A/I44B1 and I44B2A/I44B2 for the index words
above, and to stop a wrong branch instead of letting it run on -- what
programs/ibox4_refill_nop.strap does with 1238's table at 005674.00.
Entries 2 through 31 of each table are NOT transcribed and NOT checked.

RNX'S FIRST LISTING WITNESS IN THIS REPO.  No verify_*.py contains an
RNX row.  The name occurs four other places and none is a transcribed
instruction: opcodes.py's DIR_INDEX_CODES entry,
audit_opcode_coverage.py's coverage list, a COMMENT in
programs/ibox4_refill_nop.strap (echoed into run_tests.sh) noting that
ja_ax1a's constants print "$RNX" as a patchable constant WORD -- a
datum, never transcribed -- and a COMMENT in
programs/problem_2_2_method3.strap recording that bsv does not
implement it.  These two rows are the first:

    006477.40  RNX,$X1,I44D2   6727.03 F0
    006505.00  RNX,$X1,I4418   6505.03 F0

and they pin the 5-bit direct-index code.  Bit 23 is the top bit of the
code and bits 24-27 the rest: octal pair 03 = 000011 gives bit 23 = 1,
hex F0 = 11110000 gives bits 24-27 = 1111, so the code reads 1 1111 =
0b11111 -- DIR_INDEX_CODES["RNX"].  The same decomposition on the
neighbouring "LX,$X1,I44D2" (6727.02 10) gives 0 0001 = 0b00001,
DIR_INDEX_CODES["LX"], which is how the field boundary was fixed rather
than assumed.  RNX lives in DIR_INDEX_CODES, with LX/SX/SVA -- not in
MISC_CODES.

THIS IS AN ENCODING ORACLE AND COULD NOT BE ANYTHING ELSE.
bsv/StretchDecode.bsv does define dixop_RNX = 5'b11111 and
StretchTypes.bsv names it, so the word DECODES; but
StretchExecute.bsv:2693 falls through to "default: ind =
setOpInvalid(ind); // RNX, LVE: out of scope", so the model executes it
as Operation Code Invalid, and StretchSmoke.bsv uses RNX as its
deliberate "structurally-valid opcode" that sets OP.  There is nothing
to run; what a listing settles is the bit pattern.

THE BLOCK'S ADDRESS WITNESSES, self-checked by decoding BIT 18 out of
the printed octal pair and matching the page's own label column.  There
are thirteen in-range branch targets plus four self-relatives, against
the two that ax5b_162_test3a could muster, and -- unlike that block --
five of them have BIT 18 SET:

  006471.40  SVA,$X15,I4416 -> 6501.37 D0.  Pair 37 = 011111, bit 18 =
             0 -> 006501.00, where p.90 prints label I4416.
  006472.00  SVA,$X14,I4419 -> 6507.35 D0.  35 = 011101 -> 006507.00 =
             I4419.
  006472.40  SVA,$X12,I4415 -> 6477.31 D0 -> 006477.00 = I4415.
  006473.00  SVA,$X12,I4418 -> 6505.31 D0 -> 006505.00 = I4418.
  006500.40  BXVZ,$+1.0     -> 6501.71 42.  71 = 111001, BIT 18 = 1 ->
             006501.40, and 006500.40 + one word = 006501.40.
  006501.40  BXCZ,I4416     -> 6501.30 42 -> 006501.00 = I4416.
  006505.00  RNX,$X1,I4418  -> 6505.03 F0 -> 006505.00, its own row.
  006506.00  BXVZ,I4419     -> 6507.31 42 -> 006507.00 = I4419.
  006506.40  BXCZ,I4420     -> 6507.70 42.  70 = 111000, BIT 18 = 1 ->
             006507.40, where p.90 prints label I4420.
  006510.00  BZXVZ,I4421    -> 6512.31 40 -> 006512.00 = I4421.
  006511.00  BXCZ,$+1.0     -> 6512.30 42 -> 006512.00, one word on.
  006511.40  BD,I4414       -> 6474.44 00.  44 = 100100, BIT 18 = 1 ->
             006474.40, where p.90 prints label I4414.
  006512.40  BXCZ,I4422     -> 6515.30 42 -> 006515.00 = I4422.
  006514.40  B,I4413        -> 6471.50 00.  50 = 101000, BIT 18 = 1 ->
             006471.40 = I4413.
  006515.00  B,$+1.0        -> 6516.10 00 -> 006516.00.
  006515.40  BD,I4412       -> 6470.04 00 -> 006470.00 = I4412.
  006517.00  BD,$+.32       -> 6517.44 00.  44 = 100100, BIT 18 = 1 ->
             006517.40, and 006517.00 + 32 bits = 006517.40.

I4412 is deliberately NOT counted among them: the SLC sets the counter
to 006470.0 and I4412 is the first label after it, so checking it
checks the SLC against the number this transcription handed the SLC.
It is asserted below as the block's anchor; it is not evidence.  The
same caveat ax5b_162_test3a.strap makes about I62100.

ONE ROW IN THE BLOCK IS NOT A HALF-WORD SELECT AT ALL, and saying so is
the point of the format note: "SIC,SENO+.32" at 006516.00 prints
1311.40 80, and there the octal pair 40 is a BIT OFFSET of 32 within
word 001311, not bit 18 and a half-word select.  SIC's own format
(Reference Manual p.41) puts a 24-bit BIT address in bits 0-23.  The
row checks out either way; the field does not mean what it means two
rows up.

EXTERNALS ARE INPUTS, NOT WITNESSES.  Every SYN in the program file
(SEN, SENO, SERS, SSW, I00VO, BIT3, I46) makes its address field come
out right by construction, so the rows naming one prove only that this
assembler places every OTHER field where the listing places it -- the
caveat verify_ax5b_16082_16083_listing.py makes about I6088.  Two have
a second, independently read page behind them: I00VO at 013036.00 from
PDF p.190's own label column, and BIT3 at 013057.00 from PDF p.191's
("BIT3  XW,%8@40000.00,0,0").  That is corroboration; it does not turn
an input into a witness.  SEN/SERS/SSW rest on other verify files in
this repo, and I46's address comes from the very operand field it
appears in.  By contrast IC244, ICK244, I44D1, I44D2 and I44XW1-3 are
DEFINED INSIDE the transcribed range at addresses the location counter
computes, so every row naming one of them is a real address check.

THE FOUR STUB HEADS ARE ANCHORS, NOT WITNESSES, and the same reasoning
that exempts I4412 exempts them.  I44B1A and I44B2A sit at the
addresses two SLCs put them at, typed from the address columns of PDF
pp.92 and 95, so I44XWA printing 6526.00 and I44XWB printing 6626.00
check this transcription against its own SLCs.  I44B1 and I44B2 are
only marginally better -- four stub half-words have to be sized right
for each to land -- and the XW rows naming them still trace back to an
SLC.  They are asserted below because a wrong one would silently
mis-aim the stubs, not because they are evidence.

SUBSTITUTIONS: two, all mechanical, where this docstring used to name
three.  The one that went read "digit-leading labels take an 'L'
prefix, as ax5b_162_test3a.strap already does".  They are not
digit-leading: measured at 600 dpi the leading glyph is the LETTER I
(ax4b p.90's "I4412 LX,$X15,I44XW1" reads I 10, 4 47, 4 49, 1 33,
2 40 -- letter and digit in one token), so I4412..I4422, I44D1/2,
I44XW1..3, I46 and the rest are legal STRAP-1 symbols unaided and
ax5b_162_test3a.strap no longer prefixes either
(docs/listing_typography.md).  The listing's "$B,0" at
I4416 and I4419 is written "B, 0" -- the dollar prefix is the deck's
mark for an opcode assembled as a patchable word (ja_ax1a's "$L%BU" and
"$RNX"; 1238's I3825 at 005537.00 does the same), and it changes no
bit: the printed code is 0.10 00, a plain B to address 0.  And "%8@" is
written "(8)".  That last one is load-bearing: the listing's default
radix is decimal -- "LCI,$X11,10" prints 12.27 02, ten in bits 0-17 --
and so is this assembler's, so an unmarked 777777 would assemble
decimal.  The same point ax5b_162_test3a.strap makes about "(8)3740".

PROVEN DISCRIMINATING.  Observed failure sets, not predicted -- every
injection was made with __pycache__ cleared on BOTH sides of the run,
and opcodes.py restored from a byte-for-byte copy afterwards:

  DIR_INDEX_CODES["RNX"] 0b11111 -> 0b01111   (the code's TOP bit)
      006477.40  RNX -> "6727.02 F0"                       (2 rows)
      006505.00  RNX -> "6505.02 F0"
      OCTAL PAIR ONLY: 03 -> 02, hex byte unchanged at F0, because the
      top bit of the 5-bit direct-index code is IBM bit 23 and bit 23
      is the bottom bit of the printed octal pair.

  DIR_INDEX_CODES["RNX"] 0b11111 -> 0b11110   (the code's BOTTOM bit)
      006477.40  RNX -> "6727.03 E0"                       (2 rows)
      006505.00  RNX -> "6505.03 E0"
      HEX BYTE ONLY: F0 -> E0, octal pair unchanged at 03, because
      bits 24-27 are the top nibble of the hex byte.
      Together these two are the encoding oracle: they move nothing
      but the two RNX rows, they move them in the two DIFFERENT
      printed columns, and between them they exercise both ends of
      the field.  A check reading only one column would miss one.

  MISC_CODES["Z"] 0b100 -> 0b101
      006474.00  Z,$X10  -> "32.26 00"                     (5 rows)
      006474.40  Z,$X1   -> "21.26 00"
      006475.40  Z,I44D1 -> "6726.26 00"
      006502.00  Z,$X1   -> "21.26 00"
      006503.00  Z,I44D1 -> "6726.26 00"
      Octal pair only, and on the block's most-repeated opcode.

  INDICATOR_BITS["XVZ"] 50 <-> "XVGZ" 51
      006500.40  BXVZ,$+1.0    -> "6501.71 C2"             (3 rows)
      006506.00  BXVZ,I4419    -> "6507.31 C2"
      006510.00  BZXVZ,I4421   -> "6512.31 C0"
      Hex byte only, and note WHERE: 50 and 51 differ solely in the
      bit that lands at 24, so the octal pair -- which carries the
      indicator's high bits AND bit 18 -- is untouched.  The same
      shape as ax5b_162_test3a's AD 16->17 injection.

  IMM_INDEX_CODES["LCI"] 0b0010 -> 0b0110
      006473.40  LCI,$X11,10        -> "12.27 06"          (3 rows)
      006475.00  LCI,$X1,(8)777777  -> "777777.03 06"
      006502.40  LCI,$X1,(8)777777  -> "777777.03 06"

AND ONE INJECTION THIS BLOCK DOES *NOT* CATCH, recorded because a
negative result measured is worth more than a positive one assumed.
Dropping "LRI" from IMM_INDEX_COUNT_OPS -- which switches the operand
from the 18-bit count field (eval_addr_field shift 6, then <<1) to the
19-bit value field (shift 5) -- leaves every row here unchanged and the
run green.  The reason is arithmetic, not luck: both of this block's
LRI operands are WORD-ALIGNED ("0.0" and I44D2 at 006727.00), and for a
word-aligned operand (bits>>6)<<1 and bits>>5 are the same number.  So
these two rows witness LRI's opcode and its J field but say NOTHING
about which of the two field layouts is right; only an LRI with a
half-word-odd operand could, and this block has none.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ibox4_rnx_nop.strap").read())

# PDF p.91 (the routine's own continuity words) and PDF p.98
# ("-CONSTANTS FOR 1244.").  All ten are defined inside the
# transcription, so these are checks, not SYN-fed inputs.
DATA_ROWS = [
    ('006524.00', '0.00 00 000000.00 00',
     'IC244 XW,0,0,0   "-CONTINUITY REG 1244."'),
    ('006525.00', '740000.00 00 000000.00 00',
     'ICK244 XW,%8@740000.00,0,0'),
    ('006726.00', '0.00 00 000000.00 00',
     'I44D1 XW,0,0,0'),
    ('006727.00', '0.00 00 000000.00 00',
     'I44D2 XW,0,0,0'),
    ('006730.00', '6530.00 00 000000.00 00',
     'I44XW1 XW,I44B1,0,0   -> error table 1, entry "1"'),
    ('006731.00', '6630.00 00 000000.00 00',
     'I44XW2 XW,I44B2,0,0   -> error table 2, entry "1"'),
    ('006732.00', '1.00 00 000760.00 00',
     'I44XW3 XW,1.0,31,0    start 1.0, count 31 = 1 to 37 octal'),
    ('006733.00', '6526.00 00 000000.00 00',
     'I44XWA XW,I44B1A,0,0  the "IF 0 BECOMES ILLEGAL" spare'),
    ('006734.00', '6626.00 00 000000.00 00',
     'I44XWB XW,I44B2A,0,0  the "IF 0 BECOMES ILLEGAL" spare'),
    ('006735.00', '0.00 00 001000.00 00',
     'I44XWC XW,0.0,32,0    start 0.0, count 32 = the manual"s 0-31'),
]

# PDF p.90, 006470.00-006521.40, then PDF p.91, 006522.00-006523.40.
CODE_ROWS = [
    ('006470.00', '6730.36 10', 'I4412 LX,$X15,I44XW1   "-SETUP"'),
    ('006470.40', '6731.34 10', 'LX,$X14,I44XW2'),
    ('006471.00', '6732.30 10', 'LX,$X12,I44XW3'),
    ('006471.40', '6501.37 D0', 'I4413 SVA,$X15,I4416   bit 18 -> 006501.00'),
    ('006472.00', '6507.35 D0', 'SVA,$X14,I4419          bit 18 -> 006507.00'),
    ('006472.40', '6477.31 D0', 'SVA,$X12,I4415          bit 18 -> 006477.00'),
    ('006473.00', '6505.31 D0', 'SVA,$X12,I4418          patches RNX"s own field'),
    ('006473.40', '12.27 02',   'LCI,$X11,10              DECIMAL ten -> 0o12'),
    ('006474.00', '32.22 00',   'Z,$X10                   the error counter'),
    ('006474.40', '21.22 00',   'I4414 Z,$X1             "-START TEST."'),
    ('006475.00', '777777.03 02', 'LCI,$X1,(8)777777      octal marker load-bearing'),
    ('006475.40', '6726.22 00', 'Z,I44D1'),
    ('006476.00', '13036.04 10', 'LX,$X2,I00VO            (ext) PDF p.190'),
    ('006476.40', '6727.05 10', 'SX,$X2,I44D2'),
    ('006477.00', '0.01 03',    'I4415 LRI,$X0,0.0       address field patched'),
    ('006477.40', '6727.03 F0', 'RNX,$X1,I44D2           RNX WITNESS 1: code 0b11111'),
    ('006500.00', '21.02 10',   'LX,$X1,$X1'),
    ('006500.40', '6501.71 42', 'BXVZ,$+1.0               BIT 18 SET -> 006501.40'),
    ('006501.00', '0.10 00',    'I4416 B,0               listing "$B,0" -BRANCH TO ERROR TABLE 1.'),
    ('006501.40', '6501.30 42', 'BXCZ,I4416              bit 18 -> 006501.00'),
    ('006502.00', '21.22 00',   'I4417 Z,$X1'),
    ('006502.40', '777777.03 02', 'LCI,$X1,(8)777777'),
    ('006503.00', '6726.22 00', 'Z,I44D1'),
    ('006503.40', '13036.04 10', 'LX,$X2,I00VO            (ext)'),
    ('006504.00', '6727.05 10', 'SX,$X2,I44D2'),
    ('006504.40', '6727.01 03', 'LRI,$X0,I44D2           a LEGAL old refill'),
    ('006505.00', '6505.03 F0', 'I4418 RNX,$X1,I4418    RNX WITNESS 2: self-referential'),
    ('006505.40', '6727.02 10', 'LX,$X1,I44D2'),
    ('006506.00', '6507.31 42', 'BXVZ,I4419              bit 18 -> 006507.00'),
    ('006506.40', '6507.70 42', 'BXCZ,I4420              BIT 18 SET -> 006507.40'),
    ('006507.00', '0.10 00',    'I4419 B,0               listing "$B,0" -BRANCH TO ERROR TABLE 2.'),
    ('006507.40', '32.24 10',   'I4420 LX,$X10,$X10'),
    ('006510.00', '6512.31 40', 'BZXVZ,I4421             "-TO NEXT ADDRESS"'),
    ('006510.40', '1.27 08',    'C-I,$X11,1               "-NO ERROR, CONTINUE."'),
    ('006511.00', '6512.30 42', 'BXCZ,$+1.0'),
    ('006511.40', '6474.44 00', 'BD,I4414                BIT 18 SET -> 006474.40'),
    ('006512.00', '1.31 08',    'I4421 C-I,$X12,1'),
    ('006512.40', '6515.30 42', 'BXCZ,I4422              bit 18 -> 006515.00'),
    ('006513.00', '1.31 05',    'V+I,$X12,1.0             next trial address'),
    ('006513.40', '2.35 05',    'V+I,$X14,2.0             next table 2 entry'),
    ('006514.00', '2.37 05',    'V+I,$X15,2.0             next table 1 entry'),
    ('006514.40', '6471.50 00', 'B,I4413                 BIT 18 SET -> 006471.40'),
    ('006515.00', '6516.10 00', 'I4422 B,$+1.0'),
    ('006515.40', '6470.04 00', 'BD,I4412                bit 18 -> 006470.00'),
    ('006516.00', '1311.40 80', 'SIC,SENO+.32             (ext) pair 40 is a BIT OFFSET'),
    ('006516.40', '1301.10 00', 'B,SSW                    (ext) "-TO SSIP"'),
    ('006517.00', '6517.44 00', 'BD,$+.32                 BIT 18 SET -> 006517.40'),
    ('006517.40', '6524.32 10', 'LX,$X13,IC244            "-UPDATE CONTINUITY CHECK."'),
    ('006520.00', '13057.32 B0', 'V+,$X13,BIT3            (ext) PDF p.191'),
    ('006520.40', '6524.33 10', 'SX,$X13,IC244'),
    ('006521.00', '6524.32 10', 'LX,$X13,IC244            "-UPDATE CONTINUITY CHECK."'),
    ('006521.40', '6525.32 90', 'KV,$X13,ICK244'),
    ('006522.00', '1310.00 80', 'SIC,SEN                  (ext)'),
    ('006522.40', '1304.32 C0', 'BZXE,SERS                (ext) "-CONTINUITY ERROR."'),
    ('006523.00', '6736.10 00', 'B,I46                   (ext)'),
    ('006523.40', '0.30 00',    'CNOP                     the gap filler"s NOP'),
]

# Labels DEFINED inside the transcription.  I4412 is the block's
# anchor, not evidence: the SLC put the counter there.  So are the four
# I44B* stub heads and I44D1/I44D2/I44XW*, each of which follows an
# SLC typed from the listing's address column -- see the docstring.
# The rest (I4413-I4422, IC244, ICK244) fall out of the location
# counter and are the real checks.
SYMBOLS = {
    'I4412': '006470.00', 'I4413': '006471.40', 'I4414': '006474.40',
    'I4415': '006477.00', 'I4416': '006501.00', 'I4417': '006502.00',
    'I4418': '006505.00', 'I4419': '006507.00', 'I4420': '006507.40',
    'I4421': '006512.00', 'I4422': '006515.00',
    'IC244': '006524.00', 'ICK244': '006525.00',
    'I44B1A': '006526.00', 'I44B1': '006530.00',
    'I44B2A': '006626.00', 'I44B2': '006630.00',
    'I44D1': '006726.00', 'I44D2': '006727.00',
    'I44XW1': '006730.00', 'I44XW2': '006731.00', 'I44XW3': '006732.00',
    'I44XWA': '006733.00', 'I44XWB': '006734.00', 'I44XWC': '006735.00',
}

if __name__ == "__main__":
    fails = check_rows(prog, DATA_ROWS, SYMBOLS, label='1244 T4 ')
    fails += check_rows(prog, CODE_ROWS, label='1244 T4 ')
    finish(fails)
