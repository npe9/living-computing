#!/usr/bin/env python3
"""verify_ax5b_160_test8b_listing.py -- jb_ax5b "I-Box 5", routine 1260
TEST 8B (programs/ax5b_160_test8b.strap) against the listing's own
printed machine code, PDF p.75, octal 022513.00-022545.40.  52 rows,
one unbroken run; the block occupies 54 half-words because two of the
rows are full-word VFL loads.  (This deck's listing pages carry no
printed page numbers -- cite by PDF page.)

THE RICHER DS ORACLE.  verify_ax5b_16086_listing.py already checked
IBM's DS test for "SV TO 1.0 FAILS TO SET DS WHEN ENABLED", nineteen
half-words of it.  TEST 8B checks the same indicator with the system
DISABLED and ENABLED, and adds what 16086 never touches: whether the
offending store was SUPPRESSED.  Its error messages, transcribed
verbatim:

  022520.40  -SX OUT OF BOUNDS SETS DS WHEN
  022521.00  -SYSTEM DISABLED.

  022530.40  -UNABLE TO CLR IND REGS MUST
  022531.00  -TERMINATE THIS TEST.

  022536.00  -NO INTERRUPT OCCURED ON AN
  022536.40  -SX ABOVE UB.

  022540.40  -SX ABOVE UB WAS NOT NOPED, DATA
  022541.00  -WAS STORED WHEN ENABLED.

and the block's own header, at 022515.40-022516.00:

  160125 BD,$+.32   -TEST 8B CHKS DS WITH SYSTEMS
         LX,$X1,BIT57  -DISABLED, AND ENABLED.

("OCCURED", one R, and "SYSTEMS" plural, are the deck's own spellings.)

THE THIRD MESSAGE IS THE ACCEPTANCE TEST FOR OPERATION TERMINATION.
The enabled half stores the all-ones index word into 160AD1, which is
above the upper boundary planted at 022525.00, then reads 160AD1 back
with L(BU) at 022537.00 and demands Result Zero.  If the machine let
the store land, BRZ does not branch and the deck prints "SX ABOVE UB
WAS NOT NOPED, DATA WAS STORED WHEN ENABLED."  That is IBM's own
regression suite requiring a protection violation to NOP the store,
not merely to raise an indicator.

FOUR ENCODINGS NO LISTING IN THIS PROJECT HAD CHECKED BEFORE:

  * BDSZ   "22517.51 C6"  branch on DS (19) and zero it
  * BZDSZ  "22521.51 C4"  branch on ZERO DS and zero it

BRANCH POLARITY, AND A CORRECTION TO THIS FILE'S FIRST DRAFT.  The two
codes above differ in ONE printed bit and the whole reading of the
block turns on it.  strap_asm.py's enc_branch_ind lays the word out as
addr19(19) | indnum(6) | 0b1000(4) | clear(1) | branchOn(1) | idx(1),
so branchOn is bit 30 and lands in the printed HEX BYTE: 0xC6 =
11000110 has it set, 0xC4 = 11000100 does not.  classify_branch_indicator
assigns branchOn=1 to the "B" prefix and branchOn=0 to "BZ".  So
B<IND> branches when the indicator is ON and BZ<IND> branches when it
is OFF; a trailing Z clears it either way (bit 29, set in both words
here).

WHICH MEANS THE BRANCH IS THE OK PATH AND THE FALL-THROUGH IS THE
ERROR, throughout 8B and 8C.  BZDSZ at 022520.00 jumps over the
SIC,SEN / B,SERS pair at 022520.40-022521.00 when DS is OFF.  So this
deck's position is that a protection violation with the interruption
system DISABLED does not actuate the indicator at all -- and the error
text names the anomaly rather than the requirement, which is the only
way "-SX OUT OF BOUNDS SETS DS WHEN / -SYSTEM DISABLED." parses as a
complaint.  ax5b_160_test8c_disabled.strap states the same rule
independently ("disabled means: no suppression, no indicator, no
interrupt, whatever the mask says"), and the model already agrees:
StretchExecute.bsv's protViolates ends `st.irqEnabled() && installed(a)
&& signalled`.

This file's first draft glossed 022520.00 as "disabled: DS must still
be ON" and said so at length in ax5b_160_test8b.strap.  That was
backwards.  The transcription was never in question -- the rows are
bit-exact against the printed code, which is why nothing caught it.
Prose is not executable; only the encodings are checked.
  * BRZ    "22532.34 C2"  branch on Result Zero -- indicator 57
  * L(BU)  "13.00 80 000000.20 50"  a full-word VFL load with the
    default (BU,64,8) data description, reading word 11 back as one
    64-bit unsigned binary field

BRZ is the one worth stating twice: bits 19-24 of the printed row are
111001 = 57, and opcodes.INDICATOR_BITS has RZ at 57.  That number
reached this project from the IBM 7030 Reference Card's "INDICATOR
LIST" by way of bsv/StretchTypes.bsv (whose 48-63 run cites exactly
that card and nothing else) -- no deck listing had ever witnessed it.
These two rows are that witness.

TWO MORE CONFIRMATIONS OF THE BIT TABLE, and this time from its own
endpoints.  024522 + n gives BIT11 -> 024535 and BIT57 -> 024613, and
the printed rows are 24535.32 B0 and 24613.02 10 / 24613.04 10.  All
four of the constants-listing addresses behind that sentence were
re-read at 600 dpi (PDF p.114 for BIT0 -> 024522.00, BIT10 ->
024534.00 so BIT11 -> 024535.00, and 100O -> 024503.00; p.115 for
BIT57 -> 024613.00, BIT62 -> 024620.00 and BIT63 -> 024621.00), NOT
from the 200 dpi survey render that located them.  The distinction is
not pedantry: verify_ax5b_16086_listing.py records a 200 dpi render
printing 021400.00 where 600 dpi printed 021400.40, which is what once
made a page look a half-word short.  With both ends read at full
resolution the 024522 + n rule is now bracketed rather than inferred.

100O IS A LETTER O, NOT A ZERO.  The p.114 common-constants block runs
100LC, 100Z, 100O, 100VO, 100CO; measured at 600 dpi, a digit zero in
that font is 42-47 px wide and a letter O is 49-54, and 100O's last
glyph is 51 against 42/42 for the two zeros before it.  Its defining
line says "-INDX WD. OF ONES."  The operand at 022533.40 measures 42,
43, 49 the same way.  This mattered: it is the value the suppressed
store tries to write, so getting the symbol wrong would have made the
whole point of the second half unreadable.  Note the honest margin --
p.75's third glyph at 49 px is only 2 px outside the digit range, so
it is the p.114 measurement (51 against 42/42) and the "OF ONES"
comment that carry the reading, not the p.75 pixel count alone.

TWO GLYPH CAVEATS THAT CHANGE NO BIT BUT SHOULD NOT GO UNRECORDED.
(1) The leading character of every 160xxx label on p.75 is a bare
vertical stroke, and this chain printer sets the digit 1 and the
letter I with the identical glyph -- compare "160123" against "INDX"
on p.114.  Reading them as digits is this project's standing
convention (ax5b_16086, ax5b_160102, ax5b_160_test8c all do it), not a
measurement.  (2) By the same width calibration, SEN0's fourth glyph
in its defining line on p.114 measures 54 px, which is letter-O
territory, so the symbol may really be "SENO".  The name is kept as
LSEN0 to match verify_ax5b_160_test8c_listing.py, and it cannot affect
a bit either way: LSEN0 is a SYN whose address came from the very row
("1311.40 80") that names it.

A SYN IS AN INPUT TO THIS CHECK, NOT A WITNESS.  Every symbol in the
program's SYN block was derived from the very row that names it, by
reading bit 18 out of that row's octal pair, so those rows verify only
the opcode and modifier bits.  The rows that actually check address
placement are the ones naming L160123 (022542.40, "22513.04 00"),
L160126 (022523.40, "22537.05 01") and L160Z1 (022531.40, "22542.10
00") -- all three defined INSIDE the transcribed range, and all three
cross-checked against the page's own label column before being written
down.

BIT-18 SELF-CHECKS, each decoded from the printed octal pair and read
back against the label column on p.75:

  022514.40  CB+,$X1,$-.32   22514.03 48  pair 03 -> bit18=0 -> 022514.00
  022515.40  BD,$+.32        22516.04 00  pair 04 -> bit18=0 -> 022516.00
  022517.00  BDSZ,$+.32      22517.51 C6  pair 51 -> bit18=1 -> 022517.40
  022520.00  BZDSZ,$+1.32    22521.51 C4  pair 51 -> bit18=1 -> 022521.40
  022530.00  BRZ,$+2.0       22532.34 C2  pair 34 -> bit18=0 -> 022532.00
  022531.40  B,L160Z1        22542.10 00  pair 10 -> bit18=0 -> 022542.00 = L160Z1
  022534.00  BE,$+.32        22534.40 00  pair 40 -> bit18=1 -> 022534.40
  022535.00  BD,$+.32        22535.44 00  pair 44 -> bit18=1 -> 022535.40
  022540.00  BRZ,$+1.32      22541.74 C2  pair 74 -> bit18=1 -> 022541.40
  022542.00  B,$+1.0         22543.10 00  pair 10 -> bit18=0 -> 022543.00
  022542.40  BD,L160123      22513.04 00  pair 04 -> bit18=0 -> 022513.00 = L160123
  022544.00  BD,$+.32        22544.44 00  pair 44 -> bit18=1 -> 022544.40

PROVEN DISCRIMINATING.  Observed failure sets, each measured with
__pycache__ cleared on both sides of the injection:

  INDICATOR_BITS["DS"] 19 -> 18
      022517.00, 022520.00                                   (2 rows)
  INDICATOR_BITS["RZ"] 57 -> 56
      022530.00, 022540.00                                   (2 rows)
  DIR_INDEX_CODES["SX"] 0b10001 -> 0b10000
      022514.00, 022516.40, 022517.40, 022523.00, 022534.40,
      022545.40                                              (6 rows)
  MODE_DEFAULT_BS["BU"] 8 -> 4
      022527.00, 022537.00       (the two full-word VFL rows) (2 rows)

and two more in strap_asm.py, because the four above all mutate
opcode/modifier fields and none of them perturbs BIT 18 -- which would
have left the self-check block above as hand-decoding asserted rather
than witnessed:

  the unconditional-branch/misc path's addr19 mask 0x7FFFF -> 0x7FFFE
  (i.e. bit 18 forced to zero)
      022534.00, 022535.00, 022544.00                        (3 rows)
  the branch-on-indicator path's addr19 mask, same change
      022517.00, 022520.00, 022540.00                        (3 rows)

Those six are exactly the rows in this block whose branch target is a
.40 half-word, and clearing the bit leaves every .00 target untouched
-- which is the half-word select doing precisely what the print format
says it does.

Every one of those sets is exactly the rows that use the mutated
field, and nothing else moved -- the block has no CNOP and no
alignment-dependent row, so a bad encoding cannot cascade here the way
TEST 8C's p.80 CNOP does.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("programs/ax5b_160_test8b.strap").read())

ROWS = [
    ('022513.00', '23065.02 10',
     'L160123 LX,$X1,L160XW1 (ext) "-SETUP BD, 160107 INTERRUPT TABLE"'),
    ('022513.40', '23062.04 10',
     'LX,$X2,L160K17         (ext) "-FOR TESTS 8B, 8C, 8D"'),
    ('022514.00', '23201.05 11',
     'SX,$X2,L160IT($X1)     (ext) index-modified store into the table'),
    ('022514.40', '22514.03 48',
     'CB+,$X1,$-.32           count up, loop back one half-word'),
    ('022515.00', '14.22 00',
     'Z,$MASK                 mask register (word 12)'),
    ('022515.40', '22516.04 00',
     'L160125 BD,$+.32        "-TEST 8B CHKS DS WITH SYSTEMS"'),
    ('022516.00', '24613.02 10',
     'LX,$X1,LBIT57          (ext) "-DISABLED, AND ENABLED."'),
    ('022516.40', '3.03 10',
     'SX,$X1,3.0              boundary control word'),
    ('022517.00', '22517.51 C6',
     'BDSZ,$+.32              branch on DS and zero it'),
    ('022517.40', '23063.03 10',
     'SX,$X1,L160AD1         (ext) THE STORE OUT OF BOUNDS, DISABLED'),
    ('022520.00', '22521.51 C4',
     'BZDSZ,$+1.32            disabled: DS must be OFF -- see BRANCH POLARITY'),
    ('022520.40', '1310.00 80',
     'SIC,SEN                (ext) "-SX OUT OF BOUNDS SETS DS WHEN"'),
    ('022521.00', '1304.10 00',
     'B,SERS                 (ext) "-SYSTEM DISABLED."'),
    ('022521.40', '1353.03 01',
     'LVI,$X1,LINT           (ext)'),
    ('022522.00', '23201.03 03',
     'LRI,$X1,L160IT         (ext) the 64-word table'),
    ('022522.40', '24613.04 10',
     'LX,$X2,LBIT57          (ext)'),
    ('022523.00', '3.05 10',
     'SX,$X2,3.0'),
    ('022523.40', '22537.05 01',
     'LVI,$X2,L160126         INTERNAL label -- the real address check'),
    ('022524.00', '22372.05 D0',
     'SVA,$X2,L160107        (ext) plant the handler'),
    ('022524.40', '23054.05 01',
     'LVI,$X2,L160K11        (ext)'),
    ('022525.00', '3.05 30',
     'SV,$X2,$UB              upper boundary := 160K11'),
    ('022525.40', '23041.00 80',
     'SIC,L160SX1            (ext)'),
    ('022526.00', '22741.04 00',
     'BD,L160S1              (ext) SSIP save/restore'),
    ('022526.40', '13.22 00',
     'Z,$IND'),
    ('022527.00', '13.00 80 000000.20 50',
     'L(BU),$IND              FULL WORD: read word 11 back, 64 bits BU'),
    ('022530.00', '22532.34 C2',
     'BRZ,$+2.0               branch on Result Zero (indicator 57)'),
    ('022530.40', '1310.00 80',
     'SIC,SEN                (ext) "-UNABLE TO CLR IND REGS MUST"'),
    ('022531.00', '1304.10 00',
     'B,SERS                 (ext) "-TERMINATE THIS TEST."'),
    ('022531.40', '22542.10 00',
     'B,L160Z1                INTERNAL label -- the real address check'),
    ('022532.00', '2.03 70',
     'SR,$X1,$IA'),
    ('022532.40', '13.22 00',
     'Z,$IND'),
    ('022533.00', '23063.22 00',
     'Z,L160AD1              (ext) the target starts at zero'),
    ('022533.40', '24503.04 10',
     'LX,$X2,L100O           (ext) p.114\'s "INDX WD. OF ONES"'),
    ('022534.00', '22534.40 00',
     'BE,$+.32                enable'),
    ('022534.40', '23063.05 10',
     'SX,$X2,L160AD1         (ext) THE STORE ABOVE UB, ENABLED'),
    ('022535.00', '22535.44 00',
     'BD,$+.32'),
    ('022535.40', '2.03 30',
     'SV,$X1,$IA'),
    ('022536.00', '1310.00 80',
     'SIC,SEN                (ext) "-NO INTERRUPT OCCURED ON AN"'),
    ('022536.40', '1304.10 00',
     'B,SERS                 (ext) "-SX ABOVE UB."'),
    ('022537.00', '23063.00 80 000000.20 50',
     'L160126 L(BU),L160AD1  (ext) FULL WORD: the suppression probe'),
    ('022540.00', '22541.74 C2',
     'BRZ,$+1.32              the store must NOT have landed'),
    ('022540.40', '1310.00 80',
     'SIC,SEN                (ext) "-SX ABOVE UB WAS NOT NOPED, DATA"'),
    ('022541.00', '1304.10 00',
     'B,SERS                 (ext) "-WAS STORED WHEN ENABLED."'),
    ('022541.40', '2.03 30',
     'SV,$X1,$IA'),
    ('022542.00', '22543.10 00',
     'L160Z1 B,$+1.0'),
    ('022542.40', '22513.04 00',
     'BD,L160123              INTERNAL label -- the real address check'),
    ('022543.00', '1311.40 80',
     'SIC,LSEN0+.32          (ext)'),
    ('022543.40', '1301.10 00',
     'B,LSSW                 (ext) "-TO SSIP."'),
    ('022544.00', '22544.44 00',
     'BD,$+.32'),
    ('022544.40', '22737.32 10',
     'LX,$X13,LIC260         (ext) "-UPDATE CONTINUITY CHECK."'),
    ('022545.00', '24535.32 B0',
     'V+,$X13,LBIT11         (ext) test 8B done = bit 11'),
    ('022545.40', '22737.33 10',
     'SX,$X13,LIC260        (ext)'),]

SYMBOLS = {'L160123': '022513.00', 'L160125': '022515.40',
           'L160126': '022537.00', 'L160Z1': '022542.00'}

finish(check_rows(prog, ROWS, SYMBOLS, label='1260 8B '))
