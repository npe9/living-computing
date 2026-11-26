#!/usr/bin/env python3
"""Rung M4 (docs/multi_pe.md): the shoen across PEs.

    python3 ref/pimm/m4_shoen.py         the check; ends `m4 shoen: PASS`

The reference model only (pimm_pe.py).  The machine is M1's
(pimm_shell360E.sav loaded by ipl_loader:load/4, m1_gc.py), copied to
every PE.  Every part runs a shoen made by the IMAGE'S OWN
shoen:execute/4 (cell 15550: create_shoen, then control/2 and
report/2 at the root) on the home node c, its code PIMOS's
prof:apply_goals/1 from the same file (shell/utils/prof.kl1:200-209,
HELD-SOURCE: each {Code, ArgV, Node} of its list becomes
apply_with_pgm(Code, ArgV)@node(Node)), so that what runs on the other
nodes is a goal of the shoen thrown there, in a foster parent.  The
bench reads the Report stream as report/2 gives it (atoms, and
statistics(H, L), return_resource(H, L), exception(Kind, Info, NewCode,
NewArgV) as vectors) and binds the Control stream's tail between runs.

Parts (k = (c + 1) mod N, the node the work goes to; on one PE k = c):
  spread     seqgc:go/0 at node k: the foster parent on k throws to
             every other node and to the home (M1's seqgc, from k).
             Control [start, add_resource(16#3FFFFFFF, 16#FFFFFFFF)];
             then [statistics]; then [] (the removal).
  home       gc:go/0 at node c: the shoen's own PE throws to every node.
  stop       ipl_pool:hash/3 at node k on {X, H, NewX}, X the home's,
             and ipl:dummy/2 at node k after it (a goal to the foster
             parent there): hash/3 waits for X (a %read); the bench
             asks statistics (of the live foster parent), sends stop, binds X
             (so the goal is woken on a stopped foster parent and
             parks), sees H unbound, sends start, sees H bound.
  abort      the same, then abort in place of start; then X bound: the
             woken goal of the ended foster parent is discarded.
  exception  ipl:close_fep(shut, 0) at node k, no clause for it: a
             reduction failure in the foster parent, %exception to the
             shoen; the bench answers NewCode = ipl:dummy/2, NewArgV =
             {0, 0}.
  nested     shoen:execute/4 at node k with hash/3 on the home's X: a
             shoen made inside the foster parent, its Control and
             Report the home's variables; the bench starts and funds
             it, the image's top:bios_monitor/3 at the home reads its
             Report (each element read across) and closes its Control
             after terminated; then the bench binds X.
  resource   seqgc at node k, the shoen funded with only 16 (8
             reductions): its resource runs out (on several PEs the
             foster parents' too: they ask, %request_resource, and the
             shoen has none to give), resource_low is reported, and the
             run stops short of termination; the bench then adds
             16#3FFFFFFF:FFFFFFFF.

What is checked, on (N, c) = (1,0), (2,0), (2,1), (4,0), (4,3), each
part under quota 1 and quota 1,000,000:
  - `terminated` reported once, after `started` (and after `aborted`
    for abort); `stopped` and no `terminated` while stopped.
  - statistics(H, L) after termination = 2 x the reductions of goals
    of a shoen, counted on every PE as they end (pimm.Machine.
    end_reduction's own count, gathered here; every non-root goal of
    these parts is the shoen's or its child's).  return_resource =
    what was added less that.
  - the answers: hash/3's H bound only after start; the exception's
    Kind reduction_failure and Info's Pe = k, the foster parent's PE
    (the raw report of shoen:execute/4; the image's
    exception_table:translate/4 makes a node from it).
  - after every run: no anomaly, every shoen's WTC accounted for (its
    entry's WEC = minus the WTC its foster parents hold), its resource
    out = what they were given less what they reported; at the end no
    foster parent and no shoen table left, one %terminated for each
    %ready per (shoen ID, PE), and nothing left on any PE but what the
    part leaves on purpose (abort: none either, once X is bound).
  - both quotas give the same Reports (statistics values aside: the
    reductions differ by schedule, as at M1) and the same answers.
The message counts are printed, not pinned (whether a foster parent
ends and is made again depends on the schedule).

A part that raises is that run's FAIL line (`raised`), the other runs
going on.

Observed fault injections (each on a private copy of pimm_pe.py, this
whole script run, 2026-11-26; docs/multi_pe.md 5, M4):
  - no extra goal count while WTC is out: 104 FAIL lines (spread,
    resource: tables and goals left, one %terminated per %ready, low
    not terminated; abort's order; exception: report, the two
    schedules differ, KeyError; nested; stop raises start_shoen ...
    not dormant or stopped)
  - %terminated gives back no WTC: 368 (every N>1 part: WTC not
    accounted for, tables, goals left, never terminated)
  - stopped not sent to the foster parents: 8 (each N>1 stop run
    raises start_shoen of a shoen that is not dormant or stopped)
  - %terminated's consumption not charged: 96 (statistics and
    return_resource in spread, home, stop, exception, nested, resource)
  - a goal to an existing foster parent loses its WTC: 160 (stop and
    abort: WTC, tables, goals left, terminated)
  - a foster parent never asks for resource: 104 (spread, resource)
  - the loaded modules not collector roots: nothing (PASS); no part
    throws a goal to a PE after it collected.
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
from pimm import INT, ATOM, REF, LIST, VECT0, COD  # noqa: E402

FILE = 'pimm_shell360E.sav'
CASES = [(1, 0), (2, 0), (2, 1), (4, 0), (4, 3)]
QUOTAS = (1, 1000000)
FUND = (0x3FFFFFFF, 0xFFFFFFFF)
PARTS = ('spread', 'home', 'stop', 'abort', 'exception', 'nested', 'resource')


def loaded_machine():
    """M1's machine, and the code of seqgc:go/0, gc:go/0 and
    prof:apply_goals/1 (asm/unlsav.py names it apply2goals).
    M4_CACHE=PATH keeps it between runs."""
    cache = os.environ.get('M4_CACHE')
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
    for mod, pred, ar in (('seqgc', 'go', 0), ('gc', 'go', 0), ('prof', 'apply2goals', 1)):
        i = [k for k, x in enumerate(fm) if x['name'] == mod]
        assert len(i) == 1, (mod, i)
        hits = [loc for pn, a, loc in fm[i[0]]['preds'] if pn == pred and a == ar]
        assert len(hits) == 1, (mod, fm[i[0]]['preds'])
        code[mod] = mods[i[0]] + hits[0] - m.load
        assert m.opname(code[mod]) is not None
    out = (m, code)
    if cache:
        with open(cache, 'wb') as f:
            f.write(pimm_pe.dumps(out))
    return out


# the reductions of goals of a shoen, per PE, as end_reduction counts them
TALLY = {}
_end = pimm_pe.PE.end_reduction


def _counting(self):
    if self.chain and self.shoen:
        TALLY[self.pe] = TALLY.get(self.pe, 0) + self.chain
    return _end(self)


pimm_pe.PE.end_reduction = _counting


class Bench:
    def __init__(self, blob, code, n, c, quota):
        TALLY.clear()
        self.sys = pimm_pe.System(blob, n)
        self.n, self.c, self.quota = n, c, quota
        self.k = (c + 1) % n
        self.home = self.sys.pes[c]
        self.code = code
        im = self.home.im
        self.atoms = {name: num for num, name in im.sym.items()}
        self.names = dict(im.sym)
        self.P = lambda mod, pred: (COD, self.home.load + pimm.predicate(im, mod, pred))
        self.bad = []
        self.added = 0

    def A(self, name):
        return (ATOM, self.atoms[name])

    def vec(self, *ws):
        if not ws:
            return (VECT0, 0)
        w, b = self.home.vnew(len(ws))
        for i, x in enumerate(ws):
            self.home.mem[b + i] = x
        return w

    def lst(self, items, tail):
        out = tail
        for x in reversed(items):
            a = self.home.alloc(2)
            self.home.mem[a], self.home.mem[a + 1] = x, out
            out = (LIST, a)
        return out

    def var(self):
        return self.home.new_var()

    def shoen(self, goals, control_items):
        """shoen:execute(prof:apply_goals/1, {Goals}, Control, Report) at
        the root on the home node; the Control's open tail."""
        h = self.home
        tail = self.var()
        control = self.lst(control_items, tail)
        report = self.var()
        gl = self.lst([self.vec(*g) for g in goals], pimm.NIL)
        argv = self.vec(gl)
        h.spawn(pimm.predicate(h.im, 'shoen', 'execute/4'),
                [(COD, h.load + self.code['prof']), argv, control, report])
        h.roots['report'] = report
        return self.hold('tail', tail)

    def hold(self, name, w):
        """A word the bench keeps: a root of the home's collector
        (PE.roots), read back by name."""
        self.home.roots[name] = w
        return name

    def get(self, name):
        return self.home.roots[name]

    @property
    def report(self):
        return self.home.roots['report']

    def fund(self, hi, lo):
        self.added += hi << 32 | lo
        return self.vec(self.A('add_resource'), (INT, hi), (INT, lo))

    def send(self, tail, items, closed=False):
        """Bind the Control tail (held by name) to the items and an
        open tail, held under the same name, or []."""
        new = pimm.NIL if closed else self.var()
        self.home.unify(self.get(tail), self.lst(items, new))
        self.hold(tail, new)
        return tail

    def run(self, rounds=None):
        self.sys.run(self.quota, rounds=rounds)
        self.invariants()

    def term(self, w, depth=0):
        """A term of the home PE, read (the bench's own reading)."""
        d = self.home.deref(w)
        t = d[0] & ~1
        if self.home.unbound(d) or self.home.is_ex(d):
            return '_'
        if t == INT:
            return pimm.signed(d[1])
        if t == ATOM:
            return '[]' if d == pimm.NIL else self.names.get(d[1], '#%d' % d[1])
        if t == LIST:
            out = []
            while (d[0] & ~1) == LIST and depth < 50:
                out.append(self.term(self.home.mem[d[1]], depth + 1))
                d = self.home.deref(self.home.mem[d[1] + 1])
                depth += 1
            tl = self.term(d, depth + 1)
            return out + ([] if tl == '[]' else ['|', tl])
        n = self.home.vsize(d)
        if n is not None:
            b = self.home.vbase(d)
            return tuple(self.term(self.home.mem[b + i], depth + 1) for i in range(n))
        if t == COD:
            return 'code'
        return '?%02x' % d[0]

    def reports(self):
        return self.term(self.report)

    def invariants(self):
        """At quiescence (or a pause): the WTC and resource of every
        shoen with goals elsewhere accounted for; no anomaly."""
        s = self.sys
        if s.anomalies:
            self.bad.append(('anomalies', s.anomalies[:3]))
            s.anomalies.clear()
        inflight = sum(len(q) for q in s.queues.values())
        for pe in s.pes:
            for sh, h in pe.homes.items():
                sid = pimm_pe.ext_id(pe.pe, h['e'])
                fps = [(o.pe, o.fpi[o.fps[sid]]) for o in s.pes if sid in o.fps]
                if not inflight:
                    held = sum(i['wtc'] for _k, i in fps)
                    if pe.wec[h['e']] + held:
                        self.bad.append(('WTC not accounted for', pe.pe, pe.wec[h['e']], held))
                    out = sum(i['given'] - i['reported'] for _k, i in fps)
                    if h['adv'] != out:
                        self.bad.append(('resource out', pe.pe, h['adv'], out))
                    live = sorted(k for k, n in h['fps'].items() if n)
                    if live != sorted(k for k, _i in fps):
                        self.bad.append(('foster parents known', pe.pe, live, [k for k, _i in fps]))

    def end(self, drain=False):
        """What must be left at the end of a part.  drain: the bench
        lets go of what it holds and every PE is collected twice (as
        m3_gc.py drains), so that the imports a discarded goal held are
        released (the import table is weak, pimm_pe.PECollector)."""
        s = self.sys
        self.last = flat(self.reports())
        if drain:
            self.home.roots.clear()
            for _ in range(2):
                for pe in s.pes:
                    pe.collect()
                self.run()
        made = {}
        for e in s.log:
            if e[0] in ('fp', 'fp end'):
                made.setdefault((e[1], e[2]), [0, 0])[e[0] == 'fp end'] += 1
        for key, (a, b) in made.items():
            if a != b:
                self.bad.append(('one %terminated for each %ready', key, a, b))
        for pe in s.pes:
            if pe.homes or pe.fps or pe.fpi:
                self.bad.append(('PE %d keeps shoen tables' % pe.pe, pe.homes, pe.fps))
            if (pe.nsusp or pe.exports or pe.imports or pe.rq or pe.mq or pe.mwh):
                self.bad.append(('PE %d left' % pe.pe, pe.nsusp, pe.exports, pe.imports))

    def statistics_ok(self, rep):
        st = [r for r in rep if isinstance(r, tuple) and r[0] == 'statistics']
        red = sum(TALLY.values())
        want = ('statistics', (2 * red) >> 32, (2 * red) & 0xffffffff)
        if [x if x >= 0 else x + (1 << 32) for x in st[-1][1:]] != list(want[1:]):
            self.bad.append(('statistics', st, want))
        rr = [r for r in rep if isinstance(r, tuple) and r[0] == 'return_resource']
        left = self.added - 2 * red
        if rr and [x & 0xffffffff for x in rr[-1][1:]] != [left >> 32, left & 0xffffffff]:
            self.bad.append(('return_resource', rr, left))


