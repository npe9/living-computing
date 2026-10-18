#!/usr/bin/env python3
"""verify_ax5b_1681_listing.py -- jb_ax5b "I-Box 5", routine 1268's
TEST 1A (../decks/ax5b_1681_if_close_to_ds.strap) against the
listing's printed machine code, PDF p.110, octal
024337.00-024344.00.

WHAT 1268 IS: see verify_ax5b_1683_listing.py.  docs/NEXT.md called it
the deck test of the DF and IF INDICATORS; it is not.  Test 2 is the
store-to-LOAD side; this is the store-to-INSTRUCTION-FETCH side.

THE BLOCK plants a whole word over location I682 twice and then FALLS
INTO I682 and executes what is there -- first [Z,$X2 | NOP], then
[LVI,$X2,(8)777777.40 | NOP].  "LX,$X2,$X2" re-reads X2 without
changing it, purely so the index result indicators describe X2 (Ref.
Manual p.23), and the following BXVZ tests them: value zero means the
stale Z ran, which is "EXECUTED OLD INSTRUCTION FROM EXT."

THE PEN MARKS on this page were resolved at 600 dpi before anything
was transcribed.  The XW's second half-word is boxed with "LVI"
written beside it, and "LX,$X2,$X2" is circled: a reader noting that
the slot is overwritten at run time and that the re-read is an
indicator trick.  Explanations, not corrections -- the printed machine
code is the assembler's own output and is what this file checks.

PROVEN DISCRIMINATING (encoding).  Observed failure sets:

  DIR_INDEX_CODES["SX"] 0b10001 -> 0b10010
      024337.40 and 024341.40 -- both SX rows        (2 rows)
  UNCOND_BRANCH_CODES["NOP"] 0b110 -> 0b101
      024340.00 and 024340.40                        (2 rows)
  INDICATOR_BITS["XVZ"] 50 -> 51
      024344.00  BXVZ                                (1 row)

AND THE RUN, measured rather than assumed.  The companion execution
passes, and what it does and does not witness was established by
injecting packIndexWord (LX/SX move a WHOLE 64-bit index word, so the
planted instruction round-trips through it):

  packIndexWord zeroes `count` (IBM 28-45)
      halts at 1416 = 001304.00 = SERS, the deck's OWN error path.
      IBM bit 31 lives in `count` and is part of the planted LVI's J
      field, so the plant stops being "LVI,$X2", X2 stays zero, and
      BXVZ fires exactly as the deck intends.  This is the witness.
  packIndexWord drops `addr` bit 23
      halts at 0 -- caught, but chaotically: the plant decodes as
      something else entirely and control runs away.  (A zero
      half-word decodes as BE,0; see docs/NEXT.md's trap list.)
  packIndexWord zeroes `spare` (IBM 26-27) -- the EXISTING
  index-spare-bits-zeroed mutant
      PASSES, and provably must.  The planted words are
      I68K1 = 0x0004920000001800 and I68K2 = 0xffffe50100001800;
      both have sign, flag AND SPARE zero already, so a mutant that
      only disturbs bits 26-27 cannot change what is planted.  This
      block therefore does NOT help that mutant, which the campaign
      still catches 23 minutes away in "IBOX-3 SVA into a
      floating-point instruction".

WHAT THE RUN DOES NOT WITNESS: look-ahead forwarding.  It puts TWO
NOPs between the store and the fetch, gentler even than test 2, which
is already too gentle for this model -- removing StretchStorage.bsv's
store-queue drain leaves test 2 green.  It is a regression guard on
self-modifying execution and on the LX/SX index-word round trip.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_1681_if_close_to_ds.strap").read())

# Rows marked (ext) name a symbol given by SYN from the listing's own
# print.  The two SX rows name I682, defined INSIDE the range, and are
# real address checks.
ROWS = [
    ('024337.00', '24407.02 10', 'I681 LX,$X1,I68K1   (ext) "-TEST 1A,IF CLOSE TO DS IN EXT MEM."'),
    ('024337.40', '24342.03 10', 'SX,$X1,I682          plant the OLD instruction'),
    ('024340.00', '0.30 00',     'NOP'),
    ('024340.40', '0.30 00',     'NOP'),
    ('024341.00', '24410.02 10', 'LX,$X1,I68K2         (ext)'),
    ('024341.40', '24342.03 10', 'SX,$X1,I682          plant the NEW one over it'),
    ('024342.00', '0.00 00 000000.00 00',
                                 'I682 XW,0,0,0        the slot -- executed as planted'),
    ('024343.00', '22.04 10',    'LX,$X2,$X2            re-read to set the indicators'),
    ('024343.40', '1310.00 80',  'SIC,SEN               (ext)'),
    ('024344.00', '1304.31 42',  'BXVZ,SERS             (ext) "EXECUTED OLD INSTRUCTION FROM EXT."'),
]

SYMBOLS = {'I681': '024337.00', 'I682': '024342.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1268 T1A '))
