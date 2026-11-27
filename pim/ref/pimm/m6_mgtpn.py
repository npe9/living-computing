#!/usr/bin/env python3
"""Rung M6: a period multi-node program, MGTP/N's model-distributed
KL1 version (ICOT Free Software No. 91), on N PEs of the reference
model (docs/multi_pe.md 5, M6).

    python3 ref/pimm/m6_mgtpn.py LINK.pkl [--run N,C,T ...] [--quota Q ...]

LINK.pkl is the link checkpoint m5_boot.py takes (M5_CACHE keeps its
slimmed machine between runs).  A long runner, NOT in run_tests.sh:
each boot and compile is minutes (below).  M6_INJECT=local|lifo|nowake
makes one fault in every query run (in the forked child only; the
discriminating checks, docs/multi_pe.md 5, M6).  M6_CACHE=DIR keeps
each N's System after the compile (DIR/nN.pkl) between runs.

The program and its oracle (both held: docs/nonlocal/ifs/solver-prover/
pimos/MGTP-N/MGTP-N-KL1.tgz, in git, ICOT Free Software, NO WARRANTY):
  - mgtpv0.kl1 ("Multi-PSI version0 ... master-node", 454 lines) and
    util.kl1 (1,417), served whole from the tgz as home files, byte for
    byte (ASCII; a TAB as 00 09 as everywhere, a form feed, 7 lines of
    util.kl1, as 00 0C: INFERENCE, the same JIS control-code scheme).
    Registered here only, not in longrun_ipl.HOME_FILES (the suite's
    `ls` pins list the home directory).
  - INSTALL.j (and the Japanese manual mgtp-manual-J.ps, 4.3.3.2, pp.
    58-59) prints one run: problem 2 on five worker nodes, the goal
    `mgtpv0: main(1,5,3,[...],[...],[...],(1,1,2,YYNN),Result,Ncalc,
    Delta) .` and its result: Result=unsat, Ncalc= 18, time=385832
    reductions 2367 msec, and Delta, 18 model candidates, each printed
    as its key (node, number on that node, dummy) and its first term
    (the second, with odd variable numbers, "omitted").  The goal is
    typed as printed (its lines joined); the oracle is read from
    INSTALL.j at run time.
  - main/10's Cnd..Tnd are the worker nodes (">=1": node 0 is the
    master's, where the goal runs); disperse/7 places one
    disperse_node/8 on each with @node(PEone).  So the printed run
    needs 6 PEs.  The keys of Delta come from the node NUMBER passed as
    an argument, not from current_node.

The procedure (INSTALL.j's, adapted, OURS where it differs):
  compile, !package work, util, mgtpv0, !exit (INSTALL: compile(
  ["mgtpv0","util"]); one file a line as R9 types them, util first:
  mgtpv0 first is refused, "undefined module : work:: util"), then
  listener, default_package(work)., statistics. (INSTALL's st.),
  print_depth(20)., print_length(100). (INSTALL's pd. and pl. print
  "Print depth: 4 => 20", "Print length: 10 => 100"), then the goal.

Runs, each (N PEs, Cnd, Tnd): the System is booted and the files
compiled once (quota 1,000,000), then each query is run in a fork,
under each quota:
  (6,1,5)  the printed run: five workers on PEs 1..5
  (5,0,4)  the same five workers placed with the master on PE 0 (keys
           shifted by one; Cnd = 0 is OURS, outside main's ">=1")
  (1,0,0)  one worker, on the master's PE (OURS, Cnd = 0)
  (2,1,1)  one worker on PE 1
A worker range other than these cannot run on 1 PE: @node(K) with
K >= N is PIMOS's range_overflow, not modelled (refused).

Checked:
  - every run: Result = unsat, the print's (the one answer KL1 fixes:
    a refutation, whatever the schedule); stop "nothing left to run";
    no anomaly; every shoen accounted for (pimm_pe.shoen_accounting);
    the shoen tables and foster parents per PE after the query as
    before it;
  - Delta: it begins with the five axioms as typed (both terms; their
    first terms are the print's), Ncalc is its length, each derived
    key is (a worker node, a number rising on that node, dummy);
  - one worker: (2,1,1)'s Delta is (1,0,0)'s with node 0 made 1;
  - placement: in the query, disperse_node is placed once on each of
    Cnd..Tnd, and on N > 1 every worker PE other than 0 reduces;
  - PINS: Ncalc and the Listener's reductions of each run (OBSERVED;
    the model is deterministic, KL1 is not).
NOT checked against the print: Ncalc (18) and Delta's derived entries.
The master's `alternatively` (mgtpv0.kl1 master/9) tests Result
against the next step's J, which the workers bind in the same step,
and merge/2 orders the candidates as they arrive, so the step at which
unsat is seen and which candidate a node numbers first depend on the
schedule: on 6 PEs quota 1 gives Ncalc 33, quota 1,000,000 gives 21,
PIM/m printed 18.  How many of the print's 13 derived candidates are
in each Delta is printed.
Printed, not pinned: reductions per PE in the query (pe.reductions),
messages by kind, collections.

Observed 2026-11-26: m6 mgtpn: PASS (8 runs), every Result unsat;
Ncalc / Listener reductions (PINS): 6 PEs 33 / 2,406,271 (quota 1),
21 / 587,072 (1,000,000); 5 PEs 26 / 1,278,086, 21 / 594,582; one
worker 29 / 663,360 on 1 PE, 663,584 and 661,556 on 2.  The print: 18
/ 385,832.

Observed fault injections (M6_INJECT, the runner from M6_CACHE):
  - local (every @node on PE 0), on (6,1,5) and (2,1,1): 12 FAIL lines
    (placement, no worker reduces, pins: 31 / 1,989,309 and 29 /
    663,360); every Result still unsat
  - nowake (an exported variable bound without waking): 29 (no answer
    in any run, shoens and foster parents left)
  - oldwait (X = Y on one external cell refused, as before M6), 6 PEs:
    22 (the refusal, messages in flight, goals left, path never met)
  - lifo (each pair's channel LIFO; thousands of deliveries reversed):
    1, a pin, (5,0,4) at quota 1,000,000 (18 / 397,125); the 2- and
    6-PE runs unchanged: no check but a pin depends on the order
  (local and nowake were run before the goals-left and X = Y-path
  checks were added; their counts are of the earlier checks)

The heap limit: pimm.Machine.heap_limit = 24M cells on every PE (OURS):
without one, the second compile fills memory ("heap full"; the slim
machine leaves ~60M cells).  PIMOS's collections are then made by
PECollector at goal switches while the program runs.
"""
import json
import os
import pickle
import re
import sys
import tarfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import m5_boot as m5  # noqa: E402
import longrun_ipl as lr  # noqa: E402
import pimm  # noqa: E402
import pimm_pe  # noqa: E402
import fep as fepm  # noqa: E402

