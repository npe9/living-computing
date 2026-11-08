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

CHOSEN (docs/smac_7030.md): core above the deck holds the inner-macro stack.
A Generator Language statement compiles to
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
Q_SYMBOLS = ("QEXIT", "QBGEN", "QOUTF", "QOUTV", "QMVPT", "QOUT", "QGETL",
             "QKPEQ", "QKPNE", "QKCEQ", "QKCNE", "QDBUGB", "QMIBIT", "QCIBIT",
             "QMACBIT", "QINBIT", "QERRBIT", "QERR", "QCOUNT", "QPT1", "QPT2",
             "QPT3", "QPT4", "QPT5", "QLIT", "QCN", "QGUB")
POINTERS = ("QPT1", "QPT2", "QPT3", "QPT4", "QPT5")
COMPARES = {"MKPEQ": "QKPEQ", "MKPEQI": "QKPEQ", "MKPNEQ": "QKPNE", "MKPNEQI": "QKPNE",
            "MKCEQ": "QKCEQ", "MKCEQI": "QKCEQ", "MKCNEQ": "QKCNE", "MKCNEQI": "QKCNE"}
MARKS = "?\"&:="         # an (IQSx) end mark must not occur in its text


class BuildError(Exception):
    pass


def iqs_text(text, width):
    """An (IQSx)DD of WIDTH characters.  A literal covers only its own
    length, so it is padded, or core past it reads back uninitialised."""
    text = text.ljust(width)
    if len(text) != width:
        raise BuildError(f"text wider than {width}: {text!r}")
    for m in MARKS:
        if m not in text:
            return f"(IQS{m})DD(BU,{width * 8},8),{text}{m}"
    raise BuildError(f"no end mark is free for {text!r}")


def iqs_card(text):
    return "        " + iqs_text(text, 80)


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


def pointer(name):
    if name not in POINTERS:
        raise BuildError(f"{name} is not QPT1-QPT5 (p.5)")
    return name


