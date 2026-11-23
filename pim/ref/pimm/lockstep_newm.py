#!/usr/bin/env python3
"""Lockstep: the IPL builds whole module objects.

    python3 ref/pimm/lockstep_newm.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_newm.py compare

ipl_module:load/4 (object code; its source's later form is
library/loader/loader.kl1) on real modules of pimm_kernel360E.sav, each
first decoded from the file's words by ipl_file_decoder:load_module/7:
a vector of the module's size is made, the GC area, the predicate entry
table and the code area are written into it, and new_module turns it
into a module object, which comes out in [module(Package, Name, Module,
ExternalModules)|_] with the status normal.

new_module (22:D6) is new on both models.  loader.kl1: "First Element
is for CDESC created by new_module", and the caller puts 06000000h \\/
(size - 1) there.  The result has the shape of the IPL image's own 20
modules: {MOD, a} -> {CDESC, 06 << 24 | n} and n cells.  Whether the
machine converts the vector in place is not known; both models copy.
An element may be a reference to a variable (the loader leaves one
where another module will be); an unbound cell in the vector itself,
and an element 0 that is not that integer, are refused.

The oracle, per built object (every cell is accounted for):
  cell 1          the GC area's size: 2 + 1 per constant, 5 per
                  external call, 2 per module reference, of the
                  elements asm/unlsav.py reads from the file
  cell 2, 3       the module's atom; load_module/7's second argument,
                  which is therefore the package (the image has the
                  package atom there)
  constants       the term asm/unlsav.py reads from the file
  external call   {0, reference to a variable, key, module atom, 0};
                  the key is arity << 24 | (atom + arity) & FFFFFFh,
                  as in the image's tables; the variable is the one
                  in the output's ext_mod(Module, {Variable, Pred,
                  Arity}).  FIVE cells, where the image's own modules
                  have four (TM-662): the fifth is the package's
                  place in loader.kl1
  module ref.     {reference to the ext_mod variable, 0}
  entry table     every predicate is found by the rule the image's
                  tables follow, at the place the file gives, and
                  the predicate's header two cells before holds its
                  own place and the arity; empty slots are 0
  code            every item unlsav reads, in order: an integer, an
                  atom, an instruction cell with its tag and value, an
                  instruction with an atom operand (the atom's number
                  in the low 24 bits); a hash_on_constant table has
                  its size in slots and two cells per entry, and every
                  key is found by the model's hash_on_constant rule
                  (the image's layout) at the label the file gives

Not checked: that code in a built module RUNS (the models fetch code
from the image, not from the heap).  Modules of more than about 2700
file words do not fit: every set_vector_element copies the vector.
One hash table is built (stdio2filter's, 17 keys, all atoms); integer
keys are not run.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  new_module returns the vector         the first module: R 1 a vector
  element 0 left an integer            the same: the descriptor cell
  copies one cell short                the same: the last cell missing
  copies from one cell on              the same: the second cell
  refuses a reference element          module2pool, the first with an
                                       external call: E unimp
  the result into the vector register  the first module: R 2 for R 1

Not caught: new_module accepting any element 0 (the refusals are not
run: no vector here has another, or an unbound cell of its own).
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

PINNED = dict(parts=5, lines=326883, cells=1143)
MODULES = ('privileged2module', 'module2pool', 'pimos2version', 'task2std2abnormal',
           'stdio2filter')
PACKAGE = (pimm.ATOM, 0x1fffe)       # stands for the package atom


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    names = {name: n for n, name in im.sym.items()}
    mods = {m['name']: m for m in modc.modules()}
    tops = {a[0]: a[3] for a in gca.areas()}
    want = []
    for name in MODULES:
        mod = mods[name]
        s.label(name)
        for i in (0, 1, 2, 3, 4, 7):
            s.newvar(i)
        s.arg(1, 2)
        s.argc(2, PACKAGE)
        for a, sl in ((3, 0), (4, 1), (5, 7), (6, 3), (7, 4)):
            s.arg(a, sl)
        s.spawn(pimm.predicate(im, 'ipl_file_decoder', 'load_module/7'), 7)
        s.live()
        table = {k: deca.number(k, v) for k, v in mod['atoms_before'].items()}
        at, atq, feed = deca.serve(s, s.live_slot[0], s.live_slot[7], list(mod['whole']),
                                   table, names, [])
        assert not feed
        for i in (9, 10, 11):
            s.newvar(i)
        s.arg(1, 2)
        s.arg(2, 9)
        s.arg(3, 10)
        s.arg(4, 11)
        s.spawn(pimm.predicate(im, 'ipl_module', 'load/4'), 4)
        s.run()
        for i in (2, 9, 10, 11):
            s.out(i)
        want.append((name, mod, tops[name]))
    return s, want


def number(a):
    return deca.number(a[0], a[1])


def check_object(m, mod, tops, out, tail, status):
    """The list of what is wrong with one built module, and its size."""
    if m.unbound(status) or m.term(status) != 'normal':
        return ['status'], 0
    lst = m.deref(out)
    if lst[0] & ~1 != pimm.LIST or m.deref(m.mem[lst[1] + 1]) != m.deref(tail):
        return ['the output is not [_|Tail]'], 0
    return check_record(m, mod, tops, m.deref(m.mem[lst[1]]))


def check_record(m, mod, tops, rec):
    """The same for a module(Package, Name, Module, ExternalModules)."""
    if m.vsize(rec) != 5:
        return ['the record'], 0
    rb = m.vbase(rec)
    f = [m.deref(m.mem[rb + i]) for i in range(5)]
    name_atom = (pimm.ATOM, deca.number(mod['name_id'], mod['name']))
    if [(t & ~1, v) for t, v in f[1:3]] != [PACKAGE, name_atom] or f[3][0] != pimm.MOD:
        return ['module(Package, Name, Module, _): %r' % (f,)], 0
    a = f[3][1]
    desc = m.mem[a]
    n = desc[1] & 0xffffff
    if desc[0] != pimm.CDESC or desc[1] >> 24 != 6:
        return ['descriptor %r' % (desc,)], 0
    cell = [m.mem[a + i] for i in range(n + 1)]
    plain = [(t & ~1 if t < 0x20 else t, v) for t, v in cell]
    bad = []
    # the external modules of the output: ext_mod(Name, {Var...})
    ext = []
    e = m.deref(f[4])
    while e[0] & ~1 == pimm.LIST:
        r = m.deref(m.mem[e[1]])
        eb = m.vbase(r)
        inner = m.deref(m.mem[eb + 2])
        # the variable may be the vector's own first cell
        ext.append((m.deref(m.mem[eb + 1]), m.deref((pimm.REF, m.vbase(inner)))[1],
                    m.vsize(inner)))
        e = m.deref(m.mem[e[1] + 1])
    # the GC area
    consts = gca.expected(tops, {})
    i, k = 4, 0
    if plain[2] != name_atom or plain[3] != PACKAGE:
        bad.append('name, package: %r' % (plain[2:4],))
    for j, top in enumerate(tops):
        if top[0] == 'extcall':
            key = top[3] << 24 | (number(top[2]) + top[3]) & 0xffffff
            modatom = (pimm.ATOM, number(top[1]))
            var = m.deref(cell[i + 1])
            unb, var = m.unbound(var), var[1]
            if not (plain[i] == (pimm.INT, 0) and unb
                    and plain[i + 2:i + 5] == [(pimm.ATOM, key), modatom, (pimm.INT, 0)]):
                bad.append('external call at %d: %r' % (i, plain[i:i + 5]))
            elif k >= len(ext) or \
                    (ext[k][0][0] & ~1, ext[k][0][1], ext[k][1], ext[k][2]) != modatom + (var, 3):
                bad.append('ext_mod %d: %r' % (k, ext[k:k + 1]))
            i, k = i + 5, k + 1
        elif top[0] == 'module' and len(top) == 3:
            var = m.deref(cell[i])
            unb, var = m.unbound(var), var[1]
            if not (unb and plain[i + 1] == (pimm.INT, 0)):
                bad.append('module reference at %d: %r' % (i, plain[i:i + 2]))
            elif k >= len(ext) or (ext[k][1], ext[k][2]) != (var, 1):
                bad.append('ext_mod %d: %r' % (k, ext[k:k + 1]))
            i, k = i + 2, k + 1
        else:
            got = m.term(m.deref(cell[i]))
            exp = consts[j]
            if isinstance(exp, tuple) and len(exp) == 2 and exp[0] == 'struct':
                exp = exp[1]
            if got != exp:
                bad.append('constant at %d: %r, not %r' % (i, str(got)[:60], str(exp)[:60]))
            i += 1
    if k != len(ext):
        bad.append('%d ext_mod, %d references' % (len(ext), k))
    gs = i - 2
    if plain[1] != (pimm.INT, gs):
        bad.append('GC size %r, not %d' % (plain[1], gs))
    # the predicate entry table, by the rule of the image's tables
    hs, preds = mod['hs'], mod['preds']
    pos = gs + 2
    used = {pos}
    if plain[pos] != (pimm.INT, hs - 1):
        bad.append('mask')
    code0 = pos + 1 + hs + 2 * len(preds)
    exp_code = modc.expected_code(mod)
    # where each file location is in the object
    where, j = {}, code0
    for it in mod['items']:
        where[it[1]] = j
        j += it[2] + 2 * it[3] if it[0] == 'table' else 1
    if j != n + 1:
        bad.append('size: the items end at %d, the object at %d' % (j, n + 1))
        return bad, n + 1
    for (pname, arity, loc), aid in zip(preds, mod['detail']['entry_ids']):
        key = arity << 24 | (deca.number(aid, mod['atoms'][aid]) + arity) & 0xffffff
        slot = pos + 1 + (key & (hs - 1))
        used.add(slot)
        st, sv = plain[slot]
        hit = None
        if st == pimm.INT:
            for q in range(sv >> 16):
                p = slot + (sv & 0xffff) + 2 * q
                if plain[p] == (pimm.ATOM, key):
                    hit = p + 1 + plain[p + 1][1]
                    used.update((p, p + 1))
        # the file's pointer is the place in the module, two cells
        # after the predicate's header, which holds its own place
        if hit != loc or cell[loc - 2] != (0x24, arity << 24 | loc - 2):
            bad.append('entry %s: %r, not %d' % (pname, hit, loc))
    for q in range(pos, code0):
        if q not in used and plain[q] != (pimm.INT, 0):
            bad.append('table cell %d is %r' % (q, plain[q]))
    # the code
    for it, e in zip(mod['items'], exp_code):
        j, kind = where[it[1]], it[0]
        if kind == 'int':
            ok = plain[j] == (pimm.INT, e & 0xffffffff)
        elif kind == 'inst':
            ok = cell[j] == (e[0], e[1] & 0xffffffff)
        elif kind == 'atomref':
            ok = plain[j] == (pimm.ATOM, 0 if e == [] else int(e[1:], 16))
        elif kind == 'atom':
            tag, op, at = e[1]
            ok = cell[j] == (tag, op << 24 | (0 if at == [] else int(at[1:], 16)))
        else:
            # a hash_on_constant table: the instruction is two cells back
            size, ent = it[2], it[3]
            mask = cell[j - 2][1] & 0xffff
            ok = mask == size - 1 and cell[j - 2][1] >> 24 == 0x2d
            seen = set()
            for key, lab in mod['detail']['code'][it[1]]:
                if key[0] == 'atom':
                    w = (pimm.ATOM, deca.number(key[1], key[2]))
                else:
                    w = (pimm.INT, key[1] & 0xffffffff)
                slot = j + (w[1] & mask)
                seen.add(slot)
                st, sv = plain[slot]
                hit = None
                if st == pimm.INT:
                    for q in range(sv >> 16):
                        p = slot + (sv & 0xffff) + 2 * q
                        if plain[p] == w:
                            hit = p + 2 + plain[p + 1][1]
                            seen.update((p, p + 1))
                if hit != lab:
                    ok = False
            for q in range(j, j + size + 2 * ent):
                if q not in seen and plain[q] != (pimm.ATOM, 0):
                    ok = False
        if not ok:
            bad.append('code %s at %d: %r' % (kind, j, cell[j]))
    return bad, n + 1


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad, cells = [], 0
    for name, mod, tops in want:
        decoded, out, tail, status = got[name][-4:]
        b, n = check_object(m, mod, tops, out, tail, status)
        cells += n
        bad += [(name, x) for x in b]
    return bad, cells


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep newm',
                           dict(parts=PINNED['parts'], lines=PINNED['lines']))
    if not ok:
        return 1
    bad, cells = check(s, m, want)
    if bad or cells != PINNED['cells']:
        print('pimm lockstep newm: FAIL %d cells, %r' % (cells, bad[:3]))
        return 1
    print('pimm lockstep newm: PASS (ipl_module:load/4 builds %d real modules of the kernel '
          'file as module objects on the Bluespec core, %d trace lines identical to the '
          'reference model: %d cells, each as the file and the layout of the image\'s own '
          'modules say: GC area, external-call descriptors, entry table, code, one hash '
          'table)' % (len(MODULES), s.counts['lines'], cells))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
