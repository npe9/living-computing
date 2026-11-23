#!/usr/bin/env python3
"""Lockstep: a goal of more than eleven arguments.

    python3 ref/pimm/lockstep_pack.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_pack.py compare

A goal has 11 argument slots.  The compiler packs the arguments from
the 11th on into a vector, which is passed as the 11th
(library/compiler/pack.kl1: max_goal_slots(X) :- true | X=11, "for
V2"; pack_body_goal).  The image has two such goals, and both are made
that way: ipl_module:load/4 makes check_status/12 with eleven set_*
and a 2-vector, ipl_file_decoder:decode/8 makes check_magic_num/13
with eleven and a 3-vector.  The called predicate has no code to
unpack: check_status/12 reads r10 and r11.  So the firmware spreads
the vector; where it does is not known.  Both models spread it as the
goal is made, and their record holds every argument (the record's
layout is ours anyway).

The goal run: ipl_module:load/4 on a module with no entries.  The
module is a real one of pimm_kernel360E.sav, decoded by
ipl_file_decoder:load_module/7 from the file's words with its entry
table replaced by an empty one.  set_pred_table/6 refuses the empty
list, so check_status/12 takes its last clause (object code,
asm/kl1decomp.py):

    load(module(...), J, K, L) :- ... check_status(W, X, Y, B, A, Z, Q, _, J, K, {A1, L}) ...
    check_status(_, _, _, _, _, _, _, _, A, B, _, C) :- true |
        B = A, abnormal(string8#"Module Generation Error") = C.

Check: K is J, and L, which is only reachable as the 12th argument, is
abnormal("Module Generation Error").

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  packed arguments not spread        the first module: A 11 not written
  spread starts one argument late    the same: A 12 written for A 11
  spread repeats the first element   the same: A 12 gets the 11th argument
  spread stops one short             the same: A 12 not written

A goal of 13 arguments (decode/8's, a 3-vector) is run by
lockstep_file.py.  Not run: the refusals (no vector, a vector of
another size, more than 16).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_deca as deca  # noqa: E402
import lockstep_modc as modc  # noqa: E402

PINNED = dict(parts=2, lines=106052)
MODULES = ('system2defined2servers', 'task2std2abnormal')
TEXT = 'Module Generation Error'


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    names = {name: n for n, name in im.sym.items()}
    mods = {m['name']: m for m in modc.modules()}
    # the two goals of more than 11 arguments are made as the header says
    made = []
    for a, (t, v) in enumerate(im.cells):
        if t == 0x23 and im.dis(a).split()[0] == 'enqueue_goal' and (v >> 16 & 255) > 11:
            n = v >> 16 & 255
            made.append((n, im.dis(a - 1), im.dis(a - (n - 10) - 2).split()[0]))
    assert [(n, d.split()[0], d.split()[1][:2], p) for n, d, p in made] == \
        [(13, 'set_value', '11', 'put_vector_3'), (12, 'set_value', '11', 'put_vector_2')], made
    want = []
    for name in MODULES:
        mod = mods[name]
        whole = mod['whole']
        head = whole[:len(whole) - len(mod['index']) - len(mod['code'])]
        words = head + [mod['hs'], 0] + mod['code']
        label = '%s without entries' % name
        s.label(label)
        for i in (0, 1, 2, 3, 4, 7):
            s.newvar(i)
        s.arg(1, 2)
        s.argc(2, (pimm.INT, 77))
        for a, sl in ((3, 0), (4, 1), (5, 7), (6, 3), (7, 4)):
            s.arg(a, sl)
        s.spawn(pimm.predicate(im, 'ipl_file_decoder', 'load_module/7'), 7)
        s.live()
        table = {k: deca.number(k, v) for k, v in mod['atoms_before'].items()}
        at, atq, feed = deca.serve(s, s.live_slot[0], s.live_slot[7], words, table, names, [])
        assert not feed
        for i in (9, 10, 11):
            s.newvar(i)
        s.arg(1, 2)
        s.arg(2, 9)
        s.arg(3, 10)
        s.arg(4, 11)
        s.spawn(pimm.predicate(im, 'ipl_module', 'load/4'), 4)
        s.run()
        for i in (9, 10, 11):
            s.out(i)
        want.append(label)
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for label in want:
        j, k, status = got[label][-3:]
        if not (m.unbound(j) and j == k):
            bad.append((label, 'K is not J', j, k))
        if m.unbound(status) or m.term(status) != ('abnormal', (8, [ord(c) for c in TEXT])):
            bad.append((label, 'status', status))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep pack', PINNED)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad:
        print('pimm lockstep pack: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep pack: PASS (a goal of 12 arguments, the 11th and 12th packed in a '
          'vector as the compiler makes it, on the Bluespec core: ipl_module:load/4 refuses '
          '%d real modules given without entries, %d trace lines identical to the reference '
          'model; the status arrives through the 12th argument)'
          % (len(MODULES), s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
