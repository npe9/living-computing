"""symtab.py -- the dictionary and vle table, C22-6729 pp.13, 43-53, 190-191.

Vle: delete bit, 13-bit total length, 6-bit A6 ID, 12-bit length of the rest of
the name, the rest of the name, the function.

CHOSEN, README gap 1: the guide names Zst bits (p.202 calls ZST... "relative
locations in the function") and tabulates none.  So Zst<n> is simply bit n of
the function, which gives every printed name a place, and the fields it needs
beyond the printed names follow them.  The function table below is the single
statement of the layout.

The dictionary is a TABMAN table (tabman.py, pp.40-53), step 3c of
docs/strap2_7030.md: Fig. 21 p.190's entry, AL 64 ("First Eight Characters
of the Name") and ADDL 25 ("Signed Address of its vle"), the vle bit always 1
(p.13: "each entry in the dictionary portion must have a corresponding vle
portion"), so every symbol's function is in its vle and a name over eight
characters keeps the rest there (p.44's third form).
  The argument: the name's A8 characters.  CHOSEN: a name under eight
  characters is filled with zero bits to 64, as Fig. 21 draws the special
  symbol's argument ("2^8-1, n, 0"); a bare length would let a name match a
  longer one it begins (measured: 278 references in 179 decks).  A8 has no
  character 0 (its codes are 1-60), so the fill cannot be read as one.  A
  character with no A8 code is refused, never mapped to 0.
  A special symbol (p.13, Fig. 21): 2^8-1, a 16-bit n, the fill; entered by
  ADDUNO, "inserted unordered into the symbol table", because it is
  "necessarily the currently last symbol" (p.13): 0xFF is above every A8
  code and n ascends.  ADDUNO marks the table unordered (p.49), so SEARCH is
  linear from then on, and an ADDORD after it would append unsorted: it is
  refused here.  CHOSEN: Fig. 22 draws its vle with ID Y, where TABMAN
  stamps the table's ID (S); STRAP II rewrites the ID after ADDUNO.
  Placement, CHOSEN: the vle table builds up from bit 64 as before; the
  universal block, the control block and the dictionary sit at 2^23, and
  the vle table may not reach them.
  Coded expressions live in vles, so the vle table walks by its length
  fields from Auvbot to Auvtab (step 3c-iii, 2026-11-15).  p.13 (read in
  the ink): the vle "contains ... information about the symbol such as its
  data description, and its value or the coded expression of the value of
  the symbol", and a special symbol's coded expression "built up in the
  vle"; Fig. 22 gives the function as "231 minimum".  So a symbol's
  coded expressions (value, symbolic f.l. and b.s.) follow its fixed
  function fields, in its own vle (extend), and ZEXPR, ZFLX and ZBSX point
  inside it.  CHOSEN: the vle grows while its card block is processed,
  which needs it to be the last vle; anything else is refused.  Dimension
  fields are a D vle of their own (p.13: "any dimension entry made in
  addition to its corresponding regular symbol table entry for a name on
  a DR, DRZ, or SYN"; Fig. 22's "evaluated dimension entry": 5 bits, an
  evaluation indicator, the products).  CHOSEN: before evaluation the
  5 bits hold the number of dimensions, the indicator is 0, and the
  dimension fields' coded expressions follow from bit 32.
  The host still keeps st.vles (ANEXT's order) and name_of (RSERCH's
  answer) beside the table.
"""
from .a8 import A8
from .bits import BitMem
from .tabman import Tabman, TabmanError

S, Y, D = "S", "Y", "D"
A6_ID = {"S": 0o22, "Y": 0o30, "T": 0o23, "D": 0o64, "H": 0o70}

