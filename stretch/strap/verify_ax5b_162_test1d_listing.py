#!/usr/bin/env python3
"""verify_ax5b_162_test1d_listing.py -- jb_ax5b "I-Box 5", routine 1262
("TEST EX AND EXIC"), TEST 1D (programs/ax5b_162_test1d.strap) against
the listing's printed machine code, PDF p.95, octal
023551.40-023576.00.  42 SOURCE ROWS over 42 half-words -- no
full-word row, because the DD(BU,32,8) at 023570.00 is a 32-bit datum
occupying one half-word.  Entry label I6241; five more labels defined
inside the range.  THE WHOLE OF TEST 1D, ON ONE PAGE.

CITED BY PDF PAGE.  jb_ax5b's LISTING pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering, and the only printed numbers are in the
front write-up, which is scanned 2-up.  Every verify_ax5b_*.py here
already says "PDF p.NN" for that reason.

WHERE THIS SITS.  verify_ax5b_162_test1cc_listing.py ends at
023545.40; verify_ax5b_162_test2a_listing.py opens TEST 2A at
023576.40, the first row of PDF p.96.  A programmatic sweep of every
ROWS tuple in every verify_*.py in this directory finds NO file with
any octal location inside 023551.40-023576.00 -- not even the jb_af1c
PAU decks (verify_pau_chkssr*_listing.py, verify_pau_srte30_
listing.py), which collide with routine 1262 elsewhere only because
that is a DIFFERENT DECK loading at the same octal addresses.  The
same sweep run against 023442.40-023460.00 and 023576.40-023600.00 as
a control does report the expected files, so the empty result is a
measurement, not a broken sweep.

WHAT TEST 1D DOES TO PROVOKE USA -- the part that matters to the
implementation.  The deck BUILDS a chain of EXECUTEs at run time and
fires it with one EX:

  023551.40  LX,$X1,USAWD             the loop count
  023552.00  LX,$X2,I62K4             the TEMPLATE: PDF p.109's
                                      "I62K4  EX,$L" is a FULL WORD
                                      holding TWO "EX" half-words
  023552.40  LVI,$X3,I6084A+.32       $X3 := the chain's 2nd half-word
  023553.00  I6242 SX,$X2,I6084A($X1) store the template word
  023553.40  SVA,$X3,I6084A($X1)      aim the 1st EX at $X3
  023554.00  V+I,$X3,(8)0.40          advance one half-word
  023554.40  SVA,$X3,I6084A+.32($X1)  aim the 2nd EX at $X3
  023555.00  V+I,$X3,(8)0.40
  023555.40  CB+,$X1,I6242            count up, loop

so each pass lays down one word = two EX half-words, each pointing at
the half-word after it.  023556.00/023556.40 then patch the last link
to point at I6243.  WHY 2049, and this is derived from the print
rather than conjectured (docs/execution_operations.md sec.4 lists it
as unsettled, "presumably 2048+1"):

    023552.40  "LVI,$X3,I6084A+.32" -> 17245.47 01  =>  I6084A=017245.00
    023556.40  "SVA,$X1,I6084B"     -> 21245.03 D0  =>  I6084B=021245.00
    021245 - 017245 = 0o2000 = 1024 WORDS = 2048 HALF-WORDS, so
    017245.00 THROUGH 021245.00 INCLUSIVE IS 2049 HALF-WORDS.

The loop fills the 2048 below I6084B, two per pass; I6084B itself is
an existing named word whose address field the patch rewrites.  2049
successive EXECUTEs is the length of the chain the block constructs,
and the error text names that number twice.  CAVEAT: both addresses
are SYN'd in the .strap FROM THIS PRINT, so the rows agree with them
by construction and this checker cannot catch a misreading -- the
same caveat ax5b_162_test1cab.strap records for I62EXI.

Then, before the EX: $IA is pointed at the 64-word table; I60S1 is
called to clear indicators 0-19 (via a PLAIN "B", not the "BD" TEST
1C and TEST 2CA use -- transcribed, not tidied; I60S1 returns via
"$BD,0" either way, so the system is still DISABLED); "Z,$IND /
Z,$MASK" clears every indicator AND EVERY SETTABLE MASK BIT, so that
NOTHING outside the permanently-masked 0-19 range can interrupt
(Reference Manual printed p.48: "Those corresponding to indicators
0-19 are permanently set to 1"; USA is 17); and "LVI,$X1,I6245 /
SVA,$X1,I62ITE" plants the PASS landing with NO "+.32", i.e. at
024320.00, which PDF p.109 prints as "BD,$".

THREE OUTCOMES, ONE PASS:
  * USA fires, the operation is terminated, and the interruption is
    taken AT THE COMPLETION OF THE EXECUTION OPERATION although the
    system is disabled -> I62ITE -> I6245.  THE PASS, and it needs
    printed p.50's SECOND special exception.
  * USA fires, no interruption -> "BUSA,I6244" branches and
    023565.40/023566.00 report "-2049 SUCCESSIVE EXECUTES FAIL TO
    COUSE INT BUT DO SET USA."
  * USA never fires -> the branch is not taken and 023564.00/
    023564.40 report "-2049 SUCCESSIVE EXECUTES FAIL TO SET USA AND
    FAIL TO CAUSE INTERRUPT."
So TEST 1D is a SECOND deck witness for exception 2 on top of TEST
1CA's, and the only one in the deck for USA.  Reference Manual
printed p.45 item 17: "The operation is terminated wherever it may be
and the program proceeds. ... If interruption occurs, it takes place
after execution of the causing instruction has been terminated."

HALF TWO is a separate test sharing the entry: from I6245 the block
replants the landing, falls through an inline illegal-op word
(00000003740 at 023570.00, actuating OP in passing), runs "EX,I62B7"
whose subject the error text names as a BD, and checks EXE with
"BEXEZ,$+1.32".  Falling through reports "-EX OF A BD FAILS TO SET
EXE IND."  I did not read I62B7's contents.

EVERY HEADING AND ERROR MESSAGE, VERBATIM, WITH ITS LOCATION:

  023551.40  -TEST 1D, CHK EXE AND USA INDS.
  023564.00  -2049 SUCCESSIVE EXECUTES FAIL TO SET
  023564.40  -USA AND FAIL TO CAUSE INTERRUPT.
  023565.40  -2049 SUCCESSIVE EXECUTES FAIL TO COUSE
  023566.00  -INT BUT DO SET USA.
  023570.00  -ILLEGAL OP CODE,
  023571.40  -EX OF A BD FAILS
  023572.00  -TO SET EXE IND.
  023574.00  -TO SSIP
  023575.00  -UPDATE CONTINUITY CHECK.

One heading, three error messages (each over two rows), one
inline-data comment, one exit comment, one continuity comment.  The
four rows that end without punctuation (023564.00, 023565.40,
023571.40, 023574.00) were MEASURED to end without it, not assumed:
each one's last glyph is a 42-48 px letter, with nothing in the next
pitch cell.

TYPO-VS-DAMAGE VERDICTS, one per garble, all measured at 600 dpi.

  1. "COUSE" at 023565.40 is a DECK TYPO.  Five letters stand where
     "CAUSE" needs five, so this is a SUBSTITUTION and pitch is not
     the test -- SHAPE is.  WIDTH IS NOT A DISCRIMINATOR HERE and
     saying so matters, because the obvious measurement misleads:
     the "A" of "CAUSE" two rows up is w51 and the disputed glyph is
     w52.  What separates them is the FORM.
       the disputed glyph  x4472-4523 y2870-2909 -- a CLOSED OVAL:
            continuous outline, no apex, no crossbar, an open counter
       "A" of "CAUSE" at 023564.40, TWO ROWS UP, x3446-3496 w51 -- a
            POINTED APEX with a crossbar and two open legs, in the
            SAME WORD spelled correctly on the same page
       "O" of "TO" on the SAME ROW, x4292-4342 w51 -- the same closed
            oval as the disputed glyph
       "A" of "FAIL" on the SAME ROW, x3998-4034 w37 -- the same
            pointed A, inked heavily enough to half-fill its counter,
            which is why it is 14 px narrower than the other As: that
            is what a struck-and-degraded CORRECT letter looks like,
            and the disputed glyph looks nothing like it
     A clean, correctly formed letter O where an A belongs, with the
     correct spelling of the same word two rows above.  Damage leaves
     a RAGGED A; this is a CLEAN WRONG LETTER.  docs/execution_
     operations.md sec.3.4 reported COUSE as the deck's typo; that is
     now measured rather than assumed.

  2. "-ILLEGAL OP CODE," at 023570.00 is ALSO A DECK TYPO -- a COMMA
     where this deck's other two copies of the identical comment
     print a PERIOD.  SHAPE FIRST, because the bounding box alone is
     ambiguous: this chain's COMMA is a rounded blob with a NOTCH
     bitten out of its LOWER LEFT and a tail descending from that
     notch past the baseline; its PERIOD is a plain round blob with
     neither.  The glyph at 023570.00 has the notch and the tail.
     Its per-scanline column extent at 600 dpi (row 30's cap height
     is y3462 and its baseline y3524, measured on an UNCLIPPED
     window -- an earlier window starting at y3480 clipped every
     letter top on the row and gave a cap height 18 px too low):
         y3479-3484   3, 3, 4, 8, 12, 13 px   a point, and NO GAP
         y3485-3500   17 rising to 25 px      the swell
         y3501-3502   27 px                   widest
         y3503-3516   25 falling to 17 px
         y3517-3523   16,16,17,16,15,15,15    the notch/tail
         y3524-3526   11, 8, 7 px at x3345-3351 -- the TAIL, pinned
                      to the LEFT edge, 2 px BELOW the baseline
     against the known COMMA of "-TEST 1D," on this page's row 1
     (cap y387, baseline y450, x2866-2893 = w28):
         y409-412     1, 2, 11, 14 px         the same point
         y420-432     26-28 px                widest
         y440         16 px                   THE NOTCH
         y441-444     18, 19, 20, 20 px       the tail
         y451-452     6, 4 px                 2 px below the baseline
     Same width (27 against 28), same bottom (baseline+2), same
     point-swell-notch-tail profile, and the ink grows MONOTONICALLY
     from a 3 px point with no gap, so it is ONE mark and not a
     period with a speck above it.  The only difference is that it
     starts 17 px below cap height where the comma starts 22, and is
     4 px taller -- strike variation, not a second glyph.
     The two PERIODS of the same comment, for contrast:
         p.92  023445.40  x3371-3401 w31, y1005-1037, ROUND, no
               notch, no tail, 20 px below cap height
         p.103 024003.00  x3384-3416 w33, y910-940, the same round
               period, also 20 px below cap height
     A period on this chain is 31-33 px wide and 31-36 px tall with
     no notch; this mark is 27 x 48 with one.  One clean comma
     against two clean periods of the identical comment: DECK TYPO.

  3. The second mark after "-UPDATE CONTINUITY CHECK." at 023575.00
     IS NOT A CHARACTER.  At 400 dpi the row reads "CHECK. ."  At
     600 dpi the real period is x3816-3845, 30x39 px, bottom on the
     baseline y4732; the second mark is x3942-3955, 14x15 px,
     FLOATING at y4713-4727, five px clear of the baseline, two pitch
     cells to the right.  Too small for this printer's period (30x39)
     and the wrong shape for its comma (28x44), and the same row
     carries another 4 px fleck at x2352-2355 in a blank cell.  SCAN
     SPECK.  NOT TRANSCRIBED.

  NO DROPPED AND NO ADDED LETTER IN THE RANGE.  The heading row is
  set on 60.57 px/cell at 600 dpi (hyphen x2370 to final period
  x4187 = 30 cells) and every glyph lands on its cell, so no word
  here is short or long of its pitch.  "CNTRLS" does not occur on
  this page.

BIT-18 SELF-CHECKS, decoded from the printed octal pair and matched
against the page's own label column.  Print format: bits 0-17 as six
octal digits, ".", bits 18-23 as two octal digits, bits 24-31 as two
hex digits -- so BIT 18 IS THE TOP BIT OF THE OCTAL PAIR.  FIVE
classes, FOUR reasons:

 (a) HALF-WORD SELECT, DECODABLE.  Branch targets, MISC addresses,
     the 19-bit DirIndex and ImmIndex address fields, and V+/KV.
     Reference Manual printed p.23 (PDF p.26), READ FIRST-HAND FOR
     THIS FILE (footer "Operand Designation  23"): "In the majority
     of these operations, 19 bits of the effective address are used
     in order to permit addressing of half-words."
       023556.00  LVI,$X1,I6243 -> 23563.43 01.  Pair 43 = 100011,
                  bit 18 = 1 -> 023563.40 = I6243.  IN-RANGE: EVIDENCE.
       023562.00  LVI,$X1,I6245 -> 23566.43 01.  Bit 18 = 1 ->
                  023566.40 = I6245.  IN-RANGE: evidence.
       023563.40  BUSA,I6244 -> 23565.50 C2.  Pair 50 = 101000,
                  bit 18 = 1 -> 023565.40 = I6244.  IN-RANGE, and on
                  an INDICATOR-BRANCH encoder, not an LVI.
       023566.40  LVI,$X1,I6246 -> 23571.03 01.  Pair 03, bit 18 = 0
                  -> 023571.00 = I6246.  IN-RANGE: THE CONTROL.
       023555.40  CB+,$X1,I6242 -> 23553.03 48.  Bit 18 = 0 ->
                  023553.00 = I6242.  IN-RANGE, a fourth encoder.
     So the block carries a MATCHED SET -- five in-range labels,
     three with bit 18 = 1 and two with bit 18 = 0, across four
     encoders.  That is what injection 2 below makes falsifiable.
       023553.40 / 023554.40  SVA,$X3,I6084A($X1) -> 17245.07 D1 and
                  SVA,$X3,I6084A+.32($X1) -> 17245.47 D1: the SAME
                  external label with bit 18 clear and set, so the
                  "+.32" is checked even though the label is a SYN.
       023552.40  LVI,$X3,I6084A+.32 -> 17245.47 01.  Same shape.
       023554.00 / 023555.00  V+I,$X3,(8)0.40 -> 0.47 05.  The
                  IMMEDIATE is 19 bits of a bit address too, so
                  0.40 octal = 32 bits = half-word 1 = bits 0-17 zero
                  with BIT 18 SET.  That is why both print "0.47".
       023573.00  BD,I6241 -> 23551.44 00, bit 18 = 1 -> 023551.40.
                  I6241 is the SLC ANCHOR, so this checks the SLC
                  against its own input: NOT evidence.
       self-relative, all decodable: 023565.00 B,$+1.32 -> 23566.50
                  (bit 18 = 1); 023567.40 BD,$+.32 -> 23570.04 (0);
                  023571.00 BEXEZ,$+1.32 -> 23572.51 (1); 023572.40
                  B,$+1.0 -> 23573.50 (1); 023574.40 BD,$+.32 ->
                  23575.04 (0).
       SYN-addressed rows in this class, which check every field but
                  the address: 023556.40, 023557.00, 023557.40,
                  023560.40, 023561.00, 023561.40, 023562.40,
                  023563.00, 023567.00, 023570.40, 023574.00,
                  023575.40.
 (b) LX and SX are EXCLUDED, and not for the reason (c)/(d)/(e) are.
     Reference Manual printed p.23 (PDF p.26), READ FIRST-HAND HERE:
     "The two exceptions use only 18 bits of the effective address
     because they require full-word operands", and the LX paragraph
     on the same page: "The index word specified by J is replaced by
     the full-word specified by bits 0-17 of the effective address."
     Five rows: 023551.40 (02 10), 023552.00 (04 10), 023553.00
     (05 11), 023575.00 (32 10), 023576.00 (33 10).  Bit 18 is not
     part of the address in any of them.
 (c) SIC is EXCLUDED because its operand is a 24-bit BIT address in
     bits 0-23, so the octal pair is a BIT OFFSET inside the word.
     Five rows: 023560.00, 023564.00, 023565.40, 023571.40 and
     023573.40.  The last makes the point -- "SIC,SEN0+.32" prints
     "1311.40 80" and the pair 40 is BIT 32 OF WORD 0o1311, not
     "bit 18 set".
 (d) TRANSMIT's A1 would be excluded for the same reason as (c).
     NO TRANSMIT OCCURS IN THIS RANGE; the class is named because
     verify_ax5b_162_test2cab_listing.py has one and the frame is
     shared.
 (e) EXIC is EXCLUDED because printed p.50 (PDF p.53) makes its
     operand an 18-bit WORD address.  READ FIRST-HAND FOR THIS FILE,
     the opening sentence of "Execute Indirect and Count (EXIC)":
     "Bits 0-18 of the full-word addressed by BITS 0-17 of the
     effective address are used as a pseudo-instruction counter."
     Against "Execute (EX)", three paragraphs earlier on the SAME
     PAGE: "BITS 0-18 of the effective address form the address of
     the location of a subject instruction that is fetched and
     executed."  EX is a 19-bit half-word address with bit 18 live;
     EXIC is an 18-bit word address and bit 18 is not in it.
     NO EXIC OCCURS IN THIS RANGE either.
     WHAT THIS BLOCK CANNOT SHOW ABOUT EX, said rather than implied:
     both EX rows here (023563.00, 023570.40) print pair 12, bit
     18 = 0, so TEST 1D does NOT witness EX's 19-bit operand.  TEST
     1CA does -- "EX,$-.32" at 023447.00 prints 23446.52, bit 18 = 1
     (verify_ax5b_162_test1cab_listing.py).

BRANCH POLARITY, DECIDED PER CHECK, NOT PER BLOCK.  enc_branch_ind
lays out addr19(0-18), indnum(19-24), the literal 1000(25-28),
clear(29), branchOn(30), idx(31), so hex bit 30 is the polarity and
hex bit 29 is the "...Z" reset suffix.  Two indicator branches here,
and they are NOT the shape TEST 1CB and TEST 2CB use:
  023563.40  BUSA,I6244 -> 23565.50 C2.  Hex C2 = 1100 0010 over
             bits 24-31: indnum = bits 19-24 = 010001 = 17 = USA;
             bit 29 = 0, do NOT reset; bit 30 = 1, BRANCH ON USA ON.
             Right: I6243 is reached when the chain ended without an
             interruption, and the two error reports are told apart
             by whether USA came on.  Leaving USA set is what lets
             the SERS report see it.
  023571.00  BEXEZ,$+1.32 -> 23572.51 46.  Hex 46 = 0100 0110:
             indnum = 010010 = 18 = EXE; bit 29 = 1, AND ZERO IT;
             bit 30 = 1, BRANCH ON EXE ON.  Taking the branch is the
             PASS and it clears EXE on the way out.
  The sibling's TEST 2CB has "BZXVZ,SERS" -> 1304.31 40, bit 30 = 0
  (branch-on-OFF), bit 29 = 0.  Injections 3 and 4 below move these
  rows in OPPOSITE directions, which is what makes the two bits
  independently measured rather than jointly assumed.

WITNESS TIERING.  EVERY SYN IN THE .strap IS AN INPUT, NOT A WITNESS
-- the caveat verify_ax5b_16082_16083_listing.py makes about I6088.
A SYN makes the address field come out right by construction.  I6241
IS NOT EVIDENCE EITHER: it is the first label after an SLC this same
transcription fed 023551.40, so checking it checks the SLC against
its own input; it is asserted as the anchor.
  GENUINE ADDRESS EVIDENCE: I6242, I6243, I6244, I6245, I6246 -- each
  the cumulative sizing of every half-word before it, each named by a
  row whose printed octal pair carries bit 18, across four encoders
  and both values of bit 18 -- plus the nine self-relative rows,
  which are arithmetic on the SLC rather than on a SYN.
  TIERS BELOW, AND NEITHER PROMOTES AN EXTERNAL: I62INT, I62ITE,
  I62K4 and IC262 are confirmed by separately read pages' own label
  columns (PDF pp.109/110/114, and verify_ax5b_162_test3b_listing.py
  for IC262 = 024171.00); BIT3 = 024525.00 by verify_ax5b_bit_table_
  listing.py; SEN, SERS, SEN0, SSW, I60SX1, I60S1 by other files
  here.  USAWD, I6084A, I6084B and I62B7 rest on NOTHING BUT THIS
  PAGE'S OWN MACHINE-CODE COLUMN.

NO CNOP AND NO SLC-ACROSS.  No CNOP occurs on PDF p.95, and every
printed location in the range carries machine code, so no row is
"location printed, no word" and nothing had to be SLC'd across or
left to a SYN for want of a datum.

FIRSTS: exactly TWO, and they survived a grep of every verify_*.py
and every programs/*.strap.
  * "SVA,$X3,I6084A($X1)" at 023553.40 (and its twin at 023554.40) is
    the repo's FIRST INDEX-MODIFIED SVA.  No other SVA anywhere here
    takes a parenthesised index; every one is a bare label with or
    without "+.32".
  * "BUSA,I6244" at 023563.40 is the repo's FIRST BRANCH ON USA
    WITHOUT THE RESET SUFFIX.  The only other indicator-17 branches
    are "BUSAZ,$+.32" (ax5b_160s1_tail.strap 023027.40,
    ssip_sip17_reset.strap 001602.40), both with the Z.  TEST 1D is
    therefore the first block in the repo to hold a clear=0/clear=1
    PAIR on indicator branches.
  NOT FIRSTS, each knocked down: index-modified SX (ax5b_160_test6
    "SX,$X2,I60IT($X1)"), V+I (five files), CB+ (eight), BEXEZ (three
    programs), EX (test1b/test1cc/test1cab), "B,$+1.32"
    (verify_pau_srte30_listing.py 023672.00, a different deck),
    "B,$+1.0" (test1cc, test3b), an octal "(8)..." immediate on an
    immediate-index op (test3b "KVI,$X13,(8)777000.0"), and the
    DD(BU,32,8),(8)3740 word (three files).

PROVEN DISCRIMINATING.  Eleven injections were run; the nine that
move a row in THIS file are listed below with the OBSERVED failing
rows.  Each was made with a WHOLE-LINE anchored edit that refuses
unless the anchor matches exactly once, each was CONFIRMED APPLIED by
printing the patched line with its line number BEFORE the run, each
run had __pycache__ removed on BOTH sides, each was reverted by
reversing the exact patch (never git checkout, per AGENTS.md rule 2)
and the file's md5 was checked back to its original.  The failure
sets are OBSERVED.

  1. strap_asm.enc_dir_index, (idx, 4) -> ((idx << 1) & 0xF, 4)
     (confirmed: line 340 read
      '    v, w = cat((addr19, 19), (j, 4), (code, 5), ((idx << 1) & 0xF, 4))')
       023553.00  SX,$X2,I6084A($X1)       -> "017245.05 12"  (3 rows)
       023553.40  SVA,$X3,I6084A($X1)      -> "017245.07 D2"
       023554.40  SVA,$X3,I6084A+.32($X1)  -> "017245.47 D2"
     THIS IS THE SIBLING'S MEASURED NULL TURNED INTO A HIT.
     verify_ax5b_162_test1cab_listing.py records exactly this patch as
     a null, because 1CA/1CB contain no parenthesised index at all and
     it had to prove liveness with a CONSTRUCTED row.  TEST 1D has
     three, and under the same build the same patch moves all three
     and nothing else.
  2. strap_asm's branch/misc address mask 0x7FFFF -> 0x7FFFE -- i.e.
     "a branch/MISC operand is an 18-bit word address like LX/SX"
     (confirmed: line 1428 read
      '            eval_addr_field(base, symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFE')
       023565.00  B,$+1.32 -> "023566.10 00"                  (3 rows)
       023572.40  B,$+1.0  -> "023573.10 00"
       023573.00  BD,I6241 -> "023551.04 00"
     Exactly the three branch/MISC rows whose bit 18 is set; the
     other eleven rows in the class, including BOTH EX rows, do not
     move, which is the measured form of "this block does not witness
     EX's bit 18".
  3. strap_asm.enc_branch_ind, branchOn -> 1 - branchOn
     (confirmed: line 355 read
      '    v, w = cat((addr19, 19), (indnum, 6), (0b1000, 4), (clear, 1), (1 - branchOn, 1), (idx, 1))')
       023563.40  BUSA,I6244   -> "023565.50 C0"              (2 rows)
       023571.00  BEXEZ,$+1.32 -> "023572.51 44"
     Both LOSE hex bit 30, i.e. both were branch-on-ON.  Under the
     same patched build the sibling's TEST 2CB row GAINS it
     (BZXVZ 40 -> 42), so the two polarities are separated by
     direction, not asserted.
  4. strap_asm.enc_branch_ind, clear -> 1 - clear
     (confirmed: line 355 read
      '    v, w = cat((addr19, 19), (indnum, 6), (0b1000, 4), (1 - clear, 1), (branchOn, 1), (idx, 1))')
       023563.40  BUSA,I6244   -> "023565.50 C6"              (2 rows)
       023571.00  BEXEZ,$+1.32 -> "023572.51 42"
     BUSA GAINS bit 29 and BEXEZ LOSES it, in one patch, which is the
     Z-suffix decision made falsifiable independently of injection 3.
  5. opcodes.MISC_CODES["EX"] 0b010 -> 0b110
     (confirmed: line 215 read '    "EX":  0b110,')
       023563.00  EX,I6084A -> "017245.32 00"                 (2 rows)
       023570.40  EX,I62B7  -> "024207.32 00"
     Both EX rows and nothing else in 42 half-words; the same patched
     build leaves verify_ax5b_162_test2cab_listing.py entirely green,
     so EX and EXIC are checked independently.
  6. opcodes.IMM_INDEX_CODES["V+I"] 0b0101 -> 0b0111
     (confirmed: line 130 read '    "V+I":    0b0111,')
       023554.00  V+I,$X3,(8)0.40 -> "000000.47 07"           (2 rows)
       023555.00  V+I,$X3,(8)0.40 -> "000000.47 07"
     Only the hex byte moves, so the immediate-index code is checked
     independently of the 19-bit value and of bit 18 -- and
     023575.40's "V+,$X13,BIT3", a DIRECT-index op with a confusable
     mnemonic, does NOT move.
  7. opcodes.CB_CODES["CB+"] (0b10, 0, 0) -> (0b11, 0, 0)
     (confirmed: line 183 read '    "CB+":     (0b11, 0, 0),')
       023555.40  CB+,$X1,I6242 -> "023553.03 C8"             (1 row)
     The block's only count-and-branch, and the "add one to value"
     field separated from the refill and branch-if-zero fields.
  8. opcodes.DIR_INDEX_CODES["SVA"] 0b11101 -> 0b11001
     (confirmed: line 115 read '    "SVA":  0b11001,')
       023553.40  SVA,$X3,I6084A($X1)      -> "017245.07 91"  (5 rows)
       023554.40  SVA,$X3,I6084A+.32($X1)  -> "017245.47 91"
       023556.40  SVA,$X1,I6084B           -> "021245.03 90"
       023562.40  SVA,$X1,I62ITE           -> "024320.03 90"
       023567.00  SVA,$X1,I62ITE           -> "024320.03 90"
     All five SVAs and only those; SV at 023557.40 and SX at
     023553.00, which share the encoder, do not move.
  9. strap_asm's INDICATOR-BRANCH address mask 0x7FFFF -> 0x7FFFE
     (a separate site from injection 2; confirmed: line 1501 read
      '        addr19 = eval_addr_field(base, symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFE'
      inside the classify_branch_indicator arm, with lines 1502-1503
      printed as the anchor's remaining two lines)
       023563.40  BUSA,I6244   -> "023565.10 C2"              (2 rows)
       023571.00  BEXEZ,$+1.32 -> "023572.11 46"
     The indicator-branch encoder's own 19-bit field, checked
     separately from the branch/MISC one.

A MEASURED NULL IN THE SIBLING, WITH THIS FILE AS THE LIVENESS PROOF.
Injections 1, 2, 5, 6, 7, 8 and 9 above were also run against
verify_ax5b_162_test2cab_listing.py; SIX of them -- 1, 2, 5, 6, 7 and
9 -- leave it green (8 is the exception: it moves four SVA rows
there).  Those six nulls are
MEASUREMENTS and not silently failed patches, because the SAME
patched build -- same run, same confirmed line -- moves the rows
listed above in THIS file.  No constructed case was needed.
Symmetrically, two injections are nulls HERE and hits there:
  N1. opcodes.MISC_CODES["EXIC"] 0b011 -> 0b111
      (confirmed: line 216 read '    "EXIC":0b111,')
        this file: ALL TESTS PASSED -- zero rows moved.
        LIVENESS: the same build moved 024006.40 and 024015.40 in
        verify_ax5b_162_test2cab_listing.py.  There is no EXIC in
        023551.40-023576.00, so this block cannot see the bug at all.
  N2. strap_asm.enc_transmit's literal (0b10, 2) -> (0b11, 2)
      (confirmed: line 384 read
       '               (1 if swap else 0, 1), (0b11, 2), (i2, 4))')
        this file: ALL TESTS PASSED -- zero rows moved.
        LIVENESS: the same build moved 024014.40 in the sibling.
        There is no TRANSMIT in this range.

WHAT THIS FILE CANNOT SEE, recorded rather than left.
  * USAWD, I6084A, I6084B and I62B7 are read ONLY from this page's
    machine-code column and appear nowhere else in this repo.  Their
    rows agree with the SYNs BY CONSTRUCTION.  The 2049 derivation
    rests on two of them.
  * I62B7's CONTENTS WERE NOT READ.  Half two's premise -- that the
    subject at 024207.00 is a BRANCH DISABLED -- rests on the deck's
    own error text.
  * USAWD's VALUE WAS NOT READ, so the loop count is not confirmed
    independently of the two chain endpoints.
  * WHAT THE 64-WORD INTERRUPT TABLE HOLDS WHEN 1D RUNS IS NOT READ.
    "SVA,$X1,I62ITE" with no "+.32" only works if the entry still
    holds I62K1 ("BD,I62ITE"); TEST 1CC's I6233 fill loop at
    023522.00 is upstream of here, which helps, but it is still a
    conjecture and is flagged as one.
  * THIS IS AN ENCODING ORACLE ONLY.  Nothing here was run on the
    Bluespec model, and nothing here shows that the model fires USA.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_162_test1d.strap").read())

ROWS = [
    # ---- half one: build the chain ----------------------------------
    ('023551.40', '23076.02 10',
     'I6241 LX,$X1,USAWD   (ext) "-TEST 1D, CHK EXE AND USA INDS."'),
    ('023552.00', '24175.04 10',
     'LX,$X2,I62K4         (ext) p.109 "I62K4 EX,$L" -- the template'),
    ('023552.40', '17245.47 01',
     'LVI,$X3,I6084A+.32   (ext) bit 18 = 1 -> 017245.40'),
    ('023553.00', '17245.05 11',
     'I6242 SX,$X2,I6084A($X1)   index-modified store'),
    ('023553.40', '17245.07 D1',
     'SVA,$X3,I6084A($X1)  bit 18 = 0; FIRST INDEX-MODIFIED SVA here'),
    ('023554.00', '0.47 05',
     'V+I,$X3,(8)0.40      bits 0-17 zero, BIT 18 SET = one half-word'),
    ('023554.40', '17245.47 D1',
     'SVA,$X3,I6084A+.32($X1)    bit 18 = 1: the matched pair'),
    ('023555.00', '0.47 05',
     'V+I,$X3,(8)0.40'),
    ('023555.40', '23553.03 48',
     'CB+,$X1,I6242        in-range label, bit 18 = 0 -> 023553.00'),
    ('023556.00', '23563.43 01',
     'LVI,$X1,I6243        in-range label, bit 18 = 1 -> 023563.40'),
    ('023556.40', '21245.03 D0',
     'SVA,$X1,I6084B       (ext) patch the chain\'s LAST link'),
    ('023557.00', '24220.03 01',
     'LVI,$X1,I62INT       (ext) the 64-word interrupt table'),
    ('023557.40', '2.03 30',
     'SV,$X1,$IA           word 2 = the interruption address register'),
    ('023560.00', '23041.00 80',
     'SIC,I60SX1           (ext) 1260\'s return link'),
    ('023560.40', '22741.10 00',
     'B,I60S1              (ext) NOTE "B", not "BD": code 0o10'),
    ('023561.00', '13.22 00',
     'Z,$IND               word 11 = 0o13'),
    ('023561.40', '14.22 00',
     'Z,$MASK              word 12 = 0o14: only 0-19 can interrupt'),
    ('023562.00', '23566.43 01',
     'LVI,$X1,I6245        in-range label, bit 18 = 1 -> 023566.40'),
    ('023562.40', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext) NO "+.32": the BD half of the landing'),
    ('023563.00', '17245.12 00',
     'EX,I6084A            (ext) THE TEST; bit 18 = 0 -> 017245.00'),
    ('023563.40', '23565.50 C2',
     'I6243 BUSA,I6244     bit 18 = 1 -> 023565.40; hex C2: USA ON, no reset'),
    ('023564.00', '1310.00 80',
     'SIC,SEN              (ext) "-2049 SUCCESSIVE EXECUTES FAIL TO SET"'),
    ('023564.40', '1304.04 00',
     'BD,SERS              (ext) "-USA AND FAIL TO CAUSE INTERRUPT."'),
    ('023565.00', '23566.50 00',
     'B,$+1.32             bit 18 = 1 -> 023566.40, past I6244'),
    ('023565.40', '1310.00 80',
     'I6244 SIC,SEN        (ext) "-2049 SUCCESSIVE EXECUTES FAIL TO COUSE"'),
    ('023566.00', '1304.10 00',
     'B,SERS               (ext) "-INT BUT DO SET USA."'),
    # ---- half two: EXE on an executed branch ------------------------
    ('023566.40', '23571.03 01',
     'I6245 LVI,$X1,I6246  in-range label, bit 18 = 0 -> 023571.00'),
    ('023567.00', '24320.03 D0',
     'SVA,$X1,I62ITE       (ext) replant the landing'),
    ('023567.40', '23570.04 00',
     'BD,$+.32             bit 18 = 0 -> 023570.00, the illegal word'),
    ('023570.00', '00000003740',
     'DD(BU,32,8),(8)3740  "-ILLEGAL OP CODE,"  COMMA: see the verdicts'),
    ('023570.40', '24207.12 00',
     'EX,I62B7             (ext) subject is a BD, per the error text'),
    ('023571.00', '23572.51 46',
     'I6246 BEXEZ,$+1.32   hex 46: EXE ON and ZERO IT; bit 18 = 1'),
    ('023571.40', '1310.00 80',
     'SIC,SEN              (ext) "-EX OF A BD FAILS"'),
    ('023572.00', '1304.10 00',
     'B,SERS               (ext) "-TO SET EXE IND."'),
    # ---- exit and continuity bridge ---------------------------------
    ('023572.40', '23573.50 00',
     'B,$+1.0              bit 18 = 1 -> 023573.40, past the restart'),
    ('023573.00', '23551.44 00',
     'BD,I6241             bit 18 = 1 -> 023551.40: the SLC ANCHOR'),
    ('023573.40', '1311.40 80',
     'SIC,SEN0+.32         (ext) pair 40 is BIT 32 of word 0o1311'),
    ('023574.00', '1301.10 00',
     'B,SSW                (ext) "-TO SSIP"  (no period: measured)'),
    ('023574.40', '23575.04 00',
     'BD,$+.32             bit 18 = 0 -> 023575.00'),
    ('023575.00', '24171.32 10',
     'LX,$X13,IC262        (ext) "-UPDATE CONTINUITY CHECK."'),
    ('023575.40', '24525.32 B0',
     'V+,$X13,BIT3         (ext) a DIRECT-index V+, not V+I'),
    ('023576.00', '24171.33 10',
     'SX,$X13,IC262        (ext) p.95\'s last printed row'),
]

# Only labels DEFINED inside the transcribed range belong here.  I6241
# is the SLC anchor, NOT evidence -- the SLC was fed 023551.40 by this
# same transcription.  I6242-I6246 are genuine witnesses: each is the
# cumulative sizing of every half-word before it, and each is named by
# a row whose printed octal pair carries bit 18, across four different
# encoders (CB+, LVI, indicator-branch, LVI).
SYMBOLS = {
    'I6241': '023551.40',
    'I6242': '023553.00',
    'I6243': '023563.40',
    'I6244': '023565.40',
    'I6245': '023566.40',
    'I6246': '023571.00',
}

finish(check_rows(prog, ROWS, SYMBOLS, label='1262 1D '))
