#!/usr/bin/env python3
"""Lockstep: the built-in merger, under the IPL's keyed pool.

    python3 ref/pimm/lockstep_pool.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_pool.py compare

ipl_pool:keyed_set(Stream, Size) is the table the IPL keeps atom
numbers in (ipl_loader:decode_atom/3, atom_table/1).  Its first act
(object code, asm/kl1decomp.py):

    wait_table_size_set(A, B) :- wait(B) |
        new_vector(B, C), merge(D, E), A = E, F := B - 1,
        keyed_set(D, F, 0, 0, C).

which is merge(A, D) in the source: the compiler gives the built-in
its OUTPUT stream first and receives the input second
(library/compiler/blt.kl1, active_builtin(merge(X1,X2))).  So every
request to the pool goes through a merger.

merge is new on both models, and it is NOT the machine's merger.  On
PIM/m a merger input is a cell of its own tag (MGHOK) pointing at a
merger record {output variable}{number of inputs} (TR-466 3.3), and
the merger acts when that cell is unified.  Here the input is a
variable with a GOAL waiting on it, whose code is a stub of one
instruction, merge_in (asm/pimm_stubs.py; 22:00, an opcode with no
entry in the firmware's decode table, refused anywhere else), and the
record is {output}{count}.  The logic is the manual's (merge([A|I],O)
:- O=[A|NO], merge(I,NO); merge([],O) :- O=[]); the output appears
after a goal switch rather than at the unification.  A vector on the
input (more inputs) is refused; so is anything else but a list, []
or a variable (the machine's illegal_merger_input).

Also new: put_vector_0 (the empty vector).

What is run.  A pool of size 4 (so the keys 1 and 5, and the atoms,
share slots), twice: with each request given after the pool has
started, and with the whole stream bound before the call.  The
oracle is a Python dictionary with the pool's meaning as its object
code gives it and the answers show it:
    put(K, V, Old)                 Old = {} or {the old value}
    get_if_any(K, X)               X = {} or {V}; V is REMOVED
    empty(K, YesNo)
    get_and_put(K, Old, New)       K must be there
    get_if_any_and_put(K, X, New)  X = {} or {V}
    get_all(L)                     every {K, V}, any order; the pool
                                   is empty afterwards
Then the stream is closed and no goal may be left waiting.

Observed fault injections into the Bluespec, 2026-11-23, each FAILed
where shown and was restored:
All in the first part, at the trace line shown:
  the element not copied              151: the new list cell's car
  the cdr not followed                154: R 0 nil for the rest
  the output never closed             5055: the [] not written
  the old output variable kept        153: the record's output
  merge returns the output as input   87: R 3
  put_vector_0 makes []               309: R 0

Re-pinned for the merger timing change (2026-11-24, docs/
pimm_semantics.md merge: a woken goal of merge_in goes on the
merger's list, taken before the ready queue), 9113 -> 9134 trace
lines, both models identical and all 38 answers unchanged: one input,
so the order of the requests cannot change; the goals run in another
order and each pickup that splices the list writes one link more.
(lockstep_merge.py is the test of the order itself.)

Not caught: merge_in accepted outside its stub (no code holds it),
and the refusals (a vector or a non-stream on the input, an output
that is not a variable) are not run.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=2, lines=9134, answers=38)


def requests(names):
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    I = lambda v: (pimm.INT, v & 0xffffffff)       # noqa: E731
    return [
        ('put', [I(1), I(100), None]),
        ('put', [I(5), I(500), None]),             # the slot of 1
        ('put', [I(1), I(101), None]),
        ('put', [A('normal'), I(7), None]),
        ('put', [A('module'), A('normal'), None]),
        ('empty', [I(1), None]),
        ('empty', [I(2), None]),
        ('empty', [A('module'), None]),
        ('get_and_put', [I(5), None, I(501)]),
        ('get_if_any_and_put', [I(7), None, I(700)]),
        ('get_if_any_and_put', [I(7), None, I(701)]),
        ('get_if_any', [I(5), None]),
        ('get_if_any', [I(5), None]),
        ('get_if_any', [A('normal'), None]),
        ('empty', [I(5), None]),
        ('get_all', [None]),
        ('empty', [I(1), None]),
        ('put', [I(1), I(1), None]),
        ('get_all', [None]),
    ]


def expected(reqs, sym):
    def shown(c):
        return c[1] if c[0] == pimm.INT else sym[c[1]]

    # the answers, in order, as Machine.term shows them; get_all's as
    # a sorted list
    pool, out = {}, []
    for name, args in reqs:
        k = args[0] if args[0] is None else shown(args[0])
        if name == 'put':
            out.append((pool[k],) if k in pool else ())
            pool[k] = shown(args[1])
        elif name == 'empty':
            out.append('no' if k in pool else 'yes')
        elif name == 'get_and_put':
            out.append(pool[k])
            pool[k] = shown(args[2])
        elif name == 'get_if_any_and_put':
            out.append((pool[k],) if k in pool else ())
            pool[k] = shown(args[2])
        elif name == 'get_if_any':
            out.append((pool.pop(k),) if k in pool else ())
        else:
            out.append(sorted(pool.items(), key=str))
            pool = {}
    return out


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    reqs = requests(names)
    pc = pimm.predicate(im, 'ipl_pool', 'keyed_set/2')
    s = driver.Script()

    def request(name, args):
        # the stream's tail is slot 0; the request in 11.., the cell in 9, 10
        s.vector(5, 11, [A(name)] + args)
        s.cons(6, 9, ('slot', 5), None)
        s.unify(0, 6)
        return [12 + i for i, a in enumerate(args) if a is None]

    s.label('requests after the call')
    s.newvar(0)
    s.arg(1, 0)
    s.argc(2, (pimm.INT, 4))
    s.spawn(pc, 2)
    s.run()
    for name, args in reqs:
        outs = request(name, args)
        s.run()
        for o in outs:
            s.out(o)
        s.live()
        s.setslot(0, s.live_slot[10])
    s.unifyc(0, (pimm.ATOM, 0))
    s.run()

    s.label('the stream bound before the call')
    s.newvar(0)
    s.setslot(8, (0, 0))
    s.newvar(8)
    s.unify(8, 0)                  # slot 8 keeps the head
    held = []
    for n, (name, args) in enumerate(reqs):
        outs = request(name, args)
        # an answer's variable must outlive the slots: keep it in a
        # list built in slots 1..4?  No: read it now, it is a variable
        # cell that stays where it is
        s.live()
        held.append([s.live_slot[o] for o in outs])
        s.setslot(0, s.live_slot[10])
    s.unifyc(0, (pimm.ATOM, 0))
    s.arg(1, 8)
    s.argc(2, (pimm.INT, 4))
    s.spawn(pc, 2)
    s.run()
    for cells in held:
        for c in cells:
            s.setslot(7, c)
            s.out(7)
    return s, expected(reqs, im.sym)


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad, n = [], 0
    for label, ws in got.items():
        if len(ws) != len(want):
            bad.append((label, 'answers', len(ws)))
            continue
        for i, (w, e) in enumerate(zip(ws, want)):
            n += 1
            d = m.deref(w)
            t = None if m.unbound(d) else m.term(d)
            if isinstance(e, list):
                t = sorted(t, key=str) if isinstance(t, list) else t
                e = sorted([tuple(p) for p in e], key=str)
            if t != e:
                bad.append((label, i, t, e))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad, n


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep pool',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, n = check(s, m, want)
    if bad or n != PINNED['answers']:
        print('pimm lockstep pool: FAIL %d answers, %r' % (n, bad[:3]))
        return 1
    print('pimm lockstep pool: PASS (the built-in merger under ipl_pool:keyed_set/2 on the '
          'Bluespec core, %d trace lines identical to the reference model: %d answers of a '
          'pool of colliding keys as a dictionary gives them, the stream fed after the call '
          'and bound before it; no goal left waiting)' % (s.counts['lines'], n))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
