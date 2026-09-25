#!/usr/bin/env python3
# The docstring is a RAW string: it quotes a grep regex verbatim.
r"""verify_ax5b_bit_table_listing.py -- jb_ax5b "I-Box 5", THE BIT TABLE
and the -COMMON CONSTANTS FOR FETCH ONLY pool that contains it (PDF
pp.114-115, octal 024501.00-024621.00), plus the deck's SYN table and
END (PDF p.116), from programs/ax5b_bit_table.strap against the
listing's own printed machine code.

81 checked rows, 82 symbol assertions, 1 END assertion.

CITED BY PDF PAGE.  jb_ax5b's listing pages carry no printed page
numbers -- the "12 11 10 9" down the left margin is fanfold
carriage-tape line numbering.  Every quotation below was read off a
page image rendered with pdftoppm (400 dpi for text, 600 dpi wherever
a glyph width was load-bearing).  The .strap file's header carries the
full argument; this docstring carries the verification record.

====================================================================
PREMISE CHECK, run before a line was written, because this project
has handed out work on a stale premise four times in two days.

Every octal address in 024501-024621 was grepped against every
strap/verify_*.py and every strap/programs/*.strap.

RESULT: NOT ONE OF THEM IS IN A ROWS ENTRY ANYWHERE.  The split the
brief asked for, spelled out, because a bare grep hit on "024522"
looks like coverage and is not:

  * REALLY COVERED (a ROWS tuple): nothing in 024501-024621.  The
    only ROWS tuple in the neighbourhood is
    verify_ax5b_1274_truncation_listing.py:587
        ('024500.00', '0.00 00 000000.00 00', 'I74PSI XW,0,0,0'),
    -- 024500, one word BELOW this block, routine 1274's last word.
  * NOT COVERED (a SYN line, i.e. an INPUT): 024522 in
    ax5b_1258_test1.strap:251 ('BIT0 SYN, (8)24522.0'),
    ax5b_1268_tail_pool.strap, ax5b_1274_truncation.strap;
    024501/024502/024503 as I00LC / I00Z / I00O SYNs in
    ax5b_160_test6.strap, ax5b_1683 and ax5b_1274.
  * NOT COVERED (prose only): 024534, 024535 (verify_ax5b_160_test8b
    lines 91-101, verify_ax5b_160_test7_sweep:155-157,
    verify_ax5b_160102:21), 024543 (verify_ax5b_1258_test2:107),
    024613, 024620, 024621 (verify_ax5b_160_test8b:94-96), 024532
    (verify_ax5b_162_test3b:137), 024536 (verify_ax5b_160_test8c_
    disabled:71).
  * NOT COVERED (an OPERAND of a row outside the range): '24522.32
    B0' in verify_ax5b_1268_test1bc:353 and verify_ax5b_1258_test1,
    '24523.32 B0' in verify_ax5b_1268_tail_pool:294, '24534.32 B0' in
    verify_ax5b_160_test7_sweep:217.  Those rows check an
    INSTRUCTION at some other address whose operand happens to name a
    BIT symbol supplied by a SYN.  They verify the opcode and the
    index field; the address field came from the same SYN.

verify_ax5b_1268_test1bc_listing.py:405 states it outright: "no
verify_*.py in this repository has a ROWS entry on p.114's BIT
table."  Correct when written.  This file is that entry.

====================================================================
THE HEADING, VERBATIM.

PDF p.114 prints, in the comment column, with NO location and NO
machine code, between routine 1274's last word and the pool:

    -COMMON CONSTANTS FOR FETCH ONLY

The rows under it, with their printed locations:

    (no location)   SENO    SYN,SEN0            1311.00+  +00000000
    024501.00       I00LC   (8)DD(BU,64,8),0 000 011 770 025 700 000 000
    024502.00       I00Z    XW,0,0,0,0          -ZERO INDX WD.
    024503.00       I00O    (8)DD(BU,64,8),1777777777777777777777-INDX WD. OF ONES.
    024504.00       I00VO   XW,(8)-777777.77,0,0
    024505.00       I00CO   XW,0,(8)777777,0
    024506.00-      (four anonymous DD(BU,64,8),0,0,0 statements,
      024521.00      twelve zero words, no label on any of them)
    024522.00       BIT0    XW,(8)400000.00,0,0
      ...            ...
    024621.00       BIT63   XW,0,0,1

AND THE NEGATIVE: the BIT table has NO banner of its own.  Between
024521.00 and BIT0 the listing prints exactly one bare "-" comment
row and nothing else.

PDF p.116, the SYN table, verbatim from its source column (every row
prints its value and no location, because a SYN occupies no storage):

    SSW  SYN,(8)1301.0   ERS  SYN,(8)1302.0   SERS SYN,(8)1304.0
    RET  SYN,(8)1306.40  RET1 SYN,(8)1307.0   RET2 SYN,(8)1307.40
    SEN  SYN,(8)1310.0   SEN0 SYN,(8)1311.0   DPET13 SYN,(8)1437.0
    INT  SYN,(8)1353.0   IDF1 SYN,(8)1443.0   IDF2 SYN,(8)1444.40
          END,(8)14000.0          14000.00         024622.00

(the listing prints "%8¤" where STRAP punches "(8)"; see
docs/listing_typography.md.)

====================================================================
THE TWO QUESTIONS.

Q1.  IS THE RULE EXACTLY 024522 + n FOR ALL 64?  YES.  Every row's
location was read off the page, not just the endpoints:

    PDF p.114   BIT0  024522.00 ... BIT35 024565.00   36 rows
    PDF p.115   BIT36 024566.00 ... BIT63 024621.00   28 rows

0o24565 - 0o24522 = 0o43 = 35 and 0o24621 - 0o24566 = 0o33 = 27, so
neither page has an internal gap; 0o24621 - 0o24522 = 0o77 = 63
across the page break.  All 64 are asserted individually in SYMBOLS.
Independently, PDF p.116's END prints location 024622.00 = BIT63 + 1,
and the block starts at I74PSI's 024500 + 1, so the range is sealed
at both ends by printed locations.

Q2.  DOES BIT<n> HOLD BIT n?  YES for all 64 -- and the table is NOT
64 XWs.  The one exception is the more interesting result.

Decoding every printed machine-code value gives exactly one set bit
at IBM position n, 64 for 64.  But the bit is carried by a different
XW field in each of five bands:

    BIT0-23   VALUE field (magnitude, packed << 40)
    BIT24     the SIGN bit -- written as a DD, NOT an XW
    BIT25-27  the 3-bit flag operand (<< 36)
    BIT28-45  COUNT (<< 18)
    BIT46-63  REFILL

THE BIT24 EXCEPTION IS MECHANICALLY FORCED.  IBM bit 24 is the index
word's VALUE SIGN.  STRAP's "XW,VALUE,COUNT,REFILL,FLAG" gives no
operand that sets it alone -- the sign comes only from a negative
VALUE, which also writes magnitude bits.  A word holding bit 24 and
nothing else is unreachable through XW, and the deck drops to a raw
data definition for that one row:

    BIT24   (8)DD(BU),0 000 000 010 000 000 000 000
                                    0000000010000000000000

I00VO, five rows earlier, is the control: "XW,(8)-777777.77,0,0"
prints "777777.77 80 000000.00 00" -- the sign bit set, but with all
24 magnitude bits alongside it.

So: the ADDRESS sequence is unbroken for all 64 rows, while the
SOURCE FORM has an exception at exactly one row.

The printed encodings the brief asked about, read here:
    BIT0   XW,(8)400000.00,0,0  ->  400000.00 00 000000.00 00
    BIT17  XW,(8)1.00,0,0       ->       1.00 00 000000.00 00
    BIT32  XW,0,8192,0          ->       0.00 00 400000.00 00
    BIT63  XW,0,0,1             ->       0.00 00 000000.00 01
and the cross-check the brief offered is confirmed on the page:
    BIT16  XW,(8)2.00,0,0       ->       2.00 00 000000.00 00
    BIT17  XW,(8)1.00,0,0       ->       1.00 00 000000.00 00
(the second two-character group of each printed half-word is HEX, not
octal -- listing_oracle.fmt_half; that is why BIT28 prints "0.00 08".)

====================================================================
WITNESS TIERING.

WITNESSED, TIER 1 -- 81 printed machine-code values, read row by row
off pp.114-115.  Each is an independent datum.

WITNESSED, TIER 1 -- the 64 BIT<n> LOCATIONS, read off pp.114-115's
own location column separately from the machine code.  These, and not
the location counter, are what establishes 024522 + n.  They are in
SYMBOLS, one assertion per row.

ANCHOR, NOT EVIDENCE -- the single "SLC,(8)24501.0".  The assembler
derives all 81 locations from that one number by size accounting.
A label placed by the location counter is not a witness to its own
address.  What is actually checked is the AGREEMENT between that
propagation and the independently-read location column.  Because
these are 64 consecutive, identically-sized XWs, one SLC plus the
counter does nearly all of the address arithmetic; that is exactly
why the page's location column had to be read for every row, and why
injection 7 below (shift the SLC) is recorded as proving nothing.

DERIVED BY ARITHMETIC, NOT READ -- the 3-words-per-statement split of
the four anonymous "DD(BU,64,8),0,0,0" statements.  Four printed
source lines, twelve printed machine-code lines (024506.00-024521.00);
12/4 = 3 matches the three operands on each line, and
strap_asm.statement_size computes length * len(fields).  The
boundaries between the four groups were NOT read: the source lines
sit between code rows, not level with them.  Those twelve rows carry
no label and print 22 zeros, so they are the weakest rows here.

INPUTS -- NONE.  This file SYNs no symbol from outside itself.  Every
symbol it defines comes from a row printed on pp.114-116.  That is
unusual in this repo and is the point of the file.

PROMOTED FROM INPUT TO CHECKED -- p.116's SYN table.  SEN, SEN0,
SERS, SSW, RET, RET1, RET2, ERS, INT, IDF1, IDF2, DPET13 are pure
assumed inputs in nearly every transcription in this repository
(ax5b_1274_truncation.strap:393-399, ax5b_1268_tail_pool.strap:
434-440, ax5b_1258_test1.strap:249-253, ax4b_1246_modifiers.strap:
298-306, ax4b_1246_transmit_swap.strap:240-251, ...).  Here they are
transcribed from p.116's SOURCE column and asserted against p.116's
VALUE column -- two different printed columns, so the assertion
checks STRAP's evaluation rather than assuming it.
verify_ax5b_1274_truncation_listing.py:158 quoted this table in prose
and called it "Corroboration, not promotion"; this is the promotion.
The check is narrow: it proves the deck's own SYN operands evaluate
to the deck's own printed values.  It does not prove what SSIP does
with them.

====================================================================
SENO / SEN0 -- THE ALIAS, SETTLED.

PDF p.114's first pool row prints

    SENO    SYN,SEN0            1311.00+   +00000000

Three independent lines agree and none dissents:

 1. SAME PRINTED ROW, 600 dpi (pdftoppm -r 600 -png -gray, glyph
    bounding boxes from pixel-column ink profiles): the LABEL's 4th
    glyph is 54 px, the OPERAND's 4th glyph is 42 px.  On the next
    printed row I00LC's two digit zeros measure 48 and 45 px.  Ratio
    54/42 = 1.29 against docs/listing_typography.md Sec.6's
    calibrated 1.15-1.22 for letter O over digit 0 on this deck.
    This reproduces Sec.6's own numbers (54 and 42) independently.
 2. PDF p.116, 600 dpi: "SEN0  SYN,(8)1311.0" -- the LABEL's 4th
    glyph measures 44 px, i.e. a digit zero.  (Same row's S=46, E=42,
    N=43.)
 3. GLYPH-FREE, and decisive: p.114's row prints the VALUE 1311.00+,
    and p.116 DEFINES SEN0 as (8)1311.0 = 1311.00+.  A symbol cannot
    be SYN'd to itself -- the definition would be circular and could
    not have printed a value at all.  The two spellings must differ,
    and p.116 supplies the one the operand names.

VERDICT: the row is an ALIAS, letter-O SENO defined as digit-zero
SEN0, and both are defined in the .strap.  docs/listing_typography.md
Sec.6 rates this "moderate, direction only"; with p.116's definition
in hand it is settled for this row.  programs/ax5b_1258_test2.strap's
"SENO SYN,SENO" (a self-SYN) is wrong.

BIT0 IS A DIGIT ZERO.  Its 4th glyph measures 45 px; the five digit
zeros in its own operand on the same printed row measure 45-50 px,
and SENO's letter O eighteen rows above measures 54 px.

I00O, NOT I000.  Measured at 600 dpi in the SAME token: I = 12 px
(letter I), 0 = 43 px, 0 = 42 px, final glyph = 51 px -- ratio 1.20,
in the letter-O band.  I00VO's last glyph is 51 px and I00CO's is 55
px on the same page, both letter O.  The row's own comment is "-INDX
WD. OF ONES." and its neighbour I00Z's is "-ZERO INDX WD.", so O is
for Ones as Z is for Zero.  This reproduces
verify_ax5b_160_test8b_listing.py:103-105 independently.
A DELIBERATE DEPARTURE FROM THE BRIEF, FLAGGED AS SUCH: the task
that produced this file specified the spelling "I000" and said a
repo-wide rename had already applied it.  This file writes I00O
instead, on the measurement above.  The reason the instruction and
the page disagree is narrow and checkable: docs/listing_typography.md
Sec.5 lists the pool as "I00LC, I00Z, I000, I00VO, I00CO", but Sec.5
measured only the LEADING glyph of each label -- that is what its
rename was about -- and never measured the trailing one.
verify_ax5b_1683_listing.py:53 also writes "I000".  The repo majority
(12 files) already writes I00O, and so does the row's own comment
logic (O for Ones, Z for Zero).  The leading-letter-I
verdict of Sec.4 is confirmed here for all five labels (12-14 px).

====================================================================
FIRST FOR THIS REPO: ONE, after grep eliminated two candidates.

  * "DD(BU)" WITH NO LENGTH OR PADDING MODIFIER -- BIT24's row.
    WHAT WAS ACTUALLY RUN, and when: `grep -rn 'DD(BU)' strap/` was
    run BEFORE either of these two files existed and returned ZERO
    hits.  It was then re-run as a regex to close the spacing
    variants -- `grep -rnE 'DD *\( *BU *\)' strap/ --include='*.strap'
    --include='*.py'`, excluding this pair, also zero.  Every other DD
    in the repository writes DD(BU,64,8) or DD(BU,32,8).  (Re-running
    the plain grep NOW will return these two files; that is not
    evidence either way.)  strap_asm.dds_length_bits defaults a
    missing length to 64 (`if length_expr is None: return 64`), which
    is what makes the row a full word.  Nothing exercised that default
    before.  Injection 2 below is the discriminating test for it.

  ELIMINATED BY GREP (claimed on inspection, then knocked out):
  * "XW with a non-zero FOURTH operand" (BIT25/26/27).  NOT a first:
    programs/ibox1_bind.strap:79 already assembles "IBXWZO
    XW,-1,0,0,4", and strap_asm.py's own comment at line 1394 names
    programs/op_ad_indicators.strap's WOTHER.
  * "A SYN whose operand is another SYMBOL" (SENO SYN,SEN0).  NOT a
    first: programs/dcp_maintenance_compool.strap:104 has "EBAUTO
    SYN, ECTL1" and eleven more of the same shape.
  * The 54 px / 42 px SENO measurement itself is NOT new either --
    verify_ax5b_1274_truncation_listing.py:245-249 has it.  What is
    new is p.116's SEN0 label measurement and the value argument
    (line 3 above), which together close the question.

====================================================================
PROVEN DISCRIMINATING.

The obvious objection to this block is that 64 near-identical XW rows
cannot tell much apart: an injection that moves all 64 identically
proves only that the file is wired up.  So the injections below were
chosen off the five-band table in Q2 -- each one is aimed at a
DIFFERENT, NAMED subset, and three of them move a single row.

Method, applied to every entry: edit strap_asm.py with a reversed-
patch-able edit; `grep -n` the changed line and read it back to
confirm the edit APPLIED (a sed that silently fails to match produces
ALL TESTS PASSED, which is indistinguishable from a measured null);
`rm -rf __pycache__`; run `python3 verify_ax5b_bit_table_listing.py`;
record the OBSERVED failing rows; reverse the patch; `rm -rf
__pycache__` again; confirm `git diff --stat strap_asm.py` is empty.
Never `git checkout` a file with uncommitted work (AGENTS.md).

Clean run first, for the baseline: 164 checks, 0 FAIL, "ALL TESTS
PASSED" (82 symbol assertions + 81 rows + 1 END).

  # target (strap_asm.py)              OBSERVED failures
  --------------------------------------------------------------------
  1 line 1396, the XW flag operand's   2 rows, NAMED:
    mask, "& 0x7" -> "& 0x1".  This      FAIL 024553.00 BIT25
    is the historically real bug the     FAIL 024554.00 BIT26
    file's own comment records.        BIT27 SURVIVES, and the reason is
                                       arithmetic: 1 & 0x1 == 1, so the
                                       one-bit operand still lands at
                                       IBM 27.  Only the 4 and the 2 are
                                       masked away.  2 of 81 rows.

  2 line 947, dds_length_bits'         1 ROW, and only one:
    "if length_expr is None:             FAIL 024552.00 BIT24
    return 64" -> "return 32".         assembled '0000000000000000000000'
                                       vs listing '00000000100000000000
                                       00'.  This is the single-row
                                       discriminator for BIT24 being a
                                       DD *with no length modifier* --
                                       nothing else in the block, and
                                       nothing else in the repository,
                                       reaches that default.

  3 line 1398, "(sign << 39)"          1 ROW, and it is NOT BIT24:
    -> "(sign << 38)".                   FAIL 024504.00 I00VO
                                       assembled '777777.77 40 ...' vs
                                       listing '777777.77 80 ...'.
                                       BIT24 does not move.  That is the
                                       clean proof that BIT24 is not an
                                       XW with a negative value: it
                                       holds IBM bit 24, but it does not
                                       go through XW's sign path.

  4 line 1398, "(mag << 40)"           25 rows: I00VO and BIT0..BIT23,
    -> "(mag << 39)".                  and NOTHING from BIT24 up.  e.g.
                                         FAIL 024522.00 BIT0 assembled
                                         '200000.00 00 ...' vs listing
                                         '400000.00 00 ...'
                                       The whole VALUE band moves one
                                       bit right; the four other bands
                                       are untouched.

  5 line 1398, "(count << 18)"         19 rows: I00CO and BIT28..BIT45,
    -> "(count << 17)".                and nothing else.  e.g.
                                         FAIL 024556.00 BIT28 assembled
                                         '000000.00 04 ...' vs listing
                                         '000000.00 08 ...'
                                         FAIL 024505.00 I00CO assembled
                                         '000000.00 07 777770.00 00' vs
                                         listing '...0F 777760.00 00'
                                       Exactly the COUNT band.

  6 line 1376, the REFILL mask         1 ROW, and only one:
    "& 0x3FFFF" -> "& 0x1FFFF".          FAIL 024600.00 BIT46
                                       assembled '...000000.00 00' vs
                                       listing '...000010.00 00'.
                                       BIT46's refill is 131072 = 2^17,
                                       the top bit of the 18-bit field;
                                       BIT47..BIT63 all have refill
                                       <= 2^16 and are unaffected.  The
                                       block's own geometry is what
                                       makes this a one-row test.

  7 line 1371, the COUNT mask          2 rows: I00CO (0o777777 clipped
    "& 0x3FFFF" -> "& 0x1FFFF".        to 0o377777) and BIT28 (131072 ->
                                       0).  BIT29..BIT45 survive for the
                                       same arithmetic reason as 6:
                                       their counts are <= 2^16.

  8 THE DELIBERATELY WEAK ONE, run     139 of 164 checks FAIL: all 69
    and recorded because the brief     LOCATION symbols (I00LC..I00CO
    asks what an injection can         and BIT0..BIT63) and 70 of the 81
    actually distinguish here.         rows.
    line 1233, the SLC handler's       WHAT IT PROVES: almost nothing.
    "new_loc = eval_expr(...)"         It moves every row identically,
    -> "... + 64" (one word).          so it cannot tell any row from
                                       any other.  Compare 2, 3 and 6,
                                       which each name a single row.
                                       WHAT IS INTERESTING is the 11
                                       SURVIVORS: 024507.00-024521.00,
                                       eleven of the twelve anonymous
                                       zero words, still read zero after
                                       the shift because their
                                       neighbours are zero too.  The
                                       twelve label-free zero rows are
                                       the weakest rows in this file and
                                       this injection measures exactly
                                       how weak.  THE 25 SURVIVORS, in
                                       full: those 11 zero rows, the 13
                                       VALUE symbols (the twelve p.116
                                       names plus SENO -- a SYN takes no
                                       location counter, so shifting it
                                       cannot move them), and the END
                                       assertion.  69 location-symbol
                                       FAILs + 70 row FAILs = 139;
                                       164 - 139 = 25.

  9 A GENUINE NULL, recorded with      0 failures.  "ALL TESTS PASSED".
    its arithmetic reason.             REASON: line 944 is the first
    line 944, dds_length_bits'         branch of dds_length_bits and
    "if not mods or not mods[0]        fires only when a DD carries NO
    .strip(): return 64" -> "return    data-description modifier at all.
    8".                                Every DD in this block writes
                                       (BU,64,8) or (BU), so mods[0] is
                                       never empty and the branch is
                                       never reached.  Injection 2 hits
                                       the branch that IS reachable,
                                       three lines below it.  This pair
                                       is why the "confirm it applied"
                                       step matters: both patches touch
                                       a line reading "return 64", and a
                                       sed aimed at the wrong one would
                                       look exactly like this null.

 10 A SECOND GENUINE NULL, on a               0 failures.  "ALL TESTS
    DIFFERENT mechanism from 9.        PASSED".  REASON: eval_addr_field's
    line 1376, eval_addr_field's       shift converts a LABEL's bit
    bit-count-to-word-address shift,   address to a word address.  Every
    "loc, 6, lineno" -> "loc, 0,       REFILL operand in this block is a
    lineno".                           BARE INTEGER counting words
                                       (131072, 65536, ..., 1), and
                                       eval_addr_field applies the shift
                                       only to the label form.  So the
                                       18 REFILL rows pin down the
                                       field's POSITION and WIDTH
                                       (injection 6) but say nothing
                                       about its units.  Recorded so the
                                       gap is on the record rather than
                                       implied.

HOW EACH INJECTION WAS CONFIRMED TO APPLY.  A shared driver printed
the target line BEFORE the edit and AGAIN AFTER it, and the Python
that applied the patch asserted the old text was present in that
exact line (raising if not), so a non-matching patch aborts instead of
producing a passing run.  `rm -rf __pycache__` ran immediately before
and immediately after every run.  Each patch was reversed by the same
mechanism with the arguments swapped, the line was printed a third
time, and `git diff --stat -- stretch/strap/strap_asm.py` was checked
empty after every one.  It is empty now, and `git status` shows only
the two new untracked files.

====================================================================
WHAT THIS FILE DOES NOT DO.  It is an ENCODING oracle only: the
assembled image is compared against IBM's own printed machine code.
Nothing here is run on the Bluespec model -- a table of 64 constants
has no behaviour -- and this session was instructed not to run bsc,
run_tests.sh, run_program.sh or mutation_score.py.  It is not wired
into run_tests.sh.
"""
import sys