TGZ = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'ifs', 'solver-prover', 'pimos',
                   'MGTP-N', 'MGTP-N-KL1.tgz')
HEAP_LIMIT = 24 * 2 ** 20
T0 = time.time()


def say(text):
    print('%6.0fs %s' % (time.time() - T0, text))
    sys.stdout.flush()


def member(name):
    with tarfile.open(TGZ) as t:
        return t.extractfile('MGTP-N-KL1/' + name).read()


def serve():
    """mgtpv0.kl1 and util.kl1 as home files (this runner only)."""
    for name in ('mgtpv0.kl1', 'util.kl1'):
        text = member(name).decode('ascii')
        assert text.endswith('\n') and '\r' not in text
        data = b''.join(b'\x00\x09' if ch == '\t' else b'\x00\x0c' if ch == '\x0c' else fepm.jis(ch)
                        for ch in text)
        lr.HOME_FILES[name] = ('MGTP-N-KL1.tgz', name)
        lr._home[name] = fepm.FileData(
            data, 'PSI::%s>%s.1' % (lr.HOME, name),
            fepm.attribute_string('pmpsi', 'pmpsi', '20-May-93', '00:00:00', '20-May-93',
                                  '00:00:00', 1, len(data), 0))


# ---- the print (INSTALL.j) --------------------------------------------
def split0(s):
    """s split at its commas outside brackets."""
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '([{':
            depth += 1
        elif ch in ')]}':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    out.append(cur)
    return out


