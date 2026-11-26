#!/usr/bin/env python3
"""PIM/m with more than one PE, on the reference model: rungs M1 and M2.

docs/multi_pe.md is the plan and the evidence; every choice below is
labelled there.  In brief:

- A System holds N PEs.  Each PE is a pimm.Machine of its own (its own
  memory, heap, registers, ready queue): PIM/m has one memory per PE
  (M92 p. 430).  The PEs are made by copying one loaded machine, so a
  code address means the same on every PE (OURS scaffolding; PIM/m
  sends a module's global identifier and fetches it, M92 pp. 430-431).
  After a PE has collected, its modules have moved: a goal thrown from
  or to it with code in the heap is refused (rung M5, code fetch).
- current_node gives (k, N) on PE k (PIMOS manual e-builtin.tex
  current_node).  current_processor gives (k, N, 1): PIMOS's
  mdlib#current_cluster(Cluster, Total) is current_processor(Cluster,
  X, Y), Total := X*Y on Multi-PSI and PIM/m (pimos.vmac 378-381,
  HELD-SOURCE); N = N x 1 is OURS.  unbound/2 gives {k, Address, X}
  (VPIM kblt_b_unbound, the cluster number); of an external reference
  VPIM throws a goal to its owner: refused.
- Goal@node(K) (enqueue_goal_to_processor, 23:65; PIMOS compiler
  newnorm.kl1:842-905) with K this PE makes the goal here; with K
  another PE it sends %throw_goal (VPIM's cluster branch, klb_fork.psl.c
  1069-1075, docs/multi_pe.md 1.3).  An atom or a number out of range is
  an exception on PIM/m (illegal_input, range_overflow, e-shoen.tex
  486-514), not modelled: refused.  A node that is a variable waits for
  it (to_processor, the stub), then the goal goes there.
- The arguments of a thrown goal are copied at level 0 (TM-1044 9.2;
  VPIM f_int_cl_msg_type.psl.c section 4): an integer, an atom or the
  null vector as it is; anything else is EXPORTED, an entry of this
  PE's export table holding the word, and sent as an external
  reference ID {tag, pe << 24 | entry} (8-bit cluster, 4 flag bits,
  20-bit offset): an unbound variable as EXREF, a list, vector or
  string as EXVAL (VPIM f_GetLogicalPacketData_W_StructureGroup:
  WEXVAL; ..._W_UnboundGroup: WEXREF).  The tag's low bit is the MRB
  of the path (EXREFo/x, EXVALo/x, PIMOS debugger/inspector/
  tagtbl.kl1 32h-35h), M92's MRB-off and MRB-on tables (INFERENCE);
  at M2 both are handled alike, one entry per export, never reused.
- Level 1 (the value of %unify and %answer_value, TM-1044 9.2): the
  structure itself, its elements at level 0 (VPIM f_int_cl_msg_type
  section 4 (3): LISTo then car and cdr; VECTn then the elements; a
  long vector VECTo, its length, the elements); a string as STRG, its
  descriptor and words (OURS: VPIM's table says "undecided").
- The receiver IMPORTS an external reference ID: an import entry
  holding the ID (TM-1044 s9.tex:199-215; here a table of the PE,
  outside the heap, as the import tables are in the system's fixed
  area there, OURS that it is not in memory cells) and a one-word
  external cell {EXREF.. or EXVAL.., entry} in the heap; what refers to
  it is always a reference to that cell, never the cell's word (so a
  structure's element cell is never an external cell).  An ID of the
  receiver's own coming home resolves to the word its export entry
  holds (VPIM f_Get_WExRef_fromLogicalPacket_Sub: "if it is data we
  exported, take the pointer to it"); the entry is kept, the sender
  still holding its import (OURS: VPIM reclaims it there, its sender
  having released its import, the release export).
- An external cell looks unbound to the machine (deref stops at it).
  A goal that waits on one (any suspension: a guard, a waiting
  built-in, a variable node) sends %read once, {6, the ID, the reply
  ID}: a fresh variable V of the reader is exported for the reply and
  the waiters hook on V (VPIM f_int_cl_send_read.psl.c, the read with
  the import kept, RDHOK: OURS that this is the only way, and that V
  is a plain variable; the RDHOK tag is not in PIMOS's table).  The
  owner of the ID answers at once if the data is bound, else when it
  is (VPIM f_int_cl_recv_read.psl.c: a reply record, RHOOK, hooked on
  the variable; here a goal record with no code, G_CODE 0, hooked
  as any goal is, whose waking sends the answer: OURS, so the one-PE
  hook, wake and collection code serves it).  %answer_value {7, the
  reply ID, the value at level 1} binds V, the external cell is made a
  reference to V, and the import is given back with %release {8, the
  ID} (VPIM f_ReceiveAnswerValue_Body, case RDHOK: "if an import
  record hangs off the read hook, send %release").
- A unification of an external cell: with an unbound variable of this
  PE, the variable is made a reference to the cell (VPIM
  f_Send_IntClMsg_Unify_Sub (1)); with anything else, %unify {9,
  shoen, WTC, priority, profiling, minimum node, node count, the ID,
  the value at level 1} to the owner (f_int_cl_recv_unify.psl.c 9-35),
  and the import is given up with it; the cell is then the value here.
  Each export entry so gets exactly one %unify or %release (OURS).
- Messages are VPIM's logical packets, one word per item, the fields
  not modelled sent as 0 (f_int_cl_send_throw_goal.psl.c 15-60); the
  kind codes are the Pseudo PIM/m console's (pimmcsp.ptf
  kl1_message_order_macro: m_throw 0, m_read 6, m_answer_value 7,
  m_release 8, m_unify 9).  Each ordered pair of PEs is a FIFO (TR-390
  3.1); a PE decodes the messages waiting for it at a goal switch,
  before its next goal (TR-715 3.3), from the lower-numbered sender
  first (OURS).
- The PEs run in turn, PE 0 first, each for a quota of goal switches
  (the console's roundrobin_scheduler, INFERENCE as to the unit).

Goals of the root only (no shoen): a throw from inside a shoen is
refused (rung M4).  A collection with a live export or import is
refused (rung M3).  The PE classes never change a single machine:
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
from pimm import (INT, ATOM, REF, UNDF, HOOK, LIST, STRG, CDESC, VECT0,  # noqa: E402
                  Unimplemented, sx16)
from pimm_layout import G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS, SUSPENDED, TAKEN, HEAP  # noqa: E402

# external cells and IDs (debugger/inspector/tagtbl.kl1): o = MRB off
EXREF, EXREFx, EXVAL, EXVALx = 0x32, 0x33, 0x34, 0x35
EX_TAGS = (EXREF, EXREFx, EXVAL, EXVALx)
# message kinds: the Pseudo PIM/m console's codes (docs/multi_pe.md 1.1),
# the same as VPIM's _NW_ numbering
M_THROW, M_READ, M_ANSWER, M_RELEASE, M_UNIFY = 0, 6, 7, 8, 9
KIND_NAMES = {M_THROW: 'throw', M_READ: 'read', M_ANSWER: 'answer_value',
              M_RELEASE: 'release', M_UNIFY: 'unify'}
# where the arguments start in a %throw_goal packet (VPIM's fields 1-15),
# and %unify's first argument (its fields 1-6 before it)
THROW_ARGS = 15
UNIFY_ARG1 = 7
LONG_VECT = VECT0 + 14


def ext_id(pe, entry):
    if not (0 <= pe < 256 and 0 < entry < 1 << 20):
        raise Unimplemented('an external reference ID out of range: PE %d, entry %d' % (pe, entry))
    return pe << 24 | entry


def id_pe(ident):
    return ident >> 24


def id_entry(ident):
    return ident & 0xfffff


class PE(pimm.Machine):
    """One processing element.  Made by System from a loaded machine."""

    def setup(self, system, pe):
        self.system = system
        self.pe = pe
        self.exports = {}           # entry -> the exported word
        self.next_export = 1        # entries are never reused
        self.imports = {}           # entry -> {'id', 'cell', 'read'}
        self.next_import = 1
        self.reading = {}           # reply export entry -> import entry
        self.collections = 0
        self.heap_log = []          # get_heap_size: (size, used), in order
        self.paths = {}             # which paths ran, for the tests (not machine state)

    def ran(self, path):
        self.paths[path] = self.paths.get(path, 0) + 1

    # ---- what a PE knows of the others ------------------------------
    def i_current_node(self, pc, x, y, z, c16):
        self.reg[x] = (INT, self.pe)
        self.reg[y] = (INT, self.system.n)

    def i_current_processor(self, pc, x, y, z, c16):
        # current_processor(^Cluster, ^X, ^Y): Cluster this node, X * Y
        # the number of nodes (pimos.vmac mdlib#current_cluster); N x 1
        # is OURS
        self.reg[x] = (INT, self.pe)
        self.reg[y] = (INT, self.system.n)
        self.reg[z] = (INT, 1)

    def i_unbound(self, pc, x, y, z, c16):
        v = self.deref(self.reg[x])
        if self.is_ex(v):
            raise Unimplemented('unbound/2 of an external reference (VPIM throws it to the owner)')
        if self.unbound(v):
            w, a = self.vnew(3)
            self.mem[a], self.mem[a + 1], self.mem[a + 2] = (INT, self.pe), (INT, v[1]), v
        else:
            w, a = self.vnew(1)
            self.mem[a] = v
        self.reg[y] = w

    def i_get_heap_size(self, pc, x, y, z, c16):
        # get_heap_size(^Size, ^Used), 22:FE r_r (inst_tab.kl1:370;
        # blt.kl1:672: two outputs): "the memory usage state for the node
        # on which the predicate is running ... in word units ... on
        # Multi-PSI and PIM/m" (e-builtin.tex get_heap_size, PRINTED);
        # Size "the size of one half of the copying collector's heap"
        # (VPIM klb_pimos.psl.c:157-158).  Here: half of the cells from
        # the heap's first cell to the end of memory, and the cells from
        # the heap in use's first cell to the heap pointer (OURS).  On
        # the PEs only: not a one-machine instruction of this model.
        size = (self.size - HEAP) // 2
        used = self.hp - (getattr(self, 'heap_lo', None) or self.load + HEAP)
        self.heap_log.append((size, used))
        self.reg[x] = (INT, size)
        self.reg[y] = (INT, used)

    # ---- collect_garbage asks; the collection is at the goal switch --
    def i_collect_garbage(self, pc, x, y, z, c16):
        self.system.log.append(('ask', self.pe))
        return pimm.Machine.i_collect_garbage(self, pc, x, y, z, c16)

    def goal_switch(self, limit):
        if self.gc_request:
            if self.exports or self.imports:
                # the tables would be roots of the collector (TR-466
                # 3.2): rung M3
                raise Unimplemented('a collection with %d live exports, %d imports'
                                    % (len(self.exports), len(self.imports)))
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

    # ---- sending -----------------------------------------------------
    def send(self, dst, packet):
        self.system.send(self.pe, dst, packet)

    def throw(self, k, code, args):
        if self.shoen:
            raise Unimplemented('a goal thrown from inside a shoen (rung M4)')
        if self.collections and code >= HEAP:
            raise Unimplemented('a goal thrown after a collection moved its module (rung M5)')
        packet = [(INT, M_THROW), (INT, 0), (INT, 0), (INT, 0), (INT, 0), (INT, 0),
                  (INT, 0), (INT, 0), (INT, self.system.n), (INT, 0),
                  (pimm.COD, self.load + code), (INT, 0), (INT, 0), (INT, 0),
                  (INT, len(args))]
        assert len(packet) == THROW_ARGS
        for a in args:
            packet += self.level0(a, k)
        self.send(k, packet)

    def is_ex(self, d):
        """d (dereferenced) is a reference to an external cell."""
        return d[0] & ~1 == REF and self.mem[d[1]][0] in EX_TAGS

    def new_export(self, w):
        e = self.next_export
        self.next_export += 1
        self.exports[e] = w
        return ext_id(self.pe, e)

    def level0(self, w, dst):
        """The words of a message for w at level 0, sent to PE dst."""
        d = self.deref(w)
        t, mrb = d[0] & ~1, d[0] & 1
        if t in (INT, ATOM, VECT0):
            return [(t, d[1])]
        if self.is_ex(d):
            cell = self.mem[d[1]]
            ent = self.imports[cell[1]]
            if id_pe(ent['id']) == dst:
                self.ran('goes home')
                return [(cell[0] & ~1, ent['id'])]            # it goes home
            self.ran('indirect export')
            return [(cell[0] & ~1 | mrb, self.new_export(d))]  # an indirect export
        if self.unbound(d):
            return [(EXREF | mrb, self.new_export(d))]
        if t == LIST or t == STRG or self.vsize(d) is not None:
            return [(EXVAL | mrb, self.new_export(d))]
        raise Unimplemented('exporting %r' % (d,))

    def level1(self, w, dst):
        """The words of a message for w at level 1."""
        d = self.deref(w)
        t = d[0] & ~1
        if self.unbound(d) or t in (INT, ATOM, VECT0):
            return self.level0(d, dst)
        self.ran('level 1 %s' % ('list' if t == LIST else 'string' if t == STRG
                                 else 'long vector' if t == LONG_VECT else 'vector'))
        if t == LIST:
            return ([(LIST, 0)] + self.level0(self.taken(d[1]), dst)
                    + self.level0(self.taken(d[1] + 1), dst))
        if t == STRG:
            desc = self.mem[d[1]]
            if desc[0] != CDESC:
                raise Unimplemented('a string without a descriptor')
            return [(STRG, 0), desc] + [self.mem[d[1] + 1 + i] for i in range(desc[1] & 0xffffff)]
        n = self.vsize(d)
        if n is None:
            raise Unimplemented('exporting %r at level 1' % (d,))
        out = [(LONG_VECT, 0), (INT, n)] if t == LONG_VECT else [(t, 0)]
        b = self.vbase(d)
        for i in range(n):
            out += self.level0(self.taken(b + i), dst)
        return out

    def send_read(self, cell_addr):
        """The first waiter on an external cell: %read, once; the
        address of the variable the waiters hook on."""
        cell = self.mem[cell_addr]
        imp = cell[1]
        ent = self.imports[imp]
        if ent['read'] is None:
            v = self.new_var()
            rid = self.new_export(v)
            self.reading[id_entry(rid)] = imp
            ent['read'] = v[1]
            self.send(id_pe(ent['id']), [(INT, M_READ), (cell[0], ent['id']), (EXREF, rid)])
        return ent['read']

    def send_release(self, ident, tag):
        self.send(id_pe(ident), [(INT, M_RELEASE), (tag, ident)])

    def send_unify(self, cell_addr, v):
        """A unification of the external cell with v (not a variable of
        this PE): %unify to the owner; the cell is v here."""
        cell = self.mem[cell_addr]
        ent = self.imports.pop(cell[1])
        dst = id_pe(ent['id'])
        self.send(dst, [(INT, M_UNIFY), (INT, 0), (INT, 0), (INT, 0), (INT, 0),
                        (INT, 0), (INT, self.system.n), (cell[0], ent['id'])]
                  + self.level1(v, dst))
        if ent['read'] is not None:
            self.ran('unify with a read pending')
            self.mem[cell_addr] = (REF, ent['read'])
            self.unify((REF, ent['read']), v)
        else:
            self.mem[cell_addr] = v

    def answer(self, reply, w):
        """%answer_value of the bound w to the reader whose reply ID is
        reply."""
        dst = id_pe(reply[1])
        self.send(dst, [(INT, M_ANSWER), reply] + self.level1(w, dst))

    def reply_when_bound(self, w, reply):
        d = self.deref(w)
        if not self.unbound(d):
            self.ran('answer at once')
            return self.answer(reply, d)
        self.ran('reply record')
        # a reply record: a goal record with no code, hooked on the
        # variable (or on the external cell, which reads it in turn)
        g = self.alloc(G_ARGS + 2)
        self.mem[g + G_LINK] = (INT, 0)
        self.mem[g + G_STATUS] = (INT, SUSPENDED)
        self.mem[g + G_CODE] = (INT, 0)
        self.mem[g + G_ARGN] = (INT, 2)
        self.mem[g + G_ARGS] = d
        self.mem[g + G_ARGS + 1] = reply
        self.nsusp += 1
        self.hook(g, d[1])

    # ---- receiving -----------------------------------------------------
    def get0(self, pk, i):
        """A level-0 word of a message at pk[i]: (the word here, next i)."""
        w = pk[i]
        if w[0] & ~1 in (INT, ATOM, VECT0):
            return w, i + 1
        if w[0] in EX_TAGS:
            if id_pe(w[1]) == self.pe:
                e = id_entry(w[1])
                if e not in self.exports:
                    raise Unimplemented('an ID of a released export entry %d came home' % e)
                self.ran('came home')
                return self.exports[e], i + 1
            return self.import_id(w), i + 1
        raise Unimplemented('importing %r' % (w,))

    def import_id(self, w):
        e = self.next_import
        self.next_import += 1
        a = self.alloc(1)
        self.mem[a] = (w[0], e)
        self.imports[e] = {'id': w[1], 'cell': a, 'read': None, 'tag': w[0]}
        return (REF, a)

    def get1(self, pk, i):
        """A level-1 value of a message at pk[i]."""
        t = pk[i][0] & ~1
        if t == LIST:
            a = self.alloc(2)
            car, i = self.get0(pk, i + 1)
            cdr, i = self.get0(pk, i)
            self.mem[a], self.mem[a + 1] = car, cdr
            return (LIST, a), i
        if t == STRG:
            desc = pk[i + 1]
            n = desc[1] & 0xffffff
            a = self.alloc(1 + n)
            for k in range(1 + n):
                self.mem[a + k] = pk[i + 1 + k]
            return (STRG, a), i + 2 + n
        if VECT0 + 2 <= t <= LONG_VECT:
            if t == LONG_VECT:
                n, i = pk[i + 1][1], i + 2
            else:
                n, i = (t - VECT0) // 2, i + 1
            w, b = self.vnew(n)
            for k in range(n):
                e, i = self.get0(pk, i)
                self.mem[b + k] = e
            return (w[0] & ~1, w[1]), i
        return self.get0(pk, i)

    def receive(self, src, packet):
        kind = packet[0][1]
        sh = self.shoen
        self.shoen = 0              # a message is decoded at the root
        try:
            if kind == M_THROW:
                if self.collections and packet[10][1] - self.load >= HEAP:
                    raise Unimplemented('a goal thrown to a PE whose modules a collection moved (rung M5)')
                n = packet[THROW_ARGS - 1][1]
                code = packet[10][1] - self.load
                args, i = [], THROW_ARGS
                for _ in range(n):
                    a, i = self.get0(packet, i)
                    args.append(a)
                self.record(pimm.READY, code, args)
                self.event('N throw %d %d' % (src, code))
            elif kind == M_UNIFY:
                e = self.own_entry(packet[UNIFY_ARG1], 'unify')
                var = self.exports.pop(e)
                val, _ = self.get1(packet, UNIFY_ARG1 + 1)
                self.event('N unify %d %d' % (src, e))
                self.unify(var, val)
            elif kind == M_READ:
                e = self.own_entry(packet[1], 'read')
                self.event('N read %d %d' % (src, e))
                self.reply_when_bound(self.exports[e], packet[2])
            elif kind == M_ANSWER:
                e = self.own_entry(packet[1], 'answer_value')
                v = self.exports.pop(e)
                imp = self.reading.pop(e)
                val, _ = self.get1(packet, 2)
                self.event('N answer %d %d' % (src, e))
                ent = self.imports.pop(imp, None)
                self.ran('answer, import %s' % ('kept' if ent is not None else 'given up'))
                if ent is not None:             # not given up by a %unify
                    self.mem[ent['cell']] = v
                    self.send_release(ent['id'], ent['tag'])
                self.unify(v, val)
            elif kind == M_RELEASE:
                e = id_entry(packet[1][1])
                assert id_pe(packet[1][1]) == self.pe
                if self.exports.pop(e, None) is None:
                    self.system.anomalies.append(('release of a free entry', self.pe, e))
                self.event('N release %d %d' % (src, e))
            else:
                raise Unimplemented('message kind %d' % kind)
        finally:
            self.shoen = sh

    def own_entry(self, w, what):
        assert w[0] in EX_TAGS and id_pe(w[1]) == self.pe, (w, self.pe)
        e = id_entry(w[1])
        if e not in self.exports:
            raise Unimplemented('%%%s to a released export entry %d' % (what, e))
        return e

    # ---- external cells ---------------------------------------------
    def deref(self, w):
        """pimm.Machine.deref, stopping at an external cell too: a
        reference to it is what an unbound variable's would be."""
        on = False
        while w[0] & ~1 == REF:
            on = on or bool(w[0] & 1)
            c = self.mem[w[1]]
            if c[0] == UNDF or c[0] & ~1 == HOOK or c[0] in EX_TAGS:
                break
            w = c
        return pimm.marked(w) if on else w

    def hook(self, g, var):
        if self.mem[var][0] in EX_TAGS:
            var = self.send_read(var)
        return pimm.Machine.hook(self, g, var)

    def ready(self, g):
        if self.mem[g + G_CODE][1] != 0:
            return pimm.Machine.ready(self, g)
        # a reply record woken: its variable is bound, or bound to
        # another variable, on which it waits again
        d = self.deref(self.mem[g + G_ARGS])
        if self.unbound(d):
            self.ran('reply record waits again')
            self.mem[g + G_STATUS] = (INT, SUSPENDED)
            self.mem[g + G_ARGS] = d
            self.nsusp += 1
            self.hook(g, d[1])
            return
        self.mem[g + G_STATUS] = (INT, TAKEN)
        self.answer(self.mem[g + G_ARGS + 1], d)

    def unify(self, a, b):
        da, db = self.deref(a), self.deref(b)
        ea, eb = self.is_ex(da), self.is_ex(db)
        if not ea and not eb:
            return pimm.Machine.unify(self, a, b)
        if eb and not ea:
            da, db, eb = db, da, ea
        if eb and da[1] == db[1]:
            return                              # the same external cell
        if self.unbound(db) and not eb:
            self.ran('variable to external cell')
            self.bind(db, da)                   # a variable here points at the cell
            return
        self.send_unify(da[1], db)


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
        self.log = []               # ('gc', pe), ('ask', pe), ('send', kind, src, dst), in order
        self.sent = {}              # kind -> count
        self.anomalies = []         # what a check must find empty

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
