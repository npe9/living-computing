"""value.py -- VALUE, C22-6729 pp.54-60, reading coded expressions from storage.

Its output is Fig. 9's: a bit-style value Sinb and an integer Sini, kept
separate, because INSERT adds them "according to the function of the address"
(p.144).

The arithmetic of each operator is UNSPECIFIED on the guide's pages.  What is
here comes from C22-6531 printed pp.10-12 and C22-6578 printed p.64, as verified
in strap_asm's tokenizer: a point makes a bit address, an integer before it
counts words, an integer after it counts bits, and a bit address is unchanged by
it.  CHOSEN: * and / apply to both parts; a quotient of two bit addresses is an
integer.

Python recursion stands in for the push list of Fig. 10.  VBREAK, the break exit
of pp.55-57, is here simply "not available": VALUE goes on through the expression
so that undefined entries are made (p.19), and the caller decides.
"""
from .a8 import a8_bits
from .coded import OP_NAME
from .optable import dds_parts
from .symtab import KIND_LABEL, KIND_SYN, KIND_UNDEF, KIND_SPECIAL

A8_TO_CHAR = None


def _chars():
    from .a8 import A8
    return {v: k for k, v in A8.items()}


class V:
    __slots__ = ("B", "I", "X", "xq", "avail", "dds", "sym", "gps", "next", "dims", "nullf")

    def __init__(self):
        self.B = 0
        self.I = 0
        self.X = 0
        self.xq = False
        self.avail = True
        self.dds = None         # 13 bits, or None for no reference
        self.sym = None
        self.gps = []
        self.next = 0
        self.dims = None
        self.nullf = False

    @property
    def total(self):
        return self.B + self.I


