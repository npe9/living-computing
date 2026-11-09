"""getfld.py -- GETFLD, with CPLTNM and CPLTSY, C22-6729 pp.70-76, 80-86.

The chart is a state machine over a syntax matrix whose cells the guide does
not print (pp.83-84 give only the legends).  CHOSEN: this is recursive descent
enforcing Appendix F's rules (p.207).  It writes the same bits, which is what
the printed Figures 28 and 29 can check.  Priority is the table on p.198:
.+ .L .R U- * / + - with parentheses highest (p.199 note 4).

On entry $3 (g.ch) holds the character before the field unless have_first.  On
exit it holds the first character after the field (p.83).
"""
from .coded import Expr, Datum

END_FIELD = ",;')"
ALPHA = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
DIGIT = set("0123456789")
ALNUM = ALPHA | DIGIT


class FieldError(Exception):
    def __init__(self, number, text):
        super().__init__(f"{number}: {text}")
        self.number = number


class Getfld:
    def __init__(self, g, sysym, tail=None):
        self.g = g
        self.sysym = sysym      # name -> (value, dds) or None; CPLTSY's BOPSER
        self.tail = tail        # TAILOR's prefix, or None
        self.radix = 0          # Gfsrad: 8 bits, zero means 10 (p.70)

    # -- the top: a field and its g.p. chain ----------------------------------
    def field(self, nogp=False, have_first=False):
        g = self.g
        # Radix: p.70 says zeroed "in instruction initialization", but printed
        # listings have "LFI(BU,8),(8)37,8" with a decimal offset in the next
        # field (C28-6129 p.26's "(.n,r)" is per field too).  So per field.
        self.radix = 0
        if not have_first:
            g.next()
        x = Expr()
        if g.ch is None or g.ch in END_FIELD:
            x.null = True
        elif g.ch == "(" and self._peek_gp():
            x.null = True       # p.207 forbids this, but C28 p.26 uses it
        elif g.ch == "(" and self._closes_field() and not self._radix_ahead():
            # MCP printed p.126 line 11, "KV,2,($1)", compiles 000000.04 91: an
            # omitted address before an index is a zero (C22-6531 printed p.7).
            x.data.append(Datum("abs", 0))
            self._subscripts(x)
        else:
            self._sum(x)
            self._subscripts(x)
        x_end = x
        while g.ch == "(" and self._peek_gp():
            if nogp:
                raise FieldError(108, "G.P. NOT ALLOWED: this statement produces no binary output (C28-6129 printed p.26)")
            n = self._gp_number()
            if g.ch is None or g.ch in END_FIELD:
                raise FieldError(66, f"parenthetical integer entry (.{n}) has no value after it (C28-6129 printed p.25)")
            inner = Expr()
            self._sum(inner)
            self._subscripts(inner)
            x_end.gp = (n, inner)
            x_end = inner
        if g.ch is not None and g.ch not in END_FIELD:
            raise FieldError(67, f"INAPPROPRIATE CHARACTER {g.ch!r}")
        return x

    def _closes_field(self):
        """Does the parenthesis here close with nothing after it in the field?"""
        g = self.g
        card, col, depth = g.card, g.col, 1
        while card is not None and col < 72:
            c = card[col]
            col += 1
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
        while card is not None and col < 72 and card[col] == " ":
            col += 1
        return card is not None and (col >= 72 or card[col] in ",;'" or
                                     (card[col] == "(" and card[col + 1:col + 2] == "."))

    def _peek_gp(self):
        """Is '(' here the start of (.n)?  Look past blanks without consuming."""
        g = self.g
        col = g.col
        card = g.card
        while card is not None and col < 72:
            if card[col] != " ":
                return card[col] == "."
            col += 1
        return False

    def _gp_number(self):
        g = self.g
        g.next()                # '.'
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
        while g.ch in ("+", "-"):
            op = g.ch
            number = len(x.data)
            g.next()
            self._term(x)
            x.ops.append((op, number))

    def _term(self, x):
        g = self.g
        self._unary(x)
        while g.ch in ("*", "/"):
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

    def _dotted(self, x):
        """a.b, a., .b -- the three codes of p.198."""
        g = self.g
        while g.ch == "(" and self._radix_prefix():
            pass
        if g.ch == ".":
            number = len(x.data)
            g.next()
            self._primary(x)
            x.ops.append((".R", number))
            return
        self._primary(x)
        if g.ch == ".":
            number = len(x.data)
            g.next()
            if g.ch == "(" and self._peek_gp():
                x.ops.append((".L", number))
            elif g.ch == "(" and not self._radix_ahead():
                # Fig. 29 p.201, "+7.(3-6*18)($X2+3.0)": the parenthesis after
                # the point holds S/X of the datum before it, and the operator
                # is still printed as .+ (Box 58-59 changes .L only when a
                # datum follows; the figure is the authority here).
                self._subscripts(x)
                x.ops.append((".+", number))
            elif g.ch is not None and (g.ch in ALNUM or g.ch == "$" or g.ch == "("):
                while g.ch == "(" and self._radix_prefix():
                    pass
                self._primary(x)
                x.ops.append((".+", number))
            else:
                x.ops.append((".L", number))

    def _primary(self, x):
        g = self.g
        c = g.ch
        if c == "(":
            g.next()
            self._sum(x)
            if g.ch != ")":
                raise FieldError(67, "PAREN NOT CLOSED")
            g.next()
        elif c in DIGIT or (self.radix > 10 and c.upper() in "ABCDEF"):
            x.data.append(Datum("abs", self._cpltnm()))
        elif c in ALPHA or c == "$":
            self._cpltsy(x)
        elif c == ".":
            # '2+.3' reaches here through _unary -> _dotted only; a stray point.
            raise FieldError(66, "SYNTAX ERROR")
        else:
            raise FieldError(66, f"SYNTAX ERROR AT {c!r}")
        if g.ch == "(" and not self._peek_gp():
            self._subscripts(x)

    def _radix_ahead(self):
        g = self.g
        keep = (g.col, g.ch, list(g.bsyst), g.card, self.radix)
        got = self._radix_prefix()
        g.col, g.ch, g.bsyst, g.card, self.radix = keep[0], keep[1], keep[2], keep[3], keep[4]
        return got

    def _radix_prefix(self):
        """'(8)' before a number: Box 74, Gfsrad.  Decided by looking ahead."""
        g = self.g
        card, col = g.card, g.col
        digits = ""
        while card is not None and col < 72:
            c = card[col]
            col += 1
            if c == " ":
                continue
            if c in DIGIT:
                digits += c
                continue
            if c != ")" or not digits:
                return False
            break
        else:
            return False
        while col < 72 and card[col] == " ":
            col += 1
        follow = card[col] if col < 72 else ""
        if not (follow in DIGIT or follow == "." or
                (follow and int(digits) > 10 and follow.upper() in "ABCDEF")):
            return False
        for _ in digits:
            g.next()
        g.next()                # ')'
        g.next()                # the number
        self.radix = int(digits)
        return True

    def _subscripts(self, x):
        """S/X after the last datum, the index included (formats.md 5.2)."""
        g = self.g
        while g.ch == "(" and not self._peek_gp():
            g.next()
            while True:
                sub = Expr()
                self._sum(sub)
                if not x.data:
                    raise FieldError(66, "SYNTAX ERROR")
                x.data[-1].subs.append(sub)
                if g.ch != ",":
                    break
                g.next()
            if g.ch != ")":
                raise FieldError(67, "SUBSCRIPT NOT CLOSED")
            g.next()

    # -- CPLTNM ---------------------------------------------------------------
    def _cpltnm(self):
        """p.70: loop while alphameric.  A digit too large is error 63, used."""
        g = self.g
        radix = self.radix or 10
        v = 0
        while g.ch is not None and g.ch in ALNUM:
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
