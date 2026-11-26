#!/usr/bin/env python3
"""PIM/m with more than one PE, on the reference model: rung M1.

docs/multi_pe.md is the plan and the evidence; every choice below is
labelled there.  In brief:

- A System holds N PEs.  Each PE is a pimm.Machine of its own (its own
  memory, heap, registers, ready queue): PIM/m has one memory per PE
  (M92 p. 430).  The PEs are made by copying one loaded machine, so a
  code address means the same on every PE (OURS scaffolding; PIM/m
  sends a module's global identifier and fetches it, M92 pp. 430-431).
- current_node gives (k, N) on PE k (PIMOS manual e-builtin.tex
  current_node).
- Goal@node(K) (enqueue_goal_to_processor, 23:65; PIMOS compiler
  newnorm.kl1:842-905) with K this PE makes the goal here; with K
  another PE it sends %throw_goal (VPIM's cluster branch, klb_fork.psl.c
  1069-1075, docs/multi_pe.md 1.3).  An atom or a number out of range is
  an exception on PIM/m (illegal_input, range_overflow, e-shoen.tex
  486-514), not modelled: refused.
- The arguments of a thrown goal are copied at level 0 (TM-1044 9.2;
  TR-715 5.4.1): an integer or atom as it is; an unbound variable is
  EXPORTED (an entry of this PE's export table holding the reference)
  and sent as an external reference ID, {EXREFo, pe << 24 | entry}
  (VPIM's ID: 8-bit cluster, 4 flag bits, 20-bit offset,
  f_int_cl_msg_type.psl.c section 4; EXREFx for a reference with its
  MRB on, INFERENCE from M92's MRB-on table).  Anything else is
  refused (rung M2).
- The receiver IMPORTS an external reference ID: a white import entry
  holding the ID (TM-1044 s9.tex:199-215; here a table of the PE,
  outside the heap as the white import table is in the system's fixed
  area there, OURS that it is not in memory cells) and a one-word
  external cell {EXREFo, entry} in the heap; the goal's argument is a
  reference to that cell.
- A unification of an external cell with an integer or atom sends
  %unify(ID, value) to the exporting PE (level 1: TM-1044 9.2), which
  binds its variable (waking its goals) and frees the entry (OURS at
  M1: no WEC, no %release; one table for both MRB kinds; rung M3).
  Any other use of an external cell is refused: a guard or wait on it
  needs %read (rung M2).
- Messages are VPIM's logical packets, one word per item, the fields
  this rung does not model sent as 0 (f_int_cl_send_throw_goal.psl.c
  15-60, f_int_cl_recv_unify.psl.c 9-35); the kind codes are the
  Pseudo PIM/m console's (pimmcsp.ptf kl1_message_order_macro: m_throw
  0, m_unify 9).  Each ordered pair of PEs is a FIFO (TR-390 3.1); a PE
  decodes the messages waiting for it at a goal switch, before its next
  goal (TR-715 3.3), from the lower-numbered sender first (OURS).
- The PEs run in turn, PE 0 first, each for a quota of goal switches
  (the console's roundrobin_scheduler, INFERENCE as to the unit).

Goals of the root only (no shoen): a throw from inside a shoen is
refused (rung M4).  The PE classes never change a single machine:
pimm.Machine's behaviour on one PE is untouched (its run() calls the
same goal_switch() this file calls).
"""
import io
import os
import pickle
import sys
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pimm  # noqa: E402
from pimm import INT, ATOM, REF, Unimplemented, sx16  # noqa: E402

EXREF = 0x32            # EXREFo; 0x33 EXREFx (debugger/inspector/tagtbl.kl1)
EXVAL = 0x34            # EXVALo, EXVALx: not made at M1
EX_TAGS = (0x32, 0x33, 0x34, 0x35)
# message kinds: the Pseudo PIM/m console's codes (docs/multi_pe.md 1.1),
# the same as VPIM's _NW_THROW_GOAL and _NW_UNIFY
M_THROW, M_UNIFY = 0, 9
# where the arguments start in a %throw_goal packet (VPIM's fields 1-15)
THROW_ARGS = 15


def ext_id(pe, entry):
    assert 0 <= pe < 256 and 0 < entry < 1 << 20
    return pe << 24 | entry


