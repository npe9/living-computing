#!/usr/bin/env python3
"""verify_ax5b_16082_16083_listing.py -- jb_ax5b "I-Box 5", routine
1260's OP and AD blocks (../decks/ax5b_16082_op_ad.strap) against the
listing's printed machine code, PDF pp.41-42, octal
017225.00-017234.40.

WHY THESE TWO.  They are contiguous, every instruction in them is
already implemented here (see docs/archival_inventory.md's triage of
the sixteen blocks on pp.41-44), and together they print the SAME
branch target through TWO different indicator numbers:

    BOP,I6088   21400.47 C2      indicator 15
    BAD,I6088   21400.50 42      indicator 16

THAT PAIR IS WHY THIS FILE EXISTS.  enc_branch_ind puts the 6-bit
indicator number at bits 19-24; the listing prints bits 18-23 as an
octal pair and bits 24-31 as hex.  The indicator number therefore
STRADDLES the two printed fields, five bits in one and one in the
other.  Two rows with the same address and adjacent indicator numbers
differ in BOTH fields at once, which pins that placement harder than
any single row can.  The I6086 block's BDS/BADZ (19 and 16) never
exercised a number whose top bit differs.

AND THEY CORROBORATE A PAGE READ SEPARATELY.  Both rows carry bit 18
of their target set, so I6088 is at 021400.40 -- which was established
from pp.43-45.  These rows are on pp.41-42, so they say it again from
a different page, independently of that reading.

BUT THE PASSING ROWS ARE NOT THE WITNESS.  I6088 is a SYN of
021400.40, an INPUT to this check, chosen so the rows match.  The
evidence is the printed code read off pp.41-42 at 600 dpi -- ".47" is
100111 and ".50" is 101000, both with bit 18 set.  What these rows add
is that this assembler places bit 18 where the listing places it,
which the 5-bit indnum injection below witnesses.

PROVEN DISCRIMINATING.  Observed failure sets, not predicted:

  INDICATOR_BITS["OP"] 15 -> 14
      017230.00  BOP -> "21400.47 42" for "...C2"      (1 row)
      Note WHERE it shows: the octal pair is UNCHANGED at .47 and
      only the hex byte moves, because 14 and 15 differ solely in
      the bit that lands at 24.  A check reading only the octal
      field would have missed it entirely.
  enc_branch_ind packs indnum in 5 bits instead of 6
      017230.00  BOP -> "...84", 017233.00  BAD -> "...84"  (2 rows)
  UNCOND_BRANCH_CODES["NOP"] 0b110 -> 0b101
      017226.00, 017226.40, 017232.40 -> "0.24 00"      (3 rows)
  XW sized as a half-word rather than a full one
      No row fails: the assembler's own overlap guard raises first
      ("two statements deposited overlapping bits in word 7831").
      run_tests.sh's `run` tracks a non-zero exit as a failure, so
      the suite still catches it -- but it is not a named-row check.

AND TWO THINGS THIS FILE CANNOT SEE, recorded because the bar here is
that a green test is only evidence about faults its inputs could have
made visible:

  CNOP's alignment, FULL changed to HALF
      NOTHING fails.  At 017227.00 the location counter is already
      word-aligned, so this block's CNOP emits nothing either way.
      verify_ibox1_ensu_listing.py does witness it: there the CNOP
      lands on an odd half-word and emits a real NOP.
  XW's FIELD PLACEMENT
      Not injected, because nothing could fail.  This XW is "0,0,0",
      so value, count and refill are all zero and any permutation of
      the three emits the same all-zero word.  The row checks that XW
      occupies a FULL word and that the word is zero, nothing more.
      ibox1_ensu.strap's "XW,(8)777777.00,2,(8)100" is where the
      fields are actually pinned.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_16082_op_ad.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from the same print, so they check the opcode and
# modifier bits rather than address placement.  The SX row names
# I6082A, defined INSIDE the range, and is a real address check.
ROWS = [
    ('017225.00', '23050.10 10', 'I6082 LX,$X4,I60K7  (ext) "-OP"'),
    ('017225.40', '17227.11 10', 'SX,$X4,I6082A        over the zeroed slot'),
    ('017226.00', '0.30 00',     'NOP'),
    ('017226.40', '0.30 00',     'NOP'),
    ('017227.00', '0.00 00 000000.00 00',
                                 'I6082A XW,0,0,0      the slot, all zeros'),
    ('017230.00', '21400.47 C2', 'BOP,I6088            (ext) indicator 15'),
    ('017230.40', '1310.00 80',  'SIC,SEN               (ext)'),
    ('017231.00', '1304.10 00',  'B,SERS                (ext) "UNABLE TO TURN OP ON."'),
    ('017231.40', '21734.10 00', 'B,I6093              (ext)'),
    ('017232.00', '1.51 30',     'I6083 SV,$X4,1.32    "-AD"'),
    ('017232.40', '0.30 00',     'NOP'),
    ('017233.00', '21400.50 42', 'BAD,I6088            (ext) indicator 16'),
    ('017233.40', '1310.00 80',  'SIC,SEN               (ext)'),
    ('017234.00', '1304.10 00',  'B,SERS                (ext) "UNABLE TO TURN AD ON."'),
    ('017234.40', '21734.10 00', 'B,I6093              (ext)'),
]

SYMBOLS = {
    'I6082':  '017225.00',
    'I6082A': '017227.00',
    'I6083':  '017232.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 OP/AD '))
