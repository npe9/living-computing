#!/usr/bin/env python3
"""Lockstep: the instructions met on the way from the login to the
shell's prompt (2026-11-24): unbound, the four double-precision integer
built-ins, the guards module, extended_floating_point,
bignum_less_than and bignum_not_less_than, apply of a vector of seven
or more, enqueue_goal of more than 16 arguments.

    python3 ref/pimm/lockstep_login.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_login.py compare
    python3 ref/pimm/lockstep_login.py --reference       the reference alone

Each was the stop of `longrun_ipl.py --go --fep` in turn, in modules
the IPL loads (none has a site in the IPL image).  Sources: pimm.py at
each i_*.  The expected values are from the manual's text as quoted
there (PIMOS manual e-builtin.tex), worked by hand, not read from
either model; the module's size from asm/kbndis.py's table.

Parts (the code marked OURS is cells the bench writes into the heap):
  unbound       at its stub (22:EF): X unbound gives {0, the variable's
                address, X}; X = 5 gives {5}.
  extended      add_extended, subtract_extended, multiply_extended,
                divide_extended at their stubs (22:B2..B5), unsigned:
                ffffffffh + 2 = carry 1, 1; 1 - 2 = borrow 1,
                ffffffffh; 10000h * 10000h = 1, 0; ffffffffh *
                ffffffffh = fffffffeh, 1; 1:5 / 7 = 613566757
                remainder 2 (2^32 + 5 = 7 * 613566757 + 2); an unbound
                X waits, then 3 + 4 = 0, 7.
  module        OURS, try_me_else; module 0, 2; get_value 1, 2;
                proceed; suspend: scsi_fep_util's module object gives
                its size, 174 (kbndis); 5 fails; a variable waits and
                the module gives 174.
  extended float  OURS, try_me_else; extended_floating_point (23:6E,
                function 8) 0, 1; proceed; suspend: 5 and an atom
                fail; a variable waits and 5 fails.
  bignum        OURS, try_me_else; bignum_less_than 0, 1 (then
                bignum_not_less_than); put_integer 3, 1; get_value 2,
                3; proceed; suspend: R = 1 when the guard holds.  Pairs:
                [1] [2]; [2] [1]; [1, 0] [5] (the longer is the
                larger); [5] [1, 0]; [] [1]; [3, 4] [3, 4]; [3, 4] [3,
                5]; [ffffffffh] [1] (unsigned); [0, 1] [5] (a leading
                zero), a 16-bit string, the integer 5: both fail.  Then
                less_than with B1 unbound waits, and [] gives R = 1.
  apply long    OURS, a predicate head of arity 7, then get_value 0, 6;
                proceed: apply at its stub with a vector of 7 laid out
                as the linker's ({VDESC, ..}, 7, 7, the elements),
                element 6 = 5: element 0 becomes 5.
  enqueue 17    OURS, set_value 1..11, 0..10; enqueue_goal 17, @13;
                proceed; @13: get_value 0, 16; proceed.  Spawned with
                X ten times and a vector of 7 (its element 6 = 5) as
                the 11th: the goal of 17 has the vector spread, so X
                = 5.
  external 12   OURS, set_value 1..11, 0..10; enqueue_goal_external 12,
                the label the image's own descriptor of
                scsi_fep_util:device_abnormal/1 (the one
                scsi_fep_file:check_send_status/6 executes; reached
                from the heap by a negative label); proceed.  Spawned
                with V = {_, _, _} ten times and {7, 8} as the 11th:
                device_abnormal(V) leaves V = {_, 5, 0} (lockstep_ext.py
                reads it from the object code).  The spread itself is
                compared with the reference only through the goal
                record's writes: device_abnormal reads r0 alone.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv),
2026-11-24, each restored from a copy (checksums compared after), the
first difference:
  unbound: the address one too many       unbound, line 16: M .. 8001 for 8000
  unbound: a variable taken as {X}        unbound, line 25 (the next
                                          allocation one cell low)
  add_extended: no carry                  extended, line 21: R 4 0 for 1
  multiply_extended: halves swapped       extended, line 85
  divide_extended: quotient and remainder swapped  extended, line 152
  module: the size one too many           module, line 25: R 2 af for ae
  extended_floating_point succeeds        extended float, line 23: proceed
                                          for suspend
  bignum: the lengths not compared        bignum, line 167
  bignum: a leading zero word accepted    bignum, line 565
  bignum: words compared signed           bignum, line 477
  apply of 7: elements from the descriptor  apply long, line 37
  enqueue_goal: a long vector refused     enqueue 17, line 107: E unimp
  enqueue_goal_external: the spread then a goal of the label (not
    looked up)                            external 12, line 99
  enqueue_goal_external: the spread one element late  external 12,
                                          line 95: A 11 8 for 7
NOT caught: the vector's size not checked against the arguments left
over (spreadInfo): every vector here has the right size, and a wrong
one is a refusal, not run.  Not run: enqueue_goal_external of more
than 16.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=8, lines=1600)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB = 0x23
S = pimm.signed


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    stubs = pimm.Machine().stubs
    s = driver.Script()
    want = []

    def part(name, exp):
        want.append((name, exp))

    def spawn(addr, *slots):
        for i, k in enumerate(slots):
            s.arg(i + 1, k)
        s.spawn(addr, len(slots))
        s.run()

    def cells(code):
        """code in consecutive heap cells (slots 0..): its address"""
        for k in range(len(code)):
            s.newvar(k)
        m = s.live()
        a0 = s.live_slot[0][1]
        assert [s.live_slot[k][1] for k in range(len(code))] == list(range(a0, a0 + len(code)))
        for k, c in enumerate(code):
            s.unifyc(k, c)
        s.live()
        return a0 - m.load

    def long_vec(slot, n, elems):
        for k in range(n + 3):
            s.newvar(k)
        s.live()
        a0 = s.live_slot[0][1]
        assert [s.live_slot[k][1] for k in range(n + 3)] == list(range(a0, a0 + n + 3))
        s.unifyc(0, (pimm.VDESC, a0 + 3))
        s.unifyc(1, I(n))
        s.unifyc(2, I(n))
        for i, e in elems.items():
            if isinstance(e, tuple) and e[0] == 'slot':
                s.unify(3 + i, e[1])
            else:
                s.unifyc(3 + i, I(e))
        s._op(driver.PTR, slot, 0, (pimm.VECT0 + 15, 0))

    # 1. unbound(X, ^R) at its stub
    s.label('unbound')
    s.newvar(10)
    s.newvar(11)
    s.live()
    xaddr = s.live_slot[10][1]
    spawn(stubs['unbound']['addr'], 10, 11)
    s.out(11)
    s.setslot(10, I(5))
    s.newvar(11)
    spawn(stubs['unbound']['addr'], 10, 11)
    s.out(11)
    part('unbound', [(0, S(xaddr), None), (5,)])

    # 2. the double-precision integers at their stubs
    s.label('extended')

    def ext(name, *ins):
        for k, v in enumerate(ins):
            if isinstance(v, tuple):
                s.arg(1 + k, v[1])
            else:
                s.argc(1 + k, I(v))
        s.newvar(14)
        s.newvar(15)
        s.arg(len(ins) + 1, 14)
        s.arg(len(ins) + 2, 15)
        s.spawn(stubs[name]['addr'], len(ins) + 2)
        s.run()
    ext('add_extended', 0xffffffff, 2)
    s.out(14)
    s.out(15)
    ext('subtract_extended', 1, 2)
    s.out(14)
    s.out(15)
    ext('multiply_extended', 0x10000, 0x10000)
    s.out(14)
    s.out(15)
    ext('multiply_extended', 0xffffffff, 0xffffffff)
    s.out(14)
    s.out(15)
    ext('divide_extended', 1, 5, 7)
    s.out(14)
    s.out(15)
    s.newvar(13)
    ext('add_extended', ('slot', 13), 4)
    s.out(14)
    s.unifyc(13, I(3))
    s.run()
    s.out(14)
    s.out(15)
    part('extended', [1, 1, 1, -1, 1, 0, S(0xfffffffe), 1, 613566757, 2, None, 0, 7])

    # 3. the guard module(X, ^Size)
    s.label('module')
    at = cells([(KLB, 0x68 << 24 | 2),                 # try_me_else @4
                (KLB, 0xfb << 24 | 0 << 16 | 2 << 8),  # module 0, 2
                (KLB, 0xbc << 24 | 1 << 16 | 2 << 8),  # get_value 1, 2
                (KLB, 0x60 << 24),                     # proceed
                (KLB, 0x69 << 24 | 2 << 16 | 0xfffa)])  # suspend 2, @0
    m = s.live()
    assert [m.opname(at + i) for i in range(5)] == [
        'try_me_else', 'module', 'get_value', 'proceed', 'suspend']
    mod = [x for x in im.mods if x['name'] == 'scsi_fep_util'][0]
    modobj = (pimm.MOD, im.load + mod['addr'] + 1)
    s.setslot(10, modobj)
    s.newvar(11)
    spawn(at, 10, 11)
    s.out(11)
    s.setslot(10, I(5))
    s.newvar(11)
    spawn(at, 10, 11)
    s.out(11)
    s.newvar(10)
    s.newvar(11)
    spawn(at, 10, 11)
    s.out(11)
    s.unifyc(10, modobj)
    s.run()
    s.out(11)
    part('module', [mod['length'], None, None, mod['length']])

    # 4. the guard extended_floating_point(X, ^NewX)
    s.label('extended float')
    at = cells([(KLB, 0x68 << 24 | 1),                 # try_me_else @3
                (KLB, 0x6e << 24 | 8 << 16 | 0 << 8 | 1),  # extended_floating_point 0, 1
                (KLB, 0x60 << 24),                     # proceed
                (KLB, 0x69 << 24 | 2 << 16 | 0xfffb)])  # suspend 2, @0
    m = s.live()
    assert [m.opname(at + i) for i in range(4)] == [
        'try_me_else', 'extended_floating_point', 'proceed', 'suspend']
    for v in (I(5), A('normal')):
        s.setslot(10, v)
        s.newvar(11)
        spawn(at, 10, 11)
    s.newvar(10)
    s.newvar(11)
    spawn(at, 10, 11)
    s.out(11)
    s.unifyc(10, I(5))
    s.run()
    part('extended float', [None])

    # 5. bignum_less_than, bignum_not_less_than
    s.label('bignum')
    codes = []
    for op in (0xb6, 0xb7):
        at = cells([(KLB, 0x68 << 24 | 3),                 # try_me_else @5
                    (KLB, op << 24 | 0 << 16 | 1 << 8),    # bignum_(not_)less_than 0, 1
                    (KLB, 0x31 << 24 | 3 << 16 | 1),       # put_integer 3, 1
                    (KLB, 0xbc << 24 | 2 << 16 | 3 << 8),  # get_value 2, 3
                    (KLB, 0x60 << 24),                     # proceed
                    (KLB, 0x69 << 24 | 3 << 16 | 0xfff9)])  # suspend 3, @0
        m = s.live()
        assert [m.opname(at + i) for i in range(6)] == [
            'try_me_else', 'bignum_less_than' if op == 0xb6 else 'bignum_not_less_than',
            'put_integer', 'get_value', 'proceed', 'suspend']
        codes.append(at)
    pairs = [([1], [2], True), ([2], [1], False), ([1, 0], [5], False), ([5], [1, 0], True),
             ([], [1], True), ([3, 4], [3, 4], False), ([3, 4], [3, 5], True),
             ([0xffffffff], [1], False), ([0, 1], [5], None), (16, [1], None), (5, [1], None)]
    exp = []

    def operand(slot, v):
        if v == 16:
            s.string(slot, 16, [1, 2])
        elif isinstance(v, int):
            s.setslot(slot, I(v))
        else:
            s.string(slot, 32, v)
    for b1, b2, lt in pairs:
        for k, at in enumerate(codes):
            operand(10, b1)
            operand(11, b2)
            s.newvar(12)
            spawn(at, 10, 11, 12)
            s.out(12)
            exp.append(None if lt is None or lt != (k == 0) else 1)
    s.newvar(10)
    s.string(11, 32, [1])
    s.newvar(12)
    spawn(codes[0], 10, 11, 12)
    s.out(12)
    s.string(9, 32, [])
    s.unify(10, 9)
    s.run()
    s.out(12)
    part('bignum', exp + [None, 1])

    # 6. apply(Code, Args) with Args a vector of 7
    s.label('apply long')
    at = cells([(pimm.PREDH, 7 << 24),
                I(0),
                (KLB, 0xbc << 24 | 0 << 16 | 6 << 8),  # get_value 0, 6
                (KLB, 0x60 << 24)]) + 2                # proceed
    m = s.live()
    assert [m.opname(at), m.opname(at + 1)] == ['get_value', 'proceed']
    s.setslot(14, (pimm.COD, m.load + at))
    s.newvar(15)
    long_vec(12, 7, {0: ('slot', 15), 6: 5})
    spawn(stubs['apply']['addr'], 14, 12)
    s.out(15)
    s.out(12)
    part('apply long', [5, (5, None, None, None, None, None, 5)])

    # 7. enqueue_goal 17: the 11th argument a vector of 7, spread
    s.label('enqueue 17')
    code = [(KLB, 0x14 << 24 | i << 16 | (i - 1) << 8) for i in range(1, 12)]   # set_value i, i-1
    code += [(KLB, 0x63 << 24 | 17 << 16 | 0),         # enqueue_goal 17, @13
             (KLB, 0x60 << 24),                        # proceed
             (KLB, 0xbc << 24 | 0 << 16 | 16 << 8),    # get_value 0, 16
             (KLB, 0x60 << 24)]                        # proceed
    at = cells(code)
    m = s.live()
    assert [m.opname(at + i) for i in range(10, 15)] == [
        'set_value', 'enqueue_goal', 'proceed', 'get_value', 'proceed']
    s.newvar(15)
    long_vec(10, 7, {6: 5})
    spawn(at, *([15] * 10 + [10]))
    s.out(15)
    part('enqueue 17', [5])

    # 8. enqueue_goal_external 12: the 11th argument a vector of 2,
    #    spread, then the predicate found through the image's own
    #    descriptor of scsi_fep_util:device_abnormal/1 (the one
    #    scsi_fep_file:check_send_status/6 executes)
    s.label('external 12')
    site = pimm.predicate(im, 'scsi_fep_file', 'check_send_status/6')
    site = next(pc for pc in range(site, site + 40)
                if im.cells[pc][0] == KLB and im.cells[pc][1] >> 24 == 0x62)
    desc = site + 2 + pimm.sx16(im.cells[site][1] & 0xffff)
    code = [(KLB, 0x14 << 24 | i << 16 | (i - 1) << 8) for i in range(1, 12)]   # set_value i, i-1
    code += [None, (KLB, 0x60 << 24)]                 # enqueue_goal_external 12; proceed
    for k in range(len(code)):
        s.newvar(k)
    m = s.live()
    a0 = s.live_slot[0][1] - m.load
    c16 = desc - (a0 + 11 + 2)
    assert -32768 <= c16 < 0
    code[11] = (KLB, 0x66 << 24 | 12 << 16 | (c16 & 0xffff))
    for k, c in enumerate(code):
        s.unifyc(k, c)
    m = s.live()
    assert [m.opname(a0 + i) for i in range(10, 13)] == [
        'set_value', 'enqueue_goal_external', 'proceed']
    assert m.external(a0 + 11, c16 & 0xffff, 'test') == pimm.predicate(im, 'scsi_fep_util',
                                                                   'device_abnormal/1')
    s.vector(14, 0, [None, None, None])
    s.vector(15, 4, [I(7), I(8)])
    spawn(a0, *([14] * 10 + [15]))
    s.out(14)
    part('external 12', [(None, 5, 0)])
    return s, want


# part: (reductions that end in a failure, in a suspension)
ENDS = {'unbound': (0, 0), 'extended': (0, 0), 'module': (1, 1), 'extended float': (3, 1),
        'bignum': (14, 1), 'apply long': (0, 0), 'enqueue 17': (0, 0), 'external 12': (0, 0)}
# part: (the instruction that must be taken, how often at least)
TAKEN = {'unbound': ('unbound', 2), 'extended': ('add_extended', 2),
         'module': ('module', 4), 'extended float': ('extended_floating_point', 4),
         'bignum': ('bignum_less_than', 13), 'apply long': ('apply', 1),
         'enqueue 17': ('enqueue_goal', 1), 'external 12': ('enqueue_goal_external', 1)}
OPCODE = {'unbound': '22ef', 'add_extended': '22b2', 'module': '23fb',
          'extended_floating_point': '236e', 'bignum_less_than': '23b6', 'apply': '22f1',
          'enqueue_goal': '2363', 'enqueue_goal_external': '2366'}


def check(s, m, want, parts):
    bad = []
    outs = {}
    for label, w in s.outs:
        outs.setdefault(label, []).append(w)
    for name, exp in want:
        got = [None if m.unbound(w) else m.term(w) for w in outs.get(name, [])]
        if got != exp:
            bad.append((name, got, exp))
        lines = parts.get(name, [])
        ends = (lines.count('E fail'), lines.count('E susp'))
        if ends != ENDS[name]:
            bad.append((name, 'fails, suspensions', ends, ENDS[name]))
        op, least = TAKEN[name]
        n = sum(1 for ln in lines if ln.startswith('I ') and ln.split()[2].startswith(OPCODE[op]))
        if n < least:
            bad.append((name, op, 'taken %d times' % n))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        parts = dict(s.play())
        print(check(s, s.machine, want, parts), len(parts), sum(len(v) for v in parts.values()))
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep login',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, want, kept)
    if bad:
        print('pimm lockstep login: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep login: PASS (unbound, the double-precision integers, the guards '
          'module, extended_floating_point and the bignum comparisons, apply of 7, '
          'enqueue_goal of 17 on the Bluespec core: %d parts, %d trace lines identical '
          'to the reference model)' % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
