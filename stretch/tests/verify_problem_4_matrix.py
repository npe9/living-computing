#!/usr/bin/env python3
"""verify_problem_4_matrix.py PROBLEM DECK ASM=strap2 [--corrected]
[--sub OLD NEW]... -- C22-6578 Problems 4.7 and 4.8, the 64 x 64 bit
matrix transposes and the product of square matrices, and 4.3-4.5, the
sparse-vector problems, checked word for word against what the PAGE
defines, worked here and not by the model.

    4.7m1   decks/problem_4_7_method1.strap   transpose, bit by bit
    4.7m2   decks/problem_4_7_method2.strap   transpose, 8 x 8 blocks
    4.8     decks/problem_4_8.strap           P = L * R, floating point
    4.5     decks/problem_4_5.strap           sparse scalar product, N = 40
    4.5n37  decks/problem_4_5.strap           the same deck, N = 37
    4.5k0   decks/problem_4_5.strap           x_1 y_1 non-zero, as printed

THE DECK AND ITS ASSEMBLER ARE NAMED ON THE RUN LINE, as run_program.sh's
are: the decks are assembled by the host STRAP II (they hold "N*N", which
strap_asm refuses), and check_strap2_oracles.py reads the run lines to know
which assembler a deck is for.  The named deck must be the problem's.

THIS IS NOT THE MODEL.  It imports nothing from bsv/.  It reads the
deck's data words as strap2 assembles them and works the expected words:

  transpose   the problem statement itself: bit (r, c) to (c, r).
  trace       for a program as PRINTED where it does not do what the
              statement asks, the program's own steps, written out below
              from the Reference Manual (22-6530-2, printed page = PDF - 3):
              index words pp.21 and 24, progressive indexing and the
              second I field (index bit 3 at instruction bit 35) p.21, V+/V+C
              p.24, V+I/V-ICR/C-I p.25, CB/CBR/CBZR p.26 ("The setting of
              the index flag and index result indicators precedes the
              refill"), VFL load p.61, CONNECT pp.75-76 (bytes of fewer
              than eight bits widened with high-order zeros; the
              accumulator operand as many eight-bit bytes from the offset;
              bits past the accumulator's left end dropped, "partial
              field"), and for 4.8 problem_3_expected.py's floating
              arithmetic (LFT p.98, *+ p.98, DL p.96, SRD p.96), which
              is that file's and is not the model either.
              The trace run on the CORRECTED program must give the
              statement's answer; that is asserted before anything runs,
              so the trace is checked against the definition.

--corrected   applies the deck's documented correction (CORRECTIONS
              below) to a temporary copy; the printed card stays in the
              deck.
--sub OLD NEW replaces OLD (exactly one occurrence) in the copy that is
              RUN, after the expected words are worked from the deck as it
              stands: the injection mechanism.  An injected datum is then
              charged to the model's result, not followed by the
              expectation.
"""
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'strap'))
sys.path.insert(0, HERE)

M64 = (1 << 64) - 1
M18 = (1 << 18) - 1


def xword(v, count, refill):
    """An index word: value bits 0-23 as a bit address, sign bit 24
    (printed p.21), count bits 28-45, refill bits 46-63 (printed p.24)."""
    return ((abs(v) & 0xFFFFFF) << 40) | ((1 if v < 0 else 0) << 39) | \
        ((count & M18) << 18) | (refill & M18)


class X:
    """An index register: value (bits, signed), count, refill (word)."""

    def __init__(self, v, count, refill):
        self.v, self.c, self.r = v, count, refill

    def copy(self):
        return X(self.v, self.c, self.r)

    def word(self):
        return xword(self.v, self.c, self.r)


class Bits:
    """Storage as words, addressed by bit."""

    def __init__(self, words):
        self.w = dict(words)

    def get(self, a, n):
        out = 0
        for i in range(n):
            q, b = divmod(a + i, 64)
            out = (out << 1) | ((self.w.get(q, 0) >> (63 - b)) & 1)
        return out

    def put(self, a, n, val):
        for i in range(n):
            q, b = divmod(a + i, 64)
            bit = (val >> (n - 1 - i)) & 1
            self.w[q] = (self.w.get(q, 0) & ~(1 << (63 - b))) | (bit << (63 - b))


