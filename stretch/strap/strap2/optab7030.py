"""optab7030.py -- the 7030 STRAP II's operation tables, generated from the
host's (optable.py), and read back.

>>> A RECONSTRUCTION.  The guide prints the FORMATS (C22-6729 Figs. 23 and
>>> 24, printed p.192, and p.22's op index, all read in the ink 2026-11-15)
>>> and no contents.  What is CHOSEN here is marked so. <<<

THE TABLE OF PRIMARY OPERATIONS (Fig. 23), one two-word entry per mnemonic,
sorted on word one for BOPSER (p.67: ordered, a 64-bit test word):
  word 1   the mnemonic, eight A8 characters, blank-filled (p.22: "eight
           characters are collected")
  word 2   non-ambiguous op: its skeleton, with the op index's location in
           the leading bits; ambiguous op: bits 0-31 the floating skeleton,
           bits 32-63 the last half of the VFL skeleton (p.22: "the skeleton
           bit pattern of the normalized version of the instruction, the
           last half of the bit pattern of the variable field length
           version"); pseudo-op: the op index's location, and the
           digit-select pseudo-op number in bits 32-50.
  DERIVED (C10 and C2 of docs/strap2/formats.md): Fig. 23 draws the
  location "in Bits 0-23" INSIDE the skeleton row, and p.22 says "the first
  18 bits".  Over the printed set, bits 0-17 of every skeleton are zero and
  bits 18-23 are used by 168, so the location is an 18-bit word address in
  bits 0-17, ORed into the skeleton word.

THE TABLE OF SECONDARY OPERATIONS (Fig. 24), sorted on word one:
  word 1   00000abc, then the secondary's mnemonic in seven A8 characters
           (p.22: "may not be greater than seven characters")
  word 2   the skeleton bits it adds (CW's three bits 36-38, field P's code
           in bits 32-34, SEOP's bit 52 -- the rule of
           tests/check_strap2_op_reconstruction.py)
  abc: 001 a secondary of a VFL instruction, 100 of CW, and for SEOP the
  figure prints "020", which is not three bits: CHOSEN 010
  (formats.md C4).

THE OP INDEX (p.22: "a string of bits which represent yes/no answers to the
questions about the op ... The first 24 bits in the actual string contains
the address of the first control word in the chain of control words which
are used in Pass 2 to insert the address fields ... The op index for a
binary producing instruction which can have a secondary op also contains the
code number for the secondary op").  CHOSEN: one 64-bit word per distinct
set of answers, shared by every mnemonic that gives them:
   0-23  the fill chain's first control word (0: none), a word address
         in bits 0-17
  24-26  abc, the secondary code (as Fig. 24; 000 takes none)
  27-33  the fixed I-O function code (CTL's function ops; 0 none)
  34     Zoddsa  a dds is needed (p.140 Box 2)
  35     Zoimm   an immediate VFL op (p.22)
  36     Zopo    a pseudo-op (p.140 Box 9)
  37     ZOMCP   an MCP-type op (p.97: "a special bit in its op index")
  38     ZOAMB   ambiguous (Fig. 23's second format)
  39     ZOCONN  a connective
  40     ZOFPU   a floating op whose no-dds default is unnormalized (E, E+I;
                 p.140 Box 5 rule 4)
  41     ZOCODE  an I-O op whose address is a code field (CTL, LOC)
  42     ZOREL   REL
  43     ZOREEL  REEL (chart p.147)
  44-46  the kind: 0 instr, 1 fp, 2 vfl, 3 conn, 4 io, 5 data, 6 pseudo
  47-53  the binary's length in bits (0-64)
  54-60  its alignment in bits (0-64)
  61-63  zero
The names Zoddsa, Zoimm, Zopo and ZOREEL are the guide's (p.202 says only
that ZO... are relative locations); the bit positions are CHOSEN, as are
the other names.

THE FILL CHAIN.  CHOSEN: one chain per distinct fill list, a control word
per fill routine: CW(CCR) to chain to the next, CW(CR) for the last, with
the routine in the address field and the count in the count field.  The
routines are p.144's INSERT routines (S1918A, STTI, SSIC24, S24CW, STT19A
are its examples; the host's names otherwise), which the 7030 deck does not
have yet: until Pass 2's INSERT exists, each routine's "address" is its
number in FILL_ROUTINES (PROVISIONAL).

THE DIGIT-SELECT PSEUDO-OP NUMBER.  p.22: "This number will be used in three
different phases of the assembly in determining the treatment of an
individual pseudo-op".  The numbering is UNSPECIFIED; PROVISIONAL: the
pseudo-op's 1-based place in the sorted table, until step 4's pseudo-ops
say what the three digits select.
"""
from . import optable as T
from .a8 import a8

