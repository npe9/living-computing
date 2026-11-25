#!/usr/bin/env python3
"""Lockstep: an external call between two modules the IPL loaded.

    python3 ref/pimm/lockstep_xmod.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_xmod.py compare
    python3 ref/pimm/lockstep_xmod.py --reference       the reference alone

An external call (execute_external, enqueue_goal_external) finds its
predicate through a four-cell descriptor in the calling module's GC
area: the cache field, the module field, the key, the module's name
(TM-662 fig. 2; docs/pimm_semantics.md `execute_external`).  In the
image the module field reaches the module object through the module
table (two references); in a module the IPL loaded it is a reference
to a variable, which the IPL's linker binds to the module object
(ipl_link_table:unify_modules/1 as decompiled: "unify_modules([{A,
B}|C]) :- true | B = A, ..."), so both models dereference the field
(commit a35c9a3f).  lockstep_ext.py runs the image's form only; this
test runs the loaded form on both models.

The file: pimm_patch_mkdir360E.sav (41,359 words, six modules), loaded
by ipl_loader:load/4 exactly as lockstep_link.py's second part loads it
(its script, reused: the IPL's loader, atom table and linker, the bench
answering open and the buffers).  That link is ABNORMAL (the file calls
sixteen modules it does not hold), so the linker never reaches
unify_modules/1 and the calls between the file's own modules are left
with their module variables unbound.  THE BENCH THEN DOES THE LINKER'S
JOB for one descriptor: it binds the module variable to a variable of
its own and that to the called module's object {MOD, its descriptor
cell}, so the field is TWO references from the module object, as in
the image (unify binds its first argument to its second on both
models; the test checks the depth).  Then a goal is started at the
call instruction itself, its arguments the bench's variables (as
lockstep_ext.py starts its sites).

The site, relative to the load address (with lockstep_link.py's first
part loaded before, as a probe of 2026-11-23 had it, every address is
217,509 higher: this site was 891692 there):
  enqueue_goal_external 2 at 674183, in the module at 673893
  (fep_filter), to the module at 586110 (filereq_filter), predicate
  filereq_filter/2 at 586151.  Since the merger timing change
  (2026-11-24) the loader's heap is laid out otherwise: the same call
  (opcode 66h, the same modules) is at 676409, to the module at
  587874, predicate at 587915 (SITE re-pinned from the check's own
  report; the trace pin below with it).
It is found on the loaded memory by the probe's method (a call whose
descriptor has a cache field of 0, an unbound module variable and a
key another loaded module's table holds), the first enqueue_goal_
external.  The goal started there makes the goal of the target, then
goes on with the caller's clause on the bench's registers and fails
(E fail, both models); a second run takes the goal the call made,
whose first instruction must be the target; it runs to a wait_vector_4
and suspends.  The file's five execute_external sites of this kind
were tried on the reference and are NOT used: each reaches its target
and then stops at an instruction not modelled (an external call into
a module the file does not hold; the general wait_vector).

Oracle, independent of the entry table the models walk: the target is
the called module's address plus the predicate's code offset as
asm/unlsav.py reads it from the FILE's index table (lockstep_modc.
modules: filereq_filter/2 at 41), the loaded modules taken to lie in
the file's order (an assumption; checked only in that the key's arity
picks exactly one predicate of that module).

Run time: 7,421,731 trace lines; the reference alone plays them in
about 25 s; bsv/run_pimm_lockstep.sh xmod took 3 min 40 s on this
machine, the build included, with a suite running beside it
(2026-11-23).

Observed fault injections into the Bluespec (bsv/PimmHBox.bsv, rule
xTab, where the field's chain is followed), each run alone
(bsv/run_pimm_lockstep.sh xmod, then ext) and restored from a copy,
2026-11-23:
  the reverse of a35c9a3f: the field    xmod: the site, line 14: the
    must be the image's form (a REF     call refused (E unimp).
    to the module table's cell, the     lockstep_ext.py PASSES: only
    descriptor cell after it)           this test catches it
  one reference step only: a REF met    xmod: the load, line 139 (the
    in xTab is a miss, no loop          IPL's own calls through the
                                        image's module table); ext:
                                        its first call, line 38
NOT caught here: a dereference limited to the image's depth (one REF
met in xTab, then a miss): the bench's chain is no deeper than the
image's;
the field's MRB; a cache field that is not 0 (refused, never met).

Re-pinned for the merger timing change (2026-11-24, docs/
pimm_semantics.md merge: a woken goal of merge_in goes on the
merger's list, taken before the ready queue), 7421731 -> 7431633
trace lines, both models identical and every check passing (injection line numbers above, if any, are as observed before it).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_link as link  # noqa: E402
import lockstep_modc as modc  # noqa: E402

PINNED = dict(parts=2, lines=7431633)
FILE = 'pimm_patch_mkdir360E.sav'
SITE = (676409, 0x66, 587874, 587915)   # pc, opcode, called module, target
DEPTH = 2                   # references from the module field to {MOD, ..}


def sx(v):
    return v - 0x10000 if v & 0x8000 else v


def loaded(m):
    """The module objects' descriptor cells above the image, ascending."""
    return sorted(a for a, c in m.mem.items()
                  if a >= m.load + 0x8000 and c[0] == pimm.CDESC and c[1] >> 24 == 6)


