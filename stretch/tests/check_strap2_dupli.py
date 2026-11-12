#!/usr/bin/env python3
"""check_strap2_dupli.py -- STRAP II's DUPLI (REPEAT): repeat the next X cards
Y times.

Sources, read in the ink 2026-11-12:
  N28-1081 (C28-6129 update, April 1963) page 1 (PDF 59): "DUPLI, X, Y / The
    DUPLI pseudo-op will cause STRAP to repeat the next X cards Y times ... X
    refers to card images, not individual instructions ... If a name appears
    on any card to be duplicated, it will not be included in the duplicated
    cards; however, a comment character in the name field will be included.
    X and Y must both be absolute numbers."  "REPEAT is an alternate mnemonic
    for DUPLI."
  C22-6729 p.27, MDUP and XINPUT: the n cards go to GETCHA as they are
    stacked, "then GETCHA gets the next n times d card images from its own
    duplicating block" -- so each card is read d + 1 times.

Before this, strap2 accepted DUPLI and did nothing.

MEASURED INJECTIONS, 2026-11-12, cards.py / pass1.py / optable.py restored by
copy and cmp, PYTHONDONTWRITEBYTECODE=1, control all passing:
  each card read d times, not d + 1   DUPLI,2,3; REPEAT; the comment check
  names kept in the copies            only the name check (A goes on the
                                      multiple list; no message is printed)
  a name-field comment blanked        only the comment check (its LX,$3,7
                                      assembles)
  REPEAT missing                      only REPEAT
  a symbolic X accepted               only the symbolic check
  a short deck accepted               only the fewer-cards check
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap2                   # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}: got {got!r}" + ("" if ok else f", want {want!r}"))


def run(*body):
    try:
        r = strap2.compile_cards(["         SLC,(8)100.0"] + list(body) + ["         END"])
    except strap2.StrapError as x:
        return "refused: " + str(x).split(":")[0], None, None
    except strap2.optable._a.AssemblerError as x:
        return "refused: " + str(x).split(" (")[0], None, None
    halves = []
    for a in sorted(r.image.words):
        w = r.image.words[a]
        halves += [w >> 32, w & 0xFFFFFFFF]
    while halves and halves[-1] == 0:
        halves.pop()
    return [n for n, *_ in r.msg.items], halves, r


_, (lx1,), _ = run("         LX,$1,5")
_, (lx2,), _ = run("         LX,$2,6")

msgs, halves, r = run("         DUPLI,2,3", " A       LX,$1,5", "         LX,$2,6")
check("DUPLI,2,3: each of the 2 cards read 3 + 1 times (p.27)", halves, [lx1, lx2] * 4)
check("DUPLI,2,3: the name is not in the copies -- A once at 100.0, not on the multiple list",
      (msgs, r.val.symbol_value(r.st.search("A"))[0], r.lists.get("multiple")), ([], 0o100 * 64, []))
check("REPEAT is DUPLI", run("         REPEAT,1,2", "         LX,$1,5")[1], [lx1] * 3)
check("DUPLI,1,0: no copies", run("         DUPLI,1,0", "         LX,$1,5")[1], [lx1])
check("a comment character in the name field is kept: the comment stays a comment",
      run("         DUPLI,2,1", "  'NOTE  LX,$3,7", "         LX,$1,5")[1], [lx1, lx1])
check("X symbolic: refused (X and Y must be absolute numbers)",
      run("         DUPLI,N,2", "         LX,$1,5")[0], "refused: DUPLI needs X and Y, both absolute numbers")
check("fewer than X cards follow: refused",
      run("         DUPLI,5,2", "         LX,$1,5")[0], "refused: DUPLI,5,2: fewer than 5 cards follow")

print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
sys.exit(1 if fails else 0)
