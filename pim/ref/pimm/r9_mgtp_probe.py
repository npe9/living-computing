#!/usr/bin/env python3
"""R9's first probe: MGTP/G (IFS No.22) on PIMOS, on the reference
model (2026-11-26).  OURS, not in the suite: it needs a prompt
checkpoint (bsv/README.md, "The lockstep from a saved machine"),
~1.1 GB, not in git.

    python3 ref/pimm/r9_mgtp_probe.py PROMPT.pkl [compile|q6 ...]

Extracts `docs/nonlocal/ifs/solver-prover/pimos/MGTP/mgtp.tgz` (held,
ICOT Free Software) into a temporary directory and serves its four
.kl1 files, plus our 6-Queens axioms `q6.clause` (Q6 below), as home
files: private entries of longrun_ipl.HOME_FILES in this process
only, so the suite's `ls` pin and the FEP card are unchanged. Then it
types each session from the reference's prompt checkpoint, in a fork,
and prints the counts, the stop and the window's last lines.

q6.clause is INFERENCE/OURS: the manual (mgtp/manualE.tex, lines
213-224) prints the 8-Queens axioms, which we cut to 6. Its 4 models
(the 6-Queens solutions) and the manual's 18,759 reductions for N = 6
on MGTP/G/MERC are the values R9 will check.

Observed 2026-11-26 (from the R8 second half's prompt checkpoint,
8,595,408 instructions):
  compile: preotter and otter compile and load in package work,
      19,944,332 instructions; otter ends with
      `undefined module : work:: mgtp` (the axioms' module is not yet
      made; the manual's order has it).
  q6: `!attach clause clause_trans_o` is accepted
      (`Preprocess : clause => pkl1 : clause_trans_o`); compiling
      q6.clause stops in the reference with
      `refused: mark_element of (5, ...), (0, 0)`: mark_element on a
      list cell, which pimm.py refuses. That is R9's next item
      (docs/pimos_roadmap.md, R9).
"""
import json
import os
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lockstep_shell as ls  # noqa: E402
import longrun_ipl as L  # noqa: E402

TGZ = os.path.join(HERE, '..', '..', 'docs', 'nonlocal', 'ifs', 'solver-prover', 'pimos',
                   'MGTP', 'mgtp.tgz')
FILES = ('preotter.kl1', 'otter.kl1', 'prerotter.kl1', 'rotter.kl1')

Q6 = """\
% 6-Queens for MGTP/G/MERC: the 8-Queens axioms of manualE.tex
% (lines 213-224) cut to 6 (INFERENCE: OURS, the manual prints 8)
(q(1,1);q(1,2);q(1,3);q(1,4);q(1,5);q(1,6)),
(q(2,1);q(2,2);q(2,3);q(2,4);q(2,5);q(2,6)),
(q(3,1);q(3,2);q(3,3);q(3,4);q(3,5);q(3,6)),
(q(4,1);q(4,2);q(4,3);q(4,4);q(4,5);q(4,6)),
(q(5,1);q(5,2);q(5,3);q(5,4);q(5,5);q(5,6)),
(q(6,1);q(6,2);q(6,3);q(6,4);q(6,5);q(6,6)) :- true.

false :- {(X0-X1)*(Y0-Y1)*(X0-X1-Y0+Y1)*(X0-X1+Y0-Y1)=:=0},
         {(X0-X1)*(X0-X1)+(Y0-Y1)*(Y0-Y1)=\\=0},q(X0,Y0),q(X1,Y1).
"""

SESSIONS = {
    'compile': ['compile', '!package work', 'preotter', 'otter', '!exit'],
    'q6': ['compile', '!package work', 'preotter', 'otter', '!attach clause clause_trans_o',
           'q6.clause', '!exit', 'relink(hyper_o)', 'listener', 'default_package(work).',
           'hyper_o:do(20,M).'],
}


class Null:
    def write(self, s):
        pass


def serve(d):
    with tarfile.open(TGZ) as t:
        for mem in t.getmembers():
            base = os.path.basename(mem.name)
            if mem.isfile() and base in FILES:
                with open(os.path.join(d, base), 'wb') as f:
                    f.write(t.extractfile(mem).read())
    for n in FILES:
        L.HOME_FILES[n] = (os.path.join(d, n), None, None, '%', None)
    q6 = os.path.join(d, 'q6.clause')
    with open(q6, 'w') as f:
        f.write(Q6)
    L.HOME_FILES['q6.clause'] = (q6, None, None, '%', None)


def main():
    m, loaded, info, kind = ls.load(sys.argv[1])
    m.ahead = False
    names = sys.argv[2:] or list(SESSIONS)
    with tempfile.TemporaryDirectory() as d:
        serve(d)
        for n in names:
            pid = os.fork()
            if pid == 0:
                m.heap_limit = 0
                m.gc_paths = None
                log0 = len(m.fep.log)
                sink = ls.Sink(Null())
                _o, _e, stop, dev = ls.play(m, loaded, kind, list(SESSIONS[n]), sink)
                win = [t for _d, t in dev.log[log0:]]
                print(json.dumps(dict(name=n, instructions=sink.instructions, lines=sink.lines,
                                      stop=str(stop)[:300], window=win[-4:])), flush=True)
                os._exit(0)
            os.waitpid(pid, 0)


if __name__ == '__main__':
    main()
