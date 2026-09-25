#!/usr/bin/env python3
"""verify_ax5b_160_test7_sweep_listing.py -- jb_ax5b "I-Box 5",
routine 1260 TEST 7's LAST BLOCK (programs/ax5b_160_test7_sweep.strap)
against the listing's own printed machine code, PDF p.74, octal
022461.00-022512.40.  50 rows occupying 52 half-words (two of the rows
are full-word TRANSMIT IMMEDIATEs).  (This deck's listing pages carry
NO printed page numbers -- cite by PDF page.)

THE PREMISE WAS CHECKED FIRST, and it held.  Before a line was
written, every strap/verify_*.py and programs/*.strap was grepped for
each octal address 022461 through 022512.  Eight of them hit
verify_ax5b_160_test7_compare_listing.py, and all eight are PROSE or
decode lines, never a ROWS entry: 022461 / 022506 / 022512 in its "THE
CUT POINT" paragraph and its SYN and bit-18 tables, and 022475 /
022477 / 022501 / 022503 / 022504 in its 0-31 carve-out analysis --
the paragraph that file itself fences as "about p.74, a page this file
reads but does NOT transcribe or check".  022471 hits four
verify_fp_arith_*.py files at an unrelated address in another program.
So the range was genuinely untranscribed, and TEST 7 is now covered
end to end by three non-overlapping files:

    ax5b_160105_compare.strap      p.71     022346.40-022401.00
    ax5b_160_test7_compare.strap   pp.72-73 022401.40-022460.40
    ax5b_160_test7_sweep.strap     p.74     022461.00-022512.40  THIS

THE CUT POINT.  022512.40 is the last row on p.74 and the last row of
TEST 7: the next label after it, at 022513.00, is I60123, which
verify_ax5b_160_test8b_listing.py already transcribes as the head of
TEST 8B.  Nothing of TEST 7 is left.

WHAT THE BLOCK COMPLETES.  pp.72-73 witnessed two cells of the
boundary-control truth table.  This page adds the other two, and the
control bit is switched inside the page:

  BC 1, comparand INSIDE  -> NO signal   (I60121, 022461.00-022470.00)
      022463.00  TI,1,BOUND1,3.0
      022465.00  LX,$X13,0($X2)  -FETCH FRM LB+1, UB-1, BC IS 1.
      022466.40  BZDFZ,I60212    branch on DF OFF is the OK path
      022467.00  SIC,SEN         -FETCH BETWEEN UB AND LB,
      022467.40  B,SERS          -BC 1, CAUSES DF TO SET.

  BC 0, comparand OUTSIDE -> NO signal   (I60212, 022472.40-022502.00)
      022474.40  TI,1,BOUND0,3.0
      022475.40  V+I,$X2,2.0       X2 := LB+3 = UB+1
      022477.00  LX,$X13,0($X2)    the UB+1 fetch
      022500.40  BZDFZ,I60214    branch on DF OFF is the OK path
      022501.00  SIC,SEN         -FETCH FROM UB+1, BC 0, CAUSES
      022501.40  B,SERS          -DF TO BE SET.

Together with p.71's "UB signals under BC 1" and p.73's "LB+1 signals
under BC 0", all four cells of (inside, outside) x (BC 0, BC 1) are
now checked by transcribed rows.  Reference Manual C22-6530-2 printed
p.31 (PDF p.34 of docs/22-6530-2_7030RefMan.pdf, re-read at 400 dpi
for this file; PDF page = printed page + 3), "Definition of Monitored
Area": "The boundary control bit, bit 57 of storage location 3,
determines which condition will cause an address monitoring signal.
When the boundary control bit is zero, a signal is obtained for a
comparand inside the specified area.  When the boundary control bit is
one, a signal is obtained for a comparand outside the specified area."

BRANCH POLARITY, DETERMINED FROM THESE ROWS, NOT ASSUMED.  B<IND>
branches when the indicator is ON, BZ<IND> when it is OFF, a trailing
Z clears it.  The two check triples in this block are
022466.40/022467.00/022467.40 and 022500.40/022501.00/022501.40.  In
both, the BRANCH is the OK path and the FALL-THROUGH is the SIC,SEN /
B,SERS error pair, so the message names the ANOMALY, not the
requirement: "-BC 1, CAUSES DF TO SET." is printed on the path taken
when DF WAS set and should not have been.  This is the pp.72-73 shape.
It is NOT routine 1274's shape (SIC,SEN first, branching TO SERS);
that was checked against these rows rather than assumed away.

THE ERROR MESSAGES AND HEADINGS, verbatim with their octal locations,
read at 600 dpi:

  022464.00  -RESTORE MY INT.
  022465.00  -FETCH FRM LB+1, UB-1, BC IS 1.
  022466.00  -RESTORE INT.
  022467.00  -FETCH BETWEEN UB AND LB,
  022467.40  -BC 1, CAUSES DF TO SET.
  022470.40  -RESTORE INT.
  022471.00  -FETCH BETWEEN UB AND LB, BC 1,
  022471.40  -CAUSES AD INTERRUPT, TESTING DONE.
  022476.00  -RESTORE MY INT.
  022500.00  -RESTORE INT.
  022501.00  -FETCH FROM UB+1, BC 0, CAUSES
  022501.40  -DF TO BE SET.
  022502.40  -RESTORE INT.
  022503.00  -FETCH FROM UB+1, BC 0, CAUSES AD
  022503.40  -INTERRUPT, TESTING DONE
  022504.40  -DONE ALL COMPS.
  022505.00  -YES
  022505.40  -NO
  022506.40  -CLR BOUNDS REG.
  022510.40  -TO SSIP.
  022511.40  -UPDATE CONTINUITY CHECK.

THREE QUIRKS IN THAT LIST.  (1) "FRM" for FROM at 022465.00 -- the
same garble pp.72-73 records at 022444.40 on the mirror-image row, so
it is the deck's habit and not a one-off.  (2) "-BC 1, CAUSES DF TO
SET." at 022467.40 against "-DF TO BE SET." at 022501.40: the deck
writes "TO SET" in one message and "TO BE SET" in its twin.  (3)
"-INTERRUPT, TESTING DONE" at 022503.40 carries NO terminating period
where its twin at 022471.40, "-CAUSES AD INTERRUPT, TESTING DONE.",
does.  That one was checked at 8x on the 600 dpi render rather than
inferred: the character cell after the final E is empty, and the
period on the twin line is a clear round blot at the same scale.

EVERY PRINTED LOCATION IN RANGE CARRIES MACHINE CODE.  No row on this
page prints a location with a blank code column, so nothing here
needed an SLC across a gap or a SYN stand-in for a fabricated word.

LETTER I VERSUS DIGIT 1 IS MEASUREMENT NOW, NOT HOUSE STYLE.  This
docstring used to read: "the leading glyph of every 160xxx label and
of IC260 is a bare vertical stroke, the same stroke this printer uses
for letter I.  Reading the 160xxx ones as digits, and IC260's as a
letter, is this project's standing convention (ax5b_16086,
ax5b_160102, ax5b_160_test6, _test8b, _test8c and the two adjacent
TEST 7 files all do it); no new convention is started here."  Reading
one bare stroke two ways was the tell.  At 600 dpi this chain's digit
1 has an upper-left flag and a base serif and measures 30-42 px; the
bare stroke measures 9-18; the populations do not overlap across
~16 000 glyphs, and fifteen same-row instances put both in one printed
token.  Every one of these leads is the LETTER I -- I60121, I6012A,
I60211, IC260 and the rest -- and the files named above carry the
corrected spellings too (docs/listing_typography.md).  The
letter-O-versus-digit-0 width
calibration for this printer (50-51 px against 44-45 px at 600 dpi,
established by verify_ax5b_160_test8b_listing.py from p.114) decides
nothing in this block: the only O/0 ambiguity in range is SEN0, whose
spelling is inherited from the adjacent file.

WITNESS TIERING.  Every SYN is an INPUT to this check, never a
witness -- but the tiers here are much sharper than a blanket
disclaimer, so they are named:

  (a) GENUINELY WITNESSED -- defined by a row INSIDE this range and
      referenced by another row inside it, so the check really tests
      address placement:
        I60121 022461.00   I6012A 022466.00   I60211 022470.40
        I60212 022472.40   I6021B 022500.00   I60213 022502.40
        I60214 022504.40   I60122 022506.40
      Seven of the eight are referenced by a row in range (I60211 is
      referenced by 022461.00's LVI; I60121 itself is referenced only
      from p.73, see (b)).

  (b) UPGRADED BY THIS PAGE, and this is the headline.
      verify_ax5b_160_test7_compare_listing.py had to SYN both
      "I60121 SYN,(8)22461.0" and "I60122 SYN,(8)22506.40" as pure
      inputs, decoded from the octal pairs of 022453.00 "B,I60121"
      (22461.10 00) and 022427.00 "B,I60122" (22506.50 00).  THIS page
      DEFINES both, at exactly those addresses.  The adjacent file's
      two assumptions are now witnessed, from the other side.

  (c) CORROBORATED INDEPENDENTLY, by a file that read a different
      page:
        I60105 022346.40 and I60106 022356.00 -- this page's
          022507.40 "BD,I60105" (22346.44 00) and 022506.00
          "BD,I60106" (22356.04 00) agree with
          verify_ax5b_160105_listing.py, which transcribes p.71 where
          both labels are DEFINED.
        IC260 022737.00 -- agrees with ax5b_160_test6 / _test8b /
          _test8c, which each derive it from their own continuity row.
        LBIT10 024534.00 -- agrees with ax5b_160_test8b's 600 dpi read
          of the p.114 constants block (BIT0 -> 024522.00, so
          BIT0 + 10 = 024534.00).
        I60107 022372.00 and I6010A 022371.40 -- both are DEFINED in
          p.71's transcribed range (verify_ax5b_160105_listing.py).
        BOUND0 023302.00 and BOUND1 023303.00 -- corroborated by the
          deck's own work area on PDF p.86, per the pp.72-73 file.

  (d) STILL PURE ASSUMPTION, and it is exactly four symbols: SEN
      001310.00, SERS 001304.00, SEN0 001311.00, SSW 001301.00 -- the
      SSIP entry points.  Each came from the octal pair of a row that
      names it, so each is itself a checkable claim, but nothing
      outside this deck's own print corroborates them.

BIT-18 SELF-CHECKS, one for every label-valued, self-relative or
half-word-address operand in the block, each decoded from the printed
octal pair and read back against the page's own label column.  Print
format: bits 0-17 as 6 octal digits, ".", bits 18-23 as 2 octal
digits, then bits 24-31 as 2 hex digits -- so BIT 18 IS THE TOP BIT OF
THE OCTAL PAIR, the half-word select.  "(int)" marks a label defined
INSIDE this range (a real address check); the rest are SYN inputs or
externals and verify only that the bit this file wrote back is the bit
the page printed.

  022461.00  LVI,$X13,I60211  22470.73 01  73 -> 1 -> 022470.40 = I60211 (int)
  022461.40  SVA,$X13,I60107  22372.33 D0  33 -> 0 -> 022372.00 = I60107
  022462.00  LVI,$X3,I6012A   22466.07 01  07 -> 0 -> 022466.00 = I6012A (int)
  022462.40  SVA,$X3,I6010A   22371.47 D0  47 -> 1 -> 022371.40 = I6010A
  022463.00  TI,1,BOUND1,3.0  ...000003.02 A0  A2's pair 02 -> 0 -> 000003.00
             (A1's pair is EXCLUDED -- see below)
  022464.40  BE,$+.32         22465.00 00  00 -> 0 -> 022465.00
  022465.40  BD,$+.32         22466.04 00  04 -> 0 -> 022466.00
  022466.40  BZDFZ,I60212     22472.52 44  52 -> 1 -> 022472.40 = I60212 (int)
  022467.40  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022470.00  B,I60212         22472.50 00  50 -> 1 -> 022472.40 = I60212 (int)
  022471.40  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022472.00  B,I60122         22506.50 00  50 -> 1 -> 022506.40 = I60122 (int)
  022472.40  LVI,$X13,I60213  22502.73 01  73 -> 1 -> 022502.40 = I60213 (int)
  022473.00  SVA,$X13,I60107  22372.33 D0  33 -> 0 -> 022372.00 = I60107
  022473.40  LVI,$X3,I6021B   22500.07 01  07 -> 0 -> 022500.00 = I6021B (int)
  022474.00  SVA,$X3,I6010A   22371.47 D0  47 -> 1 -> 022371.40 = I6010A
  022474.40  TI,1,BOUND0,3.0  ...000003.02 A0  A2's pair 02 -> 0 -> 000003.00
  022476.40  BE,$+.32         22477.00 00  00 -> 0 -> 022477.00
  022477.40  BD,$+.32         22500.04 00  04 -> 0 -> 022500.00
  022500.40  BZDFZ,I60214     22504.52 44  52 -> 1 -> 022504.40 = I60214 (int)
  022501.40  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022502.00  BD,I60214        22504.44 00  44 -> 1 -> 022504.40 = I60214 (int)
  022503.40  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022504.00  B,I60122         22506.50 00  50 -> 1 -> 022506.40 = I60122 (int)
  022504.40  LV,$X2,$X2       22.04 30     04 -> 0 -> 000022.00 = $X2's own
             storage word.  Not a label: index registers X1-X15 ARE
             storage locations 17-31 (Reference Manual printed p.20),
             so $X2 = word 16+2 = 0o22, and the operand is the
             register's own word.  Listed here because its pair is a
             half-word select like any other and it decodes.
  022505.00  BXVZ,I60122      22506.71 42  71 -> 1 -> 022506.40 = I60122 (int)
  022506.00  BD,I60106        22356.04 00  04 -> 0 -> 022356.00 = I60106
  022507.00  B,$+1.0          22510.10 00  10 -> 0 -> 022510.00
  022507.40  BD,I60105        22346.44 00  44 -> 1 -> 022346.40 = I60105
  022510.40  B,SSW            1301.10 00   10 -> 0 -> 001301.00 = SSW
  022511.00  BD,$+.32         22511.44 00  44 -> 1 -> 022511.40
  022511.40  LX,$X13,IC260    22737.32 10  32 -> 0 -> 022737.00 = IC260
  022512.00  V+,$X13,BIT10    24534.32 B0  32 -> 0 -> 024534.00 = BIT10
  022512.40  SX,$X13,IC260    22737.33 10  33 -> 0 -> 022737.00 = IC260

Thirty-four entries.  The other sixteen rows split two ways.

EXCLUDED BECAUSE THE OPERAND IS A BIT ADDRESS, and therefore its
octal pair is a BIT OFFSET INSIDE THE WORD, not a half-word select --
one principle, two mnemonics.  SIC's operand is a 24-bit bit address,
and so is TRANSMIT's A1 (strap_asm.py evaluates it ">>0, like SIC's
and BRANCH ON BIT's B", against A2 which is a half-word address).
  * the four "SIC,SEN" rows (022467.00, 022471.00, 022501.00,
    022503.00) print 1310.00 80 -- bit offset 0 of word 001310.
  * "SIC,SEN0+.32" at 022510.00 prints 1311.40 80: the 40 is octal 40
    = 32 decimal = bit 32 of word 001311, the same place the source's
    decimal ".32" names.  Applying the bit-18 rule to it would read 1
    and mean nothing.
  * the two TI rows are the place where BOTH scalings appear in one
    printed row: 022463.00's "23303.00 80 000003.02 A0" has a
    BIT-offset pair 00 in its first half-word (A1 = BOUND1 =
    023303.00, bit 0) and a HALF-WORD select pair 02 in its second
    (A2 = 3.0, bit 18 = 0 -> 000003.00).  Only the A2 half is in the
    table above.

CARRYING NO HALF-WORD SELECT TO CHECK -- eleven rows whose operand is
a special register, an absolute constant or an indexed zero:
  022464.00 and 022476.00  SR,$X1,$IA      2.03 70   ($IA = word 2)
  022466.00, 022470.40, 022500.00, 022502.40  SV,$X1,$IA   2.03 30
  022465.00 and 022477.00  LX,$X13,0($X2)  0.32 12   (address 0)
  022475.40  V+I,$X2,2.0   2.05 05   a word-count immediate
  022505.40  V-I,$X2,2.0   2.05 0D   likewise
  022506.40  Z,3.0         3.22 00   absolute word 3
34 + 5 + 11 = 50, the whole block.

ALSO NOT A HALF-WORD SELECT: the two columns print the same quantity
in different radixes.  The location column's "022511.00" plus the
source's "$+.32" (decimal 32 bits) lands at 022511.40, and the row
prints 22511.44 00 -- pair 44, bit 18 = 1 -> 022511.40.  0o40 = 32.

THE ONE ANALYSIS THIS BLOCK WAS COMMISSIONED TO SETTLE, and it does
settle it, in three parts.  The pp.72-73 file worked out, from pages
it read but did not transcribe, that the sweep walks the lower bound
UP one word per pass and ends when LB+3 overflows the 24-bit value
field to zero -- and that on the last pass "V+I,$X2,2.0" at 022475.40
carries X2 to 2**24 bits, which wraps to zero, so the UB+1 fetch at
022477.00 reads WORD 0.  Both addresses are in range and both rows are
now checked bit-exactly.

PART 1 -- THE CITATION NAMED THE RULE FOR THE WRONG STEP.  The
pp.72-73 file wrote: '("this overflow bit ... is ignored", Reference
Manual p.21)'.  Printed p.21 was read first-hand (PDF p.24) and does
not contain that sentence.  The sentence is real, but it is on printed
p.20 (PDF p.23), under "Address Modification", and it governs a
DIFFERENT step: "In the addition of index and instruction address, an
overflow bit may be produced.  This overflow bit, which is a carry
produced in the high-order bit position, is ignored."  That rule
applies to the "0($X2)" at 022477.00 -- adding X2's value to the
instruction's address part -- not to the V+I at 022475.40 that
PRODUCES the zero.  The rule for the V+I step is on printed p.24 (PDF
p.27), in the PROGRAMMING NOTES that close "Direct Index Arithmetic":
"The overflow which may occur in index arithmetic is ignored."  So the
conclusion stands and the citation should be printed p.24.

THE ONE SCOPE GAP IN THAT CITATION, stated rather than glossed.  V+I
is IMMEDIATE index arithmetic, and the sentence just quoted closes the
DIRECT subsection.  Printed p.25 (PDF p.28), where V+I is actually
defined, was read to settle it and does NOT restate an overflow rule:
"Add Immediate to Value (V+I).  The address part, bits 0-18, of the
instruction is added to bits 0-18 of the value field of the index word
specified by J.  Zeros are added to bits 19-24 of the value field.
Addition is algebraic, taking into account the sign, bit 24, of the
value field."  (That also confirms the scaling used above: the "2.0"
immediate occupies bits 0-18 as 4 half-words, which lands on the
magnitude as 4 << 5 = 128 bits.)  p.24's note is then the ONLY
overflow statement anywhere in the Index Arithmetic chapter (printed
pp.22-28); it says "index arithmetic" with no qualifier, and the
chapter it sits in is headed "Index Arithmetic" with Direct and
Immediate as its two subsections.  The general reading is the one
taken here.  Two things support it and neither is proof: a 25th
magnitude bit has no home in a bits-0-24 value field, and none of the
eight index indicators listed on printed p.23 (XF, XCZ, XVLZ, XVZ,
XVGZ, XL, XE, XH) is an overflow indicator, so there is nowhere else
for the carry to go.  This is the residual uncertainty in Part 2 and
it is flagged as such rather than elided.

(A project-wide note: bsv/StretchExecute.bsv's comment at the
address-modification helpers also says "p.21" for the p.20 sentence.
That is a one-page slip in a comment about the RIGHT rule for the
RIGHT step; only the pp.72-73 use of it crosses into the wrong step.)

PART 2 -- THE WRAP IS REAL, AND IT IS THE LOOP'S TERMINATION
CONDITION, not an incidental curiosity.  The arithmetic, from rows
this project has transcribed in all three files:
  p.71  022362.00/022362.40  LB := X2, then 022363.00 V+I,$X2,2.0 and
        022363.40/022364.00  UB := X2, so UB = LB+2 and X2 = UB.
  p.72  022405.40 V-I,$X2,1.0 -> UB-1; 022420.40 V-I,$X2,2.0 -> LB-1.
  p.73  022443.40 V+I,$X2,2.0 -> LB+1.
  p.74  022475.40 V+I,$X2,2.0 -> LB+3 = UB+1;
        022505.40 V-I,$X2,2.0 -> LB+1, which is the next pass's LB.
So the lower bound rises by exactly one word per pass, and at I60214
X2 holds LB+3.  The index word's value field is bits 0-24 (Reference
Manual printed p.22's index-word diagram and printed p.21, "the value
field, bits 0-24 of the index specified by I"), sign-magnitude with
bit 24 the sign (printed p.24, COMPARE VALUE: "Comparison is
algebraic, taking into account the sign, bit 24, of both addresses.
Positive and negative zero are considered equal."), so the magnitude
is the 24 bits 0-23.  On the last pass LB = 0o777775, X2 before the
V+I is (LB+1)*64 = (2**18 - 2)*64 = 2**24 - 128 bits, and adding 2.0 =
128 bits gives exactly 2**24: a carry out of bit 0, ignored by printed
p.24, leaving magnitude 0 and the sign unchanged.  Value field zero
sets XVZ -- printed p.23: "Index Value Zero (XVZ).  This indicator is
set to one when the value field is zero." -- and 022505.00's
"BXVZ,I60122" takes the exit.  That is the ONLY way this loop ends.
022504.40's "LV,$X2,$X2" is there precisely to re-derive XVZ from X2,
because every row between the V+I and it loads or stores X13, not X2:
printed p.23, "Load Value (LV).  The value field, bits 0-24, of the
index word specified by J is replaced by bits 0-24 of the half-word
specified by bits 0-18 of the effective address", and "The index
result indicators are set in all cases in which the index flag
indicator is set, except the index comparison operations."  It also
confirms the p.71 header's upper endpoint exactly: X = UB = 0o777777,
"RANGE OF X IS ... THRU 777777 OCTAL".

PART 3 -- IT STILL DECIDES NOTHING ABOUT THE 0-31 CARVE-OUT, and
saying so is the point.  On that last pass the fetch at 022477.00
reads word 0.  Printed p.31, read first-hand: "References to locations
0 and 4 through 31, inclusive, never cause an address monitoring
signal."  So word 0 never signals under EITHER control-bit setting.
The deck's expectation on that row is "no signal" anyway -- boundary
control is 0 and UB+1 is outside the area, so no signal either way.
The two readings agree; the row discriminates nothing, and this deck
neither confirms nor refutes the carve-out.

PART 2 IS ANALYSIS, FENCED LIKE THE pp.72-73 FILE FENCED ITS OWN.  The
ALL TESTS PASSED line below checks BITS -- that the rows as printed
assemble to the codes as printed.  It does not execute the loop.  The
overflow story is derived from those rows plus the four primary-source
quotations above, all read first-hand at 400 dpi from
docs/22-6530-2_7030RefMan.pdf (printed pp.20, 21, 22, 23, 24, 31 =
PDF pp.23, 24, 25, 26, 27, 34).  It is not asserted by a row of the
table below.

NO MNEMONIC HERE IS A FIRST FOR THE REPO, and the claim was knocked
down rather than made.  All eighteen mnemonics in the block were
grepped across every other verify_*.py: LVI 21 files, SVA 20, TI 8,
SR 17, BE 17, LX 51, BD 73, SV 31, BZDFZ 2, SIC 134, B 119, V+I 11,
LV 24, BXVZ 14, V-I 2, Z 133, SX 36, V+ 20.  Every one appears in at
least two other files.  "Z,3.0" is not new either
(verify_ax5b_162_test1cc_listing.py has it).  What IS new is an
IDIOM, not a mnemonic: "LV,$X2,$X2", loading an index register's value
field from the register's own storage word purely to set XVZ, appears
nowhere else in the repo as an assembled row -- a regex over every
verify_*.py and programs/*.strap for LV,$Xn,$Xn found exactly one
other hit, and it is the pp.72-73 docstring's prose quotation of this
very page.

PROVEN DISCRIMINATING.  Observed failure sets -- the rows that were
actually seen to fail, never predicted -- each measured with
"rm -rf __pycache__" run on BOTH sides of the injection (stale
bytecode has replayed a previous injection's answer in this project
before and produced a false result), and the working tree confirmed
clean of assembler edits afterwards.  The first four move the printed
OCTAL PAIR (bit 18); the rest move the printed HEX BYTE or the
modifier bits.

  strap_asm.py, the UNCONDITIONAL-BRANCH/MISC path's addr19 mask,
  0x7FFFF -> 0x7FFFE (bit 18 forced to zero)
      022470.00, 022472.00, 022502.00, 022504.00, 022507.40,
      022511.00                                             (6 rows)
  strap_asm.py, the BRANCH-ON-INDICATOR path's addr19 mask, same
      022466.40, 022500.40, 022505.00                       (3 rows)
  strap_asm.py, the DIRECT-INDEX path's addr19 mask, same
      022462.40, 022474.00                                  (2 rows)
  strap_asm.py, the IMMEDIATE-INDEX path's imm19 mask, same
      022461.00, 022472.40                                  (2 rows)
  opcodes.DIR_INDEX_CODES["SVA"] 0b11101 -> 0b11100
      022461.40, 022462.40, 022473.00, 022474.00            (4 rows)
  opcodes.DIR_INDEX_CODES["LV"] 0b00011 -> 0b00010
      022504.40                                             (1 row)
  opcodes.DIR_INDEX_CODES["V+"] 0b01011 -> 0b01010
      022512.00                                             (1 row)
  opcodes.TRANSMIT_CODES["TI"] (0,1,0) -> (0,0,0)
      022463.00, 022474.40   (the two TI rows)              (2 rows)
  opcodes.INDICATOR_BITS["DF"] 20 -> 22
      022466.40, 022500.40                                  (2 rows)
  opcodes.INDICATOR_BITS["XVZ"] 50 -> 47
      022505.00                                             (1 row)
  opcodes.IMM_INDEX_CODES["V+I"] 0b0101 -> 0b0100
      022475.40                                             (1 row)

The four mask injections together are what turns the bit-18 table
above from hand-decoding ASSERTED into hand-decoding WITNESSED, and
they partition cleanly: thirteen rows in this block carry a half-word
select with bit 18 set, and those thirteen are exactly the union of
the four sets, with every .00 target left untouched.  Four different
assembler code paths, four disjoint row sets, one half-word select.
FOURTEEN rows print an octal pair with its top bit set; the
fourteenth is 022510.00's "1311.40 80", and the masks leave it
untouched because its 40 is a BIT OFFSET (octal 40 = bit 32), not a
half-word select.  That is the exclusion section's thesis measured
rather than argued.

MEASURED NULLS, with the arithmetic reason -- a measured null is a
real result:

  opcodes.INDICATOR_BITS["DS"] 19 -> 18            0 rows.
      DS is indicator 19.  The only branch-on-indicator mnemonics in
      022461.00-022512.40 are BZDFZ and BXVZ, so no row's indicator
      field carries 19.
  opcodes.MODE_DEFAULT_BS["BU"] 8 -> 4             0 rows.
      That default byte size is consulted only when a VFL data
      description is assembled.  This block has no VFL row; the two
      full-word rows are TRANSMITs, whose second half-word is an
      address and a count, not a data description.
  opcodes.IMM_INDEX_CODES["LCI"] 0b0010 -> 0b1011  0 rows.
      The immediate index operations used here are LVI, V+I and V-I.
      LCI does not appear, so the four bits it names are never
      deposited.

ONE ROW SHAPE WORTH NAMING, AND A CLAIM ABOUT IT THAT DID NOT
SURVIVE.  022463.00's "TI,1,BOUND1,3.0" is a FULL WORD at an EVEN
half-word, where every TRANSMIT IMMEDIATE in pp.71-73 sits at a .40
and straddles a word boundary (022365.40, 022402.40, 022417.40,
022442.40).  It was tempting to call that a first, and it is not: a
regex over every other verify_*.py for a .00 location with a
four-token printed code found 356 even-aligned full-word rows, TIs
among them -- verify_ax5b_160_test6_listing.py alone has ten
(022063.00, 022074.00, 022106.00, 022112.00, 022117.00, 022124.00,
022130.00, 022137.00, 022143.00, 022172.00, ...) in this very
routine's family.  So: this is the first even-aligned TI in the
pp.71-74 TEST 7 range, nothing more, and the block exercises both
alignments (022463.00 even, 022474.40 odd) with both checked below.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_160_test7_sweep.strap").read())

ROWS = [
    # ---- I60121: fetch between the bounds, boundary control 1 -------
    ('022461.00', '22470.73 01',
     'I60121 LVI,$X13,I60211  INTERNAL label -- real address check'),
    ('022461.40', '22372.33 D0',
     'SVA,$X13,I60107       (ext) plant the AD handler'),
    ('022462.00', '22466.07 01',
     'LVI,$X3,I6012A         INTERNAL label -- real address check'),
    ('022462.40', '22371.47 D0',
     'SVA,$X3,I6010A        (ext) plant the non-AD handler'),
    ('022463.00', '23303.00 80 000003.02 A0',
     'TI,1,BOUND1,3.0         FULL WORD at an EVEN half-word: BC = 1'),
    ('022464.00', '2.03 70',
     'SR,$X1,$IA             "-RESTORE MY INT."'),
    ('022464.40', '22465.00 00',
     'BE,$+.32                enable'),
    ('022465.00', '0.32 12',
     'LX,$X13,0($X2)         "-FETCH FRM LB+1, UB-1, BC IS 1." INSIDE'),
    ('022465.40', '22466.04 00',
     'BD,$+.32'),
    ('022466.00', '2.03 30',
     'I6012A SV,$X1,$IA     "-RESTORE INT."'),
    ('022466.40', '22472.52 44',
     'BZDFZ,I60212           DF OFF is the OK path -- BC 1, INSIDE'),
    ('022467.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH BETWEEN UB AND LB,"'),
    ('022467.40', '1304.10 00',
     'B,SERS                 (ext) "-BC 1, CAUSES DF TO SET."'),
    ('022470.00', '22472.50 00',
     'B,I60212               INTERNAL label -- real address check'),
    # ---- I60211: the AD landing for that fetch ----------------------
    ('022470.40', '2.03 30',
     'I60211 SV,$X1,$IA     "-RESTORE INT."'),
    ('022471.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH BETWEEN UB AND LB, BC 1,"'),
    ('022471.40', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES AD INTERRUPT, TESTING DONE."'),
    ('022472.00', '22506.50 00',
     'B,I60122               INTERNAL (defined at 022506.40 below)'),
    # ---- I60212: the UB+1 fetch, boundary control 0 -----------------
    ('022472.40', '22502.73 01',
     'I60212 LVI,$X13,I60213  INTERNAL label -- real address check'),
    ('022473.00', '22372.33 D0',
     'SVA,$X13,I60107       (ext)'),
    ('022473.40', '22500.07 01',
     'LVI,$X3,I6021B         INTERNAL label -- real address check'),
    ('022474.00', '22371.47 D0',
     'SVA,$X3,I6010A        (ext)'),
    ('022474.40', '23302.00 80 000003.02 A0',
     'TI,1,BOUND0,3.0         THE CONTROL BIT FLIPS: BOUND0 has BC = 0'),
    ('022475.40', '2.05 05',
     'V+I,$X2,2.0             X2 := LB+3 = UB+1 -- see the docstring'),
    ('022476.00', '2.03 70',
     'SR,$X1,$IA             "-RESTORE MY INT."'),
    ('022476.40', '22477.00 00',
     'BE,$+.32                enable'),
    ('022477.00', '0.32 12',
     'LX,$X13,0($X2)          the UB+1 fetch -- OUTSIDE, BC 0'),
    ('022477.40', '22500.04 00',
     'BD,$+.32'),
    ('022500.00', '2.03 30',
     'I6021B SV,$X1,$IA     "-RESTORE INT."'),
    ('022500.40', '22504.52 44',
     'BZDFZ,I60214           DF OFF is the OK path -- BC 0, OUTSIDE'),
    ('022501.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH FROM UB+1, BC 0, CAUSES"'),
    ('022501.40', '1304.10 00',
     'B,SERS                 (ext) "-DF TO BE SET."'),
    ('022502.00', '22504.44 00',
     'BD,I60214              INTERNAL label -- real address check'),
    # ---- I60213: the AD landing for the UB+1 fetch ------------------
    ('022502.40', '2.03 30',
     'I60213 SV,$X1,$IA     "-RESTORE INT."'),
    ('022503.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH FROM UB+1, BC 0, CAUSES AD"'),
    ('022503.40', '1304.10 00',
     'B,SERS                 (ext) "-INTERRUPT, TESTING DONE" NO PERIOD'),
    ('022504.00', '22506.50 00',
     'B,I60122               INTERNAL (defined at 022506.40 below)'),
    # ---- I60214: the sweep teardown ---------------------------------
    ('022504.40', '22.04 30',
     'I60214 LV,$X2,$X2     "-DONE ALL COMPS."  sets XVZ from X2'),
    ('022505.00', '22506.71 42',
     'BXVZ,I60122           "-YES"  INTERNAL -- real address check'),
    ('022505.40', '2.05 0D',
     'V-I,$X2,2.0            "-NO"   X2 := LB+1 for the next pass'),
    ('022506.00', '22356.04 00',
     'BD,I60106             (ext) round again -- 022356.00, p.71'),
    # ---- I60122: the TEST 7 exit ------------------------------------
    ('022506.40', '3.22 00',
     'I60122 Z,3.0          "-CLR BOUNDS REG."'),
    ('022507.00', '22510.10 00',
     'B,$+1.0'),
    ('022507.40', '22346.44 00',
     'BD,I60105             (ext) the routine head -- 022346.40, p.71'),
    ('022510.00', '1311.40 80',
     'SIC,SEN0+.32           (ext) BIT address: 0o40 = bit 32'),
    ('022510.40', '1301.10 00',
     'B,SSW                  (ext) "-TO SSIP."'),
    ('022511.00', '22511.44 00',
     'BD,$+.32'),
    ('022511.40', '22737.32 10',
     'LX,$X13,IC260         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('022512.00', '24534.32 B0',
     'V+,$X13,LBIT10         (ext) TEST 7 done = bit 10'),
    ('022512.40', '22737.33 10',
     'SX,$X13,IC260         (ext)'),
]

SYMBOLS = {'I60121': '022461.00', 'I6012A': '022466.00',
           'I60211': '022470.40', 'I60212': '022472.40',
           'I6021B': '022500.00', 'I60213': '022502.40',
           'I60214': '022504.40', 'I60122': '022506.40'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 T7 swp '))
