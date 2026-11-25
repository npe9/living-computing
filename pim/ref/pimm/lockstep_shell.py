#!/usr/bin/env python3
"""Lockstep from a saved machine: PIMOS on the Bluespec core, from the
end of the IPL's link or from the shell's prompt, through the lines
typed, compared line by line with the reference model.

    python3 ref/pimm/lockstep_shell.py make PKL DIR [--type LINE ...]
        DIR/heap.hex     the saved machine's heap, for the bench's memory
        DIR/script.hex   the RESTORE operations, then RUN and POLL as
                         longrun_ipl.py go() runs, then the device tape
        DIR/trace        the reference model's trace of that script
        DIR/want.json    its counts, the console, the stop
    sim_pimm_shell | python3 ref/pimm/lockstep_shell.py compare DIR
    python3 ref/pimm/lockstep_shell.py splices PKL [--type LINE ...]
        the reference alone: the merger's splices onto a non-empty list

Run by bsv/run_pimm_shell.sh.  NOT part of run_tests.sh: the saved
machines are ~1.1 GB pickles that the IPL's link makes in 15-50 min
(longrun_ipl.py --reference --save), not kept in git.

PKL is either
  - the machine after the link (longrun_ipl.py --save FILE): the script
    then begins as go() does, a new variable BootInfo, the goals
    top:go_pimos1(Loaded, BootInfo) and ipl:make_boot_info(BootInfo)
    spawned (ARGC, SPAWN), and the device fep.py attached as go()
    attaches it; or
  - the machine at the shell's prompt (longrun_ipl.py --load FILE --go
    --fep --save-prompt FILE2): run dry after the login, the window's
    getl held by the device, one RECEIVE waiting in the SCSI box.

What of the saved machine is not in its memory is given to the core by
RESTORE operations, silently (driver.py): the heap pointer, new_atom's
counter, the clock (pimm.py steps, as ticks and the instructions since
the last one), the SCSI commands so far and the waiting commands (all
four of the box's state a saved machine can hold: the run queue, the
merger's lists and the current shoen are empty between runs, asserted
here).  The heap goes into the bench's memory as a file (PimmMem.bsv);
cells below the heap are the image's, unchanged (checked here).  The
argument and working registers are not given: a goal loads what it
reads, so their contents between runs are never read (if one were, the
traces would part).

The reference runs with Machine.ahead off (what only it has is
refused), unlike longrun_ipl.py's go(): the run is then what the core
must do too.  Its counts are the same as go()'s.

The device on the core is the tape (driver.py): the answers the
reference's fep.py gave, in order.  Fep.idle(), the scripted login and
the lines typed, is the reference's alone and is not an operation: it
changes only what the next POLL's answer is.

Pinned (PINNED below, measured on both models, bsv/run_pimm_shell.sh):
see bsv/README.md "The lockstep from a saved machine".

Observed injections (2026-11-24, from the prompt checkpoint made with
the login ID 1, before P-f3, shutdown / yes; each
RESTORE word of the script replaced by a silent SLOT 15):
  0 (heap pointer)  FAIL at line 4, instruction 0: M 77959241 / M 32768
  1, 2, 3 (new_atom's counter, the clock)  PASS: not caught.  The
    window runs no new_atom and nothing that reads the clock (each
    would write a register the trace shows: inferred, not counted)
  4 (SCSI command count)  FAIL at line 6231, instruction 718:
    R 11 0000000080 / R 11 0000000000
  31 (the waiting RECEIVE)  FAIL at line 1, instruction 0:
    B 7 1 0820004000 2 16384 / Q
The splice-order injection into PimmGBox (lockstep_merge.py's header)
fails the same run at line 8429.
"""
import json
import os
import pickle
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import fep as fepm  # noqa: E402
import pimm  # noqa: E402
import longrun_ipl as longrun  # noqa: E402
import lockstep_cons as cons  # noqa: E402

# (the saved machine, the lines typed) -> (trace lines, instructions),
# measured on both models 2026-11-24 (bsv/run_pimm_shell.sh), with the
# login ID 0 (fep.py LOGIN, P-f3; the link row was 20107047, 8766339
# with the ID 1, the prompt rows the same)
PINNED = {
    ('prompt', ('shutdown', 'yes')): (878180, 179247),
    ('prompt', ('cat <= file("pimos:pimos.groups")',)): (731110, 173593),
    ('link', ('shutdown', 'yes')): (20107017, 8766319),
}
POISON = (0xff, 0xdeadbeef)     # a heap cell the saved machine never wrote
T0 = time.time()


def say(text):
    print('%6.0fs %s' % (time.time() - T0, text), file=sys.stderr, flush=True)


