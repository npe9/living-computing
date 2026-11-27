#!/usr/bin/env python3
"""Constraint-based inference of microinstruction field meanings: CEGIS
over SMT-LIB2, solved by the z3 binary (/opt/homebrew/bin/z3; there is
no Python z3 module here and none was installed).

Every unknown field value is a SELECTOR over a finite set of meanings
(hyp_space).  Held routines with a known contract (contracts()) are
executed symbolically under the selectors (Inst).  A selector assignment
survives only if every contract holds for ALL data.  Counterexample-
guided inductive synthesis: find an assignment that satisfies the
contracts on a finite pool of concrete examples (synthesis), check it
with symbolic data (verification), and add the counterexample to the
pool when verification fails.  The pool is shared between runs, since
examples are data and do not depend on the selectors.

The question the documents disagree on is in the hypothesis space as the
selector 'layout': Nakashima's thesis Fig. 3-25 (ADF 36-34, AS1F 33-31,
AS2F 30-29, ALF 28-27) against TR-733 fig. 4 (AS1F 36-34, AS2F 33-32,
ADF 31-29, ALF 28-26).  Each layout gets its own free meaning for each
of its own field values, so neither is helped by the other's numbering.

Results, labels and the per-selector table: docs/pu_microcode_inference.md
section 6.

Usage:
    python3 asm/pu_smt.py --check          pinned decisions
    python3 asm/pu_smt.py --measure        the decisions, unpinned
    python3 asm/pu_smt.py --table          every value of every pinned
                                           selector: survives, or which
                                           contracts eliminate it alone
    python3 asm/pu_smt.py --model          one surviving assignment
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mekbn                      # noqa: E402
from mekbn import field, regname  # noqa: E402
import pu_store                   # noqa: E402

Z3 = os.environ.get('Z3', '/opt/homebrew/bin/z3')

# ------------------------------------------------------------------ hypotheses
LATCHES = ['XR', 'YR', 'MDR1', 'MDR2', 'MAR1', 'MAR2']
SRC = ['zero'] + LATCHES            # an ALU input
DST = ['none'] + LATCHES            # a load destination (SD1F, SD2F, ADF)
OPS = ['add', 'sub', 'pass1', 'pass2']
CONDS = ['lt', 'le', 'eq', 'ne', 'gt', 'ge', 'never', 'always']
# Conditions on a tag: the MRB (tag bit 0) of the ALU result's tag, which
# for a word with an AS1 input and no operation is that input's tag.
# Offered only to the condition keys listed in TAG_CONDS (in every
# domain they cost --check about a minute): U2, 2026-11-27, contract
# 'reuse_kl1', CNDF 7 EM1 29.
TAG_CONDS = {'7_29': CONDS + ['mrb_on', 'mrb_off']}
STAMP = ['none', 'S1', 'ALU']       # what a TGIF bit stamps with the EM1 tag
BITS = [58, 59, 60, 61, 62]
SEL = ['none', 58, 59, 60]          # a select bit: set picks the second register
TR733 = {'AS1F': (36, 34), 'AS2F': (33, 32), 'ADF': (31, 29), 'ALF': (28, 26)}
GLOBAL = {
    'layout': ['thesis', 'tr733'],
    'vis': ['same', 'next'],        # phase 2 sees this word's phase-1 loads, or not
    'wtime': ['old', 'new'],        # a write stores the MDR as before / after phase 1
    'ctime': ['same', 'prev'],      # a transfer tests the condition its own word forms / the previous word's
    'endpol': ['b0=0 ends if cond', 'b0=0 ends if not cond'],
    'rd': BITS, 'wr': BITS, 'inc': ['none'] + BITS,
    'marsel': SEL, 'mdrsel': SEL, 'wdsel': SEL,
    'tg1': STAMP, 'tg2': STAMP,
    'dstsrc': ['ALU', 'S1'],
}
LIMIT = 1 << 20                     # data range: no overflow inside it
UNDF, REFO, INTO, LISTO = 8, 6, 0, 4  # kbn.TAGS


def tr(x, name):
    hi, lo = TR733[name]
    return x >> lo & ((1 << (hi - lo + 1)) - 1)


def condkey(x):
    c = field(x, 'CNDF')
    return '%x' % c if c != 7 else '7_%02x' % field(x, 'EM1')


def hyp_space(words):
    h = dict(GLOBAL)
    for x in words:
        for f, n in (('SD1F', 'sd1'), ('SD2F', 'sd2')):
            if field(x, f):
                h['%s_%d' % (n, field(x, f))] = DST
        h['th_adf_%d' % field(x, 'ADF')] = DST
        h['th_as1_%d' % field(x, 'AS1F')] = SRC
        h['th_as2_%d' % field(x, 'AS2F')] = SRC
        h['th_alf_%d' % field(x, 'ALF')] = OPS
        h['tr_adf_%d' % tr(x, 'ADF')] = DST
        h['tr_as1_%d' % tr(x, 'AS1F')] = SRC
        h['tr_as2_%d' % tr(x, 'AS2F')] = SRC
        h['tr_alf_%d' % tr(x, 'ALF')] = OPS
        h['cond_%s' % condkey(x)] = TAG_CONDS.get(condkey(x), CONDS)
    return h


HYP = {}


def is_(sel, meaning):
    return '(= %s %d)' % (sel, (HYP[sel] if sel in HYP else GLOBAL[sel]).index(meaning))


# ------------------------------------------------------------------ terms
def ite(c, a, b):
    return a if a == b else '(ite %s %s %s)' % (c, a, b)


def pite(c, a, b):
    return ite(c, a[0], b[0]), ite(c, a[1], b[1])


def lor(xs):
    xs = list(xs)
    return 'false' if not xs else xs[0] if len(xs) == 1 else '(or %s)' % ' '.join(xs)


REL = {'lt': '(< %s 0)', 'le': '(<= %s 0)', 'eq': '(= %s 0)', 'ne': '(not (= %s 0))',
       'gt': '(> %s 0)', 'ge': '(>= %s 0)'}


class Inst:
    """One contract instance: data variables, symbolic run, final state."""

    def __init__(self, sfx, words, cells):
        self.sfx, self.words = sfx, words
        self.data = []
        self.L = {n: (self.d('L%s_t' % n), self.d('L%s_v' % n)) for n in LATCHES}
        self.L0 = dict(self.L)
        self.RF, self.RF0 = {}, {}
        self.cells = {c: (self.d('A_' + c), (self.d('C%s_t' % c), self.d('C%s_v' % c))) for c in cells}
        self.default = (self.d('Cdef_t'), self.d('Cdef_v'))
        self.writes = []
        self.defs = []
        self.cond = ['(= %s 1)' % self.d('cprev')]     # c_-1: the word before the path
        for x in words:
            self.step(x)

    def d(self, name):
        full = '%s_%s' % (self.sfx, name)
        if full not in self.data:
            self.data.append(full)
        return full

    def nm(self, term, sort='Int'):
        """Name a compound term (define-fun) so terms stay linear in size."""
        if ' ' not in term:
            return term
        n = '%s_t%d' % (self.sfx, len(self.defs))
        self.defs.append('(define-fun %s () %s %s)' % (n, sort, term))
        return n

    def P(self, pair):
        return self.nm(pair[0]), self.nm(pair[1])

    def rf(self, name):
        if name not in self.RF:
            self.RF[name] = self.RF0[name] = (self.d('R%s_t' % name), self.d('R%s_v' % name))
        return self.RF[name]

    def mem(self, a):
        """The memory word at address term a after the writes so far."""
        t, v = self.default
        for ca, (ct, cv) in self.cells.values():
            t, v = ite('(= %s %s)' % (a, ca), ct, t), ite('(= %s %s)' % (a, ca), cv, v)
        for flag, wa, (wt, wv) in self.writes:
            c = '(and %s (= %s %s))' % (flag, wa, a)
            t, v = ite(c, wt, t), ite(c, wv, v)
        return self.P((t, v))

    def step(self, x):
        L = self.L
        em1, tg = field(x, 'EM1'), field(x, 'TGIF')
        set_bits = [b for b in BITS if x >> b & 1]

        def bitflag(sel, dom):
            return lor(is_(sel, b) for b in set_bits if b in dom)
        # phase 1: the register file (or an immediate) into the work registers
        sc1, sc2 = field(x, 'SC1F'), field(x, 'SC2F')
        s1 = self.rf(regname(x, sc1)) if sc1 else ('0', '0')
        if tg & 1:
            s1 = (ite(is_('tg1', 'S1'), str(em1), s1[0]), s1[1])
        if tg & 2:
            s1 = (ite(is_('tg2', 'S1'), str(em1), s1[0]), s1[1])
        imm = mekbn.sc2_immediate(x)
        s2 = ('0', str(imm)) if imm is not None else self.rf(regname(x, sc2)) if sc2 else ('0', '0')
        s1, s2 = self.P(s1), self.P(s2)
        p1 = dict(L)
        for n in LATCHES:
            if field(x, 'SD2F'):
                p1[n] = pite(is_('sd2_%d' % field(x, 'SD2F'), n), s2, p1[n])
            if field(x, 'SD1F'):
                p1[n] = pite(is_('sd1_%d' % field(x, 'SD1F'), n), s1, p1[n])
            p1[n] = self.P(p1[n])
        seen = {n: self.P(pite(is_('vis', 'same'), p1[n], L[n])) for n in LATCHES}
        # phase 2: the ALU, under each layout with that layout's own selectors
        alus = []
        for pre, f in (('th', lambda n: field(x, n)), ('tr', lambda n: tr(x, n))):
            def pick(sel):
                tv = ('0', '0')
                for n in LATCHES:
                    tv = pite(is_(sel, n), seen[n], tv)
                return tv
            a1, a2 = pick('%s_as1_%d' % (pre, f('AS1F'))), pick('%s_as2_%d' % (pre, f('AS2F')))
            op = '%s_alf_%d' % (pre, f('ALF'))
            v = ite(is_(op, 'add'), '(+ %s %s)' % (a1[1], a2[1]),
                    ite(is_(op, 'sub'), '(- %s %s)' % (a1[1], a2[1]),
                        ite(is_(op, 'pass1'), a1[1], a2[1])))
            t = ite(is_(op, 'pass2'), a2[0], a1[0])
            alus.append((self.P((t, v)), '%s_adf_%d' % (pre, f('ADF'))))
        r = pite(is_('layout', 'thesis'), alus[0][0], alus[1][0])
        if tg & 1:
            r = (ite(is_('tg1', 'ALU'), str(em1), r[0]), r[1])
        if tg & 2:
            r = (ite(is_('tg2', 'ALU'), str(em1), r[0]), r[1])
        r = self.P(r)
        ck = 'cond_%s' % condkey(x)
        c = 'false'
        for m in HYP.get(ck, CONDS):
            if m in REL:
                c = ite(is_(ck, m), REL[m] % r[1], c)
            elif m == 'always':
                c = ite(is_(ck, m), 'true', c)
            elif m in ('mrb_on', 'mrb_off'):
                c = ite(is_(ck, m), '(= (mod %s 2) %d)' % (r[0], m == 'mrb_on'), c)
        self.cond.append(self.nm(c, 'Bool'))
        new = dict(p1)
        for n in LATCHES:
            hit = '(ite %s %s %s)' % (is_('layout', 'thesis'), is_(alus[0][1], n), is_(alus[1][1], n))
            new[n] = pite(hit, r, new[n])
        if field(x, 'DSTF'):
            self.RF[regname(x, field(x, 'DSTF'))] = self.P(pite(is_('dstsrc', 'ALU'), r, s1))
        # memory: the strobe roles are selectors over this word's set CCF bits
        rd, wr, inc = bitflag('rd', BITS), bitflag('wr', BITS), bitflag('inc', BITS)
        m2, d2, w2 = bitflag('marsel', SEL), bitflag('mdrsel', SEL), bitflag('wdsel', SEL)
        mar = self.P(pite(m2, L['MAR2'], L['MAR1']))
        src = {n: pite(is_('wtime', 'old'), L[n], p1[n]) for n in ('MDR1', 'MDR2')}
        data = self.P(pite(w2, src['MDR2'], src['MDR1']))
        rd, wr, inc = self.nm(rd, 'Bool'), self.nm(wr, 'Bool'), self.nm(inc, 'Bool')
        m2, d2 = self.nm(m2, 'Bool'), self.nm(d2, 'Bool')
        got = self.mem(mar[1])
        self.writes.append((wr, mar[1], data))
        new['MDR2'] = pite('(and %s %s)' % (rd, d2), got, new['MDR2'])
        new['MDR1'] = pite('(and %s (not %s))' % (rd, d2), got, new['MDR1'])
        up = (mar[0], '(+ %s 1)' % mar[1])
        new['MAR2'] = pite('(and %s %s)' % (inc, m2), up, new['MAR2'])
        new['MAR1'] = pite('(and %s (not %s))' % (inc, m2), up, new['MAR1'])
        self.L = {n: self.P(v) for n, v in new.items()}

    def tested(self, i):
        """The condition word i's transfer tests (c_i or c_i-1, by ctime)."""
        return ite(is_('ctime', 'same'), self.cond[i + 1], self.cond[i])

    def ended(self):
        x = self.words[-1]
        em = field(x, 'EM')
        assert mekbn.jk(x) == 1 and em & mekbn.J1_COND and not em & mekbn.J1_JUMP
        c = self.tested(len(self.words) - 1)
        if_c = '(not %s)' % c if em & 1 else c
        return ite(is_('endpol', 'b0=0 ends if cond'), if_c, '(not %s)' % if_c)

    def ranges(self):
        out = []
        for v in self.data:
            if v.endswith('_t'):
                out.append('(and (>= %s 0) (< %s 64))' % (v, v))
            elif v.endswith('cprev'):
                out.append('(or (= %s 0) (= %s 1))' % (v, v))
            else:
                out.append('(and (> %s (- %d)) (< %s %d))' % (v, LIMIT, v, LIMIT))
        return out


