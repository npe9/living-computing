#!/usr/bin/env python3
"""verify_ax5b_162_test1cc_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), TEST 1CC (programs/ax5b_162_test1cc.strap) against
the listing's printed machine code, PDF pp.93-94, octal
023474.40-023545.40.  81 SOURCE ROWS over 83 half-words (the two BB
rows are full words), entry label I6225.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

WHERE THIS WAS CUT.  TEST 1CC is 023460.40-023545.40, 105 half-words
over PDF pp.92-94.  The cut is at 023474.40 = label I6225, the deck's
own "-DO BE AND BD." seam, which p.92 enters by "BD,I6225" at
023473.00.  Left behind: 1CC's first subject class, EX of a BIND
instruction, error entries I6221-I6224 (023460.40-023474.00).  Taken:
BE, BD and BB.  The far end is 1CC's own exit label I6240, the target
of five branches inside the range; p.94's rows after it are 1262's
shared exit tail.

WHAT THIS BLOCK IS.  It is the executable form of Reference Manual
printed p.49 (PDF p.52) on EXECUTE: "the subject instruction is not
allowed to change the state of the interruption system or replace the
contents of the instruction counter.  The execution exception indicator
(EXE) is turned on by any branch operation of a subject instruction in
which the condition for a successful branch is met.  When indicator EXE
is actuated, the branch and all associated operations are not
performed.  The suppressed actions include the disabling in BRANCH
DISABLED, the enabling in BRANCH ENABLED or BRANCH ENABLED AND WAIT,
the counting and refilling in COUNT, BRANCH AND REFILL, and so on."

FOURTEEN error messages, not twelve.  I6238 and I6239 are easy to miss
because they belong to the subject whose branch condition is NOT met
and so read like near-duplicates of I6237.  All fourteen are quoted
verbatim in the program file's header, punctuation included -- it is
inconsistent on the page ("-EXECUTED,BRANCH EXECUTED." at I6226 against
"-EXECUTED, BRANCH EXECUTED." at I6231) and is transcribed, not tidied.

I6237 AT 023541.40 IS THE INVERTED ONE: "-INT TAKEN WHEN EX BB, COND
FOR / -BRANCH NOT MET, NO BRANCH."  No leading "NO", and correctly so.
I6237's address is planted into the interrupt landing before
"EX,I62B6" runs, so I6237 is reached ONLY via the interrupt vector;
I62B6's branch condition is not met, so EXE must not come on and no
interruption must occur.  Arriving there IS the failure.

THE INTERRUPT VECTOR IS THE INSTRUMENT, and PDF p.109's constants area
for 1262 supplies it in its own LABEL column, read at 600 dpi:
"I62K1 BD,I62ITE" (24320.04 00) at 024172.00, "I62K6 B,I62ITE+.32"
(24320.50 00) at 024177.00, "I62INT DR%BU,64,8@,64 -INTRPT TABLE." at
024220.00, "I62ITE BD,$" at 024320.00 with "B,$" at 024320.40, and
"I62XW1 XW,0,64,I62INT" at 024326.00.  I62K1 and I62K6 are each a full
WORD holding the same half-word branch twice.  I62XW1 decodes (against
the XW rows on pp.113-114, not from operand order) as VALUE 0, COUNT 64
(bit 39; the count field is bits 28-45) and REFILL I62INT (bits 46-63 =
10384 = 0o24220) -- so the walk starts at zero and CB+ steps it, the
I62INT base coming from the SX's own address field.  So "LX,$X1,I62XW1
/ LX,$X2,I62Kn / SX,$X2,I62INT%$X1@ / CB+,$X1,$-.32" is a LOOP filling
all 64 table words, not a single write to I62ITE.  Which HALF of the I62ITE pair an interruption lands
on is what the constant chooses -- I62K6 lands on 024320.40 with the
system untouched, I62K1 on 024320.00 with the system disabled -- and
the test plants its handler in the matching half with SVA (which
rewrites only the address part, so the landing keeps its own B or BD).
The pairing holds with no exception: I6225's loop takes I62K6 and every
SVA through 023520.00 names I62ITE+.32; I6233's loop takes I62K1 and
both SVAs after it name I62ITE.

AND IT EXPLAINS THE "-ILLEGAL OP." ROW that verify_ax5b_162_test3a_
listing.py had to leave unexplained.  00000003740 in the straight-line
path is a PROBE FOR THE ENABLE STATE.  At I6227 the subject was
"BE,I6226", so the enabling must have been suppressed and the probe
must NOT interrupt -- falling past it to "BD,I6229" is correct and an
interruption reports "-SYSTEM ENABLED AFTER EX OF / -A BE INSTRUCTION."
At I6232 a real "BE,$+.32" enabled the system first and the subject was
"BD,I6231", so the disabling must have been suppressed and the probe
MUST interrupt -- falling past it reports "-SYSTEM DISABLED AFTER EX OF
/ -A BD INSTRUCTION."  Opposite directions, same word.

ONE ROW IS STILL NOT EXPLAINED.  023510.00's "LX,$X1,I62XW1" carries
"-SETUP B,I62ITE+.32 INT TABLE" but its stanza has no store loop, and
the next row overwrites the value it loaded.  The comment is true of
the machine state (I6225's loop left the table that way) while the LX
does no work.  Recorded the way ax5b_16082_op_ad.strap records what it
could not trace; the row's ENCODING is settled regardless.

NO MNEMONIC HERE IS A FIRST, and that was checked by grep rather than
assumed: BE is witnessed by verify_ax1a_bew_listing.py and four jb_ax5b
files, CB+ by verify_ibox4_listing.py and verify_ax5b_160_test8b_
listing.py, BB by verify_fp_arith_f206a_listing.py ("BB,ROS+.60,$+2.0"
at 013574.40).  What the block does add: EX four times, more than the
rest of the repo together; the first BB whose bit operand is an INDEX
REGISTER ($X0, $X0+.01) rather than a core word; the first EX subject
at a .40 half-word; and both of listing_oracle.word_at()'s full-word
paths in one block, since 023524.40 is an ODD half-word whose
instruction straddles two words and 023527.00 is not.

EXTERNALS ARE INPUTS, NOT WITNESSES -- the caveat verify_ax5b_16082_
16083_listing.py makes about I6088.  Every SYN in the program file
makes an address field come out right by construction, so rows naming
one prove only that every OTHER field lands where the listing puts it.
Two tiers of corroboration exist and neither converts an input into a
witness: I62INT/I62ITE/I62K1/I62K6/I62XW1/I62B3-I62B6 and BIT0 are
confirmed by separately read pages' own label columns (pp.109 and 114),
while SEN/SERS/I60SX1/I60S1 rest on other verify files in this repo
(verify_ax5b_16087_listing.py gives I60SX1 = 023041.00 and I60S1 =
022741.00).

THE GENUINE ADDRESS EVIDENCE is unusually thick here -- fifteen labels
defined inside the range (I6226 through I6240), sixteen rows whose
operand is one of them, and eight self-relative rows.  I6225 is
deliberately NOT counted: the SLC sets the counter to 023474.40 and
I6225 is the first label after it, so that check tests the SLC against
the number this transcription handed the SLC.  It is asserted below as
the anchor; it is not evidence.

BIT-18 SELF-CHECKS, decoded out of the printed octal pair and matched
against the page's own label column (bit 18 is the TOP bit of the pair):

  023510.40  "LVI,$X1,I6232" -> 23517.43 01.  Pair 43 = 100011, bit 18
             = 1 -> 023517.40, which is where p.93 prints I6232.
  023516.00  "B,I6232"       -> 23517.50 00.  Pair 50 = 101000, bit 18
             = 1 -> 023517.40, the same label.  Note the low bits: B is
             0o10 and BD is 0o04 in this field, and bit 18 adds 0o40 --
             so "BD,I6227" at 023503.40 prints 04 (bit 18 = 0 ->
             023505.00) and "B,I6240" prints 50.
  023541.00  "B,I6240"       -> 23545.50 00.  Bit 18 = 1 -> 023545.40 =
             I6240, the last row of the transcribed range.
  023540.40  "EX,I62B6"      -> 24205.52 00.  Pair 52 = 101010, bit 18
             = 1 -> 024205.40.  This is the ONLY EX in 1CC whose
             subject is at a .40 half-word, and p.109 says why: I62B5's
             "BB,$X0,I6234" is a full word at 024204.00-024204.40 and
             its "B,I6235" takes 024205.00, so I62B6 begins at
             024205.40.  Every other EX here prints pair 12.
  023476.00  "CB+,$X1,$-.32" -> 23475.43 48.  Bit 18 = 1 -> 023475.40,
             which is 023476.00 minus 32 bits -- the top of the
             table-fill loop.  Its twin at 023523.40 prints 23523.03,
             bit 18 = 0 -> 023523.00, again exactly 32 bits back.
  023524.40  "BB,$X0,$+2.32" -> 20.00 80 023527.34 02.  In the SECOND
             printed group the branch address A occupies bits 32-50, so
             bit 50 is the top bit of pair 34 = 011100: 0, giving
             023527.00.  And 023524.40 + 2 words + 32 bits = 192 bits =
             3 whole words -> 023527.00.  The rest of that group is the
             format's own literal: bits 51-59 read 111000000, bits
             60-61 = 00 (tested bit left unchanged), bit 62 = 1 (branch
             on a ONE bit, i.e. BB and not BZB).  In the FIRST group
             "20.00" is the 24-bit bit address -- word 0o20 = 16 = $X0
             -- and 0x80's high nibble is the literal 1000 at bits
             24-27.
  023527.00  "BB,$X0+.01,$+1.32" -> 20.01 80 023530.74 02.  Bit address
             20.01 = word 16 bit 1.  Pair 74 = 111100 so bit 50 = 1 ->
             023530.40, and 023527.00 + 1 word + 32 bits = 96 bits ->
             023530.40, the "-BB,BIT 1 IS 0, FAILS" entry: the branch is
             taken only if the bit is wrongly set.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted -- each
injection was made with __pycache__ cleared on BOTH sides of the run:

  UNCOND_BRANCH_CODES["BE"] 0b000 -> 0b101
      023514.00  BE,$+.32 -> "023514.64 00"                 (1 row)
      The cleanest possible isolation this repo has: BE occurs exactly
      once in the block and nothing else moves.  Note the whole change
      lands in the OCTAL pair (40 -> 64), because the 3-bit code field
      sits beside bit 18.
  BB_CODES["BB"] (0b00, 1) -> (0b01, 1)
      023524.40  -> "000020.00 80 023527.34 06"             (2 rows)
      023527.00  -> "000020.01 80 023530.74 06"
      Both full-word rows, and only the LAST hex byte moves (02 -> 06),
      because the mod field sits at bits 60-61.  One of the two
      straddles a word boundary and one does not, so this also
      exercises both of listing_oracle.word_at()'s paths.
  MISC_CODES["EX"] 0b010 -> 0b110
      023502.00  EX,I62B3 -> "024202.32 00"                (4 rows)
      023514.40  EX,I62B4 -> "024203.32 00"
      023533.00  EX,I62B5 -> "024204.32 00"
      023540.40  EX,I62B6 -> "024205.72 00"
      The fourth is the .40-half-word subject: pair 52 -> 72, i.e. the
      code field moved while bit 18 stayed 1.
  CB_CODES["CB+"] (0b10, 0, 0) -> (0b10, 1, 0)
      023476.00  CB+ -> "023475.43 4C"                      (2 rows)
      023523.40  CB+ -> "023523.03 4C"
      The refill bit, which nothing else in this block exercises, and
      it shows only in the hex byte (48 -> 4C).
  DIR_INDEX_CODES["SX"] 0b10001 -> 0b11001
      023475.40  SX,$X2,I62INT($X1) -> "024220.05 91"      (2 rows)
      023523.00  SX,$X2,I62INT($X1) -> "024220.05 91"
      The two indexed table stores; no other SX appears in the range.
      Only the hex byte moves (11 -> 91), so the index digit 1 in its
      low nibble is being checked independently of the opcode.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_test1cc.strap").read())

ROWS = [
    # ---- BE: fill all 64 interrupt-table words with "B,I62ITE+.32" --
    ('023474.40', '24326.02 10',
     'I6225 LX,$X1,I62XW1 (ext) "-DO BE AND BD."  count 64'),
    ('023475.00', '24177.04 10',
     'LX,$X2,I62K6        (ext) the word "B,I62ITE+.32" twice'),
    ('023475.40', '24220.05 11',
     'SX,$X2,I62INT($X1)  (ext) index-modified store; idx 1 in bits 28-31'),
    ('023476.00', '23475.43 48',
     'CB+,$X1,$-.32        self-relative: -32 bits -> 023475.40'),
    ('023476.40', '23477.04 00',
     'BD,$+.32             self-relative: +32 bits -> 023477.00'),
    ('023477.00', '23505.03 01',
     'LVI,$X1,I6227       in-range label; bit 18 = 0 -> 023505.00'),
    ('023477.40', '24320.43 D0',
     'SVA,$X1,I62ITE+.32  (ext) plant in the half I62K6 lands on'),
    ('023500.00', '23041.00 80',
     'SIC,I60SX1          (ext)'),
    ('023500.40', '22741.04 00',
     'BD,I60S1            (ext) clear indicators 0-19'),
    ('023501.00', '13.22 00',
     'Z,$IND'),
    ('023501.40', '14.22 00',
     'Z,$MASK'),
    ('023502.00', '24202.12 00',
     'EX,I62B3            (ext) THE TEST: EX of "BE,I6226"'),
    ('023502.40', '1310.00 80',
     'SIC,SEN              (ext) "-NO INT TAKEN WHEN BE"'),
    ('023503.00', '1304.10 00',
     'B,SERS               (ext) "-INSTR EXECUTED, BRANCH NOT EXECUTED."'),
    ('023503.40', '23505.04 00',
     'BD,I6227            in-range label; bit 18 = 0 -> 023505.00'),
    ('023504.00', '1310.00 80',
     'I6226 SIC,SEN       (ext) "-NO INT TAKEN WHEN BE INSTR"'),
    ('023504.40', '1304.10 00',
     'B,SERS               (ext) "-EXECUTED,BRANCH EXECUTED."'),
    # ---- I6227: was the ENABLING suppressed? ------------------------
    ('023505.00', '23507.03 01',
     'I6227 LVI,$X1,I6228   in-range label -> 023507.00'),
    ('023505.40', '24320.43 D0',
     'SVA,$X1,I62ITE+.32  (ext) the probe\'s handler'),
    ('023506.00', '00000003740',
     'DD(BU,32,8),(8)3740  "-ILLEGAL OP CODE." -- the enable-state probe'),
    ('023506.40', '23510.04 00',
     'BD,I6229            in-range label -> 023510.00 (the CORRECT path)'),
    ('023507.00', '1310.00 80',
     'I6228 SIC,SEN       (ext) "-SYSTEM ENABLED AFTER EX OF"'),
    ('023507.40', '1304.04 00',
     'BD,SERS              (ext) "-A BE INSTRUCTION."'),
    # ---- BD: table unchanged; see the docstring on this LX ----------
    ('023510.00', '24326.02 10',
     'I6229 LX,$X1,I62XW1   (ext) "-SETUP B,I62ITE+.32 INT TABLE"'),
    ('023510.40', '23517.43 01',
     'LVI,$X1,I6232       in-range; bit 18 = 1 -> 023517.40'),
    ('023511.00', '24320.43 D0',
     'SVA,$X1,I62ITE+.32  (ext)'),
    ('023511.40', '23041.00 80',
     'SIC,I60SX1          (ext)'),
    ('023512.00', '22741.10 00',
     'B,I60S1             (ext) clear indicators 0-19 (B here, BD above)'),
    ('023512.40', '13.22 00',
     'Z,$IND'),
    ('023513.00', '14.22 00',
     'Z,$MASK'),
    ('023513.40', '3.22 00',
     'Z,3.0                clear the boundary register'),
    ('023514.00', '23514.40 00',
     'BE,$+.32             the block\'s only BE: enable for real'),
    ('023514.40', '24203.12 00',
     'EX,I62B4            (ext) THE TEST: EX of "BD,I6231"'),
    ('023515.00', '1310.00 80',
     'I6230 SIC,SEN       (ext) "-NO INT TAKEN WHEN BD INSTR"'),
    ('023515.40', '1304.10 00',
     'B,SERS               (ext) "-EXECUTED, BRANCH NOT EXECUTED."'),
    ('023516.00', '23517.50 00',
     'B,I6232             in-range; bit 18 = 1 -> 023517.40'),
    ('023516.40', '1310.00 80',
     'I6231 SIC,SEN       (ext) "-NO INT TAKEN WHEN BD INSTR"'),
    ('023517.00', '1304.10 00',
     'B,SERS               (ext) "-EXECUTED, BRANCH EXECUTED."'),
    # ---- I6232: was the DISABLING suppressed?  same probe, inverted -
    ('023517.40', '23522.03 01',
     'I6232 LVI,$X1,I6233   in-range -> 023522.00'),
    ('023520.00', '24320.43 D0',
     'SVA,$X1,I62ITE+.32  (ext)'),
    ('023520.40', '00000003740',
     'DD(BU,32,8),(8)3740  "-ILLEGAL OP CODE."  here it MUST interrupt'),
    ('023521.00', '1310.00 80',
     'SIC,SEN              (ext) "-SYSTEM DISABLED AFTER EX OF"'),
    ('023521.40', '1304.04 00',
     'BD,SERS              (ext) "-A BD INSTRUCTION."'),
    # ---- BB: refill all 64 entries with "BD,I62ITE" -----------------
    ('023522.00', '24326.02 10',
     'I6233 LX,$X1,I62XW1   (ext) "-DO BB, SETUP BD INT TBL."'),
    ('023522.40', '24172.04 10',
     'LX,$X2,I62K1        (ext) the word "BD,I62ITE" twice'),
    ('023523.00', '24220.05 11',
     'SX,$X2,I62INT($X1)  (ext)'),
    ('023523.40', '23523.03 48',
     'CB+,$X1,$-.32        self-relative: -32 bits -> 023523.00'),
    # ---- pre-flight: does a PLAIN BB work? --------------------------
    ('023524.00', '24522.00 10',
     'LX,$X0,BIT0          (ext) p.114: XW,%8@400000.00,0,0'),
    ('023524.40', '20.00 80 023527.34 02',
     'BB,$X0,$+2.32        FULL WORD at an ODD half-word: it straddles'),
    ('023525.40', '1310.00 80',
     'SIC,SEN              (ext) "-BB BIT 0 FAILS, UNABLE TO EX SAME."'),
    ('023526.00', '1304.10 00',
     'B,SERS               (ext) "-TERM THIS TEST."'),
    ('023526.40', '23545.50 00',
     'B,I6240             in-range; bit 18 = 1 -> 023545.40'),
    ('023527.00', '20.01 80 023530.74 02',
     'BB,$X0+.01,$+1.32    FULL WORD, word-aligned; bit 1 of $X0'),
    ('023530.00', '23532.04 00',
     'BD,$+2.0             self-relative: +2 words -> 023532.00'),
    ('023530.40', '1310.00 80',
     'SIC,SEN              (ext) "-BB,BIT 1 IS 0, FAILS, UNABLE"'),
    ('023531.00', '1304.10 00',
     'B,SERS               (ext) "-TO EXECUTE SAME, TERM THIS TEST."'),
    ('023531.40', '23545.50 00',
     'B,I6240             in-range -> 023545.40'),
    # ---- EX of a BB whose branch condition IS met -------------------
    ('023532.00', '23537.43 01',
     'LVI,$X1,I6236       in-range; bit 18 = 1 -> 023537.40'),
    ('023532.40', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) NOTE: no "+.32" from here on'),
    ('023533.00', '24204.12 00',
     'EX,I62B5            (ext) THE TEST: EX of "BB,$X0,I6234"'),
    ('023533.40', '1310.00 80',
     'SIC,SEN              (ext) "-NO INT WHEN EX BB,COND"'),
    ('023534.00', '1304.10 00',
     'B,SERS               (ext) "-FOR BRANCH MET, BRANCH NOT TAKEN."'),
    ('023534.40', '23537.50 00',
     'B,I6236             in-range -> 023537.40'),
    ('023535.00', '1310.00 80',
     'I6234 SIC,SEN       (ext) "-NO INT WHEN EX BB, COND FOR"'),
    ('023535.40', '1304.10 00',
     'B,SERS               (ext) "-BRANCH MET, BRANCH TAKEN."'),
    ('023536.00', '23537.50 00',
     'B,I6236             in-range -> 023537.40'),
    ('023536.40', '1310.00 80',
     'I6235 SIC,SEN       (ext) "-NO INT WHEN EX BB, COND FOR BRANCH"'),
    ('023537.00', '1304.10 00',
     'B,SERS               (ext) "-MET, NO BRANCH, CONTROL GIVEN TO NEXT"'),
    # ---- EX of a BB whose branch condition is NOT met ---------------
    ('023537.40', '23541.43 01',
     'I6236 LVI,$X1,I6237   in-range; bit 18 = 1 -> 023541.40'),
    ('023540.00', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext)'),
    ('023540.40', '24205.52 00',
     'EX,I62B6            (ext) bit 18 = 1 -> 024205.40, the odd one'),
    ('023541.00', '23545.50 00',
     'B,I6240             the ONLY correct outcome of the I62B6 test'),
    ('023541.40', '1310.00 80',
     'I6237 SIC,SEN       (ext) "-INT TAKEN WHEN EX BB, COND FOR"'),
    ('023542.00', '1304.10 00',
     'B,SERS               (ext) "-BRANCH NOT MET, NO BRANCH."'),
    ('023542.40', '23545.50 00',
     'B,I6240             in-range -> 023545.40'),
    ('023543.00', '1310.00 80',
     'I6238 SIC,SEN       (ext) "-NO INT TAKEN WHEN EX BB, COND FOR"'),
    ('023543.40', '1304.10 00',
     'B,SERS               (ext) "-BRANCH NOT MET, BRANCH TAKEN."'),
    ('023544.00', '23545.50 00',
     'B,I6240             in-range -> 023545.40'),
    ('023544.40', '1310.00 80',
     'I6239 SIC,SEN       (ext) "-NO INT TAKEN WHEN EX BB,COND FOR"'),
    ('023545.00', '1304.10 00',
     'B,SERS               (ext) "-BRANCH NOT MET, NO BRANCH, CONTROL"'),
    ('023545.40', '23546.50 00',
     'I6240 B,$+1.0       1CC\'s exit; +1 word -> 023546.40'),
]

# Only labels DEFINED inside the transcribed range belong here; a SYN'd
# external would be checking this file against itself.  Of these,
# I6226..I6240 are evidence; I6225 is the SLC anchor -- see the
# docstring.
SYMBOLS = {
    'I6225': '023474.40',
    'I6226': '023504.00',
    'I6227': '023505.00',
    'I6228': '023507.00',
    'I6229': '023510.00',
    'I6230': '023515.00',
    'I6231': '023516.40',
    'I6232': '023517.40',
    'I6233': '023522.00',
    'I6234': '023535.00',
    'I6235': '023536.40',
    'I6236': '023537.40',
    'I6237': '023541.40',
    'I6238': '023543.00',
    'I6239': '023544.40',
    'I6240': '023545.40',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 1CC '))
