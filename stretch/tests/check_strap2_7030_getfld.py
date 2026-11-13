#!/usr/bin/env python3
"""check_strap2_7030_getfld.py -- the 7030 STRAP II's GETFLD
(decks/strap2_7030.strap), assembled by the host STRAP II and run on the
Bluespec model, against the host's GETFLD (strap/strap2/getfld.py) and
encode() (coded.py), docs/strap2_7030.md step 2.

>>> Both are RECONSTRUCTIONS of IBM's STRAP II; agreement shows the 7030
>>> program implements the host's specification.  The printed bits of
>>> Figs. 28-29 bind the host (check_strap2_coded.py); Fig. 28 is here too,
>>> and Fig. 29 needs sub-slices b-c. <<<

SUB-SLICE a: numbers (CPLTNM, floating point), programmer symbols, + - * /,
unary minus, and the points.  The test's driver (tests/strap2_7030_gfdrive.
strap, NOT part of the reconstruction) calls GETFLD on every field of every
card block, each at a fresh word, and records each field's first bit and
the bit after it.  The host reads the same cards with Getcha and Getfld.

MEASURED INJECTIONS into the deck, 2026-11-13, restored by copy and cmp,
control all passing before and after; fields by number, CARDS in order
(0 JOE ... 6 2.3, 11 A.B, 14 A/B/C, 18 -A*B-C, 21 007, 32 A+B*C.D-E.):
  unary minus ranks with + -            field 18
  equal priority waits (right to left)  fields 14, 15, 17, 32
  a.b coded .L                          fields 6, 11, 12, 13, 32
  a point's number one too high         fields 6, 7, 8, 11, 12, 13, 32
  radix 8 when GFSRAD is zero           fields 19, 24; the ERRC 168 halt
  no zero-PR rule (Box 6 as drawn)      field 21
  symbol length in 6 bits               every field with a symbol (20)
  no end-of-datum bit                   every field but the null ones (32)
  a comma is not a null field           ERRC 0, the number of fields
  a leading plus not skipped            ERRC 0, the number of fields
  the operators not put (GFZA)          every field with an operator (21)
  no 24-bit limit                       the ERRC 168 halt
(A first form of the point-number injection added a zero field, changed
nothing and measured nothing; it was rewritten as M+1/M-1 and re-run.)
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import strap_asm                                    # noqa: E402
import strap2                                       # noqa: E402
from strap2.cards import Getcha, deck_cards         # noqa: E402
from strap2.coded import encode                     # noqa: E402
from strap2.getfld import Getfld, FieldError        # noqa: E402
from check_strap2_7030 import card, iqs_words, BSV  # noqa: E402

DECK = os.path.join(HERE, "..", "decks", "strap2_7030.strap")
DRIVE = os.path.join(HERE, "strap2_7030_gfdrive.strap")
MODULE = "StretchStrap2x7030GfTb"
STEPS = 60000000
fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f":\n  got  {got!r}\n  want {want!r}"))


CARDS = [
    card(" ", "", "JOE,7,A+B,A-B*C,-7,A*-2"),
    card(" ", "", "2.3,2.,2.+3,.2,2+.3,A.B,-A.B,X.Y+.5"),
    card(" ", "", "A/B/C,A-B-C,A*B+C*D,A+B*C-D/E,-A*B-C"),
    card(" ", "", "16777215,0,007,ABC123DEF,+5,123456"),
    card(" ", "", "PEACHES CREAM OF WHEAT+7, lower*case"),
    card(" ", "", ",,X,"),
    card(" ", "N", "A1234567890123456789012345678901234567890123456789012345678"),
    card(" ", "", "A+B*C.D-E.,X"),
    card(" ", "", "ALPHA+BET"),
    card("*", "", "A*2"),
    card(" ", "", ""),
    card(" ", "", "(((JOE - 1)/4.)*4+1)."),
]
FIG28 = 11      # Fig. 28 p.200, needs parentheses (sub-slice b)


def deck_text(cards):
    src = open(DECK).read()
    rows = []
    for c in cards:
        rows += [f"        DD(BU,64), (16){w:016X}" for w in iqs_words(c)]
    src = src.replace("INX     XW, INB, 0, 0\n", f"INX     XW, INB, {len(cards)}, 0\n", 1)
    assert src.endswith("        END\n")
    return src[:-len("        END\n")] + "\n".join(rows) + "\n" + open(DRIVE).read() + "        END, START\n"


def host(cards):
    """Each field's coded expression, as strap2 makes it, or 'refused n'."""
    g = Getcha(cards)
    f = Getfld(g, lambda name: None)
    out = []
    g.next()
    have = True
    while g.ch is not None:
        try:
            out.append(encode(f.field(have_first=have)))
        except FieldError as x:
            out.append(f"refused {x.number}")
            return out
        if g.ch == ",":
            have = False
        else:
            g.next()
            have = True
    return out


