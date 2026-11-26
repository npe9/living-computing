#!/usr/bin/env python3
"""Rung M5: PIMOS boots on N PEs, and a program runs from its prompt
with @node placement (docs/multi_pe.md 5, M5).

    python3 ref/pimm/m5_boot.py LINK.pkl [--n N ...] [--quota Q ...] [--app NAME ...]

LINK.pkl is the machine after the IPL's checked load and link, as
`longrun_ipl.py --reference --save FILE` writes it (14 GB loaded; not
in git).  M5_CACHE=PATH keeps the slimmed machine (below) between runs
(17 MB).  NOT part of run_tests.sh: one boot on one PE is ~30 s and
on N PEs minutes, and the checkpoint is 1.1 GB on disk.

What is done:
  1. The checkpoint is collected once on its one machine, with Loaded
     (load/4's answer: the atoms, the 480 modules, the comments, the
     entry code) a root: the IPL's file data dies, the modules live.
     73,594,186 heap cells become 1,016,836.  The one-PE boot from the
     slim machine (longrun_ipl.py --load SLIM --go --fep) is the same
     run as from the checkpoint itself: 8,595,408 instructions, the
     same console and FEP conversation, 1,218 goals waiting.
  2. A pimm_pe.System of N PEs is made from it, every PE a copy (OURS,
     docs/multi_pe.md 3).  The boot goal top:go_pimos1(Loaded,
     BootInfo) and ipl:make_boot_info(BootInfo) are made on the BOOT
     PE, 0, as longrun_ipl.go makes them on its one machine (the
     Pseudo PIM/m console throws the IPL goal to the boot PE:
     pimmcsp, docs/multi_pe.md 1.1; that PE 0 is it is OURS, its
     PARAM's default).  The FEP device (fep.py) is attached to PE 0,
     the cluster BootInfo names (make_boot_info gives cluster 0); a
     SCSI command on any other PE is refused by pimm.py.
  3. The System runs (quota Q goal switches a PE a turn) until no PE
     has a goal and no message is in flight; then, as longrun_ipl.go:
     the FEP's waiting commands are given it again; else every armed
     alarm is moved to (each PE its own clock: OURS); else the FEP's
     next scripted event (the login, then each typed line).
  4. Each app's lines are typed at the shell's prompt (lockstep_shell
     APPS's form); its answer is the text the Listener writes to the
     window (fep.py's log), compared with the one-PE run's.

Checked, per (N, quota):
  - the console is the one-PE run's (the banner, LOCAL LOGIN SERVICE
    STARTS, CANNOT MAKE A TCPIP LOGIN SERVICE!!) and the window shows
    "Shell>> "; each app's window text is the one-PE run's;
  - the one-machine run (longrun_ipl.go on the slim machine) and
    System(1) to the prompt: the same instructions, stop, console
    and FEP messages;
  - for each N, the prompt alone: the window ends "Shell>> ", no
    anomaly, every shoen's WTC, resource and foster parents accounted
    for (pimm_pe.shoen_accounting, m4_shoen.py's invariants); what it
    leaves (shoen tables and foster parents per PE) is the baseline;
  - after each app: no anomaly, the same accounting, and the same
    tables as the baseline (the app's shoens and foster parents gone);
  - sample9's job_ext placements are 0,1,..,N-1,0,1,.. (the primer's
    printed order, primer25.tex:1166-1168, for distribute(8) on 4).
Printed, not pinned: instructions per PE, messages by kind, goals
waiting per PE, each PE's new_atom counter.  A raise inside a run is
that run's stop (and FAIL lines), the other runs going on.

Observed 2026-11-26: m5 boot: PASS (12 runs: sample9 and qsort on
N = 1, 2, 4 under quota 1 and 1,000,000), about 7 minutes.

Observed fault injections (each on a private copy of pimm_pe.py, this
script run; docs/multi_pe.md 5, M5):
  - no module fetch: 12 FAIL lines (every N>1 run raises KeyError)
  - unbound/2 of an external variable answered here as unbound: 1
    (qsort N=2: the window shows R =[2,17,18|B])
  - every Goal@node made local: 1 (sample9 N=4: placement all 0)
  - unbound/2 of an exported value thrown to the owner too; current_node
    giving node 0 on every PE: nothing (PASS; both right, and only PE 0
    calls current_node here)
"""
import os
import pickle
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import fep as fepm  # noqa: E402
import pimm  # noqa: E402
import pimm_gc  # noqa: E402
import pimm_pe  # noqa: E402
import longrun_ipl as lr  # noqa: E402
import lockstep_cons as cons  # noqa: E402

