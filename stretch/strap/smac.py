#!/usr/bin/env python3
"""smac.py -- RECONSTRUCTION of SMAC, the Stretch MACro language
processor, as a host-side executable specification.

>>> THIS IS A RECONSTRUCTION, labelled as AGENTS.md and
>>> docs/programming_environment.md require.  IBM's SMAC processor was a
>>> 7030 program.  No listing of it is known.  This file implements the
>>> LANGUAGE its bulletin specifies, page by page.  Every choice the
>>> bulletin leaves open is marked CHOSEN below. <<<

SOURCES, each read in the ink
-----------------------------
J28-6128, "SMAC Language Processor", 7030 Data Processing System
Bulletin, 6/61 (CHM 102634360, docs/chm/).  Printed page = PDF page.
  p.1   statement and card format: column 1 comment/continuation mark
        "as in STRAP"; columns 2-9 tag; columns 10-72 "OP, ARG1, ...,
        ARGN"; OP up to nine letters, first M, none Q; tags and symbols
        up to eight characters, none Q (also in STRAP statements).
  p.2   continuation (up to nine cards); columns 73-80 unused; the
        one-pass processor: shell, branch table, subroutines,
        generators; "an N to 1 relationship between SMAC statements
        and generators".
  p.3   generators: logic + skeletons; the Generator Language; the
        parameter numbering (column 1, tag, operation, each argument);
        the pointers QPT1-QPT5.
  pp.4-11  the thirteen Generator Language statements, with examples.
  p.12  order of statements; skeletons: /n/, /Q/ (a unique tag, up to
        three characters around it, none Q), // for a slash.
  p.13  index registers in generators; the branch-table entries
        QDBUGB, QGUB, QMIBIT, QCIBIT, QMACBIT, QINBIT, QERRBIT.

The ERRATA SHEET (CHM 102634361, two pages), read in the ink.  It
renames MKPEQ, MKPNEQ, MKCEQ, MKCNEQ to MKPEQI, MKPNEQI, MKCEQI,
MKCNEQI ("Immediate"), corrects p.4's MOUTY to MOUTV, says QCOUNT is the
VALUE field (p.4 line 22), corrects the p.7 examples, and adds
"P = number of sets" to p.11's formula.  BOTH SPELLINGS ARE ACCEPTED:
the bulletin's and the errata's.  The owner's rule is to keep every
historical variant.  "MOUTY" is a misprint, not a variant, and is not
accepted.

C22-6678-1 (MCP Reference Manual, June 1964), printed p.14: an MCP
macro-instruction "MOP, parameter 1, parameter 2, etc." is expanded "by
the macro-generator (SMAC)" to "B,$MCP" / ",$OP" followed, "in
consecutive half-words, by the specified parameters".  The MCP macro
library (strap/smac_mcp.py) is built on that page.

C28-6129 (STRAP II), printed p.2: an apostrophe (8-4 punch) begins a
comment, and ";" (11-0) separates statements.  An apostrophe in the
NAME field makes the whole card block a comment.  printed p.3
(PDF p.7): a continuation card has "*" in column 1.

WHAT THE HOST SPEC DOES NOT DO, AND SAYS SO
-------------------------------------------
  * Generator LOGIC may contain STRAP statements (p.12: "STRAP and SMAC
    statements may be freely intermixed").  On the 7030 they are machine
    code run by the processor.  Here they would need a 7030, so a
    STRAP statement met while EXECUTING logic raises SmacError naming
    it.  The thirteen Generator Language statements run natively.
    The 7030-hosted processor (plan S-2, later) removes this limit.
  * Generators were COMPILED, with the Generator Language library
    (p.3), into relocatable 7030 code stored on a library tape.  Here
    they are interpreted from their source.  The observable result,
    the statements put out, is the same.

CHOSEN, each marked where it is used
------------------------------------
  C1 the library format.  The bulletin says only that "a library
     updating program adds the generator to the library tape and
     updates the table of acceptable SMAC operations" (p.2).  The
     update program's input format is not given.  Here a library is
     text in which each generator is preceded by a line "=OP1,OP2,..."
     naming the SMAC operations that call it.  That is the N-to-1 map
     of p.2.
  C2 the unique tag for /Q/.  Tags and symbols may not contain Q
     (p.1), so any tag holding a Q cannot clash with a programmer's.
     Here /Q/ becomes "Q" + four decimal digits, one value per generator
     execution.  With three characters around it, that is the eight-
     character maximum.
  C3 a /n/ beyond the subject statement's last parameter raises
     SmacError rather than inserting nothing.
  C4 a lone "/" in a skeleton that does not form /n/, /Q/ or // raises
     SmacError.  p.12 says "to insert a / into the card image, a // is
     used".
  C5 MGETL's literal: decimal digits, with an optional trailing ".".
     The bulletin says only "converted to a binary integer" (p.6).
"""
import re
import sys

