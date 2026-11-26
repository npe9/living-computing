#!/usr/bin/env python3
"""Rung M3 (docs/multi_pe.md): the tables as the machine had them.

    python3 ref/pimm/m3_gc.py              the check; ends `m3 gc: PASS`

The reference model only (pimm_pe.py).  White and black export entries
by the path's MRB, WEC on black IDs, the white-path pass-on of an ID,
one import per black ID, %release with WEC, and a collection on a PE
with live tables: the export table a root, the import table weak (an
import whose external cell is not reached is released).

The programs are PIMOS's heap monitors, as in m2_read.py (same file,
same loading, same oracle for the answers), now with every PE
collected at quiescence after the start and after each of the three
rounds (the bench asks; OURS that it is at quiescence, so the
messages a collection sends do not depend on the quota).  Then the
bench lets go of the stream and the answers, every PE is collected
again, twice, and what is left is pinned: the monitors' own goals,
which wait on each other across PEs through the export tables, are
never reclaimed (the tables are roots: a cycle across PEs is not
collected, as with any reference count; TR-390 7).

Since the retagging (TM-1044 s9-msg-kl1data.tex 269-300): retagged,
every exported variable still unbound is EUNDF/EHOOK and every such
cell is one an entry holds, also at every quiescence.

Checked at every quiescence, on (N, c) = (1,0), (2,0), (2,1), (4,0),
(4,3), quota 1 and 1,000,000:
  answers   each round's answer is each node's own heap (m2_read.py);
  WEC       for each black entry, its WEC plus the WEC of every import
            of its ID is 0, and its WEC is negative (TM-1044 9: the
            sum of the WEC over the table, the messages and the
            imports is zero; no message is in flight at quiescence);
  named     every export entry is named by an import of some PE or is
            the reply entry of a pending read; a white one by exactly
            one import (each white ID has one holder);
  cells     after a collection, the external cells in a PE's heap and
            its import entries correspond one to one (a cell copied
            twice, or a stale one, fails);
  fixpoint  a second round of collections releases nothing;
  schedule  the message counts and what is left are the same under
            both quotas.
Bench drain (OURS, h_monitor's out/2 as in m2_read.py's `wait`): the
bench lets go of P; PE 0's collection releases its two imports of PE
1, PE 1's entries are freed, and PE 1's collection then finds out1's
goal unreachable: every table empty, no goal left.

Also bench black (reverse([], X, X) with X on an MRB-on path: one
black entry, two units, one import of them on PE 1, released with
both by PE 1's collection), via (a black ID passed on with all its
WEC by PE 1 to a third PE), share (reverse(X, X)@node(N-2) by way
of PE 1, X marked twice: one import with its flag set, both
references passed on with half the WEC, the import kept) and the two
indirect exports as units.
Every M3 path pimm_pe.py marks must run (PATHS).

Observed fault injections, 2026-11-26, each on a private copy of
pimm_pe.py, this check and m2_read.py run: docs/multi_pe.md 5 (M3)
has the table.  Caught by checks here: a dead import dropped without
%release (56), imports as roots (25), nsusp not recounted (16), %read
keeping or not giving back WEC (6312, 4040), %unify's WEC not given
back (848), a white or black ID passed on with its import kept (8,
8), a white ID come home kept (4).  Caught by a raise: an import's
cell not moved, no black entry reused, a black ID imported twice, WEC
not halved, the import flag ignored, the cell left external after
%answer_value.  Not caught: external cells not in VAR_TAGS (not
reachable).  Never fired: cells, fixpoint (vacuous for the monitors,
which release nothing; drain's releases by round is the real one),
a white entry held twice, an import with no WEC, a reply entry
imported, the two schedules differ.
The retagging: no retag, 678 FAIL lines here (exported variable not
retagged), m2 PASS; no untag, 4 here (black: a cell no entry holds);
EHOOK bound without waking, 73 in m2 (monitors, chain, alias, paths),
and here raises `gc: the to-space is full`.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pimm  # noqa: E402
import pimm_pe  # noqa: E402
import m2_read  # noqa: E402
from pimm import INT, LIST  # noqa: E402
from pimm_layout import HEAP  # noqa: E402

CASES = [(1, 0), (2, 0), (2, 1), (4, 0), (4, 3)]
# observed 2026-11-26 and pinned: messages, R, what is left
VIA = {
    # back to PE 0, which runs reverse with its own L and R
    2: ({0: 2}, [3, 2, 1], [(0, 0, 0, 0, 0), (0, 0, 0, 0, 0)]),
    # on to PE 2, which reads L from PE 0 (3 conses and []); R's
    # binding comes home with its rest exported by PE 2
    4: ({0: 2, 6: 3, 7: 3, 8: 3, 9: 1}, ('|', 3, None),
        [(0, 1, 0, 0, 0), (0, 0, 0, 0, 0), (1, 0, 0, 0, 0), (0, 0, 0, 0, 0)]),
}
# messages; what is left before X = [] (PE 1 keeps its import)
SHARE = {
    # back to PE 0: both IDs come home with half the WEC each; reverse
    # waits on X there; PE 1 keeps its import (its collection releases
    # it with the rest)
    2: ({0: 2, 8: 1}, [(1, 0, 0, 1, 0), (0, 1, 0, 0, 0)]),
    # on to PE 2, which imports the ID once (twice arrived) and reads
    # it; the answer's release and PE 1's at its collection
    4: ({0: 2, 6: 1, 7: 1, 8: 2},
        [(1, 0, 0, 1, 0), (0, 1, 0, 0, 0), (1, 1, 1, 1, 0), (0, 0, 0, 0, 0)]),
}
# the monitors' tables at the end, let go: (program, N) -> the home's
# row, each other PE's
LEFT = {
    ('h', 1): ((0, 0, 0, 0, 0), None),
    ('h', 2): ((1, 0, 0, 1, 0), (1, 1, 1, 1, 0)),
    ('h', 4): ((3, 0, 0, 3, 0), (1, 1, 1, 1, 0)),
    ('x', 1): ((0, 0, 0, 0, 0), None),
    ('x', 2): ((1, 1, 0, 3, 0), (2, 1, 1, 1, 0)),
    ('x', 4): ((1, 3, 0, 5, 0), (2, 1, 1, 1, 0)),
}
# the M3 paths of pimm_pe.py (PE.ran) this check must run; the reading
# ones are m2_read.py's
PATHS = ('import released at a collection', 'indirect export', 'multi-import: half',
         'indirect export, no WEC to give', 'black ID passed on, all its WEC',
         'black ID passed on, half its WEC', 'black ID imported again', 'black entry again',
         'black entry reclaimed', 'black ID came home', 'white ID passed on',
         'white ID came home')
QUOTAS = (1, 1000000)


def wec_check(system):
    bad = []
    held = {}
    for pe in system.pes:
        for ent in pe.imports.values():
            if ent['black']:
                held[ent['id']] = held.get(ent['id'], 0) + ent['wec']
                if ent['wec'] <= 0:
                    bad.append(('an import with no WEC', pe.pe, ent['id'], ent['wec']))
    for pe in system.pes:
        for e, w in pe.wec.items():
            ident = pimm_pe.ext_id(pe.pe, e)
            if w >= 0 or w + held.get(ident, 0) != 0:
                bad.append(('WEC of entry %d of PE %d' % (e, pe.pe), w, held.get(ident, 0)))
    return bad


def named(system):
    bad = []
    holders = {}
    for pe in system.pes:
        for ent in pe.imports.values():
            holders[ent['id']] = holders.get(ent['id'], 0) + 1
    for pe in system.pes:
        for e in pe.exports:
            ident = pimm_pe.ext_id(pe.pe, e)
            h = holders.get(ident, 0)
            if e in pe.reading:
                if h:
                    bad.append(('a reply entry imported', pe.pe, e))
            elif h == 0:
                bad.append(('entry %d of PE %d named by no import' % (e, pe.pe)))
            elif e not in pe.wec and h != 1:
                bad.append(('white entry %d of PE %d held %d times' % (e, pe.pe, h)))
    return bad


def cells(pe):
    """The external cells in pe's heap against its import table."""
    lo = getattr(pe, 'heap_lo', None) or pe.load + HEAP
    found = {}
    for a in range(lo, pe.hp):
        c = dict.get(pe.mem, a)
        if c is not None and c[0] in pimm_pe.EX_TAGS:
            found.setdefault(c[1], []).append(a)
    bad = []
    for imp, ent in pe.imports.items():
        if found.get(imp) != [ent['cell']]:
            bad.append(('import %d of PE %d: its cell %x, cells %r'
                        % (imp, pe.pe, ent['cell'], found.get(imp))))
    for imp in found:
        if imp not in pe.imports:
            bad.append(('a cell of a dropped import %d on PE %d' % (imp, pe.pe), found[imp]))
    return bad