def sites(m, mods):
    """(pc, opcode, descriptor, called module, its target) for each call
    between two loaded modules with an unbound module variable; the
    target here from the models' own table walk (m.entry), only to find
    the sites: the oracle is target()."""
    out = []
    for a in mods:
        n, gc = m.mem[a][1] & 0xffffff, m.mem[a + 1][1]
        for pc in range(a + 2 + gc, a + n + 1):
            c = m.mem.get(pc)
            if not (c and c[0] == 0x23 and c[1] >> 24 in (0x62, 0x66)):
                continue
            e = pc + 2 + sx(c[1] & 0xffff)
            if not a + 2 <= e < a + 2 + gc:
                continue
            if m.mem[e] != (pimm.INT, 0) or m.mem[e + 1][0] & ~1 != pimm.REF:
                continue
            if not m.unbound(m.deref(m.mem[e + 1])):
                continue
            for b in mods:
                if b != a and m.entry(b, m.mem[e + 2]) is not None:
                    out.append((pc, c[1] >> 24, e, b, m.entry(b, m.mem[e + 2])))
    return out


def target(m, mods, b, key):
    """The oracle: module b's address plus the code offset of the
    predicate of the key's arity, as unlsav reads the file."""
    fm = modc.modules(FILE)
    assert len(fm) == len(mods)
    preds = fm[mods.index(b)]['preds']
    arity = key[1] >> 24
    hits = [off for _name, ar, off in preds if ar == arity]
    assert len(hits) == 1, (b, preds, arity)
    return b + hits[0]


def depth(m, w):
    n = 0
    while w[0] & ~1 == pimm.REF:
        w = m.mem[w[1]]
        n += 1
    return n, w


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    link.one(s, im, names, 'load', [FILE])
    m = s.live()
    mods = loaded(m)
    pc, op, e, b, _t = [x for x in sites(m, mods) if x[1] == 0x66][0]
    n = m.cells[pc - m.load][1] >> 16 & 255
    s.label('enqueue_goal_external at %d to the module at %d' % (pc - m.load, b - m.load))
    var = m.deref(m.mem[e + 1])
    s.setslot(0, (pimm.REF, var[1]))
    # the linker's job, done by the bench, through a variable of its own
    s.newvar(1)
    s.unify(0, 1)
    s.unifyc(1, (pimm.MOD, b))
    # the goal at the call, the call's arguments the bench's variables
    for i in range(n):
        s.newvar(2 + i)
        s.arg(i + 1, 2 + i)
    s.spawn(pc - m.load, 0)
    s.run()                 # the call, then the caller's clause fails
    s.run()                 # the goal it enqueued
    m = s.live()
    s.chosen = (pc, op, e, b, target(m, mods, b, m.mem[e + 2]), depth(m, m.mem[e + 1]))
    return s


def check(s, m, parts):
    bad = []
    pc, op, _e, b, t, (d, w) = s.chosen
    if (pc - m.load, op, b - m.load, t - m.load) != SITE:
        bad.append(('site', (pc - m.load, op, b - m.load, t - m.load), SITE))
    if (d, w) != (DEPTH, (pimm.MOD, b)):
        bad.append(('module field', d, w))
    lines = [ln for k, v in parts.items() if k != 'load' for ln in v]
    # the goal at the call is taken, then, the caller's clause having
    # failed, the goal the call made, whose first instruction must be
    # the target: the first I line after each G line
    taken = []
    for k, ln in enumerate(lines):
        if ln[0] == 'G':
            taken += [nx.split()[1] for nx in lines[k + 1:] if nx[0] == 'I'][:1]
    if 'E fail' not in lines:
        bad.append(('the caller did not fail',))
    if taken != [str(pc - m.load), str(t - m.load)]:
        bad.append(('the goals taken begin at', taken, t - m.load))
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
            if what != 'load':
                kept[what] = list(lines)
            yield what, lines
    s.play = keeping
    if '--reference' in argv:
        n = 0
        for what, lines in s.play():
            n += len(lines)
            if what == 'load':
                lines.clear()
        bad = check(s, s.machine, dict([('load', [])] + list(kept.items())))
        print(bad, n, [(k, len(v)) for k, v in kept.items()])
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep xmod', PINNED)
    if not ok:
        return 1
    bad = check(s, m, dict([('load', [])] + list(kept.items())))
    if bad:
        print('pimm lockstep xmod: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep xmod: PASS (an external call between two modules the IPL loaded, on '
          'the Bluespec core: %d trace lines identical to the reference model; the file %s '
          'loaded by ipl_loader:load/4, the bench binding a module variable as the linker '
          'would, two references deep; the call reaches the predicate where the file\'s '
          'index table puts it)' % (s.counts['lines'], FILE))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
