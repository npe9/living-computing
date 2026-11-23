#!/usr/bin/env python3
"""Lockstep: the IPL builds a module's predicate entry table.

    python3 ref/pimm/lockstep_ptab.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_ptab.py compare

ipl_module:set_pred_table/6, the part of the IPL's module builder
(ipl_module:load/4) that writes the table execute_external looks
predicates up in.  Roles read from the object code (asm/kl1decomp.py):

    set_pred_table(Vector, Position, HashSize, Entries, Vector1, Status)

Entries is the list ipl_file_decoder:decode_index_table/9 makes from a
real module (lockstep_modc.py); this test makes it the same way, from
the words of pimm_kernel360E.sav, and has the decoder make a vector of
zeros to build in (decode_0/7 on a written 0700 term).

Oracle: the table's layout as the IPL image itself has it.  That
layout was read from the image and holds for all 59 entries of its 20
modules (pimm.Machine.i_execute_external; those tables are the
linker's work, library/kbn).  Here the IPL's builder must produce the
same thing from a .sav module:

    Vector1[Position]           {INT, HashSize - 1}
    then HashSize slots         {INT, count << 16 | offset} or 0
    pairs                       {ATOM, arity << 24 | (atom + arity)}, {INT, off}
                                the off cell's index + off = the
                                predicate's location in the file

and the test looks every predicate of the module up by that rule, with
asm/unlsav.py's atoms, arities and locations; the pairs found must be
all the pairs there are, and every cell outside the table still 0.
Each module is built at Position 0 and at Position 5.

put_structured_constant is run by three clauses that refuse their
input and answer abnormal("..."): the string is a constant kept
outside the module, reached through a cell of the GC area (TM-662).
Oracle: the text, as the decompiler reads the constant from the image.

New here: tag_and_value, new_instruction, b_vector_element, the guard
add, wait_nil, wait_list, read_atom, switch_on_non_atom,
write_marked_value, set_marked_value, set_integer,
put_structured_constant, and collect_list / collect_vector (MRB
reclamation: no operation here, as collect_value).

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
All in the first table built unless said:
  tag_and_value: value in the tag register; the tag given for the
    value; stepping one cell
  new_instruction making an integer; tag and value swapped
  b_vector_element: the element into the vector's register
  the guard add subtracting
  wait_list leaving the structure pointer
  read_atom not advancing
  set_integer setting the next argument
  collect_list, collect_vector stopping
  switch_on_non_atom inverted          lockstep_ext.py, the call at 1851
  put_structured_constant writing      decode_GC_area/7 refuses: R 254
    r[y]; reading one cell on          written; another constant loaded

Not caught:
  - the guard add never failing on overflow (no sum here overflows);
  - wait_nil and read_atom accepting any atom (no clause here is
    offered a different atom at those places);
  - set_integer zero-extending (no negative operand here).
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

PINNED = dict(parts=9, lines=106289, entries=40)
MODULES = ('system2defined2servers', 'task2std2abnormal', 'shoen')
POSITIONS = (0, 5)
SPARE = 4
# module, predicate, {argument: cell} ('other': an atom that is not
# `normal`), the status argument, and the text as asm/kl1decomp.py
# shows the constant
REFUSALS = (
    ('ipl_file_decoder', 'decode_GC_area/7', {1: 'other'}, 7, 'Illegal GC Area'),
    ('ipl_file_decoder', 'decode_index_table/9', {1: 'other'}, 9, 'Illegal Hash Entry'),
    ('ipl_module', 'set_pred_table/6', {4: (pimm.ATOM, 0)}, 6, 'Illegal Predicate Table Data'),
)


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    names = {name: n for n, name in im.sym.items()}
    normal = (pimm.ATOM, names['normal'])
    mods = {m['name']: m for m in modc.modules()}
    want, entries = [], 0
    for name in MODULES:
        mod = mods[name]
        for pos in POSITIONS:
            n, hs = len(mod['preds']), mod['hs']
            size = pos + 1 + hs + 2 * n + SPARE
            label = '%s at %d: %d entries, hash size %d' % (name, pos, n, hs)
            s.label(label)
            # the entries, in slot 2
            for i in (0, 1, 2, 3, 4, 7, 8, 9):
                s.newvar(i)
            s.argc(1, normal)
            for a, sl in ((2, 0), (3, 1), (4, 8), (5, 9), (6, 2), (7, 7), (8, 3), (9, 4)):
                s.arg(a, sl)
            s.spawn(pimm.predicate(im, 'ipl_file_decoder', 'decode_index_table/9'), 9)
            s.live()
            table = {k: deca.number(k, v) for k, v in mod['atoms_index'].items()}
            deca.serve(s, s.live_slot[0], s.live_slot[7], list(mod['index']), table, names, [])
            # a vector of zeros, in slot 10
            for i in (0, 1, 10, 3, 4, 7):
                s.newvar(i)
            s.argc(1, (pimm.INT, 0x0700))
            for a, sl in ((2, 0), (3, 1), (4, 10), (5, 7), (6, 3), (7, 4)):
                s.arg(a, sl)
            s.spawn(pimm.predicate(im, 'ipl_file_decoder', 'decode_0/7'), 7)
            s.live()
            deca.serve(s, s.live_slot[0], s.live_slot[7],
                       [size >> 16, size & 0xffff] + [0x0100] * size, {}, names, [])
            # the table
            s.newvar(11)
            s.newvar(12)
            s.arg(1, 10)
            s.argc(2, (pimm.INT, pos))
            s.argc(3, (pimm.INT, hs))
            s.arg(4, 2)
            s.arg(5, 11)
            s.arg(6, 12)
            s.spawn(pimm.predicate(im, 'ipl_module', 'set_pred_table/6'), 6)
            s.run()
            s.out(11)
            s.out(12)
            preds = [(deca.number(aid, mod['atoms'][aid]), arity, loc)
                     for (_n, arity, loc), aid in zip(mod['preds'], mod['detail']['entry_ids'])]
            want.append((label, pos, hs, size, preds))
            entries += n
    # put_structured_constant: three clauses that answer with a string
    # constant kept outside the module (TM-662)
    for mod, pred, args, out, text in REFUSALS:
        label = '%s:%s refuses' % (mod, pred)
        s.label(label)
        n = int(pred.split('/')[1])
        for i in range(n):
            s.newvar(i)
            s.arg(i + 1, i)
        for a, cell in args.items():
            s.unifyc(a - 1, cell if cell != 'other' else (pimm.ATOM, names['abnormal']))
        s.spawn(pimm.predicate(im, mod, pred), n)
        s.run()
        s.out(out - 1)
        want.append((label, text))
    s.entries = entries
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for item in want:
        if len(item) == 2:
            label, text = item
            t = m.term(got[label][-1])
            if t != ('abnormal', (8, [ord(c) for c in text])):
                bad.append((label, t))
            continue
        label, pos, hs, size, preds = item
        vec, status = got[label][-2:]
        v = m.deref(vec)
        if m.term(status) != 'normal' or m.vsize(v) != size:
            bad.append((label, 'status or size'))
            continue
        base = m.vbase(v)
        cell = [m.deref(m.mem[base + i]) for i in range(size)]
        cell = [(t & ~1, x) for t, x in cell]
        used = {pos}
        if cell[pos] != (pimm.INT, hs - 1):
            bad.append((label, 'mask', cell[pos]))
        for atom, arity, loc in preds:
            key = (pimm.ATOM, arity << 24 | (atom + arity) & 0xffffff)
            slot = pos + 1 + (key[1] & (hs - 1))
            st, sv = cell[slot]
            used.add(slot)
            hit = None
            if st == pimm.INT:
                for k in range(sv >> 16):
                    p = slot + (sv & 0xffff) + 2 * k
                    if cell[p] == key:
                        hit = p
            if hit is None or cell[hit + 1][0] != pimm.INT or hit + 1 + cell[hit + 1][1] != loc:
                bad.append((label, 'not found', hex(key[1]), loc))
            else:
                used |= {hit, hit + 1}
        if len(used) != 1 + len({pos + 1 + ((a + n) & (hs - 1)) for a, n, _l in preds}) \
                + 2 * len(preds):
            bad.append((label, 'pairs'))
        rest = [i for i in range(size) if i not in used and cell[i] != (pimm.INT, 0)]
        if rest:
            bad.append((label, 'other cells written', rest[:4]))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    pinned = dict(PINNED)
    entries = pinned.pop('entries')
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep ptab', pinned)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad or s.entries != entries:
        print('pimm lockstep ptab: FAIL, %d entries (pinned %d); %r'
              % (s.entries, entries, bad[:3]))
        return 1
    print('pimm lockstep ptab: PASS (the IPL builds the predicate entry tables of %d real '
          'modules, at two positions each, on the Bluespec core: %d entries, %d trace '
          'lines identical to the reference model; every predicate is found in the built '
          'table by the layout the IPL image\'s own tables have, at its location in the '
          'file)' % (len(MODULES), s.entries, s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
