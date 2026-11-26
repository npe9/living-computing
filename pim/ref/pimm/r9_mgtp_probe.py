#!/usr/bin/env python3
"""R9's probe: MGTP/G (IFS No.22) on PIMOS, on the reference model
(2026-11-26).  OURS, not in the suite: it needs a prompt checkpoint
(bsv/README.md, "The lockstep from a saved machine"), ~1.1 GB, not in
git.

    python3 ref/pimm/r9_mgtp_probe.py PROMPT.pkl [SESSION|APPS-ROW ...]

Types each session (SESSIONS below, or a row of lockstep_shell.APPS)
from the reference's prompt checkpoint, in a fork, and prints the
counts, the stop and the window's last R9_TAIL (4) parts; for an APPS
row, whether the window is the row's.  The files are the home files
of longrun_ipl.HOME_FILES (MGTP/G's four from the held mgtp.tgz, and
q6.clause / q8.clause, the manual's 8-Queens axioms and the same cut
to 6).  Measurements, each OURS and in this process only:
  R9_TALLY=1   the reductions of each shoen whose total the Listener
               reported, split into our stubs (pimm_stubs) by name and
               'kl1' for all other code
  R9_MARKS=1   mark_element on a list cell counted, by Position, and
               the cells it wrote
  R9_INJECT=   car / none / pos2: mark_element on a list made wrong
               (the discriminating checks, lockstep_mklist.py)

Observed 2026-11-26 (from the prompt checkpoint at 8,595,408
instructions, made afresh from the link checkpoint):
  compile: preotter and otter compile and load in package work,
      19,944,332 instructions; otter ends with
      `undefined module : work:: mgtp`, the axioms' module not yet
      made, as the manual's order has it.
  q6 (before mark_element on lists): compiling q6.clause stopped with
      `refused: mark_element of (5, ...), (0, 0)` at 20,191,261.
  After it (pimm.py i_mark_element, the list case): the rows mgtp_q6,
      mgtp_q8 and mgtp_pf6 of lockstep_shell.APPS run to the
      Listener's answer: 4 models for 6, 92 for 8, each an N-Queens
      solution; 21,497 reductions for 6 and 438,279 for 8 on MERC
      (the manual: 18,759 and 384,567), 11,048 for 6 on PF (10,949).
      Do(6, M) and do(100, M) give what do(20, M) gives.
  R9_TALLY: the query's shoen on MERC 6 is 17,695 reductions of KL1
      code, 3,801 of our merger stub merge_in, 1 of apply: without the
      stub 17,696 (the manual's 18,759 is 6.0% more); on PF 6, 9,959 of
      KL1, 214 merge_in, 534 b_add and 340 set_vector_element stubs
      (waiting body built-ins), 1 apply.
  R9_MARKS: in the whole mgtp_q6 run mark_element meets a list once,
      Position 0, and writes nothing (the car already marked).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockstep_shell as ls  # noqa: E402
import longrun_ipl as L  # noqa: E402

STAT = ['listener', 'default_package(work).', 'statistics.', 'print_depth(10).',
        'print_length(100).']


def merc(axioms, n=20):
    """MGTP/G/MERC by the manual's procedure (manualE.tex 86-128)"""
    return ['compile', '!package work', 'preotter', 'otter', '!attach clause clause_trans_o',
            axioms, '!exit', 'relink(hyper_o)', 'relink(work::hyper_o)'] + STAT + [
                'hyper_o:do(%d,M).' % n]


def pf(axioms, n=20):
    """MGTP/G/MERC/PF by the manual's procedure (manualE.tex 132-178)"""
    return ['compile', '!package work', 'prerotter', 'rotter', '!attach clause clause_trans_r',
            axioms, '!exit', 'relink(hyper_r)', 'relink(work::hyper_r)'] + STAT + [
                'hyper_r:do(%d,M).' % n]


SESSIONS = {
    'compile': ['compile', '!package work', 'preotter', 'otter', '!exit'],
    'q6': ['compile', '!package work', 'preotter', 'otter', '!attach clause clause_trans_o',
           'q6.clause', '!exit', 'relink(hyper_o)', 'listener', 'default_package(work).',
           'hyper_o:do(20,M).'],
    # the Listener's statistics on (debugger/listener/task_mon.kl1
    # display_statistics: " N reductions", " T msec" after the answer)
    # and the models printed whole
    'q6s': merc('q6.clause'),
    'q6s6': merc('q6.clause', 6),
    'q6s100': merc('q6.clause', 100),
    'q8s': merc('q8.clause'),
    'q6r': (merc('q6.clause')[:9] + ['relink(work,work::hyper_o,[work::mgtp])']
            + merc('q6.clause')[9:]),
    'pf6s': pf('q6.clause'),
    'pf8s': pf('q8.clause'),
}