from strap_asm import assemble
from listing_oracle import check_rows, finish, loc_bits

prog = assemble(open("programs/ax5b_bit_table.strap").read())

# ---------------------------------------------------------------------
# PDF p.114, the pool head.  Printed source in the note column; where
# the note differs from the assembled source line, see the .strap
# header's "WHAT IS NOT VERBATIM" section.
# ---------------------------------------------------------------------
POOL_ROWS = [
    ('024501.00', '0000011770025700000000',
     'I00LC (8)DD(BU,64,8),0 000 011 770 025 700 000 000'),
    ('024502.00', '0.00 00 000000.00 00',
     'I00Z  XW,0,0,0,0            "-ZERO INDX WD."'),
    ('024503.00', '1777777777777777777777',
     'I00O  (8)DD(BU,64,8),1777777777777777777777  "-INDX WD. OF ONES."'),
    ('024504.00', '777777.77 80 000000.00 00',
     'I00VO XW,(8)-777777.77,0,0  the SIGN-bit control for BIT24'),
    ('024505.00', '0.00 0F 777760.00 00',
     'I00CO XW,0,(8)777777,0      COUNT all ones, 18 bits'),
]

# The four anonymous "DD(BU,64,8),0,0,0" statements, twelve zero words.
# TIER 3: no labels, 22 printed zeros, and the 3-words-per-statement
# split is arithmetic (12 words / 4 source lines), not read off the
# page.  Their LOCATIONS are printed, and they are what puts BIT0 at
# 024522.
ZERO_ROWS = [
    ('024506.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 1, word 1 of 3'),
    ('024507.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 1, word 2 of 3'),
    ('024510.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 1, word 3 of 3'),
    ('024511.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 2, word 1 of 3'),
    ('024512.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 2, word 2 of 3'),
    ('024513.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 2, word 3 of 3'),
    ('024514.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 3, word 1 of 3'),
    ('024515.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 3, word 2 of 3'),
    ('024516.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 3, word 3 of 3'),
    ('024517.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 4, word 1 of 3'),
    ('024520.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 4, word 2 of 3'),
    ('024521.00', '0000000000000000000000',
     'DD(BU,64,8),0,0,0  statement 4, word 3 of 3'),
]