T0 = time.time()
BOOT = 0
# the one-machine boot to the prompt (longrun_ipl.py --load ... --go
# --fep, from the checkpoint and from the slim machine alike)
PROMPT = (8595408, 'nothing left to run, 1218 goals waiting')


def say(text):
    print('%6.0fs %s' % (time.time() - T0, text))
    sys.stdout.flush()


def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9


# ---- the programs typed at the prompt ---------------------------------
# sample9 of the primer (primer25.tex:1138-1155), served from HOME as
# longrun_ipl serves sample1 (its lines as printed; module sample9,
# public distribute/1)
lr.HOME_FILES['sample9.kl1'] = (lr.PRIMER, 1138, 1155, ':- module sample9.', 'job :- true | true.')
# qsort of pkl1 (R8's qsort_r8.kl1) with its second recursive call
# placed by its pivot: qsort(L2, R1, R0)@node(X mod Nodes) (OURS, the
# least change that spreads the work; KL1's answer does not depend on
# placement)
lr.HOME_FILES['qsort_m5.kl1'] = (
    os.path.join(lr.PKL1, 'qsort.kl1'), None, None, lr.PKL1_HEAD,
    lr.PKL1_ADAPT['qsort.kl1'] + (
        ('drop', 29, 29),
        ('after', 29, '    partition(L, X, L1, L2), current_node(_, Ns), Nd := X mod Ns,'),
        ('after', 29, '    qsort(L2, R1, R0)@node(Nd), qsort(L1, R, [X|R1]).')))


def compile_and(file, goal):
    return ('compile', '!package work', file, '!exit', 'listener', 'default_package(work).', goal)


APPS = {
    'sample9': compile_and('sample9', 'sample9:distribute(8).'),
    'qsort': compile_and('qsort_m5', 'qsort:qsort([27,74,17,33,94,18,46,83,65,2],R).'),
}


# ---- the slim machine ---------------------------------------------------
def slim(link):
    cache = os.environ.get('M5_CACHE')
    if cache and os.path.exists(cache):
        with open(cache, 'rb') as f:
            return pickle.load(f)
    with open(link, 'rb') as f:
        m, loaded, info = pickle.load(f)
    say('checkpoint loaded: %d heap cells, rss %.1f GB' % (m.hp - m.load, rss()))
    box = [loaded]

    class Slim(pimm_gc.Collector):
        def more_roots(self):
            box[0] = self.word(box[0])

    m.tr = None
    line = Slim(m).run()
    say('collected with Loaded a root: %s, %d cells live' % (line, m.hp - m.heap_lo))
    out = (pimm_pe.dumps(m), box[0], info)
    del m
    if cache:
        with open(cache, 'wb') as f:
            pickle.dump(out, f, protocol=5)
    return out


# ---- the boot on a System -----------------------------------------------
def boot(blob, loaded, n, quota, lines):
    s = pimm_pe.System(blob, n)
    for pe in s.pes:
        pe.ahead = True
        pe.tr = lr.GoTrace()
    b = s.pes[BOOT]
    im = b.im
    boot_info = b.new_var()
    b.argv[1], b.argv[2] = pimm.marked(loaded), pimm.marked(boot_info)
    b.record(pimm.READY, pimm.predicate(im, 'top', 'go_pimos1/2'), b.argv[1:3])
    b.spawn(pimm.predicate(im, 'ipl', 'make_boot_info/1'), [boot_info])
    dev = b.fep = fepm.Fep(lr.kernel_file, getb_unit=2, lines=list(lines), list_dir=lr.home_listing)
    skips = 0
    stop = None
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
        stop = 'refused: %s' % e
    except pimm.Fail as e:
        stop = 'Fail %s' % e
    except fepm.FepError as e:
        stop = 'FepError: %s' % e
    except Exception as e:          # a raise: this run's stop, the others go on
        stop = 'raised %s: %s' % (type(e).__name__, e)
    if stop is None:
        stop = 'nothing left to run, %d goals waiting' % sum(pe.nsusp for pe in s.pes)
    return s, dev, stop


def tables(s):
    """(shoens with goals elsewhere, foster parents) on each PE."""
    return [(len(pe.homes), len(pe.fps)) for pe in s.pes]


def window(dev):
    return [t for _d, t in dev.log]


