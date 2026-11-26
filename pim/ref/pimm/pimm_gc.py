"""The garbage collector of the reference model (pimm.py), R7G.

INFERENCE / OURS, the whole of it.  What PIM/m's collector did is lost
with its firmware.  What is held:

  - the microcode entry of `collect_garbage` (23:77), 02d5-02d7, three
    microinstructions (`asm/mekbn.py --rtl 02d5 24`):
        MAR1<-R05; MDR1<-#wide; MDR2<-{ex_float tag,0}
        XR<-W1f; YR<-#34; MAR1<-MAR1 add_with_one MDR1
        W1f<-XR em2_19 YR; [MAR1]<-MDR2 | end
    It collects nothing itself: it writes one cell and changes the
    work register W1f, and ends.  READ: that much.  INFERENCE: W1f
    holds event or request flags and the collection is done later,
    outside the instruction, as VPIM does it (below).  So here
    `collect_garbage` sets a request and succeeds, and the collection
    is made at the next goal switch (pimm.py run, before the alarm is
    looked at), when no register holds anything live.
  - VPIM's collector (ANALOGY: a sibling's, not PIM/m's), TM-1044
    chapter 11 (`DOCUMENT/TM-1044.j/s11.tex`) and
    `src/functions/f_gc_in_cluster.psl.c`: a copying collector (the
    copy area scanned from its start to its end, S to B, the copied
    cell's old place given a forwarding mark, done when S reaches B),
    started from an event at a goal switch (f_RequestLocalGC, :68,
    sets the request; f_GCHandler_Sub collects), its roots the ready
    goal stack, the foster parents (shoen), the alarm timer's
    variable and the SCSI records among others
    (f_GCPreProcedure_Sub, :216-245: :221, :227, :239, :243).

Ours, each for want of PIM/m's:

  - The heap is [lo, hp): lo is the heap's first cell (pimm_layout
    HEAP) until the first collection.  The live cells are copied to
    the to-space, which starts at the heap's first cell when what
    could be live (hp - lo) fits below lo, else at hp (two halves
    that alternate, as a semispace collector's do; the first
    collection, with the boot's modules in the heap, copies above).
    Afterwards lo is where the to-space started and hp its end.
  - Roots, in this order: the ready queue, the merger's list and the
    goals made ready since the last pickup (each list in its order),
    the armed alarm's variable, each SCSI command that waits for the
    device (its buffer, its CDB, its three output variables), then the
    current shoen (the last goal's: a unification the alarm makes
    before the next goal is taken makes its goal there).  Nothing else
    of the machine holds a heap address at a goal switch: the
    registers, the argument registers, the structure pointer and the
    work slots are dead then (each goal loads its registers from its
    record).  Neither are a bench's slots or the checkpoint's Loaded
    word roots: a collection while a bench holds heap words in its
    slots is not supported.
  - A forwarding mark is a from-space cell {GCFWD 3Dh, the new
    address}.  A goal, suspension or shoen record is copied with a
    header {GCHDR 3Ch, kind << 24 | length} before it in the to-space
    (kind 1 goal, 2 suspension, 3 shoen), because their link fields
    are addresses with the INT tag, found only by where they are.
    The headers stay in the heap, dead.  Neither tag is in PIMOS's
    tag table (debugger/inspector/tagtbl.kl1) or in the image.
  - A word's tag says what it points at: REF one cell, LIST two,
    VECTn n, a long vector its descriptor, three cells and the
    elements, a string its descriptor and words, MOD a module (its
    descriptor, then the cells: copied whole), COD the code of a
    predicate in a module (the module copied whole, the address moved
    with it; the module from the predicate head two cells before, as
    pimm.py i_code_to_predicate reads it), SHREC a shoen record, HOOK
    a suspension record.  A structure is copied once: one with
    cells already copied, each on its own (a reference to one of its
    cells was met first), is copied with each such cell's value in its
    place (a bound cell does not change, so two copies of it are one
    value), or, if that cell is an unbound variable, the variable
    itself, its copy made a reference to it (one variable stays one
    cell, and it is in the structure, where a reading of the structure
    finds it as it would without the collection); then every one of
    its cells forwards to its place in the copy.  A module, a string, a record or a long vector's
    descriptor partly copied is refused (the prompt checkpoint has no
    pointer into a module but MOD and COD: checked 2026-11-25).
  - A record's link to the next goal (G_LINK) is kept if that goal
    is copied, else it is 0 (a goal on no list has a stale link that
    is never read); a shoen's list of parked goals is copied with it,
    in order.  A goal only a dead variable could wake is not copied
    (as VPIM's collector would find it; VPIM then reports it, PIMOS's
    "deadlock", which is NOT done here): the shoen's count and the
    machine's count of suspended goals keep it, so that what the
    machine does next is what it would have done without the
    collection.
  - The collection writes are not traced (the M lines would be as
    many as the cells copied); one line is: `K gc LO HP TO TOP SUM`,
    the old heap's bounds, the new heap's, from the load address, and
    an FNV-1 checksum of the new heap's cells (tag, then value, each
    a 32-bit step), which the Bluespec's collector writes the same.

Refused (pimm.Unimplemented): a pointer into the dead part of memory
below lo or at or above hp, a tag the collector does not know, the
to-space not fitting.
"""
import pimm
from pimm_layout import (G_LINK, G_STATUS, G_CODE, G_ARGN, G_ARGS, S_NEXT, S_GOAL,
                         SH_PARENT, SH_REPORT, SH_GOAL, SH_SIZE, HEAP)

