#!/usr/bin/env python3
"""Rung M2 (docs/multi_pe.md): reading across PEs, PIMOS's heap monitors.

    python3 ref/pimm/m2_read.py            the check; ends `m2 read: PASS`

The reference model only (pimm_pe.py; the core is one PE, rung M7).

The programs are PIMOS's, compiled: modules h_monitor (101) and
x_h_monitor (107) of pimm_debugger360E.sav, the paragraph profiler's
heap meters (pimos/src/debugger/paragraph/processor/hmonitor.kl1 and
x_hmonitor.kl1, HELD-SOURCE), loaded by ipl_loader:load/4 as
m1_gc.py loads its file.  Neither calls another module.  Each throws
pe_profile/1 (h) or pe_profile/2 (x) to every node 0..MaxNode
(throw_pe_profile, `pe_profile(..)@node(Count)`), and for each
`profile` on its stream TStream asks each node for its heap
(get_heap_size) and collects the answers, node 0 first, as one list
of {Used, UnUsed} vectors:
  h  the home binds each node's stream, [start | RS] then
     [get_ans(Ans) | RS']; the node reads it (%read, a list at level 1
     with a vector at level 0 in it) and unifies Ans with a vector
     (%unify at level 1);
  x  every node reads the one TStream (a variable read by N-1 PEs);
     the node binds its own stream to [get_ans(Ans) | PStream1] (a
     %unify carrying a structure whose elements are exported back),
     and the home reads that list, the vector in it and Ans
     (wait(Ans)), each by message.
The entry is the internal throw_profile_process/3 (MaxNode, Repo,
TStream): the predicates are found by the predicate heads in the
loaded module (PREDH, two cells before each entry, its offset back to
the module) and named by the name cell before it, checked against the
source's predicate order (h 20, x 24).  The bench (OURS) is the timer
the source's msg_timer_control is: it binds TStream to
[profile | T] three times, the system run to quiescence after each.
get_heap_size is OURS in its values (pimm_pe.py), and logged.

The oracle (the source and KL1's semantics): on N nodes from home c,
each of the three answers is a list of N vectors, the k-th equal to
{Used, Size - Used} of PE k's own get_heap_size in that round, and
each PE asked exactly three times; under quota 1 and 1,000,000 the
message counts by kind are the same and so is what is left at the end
(per PE: exports, imports, pending reads, suspended goals; both
pinned per program and N, MONITOR, since rung M3); every
import left refers to a live export entry, and no %release finds a
free entry.  The heap values themselves differ by schedule (they are
the allocation order's), so they are checked against the log only.

Bench cases on h_monitor's reverse/2 and reverse/3 (OURS, the code
PIMOS's), N = 2 and 4, home 0:
  rev    reverse(L, R) thrown to PE 1 with L = [1..6] of PE 0: PE 1
         reads L one cons at a time, R's binding comes home at level 1
         with its rest exported; then reverse(R, RR) on PE 0 reads that
         rest from PE 1: RR = [1..6]; throw 1, read 11, answer 11,
         unify 1, release 11; every table empty at the end.
  home   reverse([], A, B) thrown to PE 1, A and B of PE 0: PE 1's A = B
         sends %unify(A, B's ID), PE 1 passing B's ID on with its import
         (a white path, rung M3), which comes home and is resolved to B
         itself, B's entry done with; then B = 7 on PE 0 gives A = 7;
         every table empty (at M2, before the pass-on, PE 1's import of
         B and PE 0's entry were left).
  chain  reverse(X, R) thrown to PE 1, X of PE 0: PE 1 reads X; then
         X = Y on PE 0 wakes the reply record with X still unbound, and
         it waits again on Y; Y = [] gives R = []; throw, read, answer,
         unify, release one each; every table empty.
  node   rev with the goal waiting for its node: the to_processor goal
         of Goal@node(P), P unbound, made as enqueue_goal_to_processor
         makes it, then P = 1: the same answer and messages as rev.
  third  rev with the to_processor goal of Goal@node(K) thrown to PE 1
         with K = N - 2: on 2 PEs it goes back to PE 0, both IDs come
         home and reverse runs there (throw 2); on 4 it goes on to PE
         2, PE 1 passing the two IDs on (white paths, rung M3): PE 2
         reads L from PE 0 itself (throw 2, read 11, answer 11, unify
         1, release 11); every table empty.  (At M2 PE 1 exported them
         again: 22 reads, and on 2 PEs two entries left.)
  alias  reverse(X, R) thrown to PE 1, which reads X; then on PE 1 a
         new variable Y = X's cell (Y becomes a reference to it) and
         Y = [] (%unify with the read pending): X = R = [] on PE 0;
         throw 1, read 1, answer 1, unify 2; every table empty.
  wait   h_monitor's out/2 (guard wait(String)) thrown to PE 1 with
         [S] and P, S of PE 0 a 16-bit string or a vector of 7: PE 1
         reads the list, then S at level 1, and binds P to
         [io(2, S, Status) | Pcdr]; PE 1's copy of S (through its
         export of io(..)) is S; out1 waits on Status for ever; throw
         1, read 2, answer 2, release 2, unify 1.
And current_processor and unbound/2 run on PE 1 of 2: (1, 2, 1), and
{1, Address, X} for a variable; of an external reference refused.
Every path pimm_pe.py marks (PE.ran: answer at once or by a reply
record, a reply record waiting again, level 1 of a list, vector, long
vector, string, an ID going home and coming home, an indirect export,
...) must run in some case (PATHS).

Observed fault injections, 2026-11-26, each on a private copy of
rung M2's pimm_pe.py (commit 53012caa), the whole check run (FAIL
lines by check, both quotas; rung M3's are in m3_gc.py):
  no %read sent              107: every N>1 monitor case (each PE
                             asked, the answers), every bench answer,
                             messages and tables, `PE 1 has S`, paths
  reply record not re-hooked 12: chain's R, messages, tables
  an ID going home exported  raises RuntimeError: heap full (the reads
    again                    chase each other)
  no %release after answer   44: messages and tables of rev, chain,
                             wait, node, third
  %release sent twice        478: `release of a free entry` everywhere,
                             bench messages
  %unify keeps the entry     30: tables of every bench case
  the cell not made the      raises KeyError (a second read of a
    value after %unify       given-up import)
  every @node made local     33: the monitors' asked/answers, paths
                             (level 1 vector never ran)
  current_processor gives    1: builtins current_processor
    Y = N
  unbound/2 gives node 0     1: builtins unbound
  %read frees the entry      raises Unimplemented: %unify to a released
                             export entry
  %answer_value keeps the    502: `pending read has no reply entry`
    pending read             everywhere, bench tables
  %unify keeps the import    135: `import .. dangles` in every N>1
                             case, `release of a free entry`, tables,
                             paths
  delivery LIFO, not FIFO    nothing: PASS (no case here depends on
                             the order within a pair; not caught)
Never fired: `the two schedules differ`, `messages in flight`, alias's
`Y refers to the external cell` and `PE 1 reads one import`, and the
refusal of unbound/2 of an external reference (since rung M5 not a
refusal: the builtins case checks that of an external variable the
goal is thrown to its owner, and of an external value it gives {X}).
"""
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import pimm_gc  # noqa: E402
import pimm_pe  # noqa: E402
import lockstep_link as link  # noqa: E402
import lockstep_modc as modc  # noqa: E402
import lockstep_xmod as xmod  # noqa: E402
from pimm import INT, ATOM, REF, UNDF, LIST, MOD  # noqa: E402
from pimm_layout import G_ARGS, G_LINK  # noqa: E402

