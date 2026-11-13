#!/usr/bin/env python3
"""check_strap2_7030.py -- the 7030 STRAP II (decks/strap2_7030.strap),
assembled by the host STRAP II and run on the Bluespec model, against the host
STRAP II (strap/strap2), docs/strap2_7030.md.

>>> Both are RECONSTRUCTIONS of IBM's STRAP II, so agreement shows that the
>>> 7030 program implements the host specification, not that either is IBM's. <<<

STEP 1, XINPUT and GETCHA.  The deck's DRIVE, standing in for MAIN, calls
GETCHA to the end of the input and records each character GETCHA gives in
$3, and at each false semicolon the card block's name.  The same cards go
through strap2's Getcha, every character mapped to A8 (strap2/a8.py), the
code GETCHA gives (C22-6729 p.175).  The deck is loaded from the binary deck
strap2 punches (gen_tb.py ASM=strap2), not from the scaffolding assembler.

The run prints the model's steps, so the cost of a card is on record
(docs/strap2_7030.md asks for it before the next step): 274,565 steps for the
15 cards, about 18,300 a card, DRIVE and the load included; 8 s of Bluesim
on a quiet machine.  Now 21 cards, 356,935 steps.

FOUND BY THIS TEST, fixed in strap2/cards.py: the host gave MAIN the characters
of a comment block after its first character, against p.79 (a quote in the
name field gave the card's statement; every comment block gave its
continuation cards).  The p.79 checks below test the host alone.

MEASURED INJECTIONS, 2026-11-12, restored by copy and cmp, control all
passing before and after, observed ("chars", "names": the two comparisons):
  blanks not skipped                    chars
  column-1 comment not tested           chars
  name-field comment not tested         chars, names
  continuation mark wrong (+ for *)     chars, names, ERRC 2
  IQS to A8 one byte off                chars, names, ERRC 2
  a blank name field does not end it    names
  initial name keeps trailing blanks    names
  a comment block's continuation given  chars
  trailing blanks counted in the name   names
  continuation quote not seen           chars, names
  GCCMC not set (comment does not hold) chars
  later statement fields given after it chars
  COMREC's code not tested              ERRC 1
  no name limit                         ERRC 2
  host: name-field comment gives the    the columns 2-9 p.79 check, chars
    card's statement
  host: a comment block's continuation  both p.79 checks, chars
    given
  host: a continuation's quote kept in  the continuation p.79 check, names
    the name
  host: a continuation's comment not    chars
    seen
(One host injection first left an if with no body, a syntax error that
measured nothing; it was rewritten as valid code and re-run.)
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)
import charsets                                     # noqa: E402
import strap_asm                                    # noqa: E402
import strap2                                       # noqa: E402
from strap2.a8 import a8                            # noqa: E402
from strap2.cards import Getcha, deck_cards         # noqa: E402

BSV = os.path.join(HERE, "..", "bsv")
DECK = os.path.join(HERE, "..", "decks", "strap2_7030.strap")
DRIVE = os.path.join(HERE, "strap2_7030_drive.strap")     # the test's, not STRAP II's
MODULE = "StretchStrap2x7030Tb"
STEPS = 40000000
fails = 0


def check(label, got, want):
    global fails
    ok = got == want
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}" + ("" if ok else f": got {got!r}, want {want!r}"))


def card(col1="", name="", stmt="", ident=""):
    return (col1.ljust(1) + name.ljust(8) + stmt.ljust(63) + ident.ljust(8))[:80]


CARDS = [
    card(" ", "A", "L,B", "ID000001"),                   # a named statement
    card(" ", "", "L, $3 ,  B+1   ;  ST,C"),             # blanks; a real semicolon
    card(" ", "LONGNAM", "LX,$1,"),                      # a name, then continued
    card("*", "EXTRA", "TABLE+2.32"),                    # the name continues
    card("*", "", "($4)"),                               # a blank name field ends it
    card("*", "MORE", ",5"),                             # ... later ones are dropped
    card("'", "", "A COMMENT CARD, ALL OF IT"),          # comment: column 1
    card(" ", "AB'CD", "NOT SEEN"),                      # comment: quote in the name
    card("*", "", "SEEN ON A CONTINUATION"),             # its continuation is given
    card(" ", "lower", "lx,$2,tab"),                     # lower case folds
    card(" ", "", "B,X&?"),                              # IQS characters A8 lacks: 0
    card(" ", "", ""),                                   # an empty card
    card(" ", "N  M", "B, N M"),                         # embedded blanks kept
    card(" ", "Z", "".join("X" for _ in range(63))),     # a full statement field
    card("*", "", "Y"),                                  # it continues
    card(" ", "CM", "L,A"),                              # p.79: a comment from a
    card("*", "XY'Z", "NOT GIVEN"),                      #   continuation's name field;
    card("*", "TAIL", "NOR THIS"),                       #   the name goes on
    card(" ", "Q", "B,1"),                               # a quote in column 2 of a
    card("*", "'", "NOT GIVEN"),                         #   continuation ends the name
    card("*", "MORE", "X"),                              #   too
]


def iqs_words(c):
    v = [charsets.IQS[ch] for ch in c]
    return [int.from_bytes(bytes(v[k:k + 8]), "big") for k in range(0, 80, 8)]


def deck_text(cards, code=5):
    """The deck, its input cards after INB, then the test's driver."""
    src = open(DECK).read()
    rows = []
    for c in cards:
        rows += [f"        DD(BU,64), (16){w:016X}" for w in iqs_words(c)]
    src = src.replace("INX     XW, INB, 0, 0\n", f"INX     XW, INB, {len(cards)}, 0\n", 1)
    src = src.replace("(16)0000005000000000", f"(16){code << 36:016X}", 1)
    assert src.endswith("        END\n")
    return src[:-len("        END\n")] + "\n".join(rows) + "\n" + open(DRIVE).read() + "        END, START\n"


