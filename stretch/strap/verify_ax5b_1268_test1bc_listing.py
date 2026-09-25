#!/usr/bin/env python3
"""verify_ax5b_1268_test1bc_listing.py -- jb_ax5b "I-Box 5", routine
1268's TEST 1B and TEST 1C (programs/ax5b_1268_test1bc.strap) against
the listing's printed machine code, PDF pp.110-111, octal
024344.40-024363.00.  30 half-words, no label of its own.

WHAT WAS ALREADY THERE, because the brief asked for the premise to be
checked first.  Routine 1268 runs 024333.00-024411.00 on PDF pp.110-111
and routine 1274's banner follows at 024412.00 on p.112.  TWO of its
blocks were already committed and green before this file existed:
verify_ax5b_1681_listing.py covers 024337.00-024344.00 (test 1A) and
verify_ax5b_1683_listing.py covers 024363.40-024375.40 (tests 2A/2B/2C).
This file fills the largest remaining hole, 024344.40-024363.00, which
is exactly where ax5b_1681_if_close_to_ds.strap says it stopped: "A
'BEW,$' exit at 024344.40, where the listing continues into test 1B ...
1B and 1C need EX, deferred in docs/NEXT.md section 5."  Two holes are
left after this one; see WHERE THIS STOPS.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold carriage-
tape line numbering.  Every verify_ax5b_*.py here says "PDF p.NN".

THE BANNER, verbatim, PDF p.110.  It prints between 024332.40 and
024333.00 and carries NO location of its own:

    ----1268---IF AND DF CLOSE TO DS.

              -THIS TEST IS COMPOSED OF TWO ROUTINES
              -WHICH CHECK THE BELOW FUNCTIONS.

                  -TEST 1 CHECKS IF CLOSE TO DS
                   -IN ALL 3 MEMORIES.

                  -TEST 2 CHECKS DF CLOSE TO DS
                   -IN ALL 3 MEMORIES.

THE DASH COUNTS WERE MEASURED, not eyeballed.  At 500 dpi the ink in
the banner's dash band (full-res rows 422-432 of p.110, page columns
1514-2058) forms runs at 1514+44, 1560+148, 1911+48, 1962+96 against a
48-pixel character pitch: 194 px of ink before "1268" is FOUR dashes,
147 px after is THREE.  That matches the "----NNNN---" every other
banner in this deck uses (1244, 1246, 1250, 1258, 1262 are all quoted
that way in this directory).  NOTE, recorded and not corrected: the
committed programs/ax5b_1683_df_close_to_ds.strap quotes this same
banner as "----1268----IF AND DF CLOSE TO DS.", with four trailing
dashes.  By this measurement that is one dash too many.  Nothing in
that file is edited here.

THE HEADINGS AND ERROR MESSAGES IN THIS RANGE, verbatim with their
octal locations, kept exactly as printed.  Three spelling contrasts
with the neighbouring blocks, ALL re-measured here from
full-resolution crops rather than inherited from the committed I681
and I683 files: test 1A says "INSTRUCTION" where 1B and 1C say
"INST"; 1A prints "-TEST 1A,IF" with NO space after the comma where
1B and 1C print one (p.110 rows 2060-2200 against rows 2990-3090 and
4050-4150); and "-TO SSIP." here carries a period where 024377.40's
on p.111 does not (p.110 rows 4620-4740 against p.111 rows
2340-2900).  None of these is normalised below:

  024344.40  -TEST 1B, IF CLOSE TO DS IN IX STG.
  024351.40  -EXECUTED OLD INST FROM IX STG.
  024352.00  -TEST 1C, IF CLOSE TO DS IN INT MEM.
  024357.00  -EXECUTED OLD INST FROM INT MEM.
  024361.00  -TO SSIP.
  024362.00  -UPDATE CONTINUITY CHECK.

WHAT 1B AND 1C DO, and why they need EX where 1A did not.  Test 1A
plants a word over location I682 and FALLS INTO it, which only works
for a location in the instruction stream.  Index storage and word 9
are not in the instruction stream, so 1B and 1C reach them with
EXECUTE:

  LX,$X1,I68K1 / SX,$X1,$X3   plant [Z,$X2 | NOP] into word 19
  NOP / NOP / NOP
  LX,$X1,I68K2 / SX,$X1,$X3   plant [LVI,$X2,(8)777777.40 | NOP]
  EX,$X3                      execute what is in word 19 NOW
  LX,$X2,$X2                  re-read X2 to set the indicators
  SIC,SEN / BXVZ,SERS         "-EXECUTED OLD INST FROM IX STG."

and 1C is the same with $R (word 9) in place of $X3 (word 19).

PRIMARY SOURCES, quoted first-hand from page images at 350 dpi.

  Reference Manual printed p.49 (PDF p.52), "Execution Instructions":
  "One instruction, EXECUTE, directly specifies the location of a
  second instruction, the subject instruction, which is executed."
  That is the whole semantic claim this file makes about EX.

  Reference Manual printed p.43 (PDF p.46), Figure 11 "Indicator
  List", row 50: mnemonic "XVZ", mask 0, class "T,C", name "Index
  Value Zero", braced with rows 48/49/51 under "Reset by index
  arithmetic ops. other than comparisons".  That is why "LX,$X2,$X2"
  is there: it changes nothing and exists only so an index arithmetic
  operation resets the value indicators to describe X2, which the
  following BXVZ then tests.  (Internal corroboration only, not a
  source: BZXVZ already parses in this assembler, so XVZ is an
  indicator name and not a mnemonic with a trailing clear.)

  Reference Manual printed p.31 (PDF p.34), "Action of Address
  Monitoring Signal": "The indicators that can be turned on by the
  presence of the address monitoring signal are DS (data store), DF
  (data fetch), and IF (instruction fetch)."  Same page, "Definition
  of Monitored Area": "The upper boundary and lower boundary registers
  are located in bits 0-17 and 32-49, respectively, of storage
  location 3", "The boundary control bit, bit 57 of storage location
  3, determines which condition will cause an address monitoring
  signal", and "References to locations 0 and 4 through 31, inclusive,
  never cause an address monitoring signal."

  Reference Manual printed p.32 (PDF p.35): "The three address alarm
  indicators, DS, DF, and IF, are permanent.  Once turned on, they
  remain on until they cause an interruption or are turned off by
  program control."  And, same page, "When an address alarm is caused
  by a data address used in a store-type operation, indicator DS is
  turned on."  Figure 11 on printed p.43 numbers them 19 DS "Data
  Store", 20 DF "Data Fetch", 21 IF "Instruction Fetch", all under
  "Instruction Exception".

  Reference Manual printed p.41 format, as quoted by strap_asm.py's
  enc_sic: SIC's "bits 0-23 storage address (bit address), 24-27
  literal 1000, 28-31 index".  This is what excludes the SIC rows from
  the bit-18 self-checks below.

DOES THIS BEAR ON protViolates?  NO -- and the evidence is the rows
themselves, not the title.  bsv/StretchExecute.bsv's commentary above
protViolates is about the ADDRESS ALARM indicators DS/DF/IF, the
boundary registers in storage location 3, the boundary control bit 57,
and the permanently protected locations 1-3.  Nothing in these 30 rows
writes location 3, reads or writes the mask, names an address below 32
except word 9 and word 19 (which p.31 puts in the "4 through 31 ...
never cause an address monitoring signal" class), or branches on DF,
DS or IF.  The only indicator branch in the block is BXVZ, indicator
50.  "DF CLOSE TO DS" names the data-fetch and data-store PATHS and
"close" is a statement about TIME, not about protection.  This
independently corroborates the reading verify_ax5b_1683_listing.py
reached from the other half of the routine; it is not a new finding.

One near-miss worth naming so nobody else re-finds it and gets
excited.  Printed p.32's list "Address monitoring for Instruction
Fetch includes: ... 3. The location of the subject instruction of the
EXECUTE and EXECUTE INDIRECT AND COUNT operations when this location
is in main storage."  So an EX subject location IS monitored for IF --
but only "when this location is in main storage", and 1B's and 1C's
subjects are word 19 and word 9, which are not.  The overlap is in the
vocabulary, not in the mechanism.

BRANCH POLARITY: BRANCH-TAKEN IS THE ERROR PATH.  These rows use the
MINORITY of the two shapes in this deck.  There is no branch to an OK
label anywhere in the block; both test bodies end "SIC,SEN" then
"BXVZ,SERS", the same order routine 1274 uses.  B<IND> branches when
the indicator is ON, so BXVZ branches when Index Value Zero is on,
i.e. when X2 came out ZERO, i.e. when the STALE "Z,$X2" ran.  Branch
taken -> SERS -> the message, so the message names the anomaly AND is
on the taken path.  Falling through is the pass.  The encoding says
the same thing without the prose: both BXVZ rows print "1304.31 42",
and enc_branch_ind puts branchOn in bit 30 -- hex 42 = 0100_0010 over
bits 24-31, so bit 30 is 1 (branch when ON) and bit 29, the clear bit,
is 0 (no trailing Z).  A BZXVZ would print 40, and a BXVZZ 46.

WITNESS TIERING.  Every SYN in the program file is an INPUT to this
check, not a witness: it makes the address field come out right by
construction, so a SYN'd row proves only that this assembler puts every
OTHER field where the listing puts it.

  (i)  GENUINELY WITNESSED BY THIS BLOCK'S OWN ROWS -- two, both
       self-relative, neither depending on any symbol:
         024357.40  B,$+1.0   and  024361.40  BD,$+.32
       These are the location counter's own witnesses.  There is no
       third: the listing's LABEL COLUMN IS EMPTY FOR ALL 30 ROWS
       (I681 is at 024337.00 above, I683 at 024363.40 below), so this
       block defines no symbol, and there is not even an
       "anchor placed by the SLC" to argue about.  ENT1B in the
       program file is this file's own name for the first row and is
       deliberately NOT asserted in SYMBOLS below.

  (ii) CORROBORATED BY A LABEL COLUMN ON A PAGE READ HERE -- four.
       Still inputs, but the page prints the definition, and all four
       were read from FULL-RESOLUTION crops at 500 dpi (p.111 rows
       3880-4620, p.110 rows 2060-2200), not from a reduced view:
         I68K1  024407.00  (p.111 label column, beside "Z,$X2")
         I68K2  024410.00  (p.111, beside "LVI,$X2,%8@777777.40")
         I681   024337.00  (p.110, beside "LX,$X1,I68K1")
         IC268  024405.00  (p.111, beside "XW,0,0,0  -CONTINUITY
                            REG 1268.")
       The same p.111 crop also prints ICK268 at 024406.00 and I68K3
       at 024411.00, neither of which this block references.

  (iii) ASSUMED, no printed row on pp.110-111 -- five:
         SEN 001310.00, SEN0 001311.00, SERS 001304.00, SSW 001301.00
         (SSIP's, taken from the SYN table ax5b_1274_truncation.strap
         transcribes from PDF p.116), and BIT0 024522.00.

BIT-18 SELF-CHECKS.  Print format: bits 0-17 as 6 octal digits, ".",
bits 18-23 as 2 octal digits, then bits 24-31 as 2 hex digits.  Bit 18
is the TOP bit of the octal pair and is the half-word select.  Every
label-valued and self-relative operand in the block, decoded from the
printed pair and read back against the page's own label column:

  024357.40  B,$+1.0        -> 24360.50 00.  Pair 50 = 101000, bit 18
                             = 1 -> 024360.40.  And 024357.40 + one
                             WORD (64 bits) = 024360.40.  Agrees.
  024361.40  BD,$+.32       -> 24362.04 00.  Pair 04 = 000100, bit 18
                             = 0 -> 024362.00.  And 024361.40 + 32
                             bits = 024362.00, the next row.  Agrees.
  024344.40  LX,$X1,I68K1   -> 24407.02 10.  Pair 02 = 000010, bit 18
  024352.00  (same row text)   = 0 -> 024407.00.  p.111's label column
                             prints I68K1 at 024407.00.  Agrees.
  024347.00  LX,$X1,I68K2   -> 24410.02 10.  Bit 18 = 0 -> 024410.00.
  024354.40  (same row text)   p.111 prints I68K2 at 024410.00.
  024360.00  BD,I681        -> 24337.04 00.  Pair 04 = 000100, bit 18
                             = 0 -> 024337.00.  p.110 prints I681 at
                             024337.00.  Agrees.
  024362.00  LX,$X13,IC268  -> 24405.32 10.  Pair 32 = 011010, bit 18
                             = 0 -> 024405.00.  p.111 prints IC268 at
                             024405.00.  Agrees.
  024363.00  SX,$X13,IC268  -> 24405.33 10.  Pair 33 = 011011, bit 18
                             = 0 -> 024405.00, the same word.  The
                             pair differs from the LX row's ONLY in
                             bit 23, which is the top bit of the 5-bit
                             direct-index code (LX 00001, SX 10001).
  024362.40  V+,$X13,BIT0   -> 24522.32 B0.  Pair 32, bit 18 = 0 ->
                             024522.00.
  024345.00  SX,$X1,$X3     -> 23.03 10.  Bit 18 = 0 -> word 19 (octal
  024347.40                    23), half-word 0.  $X3 is index register
                             3 = word 19.
  024352.40  SX,$X1,$R      -> 11.03 10.  Bit 18 = 0 -> word 9 (octal
  024355.00                    11), half-word 0.  opcodes.py
                             SYSTEM_SYMBOLS "R": (9, 0).
  024350.00  EX,$X3         -> 23.12 00.  Bit 18 = 0 -> word 19.
  024355.40  EX,$R          -> 11.12 00.  Bit 18 = 0 -> word 9.
  024350.40  LX,$X2,$X2     -> 22.04 10.  Bit 18 = 0 -> word 18.
  024356.00
  024345.40  NOP            -> 0.30 00.  Bit 18 = 0, address 0.
  (and the other five NOPs)

EXCLUDED, AND WHY.  Two rows are NOT bit-18 self-checks because their
operand is not a half-word address at all:

  024351.00  SIC,SEN        -> 1310.00 80
  024356.40  (same)
  024360.40  SIC,SEN0+.32   -> 1311.40 80

SIC's operand is a 24-BIT BIT ADDRESS (Reference Manual p.41 format,
quoted above), so its bits 18-23 are a BIT OFFSET WITHIN THE WORD, not
a half-word select.  The SEN rows carry offset 0 and the SEN0+.32 row
carries offset octal 40 = decimal 32, which is the "+.32" written in
the source.  Note the trap the exclusion avoids: 32 bits IS one
half-word, so the digits "40" would look identical under the wrong
reading.  The arithmetic, not the digits, is what settles it.  The
other operand this rule covers, TRANSMIT's A1, does not occur in this
block -- there is no TRANSMIT or SWAP in these 30 rows.

THE "BIT<n>" TABLE: SYN'd INTO, NOT WITNESSED.  The rule elsewhere in
this repo is that BIT<n> is the word at octal 024522 + n.  This block
touches it once, at 024362.40, whose operand field prints 24522 --
consistent with n = 0, but the TABLE'S OWN defining row is not on
pp.110-111, so BIT0 is a SYN here and tier (iii).  Corroboration from
the page without a claim: 024401.00 (routine 1268's second continuity
update, in the block this file does NOT transcribe) prints
"V+,$X13,BIT1 -> 24523.32 B0", consistent with n = 1.

THE STRONGEST SINGLE PIECE OF EVIDENCE that the half-word select is
COMPUTED and not copied is a comparison of ONE IDENTICAL SOURCE LINE
at two half-word parities.  The very same text "B,$+1.0" prints pair
50 here at 024357.40 (an ODD half-word) and pair 10 at 024376.00 on
p.111 -- read at full resolution for this file -- and again pair 10 at
024460.00 in routine 1274 (both EVEN half-words; the 1274 row is
already committed in verify_ax5b_1274_truncation_listing.py).
50 = 101000 against 10 = 001000: they differ in exactly bit 18.  The
same holds, inverted, for "BD,$+.32": pair 04 here at 024361.40
against pair 44 at 024400.00 on p.111 and pair 44 at 024462.00 in
1274.  A constant could not do that.  Those p.111 rows are cited as
corroboration only; they are not transcribed here.

The same p.111 crop also settles this block's LOWER boundary from the
page rather than from another verify file: 024376.40 prints
"BD,I683 -> 24363.44 00", pair 44 = 100100, bit 18 = 1 -> 024363.40 --
exactly where p.111's label column prints I683, and exactly the row
after this file's last.  Nothing overlaps.

NO MNEMONIC HERE IS A FIRST FOR THIS REPO, and each claim was knocked
out by grep rather than asserted.  EX: already in
verify_ax5b_162_int_entry_listing.py, verify_ax5b_162_test1b_listing.py
and verify_ax5b_162_test1cc_listing.py.  V+: in a dozen files,
including verify_ax5b_1258_test1_listing.py's own "V+,$X13,BIT0".
BXVZ, SIC, NOP, LX, SX, B, BD: everywhere.  "EX with a SYSTEM SYMBOL
operand" was checked too and is not a first -- ax5b_162_int_entry.strap
already writes "EX,$X3" and "EX,$L".  The ONE thing that survived the
grep is not a mnemonic at all: "EX,$R" -- EXECUTE with word 9, the
right half of the accumulator, as its subject -- appears nowhere else
in programs/ or verify_*.py.  Flagged as a first only at that
resolution, an operand pairing rather than an instruction.

GLYPHS.  Every label is spelled with a LETTER I -- I681, I68K1, I68K2,
IC268 -- and "SEN0" with a DIGIT zero, while "1B"/"1C"/"1268" stay
digits because they are the deck's test and routine NUMBERS rather
than labels.  When this file was written the letter was house style
for IC268 alone, carried by IC244/IC246/IC258/IC260/IC262/IC274 across
programs/ and verify_*.py, while the body labels were written 1681 and
168K1/2 with an "L" prefixed to make them legal for the assembler, and
the letter-I-versus-digit-1 question was under active dispute.  It is
no longer: docs/listing_typography.md settles it by measurement in
favour of the letter throughout, and the names here are uniform.  The
digit zero of SEN0 still rests on the pixel measurement
programs/ax5b_1274_truncation.strap records for the "SIC,SEN0+.32"
row ("has digit 0 at 45 px").  The one measurement this session did
make is the banner's dash counts, reported above as evidence in its
own paragraph and acted on only for the banner.

THIS FILE IS AN ENCODING ORACLE ONLY.  No run was attempted: the
session that wrote it was instructed not to invoke run_program.sh,
run_tests.sh, bsc or mutation_score.py.  The program file's
substitution blocks (the SERS/SSW hangs, the SEN word, the two planted
constants) exist so that a follow-up can wire it in; they are
UNVERIFIED as an execution.  The file is also NOT listed in
run_tests.sh, which names its programs explicitly rather than globbing,
so it is inert until someone adds it.

PROVEN DISCRIMINATING.  Seven injections, every failure set OBSERVED
and copied out of the run, none predicted -- two of the predictions
made before running were in fact wrong, and the wrong ones are named
below.  "rm -rf __pycache__" was run on BOTH sides of every injection,
because stale bytecode has replayed a previous injection's answer in
this project before; each was reverted by restoring a byte-for-byte
copy taken before the first one, and "git status" was clean (only the
two new files untracked) afterwards.  The injections were chosen to
move DIFFERENT printed columns, and they do -- see WHY THE COLUMNS
SPLIT below.

  strap_asm.py line 1428, the UNCOND_BRANCH/MISC address field,
  "& 0x7FFFF" -> "& 0x7FFFE" (force bit 18, the half-word select,
  to zero)                                    OCTAL PAIR   (1 row)
      024357.40  B,$+1.0  '024360.50 00' -> '024360.10 00'
      Exactly the row the bit-18 self-check above asserts, and only
      that row: it is the block's one branch target at an odd
      half-word.  A check reading the hex byte alone would miss it.
  DIR_INDEX_CODES["LX"] 0b00001 -> 0b00010    HEX BYTE    (7 rows)
      024344.40  '024407.02 10' -> '024407.02 20'
      024347.00, 024350.40, 024352.00, 024354.40, 024356.00,
      024362.00 -- the other six LX rows, all "... 10" -> "... 20".
      PREDICTED WRONGLY as "moves both columns"; the octal pair does
      not move at all.
  DIR_INDEX_CODES["SX"] 0b10001 -> 0b10010    HEX BYTE    (5 rows)
      024345.00  '000023.03 10' -> '000023.03 20'
      024347.40, 024352.40, 024355.00, 024363.00 -- the other four.
  MISC_CODES["EX"] 0b010 -> 0b101             OCTAL PAIR  (2 rows)
      024350.00  '000023.12 00' -> '000023.26 00'
      024355.40  '000011.12 00' -> '000011.26 00'
      The two rows nothing else in this block exercises.  PREDICTED
      WRONGLY as "26" -> the prediction said 25.
  INDICATOR_BITS["XVZ"] 50 -> 51              HEX BYTE    (2 rows)
      024351.40, 024357.00  '001304.31 42' -> '001304.31 C2'
      The octal pair is UNCHANGED and only the hex byte moves,
      because 50 = 110010 and 51 = 110011 differ solely in the bit
      that lands at 24.  The mirror image of the half-word-select
      injection above, and the reason both are in this table.
  DIR_INDEX_CODES["V+"] 0b01011 -> 0b01101    HEX BYTE    (1 row)
      024362.40  '024522.32 B0' -> '024522.32 D0'
      The block's only V+ row.
  UNCOND_BRANCH_CODES["NOP"] 0b110 -> 0b101   OCTAL PAIR  (6 rows)
      024345.40, 024346.00, 024346.40, 024353.00, 024353.40,
      024354.00  '000000.30 00' -> '000000.24 00'
      All six NOPs and nothing else.

WHY THE COLUMNS SPLIT, since the pattern is not arbitrary.  The
printed octal pair is bits 18-23 and the hex byte is bits 24-31.  A
direct-index code is 5 bits at 23-27, so its TOP bit is the only one
inside the pair -- LX 00001->00010, SX 10001->10010 and V+
01011->01101 all leave bit 23 alone, which is why all three move the
hex byte only.  A misc/uncond-branch code is 3 bits at 19-21, wholly
inside the pair, which is why EX and NOP move the pair only.  An
indicator number is 6 bits at 19-24, straddling the boundary, and
50->51 happens to flip the one bit on the hex side.

MEASURED NULL, with its arithmetic reason.  enc_branch_ind's `clear`
bit, forced to 0 ("(clear, 1)" -> "(0, 1)" at strap_asm.py line 355):
ALL 30 ROWS STILL PASS.  Neither BXVZ row carries a trailing Z, so the
clear bit is already 0 in both and nothing can move.  That field is
this block's one blind spot, and it is arithmetic, not luck -- the
block simply contains no branch-on-indicator with a trailing Z.  (For
contrast, verify_ax5b_162_test3a_listing.py does catch it, on its
BADZ row.)

WHERE THIS STOPS, and what is next.  This file ends at 024363.00,
where routine 1268's test 2A begins at 024363.40 (already covered by
verify_ax5b_1683_listing.py).  Two holes are left in routine 1268:

  024376.00-024411.00, PDF p.111 -- THE HIGHER-VALUE ONE.  It is the
  tail of test 2 (B,$+1.0 / BD,I683 / SIC,SEN0+.32 / B,SSW / BD,$+.32),
  the second continuity update (LX,$X13,IC268 / V+,$X13,BIT1 /
  SX,$X13,IC268), the continuity CHECK (LX,$X13,IC268 /
  KV,$X13,ICK268 / SIC,SEN / BZXE,SERS "-CONTINUITY ERROR."), "BD,174",
  a CNOP, and then the routine's whole CONSTANT POOL: IC268 at
  024405.00, ICK268 at 024406.00, I68K1 at 024407.00, I68K2 at
  024410.00, I68K3 at 024411.00.  Transcribing it would upgrade five
  addresses that verify_ax5b_1681_listing.py, verify_ax5b_1683_listing
  .py and this file all currently take as SYN'd inputs into witnessed
  rows.
  024333.00-024336.00, PDF p.110 -- the routine's entry (168 LX,$X1,
  I68ID / SX,$X1,DPET13 / SIC,RET / B,IDF1 / Z,IC268 / BD,I681), a
  CNOP, and the ident row "I68ID %IQSZ@DD%BU,64,8@,1268  Z" at
  024336.00, which the listing prints with a LOCATION AND NO MACHINE
  CODE.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_1268_test1bc.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from a printed address; see WITNESS TIERING.
ROWS = [
    # ---- TEST 1B: store into INDEX STORAGE, then EXECUTE it --------
    ('024344.40', '24407.02 10',
     'LX,$X1,I68K1          (ext) "-TEST 1B, IF CLOSE TO DS IN IX STG."'),
    ('024345.00', '23.03 10',
     'SX,$X1,$X3            plant the OLD instruction in word 19'),
    ('024345.40', '0.30 00',   'NOP'),
    ('024346.00', '0.30 00',   'NOP'),
    ('024346.40', '0.30 00',   'NOP'),
    ('024347.00', '24410.02 10',
     'LX,$X1,I68K2          (ext) p.111 label column: 024410.00'),
    ('024347.40', '23.03 10',
     'SX,$X1,$X3            plant the NEW one over it'),
    ('024350.00', '23.12 00',
     'EX,$X3                execute what is in word 19 NOW'),
    ('024350.40', '22.04 10',
     'LX,$X2,$X2            re-read X2 to set the indicators'),
    ('024351.00', '1310.00 80',
     'SIC,SEN               (ext) bit address, NOT a half-word select'),
    ('024351.40', '1304.31 42',
     'BXVZ,SERS             (ext) "-EXECUTED OLD INST FROM IX STG."'),
    # ---- TEST 1C: store into INTERNAL MEMORY (word 9), then EXECUTE
    ('024352.00', '24407.02 10',
     'LX,$X1,I68K1          (ext) "-TEST 1C, IF CLOSE TO DS IN INT MEM."'),
    ('024352.40', '11.03 10',
     'SX,$X1,$R             plant the OLD instruction in word 9'),
    ('024353.00', '0.30 00',   'NOP'),
    ('024353.40', '0.30 00',   'NOP'),
    ('024354.00', '0.30 00',   'NOP'),
    ('024354.40', '24410.02 10',
     'LX,$X1,I68K2          (ext)'),
    ('024355.00', '11.03 10',
     'SX,$X1,$R             plant the NEW one over it'),
    ('024355.40', '11.12 00',
     'EX,$R                 execute what is in word 9 NOW'),
    ('024356.00', '22.04 10',
     'LX,$X2,$X2            re-read X2 to set the indicators'),
    ('024356.40', '1310.00 80',
     'SIC,SEN               (ext)'),
    ('024357.00', '1304.31 42',
     'BXVZ,SERS             (ext) "-EXECUTED OLD INST FROM INT MEM."'),
    # ---- loop once, return to SSIP ---------------------------------
    ('024357.40', '24360.50 00',
     'B,$+1.0               self-relative: pair 50, bit 18 -> 024360.40'),
    ('024360.00', '24337.04 00',
     'BD,I681               (ext) bit 18 = 0 -> 024337.00, p.110'),
    ('024360.40', '1311.40 80',
     'SIC,SEN0+.32          (ext) pair 40 = a BIT offset of 32'),
    ('024361.00', '1301.10 00',
     'B,SSW                 (ext) "-TO SSIP."'),
    ('024361.40', '24362.04 00',
     'BD,$+.32              self-relative: +32 bits -> 024362.00'),
    # ---- the routine's continuity register, test 1's bit -----------
    ('024362.00', '24405.32 10',
     'LX,$X13,IC268         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('024362.40', '24522.32 B0',
     'V+,$X13,BIT0          (ext) test 1 done = bit 0'),
    ('024363.00', '24405.33 10',
     'SX,$X13,IC268         (ext) pair 33 vs the LX row"s 32: bit 23'),
]

# The listing's LABEL COLUMN IS EMPTY for all 30 of these rows, so this
# block defines no symbol and there is nothing to assert here.  ENT1B
# in the program file is this file's own name for the first row, placed
# by the SLC; asserting it would check the SLC against the number this
# transcription handed the SLC.  See WITNESS TIERING.
SYMBOLS = {}

finish(check_rows(prog, ROWS, SYMBOLS, label='1268 1B/1C '))