def once(rep, what):
    return sum(1 for r in rep if r == what)


RESOURCE_EVENTS = ('resource_low', 'resource_added', 'resource_report_allowed')


def flat(rep):
    """A report list with its numbers dropped (they differ by schedule),
    and without the resource events, whose number and place depend on
    when the first goal is taken against when the funding is (a monitor
    answers resource_low with more)."""
    return [r if not isinstance(r, tuple) or r[0] not in ('statistics', 'return_resource')
            else r[0] for r in rep if r not in ('|', '_') and r not in RESOURCE_EVENTS]


def part(name, blob, code, n, c, q):
    b = Bench(blob, code, n, c, q)
    k = b.k
    A, P, vec = b.A, b.P, b.vec
    start = [A('start'), b.fund(*((0, 16) if name == 'resource' else FUND))]
    out = {}
    if name in ('spread', 'home', 'resource'):
        prog, node = ('gc', c) if name == 'home' else ('seqgc', k)
        tail = b.shoen([((COD, b.home.load + code[prog]), vec(), (INT, node))], start)
        b.run()
        if name == 'resource':
            rep = b.reports()
            out['before'] = flat(rep)
            if 'resource_low' not in rep or 'terminated' in rep:
                b.bad.append(('resource: low, not terminated', rep))
            tail = b.send(tail, [b.fund(*FUND)])
            b.run()
        tail = b.send(tail, [A('statistics')])
        b.run()
        b.send(tail, [], closed=True)
        b.run()
        rep = b.reports()
        if once(rep, 'terminated') != 1 or rep.index('started') > rep.index('terminated'):
            b.bad.append(('terminated once, after started', rep))
        b.statistics_ok(rep)
        b.end()
    elif name in ('stop', 'abort'):
        x, h, nx = b.var(), b.var(), b.var()
        b.hold('x', x)
        b.hold('h', h)
        # a second goal to node k, after hash/3: to the foster parent
        # already there; statistics asked while hash/3 waits there
        tail = b.shoen([(P('ipl_pool', 'hash/3'), vec(x, h, nx), (INT, k)),
                        (P('ipl', 'dummy/2'), vec((INT, 0), (INT, 0)), (INT, k))], start)
        b.run()
        tail = b.send(tail, [A('statistics')])
        b.run()
        tail = b.send(tail, [A('stop' if name == 'stop' else 'abort')])
        b.run()
        b.home.unify(b.get('x'), (INT, -7 & 0xffffffff))
        b.run()
        rep = b.reports()
        hv = b.term(b.get('h'))
        out['paused'] = (flat(rep), hv)
        if name == 'stop':
            if 'stopped' not in rep or 'terminated' in rep or hv != '_':
                b.bad.append(('stopped, H unbound, not terminated', rep, hv))
            tail = b.send(tail, [A('start')])
            b.run()
            if b.term(b.get('h')) == '_':
                b.bad.append(('H bound after start', b.term(b.get('h'))))
        else:
            if rep.count('aborted') != 1 or once(rep, 'terminated') != 1 \
                    or rep.index('aborted') > rep.index('terminated') or hv != '_':
                b.bad.append(('aborted, then terminated once; H never bound', rep, hv))
        tail = b.send(tail, [A('statistics')])
        b.run()
        b.send(tail, [], closed=True)
        b.run()
        rep = b.reports()
        if once(rep, 'terminated') != 1:
            b.bad.append(('terminated once', rep))
        if name == 'stop':
            b.statistics_ok(rep)
        b.end(drain=name == 'abort')
    elif name == 'exception':
        tail = b.shoen([(P('ipl', 'close_fep/2'), vec(A('shut'), (INT, 0)), (INT, k))], start)
        b.run()
        rep = b.reports()
        exc = [r for r in rep if isinstance(r, tuple) and r[0] == 'exception']
        if len(exc) != 1 or exc[0][1] != 'reduction_failure' or exc[0][2][0] != k \
                or 'terminated' in rep:
            b.bad.append(('one reduction_failure from PE k, not terminated', rep))
        # the handler's answer: NewCode, NewArgV of the report's exception
        d = b.home.deref(b.report)
        while True:
            car = b.home.deref(b.home.mem[d[1]])
            if b.home.vsize(car) == 5:
                break
            d = b.home.deref(b.home.mem[d[1] + 1])
        base = b.home.vbase(car)
        b.home.unify(b.home.mem[base + 3], P('ipl', 'dummy/2'))
        b.home.unify(b.home.mem[base + 4], vec((INT, 0), (INT, 0)))
        b.run()
        tail = b.send(tail, [A('statistics')])
        b.run()
        b.send(tail, [], closed=True)
        b.run()
        rep = b.reports()
        out['exception'] = exc[:1] and (exc[0][1], exc[0][2][0])
        if once(rep, 'terminated') != 1:
            b.bad.append(('terminated once after the answer', rep))
        b.statistics_ok(rep)
        # drain: NewArgV's vector, exported to the foster parent's PE
        # by the answer's %unify, is held there until a collection
        b.end(drain=True)
    elif name == 'nested':
        x, h, nx = b.var(), b.var(), b.var()
        c2 = b.var()
        r2 = b.var()
        for nm, w in (('x', x), ('h', h), ('c2', c2), ('r2', r2)):
            b.hold(nm, w)
        inner = vec(P('ipl_pool', 'hash/3'), vec(x, h, nx), c2, r2)
        tail = b.shoen([(P('shoen', 'execute/4'), inner, (INT, k))], start)
        b.run()
        t2 = b.send('c2', [A('start'), b.fund(*FUND)])
        b.added -= FUND[0] << 32 | FUND[1]           # the inner's, not the outer's
        # the image's top:bios_monitor/3 on the inner's Report, at the
        # root on the home: it reads Report2 across (each element a
        # %read of what report/2 on node k wrote), answers terminated
        # with [statistics] on the inner's Control, and binds Shut on []
        shut = b.var()
        b.hold('shut', shut)
        b.home.spawn(pimm.predicate(b.home.im, 'top', 'bios_monitor/3'),
                     [b.get('r2'), b.get(t2), shut])
        b.run()
        b.home.unify(b.get('x'), (INT, -7 & 0xffffffff))
        b.run()
        if b.term(b.get('shut')) != 'shut':
            b.bad.append(('the inner monitor shut', b.term(b.get('shut')), b.term(b.get('r2'))))
        tail = b.send(tail, [A('statistics')])
        b.run()
        b.send(tail, [], closed=True)
        b.run()
        rep, rep2 = b.reports(), b.term(b.get('r2'))
        hv = b.term(b.get('h'))
        out['inner'] = flat(rep2)
        if once(rep2, 'terminated') != 1 or hv == '_':
            b.bad.append(('the inner terminated once, H bound', rep2, hv))
        if once(rep, 'terminated') != 1:
            b.bad.append(('the outer terminated once', rep))
        b.statistics_ok(rep)
        b.end()
    out['report'] = b.last
    sent = dict(sorted((pimm_pe.KIND_NAMES[kd], v) for kd, v in b.sys.sent.items()))
    paths = {}
    for pe in b.sys.pes:
        for p, v in pe.paths.items():
            paths[p] = paths.get(p, 0) + v
    return b.bad, out, sent, paths, sum(TALLY.values())