def printed():
    """(goal as printed, joined; {'Result', 'Ncalc', 'reductions',
    'Delta': [(key, first term)]}) from INSTALL.j."""
    lines = member('INSTALL.j').decode('iso2022_jp').split('\n')
    i = next(k for k, x in enumerate(lines) if x.startswith('[5] mgtpv0: main('))
    j = next(k for k in range(i, len(lines)) if lines[k].endswith('Result,Ncalc,Delta) . '))
    goal = (lines[i][len('[5] '):] + ''.join(x.strip() for x in lines[i + 1:j + 1])).strip()
    want = {}
    for x in lines[j:]:
        m = re.match(r'\s*Result=(\w+)', x)
        if m:
            want['Result'] = m.group(1)
        m = re.match(r'\s*Ncalc=\s*(\d+)', x)
        if m:
            want['Ncalc'] = int(m.group(1))
        m = re.match(r'\s*time=(\d+) reductions', x)
        if m:
            want['reductions'] = int(m.group(1))
    d = next(k for k, x in enumerate(lines) if x.startswith(' Delta='))
    delta = []
    for x in lines[d + 1:]:
        if x.strip().startswith('であった'):
            break
        m = re.match(r'\(\((\d+),(\d+),(\w+)\),(.*)', x)
        if not m:
            continue                # the print's note continued
        delta.append(((int(m.group(1)), int(m.group(2)), m.group(3)), split0(m.group(4))[0]))
    want['Delta'] = delta
    return goal, want


def goal_for(goal, c, t):
    """the printed goal with Cnd, Tnd and J's initial (Js, Ja, Jn) for
    workers c..t (the print's: 1, 5 and (1,1,2))"""
    assert goal.count('main(1,5,3,') == 1 and goal.count('(1,1,2,YYNN)') == 1
    return goal.replace('main(1,5,3,', 'main(%d,%d,3,' % (c, t)).replace(
        '(1,1,2,YYNN)', '(%d,%d,%d,YYNN)' % (c, c, c + 1 if t > c else c))


def answer(text):
    """the Listener's answer: Result, Ncalc, YYNN, reductions and Delta
    (each candidate's key and both terms)."""
    got = {}
    for k in ('Result', 'YYNN'):
        m = re.search(r' %s = (\w+)\n' % k, text)
        got[k] = m and m.group(1)
    m = re.search(r' Ncalc = (\d+)\n', text)
    got['Ncalc'] = m and int(m.group(1))
    m = re.findall(r' (\d+) reductions\n', text)
    got['reductions'] = int(m[-1]) if m else None
    m = re.search(r' Delta =\[(.*?)\]\n', text, re.S)
    delta = []
    if m:
        for item in split0(m.group(1)):
            assert item[0] == '(' and item[-1] == ')', item
            key, t1, t2 = split0(item[1:-1])
            a, b, w = split0(key[1:-1])
            delta.append([[int(a), int(b), w], t1, t2])
    got['Delta'] = delta if m else None
    return got


def shifted(delta, by):
    """Delta with every derived key's node moved by `by` (the axioms'
    (0,0,0) stay)."""
    return [[[k[0] + by if k[2] != '0' else k[0], k[1], k[2]], t1, t2] for k, t1, t2 in delta]


# ---- the System -----------------------------------------------------------
def drive(s, dev, quota):
    """m5_boot.boot's loop: run, the FEP, the alarms, the next scripted
    event; the stop."""
    b = s.pes[m5.BOOT]
    skips = 0
    try:
        while True:
            s.run(quota=quota, limit=10 ** 12)
            if b.scsi_poll():
                skips = 0
                continue
            armed = [pe for pe in s.pes if pe.alarm_var is not None]
            if armed:
                skips += 1
                if skips > 100:
                    raise pimm.Unimplemented('100 alarms in a row with nothing else to do')
                for pe in armed:
                    pe.alarm_skip()
                continue
            skips = 0
            if not dev.idle():
                break
    except pimm.Unimplemented as e:
        return 'refused: %s' % e
    except pimm.Fail as e:
        return 'Fail %s' % e
    except fepm.FepError as e:
        return 'FepError: %s' % e
    except Exception as e:
        return 'raised %s: %s' % (type(e).__name__, e)
    return 'nothing left to run, %d goals waiting' % sum(pe.nsusp for pe in s.pes)


