#!/usr/bin/env python3
"""Lockstep: string_less_than and string_not_less_than's order, the
extended-float comparison guards on other arguments, and a string
unified with itself (R8, 2026-11-25: all three met by the KL1 Listener
on the goal typed at its prompt).

    python3 ref/pimm/lockstep_sord.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_sord.py compare
    python3 ref/pimm/lockstep_sord.py --reference       the reference alone

string_less_than(S1, S2), 23:FE r_r, and string_not_less_than, 23:FF
(assembler/inst_tab.kl1:227, 229; compiler/blt.kl1:392-397, both inputs
waited for).  The PIMOS manual's order (e-builtin.tex:813-837): the
string of wider elements is larger; otherwise element by element from
the first, a longer string larger; Suspend if either is unbound, Fail
if either is not a string.  As VPIM computes it (s_WhichIsLessString,
structures/str_string.psl.c, called from functions/
f_reduce_string_ope.psl.c:251): element sizes, then the words from the
first as UNSIGNED, a string whose words run out first smaller, then
the element counts (pimm.py string_order).

extended_floating_point_less_than / _not_less_than, 23:6E with x = 2
and 3 (inst_tab.kl1:98-99; blt.kl1:417-424): fail unless both
arguments are extended floats, as the held sorter needs
(utility/sorter/sorter.kl1:51-71, its comparator trying each kind in
turn); two extended floats are refused (none can be made here).

Code of OURS, in the heap as lockstep_alt.py's (try_me_else's offset
from the cell after it):

  less     p(S1, S2, R) :- string_less_than(S1, S2) | R = 1.
           p(S1, S2, R) :- string_not_less_than(S1, S2) | R = 0.
           (try_me_else @4; string_less_than 0, 1; get_integer 2, 1;
           proceed; try_me_else @8; string_not_less_than 0, 1;
           get_integer 2, 0; proceed; suspend 3, @0)
  xf       q(X, Y, R) :- X $$< Y | R = 1.   q(X, Y, R) :- true | R = 0.
           (try_me_else @4; 23:6E 2, 0, 1; get_integer 2, 1; proceed;
           get_integer 2, 0; proceed), and the same with x = 3
  self     r(S, R) :- true | S = S, R = 1.  (get_value 0, 0;
           get_integer 1, 1; proceed)

Parts, R as the manual's order gives it (1: S1 < S2), not from a model:
  words       "abc" "abd" 1; "abd" "abc" 0; "abc" "abc" (two objects)
              0; "ab" "abc" 1 (a word of fewer elements, the pad
              zero); "\\x80" "a" 0 (unsigned: 80h above 61h)
  widths      8-bit "zz" and 16-bit "a": 1; the other way 0
  counts      "abcd" "abcde" 1 (a word more); "ab" "ab\\0" 1 (the same
              words, an element more); and the other way 0
  waits       S1 unbound: the goal suspends; S1 = "a", S2 "b": 1
  xf          q(1, 2, R) and q(a, 2, R) for x = 2 and 3: the guard
              fails, R = 0 (no Unimplemented)
  self        r("ab", R): R = 1, the string unified with itself
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=7, lines=573)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
KLB = 0x23
B = lambda t: [ord(c) for c in t]                  # noqa: E731
# (S1 bits, S1, S2 bits, S2, R)
WORDS = [(8, 'abc', 8, 'abd', 1), (8, 'abd', 8, 'abc', 0), (8, 'abc', 8, 'abc', 0),
         (8, 'ab', 8, 'abc', 1), (8, '\x80', 8, 'a', 0)]
WIDTHS = [(8, 'zz', 16, 'a', 1), (16, 'a', 8, 'zz', 0)]
COUNTS = [(8, 'abcd', 8, 'abcde', 1), (8, 'ab', 8, 'ab\x00', 1),
          (8, 'abcde', 8, 'abcd', 0), (8, 'ab\x00', 8, 'ab', 0)]
EXPECT = {'words': [r for *_x, r in WORDS], 'widths': [r for *_x, r in WIDTHS],
          'counts': [r for *_x, r in COUNTS], 'waits': [1], 'xf': [0, 0, 0, 0],
          'self': [1]}
ENDS = {'waits': 1}    # the goals that suspend once ('E susp')


def heap_code(s, words, names):
    """The code in the heap: one vector's cells, or two made one after
    the other (a vector is six cells at most; the names checked prove
    them contiguous)."""
    s.vector(15, 4, words[:6])
    if len(words) > 6:
        s.vector(14, 10, words[6:])
    m = s.live()
    at = s.live_slot[15][1] - m.load
    got = [m.opname(at + i) for i in range(len(words))]
    assert got == names, got
    return at


def script():
    s = driver.Script()
    less = heap_code(s, [(KLB, 0x68 << 24 | 2),                  # try_me_else @4
                         (KLB, 0xfe << 24 | 0 << 16 | 1 << 8),   # string_less_than 0, 1
                         (KLB, 0xb9 << 24 | 2 << 16 | 1),        # get_integer 2, 1
                         (KLB, 0x60 << 24),                      # proceed
                         (KLB, 0x68 << 24 | 2),                  # try_me_else @8
                         (KLB, 0xff << 24 | 0 << 16 | 1 << 8),   # string_not_less_than 0, 1
                         (KLB, 0xb9 << 24 | 2 << 16 | 0),        # get_integer 2, 0
                         (KLB, 0x60 << 24),                      # proceed
                         (KLB, 0x69 << 24 | 3 << 16 | 0xfff6)],  # suspend 3, @0
                     ['try_me_else', 'string_less_than', 'get_integer', 'proceed',
                      'try_me_else', 'string_not_less_than', 'get_integer', 'proceed',
                      'suspend'])

    def p(cases):
        for b1, t1, b2, t2, _r in cases:
            s.string(0, b1, B(t1))
            s.string(1, b2, B(t2))
            s.newvar(2)
            for i in range(3):
                s.arg(i + 1, i)
            s.spawn(less, 3)
            s.run()
            s.out(2)
    s.label('words')
    p(WORDS)
    s.label('widths')
    p(WIDTHS)
    s.label('counts')
    p(COUNTS)
    s.label('waits')
    s.newvar(0)
    s.string(1, 8, B('b'))
    s.newvar(2)
    for i in range(3):
        s.arg(i + 1, i)
    s.spawn(less, 3)
    s.run()
    s.string(3, 8, B('a'))
    s.unify(0, 3)
    s.run()
    s.out(2)
    s.label('xf')
    for fn in (2, 3):
        xf = heap_code(s, [(KLB, 0x68 << 24 | 2),                     # try_me_else @4
                           (KLB, 0x6e << 24 | fn << 16 | 0 << 8 | 1),  # 23:6E fn, 0, 1
                           (KLB, 0xb9 << 24 | 2 << 16 | 1),           # get_integer 2, 1
                           (KLB, 0x60 << 24),                         # proceed
                           (KLB, 0xb9 << 24 | 2 << 16 | 0),           # get_integer 2, 0
                           (KLB, 0x60 << 24)],                        # proceed
                       ['try_me_else', 'extended_floating_point_less_than'
                        if fn == 2 else 'extended_floating_point_not_less_than',
                        'get_integer', 'proceed', 'get_integer', 'proceed'])
        for x in (I(1), (pimm.ATOM, 0)):
            s.argc(1, x)
            s.argc(2, I(2))
            s.newvar(2)
            s.arg(3, 2)
            s.spawn(xf, 3)
            s.run()
            s.out(2)
    s.label('self')
    me = heap_code(s, [(KLB, 0xbc << 24 | 0 << 16 | 0 << 8),   # get_value 0, 0
                       (KLB, 0xb9 << 24 | 1 << 16 | 1),        # get_integer 1, 1
                       (KLB, 0x60 << 24)],                     # proceed
                   ['get_value', 'get_integer', 'proceed'])
    s.string(0, 8, B('ab'))
    s.newvar(1)
    s.arg(1, 0)
    s.arg(2, 1)
    s.spawn(me, 2)
    s.run()
    s.out(1)
    return s


def check(s, m, parts):
    bad = []
    outs = {}
    for label, w in s.outs:
        outs.setdefault(label, []).append(None if m.unbound(m.deref(w)) else m.term(w))
    # 'start': the code made in the heap before the first part
    if list(parts) != ['start'] + list(EXPECT):
        return [('parts', list(parts))]
    for k, want in EXPECT.items():
        if outs.get(k) != want:
            bad.append((k, outs.get(k), want))
        n = parts[k].count('E susp')
        if n != ENDS.get(k, 0):
            bad.append((k, 'suspensions', n))
        if 'E fail' in parts[k] or 'E unimp' in parts[k]:
            bad.append((k, 'a reduction failed'))
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
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep sord', PINNED)
    if not ok:
        return 1
    bad = check(s, m, kept)
    if bad:
        print('pimm lockstep sord: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep sord: PASS (string_less_than, string_not_less_than, the '
          'extended-float guards and a string unified with itself on the Bluespec core, '
          '%d parts, %d trace lines identical to the reference model: the order by element '
          'width, unsigned words, word count and element count; the guards fail on '
          'integers and atoms)' % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
