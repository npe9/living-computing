#!/usr/bin/env python3
"""A host-side reference model of the PIM/m KL1-B machine (scaffold).

It executes the PIMOS binaries' own cells: the 40-bit tagged words,
tag values (debugger/inspector/tagtbl.kl1), relative labels and
instruction encodings of the IPL image, loaded by asm/kbn.py.  It is
not the deliverable (docs/pimos_roadmap.md decision 3): the Bluespec
model is, and this exists to find out what the instructions do and to
be diffed against it.

Scope so far: goals on a single LIFO ready stack (no priorities, one
processor), suspension on unbound variables kept in a side table (the
machine's HOOK cells are not modelled), body built-ins that wait for
their inputs, 8- and 16-bit strings.  No garbage collection, no MRB,
no shoen, no exceptions.  An instruction this file does not
implement raises Unimplemented: it never guesses.

Every instruction's operand reading below is taken from object code
paired with its KL1 source; docs/pimm_semantics.md records which.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import kbn  # noqa: E402
import kbndis  # noqa: E402

INT, ATOM, REF, UNDF, STRG, CDESC = 0x00, 0x02, 0x06, 0x08, 0x0e, 0x25


class Unimplemented(Exception):
    pass


class Suspend(Exception):
    """A reduction cannot choose a clause until a variable is bound."""


class Fail(Exception):
    """No clause applies (a reduction failure), or a body unification fails."""


class Deadlock(Exception):
    """Nothing is ready and goals are still suspended."""


def sx16(v):
    v &= 0xffff
    return v - 0x10000 if v & 0x8000 else v


def signed(v):
    return v - (1 << 32) if v >> 31 else v


class _Regs(list):
    """The register file; writes are traced while a reduction runs."""

    def __setitem__(self, i, w):
        list.__setitem__(self, i, w)
        m = self.machine
        if m.tr is not None and m.tracing:
            m.tr.append('R %d %02x%08x' % (i, w[0], w[1]))


class _Mem(dict):
    """Memory; writes are traced while a reduction runs."""

    def __setitem__(self, a, w):
        dict.__setitem__(self, a, w)
        m = self.machine
        if m.tr is not None and m.tracing:
            m.tr.append('M %d %02x%08x' % (a - m.load, w[0], w[1]))


class Goal:
    """A goal record: code address and arguments, or a body built-in
    waiting for its inputs (code is then a Python function)."""

    def __init__(self, code, args, outs=None):
        self.code, self.args, self.outs = code, list(args), outs
        self.live = True


class Machine:
    def __init__(self, image=None, heap=0x100000):
        self.im = image or kbndis.Image()
        self.load = self.im.load
        # The lockstep trace (docs/pimm_semantics.md "Trace"): None, or a
        # list that receives one line per instruction, register write
        # and memory write made while a reduction runs.
        self.tr = None
        self.tracing = False
        # memory is addressed in cells, absolute (load address included)
        self.mem = _Mem({self.load + i: c for i, c in enumerate(self.im.cells)})
        self.mem.machine = self
        self.heap = self.load + heap          # fresh cells go here
        self.reg = _Regs([(INT, 0)] * 256)
        self.reg.machine = self
        self.argv = [(INT, 0)] * 256          # arguments of the goal being built
        self.ready = []                       # LIFO: the newest goal runs first
        self.hooks = {}                       # unbound cell -> goals waiting on it
        self.nsusp = 0
        self.builtin_waits = 0
        self.goal_waits = 0
        self.steps = 0
        self.reductions = 0
        self.names = {}

    # ---- data ----------------------------------------------------
    def alloc(self, n):
        a = self.heap
        self.heap += n
        return a

    def new_var(self):
        a = self.alloc(1)
        self.mem[a] = (UNDF, 0)
        return (REF, a)

    def deref(self, w):
        while w[0] & ~1 == REF:
            c = self.mem[w[1]]
            if c[0] == UNDF:
                return w                      # a reference to an unbound cell
            w = c
        return w

    def unbound(self, w):
        return w[0] & ~1 == REF               # after deref

    def bind(self, ref, w):
        assert self.mem[ref[1]][0] == UNDF
        self.mem[ref[1]] = w
        for g in self.hooks.pop(ref[1], ()):  # wake what waited on it
            if g.live:
                g.live = False
                self.nsusp -= 1
                self.ready.append(Goal(g.code, g.args, g.outs))

    def hook(self, goal, cells):
        self.nsusp += 1
        for c in set(cells):
            self.hooks.setdefault(c, []).append(goal)

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
    def call(self, pc, args):
        self.ready.append(Goal(pc, args))

    def run(self, pc=None, args=(), limit=10000000):
        """Run until nothing is ready.  Raises Suspend if goals are left
        waiting (a deadlock, or a goal waiting on the caller's variable)."""
        if pc is not None:
            self.call(pc, args)
        before = self.steps
        while self.ready:
            g = self.ready.pop()
            if g.outs is not None:
                self.resume_builtin(g)
            else:
                self.reduce(g, limit)
        if self.nsusp:
            raise Suspend('%d goals still suspended' % self.nsusp)
        return self.steps - before

    def abandon(self):
        """Drop every suspended goal (a test's way of ending a run)."""
        self.hooks.clear()
        self.nsusp = 0

    def reduce(self, g, limit):
        self.reductions += 1
        pc = g.code
        for i, a in enumerate(g.args):
            self.reg[i] = a
        self.alt = None                       # next clause on guard failure
        self.waiting = []                     # variables a guard wanted bound
        cells = self.im.cells
        self.tracing = True
        try:
            self.reduce_loop(pc, cells, limit)
            self.end('done')
        except Fail:
            self.end('fail')
            raise
        finally:
            self.tracing = False

    def end(self, how):
        if self.tr is not None and not self.ended:
            self.tr.append('E ' + how)
        self.ended = True

    def reduce_loop(self, pc, cells, limit):
        self.ended = False
        while True:
            self.steps += 1
            if self.steps > limit:
                raise RuntimeError('step limit')
            t, v = cells[pc]
            if t not in (0x22, 0x23):
                raise RuntimeError('pc %d is not an instruction: %02x:%08x' % (pc, t, v))
            name = self.names.get(pc)
            if name is None:
                name = self.names[pc] = self.im.dis(pc).split()[0]
            if self.tr is not None:
                self.tr.append('I %d %02x%08x' % (pc, t, v))
            fn = getattr(self, 'i_' + name, None)
            if fn is None:
                raise Unimplemented('%s at %d' % (name, pc))
            nxt = fn(pc, (v >> 16) & 255, (v >> 8) & 255, v & 255, v & 0xffff)
            if nxt == 'done':
                return
            pc = pc + 1 if nxt is None else nxt

    def guard_fail(self):
        if self.alt is None:
            raise RuntimeError('guard failed with no alternative')
        return self.alt

    def suspend_goal(self, pc, arity, c16):
        """Put the goal back as a record, entry = the label, arguments =
        r[0..arity), hooked on every variable a guard waited for."""
        self.goal_waits += 1
        self.end('susp')
        self.hook(Goal(pc + 2 + sx16(c16), self.reg[:arity]), self.waiting)
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
    def builtin(self, f, ins, outs):
        """Apply f to the dereferenced inputs and put its results in the
        output registers.  If an input is unbound the built-in becomes a
        goal waiting on it, and each output register gets a fresh
        variable that the built-in will bind when it runs."""
        vals = [self.deref(w) for w in ins]
        wait = [w[1] for w in vals if self.unbound(w)]
        if not wait:
            for r, w in zip(outs, f(*vals)):
                self.reg[r] = w
            return
        self.builtin_waits += 1
        outvars = [self.new_var() for _ in outs]
        for r, w in zip(outs, outvars):
            self.reg[r] = w
        self.hook(Goal(f, vals, outvars), wait)

    def resume_builtin(self, g):
        vals = [self.deref(w) for w in g.args]
        wait = [w[1] for w in vals if self.unbound(w)]
        if wait:
            self.hook(Goal(g.code, vals, g.outs), wait)
            return
        for var, w in zip(g.outs, g.code(*vals)):
            self.unify(var, w)

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
        cells = self.im.cells
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
        self.reg[x] = self.reg[y] = self.new_var()

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
        self.argv[x] = self.reg[y] = self.new_var()

    def i_enqueue_goal(self, pc, x, y, z, c16):
        self.ready.append(Goal(pc + 2 + sx16(c16), self.argv[1:x + 1]))

    def i_execute(self, pc, x, y, z, c16):
        # the same goal goes on as a reduction of the predicate at the label
        self.reductions += 1
        self.alt = None
        self.waiting = []
        return pc + 2 + sx16(c16)

    def i_proceed(self, pc, x, y, z, c16):
        return 'done'

    # body arithmetic: r[z] := r[x] op r[y]
    def i_b_add(self, pc, x, y, z, c16):
        self.builtin(lambda a, b: [(INT, (self.need_int(a) + self.need_int(b)) & 0xffffffff)],
                     [self.reg[x], self.reg[y]], [z])

    def i_b_subtract(self, pc, x, y, z, c16):
        self.builtin(lambda a, b: [(INT, (self.need_int(a) - self.need_int(b)) & 0xffffffff)],
                     [self.reg[x], self.reg[y]], [z])

    # strings.  The fourth register of a four-register built-in is the
    # top byte of the following cell (klb_opr.kl1 p(r4,...)).
    def i_new_string(self, pc, x, y, z, c16):
        # new_string(^S, Length, ElementSize): r[z] := string of r[x] zeros
        def f(n, size):
            return [self.make_string(self.need_int(size), [0] * self.need_int(n))]
        self.builtin(f, [self.reg[x], self.reg[y]], [z])

    def i_b_string_element(self, pc, x, y, z, c16):
        # string_element(S, I, ^E, ^S1): r[z] := element, r[w] := the string
        w4 = self.im.cells[pc + 1][1] >> 24

        def f(s, i):
            _size, elems = self.need_string(s)
            return [(INT, elems[self.need_int(i)]), s]
        self.builtin(f, [self.reg[x], self.reg[y]], [z, w4])
        return pc + 2

    def i_set_string_element(self, pc, x, y, z, c16):
        # set_string_element(S, I, E, ^S1): r[w] := S with element I = r[z].
        # The machine may update in place when S is singly referenced;
        # this model always copies.
        w4 = self.im.cells[pc + 1][1] >> 24

        def f(s, i, e):
            size, elems = self.need_string(s)
            elems = list(elems)
            elems[self.need_int(i)] = self.need_int(e) & ((1 << size) - 1)
            return [self.make_string(size, elems)]
        self.builtin(f, [self.reg[x], self.reg[y], self.reg[z]], [w4])
        return pc + 2


def predicate(im, module, pred):
    for m in im.mods:
        if m['name'] == module:
            for n, _ln, addr in m['preds']:
                if n == pred:
                    return addr
    raise KeyError('%s:%s' % (module, pred))