def host(cards):
    """strap2's Getcha: the A8 characters, and the name at each false ';'."""
    g = Getcha(cards)
    chars, names = [], []
    while True:
        c = g.next()
        if c is None:
            return chars, names
        chars.append(a8(c))
        if c == ";" and g.card is None:
            names.append([a8(x) for x in g.name.rstrip()])


def run(cards, tmp, code=5):
    text = deck_text(cards, code)
    p2 = strap2.compile_cards(deck_cards(text), strap_asm.DEFAULT_ORIGIN_BITS)

    def word(n):
        return p2.val.symbol_value(p2.st.search(n))[0] // 64
    first, last = word("OUTN"), word("NAMS") + 100
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
    steps = int(m.group(1)) if m else None
    errc = re.search(r"(PASS|FAIL) ERRC = (\d+)", out)

    def byte_at(w0, k):
        return (mem[w0 + k // 8] >> (56 - 8 * (k % 8))) & 255
    n = mem[word("OUTN")] >> 40
    chars = [byte_at(word("OUTB"), k) for k in range(n)]
    names, cur = [], []
    nams = word("NAMS")
    for k in range(((mem[word("NAMSP")] >> 40) - nams * 64) // 8):
        b = byte_at(nams, k)
        if b == 0o35:
            names.append(cur)
            cur = []
        else:
            cur.append(b)
    return {"chars": chars, "names": names, "steps": steps,
            "errc": str(int(errc.group(2)) >> 40) if errc else None}, out


def main():
    want_chars, want_names = host(CARDS)
    check("control: the host sees the 12 card blocks", len(want_names), 12)
    # p.79, read in the ink 2026-11-12: a comment started in the first nine
    # columns gives MAIN the comment character, then nothing more of the block
    # ("without giving them out to main flow through $3"), then the end of the
    # card block.  Checked on the host alone: the 7030 is compared with it below.
    for label, block in (("column 1", [card("'", "", "NOT GIVEN"), card("*", "", "NOR THIS")]),
                         ("columns 2-9", [card(" ", "AB'C", "NOT GIVEN"), card("*", "X", "NOR THIS")])):
        check(f"host, p.79: a comment in {label} gives the quote, then the false semicolon",
              host(block)[0], [0o14, 0o35])
    check("host, p.79: a continuation's comment keeps the name before it, and later names",
          [bytes(n) for n in want_names[10:]], [bytes(a8(c) for c in "CMXYTAIL"), bytes([a8("Q")])])
    with tempfile.TemporaryDirectory() as tmp:
        got, out = run(CARDS, tmp)
        bad_code, _ = run(CARDS[:2], tmp, code=3)
        long_name, _ = run([card(" ", "NAMEPART", "B,1")] + [card("*", "NAMEPART", "")] * 8, tmp)
    # The failure halts (the deck's header).  strap2 has neither: it reads
    # characters, not a coded input, and its name has no length limit.
    check("ERRC 1: COMREC's input code 3 (A8) is not written, halts before a character",
          (bad_code and bad_code["errc"], bad_code and len(bad_code["chars"])), ("1", 0))
    check("ERRC 2: a name of 72 characters is past NAMEB's 64 (a CHOSEN size)",
          long_name and long_name["errc"], "2")
    if got is None:
        print("FAIL the 7030 STRAP II did not run to its halt:\n" + out)
        return 1
    check("ERRC is 0 (no failure halt)", got["errc"], "0")
    check(f"GETCHA's characters equal strap2's ({len(want_chars)})", got["chars"], want_chars)
    check(f"the card blocks' names equal strap2's ({len(want_names)})", got["names"], want_names)
    print(f"INFO model steps for {len(CARDS)} cards: {got['steps']}"
          f" ({got['steps'] // len(CARDS) if got['steps'] else '?'} a card, DRIVE and the load included)")
    print("ALL CHECKS PASSED" if not fails else f"{fails} FAILED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