class Sink:
    """The reference's trace, to a file; the console's lines kept, the
    instructions counted."""

    def __init__(self, f):
        self.f = f
        self.lines = 0
        self.instructions = 0
        self.kept = []

    def append(self, line):
        self.f.write(line)
        self.f.write('\n')
        self.lines += 1
        c = line[0]
        if c == 'I':
            self.instructions += 1
        elif c in 'CS':
            self.kept.append(line)


def load(path):
    with open(path, 'rb') as f:
        m, loaded, info = pickle.load(f)
    say('loaded %s' % path)
    return m, loaded, info, ('prompt' if 'prompt' in info else 'link')


def typed(argv):
    return [argv[i + 1] for i, a in enumerate(argv) if a == '--type']


def write_heap(m, path):
    """The heap, heap's first cell to hp, as the bench's memory loads
    it: one addressed block, a cell never written given POISON."""
    base = m.load + pimm.HEAP
    mem = m.mem
    n = len(m.cells)
    for i in range(pimm.HEAP):
        assert (mem.get(m.load + i) == list.__getitem__(m.cells, i)) if i < n \
            else m.load + i not in mem, 'a cell below the heap is not the image\'s: %d' % i
    gaps = 0
    with open(path, 'w') as f:
        f.write('@%x\n' % pimm.HEAP)
        chunk = []
        for a in range(base, m.hp):
            c = mem.get(a)
            if c is None:
                c = POISON
                gaps += 1
            chunk.append('%02x%08x\n' % c)
            if len(chunk) >= 1 << 16:
                f.write(''.join(chunk))
                chunk = []
        f.write(''.join(chunk))
    say('heap written: %d cells, %d never written' % (m.hp - base, gaps))
    return gaps


