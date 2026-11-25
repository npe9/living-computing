#!/usr/bin/env python3
"""Lockstep: strings of 1-bit elements, and the unary string_operation.

    python3 ref/pimm/lockstep_s1.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_s1.py compare
    python3 ref/pimm/lockstep_s1.py --reference       the reference alone

A string of 1-bit elements is {CDESC, pad << 27 | 0 << 24 | words}, the
pad five bits wide, (32 - Len mod 32) << 27 (library/kbn/kbnheap.kl1
string_cdesc:168-169: a whole last word gives 32 << 27, which falls
out of the word: pad 0); element 0 is the top bit of word 0, as for
the other sizes.  VPIM takes element sizes 1, 8, 16 and 32
(interpreter/klb_body_blt_struct.psl.c kblt_b_search_character, its
PreCondition).  The PIMOS compiler makes them: compiler/reg.kl1
new_string(Str, Size, 1) and its register masks (unary_string_operation
(string_operation#set, ...), string_element, set_string_element,
substring).  Met compiling the primer's sample1 (2026-11-25).

unary_string_operation(Op, Str1, Pos1, Len, NewS1) reaches the machine
as string_operation(Op, {Pos1, Str1, Len}, NewS1, NewS2), NewS2 a new
variable (compiler/blt.kl1:937-939); VPIM's f_UnaryStringOpe_Sub
(functions/f_reduce_string_ope.psl.c:1206-1229) is the binary
operation with Str1 and Pos1 again in place of the second string
("Dummy"), so each element becomes op(e, e).  NewS2 is given Str1
(OURS).

The built-ins run through their stubs (asm/pimm_stubs.py).  Parts and
the values expected, worked by hand here, not by either model:
  1 bit     new_string(40, 1): descriptor 24 << 27 | 2, [0]*40;
            set_string_element 0, 33 (in the second word) and 5 to 3
            (kept to its low bit: 1); string_element 33 = 1, 34 = 0;
            string(S, 40, 1); change_element_size to 8: five bytes
            80h 04h 00h 00h 40h; search_character for 1 from 0 to 39
            (0) and from 39 down to 6 (33); the binary string_operation
            7 (or) of 31 elements from 2 of a second string, ones at 3
            and 32, into the first; new_string(32, 1) (pad 0, one
            word), new_string(0, 1) (no word).
  unary     on a 1-bit string: op 15 (set) on 31 elements from 2,
            across the word; op 10 (not) on 6 elements from 30 after
            it; op 0 (clear) on 0 elements (the copy); on an 8-bit
            string: op 10 on [1, 2, 3] from 1, 2 elements.  NewS2 is
            Str1 each time.
  wait      the unary form waiting on its Len, bound later (the stub's
            goal waits on the first unbound element, as the binary).
  refused   change_element_size of a 1-bit string to 1 bit: refused
            on both models (last, no OUT after it).

Observed fault injections into the Bluespec, 2026-11-25, each built
alone from a copy of bsv/PimmSBox.bsv or bsv/PimmStages.bsv (the
first difference of each):
  new_string of 1 bit made as 8 bits    1 bit, line 17: M 32776
                                        250300000a for 25c0000002
  the 1-bit pad read two bits wide      1 bit, line 199: R 4 40 (the
                                        length) for 28
  the 1-bit mask taken as 8 bits        1 bit, line 106: M 32813
                                        000c000000 for 0084000000
  the unary form's Pos2 taken from Len  unary, line 27: E error:
    (not from Pos1)                     string_operation: out of range,
                                        for M 32934 25c0000002
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=4, lines=746)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731


def bits(n, ones):
    return [1 if i in ones else 0 for i in range(n)]


def script():
    stubs = pimm.Machine().stubs
    s = driver.Script()
    want = []

    def call(name, ins, outs):
        """The built-in through its stub: inputs are cells or
        ('slot', n); outs are slots, made new variables."""
        k = 1
        for a in ins:
            if a[0] == 'slot':
                s.arg(k, a[1])
            else:
                s.argc(k, a)
            k += 1
        for o in outs:
            s.newvar(o)
            s.arg(k, o)
            k += 1
        s.spawn(stubs[name]['addr'], k - 1)
        s.run()

    # 1. 1-bit strings
    s.label('1 bit')
    call('new_string', [I(40), I(1)], [0])
    s.out(0)
    call('set_string_element', [('slot', 0), I(0), I(1)], [1])
    call('set_string_element', [('slot', 1), I(33), I(1)], [2])
    call('set_string_element', [('slot', 2), I(5), I(3)], [3])
    s.out(3)
    call('b_string_element', [('slot', 3), I(33)], [4, 5])
    s.out(4)
    call('b_string_element', [('slot', 3), I(34)], [4, 5])
    s.out(4)
    call('b_string', [('slot', 3)], [4, 5, 6])
    s.out(4)
    s.out(5)
    call('change_element_size', [('slot', 3), I(8)], [4])
    s.out(4)
    call('search_character', [('slot', 3), I(0), I(39), I(1)], [4, 5])
    s.out(4)
    call('search_character', [('slot', 3), I(39), I(6), I(1)], [4, 5])
    s.out(4)
    s.string(6, 1, bits(40, {3, 32}))
    s.vector(7, 8, [I(2), ('slot', 3), I(31), I(2), ('slot', 6)])
    call('string_operation', [I(7), ('slot', 7)], [4, 5])
    s.out(4)
    s.out(5)
    call('new_string', [I(32), I(1)], [4])
    s.out(4)
    call('new_string', [I(0), I(1)], [4])
    s.out(4)
    s0 = bits(40, {0, 5, 33})
    orr = list(s0)
    for i in range(31):
        orr[2 + i] |= bits(40, {3, 32})[2 + i]
    want.append(('1 bit', [
        (1, [0] * 40), (1, s0), 1, 0, 40, 1, (8, [0x84, 0x00, 0x00, 0x00, 0x40]), 0, 33,
        (1, orr), (1, bits(40, {3, 32})), (1, [0] * 32), (1, [])]))

    # 2. the unary form
    s.label('unary')
    exp = []
    for op, pos, n, fn in ((15, 2, 31, lambda e: 1), (10, 30, 6, lambda e: 1 - e),
                           (0, 4, 0, lambda e: 0)):
        s.vector(7, 8, [I(pos), ('slot', 3), I(n)])
        call('string_operation', [I(op), ('slot', 7)], [4, 5])
        s.out(4)
        s.out(5)
        e = list(s0)
        for i in range(pos, pos + n):
            e[i] = fn(e[i])
        exp += [(1, e), (1, s0)]
    s.string(6, 8, [1, 2, 3])
    s.vector(7, 8, [I(1), ('slot', 6), I(2)])
    call('string_operation', [I(10), ('slot', 7)], [4, 5])
    s.out(4)
    s.out(5)
    exp += [(8, [1, 0xfd, 0xfc]), (8, [1, 2, 3])]
    want.append(('unary', exp))

    # 3. waiting on Len
    s.label('wait')
    s.vector(7, 8, [I(1), ('slot', 3), None])      # Len in slot 10
    call('string_operation', [I(15), ('slot', 7)], [4, 5])
    s.out(4)
    s.unifyc(10, I(4))
    s.run()
    s.out(4)
    e = list(s0)
    for i in range(1, 5):
        e[i] = 1
    want.append(('wait', [None, (1, e)]))

    # 4. refused: a change to 1 bit
    s.label('refused')
    call('change_element_size', [('slot', 3), I(1)], [4])
    want.append(('refused', []))
    s.want = want
    return s


def check(s, m):
    got = [None if m.unbound(w) else m.term(w) for _l, w in s.outs]
    exp = [v for _n, vs in s.want for v in vs]
    bad = [] if got == exp else [(i, g, e) for i, (g, e) in enumerate(zip(got, exp)) if g != e]
    if len(got) != len(exp):
        bad.append(('outs', len(got), len(exp)))
    d = m.mem[m.deref(s.outs[0][1])[1]]
    if d != (pimm.CDESC, 24 << 27 | 2):
        bad.append(('descriptor', d))
    return bad


def refusing(s, orig):
    """s.play(), its last part refused: the reference's Unimplemented
    is the core's `E unimp` line, the part's trace up to there kept."""
    gen = orig()
    while True:
        try:
            item = next(gen)
        except StopIteration:
            return
        except pimm.Unimplemented as e:
            s.refused = str(e)
            yield 'the refusal', s.machine.tr + ['E unimp']
            return
        yield item


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    orig = s.play
    s.play = lambda: refusing(s, orig)
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s, s.machine)
        print(bad, n, getattr(s, 'refused', None))
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep s1', PINNED)
    if not ok:
        return 1
    bad = check(s, m)
    if bad:
        print('pimm lockstep s1: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep s1: PASS (strings of 1-bit elements and the unary string_operation '
          'on the Bluespec core, %d parts, %d trace lines identical to the reference model: '
          'the answers as worked by hand; a change to 1 bit refused on both)'
          % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
