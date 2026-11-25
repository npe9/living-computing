#!/usr/bin/env python3
"""Lockstep: strings of 32-bit elements made by new_string.

    python3 ref/pimm/lockstep_s32.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_s32.py compare

new_string(Size, ElementSize, ^String) with ElementSize 32 (the PDSS
manual allows 1 to 32; 8 and 16 were in, 1 is not).  The system
files need it: the IPL stops at new_string(1, 32) in pimm_bios360E.sav
without it.  A string of 32-bit elements is {CDESC, 5 << 24 | words},
one element a word (library/kbn/kbnheap.kl1 string_cdesc).

The built-ins are run through their stubs (asm/pimm_stubs.py):
new_string(3, 32), set_string_element of element 1 to 92345678h,
string_element of elements 1 and 2, new_string(0, 32) and (1, 32).
Checked: each string's elements, the element read back (as a signed
integer), the first descriptor, no goal left waiting.

Observed fault injections into the Bluespec, 2026-11-23, restored:
  new_string: 32 taken as 16       s32: line 17 (the descriptor)
  new_string: one word too few     conv: part 1, line 0
Not run: string_operation, substring, the hash and equality of a
32-bit string.  1-bit strings: lockstep_s1.py (2026-11-25).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=1, lines=172)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
VALUE = 0x92345678


def script():
    stubs = pimm.Machine().stubs
    s = driver.Script()
    s.label('32 bits')

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

    call('new_string', [I(3), I(32)], [0])
    s.out(0)
    call('set_string_element', [('slot', 0), I(1), I(VALUE)], [1])
    s.out(1)
    call('b_string_element', [('slot', 1), I(1)], [2, 3])
    s.out(2)
    call('b_string_element', [('slot', 1), I(2)], [4, 5])
    s.out(4)
    call('new_string', [I(0), I(32)], [9])
    s.out(9)
    call('new_string', [I(1), I(32)], [10])
    s.out(10)
    return s


def check(s, m):
    got = [None if m.unbound(w) else m.term(w) for _l, w in s.outs]
    exp = [(32, [0, 0, 0]), (32, [0, VALUE, 0]), pimm.signed(VALUE), 0, (32, []), (32, [0])]
    bad = [] if got == exp else [(got, exp)]
    # the descriptor of the first: type 5, no pad, three words
    d = m.mem[m.deref(s.outs[0][1])[1]]
    if d != (pimm.CDESC, 5 << 24 | 3):
        bad.append(('descriptor', d))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        n = sum(len(ls) for _w, ls in s.play())
        print(check(s, s.machine), n)
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep s32',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m)
    if bad:
        print('pimm lockstep s32: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep s32: PASS (new_string with 32-bit elements on the Bluespec core, %d '
          'trace lines identical to the reference model; an element set and read back, the '
          'descriptor as kbnheap.kl1 has it)' % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