def start(blob, loaded, n, lines):
    """m5_boot.boot's System, booted and driven to the end of lines."""
    s = pimm_pe.System(blob, n)
    for pe in s.pes:
        pe.ahead = True
        pe.tr = lr.GoTrace()
    b = s.pes[m5.BOOT]
    im = b.im
    boot_info = b.new_var()
    b.argv[1], b.argv[2] = pimm.marked(loaded), pimm.marked(boot_info)
    b.record(pimm.READY, pimm.predicate(im, 'top', 'go_pimos1/2'), b.argv[1:3])
    b.spawn(pimm.predicate(im, 'ipl', 'make_boot_info/1'), [boot_info])
    dev = b.fep = fepm.Fep(lr.kernel_file, getb_unit=2, lines=list(lines), list_dir=lr.home_listing)
    return s, dev, drive(s, dev, 1000000)


SETUP = ('compile', '!package work', 'util', 'mgtpv0', '!exit', 'listener',
         'default_package(work).', 'statistics.', 'print_depth(20).', 'print_length(100).')


def inject(kind):
    """M6_INJECT: one fault, in this (forked) process only."""
    if kind == 'local':         # every Goal@node(K) made on this PE
        pimm_pe.PE.node_number = lambda self, w: self.pe
    elif kind == 'lifo':        # each pair's channel LIFO, not FIFO
        def deliver(self, pe):
            for s in range(self.n):
                if s != pe.pe:
                    q = self.queues[(s, pe.pe)]
                    if len(q) > 1:
                        LIFO_FIRED[0] += 1
                    while q:
                        pe.receive(s, q.pop())
        pimm_pe.System.deliver = deliver
    elif kind == 'nowake':      # an exported variable bound without waking its goals
        pimm_pe.PE.bind = lambda self, ref, w: pimm.Machine.bind(self, ref, w)
    elif kind == 'oldwait':     # X = Y on one external cell refused, as before M6
        pimm_pe.PE.i_wait_value = pimm.Machine.i_wait_value
    elif kind:
        raise SystemExit('M6_INJECT: local, lifo, nowake or oldwait')


WAIT_PATH = 'wait_value of an external cell with itself'
LIFO_FIRED = [0]


def query(s, dev, goal, c, t, quota):
    """the goal typed and run (in a fork); the result as a dict."""
    inject(os.environ.get('M6_INJECT', ''))
    # a measurement: deliveries that find two or more messages waiting
    # in one pair's channel (where FIFO against LIFO can matter)
    multi = [0]
    deliver0 = pimm_pe.System.deliver

    def deliver(self, pe):
        multi[0] += sum(1 for k in range(self.n) if k != pe.pe and len(self.queues[(k, pe.pe)]) > 1)
        deliver0(self, pe)
    pimm_pe.System.deliver = deliver
    log0, placed0 = len(dev.log), len(s.placed)
    susp0 = sum(pe.nsusp for pe in s.pes)
    wait0 = sum(pe.paths.get(WAIT_PATH, 0) for pe in s.pes)
    red0 = [pe.reductions for pe in s.pes]
    gc0 = [pe.collections for pe in s.pes]
    sent0 = dict(s.sent)
    tab0 = m5.tables(s)
    dev.script.append(('getl', goal))
    t0 = time.time()
    stop = drive(s, dev, quota)
    text = ''.join(t for _d, t in dev.log[log0:])
    got = answer(text)
    places = {}
    for _src, k, code in s.placed[placed0:]:
        places.setdefault(code, []).append(k)
    return dict(
        got=got, stop=stop, seconds=round(time.time() - t0),
        reductions=[pe.reductions - r for pe, r in zip(s.pes, red0)],
        collections=[pe.collections - g for pe, g in zip(s.pes, gc0)],
        messages={pimm_pe.KIND_NAMES.get(k, k): v - sent0.get(k, 0) for k, v in sorted(s.sent.items())
                  if v != sent0.get(k, 0)},
        placed=sorted(places.values()), anomalies=[repr(a) for a in s.anomalies[:5]],
        accounting=[repr(a) for a in pimm_pe.shoen_accounting(s)[:5]],
        tables=m5.tables(s), tables_before=tab0, tail=text[-300:], multi=multi[0], lifo_fired=LIFO_FIRED[0],
        waiting=sum(pe.nsusp for pe in s.pes) - susp0,
        wait_path=sum(pe.paths.get(WAIT_PATH, 0) for pe in s.pes) - wait0)