FILE = 'pimm_debugger360E.sav'
# the predicates in source order (hmonitor.kl1, x_hmonitor.kl1), named
# as the unloader writes them ('_' as '2'), with their arities
PREDS = {
    'h2monitor': [('p2meter', 7), ('p2meter0', 7), ('p2meter1', 7), ('msg2timer2control', 5),
                  ('msg2timer2control2', 5), ('throw2profile2process', 3),
                  ('throw2pe2profile', 2), ('get2time2stream', 3), ('throw2profile2msg', 3),
                  ('pe2profile', 1), ('throw2heap', 1), ('reverse', 2), ('reverse', 3),
                  ('make2data', 5), ('counter', 5), ('cal', 5), ('cal1', 2),
                  ('check2value', 3), ('out', 2), ('out1', 3)],
    'x2h2monitor': [('p2meter', 7), ('p2meter0', 7), ('check2p2meter1', 8), ('send2socket', 5),
                    ('send2socket2stat', 2), ('send2socket2N', 5), ('p2meter1', 7),
                    ('msg2timer2control', 5), ('msg2timer2control2', 5),
                    ('throw2profile2process', 3), ('throw2pe2profile', 3),
                    ('get2time2stream', 3), ('throw2profile2msg', 3), ('pe2profile', 2),
                    ('throw2heap', 1), ('reverse', 2), ('reverse', 3), ('make2data', 5),
                    ('counter', 5), ('cal', 5), ('cal1', 2), ('check2value', 3),
                    ('out', 2), ('out1', 3)],
}
PROGS = (('h', 'h2monitor'), ('x', 'x2h2monitor'))
CASES = [(1, 0), (2, 0), (2, 1), (4, 0), (4, 3)]      # (N, the home node c)
QUOTAS = (1, 1000000)
ROUNDS = 3
# the monitors: messages by kind, and what is left on the home and on
# each other PE (exports, imports, pending reads, suspended goals,
# ready), by (program, N); observed 2026-11-26 and pinned
MONITOR = {
    ('h', 1): ({}, (0, 0, 0, 2, 0), None),
    ('h', 2): ({0: 1, 6: 8, 7: 7, 8: 7, 9: 3}, (1, 0, 0, 3, 0), (1, 1, 1, 1, 0)),
    ('h', 4): ({0: 3, 6: 24, 7: 21, 8: 21, 9: 9}, (3, 0, 0, 5, 0), (1, 1, 1, 1, 0)),
    ('x', 1): ({}, (0, 0, 0, 2, 0), None),
    ('x', 2): ({0: 1, 6: 14, 7: 13, 8: 12, 9: 1}, (1, 1, 0, 3, 0), (2, 1, 1, 1, 0)),
    ('x', 4): ({0: 3, 6: 42, 7: 39, 8: 36, 9: 3}, (1, 3, 0, 5, 0), (2, 1, 1, 1, 0)),
}
# third: messages by kind (observed 2026-11-26, then pinned)
THIRD = {
    # back to PE 0: both IDs come home there, their entries done with
    # (PE 1 passed them on, white paths), and reverse runs on PE 0
    2: ({0: 2}, None),
    # on to PE 2: PE 1 passes the two IDs on (rung M3; at M2 it
    # exported them again, 22 reads); PE 2 reads L from PE 0 itself
    4: ({0: 2, 6: 11, 7: 11, 8: 11, 9: 1}, None),
}


