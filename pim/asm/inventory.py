#!/usr/bin/env python3
"""Runtime inventory: what the PIMOS binaries ask of the machine.

Groups every instruction the object set (asm/census.py) and the IPL
image (asm/kbn.py) use by the part of the runtime it needs, and breaks
the shared opcodes out by their sub-function field (bits 23-16 of the
word, klb_opr.kl1 p({f_r_r,F},...)).  The grouping is by mnemonic and
is ours; it sizes the work, it does not define semantics.

Usage:
    python3 asm/inventory.py [--check] [--list]
"""
import collections
import re
import struct
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402
import kbn  # noqa: E402
from unlsav import Reader, parse_module, load_opcodes  # noqa: E402

# First match wins.
GROUPS = [
    ('device', r'^(scsi_|display_console|put_console|read_console|log_event|system_timer|set_timer|halt$)'),
    ('shoen/priority/processor',
     r'shoen|priority|processor|^current_node|^raise$|consume_resource'),
    ('goal control',
     r'^(proceed|execute|enqueue_goal|suspend|try_me_else|otherwise|jump|'
     r'fail|save|restore|clause_info|apply|true)'),
    ('heap/gc/profile', r'garbage|heap|profile|^collect_|^mark_element|unbound'),
    ('code/module/atom objects',
     r'^(code|module|new_module|new_instruction|predicate_to_code|'
     r'code_to_predicate|module_|new_atom|supply_atom|tag_and_value|'
     r'export_entry|hash$|merge$)'),
    ('extended float', r'extended_floating|binary_to_extended'),
    ('float', r'floating_point'),
    ('bignum/extended integer', r'bignum|_extended$'),
    ('string/vector built-ins',
     r'^(b_)?(set_)?(vector|string)(_element|_operation|_less|_not_less)?|'
     r'^new_(vector|string)|search_char|change_element_size'),
    ('indexing', r'^(switch_on|hash_on|jump_on|branch_on)'),
    ('guard type/compare',
     r'^(wait$|atom$|integer$|list$|vector$|string$|floating_point$|'
     r'less_than|not_less_than|equal|not_equal|diff)'),
    ('integer arithmetic',
     r'^(b_)?(add|subtract|multiply|divide|modulo|minus|shift_|and$|or$|'
     r'exclusive_or|complement|increment|decrement|abs|min|max)'),
    ('unification/structure',
     r'^(put_|get_|set_|write_|read_|wait_)'),
]

PINNED = {'device': (14, 563, 5, 137),
 'shoen/priority/processor': (19, 278, 17, 48),
 'goal control': (14, 117634, 9, 2197),
 'heap/gc/profile': (8, 57556, 4, 911),
 'code/module/atom objects': (13, 1228, 11, 51),
 'extended float': (43, 259, 1, 1),
 'float': (16, 485, 2, 8),
 'bignum/extended integer': (9, 322, 0, 0),
 'string/vector built-ins': (18, 7222, 13, 287),
 'indexing': (6, 20821, 6, 429),
 'guard type/compare': (8, 9923, 7, 547),
 'integer arithmetic': (21, 5176, 18, 397),
 'unification/structure': (56, 504586, 51, 8143),
 'UNGROUPED': (0, 0, 0, 0)}


def group(name):
    for g, pat in GROUPS:
        if re.search(pat, name):
            return g
    return 'UNGROUPED'


def subfunctions():
    sub = {}
    for op, ents in load_opcodes().items():
        for name, typ, tag in ents:
            m = re.match(r'f_r_r(?:_r)?\((16#")?([0-9a-fA-F]+)', typ)
            if m:
                sub[(tag, op, int(m.group(2), 16 if m.group(1) else 10))] = name
    return sub


def sav_subcounts(sub):
    ops = set(k[:2] for k in sub)
    c = collections.Counter()
    for _name, raw in census.sav_files(None):
        w = list(struct.unpack('>%dH' % (len(raw) // 2), raw[:len(raw) // 2 * 2]))
        r = Reader(w)
        magic, nmod, _sep = r.rd(), r.rd(), r.rd()
        if magic in (0x5702, 0x5802):
            r.i += (r.rd() << 16) | r.rd()
        for _ in range(nmod):
            for it in parse_module(r)[5]:
                if it[0] == 'inst':
                    k = (it[3], (it[2] >> 24) & 0xff, (it[2] >> 16) & 0xff)
                    if k[:2] in ops:
                        c[sub.get(k, 'UNKNOWN %02x/%02x f=%02x' % k)] += 1
    return c


def by_name(key, used, sub, subc):
    """Counter mnemonic -> uses, shared opcodes replaced by sub-functions."""
    ops = set(k[:2] for k in sub)
    out = collections.Counter()
    for k, c in used.items():
        if k in ops:
            continue
        out[key[k][0]] += c
    if subc is not None:
        out.update(subc)
    return out


def main(argv):
    key, used = census.census(None)[:2]
    sub = subfunctions()
    subc = sav_subcounts(sub)
    full = by_name(key, used, sub, subc)
    # IPL image: shared opcodes by sub-function straight from the cells.
    _got, cells, _mods, _tags, kused, _key = kbn.decode(kbn.image())
    ops = set(k[:2] for k in sub)
    ksub = collections.Counter()
    for t, v in cells:
        if (t, v >> 24) in ops:
            k = (t, v >> 24, (v >> 16) & 0xff)
            ksub[sub.get(k, 'UNKNOWN %02x/%02x f=%02x' % k)] += 1
    ipl = by_name(key, kused, sub, ksub)
    rows = []
    for g, _ in GROUPS + [('UNGROUPED', '')]:
        fn = [n for n in full if group(n) == g]
        kn = [n for n in ipl if group(n) == g]
        rows.append((g, len(fn), sum(full[n] for n in fn),
                     len(kn), sum(ipl[n] for n in kn)))
    got = dict((r[0], r[1:]) for r in rows)
    if '--check' in argv:
        if got != PINNED:
            print('inventory: FAIL\n  got    %r\n  pinned %r' % (got, PINNED))
            return 1
        print('inventory: PASS (%d mnemonics in the object set, %d in the '
              'IPL image, none ungrouped)' % (len(full), len(ipl)))
        return 0
    print('%-28s %9s %9s   %7s %7s' % ('group', 'set:names', 'uses', 'IPL:names', 'uses'))
    for r in rows:
        print('%-28s %9d %9d   %7d %7d' % r)
    print('%-28s %9d %9d   %7d %7d' % ('total', len(full), sum(full.values()),
                                       len(ipl), sum(ipl.values())))
    print(repr(got))
    if '--list' in argv:
        for g, _ in GROUPS + [('UNGROUPED', '')]:
            print('\n%s:' % g)
            for n, c in sorted(full.items(), key=lambda x: -x[1]):
                if group(n) == g:
                    print('  %7d %6s  %s' % (c, ipl.get(n, ''), n))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
