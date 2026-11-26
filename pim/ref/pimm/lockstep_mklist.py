#!/usr/bin/env python3
"""Lockstep: mark_element(List, Position) on a list cell (R9).

    python3 ref/pimm/lockstep_mklist.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_mklist.py compare
    python3 ref/pimm/lockstep_mklist.py --reference       the reference alone

mark_element, 23:1C r_r, on a LIST word: Position 0 sets the MRB of the
car's cell, 1 that of the cdr's, in the list.  HELD-SOURCE: PIMOS's own
compiler emits `put_constant(0, Rpos), mark_element(Rlist, Rpos)` for
a car(List) the body refers to and the same with 1 for a cdr(List)
(library/compiler/body.kl1:437-460, generate_add_ref_); that the
list's two cells are addressed as a short vector's (its address +
Position, no header) is INFERENCE (docs/pimm_semantics.md, the row).
Met compiling MGTP/G's axioms (R9, 2026-11-26: once in the whole
6-Queens run, Position 0, the car already marked, so no write); the
compiler's code that runs it is loaded from a .sav at run time, not in
the IPL image (whose 13 mark_element sites are all on vectors), so this
bench makes its own code: three cells of a vector, OURS, a predicate
head of arity 2, a cell, `mark_element 0,1` and `proceed`, applied to
{List, Position} (lockstep_apply.py's way, its part `no argument`).

The lists' cells are the bench's variables bound to list words with
the MRB off, {LIST, a} (driver SLOT), pointing at a list the bench
made, so that marking one changes the cell.  Parts, the expected cells
read from the reference's memory after the run (check):
  car       Position 0: the car's cell gets the MRB, the cdr's does not
  cdr       Position 1: the cdr's cell gets it, the car's does not
  marked    Position 0 on a car whose word is already marked: no write
            in the part (the rule "written only if that changes it",
            pimm.py taken)
  unbound   Position 1 on an unbound cdr: the cell is left, no write
  refused   Position 2 on a list: refused by both models (last, no OUT
            after it)

Observed fault injections (2026-11-26):
  reference (pimm.py i_mark_element patched, --reference; car, none
  and pos2 are r9_mgtp_probe.py's R9_INJECT, always a one-off patch):
    car     (the car marked whatever the Position): fails cdr, unbound
    none    (nothing marked on a list): fails car, cdr
    pos2    (Position 2 taken too): fails refused
    always  (written even when already marked): fails marked, unbound
  core (Bluespec, copies of bsv/ in scratch, driver bench rebuilt):
    (each: the reference's line, then the core's)
    car     (PimmStages passes Position 0 for a list): FAIL at part 2
            (cdr), line 36, `M 32791 05e0008004` / `M 32790 05e0008004`
    none    (VBox no-op on a list): FAIL at part 1 (car), line 36,
            `M 32774 05e0008004` / `I 32771 2360000000`
    pos2    (VBox n <= 3 for a list): FAIL at part 5 (the refusal),
            line 36, `E unimp` / `I 32771 2360000000`
  each reverted; the tree's git diff carried none of them.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=6, lines=210)
I = lambda v: (pimm.INT, v)                        # noqa: E731
MARK = (0x23, 0x1c << 24 | 0 << 16 | 1 << 8)       # mark_element 0,1
PROCEED = (0x23, 0x60 << 24)


def script():
    stubs = pimm.Machine().stubs
    s = driver.Script()
    lists = {}

    # the code: {PREDH arity 2, a cell, mark_element 0,1, proceed}; the
    # code object is its third cell (lockstep_apply.py, no argument)
    s.vector(15, 4, [(pimm.PREDH, 2 << 24), I(0), MARK, PROCEED])
    m = s.live()
    code = (pimm.COD, s.live_slot[15][1] + 2)
    # a list for the cells to point at: [1|2]
    s.cons(14, 4, I(1), I(2))
    m = s.live()
    target = s.live_slot[14][1]
    off = (pimm.LIST, target)                      # a list word, MRB off
    on = (pimm.LIST + 1, target)

    def part(label, car, cdr, pos):
        s.label(label)
        s.cons(2, 4, car, cdr)
        m = s.live()
        lists[label] = s.live_slot[2][1] - m.load
        s.vector(3, 6, [('slot', 2), I(pos)])
        s.setslot(0, code)
        s.arg(1, 0)
        s.arg(2, 3)
        s.spawn(stubs['apply']['addr'], 2)
        s.run()
        s.out(2)

    part('car', off, off, 0)
    part('cdr', off, off, 1)
    part('marked', on, off, 0)
    part('unbound', off, None, 1)
    s.label('refused')
    s.cons(2, 4, off, off)
    s.vector(3, 6, [('slot', 2), I(2)])
    s.setslot(0, code)
    s.arg(1, 0)
    s.arg(2, 3)
    s.spawn(stubs['apply']['addr'], 2)
    s.run()
    s.lists = lists
    s.code = code
    return s


def check(s, m, parts):
    """The cells of each part's list after the run, against the rule;
    and what the part writes to them once mark_element has run: one
    write in car and cdr, none in marked and unbound."""
    bad = []
    want = {'car': (True, False), 'cdr': (False, True), 'marked': (True, False),
            'unbound': (False, None)}
    pc = 'I %d ' % (s.code[1] - m.load)
    for label, (car, cdr) in want.items():
        a = m.load + s.lists[label]
        for k, exp in enumerate((car, cdr)):
            c = m.mem[a + k]
            if exp is None:
                if c[0] & ~1 not in (pimm.UNDF, pimm.HOOK):
                    bad.append((label, k, 'not left unbound', c))
            elif (c[0] & ~1 != pimm.LIST) or bool(c[0] & 1) != exp:
                bad.append((label, k, c, 'MRB %s wanted' % ('on' if exp else 'off')))
        tr = parts.get(label, [])
        at = [i for i, ln in enumerate(tr) if ln.startswith(pc)]
        if len(at) != 1:
            bad.append((label, 'mark_element run %d times' % len(at)))
            continue
        a -= m.load
        hits = [ln for ln in tr[at[0]:] if ln.split()[:2] in (['M', str(a)], ['M', str(a + 1)])]
        if len(hits) != (1 if label in ('car', 'cdr') else 0):
            bad.append((label, 'writes after mark_element', hits))
    if not getattr(s, 'refused', None):
        bad.append(('refused', 'not refused'))
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
    parts = {}

    def kept():
        for label, tr in refusing(s, orig):
            parts[label] = tr
            yield label, tr
    s.play = kept
    if '--reference' in argv:
        n = sum(len(v) for _k, v in s.play())
        bad = check(s, s.machine, parts)
        print(bad, n, len(parts), getattr(s, 'refused', None))
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep mklist', PINNED)
    if not ok:
        return 1
    bad = check(s, m, parts)
    if bad:
        print('pimm lockstep mklist: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep mklist: PASS (mark_element on a list cell on the Bluespec core, %d '
          'parts, %d trace lines identical to the reference model: Position 0 marks the car '
          'and 1 the cdr, in the list; an already marked car and an unbound cdr not written; '
          'Position 2 refused on both)' % (s.counts['parts'], s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
