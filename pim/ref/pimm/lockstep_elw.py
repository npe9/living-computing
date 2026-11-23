#!/usr/bin/env python3
"""Lockstep: string_operation waiting on an element of its vector.

    python3 ref/pimm/lockstep_elw.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_elw.py compare
    python3 ref/pimm/lockstep_elw.py --reference       the reference alone

string_operation(Op, {Pos1, Str1, Len, Pos2, Str2}, ^NewS1, ^NewS2)
takes its arguments in a vector, and an element of that vector may not
be a value yet: the manual says the built-in waits.  As on the
reference model (pimm.py Machine.builtin, `elements`): once the two
operands are bound, the goal of the stub waits on the FIRST element,
in order, that is unbound, as it would on an operand; woken, the stub
tries again (and may wait on the next).  That it is a goal of the
stub is the project's design (asm/pimm_stubs.py); what the firmware
did is lost.

Parts, the expected values from the KL1 source (asm/kl1decomp.py) and
written out here, not from either model:
  packet    scsi_fep_module:send_last_packet(Id, Buf, Pos, Len, Src,
            From, G, H, I), which makes the packet of a front-end
            request: Buf with Len bytes of Src from From copied to
            Pos (copy_str8_elements/7), Id in bytes 0..3 and 0 in
            bytes 4..7, and G = [send(Packet, Len + 8, I)|H].  Three
            string_operations, each given a string that a goal not
            yet run will make, and b_string's three real sites of
            this path (two here, one in copy_str8_elements/7), each
            on a variable bound later.
  append    builtin_utility:append_string/2 on lists of strings: the
            new string's length is not known until the list has been
            walked, so every string_operation waits on it (element
            1).  The concatenation; one string; none (""; 16-bit, as
            the image's constant is).
  stub      string_operation at its stub (the bench's goal), the five
            elements bound by the bench one at a time, out of order:
            Str2 first (nothing happens: the goal waits on Pos1),
            Pos1 (it wakes and waits on Str1), Len (nothing), Str1
            (it waits on Pos2), Pos2: the answer.  Then with only
            Len unbound when the goal is made, and with only Str2.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv),
2026-11-23, each restored from a copy:
  waits on the LAST unbound element          packet, line 100
  no wait on an element (as before: refused) packet, line 86
  an unbound Str2 (element 4) not waited for stub, line 268
  an unbound Len (element 2) not waited for  stub, line 188
  b_string: size and width swapped           packet, line 348
  b_string: NewString not given              packet, line 350
The third and fourth were NOT caught by this test's first form (no
goal was ever tried with only that element unbound); the last two
cases of part stub were added for them.
Not tried: the operation checked before the elements are waited for
(a refusal either way).

Not run: the vector's forms of four and three elements, an operation
outside 0..15, an element of the wrong type (refused by both models;
the driver cannot play a refusal); scsi_command's wait on ITS vector
(the reference model alone).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=3, lines=2801)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
NIL = (pimm.ATOM, 0)
B = lambda t: [ord(c) for c in t]                  # noqa: E731
# Id, Buf, Pos, Len, Src, From; the packet
PACKETS = [
    (0x01020304, [0x10 + i for i in range(16)], 8, 4, B('abcdefgh'), 2,
     [1, 2, 3, 4, 0, 0, 0, 0] + B('cdef') + [0x1c, 0x1d, 0x1e, 0x1f]),
    (77, [0xee] * 20, 9, 7, B('0123456'), 0,
     [0, 0, 0, 77, 0, 0, 0, 0, 0xee] + B('0123456') + [0xee] * 4),
]
APPENDS = [(8, [B('ab'), B('cde'), B('f')]), (16, [[0x2341], [0x2342, 0x2343]]),
           (8, [B('xyz')]), (8, [[], B('q'), []])]


def script():
    im = pimm.kbndis.Image()
    P = lambda mod, pred: pimm.predicate(im, mod, pred)   # noqa: E731
    stubs = pimm.Machine().stubs
    s = driver.Script()
    want = []      # (part, [expected terms of its outs]; None = unbound)

    # 1. a front-end packet
    s.label('packet')
    exp = []
    for ident, buf, pos, n, src, start, packet in PACKETS:
        s.string(0, 8, buf)
        s.string(1, 8, src)
        s.newvar(2)                                # G
        s.argc(1, I(ident))
        s.arg(2, 0)
        s.argc(3, I(pos))
        s.argc(4, I(n))
        s.arg(5, 1)
        s.argc(6, I(start))
        s.arg(7, 2)
        s.argc(8, NIL)                             # H
        s.argc(9, I(5))                            # I
        s.spawn(P('scsi_fep_module', 'send_last_packet/9'), 9)
        s.run()
        s.out(2)
        exp.append([('send', (8, packet), n + 8, 5)])
    want.append(('packet', exp))

    # 2. a list of strings appended
    s.label('append')
    exp = []
    for bits, strings in APPENDS:
        tail = NIL
        for k, e in enumerate(reversed(strings)):
            here = 2 if (len(strings) - k) % 2 else 3      # the last made is in 2
            s.string(0, bits, e)
            s.cons(here, 8, ('slot', 0), tail)
            tail = ('slot', here)
        s.newvar(1)
        s.arg(1, 2)
        s.arg(2, 1)
        s.spawn(P('builtin_utility', 'append_string/2'), 2)
        s.run()
        s.out(1)
        exp.append((bits, [c for e in strings for c in e]))
    s.newvar(1)
    s.argc(1, NIL)
    s.arg(2, 1)
    s.spawn(P('builtin_utility', 'append_string/2'), 2)
    s.run()
    s.out(1)
    exp.append((16, []))
    want.append(('append', exp))

    # 3. at the stub, the elements bound out of order
    s.label('stub')
    s.vector(1, 8, [None] * 5)                     # Pos1 8, Str1 9, Len 10, Pos2 11, Str2 12
    s.string(2, 8, [1, 2, 3, 4, 5, 6])
    s.string(3, 8, [9, 9, 7, 8])
    s.newvar(4)
    s.newvar(5)
    s.argc(1, I(3))
    s.arg(2, 1)
    s.arg(3, 4)
    s.arg(4, 5)
    s.spawn(stubs['string_operation']['addr'], 4)
    s.run()
    s.out(4)
    for slot, v in ((12, ('slot', 3)), (8, I(1)), (10, I(2)), (9, ('slot', 2)), (11, I(2))):
        if v[0] == 'slot':
            s.unify(slot, v[1])
        else:
            s.unifyc(slot, v)
        s.run()
        s.out(4)
    s.out(5)
    exp = [None] * 5 + [(8, [1, 7, 8, 4, 5, 6]), (8, [9, 9, 7, 8])]
    # one element unbound, nothing before it: Len (2), then Str2 (4)
    for elems, late, v, new in (
            ([I(1), ('slot', 2), None, I(2), ('slot', 3)], 10, I(2), [1, 7, 8, 4, 5, 6]),
            ([I(0), ('slot', 2), I(1), I(3), None], 12, ('slot', 3), [8, 2, 3, 4, 5, 6])):
        s.vector(1, 8, elems)
        s.newvar(4)
        s.newvar(5)
        s.argc(1, I(3))
        s.arg(2, 1)
        s.arg(3, 4)
        s.arg(4, 5)
        s.spawn(stubs['string_operation']['addr'], 4)
        s.run()
        s.out(4)
        if v[0] == 'slot':
            s.unify(late, v[1])
        else:
            s.unifyc(late, v)
        s.run()
        s.out(4)
        s.out(5)
        exp += [None, (8, new), (8, [9, 9, 7, 8])]
    want.append(('stub', exp))
    s.stub = stubs['string_operation']['addr']
    return s, want


# part: how often string_operation is taken at its stub, at least (a
# wait that was woken); for `stub` exactly: the first try and one for
# each binding that wakes it (Pos1, Str1, Pos2), not for Str2 and Len;
# then two tries for each of the two goals with one element unbound
WOKEN = {'packet': 2 * 3, 'append': 6, 'stub': 4 + 2 + 2}


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
        if 'E fail' in lines:
            bad.append((name, 'a reduction failed'))
        n = sum(1 for ln in lines if ln.startswith('I %d ' % s.stub))
        if n < WOKEN[name] or (name == 'stub' and n != WOKEN[name]):
            bad.append((name, 'string_operation taken at its stub %d times' % n))
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
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep elw',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, want, kept)
    if bad:
        print('pimm lockstep elw: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep elw: PASS (string_operation waiting on an element of its vector, on '
          'the Bluespec core: %d parts, %d trace lines identical to the reference model; '
          'scsi_fep_module:send_last_packet/9 makes %d packets, b_string at its real sites; '
          'builtin_utility:append_string/2 on %d lists; the elements bound out of order at '
          'the stub)' % (s.counts['parts'], s.counts['lines'], len(PACKETS), len(APPENDS) + 1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
