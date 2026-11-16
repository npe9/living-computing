#!/usr/bin/env python3
"""verify_buchholz_b6.py printed|corrected [DECK] -- Buchholz Appendix B,
Table B.6, "Transposition of a Large Bit Matrix" (printed pp.303-304),
checked over EVERY word of the 128-by-128 matrix.

    printed    decks/buchholz_b6_bit_matrix_transpose.strap as it stands.
               THE TABLE AS PRINTED DOES NOT TRANSPOSE: its line 101.32 is
               "CONNECT 0011 (V + I) (VBU, 1, 1)", and a byte size of 1 makes
               each step replace eight accumulator bits (the book's own
               sec. 7.14, printed pp.90-91; Reference Manual 22-6530-2 printed
               p.75).  The deck's header works out what that leaves: each
               stored word holds the LAST of its 64 bits, in bit 63, and
               nothing else.  This mode checks exactly that.
    corrected  the same deck with that one data description rewritten as
               (BU,1,8) -- one accumulator bit per step -- which is done here,
               in memory, and nowhere else.  The output must be the
               transpose.

The expectations are computed from the matrix A that is in the deck, by
definition; nothing is taken from a run.  With the output's row j, word w,
bit i (bit 0 the leftmost):

    corrected:  B[j][w] bit i  ==  A[64w + i][j]
    printed:    B[j][w] bit 63 ==  A[64w + 63][j],  bits 0-62 zero

Also checked, in both modes: A is untouched (every word), the guard word
either side of A and of B, the three index registers (worked in the deck's
header) and the halt at 106.32.

A second argument names another copy of the deck: that is how an injection
is run without editing the one in decks/.

THE REACH IS PRINTED AND A SHORT ONE FAILS.  A dump that came back short, or
a run that never reached the BEW, must not read as a pass.
"""
import os
import re
import subprocess
import sys
import tempfile

N = 2
ROWS = 64 * N
A0, B0 = 1000, 2000
WORDS = ROWS * N
PRINTED_DDS = "C0011(V+I)(BU,1,1), 2.0($1), 63($3)"
CORRECT_DDS = "C0011(V+I)(BU,1,8), 2.0($1), 63($3)"


def main():
    if len(sys.argv) not in (2, 3) or sys.argv[1] not in ("printed", "corrected"):
        raise SystemExit("usage: verify_buchholz_b6.py printed|corrected [DECK]")
    mode = sys.argv[1]
    here = os.path.dirname(os.path.abspath(__file__))
    path = sys.argv[2] if len(sys.argv) == 3 else os.path.join(
        here, "..", "decks", "buchholz_b6_bit_matrix_transpose.strap")
    with open(path) as f:
        src = f.read()
    code = [ln for ln in src.splitlines() if not ln.lstrip().startswith("!")]
    if sum(PRINTED_DDS in ln for ln in code) != 1:
        print("FAIL the deck does not have the printed line 101.32 exactly once")
        return 1
    if mode == "corrected":
        src = "\n".join(ln.replace(PRINTED_DDS, CORRECT_DDS)
                        if not ln.lstrip().startswith("!") else ln
                        for ln in src.splitlines()) + "\n"
    sys.path.insert(0, os.path.join(here, "..", "strap"))
    from strap_asm import assemble
    image = dict(assemble(src).words)
    a_words = [image.get(A0 + k, 0) for k in range(WORDS)]

    def a_bit(r, c):
        return (a_words[r * N + c // 64] >> (63 - c % 64)) & 1

    with tempfile.TemporaryDirectory() as tmp:
        deck = os.path.join(tmp, "b6.strap")
        with open(deck, "w") as f:
            f.write(src)
        r = subprocess.run(
            ["./run_program.sh", deck, "StretchBuchB6Tb", "PC=213", "STEPS=3000000",
             "x1:17=0x00FA8000000000C9", "x2:18=0x02340000000800CA",
             "x3:19=0x00000000010000CB",
             f"guard_below_a:{A0 - 1}=99", f"guard_above_a:{A0 + WORDS}=99",
             f"guard_below_b:{B0 - 1}=99", f"guard_above_b:{B0 + WORDS}=99",
             f"DUMP={A0},{B0 + WORDS - A0}"],
            cwd=here, capture_output=True, text=True)
    lines = [ln for ln in r.stdout.splitlines()
             if ln.startswith(("PASS", "FAIL", "StretchCore: OP SET"))]
    print("\n".join(lines))
    if r.returncode != 0 and not lines:
        print(r.stdout[-2000:], r.stderr[-2000:])
        print("FAIL run_program.sh exit status", r.returncode)
        return 1
    fails = sum(1 for ln in lines if ln.startswith(("FAIL", "StretchCore: OP SET")))
    dump = {int(a): int(v, 16)
            for a, v in re.findall(r"^MEMDUMP (\d+) ([0-9a-f]{16})$", r.stdout, re.M)}
    read = 0
    a_bad = b_bad = 0
    first = []
    for k in range(WORDS):
        if A0 + k not in dump:
            continue
        read += 1
        if dump[A0 + k] != a_words[k]:
            a_bad += 1
    for j in range(ROWS):
        for w in range(N):
            addr = B0 + j * N + w
            if addr not in dump:
                continue
            read += 1
            want = 0
            for i in range(64):
                if mode == "corrected" or i == 63:
                    want |= a_bit(64 * w + i, j) << (63 - i)
            if dump[addr] != want:
                b_bad += 1
                if len(first) < 3:
                    first.append(f"  word {addr} (row {j}, word {w}) = {dump[addr]:016x}, expected {want:016x}")
    what = "the transpose" if mode == "corrected" else "one bit per word, as the printed line leaves it"
    print(f"{'PASS' if a_bad == 0 else 'FAIL'} A untouched: {WORDS - a_bad} of {WORDS} words")
    print(f"{'PASS' if b_bad == 0 else 'FAIL'} B is {what}: {WORDS - b_bad} of {WORDS} words")
    for ln in first:
        print(ln)
    fails += (a_bad > 0) + (b_bad > 0)
    print(f"{read} of {2 * WORDS} matrix words read back; {a_bad + b_bad} of them wrong; "
          f"{fails} check(s) failed")
    if read != 2 * WORDS:
        print("FAIL short reach")
        return 1
    if fails:
        print("1 TEST(S) FAILED")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