# ------------------------------------------------------------------ contracts
def eq(a, b):
    return '(= %s %s)' % (a, b)


def contracts():
    """name -> (image, path, cells, spec, text, label).  spec(inst) gives
    (pre, post) term lists.  cprev = 0: the word before the path did not
    ask for a transfer (the operand checks of the decode passed)."""
    out = {}

    def alloc(e):
        p, (pt, pv) = e.cells['p']
        q = e.d('q')
        pre = [eq(e.RF0['R19'][1], p), eq(pv, q), '(distinct %s %s)' % (p, q), eq(e.d('cprev'), 0)]
        post = [eq(e.rf('R19')[1], q), eq(e.rf('W1c')[0], REFO), eq(e.rf('W1c')[1], p),
                eq(e.mem(p)[0], UNDF)]
        return pre, post
    out['alloc_1cell'] = ('img2', (0x3320, 0x3321, 0x3322, 0x3323), ['p'], alloc,
                          'pop the one-cell free list R19: R19 := mem[p].v, W1c := {REFo, p}, '
                          'mem[p].tag := UNDF', 'INFERRED contract (mekbn section 17, allocator index 1)')

    def setvar(dst, addr_from):
        def f(e):
            h = e.cells['h'][0]
            s = e.cells['s'][0]
            q = e.d('q')
            sv = e.RF0['R02'][1] if addr_from == 'R02' else e.L0['MAR1'][1]
            pre = [eq(e.RF0['R19'][1], h), eq(e.L0['MAR2'][1], h), eq(sv, s),
                   eq(e.cells['h'][1][1], q), '(distinct %s %s %s)' % (h, q, s), eq(e.d('cprev'), 0)]
            post = [eq(e.rf('R19')[1], q), eq(e.mem(h)[0], UNDF), eq(e.mem(s)[0], REFO),
                    eq(e.mem(s)[1], h), eq(e.rf(dst)[0], REFO), eq(e.rf(dst)[1], h)]
            return pre, post
        return f
    out['set_variable'] = ('img2', (0x318b, 0x318c, 0x318f), ['h', 's'], setvar('opda', 'MAR1'),
                           'new unbound cell h from R19 (= MAR2); {REFo, h} into the structure word '
                           '(MAR1) and opda', 'INFERRED contract (WAM set_variable; KL1 entry name)')
    out['write_variable'] = ('img2', (0x3195, 0x3196, 0x3199), ['h', 's'], setvar('opd9', 'R02'),
                             'as set_variable; the structure address from R02, operand 9',
                             'INFERRED contract (KL1 entry name)')

    def arith(dst, op, stamped):
        def f(e):
            a, b = e.d('a'), e.d('b')
            pre = [eq(e.L0['MDR1'][0], INTO), eq(e.L0['MDR2'][0], INTO), eq(e.L0['MDR1'][1], a),
                   eq(e.L0['MDR2'][1], b), eq(e.d('cprev'), 0)]
            post = ['(= %s (%s %s %s))' % (e.rf(dst)[1], op, a, b), '(not %s)' % e.tested(0),
                    e.ended()]
            if stamped:
                post.append(eq(e.rf(dst)[0], INTO))
            return pre, post
        return f
    for name, img, path, op, st in (('add_kl1', 'img2', (0x3a68, 0x3a69), '+', True),
                                    ('subtract_kl1', 'img2', (0x3a70, 0x3a71), '-', True),
                                    ('add_kl0', 'psi', (0x1120, 0x1121), '+', True),
                                    ('subtract_kl0', 'psi', (0x1130, 0x1131), '-', False)):
        out[name] = (img, path, [], arith('opdb', op, st),
                     'opdb := {INT, a %s b} for in-range INT operands in MDR1/MDR2; the first '
                     "word's conditional jump is not taken and the second word's conditional "
                     'end ends (falling through to the next word restores opdb: the overflow '
                     'exit)' % op,
                     'DOCUMENTED instruction; operands in MDR1/MDR2 INFERRED')

    def compare(rel, jumps):
        def f(e):
            a, b = e.d('a'), e.d('b')
            pre = [eq(e.L0['MDR1'][1], a), eq(e.L0['MDR2'][1], b), eq(e.d('cprev'), 0)]
            holds = '(not (= %s %s))' % (a, b) if rel == 'ne' else '(%s %s %s)' % (rel, a, b)
            ok = e.ended()
            if jumps:
                ok = '(and (not %s) %s)' % (e.tested(0), ok)
            return pre, ['(= %s %s)' % (ok, holds)]
        return f
    for name, img, path, rel, j in (('less_than_kl1', 'img2', (0x3a48, 0x3a49), '<', True),
                                    ('not_less_than_kl1', 'img2', (0x3a50, 0x3a51), '>=', True),
                                    ('equal_kl1', 'img2', (0x3a58, 0x3a59), '=', True),
                                    ('not_equal_kl1', 'img2', (0x3a60, 0x3a61), 'ne', True),
                                    ('equal_kl0', 'psi', (0x1000, 0x1001), '=', False)):
        out[name] = (img, path, [], compare(rel, j),
                     'succeeds (the second word ends; the first does not jump to the R04 := R11 '
                     'exit) iff a %s b' % rel, 'DOCUMENTED instruction; the exits read as failure INFERRED')

    return out