# name: (bit offset in the function, width)
FUNCTION = {
    "ZST0": (0, 1), "ZST1": (1, 1), "ZST3": (3, 1), "ZST4": (4, 1),
    "ZST10": (10, 1), "ZST11": (11, 1), "ZST12": (12, 1), "ZST14": (14, 1),
    "ZST15": (15, 1), "ZST17": (17, 1), "ZST22": (22, 1), "ZST23": (23, 1),
    "ZST24": (24, 1), "ZST26": (26, 1), "ZST32": (32, 1), "ZST35": (35, 1),
    "ZST36": (36, 1), "ZST37": (37, 1),
    "ZKIND": (41, 2),           # 0 label, 1 SYN, 2 undefined, 3 special
    "ZDDS": (43, 13),           # as ZIDDS
    "ZSTCNT": (56, 4),          # the name's check digit, p.173
    "ZSTCOM": (60, 1), "ZSTCON": (61, 18),
    "ZVALB": (79, 25), "ZVALI": (104, 25),   # VALUE's Sinb, Sini
    "ZX": (129, 4), "ZXQ": (133, 1),         # index
    "ZABS": (134, 25), "ZSYM": (159, 25),    # the two location counters
    "ZCTR": (184, 1),           # the counters above are set
    "ZROUND": (185, 2),         # special symbol: 1 half, 2 full word
    "ZLBO": (187, 7),
    "ZEXPR": (194, 25),         # value's coded expression
    "ZFLX": (219, 25),          # symbolic f.l. coded expression
    "ZBSX": (244, 25),          # symbolic b.s. coded expression
    "ZDIMX": (269, 25),         # dimension fields: their number at ZDIMN
    "ZDIMN": (294, 5),
    "ZFLM": (299, 25),          # special symbol: multiplier of the dimensions
    # The guide names no bit for "contagiously defined" (p.25, p.32), so it
    # takes the unnamed bit 5.  ZOLDF: MULTI's legal case, the vle it replaced,
    # whose index still holds (p.127, chart RE boxes 20-22).
    "ZSTCTG": (5, 1),
    "ZOLDF": (324, 25),
}
FUNCTION_BITS = 349
KIND_LABEL, KIND_SYN, KIND_UNDEF, KIND_SPECIAL = 0, 1, 2, 3
SIGNED = {"ZVALB", "ZVALI", "ZABS"}


DICT_AL, DICT_ADDL = 64, 25
UCB = 1 << 23
CB = UCB + 256
DICT_FW = CB + 512


class SymbolError(Exception):
    pass


def argument(name):
    """(arg, al) for SEARCH/ADDORD: the A8 characters, filled to 64."""
    v = 0
    for c in name:
        if c not in A8:
            raise SymbolError(f"a name with a character that has no A8 code: {name!r}")
        v = (v << 8) | A8[c]
    al = 8 * len(name)
    if al < DICT_AL:
        v <<= DICT_AL - al
        al = DICT_AL
    return v, al


_CHAR = {code: c for c, code in A8.items()}


class _Dictionary:
    """The name -> function view the callers use, answered by TABMAN."""
    def __init__(self, st):
        self.st = st

    def get(self, name, default=None):
        f = self.st.search(name)
        return default if f is None else f

    def __getitem__(self, name):
        f = self.st.search(name)
        if f is None:
            raise KeyError(name)
        return f

    def __contains__(self, name):
        return self.st.search(name) is not None

    def items(self):
        """Every undeleted entry, in the table's own order."""
        st, t = self.st, self.st.t
        out = []
        for e in t.entries(CB):
            if t.deleted(e):
                continue
            out.append((st.name_at(e), t.function_address(CB, e)))
        return out

    def __iter__(self):
        return iter([n for n, _ in self.items()])

    def __len__(self):
        return len(self.items())