KINDS = ["instr", "fp", "vfl", "conn", "io", "data", "pseudo"]
FLAGS = [  # (bit, name, how it is read off an OpEntry)
    (34, "Zoddsa", lambda e: e.dds_needed),
    (35, "Zoimm", lambda e: e.immediate),
    (36, "Zopo", lambda e: e.pseudo),
    (37, "ZOMCP", lambda e: e.mcp),
    (38, "ZOAMB", lambda e: e.ambiguous),
    (39, "ZOCONN", lambda e: e.is_conn),
    (40, "ZOFPU", lambda e: getattr(e, "fp_default_u", False)),
    (41, "ZOCODE", lambda e: getattr(e, "code_field", False)),
    (42, "ZOREL", lambda e: getattr(e, "rel", False)),
    (43, "ZOREEL", lambda e: e.name == "REEL"),
]
ABC = {"VFL": 0b001, "SEOP": 0b010, "CW": 0b100}
LOC_SHIFT = 46                  # an 18-bit word address in bits 0-17
BEGIN = "! >>> OPTAB: generated, do not edit (strap/strap2/optab7030.py) <<<"
END = "! <<< OPTAB end >>>"
ORIGIN = 0o100000


def pairs_of(n):
    """Fig. 11's pair space, N = 18 - LZC (strap2/bopser.py's CHOSEN N)."""
    return n.bit_length()




def field(word, first, width):
    return (word >> (64 - first - width)) & ((1 << width) - 1)


def put(first, width, value):
    assert 0 <= value < (1 << width), (first, width, value)
    return value << (64 - first - width)


def name_word(text, code=None):
    """Eight A8 characters, blank-filled; or a code byte and seven."""
    if code is None:
        chars = text.ljust(8)
        assert len(chars) == 8, text
        w = 0
    else:
        chars = text.ljust(7)
        assert len(chars) == 7, text
        w = code
    for c in chars:
        w = (w << 8) | a8(c)
    return w


def secondary_code(name):
    """The abc a mnemonic's op index carries: which secondary family it takes
    (strap_asm.secondary_error, C22-6729 p.22)."""
    a = T._a
    if a.secondary_error(name, ["CCR"]) is None:
        return ABC["CW"]
    if a.secondary_error(name, ["SEOP"]) is None:
        return ABC["SEOP"]
    if a.secondary_error(name, ["BU", "V+I"]) is None and T.lookup(name, "BU", ("V+I",)):
        return ABC["VFL"]
    return 0


def question_bits(e):
    w = 0
    for bit, _, f in FLAGS:
        if f(e):
            w |= put(bit, 1, 1)
    w |= put(44, 3, KINDS.index(e.kind))
    w |= put(47, 7, e.length)
    w |= put(54, 7, e.align)
    w |= put(27, 7, getattr(e, "fixed_code", None) or 0)
    return w


def secondaries():
    """Fig. 24's entries: (word 1, word 2, name), sorted."""
    a = T._a
    out = []
    for s, p in a.PROGRESSIVE_SECONDARY_OP.items():
        out.append((name_word(s, ABC["VFL"]), p << 29, s))
    out.append((name_word("SEOP", ABC["SEOP"]), 0x800, "SEOP"))
    for s, (c, m, k) in a.CW_SECONDARY.items():
        out.append((name_word(s, ABC["CW"]), ((4 * c + 2 * m + k) << 36), s))
    return sorted(out)


