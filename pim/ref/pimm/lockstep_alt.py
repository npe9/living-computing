#!/usr/bin/env python3
"""Lockstep: read_eagerly (`alternatively`), not_equal, wait_vector_0/1/4/6, jump,
set_marked_variable.

    python3 ref/pimm/lockstep_alt.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_alt.py compare
    python3 ref/pimm/lockstep_alt.py --reference       the reference alone

Four guard-side instructions the reference model had alone, on real
predicates of the IPL image (sources: pimm.py at each i_*):

  read_eagerly, 23:6B   what the compiler writes for `alternatively.`;
                        one processor has no external references, so
                        nothing is done and the variables noted so far
                        STAY noted
  not_equal, 23:F3      the guard X =\\= Y on integers
  wait_vector_4, 23:AC  as wait_vector_2/3/5
  wait_vector_6, 23:AE
  wait_vector_1, 23:A9  NOT IN THE IPL IMAGE (asm/kbndis.py finds no
                        site): run on six cells of code the bench
                        writes into the heap, OURS, see part vector 1

Parts, the expected values from the KL1 source as asm/kl1decomp.py
gives it, not from either model:
  attention     scsi_fep_util:set_attention/1, close_attention/1 and
                close_device/2, `p(3) :- true | true.  alternatively.
                p(A) :- true | A = N.`: on 3 nothing; on a variable
                the first clause notes it, read_eagerly is passed and
                the second clause binds it (3, 0, and 0 with []).
  taken twice   set_attention(5): 5 = 3 fails in the body.
  not equal     scsi_fep_file:reply_with_attention([], B,
                [normal({7, H, 9})], [receive({7, X, Y}, F)]), whose
                second clause has the guard H =\\= 3: with H = 1,
                F = normal and scsi_fep_util:set_value/2 unifies the
                two vectors, {7, 1, 9}; with H = 2 its other clause
                gives {7, 2, 0}.  B stays unbound.
  equal         the same with [normal({7, 3, 9}), normal({7, 1, 9})]:
                not_equal FAILS on the first, the third clause takes
                it (set_attention(B): B = 3), and the second element
                answers the receive as above.
  alternatively reply_with_attention([next_attention(A)], B, C, D)
                and [reset(A)], C and D unbound: the clauses before
                `alternatively` note C, the fourth clause is taken all
                the same; then reply_with_attention([], A, C, D)
                notes D and C and, after read_eagerly, reaches
                `suspend` with them still noted: it SUSPENDS (were
                they forgotten it would fail), and goes on when D is
                [].
  vector 4      scsi:request_manager/3, the info vector {D, E, F, G}
                read by wait_vector_4: [get_info(A)] gives A =
                normal(8, 16000) for F = 0 and normal(2048, 16000) for
                F = 4; [processor(normal, 1, C)] gives C =
                abnormal(illegal_input(normal, 1)); the message
                {normal, _, _, B} (wait_vector_4 on the message, after
                `otherwise`) gives B = abnormal(not_implemented); the
                stream is closed each time.  An info vector of three:
                no clause applies, the reduction fails.
  vector 6      scsi:command_executer/2, [{X, 1, 2, 3, 4, 5}]: with X
                unbound wait_vector_6 passes, read_atom notes X and
                the goal suspends; X = normal then fails it.  A
                message of three elements fails at once.
  vector 1      p({X}, Y) :- true | Y = X, six cells of OURS made by
                the bench in the heap (try_me_else, wait_vector_1 0,
                read_variable 2, get_value 1 2, proceed, suspend):
                {5} gives 5; a variable waits and {7} gives 7; a
                vector of two fails.
  vector 0      wait_vector_0, 23:A8, the same way (2026-11-24; a stop
                of pim:go/4 with the device, scsi_fep:receive_packet2_1/8
                `receive_packet2_1({}, ..)`, not playable here): five
                cells, p({}, Y) :- true | Y = {} (try_me_else,
                wait_vector_0 0, get_value 1 0, proceed, suspend): {}
                gives {}; a variable waits and {} gives {}; {5} fails.
                Pins 9 parts / 1801 lines -> 10 / 1897: this part's 96
                lines, the other parts unchanged.
  jump          jump, 23:67 (2026-11-24; a stop of pim:go/4 with the
                device, in a module the boot loads; none in the image):
                five cells, OURS: jump @3; @1: get_value 1, 0;
                proceed; @3: put_integer 1, 7; jump @1, a branch forward
                and one back: p(X) gives X = 7.  Pins 10 / 1897 ->
                11 / 1927, this part's 30 lines.
  marked variable  set_marked_variable, 23:15 (2026-11-24; the next
                stop of pim:go/4; none in the image): six cells, OURS,
                p(X) :- true | q(Y), X = Y. q(5).  X = 5, the goal's
                argument and r1 written with the MRB on.  Pins 11 /
                1927 -> 12 / 1972, this part's 45 lines.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv),
2026-11-23, each restored from a copy:
  read_eagerly forgets the noted variables   alternatively, line 66
                                             (E fail for the suspension)
  not_equal as equal                         not equal, line 88
  not_equal always succeeds                  equal, line 102
  wait_vector_4 takes a vector of three      vector 4 of three, line 45
  wait_vector_6 always fails                 vector 6, line 36
  wait_vector_1 takes any vector             vector 1, line 105
  wait_vector_4 leaves the structure pointer vector 4, line 48
  wait_vector_0 takes any vector             vector 0, line 93 (2026-11-24:
                                             get_value for the suspend)
  (2026-11-24) jump falls through            jump, line 21 (get_value
                                             for put_integer)
  (2026-11-24) jump to the label + 1         jump, line 21 (the second
                                             jump for put_integer)
  (2026-11-24) set_marked_variable unmarked  marked variable, line 24:
                                             A 1 06.. for 07..
Not tried: the MRB of what read_variable takes after wait_vector_4 or
_6 (the rule is wait_vector_2's, one code path for every N;
lockstep_mrb.py and lockstep_repl.py run it).

Not run:
  command_executer's first clause past read_atom (it is scsi_command,
  which neither lockstep model has); not_equal on an unbound or a
  non-integer operand (its only site in the image, 4782, follows
  wait and integer on one operand and put_integer on the other);
  wait_vector_1 on a real predicate.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=12, lines=1972)
I = lambda v: (pimm.INT, v)                        # noqa: E731
NIL = (pimm.ATOM, 0)
KLB = 0x23


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    P = lambda mod, pred: pimm.predicate(im, mod, pred)   # noqa: E731
    s = driver.Script()
    want = []      # (part, [expected terms of its outs]; None = unbound)

    def part(name, exp):
        want.append((name, exp))

    # 1. `alternatively` between two clauses
    s.label('attention')
    for pred, arity in (('set_attention/1', 1), ('close_attention/1', 1), ('close_device/2', 2)):
        for first in (I(3), None):
            if first is None:
                s.newvar(0)
                s.arg(1, 0)
            else:
                s.setslot(0, first)
                s.argc(1, first)
            if arity == 2:
                s.newvar(1)
                s.arg(2, 1)
            s.spawn(P('scsi_fep_util', pred), arity)
            s.run()
            s.out(0)
            if arity == 2:
                s.out(1)
    part('attention', [3, 3, 3, 0, 3, [], 0, []])

    # 2. the second clause's body fails: 5 = 3
    s.label('taken twice')
    s.argc(1, I(5))
    s.spawn(P('scsi_fep_util', 'set_attention/1'), 1)
    s.run()
    part('taken twice', [])

    def reply(hs, receive=True):
        """reply_with_attention([], B, [normal({7, h, 9}) for h in hs],
        [receive({7, X, Y}, F)]); E in slot 3, F in 4, B in 7."""
        tail = NIL
        for k, h in enumerate(reversed(hs)):
            here = 2 if (len(hs) - k) % 2 else 12  # the last made is in 2
            s.vector(0, 8, [I(7), I(h), I(9)])
            s.vector(1, 8, [A('normal'), ('slot', 0)])
            s.cons(here, 8, ('slot', 1), tail)
            tail = ('slot', here)
        s.vector(3, 8, [I(7), None, None])
        s.newvar(4)
        s.vector(5, 8, [A('receive'), ('slot', 3), ('slot', 4)])
        s.cons(6, 8, ('slot', 5), NIL)
        s.newvar(7)
        s.argc(1, NIL)
        s.arg(2, 7)
        s.arg(3, 2)
        s.arg(4, 6)
        s.spawn(P('scsi_fep_file', 'reply_with_attention/4'), 4)
        s.run()
        s.out(3)
        s.out(4)
        s.out(7)

    # 3. not_equal succeeds
    s.label('not equal')
    reply([1])
    reply([2])
    part('not equal', [(7, 1, 9), 'normal', None, (7, 2, 0), 'normal', None])

    # 4. not_equal fails: the next clause
    s.label('equal')
    reply([3, 1])
    part('equal', [(7, 1, 9), 'normal', 3])

    # 5. the clauses after `alternatively`, and a suspension past it
    s.label('alternatively')
    for msg in ('next_attention', 'reset'):
        s.newvar(0)                                # A
        s.vector(1, 8, [A(msg), ('slot', 0)])
        s.cons(2, 8, ('slot', 1), NIL)
        s.newvar(3)                                # B
        s.newvar(4)                                # C
        s.newvar(5)                                # D
        s.arg(1, 2)
        s.arg(2, 3)
        s.arg(3, 4)
        s.arg(4, 5)
        s.spawn(P('scsi_fep_file', 'reply_with_attention/4'), 4)
        s.run()
        s.out(5)
        s.unifyc(5, NIL)
        s.run()
        s.out(0)
        s.out(3)
        s.out(4)
    part('alternatively', [None, None, None, None] * 2)

    def manager(msg, info):
        """request_manager([msg], E, info); E in slot 6."""
        s.vector(1, 8, msg)
        s.cons(2, 8, ('slot', 1), NIL)
        s.vector(3, 8, [I(v) for v in info])
        s.newvar(6)
        s.arg(1, 2)
        s.arg(2, 6)
        s.arg(3, 3)
        s.spawn(P('scsi', 'request_manager/3'), 3)
        s.run()

    # 6. wait_vector_4
    s.label('vector 4')
    for f, in ((0,), (4,)):
        s.newvar(0)
        manager([A('get_info'), ('slot', 0)], [16000, 8, f, 0])
        s.out(0)
        s.out(6)
    s.newvar(0)
    manager([A('processor'), A('normal'), I(1), ('slot', 0)], [16000, 8, 4, 0])
    s.out(0)
    s.out(6)
    s.newvar(0)
    manager([A('normal'), None, None, ('slot', 0)], [16000, 8, 4, 0])
    s.out(0)
    s.out(6)
    part('vector 4', [('normal', 8, 16000), [], ('normal', 2048, 16000), [],
                      ('abnormal', ('illegal_input', 'normal', 1)), [],
                      ('abnormal', 'not_implemented'), []])

    s.label('vector 4 of three')
    s.newvar(0)
    manager([A('get_info'), ('slot', 0)], [16000, 8, 4])
    s.out(0)
    part('vector 4 of three', [None])

    # 7. wait_vector_6
    s.label('vector 6')
    s.vector(1, 8, [None, I(1), I(2), I(3), I(4), I(5)])
    s.setslot(0, (0, 0))
    s.newvar(0)
    s.unify(0, 8)                                  # keeps X
    s.cons(2, 8, ('slot', 1), NIL)
    s.arg(1, 2)
    s.argc(2, I(1))
    s.spawn(P('scsi', 'command_executer/2'), 2)
    s.run()
    s.out(0)
    s.unifyc(0, A('normal'))
    s.run()
    s.vector(1, 8, [A('command'), I(1), I(2)])
    s.cons(2, 8, ('slot', 1), NIL)
    s.arg(1, 2)
    s.argc(2, I(1))
    s.spawn(P('scsi', 'command_executer/2'), 2)
    s.run()
    part('vector 6', [None])

    # 8. wait_vector_1: no site in the image.  p({X}, Y) :- true | Y = X,
    #    OURS, six cells the bench puts in the heap (a vector's cells)
    s.label('vector 1')
    code = [(KLB, 0x68 << 24 | 3),                 # try_me_else @5
            (KLB, 0xa9 << 24 | 0 << 16),           # wait_vector_1 0
            (KLB, 0xb4 << 24 | 2 << 16),           # read_variable 2
            (KLB, 0xbc << 24 | 1 << 16 | 2 << 8),  # get_value 1, 2
            (KLB, 0x60 << 24),                     # proceed
            (KLB, 0x69 << 24 | 2 << 16 | 0xfff9)]  # suspend 2, @0
    s.vector(15, 8, code)
    m = s.live()
    at = s.live_slot[15][1] - m.load
    assert [m.opname(at + i) for i in range(6)] == [
        'try_me_else', 'wait_vector_1', 'read_variable', 'get_value', 'proceed', 'suspend']
    s.vector(0, 8, [I(5)])
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(1)
    s.newvar(0)
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(1)
    s.vector(2, 8, [I(7)])
    s.unify(0, 2)
    s.run()
    s.out(1)
    s.vector(0, 8, [I(5), I(6)])
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(1)
    part('vector 1', [5, None, 7, None])

    # 9. wait_vector_0: no site in the image either (scsi_fep's
    #    receive_packet2_1/8 and receive_packet3/8, `({}, ...)`, are in
    #    the bios and patch files and go on into builtin#substring, a
    #    module those files do not hold).  p({}, Y) :- true | Y = 0,
    #    OURS, five cells the bench puts in the heap
    s.label('vector 0')
    code = [(KLB, 0x68 << 24 | 2),                 # try_me_else @4
            (KLB, 0xa8 << 24 | 0 << 16),           # wait_vector_0 0
            (KLB, 0xbc << 24 | 1 << 16 | 0 << 8),  # get_value 1, 0
            (KLB, 0x60 << 24),                     # proceed
            (KLB, 0x69 << 24 | 2 << 16 | 0xfffa)]  # suspend 2, @0
    s.vector(15, 8, code)
    m = s.live()
    at = s.live_slot[15][1] - m.load
    assert [m.opname(at + i) for i in range(5)] == [
        'try_me_else', 'wait_vector_0', 'get_value', 'proceed', 'suspend']
    EMPTY = (pimm.VECT0, 0)
    s.argc(1, EMPTY)
    s.newvar(1)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(1)
    s.newvar(0)
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(1)
    s.unifyc(0, EMPTY)
    s.run()
    s.out(1)
    s.vector(0, 8, [I(5)])
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(at, 2)
    s.run()
    s.out(1)
    part('vector 0', [(), None, (), None])
    # 10. jump (2026-11-24, met in pim:go/4 in a module the boot
    #    loads; no site in the image): forward, then back.  OURS, five
    #    cells: jump @3; @1: get_value 1, 0; proceed; @3: put_integer
    #    1, 7; jump @1.  p(X) gives X = 7
    s.label('jump')
    code = [(KLB, 0x67 << 24 | 1),                 # jump @3
            (KLB, 0xbc << 24 | 1 << 16 | 0 << 8),  # @1: get_value 1, 0
            (KLB, 0x60 << 24),                     # proceed
            (KLB, 0x31 << 24 | 1 << 16 | 7),       # @3: put_integer 1, 7
            (KLB, 0x67 << 24 | 0xfffb)]            # jump @1
    s.vector(15, 8, code)
    m = s.live()
    at = s.live_slot[15][1] - m.load
    assert [m.opname(at + i) for i in range(5)] == [
        'jump', 'get_value', 'proceed', 'put_integer', 'jump']
    s.newvar(0)
    s.arg(1, 0)
    s.spawn(at, 1)
    s.run()
    s.out(0)
    part('jump', [7])
    # 11. set_marked_variable (2026-11-24, met in pim:go/4 after jump;
    #    none in the image).  OURS, six cells: p(X) :- true | q(Y),
    #    X = Y. q(5).  set_marked_variable 1, 1; enqueue_goal 1, @4;
    #    get_value 0, 1; proceed; @4: get_integer 0, 5; proceed.  The
    #    argument and r1 are written with the MRB on (the A and R lines)
    s.label('marked variable')
    code = [(KLB, 0x15 << 24 | 1 << 16 | 1 << 8),  # set_marked_variable 1, 1
            (KLB, 0x63 << 24 | 1 << 16 | 1),       # enqueue_goal 1, @4
            (KLB, 0xbc << 24 | 0 << 16 | 1 << 8),  # get_value 0, 1
            (KLB, 0x60 << 24),                     # proceed
            (KLB, 0xb9 << 24 | 0 << 16 | 5),       # @4: get_integer 0, 5
            (KLB, 0x60 << 24)]                     # proceed
    s.vector(15, 8, code)
    m = s.live()
    at = s.live_slot[15][1] - m.load
    assert [m.opname(at + i) for i in range(6)] == [
        'set_marked_variable', 'enqueue_goal', 'get_value', 'proceed', 'get_integer', 'proceed']
    s.newvar(0)
    s.arg(1, 0)
    s.spawn(at, 1)
    s.run()
    s.out(0)
    part('marked variable', [5])
    return s, want


# part: (reductions that end in a failure, in a suspension)
ENDS = {'attention': (0, 0), 'taken twice': (1, 0), 'not equal': (0, 0), 'equal': (0, 0),
        'alternatively': (0, 2), 'vector 4': (0, 0), 'vector 4 of three': (1, 0),
        'vector 6': (2, 1), 'vector 1': (1, 1), 'vector 0': (1, 1), 'jump': (0, 0),
        'marked variable': (0, 0)}
# part: (the instruction that must be taken, how often at least)
TAKEN = {'attention': ('read_eagerly', 3), 'taken twice': ('read_eagerly', 1),
         'not equal': ('not_equal', 2), 'equal': ('not_equal', 2),
         'alternatively': ('read_eagerly', 4), 'vector 4': ('wait_vector_4', 4),
         'vector 4 of three': ('wait_vector_4', 1), 'vector 6': ('wait_vector_6', 3),
         'vector 1': ('wait_vector_1', 4), 'vector 0': ('wait_vector_0', 4),
         'jump': ('jump', 2), 'marked variable': ('set_marked_variable', 1)}
OPCODE = {'jump': '2367', 'set_marked_variable': '2315', 'wait_vector_0': '23a8', 'read_eagerly': '236b', 'not_equal': '23f3', 'wait_vector_1': '23a9',
          'wait_vector_4': '23ac', 'wait_vector_6': '23ae'}


def check(s, m, want, parts):
    """parts: {label: trace lines}."""
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
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep alt',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, want, kept)
    if bad:
        print('pimm lockstep alt: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep alt: PASS (read_eagerly, not_equal and wait_vector_0, _1, _4, _6 on the '
          'Bluespec core: %d parts, %d trace lines identical to the reference model; '
          '`alternatively` in scsi_fep_util and scsi_fep_file:reply_with_attention/4, a goal '
          'suspending past it, scsi:request_manager/3 on its info vector, '
          'scsi:command_executer/2 up to scsi_command; wait_vector_1 on code of the bench)'
          % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
