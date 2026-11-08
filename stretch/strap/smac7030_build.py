#!/usr/bin/env python3
"""smac7030_build.py -- RECONSTRUCTION scaffolding for the 7030 SMAC
(docs/smac_7030.md): compiles generators to relocatable 7030 images and
builds a loadable deck of the shell, the operation table, the library and
the input cards.

>>> SCAFFOLDING, labelled.  J28-6128 p.3 says generators were compiled by
>>> SMAC itself, with a special library of generators for the Generator
>>> Language statements, and p.2 says a library updating program added them
>>> to the library tape.  This Python file stands in for both until the
>>> 7030 SMAC can do it (docs/smac_7030.md, the order of work). <<<

CHOSEN (docs/smac_7030.md): a Generator Language statement compiles to
SIC,$15 / B,Qxxx($2) / half-word arguments.  A generator is assembled at
origin 0, so that every reference inside it is its offset from X1 (p.3,
p.13 item 2).  It can load anywhere.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import charsets                                     # noqa: E402
import smac                                         # noqa: E402
import strap_asm                                    # noqa: E402

SHELL = os.path.join(HERE, "..", "decks", "smac7030_shell.strap")
NFLAG = "(8)777777.0"
Q_SYMBOLS = ("QEXIT", "QBGEN", "QOUTF", "QOUTV")
END_MARK = "?"


class BuildError(Exception):
    pass


def iqs_card(text):
    """80 columns as an (IQS?)DD: a literal covers only its own length, so
    it must be padded, or core past it reads back uninitialised."""
    text = text.ljust(80)
    if len(text) != 80 or END_MARK in text:
        raise BuildError(f"cannot store card {text!r}")
    return f"        (IQS{END_MARK})DD(BU,640,8),{text}{END_MARK}"


def card_words(text):
    """The ten words an 80-column card must be, computed apart from the
    assembler."""
    text = text.ljust(80)
    words = []
    for w in range(10):
        v = 0
        for ch in text[w * 8:w * 8 + 8]:
            v = (v << 8) | charsets.IQS[ch]
        words.append(v)
    return words


def fmt_bits(bits):
    return f"{bits // 64}.{bits % 64}"


def compile_generator(gen, q):
    """A generator's source -> STRAP text, assembled at origin 0."""
    out = [f"{k:<8}SYN, {fmt_bits(q[k])}" for k in Q_SYMBOLS]
    out += ["        SLC, 0.0", "        SIC, $15", "        B, QBGEN($2)"]
    for b in gen.logic:
        f = smac.split_args(b["var"])
        op, a = f[0], f[1:]
        if op == "MEXIT":
            out.append("        B, QEXIT($2)")
        elif op == "MOUTF":
            if len(a) % 2 or len(a) > 30:
                raise BuildError("MOUTF: up to 15 (SK, n) pairs (p.7)")
            out += ["        SIC, $15", "        B, QOUTF($2)",
                    f"        , {len(a) // 2}"]
            for name, n in zip(a[0::2], a[1::2]):
                out += [f"        , {name}", f"        , {int(n)}"]
        elif op == "MOUTV":
            if len(a) % 3:
                raise BuildError("MOUTV takes sets of three (p.10)")
            if sum(1 for m in a[0::3] if m == "N") > 1:
                raise BuildError("MOUTV: only one M may be N (p.10)")
            out += ["        SIC, $15", "        B, QOUTV($2)",
                    f"        , {len(a) // 3}"]
            for m, name, k in zip(a[0::3], a[1::3], a[2::3]):
                mv = NFLAG if m == "N" else str(int(m))
                out += [f"        , {mv}", f"        , {name}", f"        , {int(k)}"]
        else:
            raise BuildError(f"{gen.ops}: {op} has no 7030 subroutine yet")
    for name, blocks in gen.skeletons.items():
        out += ["        CNOP", f"{name:<8}DD(BU,24), {len(blocks)}", "        CNOP"]
        for b in blocks:
            var = b["var"] + ("'" + b["comment_text"] if b["in_comment"] else "")
            out.append(iqs_card((b["col1"] or " ") + b["tag"].ljust(8) + var))
    out.append("        END, 0.0")
    return "\n".join(out) + "\n"


def link_generator(text):
    p = strap_asm.assemble(text)
    words = dict(p.words)
    if not words:
        raise BuildError("an empty generator")
    return [words.get(i, 0) for i in range(max(words) + 1)]


def build(library, ops, cards, out_cards):
    """The whole deck.  Returns (deck text, dict of the build's facts)."""
    shell = open(SHELL).read()
    stub = ("OPTX    DD(BU,64), 0\nQINP    DD(BU,64), 0\nQOUTP   DD(BU,64), 0\n"
            "OUTCNT  DD(BU,64), 0\n        END, START\n")
    sym = strap_asm.assemble(shell + stub).symtab
    q = {k: sym[k] for k in Q_SYMBOLS}

    images, seen = [], {}
    for op in ops:
        g = library.gens[op]
        if id(g) not in seen:
            seen[id(g)] = len(images)
            images.append(link_generator(compile_generator(g, q)))
    tail = ["        CNOP", "OPTAB   SYN, $"]
    offs, n = [], 0
    for im in images:
        offs.append(n)
        n += len(im)
    for op in ops:
        smac.check_op(op)
        name = op.ljust(9)
        tail += [f"        (IQS{END_MARK})DD(BU,64,8),{name[:8]}{END_MARK}",
                 f"        , LIB+{offs[seen[id(library.gens[op])]]}.0",
                 f"        (IQS{END_MARK})DD(BU,32,8),{name[8]}   {END_MARK}"]
    tail += ["        CNOP", f"OPTX    XW, OPTAB, {len(ops)}, 0",
             f"QINP    XW, INBUF, {len(cards)}, 0",
             "QOUTP   XW, OUTBUF, 0, 0", "LIB     SYN, $"]
    image = [w for im in images for w in im]
    for w in image:
        tail.append(f"        DD(BU,64), (16){w:x}")
    tail += ["        CNOP", "INBUF   SYN, $"]
    for c in cards:
        tail.append(iqs_card(c))
    tail += ["        CNOP", "OUTCNT  DD(BU,64), 0",
             f"OUTBUF  DRZ(BU,64), {out_cards * 10}",
             "        END, START"]
    deck = shell + "\n".join(tail) + "\n"
    p = strap_asm.assemble(deck)
    # controls that need no simulator: the assembler stored what was meant
    for i, c in enumerate(cards):
        for j, w in enumerate(card_words(c)):
            got = p.words.get(p.symtab["INBUF"] // 64 + i * 10 + j)
            if got != w:
                raise BuildError(f"input card {i} word {j}: {got} != {w}")
    for i, w in enumerate(image):
        if p.words.get(p.symtab["LIB"] // 64 + i) != w:
            raise BuildError(f"library word {i} did not land")
    return deck, {"prog": p, "symtab": p.symtab,
                  "outcnt_word": p.symtab["OUTCNT"] // 64,
                  "lib_words": len(image), "words": len(p.words)}
