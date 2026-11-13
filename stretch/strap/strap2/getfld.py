"""getfld.py -- GETFLD, with CPLTNM and CPLTSY, C22-6729 pp.70-76, 80-86.

The chart is a state machine over a syntax matrix whose cells the guide does
not print (pp.83-84 give only the legends).  CHOSEN: this is recursive descent
enforcing Appendix F's rules (p.207).  It writes the same bits, which is what
the printed Figures 28 and 29 can check.  Priority is the table on p.198:
.+ .L .R U- * / + - with parentheses highest (p.199 note 4).

A parenthesis is classified at its ')', from what it holds and what came
before it, never from what follows (Chart BK p.82, Boxes 64-83, text p.85; read
in the ink 2026-11-13): GETCHA gives one character and keeps no pushback, and
GETFLD reads none past the ')'.  See _paren.

On entry $3 (g.ch) holds the character before the field unless have_first.  On
exit it holds the first character after the field (p.83).
"""
from .coded import Expr, Datum

END_FIELD = ",;')"
ALPHA = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
DIGIT = set("0123456789")
ALNUM = ALPHA | DIGIT


from .optable import mbspec      # noqa: E402


class FieldError(Exception):
    def __init__(self, number, text):
        super().__init__(f"{number}: {text}")
        self.number = number


def _lone(e):
    """One absolute datum, no operator, no subscript: Box 64's 'one absolute
    datum only' (an absolute datum is prefix 110, p.198 item 2B; a system
    symbol is not one, so MCP p.126's ($1) is not a radix)."""
    return (len(e.data) == 1 and e.data[0].kind == "abs" and not e.data[0].subs
            and not e.ops and e.gp is None)


def _point_n(e):
    """.n: one absolute datum with a point before it (p.198's .R)."""
    return (len(e.data) == 1 and e.data[0].kind == "abs" and not e.data[0].subs
            and e.ops == [(".R", 0)] and e.gp is None)


def _decimal(e):
    """The digits as written, read in decimal: a radix, and a g.p.'s n and r."""
    return int(e.data[0].text)


