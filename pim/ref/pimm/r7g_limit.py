#!/usr/bin/env python3
"""R7G stage 5 on the reference: a collection when memory runs out.

    python3 ref/pimm/r7g_limit.py PROMPT.pkl

PROMPT.pkl is the machine saved at the shell's prompt (bsv/README.md,
"The lockstep from a saved machine").  The rule (ref/pimm/pimm_gc.py,
"When memory runs out"; INFERENCE/OURS from M92 p. 430, PIMM.PARAM's
kl1_heap_limit, TR-469 and VPIM's heap-limit warning): with a heap
limit L (Machine.heap_limit), an allocation that takes the heap in use
past L - HEAP_INSURANCE asks for a collection at the next goal switch;
once the heap has been collected, one past L itself is the end.

The lines typed are r7g_gc.py's (APPS gc_listener): `gc`, the primer's
compile of sample1 into work, `gc`, the Listener's sieve.  Three runs
from the checkpoint, each in a process of its own (fork), with
Machine.ahead set as r7g_gc.py has it:

1. no limit: the two collections the shell's gc asks for (r7g_gc.py);
2. L = LIMIT (3,000,000 cells): the limit's collections as well;
3. L = LIMIT with the limit's request dropped (Machine.alloc's
   gc_request undone): the control, the session that would otherwise
   exhaust the heap.

Checked: run 2 makes more than the two collections asked for and gives
run 1's window, instructions, reductions and suspended goals, and the
same trace but for what a collection moves (r7g_gc.Kept); run 3 stops
with `heap full: past the heap limit` (after the shell's first gc has
collected, the limit binds and nothing collects again in time) before
the compile's window is written.

Ends `r7g limit: PASS`.  Measured 2026-11-25: see the docs
(binary_reverse_engineering.md 1.4, "R7G stage 5"); the counts are
printed.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import lockstep_shell as ls  # noqa: E402
import pimm  # noqa: E402
import r7g_gc  # noqa: E402

LIMIT = 3000000


def run(m, loaded, kind, limit, trigger):
    m.heap_limit = limit
    if not trigger:
        alloc = pimm.Machine.alloc

        def no_request(self, n):
            asked = self.gc_request
            a = alloc(self, n)
            self.gc_request = asked
            return a
        pimm.Machine.alloc = no_request
    sink = r7g_gc.Kept()
    try:
        _ops, _events, stop, dev = ls.play(m, loaded, kind, r7g_gc.LINES, sink)
    except RuntimeError as e:
        stop, dev = 'RuntimeError: %s' % e, m.fep
    window = [t for _d, t in dev.log][4:]
    return dict(stop=stop, window=window, instructions=sink.instructions, steps=m.steps,
                reductions=m.reductions, nsusp=m.nsusp, k=sink.k,
                paths=getattr(m, 'gc_paths', None), trace_hash=hash(tuple(sink.lines)),
                trace_lines=len(sink.lines))


def main(argv):
    m, loaded, _info, kind = ls.load(argv[1])
    assert kind == 'prompt'
    m.ahead = True
    got = {}
    for name, limit, trigger in (('free', 0, True), ('limit', LIMIT, True),
                                 ('control', LIMIT, False)):
        r, w = os.pipe()
        pid = os.fork()
        if pid == 0:
            os.close(r)
            try:
                out = run(m, loaded, kind, limit, trigger)
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
        got[name] = eval(data.decode())               # our own repr
        print('%s: %r' % (name, {k: v for k, v in got[name].items() if k != 'window'}), flush=True)
    free, lim, ctl = got['free'], got['limit'], got['control']
    if any('error' in g for g in got.values()):
        print('r7g limit: FAIL')
        return 1
    ok = (len(free['k']) == 2 and len(lim['k']) > 2
          and lim['window'] == free['window']
          and all(lim[x] == free[x] for x in ('stop', 'instructions', 'steps', 'reductions',
                                              'nsusp', 'trace_hash', 'trace_lines'))
          and ctl['stop'] == 'RuntimeError: heap full: past the heap limit'
          and '"work:: sample1" Loaded\n' not in ctl['window'])
    if not ok:
        print('r7g limit: FAIL')
        return 1
    print('r7g limit: PASS (the limit %d: %d collections, %d of them the limit\'s, and the run '
          'as without the limit, %d instructions, the same window and trace; with the limit\'s '
          'request dropped the run stops: %s, at %d instructions, %d K line(s))'
          % (LIMIT, len(lim['k']), len(lim['k']) - 2, lim['instructions'], ctl['stop'],
             ctl['instructions'], len(ctl['k'])))
    for line in lim['k']:
        print('  ' + line)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