def retagged(system):
    """Every exported variable still unbound is EUNDF or EHOOK, and
    every EUNDF or EHOOK cell in a heap is one an entry holds."""
    bad = []
    for pe in system.pes:
        held = set()
        for e, w in pe.exports.items():
            if w[0] & ~1 == pimm.REF:
                c = pe.mem[w[1]]
                held.add(w[1])
                if c[0] & ~1 in (pimm.UNDF, pimm.HOOK):
                    bad.append(('exported variable not retagged', pe.pe, e, c))
        lo = getattr(pe, 'heap_lo', None) or pe.load + HEAP
        for a in range(lo, pe.hp):
            c = dict.get(pe.mem, a)
            if c is not None and c[0] in pimm_pe.E_TAGS and a not in held:
                bad.append(('an EUNDF/EHOOK cell no entry holds', pe.pe, a))
    return bad


def quiet(system):
    return (wec_check(system) + named(system) + retagged(system)
            + m2_read.consistent(system))


def collect_all(system, quota):
    """Every PE collected, PE 0 first, then the releases delivered; the
    external cells checked after each collection."""
    bad = []
    before = dict(system.sent)
    for pe in system.pes:
        pe.collect()
        bad += cells(pe)
    system.run(quota)
    released = system.sent.get(pimm_pe.M_RELEASE, 0) - before.get(pimm_pe.M_RELEASE, 0)
    return bad, released


