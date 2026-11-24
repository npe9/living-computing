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
                         to (val & 0xffff): a copy, as the built-in
    SETW    a i val      word i of the string in slot a := val, IN PLACE.
                         The bench's own way to fill a string it has
                         just made and nothing else refers to; i is 16
                         bits (the b and tag fields)
    PTR     a b tag      slot a := {tag, the address in slot b}: a
                         structure whose cells are the variables made
                         by consecutive NEWVARs starting with slot b's
                         (variables are single cells taken in order)
    SLOT    a cell       slot a := cell, as given.  For a test that
                         answers what a goal asks for: the script's
                         author runs the reference model as the script
                         grows (Script.live), finds the cell a goal
                         left unbound, and names it here.  The address
                         holds on the Bluespec because the traces,
                         which show every memory write, are compared.
    POLL                 the device's turn: the SCSI commands that wait
                         for it (pimm.Machine.scsi_poll) are given to it
                         again, oldest first.  What the reference model
                         does when the machine has run dry; a script
                         puts it after a RUN, where the reference ran
                         dry with a command waiting (Script.live)

The device tape.  The bench has no device: scsi_init and scsi_command
(bsv/PimmScsiBox.bsv) put each command on the core's port, and the
bench answers it from a tape the reference model recorded while playing
the same script (pimm.Machine.scsi_tape, Script.record_tape).  The bench
prints a B line for each command from what the CORE sent (unit, LUN,
CDB, direction, length, and a SEND's bytes), and the reference prints
the same line at the same point (pimm.Machine.scsi_do): so what goes on
the bus is compared, and only the answers are replayed.  In the file
the tape follows the script's END word; a first word

    TAPE      val        the tape begins at word val of the file

tells the bench where (a script without a device has no TAPE word and
no tape).  One entry per device call, in order; the first word of an
entry is kind << 56 | n << 32 | value:

    kind 1    scsi_init asked the buffer size: value
    kind 2    the command cannot finish yet (the device's None): the
              built-in's "not finished yet" path, or, for a command
              asked again by a poll, still waiting
    kind 3    the command finished: value = Result, n = the number of
              bytes received; then (n + 7) / 8 words of those bytes,
              eight a word from the top, the last one padded with zeros

A tape that runs out, or an entry of the wrong kind, stops the bench
with an X line, which no reference trace has.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pimm  # noqa: E402

(END, NEWVAR, ARG, ARGC, SPAWN, RUN, OUT, UNIFY, UNIFYC, NEWSTR, SETEL, PTR, SLOT,
 SETW, POLL, TAPE) = range(16)
SCRIPT_BITS = 24            # the driver's script memory holds 1 << 24 operations
# The script file holds the operations only, so the simulator's first
# line is its warning that the rest of the memory is not given.
GAP = "Warning: file 'generated/pimm_script.hex' for memory 'script' has a gap"


class Script:
    def __init__(self):
        self.ops = []       # (kind, a, b, (tag, val)) or ('label', text)
        # what play() and live() run on: a test with a device gives a
        # function that makes a machine with its Machine.fep attached
        self.make = pimm.Machine

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

    def setw(self, a, i, v):
        assert 0 <= i < 1 << 16
        self._op(SETW, a, i >> 8, (i & 0xff, v))

    def setslot(self, a, cell):
        self._op(SLOT, a, 0, cell)

    def poll(self):
        self._op(POLL)

    def live(self):
        """Perform the operations added since the last call on a private
        reference machine and return it; live_slot is its slots."""
        if not hasattr(self, '_live'):
            self._live = (self.make(), [(0, 0)] * 16, [0], [])
        m, slot, done, outs = self._live
        m.tr = []
        for o in self.ops[done[0]:]:
            if o[0] != 'label':
                self._do(m, slot, o, outs, '')
        done[0] = len(self.ops)
        self.live_slot = slot
        return m

    def vector(self, a, first, elems):
        """slot a := a vector of len(elems) cells, built in slots first,
        first+1, ...: each a new variable, bound to its element unless
        that is None.  An element is a cell or ('slot', n)."""
        n = len(elems)
        assert 1 <= n <= 6
        for i in range(n):
            self.newvar(first + i)
        self._op(PTR, a, first, (pimm.VECT0 + 2 * n + 1, 0))
        for i, e in enumerate(elems):
            if e is None:
                continue
            if e[0] == 'slot':
                self.unify(first + i, e[1])
            else:
                self.unifyc(first + i, e)

    def cons(self, a, first, car, cdr):
        """slot a := a list cell built in slots first, first+1; car and
        cdr as vector()'s elements."""
        self.newvar(first)
        self.newvar(first + 1)
        self._op(PTR, a, first, (pimm.LIST + 1, 0))
        for i, e in enumerate((car, cdr)):
            if e is None:
                continue
            if e[0] == 'slot':
                self.unify(first + i, e[1])
            else:
                self.unifyc(first + i, e)

    def string(self, a, bits, elems):
        """slot a := a string with these elements: a new string (all
        zero), then one SETW per nonzero word."""
        self.newstr(a, len(elems), bits)
        per = 32 // bits
        for i in range(0, len(elems), per):
            w = 0
            for e in (list(elems[i:i + per]) + [0] * per)[:per]:
                w = w << bits | e
            if w:
                self.setw(a, i // per, w)

    def words(self, tape=None):
        out = [k << 56 | a << 48 | b << 40 | c[0] << 32 | c[1]
               for k, a, b, c in (o for o in self.ops if o[0] != 'label')]
        if tape is not None:
            # TAPE first, the script, END, then the tape
            out = [TAPE << 56 | len(out) + 2] + out + [0] + tape_words(tape)
        else:
            out += [0]
        assert len(out) < 1 << SCRIPT_BITS
        return out

    def write(self, path, tape=None):
        with open(path, 'w') as f:
            words = self.words(tape)
            f.write(''.join('%016x\n' % w for w in words))

    def record_tape(self):
        """Play the script on a machine of self.make() and return the
        device's answers (pimm.Machine.scsi_tape), for write()."""
        for _ in self.play():
            pass
        return self.machine.scsi_tape

    @staticmethod
    def _do(m, slot, o, outs, label):
        k, a, b, c = o
        if k == NEWVAR:
            slot[a] = m.new_var()
        elif k == ARG:
            m.argv[a] = pimm.marked(slot[b])      # the slot keeps it: MRB on
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
            w = m.deref(pimm.marked(slot[a]))
            outs.append((label, w))
            m.tr.append('O %02x%08x' % w)
        elif k == UNIFY:
            m.unify(pimm.marked(slot[a]), pimm.marked(slot[b]))
        elif k == UNIFYC:
            m.unify(pimm.marked(slot[a]), c)
        elif k == NEWSTR:
            slot[a] = m.new_string(c[1] >> 8, c[1] & 0xff)
        elif k == SETEL:
            slot[a] = m.set_element(slot[a], c[1] >> 16, c[1] & 0xffff)
        elif k == SETW:
            i, at = b << 8 | c[0], slot[a][1]
            assert m.mem[at][0] == pimm.CDESC and i < m.mem[at][1] & 0xffffff
            m.mem[at + 1 + i] = (pimm.INT, c[1])
        elif k == PTR:
            slot[a] = (c[0], slot[b][1])
        elif k == SLOT:
            slot[a] = c
        elif k == POLL:
            m.scsi_poll()
        else:
            raise ValueError(k)

    def play(self, m=None):
        """Yield (label, [trace lines]) for each labelled part."""
        m = m or self.make()
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
            self._do(m, slot, o, self.outs, label)
        self.slots = slot
        yield label, m.tr


def tape_words(tape):
    """The device tape (pimm.Machine.scsi_tape) as the bench reads it:
    see the module's header."""
    out = []
    for e in tape:
        if e is None:
            out.append(2 << 56)
        elif e[0] == 'init':
            out.append(1 << 56 | e[1] & 0xffffffff)
        else:
            result, data = e
            assert len(data) < 1 << 24
            out.append(3 << 56 | len(data) << 32 | result & 0xffffffff)
            padded = bytes(data) + bytes(-len(data) % 8)
            out += [int.from_bytes(padded[i:i + 8], 'big') for i in range(0, len(padded), 8)]
    return out


def compare(script, stream, name, pinned=None):
    """Compare the Bluespec trace on `stream` with the script played on
    the reference model.  Prints PASS/FAIL; returns (ok, machine)."""
    parts = lines = 0
    first = True
    for what, want in script.play():
        for i, w in enumerate(want):
            got = stream.readline().rstrip('\n')
            if first and got.startswith(GAP):
                got = stream.readline().rstrip('\n')
            first = False
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
