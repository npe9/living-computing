#!/usr/bin/env python3
"""Map the PIM/m KL1-B instructions PIMOS uses onto PDSS and VPIM.

The PIMOS object set (docs/nonlocal/pimosobj.tar.Z) uses 197 distinct
instructions (asm/census.py).  Two KL1 executors survive as source:
PDSS (C, docs/nonlocal/pdss.tar.Z, emulator/instr.h) and VPIM (PSL,
docs/nonlocal/vpim.tar.Z, src/primitives/p_opecode_table.psl.c).  This
tool says, per PIM/m instruction, whether PDSS has a counterpart and of
what kind:

  same     the same mnemonic (quick forms count with their base form)
  prefix   the same name under PDSS's g_/b_ built-in prefix, with
           floating_point spelled float
  renamed  a one-to-one counterpart under another name (RENAMED below)
  merged   a PIM/m specialisation of an instruction PDSS has only once
  differs  a name counterpart exists but takes a different number of
           register operands
  split    PIM/m has one instruction where PDSS has one per type or per
           position (SPLIT below); the semantics are there, the
           instruction is not
  absent   nothing in PDSS's table

The classification is by NAME and by the NUMBER of register operands
(inst_tab.kl1 Type against PDSS instr.c format).  It says nothing about
operand order, non-register operands or behaviour: "same" is a
candidate to check, not a result.  An opcode shared by several
mnemonics (a sub-function field) is classified by its first one.
--check pins the class sizes; it catches a changed table or decoder,
not a wrong pairing of equal count.

Usage:
    python3 asm/namemap.py [--check] [--table]
"""
import collections
import io
import os
import re
import subprocess
import sys
import tarfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import census  # noqa: E402
from unlsav import load_opcodes  # noqa: E402

NONLOCAL = os.path.join(HERE, '..', 'docs', 'nonlocal')

# One-to-one, different name.  The priority pair was read in PDSS
# blt_system.c: b_rate scales from the parent shoen's minimum priority,
# b_rltv from the goal's current one.  The switch/jump pairs are by
# name: the PIM/m forms are type r_c16_i (klb_opr.kl1), the PDSS ones
# REG_LAB; what the extra PIM/m word holds against PDSS is unchecked.
RENAMED = {
    'switch_on_non_atom': 'jump_on_non_atom',
    'switch_on_non_integer': 'jump_on_non_integer',
    'switch_on_non_list': 'jump_on_non_list',
    'switch_on_non_vector': 'jump_on_non_vector',
    'add_shoen_resource': 'b_shoen_add_resource',
    'collect_garbage': 'g_request_gc',
    'calculate_priority_from_current': 'b_rltv',
    'calculate_priority_from_minimum': 'b_rate',
}

# PIM/m has get_value (23/bc, 15,800 uses) as well; PDSS has one.
MERGED = {
    'get_bound_value': 'get_value',
}

# PIM/m instruction -> the PDSS family that covers it.
SPLIT = {
    'write_value': 'write_{car,cdr,element}_value',
    'write_marked_value': 'write_{car,cdr,element}_marked_value',
    'write_variable': 'write_{car,cdr,element}_variable',
    'write_marked_variable': 'write_{car,cdr,element}_marked_variable',
    'write_nil': 'write_{car,cdr,element}_nil',
    'write_integer': 'write_{car,cdr,element}_integer',
    'write_constant': 'write_{car,cdr,element}_{atom,integer,float}',
    'write_atom': 'write_{car,cdr,element}_atom',
    'read_variable': 'read_{car,cdr,element}',
    'read_variable_without_deref': 'read_{car,cdr,element}',
    'put_constant': 'put_{atom,integer,float}',
    'set_constant': 'set_{atom,integer,float}',
    'get_constant': 'get_{atom,integer,float}',
    'wait_constant': 'wait_{atom,integer,float}',
    'switch_on_constant': 'branch_on_{atom,integer}',
    'hash_on_constant': 'hash_on_{atom,integer}',
    'put_reused_structure': 'put_reused_{list,vector}',
    'string_operation': 'b_string_{and,or,exclusive_or,complement}',
}

CLASSES = ('same', 'prefix', 'renamed', 'merged', 'differs', 'split', 'absent')

PINNED = dict(same=73, prefix=46, renamed=5, merged=1, differs=4, split=18,
              absent=50)