MAX_PARAMS_TAG = 8


class SmacError(Exception):
    pass


# ---------------------------------------------------------------------
# Cards
# ---------------------------------------------------------------------
class Card:
    """One card image: column 1, the tag (columns 2-9), and the variable
    field (columns 10-72).  Columns 73-80 are not used (p.2)."""
    __slots__ = ("col1", "tag", "var", "src")

    def __init__(self, col1, tag, var, src=None):
        self.col1, self.tag, self.var, self.src = col1, tag, var, src

    @classmethod
    def parse(cls, line):
        line = line.rstrip("\n").ljust(80)
        return cls(line[0].strip(), line[1:9].strip(), line[9:72].rstrip(), line)

    def image(self):
        """The card as IBM punched it (col 1, tag cols 2-9, cols 10-72)."""
        if len(self.tag) > 8:
            raise SmacError(f"tag {self.tag!r} is longer than eight characters (p.1)")
        if len(self.var) > 63:
            raise SmacError(f"variable field longer than columns 10-72: {self.var!r}")
        return (self.col1 or " ") + self.tag.ljust(8) + self.var

    def __repr__(self):
        return f"Card({self.image()!r})"


def split_comment(var):
    """C28-6129 printed p.2: the apostrophe begins a comment.  Returns
    (statement text, comment or None)."""
    i = var.find("'")
    if i < 0:
        return var.rstrip(), None
    return var[:i].rstrip(), var[i + 1:]


def split_args(text):
    """OP, ARG1, ... split on commas outside parentheses."""
    out, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur).strip())
    return out


def read_blocks(lines):
    """Card blocks: a card plus its continuation cards ("*" in column 1,
    C28-6129 p.3; J28-6128 p.2 "a maximum of nine continuation cards").
    A card whose column 1 is a comment mark, or whose tag field begins
    with an apostrophe, is a comment block and is passed through."""
    blocks = []
    for raw in lines:
        if not raw.strip():
            continue
        c = Card.parse(raw)
        if c.col1 == "*" and blocks and not blocks[-1]["comment"]:
            b = blocks[-1]
            if len(b["cards"]) >= 10:
                raise SmacError("more than nine continuation cards (p.2)")
            b["cards"].append(c)
            if b["in_comment"]:
                b["comment_text"] += c.var
            else:
                stmt, com = split_comment(c.var)
                b["var"] += stmt.strip()
                if com is not None:
                    b["in_comment"] = True
            continue
        comment = c.col1 not in ("", "*") or c.tag.startswith("'")
        stmt, com = split_comment(c.var)
        blocks.append({"cards": [c], "comment": comment, "col1": c.col1,
                       "tag": c.tag, "var": stmt.strip(),
                       "in_comment": com is not None,
                       "comment_text": com or ""})
    return blocks


# ---------------------------------------------------------------------
# Generators
# ---------------------------------------------------------------------
GL_OPS = {"MBGEN", "MEXIT", "MBSKL", "MEGEN", "MMVPT", "MOUT", "MGETL",
          "MKPEQ", "MKPNEQ", "MKCEQ", "MKCNEQ",          # bulletin p.4
          "MKPEQI", "MKPNEQI", "MKCEQI", "MKCNEQI",      # errata p.1
          "MOUTF", "MOUTV"}


