"""bits.py -- bit-addressed storage, numbered as the 7030 numbers it.

Bit 0 is the leftmost bit of word 0, as in C22-6729's figures.  Units, vles and
coded expressions live in one of these, so a field is at a bit address and not
in a Python attribute.
"""


class BitMem:
    def __init__(self):
        self.words = {}

    def get(self, addr, n):
        """The n bits at bit address addr, unsigned."""
        out, left = 0, n
        while left > 0:
            w, b = addr >> 6, addr & 63
            take = min(left, 64 - b)
            out = (out << take) | ((self.words.get(w, 0) >> (64 - b - take))
                                   & ((1 << take) - 1))
            addr, left = addr + take, left - take
        return out

    def get_signed(self, addr, n):
        """A sign-and-magnitude field, sign first, as Fig. 22's 25-bit counters."""
        v = self.get(addr, n)
        mag = v & ((1 << (n - 1)) - 1)
        return -mag if v >> (n - 1) else mag

    def put(self, addr, n, value):
        value &= (1 << n) - 1
        left = n
        while left > 0:
            w, b = addr >> 6, addr & 63
            take = min(left, 64 - b)
            piece = (value >> (left - take)) & ((1 << take) - 1)
            shift = 64 - b - take
            old = self.words.get(w, 0)
            self.words[w] = (old & ~(((1 << take) - 1) << shift)) | (piece << shift)
            addr, left = addr + take, left - take

    def put_signed(self, addr, n, value):
        mag = abs(value) & ((1 << (n - 1)) - 1)
        self.put(addr, n, mag | ((1 << (n - 1)) if value < 0 else 0))

    def put_str(self, addr, s):
        """Store a string of '0' and '1'.  Returns the bit after it."""
        i = 0
        while i < len(s):
            piece = s[i:i + 64]
            self.put(addr + i, len(piece), int(piece, 2))
            i += 64
        return addr + len(s)

    def get_str(self, addr, n):
        return format(self.get(addr, n), "0%db" % n) if n else ""


def field(value, width):
    """value as a string of width bits, two's complement if negative."""
    return format(value & ((1 << width) - 1), "0%db" % width)