def monitor(blob, info, prog, n, c, quota):
    p = info[prog]
    system = m2_read.new_system(blob, n)
    home = system.pes[c]
    repo, t = home.new_var(), home.new_var()
    home.roots['repo'], home.roots['t'] = repo, t
    home.spawn(p['entry'][('throw2profile2process', 3)], [(INT, n - 1), repo, t])
    system.run(quota)
    bad, rel = [], []
    b, r = collect_all(system, quota)
    bad += b + quiet(system)
    rel.append(r)
    for _ in range(m2_read.ROUNDS):
        home.roots['t'] = m2_read.push(home, home.roots['t'], p['atoms']['profile'])
        system.run(quota)
        bad += quiet(system)
        b, r = collect_all(system, quota)
        bad += b + quiet(system)
        rel.append(r)
    b, r = collect_all(system, quota)
    if r:
        bad.append(('fixpoint: a second collection released %d' % r,))
    bad += b
    bad += m2_read.check_monitor(system, home.roots['repo'], n, c)
    held = tables(system)
    # let go: the bench no longer holds the stream or the answers
    home.roots.clear()
    for _ in range(2):
        b, r = collect_all(system, quota)
        bad += b + quiet(system)
        rel.append(r)
    return system, bad, rel, held


def tables(system):
    return m2_read.tables(system)


def bench_drain(blob, info, n, quota):
    eo = info['h']['entry'][('out', 2)]
    system = m2_read.new_system(blob, n)
    p0, p1 = system.pes[0], system.pes[1]
    s = p0.make_string(16, [1, 2, 3])
    c = p0.alloc(2)
    p0.mem[c], p0.mem[c + 1] = s, pimm.NIL
    pm = p0.new_var()
    p0.roots['p'] = pm
    p0.throw(1, eo, [(LIST, c), pm])
    system.run(quota)
    bad = quiet(system)
    before = tables(system)
    b, r1 = collect_all(system, quota)                # P still held: nothing released
    bad += b
    del p0.roots['p']
    b, r2 = collect_all(system, quota)                # PE 0 releases, PE 1 frees
    bad += b
    b, r3 = collect_all(system, quota)                # PE 1 finds out1 unreachable
    bad += b + quiet(system)
    want_before = [(0, 2, 0, 0, 0), (2, 0, 0, 1, 0)] + [(0, 0, 0, 0, 0)] * (n - 2)
    if before != want_before:
        bad.append(('drain: before', before, want_before))
    if (r1, r2, r3) != (0, 2, 0):
        bad.append(('drain: releases by round', (r1, r2, r3), (0, 2, 0)))
    if tables(system) != [(0, 0, 0, 0, 0)] * n:
        bad.append(('drain: every table empty, no goal', tables(system)))
    return bad, dict(sorted(system.sent.items()))