def side_contracts():
    """Contracts decided on their own, outside contracts() (in the joint
    set each one costs --check about a minute): name -> as contracts()."""
    out = {}

    def reuse(e):
        t = e.L0['MDR1'][0]
        pre = ['(or (= %s %d) (= %s %d))' % (t, LISTO, t, LISTO + 1), eq(e.d('cprev'), 0)]
        return pre, ['(= %s (= %s %d))' % (e.ended(), t, LISTO)]
    out['reuse_kl1'] = ('img2', (0x31ec, 0x31ed), [], reuse,
                        "put_reused_structure's other row with a list pointer in MDR1: the "
                        'second word ends (the cell reused in place) iff the MRB is off '
                        '(LISTo), and goes on to the allocating arm 31ee for LISTx',
                        'INFERRED contract (TR-466 4.2: a single-referenced input cons cell is '
                        'reused; thesis Fig. 3-23)')

    def execute_fast(e):
        # 4cc1 is a JMPF b to 4cc5, taken when the COND it tests holds
        # (pu.py CJUMP_TAKEN_ON); the contract: with no event pending it is
        # not taken, whatever the registers hold (R0d, MDR1, YR, ...)
        return [], ['(not %s)' % e.tested(1)]
    out['execute_fast'] = ('img2', (0x4cc0, 0x4cc1), [], execute_fast,
                           "execute's first two words with no asynchronous event pending: "
                           '4cc1 (JMPF b to 4cc5) is not taken for any register contents, so '
                           'the routine goes on to 4cc2-4cc3 (R04 := the label, end)',
                           'INFERRED contract (the slit check, polled once per reduction: '
                           'literature_gaps.md [P1] s.5.4; pu.py FLAG_CONDS)')
    return out


