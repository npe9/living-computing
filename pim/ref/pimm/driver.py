#!/usr/bin/env python3
"""Lockstep scripts: one list of operations, played on both models.

A lockstep test is a Script: operations on the machine from outside
(make a variable, load an argument, spawn a goal, run, bind, print).
write() saves it as the file the Bluespec driver bench executes
(bsv/PimmDriverTb.bsv); play() performs the same operations on the
reference model (pimm.Machine) and yields its trace; compare() checks
the Bluespec's trace, read from a stream, against it line by line.

An operation is one 64-bit word: kind, a, b (8 bits each), then a
40-bit cell (tag, value).  Slots are the driver's sixteen variables.

    END
    NEWVAR  a            slot a := a fresh unbound variable
    ARG     a b          argument register a := slot b
    ARGC    a cell       argument register a := cell
    SPAWN   a val        a ready goal: code address val, a arguments
    RUN                  run until the ready queue is empty or the
                         model stops
    OUT     a            print "O <slot a dereferenced>"
    UNIFY   a b          unify slot a with slot b
    UNIFYC  a cell       unify slot a with cell
    NEWSTR  a val        slot a := a new string, val = length << 8 | bits
    SETEL   a val        slot a := slot a with element (val >> 16) set
                         to (val & 0xffff)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pimm  # noqa: E402

END, NEWVAR, ARG, ARGC, SPAWN, RUN, OUT, UNIFY, UNIFYC, NEWSTR, SETEL = range(11)
SCRIPT_BITS = 20            # the driver's script memory holds 1 << 20 operations


class Script:
    def __init__(self):
        self.ops = []       # (kind, a, b, (tag, val)) or ('label', text)

    def _op(self, kind, a=0, b=0, cell=(0, 0)):
        self.ops.append((kind, a, b, cell))

    def label(self, text):
        """Name what follows, for the comparison's messages."""
        self.ops.append(('label', text))

    def newvar(self, a):
        self._op(NEWVAR, a)

    def arg(self, n, slot):
        self._op(ARG, n, slot)

    def argc(self, n, cell):
        self._op(ARGC, n, 0, cell)

    def spawn(self, pc, argn):
        self._op(SPAWN, argn, 0, (0, pc))

    def run(self):
        self._op(RUN)

    def out(self, a):
        self._op(OUT, a)

    def unify(self, a, b):
        self._op(UNIFY, a, b)

    def unifyc(self, a, cell):
        self._op(UNIFYC, a, 0, cell)

    def newstr(self, a, n, bits):
        self._op(NEWSTR, a, 0, (0, n << 8 | bits))

    def setel(self, a, i, e):
        self._op(SETEL, a, 0, (0, i << 16 | e))

    def string(self, a, bits, elems):
        """slot a := a string with these elements (a new string, then
        one SETEL per nonzero element)."""
        self.newstr(a, len(elems), bits)
        for i, e in enumerate(elems):
            if e:
                self.setel(a, i, e)

    def words(self):
        out = [k << 56 | a << 48 | b << 40 | c[0] << 32 | c[1]
               for k, a, b, c in (o for o in self.ops if o[0] != 'label')]
        assert len(out) < 1 << SCRIPT_BITS
        return out + [0]

    def write(self, path):
        with open(path, 'w') as f:
            words = self.words()
            f.write(''.join('%016x\n' % w for w in words))
            # the whole memory, so that the simulator has no gap to report
            f.write('0000000000000000\n' * ((1 << SCRIPT_BITS) - len(words)))

    def play(self, m=None):
        """Yield (label, [trace lines]) for each labelled part."""
        m = m or pimm.Machine()
        self.machine = m
        self.outs = []      # (label, word) of every OUT, in order
        slot = [(0, 0)] * 16
        label = 'start'
        m.tr = []
        for o in self.ops:
            if o[0] == 'label':
                if m.tr:
                    yield label, m.tr
                label, m.tr = o[1], []
                continue
            k, a, b, c = o
            if k == NEWVAR:
                slot[a] = m.new_var()
            elif k == ARG:
                m.argv[a] = slot[b]
            elif k == ARGC:
                m.argv[a] = c
            elif k == SPAWN:
                m.record(pimm.READY, c[1], m.argv[1:a + 1])
            elif k == RUN:
                try:
                    m.run()
                except (pimm.Suspend, pimm.Fail):
                    pass
            elif k == OUT:
                w = m.deref(slot[a])
                self.outs.append((label, w))
                m.tr.append('O %02x%08x' % w)
            elif k == UNIFY:
                m.unify(slot[a], slot[b])
            elif k == UNIFYC:
                m.unify(slot[a], c)
            elif k == NEWSTR:
                slot[a] = m.new_string(c[1] >> 8, c[1] & 0xff)
            elif k == SETEL:
                slot[a] = m.set_element(slot[a], c[1] >> 16, c[1] & 0xffff)
            else:
                raise ValueError(k)
        self.slots = slot
        yield label, m.tr


def compare(script, stream, name, pinned=None):
    """Compare the Bluespec trace on `stream` with the script played on
    the reference model.  Prints PASS/FAIL; returns (ok, machine)."""
    parts = lines = 0
    for what, want in script.play():
        for i, w in enumerate(want):
            got = stream.readline().rstrip('\n')
            if got != w:
                print('%s: FAIL at part %d (%s), line %d of its trace' % (name, parts, what, i))
                print('  reference: %s' % w)
                print('  bluespec:  %s' % (got or '(end of trace)'))
                for prev in want[max(0, i - 3):i]:
                    print('  after:     %s' % prev)
                return False, script.machine
        lines += len(want)
        parts += 1
    extra = stream.readline()
    if extra:
        print('%s: FAIL, the Bluespec trace goes on: %s' % (name, extra.strip()))
        return False, script.machine
    got = dict(parts=parts, lines=lines)
    if pinned is not None and got != pinned:
        print('%s: FAIL, counts %r, pinned %r' % (name, got, pinned))
        return False, script.machine
    script.counts = got
    return True, script.machine
