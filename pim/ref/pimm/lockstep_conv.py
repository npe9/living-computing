#!/usr/bin/env python3
"""Lockstep: jis_to_ascii:convert/2, the whole module, on the Bluespec core.

    python3 ref/pimm/lockstep_conv.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_conv.py compare

convert/2 takes a 16-bit JIS string and gives the 8-bit ASCII string
(bios/boot/jtoa.kl1).  It runs convert_loop/4, which spawns a
convert_loop goal and continues as convert_element/2 for each element,
with string_element and set_string_element; as compiled,
set_string_element is reached before its element is bound, so it waits
as a goal of its stub and runs when convert_element binds the element.

The script (ref/pimm/driver.py) builds each input string in the
machine's memory and runs the goal:

    empty, one element, every mapped key (94), a mixed string with
    unmapped keys, and "PIMOS 3.6" in full-width characters
    an unbound argument, bound to a string after the goal suspends
    b_add with both inputs unbound, as a goal of its own stub: it
    waits on the first; binding the second wakes nothing
    an 8-bit string, for which no clause applies: the reduction fails

The Bluespec trace must equal the reference model's line for line, and
each result on the reference model must be the string the source-
derived oracle gives (test_jtoa.py), so the trace is tied to the
source and not only to the other model.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  SBox  elements packed from the bottom          one: the string's word
  SBox  set_string_element shifts the element    one: the string's word
  SBox  new string's padding count dropped       one: the descriptor cell
  Exec  string_element's outputs swapped         one: R 4 for R 1
  Exec  string/3 length and size swapped         empty: R 2 = 16 for 0
  Exec  two-word built-in continues at the next
        cell                                     one: I 9366, its second word
  Exec  put_variable's second register           one: R 7 for R 6
  Exec  wait does not note the variable          unbound: E fail for the record
  Exec  wait_integer compares four bits          mapped: wrong clause, I 9356
  Exec  waiting built-in hooked on the last
        unbound input                            add: the wrong variable hooked
  GBox  waiting built-in's output register not
        given its variable                       one: the R line missing
  GBox  enqueue_goal arguments from a0           jtoa key 0000: the record's
                                                 argument cell
  Exec  b_add subtracts                          jtoa key 2330: R 0
NOT caught, each PASSed (what the runs cannot tell):
  execute keeps the old alternative clause       every predicate executed
                                                 here begins with try_me_else
  guard subtract writes its first operand        the only use is subtract 0,4,0
                                                 (asm/bltdir.py gives iio)
  less_than is less-or-equal                     the only use is 0 < N after
                                                 N = 0 has been tried
"Hooked on the last unbound input" passed until the add scenario was
written for it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import driver  # noqa: E402
import pimm  # noqa: E402
import test_jtoa  # noqa: E402

PINNED = dict(parts=8, lines=35743)
PIMOS = [0x2350, 0x2349, 0x234d, 0x234f, 0x2353, 0x2121, 0x2333, 0x2125, 0x2336]


def cases(f):
    mapped = [k for k in range(0x10000) if f(k) != ord('?')]
    return [('empty', []), ('one', [0x2350]), ('mapped', mapped),
            ('mixed', mapped[::-1] + [0x3021, 0, 0xffff]), ('PIMOS 3.6', PIMOS)]


def script(f):
    s = driver.Script()
    conv = pimm.predicate(pimm.kbndis.Image(), 'jis_to_ascii', 'convert/2')

    def goal(arg_slot, out_slot):
        s.arg(1, arg_slot)
        s.arg(2, out_slot)
        s.spawn(conv, 2)
        s.run()
        s.out(out_slot)

    for name, jis in cases(f):
        s.label(name)
        s.string(0, 16, jis)
        s.newvar(1)
        goal(0, 1)
    s.label('unbound')
    s.newvar(0)
    s.newvar(1)
    goal(0, 1)
    s.string(2, 16, [0x2341, 0x2342])
    s.unify(0, 2)
    s.run()
    s.out(1)
    # A built-in with two unbound inputs, run as a goal of its own stub:
    # b_add(X, Y, Z) waits on X, the first; binding Y wakes nothing;
    # binding X wakes it, and it finishes.
    s.label('add')
    for i in range(3):
        s.newvar(i)
        s.arg(i + 1, i)
    s.spawn(pimm.Machine().stubs['b_add']['addr'], 3)
    s.run()
    s.out(2)
    s.unifyc(1, (pimm.INT, 5))
    s.run()
    s.out(2)
    s.unifyc(0, (pimm.INT, 7))
    s.run()
    s.out(2)
    s.label('8-bit')
    s.string(0, 8, [65])
    s.newvar(1)
    goal(0, 1)
    return s


def main(argv):
    f, _n = test_jtoa.oracle()
    s = script(f)
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep conv', PINNED)
    if not ok:
        return 1
    # the reference model's answers against the source
    want = dict((name, [f(k) for k in jis]) for name, jis in cases(f))
    want['unbound'] = [65, 66]
    bad = []
    last = {}
    for label, w in s.outs:
        last[label] = w
    for label, exp in want.items():
        w = last[label]
        if w[0] & ~1 != pimm.STRG or m.string(w) != (8, exp):
            bad.append(label)
    if not m.unbound(last['8-bit']):
        bad.append('8-bit')
    if last['add'] != (pimm.INT, 12):
        bad.append('add')
    waits = m.builtin_waits
    if bad or waits != sum(len(j) for _n, j in cases(f)) + 2 + 1:
        print('pimm lockstep conv: FAIL, wrong answers %r, %d built-in waits' % (bad, waits))
        return 1
    print('pimm lockstep conv: PASS (convert/2 from the IPL image on the Bluespec '
          'core: %d scenarios, %d trace lines identical to the reference model; '
          'answers as the source gives, "%s" among them; %d built-in waits)'
          % (s.counts['parts'], s.counts['lines'],
             bytes(m.string(last['PIMOS 3.6'])[1]).decode(), waits))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
