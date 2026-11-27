#!/usr/bin/env python3
"""Lockstep: the single-precision floating point built-ins (docs/float.md).

    python3 ref/pimm/lockstep_float.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_float.py compare
    python3 ref/pimm/lockstep_float.py --reference       the reference alone

A float is the immediate word {30h, IEEE single} (docs/float.md).  The
instructions (assembler/inst_tab.kl1, docs/kl1_encoding.md):
  23:FC f_r_r  0 floating_point_equal, 1 _not_equal, 2 _less_than,
               3 _not_less_than (inputs y, z); 4 floating_point_to_integer,
               5 integer_to_floating_point (input y, output z)
  23:FD f_r_r_r  0 floating_point_add, 1 _subtract, 2 _multiply,
               3 _divide (inputs y, z; output the second cell's top
               byte, klb_opr.kl1:275-282)
  22:CE, 22:CF  the body forms b_* of the same, the same operands
In a guard what the manual calls "Fail, Exception" fails the guard
(e-builtin.tex:20, 423-610): a non-float, inf - inf, 0 * inf, 0/0,
inf/inf, an integer overflow.  Overflow gives infinity, x/0 infinity
(e-builtin.tex:509, 561).  Rounding to nearest even: INFERENCE
(docs/float.md).  The body forms are run on valid operands only (their
exception is refused on both models, as b_divide's).

Code of OURS, in the heap as lockstep_sord.py's:
  arith  f(X, Y, R) :- floating_point_OP(X, Y, Z) | R = Z.
         f(X, Y, R) :- true | R = 999.
         (try_me_else @4; 23:FD fn, 0, 1; {INT, 3 << 24}; get_value 2, 3;
         proceed; get_integer 2, 999; proceed)
  cmp    c(X, Y, R) :- floating_point_CMP(X, Y) | R = 1.
         c(X, Y, R) :- true | R = 0.
  conv   v(X, R) :- CONV(X, Z) | R = Z.   v(X, R) :- true | R = 999.
  body   b(X, Y, R) :- true | b_floating_point_OP(X, Y, Z), R = Z.
         (22:CF fn, 0, 1; {INT, 3 << 24}; get_value 2, 3; proceed)
  bconv  w(X, R) :- true | b_CONV(X, Z), R = Z.

The expected words are IEEE single constants written here by hand, not
computed by either model.

Observed fault injections (2026-11-26; each into a backup restored
with cp and checked with cmp):
  pimm.py to_f32 rounding toward zero (--reference): arith0, body0,
    arith3, body3, toflt, btoflt fail, one ulp low (4b800001 for
    4b800002, 3eaaaaaa for 3eaaaaab, 4effffff for 4f000000, ...);
    nothing else
  pimm.py integer_to_floating_point writing an INT word (--reference):
    toflt fails (tag 0 for 30h), nothing else; btoflt, a separate
    instruction, passes
  PimmFBox.bsv Rnd_Zero for Rnd_Nearest_Even (the lockstep): the trace
    differs at its first rounded result, the core writing R 3
    304b800001 where the reference writes 304b800002 (arith0)
  PimmStages.bsv the conversion's cell tag_INTo for tag_FLTo: the
    trace differs at R 2 004b800000 against 304b800000 (toflt's first
    row)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=18, lines=4299)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
F = lambda h: (pimm.FLT, h)                         # noqa: E731
KLB, BLT = 0x23, 0x22
NO = 999                                            # the second clause's R

ONE, TWO, THREE = 0x3f800000, 0x40000000, 0x40400000
P15, P225 = 0x3fc00000, 0x40100000
INF, NINF, NZERO = 0x7f800000, 0xff800000, 0x80000000
BIG = 0x7f61b1e6                                    # 3.0e38
TEN = 0x41200000
T24, T24P2 = 0x4b800000, 0x4b800001                 # 2^24, 2^24 + 2
FMIN, FMIN1 = 0x00800000, 0x00800001                # least normal, and the next

# (X, Y, [add, subtract, multiply, divide]) as words, NO for a failure
ARITH = [
    (F(ONE), F(THREE), [F(0x40800000), F(0xc0000000), F(THREE), F(0x3eaaaaab)]),
    (F(P15), F(P225), [F(0x40700000), F(0xbf400000), F(0x40580000), F(0x3f2aaaab)]),
    # ties to even: 2^24 + 1 is 2^24; 2^24 + 2 + 1 is 2^24 + 4
    (F(T24), F(ONE), [F(T24), F(0x4b7fffff), F(T24), F(T24)]),
    (F(T24P2), F(ONE), [F(0x4b800002), F(T24), F(T24P2), F(T24P2)]),
    # overflow to infinity; 3e38 / 10 = 3e37
    (F(BIG), F(TEN), [F(BIG), F(BIG), F(INF), F(0x7db48e52)]),
    # x/0: the infinity of the signs; 0 * x
    (F(ONE), F(0), [F(ONE), F(ONE), F(0), F(INF)]),
    (F(0xbf800000), F(0), [F(0xbf800000), F(0xbf800000), F(NZERO), F(NINF)]),
    # invalid: inf + -inf, inf - inf, 0 * inf, 0/0, inf/inf
    (F(INF), F(NINF), [NO, F(INF), F(NINF), NO]),
    (F(INF), F(INF), [F(INF), NO, F(INF), NO]),
    (F(0), F(INF), [F(INF), F(NINF), NO, F(0)]),
    (F(0), F(0), [F(0), F(0), F(0), NO]),
    # subnormal results: FMIN / 4 exact; FMIN1 / 2 a tie, to even
    (F(FMIN), F(0x40800000), [F(0x40800000), F(0xc0800000), F(0x01800000), F(0x00200000)]),
    (F(FMIN1), F(TWO), [F(TWO), F(0xc0000000), F(0x01000001), F(0x00400000)]),
    # not floats
    (I(1), F(ONE), [NO, NO, NO, NO]),
    (F(ONE), (pimm.ATOM, 0), [NO, NO, NO, NO]),
]
# (X, Y, [equal, not_equal, less_than, not_less_than]) as 1/0
CMP = [
    (F(ONE), F(TWO), [0, 1, 1, 0]),
    (F(TWO), F(ONE), [0, 1, 0, 1]),
    (F(ONE), F(ONE), [1, 0, 0, 1]),
    (F(NZERO), F(0), [1, 0, 0, 1]),
    (F(INF), F(BIG), [0, 1, 0, 1]),
    (F(NINF), F(0xbf800000), [0, 1, 1, 0]),
    (I(1), F(ONE), [0, 0, 0, 0]),
]
# floating_point_to_integer: (X, R)
TOINT = [(F(0xc0700000), I(-3)), (F(0x40700000), I(3)), (F(0x4effffff), I(2147483520)),
         (F(0x4f000000), NO), (F(0xcf000000), I(-2147483648)), (F(0xcf000001), NO),
         (F(INF), NO), (F(NZERO), I(0)), (I(5), NO)]
# integer_to_floating_point: (X, R)
TOFLT = [(I(16777217), F(0x4b800000)), (I(16777219), F(0x4b800002)), (I(-1), F(0xbf800000)),
         (I(0), F(0)), (I(2147483647), F(0x4f000000)), (I(-2147483648), F(0xcf000000)),
         (I(100), F(0x42c80000)), ((pimm.ATOM, 0), NO), (F(ONE), NO)]

PARTS = (['arith%d' % fn for fn in range(4)] + ['cmp%d' % fn for fn in range(4)]
         + ['toint', 'toflt'] + ['body%d' % fn for fn in range(4)] + ['btoint', 'btoflt']
         + ['passive', 'active'])
# unification by bit pattern (e-syntax.tex:247): (X, Y, R) for the guard
# X = Y (wait_value; R 1 if it succeeds); a vector given as a list of
# its elements
PASSIVE = [(F(ONE), F(ONE), 1), (F(0), F(NZERO), 0), (F(ONE), I(ONE), 0),
           ([F(ONE), I(2)], [F(ONE), I(2)], 1), ([F(0)], [F(NZERO)], 0)]
# the body X = Y (get_value) on equal floats, and on two vectors of them
ACTIVE = [(F(P15), F(P15)), ([F(P15), F(TWO)], [F(P15), F(TWO)])]


def valid_body(rows, k):
    """the rows whose operands are floats and whose op is valid"""
    return [(x, y, r[k]) for x, y, r in rows if r[k] != NO]


def expect():
    e = {}
    for fn in range(4):
        e['arith%d' % fn] = [r[fn] for _x, _y, r in ARITH]
        e['cmp%d' % fn] = [I(r[fn]) for _x, _y, r in CMP]
        e['body%d' % fn] = [r for _x, _y, r in valid_body(ARITH, fn)]
    e['toint'] = [r for _x, r in TOINT]
    e['toflt'] = [r for _x, r in TOFLT]
    e['btoint'] = [r for _x, r in TOINT if r != NO]
    e['btoflt'] = [r for _x, r in TOFLT if r != NO]
    e['passive'] = [I(r) for _x, _y, r in PASSIVE]
    e['active'] = [I(1) for _x in ACTIVE]
    return {k: [I(NO) if w == NO else w for w in v] for k, v in e.items()}


def heap_code(s, words, names):
    """as lockstep_sord.py: one vector's cells, or two made one after
    the other"""
    s.vector(15, 4, words[:6])
    if len(words) > 6:
        s.vector(14, 10, words[6:])
    m = s.live()
    at = s.live_slot[15][1] - m.load
    got = [m.opname(at + i) for i in range(len(words)) if words[i][0] != pimm.INT]
    assert got == names, got
    return at


GET_NO = lambda r: (KLB, 0xb9 << 24 | r << 16 | NO)       # noqa: E731  get_integer r, 999
PROCEED = (KLB, 0x60 << 24)
GETV = lambda a, b: (KLB, 0xbc << 24 | a << 16 | b << 8)   # noqa: E731  get_value a, b
TRY4 = (KLB, 0x68 << 24 | 2)                               # try_me_else @4 (pc + 2 + c16)
FNAMES = ('add', 'subtract', 'multiply', 'divide')
CNAMES = ('equal', 'not_equal', 'less_than', 'not_less_than')


def run3(s, code, x, y):
    s.argc(1, x)
    s.argc(2, y)
    s.newvar(2)
    s.arg(3, 2)
    s.spawn(code, 3)
    s.run()
    s.out(2)


def run2(s, code, x):
    s.argc(1, x)
    s.newvar(1)
    s.arg(2, 1)
    s.spawn(code, 2)
    s.run()
    s.out(1)


def script():
    s = driver.Script()
    for fn in range(4):
        s.label('arith%d' % fn)
        code = heap_code(s, [(KLB, 0x68 << 24 | 3),               # try_me_else @5
                             (KLB, 0xfd << 24 | fn << 16 | 0 << 8 | 1), I(3 << 24),
                             GETV(2, 3), PROCEED, GET_NO(2), PROCEED],
                         ['try_me_else', 'floating_point_' + FNAMES[fn], 'get_value',
                          'proceed', 'get_integer', 'proceed'])
        for x, y, _r in ARITH:
            run3(s, code, x, y)
    for fn in range(4):
        s.label('cmp%d' % fn)
        code = heap_code(s, [TRY4, (KLB, 0xfc << 24 | fn << 16 | 0 << 8 | 1),
                             (KLB, 0xb9 << 24 | 2 << 16 | 1), PROCEED,
                             (KLB, 0xb9 << 24 | 2 << 16 | 0), PROCEED],
                         ['try_me_else', 'floating_point_' + CNAMES[fn], 'get_integer',
                          'proceed', 'get_integer', 'proceed'])
        for x, y, _r in CMP:
            run3(s, code, x, y)
    for part, fn, rows, name in (('toint', 4, TOINT, 'floating_point_to_integer'),
                                 ('toflt', 5, TOFLT, 'integer_to_floating_point')):
        s.label(part)
        code = heap_code(s, [TRY4, (KLB, 0xfc << 24 | fn << 16 | 0 << 8 | 2),
                             GETV(1, 2), PROCEED, GET_NO(1), PROCEED],
                         ['try_me_else', name, 'get_value', 'proceed', 'get_integer',
                          'proceed'])
        for x, _r in rows:
            run2(s, code, x)
    for fn in range(4):
        s.label('body%d' % fn)
        code = heap_code(s, [(BLT, 0xcf << 24 | fn << 16 | 0 << 8 | 1), I(3 << 24),
                             GETV(2, 3), PROCEED],
                         ['b_floating_point_' + FNAMES[fn], 'get_value', 'proceed'])
        for x, y, _r in valid_body(ARITH, fn):
            run3(s, code, x, y)
    for part, fn, rows, name in (('btoint', 0, TOINT, 'b_floating_point_to_integer'),
                                 ('btoflt', 1, TOFLT, 'b_integer_to_floating_point')):
        s.label(part)
        code = heap_code(s, [(BLT, 0xce << 24 | fn << 16 | 0 << 8 | 2), GETV(1, 2), PROCEED],
                         [name, 'get_value', 'proceed'])
        for x, r in rows:
            if r != NO:
                run2(s, code, x)

    def given(n, v, slot):
        if isinstance(v, list):
            s.vector(slot, slot + 1, v)
            s.arg(n, slot)
        else:
            s.argc(n, v)

    def run_u(code, x, y):
        given(1, x, 0)
        given(2, y, 3)
        s.newvar(6)
        s.arg(3, 6)
        s.spawn(code, 3)
        s.run()
        s.out(6)
    s.label('passive')
    code = heap_code(s, [TRY4, (KLB, 0xa4 << 24 | 0 << 16 | 1 << 8),
                         (KLB, 0xb9 << 24 | 2 << 16 | 1), PROCEED,
                         (KLB, 0xb9 << 24 | 2 << 16 | 0), PROCEED],
                     ['try_me_else', 'wait_value', 'get_integer', 'proceed', 'get_integer',
                      'proceed'])
    for x, y, _r in PASSIVE:
        run_u(code, x, y)
    s.label('active')
    code = heap_code(s, [GETV(0, 1), (KLB, 0xb9 << 24 | 2 << 16 | 1), PROCEED],
                     ['get_value', 'get_integer', 'proceed'])
    for x, y in ACTIVE:
        run_u(code, x, y)
    return s


def check(s, m, parts):
    bad = []
    outs = {}
    for label, w in s.outs:
        w = m.deref(w)
        outs.setdefault(label, []).append(None if m.unbound(w) else (w[0] & ~1, w[1]))
    if list(parts) != list(PARTS):
        return [('parts', list(parts))]
    for k, want in expect().items():
        if outs.get(k) != want:
            got = outs.get(k) or []
            diff = [(i, g, w) for i, (g, w) in enumerate(zip(got, want)) if g != w]
            bad.append((k, diff[:3] or (len(got), len(want))))
        if 'E fail' in parts[k] or 'E unimp' in parts[k] or 'E susp' in parts[k]:
            bad.append((k, 'a reduction failed, suspended or was refused'))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s, s.machine, kept)
        print(bad, len(kept), n)
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep float', PINNED)
    if not ok:
        return 1
    bad = check(s, m, kept)
    if bad:
        print('pimm lockstep float: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep float: PASS (the single-precision float built-ins on the Bluespec '
          'core (mkPimmFBox), %d parts, %d trace lines identical to the reference model: '
          'add, subtract, multiply, divide, the four comparisons and the two conversions, '
          'guard and body, rounding to nearest even, overflow, x/0, the invalid cases '
          'failing, subnormal results)' % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