def bench_black(blob, info, n, quota):
    """black: reverse([], X, X) thrown to PE 1, X of PE 0 on an MRB-on
    path (marked, as a compiled body marks a variable it passes twice):
    one black entry gives two IDs (WEC 2 units); PE 1 imports the ID
    once, with both units; X = X there is the same cell, nothing sent;
    PE 1's collection finds the import unreachable and releases it with
    all its WEC; PE 0's entry is reclaimed at 0."""
    e3 = info['h']['entry'][('reverse', 3)]
    system = m2_read.new_system(blob, n)
    p0, p1 = system.pes[0], system.pes[1]
    x = p0.new_var()
    p0.roots['x'] = x
    p0.throw(1, e3, [pimm.NIL, pimm.marked(x), pimm.marked(x)])
    bad = []
    got = [(e, w) for e, w in p0.wec.items()]
    if [w for _e, w in got] != [-2 * pimm_pe.WEC_UNIT]:
        bad.append(('one black entry, two units given', got))
    system.run(quota)
    imps = [(ent['black'], ent['wec']) for ent in p1.imports.values()]
    if imps != [(True, 2 * pimm_pe.WEC_UNIT)]:
        bad.append(('PE 1: one black import, two units', imps))
    bad += quiet(system)
    b, r = collect_all(system, quota)
    bad += b + quiet(system)
    if r != 1:
        bad.append(('one release', r))
    if tables(system) != [(0, 0, 0, 0, 0)] * n:
        bad.append(('every table empty', tables(system)))
    if p0.term(p0.roots['x']) is not None:
        bad.append(('X unbound', p0.term(p0.roots['x'])))
    return bad, dict(sorted(system.sent.items()))


def bench_via(blob, info, n, quota):
    """via: m2_read.py's third with L on an MRB-on path: PE 1 imports a
    black ID and passes it on to PE N-2 on its own MRB-off path with
    all its WEC; that PE reads L from PE 0 itself."""
    e2 = info['h']['entry'][('reverse', 2)]
    system = m2_read.new_system(blob, n)
    p0 = system.pes[0]
    lst = pimm.NIL
    for v in range(3, 0, -1):
        c = p0.alloc(2)
        p0.mem[c], p0.mem[c + 1] = (INT, v), lst
        lst = (LIST, c)
    r = p0.new_var()
    p0.roots['r'] = r
    p0.throw(1, p0.stubs['$to_processor2']['addr'],
             [pimm.marked(lst), r, (INT, n - 2), (INT, p0.load + e2)])
    system.run(quota)
    bad = quiet(system)
    got = p0.term(p0.roots['r'])
    sent = dict(sorted(system.sent.items()))
    msgs, term, left = VIA[n]
    if (sent, got, tables(system)) != (msgs, term, left):
        bad.append(('via', sent, got, tables(system)))
    return bad, (sent, got, tables(system))


def bench_share(blob, info, n, quota):
    """share: the to_processor goal of reverse(X, X)@node(N-2) thrown
    to PE 1 with X of PE 0 on a marked path twice: PE 1 imports the
    black ID once (the second arrival adds its WEC and sets the import
    flag), then passes both references on, each with half the WEC and
    the import kept (an ID imported more than once is never given up
    by one of its references); then X = [] on PE 0, and every PE is
    collected."""
    e2 = info['h']['entry'][('reverse', 2)]
    system = m2_read.new_system(blob, n)
    p0, p1 = system.pes[0], system.pes[1]
    x = p0.new_var()
    p0.roots['x'] = x
    p0.throw(1, p0.stubs['$to_processor2']['addr'],
             [pimm.marked(x), pimm.marked(x), (INT, n - 2), (INT, p0.load + e2)])
    system.run(quota)
    bad = quiet(system)
    mid = tables(system)
    p0.unify(p0.roots['x'], pimm.NIL)
    system.run(quota)
    bad += quiet(system)
    b, r = collect_all(system, quota)
    bad += b + quiet(system)
    sent = dict(sorted(system.sent.items()))
    msgs, want_mid = SHARE[n]
    if (sent, mid, tables(system)) != (msgs, want_mid, [(0, 0, 0, 0, 0)] * n):
        bad.append(('share', sent, mid, tables(system)))
    return bad, (sent, mid, tables(system))