def forked(fn, *args):
    r, w = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(r)
        try:
            out = json.dumps(fn(*args)).encode()
        except BaseException as e:      # noqa: B902
            out = json.dumps(dict(error='%s: %s' % (type(e).__name__, e))).encode()
        with os.fdopen(w, 'wb') as f:
            f.write(out)
        os._exit(0)
    os.close(w)
    with os.fdopen(r, 'rb') as f:
        data = f.read()
    os.waitpid(pid, 0)
    return json.loads(data)


RUNS = [(6, 1, 5), (5, 0, 4), (1, 0, 0), (2, 1, 1)]
# OBSERVED (N, Cnd, Tnd, quota) -> (Ncalc, the Listener's reductions):
# the model is deterministic, so these pin it; KL1 does not fix them
# (the master's `alternatively` races the step's test against the next
# step's J, and merge/2 orders the candidates as they come)
PINS = {(6, 1, 5, 1): (33, 2406271), (6, 1, 5, 1000000): (21, 587072),
        (5, 0, 4, 1): (26, 1278086), (5, 0, 4, 1000000): (21, 594582),
        (1, 0, 0, 1): (29, 663360), (1, 0, 0, 1000000): (29, 663360),
        (2, 1, 1, 1): (29, 663584), (2, 1, 1, 1000000): (29, 661556)}