class Generator:
    """A generator's source: logic statements, then skeletons (p.3,
    p.12).  Built from card blocks MBGEN .. MEGEN."""

    def __init__(self, ops, blocks):
        self.ops = ops
        self.logic, self.labels, self.skeletons = [], {}, {}
        stmts = [b for b in blocks if not b["comment"]]
        if not stmts or split_args(stmts[0]["var"])[0] != "MBGEN":
            raise SmacError(f"{ops}: the first statement must be MBGEN (p.4)")
        if split_args(stmts[-1]["var"])[0] != "MEGEN":
            raise SmacError(f"{ops}: MEGEN must be physically last (p.5)")
        current = None
        for b in stmts[1:-1]:
            op = split_args(b["var"])[0]
            if op == "MBSKL":
                if not b["tag"]:
                    raise SmacError(f"{ops}: an MBSKL needs the skeleton's name as its tag")
                current = b["tag"]
                self.skeletons[current] = []
                continue
            if current is not None:
                self.skeletons[current].append(b)
                continue
            if b["tag"]:
                self.labels[b["tag"]] = len(self.logic)
            self.logic.append(b)


class Library:
    """The table of acceptable SMAC operations and their generators."""

    def __init__(self):
        self.gens = {}

    def add(self, ops, text):
        g = Generator(ops, read_blocks(text.splitlines()))
        for op in ops:
            check_op(op)
            self.gens[op] = g
        return g

    def load(self, text):
        """CHOSEN C1: "=OP1,OP2" heads each generator."""
        ops, body = None, []
        for line in text.splitlines() + ["="]:
            if line.startswith("="):
                if ops:
                    self.add(ops, "\n".join(body))
                ops = [o.strip() for o in line[1:].split(",") if o.strip()]
                body = []
            else:
                body.append(line)
        return self

    def __contains__(self, op):
        return op in self.gens


def check_op(op):
    """p.1: "up to nine alphabetic characters the first of which is M and
    none of which are Q".  The bulletin's own examples (pp.8-9) use
    MOP1-MOP4, so digits after the M are accepted, as the examples do."""
    # p.1 forbids Q in an operation, yet p.4 and the errata print MKPEQ, MKPNEQ,
    # MKCEQ and MKCNEQ.  The printed Generator Language names are taken as they
    # stand: those statements alone are exempt, and a generator for one can only
    # be written on the special library (p.3; decks/smac_special_library.smac).
    if op in GL_OPS:
        return
    if not (1 <= len(op) <= 9 and op.isalnum() and op[0] == "M" and "Q" not in op):
        raise SmacError(f"{op!r} is not a SMAC operation (p.1: up to nine "
                        "characters, the first M, none Q)")


# ---------------------------------------------------------------------
# The processor
# ---------------------------------------------------------------------
class Processor:
    """The processor shell (p.2): statements one at a time; a SMAC
    statement calls its generator; everything else passes to STRAP."""

    def __init__(self, library):
        self.lib = library
        self.unique = 0
        # the branch-table entries of p.13 that the host spec keeps
        self.QGUB = set()          # generators executed at least once
        self.QMACBIT = False
        self.QINBIT = False
        self.QERRBIT = False
        self.out = []

    # -- the shell ----------------------------------------------------
    def run(self, lines):
        for b in read_blocks(lines):
            # A card that is not a SMAC statement goes to STRAP exactly
            # as punched (its src), never re-rendered from its fields.
            if b["comment"]:
                self.out.extend(c.src.rstrip() for c in b["cards"])
                continue
            op = split_args(b["var"])[0] if b["var"] else ""
            if op in self.lib:
                # The subject statement's own comment is not carried
                # into the expansion: the bulletin says nothing of it.
                self.expand(b["col1"], b["tag"], b["var"], depth=0)
            else:
                self.out.extend(c.src.rstrip() for c in b["cards"])
        return self.out

    def expand(self, col1, tag, var, depth):
        if depth > 20:
            raise SmacError("macro nesting deeper than 20: a generator calls itself?")
        fields = split_args(var)
        op, args = fields[0], fields[1:]
        if args == [""]:
            args = []
        params = [col1, tag, op] + args
        g = self.lib.gens[op]
        self.QMACBIT, self.QINBIT = True, depth > 0
        self.unique += 1
        Execution(self, g, params, "Q%04d" % self.unique, depth).run()  # CHOSEN C2
        self.QGUB.add(id(g))
        self.QMACBIT = self.QINBIT = False

    def put(self, col1, tag, var, depth):
        """A skeleton statement after substitution.  If it is itself a
        SMAC statement it is expanded (an inner macro, QINBIT p.13)."""
        stmt, _ = split_comment(var)
        op = split_args(stmt)[0] if stmt.strip() else ""
        if op in self.lib:
            self.expand(col1, tag, stmt.strip(), depth + 1)
        else:
            self.out.append(Card(col1, tag, var).image())


