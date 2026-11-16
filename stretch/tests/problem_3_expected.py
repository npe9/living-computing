#!/usr/bin/env python3
"""problem_3_expected.py -- the EXPECTED words of C22-6578 Chapter 3's
floating-point examples, worked from the Reference Manual's rules.

THIS IS NOT THE MODEL.  It imports nothing from bsv/ or strap/ and was
written from the Reference Manual (22-6530-2) text alone, one function per
operation, each citing the printed page it transcribes.  It is the long
hand arithmetic of decks/problem_3_*.strap done by machine because a 48-bit
fraction carried through twenty truncating steps is not something to do on
paper; where a deck's data is small integers the same numbers were also
checked on paper and the header of the deck says so.

    python3 problem_3_expected.py            # print every deck's check words
    python3 problem_3_expected.py --self     # the self-checks only

THE RULES, AND WHERE EACH IS PRINTED (Reference Manual printed pages; the
PDF page is the printed page plus 3):

  word      bit 0 EF, 1-10 EM, 11 ES, 12-59 fraction, 60 sign, 61-63 flags
            (p.80 "one EF bit, ten EM bits, and one ES bit"; p.82 flags
            61-63).  Only the N range is implemented here: every deck stays
            far inside it, and a flagged exponent raises.
  single    "Only bit positions 12-59 of the accumulator are used" and
            "All single-precision floating-point operations provide results
            which are truncated to 48 bits" (p.80).
  normalize "a left shift ... to eliminate high-order zeros, or ... a right
            shift to insert a high-order one bit when the arithmetic
            operation produces a result fraction overflow bit.  After the
            shift, the result fraction is truncated"; a zero fraction is
            not normalized (p.81).
  +         p.86-87: the fraction with the smaller exponent is shifted
            right by the difference; both are extended to 96 bits; bits
            shifted beyond the 96 "do not take part"; a difference over 95
            adds nothing; normalized, "the entire 96-bit intermediate sum
            fraction and overflow bit are shifted" and the 48 high-order
            bits replace accumulator bits 12-59; "This normalization is not
            performed if the overflow bit and high-order 48 bits of the
            intermediate sum are zero."  Bits 60-127 are unchanged.
  L         p.88: bits 0-59 replaced, 60-127 not changed.
  M+        p.88-89: the sum goes to storage; "The contents of the entire
            accumulator and its sign byte register remain unchanged".
  ST        p.90: accumulator bits 0-59 to storage; normalized, "the 48-bit
            operand fraction in the accumulator is normalized before being
            placed in storage"; the accumulator is unchanged.
  K         p.90-91: a subtraction whose result is discarded; a difference
            of 48 or less with a zero result is equality, and p.82 says
            which bits are the result: "the high-order 48 bits and the
            overflow bit of the 96-bit intermediate result".
  *         p.92: 48 x 48 -> 96 bits, normalized, then truncated to 48.
  /         p.93-94: both operands pre-normalized; a divisor fraction
            greater than the dividend's gives 48 quotient bits, otherwise
            one is added to the exponent, a one is placed in the
            high-order quotient bit and 47 more are obtained.  No
            remainder.  The quotient is truncated either way.
  R/        p.94: "the same ... with the exception of the interchange of
            the operands"; the sign modifiers apply to the dividend.
  SRT       p.94-95: an odd exponent has one added and the fraction
            shifted right one place; the exponent is halved; "The result is
            a 48-bit fraction."  Truncation of the root is ASSUMED here
            (the page does not say rounded or truncated); the one deck
            that uses SRT takes the root of an exact square, where the two
            agree.
  D+        p.95: accumulator bits 12-107 plus the operand extended with 48
            zeros; the sum replaces bits 0-107.
  DL        p.96: as L, and bits 60-107 are set to zero.
  SRD       p.96: "adding one to the fraction in the accumulator in bit
            position 60 ... The 48 low-order bits are discarded.  When
            normalized operation is specified, the 48-bit sum is then
            normalized".  The accumulator is unchanged "unless used as the
            effective address".
  SLO       p.97: fraction is bits 60-107, exponent is the accumulator's
            less 48, sign is the accumulator's; normalized, shifted left
            "until a high-order one bit is leftmost".
  D*        p.97: as *, the 96-bit product to bits 12-107.
  LFT       p.98: the operand, normalized if asked, to the factor register.
  *+        p.98: FT times the operand, 96 bits, "remains unnormalized
            throughout the addition", added as in D+.
  E+I       p.102-103: the immediate is added to the exponent; unnormalized
            leaves the fraction alone.
  address 8 C22-6578 printed p.28 comment (b): "the leading 60 bits of the
            accumulator plus the lowest four-bits of $SB".
"""
import math
import sys
from fractions import Fraction