def entries(m, a, items):
    """The predicates of the loaded module at a: [(name, arity, entry)],
    entry a code index, in the module's order."""
    n = m.mem[a][1] & 0xffffff
    heads = [c for c in range(a, a + n + 1)
             if m.mem[c][0] == pimm.PREDH and c - (m.mem[c][1] & 0xffffff) == a]
    # the code area's first item: the first predicate's name cell is
    # item 0 (asm/unlsav.py's items, one cell each)
    base = heads[0] - 2
    out = []
    for h in heads:
        it = items[h - 2 - base]
        assert it[0] == 'atomref' and m.mem[h - 2][0] == ATOM, (it, m.mem[h - 2])
        out.append((it[3], m.mem[h][1] >> 24, h + 2 - m.load))
    return out, base


def atoms(m, base, items):
    """name -> the atom number the loader gave it, from the code area's
    atom items and the cells they were loaded into."""
    out = {}
    for k, it in enumerate(items):
        if it[0] in ('atom', 'atomref'):
            c = m.mem[base + k]
            v = c[1] & 0xffffff if c[0] != ATOM else c[1]
            if out.setdefault(it[3], v) != v:
                raise AssertionError('atom %s loaded as %d and %d' % (it[3], out[it[3]], v))
    return out


def loaded():
    """The machine with FILE loaded and collected down to the two
    modules (a root goal holding them, removed after), and what the
    checks need.  M2_CACHE=PATH keeps it between runs (a scratch file;
    not part of the check)."""
    cache = os.environ.get('M2_CACHE')
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
    found = {}
    for _short, name in PROGS:
        i = [k for k, mod in enumerate(fm) if mod['name'] == name]
        assert len(i) == 1, (name, i)
        preds, base = entries(m, mods[i[0]], fm[i[0]]['items'])
        assert [(p, a) for p, a, _e in preds] == PREDS[name], (name, preds)
        found[name] = (mods[i[0]], preds, atoms(m, base, fm[i[0]]['items']))
    # collect everything but the two modules: a goal of the root holds
    # them (its code a stub's, below the heap), taken off after
    g = m.record(pimm.READY, m.stubs['apply']['addr'],
                 [(MOD, found[name][0]) for _s, name in PROGS])
    pimm_gc.collect(m)
    g = m.rq
    info = {}
    for k, (short, name) in enumerate(PROGS):
        old, preds, at = found[name]
        new = m.mem[g + G_ARGS + k][1]
        info[short] = {'entry': {(p, a): e + new - old for p, a, e in preds}, 'atoms': at}
    m.rq = m.mem[g + G_LINK][1]
    assert m.rq == 0 and m.nsusp == 0
    out = (pimm_pe.dumps(m), info)
    if cache:
        with open(cache, 'wb') as f:
            pickle.dump(out, f)
    return out