def run(cards, tmp, whole=False):
    text = deck_text(cards)
    p2 = strap2.compile_cards(deck_cards(text), strap_asm.DEFAULT_ORIGIN_BITS)

    def word(n):
        return p2.val.symbol_value(p2.st.search(n))[0] // 64
    first, last = (1024 if whole else word("OUTN")), word("OUTF") + 800
    path = os.path.join(tmp, MODULE + ".strap")
    with open(path, "w") as fh:
        fh.write(text)
    args = [os.path.join(HERE, "run_program.sh"), path, MODULE, "ASM=strap2",
            f"DUMP={first},{last - first}", f"STEPS={STEPS}", f"CYCLES<={STEPS}",
            f"FASTLOAD={os.path.join(tmp, MODULE + '.hex')}",
            f"ERRC:{word('ERRC')}=0x0"]
    r = subprocess.run(args, capture_output=True, text=True, cwd=HERE)
    for name in os.listdir(BSV):            # by exact name, never a glob
        if name in (MODULE + ".bsv", MODULE + "_sim", MODULE + "_sim.so"):
            os.remove(os.path.join(BSV, name))
    out = r.stdout
    if r.returncode or "step cap" in out:
        return None, (out + r.stderr)[-1500:]
    mem = {int(a): int(v, 16) for a, v in re.findall(r"MEMDUMP (\d+) ([0-9a-f]+)", out)}
    m = re.search(r"cycles = (\d+)", out)
    errc = re.search(r"(PASS|FAIL) ERRC = (\d+)", out)

    def bits(a, b):
        return "".join(format(mem[w], "064b") for w in range(a // 64, (b + 63) // 64))[a % 64:a % 64 + b - a]
    n = mem[word("OUTN")] >> 40
    fields = []
    for k in range(n):
        a = mem[word("OUTL") + 2 * k] >> 40
        b = mem[word("OUTL") + 2 * k + 1] >> 40
        fields.append(bits(a, b))
    return {"fields": fields, "steps": int(m.group(1)) if m else None,
            "errc": int(errc.group(2)) >> 40 if errc else None}, out


def main():
    want = host(CARDS[:FIG28])
    check("control: the host encodes all 36 fields", len(want), 36)
    halts = [("163, a digit too large for the radix (the host's 63)", "19A", 163, 63),
             ("166, a plus after an operator (the host's 66)", "A++B", 166, 66),
             ("167, a character that ends no field (the host's 67)", "7$", 167, 67),
             ("168, a number over 24 bits (the host's 68)", "16777216", 168, 68),
             ("149, a symbol over 128 characters (the host's 49)",
              ["A" * 63, "A" * 63, "A" * 3], 149, 49),
             ("9, a parenthesis: not written yet", "(A)", 9, None),
             ("9, a $: not written yet", "$X2", 9, None)]
    with tempfile.TemporaryDirectory() as tmp:
        got, out = run(CARDS[:FIG28], tmp)
        for label, stmt, errc, msg in halts:
            if isinstance(stmt, list):
                cs = [card(" ", "", stmt[0])] + [card("*", "", t) for t in stmt[1:]]
            else:
                cs = [card(" ", "", stmt)]
            h, _ = run(cs, tmp)
            check(f"ERRC {label}", h and h["errc"], errc)
            if msg is not None:
                check(f"  and the host refuses it, {msg}", host(cs)[-1], f"refused {msg}")
    if got is None:
        print("FAIL the 7030 GETFLD did not run to its halt:\n" + out)
        return 1
    check("ERRC is 0 (no failure halt)", got["errc"], 0)
    check(f"the number of fields ({len(want)})", len(got["fields"]), len(want))
    for k, (g, w) in enumerate(zip(got["fields"], want)):
        if g != w:
            check(f"field {k}", g, w)
    check("every field's coded expression equals strap2's", got["fields"], want)
    print(f"INFO model steps: {got['steps']}")
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