M48 = (1 << 48) - 1
M96 = (1 << 96) - 1


def dec(w):
    """A storage word as (exponent, fraction48, negative)."""
    if w >> 63:
        raise ValueError("flagged exponent: outside this calculator")
    em = (w >> 53) & 0x3FF
    return (-em if (w >> 52) & 1 else em), (w >> 4) & M48, bool((w >> 3) & 1)


def enc(e, f, neg, flags=0):
    assert 0 <= f <= M48 and abs(e) < 1024, (e, f)
    return (abs(e) << 53) | ((1 if e < 0 else 0) << 52) | (f << 4) | (8 if neg else 0) | flags


def value(w):
    e, f, neg = dec(w)
    v = Fraction(f, 1 << 48) * Fraction(2) ** e
    return -v if neg else v


def norm(e, f, width):
    """p.81.  f may carry one overflow bit above `width`."""
    if f == 0:
        return e, 0
    if f >> width:
        f >>= 1
        e += 1
    while not (f >> (width - 1)):
        f <<= 1
        e -= 1
    return e, f


class Acc:
    """Accumulator bits 0-107 and the sign: exponent, two 48-bit halves."""

    def __init__(self):
        self.e, self.hi, self.lo, self.neg = 0, 0, 0, False
        self.ft = 0                       # the factor register, word 14

    # -- the accumulator as storage words 8 and 9 ---------------------------
    def word8(self):
        """Word 8 is accumulator bits 0-63: exponent, the high fraction, and
        the top four bits of the low fraction."""
        return (enc(self.e, self.hi, False) & ~0xF) | (self.lo >> 44)

    def left(self):
        """Address 8.0 as a floating-point operand."""
        return enc(self.e, self.hi, self.neg)

    # -- single precision ----------------------------------------------------
    def _sum(self, a, m, normalized):
        """p.86-87.  a, m are (e, f48, neg); a is the accumulator operand.
        Returns (e, f48, neg) and whether the high 48 bits came out zero."""
        (ea, fa, na), (em, fm, nm) = a, m
        if ea >= em:
            e, d = ea, ea - em
            big, small = (fa << 48, na), (((fm << 48) >> d) if d <= 95 else 0, nm)
        else:
            e, d = em, em - ea
            big, small = (fm << 48, nm), (((fa << 48) >> d) if d <= 95 else 0, na)
        v = (-big[0] if big[1] else big[0]) + (-small[0] if small[1] else small[0])
        # p.82: a zero sum takes the sign of the operand with the larger
        # exponent, the accumulator's when they are equal.
        neg = (v < 0) if v else (na if ea >= em else nm)
        mag = abs(v)
        if normalized:
            if (mag >> 48) == 0:
                return (e, 0, neg), mag
            e, mag = norm(e, mag, 96)
        return (e, (mag >> 48) & M48, neg), mag

    def add(self, w, normalized=True, negate=False):
        e, f, n = dec(w)
        (self.e, self.hi, self.neg), _ = self._sum((self.e, self.hi, self.neg), (e, f, n ^ negate), normalized)

    def sub(self, w, normalized=True):
        self.add(w, normalized, negate=True)

    def load(self, w, normalized=False):
        e, f, self.neg = dec(w)
        self.e, self.hi = norm(e, f, 48) if normalized else (e, f)

    def store(self, normalized=False):
        e, f = norm(self.e, self.hi, 48) if normalized else (self.e, self.hi)
        return enc(e, f, self.neg)

    def add_to_memory(self, w, normalized=True):
        """M+: the new storage word.  The accumulator is not touched."""
        (e, f, neg), _ = self._sum((self.e, self.hi, self.neg), dec(w), normalized)
        return enc(e, f, neg, w & 7)

    def compare(self, w):
        """K: 'AL', 'AE' or 'AH' (p.90-91, zero test of p.82)."""
        m = dec(w)
        a = (self.e, self.hi, self.neg)
        if abs(a[0] - m[0]) > 48:
            raise ValueError("exponent difference over 48: not needed here")
        (_, _, neg), mag = self._sum(a, (m[0], m[1], not m[2]), False)
        if (mag >> 48) == 0:
            return 'AE'
        return 'AL' if neg else 'AH'

    def mul(self, w, normalized=True):
        e, f, n = dec(w)
        self.e, p = self.e + e, self.hi * f
        if normalized:
            self.e, p = norm(self.e, p, 96)
        self.hi, self.neg = p >> 48, self.neg ^ n

    def _quot(self, d, v):
        """p.93-94, normalized: d / v as (e, f48)."""
        (ed, fd), (ev, fv) = norm(d[0], d[1], 48), norm(v[0], v[1], 48)
        if fv == 0:
            raise ZeroDivisionError("ZD")
        if fd == 0:
            return ed - ev, 0
        if fv > fd:
            return ed - ev, (fd << 48) // fv
        return ed - ev + 1, (fd << 47) // fv

    def div(self, w):
        e, f, n = dec(w)
        self.e, self.hi = self._quot((self.e, self.hi), (e, f))
        self.neg ^= n

    def rdiv(self, w, negate=False):
        """R/, and R/N with negate: storage / accumulator."""
        e, f, n = dec(w)
        self.e, self.hi = self._quot((e, f), (self.e, self.hi))
        self.neg ^= n ^ negate

    def store_root(self):
        """SRT(N).  Truncation of an inexact root is assumed; see above."""
        import math
        if self.neg:
            raise ValueError("IR")
        e, f = self.e, self.hi
        if e % 2:
            e, r = e + 1, math.isqrt(f << 47)
        else:
            r = math.isqrt(f << 48)
        e, r = norm(e // 2, r, 48)
        return enc(e, r, False)

    def exp_add(self, n):
        self.e += n

    # -- double precision ----------------------------------------------------
    def _dsum(self, m, normalized):
        """p.95.  m is (e, f96, neg)."""
        fa = (self.hi << 48) | self.lo
        em, fm, nm = m
        if self.e >= em:
            e, d = self.e, self.e - em
            big, small = (fa, self.neg), ((fm >> d) if d <= 95 else 0, nm)
        else:
            e, d = em, em - self.e
            big, small = (fm, nm), ((fa >> d) if d <= 95 else 0, self.neg)
        v = (-big[0] if big[1] else big[0]) + (-small[0] if small[1] else small[0])
        neg = (v < 0) if v else (self.neg if self.e >= em else nm)
        mag = abs(v)
        if normalized:
            e, mag = norm(e, mag, 96)
        mag &= M96
        self.e, self.hi, self.lo, self.neg = e, mag >> 48, mag & M48, neg

    def dadd(self, w, normalized=True, negate=False):
        e, f, n = dec(w)
        self._dsum((e, f << 48, n ^ negate), normalized)

    def dsub(self, w, normalized=True):
        self.dadd(w, normalized, negate=True)

    def dload(self, w, normalized=False):
        self.load(w, False)
        self.lo = 0
        if normalized:
            self.e, f = norm(self.e, self.hi << 48, 96)
            self.hi, self.lo = f >> 48, f & M48

    def dmul(self, w, normalized=True):
        e, f, n = dec(w)
        self.e, p = self.e + e, self.hi * f
        if normalized:
            self.e, p = norm(self.e, p, 96)
        self.hi, self.lo, self.neg = p >> 48, p & M48, self.neg ^ n

    def load_factor(self, w, normalized=True):
        e, f, n = dec(w)
        if normalized:
            e, f = norm(e, f, 48)
        self.ft = enc(e, f, n)

    def mul_add(self, w, normalized=True):
        e1, f1, n1 = dec(self.ft)
        e2, f2, n2 = dec(w)
        self._dsum((e1 + e2, f1 * f2, n1 ^ n2), normalized)

    def store_rounded(self, normalized=True):
        e, r = self.e, (((self.hi << 48) | self.lo) + (1 << 47)) >> 48
        if normalized:
            e, r = norm(e, r, 48)
        return enc(e, r & M48, self.neg)

    def store_low(self, normalized=False):
        e, f = self.e - 48, self.lo
        if normalized:
            e, f = norm(e, f, 48)
        return enc(e, f, self.neg)

    def to_left(self, w):
        """A store whose address is 8.0: bits 0-59 and the sign."""
        self.e, self.hi, self.neg = dec(w)


def fl(x):
    """The normalized word of an exactly representable rational."""
    x = Fraction(x)
    if x == 0:
        return 0
    e, m = 0, abs(x)
    while m >= 1:
        m /= 2
        e += 1
    while m < Fraction(1, 2):
        m *= 2
        e -= 1
    f = m * (1 << 48)
    assert f.denominator == 1, "not exact in 48 bits"
    return enc(e, int(f), x < 0)


# What the host STRAP II makes of the pages' decimal constants.  A decimal
# with a point comes out one unit of the 48th place short when it is an
# exact binary number, because the conversion multiplies by a truncated
# 1/10 (tests/check_strap2_dd.py: "17.5 is ... one unit low in 48 bits,
# and 1.0 and .5 likewise").  These are copied from its output, and every
# deck that uses one checks the word in storage too, so they are premises
# that are tested, not trusted.
D_0_5 = 0x003FFFFFFFFFFFF0        # DD(N), 0.5     .FFFFFFFFFFFF x 2^-1
D_2_0 = 0x002FFFFFFFFFFFF0        # DD(N), 2.0     .FFFFFFFFFFFF x 2^1
D_2_5 = 0x0049FFFFFFFFFFF0        # DD(N), 2.5     .9FFFFFFFFFFF x 2^2
D_8_0 = 0x006FFFFFFFFFFFF0        # DD(N), 8.0     .FFFFFFFFFFFF x 2^3
D_20_0 = 0x00A9FFFFFFFFFFF0       # DD(N), 20.0    .9FFFFFFFFFFF x 2^5
D_39_0 = 0x00C9BFFFFFFFFFF0       # DD(N), 39.0    .9BFFFFFFFFFF x 2^6
D_PI_4 = 0x000C90FDAA221680       # DD(N), $PI/4   .C90FDAA22168 x 2^0


# ---------------------------------------------------------------------------
# The problems.  Each returns [(label, word)] in the deck's own check order.
# ---------------------------------------------------------------------------

X48 = enc(48, 0, False)                   # DD(N), 0.0X48


def p31(n_word):
    """3.1: DL(U),DOG / D+(U),X48 / ST(N),CAT / SLO(N),CAT+1.0"""
    a = Acc()
    a.dload(n_word)
    a.dadd(X48, normalized=False)
    return a.store(normalized=True), a.store_low(normalized=True), a


def p32_count(n_word):
    """3.2: the 18 bits ST(BU,18),17.28,68 takes: accumulator bits 42-59."""
    a = Acc()
    a.dload(n_word)
    a.dadd(X48, normalized=False)
    return a.hi & 0x3FFFF


def p33_m1(x, coef):
    a = Acc()
    a.load(coef[0])
    poly = a.store(normalized=True)
    a.load(x)
    k = 1
    while True:
        xk = a.store()
        a.mul(coef[k])
        a.add(poly)
        poly = a.store()
        k += 1
        if k > 20:
            break
        a.load(xk)
        a.mul(x)
    return poly, xk, a


def p33_m2(x, coef):
    a = Acc()
    a.load(coef[20], normalized=True)
    for k in range(19, -1, -1):
        a.mul(x)
        a.add(coef[k])
    return a.store(), a


def p33_m3(x, coef):
    a = Acc()
    top = len(coef) - 1
    a.load(coef[top], normalized=True)
    for k in range(top - 1, -1, -1):
        a.dmul(x)
        a.dadd(coef[k])
        a.to_left(a.store_rounded(normalized=True))
    return a.store(), a


def p34(A, B, N):
    """3.4, either method: the arithmetic is the same sequence."""
    a = Acc()
    a.load(B)
    a.sub(A)
    a.div(N)
    h = a.store()
    a.exp_add(-1)
    a.add(A)
    ans = 0                               # ANS DD(N), 0
    for i in range(20):
        if i:
            a.load(temp)
            a.add(h)
        temp = a.store()
        a.mul(a.left())
        a.mul(a.left())
        ans = a.add_to_memory(ans)
    a.mul(h)
    return ans, temp, h, a


def p35(X, NUM, TWO):
    a = Acc()
    a.load(X)
    a.mul(X)
    temp = a.store()
    num = NUM
    a.load(num)
    for _ in range(19):
        a.rdiv(temp, negate=True)
        temp1 = a.store(normalized=True)
        a.load(num)
        a.sub(TWO)
        num = a.store()
        a.add(temp1)
    a.rdiv(X)
    return a.store(), num, temp, temp1, a


def p36(A, B):
    a = Acc()
    a.load(A[0])
    a.dmul(B[0])
    for k in range(1, 17):
        a.load_factor(A[k])
        a.mul_add(B[k])
    return a.store_rounded(normalized=True), a


def p37(EN, GUESS, HALF):
    a = Acc()
    a.load(EN)
    a.exp_add(-1)
    a.add(EN)
    temp = a.store()
    a.load(GUESS, normalized=True)
    for _ in range(10):
        xk = a.store(normalized=True)
        a.mul(xk)
        a.mul(xk)
        a.exp_add(1)
        a.add(EN)
        a.rdiv(temp)
        a.add(HALF)
        a.mul(xk)
    return a.store(normalized=True), temp, xk, a


def p38(ints, eplus=True):
    """3.8.  LCV leaves the integer in accumulator bits 12-59 with a zero
    exponent (offset 68 puts its units bit at bit 59) and the sign in the
    sign byte; E+I,48 makes that an unnormalized integer.  eplus=False is
    the program with the page's EPLUS statement taken out, comment (b)."""
    a = Acc()
    total = 0
    floats = []
    for n in ints:
        a.e, a.hi, a.lo, a.neg = 0, abs(n), 0, n < 0
        if eplus:
            a.exp_add(48)
        floats.append(a.store(normalized=True))
        a.mul(a.left())
        a.add(total)
        total = a.store()
    root = a.store_root()
    out = []
    for w in floats:
        a.load(w, normalized=True)
        try:
            a.div(root)
        except ZeroDivisionError:
            pass                          # p.93: ZD, "the accumulator ... remain unchanged"
        out.append(a.store())
    return out, total, root


def p39(a1, a2, m1, m2):
    """3.9 Method 1's subtraction: 'RLZ', 'RZ' or 'RGZ', which the program
    copies to $AL, $AE, $AH.  a1, a2 are the accumulator's two halves as
    the words ST(U) and SLO(U) make of it."""
    a = Acc()
    a.dload(a2)
    a.dsub(m2)
    a.dadd(a1)
    a.dsub(m1)
    if a.hi == 0 and a.lo == 0:
        return 'RZ'
    return 'RLZ' if a.neg else 'RGZ'


def p39_run(method, ahi, alo, m1, m2):
    """3.9 run whole, as a deck does: the deck loads the accumulator with
    DL(U), AHI / D+(U), ALO, then the printed Method 1 or 2.  Returns the
    comparison indicator ('AL', 'AE' or 'AH'), A1, A1+1, and the
    accumulator at the end."""
    a = Acc()
    a.dload(ahi)
    a.dadd(alo, normalized=False)
    a1, a2 = a.store(), a.store_low()          # ST(U), A1 / SLO(U), A1+1.
    if method == 2:
        # K(U), M: Reference Manual printed p.90-91.
        (ea, fa, na), (em, fm, nm) = (a.e, a.hi, a.neg), dec(m1)
        if abs(ea - em) > 48:
            # "the algebraically larger of the two numbers, judged by
            # exponent and fraction sign, is considered high"
            if na != nm:
                ind = 'AL' if na else 'AH'
            else:
                ind = 'AH' if (ea > em) != na else 'AL'
            return ind, a1, a2, a
        ind = a.compare(m1)
        if ind != 'AE':
            return ind, a1, a2, a
    r = Acc()
    r.dload(a2)
    r.dsub(m2, normalized=(method == 1))       # D-(N) in 1, D-(U) in 2
    r.dadd(a1)
    r.dsub(m1)
    ind = 'AE' if r.hi == 0 and r.lo == 0 else ('AL' if r.neg else 'AH')
    a = Acc()
    a.dload(a2)                                # restore: DL(U), A1+1.
    a.dadd(a1, normalized=False)               #          D+(U), A1
    return ind, a1, a2, a


P39_CASES = {
    # name: (method, AHI, ALO, M1, M1+1)
    'm1_less': (1, enc(1, M48, False), enc(-47, 1 << 47, False), enc(2, 1 << 47, False), enc(-46, 0, False)),
    'm1_equal': (1, enc(1, M48, False), enc(-47, 1 << 47, False), enc(1, M48, False), enc(-47, 1 << 47, False)),
    'm1_greater': (1, enc(1, 1 << 47, False), enc(-47, 3 << 46, False), enc(1, 1 << 47, False), enc(-47, 1 << 47, False)),
    'm2_page_fault': (2, enc(50, 0, False), enc(2, 0, False), enc(1, M48, False), enc(-47, M48, False)),
    'm2_less': (2, enc(1, M48, False), enc(-47, 1 << 47, False), enc(2, 1 << 47, False), enc(-46, 0, False)),
}


def self_checks():
    """Things known without this file."""
    ok = True

    def check(name, got, want):
        nonlocal ok
        if got != want:
            ok = False
            print(f"SELF-CHECK FAIL {name}: got {got!r}, want {want!r}")

    check("1.0", fl(1), 0x0028000000000000)
    check("2.5", fl(Fraction(5, 2)), 0x004A000000000000)
    check("-5", fl(-5), 0x006A000000000008)
    check("value", value(fl(Fraction(-7, 4))), Fraction(-7, 4))
    # C22-6578 printed p.26 comment (b): "illustrate ... using N = 2.5".
    i, f, _ = p31(fl(Fraction(5, 2)))
    check("3.1 I", value(i), 2)
    check("3.1 F", value(f), Fraction(1, 2))
    a = Acc()
    a.load(fl(3))
    a.mul(fl(5))
    a.add(fl(-1))
    a.div(fl(7))
    check("(3*5-1)/7", value(a.store()), 2)
    a.load(fl(1))
    a.div(fl(3))
    check("1/3 truncates", a.store(), enc(-1, 0xAAAAAAAAAAAA, False))
    a.load(fl(49))
    check("sqrt 49", value(a.store_root()), 7)
    a.load(fl(8))
    check("sqrt 8 is odd-exponent free", value(a.store_root()) ** 2 <= 8, True)
    # Reference Manual Figure 28's subtraction, on small numbers.
    check("3.9 less", p39(fl(4), fl(Fraction(1, 1 << 46)), fl(4), fl(Fraction(1, 1 << 45))), 'RLZ')
    check("3.9 equal", p39(fl(4), fl(Fraction(1, 1 << 46)), fl(4), fl(Fraction(1, 1 << 46))), 'RZ')
    return ok


def h(w):
    return '0x%016X' % w


F = Fraction
P33_COEF = [(-1) ** k * (k + 1) for k in range(21)]
P38_INTS = [1, -2, 3, 1024, -512, 768, 100, -99, 7, 1234, -321, 5, 64, -640, 17,
            250, -33, 11, 400, -8, 129, 1000, 1511, -2132, 2179]


def decks(which):
    """Print each deck's expected words from its data."""
    if which in ('31', 'all'):
        print("problem_3_1  (N, I, F)")
        for name, n in (('A', F(-4939, 4)), ('B', F(1, 4)), ('C', F(2097163, 2)), ('last', F(5, 2))):
            i, f, _ = p31(fl(n))
            print(f"  {name:5s} {h(fl(n))} {h(i)} {h(f)}")
    if which in ('32', 'all'):
        print("problem_3_2  (count field)")
        for name, n in (('A', F(-29, 4)), ('B', F(2097163, 2)), ('last', F(5, 2))):
            c = p32_count(fl(n))
            print(f"  {name:5s} {c}  $1 = {h((0xA5A5A5A5A5A5A5A5 & ~(0x3FFFF << 18)) | (c << 18))}")
    if which in ('33', 'all'):
        coef = [fl(c) for c in P33_COEF]
        x = fl(3)
        p = sum(c * 3 ** k for k, c in enumerate(P33_COEF))
        print(f"problem_3_3  P(3) = {p} = {h(fl(p))}; 3^20 = {3 ** 20} = {h(fl(3 ** 20))}")
        poly, xk, a = p33_m1(x, coef)
        print(f"  method 1 POLY {h(poly)} XK {h(xk)} word 8 {h(a.word8())}")
        poly, a = p33_m2(x, coef)
        print(f"  method 2 POLY {h(poly)} word 8 {h(a.word8())}")
        poly, a = p33_m3(x, coef)
        print(f"  method 3 block A POLYA {h(poly)}")
        u = F(1, 1 << 47)
        poly, a = p33_m3(fl(F(3, 2)), [0, 0, fl(1 + u)])
        print(f"  method 3 block B POLYB {h(poly)}")
        poly, a = p33_m3(fl(1 + u), [0] * 20 + [fl(1 + u)])
        print(f"  method 3 last    POLY  {h(poly)} word 8 {h(a.word8())} low half {a.lo:012X}")
    if which in ('34', 'all'):
        print("problem_3_4  A = 0, B = 2.0 and N = 20.0 as the host STRAP II makes them")
        for name, (b, n) in (('printed', (D_2_0, D_20_0)), ('exact 2, 20', (fl(2), fl(20)))):
            ans, temp, hh, a = p34(0, b, n)
            print(f"  {name}: B {h(b)} N {h(n)}")
            print(f"    ANS {h(ans)} = {float(value(ans)):.15f}   (times h = {float(value(ans) * value(hh)):.15f})")
            print(f"    TEMP {h(temp)} = {float(value(temp)):.15f}   H {h(hh)} = {float(value(hh)):.17f}")
            print(f"    word 8 {h(a.word8())} = {float(value(a.left())):.15f}")
        exact = sum(F(2 * i + 1, 20) ** 4 for i in range(20))
        print(f"  in exact arithmetic: sum f = {float(exact):.15f}, times 1/10 = {float(exact / 10):.15f}, "
              f"last f times h = {float(F(39, 20) ** 4 / 10):.15f}")
    if which in ('35', 'all'):
        print("problem_3_5  X = $PI/4, NUM = 39.0, TWO = 2.0 as the host STRAP II makes them")
        for name, c in (('printed', (D_PI_4, D_39_0, D_2_0)), ('exact 39, 2', (D_PI_4, fl(39), fl(2)))):
            f, num, temp, temp1, a = p35(*c)
            print(f"  {name}:")
            print(f"    TEMP2 {h(f)} = {float(value(f)):.16f}   NUM {h(num)} = {float(value(num)):.16f}")
            print(f"    TEMP {h(temp)} = {float(value(temp)):.16f}   TEMP1 {h(temp1)} = {float(value(temp1)):.16f}")
            print(f"    word 8 {h(a.word8())}")
    if which in ('37', 'all'):
        print("problem_3_7  EN = 8.0, GUESS = 2.5, HALF = 0.5 as the host STRAP II makes them")
        for name, c in (('printed', (D_8_0, D_2_5, D_0_5)), ('exact', (fl(8), fl(F(5, 2)), fl(F(1, 2))))):
            ans, temp, xk, a = p37(*c)
            print(f"  {name}:")
            print(f"    ANS {h(ans)} = {float(value(ans)):.16f}   TEMP {h(temp)} = {float(value(temp)):.16f}")
            print(f"    XK {h(xk)} = {float(value(xk)):.16f}   word 8 {h(a.word8())}")
    if which in ('36', 'all'):
        av = [2 ** 40 + 1, 2 ** 16] + list(range(2, 17))
        bv = [2 ** 40 + 1, 2 ** 16] + [(-1) ** k * k for k in range(2, 17)]
        total = sum(x * y for x, y in zip(av, bv))
        c, a = p36([fl(x) for x in av], [fl(x) for x in bv])
        print(f"problem_3_6  (a, b) = {total} = 2**80 + 2**41 + 2**32 + {total - 2**80 - 2**41 - 2**32}")
        print(f"  C {h(c)}   word 8 {h(a.word8())}   $FT {h(a.ft)}   low half {a.lo:012X}")
        bv[1] -= 1
        c, a = p36([fl(x) for x in av], [fl(x) for x in bv])
        print(f"  with b(1) = 65535: C {h(c)}")
    if which in ('38', 'all'):
        total = sum(n * n for n in P38_INTS)
        print(f"problem_3_8  sum of squares = {total} = 4**{total.bit_length() // 2}, root {math.isqrt(total)}")
        out, tot, root = p38(P38_INTS)
        print(f"  SUM {h(tot)}  ROOT {h(root)}")
        for k, (n, w) in enumerate(zip(P38_INTS, out)):
            assert value(w) == F(n, math.isqrt(total))
            print(f"  FLOAT+{k:<2d} {n:6d}/4096  {h(w)}")
        out, tot, root = p38(P38_INTS, eplus=False)
        print(f"  without EPLUS: SUM {h(tot)}  ROOT {h(root)}")
        for k, (n, w) in enumerate(zip(P38_INTS, out)):
            assert value(w) == F(n, 1 << 48)
            print(f"  FLOAT+{k:<2d} {n:6d}/2**48  {h(w)}")

    if which in ('39', 'all'):
        print("problem_3_9  (the deck's AHI, ALO, M1, M1+1; true order by exact values)")
        for name, c in P39_CASES.items():
            ind, a1, a2, a = p39_run(*c)
            va = value(c[1]) + value(c[2])
            vm = value(c[3]) + value(c[4])
            true = 'AL' if va < vm else 'AE' if va == vm else 'AH'
            print(f"  {name:14s} {ind}  (true {true})  A1 {h(a1)}  A1+1 {h(a2)}  word 8 {h(a.word8())}  low {a.lo:012X}")


if __name__ == '__main__':
    if not self_checks():
        sys.exit(1)
    print("self-checks pass")
    if '--self' not in sys.argv:
        decks(sys.argv[1] if len(sys.argv) > 1 else 'all')
