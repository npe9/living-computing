#!/usr/bin/env python3
"""PIM/m with more than one PE, on the reference model: rungs M1 to M5.

docs/multi_pe.md is the plan and the evidence; every choice below is
labelled there.  In brief:

- A System holds N PEs.  Each PE is a pimm.Machine of its own (its own
  memory, heap, registers, ready queue): PIM/m has one memory per PE
  (M92 p. 430).  The PEs are made by copying one loaded machine, so a
  loaded module is at the same address on every PE (OURS scaffolding).
  A code or module word in the heap goes in a message as its module's
  number and offset (CODE_ID, MODULE_ID), each PE taking its own copy
  of that module; one made after the split is fetched, copied from the
  PE that has it (PIM/m sends a module's global identifier and fetches
  it, M92 pp. 430-431; the copy without messages is OURS).  The modules
  a PE has are roots of its collector.
- current_node gives (k, N) on PE k (PIMOS manual e-builtin.tex
  current_node).  current_processor gives (k, N, 1): PIMOS's
  mdlib#current_cluster(Cluster, Total) is current_processor(Cluster,
  X, Y), Total := X*Y on Multi-PSI and PIM/m (pimos.vmac 378-381,
  HELD-SOURCE); N = N x 1 is OURS.  unbound/2 gives {k, Address, X}
  (VPIM kblt_b_unbound, the cluster number); of an external variable
  the goal unbound(X, Result) is thrown to its owner, as VPIM does
  (rung M5), and of an external value (EXVAL) it gives {X} at once.
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

- Rung M4, the shoen across PEs (docs/multi_pe.md 5, M4).  A shoen's
  ID is a black export entry of its record (SHREC) on its home PE, its
  WEC the negative of the WTC given out (VPIM: the WTC is the shoen's
  weighted throw count; TM-1044 9).  A throw from a shoen gives
  WTC_THROW = wtctu 0x400 and min(rsctu 0x1000, what is left) of
  resource with the goal (Pseudo PIM/m PARAM, preferred to VPIM's
  2^16/2^24 units: INFERENCE); while any WTC is out the shoen's goal
  count holds 1 more, so it cannot terminate until every foster
  parent's %terminated and every %return_wtc is back.  On the goal's
  PE a FOSTER PARENT is made (VPIM f_Get_FP_Ptr): a record of the
  shoen layout, parent 0, mask 0, report INT 0, with %ready {1, ID,
  WTC, PE} to the shoen, which answers %supply_wtc (wtcsu 0x1000000;
  %stop or %abort first if the shoen is stopped or ended).  The
  foster parent throws on with its own WTC (asking %request_wtc when
  it has less than 0x403, the goal queued), asks %request_resource
  when its resource is out, forwards an exception as %exception {10,
  ID, WTC, tag, number, Info, NewCode, NewArgv}, answers
  %ask_statistics with %answer_statistics (its consumption), and ends
  with %terminated {2, ID, PE, WTC, resource left, used}.  The shoen
  broadcasts started/stopped/aborted as %start/%stop/%abort to its
  live foster parents.  Consumption reported back is the shoen's
  (reductions = used / 2).  OURS: abort at home ends the shoen at once
  (as on one PE), late WTC just freeing the entry.

The PE classes never change a single machine:
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
                  SHREC, Unimplemented, sx16)
from pimm_layout import G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS, SUSPENDED, TAKEN, HEAP  # noqa: E402
from pimm_layout import (SH_COUNT, SH_STATUS, SH_PARENT, SH_REPORT, SH_GOAL, SH_SIZE,  # noqa: E402
                         SH_REDUCTIONS, SH_REMOVE, SH_MASK, SH_RSC_HI, SH_RSC_LO,
                         SH_RSC_FLAGS, RSC_REPORT_DISALLOWED, STARTED, STOPPED,
                         TERMINATED, REMOVED, READY, REPORT_STARTED, REPORT_STOPPED,
                         REPORT_ABORTED, REPORT_EXCEPTION, REPORT_RESOURCE_LOW,
                         REPORT_STATISTICS_STARTED, REPORT_STATISTICS)

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
# code across PEs (rung M5, code fetch): a code or module word in the
# heap goes as its module's number in the loaded order and the offset
# in it, and the receiver finds its own copy of that module (PIM/m
# sends the module's global identifier and fetches it, M92 pp. 430-431;
# here every PE has every module, copied before the split, so the fetch
# is a lookup: OURS).  Packet words only, never in memory; no PIM/m
# byte format.
CODE_ID, MODULE_ID = 0x1C0, 0x1C2
UNIFY_ARG1 = 7
LONG_VECT = VECT0 + 14
# the WEC a black export gives each ID it sends (VPIM
# D_EXPORT_WEC_UNIT; TR-390 7: 2^24)
WEC_UNIT = 1 << 24
# rung M4, the shoen across PEs: the console's codes (docs/multi_pe.md 1.1)
M_READY, M_TERMINATED, M_START, M_STOP, M_ABORT = 1, 2, 3, 4, 5
M_EXCEPTION = 10
M_REQUEST_WTC, M_SUPPLY_WTC, M_RETURN_WTC = 14, 15, 16
M_REQUEST_RSC, M_SUPPLY_RSC, M_RETURN_RSC = 17, 18, 19
M_ASK_STAT, M_ANSWER_STAT = 20, 21
KIND_NAMES.update({M_READY: 'ready', M_TERMINATED: 'terminated', M_START: 'start',
                   M_STOP: 'stop', M_ABORT: 'abort', M_EXCEPTION: 'exception',
                   M_REQUEST_WTC: 'request_wtc', M_SUPPLY_WTC: 'supply_wtc',
                   M_RETURN_WTC: 'return_wtc', M_REQUEST_RSC: 'request_resource',
                   M_SUPPLY_RSC: 'supply_resource', M_RETURN_RSC: 'return_resource',
                   M_ASK_STAT: 'ask_statistics', M_ANSWER_STAT: 'answer_statistics'})
# the WTC units: a thrown goal's (PIMM.PARAM wtctu 16'400; VPIM
# _WTC_THROW_GOAL_UNIT 2^10), a supply's (wtcsu 16'1000000; VPIM
# _SUPPLY_WTC_UNIT 2^24), a control message's (VPIM _SHOEN_WTC_UNIT 1),
# and what a foster parent keeps back (VPIM _WTC_RESERVED, 1 + 2)
WTC_THROW, WTC_SUPPLY, WTC_CONTROL, WTC_RESERVED = 0x400, 0x1000000, 1, 3
# the resource units: a thrown goal's and a supply's (PIMM.PARAM rsctu
# 16'1000, rscsu 16'10000; VPIM's are 2^16 and 2^24: the Pseudo PIM/m's
# parameter file is preferred, docs/multi_pe.md 5, M4)
RSC_THROW, RSC_SUPPLY = 0x1000, 0x10000


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
        # the loaded modules' descriptors, in the loaded order: a root of
        # the collector (PIMOS's module table is one), moved by it
        self.mods = list(system.mods)
        self.mod_gid = {a: g for g, a in enumerate(self.mods)}
        self.heap_log = []          # get_heap_size: (size, used), in order
        self.paths = {}             # which paths ran, for the tests (not machine state)
        # rung M4: a shoen of this PE with goals elsewhere -> {'e': its
        # black export entry (the shoen ID), 'fps': {pe: %ready less
        # %terminated}, 'adv': the resource out at its foster parents,
        # 'stat': the answers each pending statistics waits for, 'req':
        # the PEs whose resource request waits}
        self.homes = {}
        self.fps = {}               # shoen ID -> the foster parent's record here
        self.fpi = {}               # foster parent record -> {'sid', 'wtc', 'given',
        #                             'reported', 'wait_wtc', 'queued', 'req'}

    def is_fp(self, sh):
        return sh in self.fpi

    def ran(self, path):
        self.paths[path] = self.paths.get(path, 0) + 1

    def i_wait_value(self, pc, x, y, z, c16):
        """The guard X = Y with both arguments one external cell
        (M6, 2026-11-26: MGTP/N on 6 PEs, never on one, where the value
        is local and bound): the goal suspends on it, which sends
        %read, as PDSS suspends X = Y on an unbound X even when Y is
        the same variable (emulator/passive.c passive_unify, case REF:
        PushToSuspensionStack2(x), NO).  One plain variable twice is
        still refused, as on one machine."""
        a, b = self.deref(self.reg[x]), self.deref(self.reg[y])
        if self.is_ex(a) and self.is_ex(b) and a[1] == b[1]:
            self.ran('wait_value of an external cell with itself')
            self.waiting.append(a[1])
            return self.guard_fail()
        return pimm.Machine.i_wait_value(self, pc, x, y, z, c16)

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
        if self.is_ex(v) and self.mem[v[1]][0] & ~1 == EXVAL:
            # an exported VALUE (a list, vector or string: EXVAL) is never
            # a variable, so {X} at once, no message (OURS from the tag's
            # meaning, TM-1044 9.2; rung M5, the Listener printing an
            # answer whose cells are on other PEs)
            self.ran('unbound/2 of an external value')
            w, a = self.vnew(1)
            self.mem[a] = v
            self.reg[y] = w
            return
        if self.is_ex(v):
            # an exported variable: as VPIM's kblt_b_unbound, the goal
            # unbound(X, Result) is thrown to X's owner (the image's stub
            # for the built-in, pimm_stubs), which answers there; Result
            # is a fresh variable here, bound by that PE's %unify
            self.ran('unbound/2 thrown to the owner')
            r = self.new_var()
            k = id_pe(self.imports[self.mem[v[1]][1]]['id'])
            self.throw(k, self.stubs['unbound']['addr'], [v, r])
            self.reg[y] = r
            return
        if self.unbound(v):
            w, a = self.vnew(3)
            self.mem[a], self.mem[a + 1], self.mem[a + 2] = (INT, self.pe), (INT, v[1]), v
        else:
            w, a = self.vnew(1)
            self.mem[a] = v
        self.reg[y] = w

    def i_get_heap_size(self, pc, x, y, z, c16):
        # get_heap_size(^Size, ^Used), 22:FE: pimm.Machine's (its values
        # OURS, sources there), each answer logged for M2's check
        self.heap_log.append(self.heap_size())
        return pimm.Machine.i_get_heap_size(self, pc, x, y, z, c16)

    # ---- collect_garbage asks; the collection is at the goal switch --
    def i_collect_garbage(self, pc, x, y, z, c16):
        self.system.log.append(('ask', self.pe))
        return pimm.Machine.i_collect_garbage(self, pc, x, y, z, c16)

    def goal_switch_gc(self, limit):
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
            self.system.placed.append((self.pe, self.pe, code))
            self.record(pimm.READY, code, self.argv[1:n + 1])
        else:
            self.system.placed.append((self.pe, k, code))
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
            self.system.placed.append((self.pe, self.pe, code))
            self.record(pimm.READY, code, self.reg[:z])
        else:
            self.system.placed.append((self.pe, k, code))
            self.throw(k, code, self.reg[:z])
        return None

    # ---- sending -----------------------------------------------------
    def send(self, dst, packet):
        self.system.send(self.pe, dst, packet)

    def throw(self, k, code, args, sh=None):
        """%throw_goal of code(args) to PE k, a goal of shoen sh (the
        current one if None).  From inside a shoen (rung M4) it carries
        the shoen ID, WTC and resource (VPIM f_Send_IntClMsg_
        ThrowGoal_Sub): from the shoen's own PE, WTC_THROW of WTC newly
        given out by its export entry and RSC_THROW of the resource not
        yet out; from a foster parent, WTC_THROW of its own WTC (with
        less than WTC_THROW + WTC_RESERVED the goal waits for
        %supply_wtc, counted as one of the foster parent's children,
        f_ThrowGoalMsgSusp) and RSC_THROW of its resource left, or what
        there is."""
        sh = self.shoen if sh is None else sh
        sid = wtc = rsc = 0
        if sh and self.is_fp(sh):
            fp = self.fpi[sh]
            if fp['wtc'] < WTC_THROW + WTC_RESERVED:
                self.ran('throw waits for WTC')
                fp['queued'].append((k, code, list(args)))
                self.mem[sh + SH_COUNT] = (INT, self.mem[sh + SH_COUNT][1] + 1)
                if not fp['wait_wtc']:
                    fp['wait_wtc'] = True
                    self.fp_send(sh, M_REQUEST_WTC, [(INT, self.pe)])
                return
            fp['wtc'] -= WTC_THROW
            sid, wtc = fp['sid'], WTC_THROW
            left = self.rsc_left(sh)
            rsc = min(RSC_THROW, max(left, 0))
            self.set_rsc_left(sh, left - rsc)
            fp['given'] -= rsc
            self.ran('throw from a foster parent')
        elif sh:
            h = self.home_of(sh)
            rsc = min(RSC_THROW, max(self.rsc_left(sh) - h['adv'], 0))
            h['adv'] += rsc
            sid, wtc = self.mint(sh, WTC_THROW), WTC_THROW
            self.ran('throw from a shoen')
        packet = [(INT, M_THROW), (INT, sid), (INT, wtc), (INT, 0), (INT, 0), (INT, rsc),
                  (INT, 0), (INT, 0), (INT, self.system.n), (INT, 0),
                  self.code_out(pimm.COD, self.load + code), (INT, 0), (INT, 0), (INT, 0),
                  (INT, len(args))]
        assert len(packet) == THROW_ARGS
        for a in args:
            packet += self.level0(a, k)
        self.send(k, packet)

    # ---- the shoen across PEs (rung M4) --------------------------------
    def home_of(self, sh):
        """The table of a shoen of this PE with goals elsewhere: made at
        its first throw, with its ID, a black export entry of its record
        (VPIM: "荘園ＩＤ (黒輸出表エントリのオフセット)",
        f_int_cl_recv_throw_goal.psl.c), whose WEC is the WTC given out
        (TR-390 7; VPIM f_AddWTCWithReclaimExpEntryAndShoenTerminate_Sub:
        the shoen terminates when it is all back).  While any is out the
        shoen counts one more child (OURS: so that pimm.py's count, its
        end at 0 and its report are the one-PE code), and the entry, a
        root of the collector, holds the record."""
        h = self.homes.get(sh)
        if h is None:
            e = self.next_export
            self.next_export += 1
            w = (SHREC, sh)
            self.exports[e] = w
            self.wec[e] = 0
            self.black[key(w)] = e
            h = self.homes[sh] = {'e': e, 'fps': {}, 'adv': 0, 'stat': [], 'req': []}
            self.mem[sh + SH_COUNT] = (INT, self.mem[sh + SH_COUNT][1] + 1)
            self.system.log.append(('shoen out', self.pe, sh))
        return h

    def mint(self, sh, n):
        """n of WTC given out by shoen sh's entry; its ID."""
        h = self.home_of(sh)
        self.wec[h['e']] -= n
        return ext_id(self.pe, h['e'])

    def free_export(self, e):
        w = self.exports[e]
        self.free_entry(e)
        if w[0] == SHREC:
            self.shoen_back(w[1])

    def shoen_back(self, sh):
        """All of shoen sh's WTC is back: no goal or message of it is
        anywhere else.  The child it counted for that ends (unless an
        abort ended the shoen already)."""
        h = self.homes.pop(sh)
        self.system.log.append(('shoen back', self.pe, sh))
        if h['adv'] or any(h['fps'].values()) or h['stat'] or h['req']:
            self.system.anomalies.append(('shoen back with', self.pe, sh, h))
        if self.mem[sh + SH_STATUS][1] not in (TERMINATED, REMOVED):
            self.ended(sh, 0)

    def home_shoen(self, sid):
        """The shoen record of an ID of this PE's."""
        e = id_entry(sid)
        w = self.exports.get(e)
        if w is None or w[0] != SHREC:
            raise Unimplemented('a shoen ID %x of no shoen here' % sid)
        return e, w[1]

    def to_fps(self, sh, kind, extra=()):
        """A control message to every foster parent of shoen sh (VPIM
        f_Send_IntClMsg_ToAllFPs), each with WTC_CONTROL newly given
        out; the PEs it went to."""
        h = self.homes.get(sh)
        live = sorted(k for k, n in (h['fps'].items() if h else ()) if n)
        for k in live:
            self.to_fp(sh, k, kind, extra)
        return live

    def to_fp(self, sh, k, kind, extra=(), wtc=WTC_CONTROL):
        sid = self.mint(sh, wtc)
        self.send(k, [(INT, kind), (INT, sid), (INT, wtc)] + list(extra))

    def fp_send(self, fp, kind, extra, wtc=WTC_CONTROL):
        """A message of foster parent fp to its shoen, with wtc of its
        WTC (VPIM: every message to the shoen carries some)."""
        info = self.fpi[fp]
        if info['wtc'] < wtc:
            raise Unimplemented('a foster parent with no WTC for a message (VPIM suspends it)')
        info['wtc'] -= wtc
        self.send(id_pe(info['sid']), [(INT, kind), (INT, info['sid']), (INT, wtc)] + list(extra))

    def new_fp(self, sid):
        """A foster parent for the shoen of ID sid, here (VPIM f_Get_FP_Ptr,
        f_InitFPSlots: started, child count 0, the goal's resource;
        manual e-shoen.tex:304 "a new shoen is created on the goal's
        destination node"): a record of the shoen's layout, its parent
        0 so that it is the top of this PE's chain, its mask 0 (an
        exception goes to the shoen), and %ready to the shoen."""
        fp = self.alloc(SH_SIZE)
        for i, w in ((SH_COUNT, 0), (SH_STATUS, STARTED), (SH_PARENT, 0), (SH_REPORT, 0),
                     (SH_GOAL, 0), (SH_REDUCTIONS, 0), (SH_REMOVE, 0), (SH_MASK, 0),
                     (SH_RSC_HI, 0), (SH_RSC_LO, 0), (SH_RSC_FLAGS, 0)):
            self.mem[fp + i] = (INT, w)
        self.fps[sid] = fp
        # wait_wtc: the shoen answers %ready with %supply_wtc (VPIM
        # f_ShoenReceiveReady), so it is as if asked (INFERENCE)
        self.fpi[fp] = {'sid': sid, 'wtc': 0, 'given': 0, 'reported': 0,
                        'wait_wtc': True, 'queued': [], 'req': False}
        self.system.log.append(('fp', self.pe, sid))
        return fp

    def fp_end(self, fp):
        """Foster parent fp terminates (VPIM f_FPTerminateWithUnlockFP_Sub):
        %terminated with all its WTC, the resource it has left and what
        it consumed not yet reported; it is TERMINATED (a goal of it met
        later is discarded) and forgotten."""
        info = self.fpi.pop(fp)
        del self.fps[info['sid']]
        self.mem[fp + SH_STATUS] = (INT, TERMINATED)
        left = max(self.rsc_left(fp), 0)
        used = info['given'] - left - info['reported']
        if info['queued']:
            self.ran('aborted foster parent drops a waiting throw')
        self.system.log.append(('fp end', self.pe, info['sid']))
        self.send(id_pe(info['sid']),
                  [(INT, M_TERMINATED), (INT, info['sid']), (INT, self.pe), (INT, info['wtc']),
                   (INT, left >> 32), (INT, left & 0xffffffff),
                   (INT, used >> 32), (INT, used & 0xffffffff)])

    def terminate(self, sh):
        if self.is_fp(sh):
            return self.fp_end(sh)
        if self.mem[sh + SH_REPORT][0] == INT:
            # a foster parent already ended by %abort: a child shoen of it
            # ending cannot reach here (its goals are discarded)
            raise Unimplemented('a foster parent ended twice')
        return pimm.Machine.terminate(self, sh)

    def report(self, sh, code, car=None):
        if self.is_fp(sh):
            if code != REPORT_RESOURCE_LOW:
                raise Unimplemented('a report %r to a foster parent' % (code,))
            # its resource is out (taken_check): ask the shoen (VPIM
            # f_FPRequestResource_Sub)
            info = self.fpi[sh]
            if not info['req']:
                info['req'] = True
                self.ran('foster parent asks for resource')
                self.fp_send(sh, M_REQUEST_RSC, [(INT, self.pe)])
            return
        pimm.Machine.report(self, sh, code, car)
        if sh in self.homes:
            kind = {REPORT_STARTED: M_START, REPORT_STOPPED: M_STOP,
                    REPORT_ABORTED: M_ABORT}.get(code)
            if kind is not None and self.to_fps(sh, kind):
                self.ran('%s to the foster parents' % KIND_NAMES[kind])

    def charge(self, sh, used):
        """Resource a foster parent of shoen sh consumed: half of it the
        shoen's reductions (2 a reduction, manual e-shoen.tex:42), all of
        it taken from the shoen and those above it, as pimm.py
        end_reduction takes a local goal's."""
        if used:
            self.mem[sh + SH_REDUCTIONS] = (INT, self.mem[sh + SH_REDUCTIONS][1] + (used >> 1) & 0xffffffff)
            for s in self.chain_of(sh):
                self.set_rsc_left(s, self.rsc_left(s) - used)

    def avail(self, sh):
        return self.rsc_left(sh) - self.homes[sh]['adv']

    def supply(self, sh):
        """Answer the resource requests of shoen sh's foster parents while
        it has a supply unit not yet out (VPIM
        f_Send_IntClMsg_SupplyResource_ToResourceRequestFPs_Sub); with
        none, resource_low to the shoen once (VPIM
        f_ReplicateSupplyResourceDestinations: when its reports are
        allowed), so that its monitor may add some."""
        h = self.homes[sh]
        while h['req'] and self.avail(sh) >= RSC_SUPPLY:
            k = h['req'].pop(0)
            h['adv'] += RSC_SUPPLY
            self.ran('resource supplied')
            self.to_fp(sh, k, M_SUPPLY_RSC)
        if h['req'] and not self.mem[sh + SH_RSC_FLAGS][1] & RSC_REPORT_DISALLOWED \
                and self.mem[sh + SH_STATUS][1] == STARTED:
            self.mem[sh + SH_RSC_FLAGS] = (INT, self.mem[sh + SH_RSC_FLAGS][1] | RSC_REPORT_DISALLOWED)
            self.ran('resource_low for a foster parent')
            pimm.Machine.report(self, sh, REPORT_RESOURCE_LOW)

    def i_shoen_statistics(self, pc, x, y, z, c16):
        """pimm.py's, and with foster parents (VPIM f_ShoenStatistics_Sub):
        10 at once, %ask_statistics to each, and {9, H, L} when every
        one has answered with what it consumed."""
        def f(h):
            if h[0] != SHREC:
                raise Unimplemented('shoen_statistics(%r)' % (h,))
            sh = h[1]
            ho = self.homes.get(sh)
            pimm.Machine.report(self, sh, REPORT_STATISTICS_STARTED)
            live = self.to_fps(sh, M_ASK_STAT) if ho else []
            if live:
                self.ran('statistics asked of the foster parents')
                ho['stat'].append(len(live))
            else:
                self.report_statistics(sh)
            return [h]
        self.builtin('shoen_statistics', [x, y], f)

    def report_statistics(self, sh):
        red = self.mem[sh + SH_REDUCTIONS][1]
        self.report3(sh, REPORT_STATISTICS, red >> 31, red << 1)

    def exception(self, num, tag, b, c):
        """pimm.py's, Info's Pe this PE; from inside a foster parent
        before any shoen here accepts it, %exception to the shoen
        (VPIM f_Send_IntClMsg_Exception: kind, shoen ID, WTC, the type,
        the number, Info, NewCode, NewArgv), where the innermost shoen
        from it up that accepts it is reported to."""
        target = fp = 0
        for sh in self.chain_of(self.shoen):
            if self.is_fp(sh):
                fp = sh
                break
            if self.mem[sh + SH_MASK][1] & tag:
                target = sh
                break
        if not target and not fp:
            raise Unimplemented('an exception (tag %x) no shoen accepts' % tag)
        nc, na = self.new_var(), self.new_var()
        self.record(READY, self.stubs['apply']['addr'], [nc, na])
        if callable(c):
            c = c()
        info = self.alloc(3)
        self.mem[info] = (INT, self.pe)
        self.mem[info + 1] = b
        self.mem[info + 2] = c
        if target:
            self.exception_report(target, num, (VECT0 + 6, info), nc, na)
            return
        self.ran('exception to the shoen')
        home = id_pe(self.fpi[fp]['sid'])
        self.fp_send(fp, M_EXCEPTION, [(INT, tag), (INT, num)] + self.level0((VECT0 + 6, info), home)
                     + self.level0(nc, home) + self.level0(na, home))

    def exception_report(self, target, num, info, nc, na):
        m = self.alloc(5)
        self.mem[m] = (INT, REPORT_EXCEPTION)
        self.mem[m + 1] = (INT, num)
        self.mem[m + 2] = info
        self.mem[m + 3] = nc
        self.mem[m + 4] = na
        pimm.Machine.report(self, target, None, car=(VECT0 + 10, m))

    def goal_switch(self, limit):
        # resource that came back (or was added) answers a waiting request
        for sh in [s for s, h in self.homes.items() if h['req']]:
            if self.avail(sh) >= RSC_SUPPLY:
                self.supply(sh)
        return self.goal_switch_gc(limit)

    def receive_goal(self, packet, code, args):
        """A thrown goal: of the root; of a shoen of this PE (it is the
        shoen's again, its WTC and resource back); else of the foster
        parent of its shoen here, made if there is none (VPIM
        f_Recv_IntClMsg_Throw_Goal_Sub, f_Get_FP_Ptr)."""
        sid, wtc, rsc = packet[1][1], packet[2][1], packet[5][1]
        if not sid:
            self.record(pimm.READY, code, args)
            return
        if id_pe(sid) == self.pe:
            self.ran('goal came home to its shoen')
            e, sh = self.home_shoen(sid)
            self.homes[sh]['adv'] -= rsc
            self.record(pimm.READY, code, args, shoen=sh)
            self.mem[sh + SH_COUNT] = (INT, self.mem[sh + SH_COUNT][1] + 1)
            self.give_back(e, wtc)
            return
        fp = self.fps.get(sid)
        if fp is None:
            fp = self.new_fp(sid)
            self.fpi[fp]['wtc'] = wtc
            self.fp_send(fp, M_READY, [(INT, self.pe)])
        else:
            self.ran('goal to a foster parent')
            self.fpi[fp]['wtc'] += wtc
        self.fpi[fp]['given'] += rsc
        self.set_rsc_left(fp, self.rsc_left(fp) + rsc)
        self.record(pimm.READY, code, args, shoen=fp)
        self.mem[fp + SH_COUNT] = (INT, self.mem[fp + SH_COUNT][1] + 1)

    def receive_shoen(self, src, kind, packet):
        """The shoen and foster-parent messages (rung M4)."""
        sid, wtc = packet[1][1], packet[2][1]
        if id_pe(sid) == self.pe:                       # to the shoen
            e, sh = self.home_shoen(sid)
            h = self.homes[sh]
            self.event('N %s %d %d' % (KIND_NAMES[kind], src, e))
            if kind == M_READY:
                h['fps'][src] = h['fps'].get(src, 0) + 1
                st = self.mem[sh + SH_STATUS][1]
                if st == STOPPED:
                    self.ran('ready while stopped')
                    self.to_fp(sh, src, M_STOP)
                elif st in (TERMINATED, REMOVED):
                    self.ran('ready while aborted')
                    self.to_fp(sh, src, M_ABORT)
                self.to_fp(sh, src, M_SUPPLY_WTC, wtc=WTC_SUPPLY)
                self.give_back(e, wtc)
            elif kind == M_TERMINATED:
                wtc = packet[3][1]
                left = packet[4][1] << 32 | packet[5][1]
                used = packet[6][1] << 32 | packet[7][1]
                h['fps'][src] -= 1
                h['adv'] -= left + used
                self.charge(sh, used)
                if src in h['req'] and not h['fps'][src]:
                    h['req'] = [k for k in h['req'] if k != src]
                self.give_back(e, wtc)
            elif kind == M_REQUEST_WTC:
                self.to_fp(sh, src, M_SUPPLY_WTC, wtc=WTC_SUPPLY)
                self.give_back(e, wtc)
            elif kind == M_RETURN_WTC:
                self.give_back(e, wtc)
            elif kind == M_REQUEST_RSC:
                h['req'].append(src)
                self.supply(sh)
                self.give_back(e, wtc)
            elif kind == M_RETURN_RSC:
                h['adv'] -= packet[3][1] << 32 | packet[4][1]
                self.give_back(e, wtc)
            elif kind == M_ANSWER_STAT:
                used = packet[3][1] << 32 | packet[4][1]
                h['adv'] -= used
                self.charge(sh, used)
                h['stat'][0] -= 1
                if not h['stat'][0]:
                    h['stat'].pop(0)
                    self.ran('statistics answered')
                    self.report_statistics(sh)
                self.give_back(e, wtc)
            elif kind == M_EXCEPTION:
                tag, num = packet[3][1], packet[4][1]
                info, i = self.get0(packet, 5)
                nc, i = self.get0(packet, i)
                na, i = self.get0(packet, i)
                target = 0
                for s in self.chain_of(sh):
                    if self.mem[s + SH_MASK][1] & tag:
                        target = s
                        break
                if not target:
                    raise Unimplemented('an exception (tag %x) no shoen accepts' % tag)
                self.exception_report(target, num, info, nc, na)
                self.give_back(e, wtc)
            else:
                raise Unimplemented('message kind %d to a shoen' % kind)
            return
        fp = self.fps.get(sid)                          # to a foster parent
        self.event('N %s %d %x' % (KIND_NAMES[kind], src, sid))
        if fp is None:
            # none here now (it terminated): the WTC goes back (VPIM
            # f_Recv_IntClMsg_*_Sub "No FP... WTC return"), a supply of
            # resource with it, statistics answered 0 (2.4.2)
            self.ran('no foster parent for %s' % KIND_NAMES[kind])
            back = [(INT, M_RETURN_WTC), (INT, sid), (INT, wtc), (INT, self.pe)]
            if kind == M_SUPPLY_RSC:
                back = [(INT, M_RETURN_RSC), (INT, sid), (INT, wtc), (INT, 0), (INT, RSC_SUPPLY),
                        (INT, self.pe)]
            elif kind == M_ASK_STAT:
                back = [(INT, M_ANSWER_STAT), (INT, sid), (INT, wtc), (INT, 0), (INT, 0),
                        (INT, self.pe)]
            self.send(id_pe(sid), back)
            return
        info = self.fpi[fp]
        info['wtc'] += wtc
        st = self.mem[fp + SH_STATUS][1]
        if kind == M_START:
            if st == STOPPED:
                self.mem[fp + SH_STATUS] = (INT, STARTED)
                self.release(fp)
        elif kind == M_STOP:
            if st == STARTED:
                self.mem[fp + SH_STATUS] = (INT, STOPPED)
        elif kind == M_ABORT:
            # VPIM f_FPReceiveAbort: aborted, its stopped goals freed; it
            # ends now (OURS, as pimm.py's abort ends the shoen at once;
            # VPIM ends it at its next goal's end): its goals met later
            # are discarded (taken_check)
            self.ran('foster parent aborted')
            self.fp_end(fp)
        elif kind == M_SUPPLY_WTC:
            info['wait_wtc'] = False
            queued, info['queued'] = info['queued'], []
            for k, code, args in queued:
                self.ran('throw sent with the WTC supplied')
                self.throw(k, code, args, sh=fp)
                if fp in self.fpi:
                    self.ended(fp, 0)               # the goal it counted is gone
        elif kind == M_SUPPLY_RSC:
            info['req'] = False
            info['given'] += RSC_SUPPLY
            self.set_rsc_left(fp, self.rsc_left(fp) + RSC_SUPPLY)
            self.mem[fp + SH_RSC_FLAGS] = (INT, self.mem[fp + SH_RSC_FLAGS][1] & ~RSC_REPORT_DISALLOWED)
            if st == STARTED and self.rsc_left(fp) > 0:
                self.release(fp)
        elif kind == M_ASK_STAT:
            used = info['given'] - self.rsc_left(fp) - info['reported']
            info['reported'] += used
            self.fp_send(fp, M_ANSWER_STAT, [(INT, used >> 32), (INT, used & 0xffffffff),
                                             (INT, self.pe)])
        else:
            raise Unimplemented('message kind %d to a foster parent' % kind)

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

    def free_entry(self, e):
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
        if t in (pimm.COD, pimm.MOD):
            # code, or a module, as the thrown goal's code goes (rung M4:
            # prof's apply_with_pgm(Code, ArgV)@node(Node)): by its
            # module's number if it is in the heap (code_out)
            self.ran('code sent')
            return [self.code_out(t, d[1])]
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
        if self.unbound(d) or t in (INT, ATOM, VECT0, pimm.COD, pimm.MOD):
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

    def module_base(self, tag, a):
        """The module descriptor of a code word (the predicate head two
        cells before it holds the offset back to it, as pimm.py
        i_code_to_predicate and pimm_gc read it) or of a module word."""
        if tag == pimm.MOD:
            return a
        h = self.mem[a - 2]
        if h[0] != pimm.PREDH:
            raise Unimplemented('code at %x has no predicate head' % a)
        return a - 2 - (h[1] & 0xffffff)

    def module_id(self, base):
        """The global number of the module at base here: its place in
        the loaded order, or, for one made here later (a compiled
        module), the next number, given at its first send (OURS)."""
        g = self.mod_gid.get(base)
        if g is None:
            g = len(self.system.mod_home)
            self.system.mod_home.append(self.pe)
            self.mods += [None] * (g + 1 - len(self.mods))
            self.mods[g] = base
            self.mod_gid[base] = g
            self.ran('module numbered')
        return g

    def code_out(self, tag, a):
        """A code (COD) or module (MOD) word at address a as a message
        sends it: in the image as it is; in the heap as {CODE_ID or
        MODULE_ID, module number << 24 | offset} (CODE_ID above)."""
        if a - self.load < HEAP:
            return (tag, a)
        base = self.module_base(tag, a)
        g = self.module_id(base)
        self.ran('code sent by its module')
        return (CODE_ID if tag == pimm.COD else MODULE_ID, g << 24 | (a - base))

    def code_in(self, w):
        """The word here for a code or module word of a message: this
        PE's copy of the module, fetched if it has none."""
        if w[0] in (pimm.COD, pimm.MOD):
            return w
        g = w[1] >> 24
        base = self.mods[g] if g < len(self.mods) else None
        if base is None:
            base = self.fetch(g)
        return (pimm.COD if w[0] == CODE_ID else pimm.MOD, base + (w[1] & 0xffffff))

    def fetch(self, g):
        """Module g copied here from the PE that numbered it (PIM/m
        fetches a module by its global identifier, M92 pp. 430-431; here
        the copy is made at once, without messages: OURS).  Its cells
        are copied word by word; what they point at outside the module
        (its constants: strings, vectors, lists, the cells of its calls
        to other modules) is copied with it, sharing kept; a call cell
        still unbound is a fresh variable here (linked here when first
        called); a code or module word is this PE's copy of that
        module."""
        src = self.system.pes[self.system.mod_home[g]]
        a = src.mods[g]
        n = src.mem[a][1] & 0xffffff
        new = self.alloc(n + 1)
        self.mods += [None] * (g + 1 - len(self.mods))
        self.mods[g] = new
        self.mod_gid[new] = g
        memo = {}
        self.mem[new] = src.mem[a]
        for i in range(1, n + 1):
            self.mem[new + i] = self.copy_from(src, src.mem[a + i], memo)
        self.system.log.append(('fetch', self.pe, g))
        self.ran('module fetched')
        return new

    def copy_from(self, src, w, memo):
        """The word w of PE src's memory as a word here (fetch)."""
        t, v = w
        k = t & ~1 if t < 0x20 else t
        if k in (INT, ATOM, UNDF, VECT0) or t in (0x22, 0x23, pimm.PREDH, pimm.FLT):
            return w
        if t in (pimm.MOD, pimm.COD):
            base = src.module_base(t, v)
            g = src.module_id(base)
            here = self.mods[g] if g < len(self.mods) and self.mods[g] is not None else self.fetch(g)
            return (t, here + (v - base))
        if k == REF:
            if v not in memo:
                c = src.mem[v]
                memo[v] = a = self.alloc(1)
                self.mem[a] = (UNDF, 0) if c[0] & ~1 == UNDF else self.copy_from(src, c, memo)
            return (t, memo[v])
        if k == LIST:
            return (t, self.copy_block(src, v, 2, memo))
        if VECT0 + 2 <= k <= VECT0 + 12:
            return (t, self.copy_block(src, v, (k - VECT0) // 2, memo))
        if k == LONG_VECT:
            return (t, self.copy_block(src, v, 3 + src.mem[v + 1][1], memo, head=3))
        if k == STRG:
            if v not in memo:
                n = (src.mem[v][1] & 0xffffff) + 1
                memo[v] = a = self.alloc(n)
                for i in range(n):
                    self.mem[a + i] = src.mem[v + i]
            return (t, memo[v])
        raise Unimplemented('fetching a module: a word with tag %02x' % t)

    def copy_block(self, src, v, n, memo, head=0):
        if v in memo:
            return memo[v]
        memo[v] = a = self.alloc(n)
        for i in range(n):
            c = src.mem[v + i]
            if i < head:
                self.mem[a + i] = (c[0], a + 3) if c[0] == pimm.VDESC else c
            else:
                self.mem[a + i] = self.copy_from(src, c, memo)
        return a

    # ---- receiving -----------------------------------------------------
    def get0(self, pk, i):
        """A level-0 word of a message at pk[i]: (the word here, next i)."""
        w = pk[i]
        if w[0] & ~1 in (INT, ATOM, VECT0):
            return w, i + 1
        if w[0] in (pimm.COD, pimm.MOD, CODE_ID, MODULE_ID):
            return self.code_in(w), i + 1
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
                n = packet[THROW_ARGS - 1][1]
                code = self.code_in(packet[10])[1] - self.load
                args, i = [], THROW_ARGS
                for _ in range(n):
                    a, i = self.get0(packet, i)
                    args.append(a)
                self.receive_goal(packet, code, args)
                self.event('N throw %d %d' % (src, code))
            elif kind in KIND_NAMES and kind not in (M_READ, M_ANSWER, M_RELEASE, M_UNIFY):
                self.receive_shoen(src, kind, packet)
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
        # rung M5: the loaded modules are roots (PIMOS's module table;
        # VPIM's collector, f_GCPreProcedure_Sub, keeps the code area),
        # so a goal thrown here later finds its module (code_in)
        pe.mods = [a and self.module(a) for a in pe.mods]
        if pe.mods:
            pe.ran('modules kept at a collection')
        pe.mod_gid = {a: g for g, a in enumerate(pe.mods) if a}
        for e in sorted(pe.exports):
            pe.exports[e] = self.word(pe.exports[e])
        for k in sorted(pe.roots):
            pe.roots[k] = self.word(pe.roots[k])
        # rung M4: the foster parents (VPIM's collector: one of its roots,
        # f_GCPreProcedure_Sub), each with the goals that wait for WTC
        fpi = {}
        for fp in sorted(pe.fpi):
            info = pe.fpi[fp]
            info['queued'] = [(k, self.code(pe.load + c) - pe.load, [self.word(a) for a in args])
                              for k, c, args in info['queued']]
            fpi[self.shoen(fp)] = info
        pe.fpi = fpi
        pe.fps = {info['sid']: fp for fp, info in fpi.items()}
        # a shoen with goals elsewhere: its record is held by its entry
        pe.homes = {pe.exports[h['e']][1]: h for h in pe.homes.values()}

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


def shoen_accounting(system):
    """At quiescence: every shoen with goals elsewhere has its WTC
    (its entry's WEC = minus what its foster parents hold), its
    resource out and its foster parents accounted for; what is not."""
    s, bad = system, []
    if any(s.queues.values()):
        return [('messages in flight',)]
    for pe in s.pes:
        for sh, h in pe.homes.items():
            sid = ext_id(pe.pe, h['e'])
            fps = [(o.pe, o.fpi[o.fps[sid]]) for o in s.pes if sid in o.fps]
            held = sum(i['wtc'] for _k, i in fps)
            if pe.wec[h['e']] + held:
                bad.append(('WTC not accounted for', pe.pe, pe.wec[h['e']], held))
            out = sum(i['given'] - i['reported'] for _k, i in fps)
            if h['adv'] != out:
                bad.append(('resource out', pe.pe, h['adv'], out))
            live = sorted(k for k, n in h['fps'].items() if n)
            if live != sorted(k for k, _i in fps):
                bad.append(('foster parents known', pe.pe, live, [k for k, _i in fps]))
    return bad


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
            if not k:
                # the loaded modules, in the loaded order (lockstep_xmod
                # loaded: their descriptors above the image, ascending)
                self.mods = sorted(a for a, c in m.mem.items()
                                   if a >= m.load + HEAP and c[0] == pimm.CDESC and c[1] >> 24 == 6)
                # the PE that numbered each module made after the split (None:
                # the loaded ones, on every PE)
                self.mod_home = [None] * len(self.mods)
            m.__class__ = PE
            m.setup(self, k)
            self.pes.append(m)
        self.queues = {(s, d): deque() for s in range(n) for d in range(n) if s != d}
        self.log = []               # ('gc', pe), ('ask', pe), ('send', kind, src, dst), in order
        self.sent = {}              # kind -> count
        self.anomalies = []         # what a check must find empty
        self.placed = []            # (PE, the node it is made on or sent to, code) of each @node goal

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

    def run(self, quota=1, limit=10 ** 8, rounds=None):
        """Run every PE until no PE has a goal and no message is in
        flight (or for `rounds` turns of every PE, a bench's way to act
        while the system runs).  Returns the goal switches each PE made."""
        switches = [0] * self.n
        while rounds is None or rounds > 0:
            if rounds is not None:
                rounds -= 1
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
