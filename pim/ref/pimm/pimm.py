#!/usr/bin/env python3
"""A host-side reference model of the PIM/m KL1-B machine (scaffold).

It executes the PIMOS binaries' own cells: the 40-bit tagged words,
tag values (debugger/inspector/tagtbl.kl1), relative labels and
instruction encodings of the IPL image, loaded by asm/kbn.py.  It is
not the deliverable (docs/pimos_roadmap.md decision 3): the Bluespec
model is, and this exists to find out what the instructions do and to
be diffed against it.

Scope so far: one goal run to its end; no scheduler, no suspension
queue, no garbage collection.  An instruction this file does not
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

INT, ATOM, REF, UNDF = 0x00, 0x02, 0x06, 0x08


class Unimplemented(Exception):
    pass


class Suspend(Exception):
    """The goal cannot commit to any clause until a variable is bound."""


class Fail(Exception):
    """No clause applies (a reduction failure)."""


def sx16(v):
    v &= 0xffff
    return v - 0x10000 if v & 0x8000 else v


class Machine:
    def __init__(self, image=None):
        self.im = image or kbndis.Image()
        self.load = self.im.load
        # memory is addressed in cells, absolute (load address included)
        self.mem = {self.load + i: c for i, c in enumerate(self.im.cells)}
        self.heap = self.load + 0x100000      # fresh cells go here
        self.reg = [(INT, 0)] * 256
        self.steps = 0
        self.names = {}
        self.trace = None

    # ---- data ----------------------------------------------------
    def new_var(self):
        a = self.heap
        self.heap += 1
        self.mem[a] = (UNDF, 0)
        return (REF, a)

    def deref(self, w):
        while w[0] in (REF, REF | 1):
            c = self.mem[w[1]]
            if c[0] == UNDF:
                return w                      # a reference to an unbound cell
            w = c
        return w

    def unbound(self, w):
        return w[0] in (REF, REF | 1)         # after deref

    def bind(self, ref, w):
        assert self.mem[ref[1]][0] == UNDF
        self.mem[ref[1]] = w

    def unify(self, a, b):
        a, b = self.deref(a), self.deref(b)
        if self.unbound(a):
            if not (self.unbound(b) and b[1] == a[1]):
                self.bind(a, b)
            return
        if self.unbound(b):
            self.bind(b, a)
            return
        if a[0] & ~1 == b[0] & ~1 and a[0] in (INT, INT | 1, ATOM, ATOM | 1):
            if a[1] != b[1]:
                raise Fail('unify %r %r' % (a, b))   # body unification failure
            return
        raise Unimplemented('unify of %r and %r' % (a, b))

    def integer(self, r):
        """Guard read of an integer; None if unbound, Fail if another type."""
        w = self.deref(self.reg[r])
        if self.unbound(w):
            return None
        if w[0] & ~1 != INT:
            raise KeyError
        return w[1] - (1 << 32) if w[1] >> 31 else w[1]

    # ---- one goal --------------------------------------------------
    def run(self, pc, args, limit=100000):
        """Reduce one goal at code address pc (cell index) with args in
        r0.. until proceed.  Returns the number of instructions."""
        for i, a in enumerate(args):
            self.reg[i] = a
        self.alt = None                       # next clause on guard failure
        self.waiting = []                     # variables a guard wanted bound
        self.past_otherwise = False
        n = 0
        while True:
            n += 1
            if n > limit:
                raise RuntimeError('step limit')
            t, v = self.im.cells[pc]
            if t not in (0x22, 0x23):
                raise RuntimeError('pc %d is not an instruction: %02x:%08x' % (pc, t, v))
            name = self.names.get(pc)
            if name is None:
                name = self.names[pc] = self.im.dis(pc).split()[0]
            if self.trace is not None:
                self.trace.append((pc, name))
            fn = getattr(self, 'i_' + name, None)
            if fn is None:
                raise Unimplemented('%s at %d' % (name, pc))
            nxt = fn(pc, (v >> 16) & 255, (v >> 8) & 255, v & 255, v & 0xffff)
            if nxt == 'done':
                self.steps += n
                return n
            pc = pc + 1 if nxt is None else nxt

    def guard_fail(self):
        if self.alt is None:
            raise RuntimeError('guard failed with no alternative')
        return self.alt

    # ---- instructions ------------------------------------------------
    # clause selection
    def i_try_me_else(self, pc, x, y, z, c16):
        self.alt = pc + 2 + sx16(c16)

    def i_otherwise(self, pc, x, y, z, c16):
        # Clauses after `otherwise` apply only when none before can:
        # if an earlier guard was waiting on a variable, suspend instead.
        if self.waiting:
            raise Suspend(self.waiting)
        self.past_otherwise = True
        self.alt = None

    def i_suspend(self, pc, x, y, z, c16):
        if self.waiting:
            raise Suspend(self.waiting)
        raise Fail('no clause of the predicate at %d applies' % (pc + 2 + sx16(c16)))

    def i_switch_on_non_integer(self, pc, x, y, z, c16):
        w = self.deref(self.reg[x])
        if self.unbound(w):
            self.waiting.append(w[1])
            return pc + 2 + sx16(c16)
        if w[0] & ~1 != INT:
            return pc + 2 + sx16(c16)

    def i_hash_on_constant(self, pc, x, y, z, c16):
        # word 1: register, mask.  word 2: the miss label, relative to
        # itself.  Then mask+1 slots: {atom,0} empty, or {integer,
        # count << 16 | offset from the slot} to `count` {key, offset}
        # pairs; a pair's target is offset-cell + 1 + offset (kbn.kl1
        # out_hash_table / set_entry_part, hash_on_cnst).
        cells = self.im.cells
        miss = pc + 1 + 2 + sx16(cells[pc + 1][1])
        w = self.deref(self.reg[x])
        if self.unbound(w):
            self.waiting.append(w[1])
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
    def i_not_less_than(self, pc, x, y, z, c16):
        try:
            a, b = self.integer(x), self.integer(y)
        except KeyError:
            return self.guard_fail()
        if a is None or b is None:
            raise Unimplemented('not_less_than on an unbound variable')
        if not a >= b:
            return self.guard_fail()

    # moves and unification
    def i_put_integer(self, pc, x, y, z, c16):
        self.reg[x] = (INT, sx16(c16) & 0xffffffff)

    def i_get_integer(self, pc, x, y, z, c16):
        self.unify(self.reg[x], (INT, sx16(c16) & 0xffffffff))

    def i_get_value(self, pc, x, y, z, c16):
        self.unify(self.reg[x], self.reg[y])

    def i_collect_value(self, pc, x, y, z, c16):
        pass        # MRB reclamation of what r[x] points at: no GC here

    # body arithmetic: r[z] := r[x] op r[y]
    def arith(self, x, y, z, f):
        a, b = self.integer(x), self.integer(y)
        if a is None or b is None:
            raise Unimplemented('body arithmetic on an unbound variable')
        self.reg[z] = (INT, f(a, b) & 0xffffffff)

    def i_b_add(self, pc, x, y, z, c16):
        self.arith(x, y, z, lambda a, b: a + b)

    def i_b_subtract(self, pc, x, y, z, c16):
        self.arith(x, y, z, lambda a, b: a - b)

    def i_proceed(self, pc, x, y, z, c16):
        return 'done'


def predicate(im, module, pred):
    for m in im.mods:
        if m['name'] == module:
            for n, _ln, addr in m['preds']:
                if n == pred:
                    return addr
    raise KeyError('%s:%s' % (module, pred))
