#!/usr/bin/env python3
"""cards.card_words_cols -- raw 12-bit column punching, and the one
relation the IOD card's field map rests on.

printed p.40 lines 14-22 convert ten SIX-BIT fields off an IOD card,
starting at `Y UTOE`, which printed p.41 line 37 defines as
`Y UCBF1+.372` -- 372 bits into the card buffer.  A card column is
twelve bits (R23-9702 Figure 4.3-1, and cards.WORDS_PER_CARD is
80 * 12 // 64 = 15 exactly), so 372 / 12 = 31 with no remainder and
the field begins at CARD COLUMN 32, one-based.  That division is the
whole derivation and this file pins it.

Two octal digits per column is why `card_words_cols` had to exist: no
single character punches a column whose two six-bit halves are
independent values.
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

# 2. Y UTOE's 372 bits IS column 32, one-based -- the derivation.
BITS_PER_COLUMN = 12
check("bits_per_column", cards.COLUMNS * BITS_PER_COLUMN // 64,
      cards.WORDS_PER_CARD)
check("yutoe_372_is_a_column_boundary", 372 % BITS_PER_COLUMN, 0)
check("yutoe_372_is_column_32_one_based", 372 // BITS_PER_COLUMN + 1, 32)

# 3. An override writes exactly its own twelve bits and nothing else.
#    Read the whole card back as one 960-bit integer and compare.
def as_int(words):
    v = 0
    for w in words:
        v = (v << 64) | w
    return v

base = as_int(cards.card_words_cols(" " * 80))
PATTERN = 0b000010000011          # two six-bit halves: 2 and 3
over = as_int(cards.card_words_cols(" " * 80, {31: PATTERN}))
TOTAL = cards.COLUMNS * BITS_PER_COLUMN
shift = TOTAL - 372 - BITS_PER_COLUMN
check("override_sets_column_32_bits", (over >> shift) & 0xFFF, PATTERN)
check("override_touches_nothing_else", over ^ base, PATTERN << shift)

# 4. The two halves really are independent six-bit values.
check("column_32_first_half", ((over >> shift) >> 6) & 0x3F, 2)
check("column_32_second_half", (over >> shift) & 0x3F, 3)

# 5. Refusals, because a silent truncation here would be a wrong card.
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
