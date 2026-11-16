"""atlas_data.py -- reader for tests/perf_char_vol2_atlas.txt, the
transcription of Perf. Char. Vol. 2's per-instruction timing atlas.

The file's own header is the grammar.  This module turns the sheets into
RECORDS, one per printed cell that holds something (a time, an indicator
mark, an illegible smudge); blank cells produce no record but are counted.

    from atlas_data import load_atlas
    pages = load_atlas()           # list of Page
    for r in pages[0].records: ...

Used by check_atlas_data.py (the fast self-check, in run_tests.sh) and by
atlas_oracle.py (the slow measurement, NOT in run_tests.sh).
"""
import os
import re
from decimal import Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS = os.path.join(HERE, "perf_char_vol2_atlas.txt")

CLOCK_US = Decimal("0.3")       # docs/clock_unit.md: one model clock

_NUM = re.compile(r"^\d+\.\d\d$")
_MARK = re.compile(r"^\*\d+\*$")


class AtlasError(Exception):
    pass


class Record:
    """One printed cell."""
    __slots__ = ("pdf", "printed", "cls", "instr", "cond", "block", "row",
                 "col", "text", "kind", "uncertain", "marks", "lineno")

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def us(self):
        """The printed time in microseconds, or None for a mark/smudge."""
        return Decimal(self.text) if self.kind == "time" else None

    @property
    def cycles(self):
        """Printed time / 0.3, unrounded (a Decimal), or None."""
        return None if self.us is None else self.us / CLOCK_US

    @property
    def whole_cycles(self):
        """True if the printed time is a whole number of 0.3 us clocks."""
        return self.us is not None and (self.us * 100) % 30 == 0

    def key(self):
        return (self.pdf, self.instr, self.block, self.row, self.col)

    def __repr__(self):
        return "<%s pdf %d %s [%s] %s %s = %s>" % (
            self.cls, self.pdf, self.instr, self.block, self.row, self.col,
            self.text + ("?" if self.uncertain else ""))


class Page:
    def __init__(self, pdf, printed, cls, lineno):
        self.pdf, self.printed, self.cls, self.lineno = pdf, printed, cls, lineno
        self.head = None
        self.notes = []
        self.records = []
        self.blank = 0              # cells stated blank
        self.tallies = {}           # rule -> (exact, near, far)
        self.sum = None             # (n, total) as written in the file
        self.instrs = []            # INSTR values, in order
        self.blocks = []            # (instr, caption) in order
        self.rows = []              # (instr, block, row label) in order
        self.cols_seen = []         # every COLS key that appeared

    def cell(self, instr, block, row, col):
        for r in self.records:
            if (r.instr, r.block, r.row, r.col) == (instr, block, row, col):
                return r
        return None


