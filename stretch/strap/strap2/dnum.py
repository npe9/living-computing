"""dnum.py -- numeric DD: MQDNUM, DNUM and MQDDPA's double precision, C22-6729
pp.104-113, and OUTPUT's conversion to the final word, pp.26, 158-159.

Pass 1 keeps every numeric entry as a floating number of 96 bits, normalized,
truncated at every step, whatever the use mode (p.26); Fn entries are not
treated separately here until OUTPUT, because the host holds the fixed value
through `fractional`.  OUTPUT (`final`) makes the word the mode wants, using
C28-6129 pp.27-30 for what each mode wants.

CHOSEN: MQLL4's three-step division (p.111) is replaced by an exact quotient
truncated to 96 bits.  The chart's step corrects for the divisor's low half, so
the two agree except possibly in the last bits of 96; the words are at most 64.
"""
from fractions import Fraction

from .getfld import FieldError

BITS = 96
TOP = 1 << (BITS - 1)


class DnumError(FieldError):
    pass


class Dbl:
    """(-1)^neg * frac/2^96 * 2^exp, with 1/2 <= frac/2^96 < 1, or frac 0."""
    __slots__ = ("neg", "exp", "frac")

    def __init__(self, neg=False, exp=0, frac=0):
        self.neg, self.exp, self.frac = neg, exp, frac

    @staticmethod
    def of(n):
        neg = n < 0
        n = abs(n)
        if n == 0:
            return Dbl()
        size = n.bit_length()
        f = n << (BITS - size) if size <= BITS else n >> (size - BITS)
        return Dbl(neg, size, f)

    def is_zero(self):
        return self.frac == 0

    def exact(self):
        v = Fraction(self.frac) * Fraction(2) ** (self.exp - BITS)
        return -v if self.neg else v

    def __eq__(self, o):
        return (self.neg, self.exp, self.frac) == (o.neg, o.exp, o.frac)

    def __repr__(self):
        return f"Dbl({'-' if self.neg else '+'}{self.exp},{self.frac:024x})"


def _norm(neg, exp, f):
    if f == 0:
        return Dbl()
    size = f.bit_length()
    if size > BITS:
        return Dbl(neg, exp + size - BITS, f >> (size - BITS))
    return Dbl(neg, exp - (BITS - size), f << (BITS - size))


def add(a, b, sub=False):
    """MQ1, truncating."""
    bneg = b.neg != sub
    if a.is_zero():
        return Dbl(bneg, b.exp, b.frac)
    if b.is_zero():
        return a
    if a.exp < b.exp:
        a, b, bneg = Dbl(bneg, b.exp, b.frac), Dbl(a.neg, a.exp, a.frac), a.neg
    shift = a.exp - b.exp
    if shift > BITS + 2:
        return a
    # Exact, then truncated: a 96-bit accumulator with guard bits would do this.
    x = a.frac << shift
    y = b.frac
    v = (-x if a.neg else x) + (-y if bneg else y)
    return _norm(v < 0, a.exp - shift, abs(v))


def mul(a, b):
    """MQ2: the product's upper 96 bits."""
    if a.is_zero() or b.is_zero():
        return Dbl()
    return _norm(a.neg != b.neg, a.exp + b.exp - BITS, a.frac * b.frac)


