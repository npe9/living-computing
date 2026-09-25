#!/usr/bin/env python3
"""verify_ax5b_1258_test1_listing.py -- jb_ax5b "I-Box 5", routine 1258
"CHK TIME CLOCK AND INTERVAL TIMER", TEST 1
(programs/ax5b_1258_test1.strap) against the listing's printed machine
code, PDF pp.5-6.  46 rows in three contiguous blocks:

    014002.00-014004.40   routine 158's preamble          (6 half-words)
    014006.00-014011.00   routine 1258's constant pool    (4 FULL words)
    014012.00-014033.40   TEST 1 itself, entry I581      (36 half-words)

WHERE IT IS.  Routine 1258 is the FIRST listing block of the deck, PDF
pp.5-7, right after the prose write-up -- not in the tail where its
number would put it.  These listing pages carry no printed page
numbers, so every citation here is a PDF page.  TEST 1 fills the whole
of PDF p.6; the preamble and the constants are the last dozen lines of
PDF p.5.  TEST 2 (014034.00-014063.40, PDF p.7) is
verify_ax5b_1258_test2_listing.py; the two together are all of 1258.

THE ONE CUT, AND WHY IT IS FORCED.  014005.00 is not transcribed.  Its
source line reads "I58ID  %IQSZ*DD%BU,64,8*,I258   Z" (corrected
2026-09-24 from a digits reading, "1581D ... ,1258"; the label's first
and fourth characters and the operand's lead are all the LETTER I,
measured at 600 dpi -- see docs/listing_typography.md) -- % is this
printer's "(" and * stands for its ")" glyph, fixed by the same page's
"XW,%8*777777.40,0,0" being the "(8)" radix prefix this assembler
already accepts -- so the line is a call of the SSIP/DCP
print-formatting macro %IQSZ, the routine's IDENT word.
docs/archival_inventory.md already records %IQSZ/%IQS* as macros with
no counterpart in this model and notes that every routine's ident line
carries one.  THE LISTING PRINTS A LOCATION FOR IT AND NO MACHINE CODE.
There is therefore nothing to check there, and writing
"DD(BU,64,8),1258" in its place would assert a row shape the page does
not print.  The program cuts with SLC,(8)14006.0 and takes the ident
word's address as a SYN.  Nothing else in 014002.00-014033.40 is
skipped.

WHY THIS BLOCK IS THE TIME CLOCK'S ORACLE.  The model has no time
clock at all -- not a register, not a stub.  Reference Manual printed
p.35 (PDF 38), read first-hand:

  "This clock consists of a number 36 bits long which is continually
   stepped up by pulses originating from the same 1024 cycle per second
   oscillator which controls the updating of the interval timer.  The
   two clocks are updated consecutively in the same time interval."

  "The value of the clock occupies bits 28-63 of location 1.  Each time
   the oscillator delivers a pulse it is read out, incremented by one,
   using the index adder, and returned to core storage."

  "Its setting, however, cannot be altered under program control.  Any
   attempt to store into the right half of location 1 is suppressed,
   and indicator AD, address invalid, is turned on."

Bits 28-63 of a word are exactly the COUNT (28-45) and REFILL (46-63)
fields of an INDEX WORD, which is the whole shape of this block: word 1
is read as ONE index word with LX, and the 36-bit clock comes back
split across two fields that half-word instructions can move
separately.  Reference Manual printed p.24, first-hand:

  STORE REFILL (SR): "The refill field, bits 46-63, of the index word
  specified by J replaces bits 0-17 of the half word specified by bits
  0-18 of the effective address.  Bits 18-24 of the half word are set
  to zero."

  STORE COUNT (SC): the same sentence with "count field, bits 28-45".

  COMPARE VALUE (KV): "The address part, bits 0-24, of the half-word
  addressed by bits 0-18 of the effective address is compared with the
  address part, bits 0-24, of the index word specified by J."

So SR moves the clock's LOW 18 bits and SC its HIGH 18 bits into the
VALUE position of a scratch index word, where KV can compare them.  The
scratch words are $X2 (old low), $X3 (old high), $X4 (new low), $X5
(new high), zeroed by "Z,$X2" addressing index register 2 as storage
word 18 -- which is why those four rows assemble to 22/23/24/25 octal.

THE DECK'S THREE ASSERTIONS, each with its own printed error text:

  1. IT STEPS WITHIN ONE MILLISECOND (I581/I582, 014012.00-014021.40).
     Snapshot the clock, then spin a 256-count CB re-reading word 1 and
     asking whether the low half still equals the snapshot.  BZXE
     branches out while XE is OFF -- while they DIFFER -- and the
     deck's own comment on that row is "-IT STEPPED."  Falling out of
     the spin reports
         "-TIME CLOCK FAILS TO STEP IN 1 MSEC."
     One millisecond is the deck's statement of the rate; the manual's
     1,024 steps per second is one step per 0.9766 ms.

  2. THE LOW HALF WENT UP BY EXACTLY ONE (I583/I584).  V+I,$X2,1.0 adds
     one to the saved old low half, and I584's KV,$X2,$X4 compares it
     against the new low half.  Failure:
         "-BITS 46-63 ARE NOT CORRECT AFTER"
         "-TIME CLOCK STEPPED."
     Those ARE the refill field's bit numbers, printed by the deck.

     THE COMMENT-TO-BLOCK ASSIGNMENT DOES NOT REST ON PIXEL POSITIONS.
     I584 compares $X2 against $X4 and I585 compares $X3 against $X5, in
     the CODE column; the manual independently defines refill as 46-63
     and count as 28-45; SR wrote $X2/$X4 and SC wrote $X3/$X5.  The
     register numbers pin which message belongs to which block, the way
     TEST 2's "IX 1"/"IX 2"/"IX 3" tails do there.  The deck's text and
     the Reference Manual's definitions then corroborate each other
     rather than either one carrying the claim alone.

  3. THE HIGH HALF IS RIGHT (I585).  KV,$X3,$X5.  Failure:
         "-BITS 28-45 ARE NOT CORRECT AFTER"
         "-TIME CLOCK STEPPED."
     Again the deck names the count field's own bit numbers, over the SC
     rows at 014015.40 and 014022.00.

THE CARRY PATH DOES NOT REACH THE FIELD THAT IS COMPARED.  BZXVZ at
014023.00 branches past the carry step while XVZ is OFF (the
incremented low half is NONZERO); only a wrap falls through to
014023.40's C+I,$X3,1.0.  Reference Manual printed p.25, first-hand:

  "ADD IMMEDIATE TO COUNT (C+I): Bits 0-17 of the address part of the
   instruction are added to the count field, bits 28-45, of the index
   word specified by J.  Both quantities are unsigned and the addition
   takes place modulo 2**18."

-- while 014026.00's KV compares bits 0-24, the VALUE field, which is
where SC put the old high half.  So the carry lands in a field the
comparison never reads, and the block would report a spurious "-BITS
28-45 ARE NOT CORRECT" on the one entry in 2**18 where the low half
wraps.  C+I and V+I differ by one letter in the source and one NIBBLE
in the printed encoding -- "1.07 00" against "1.07 05" -- and the
IMM_INDEX_CODES["C+I"] injection below measures exactly that one row, so
this is a bit-level claim about the page and not an inference about
intent.  V+I would have propagated the carry; what the deck MEANT is
not recoverable from the print.  I585 is reached on both paths out of
I584 (BXE,I585 when the low half checks out, fall-through into the
SIC / B,SERS report otherwise), so nothing conditionally skips it.

NOTHING IN THIS RANGE STORES INTO WORD 1.  TEST 2 sets the interval
timer with three SV,$X0,1.0 rows and so needs the interruption system
disabled; TEST 1 only READS (LX,$X0,1.0, twice).  That is forced by
p.35: the clock's setting "cannot be altered under program control".

THIRTEEN ROWS ARE REAL ADDRESS CHECKS -- their targets are labels
defined inside this transcript: Z->IC258 and BD->I581 from the
preamble (which is why the preamble is here: they reach across all
three blocks), BZXE->I583, CB->I582, B->I586, BZXVZ->I584,
BXE->I585, BXE->I586, B,$+1.0, BD->I581, BD,$+.32, LX->IC258 and
SX->IC258.  Every one was checked by reading bit 18 out of the printed
octal pair against the page's own label column, and every one agrees.
EXACTLY ONE of them carries bit 18 set: BD,$+.32 at 014032.00 prints
"14032.44 00", octal pair 44 = 100100, whose top bit makes the target
014032.40 -- the next half-word, which is what "$+.32" says.  The other
twelve are bit-18 clear against word-aligned labels.  That single row is
this transcript's whole witness for "bit 18 is the top bit of the octal
pair", and the enc_branch_or_misc injection below isolates it.

THE SYN LIST IS FOUR SHORTER THAN TEST 2'S, which is the payoff for
carrying the preamble and the constant pool: IC258, ICK258, I58K1 and
I58K2 are DEFINED here, so the rows TEST 2 could only mark "(ext)" --
Z,IC258 at 014004.00, LX,$X13,IC258 at 014032.40 and SX,$X13,IC258 at
014033.40 -- are real address checks in this file.

AND IT RETIRES FOUR OF TEST 2'S INPUT CAVEATS, which is the more useful
direction.  ax5b_1258_test2.strap SYNs IC258 (8)14006.0, ICK258
(8)14007.0, I58K1 (8)14010.0 and I58K2 (8)14011.0 as unwitnessed
inputs, read out of the very rows that name them.  This file defines all
four from their own printed constant-pool rows at exactly those
addresses, so TEST 2's four addresses now have transcribed rows behind
them -- including I58K1 and I58K2, the constants TEST 2's reload
assertion and its bits-19-23 assertion rest on.

SIC'S PRINTED OCTAL PAIR IS NOT A BIT-18 SELECT, and two rows here would
otherwise look like counter-examples to the "exactly one bit-18-set row"
claim above.  SIC's operand is a 24-bit BIT address (bits 0-23 of the
half-word), so its pair is a bit offset WITHIN the word: "1306.40 80" at
014003.00 is bit 32 of word 001306, and "1311.40 80" at 014031.00 is
SENO+.32.  Same printed column, different meaning; neither is a branch
target and neither is among the thirteen in-range address checks.

EVERY SYN IS AN INPUT TO THIS CHECK, NOT A WITNESS.  I58ID, DPET13,
RET, IDF1, BIT0, SEN, SENO, SERS and SSW were each derived by reading
bit 18 out of the octal pair of the very row that names them, so those
rows can only re-derive what was put in.  The same caveat
verify_ax5b_16082_16083_listing.py makes about I6088 and
verify_ax5b_1258_test2_listing.py makes about its thirteen.

BIT0 IS SETTLED BY THE CONSTANT POOL, not by analogy.  014033.00 prints
"24522.32 B0", one below TEST 2's BIT1 at 024523, so the bit table's
base 024522 is read off an encoding here.  Which BIT it is does not rest
on the name (this printer draws letter O and digit 0 with one glyph):
ICK258, transcribed in this file at 014007.00, prints "600000.00 00
000000.00 00" -- bits 0 AND 1 set -- and TEST 2's own continuity row
adds BIT1.  So bit 0 is TEST 1's, digit zero, witnessed by the word the
two tests jointly build.

THE CONTINUITY BLOCK IS UPDATE-ONLY HERE.  TEST 1 closes with three rows
and no compare; TEST 2 does the same update with BIT1 and then verifies
against ICK258.  ICK258 is therefore transcribed in this file as a
constant and referenced by no row in range.

CNOP IS IN THIS TRANSCRIPT AND EMITS NOTHING.  The listing prints
NEITHER a location NOR machine code for the CNOP line following
014004.40: that row is the second half of word 014004, so the counter
already stands at the word boundary 014005.00 and CNOP has no gap to
fill.  It is kept as CNOP, never hand-expanded.  THE LIMITATION, stated
plainly: because the transcript cuts at the very next row, the
SLC,(8)14006.0 that follows re-establishes the counter, so no row in
this file would move if CNOP misbehaved.  The silence is witnessed by
the page, not by this check.
verify_ax5b_160_test8c_disabled_listing.py is the file that witnesses
both CNOP branches from assembled output (case 1 emits a filler NOP at
022567.40, case 2 emits nothing at 022626.00).

WHAT THIS FILE CANNOT SEE, recorded because a green test is only
evidence about faults its inputs could have made visible:

  THE CLOCK ITSELF.  There is none in the model.  Every row here is an
  encoding; not one of them can be executed to a meaningful result
  today.  That is the point of transcribing it.

  THE TIMING.  "-IN 1 MSEC." and the 256-count spin are assertions about
  wall-clock rate.  No encoding check can test them.

  THE IDENT WORD at 014005.00, and the %IQSZ macro's expansion.

  "1.0" IS TRANSCRIBED VERBATIM.  opcodes.py's SYSTEM_SYMBOLS has
  "TC": (1, 28) for the time clock and "IT": (1, 0) for the timer; the
  deck wrote 1.0 and this is a transcription, not a rewrite.

PROVEN DISCRIMINATING.  Observed failure sets -- measured, with
__pycache__ cleared on both sides of each injection.  TEST 2's own four
injections were checked here first and two of them fail NOTHING in this
range (recorded so the next pass does not repeat the experiment): the
enc_count_branch "addr19 & ~1" injection is null because the one CB row
here targets word-aligned 014016.00, and dropping "C+I" from
IMM_INDEX_COUNT_OPS is null because "1.0" yields imm19 = 2 on the
shift-6 and the shift-5 path alike.  The four below do bite:

  DIR_INDEX_CODES["SR"] 0b10111 -> SC's 0b10101
      014015.00 SR,$X0,$X2  '000022.01 50' for '000022.01 70'
      014016.40 SR,$X0,$X4  '000024.01 50' for '000024.01 70'   (2 rows)

  DIR_INDEX_CODES["SC"] 0b10101 -> SR's 0b10111
      014015.40 SC,$X0,$X3  '000023.01 70' for '000023.01 50'
      014022.00 SC,$X0,$X5  '000025.01 70' for '000025.01 50'   (2 rows)
      THE PAIR IS THE POINT.  Refill and count are one bit apart in the
      5-bit direct-index code and that bit lands inside the printed hex
      byte, so the page distinguishes "clock bits 46-63" from "clock
      bits 28-45" at the encoding level -- which is this routine's
      entire subject.  Neither injection moves any octal pair.

  MISC_CODES["Z"] 0b100 -> 0b000
      014004.00 Z,IC258    '014006.02 00' for '014006.22 00'
      014013.00 Z,$X2       '000022.02 00' for '000022.22 00'
      014013.40 Z,$X4       '000024.02 00' for '000024.22 00'
      014014.00 Z,$X3       '000023.02 00' for '000023.22 00'
      014014.40 Z,$X5       '000025.02 00' for '000025.22 00'  (5 rows)
      Five rows spanning TWO of the three blocks, and the whole
      difference is in the OCTAL PAIR: the misc code sits at bits 19-21,
      above the printed octal/hex boundary, where the direct-index code
      straddles it.  Two injections, two different printed fields.

  IMM_INDEX_CODES["C+I"] 0b0000 -> V+I's 0b0101
      014023.40 C+I,$X3,1.0 '000001.07 05' for '000001.07 00'  (1 row)
      The empirical half of the carry-path finding above: the page's own
      hex byte separates ADD IMMEDIATE TO COUNT from ADD IMMEDIATE TO
      VALUE while leaving address and J identical.

  enc_branch_or_misc drops bit 18 of its address (addr19 & ~1)
      014032.00 BD,$+.32    '014032.04 00' for '014032.44 00'  (1 row)
      ONE row out of eleven branch/misc rows, and it is the only one
      whose target is not word-aligned -- the isolation of the bit-18
      claim, exactly as verify_ax5b_1258_test2_listing.py's CB injection
      isolated I587A there.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_1258_test1.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from the same print, so they check opcode/modifier
# bits rather than address placement.  The unmarked rows whose operand
# is a label or "$" are the real address checks.
ROWS = [
    # --- BLOCK A: routine 158's preamble, PDF p.5 -------------------
    ('014002.00', '14005.02 10',
     'I58 LX,$X1,I58ID     (ext) "-UPDATE IDENT."; the %IQSZ word'),
    ('014002.40', '1437.03 10',
     'SX,$X1,DPET13          (ext)'),
    ('014003.00', '1306.40 80',
     'SIC,RET                (ext) a half-word-odd SIC target'),
    ('014003.40', '1443.10 00',
     'B,IDF1                 (ext)'),
    ('014004.00', '14006.22 00',
     'Z,IC258               clear the continuity word, defined in BLOCK B'),
    ('014004.40', '14012.04 00',
     'BD,I581               into TEST 1 with the system disabled'),
    # the CNOP line follows here and prints NO location and NO machine
    # code: 014005.00 is already a word boundary.  Then the cut.

    # --- BLOCK B: routine 1258's constant pool, PDF p.5 -------------
    ('014006.00', '0.00 00 000000.00 00',
     'IC258 XW,0,0,0        "-CONTINUITY REG 1258."'),
    ('014007.00', '600000.00 00 000000.00 00',
     'ICK258 XW,(8)600000.00,0,0   bits 0 AND 1: both tests done'),
    ('014010.00', '777777.40 00 000000.00 00',
     'I58K1 XW,(8)777777.40,0,0    all ones 0-18; TEST 2 uses it'),
    ('014011.00', '1.77 00 000000.00 00',
     'I58K2 XW,(8)1.77,0,0         bit 17 + bits 18-23; TEST 2 uses it'),

    # --- BLOCK C: TEST 1 itself, the whole of PDF p.6 ---------------
    ('014012.00', '400.03 02',
     'I581 LCI,$X1,256      "-TEST 1, CHECK TIME CLOCK STEPPING."'),
    ('014012.40', '1.00 10',
     'LX,$X0,1.0             word 1 AS ONE INDEX WORD'),
    ('014013.00', '22.22 00',
     'Z,$X2                  word 18'),
    ('014013.40', '24.22 00',
     'Z,$X4                  word 20'),
    ('014014.00', '23.22 00',
     'Z,$X3                  word 19'),
    ('014014.40', '25.22 00',
     'Z,$X5                  word 21'),
    ('014015.00', '22.01 70',
     'SR,$X0,$X2             OLD bits 46-63 -> X2 value field'),
    ('014015.40', '23.01 50',
     'SC,$X0,$X3             OLD bits 28-45 -> X3 value field'),
    ('014016.00', '1.00 10',
     'I582 LX,$X0,1.0       re-read the clock'),
    ('014016.40', '24.01 70',
     'SR,$X0,$X4             NEW bits 46-63 -> X4 value field'),
    ('014017.00', '22.10 90',
     'KV,$X4,$X2             new low half against old low half'),
    ('014017.40', '14022.32 C0',
     'BZXE,I583             "-IT STEPPED."  XE (53) OFF = they differ'),
    ('014020.00', '14016.02 48',
     'CB,$X1,I582           ...256 tries'),
    ('014020.40', '1310.00 80',
     'SIC,SEN                (ext)'),
    ('014021.00', '1304.10 00',
     'B,SERS                 (ext) "-TIME CLOCK FAILS TO STEP IN 1 MSEC."'),
    ('014021.40', '14030.10 00',
     'B,I586                give up on TEST 1'),
    ('014022.00', '25.01 50',
     'I583 SC,$X0,$X5       NEW bits 28-45 -> X5 value field'),
    ('014022.40', '1.05 05',
     'V+I,$X2,1.0            old low half + 1'),
    ('014023.00', '14024.31 40',
     'BZXVZ,I584            XVZ (50) OFF = nonzero: no carry'),
    ('014023.40', '1.07 00',
     'C+I,$X3,1.0            the carry -- into bits 28-45; see the header'),
    ('014024.00', '24.04 90',
     'I584 KV,$X2,$X4       old low + 1 against new low'),
    ('014024.40', '14026.32 C2',
     'BXE,I585              XE (53) ON = correct'),
    ('014025.00', '1310.00 80',
     'SIC,SEN                (ext) "-BITS 46-63 ARE NOT CORRECT AFTER"'),
    ('014025.40', '1304.10 00',
     'B,SERS                 (ext) "-TIME CLOCK STEPPED."'),
    ('014026.00', '25.06 90',
     'I585 KV,$X3,$X5       old high against new high'),
    ('014026.40', '14030.32 C2',
     'BXE,I586'),
    ('014027.00', '1310.00 80',
     'SIC,SEN                (ext) "-BITS 28-45 ARE NOT CORRECT AFTER"'),
    ('014027.40', '1304.10 00',
     'B,SERS                 (ext) "-TIME CLOCK STEPPED."'),
    ('014030.00', '14031.10 00',
     'I586 B,$+1.0'),
    ('014030.40', '14012.04 00',
     'BD,I581               loop back to the head of TEST 1'),
    ('014031.00', '1311.40 80',
     'SIC,SENO+.32           (ext)'),
    ('014031.40', '1301.10 00',
     'B,SSW                  (ext) "-TO SSIP."'),
    ('014032.00', '14032.44 00',
     'BD,$+.32               THE ONE BIT-18-SET ROW: pair 44 -> 014032.40'),
    ('014032.40', '14006.32 10',
     'LX,$X13,IC258         "-UPDATE CONTINUITY CHECK."'),
    ('014033.00', '24522.32 B0',
     'V+,$X13,BIT0           (ext) test 1 done = bit 0'),
    ('014033.40', '14006.33 10',
     'SX,$X13,IC258'),
]

SYMBOLS = {'I58':   '014002.00', 'IC258': '014006.00',
           'ICK258': '014007.00', 'I58K1': '014010.00',
           'I58K2': '014011.00', 'I581':  '014012.00',
           'I582':  '014016.00', 'I583':  '014022.00',
           'I584':  '014024.00', 'I585':  '014026.00',
           'I586':  '014030.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1258 T1 '))