class Null:
    def write(self, s):
        pass


def install_tally(m):
    """R9_TALLY=1: the reductions (pimm.Machine.chain at each
    end_reduction, what SH_REDUCTIONS adds up) of the runs made after
    the last typed line was taken, split by the goal's code: our stubs
    (pimm_stubs: a waiting body built-in, the merger's merge_in, a
    structure unification's unify_step, to_processor), by name, and
    'kl1' for every other code, for each shoen (its own and its
    descendants').  Printed: the shoens whose total is one the Listener
    reported (its window's " N reductions").  OURS, a measurement only."""
    tally = {}      # shoen -> {kind: reductions}, the shoen's and below
    names = {v['addr']: k for k, v in m.stubs.items()}
    reduce0, end0 = m.reduce, m.end_reduction
    cur = [None]

    def reduce(code, *a):
        cur[0] = code
        return reduce0(code, *a)

    def end_reduction():
        if not m.fep.script and m.chain:
            k = names.get(cur[0], 'kl1')
            for sh in m.chain_of(m.shoen):
                t = tally.setdefault(sh, {})
                t[k] = t.get(k, 0) + m.chain
        return end0()
    m.reduce, m.end_reduction = reduce, end_reduction
    return tally


def install_injection(how):
    """R9_INJECT=HOW: mark_element on a list cell made wrong, in this
    process only (pimm.Machine.i_mark_element patched; a vector is as
    before): `car` marks the car whatever the Position, `none` marks
    nothing, `pos2` takes Position 2 too (the cell after the cdr).
    For the discriminating checks of the list case (R9)."""
    import pimm
    orig = pimm.Machine.i_mark_element

    def wrong(self, pc, x, y, z, c16):
        v, i = self.deref(self.reg[x]), self.deref(self.reg[y])
        if v[0] & ~1 != pimm.LIST or i[0] & ~1 != pimm.INT:
            return orig(self, pc, x, y, z, c16)
        if how == 'car':
            self.taken(v[1], mark=True)
        elif how == 'pos2' and i[1] < 3:
            self.taken(v[1] + i[1], mark=True)
        elif how == 'pos2' or how != 'none':
            return orig(self, pc, x, y, z, c16)
    pimm.Machine.i_mark_element = wrong


def install_marks():
    """R9_MARKS=1: mark_element on a list cell counted over the whole
    run, by Position, and the cells it wrote (the MRB was off)."""
    import pimm
    orig = pimm.Machine.i_mark_element
    marks = {}

    def counted(self, pc, x, y, z, c16):
        v, i = self.deref(self.reg[x]), self.deref(self.reg[y])
        if v[0] & ~1 == pimm.LIST and i[0] & ~1 == pimm.INT:
            k = 'list %d' % i[1]
            marks[k] = marks.get(k, 0) + 1
            if self.mem[v[1] + i[1]] != pimm.marked(self.mem[v[1] + i[1]]) and \
                    self.mem[v[1] + i[1]][0] & ~1 not in (pimm.UNDF, pimm.HOOK):
                marks['writes'] = marks.get('writes', 0) + 1
        return orig(self, pc, x, y, z, c16)
    pimm.Machine.i_mark_element = counted
    return marks


def main():
    m, loaded, info, kind = ls.load(sys.argv[1])
    m.ahead = False
    names = sys.argv[2:] or list(SESSIONS)
    tail = int(os.environ.get('R9_TAIL', '4'))
    for n in names:
        pid = os.fork()
        if pid == 0:
            m.heap_limit = 0
            m.gc_paths = None
            log0 = len(m.fep.log)
            sink = ls.Sink(Null())
            tally = install_tally(m) if os.environ.get('R9_TALLY') else None
            if os.environ.get('R9_INJECT'):
                install_injection(os.environ['R9_INJECT'])
            marks = install_marks() if os.environ.get('R9_MARKS') else None
            typed = SESSIONS[n] if n in SESSIONS else ls.APPS[n][0]
            _o, _e, stop, dev = ls.play(m, loaded, kind, list(typed), sink)
            win = [t for _d, t in dev.log[log0:]]
            if tally is not None:
                said = {int(x) for x in re.findall(r'(\d+) reductions', ''.join(win))}
                tally = {'%d' % sh: t for sh, t in tally.items() if sum(t.values()) in said}
            print(json.dumps(dict(name=n, instructions=sink.instructions, lines=sink.lines,
                                  stop=str(stop)[:300], window=win[-tail:], tally=tally,
                                  marks=marks,
                                  apps=n in ls.APPS and tuple(win) == tuple(ls.APPS[n][1]))),
                  flush=True)
            os._exit(0)
        os.waitpid(pid, 0)


if __name__ == '__main__':
    main()
