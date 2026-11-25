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
strings.  Garbage collection only when collect_garbage asks for it
(R7G, pimm_gc.py, INFERENCE/OURS; otherwise the heap only grows); the MRB is
kept (docs/pimm_semantics.md "The MRB") but nothing is reclaimed on
it; the shoen in its first two stages only (create_shoen,
start_shoen, termination, shoen_statistics, remove_shoen: "the shoen"
below); no exceptions.  An instruction
this file does not implement raises Unimplemented: it never guesses.

The SCSI built-ins scsi_init and scsi_command run against a device
that is a Python object (Machine.fep, ref/pimm/fep.py); on the core
they are bsv/PimmScsiBox.bsv, the device on a port answered from the
tape this model records (lockstep_scsi.py, with ref_scsi.py's IPL
parts).  Nothing is on this model alone now.  The core has
since been given read_eagerly, not_equal and wait_vector_1/4/6
(lockstep_alt.py), b_divide, b_modulo, b_string and
enqueue_goal_to_processor (lockstep_body.py), string_operation
waiting on an element of its vector (lockstep_elw.py),
put_reused_structure of a long vector (lockstep_reuse.py) and a
merger input bound to a vector (lockstep_atom.py: this model now
makes those goals through the argument registers, as the core does).

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
from census import atom_base, opcode_table  # noqa: E402

INT, ATOM, REF, UNDF, HOOK, STRG, CDESC = 0x00, 0x02, 0x06, 0x08, 0x0a, 0x0e, 0x25
MOD = 0x27                  # a module object: {MOD, a} -> {CDESC, 06 << 24 | n}, n cells
# A code object: {COD, the address of a predicate's first instruction}
# (the tag from debugger/inspector/tagtbl.kl1; where it points is
# ASSUMED, see i_predicate_to_code).  COD and MOD differ only in the
# low bit, which is NOT an MRB for tags from 20h: compare whole tags.
COD = 0x26
PREDH = 0x24                # a predicate head: arity << 24 | offset from the module
VDESC = 0x0d                # kbnheap.kl1 tag(vdesc)
LIST = 0x04                 # {LIST, address} -> car, cdr; nil is the atom 0
NIL = (ATOM, 0)
FLT = 0x30                  # a floating point number (kbn.TAGS FLTo): not modelled
M32 = 0xffffffff
EXFLT = 0x3f                # an extended floating point (kbn.TAGS, kbnheap.kl1): not modelled
NEW_ATOM0 = 0x10000         # the first atom new_atom gives: ours
VECT0 = 0x10                # VECTn (n = 1..6) is VECT0 + 2n, low bit as o/x
# A shoen's handle: {SHREC, the address of its shoen record}.  The tag
# is PIM/m-sourced (PIMOS debugger/inspector/tagtbl.kl1, 16#"38" SHREC);
# what it points at is OURS (asm/pimm_layout.py).  From 20h: no MRB bit.
SHREC = 0x38
# THE CLOCK (system_timer, set_timer; fep.py's time of day): it advances
# with the instructions both models execute, one tick of the system
# timer (1/16 msec, PIMOS manual e-builtin.tex:1537-1549) every
# INSTRUCTIONS_PER_TICK instructions, counted before the instruction
# that reads it.  The rate: 615 KLIPS on append for one PIM/m processor
# (FGCS'92, M92 p. 425; docs/pim_architecture.md), the image's own
# append/3 (scsi_fep_module) taking 11 instructions a reduction, so
# 615000 * 11 instructions a second, 62.5 usec * 6.765e6 = 422.8 per
# tick.  That every instruction costs the same is OURS.
INSTRUCTIONS_PER_TICK = 423
from pimm_layout import (G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS,  # noqa: E402
                         READY, SUSPENDED, TAKEN, S_NEXT, S_GOAL, S_SIZE,
                         MEMORY_CELLS, HEAP)
from pimm_layout import (SH_COUNT, SH_STATUS, SH_PARENT, SH_REPORT,  # noqa: E402
                         SH_GOAL, SH_SIZE, DORMANT, STARTED, TERMINATED,
                         REPORT_STARTED, REPORT_TERMINATED)
from pimm_layout import (SH_REDUCTIONS, SH_REMOVE, REMOVED,  # noqa: E402
                         REPORT_STATISTICS_STARTED, REPORT_STATISTICS,
                         REPORT_RETURN_RESOURCE)
from pimm_layout import (SH_MASK, STOPPED, REPORT_ABORTED,  # noqa: E402
                         REPORT_EXCEPTION, REPORT_STOPPED,
                         EXC_REDUCTION_FAILURE, EXC_RAISED, REPORT_RESOURCE_ADDED,
                         REPORT_RESOURCE_REPORT_ALLOWED)
from pimm_layout import (SH_RSC_HI, SH_RSC_LO, SH_RSC_FLAGS,  # noqa: E402
                         RSC_REPORT_DISALLOWED, REPORT_RESOURCE_LOW)


class Unimplemented(Exception):
    pass


class Suspend(Exception):
    """The ready queue is empty and goals are still suspended."""


class Fail(Exception):
    """No clause applies (a reduction failure), or a body unification fails."""


def sx24(v):
    return v - (1 << 24) if v & 0x800000 else v


def sx16(v):
    v &= 0xffff
    return v - 0x10000 if v & 0x8000 else v


def signed(v):
    return v - (1 << 32) if v >> 31 else v


def marked(w):
    """The word with its MRB on: a reference or a pointer that is, or
    may be, held more than once.  Integers and atoms are left alone
    (PDSS marks them too; nothing reads their bit), as are the tags
    from 20h, which have no such bit."""
    return (w[0] | 1, w[1]) if 4 <= w[0] < 0x20 and w[0] & ~1 not in (UNDF, HOOK) else w


class _Regs(list):
    """A register file; every write is traced."""

    def __setitem__(self, i, w):
        list.__setitem__(self, i, w)
        m = self.machine
        if m.tr is not None:
            m.tr.append('%s %d %02x%08x' % (self.letter, i, w[0], w[1]))


