#!/usr/bin/env python3
"""verify_ax5b_162_int_entry_listing.py -- jb_ax5b "I-Box 5", routine
1262's INTERRUPT ENTRY and constant pool
(programs/ax5b_162_int_entry.strap) against the listing's printed
machine code, PDF p.109 whole, octal 024172.00-024331.00.  54 printed
rows.

CITED BY PDF PAGE.  jb_ax5b's listing pages carry no printed page
numbers; the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering.

THE ROW THE PAGE EXISTS FOR:

    024320.00  I62ITE  BD,$  "-ALL INTERRUPTS ENTER HERE."  24320.04 00
    024320.40          B,$                                  24320.50 00

One full word, two self-branches, differing in exactly one thing: the
.00 half is BRANCH DISABLED and the .40 half is BRANCH.  Reference
Manual printed p.40 (PDF p.43): "Branch Disabled (BD).  This operation
disables the interruption mechanism, and then performs the same
operation as BRANCH."  So the landing half decides whether the
interrupt routine runs disabled, and 1262 chooses per test by storing
a different constant into the 64-word table:

    024172.00  I62K1  BD,I62ITE     24320.04 00   -> lands at .00
    024177.00  I62K6  B,I62ITE+.32  24320.50 00   -> lands at .40

each a full word carrying the same half-word instruction TWICE, which
is what makes it storable into one table entry ("SX,$X2,I62INT%$X1@",
PDF p.93, at 023475.40 for I62K6 and 023523.00 for I62K1).

WHICH HALF A GIVEN TEST AIMS AT is settled by bit 18, the top bit of
the printed octal pair: I62K1's "04" = 000100 has bit 18 = 0 ->
024320.00, the BD half; I62K6's "50" = 101000 has bit 18 = 1 ->
024320.40, the B half.  The rule the pages show is TRANSPARENCY rather
than "enabled": the B half is used wherever the landing must not
change the enable state because the block is about to MEASURE it --
p.93's I6225 probes "am I still disabled?" (it is disabled throughout:
"BD,$+.32" at 023476.40, "BD,I60S1" at 023500.40, and the subject BE's
enabling suppressed by EXE) and I6229/I6232 probes "am I still
enabled?", and BOTH write "SVA,$X1,I62ITE+.32".  The BD half is used
where disabling on landing costs nothing, as in TEST 3A and TEST 3B
(pp.107-108), whose landing is the end of the test; both write
"SVA,$X1,I62ITE".

ONE CONJECTURE, FLAGGED AS ONE.  That the table still holds I62K1 when
TEST 3B runs is not read here: pp.94-107 were not swept, and p.93's
I6233 block ("-DO BB, SETUP BD INT TBL.", which loads I62K1) is the
last table fill seen.  The internal argument is strong -- if the table
still held I62K6, an interrupt would land at I62ITE+.32, which 3A and
3B never SVA, so the landing would be the untouched "B,$" self-loop
and neither block could pass -- but it is an argument, not a page.

AND SVA REWRITES ONLY THE ADDRESS FIELD, from the primary source
rather than from this usage.  Reference Manual printed p.29 (PDF
p.32), "Store Value in Address (SVA)": "The first 18, 19, or 24 bits
of the value field of the index word specified by J replace THE
ADDRESS FIELD of the instruction specified by the effective address",
the width "determined from the instruction operation code".  A
half-word branch's address field is bits 0-18 -- 19 bits, bit 18
included -- so an SVA into I62ITE plants a half-word-resolved target
and leaves the BD op standing.

A MEASURED NULL, with its arithmetic.  "I62INT DR%BU,64,8@,64
-INTRPT TABLE." at 024220.00 prints "100.00", which is the RESERVE
SIZE (0o100 = 64 words), not a machine word.  No row is asserted for
it and none is fabricated: the program SLCs across the reserve and
takes the label by SYN.  The arithmetic is the check -- 024220 + 0o100
= 024320, exactly where the page prints I62ITE, and the CNOP row
immediately before the reserve (024217.40, asserted below) is what
witnesses that the counter really stood at 024220.00.  Ref. Manual
printed p.48 (PDF p.51) calls the table "48 successive full-word
locations"; the deck reserves 64 and points $IA at it with I62XW1's
"XW,0,64,I62INT", whose refill-address field holds 024220.

A SECOND MEASURED NULL: 024325.40.  I62BR2 is a half-word at
024325.00 and I62XW1 is an XW, which must start on a word boundary, so
the page jumps to 024326.00 and prints nothing in between.  strap_asm
leaves that half-word untouched rather than NOP-filling it, because
its gap filler skips gaps that precede a data pseudo-op ("dead space
no program counter ever visits").  The listing gives no evidence
either way, so no row is asserted there.

THE FOUR CNOPs ARE A FOUR-WAY SELF-CHECK on that same rule, and they
are kept verbatim.  Two sit at an ODD half-word and print a NOP word
(024207.40 and 024217.40, both asserted below); two are already
word-aligned and print NOTHING AT ALL -- the one above I62K1 and the
one above I62EX -- and the page gives them no address column either.
That this assembler reproduces the pattern is measured, not assumed:
removing CNOP's alignment moves seven labels and fifteen rows, and
exactly the ones the page predicts -- see the injection table below.

WITNESS TIERING.  Every SYN in the program file is an INPUT to this
check, not a witness: it makes the address field come out right by
construction, so a row naming one proves only that every OTHER field
lands where the listing puts it.  That covers the twenty-four branch
targets I6221...I6299 (all in 1262's body on earlier pages), I000
(the deck's own numeric label, 024503.00), and I62INT.  Five of the
twenty-four are corroborated by a separately read page -- p.93's label
column prints I6225 at 023474.40, I6226 at 023504.00, I6227 at
023505.00, I6231 at 023516.40 and I6232 at 023517.40 -- but
corroboration does not convert an input into a witness.

Two more rows are ANCHORS rather than evidence: I62K1 at 024172.00
and I62ITE at 024320.00 are each the FIRST label after an SLC, so
checking them checks the SLC against the number this transcription
handed it.  They are asserted as the block's two anchors.

THE GENUINE ADDRESS WITNESSES, all self-checked by decoding bit 18 out
of the printed octal pair and reading it back against the page's own
label column:

  024320.40  "B,$" -> 24320.50 00.  Pair 50 = 101000, bit 18 = 1, so
             the target is 024320.40 -- the row's OWN address.  The
             cleanest bit-18 witness on the page: the same source text
             "$" one half-word earlier prints "24320.04 00", bit 18 =
             0.  Nothing here is SYN'd.
  024176.00  "EXIC,$+.32" -> 24176.56 00.  Pair 56 = 101110, bit 18 =
             1 -> 024176.40, and
  024176.40  the identical source text -> 24177.16 00.  Pair 16 =
             001110, bit 18 = 0 -> 024177.00.  One spelling, two
             different half-word selects, because "$" moved: the
             select is being COMPUTED, not copied.
  024173.00  "EX,I62EXT" -> 24321.12 00.  Pair 12 = 001010, bit 18 = 0
             -> 024321.00, and I62EXT is defined INSIDE this
             transcription at 024321.00 by the second SLC plus the
             cumulative sizing of I62ITE's two halves.  No SYN.
  024177.00  "B,I62ITE+.32" -> 24320.50 00.  Bit 18 = 1 -> 024320.40:
             the "+.32" arithmetic and the bit-18 placement are
             genuine, the BASE is not -- I62ITE is the anchor the SLC
             sets, so this row witnesses the offset, not the word.
  024200.00  "BXVZ,$+.32" -> 24200.71 42.  Pair 71 = 111001, bit 18 =
             1 -> 024200.40, the "BD,I6221" row below it.  Same at
  024210.00  -> 24210.71 42 -> 024210.40.
  024217.00  "I62B16" and the 44 half-words before it: the whole
             I62K/I62B run is checked by the SYMBOLS table, and its
             addresses fall out of the sizing of four full-word BB
             instructions at both even and ODD half-words (I62B6 at
             024205.40 and I62B15 at 024215.40 straddle a word
             boundary, Ref. Manual p.39).

FOR THE RECORD, bit 18 is NOT a half-word select in every class, and
this page shows it: I62EXF's "L(U),I000" prints 24503.40 60, where the
pair 40 = 100000 has its top bit set, yet the symbol is the same
"I000" = 024503.00 that I62EX's "LX,$X1,I000" prints as 24503.02 10 --
so the set bit cannot be a half-word select.  A floating point
operation is format 1, "OP,A(I)" with an 18-bit WORD address (pocket
card X22-6533's FLOATING POINT field diagram, carried in opcodes.py's
sourced comment for FP_CODES); bit 18 is part of what follows the
address, not of the address.  Decoding bit 18 as the half-word select
is right for the branch and index classes and wrong here.  The exact
field boundary is not re-derived for this file: what is measured is
that the same symbol prints two different pairs.

SUBSTITUTIONS: four, listed in the program file.  The load-bearing one
is that I62BR1 (024323.40) and I62BR2 (024325.00) are printed "$BD,0"
and written "BD,0"; the 32 bits are identical -- both are the printed
"0.04 00", measured below -- but STRAP's "$" prefix on an operation is
not explained by any page read for this work.  It occurs only on
data-in-the-instruction-stream rows (these two, and I60SX1 at
023041.00, verify_ax5b_160s1_clear_inds_listing.py).  Left open.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted; each
injection was made with __pycache__ removed on BOTH sides of the run
(stale bytecode has replayed a previous injection's answer in this
project):

  UNCOND_BRANCH_CODES["BE"] 0b000 -> 0b101
      024202.00  BE,I6226 -> "023504.24 00"
      024212.00  BE,I6279 -> "024045.64 00"             (2 rows)
      The two BE rows, and the two the EX/EXIC enable tests execute.
  UNCOND_BRANCH_CODES["BD"] 0b001 -> 0b100  (= BEW)
      024172.00, 024172.40, 024200.40, 024203.00, 024207.00,
      024210.40, 024213.00, 024217.00, 024320.00, 024323.40,
      024325.00                                        (11 rows)
      Including 024320.00, the landing half, and the two "$BD,0"
      rows.  Note 024320.40's "B,$" is NOT among them, which is the
      whole point of the pair.
  MISC_CODES["EX"] 0b010 -> 0b001
      024173.00, 024173.40, 024174.00, 024174.40, 024175.00,
      024175.40                                         (6 rows)
      All six EX rows; the two EXIC rows are untouched.
  MISC_CODES["EXIC"] 0b011 -> 0b111
      024176.00, 024176.40                              (2 rows)
  BB_CODES["BB"] (0b00, 1) -> (0b01, 1)  (= BBZ)
      024204.00, 024205.40, 024214.00, 024215.40        (4 rows)
      All four BRANCH ON BIT rows, each a full word, two of them at
      an odd half-word.
  strap_asm's CNOP alignment removed (sizing FULL,0 -> HALF,0, i.e.
  CNOP no longer rounds the location counter up to a word)
      symbols I62B10 I62B11 I62B12 I62B13 I62B14 I62B15 I62B16
      rows 024207.40 024210.00 024210.40 024211.00 024211.40 024212.00
           024212.40 024213.00 024213.40 024214.00 024215.00 024215.40
           024216.40 024217.00 024217.40      (7 symbols + 15 rows)
      This is the measurement behind "the four CNOPs are a four-way
      self-check", and it is sharper than a global slide: the rows
      BEFORE 024207.40 are untouched, because the two CNOPs at an
      aligned position were already emitting nothing; everything from
      the first ODD-half-word CNOP to the end of the I62B run moves;
      and nothing below 024320.00 moves at all, because the SLC across
      the interrupt table re-anchors the counter.  A transcription
      that had mis-sized CNOP would therefore have failed exactly in
      the I62B block and nowhere else.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_int_entry.strap").read())

ROWS = [
    # ---- the constants stored into the interrupt table --------------
    ('024172.00', '24320.04 00',
     'I62K1 BD,I62ITE     bit 18 = 0 -> 024320.00, the DISABLED half'),
    ('024172.40', '24320.04 00',
     'BD,I62ITE            the same half-word twice, so one SX plants it'),
    ('024173.00', '24321.12 00',
     'I62K2 EX,I62EXT     in-range label: 024321.00'),
    ('024173.40', '24321.12 00',
     'EX,I62EXT'),
    ('024174.00', '23.12 00',
     'I62K3 EX,$X3         system symbol: word 19'),
    ('024174.40', '23.12 00',
     'EX,$X3'),
    ('024175.00', '10.12 00',
     'I62K4 EX,$L          the left half of the accumulator, word 8'),
    ('024175.40', '10.12 00',
     'EX,$L'),
    ('024176.00', '24176.56 00',
     'I62K5 EXIC,$+.32     bit 18 = 1 -> 024176.40'),
    ('024176.40', '24177.16 00',
     'EXIC,$+.32            same text, bit 18 = 0 -> 024177.00'),
    ('024177.00', '24320.50 00',
     'I62K6 B,I62ITE+.32  bit 18 = 1 -> 024320.40, the ENABLED half'),
    ('024177.40', '24320.50 00',
     'B,I62ITE+.32'),
    # ---- the subject-instruction branch pairs -----------------------
    ('024200.00', '24200.71 42',
     'I62B1 BXVZ,$+.32     self-relative -> 024200.40'),
    ('024200.40', '23464.04 00',
     'BD,I6221             (ext)'),
    ('024201.00', '23473.71 42',
     'I62B2 BXVZ,I6224    (ext) bit 18 = 1 -> 023473.40'),
    ('024201.40', '23474.50 00',
     'B,I6225              (ext) p.93 prints I6225 at 023474.40'),
    ('024202.00', '23504.00 00',
     'I62B3 BE,I6226      (ext) the "BE" subject pair, executed p.93'),
    ('024202.40', '23505.10 00',
     'B,I6227              (ext) p.93 prints I6227 at 023505.00'),
    ('024203.00', '23516.44 00',
     'I62B4 BD,I6231      (ext) the "BD" subject pair, executed p.93'),
    ('024203.40', '23517.50 00',
     'B,I6232              (ext) p.93 prints I6232 at 023517.40'),
    ('024204.00', '20.00 80 023535.34 02',
     'I62B5 BB,$X0,I6234  (ext) full word; bit 50 = 0 -> 023535.00'),
    ('024205.00', '23536.50 00',
     'B,I6235              (ext)'),
    ('024205.40', '20.01 80 023543.34 02',
     'I62B6 BB,$X0+.01,I6238  (ext) full word at an ODD half-word'),
    ('024206.40', '23544.50 00',
     'B,I6239              (ext)'),
    ('024207.00', '23571.04 00',
     'I62B7 BD,I6246      (ext)'),
    ('024207.40', '0.30 00',
     'CNOP                  odd half-word: the NOP is printed'),
    ('024210.00', '24210.71 42',
     'I62B10 BXVZ,$+.32    self-relative -> 024210.40'),
    ('024210.40', '24025.04 00',
     'BD,I6274             (ext)'),
    ('024211.00', '24034.31 42',
     'I62B11 BXVZ,I6277   (ext)'),
    ('024211.40', '24035.10 00',
     'B,I6278              (ext)'),
    ('024212.00', '24045.40 00',
     'I62B12 BE,I6279     (ext) bit 18 = 1 -> 024045.40'),
    ('024212.40', '24046.50 00',
     'B,I6280              (ext)'),
    ('024213.00', '24060.44 00',
     'I62B13 BD,I6284     (ext)'),
    ('024213.40', '24061.50 00',
     'B,I6285              (ext)'),
    ('024214.00', '20.00 80 024072.74 02',
     'I62B14 BB,$X0,I6287 (ext) full word; bit 50 = 1 -> 024072.40'),
    ('024215.00', '24074.10 00',
     'B,I6288              (ext)'),
    ('024215.40', '20.01 80 024101.74 02',
     'I62B15 BB,$X0+.01,I6291  (ext) full word at an ODD half-word'),
    ('024216.40', '24103.10 00',
     'B,I6292              (ext)'),
    ('024217.00', '24130.44 00',
     'I62B16 BD,I6299     (ext)'),
    ('024217.40', '0.30 00',
     'CNOP                  odd half-word: the NOP is printed'),
    # 024220.00  I62INT  DR%BU,64,8@,64  "100.00" -- the RESERVE SIZE,
    # 0o100 = 64 words, not a machine word.  No row; SLC across it.
    # 024220 + 0o100 = 024320, the next printed address.
    # ---- the landing word -------------------------------------------
    ('024320.00', '24320.04 00',
     'I62ITE BD,$          "-ALL INTERRUPTS ENTER HERE."  bit 18 = 0'),
    ('024320.40', '24320.50 00',
     'B,$                   bit 18 = 1 -> its own address, 024320.40'),
    ('024321.00', '0.00 00 000000.00 00',
     'I62EXT XW,0,0,0      the EX subject slot, an all-zero index word'),
    # ---- the subject instructions, "-KEEP / -IN / -ORDER" -----------
    ('024322.00', '24503.02 10',
     'I62EX LX,$X1,I000   (ext) the deck\'s numeric label "I000"'),
    ('024322.40', '0.30 00',
     'NOP                   "-ORDER"'),
    ('024323.00', '0.00 10',
     'I62PSI LX,$X0,0      "-PSEUDO IC."  address 0 until SVA fills it'),
    ('024323.40', '0.04 00',
     'I62BR1 BD,0          listing "$BD,0"'),
    ('024324.00', '0.00 00 000000.00 00',
     'I62SUB XW,0,0,0      "-SUBJ INST."'),
    ('024325.00', '0.04 00',
     'I62BR2 BD,0          listing "$BD,0"; 024325.40 is skipped'),
    ('024326.00', '0.00 00 002000.50 90',
     'I62XW1 XW,0,64,I62INT  count 64, refill address 024220'),
    ('024327.00', '24503.00 80 000000.20 50',
     'I62EXV L(BU),I000   "-VFL FULL WD."'),
    ('024330.00', '24503.40 60',
     'I62EXF L(U),I000    "-FLT PT."  bit 18 here is NOT a half-word'),
    ('024330.40', '24503.40 60',
     'L(U),I000            select -- see the docstring'),
    ('024331.00', '21.22 00',
     'I62EXM Z,$X1         "-MISC."'),
]

# Labels DEFINED inside the transcribed range.  I62K1 and I62ITE are
# ANCHORS, not evidence: each is the first label after an SLC.  Every
# other entry is the cumulative sizing of the half-words before it --
# including four full-word BB instructions, two of them at an odd
# half-word -- and is checked against the page's own label column.
SYMBOLS = {
    'I62K1': '024172.00', 'I62K2': '024173.00', 'I62K3': '024174.00',
    'I62K4': '024175.00', 'I62K5': '024176.00', 'I62K6': '024177.00',
    'I62B1': '024200.00', 'I62B2': '024201.00', 'I62B3': '024202.00',
    'I62B4': '024203.00', 'I62B5': '024204.00', 'I62B6': '024205.40',
    'I62B7': '024207.00', 'I62B10': '024210.00', 'I62B11': '024211.00',
    'I62B12': '024212.00', 'I62B13': '024213.00', 'I62B14': '024214.00',
    'I62B15': '024215.40', 'I62B16': '024217.00',
    'I62ITE': '024320.00', 'I62EXT': '024321.00', 'I62EX': '024322.00',
    'I62PSI': '024323.00', 'I62BR1': '024323.40', 'I62SUB': '024324.00',
    'I62BR2': '024325.00', 'I62XW1': '024326.00', 'I62EXV': '024327.00',
    'I62EXF': '024330.00', 'I62EXM': '024331.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 INT '))
