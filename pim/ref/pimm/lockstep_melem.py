#!/usr/bin/env python3
"""Lockstep: module_element(Module, Position, ^Element).

    python3 ref/pimm/lockstep_melem.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_melem.py compare
    python3 ref/pimm/lockstep_melem.py --reference       the reference alone

module_element, 22:F7 r_r_r (assembler/inst_tab.kl1:356; compiler/
blt.kl1:617-618): element Position of the module, counted from the
cell after its descriptor: the unloader writes {MOD, A}, {CDESC, 06 <<
24 | Length}, then element 0, the GC size (library/kbn/kbn.kl1
encode_module:140-158), and module_utility reads element 1 as the
module's name and 2 as its package (library/utility/modutil.kl1:52-67).
A Position from Length up, or a Module not a module, is the built-in's
exception (VPIM interpreter/klb_body_blt_cont.psl.c
kblt_b_module_element): refused.  Met compiling the primer's sample1
(2026-11-25, module_utility ground_module/3).

Parts, the expected values from the image as asm/kbndis.py decodes it
(its own reader of the module layout, not either model):
  image       three modules of the IPL image (the first, one in the
              middle, the last): elements 0 (the GC size), 1 (the name,
              the module's name in kbndis's table) and 2 (the package)
  new_module  a module made by new_module from {06000003h, an atom, 7,
              9}: elements 0, 1, 2 are the atom, 7 and 9
  wait        the Position unbound, bound later: the stub's goal waits
              on it and then answers
  refused     Position = Length on an image module: refused on both
              models (last, no OUT after it)

Observed fault injections into the Bluespec (bsv/PimmStages.bsv, rules
modElem1 and modElem2), 2026-11-25, each built alone from a copy:
  the element counted from the          image, line 17: R 3 2506000741
    descriptor (no + 1)                 (the descriptor) for 1a
  Position = Length accepted            the refusal, line 17: R 3
                                        020000002d for E unimp
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=4, lines=391)
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731


def script():
    im = pimm.kbndis.Image()
    stubs = pimm.Machine().stubs
    s = driver.Script()
    want = []

    def call(name, ins, outs):
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

    # 1. modules of the image
    s.label('image')
    exp = []
    mods = [im.mods[0], im.mods[len(im.mods) // 2], im.mods[-1]]
    for md in mods:
        a = md['addr']
        mod = im.cells[a]
        assert mod[0] == pimm.MOD and im.cells[a + 1] == (pimm.CDESC, 6 << 24 | md['length'])
        for i in range(3):
            call('module_element', [mod, I(i)], [0])
            s.out(0)
        gc = im.cells[a + 2]
        assert gc[0] == pimm.INT
        exp += [gc[1], md['name'], md['package']]
    want.append(('image', exp))

    # 2. a module of new_module
    s.label('new_module')
    s.vector(1, 8, [I(6 << 24 | 3), (pimm.ATOM, 1), I(7), I(9)])
    call('new_module', [('slot', 1)], [2])
    for i in range(3):
        call('module_element', [('slot', 2), I(i)], [0])
        s.out(0)
    want.append(('new_module', [im.atom(1), 7, 9]))

    # 3. the position waited for
    s.label('wait')
    s.newvar(3)
    call('module_element', [im.cells[mods[1]['addr']], ('slot', 3)], [0])
    s.out(0)
    s.unifyc(3, I(1))
    s.run()
    s.out(0)
    want.append(('wait', [None, mods[1]['name']]))

    # 4. refused: one past the end
    s.label('refused')
    call('module_element', [im.cells[mods[0]['addr']], I(mods[0]['length'])], [0])
    want.append(('refused', []))
    return s, want


def check(s, m, want):
    got = [None if m.unbound(w) else m.term(w) for _l, w in s.outs]
    exp = [v for _n, vs in want for v in vs]
    bad = [(i, g, e) for i, (g, e) in enumerate(zip(got, exp)) if g != e]
    if len(got) != len(exp):
        bad.append(('outs', len(got), len(exp)))
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
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    orig = s.play
    s.play = lambda: refusing(s, orig)
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s, s.machine, want)
        print(bad, n, getattr(s, 'refused', None))
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep melem', PINNED)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad:
        print('pimm lockstep melem: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep melem: PASS (module_element on the Bluespec core, %d parts, %d '
          'trace lines identical to the reference model: the GC size, name and package of '
          'three image modules as asm/kbndis.py reads them, a new_module\'s elements, a '
          'position waited for; one past the end refused on both)'
          % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
