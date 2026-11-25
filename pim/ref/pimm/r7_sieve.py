#!/usr/bin/env python3
"""R7 on the reference: compile the primer's sample1 into the package
`work`, then run the module it made, sieve([1,2,3],E,O).

    python3 ref/pimm/r7_sieve.py PROMPT.pkl

PROMPT.pkl is the machine saved at the shell's prompt (bsv/README.md,
"The lockstep from a saved machine").  The lines typed are APPS
`compile_work`'s (lockstep_shell.py): `compile`, `!package work`,
`sample1`, `!exit`; the compiler loads the module as
`"work:: sample1" Loaded`.  The module is the last one new_module made
(the loader's, library/loader/loader.kl1), caught by wrapping the
reference's built-in.  Its code is then disassembled with
asm/kbndis.py's decoder and its sieve/3 run as a goal of the root, the
arguments built here: the primer runs the same goal in the Listener
(primer25.tex:1343-1349, `[1] sample1:sieve([1,2,3],E,O).`, E = [2],
O = [1,3]).  The Listener itself is not reached
(docs/binary_reverse_engineering.md 1.4), so this is the goal, not
the primer's session: OURS how it is started.  Reference only; the
compile it rests on is in lockstep on the core (run_pimm_apps.sh
compile_work).  Ends `r7 sieve: PASS` when E and O are the primer's.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import kbndis  # noqa: E402
import lockstep_shell as ls  # noqa: E402
import pimm  # noqa: E402

LINES = ['compile', '!package work', 'sample1', '!exit']


class Count:
    """The trace, counted, not kept."""
    def __init__(self):
        self.lines = 0
        self.instructions = 0

    def append(self, line):
        self.lines += 1
        if line[0] == 'I':
            self.instructions += 1


def main(argv):
    m, loaded, _info, kind = ls.load(argv[1])
    assert kind == 'prompt'
    m.ahead = False
    made = []
    builtin = m.builtin

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
    window = [t for _d, t in dev.log]
    print('compile: %d instructions, %d trace lines; stop %s' % (sink.instructions, sink.lines, stop))
    print('window:', ''.join(window[-6:]).replace('\n', ' | '))
    if not made:
        print('r7 sieve: FAIL, no module made')
        return 1
    mod = made[-1]
    a = mod[1]
    n = m.mem[a][1] & 0xffffff
    im = kbndis.Image()
    # a stand-in image of the module alone, indexed by the offset from
    # its descriptor, so a label @N is offset N; the compile's new atoms
    # (the module's and the predicate's names) have no name in the
    # image's table and print as #number
    im.cells = [tuple(m.mem[a + k]) for k in range(n + 1)] + [(0, 0)] * 4
    heads = [i for i in range(1, n + 1) if im.cells[i][0] == pimm.PREDH]
    im.mods = [dict(addr=-1, length=n, preds=[], name='sample1', package='work')]
    print('module: %d elements, predicate heads at %r' % (n, heads))
    for i in range(n + 1):
        print('  %3d  %02x %08x  %s' % (i, im.cells[i][0], im.cells[i][1], im.dis(i)))
    if len(heads) != 1:
        print('r7 sieve: FAIL, %d predicates' % len(heads))
        return 1
    m.builtin = builtin
    pc = a + heads[0] + 2 - m.load            # the code after the head's two cells
    cells = m.alloc(6)
    for k, v in enumerate((1, 2, 3)):
        m.mem[cells + 2 * k] = (pimm.INT, v)
        m.mem[cells + 2 * k + 1] = (pimm.LIST, cells + 2 * k + 2) if k < 2 else (pimm.ATOM, 0)
    e, o = m.new_var(), m.new_var()
    try:
        steps = m.run(pc, [(pimm.LIST, cells), e, o])
    except pimm.Suspend:
        steps = None              # the shell's own goals still wait
    got = (m.term(e), m.term(o))
    print('sieve([1,2,3],E,O): E = %r, O = %r%s' % (
        got[0], got[1], '' if steps is None else ' (%d instructions)' % steps))
    if got != ([2], [1, 3]):
        print('r7 sieve: FAIL')
        return 1
    print('r7 sieve: PASS (the module the PIMOS compiler made from the primer\'s sample1, '
          'run on the reference: E = [2], O = [1,3], as primer25.tex:1343-1349)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