class SymbolTable:
    def __init__(self):
        self.mem = BitMem()
        self.t = Tabman(self.mem, UCB)
        self.t.define_universal(64)     # bit 0 is never a function address
        self.t.define(CB, DICT_FW, A6_ID[S], DICT_AL, DICT_ADDL)
        self.dictionary = _Dictionary(self)
        self.first_vle = 64
        self.count_y = 0
        self.vles = []          # every function, in the order ANEXT meets them
        self.name_of = {}       # function -> name, RSERCH's answer

    @property
    def next(self):
        return self.t.auvtab

    def _check_room(self):
        if self.t.auvtab > UCB:
            raise SymbolError("the vle table has reached the symbol dictionary")

    def name_at(self, e):
        """The name an entry holds: its eight characters, fill dropped, then
        its rest."""
        t = self.t
        a = t.argument(CB, e, DICT_AL)
        codes = [(a >> (56 - 8 * i)) & 255 for i in range(8)]
        if codes[0] == 255:
            return "\xff" + chr(codes[1]) + chr(codes[2])
        while codes and codes[-1] == 0:
            codes.pop()
        rest = t.rest(CB, e)
        codes += [int(rest[i:i + 8], 2) for i in range(0, len(rest), 8)]
        return "".join(_CHAR[c] for c in codes)

    def _made(self, f, name, kind, v):
        self._check_room()
        self._last = (v, f)
        self.vles.append(f)
        self.name_of[f] = name
        self.put(f, "ZKIND", kind)
        return f

    def _fx(self):
        return self.mem.get(CB, 24)

    def search(self, name):
        arg, al = argument(name)
        if self.t.search(CB, arg, al) == "found":
            return self._fx()
        return None

    def addord(self, name, kind=KIND_LABEL):
        """ADDORD: enter a new symbol.  Returns (function, already_there)."""
        if self.t.get(CB, "TO"):
            raise SymbolError("ADDORD on the symbol table after ADDUNO marked it "
                              "unordered (p.49)")
        arg, al = argument(name)
        v = self.t.auvtab
        got = self.t.addord(CB, arg, al, 0, FUNCTION_BITS)
        if got == "already there":
            return self._fx(), True
        return self._made(self._fx(), name, kind, v), False

    def _vle(self, name):
        """A vle with no new dictionary entry: the name's rest, then the
        function (MULTI's two cases).  Returns the function address."""
        arg, al = argument(name)
        rest = al - DICT_AL
        v = self.t.new_vle(A6_ID[S], rest, arg & ((1 << rest) - 1), 0, FUNCTION_BITS)
        return v, v + 32 + rest

    def replace(self, name, kind):
        """MULTI's legal case: a new vle, and the dictionary repointed (p.127)."""
        arg, al = argument(name)
        if self.t.search(CB, arg, al) != "found":
            raise SymbolError(f"MULTI's legal case for a name not in the table: {name!r}")
        e = self.mem.get(CB + 64, 24)                       # DX
        v, f = self._vle(name)
        self.mem.put_signed(e + 2 + DICT_AL, DICT_ADDL, v)
        return self._made(f, name, kind, v)

    def orphan(self, name, kind):
        """MULTI's contradictory case: a basic vle, dictionary unchanged (p.127,
        chart RE boxes 2-3)."""
        v, f = self._vle(name)
        return self._made(f, name, kind, v)

    def special(self):
        """A new special symbol, ADDUNO, unordered (p.13, Fig. 21).

        Fig. 21's n: "How n is chosen ... UNSPECIFIED"; CHOSEN, it counts from
        1 (Fig. 21: "n = 0 for the $ itself").
        """
        self.count_y += 1
        if self.count_y >= 1 << 16:
            raise SymbolError("more special symbols than Fig. 21's 16-bit n")
        name = "\xff" + chr(self.count_y >> 8) + chr(self.count_y & 255)
        v = self.t.auvtab
        self.t.adduno(CB, ((0xFF << 16) | self.count_y) << 40, DICT_AL, 0, FUNCTION_BITS)
        f = self._fx()
        self.mem.put(v + 14, 6, A6_ID[Y])                   # Fig. 22: Y
        return self._made(f, name, KIND_SPECIAL, v)

    def extend(self, f, bits):
        """A coded expression appended to the function of the vle just made
        (the header).  Returns its address."""
        v, last = getattr(self, "_last", (None, None))
        if last != f or v + self.mem.get(v + 1, 13) != self.t.auvtab:
            raise SymbolError("a coded expression for a vle that is not the last one")
        total = self.mem.get(v + 1, 13) + len(bits)
        if total >= 1 << 13:
            raise SymbolError(f"a vle of {total} bits: Fig. 22's length field has 13")
        at = self.t.auvtab
        self.mem.put_str(at, bits)
        self.mem.put(v + 1, 13, total)
        self.t.auvtab = at + len(bits)
        self._check_room()
        return at

    def dimension(self, bits, n):
        """A D vle holding n dimension fields' coded expressions (the header).
        Returns the address of the first."""
        v = self.t.new_vle(A6_ID[D], 0, 0, int(bits, 2) if bits else 0, len(bits))
        self.mem.put(v + 20, 5, n)
        self.mem.put(v + 25, 1, 0)                          # not yet evaluated
        self._check_room()
        return v + 32

    def walk(self):
        """The vle table by its length fields, Auvbot to Auvtab, as ANEXT
        steps: [(address, ID)].  Refuses a table that does not walk."""
        out, p = [], self.t.auvbot
        while p < self.t.auvtab:
            length = self.mem.get(p + 1, 13)
            if length < 32:
                raise SymbolError(f"the vle table does not walk: length {length} at {p}")
            out.append((p, self.mem.get(p + 14, 6)))
            p += length
        if p != self.t.auvtab:
            raise SymbolError("the vle table walks past Auvtab")
        return out

    def get(self, f, name):
        off, w = FUNCTION[name]
        if name in SIGNED:
            return self.mem.get_signed(f + off, w)
        return self.mem.get(f + off, w)

    def put(self, f, name, value):
        off, w = FUNCTION[name]
        if name in SIGNED:
            self.mem.put_signed(f + off, w, value)
        else:
            self.mem.put(f + off, w, value)

    def sorted_names(self):
        return sorted(n for n, _ in self.dictionary.items() if not n.startswith("\xff"))