class Value:
    """The evaluator.  mem holds the expressions; st is the symbol table."""

    def __init__(self, st, messages):
        self.st = st
        self.msg = messages
        self.vcundf = False     # p.57: may make an undefined entry
        self.abs = 0            # $4
        self.sym = 0            # $6
        self.have_counters = False
        self.chars = _chars()

    # -- the location counter ---------------------------------------------------
    def counter_value(self, absc, symc):
        """location = value of the special symbol in $6, if any, plus $4 (p.13)."""
        if not symc:
            return absc
        v = self.symbol_value(symc)
        return None if v is None else v[0] + v[1] + absc

    def dollar(self):
        if not self.have_counters:
            return None
        return self.counter_value(self.abs, self.sym)

    # -- a symbol ---------------------------------------------------------------
    def symbol_value(self, f):
        """(B, I, X, xq) of the symbol at function f, or None if not yet known."""
        st = self.st
        if st.get(f, "ZST26"):
            return (st.get(f, "ZVALB"), st.get(f, "ZVALI"), st.get(f, "ZX"), st.get(f, "ZXQ"))
        kind = st.get(f, "ZKIND")
        if kind == KIND_LABEL:
            if not st.get(f, "ZCTR"):
                return None
            at = self.counter_value(st.get(f, "ZABS"), st.get(f, "ZSYM"))
            if at is None:
                return None
            return self._enter(f, at, 0, 0, 0)
        if kind == KIND_UNDEF:
            return None
        if st.get(f, "ZST17"):
            # p.32: UITER assigns zero to the base symbol of a circular chain;
            # C28-6129 p.21: A SYN,B; B SYN,A+5 gives A=0, B=5.
            st.put(f, "ZST4", 1)
            return self._enter(f, 0, 0, 0, 0)
        st.put(f, "ZST17", 1)
        try:
            if kind == KIND_SYN:
                got = self._syn(f)
            else:
                got = self._special(f)
        finally:
            st.put(f, "ZST17", 0)
        if st.get(f, "ZST26"):      # circular, zero already given
            return (st.get(f, "ZVALB"), st.get(f, "ZVALI"), st.get(f, "ZX"), st.get(f, "ZXQ"))
        return got

    def _enter(self, f, b, i, x, xq):
        st = self.st
        st.put(f, "ZVALB", b)
        st.put(f, "ZVALI", i)
        st.put(f, "ZX", x)
        st.put(f, "ZXQ", xq)
        st.put(f, "ZST26", 1)
        return (b, i, x, xq)

    def _syn(self, f):
        st = self.st
        saved = (self.abs, self.sym, self.have_counters)
        # A $ in a SYN is the counter at the SYN's own unit (NSYN keeps it).
        self.have_counters = bool(st.get(f, "ZCTR"))
        self.abs, self.sym = st.get(f, "ZABS"), st.get(f, "ZSYM")
        try:
            v = self.read_field(st.mem, st.get(f, "ZEXPR"))
        finally:
            self.abs, self.sym, self.have_counters = saved
        if st.get(f, "ZST26"):      # circular: the zero stands (p.32)
            return None
        if not v.avail:
            return None
        if not st.get(f, "ZST3") and v.dds is not None:
            # p.31 of C22-6531: dds transferred to A, as is the classification.
            st.put(f, "ZDDS", v.dds)
            st.put(f, "ZST3", 1)
        return self._enter(f, v.B, v.I, v.X, 1 if v.xq else 0)

    def _special(self, f):
        """p.34: the sum of the current symbolic counter and the absolute one,
        here with the rounding a new symbolic counter carries (p.33) and the
        length of a DD or DR that was not known (14J)."""
        st = self.st
        at = self.counter_value(st.get(f, "ZABS"), st.get(f, "ZSYM"))
        if at is None:
            return None
        n = st.get(f, "ZDIMN")
        if n:
            size = st.get(f, "ZFLM")
            addr = st.get(f, "ZDIMX")
            for _ in range(n):
                v = self.read_field(st.mem, addr)
                if not v.avail:
                    return None
                size *= v.total
                addr = v.next
            at += size
        expr = st.get(f, "ZEXPR")
        if expr:
            v = self.read_field(st.mem, expr)
            if not v.avail:
                return None
            at = v.B + v.I      # an SLC: the whole location
        r = st.get(f, "ZROUND")
        if r:
            unit = 32 if r == 1 else 64
            at = (at + unit - 1) // unit * unit
        return self._enter(f, at, 0, 0, 0)

    def symbol_dds(self, f):
        """The dds a symbol carries, or None."""
        st = self.st
        if not st.get(f, "ZST3"):
            if st.get(f, "ZKIND") == KIND_SYN:
                self.symbol_value(f)
            if not st.get(f, "ZST3"):
                return None
        d = st.get(f, "ZDDS")
        mode, fl, bs = dds_parts(d)
        flx, bsx = st.get(f, "ZFLX"), st.get(f, "ZBSX")
        if flx:
            v = self.read_field(st.mem, flx)
            if not v.avail:
                return None
            fl = v.total
        if bsx:
            v = self.read_field(st.mem, bsx)
            if not v.avail:
                return None
            bs = v.total
        return (d >> 10 << 10) | ((fl & 63) << 4) | (bs & 15)

    def lookup_or_enter(self, name):
        st = self.st
        f = st.search(name)
        if f is None and self.vcundf:
            f, _ = st.addord(name, KIND_UNDEF)
        if f is not None:
            st.put(f, "ZST24", 1)  # p.33: referenced from an address field
        return f

    # -- reading expressions ----------------------------------------------------
    def read_field(self, mem, addr):
        """A whole field: expression, then its g.p. chain (Appendix C)."""
        v = V()
        p = addr
        if mem.get(p, 1) == 0:
            v.next = p + 1
            return v
        prefix = mem.get(p + 1, 3)
        p += 4
        if prefix == 0b111:         # null: ends at its first 0
            p = self._skip_ones(mem, p)
            v.nullf = True
        elif prefix == 0b000:
            p = self._normal(mem, p, v)
        else:
            raise ValueError("prefix %o" % prefix)
        v.next = self._gp_chain(mem, p, v)
        return v

    def _gp_chain(self, mem, p, v):
        """4A: the g.p. chain and its final 0; the bit after."""
        while mem.get(p, 1):
            n = mem.get(p + 1, 6)
            p += 7
            inner = V()
            prefix = mem.get(p, 4)
            p += 4
            if prefix == 0b1111:
                p = self._skip_ones(mem, p)
            else:
                p = self._normal(mem, p, inner)
            if not inner.avail:
                v.avail = False
            v.gps.append((n, inner.total))
        return p + 1

    def read_chain(self, mem, p):
        """For Fig. 26: ([(n, value)], the bit after).  Fig. 26's d is the chain's
        first bit."""
        v = V()
        p = self._gp_chain(mem, p, v)
        if not v.avail:
            raise ValueError("g.p. value unavailable")
        return v.gps, p

    @staticmethod
    def _skip_ones(mem, p):
        while mem.get(p, 1):
            p += 1
        return p + 1

    def _normal(self, mem, p, v):
        data = []
        while mem.get(p, 1):        # 2A
            p += 1
            kind = mem.get(p, 2)
            p += 2
            b = i = 0
            ok = True
            if kind == 0b00:        # symbolic
                n = mem.get(p, 7)
                p += 7
                text = "".join(self.chars.get(mem.get(p + 8 * k, 8), "\0") for k in range(n))
                p += 8 * n
                if text == "$\0\0":   # the lone $, Fig. 14 p.76
                    at = self.dollar()
                    ok = at is not None
                    b = at or 0
                else:
                    f = self.lookup_or_enter(text)
                    got = None if f is None else self.symbol_value(f)
                    if got is None:
                        ok = False
                    else:
                        b, i = got[0], got[1]
                        if got[3]:
                            v.X, v.xq = got[2], True
                    if f is not None:
                        d = self.symbol_dds(f)
                        v.dds = d
                        v.sym = f
            elif kind == 0b10:      # absolute
                i = mem.get(p, 24)
                p += 24
            elif kind == 0b11:      # long prefix
                long2 = mem.get(p, 2)
                p += 2
                if long2 != 0:
                    raise ValueError("unused datum prefix")
                b = mem.get(p, 24)
                p += 24
                v.dds = mem.get(p, 13)
                p += 13
            else:
                raise ValueError("sub-expression datum")
            # 2E: S/X, each a coded expression without 4A.
            while mem.get(p, 1):
                p += 4
                sub = V()
                p = self._normal(mem, p, sub)
                if not sub.avail:
                    ok = False
                    continue
                v.xq = True
                v.X = (sub.B >> 6) & 15 if sub.B else sub.I & 15
            p += 1
            data.append([b, i, ok])
        p += 1
        # The operators, in the order performed.
        segs = [[n, n, d[0], d[1], d[2]] for n, d in enumerate(data, 1)]

        def ending(n):
            for s in segs:
                if s[1] == n:
                    return s
            return None

        def starting(n):
            for s in segs:
                if s[0] == n:
                    return s
            return None

        while mem.get(p, 1):
            code = mem.get(p + 1, 3)
            number = mem.get(p + 4, 5)
            p += 9
            op = OP_NAME[code]
            if op == ".L" or (op == ".+" and starting(number + 1) is None):
                s = ending(number)
                s[2], s[3] = s[3] * 64 + s[2], 0
            elif op == ".R":
                s = starting(number + 1)
                s[2], s[3] = s[2] + s[3], 0
            elif op == "U-":
                s = starting(number + 1)
                s[2], s[3] = -s[2], -s[3]
            else:
                a, c = ending(number), starting(number + 1)
                if op == ".+":
                    b_, i_ = a[3] * 64 + a[2] + c[3] + c[2], 0
                elif op == "+":
                    b_, i_ = a[2] + c[2], a[3] + c[3]
                elif op == "-":
                    b_, i_ = a[2] - c[2], a[3] - c[3]
                elif op == "*":
                    if c[2] == 0:
                        b_, i_ = a[2] * c[3], a[3] * c[3]
                    elif a[2] == 0:
                        b_, i_ = c[2] * a[3], c[3] * a[3]
                    else:
                        b_, i_ = (a[2] + a[3]) * (c[2] + c[3]), 0
                else:
                    d = (c[2] + c[3]) or 1
                    if c[2]:
                        b_, i_ = 0, _trunc(a[2] + a[3], d)
                    else:
                        b_, i_ = _trunc(a[2], d), _trunc(a[3], d)
                a[1], a[2], a[3], a[4] = c[1], b_, i_, a[4] and c[4]
                segs.remove(c)
        p += 1
        if segs:
            v.B, v.I = segs[0][2], segs[0][3]
            v.avail = v.avail and all(s[4] for s in segs)
        v.next = p
        return p


def _trunc(a, b):
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q