def div(a, b):
    """MQLL4; see CHOSEN above."""
    if b.is_zero():
        raise DnumError(112, "DIVISION BY ZERO IN A DD")
    if a.is_zero():
        return Dbl()
    return _norm(a.neg != b.neg, a.exp - b.exp - 2, (a.frac << (BITS + 2)) // b.frac)


ONE = Dbl.of(1)


def power(base, n):
    """MQDDPP [111-113]: multiply the base**(2**k) entries n's bits select.  A
    negative exponent is MQ3, the inverse of the positive power."""
    if base.is_zero():
        raise DnumError(112, "ZERO BASE TO A POWER")
    if abs(n) >= 1 << 18:
        raise DnumError(113, "EXPONENT OUT OF RANGE")
    if n == 0:
        return ONE
    m = abs(n)
    entry, out = base, ONE
    while True:
        if m & 1:
            out = mul(out, entry)
        m >>= 1
        if not m:
            break
        entry = mul(entry, entry)
    return div(ONE, out) if n < 0 else out


class Number:
    """A value and what was written: `fractional` is p.29's distinction between
    an integer and a decimal fraction ("17 E 5" against "17 E-5", "17.5 E 5")."""
    __slots__ = ("v", "fractional")

    def __init__(self, v, fractional=False):
        self.v, self.fractional = v, fractional


_SYSTEM_CACHE = {}


def system_constant(name):
    """C28-6129 p.28's constants, as 96-bit truncations; CHOSEN how they got
    there, since their table (Fig. 25) holds only their addresses."""
    if name in _SYSTEM_CACHE:
        return _SYSTEM_CACHE[name]
    scale = 1 << 140
    def ln2():
        s, k, term = 0, 1, scale // 2
        while term:
            s += term // k
            k += 1
            term //= 2
        return s
    if name == "E":
        s, term, k = scale, scale, 1
        while term:
            term //= k
            s += term
            k += 1
        q = Fraction(s, scale)
    elif name == "N":   # log e 2
        q = Fraction(ln2(), scale)
    elif name == "M":   # log 10 e = 1/ln 10; ln 10 by atanh(9/11)*2
        s, k, t = 0, 1, scale * 9 // 11
        while t:
            s += t // k
            t = t * 81 // 121
            k += 2
        q = Fraction(scale, 2 * s)
    elif name == "PI":  # Machin
        def atan_inv(x):
            s, t, k, sign = 0, scale // x, 1, 1
            while t:
                s += sign * (t // k)
                t //= x * x
                k += 2
                sign = -sign
            return s
        q = Fraction(16 * atan_inv(5) - 4 * atan_inv(239), scale)
    else:
        return None
    n = q.numerator
    d = q.denominator
    e = n.bit_length() - d.bit_length()
    f = (n << (BITS - e)) // d if BITS >= e else n // (d << (e - BITS))
    got = _norm(False, e, f)
    _SYSTEM_CACHE[name] = got
    return got


class Scan:
    """MQDNUM and DNUM over GETCHA."""

    def __init__(self, g, radix):
        self.g = g
        self.radix = radix

    def expression(self):
        """p.107's orders: + - below * / below **, levels by parentheses."""
        return self._sum()

    def _sum(self):
        g = self.g
        x = self._term()
        while g.ch in ("+", "-"):
            op = g.ch
            g.next()
            y = self._term()
            x = Number(add(x.v, y.v, sub=op == "-"), x.fractional or y.fractional)
        return x

    def _term(self):
        g = self.g
        x = self._power()
        while g.ch in ("*", "/"):
            op = g.ch
            g.next()
            if op == "*" and g.ch == "*":
                raise DnumError(66, "MISPLACED **")
            y = self._power()
            if op == "*":
                x = Number(mul(x.v, y.v), x.fractional or y.fractional)
            else:
                # 1/3 is not a whole number, and a whole quotient is not a
                # fraction: p.29 tells only of points and E's, so CHOSEN.
                q = div(x.v, y.v)
                x = Number(q, x.fractional or y.fractional or q.exact().denominator != 1)
        return x

    def _power(self):
        g = self.g
        x = self._unary()
        while g.ch == "*" and g.card is not None and g.col < 72 and g.card[g.col] == "*":
            g.next()
            g.next()
            y = self._unary()
            e = y.v.exact()
            if e.denominator != 1:
                raise DnumError(113, "EXPONENT NOT WHOLE")
            x = Number(power(x.v, int(e)), x.fractional or e < 0)
        return x

    def _unary(self):
        g = self.g
        if g.ch == "-":
            g.next()
            x = self._unary()
            return Number(Dbl(not x.v.neg, x.v.exp, x.v.frac), x.fractional)
        if g.ch == "+":
            g.next()
            return self._unary()
        if g.ch == "(":
            g.next()
            x = self._sum()
            if g.ch != ")":
                raise DnumError(66, "PAREN NOT CLOSED IN A DD")
            g.next()
            return x
        if g.ch == "$":
            g.next()
            name = ""
            while g.ch is not None and g.ch.isalnum():
                name += g.ch.upper()
                g.next()
            c = system_constant(name)
            if c is None:
                raise DnumError(56, f"NO FLOATING CONSTANT ${name}")
            return Number(c, True)
        return self._dnum()

    def _is_digit(self, c, radix):
        if c is None:
            return False
        c = c.upper()
        if c.isdigit():
            return True
        return radix > 10 and c in "ABCDEF"

    def _dnum(self):
        """DNUM [108-110]."""
        g = self.g
        radix = self.radix or 10
        pr = Dbl()
        scale = 0
        point = False
        seen = False
        fractional = False
        while True:
            c = g.ch
            if self._is_digit(c, radix):
                d = int(c, 16)
                if d >= radix:
                    raise DnumError(47, f"CHAR ILLEGAL IN RADIX {radix}: {c}")
                pr = add(mul(pr, Dbl.of(radix)), Dbl.of(d))
                if point:
                    scale -= 1
                seen = True
            elif c == ".":
                if point:
                    raise DnumError(48, "MORE THAN ONE POINT")
                point = True
                seen = True
            else:
                break
            g.next()
        if not seen and (g.ch is None or g.ch.upper() != "E"):
            raise DnumError(66, f"SYNTAX ERROR AT {g.ch!r} IN A DD")
        if point and scale < 0:
            fractional = True
        if scale and radix != 10:
            # p.110: the end with C and A on is DNADJ in this radix; radix 10 waits
            # for E, whose exponent is added to the running one first.
            pr = mul(pr, power(Dbl.of(radix), scale))
            scale = 0
        if g.ch is not None and g.ch.upper() == "E" and radix <= 10:
            # E: decimal thereafter, the exponent read by re-entering DNUM's
            # start with the sign reset.
            g.next()
            neg = False
            if g.ch in ("+", "-"):
                neg = g.ch == "-"
                g.next()
            e = 0
            any_digit = False
            while g.ch is not None and g.ch.isdigit():
                e = e * 10 + int(g.ch)
                any_digit = True
                g.next()
            if not any_digit:
                raise DnumError(66, "E WITH NO EXPONENT")
            if g.ch is not None and g.ch.upper() == "E":
                raise DnumError(50, "MORE THAN ONE E IN NUM. DD")
            if neg:
                e = -e
                if e:
                    fractional = True
            if point:
                fractional = True
            scale += e
        if scale:
            pr = mul(pr, power(Dbl.of(10), scale))
        return Number(pr, fractional)


def _fixed(num, fn, what):
    """The magnitude of num as an integer scaled by 2**fn, truncated."""
    q = abs(num.v.exact()) * (1 << fn)
    if fn == 0 and q.denominator != 1:
        # C28-6129 p.29: "A decimal fraction must have a controlling (Fn) entry mode".
        raise DnumError(45, f"{what}: a decimal fraction needs an (Fn) entry mode (C28-6129 p.29)")
    return q.numerator // q.denominator


def _floating_word(exp, frac48, sbyte):
    if not -1023 <= exp <= 1023:
        raise DnumError(113, f"binary exponent {exp} outside +-1023 (C28-6129 p.27; Reference Manual p.79)")
    return (abs(exp) << 53) | ((1 if exp < 0 else 0) << 52) | (frac48 << 4) | (sbyte & 15)


def final(mode, fl, bs, num, fn, sbits, xexp):
    """OUTPUT's conversion to the final bits, right justified in FL.

    mode, fl, bs the dds; num the Number; fn the Fn entry mode or None; sbits the
    S entry (already octal) or None; xexp the X entry or None.
    """
    if fn is not None and mode not in ("U", "B", "BU"):
        raise DnumError(45, f"(F{fn}) has no meaning for use mode {mode} (C28-6129 p.30)")
    if xexp is not None and mode not in ("N", "U"):
        raise DnumError(45, f"X has no meaning for use mode {mode} (C28-6129 p.30)")
    neg = num.v.neg
    if mode in ("N", "U"):
        sbyte = 8 if neg else 0
        if sbits is not None:
            sbyte |= sbits
        v = num.v
        if mode == "U":
            big = abs(v.exact()) >= (1 << 48)
            if fn is None and not num.fractional and not big:
                fn = 0
            if fn is not None:
                # p.28: as an unnormalized number, n fraction bits at the right;
                # "the correct exponent (in this case 27)" for (F21) is 48-n.
                f = _fixed(num, fn, "U")
                if f >> 48:
                    raise DnumError(45, f"{num.v.exact()} does not fit (F{fn})")
                return _floating_word(48 - fn if xexp is None else xexp, f, sbyte)
        if v.is_zero():
            return _floating_word(0 if xexp is None else xexp, 0, sbyte)
        return _floating_word(v.exp if xexp is None else xexp, v.frac >> (BITS - 48), sbyte)
    if mode in ("B", "BU"):
        f = _fixed(num, fn or 0, mode)
        if mode == "BU":
            return f & ((1 << fl) - 1)
        data = fl - bs
        sbyte = 0
        if neg:
            sbyte = 1 << (min(bs, 4) - 1)
        if sbits is not None:
            sbyte |= sbits
        return ((f & ((1 << data) - 1)) << bs) | (sbyte & ((1 << bs) - 1))
    if mode in ("D", "DU"):
        f = _fixed(num, 0, mode)
        if bs < 4:
            raise DnumError(45, f"a {bs}-bit decimal byte holds no digit")
        data = fl if mode == "DU" else fl - bs
        room = data // bs
        digits = str(f)
        if len(digits) > room:
            raise DnumError(45, f"{f} does not fit {room} decimal bytes")
        out = 0
        for ch in digits:
            out = (out << bs) | int(ch)
        if mode == "DU":
            return out
        sbyte = 0
        if neg:
            sbyte = 8
        if sbits is not None:
            sbyte |= sbits
        return (out << bs) | (sbyte & ((1 << bs) - 1))
    raise DnumError(45, f"use mode {mode} in a numeric DD")


def store_entry(mem, p, fn, num, sbits, xexp, chain_bits, more):
    """Fig. 26 p.193, written at bit p of the unit; returns the bit after it.

    CHOSEN: Fig. 26 has no place for the number's own sign, because the sign byte
    holds the S entry until OUTPUT knows the byte size, so one bit `m` follows
    the sign byte.  chain_bits is App. C's 4A chain, whose first bit is Fig. 26's
    d, and whose first 6 bits after it are Fig. 26's 6.
    """
    mem.put(p, 1, 0 if fn is None else 1)
    p += 1
    if fn is not None:
        mem.put(p, 11, fn)
        p += 11
    v = num.v
    mem.put(p, 12, (1 << 11 if v.exp < 0 else 0) | (abs(v.exp) & 2047))
    p += 12
    mem.put(p, 48, v.frac >> 48)
    mem.put(p + 48, 48, v.frac & ((1 << 48) - 1))
    p += 96
    mem.put(p, 8, sbits or 0)
    p += 8
    mem.put(p, 1, 1 if v.neg else 0)
    p += 1
    mem.put(p, 1, 1 if num.fractional else 0)   # b
    p += 1
    mem.put(p, 1, 0 if xexp is None else 1)     # c
    p += 1
    if xexp is not None:
        mem.put(p, 12, (1 << 11 if xexp < 0 else 0) | (abs(xexp) & 2047))
        p += 12
    mem.put_str(p, chain_bits)
    p += len(chain_bits)
    mem.put(p, 1, 1 if more else 0)             # e
    return p + 1


def load_entry(mem, p, read_chain):
    """(fn, num, sbits, xexp, gps, more, next p); sbits 0 is no S entry."""
    fn = None
    if mem.get(p, 1):
        fn = mem.get(p + 1, 11)
        p += 11
    p += 1
    e = mem.get(p, 12)
    exp = -(e & 2047) if e >> 11 else e & 2047
    p += 12
    frac = (mem.get(p, 48) << 48) | mem.get(p + 48, 48)
    p += 96
    sbits = mem.get(p, 8)
    p += 8
    neg = bool(mem.get(p, 1))
    fractional = bool(mem.get(p + 1, 1))
    c = mem.get(p + 2, 1)
    p += 3
    xexp = None
    if c:
        e = mem.get(p, 12)
        xexp = -(e & 2047) if e >> 11 else e & 2047
        p += 12
    gps, p = read_chain(mem, p)
    more = mem.get(p, 1)
    return fn, Number(Dbl(neg, exp, frac), fractional), sbits, xexp, gps, bool(more), p + 1