# every path of pimm_pe.py's reading code (PE.ran) must run in some
# case; the rest of the M3 paths in m3_gc.py
PATHS = ('answer at once', 'answer, import given up', 'answer, import kept',
         'black ID came home', 'black ID passed on, half its WEC', 'black entry again',
         'black entry reclaimed', 'black export', 'level 1 list', 'level 1 long vector',
         'level 1 string', 'level 1 vector', 'reply record', 'reply record waits again',
         'unify with a read pending', 'variable to external cell', 'white ID came home',
         'white ID passed on')
SYSTEMS = []


def new_system(blob, n):
    s = pimm_pe.System(blob, n)
    SYSTEMS.append(s)
    return s


def paths():
    out = {}
    for s in SYSTEMS:
        for pe in s.pes:
            for k, v in pe.paths.items():
                out[k] = out.get(k, 0) + v
    return dict(sorted(out.items()))


def walk(pe, w):
    """The elements of a list on pe up to its unbound tail."""
    out = []
    d = pe.deref(w)
    while d[0] & ~1 == LIST:
        out.append(pe.term(pe.taken(d[1])))
        d = pe.deref(pe.taken(d[1] + 1))
    return out, pe.unbound(d)


def push(pe, tail, atom):
    """The bench binds the stream's tail to [atom | T]; T."""
    c = pe.alloc(2)
    pe.mem[c] = (ATOM, atom)
    pe.mem[c + 1] = (UNDF, 0)
    pe.unify(tail, (LIST, c))
    return (REF, c + 1)


def tables(system):
    """What is left, per PE: exports, imports, pending reads, suspended
    goals, ready goals."""
    return [(len(pe.exports), len(pe.imports), len(pe.reading), pe.nsusp, int(bool(pe.rq or pe.mq)))
            for pe in system.pes]


def consistent(system):
    """Every import refers to a live export entry; every pending read's
    reply entry is live; no anomaly."""
    bad = list(system.anomalies)
    for pe in system.pes:
        for imp, ent in pe.imports.items():
            owner = system.pes[pimm_pe.id_pe(ent['id'])]
            if pimm_pe.id_entry(ent['id']) not in owner.exports:
                bad.append(('import %d of PE %d dangles' % (imp, pe.pe), ent['id']))
        for e in pe.reading:
            if e not in pe.exports:
                bad.append(('pending read %d of PE %d has no reply entry' % (e, pe.pe)))
    if any(q for q in system.queues.values()):
        bad.append('messages in flight at the end')
    return bad


def monitor(blob, info, prog, n, c, quota):
    p = info[prog]
    system = new_system(blob, n)
    home = system.pes[c]
    repo, t = home.new_var(), home.new_var()
    home.spawn(p['entry'][('throw2profile2process', 3)], [(INT, n - 1), repo, t])
    system.run(quota)
    for _ in range(ROUNDS):
        t = push(home, t, p['atoms']['profile'])
        system.run(quota)
    return system, repo