class _Code(list):
    """The code as loaded; an index past it is a cell of the heap."""

    def __getitem__(self, i):
        if isinstance(i, int) and i >= len(self):
            m = self.machine
            return m.mem[m.load + i]
        return list.__getitem__(self, i)


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
    # the merger's list (2026-11-24): ready goals of the stub merge_in,
    # taken before the ready queue (Machine.ready, Machine.run).  mq is
    # its head; mwh, mwt the goals made ready since the last pickup, in
    # the order they were made ready.  Class defaults: a machine pickled
    # before them has none.  So a message bound to a merger input reaches
    # the output in the order of the unifications and before what the
    # binding reduction spawned, as VPIM (f_reduce_merger_unify.psl.c),
    # KLIC (runtime/gmerge.c) and PDSS (emulator/unify.c) do it AT the
    # unification; doing it at the next goal switch is OURS
    # (docs/pimm_semantics.md, merge)
    mq = mwh = mwt = 0

    def __init__(self, image=None, heap=HEAP, size=MEMORY_CELLS):
        self.im = image or kbndis.Image()
        self.load = self.im.load
        self.size = size
        # The lockstep trace (docs/pimm_semantics.md "Trace"): None, or a
        # list that receives one line per event.
        self.tr = None
        # code = the image, then the built-in stubs
        stubs, self.stubs = pimm_stubs.build(len(self.im.cells))
        # code is fetched from here: the image and the stubs as loaded,
        # and beyond them the heap, where a module the IPL builds lies
        self.cells = _Code(list(self.im.cells) + stubs)
        self.cells.machine = self
        assert len(self.cells) <= heap
        self.mem = _Mem({self.load + i: c for i, c in enumerate(self.cells)})
        self.mem.machine = self
        self.reg = _Regs([(INT, 0)] * 256)
        self.reg.machine, self.reg.letter = self, 'R'
        self.argv = _Regs([(INT, 0)] * 256)   # arguments of the goal being built
        self.argv.machine, self.argv.letter = self, 'A'
        self.hp = self.load + heap            # heap pointer: the next free cell
        self.rq = 0                           # ready queue: the newest goal record
        # the current shoen: the shoen record of the goal taken from the
        # ready queue; 0 for the root (no record) and between runs
        self.shoen = 0
        # the reductions of the goal in hand so far (shoen stage 2): one
        # for each execute and for its proceed (end_reduction)
        self.chain = 0
        self.next_atom = NEW_ATOM0            # new_atom's counter (ours)
        self.supplied = []                    # supply_atom_number's calls: not machine state
        self.sp = 0                           # structure pointer: where write_* stores next
        self.optab = opcode_table()
        self.optab[(0x22, 0x00)] = ('merge_in',)     # ours: asm/pimm_stubs.py
        self.optab[(0x22, 0x01)] = ('unify_step',)   # ours: asm/pimm_stubs.py
        self.optab[(0x22, 0x02)] = ('to_processor',)  # ours: asm/pimm_stubs.py
        # instruction names by code address; for code in the heap this
        # assumes a heap cell is never reused for other code
        self.names = {}
        # statistics, not machine state
        self.nsusp = 0
        self.steps = 0
        self.reductions = 0
        self.builtin_waits = 0
        self.goal_waits = 0
        # the SCSI device (ref/pimm/fep.py), None if there is none; its
        # commands that wait for the device; counts
        self.fep = None
        self.scsi_waiting = []
        self.scsi_commands = 0
        self.scsi_deferred = 0
        # every answer the device gave, in order: what driver.py writes
        # into a script as the bench's device tape (docs/pimm_semantics.md
        # "Trace", the B line)
        self.scsi_tape = []

    def event(self, text):
        if self.tr is not None:
            self.tr.append(text)

    # ---- data ----------------------------------------------------
    # The structure pointer.  sp_single: it was set by wait_vector_N
    # from a vector reached with every MRB off, so that read_variable
    # takes the elements as they are; anything else that sets it
    # clears that.
    @property
    def sp(self):
        return self._sp

    @sp.setter
    def sp(self, a):
        self._sp = a
        self.sp_single = False

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
        an unbound cell (UNDF, or HOOK when goals wait on it).  If any
        reference on the way has its MRB on, so has the result (PDSS
        emulator/deref.c: SetAll(reg, ..., MRBON))."""
        on = False
        while w[0] & ~1 == REF:
            on = on or bool(w[0] & 1)
            c = self.mem[w[1]]
            if c[0] == UNDF or c[0] & ~1 == HOOK:
                break
            w = c
        return marked(w) if on else w

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
                st = self.mem[g + G_STATUS][1]      # shoen << 2 | status
                if st & 3 == SUSPENDED:
                    self.event('W %d' % (g - self.load))
                    self.mem[g + G_STATUS] = (INT, st & ~3 | READY)
                    self.ready(g)
                    self.nsusp -= 1
                s = self.mem[s + S_NEXT][1]

    def ready(self, g):
        """A woken goal goes on the ready queue, or, a goal of the stub
        merge_in, at the end of the merger's list (docs/pimm_semantics.md,
        merge: a goal record made READY, a vector's element, stays on the
        ready queue)."""
        if self.mem[g + G_CODE][1] == self.load + self.stubs['$merge_in']['addr']:
            self.mem[g + G_LINK] = (INT, 0)
            if self.mwh:
                self.mem[self.mwt + G_LINK] = (INT, g)
            else:
                self.mwh = g
            self.mwt = g
        else:
            self.mem[g + G_LINK] = (INT, self.rq)
            self.rq = g

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
        if a[0] & ~1 == LIST or VECT0 + 2 <= a[0] & ~1 <= VECT0 + 14:
            # Two lists, or two vectors of the same size (of up to six:
            # the size is in the tag, so the tags were equal).  Not
            # unified here: a goal is made that unifies the elements
            # when it runs, as PDSS does (emulator/unify.c
            # make_unify_list_list_goal_and_enqueue,
            # make_unify_vector_vector_goal_and_enqueue).  What PIM/m's
            # firmware did is not known.  The goal's code is the stub
            # unify_step (asm/pimm_stubs.py).  The same object against
            # itself makes a goal too, as in PDSS.  Two vectors of seven
            # or more (2026-11-24): their sizes are in memory, so they
            # are compared in the goal's steps, not here (OURS; PDSS
            # active_unify_with_vector compares the lengths first: a
            # failure either way)
            self.record(READY, self.stubs['$unify_step']['addr'], [a, b, (INT, 0)])
            return
        # a module, anything else
        raise Unimplemented('unify of %r and %r' % (a, b))

    # strings: {STRG, address} -> {CDESC, pad << 27 | type << 24 | words},
    # then `words` cells of 32 bits, elements packed from the top.
    # type 3 = 8-bit elements, 4 = 16-bit, 5 = 32-bit, 0 = 1-bit
    # (kbnheap.kl1 string_cdesc:168-175).  The pad is two bits at 27
    # for types 3..5 and five bits at 27 for type 0: (32 - Len mod 32)
    # << 27, the 32 of a whole last word falling out of the word.
    # VPIM: "the element sizes are 1, 8, 16 and 32"
    # (interpreter/klb_body_blt_struct.psl.c kblt_b_search_character,
    # its PreCondition); element 0 is the top bit of the first word, as
    # for the other sizes (2026-11-25, met compiling the primer's
    # sample1: compiler/reg.kl1 new_string(Str, Size, 1)).
    def string(self, w):
        t, v = self.mem[w[1]]
        if t != CDESC:
            raise RuntimeError('string without a descriptor at %x' % w[1])
        typ, words = (v >> 24) & 7, v & 0xffffff
        pad = (v >> 27) & (31 if typ == 0 else 3)
        if typ not in (0, 3, 4, 5):
            raise Unimplemented('string element type %d' % typ)
        size = 1 << typ if typ else 1
        per = 32 // size
        out = []
        for i in range(words):
            x = self.mem[w[1] + 1 + i][1]
            out += [(x >> (32 - size * (k + 1))) & ((1 << size) - 1) for k in range(per)]
        return size, out[:len(out) - pad]

    def new_string(self, n, size):
        """A new string of n zero elements of `size` bits."""
        if size not in (1, 8, 16, 32) or n < 0:
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
        typ = {1: 0, 8: 3, 16: 4, 32: 5}[size]
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
        if w[0] == COD:
            return ('COD', w[1] - self.load)
        if w[0] == MOD:                      # tags from 20h have no MRB bit
            return ('MOD', self.mem[w[1]][1] & 0xffffff)
        if w[0] == SHREC:
            return ('SHREC', w[1] - self.load)
        if VECT0 <= t <= VECT0 + 14:
            n, a = self.vsize(w), self.vbase(w)
            return tuple(self.term(self.mem[a + i]) for i in range(n))
        raise Unimplemented('term with tag %02x' % w[0])

    # ---- goals -----------------------------------------------------
    def record(self, status, code, args, shoen=None):
        """Write a goal record; code is a cell index.  It belongs to the
        current shoen and is counted there; with `shoen` (a shoen
        record: create_shoen's first goal) to that one, not counted."""
        g = self.alloc(G_ARGS + len(args))
        self.mem[g + G_LINK] = (INT, self.rq if status == READY else 0)
        self.mem[g + G_STATUS] = self.gstatus(status, shoen)
        self.mem[g + G_CODE] = (INT, self.load + code)
        self.mem[g + G_ARGN] = (INT, len(args))
        for i, a in enumerate(args):
            self.mem[g + G_ARGS + i] = a
        if shoen is None:
            self.counted()
        if status == READY:
            self.rq = g
        return g

    # ---- the shoen ---------------------------------------------------
    # Stages 1 and 2: create_shoen, start_shoen, termination,
    # shoen_statistics, remove_shoen.  What is
    # PIM/m-sourced is said at each place; the record, the count, the
    # parked first goal and when a message is reported are not (they
    # are carried over from PDSS and VPIM, or ours): docs/
    # pimm_semantics.md "Shoen".
    def gstatus(self, status, shoen=None):
        """A goal record's status cell: {INT, shoen << 2 | status}, the
        shoen as its record's address relative to the load address; the
        root is 0, so a goal outside every shoen has the plain status
        (OURS, asm/pimm_layout.py)."""
        sh = self.shoen if shoen is None else shoen
        return (INT, ((sh - self.load) << 2 if sh else 0) | status)

    def counted(self):
        """A goal record has been written while a shoen is current: one
        more on its count.  Nothing for the root.  (Carried over from
        PDSS: record.h number_of_children, counted up where a goal
        record is made.)"""
        if self.shoen:
            a = self.shoen + SH_COUNT
            self.mem[a] = (INT, self.mem[a][1] + 1)

    def report(self, sh, code, car=None):
        """A message on a shoen's report stream: its unbound tail is
        bound to [code | NewTail] (or [car | NewTail]), waking the
        goals that wait on it, and NewTail is the tail from now on
        (OURS).  The tail is followed through references (create_shoen
        run from its stub has its Report bound to the caller's
        variable); a tail that someone has bound to a value (or that
        remove_shoen has closed) is refused."""
        c = self.alloc(2)
        self.mem[c] = (INT, code) if car is None else car
        self.mem[c + 1] = (UNDF, 0)
        tail = self.deref(self.mem[sh + SH_REPORT])
        if not self.unbound(tail):
            raise Unimplemented('the report stream of a shoen is bound to %r' % (tail,))
        self.unify(tail, (LIST, c))
        self.mem[sh + SH_REPORT] = (REF, c + 1)

    def report3(self, sh, code, h, lo):
        """A message {code, H, L} on the report stream: the vector's
        three cells, then the list cell as report() makes it."""
        v = self.alloc(3)
        self.mem[v] = (INT, code)
        self.mem[v + 1] = (INT, h & 0xffffffff)
        self.mem[v + 2] = (INT, lo & 0xffffffff)
        self.report(sh, None, car=(VECT0 + 6, v))

    def remove(self, sh):
        """A terminated shoen is removed: {14, H, L}, return_resource
        with the resource left (R7L, 2026-11-25: "The remaining amount
        of the resource when the shoen execution terminated is reported
        with this message", manual e-shoen.tex:246; a shoen that went
        past its bound has none left, 0), then the report stream is
        closed (its tail unified with []) and the record marked
        REMOVED.  VPIM's order (f_shoen_control.psl.c:547-575,
        f_shoen_with_fp.psl.c:69-71: return_resource, close, reclaim),
        not PIM/m-sourced.  (Until R7L this was {14, 0, 0}, no resource
        being modelled.)"""
        left = max(self.rsc_left(sh), 0)
        self.report3(sh, REPORT_RETURN_RESOURCE, left >> 32, left)
        tail = self.deref(self.mem[sh + SH_REPORT])
        if not self.unbound(tail):
            raise Unimplemented('the report stream of a shoen is bound to %r' % (tail,))
        self.unify(tail, NIL)
        self.mem[sh + SH_STATUS] = (INT, REMOVED)

    def end_reduction(self):
        """The run of a goal has ended (proceed or suspend; not
        execute, which goes on with the same goal).  First its
        reductions (self.chain: each execute, and the proceed) are
        added to its shoen's SH_REDUCTIONS.  Then one less on the
        shoen's count.  A suspension wrote its record first (+1), so it
        nets nothing.  At 0 the shoen has terminated: its status says
        so, 12 (terminated) is reported (and if remove_shoen came
        first, it is removed now: 14, the close), and its parent, of
        which it was one, gets its reductions added and loses one in
        turn.  Nothing for the root.

        What a reduction is: the PIMOS manual (e-shoen.tex:388-395, the
        profile's counts) has reductions = dequeues and executes less
        suspensions, which is one per execute and one per proceed; PDSS
        counts there too (emulator/emulate.c:333-365, KL1B_PROCEED,
        KL1B_EXECUTE, KL1B_EXECUTE_EXTERNAL).  That a statistic covers
        the descendant shoen is the manual's (e-shoen.tex:234); adding
        a child's total to its parent at its termination is PDSS's
        (shoen.c:293).  Writing the cell once per run, at its end, is
        OURS.

        Carried over from PDSS (emulator/emulate.c:340 "if(--number_
        of_children == 0){ terminate_shoen(); }"; shoen.c:280-309: the
        parent's count, the report, recursing) and VPIM (functions/
        f_shoen_with_fp.psl.c:86: `terminated` alone while the control
        stream is open); not PIM/m-sourced.  The code 12 is
        (asm/pimm_layout.py).

        Before that (R7L, 2026-11-25), the resource: 2 for each of the
        run's reductions ("1 for goal creation and 1 for termination of
        the reduction, thus 2 is taken for each reduction", manual
        e-shoen.tex:42) is taken from the resource left of the goal's
        shoen and of every shoen above it, innermost first (a shoen's
        consumption includes its descendants', e-shoen.tex:234; VPIM
        supplies a child shoen's resource from its parent's foster
        parent, f_shoen_with_fp.psl.c f_CheckShoenResourceLeftMargin).
        Taking it once per run, at its end, without VPIM's supply
        units, is OURS.  Nothing for the root, nor for a run of no
        reduction."""
        if self.chain:
            for sh in self.chain_of(self.shoen):
                self.set_rsc_left(sh, self.rsc_left(sh) - 2 * self.chain)
        self.ended(self.shoen, self.chain)

    def ended(self, sh, red):
        """The end of one of shoen sh's goals (or of a child shoen whose
        total is red): as end_reduction says, from sh up."""
        while sh:
            red = self.mem[sh + SH_REDUCTIONS][1] + red & 0xffffffff
            self.mem[sh + SH_REDUCTIONS] = (INT, red)
            n = self.mem[sh + SH_COUNT][1] - 1 & 0xffffffff
            self.mem[sh + SH_COUNT] = (INT, n)
            if n:
                break
            self.terminate(sh)
            sh = self.mem[sh + SH_PARENT][1]

    def terminate(self, sh):
        """A shoen terminates: TERMINATED, 12, and the removal if a
        remove_shoen came first."""
        self.mem[sh + SH_STATUS] = (INT, TERMINATED)
        self.report(sh, REPORT_TERMINATED)
        if self.mem[sh + SH_REMOVE][1]:
            self.remove(sh)

    # ---- shoen stage 3: exceptions, stop, abort -------------------------
    def chain_of(self, sh):
        """The shoen sh and those above it, innermost first (reads only)."""
        while sh:
            yield sh
            sh = self.mem[sh + SH_PARENT][1]

    def exception(self, num, tag, b, c):
        """An exception: reported to the innermost shoen, from the
        current one up, whose mask AND tag is not 0 (PIM/m-sourced: the
        PIMOS manual e-shoen.tex:57 "the innermost parent shoen for
        which AND of the exception tag and the mask pattern is not 0";
        its raise/3 hint, :776, says "is 0", taken as a slip: with
        execute/4's mask -1 nothing would ever be reported.  VPIM's
        s_IfExceptionMasked accepts only if mask AND tag = tag, which
        differs for a tag of several bits).  None accepts it: refused
        (OURS: what the machine did is not sourced).

        What is done, in VPIM's order (f_reduce_exception_handler.psl.c
        f_Failure_Sub, f_Raise_Sub: carried over, not PIM/m-sourced):
        two fresh variables NewCode and NewArgv; a READY goal
        apply(NewCode, NewArgv) of the CURRENT shoen, counted there (so
        the shoen does not terminate until the handler binds them: the
        manual, e-shoen.tex:59-60); the Info vector {Pe, b, c}, Pe = 0,
        the one processor (OURS; the image's exception_table:translate/4
        turns it into a node number); then the message {2, num, Info,
        NewCode, NewArgv} (pimos.vmac shoen#exception, the image's
        report/2) on the report stream of the shoen found.  c may be a
        function that makes it, called after the goal (the ArgV of a
        reduction failure: VPIM makes it there)."""
        target = 0
        for sh in self.chain_of(self.shoen):
            if self.mem[sh + SH_MASK][1] & tag:
                target = sh
                break
        if not target:
            raise Unimplemented('an exception (tag %x) no shoen accepts' % tag)
        nc, na = self.new_var(), self.new_var()
        self.record(READY, self.stubs['apply']['addr'], [nc, na])
        if callable(c):
            c = c()
        info = self.alloc(3)
        self.mem[info] = (INT, 0)
        self.mem[info + 1] = b
        self.mem[info + 2] = c
        m = self.alloc(5)
        self.mem[m] = (INT, REPORT_EXCEPTION)
        self.mem[m + 1] = (INT, num)
        self.mem[m + 2] = (VECT0 + 6, info)
        self.mem[m + 3] = nc
        self.mem[m + 4] = na
        self.report(target, None, car=(VECT0 + 10, m))

    def rsc_left(self, sh):
        """The resource left of shoen sh, a signed 64-bit integer from
        its two cells (asm/pimm_layout.py SH_RSC_HI, SH_RSC_LO)."""
        v = self.mem[sh + SH_RSC_HI][1] << 32 | self.mem[sh + SH_RSC_LO][1]
        return v - (1 << 64) if v >> 63 else v

    def set_rsc_left(self, sh, v):
        """Write the resource left of shoen sh, high cell first."""
        if not -(1 << 63) <= v < 1 << 63:
            raise Unimplemented('the resource left of a shoen past 64 bits: %d' % v)
        v &= (1 << 64) - 1
        self.mem[sh + SH_RSC_HI] = (INT, v >> 32)
        self.mem[sh + SH_RSC_LO] = (INT, v & M32)

    def taken_check(self, g):
        """A goal of a shoen taken from the ready queue (after its
        arguments are loaded): 'run', or 'aborted' if a shoen at or above
        its own is TERMINATED or REMOVED (only an abort leaves a goal
        there: a shoen that ends by itself has none), or 'park' if one is
        STOPPED or EXHAUSTED.  A parked goal is SUSPENDED and put on the
        parked list of the innermost such shoen; start_shoen releases a
        stopped one's, add_shoen_resource an exhausted one's.
        Carried over from PDSS (emulator/goal.c:302-335: at dequeue, a
        goal whose shoen is aborted is freed, one whose shoen is
        suspended is hooked on the shoen's queue); where the check is
        made and the list are OURS.

        Exhausted (R7L, 2026-11-25): no resource left, the shoen's
        consumption at or past its bound.  "When resource consumption
        actually exceeds the upper bound, execution is suspended.  ...
        If the upper bound value is increased when execution is
        suspended due to trespassing the upper bound, shoen execution
        resumes" (manual e-shoen.tex:31).  If the innermost shoen that
        stops the goal is an exhausted one (not a stopped one) and its
        reports are allowed, resource_low (6) is reported to it and its
        reports are disallowed (e-shoen.tex:179, 218-224; VPIM
        f_ReplicateSupplyResourceDestinations, f_shoen_with_fp.psl.c:
        560-590: _RESOURCE_LIMIT_OVER reports _RSC_LOW_REP when the
        disallowed flag is off and sets it).  "How close the resource
        consumption has come to the upper bound when this report is
        made depends on the processing system" (e-shoen.tex:224): here
        it is made when none is left, OURS (VPIM: when the bound less
        what was supplied is under one supply unit, 2^24).  A task
        that PIMOS starts with no resource parameter has a bound of 0
        (kernel/task/int_hdl.kl1:191 {0,0}, zero_check 560-566 sends
        `start` alone), so its first goal reports resource_low: the
        Listener's task monitor waits for exactly that
        (debugger/listener/task_mon.kl1:13)."""
        park = 0
        for sh in self.chain_of(self.shoen):
            st = self.mem[sh + SH_STATUS][1]
            if st in (TERMINATED, REMOVED):
                return 'aborted'
            if not park and (st == STOPPED or self.rsc_left(sh) <= 0):
                park = sh
        if not park:
            return 'run'
        if self.mem[park + SH_STATUS][1] != STOPPED \
                and not self.mem[park + SH_RSC_FLAGS][1] & RSC_REPORT_DISALLOWED:
            self.mem[park + SH_RSC_FLAGS] = (INT, self.mem[park + SH_RSC_FLAGS][1] | RSC_REPORT_DISALLOWED)
            self.report(park, REPORT_RESOURCE_LOW)
        st = self.mem[g + G_STATUS][1]
        self.mem[g + G_STATUS] = (INT, st & ~3 | SUSPENDED)
        self.mem[g + G_LINK] = self.mem[park + SH_GOAL]
        self.mem[park + SH_GOAL] = (INT, g)
        self.nsusp += 1
        return 'park'

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
        while True:
            if self.gc_request:
                # R7G: the collection collect_garbage asked for, at the
                # goal switch, before the alarm (pimm_gc.py: INFERENCE)
                self.gc_request = False
                import pimm_gc
                pimm_gc.collect(self)
            if self.alarm_var is not None and self.alarm_due():
                self.fire_alarm()       # R7L: before the next goal is taken
            g = self.pick()
            if not g:
                break
            self.event('G %d' % (g - self.load))
            st = self.mem[g + G_STATUS][1]        # shoen << 2 | status
            self.shoen = self.load + (st >> 2) if st >> 2 else 0
            self.mem[g + G_STATUS] = (INT, st & ~3 | TAKEN)
            code = self.mem[g + G_CODE][1] - self.load
            for i in range(self.mem[g + G_ARGN][1]):
                self.reg[i] = self.mem[g + G_ARGS + i]
            if self.shoen:
                how = self.taken_check(g)
                if how != 'run':
                    self.event('E ' + how)
                    continue
            self.chain = 0
            self.reduce(code, before + limit)     # the limit is this run's
            self.end_reduction()
        self.shoen = 0                # what a bench makes between runs is the root's
        self.event('Q')
        if self.nsusp:
            raise Suspend('%d goals still suspended' % self.nsusp)
        return self.steps - before

    def pick(self):
        """The next goal to run, taken off its list, or 0.  The goals
        made ready since the last pickup go to the front of the
        merger's list (in the order they were made ready), and that
        list is taken before the ready queue."""
        if self.mwh:
            self.mem[self.mwt + G_LINK] = (INT, self.mq)
            self.mq, self.mwh, self.mwt = self.mwh, 0, 0
        if self.mq:
            g = self.mq
            self.mq = self.mem[g + G_LINK][1]
        else:
            g = self.rq
            if g:
                self.rq = self.mem[g + G_LINK][1]
        return g

    def abandon(self):
        """Forget that goals are suspended (a test's way of ending a run).
        Their records and hooks stay in memory."""
        self.nsusp = 0

    def opname(self, pc):
        name = self.names.get(pc)
        if name is None:
            if pc < len(self.im.cells):
                name = self.im.dis(pc).split()[0]
            elif pc < len(self.cells):       # a built-in's stub
                t, v = self.cells[pc]
                name = self.optab[(t, v >> 24)][0]
            else:
                # code in the heap, named as asm/kbndis.py names the
                # image's: the atom forms carry a register in the
                # opcode, two opcodes are numbered by their x field
                t, v = self.cells[pc]
                k = (t, v >> 24)
                if k not in self.im.key:
                    name = self.im.key[(0x23, atom_base(v >> 24))][0]
                else:
                    name = self.im.key[k][0]
                    fn = kbndis.functions().get(k)
                    if fn:
                        if (v >> 16) & 255 not in fn:
                            raise Unimplemented('%s function %d at %d' % (name, (v >> 16) & 255, pc))
                        name = fn[(v >> 16) & 255][0]
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
                self.pc = pc                  # for a message; not machine state
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
            if self.shoen:
                # inside a shoen a failure is reported to the shoen (the
                # exception path).  A reduction failure is (i_suspend);
                # a failed body unification, unification_failure, is
                # not modelled: refused
                raise Unimplemented('a goal failed inside a shoen')
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
    def builtin(self, name, operands, f, nowait=(), elements=None):
        """A body built-in with register operands, directions from the
        stub table.  f takes the dereferenced inputs and returns the
        output words.  If an input is unbound the built-in becomes a
        suspended goal of its stub (asm/pimm_stubs.py), waiting on the
        first such input; each output operand's argument is a fresh
        variable, which the register also gets.  `elements`, for a
        built-in whose input is a vector of arguments: called with the
        inputs once they are all bound, it returns the addresses of
        the unbound cells among the elements it needs, and the
        built-in waits on the first of those the same way."""
        stub = self.stubs[name]
        dirs = stub['dirs']
        ins = [r for r, d in zip(operands, dirs) if d == 'i']
        outs = [r for r, d in zip(operands, dirs) if d == 'o']
        vals = [self.deref(self.reg[r]) for r in ins]
        wait = [w[1] for k, w in enumerate(vals) if self.unbound(w) and k not in nowait]
        if not wait and elements is not None:
            wait = elements(*vals)
            if wait and name not in ('string_operation', 'scsi_command'):
                self.alone(name + ' waiting on a vector element')
        if not wait:
            for r, w in zip(outs, f(*vals)):
                self.reg[r] = w
            return
        self.builtin_waits += 1
        self.nsusp += 1
        g = self.alloc(G_ARGS + len(operands))
        self.mem[g + G_LINK] = (INT, 0)
        self.mem[g + G_STATUS] = self.gstatus(SUSPENDED)
        self.mem[g + G_CODE] = (INT, self.load + stub['addr'])
        self.mem[g + G_ARGN] = (INT, len(operands))
        for k, (r, d) in enumerate(zip(operands, dirs)):
            if d == 'i':
                self.mem[g + G_ARGS + k] = self.reg[r]
            else:
                var = self.new_var()
                self.mem[g + G_ARGS + k] = var
                self.reg[r] = var
        self.counted()
        self.hook(g, wait[0])

    # What only this model has (see the module's header) is refused
    # unless a bench asks for it, so that the lockstep tests, which
    # enter whatever this model can run, stay within what the Bluespec
    # core has too.  ref/pimm/ref_scsi.py sets it.  The list shrinks
    # as each piece is given to the core with a lockstep test.
    ahead = False

    def alone(self, what):
        if not self.ahead:
            raise Unimplemented(what + ': on the reference model alone (Machine.ahead)')

    def unbound_elements(self, v):
        """The addresses of the unbound cells among a vector's elements,
        in order."""
        out = []
        for i in range(self.vsize(v)):
            c = self.deref(self.taken(self.vbase(v) + i))
            if self.unbound(c):
                out.append(c[1])
        return out

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

    def i_jump(self, pc, x, y, z, c16):
        # 23:67 c16_exe: an unconditional branch to the label, the
        # label as try_me_else's (assembler/klb_opr.kl1 p(c16_exe),
        # cal_location_address: Label - (pc + 2)).  The compiler puts
        # it after a branch of register shortage (compiler/regass.kl1
        # insertBranch); VPIM klb_control.psl.c klb_jump and PDSS
        # emulate.c KL1B_JUMP branch with nothing else
        return pc + 2 + sx16(c16)

    def i_otherwise(self, pc, x, y, z, c16):
        # Clauses after `otherwise` apply only when none before can:
        # if an earlier guard was waiting on a variable, suspend instead.
        if self.waiting:
            return self.suspend_goal(pc, x, c16)
        self.alt = None

    def i_suspend(self, pc, x, y, z, c16):
        if self.waiting:
            return self.suspend_goal(pc, x, c16)
        if self.shoen:
            # No clause applies inside a shoen: reduction_failure (number
            # 9, tag 1 << 25: pimos.vmac, the manual's tag table), Info
            # {Pe, Code, ArgV} (PIMOS kernel/builtin/excpt_tbl.kl1
            # "FIRMWARE FORMAT" 9; VPIM f_Failure_Sub).  Code: the code
            # of the predicate, {COD, the label}, which is the entry a
            # suspension would resume at; ArgV: a vector of r[0..x) as
            # they stand (OURS: VPIM takes the goal record's).  The goal
            # ends; that counts as one reduction (OURS, as a proceed:
            # the manual's profile counts reductions as dequeues and
            # executes less suspensions).  An arity of 0 or above 6 (a
            # long vector) is refused.
            if not 1 <= x <= 6:
                raise Unimplemented('reduction failure of arity %d inside a shoen' % x)
            def argv():
                v = self.alloc(x)
                for i in range(x):
                    self.mem[v + i] = self.reg[i]
                return (VECT0 + 2 * x, v)
            self.exception(EXC_REDUCTION_FAILURE, 1 << 16 + EXC_REDUCTION_FAILURE,
                           (COD, self.load + pc + 2 + sx16(c16)), argv)
            self.chain += 1
            self.event('E fail')
            return 'done'
        raise Fail('no clause of the predicate at %d applies' % (pc + 2 + sx16(c16)))

    def i_switch_on_non_integer(self, pc, x, y, z, c16):
        w = self.g_word(x)
        if w is None or w[0] & ~1 != INT:
            return pc + 2 + sx16(c16)

    def i_tag_and_value(self, pc, x, y, z, c16):
        # guard tag_and_value(X, ^Tag, ^Value): the cell's tag and its
        # value, as integers (PDSS emulator/blt_system.c; the unloader
        # writes instruction cells with it, encoder.kl1 encode_code,
        # and the .sav files hold their tags as the image has them).
        # Function 4 of opcode 76; two cells, the third register in
        # the next cell's top byte.  For a tag that has an MRB bit,
        # whether that bit is returned is not established: the tag is
        # returned as it stands.
        if x != 4:
            raise Unimplemented('opcode 76 function %d' % x)
        w = self.g_word(y)
        if w is None:
            return self.guard_fail()
        self.reg[z] = (INT, w[0])
        self.reg[self.cells[pc + 1][1] >> 24] = (INT, w[1])
        return pc + 2

    def i_switch_on_non_atom(self, pc, x, y, z, c16):
        w = self.g_word(x)
        if w is None or w[0] & ~1 != ATOM:
            return pc + 2 + sx16(c16)

    def i_wait_nil(self, pc, x, y, z, c16):
        w = self.g_word(x)
        if w is None or (w[0] & ~1, w[1]) != NIL:
            return self.guard_fail()

    def i_wait_list(self, pc, x, y, z, c16):
        # a list: the structure pointer is set to its car, for read_*
        w = self.g_word(x)
        if w is None or w[0] & ~1 != LIST:
            return self.guard_fail()
        self.sp = w[1]

    def i_read_atom(self, pc, x, y, z, c16):
        # the element at the structure pointer must be the atom in the
        # low 24 bits; an unbound one is noted and the guard fails
        w = self.deref(self.taken(self.sp))
        if self.unbound(w):
            self.waiting.append(w[1])
            return self.guard_fail()
        if (w[0] & ~1, w[1]) != (ATOM, self.cells[pc][1] & 0xffffff):
            return self.guard_fail()
        self._sp += 1

    def i_add(self, pc, x, y, z, c16):           # guard arithmetic
        # an overflow fails the guard (PIMOS manual, add)
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or not -(1 << 31) <= a + b < 1 << 31:
            return self.guard_fail()
        self.reg[z] = (INT, (a + b) & 0xffffffff)

    def i_multiply(self, pc, x, y, z, c16):      # guard arithmetic
        # multiply(Integer1, Integer2, ^NewInteger), 23:F6 r_r_r
        # (inst_tab.kl1:209; directions iio, blt.kl1:29-30): "Fail,
        # Exception: if either ... is not an integer; if an overflow
        # occurs" (PIMOS manual, e-builtin.tex:268-283): as a guard,
        # the guard fails; an unbound operand is noted
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or not -(1 << 31) <= a * b < 1 << 31:
            return self.guard_fail()
        self.reg[z] = (INT, (a * b) & 0xffffffff)

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

    def taken(self, a, single=False, mark=False):
        """What is taken from the cell at a: its value, or a reference
        to it if it is an unbound variable.  The cell goes on holding
        it, so what is taken has its MRB on, unless the structure is
        `single`: reached by a path with every MRB off, and read by
        read_variable (PDSS read_car/read_element: "if(Mrbof(ptr) ==
        MRBON) SetMrbof(car, MRBON)").  With `mark` the cell itself is
        marked too (PDSS b_vector_element, mark_element), written only
        if that changes it."""
        c = self.mem[a]
        if c[0] & ~1 in (UNDF, HOOK):
            return (REF, a) if single else (REF + 1, a)
        if mark and marked(c) != c:
            self.mem[a] = marked(c)
        return c if single else marked(c)

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
        # mark_element(Vector, Position): the element's MRB on, in the
        # vector (PDSS emulate.c KL1B_MARK_ELEMENT; TR-733's "MRBを
        # オンにする").  It follows a guard vector_element whose
        # vector is used again.
        v, i = self.deref(self.reg[x]), self.deref(self.reg[y])
        if self.vsize(v) is None or i[0] & ~1 != INT or not i[1] < self.vsize(v):
            raise Unimplemented('mark_element of %r, %r' % (v, i))
        self.taken(self.vbase(v) + i[1], mark=True)

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

    def i_display_console(self, pc, x, y, z, c16):
        # display_console(X): "displays the current value of X on the
        # console window, even if this variable is unbound" (PDSS
        # manual); it does not wait and cannot fail.  What the console
        # is given is traced: the value, and for a string its
        # descriptor and words.  How PIM/m's console showed a value
        # (an integer's digits, the end of a line) is not known and
        # not modelled.
        w = self.deref(self.reg[x])
        self.event('C %02x%08x' % w)
        if w[0] & ~1 == STRG:
            for i in range((self.mem[w[1]][1] & 0xffffff) + 1):
                self.event('S %02x%08x' % self.mem[w[1] + i])

    def i_wait_integer(self, pc, x, y, z, c16):
        if self.g_int(x) != sx16(c16):
            return self.guard_fail()

    @staticmethod
    def atomic(w):
        return w[0] & ~1 in (INT, ATOM)

    def i_wait_value(self, pc, x, y, z, c16):
        # the guard X = Y on two arguments (TR-246 p. 5).  Modelled for
        # atomic values and strings: two strings are equal when their
        # descriptors and all their words are (PDSS emulator/passive.c
        # passive_unify, case STRING), a string and an atomic value
        # are not.  Lists and vectors as below; one variable twice is
        # refused
        a, b = self.deref(self.reg[x]), self.deref(self.reg[y])
        if self.unbound(a) and self.unbound(b) and a[1] == b[1]:
            raise Unimplemented('wait_value of a variable with itself')
        a, b = self.g_word(x), self.g_word(y)
        if a is None or b is None:
            return self.guard_fail()
        sa, sb = a[0] & ~1 == STRG, b[0] & ~1 == STRG
        if sa and sb:
            n = self.mem[a[1]][1] & 0xffffff
            if self.mem[a[1]] != self.mem[b[1]] or any(
                    self.mem[a[1] + i][1] != self.mem[b[1] + i][1] for i in range(1, n + 1)):
                return self.guard_fail()
            return
        if (sa or self.atomic(a)) and (sb or self.atomic(b)) and (sa or sb):
            return self.guard_fail()
        if self.structure(a) or self.structure(b):
            # lists and vectors: the general passive unification,
            # VPIM's (passive below; 2026-11-25, before: two vectors of
            # 0..6 atomic elements, after PDSS).  The Bluespec's is
            # PimmPBox.bsv, step for step
            if not self.passive(a, b):
                return self.guard_fail()
            return
        if not (self.atomic(a) and self.atomic(b)):
            raise Unimplemented('wait_value on a structure')
        if (a[0] & ~1, a[1]) != (b[0] & ~1, b[1]):
            return self.guard_fail()

    def structure(self, w):
        return w[0] & ~1 == LIST or self.vsize(w) is not None

    # VPIM's unify stack: _LOCAL_MEM_UNIFY_STACK_AREA_SIZE 0x800 words
    # (basics/bsc_mem_map.psl.c:90), a frame of 4 (crp, size, X's and
    # Y's first element; structures/str_passive_unify.psl.c
    # C_U_STACK_FRAME_SIZE), so 512 frames.  VPIM's bound, not PIM/m's
    # (its microcode is not held)
    PASSIVE_FRAMES = 512

    def passive(self, a, b):
        """Two bound words, at least one a list or a vector: whether
        they are equal (wait_value), as VPIM's f_EqualStruct and
        f_Equal_Sub take them (functions/f_reduce_passive_unify.psl.c
        41-109, 166-312): words of two types are not equal; two null
        vectors are; two long vectors of different sizes are not; two
        lists or vectors are compared element by element, depth first,
        with an explicit stack of frames (crp, size, X's and Y's first
        element; structures/str_passive_unify.psl.c).  Each pair of
        elements, dereferenced: an unbound X is noted and the answer is
        False (s_PushSuspendStack, Lsusp), then an unbound Y; a module
        or a code is equal only to the same tag and value (MOD 27h and
        COD 26h differ in the bit other tags keep for the MRB); other
        types that differ are not equal; integers and atoms by tag and
        value; strings by descriptor and words; a null
        vector is equal; a list or vector (a long one after its size)
        pushes the frame in hand, even one at its end (so a list's cdr
        takes a frame), and its elements are compared next.  Refused,
        loud: a 513th frame (VPIM suspends there with a DEBUG warning
        and no variable, which would hang the goal) and a type the
        model does not compare (a float: VPIM compares its value; or
        any other).  VPIM's deref writes the result back into the
        structure: not carried over (PIM/m's microcode is not held).
        2026-11-25, met by the compiler on the primer's sample1
        (pimos::keyed_bag if_empty/4, utility/pool/k_bag.kl1:155, the
        keys {car, {arg, 1}} of library/compiler/index.kl1:787); before,
        two short vectors of atomic elements only."""
        stack = []
        frame = None
        x, y = a, b
        while True:
            if self.unbound(x):
                self.waiting.append(x[1])
                return False
            if self.unbound(y):
                self.waiting.append(y[1])
                return False
            tx, ty = x[0] & ~1, y[0] & ~1
            expand = None
            if x[0] in (MOD, COD) or y[0] in (MOD, COD):
                if x != y:                             # tags from 20h: no MRB bit
                    return False
            elif tx != ty:
                return False
            elif tx in (INT, ATOM):
                if x[1] != y[1]:
                    return False
            elif tx == STRG:
                k = self.mem[x[1]][1] & 0xffffff
                if self.mem[x[1]] != self.mem[y[1]] or any(
                        self.mem[x[1] + i][1] != self.mem[y[1] + i][1] for i in range(1, k + 1)):
                    return False
            elif tx == VECT0:
                pass                                   # the null vector
            elif tx == LIST:
                expand = (x[1], y[1], 2)
            elif self.vsize(x) is not None:
                n = self.vsize(x)
                if n != self.vsize(y):
                    return False                       # long vectors of two sizes
                expand = (self.vbase(x), self.vbase(y), n)
            else:
                raise Unimplemented('wait_value: an element %r' % (x,))
            if expand:
                if frame is not None:
                    if len(stack) == self.PASSIVE_FRAMES:
                        raise Unimplemented('wait_value: the unify stack full (%d frames)'
                                            % self.PASSIVE_FRAMES)
                    stack.append(frame)
                frame = [0, expand[2], expand[0], expand[1]]
            else:
                while frame is None or frame[0] == frame[1]:
                    if not stack:
                        return True
                    frame = stack.pop()
            crp, _n, xa, ya = frame
            x = self.deref(self.taken(xa + crp))
            y = self.deref(self.taken(ya + crp))
            frame[0] = crp + 1

    def i_diff(self, pc, x, y, z, c16):
        # the guard diff(X, Y), X \= Y, 23:F9 r_r (inst_tab.kl1:212;
        # both inputs, blt.kl1:239-244): "Succeeds if it is assured
        # that X is not equal to Y ... X or Y must be an atomic term";
        # suspends on an unbound one, fails if they are equal (PIMOS
        # manual, e-builtin.tex:114-143).  A term that is not atomic
        # is "Illegal DIFF!!!" on the CSP (the same page): refused.
        # Atomic here: an integer or an atom (the manual's empty
        # vector is refused, not met)
        a, b = self.g_word(x), self.g_word(y)
        if a is None or b is None:
            return self.guard_fail()
        if not self.atomic(a) and not self.atomic(b):
            raise Unimplemented('diff on two terms that are not atomic')
        if not (self.atomic(a) and self.atomic(b)):
            # one atomic (one word), the other a structure, string or
            # the like: never equal, diff succeeds.  The manual: "X or
            # Y must be an atomic term"; KLIC (include/klic/gb.h
            # gblt_diff: "isatomic(y) || isatomic(x) ? (x) == (y)")
            # and PDSS (emulator/emulate.c KL1B_G_DIFF, passive_unify)
            # agree.  Met in pim:go/4 (task_handler)
            return None
        if (a[0] & ~1, a[1]) == (b[0] & ~1, b[1]):
            return self.guard_fail()

    def i_wait_constant(self, pc, x, y, z, c16):
        # two cells: the constant is the whole next cell (r_c40), as
        # put_constant's.  Atomic values only
        w, k = self.g_word(x), self.cells[pc + 1]
        if w is None:
            return self.guard_fail()
        if not (self.atomic(w) and self.atomic(k)):
            raise Unimplemented('wait_constant on a structure')
        if (w[0] & ~1, w[1]) != (k[0] & ~1, k[1]):
            return self.guard_fail()
        return pc + 2

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

    def i_not_equal(self, pc, x, y, z, c16):
        # guard not_equal(Integer1, Integer2), X =\= Y: "Succeeds if
        # Integer1 is not equal to Integer2"; suspends on an
        # uninstantiated one, fails on a non-integer (PIMOS manual,
        # e-builtin.tex line 206)
        return self.compare(x, y, lambda a, b: a != b)

    def i_floating_point_not_less_than(self, pc, x, y, z, c16):
        # guard floating_point_not_less_than(F1, F2), function 3 of
        # opcode 23:FC, registers y and z.  "If both Float1 and Float2
        # are floating points and the value of the former is larger
        # than, or equal that of the latter, this predicate succeeds.
        # Otherwise it fails" (PDSS manual).  The IPL's pool tries it
        # on every key that is neither atom nor integer; there is no
        # floating point here, so two floats are refused.
        a, b = self.g_word(y), self.g_word(z)
        if a is None or b is None or a[0] & ~1 != FLT or b[0] & ~1 != FLT:
            return self.guard_fail()
        raise Unimplemented('floating point comparison')

    def i_exclusive_or(self, pc, x, y, z, c16):  # guard arithmetic
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None:
            return self.guard_fail()
        self.reg[z] = (INT, (a ^ b) & 0xffffffff)

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

    def i_shift_left(self, pc, x, y, z, c16):    # guard arithmetic
        # as the body b_shift_left: bits shifted out are lost; a count
        # outside 0..31 fails the guard, as shift_right
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or not 0 <= b < 32:
            return self.guard_fail()
        self.reg[z] = (INT, (a << b) & 0xffffffff)

    def i_modulo(self, pc, x, y, z, c16):        # guard arithmetic
        # the remainder has the dividend's sign, as PDSS's C % (not
        # established for PIM/m); a zero divisor fails the guard
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or b == 0:
            return self.guard_fail()
        r = abs(a) % abs(b)
        self.reg[z] = (INT, (-r if a < 0 else r) & 0xffffffff)

    def i_divide(self, pc, x, y, z, c16):        # guard arithmetic
        # "The result of the division is unified with NewInteger ...
        # if overflow is detected, or if Integer2 is bound to 0,
        # failure or exception occurs" (PDSS manual): in a guard, a
        # failure.  The quotient is truncated towards zero, as PDSS's
        # C / (not established for PIM/m, as for modulo); the one
        # overflow is the least integer divided by -1.
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None or b == 0 or (a == -1 << 31 and b == -1):
            return self.guard_fail()
        q = abs(a) // abs(b)
        self.reg[z] = (INT, (-q if (a < 0) != (b < 0) else q) & 0xffffffff)

    def i_extended_floating_point(self, pc, x, y, z, c16):
        # guard extended_floating_point(X, ^NewX), function 8 of 23:6E
        # f_r_r (assembler/inst_tab.kl1:104), registers y and z; X an
        # input waited for before it, NewX an output (compiler/blt.kl1
        # builtin(extended_floating_point(X1, X2)): In [X1], Out [X2],
        # Pre [wait]).  The type test: an extended floating point has
        # its own tag, 3Fh (library/kbn/kbnheap.kl1, asm/kbn.py TAGS
        # ex_float).  Anything else fails (2026-11-24, met in pim:go/4
        # after the login, on a non-float); an unbound X is noted.  An
        # extended float is refused: none can be made here, and what
        # NewX is is not documented
        w = self.g_word(y)
        if w is None or w[0] != EXFLT:
            return self.guard_fail()
        raise Unimplemented('extended_floating_point of an extended float')

    def ext_float_compare(self, y, z):
        """The guards extended_floating_point_less_than (function 2 of
        23:6E f_r_r) and extended_floating_point_not_less_than (3),
        registers y and z (assembler/inst_tab.kl1:98-99; compiler/
        blt.kl1:417-424, both inputs waited for, class user): the
        compiler's `$$<` and `$$>=` in a guard (macro/pimos/pimos/
        pimos.smac:390-405).  Neither the PIMOS manual nor VPIM nor PDSS
        has them.  Two arguments that are not both extended floats
        (tag 3Fh) fail the guard: the held sorter relies on it, its
        comparator trying the integer, float and extended-float
        comparisons, then atoms, then strings, then `otherwise` for
        anything else (utility/sorter/sorter.kl1:51-71), as the float
        comparison fails on anything but two floats (PDSS manual,
        i_floating_point_not_less_than).  Two extended floats are
        refused: none can be made here (R7L, 2026-11-25: met in the
        Listener, the sort of the goal's variables)."""
        a, b = self.g_word(y), self.g_word(z)
        if a is None or b is None or a[0] != EXFLT or b[0] != EXFLT:
            return self.guard_fail()
        raise Unimplemented('extended floating point comparison')

    def i_extended_floating_point_less_than(self, pc, x, y, z, c16):
        return self.ext_float_compare(y, z)

    def i_extended_floating_point_not_less_than(self, pc, x, y, z, c16):
        return self.ext_float_compare(y, z)

    def i_floating_point(self, pc, x, y, z, c16):
        # guard floating_point(X): "If X is a floating point, this
        # predicate succeeds, otherwise it fails" (PDSS manual); an
        # unbound X is noted
        w = self.g_word(x)
        if w is None or w[0] & ~1 != FLT:
            return self.guard_fail()

    def i_atom(self, pc, x, y, z, c16):          # guard type check
        # "If X is an atom, this predicate succeeds, otherwise it
        # fails" (PDSS manual); an unbound X is noted
        w = self.g_word(x)
        if w is None or w[0] & ~1 != ATOM:
            return self.guard_fail()

    def i_integer(self, pc, x, y, z, c16):       # guard type check
        if self.g_int(x) is None:
            return self.guard_fail()

    def i_subtract(self, pc, x, y, z, c16):      # guard arithmetic
        a, b = self.g_int(x), self.g_int(y)
        if a is None or b is None:
            return self.guard_fail()
        self.reg[z] = (INT, (a - b) & 0xffffffff)

    def i_string_element(self, pc, x, y, z, c16):
        # guard string_element(String, Position, ^Element); anything
        # but a string and a position inside it fails the guard
        w, i = self.g_word(x), self.g_int(y)
        if w is None or i is None or w[0] & ~1 != STRG:
            return self.guard_fail()
        _size, elems = self.string(w)
        if not 0 <= i < len(elems):
            return self.guard_fail()
        self.reg[z] = (INT, elems[i])

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

    # save r, POS and restore r, POS, 23:19 and 23:1A r_c16
    # (inst_tab.kl1:23, 25): the KL1 compiler's spill of a register it
    # has run out of (library/compiler/regass.kl1 outputCode/6,
    # saveRegisters, restoreRegisters: save(Y, W) after the register Y
    # is written, restore(Y, W) before it is read again, W the virtual
    # register).  TM-1044 names them save(Reg, POS) and restore(POS,
    # Reg) on "work memory" (作業用メモリ, TM-1044.j_s3.tex:1559-1567, as
    # listed in docs/literature_gaps.md), in each processor's local
    # fixed area.  HERE (OURS) that area is 256 slots of its own,
    # traced as V lines; a POS of 256 or more is refused
    def work(self):
        if 'wk' not in self.__dict__:
            self.wk = _Regs([(INT, 0)] * 256)
            self.wk.machine, self.wk.letter = self, 'V'
        return self.wk

    def i_save(self, pc, x, y, z, c16):
        if c16 >= 256:
            raise Unimplemented('save to work slot %d' % c16)
        self.work()[c16] = self.reg[x]

    def i_restore(self, pc, x, y, z, c16):
        if c16 >= 256:
            raise Unimplemented('restore from work slot %d' % c16)
        self.reg[x] = self.work()[c16]

    def i_put_marked_value(self, pc, x, y, z, c16):
        # "the same functions as those without it except that the MRB
        # of the destination is always set.  They are for reference
        # duplication" (TR-248 sec. 6); PDSS marks the source first
        self.reg[y] = marked(self.reg[y])
        self.reg[x] = self.reg[y]

    def i_put_variable(self, pc, x, y, z, c16):
        var = self.new_var()
        self.reg[x] = var
        self.reg[y] = var

    def i_put_marked_variable(self, pc, x, y, z, c16):
        # as put_variable, both references with the MRB on (PDSS
        # emulate.c KL1B_PUT_MARKED_VARIABLE: SetAll(reg, REF, undef,
        # MRBON), then the second register a copy)
        var = self.new_var()
        self.reg[x] = (REF + 1, var[1])
        self.reg[y] = (REF + 1, var[1])

    def i_get_constant(self, pc, x, y, z, c16):
        # get_constant(X, C), 23:B8 r_c40 (assembler/inst_tab.kl1:174):
        # r[x] unified with the constant, the whole next cell, as
        # put_constant's.  The compiler writes it for an atomic constant
        # that is not an atom nor [] (library/compiler/comp.kl1
        # compile_put_valuable, instrtbl.kl1 convert_instr)
        self.unify(self.reg[x], self.cells[pc + 1])
        return pc + 2

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

    def i_put_vector_0(self, pc, x, y, z, c16):
        self.reg[x] = (VECT0, 0)              # the empty vector: no cells

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
        self._sp += 1

    def i_write_integer(self, pc, x, y, z, c16):
        # the integer is the low 24 bits, SIGNED: the PIMOS assembler
        # writes an integer constant in -2^23..2^23-1 (16#"FF800000"
        # ..16#"007FFFFF") in this c24 form, masked to 24 bits, and any
        # other in the two-cell c40 form (library/assembler/klb_opr.kl1
        # p(c24, ..), lines 50-54, and p(c40, ..), 60-81).  A real -1:
        # scsi_fep's check_data_size1/6, `L = [-1|NL]`
        # (bios/fep_module/scsi_fep.kl1:429-433)
        v = sx24(self.cells[pc][1] & 0xffffff)
        self.mem[self.sp] = (INT, v & 0xffffffff)
        self._sp += 1

    def i_write_nil(self, pc, x, y, z, c16):
        self.mem[self.sp] = NIL
        self._sp += 1

    def i_write_marked_value(self, pc, x, y, z, c16):
        # as write_value, both copies marked (see put_marked_value)
        self.reg[x] = marked(self.reg[x])
        return self.i_write_value(pc, x, y, z, c16)

    def i_write_value(self, pc, x, y, z, c16):
        self.mem[self.sp] = self.reg[x]
        self._sp += 1

    def i_write_variable(self, pc, x, y, z, c16):
        # the element itself is the new variable; r[x] refers to it
        # (our choice: the machine's is not known).  The compiler names
        # r31 when the variable is not used again.
        self.mem[self.sp] = (UNDF, 0)
        self.reg[x] = (REF, self.sp)
        self._sp += 1

    def i_write_marked_variable(self, pc, x, y, z, c16):
        # as write_variable; the variable is referenced more than
        # once, so r[x]'s reference has its MRB on
        self.mem[self.sp] = (UNDF, 0)
        self.reg[x] = (REF + 1, self.sp)
        self._sp += 1

    # Reading a vector: wait_vector_N checks r[x] and points the
    # structure pointer at its first element; each read_variable takes
    # the next element.  An element that is an unbound variable is
    # taken as a reference to it.
    def wait_vector(self, n, x):
        w = self.g_word(x)
        if w is None or w[0] & ~1 != VECT0 + 2 * n:
            return self.guard_fail()
        self.sp = w[1]
        self.sp_single = not w[0] & 1

    def i_wait_vector(self, pc, x, y, z, c16):
        # the general form, 23:AF r_vector: a vector of 7 or more, the
        # length in the low bits (assembler klb_opr.kl1 p(r_vector, ..)
        # Length>6: Op \/ Reg<<16 \/ Length; read as 16 bits, as
        # put_vector's).  Below 7 the assembler writes wait_vector_N
        n = c16
        if n < 7:
            raise Unimplemented('wait_vector of %d' % n)
        w = self.g_word(x)
        if w is None or w[0] & ~1 != VECT0 + 14 or self.vsize(w) != n:
            return self.guard_fail()
        self.sp = self.vbase(w)
        self.sp_single = not w[0] & 1

    def i_wait_vector_2(self, pc, x, y, z, c16):
        return self.wait_vector(2, x)

    def i_wait_vector_3(self, pc, x, y, z, c16):
        return self.wait_vector(3, x)

    def i_wait_vector_5(self, pc, x, y, z, c16):
        return self.wait_vector(5, x)

    def i_wait_vector_0(self, pc, x, y, z, c16):
        # the empty vector {} (no element is read after it)
        return self.wait_vector(0, x)

    def i_wait_vector_1(self, pc, x, y, z, c16):
        return self.wait_vector(1, x)

    def i_wait_vector_4(self, pc, x, y, z, c16):
        return self.wait_vector(4, x)

    def i_wait_vector_6(self, pc, x, y, z, c16):
        return self.wait_vector(6, x)

    def i_read_variable(self, pc, x, y, z, c16):
        self.reg[x] = self.taken(self.sp, single=self.sp_single)
        self._sp += 1

    def i_read_variable_without_deref(self, pc, x, y, z, c16):
        # The compiler writes this for read_variable when the clause
        # collects the structure and not the element (library/compiler/
        # regass.kl1 convertIfNotCollected); same operands, same data
        # movement.  The machine's read_variable dereferences what it
        # takes at once and this one does not; here neither does (the
        # instruction that uses the register dereferences), so the
        # two are the same.
        return self.i_read_variable(pc, x, y, z, c16)

    def i_put_reused_structure(self, pc, x, y, z, c16):
        # r[x] := a structure of z cells to be filled by write_*, which
        # the machine takes from r[y]'s cells when nothing else refers
        # to them (MRB).  No reference counts here, so nothing is ever
        # reused: new cells, under the tag r[y]'s structure has.
        # A vector of seven or more has its descriptor (vsize): the
        # new one gets its own.
        w = self.deref(self.reg[y])
        if w[0] & ~1 == VECT0 + 14:
            if z < 7:       # a long vector's tag on fewer than seven cells
                raise Unimplemented('put_reused_structure of %d cells from a long vector' % z)
            new, self.sp = self.vnew(z)
            self.reg[x] = (w[0], new[1])
            return
        a = self.alloc(z)
        self.sp = a
        self.reg[x] = (w[0], a)

    def i_collect_value(self, pc, x, y, z, c16):
        pass        # MRB reclamation of what r[x] points at: no GC here

    # building and starting goals
    def i_set_value(self, pc, x, y, z, c16):
        self.argv[x] = self.reg[y]

    def i_set_marked_value(self, pc, x, y, z, c16):
        self.reg[y] = marked(self.reg[y])     # see put_marked_value
        self.argv[x] = self.reg[y]

    def i_set_atom(self, pc, x, y, z, c16):
        # one cell: opcode byte = the goal argument (0..15), low 24
        # bits = the atom (assembler/inst_tab.kl1: set_atom_1..15)
        v = self.cells[pc][1]
        self.argv[v >> 24] = (ATOM, v & 0xffffff)

    def i_calculate_priority_from_minimum(self, pc, x, y, z, c16):
        # calculate_priority_from_minimum(X, ^Y): "the logical priority
        # corresponding to X is calculated from the logical priority
        # range for the shoen"; X is 0..4096 (manual).  There is no
        # shoen here: the range is taken as 0..4096, so Y = X.  That
        # range is ours.
        def f(v):
            v = self.need_int(v)
            if not 0 <= v <= 4096:
                raise Unimplemented('calculate_priority_from_minimum of %d' % v)
            return [(INT, v)]
        self.builtin('calculate_priority_from_minimum', [x, y], f)

    def i_calculate_priority_from_current(self, pc, x, y, z, c16):
        # calculate_priority_from_current(X, ^Y), 22:EC r_r: "the
        # logical priority corresponding to X is calculated from the
        # logical priority of this predicate"; X is -4096..4096
        # (PIMOS manual, e-builtin.tex calculate_priority_from_current).
        # The manual gives no formula; this is PDSS's (emulator/
        # blt_system.c blt_b_rltv): for X >= 0 the current priority
        # plus X/4096 of the way to the shoen's maximum, for X < 0
        # minus -X/4096 of the way to its minimum.  There is no shoen
        # here: the range is 0..4096, as for _from_minimum (ours), and
        # the current priority is the range's top, 4096 (ours; PDSS
        # starts a shoen's goals at its maximum, emulator/shoen.c:100,
        # 166).  So Y = 4096 + X for X < 0, 4096 for X >= 0, and
        # shoen:execute/7's X = C - 4096 gives C.
        def f(v):
            v = self.need_int(v)
            if not -4096 <= v <= 4096:
                raise Unimplemented('calculate_priority_from_current of %d' % v)
            return [(INT, 4096 + v if v < 0 else 4096)]
        self.builtin('calculate_priority_from_current', [x, y], f)

    def i_system_timer(self, pc, x, y, z, c16):  # guard, no input
        # system_timer(^X1, ^X2), 23:78 r_r (blt.kl1:287-288, both
        # outputs): "The upper 16 bits of the time (in 1/16 msec units)
        # that has passed since the processor ... was booted is unified
        # with X1, and the lower 32 bits ... with X2. Suspend,
        # Exception: None" (manual, e-builtin.tex:1537-1549).  VPIM
        # gives X1 = 0 and X2 the current time (klb_pimos.psl.c
        # kblt_system_timer, "just for PIM/s").  The clock (2026-11-24;
        # it stood at 0 before): self.timer(), 48 bits, X1 its upper 16,
        # X2 its lower 32, written r[x] then r[y]
        t = self.timer()
        self.reg[x] = (INT, (t >> 32) & 0xffff)
        self.reg[y] = (INT, t & 0xffffffff)

    def timer(self):
        """The system timer, in 1/16 msec: the instructions executed
        before this one, INSTRUCTIONS_PER_TICK to a tick (OURS rate,
        above), 48 bits; plus the ticks the clock was moved on while the
        machine waited for an alarm (tick_skip, R7L)."""
        return ((self.steps - 1) // INSTRUCTIONS_PER_TICK + self.tick_skip) & 0xffffffffffff

    # The alarm (R7L, 2026-11-25): set_timer's request still to come, one
    # for the processor (VPIM klb_pimos.psl.c kblt_b_set_timer: the PE's
    # AlarmTimerVar and _SetAlarmTimer).  Class attributes, so that a
    # machine pickled before R7L has none.
    alarm_time = None       # the time asked for, 32 bits
    alarm_var = None        # the Wakeup variable it binds
    tick_skip = 0           # ticks the clock was moved on, idle (alarm_skip)

    @staticmethod
    def reached(t, now):
        """A time t is reached at now (both 32 bits): "T2 is after T1 :-
        T2 &- T1 < 2^(W-1)" (VPIM klb_pimos.psl.c, before
        kblt_system_timer; &- unsigned, mod 2^W, W = 32)."""
        return (now - t) & 0xffffffff < 1 << 31

    def alarm_due(self):
        return self.alarm_var is not None and self.reached(self.alarm_time, self.timer() & 0xffffffff)

    def alarm_bind(self, value):
        """The armed alarm's Wakeup bound to value, waking its goals,
        and the alarm cleared.  A Wakeup that someone else has bound is
        refused (VPIM unifies it, i_KlbUnifyBound: not modelled)."""
        v = self.deref(self.alarm_var)
        self.alarm_var = self.alarm_time = None
        if not self.unbound(v):
            raise Unimplemented('the Wakeup of set_timer is bound to %r' % (v,))
        self.unify(v, value)

    def fire_alarm(self):
        """The alarm's time has come: Wakeup = the timer's low 32 bits
        now (VPIM functions/f_event_external_int.psl.c
        f_WakeupGoalByAlarmClock: b_GetCurrentTime, then the unify and
        the wake).  Checked when the next goal is to be taken (run: VPIM
        takes its event flags between reductions; at the goal switch is
        OURS)."""
        self.alarm_bind((INT, self.timer() & 0xffffffff))

    def alarm_skip(self):
        """The machine has nothing to run and the device nothing to
        give (lockstep_shell.py play, the driver's ALARM): the clock is
        moved on to the alarm's time, whole ticks, so the next run's
        first goal switch fires it.  Time passing while the machine
        waits is what a real machine does; that it passes at once is
        OURS (the model's clock counts instructions)."""
        now = self.timer() & 0xffffffff
        self.tick_skip += (self.alarm_time - now) & 0xffffffff

    def i_set_timer(self, pc, x, y, z, c16):
        # set_timer(Time, ^Wakeup), 22:FF r_r (blt.kl1:702-704: input
        # X1, output X2; class pimos).  VPIM's account (klb_pimos.psl.c,
        # the comment before kblt_system_timer, for its three-argument
        # form): an alarm; "if the specified time (in system timer
        # values) has already come, Wakeup is unified at once with the
        # system timer's value", else at the earliest time after; "T2
        # is after T1 :- T2 &- T1 < 2^(W-1)" (&- unsigned, mod 2^W).
        # The clock is self.timer() (2026-11-24; it stood at 0): a time
        # reached gives Wakeup = the timer's low 32 bits, now.  R7L
        # (2026-11-25), as VPIM's kblt_b_set_timer (klb_pimos.psl.c,
        # after the time is read): an alarm already armed is cancelled
        # first, its Wakeup bound to [] ("the cancelling of the earlier
        # request is shown by []"); then a time reached gives Wakeup =
        # now, and one still to come arms the alarm with a fresh
        # variable as Wakeup, bound when the time comes (fire_alarm).
        # Time's high half is not an operand of this two-argument form
        # (VPIM warns "TimeHigh not ZERO ignored")
        def f(t):
            t = self.need_int(t) & 0xffffffff
            if self.alarm_var is not None:
                self.alarm_bind(NIL)
            now = self.timer() & 0xffffffff
            if self.reached(t, now):
                return [(INT, now)]
            self.alarm_var = self.new_var()
            self.alarm_time = t
            return [self.alarm_var]
        self.builtin('set_timer', [x, y], f)

    def i_current_node(self, pc, x, y, z, c16):
        # current_node(^NodeNumber, ^TotalNode), 22:EE r_r: "NodeNumber
        # is unified with the number of node on which this predicate is
        # running and TotalNode is unified with the total number of
        # nodes.  The node number will be a value between 0 and
        # (TotalNode - 1) inclusive" (PIMOS manual, e-builtin.tex
        # current_node).  One node here (ours), so 0 and 1, the values
        # PDSS gives (emulator/blt_system.c blt_b_current_node).  No
        # input: it never waits (no stub), and r[x] is written first.
        self.reg[x] = (INT, 0)
        self.reg[y] = (INT, 1)

    def i_unbound(self, pc, x, y, z, c16):
        # unbound(X, ^Result), 22:EF r_r (assembler/inst_tab.kl1:348):
        # "If X is an undefined variable ... a vector {Id, Address,
        # NewX} is unified with Result ... If X has been instantiated,
        # a vector composed of only one element {NewX}"; it neither
        # suspends nor raises (PIMOS manual, e-builtin.tex 102-109).
        # As VPIM (klb_body_blt_cont.psl.c kblt_b_unbound): X
        # dereferenced; unbound, {the cluster number, the variable's
        # address as an integer, the reference}; else {X}.  The
        # cluster is 0, one here (ours, as current_node).  Not a
        # waiting built-in: its stub is never used
        v = self.deref(self.reg[x])
        if self.unbound(v):
            w, a = self.vnew(3)
            self.mem[a], self.mem[a + 1], self.mem[a + 2] = (INT, 0), (INT, v[1]), v
        else:
            w, a = self.vnew(1)
            self.mem[a] = v
        self.reg[y] = w

    def i_enqueue_goal_with_priority(self, pc, x, y, z, c16):
        # two cells: the priority's register, the label; the arity in
        # the next cell's top byte (assembler/klb_opr.kl1
        # p(r_c16_c8_exe)).  The priority must be an integer and is
        # then DROPPED: there is one ready queue here, where the
        # machine has a goal stack per priority.
        n = self.cells[pc + 1][1] >> 24
        if self.reg[x][0] & ~1 != INT or n > 11:
            raise Unimplemented('enqueue_goal_with_priority %r, %d arguments' % (self.reg[x], n))
        self.record(READY, pc + 2 + sx16(c16), self.argv[1:n + 1])
        return pc + 2

    def i_set_nil(self, pc, x, y, z, c16):
        self.argv[x] = NIL

    def i_set_integer(self, pc, x, y, z, c16):
        self.argv[x] = (INT, sx16(c16) & 0xffffffff)

    def i_collect_vector(self, pc, x, y, z, c16):
        pass        # MRB reclamation of the vector r[x] of c16 cells: no GC here

    def i_collect_list(self, pc, x, y, z, c16):
        pass        # MRB reclamation of the list cell r[x]: no GC here

    def i_put_structured_constant(self, pc, x, y, z, c16):
        # r[x] := the cell at the label, a place in the module's GC
        # area that holds the pointer to a constant built outside the
        # module (TM-662).  A {REFx} there is module#M: in the image a
        # reference to the module table's cell (ipl:boot/0 gives it to
        # predicate_to_code as module#ipl), in a module the IPL loaded
        # a reference to the variable its linker binds to the module
        # object.  The register gets the cell as it stands, and
        # whatever uses a reference dereferences it.
        self.reg[x] = self.mem[self.load + pc + 2 + sx16(c16)]

    def i_set_variable(self, pc, x, y, z, c16):
        var = self.new_var()
        self.argv[x] = var
        self.reg[y] = var

    def i_set_marked_variable(self, pc, x, y, z, c16):
        # as set_variable, the argument and the register with the MRB
        # on (23:15 c8_r, assembler/inst_tab.kl1:18; PDSS emulate.c
        # KL1B_SET_MARKED_VARIABLE: SetAll(arg, REF, undef, MRBON), the
        # register a copy), as put_marked_variable
        var = self.new_var()
        self.argv[x] = (REF + 1, var[1])
        self.reg[y] = (REF + 1, var[1])

    def i_enqueue_goal(self, pc, x, y, z, c16):
        # A goal has 11 argument slots; the compiler packs the
        # arguments from the 11th on into a vector, which is the 11th
        # (library/compiler/pack.kl1: max_goal_slots, "for V2").  The
        # called predicate uses r10, r11, ... with no code to unpack
        # them, so the firmware must spread the vector; where it does
        # is not known.  Here it is spread as the goal is made, and
        # this model's record holds every argument.
        self.spread_args(x, 'enqueue_goal')
        self.record(READY, pc + 2 + sx16(c16), self.argv[1:x + 1])

    def spread_args(self, x, what):
        """Arguments 11 on, packed by the compiler into a vector in the
        11th, spread into the argument registers (enqueue_goal).  A
        vector of 7 or more (more than 16 arguments; 2026-11-24, met in
        pim:go/4 after the login) is spread the same way, from its
        descriptor's first element; its size must be the arguments
        left over."""
        if x > 11:
            v = self.argv[11]
            if self.vsize(v) != x - 10:
                raise Unimplemented('%s %d without its argument vector' % (what, x))
            base = self.vbase(v)
            for i in range(x - 10):
                self.argv[11 + i] = self.taken(base + i)

    def i_execute(self, pc, x, y, z, c16):
        # the same goal goes on as a reduction of the predicate at the label
        self.reductions += 1
        self.chain += 1
        self.alt = None
        self.waiting = []
        return pc + 2 + sx16(c16)

    def i_execute_external(self, pc, x, y, z, c16):
        # The operand locates a four-cell predicate descriptor in the
        # calling module's GC area (TM-662 fig. 2; asm/kbndis.py
        # Image.external): the cache field, {REFx} to a cell holding
        # {REFo} to the called module, the key {atom, arity << 24 |
        # name}, the module's name.  The called module's code area
        # begins with its predicate entry table (TM-662), which in the
        # image is: {INT, mask}, mask + 1 slots indexed by key AND
        # mask, a slot {INT, count << 16 | offset from the slot} to
        # `count` pairs {key, {INT, off}}; the predicate's code is at
        # the off cell + off.  Read from the image and checked on all
        # 59 entries of its 20 modules (docs/pimm_semantics.md).
        #
        # TM-662 (Multi-PSI/V2) says the cache field is filled with the
        # code address on the first call.  What is written there is not
        # known: this model looks the predicate up at every call and
        # writes nothing, and refuses a cache field that is not 0.
        target = self.external(pc, c16, 'execute_external')
        self.reductions += 1
        self.chain += 1
        self.alt = None
        self.waiting = []
        return target

    def i_enqueue_goal_external(self, pc, x, y, z, c16):
        # enqueue_goal with the predicate found as execute_external
        # finds it (the same operand type, assembler/klb_opr.kl1
        # p(c8_c16_ext)).  More than 11 arguments: the vector of those
        # from the 11th on spread as enqueue_goal spreads it
        # (2026-11-24; met in pim:go/4 after the login), before the
        # predicate is looked up
        self.spread_args(x, 'enqueue_goal_external')
        self.record(READY, self.external(pc, c16, 'enqueue_goal_external'), self.argv[1:x + 1])

    def external(self, pc, c16, what):
        """The code address of the predicate whose descriptor is at the
        label."""
        mem, e = self.mem, self.load + pc + 2 + sx16(c16)
        if mem[e] != (INT, 0):
            raise Unimplemented(what + ': a filled cache field')
        via = mem[e + 1]
        # the module field, dereferenced, is the module object {MOD,
        # its descriptor cell}: in the image through the module table's
        # reference to a cell {MOD, the next cell}; in a module the IPL
        # loaded through the variable its linker bound
        # (ipl_link_table:unify_modules/1 as decompiled)
        head = self.deref(via)
        if via[0] & ~1 != REF or head[0] != MOD:
            raise Unimplemented(what + ': the module field')
        target = self.entry(head[1], mem[e + 2])
        if target is None:
            raise Unimplemented(what + ': no such predicate')
        return target - self.load

    def entry(self, a, key):
        """The address of the first instruction of the predicate with
        this key in the module whose descriptor cell is at a ({MOD, a}),
        or None.  After the descriptor: {INT, GC-area size}, then that
        area; the code area begins with the predicate entry table
        (TM-662 fig. 2, read from the image): {INT, mask}, mask + 1
        slots indexed by key AND mask, a slot {INT, count << 16 | off}
        leading to `count` pairs {key, {INT, off}}, the code at the off
        cell + off."""
        mem = self.mem
        table = a + 2 + mem[a + 1][1]
        slot = table + 1 + (key[1] & mem[table][1])
        st, sv = mem[slot]
        if st == INT:
            for k in range(sv >> 16):
                p = slot + (sv & 0xffff) + 2 * k
                if mem[p] == key:
                    return p + 1 + mem[p + 1][1]
        return None

    def i_proceed(self, pc, x, y, z, c16):
        self.chain += 1
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

    def i_b_divide(self, pc, x, y, z, c16):
        # divide(Integer1, Integer2, ^NewInteger), guard and body:
        # "Divides Integer1 by Integer2 and unifies the quotient with
        # NewInteger" (PIMOS manual, e-builtin.tex line 285).  As the
        # guard here (truncated towards zero, PDSS's C /, not
        # established for PIM/m); a zero divisor or the one overflow
        # is the built-in's exception: not modelled
        def f(a, b):
            a, b = self.need_int(a), self.need_int(b)
            if b == 0 or (a == -1 << 31 and b == -1):
                raise Unimplemented('built-in exception: divide %d by %d' % (a, b))
            q = abs(a) // abs(b)
            return [(INT, (-q if (a < 0) != (b < 0) else q) & 0xffffffff)]
        self.builtin('b_divide', [x, y, z], f)

    def i_b_modulo(self, pc, x, y, z, c16):
        # modulo(Integer1, Integer2, ^NewInteger), guard and body:
        # "unifies the remainder with NewInteger" (PIMOS manual,
        # e-builtin.tex line 303).  As the guard here (the remainder
        # has the dividend's sign, PDSS's C %, not established for
        # PIM/m); a zero divisor is the built-in's exception: not
        # modelled
        def f(a, b):
            a, b = self.need_int(a), self.need_int(b)
            if b == 0:
                raise Unimplemented('built-in exception: modulo by 0')
            r = abs(a) % abs(b)
            return [(INT, (-r if a < 0 else r) & 0xffffffff)]
        self.builtin('b_modulo', [x, y, z], f)

    def i_b_and(self, pc, x, y, z, c16):
        self.builtin('b_and', [x, y, z], lambda a, b: [
            (INT, (self.need_int(a) & self.need_int(b)) & 0xffffffff)])

    def i_b_exclusive_or(self, pc, x, y, z, c16):
        self.builtin('b_exclusive_or', [x, y, z], lambda a, b: [
            (INT, (self.need_int(a) ^ self.need_int(b)) & 0xffffffff)])

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
    def i_change_element_size(self, pc, x, y, z, c16):
        # change_element_size(String, NewElemSize, ^NewString): "the
        # smallest index element occupies the highest order bits";
        # widening pads with zero elements to the boundary (manual).
        # To 8, 16 and 32 bits, from any of 1, 8, 16, 32; a change to
        # 1 bit is refused.
        def f(s, new):
            size, elems = self.need_string(s)
            new = self.need_int(new)
            if new not in (8, 16, 32):
                raise Unimplemented('change_element_size to %d' % new)
            if new > size:
                per = new // size
                elems = list(elems) + [0] * (-len(elems) % per)
                out = []
                for i in range(0, len(elems), per):
                    v = 0
                    for e in elems[i:i + per]:
                        v = v << size | e
                    out.append(v)
            else:
                per = size // new
                out = [(e >> new * (per - 1 - k)) & ((1 << new) - 1)
                       for e in elems for k in range(per)]
            return [self.make_string(new, out)]
        self.builtin('change_element_size', [x, y, z], f)

    # The 16 general string operations (manual, table "General String
    # Operations"), by number: the output for inputs S1 and S2.
    STRING_OPS = [
        lambda a, b: 0,          lambda a, b: a & b,     lambda a, b: ~a & b,
        lambda a, b: b,          lambda a, b: a & ~b,    lambda a, b: a,
        lambda a, b: a ^ b,      lambda a, b: a | b,     lambda a, b: ~(a | b),
        lambda a, b: ~(a ^ b),   lambda a, b: ~a,        lambda a, b: ~a | b,
        lambda a, b: ~b,         lambda a, b: a | ~b,    lambda a, b: ~(a & b),
        lambda a, b: -1]

    def i_string_operation(self, pc, x, y, z, c16):
        # string_operation(Op, Vector, ^NewS1, ^NewS2), what the compiler
        # makes of binary_string_operation(Op, Str1, Pos1, Len, Str2,
        # Pos2, NewS1, NewS2): Vector = {Pos1, Str1, Len, Pos2, Str2}
        # (library/compiler/blt.kl1 specialPredicate).  The operation
        # on Len elements of Str1 from Pos1 and of Str2 from Pos2;
        # NewS1 is Str1 with those elements replaced (a copy here),
        # NewS2 is Str2 (manual).  The vector of three is the unary
        # form, unary_string_operation(Op, Str1, Pos1, Len, NewS1):
        # {Pos1, Str1, Len}, NewS2 a new variable of the compiler's
        # (blt.kl1:937-939); VPIM's f_UnaryStringOpe_Sub
        # (functions/f_reduce_string_ope.psl.c:1206-1229) is the
        # binary one with String1 and Position1 in place of the second
        # string's ("Dummy"), so op(e, e) for each element; NewS2 gets
        # Str1 here (OURS: VPIM's unary built-in has no such output).
        # The vector of four (the shifting form) is refused.  An
        # element of the vector that is not yet a value is waited for
        # (the manual says the built-in waits; builtin_utility:
        # append_string/2 gives it a new_string whose length is not
        # yet known): the goal of the stub waits on the first such
        # element, as it would on an operand.
        w4 = self.cells[pc + 1][1] >> 24

        def f(op, v):
            op = self.need_int(op)
            if self.vsize(v) not in (3, 5) or not 0 <= op <= 15:
                raise Unimplemented('string_operation %d on %r' % (op, v))
            e = [self.deref(self.mem[self.vbase(v) + i]) for i in range(self.vsize(v))]
            if len(e) == 3:
                e = e + [e[0], e[1]]
            p1, n, p2 = self.need_int(e[0]), self.need_int(e[2]), self.need_int(e[3])
            size1, s1 = self.need_string(e[1])
            size2, s2 = self.need_string(e[4])
            if size1 != size2 or min(p1, n, p2) < 0 or p1 + n > len(s1) or p2 + n > len(s2):
                raise Unimplemented('built-in exception: string_operation')
            # as the string box does it: the copy, then one word
            # rewritten per element
            fn, mask, per = self.STRING_OPS[op], (1 << size1) - 1, 32 // size1
            new = self.make_string(size1, s1)
            for i in range(n):
                a = new[1] + 1 + (p1 + i) // per
                sh = size1 * (per - 1 - (p1 + i) % per)
                w = self.mem[a][1]
                self.mem[a] = (INT, w & ~(mask << sh) & 0xffffffff
                               | (fn(s1[p1 + i], s2[p2 + i]) & mask) << sh)
            return [new, e[4]]
        self.builtin('string_operation', [x, y, z, w4], f, elements=lambda op, v: (
            self.unbound_elements(v) if self.vsize(v) in (3, 5) else []))
        return pc + 2

    def i_multiply_bignum_word(self, pc, x, y, z, c16):
        # multiply_bignum_by_word(BigX, Y, ^BigZ), 22:B8 r_r_r
        # (assembler/inst_tab.kl1:247; compiler/blt.kl1 the inputs X, Y,
        # the output Z): "The result of multiplying BigX by Y seen as a
        # 32-bit unsigned integer"; a bignum is a 32-bit string read as
        # unsigned, "The MSB is the zeroth element and is zero
        # suppressed" (PIMOS manual e-builtin.tex 703-741).  As VPIM
        # (interpreter/klb_body_blt_bignum.psl.c
        # kblt_b_multiply_bignum_by_word, functions/f_reduce_bignum.psl.c
        # f_Multiply_BIGNUM_By_Word_Sub, structures/str_bignum.psl.c
        # s_Multiply_BIGNUM_By_Word): the empty X is the answer itself;
        # Y = 0 gives the empty string; otherwise the product, one word
        # longer only when the last carry is not 0.  A leading zero word,
        # or BigX not a 32-bit string, or Y not an integer: the
        # built-in's exception (VPIM's too), refused.  The words are
        # written from the least significant up into a new string of
        # zeros (OURS: the Bluespec's order)
        def f(big, w):
            size, elems = self.need_string(big)
            yv = self.need_int(w) & 0xffffffff
            if size != 32 or (elems and elems[0] == 0):
                raise Unimplemented('built-in exception: multiply_bignum_word of %r' % (elems[:2],))
            if not elems:
                return [big]
            v = 0
            for e in elems:
                v = (v << 32) | e
            p = v * yv
            n = 0 if yv == 0 else len(elems) + (1 if p >> (32 * len(elems)) else 0)
            out = self.new_string(n, 32)
            for i in reversed(range(n)):
                self.mem[out[1] + 1 + i] = (INT, (p >> (32 * (n - 1 - i))) & 0xffffffff)
            return [out]
        self.builtin('multiply_bignum_word', [x, y, z], f)

    # The guards bignum_less_than(B1, B2), 23:B6, and
    # bignum_not_less_than(B1, B2), 23:B7, r_r (assembler/inst_tab.kl1:
    # 171-172; compiler/blt.kl1:399-404, both waited for): "32-bit
    # strings ... handled as though they represented unsigned integer
    # values.  The MSB is the zeroth element and is zero suppressed";
    # succeeds if B1 < B2 (B1 >= B2); "Fail: If either ... is anything
    # other than a 32-bit string multiple precision integer" (PIMOS
    # manual, e-builtin.tex 665-697).  As VPIM (klb_guard_blt_bignum.
    # psl.c, str_bignum.psl.c s_IfBignumLessThan, s_CompareBIGNUM): an
    # element size other than 32 or a leading zero word fails either
    # guard; then the longer is the larger, equal lengths compared word
    # by word from element 0, unsigned.  An unbound one is noted and
    # the guard fails (as every two-operand guard here).  2026-11-24,
    # met in pim:go/4 after the login
    def bignum_order(self, x, y):
        a, b = self.g_word(x), self.g_word(y)
        if a is None or b is None:
            return None
        nums = []
        for w in (a, b):
            if w[0] & ~1 != STRG or (self.mem[w[1]][1] >> 24) & 7 != 5:
                return None
            _, e = self.string(w)
            if e and e[0] == 0:
                return None
            nums.append(e)
        ea, eb = nums
        if len(ea) != len(eb):
            return -1 if len(ea) < len(eb) else 1
        return (ea > eb) - (ea < eb)

    def i_bignum_less_than(self, pc, x, y, z, c16):
        o = self.bignum_order(x, y)
        if o is None or o >= 0:
            return self.guard_fail()

    def i_bignum_not_less_than(self, pc, x, y, z, c16):
        o = self.bignum_order(x, y)
        if o is None or o < 0:
            return self.guard_fail()

    def string_order(self, x, y):
        """string_less_than and string_not_less_than's order of the
        strings in r[x], r[y]: -1, 0 or 1; None if the guard fails (an
        unbound argument noted, so the goal suspends, or one that is not
        a string).  The PIMOS manual: "If the bit widths of the elements
        differ, the string with the wider elements is `larger'.
        Otherwise the strings are compared element by element starting
        at the first character. During the comparison, if it is found
        that one string is longer than the other, the longer string is
        `larger'" (e-builtin.tex:813, string comparison; Suspend if
        either is uninstantiated, Fail if either is not a string,
        816-837).  As VPIM computes it (structures/str_string.psl.c
        s_WhichIsLessString, called by f_StringLessThan_Sub,
        functions/f_reduce_string_ope.psl.c:251): the element sizes,
        then the words from the first, compared as unsigned (its
        sign-split compare, :1855-1960), a string whose words run out
        first being the smaller, and two of the same words ordered by
        their element counts.  With the elements packed from the top
        and the pad zero that is the manual's order (R7L, 2026-11-25:
        met in the Listener, the goal typed at its prompt)."""
        a, b = self.g_word(x), self.g_word(y)
        if a is None or b is None:
            return None
        if a[0] & ~1 != STRG or b[0] & ~1 != STRG:
            return None
        da, db = self.mem[a[1]][1], self.mem[b[1]][1]
        ta, tb = (da >> 24) & 7, (db >> 24) & 7
        if ta != tb:
            return -1 if ta < tb else 1
        na, nb = da & 0xffffff, db & 0xffffff
        for i in range(min(na, nb)):
            wa, wb = self.mem[a[1] + 1 + i][1], self.mem[b[1] + 1 + i][1]
            if wa != wb:
                return -1 if wa < wb else 1
        if na != nb:
            return -1 if na < nb else 1
        la, lb = len(self.string(a)[1]), len(self.string(b)[1])
        return (la > lb) - (la < lb)

    def i_string_less_than(self, pc, x, y, z, c16):
        # guard string_less_than(S1, S2), 23:FE r_r (inst_tab.kl1:227;
        # blt.kl1:392-394, both inputs waited for, class user)
        o = self.string_order(x, y)
        if o is None or o >= 0:
            return self.guard_fail()

    def i_string_not_less_than(self, pc, x, y, z, c16):
        # guard string_not_less_than(S1, S2), 23:FF r_r (inst_tab.kl1:229;
        # blt.kl1:395-397)
        o = self.string_order(x, y)
        if o is None or o < 0:
            return self.guard_fail()

    def i_add_bignum(self, pc, x, y, z, c16):
        # add_bignum(BigX, BigY, ^BigZ), 22:B6 r_r_r (assembler/
        # inst_tab.kl1:245; compiler/blt.kl1:718-719 the inputs X, Y,
        # the output Z): "Adds BigX and BigY and unifies the result with
        # BigZ" (manual e-builtin.tex 710-717; bignums as
        # multiply_bignum_word's).  As VPIM (klb_body_blt_bignum.psl.c
        # kblt_b_add_bignum, f_reduce_bignum.psl.c f_Add_BIGNUM_Sub,
        # str_bignum.psl.c s_Add_BIGNUM): either not a 32-bit string, or
        # a leading zero word (X checked first), is the exception,
        # refused; X empty gives Y itself, Y empty X itself; otherwise
        # the sum, as long as the longer, one word longer when the last
        # carry is 1.  The words are written from the least significant
        # up into a new string of zeros, the carry word last (OURS: the
        # Bluespec's order).  2026-11-25, met in the shell's `ts`
        def f(bx, by):
            sx, ex = self.need_string(bx)
            sy, ey = self.need_string(by)
            if sx != 32 or sy != 32 or (ex and ex[0] == 0) or (ey and ey[0] == 0):
                raise Unimplemented('built-in exception: add_bignum of %r, %r' % (ex[:2], ey[:2]))
            if not ex:
                return [by]
            if not ey:
                return [bx]
            vx = vy = 0
            for e in ex:
                vx = (vx << 32) | e
            for e in ey:
                vy = (vy << 32) | e
            nl = max(len(ex), len(ey))
            s = vx + vy
            extra = 1 if s >> (32 * nl) else 0
            out = self.new_string(nl + extra, 32)
            for i in reversed(range(nl)):
                self.mem[out[1] + 1 + i + extra] = (INT, (s >> (32 * (nl - 1 - i))) & 0xffffffff)
            if extra:
                self.mem[out[1] + 1] = (INT, 1)
            return [out]
        self.builtin('add_bignum', [x, y, z], f)

    def i_subtract_bignum(self, pc, x, y, z, c16):
        # subtract_bignum(BigX, BigY, ^Borrow, ^BigZ), 22:B7 r4
        # (assembler/inst_tab.kl1:246; compiler/blt.kl1 inputs X, Y,
        # outputs Borrow, Z): "The difference between BigX and BigY is
        # calculated and the absolute value of that result is unified
        # with BigZ.  If the result was non-negative 0, otherwise 1, is
        # unified with Borrow" (manual e-builtin.tex 720-727; bignums as
        # multiply_bignum_word's).  The edges as VPIM's
        # (klb_body_blt_bignum.psl.c kblt_b_subtract_bignum,
        # f_reduce_bignum.psl.c f_Subtract_BIGNUM_Sub, str_bignum.psl.c
        # s_Subtract_BIGNUM): a leading zero word in either (checked X
        # then Y), or either not a 32-bit string, is the exception,
        # refused; Y empty gives X itself and 0; X empty, Y itself and 1;
        # equal, the empty string and 0; otherwise the difference of the
        # larger and the smaller, its leading zero words dropped.  The
        # kept words are written from the least significant up into a
        # new string of zeros (OURS: the Bluespec's order)
        w4 = self.cells[pc + 1][1] >> 24

        def f(bx, by):
            sx, ex = self.need_string(bx)
            sy, ey = self.need_string(by)
            if sx != 32 or sy != 32 or (ex and ex[0] == 0) or (ey and ey[0] == 0):
                raise Unimplemented('built-in exception: subtract_bignum of %r, %r' % (ex[:2], ey[:2]))
            if not ey:
                return [(INT, 0), bx]
            if not ex:
                return [(INT, 1), by]
            vx = vy = 0
            for e in ex:
                vx = (vx << 32) | e
            for e in ey:
                vy = (vy << 32) | e
            if vx == vy:
                return [(INT, 0), self.new_string(0, 32)]
            borrow = 1 if vx < vy else 0
            n = len(ey) if borrow else len(ex)
            d = abs(vx - vy)
            words = [(d >> (32 * (n - 1 - i))) & 0xffffffff for i in range(n)]
            k = next(i for i, w in enumerate(words) if w)
            out = self.new_string(n - k, 32)
            for i in reversed(range(k, n)):
                self.mem[out[1] + 1 + i - k] = (INT, words[i])
            return [(INT, borrow), out]
        self.builtin('subtract_bignum', [x, y, z, w4], f)
        return pc + 2

    # The double-precision integer built-ins, 22:B2..B5 (assembler/
    # inst_tab.kl1:241-244; directions compiler/blt.kl1:706-717), the
    # operands read as 32-bit unsigned: "the lower 32 bits of their sum
    # is unified with Zl and the carry with Zh"; "Y is subtracted from
    # X ... Borrow"; "the upper 32 bits of the product are unified with
    # Zh and the lower 32 bits with Zl"; the 64-bit Xh:Xl divided by Y,
    # quotient Z and remainder Mod, a quotient wider than 32 bits or Y
    # = 0 the exception (PIMOS manual, e-builtin.tex 615-660, where it
    # is spelt devide_extended).  As VPIM (klb_body_blt_bignum.psl.c
    # kblt_b_*_extended): Z of subtract_extended is X - Y modulo 2^32;
    # divide_extended's exception is Xh >= Y, unsigned.  A non-integer
    # is the exception: refused.  2026-11-24, met in pim:go/4 after
    # the login.  Zh (Borrow, Z) is written first
    def i_add_extended(self, pc, x, y, z, c16):
        w4 = self.cells[pc + 1][1] >> 24

        def f(a, b):
            s = (self.need_int(a) & M32) + (self.need_int(b) & M32)
            return [(INT, s >> 32), (INT, s & M32)]
        self.builtin('add_extended', [x, y, z, w4], f)
        return pc + 2

    def i_subtract_extended(self, pc, x, y, z, c16):
        w4 = self.cells[pc + 1][1] >> 24

        def f(a, b):
            a, b = self.need_int(a) & M32, self.need_int(b) & M32
            return [(INT, 1 if a < b else 0), (INT, (a - b) & M32)]
        self.builtin('subtract_extended', [x, y, z, w4], f)
        return pc + 2

    def i_multiply_extended(self, pc, x, y, z, c16):
        w4 = self.cells[pc + 1][1] >> 24

        def f(a, b):
            p = (self.need_int(a) & M32) * (self.need_int(b) & M32)
            return [(INT, p >> 32), (INT, p & M32)]
        self.builtin('multiply_extended', [x, y, z, w4], f)
        return pc + 2

    def i_divide_extended(self, pc, x, y, z, c16):
        w = self.cells[pc + 1][1]

        def f(h, lo, d):
            h, lo, d = self.need_int(h) & M32, self.need_int(lo) & M32, self.need_int(d) & M32
            if d == 0 or h >= d:
                raise Unimplemented('built-in exception: divide_extended %d:%d by %d' % (h, lo, d))
            q, r = divmod(h << 32 | lo, d)
            return [(INT, q), (INT, r)]
        self.builtin('divide_extended', [x, y, z, w >> 24, w >> 16 & 0xff], f)
        return pc + 2

    def i_new_string(self, pc, x, y, z, c16):
        # new_string(^S, Length, ElementSize): r[z] := string of r[x] zeros
        def f(n, size):
            return [self.new_string(self.need_int(n), self.need_int(size))]
        self.builtin('new_string', [x, y, z], f)

    def i_b_string(self, pc, x, y, z, c16):
        # body string(X, ^Size, ^ElementSize, ^NewString): "The size
        # of string X is unified with Size, the element bit width is
        # unified with ElementSize, and X is unified with NewString"
        # (PIMOS manual, e-builtin.tex line 844; directions also in
        # library/compiler/blt.kl1 active_builtin(string(X1,X2,X3,
        # X4))).  Anything but a string is the built-in's exception:
        # refused
        w4 = self.cells[pc + 1][1] >> 24

        def f(s):
            size, elems = self.need_string(s)
            return [(INT, len(elems)), (INT, size), s]
        self.builtin('b_string', [x, y, z, w4], f)
        return pc + 2

    def i_b_string_element(self, pc, x, y, z, c16):
        # string_element(S, I, ^E, ^S1): r[z] := element, r[w] := the string
        w4 = self.cells[pc + 1][1] >> 24

        def f(s, i):
            self.need_string(s)
            return [self.element(s, self.need_int(i)), s]
        self.builtin('b_string_element', [x, y, z, w4], f)
        return pc + 2

    def i_search_character(self, pc, x, y, z, c16):
        # search_character(String, Start, End, CharacterCode, ^Position,
        # ^NewString), 22:D9 r6 (assembler/inst_tab.kl1:321): the first
        # element equal to CharacterCode from Start to End, End
        # included, searching from the rear when End < Start; -1 if
        # none; NewString is String (PIMOS manual, e-builtin.tex
        # 928-942; VPIM kblt_b_search_character, the same, operands
        # A1..A6 in that order).  Start or End outside the string, or a
        # code too wide for its elements (negative only for 32-bit
        # strings), is the built-in's exception: refused
        w = self.cells[pc + 1][1]
        ops = [x, y, z, w >> 24, w >> 16 & 0xff, w >> 8 & 0xff]

        def f(s, a, b, c):
            size, elems = self.need_string(s)
            a, b, c = self.need_int(a), self.need_int(b), self.need_int(c)
            if not (0 <= a < len(elems) and 0 <= b < len(elems)):
                raise Unimplemented('built-in exception: search_character range')
            if size == 32:
                c &= 0xffffffff
            elif not 0 <= c < 1 << size:
                raise Unimplemented('built-in exception: search_character code')
            step = 1 if b >= a else -1
            for i in range(a, b + step, step):
                if elems[i] == c:
                    return [(INT, i), s]
            return [(INT, 0xffffffff), s]
        self.builtin('search_character', ops, f)
        return pc + 2

    # The merger.  merge(In, ^Out) "creates a built-in constant time
    # merger" (manual); the compiler makes it merge(Out, ^In): the first
    # operand is the output stream as given, the second receives the
    # input (library/compiler/blt.kl1 active_builtin(merge(X1,X2))).
    # On the machine the input is a cell of its own tag (MGHOK) pointing
    # at a merger record {output variable}{number of inputs} (TR-466
    # 3.3), and the merger acts when that cell is unified.  HERE a
    # merger input is a GOAL waiting on the input stream, with the
    # record {output}{count} and the first input variable in three
    # cells; its code is the stub merge_in (asm/pimm_stubs.py), which
    # is not a PIM/m instruction.  So the output appears after a goal
    # switch, not at the unification; a woken merge_in is taken before
    # any other goal (the merger's list, Machine.ready and pick).  A vector on the input adds as
    # many inputs as it has elements (i_merge_in); anything but a
    # list, [] or a vector, or a
    # variable is the machine's illegal_merger_input exception:
    # refused.  The output operand must be an unbound variable (it is
    # a fresh put_variable at all six sites in the image).
    def i_merge(self, pc, x, y, z, c16):
        out = self.deref(self.reg[x])
        if not self.unbound(out):
            raise Unimplemented('merge onto %r' % (out,))
        rec = self.alloc(3)
        self.mem[rec] = out
        self.mem[rec + 1] = (INT, 1)
        self.mem[rec + 2] = (UNDF, 0)
        self.reg[y] = (REF, rec + 2)
        self.reg[254] = (INT, rec)
        self.merge_wait(self.reg[y], self.reg[254], rec + 2)

    def merge_wait(self, stream, rec, var):
        """A goal of merge_in(stream, rec) waiting on the cell var."""
        self.nsusp += 1
        g = self.alloc(G_ARGS + 2)
        self.mem[g + G_LINK] = (INT, 0)
        self.mem[g + G_STATUS] = self.gstatus(SUSPENDED)
        self.mem[g + G_CODE] = (INT, self.load + self.stubs['$merge_in']['addr'])
        self.mem[g + G_ARGN] = (INT, 2)
        self.mem[g + G_ARGS] = stream
        self.mem[g + G_ARGS + 1] = rec
        self.counted()
        self.hook(g, var)

    def i_merge_in(self, pc, x, y, z, c16):
        if pc != self.stubs['$merge_in']['addr']:
            raise Unimplemented('merge_in at %d' % pc)
        w = self.deref(self.reg[x])
        rec = self.reg[y][1]
        if self.unbound(w):
            self.merge_wait(self.reg[x], self.reg[y], w[1])
        elif w[0] & ~1 == LIST:
            out = self.mem[rec]
            c = self.alloc(2)
            self.mem[c] = self.taken(w[1])
            self.mem[c + 1] = (UNDF, 0)
            self.mem[rec] = (REF, c + 1)
            self.reg[x] = self.taken(w[1] + 1)
            self.unify(out, (LIST + 1, c))
            return pc                         # go on with the cdr
        elif (w[0] & ~1, w[1]) == NIL:
            n = self.mem[rec + 1][1] - 1
            self.mem[rec + 1] = (INT, n)
            if n == 0:
                self.unify(self.mem[rec], NIL)
        elif self.vsize(w) is not None:
            # "When a vector is unified to an MHV, as many input
            # streams (MHVs) as the arity of the vector are added to
            # the merger process and each element of the vector is
            # unified to each new input stream" (TR-466 3.3; TR-483
            # 2.7.2: merge({}, O) :- O = [], merge({I}, O) :-
            # merge(I, O), merge({I1,I2}, O) :- merge(I1, I2, O);
            # both as quoted in docs/literature_gaps.md, lines 1571
            # and 1581: the reports were not opened again for this).
            # Here: this input ends and each element gets a goal of
            # merge_in, ready, the last element's first (it suspends
            # itself if its stream is unbound).  Each goal is made
            # through the argument registers, a1 the element, a2 the
            # record, as enqueue_goal makes one, so that the Bluespec's
            # goal box makes it the same way (2026-11-23: the records
            # were written straight from cells before, and the core
            # refused the case).  A vector of seven or more
            # (2026-11-25, met by the compiler on the primer's sample1,
            # two vectors of 9): the same, its size and elements from
            # its descriptor (vsize, vbase).  No source bounds the
            # arity: TR-466 3.3 says "as many input streams as the
            # arity of the vector"; KLIC's merger takes a vector of any
            # size the same way (runtime/gmerge.c:81-104: the count
            # goes up by size - 1, then each element 0..size-1 is
            # unified with a new input); VPIM's merger takes a long
            # vector too (functions/f_reduce_merger_unify.psl.c
            # f_Unify_MGHOK_VECT_Sub, 1487ff, a WARNING for one at
            # :1499-1500; :210-213 the dispatch).  The order of the goals is
            # this model's, as for a short vector.
            n = self.vsize(w)
            base = self.vbase(w)
            count = self.mem[rec + 1][1] - 1 + n
            self.mem[rec + 1] = (INT, count)
            if count == 0:
                self.unify(self.mem[rec], NIL)
            for i in range(n):
                self.argv[1] = self.taken(base + i)
                self.argv[2] = self.reg[y]
                self.record(READY, pc, self.argv[1:3])
        else:
            raise Unimplemented('merger input %r' % (w,))

    def i_unify_step(self, pc, x, y, z, c16):
        """Ours, only at its stub: element r[z] of the structures r[x]
        and r[y] is unified, r[z] goes up by one and the instruction is
        taken again; at the size it is passed.  An element is taken
        with its MRB on if its structure's is (PDSS
        dc_unify_vector_vector2: "Dereference(vp1+i); if(mrb1 ==
        MRBON) SetMrbof(vp1+i, MRBON)"), else as it is.  PDSS does all
        the elements in one reduction and frees a structure whose MRB
        is off; here nothing is freed."""
        if pc != self.stubs['$unify_step']['addr']:
            raise Unimplemented('unify_step at %d' % pc)
        a, b, i = self.reg[x], self.reg[y], self.reg[z][1]
        if a[0] & ~1 == VECT0 + 14:
            # vectors of seven or more: the sizes, compared at every
            # step, and the elements from the descriptors
            n = self.vsize(a)
            if self.vsize(b) != n:
                raise Fail('unify of vectors of %d and %d' % (n, self.vsize(b)))
            ba, bb = self.vbase(a), self.vbase(b)
        else:
            n = 2 if a[0] & ~1 == LIST else (a[0] & ~1) - VECT0 >> 1
            ba, bb = a[1], b[1]
        if i == n:
            return None
        ea = self.taken(ba + i, single=not a[0] & 1)
        eb = self.taken(bb + i, single=not b[0] & 1)
        self.reg[z] = (INT, i + 1)
        self.unify(ea, eb)
        return pc

    def i_new_instruction(self, pc, x, y, z, c16):
        # new_instruction(Tag, Value, ^Cell): the cell with that tag
        # and value, tag_and_value's inverse (library/unloader
        # decoder.kl1 decode_atomic, encoder.kl1 decode_pred_hash_key).
        # Tags of references and pointers are refused: only atomic
        # cells (0..3) and tags from 20h (instructions, descriptors)
        def f(t, v):
            t = self.need_int(t)
            if not (0 <= t <= 3 or 0x20 <= t <= 0xff):
                raise Unimplemented('new_instruction with tag %x' % t)
            return [(t, self.need_int(v) & 0xffffffff)]
        self.builtin('new_instruction', [x, y, z], f)

    def i_new_module(self, pc, x, y, z, c16):
        # new_module(Vector, ^Module): the vector becomes a module
        # object.  library/loader/loader.kl1: "First Element is for
        # CDESC created by new_module", and its caller puts
        # 06000000h \/ (size - 1) there.  The result has the shape of
        # every module of the IPL image: {MOD, a} -> {CDESC, 06 << 24 |
        # n}, then the n other elements as they are (module_element
        # counts from the cell after the descriptor,
        # library/unloader/encoder.kl1).  Whether the machine converts
        # in place is not known; this model copies, as everywhere.
        # An element may be a reference to a variable: the loader puts
        # one where another module will be (loader.kl1 encode_gc_area,
        # "set_vector_element(ModVec1,P1,_,Module,ModVec2)"), which is
        # the {REF} of TM-662's predicate descriptor; it is copied as
        # it is.  Refused: an element 0 that is not that integer, and
        # an unbound cell in the vector itself.
        def f(v):
            n = self.vsize(v)
            if not n:
                raise Unimplemented('new_module of %r' % (v,))
            base = self.vbase(v)
            e0 = self.mem[base]
            if e0[0] & ~1 != INT or e0[1] != (6 << 24 | n - 1):
                raise Unimplemented('new_module: element 0 is %r' % (e0,))
            a = self.alloc(n)
            self.mem[a] = (CDESC, e0[1])
            for i in range(1, n):
                c = self.mem[base + i]
                if c[0] & ~1 in (UNDF, HOOK):
                    raise Unimplemented('new_module: element %d is unbound in place' % i)
                self.mem[a + i] = c
            return [(MOD, a)]
        self.builtin('new_module', [x, y], f)

    def i_predicate_to_code(self, pc, x, y, z, c16):
        # predicate_to_code(Module, Name, Arity, ^Code), 22:F3, r4.
        # "Unifies a code denoting module Module, predicate name Name
        # and argument count Arity with Code.  If a corresponding
        # predicate is absent in the module ... unifies a 3-element
        # vector {Module, Name, Arity}" (PIMOS manual, e-builtin.tex
        # predicate_to_code; PDSS takes an atom for the module and
        # gives [], which is not this machine).  Module is a module
        # object; anything else is the built-in's exception: refused.
        # The predicate is found in the module's entry table as an
        # external call finds it; its key is arity << 24 | (atom +
        # arity) (library/kbn/kbnatom.kl1; an ATOM cell, as the table
        # holds it).  The code object is {COD, the address of the
        # predicate's first instruction}.  That target is ASSUMED for
        # PIM/m: it agrees with code_to_predicate's "contents of <Code
        # address - 3>" (manual) and with the image header's start
        # address, two cells after a predicate head.
        w4 = self.cells[pc + 1][1] >> 24

        def f(mod, name, arity):
            n = self.need_int(arity)
            if mod[0] != MOD or name[0] & ~1 != ATOM or not 0 <= n <= 255:
                raise Unimplemented('built-in exception: predicate_to_code(%r, %r, %r)'
                                    % (mod, name, arity))
            key = (ATOM, n << 24 | (name[1] + n) & 0xffffff)
            code = self.entry(mod[1], key)
            if code is not None:
                return [(COD, code)]
            w, a = self.vnew(3)
            self.mem[a], self.mem[a + 1], self.mem[a + 2] = mod, name, arity
            return [w]
        self.builtin('predicate_to_code', [x, y, z, w4], f)
        return pc + 2

    def i_apply(self, pc, x, y, z, c16):
        # apply(Code, Args), 22:F1.  "Calls a predicate corresponding
        # to Code with argument environment Args.  Suspend: Code or
        # Args uninstantiated.  Exception: Code other than a code, Args
        # other than a vector, the number of arguments to Code and the
        # number of elements in Args do not agree" (PIMOS manual,
        # e-builtin.tex apply).  A new ready goal of the code, as PDSS
        # makes one (emulator/blt_system.c blt_b_apply: a goal record,
        # each element dereferenced and its MRB set if the vector's
        # is, enqueue).  The arguments go through the argument
        # registers, as for enqueue_goal.  The exceptions are refused;
        # so is a vector of seven or more (its size is in memory).  The
        # empty vector makes a goal of no argument (2026-11-24: met in
        # pim:go/4 with the device).
        # A vector of 7 to 16 elements (2026-11-24, met in pim:go/4
        # after the login): its elements from the descriptor's first,
        # every one into an argument register, as enqueue_goal's
        # spread leaves a goal of more than 11 (OURS, that limit's)
        def f(code, args):
            n = self.vsize(args)
            head = self.mem[code[1] - 2] if code[0] == COD else None
            if head is None or head[0] != PREDH or n is None or n > 16 or n != head[1] >> 24:
                raise Unimplemented('built-in exception: apply(%r, %r)' % (code, args))
            base = self.vbase(args) if n else 0
            for i in range(n):
                self.argv[i + 1] = self.taken(base + i, single=not args[0] & 1)
            self.record(READY, code[1] - self.load, self.argv[1:n + 1])
            return []
        self.builtin('apply', [x, y], f)

    def i_create_shoen(self, pc, x, y, z, c16):
        # create_shoen(MinPrio, MaxPrio, ExcepMask, Code, Argv, ^Report,
        # ^Shoen), 22:E0, r7: two cells, the last four registers in the
        # second (PIMOS library/assembler/inst_tab.kl1:332-362,
        # klb_opr.kl1:144-154; directions library/compiler/blt.kl1:
        # 567-569; meanings kernel/builtin/shoen.kl1:40-48).  All that
        # is PIM/m-sourced, and so is that the outputs may be the input
        # registers: the image's shoen:execute/4 (cell 15553) has
        # 22:e0040506, 00:00010001, Code and Report both r0, Argv and
        # Shoen both r1, so every input is read before an output is
        # written.  The PIMOS manual does not document the built-in.
        #
        # What it DOES is not PIM/m-sourced:
        #  - MinPrio, MaxPrio and ExcepMask are waited for, must be
        #    integers (or two 2-vectors, shoen:execute1/7's, below) and
        #    are then DROPPED: no priorities and no exceptions here
        #    (OURS, as enqueue_goal_with_priority drops its priority);
        #  - a shoen record (OURS, asm/pimm_layout.py): dormant, count
        #    1, its parent the current shoen, which counts it as one
        #    (carried over from PDSS, emulator/shoen.c:123-178: "prec->
        #    number_of_children = 1; ... prec->parent = parent;
        #    number_of_children++");
        #  - Report is a fresh variable, the handle {SHREC, the record}
        #    (OURS);
        #  - ONE goal, apply(Code, Argv), of the new shoen, its code
        #    apply's stub (PDSS: "grec->code = (OBJ *)dc_apply;
        #    grec->argn = 2"), its arguments through the argument
        #    registers.  It is PARKED: suspended, on no queue and on no
        #    variable, until start_shoen (PDSS hooks the goals of a
        #    shoen that is not ready on the shoen, goal.c:310-334; the
        #    PIMOS manual has a shoen dormant until `start`,
        #    e-shoen.tex:117-262).  Code and Argv are not waited for:
        #    apply waits itself.
        # No resource is counted and resource_low (6) is NEVER reported
        # (OURS.  VPIM reports it for a shoen with no limit left, and
        # the callers of execute/4 grant resource only when they get
        # it, so the machine probably did report it).
        r7 = self.cells[pc + 1][1]
        regs = [x, y, z, r7 >> 24, r7 >> 16 & 255, r7 >> 8 & 255, r7 & 255]

        # The distributed form (2026-11-24, met in pim:go/4 after the
        # login): shoen:execute1/7 passes {MinPrio, MaxPrio} and
        # {MinNode, NumNode} in place of MinPrio and MaxPrio
        # (kernel/builtin/shoen.kl1 execute/9, execute1/7).  Two
        # 2-vectors there are accepted and dropped as the integers are,
        # their elements not read (OURS: one node, no priorities)
        def f(lo, hi, mask, _code, _argv):
            two = self.vsize(lo) == 2 and self.vsize(hi) == 2
            for w in (mask,) if two else (lo, hi, mask):
                if w[0] & ~1 != INT:
                    raise Unimplemented('create_shoen(%r, %r, %r, ..)' % (lo, hi, mask))
            self.argv[1] = self.reg[regs[3]]          # as they are
            self.argv[2] = self.reg[regs[4]]
            sh = self.alloc(SH_SIZE)
            self.mem[sh + SH_COUNT] = (INT, 1)
            self.mem[sh + SH_STATUS] = (INT, DORMANT)
            self.mem[sh + SH_PARENT] = (INT, self.shoen)
            var = self.new_var()
            self.mem[sh + SH_REPORT] = var
            g = self.record(SUSPENDED, self.stubs['apply']['addr'], self.argv[1:3], shoen=sh)
            self.mem[sh + SH_GOAL] = (INT, g)
            self.mem[sh + SH_REDUCTIONS] = (INT, 0)
            self.mem[sh + SH_REMOVE] = (INT, 0)
            self.mem[sh + SH_MASK] = (INT, mask[1])   # stage 3: kept, for exceptions
            self.mem[sh + SH_RSC_HI] = (INT, 0)       # R7L: no resource yet,
            self.mem[sh + SH_RSC_LO] = (INT, 0)       # reports allowed
            self.mem[sh + SH_RSC_FLAGS] = (INT, 0)
            self.counted()                # the child is one of its parent's
            self.nsusp += 1
            return [var, (SHREC, sh)]
        self.builtin('create_shoen', regs, f, nowait=(3, 4))
        return pc + 2

    def i_start_shoen(self, pc, x, y, z, c16):
        # start_shoen(Shoen, ^NewShoen), 22:E1, r_r (inst_tab.kl1,
        # blt.kl1:537-601: PIM/m-sourced; the image's control/2, cell
        # 15755, has start_shoen 1,1).  A dormant shoen: 8 (started) is
        # reported FIRST, then the status changes (VPIM functions/
        # f_shoen_control.psl.c:324-330 reports before it changes the
        # state: carried over, not PIM/m-sourced), and the parked goal
        # goes on the ready queue as a woken goal does.  NewShoen is
        # the same handle (OURS).  A shoen that is not dormant
        # (started twice, or terminated) is refused, as is anything
        # but a handle.
        #
        # Stage 3: a STOPPED shoen is started again the same way ("This
        # message is also used to restart the execution suspended by the
        # stop message", manual e-shoen.tex:139: PIM/m-sourced): every
        # goal on its parked list (asm/pimm_layout.py) is released, in
        # the list's order, then the list is emptied (SH_GOAL := 0).
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('start_shoen(%r)' % (h,))
            sh = h[1]
            if self.mem[sh + SH_STATUS][1] not in (DORMANT, STOPPED):
                raise Unimplemented('start_shoen of a shoen that is not dormant or stopped')
            self.report(sh, REPORT_STARTED)
            self.mem[sh + SH_STATUS] = (INT, STARTED)
            self.release(sh)
            return [h]
        self.builtin('start_shoen', [x, y], f)

    def release(self, sh):
        """Every goal on shoen sh's parked list goes on the ready queue
        as a woken goal does, in the list's order, then the list is
        emptied (SH_GOAL := 0): start_shoen's, and add_shoen_resource's
        (R7L)."""
        g = self.mem[sh + SH_GOAL][1]
        while g:
            nxt = self.mem[g + G_LINK][1]
            st = self.mem[g + G_STATUS][1]
            self.event('W %d' % (g - self.load))
            self.mem[g + G_STATUS] = (INT, st & ~3 | READY)
            self.mem[g + G_LINK] = (INT, self.rq)
            self.rq = g
            self.nsusp -= 1
            g = nxt
        self.mem[sh + SH_GOAL] = (INT, 0)

    def i_stop_shoen(self, pc, x, y, z, c16):
        # stop_shoen(Shoen, ^NewShoen), 22:E2, r_r (inst_tab.kl1:334,
        # blt.kl1: PIM/m-sourced; the image's control/2 for `stop`).
        # "Suspends a shoen execution", acknowledged by `stopped`, 11
        # (manual e-shoen.tex:143-150, 254-262; pimos.vmac).  11 is
        # reported first, then a STARTED shoen becomes STOPPED; on any
        # other (dormant, stopped, terminated) only 11 (VPIM
        # f_shoen_control.psl.c:392-450 f_StopShoen_Sub, carried over;
        # VPIM's dormant shoen is itself "stopped by control").  A
        # stopped shoen's goals are parked as they are taken from the
        # ready queue (taken_check); the goal running is not stopped
        # (the manual's caution: "even if a stopped message has been
        # reported, it cannot be inferred that the shoen internal
        # processing has already been suspended").  NewShoen is the
        # same handle (OURS).  Refused: anything but a handle; a removed
        # shoen (its report stream is closed).
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('stop_shoen(%r)' % (h,))
            sh = h[1]
            self.report(sh, REPORT_STOPPED)
            if self.mem[sh + SH_STATUS][1] == STARTED:
                self.mem[sh + SH_STATUS] = (INT, STOPPED)
            return [h]
        self.builtin('stop_shoen', [x, y], f)

    def i_abort_shoen(self, pc, x, y, z, c16):
        # abort_shoen(Shoen, ^NewShoen), 22:E3, r_r (inst_tab.kl1:335,
        # blt.kl1: PIM/m-sourced; the image's control/2 for `abort`).
        # "Aborts a shoen execution ... execution cannot be restarted
        # later", acknowledged by `aborted`, 1; `terminated` comes after
        # it, and whether `aborted` is ahead of it tells a forced end
        # from a normal one (manual e-shoen.tex:152-158, 212-218:
        # PIM/m-sourced).  1 is reported first (VPIM f_AbortShoen_Sub,
        # carried over); then a shoen not yet terminated terminates AT
        # ONCE (OURS: VPIM tells its foster parents, which end their
        # goals and then report termination; PDSS frees the parked
        # goals, aborts the sons and takes the shoen off its parent's
        # count, shoen.c:237-267, and reports no termination): status
        # TERMINATED, 12, the removal if one is pending, its reductions
        # to its parent and one off the parent's count, as at an
        # ordinary end.  Its goals, and those of the shoen inside it,
        # are discarded as they are taken from the ready queue
        # (taken_check: PDSS goal.c:328-331); those waiting on a
        # variable or parked stay in memory, never run.  The shoen
        # inside it report nothing (OURS; PDSS aborts each with
        # `aborted`): their report/2 and monitors are goals of the
        # aborted shoen.  On a terminated shoen only 1 (VPIM: "abort to
        # terminated shoen" is no error).  NewShoen is the same handle
        # (OURS).  Refused: anything but a handle; a removed shoen; a
        # shoen at or above the goal's own (its end would count in a
        # terminated shoen: not modelled).
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('abort_shoen(%r)' % (h,))
            sh = h[1]
            if sh in self.chain_of(self.shoen):
                raise Unimplemented('abort_shoen of the shoen the goal is in')
            st = self.mem[sh + SH_STATUS][1]
            self.report(sh, REPORT_ABORTED)
            if st != TERMINATED:
                red = self.mem[sh + SH_REDUCTIONS][1]
                self.terminate(sh)
                self.ended(self.mem[sh + SH_PARENT][1], red)
            return [h]
        self.builtin('abort_shoen', [x, y], f)

    def i_raise(self, pc, x, y, z, c16):
        # raise(Tag, Info, Data), 22:F2, r_r_r, three inputs (inst_tab.kl1
        # :351, blt.kl1:537: PIM/m-sourced; shoen:raise/3 calls it once
        # Info is ground, the image's control/2 directly).  A `raised`
        # exception, number 16, its tag the Tag given, Info {Pe, Info,
        # Data} (excpt_tbl.kl1 "FIRMWARE FORMAT" 16; the manual,
        # e-shoen.tex:738-746, 766-777), reported as exception() says;
        # the goal goes on (raise is a body built-in), and the goal
        # apply(NewCode, NewArgv) is the one "to be executed in place of
        # raise" (manual).  Only Tag is waited for, Info and Data are
        # taken as the registers hold them (VPIM kblt_b_raise:
        # f_ActiveDeref of Tag only; carried over).  Refused: a Tag
        # that is not an integer (VPIM: illegal_input), an exception no
        # shoen accepts (outside every shoen too).
        def f(tag, _info, _data):
            if tag[0] & ~1 != INT:
                raise Unimplemented('raise with tag %r' % (tag,))
            self.exception(EXC_RAISED, tag[1], self.reg[y], self.reg[z])
            return []
        self.builtin('raise', [x, y, z], f, nowait=(1, 2))

    def i_current_processor(self, pc, x, y, z, c16):
        # current_processor(^Current, ^X, ^Y), 22:EB r_r_r, three outputs
        # (inst_tab.kl1:343, blt.kl1:552: PIM/m-sourced).  Not in the
        # PIMOS manual; PIMOS's macros use it as current_processor(
        # Cluster, X, Y) with X * Y the number of processors (pimos.vmac
        # :381, shell/main/comexe.kl1:220); the image's exception_table:
        # translate/4 subtracts Current from the exception's Pe.  One
        # processor here: 0, 1, 1, PDSS's values (emulator/blt_system.c
        # blt_b_current_processor: carried over).  No input: never
        # waits; r[x], r[y], r[z] written in that order.
        self.reg[x] = (INT, 0)
        self.reg[y] = (INT, 1)
        self.reg[z] = (INT, 1)

    def i_shoen_statistics(self, pc, x, y, z, c16):
        # shoen_statistics(Shoen, ^NewShoen), 22:E6, r_r (inst_tab.kl1,
        # blt.kl1:537-601: PIM/m-sourced; the image's control/2 calls it
        # for `statistics`).  10 (statistics_started) is reported, then
        # {9, H, L} (statistics(H, L)): H and L the high and low 32 bits
        # of twice the shoen's reductions (PIM/m-sourced: the PIMOS
        # manual, e-shoen.tex:234, "twice of the number of reductions
        # ... including the descendent shoens"; the count is
        # SH_REDUCTIONS, see end_reduction).  10 first and {9, ..} at
        # once on a terminated shoen is VPIM's (f_shoen_control.psl.c:
        # 691-727); on a shoen not terminated VPIM asks its processors
        # and reports later, this model reports the count as it stands
        # (the goal in hand's reductions not yet in it), which the
        # manual allows ("should not exceed the actual consumption"):
        # OURS.  NewShoen is the same handle (OURS).
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('shoen_statistics(%r)' % (h,))
            sh = h[1]
            self.report(sh, REPORT_STATISTICS_STARTED)
            red = self.mem[sh + SH_REDUCTIONS][1]
            self.report3(sh, REPORT_STATISTICS, red >> 31, red << 1)
            return [h]
        self.builtin('shoen_statistics', [x, y], f)

    def i_add_shoen_resource(self, pc, x, y, z, c16):
        # add_shoen_resource(Shoen, High, Low, ^NewShoen), 22:E5 r4
        # (inst_tab.kl1:337; blt.kl1 active_builtin(add_shoen_resource(
        # X1,X2,X3,X4)), class pimos): the shoen's add_resource(H, L),
        # "A value of which the upper 32 bits are expressed in Amount_h
        # and the lower 32 bits ... in Amount_l is added to the upper
        # bound value of the resource consumption amount", acknowledged
        # by resource_added (manual e-shoen.tex:166-172, 254-262), 5
        # (pimos.vmac).  VPIM (f_shoen_control.psl.c
        # f_AddShoenResource_Sub) reports 5 first, then adds, and
        # reports return_resource only when the bound passes 2^63;
        # NewShoen is the handle.  R7L (2026-11-25): the amount, High
        # and Low as two 32-bit halves, is added to the resource left
        # (asm/pimm_layout.py SH_RSC_HI, SH_RSC_LO) after the report
        # (VPIM's order); a sum of 2^63 or more is refused (VPIM and the
        # manual, e-shoen.tex:246, then report return_resource: not
        # modelled).  If the shoen is STARTED and now has resource left,
        # the goals parked on it are released, in the list's order, as
        # start_shoen releases them ("If the upper bound value is
        # increased when execution is suspended due to trespassing the
        # upper bound, shoen execution resumes", e-shoen.tex:31); a
        # dormant shoen's parked list is its first goal, kept for
        # start_shoen, and a stopped one's waits for start_shoen too.
        # Refused: anything but a handle, High or Low not an integer
        # (the exception); a closed report stream
        w4 = self.cells[pc + 1][1] >> 24

        def f(h, hi, lo):
            if h[0] != SHREC:
                raise Unimplemented('add_shoen_resource(%r)' % (h,))
            hi = self.need_int(hi) & M32
            lo = self.need_int(lo) & M32
            sh = h[1]
            self.report(sh, REPORT_RESOURCE_ADDED)
            left = self.rsc_left(sh) + (hi << 32 | lo)
            if left >= 1 << 63:
                raise Unimplemented('add_shoen_resource past 2^63 (return_resource)')
            self.set_rsc_left(sh, left)
            if left > 0 and self.mem[sh + SH_STATUS][1] == STARTED:
                self.release(sh)
            return [h]
        self.builtin('add_shoen_resource', [x, y, z, w4], f)
        return pc + 2

    def i_allow_shoen_resource_report(self, pc, x, y, z, c16):
        # allow_shoen_resource_report(Shoen, ^NewShoen), 22:E7 r_r
        # (inst_tab.kl1:339; blt.kl1:595 In [X1], Out [X2], class
        # pimos): the shoen's allow_resource_report (shoen.kl1:131),
        # "Allows a report to be sent as the amount of consumed
        # resource has nearly reached its upper bound", acknowledged
        # by resource_report_allowed (manual e-shoen.tex:174-180,
        # 254-262), 7 (pimos.vmac).  VPIM (f_shoen_control.psl.c
        # f_AllowShoenResourceReport_Sub) reports it, then clears the
        # shoen's report-disallowed flag (R7L, 2026-11-25:
        # asm/pimm_layout.py SH_RSC_FLAGS; until then no flag was
        # kept); NewShoen is the handle.  VPIM then supplies any foster
        # parent still asking; here a goal parked on an exhausted shoen
        # stays parked until add_shoen_resource (OURS).  Refused:
        # anything but a handle (the exception); a closed report
        # stream.  2026-11-24, met in pim:go/4 after the login
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('allow_shoen_resource_report(%r)' % (h,))
            sh = h[1]
            self.report(sh, REPORT_RESOURCE_REPORT_ALLOWED)
            self.mem[sh + SH_RSC_FLAGS] = (INT, self.mem[sh + SH_RSC_FLAGS][1] & ~RSC_REPORT_DISALLOWED)
            return [h]
        self.builtin('allow_shoen_resource_report', [x, y], f)

    def i_remove_shoen(self, pc, x, y, z, c16):
        # remove_shoen(Shoen), 22:E4, r (inst_tab.kl1, blt.kl1: PIM/m-
        # sourced; the image's control/2 calls it when the control
        # stream is []).  A terminated shoen is removed at once (remove:
        # 14, the close).  One not yet terminated (dormant or started)
        # is marked, SH_REMOVE = 1, and removed when it terminates
        # (end_reduction): VPIM's (f_shoen_control.psl.c:547-575 sets
        # its no_more_external_event flag; f_shoen_with_fp.psl.c:69-71
        # then reports terminated, return_resource and closes), not
        # PIM/m-sourced.  A shoen removed already is refused.
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('remove_shoen(%r)' % (h,))
            sh = h[1]
            st = self.mem[sh + SH_STATUS][1]
            if st == REMOVED:
                raise Unimplemented('remove_shoen of a shoen removed already')
            if st == TERMINATED:
                self.remove(sh)
            else:
                self.mem[sh + SH_REMOVE] = (INT, 1)
            return []
        self.builtin('remove_shoen', [x], f)

    def i_module(self, pc, x, y, z, c16):
        # guard module(X, ^Size), 23:FB r_r (assembler/inst_tab.kl1:
        # 214): "Unifies the size of the module X with Size.  Suspend:
        # X uninstantiated.  Fail: X anything other than a module"
        # (PIMOS manual, e-builtin.tex 86-92).  Size is the count in
        # the module's descriptor, the elements after it: the
        # unloader writes it as the module's length and reads
        # module_element 0 .. Length - 1 (library/unloader/
        # encoder.kl1 encode_module/7), the loader puts 06000000h \/
        # (vector size - 1) there (i_new_module).  VPIM reads its own
        # header's size word (kblt_module).  2026-11-24, met in
        # pim:go/4 after the login
        w = self.g_word(x)
        if w is None or w[0] != MOD:
            return self.guard_fail()
        d = self.mem[w[1]]
        if d[0] != CDESC:
            raise Unimplemented('module: no descriptor at %x' % w[1])
        self.reg[y] = (INT, d[1] & 0xffffff)

    def i_module_element(self, pc, x, y, z, c16):
        # module_element(Module, Position, ^Element), 22:F7 r_r_r
        # (assembler/inst_tab.kl1:356; compiler/blt.kl1:617-618 the
        # inputs X1, X2, the output X3).  Element i is the cell i + 1
        # after the module's descriptor, 0 <= i < the descriptor's
        # count: the unloader writes {CDESC, 06 << 24 | Length} and
        # then module_element 0 (the GC size) and on
        # (library/kbn/kbn.kl1 encode_module:140-158), as i_module
        # reads the count.  VPIM (interpreter/klb_body_blt_cont.psl.c
        # kblt_b_module_element) reads the element at the module
        # pointer plus Position under its own header, with Position
        # checked against the module's size; a Position out of range,
        # or a Module not a module, is the built-in's exception there:
        # refused here.  2026-11-25, met compiling the primer's
        # sample1 (module_utility, ground_module/3)
        def f(md, i):
            i = self.need_int(i)
            if md[0] != MOD:
                raise Unimplemented('built-in exception: module_element of %r' % (md,))
            d = self.mem[md[1]]
            if d[0] != CDESC:
                raise Unimplemented('module_element: no descriptor at %x' % md[1])
            if not 0 <= i < d[1] & 0xffffff:
                raise Unimplemented('built-in exception: module_element %d' % i)
            return [self.mem[md[1] + 1 + i]]
        self.builtin('module_element', [x, y, z], f)

    def i_code(self, pc, x, y, z, c16):
        # guard code(X, ^Arity, ^Module, ^Position), 23:FA, r4.
        # "Unifies the number of arguments of the code X with Arity,
        # the module to which the code belongs with Module and the
        # position from the beginning of the module with Position.
        # Suspend: X uninstantiated.  Fail: X anything other than a
        # code" (PIMOS manual, e-builtin.tex code).  The predicate head
        # {PREDH, arity << 24 | offset} is two cells before the code
        # and its offset leads back to the module's descriptor cell;
        # Position is counted from that cell (library/kbn/kbnlink.kl1:
        # the start address is the module's address + the offset
        # code/4 gave).
        w = self.g_word(x)
        if w is None or w[0] != COD:
            return self.guard_fail()
        head = self.mem[w[1] - 2]
        m = w[1] - 2 - (head[1] & 0xffffff)
        if head[0] != PREDH or self.mem[m][0] != CDESC:
            raise Unimplemented('code: no predicate head or module before %x' % w[1])
        self.reg[y] = (INT, head[1] >> 24)
        self.reg[z] = (MOD, m)
        self.reg[self.cells[pc + 1][1] >> 24] = (INT, w[1] - m)
        return pc + 2

    def i_scsi_where(self, pc, x, y, z, c16):
        # scsi_where(^Info), 22:A0: "Info ::= [] | [SCSI_Info | Info],
        # SCSI_Info ::= {Cluster, Processor, SCSI_PORT, MY_UNIT}" (the
        # built-in's stand-in in PIMOS source, bios/boot/scsi_conf.kl1,
        # whose header gives that grammar; its compiler entry
        # library/compiler/blt.kl1 has one output, no input).  The
        # value is the stand-in's for one front-end processor on eight
        # or fewer nodes, [{0, 0, 0, 6}]: one SCSI port on cluster 0,
        # processor 0, port 0, this machine's own unit 6.  What PIM/m's
        # firmware read it from (the machine's configuration) is not
        # known; the single-FEP value is the stand-in's, labelled as
        # such.
        w, a = self.vnew(4)
        for k, v in enumerate((0, 0, 0, 6)):
            self.mem[a + k] = (INT, v)
        c = self.alloc(2)
        self.mem[c], self.mem[c + 1] = w, NIL
        self.reg[x] = (LIST + 1, c)

    def i_new_atom(self, pc, x, y, z, c16):
        # new_atom(^Atom): "creates a new atom ... The atom has no
        # printing name" (PDSS manual, pdss.tex).  Which number is
        # OURS: a counter up from NEW_ATOM0, clear of the image's own
        # atoms.  PDSS counts down from the top of its table; PIM/m
        # gave each processor a range (supply_atom_number, the server
        # in pimos::top), whose first value is not known.
        if self.next_atom > 0xffffff:
            raise Unimplemented('new_atom: out of atom numbers')
        self.reg[x] = (ATOM, self.next_atom)
        self.next_atom += 1

    def i_supply_atom_number(self, pc, x, y, z, c16):
        # supply_atom_number(X, Y, ^Done), 22:B9 r_r_r, two inputs and
        # an output (PIMOS library/assembler/inst_tab.kl1:249,
        # library/compiler/blt.kl1:747-750).  No manual entry; nothing
        # in PDSS, VPIM or the PIMOS source says what it does.  Its
        # callers (top:throw_atom_number_client/7, atom_number_client/5,
        # ref/pimm/lockstep_atom.py) force only this much: X and Y are
        # integers (a block of atom numbers from the server in
        # pimos::top, which numbers is not inferred) and Done is waited
        # for, each binding making the processor ask for another block,
        # so the machine binds it later, not at once.  OURS, the
        # narrowest: the integers are dropped, Done is a fresh variable
        # no model binds (new_atom, a counter of ours, draws on no
        # block).  supplied records the calls, for tests.
        def f(a, b):
            a, b = self.need_int(a), self.need_int(b)
            v = self.new_var()
            self.supplied.append((a, b, v))
            return [v]
        self.builtin('supply_atom_number', [x, y, z], f)

    def i_hash(self, pc, x, y, z, c16):
        # hash(X, ^Value, ^NewX): "unifies Value with a hash code
        # computed according to X, and also unifies NewX with X" (PDSS
        # manual).  The code is PDSS's (emulator/blt_system.c
        # blt_b_hash): the value of an atom or integer, -1 for a list,
        # a vector's length, and for a string its word count plus a
        # mix of its first and last words.  PIM/m's own function is
        # lost with the firmware; any function gives a correct table,
        # so where an entry lies in a hashed table is not the
        # machine's.  PDSS gives 0 for anything else: refused here.
        def f(w):
            t = w[0] & ~1
            if t in (INT, ATOM):
                h = w[1]
            elif t == LIST:
                h = 0xffffffff
            elif t == STRG:
                d = self.mem[w[1]]
                if d[0] != CDESC:
                    raise RuntimeError('string without a descriptor at %x' % w[1])
                h = d[1] & 0xffffff
                if h:
                    a, b = self.mem[w[1] + 1][1], self.mem[w[1] + h][1]
                    h += a + (a >> 16) + (a >> 24) + (b << 1) + (b >> 15) + (b >> 23)
            elif VECT0 <= t <= VECT0 + 12:
                h = self.vsize(w)
            else:           # a long vector too, for now
                raise Unimplemented('hash of %r' % (w,))
            return [(INT, h & 0xffffffff), w]
        self.builtin('hash', [x, y, z], f)

    def i_code_to_predicate(self, pc, x, y, z, c16):
        # code_to_predicate(Code, ^Module, ^Name, ^Arity, ^Info), 22:F4
        # r5 (assembler/inst_tab.kl1:353): "Unifies a module to which
        # Code belongs with Module, a predicate atom with Name, argument
        # count with Arity, and 1-word information (contents of <Code
        # address - 3>) for software with Info.  Exception: If Code is
        # anything other than a code" (PIMOS manual, e-builtin.tex
        # 1304-1311, "for the Multi-PSI and PIM/m"): refused.  The
        # predicate is laid out Name, 0, the head, the length, then the
        # code (assembler/assemble.kl1 make_pred_head), so Name is Code
        # - 4 and Info Code - 3; the module as the guard code finds it.
        # VPIM (klb_body_blt_cont.psl.c kblt_b_code_to_predicate) gives
        # Name the atom tag and Arity the integer tag, MRB off
        w4, w5 = self.cells[pc + 1][1] >> 24, self.cells[pc + 1][1] >> 16 & 0xff

        def f(c):
            if c[0] != COD:
                raise Unimplemented('built-in exception: code_to_predicate(%r)' % (c,))
            head = self.mem[c[1] - 2]
            m = c[1] - 2 - (head[1] & 0xffffff)
            name = self.mem[c[1] - 4]
            if head[0] != PREDH or self.mem[m][0] != CDESC or name[0] & ~1 != ATOM:
                raise Unimplemented('code_to_predicate: no predicate head before %x' % c[1])
            return [(MOD, m), (ATOM, name[1]), (INT, head[1] >> 24), self.mem[c[1] - 3]]
        self.builtin('code_to_predicate', [x, y, z, w4, w5], f)
        return pc + 2

    def i_b_vector(self, pc, x, y, z, c16):
        # body vector(X, ^Size, ^NewVector), 22:CA r_r_r (assembler/
        # inst_tab.kl1:298): "The size of the vector X is unified with
        # Size, and X is unified with NewVector.  Exception: If X is
        # anything other than a vector" (PIMOS manual, e-builtin.tex
        # 750-755): refused.  r[y] := the size, then r[z] := X.  VPIM
        # (kblt_b_vector_size) copies a vector whose MRB is on, to give
        # NewVector a single reference; the same term, so OURS: X itself
        def f(v):
            n = self.vsize(v)
            if n is None:
                raise Unimplemented('built-in exception: vector')
            return [(INT, n), v]
        self.builtin('b_vector', [x, y, z], f)

    def i_b_vector_element(self, pc, x, y, z, c16):
        # vector_element(V, I, ^E, ^V1): r[z] := element, r[w] := the vector
        w4 = self.cells[pc + 1][1] >> 24

        def f(v, i):
            n, i = self.vsize(v), self.need_int(i)
            if n is None or not 0 <= i < n:
                raise Unimplemented('built-in exception: vector_element')
            return [self.taken(self.vbase(v) + i, mark=True), v]
        self.builtin('b_vector_element', [x, y, z, w4], f)
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
            return [(w[0] & ~1, w[1])]        # the only reference: MRB off
        self.builtin('new_vector', [x, y], f)

    def i_set_vector_element(self, pc, x, y, z, c16):
        # set_vector_element(V, I, New, ^Old, ^V1).  It does not wait
        # for New.  In place when the vector was reached with every
        # MRB off ("providing the path to the vector is single", M92
        # p. 430; PDSS blt_b_set_vector_element: "if(Mrbof(vect) ==
        # MRBOFF){ ... *x = newelem"), and V1 is V.  Otherwise a copy
        # whose elements are marked, an unbound one copied as a
        # reference to the old cell; that the copy is whole is ours
        # (Multi-PSI/V2 had a mutable-array scheme, TR-466 4.1.1).
        # Ours too: an element cell that is itself an unbound variable
        # is never overwritten (Old would become New); that copies.
        w4, w5 = self.cells[pc + 1][1] >> 24, self.cells[pc + 1][1] >> 16 & 0xff

        def f(v, i, e):
            n, i = self.vsize(v), self.need_int(i)
            if n is None or not 0 <= i < n:
                raise Unimplemented('built-in exception: set_vector_element')
            src = self.vbase(v)
            if not v[0] & 1 and self.mem[src + i][0] & ~1 not in (UNDF, HOOK):
                old = self.mem[src + i]
                self.mem[src + i] = e
                return [old, v]
            w, a = self.vnew(n)
            old = None
            for k in range(n):
                c = self.taken(src + k)
                if k == i:
                    old = c
                self.mem[a + k] = e if k == i else c
            return [old, (v[0] & ~1, w[1])]   # a new vector: MRB off
        self.builtin('set_vector_element', [x, y, z, w4, w5], f, nowait=(2,))
        return pc + 2

    # ---- one processor ------------------------------------------------
    def i_enqueue_goal_to_processor(self, pc, x, y, z, c16):
        # Goal@processor(N).  Two cells, as enqueue_goal_with_priority
        # (assembler/klb_opr.kl1 p(r_c16_c8_exe)): the processor's
        # register, the label; the arity in the next cell's top byte.
        # TM-1044's enqueue_to_processor(.., Rprocessor, ARITY) (as
        # listed in docs/literature_gaps.md, line 2441).  There
        # is ONE processor here, number 0 (ours): for 0 the goal is
        # made as enqueue_goal makes it; another number is refused.
        # An unbound number is waited for (carried over from VPIM,
        # agreeing with KLIC; the PIM/m firmware's behaviour is not
        # held: asm/pimm_stubs.py TO_PROCESSOR): P and the code address
        # are put after the arguments, and a goal of the stub
        # to_processor N is hooked on P.
        n = self.cells[pc + 1][1] >> 24
        w = self.deref(self.reg[x])
        if self.unbound(w) and n <= pimm_stubs.TO_PROCESSOR_MAX:
            self.argv[n + 1] = w
            self.argv[n + 2] = (INT, self.load + pc + 2 + sx16(c16))
            g = self.record(SUSPENDED, self.stubs['$to_processor%d' % n]['addr'], self.argv[1:n + 3])
            self.nsusp += 1
            self.hook(g, w[1])
            return pc + 2
        if w[0] & ~1 != INT or w[1] != 0 or n > 11:
            raise Unimplemented('enqueue_goal_to_processor %r, %d arguments' % (w, n))
        self.record(READY, pc + 2 + sx16(c16), self.argv[1:n + 1])
        return pc + 2

    def i_to_processor(self, pc, x, y, z, c16):
        """Ours, only at its stub: the waiting goal of Goal@processor(P),
        r0.. the goal's z arguments, r[x] = P, r[y] = the goal's code
        address.  P still unbound: the goal waits again.  P = 0: the
        goal is made ready (VPIM's dcode_apply(Code,Argv)@processor(P)).
        Another number is refused."""
        if pc != self.stubs.get('$to_processor%d' % z, {}).get('addr'):
            raise Unimplemented('to_processor at %d' % pc)
        w = self.deref(self.reg[x])
        if self.unbound(w):
            g = self.record(SUSPENDED, pc, self.reg[:z + 2])
            self.nsusp += 1
            self.hook(g, w[1])
            return None
        if w[0] & ~1 != INT or w[1] != 0:
            raise Unimplemented('enqueue_goal_to_processor %r' % (w,))
        self.record(READY, self.reg[y][1] - self.load, self.reg[:z])
        return None

    # collect_garbage, 23:77, no operands (inst_tab.kl1; the shell's
    # gc, shell/utils/gc.kl1: `gcCall :- collect_garbage | true`).
    # R7G, INFERENCE (pimm_gc.py, its header): its microcode, 02d5-02d7,
    # writes one cell and a work register and ends, so it only asks;
    # the collection is made at the next goal switch (run).  The guard
    # succeeds.  The request is not machine memory: no trace line until
    # the collection's K line
    gc_request = False

    def i_collect_garbage(self, pc, x, y, z, c16):
        self.alone('collect_garbage')       # until the core has its collector
        self.gc_request = True

    def i_read_eagerly(self, pc, x, y, z, c16):
        # What the compiler writes for `alternatively.` (library/
        # compiler/indexornot.kl1 compile_one_block: "&code <<=
        # [read_eagerly]").  The clauses after it are tried "not only
        # when the first clause fails but also when it suspends"
        # (TR-483 2.4.4); the instruction itself: "if external
        # references are on the suspension stack, perform Eager Read
        # on them", no branch (TM-1044 s3, alternatively()); both as
        # quoted in docs/literature_gaps.md, lines 1534 and 2259.  One
        # processor has no external references: nothing is done, the
        # variables noted so far stay noted, and the next clause is
        # tried.
        pass

    # ---- the SCSI built-ins --------------------------------------------
    # The firmware that ran them is lost.  What is known: the operand
    # directions (library/compiler/blt.kl1 active_builtin(scsi_init /
    # scsi_command)), the callers (bios/scsi/scsi_handler.kl1 =
    # scsi:create/2, command_executer/2 in the image; scsi_common.kl1,
    # scsi_processor.kl1) and the stand-in for a machine without the
    # built-ins, bios/scsi/scsi_blt.kl1, which is also in the IPL image
    # (scsi_builtin:scsi_init/3 at cell 13952).  The device is a Python
    # object, Machine.fep (ref/pimm/fep.py): NOT machine state.  On the
    # core: bsv/PimmScsiBox.bsv, the device on a port (lockstep_scsi.py).
    def i_scsi_init(self, pc, x, y, z, c16):
        # scsi_init(^Obj, ^TargetInterruptVector, ^Info): three
        # outputs, so it never waits.  OURS, all three values, taken
        # from the stand-in (scsi_blt.kl1: "SCSI_Obj = 1,
        # TargetInterruptVector = {0,0,0}, Info = {16000,8,4,0}").
        # What the callers need: Obj bound (scsi:object_manager/2
        # waits for it), Info a vector of four with integers at 0 (the
        # largest transfer: scsi_fep_module makes its packet buffers
        # that long) and 2.
        if getattr(self, 'fep', None) is None:
            raise Unimplemented('scsi_init: no device attached')
        self.reg[x] = (INT, 1)
        # the buffer size is the device's: asked here (a bench's tape)
        size = self.fep.MAX_BUFFER
        self.event('B init')
        self.scsi_tape.append(('init', size))
        for r, elems in ((y, (0, 0, 0)), (z, (size, 8, 4, 0))):
            w, a = self.vnew(len(elems))
            for k, e in enumerate(elems):
                self.mem[a + k] = (INT, e)
            self.reg[r] = (w[0] & ~1, w[1])      # the only reference: MRB off

    def i_scsi_command(self, pc, x, y, z, c16):
        # scsi_command(Obj, {Unit, LUN, CDB, Length, Dir, Buffer, 0},
        # ^Data, ^TransferredLength, ^Id, ^Result, ^NewObj): seven
        # registers, the last four in the next cell (klb_opr.kl1 r7).
        # From the callers: Dir 0 none, 1 out, 2 in; Result 0 is
        # success (scsi_common:analyze_scsi_command_result/7); Data is
        # an 8-bit string the caller uses as its next buffer
        # (scsi_fep_module:next_send/7, receive_packet*/9), so it is
        # the WHOLE buffer with the bytes received written in (a copy
        # here; the same string for a command that receives nothing).
        # OURS:
        #  - it waits for every element of the vector, as
        #    string_operation waits for its vector's.  Run only by
        #    lockstep_scsi.py ("element"): in the IPL's runs the
        #    elements were all bound when the command was made;
        #  - Id is the count of commands so far (no caller reads it);
        #  - NewObj is Obj;
        #  - a command the device cannot finish yet (a RECEIVE with no
        #    reply made: the IPL asks for the reply when it queues the
        #    request, not when the request has gone) gives Id and
        #    NewObj at once and leaves Data, TransferredLength and
        #    Result unbound until the device has the reply, since the
        #    next command (the SEND) is only issued once NewObj is
        #    bound.  The waiting commands are in Python
        #    (self.scsi_waiting), not in memory.
        # The seventh element (0 from every caller) is not understood
        # and must be the integer 0.
        r7 = self.cells[pc + 1][1]
        regs = [x, y, z, r7 >> 24, r7 >> 16 & 255, r7 >> 8 & 255, r7 & 255]

        def f(obj, v):
            if getattr(self, 'fep', None) is None:
                raise Unimplemented('scsi_command: no device attached')
            if self.vsize(v) != 7:
                raise Unimplemented('scsi_command on %r' % (v,))
            e = [self.deref(self.taken(self.vbase(v) + i)) for i in range(7)]
            unit, lun, length, direction = (self.need_int(e[i]) for i in (0, 1, 3, 4))
            cs, cdb = self.need_string(e[2])
            bs, buf = self.need_string(e[5])
            if cs != 8 or bs != 8 or self.need_int(e[6]) != 0 or not 0 <= length <= len(buf):
                raise Unimplemented('scsi_command arguments %r' % (e,))
            # cdbw: the CDB's string, kept for a checkpoint of a waiting
            # command (lockstep_shell.py gives it to the core, whose
            # waiting list holds the cells); not read here
            cmd = dict(unit=unit, lun=lun, cdb=cdb, length=length, dir=direction, buf=buf,
                       word=e[5], cdbw=e[2])
            ident = (INT, self.scsi_commands)
            self.scsi_commands += 1
            done = self.scsi_do(cmd)
            if done is None:
                cmd['outs'] = [self.new_var() for _ in range(3)]
                self.scsi_waiting.append(cmd)
                self.scsi_deferred += 1
                done = cmd['outs']
            else:
                self.scsi_poll()      # the device has moved
            return [done[0], done[1], ident, done[2], obj]
        self.builtin('scsi_command', regs, f, elements=lambda obj, v: (
            self.unbound_elements(v) if self.vsize(v) == 7 else []))
        return pc + 2

    def scsi_poll(self):
        """Give the device the commands that wait for it again, oldest
        first; the outputs of one that finishes are bound (waking
        whatever waits for them).  Returns how many finished.  Called
        after any command that finishes, and by a bench when the
        machine has nothing left to run (the device's interrupt, as
        it were)."""
        n = 0
        for c in list(self.scsi_waiting):
            got = self.scsi_do(c)
            if got is not None:
                self.scsi_waiting.remove(c)
                for var, w in zip(c['outs'], got):
                    self.unify(var, w)
                n += 1
        return n

    def scsi_do(self, cmd):
        """Give the command to the device: (Data, TransferredLength,
        Result) words, or None if the device cannot finish it yet.
        Each call is one B line in the trace (what the core puts on the
        bus) and one entry of the device tape (what it is answered)."""
        out = bytes(cmd['buf'][:cmd['length']])
        self.event('B %d %d %s %d %d%s' % (cmd['unit'], cmd['lun'], bytes(cmd['cdb']).hex(),
                                           cmd['dir'], cmd['length'],
                                           ' ' + out.hex() if cmd['dir'] == 1 and out else ''))
        self.fep.ticks = self.timer()     # the FEP's time of day follows the clock
        got = self.fep.command(cmd['unit'], cmd['lun'], bytes(cmd['cdb']), cmd['length'],
                               cmd['dir'], out)
        self.scsi_tape.append(got)
        if got is None:
            return None
        result, data = got
        word = cmd['word']
        if data:
            if len(data) > cmd['length']:
                raise RuntimeError('the device gave %d bytes for %d' % (len(data), cmd['length']))
            word = self.make_string(8, list(data) + cmd['buf'][len(data):])
        n = len(data) if cmd['dir'] == 2 else cmd['length']
        return [word, (INT, n), (INT, result)]


def predicate(im, module, pred):
    for m in im.mods:
        if m['name'] == module:
            for n, _ln, addr in m['preds']:
                if n == pred:
                    return addr
    raise KeyError('%s:%s' % (module, pred))
