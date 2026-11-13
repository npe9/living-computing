#!/usr/bin/env python3
"""check_strap2_7030_getfld.py -- the 7030 STRAP II's GETFLD
(decks/strap2_7030.strap), assembled by the host STRAP II and run on the
Bluespec model, against the host's GETFLD (strap/strap2/getfld.py) and
encode() (coded.py), docs/strap2_7030.md step 2.

>>> Both are RECONSTRUCTIONS of IBM's STRAP II; agreement shows the 7030
>>> program implements the host's specification.  The printed bits of
>>> Figs. 28-29 bind the host (check_strap2_coded.py) and, since sub-slices
>>> b and c, the 7030 program too. <<<

SUB-SLICE a: numbers (CPLTNM, floating point), programmer symbols, + - * /,
unary minus, and the points.  SUB-SLICE b: parentheses; Fig. 28 p.200's
printed bits are checked before the host comparison.  SUB-SLICE c: `$` and
the system symbols (BOPSER, MBSPEC as notes), Fig. 29 p.201's printed bits.
SUB-SLICE d: the g.p. and the radix.
The test's driver (tests/strap2_7030_gfdrive.strap, NOT part of the reconstruction) calls GETFLD on every field of every
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
RE-MEASURED 2026-11-13 after the points became stack operators (the
cells GFNUM and GFD went; a point now waits on GFSTK, priority 4):
  a.b coded .L (no Box 59)              fields 6, 11, 12, 13, 32
  a point's number one too high         fields 6, 7, 8, 11, 12, 13, 32
  two unary minuses allowed             the --2 halt
  two points in a datum allowed         the 2.3.4 halt
  a point ranks with * /                NOTHING: a point is pushed after its
                                        datum, so it is the top entry when
                                        the next operator comes, and any
                                        priority from 2 up puts it first
SUB-SLICE b, parentheses, MEASURED 2026-11-13 (restored by copy and cmp,
control all passing); fields 36 Fig. 28, 37 T(2,1), 38 T(2,1)(A),
39 A*(B+C), 40 -(A+B)*C, 41 (A), 42 (A)(3), 43 (A+B)(3), 44 ((A)),
45 .(A+B), 46 (A,B), 47 A(B(C(D))), 48 7.(3-6*18)(A+3.0), 49 X(A+B,C*D),
50 ((A+B)*(C-D))/E, 51 (A).B, 52 A.(B)(C), 53 the 58-character subscript,
54 Q(((R+S)*T)-(U/V),W), 55 -(((A))):
  no zero datum                         41, 42, 44, 46, 51, 55
  never arithmetic                      Fig. 28; 36, 39, 40, 43, 45, 50, 54
  spliced operators not renumbered      39, 50, 54
  end bit not held open                 Fig. 28; every field 36-55
  S/X operators not copied              48, 49, 54
  after a point .L kept                 48, 52
  GFOPS not rewound after S/X           48, 49, 54
  15 context words restored             54
  no whole-word copy                    Fig. 28; 36, 47, 48, 50, 53, 54, 55
  S/X makes a datum lone                ERRC 0 (a radix halt), field count
  depth limit 8                         the depth-over-7 halt
  after a datum taken as a start        37, 38; ERRC 0, field count
(A first form of the point-number injection added a zero field, changed
nothing and measured nothing; it was rewritten as M+1/M-1 and re-run.)
SUB-SLICE c, $ and system symbols, MEASURED 2026-11-13 (restored by copy and
cmp, control all passing); fields 56-57 Fig. 29, then 58 $, 59 A+$, 60 $X2,
61 $15, 62 $CPU, 63 $IND, 64 $X2+3, 65 A($X3), 66 $XO, 67 $1ND, 68 -$,
69 $.4, 70 ($X2), 71 $51T:
  BOPSER's compare reversed             ERRC 0, Fig. 29, NOTEC, field count
  the key zero-filled                   ERRC 0, Fig. 29, NOTEC, field count
  no dds                                Fig. 29; 56, 57, 60-67, 70, 71
  Fig. 14's + before .L                 58, 59, 68, 69
  $ alone's length 0 (Fig. 14 drawn)    58, 59, 68, 69
  no MBSPEC                             ERRC 0, NOTEC, field count
  MBSPEC never restores                 ERRC 0, NOTEC, field count
  129 not counted                       NOTEC only
  a system datum absolute               ERRC 0, NOTEC, field count
(Each "ERRC 0" set also fails "every field equals strap2's".  MBSPEC never
restores measured NOTHING until $51T was added: $XO and $1ND are found on
the counter's first step, $51T -> SIT only on its third, through a carry.)
SUB-SLICE d, g.p. and radix, MEASURED 2026-11-13 (restored by copy and cmp,
control all passing); fields 72 (8)17, 73 (16)10, 74 (8)7+A(.12)9,
75 A(.3)5, 76 (.3)5, 77 -(.3)5, 78 A+(.3)5, 79 A.(.3)5, 80 A(.3,8)17,
81 A(8,.3)17, 82 A(.3)(.4)5, 83 A(.3)B(.12)C+1, 84 A(.3)+5, 85 A(.3,B),
86 A.(8)17, 87 A.(8)(B+1), 88 (8)(.3)5, 89 2*(8)17+1, 90 ((8)17)5,
91 (8).5, 92 X(B)(.6)7:
  a g.p.'s items' operators not spent   74, 75, 78-84, 92
  n and r in the current radix          74
  the decimal times 8, not 10           73, 74, 83
  (r,.n) read as (.n,r)                 ERRC 0 (a 163 halt), field count
  r not the value's radix               80, 81; the 163 halt for A(.3,8)9
  no data before a g.p. not null        76, 77, 88
  a value's null taken as the field's   82
  a g.p. allowed in parentheses         the 166 halt for (A(.3)5)
  after a point's radix a ( keeps .L    87
  a radix after a point as at a start   86, 87
  a radix at a datum's start not one    ERRC 0, field count; the 163 halt
                                        for (8)19
(Each field set also fails "every field equals strap2's".  The first
"(r,.n)" injection swapped one store of two and measured NOTHING: r kept
the previous field's 8; it was redone swapping both.  "A g.p. with no value
accepted" measured NOTHING: the end of the field where a value's datum is
expected is already GFE's 166, so the check was dead and was removed, then
the control and the redone injection re-run on the deck without it.)
Field 93 A.(8)(.3)5, MEASURED 2026-11-13: the host gave .+ 1 there (fixed,
check_strap2_getfld_paren.py); the 7030 program gives .L 0, as for A.(.3)5.
  a g.p. after a point's radix makes .L .+   93
Bcfxtx (Box 55 GFLONG), MEASURED 2026-11-13; the driver gives each field
64 words, a 3998-bit field passes and a 4498-bit one halts 11:
  GFLONG never halts                    the 11 halt
  no check at the field's end (GFX)     the 11 halt
  the limit taken from Bcfldx           every field: ERRC 0, Figs. 28-29,
                                        NOTEC, field count, five halts
  no check after an operator (Box 55)   NOTHING: the exit check halts 11
                                        all the same; Box 55 only halts
                                        sooner, and is kept as the chart
                                        draws it
  checked inside parentheses too        NOTHING: GFSCR lies below the
                                        driver's OUTF, so a scratch address
                                        never compares high; kept, since
                                        MAIN's buffer may lie below GFSCR
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
from strap2.optable import system_symbol           # noqa: E402
from check_strap2_7030 import card, iqs_words, BSV  # noqa: E402

DECK = os.path.join(HERE, "..", "decks", "strap2_7030.strap")
DRIVE = os.path.join(HERE, "strap2_7030_gfdrive.strap")
MODULE = "StretchStrap2x7030GfTb"
STEPS = 60000000
fails = 0
CHANGED = []    # the host's MBSPEC alterations, message 129 (p.178)


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
    card(" ", "", "T(2,1),T(2,1)(A),A*(B+C),-(A+B)*C,(A),(A)(3),(A+B)(3)"),
    card(" ", "", "((A)),.(A+B),(A,B),A(B(C(D))),7.(3-6*18)(A+3.0)"),
    card(" ", "", "X(A+B,C*D),((A+B)*(C-D))/E,(A).B,A.(B)(C)"),
    card(" ", "", "A(PEACHESCREAMOFWHEATANDMILKANDHONEYANDSUGARANDTOASTANDJAM)"),
    card(" ", "", "Q(((R+S)*T)-(U/V),W),-(((A)))"),
    card(" ", "", "PEACHES CREAM OF WHEAT +7.(3-6*18)($X2+3.0), MILK-CREAM ($X3+7)"),
    card(" ", "", "$,A+$,$X2,$15,$CPU,$IND,$X2+3,A($X3),$XO,$1ND,-$,$.4,($X2),$51T"),
    card(" ", "", "(8)17,(16)10,(8)7+A(.12)9,A(.3)5,(.3)5,-(.3)5,A+(.3)5,A.(.3)5"),
    card(" ", "", "A(.3,8)17,A(8,.3)17,A(.3)(.4)5,A(.3)B(.12)C+1,A(.3)+5,A(.3,B)"),
    card(" ", "", "A.(8)17,A.(8)(B+1),(8)(.3)5,2*(8)17+1,((8)17)5,(8).5,X(B)(.6)7"),
    card(" ", "", "A.(8)(.3)5"),
]
FIG29 = 56      # Fig. 29 p.201: its two fields' printed bits
FIG28 = 11      # Fig. 28 p.200: its printed bits, before the host comparison


def a8sym(t):
    from strap2.a8 import a8_bits
    from strap2.bits import field
    return "100" + field(len(t), 7) + a8_bits(t)


def fig28_printed():
    """As tests/check_strap2_coded.py writes Fig. 28, p.200, read in the ink."""
    from strap2.bits import field

    def abs24(n):
        return "110" + field(n, 24)

    def op(code, n):
        return "1" + code + field(n, 5)
    return ("1000" + a8sym("JOE") + "0" + abs24(1) + "0" + abs24(4) + "0" +
            abs24(4) + "0" + abs24(1) + "0" + "0" +
            op("000", 1) + op("110", 3) + op("010", 2) + op("011", 3) +
            op("001", 4) + op("110", 5) + "0" + "0")


def fig29_printed():
    """As tests/check_strap2_coded.py writes Fig. 29, p.201, read in the ink."""
    from strap2.bits import field

    def abs24(n):
        return "110" + field(n, 24)

    def op(code, n):
        return "1" + code + field(n, 5)
    sysd = "1010000001000"
    a = ("1000" + a8sym("PEACHESCREAMOFWHEAT") + "0" + abs24(7) +
         "1000" + abs24(3) + "0" + abs24(6) + "0" + abs24(18) + "0" + "0" +
         op("011", 2) + op("000", 1) + "0" +
         "1000" + "11100" + field(18 * 64, 24) + sysd + "0" +
         abs24(3) + "0" + abs24(0) + "0" + "0" +
         op("111", 2) + op("001", 1) + "0" +
         "0" + "0" +
         op("111", 2) + op("001", 1) + "0" + "0")
    b = ("1000" + a8sym("MILK") + "0" + a8sym("CREAM") +
         "1000" + "11100" + field(19 * 64, 24) + sysd + "0" +
         abs24(7) + "0" + "0" + op("001", 1) + "0" +
         "0" + "0" + op("000", 1) + "0" + "0")
    return [a, b]


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
    f = Getfld(g, system_symbol, changed=lambda written, used: CHANGED.append((written, used)))
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
            f"ERRC:{word('ERRC')}=0x0", f"NOTEC:{word('NOTEC')}=0x0"]
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
    notec = re.search(r"(PASS|FAIL) NOTEC = (\d+)", out)

    def bits(a, b):
        return "".join(format(mem[w], "064b") for w in range(a // 64, (b + 63) // 64))[a % 64:a % 64 + b - a]
    n = mem[word("OUTN")] >> 40
    fields = []
    for k in range(n):
        a = mem[word("OUTL") + 2 * k] >> 40
        b = mem[word("OUTL") + 2 * k + 1] >> 40
        fields.append(bits(a, b))
    return {"fields": fields, "steps": int(m.group(1)) if m else None,
            "errc": int(errc.group(2)) >> 40 if errc else None,
            "notes": int(notec.group(2)) >> 40 if notec else None}, out


def main():
    want = host(CARDS)
    check("control: the host encodes all 94 fields", len(want), 94)
    check("control: the host's Fig. 29 is the printed one", want[FIG29:FIG29 + 2], fig29_printed())
    check("control: the host's MBSPEC changes $XO, $1ND, $51T (129)", CHANGED,
          [("XO", "X0"), ("1ND", "IND"), ("51T", "SIT")])
    check("control: the host's Fig. 28 is the printed one", want[36], fig28_printed())
    halts = [("163, a digit too large for the radix (the host's 63)", "19A", 163, 63),
             ("166, a plus after an operator (the host's 66)", "A++B", 166, 66),
             ("167, a character that ends no field (the host's 67)", "7$", 167, 67),
             ("168, a number over 24 bits (the host's 68)", "16777216", 168, 68),
             ("149, a symbol over 128 characters (the host's 49)",
              ["A" * 63, "A" * 63, "A" * 3], 149, 49),
             ("167, a second point in one datum (the host's 67)", "2.3.4", 167, 67),
             ("166, a second unary minus (the host's 66)", "--2", 166, 66),
             ("166, a second point before a datum (the host's 66)", "..2", 166, 66),
             ("166, an empty parenthesis (the host's 66)", "()", 166, 66),
             ("166, an empty item (the host's 66)", "(A,)", 166, 66),
             ("167, a parenthesis not closed (the host's 67)", "(A", 167, 67),
             ("166, a g.p. with no value (the host's 66)", "A(.3)", 166, 66),
             ("166, a g.p. inside parentheses (the host's 66)", "(A(.3)5)", 166, 66),
             ("163, a g.p.'s value in its radix r (the host's 63)", "A(.3,8)9", 163, 63),
             ("163, a digit too large for a radix prefix (the host's 63)", "(8)19", 163, 63),
             ("10, parentheses deeper than 7", "((((((((A))))))))", 10, None),
             ("156, a system symbol not found (the host's 56)", "$QQQ", 156, 56),
             ("156, a system symbol of 9 characters (the host's 56)", "$ABCDEFGHI", 156, 56),
             ("9, a tail: TAILOR is step 4", "A$B", 9, None),
             ("0, control: 3998 bits in a 4096-bit buffer (Bcfxtx)",
              [c * 60 + "+" for c in "ABCDEFG"] + ["K" * 60], 0, None),
             ("11, 4498 bits past a 4096-bit buffer (Bcfxtx, Box 55)",
              [c * 60 + "+" for c in "ABCDEFGH"] + ["K" * 60], 11, None)]
    with tempfile.TemporaryDirectory() as tmp:
        got, out = run(CARDS, tmp)
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
    check("Fig. 28 p.200: the 7030 GETFLD gives the printed bits",
          got["fields"][36] if len(got["fields"]) > 36 else None, fig28_printed())
    check("Fig. 29 p.201: the 7030 GETFLD gives the printed bits",
          got["fields"][FIG29:FIG29 + 2], fig29_printed())
    check("message 129 three times, as notes (NOTEC)", got["notes"], 3)
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