def check_indirect(blob):
    """The two indirect exports (VPIM f_IndirectExportEX), as units: a
    white import on an MRB-on path, and a black import whose WEC cannot
    be halved.  The words only; no message is sent."""
    bad = []
    system = m2_read.new_system(blob, 3)
    p0, p1 = system.pes[0], system.pes[1]
    x = p0.new_var()
    white = p1.import_id((pimm_pe.EXREF, p0.level0(x, 1)[0][1]))
    out = p1.level0(pimm.marked(white), 2)
    if [w[0] for w in out] != [pimm_pe.EXREFx, INT] or pimm_pe.id_pe(out[0][1]) != 1:
        bad.append(('indirect export of a white import', out))
    blk = p1.import_id((pimm_pe.EXREFx, pimm_pe.ext_id(0, 9)), 1)
    out = p1.level0(pimm.marked(blk), 2)
    if [w[0] for w in out] != [pimm_pe.EXREFx, INT] or pimm_pe.id_pe(out[0][1]) != 1:
        bad.append(('indirect export of a black import with WEC 1', out))
    return bad


def main(argv):
    blob, info = m2_read.loaded()
    bad, rows = [], []
    for prog, _name in m2_read.PROGS:
        for n, c in CASES:
            seen = []
            for q in QUOTAS:
                system, b, rel, held = monitor(blob, info, prog, n, c, q)
                bad += [(prog, n, c, q, x) for x in b]
                sent = dict(sorted(system.sent.items()))
                seen.append((sent, held, tables(system), rel))
                msgs, hrow, orow = m2_read.MONITOR[(prog, n)]
                lh, lo = LEFT[(prog, n)]
                want = (msgs, [hrow if k == c else orow for k in range(n)],
                        [lh if k == c else lo for k in range(n)], [0] * (2 + m2_read.ROUNDS + 1))
                if (sent, held, tables(system), rel) != want:
                    bad.append((prog, n, c, q, ('pinned', (sent, held, tables(system), rel), want)))
                rows.append('%s N=%d c=%d quota=%-7d messages %s  releases by round %s  held %s  left %s'
                            % (prog, n, c, q, sent, rel, held, tables(system)))
            if seen[0] != seen[1]:
                bad.append((prog, n, c, 'the two schedules differ', seen))
    for n in (2, 4):
        for q in QUOTAS:
            b, sent = bench_drain(blob, info, n, q)
            bad += [('drain', n, q, x) for x in b]
            rows.append('drain N=%d quota=%-7d messages %s' % (n, q, sent))
            b, sent = bench_black(blob, info, n, q)
            bad += [('black', n, q, x) for x in b]
            rows.append('black N=%d quota=%-7d messages %s' % (n, q, sent))
            if sent != {0: 1, 8: 1}:
                bad.append(('black', n, q, 'messages', sent))
            b, got = bench_via(blob, info, n, q)
            bad += [('via', n, q, x) for x in b]
            rows.append('via   N=%d quota=%-7d %s' % (n, q, got))
            b, got = bench_share(blob, info, n, q)
            bad += [('share', n, q, x) for x in b]
            rows.append('share N=%d quota=%-7d %s' % (n, q, got))
    bad += [('indirect', x) for x in check_indirect(blob)]
    for r in rows:
        print(r)
    print('paths', m2_read.paths())
    missing = [k for k in PATHS if k not in m2_read.paths()]
    if missing:
        bad.append(('paths that never ran', missing))
    for b in bad:
        print('FAIL', b)
    print('m3 gc: %s (%d runs)' % ('FAIL' if bad else 'PASS', len(rows)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
