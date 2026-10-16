#!/usr/bin/env python3
"""verify_ax5b_162_test2cab_listing.py -- jb_ax5b "I-Box 5", routine
1262 ("TEST EX AND EXIC"), the TEST 2C header row plus TEST 2CA and
TEST 2CB (programs/ax5b_162_test2cab.strap) against the listing's
printed machine code, PDF p.103, octal 024000.40-024020.00.  31
SOURCE ROWS over 32 half-words (the TI at 024014.40 is a full word at
an ODD half-word, so it spans 024014.40-024015.00 and the listing
prints no row at 024015.00).  Entry labels I6271, I6272, I6273.

ONE FILE FOR BOTH BLOCKS, for the reason verify_ax5b_162_test1cab_
listing.py gives for 1CA+1CB: THE RANGES ABUT.  2CA ends at 024007.40
and 2CB starts at 024010.00, the next half-word, with nothing between
them.  They share the TEST 2C header row, the same disabled state and
the same SEN/SERS harness, and 2CA's PASS PATH IS THE ENTRY TO 2CB --
the interruption lands at I62ITE, which branches to I6272.  Splitting
them would duplicate eleven SYNs and cut a control-flow edge in half.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.

WHERE THIS SITS.  verify_ax5b_162_test2b_head_tail_listing.py ends
TEST 2B at 024000.00, the VERY HALF-WORD BEFORE this range, so the two
abut with nothing between them; the next routine-1262 address covered
anywhere in this directory is 024136.00
(verify_ax5b_162_test3a_listing.py).  A programmatic sweep of every
ROWS tuple in every verify_*.py here finds NO file with any octal
location inside 024000.40-024020.00 (the nearest hit above it is
024117.00 in verify_pau_shf0_listing.py, which is the jb_af1c PAU
deck -- a DIFFERENT DECK that happens to load at the same octal
addresses).  The same sweep run against known-covered
ranges as a control does report the expected files, so the empty
result is a measurement.  024020.40 -- "SIC,I60SX1  -TEST ICC, CHK
EXIC OF BRANCH AND EXE." -- opens TEST 2CC and is deliberately NOT
transcribed here.

=====================================================================
THE GLYPH QUESTION THIS FILE WAS COMMISSIONED TO SETTLE:
p.103 PRINTS "ICB" WITH THE LETTER I, AND IT IS NOT THE p.92 ARTEFACT.
=====================================================================

docs/listing_typography.md sec.10 records that p.92's TEST 1C header
prints a DIGIT 1 whose apparent top bar is the row's own dashed rule
line, and closes with: "Not yet checked: PDF p.103's `ICB` at TEST
2CB ... The same artefact is the likely explanation and is explicitly
NOT asserted."  Measured at 600 dpi, IT IS NOT THE SAME ARTEFACT.

  THE ROW IS RULED THROUGH, so sec.10's warning does apply -- but the
  rule misses the glyph.  The dashed rule on the I6272 row runs at
  y1971-1976.  y1977 is BLANK.  The glyph occupies y1978-2045.  A
  six-pixel gap, so nothing about this glyph's top is forged.

  THE GLYPH IS A BARE STROKE.  Full per-scan-line column extent:
      y1978-1985   3, 5, 6, 7, 8, 9, 9, 9 px   (a taper, not a flag)
      y1986-2042   11-16 px throughout
      y2043-2045   6, 6, 4 px                  (a taper, not a serif)
  Total bbox x2796-2812 = 17 px wide, 68 px tall.  NO upper-left flag
  and NO base serif -- and sec.10's own rule is that the BOTTOM is
  what settles it, because no horizontal rule can forge a foot.

  CALIBRATION, ALL FROM THIS SAME PAGE:
      digit 2 of "-TEST 2C,"   row 1            x2782-2822   w41
      digit 2 of "-TEST 2CA,"  row 2            x2781-2821   w41
      letter I of "MISC"       row 1            x3336-3347   w12
      letter I of "MONITOR"    SAME ROW as the glyph  x3758-3770  w13
      THE DISPUTED GLYPH       row 16           x2796-2812   w17
  docs/listing_typography.md's jb_ax5b calibration (11 826 glyphs):
  no printed digit is ever narrower than 24 px and 99 % are 30+; the
  letter I is 10-18 px, mode 12-15.  17 px is inside the letter-I
  population and outside the digit population.

  p.92'S GLYPH, RE-MEASURED HERE RATHER THAN INHERITED.  The "1" of
  "-TEST 1CB," at 023450.40 has an upper-left flag at y1672-1682
  spanning x2767-2789, and a BASE SERIF at y1725-1735 spanning
  x2767-2803.  Total bbox w37.  A 37 px glyph with a 37 px foot
  against a 17 px bare stroke: the two are different characters and
  the sibling's reading of p.92 is independently confirmed.

  CORROBORATION ON THE SAME PAGE: 024020.40's "-TEST ICC, CHK EXIC OF
  BRANCH AND EXE." (TEST 2CC, just outside this range) carries the
  same glyph, x2790-2810, w21 -- also a bare stroke.  It happened
  TWICE on p.103 and not at all on p.92.

  VERDICT: DECK TYPO, not scan damage and not the rule-line artefact.
  Damage leaves a RAGGED correct letter -- a partial flag, a broken
  serif; this stroke is clean and uniform at 11-13 px over its whole
  height, indistinguishable from the letter I of "MONITOR" nine cells
  along the same row.  WHAT THE DECK MEANT is an inference and is
  kept separate from the measurement: the comment is
  character-for-character p.92's "-TEST 1CB, CHK ADR MONITOR.", the
  block is TEST 2C's second part, and the label column beside it
  reads I6272 between I6271 and I6273 -- so "2CB" is what belongs
  there.  Note that a duplicated 1CB card would have reproduced
  p.92's DIGIT; a letter I in both ICB and ICC is a keypunch that
  went wrong the same way twice.  Transcribed as printed.

WHAT THESE BLOCKS ARE.  TEST 1CA and TEST 1CB rebuilt for EXIC, and
the only deck witness this project has for the FIRST-LEVEL PSEUDO-IC
CARVE-OUT.  Reference Manual printed p.50 (PDF p.53), read first-hand
at 300 dpi for this file:

  "abled, interruption cannot occur and address monitoring is
  suspended.  In order that control may remain entirely with the main
  program during an execution operation, two special exceptions are
  made.  First, address monitoring is always in force during (1)
  EXECUTE and (2) EXECUTE INDIRECT AND COUNT, EXCEPT FOR THE ADDRESS
  OF THE LOCATION OF THE *FIRST LEVEL* PSEUDO-INSTRUCTION COUNTER.
  Second, at the completion, termination, or suppression of an
  execution operation, interruption is always permitted."

and, from the same page, the sentence that makes EXIC's operand an
18-bit WORD address:

  "Execute Indirect and Count (EXIC).  Bits 0-18 of the full-word
  addressed by BITS 0-17 of the effective address are used as a
  pseudo-instruction counter.  The contents of the pseudo-instruction
  counter address the location of a subject instruction that is
  fetched and executed.  After the subject instruction has been
  fetched but prior to its execution, the pseudo-instruction counter
  is stepped.  If the subject instruction is half-length, the
  pseudo-instruction counter is stepped once; if full-length, twice."

2CA is 1CA with the subject reached through a pseudo-IC: the inline
"-ILLEGAL OP CODE." word at 024003.00 actuates OP in the straight
line (printed p.45 item 15, "executed as NO OPERATION"), the pseudo-IC
is aimed at I62SUB and I62SUB loaded from I62EXI, and "EXIC,I62PSI"
must interrupt AT ITS COMPLETION although the system is disabled.

2CB IS THE CARVE-OUT ORACLE.  It sets the upper boundary from
"LVI,$X1,I62PSI-1.0" -> 024322.00, which is ONE WORD BELOW the
pseudo-IC rather than one word below the subject:

      upper boundary                        024322.00
      I62PSI, the FIRST-LEVEL pseudo-IC     024323.00   protected
      I62SUB, the subject instruction       024324.00   protected

Both are inside the monitored region.  The subject must signal IF, be
suppressed and interrupt (exception 1 plus printed p.45 item 21's
mask-one suppression); the pseudo-IC must NOT signal, because p.50
exempts it.  An exception-1 implementation WITHOUT the carve-out
raises a spurious IF on the pseudo-IC fetch and 2CB fails.  The
choice of "I62PSI-1.0" over "I62SUB-1.0" is a deliberate one word,
and it is what makes the block discriminating.

EVERY HEADING AND ERROR MESSAGE, VERBATIM, WITH ITS LOCATION:

  024000.40  -TEST 2C, CHK MISC CNTRLS OF EXIC.
  024001.00  -TEST 2CA, ENABLE AFTER EXIC.
  024003.00  -ILLEGAL OP CODE.
  024007.00  -NO INT TAKEN ON EXIC
  024007.40  -WHEN OP WAS SET.
  024010.00  -TEST ICB, CHK ADR MONITOR.
  024016.00  -NO INT TAKEN WHEN
  024016.40  -EXIC INSTRUCT ABOVE UB.
  024017.40  -EXIC INSTRUCT ABOVE UB
  024020.00  -WAS NOT NOPED.

Three error messages (each over two rows), three headings, one inline
data word.  Trailing punctuation was MEASURED on every one:
024007.00, 024016.00 and 024017.40 end with a 45-50 px letter and
nothing in the next pitch cell; 024003.00 (w33 h31), 024007.40
(w32 h30), 024016.40 (w31 h38) and 024020.00 (w32 h35) end with a
round blob on the baseline, i.e. a period, not this chain's comma
(which is 27-28 px wide, 44-48 px tall, and has a tail below the
baseline -- see verify_ax5b_162_test1d_listing.py, where p.95's copy
of "-ILLEGAL OP CODE" ends with one).

GARBLE INVENTORY: "ICB" at 024010.00 is the ONLY garble in the range,
and its verdict is above.  "CNTRLS" at 024000.40 is an ABBREVIATION,
not a dropped letter, by pitch: the header row is set on 60.0 px/cell
at 600 dpi and the six letters of CNTRLS occupy six consecutive
cells, with no ~60 px hole where an O would be -- the same argument
verify_ax5b_162_test1cab_listing.py makes for p.92's identical row.
No letter is dropped and none is added anywhere on these rows.

BIT-18 SELF-CHECKS.  Print format: bits 0-17 as six octal digits,
".", bits 18-23 as two octal digits, bits 24-31 as two hex digits --
BIT 18 IS THE TOP BIT OF THE OCTAL PAIR.  FIVE classes, FOUR reasons.
THE HONEST HEADLINE FIRST:

  NO ROW IN 024000.40-024020.00 HAS BIT 18 SET.  Every printed octal
  pair in the range is below 40 octal.  These blocks CANNOT witness
  bit 18 at all and inherit the reading from TEST 1D (three in-range
  labels with bit 18 = 1, across three encoders) and from TEST 1CA
  ("EX,$-.32" -> 23446.52).  Stated rather than presented as a
  measurement.

 (a) HALF-WORD SELECT, DECODABLE -- branch targets, MISC addresses,
     the 19-bit DirIndex and ImmIndex fields.  Reference Manual
     printed p.23 (PDF p.26), read first-hand (footer "Operand
     Designation  23"): "In the majority of these operations, 19 bits
     of the effective address are used in order to permit addressing
     of half-words."
       024003.40  LVI,$X1,I6272 -> 24010.03 01.  Pair 03, bit 18 = 0
                  -> 024010.00, which is where p.103 prints I6272.
                  IN-RANGE: evidence for the other eighteen bits.
       024013.00  LVI,$X1,I6273 -> 24017.03 01.  Bit 18 = 0 ->
                  024017.00 = I6273.  IN-RANGE: evidence.
       024000.40  BD,$+.32 -> 24001.04 00.  Bit 18 = 0 -> 024001.00,
                  and 024000.40 + 32 bits is 024001.00.  The range's
                  only self-relative row.
       024012.00  LVI,$X1,I62PSI-1.0 -> 24322.03 01.  THE BOUNDARY
                  ROW.  The SYN gives I62PSI = 024323.00, so this
                  checks the "-1.0" arithmetic rather than the label:
                  024323.00 minus one word is 024322.00.
       SYN-addressed rows in this class (every field but the
                  address): 024001.40, 024002.00, 024002.40,
                  024004.00, 024004.40, 024005.00, 024007.40,
                  024010.00, 024010.40, 024013.40, 024014.00,
                  024016.40.
 (b) LX and SX are EXCLUDED by printed p.23 (PDF p.26), read
     first-hand: "The two exceptions use only 18 bits of the
     effective address because they require full-word operands", and
     on the same page "The index word specified by J is replaced by
     the full-word specified by bits 0-17 of the effective address."
     Five rows: 024005.40, 024006.00, 024011.00, 024011.40,
     024017.00.
 (c) SIC is EXCLUDED because its operand is a 24-bit BIT address in
     bits 0-23, so the octal pair is a BIT OFFSET inside the word.
     Four rows: 024001.00, 024007.00, 024016.00, 024017.40, all
     printing ".00 80" (the 80's high nibble is the format's literal
     1000 at bits 24-27).
 (d) TRANSMIT at 024014.40 is BOTH.  A1 is a 24-bit BIT address and
     is excluded for the same reason as (c): "24503.00 80" is word
     0o24503, bit 0.  A2 IS decodable -- a 19-bit half-word address
     at bits 32-50, so in the SECOND printed group bit 50 is the top
     bit of the pair: "000014.02 A0" gives bit 50 = 0, i.e. word
     0o14 = 12 = $MASK at its .00 half.  The ".02 A0" tail is the
     format's literal for a count-1 immediate transmit, identical in
     verify_ax5b_16087_listing.py's "TI,1,BIT0($X1),$MASK".
 (e) EXIC IS EXCLUDED because printed p.50 (PDF p.53) makes its
     operand an 18-bit WORD address -- the quote is above: "the
     full-word addressed by BITS 0-17 of the effective address".
     Against "Execute (EX)" three paragraphs earlier on the same
     page: "BITS 0-18 of the effective address form the address of
     the location of a subject instruction."
     WHAT THIS BLOCK CANNOT SHOW, and it matters: both EXIC rows
     (024006.40, 024015.40) print "24323.16 00" -- pair 16 = 001110,
     bit 18 = 0.  The data is CONSISTENT with the exclusion but does
     not DISCRIMINATE it: an assembler treating EXIC's operand as a
     19-bit half-word address would print exactly the same, because
     I62PSI is word-aligned and there is no bit-18-set EXIC anywhere
     in the range.  The exclusion rests on the printed manual, not on
     these rows.  That is what AGENTS.md rule 4 is for.

BRANCH POLARITY, DECIDED PER CHECK, NOT PER BLOCK.  enc_branch_ind
lays out addr19(0-18), indnum(19-24), the literal 1000(25-28),
clear(29), branchOn(30), idx(31).  ONE indicator branch here:
  024020.00  BZXVZ,SERS -> 1304.31 40.  Hex 40 = 0100 0000 over bits
             24-31, so bit 30 = 0: BRANCH ON XVZ OFF, and bit 29 = 0,
             do not reset.  Right: "Z,$X1" zeroed $X1 and
             "LX,$X1,$X1" reads it back, so XVZ is ONE if the
             suppressed subject left $X1 alone (pass, no branch) and
             ZERO if the subject ran (branch to SERS, "-EXIC INSTRUCT
             ABOVE UB WAS NOT NOPED.").
  THE OPPOSITE POLARITY IS LIVE IN THE SIBLING: TEST 1D's "BUSA" is
  hex C2 (bit 30 = 1) and its "BEXEZ" is hex 46 (bit 30 = 1 and bit
  29 = 1).  Injections 2 and 3 below move this row and those two in
  OPPOSITE directions under one patch, which is what makes the
  polarity measured per check rather than assumed per block.

WITNESS TIERING.  EVERY SYN IN THE .strap IS AN INPUT, NOT A WITNESS
-- the caveat verify_ax5b_16082_16083_listing.py makes about I6088.
I6271 IS NOT EVIDENCE EITHER: it is the first label after an SLC this
transcription fed 024000.40, so checking it checks the SLC against
its own input; it is asserted as the anchor.
  GENUINE ADDRESS EVIDENCE: I6272 and I6273, each the cumulative
  sizing of every half-word before it and each named by an LVI --
  plus the self-relative row at 024000.40 and the "-1.0" arithmetic
  at 024012.00.  BOTH witnesses have bit 18 = 0, so neither witnesses
  bit 18; see the headline above.
  CORROBORATION THAT DOES NOT PROMOTE AN EXTERNAL: I62INT, I62ITE,
  I62PSI, I62SUB, I62EXI and I00O from separately read pages' own
  label columns (PDF pp.109, 110, 114), BIT57 = 024613.00 from
  verify_ax5b_bit_table_listing.py, and SEN/SERS/I60SX1/I60S1 from
  other files here.

NO CNOP AND NO SLC-ACROSS.  No CNOP occurs on PDF p.103, and every
printed location in the range carries machine code, so no row is
"location printed, no word".  024015.00 prints nothing because the TI
above it is a full word at an odd half-word and covers it -- the
listing's own layout, not a missing datum.

FIRSTS: one modest one.  "LVI,$X1,I62PSI-1.0" at 024012.00 is the
repo's first LABEL-MINUS-WORD-OFFSET in an IMMEDIATE-INDEX field.
The construct is not new in itself -- ax5b_160_test6.strap has
"LX,$X2,I6082A-1.0" -- but that is a DIRECT-index op through a
different encoder arm.  NOT FIRSTS, knocked down: EXIC (six files),
TI in the exact "TI,1,<word>,$MASK" shape (verify_ax5b_16087_
listing.py 021400.40, verify_ax5b_160_test6_listing.py 022063.00),
BZXVZ (ten files), the DD(BU,32,8),(8)3740 word (four files), and
SVA/LVI/LX/SX/SV/Z/SIC/BD/B throughout.

PROVEN DISCRIMINATING.  Eleven injections were run against this file
and its sibling; the five that move a row HERE are listed with their
OBSERVED failing rows.  Each was made with a WHOLE-LINE anchored edit
that refuses unless the anchor matches exactly once, each was
CONFIRMED APPLIED by printing the patched line with its line number
BEFORE the run, each run had __pycache__ removed on BOTH sides, each
was reverted by reversing the exact patch (never git checkout, per
AGENTS.md rule 2) and the file's md5 was checked back to its
original.

  1. opcodes.MISC_CODES["EXIC"] 0b011 -> 0b111
     (confirmed: line 216 read '    "EXIC":0b111,')
       024006.40  EXIC,I62PSI -> "024323.36 00"           (2 rows)
       024015.40  EXIC,I62PSI -> "024323.36 00"
     Both EXIC rows and nothing else.  Under the SAME build
     verify_ax5b_162_test1d_listing.py stays green, and the
     complementary patch (MISC_CODES["EX"] 0b010 -> 0b110) moves both
     of 1D's EX rows and leaves THIS file green -- so EX and EXIC are
     separated by measurement, not by inspection of the table.
  2. strap_asm.enc_branch_ind, branchOn -> 1 - branchOn
     (confirmed: line 355 read
      '    v, w = cat((addr19, 19), (indnum, 6), (0b1000, 4), (clear, 1), (1 - branchOn, 1), (idx, 1))')
       024020.00  BZXVZ,SERS -> "001304.31 42"            (1 row)
     The row GAINS hex bit 30, i.e. it was branch-on-OFF.  Under the
     same build 1D's BUSA and BEXEZ LOSE it (C2 -> C0, 46 -> 44), so
     the two polarities are told apart by DIRECTION.
  3. strap_asm.enc_branch_ind, clear -> 1 - clear
     (confirmed: line 355 read
      '    v, w = cat((addr19, 19), (indnum, 6), (0b1000, 4), (1 - clear, 1), (branchOn, 1), (idx, 1))')
       024020.00  BZXVZ,SERS -> "001304.31 44"            (1 row)
     Bit 29, the "...Z" reset suffix, checked independently of bit 30
     -- and under the same build 1D's BEXEZ LOSES bit 29 (46 -> 42)
     while its BUSA gains it, which is the suffix made falsifiable.
  4. opcodes.DIR_INDEX_CODES["SVA"] 0b11101 -> 0b11001
     (confirmed: line 115 read '    "SVA":  0b11001,')
       024004.00  SVA,$X1,I62ITE -> "024320.03 90"        (4 rows)
       024005.00  SVA,$X1,I62PSI -> "024323.03 90"
       024010.40  SVA,$X1,I62PSI -> "024323.03 90"
       024013.40  SVA,$X1,I62ITE -> "024320.03 90"
     All four SVAs and only those; the SV at 024012.40 and the SX
     rows, which share the encoder, do not move.
  5. strap_asm.enc_transmit's literal (0b10, 2) -> (0b11, 2)
     (confirmed: line 384 read
      '               (1 if swap else 0, 1), (0b11, 2), (i2, 4))')
       024014.40  TI,1,I00O,$MASK ->
                  "024503.00 80 000014.02 B0"             (1 row)
     The range's only full-word instruction, and the Transmit/Swap
     literal at bits 58-59 checked apart from the A1 bit address, the
     J count and the A2 half-word address.  Under the same build
     verify_ax5b_162_test1d_listing.py stays green: it has no
     TRANSMIT.

MEASURED NULLS, EACH WITH A LIVENESS PROOF FROM THE SAME BUILD -- not
a constructed case, and not a silently failed patch.  Six injections
leave this file green; for each one the SAME patched build (same run,
same confirmed line number) moved rows in
verify_ax5b_162_test1d_listing.py:
  N1. enc_dir_index (idx, 4) -> ((idx << 1) & 0xF, 4)  [line 340]
      here: ALL TESTS PASSED.  1D: 3 rows moved (023553.00, 023553.40,
      023554.40).  There is NO parenthesised index anywhere in
      024000.40-024020.00, so this block cannot see the bug.
  N2. branch/MISC address mask 0x7FFFF -> 0x7FFFE  [line 1428]
      here: ALL TESTS PASSED.  1D: 3 rows moved.  No row here has
      bit 18 set, which is the headline above, measured.
  N3. indicator-branch address mask 0x7FFFF -> 0x7FFFE  [line 1501]
      here: ALL TESTS PASSED.  1D: 2 rows moved.  Same reason --
      024020.00's bit 18 is 0.
  N4. MISC_CODES["EX"] 0b010 -> 0b110  [line 215]
      here: ALL TESTS PASSED.  1D: 2 rows moved.  No EX here.
  N5. IMM_INDEX_CODES["V+I"] 0b0101 -> 0b0111  [line 130]
      here: ALL TESTS PASSED.  1D: 2 rows moved.  No V+I here.
  N6. CB_CODES["CB+"] (0b10,0,0) -> (0b11,0,0)  [line 183]
      here: ALL TESTS PASSED.  1D: 1 row moved.  No CB+ here.

WHAT THIS FILE CANNOT SEE.
  * The EXIC bit-18 exclusion is CONSISTENT, not WITNESSED -- see
    class (e).
  * I62PSI = 024323.00 and I62SUB = 024324.00 come from PDF p.109's
    label column as other files here record it, and I62EXI =
    024332.00 from docs/NEXT.md's read of p.110; none was re-rendered
    for this file.  2CB's whole premise is the ordering
    024322 < 024323 < 024324, and all three rows agree with the SYNs
    BY CONSTRUCTION.
  * I DID NOT READ I62EXI's CONTENTS.  2CB's BZXVZ check only means
    something if the subject copied from I62EXI writes $X1;
    ax5b_162_test1cab.strap records "I62EXI LVI,$X1,%8@777777.40"
    from docs/NEXT.md, unverified at any dpi.
  * THIS IS AN ENCODING ORACLE ONLY.  Nothing here was run on the
    Bluespec model, and nothing here shows that the carve-out is
    implemented -- that is the work this transcription exists to
    gate.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_test2cab.strap").read())

ROWS = [
    # ---- TEST 2C header row, then TEST 2CA --------------------------
    ('024000.40', '24001.04 00',
     'I6271 BD,$+.32      "-TEST 2C, CHK MISC CNTRLS OF EXIC."'),
    ('024001.00', '23041.00 80',
     'SIC,I60SX1          (ext) "-TEST 2CA, ENABLE AFTER EXIC."'),
    ('024001.40', '22741.04 00',
     'BD,I60S1            (ext) NOTE "BD" here, "B" in TEST 1D'),
    ('024002.00', '24220.03 01',
     'LVI,$X1,I62INT      (ext) the 64-word interrupt table'),
    ('024002.40', '2.03 30',
     'SV,$X1,$IA           word 2 = the interruption address register'),
    ('024003.00', '00000003740',
     'DD(BU,32,8),(8)3740  "-ILLEGAL OP CODE."  PERIOD (cf. p.95)'),
    ('024003.40', '24010.03 01',
     'LVI,$X1,I6272       in-range label; bit 18 = 0 -> 024010.00'),
    ('024004.00', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) NO "+.32": the BD half of the landing'),
    ('024004.40', '24324.03 01',
     'LVI,$X1,I62SUB      (ext) the subject slot, 024324.00'),
    ('024005.00', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext) aim the FIRST-LEVEL pseudo-IC'),
    ('024005.40', '24332.02 10',
     'LX,$X1,I62EXI       (ext) LX: 18-bit word address, p.23'),
    ('024006.00', '24324.03 10',
     'SX,$X1,I62SUB       (ext) copy the subject into the slot'),
    ('024006.40', '24323.16 00',
     'EXIC,I62PSI         (ext) THE TEST; pair 16, bit 18 = 0'),
    ('024007.00', '1310.00 80',
     'SIC,SEN              (ext) "-NO INT TAKEN ON EXIC"'),
    ('024007.40', '1304.04 00',
     'BD,SERS              (ext) "-WHEN OP WAS SET."'),
    # ---- TEST 2CB ---------------------------------------------------
    ('024010.00', '24324.03 01',
     'I6272 LVI,$X1,I62SUB  "-TEST ICB, CHK ADR MONITOR."  LETTER I'),
    ('024010.40', '24323.03 D0',
     'SVA,$X1,I62PSI      (ext) re-aim the pseudo-IC'),
    ('024011.00', '24613.02 10',
     'LX,$X1,BIT57        (ext) the boundary-control bit'),
    ('024011.40', '3.03 10',
     'SX,$X1,3.0           the boundary register; control bit on'),
    ('024012.00', '24322.03 01',
     'LVI,$X1,I62PSI-1.0   THE CARVE-OUT ROW: upper bound 024322.00'),
    ('024012.40', '3.03 30',
     'SV,$X1,$UB           upper boundary one word BELOW the pseudo-IC'),
    ('024013.00', '24017.03 01',
     'LVI,$X1,I6273       in-range label; bit 18 = 0 -> 024017.00'),
    ('024013.40', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) again the BD half'),
    ('024014.00', '21.22 00',
     'Z,$X1                word 0o21 = 17 = X1'),
    ('024014.40', '24503.00 80 000014.02 A0',
     'TI,1,I00O,$MASK     (ext) FULL WORD at an ODD half-word:'
     ' covers 024015.00, so no row prints there'),
    ('024015.40', '24323.16 00',
     'EXIC,I62PSI         (ext) THE TEST: subject AND pseudo-IC'
     ' both inside the monitored area'),
    ('024016.00', '1310.00 80',
     'SIC,SEN              (ext) "-NO INT TAKEN WHEN"'),
    ('024016.40', '1304.10 00',
     'B,SERS               (ext) "-EXIC INSTRUCT ABOVE UB."'),
    ('024017.00', '21.02 10',
     'I6273 LX,$X1,$X1     read $X1 back to set the index indicators'),
    ('024017.40', '1310.00 80',
     'SIC,SEN              (ext) "-EXIC INSTRUCT ABOVE UB"'),
    ('024020.00', '1304.31 40',
     'BZXVZ,SERS           (ext) "-WAS NOT NOPED."  hex 40 ->'
     ' branch-on-OFF, bit 29 = 0'),
]

# Only labels DEFINED inside the transcribed range belong here.  I6271
# is the SLC anchor, NOT evidence -- the SLC was fed 024000.40 by this
# same transcription.  I6272 and I6273 are genuine witnesses: each is
# the cumulative sizing of every half-word before it, including the
# full-word TI, and each is independently named by an LVI.  Neither
# carries bit 18, so neither witnesses bit 18; TEST 1D does.
SYMBOLS = {
    'I6271': '024000.40',
    'I6272': '024010.00',
    'I6273': '024017.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 2CA/2CB '))
