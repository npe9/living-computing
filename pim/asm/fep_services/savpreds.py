#!/usr/bin/env python3
"""Predicate-by-predicate comparison of .sav object modules: a patch
module against the base module it replaces, and either against the
held source.  Read-only probe for docs/fep_services.md (U8).

For every predicate of a module (a predicate starts at an entry header:
atom, integer, an item of tag 24h whose top byte is the arity) it takes

  ops      the instruction names in order (asm/census.py's opcode
           table, by tag and opcode), with the whole word for the forms
           that hold no code address;
  consts   the atoms, integers, strings and hash-table keys in the
           code, in order (a string with both bytes of every word); the
           keys are compared as a set, their order being the hasher's;
  GC area  per module, not per predicate: the structured constants
           (strings, vectors, lists) and the external calls;
  ends     the number of proceed / execute / execute_external
           instructions: one per clause body, so the clause count,
           except where the compiler shares a body between clauses.

    python3 asm/fep_services/savpreds.py --patch MODULE [--show]
        base module against patch module: predicates added, dropped,
        changed (ops or consts differ); --show prints a diff of the
        changed ones
    python3 asm/fep_services/savpreds.py --source MODULE [--base]
        each object predicate (patch if there is one, else base; with
        --base the base) against the source file declaring the module:
        clause count (ends against the crude source reader's count,
        which counts every branch of a conditional) and the integers
        of the source clause (literals and fep#/scsi# macros) that are
        not among the predicate's integers.  One way only: integers
        the object has and the source does not are not reported (the
        compiler adds arities and sizes), and an integer inside a
        structured constant is in the module's GC area, not the
        predicate's
    python3 asm/fep_services/savpreds.py --has MODULE [PRED/N ...]
        which .sav files hold the module, and whether each predicate
        is in it (for the build switches)
    python3 asm/fep_services/savpreds.py --grep TEXT
        every module and predicate holding an atom or string with TEXT
    python3 asm/fep_services/savpreds.py --check
        the probe proved: a module the same in base and patch shows no
        difference (kl1_library_variable_pool), fep_server shows the 8
        added and 5 dropped predicates asm/savsrc.py --patches counts,
        scsi_fep 43 predicates and none added or dropped

The objects are read from docs/nonlocal/pimosobj.tar.Z and the source
from docs/nonlocal/pimos.tar.Z (not in git); nothing is written.
"""
import collections
import difflib
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))
import census  # noqa: E402
import savsrc  # noqa: E402
import unlsav  # noqa: E402

PLAIN = ('no', 'r', 'r_r', 'r_r_r', 'c8', 'c8_r', 'r_c16')
ENDS = ('proceed', 'execute', 'execute_external')


def _jis(raw, bits):
    if bits == 16:
        return savsrc._jis_name([raw[i] << 8 | raw[i + 1] for i in range(0, len(raw) - 1, 2)])
    return raw.decode('latin1')


def term(t):
    """A GC-area term of asm/unlsav.py's reader as text."""
    if t[0] == 'string':
        return '"%s"' % (savsrc._jis_name(t[3]) if t[2] == 16 else
                         ''.join(chr(e) for e in t[3]) if t[2] == 8 else t[3])
    if t[0] == 'atom':
        return t[2]
    if t[0] == 'int':
        return str(t[1])
    if t[0] in ('vector', 'list'):
        return ('{%s}' if t[0] == 'vector' else '[%s]') % ','.join(term(x) for x in t[1])
    if t[0] == 'extcall':
        return '%s:%s/%d' % (t[1][1], t[2][1], t[3])
    return repr(t)


def _code_base(words, r, code, size):
    """Index of the code area's first word: after the two words of
    its size, and every item's tag word of the right kind there."""
    hi, lo = size >> 16, size & 0xffff
    kinds = {'atom': lambda t: t >> 8 == 0x23, 'int': lambda t: t >> 8 in (1, 2, 3),
             'string': lambda t: t >> 8 == 6, 'table': lambda t: t == 0x1100,
             'atomref': lambda t: t == 0, 'inst': lambda t: t >> 8 == 0 and t & 255}
    for c in range(r.i - 1, 2, -1):
        if words[c - 2] == hi and words[c - 1] == lo and \
                all(kinds[it[0]](words[c + it[1]]) for it in code):
            return c
    raise ValueError('code base not found')


