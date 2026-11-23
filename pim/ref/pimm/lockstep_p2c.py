#!/usr/bin/env python3
"""Lockstep: predicate_to_code and the guard code.

    python3 ref/pimm/lockstep_p2c.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_p2c.py compare

predicate_to_code(Module, Name, Arity, ^Code), 22:F3: "Unifies a code
denoting module Module, predicate name Name and argument count Arity
with Code.  If a corresponding predicate is absent in the module ...
unifies a 3-element vector {Module, Name, Arity}" (PIMOS manual,
e-builtin.tex).  Module is a module OBJECT here (PDSS takes an atom
and answers [] when absent: not this machine).  The IPL asks it for
pim:go/4 after a normal link (ipl_loader:check_module/7) and for its
own boot0/0 (ipl:boot/0).

Guard code(X, ^Arity, ^Module, ^Position), 23:FA: succeeds on a code,
"Fail: X anything other than a code" (the same manual).  The IPL's
check_code/5 uses code(A, _, _, _) and never reads the outputs.

A code object is {COD (26h), the address of the predicate's first
instruction}.  The tag is from debugger/inspector/tagtbl.kl1; the
TARGET IS ASSUMED for PIM/m.  For it: the manual's code_to_predicate
reads "<Code address - 3>", the INT cell before a predicate head if
the code is the first instruction; the image header's start address
is two cells after a predicate head, and equals the header's module
address (ipl's descriptor cell) + the Position this guard gives for
boot/0 (checked here).  The image holds no cell of tag 26h to settle
it.  COD and MOD (27h) differ in the low bit only, which is no MRB
for tags from 20h: both models compare the whole tag.

The predicate is found through the module's entry table by one
lookup shared with execute_external and enqueue_goal_external
(pimm.Machine.entry; PimmHBox entry/external).

Four parts, on a bare machine (the image's own twenty modules):
  every predicate  predicate_to_code, through its stub, for each of
                   the image's 349 predicates: a code for the 59 in
                   an entry table, the vector for the 290 others.
                   Which are public is found by walking every slot
                   and pair of each table, not by key.
  the guard        four codes, each put in a vector and taken from it
                   by a marked reference, given to check_code/5: the
                   answer normal(B, D, C, Code) with the code's tag
                   still 26h; the guard's three outputs read from the
                   trace's R lines: the arity, {MOD, the module's
                   descriptor cell}, the code's offset from that cell.
  not a code       check_code/5 on a module object, on the vector of
                   a missing predicate (boot/3) and on an integer:
                   abnormal("No PIMOS Top Predicate : pim:go/4"), and
                   the guard writes no register.
  waiting          the module unbound: the built-in waits and answers
                   when it is bound; the guard waits for the code.

Observed fault injections into the Bluespec, 2026-11-23, restored:
  code guard ignores the low tag bit         p2c: not a code, line 55
  entry table one cell further (shared)      ext: part 0, line 38
  key without the arity added to the atom    p2c: every predicate, 50
  absent: the arity in the name's place      p2c: every predicate, 21
  guard: Position one short                  p2c: the guard, line 55
  guard: Module given the COD tag            p2c: the guard, line 54
  code object points at the predicate head   p2c: every predicate, 50
NOT caught: "predicate_to_code accepts a code for the module" (no
test gives it one; both models refuse anything but a module there).
The shared-lookup injection stops at the ext test, which comes
first; the run does not go on to show this test failing too.

Not run: a module the IPL loaded (bsv/run_pimm_longrun.sh does:
pim:go/4 after the whole list); an arity over 255, a name that is not
an atom (refused: the built-in's exception); code_to_predicate,
apply (not implemented).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=4, lines=10872, public=59, private=290)
I = lambda v: (pimm.INT, v)                        # noqa: E731
NO_PRED = 'No PIMOS Top Predicate : pim:go/4'


def public(im):
    """{(module, name/arity): first instruction} of every predicate in
    a module's entry table, by walking each table whole: every slot,
    every pair (not by key, as the machine looks one up)."""
    out = {}
    for m in im.mods:
        a = m['addr'] + 1                      # the descriptor cell
        table = a + 2 + im.cells[a + 1][1]
        mask = im.cells[table][1]
        targets = set()
        for s in range(table + 1, table + 2 + mask):
            st, sv = im.cells[s]
            if st == pimm.INT:
                for k in range(sv >> 16):
                    p = s + (sv & 0xffff) + 2 * k
                    targets.add(p + 1 + im.cells[p + 1][1])
        for name, _ln, addr in m['preds']:
            if addr in targets:
                out[(m['name'], name)] = addr
        assert len(targets) == sum(1 for _n, _l, ad in m['preds'] if ad in targets), m['name']
    return out


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    stub = pimm.Machine().stubs['predicate_to_code']['addr']
    check_code = pimm.predicate(im, 'ipl_loader', 'check_code/5')
    pub = public(im)
    s = driver.Script()
    want = dict(pub=pub, asked=[], names=names)

    def p2c(mod, name, arity, out):
        """predicate_to_code through its stub: slot `out` := Code."""
        if mod[0] == 'slot':
            s.arg(1, mod[1])
        else:
            s.argc(1, mod)
        s.argc(2, (pimm.ATOM, names[name]))
        s.argc(3, I(arity))
        s.newvar(out)
        s.arg(4, out)
        s.spawn(stub, 4)

    def modobj(m):
        return (pimm.MOD, im.load + m['addr'] + 1)

    # 1. every predicate of every image module whose name is an atom
    #    of the image: a code for a public one, the vector otherwise
    s.label('every predicate')
    for m in im.mods:
        for name, _ln, addr in m['preds']:
            n, ar = name.rsplit('/', 1)
            if n not in names:
                continue
            p2c(modobj(m), n, int(ar), 0)
            s.run()
            s.out(0)
            want['asked'].append((m['name'], name, addr, modobj(m)))

    # 2. the code through marked paths, then the guard: check_code(A,
    #    B, C, D, E) :- wait(A), code(A, _, _, _) | E = normal(B, D, C, A)
    s.label('the guard')
    guarded = [('ipl', 'boot/0'), ('ipl_loader', 'load/4'), ('top', 'go/4'),
               ('ipl_file_decoder', 'decode/8')]
    for mod, name in guarded:
        m = [x for x in im.mods if x['name'] == mod][0]
        n, ar = name.rsplit('/', 1)
        p2c(modobj(m), n, int(ar), 0)
        s.run()
        s.vector(1, 2, [('slot', 0)])              # the code as a marked vector's element
        s.newvar(5)
        s.arg(1, 2)                                # the element's variable, MRB on
        for a in (2, 3, 4):
            s.argc(a, I(a))
        s.arg(5, 5)
        s.spawn(check_code, 5)
        s.run()
        s.out(5)
    want['guarded'] = guarded

    # 3. not a code: a module object, the vector of a missing
    #    predicate, an integer: "No PIMOS Top Predicate"
    s.label('not a code')
    m = [x for x in im.mods if x['name'] == 'ipl'][0]
    p2c(modobj(m), 'boot', 3, 0)                   # boot/0 is there, boot/3 is not
    s.run()
    s.out(0)
    for what in (modobj(m), ('slot', 0), I(7)):
        s.newvar(5)
        if what[0] == 'slot':
            s.arg(1, what[1])
        else:
            s.argc(1, what)
        for a in (2, 3, 4):
            s.argc(a, I(a))
        s.arg(5, 5)
        s.spawn(check_code, 5)
        s.run()
        s.out(5)
    want['absent'] = (modobj(m), 'boot', 3)

    # 4. the module not yet known: the built-in waits, then answers
    s.label('waiting')
    s.newvar(1)
    p2c(('slot', 1), 'boot', 0, 0)
    s.run()
    s.out(0)
    s.unifyc(1, modobj(m))
    s.run()
    s.out(0)
    # the guard waits for the code too
    s.newvar(1)
    s.newvar(5)
    s.arg(1, 1)
    for a in (2, 3, 4):
        s.argc(a, I(a))
    s.arg(5, 5)
    s.spawn(check_code, 5)
    s.run()
    s.out(5)
    s.unify(1, 0)
    s.run()
    s.out(5)
    want['boot'] = pimm.predicate(im, 'ipl', 'boot/0')
    return s, want


def guard_outputs(lines, im):
    """The three registers the guard code writes, from the trace: the R
    lines that follow each taking of check_code's code instruction."""
    at = pimm.predicate(im, 'ipl_loader', 'check_code/5')
    while im.dis(at).split()[0] != 'code':
        at += 1
    out = []
    for i, ln in enumerate(lines):
        if ln.startswith('I %d ' % at):
            rs = []
            for nxt in lines[i + 1:i + 4]:
                if nxt[0] != 'R':
                    break
                r, v = nxt.split()[1:]
                rs.append((int(r), int(v[:2], 16), int(v[2:], 16)))
            out.append(rs)
    return out


