#!/usr/bin/env python3
"""Code stubs for body built-ins that must wait (the project's design).

When a body built-in meets an unbound input, the PIM/m firmware kept it
for later; how is lost with the firmware.  PDSS, the sibling emulator,
turns it into a goal of a small code object (`body_builtin_suspend`,
emulator/goal.c, with the `dc_*` pseudo-predicates of dcode.c): inputs
as arguments, a fresh variable for each output.  We do the same with
ordinary KL1-B code, so that a waiting built-in needs no machinery of
its own: its goal's code is a stub

    <the built-in> 0, 1, .. n-1      inputs in r[k], outputs to r[n+j]
    get_value n+j, k                 one per output operand k
    proceed

where the goal's n arguments are the instruction's n operands in order
(an output operand's argument is the fresh variable).  The stubs are a
fixed table placed directly after the IPL image, one per body built-in
whose encoding and operand directions are both known
(docs/kl1_encoding.md, asm/bltdir.py).  Both models load the same
table: the reference model calls build(), the Bluespec loads it as
part of generated/pimm_ipl.hex.

    python3 asm/pimm_stubs.py --check
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bltdir  # noqa: E402
from unlsav import load_opcodes  # noqa: E402

REGS = {'r': 1, 'r_r': 2, 'r_r_r': 3, 'r4': 4, 'r5': 5, 'r6': 6, 'r7': 7}
GET_VALUE = (0x23, 0xbc)
PROCEED = (0x23, 0x60)

PINNED = dict(stubs=71, cells=260)

# The merger's step.  NOT a PIM/m instruction: the machine's merger is a
# cell with its own tag (MGHOK) that acts when it is unified; here a
# merger input is a goal of this code waiting on the input stream
# (docs/pimm_semantics.md).  22:00 has no entry in the firmware's
# decode table (asm/psdpim.py --table 2); both models refuse it
# anywhere but here.
MERGE_IN = (0x22, 0x00)

# The step of a unification of two structures.  NOT a PIM/m instruction
# either (22:01 has no entry in the firmware's table).  PDSS does not
# unify two lists or two vectors where it meets them: it makes a goal
# of a pseudo-predicate (emulator/unify.c
# make_unify_vector_vector_goal_and_enqueue, dc_unify_vector_vector2:
# arguments X, Y and the element to go on from) that unifies the
# elements when it runs.  Here that goal's code is this stub:
# unify_step 0, 1, 2 unifies element r2 of r0 and r1, adds one to r2
# and is taken again, until r2 is the size.
UNIFY_STEP = (0x22, 0x01)


def encode(tag, op, regs):
    """The cells of an instruction with register operands (klb_opr.kl1
    p(r_r_r..r7)): three in the first cell, the rest from the top byte
    of a second."""
    r = list(regs) + [0] * (7 - len(regs))
    cells = [(tag, op << 24 | r[0] << 16 | r[1] << 8 | r[2])]
    if len(regs) > 3:
        cells.append((0x00, r[3] << 24 | r[4] << 16 | r[5] << 8 | r[6]))
    return cells


def build(base):
    """Return (cells, table): the stub cells, to be placed at cell index
    `base`, and name -> dict(addr, dirs, words) with addr a cell index
    and words the length of the built-in instruction itself."""
    enc = {}
    for op, ents in load_opcodes().items():
        for name, typ, tag in ents:
            enc.setdefault(name, (tag, op, typ))
    cells, table = [], {}
    rows, _count = bltdir.table()
    for kind, name, dirs, _src in rows:
        if kind != 'body' or name not in enc or name in table:
            continue
        tag, op, typ = enc[name]
        n = REGS.get(typ)
        if n is None or n != len(dirs) or '?' in dirs or 'i' not in dirs:
            continue
        regs, outs = [], []
        for k, d in enumerate(dirs):
            if d == 'i':
                regs.append(k)
            else:
                regs.append(n + len(outs))
                outs.append((n + len(outs), k))
        ins = encode(tag, op, regs)
        table[name] = dict(addr=base + len(cells), dirs=dirs, words=len(ins))
        cells += ins
        for r, k in outs:
            cells.append((GET_VALUE[0], GET_VALUE[1] << 24 | r << 16 | k << 8))
        cells.append((PROCEED[0], PROCEED[1] << 24))
    # merge_in 0, 1: the input stream, the merger's record
    table['$merge_in'] = dict(addr=base + len(cells), dirs='ii', words=1)
    cells.append((MERGE_IN[0], MERGE_IN[1] << 24 | 0 << 16 | 1 << 8))
    cells.append((PROCEED[0], PROCEED[1] << 24))
    # unify_step 0, 1, 2: the two structures, the element to go on from
    table['$unify_step'] = dict(addr=base + len(cells), dirs='iii', words=1)
    cells.append((UNIFY_STEP[0], UNIFY_STEP[1] << 24 | 0 << 16 | 1 << 8 | 2))
    cells.append((PROCEED[0], PROCEED[1] << 24))
    return cells, table


def main(argv):
    cells, table = build(0)
    got = dict(stubs=len(table), cells=len(cells))
    if '--check' not in argv:
        for name, e in table.items():
            print('%5d %-36s %s' % (e['addr'], name, e['dirs']))
        print(got)
        return 0
    if got != PINNED:
        print('pimm_stubs: FAIL %r, pinned %r' % (got, PINNED))
        return 1
    print('pimm_stubs: PASS (%d built-in stubs, %d cells)' % (got['stubs'], got['cells']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
