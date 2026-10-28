#!/usr/bin/env python3
"""cards.card_words_cols -- raw 12-bit column punching, and the IOD
card's field position, CORRECTED.

>>> THIS FILE ONCE ASSERTED SOMETHING FALSE AND THE ASSERTION IS THE
POINT OF THE CORRECTION. <<<  It claimed the IOD card's field begins at
CARD COLUMN 32, by dividing `Y UTOE`'s offset of 372 bits by twelve
bits per column.  The arithmetic was right and the proposition was
false, because **`Y UCBF1` does not hold the card image.**

`C22-6728-1` printed p.66: "Uncode uses two subroutines, SCA6 and
SBRK8, respectively to convert the card to BCD", and "Y UTOE is the
symbolic location of the reference number on a BCD IOD card.  Cards are
converted to BCD into Y UCBF1."  So `Y UCBF1` holds SCA6's output --
**six bits per character** -- and the divisor is 6, not 12.

THE CLINCHER IS IN THE LISTING, and it is a refutation rather than a
preference.  Line 2156 of `docs/ocr/MCP_Mar63_001-249.txt` is
`VF,YUCBF1+.54`, the second argument of the same call sequence:

    54 / 6  = 9 exactly -> character 10 = column 10, and the CF,53
                           beside it gives columns 10-62, which is the
                           documented statement field
    54 / 12 = 4.5       -> MID-COLUMN, which no character-string
                           argument can be

**54 is not divisible by twelve.**  The twelve-bit reading is not
merely less likely; it is impossible for that argument.

WHAT THE SIX-BIT READING GIVES, and all four agree:

  * 372 / 6 = 62 -> the field starts at CARD COLUMN 63;
  * 372 + 60 = 432 = 72 * 6 -> it ENDS at column 72, the documented
    last column of the IOD statement area (73-80 are program ID);
  * `LF(BU,60,6), YUTOE` reads ten six-bit bytes, and `C22-6678-1`
    printed p.9 gives I/O Reference Number = cols 63-66 (four) and
    Absolute Exit = cols 67-72 (six) -- four plus six is ten;
  * the listing's own comment on the SYN names both fields:
    "LOCATION OF REF # AND TOE".

WHAT IS STILL TRUE, because the correction is narrower than it looks.
A CARD COLUMN REALLY IS TWELVE BITS (`R23-9702` Figure 4.3-1, and
`cards.WORDS_PER_CARD` is 80 * 12 // 64 = 15 exactly) and SCA6 reads
the card that way -- its own call passes `CF,80`, eighty columns in.
`card_words_cols` is therefore still correct and still useful.  Only
its MOTIVATION was wrong: after SCA6 there is **one** six-bit character
per column, so "two octal digits per column, which no single character
can punch" describes nothing.  The raw-column path remains the right
way to punch a field a keypunch has no character for; the IOD's field
simply is not such a field.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "strap"))
import cards

fails = 0

def check(label, got, want):
    global fails
    if got == want:
        print(f"PASS {label} = {got}")
    else:
        print(f"FAIL {label} = {got}, expected {want}")
        fails += 1

# 1. No overrides must be byte-for-byte the character path.
for line in ("B", "BIOCD", "IOD", "", "X" * 80):
    check(f"no_override_matches_card_words[{len(line)}]",
          cards.card_words_cols(line), cards.card_words(line))

# 2. A card column is twelve bits.  Still true, still the basis of
#    card_words_cols, and independently confirmed by R23-9695 line 300
#    ("in the no-ECC mode ... 15 full words", "13 full words ... 78 card
#    columns, with the last two columns ignored").
BITS_PER_COLUMN = 12
check("bits_per_column", cards.COLUMNS * BITS_PER_COLUMN // 64,
      cards.WORDS_PER_CARD)

# 3. Y UCBF1 IS A BCD BUFFER, SIX BITS PER CHARACTER -- and the proof is
#    a refutation, not a preference.  The listing's own second argument
#    into the same buffer is YUCBF1+.54, and 54 is NOT divisible by 12.
BITS_PER_BCD_CHAR = 6
check("yucbf1_second_argument_54_is_not_a_12_bit_column_boundary",
      54 % BITS_PER_COLUMN != 0, True)
check("yucbf1_second_argument_54_is_a_6_bit_character_boundary",
      54 % BITS_PER_BCD_CHAR, 0)
check("yucbf1_54_is_character_10_so_column_10",
      54 // BITS_PER_BCD_CHAR + 1, 10)
# 53 characters from column 10 is the documented statement field, 10-62
check("statement_field_ends_at_column_62", 10 + 53 - 1, 62)

# 4. So Y UTOE's 372 bits is CARD COLUMN 63, and the field ends at 72.
check("yutoe_372_is_a_character_boundary", 372 % BITS_PER_BCD_CHAR, 0)
check("yutoe_372_is_column_63_one_based",
      372 // BITS_PER_BCD_CHAR + 1, 63)
check("iod_field_ends_at_column_72", (372 + 60) // BITS_PER_BCD_CHAR, 72)
# C22-6678-1 printed p.9: reference number cols 63-66, exit cols 67-72
check("iod_field_is_ten_characters", (66 - 63 + 1) + (72 - 67 + 1), 10)
# and LF(BU,60,6) reads exactly that many six-bit bytes
check("lf_60_6_reads_ten_bytes", 60 // BITS_PER_BCD_CHAR, 10)

# 5. An override writes exactly its own twelve bits and nothing else.
#    Read the whole card back as one 960-bit integer and compare.
def as_int(words):
    v = 0
    for w in words:
        v = (v << 64) | w
    return v

base = as_int(cards.card_words_cols(" " * 80))
PATTERN = 0b000010000011          # two six-bit halves: 2 and 3
# Column index 62 is CARD COLUMN 63 -- the IOD field's real first
# column, so the override test exercises the place that matters.
IOD_FIRST_COL0 = 62
over = as_int(cards.card_words_cols(" " * 80, {IOD_FIRST_COL0: PATTERN}))
TOTAL = cards.COLUMNS * BITS_PER_COLUMN
shift = TOTAL - IOD_FIRST_COL0 * BITS_PER_COLUMN - BITS_PER_COLUMN
check("override_sets_card_column_63_bits", (over >> shift) & 0xFFF, PATTERN)
check("override_touches_nothing_else", over ^ base, PATTERN << shift)

# 6. The override's two six-bit halves are independently placed.
check("card_column_63_first_half", ((over >> shift) >> 6) & 0x3F, 2)
check("card_column_63_second_half", (over >> shift) & 0x3F, 3)

# 7. Refusals, because a silent truncation here would be a wrong card.
for bad, why in (({31: 1 << 12}, "thirteen bits"),
                 ({80: 1}, "column past the card"),
                 ({-1: 1}, "negative column")):
    try:
        cards.card_words_cols(" " * 80, bad)
        print(f"FAIL refuses_{why.replace(' ', '_')} = accepted")
        fails += 1
    except ValueError:
        print(f"PASS refuses_{why.replace(' ', '_')}")

if fails:
    print(f"{fails} TEST(S) FAILED")
    sys.exit(1)
print("ALL TESTS PASSED")
