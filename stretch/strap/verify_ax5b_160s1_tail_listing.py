#!/usr/bin/env python3
"""verify_ax5b_160s1_tail_listing.py -- jb_ax5b "I-Box 5",
routine 1260's I60S1, THE TAIL (programs/ax5b_160s1_tail.strap)
against the listing's printed machine code, PDF p.85, octal
023021.40-023041.00.  27 printed rows, 32 half-words.

THE HEAD of the same subroutine, 022741.00-023021.00 (PDF pp.83-84),
is checked by verify_ax5b_160s1_listing.py and is NOT repeated here.
Together the two cover I60S1 whole.  They are separate files only
because the head is committed and this work had to leave the tree's
diff empty apart from new files.

CITED BY PDF PAGE.  jb_ax5b's listing pages carry no printed page
numbers; the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering.  Every verify_ax5b_*.py here says
"PDF p.NN" for that reason.

WHY THE LAST TWO ROWS MATTER.  I60S1 is the subroutine every 1260 and
1262 test block calls as "SIC,I60SX1 / B,I60S1".  Its RETURN had never
been read:

    023040.40         LX,$X1,I60DMP       23301.02 10
    023041.00  I60SX1 $BD,0               0.04 00

a BRANCH DISABLED whose address field the caller's SIC plants.
Reference Manual printed p.41 (PDF p.44), "Store Instruction Counter
If (SIC)": it "causes the instruction counter contents to be stored in
bits 0-18 of the half-word specified by bits 0-18 of the effective
storage address.  OTHER BITS OF THE HALF-WORD ARE NOT DISTURBED."
Reference Manual printed p.40 (PDF p.43): "Branch Disabled (BD).  This
operation disables the interruption mechanism, and then performs the
same operation as BRANCH."  So I60S1 RETURNS DISABLED, and neither
half of the subroutine contains a BE.

THAT RESOLVES 1262 TEST 3B (PDF p.108), whose straight-line path is
"SIC,I60SX1 / B,I60S1 ... Z,$X1 / DD 3740 'ILLEGAL OP' / EXIC,I62PSI"
with an INTERRUPTION as the OK path out of the EXIC.  Ref. Manual
printed p.50 (PDF p.53): "at the completion, termination, or
suppression of an execution operation, interruption is always
permitted", with the PROGRAMMING NOTE "When interruption occurs
following an execution operation with the interruption system
DISABLED, it is caused only by the actuated indicator of highest
priority whose mask bit is one."  The block is disabled from the
moment I60S1 returns, and the interruption happens anyway.

AND THE DD IS LOAD-BEARING.  p.48: the interruption "develops the
number of the leftmost actuated indicator whose mask bit is one.
After this leftmost indicator has been TURNED OFF, the developed
number is added to the contents of the interruption address register".
The EXIC actuates AD (16).  With no DD, AD would be leftmost, the
interruption would consume it, and "BADZ,$+1.32" at the landing would
find AD off and report "-AD NOT SET WHEN SUBJ INST OF EXIC LESS THAN
32." falsely.  The DD actuates OP (15), which outranks AD; OP is
consumed and AD survives.  p.50: "Examination for other actuated
indicators can be programmed into the correction routine."

The rows below are the other half of that argument: the BOPZ rung at
023021.40 and the BADZ rung at 023024.40 are I60S1 CLEARING indicators
15 and 16, so both are provably off when a caller reaches its DD.

ONE ROW IS NOT LIKE THE OTHER FOURTEEN.  023037.00 is "KV,$X1,BIT19",
a DIRECT index compare against a stored constant, where all fourteen
other rungs in the subroutine use the IMMEDIATE form KVI: DS is
indicator 19 and its bit sits below the 19-bit immediate field.  It is
I60S1's only KV, and the only row in this repo that separates KV
(DIR_INDEX_CODES 0b01001) from KVI (IMM_INDEX_CODES 0b0100).

ERROR TEXT, verbatim from the page at 400 dpi:
    023024.00  "-UNABLE OT CLR OP OR ABOVE IND."    <- "OT" is the
               listing's own typo, kept (compare "PSEDUO" in
               verify_ax5b_162_test3a_listing.py)
    023027.00  "-UNABLE TO CLR AD OR ABOVE IND."
    023032.00  "-UNABLE TO CLR USA OR ABOVE IND."
    023035.00  "-UNABLE TO CLR EXE OR ABOVE IND."
    023040.00  "-UNABLE TO CLR DS OR ABOVE IND."

WITNESS TIERING.  Every SYN in the program file -- I60DMP, SEN, SERS,
BIT19 -- is an INPUT to this check, not a witness: a SYN makes the
address field come out right by construction, so a row naming one
proves only that every OTHER field lands where the listing puts it.
The genuine address evidence is:

  * the FIVE self-relative "$+.32" rows, which no SYN touches, and
  * I60SX1 at 023041.00, which is not the first label after the SLC
    (023021.40 is) but the last, so its address falls out of the
    cumulative sizing of the 25 half-words before it -- including the
    five TI rows that are FULL words at ODD half-words.

BIT-18 SELF-CHECKS, decoded from the printed octal pair (bit 18 is the
TOP bit of the two octal digits) and read back against the page:

  023021.40  BOPZ,$+.32  -> 23022.07 C6.  Pair 07 = 000111, bit 18 = 0
             -> 023022.00.  023021.40 + 32 bits = 023022.00, the
             TI row.  Same shape at
  023024.40  BADZ,$+.32  -> 23025.10 46.  Pair 10 = 001000, bit 18 = 0
             -> 023025.00.
  023027.40  BUSAZ,$+.32 -> 23030.10 C6.  Pair 10, bit 18 = 0 ->
             023030.00.
  023032.40  BEXEZ,$+.32 -> 23033.11 46.  Pair 11 = 001001, bit 18 = 0
             -> 023033.00.
  023035.40  BDSZ,$+.32  -> 23036.11 C6.  Pair 11, bit 18 = 0 ->
             023036.00.
             All five land on the .00 half that follows, which is
             where the page prints the next TI.
  023037.00  KV,$X1,BIT19 -> 24545.02 90.  Pair 02 = 000010, bit 18 =
             0 -> 024545.00 (external; the SYN is an input).
  023040.40  LX,$X1,I60DMP -> 23301.02 10.  Pair 02, bit 18 = 0 ->
             023301.00, which is where pp.83/85 print I60DMP.
  023041.00  BD,0         -> 0.04 00.  Pair 04 = 000100, bit 18 = 0,
             address 0 -- the empty address field the caller's SIC
             fills in, bits 0-18, "other bits of the half-word are not
             disturbed" (printed p.41).  This is the row the whole
             argument above rests on.

A MEASURED NULL.  The five TI rows print "13.00 80 000021.02 A0",
identical to the fifteen in the head.  Their A1, the indicator
register, is word 11 = 0o13 and prints as a 24-BIT bit address; their
A2 is $X1 = word 17 = 0o21 and prints as a 19-bit half-word address.
Nothing in this block varies them, so they are not evidence of field
width here -- they are evidence that a FULL word at an ODD half-word
is deposited straddling two words (Ref. Manual p.39), which is what
puts I60SX1 at 023041.00 rather than 023037.00.

SUBSTITUTIONS: three, all in the program file's header.  The third is
load-bearing and is recorded rather than smoothed away: the listing
prints the return row as "$BD,0" and the transcription writes "BD,0".
The 32 bits are IDENTICAL -- both produce the printed "0.04 00",
measured below, not assumed -- but what STRAP's "$" prefix on an
operation means is not established by any page read for this work.  It
appears only on data-in-the-instruction-stream rows (I60SX1 here;
I62BR1 and I62BR2 on PDF p.109) and is left as an open question.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted; each
injection was made with __pycache__ removed on BOTH sides of the run
(stale bytecode has replayed a previous injection's answer in this
project):

  UNCOND_BRANCH_CODES["BD"] 0b001 -> 0b010
      023041.00  BD,0 -> "000000.10 00"                     (1 row)
      The row that carries the resolution.  Nothing else in the
      block is an unconditional branch.
  INDICATOR_BITS["OP"] 15 -> 14
      023021.40  BOPZ,$+.32 -> "023022.07 46"               (1 row)
      Note WHERE it shows: the octal pair is UNCHANGED and only the
      hex byte moves (C6 -> 46), because 14 and 15 differ solely in
      the bit that lands at 24.  A check reading only the octal field
      would miss it.
  DIR_INDEX_CODES["KV"] 0b01001 -> 0b01011  (= LVE)
      023037.00  KV,$X1,BIT19 -> "024545.02 B0"             (1 row)
      The block's only KV, and what separates it from the KVIs.
  enc_branch_ind drops the `clear` bit (clear -> 0)
      023021.40, 023024.40, 023027.40, 023032.40, 023035.40
                                                            (5 rows)
      FIVE, not ten, and the five it misses are the finding: the
      BZXL,SERS rows are NOT affected, because a branch on an INDEX
      indicator goes through a different encoder in strap_asm.py than
      enc_branch_ind.  The five that fail are exactly the block's
      branch-on-INDICATOR rows, all of which carry the trailing Z.
  IMM_INDEX_CODES["KVI"] 0b0100 -> 0b0101  (= V+I)
      023023.00, 023026.00, 023031.00, 023034.00            (4 rows)
      Four of the five rungs; 023037.00's KV is untouched, which is
      the point of that row.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_160s1_tail.strap").read())

ROWS = [
    # ---- OP, indicator 15 -------------------------------------------
    ('023021.40', '23022.07 C6',
     'BOPZ,$+.32            self-relative; bit 18 -> 023022.00'),
    ('023022.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1         indicators -> $X1 (full word, odd half)'),
    ('023023.00', '4.03 04',
     'KVI,$X1,(8)4.0        OP'),
    ('023023.40', '1310.00 80',
     'SIC,SEN               (ext) "-UNABLE OT CLR OP OR ABOVE IND."'),
    ('023024.00', '1304.32 40',
     'BZXL,SERS             (ext) the listing\'s own "OT" typo'),
    # ---- AD, indicator 16 -------------------------------------------
    ('023024.40', '23025.10 46',
     'BADZ,$+.32            self-relative; bit 18 -> 023025.00'),
    ('023025.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023026.00', '2.03 04',
     'KVI,$X1,2.0           AD'),
    ('023026.40', '1310.00 80',
     'SIC,SEN               (ext) "-UNABLE TO CLR AD OR ABOVE IND."'),
    ('023027.00', '1304.32 40',
     'BZXL,SERS             (ext)'),
    # ---- USA, indicator 17 ------------------------------------------
    ('023027.40', '23030.10 C6',
     'BUSAZ,$+.32           self-relative; bit 18 -> 023030.00'),
    ('023030.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023031.00', '1.03 04',
     'KVI,$X1,1.0           USA'),
    ('023031.40', '1310.00 80',
     'SIC,SEN               (ext) "-UNABLE TO CLR USA OR ABOVE IND."'),
    ('023032.00', '1304.32 40',
     'BZXL,SERS             (ext)'),
    # ---- EXE, indicator 18 ------------------------------------------
    ('023032.40', '23033.11 46',
     'BEXEZ,$+.32           self-relative; bit 18 -> 023033.00'),
    ('023033.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023034.00', '0.43 04',
     'KVI,$X1,(8)0.40       EXE: the operand\'s own bit 18'),
    ('023034.40', '1310.00 80',
     'SIC,SEN               (ext) "-UNABLE TO CLR EXE OR ABOVE IND."'),
    ('023035.00', '1304.32 40',
     'BZXL,SERS             (ext)'),
    # ---- DS, indicator 19: below the immediate field, so KV ---------
    ('023035.40', '23036.11 C6',
     'BDSZ,$+.32            self-relative; bit 18 -> 023036.00'),
    ('023036.00', '13.00 80 000021.02 A0',
     'TI,1,11.0,$X1'),
    ('023037.00', '24545.02 90',
     'KV,$X1,BIT19          (ext) the subroutine\'s only KV'),
    ('023037.40', '1310.00 80',
     'SIC,SEN               (ext) "-UNABLE TO CLR DS OR ABOVE IND."'),
    ('023040.00', '1304.32 40',
     'BZXL,SERS             (ext)'),
    # ---- restore, and return DISABLED -------------------------------
    ('023040.40', '23301.02 10',
     'LX,$X1,I60DMP        (ext) restore the caller\'s $X1'),
    ('023041.00', '0.04 00',
     'I60SX1 BD,0          listing "$BD,0": THE RETURN, DISABLED'),
]

# The one label defined inside the transcribed range.  It IS evidence:
# 023021.40 is where the SLC puts the counter, and I60SX1 is the LAST
# label, so its address is the cumulative sizing of all 25 half-words
# before it -- five of which are full words at odd half-words.
SYMBOLS = {'I60SX1': '023041.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 S1 tail '))
