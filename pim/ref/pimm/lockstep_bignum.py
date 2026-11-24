#!/usr/bin/env python3
"""Lockstep: multiply_bignum_by_word, the multiple precision built-in.

    python3 ref/pimm/lockstep_bignum.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_bignum.py compare
    python3 ref/pimm/lockstep_bignum.py --reference       the reference alone

multiply_bignum_by_word(BigX, Y, ^BigZ), 22:B8 r_r_r (library/assembler/
inst_tab.kl1:247, compiler/blt.kl1 multiply_bignum_word): "The result
of multiplying BigX by Y seen as a 32-bit unsigned integer is unified
with BigZ"; a bignum is a 32-bit string read as an unsigned integer,
"The MSB is the zeroth element and is zero suppressed" (PIMOS manual
e-builtin.tex 703-741).  VPIM's (klb_body_blt_bignum.psl.c,
f_reduce_bignum.psl.c, str_bignum.psl.c) settles the edges: the empty
X is the answer itself, Y = 0 gives the empty string, a leading zero
word is the exception.  It was the stop of pim:go/4 with the device
(rung S0), timer_calc:trans (server/fep/timer/sysTcalc.kl1), which
multiplies by 1000, 16, 16000 ... to change units.

Parts, each at the built-in's stub (as lockstep_timer.py runs
set_timer), the strings made by the bench (NEWSTR, SETW), the expected
answers the product's words, MSB first:
  32#{1000} * 1000              32#{1000000}
  32#{16#80000000, 1} * 4       32#{2, 0, 4}         one word longer
  32#{1, 16#ffffffff} * 2       32#{3, 16#fffffffe}  a carry between words
  32#{2} * -1 (unsigned)        32#{1, 16#fffffffe}
  32#{} * 5                     32#{}                 X itself
  32#{7} * 0                    32#{}
  X unbound, * 16               waits (the stub taken twice); X :=
                                32#{3}: 32#{48}

Not run: a leading zero word, X not a 32-bit string, Y not an integer
(the exception; refused by both models).

Observed fault injections into the Bluespec (bsv/PimmStages.bsv rules
bn1..bn8, bsv/PimmMBox.bsv multiplyAdd), each run alone
(bsv/run_pimm_lockstep.sh bignum) and restored from a copy, 2026-11-24:
  the carry not added (multiplyAdd)  inner carry, line 26: M .. 02 for 03
  Y taken as signed (multiplyAdd)    carry, line 28: M .. fffffffe for 02
  no word for the last carry         carry, line 22: the descriptor of 2
                                     words for 3
  Y = 0 not special                  Y = 0, line 20: the descriptor of 1
                                     word for 0
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=7, lines=244)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
M = 0xffffffff
CASES = [
    ('1000 * 1000', [1000], 1000, (32, [1000000])),
    ('carry', [0x80000000, 1], 4, (32, [2, 0, 4])),
    ('inner carry', [1, 0xffffffff], 2, (32, [3, 0xfffffffe])),
    ('unsigned Y', [2], -1, (32, [1, 0xfffffffe])),
    ('empty X', [], 5, (32, [])),
    ('Y = 0', [7], 0, (32, [])),
]


def bignum(s, slot, words):
    s.newstr(slot, len(words), 32)
    for i, w in enumerate(words):
        s.setw(slot, i, w & M)


def script():
    stub = pimm.Machine().stubs['multiply_bignum_word']['addr']
    s = driver.Script()
    for label, x, y, _want in CASES:
        s.label(label)
        bignum(s, 0, x)
        s.newvar(1)
        s.arg(1, 0)
        s.argc(2, I(y))
        s.arg(3, 1)
        s.spawn(stub, 3)
        s.run()
        s.out(1)
    s.label('X unbound')
    s.newvar(0)
    s.newvar(1)
    s.arg(1, 0)
    s.argc(2, I(16))
    s.arg(3, 1)
    s.spawn(stub, 3)
    s.run()
    s.out(1)
    bignum(s, 2, [3])
    s.unify(0, 2)
    s.run()
    s.out(1)
    return s


EXPECT = dict([(label, [want]) for label, _x, _y, want in CASES])
# the outs are read at the end (driver.Script), so both are the answer;
# that the built-in waited is the stub taken twice in that part
EXPECT['X unbound'] = [(32, [48]), (32, [48])]


def check(m, outs, parts=None):
    bad = []
    if parts is not None:
        at = 'I %d ' % m.stubs['multiply_bignum_word']['addr']
        n = sum(ln.startswith(at) for ln in parts.get('X unbound', []))
        if n != 2:
            bad.append(('X unbound: the stub taken %d times' % n,))
    for k, want in EXPECT.items():
        got = [None if m.unbound(m.deref(w)) else m.term(w) for lab, w in outs if lab == k]
        got = [tuple(g) if isinstance(g, (list, tuple)) and len(g) == 2 and g[0] == 32 else g for g in got]
        want = [None if v is None else (v[0], v[1]) for v in want]
        if [None if g is None else (g[0], list(g[1])) for g in got] != want:
            bad.append((k, got, want))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = list(lines)
            yield what, lines
    s.play = keeping
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s.machine, s.outs, kept)
        print(bad, n, [(lab, s.machine.term(w)) for lab, w in s.outs])
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep bignum', PINNED)
    if not ok:
        return 1
    bad = check(m, s.outs, kept)
    if bad:
        print('pimm lockstep bignum: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep bignum: PASS (multiply_bignum_by_word on the Bluespec core, %d '
          'trace lines identical to the reference model: products with and without a '
          'last carry, Y unsigned, the empty X, Y = 0, and an unbound X waited for)'
          % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