class Execution:
    """One execution of one generator for one subject statement."""

    def __init__(self, proc, gen, params, unique, depth):
        self.p, self.g, self.params = proc, gen, params
        self.unique, self.depth = unique, depth
        # MBGEN: QCOUNT = number of parameters (errata: the VALUE field),
        # QPT1 at the first parameter (column 1).  Pointers are held as
        # 1-based parameter numbers.
        self.QCOUNT = len(params)
        self.ptr = {}
        self.QLIT = None
        self.QCN = None

    def param(self, n):
        if not 1 <= n <= len(self.params):
            raise SmacError(f"parameter {n} does not exist: the subject statement "
                            f"has {len(self.params)} (CHOSEN C3)")
        return self.params[n - 1]

    def pointer(self, name):
        if name not in self.ptr:
            raise SmacError(f"pointer {name} used before it is defined (p.5)")
        return self.ptr[name]

    def run(self):
        self.ptr = {"QPT1": 1}               # MBGEN, p.4
        pc = 0
        logic = self.g.logic
        while True:
            if pc >= len(logic):
                raise SmacError(f"{self.g.ops}: logic ran past its end without MEXIT (p.4)")
            b = logic[pc]
            f = split_args(b["var"])
            op, a = f[0], f[1:]
            pc += 1
            if op == "MEXIT":
                return
            elif op == "MMVPT":                       # p.5
                src, n, dst = a
                n = self.QCN if n == "QCN" else int(n)
                if n is None or n < 0:
                    raise SmacError("MMVPT: N must be positive (p.5)")
                if dst not in ("QPT1", "QPT2", "QPT3", "QPT4", "QPT5"):
                    raise SmacError(f"MMVPT: {dst} is not QPT1-QPT5 (p.5)")
                self.ptr[dst] = self.pointer(src) + n
            elif op == "MOUT":                        # pp.5-6
                base = self.pointer(a[0])
                for name in a[1:]:
                    self.put_skeleton(name, base)
            elif op == "MGETL":                       # p.6
                lit = self.param(self.pointer(a[0]) + int(a[1]) - 1)
                m = re.fullmatch(r"(\d+)\.?", lit)     # CHOSEN C5
                if not m:
                    raise SmacError(f"MGETL: {lit!r} is not a literal")
                self.QLIT = int(m.group(1))
            elif op in ("MKPEQ", "MKPNEQ", "MKCEQ", "MKCNEQ",
                        "MKPEQI", "MKPNEQI", "MKCEQI", "MKCNEQI"):   # pp.6-7
                ptr, n, chars, target = a
                if not 1 <= len(chars) <= 8:
                    raise SmacError(f"{op}: one to eight characters (p.6)")
                p = self.param(self.pointer(ptr) + int(n) - 1)
                if op.startswith("MKP"):
                    equal = p == chars              # "a whole parameter"
                else:
                    equal = p[:len(chars)] == chars  # "the first one to eight"
                if equal == ("NEQ" not in op):
                    if target not in self.g.labels:
                        raise SmacError(f"{op}: no logic statement tagged {target}")
                    pc = self.g.labels[target]
            elif op == "MOUTF":                       # pp.7-9
                pairs = list(zip(a[0::2], (int(x) for x in a[1::2])))
                if len(pairs) > 15 or len(a) % 2:
                    raise SmacError("MOUTF: up to 15 (SK, n) pairs (p.7)")
                nargs = len(self.params) - 3
                for name, n in pairs:
                    if n == nargs:
                        self.put_skeleton(name, 1)  # "a pointer which points at column one"
                        break
                else:
                    raise SmacError(f"MOUTF: no skeleton for {nargs} arguments")
            elif op == "MOUTV":                       # pp.9-11
                self.moutv(a)
            elif op in GL_OPS:
                raise SmacError(f"{op} may not appear in a generator's logic here")
            else:
                raise SmacError(
                    f"{self.g.ops}: the logic statement {b['var']!r} is STRAP, "
                    "i.e. 7030 code the processor would execute.  The host-side "
                    "specification cannot run it (see the header).")

    def moutv(self, a):
        """MOUTV, M1, NAME1, K1, ..., Mn, NAMEn, Kn (pp.9-11).  The set i
        pointer is column one moved over L = 3 + sum(j<i) Mj Kj (p.10;
        for set 1 it is column one).  The skeleton is put out M times,
        the pointer shifting K after each.  One M may be N, computed as
        p.11 gives it, P being the number of sets (errata)."""
        if len(a) % 3:
            raise SmacError("MOUTV takes sets of three: M, NAME, K (p.10)")
        sets = [[a[i], a[i + 1], int(a[i + 2])] for i in range(0, len(a), 3)]
        ns = [s for s in sets if s[0] == "N"]
        if len(ns) > 1:
            raise SmacError("MOUTV: only one M may be N (p.10)")
        if ns:
            i = sets.index(ns[0])
            rest = sum(int(s[0]) * s[2] for j, s in enumerate(sets) if j != i)
            num = (len(self.params) - 3) - rest
            k = sets[i][2]
            if k == 0 or num < 0 or num % k:
                raise SmacError(f"MOUTV: N = {num}/{k} is not a whole number "
                                "of repetitions (p.11)")
            sets[i][0] = num // k
        moved = 0
        for idx, (m, name, k) in enumerate(sets):
            m = int(m)
            base = 1 if idx == 0 else 1 + 3 + moved
            for r in range(m):
                self.put_skeleton(name, base + r * k)
            moved += m * k

    # -- skeletons -----------------------------------------------------
    def put_skeleton(self, name, base):
        if name not in self.g.skeletons:
            raise SmacError(f"{self.g.ops}: no skeleton {name}")
        for b in self.g.skeletons[name]:
            col1 = self.subst(b["col1"], base)
            tag = self.subst(b["tag"], base)
            var = self.subst(b["var"], base)
            if b["in_comment"]:
                var += "'" + b["comment_text"]
            self.p.put(col1, tag, var, self.depth)

    def subst(self, text, base):
        """p.12: /n/ inserts parameter n (counted from the pointer),
        /Q/ the unique tag, // a slash."""
        out, i = [], 0
        while i < len(text):
            if text[i] != "/":
                out.append(text[i])
                i += 1
                continue
            if text.startswith("//", i):
                out.append("/")
                i += 2
                continue
            m = re.match(r"/(\d+|Q)/", text[i:])
            if not m:
                raise SmacError(f"a lone '/' in skeleton text {text!r} "
                                "(p.12: write // for a slash; CHOSEN C4)")
            v = m.group(1)
            out.append(self.unique if v == "Q" else self.param(base + int(v) - 1))
            i += m.end()
        return "".join(out)


def to_scaffold(cards):
    """Card images -> the deck dialect strap/strap_asm.py reads (name in
    column 0, '!' comments).  strap_asm is scaffolding; this is only
    how SMAC's output reaches it until a STRAP II exists."""
    out = []
    for img in cards:
        c = Card.parse(img)
        if c.col1 not in ("", "*") or c.tag.startswith("'"):
            out.append("! " + img.rstrip())
            continue
        stmt, com = split_comment(c.var)
        line = (c.tag.ljust(8) if c.tag else " " * 8) + stmt.strip()
        if com:
            line = line.ljust(40) + " ! " + com.strip()
        out.append(line.rstrip())
    return "\n".join(out) + "\n"


def expand(library, text):
    return Processor(library).run(text.splitlines())


if __name__ == "__main__":
    import smac_mcp
    lib = smac_mcp.library()
    for line in expand(lib, open(sys.argv[1]).read()):
        print(line)