def restore_ops(m):
    """The RESTORE operations for what of m is not in its memory."""
    assert m.rq == 0 and m.mq == 0 and m.mwh == 0 and m.mwt == 0 and m.shoen == 0, \
        'the saved machine is not between runs'
    ops = []

    def R(which, cell):
        ops.append((driver.RESTORE, which, 0, cell))
    R(0, (0, m.hp & pimm.M32))
    R(1, (0, m.next_atom))
    R(2, (0, m.steps // pimm.INSTRUCTIONS_PER_TICK))
    R(3, (0, m.steps % pimm.INSTRUCTIONS_PER_TICK))
    R(4, (0, m.scsi_commands & pimm.M32))
    for c in m.scsi_waiting:
        for which, cell in ((16, (pimm.INT, c['unit'] & pimm.M32)),
                            (17, (pimm.INT, c['lun'] & pimm.M32)),
                            (18, (pimm.INT, c['dir'] & pimm.M32)),
                            (19, (pimm.INT, c['length'] & pimm.M32)),
                            (20, c['cdbw']), (21, (0, len(c['cdb']))),
                            (22, c['word']), (23, (0, len(c['buf']))),
                            (24, c['outs'][0]), (25, c['outs'][1]), (26, c['outs'][2])):
            R(which, cell)
        R(31, (0, 0))
    return ops


def splice_counter(m, stats):
    """Count the merger's splices (pimm.py pick: the goals made ready
    since the last pickup put in front of the merger's list), and those
    onto a list that is not empty."""
    pick = m.pick

    def counted():
        if m.mwh:
            stats['splices'] += 1
            if m.mq:
                stats['onto_nonempty'] += 1
        return pick()
    m.pick = counted


def play(m, loaded, kind, lines, sink, stats=None):
    """The script, performed on the reference as it is made: go()'s
    loop, as bench operations.  Returns (ops, events, stop)."""
    ops = restore_ops(m)
    slot = [(0, 0)] * 16
    outs = []

    def op(o):
        ops.append(o)
        driver.Script._do(m, slot, o, outs, '')
    m.tr = sink
    if stats is not None:
        splice_counter(m, stats)
    im = m.im
    if kind == 'link':
        assert not m.scsi_waiting and m.fep is None
        op((driver.NEWVAR, 0, 0, (0, 0)))
        boot = slot[0]
        op((driver.ARGC, 1, 0, pimm.marked(loaded)))
        op((driver.ARGC, 2, 0, pimm.marked(boot)))
        op((driver.SPAWN, 2, 0, (0, pimm.predicate(im, 'top', 'go_pimos1/2'))))
        op((driver.ARGC, 1, 0, boot))
        op((driver.SPAWN, 1, 0, (0, pimm.predicate(im, 'ipl', 'make_boot_info/1'))))
        dev = m.fep = fepm.Fep(longrun.kernel_file, getb_unit=2, lines=lines)
    else:
        dev = m.fep
        dev.open_file = longrun.kernel_file
        dev.script = [('getl', line) for line in lines]
    events = []
    stop = None
    try:
        while True:
            ops.append((driver.RUN, 0, 0, (0, 0)))
            try:
                m.run(limit=10 ** 12)
            except pimm.Suspend:
                pass
            ops.append((driver.POLL, 0, 0, (0, 0)))
            if m.scsi_poll():
                continue
            if not dev.idle():
                break
            events.append(sink.instructions)
            say('fep: a scripted event at %d instructions' % sink.instructions)
        stop = 'nothing left to run, %d goals waiting' % m.nsusp
    except pimm.Unimplemented as e:
        stop = 'refused: %s' % e
    except pimm.Fail as e:
        stop = 'Fail %s' % e
    except fepm.FepError as e:
        stop = 'FepError: %s' % e
    return ops, events, stop, dev


def make(argv):
    pkl, out = argv[2], argv[3]
    lines = typed(argv)
    os.makedirs(out, exist_ok=True)
    m, loaded, info, kind = load(pkl)
    m.ahead = '--ahead' in argv
    gaps = write_heap(m, os.path.join(out, 'heap.hex'))
    tape0 = len(m.scsi_tape)
    before = info.get('prompt', {}).get('instructions', 0)
    stats = dict(splices=0, onto_nonempty=0)
    with open(os.path.join(out, 'trace'), 'w', buffering=1 << 22) as f:
        sink = Sink(f)
        ops, events, stop, dev = play(m, loaded, kind, lines, sink, stats)
    s = driver.Script()
    s.ops = ops
    s.write(os.path.join(out, 'script.hex'), m.scsi_tape[tape0:])
    want = dict(kind=kind, typed=lines, lines=sink.lines, instructions=sink.instructions,
                from_instruction=before, to_instruction=before + sink.instructions,
                operations=len(ops), tape=len(m.scsi_tape) - tape0, events=events,
                console=cons.console(sink.kept), stop=stop, heap_gaps=gaps,
                fep_messages=len(dev.messages), held=dev.held, **stats)
    with open(os.path.join(out, 'want.json'), 'w') as f:
        json.dump(want, f, indent=1, default=str)
    say('made: %r' % (want,))
    return 0


def compare(argv):
    d = argv[2]
    with open(os.path.join(d, 'want.json')) as f:
        want = json.load(f)
    name = 'pimm lockstep shell (%s, %s)' % (want['kind'], ' / '.join(want['typed']) or 'nothing typed')
    got = sys.stdin
    first = got.readline()
    while first.startswith('Warning: file'):
        first = got.readline()
    n = ins = 0
    recent = []
    with open(os.path.join(d, 'trace')) as f:
        for w in f:
            g = first if n == 0 else got.readline()
            if g != w:
                print('%s: FAIL at line %d of the trace, instruction %d after the checkpoint'
                      % (name, n, ins))
                print('  reference: %s' % w.rstrip('\n'))
                print('  bluespec:  %s' % (g.rstrip('\n') or '(end of trace)'))
                for prev in recent:
                    print('  after:     %s' % prev)
                return 1
            if w[0] == 'I':
                ins += 1
            recent = (recent + [w.rstrip('\n')])[-6:]
            n += 1
    extra = got.readline() if n else first
    if extra:
        print('%s: FAIL, the Bluespec trace goes on: %s' % (name, extra.strip()))
        return 1
    if n != want['lines'] or ins != want['instructions']:
        print('%s: FAIL, %d lines, %d instructions; the reference made %d, %d'
              % (name, n, ins, want['lines'], want['instructions']))
        return 1
    pin = PINNED.get((want['kind'], tuple(want['typed'])))
    if pin is not None and pin != (n, ins):
        print('%s: FAIL, %d lines, %d instructions, pinned %r' % (name, n, ins, pin))
        return 1
    print('%s: PASS (instructions %d to %d of go(), %d trace lines identical to the reference '
          'model; console %r; %s; %.0f s to the compare%s)'
          % (name, want['from_instruction'], want['to_instruction'], n, want['console'],
             want['stop'], time.time() - T0, '' if pin else '; NOT PINNED'))
    return 0


def splices(argv):
    m, loaded, info, kind = load(argv[2])
    stats = dict(splices=0, onto_nonempty=0)

    class Count(Sink):
        def append(self, line):
            if line[0] == 'I':
                self.instructions += 1
    ops, events, stop, dev = play(m, loaded, kind, typed(argv), Count(None), stats)
    print(kind, stats, stop)
    return 0


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'make':
        sys.exit(make(sys.argv))
    if cmd == 'compare':
        sys.exit(compare(sys.argv))
    if cmd == 'splices':
        sys.exit(splices(sys.argv))
    print(__doc__)
    sys.exit(2)