# ---------------------------------------------------------------------
# THE BIT TABLE ITSELF.  PDF p.114 rows BIT0-BIT35 (024522.00-
# 024565.00), PDF p.115 rows BIT36-BIT63 (024566.00-024621.00).
# 64 consecutive full words, read row by row from both the machine-code
# column and the location column.
# ---------------------------------------------------------------------
BIT_ROWS = [
    ('024522.00', '400000.00 00 000000.00 00',
     'BIT0 XW,(8)400000.00,0,0'),
    ('024523.00', '200000.00 00 000000.00 00',
     'BIT1 XW,(8)200000.00,0,0'),
    ('024524.00', '100000.00 00 000000.00 00',
     'BIT2 XW,(8)100000.00,0,0'),
    ('024525.00', '40000.00 00 000000.00 00',
     'BIT3 XW,(8)40000.00,0,0'),
    ('024526.00', '20000.00 00 000000.00 00',
     'BIT4 XW,(8)20000.00,0,0'),
    ('024527.00', '10000.00 00 000000.00 00',
     'BIT5 XW,(8)10000.00,0,0'),
    ('024530.00', '4000.00 00 000000.00 00',
     'BIT6 XW,(8)4000.00,0,0'),
    ('024531.00', '2000.00 00 000000.00 00',
     'BIT7 XW,(8)2000.00,0,0'),
    ('024532.00', '1000.00 00 000000.00 00',
     'BIT8 XW,(8)1000.00,0,0'),
    ('024533.00', '400.00 00 000000.00 00',
     'BIT9 XW,(8)400.00,0,0'),
    ('024534.00', '200.00 00 000000.00 00',
     'BIT10 XW,(8)200.00,0,0'),
    ('024535.00', '100.00 00 000000.00 00',
     'BIT11 XW,(8)100.00,0,0'),
    ('024536.00', '40.00 00 000000.00 00',
     'BIT12 XW,(8)40.00,0,0'),
    ('024537.00', '20.00 00 000000.00 00',
     'BIT13 XW,(8)20.00,0,0'),
    ('024540.00', '10.00 00 000000.00 00',
     'BIT14 XW,(8)10.00,0,0'),
    ('024541.00', '4.00 00 000000.00 00',
     'BIT15 XW,(8)4.00,0,0'),
    ('024542.00', '2.00 00 000000.00 00',
     'BIT16 XW,(8)2.00,0,0'),
    ('024543.00', '1.00 00 000000.00 00',
     'BIT17 XW,(8)1.00,0,0'),
    ('024544.00', '0.40 00 000000.00 00',
     'BIT18 XW,(8).40,0,0'),
    ('024545.00', '0.20 00 000000.00 00',
     'BIT19 XW,(8).20,0,0'),
    ('024546.00', '0.10 00 000000.00 00',
     'BIT20 XW,(8).10,0,0'),
    ('024547.00', '0.04 00 000000.00 00',
     'BIT21 XW,(8)0.04,0,0'),
    ('024550.00', '0.02 00 000000.00 00',
     'BIT22 XW,(8)0.02,0,0'),
    ('024551.00', '0.01 00 000000.00 00',
     'BIT23 XW,(8)0.01,0,0'),
    ('024552.00', '0000000010000000000000',
     'BIT24 (8)DD(BU),0 000 000 010 000 000 000 000'),
    ('024553.00', '0.00 40 000000.00 00',
     'BIT25 XW,0,0,0,4'),
    ('024554.00', '0.00 20 000000.00 00',
     'BIT26 XW,0,0,0,2'),
    ('024555.00', '0.00 10 000000.00 00',
     'BIT27 XW,0,0,0,1'),
    ('024556.00', '0.00 08 000000.00 00',
     'BIT28 XW,0,131072,0'),
    ('024557.00', '0.00 04 000000.00 00',
     'BIT29 XW,0,65536,0'),
    ('024560.00', '0.00 02 000000.00 00',
     'BIT30 XW,0,32768,0'),
    ('024561.00', '0.00 01 000000.00 00',
     'BIT31 XW,0,16384,0'),
    ('024562.00', '0.00 00 400000.00 00',
     'BIT32 XW,0,8192,0'),
    ('024563.00', '0.00 00 200000.00 00',
     'BIT33 XW,0,4096,0'),
    ('024564.00', '0.00 00 100000.00 00',
     'BIT34 XW,0,2048,0'),
    ('024565.00', '0.00 00 040000.00 00',
     'BIT35 XW,0,1024,0'),
    ('024566.00', '0.00 00 020000.00 00',
     'BIT36 XW,0,512,0'),
    ('024567.00', '0.00 00 010000.00 00',
     'BIT37 XW,0,256,0'),
    ('024570.00', '0.00 00 004000.00 00',
     'BIT38 XW,0,128,0'),
    ('024571.00', '0.00 00 002000.00 00',
     'BIT39 XW,0,64,0'),
    ('024572.00', '0.00 00 001000.00 00',
     'BIT40 XW,0,32,0'),
    ('024573.00', '0.00 00 000400.00 00',
     'BIT41 XW,0,16,0'),
    ('024574.00', '0.00 00 000200.00 00',
     'BIT42 XW,0,8,0'),
    ('024575.00', '0.00 00 000100.00 00',
     'BIT43 XW,0,4,0'),
    ('024576.00', '0.00 00 000040.00 00',
     'BIT44 XW,0,2,0'),
    ('024577.00', '0.00 00 000020.00 00',
     'BIT45 XW,0,1,0'),
    ('024600.00', '0.00 00 000010.00 00',
     'BIT46 XW,0,0,131072'),
    ('024601.00', '0.00 00 000004.00 00',
     'BIT47 XW,0,0,65536'),
    ('024602.00', '0.00 00 000002.00 00',
     'BIT48 XW,0,0,32768'),
    ('024603.00', '0.00 00 000001.00 00',
     'BIT49 XW,0,0,16384'),
    ('024604.00', '0.00 00 000000.40 00',
     'BIT50 XW,0,0,8192'),
    ('024605.00', '0.00 00 000000.20 00',
     'BIT51 XW,0,0,4096'),
    ('024606.00', '0.00 00 000000.10 00',
     'BIT52 XW,0,0,2048'),
    ('024607.00', '0.00 00 000000.04 00',
     'BIT53 XW,0,0,1024'),
    ('024610.00', '0.00 00 000000.02 00',
     'BIT54 XW,0,0,512'),
    ('024611.00', '0.00 00 000000.01 00',
     'BIT55 XW,0,0,256'),
    ('024612.00', '0.00 00 000000.00 80',
     'BIT56 XW,0,0,128'),
    ('024613.00', '0.00 00 000000.00 40',
     'BIT57 XW,0,0,64'),
    ('024614.00', '0.00 00 000000.00 20',
     'BIT58 XW,0,0,32'),
    ('024615.00', '0.00 00 000000.00 10',
     'BIT59 XW,0,0,16'),
    ('024616.00', '0.00 00 000000.00 08',
     'BIT60 XW,0,0,8'),
    ('024617.00', '0.00 00 000000.00 04',
     'BIT61 XW,0,0,4'),
    ('024620.00', '0.00 00 000000.00 02',
     'BIT62 XW,0,0,2'),
    ('024621.00', '0.00 00 000000.00 01',
     'BIT63 XW,0,0,1'),
]