def transpose(words, n):
    """Bits r*n+c -> c*n+r of an n x n matrix stored row-wise."""
    bits = []
    for w in words:
        bits += [(w >> (63 - i)) & 1 for i in range(64)]
    out = bits[:]
    for r in range(n):
        for c in range(n):
            out[c * n + r] = bits[r * n + c]
    return [int(''.join(map(str, out[64 * i:64 * i + 64])), 2) for i in range(len(words))]


# ---------------------------------------------------------------------------
# 4.7 Method 2, printed pp.40-41, as a trace of its own statements.
# ---------------------------------------------------------------------------

def trace_4_7m2(sym, words, xw2_count):
    LOC = sym['BMX64']
    mem = Bits(words)
    cell = {}                           # the XW words, by word address
    for n in ('XW1', 'XW2', 'XW3', 'XW4', 'XW11', 'XW22', 'XW44', 'XW111', 'XW222'):
        cell[sym[n] // 64] = None
    xw = lambda n: sym[n] // 64        # noqa: E731
    acc = [0]                           # 128 bits, bit 0 leftmost

    def refill(x):
        c = cell[x.r]
        x.v, x.c, x.r = c.v, c.c, c.r

    def count(x):                       # count down, refill at zero; XCZ
        x.c = (x.c - 1) & M18
        z = x.c == 0
        if z:
            refill(x)
        return z

    def connect_or(addr, off):          # C0111(BU,8,1): 8 one-bit bytes
        m = mem.get(addr, 8)
        for c in range(8):              # byte c's data bit, the low one
            p = 127 - off - 8 * (7 - c)
            if p >= 0 and (m >> (7 - c)) & 1:
                acc[0] |= 1 << (127 - p)

    def store8(addr, off):              # ST(BU,8,8): 8 bits ending at off
        right = 127 - off
        mem.put(addr, 8, (acc[0] >> (127 - right)) & 0xFF)

    def off3(base, x3):                 # offset indexed by $3's half words
        assert x3.v % 32 == 0
        return base + x3.v // 32

    x1 = X(LOC, 8, xw('XW111'))
    cell[xw('XW1')] = x1.copy()
    cell[xw('XW11')] = x1.copy()
    cell[xw('XW111')] = x1.copy()
    x2 = X(LOC, xw2_count, xw('XW222'))
    cell[xw('XW2')] = x2.copy()
    cell[xw('XW22')] = x2.copy()
    cell[xw('XW222')] = x2.copy()
    x3 = X(0, 8, xw('XW3'))
    cell[xw('XW3')] = x3.copy()
    x4 = X(0, 8, xw('XW44'))
    cell[xw('XW4')] = x4.copy()
    cell[xw('XW44')] = x4.copy()
    for _row in range(100):
        acc[0] = 0                                          # DIAG
        while True:                                         # DIAG1
            connect_or(x1.v, off3(7, x3))
            x1.v += 64
            count(x1)
            x3.v -= 32
            if count(x3):
                break
        while True:                                         # DIAG2
            store8(x1.v, off3(64 - 8, x3))
            x1.v += 64
            count(x1)
            x3.v -= 8 * 32
            if count(x3):
                break
        if count(x4):                                       # CBZR,$4,BEW
            break
        while True:                                         # OFDIAG
            x1.v += 8
            cell[xw('XW111')] = x1.copy()
            x2.v += 8 * 64
            cell[xw('XW222')] = x2.copy()
            acc[0] = 0
            while True:                                     # OFDIA1
                connect_or(x1.v, off3(7, x3))
                x1.v += 64
                count(x1)
                connect_or(x2.v, off3(64 + 7, x3))
                x2.v += 64
                count(x2)
                x3.v -= 32
                if count(x3):
                    break
            while True:                                     # OFDIA2
                store8(x2.v, off3(64 - 8, x3))
                x2.v += 64
                count(x2)
                store8(x1.v, off3(128 - 8, x3))
                x1.v += 64
                count(x1)
                x3.v -= 8 * 32
                if count(x3):
                    break
            if not count(x4):                               # CBR,$4,OFDIAG
                continue
            break
        x1 = cell[xw('XW11')].copy()                        # NEWROW
        x1.v += 8 * 64 + 8
        cell[xw('XW11')] = x1.copy()
        cell[xw('XW111')] = x1.copy()
        x2 = cell[xw('XW22')].copy()
        x2.v += 8 * 64 + 8
        cell[xw('XW22')] = x2.copy()
        cell[xw('XW222')] = x2.copy()
        x4.c = (x4.c - 1) & M18                             # C-I,$4,1
        cell[xw('XW44')] = x4.copy()
    else:
        raise SystemExit("trace_4_7m2: no halt in 100 rows")
    out = {a: mem.w[a] for a in range(LOC // 64, LOC // 64 + 64)}
    regs = {'x1': x1, 'x2': x2, 'x3': x3, 'x4': x4}
    cells = {n: cell[xw(n)] for n in ('XW11', 'XW22', 'XW44', 'XW111', 'XW222')}
    return out, regs, cells, acc[0]


# ---------------------------------------------------------------------------
# 4.8, printed p.42, as a trace of its own statements.
# ---------------------------------------------------------------------------

def trace_4_8(sym, words, step3, sub3, step2):
    """step3, step2: the half words V+I adds to $3 and $2; sub3: the half
    words V-ICR takes from $3.  As printed, with N an integer 8, these are
    8, 64 - 2 and 8 (an integer in a 19-bit field counts half words,
    C28-6129 Section I printed pp.8-9)."""
    from problem_3_expected import Acc
    N = 8
    w = lambda a: words.get(a // 64, 0)         # noqa: E731
    xw22 = sym['XW22'] // 64
    x2 = X(sym['LMTRIX'], N, xw22)
    x3 = X(sym['RMTRIX'], N, sym['XW3'] // 64)
    x4 = X(sym['PMTRIX'], N, sym['XW4'] // 64)
    xw3 = x3.copy()
    cell22 = None
    out = {}
    read = []
    acc = Acc()
    for _i in range(N + 1):
        cell22 = x2.copy()                                  # SIX
        while True:
            acc.dload(w(sym['ZERO']), normalized=False)     # LU  DL(U)
            elems = []
            while True:
                acc.load_factor(w(x2.v), normalized=False)  # LFT(U)
                acc.mul_add(w(x3.v), normalized=True)       # *+(N)
                elems.append((x2.v // 64, x3.v // 64))
                x3.v += step3 * 32                          # V+I,$3,N
                x2.v += 64                                  # CBR+: one word
                x2.c = (x2.c - 1) & M18
                if x2.c != 0:
                    continue
                x2.v, x2.c, x2.r = cell22.v, cell22.c, cell22.r
                break
            out[x4.v // 64] = acc.store_rounded(normalized=True)   # SRD(N)
            read.append(elems)
            x4.v += 64                                      # V+I,$4,1.0
            x3.v -= sub3 * 32                               # V-ICR,$3
            x3.c = (x3.c - 1) & M18
            if x3.c == 0:
                x3.v, x3.c, x3.r = xw3.v, xw3.c, xw3.r
                break                                       # BZXCZ falls
        x2.v += step2 * 32                                  # V+I,$2,N
        x4.c = (x4.c - 1) & M18                             # CB,$4,SIX
        if x4.c == 0:
            break
    else:
        raise SystemExit("trace_4_8: no halt")
    return out, {'x2': x2, 'x3': x3, 'x4': x4}, cell22, read


# ---------------------------------------------------------------------------
# 4.5, printed pp.38-39, as a trace of its own statements.
# ---------------------------------------------------------------------------

def popcount(v):
    return bin(v).count('1')


def lzc_of(v, n):
    """Left zeros of an n-bit result field; n if it is all zero (p.76)."""
    return n - v.bit_length()


def trace_4_5(sym, words, N):
    """The printed program, statement by statement, on a copy of storage.
    Returns the words it leaves and the accumulator state.  The second I
    field ($1) adds index value bits 3-18 to instruction bits 35-50 (p.56):
    LV,$1,8.0 after LF(BU,25),$LZC-0.2,128-25 puts the left-zeros count at
    value bits 2-8, so bits 3-8 -- the count modulo 64 -- are the length;
    the instruction's own length is 0, and a length of 0 is 64 (p.56)."""
    from problem_3_expected import Acc
    mem = Bits(words)
    w = lambda s: s // 64                       # noqa: E731
    XB, YB, KEY = sym['XBMAGE'], sym['YBMAGE'], sym['KEYVEC']
    SAVEX, PRODT = w(sym['SAVEX']), w(sym['PRODT'])
    XV, YV = w(sym['XVEC']), w(sym['YVEC'])
    regs = {1: words[w(sym['SENT1'])], 2: words[w(sym['SENT2'])],
            3: words[w(sym['SENT3'])]}          # the deck's preamble
    for i in range(3):                          # TI,3,17.0,SAVEX
        mem.w[SAVEX + i] = regs[1 + i]
    nmask = (1 << N) - 1
    res = mem.get(XB, N) & mem.get(YB, N)       # L, C0001: "and" (Fig. 20)
    aoc, lzc = popcount(res), lzc_of(res, N)
    mem.put(KEY, N, res)                        # ST(BU,N),KEYVEC
    count3 = aoc                                # L(BU,7),$AOC,64+18; LX
    acc = Acc()
    acc.dload(words.get(w(sym['ZERO']), 0), normalized=False)
    mem.w[PRODT] = acc.store(normalized=False)  # DL(U),ZERO;ST(U),PRODT
    products = []
    last = (lzc, aoc)
    if count3 != 0:                             # BXCZ,FIN; B,LOF
        while True:
            k = lzc                             # LOF: $LZC into $1
            length = (k & 63) or 64
            fx = mem.get(XB, length)            # CT0011(BU,0),XBMAGE,0($1)
            ax = popcount(fx)                   # LV,$2,7.32; V+,$2,18.0
            fy = mem.get(YB, length)            # CT0011(BU,0),YBMAGE,0($1)
            ay = popcount(fy)
            last = (lzc_of(fy, length), ay)
            count3 = (count3 - 1) & M18         # LV,$3,7.32; V+C,$3,19.0
            acc.load(mem.w[PRODT], normalized=False)          # L(U)
            acc.load_factor(mem.w.get(XV + ax, 0), normalized=False)  # LFT(U)
            acc.mul_add(mem.w.get(YV + ay, 0), normalized=True)     # *+(N)
            mem.w[PRODT] = acc.store(normalized=False)         # ST(U)
            products.append((k, ax, ay))
            if count3 == 0:                     # BZXCZ,LOOP falls
                break
            mem.put(KEY + 1, length, 0)         # LOOP: CM0000 at KEYVEC+0.1
            lzc = lzc_of(mem.get(KEY, N) & nmask, N)   # CT0011(BU,N),KEYVEC
    for i in range(3):                          # FIN: TI,3,SAVEX,17.0
        regs[1 + i] = mem.w[SAVEX + i]
    w7 = (last[0] << (63 - 23)) | (last[1] << (63 - 50))
    # acc bits 108-127: cleared by the VFL L(BU,7) (p.61) and untouched by
    # every floating operation after it (pp.88, 96, 98)
    w9 = (acc.lo & ((1 << 44) - 1)) << 20
    return mem, regs, acc, w7, w9, products


def spec_4_5(sym, words, corrected, N):
    from problem_3_expected import value
    from fractions import Fraction
    w = lambda s: s // 64                       # noqa: E731
    xb, yb = words[w(sym['XBMAGE'])], words[w(sym['YBMAGE'])]
    bit = lambda v, i: (v >> (63 - i)) & 1     # noqa: E731
    # the statement: the sum over k < N of x_k y_k, x_k the (number of
    # ones of XBMAGE before k)-th word of XVEC
    xs = [k for k in range(N) if bit(xb, k)]
    ys = [k for k in range(N) if bit(yb, k)]
    common = [k for k in range(N) if bit(xb, k) and bit(yb, k)]
    S = sum(value(words[w(sym['XVEC']) + xs.index(k)]) *
            value(words[w(sym['YVEC']) + ys.index(k)]) for k in common)
    mem, regs, acc, w7, w9, products = trace_4_5(sym, words, N)
    got = Fraction((acc.hi << 48) | acc.lo, 1 << 96) * Fraction(2) ** acc.e
    got = -got if acc.neg else got
    if common and common[0] != 0:
        assert got == S, "trace of the printed program is not the scalar product"
    PRODT = w(sym['PRODT'])
    exact = [("PRODT", PRODT, mem.w[PRODT]),
             ("KEYVEC", w(sym['KEYVEC']), mem.w[w(sym['KEYVEC'])])]
    exact += [("SAVEX%d" % i, w(sym['SAVEX']) + i, mem.w[w(sym['SAVEX']) + i])
              for i in range(3)]
    exact += [("x%d_restored" % j, 16 + j, regs[j]) for j in (1, 2, 3)]
    exact += [("w7_lzc_aoc", 7, w7), ("acc_left", 8, acc.word8()),
              ("acc_right", 9, w9)]
    note = ("statement: N = %d, common non-zero k = %s, sum = %s (%d bits); "
            "trace: %d products %s, sum %s"
            % (N, common, S, abs(S).numerator.bit_length() if S else 0,
               len(products), products, got))
    return exact, note


# ---------------------------------------------------------------------------

CORRECTIONS = {
    # printed p.41: $2 counts 7 and is used eight times a block
    '4.7m2': [("XW2     XW,LOC,7,XW222", "XW2     XW,LOC,8,XW222")],
    # printed p.42: "N" in V+I is N HALF words; a row of R or L is N words
    '4.8': [("VPI     V+I,$3,N                        !'advance $3 to next row",
             "VPI     V+I,$3,N+N                      !'advance $3 to next row"),
            ("\n        V-ICR,$3,N*N-1.0\n", "\n        V-ICR,$3,2*N*N-1.0\n"),
            ("        V+I,$2,N                        !'procedure for new row",
             "        V+I,$2,N+N                      !'procedure for new row")],
}
DECKS = {'4.7m1': ('problem_4_7_method1.strap', 'StretchP47M1Tb'),
         '4.7m2': ('problem_4_7_method2.strap', 'StretchP47M2Tb'),
         '4.8': ('problem_4_8.strap', 'StretchP48Tb'),
         '4.5': ('problem_4_5.strap', 'StretchP45Tb'),
         '4.5n37': ('problem_4_5.strap', 'StretchP45N37Tb'),
         '4.5k0': ('problem_4_5.strap', 'StretchP45K0Tb')}
# A run of a deck under a different N, or other data, the page allows:
# applied BEFORE the expected words are worked, so they follow it (unlike
# --sub, which is an injection the expectation does not follow).
VARIANTS = {'4.5n37': [("\nN       SYN,40\n", "\nN       SYN,37\n")],
            '4.5k0': [("(16)6991892315442001", "(16)E991892315000000"),
                      ("(16)31530A2527420001", "(16)B1530A2527000000")]}


def halt_pc(words, lo, hi):
    """The half word of the first BEW, $ in words lo..hi: an unconditional
    BEW to its own half word assembles as (h << 13) | (16)1000."""
    for a in range(lo, hi + 1):
        for h, hw in ((2 * a, words.get(a, 0) >> 32), (2 * a + 1, words.get(a, 0) & 0xFFFFFFFF)):
            if hw == ((h << 13) | 0x1000):
                return h
    raise SystemExit("no BEW, $ found")


def spec_4_7m1(sym, words, corrected):
    LOC, N = sym['BMX64'] // 64, 64
    A = [words[LOC + i] for i in range(64)]
    T = transpose(A, N)
    bit = lambda r, c: (A[(r * N + c) // 64] >> (63 - (r * N + c) % 64)) & 1   # noqa: E731
    v2 = sym['BMX64'] + N * N
    v3 = sym['BMX64'] + N * N + N - 1
    exact = [("row%02d" % i, LOC + i, T[i]) for i in range(64)]
    exact += [("x2", 18, xword(v2, 0, sym['XW22'] // 64)),
              ("XW22", sym['XW22'] // 64, xword(v2, 0, sym['XW22'] // 64)),
              ("x3", 19, xword(v3, 0, sym['XW33'] // 64)),
              ("XW33", sym['XW33'] // 64, xword(v3, 0, sym['XW33'] // 64)),
              ("acc_left_A63_62", 8, bit(63, 62)),
              ("acc_right_A62_63", 9, bit(62, 63))]
    return exact, None


def spec_4_7m2(sym, words, corrected):
    LOC = sym['BMX64'] // 64
    A = [words[LOC + i] for i in range(64)]
    T = transpose(A, 64)
    good, gregs, gcells, gacc = trace_4_7m2(sym, words, 8)
    assert [good[LOC + i] for i in range(64)] == T, "trace of the corrected program is not the transpose"
    out, regs, cells, acc = trace_4_7m2(sym, words, 8 if corrected else 7)
    got = [out[LOC + i] for i in range(64)]
    exact = [("row%02d" % i, LOC + i, got[i]) for i in range(64)]
    exact += [(n, 16 + int(n[1]), regs[n].word()) for n in ('x1', 'x2', 'x3', 'x4')]
    exact += [(n, sym[n] // 64, c.word()) for n, c in cells.items()]
    exact += [("acc_left", 8, acc >> 64), ("acc_right", 9, acc & M64)]
    nbad = sum(bin(g ^ t).count('1') for g, t in zip(got, T))
    rows = sum(g != t for g, t in zip(got, T))
    note = ("trace: %d of 4096 bits differ from the transpose, in %d of 64 rows"
            % (nbad, rows))
    return exact, note


def spec_4_8(sym, words, corrected):
    from problem_3_expected import Acc, value
    N = 8
    L = [words[sym['LMTRIX'] // 64 + i] for i in range(N * N)]
    R = [words[sym['RMTRIX'] // 64 + i] for i in range(N * N)]
    # the statement: P = L * R, each element worked with the same
    # arithmetic, in the order the program sums (k = 0..N-1)
    want = {}
    for i in range(N):
        for j in range(N):
            acc = Acc()
            acc.dload(words.get(sym['ZERO'] // 64, 0), normalized=False)
            for k in range(N):
                acc.load_factor(L[i * N + k], normalized=False)
                acc.mul_add(R[k * N + j], normalized=True)
            want[sym['PMTRIX'] // 64 + i * N + j] = acc.store_rounded(normalized=True)
    # and the exact sums, which the small integers make representable
    for i in range(N):
        for j in range(N):
            s = sum(value(L[i * N + k]) * value(R[k * N + j]) for k in range(N))
            assert value(want[sym['PMTRIX'] // 64 + i * N + j]) == s
    good = trace_4_8(sym, words, 16, 2 * 64 - 2, 16)
    assert good[0] == want, "trace of the corrected program is not L * R"
    out, regs, cell22, read = trace_4_8(sym, words, 16, 126, 16) if corrected \
        else trace_4_8(sym, words, 8, 62, 8)
    P = sym['PMTRIX'] // 64
    exact = [("P%d%d" % divmod(a - P, N), a, out[a]) for a in sorted(out)]
    exact += [(n, 16 + int(n[1]), regs[n].word()) for n in ('x2', 'x3', 'x4')]
    exact += [("XW22", sym['XW22'] // 64, cell22.word())]
    bad = sum(out[a] != want[a] for a in want)
    l0, r0 = sym['LMTRIX'] // 64, sym['RMTRIX'] // 64
    e = read[0 * N + 1]
    note = ("trace: %d of 64 elements differ from L * R; P[0][1] reads L%s and R%s"
            % (bad, [a - l0 for a, _ in e], [b - r0 for _, b in e]))
    return exact, note


SPECS = {'4.7m1': spec_4_7m1, '4.7m2': spec_4_7m2, '4.8': spec_4_8,
         '4.5': lambda s, w, c: spec_4_5(s, w, c, 40),
         '4.5n37': lambda s, w, c: spec_4_5(s, w, c, 37),
         '4.5k0': lambda s, w, c: spec_4_5(s, w, c, 40)}


def main():
    args = sys.argv[1:]
    subs = []
    corrected = '--corrected' in args
    if corrected:
        args.remove('--corrected')
    while '--sub' in args:
        i = args.index('--sub')
        subs.append((args[i + 1], args[i + 2]))
        del args[i:i + 3]
    if len(args) != 3 or args[0] not in SPECS or args[2] != 'ASM=strap2':
        raise SystemExit("usage: verify_problem_4_matrix.py %s DECK ASM=strap2 "
                         "[--corrected] [--sub OLD NEW]..." % '|'.join(sorted(SPECS)))
    problem, deck_arg = args[0], args[1]
    deck_name, module = DECKS[problem]
    if os.path.basename(deck_arg) != deck_name:
        raise SystemExit("%s is deck %s, not %s" % (problem, deck_name, deck_arg))
    with open(os.path.join(HERE, '..', 'decks', deck_name)) as f:
        src = f.read()
    def apply(src, pairs, what):
        for old, new in pairs:
            if src.count(old) != 1:
                raise SystemExit("%s: %r occurs %d times, need exactly 1" % (what, old, src.count(old)))
            src = src.replace(old, new)
            print("%s: %r -> %r" % (what, old, new))
        return src
    if problem in VARIANTS:
        src = apply(src, VARIANTS[problem], "VARIANT")
    if corrected:
        src = apply(src, CORRECTIONS[problem], "CORRECTED")
    run_src = apply(src, subs, "INJECTED")
    import strap_asm
    import strap2
    prog = strap2.assemble(src, strap_asm.DEFAULT_ORIGIN_BITS)
    sym, words = prog.symtab, prog.words
    exact, note = SPECS[problem](sym, words, corrected)
    if note:
        print(note)
    lo = strap_asm.DEFAULT_ORIGIN_BITS // 64
    checks = ["ASM=strap2", "PC=%d" % halt_pc(words, lo, lo + 200), "STEPS=4000000"]
    checks += ["%s:%d=0x%X" % (lab, a, w) for lab, a, w in exact]
    # the guards, the deck's GUARD words, unchanged
    for g in sorted(k for k in sym if k.startswith('GUARD')):
        checks.append("%s:%d=0x%X" % (g, sym[g] // 64, words[sym[g] // 64]))
    with tempfile.TemporaryDirectory() as tmp:
        deck = os.path.join(tmp, deck_name)
        with open(deck, 'w') as f:
            f.write(run_src)
        r = subprocess.run(["./run_program.sh", deck, module] + checks,
                           cwd=HERE, capture_output=True, text=True)
    shown = [ln for ln in r.stdout.splitlines() if ln.startswith(('PASS', 'FAIL', 'ALL TESTS'))]
    print("\n".join(shown))
    fails = 0
    if r.returncode != 0:
        print(r.stdout[-1500:], r.stderr[-1500:])
        print("FAIL run_program.sh exit status", r.returncode)
        fails += 1
    if any(ln.startswith('FAIL') for ln in shown):
        fails += 1
    if not any(ln.startswith('ALL TESTS PASSED') for ln in shown):
        print("FAIL the run printed no ALL TESTS PASSED")
        fails += 1
    print("verify_problem_4_matrix %s%s: %d checks and the PC"
          % (problem, " (corrected)" if corrected else "", len(checks) - 3))
    print("ALL CHECKS PASSED" if not fails else "FAILED")
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
