#!/usr/bin/env python3
"""verify_ax5b_1258_test2_listing.py -- jb_ax5b "I-Box 5", routine 1258
"CHK TIME CLOCK AND INTERVAL TIMER", TEST 2
(programs/ax5b_1258_test2.strap) against the listing's printed machine
code, PDF p.7, octal 014034.00-014063.40.  48 rows, one unbroken
half-word run.

WHERE IT IS.  Routine 1258 is the FIRST listing block of the deck, PDF
pp.5-7, right after the prose write-up -- not in the tail where its
number would put it.  These listing pages carry no printed page
numbers, so every citation here is a PDF page.

WHERE THE CUT IS.  Test 1 (I581-I586, 014012.00-014033.40) is the TIME
CLOCK half and fills PDF p.6, closing with its own three-row
continuity block at 014033.40.  Test 2 opens the next page at
014034.00 with label I587.  Nothing straddles the boundary and no
symbol defined in Test 1 is referenced here.  Test 1 is not
transcribed: this model has no time clock at all, so it is further
from being runnable than the timer.

TWO SOURCE LINES IN THIS RANGE CARRY ONLY A COMMENT and emit no code,
both of them "-CONTAINS ITS NEW VALUE, 0-18.": one after 014042.00 and
one after 014047.00.  So the block is ~50 source lines and 48
machine-code rows, and every one of the 48 is a half-word instruction
-- no XW, VF or DD, so no full-word row shape occurs here.  The
routine's full-word constants (IC258, ICK258, I58K1, I58K2) all sit on
PDF p.5, outside the range, and enter as SYN.

THIS IS THE INTERVAL TIMER'S CONTRACT, IN THE DECK'S OWN WORDS.
verify_ax5b_16071_listing.py already holds an eight-row block that
loads the timer with one, spins, and asks whether TS came on -- a
witness that the countdown EXISTS.  This block is four separate
assertions about how it behaves, each carrying its own error text:

  1. THE RATE, I587/I587A/I587B.  Timer := BIT18 (the value one), then
     a 256-count spin watching for word 1 to stop equalling 1.0.
     Failure: "-INTERVAL TIMER FAILS TO STEP IN" / "-ONE MILLISEC,
     TERMINATE TEST 2."  One millisecond is the deck's own statement
     of the rate; Reference Manual printed p.34 gives 1,024 (2^10)
     steps per second, one step per 0.9766 ms.

  2. THE DECREMENT BY EXACTLY ONE, I588.  KV against I00Z, whose row
     on PDF p.114 reads "I00Z XW,0,0,0,0  -ZERO INDX WD." and prints
     "0.00 00 000000.00 00" -- the constant's VALUE is printed, not
     inferred from its name.  Failure: "-INTERVAL TIMER FAILS TO STEP"
     / "-FROM 000000.4 TO 000000.0. IX 1" / "-CONTAINS ITS NEW VALUE,
     0-18."

  3. THE RELOAD RULE, I589/I5810.  Timer := zero, spin until it
     changes, then compare against I58K1, whose row on PDF p.5 prints
     "777777.40 00 000000.00 00" -- bits 0-17 all ones and octal pair
     40 = 100000, so bit 18 too: ALL ONES IN BITS 0-18, nothing else.
     Failure: "-INTERVAL TIMER FAILS TO STEP" / "-FROM 000000.0 TO
     777777.40. IX 2" / "-CONTAINS ITS NEW VALUE, 0-18."  That is the
     1 -> 0 -> all-ones reload, printed, from the deck.

  4. THE BITS-19-23 CLEARING, I5811/I5812.  Timer := I58K2, whose p.5
     row prints "1.77 00 000000.00 00" -- bit 17 set AND bits 18-23
     all ones, and bits 19-23 lie OUTSIDE the timer's 0-18 field.
     After the step the expected value is BIT17, "1.00 00 000000.00
     00", bit 17 alone.  Failure: "-INTERVAL TIMER FAILS TO STEP" /
     "-FROM 000001.77 TO 000001.00. IX 3" / "-CONTAINS ITS NEW VALUE,
     0-23."

     THE FIELD WIDTH IN THAT LAST LINE IS THE FINDING.  Blocks I588
     and I5810 both say "0-18."  This one says "0-23."  The deck
     widens its own message exactly where it is testing the five bits
     the timer field does not cover, and the value it expects has them
     CLEAR.  Reference Manual printed p.34's programming note -- bits
     19-23 of location 1's left half go to zero when the timer is set
     -- is thereby stated by the deck as the SCOPE OF ITS OWN
     COMPARISON, which is stronger than a constant that merely happens
     to have those bits off.

  The "IX 1" / "IX 2" / "IX 3" tails name the index register of each
  block's KV -- $X1 at 014041.00, $X2 at 014046.00, $X3 at 014053.40
  -- so the comment-to-row assignment is corroborated by the code
  column and does not rest on reading pixel positions.

THE BRANCH POLARITY, stated once: a "BZ<ind>" mnemonic branches while
the indicator is OFF and a "B<ind>" while it is ON
(strap_asm.classify_branch_indicator gives the BZ prefix branchOn=0).
So BZXE (XE is 53, compare-equal) branches while the two values
DIFFER, BZXVZ (XVZ is 50, index value zero) branches while the value
is NONZERO, and BXE at 014054.00 branches to the exit while the value
IS the expected one.

THIRTEEN ROWS ARE REAL ADDRESS CHECKS.  Their targets are labels
defined inside the transcribed range: BZXE->I588, CB->I587A,
B->I5813, BZXVZ->I5810, CB->I589, B->I587B (twice), BZXE->I5812,
CB->I5811, BXE->I5813, B,$+1.0, BD->I587, BD,$+.32.  Every one was
checked by reading bit 18 out of the printed octal pair against the
page's own label column, and every one agrees; ax5b_16071_ts.strap,
by contrast, has exactly one such row.  Rows marked (ext) name a
symbol given by SYN from the same print and check only the opcode and
modifier bits.

EVERY SYN IS AN INPUT TO THIS CHECK, NOT A WITNESS.  BIT18, BIT17,
BIT1, I00Z, I58K1, I58K2, IC258, ICK258, SEN, SENO, SERS, SSW and
I60 were each derived by reading bit 18 out of the octal pair of the
very row that names them, so those rows can only re-derive what was
put in.  The same caveat verify_ax5b_16082_16083_listing.py makes
about I6088.

THE BIT TABLE GAINS THREE CONFIRMATIONS of 024522 + n, each read off
an encoding here and then matched against the table as PDF p.114
prints it: BIT1 -> 024523 ("200000.00 00 ..."), BIT17 -> 024543
("1.00 00 ..."), BIT18 -> 024544 ("0.40 00 ...").

SENO's SPELLING IS STILL OPEN, but not for the reason this docstring
used to give.  It said the printer draws letter O and digit 0 with the
same glyph; docs/listing_typography.md section 6 names that claim and
measures it wrong -- letter O runs 15-22% wider than digit 0 on both
decks, its three calibration pairs being 55 against 45 (ax5b p.83,
within one printed comment), 49/42 and 48/43 (ax4b p.6).  The result
is a direction rather than a reading: n = 3, within reach of ink
weight and skew.  The repository still spells the symbol SENO, SEN0
and LSEN0 in different files.  p.114 prints its own row, measured
there as "SENO SYN,SEN0" -> "1311.00+ +00000000": a label and an
operand that must be DIFFERENT spellings, since a symbol defined as
itself could not have produced that printed value, with the width
measurement deciding which is which.  Either way the row fixes the
ADDRESS at 001311.00.  Nothing in this check or any injection below
depends on the name.

THERE IS NO CNOP IN THIS RANGE.  The routine's one CNOP is at
014004.40, in the 158 preamble on PDF p.5, outside the transcript.

PROVEN DISCRIMINATING.  Observed failure sets -- measured, with
__pycache__ cleared on both sides of each injection:

  INDICATOR_BITS["XE"] 53 -> 52
      014036.00 BZXE  '014040.72 40' for '014040.72 C0'
      014042.00 BZXE  '001304.32 40' for '001304.32 C0'
      014047.00 BZXE  '001304.32 40' for '001304.32 C0'
      014051.40 BZXE  '014053.32 40' for '014053.32 C0'
      014054.00 BXE   '014055.72 42' for '014055.72 C2'
      014063.00 BZXE  '001304.32 40' for '001304.32 C0'      (6 rows)
      The OCTAL PAIR IS UNCHANGED and the whole difference is in the
      hex byte: 53 is 110101 and 52 is 110100, differing only in the
      bit that lands at 24.  Same phenomenon verify_ax5b_16071_
      listing.py records for TS 4 -> 5 and verify_ax5b_16082_16083_
      listing.py for OP 15 -> 14 -- the indicator field straddles the
      listing's printed octal/hex boundary.

  INDICATOR_BITS["XE"] 53 -> 51
      the same six rows, and now the complement:
      014036.00 '014040.71 C0', 014042.00/014047.00/014063.00
      '001304.31 C0', 014051.40 '014053.31 C0', 014054.00
      '014055.71 C2'                                          (6 rows)
      The OCTAL PAIR moves and the HEX BYTE does not.  Two injections
      one indicator apart in opposite directions move two different
      printed fields, which is what a straddling field looks like from
      either side.

  IMM_INDEX_COUNT_OPS loses "LCI" (256 encoded as a 19-bit value
  rather than an 18-bit count)
      014035.00 '000200.03 02' for '000400.03 02'
      014043.40 '000200.11 02' for '000400.11 02'
      014050.40 '000200.07 02' for '000400.07 02'             (3 rows)
      The count shifts one bit: octal 200 instead of 400.  A third
      independent witness for the field strap/README.md's Gotchas item
      16 records, after verify_ibox1_listing.py and
      verify_ax5b_16071_listing.py.

  enc_count_branch drops bit 18 of its target (addr19 & ~1)
      014036.40 CB  '014035.02 48' for '014035.42 48'         (1 row)
      ONLY ONE OF THE THREE CB ROWS FAILS, and that is the interesting
      part.  I587A is at 014035.40, so its target has bit 18 set and
      the dropped bit shows; I589 (014044.00) and I5811 (014051.00)
      are word-aligned, so the same fault is invisible in those two
      rows.  A count-and-branch also does not go through
      enc_branch_or_misc, so an injection there would fail nothing
      here -- the injection has to name CB's own encoder.

WHAT THIS FILE CANNOT SEE, recorded because a green test is only
evidence about faults its inputs could have made visible:

  THE INTERRUPTION SYSTEM'S STATE.  Word 1 is one of Reference Manual
  p.31's permanently protected locations, and printed p.34 names this
  very instruction: "The only store-type operations that may store in
  the left half of location 1, and hence may be used to set the
  interval timer, are STORE VALUE, STORE COUNT, STORE REFILL, and
  STORE VALUE IN ADDRESS, and these operations can be performed only
  when the interruption system is disabled.  When enabled, these
  operations will turn on indicator DS, data store, and be
  suppressed."  So the three SV,$X0,1.0 rows land only with the system
  off; the BD that does it is outside this range.  ax5b_16071_ts.strap
  makes the same point about the same word.

  THE TIMING.  "-ONE MILLISEC" and the three 256-count spins are the
  deck's assertion about wall-clock rate.  Nothing in an encoding
  check can test that; it is an acceptance criterion for a model that
  ticks, which this one does not.

  "1.0" IS TRANSCRIBED VERBATIM.  opcodes.py's SYSTEM_SYMBOLS has
  "IT": (1, 0), so $IT would assemble to identical bits -- but the
  deck wrote 1.0 and this is a transcription, not a rewrite.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_1258_test2.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from the same print, so they check opcode/modifier
# bits rather than address placement.  The unmarked branch rows are the
# real address checks.
ROWS = [
    ('014034.00', '24544.00 10',
     'I587 LX,$X0,BIT18     (ext) "-TEST 2"; bit 18 = the value one'),
    ('014034.40', '1.01 30',
     'SV,$X0,1.0             into word 1, the interval timer'),
    ('014035.00', '400.03 02',
     'LCI,$X1,256            256 = octal 400, an 18-bit count'),
    ('014035.40', '1.00 90',
     'I587A KV,$X0,1.0      has the timer moved?'),
    ('014036.00', '14040.72 C0',
     'BZXE,I588             XE (53) OFF = the values differ: it stepped'),
    ('014036.40', '14035.42 48',
     'CB,$X1,I587A          ...256 tries'),
    ('014037.00', '1310.00 80',
     'I587B SIC,SEN         (ext) "-INTERVAL TIMER FAILS TO STEP IN"'),
    ('014037.40', '1304.10 00',
     'B,SERS                 (ext) "-ONE MILLISEC, TERMINATE TEST 2."'),
    ('014040.00', '14055.50 00',
     'B,I5813               give up on TEST 2'),
    ('014040.40', '1.02 10',
     'I588 LX,$X1,1.0       read the stepped timer'),
    ('014041.00', '24502.02 90',
     'KV,$X1,I00Z           (ext) the new value must be ZERO'),
    ('014041.40', '1310.00 80',
     'SIC,SEN                (ext) "-INTERVAL TIMER FAILS TO STEP"'),
    ('014042.00', '1304.32 C0',
     'BZXE,SERS              (ext) "-FROM 000000.4 TO 000000.0. IX 1"'),
    ('014042.40', '24502.00 10',
     'LX,$X0,I00Z           (ext) [a comment-only source line,'
     ' "-CONTAINS ITS NEW VALUE, 0-18.", sits above this row]'),
    ('014043.00', '1.01 30',
     'SV,$X0,1.0             timer := zero'),
    ('014043.40', '400.11 02',
     'LCI,$X4,256'),
    ('014044.00', '1.04 10',
     'I589 LX,$X2,1.0'),
    ('014044.40', '14046.31 40',
     'BZXVZ,I5810           XVZ (50) OFF = nonzero: it reloaded'),
    ('014045.00', '14044.10 48',
     'CB,$X4,I589'),
    ('014045.40', '14037.10 00',
     'B,I587B               never reloaded: the timing error'),
    ('014046.00', '14010.04 90',
     'I5810 KV,$X2,I58K1   (ext) ...and it must be ALL ONES 0-18'),
    ('014046.40', '1310.00 80',
     'SIC,SEN                (ext) "-INTERVAL TIMER FAILS TO STEP"'),
    ('014047.00', '1304.32 C0',
     'BZXE,SERS              (ext) "-FROM 000000.0 TO 777777.40. IX 2"'),
    ('014047.40', '14011.00 10',
     'LX,$X0,I58K2          (ext) bit 17 plus bits 18-23; a second'
     ' comment-only line, "-CONTAINS ITS NEW VALUE, 0-18.", sits above'),
    ('014050.00', '1.01 30',
     'SV,$X0,1.0'),
    ('014050.40', '400.07 02',
     'LCI,$X3,256'),
    ('014051.00', '1.00 90',
     'I5811 KV,$X0,1.0'),
    ('014051.40', '14053.32 C0',
     'BZXE,I5812'),
    ('014052.00', '14051.06 48',
     'CB,$X3,I5811'),
    ('014052.40', '14037.10 00',
     'B,I587B'),
    ('014053.00', '1.06 10',
     'I5812 LX,$X3,1.0'),
    ('014053.40', '24543.06 90',
     'KV,$X3,BIT17           (ext) bit 17 ALONE: 19-23 must be clear'),
    ('014054.00', '14055.72 C2',
     'BXE,I5813             "-INTERVAL TIMER FAILS TO STEP"'),
    ('014054.40', '1310.00 80',
     'SIC,SEN                (ext) "-FROM 000001.77 TO 000001.00. IX 3"'),
    ('014055.00', '1304.10 00',
     'B,SERS                 (ext) "-CONTAINS ITS NEW VALUE, 0-23."'),
    ('014055.40', '14056.50 00',
     'I5813 B,$+1.0'),
    ('014056.00', '14034.04 00',
     'BD,I587               loop back to the head of TEST 2'),
    ('014056.40', '1311.40 80',
     'SIC,SENO+.32           (ext)'),
    ('014057.00', '1301.10 00',
     'B,SSW                  (ext) to SSIP'),
    ('014057.40', '14060.04 00',
     'BD,$+.32'),
    ('014060.00', '14006.32 10',
     'LX,$X13,IC258         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('014060.40', '24523.32 B0',
     'V+,$X13,BIT1           (ext) test 2 done = bit 1'),
    ('014061.00', '14006.33 10',
     'SX,$X13,IC258         (ext)'),
    ('014061.40', '14006.32 10',
     'LX,$X13,IC258         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('014062.00', '14007.32 90',
     'KV,$X13,ICK258        (ext) against the expected word'),
    ('014062.40', '1310.00 80',
     'SIC,SEN                (ext)'),
    ('014063.00', '1304.32 C0',
     'BZXE,SERS              (ext) "-CONTINUITY ERROR."'),
    ('014063.40', '14064.10 00',
     'B,I60                 (ext) on to routine 160'),
]

SYMBOLS = {'I587':  '014034.00', 'I587A': '014035.40',
           'I587B': '014037.00', 'I588':  '014040.40',
           'I589':  '014044.00', 'I5810': '014046.00',
           'I5811': '014051.00', 'I5812': '014053.00',
           'I5813': '014055.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1258 T2 '))