# the paths of pimm_pe.py's M4 code each part must have run somewhere
M4_PATHS = ('throw from a shoen', 'throw from a foster parent', 'goal came home to its shoen',
            'goal to a foster parent', 'throw waits for WTC', 'throw sent with the WTC supplied',
            'start to the foster parents', 'stop to the foster parents',
            'abort to the foster parents', 'foster parent aborted',
            'statistics asked of the foster parents', 'statistics answered',
            'exception to the shoen', 'foster parent asks for resource',
            'resource supplied', 'resource_low for a foster parent')


def main(argv):
    m, code = loaded_machine()
    blob = pimm_pe.dumps(m)
    bad, rows, paths = [], [], {}
    parts = [p for p in PARTS if p in argv[1:]] or PARTS
    for name in parts:
        for n, c in CASES:
            seen = []
            for q in QUOTAS:
                try:
                    b, out, sent, ps, red = part(name, blob, code, n, c, q)
                except Exception as e:      # a refusal: this run's failure
                    b, out, sent, ps, red = [('raised', '%s: %s' % (type(e).__name__, e))], \
                        ('raised', type(e).__name__), {}, {}, 0
                bad += [(name, n, c, q) + x for x in b]
                seen.append(out)
                rows.append((name, n, c, q, red, sent))
                for p, v in ps.items():
                    paths[p] = paths.get(p, 0) + v
            if seen[0] != seen[1]:
                bad.append((name, n, c, 'the two schedules differ', seen))
    for r in rows:
        print('%-9s N=%d c=%d quota=%-7d reductions %4d  messages %s' % r)
    print('paths', dict(sorted(paths.items())))
    if parts == list(PARTS):
        missing = [p for p in M4_PATHS if p not in paths]
        if missing:
            bad.append(('M4 paths never run', missing))
    for x in bad:
        print('FAIL', x)
    print('m4 shoen: %s (%d runs)' % ('FAIL' if bad else 'PASS', len(rows)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