EXEC_DECIDED = (('layout', 'thesis'), ('th_as1_4', 'MDR1'), ('th_as2_0', 'zero'),
                ('th_alf_1', 'sub'), ('sd1_1', 'XR'), ('sd2_1', 'YR'), ('th_adf_0', 'none'),
                ('th_as2_1', 'YR'), ('th_as1_2', 'YR'))
SIDE_PINNED = {
    # U2 2026-11-27, third session (pu.py RULES['em1_29_mrb']): CNDF 7
    # EM1 29 over contract reuse_kl1 alone.  Every value relation,
    # 'never' and 'always' are eliminated; the MRB test survives up to
    # the global end polarity, and under the adopted one ('b0=0 ends if
    # cond', pu.py's j1 rules) only mrb_on.
    ('reuse_kl1', 'cond_7_29', None): ['mrb_on', 'mrb_off'],
    ('reuse_kl1', 'cond_7_29', 'b0=0 ends if cond'): ['mrb_on'],
    # U2 2026-11-27, fifth session (pu.py RULES['cjump_time'], FLAG_CONDS):
    # execute's 4cc0-4cc1 over contract execute_fast alone, with the
    # datapath values already decided fixed (EXEC_DECIDED: the thesis
    # layout; AS1F 4 MDR1, AS2F 0 zero, ALF 1 sub, 6.3 item 2; SD1F 1 XR,
    # SD2F 1 YR, ADF 0 none, mekbn / rassy; AS2F 1 YR, rassy; AS1F 2 YR,
    # pu.py RULES['as1f2_yr']).  Left free, a selector finds a degenerate
    # way out (ADF 0 = MDR1 makes 4cc1 compare R0d with itself).  With
    # CNDF 3 a relation on the ALU result (lt, pu.py's sign), only ctime
    # 'prev' survives; under 'same' CNDF 3 would have to be 'never'.
    # Under 'prev' the condition 4cc0 forms (CNDF 7 EM1 19) must be
    # 'never' for every register content: it does not depend on the ALU
    # result (R15 := YR), as a hardware flag (slit_check) that is clear.
    ('execute_fast', 'ctime', (('cond_3', 'lt'),) + EXEC_DECIDED): ['prev'],
    ('execute_fast', 'cond_3', (('ctime', 'same'),) + EXEC_DECIDED): ['never'],
    ('execute_fast', 'cond_7_19', (('ctime', 'prev'),) + EXEC_DECIDED): ['never'],
}


