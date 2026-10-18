#!/usr/bin/env python3
"""verify_ax5b_162_test1a_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), the ROUTINE HEAD and TEST 1A
(../decks/ax5b_162_test1a.strap) against the listing's printed machine
code, PDF pp.87-89, octal 023304.00-023306.40 and
023310.00-023373.00.  109 rows: 6 in the head, 103 in TEST 1A.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

WHERE THIS SITS.  023373.00 is the last row transcribed; 023373.40 is
where verify_ax5b_162_test1b_listing.py's I6212 begins.  The two files
abut exactly and share no row.  Upward, PDF p.87 is the routine's own
first page, so nothing precedes the head.

THE ROUTINE BANNER, verbatim, PDF p.87:

    ----I262---TEST EX AND EXIC.

Measured on that printed row at 600 dpi: dashes 54/54/58/56 px, then a
12 px bare stroke, then 2 = 42 and 6 = 47; and the I of EXIC on the
SAME ROW is 16 px.  docs/listing_typography.md puts letter I at 9-18 px
and digit 1 at 30-42 px with no overlap, so the banner reads I262.
The same measurement repeats in the name field at 023310.00: "I621" is
I = 15, 6 = 45, 2 = 44, 1 = 36 -- letter and digit inside ONE token --
and its operand "I62XW1" is I = 12, 6 = 45, 2 = 42, X = 45, W = 51,
1 = 35.

THE FULL HEADER BLOCK, the eight error entries, the seven case
headers and the two DECK-TYPO verdicts ("-UPDATE INDENT." at 023304.00
and "-SETUP 8D INT TBL" at 023310.40) are quoted verbatim, with their
measurements, in ../decks/ax5b_162_test1a.strap's own header.  Summary
of the verdicts: both are clean, correctly formed WRONG glyphs, not
ragged correct ones -- the intruding N of INDENT is 45 px against the
word's own second N at 47 px and the pitch says seven cells where
"IDENT." needs six, and the 8 of "8D" resolves at 6x into two closed
bowls with no left stem against the 44 px straight-stemmed B of "TBL"
nine cells later on the same row.  The 8D verdict does not rest on the
glyph alone: TEST 1CC's sibling stanza prints "-DO BB, SETUP BD INT
TBL." with a clean B while loading the SAME constant I62K1 (quoted
from PDF p.93 in verify_ax5b_162_int_entry_listing.py).

THE HEADER MISDESCRIBES TEST 1 AS WELL AS TEST 3.  Its TEST 3 line
says "THE ILLEGAL COMBINATIONS OF EX AND EXIC" where 3A and 3B are
both EXIC-alone address-range checks.  Its TEST 1 lines -- "ALL
CLASSES OF INSTRUCTIONS" and "ILLEGAL EXECUTES WILL SET THE CORRECT
INDICATORS" -- describe 1B and 1CC and omit BOTH of 1A's subjects.

WHAT THE "SEVEN MEMORY COMBINATIONS" ACTUALLY ARE.  Read off the page,
not from docs/NEXT.md.  The deck's own words at 023316.40-023317.00
are "-CHECK SEVEN POSSIBILITIES OF / -EXECUTES IN 3 MEMORIES.", and
seven stanza headers follow:

    1  023316.40  -MAIN TO MAIN.              EX main -> LX main
    2  023324.00  -MAIN TO IX.                EX main -> LX in $X3
    3  023331.40  -MAIN TO INTERNAL.          EX main -> LX in $R
    4  023337.00  -MAIN TO IX TO MAIN.        EX -> EX in $X2 -> LX main
    5  023345.00  -MAIN TO INTERNAL TO MAIN.  EX -> EX in $R  -> LX main
    6  023353.40  -MAIN TO IX TO IX.          EX -> EX in $X2 -> LX in $X3
    7  023361.00  -MAIN TO INT TO INT.        EX -> EX in $R  -> LX in $L

The three memories are MAIN core storage, INDEX storage and the
INTERNAL registers, which on the 7030 share one address space.  Three
one-level cases, one per memory, then four two-level chains out of the
nine that exist.  The shape repeats after case 4 and the rows below say
so plainly rather than re-arguing each one: every stanza is
plant-the-subject / LVI+SVA the landing / Z,$X1 / EX / LX,$X1,$X1 /
BZXVZ / BZXCZ / SIC,SEN / B,SERS.  What varies is only WHERE the
subject was put and which constant supplied the middle level.

THE DOUBLED K-WORD IS THE MECHANISM.  PDF p.109 (asserted in
verify_ax5b_162_int_entry_listing.py) makes I62K2/K3/K4 full WORDS
holding the same half-word twice -- 024173.00 and 024173.40 both print
"24321.12 00".  "LX,$X2,I62K2" loads all 64 bits into word 18 and
"EX,$X2" prints pair 12, bit 18 = 0, so it takes half-word 0.  The
doubling is why one register can hold a whole intermediate level
regardless of which half the EX selects.

BRANCH POLARITY, DECIDED PER CHECK AND SETTLED FROM THE PRINTED HEX.
strap_asm.enc_branch_ind puts branchOn at bit 30, so hex 42 is
branch-on-ON and 40 is branch-on-OFF.  All fourteen BZXVZ/BZXCZ rows
here print 40, and all fourteen targets are the first row of the NEXT
stanza (arithmetic in the rows below).  So in every one of the seven
cases the pair SKIPS the error and the error entry is the fall-through
-- uniform, unlike TEST 1B, whose MISC class inverts.

BIT-18 SELF-CHECKS, decoded out of the printed octal pair and read
back against the page's own label column (bit 18 is the TOP bit of the
pair; the print format is bits 0-17 as six octal digits, ".", bits
18-23 as two octal digits, then bits 24-31 as two hex digits).

  TEN OF THE ELEVEN IN-RANGE LABEL OPERANDS (the eleventh, "EX,I623",
  gets its own paragraph below).  Each LVI also carries its index
  digit in bits 19-22 of the same pair -- $X1 -> 03, $X2 -> 05,
  $X3 -> 07 -- so one printed pair checks two fields at once.

  023312.40  "LVI,$X1,I622"  -> 23314.03 01.  Pair 03 = 000011, bit 18
             = 0 -> 023314.00, where p.88 prints I622.  Field 03 = $X1.
  023314.00  "BD,I624"       -> 23316.44 00.  Pair 44 = 100100, bit 18
             = 1 -> 023316.40, where p.88 prints I624.
  023320.00  "LVI,$X2,I625"  -> 23321.45 01.  Pair 45 = 100101, bit 18
             = 1 -> 023321.40 = I625.  Field 05 = $X2.
  023325.40  "LVI,$X2,I626"  -> 23327.05 01.  Bit 18 = 0 -> 023327.00
             = I626.  Same index field 05, bit 18 flipped -- the two
             pairs differ ONLY in bit 18.
  023333.00  "LVI,$X2,I627"  -> 23334.45 01.  Bit 18 = 1 -> 023334.40
             = I627.
  023340.40  "LVI,$X3,I628"  -> 23342.47 01.  Pair 47 = 100111, bit 18
             = 1 -> 023342.40 = I628.  Field 07 = $X3.
  023347.00  "LVI,$X3,I629"  -> 23351.07 01.  Bit 18 = 0 -> 023351.00
             = I629.  Field 07 again.
  023354.40  "LVI,$X1,I6210" -> 23356.43 01.  Pair 43 = 100011, bit 18
             = 1 -> 023356.40 = I6210.  Back to field 03.
  023363.00  "LVI,$X1,I6211" -> 23365.03 01.  Bit 18 = 0 -> 023365.00
             = I6211.
  023370.00  "BD,I621"       -> 23310.04 00.  Pair 04 = 000100, bit 18
             = 0 -> 023310.00 = I621.  Its LOCATION is evidence (it is
             right only if all 96 preceding rows of TEST 1A were sized
             right); its TARGET traces straight back to this file's own
             SLC, so the target is not.

  SIX MORE DECODES, for rows whose address comes from neither a SYN
  nor a label -- the location counter's own witnesses.  (Fourteen of
  the seventeen self-relative rows are the BZXVZ/BZXCZ pairs and are
  decoded inline in the rows below; two of those are spelled out here
  because theirs are the bit-18-is-1 cases.)

  023311.40  "CB+,$X1,$-.32" -> 23311.03 48.  Bit 18 = 0 -> 023311.00,
             which is 023311.40 minus 32 bits -- the top of the
             table-fill loop.  (Its twin in TEST 1CC at 023476.00
             prints 43, bit 18 = 1: same instruction, other half.)
  023327.40  "BZXVZ,$+2.00"  -> 23331.71 40.  Pair 71 = 111001, bit 18
             = 1 -> 023331.40, and 023327.40 + 2 words = 023331.40.
  023330.00  "BZXCZ,$+1.32"  -> 23331.70 40.  Bit 18 = 1 -> 023331.40,
             the same target one row later: 1 word + 32 bits.
  023367.40  "B,$+1.0"       -> 23370.50 00.  Pair 50 = 101000, bit 18
             = 1 -> 023370.40.  Note the low bits against 023370.00's
             "BD,I621" 04: B is 0o10 in this field and BD is 0o04, and
             bit 18 adds 0o40.
  023371.40  "BD,$+.32"      -> 23372.04 00.  Bit 18 = 0 -> 023372.00.
  023315.00  "LX,$X0,$"      -> 23315.00 10.  NOT a bit-18 decode --
             see the exclusions below -- but the 18-bit word address
             is its own location, and the pair's 00 is the J field for
             $X0 (LX,$X1 prints 02, LX,$X2 04, LX,$X3 06).

  THE ONE EX ROW THAT IS ADDRESS EVIDENCE, and it is also the CNOP
  witness.  All eight EX rows in this range print octal pair 12 --
  bit 18 = 0 in every one, so the harvest is thin and is not dressed
  up (contrast TEST 1CC's "EX,I62B6" = 24205.52, bit 18 = 1).  Only
  ONE of the eight names an in-range label; of the rest, two name the
  SYN'd I62EXT and five resolve through "$" system symbols ($X3, $R,
  $X2, $R, $R), which are not SYNs but are just as much inputs.

  023313.40  "EX,I623" -> 23315.12 00.  Pair 12 = 001010, bit 18 = 0
             -> 023315.00, where p.88 prints I623.  AND THAT IS THE
             CNOP CHECK: 023314.40 is an odd half-word, so the CNOP
             there must EMIT a filler NOP ("0.30 00" on the page).  If
             it emitted nothing, I623 would fall at 023314.40 and this
             pair would have to read 52.  It reads 12.  The CNOP row,
             the EX row and the label assertion below are one chain.

  FOUR EXCLUSIONS, THREE REASONS, and they cover every remaining
  label-valued operand here:
    * LX and SX -- Reference Manual printed p.23: "The two exceptions
      use only 18 bits of the effective address because they require
      full-word operands."  Bit 18 is not part of the address, so
      "LX,$X1,I62ID" -> 23307.02 and "SX,$X13,IC262" -> 24171.33 carry
      no half-word select.  Their pairs are pure J field.
    * SIC and TRANSMIT's A1 -- 24-bit BIT addresses, where the printed
      pair is a bit offset, not bits 18-23 of a half-word address.
      "SIC,RET" -> 1306.40 80 is bit 32 of word 0o1306, and
      "SIC,SEN0+.32" -> 1311.40 80 is bit 32 of word 0o1311.  Reading
      either pair as a half-word select would give ".40" and the same
      digits -- 32 bits IS one half-word -- so only the arithmetic
      separates them, and this block has no TRANSMIT.
    * branch targets and V+/KV use bit 18 as the half-word select, and
      are decoded above.  "V+,$X13,BIT0" -> 24522.32 B0, pair 32 =
      011010, bit 18 = 0 -> 024522.00, which is the BIT0 that
      ax5b_162_int_entry.strap SYNs from PDF p.114; TEST 1B's
      "V+,$X13,BIT1" prints 24523.32 on the same page range.

WITNESS TIERING.  Every SYN in the program file is an INPUT: it makes
the address field come out right by construction, so a row naming one
proves only that this assembler puts every OTHER field where the
listing puts it.  An SLC-placed label is an ANCHOR, not evidence.

  ANCHORS (asserted below, not evidence): I62 = 023304.00 and
    I621 = 023310.00.  Each is the first label after an SLC, so
    asserting it checks this transcription against the number it
    handed the SLC.  "BD,I621" at 023306.40 and again at 023370.00
    traces straight back to that same SLC and is not an address
    witness either.
  EVIDENCE (ten labels): I622, I623, I624, I625, I626, I627, I628,
    I629, I6210, I6211 -- every one DEFINED inside the transcribed
    range and NAMED by an in-range operand whose printed pair is
    decoded above.
  INPUTS, corroborated by a separately read page's own label column
    (PDF p.109, read for verify_ax5b_162_int_entry_listing.py and
    asserted there): I62K1, I62K2, I62K3, I62K4, I62INT, I62ITE,
    I62EXT, I62EX, I62XW1.
  INPUTS resting on other files in this repo, not on a page read for
    this block: SEN, SERS, SEN0, SSW, RET, DPET13, IDF1, BIT0.
  INPUTS resting on nothing but the operand field of these pages:
    IC262 (024171.00) and I62ID (023307.00).  Said plainly.  I62ID
    gets one independent corroboration that does NOT convert it: the
    location counter, starting from the SLC at 023304.00, arrives at
    023307.00 after exactly the six head rows -- which is where the
    page prints the ident line.

AND TEST 1A CORROBORATES A CONJECTURE verify_ax5b_162_int_entry_
listing.py had to flag as one.  That file argues I62K1 ("BD,I62ITE",
landing on the DISABLED half 024320.00) pairs with "SVA ... I62ITE"
while I62K6 ("B,I62ITE+.32") pairs with "SVA ... I62ITE+.32".  TEST 1A
is an independent instance: its fill loop loads I62K1 at 023310.40,
and all EIGHT SVA rows below name bare I62ITE (pair bit 18 = 0).
Eight for eight, no exception.  Corroborating, not proving.

A GLYPH NOTE THAT CHANGES NO BIT.  023370.40's operand prints SEN?
whose fourth character measures 56 px, against 40-45 px for every
digit on that row and the row above it ("BD,I621": B 48, D 50, I 13,
6 45, 2 42, 1 40).  docs/listing_typography.md §6 measured letter O at
15-22% wider than digit 0 and supported "SENO SYN,SEN0" on PDF p.114;
this is a second, independent instance pointing the same way, and
rather wider.  Kept spelled SEN0 to match
verify_ax5b_162_test1b_listing.py, and harmless either way: it is a
SYN taken from the row that names it.

NO MNEMONIC HERE IS A FIRST, and that was checked by grep rather than
asserted.  The candidates were knocked out one at a time:
  * EX with a REGISTER subject -- "EX,$X3" and "EX,$R" are already in
    verify_ax5b_1268_test1bc_listing.py, and "EX,$X3"/"EX,$L" in
    verify_ax5b_162_int_entry_listing.py.  "EX,$X2" here is the same
    shape with a different digit.
  * SX with a register destination -- "SX,$X1,$L", "SX,$X1,$R",
    "SX,$X1,$X3" and "SX,$X1,$X4" already exist in ../decks/*.strap.
  * Z to a core word -- "Z,IC246", "Z,IC258", "Z,IC268", "Z,IC274"
    already exist, so "Z,IC262" is not one.
  * CB+, SR, SVA, LVI, BZXVZ, BZXCZ, V+, SIC, CNOP -- all witnessed by
    verify_ax5b_162_test1b_listing.py and verify_ax5b_162_test1cc_
    listing.py alone.
  What the block does add, stated as the smaller claim it is: EIGHT
  EX ROWS IN 109, more than any other single file in the repo --
  counted, not guessed: TEST 1B five, TEST 1CC four,
  ax5b_162_int_entry six (three source texts, each a doubled word),
  verify_ax5b_1268_test1bc two, and the hand-written behavioural
  programs six (ex_exe), four (ex_subject), four (ex_monitor), two
  (ex_exe_bind).  One smaller claim, cut
  back after checking it: "LX,$X0,$" is the first LX in this corpus
  whose operand is the bare location counter -- grepped across
  ../decks/*.strap, verify_*.py, test_*.py and line_addresses.py, zero
  hits -- but it is NOT a new operand SHAPE, since
  "LX,$X1,(8)103.0", "LX,$X0,1.0" and "LX,$X1,1.0" already put bit
  addresses in that same field.  "$" is one more expression form in a
  field that already takes them.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted.  Each
injection was applied to strap/opcodes.py with __pycache__ removed on
BOTH sides of the run, and the PATCHED LINE WAS PRINTED BACK before
the run -- a sed that silently fails to match prints ALL TESTS PASSED,
which reads exactly like an honest null, and this project has been
bitten by that twice.

  MISC_CODES["EX"] 0b010 -> 0b110
      023313.40, 023321.00, 023326.40, 023334.00, 023342.00,
      023350.40, 023356.00, 023364.40                       (8 rows)
      Every EX in the block, one per stanza plus the relinquish-control
      subject.  The pair moves 12 -> 32 where bit 18 is 0 throughout,
      so the code field is being checked beside a bit 18 that does not
      move.  This is the block's reason to exist.
  INDICATOR_BITS["XCZ"] 48 -> 14
      023322.40  BZXCZ -> "023324.07 40"                     (7 rows)
      023330.00  BZXCZ -> "023331.47 40"
      023335.40, 023343.40, 023352.00, 023357.40, 023366.00
      All seven BZXCZ rows and nothing else: the seven BZXVZ rows
      (XVZ = 50) are untouched, which separates the two indicator
      numbers from each other and not merely from zero.  14 and not a
      one-bit flip on purpose, and the reason was CHECKED not assumed
      -- a script over INDICATOR_BITS.values() reports that 14 is the
      ONLY number in 0-63 the table does not already hold (48's
      neighbours are XVLZ = 49 and XVZ = 50), so any other choice
      would have been a table collision rather than a clean
      perturbation.  The same number, for the same reason, as
      verify_ax5b_162_test1b_listing.py's RZ injection.
  UNCOND_BRANCH_CODES["NOP"] 0b110 -> 0b111
      023314.40  CNOP -> "000000.34 00"                      (1 row)
      The CNOP filler, and ONLY it.  The block writes no NOP of its
      own, so this row proves the pseudo-op really routes through the
      NOP encoding -- which is the other half of the "EX,I623" ->
      023315.00 chain above.
  DIR_INDEX_CODES["SR"] 0b10111 -> 0b10110
      023312.00  SR,$X1,$IA -> "000002.03 60"                (1 row)
      SR occurs exactly once in 109 rows; nothing else moves.
  CB_CODES["CB+"] (0b10, 0, 0) -> (0b10, 1, 0)
      023311.40  CB+,$X1,$-.32 -> "023311.03 4C"             (1 row)
      The refill bit, which only the hex byte carries (48 -> 4C), and
      the one CB+ in the block.

  THREE OF THE FIVE ISOLATE TO A SINGLE ROW, AND NONE OF THE FIVE
  PRODUCED A NULL, so no liveness proof is owed here.  Each injection
  was confirmed APPLIED before its run -- the patch script aborts
  unless its anchor occurs exactly once, prints the patched whole line
  back, and "git diff -U0 -- strap/opcodes.py" was printed beside it;
  after each revert the same diff came back empty.  That guard is not
  ceremony: a substitution that silently fails to match prints ALL
  TESTS PASSED, which is indistinguishable from an honest null, and
  this project has been bitten by it twice.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_162_test1a.strap").read())

ROWS = [
    # ---- the routine head, PDF p.87 ---------------------------------
    ('023304.00', '23307.02 10',
     'I62 LX,$X1,I62ID     (ext) "-UPDATE INDENT." [sic]; LX, no bit 18'),
    ('023304.40', '1437.03 10',
     'SX,$X1,DPET13        (ext) the ident cell'),
    ('023305.00', '1306.40 80',
     'SIC,RET              (ext) BIT address: bit 32 of word 0o1306'),
    ('023305.40', '1443.10 00',
     'B,IDF1               (ext) "-PRINT ID."'),
    ('023306.00', '24171.22 00',
     'Z,IC262              (ext) clear 1262\'s continuity word'),
    ('023306.40', '23310.04 00',
     'BD,I621              anchor target; bit 18 = 0 -> 023310.00'),
    # 023307.00 is the ident word: LOCATION printed, machine code NOT.
    # SLC across it; I62ID is a SYN.  See the program file's header.

    # ---- TEST 1A: fill the 64-word interrupt table, PDF p.88 --------
    ('023310.00', '24326.02 10',
     'I621 LX,$X1,I62XW1   (ext) "-TEST 1A, CHK EX CNTRL."; count 64'),
    ('023310.40', '24172.04 10',
     'LX,$X2,I62K1         (ext) "-SETUP 8D INT TBL..." [sic]; "BD,I62ITE" x2'),
    ('023311.00', '24220.05 11',
     'SX,$X2,I62INT($X1)   (ext) index-modified store; idx 1 in bits 28-31'),
    ('023311.40', '23311.03 48',
     'CB+,$X1,$-.32         self-relative: bit 18 = 0 -> 023311.00, -32 bits'),
    ('023312.00', '2.03 70',
     'SR,$X1,$IA            the Interruption Address register, word 2'),
    # ---- (a) EX must not relinquish control -------------------------
    ('023312.40', '23314.03 01',
     'LVI,$X1,I622         in-range; bit 18 = 0 -> 023314.00; field 03 = $X1'),
    ('023313.00', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext) plant I622 in the interrupt landing'),
    ('023313.40', '23315.12 00',
     'EX,I623              in-range; bit 18 = 0 -> 023315.00 -- the CNOP chain'),
    ('023314.00', '23316.44 00',
     'I622 BD,I624         in-range; bit 18 = 1 -> 023316.40'),
    ('023314.40', '0.30 00',
     'CNOP                  odd half-word: EMITS the filler NOP'),
    ('023315.00', '23315.00 10',
     'I623 LX,$X0,$         the subject; "$" is its own word 0o23315'),
    ('023315.40', '1310.00 80',
     'SIC,SEN              (ext) "-EXECUTE RELINQUISHES CONTROL TO"'),
    ('023316.00', '1304.10 00',
     'B,SERS               (ext) "-SUBJECT INSTRUCTION."'),

    # ---- 1. MAIN TO MAIN --------------------------------------------
    ('023316.40', '24322.02 10',
     'I624 LX,$X1,I62EX    (ext) "-CHECK SEVEN POSSIBILITIES OF"'),
    ('023317.00', '24321.03 10',
     'SX,$X1,I62EXT        (ext) "-EXECUTES IN 3 MEMORIES."'),
    ('023317.40', '21.22 00',
     'Z,$X1                 "-MAIN TO MAIN."; word 17'),
    ('023320.00', '23321.45 01',
     'LVI,$X2,I625         bit 18 = 1 -> 023321.40; field 05 = $X2'),
    ('023320.40', '24320.05 D0',
     'SVA,$X2,I62ITE       (ext)'),
    ('023321.00', '24321.12 00',
     'EX,I62EXT            (ext) THE INSTRUCTION UNDER TEST'),
    ('023321.40', '21.02 10',
     'I625 LX,$X1,$X1       set the index indicators from $X1'),
    ('023322.00', '23324.31 40',
     'BZXVZ,$+2.00          bit 18 = 0 -> 023324.00; +2 words; hex 40 = on OFF'),
    ('023322.40', '23324.30 40',
     'BZXCZ,$+1.32          -> 023324.00, the same target: both SKIP the error'),
    ('023323.00', '1310.00 80',
     'SIC,SEN              (ext) "-EX IN MAIN TO LX IN MAIN FAILS,LX"'),
    ('023323.40', '1304.10 00',
     'B,SERS               (ext) "-NOT EXECUTED."'),

    # ---- 2. MAIN TO IX ----------------------------------------------
    ('023324.00', '24322.02 10',
     'LX,$X1,I62EX         (ext) "-MAIN TO IX."'),
    ('023324.40', '23.03 10',
     'SX,$X1,$X3            the subject into INDEX storage, word 19'),
    ('023325.00', '21.22 00',
     'Z,$X1'),
    ('023325.40', '23327.05 01',
     'LVI,$X2,I626         bit 18 = 0 -> 023327.00; same field 05 as 023320.00'),
    ('023326.00', '24320.05 D0',
     'SVA,$X2,I62ITE       (ext)'),
    ('023326.40', '23.12 00',
     'EX,$X3                EX of an INDEX REGISTER; word 19, pair 12'),
    ('023327.00', '21.02 10',
     'I626 LX,$X1,$X1'),
    ('023327.40', '23331.71 40',
     'BZXVZ,$+2.00          pair 71: bit 18 = 1 here -> 023331.40'),
    ('023330.00', '23331.70 40',
     'BZXCZ,$+1.32          -> 023331.40, same target'),
    ('023330.40', '1310.00 80',
     'SIC,SEN              (ext) "-EX IN MAIN TO LX IN IX STG FAILS,"'),
    ('023331.00', '1304.10 00',
     'B,SERS               (ext) "-LX NOT EXECUTED."'),

    # ---- 3. MAIN TO INTERNAL ----------------------------------------
    ('023331.40', '24322.02 10',
     'LX,$X1,I62EX         (ext) "-MAIN TO INTERNAL."'),
    ('023332.00', '11.03 10',
     'SX,$X1,$R             the subject into an INTERNAL register, word 9'),
    ('023332.40', '21.22 00',
     'Z,$X1'),
    ('023333.00', '23334.45 01',
     'LVI,$X2,I627         bit 18 = 1 -> 023334.40'),
    ('023333.40', '24320.05 D0',
     'SVA,$X2,I62ITE       (ext)'),
    ('023334.00', '11.12 00',
     'EX,$R                 EX of word 9 -- p.50\'s "any addressable location"'),
    ('023334.40', '21.02 10',
     'I627 LX,$X1,$X1'),
    ('023335.00', '23337.31 40',
     'BZXVZ,$+2.00          bit 18 = 0 -> 023337.00'),
    ('023335.40', '23337.30 40',
     'BZXCZ,$+1.32          -> 023337.00'),
    ('023336.00', '1310.00 80',
     'SIC,SEN              (ext) "-EX IN MAIN TO LX IN INT FAILS,"'),
    ('023336.40', '1304.10 00',
     'B,SERS               (ext) "-LX NOT EXECUTED."'),

    # ---- 4. MAIN TO IX TO MAIN, PDF p.89 ----------------------------
    ('023337.00', '24322.02 10',
     'LX,$X1,I62EX         (ext) "-MAIN TO IX TO MAIN."'),
    ('023337.40', '24321.03 10',
     'SX,$X1,I62EXT        (ext) the LX subject goes to MAIN'),
    ('023340.00', '24173.04 10',
     'LX,$X2,I62K2         (ext) the doubled word "EX,I62EXT", p.109'),
    ('023340.40', '23342.47 01',
     'LVI,$X3,I628         bit 18 = 1 -> 023342.40; field 07 = $X3'),
    ('023341.00', '24320.07 D0',
     'SVA,$X3,I62ITE       (ext) field 07 again'),
    ('023341.40', '21.22 00',
     'Z,$X1'),
    ('023342.00', '22.12 00',
     'EX,$X2                EX in main -> EX in IX -> LX in main'),
    ('023342.40', '21.02 10',
     'I628 LX,$X1,$X1'),
    ('023343.00', '23345.31 40',
     'BZXVZ,$+2.0           p.89 prints "2.0", p.88 "2.00" -- see the header'),
    ('023343.40', '23345.30 40',
     'BZXCZ,$+1.32          -> 023345.00'),
    ('023344.00', '1310.00 80',
     'SIC,SEN              (ext) "-EX IN MAIN TO EX IN IX TO LX IN"'),
    ('023344.40', '1304.10 00',
     'B,SERS               (ext) "-MAIN, FAILS, LX NOT EXECUTED."'),

    # ---- 5. MAIN TO INTERNAL TO MAIN --------------------------------
    ('023345.00', '24322.02 10',
     'LX,$X1,I62EX         (ext) "-MAIN TO INTERNAL TO MAIN."'),
    ('023345.40', '24321.03 10',
     'SX,$X1,I62EXT        (ext)'),
    ('023346.00', '24173.04 10',
     'LX,$X2,I62K2         (ext) the same doubled "EX,I62EXT"'),
    ('023346.40', '11.05 10',
     'SX,$X2,$R             ...but the middle level goes to word 9'),
    ('023347.00', '23351.07 01',
     'LVI,$X3,I629         bit 18 = 0 -> 023351.00; field 07'),
    ('023347.40', '24320.07 D0',
     'SVA,$X3,I62ITE       (ext)'),
    ('023350.00', '21.22 00',
     'Z,$X1'),
    ('023350.40', '11.12 00',
     'EX,$R                 EX in main -> EX in INT -> LX in main'),
    ('023351.00', '21.02 10',
     'I629 LX,$X1,$X1'),
    ('023351.40', '23353.71 40',
     'BZXVZ,$+2.0           bit 18 = 1 -> 023353.40'),
    ('023352.00', '23353.70 40',
     'BZXCZ,$+1.32          -> 023353.40'),
    ('023352.40', '1310.00 80',
     'SIC,SEN              (ext) "-EX IN MAIN TO EX IN INT TO LX IN"'),
    ('023353.00', '1304.10 00',
     'B,SERS               (ext) "-MAIN FAILS, LX NOT EXECUTED."  (no comma)'),

    # ---- 6. MAIN TO IX TO IX ----------------------------------------
    ('023353.40', '24174.04 10',
     'LX,$X2,I62K3         (ext) "-MAIN TO IX TO IX."; "EX,$X3" twice'),
    ('023354.00', '24322.06 10',
     'LX,$X3,I62EX         (ext) field 06 = $X3 load'),
    ('023354.40', '23356.43 01',
     'LVI,$X1,I6210        bit 18 = 1 -> 023356.40; back to field 03'),
    ('023355.00', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext)'),
    ('023355.40', '21.22 00',
     'Z,$X1'),
    ('023356.00', '22.12 00',
     'EX,$X2                BOTH levels in index storage'),
    ('023356.40', '21.02 10',
     'I6210 LX,$X1,$X1'),
    ('023357.00', '23361.31 40',
     'BZXVZ,$+2.0           bit 18 = 0 -> 023361.00'),
    ('023357.40', '23361.30 40',
     'BZXCZ,$+1.32          -> 023361.00'),
    ('023360.00', '1310.00 80',
     'SIC,SEN              (ext) "-EX IN MAIN TO EX IN IX TO LX IN IX"'),
    ('023360.40', '1304.10 00',
     'B,SERS               (ext) "-FAILS, LX NOT EXECUTED."'),

    # ---- 7. MAIN TO INT TO INT --------------------------------------
    ('023361.00', '24175.02 10',
     'LX,$X1,I62K4         (ext) "-MAIN TO INT TO INT."; "EX,$L" twice'),
    ('023361.40', '11.03 10',
     'SX,$X1,$R             the middle level into word 9'),
    ('023362.00', '24322.02 10',
     'LX,$X1,I62EX         (ext)'),
    ('023362.40', '10.03 10',
     'SX,$X1,$L             ...and the LX into word 8'),
    ('023363.00', '23365.03 01',
     'LVI,$X1,I6211        bit 18 = 0 -> 023365.00'),
    ('023363.40', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext) the eighth and last bare-I62ITE SVA'),
    ('023364.00', '21.22 00',
     'Z,$X1'),
    ('023364.40', '11.12 00',
     'EX,$R                 BOTH levels in internal registers'),
    ('023365.00', '21.02 10',
     'I6211 LX,$X1,$X1'),
    ('023365.40', '23367.71 40',
     'BZXVZ,$+2.0           bit 18 = 1 -> 023367.40'),
    ('023366.00', '23367.70 40',
     'BZXCZ,$+1.32          -> 023367.40'),
    ('023366.40', '1310.00 80',
     'SIC,SEN              (ext) "-EX IN MAIN TO EX IN INT TO LX IN"'),
    ('023367.00', '1304.10 00',
     'B,SERS               (ext) "-INT FAILS, LX NOT EXECUTED."'),

    # ---- exit and continuity ----------------------------------------
    ('023367.40', '23370.50 00',
     'B,$+1.0               self-relative: +1 word -> 023370.40'),
    ('023370.00', '23310.04 00',
     'BD,I621               the loop back; bit 18 = 0 -> 023310.00'),
    ('023370.40', '1311.40 80',
     'SIC,SEN0+.32         (ext) SEN0 + 32 bits -> bit 32 of word 0o1311'),
    ('023371.00', '1301.10 00',
     'B,SSW                (ext) "-TO SSIP" (no period; p.110 has one)'),
    ('023371.40', '23372.04 00',
     'BD,$+.32              self-relative: +32 bits -> 023372.00'),
    ('023372.00', '24171.32 10',
     'LX,$X13,IC262        (ext) "-UPDATE CONTINUITY CHECK."'),
    ('023372.40', '24522.32 B0',
     'V+,$X13,BIT0         (ext) bit 18 = 0 -> 024522.00'),
    ('023373.00', '24171.33 10',
     'SX,$X13,IC262        (ext) the last row before TEST 1B\'s 023373.40'),
]

# I62 and I621 are SLC ANCHORS -- each is the first label after an SLC,
# so asserting it checks this transcription against the number it handed
# the SLC.  The other ten are the evidence: defined inside the range and
# named by an in-range operand whose printed pair is decoded above.
SYMBOLS = {'I62': '023304.00', 'I621': '023310.00',
           'I622': '023314.00', 'I623': '023315.00',
           'I624': '023316.40', 'I625': '023321.40',
           'I626': '023327.00', 'I627': '023334.40',
           'I628': '023342.40', 'I629': '023351.00',
           'I6210': '023356.40', 'I6211': '023365.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 1A '))