def typed_axioms(goal):
    """main's Axiom argument, as Delta prints its entries."""
    args = split0(goal[goal.index('main(') + 5:goal.rindex(')')])
    out = []
    for item in split0(args[3][1:-1]):
        key, t1, t2 = split0(item[1:-1])
        a, b, w = split0(key[1:-1])
        out.append([[int(a), int(b), w], t1, t2])
    return out


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    runs = [tuple(int(x) for x in argv[i + 1].split(',')) for i, a in enumerate(argv) if a == '--run'] or RUNS
    quotas = [int(argv[i + 1]) for i, a in enumerate(argv) if a == '--quota'] or [1, 1000000]
    goal, want = printed()
    say('the print: Result %s, Ncalc %d, %d reductions, Delta of %d' % (
        want['Result'], want['Ncalc'], want['reductions'], len(want['Delta'])))
    serve()
    pimm.Machine.heap_limit = HEAP_LIMIT
    blob, loaded, _info = m5.slim(argv[1])
    bad, res = [], {}
    for n, c, t in runs:
        t0 = time.time()
        cache = os.environ.get('M6_CACHE') and os.path.join(os.environ['M6_CACHE'], 'n%d.pkl' % n)
        if cache and os.path.exists(cache):
            with open(cache, 'rb') as f:
                s, dev, stop = pickle.load(f)
        else:
            s, dev, stop = start(blob, loaded, n, SETUP)
            if cache:
                import io
                f = io.BytesIO()
                lr._pickler(f).dump((s, dev, stop))
                with open(cache, 'wb') as g:
                    g.write(f.getvalue())
        win = ''.join(x for _d, x in dev.log)
        say('N=%d workers %d..%d: booted and compiled in %.0fs, stop %s, instructions %r' % (
            n, c, t, time.time() - t0, stop, [pe.tr.instructions for pe in s.pes]))
        if not stop.startswith('nothing left') or '"work:: mgtpv0" Loaded' not in win \
                or not win.endswith('[5] '):
            bad.append(((n, c, t), 'setup', stop, win[-300:]))
            continue
        for q in quotas:
            r = forked(query, s, dev, goal_for(goal, c, t), c, t, q)
            res[(n, c, t, q)] = r
            if 'error' in r:
                bad.append(((n, c, t, q), r['error']))
                say('  quota %d: %s' % (q, r['error']))
                continue
            g = r['got']
            say('  quota %d: %ds, stop %s; Result %s, Ncalc %s, YYNN %s, %s reductions; Delta keys %r' % (
                q, r['seconds'], r['stop'], g['Result'], g['Ncalc'], g['YYNN'], g['reductions'],
                [tuple(k) for k, _a, _b in g['Delta'] or []]))
            say('    reductions per PE %r (sum %d), collections %r' % (
                r['reductions'], sum(r['reductions']), r['collections']))
            say('    messages %r' % r['messages'])
            say('    placed %r' % r['placed'])
            key = (n, c, t, q)
            if g['Result'] != 'unsat':
                bad.append((key, 'Result', g['Result'], r['tail']))
            if not r['stop'].startswith('nothing left'):
                bad.append((key, 'stop', r['stop']))
            for k in ('anomalies', 'accounting'):
                if r[k]:
                    bad.append((key, k, r[k]))
            if r['tables'] != r['tables_before']:
                bad.append((key, 'left: homes/foster parents per PE', r['tables'], r['tables_before']))
            if list(range(c, t + 1)) not in r['placed']:
                bad.append((key, 'disperse_node not placed on %d..%d once each' % (c, t), r['placed']))
            if n > 1 and any(r['reductions'][k] == 0 for k in range(max(c, 1), t + 1)):
                bad.append((key, 'a worker PE did not reduce', r['reductions']))
            if r.get('lifo_fired'):
                say('    lifo: %d deliveries reversed' % r['lifo_fired'])
            say('    goals left %d, reads unanswered %d, deliveries with 2+ waiting %d, %r %d' % (
                r['waiting'], r['messages'].get('read', 0) - r['messages'].get('answer_value', 0),
                r['multi'], WAIT_PATH, r['wait_path']))
            if r['waiting'] != r['messages'].get('read', 0) - r['messages'].get('answer_value', 0):
                bad.append((key, 'goals left are not the reads unanswered', r['waiting']))
            if (n, c, t) == (6, 1, 5) and not r['wait_path']:
                bad.append((key, 'X = Y on one external cell never met'))
    # the answers: what KL1 fixes, the print, and the observed pins
    axioms = typed_axioms(goal)
    for (n, c, t, q), r in sorted(res.items()):
        g = r.get('got')
        if not g:
            continue
        key = (n, c, t, q)
        delta = g['Delta'] or []
        if delta[:len(axioms)] != axioms:
            bad.append((key, 'Delta does not begin with the five axioms as typed'))
        if g['Ncalc'] != len(delta):
            bad.append((key, 'Ncalc is not the length of Delta', g['Ncalc'], len(delta)))
        if g['YYNN'] not in ('yes', 'no'):
            bad.append((key, 'YYNN', g['YYNN']))
        last = {}
        for k, _t1, _t2 in delta[len(axioms):]:
            if k[2] != 'dummy' or not c <= k[0] <= t or k[1] <= last.get(k[0], 0):
                bad.append((key, 'a derived key out of order or range', k))
                break
            last[k[0]] = k[1]
        if [x[1] for x in delta[:len(axioms)]] != [x[1] for x in want['Delta'][:len(axioms)]]:
            bad.append((key, 'the axioms differ from the print'))
        printed_terms = {x[1] for x in want['Delta'][len(axioms):]}
        both = sum(1 for x in delta[len(axioms):] if x[1] in printed_terms)
        say('%r: Ncalc %s (the print 18), %s reductions (the print 385832); of the print\'s %d derived '
            'candidates %d are in this Delta' % (key, g['Ncalc'], g['reductions'], len(printed_terms), both))
        if (n, c, t) == (2, 1, 1) and ('got' in res.get((1, 0, 0, q), {})):
            # one worker, on 1 PE and on 2: printed, not checked (KL1
            # does not fix the order merge/2 gives a step's candidates)
            one = shifted(res[(1, 0, 0, q)]['got']['Delta'] or [], 1)
            diff = [i for i, (a, b) in enumerate(zip(delta, one)) if a != b]
            same = sorted(map(str, delta)) == sorted(map(str, one))
            say('%r: one worker against (1,0,0): Delta entries differing %r, the same entries %s' % (
                key, diff, same))
        pin = PINS.get(key)
        if pin and (g['Ncalc'], g['reductions']) != pin:
            bad.append((key, 'pin (Ncalc, reductions)', (g['Ncalc'], g['reductions']), pin))
    if os.environ.get('M6_JSON'):
        with open(os.environ['M6_JSON'], 'w') as f:
            json.dump({'%d,%d,%d,%d' % k: v for k, v in res.items()}, f)
    for x in bad:
        print('FAIL', x)
    print('m6 mgtpn: %s (%d runs)' % ('FAIL' if bad else 'PASS', len(res)))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
