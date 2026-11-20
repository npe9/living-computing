#!/usr/bin/env python3
"""Lockstep: the IPL's file decoder on real entry tables and code areas.

    python3 ref/pimm/lockstep_modc.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_modc.py compare

The rest of a module of the real pimm_kernel360E.sav after its GC area
(lockstep_gca.py does the part before), as two goals per module.  The
argument roles are read from the object code (asm/kl1decomp.py):

    decode_index_table(normal, In, Rest, HashSize, Twice, Entries, AT0, AT, Status)
        In is [HashSize, N | ...]; Twice is N * 2 (b_multiply);
        Entries is [pred(Name/Arity), pointer(Location), ...], N pairs
    decode_code_area(normal, In, Rest, Size, Code, AT0, AT, Status)
        In is {Size, [...]}: a 32-bit size, then the code up to FFFF

The test plays the reader and the atom table (lockstep_deca.serve).

Oracle, asm/unlsav.py's reading of the same words (its census of the
whole .sav set is the suite's `census` check):
  - HashSize, N * 2, and each entry's atom, arity and location;
  - Size, the number of code items, and item by item:
      an integer                        the integer
      00TT hi lo  (an instruction)      {TT, Value}
      0000 atom                         the atom
      23oo atom                         atom({35, oo, Atom})
      1100 size n, n keys and labels    table({Size, [Key = Label, ...]})
    The left column is unlsav's; the right-hand shapes are the object
    code's, and the oracle confirms the numbers and atoms in them;
  - all the words are taken, Status is normal, both streams end.

Modules: MODULES, chosen to hold every item kind above (shoen has two
tables, one keyed by integers and one by atoms).  No code area in the
file holds a string.

New here: b_multiply (the multiply box, PimmMBox.bsv),
write_marked_variable, write_integer.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  multiplier never adds              the first index table: N * 2 = 0 for 2
  multiplicand does not shift        the same: 1 for 2
  b_multiply writes r[x]             the same: R 0 written for R 3
  write_integer writes an atom       the first atom item: M = 02:00000023 for 00:
  write_integer does not advance     the same: the next cell written one low
  write_marked_variable leaves the   the first index table: R 9 not written
    register

Not caught: the multiplier one step short, and never reporting an
overflow.  The only product here is N * 2 with N at most 15: no large
operand, no negative one, no overflow.
"""
import io
import os
import struct
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import unlsav  # noqa: E402
import lockstep_deca as deca  # noqa: E402

sys.setrecursionlimit(100000)       # a code list is shown recursively

PINNED = dict(parts=6, lines=217484, items=1479)
MODULES = ('system2defined2servers', 'task2std2abnormal', 'shoen')


def s32(v):
    return v - (1 << 32) if v >= 1 << 31 else v