def check_monitor(system, repo, n, c):
    bad = []
    home = system.pes[c]
    answers, open_tail = walk(home, repo)
    want = [[(used, size - used) for size, used in [system.pes[k].heap_log[r] for k in range(n)]]
            for r in range(min(ROUNDS, min(len(pe.heap_log) for pe in system.pes)))]
    if [len(pe.heap_log) for pe in system.pes] != [ROUNDS] * n:
        bad.append(('each PE asked %d times' % ROUNDS, [len(pe.heap_log) for pe in system.pes]))
    if not open_tail or [list(a) if isinstance(a, list) else a for a in answers] != want:
        bad.append(('the answers are each node\'s own heap, node 0 first', answers, want))
    bad += consistent(system)
    return bad


def bench_rev(blob, info, n, quota, node_var=False, via=None, want=None, left=None):
    """rev / node / third: reverse(L, R) on PE 1 (on PE 2 by way of
    PE 1), then reverse(R, RR) on PE 0."""
    e2 = info['h']['entry'][('reverse', 2)]
    system = new_system(blob, n)
    p0 = system.pes[0]
    lst = pimm.NIL
    for v in range(6, 0, -1):
        c = p0.alloc(2)
        p0.mem[c], p0.mem[c + 1] = (INT, v), lst
        lst = (LIST, c)
    r = p0.new_var()
    if node_var:
        # Goal@node(P), P unbound: the to_processor goal, as
        # pimm.Machine.i_enqueue_goal_to_processor makes it
        pv = p0.new_var()
        g = p0.record(pimm.SUSPENDED, p0.stubs['$to_processor2']['addr'],
                      [lst, r, pv, (INT, p0.load + e2)])
        p0.nsusp += 1
        p0.hook(g, pv[1])
        system.run(quota)
        p0.unify(pv, (INT, 1))
    elif via is not None:
        # the to_processor goal of Goal@node(2), thrown to PE 1, which
        # throws the goal on with its two imports exported again
        p0.throw(1, p0.stubs['$to_processor2']['addr'],
                 [lst, r, (INT, via), (INT, p0.load + e2)])
    else:
        p0.throw(1, e2, [lst, r])
    system.run(quota)
    rr = p0.new_var()
    p0.spawn(e2, [r, rr])
    system.run(quota)
    bad = []
    got = p0.term(rr)
    if got != [1, 2, 3, 4, 5, 6]:
        bad.append(('RR', got))
    sent = dict(sorted(system.sent.items()))
    want = want or {0: 1, 6: 11, 7: 11, 8: 11, 9: 1}
    if sent != want:
        bad.append(('messages', sent, want))
    if tables(system) != (left or [(0, 0, 0, 0, 0)] * n):
        bad.append(('left', tables(system), left))
    return bad + consistent(system), sent


def bench_home(blob, info, n, quota):
    e3 = info['h']['entry'][('reverse', 3)]
    system = new_system(blob, n)
    p0 = system.pes[0]
    a, b = p0.new_var(), p0.new_var()
    p0.throw(1, e3, [pimm.NIL, a, b])
    system.run(quota)
    p0.unify(b, (INT, 7))
    system.run(quota)
    bad = []
    if p0.term(a) != 7:
        bad.append(('A', p0.term(a)))
    sent = dict(sorted(system.sent.items()))
    if sent != {0: 1, 9: 1}:
        bad.append(('messages', sent))
    left = tables(system)
    if left != [(0, 0, 0, 0, 0)] * n:
        bad.append(('left: B passed home, nothing left', left))
    return bad + consistent(system), sent


