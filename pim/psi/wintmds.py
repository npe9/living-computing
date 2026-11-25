#!/usr/bin/env python3
"""TMDS (DVI) encoder and decoder: the Python reference of the scan-out's
TMDS stage (bsv/WinScanOut.bsv, mkWinTmdsEnc), docs/simpos/window_hardware_plan.md H2.

SOURCE: Digital Visual Interface DVI, Revision 1.0, Digital Display
Working Group, 02 April 1999 ("DVI 1.0" below; a copy was read on
2026-11-25 from the DigiKey forum attachment dvi_spec-V1_0.pdf, page
numbers are its own "Page n of 76", which equal the PDF page numbers;
the PDF is not in the repository):
  - Fig. 3-5 p29, the encode algorithm, with Table 3-1 p28 (cnt is the
    running disparity, ones minus zeros transmitted; N1/N0 count ones
    and zeros); transcribed in `encode` below line by line;
  - the four control characters, written in Fig. 3-5 as q_out[0:9],
    i.e. BIT 0 FIRST: 00 -> 0010101011, 01 -> 1101010100,
    10 -> 0010101010, 11 -> 1101010101 (C1, C0); transcribed literally
    in CTRL_SPEC and turned into [9:0] integers by `_bits0first`;
  - Fig. 3-6 p31, the decode algorithm (`decode` below), whose case
    table repeats the same four characters in D[0:9] order;
  - §3.2.2 p28: "one of 460 unique 10-bit characters during active
    data" (pinned by test_winscan.py from `reachable()`);
  - §3.2.3 p30: q_out[0] is the first bit transmitted;
  - Fig. 3-2 p26: channel 0 carries BLU[7:0] with C0 = HSYNC and
    C1 = VSYNC; channels 1 (GRN) and 2 (RED) carry CTL0..CTL3, which
    §3.2.1 p26 says must be held low (CTL0 "recommended").

Symbols here are integers with bit i = q_out[i]; so the [9:0] value the
BSV encoder registers is the same integer, and a serializer sends bit 0
first.

Use:
    python3 -I psi/wintmds.py selftest      (the reachability numbers)
The unit tests are in psi/test_winscan.py.
"""
import sys

CTRL_SPEC = {0: '0010101011', 1: '1101010100', 2: '0010101010',
             3: '1101010101'}      # (C1 << 1 | C0) -> q_out[0:9], DVI 1.0 Fig. 3-5


def _bits0first(s):
    return sum(1 << i for i, ch in enumerate(s) if ch == '1')


CTRL = {c: _bits0first(s) for c, s in CTRL_SPEC.items()}
CTRL_OF = {v: c for c, v in CTRL.items()}


def n1(x):
    return bin(x).count('1')


def encode(cnt, de, c, d):
    """One step of DVI 1.0 Fig. 3-5: (symbol, new cnt).  c = C1 << 1 | C0."""
    if not de:
        return CTRL[c], 0
    nd = n1(d)
    xnor = nd > 4 or (nd == 4 and (d & 1) == 0)
    qm = d & 1
    for i in range(1, 8):
        prev = (qm >> (i - 1)) & 1
        b = (d >> i) & 1
        bit = (1 - (prev ^ b)) if xnor else (prev ^ b)
        qm |= bit << i
    qm8 = 0 if xnor else 1
    ones = n1(qm)
    zeros = 8 - ones
    inv = (~qm) & 0xff
    if cnt == 0 or ones == zeros:
        q = ((1 - qm8) << 9) | (qm8 << 8) | (qm if qm8 else inv)
        cnt = cnt + (zeros - ones) if qm8 == 0 else cnt + (ones - zeros)
    elif (cnt > 0 and ones > zeros) or (cnt < 0 and zeros > ones):
        q = (1 << 9) | (qm8 << 8) | inv
        cnt = cnt + 2 * qm8 + (zeros - ones)
    else:
        q = (qm8 << 8) | qm
        cnt = cnt - 2 * (1 - qm8) + (ones - zeros)
    return q, cnt


def decode(q, active):
    """DVI 1.0 Fig. 3-6: ('d', byte) in active data, ('c', C1C0) for a
    control character in blanking, None for anything else."""
    if not active:
        c = CTRL_OF.get(q)
        return None if c is None else ('c', c)
    d = q & 0xff
    if (q >> 9) & 1:
        d = (~d) & 0xff
    out = d & 1
    for i in range(1, 8):
        a, b = (d >> i) & 1, (d >> (i - 1)) & 1
        bit = (a ^ b) if (q >> 8) & 1 else (1 - (a ^ b))
        out |= bit << i
    return ('d', out)


def disparity(q):
    """Ones minus zeros of a 10-bit character."""
    return 2 * n1(q) - 10


def reachable():
    """(the cnt values reachable from 0 over all data bytes, the set of
    data characters produced) by exhaustive search."""
    seen, todo, syms = {0}, [0], set()
    while todo:
        c = todo.pop()
        for d in range(256):
            q, c2 = encode(c, True, 0, d)
            syms.add(q)
            if c2 not in seen:
                seen.add(c2)
                todo.append(c2)
    return seen, syms


_TAB = {}


def enc_table(cnt):
    """[d] -> (symbol, new cnt) for one cnt, memoised (the bench checks
    encode millions of pixels)."""
    t = _TAB.get(cnt)
    if t is None:
        t = _TAB[cnt] = [encode(cnt, True, 0, d) for d in range(256)]
    return t


# active and blanking decode tables over all 1,024 characters
DEC_DATA = [decode(q, True)[1] for q in range(1024)]
DEC_CTRL = [CTRL_OF.get(q) for q in range(1024)]


def main(argv):
    if argv[:1] == ['selftest']:
        states, syms = reachable()
        print('cnt reachable: %s' % sorted(states))
        print('data characters: %d' % len(syms))
        print('control characters [9:0]: %s' % {c: '{:010b}'.format(v)
                                                for c, v in CTRL.items()})
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
