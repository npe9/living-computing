#!/usr/bin/env python3
"""Lockstep: the IPL's file decoder on terms: integers, lists, vectors.

    python3 ref/pimm/lockstep_dect.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_dect.py compare

ipl_file_decoder:decode_0/7 (see lockstep_dec0.py for the module and
the argument roles) with what it calls: decode_atomic, decode_structure,
decode_list, decode_car, check_cdr, decode_vector.  The decoder does
not take its input as a list of words.  It ASKS: it binds its input
variable to a request and waits for the reader to fill it in (read
from the object code; asm/kl1decomp.py prints the clauses):

    [W|Rest]     one 16-bit word wanted in W
    {V, Rest}    a 32-bit value (two words, high first) wanted in V

This test plays the reader.  The script is grown against the reference
model (driver.Script.live): after each run the request the decoder left
is found in memory and answered with the next words of the term, by
address (the SLOT operation).  The Bluespec then replays the finished
script; the addresses hold there because the traces are compared.

Terms are encoded here by the rules of library/unloader/encoder.kl1:

    01xx / 02xx / 0300 hi lo     integer
    0700 n.hi n.lo  e1 .. en     vector of n elements
    0800 n.hi n.lo  c1 .. c(n-1) cdr     list: n-1 cars, then the cdr

and the oracle is twofold: asm/unlsav.py (an independent decoder of the
format, checked on the real .sav files) must read the same words back
to the term, and the model's Object must be that term; the input left
over must be the reader's unbound tail and Status normal.  Lists here
end in an integer, not [], because [] is an atom and atoms go through
the atom table, which needs instructions not modelled yet; for the
same reason no term is taken from a real .sav file yet.

The terms never take the decoder's error paths, where get_nil and
wait_atom are, so check_cdr/4 is also asked directly:

    check_cdr(abnormal(A), _, List, Status)   List = [], Status = abnormal(A)
    otherwise.
    check_cdr(_, Cdr, List, Status)           List = Cdr, Status = normal

That is the image's code as asm/kl1decomp.py prints it.  The held
source (decoder.kl1) has the same two clauses with the bare atom
abnormal for abnormal(A), so List = [] and List = Cdr are the source's
and the carried abnormal(A) is the image's alone.

New here: put_list, get_nil, wait_atom, and the driver's SLOT.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  put_list takes one cell              the vector (1): the next cell one lower
  put_list tagged as a 2-vector        the vector (1): R 11 = 15.. for 05..
  get_nil unifies with the integer 0   check_cdr abnormal(77): M = 00.. for 02..
  wait_atom passes any atom            check_cdr normal(77): the first clause goes on
  wait_atom does not note an unbound   the atom late: no suspension
    operand
  wait_atom reads register x           check_cdr abnormal(77): the otherwise clause
  SLOT keeps only the value (bench)    term 0: O 00.. for 06..
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import unlsav  # noqa: E402

PINNED = dict(parts=19, lines=10308)

# a term: an integer, ('v', [terms]) a vector, ('l', [cars], cdr) a list
TERMS = [
    7, -3, 300, -70000, 0x7fffffff, -0x80000000,
    ('v', [1]), ('v', [1, -2, 300]), ('v', [10, 20, 30, 40, 50, 60]), ('v', []),
    ('l', [1], 2), ('l', [1, 2, 3], 4), ('l', [], 9),
    ('l', [('v', [1, 2]), ('l', [5], 6)], -1),
    ('v', [('l', [1, 70000], 2), ('v', [('v', [3])]), 4]),
]


def encode(t):
    if isinstance(t, int):
        if 0 <= t < 0xff:
            return [0x0100 | t]
        if -256 < t < 0:
            return [0x0200 | t & 0xff]
        return [0x0300, t >> 16 & 0xffff, t & 0xffff]
    if t[0] == 'v':
        n = len(t[1])
        return [0x0700, n >> 16, n & 0xffff] + [w for e in t[1] for w in encode(e)]
    n = len(t[1]) + 1
    return ([0x0800, n >> 16, n & 0xffff] + [w for e in t[1] for w in encode(e)]
            + encode(t[2]))


def unl(p):
    """asm/unlsav.py's reading, as a term of this file's kind."""
    if p[0] == 'int':
        return p[1] - (1 << 32) if p[1] >= 1 << 31 else p[1]
    if p[0] == 'vector':
        return ('v', [unl(e) for e in p[1]])
    assert p[0] == 'list', p
    return ('l', [unl(e) for e in p[1][:-1]], unl(p[1][-1]))


def shown(t):
    """The term as pimm.Machine.term prints it."""
    if isinstance(t, int):
        return t
    if t[0] == 'v':
        return tuple(shown(e) for e in t[1])
    out = shown(t[2])
    for e in reversed(t[1]):
        out = ('|', shown(e), out)
    return out


def norm(v):
    """Machine.term gives a Python list for a proper list; none here."""
    return v


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    pc = pimm.predicate(im, 'ipl_file_decoder', 'decode_0/7')
    want = []
    for n, t in enumerate(TERMS):
        words = encode(t)
        r = unlsav.Reader(list(words))
        assert unl(unlsav.parse_term(r)) == t and r.i == len(words), t
        # slots: 0 the input, 1 UNLFS, 2 Object, 3 AT, 4 Status, 5 a request
        s.label('term %d: %r' % (n, t))
        for i in range(5):
            s.newvar(i)
        s.argc(1, (pimm.INT, words[0]))
        s.arg(2, 0)
        s.arg(3, 1)
        s.arg(4, 2)
        s.argc(5, (pimm.INT, 2222))
        s.arg(6, 3)
        s.arg(7, 4)
        s.spawn(pc, 7)
        feed = words[1:]
        m = s.live()
        at = s.live_slot[0]               # where the next request appears
        while True:
            s.run()
            m = s.live()
            progress = False
            while True:
                w = m.deref(at)
                if m.unbound(w):
                    break
                if w[0] & ~1 == pimm.LIST:
                    value, take = (pimm.INT, feed[0]), 1
                elif w[0] & ~1 == pimm.VECT0 + 4:
                    value, take = (pimm.INT, feed[0] << 16 | feed[1]), 2
                else:
                    raise AssertionError('an unknown request %r' % (w,))
                feed = feed[take:]
                s.setslot(5, (pimm.REF, w[1]))
                s.unifyc(5, value)
                at = (pimm.REF, w[1] + 1)
                m = s.live()
                progress = True
            if not progress:
                break
        assert not feed, (t, feed)
        s.setslot(5, at)
        for i in (1, 2, 3, 4, 5):
            s.out(i)
        want.append(('term %d: %r' % (n, t), t))
    # check_cdr/4.  slots: 0 List, 1 Status, 2 a late variable, 4 5 the
    # status vector's elements, 6 the status
    number = {name: n for n, name in im.sym.items()}
    cdr = pimm.predicate(im, 'ipl_file_decoder', 'check_cdr/4')
    A = lambda name: (pimm.ATOM, number[name])      # noqa: E731
    for label, first, late, expect in (
            ('check_cdr abnormal(77)', 'abnormal', False, ([], ('abnormal', 77))),
            ('check_cdr normal(77)', 'normal', False, (5, 'normal')),
            ('check_cdr abnormal(77), the atom late', 'abnormal', True, ([], ('abnormal', 77))),
            ('check_cdr the atom normal', None, False, (5, 'normal'))):
        s.label(label)
        s.newvar(0)
        s.newvar(1)
        if first is None:
            s.argc(1, A('normal'))
        else:
            s.vector(6, 4, [None if late else A(first), (pimm.INT, 77)])
            s.arg(1, 6)
        s.argc(2, (pimm.INT, 5))
        s.arg(3, 0)
        s.arg(4, 1)
        s.spawn(cdr, 4)
        s.run()
        if late:
            s.out(0)
            s.unifyc(4, A(first))
            s.run()
        s.out(0)
        s.out(1)
        want.append((label, expect))
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for label, t in want:
        if label.startswith('check_cdr'):
            if (m.term(got[label][-2]), m.term(got[label][-1])) != t:
                bad.append((label, m.term(got[label][-2]), m.term(got[label][-1]), t))
            continue
        unlfs, obj, at, status, tail = got[label][-5:]
        if m.term(obj) != shown(t):
            bad.append((label, m.term(obj), shown(t)))
        if not (m.unbound(tail) and unlfs == tail):
            bad.append((label, 'input left over', unlfs, tail))
        if (m.term(at), m.term(status)) != (2222, 'normal'):
            bad.append((label, m.term(at), m.term(status)))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep dect', PINNED)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad:
        print('pimm lockstep dect: FAIL, answers differ from the format: %r' % bad[:3])
        return 1
    print('pimm lockstep dect: PASS (the IPL file decoder on integers, lists and '
          'vectors on the Bluespec core: %d terms, %d trace lines identical to the '
          'reference model; the test answers the decoder\'s read requests; every '
          'object the term encoded, which asm/unlsav.py reads from the same words)'
          % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
