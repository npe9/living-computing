#!/usr/bin/env python3
"""Lockstep: Goal@processor(P) with P unbound waits for P.

    python3 ref/pimm/lockstep_tproc.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_tproc.py compare
    python3 ref/pimm/lockstep_tproc.py --reference       the reference alone

enqueue_goal_to_processor (23:65) with an unbound processor number:
the goal waits for the number.  Carried over from VPIM, agreeing with
KLIC; the PIM/m firmware's behaviour is not held.  VPIM
(src/interpreter/klb_fork.psl.c klb_enqueue_to_processor, lines
406-447) hooks on the processor a D-code goal
`dcode_enqueue_processor(Processor,Code,Argv) :- integer(Processor) |
dcode_apply(Code,Argv)@processor(Processor).`; KLIC (runtime/sched.c
enqueue_throw_goal, 267-330) waits for the node number too.  PDSS
drops the number when it compiles (compiler/outp.kl1:360-363), a
single processor's simplification.  Here (OURS, asm/pimm_stubs.py
TO_PROCESSOR) P and the goal's code address are put after the
arguments, and a goal of the stub to_processor N (22:02, not a PIM/m
instruction) is hooked on P; when it runs, P still unbound waits
again, P = 0 makes the goal ready with the first N, another number is
refused.  It was the stop of pim:go/4 with
the device (rung S0, docs/binary_reverse_engineering.md 1.4):
scsi_manager:check_lpid_pool/7, create_scsi_device(..)@node(Cluster),
Cluster from a pool's answer in the same body.

The site here: pimm_patch_scsifep360E.sav, loaded by ipl_loader:load/4
exactly as lockstep_gmul.py loads it; the one enqueue_goal_to_processor
of the file, to processor r17 with eight arguments, then proceed:

    put_vector r18, 3 {r9, r10, r11}
    set_value 1, r18 / 2, r7 / 3, r8;  set_integer 4, 0 / 5, 1
    set_value 6, r1 / 7, r5 / 8, r13
    enqueue_goal_to_processor r17, L, 8
    proceed

(asm/unlsav.py --disasm, words 01cb..01f5).  r17 is, in the clause,
an element of a message read without dereference (put_marked_value
r17, r9): the processor comes from elsewhere.  A goal of 19 arguments
(r0..r18, the bench's integers k for rk, r17 the bench's variable P)
is started at the put_vector, so the clause's own instructions make
the goal's arguments.

Parts:
  P unbound        the clause proceeds (E done) and the goal does not
                   run: no instruction at L
  P = 0            the stub runs, then the goal at L, its r0..r7
                   {9,10,11}, 7, 8, 0, 1, 1, 5, 13 (the oracle: the
                   clause's set_value list as written above)
  P := Q unbound   a second goal; P bound to another variable Q: the
                   stub runs and waits again on Q (nothing at L)
  Q = 0            then the goal runs at L with the same arguments

Observed fault injections into the Bluespec (bsv/PimmStages.bsv), each
run alone (bsv/run_pimm_lockstep.sh tproc) and restored from a copy,
2026-11-24 (first difference):
  the waiting-again goal one argument short   P := Q unbound, line 132
                                              (the record's arity cell)
  the ready goal one argument short           P = 0, line 20 (the same)
  P unbound at the stub taken as 0            P := Q unbound, line 129
                                              (the Bluespec refuses
                                              the unbound P: E unimp)
  P and the code address swapped              P unbound, line 89 (A 10
                                              for A 9)
  the waiting goal hooked on its own record   P unbound, line 107
NOT run: another processor number (a refusal), an arity over 9
(refused), the waiting goal inside a shoen.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_link as link  # noqa: E402

PINNED = dict(parts=5, lines=2064615)
FILE = 'pimm_patch_scsifep360E.sav'
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
ARGS = [None, 7, 8, 0, 1, 1, 5, 13]                 # r0 is the vector


def sites(m):
    """pc of each enqueue_goal_to_processor in the loaded modules."""
    out = []
    for a in sorted(a for a, c in m.mem.items()
                    if a >= m.load + 0x8000 and c[0] == pimm.CDESC and c[1] >> 24 == 6):
        n, gc = m.mem[a][1] & 0xffffff, m.mem[a + 1][1]
        for pc in range(a + 2 + gc, a + n + 1):
            c = m.mem.get(pc)
            if c and c[0] == 0x23 and c[1] >> 24 == 0x65:
                out.append(pc)
    return out


def start(s, pslot):
    """A goal of 19 arguments at the put_vector: rk = k, r17 = slot."""
    for k in range(19):
        if k == 17:
            s.arg(k + 1, pslot)
        else:
            s.argc(k + 1, I(k))
    s.spawn(s.start, 19)
    s.run()


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    link.one(s, im, names, 'load', [FILE])
    m = s.live()
    found = sites(m)
    assert len(found) == 1, found
    pc = found[0]
    st = pc - 12
    c = m.mem[st]
    assert c[1] >> 24 == 0x3b and (c[1] >> 16) & 255 == 18, (st, c)   # put_vector r18
    assert (m.mem[pc][1] >> 16) & 255 == 17 and m.mem[pc + 1][1] >> 24 == 8
    s.start = st - m.load
    s.site = pc - m.load
    s.target = pc + 2 + pimm.sx16(m.mem[pc][1] & 0xffff) - m.load
    s.stub = m.stubs['$to_processor8']['addr']
    s.label('P unbound')
    s.newvar(0)
    start(s, 0)
    s.label('P = 0')
    s.unifyc(0, I(0))
    s.run()
    s.label('P := Q unbound')
    s.newvar(1)
    s.newvar(2)
    start(s, 1)
    s.unify(1, 2)
    s.run()
    s.label('Q = 0')
    s.unifyc(2, I(0))
    s.run()
    return s


def check(s, parts):
    bad = []
    at = lambda lines, a: [k for k, ln in enumerate(lines) if ln.startswith('I %d ' % a)]  # noqa: E731
    want = {'P unbound': (0, 0), 'P = 0': (1, 1), 'P := Q unbound': (1, 0), 'Q = 0': (1, 1)}
    for label, (nstub, ntarget) in want.items():
        lines = parts.get(label, [])
        if not lines:
            bad.append((label, 'not played'))
            continue
        if label in ('P unbound', 'P := Q unbound') and not at(lines, s.site):
            bad.append((label, 'the site not reached'))
        st, tg = at(lines, s.stub), at(lines, s.target)
        if len(st) != nstub or (len(tg) > 0) != (ntarget > 0):
            bad.append((label, 'stub %d target %d' % (len(st), len(tg))))
            continue
        if ntarget:
            if tg[0] < st[0]:
                bad.append((label, 'the goal ran before the stub'))
            regs = {}
            for ln in lines[st[0] + 1:tg[0]]:
                f = ln.split()
                if f[0] == 'R':
                    regs[int(f[1])] = f[2]
            for k, v in enumerate(ARGS):
                got = regs.get(k)
                if v is None:
                    ok = got is not None and int(got[:2], 16) & 0xfe == pimm.VECT0 + 6
                else:
                    ok = got == '00%08x' % v
                if not ok:
                    bad.append((label, 'r%d' % k, got, v))
    if 'E done' not in parts.get('P unbound', []):
        bad.append(('P unbound', 'no E done'))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    kept = {}
    play = s.play

    def keeping(m=None):
        for what, lines in play(m):
            if what != 'load':
                kept[what] = list(lines)
            yield what, lines
    s.play = keeping
    if '--reference' in argv:
        n = 0
        for what, lines in s.play():
            n += len(lines)
            if what == 'load':
                lines.clear()
        bad = check(s, kept)
        print(bad, n, len(kept), [(k, len(v)) for k, v in kept.items()])
        if '--show' in argv:
            for k, v in kept.items():
                print('==', k)
                print('\n'.join(v[:200]))
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep tproc', PINNED)
    if not ok:
        return 1
    bad = check(s, kept)
    if bad:
        print('pimm lockstep tproc: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep tproc: PASS (Goal@processor(P) with P unbound waits for P, at the '
          'one site of %s loaded by ipl_loader:load/4, on the Bluespec core: %d trace lines '
          'identical to the reference model; the goal runs at P = 0 with the clause\'s eight '
          'arguments, and after P is bound to a variable waits again)' % (FILE, s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
