#!/usr/bin/env python3
"""The reference models alone, one PE (pimm.py) and the multi-PE model
(pimm_pe.py, a System of one PE): two more of the IFS sweep's stops
(docs/ifs_apps.md 4, 2026-11-27, after ref_node_alert.py's three), and
the model's half of a third.

    python3 ref/pimm/ref_prio_list.py      ends `ref prio list: PASS ...`

1. `enqueue_goal_with_priority` of more than 11 arguments (H9-07's four
   rows: `(0, 3000), 12 arguments`).  The compiler packs a goal with a
   pragma as it packs a plain one: normalize_body_goal(Goal@Pragma)
   calls pack_body_goal first (PIMOS library/compiler/newnorm.kl1
   907-909), which puts the arguments from the 11th on into a vector in
   the 11th (pack.kl1 13-29, max_goal_slots 11), and the instruction's
   arity is the unpacked goal's (the Label F/A, newnorm.kl1 893-901).
   So the vector is spread as enqueue_goal spreads it (pimm.py
   spread_args, lockstep_pack.py); the priority is still dropped (one
   ready queue).  Both models: pimm_pe.py takes pimm.Machine's.
2. The guard `list(X)`, 23:E3 r (library/assembler/inst_tab.kl1 190):
   "Succeeds if X is a list.  Suspend: If X is uninstantiated.  Fail:
   If X is anything other than a list" (PIMOS manual e-builtin.tex
   62-68, PRINTED); [] is not a list (PDSS emulate.c 685 KL1B_LIST,
   WAIT_AND_CHECK_TYPE1(LIST), NIL the atom 0, atom.h 8; VPIM
   interpreter/klb_index.psl.c 117-127 klb_is_list).  Met by mmi after
   `" Now intializing DIS?? "`.
3. A body unification failing inside a shoen (cohlex, dulcinea: `a goal
   failed inside a shoen`, refused before): the exception
   unification_failure, number 10, Info {Pe, DataX, DataY} "without
   Caller" (PIMOS kernel/builtin/excpt_tbl.kl1 56, 209-215; VPIM
   functions/f_reduce_exception_handler.psl.c 79-96, the number 2257
   and its tag bit 0x04000000, 2283), reported by the path a reduction
   failure takes (pimm.py Machine.exception); the goal ends.  What they
   met was a FEP stand-in gap, not this (the root directory refused,
   docs/ifs_apps.md 4); this is the model's half.

The code, cells in the heap of a bare machine of each model:
  q(_, P, V) :- true | t(1, 2, .., 10, V)@priority(P)   (V the packed
      vector of t's 11th and 12th arguments, {R, 12}):
      set_integer 1..10, 1..10; set_value 11, r2;
      enqueue_goal_with_priority r1, @t (arity 12); proceed
  t(A1, .., A10, R, K) :- true | A1 = 1, A10 = 10, K = 12, R = 1:
      get_integer r0, 1; get_integer r9, 10; get_integer r11, 12;
      get_integer r10, 1; proceed
  l(X, R) :- list(X) | R = 1.  otherwise.  l(_, R) :- true | R = 0.
      try_me_else @4; list r0; get_integer r1, 1; proceed;
      @4: otherwise 3, @0; get_integer r1, 0; proceed
The parts, R worked by hand:
  q(_, 3000, {R, 12})         R = 1 (t's r10 and r11 are the vector's
                              elements, r0..r9 the ten integers)
  q(_, 3000, {R, 13})         t fails (K = 12 against 13): R unbound,
                              the failure reported (outside a shoen)
  l([a], R)                   R = 1
  l([], R) l(a, R) l(5, R) l({a}, R) l("ab", R)    R = 0 each
  l(V, R)                     waits on V; V = [1|2]: R = 1
  l(W, R)                     waits on W; W = []: R = 0
  u(X) :- true | X = a, its goal in a started shoen (mask -1, resource
      2^30, built as create_shoen leaves one): get_atom r0, a; proceed
  u(b)                        the shoen's report: {2, 10, {0, b, a},
                              NewCode, NewArgv}; apply(NewCode, NewArgv)
                              waits (Suspend)
  u(a)                        no exception: terminated (12) its report
  u(b), mask 1 << 25 (reduction_failure's bit alone)    refused, `an
                              exception (tag 4000000) no shoen accepts`

Observed fault injections (each into a private copy of ref/pimm, this
script run on it, 2026-11-27; the failures listed are all of them):
  the old refusal (n > 11)               q {R, 12} refused, `(0, 3000), 12
                                         arguments`, each model (2 lines)
  the vector not spread                  q {R, 12}: t's r11 the stale 0,
                                         `unify (0, 0) (0, 12)` (2 lines)
  the vector spread one late (the 11th   q {R, 12} and {R, 13}: R bound to
    and 12th swapped)                    the 12/13 meant for K (4 lines)
  list: [] taken as a list               l([]) and l(W), W = [] answer 1
                                         (4 lines)
  list: an unbound X fails, no wait      l(V) and l(W) answer 0 at once
                                         (6 lines: V's waiting and answer,
                                         W's waiting)
  list: not there (the sweep's stop)     every list part refused, `list
                                         at ..` (16 lines)
  unification failure: the old refusal  u(b) both parts refused, `a goal
                                         failed inside a shoen` (4 lines)
  unification failure: X and Y swapped   u(b): Info {0, a, b} (2 lines)
  unification failure numbered 9 (as a   u(b): number 9; and the mask of
    reduction failure, its tag 1 << 25)  1 << 25 accepts it (4 lines)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pimm  # noqa: E402
import pimm_pe  # noqa: E402

I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB = 0x23


def klb(op, x=0, y=0, c16=0):
    return (KLB, op << 24 | x << 16 | (y << 8 if y else c16 & 0xffff))


QCODE = ([klb(0x11, k, c16=k) for k in range(1, 11)]       # set_integer k, k
         + [klb(0x14, 11, 2),                             # set_value 11, r2
            klb(0x64, 1, c16=1),                          # enqueue_goal_with_priority r1, @t
            (KLB, 12 << 24),                              # its arity
            klb(0x60),                                    # proceed
            klb(0xb9, 0, c16=1),                          # t: get_integer r0, 1
            klb(0xb9, 9, c16=10),                         # get_integer r9, 10
            klb(0xb9, 11, c16=12),                        # get_integer r11, 12
            klb(0xb9, 10, c16=1),                         # get_integer r10, 1
            klb(0x60)])                                   # proceed
QNAMES = ['set_integer'] * 10 + ['set_value', 'enqueue_goal_with_priority', None, 'proceed'] \
    + ['get_integer'] * 4 + ['proceed']
LCODE = [(KLB, 0x68 << 24 | 2),                    # try_me_else @4
         klb(0xe3, 0),                             # list r0
         klb(0xb9, 1, c16=1),                      # get_integer r1, 1
         klb(0x60),                                # proceed
         (KLB, 0x6a << 24 | 3 << 16 | 0xfffa),     # otherwise 3, @0
         klb(0xb9, 1, c16=0),                      # get_integer r1, 0
         klb(0x60)]                                # proceed
LNAMES = ['try_me_else', 'list', 'get_integer', 'proceed', 'otherwise', 'get_integer', 'proceed']


def pe():
    return pimm_pe.System(pimm.Machine(), 1).pes[0]


def place(m, code, names):
    a = m.alloc(len(code))
    for i, c in enumerate(code):
        m.mem[a + i] = c
    pc = a - m.load
    got = [m.opname(pc + i) for i, n in enumerate(names) if n]
    assert got == [n for n in names if n], got
    return pc


def term(m, w):
    w = m.deref(w)
    return None if m.unbound(w) else m.term(w)


def go(m, pc, args):
    """run to the end; the refusal's or the failure's text, or None"""
    try:
        m.run(pc, args)
    except pimm.Unimplemented as e:
        return 'refused: %s' % e
    except pimm.Fail as e:
        return 'failed: %s' % e
    except Exception as e:      # Suspend: goals left waiting
        return '%s: %s' % (type(e).__name__, e)
    return None


def check(name, make):
    bad = []
    m = make()
    q = place(m, QCODE, QNAMES)
    answers = 0
    for k, want, fails in ((12, 1, False), (13, None, True)):
        r = m.new_var()
        v, a = m.vnew(2)
        m.mem[a], m.mem[a + 1] = r, I(k)
        out = go(m, q, [I(0), I(3000), v])
        got = term(m, r)
        answers += 1
        if got != want or (out is not None) != fails:
            bad.append((name, 'q {R, %d}' % k, got, out))
    lc = place(m, LCODE, LNAMES)

    def lst(label, x, want, bind=None):
        r = m.new_var()
        out = go(m, lc, [x, r])
        if bind is not None:
            if term(m, r) is not None:
                bad.append((name, label + ', waiting', term(m, r)))
            m.unify(x, bind)
            out = go(m, None, [])
        if term(m, r) != want or out is not None:
            bad.append((name, label, term(m, r), out))

    _c, ca = m.vnew(2)              # a list cell [a]: car, cdr
    cell = (pimm.LIST + 1, ca)
    m.mem[ca], m.mem[ca + 1] = (pimm.ATOM, 0x55), pimm.NIL
    lst('l([a])', cell, 1)
    vec, va = m.vnew(1)
    m.mem[va] = (pimm.ATOM, 0x55)
    for label, x in (('l([])', pimm.NIL), ('l(a)', (pimm.ATOM, 0x55)), ('l(5)', I(5)),
                     ('l({a})', vec), ('l("ab")', string(m, 'ab'))):
        lst(label, x, 0)
    _d, da = m.vnew(2)
    m.mem[da], m.mem[da + 1] = I(1), I(2)
    lst('l(V), V = [1|2]', m.new_var(), 1, (pimm.LIST + 1, da))
    lst('l(W), W = []', m.new_var(), 0, pimm.NIL)
    return bad, answers + 9


UCODE = [(KLB, (0xc0 | 0) << 24 | 0x55),     # u(X) :- true | X = a: get_atom r0, a
         klb(0x60)]                          # proceed
UNAMES = ['get_atom', 'proceed']
A, B = (pimm.ATOM, 0x55), (pimm.ATOM, 0x56)


def shoen(m, mask):
    """a started shoen of the root, built as create_shoen and
    start_shoen leave one (pimm.py i_create_shoen's f), with 2^30 of
    resource (none would park its goal: taken_check): its record and
    the report stream's variable"""
    sh = m.alloc(pimm.SH_SIZE)
    for k, v in ((pimm.SH_COUNT, 0), (pimm.SH_STATUS, pimm.STARTED), (pimm.SH_PARENT, 0),
                 (pimm.SH_GOAL, 0), (pimm.SH_REDUCTIONS, 0), (pimm.SH_REMOVE, 0),
                 (pimm.SH_MASK, mask), (pimm.SH_RSC_HI, 0), (pimm.SH_RSC_LO, 1 << 30),
                 (pimm.SH_RSC_FLAGS, 0)):
        m.mem[sh + k] = I(v)
    rep = m.new_var()
    m.mem[sh + pimm.SH_REPORT] = rep
    return sh, rep


def check_unify(name, make):
    """u(b) in a shoen: the exception unification_failure reported, its
    Info {0, b, a}, and the handler's goal apply(NewCode, NewArgv) left
    waiting; u(a) in one: terminated its only report; u(b) in a shoen
    whose mask lacks the tag: refused"""
    bad = []
    m = make()
    uc = place(m, UCODE, UNAMES)
    for label, x, mask, want in (('u(b) in a shoen', B, 0xffffffff, 'reported'),
                                 ('u(a) in a shoen', A, 0xffffffff, 'none'),
                                 ('u(b), the mask without the tag', B, 1 << 25, 'refused')):
        sh, rep = shoen(m, mask)
        m.record(pimm.READY, uc, [x], shoen=sh)
        m.mem[sh + pimm.SH_COUNT] = I(1)
        out = go(m, None, [])
        r = m.deref(rep)
        if want == 'refused':
            if not (out or '').startswith('refused: an exception (tag 4000000)'):
                bad.append((name, label, out))
            continue
        if want == 'none':
            # the shoen ends, terminated (12) its one report (the earlier
            # part's handler goal still waits: Suspend)
            if m.unbound(r) or term(m, r) != ('|', pimm.REPORT_TERMINATED, None):
                bad.append((name, label, term(m, r), out))
            continue
        if m.unbound(r) or r[0] & ~1 != pimm.LIST:
            bad.append((name, label, 'no report', out))
            continue
        msg = m.deref(m.mem[r[1]])
        el = [m.deref(m.mem[m.vbase(msg) + i]) for i in range(m.vsize(msg) or 0)]
        info = [m.deref(m.mem[m.vbase(el[2]) + i]) for i in range(3)] if len(el) == 5 else None
        if len(el) != 5 or el[0] != I(2) or el[1] != I(10) or info != [I(0), B, A] \
                or not (out or '').startswith('Suspend'):
            bad.append((name, label, el, info, out))
    return bad


def string(m, text):
    """an 8-bit string word (pimm.Machine.make_string)"""
    return m.make_string(8, [ord(ch) for ch in text])


def main():
    bad, n = [], 0
    for name, make in (('pimm', pimm.Machine), ('pimm_pe', pe)):
        b, k = check(name, make)
        bad += b + check_unify(name, make)
        n += k + 3
    if bad:
        print('ref prio list: FAIL %d: %r' % (len(bad), bad))
        return 1
    print('ref prio list: PASS (enqueue_goal_with_priority of 12 arguments spreads the packed '
          'vector as enqueue_goal does, a failing goal still fails; the guard list(X) on a list '
          'cell, [], an atom, an integer, a vector, a string, waiting on an unbound X; a body '
          'unification failing in a shoen reported as unification_failure {0, X, Y}; on '
          'pimm.py and pimm_pe.py, %d parts)' % n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