def bench_chain(blob, info, n, quota):
    """chain: reverse(X, R) thrown to PE 1 reads X of PE 0; then X = Y
    on PE 0 (Y a new variable) wakes the reply record with X still
    unbound, and it waits on Y; then Y = [] gives R = []."""
    e2 = info['h']['entry'][('reverse', 2)]
    system = new_system(blob, n)
    p0 = system.pes[0]
    x, r, y = p0.new_var(), p0.new_var(), p0.new_var()
    p0.throw(1, e2, [x, r])
    system.run(quota)
    p0.unify(x, y)
    system.run(quota)
    p0.unify(y, pimm.NIL)
    system.run(quota)
    bad = []
    if p0.term(r) != []:
        bad.append(('R', p0.term(r)))
    sent = dict(sorted(system.sent.items()))
    if sent != {0: 1, 6: 1, 7: 1, 8: 1, 9: 1}:
        bad.append(('messages', sent))
    if any(t != (0, 0, 0, 0, 0) for t in tables(system)):
        bad.append(('every table empty', tables(system)))
    return bad + consistent(system), sent


def bench_alias(blob, info, n, quota):
    """alias: reverse(X, R) thrown to PE 1, which reads X; then on PE 1
    a new variable Y = X's external cell (Y becomes a reference to it)
    and Y = [] (a %unify with the read still pending); R = [] on PE 0."""
    e2 = info['h']['entry'][('reverse', 2)]
    system = new_system(blob, n)
    p0, p1 = system.pes[0], system.pes[1]
    x, r = p0.new_var(), p0.new_var()
    p0.throw(1, e2, [x, r])
    system.run(quota)
    cells = [ent['cell'] for ent in p1.imports.values() if ent['read'] is not None]
    bad = []
    if len(cells) != 1:
        return [('PE 1 reads one import', cells)], dict(system.sent)
    y = p1.new_var()
    p1.unify(y, (REF, cells[0]))
    if p1.deref(y) != (REF, cells[0]):
        bad.append(('Y refers to the external cell', p1.deref(y)))
    p1.unify(y, pimm.NIL)
    system.run(quota)
    for name, w in (('X', x), ('R', r)):
        if p0.term(w) != []:
            bad.append((name, p0.term(w)))
    sent = dict(sorted(system.sent.items()))
    if sent != {0: 1, 6: 1, 7: 1, 9: 2}:
        bad.append(('messages', sent))
    if any(t != (0, 0, 0, 0, 0) for t in tables(system)):
        bad.append(('every table empty', tables(system)))
    return bad + consistent(system), sent


def bench_wait(blob, info, n, quota, kind):
    """wait: out([S], P) thrown to PE 1 (h_monitor's out/2, its guard
    wait(String)), S of PE 0 a string or a vector of seven: PE 1 reads
    the list, then S (at level 1, a string or a long vector), and binds
    P to [io(2, S, Status) | Pcdr], its elements exported; out1 then
    waits on Status, a variable of PE 1, for ever.  PE 1's copy of S
    (found through its export of io(..)) is S."""
    eo = info['h']['entry'][('out', 2)]
    system = new_system(blob, n)
    p0, p1 = system.pes[0], system.pes[1]
    if kind == 'string':
        s = p0.make_string(16, [0x2422, 0x2423, 7])
    else:
        s, a = p0.vnew(7)
        for i in range(7):
            p0.mem[a + i] = (INT, 10 + i)
    want_s = p0.term(s)
    c = p0.alloc(2)
    p0.mem[c], p0.mem[c + 1] = s, pimm.NIL
    pm = p0.new_var()
    p0.throw(1, eo, [(LIST, c), pm])
    system.run(quota)
    bad = []
    io = info['h']['atoms']['io']
    copies = []
    for w in p1.exports.values():
        d = p1.deref(w)
        if d[0] & ~1 == pimm.VECT0 + 8 and p1.taken(p1.vbase(d)) == (ATOM, io):
            copies.append(p1.term(p1.taken(p1.vbase(d) + 2)))
    if copies != [want_s]:
        bad.append(('PE 1 has S', copies, want_s))
    sent = dict(sorted(system.sent.items()))
    if sent != {0: 1, 6: 2, 7: 2, 8: 2, 9: 1}:
        bad.append(('messages', sent))
    want = [(0, 2, 0, 0, 0), (2, 0, 0, 1, 0)] + [(0, 0, 0, 0, 0)] * (n - 2)
    if tables(system) != want:
        bad.append(('left: PE 1 exports io(..) and Pcdr, out1 waits', tables(system), want))
    return bad + consistent(system), sent