def check(s, m, want, parts):
    im, bad = m.im, []
    outs = {}
    for label, w in s.outs:
        outs.setdefault(label, []).append(w)
    # 1
    n_pub = n_priv = 0
    for (mod, name, addr, obj), w in zip(want['asked'], outs['every predicate']):
        n, ar = name.rsplit('/', 1)
        if (mod, name) in want['pub']:
            n_pub += 1
            if w != (pimm.COD, im.load + addr):
                bad.append((mod, name, w))
        else:
            n_priv += 1
            if m.unbound(w) or m.vsize(w) != 3 or [m.mem[m.vbase(w) + i] for i in range(3)] != [
                    obj, (pimm.ATOM, want['names'][n]), I(int(ar))]:
                bad.append((mod, name, 'not the vector', w))
    # 2: normal(2, 4, 3, Code), the code's tag whole; the guard's outputs
    gouts = guard_outputs(parts['the guard'], im)
    for (mod, name), w, rs in zip(want['guarded'], outs['the guard'], gouts):
        mrec = [x for x in im.mods if x['name'] == mod][0]
        addr = pimm.predicate(im, mod, name)
        desc = im.load + mrec['addr'] + 1
        el = None if m.unbound(w) else [m.deref(m.mem[m.vbase(w) + i]) for i in range(m.vsize(w) or 0)]
        if el is None or el[1:] != [I(2), I(4), I(3), (pimm.COD, im.load + addr)]:
            bad.append((mod, name, 'check_code', el))
        exp = [(5, pimm.INT, int(name.rsplit('/', 1)[1])), (6, pimm.MOD, desc),
               (7, pimm.INT, im.load + addr - desc)]
        if rs != exp:
            bad.append((mod, name, 'guard outputs', rs, exp))
    if len(gouts) != len(want['guarded']):
        bad.append(('guard taken', len(gouts)))
    # 3
    o = outs['not a code']
    obj, n, ar = want['absent']
    if m.vsize(o[0]) != 3 or [m.mem[m.vbase(o[0]) + i] for i in range(3)] != [
            obj, (pimm.ATOM, want['names'][n]), I(ar)]:
        bad.append(('absent', o[0]))
    for w in o[1:]:
        t = None if m.unbound(w) else m.term(w)
        if t != ('abnormal', (8, [ord(c) for c in NO_PRED])):
            bad.append(('not a code', t))
    if any(rs for rs in guard_outputs(parts['not a code'], im)):
        bad.append(('the guard wrote a register on a non-code',))
    # 4
    o = outs['waiting']
    code = (pimm.COD, im.load + want['boot'])
    if not m.unbound(o[0]) or o[1] != code or not m.unbound(o[2]) or m.unbound(o[3]):
        bad.append(('waiting', o))
    # the image header: start = the module's descriptor cell + Position
    if im.got['start'] != im.load + want['boot'] or im.got['module'] != im.load + [
            x for x in im.mods if x['name'] == 'ipl'][0]['addr'] + 1:
        bad.append(('image header', im.got['start'], im.got['module']))
    if m.nsusp:
        bad.append(('%d goals left waiting' % m.nsusp,))
    return bad, n_pub, n_priv


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        parts = dict(s.play())
        print(check(s, s.machine, want, parts), sum(len(v) for v in parts.values()))
        return 0
    kept = {}
    play = s.play

    def keeping():
        for what, lines in play():
            kept[what] = lines
            yield what, lines
    s.play = keeping
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep p2c',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, n_pub, n_priv = check(s, m, want, kept)
    if bad or (n_pub, n_priv) != (PINNED['public'], PINNED['private']):
        print('pimm lockstep p2c: FAIL %d public, %d not, %r' % (n_pub, n_priv, bad[:3]))
        return 1
    print('pimm lockstep p2c: PASS (predicate_to_code and the guard code on the Bluespec core, '
          '%d trace lines identical to the reference model: %d public predicates of the image '
          'found where its entry tables have them, %d others answered with the vector; the '
          "guard's outputs as the image has them; a module or a vector is not a code)"
          % (s.counts['lines'], n_pub, n_priv))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
