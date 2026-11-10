"""listing.py -- OUTPUT's listing: C28-6129 printed pp.18-20 and Fig. 3 p.19,
C22-6678-1 Fig. 5 p.48, C22-6729 charts OP, OV, OW, OT and OEDIT pp.150-165.

A line is line number, location, binary, name, statement, in that order.

What the pages fix:
  half word   24 bits in octal, a point between the 6th and 7th digits, two hex
              digits; a full-word instruction prints two (p.18).
  floating    exponent, exponent sign, fraction, fraction sign, flags (p.18,
              Fig. 3 lines 14-15: 0022+ 5453370000000000 +TUV).
  index word  value and sign, index flag and two unused bits, count, refill
              (p.18, Fig. 3 line 17; a CW the same, p.48 line 23).
  fixed       straight octal, one line per field (p.20, Fig. 3 lines 19-20).
  decimal     displayed in decimal (p.20).
  DR          the words and bits reserved, as a bit address (p.20).
  SYN         a bit address in the location column, the integer in the binary
              column (p.20, Fig. 3 line 2).
  SLC         the resulting counter in the location column (p.20).
  END         its location, and the transfer address in the binary column
              (Fig. 3 line 24, p.48 line 25).
  alphabetic  location but no code (p.48 line 24; chart OW bypasses box 10).
  bounds      the full word before the first used and after the last (p.20).
  a long name the name on the first line, the statement on the next (Fig. 3
              lines 20-21, 22-23).  Each card of a statement is a line (lines
              11-12).

CHOSEN, for no page gives them: the print positions, measured from Fig. 3; a
name fits its column at eight characters or fewer, the width of columns 2-9; a
signed fixed field prints its sign byte in octal after the data; a SYN with no
bit address has an empty location column; a continued statement's cards are kept
apart by a newline in the print image.

Two forms were printed.  Fig. 3 (1963) marks a line number with '-' and a comment
with '-'; p.48 (1964) marks line numbers with '*' and comments with an apostrophe.
`mark` selects.  NOT REPRODUCED: the second '*' after the location on five of
p.48's lines, unexplained by any page (docs/strap2/pass2.md section 12), and the
blank line after Fig. 3 line 13, likewise.

The error flags (C28-6129 pp.20-21, N28-1081 page 7, guide p.157 box 2) print on
the line immediately preceding the statement's first line.  CHOSEN: that line
has no line number, holds every flag the unit has in the manual's order, and
starts at the location column.

The symbol lists (NUNDSY, charts EG, EH pp.170-172) follow the statements,
then the error messages (ERRPRT), then the seconds, the last item (C28-6129
p.20; the guide puts the lists at the end, p.157, where the manual says the
beginning, and governs).  Chart EG prints a header before the undefined symbols
only when the whole table is printed (boxes 6B, 7), so there is none here.
CHOSEN: the other three headers' words, from the manual's descriptions; a name
and its address separated by two blanks.  ERRPRT is not yet written: the
messages are on p2.msg, unprinted.
"""
from .unit import ZILCFD, ZILSST, FIXED_BITS, ZIFLAGS
from .value import flag_names

LOC, BIN, NAME, STMT = 4, 17, 47, 56    # CHOSEN: print positions, measured


def loc(bits):
    return f"{bits // 64:06o}.{bits % 64:02o}"


def halfword(h):
    return f"{h >> 14:06o}.{(h >> 8) & 0o77:02o} {h & 255:02X}"


def index_form(w):
    value = w >> 40
    sign = "-" if (w >> 39) & 1 else "+"
    flags = f"{(w >> 36) & 7:03b}"
    return f"{loc(value)}{sign} {flags} {(w >> 18) & 0o777777:06o} {w & 0o777777:06o}"


def floating_form(w):
    expo = w >> 53
    esign = "-" if (w >> 52) & 1 else "+"
    frac = (w >> 4) & ((1 << 48) - 1)
    sign = "-" if (w >> 3) & 1 else "+"
    flags = "".join(c if (w >> k) & 1 else "0" for c, k in (("T", 2), ("U", 1), ("V", 0)))
    return f"{expo:04o}{esign} {frac:016o} {sign}{flags}"


