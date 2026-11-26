#!/usr/bin/env python3
"""Rung M1 (docs/multi_pe.md): PIMOS's own seqgc and gc on 1, 2, 4 PEs.

    python3 ref/pimm/m1_gc.py            the check; ends `m1 gc: PASS`

The reference model only (pimm_pe.py; the core is one PE, rung M7).
The code is PIMOS's, compiled: modules seqgc (33) and gc (22) of
pimm_shell360E.sav, loaded by ipl_loader:load/4 as lockstep_link.py
loads a file (the file's link is abnormal, it calls modules it does
not hold; seqgc and gc call none, asm/unlsav.py), found as
lockstep_xmod.py finds a loaded module (the descriptor cells in load
order against asm/unlsav.py's reading of the file).  The loaded
machine is copied to every PE (OURS, docs/multi_pe.md 3).  Then
seqgc:go/0 or gc:go/0 is spawned as a goal of the root on node c, and
the system run until no PE has a goal and no message is in flight.

The oracle is the source (pimos/src/shell/utils/seqgc.kl1, gc.kl1,
HELD-SOURCE), on N nodes from node c.  What it fixes is the order of
the collect_garbage guards (the requests, `ask` below); the collection
itself is made at the PE's next goal switch (pimm.py, INFERENCE, R7G),
so its place among other PEs' events is the model's, and only its
count is checked (one per node).
  seqgc:go/0  gcLoopSeq(0,0,N,1,c): one node a round, the round over
              when the merger's output is [] (waitGcLoopSeq/6); a node
              other than c gets gcCall(M)@node(PE), whose guard asks,
              and proceedGcCall(M) binds M = [] (a %unify home); c is
              skipped in its round and asks last (gcLoopSeq's first
              clause, gcCall@node(c)).  So: requests in the order 0, 1,
              .., N-1 without c, then c; N-1 %throw_goal, N-1 %unify.
  gc:go/0     gcLoop/4 sends gcCall(M1)@node(PE) to every node but c at
              once, each M1 a merger input; c asks when the merger's
              output is [] (gcCall/2).  So: one request per node, c's
              after every %unify was sent; N-1 throws, N-1 %unify.  The
              order of the other nodes' requests is not fixed by the
              source and is not checked.
Each case under two schedules (quota 1 and 1,000,000 goal switches a
turn; pimm_pe.System.run): the checks must hold under both, and the
requests seqgc orders and the message counts must be the same under
both (so what is checked is the program's, not the scheduler's).  The
reduction counts are printed, not checked: they differ by schedule, as
KL1 allows (seqgc on 2 PEs from node 0: 23 under quota 1, 25 under the
long quota, where node 0 runs waitGcLoopSeq/6 before the %unify is in
and it suspends once and is resumed).  At the end: no goal left on
any PE, suspended or ready, and no export or import entry left.

Observed fault injections (each on a private copy of pimm_pe.py, this
whole script run, 2026-11-26; docs/multi_pe.md 5):
  every @node made local      every N>1 case FAILS, both quotas (order,
                              one request/collection per node, messages
                              {0: 0, 9: 0}); N=1 passes
  current_node's number 0     c!=0 cases (2/1, 4/2, both programs) raise
                              KeyError (e.g. 3762438966): a collection
                              drops the unrooted loaded code; c=0 pass
  current_node's total 1      every N>1 case FAILS
  no %unify sent              every N>1 case FAILS, both quotas; home
                              left with live exports, suspended goals
  %unify without waking       PASS under quota 1; under 1,000,000 every
                              N>1 case FAILS and the schedules differ
  no import (raw word)        Unimplemented: a second unification of
                              external cell (50, 16777217)
"""
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import pimm_pe  # noqa: E402
import lockstep_link as link  # noqa: E402
import lockstep_modc as modc  # noqa: E402
import lockstep_xmod as xmod  # noqa: E402

FILE = 'pimm_shell360E.sav'
CASES = [(1, 0), (2, 0), (2, 1), (4, 0), (4, 2)]      # (N, the home node c)
QUOTAS = (1, 1000000)