class PE(pimm.Machine):
    """One processing element.  Made by System from a loaded machine."""

    def setup(self, system, pe):
        self.system = system
        self.pe = pe
        self.exports = {}           # entry -> the exported reference
        self.next_export = 1
        self.imports = {}           # entry -> external reference ID
        self.next_import = 1
        self.ex_ok = False          # set while unify looks at an external cell
        self.collections = 0

    # ---- what a PE knows of the others ------------------------------
    def i_current_node(self, pc, x, y, z, c16):
        self.reg[x] = (INT, self.pe)
        self.reg[y] = (INT, self.system.n)

    def i_current_processor(self, pc, x, y, z, c16):
        if self.system.n > 1:
            raise Unimplemented('current_processor on more than one PE')
        return pimm.Machine.i_current_processor(self, pc, x, y, z, c16)

    def i_unbound(self, pc, x, y, z, c16):
        if self.system.n > 1:
            raise Unimplemented('unbound/2 on more than one PE')
        return pimm.Machine.i_unbound(self, pc, x, y, z, c16)

    # ---- collect_garbage asks; the collection is at the goal switch --
    def i_collect_garbage(self, pc, x, y, z, c16):
        self.system.log.append(('ask', self.pe))
        return pimm.Machine.i_collect_garbage(self, pc, x, y, z, c16)

    def goal_switch(self, limit):
        if self.gc_request:
            if self.exports:
                # the export table would be a root of the collector
                # (TR-466 3.2): rung M3
                raise Unimplemented('a collection with %d live exports' % len(self.exports))
            self.collections += 1
            self.system.log.append(('gc', self.pe))
        return pimm.Machine.goal_switch(self, limit)

    # ---- @node -------------------------------------------------------
    def node_number(self, w):
        if w[0] & ~1 != INT:
            raise Unimplemented('Goal@node(%r): illegal_input, not modelled' % (w,))
        k = pimm.signed(w[1])
        if not 0 <= k < self.system.n:
            raise Unimplemented('Goal@node(%d) of %d nodes: range_overflow, not modelled'
                                % (k, self.system.n))
        return k

    def i_enqueue_goal_to_processor(self, pc, x, y, z, c16):
        n = self.cells[pc + 1][1] >> 24
        w = self.deref(self.reg[x])
        if self.unbound(w):
            return pimm.Machine.i_enqueue_goal_to_processor(self, pc, x, y, z, c16)
        k = self.node_number(w)
        if n > 11:
            raise Unimplemented('enqueue_goal_to_processor, %d arguments' % n)
        code = pc + 2 + sx16(c16)
        if k == self.pe:
            self.record(pimm.READY, code, self.argv[1:n + 1])
        else:
            self.throw(k, code, self.argv[1:n + 1])
        return pc + 2

    def i_to_processor(self, pc, x, y, z, c16):
        if pc != self.stubs.get('$to_processor%d' % z, {}).get('addr'):
            raise Unimplemented('to_processor at %d' % pc)
        w = self.deref(self.reg[x])
        if self.unbound(w):
            return pimm.Machine.i_to_processor(self, pc, x, y, z, c16)
        k = self.node_number(w)
        code = self.reg[y][1] - self.load
        if k == self.pe:
            self.record(pimm.READY, code, self.reg[:z])
        else:
            self.throw(k, code, self.reg[:z])
        return None

    # ---- %throw_goal -------------------------------------------------
    def throw(self, k, code, args):
        if self.shoen:
            raise Unimplemented('a goal thrown from inside a shoen (rung M4)')
        packet = [(INT, M_THROW), (INT, 0), (INT, 0), (INT, 0), (INT, 0), (INT, 0),
                  (INT, 0), (INT, 0), (INT, self.system.n), (INT, 0),
                  (pimm.COD, self.load + code), (INT, 0), (INT, 0), (INT, 0),
                  (INT, len(args))]
        assert len(packet) == THROW_ARGS
        packet += [self.export(a) for a in args]
        self.system.send(self.pe, k, packet)

    def export(self, w):
        """Level 0: a word of a message for the argument w."""
        d = pimm.Machine.deref(self, w)
        if d[0] & ~1 in (INT, ATOM):
            return (d[0] & ~1, d[1])
        if self.unbound(d):
            e = self.next_export
            self.next_export += 1
            self.exports[e] = d
            return (EXREF | (d[0] & 1), ext_id(self.pe, e))
        raise Unimplemented('exporting %r (rung M2)' % (d,))

    def receive(self, src, packet):
        kind = packet[0][1]
        sh = self.shoen
        self.shoen = 0              # a message is decoded at the root
        try:
            if kind == M_THROW:
                n = packet[THROW_ARGS - 1][1]
                code = packet[10][1] - self.load
                args = [self.import_word(w) for w in packet[THROW_ARGS:THROW_ARGS + n]]
                self.record(pimm.READY, code, args)
                self.event('N throw %d %d' % (src, code))
            elif kind == M_UNIFY:
                ref, val = packet[7], packet[8]
                pe, e = ref[1] >> 24, ref[1] & 0xfffff
                assert pe == self.pe, (pe, self.pe)
                if e not in self.exports:
                    raise Unimplemented('%%unify to a released export entry %d' % e)
                var = self.exports.pop(e)
                self.event('N unify %d %d' % (src, e))
                self.unify(var, val)
            else:
                raise Unimplemented('message kind %d' % kind)
        finally:
            self.shoen = sh

    def import_word(self, w):
        if w[0] & ~1 in (INT, ATOM):
            return w
        if w[0] in (EXREF, EXREF | 1):
            if w[1] >> 24 == self.pe:
                raise Unimplemented('a reference coming home (rung M2)')
            e = self.next_import
            self.next_import += 1
            self.imports[e] = w[1]
            a = self.alloc(1)
            self.mem[a] = (w[0], e)
            return (REF, a)
        raise Unimplemented('importing %r' % (w,))

    # ---- external cells ---------------------------------------------
    def deref(self, w):
        d = pimm.Machine.deref(self, w)
        if d[0] in EX_TAGS and not self.ex_ok:
            raise Unimplemented('reading an external reference (%%read, rung M2) at %d'
                                % getattr(self, 'pc', -1))
        return d

    def unify(self, a, b):
        da, db = pimm.Machine.deref(self, a), pimm.Machine.deref(self, b)
        if da[0] not in EX_TAGS and db[0] not in EX_TAGS:
            return pimm.Machine.unify(self, a, b)
        if db[0] in EX_TAGS:
            da, db = db, da
        if db[0] in EX_TAGS or db[0] & ~1 not in (INT, ATOM):
            raise Unimplemented('unify of %r and %r (rung M2)' % (da, db))
        ident = self.imports.pop(da[1], None)
        if ident is None:
            raise Unimplemented('a second unification of external cell %r' % (da,))
        self.system.send(self.pe, ident >> 24,
                         [(INT, M_UNIFY), (INT, 0), (INT, 0), (INT, 0), (INT, 0),
                          (INT, 0), (INT, self.system.n),
                          (EXREF, ident), (db[0] & ~1, db[1])])