class Tables:
    """The generated tables, laid out from word address `base`."""

    def __init__(self, names):
        self.entries = {}
        for n in sorted(set(names)):
            e = T.lookup(n)
            assert e is not None, n
            self.entries[n] = e
        self.routines = sorted({f for e in self.entries.values() for f, _ in e.fills})
        chains = sorted({tuple(e.fills) for e in self.entries.values() if e.fills})
        self.chains = chains
        idx = set()
        for n, e in self.entries.items():
            idx.add(self._index_key(n, e))
        self.indexes = sorted(idx)
        pseudo = [n for n in sorted(self.entries) if self.entries[n].pseudo]
        self.pseudo_number = {n: i + 1 for i, n in enumerate(pseudo)}
        self.order = sorted(self.entries, key=name_word)

    def _index_key(self, n, e):
        return (question_bits(e), secondary_code(n), tuple(e.fills))

    def layout(self, origin=ORIGIN):
        """Word addresses, from the fixed origin: OPKEY, OPCB and its pairs,
        OPTAB; SECKEY, SECCB and its pairs, SECTAB; OPIDX; OPFILL."""
        self.origin = origin
        n_p, n_s = len(self.order), len(secondaries())
        self.opkey, self.opcb = origin, origin + 1
        self.prim = self.opcb + 1 + pairs_of(n_p)
        self.seckey = self.prim + 2 * n_p
        self.seccb = self.seckey + 1
        self.sec = self.seccb + 1 + pairs_of(n_s)
        self.idx = self.sec + 2 * n_s
        self.chain_at = {}
        a = self.idx + len(self.indexes)
        for c in self.chains:
            self.chain_at[c] = a
            a += len(c)
        self.end = a
        return self

    def index_word(self, key):
        qb, abc, fills = key
        w = qb | put(24, 3, abc)
        if fills:
            w |= self.chain_at[fills] << LOC_SHIFT
        return w

    def primary_word2(self, n):
        e = self.entries[n]
        loc = (self.idx + self.indexes.index(self._index_key(n, e))) << LOC_SHIFT
        if e.pseudo:
            return loc | put(32, 19, self.pseudo_number[n])
        if e.ambiguous:
            fp = T.lookup(n, "N")
            sk = (fp.skeleton & (0xFFFFFFFF << 32)) | (e.skeleton & 0xFFFFFFFF)
        else:
            sk = e.skeleton
        assert sk & (((1 << 18) - 1) << LOC_SHIFT) == 0, n
        return sk | loc

    def fill_word(self, chain, i):
        r, count = chain[i]
        w = put(0, 18, self.routines.index(r)) | put(28, 18, count)
        if i + 1 < len(chain):
            w |= put(25, 1, 1)                  # chain: CW(CCR)
        return w

    def deck_text(self):
        """The block for decks/strap2_7030.strap, between its markers."""
        L = [BEGIN,
             "! The 7030 STRAP II's operation tables (C22-6729 Figs. 23, 24 p.192;",
             "! p.22's op index; Fig. 11 p.67's control blocks), GENERATED by",
             "! strap/strap2/optab7030.py from the host's optable.py.  Do not edit:",
             "! regenerate (tools/gen_strap2_optab.py).  The layout and every",
             "! CHOSEN or PROVISIONAL field are in optab7030.py's docstring.",
             "! Fixed origin, so nothing earlier in the deck moves the addresses.",
             f"        SLC, (8){self.origin:o}.0",
             "OPKEY   DD(BU,64), 0",
             f"OPCB    XW, OPKEY, 128, {len(self.order)}",
             f"        DRZ(BU,64), {pairs_of(len(self.order))}",
             "OPTAB   SYN, $"]
        for n in self.order:
            L.append(f"        DD(BU,64), (16){name_word(n):016X}   ! {n}")
            L.append(f"        DD(BU,64), (16){self.primary_word2(n):016X}")
        L += ["SECKEY  DD(BU,64), 0",
              f"SECCB   XW, SECKEY, 128, {len(secondaries())}",
              f"        DRZ(BU,64), {pairs_of(len(secondaries()))}",
              "SECTAB  SYN, $"]
        for w1, w2, nm in secondaries():
            L.append(f"        DD(BU,64), (16){w1:016X}   ! {nm}")
            L.append(f"        DD(BU,64), (16){w2:016X}")
        L.append("OPIDX   SYN, $")
        for k in self.indexes:
            L.append(f"        DD(BU,64), (16){self.index_word(k):016X}")
        L.append("OPFILL  SYN, $")
        for c in self.chains:
            for i in range(len(c)):
                L.append(f"        DD(BU,64), (16){self.fill_word(c, i):016X}   ! {c[i][0]},{c[i][1]}")
        L.append(END)
        return "\n".join(L) + "\n"


def decode(word_at, prim, count, routines):
    """Read the 7030 primary table back: {name: attributes} as the host's
    OpEntry would give them.  word_at(address) -> 64-bit word."""
    out = {}
    for i in range(count):
        w1, w2 = word_at(prim + 2 * i), word_at(prim + 2 * i + 1)
        name = "".join(_A8_CHAR.get((w1 >> (56 - 8 * k)) & 0xFF, "?")
                       for k in range(8)).rstrip()
        ix = word_at(field(w2, 0, 18))
        d = {"kind": KINDS[field(ix, 44, 3)], "length": field(ix, 47, 7),
             "align": field(ix, 54, 7), "fixed_code": field(ix, 27, 7) or None,
             "abc": field(ix, 24, 3)}
        for bit, nm, _ in FLAGS:
            d[nm] = bool(field(ix, bit, 1))
        if d["Zopo"]:
            d["pseudo_number"] = field(w2, 32, 19)
        else:
            d["skeleton"] = w2 & ~(((1 << 18) - 1) << LOC_SHIFT)
        fills = []
        a = field(ix, 0, 18)
        while a:
            cw = word_at(a)
            fills.append((routines[field(cw, 0, 18)], field(cw, 28, 18)))
            a = a + 1 if field(cw, 25, 1) else 0
        d["fills"] = fills
        out[name] = d
    return out


from .a8 import A8 as _A8                       # noqa: E402
_A8_CHAR = {v: k for k, v in _A8.items()}


def attributes(n, e):
    """What decode() should read back for mnemonic n, from the host entry."""
    d = {"kind": e.kind, "length": e.length, "align": e.align,
         "fixed_code": getattr(e, "fixed_code", None) or None,
         "fills": list(e.fills), "abc": secondary_code(n)}
    for bit, nm, f in FLAGS:
        d[nm] = bool(f(e))
    if not e.pseudo:
        sk = e.skeleton
        if e.ambiguous:
            sk = (T.lookup(n, "N").skeleton & (0xFFFFFFFF << 32)) | (e.skeleton & 0xFFFFFFFF)
        d["skeleton"] = sk
    return d