class Getfld:
    def __init__(self, g, sysym, tail=None, changed=None):
        self.g = g
        self.sysym = sysym      # name -> (value, dds) or None; CPLTSY's BOPSER
        self.tail = tail        # TAILOR's prefix, or None
        self.changed = changed  # (written, used): MBSPEC changed a system symbol
        self.radix = 0          # Gfsrad: 8 bits, zero means 10 (p.70)
        self.gp_radix = 0       # a DD's radix for its g.p. values (C28 p.30 c)
        self.pending = None     # a (.n) met, its value not yet read: (n, r)

    # -- the top: a field and its g.p. chain ----------------------------------
    def field(self, nogp=False, have_first=False):
        g = self.g
        # Radix: p.70 says zeroed "in instruction initialization", but printed
        # listings have "LFI(BU,8),(8)37,8" with a decimal offset in the next
        # field (C28-6129 p.26's "(.n,r)" is per field too).  So per field.
        self.radix = 0
        self.pending = None
        if not have_first:
            g.next()
        x = Expr()
        if g.ch is None or g.ch in END_FIELD:
            x.null = True
        else:
            self._sum(x)
            if not x.data:
                x.null = True   # the field is a g.p.: p.207 forbids it, C28 p.26 uses it
        self._gp_values(x, nogp)
        if g.ch is not None and g.ch not in END_FIELD:
            raise FieldError(67, f"INAPPROPRIATE CHARACTER {g.ch!r}")
        return x

    def _gp_values(self, x, nogp):
        """Each (.n) with its value after it (Boxes 37-38, 67-70)."""
        g = self.g
        x_end = x
        while self.pending is not None:
            if nogp:
                raise FieldError(108, "G.P. NOT ALLOWED: this statement produces no binary output (C28-6129 printed p.26)")
            n, r = self.pending
            self.pending = None
            self.radix = self.gp_radix if r is None else r
            if g.ch is None or g.ch in END_FIELD:
                raise FieldError(66, f"parenthetical integer entry (.{n}) has no value after it (C28-6129 printed p.25)")
            inner = Expr()
            self._sum(inner)
            x_end.gp = (n, inner)
            x_end = inner

    def gp_chain(self, x, nogp=False):
        """MQDD's numeric DD (pass1): its g.p. chain.  MQDD still decides by
        looking ahead (_peek_gp); its chart is step 4's (docs/strap2_7030.md)."""
        g = self.g
        self.pending = None
        if g.ch == "(" and self._peek_gp():
            self.radix = self.gp_radix
            self.pending = self._gp_of(self._paren_items())
        self._gp_values(x, nogp)

    def _peek_gp(self):
        """MQDD only: is '(' here the start of (.n), or of C28-6129 p.30's
        (r,.n)?  Look past blanks without consuming."""
        g = self.g
        col = g.col
        card = g.card
        while card is not None and col < 72 and card[col] in " 0123456789":
            col += 1
        if card is None or col >= 72:
            return False
        if card[col] == ".":
            return True
        if card[col] != ",":
            return False
        col += 1
        while col < 72 and card[col] == " ":
            col += 1
        return col < 72 and card[col] == "."

    # -- a parenthesis, classified at its ')' ----------------------------------
    def _paren_items(self):
        """'(' e, e, ... ')': each entry an expression.  $3 holds '(' on entry
        and the character after ')' on exit."""
        g = self.g
        g.next()
        items = []
        while True:
            e = Expr()
            self._sum(e)
            if self.pending is not None:
                raise FieldError(66, "SYNTAX ERROR: a g.p. inside parentheses (p.207)")
            items.append(e)
            if g.ch != ",":
                break
            g.next()
        if g.ch != ")":
            raise FieldError(67, "PARENTHESIS NOT CLOSED")
        g.next()
        return items

    @staticmethod
    def _gp_of(items):
        """Boxes 64-66: (.n), and C28-6129 p.25's (.n,r) and p.30's (r,.n)."""
        if len(items) == 1 and _point_n(items[0]):
            return _decimal(items[0]), None
        if len(items) == 2 and _point_n(items[0]) and _lone(items[1]):
            return _decimal(items[0]), _decimal(items[1])
        if len(items) == 2 and _lone(items[0]) and _point_n(items[1]):
            return _decimal(items[1]), _decimal(items[0])
        return None

    def _paren(self, x, after):
        """A parenthesis, classified at its ')' (Boxes 56-83, p.85).

        after: None at the start of a datum (the expression's start, or after an
        operator); 'datum' after a datum; 'point' after a datum and its point.
          a g.p. (.n), (.n,r), (r,.n), Boxes 64-70: pending; returns 'gp'.
          after a datum: the subscripts and index of that datum (Boxes 56-62,
            79 'subscript allowed'); returns 'subs'.
          one absolute datum alone, Boxes 79-81, 74: the radix of what
            follows, read as written (decimal); returns 'radix'.
          one expression with an operator, Boxes 76-78: arithmetic, spliced
            into x; returns 'datum'.
          otherwise (no operator, e.g. MCP p.126's KV,2,($1), 000000.04 91):
            not arithmetic, Box 82: S/X on a zero datum; returns 'datum'.
        CHOSEN, Box 76 draws no test: 'arithmetic parentheses legal' is an
        operator inside (Boxes 43-49: 'if there was no operator to make the
        parentheses arithmetic ... a sub-expression') at the start of a datum.
        After a point it is S/X, as Fig. 29 p.201 prints +7.(3-6*18)($X2+3.0)."""
        items = self._paren_items()
        gp = self._gp_of(items)
        if gp is not None:
            self.pending = gp
            return "gp"
        if after == "point" and len(items) == 1 and _lone(items[0]):
            # Box 79: no subscript after a point, so a radix; the datum the
            # point joins follows it.
            self.radix = _decimal(items[0])
            return "radix"
        if after is not None:
            if not x.data:
                raise FieldError(66, "SYNTAX ERROR")
            x.data[-1].subs.extend(items)
            return "subs"
        if len(items) == 1 and _lone(items[0]):
            self.radix = _decimal(items[0])
            return "radix"
        if len(items) == 1 and items[0].ops:
            base = len(x.data)
            x.data.extend(items[0].data)
            x.ops.extend((name, number + base) for name, number in items[0].ops)
            return "datum"
        zero = Datum("abs", 0)
        zero.subs.extend(items)
        x.data.append(zero)
        return "datum"

    def _after_datum(self, x):
        """Subscripts, the index, or a g.p., after a datum."""
        g = self.g
        while g.ch == "(" and self.pending is None:
            self._paren(x, "datum")

    def _gp_number(self):
        g = self.g
        g.next()                # '.', or the digit of (r,.n)
        if g.ch in DIGIT:
            r = 0
            while g.ch in DIGIT:
                r = r * 10 + int(g.ch)
                g.next()
            self.radix = r
            g.next()            # ','
        g.next()
        n = 0
        while g.ch in DIGIT:
            n = n * 10 + int(g.ch)
            g.next()
        if g.ch == ",":         # (.n,r): the pattern's radix, C28-6129 p.25
            g.next()
            r = 0
            while g.ch in DIGIT:
                r = r * 10 + int(g.ch)
                g.next()
            self.radix = r
        if g.ch != ")":
            raise FieldError(67, "G.P. NOT CLOSED")
        g.next()
        return n

    # -- expression, by priority ----------------------------------------------
    def _sum(self, x):
        g = self.g
        if g.ch == "+":
            g.next()            # a leading plus does nothing
        self._term(x)
        while g.ch in ("+", "-") and self.pending is None:
            op = g.ch
            number = len(x.data)
            g.next()
            self._term(x)
            x.ops.append((op, number))

    def _term(self, x):
        g = self.g
        self._unary(x)
        while g.ch in ("*", "/") and self.pending is None:
            op = g.ch
            number = len(x.data)
            g.next()
            self._unary(x)
            x.ops.append((op, number))

    def _unary(self, x):
        g = self.g
        if g.ch == "-":
            number = len(x.data)
            g.next()
            self._dotted(x)
            x.ops.append(("U-", number))
        else:
            self._dotted(x)

    def _datum(self, x):
        """The start of a datum: radix prefixes, then a primary or a
        parenthesis.  'gp' if a g.p. was met instead of a datum."""
        g = self.g
        while g.ch == "(":
            got = self._paren(x, None)
            if got == "radix":
                continue
            if got == "gp":
                return "gp"
            self._after_datum(x)
            return "paren"
        return None

    def _dotted(self, x):
        """a.b, a., .b -- the three codes of p.198."""
        g = self.g
        got = self._datum(x)
        if got == "gp":
            return
        if got is None:
            if g.ch == ".":
                number = len(x.data)
                g.next()
                if self._datum(x) is None:
                    self._primary(x)
                x.ops.append((".R", number))
                return
            self._primary(x)
        if self.pending is not None:
            return
        if g.ch == ".":
            number = len(x.data)
            g.next()
            if g.ch == "(":
                got = self._paren(x, "point")
                if got == "gp":
                    x.ops.append((".L", number))
                    return
                if got == "subs":
                    self._after_datum(x)
                elif self._datum(x) is None:
                    self._primary(x)
                x.ops.append((".+", number))
            elif g.ch is not None and (g.ch in ALNUM or g.ch == "$"):
                self._primary(x)
                x.ops.append((".+", number))
            else:
                x.ops.append((".L", number))

    def _primary(self, x):
        g = self.g
        c = g.ch
        if c is None:
            raise FieldError(66, "SYNTAX ERROR AT THE END OF THE FIELD")
        if c in DIGIT:
            # Box 7 tests for a symbol before Box 8 tests for a number, so a
            # number in radix 16 begins with a digit (p.80).
            d = Datum("abs", self._cpltnm())
            d.text = self.number_text
            x.data.append(d)
        elif c in ALPHA or c == "$":
            self._cpltsy(x)
        elif c == ".":
            # '2+.3' reaches here through _unary -> _dotted only; a stray point.
            raise FieldError(66, "SYNTAX ERROR")
        else:
            raise FieldError(66, f"SYNTAX ERROR AT {c!r}")
        self._after_datum(x)

    # -- CPLTNM ---------------------------------------------------------------
    def _cpltnm(self):
        """p.70: loop while alphameric.  A digit too large is error 63, used."""
        g = self.g
        radix = self.radix or 10
        v = 0
        self.number_text = ""   # as written: a radix, or a g.p.'s n, is decimal
        while g.ch is not None and g.ch in ALNUM:
            self.number_text += g.ch
            d = int(g.ch, 36)
            if d >= radix:
                raise FieldError(63, f"DIGIT INCORRECT {g.ch!r} IN RADIX {radix}")
            v = v * radix + d
            g.next()
        if v >= 1 << 24:
            raise FieldError(68, f"{v} is more than the 24 significant bits a datum holds (Fig. 12 p.71)")
        return v

    # -- CPLTSY ---------------------------------------------------------------
    def _cpltsy(self, x):
        g = self.g
        if g.ch == "$":
            g.next()
            text = ""
            while g.ch is not None and g.ch in ALNUM:
                text += g.ch.upper()
                g.next()
            if text == "":
                # p.24, p.84: a lone $ is datum $00 and an absolute zero, with
                # .L and + operators.  Fig. 14's count field shows 0 where the
                # three bytes need 3, so CHOSEN: 3 (pass1.md gap 27).
                first = len(x.data)
                x.data.append(Datum("sym", "$\0\0"))
                x.data.append(Datum("abs", 0))
                x.ops.append((".L", first + 2))
                x.ops.append(("+", first + 1))
                return
            found = self.sysym(text)
            if found is None:
                # Boxes 32-41 [75]: not found, MBSPEC [92-93]; no help, 56;
                # MBSPEC altered it, 129 (p.178).
                for test in mbspec(text):
                    found = self.sysym(test)
                    if found is not None:
                        if self.changed:
                            self.changed(text, test)
                        break
            if found is None:
                raise FieldError(56, f"NONEXISTENT SYSTEM SYMBOL ${text}")
            x.data.append(Datum("sys", found[0], found[1]))
            return
        text = ""
        while g.ch is not None and g.ch in ALNUM:
            text += g.ch.upper()
            g.next()
        if len(text) > 128:
            raise FieldError(49, "SYMBOL TOO LONG")
        written = None
        if g.ch == "$":
            written = self._written_tail()
        if self.tail:
            text = self.tail(text, written)
        x.data.append(Datum("sym", text))

    def _written_tail(self):
        """p.74: tails written on a symbol override its levels for it alone:
        the first $ is level 1, the next level 2, and an empty one zeroes that
        level.  MCP printed p.43 line 6's "$B,Q GO$A" reaches Q GO under TAIL,A."""
        g = self.g
        out = []
        while g.ch == "$":
            g.next()
            t = ""
            while g.ch is not None and g.ch in ALNUM:
                t += g.ch.upper()
                g.next()
            out.append(t)
        return out
