#!/usr/bin/env python3
"""verify_ax5b_16071_listing.py -- jb_ax5b "I-Box 5", routine 1260's TS
block (programs/ax5b_16071_ts.strap) against the listing's printed
machine code, PDF p.41, octal 016007.00-016012.40.

WHAT THE BLOCK IS.  The deck's test that the INTERVAL TIMER counts
down.  Reference Manual p.44: "4. Time Signal (TS).  The interval
timer has become zero."  The block loads the timer with the value one
(BIT18 -- bit 18 is the low-order bit of word 1's 0-18 timer field),
spins 512 times on a COUNT AND BRANCH to itself, then asks BTS whether
TS came on; failing that it reports "UNABLE TO TURN TS ON."

WHY IT IS WORTH HAVING.  docs/NEXT.md §5 defers "the interval timer
actually ticking" and names routine 1258 as the deck oracle.  This is
a SECOND oracle for the same hardware, eight rows long, inside a
routine already being transcribed.

THREE ENCODINGS IT PINS.

  * BTS "21400.42 42" -- branch on indicator 4.  With BOP (15) and BAD
    (16) in verify_ax5b_16082_16083_listing.py and BDS (19) / BADZ
    (16) in verify_ax5b_16086_listing.py, four widely-spaced indicator
    numbers now cross the printed octal/hex boundary.
  * LCI "1000.11 02" -- 512 decimal is octal 1000, printed in the
    WORD-address column because LCI's operand is an 18-bit count in
    the top 18 bits of the 19-bit field, not an address (Ref. Manual
    p.25).  strap/README.md's Gotchas item 16 records that this field
    was once encoded wrongly; this is a second, independent witness.
  * CB "16010.50 48" -- count and branch to ITSELF at 016010.40, bit
    18 of the target set.  "$" is this block's only operand that is
    not an external symbol, so it is its only real address check.

PROVEN DISCRIMINATING.  Observed failure sets -- and two of the three
were written here as PREDICTIONS first and were WRONG, which is why
this project's bar says to run the injection and record what it does:

  INDICATOR_BITS["TS"] 4 -> 5
      016011.00  BTS -> "21400.42 C2" for "21400.42 42"  (1 row)
      Predicted "21400.44 42", i.e. a change in the OCTAL pair.
      Wrong: 4 is 000100 and 5 is 000101, differing only in the bit
      that lands at 24, so the octal pair is UNCHANGED and the whole
      difference is in the hex byte.  Same phenomenon as OP 15 -> 14
      in verify_ax5b_16082_16083_listing.py, from the other end of
      the indicator range.
  IMM_INDEX_COUNT_OPS loses "LCI" (512 encoded as a 19-bit value
  rather than an 18-bit count)
      016010.00  LCI -> "000400.11 02" for "001000.11 02"  (1 row)
      The count is shifted one bit: octal 400 instead of 1000.
  enc_count_branch drops bit 18 of its target (addr19 & ~1)
      016010.40  CB  -> "016010.10 48" for "016010.50 48"  (1 row)
      Predicted against enc_branch_or_misc, which fails NOTHING here:
      a count-and-branch does not go through that encoder.  CB has
      its own, and the injection has to name it.

WHAT THIS FILE CANNOT SEE, recorded because a green test is only
evidence about faults its inputs could have made visible:

  BIT18's VALUE is not on p.41 -- only its ADDRESS, 024544.00.  This
  check therefore does not verify it.  It IS however a printed fact
  elsewhere in the same document: PDF p.114, under "-COMMON CONSTANTS
  FOR FETCH ONLY", prints the whole BIT table, and BIT18's row reads
  "XW,(8).40,0,0" assembling to "0.40 00 000000.00 00" -- bits 0-17
  zero, octal pair 40 = 100000, i.e. bit 18 set.  BIT<n> is the word
  whose only set bit is bit n, one word per bit from BIT0 at
  024522.00.  Read off the page, not off the symbol's name.

  THE INTERRUPTION SYSTEM'S STATE is not shown either.  Word 1 is one
  of Reference Manual p.31's permanently protected locations, and p.45
  raises DS -- and suppresses the store -- on a to-memory operation
  into that area "while the interruption system was enabled".  So the
  deck must be running DISABLED for this SV to land.  That follows
  from two manual pages; the BD that does it is outside this range.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_16071_ts.strap").read())

# Rows marked (ext) name a symbol defined outside the transcribed range
# and given by SYN from the same print, so they check the opcode and
# modifier bits rather than address placement.  The CB names "$" and is
# the one real address check.
ROWS = [
    ('016007.00', '24544.10 10', 'I6071 LX,$X4,BIT18  (ext) "-TS", the value one'),
    ('016007.40', '1.11 30',     'SV,$X4,1.0           into word 1, the interval timer'),
    ('016010.00', '1000.11 02',  'LCI,$X4,512          512 = octal 1000, an 18-bit count'),
    ('016010.40', '16010.50 48', 'CB,$X4,$             count and branch to itself'),
    ('016011.00', '21400.42 42', 'BTS,I6088           (ext) indicator 4'),
    ('016011.40', '1310.00 80',  'SIC,SEN              (ext) "UNABLE TO TURN TS ON."'),
    ('016012.00', '1304.10 00',  'B,SERS               (ext)'),
    ('016012.40', '21734.10 00', 'B,I6093             (ext)'),
]

SYMBOLS = {
    'I6071': '016007.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 TS '))
