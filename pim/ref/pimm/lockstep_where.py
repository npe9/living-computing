#!/usr/bin/env python3
"""Lockstep: scsi_where.

    python3 ref/pimm/lockstep_where.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_where.py compare

scsi_where(^Info), 22:A0: one output, no input (PIMOS compiler,
library/compiler/blt.kl1).  Its meaning is from the built-in's
stand-in in the PIMOS source, bios/boot/scsi_conf.kl1: "Info ::= '[]'
| '[' SCSI_Info '|' Info ']'; SCSI_Info ::= '{' Cluster ',' Processor
',' SCSI_PORT ',' MY_UNIT '}'", and for one front-end processor on
eight nodes or fewer the stand-in answers [{0,0,0,6}].  Both models
give that value: the single-FEP configuration is the stand-in's, and
what PIM/m's firmware read it from is not known.  pim:go/4 meets it
first after the banner (longrun_ipl.py --reference --go).

No predicate of the IPL image uses it, and a built-in with no input
has no stub (asm/pimm_stubs.py), so the bench writes a three-cell
code into the heap, OURS: scsi_where 1; get_value 1, 0; proceed, and
starts a goal of it twice.

Checked: both answers are [{0, 0, 0, 6}], and each is a new list.

Observed fault injections into the Bluespec, 2026-11-23, restored:
  own unit 5                         where, line 20
  the list's cdr not nil             where, line 22
  the vector's MRB off               where, line 21
  the list cell before the vector    where, line 18
  the register not written           where, line 23
All five fail in the trace before any value check; the value check
alone would catch the first two and the fifth.

Not run: PIMOS's own use of the answer (bios's SCSI set-up, after
the banner); a configuration with more than one front end.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=1, lines=54)
# the bench's code, OURS: scsi_where 1; get_value 1, 0; proceed
CODE = [(0x22, 0xa0 << 24 | 1 << 16), (0x23, 0xbc << 24 | 1 << 16), (0x23, 0x60 << 24)]


def script():
    s = driver.Script()
    s.label('where')
    s.vector(0, 2, CODE)
    m = s.live()
    code = m.vbase(m.deref(s.live_slot[0])) - m.load
    for _ in range(2):
        s.newvar(6)
        s.arg(1, 6)
        s.spawn(code, 1)
        s.run()
        s.out(6)
    return s


def check(s, m):
    got = [m.term(w) for _l, w in s.outs]
    want = [[(0, 0, 0, 6)]] * 2
    bad = [] if got == want else [('answers', got, want)]
    a, b = [m.deref(w) for _l, w in s.outs]
    if a[0] != pimm.LIST + 1 or a[1] == b[1]:
        bad.append(('not two new lists', a, b))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        parts = dict(s.play())
        print(check(s, s.machine), sum(len(v) for v in parts.values()))
        return 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep where', PINNED)
    if not ok:
        return 1
    bad = check(s, m)
    if bad:
        print('pimm lockstep where: FAIL %r' % (bad,))
        return 1
    print('pimm lockstep where: PASS (scsi_where on the Bluespec core, %d trace lines identical '
          'to the reference model: [{0, 0, 0, 6}] twice, each a new list)' % s.counts['lines'])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