def placements(s):
    """The nodes of each @node goal by its code, for the codes placed
    exactly 8 times (sample9's job_ext/0: distribute(8)); in order."""
    by = {}
    for _src, k, code in s.placed:
        by.setdefault(code, []).append(k)
    return sorted(v for v in by.values() if len(v) == 8)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2

    def opts(flag, conv, default):
        v = [conv(argv[i + 1]) for i, a in enumerate(argv) if a == flag]
        return v or default
    ns = opts('--n', int, [1, 2, 4])
    quotas = opts('--quota', int, [1000000])
    apps = opts('--app', str, ['sample9', 'qsort'])
    blob, loaded, _info = slim(argv[1])
    say('slim machine: %d bytes pickled' % len(blob))
    bad = []
    # the prompt alone on one machine (longrun_ipl.go on the slim
    # machine), and on a System(1): the same run
    m = pickle.loads(blob)
    lbad, linfo = [], {}
    lr.go(m, loaded, linfo, lbad, True)
    one = linfo['go']
    del m
    s, dev, stop = boot(blob, loaded, 1, quotas[0], [])
    instr = s.pes[0].tr.instructions
    say('prompt, pimm.Machine: %d instructions, stop %s; System(1): %d, stop %s' % (
        one['instructions'], one['stop'], instr, stop))
    if (instr, stop) != PROMPT or (one['instructions'], one['stop']) != PROMPT or lbad:
        bad.append(('to the prompt', instr, stop, one['instructions'], one['stop'], PROMPT, lbad))
    if cons.console(s.pes[0].tr) != one['console'] or dev.messages != one['fep']['messages']:
        bad.append(('System(1) console or FEP messages differ from pimm.Machine',))
    # the prompt on each N: what the boot leaves (foster parents and
    # shoen tables per PE), the baseline for what an app may leave
    base = {}
    for n in ns:
        s, dev, stop = boot(blob, loaded, n, quotas[0], [])
        base[n] = tables(s)
        acc = pimm_pe.shoen_accounting(s)
        say('prompt N=%d: instructions %r, stop %s, homes/foster parents %r, messages %r' % (
            n, [pe.tr.instructions for pe in s.pes], stop, base[n],
            {pimm_pe.KIND_NAMES.get(k, k): v for k, v in sorted(s.sent.items())}))
        if acc or s.anomalies or window(dev)[-1:] != ['Shell>> '] or not stop.startswith('nothing'):
            bad.append(('prompt', n, acc, s.anomalies[:3], window(dev)[-1:], stop))
    runs = 0
    for app in apps:
        ref = None
        for n in ns:
            for q in quotas:
                t = time.time()
                runs += 1
                s, dev, stop = boot(blob, loaded, n, q, APPS[app])
                instr = [pe.tr.instructions for pe in s.pes]
                con = cons.console(s.pes[BOOT].tr)
                others = [cons.console(pe.tr) for pe in s.pes[1:]]
                win = window(dev)
                got = dict(console=con, window=win, stop=stop.split(',')[0])
                say('%s N=%d quota=%d: %.0fs, instructions %r (%d), stop %s' % (
                    app, n, q, time.time() - t, instr, sum(instr), stop))
                say('  messages %r' % {pimm_pe.KIND_NAMES.get(k, k): v for k, v in sorted(s.sent.items())})
                say('  goals waiting %r, new_atom %r, rss %.1f GB' % (
                    [pe.nsusp for pe in s.pes], [pe.next_atom for pe in s.pes], rss()))
                say('  console %r; others %r' % (con, others))
                say('  window %r' % (win,))
                if app == 'sample9':
                    pl = placements(s)
                    say('  placed 8 times: %r' % (pl,))
                    if [i % n for i in range(8)] not in pl:
                        bad.append((app, n, q, 'sample9 placement order', pl))
                acc = pimm_pe.shoen_accounting(s)
                if acc:
                    bad.append((app, n, q, 'shoen accounting', acc[:5]))
                if tables(s) != base[n]:
                    bad.append((app, n, q, 'left: homes/foster parents per PE', tables(s), base[n]))
                if s.anomalies:
                    bad.append((app, n, q, 'anomalies', s.anomalies[:5]))
                if any(others):
                    bad.append((app, n, q, 'console text on another PE', others))
                if ref is None:
                    ref = got
                    if n != 1:
                        bad.append(('the first run must be N=1', n))
                else:
                    for k in got:
                        if got[k] != ref[k]:
                            bad.append((app, n, q, '%s differs from N=1' % k, got[k], ref[k]))
                if not stop.startswith('nothing left to run'):
                    bad.append((app, n, q, 'stop', stop))
    for x in bad:
        print('FAIL', x)
    print('m5 boot: %s (%d runs)' % ('FAIL' if bad else 'PASS', runs))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