def check_builtins(blob):
    system = new_system(blob, 2)
    p1 = system.pes[1]
    bad = []
    p1.i_current_processor(0, 1, 2, 3, 0)
    if p1.reg[1:4] != [(INT, 1), (INT, 2), (INT, 1)]:
        bad.append(('current_processor', p1.reg[1:4]))
    v = p1.new_var()
    p1.reg[1] = v
    p1.i_unbound(0, 1, 2, 0, 0)
    w = p1.reg[2]
    got = [p1.mem[p1.vbase(w) + i] for i in range(p1.vsize(w))]
    if got != [(INT, 1), (INT, v[1]), v]:
        bad.append(('unbound', got))
    p1.reg[1] = p1.import_id((pimm_pe.EXREF, pimm_pe.ext_id(0, 1)))
    # rung M5: of an external variable, the goal unbound(X, Result) is
    # thrown to its owner (PE 0) and Result is a fresh variable here
    throws = system.sent.get(0, 0)
    p1.i_unbound(0, 1, 2, 0, 0)
    if system.sent.get(0, 0) != throws + 1 or not p1.unbound(p1.deref(p1.reg[2])):
        bad.append(('unbound of an external variable thrown to its owner', system.sent, p1.reg[2]))
    # ... and of an external value it is {X} at once
    p1.reg[1] = x = p1.import_id((pimm_pe.EXVAL, pimm_pe.ext_id(0, 2)))
    p1.i_unbound(0, 1, 2, 0, 0)
    w = p1.reg[2]
    if system.sent.get(0, 0) != throws + 1 or p1.vsize(w) != 1 or p1.mem[p1.vbase(w)] != p1.deref(x):
        bad.append(('unbound of an external value', w))
    return bad


def main(argv):
    blob, info = loaded()
    bad, rows = [], []
    for prog, _name in PROGS:
        for n, c in CASES:
            seen = []
            for q in QUOTAS:
                system, repo = monitor(blob, info, prog, n, c, q)
                b = check_monitor(system, repo, n, c)
                bad += [(prog, n, c, q) + (x,) for x in b]
                sent = dict(sorted(system.sent.items()))
                msgs, hrow, orow = MONITOR[(prog, n)]
                if sent != msgs:
                    bad.append((prog, n, c, q, ('messages', sent, msgs)))
                want = [hrow if k == c else orow for k in range(n)]
                if tables(system) != want:
                    bad.append((prog, n, c, q, ('left', tables(system), want)))
                seen.append((sent, tables(system)))
                rows.append('%s N=%d c=%d quota=%-7d messages %s  left %s' % (
                    prog, n, c, q, sent, tables(system)))
            if seen[0] != seen[1]:
                bad.append((prog, n, c, 'the two schedules differ', seen))
    for n in (2, 4):
        for name, f in (('rev', lambda q: bench_rev(blob, info, n, q)),
                        ('home', lambda q: bench_home(blob, info, n, q)),
                        ('chain', lambda q: bench_chain(blob, info, n, q)),
                        ('alias', lambda q: bench_alias(blob, info, n, q)),
                        ('wait string', lambda q: bench_wait(blob, info, n, q, 'string')),
                        ('wait vector', lambda q: bench_wait(blob, info, n, q, 'vector')),
                        ('node', lambda q: bench_rev(blob, info, n, q, node_var=True)),
                        ('third', lambda q: bench_rev(blob, info, n, q, via=n - 2,
                                                      want=THIRD[n][0], left=THIRD[n][1]))):
            for q in QUOTAS:
                b, sent = f(q)
                bad += [(name, n, q, x) for x in b]
                rows.append('%-5s N=%d quota=%-7d messages %s' % (name, n, q, sent))
    bad += [('builtins', x) for x in check_builtins(blob)]
    for r in rows:
        print(r)
    print('paths', paths())
    missing = [k for k in PATHS if k not in paths()]
    if missing:
        bad.append(('paths that never ran', missing))
    for b in bad:
        print('FAIL', b)
    print('m2 read: %s (%d runs)' % ('FAIL' if bad else 'PASS', len(rows)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