def side_check():
    global HYP
    sc = side_contracts()
    fails = []
    for (cn, sel, pol), want in SIDE_PINNED.items():
        cs = {cn: sc[cn]}
        HYP = hyp_space(words_of(sc[cn]))
        fixed = dict(pol) if isinstance(pol, tuple) else {'endpol': pol} if pol else {}
        got = [m for m in HYP[sel] if cegis(cs, dict(fixed, **{sel: m}))[0]]
        if got != want:
            fails.append('FAIL pu_smt %s over %s (fixed %s): got %r, pinned %r'
                         % (sel, cn, pol, got, want))
    return fails


def words_of(c):
    st = pu_store.stores()
    im = st.img2 if c[0] == 'img2' else st.psi
    return [im[a] for a in c[1]]


def build(c, sfx):
    e = Inst(sfx, words_of(c), c[2])
    pre, post = c[3](e)
    decl = ['(declare-const %s Int)' % v for v in e.data] + e.defs
    return e, decl, pre + e.ranges(), post


# ------------------------------------------------------------------ solver
CALLS = [0]


def run_z3(script):
    CALLS[0] += 1
    p = subprocess.run([Z3, '-in', '-T:120'], input=script, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    return p.stdout.split('\n')


def values(lines, names):
    """Parse (get-value) output: '((x 3)', ' (y (- 4)))'."""
    out = {}
    for ln in lines:
        s = ln.strip()
        while s.startswith('('):
            s = s[1:]
        if ' ' not in s:
            continue
        k, v = s.split(' ', 1)
        if k in names:
            neg = '-' in v
            v = ''.join(ch for ch in v if ch.isdigit())
            out[k] = -int(v) if neg else int(v)
    return out


def selector_decls(fixed):
    out = []
    for s, dom in HYP.items():
        out.append('(declare-const %s Int)' % s)
        out.append('(assert (and (>= %s 0) (< %s %d)))' % (s, s, len(dom)))
    for s, m in fixed.items():
        out.append('(assert %s)' % is_(s, m))
    return out


POOL = {}          # contract name -> counterexamples (data name without suffix -> int)


def cegis(cs, fixed=None, max_iter=60):
    """(True, model) if some selector assignment, with `fixed` held, meets
    every contract in cs for all data; (False, None) if none does."""
    global HYP
    HYP = hyp_space([x for c in cs.values() for x in words_of(c)])
    fixed = fixed or {}
    for _ in range(max_iter):
        lines = ['(set-option :produce-models true)'] + selector_decls(fixed)
        k = 0
        for n, c in cs.items():
            for ex in POOL.get(n, []):
                sfx = 'x%d' % k
                k += 1
                e, decl, pre, post = build(c, sfx)
                lines += decl
                lines += ['(assert (= %s %d))' % (v, ex.get(v[len(sfx) + 1:], 0)) for v in e.data]
                lines.append('(assert (=> (and %s) (and %s)))' % (' '.join(pre), ' '.join(post)))
        lines += ['(check-sat)', '(get-value (%s))' % ' '.join(HYP)]
        out = run_z3('\n'.join(lines))
        if out[0] != 'sat':
            if out[0] != 'unsat':
                raise RuntimeError('z3 synthesis: %s' % ' '.join(out[:3]))
            return False, None
        model = values(out[1:], set(HYP))
        # verification: one z3 run, one push/pop per contract
        vl = ['(set-option :produce-models true)'] + selector_decls({})
        vl += ['(assert (= %s %d))' % (s, v) for s, v in model.items()]
        order = []
        for n, c in cs.items():
            e, decl, pre, post = build(c, 'v')
            order.append((n, e))
            vl += ['(push)'] + decl + ['(assert (and %s))' % ' '.join(pre),
                                       '(assert (not (and %s)))' % ' '.join(post), '(check-sat)',
                                       '(get-value (%s))' % ' '.join(e.data), '(pop)']
        vo = run_z3('\n'.join(vl))
        blocks, cur = [], None
        for ln in vo:
            if ln in ('sat', 'unsat', 'unknown'):
                cur = [ln]
                blocks.append(cur)
            elif cur is not None:
                cur.append(ln)
        if len(blocks) != len(order) or any(b[0] == 'unknown' for b in blocks):
            raise RuntimeError('z3 verification: %s' % ' '.join(vo[:3]))
        bad = False
        for (n, e), blk in zip(order, blocks):
            if blk[0] == 'sat':
                vals = values(blk[1:], set(e.data))
                POOL.setdefault(n, []).append({v[2:]: vals.get(v, 0) for v in e.data})
                bad = True
        if not bad:
            return True, {s: HYP[s][v] for s, v in model.items()}
    raise RuntimeError('CEGIS did not converge in %d rounds' % max_iter)


# ------------------------------------------------------------------ decisions
PINNED_SELECTORS = ('layout', 'vis', 'wtime', 'ctime', 'endpol', 'rd', 'wr', 'inc', 'marsel',
                    'mdrsel', 'wdsel', 'tg1', 'tg2', 'dstsrc', 'sd1_1', 'sd1_4', 'sd1_5', 'sd1_6',
                    'th_adf_0', 'th_adf_1', 'th_adf_4', 'th_adf_7', 'th_as1_1', 'th_as1_4',
                    'th_as1_5', 'th_as1_6', 'th_as2_0', 'th_as2_3', 'th_alf_0', 'th_alf_1',
                    'cond_5', 'cond_7_0a', 'cond_7_09', 'cond_0', 'cond_b')


def decide(selectors=PINNED_SELECTORS, blame=False, contracts_=None):
    cs = contracts_ or contracts()
    ok, model = cegis(cs)
    out = {'satisfiable': ok}
    table = {}
    for sel in selectors:
        HYP.update(hyp_space([x for c in cs.values() for x in words_of(c)]))
        if sel not in HYP:
            continue
        dom = HYP[sel]
        surv = [m for m in dom if cegis(cs, {sel: m})[0]]
        out[sel] = surv
        if blame:
            gone = {}
            for m in dom:
                if m in surv:
                    continue
                alone = []
                for n in cs:
                    sub = {n: cs[n]}
                    if sel in hyp_space(words_of(cs[n])) and not cegis(sub, {sel: m})[0]:
                        alone.append(n)
                gone[m] = alone or ['(only jointly)']
            table[sel] = gone
    return out, table, model


# Pinned by --check (a decisive subset of the table, to keep the check
# near a minute; --table runs all of PINNED_SELECTORS, about 9 minutes).
# Surviving meanings, in domain order; docs/pu_microcode_inference.md s.6.
PINNED = {
    'satisfiable': True,
    'layout': ['thesis'],
    'wtime': ['old'],
    'ctime': ['prev'],
    'wr': [62],
    'marsel': [58],
    'mdrsel': [59],
    'tg1': ['S1'],
    'tg2': ['ALU'],
    'th_alf_0': ['add'],
    'th_alf_1': ['sub'],
    'cond_5': ['eq', 'ne'],
    'cond_7_0a': ['lt', 'ge'],
}


def check():
    got, _, _ = decide([k for k in PINNED if k != 'satisfiable'])
    fails = ['FAIL pu_smt %s: got %r, pinned %r' % (k, got.get(k), v)
             for k, v in PINNED.items() if got.get(k) != v]
    fails += side_check()
    for f in fails:
        print(f)
    print('pu_smt --check: %s (%d decisions; %d counterexamples, %d z3 runs)'
          % ('FAIL' if fails or not PINNED else 'PASS', len(PINNED) + len(SIDE_PINNED),
             sum(len(v) for v in POOL.values()), CALLS[0]))
    return 1 if fails or not PINNED else 0


def main(argv):
    if not argv or argv[0] == '--check':
        return check()
    if argv[0] == '--measure':
        import pprint
        pprint.pprint(decide()[0], width=100)
    elif argv[0] == '--table':
        got, table, _ = decide(blame=True)
        for sel, surv in got.items():
            if sel == 'satisfiable':
                print('all contracts satisfiable:', surv)
                continue
            print('%-11s survive %s' % (sel, surv))
            for m, by in table.get(sel, {}).items():
                print('%-11s   %-22s eliminated alone by %s' % ('', m, ', '.join(by)))
    elif argv[0] == '--model':
        ok, model = cegis(contracts())
        print('satisfiable:', ok, '; z3 runs', CALLS[0])
        for k in sorted(model or {}):
            print(k, model[k])
    elif argv[0] == '--contract':
        print(cegis({argv[1]: dict(contracts(), **side_contracts())[argv[1]]}))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
