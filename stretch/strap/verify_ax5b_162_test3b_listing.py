#!/usr/bin/env python3
"""verify_ax5b_162_test3b_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), TEST 3B (programs/ax5b_162_test3b.strap) against
the listing's printed machine code, octal 024151.40-024162.00, plus
routine 1262's exit and continuity bridge, 024162.40-024171.00.  32
half-words, ALL ON PDF p.108.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

WHERE THIS CHECK CUTS.  TEST 3B proper is 024151.40-024162.00 (18
half-words).  The 14 rows after it are routine 1262's exit and
continuity bridge; they are contiguous with TEST 3B, self-contained,
and they end with "IC262 XW,0,0,0 -CONTINUITY REG" at 024171.00, the
last printed row on p.108 -- p.109 opens a new block, "CNOP /
-CONSTANTS FOR 1262.", at 024172.00.  The same five-row exit sequence
is printed again at 024357.40-024361.40 on PDF p.110, ending routine
I681, with identical encodings.

WHAT TEST 3B CHECKS.  Reference Manual printed p.50 (PDF p.53), read
at 600 dpi for this file: "Subject instructions of EXECUTE INDIRECT AND
COUNT may occupy any available locations with addresses 32.00 and
greater."  It is the SECOND sentence of one paragraph whose first is
the rule TEST 3A tests -- "Pseudo-instruction counters may occupy any
of the index registers as well as main core storage locations but
cannot occupy locations addressed between 0 and 15."  The two run
together across the column break, and the page sets a trap for a
skimming eye: the right column of PDF p.53 OPENS with "15.  Subject
instructions of ...", where that "15." is the tail of the left
column's sentence, not a list number.  TEST 3A
(verify_ax5b_162_test3a_listing.py) put the PSEUDO-IC below 15; TEST
3B leaves the pseudo-IC legal, at I62PSI = 024323.00, and puts the
SUBJECT INSTRUCTION below 32 instead.  "LVI,$X1,$X0 / SVA,$X1,I62PSI"
is the whole idea: $X0 is index register 0, WORD 16, half-word address
32, and the SVA plants that address in I62PSI's address field.
"LX,$X0,I62EXI" then loads the subject instruction into $X0 itself and
"EXIC,I62PSI" tries to execute it from there.  Its three error
messages are the contract, all printed on p.108:

  (a) "-NO INTERRUPT WHEN SUBJ INST OF / -EXIC LESS THAN 32."
      at 024156.40-024157.00, reached by FALLING THROUGH the EXIC, so
      the error is that no interruption happened.
  (b) "-AD NOT SET WHEN SUBJ INST OF / -EXIC LESS THAN 32."
      at 024160.00-024160.40, reached from I62104 when "BADZ,$+1.32"
      finds AD off.
  (c) "-SUBJ INST OF EXIC NOT NOPED / -WHEN IT IS LESS THAN 32."
      at 024161.40-024162.00.  "Z,$X1" zeroes index register 1 first
      and the subject at I62EXI is "LVI,$X1,%8@777777.40" (024332.00,
      PDF p.110, read at 600 dpi for this file), so a nonzero index
      value means the subject ran.

THE DECK'S OWN TYPO, recorded not corrected.  The heading comment at
024151.40 spells the mnemonic "EXITC" -- five letters, where the six
later comment lines on this page all write "EXIC".  A ruling line runs
along the cap height of that row and hides the top bar of every
letter, so the reading was settled by measuring the monospaced comment
column instead of by eye: the four "N" glyphs of
"-NO INTERRUPT WHEN SUBJ INST OF" fix the pitch at 60.1 px per cell at
600 dpi with cell 0 at x=2403, and the final "S" of the heading's
"LESS" starts at x=4394 = cell 33, making the heading 34 characters
against 33 for "-TEST 3B, SUBJ INSTR OF EXIC LESS".  Two vertical
strokes stand between the X and the C where "-EXIC LESS THAN 32." two
rows down has one.  FIVE LETTERS IS ESTABLISHED; I versus T in the
fourth is not separable under the rule.  "EXITC" is the recorded
reading, alongside TEST 3A's "PSEDUO".

THE SAME MEASUREMENT SETTLES "SEN0", WHICH THIS REPO CURRENTLY SPELLS
TWO WAYS.  024163.40's operand is "SEN" plus one round glyph, and
verify_ax5b_1258_test2_listing.py reads it as the letter O ("SENO")
while ax5b_160_test8b.strap reads it as the digit ("LSEN0").  On
p.108, at 600 dpi, the letter O is 50-51 px wide (the two O's of
"-NO INTERRUPT WHEN SUBJ INST OF") and the digit 0 is 44-45 px (the
two 0's of "BD,I62100" on this same page).  The glyph after SEN
measures 44.  It is the DIGIT, and this file spells the symbol SEN0.
No such measurement separates 1C262's leading glyph from a letter I:
in this print chain the digit 1 has no flag, so "162100" and
"INTERRUPT" begin with the same 12-14 px bare stem.  That reading
rests on the naming scheme instead -- 1C258, 1C260, 1C262 and, on the
separately read PDF p.110, "Z,1C268" at 024335.00 inside routine 1268
-- one continuity register per routine, named for its routine number.

TEST 3A'S FORWARD REFERENCE, CONFIRMED FIRST-HAND.  024155.40 holds
"%8@DD%BU,32,8@,3740 -ILLEGAL OP." printing 00000003740, byte for byte
the word TEST 3A carries at 024144.40 and the word 1260's I60K7 prints
at 023050.00 under "-ILLEGAL OP, NO. 31."  ax5b_162_test3a.strap
predicted the identical "Z,$X1 / DD / EXIC" triple at
024155.00/.40/024156.00; it is there, read off the page for this
transcription rather than taken on trust.  That upgrades the status of
the observation only: an operation-code-invalid word standing in the
straight-line instruction path, one half-word before the EXIC, is
SYSTEMATIC in this routine and not a slip.  Nothing on pp.107-110 says
why.  Recorded the way ax5b_16082_op_ad.strap records what it could
not trace; the row's ENCODING is settled regardless, and that is what
is checked below.

NO MNEMONIC IS A FIRST HERE, and that was checked by grep, not
assumed.  LVI, SVA, SIC, B, LX, Z, EXIC, BD, BADZ, BZXVZ and SX are
all in verify_ax5b_162_test3a_listing.py's own ROWS (most also in
verify_ax5b_162_exic_listing.py and verify_ax5b_1258_test2_listing.py);
DD is in verify_ax5b_1258_test2_listing.py; KVI in five files
including verify_ibox2_kv_kvi_listing.py; V+ in thirteen; BZXE in
eight; CNOP in twelve; XW in thirty-three.  What TEST 3B adds:
  - a THIRD independent listing witness for EXIC -- 2B's
    "EXIC,I62PSI", 3A's "EXIC,$R", and this one -- and the only one of
    the three whose failure mode is the SUBJECT's address rather than
    the pseudo-IC's;
  - the first row in this repo with an INDEX REGISTER in an
    immediate-index VALUE field, "LVI,$X1,$X0" at 024151.40 -> "20.03
    01", pinning $X0 at word 16 (addr19 = 32).  Every other $X0 in a
    verify file is a J field;
  - the first self-relative row whose COMPUTED target has bit 18 SET,
    "B,$+1.0" at 024162.40 -> 024163.40.  3A's only self-relative row,
    "$+1.32", lands on a .00;
  - B and BD side by side under the same operand: 024160.40 is
    "B,SERS" where 3A's matching rule-(b) row was "BD,SERS", so one
    block now discriminates both unconditional-branch codes.

EVERY SYN IS AN INPUT TO THIS CHECK, NOT A WITNESS -- the caveat
verify_ax5b_16082_16083_listing.py makes about I6088.  A SYN row
MAKES the address field come out right by construction, so the rows
naming one prove only that this assembler places every OTHER field
where the listing places it.  Corroboration exists for most of them
and none of it converts an input into a witness:

  tier 2, a separately read page's own LABEL column, at 600 dpi for
  this file -- I62ITE "BD,$  -ALL INTERRUPTS ENTER HERE." at
  024320.00 and I62PSI "LX,$X0,0  -PSEUDO IC." at 024323.00 (PDF
  p.109); I62EXI "LVI,$X1,%8@777777.40  -IMMED IX." at 024332.00 and
  168 "LX,$X1,I68ID  -UPDATE IDENT." at 024333.00 (PDF p.110).
  tier 2, a separately read page's ENCODINGS -- SEN0 = 001311.00 and
  SSW = 001301.00, from p.110's copy of the same exit sequence
  ("SIC,SEN0+.32" -> 1311.40 80, "B,SSW" -> 1301.10 00 at
  024360.40-024361.00).
  tier 3, arithmetic inside this repo -- BIT8 = 024532.00 is the bit
  table's base 024522 plus 8, matching ax5b_160_test8b.strap's
  LBIT11 = 024535.00.
  tier 3, other verify files -- SEN, SERS, I60SX1 (023041.00) and
  I60S1 (022741.00), from verify_ax5b_16087_listing.py; I62100 =
  024136.00 from verify_ax5b_162_test3a_listing.py.

THE BLOCK'S GENUINE ADDRESS WITNESSES are THREE, and this block is
better anchored than TEST 3A for a reason worth naming: ITS FIRST ROW
CARRIES NO LABEL.  3A had to disclaim I62100, because the SLC set the
counter and I62100 was the next label, so checking it checked the SLC
against the number handed to the SLC.  Here the first label is TWELVE
half-words downstream.  Each witness below was self-checked by
decoding BIT 18 out of the printed octal pair and matching p.108's own
label column:

  024154.00  "LVI,$X1,I62104" -> 24157.43 01.  Octal pair 43 = 100011,
             bit 18 = 1, so the half-word is .40: 024157.40 -- exactly
             where p.108 prints the label I62104.
  024165.00  "LX,$X13,IC262"  -> 24171.32 10.  Pair 32 = 011010, bit
             18 = 0, so .00: 024171.00 -- where p.108 prints the label
             IC262, thirty-one half-words downstream of the SLC.
             024166.00's "SX,$X13,IC262" -> 24171.33 10 repeats it.
             The XW's CONTENT witnesses nothing (all zeros under any
             field layout); only its address counts.
  024157.40  "BADZ,$+1.32"    -> 24161.10 46.  Pair 10 = 001000, bit
             18 = 0, so .00: 024161.00.  And 024157.40 + 1 word + 32
             bits = +96 bits = 024161.00, the "LX,$X1,$X1" row.
  024162.40  "B,$+1.0"        -> 24163.50 00.  Pair 50 = 101000, bit
             18 = 1, so .40: 024163.40 -- and 024162.40 + 1 word is
             024163.40.  This is the repo's first COMPUTED target with
             bit 18 set, so it is the half-word select's own witness
             rather than a place where zero happens to be right.
  024164.40  "BD,$+.32"       -> 24165.04 00.  Pair 04 = 000100, bit
             18 = 0 -> 024165.00, and 024164.40 + 32 bits is 024165.00.

Six more bit-18 decodes, for rows whose target is external, to show
the half-word select is being placed and not assumed.  With these, and
the five above, EVERY row in the block whose operand is a label -- in
this page's own label column or in pp.109-110's -- has had its bit 18
decoded out of the printed octal pair and matched:

  024152.00  "SVA,$X1,I62PSI" -> 24323.03 D0: pair 03 = 000011, bit 18
             = 0 -> 024323.00, and p.109's label column puts I62PSI at
             024323.00.
  024153.40  "LX,$X0,I62EXI"  -> 24332.00 10: pair 00 = 000000, bit 18
             = 0 -> 024332.00 = p.110's I62EXI.
  024154.40  "SVA,$X1,I62ITE" -> 24320.03 D0: pair 03 = 000011, bit 18
             = 0 -> 024320.00 = p.109's I62ITE.
  024156.00  "EXIC,I62PSI"    -> 24323.16 00: pair 16 = 001110, bit 18
             = 0 -> 024323.00 = p.109's I62PSI.  THE TEST'S CENTRAL
             ROW: the pseudo-IC it names is legal (024323.00 is well
             above 32) and it is the SUBJECT the pseudo-IC points at,
             word 16, that is not.
  024163.00  "BD,I62100"      -> 24136.04 00: pair 04 = 000100, bit 18
             = 0 -> 024136.00 = TEST 3A's entry label on PDF p.107.
  024170.00  "BD,168"         -> 24333.04 00: pair 04 = 000100, bit 18
             = 0 -> 024333.00 = p.110's label 168.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted -- each
injection was made with __pycache__ cleared on BOTH sides of the run:

  MISC_CODES["EXIC"] 0b011 -> 0b111
      024156.00  EXIC -> "24323.36 00"                      (1 row)
  UNCOND_BRANCH_CODES["B"] 0b010 -> 0b101
      024153.00  -> "22741.24 00"                           (4 rows)
      024160.40  -> "1304.24 00"
      024162.40  -> "24163.64 00"
      024164.00  -> "1301.24 00"
      Note 024157.00, 024163.00 and 024170.00 do NOT move: they are
      BD.  The two unconditional-branch codes are separately
      discriminable inside this one block, which TEST 3A could not do.
  UNCOND_BRANCH_CODES["NOP"] 0b110 -> 0b111
      024170.40  CNOP -> "0.34 00"                          (1 row)
      The CNOP row is a GAP FILLER, not an emitted statement -- this
      shows the filler really is a NOP and really lands at 024170.40.
  IMM_INDEX_CODES["KVI"] 0b0100 -> 0b0000
      024166.40  KVI -> "777000.33 00"                      (1 row)
  DIR_INDEX_CODES["V+"] 0b01011 -> 0b01010
      024165.40  V+ -> "24532.32 A0"                        (1 row)
  INDICATOR_BITS["XE"] 53 -> 52
      024167.40  BZXE -> "1304.32 40"                       (1 row)
      Note WHERE it shows: the octal pair is UNCHANGED at 32 and only
      the hex byte moves, because 52 and 53 differ solely in the bit
      that lands at 24.  A check reading only the octal field would
      miss it -- independently reproducing the lesson TEST 3A recorded
      for AD 16 -> 17.
  strap_asm.eval_system_symbol's index-register base 16 -> 17
      (the one injection outside opcodes.py: "return n if reg_context
      else (16 + n) * 64", the line that says $Xn IS word 16+n)
      024151.40  LVI,$X1,$X0 -> "21.03 01"                  (3 rows)
      024155.00  Z,$X1       -> "22.22 00"
      024161.00  LX,$X1,$X1  -> "22.02 10"
      This is the injection that tests the claim made two paragraphs
      up, that "LVI,$X1,$X0" pins $X0 at word 16.  Note 024161.00's
      FIRST $X1 does not move -- it is a J field, evaluated with
      reg_context=True, and the same source token therefore means 1 in
      one field and 1088 bits in the other.  The block exercises both
      senses of the same spelling.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_test3b.strap").read())

ROWS = [
    # ---- TEST 3B proper, 024151.40-024162.00 ----------------------
    ('024151.40', '20.03 01',
     'LVI,$X1,$X0           "-TEST 3B, SUBJ INSTR OF EXITC LESS";'
     ' $X0 = word 16, addr19 = 32'),
    ('024152.00', '24323.03 D0',
     'SVA,$X1,I62PSI       (ext) "-THAN 32."; aim the pseudo-IC at $X0'),
    ('024152.40', '23041.00 80',
     'SIC,I60SX1           (ext) "-CLR INDS 0-19"'),
    ('024153.00', '22741.10 00',
     'B,I60S1              (ext) 1260 clear-indicators-0-19'),
    ('024153.40', '24332.00 10',
     'LX,$X0,I62EXI        (ext) the subject instruction, into word 16'),
    ('024154.00', '24157.43 01',
     'LVI,$X1,I62104       in-range label; bit 18 -> 024157.40'),
    ('024154.40', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext) plant the handler in the entry'),
    ('024155.00', '21.22 00',
     'Z,$X1                 so a subject that ran shows up'),
    ('024155.40', '00000003740',
     'DD(BU,32,8),(8)3740   "-ILLEGAL OP."  -- see the docstring'),
    ('024156.00', '24323.16 00',
     'EXIC,I62PSI          (ext) THE TEST: subject lives at word 16'),
    ('024156.40', '1310.00 80',
     'SIC,SEN               (ext) "-NO INTERRUPT WHEN SUBJ INST OF"'),
    ('024157.00', '1304.04 00',
     'BD,SERS               (ext) "-EXIC LESS THAN 32."'),
    ('024157.40', '24161.10 46',
     'I62104 BADZ,$+1.32   self-relative: +96 bits -> 024161.00'),
    ('024160.00', '1310.00 80',
     'SIC,SEN               (ext) "-AD NOT SET WHEN SUBJ INST OF"'),
    ('024160.40', '1304.10 00',
     'B,SERS                (ext) "-EXIC LESS THAN 32."  -- B, not BD'),
    ('024161.00', '21.02 10',
     'LX,$X1,$X1            the BADZ target'),
    ('024161.40', '1310.00 80',
     'SIC,SEN               (ext) "-SUBJ INST OF EXIC NOT NOPED"'),
    ('024162.00', '1304.31 40',
     'BZXVZ,SERS            (ext) "-WHEN IT IS LESS THAN 32."'),
    # ---- routine 1262's exit, 024162.40-024164.40 -----------------
    ('024162.40', '24163.50 00',
     'B,$+1.0               computed target 024163.40; BIT 18 SET'),
    ('024163.00', '24136.04 00',
     'BD,I62100            (ext) the restart link: TEST 3A entry'),
    ('024163.40', '1311.40 80',
     'SIC,SEN0+.32          (ext) SEN0 + 32 bits -> 001311.40'),
    ('024164.00', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP."'),
    ('024164.40', '24165.04 00',
     'BD,$+.32              self-relative: +32 bits -> 024165.00'),
    # ---- the continuity bridge, 024165.00-024171.00 ---------------
    ('024165.00', '24171.32 10',
     'LX,$X13,IC262        "-UPDATE CONTINUITY."; in-range label'),
    ('024165.40', '24532.32 B0',
     'V+,$X13,BIT8          (ext) routine 1262 done = bit 8'),
    ('024166.00', '24171.33 10',
     'SX,$X13,IC262        in-range label, second reference'),
    ('024166.40', '777000.33 04',
     'KVI,$X13,(8)777000.0  compare the whole continuity mask'),
    ('024167.00', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('024167.40', '1304.32 C0',
     'BZXE,SERS             (ext) "-CONTINUITY ERROR."'),
    ('024170.00', '24333.04 00',
     'BD,I68               (ext) on to routine 168, PDF p.110'),
    ('024170.40', '0.30 00',
     'CNOP                  the gap filler ahead of the full-word XW'),
    ('024171.00', '0.00 00 000000.00 00',
     'IC262 XW,0,0,0       "-CONTINUITY REG"; content witnesses'
     ' nothing, only the address does'),
]

# Only the two labels DEFINED inside the transcribed range belong here;
# a SYN'd external would be checking this file against itself.  Unlike
# TEST 3A, BOTH are evidence: TEST 3B's first row carries no label, so
# neither of these sits adjacent to the SLC.  See the docstring.
SYMBOLS = {'I62104': '024157.40', 'IC262': '024171.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 3B '))
