#!/usr/bin/env python3
"""R7G on the reference: the shell's `gc` collects, and nothing the
machine does afterwards changes.

    python3 ref/pimm/r7g_gc.py PROMPT.pkl

PROMPT.pkl is the machine saved at the shell's prompt (bsv/README.md,
"The lockstep from a saved machine").  The lines typed: `gc`, the
primer's compile of sample1 into the package work (APPS compile_work),
`gc` again, then the Listener's sieve (APPS listener_sieve):

    gc
    compile / !package work / sample1 / !exit
    gc
    listener / default_package(work). / sample1:sieve([1,2,3],E,O).

Two runs from the checkpoint, each in a process of its own (fork),
Machine.ahead set (it was needed while collect_garbage was the
reference's alone; since the core's PimmGcBox.bsv, 2026-11-25, the same
session runs in lockstep, APPS gc_listener, and this test is the
collection against none):

1. Collected (ref/pimm/pimm_gc.py, INFERENCE/OURS: its header).
2. Not collected: collect_garbage still asks, the request is dropped.

Checked: run 1 has two K lines, the first copying above the old heap
and the second back to the heap's first cell (the halves alternate);
both runs give the same window (the compiler's, `"work:: sample1"
Loaded`, the Listener's ` E =[2]` and ` O =[1,3]`), the same number of
instructions, reductions and suspended goals, and the same trace but
for the K lines, the M lines and the addresses in R, A, V, G and W lines
(an instruction's cell, not its pc: moved code has a new one; an E
line and a B line are compared as they are: the device sees the same bytes).  So no root was lost and no
variable split: a missed one would show as a different run.

Which collector paths ran (Collector.counts, the second collection's
and the first's) is printed; the paths a shell `gc` does not reach are
named NOT run in the docs (binary_reverse_engineering.md 1.4, "R7G").

Ends `r7g gc: PASS`.  Measured 2026-11-25: K lines
`K gc 32768 77892213 77892213 79768684 a8652141` (77.86M cells to
1.88M) and `K gc 77892213 82173730 32768 2452104 638807af`, 1,752,873
instructions, 1607 goals suspended either way.  Paths (the second
collection's counts): goal 3397, suspension 7548, shoen 20, module 481,
code 3242, string 15852, long vector 1705, a structure partly copied
1325, merge_in record 553, a waiting SCSI command 1, the current shoen
1; NOT run: a parked goal list, to_processor's code argument, the
merger's lists (mq, mwh) and the alarm's variable as roots.

Injections (ref/pimm/pimm_gc.py, each from a backup copy, restored by
copy, cmp clean; OBSERVED):
- the waiting SCSI command's three variables not moved: the collected
  run stops on KeyError(3835951574), a freed cell; FAIL.
- the merge_in goal's record not moved: KeyError(3835970626); FAIL.
- a partly copied structure's unbound cell given as a reference to the
  variable's copy, not the variable moved in: the windows and counts
  agree, the trace does not (chunks 12 and 212 of 10000 lines: `R 4
  07` where the run without collection has `R 4 02`, a read_variable
  that finds a reference where the variable, bound since, was); FAIL.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import lockstep_shell as ls  # noqa: E402
import pimm  # noqa: E402
import pimm_gc  # noqa: E402

LINES = ['gc', 'compile', '!package work', 'sample1', '!exit', 'gc',
         'listener', 'default_package(work).', 'sample1:sieve([1,2,3],E,O).']


class Kept:
    """The trace, with what a collection moves left out: M lines, and
    the values of R, A, V lines and the addresses of G, W lines (kept as
    their kinds, so that the order of events is compared)."""
    def __init__(self):
        self.lines = []
        self.k = []
        self.instructions = 0

    def append(self, line):
        c = line[0]
        if c == 'I':
            self.instructions += 1
            self.lines.append('I ' + line.split()[2])     # the pc of moved code moves
        elif c == 'K':
            self.k.append(line)
        elif c == 'M':
            pass
        elif c in 'RAV':
            n, w = line[2:].split()
            self.lines.append('%s %s %s' % (c, n, w[:2]))
        elif c in 'GW':
            self.lines.append(c)
        else:
            self.lines.append(line)


def run(m, loaded, kind, collect):
    if not collect:
        pimm_gc.collect = lambda _m: None
    sink = Kept()
    _ops, _events, stop, dev = ls.play(m, loaded, kind, LINES, sink)
    window = [t for _d, t in dev.log][4:]
    if os.environ.get('R7G_DUMP'):         # debugging: one chunk's lines to a file
        i = int(os.environ['R7G_DUMP'])
        with open(os.environ['R7G_DUMP_TO'] + ('.on' if collect else '.off'), 'w') as f:
            f.write('\n'.join(sink.lines[i * 10000:(i + 1) * 10000]) + '\n')
    return dict(stop=stop, window=window, instructions=sink.instructions, steps=m.steps,
                reductions=m.reductions, nsusp=m.nsusp, k=sink.k,
                counts=getattr(m, 'gc_counts', None), trace_hash=hash(tuple(sink.lines)),
                chunks=[hash(tuple(sink.lines[i:i + 10000]))
                        for i in range(0, len(sink.lines), 10000)],
                trace_lines=len(sink.lines))


def main(argv):
    m, loaded, _info, kind = ls.load(argv[1])
    assert kind == 'prompt'
    m.ahead = True
    got = {}
    for collect in (True, False):
        r, w = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(r)
            try:
                out = run(m, loaded, kind, collect)
            except BaseException as e:      # noqa: B902 -- reported by the parent
                out = dict(error=repr(e))
            os.write(w, repr(out).encode())
            os._exit(0)
        os.close(w)
        data = b''
        while True:
            chunk = os.read(r, 1 << 16)
            if not chunk:
                break
            data += chunk
        os.waitpid(pid, 0)
        got[collect] = eval(data.decode())               # our own repr
        print('%s: %r' % ('collected' if collect else 'not collected',
                          {k: v for k, v in got[collect].items() if k != 'chunks'}))
    on, off = got[True], got[False]
    diff = [i for i, (a, b) in enumerate(zip(on.get('chunks', []), off.get('chunks', []))) if a != b]
    print('trace chunks of 10000 lines that differ: %s' % diff[:10])
    if 'error' in on or 'error' in off:
        print('r7g gc: FAIL')
        return 1
    k = [line.split() for line in on['k']]
    ok = (len(k) == 2 and off['k'] == []
          and int(k[0][4]) == int(k[0][3])              # the first: above the old heap
          and int(k[1][4]) == pimm.HEAP                 # the second: at the heap's start
          and on['window'] == off['window']
          and on['window'][-2] == ' E =[2]\n O =[1,3]\n\n'
          and '"work:: sample1" Loaded\n' in on['window']
          and all(on[x] == off[x] for x in ('stop', 'instructions', 'steps', 'reductions', 'nsusp',
                                            'trace_hash', 'trace_lines')))
    if not ok:
        print('r7g gc: FAIL')
        return 1
    print('r7g gc: PASS (two collections, %s and %s; the run after them as without them: '
          '%d instructions, %d goals suspended, the same window and trace)'
          % (' '.join(k[0][2:]), ' '.join(k[1][2:]), on['instructions'], on['nsusp']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