def modules():
    """[(file, module, {pred/arity: (ops, consts, ends)}, GC area)] in
    file order.  The GC area is the module's structured constants
    (strings, vectors, lists) and external calls, as text: they are
    the module's, not a predicate's."""
    unlsav.read_atom_name = savsrc._read_atom_name
    optab = census.opcode_table()
    types = {}
    for op, ents in unlsav.load_opcodes().items():
        for name, typ, tag in ents:
            types[(tag, op)] = typ
    out = []
    for fname, raw in census.sav_files(None):
        words = list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
        r = unlsav.Reader(words)
        magic, nmod, _sep = r.rd(), r.rd(), r.rd()
        if magic in (0x5702, 0x5802):
            clen = (r.rd() << 16) | r.rd()
            for _ in range(clen):
                r.rd()
        for _ in range(nmod):
            _mlen, names, gc, _hs, _public, code = unlsav.parse_module(r)
            detail = r.detail
            base = _code_base(words, r, code, detail['code_size'])
            preds = collections.OrderedDict()
            cur = None
            for i, it in enumerate(code):
                if it[0] == 'atomref' and i + 2 < len(code) and code[i + 2][0] == 'inst' \
                        and code[i + 2][3] == 0x24:
                    key = '%s/%d' % (it[3], code[i + 2][2] >> 24)
                    cur = preds.setdefault(key, [[], [], 0])
                    skip = i + 3
                    continue
                if cur is None or i <= skip:
                    continue
                if it[0] == 'inst':
                    tag, val = it[3], it[2]
                    op = val >> 24
                    name = (optab.get((tag, op)) or ['%02x:%02x' % (tag, op)])[0]
                    typ = types.get((tag, op), '?')
                    cur[0].append('%s %06x' % (name, val & 0xffffff) if typ in PLAIN else name)
                    if name in ENDS:
                        cur[2] += 1
                    if typ in ('r_c16', 'c8_c16'):
                        v = val & 0xffff
                        cur[1].append(('imm', v - 65536 if v & 0x8000 else v))
                    elif typ == 'c24':      # write_integer, read_integer
                        v = val & 0xffffff
                        cur[1].append(('imm', v - (1 << 24) if v & 0x800000 else v))
                elif it[0] == 'atom':
                    cur[0].append('atom')
                    cur[1].append(('atom', it[3]))
                elif it[0] == 'atomref':
                    cur[1].append(('atom', it[3]))
                elif it[0] == 'int':
                    cur[1].append(('int', it[2]))
                elif it[0] == 'string':
                    at = base + it[1]
                    bits = words[at] & 255
                    ln = words[at + 1] << 16 | words[at + 2]
                    n = 2 * ((ln * bits + 31) // 32)
                    rawb = b''.join(struct.pack('>H', w) for w in words[at + 3:at + 3 + n])
                    cur[1].append(('string', _jis(rawb[:ln * bits // 8], bits)))
                elif it[0] == 'table':
                    for k, _label in detail['code'].get(it[1], []):
                        cur[1].append(('key',) + tuple(k[:1] + k[-1:]) if k[0] == 'atom'
                                      else ('key',) + tuple(k))
            out.append((fname, names[0][1], preds, [term(t) for t in gc]))
    return out


def pick(mods, name):
    base = [(f, p) for f, m, p, _g in mods if m == name and '_patch_' not in f]
    patch = [(f, p) for f, m, p, _g in mods if m == name and '_patch_' in f]
    return base, patch


def norm(consts):
    """The constants with the hash-table keys sorted after the rest:
    a table's key order is the hasher's, not the source's (the patch
    of kl1_library_variable_pool differs from its base in that alone)."""
    return [c for c in consts if c[0] != 'key'] + sorted(
        (c for c in consts if c[0] == 'key'), key=repr)


def patch_diff(mods, name, show=False, out=print):
    base, patch = pick(mods, name)
    if not base or not patch:
        out('%s: base %s, patch %s' % (name, [f for f, _ in base], [f for f, _ in patch]))
        return None
    (bf, b), (pf, p) = base[0], patch[-1]
    added = [k for k in p if k not in b]
    dropped = [k for k in b if k not in p]
    changed = [k for k in p if k in b and (p[k][0] != b[k][0] or norm(p[k][1]) != norm(b[k][1]))]
    out('%s: base %s %d predicates, patch %s %d; added %d, dropped %d, changed %d, '
        'the same %d' % (name, bf, len(b), pf, len(p), len(added), len(dropped),
                         len(changed), len(p) - len(added) - len(changed)))
    gb = collections.Counter([g for f, m, _p, g in mods if m == name and f == bf][0])
    gp = collections.Counter([g for f, m, _p, g in mods if m == name and f == pf][0])
    if gb != gp:
        out('  GC area (strings, structures, external calls): base only %s; patch only %s'
            % (sorted((gb - gp).elements()), sorted((gp - gb).elements())))
    else:
        out('  GC area the same (%d terms)' % sum(gp.values()))
    for label, ks in (('added', added), ('dropped', dropped), ('changed', changed)):
        if ks:
            out('  %s: %s' % (label, ' '.join(ks)))
    if show:
        for k in changed:
            out('--- %s (base %d instructions, %d ends; patch %d, %d)'
                % (k, len(b[k][0]), b[k][2], len(p[k][0]), p[k][2]))
            for line in difflib.unified_diff(b[k][0], p[k][0], 'base ops', 'patch ops',
                                             lineterm='', n=2):
                out('    ' + line)
            cb, cp = [repr(c) for c in norm(b[k][1])], [repr(c) for c in norm(p[k][1])]
            for line in difflib.unified_diff(cb, cp, 'base consts', 'patch consts',
                                             lineterm='', n=0):
                out('    ' + line)
        for k in added:
            out('--- added %s: %d instructions, %d ends, consts %s'
                % (k, len(p[k][0]), p[k][2], [c for c in p[k][1] if c[0] != 'imm']))
    return added, dropped, changed


def macros():
    """{'fep#name': int} from the source's .vmac files (name# value)."""
    import io
    import subprocess
    import tarfile
    raw = subprocess.run(['gzip', '-dc', savsrc.SRC_TAR], stdout=subprocess.PIPE,
                         check=True).stdout
    table = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith('.vmac'):
                text = tf.extractfile(m).read().decode('latin1')
                for pre, nm, val in re.findall(
                        r'^\s*([a-z_0-9]+)\s*#\s*([a-z_0-9A-Z]+)\s*=>\s*(-?\d+)\s*[.:]', text, re.M):
                    table['%s#%s' % (pre, nm)] = int(val)
    return table


def source_preds(text, table):
    """{pred/arity: [clause count, set of integers]} by the crude
    reader of asm/savsrc.py, keeping the clause text for its numbers."""
    text = re.sub(r'%.*', '', text)
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    bare = re.sub(r'"(?:[^"\\\n]|\\.|"")*"', '""', text)
    bare = re.sub(r"'(?:[^'\n]|'')*'", 'q', bare)
    out = {}
    for cl in re.split(r'\.(?:\s+|$)', bare):
        cl = cl.strip()
        if not cl or cl.startswith(':-') or cl in ('otherwise', 'alternatively'):
            continue
        c = savsrc._clauses(cl + '. ')
        if not c:
            continue
        key = list(c)[0]
        ent = out.setdefault(key, [0, set()])
        ent[0] += 1
        for mac in re.findall(r'[a-z_0-9]+#[a-z_0-9A-Z]+', cl):
            if mac in table:
                ent[1].add(table[mac])
        for num in re.findall(r'(?<![A-Za-z_0-9#"])-?\d+(?![A-Za-z_#"])', re.sub(
                r'[a-z_0-9]+#"?[a-z_0-9A-Z]+"?', ' ', cl)):
            ent[1].add(int(num))
    return out


def source_diff(mods, name, out=print, use_base=False):
    base, patch = pick(mods, name)
    f, p = (base if use_base else (patch or base))[-1]
    texts = savsrc.sources().get(name)
    if not texts:
        out('%s: no source module' % name)
        return
    table = macros()
    path, text = texts[0]
    src = source_preds(text, table)
    out('%s: object %s, source %s' % (name, f, path))
    same = 0
    for k, (ops, consts, ends) in p.items():
        if k.startswith('$'):
            continue
        if k not in src:
            out('  %-32s not in the source' % k)
            continue
        n, ints = src[k]
        objints = set(c[1] for c in consts if c[0] in ('int', 'imm')) | \
            set(c[2] for c in consts if c[0] == 'key' and c[1] == 'int')
        missing = sorted(i for i in ints if i not in objints)
        if ends == n and not missing:
            same += 1
            continue
        out('  %-32s clauses: object ends %d, source %d%s' % (
            k, ends, n, '; source integers not in the object: %s' % missing if missing else ''))
    out('  %d predicates agree in clause count and integers; source only: %s'
        % (same, sorted(k for k in src if k not in p) or 'none'))


def main(argv):
    mods = modules()
    if '--check' in argv:
        ok = True
        res = patch_diff(mods, 'kl1_library_variable_pool')
        ok &= res == ([], [], [])
        res = patch_diff(mods, 'fep_server')
        ok &= res is not None and len(res[0]) == 8 and len(res[1]) == 5
        res = patch_diff(mods, 'scsi_fep')
        _b, p = pick(mods, 'scsi_fep')
        ok &= res is not None and not res[0] and not res[1] and len(p[-1][1]) == 43
        print('savpreds: %s' % ('PASS' if ok else 'FAIL'))
        return 0 if ok else 1
    args = [a for a in argv if not a.startswith('--')]
    if '--patch' in argv:
        patch_diff(mods, args[0], '--show' in argv)
    elif '--source' in argv:
        source_diff(mods, args[0], use_base='--base' in argv)
    elif '--has' in argv:
        hit = [(f, p) for f, m, p, _g in mods if m == args[0]]
        if not hit:
            print('%s: in no .sav file' % args[0])
        for f, p in hit:
            print('%s: in %s, %d predicates' % (args[0], f, len(p)))
            for want in args[1:]:
                print('  %-36s %s' % (want, 'present' if want in p else 'ABSENT'))
            if '--list' in argv:
                print('  ' + ' '.join(p))
    elif '--grep' in argv:
        for f, m, p, g in mods:
            hits = sorted(set(t for t in g if args[0] in t))
            if hits:
                print('%s %s (GC area)  %s' % (f, m, ' '.join(hits)))
            for k, (_ops, consts, _e) in p.items():
                hits = sorted(set(repr(c) for c in consts
                                  if c[0] in ('atom', 'string') and args[0] in str(c[1])))
                if hits:
                    print('%s %s:%s  %s' % (f, m, k, ' '.join(hits)))
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
