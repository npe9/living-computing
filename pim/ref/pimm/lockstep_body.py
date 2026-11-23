#!/usr/bin/env python3
"""Lockstep: b_divide, b_modulo, b_string, enqueue_goal_to_processor.

    python3 ref/pimm/lockstep_body.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_body.py compare
    python3 ref/pimm/lockstep_body.py --reference       the reference alone

Four body instructions the reference model had alone (sources:
pimm.py at each i_*):

  b_divide, 22:C3    divide in a body, truncated towards zero (PDSS's;
                     not established for PIM/m)
  b_modulo, 22:C4    modulo in a body, the dividend's sign (PDSS's)
  b_string, 22:CB    string(X, ^Size, ^ElementSize, ^NewString)
  enqueue_goal_to_processor, 23:65
                     Goal@processor(N); one processor here, number 0
                     (OURS), for which the goal is made as
                     enqueue_goal makes it

Parts, the expected values worked out here, from the KL1 source as
asm/kl1decomp.py gives it and from arithmetic, not from either model:
  message       scsi_fep_module:str8_to_msg(Id, Bytes, Msg), which
                turns a front-end reply into a vector: bytes 0..3 a
                status, 4..7 the number of arguments, then a word per
                argument (-1: an integer of four bytes; else the
                length of a string, which is padded to four bytes),
                then the arguments.  str8_to_msg3/8 finds what follows
                a string with P := ((Len + 3) / 4) * 4: b_divide.  Two
                replies whose string is NOT last (six bytes then an
                integer; one byte, an integer, five bytes, an
                integer): a wrong quotient misplaces what follows.
  sixteen       scsi_fep_module:str16_to_str8(S16, S8): F := (Len * 2)
                mod 4 with b_modulo, then padding(F, ..): an even
                length gives the bytes as they are (F = 0), an odd
                one (F = 2) two zero bytes more, through
                builtin_utility:append_string/3.
  signed        b_divide and b_modulo at their stubs (the bench's goal,
                as lockstep_apply.py runs apply), on signed operands:
                -7 by 2 is -3 remainder -1, 7 by -2 is -3 remainder 1,
                and the rest of DIV; the least integer by -1 has
                remainder 0.  Then the divisor unbound: the built-in
                waits and answers when it is bound.
  string        b_string at its stub: strings of 8-, 16- and 32-bit
                elements and the empty string give their length,
                their width and themselves; an unbound X waits.
  processor     scsi_fep_module:create(0, B, 7, 0, 1, 0, G) :-
                create1(H, ..., G), $bar2(B, H)@processor(0).  B
                unbound: $bar2/2 runs (processor 0: this machine)
                into scsi:create(B, H), which waits for B, and
                create1/6 waits for H.  B = normal: scsi:create/2 has
                no clause for a non-integer, the reduction fails (so
                the goal's first argument was B).  H = abnormal:
                create1's second clause gives G = abnormal.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv),
2026-11-23, each restored from a copy:
  b_divide gives the remainder           message, line 736
  b_modulo gives the quotient            sixteen, line 37
  b_divide rounds down                   signed, line 65
  b_modulo takes the divisor's sign      signed, line 89
  b_string: size and width swapped       string, line 27
  b_string: NewString not given          string, line 29
  to_processor: one argument short       processor, line 62
  to_processor: one cell long            processor, line 65
NOT caught:
  to_processor: any integer taken for the processor (only 0 is run;
  the other numbers are a refusal)

Not run:
  b_string at a real site: each of the image's five is followed by a
  string_operation on a vector with an element not yet bound, which
  the Bluespec core does not have at this commit (pimm.py
  Machine.alone);
  enqueue_goal_to_processor to another processor, a zero divisor, the
  least integer divided by -1, b_string of a non-string: refusals,
  which the lockstep driver cannot play; scsi:create/2 with an integer
  (scsi_init is on the reference model alone).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=5, lines=5076)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
NIL = (pimm.ATOM, 0)
MIN = -(1 << 31)
# dividend, divisor, quotient, remainder: written out, not computed
DIV = [(7, 2, 3, 1), (-7, 2, -3, -1), (7, -2, -3, 1), (-7, -2, 3, -1), (0, 5, 0, 0),
       (5, 7, 0, 5), (-5, 7, 0, -5), (MIN, 2, -(1 << 30), 0), (2147483647, -1, -2147483647, 0),
       (1000000007, 13, 76923077, 6), (-12, 4, -3, 0)]
# id, the reply's bytes, the message
REPLIES = [
    (5, [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 6, 255, 255, 255, 255,
         0x61, 0x62, 0x63, 0x64, 0x65, 0x66, 0, 0, 1, 2, 3, 4],
     (5, 0, (16, [0x6162, 0x6364, 0x6566]), 0x01020304)),
    (9, [0, 0, 0, 7, 0, 0, 0, 4, 0, 0, 0, 2, 255, 255, 255, 255, 0, 0, 0, 10,
         255, 255, 255, 255,
         0x41, 0x42, 0, 0, 0, 0, 0, 77, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37,
         0x38, 0x39, 0, 0, 255, 255, 255, 254],
     (9, 7, (16, [0x4142]), 77, (16, [0x3031, 0x3233, 0x3435, 0x3637, 0x3839]), -2)),
]
STRINGS = [(8, [1, 2, 3, 4, 5]), (16, [0x2341, 0x2342]), (32, [0x92345678, 7, 1]), (8, [])]


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    P = lambda mod, pred: pimm.predicate(im, mod, pred)   # noqa: E731
    stubs = pimm.Machine().stubs
    s = driver.Script()
    want = []      # (part, [expected terms of its outs]; None = unbound)

    # 1. b_divide: a front-end reply made into a message
    s.label('message')
    exp = []
    for ident, data, msg in REPLIES:
        s.string(0, 8, data)
        s.newvar(1)
        s.argc(1, I(ident))
        s.arg(2, 0)
        s.arg(3, 1)
        s.spawn(P('scsi_fep_module', 'str8_to_msg/3'), 3)
        s.run()
        s.out(1)
        exp.append(msg)
    want.append(('message', exp))

    # 2. b_modulo: a 16-bit string as bytes
    s.label('sixteen')
    exp = []
    for elems in ([0x6162, 0x6364], [0x0102, 0x0304, 0x0506, 0x0708], [],
                  [0x6162], [0x0102, 0x0304, 0x0506]):
        s.string(0, 16, elems)
        s.newvar(1)
        s.arg(1, 0)
        s.arg(2, 1)
        s.spawn(P('scsi_fep_module', 'str16_to_str8/2'), 2)
        s.run()
        s.out(1)
        exp.append((8, [b for e in elems for b in (e >> 8, e & 255)] + [0, 0] * (len(elems) % 2)))
    want.append(('sixteen', exp))

    # 3. signed operands, at the stubs
    s.label('signed')
    exp = []
    for a, b, q, r in DIV:
        for name, v in (('b_divide', q), ('b_modulo', r)):
            s.newvar(0)
            s.argc(1, I(a))
            s.argc(2, I(b))
            s.arg(3, 0)
            s.spawn(stubs[name]['addr'], 3)
            s.run()
            s.out(0)
            exp.append(v)
    s.newvar(0)
    s.newvar(1)
    s.argc(1, I(MIN))
    s.argc(2, I(-1))
    s.arg(3, 0)
    s.spawn(stubs['b_modulo']['addr'], 3)
    s.run()
    s.out(0)
    exp.append(0)
    for name, v in (('b_divide', -14), ('b_modulo', -2)):      # -100 by 7
        s.newvar(0)
        s.newvar(1)
        s.argc(1, I(-100))
        s.arg(2, 1)
        s.arg(3, 0)
        s.spawn(stubs[name]['addr'], 3)
        s.run()
        s.out(0)
        s.unifyc(1, I(7))
        s.run()
        s.out(0)
        exp += [None, v]
    want.append(('signed', exp))

    # 4. b_string at its stub
    s.label('string')
    exp = []
    for bits, elems in STRINGS:
        s.string(0, bits, elems)
        for k in (1, 2, 3):
            s.newvar(k)
        s.arg(1, 0)
        for k in (1, 2, 3):
            s.arg(k + 1, k)
        s.spawn(stubs['b_string']['addr'], 4)
        s.run()
        for k in (1, 2, 3):
            s.out(k)
        exp += [len(elems), bits, (bits, elems)]
    s.newvar(0)
    for k in (1, 2, 3):
        s.newvar(k)
        s.arg(k + 1, k)
    s.arg(1, 0)
    s.spawn(stubs['b_string']['addr'], 4)
    s.run()
    s.out(1)
    s.string(4, 16, [9, 8, 7])
    s.unify(0, 4)
    s.run()
    for k in (1, 2, 3):
        s.out(k)
    exp += [None, 3, 16, (16, [9, 8, 7])]
    want.append(('string', exp))

    # 5. Goal@processor(0)
    s.label('processor')
    s.newvar(0)                                    # B
    s.newvar(1)                                    # G
    s.argc(1, I(0))
    s.arg(2, 0)
    for k, v in ((3, 7), (4, 0), (5, 1), (6, 0)):
        s.argc(k, I(v))
    s.arg(7, 1)
    s.spawn(P('scsi_fep_module', 'create/7'), 7)
    s.run()
    s.out(1)
    m = s.live()
    # H: the second argument of the goal waiting in scsi:create/2
    ins = [ln.split() for ln in m.tr]
    at = [k for k, f in enumerate(ins) if f[0] == 'I' and int(f[1]) == P('scsi', 'create/2')]
    assert len(at) == 1
    r1 = [f for f in ins[:at[0]] if f[0] == 'R' and f[1] == '1'][-1]
    h = (int(r1[2][:2], 16), int(r1[2][2:], 16))
    assert m.unbound(m.deref(h))
    s.setslot(2, h)
    s.unifyc(0, A('normal'))
    s.run()
    s.unifyc(2, A('abnormal'))
    s.run()
    s.out(1)
    want.append(('processor', [None, 'abnormal']))
    s.create2 = P('scsi', 'create/2')
    return s, want


# part: (reductions that end in a failure, in a suspension)
ENDS = {'message': (0, None), 'sixteen': (0, 0), 'signed': (0, 0), 'string': (0, 0),
        'processor': (1, 2)}
OPCODE = {'message': '22c3', 'sixteen': '22c4', 'signed': '22c3', 'string': '22cb',
          'processor': '2365'}
LEAST = {'message': 3, 'sixteen': 5, 'signed': len(DIV) + 2, 'string': len(STRINGS) + 2,
         'processor': 1}


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
        fails, susps = ENDS[name]
        if lines.count('E fail') != fails or (susps is not None and lines.count('E susp') != susps):
            bad.append((name, 'fails, suspensions', lines.count('E fail'), lines.count('E susp')))
        n = sum(1 for ln in lines if ln.startswith('I ') and ln.split()[2].startswith(OPCODE[name]))
        if n < LEAST[name]:
            bad.append((name, OPCODE[name], 'taken %d times' % n))
    # the goal sent to processor 0 ran: scsi:create/2 was entered
    if not any(ln.startswith('I %d ' % s.create2) for ln in parts.get('processor', [])):
        bad.append(('processor', 'scsi:create/2 not entered'))
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
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep body',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, want, kept)
    if bad:
        print('pimm lockstep body: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep body: PASS (b_divide, b_modulo, b_string and '
          'enqueue_goal_to_processor on the Bluespec core: %d parts, %d trace lines '
          'identical to the reference model; scsi_fep_module:str8_to_msg/3 on %d replies '
          'whose string is not last, str16_to_str8/2, %d signed divisions at the stubs, '
          'strings of 8, 16 and 32 bits, and create/7 sending a goal to processor 0)'
          % (s.counts['parts'], s.counts['lines'], len(REPLIES), len(DIV)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
