"""unit.py -- the expanded instruction unit, C22-6729 Fig. 20 p.189, Fig. 17 p.184.

A control word and seven fixed words, then coded expressions, then the print
image.  Offsets are in bits from the unit's control word.  The positions are
Fig. 20's, as measured in docs/strap2/formats.md section 3.2.
"""
FIXED_BITS = 8 * 64

# control word, Fig. 15 p.90
CW_NEXT = (0, 18)
CW_A = (25, 1)
CW_B = (26, 1)
CW_COUNT = (28, 18)
CW_REFILL = (46, 18)

_W1, _W2, _W3, _W4, _W5, _W6, _W7 = (64 * n for n in range(1, 8))
ZIADAB = (_W1, 25)
ZILBO = (_W1 + 25, 7)
ZIADSY = (_W1 + 32, 25)
ZIFNME = (_W1 + 57, 1)
ZIFP2 = (_W1 + 58, 1)
ZIFBO = (_W1 + 59, 1)
ZIFDD = (_W1 + 60, 1)
ZILCFD = (_W2, 25)
ZIFDDS = (_W2 + 25, 1)
ZIFPMN = (_W2 + 26, 1)
ZIFFLF = (_W2 + 27, 1)
ZIFSFL = (_W2 + 28, 1)
ZIFBSF = (_W2 + 29, 1)
ZIFSBS = (_W2 + 30, 1)
ZIFDSF = (_W2 + 31, 1)
ZILSST = (_W2 + 32, 25)
ZINXBO = (_W2 + 57, 7)
ZILPMS = (_W3, 25)
ZIFALL = (_W3 + 25, 1)
ZINAME = (_W3 + 28, 4)
ZINFLD = (_W3 + 32, 18)
ZIDDS = (_W3 + 50, 13)
ZICDID = (_W4, 64)
ZIOPX = (_W5, 25)
ZIFLAGS = (_W5 + 25, 5)
ZISUPP = (_W5 + 30, 1)
# CHOSEN: bits of the ZIOPX word that Fig. 20 draws zero, for what Pass 2's
# text keeps in indicators: the second of two EXT units (FB/11) and an alignment
# gap's NOP filling (AB in strap_asm's gap rule).
ZIEXT2 = (_W5 + 31, 1)
ZIOTPT = (_W6, 64)
ZICOMM = (_W7, 64)

# Uses of ZIOTPT's fields for a DD or DR (formats.md 3.4).
DD_LEN = (_W6, 25)
DD_NUMERIC = (_W6 + 25, 1)
DD_CC = (_W6 + 26, 1)
DD_LOC = (_W6 + 32, 25)


class Units:
    """The intermediate file: INTOUT writes it, INTIN reads it (pp.89-91, 141)."""

    def __init__(self, mem):
        self.mem = mem
        self.first = 64
        self.ibuffw = self.first
        self.units = 0

    def get(self, unit, f):
        return self.mem.get(unit + f[0], f[1])

    def put(self, unit, f, v):
        self.mem.put(unit + f[0], f[1], v)

    def intout(self, unit, end):
        """Box 1: the word count, and the next control word (p.90)."""
        end = (end + 63) // 64 * 64
        words = (end - unit) // 64
        self.put(unit, CW_COUNT, words)
        self.put(unit, CW_REFILL, end // 64)
        self.put(unit, CW_NEXT, unit // 64 + 1)
        self.units += 1
        self.ibuffw = end

    def intin(self):
        """Every unit in order; generators since a pass walks them twice."""
        at, n = self.first, 0
        while n < self.units:
            yield at
            at = self.get(at, CW_REFILL) * 64
            n += 1