def modules():
    """Per module of the kernel file: name, the index table's words and
    the atoms known before them, the code area's likewise, and
    unlsav's reading (hash size, entries, code items, detail)."""
    raw = subprocess.run(['gzip', '-dc', deca.OBJ], stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('pimm_kernel360E.sav'):
                data = tf.extractfile(m).read()
    words = list(struct.unpack('>%dH' % (len(data) // 2), data))
    r = unlsav.Reader(words)
    magic, nmod, _sep = r.rd(), r.rd(), r.rd()
    if magic in (0x5702, 0x5802):
        r.i += 2 + ((words[r.i] << 16) | words[r.i + 1])
    out = []
    for _ in range(nmod):
        start, before = r.i, dict(r.atoms)
        mod = unlsav.parse_module(r)
        end, detail = r.i, r.detail
        # where the index table and the code area begin: read again
        q = unlsav.Reader(words)
        q.i, q.atoms = start + 3, dict(before)
        unlsav.read_atom_name(q)
        unlsav.read_atom_name(q)
        unlsav.parse_term(q)
        unlsav.parse_term(q)
        while q.peek() != 0x1000:
            unlsav.parse_term(q)
        q.rd()
        index, atoms_index = q.i, dict(q.atoms)
        q.rd()
        for _ in range(q.rd()):
            unlsav.read_atom_name(q)
            q.i += 3
        code, atoms_code = q.i, dict(q.atoms)
        assert words[end - 1] == 0xffff
        out.append(dict(name=mod[1][0][1], index=words[index:code], atoms_index=atoms_index,
                        code=words[code:end], atoms_code=atoms_code, atoms=dict(r.atoms),
                        whole=words[start:end], atoms_before=before, name_id=mod[1][0][0],
                        hs=mod[3], preds=mod[4], items=mod[5], detail=detail))
    return out


def atom(aid, names):
    n = deca.number(aid, names[aid])
    return [] if n == 0 else '#%x' % n


def expected_index(mod):
    out = []
    for (name, arity, loc), aid in zip(mod['preds'], mod['detail']['entry_ids']):
        out += [('pred', ('/', atom(aid, mod['atoms']), arity)), ('pointer', loc)]
    return out


def expected_code(mod):
    out, names, detail = [], mod['atoms'], mod['detail']['code']
    for it in mod['items']:
        kind, addr = it[0], it[1]
        if kind == 'int':
            out.append(s32(it[2] & 0xffffffff))
        elif kind == 'inst':
            out.append((it[3], s32(it[2])))
        elif kind == 'atomref':
            out.append(atom(it[2], names))
        elif kind == 'atom':
            out.append(('atom', (it[2] >> 8, it[2] & 0xff, atom(detail[addr], names))))
        elif kind == 'table':
            rows = []
            for key, lab in detail[addr]:
                assert key[0] in ('int', 'atom'), key
                k = s32(key[1] & 0xffffffff) if key[0] == 'int' else atom(key[1], names)
                rows.append(('=', k, lab))
            out.append(('table', (it[2], rows)))
        else:
            raise AssertionError(it)
    return out


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    names = {name: n for n, name in im.sym.items()}
    normal = (pimm.ATOM, names['normal'])
    mods = {m['name']: m for m in modules()}
    want, items = [], 0
    for name in MODULES:
        mod = mods[name]
        for what in ('index', 'code'):
            label = '%s, %s: %d words' % (name, what, len(mod[what]))
            s.label(label)
            for i in (0, 1, 2, 3, 4, 7, 8, 9):
                s.newvar(i)
            s.argc(1, normal)
            s.arg(2, 0)
            s.arg(3, 1)
            s.arg(4, 8)
            if what == 'index':
                pc = pimm.predicate(im, 'ipl_file_decoder', 'decode_index_table/9')
                for a, sl in ((5, 9), (6, 2), (7, 7), (8, 3), (9, 4)):
                    s.arg(a, sl)
                s.spawn(pc, 9)
                exp = (mod['hs'], 2 * len(mod['preds']), expected_index(mod))
                items += len(mod['preds'])
            else:
                pc = pimm.predicate(im, 'ipl_file_decoder', 'decode_code_area/8')
                for a, sl in ((5, 2), (6, 7), (7, 3), (8, 4)):
                    s.arg(a, sl)
                s.spawn(pc, 8)
                exp = (mod['detail']['code_size'], None, expected_code(mod))
                items += len(mod['items'])
            s.live()
            table = {k: deca.number(k, v) for k, v in mod['atoms_' + what].items()}
            at, atq, feed = deca.serve(s, s.live_slot[0], s.live_slot[7], list(mod[what]),
                                       table, names, [])
            assert not feed, (label, len(feed))
            s.setslot(5, at)
            s.setslot(6, atq)
            for i in (1, 2, 3, 4, 5, 6, 8, 9):
                s.out(i)
            want.append((label, exp))
    s.items = items
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for label, (first, twice, exp) in want:
        unlfs, obj, at, status, tail, atail, a8, a9 = got[label][-8:]
        t = m.term(obj)
        if t != exp:
            d = [i for i in range(min(len(t), len(exp))) if t[i] != exp[i]][:1]
            bad.append((label, len(t), len(exp), [(i, t[i], exp[i]) for i in d]))
        if m.term(a8) != first or (twice is not None and m.term(a9) != twice):
            bad.append((label, 'numbers', m.term(a8), first, twice))
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
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep modc', pinned)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad or s.items != items:
        print('pimm lockstep modc: FAIL, %d items (pinned %d); answers differ: %s'
              % (s.items, items, repr(bad[:1])[:600]))
        return 1
    print('pimm lockstep modc: PASS (the IPL file decoder on the entry tables and code '
          'areas of %d modules of the real pimm_kernel360E.sav on the Bluespec core: %d '
          'entries and code items, %d trace lines identical to the reference model; '
          'every item as asm/unlsav.py reads the same words)'
          % (len(MODULES), s.items, s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
