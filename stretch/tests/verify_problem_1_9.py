#!/usr/bin/env python3
"""verify_problem_1_9.py METHOD -- C22-6578 Problem 1.9, checked over the
WHOLE matrix instead of a sample.

Runs decks/problem_1_9_method{METHOD}.strap on the model through
run_program.sh with a DUMP of every element and both guard words, then
compares each of the 10,000 elements with what the page asks for: "Create
the transpose of this matrix and store it in the same area."

The deck's INIT stores the index word in the location it addresses, so
the word that starts at element i of the row-wise matrix is

    value = (LOC + i).0 in bits 0-17, count = 10000 - i in bits 28-45

and after the program, element (r, c) must hold what started at (c, r).

THE REACH IS PRINTED AND A SMALL ONE FAILS.  A dump that came back short,
or a run that never reached the page's "BEW, $", must not read as a pass:
"0 mismatches" over 0 words is what this project's worst false greens
looked like (see check_deck_listing_comments.py).  The exit status is the
verdict, and the program's own status is taken without a pipeline.
"""
import os
import re
import subprocess
import sys

N = 100
LOC = 32768


def before(i):
    return ((LOC + i) << 46) | ((N * N - i) << 18)


def main():
    method = sys.argv[1]
    if method not in ('1', '2'):
        raise SystemExit("usage: verify_problem_1_9.py 1|2")
    here = os.path.dirname(os.path.abspath(__file__))
    deck = f"../decks/problem_1_9_method{method}.strap"
    sys.path.insert(0, os.path.join(here, '..', 'strap'))
    from strap_asm import assemble
    with open(os.path.join(here, deck)) as f:
        halt = assemble(f.read()).symtab['HALT'] // 32
    # gen_tb's DUMP "displays a range of core after a run"; one word
    # either side of the matrix are the guards.
    r = subprocess.run(
        ["./run_program.sh", deck, f"StretchP19M{method}Tb", f"PC={halt}",
         "STEPS=20000000", f"DUMP={LOC - 1},{N * N + 2}"],
        cwd=here, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:], r.stderr[-2000:])
        print("FAIL run_program.sh exit status", r.returncode)
        return 1
    print("\n".join(ln for ln in r.stdout.splitlines()
                    if ln.startswith(('PASS', 'FAIL', 'StretchCore: refus'))))
    dump = {int(a): int(v, 16)
            for a, v in re.findall(r"^MEMDUMP (\d+) ([0-9a-f]{16})$", r.stdout, re.M)}
    fails = 0
    if re.search(r"^FAIL ", r.stdout, re.M):
        fails += 1
    if len(dump) != N * N + 2:
        print(f"FAIL dump held {len(dump)} words, wanted {N * N + 2}")
        fails += 1
    compared = 0
    for row in range(N):
        for col in range(N):
            got = dump.get(LOC + row * N + col)
            want = before(col * N + row)
            compared += 1
            if got != want:
                fails += 1
                if fails < 10:
                    print(f"FAIL element ({row},{col}) at {LOC + row * N + col}: "
                          f"got {got if got is None else hex(got)}, want {want:#x}")
    for guard in (LOC - 1, LOC + N * N):
        compared += 1
        if dump.get(guard) != 7:
            fails += 1
            print(f"FAIL guard word {guard} is {dump.get(guard)}, want 7")
    print(f"compared {compared} words of a {N} x {N} matrix "
          f"and its two guards")
    if compared != N * N + 2:
        fails += 1
    if fails:
        print(f"{fails} TEST(S) FAILED")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == '__main__':
    sys.exit(main())
