#!/usr/bin/env python3
"""check_problem_4_dd_refusals.py -- what C22-6578 Chapter 4 prints and
strap_asm.py refuses, pinned AS REFUSALS (a bounded negative).

The floating-point problems of Chapter 4 (4.8-4.13, printed pp.42-50)
write their constants in forms C28-6129 allows and this assembler does
not build.  The problem decks therefore carry substitutes, each marked
"printed:".  This check holds the other end: the four reproducer decks
must STILL be refused, each for its own stated reason, and the control
beside each must still assemble.  The day one of them assembles this
check fails on purpose, and the substitute in the problem decks should
be replaced by the printed card (docs/NEXT.md, "G2.1 CHAPTER 4: WHAT
THE ASSEMBLER REFUSES IN A DD(N)").

  deck                                printed form        refusal names
  decks/repro_dd_n_expression.strap   DD(N), 1/720        "cannot parse DD(N) literal '1/720'"
  decks/repro_dd_n_math_constant.strap DD(N), $N          "cannot parse DD(N) literal '$N'"
  decks/repro_dd_n_zero.strap         DD(N), 0X11         "is zero"

THE FOURTH REPRODUCER LEFT THIS LIST ON 2026-11-16 (G3.1):
decks/repro_address_multiply.strap, "V-ICR,$3,N*N-1.0", printed p.42, now
ASSEMBLES under strap_asm, to the word strap2 gives, 0007C70F 00083000
(62 half words: N*N is 64 half words, an integer in a 19-bit field, less
the bit address 1.0).  This check holds that end instead
(address_multiply_assembles), and tests/check_field_arithmetic.py holds
the arithmetic.

MEASURED INJECTIONS (python3 check_problem_4_dd_refusals.py --inject):
each reproducer's offending card replaced by its control, in memory.
    control, decks as they are            PASS, 7 checks
    every offending card replaced         FAIL the three *_refused checks,
                                          and only those
  and, 2026-11-16, strap_asm._is_arith_field made always False (the old
  tokenizer): FAIL address_multiply_assembles, and only that.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap_asm import assemble  # noqa: E402

CASES = [
    ("dd_n_expression", "repro_dd_n_expression.strap",
     "DD(N), 1/720", "DD(N), 1.388888888888888888888888889E-3",
     "cannot parse DD(N) literal '1/720'"),
    ("dd_n_math_constant", "repro_dd_n_math_constant.strap",
     "DD(N), $N", "DD(N), .6931471805599453094172321215",
     "cannot parse DD(N) literal '$N'"),
    ("dd_n_zero", "repro_dd_n_zero.strap",
     "DD(N), 0X11", "DD(N), 1X11", "is zero"),
]

# printed p.42's card, assembled: the V-ICR half word and the BEW after it.
MULTIPLY_DECK = "repro_address_multiply.strap"
MULTIPLY_WORD = 0x0007C70F00083000


def outcome(src):
    try:
        assemble(src)
        return "assembles"
    except Exception as e:      # the refusal's text is the thing checked
        return "refused: " + str(e)


def main():
    inject = "--inject" in sys.argv[1:]
    fails = 0
    for name, deck, card, control, reason in CASES:
        with open(os.path.join(HERE, "..", "decks", deck)) as f:
            src = f.read()
        if src.count(card) < 1:
            print("FAIL %s: the deck no longer has the card %r" % (name, card))
            fails += 1
            continue
        # the card as a STATEMENT is the last occurrence (the header quotes it)
        i = src.rindex(card)
        fixed = src[:i] + control + src[i + len(card):]
        if inject:
            src = fixed
        got = outcome(src)
        ok = got.startswith("refused") and reason in got
        print("%s %s_refused = %s" % ("PASS" if ok else "FAIL", name, got[:110]))
        fails += not ok
        got = outcome(fixed)
        ok = got == "assembles"
        print("%s %s_control_assembles = %s" % ("PASS" if ok else "FAIL", name, got[:110]))
        fails += not ok
    with open(os.path.join(HERE, "..", "decks", MULTIPLY_DECK)) as f:
        src = f.read()
    try:
        got = "%016X" % assemble(src).words.get(32, 0)
    except Exception as e:      # noqa: BLE001  the refusal is the failure
        got = "refused: " + str(e)
    ok = got == "%016X" % MULTIPLY_WORD
    print("%s address_multiply_assembles = %s" % ("PASS" if ok else "FAIL", got[:110]))
    fails += not ok
    print("ALL TESTS PASSED" if not fails else "FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
