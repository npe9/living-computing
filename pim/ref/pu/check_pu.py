#!/usr/bin/env python3
"""U1 check: held KL1 micro-routines on ref/pu/pu.py against ref/pimm/pimm.py.

For each case, one KL1-B instruction cell runs in both models from the
same state, and the results are compared as docs/pu_microcode_plan.md
"What the same as pimm.py can mean" defines:

  registers   pimm.py reg[i] against the PU's An[i], under an address
              renaming built as the run goes (firmware cell -> pimm.py
              cell, a bijection; a conflict FAILs);
  arguments   pimm.py argv[i] against the firmware cell R10 + i;
  heap        every cell pimm.py writes, against the firmware's write to
              the renamed address;
  sp          pimm.py sp against the value of R02.

Firmware writes nothing in pimm.py corresponds to are listed as
firmware-only (the free-list links are not touched by a pop; here they
are none so far).  A difference in a pointer's tag low bit (the MRB) is
FAIL unless the case declares it with its reason ('mrb').

Four more cases take the LAST cell of a free list: they pass when the
run enters the refill (3365-337f), which is not modelled; they are what
discriminates the condition rules.

Prints one line per case and a total; exit status 1 on any FAIL.
  python3 ref/pu/check_pu.py [-v] [--inject NAME]

Observed 2026-11-26: PASS, 23 cases, 51 held microinstructions (34 in
the 19 compared cases).  Injections (INJECT below; observed results, in
full, in ref/pu/README.md): tgif3_em1 FAILs write_nil only; w59_mdr1
put_variable only; write_same_word set_variable and write_variable;
opd_a_is_z set_variable and put_variable; cnd_em_swapped the four
last-cell cases only; odsf_swapped STOPs the ten pop cases.

The firmware is read from docs/nonlocal/psdpim.tar.Z (not in git).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pimm'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pu as PU  # noqa: E402
import setup as SU  # noqa: E402
import pimm  # noqa: E402

KLB, GMI = 0x23, 0x22
POINTER_TAGS = set([0x04, 0x05, 0x06, 0x07] + list(range(0x12, 0x20)))
# firmware-side regions (OURS): the goal record being built, the free lists
REC = 0xf1000000
FREE1 = 0xf2000000      # one-cell list, R19
FREE2 = 0xf3000000      # two-cell list, R1a
NFREE = 8


def seed_lists(p, n=NFREE):
    """OURS: free lists already built, in the shape the firmware's own
    pushes and refill write (each free cell's first word {VECT0x, next},
    MEASURED section 15; the last {ATOMo, 0}, as the refill's 3368)."""
    for head, base, step in ((0x19, FREE1, 1), (0x1a, FREE2, 2)):
        for i in range(n):
            a = base + i * step
            p.mem[a] = (PU.VECT0x, a + step) if i < n - 1 else (PU.ATOM, 0)
        p.r[head] = (PU.REF, base)


def cell(op, x=0, y=0, z=0, tag=KLB):
    return (tag, op << 24 | x << 16 | y << 8 | z)


def opcode(name):
    fw = CTX['fw']
    return fw.kl1_entries()[name][0] & 255


# (decode-table name, operands (x, y, z) or a 24-bit constant, registers
#  {i: value} beyond the default, declared differences)
A0 = 0xe0010000                 # a heap address present in both models
CASES = [
    ('set_value', (3, 5, 0), {}, ()),
    ('set_integer', (2, 0xff, 0xfe), {}, ()),
    ('set_atom[03]', 0x000123, {}, ()),
    ('set_nil', (4, 0, 0), {}, ()),
    ('put_value', (1, 6, 0), {}, ()),
    ('put_integer', (7, 0x12, 0x34), {}, ()),
    ('put_atom[05]', 0x000456, {}, ()),
    ('put_nil', (2, 0, 0), {}, ()),
    ('write_value', (5, 0, 0), {}, ()),
    ('write_integer', 0xfffffe, {}, ()),
    ('write_atom', 0x00789a, {}, ()),
    ('write_nil', (0, 0, 0), {}, ()),
    ('set_variable', (2, 9, 0), {}, ()),
    # pimm.py makes the element itself the variable, "our choice: the
    # machine's is not known" (i_write_variable); the firmware (3195-3199)
    # takes a new cell from R19, makes it UNDF, and writes a REF to it at
    # the structure pointer: 'indirect'.
    ('write_variable', (4, 0, 0), {}, ('indirect',)),
    ('put_variable', (3, 8, 0), {}, ()),
    ('put_list', (6, 0, 0), {}, ('mrb',)),
    ('put_vector_N[01]', (6, 0, 0), {}, ('mrb',)),
    ('put_vector_N[02]', (5, 0, 0), {}, ('mrb',)),
    ('put_vector_N[00]', (5, 0, 0), {}, ()),
    # The pop of the LAST free cell: the exhaustion test must fire and the
    # routine go on to the refill (3378 for the one-cell list, 337d for the
    # two-cell list), which is not run (README "First routine that would
    # not run").  These cases pass when the run stops inside 3365-337f.
    ('set_variable', (2, 9, 0), {}, ('exhaust',)),
    ('put_variable', (3, 8, 0), {}, ('exhaust',)),
    ('put_list', (6, 0, 0), {}, ('exhaust', 'mrb')),
    ('put_vector_N[01]', (6, 0, 0), {}, ('exhaust', 'mrb')),
]
REFILL = range(0x3365, 0x3380)
CTX = {}


def make_cell(name, ops):
    t = GMI if CTX['fw'].kl1_entries()[name][0] >> 8 == 2 else KLB
    op = opcode(name)
    if isinstance(ops, int):
        return (t, op << 24 | ops)
    return cell(op, *ops, tag=t)


def initial_regs():
    r = {i: (pimm.INT, 100 + i) for i in range(32)}
    r[5] = (pimm.REF, A0)
    r[6] = (pimm.ATOM, 77)
    return r


class Rename:
    def __init__(self):
        self.f2p, self.p2f = {}, {}

    def same(self, fv, pv, mrb_ok, notes, what):
        """Compare a firmware value with a pimm.py value."""
        if fv is None or pv is None:
            return fv == pv
        ft, fa = fv
        pt, pa = pv
        if ft != pt:
            if mrb_ok and ft & ~1 == pt & ~1 and ft in POINTER_TAGS:
                notes.append('%s: MRB firmware %02x, pimm.py %02x' % (what, ft, pt))
            else:
                return False
        if ft not in POINTER_TAGS:
            return fa == pa
        return self.pair(fa, pa)

    def pair(self, fa, pa):
        if fa in self.f2p or pa in self.p2f:
            return self.f2p.get(fa) == pa and self.p2f.get(pa) == fa
        self.f2p[fa], self.p2f[pa] = pa, fa
        return True


def run_case(name, ops, regs_extra, declared, verbose=False):
    fw = CTX['fw']
    ir = make_cell(name, ops)
    regs = initial_regs()
    regs.update(regs_extra)
    # --- pimm.py
    m = pimm.Machine(CTX['image'])
    for i, w in regs.items():
        m.reg[i] = w
    sp0 = A0 + 0x100
    m.sp = sp0
    m.tr = []
    pc = len(m.cells) + 64
    dict.__setitem__(m.mem, m.load + pc, ir)
    t, v = ir
    getattr(m, 'i_' + SU.base(name))(pc, (v >> 16) & 255, (v >> 8) & 255, v & 255, v & 0xffff)
    # --- the PU
    p = PU.PU(fw)
    p.ir = ir
    for i, w in regs.items():
        p.an[i] = w
    p.r[SU.R_REC] = (0, REC)
    p.r[SU.R_SP] = (0, sp0)
    seed_lists(p, 1 if 'exhaust' in declared else NFREE)
    fresh = set(p.mem)
    start = SU.setup(p, name)
    nwords = p.run(start)
    # --- compare
    rn = Rename()
    for a in range(A0 - 0x1000, A0 + 0x1000):   # cells present in both: the identity
        rn.f2p[a] = rn.p2f[a] = a
    notes, fails = [], []
    mrb_ok = 'mrb' in declared
    matched = set()
    for line in m.tr:
        f = line.split()
        k, i, w = f[0], int(f[1]), f[2]
        pv = (int(w[:2], 16), int(w[2:], 16))
        if k == 'R':
            if not rn.same(p.an.get(i), pv, mrb_ok, notes, 'reg %d' % i):
                fails.append('reg %d: firmware %s, pimm.py %s' % (i, fmt(p.an.get(i)), fmt(pv)))
        elif k == 'A':
            fa = REC + i
            matched.add(fa)
            if not rn.same(p.mem.get(fa), pv, mrb_ok, notes, 'argv %d' % i):
                fails.append('argv %d: firmware [R10+%d] %s, pimm.py %s'
                             % (i, i, fmt(p.mem.get(fa)), fmt(pv)))
        elif k == 'M':
            pa = m.load + i
            fa = rn.p2f.get(pa)
            if fa is None:
                # the cell pimm.py made: pair it with the firmware write of the same value
                cands = [a for (_, a, d) in p.writes if a not in matched and a not in rn.f2p
                         and rn.same(d, pv, mrb_ok, [], 'probe')]
                if len(cands) != 1:
                    fails.append('heap %x: no single firmware cell (%d)' % (pa, len(cands)))
                    continue
                fa = cands[0]
                rn.pair(fa, pa)
            matched.add(fa)
            fv = p.mem.get(fa)
            if 'indirect' in declared and fv and fv[0] == pimm.REF and fv[1] in p.mem \
                    and fv[1] not in rn.f2p and p.mem[fv[1]] == pv:
                # the firmware puts a reference to a new cell where pimm.py
                # puts the cell itself: the same term after dereference
                notes.append('heap %x: firmware {REF, new cell %x}, pimm.py the cell itself'
                             % (pa, fv[1]))
                matched.add(fv[1])
                rn.f2p.pop(fa, None)
                rn.p2f.pop(pa, None)
                rn.pair(fv[1], pa)
                continue
            if not rn.same(fv, pv, mrb_ok, notes, 'heap'):
                fails.append('heap %x: firmware %s, pimm.py %s' % (pa, fmt(p.mem.get(fa)), fmt(pv)))
    # registers the firmware wrote that pimm.py did not
    touched = {int(l.split()[1]) for l in m.tr if l[0] == 'R'}
    for i, w in p.an.items():
        if i not in touched and w != regs.get(i):
            fails.append('reg %d written by the firmware only: %s' % (i, fmt(w)))
    # sp
    fsp = p.r.get(SU.R_SP)
    psp = m.sp
    if fsp is None or rn.f2p.get(fsp[1], fsp[1] if fsp[1] not in fresh else None) != psp:
        if not (fsp and fsp[1] in rn.f2p and rn.f2p[fsp[1]] == psp):
            fails.append('sp: firmware R02 %s, pimm.py %x' % (fmt(fsp), psp))
    only = [(u, a, d) for (u, a, d) in p.writes if a not in matched]
    if verbose:
        for u, x in p.trace:
            print('   %04x %016x' % (u, x))
        for u, a, d in only:
            print('   firmware-only write at %04x: [%x] <- %s' % (u, a, fmt(d)))
        for nline in notes:
            print('   note: %s' % nline)
    return nwords, fails, notes, only


def fmt(w):
    return 'None' if w is None else '%02x:%08x' % w


# Fault injections (--inject NAME): one decoded rule changed in this
# process only (no file is edited).  The observed results are in the
# module docstring.
INJECT = {
    'tgif3_em1': lambda: PU.RULES.update(tgif3_tag='EM1'),
    'w59_mdr1': lambda: PU.RULES.update(w59_mdr2='MDR1'),
    'write_same_word': lambda: PU.RULES.update(write_old_mdr=False),
    'opd_a_is_z': lambda: PU.RULES['opd_fields'].update({0xa: 'z'}),
    'cnd_em_swapped': lambda: PU.COND_RULES.update({9: PU._cnd_tag_eq('EM2'),
                                                    0xb: PU._cnd_tag_eq('EM1')}),
    'odsf_swapped': lambda: setattr(SU, 'ODSF_MAR', {0: 'MAR1', 1: 'MAR2'}),
}


def main(argv):
    import kbndis
    import mekbn
    verbose = '-v' in argv
    if '--inject' in argv:
        name = argv[argv.index('--inject') + 1]
        INJECT[name]()
        print('injected: %s' % name)
    CTX['fw'] = mekbn.Firmware()
    CTX['image'] = kbndis.Image()
    total = bad = words = 0
    for name, ops, extra, declared in CASES:
        total += 1
        try:
            n, fails, notes, only = run_case(name, ops, extra, declared, verbose)
        except PU.Unmodelled as e:
            if 'exhaust' in declared and e.upc in REFILL:
                print('ok   %-20s last cell: stops in the refill, %s' % (name, e))
                words += e.words
                continue
            bad += 1
            print('STOP %-20s at %s' % (name, e))
            continue
        if 'exhaust' in declared:
            bad += 1
            print('FAIL %-20s last cell taken without entering the refill' % name)
            continue
        words += n
        if fails:
            bad += 1
            print('FAIL %-20s %d words: %s' % (name, n, '; '.join(fails)))
        else:
            print('ok   %-20s %d words%s%s' % (name, n, ', firmware-only writes %d' % len(only)
                                                if only else '',
                                                ', declared: ' + '; '.join(notes) if notes else ''))
    print('%s: %d cases, %d held microinstructions executed, %d not ok'
          % ('PASS' if not bad else 'FAIL', total, words, bad))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
