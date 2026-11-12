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

# The five symbol error flags, Fig. 20's ZIOPX bits 25-29 (p.25), named as
# C28-6129 pp.20-21 prints them.  CHOSEN: their order in the five bits, which
# is the manual's order, UNDEF in bit 25 (pass2.md contradiction 16).
FLAG_NAMES = ("UNDEF", "QUEST", "MULTI", "PSEUDO", "CONTAG")
F_UNDEF, F_QUEST, F_MULTI, F_PSEUDO, F_CONTAG = 16, 8, 4, 2, 1


def flag_names(bits):
    return [n for k, n in enumerate(FLAG_NAMES) if bits & (16 >> k)]


def _chars():
    from .a8 import A8
    return {v: k for k, v in A8.items()}


class V:
    __slots__ = ("B", "I", "X", "xq", "avail", "dds", "sym", "gps", "next", "dims", "nullf",
                 "lc", "reg")

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
        # Location-counter-dependent symbols in the expression, counted
        # (bss_loader_spec.md 9): error 123's "more than one location
        # counter symbol" counts them, so they are counted, not netted.
        self.lc = 0
        # The region of the counted symbol (C22-6729 p.185, Zstcom/Zstcon):
        # None the program, 0 blank common, k named common k.
        self.reg = None

    @property
    def total(self):
        return self.B + self.I


class Value:
    """The evaluator.  mem holds the expressions; st is the symbol table."""

    def __init__(self, st, messages):
        self.st = st
        self.msg = messages
        self.vcundf = False     # p.57: may make an undefined entry
        # p.25: VALUE "informs the using program" of the error symbols in an
        # expression.  The caller clears this and reads it after.
        self.flags = 0
        # The flag a reference to a symbol multiply defined with contradictions
        # gives: MULTI in C28-6129 p.21's example (5), CONTAG in N28-1081 p.7.
        self.multi_ref = F_CONTAG
        self.abs = 0            # $4
        self.sym = 0            # $6
        self.have_counters = False
        self.chars = _chars()
        self.count_lc = False   # PUNREL mode turns the count on (pass2)
        self._lc = {}           # f -> location-counter symbols in its value
        self._lc_busy = set()
        self.region = {}        # f -> its region, set by Pass 2a (SLCRCOM)
        self.cur_region = None  # the region $ is in
        self._reg = {}          # f (a SYN) -> the region of what it counts

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
        saved, self.flags = self.flags, 0
        try:
            if kind == KIND_SYN:
                got = self._syn(f)
            else:
                got = self._special(f)
        finally:
            st.put(f, "ZST17", 0)
            inner, self.flags = self.flags, saved
        if got is not None and inner and kind == KIND_SYN:
            # p.32: UITER marks a symbol defined in terms of an error symbol
            # as it completes the entry; C28-6129 p.21 (5).
            st.put(f, "ZSTCTG", 1)
        if st.get(f, "ZST26"):      # circular, zero already given
            return (st.get(f, "ZVALB"), st.get(f, "ZVALI"), st.get(f, "ZX"), st.get(f, "ZXQ"))
        return got

    def symbol_flags(self, f):
        """The flags a reference to the symbol at f raises (p.25, C28 pp.20-21)."""
        st = self.st
        bits = 0
        if st.get(f, "ZKIND") == KIND_UNDEF or st.get(f, "ZST1"):
            bits |= F_UNDEF
        if st.get(f, "ZST22"):
            bits |= F_QUEST
        if st.get(f, "ZST23"):
            bits |= self.multi_ref
        if st.get(f, "ZST4"):
            bits |= F_PSEUDO
        if st.get(f, "ZSTCTG"):
            bits |= F_CONTAG
        return bits

    def symbol_lc(self, f):
        """How many location-counter-dependent symbols the symbol at f stands
        for: a label or a special (location-counter) symbol is one (C22-6729
        p.185, Zst36 "0-if location counter dependent"); a SYN, what its own
        expression counts; an undefined symbol, none.  CHOSEN: the count of a
        circular SYN is zero, as its value is (p.32)."""
        if f in self._lc:
            return self._lc[f]
        st = self.st
        kind = st.get(f, "ZKIND")
        if kind in (KIND_LABEL, KIND_SPECIAL):
            return 1
        if kind != KIND_SYN or f in self._lc_busy:
            return 0
        self._lc_busy.add(f)
        saved = (self.abs, self.sym, self.have_counters, self.flags, self.cur_region)
        self.have_counters = bool(st.get(f, "ZCTR"))
        self.abs, self.sym = st.get(f, "ZABS"), st.get(f, "ZSYM")
        self.cur_region = self.region.get(f)
        try:
            v = self.read_field(st.mem, st.get(f, "ZEXPR"))
            n = v.lc
        finally:
            self.abs, self.sym, self.have_counters, self.flags, self.cur_region = saved
            self._lc_busy.discard(f)
        if v.avail:
            self._lc[f] = n
            self._reg[f] = v.reg
        return n

    def symbol_region(self, f):
        """The region a location-counter-dependent symbol is relative to: a
        label's is where it was defined (after SLCRCOM, a common's); a SYN's,
        that of the symbol it counts."""
        if self.st.get(f, "ZKIND") in (KIND_LABEL, KIND_SPECIAL):
            return self.region.get(f)
        self.symbol_lc(f)
        return self._reg.get(f)

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
        x, xq = v.X, v.xq
        old = st.get(f, "ZOLDF")
        if old:
            # Chart RE boxes 20-22: an index the earlier definition gave holds.
            o = self.symbol_value(old)
            if o is not None and o[3]:
                x, xq = o[2], True
        return self._enter(f, v.B, v.I, x, 1 if xq else 0)

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
                    v.lc += 1
                    v.reg = self.cur_region
                else:
                    f = self.lookup_or_enter(text)
                    got = None if f is None else self.symbol_value(f)
                    if f is not None:
                        self.flags |= self.symbol_flags(f)
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
                        if self.count_lc:
                            k = self.symbol_lc(f)
                            if k:
                                v.lc += k
                                v.reg = self.symbol_region(f)
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
