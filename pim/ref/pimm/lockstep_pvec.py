#!/usr/bin/env python3
"""Lockstep: the guard X = Y (wait_value) on two vectors, under the
IPL's keyed pool.

    python3 ref/pimm/lockstep_pvec.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_pvec.py compare
    python3 ref/pimm/lockstep_pvec.py --reference       the reference alone

pim:go/4 with the device (rung S0, docs/scsi_plan.md) stopped at
wait_value on two vectors: the kernel's keyed_bag comparing the key
{0,0,0} (cluster, processor, SCSI port: bios/boot/scsi_man.kl1's
CONF_POOL and UNIT_POOL) with a key it holds.  The IPL image's own
pool, ipl_pool:keyed_set/2 (lockstep_pool.py), compares its keys the
same way (wait_value in if_empty/4, do_get_if_any/9,
do_get_if_any_and_put1/10, do_get_and_put/5), so this test gives that
pool vector keys.

The meaning is PDSS's passive unification (emulator/emulate.c
KL1B_WAIT_VALUE, emulator/passive.c passive_unify), as far as both
models take it (docs/pimm_semantics.md, wait_value): two vectors of 0
to 6 elements are equal when they have the same size and each pair of
elements is the same atomic value (tag and value); the elements are
taken in order, and the first unbound one met is noted and the guard
fails there (an unbound element of X; or of Y, opposite an atomic
element of X), so a goal with no other clause waits for it.  A vector
against anything that is not a vector fails.  Refused on both models:
a list, a vector of seven or more, an element of X that is a structure
or a string.

The oracle is a Python dictionary keyed by tuples, the pool's meaning
as lockstep_pool.py has it.  A pool of size 4, so keys share slots.
The comparisons run (a reference-model census, 2026-11-23): 40 of two
vectors of 2 or 3 elements: 12 equal; 8 differing in element 0, 8 in
element 1 (e.g. {0,0,7} and {0,1,0}); 12 of different sizes, 4 of them
with the shorter one equal to the longer one's start ({0,6} and
{0,6,1}, {0,0} and {0,0,7}); and 2 of two empty vectors, 12 of a
vector or an atom against the empty vector, 2 of an atom against a
vector.  No pair differing only in element 2 is compared.  The
last request's key has an unbound element: the pool waits for it
until the bench binds it, but in its hash, before any X = Y, so an
unbound element reaching wait_value is NOT run.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv, the
vector branch of deref2 and rules pv1..pv4), each run alone
(bsv/run_pimm_lockstep.sh pvec) and restored from a copy, 2026-11-23;
each first difference is the clause chosen after an X = Y (I 13453 or
I 13259 against I 13440 or I 13244):
  elements compared by value only (an atom = an integer)   line 6968
  only the first element compared                          line 4875
  the sizes not compared                                   line 8422
  X's element compared with itself, not Y's                line 4875
Before the colliding keys were added (17 requests) the second and third
of these were NOT caught: the test was made to catch them.

Re-pinned for the merger timing change (2026-11-24, docs/
pimm_semantics.md merge: a woken goal of merge_in goes on the
merger's list, taken before the ready queue), 12869 -> 12892 trace
lines, both models identical and all 22 answers unchanged; the line
numbers of the injections above are as observed before it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=3, lines=12892, answers=22)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731


def requests(A):
    return [
        ('put', (I(0), I(0), I(0)), [I(100), None]),
        ('put', (I(0), I(6), I(0)), [I(200), None]),
        ('put', (I(0), I(0), I(0)), [I(101), None]),        # the same key
        # keys that share a slot with others differing after element 0
        # (found by a census of the comparisons the pool makes)
        ('put', (I(0), I(0), I(7)), [I(300), None]),
        ('empty', (I(0), I(0), I(7)), [None]),
        ('put', (I(0), I(6)), [I(302), None]),
        ('put', (I(1), I(0), I(0)), [I(303), None]),
        ('put', (I(0), I(1), I(0)), [I(304), None]),
        ('put', (I(0), I(0)), [I(5), None]),                # a shorter one
        ('put', (A('normal'), I(0), I(0)), [I(9), None]),
        ('put', (I(A('normal')[1]), I(0), I(0)), [I(10), None]),   # an integer, not the atom
        ('put', A('normal'), [I(7), None]),                 # an atom among vector keys
        ('empty', (I(0), I(6), I(0)), [None]),
        ('get_if_any', (I(0), I(6), I(1)), [None]),         # the last element differs
        ('get_if_any', (I(0), I(6), I(0)), [None]),
        ('empty', (I(0), I(6), I(0)), [None]),
        ('get_and_put', (A('normal'), I(0), I(0)), [None, I(19)]),
        ('get_if_any', (), [None]),                         # the empty vector
        ('put', (), [I(1), None]),
        ('get_if_any_and_put', (), [None, I(2)]),
        ('put', ('var', I(0), I(0)), [I(102), None]),       # waits for its first element
        ('get_all', None, [None]),
    ]


def shown(c):
    return c[1] if c[0] == pimm.INT else ('atom', c[1])


def key_of(k):
    if k is None:
        return None
    if isinstance(k, tuple) and (not k or isinstance(k[0], tuple) or k[0] == 'var'):
        return tuple(I(0) if e == 'var' else e for e in k)   # the var is bound to 0
    return k


def expected(reqs, sym):
    def term(c):
        if isinstance(c, tuple) and (not c or isinstance(c[0], tuple)):
            return tuple(term(e) for e in c)
        return c[1] if c[0] == pimm.INT else sym[c[1]]

    pool, out = {}, []
    for name, k, args in reqs:
        k = key_of(k)
        if name == 'put':
            out.append((term(pool[k]),) if k in pool else ())
            pool[k] = args[0]
        elif name == 'empty':
            out.append('no' if k in pool else 'yes')
        elif name == 'get_and_put':
            out.append(term(pool[k]))
            pool[k] = args[1]
        elif name == 'get_if_any_and_put':
            out.append((term(pool[k]),) if k in pool else ())
            pool[k] = args[1]
        elif name == 'get_if_any':
            out.append((term(pool.pop(k)),) if k in pool else ())
        else:
            out.append(sorted(((term(kk), term(v)) for kk, v in pool.items()), key=str))
            pool = {}
    return out


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    reqs = requests(A)
    pc = pimm.predicate(im, 'ipl_pool', 'keyed_set/2')
    s = driver.Script()
    s.label('vector keys')
    s.newvar(0)
    s.arg(1, 0)
    s.argc(2, I(4))
    s.spawn(pc, 2)
    s.run()
    late = None
    for name, k, args in reqs:
        # the stream's tail is slot 0; the key in slot 4 (its elements
        # in 1..3), the request in 11.., the list cell in 9, 10
        if k is None:
            req = [A(name)] + args
        elif isinstance(k, tuple) and not k:
            req = [A(name), (pimm.VECT0, 0)] + args           # {}: no cells
        elif isinstance(k, tuple) and (isinstance(k[0], tuple) or k[0] == 'var'):
            s.vector(4, 1, [None if e == 'var' else e for e in k])
            if k[0] == 'var':
                late = 1
            req = [A(name), ('slot', 4)] + args
        else:
            req = [A(name), k] + args
        s.vector(5, 11, req)
        s.cons(6, 9, ('slot', 5), None)
        s.unify(0, 6)
        outs = [11 + i for i, a in enumerate(req) if a is None]
        s.run()
        if late is not None:
            s.label('the key\'s element bound')
            s.unifyc(late, I(0))
            s.run()
            late = None
        for o in outs:
            s.out(o)
        s.live()
        s.setslot(0, s.live_slot[10])
    s.label('the stream closed')
    s.unifyc(0, (pimm.ATOM, 0))
    s.run()
    return s, expected(reqs, im.sym)


def check(s, m, want):
    got = [w for _label, w in s.outs]
    bad, n = [], 0
    if len(got) != len(want):
        bad.append(('answers', len(got), len(want)))
    for i, (w, e) in enumerate(zip(got, want)):
        n += 1
        d = m.deref(w)
        t = None if m.unbound(d) else m.term(d)
        if isinstance(e, list):
            t = sorted(t, key=str) if isinstance(t, list) else t
            e = sorted([tuple(p) for p in e], key=str)
        if t != e:
            bad.append((i, t, e))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad, n


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        n = 0
        for _what, lines in s.play():
            n += len(lines)
        bad, k = check(s, s.machine, want)
        print(bad, n, k, len(s.outs))
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep pvec',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, n = check(s, m, want)
    if bad or n != PINNED['answers']:
        print('pimm lockstep pvec: FAIL %d answers, %r' % (n, bad[:3]))
        return 1
    print('pimm lockstep pvec: PASS (the guard X = Y on vector keys under ipl_pool:keyed_set/2 '
          'on the Bluespec core, %d trace lines identical to the reference model: %d answers '
          'as a dictionary gives them; a key with an unbound element waited for)'
          % (s.counts['lines'], n))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