def field_form(value, width, mode, bs):
    if mode in ("D", "DU"):
        data = width - (bs if mode == "D" else 0)
        v = value >> (width - data)
        digits = []
        for k in range(data // bs):
            digits.append(str((v >> (data - bs * (k + 1))) & 15))
        text = "".join(digits)
        if mode == "D":
            text += f" {value & ((1 << bs) - 1):0{(bs + 2) // 3}o}"
        return text
    if mode == "B":
        data = width - bs
        return (f"{value >> bs:0{(data + 2) // 3}o}"
                f" {value & ((1 << bs) - 1):0{(bs + 2) // 3}o}")
    return f"{value:0{(width + 2) // 3}o}"


HEADERS = {"unused": "SYMBOLS DEFINED BUT NOT USED",
           "multiple": "MULTIPLY DEFINED SYMBOLS",
           "circular": "CIRCULARLY DEFINED SYMBOLS"}


class Line:
    def __init__(self, location="", binary="", name="", statement="", right=False,
                 flags=None):
        self.location, self.binary, self.name = location, binary, name
        self.statement, self.right = statement, right
        self.flags = flags
        self.number = None

    def fields(self):
        return (self.number, self.location, self.binary, self.name, self.statement)


class Listing:
    def __init__(self, p2, names, mark="-", lines_per_page=None):
        self.p2, self.names, self.mark = p2, names, mark
        self.per_page = lines_per_page
        self.lines = []

    def bits(self, at, n):
        v = 0
        for k in range(at, at + n):
            word = self.p2.image.words.get(k // 64, 0)
            v = (v << 1) | ((word >> (63 - k % 64)) & 1)
        return v

    def statement_lines(self, unit):
        p2 = self.p2
        u = p2.units
        start = (unit + FIXED_BITS + u.get(unit, ZILCFD) + 63) // 64 * 64
        text = "".join(chr(p2.mem.get(start + 8 * k, 8)) for k in range(u.get(unit, ZILSST)))
        if self.mark == "-":
            text = text.replace("'", "-")
        return [t.rstrip() for t in text.split("\n") if t.strip()] or [""]

    def syn(self, unit, name):
        """The value the SYN's own definition gave, which for a contradictory
        multiple is not the one the dictionary holds."""
        st = self.p2.st
        f = self.p2.p1_named(unit) or st.dictionary.get(name)
        if f is None:
            return "", ""
        b, i = st.get(f, "ZVALB"), st.get(f, "ZVALI")
        where = (loc(abs(b)) + ("-" if b < 0 else "+")) if b else ""
        return where, f"{'-' if i < 0 else '+'}{abs(i):08o}"

    def add(self, line):
        self.lines.append(line)

    def unit(self, unit):
        p2 = self.p2
        e = p2._entry(unit)
        printed = p2.printed.get(unit)
        name, symbol = self.names.get(unit, ("", ""))
        stmt = self.statement_lines(unit)
        flags = flag_names(p2.units.get(unit, ZIFLAGS))
        if flags:
            self.add(Line(flags=flags))
        first = Line(name=name)
        if e.name == "SYN":
            first.location, first.binary = self.syn(unit, symbol)
            first.right = True
        extra = []
        if printed is not None:
            kind = printed[0]
            if kind == "SLC":
                first.location = loc(printed[1])
            elif kind == "END":
                first.location = loc(printed[1])
                if printed[2] is not None:
                    first.binary = loc(printed[2])
            elif kind == "DR":
                first.location, first.binary = loc(printed[1]), loc(printed[2])
            elif kind == "ALPHA":
                first.location = loc(printed[1])
            elif kind == "INSTR":
                _, at, n, ename = printed
                first.location = loc(at)
                if ename in ("XW", "CW"):
                    first.binary = index_form(self.bits(at, 64))
                elif n == 64:
                    first.binary = f"{halfword(self.bits(at, 32))} {halfword(self.bits(at + 32, 32))}"
                else:
                    first.binary = halfword(self.bits(at, 32))
            elif kind == "NUM":
                _, at, mode, fl, bs, count = printed
                for k in range(count):
                    pos = at + k * fl
                    ln = first if k == 0 else Line()
                    ln.location = loc(pos)
                    if mode in ("N", "U"):
                        ln.binary = floating_form(self.bits(pos, 64))
                    else:
                        ln.binary = field_form(self.bits(pos, fl), fl, mode, bs)
                        ln.right = True
                    if k:
                        extra.append(ln)
            elif kind == "EXT":
                _, at, n = printed
                first.location = loc(at)
                first.binary = f"{self.bits(at, n):0{(n + 2) // 3}o}"
                first.right = True
        if len(name) > 8:
            self.add(first)
            for t in stmt:
                self.add(Line(statement=t))
        else:
            first.statement = stmt[0]
            self.add(first)
            for t in stmt[1:]:
                self.add(Line(statement=t))
        for ln in extra:
            self.add(ln)

    def bounds(self):
        im = self.p2.image
        used = [w for w, m in im._written.items() if m]
        for at, width in im.reservations:
            used += [at // 64, (at + width - 1) // 64]
        if not used:
            return None
        return (min(used) - 1) * 64, (max(used) + 1) * 64

    def build(self):
        p2 = self.p2
        for unit in p2.units.intin():
            self.unit(unit)
        n = 0
        for ln in self.lines:
            if ln.flags:
                continue
            n += 1
            if self.per_page and n > self.per_page:
                n = 1
            ln.number = n
        return self

    def text(self, clock="", seconds=0):
        out = []
        out.append(" " * 16 + "TIME CLOCK" + " " * 8 + clock)
        out.append(" " * NAME + "PAGE" + " " * 13 + "1")
        out.append(" " * 5 + "LOCATION" + " " * 12 + "BINARY OUTPUT" + " " * 8 + "NAME" + " " * 5 + "STATEMENT")
        b = self.bounds()
        if b:
            out.append(f"{loc(b[0])} LOWER MEMORY BOUND")
            out.append(f"{loc(b[1])} UPPER MEMORY BOUND")
        for ln in self.lines:
            if ln.flags:
                out.append(" " * LOC + " ".join(ln.flags))
                continue
            s = f"{ln.number:2d}{self.mark}".ljust(LOC) + ln.location.ljust(BIN - LOC)
            if ln.right:
                s += ln.binary.rjust(40 - BIN).ljust(NAME - BIN)
            else:
                s += ln.binary.ljust(NAME - BIN)
            if len(ln.name) > 8:
                s = s + ln.name
            else:
                s += ln.name.ljust(STMT - NAME) + ln.statement
            out.append(s.rstrip())
        out += self.symbol_lists()
        out.append(" " * 4 + "THIS ASSEMBLY REQUIRED" + " " * 7 + f"{seconds:08d} SECONDS")
        return "\n".join(out) + "\n"

    def symbol_lists(self):
        lists = self.p2.lists
        out = []
        for name, at in lists["undefined"]:
            out.append(f"{name}  {loc(at)}")
        for key in ("unused", "multiple", "circular"):
            if lists[key]:
                out.append(HEADERS[key])
                for name, at in lists[key]:
                    out.append(name if at is None else f"{name}  {loc(at)}")
        return out


def listing_of(p2, names, mark="-", lines_per_page=None):
    return Listing(p2, names, mark, lines_per_page).build()