# ---------------------------------------------------------------------
# SYMBOLS.  Five tiers are mixed here on purpose; the .strap header
# says which is which.
#   * BIT0..BIT63 and I00LC..I00CO: the LOCATION COLUMN of pp.114-115,
#     read separately from the machine code.  This is the check of
#     "BIT<n> = 024522 + n" -- 64 separate equalities, one per row.
#   * SENO and the twelve p.116 names: the VALUE COLUMN of p.116
#     ("1301.00+"), against source lines transcribed from p.116's
#     SOURCE column.  They cannot be ROWS entries: listing_oracle's
#     render() has no branch for the two-token "1301.00+  +00000000"
#     shape and would fall through to fmt_half().
# ---------------------------------------------------------------------
SYMBOLS = {
    'I00LC': '024501.00',
    'I00Z':  '024502.00',
    'I00O':  '024503.00',
    'I00VO': '024504.00',
    'I00CO': '024505.00',
    'BIT0':   '024522.00',
    'BIT1':   '024523.00',
    'BIT2':   '024524.00',
    'BIT3':   '024525.00',
    'BIT4':   '024526.00',
    'BIT5':   '024527.00',
    'BIT6':   '024530.00',
    'BIT7':   '024531.00',
    'BIT8':   '024532.00',
    'BIT9':   '024533.00',
    'BIT10':  '024534.00',
    'BIT11':  '024535.00',
    'BIT12':  '024536.00',
    'BIT13':  '024537.00',
    'BIT14':  '024540.00',
    'BIT15':  '024541.00',
    'BIT16':  '024542.00',
    'BIT17':  '024543.00',
    'BIT18':  '024544.00',
    'BIT19':  '024545.00',
    'BIT20':  '024546.00',
    'BIT21':  '024547.00',
    'BIT22':  '024550.00',
    'BIT23':  '024551.00',
    'BIT24':  '024552.00',
    'BIT25':  '024553.00',
    'BIT26':  '024554.00',
    'BIT27':  '024555.00',
    'BIT28':  '024556.00',
    'BIT29':  '024557.00',
    'BIT30':  '024560.00',
    'BIT31':  '024561.00',
    'BIT32':  '024562.00',
    'BIT33':  '024563.00',
    'BIT34':  '024564.00',
    'BIT35':  '024565.00',
    'BIT36':  '024566.00',
    'BIT37':  '024567.00',
    'BIT38':  '024570.00',
    'BIT39':  '024571.00',
    'BIT40':  '024572.00',
    'BIT41':  '024573.00',
    'BIT42':  '024574.00',
    'BIT43':  '024575.00',
    'BIT44':  '024576.00',
    'BIT45':  '024577.00',
    'BIT46':  '024600.00',
    'BIT47':  '024601.00',
    'BIT48':  '024602.00',
    'BIT49':  '024603.00',
    'BIT50':  '024604.00',
    'BIT51':  '024605.00',
    'BIT52':  '024606.00',
    'BIT53':  '024607.00',
    'BIT54':  '024610.00',
    'BIT55':  '024611.00',
    'BIT56':  '024612.00',
    'BIT57':  '024613.00',
    'BIT58':  '024614.00',
    'BIT59':  '024615.00',
    'BIT60':  '024616.00',
    'BIT61':  '024617.00',
    'BIT62':  '024620.00',
    'BIT63':  '024621.00',
    # PDF p.116's SYN table, value column.
    'SSW':    '001301.00',
    'ERS':    '001302.00',
    'SERS':   '001304.00',
    'RET':    '001306.40',
    'RET1':   '001307.00',
    'RET2':   '001307.40',
    'SEN':    '001310.00',
    'SEN0':   '001311.00',
    'DPET13': '001437.00',
    'INT':    '001353.00',
    'IDF1':   '001443.00',
    'IDF2':   '001444.40',
    # PDF p.114's alias row, "SENO  SYN,SEN0" -> printed 1311.00+.
    'SENO':   '001311.00',
}


def check_end(prog):
    """PDF p.116 prints "END,(8)14000.0" with the value 14000.00 and
    the LOCATION 024622.00.  024622 = BIT63 + 1, which is what proves
    nothing was dropped between BIT63 and the end of the deck.  The
    END row cannot be a ROWS entry: its printed text is the single
    dotted token "14000.00", which render() would treat as a
    half-word."""
    want = 0o14000 * 2  # half-words; strap_asm records end_pc that way
    ok = prog.end_pc == want
    print(f"{'PASS' if ok else 'FAIL'} bittable END target: "
          f"assembled half-word {prog.end_pc}, listing 14000.00 "
          f"= half-word {want}")
    return not ok


fails = check_rows(prog, POOL_ROWS, SYMBOLS, label='bittable ')
fails += check_rows(prog, ZERO_ROWS, label='bittable ')
fails += check_rows(prog, BIT_ROWS, label='bittable ')
fails += check_end(prog)
finish(fails)
