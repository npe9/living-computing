#!/usr/bin/env python3
"""Lockstep: multiply_bignum_by_word and subtract_bignum, multiple precision.

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

subtract_bignum(BigX, BigY, ^Borrow, ^BigZ), 22:B7 r4 (2026-11-24):
"the absolute value of [the difference] is unified with BigZ.  If the
result was non-negative 0, otherwise 1, is unified with Borrow"
(e-builtin.tex 720-727); VPIM's edges (kblt_b_subtract_bignum,
f_Subtract_BIGNUM_Sub, s_Subtract_BIGNUM): Y empty gives X and 0, X
empty gives Y and 1, equal gives 32#{} and 0, leading zero words of
the difference dropped.  The next stop of pim:go/4 (server/fep/fep/
time_sv.kl1 compare/4, the time equation).  Parts at its stub:
  {5} - {3}            0, {2}
  {3} - {5}            1, {2}
  {1, 0} - {1}         0, {16#ffffffff}   a borrow, a word dropped
  {1, 2, 3} - {1, 2, 2}  0, {1}           equal lengths, two dropped
  {2} - {1, 0}         1, {16#fffffffe}   Y the longer
  {7} - {}             0, {7}
  {} - {7}             1, {7}
  {4, 9} - {4, 9}      0, {}
  {10} - Y unbound     waits (the stub taken twice); Y := {4}: 0, {6}

add_bignum(BigX, BigY, ^BigZ), 22:B6 r_r_r (2026-11-25, the stop of
the shell's `ts`): "Adds BigX and BigY" (e-builtin.tex 710-717); VPIM's
edges (kblt_b_add_bignum, f_Add_BIGNUM_Sub, s_Add_BIGNUM): X empty
gives Y, Y empty gives X, the sum one word longer only on a last carry.
Parts at its stub:
  {5} + {3}                 {8}
  {ffffffff} + {1}          {1, 0}             a carry out, one word more
  {1, ffffffff} + {1}       {2, 0}             a carry between words
  {1} + {2, 3, 4}           {2, 3, 5}          Y the longer
  {ffffffff, ffffffff} + {ffffffff, ffffffff}
                            {1, ffffffff, fffffffe}  equal lengths, carry out
  {7} + {}                  {7}                Y empty: X
  {} + {7}                  {7}                X empty: Y
  {} + {}                   {}
  {9} + Y unbound           waits; Y := {1}: {10}

Not run: a leading zero word, a string not of 32 bits, Y not an
integer (multiply), the exception; refused by both models.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv rules
bn1..bn8, bsv/PimmMBox.bsv multiplyAdd), each run alone
(bsv/run_pimm_lockstep.sh bignum) and restored from a copy, 2026-11-24:
  the carry not added (multiplyAdd)  inner carry, line 26: M .. 02 for 03
  Y taken as signed (multiplyAdd)    carry, line 28: M .. fffffffe for 02
  no word for the last carry         carry, line 22: the descriptor of 2
                                     words for 3
  Y = 0 not special                  Y = 0, line 20: the descriptor of 1
                                     word for 0
  subtract_bignum (rules bs1..bsWrite):
  the borrow not carried             sub a borrow, line 29: the
                                     descriptor of 2 words for 1
  leading zero words kept            sub a borrow, line 29: the same
  the longer Y not taken as larger   sub Y longer, line 31: M .. 2 for
                                     fffffffe
  equal lengths compared wrongly     sub 5 - 3, line 29: M .. fffffffe
                                     for 2
  the empty X with borrow 0          sub empty X, line 25: R 4 0 for 1
  add_bignum (rules ba1..ba9), 2026-11-25:
  the carry between words not added  add an inner carry, line 29: M ..
                                     01 for 02
  no word for the last carry         add a carry out, line 23: the
                                     descriptor of 1 word for 2
  the longer Y not taken as longer   add Y longer, line 27: the
                                     descriptor of 1 word for 3
  X empty giving X                   add empty X, line 21: R 3 the X
                                     string for Y's
Pins 7 parts / 244 lines -> 16 / 651 (2026-11-24, the subtract parts'
lines; the multiply parts unchanged) -> 25 / 981 (2026-11-25, the add
parts; the others unchanged).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=25, lines=981)
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
    sub_script(s)
    add_script(s)
    return s


# subtract_bignum (2026-11-24): (label, X, Y, (Borrow, Z's words))
SUB = [
    ('5 - 3', [5], [3], (0, [2])),
    ('3 - 5', [3], [5], (1, [2])),
    ('a borrow', [1, 0], [1], (0, [0xffffffff])),
    ('equal lengths', [1, 2, 3], [1, 2, 2], (0, [1])),
    ('Y longer', [2], [1, 0], (1, [0xfffffffe])),
    ('empty Y', [7], [], (0, [7])),
    ('empty X', [], [7], (1, [7])),
    ('equal', [4, 9], [4, 9], (0, [])),
]


def sub_script(s):
    stub = pimm.Machine().stubs['subtract_bignum']['addr']
    for label, x, y, _want in SUB:
        s.label('sub ' + label)
        bignum(s, 0, x)
        bignum(s, 1, y)
        s.newvar(2)
        s.newvar(3)
        for k in range(4):
            s.arg(k + 1, k)
        s.spawn(stub, 4)
        s.run()
        s.out(2)
        s.out(3)
    s.label('sub Y unbound')
    bignum(s, 0, [10])
    s.newvar(1)
    s.newvar(2)
    s.newvar(3)
    for k in range(4):
        s.arg(k + 1, k)
    s.spawn(stub, 4)
    s.run()
    bignum(s, 4, [4])
    s.unify(1, 4)
    s.run()
    s.out(2)
    s.out(3)


# add_bignum (2026-11-25): (label, X, Y, Z's words)
ADD = [
    ('5 + 3', [5], [3], [8]),
    ('a carry out', [M], [1], [1, 0]),
    ('an inner carry', [1, M], [1], [2, 0]),
    ('Y longer', [1], [2, 3, 4], [2, 3, 5]),
    ('equal lengths', [M, M], [M, M], [1, M, M - 1]),
    ('empty Y', [7], [], [7]),
    ('empty X', [], [7], [7]),
    ('both empty', [], [], []),
]


def add_script(s):
    stub = pimm.Machine().stubs['add_bignum']['addr']
    for label, x, y, _want in ADD:
        s.label('add ' + label)
        bignum(s, 0, x)
        bignum(s, 1, y)
        s.newvar(2)
        for k in range(3):
            s.arg(k + 1, k)
        s.spawn(stub, 3)
        s.run()
        s.out(2)
    s.label('add Y unbound')
    bignum(s, 0, [9])
    s.newvar(1)
    s.newvar(2)
    for k in range(3):
        s.arg(k + 1, k)
    s.spawn(stub, 3)
    s.run()
    bignum(s, 4, [1])
    s.unify(1, 4)
    s.run()
    s.out(2)


EXPECT = dict([(label, [want]) for label, _x, _y, want in CASES])
for _l, _x, _y, (_b, _z) in SUB:
    EXPECT['sub ' + _l] = [_b, (32, _z)]
EXPECT['sub Y unbound'] = [0, (32, [6])]
for _l, _x, _y, _z in ADD:
    EXPECT['add ' + _l] = [(32, _z)]
EXPECT['add Y unbound'] = [(32, [10])]
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
        at = 'I %d ' % m.stubs['subtract_bignum']['addr']
        n = sum(ln.startswith(at) for ln in parts.get('sub Y unbound', []))
        if n != 2:
            bad.append(('sub Y unbound: the stub taken %d times' % n,))
        at = 'I %d ' % m.stubs['add_bignum']['addr']
        n = sum(ln.startswith(at) for ln in parts.get('add Y unbound', []))
        if n != 2:
            bad.append(('add Y unbound: the stub taken %d times' % n,))
    for k, want in EXPECT.items():
        got = [None if m.unbound(m.deref(w)) else m.term(w) for lab, w in outs if lab == k]
        norm = lambda v: v if v is None or isinstance(v, int) else (v[0], list(v[1]))  # noqa: E731
        if [norm(g) for g in got] != [norm(v) for v in want]:
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
    print('pimm lockstep bignum: PASS (multiply_bignum_by_word and subtract_bignum on the '
          'Bluespec core, %d trace lines identical to the reference model: products with '
          'and without a last carry, Y unsigned, the empty X, Y = 0; differences either way, '
          'with a borrow, leading words dropped, the empty operands, equal; inputs waited for)'
          % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
