"""symtab.py -- the dictionary and vle table, C22-6729 pp.13, 43-53, 190-191.

Vle: delete bit, 13-bit total length, 6-bit A6 ID, 12-bit length of the rest of
the name, the rest of the name, the function.

CHOSEN, README gap 1: the guide names Zst bits (p.202 calls ZST... "relative
locations in the function") and tabulates none.  So Zst<n> is simply bit n of
the function, which gives every printed name a place, and the fields it needs
beyond the printed names follow them.  The function table below is the single
statement of the layout.

CHOSEN: on the host the dictionary is a Python map, with SEARCH's ordering kept
in sorted_names().  ADDORD's table move and BOPSER's probe are machine detail
for the 7030 version.
"""
from .a8 import a8_bits
from .bits import BitMem

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


class SymbolTable:
    def __init__(self):
        self.mem = BitMem()
        self.next = 64          # bit 0 is never a function address
        self.dictionary = {}    # argument -> function address
        self.first_vle = self.next
        self.count_y = 0
        self.vles = []          # every function, in the order ANEXT meets them
        self.name_of = {}       # function -> name, RSERCH's answer

    def _vle(self, ident, name, room=0):
        """ADDUNO's allocation, header included.  Returns the function address."""
        at = self.next
        rest = name[8:]
        total = 1 + 13 + 6 + 12 + 8 * len(rest) + FUNCTION_BITS + room
        m = self.mem
        m.put(at, 1, 0)
        m.put(at + 1, 13, total % (1 << 13))
        m.put(at + 14, 6, A6_ID[ident])
        m.put(at + 20, 12, len(rest))
        if rest:
            m.put_str(at + 32, a8_bits(rest))
        self.next = at + total
        f = at + 32 + 8 * len(rest)
        self.vles.append(f)
        self.name_of[f] = name
        return f

    def search(self, name):
        return self.dictionary.get(name)

    def addord(self, name, kind=KIND_LABEL):
        """ADDORD: enter a new symbol.  Returns (function, already_there)."""
        f = self.dictionary.get(name)
        if f is not None:
            return f, True
        f = self._vle(S, name)
        self.dictionary[name] = f
        self.put(f, "ZKIND", kind)
        return f, False

    def replace(self, name, kind):
        """MULTI's legal case: a new vle, and the dictionary repointed (p.127)."""
        f = self._vle(S, name)
        self.dictionary[name] = f
        self.put(f, "ZKIND", kind)
        return f

    def orphan(self, name, kind):
        """MULTI's contradictory case: a basic vle, dictionary unchanged (p.127,
        chart RE boxes 2-3)."""
        f = self._vle(S, name)
        self.put(f, "ZKIND", kind)
        return f

    def special(self):
        """A new special symbol, ADDUNO, unordered (p.13).

        Fig. 21's n: "How n is chosen ... UNSPECIFIED"; CHOSEN, it counts.
        """
        self.count_y += 1
        name = "\xff" + chr(self.count_y >> 8) + chr(self.count_y & 255)
        f = self._vle(Y, "")
        self.dictionary[name] = f
        self.put(f, "ZKIND", KIND_SPECIAL)
        return f

    def store_coded(self, s):
        """A coded expression placed further out in the vle table."""
        at = self.next
        self.mem.put_str(at, s)
        self.next = at + len(s)
        return at

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
        return sorted(n for n in self.dictionary if not n.startswith("\xff"))
