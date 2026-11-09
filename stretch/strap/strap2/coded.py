"""coded.py -- coded expressions as bit strings, C22-6729 Appendix C pp.197-201.

An expression is built as a tree of Python lists and written with encode().
Figures 28 and 29 are the test (tests/check_strap2_coded.py).
"""
from .a8 import a8_bits
from .bits import field

OP_CODE = {".+": 0b111, ".L": 0b110, ".R": 0b101, "U-": 0b100,
           "*": 0b011, "/": 0b010, "+": 0b001, "-": 0b000}
OP_NAME = {v: k for k, v in OP_CODE.items()}

PREFIX_NORMAL = "1000"
PREFIX_NULL = "1111"


class Expr:
    """A field: data [Datum], ops [(name, number)], and an optional g.p."""

    def __init__(self):
        self.data = []
        self.ops = []
        self.gp = None          # (n, Expr)
        self.null = False


class Datum:
    def __init__(self, kind, value, dds=0):
        self.kind = kind        # 'sym', 'abs', 'sys'
        self.value = value      # symbol text, or a number
        self.dds = dds          # 13 bits for a system symbol
        self.subs = []          # subscripts and index, each an Expr


def encode_body(x):
    """Data list and operator list: everything after the prefix, before the g.p."""
    s = []
    for d in x.data:
        if d.kind == "sym":
            s.append("100" + field(len(d.value), 7) + a8_bits(d.value))
        elif d.kind == "abs":
            s.append("110" + field(d.value, 24))
        elif d.kind == "sys":
            s.append("11100" + field(d.value, 24) + field(d.dds, 13))
        else:
            raise ValueError(d.kind)
        for sub in d.subs:
            # p.199 note 2: the 1 of 2E is the 1A of the inner expression; and
            # a subscript's expression has no 4A (formats.md 5.4, DERIVED).
            s.append(PREFIX_NORMAL + encode_body(sub))
        s.append("0")           # end of datum
    s.append("0")               # end of data
    for name, number in x.ops:
        s.append("1" + field(OP_CODE[name], 3) + field(number, 5))
    s.append("0")               # no more operators
    return "".join(s)


def encode(x):
    """A whole field, with its g.p. chain or the final 0 (p.85 Boxes 37, 46)."""
    if x.null:
        s = PREFIX_NULL + "0"
    else:
        s = PREFIX_NORMAL + encode_body(x)
    if x.gp is None:
        return s + "0"
    n, inner = x.gp
    return s + "1" + field(n, 6) + encode(inner)
