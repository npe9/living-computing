#!/usr/bin/env python3
"""Lockstep: the IPL's file decoder loads whole real modules.

    python3 ref/pimm/lockstep_lmod.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_lmod.py compare

ipl_file_decoder:load_module/7 on whole modules of the real
pimm_kernel360E.sav, each from its first word to the FFFF that ends
its code.  The argument roles are read from the object code
(asm/kl1decomp.py):

    load_module(Module, X, In, Rest, AT0, AT, Status)

    Module = module(Name, X, W3, Info, HashSize, Twice, Entries, Size, Code)

Name is the first of the module's two names (the second is read and
dropped), X is passed through (77 here; load_modules/8 gives it), W3
is the module's third word (the first two, its length, are skipped),
Info is lockstep_gca.py's result, and HashSize, Twice, Entries, Size
and Code are lockstep_modc.py's.  module/9 is ten cells: the general
put_vector builds it.

The test plays the reader and the atom table (lockstep_deca.serve).
Oracle: asm/unlsav.py's reading of the same words, composed with the
expected() functions of those two tests; their headers say what it
does and does not confirm.

Modules: MODULES.

New here: the general put_vector.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  put_vector: structure pointer at   the first module: 'module' written over
    the descriptor                   the descriptor
  put_vector writes r[y]             the same: R 0 written for R 13
  put_vector: one cell fewer         the same: the descriptor's length 9 for 10
  build fills with zeros first       the same: a cell written the model does not

Not caught: put_vector taking its size from 8 bits.  The only size run
is 10 (the image also has 7 and 8, in predicates not run yet).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_deca as deca  # noqa: E402
import lockstep_gca as gca  # noqa: E402
import lockstep_modc as modc  # noqa: E402

PINNED = dict(parts=4, lines=503734, items=2928)
MODULES = ('system2defined2servers', 'task2std2abnormal', 'copy', 'shoen')
X = 77


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    pc = pimm.predicate(im, 'ipl_file_decoder', 'load_module/7')
    names = {name: n for n, name in im.sym.items()}
    areas = gca.areas()
    mods = modc.modules()
    assert [a[0] for a in areas] == [m['name'] for m in mods]
    want, items = [], 0
    for name in MODULES:
        k = [m['name'] for m in mods].index(name)
        mod, area = mods[k], areas[k]
        words, before = mod['whole'], mod['atoms_before']
        label = '%s: %d words' % (name, len(words))
        s.label(label)
        for i in (0, 1, 2, 3, 4, 7):
            s.newvar(i)
        s.arg(1, 2)
        s.argc(2, (pimm.INT, X))
        s.arg(3, 0)
        s.arg(4, 1)
        s.arg(5, 7)
        s.arg(6, 3)
        s.arg(7, 4)
        s.spawn(pc, 7)
        s.live()
        table = {i: deca.number(i, v) for i, v in before.items()}
        at, atq, feed = deca.serve(s, s.live_slot[0], s.live_slot[7], list(words), table,
                                   names, [])
        assert not feed, (label, len(feed))
        s.setslot(5, at)
        s.setslot(6, atq)
        for i in (1, 2, 3, 4, 5, 6):
            s.out(i)
        exp = ('module', modc.atom(mod['name_id'], mod['atoms']), X, words[2],
               gca.expected(area[3], {}), mod['hs'], 2 * len(mod['preds']),
               modc.expected_index(mod), mod['detail']['code_size'], modc.expected_code(mod))
        want.append((label, exp))
        items += len(area[3]) - 2 + len(mod['preds']) + len(mod['items'])
    s.items = items
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for label, exp in want:
        unlfs, obj, at, status, tail, atail = got[label][-6:]
        t = m.term(obj)
        if t != exp:
            d = [i for i in range(min(len(t), len(exp))) if t[i] != exp[i]][:1]
            bad.append((label, len(t), [(i, str(t[i])[:200], str(exp[i])[:200]) for i in d]))
        if not (m.unbound(tail) and unlfs == tail and m.unbound(atail) and at == atail):
            bad.append((label, 'streams left'))
        if m.term(status) != 'normal':
            bad.append((label, m.term(status)))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    pinned = dict(PINNED)
    items = pinned.pop('items')
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep lmod', pinned)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad or s.items != items:
        print('pimm lockstep lmod: FAIL, %d items (pinned %d); answers differ: %s'
              % (s.items, items, repr(bad[:1])[:600]))
        return 1
    print('pimm lockstep lmod: PASS (the IPL file decoder loads %d whole modules of the '
          'real pimm_kernel360E.sav on the Bluespec core: %d GC elements, entries and '
          'code items, %d trace lines identical to the reference model; each module/9 '
          'term as asm/unlsav.py reads the same words)'
          % (len(MODULES), s.items, s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