def member(tarname, suffix):
    raw = subprocess.run(['gzip', '-dc', os.path.join(NONLOCAL, tarname)],
                         stdout=subprocess.PIPE, check=True).stdout
    with tarfile.open(fileobj=io.BytesIO(raw)) as tf:
        for m in tf.getmembers():
            if m.name.endswith(suffix):
                return tf.extractfile(m).read().decode('latin1')
    raise SystemExit('%s: no member %s' % (tarname, suffix))


def vpim_names():
    text = member('vpim.tar.Z', 'p_opecode_table.psl.c')
    return set(m.group(1).lower() for m in
               re.finditer(r'#CONST_define\s+(\w+)\s+0x', text))


def base(n):
    return re.sub(r'_\d+$', '', n)


def pimm_types():
    typ = {}
    for ents in load_opcodes().values():
        for name, t, _tag in ents:
            typ[name] = t
    return typ


def pdss_formats():
    text = member('pdss.tar.Z', 'emulator/instr.c')
    return dict(re.findall(r'op\(KL1B_\w+,\s*"(\w+)",\s*(\w+)\)', text))


def pimm_regs(t):
    """Register operands in an inst_tab.kl1 Type (r, r_r, r4, f_r_r(N))."""
    if t == 'atom':          # a register or argument slot rides in the
        return None          # opcode byte: no count to compare
    n = 0
    for tok in re.sub(r'\(.*\)', '', t).split('_'):
        m = re.fullmatch(r'r(\d*)', tok)
        if m:
            n += int(m.group(1) or 1)
    return n


def pdss_regs(f):
    """Register operands in a PDSS instr.c format (REG, REGS3, REG_LAB)."""
    m = re.search(r'REGS(\d)', f)
    return int(m.group(1)) if m else len(re.findall(r'REG', f))


def classify(name, typ, fmt):
    """(class, PDSS counterpart).  A name match only counts when the two
    take the same number of register operands; a name match that does
    not is 'differs' (vector, string: guard built-ins in PIM/m, the
    one-register wait-and-check instructions in PDSS)."""
    f = base(name).replace('floating_point', 'float')
    cands = [('same', name), ('same', base(name)), ('prefix', f),
             ('prefix', 'g_' + f), ('prefix', 'b_' + f),
             ('prefix', 'b_' + f + '2')]
    if name in RENAMED:
        cands.append(('renamed', RENAMED[name]))
    if name in MERGED:
        cands.append(('merged', MERGED[name]))
    t = typ.get(name) or typ.get(base(name))
    want = pimm_regs(t) if t else None
    near = None
    for kind, n in cands:
        if n in fmt and not fmt[n].startswith('ASSM_'):
            if want is None or pdss_regs(fmt[n]) == want:
                return kind, n
            near = near or n
    if near:
        return 'differs', near
    if name in SPLIT:
        return 'split', SPLIT[name]
    return 'absent', ''


def main(argv):
    key, used = census.census(None)[:2]
    vpim = vpim_names()
    typ, fmt = pimm_types(), pdss_formats()
    rows = []
    for k, c in used.most_common():
        name = key[k][0]
        kind, to = classify(name, typ, fmt)
        v = name if name in vpim else (base(name) if base(name) in vpim else '')
        rows.append((c, k, name, kind, to, v))
    total = sum(used.values())
    n = collections.Counter(r[3] for r in rows)
    w = collections.Counter()
    for r in rows:
        w[r[3]] += r[0]
    if '--check' in argv:
        if dict(n) != PINNED:
            print('namemap: FAIL\n  got    %r\n  pinned %r' % (dict(n), PINNED))
            return 1
        print('namemap: PASS (%s)' % ', '.join(
            '%d %s' % (PINNED[k], k) for k in PINNED))
        return 0
    print('PDSS instr.h: %d names; VPIM table: %d names' % (len(fmt), len(vpim)))
    for kind in CLASSES:
        print('%-8s %3d opcodes  %7d uses  %5.1f%%'
              % (kind, n[kind], w[kind], 100.0 * w[kind] / total))
    print('VPIM same-name: %d opcodes' % sum(1 for r in rows if r[5]))
    if '--table' in argv:
        for kind in ('renamed', 'merged', 'differs', 'split', 'absent'):
            print('\n%s:' % kind)
            for c, k, name, kd, to, v in rows:
                if kd == kind:
                    print('  %7d  %02x/%02x  %-36s %s' % (c, k[0], k[1], name, to))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