def loaded_machine():
    """The machine with FILE loaded, and the code of seqgc:go/0, gc:go/0.
    M1_CACHE=PATH keeps the loaded machine between runs (a scratch
    file; not part of the check)."""
    cache = os.environ.get('M1_CACHE')
    if cache and os.path.exists(cache):
        with open(cache, 'rb') as f:
            return pickle.load(f)
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    link.one(s, im, names, 'load', [FILE])
    m = s.live()
    m.tr = None
    mods = xmod.loaded(m)
    fm = modc.modules(FILE)
    assert len(fm) == len(mods), (len(fm), len(mods))
    code = {}
    for name in ('seqgc', 'gc'):
        i = [k for k, mod in enumerate(fm) if mod['name'] == name]
        assert len(i) == 1, (name, i)
        hits = [loc for pn, ar, loc in fm[i[0]]['preds'] if pn == 'go' and ar == 0]
        assert len(hits) == 1, (name, fm[i[0]]['preds'])
        code[name] = mods[i[0]] + hits[0] - m.load
        assert m.opname(code[name]) is not None
    out = (m, code)
    if cache:
        with open(cache, 'wb') as f:
            f.write(pimm_pe.dumps(out))
    return out


def play(m, pc, n, c, quota):
    system = pimm_pe.System(m, n)
    system.pes[c].spawn(pc, [])
    system.run(quota)
    return system


def expected(prog, n, c):
    """The requests in the source's order, or None where it fixes none."""
    if prog == 'seqgc':
        return [k for k in range(n) if k != c] + [c]
    return None


def check(prog, n, c, system):
    bad = []
    log = system.log
    asks = [e[1] for e in log if e[0] == 'ask']
    throws = [e[3] for e in log if e[0] == 'send' and e[1] == pimm_pe.M_THROW]
    want = expected(prog, n, c)
    if want is not None and asks != want:
        bad.append(('request order', asks, want))
    if want is not None and throws != want[:-1]:
        bad.append(('throw order', throws, want[:-1]))
    if sorted(asks) != list(range(n)) or sorted(throws) != [k for k in range(n) if k != c]:
        bad.append(('one request per node, one throw to each other node', asks, throws))
    if [pe.collections for pe in system.pes] != [1] * n:
        bad.append(('one collection per node', [pe.collections for pe in system.pes]))
    last_unify = max([i for i, e in enumerate(log) if e[0] == 'send'
                      and e[1] == pimm_pe.M_UNIFY], default=-1)
    home = [i for i, e in enumerate(log) if e == ('ask', c)]
    if not home or home[0] < last_unify:
        bad.append(('node c asks after every %unify', log))
    sent = {k: system.sent.get(k, 0) for k in (pimm_pe.M_THROW, pimm_pe.M_UNIFY)}
    if sent != {pimm_pe.M_THROW: n - 1, pimm_pe.M_UNIFY: n - 1}:
        bad.append(('messages', sent))
    for pe in system.pes:
        if pe.nsusp or pe.exports or pe.imports or pe.rq or pe.mq or pe.mwh:
            bad.append(('PE %d left' % pe.pe, pe.nsusp, pe.exports, pe.imports))
    return bad, asks, sent, [pe.reductions for pe in system.pes]


def main(argv):
    m, code = loaded_machine()
    base = m.reductions
    blob = pimm_pe.dumps(m)
    bad, rows = [], []
    for prog in ('seqgc', 'gc'):
        for n, c in CASES:
            seen = []
            for q in QUOTAS:
                system = play(blob, code[prog], n, c, q)
                b, asks, sent, red = check(prog, n, c, system)
                red = [r - base for r in red]
                bad += [(prog, n, c, q) + x for x in b]
                seen.append((asks if expected(prog, n, c) else sorted(asks), sent))
                rows.append((prog, n, c, q, asks, sent[0], sent[9], red))
            if seen[0] != seen[1]:
                bad.append((prog, n, c, 'the two schedules differ', seen))
    for r in rows:
        print('%-5s N=%d c=%d quota=%-7d asks %-12s throw %d unify %d  reductions %s' % r)
    for b in bad:
        print('FAIL', b)
    print('m1 gc: %s (%d runs)' % ('FAIL' if bad else 'PASS', len(rows)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