def dumps(machine):
    """The machine pickled with longrun_ipl's pickler (its memory and
    registers trace their writes through .machine)."""
    import longrun_ipl
    f = io.BytesIO()
    longrun_ipl._pickler(f).dump(machine)
    return f.getvalue()


class System:
    """N PEs and the network between them."""

    def __init__(self, machine, n):
        """machine: a pimm.Machine with the code loaded, or dumps() of
        one; copied to every PE (OURS, docs/multi_pe.md 3)."""
        blob = machine if isinstance(machine, bytes) else dumps(machine)
        self.n = n
        self.pes = []
        for k in range(n):
            m = pickle.loads(blob)
            m.__class__ = PE
            m.setup(self, k)
            self.pes.append(m)
        self.queues = {(s, d): deque() for s in range(n) for d in range(n) if s != d}
        self.log = []               # ('gc', pe), ('send', kind, src, dst), in order
        self.sent = {}              # kind -> count

    def send(self, src, dst, packet):
        self.queues[(src, dst)].append(packet)
        kind = packet[0][1]
        self.sent[kind] = self.sent.get(kind, 0) + 1
        self.log.append(('send', kind, src, dst))

    def deliver(self, pe):
        for s in range(self.n):
            if s != pe.pe:
                q = self.queues[(s, pe.pe)]
                while q:
                    pe.receive(s, q.popleft())

    def run(self, quota=1, limit=10 ** 8):
        """Run every PE until no PE has a goal and no message is in
        flight.  Returns the goal switches each PE made."""
        switches = [0] * self.n
        while True:
            busy = False
            for pe in self.pes:
                for _ in range(quota):
                    self.deliver(pe)
                    if not pe.goal_switch(limit):
                        break
                    switches[pe.pe] += 1
                    busy = True
            if not busy and not any(self.queues.values()):
                break
        for pe in self.pes:
            pe.shoen = 0
            pe.event('Q')
        return switches
