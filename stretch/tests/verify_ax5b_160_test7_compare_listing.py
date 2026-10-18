#!/usr/bin/env python3
"""verify_ax5b_160_test7_compare_listing.py -- jb_ax5b "I-Box 5",
routine 1260 TEST 7's COMPARISON test
(../decks/ax5b_160_test7_compare.strap) against the listing's own
printed machine code, PDF pp.72-73, octal 022401.40-022460.40.  92
rows, one unbroken run across a page break; the block occupies 95
half-words because three of the rows are full-word TRANSMIT
IMMEDIATEs.  (This deck's listing pages carry NO printed page numbers
-- cite by PDF page.)

WHY pp.72-73 AND NOT p.71.  The work order named PDF p.71.  p.71 is
already in the repo and already green: ../decks/ax5b_160105_compare.
strap covers 022346.40-022401.00, every row, and
verify_ax5b_160105_listing.py prints ALL TESTS PASSED for it,
including the two rows the order quoted as evidence the block was
untouched (022371.40 "I6010A BD,$+.32  -ALL INTRPTS EXCEPT AD ENTER
HERE." and 022372.00 "I60107 BD,$+.32  -AD INTRPTS ENTER HERE.").  A
second file on the same octal range would be duplicated coverage, so
this one takes the UNCOVERED remainder instead -- which is where the
COMPARISON's verdict is actually checked and where every error message
lives.  p.74 (022461.00-022512.40) remains; see THE CUT POINT below.

THE HEADER, read at 600 dpi, on p.71 at 022346.40-022351.00:

    I60105 LX,$X1,I60XW1   -TEST THE COMPARE CKTS, SETUP
           LX,$X2,I60K12   -INTERRUPT TAFLE. UB HAS X, LB HAS
           SX,$X2,I60IT($X1) -X-2. TETCH FROM X+1 TO CHK YB COMP,
           CB+,$X1,$-.32   -FROM X-3 TO CHK LB COMP, AND FROM
           LVI,$X1,INT     -X-1 TO CHECK WITHIN. RANGE OF X IS
           LX,$X2,I60XW3   -FROM 000040 THRU 777777 OCTAL.

ALL THREE GARBLES ARE DECK TYPOS, NOT SCAN DAMAGE, and each was
measured against a correct instance of the same letter on the same or
adjacent line at 600 dpi:

  * TAFLE (for TABLE), 022347.00.  The third glyph is a crisp F: a
    full top bar, a full mid bar, and NO trace of either of B's bowls
    or of the vertical that closes them.  The same line prints a clean
    two-bowled B nine characters later in "UB HAS X".  Ink loss would
    leave a ragged B; this is a well-formed wrong letter.
  * TETCH (for FETCH), 022347.40.  The first glyph's stem is CENTRED
    under its top bar (bar 75-425 px in the 8x crop, stem 210-300,
    both centres at ~250) and there is no mid bar at all.  An F on
    this printer puts its stem at the LEFT end of the bar and carries
    a mid bar -- see "FROM" four characters later on the same line.
    The form's dashed rule runs through the top of this text row and
    merges with the bars, but a rule cannot move a stem to the middle
    of a letter nor delete a mid bar.
  * YB (for UB), 022347.40.  Two straight diagonal arms meeting a
    short central stem: a Y.  U on this printer has parallel verticals
    and a round bottom -- "UB HAS X" one line above.  U and Y are
    adjacent keys on the 026 keypunch (Y U I), the only one of the
    three garbles with an obvious mechanism.

The same deck habit continues inside the transcribed range: FITCH for
FETCH at 022432.40 (bare vertical stroke, identical to the I in "TIME"
three words earlier; and "FETCH FROM LB-1" is spelled correctly one
line above in the SAME message), FRM for FROM at 022444.40, and "-TO
SSIP" at 022434.40 with no period where 022457.00 has one.  PDF p.85
carries another in the same style, "-UNABLE OT CLR OP OR ABOVE IND."
NOTHING in this block is scan damage; every garble measured is a
cleanly formed wrong (or missing) character.

LETTER I VERSUS DIGIT 1 IS SEPARABLE ON THIS PRINTER, and this
docstring used to say it was not.  It read: "the leading character of
every 160xxx label here is a bare vertical stroke, the same stroke the
printer uses for the letter I; compare '160110' with 'INT' on the same
line.  Reading them as digits is this project's standing house
convention (ax5b_16086, ax5b_160102, ax5b_160_test8b all do it), NOT a
measurement."  The observation was right and the inference backwards.
"I60110 Z,$X13 -CLR INT 1." at 022401.40 was re-measured at 600 dpi
for docs/listing_typography.md: the label's lead is 12 px and the I of
INT is 15, both bare strokes -- but the label's 4th and 5th characters
are 38 and 36 px and the comment's own trailing "1" is 36, each with
the flag and base serif the bare stroke lacks.  The two glyphs are in
that one printed row, and across both decks they never overlap.  So
the labels here are I60110, I6011A, I60210 and the rest, and the three
files named above have been corrected with this one.  The other
measurement this block quotes is unchanged: the
letter-O-versus-digit-0 calibration for this printer is
50-51 px for a letter O against 44-45 px for a digit zero at 600 dpi
(verify_ax5b_160_test8b_listing.py established it from the p.114
constants block); nothing in THIS block turns on it, because the only
O/0 ambiguity in range is SEN0, whose name is inherited from
verify_ax5b_160_test8c_listing.py and which is a SYN whose address
came from the very row that names it.

WHAT THIS BLOCK PROVES, AND IT IS THE HALF-OPEN INTERVAL.  The driver
on p.71 plants LB = L, UB = L+2 with the boundary control bit ONE
("signal for a comparand OUTSIDE the area") and fetches from UB
itself, expecting a signal.  The first half of THIS block fetches from
UB-1 under the same control bit and demands NO signal:

  022410.40  BZDFZ,I60111      branch on DF OFF -- the OK path
  022411.00  SIC,SEN    -FETCH FROM UB-1, BC 1,
  022411.40  B,SERS     -CAUSES DF TO BE SET.

UB signals, UB-1 does not, same control bit, same pass of the loop.
That is precisely Reference Manual 22-6530-2 printed p.31 (PDF p.34
of docs/22-6530-2_7030RefMan.pdf, re-read at 300 dpi for this file,
section "Definition of Monitored Area"): the area "includes the word
specified by the address in the lower boundary register and all words
in subsequent locations UP TO, BUT NOT INCLUDING, the address in the
upper boundary register.  The address in the upper boundary register
is normally larger than that in the lower boundary register.  If it is
equal or smaller, no words are contained in the core storage area.
The upper boundary and lower boundary registers are located in bits
0-17 and 32-49, respectively, of storage location 3."  And on the
control bit, same page: "The boundary control bit, bit 57 of storage
location 3, determines which condition will cause an address
monitoring signal.  When the boundary control bit is zero, a signal is
obtained for a comparand inside the specified area.  When the boundary
control bit is one, a signal is obtained for a comparand outside the
specified area."

The UB / UB-1 pair spans two files -- p.71's fetch is checked by
verify_ax5b_160105_listing.py at 022367.40, this one at 022407.00.

THE LOWER EDGE, still BC 1, is the second half:

  022422.00  LX,$X13,0($X2)  -FETCH FROM LB-1, BC IS 1.
  022431.00  I60114 BDFZ,I60115   branch on DF ON -- the OK path
  022431.40  LX,$X15,3.0  -LB COMP FAILED. FETCH FROM LB-1
  022432.00  SIC,SEN      -FAILS TO SET DF. IX 15 CONTAINS
  022432.40  B,SERS       -LOCN 3.0 AT TIME OF FITCH.

LB-1 is outside [LB,UB), the control bit says signal outside, so DF
must be ON; the error names the anomaly, "FAILS TO SET DF".

AND THE p.73 HALF FLIPS THE CONTROL BIT, which is why the cut is here
and not after p.72.  Every TRANSMIT IMMEDIATE on p.72 moves BOUND1
(the word carrying BIT57) into location 3; at 022442.40 p.73 moves
BOUND0 (bit 57 clear) instead and fetches from between the bounds:

  022444.40  LX,$X13,0($X2)  -FETCH FRM LB+1, UB-1, BC IS 0.
  022453.40  I60119 BDFZ,I60120   branch on DF ON -- the OK path
  022454.00  LX,$X15,3.0  -BETWEEN UB AND LB COMP FAILED. FETCH
  022454.40  SIC,SEN      -BETWEEN THE TWO FAILS TO SET DF. IX 15
  022455.00  B,SERS       -CONTAINS LOCN 3.0 AT TIME OF FETCH.

So the transcribed range witnesses BOTH arms of the control bit: BC 1
with an inside address (no signal) and BC 0 with an inside address
(signal).

BRANCH POLARITY.  B<IND> branches when the indicator is ON, BZ<IND>
when it is OFF, a trailing Z clears it.  In every check above the
BRANCH is the OK path and the FALL-THROUGH is the SIC,SEN / B,SERS
error pair; the message names the ANOMALY, not the requirement.

DOES THE DECK AGREE WITH bsv/StretchExecute.bsv's protViolates?  On
the two clauses THIS BLOCK exercises, YES, and it is a DIRECT oracle
for that function rather than a transitive one: every reference in this block
is a fetch (LX), so the model path is dfSignal, and dfSignal's whole
body is "protViolates(st, a) ? setBit(ind, ind_DF, 1) : ind"
(StretchExecute.bsv line 535-536) -- it calls protViolates, it does
not carry its own copy of the interval rule.  Matching the deck
against the function:

  half-open [lower, upper)   line 344 "(a >= lower) && (a < upper)"
        deck: UB signals (p.71), UB-1 does not (022407.00/022410.40),
        LB-1 signals (022422.00/022431.00) -- all with ctl = 1.
  control bit chooses sense  line 346 "(ctl == 1) ? !inArea : inArea"
        deck: ctl = 1 with UB-1 inside -> no signal (022410.40);
        ctl = 0 with LB+1 inside -> signal (022453.40).
A third clause, "upper first, lower second" (lines 341-342), also
agrees, but its evidence is p.71's, not this block's: p.71 stores the
SMALLER value into BOUND0+.32 (bits 32-63, i.e. IBM 32-49, the LOWER
register) and the larger into BOUND0 (bits 0-31, i.e. IBM 0-17, the
UPPER).  It is listed here for completeness and checked by
verify_ax5b_160105_listing.py, not by this file.

THE 0-31 CARVE-OUT: THIS DECK DOES NOT BEAR ON IT.  The header's
"RANGE OF X IS FROM 000040 THRU 777777 OCTAL" invites the reading that
0o40 = 32 is the deck respecting "References to locations 0 and 4
through 31, inclusive, never cause an address monitoring signal."
(22-6530-2 printed p.31 = PDF p.34, read at 300 dpi).  Checked, and it
is not that.  The arithmetic, with the constant read off the deck's
own work area on PDF p.86 -- located on a 100 dpi survey render, then
RE-READ at 600 dpi with the label column in frame before anything
below was written:

  023067.00  I60XW3  XW,%8(0)101.0,0,0   "101.00 00 000000.00 00"

so X2's value at entry to the sweep is word 0o101 = 65.  Each outer
pass sets LB := X2 (p.71, 022362.00), then X2 += 2 words and UB := X2
(022363.40), so the first X = UB = 0o103 -- NOT 0o40.  The sweep's
teardown on p.74 is "I60214 LV,$X2,$X2 / BXVZ,I60122 / V-I,$X2,2.0 /
BD,I60106" and X2 arrives there holding UB+1 = LB+3, so subtracting 2
leaves LB+1: the lower bound walks UP by one word per pass, and the
loop ends when LB+3 overflows the 24-bit value field to zero, i.e.
when LB = 0o777775 and X = UB = 0o777777.  THE UPPER ENDPOINT IN THE
HEADER IS EXACT; THE LOWER ONE IS NOT WHAT THE CODE DOES.

WITHIN THE TRANSCRIBED RANGE the lowest address any fetch touches is
LB-1, and on the first pass that is 0o100 = 64, rising from there --
so no reference checked by this file lands in 0-31 and the deck
neither confirms nor refutes the carve-out.  ACROSS THE WHOLE SWEEP
the statement needs one correction, which is stated rather than
elided: on the LAST pass LB = 0o777775 and p.74's "V+I,$X2,2.0" at
022475.40 carries X2 to LB+3 = 0o1000000 words = 2**24 bits, which the
24-bit value field wraps to zero ("this overflow bit ... is ignored",
Reference Manual p.21), so p.74's UB+1 fetch at 022477.00 reads WORD
0.  That still decides nothing: word 0 is in the never-signal set
under EITHER control-bit setting, and the deck's expectation there is
"no signal" anyway (BC = 0, UB+1 outside the area), so the two
readings agree and the row discriminates nothing.  Either way the deck
does not bear on the carve-out.  NOTE that this last paragraph is
about p.74, a page this file reads but does NOT transcribe or check;
it is analysis, not an assertion backed by a row of the table below --
the p.74 addresses in it are 022475.40 for the "V+I,$X2,2.0" and
022477.00 for the fetch, read off the page but not machine-checked.

CONJECTURE, flagged as such: "000040" looks like a comment left behind
by an earlier value of I60XW3, since 0o36 would make X start at
exactly 0o40.  The listing carries no revision history, so this is a
guess about how the discrepancy arose, not a finding.

Two further clauses of protViolates the block does NOT reach, stated
so the "agrees" above is not read wider than it is: the AD exemption
(p.32, "an address which actuates indicator AD ... is not compared")
is EXERCISED but not CHECKED here -- the deck routes AD interrupts to
I60107 and non-AD to I6010A and prints "-CAUSES AD INTERRUPT." as an
error, so it expects DF and not AD; and the straddling rule is not
touched at all, every fetch being a whole aligned word.

ONE ROW LOOKS LIKE A BUG IN IBM'S OWN DIAGNOSTIC.  At 022452.40 the
deck writes "SV,$X14,I60AD3" where both parallel blocks write $X13
(022430.00 "SV,$X13,I60AD2" and 022460.40 "SV,$X13,I60AD3"), and the
PRINTED MACHINE CODE AGREES WITH THE PRINTED SOURCE: 23064.35 30
against 23063.73 30 and 23064.33 30, an index field of 14 where the
others have 13.  Transcribed as printed; this check passes on the
bits, which is all it can settle.  Whether the deck shipped with a
first-interrupt flag that is never set is not decidable from this page.

A SYN IS AN INPUT TO THIS CHECK, NOT A WITNESS.  Every symbol in the
program's SYN block came from the very row that names it (bit 18 read
out of that row's printed octal pair), so those rows verify only the
opcode and modifier bits.  The rows that actually check ADDRESS
placement are the twelve naming labels defined INSIDE the transcribed
range: I60210 (022403.40), I6011A (022404.40), I60111 (022410.40,
022412.00, 022433.40), I60112 (022414.00), I60114 (022415.00,
022423.40), I60113 (022425.00), I60116 (022430.40, 022456.00), I60115
(022431.00), I60117 (022436.40), I60119 (022437.40, 022446.00),
I60118 (022447.40), I60120 (022453.40).  Two of those cross the page
break -- 022430.40 "B,I60116" prints 22436.50 00 and 022431.00
"BDFZ,I60115" prints 22435.52 46, both resolving onto p.73 -- which is
the listing's own evidence that pp.72 and 73 are one block.

The SYN addresses are nevertheless CORROBORATED, independently of the
rows that use them, by the deck's own work area on PDF p.86, located
on a 100 dpi survey render and then RE-READ at 600 dpi with the label
column in frame (the project has a recorded case of a 200 dpi render
printing 021400.00 where 600 dpi printed 021400.40, so the
distinction is not pedantry):

  023063.00  I60AD1  NOP    "0.30 00"
  023063.40  I60AD2  NOP    "0.30 00"
  023064.00  I60AD3  NOP    "0.30 00"
  023302.00  BOUND0  XW,0,0,0
  023303.00  BOUND1  XW,0,0,0

That is a second, independent witness for the five data symbols; the
branch-target SYNs (I60107, I6010A, I60121, I60122) and the SSIP entry
points (SEN, SERS, SEN0, SSW) are not corroborated here and remain
pure inputs.

BIT-18 SELF-CHECKS, one for EVERY label-valued or self-relative
operand in the block, each decoded from the printed octal pair and
read back against the page's own label column.  Print format: bits
0-17 as 6 octal digits, ".", bits 18-23 as 2 octal digits, then bits
24-31 as 2 hex digits -- so BIT 18 IS THE TOP BIT OF THE OCTAL PAIR,
the half-word select.  "(int)" marks a label defined INSIDE the
transcribed range (a real address check); the rest are SYN inputs and
verify only that the bit this file wrote back is the bit the page
printed.

  022402.00  SV,$X13,I60AD1   23063.33 30  33 -> 0 -> 023063.00 = I60AD1
  022403.40  LVI,$X13,I60210  22412.73 01  73 -> 1 -> 022412.40 = I60210 (int)
  022404.00  SVA,$X13,I60107  22372.33 D0  33 -> 0 -> 022372.00 = I60107
  022404.40  LVI,$X3,I6011A   22407.47 01  47 -> 1 -> 022407.40 = I6011A (int)
  022405.00  SVA,$X3,I6010A   22371.47 D0  47 -> 1 -> 022371.40 = I6010A
  022406.40  BE,$+.32         22407.00 00  00 -> 0 -> 022407.00
  022407.40  BD,$+.32         22410.04 00  04 -> 0 -> 022410.00
  022410.40  BZDFZ,I60111     22414.12 44  12 -> 0 -> 022414.00 = I60111 (int)
  022411.40  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022412.00  B,I60111         22414.10 00  10 -> 0 -> 022414.00 = I60111 (int)
  022413.00  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022414.00  LVI,$X13,I60112  22424.33 01  33 -> 0 -> 022424.00 = I60112 (int)
  022414.40  SVA,$X13,I60107  22372.33 D0  33 -> 0 -> 022372.00 = I60107
  022415.00  LVI,$X3,I60114   22431.07 01  07 -> 0 -> 022431.00 = I60114 (int)
  022415.40  SVA,$X3,I6010A   22371.47 D0  47 -> 1 -> 022371.40 = I6010A
  022416.00  BDFZ,$+.32       22416.52 46  52 -> 1 -> 022416.40
  022421.40  BE,$+.32         22422.00 00  00 -> 0 -> 022422.00
  022422.40  BD,$+.32         22423.04 00  04 -> 0 -> 022423.00
  022423.40  BD,I60114        22431.04 00  04 -> 0 -> 022431.00 = I60114 (int)
  022424.40  LV,$X13,I60AD2   23063.72 30  72 -> 1 -> 023063.40 = I60AD2
  022425.00  BXVZ,I60113      22427.71 42  71 -> 1 -> 022427.40 = I60113 (int)
  022426.40  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022427.00  B,I60122         22506.50 00  50 -> 1 -> 022506.40 = I60122
  022427.40  V+I,$X13,(8)777777.40  777777.73 05  73 -> 1 -> the
             operand's OWN .40: this immediate is a 19-bit value field
             (bits 0-18 of a bit address), so its top bit is the same
             half-word select, not a separate convention
  022430.00  SV,$X13,I60AD2   23063.73 30  73 -> 1 -> 023063.40 = I60AD2
  022430.40  B,I60116         22436.50 00  50 -> 1 -> 022436.40 = I60116 (int)
  022431.00  BDFZ,I60115      22435.52 46  52 -> 1 -> 022435.40 = I60115 (int)
  022432.40  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022433.00  B,$+1.0          22434.10 00  10 -> 0 -> 022434.00
  022433.40  BD,I60111        22414.04 00  04 -> 0 -> 022414.00 = I60111 (int)
  022434.40  B,SSW            1301.10 00   10 -> 0 -> 001301.00 = SSW
  022435.00  BD,I60122        22506.44 00  44 -> 1 -> 022506.40 = I60122
  022436.00  SV,$X13,I60AD2   23063.73 30  73 -> 1 -> 023063.40 = I60AD2
  022436.40  LVI,$X13,I60117  22446.73 01  73 -> 1 -> 022446.40 = I60117 (int)
  022437.00  SVA,$X13,I60107  22372.33 D0  33 -> 0 -> 022372.00 = I60107
  022437.40  LVI,$X3,I60119   22453.47 01  47 -> 1 -> 022453.40 = I60119 (int)
  022440.00  SVA,$X3,I6010A   22371.47 D0  47 -> 1 -> 022371.40 = I6010A
  022440.40  BDFZ,$+.32       22441.12 46  12 -> 0 -> 022441.00
  022444.00  BE,$+.32         22444.40 00  40 -> 1 -> 022444.40
  022445.00  BD,$+.32         22445.44 00  44 -> 1 -> 022445.40
  022446.00  BD,I60119        22453.44 00  44 -> 1 -> 022453.40 = I60119 (int)
  022447.00  LV,$X13,I60AD3   23064.32 30  32 -> 0 -> 023064.00 = I60AD3
  022447.40  BXVZ,I60118      22452.31 42  31 -> 0 -> 022452.00 = I60118 (int)
  022451.00  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022451.40  B,I60122         22506.50 00  50 -> 1 -> 022506.40 = I60122
  022452.00  V+I,$X13,(8)777777.40  777777.73 05  73 -> 1 -> as 022427.40
  022452.40  SV,$X14,I60AD3   23064.35 30  35 -> 0 -> 023064.00 = I60AD3
  022453.00  B,I60121         22461.10 00  10 -> 0 -> 022461.00 = I60121
  022453.40  BDFZ,I60120      22460.12 46  12 -> 0 -> 022460.00 = I60120 (int)
  022455.00  B,SERS           1304.10 00   10 -> 0 -> 001304.00 = SERS
  022455.40  B,$+1.0          22456.50 00  50 -> 1 -> 022456.40
  022456.00  BD,I60116        22436.44 00  44 -> 1 -> 022436.40 = I60116 (int)
  022457.00  B,SSW            1301.10 00   10 -> 0 -> 001301.00 = SSW
  022457.40  B,I60122         22506.50 00  50 -> 1 -> 022506.40 = I60122
  022460.40  SV,$X13,I60AD3   23064.33 30  33 -> 0 -> 023064.00 = I60AD3

Fifty-five rows, which is every row of the block except the eleven
bit-address rows treated next and the twenty-six whose operand is an
absolute constant or a special register ($IA, $MASK, $IND, $X13, 3.0,
0($X2), and the two V-I / one V+I word immediates) and therefore
carries no half-word select to check.

SIC AND TI's FIRST ADDRESS ARE EXCLUDED FROM THAT TABLE ON PURPOSE,
and for one principle, not two: a BIT-address operand's octal pair is
a bit offset inside the word, NOT a half-word select.  SIC's operand
is a 24-bit bit address, and so is TRANSMIT's A1 (strap_asm.py
evaluates it ">>0, like SIC's and BRANCH ON BIT's B", against A2 which
is a half-word address).  The three TI rows are the one place in this
block where BOTH scalings appear in a single printed row:
"23303.00 80 000003.02 A0" at 022402.40 has a BIT-offset pair 00 in
its first half-word (A1 = BOUND1 = 023303.00, bit 0) and a HALF-WORD
select pair 02 in its second (A2 = 3.0, bit 18 = 0 -> 000003.00).  "SIC,SEN0+.32" prints 1311.40 80 at 022434.00
and 022456.40: the 40 is octal 40 = 32 decimal = bit 32 of word
001311, which is the same place the source's decimal ".32" names.
Applying the bit-18 rule to it would read 1 and be meaningless.  The
six "SIC,SEN" rows (022411.00, 022412.40, 022426.00, 022432.00,
022450.40, 022454.40) print 1310.00 80 -- bit offset 0.

ALSO NOT A HALF-WORD SELECT: the two columns print the same quantity
in different radixes.  The location column's "022422.40" is an octal
bit offset (0o40 = 32); the source operand "$+.32" is decimal 32 bits.
Both mean half-word 1.  The check: 022422.40 + .32 -> 022423.00, and
the row prints 22423.04 00, pair 04, bit 18 = 0 -> 022423.00.

NO MNEMONIC HERE IS A FIRST FOR THE REPO.  Grepped across every other
verify_*.py: BZDFZ appears in verify_ax5b_160_test8c_disabled_listing,
BDFZ in verify_ax5b_160105 and _test8c, BXVZ in ten files, V-I in
verify_ibox1_vmi, TI in verify_ax5b_160105.  What IS new is the
combination -- this is the first block in the project where TI, a
control-bit change and a DF branch appear on one page.

PROVEN DISCRIMINATING.  Observed failure sets, each measured with
"rm -rf __pycache__" run on BOTH sides of the injection (stale
bytecode has replayed a previous injection's answer in this project
before and produced a false result):

  opcodes.INDICATOR_BITS["DF"] 20 -> 21
      022410.40, 022416.00, 022431.00, 022440.40, 022453.40  (5 rows)
  opcodes.INDICATOR_BITS["XVZ"] 50 -> 49
      022425.00, 022447.40                                   (2 rows)
  opcodes.IMM_INDEX_CODES["V-I"] 0b1101 -> 0b0101
      022405.40, 022420.40                                   (2 rows)
  opcodes.DIR_INDEX_CODES["SVA"] 0b11101 -> 0b11100
      022404.00, 022405.00, 022414.40, 022415.40, 022437.00,
      022440.00                                              (6 rows)
  opcodes.TRANSMIT_CODES["TI"] (0,1,0) -> (0,0,0)
      022402.40, 022417.40, 022442.40   (the three TI rows)  (3 rows)
  opcodes.DIR_INDEX_CODES["SR"] 0b10111 -> 0b10110
      022406.00, 022421.00, 022442.00                        (3 rows)

and two in strap_asm.py, because the six above all move opcode or
modifier bits and none of them perturbs BIT 18 -- which would have
left the self-check table above as hand-decoding asserted rather than
witnessed:

  strap_asm.py the unconditional-branch/misc path's addr19 mask
  0x7FFFF -> 0x7FFFE (bit 18 forced to zero)
      022427.00, 022430.40, 022435.00, 022444.00, 022445.00,
      022446.00, 022451.40, 022455.40, 022456.00, 022457.40 (10 rows)
  strap_asm.py the branch-on-indicator path's addr19 mask, same change
      022416.00, 022425.00, 022431.00                        (3 rows)

Those thirteen are exactly the rows in this block whose branch target
is a .40 half-word on those two code paths, and clearing the bit
leaves every .00 target untouched -- the half-word select doing
precisely what the print format says it does.

MEASURED NULLS, with the arithmetic reason:

  opcodes.INDICATOR_BITS["DS"] 19 -> 18            0 rows.
      DS is indicator 19; no BDS*/BZDS* appears in 022401.40-022460.40
      (the only branch-on-indicator mnemonics here are BDFZ, BZDFZ and
      BXVZ), so no row's bits 19-24 carry 19.
  opcodes.MODE_DEFAULT_BS["BU"] 8 -> 4             0 rows.
      That default byte size is used only when a VFL data description
      is assembled; this block has no VFL row at all.  The three
      full-word rows are TRANSMITs, whose second half-word is an
      address and a count, not a data description.

THE CUT POINT.  Stopped at 022460.40, the last row of PDF p.73.  What
remains of TEST 7 is PDF p.74, 022461.00-022512.40: label I60121
(fetch between the bounds with BC 1, the BC-1 mirror of p.73's BC-0
case), I6012A/I60211/I60212/I6021B/I60213 (the UB+1 fetches with BC 0,
"-FETCH FROM UB+1, BC 0, CAUSES DF TO BE SET." at 022501.00 and
"... CAUSES AD INTERRUPT, TESTING DONE" at 022503.00), the sweep
teardown I60214 at 022504.40, and the I60122 exit with the continuity
update "LX,$X13,IC260 / V+,$X13,BIT10 / SX,$X13,IC260" ending at
022512.40.  That page needs two SYNs this one does not (IC260 at
022737.00 and BIT10 at 024534.00) and is otherwise the same shapes
again, so it is a clean next piece rather than a loose end.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ax5b_160_test7_compare.strap").read())

ROWS = [
    # ---- PDF p.72, 022401.40-022435.00 -------------------------------
    ('022401.40', '35.22 00',
     'I60110 Z,$X13          "-CLR INT 1."'),
    ('022402.00', '23063.33 30',
     'SV,$X13,I60AD1        (ext) clear the first-interrupt flag'),
    ('022402.40', '23303.00 80 000003.02 A0',
     'TI,1,BOUND1,3.0         FULL WORD at an odd half-word: BC = 1'),
    ('022403.40', '22412.73 01',
     'LVI,$X13,I60210        INTERNAL label -- real address check'),
    ('022404.00', '22372.33 D0',
     'SVA,$X13,I60107       (ext) plant the AD handler'),
    ('022404.40', '22407.47 01',
     'LVI,$X3,I6011A         INTERNAL label -- real address check'),
    ('022405.00', '22371.47 D0',
     'SVA,$X3,I6010A        (ext) plant the non-AD handler'),
    ('022405.40', '1.05 0D',
     'V-I,$X2,1.0             X2 := UB-1'),
    ('022406.00', '2.03 70',
     'SR,$X1,$IA             "-RESTORE MY INT."'),
    ('022406.40', '22407.00 00',
     'BE,$+.32                enable'),
    ('022407.00', '0.32 12',
     'LX,$X13,0($X2)         "-FETCH FROM UB-1, BC IS 1." INSIDE'),
    ('022407.40', '22410.04 00',
     'I6011A BD,$+.32        the non-AD interrupt lands here'),
    ('022410.00', '2.03 30',
     'SV,$X1,$IA             "-RESTORE SSIP INT."'),
    ('022410.40', '22414.12 44',
     'BZDFZ,I60111           DF OFF is the OK path -- HALF-OPEN'),
    ('022411.00', '1310.00 80',
     'SIC,SEN                (ext) "-FETCH FROM UB-1, BC 1,"'),
    ('022411.40', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES DF TO BE SET."'),
    ('022412.00', '22414.10 00',
     'B,I60111               INTERNAL label -- real address check'),
    ('022412.40', '1310.00 80',
     'I60210 SIC,SEN        (ext) "-FETCH FROM UB-1, BC 1,"'),
    ('022413.00', '1304.10 00',
     'B,SERS                 (ext) "-CAUSES AD INTERRUPT."'),
    ('022413.40', '2.03 30',
     'SV,$X1,$IA             "-RESTORE SSIP INT."'),
    ('022414.00', '22424.33 01',
     'I60111 LVI,$X13,I60112  INTERNAL label -- real address check'),
    ('022414.40', '22372.33 D0',
     'SVA,$X13,I60107       (ext)'),
    ('022415.00', '22431.07 01',
     'LVI,$X3,I60114         INTERNAL label -- real address check'),
    ('022415.40', '22371.47 D0',
     'SVA,$X3,I6010A        (ext)'),
    ('022416.00', '22416.52 46',
     'BDFZ,$+.32              clear DF before the next fetch'),
    ('022416.40', '14.22 00',
     'Z,$MASK                 mask register (word 12)'),
    ('022417.00', '13.22 00',
     'Z,$IND                  indicator register (word 11)'),
    ('022417.40', '23303.00 80 000003.02 A0',
     'TI,1,BOUND1,3.0         FULL WORD, odd half-word: BC still 1'),
    ('022420.40', '2.05 0D',
     'V-I,$X2,2.0             X2 := LB-1'),
    ('022421.00', '2.03 70',
     'SR,$X1,$IA'),
    ('022421.40', '22422.00 00',
     'BE,$+.32                enable'),
    ('022422.00', '0.32 12',
     'LX,$X13,0($X2)         "-FETCH FROM LB-1, BC IS 1." OUTSIDE'),
    ('022422.40', '22423.04 00',
     'BD,$+.32'),
    ('022423.00', '2.03 30',
     'SV,$X1,$IA'),
    ('022423.40', '22431.04 00',
     'BD,I60114              INTERNAL label -- real address check'),
    ('022424.00', '2.03 30',
     'I60112 SV,$X1,$IA      the AD landing for the LB-1 fetch'),
    ('022424.40', '23063.72 30',
     'LV,$X13,I60AD2        (ext) "-DID WE INTRPT LAST TIME THRU."'),
    ('022425.00', '22427.71 42',
     'BXVZ,I60113            INTERNAL label -- real address check'),
    ('022425.40', '3.36 10',
     'LX,$X15,3.0             save the boundary word for the message'),
    ('022426.00', '1310.00 80',
     'SIC,SEN                (ext) "-INTERRUPTED TWICE ON A FETCH BELOW"'),
    ('022426.40', '1304.10 00',
     'B,SERS                 (ext) "-LB,IX 15 CONTAINS CONTENTS OF"'),
    ('022427.00', '22506.50 00',
     'B,I60122              (ext) "-LOCN 3.0 AT TIME OF FETCH."'),
    ('022427.40', '777777.73 05',
     'I60113 V+I,$X13,(8)777777.40'),
    ('022430.00', '23063.73 30',
     'SV,$X13,I60AD2        (ext) "-AD INTERRUPT ONCE ON FETCH"'),
    ('022430.40', '22436.50 00',
     'B,I60116               INTERNAL, ACROSS THE PAGE BREAK  "-BELOW LB."'),
    ('022431.00', '22435.52 46',
     'I60114 BDFZ,I60115    INTERNAL, ACROSS THE PAGE BREAK; DF ON is OK'),
    ('022431.40', '3.36 10',
     'LX,$X15,3.0            "-LB COMP FAILED. FETCH FROM LB-1"'),
    ('022432.00', '1310.00 80',
     'SIC,SEN                (ext) "-FAILS TO SET DF. IX 15 CONTAINS"'),
    ('022432.40', '1304.10 00',
     'B,SERS                 (ext) "-LOCN 3.0 AT TIME OF FITCH."'),
    ('022433.00', '22434.10 00',
     'B,$+1.0'),
    ('022433.40', '22414.04 00',
     'BD,I60111              INTERNAL label -- round again'),
    ('022434.00', '1311.40 80',
     'SIC,SEN0+.32           (ext) BIT address: 0o40 = bit 32'),
    ('022434.40', '1301.10 00',
     'B,SSW                  (ext) "-TO SSIP"  (no period here)'),
    ('022435.00', '22506.44 00',
     'BD,I60122             (ext)'),
    # ---- PDF p.73, 022435.40-022460.40 -------------------------------
    ('022435.40', '35.22 00',
     'I60115 Z,$X13         "-CLR INT 2."'),
    ('022436.00', '23063.73 30',
     'SV,$X13,I60AD2        (ext)'),
    ('022436.40', '22446.73 01',
     'I60116 LVI,$X13,I60117  INTERNAL label -- real address check'),
    ('022437.00', '22372.33 D0',
     'SVA,$X13,I60107       (ext)'),
    ('022437.40', '22453.47 01',
     'LVI,$X3,I60119         INTERNAL label -- real address check'),
    ('022440.00', '22371.47 D0',
     'SVA,$X3,I6010A        (ext)'),
    ('022440.40', '22441.12 46',
     'BDFZ,$+.32'),
    ('022441.00', '14.22 00',
     'Z,$MASK'),
    ('022441.40', '13.22 00',
     'Z,$IND'),
    ('022442.00', '2.03 70',
     'SR,$X1,$IA'),
    ('022442.40', '23302.00 80 000003.02 A0',
     'TI,1,BOUND0,3.0         THE CONTROL BIT FLIPS: BOUND0 has BC = 0'),
    ('022443.40', '2.05 05',
     'V+I,$X2,2.0             X2 := LB+1 = UB-1'),
    ('022444.00', '22444.40 00',
     'BE,$+.32                enable'),
    ('022444.40', '0.32 12',
     'LX,$X13,0($X2)         "-FETCH FRM LB+1, UB-1, BC IS 0." INSIDE'),
    ('022445.00', '22445.44 00',
     'BD,$+.32'),
    ('022445.40', '2.03 30',
     'SV,$X1,$IA'),
    ('022446.00', '22453.44 00',
     'BD,I60119              INTERNAL label -- real address check'),
    ('022446.40', '2.03 30',
     'I60117 SV,$X1,$IA      the AD landing for the between fetch'),
    ('022447.00', '23064.32 30',
     'LV,$X13,I60AD3        (ext) "-DID WE INTRPT LAST TIME THRU."'),
    ('022447.40', '22452.31 42',
     'BXVZ,I60118            INTERNAL label -- real address check'),
    ('022450.00', '3.36 10',
     'LX,$X15,3.0'),
    ('022450.40', '1310.00 80',
     'SIC,SEN                (ext) "-INTERRUPTED TWICE ON A FETCH BETWEEN"'),
    ('022451.00', '1304.10 00',
     'B,SERS                 (ext) "-UB AND LB, IX 15 CONTAINS CONTENTS OF"'),
    ('022451.40', '22506.50 00',
     'B,I60122              (ext) "-LOCN 3.0 AT TIME OF FETCH."'),
    ('022452.00', '777777.73 05',
     'I60118 V+I,$X13,(8)777777.40'),
    ('022452.40', '23064.35 30',
     'SV,$X14,I60AD3        (ext) $X14, NOT $X13 -- see the docstring'),
    ('022453.00', '22461.10 00',
     'B,I60121              (ext, PDF p.74) "-BETWEEN UB AND LB."'),
    ('022453.40', '22460.12 46',
     'I60119 BDFZ,I60120    DF ON is the OK path -- BC 0, INSIDE'),
    ('022454.00', '3.36 10',
     'LX,$X15,3.0            "-BETWEEN UB AND LB COMP FAILED. FETCH"'),
    ('022454.40', '1310.00 80',
     'SIC,SEN                (ext) "-BETWEEN THE TWO FAILS TO SET DF. IX 15"'),
    ('022455.00', '1304.10 00',
     'B,SERS                 (ext) "-CONTAINS LOCN 3.0 AT TIME OF FETCH."'),
    ('022455.40', '22456.50 00',
     'B,$+1.0'),
    ('022456.00', '22436.44 00',
     'BD,I60116              INTERNAL label -- round again'),
    ('022456.40', '1311.40 80',
     'SIC,SEN0+.32           (ext) BIT address: 0o40 = bit 32'),
    ('022457.00', '1301.10 00',
     'B,SSW                  (ext) "-TO SSIP."'),
    ('022457.40', '22506.50 00',
     'B,I60122              (ext) "-TERMINATE."'),
    ('022460.00', '35.22 00',
     'I60120 Z,$X13         "-CLR INT 3."'),
    ('022460.40', '23064.33 30',
     'SV,$X13,I60AD3        (ext)'),
]

SYMBOLS = {'I60110': '022401.40', 'I6011A': '022407.40',
           'I60210': '022412.40', 'I60111': '022414.00',
           'I60112': '022424.00', 'I60113': '022427.40',
           'I60114': '022431.00', 'I60115': '022435.40',
           'I60116': '022436.40', 'I60117': '022446.40',
           'I60118': '022452.00', 'I60119': '022453.40',
           'I60120': '022460.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 T7 cmp '))
