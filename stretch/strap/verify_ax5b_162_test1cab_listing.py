#!/usr/bin/env python3
"""verify_ax5b_162_test1cab_listing.py -- jb_ax5b "I-Box 5", routine
1262 ("TEST EX AND EXIC"), the TEST 1C header row plus TEST 1CA and
TEST 1CB (programs/ax5b_162_test1cab.strap) against the listing's
printed machine code, PDF p.92, octal 023442.40-023460.00.  27 SOURCE
ROWS over 28 half-words (the TI at 023454.00 is a full word), entry
labels I6218 and I6219.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

WHERE THIS SITS.  verify_ax5b_162_test1b_listing.py ends at 023442.00
and verify_ax5b_162_test1cc_listing.py begins at 023474.40, so this
range abuts 1B's last row with nothing between them and stops
023460.40 short of 1CC's cut.  No other verify file here covers any
address in 023442.40-023460.00.  A plain octal scan reports one
apparent overlap, verify_pau_chkssr_listing.py; that is a DIFFERENT
DECK (jb_af1c, the PAU gates routine, square roots) that happens to
load at the same octal addresses.

WHAT THESE BLOCKS ARE.  Reference Manual printed p.50 (PDF p.53), read
first-hand at 400 dpi, continuing from p.49's "In general, when the
interruption system is dis-":

  "abled, interruption cannot occur and address monitoring is
  suspended.  In order that control may remain entirely with the main
  program during an execution operation, two special exceptions are
  made.  First, address monitoring is always in force during (1)
  EXECUTE and (2) EXECUTE INDIRECT AND COUNT, except for the address
  of the location of the FIRST LEVEL pseudo-instruction counter.
  Second, at the completion, termination, or suppression of an
  execution operation, interruption is always permitted."

and its Programming Note, which bounds exception 2 to ONE interruption
and keeps the mask in force:

  "When interruption occurs following an execution operation with the
  interruption system disabled, it is caused only by the actuated
  indicator of highest priority whose mask bit is one.  Further
  interruptions cannot occur until either the system is enabled or
  another execution operation is completed, terminated, or suppressed.
  Examination for other actuated indicators can be programmed into the
  correction routine.

  Any actuated indicator whose mask bit is on may cause interruption
  at the completion, termination, or suppression of an execution
  operation."

1CA tests the second exception alone; 1CB tests the first, delivered by
the second.  The deck names them: "-TEST 1CA, ENABLE AFTER EX." and
"-TEST 1CB, CHK ADR MONITOR."

THE BLOCK IS DISABLED, on three grounds all visible in ROWS below:
023442.40 is BD (BRANCH DISABLED) and is TEST 1C's first instruction;
no BE occurs anywhere in the range (the next one on the page is
023514.00, inside 1CC); and both SVAs name I62ITE with NO "+.32", so
the landing is 024320.00, which PDF p.109 prints as "BD,$"
(verify_ax5b_162_int_entry_listing.py) -- 1CB is entered still
disabled and has no BD of its own.  Corroborating: "BD,I60S1" calls
1260's clear-indicators subroutine, whose return is "$BD,0"
(ax5b_160s1_clr_inds.strap's header, PDF p.85).

THE "-ILLEGAL OP CODE." WORD IS A PRE-CHARGE, a third role for
00000003740 in this deck.  It sits in the STRAIGHT-LINE stream at
023445.40, between SV,$X1,$IA and LVI,$X1,I6219, and actuates OP
(indicator 15) in passing -- Reference Manual printed p.45 (PDF p.48)
item 15: "An instruction with invalid operation code is executed as NO
OPERATION."  OP is permanently masked on (printed p.48, PDF p.51:
"Those corresponding to indicators 0-19 are permanently set to 1"),
but the system is disabled, so nothing interrupts there.  In 1CC the
same word is an ENABLE-STATE PROBE used in opposite directions
(023506.00, 023520.40); in TEST 3A/3B it is a HIGHER-PRIORITY DECOY
against AD.  Here it is neither -- nothing measures the enable state
and nothing competes with OP.  The deck's own error text asserts the
pre-charge: "-NO INT TAKEN ON EX / -WHEN OP SET."  Two more
confirmations: the vector is planted AFTER the illegal word
(023446.00/023446.40), so an interruption at 023445.40 would go to
whatever TEST 1B left in the landing and the block would break rather
than report; and nothing between 023445.40 and 023447.00 clears OP
("Z,$IND" is upstream, at 023444.00).

AND THE SUBJECT OF "EX,$-.32" IS THE SVA, settled by the print, not by
argument -- see the bit-18 table.  It is IDEMPOTENT: $X1 still holds
I6219 because nothing between 023446.00 and 023447.00 touches it, so
re-executing the SVA stores the same address into the same word.  The
subject does nothing on purpose; the only thing under test is the
boundary.  1CA's PASS PATH IS THE ENTRY TO 1CB: the interruption lands
at I62ITE, which branches to I6219.

1CB then puts the boundary control bit in word 3 (BIT57 -> 3.0), sets
the upper boundary to I62EX = 024322.00, and executes a subject at
024332.00 -- above it, i.e. protected -- with the system disabled.
"TI,1,I00O,$MASK" transmits the ALL-ONES index word into the mask,
turning on every settable bit (20-47); that is needed here and not in
1CA because IF is indicator 21, outside the permanently-masked range
OP sits in.  Printed p.45 item 21: "Instruction Fetch (IF).  An
attempt has been made to fetch an instruction from, or branch to, a
location in the protected area of storage while the interruption
system was enabled.  If the corresponding mask bit was one, the fetch
or branch did not take place and the entire operation was suppressed."
(That the item says "enabled" is precisely why p.50's exception 1 has
to exist for 1CB to mean anything.)  I6220 then checks the suppression
took: "LX,$X1,$X1 / BZXVZ,SERS" reports if the subject wrote $X1.

EVERY HEADING AND ERROR MESSAGE, VERBATIM, WITH ITS LOCATION:

  023442.40  -TEST 1C, CHK MISC CNTRLS OF EX.
  023443.00  -TEST 1CA, ENABLE AFTER EX.
  023445.40  -ILLEGAL OP CODE.
  023447.40  -NO INT TAKEN ON EX
  023450.00  -WHEN OP SET.
  023450.40  -TEST 1CB, CHK ADR MONITOR.
  023455.40  -NO INT TAKEN WHEN EX INST
  023456.00  -ABOVE UB.
  023457.00  -INSTRUCTION EXECUTED ABOVE UB WAS
  023457.40  -NOT NOPED.
  023460.00  -CLR BNDS REG.

Three error messages, five headings, one inline data word.

NO DECK TYPO AND NO SCAN DAMAGE IN THIS RANGE, and saying so requires
correcting a reading.  docs/execution_operations.md sec.3.1 records the
header as "-TEST IC," and claims the comment column prints 1C as IC
throughout.  Measured at 600 dpi it does not.  The glyph after "TEST "
on 023442.40 and the one on 023443.00 are the SAME character:

  023442.40   flag y381-387, x2766-2789 (LEFT of the stem only)
              stem x2781-2789
              foot y429-438, x2766-2801 (both sides)
  023443.00   flag y475-486, x2768-2790
              stem x2781-2789
              foot y529-538, x2766-2803

An asymmetric upper-LEFT flag with a symmetric bottom serif is this
printer's DIGIT 1, and it is the same glyph as the 1 of "1CB" at
023450.40.  What reads as a letter-I top bar on the 023442.40 row is
the DASHED RULE LINE the listing draws across that row at y376-380,
spanning x2755-2814 -- wider than the glyph.  The printer's letter I is
a different character: a BARE 13 px stroke with no serifs, as in the I
of "MISC" on the very same line (x3317, width 13), which is the glyph
docs/listing_typography.md measured for the label column.  The header
prints "-TEST 1C," with a digit.  (Whether the note's "ICB" at TEST 2CB
on PDF p.103 is the same artefact was not checked; that page was not
rendered here.)  THE METHOD GENERALISES AND docs/listing_typography.md
does not cover it: ANY glyph verdict taken on a row this listing rules
THROUGH is suspect until the rule's own x-span is measured against the
glyph's.  Here the rule spanned 59 px where the glyph spans 24.  Note
also what the corrected reading buys -- the comment column and the
label column now AGREE about digit-versus-letter on the same page,
"1C"/"1CA"/"1CB" against "I6218"/"I6219"/"I6220", rather than
disagreeing.

"CNTRLS" IS AN ABBREVIATION, NOT A DROPPED LETTER -- decided by PITCH,
which is the test for a dropped letter.  The row is set on 60.6 px at
600 dpi (C of "CHK" x2999 to C of "MISC" x3423 = 7 cells, 60.6/cell).
"CNTRLS" runs C x3539 ... S x3842 = 303 px = exactly 5 cells for 6
characters, so six letters occupy six CONSECUTIVE cells.  A dropped O
would have left a ~60 px hole; there is none.  ADR, BNDS, CHK, INST
and INDS are the same author's ordinary abbreviations.

ONE MORE CORRECTION, and it is the note's transcription rather than a
deck defect: sec.3.3 prints 023454.00 as "TI,1,1000,$MASK".  It is
"TI,1,I00O,$MASK".  The machine code settles it alone -- the first
printed group "24503.00 80" is a 24-bit BIT address in word 0o24503,
which PDF p.114 labels I00O ("-INDX WD. OF ONES.") and which five
other files here already SYN at (8)24503.0; a literal 1000 would be a
decimal bit address in word 15 and print nothing like it.  The glyphs
agree, measured at 600 dpi on this row: leading stroke 13 px (bare
letter I), two 45 px digit zeros, then a 50 px letter O, against a
33 px digit 1 in the same row's ",1," count field -- the calibration
verify_ax4b_1246_transmit_swap_listing.py established (letter O 49 px,
digit 0 42-45 px).  The correction is not cosmetic: an all-ones word
into $MASK turns on EVERY settable mask bit, which is what makes 1CB's
asymmetry with 1CA legible.

ROW COUNT.  docs/execution_operations.md sec.3.6 says 1CA is "eleven
rows"; over 023442.40-023450.00 inclusive it is TWELVE.  The note's
sec.3.2 table has eleven because the "I6218 BD,$+.32" header row is
quoted separately in sec.3.1.  1CB is fifteen rows over sixteen
half-words.  Twenty-seven rows in all.

BIT-18 SELF-CHECKS, decoded from the printed octal pair and matched
against the page's own label column.  The print format is bits 0-17 as
six octal digits, ".", bits 18-23 as two octal digits, then bits 24-31
as two hex digits -- so BIT 18 IS THE TOP BIT OF THE OCTAL PAIR.  Four
classes, three reasons, in the frame verify_ax4b_1246_memories_
listing.py already set:

  (a) HALF-WORD SELECT, decodable.  Branch targets, MISC addresses and
      the 19-bit DirIndex/ImmIndex address fields.  Bit 18 selects the
      half-word of a 19-bit effective address.
        023442.40  BD,$+.32      -> 23443.04 00.  Pair 04 = 000100,
                   bit 18 = 0 -> 023443.00, and 023442.40 + 32 bits is
                   023443.00.
        023446.00  LVI,$X1,I6219 -> 23450.43 01.  Pair 43 = 100011,
                   bit 18 = 1 -> 023450.40, which is where p.92 prints
                   I6219.  IN-RANGE, so this is evidence.
        023447.00  EX,$-.32      -> 23446.52 00.  Pair 52 = 101010,
                   bit 18 = 1 -> 023446.40.  THE STAR OF THE BLOCK.
                   023447.00 minus 32 bits is 023446.40, the SVA -- NOT
                   the illegal word, which is three half-words back
                   ("$-1.32").  EX's operand is a 19-bit half-word
                   address and bit 18 is live in it.  The trap 32 bits
                   sets -- that 32 bits is ALSO one half-word, so a
                   ".32" row reads the same under the wrong
                   interpretation -- is real for the OTHER EX:
                   023455.00's pair 12 has bit 18 = 0 and reads
                   identically whether the field is 19 bits or 18.
                   023447.00's pair 52 does not, which is exactly what
                   makes the two EX rows a matched test and control.
                   Injection 2 below is this decode made falsifiable,
                   and it moves this row and no other.
        023452.40  LVI,$X1,I6220 -> 23456.43 01.  Bit 18 = 1 ->
                   023456.40 = I6220.  IN-RANGE, evidence.
        023455.00  EX,I62EXI     -> 24332.12 00.  Pair 12 = 001010,
                   bit 18 = 0 -> 024332.00.  The CONTROL for 023447.00:
                   the two EX rows are a matched pair, one with bit 18
                   set and one clear, inside twenty-eight half-words.
        023450.00  BD,SERS  -> 1304.04 00, pair 04, bit 18 = 0.
        023456.00  B,SERS   -> 1304.10 00, pair 10 = 001000, bit 18 = 0.
                   Note the code field beside bit 18: BD is 0o04 and B
                   is 0o10 here, and bit 18 would add 0o40.
        023443.40  BD,I60S1 -> 22741.04 00, bit 18 = 0 -> 022741.00.
        023444.40 / 023451.40  LVI to I62INT / I62EX, pair 03, bit 18
                   = 0.  023445.00 / 023452.00 SV, 023446.40 /
                   023453.00 SVA, 023444.00 / 023453.40 / 023460.00 Z:
                   all pair 03 or 22, bit 18 = 0.
        (Of the rows in this class, 023443.40, 023444.40, 023450.00,
        023451.40, 023453.00 and 023456.00 name a SYN, so they check
        the other fields and not the address.  023442.40 and 023447.00
        are self-relative and 023446.00 and 023452.40 name in-range
        labels; those four are the address evidence.)
  (b) LX and SX are EXCLUDED, and not for the same reason as (c)/(d).
      Reference Manual printed p.23 (PDF p.26), read first-hand
      (footer "Operand Designation  23"): "In the majority of these
      operations, 19 bits of the effective address are used in order to
      permit addressing of half-words.  The two exceptions use only 18
      bits of the effective address because they require full-word
      operands."  The two exceptions are LOAD INDEX and STORE INDEX,
      and p.23's own LX paragraph repeats it: "The index word specified
      by J is replaced by the full-word specified by bits 0-17 of the
      effective address."  So in 023450.40 "LX,$X1,BIT57" -> 24613.02
      10, 023451.00 "SX,$X1,3.0" -> 3.03 10 and 023456.40
      "LX,$X1,$X1" -> 21.02 10, the pair is NOT a half-word select;
      bit 18 is simply not part of the address.
  (c) SIC is EXCLUDED because its operand is a 24-bit BIT address in
      bits 0-23, so the octal pair is a BIT OFFSET inside the word, not
      a half-word select.  Four rows: 023443.00, 023447.40, 023455.40,
      023457.00, all printing ".00 80" (the 80's high nibble is the
      format's literal 1000 at bits 24-27).
  (d) TRANSMIT at 023454.00 is BOTH.  Its A1 is a 24-bit BIT address in
      bits 0-23 and is excluded for the same reason as (c): "24503.00
      80" is word 0o24503 bit 0.  But its A2 IS decodable -- it is a
      19-bit half-word address at bits 32-50, so in the SECOND printed
      group bit 50 is the top bit of the pair: "000014.02 A0" gives
      bit 50 = 0, i.e. word 0o14 = 12 = $MASK at its .00 half.  The
      ".02 A0" tail is the format's own literal for a count-1
      immediate transmit and is identical in verify_ax5b_16087_
      listing.py's "TI,1,BIT0($X1),$MASK" (24522.00 81 000014.02 A0)
      and verify_ax5b_160_test6_listing.py's "TI,1,BIT38,$MASK"
      (24570.00 80 000014.02 A0); it is not a bit offset in $MASK.
  The trap this frame avoids: 32 bits is ALSO one half-word, so a
  ".32" self-relative row reads identically under the wrong
  interpretation.  023447.00 is the row where it does not.

BRANCH POLARITY, decided per check and settled from the printed hex.
enc_branch_ind puts branchOn at bit 30, so hex 42 is branch-on-ON and
hex 40 is branch-on-OFF.  This range has exactly ONE indicator branch:
  023457.40  BZXVZ,SERS -> 1304.31 40.  Hex 40 = 0100 0000 over bits
             24-31, so bit 30 = 0: BRANCH ON XVZ OFF.  Which is right:
             "Z,$X1" zeroed $X1 and "LX,$X1,$X1" reads it back, so XVZ
             is ONE if the suppressed subject left $X1 alone (pass, no
             branch) and ZERO if the subject ran and wrote a non-zero
             value (branch to SERS, "-INSTRUCTION EXECUTED ABOVE UB WAS
             NOT NOPED.").  Injection 3 below inverts the bit and moves
             this row alone.

WITNESS TIERING.  Every SYN in the program file is an INPUT, not a
witness -- the caveat verify_ax5b_16082_16083_listing.py makes about
I6088.  A SYN makes the address field come out right by construction,
so a row naming one proves only that every OTHER field lands where the
listing puts it.  I6218 is NOT evidence either: it is the first label
after an SLC this transcription fed 023442.40, so checking it checks
the SLC against its own input; it is asserted as the anchor.  The
genuine address evidence is I6219 and I6220 -- each the cumulative
sizing of every half-word before it, each named by an LVI whose octal
pair carries bit 18 -- plus the two self-relative rows 023442.40 and
023447.00.  Two tiers of corroboration exist for the externals and
neither promotes them: I62INT/I62ITE/I62EX and I00O/BIT57 are
confirmed by separately read pages' own label columns (PDF pp.109 and
114, and verify_ax5b_bit_table_listing.py for BIT57 = 024613.00),
while SEN/SERS/I60SX1/I60S1/I62EXI rest on other files here
(verify_ax5b_16087_listing.py gives I60SX1 = 023041.00 and
I60S1 = 022741.00).

THREE THINGS THIS FILE CANNOT SEE, recorded rather than left.
  * I62EXI = 024332.00 comes from docs/NEXT.md's read of PDF p.110 and
    was NOT re-verified at any dpi here; verify_ax5b_162_int_entry_
    listing.py stops at 024331.00, one half-word short of it.  1CB's
    whole premise is that the subject lies above the upper boundary
    024322.00, and I62EXI is the only thing that establishes it -- but
    023455.00's printed "24332.12 00" agrees with the SYN BY
    CONSTRUCTION, so this row cannot catch a wrong SYN.  The reading is
    at least self-consistent: p.109's own label column puts I62EXM at
    024331.00, so 024332.00 is the next free word.
  * WHAT THE 64-WORD INTERRUPT TABLE HOLDS WHEN 1CA RUNS IS NOT READ.
    1CA has no fill loop and neither does TEST 1B before it, yet
    "SVA,$X1,I62ITE" with no "+.32" only works if the table still holds
    I62K1 ("BD,I62ITE", landing at 024320.00).  The pairing rule is
    verify_ax5b_162_int_entry_listing.py's, from p.109; the last fill
    this repo has actually read is 1CC's I6233 loop at 023522.00, which
    is AFTER this block.  ONE CONJECTURE, FLAGGED AS ONE, in the style
    that file already uses.
  * WHAT WORD 3 HOLDS WHEN 1CA RUNS IS NOT READ EITHER.  1CA sets no
    boundaries and 1CB's trailing "Z,3.0" is the first clear in the
    range.  This does not touch the encoding oracle at all, but it
    matters to whoever runs 1CA on the model: under p.50's exception 1
    a stale boundary would put the EX's own subject fetch under address
    monitoring while disabled, and 1CA could interrupt for the wrong
    reason and still look like a pass.

FIRSTS: exactly one, and it survived a grep that knocked the others
down.  "EX,$-.32" at 023447.00 is the repo's first SELF-RELATIVE EX and
its first BACKWARD one -- grepping every verify_*.py and every
programs/*.strap for an EX operand finds only label operands
(I62B3-B6, I62EXT) and register operands ($X3, $R, $L).  NOT firsts,
checked: EX itself (verify_ax5b_162_test1b_listing.py, five rows;
verify_ax5b_162_test1cc_listing.py, four), TI including the exact
"TI,1,<word>,$MASK" shape (verify_ax5b_16087_listing.py 021400.40,
verify_ax5b_160_test6_listing.py 022063.00), BZXVZ (ten files),
SVA/LVI/LX/SX/SV/Z/SIC/BD/B throughout, and the DD(BU,32,8) word
(ax5b_160k_constants.strap, ax5b_162_test3a.strap).  What the block
ADDS short of a first is the matched bit-18 EX pair described above.

PROVEN DISCRIMINATING.  Five injections, each made with a whole-line
anchored edit, each CONFIRMED APPLIED by printing the patched line
before running, each run with __pycache__ removed on BOTH sides, each
reverted by reversing the exact patch (never git checkout, per
AGENTS.md rule 2) with the file's md5 checked back to its original.
The failure sets below are OBSERVED, not predicted.

  1. opcodes.MISC_CODES["EX"] 0b010 -> 0b110
     (confirmed: line 215 read '    "EX":  0b110,')
       023447.00  EX,$-.32   -> "023446.72 00"            (2 rows)
       023455.00  EX,I62EXI  -> "024332.32 00"
     Both EX rows, one per block, and nothing else in 28 half-words.
     The code field sits beside bit 18, so the whole change lands in
     the octal pair (52 -> 72 and 12 -> 32) while bit 18 stays put.
  2. strap_asm's branch/misc address mask 0x7FFFF -> 0x7FFFE -- i.e.
     "EX's operand is an 18-bit word address like LX/SX"
     (confirmed: line 1428 read '...lineno=stmt.lineno) & 0x7FFFE')
       023447.00  EX,$-.32   -> "023446.12 00"            (1 row)
     THE SHARPEST ROW IN THE FILE.  The mask drops bit 18 from every
     branch and every MISC address in the block, and exactly one row
     moves, because 023447.00 is the only one whose bit 18 is set.
     023455.00 (EX, bit 18 = 0) is the control and does not move: the
     bit-18 claim for EX is measured, not asserted.
  3. strap_asm.enc_branch_ind, branchOn -> 1 - branchOn
     (confirmed: line 355 read '... (clear, 1), (1 - branchOn, 1), ...')
       023457.40  BZXVZ,SERS -> "001304.31 42"            (1 row)
     The block's only indicator branch, and the polarity decision
     above made falsifiable: 40 -> 42 is exactly bit 30.
  4. strap_asm.enc_sic literal 0b1000 -> 0b1001
     (confirmed: line 961 read '... | (0b1001 << 4) | (idx & 0xF)')
       023443.00  SIC,I60SX1 -> "023041.00 90"            (4 rows)
       023447.40  SIC,SEN    -> "001310.00 90"
       023455.40  SIC,SEN    -> "001310.00 90"
       023457.00  SIC,SEN    -> "001310.00 90"
     All four SIC rows and only those.  The TI at 023454.00 prints the
     same 1000 literal at bits 24-27 and did NOT move: grep-confirmed,
     enc_sic (strap_asm.py line 961) and enc_transmit (line 395) hold
     two separate 0b1000 constants, so the two encoders are checked
     independently rather than sharing one witness.
  5. opcodes.IMM_INDEX_CODES["LVI"] 0b0001 -> 0b0101
     (confirmed: line 124 read '    "LVI":    0b0101,')
       023444.40  LVI,$X1,I62INT -> "024220.03 05"        (4 rows)
       023446.00  LVI,$X1,I6219  -> "023450.43 05"
       023451.40  LVI,$X1,I62EX  -> "024322.03 05"
       023452.40  LVI,$X1,I6220  -> "023456.43 05"
     Only the hex byte moves (01 -> 05), so the immediate-index code
     in its low nibble is checked independently of the 19-bit value
     and of bit 18, which the two in-range rows also carry.

A MEASURED NULL, WITH A LIVENESS PROOF.  These are 28 half-words and
not everything can be separated here; the honest thing is to show what
cannot.
  N. strap_asm.enc_dir_index, (idx, 4) -> ((idx << 1) & 0xF, 4)
     (confirmed: line 340 read
      '    v, w = cat((addr19, 19), (j, 4), (code, 5), ((idx << 1) & 0xF, 4))')
       ALL TESTS PASSED -- zero rows moved.
     LIVENESS, so the null is a measurement and not a silently failed
     patch: under the SAME patched build a CONSTRUCTED row this data
     does not contain moves, while its unindexed twin does not.
       SX,$X2,I00O($X1)   clean "024503.05 11"  patched "024503.05 12"
       SX,$X2,I00O        clean "024503.05 10"  patched "024503.05 10"
     Neither 1CA nor 1CB has a single parenthesized index -- unlike
     1CC's "SX,$X2,I62INT($X1)" -- so the index field is zero in all 27
     rows and this block cannot see the bug at all.  The same is true
     of CB_CODES' refill bit and BB_CODES' mod field: no CB+ and no BB
     occur here.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_test1cab.strap").read())

ROWS = [
    # ---- TEST 1C header row, then TEST 1CA ---------------------------
    ('023442.40', '23443.04 00',
     'I6218 BD,$+.32      "-TEST 1C, CHK MISC CNTRLS OF EX."'),
    ('023443.00', '23041.00 80',
     'SIC,I60SX1          (ext) "-TEST 1CA, ENABLE AFTER EX."'),
    ('023443.40', '22741.04 00',
     'BD,I60S1            (ext) clear indicators 0-19; returns DISABLED'),
    ('023444.00', '13.22 00',
     'Z,$IND               word 11 = 0o13'),
    ('023444.40', '24220.03 01',
     'LVI,$X1,I62INT      (ext) the 64-word interrupt table'),
    ('023445.00', '2.03 30',
     'SV,$X1,$IA           word 2 = the interruption address register'),
    ('023445.40', '00000003740',
     'DD(BU,32,8),(8)3740  "-ILLEGAL OP CODE." -- IN THE STRAIGHT LINE'),
    ('023446.00', '23450.43 01',
     'LVI,$X1,I6219       in-range label; bit 18 = 1 -> 023450.40'),
    ('023446.40', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) NO "+.32": the BD half of the landing'),
    ('023447.00', '23446.52 00',
     'EX,$-.32             THE TEST; bit 18 = 1 -> 023446.40, the SVA'),
    ('023447.40', '1310.00 80',
     'SIC,SEN              (ext) "-NO INT TAKEN ON EX"'),
    ('023450.00', '1304.04 00',
     'BD,SERS              (ext) "-WHEN OP SET."'),
    # ---- TEST 1CB ----------------------------------------------------
    ('023450.40', '24613.02 10',
     'I6219 LX,$X1,BIT57  (ext) "-TEST 1CB, CHK ADR MONITOR."'),
    ('023451.00', '3.03 10',
     'SX,$X1,3.0           the boundary register; control bit on'),
    ('023451.40', '24322.03 01',
     'LVI,$X1,I62EX       (ext) 024322.00'),
    ('023452.00', '3.03 30',
     'SV,$X1,$UB           upper boundary := 024322.00'),
    ('023452.40', '23456.43 01',
     'LVI,$X1,I6220       in-range label; bit 18 = 1 -> 023456.40'),
    ('023453.00', '24320.03 D0',
     'SVA,$X1,I62ITE      (ext) again the BD half'),
    ('023453.40', '21.22 00',
     'Z,$X1                word 0o21 = 17 = X1'),
    ('023454.00', '24503.00 80 000014.02 A0',
     'TI,1,I00O,$MASK     (ext) FULL WORD: ALL settable mask bits on'),
    ('023455.00', '24332.12 00',
     'EX,I62EXI           (ext) THE TEST; bit 18 = 0 -> 024332.00'),
    ('023455.40', '1310.00 80',
     'SIC,SEN              (ext) "-NO INT TAKEN WHEN EX INST"'),
    ('023456.00', '1304.10 00',
     'B,SERS               (ext) "-ABOVE UB."'),
    ('023456.40', '21.02 10',
     'I6220 LX,$X1,$X1     read $X1 back to set the index indicators'),
    ('023457.00', '1310.00 80',
     'SIC,SEN              (ext) "-INSTRUCTION EXECUTED ABOVE UB WAS"'),
    ('023457.40', '1304.31 40',
     'BZXVZ,SERS           (ext) "-NOT NOPED."  hex 40 -> branch-on-OFF'),
    ('023460.00', '3.22 00',
     'Z,3.0                "-CLR BNDS REG."  1CB\'s last row'),
]

# Only labels DEFINED inside the transcribed range belong here; a SYN'd
# external would be checking this file against itself.  I6218 is the
# SLC anchor, NOT evidence -- the SLC was fed 023442.40 by this same
# transcription.  I6219 and I6220 are genuine witnesses: each is the
# cumulative sizing of every half-word before it, and each is
# independently named by an LVI whose printed octal pair carries bit 18.
SYMBOLS = {
    'I6218': '023442.40',
    'I6219': '023450.40',
    'I6220': '023456.40',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 1CA/1CB '))
