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
strings.  No garbage collection (the heap only grows); the MRB is
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
NEW_ATOM0 = 0x10000         # the first atom new_atom gives: ours
VECT0 = 0x10                # VECTn (n = 1..6) is VECT0 + 2n, low bit as o/x
# A shoen's handle: {SHREC, the address of its shoen record}.  The tag
# is PIM/m-sourced (PIMOS debugger/inspector/tagtbl.kl1, 16#"38" SHREC);
# what it points at is OURS (asm/pimm_layout.py).  From 20h: no MRB bit.
SHREC = 0x38
from pimm_layout import (G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS,  # noqa: E402
                         READY, SUSPENDED, TAKEN, S_NEXT, S_GOAL, S_SIZE,
                         MEMORY_CELLS, HEAP)
from pimm_layout import (SH_COUNT, SH_STATUS, SH_PARENT, SH_REPORT,  # noqa: E402
                         SH_GOAL, SH_SIZE, DORMANT, STARTED, TERMINATED,
                         REPORT_STARTED, REPORT_TERMINATED)
from pimm_layout import (SH_REDUCTIONS, SH_REMOVE, REMOVED,  # noqa: E402
                         REPORT_STATISTICS_STARTED, REPORT_STATISTICS,
                         REPORT_RETURN_RESOURCE)


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
        if a[0] & ~1 == LIST or VECT0 + 2 <= a[0] & ~1 <= VECT0 + 12:
            # Two lists, or two vectors of the same size (of up to six:
            # the size is in the tag, so the tags were equal).  Not
            # unified here: a goal is made that unifies the elements
            # when it runs, as PDSS does (emulator/unify.c
            # make_unify_list_list_goal_and_enqueue,
            # make_unify_vector_vector_goal_and_enqueue).  What PIM/m's
            # firmware did is not known.  The goal's code is the stub
            # unify_step (asm/pimm_stubs.py).  The same object against
            # itself makes a goal too, as in PDSS.
            self.record(READY, self.stubs['$unify_step']['addr'], [a, b, (INT, 0)])
            return
        # a vector of seven or more (its size is in memory), a module,
        # anything else
        raise Unimplemented('unify of %r and %r' % (a, b))

    # strings: {STRG, address} -> {CDESC, pad << 27 | type << 24 | words},
    # then `words` cells of 32 bits, elements packed from the top.
    # type 3 = 8-bit elements, 4 = 16-bit, 5 = 32-bit (kbnheap.kl1
    # string_cdesc); 1-bit strings are not modelled.
    def string(self, w):
        t, v = self.mem[w[1]]
        if t != CDESC:
            raise RuntimeError('string without a descriptor at %x' % w[1])
        typ, pad, words = (v >> 24) & 7, (v >> 27) & 3, v & 0xffffff
        if typ not in (3, 4, 5):
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
        if size not in (8, 16, 32) or n < 0:
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
        typ = {8: 3, 16: 4, 32: 5}[size]
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
        """A terminated shoen is removed: {14, 0, 0} (return_resource:
        no resource is modelled, so nothing is left to return, OURS),
        then the report stream is closed (its tail unified with []) and
        the record marked REMOVED.  VPIM's order (f_shoen_control.psl.c:
        547-575, f_shoen_with_fp.psl.c:69-71: return_resource, close,
        reclaim), not PIM/m-sourced."""
        self.report3(sh, REPORT_RETURN_RESOURCE, 0, 0)
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
        (asm/pimm_layout.py)."""
        sh, red = self.shoen, self.chain
        while sh:
            red = self.mem[sh + SH_REDUCTIONS][1] + red & 0xffffffff
            self.mem[sh + SH_REDUCTIONS] = (INT, red)
            n = self.mem[sh + SH_COUNT][1] - 1 & 0xffffffff
            self.mem[sh + SH_COUNT] = (INT, n)
            if n:
                break
            self.mem[sh + SH_STATUS] = (INT, TERMINATED)
            self.report(sh, REPORT_TERMINATED)
            if self.mem[sh + SH_REMOVE][1]:
                self.remove(sh)
            sh = self.mem[sh + SH_PARENT][1]

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
            st = self.mem[g + G_STATUS][1]        # shoen << 2 | status
            self.shoen = self.load + (st >> 2) if st >> 2 else 0
            self.mem[g + G_STATUS] = (INT, st & ~3 | TAKEN)
            code = self.mem[g + G_CODE][1] - self.load
            for i in range(self.mem[g + G_ARGN][1]):
                self.reg[i] = self.mem[g + G_ARGS + i]
            self.chain = 0
            self.reduce(code, before + limit)     # the limit is this run's
            self.end_reduction()
        self.shoen = 0                # what a bench makes between runs is the root's
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
                # inside a shoen a failure is reported to the shoen
                # (the exception path): not modelled
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
        # are not.  Vectors as below; lists, and one variable twice,
        # need the general passive unification and are refused
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
            # vectors: PDSS's passive unification (emulator/emulate.c
            # KL1B_WAIT_VALUE, emulator/passive.c passive_unify) as far
            # as both models take it: two vectors of 0..6 elements are
            # equal when the sizes are and each pair of elements is the
            # same atomic value; in order, the first unbound element met
            # is noted and the guard fails there (X's; or Y's opposite
            # an atomic element of X).  A vector against anything else
            # bound fails.  Refused: a list, a vector of seven or more,
            # an element of X that is a structure or a string
            if not self.passive(a, b):
                return self.guard_fail()
            return
        if not (self.atomic(a) and self.atomic(b)):
            raise Unimplemented('wait_value on a structure')
        if (a[0] & ~1, a[1]) != (b[0] & ~1, b[1]):
            return self.guard_fail()

    def structure(self, w):
        return w[0] & ~1 == LIST or self.vsize(w) is not None

    def passive(self, a, b):
        """Two bound words, at least one a list or a vector: whether
        they are equal (wait_value).  An unbound element met is noted
        and answers False."""
        short = lambda w: VECT0 <= w[0] & ~1 <= VECT0 + 12      # noqa: E731
        for w in (a, b):
            if w[0] & ~1 == LIST or (self.vsize(w) is not None and not short(w)):
                raise Unimplemented('wait_value on %r' % (w,))
        if not (short(a) and short(b)):
            return False
        n = self.vsize(a)
        if n != self.vsize(b):
            return False
        for i in range(n):
            x = self.deref(self.taken(self.vbase(a) + i))
            y = self.deref(self.taken(self.vbase(b) + i))
            if self.unbound(x):
                self.waiting.append(x[1])
                return False
            if not self.atomic(x):
                raise Unimplemented('wait_value: an element %r' % (x,))
            if self.unbound(y):
                self.waiting.append(y[1])
                return False
            if (x[0] & ~1, x[1]) != (y[0] & ~1, y[1]):
                return False
        return True

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
        if not (self.atomic(a) and self.atomic(b)):
            raise Unimplemented('diff on a term that is not atomic')
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
        # the integer is the low 24 bits.  Whether bit 23 is a sign is
        # not established (the image has no such operand): refused
        v = self.cells[pc][1] & 0xffffff
        if v >> 23:
            raise Unimplemented('write_integer with bit 23 set')
        self.mem[self.sp] = (INT, v)
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

    def i_wait_vector_2(self, pc, x, y, z, c16):
        return self.wait_vector(2, x)

    def i_wait_vector_3(self, pc, x, y, z, c16):
        return self.wait_vector(3, x)

    def i_wait_vector_5(self, pc, x, y, z, c16):
        return self.wait_vector(5, x)

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

    def i_enqueue_goal(self, pc, x, y, z, c16):
        # A goal has 11 argument slots; the compiler packs the
        # arguments from the 11th on into a vector, which is the 11th
        # (library/compiler/pack.kl1: max_goal_slots, "for V2").  The
        # called predicate uses r10, r11, ... with no code to unpack
        # them, so the firmware must spread the vector; where it does
        # is not known.  Here it is spread as the goal is made, and
        # this model's record holds every argument.
        if x > 11:
            v = self.argv[11]
            if x > 16 or v[0] & ~1 != VECT0 + 2 * (x - 10):
                raise Unimplemented('enqueue_goal %d without its argument vector' % x)
            base = self.vbase(v)
            for i in range(x - 10):
                self.argv[11 + i] = self.taken(base + i)
        self.record(READY, pc + 2 + sx16(c16), self.argv[1:x + 1])

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
        # p(c8_c16_ext)).  More than 11 arguments is refused.
        if x > 11:
            raise Unimplemented('enqueue_goal_external %d' % x)
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
        # 8, 16 and 32 bits; a 1-bit string is refused.
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
        # NewS2 is Str2 (manual).  The vectors of four and three
        # elements (the shifting and unary forms) are refused.  An
        # element of the vector that is not yet a value is waited for
        # (the manual says the built-in waits; builtin_utility:
        # append_string/2 gives it a new_string whose length is not
        # yet known): the goal of the stub waits on the first such
        # element, as it would on an operand.
        w4 = self.cells[pc + 1][1] >> 24

        def f(op, v):
            op = self.need_int(op)
            if self.vsize(v) != 5 or not 0 <= op <= 15:
                raise Unimplemented('string_operation %d on %r' % (op, v))
            e = [self.deref(self.mem[self.vbase(v) + i]) for i in range(5)]
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
            self.unbound_elements(v) if self.vsize(v) == 5 else []))
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
    # switch, not at the unification.  A vector on the input adds as
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
            # refused the case).  A vector of seven or more is refused
            # (as apply refuses one; none is met).
            if w[0] & ~1 == VECT0 + 14:
                raise Unimplemented('a merger input bound to a vector of seven or more')
            n = self.vsize(w)
            count = self.mem[rec + 1][1] - 1 + n
            self.mem[rec + 1] = (INT, count)
            if count == 0:
                self.unify(self.mem[rec], NIL)
            for i in range(n):
                self.argv[1] = self.taken(w[1] + i)
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
        n = 2 if a[0] & ~1 == LIST else (a[0] & ~1) - VECT0 >> 1
        if i == n:
            return None
        ea = self.taken(a[1] + i, single=not a[0] & 1)
        eb = self.taken(b[1] + i, single=not b[0] & 1)
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
        # so are a vector of seven or more (its size is in memory) and
        # the empty vector (no test can run a predicate of no argument:
        # the image's three are boot, boot0 and noop).
        def f(code, args):
            n = self.vsize(args)
            head = self.mem[code[1] - 2] if code[0] == COD else None
            if head is None or head[0] != PREDH or not n or n > 6 or n != head[1] >> 24:
                raise Unimplemented('built-in exception: apply(%r, %r)' % (code, args))
            for i in range(n):
                self.argv[i + 1] = self.taken(args[1] + i, single=not args[0] & 1)
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
        #    integers (shoen:execute1/7 passes vectors: refused) and
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

        def f(lo, hi, mask, _code, _argv):
            for w in (lo, hi, mask):
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
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('start_shoen(%r)' % (h,))
            sh = h[1]
            if self.mem[sh + SH_STATUS][1] != DORMANT:
                raise Unimplemented('start_shoen of a shoen that is not dormant')
            self.report(sh, REPORT_STARTED)
            self.mem[sh + SH_STATUS] = (INT, STARTED)
            g = self.mem[sh + SH_GOAL][1]
            st = self.mem[g + G_STATUS][1]
            self.event('W %d' % (g - self.load))
            self.mem[g + G_STATUS] = (INT, st & ~3 | READY)
            self.mem[g + G_LINK] = (INT, self.rq)
            self.rq = g
            self.nsusp -= 1
            return [h]
        self.builtin('start_shoen', [x, y], f)

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
            cmd = dict(unit=unit, lun=lun, cdb=cdb, length=length, dir=direction, buf=buf,
                       word=e[5])
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
