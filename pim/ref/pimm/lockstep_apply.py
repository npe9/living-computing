#!/usr/bin/env python3
"""Lockstep: apply(Code, Args).

    python3 ref/pimm/lockstep_apply.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_apply.py compare

apply(Code, Args), 22:F1: "Calls a predicate corresponding to Code
with argument environment Args.  Suspend: Code or Args
uninstantiated" (PIMOS manual, e-builtin.tex).  It makes a ready goal
of the code with the vector's elements as arguments, as PDSS does
(emulator/blt_system.c blt_b_apply: each element dereferenced, its
MRB set if the vector's is, the goal enqueued).  The IPL's use:
top:go_pimos1(normal(A, B, C, D), E) :- apply(D, {E, A, B, C}), D the
code of pim:go/4.

Five parts, on a bare machine:
  convert       the code predicate_to_code gives for
                jis_to_ascii:convert/2, applied to {"abc" in JIS, A}:
                A is the 8-bit string abc.
  hash          a code the bench makes for ipl_pool:hash/3 (not
                public), applied to {-7, H, _}: H = 7.
  the IPL       top:go_pimos1/2 itself, with D the code of
                ipl_loader:load/4 and E = []: the IPL's own apply
                site, on a vector its own clause builds, runs the
                loader on an empty list: the console gets "IPL
                loading", "Link Modules ...", and the answer is
                abnormal("No PIMOS Top Module").
  one argument  ipl:close/1: its argument becomes [].
  waiting       the code unbound, then the vector unbound: apply
                waits and runs when each is bound.
A code in the HEAP (a module the IPL loaded) is applied in
lockstep_run.py.

Observed fault injections into the Bluespec, 2026-11-23, restored:
  the second element read for every argument  apply: the IPL, line 80
  element MRB always off                      apply: convert, line 48
  the goal one argument short                 apply: convert, line 52
NOT caught:
  element MRB always on       every vector here has its MRB on when
                              apply takes it (the bench's slots, and
                              go_pimos1's vector by put_vector +
                              set_value), so the rule "on if the
                              vector's is" is only run with it on
  the count not checked against the predicate head
  a module accepted as the code
The last two are refusals (the manual's exceptions), and a refusal
stops the reference model: the lockstep driver cannot play one.

Not run, and refused by both models: the empty vector (the image's
predicates of no argument are ipl:boot/0, boot0/0 and shoen:noop/0,
none of which can run yet; ipl:boot/0 gives {} to shoen:execute/4,
not to apply); a vector of seven or more; the manual's exceptions.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_cons as cons  # noqa: E402

PINNED = dict(parts=5, lines=138935)
I = lambda v: (pimm.INT, v)                        # noqa: E731
NO_MODULE = 'No PIMOS Top Module'


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    stubs = pimm.Machine().stubs

    def modobj(name):
        return (pimm.MOD, im.load + [x for x in im.mods if x['name'] == name][0]['addr'] + 1)

    def code(mod, pred):
        """A code object made by the bench (for a predicate that is not
        public, which predicate_to_code would not give)."""
        return (pimm.COD, im.load + pimm.predicate(im, mod, pred))

    s = driver.Script()

    def p2c(mod, name, arity, out):
        s.argc(1, modobj(mod))
        s.argc(2, A(name))
        s.argc(3, I(arity))
        s.newvar(out)
        s.arg(4, out)
        s.spawn(stubs['predicate_to_code']['addr'], 4)
        s.run()

    def apply(code_slot, args_slot):
        s.arg(1, code_slot)
        s.arg(2, args_slot)
        s.spawn(stubs['apply']['addr'], 2)

    # 1. the code predicate_to_code gives: jis_to_ascii:convert(Jis, ^Ascii)
    s.label('convert')
    p2c('jis_to_ascii', 'convert', 2, 0)
    s.string(1, 16, cons.jis('abc'))
    s.vector(2, 4, [('slot', 1), None])            # the answer's variable in 5
    apply(0, 2)
    s.run()
    s.out(5)

    # 2. three arguments: ipl_pool:hash(X, ^H, ^NewX), a code of the bench's
    s.label('hash')
    s.setslot(0, code('ipl_pool', 'hash/3'))
    s.vector(2, 4, [I(-7 & 0xffffffff), None, None])            # H in 5
    apply(0, 2)
    s.run()
    s.out(5)
    s.out(6)

    # 3. the IPL's own apply: top:go_pimos1(normal(A, B, C, D), E) :-
    #    apply(D, {E, A, B, C}), with D the code of ipl_loader:load/4
    #    and E an empty file list: load([], Requests, Close, Loaded)
    s.label('the IPL')
    p2c('ipl_loader', 'load', 4, 0)
    s.newvar(7)
    s.newvar(8)
    s.newvar(9)
    s.vector(1, 10, [A('normal'), ('slot', 7), ('slot', 8), ('slot', 9), ('slot', 0)])
    s.arg(1, 1)
    s.argc(2, (pimm.ATOM, 0))
    s.spawn(pimm.predicate(im, 'top', 'go_pimos1/2'), 2)
    s.run()
    s.out(9)
    s.out(7)
    s.out(8)

    # 4. one argument: ipl:close(A) :- A = [].
    s.label('one argument')
    s.setslot(0, code('ipl', 'close/1'))           # close(A) :- A = [].
    s.vector(2, 4, [None])
    apply(0, 2)
    s.run()
    s.out(4)

    # 5. it waits for the code, and for the vector
    s.label('waiting')
    s.newvar(0)
    s.vector(2, 4, [I(5), None, None])             # H in 5
    apply(0, 2)
    s.run()
    s.out(5)
    s.unifyc(0, code('ipl_pool', 'hash/3'))
    s.run()
    s.out(5)
    s.setslot(0, code('ipl_pool', 'hash/3'))
    s.newvar(3)
    apply(0, 3)
    s.run()
    s.vector(2, 4, [I(9), None, None])             # H in 5
    s.unify(3, 2)
    s.run()
    s.out(5)
    return s


def check(s, m, parts):
    bad = []
    outs = {}
    for label, w in s.outs:
        outs.setdefault(label, []).append(None if m.unbound(w) else m.term(w))
    exp = {'convert': [(8, [ord(c) for c in 'abc'])],
           'hash': [7, -7],
           'the IPL': [('abnormal', (8, [ord(c) for c in NO_MODULE])), None, None],
           'one argument': [[]],
           'waiting': [None, 5, 9]}
    for k, v in exp.items():
        if outs.get(k) != v:
            bad.append((k, outs.get(k), v))
    got = cons.console(parts['the IPL'])
    if got != ['IPL loading', 'Link Modules ...']:
        bad.append(('console', got))
    stub = 'I %d ' % m.stubs['apply']['addr']
    if not any(ln.startswith(stub) for ln in parts['waiting']):
        bad.append(('apply did not wait',))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        parts = dict(s.play())
        print(check(s, s.machine, parts), sum(len(v) for v in parts.values()))
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep apply',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad = check(s, m, kept)
    if bad:
        print('pimm lockstep apply: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep apply: PASS (apply on the Bluespec core, %d trace lines identical to '
          "the reference model: codes of two, three, four and one arguments run with a "
          "vector's elements, the IPL's own apply runs its loader on an empty list (%r); it "
          'waits for the code and for the vector)' % (s.counts['lines'], NO_MODULE))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
