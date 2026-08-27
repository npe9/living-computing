#!/usr/bin/env python3
"""verify_dcp_maintenance_compool.py -- assembles
programs/dcp_maintenance_compool.strap and checks every resolved SYN
value against the DCP manual's own printed (octal word.bit) column,
transcribed as a trailing comment on each source line
(`! WWWW.BB`, octal). This is the real oracle the compool transcription
was previously blocked on for lack of (see strap_asm.py's SYN work and
docs/archival_inventory.md) -- 63 independent checks (all entries
except the two base-defining lines ACA and EDCP1, which don't carry
their own printed-column comment since ACA's is a bare literal and
EDCP1 isn't itself a row in the manual's table).

Run standalone: `./verify_dcp_maintenance_compool.py`. Pure Python, no
Bluesim -- SYN has no machine-instruction semantics, only symbol-table
resolution (same reasoning as test_syn.py). Wired into run_tests.sh.
"""

import re
import sys

from strap_asm import assemble

FAILS = 0
CHECKED = 0

# Matches "NAME  SYN, EXPR  ! WWWW.BB" (WWWW/BB are octal, in the
# manual's own printed notation) -- skips comment-only and blank lines,
# and the two base-symbol lines (ECTL1 etc, ACA, EDCP1), which have no
# such printed-column comment of their own.
ROW_RE = re.compile(
    r'^(?P<name>[A-Z][A-Z0-9]*)\s+SYN,\s*(?P<expr>[^!]+?)\s*!\s*(?P<word>[0-7]+)\.(?P<bit>[0-7]{2})\b')


def octal_word_bit_to_bits(word_oct, bit_oct):
    """Convert the manual's printed octal word.bit notation to this
    model's bit-address units (word*64 + bit), matching
    strap_asm.py's own eval_expr bitaddr handling."""
    word = int(word_oct, 8)
    bit = int(bit_oct, 8)
    return word * 64 + bit


def main():
    global FAILS, CHECKED
    src = open('programs/dcp_maintenance_compool.strap').read()
    prog = assemble(src)

    for lineno, raw in enumerate(src.splitlines(), 1):
        m = ROW_RE.match(raw.strip())
        if not m:
            continue
        name = m.group('name')
        expected = octal_word_bit_to_bits(m.group('word'), m.group('bit'))
        got = prog.symtab.get(name)
        CHECKED += 1
        if got is None:
            print(f"FAIL line {lineno}: {name} never made it into symtab")
            FAILS += 1
        elif got != expected:
            print(f"FAIL line {lineno}: {name} = {got} (word.bit "
                  f"{got // 64}.{got % 64}), expected {expected} "
                  f"(printed {m.group('word')}.{m.group('bit')} octal)")
            FAILS += 1
        else:
            print(f"PASS {name} = {got} (matches printed "
                  f"{m.group('word')}.{m.group('bit')} octal)")

    print(f"\n{CHECKED} entries checked against the manual's printed column")
    # Exact, not a threshold: this file has exactly 64 rows carrying a
    # printed-column comment (65 SYN entries total minus EDCP1, which
    # is a derived base with no printed-column row of its own -- see
    # the file's header). A threshold check ("< 60") would keep passing
    # even if rows were silently dropped in a future edit; only an
    # exact count catches that (advisor review).
    EXPECTED_ROWS = 64
    if CHECKED != EXPECTED_ROWS:
        print(f"FAIL: expected exactly {EXPECTED_ROWS} checkable entries, "
              f"found {CHECKED} -- either ROW_RE isn't matching some "
              f"lines, or a row was added/dropped without updating this "
              f"count")
        FAILS += 1

    if FAILS == 0:
        print("ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"{FAILS} TEST(S) FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
