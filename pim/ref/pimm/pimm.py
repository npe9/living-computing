#!/usr/bin/env python3
"""A host-side reference model of the PIM/m KL1-B machine (scaffold).

It executes the PIMOS binaries' own cells: the 40-bit tagged words,
tag values (debugger/inspector/tagtbl.kl1), relative labels and
instruction encodings of the IPL image, loaded by asm/kbn.py.  It is
not the deliverable (docs/pimos_roadmap.md decision 3): the Bluespec
model is, and this exists to find out what the instructions do and to
be diffed against it.

All machine state is registers and memory cells, so that the Bluespec
core can hold the same state and be compared write for write: goal
records, the ready queue, suspension records and hooked variables are
cells on the heap (layouts in docs/pimm_semantics.md "Runtime state";
they are this project's design, the firmware being lost).  One
processor, a LIFO ready queue without priorities, 8- and 16-bit
strings.  No garbage collection (the heap only grows), no MRB, no
shoen, no exceptions.  An instruction this file does not implement
raises Unimplemented: it never guesses.

Every instruction's operand reading is taken from object code paired
with its KL1 source; docs/pimm_semantics.md records which.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import kbn  # noqa: E402,F401
import kbndis  # noqa: E402
import pimm_stubs  # noqa: E402
from census import opcode_table  # noqa: E402

INT, ATOM, REF, UNDF, HOOK, STRG, CDESC = 0x00, 0x02, 0x06, 0x08, 0x0a, 0x0e, 0x25
from pimm_layout import (G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS,  # noqa: E402
                         READY, SUSPENDED, TAKEN, S_NEXT, S_GOAL, S_SIZE,
                         MEMORY_CELLS, HEAP)


class Unimplemented(Exception):
    pass


class Suspend(Exception):
    """The ready queue is empty and goals are still suspended."""


class Fail(Exception):
    """No clause applies (a reduction failure), or a body unification fails."""


def sx16(v):
    v &= 0xffff
    return v - 0x10000 if v & 0x8000 else v


def signed(v):
    return v - (1 << 32) if v >> 31 else v


class _Regs(list):
    """A register file; every write is traced."""

    def __setitem__(self, i, w):
        list.__setitem__(self, i, w)
        m = self.machine
        if m.tr is not None:
            m.tr.append('%s %d %02x%08x' % (self.letter, i, w[0], w[1]))


class _Mem(dict):
    """Memory; every write is traced."""

    def __setitem__(self, a, w):
        m = self.machine
        if not m.load <= a < m.load + m.size:
            raise RuntimeError('write outside memory: %x' % a)
        dict.__setitem__(self, a, w)
        if m.tr is not None:
            m.tr.append('M %d %02x%08x' % (a - m.load, w[0], w[1]))


class Machine:
    def __init__(self, image=None, heap=HEAP, size=MEMORY_CELLS):
        self.im = image or kbndis.Image()
        self.load = self.im.load
        self.size = size
        # The lockstep trace (docs/pimm_semantics.md "Trace"): None, or a
        # list that receives one line per event.
        self.tr = None
        # code = the image, then the built-in stubs
        stubs, self.stubs = pimm_stubs.build(len(self.im.cells))
        self.cells = list(self.im.cells) + stubs
        assert len(self.cells) <= heap
        self.mem = _Mem({self.load + i: c for i, c in enumerate(self.cells)})
        self.mem.machine = self
        self.reg = _Regs([(INT, 0)] * 256)
        self.reg.machine, self.reg.letter = self, 'R'
        self.argv = _Regs([(INT, 0)] * 256)   # arguments of the goal being built
        self.argv.machine, self.argv.letter = self, 'A'
        self.hp = self.load + heap            # heap pointer: the next free cell
        self.rq = 0                           # ready queue: the newest goal record
        self.optab = opcode_table()
        self.names = {}
        # statistics, not machine state
        self.nsusp = 0
        self.steps = 0
        self.reductions = 0
        self.builtin_waits = 0
        self.goal_waits = 0

    def event(self, text):
        if self.tr is not None:
            self.tr.append(text)

    # ---- data ----------------------------------------------------
    def alloc(self, n):
        a = self.hp
        if a + n >= self.load + self.size:
            raise RuntimeError('heap full')
        self.hp += n
        return a

    def new_var(self):
        a = self.alloc(1)
        self.mem[a] = (UNDF, 0)
        return (REF, a)

    def deref(self, w):
        """Follow references; the result is a value, or the reference to
        an unbound cell (UNDF, or HOOK when goals wait on it)."""
        while w[0] & ~1 == REF:
            c = self.mem[w[1]]
            if c[0] == UNDF or c[0] & ~1 == HOOK:
                return w
            w = c
        return w

    def unbound(self, w):
        return w[0] & ~1 == REF               # after deref

    def bind(self, ref, w):
        """Write w over the unbound cell, then wake every goal hooked on
        it, in list order (the most recently hooked first)."""
        old = self.mem[ref[1]]
        self.mem[ref[1]] = w
        if old[0] & ~1 == HOOK:
            s = old[1]
            while s:
                g = self.mem[s + S_GOAL][1]
                if self.mem[g + G_STATUS][1] == SUSPENDED:
                    self.event('W %d' % (g - self.load))
                    self.mem[g + G_STATUS] = (INT, READY)
                    self.mem[g + G_LINK] = (INT, self.rq)
                    self.rq = g
                    self.nsusp -= 1
                s = self.mem[s + S_NEXT][1]

    def unify(self, a, b):
        a, b = self.deref(a), self.deref(b)
        if self.unbound(a):
            if not (self.unbound(b) and b[1] == a[1]):
                self.bind(a, b)
            return
        if self.unbound(b):
            self.bind(b, a)
            return
        if a[0] & ~1 != b[0] & ~1:
            raise Fail('unify %r %r' % (a, b))
        if a[0] & ~1 in (INT, ATOM):
            if a[1] != b[1]:
                raise Fail('unify %r %r' % (a, b))
            return
        if a[0] & ~1 == STRG:
            if a[1] != b[1] and self.string(a) != self.string(b):
                raise Fail('unify of two different strings')
            return
        raise Unimplemented('unify of %r and %r' % (a, b))

    # strings: {STRG, address} -> {CDESC, pad << 27 | type << 24 | words},
    # then `words` cells of 32 bits, elements packed from the top.
    # type 3 = 8-bit elements, 4 = 16-bit (kbnheap.kl1 string_cdesc).
    def string(self, w):
        t, v = self.mem[w[1]]
        if t != CDESC:
            raise RuntimeError('string without a descriptor at %x' % w[1])
        typ, pad, words = (v >> 24) & 7, (v >> 27) & 3, v & 0xffffff
        if typ not in (3, 4):
            raise Unimplemented('string element type %d' % typ)
        size = 1 << typ
        per = 32 // size
        out = []
        for i in range(words):
            x = self.mem[w[1] + 1 + i][1]
            out += [(x >> (32 - size * (k + 1))) & ((1 << size) - 1) for k in range(per)]
        return size, out[:len(out) - pad]

    def make_string(self, size, elems):
        typ = {8: 3, 16: 4}[size]
        per = 32 // size
        words = (len(elems) + per - 1) // per
        pad = words * per - len(elems)
        a = self.alloc(1 + words)
        self.mem[a] = (CDESC, (pad << 27) | (typ << 24) | words)
        padded = list(elems) + [0] * pad
        for i in range(words):
            x = 0
            for k in range(per):
                x = (x << size) | (padded[i * per + k] & ((1 << size) - 1))
            self.mem[a + 1 + i] = (INT, x)
        return (STRG | 1, a)

    # ---- goals -----------------------------------------------------
    def record(self, status, code, args):
        """Write a goal record; code is a cell index."""
        g = self.alloc(G_ARGS + len(args))
        self.mem[g + G_LINK] = (INT, self.rq if status == READY else 0)
        self.mem[g + G_STATUS] = (INT, status)
        self.mem[g + G_CODE] = (INT, self.load + code)
        self.mem[g + G_ARGN] = (INT, len(args))
        for i, a in enumerate(args):
            self.mem[g + G_ARGS + i] = a
        if status == READY:
            self.rq = g
        return g

    def hook(self, g, var):
        """Add goal record g to the goals waiting on the unbound cell."""
        old = self.mem[var]
        s = self.alloc(S_SIZE)
        self.mem[s + S_NEXT] = (INT, old[1] if old[0] & ~1 == HOOK else 0)
        self.mem[s + S_GOAL] = (INT, g)
        self.mem[var] = (HOOK, s)

    def spawn(self, pc, args):
        """Make a ready goal, as enqueue_goal does: arguments through the
        argument registers (from 1), then the record."""
        for i, a in enumerate(args):
            self.argv[i + 1] = a
        self.record(READY, pc, self.argv[1:len(args) + 1])

    call = spawn

    def run(self, pc=None, args=(), limit=10000000):
        """Run until the ready queue is empty.  Raises Suspend if goals
        are left suspended."""
        if pc is not None:
            self.spawn(pc, args)
        before = self.steps
        while self.rq:
            g = self.rq
            self.event('G %d' % (g - self.load))
            self.rq = self.mem[g + G_LINK][1]
            self.mem[g + G_STATUS] = (INT, TAKEN)
            code = self.mem[g + G_CODE][1] - self.load
            for i in range(self.mem[g + G_ARGN][1]):
                self.reg[i] = self.mem[g + G_ARGS + i]
            self.reduce(code, limit)
        self.event('Q')
        if self.nsusp:
            raise Suspend('%d goals still suspended' % self.nsusp)
        return self.steps - before

    def abandon(self):
        """Forget that goals are suspended (a test's way of ending a run).
        Their records and hooks stay in memory."""
        self.nsusp = 0

    def opname(self, pc):
        name = self.names.get(pc)
        if name is None:
            if pc < len(self.im.cells):
                name = self.im.dis(pc).split()[0]
            else:
                t, v = self.cells[pc]
                name = self.optab[(t, v >> 24)][0]
            self.names[pc] = name
        return name

    def reduce(self, pc, limit):
        self.reductions += 1
        self.alt = None                       # next clause on guard failure
        self.waiting = []                     # variables guards wanted bound, in order
        cells = self.cells
        try:
            while True:
                self.steps += 1
                if self.steps > limit:
                    raise RuntimeError('step limit')
                t, v = cells[pc]
                if t not in (0x22, 0x23):
                    raise RuntimeError('pc %d is not an instruction: %02x:%08x' % (pc, t, v))
                name = self.opname(pc)
                self.event('I %d %02x%08x' % (pc, t, v))
                fn = getattr(self, 'i_' + name, None)
                if fn is None:
                    raise Unimplemented('%s at %d' % (name, pc))
                nxt = fn(pc, (v >> 16) & 255, (v >> 8) & 255, v & 255, v & 0xffff)
                if nxt == 'done':
                    return
                pc = pc + 1 if nxt is None else nxt
        except Fail:
            self.event('E fail')
            raise

    def guard_fail(self):
        if self.alt is None:
            raise RuntimeError('guard failed with no alternative')
        return self.alt

    def suspend_goal(self, pc, arity, c16):
        """Write the goal back as a suspended record, entry = the label,
        arguments = r[0..arity), and hook it on every variable a guard
        noted, in the order noted (a variable noted twice is hooked
        twice; the status cell makes the goal wake once)."""
        self.goal_waits += 1
        self.nsusp += 1
        g = self.record(SUSPENDED, pc + 2 + sx16(c16), self.reg[:arity])
        for var in self.waiting:
            self.hook(g, var)
        self.event('E susp')
        return 'done'

    # guard helpers: a value, or None after noting the variable / failing
    def g_word(self, r):
        w = self.deref(self.reg[r])
        if self.unbound(w):
            self.waiting.append(w[1])
            return None
        return w

    def g_int(self, r):
        w = self.g_word(r)
        if w is None or w[0] & ~1 != INT:
            return None
        return signed(w[1])

    # ---- body built-ins ----------------------------------------------
    def builtin(self, name, operands, f):
        """A body built-in with register operands, directions from the
        stub table.  f takes the dereferenced inputs and returns the
        output words.  If an input is unbound the built-in becomes a
        suspended goal of its stub (asm/pimm_stubs.py), waiting on the
        first such input; each output operand's argument is a fresh
        variable, which the register also gets."""
        stub = self.stubs[name]
        dirs = stub['dirs']
        ins = [r for r, d in zip(operands, dirs) if d == 'i']
        outs = [r for r, d in zip(operands, dirs) if d == 'o']
        vals = [self.deref(self.reg[r]) for r in ins]
        wait = [w[1] for w in vals if self.unbound(w)]
        if not wait:
            for r, w in zip(outs, f(*vals)):
                self.reg[r] = w
            return
        self.builtin_waits += 1
        self.nsusp += 1
        g = self.alloc(G_ARGS + len(operands))
        self.mem[g + G_LINK] = (INT, 0)
        self.mem[g + G_STATUS] = (INT, SUSPENDED)
        self.mem[g + G_CODE] = (INT, self.load + stub['addr'])
        self.mem[g + G_ARGN] = (INT, len(operands))
        for k, (r, d) in enumerate(zip(operands, dirs)):
            if d == 'i':
                self.mem[g + G_ARGS + k] = self.reg[r]
            else:
                var = self.new_var()
                self.mem[g + G_ARGS + k] = var
                self.reg[r] = var
        self.hook(g, wait[0])

    def need_int(self, w):
        if w[0] & ~1 != INT:
            raise Unimplemented('built-in exception: not an integer: %r' % (w,))
        return signed(w[1])

    def need_string(self, w):
        if w[0] & ~1 != STRG:
            raise Unimplemented('built-in exception: not a string: %r' % (w,))
        return self.string(w)

    # ---- instructions ------------------------------------------------
    # clause selection
    def i_try_me_else(self, pc, x, y, z, c16):
        self.alt = pc + 2 + sx16(c16)

    def i_otherwise(self, pc, x, y, z, c16):
        # Clauses after `otherwise` apply only when none before can:
        # if an earlier guard was waiting on a variable, suspend instead.
        if self.waiting:
            return self.suspend_goal(pc, x, c16)
        self.alt = None

    def i_suspend(self, pc, x, y, z, c16):
        if self.waiting:
            return self.suspend_goal(pc, x, c16)
        raise Fail('no clause of the predicate at %d applies' % (pc + 2 + sx16(c16)))

    def i_switch_on_non_integer(self, pc, x, y, z, c16):
        w = self.g_word(x)
        if w is None or w[0] & ~1 != INT:
            return pc + 2 + sx16(c16)

    def i_hash_on_constant(self, pc, x, y, z, c16):
        # word 1: register, mask.  word 2: the miss label, relative to
        # itself.  Then mask+1 slots: {atom,0} empty, or {integer,
        # count << 16 | offset from the slot} to `count` {key, offset}
        # pairs; a pair's target is offset-cell + 1 + offset (kbn.kl1
        # out_hash_table / set_entry_part, hash_on_cnst).
        cells = self.cells
        miss = pc + 1 + 2 + sx16(cells[pc + 1][1])
        w = self.g_word(x)
        if w is None:
            return miss
        slot = pc + 2 + (w[1] & c16)
        st, sv = cells[slot]
        if st != INT:
            return miss
        count, off = sv >> 16, sv & 0xffff
        for k in range(count):
            e = slot + off + 2 * k
            if cells[e] == (w[0] & ~1, w[1]):
                return e + 1 + 1 + sx16(cells[e + 1][1])
        return miss

    # guards
    def i_wait(self, pc, x, y, z, c16):
        if self.g_word(x) is None:
            return self.guard_fail()

    def i_wait_integer(self, pc, x, y, z, c16):
        if self.g_int(x) != sx16(c16):
            return self.guard_fail()

    def compare(self, x, y, f):
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or not f(a, b):
            return self.guard_fail()

    def i_not_less_than(self, pc, x, y, z, c16):
        return self.compare(x, y, lambda a, b: a >= b)

    def i_less_than(self, pc, x, y, z, c16):
        return self.compare(x, y, lambda a, b: a < b)

    def i_subtract(self, pc, x, y, z, c16):      # guard arithmetic
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None:
            return self.guard_fail()
        self.reg[z] = (INT, (a - b) & 0xffffffff)

    def i_string(self, pc, x, y, z, c16):
        # guard string(S, Length, ElementSize): r[y] := length, r[z] := size
        w = self.g_word(x)
        if w is None or w[0] & ~1 != STRG:
            return self.guard_fail()
        size, elems = self.string(w)
        self.reg[y] = (INT, len(elems))
        self.reg[z] = (INT, size)

    # moves and unification
    def i_put_integer(self, pc, x, y, z, c16):
        self.reg[x] = (INT, sx16(c16) & 0xffffffff)

    def i_put_value(self, pc, x, y, z, c16):
        self.reg[x] = self.reg[y]

    def i_put_marked_value(self, pc, x, y, z, c16):
        self.reg[x] = self.reg[y]     # and marks both multiply referenced (MRB)

    def i_put_variable(self, pc, x, y, z, c16):
        var = self.new_var()
        self.reg[x] = var
        self.reg[y] = var

    def i_get_integer(self, pc, x, y, z, c16):
        self.unify(self.reg[x], (INT, sx16(c16) & 0xffffffff))

    def i_get_value(self, pc, x, y, z, c16):
        self.unify(self.reg[x], self.reg[y])

    def i_collect_value(self, pc, x, y, z, c16):
        pass        # MRB reclamation of what r[x] points at: no GC here

    # building and starting goals
    def i_set_value(self, pc, x, y, z, c16):
        self.argv[x] = self.reg[y]

    def i_set_variable(self, pc, x, y, z, c16):
        var = self.new_var()
        self.argv[x] = var
        self.reg[y] = var

    def i_enqueue_goal(self, pc, x, y, z, c16):
        self.record(READY, pc + 2 + sx16(c16), self.argv[1:x + 1])

    def i_execute(self, pc, x, y, z, c16):
        # the same goal goes on as a reduction of the predicate at the label
        self.reductions += 1
        self.alt = None
        self.waiting = []
        return pc + 2 + sx16(c16)

    def i_proceed(self, pc, x, y, z, c16):
        self.event('E done')
        return 'done'

    # body arithmetic: r[z] := r[x] op r[y]
    def i_b_add(self, pc, x, y, z, c16):
        self.builtin('b_add', [x, y, z], lambda a, b: [
            (INT, (self.need_int(a) + self.need_int(b)) & 0xffffffff)])

    def i_b_subtract(self, pc, x, y, z, c16):
        self.builtin('b_subtract', [x, y, z], lambda a, b: [
            (INT, (self.need_int(a) - self.need_int(b)) & 0xffffffff)])

    # strings.  The fourth register of a four-register built-in is the
    # top byte of the following cell (klb_opr.kl1 p(r4,...)).
    def i_new_string(self, pc, x, y, z, c16):
        # new_string(^S, Length, ElementSize): r[z] := string of r[x] zeros
        def f(n, size):
            return [self.make_string(self.need_int(size), [0] * self.need_int(n))]
        self.builtin('new_string', [x, y, z], f)

    def i_b_string_element(self, pc, x, y, z, c16):
        # string_element(S, I, ^E, ^S1): r[z] := element, r[w] := the string
        w4 = self.cells[pc + 1][1] >> 24

        def f(s, i):
            _size, elems = self.need_string(s)
            return [(INT, elems[self.need_int(i)]), s]
        self.builtin('b_string_element', [x, y, z, w4], f)
        return pc + 2

    def i_set_string_element(self, pc, x, y, z, c16):
        # set_string_element(S, I, E, ^S1): r[w] := S with element I = r[z].
        # The machine may update in place when S is singly referenced;
        # this model always copies.
        w4 = self.cells[pc + 1][1] >> 24

        def f(s, i, e):
            size, elems = self.need_string(s)
            elems = list(elems)
            elems[self.need_int(i)] = self.need_int(e) & ((1 << size) - 1)
            return [self.make_string(size, elems)]
        self.builtin('set_string_element', [x, y, z, w4], f)
        return pc + 2


def predicate(im, module, pred):
    for m in im.mods:
        if m['name'] == module:
            for n, _ln, addr in m['preds']:
                if n == pred:
                    return addr
    raise KeyError('%s:%s' % (module, pred))
