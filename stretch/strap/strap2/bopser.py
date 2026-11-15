"""bopser.py -- BOPSER, STRAP II's binary search, C22-6729 pp.65-67.

>>> A RECONSTRUCTION to Charts BA and BB (pp.65-66) and p.67's text and
>>> Figure 11, read in the ink 2026-11-15.  It is the specification the 7030
>>> BOPSER (decks/strap2_7030.strap, step 4a) is tested against. <<<

Linkage (p.67): SIC,$15; B,BOPSER; ,address of the control block(I); then
B,fix-up at the not-found exit, the normal return found.  On a find the
function's address is in Llxw's value field.

The control block (Figure 11), at cb:
  0-23 the test word's address; 24, 25, 27 unlabelled; 26 BOPSER's
  indicator (set only by BOPSER: the increment-decrement pairs are made);
  28-45 the bit length of an entry; 46-63 the number of entries; then
  "DRZ(BU), N" for the pairs.
  CHOSEN (the figure gives the space, not its layout): p.67 Box 1 keeps an
  increment list and a decrement list ($7 and $9), so the space holds N
  half words of increments, then N half words of decrements, each a signed
  index value (magnitude in bits 0-23, sign in bit 24).
  CHOSEN: Figure 11 gives no table address, and p.67 Box 1 loads one into
  $8; the table starts at the word after the pair space, cb + 64(1 + N).
  The word before it is the last pair word, whose first byte is 0 for any
  table under 2^16 bits of entries, so it is never an A8 name.

The pairs (Chart BB, LLNEW and LLZERO): from the number of entries, while
pairs remain to be made: an even count is halved and the half made a pair;
an odd count, the first time, is first increased by one (the "1st odd count
indicator") and then halved; an odd count after that is halved, the half
made a pair, and then increased by one.  Each pair is (half x entry length)
as the increment and its negative as the decrement.
  MEASURED: this is Knuth's uniform binary search (TAOCP 6.2.1 Algorithm C):
  the halves are DELTA[j] = floor((n + 2^(j-1)) / 2^j), checked for every n
  below 5000.  The first entry tested is (the table's location - an entry's
  length) + the first increment (p.67 Box 7), Knuth's i = DELTA[1].

N.  p.67's restriction 2 gives N = ceiling(log2(number of entries)).  MEASURED
(every table of 1 to 1,099 entries, every key): with that N, one entry is
never found in each table whose size is a power of two (1, 2, 4, ..., 1024),
because the search makes 18 - LZC compares (Boxes 2-3) and needs that many
halves.  CHOSEN: N = 18 - LZC of the number of entries in 18 bits, which is
ceiling(log2(entries + 1)); it equals p.67's N except at the powers of two.

The search (Chart BA): compare the test word with the entry (Box 8; CHOSEN:
the entry's first 64 bits, unsigned, as a K(BU,64)); equal: found, Llxw the
function's address (Box 16; CHOSEN: the entry + 64, the word after the
argument, as SYSTAB and p.192's op tables lay it out); not equal: count the
compare (Box 10), none left: not found (Box 11); else the next entry is
higher or lower (Box 12) by the next increment or decrement (Boxes 13-15).
As in Knuth's algorithm, a search for an argument the table does not hold
may test the entry one before or one after the table (MEASURED: 549 of the
misses in tables of 1 to 1,099 entries).  The guide says nothing of it: the
word there is compared like any other, so the table's neighbours must not
equal a test word.  The host compares memory as the 7030 does.
"""
from .bits import BitMem


class BopserError(Exception):
    pass


def _cb(field):
    return {"TW": (0, 24), "IND": (26, 1), "EL": (28, 18), "NE": (46, 18)}[field]


def lzc18(n):
    return 18 - n.bit_length()


def table_of(mem, cb):
    """The table's location: the word after the pair space (CHOSEN)."""
    return cb + 64 * (1 + 18 - lzc18(mem.get(cb + 46, 18)))


def define(mem, cb, test_word, entry_bits, entries):
    """A control block.  Returns the table's location."""
    if entry_bits < 64:
        raise BopserError("an entry is at least 64 bits (p.67 restriction 4)")
    mem.put(cb, 64, 0)
    mem.put(cb, 24, test_word)
    mem.put(cb + 28, 18, entry_bits)
    mem.put(cb + 46, 18, entries)
    n = 18 - lzc18(entries)
    for k in range(n):
        mem.put(cb + 64 + 64 * k, 64, 0)
    return table_of(mem, cb)


def pairs(entries):
    """LLNEW: the halves, N = 18 - LZC of them."""
    out, c, first = [], entries, True
    while len(out) < 18 - lzc18(entries):
        if c % 2 == 0:
            c //= 2
            out.append(c)
        elif first:
            first = False
            c = (c + 1) // 2
            out.append(c)
        else:
            c //= 2
            out.append(c)
            c += 1
    return out


def _put_index(mem, at, v):
    mem.put(at, 24, abs(v))
    mem.put(at + 24, 1, 1 if v < 0 else 0)
    mem.put(at + 25, 7, 0)


def _get_index(mem, at):
    v = mem.get(at, 24)
    return -v if mem.get(at + 24, 1) else v


class Result:
    def __init__(self, found, llxw, probes):
        self.found, self.llxw, self.probes = found, llxw, probes


def bopser(mem, cb):
    """One search.  Returns Result(found, Llxw, the entries tested)."""
    table = table_of(mem, cb)
    el = mem.get(cb + 28, 18)
    ne = mem.get(cb + 46, 18)
    if ne == 0:                                     # Box 2: a null table
        return Result(False, None, [])
    n = 18 - lzc18(ne)                              # Box 3
    inc, dec = cb + 64, cb + 64 + 32 * n
    if not mem.get(cb + 26, 1):                     # Boxes 4-6: LLNEW
        mem.put(cb + 26, 1, 1)
        for k, h in enumerate(pairs(ne)):
            _put_index(mem, inc + 32 * k, h * el)
            _put_index(mem, dec + 32 * k, -h * el)
    test = mem.get(mem.get(cb, 24), 64)
    at = table - el + _get_index(mem, inc)          # Box 7
    probes = []
    for k in range(n):
        probes.append(at)
        word = mem.get(at, 64)                      # Box 8
        if word == test:                            # Boxes 9, 16, 17
            return Result(True, at + 64, probes)
        if k + 1 == n:                              # Boxes 10, 11
            break
        step = inc if test > word else dec          # Boxes 12-14
        at += _get_index(mem, step + 32 * (k + 1))  # Box 15: the next pair
    return Result(False, None, probes)