def compile_generator(gen, q, library=None):
    """A generator's source -> STRAP text, assembled at origin 0.  Word 0 is
    the generator's usage bit, behind QGUB (p.13).  A STRAP statement in the
    logic is assembled as it stands, which is why p.13 items 2-3 make its
    references go through X1 and X2.  A SMAC statement in the logic (p.12)
    is expanded first.  The SYN cards come last, as MEGEN puts them (p.5)."""
    out = ["        SLC, 0.0", "        DD(BU,64), 0",
           "        SIC, $15", "        B, QBGEN($2)"]

    def call(tag, q_name, *args):
        out.append(f"{tag:<8}SIC, $15")
        out.append(f"        B, {q_name}($2)")
        out.extend(f"        , {a}" for a in args)

    def logic_statement(tag, var, depth=0):
        f = smac.split_args(var)
        op, a = f[0], f[1:]
        if op == "MEXIT":
            out.append(f"{tag:<8}B, QEXIT($2)")
        elif op == "MOUTF":
            if len(a) % 2 or len(a) > 30:
                raise BuildError("MOUTF: up to 15 (SK, n) pairs (p.7)")
            args = [len(a) // 2]
            for name, n in zip(a[0::2], a[1::2]):
                args += [name, int(n)]
            call(tag, "QOUTF", *args)
        elif op == "MOUTV":
            if len(a) % 3:
                raise BuildError("MOUTV takes sets of three (p.10)")
            if sum(1 for m in a[0::3] if m == "N") > 1:
                raise BuildError("MOUTV: only one M may be N (p.10)")
            args = [len(a) // 3]
            for m, name, k in zip(a[0::3], a[1::3], a[2::3]):
                args += [NFLAG if m == "N" else int(m), name, int(k)]
            call(tag, "QOUTV", *args)
        elif op == "MMVPT":
            src, n, dst = a
            if n != "QCN" and int(n) < 0:
                raise BuildError("MMVPT: N must be positive (p.5)")
            call(tag, "QMVPT", pointer(src), NFLAG if n == "QCN" else int(n), pointer(dst))
        elif op == "MOUT":
            call(tag, "QOUT", pointer(a[0]), len(a) - 1, *a[1:])
        elif op == "MGETL":
            call(tag, "QGETL", pointer(a[0]), int(a[1]))
        elif op in COMPARES:
            ptr, n, chars, target = a
            if not 1 <= len(chars) <= 8 or "," in chars or " " in chars:
                raise BuildError(f"{op}: one to eight characters, no comma or blank (p.6)")
            words = card_words(chars.ljust(8))[0]
            call(tag, COMPARES[op], pointer(ptr), int(n), len(chars), target)
            out.append(f"        DD(BU,32), (16){words >> 32:x}")
            out.append(f"        DD(BU,32), (16){words & 0xffffffff:x}")
        elif library is not None and op in library:
            if depth > 20:
                raise BuildError("macros nested too deeply in generator logic")
            expanded = smac.Processor(library)
            for img in expanded.run([(" " + tag.ljust(8) + var).rstrip()]):
                c = smac.Card.parse(img)
                logic_statement(c.tag, smac.split_comment(c.var)[0].strip(), depth + 1)
        elif op in smac.GL_OPS:
            raise BuildError(f"{gen.ops}: {op} may not appear in a generator's logic here")
        else:
            out.append(f"{tag:<8}{var}")

    for b in gen.logic:
        tags = [t for t, pc in gen.labels.items() if gen.logic[pc] is b]
        logic_statement(tags[0] if tags else "", b["var"])
    for name, blocks in gen.skeletons.items():
        out += ["        CNOP", f"{name:<8}DD(BU,24), {len(blocks)}", "        CNOP"]
        for b in blocks:
            var = b["var"] + ("'" + b["comment_text"] if b["in_comment"] else "")
            out.append(iqs_card((b["col1"] or " ") + b["tag"].ljust(8) + var))
    out += [f"{k:<8}SYN, {fmt_bits(q[k])}" for k in Q_SYMBOLS]
    out.append("        END, 0.0")
    return "\n".join(out) + "\n"


def link_generator(text):
    p = strap_asm.assemble(text)
    words = dict(p.words)
    if not words:
        raise BuildError("an empty generator")
    return [words.get(i, 0) for i in range(max(words) + 1)]


def build(library, ops, cards, out_cards, uniq_start=None):
    """The whole deck.  Returns (deck text, dict of the build's facts).
    uniq_start sets the /Q/ counter's four digits, so a test can reach its
    carries and its limit without ten thousand executions."""
    shell = open(SHELL).read()
    if uniq_start:
        if shell.count("Q0000?") != 1:
            raise BuildError("the shell's /Q/ counter has moved")
        shell = shell.replace("Q0000?", f"Q{uniq_start}?")
    stub = ("OPTX    DD(BU,64), 0\nQINP    DD(BU,64), 0\nQOUTP   DD(BU,64), 0\n"
            "FP      DD(BU,64), 0\nOUTCNT  DD(BU,64), 0\n        END, START\n")
    sym = strap_asm.assemble(shell + stub).symtab
    q = {k: sym[k] for k in Q_SYMBOLS}

    images, seen = [], {}
    for op in ops:
        g = library.gens[op]
        if id(g) not in seen:
            seen[id(g)] = len(images)
            images.append(link_generator(compile_generator(g, q, library)))
    tail = ["        CNOP", "OPTAB   SYN, $"]
    offs, n = [], 0
    for im in images:
        offs.append(n)
        n += len(im)
    for op in ops:
        smac.check_op(op)
        name = op.ljust(9)
        tail += ["        " + iqs_text(name[:8], 8),
                 f"        , LIB+{offs[seen[id(library.gens[op])]]}.0",
                 "        " + iqs_text(name[8], 4)]
    tail += ["        CNOP", f"OPTX    XW, OPTAB, {len(ops)}, 0",
             f"QINP    XW, INBUF, {len(cards)}, 0",
             "QOUTP   XW, OUTBUF, 0, 0", "FP      XW, STACK, 0, 0",
             "LIB     SYN, $"]
    image = [w for im in images for w in im]
    for w in image:
        tail.append(f"        DD(BU,64), (16){w:x}")
    tail += ["        CNOP", "INBUF   SYN, $"]
    for c in cards:
        tail.append(iqs_card(c))
    tail += ["        CNOP", "OUTCNT  DD(BU,64), 0",
             f"OUTBUF  DRZ(BU,64), {out_cards * 10}",
             "STACK   SYN, $",
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