def load_atlas(path=ATLAS):
    pages = []
    page = None
    instr = None
    cond = {}
    cols = shown = None
    block = None
    seen_pdf = set()
    with open(path) as f:
        lines = f.read().split("\n")
    for lineno, raw in enumerate(lines, 1):
        if not raw.strip() or raw.startswith("#"):
            continue
        parts = raw.split("\t")
        tag = parts[0]

        def need_page():
            if page is None:
                raise AtlasError("line %d: %s before any PAGE" % (lineno, tag))

        if tag == "PAGE":
            kv = dict(p.split("=", 1) for p in parts[1:])
            try:
                pdf, printed, cls = int(kv["pdf"]), int(kv["printed"]), kv["class"]
            except (KeyError, ValueError):
                raise AtlasError("line %d: PAGE needs pdf= printed= class=" % lineno)
            if pdf in seen_pdf:
                raise AtlasError("line %d: PDF page %d appears twice" % (lineno, pdf))
            seen_pdf.add(pdf)
            page = Page(pdf, printed, cls, lineno)
            pages.append(page)
            instr, cond, cols, shown, block = None, {}, None, None, None
        elif tag == "HEAD":
            need_page()
            page.head = "\t".join(parts[1:])
        elif tag == "INSTR":
            need_page()
            instr = parts[1]
            page.instrs.append(instr)
            block = None
        elif tag == "COND":
            need_page()
            cond = dict(p.split("=", 1) for p in parts[1:])
        elif tag == "COLS":
            need_page()
            cols = parts[1:]
            for c in cols:
                if c not in page.cols_seen:
                    page.cols_seen.append(c)
            shown = None
        elif tag == "SHOWN":
            need_page()
            shown = parts[1:]
            if cols is None:
                raise AtlasError("line %d: SHOWN before COLS" % lineno)
            bad = [c for c in shown if c not in cols]
            if bad:
                raise AtlasError("line %d: SHOWN names %s, not in COLS" % (lineno, bad))
            if [c for c in cols if c in shown] != shown:
                raise AtlasError("line %d: SHOWN is not in COLS order" % lineno)
        elif tag == "BLOCK":
            need_page()
            block = parts[1]
            if (instr, block) in page.blocks:
                raise AtlasError("line %d: BLOCK %r repeated" % (lineno, block))
            page.blocks.append((instr, block))
        elif tag == "NOTE":
            need_page()
            page.notes.append("\t".join(parts[1:]))
        elif tag == "TALLY":
            need_page()
            try:
                page.tallies[parts[1]] = tuple(int(x) for x in parts[2:5])
                assert len(page.tallies[parts[1]]) == 3
            except (ValueError, IndexError, AssertionError):
                raise AtlasError("line %d: TALLY rule exact near far" % lineno)
        elif tag == "SUM":
            need_page()
            try:
                page.sum = (int(parts[1]), Decimal(parts[2]))
            except (ValueError, IndexError, ArithmeticError):
                raise AtlasError("line %d: SUM n total" % lineno)
        else:
            need_page()
            if shown is None or block is None:
                raise AtlasError("line %d: data row before SHOWN and BLOCK" % lineno)
            row = tag
            # a page with no INSTR line (the I-box and branch tables) names
            # the instruction in the row label
            ins = instr if instr is not None else row
            cells = parts[1:]
            marks = [c[1:] for c in cells if c.startswith("!")]
            cells = [c for c in cells if not c.startswith("!")]
            if len(cells) != len(shown):
                raise AtlasError("line %d: row %r has %d cells, SHOWN has %d"
                                 % (lineno, row, len(cells), len(shown)))
            if (ins, block, row) in page.rows:
                raise AtlasError("line %d: row %r repeated in block %r"
                                 % (lineno, row, block))
            page.rows.append((ins, block, row))
            page.blank += len(cols) - len(shown)
            for col, c in zip(shown, cells):
                if c == "-":
                    page.blank += 1
                    continue
                uncertain = c.endswith("?")
                text = c[:-1] if uncertain else c
                if _NUM.match(text):
                    kind = "time"
                elif _MARK.match(text):
                    kind = "mark"
                elif text == "~":
                    kind = "illegible"
                else:
                    raise AtlasError("line %d: row %r column %s: cannot parse "
                                     "cell %r" % (lineno, row, col, c))
                page.records.append(Record(
                    pdf=page.pdf, printed=page.printed, cls=page.cls,
                    instr=ins, cond=dict(cond), block=block, row=row,
                    col=col, text=text, kind=kind, uncertain=uncertain,
                    marks=marks, lineno=lineno))
    return pages


def all_records(pages=None):
    pages = load_atlas() if pages is None else pages
    return [r for p in pages for r in p.records]


if __name__ == "__main__":
    ps = load_atlas()
    n = sum(len(p.records) for p in ps)
    print("%d pages, %d records" % (len(ps), n))
    for p in ps:
        print("  PDF %3d (printed %3d) %-8s %-22s %4d records"
              % (p.pdf, p.printed, p.cls, ",".join(dict.fromkeys(p.instrs)) or "-",
                 len(p.records)))