GCHDR, GCFWD = 0x3c, 0x3d           # OURS: not in tagtbl.kl1
K_GOAL, K_SUSP, K_SHOEN = 1, 2, 3
FNV0, FNV_PRIME = 0x811c9dc5, 16777619

_IMMEDIATE = {pimm.INT, pimm.ATOM, pimm.UNDF, pimm.VECT0}
_IMMEDIATE_HIGH = {0x22, 0x23, pimm.PREDH, pimm.FLT}


def checksum(cells):
    h = FNV0
    for t, v in cells:
        h = ((h ^ t) * FNV_PRIME) & 0xffffffff
        h = ((h ^ v) * FNV_PRIME) & 0xffffffff
    return h


class Collector:
    def __init__(self, m):
        self.m = m
        self.mem = m.mem
        self.base = m.load + HEAP
        self.lo = getattr(m, 'heap_lo', None) or self.base
        self.hp = m.hp
        live = self.hp - self.lo
        self.to = self.base if live <= self.lo - self.base else self.hp
        self.top = self.to                 # B: the next free to-space cell
        # which paths ran, for the tests (not machine state)
        self.counts = dict.fromkeys(('goal', 'susp', 'shoen', 'parked', 'module', 'code', 'string',
                                     'long_vector', 'mixed', 'merge_in', 'to_processor',
                                     'mq', 'mwh', 'alarm', 'scsi', 'cur_shoen'), 0)
        stubs = m.stubs
        self.merge_in = m.load + stubs['$merge_in']['addr']
        self.to_processor = {m.load + s['addr']: int(n[len('$to_processor'):])
                             for n, s in stubs.items() if n.startswith('$to_processor')}

    # ---- the cells -------------------------------------------------
    def get(self, a):
        return dict.__getitem__(self.mem, a)

    def put(self, a, w):
        dict.__setitem__(self.mem, a, w)

    def fwd(self, a):
        """The new address of from-space cell a, or None."""
        c = self.get(a)
        return c[1] if c[0] == GCFWD else None

    def now(self, a):
        """What the from-space cell a holds, from its copy if it has one."""
        c = self.get(a)
        return self.get(c[1]) if c[0] == GCFWD else c

    def where(self, a):
        """'static' below the heap, 'to' in the to-space so far (already
        a new address), 'from' in the from-space; else refused."""
        if a < self.base:
            return 'static'
        if self.to <= a < self.top:
            return 'to'
        if self.lo <= a < self.hp:
            return 'from'
        raise pimm.Unimplemented('gc: a pointer to %x, outside the heap [%x, %x)'
                                 % (a, self.lo, self.hp))

    def alloc(self, n):
        a = self.top
        self.top += n
        if self.top >= self.m.load + self.m.size or (self.to < self.lo and self.top > self.lo):
            raise pimm.Unimplemented('gc: the to-space is full')
        return a

    # ---- copying ---------------------------------------------------
    def data(self, a, n, head=0):
        """A structure of n data cells at a (the first `head` of them a
        descriptor, copied whole or not at all); its new address."""
        if self.where(a) != 'from':
            return a
        fw = [self.fwd(a + i) for i in range(n)]
        if all(f is not None for f in fw) and all(fw[i] == fw[0] + i for i in range(n)):
            return fw[0]
        if any(f is not None for f in fw[:head]):
            raise pimm.Unimplemented('gc: a descriptor at %x partly copied' % a)
        if any(f is not None for f in fw):
            self.counts['mixed'] += 1
        new = self.alloc(n)
        for i in range(n):
            c = self.get(a + i) if fw[i] is None else self.get(fw[i])
            if fw[i] is not None and c[0] & ~1 in (pimm.UNDF, pimm.HOOK):
                self.put(fw[i], (pimm.REF, new + i))     # the variable moves in
            self.put(new + i, c)
            self.put(a + i, (GCFWD, new + i))
        return new

    def block(self, a, n, what, key, header=None):
        """n cells at a copied whole (a module, a string, a record),
        after `header` if given; the new address of a."""
        if self.where(a) != 'from':
            return a
        f = self.fwd(a)
        if f is not None:
            if self.fwd(a + n - 1) != f + n - 1:
                raise pimm.Unimplemented('gc: %s at %x partly copied' % (what, a))
            return f
        self.counts[key] += 1
        if header is not None:
            self.put(self.alloc(1), header)
        new = self.alloc(n)
        for i in range(n):
            c = self.get(a + i)
            if c[0] == GCFWD:
                raise pimm.Unimplemented('gc: %s at %x partly copied' % (what, a))
            self.put(new + i, c)
            self.put(a + i, (GCFWD, new + i))
        return new

    def module(self, a):
        c = self.now(a)
        if c[0] != pimm.CDESC or (c[1] >> 24) & 7 != 6:
            raise pimm.Unimplemented('gc: no module at %x: %r' % (a, c))
        return self.block(a, (c[1] & 0xffffff) + 1, 'a module', 'module')

    def code(self, c):
        """A code address (a predicate's first instruction) moved with
        its module."""
        if self.where(c) != 'from':
            return c
        h = self.now(c - 2)
        if h[0] != pimm.PREDH:
            raise pimm.Unimplemented('gc: code at %x has no predicate head' % c)
        mod = c - 2 - (h[1] & 0xffffff)
        self.counts['code'] += 1
        return self.module(mod) + (c - mod)

    def string(self, a):
        c = self.now(a)
        if c[0] != pimm.CDESC or (c[1] >> 24) & 7 not in (0, 3, 4, 5):
            raise pimm.Unimplemented('gc: no string at %x: %r' % (a, c))
        return self.block(a, (c[1] & 0xffffff) + 1, 'a string', 'string')

    def long_vector(self, a):
        if self.where(a) != 'from':
            return a
        c = self.now(a)
        if c != (pimm.VDESC, a + 3) and not (c[0] == pimm.VDESC and self.fwd(a) is not None):
            raise pimm.Unimplemented('gc: no long vector at %x: %r' % (a, c))
        self.counts['long_vector'] += 1
        return self.data(a, 3 + self.now(a + 1)[1], head=3)

    def goal(self, g):
        if self.where(g) != 'from':
            return g
        n = G_ARGS + self.now(g + G_ARGN)[1]
        return self.block(g, n, 'a goal record', 'goal', (GCHDR, K_GOAL << 24 | n))

    def goals(self, g):
        """A list of goal records linked through G_LINK, each copied, in
        order; the new address of the first."""
        first = None
        while g:
            new = self.goal(g)
            if first is None:
                first = new
            g = self.get(new + G_LINK)[1]       # the copy's link is not yet moved
        return first if first is not None else 0

    def susp(self, s):
        return self.block(s, 2, 'a suspension record', 'susp', (GCHDR, K_SUSP << 24 | 2))

    def shoen(self, sh):
        if self.where(sh) != 'from':
            return sh
        was = self.fwd(sh)
        new = self.block(sh, SH_SIZE, 'a shoen record', 'shoen', (GCHDR, K_SHOEN << 24 | SH_SIZE))
        if was is None and self.get(new + SH_GOAL)[1]:
            self.counts['parked'] += 1
            self.goals(self.get(new + SH_GOAL)[1])      # its parked goals, with it
        return new

    def word(self, w):
        """The word with its address moved."""
        t, v = w
        k = t & ~1 if t < 0x20 else t
        if k in _IMMEDIATE or t in _IMMEDIATE_HIGH:
            return w
        if k == pimm.REF:
            return (t, self.data(v, 1))
        if k == pimm.LIST:
            return (t, self.data(v, 2))
        if pimm.VECT0 + 2 <= k <= pimm.VECT0 + 12:
            return (t, self.data(v, (k - pimm.VECT0) // 2))
        if k == pimm.VECT0 + 14:
            return (t, self.long_vector(v))
        if k == pimm.STRG:
            return (t, self.string(v))
        if k == pimm.HOOK:
            return (t, self.susp(v))
        if t == pimm.MOD:
            return (t, self.module(v))
        if t == pimm.COD:
            return (t, self.code(v))
        if t == pimm.SHREC:
            return (t, self.shoen(v))
        raise pimm.Unimplemented('gc: a word with tag %02x' % t)

    # ---- the scan --------------------------------------------------
    def fix_record(self, kind, r, n):
        get, put = self.get, self.put
        if kind == K_GOAL:
            st = get(r + G_STATUS)[1]
            if st >> 2:
                sh = self.shoen(self.m.load + (st >> 2))
                put(r + G_STATUS, (pimm.INT, (sh - self.m.load) << 2 | st & 3))
            code = get(r + G_CODE)[1]
            put(r + G_CODE, (pimm.INT, self.code(code)))
            for i in range(G_ARGS, n):
                put(r + i, self.word(get(r + i)))
            if code == self.merge_in:                   # arg 1: {INT, its merger record}
                self.counts['merge_in'] += 1
                rec = get(r + G_ARGS + 1)[1]
                put(r + G_ARGS + 1, (pimm.INT, self.data(rec, 3)))
            elif code in self.to_processor:             # arg N + 1: {INT, the code}
                self.counts['to_processor'] += 1
                i = r + G_ARGS + self.to_processor[code] + 1
                put(i, (pimm.INT, self.code(get(i)[1])))
        elif kind == K_SUSP:
            nx = get(r + S_NEXT)[1]
            if nx:
                put(r + S_NEXT, (pimm.INT, self.susp(nx)))
            put(r + S_GOAL, (pimm.INT, self.goal(get(r + S_GOAL)[1])))
        elif kind == K_SHOEN:
            p = get(r + SH_PARENT)[1]
            if p:
                put(r + SH_PARENT, (pimm.INT, self.shoen(p)))
            put(r + SH_REPORT, self.word(get(r + SH_REPORT)))
            g = get(r + SH_GOAL)[1]
            if g:
                put(r + SH_GOAL, (pimm.INT, self.goal(g)))     # copied with the shoen
        else:
            raise pimm.Unimplemented('gc: header kind %d' % kind)

    def scan(self):
        p = self.to
        while p < self.top:
            t, v = self.get(p)
            if t == GCHDR:
                n = v & 0xffffff
                self.fix_record(v >> 24, p + 1, n)
                p += 1 + n
            elif t == pimm.CDESC:
                typ = (v >> 24) & 7
                p += 1 if typ == 6 else 1 + (v & 0xffffff)   # a module's cells are scanned
            elif t == pimm.VDESC:
                self.put(p, (t, p + 3))
                p += 3
            else:
                self.put(p, self.word((t, v)))
                p += 1

    def links(self):
        """Each copied goal's G_LINK: its target's new address if it was
        copied, else 0."""
        p = self.to
        while p < self.top:
            t, v = self.get(p)
            if t == GCHDR:
                if v >> 24 == K_GOAL:
                    g = self.get(p + 1 + G_LINK)[1]
                    if g:
                        if not self.lo <= g < self.hp:
                            raise pimm.Unimplemented('gc: a goal linked to %x' % g)
                        f = self.fwd(g)
                        self.put(p + 1 + G_LINK, (pimm.INT, f if f is not None else 0))
                p += 1 + (v & 0xffffff)
            elif t == pimm.CDESC and (v >> 24) & 7 != 6:
                p += 1 + (v & 0xffffff)
            else:
                p += 1

    def run(self):
        m = self.m
        # the roots
        rq, mq, mwh = self.goals(m.rq), self.goals(m.mq), self.goals(m.mwh)
        mwt = self.goal(m.mwt) if m.mwt else 0
        self.counts['mq'], self.counts['mwh'] = int(mq != 0), int(mwh != 0)
        alarm = self.word(m.alarm_var) if m.alarm_var is not None else None
        self.counts['alarm'] = int(alarm is not None)
        waiting = []
        for c in m.scsi_waiting:
            waiting.append((self.word(c['word']), self.word(c['cdbw']),
                            [self.word(o) for o in c['outs']]))
        self.counts['scsi'] = len(waiting)
        cur = self.shoen(m.shoen) if m.shoen else 0
        self.counts['cur_shoen'] = int(cur != 0)
        self.scan()
        self.links()
        new_cells = [self.get(a) for a in range(self.to, self.top)]
        total = checksum(new_cells)
        # the from-space is dead: removed, so that a pointer into it
        # that the collector missed fails loud (KeyError) on the
        # reference; the to-space is kept where it is
        for a in range(self.lo, self.hp):
            dict.pop(self.mem, a, None)
        m.rq, m.mq, m.mwh, m.mwt = rq, mq, mwh, mwt
        if alarm is not None:
            m.alarm_var = alarm
        for c, (w, cdbw, outs) in zip(m.scsi_waiting, waiting):
            c['word'], c['cdbw'], c['outs'] = w, cdbw, outs
        m.shoen = cur
        for pc in [pc for pc in m.names if pc >= HEAP]:
            del m.names[pc]
        line = 'K gc %d %d %d %d %08x' % (self.lo - m.load, self.hp - m.load,
                                          self.to - m.load, self.top - m.load, total)
        m.heap_lo, m.hp = self.to, self.top
        m.gc_count = getattr(m, 'gc_count', 0) + 1
        m.gc_counts = self.counts
        if getattr(m, 'gc_dump', None) is not None:     # a test's: the new heap, cell by cell
            m.gc_dump.append(new_cells)
        m.event(line)
        return line


def collect(m):
    return Collector(m).run()
