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
VDESC = 0x0d                # kbnheap.kl1 tag(vdesc)
LIST = 0x04                 # {LIST, address} -> car, cdr; nil is the atom 0
NIL = (ATOM, 0)
VECT0 = 0x10                # VECTn (n = 1..6) is VECT0 + 2n, low bit as o/x
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
        self.sp = 0                           # structure pointer: where write_* stores next
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
            # Only the same string object: comparing contents is not
            # modelled (the Bluespec core stops there too).
            if a[1] != b[1]:
                raise Unimplemented('unify of two string objects')
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

    def new_string(self, n, size):
        """A new string of n zero elements of `size` bits."""
        if size not in (8, 16) or n < 0:
            raise Unimplemented('new_string(%d, %d)' % (n, size))
        return self.make_string(size, [0] * n)

    def set_element(self, s, i, e):
        """A copy of string s with element i set to e.  The machine may
        update in place when s is singly referenced; this model always
        copies."""
        size, elems = self.string(s)
        if not 0 <= i < len(elems):
            raise Unimplemented('built-in exception: string index %d' % i)
        elems = list(elems)
        elems[i] = e & ((1 << size) - 1)
        return self.make_string(size, elems)

    def element(self, s, i):
        _size, elems = self.string(s)
        if not 0 <= i < len(elems):
            raise Unimplemented('built-in exception: string index %d' % i)
        return (INT, elems[i])

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

    # vectors: {VECTn, address} -> n element cells, n = 1..6, no header
    # (library/kbn/kbnheap.kl1 heap/10; a functor term f(a,b) is the
    # vector {f, a, b}).  Longer vectors have a descriptor: not modelled.
    def term(self, w):
        """A term read out of memory, for tests: an integer, an atom's
        name, a tuple for a vector, a string as (bits, elements), or
        None for an unbound variable."""
        w = self.deref(w)
        t = w[0] & ~1
        if self.unbound(w) or t in (UNDF, HOOK):    # the latter: an element cell
            return None
        if t == INT:
            return signed(w[1])
        if t == ATOM:
            return [] if w[1] == 0 else self.im.atom(w[1])
        if t == LIST:
            # a Python list when the tail is one, else ('|', car, cdr)
            car, cdr = self.term(self.mem[w[1]]), self.term(self.mem[w[1] + 1])
            return [car] + cdr if isinstance(cdr, list) else ('|', car, cdr)
        if t == STRG:
            return self.string(w)
        if VECT0 <= t <= VECT0 + 14:
            n, a = self.vsize(w), self.vbase(w)
            return tuple(self.term(self.mem[a + i]) for i in range(n))
        raise Unimplemented('term with tag %02x' % w[0])

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
    def builtin(self, name, operands, f, nowait=()):
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
        wait = [w[1] for k, w in enumerate(vals) if self.unbound(w) and k not in nowait]
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

    def i_switch_on_non_list(self, pc, x, y, z, c16):
        # a list: the structure pointer is set to its car, for read_*
        w = self.g_word(x)
        if w is None or w[0] & ~1 != LIST:
            return pc + 2 + sx16(c16)
        self.sp = w[1]

    def i_switch_on_non_vector(self, pc, x, y, z, c16):
        # two cells: the label is the second (klb_opr.kl1 r_r_c16_i).
        # Only the branch is modelled: what r[y] gets for a vector is
        # not established.
        w = self.g_word(x)
        if w is None or self.vsize(w) is None:
            return pc + 2 + sx16(self.cells[pc + 1][1])
        # a vector: r[y] := its number of elements ("Ari", the arity,
        # in the compiler's index.kl1), the structure pointer at the
        # first
        self.reg[y] = (INT, self.vsize(w))
        self.sp = self.vbase(w)
        return pc + 2

    def vsize(self, w):
        """The number of elements of a vector word, None if it is not
        one.

        A vector of 7 or more is {VECT, a} -> {VDESC, a+3}, {INT, n},
        {INT, n}, then the n elements (library/kbn/kbnheap.kl1, the
        linker's heap writer: the only source; the IPL image holds no
        such vector).  Why the length is there twice is not known;
        this model reads the first and writes both."""
        t = w[0] & ~1
        if t == VECT0 + 14:
            return self.mem[w[1] + 1][1]
        return (t - VECT0) // 2 if VECT0 <= t <= VECT0 + 12 else None

    def vbase(self, w):
        """The address of a vector's first element."""
        return self.mem[w[1]][1] if w[0] & ~1 == VECT0 + 14 else w[1]

    def vnew(self, n):
        """(word, address of the first element) of a new vector of n
        cells, n >= 1, the elements not written."""
        if n <= 6:
            a = self.alloc(n)
            return (VECT0 + 2 * n + 1, a), a
        a = self.alloc(n + 3)
        self.mem[a] = (VDESC, a + 3)
        self.mem[a + 1] = self.mem[a + 2] = (INT, n)
        return (VECT0 + 15, a), a + 3

    def taken(self, a):
        """What is taken from the cell at a: its value, or a reference
        to it if it is an unbound variable."""
        c = self.mem[a]
        return (REF, a) if c[0] & ~1 in (UNDF, HOOK) else c

    def i_vector(self, pc, x, y, z, c16):
        # guard vector(X, ^Size)
        w = self.g_word(x)
        if w is None or self.vsize(w) is None:
            return self.guard_fail()
        self.reg[y] = (INT, self.vsize(w))

    def i_vector_element(self, pc, x, y, z, c16):
        # guard vector_element(Vector, Position, ^Element)
        v, i = self.g_word(x), self.g_word(y)
        if v is None or i is None or self.vsize(v) is None or i[0] & ~1 != INT \
                or not i[1] < self.vsize(v):
            return self.guard_fail()
        self.reg[z] = self.taken(self.vbase(v) + i[1])

    def i_mark_element(self, pc, x, y, z, c16):
        pass        # MRB marking of an element: no reference counts here

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

    def i_switch_on_constant(self, pc, x, y, z, c16):
        # word 1: register, the number of pairs.  Then `c16` pairs
        # {key, {INT, else << 16 | offset}}, both 16-bit fields relative
        # to the pair's second cell + 2 (klb_opr.kl1 r_c16_c16_16s_sw /
        # make_label).  Every pair carries the else label; an unbound
        # key takes the first pair's, as hash_on_constant takes its
        # miss label, and the variable is noted.
        cells = self.cells
        w = self.g_word(x)
        for k in range(c16):
            e = pc + 2 + 2 * k
            v = cells[e][1]
            if w is None or (k == c16 - 1 and cells[e - 1] != (w[0] & ~1, w[1])):
                return e + 2 + sx16(v >> 16)
            if cells[e - 1] == (w[0] & ~1, w[1]):
                return e + 2 + sx16(v)
        raise Unimplemented('switch_on_constant with no pairs at %d' % pc)

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

    def i_equal(self, pc, x, y, z, c16):
        return self.compare(x, y, lambda a, b: a == b)

    def i_and(self, pc, x, y, z, c16):           # guard arithmetic
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None:
            return self.guard_fail()
        self.reg[z] = (INT, (a & b) & 0xffffffff)

    def i_shift_right(self, pc, x, y, z, c16):   # guard arithmetic, logical
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or not 0 <= b < 32:
            return self.guard_fail()
        self.reg[z] = (INT, (a & 0xffffffff) >> b)

    def i_modulo(self, pc, x, y, z, c16):        # guard arithmetic
        # the remainder has the dividend's sign, as PDSS's C % (not
        # established for PIM/m); a zero divisor fails the guard
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or b == 0:
            return self.guard_fail()
        r = abs(a) % abs(b)
        self.reg[z] = (INT, (-r if a < 0 else r) & 0xffffffff)

    def i_integer(self, pc, x, y, z, c16):       # guard type check
        if self.g_int(x) is None:
            return self.guard_fail()

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
    def i_put_nil(self, pc, x, y, z, c16):
        self.reg[x] = NIL

    def i_put_constant(self, pc, x, y, z, c16):
        # two cells: the constant is the whole next cell (klb_opr.kl1 r_c40)
        self.reg[x] = self.cells[pc + 1]
        return pc + 2

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

    def i_get_bound_value(self, pc, x, y, z, c16):
        self.unify(self.reg[x], self.reg[y])   # as get_value; r[y] is known bound

    def i_get_atom(self, pc, x, y, z, c16):
        # one cell: opcode byte = c0 | register, low 24 bits = the atom
        v = self.cells[pc][1]
        self.unify(self.reg[(v >> 24) & 31], (ATOM, v & 0xffffff))

    def i_put_atom(self, pc, x, y, z, c16):
        # one cell: opcode byte = 40 | register, low 24 bits = the atom
        v = self.cells[pc][1]
        self.reg[(v >> 24) & 31] = (ATOM, v & 0xffffff)

    def i_wait_atom(self, pc, x, y, z, c16):
        # one cell: opcode byte = 80 | register, low 24 bits = the atom
        v = self.cells[pc][1]
        w = self.g_word((v >> 24) & 31)
        if w is None or (w[0] & ~1, w[1]) != (ATOM, v & 0xffffff):
            return self.guard_fail()

    def i_get_nil(self, pc, x, y, z, c16):
        self.unify(self.reg[x], NIL)

    def i_put_list(self, pc, x, y, z, c16):
        # two cells, car then cdr, filled by the two write_* that follow
        a = self.alloc(2)
        self.sp = a
        self.reg[x] = (LIST + 1, a)

    # Building a vector: put_vector_N takes N cells and points r[x] at
    # them; the N write_* instructions that follow fill them in order.
    def put_vector(self, n, x):
        a = self.alloc(n)
        self.sp = a
        self.reg[x] = (VECT0 + 2 * n + 1, a)

    def i_put_vector(self, pc, x, y, z, c16):
        # the general form: the size is the low 16 bits (load_module
        # builds module/9, ten cells, with put_vector r, 10).  The
        # image uses it for 7, 8 and 10 only; below 7 it is refused
        n = self.cells[pc][1] & 0xffff
        if n < 7:
            raise Unimplemented('put_vector of %d' % n)
        self.reg[x], self.sp = self.vnew(n)

    def i_put_vector_1(self, pc, x, y, z, c16):
        self.put_vector(1, x)

    def i_put_vector_5(self, pc, x, y, z, c16):
        self.put_vector(5, x)

    def i_put_vector_6(self, pc, x, y, z, c16):
        self.put_vector(6, x)

    def i_put_vector_2(self, pc, x, y, z, c16):
        self.put_vector(2, x)

    def i_put_vector_3(self, pc, x, y, z, c16):
        self.put_vector(3, x)

    def i_put_vector_4(self, pc, x, y, z, c16):
        self.put_vector(4, x)

    def i_write_atom(self, pc, x, y, z, c16):
        self.mem[self.sp] = (ATOM, self.cells[pc][1] & 0xffffff)
        self.sp += 1

    def i_write_integer(self, pc, x, y, z, c16):
        # the integer is the low 24 bits.  Whether bit 23 is a sign is
        # not established (the image has no such operand): refused
        v = self.cells[pc][1] & 0xffffff
        if v >> 23:
            raise Unimplemented('write_integer with bit 23 set')
        self.mem[self.sp] = (INT, v)
        self.sp += 1

    def i_write_nil(self, pc, x, y, z, c16):
        self.mem[self.sp] = NIL
        self.sp += 1

    def i_write_value(self, pc, x, y, z, c16):
        self.mem[self.sp] = self.reg[x]
        self.sp += 1

    def i_write_variable(self, pc, x, y, z, c16):
        # the element itself is the new variable; r[x] refers to it
        # (our choice: the machine's is not known).  The compiler names
        # r31 when the variable is not used again.
        self.mem[self.sp] = (UNDF, 0)
        self.reg[x] = (REF, self.sp)
        self.sp += 1

    def i_write_marked_variable(self, pc, x, y, z, c16):
        # as write_variable; the variable is referenced more than once
        # (MRB, not modelled)
        return self.i_write_variable(pc, x, y, z, c16)

    # Reading a vector: wait_vector_N checks r[x] and points the
    # structure pointer at its first element; each read_variable takes
    # the next element.  An element that is an unbound variable is
    # taken as a reference to it.
    def wait_vector(self, n, x):
        w = self.g_word(x)
        if w is None or w[0] & ~1 != VECT0 + 2 * n:
            return self.guard_fail()
        self.sp = w[1]

    def i_wait_vector_2(self, pc, x, y, z, c16):
        return self.wait_vector(2, x)

    def i_wait_vector_3(self, pc, x, y, z, c16):
        return self.wait_vector(3, x)

    def i_wait_vector_5(self, pc, x, y, z, c16):
        return self.wait_vector(5, x)

    def i_read_variable(self, pc, x, y, z, c16):
        self.reg[x] = self.taken(self.sp)
        self.sp += 1

    def i_put_reused_structure(self, pc, x, y, z, c16):
        # r[x] := a structure of z cells to be filled by write_*, which
        # the machine takes from r[y]'s cells when nothing else refers
        # to them (MRB).  No reference counts here, so nothing is ever
        # reused: new cells, under the tag r[y]'s structure has.
        w = self.deref(self.reg[y])
        a = self.alloc(z)
        self.sp = a
        self.reg[x] = (w[0], a)

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

    def i_b_multiply(self, pc, x, y, z, c16):
        # an overflow is the built-in's exception (PIMOS manual,
        # multiply): not modelled
        def f(a, b):
            p = signed(self.need_int(a) & 0xffffffff) * signed(self.need_int(b) & 0xffffffff)
            if not -(1 << 31) <= p < 1 << 31:
                raise Unimplemented('built-in exception: multiply overflow')
            return [(INT, p & 0xffffffff)]
        self.builtin('b_multiply', [x, y, z], f)

    def i_b_and(self, pc, x, y, z, c16):
        self.builtin('b_and', [x, y, z], lambda a, b: [
            (INT, (self.need_int(a) & self.need_int(b)) & 0xffffffff)])

    def i_b_or(self, pc, x, y, z, c16):
        self.builtin('b_or', [x, y, z], lambda a, b: [
            (INT, (self.need_int(a) | self.need_int(b)) & 0xffffffff)])

    def i_b_shift_left(self, pc, x, y, z, c16):
        # a count outside 0..31 is the built-in's exception (as PDSS,
        # blt_basic.c blt_b_shift_left): not modelled
        def f(a, b):
            n = self.need_int(b)
            if not 0 <= n < 32:
                raise Unimplemented('built-in exception: shift count %d' % n)
            return [(INT, (self.need_int(a) << n) & 0xffffffff)]
        self.builtin('b_shift_left', [x, y, z], f)

    def i_b_shift_right(self, pc, x, y, z, c16):
        # logical (manual, shift_right: "Logically shifts Integer to
        # the right"); the count as for b_shift_left
        def f(a, b):
            n = self.need_int(b)
            if not 0 <= n < 32:
                raise Unimplemented('built-in exception: shift count %d' % n)
            return [(INT, (self.need_int(a) & 0xffffffff) >> n)]
        self.builtin('b_shift_right', [x, y, z], f)

    # strings.  The fourth register of a four-register built-in is the
    # top byte of the following cell (klb_opr.kl1 p(r4,...)).
    def i_new_string(self, pc, x, y, z, c16):
        # new_string(^S, Length, ElementSize): r[z] := string of r[x] zeros
        def f(n, size):
            return [self.new_string(self.need_int(n), self.need_int(size))]
        self.builtin('new_string', [x, y, z], f)

    def i_b_string_element(self, pc, x, y, z, c16):
        # string_element(S, I, ^E, ^S1): r[z] := element, r[w] := the string
        w4 = self.cells[pc + 1][1] >> 24

        def f(s, i):
            self.need_string(s)
            return [self.element(s, self.need_int(i)), s]
        self.builtin('b_string_element', [x, y, z, w4], f)
        return pc + 2

    def i_set_string_element(self, pc, x, y, z, c16):
        # set_string_element(S, I, E, ^S1): r[w] := S with element I = r[z]
        w4 = self.cells[pc + 1][1] >> 24

        def f(s, i, e):
            self.need_string(s)
            return [self.set_element(s, self.need_int(i), self.need_int(e))]
        self.builtin('set_string_element', [x, y, z, w4], f)
        return pc + 2

    def i_new_vector(self, pc, x, y, z, c16):
        # new_vector(Size, ^V): n cells of integer 0 (PIMOS manual)
        def f(n):
            n = self.need_int(n)
            if n < 0:
                raise Unimplemented('new_vector of %d elements' % n)
            if n == 0:
                return [(VECT0, 0)]
            w, a = self.vnew(n)
            for k in range(n):
                self.mem[a + k] = (INT, 0)
            return [w]
        self.builtin('new_vector', [x, y], f)

    def i_set_vector_element(self, pc, x, y, z, c16):
        # set_vector_element(V, I, New, ^Old, ^V1).  Always a copy (no
        # MRB); an unbound element is copied as a reference to the old
        # cell.  It does not wait for New.
        w4, w5 = self.cells[pc + 1][1] >> 24, self.cells[pc + 1][1] >> 16 & 0xff

        def f(v, i, e):
            n, i = self.vsize(v), self.need_int(i)
            if n is None or not 0 <= i < n:
                raise Unimplemented('built-in exception: set_vector_element')
            src = self.vbase(v)
            w, a = self.vnew(n)
            old = None
            for k in range(n):
                c = self.taken(src + k)
                if k == i:
                    old = c
                self.mem[a + k] = e if k == i else c
            return [old, (v[0], w[1])]
        self.builtin('set_vector_element', [x, y, z, w4, w5], f, nowait=(2,))
        return pc + 2


def predicate(im, module, pred):
    for m in im.mods:
        if m['name'] == module:
            for n, _ln, addr in m['preds']:
                if n == pred:
                    return addr
    raise KeyError('%s:%s' % (module, pred))
