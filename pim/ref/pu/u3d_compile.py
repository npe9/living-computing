#!/usr/bin/env python3
"""U3d: make u3_goals.STREAM_CELLS again with the held PIMOS compiler, and
check them.  Not in run_tests.sh: it needs the prompt checkpoint.

    python3 ref/pu/u3d_compile.py PROMPT.pkl

PROMPT.pkl is the machine saved at the shell's prompt (bsv/README.md,
"The lockstep from a saved machine"; md5 75c7b1c62509fdf1d6926b0719f10dc5
for the checkpoint used 2026-11-28).  u3_goals.STREAM_SOURCE (OURS, 7
lines) is served as the home file pc.kl1 (longrun_ipl.add_home_file, this
process only) and compiled as R7 / R8 compile (lines 'compile', '!package
work', 'pc', '!exit'), on pimm.py; the module new_module makes is caught
as r7_sieve.py catches it.  Checked:

  - the compiler's answer: 'Compile Succeeded : pc' and '"work:: pc"
    Loaded' in the window;
  - the module's cells 15-61 equal u3_goals.STREAM_CELLS, tag and value
    (printed with asm/kbndis.py's decoder);
  - the cells are position free: go([1], A, B) and go([1, 2], A, B) run
    on a fresh pimm.Machine with the cells at two placements (0 and 37
    cells further on) give A = B = the list, the same instruction count
    at both, and 2 suspends and one bind waking 2 goals for [1].

Ends 'u3d compile: PASS' when all hold (about 30 s: 10 s to load the
checkpoint, 20 s of compile, 0.9 M pimm.py instructions).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pimm'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import kbndis  # noqa: E402
import lockstep_shell as ls  # noqa: E402
import pimm  # noqa: E402
import u3_goals as U3  # noqa: E402

LINES = ['compile', '!package work', 'pc', '!exit']


class Count:
    """The trace, counted, not kept."""
    def __init__(self):
        self.instructions = 0

    def append(self, line):
        if line[0] == 'I':
            self.instructions += 1


def compile_module(path):
    m, loaded, _info, kind = ls.load(path)
    assert kind == 'prompt'
    m.ahead = False
    ls.longrun.add_home_file('pc.kl1', U3.STREAM_SOURCE.encode('ascii'))
    made, builtin = [], m.builtin

    def watching(name, ops, f, **kw):
        if name == 'new_module':
            def g(*a):
                r = f(*a)
                made.append(r[0])
                return r
            return builtin(name, ops, g, **kw)
        return builtin(name, ops, f, **kw)
    m.builtin = watching
    sink = Count()
    _ops, _events, stop, dev = ls.play(m, loaded, kind, LINES, sink)
    window = ''.join(t for _d, t in dev.log)
    print('compile: %d instructions; stop %s' % (sink.instructions, stop))
    if not made:
        return window, None
    a = made[-1][1]
    n = m.mem[a][1] & 0xffffff
    return window, [tuple(m.mem[a + k]) for k in range(n + 1)]


def run_go(cells, items, pad):
    """go(items, A, B) on a fresh pimm.Machine, the cells pad cells on."""
    m = pimm.Machine()
    if pad:
        m.alloc(pad)
    a = m.alloc(len(cells))
    for i, w in enumerate(cells):
        m.mem[a + i] = w
    c = m.alloc(2 * len(items))
    for k, v in enumerate(items):
        m.mem[c + 2 * k] = (pimm.INT, v)
        m.mem[c + 2 * k + 1] = (pimm.LIST, c + 2 * k + 2) if k + 1 < len(items) else pimm.NIL
    A, B = m.new_var(), m.new_var()
    m.tr = []
    steps = m.run(a - m.load, [(pimm.LIST, c), A, B])
    susp = sum(1 for k, ln in enumerate(m.tr) if ln.startswith('I ') and
               ln.split()[2][2:4] == '69')
    woken = [ln for ln in m.tr if ln.startswith('W ')]
    return m.term(A), m.term(B), steps, susp, len(woken)


def main(argv):
    window, cells = compile_module(argv[1])
    ok = True
    for want in ('Compile Succeeded : pc', '"work:: pc" Loaded'):
        if want not in window:
            print('FAIL: the window lacks %r' % want)
            ok = False
    if cells is None:
        print('u3d compile: FAIL, no module made')
        return 1
    im = kbndis.Image()
    im.cells = cells + [(0, 0)] * 4
    im.mods = [dict(addr=-1, length=len(cells) - 1, preds=[], name='pc', package='work')]
    first = U3.STREAM_FIRST
    for i in range(len(cells)):
        print('  %3d  %02x %08x  %s' % (i, cells[i][0], cells[i][1], im.dis(i)))
    got = cells[first:first + len(U3.STREAM_CELLS)]
    if got != list(U3.STREAM_CELLS) or len(cells) != first + len(U3.STREAM_CELLS):
        print('FAIL: cells %d-%d differ from u3_goals.STREAM_CELLS (module of %d cells)'
              % (first, first + len(U3.STREAM_CELLS) - 1, len(cells)))
        ok = False
    for items in ([1], [1, 2]):
        runs = [run_go(U3.STREAM_CELLS, items, pad) for pad in (0, 37)]
        print('go(%r, A, B) at two placements: %r' % (items, runs))
        if any(r[:2] != (items, items) for r in runs) or runs[0] != runs[1]:
            print('FAIL: go(%r, A, B)' % items)
            ok = False
        if items == [1] and runs[0][3:] != (2, 2):
            print('FAIL: go([1], A, B): %d suspends, %d woken; want 2, 2' % runs[0][3:])
            ok = False
    print('u3d compile: %s' % ('PASS' if ok else 'FAIL'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
