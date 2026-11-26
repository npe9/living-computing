#!/usr/bin/env python3
"""PIM/m with more than one PE, on the reference model: rungs M1 to M3.

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
  tagtbl.kl1 32h-35h), M92's MRB-off and MRB-on tables (INFERENCE).
  Rung M3: MRB off is WHITE, a new entry per export, given back by
  exactly one %unify or %release; MRB on is BLACK (VPIM
  f_Put_*Group_inLogicalPacket: s_IfMRBoff white, else black): one
  entry per exported address, each ID sent with WEC_UNIT of WEC
  (VPIM D_EXPORT_WEC_UNIT, the entry's WEC going negative), the ID
  word tagged with the low bit on and followed by an INT word of WEC
  (INFERENCE that the x tags are the black IDs); the WEC comes back
  with %read (half the importer's), %unify (all), %release (all) and
  an ID coming home, and the entry is reclaimed at 0 (TM-1044 9).
  An imported ID passed on (VPIM f_Put_EX_inLogicalPacket_Sub): white
  on a white path goes itself and the import is given up (the release
  export); white on a black path is exported again (an indirect
  export, black); black gives half its WEC, all of it on a white path
  with no read pending to an ID imported once (the import given up),
  and is exported again when its WEC cannot be halved.  A black ID
  received again adds its WEC to the one import of it (TM-1044 9: the
  black import table hashed by ID) and marks it imported more than
  once (VPIM's import flag).  OURS: a %read always keeps the import and
  takes half the WEC (VPIM takes all of it on a white path to a single
  import), and a %unify always takes all of it and gives the import up
  (VPIM half on a black path), the cell becoming the value here.
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
  exported, take the pointer to it"); a white entry is then done with
  (its importer gave the import up passing the ID on, the release
  export), a black one has the WEC back.
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

- A collection on a PE (PECollector, pimm_gc's own with two hooks):
  the export table is a root, the import table weak; an import whose
  external cell was not reached is released (all its WEC with it).
  An exported variable's cell is retagged EUNDF (unbound) or EHOOK
  (goals waiting) while an entry holds it (TM-1044 s9-msg-kl1data.tex
  269-300), and plain again when its last entry is freed unbound
  (OURS).  EMHOK is not modelled.

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
import pimm_gc  # noqa: E402
from pimm import (INT, ATOM, REF, UNDF, HOOK, LIST, STRG, CDESC, VECT0,  # noqa: E402
                  Unimplemented, sx16)
from pimm_layout import G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS, SUSPENDED, TAKEN, HEAP  # noqa: E402

# external cells and IDs (debugger/inspector/tagtbl.kl1): o = MRB off
EXREF, EXREFx, EXVAL, EXVALx = 0x32, 0x33, 0x34, 0x35
EX_TAGS = (EXREF, EXREFx, EXVAL, EXVALx)
# an exported variable (TM-1044 s9-msg-kl1data.tex 269-300; tagtbl.kl1
# 2Ah-2Dh): EUNDF unbound, EHOOK with goals waiting
EUNDF, EUNDFx, EHOOK, EHOOKx = 0x2A, 0x2B, 0x2C, 0x2D
E_TAGS = (EUNDF, EUNDFx, EHOOK, EHOOKx)
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
# the WEC a black export gives each ID it sends (VPIM
# D_EXPORT_WEC_UNIT; TR-390 7: 2^24)
WEC_UNIT = 1 << 24


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
    VAR_TAGS = pimm.Machine.VAR_TAGS + (EUNDF, EHOOK)

    def setup(self, system, pe):
        self.system = system
        self.pe = pe
        self.exports = {}           # entry -> the exported word
        self.next_export = 1        # entries are never reused
        self.wec = {}               # black entry -> its WEC (negative: what it gave out)
        self.black = {}             # (tag, address) of a black entry's word -> entry
        self.imports = {}           # entry -> {'id', 'cell', 'read', 'tag', 'black', 'wec'}
        self.bimports = {}          # ID -> the black import of it
        self.next_import = 1
        self.roots = {}             # words a bench holds: roots of the collector
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
            self.collections += 1
            self.system.log.append(('gc', self.pe))
        return pimm.Machine.goal_switch(self, limit)

    def collect(self):
        """A collection now (a bench's, at quiescence), by PECollector."""
        self.collections += 1
        self.system.log.append(('gc', self.pe))
        return pimm_gc.collect(self)

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

    def new_export(self, w, black=False):
        """An ID for w.  White: a new entry.  Black: the entry of w's
        address if there is one, else a new one; WEC_UNIT more given
        out (VPIM s_AllocBlackExpEntry_Sub, f_GetLogicalPacketData_B_*)."""
        if black and key(w) in self.black:
            e = self.black[key(w)]
            self.ran('black entry again')
        else:
            e = self.next_export
            self.next_export += 1
            self.exports[e] = w
            if black:
                self.black[key(w)] = e
                self.wec[e] = 0
            self.retag(w)
        if black:
            self.wec[e] -= WEC_UNIT
        return ext_id(self.pe, e)

    def free_export(self, e):
        w = self.exports.pop(e)
        if e in self.wec:
            del self.wec[e]
            del self.black[key(w)]
        self.untag(w)

    def retag(self, w):
        """An exported variable's cell: UNDF to EUNDF, HOOK to EHOOK
        (TM-1044 9: the cell's type changes and a pointer to it goes in
        the export table)."""
        if w[0] & ~1 == REF:
            c = self.mem[w[1]]
            if c[0] == UNDF:
                self.mem[w[1]] = (EUNDF, 0)
            elif c[0] & ~1 == HOOK:
                self.mem[w[1]] = (EHOOK, c[1])

    def untag(self, w):
        """Its last entry freed, an exported variable still unbound is
        a plain one again (OURS: when the machine did this is not held)."""
        if w[0] & ~1 == REF and self.mem[w[1]][0] in E_TAGS:
            if any(key(v) == key(w) for v in self.exports.values()):
                return
            c = self.mem[w[1]]
            self.mem[w[1]] = (UNDF, 0) if c[0] & ~1 == EUNDF else (HOOK, c[1])

    def give_back(self, e, wec):
        """WEC returned to black entry e; reclaimed at 0 (TM-1044 9)."""
        if e not in self.wec:
            self.system.anomalies.append(('WEC returned to a white or free entry', self.pe, e))
            return
        self.wec[e] += wec
        if self.wec[e] > 0:
            self.system.anomalies.append(('more WEC returned than given', self.pe, e))
        elif self.wec[e] == 0:
            self.ran('black entry reclaimed')
            self.free_export(e)

    def drop_import(self, imp):
        ent = self.imports.pop(imp)
        if ent['black']:
            del self.bimports[ent['id']]
        return ent

    def black_export(self, tag, d):
        return [(tag | 1, self.new_export(d, black=True)), (INT, WEC_UNIT)]

    def forward(self, d, mrb, dst):
        """An external cell at level 0 (VPIM f_Put_EX_inLogicalPacket_Sub)."""
        cell = self.mem[d[1]]
        ent = self.imports[cell[1]]
        kind = cell[0] & ~1
        if not ent['black']:
            if not mrb:
                # a white path: the ID itself goes and the import with it
                # (the release export)
                self.ran('white ID passed on')
                self.drop_import(cell[1])
                return [(kind, ent['id'])]
            self.ran('indirect export')
            return self.black_export(kind, d)
        if not mrb and ent['read'] is None and not ent['multi']:
            # a white path to a black ID imported once
            # (s_GetExrefIdAllWecAndReclaimBImpRec_Sub: s_IfSingleImport)
            self.ran('black ID passed on, all its WEC')
            self.drop_import(cell[1])
            return [(kind | 1, ent['id']), (INT, ent['wec'])]
        if ent['wec'] >= 2:
            self.ran('black ID passed on, half its WEC')
            if not mrb and ent['read'] is None:
                self.ran('multi-import: half')
            half = ent['wec'] >> 1
            ent['wec'] -= half
            return [(kind | 1, ent['id']), (INT, half)]
        self.ran('indirect export, no WEC to give')
        return self.black_export(kind, d)

    def level0(self, w, dst):
        """The words of a message for w at level 0, sent to PE dst."""
        d = self.deref(w)
        t, mrb = d[0] & ~1, d[0] & 1
        if t in (INT, ATOM, VECT0):
            return [(t, d[1])]
        if self.is_ex(d):
            return self.forward(d, mrb, dst)
        if self.unbound(d):
            tag = EXREF
        elif t == LIST or t == STRG or self.vsize(d) is not None:
            tag = EXVAL
        else:
            raise Unimplemented('exporting %r' % (d,))
        if mrb:
            self.ran('black export')
            return self.black_export(tag, d)
        return [(tag, self.new_export(d))]

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
            if ent['black']:
                # half its WEC goes with it (VPIM f_GetExrefIdAndWec_forRead_BEX)
                half = ent['wec'] >> 1
                ent['wec'] -= half
                pk = [(INT, M_READ), (cell[0], ent['id']), (INT, half), (EXREF, rid)]
            else:
                pk = [(INT, M_READ), (cell[0], ent['id']), (EXREF, rid)]
            self.send(id_pe(ent['id']), pk)
        return ent['read']

    def send_release(self, ent):
        """%release of an import (dropped): {8, ID}, black {8, ID, WEC}."""
        pk = [(INT, M_RELEASE), (ent['tag'], ent['id'])]
        if ent['black']:
            pk.append((INT, ent['wec']))
        self.send(id_pe(ent['id']), pk)

    def send_unify(self, cell_addr, v):
        """A unification of the external cell with v (not a variable of
        this PE): %unify to the owner; the cell is v here."""
        cell = self.mem[cell_addr]
        ent = self.drop_import(cell[1])
        dst = id_pe(ent['id'])
        # a black ID takes all its WEC with it (VPIM f_GetExrefIdAndWec_forUnify1_BEX)
        self.send(dst, [(INT, M_UNIFY), (INT, 0), (INT, 0), (INT, 0), (INT, 0),
                        (INT, 0), (INT, self.system.n), (cell[0], ent['id'])]
                  + ([(INT, ent['wec'])] if ent['black'] else [])
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
        # variable (or on the external cell, which reads it in turn);
        # the reply ID, always white, kept as an integer, so that the
        # only ID words in a heap are external cells (OURS)
        g = self.alloc(G_ARGS + 2)
        self.mem[g + G_LINK] = (INT, 0)
        self.mem[g + G_STATUS] = (INT, SUSPENDED)
        self.mem[g + G_CODE] = (INT, 0)
        self.mem[g + G_ARGN] = (INT, 2)
        self.mem[g + G_ARGS] = d
        self.mem[g + G_ARGS + 1] = (INT, reply[1])
        self.nsusp += 1
        self.hook(g, d[1])

    # ---- receiving -----------------------------------------------------
    def get0(self, pk, i):
        """A level-0 word of a message at pk[i]: (the word here, next i)."""
        w = pk[i]
        if w[0] & ~1 in (INT, ATOM, VECT0):
            return w, i + 1
        if w[0] in EX_TAGS:
            black = w[0] & 1
            wec, j = (pk[i + 1][1], i + 2) if black else (None, i + 1)
            if id_pe(w[1]) == self.pe:
                # an ID of ours: the word its entry holds (VPIM
                # f_Get_WExRef_fromLogicalPacket_Sub); a white entry is
                # done with (its importer passed it on), a black one has
                # the WEC back
                e = id_entry(w[1])
                if e not in self.exports:
                    raise Unimplemented('an ID of a released export entry %d came home' % e)
                word = self.exports[e]
                if black:
                    self.ran('black ID came home')
                    self.give_back(e, wec)
                else:
                    self.ran('white ID came home')
                    self.free_export(e)
                return word, j
            if black and w[1] in self.bimports:
                # one import per black ID (TM-1044 9: the black import
                # table hashed by ID), its WEC summed
                # and its import flag on, multi-import (VPIM
                # s_SetMultiImportFlagBImpRec): more than one reference
                # to the one cell now
                self.ran('black ID imported again')
                ent = self.bimports[w[1]]
                ent['wec'] += wec
                ent['multi'] = True
                return (REF, ent['cell']), j
            return self.import_id(w, wec), j
        raise Unimplemented('importing %r' % (w,))

    def import_id(self, w, wec=None):
        e = self.next_import
        self.next_import += 1
        a = self.alloc(1)
        self.mem[a] = (w[0], e)
        self.imports[e] = {'id': w[1], 'cell': a, 'read': None, 'tag': w[0],
                           'black': wec is not None, 'wec': wec, 'multi': False}
        if wec is not None:
            self.bimports[w[1]] = self.imports[e]
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
                w = packet[UNIFY_ARG1]
                e = self.own_entry(w, 'unify')
                var = self.exports[e]
                if w[0] & 1:
                    val, _ = self.get1(packet, UNIFY_ARG1 + 2)
                    self.give_back(e, packet[UNIFY_ARG1 + 1][1])
                else:
                    self.free_export(e)
                    val, _ = self.get1(packet, UNIFY_ARG1 + 1)
                self.event('N unify %d %d' % (src, e))
                self.unify(var, val)
            elif kind == M_READ:
                e = self.own_entry(packet[1], 'read')
                self.event('N read %d %d' % (src, e))
                if packet[1][0] & 1:
                    self.reply_when_bound(self.exports[e], packet[3])
                    self.give_back(e, packet[2][1])
                else:
                    self.reply_when_bound(self.exports[e], packet[2])
            elif kind == M_ANSWER:
                e = self.own_entry(packet[1], 'answer_value')
                v = self.exports[e]
                self.free_export(e)
                imp = self.reading.pop(e)
                val, _ = self.get1(packet, 2)
                self.event('N answer %d %d' % (src, e))
                ent = self.drop_import(imp) if imp in self.imports else None
                self.ran('answer, import %s' % ('kept' if ent is not None else 'given up'))
                if ent is not None:             # not given up by a %unify
                    self.mem[ent['cell']] = v
                    self.send_release(ent)
                self.unify(v, val)
            elif kind == M_RELEASE:
                e = id_entry(packet[1][1])
                assert id_pe(packet[1][1]) == self.pe
                if e not in self.exports:
                    self.system.anomalies.append(('release of a free entry', self.pe, e))
                elif packet[1][0] & 1:
                    self.give_back(e, packet[2][1])
                elif e in self.wec:
                    self.system.anomalies.append(('white release of a black entry', self.pe, e))
                else:
                    self.free_export(e)
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
            if c[0] == UNDF or c[0] & ~1 == HOOK or c[0] in EX_TAGS or c[0] in E_TAGS:
                break
            w = c
        return pimm.marked(w) if on else w

    def hook(self, g, var):
        if self.mem[var][0] in EX_TAGS:
            var = self.send_read(var)
        c = self.mem[var]
        if c[0] not in E_TAGS:
            return pimm.Machine.hook(self, g, var)
        # an exported variable: hooked as a plain one, the tag kept
        self.mem[var] = (UNDF, 0) if c[0] & ~1 == EUNDF else (HOOK, c[1])
        pimm.Machine.hook(self, g, var)
        self.mem[var] = (EHOOK, self.mem[var][1])

    def bind(self, ref, w):
        c = self.mem[ref[1]]
        if c[0] & ~1 == EHOOK:
            # its goals woken as a plain variable's are (TM-1044: an
            # EHOOK is a HOOK that is exported)
            self.mem[ref[1]] = (HOOK, c[1])
        return pimm.Machine.bind(self, ref, w)

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
        self.answer((EXREF, self.mem[g + G_ARGS + 1][1]), d)

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


def key(w):
    """A black entry's key: its word's tag (MRB off) and address."""
    return (w[0] & ~1, w[1])


class PECollector(pimm_gc.Collector):
    """pimm_gc's collector on a PE: the export table a root (TR-466
    3.2; TM-1044 9), an external cell a one-word datum that moves into a
    structure copied after it as a variable does, and the import table
    weak: an import whose cell was not reached is released, all its
    WEC with it if black (OURS: when and how VPIM's collector
    releases imports was not read).  What a
    bench holds (PE.roots) is a root too, and the suspended goals are
    counted again from the copy."""
    VAR_TAGS = pimm_gc.Collector.VAR_TAGS + (EXREF, EXVAL, EUNDF, EHOOK)

    def word(self, w):
        if w[0] in EX_TAGS or w[0] & ~1 == EUNDF:
            return w
        if w[0] & ~1 == EHOOK:
            return (w[0], self.susp(w[1]))
        return pimm_gc.Collector.word(self, w)

    def more_roots(self):
        pe = self.m
        for e in sorted(pe.exports):
            pe.exports[e] = self.word(pe.exports[e])
        for k in sorted(pe.roots):
            pe.roots[k] = self.word(pe.roots[k])

    def after_scan(self):
        pe = self.m
        for imp in sorted(pe.imports):
            ent = pe.imports[imp]
            f = self.fwd(ent['cell'])
            if f is not None:
                ent['cell'] = f
                if ent['read'] is not None:
                    ent['read'] = self.fwd(ent['read'])
            else:
                pe.ran('import released at a collection')
                pe.send_release(pe.drop_import(imp))
        pe.black = {key(pe.exports[e]): e for e in pe.wec}
        n, p = 0, self.to
        while p < self.top:
            t, v = self.get(p)
            if t == pimm_gc.GCHDR:
                if v >> 24 == pimm_gc.K_GOAL and self.get(p + 1 + G_STATUS)[1] & 3 == SUSPENDED:
                    n += 1
                p += 1 + (v & 0xffffff)
            elif t == CDESC and (v >> 24) & 7 != 6:
                p += 1 + (v & 0xffffff)
            else:
                p += 1
        pe.nsusp = n


PE.Collector = PECollector


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
