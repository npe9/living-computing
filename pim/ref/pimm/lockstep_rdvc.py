#!/usr/bin/env python3
"""Lockstep: the guard instruction diff (X \\= Y), at its site in the file
request device of the mkdir patch.

    python3 ref/pimm/lockstep_rdvc.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_rdvc.py compare
    python3 ref/pimm/lockstep_rdvc.py --reference       the reference alone

diff(X, Y), 23:F9 r_r (library/assembler/inst_tab.kl1:212; both
inputs, library/compiler/blt.kl1:239-244): "Succeeds if it is assured
that X is not equal to Y ... X or Y must be an atomic term"; it
suspends while either is unbound and fails if they are equal (PIMOS
manual, e-builtin.tex:114-143).  A term that is not atomic ("Illegal
DIFF!!!" on the CSP, the same page) is refused on both models; atomic
here is an integer or an atom.  It was a stop of pim:go/4 with the
device (rung S0, docs/scsi_plan.md): scsi_manager's
create_scsi_device/9, `atom(Type), Type \\= non_existent`, in the
96,474-word pimm_bios360E.sav.

The site here: pimm_patch_mkdir360E.sav, loaded by ipl_loader:load/4
exactly as lockstep_xmod.py loads it, module file_request_device,
server/fep/file/fileRdvc.kl1:36-48, driver_0/10:

    driver_0(CAb,_,F,T,If,_,_,_,_,FA) :- wait(CAb) | (an external call)
    alternatively.
    driver_0(CAb,[reset(Args)|DRS],...) :- true | ...
    driver_0(_,[close(S)|_],...) :- true | ...
    driver_0(CAb,[Req|DRS],F,T,If,A,A1,AtF,Att,FA) :-
        vector_element(Req,0,MsgName),MsgName\\=reset,MsgName\\=close |
            A1=[Req|A2], driver_0(CAb,DRS,F,T,If,A,A2,AtF,Att,FA).
    driver_0(_,[],...) :- true | ...

The predicate is the PREDH head (arity 10) before the module's first
two diffs; a goal is started at its first instruction, the bench's
variables for the arguments, DRS = [Req|Rest] with Rest and CAb
unbound.  When the fourth clause commits, A1 is bound to [Req|A2] and
the recursive goal waits for Rest; when no clause can commit, the goal
waits (for CAb, and in the second part for MsgName) and A1 stays
unbound.  Parts (Req; expected, from the source, not either model):

  {other, 1}        A1 = [Req|_]   both diffs succeed
  {N, 1}          A1 = [Req|_]   N the integer equal to the atom
                                 number of reset (the put_atom's): an integer is not an
                                 atom of the same value
  {reset, 1, 2}   A1 unbound     the first diff fails (a three-vector
                                 is not reset(Args))
  {close, 1, 2}   A1 unbound     the second diff fails
  {M, 1}          A1 unbound, then, M bound to another atom, A1 = [Req|_]
                                 diff waits for M

Observed fault injections into the Bluespec (bsv/PimmStages.bsv, the
diff branch of rule deref2), each run alone (bsv/run_pimm_lockstep.sh
rdvc) and restored from a copy, 2026-11-23:
  diff inverted (equal succeeds)     part 1 ({other, 1}), line 81: the
                                     next clause (I 884753) for the
                                     second diff (I 884732)
  the values compared, not the tags  part 2 ({N, 1}), line 81: the same
  diff always succeeds               part 3 ({reset, 1, 2}), line 77:
                                     the second diff for the next clause

NOT run: a term that is not atomic (refused), the manual's empty
vector (refused here).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_link as link  # noqa: E402
import lockstep_modc as modc  # noqa: E402

PINNED = dict(parts=7, lines=7422314)
FILE = 'pimm_patch_mkdir360E.sav'
MODULE = 'file2request2device'      # the file's spelling of file_request_device
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731


def modules(m):
    return sorted(a for a, c in m.mem.items()
                  if a >= m.load + 0x8000 and c[0] == pimm.CDESC and c[1] >> 24 == 6)


def sites(m, a, opcode):
    """(pc, its predicate's first instruction, arity) of each
    instruction with this 23:opcode in the module at a."""
    out = []
    n, gc = m.mem[a][1] & 0xffffff, m.mem[a + 1][1]
    for pc in range(a + 2 + gc, a + n + 1):
        c = m.mem.get(pc)
        if c and c[0] == 0x23 and c[1] >> 24 == opcode:
            h = pc
            while m.mem[h][0] != pimm.PREDH:
                h -= 1
            out.append((pc, h + 2, m.mem[h][1] >> 24))
    return out


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    A = lambda n: (pimm.ATOM, names[n])            # noqa: E731
    s = driver.Script()
    link.one(s, im, names, 'load', [FILE])
    m = s.live()
    mods = modules(m)
    order = [mo['name'] for mo in modc.modules(FILE)]
    a = mods[order.index(MODULE)]
    found = sites(m, a, 0xf9)
    pc0, entry, arity = found[0]
    assert arity == 10 and found[1][1] == entry, found
    s.site = (a - m.load, [(p - m.load, e - m.load, ar) for p, e, ar in found])
    # the atoms the two diffs compare with: the put_atom before each
    # (an atom instruction: the atom in the low 24 bits)
    reset, close = ((pimm.ATOM, m.mem[p - 1][1] & 0xffffff) for p in (pc0, found[1][0]))
    # another atom: the one numbered after reset (the file's atoms are
    # numbered by the IPL's atom table, not as the image's)
    other = (pimm.ATOM, reset[1] + 1)
    assert other != close
    parts = [
        ('{other, 1}', [other, I(1)], None, True),
        ('{N, 1}, N the number of reset', [I(reset[1]), I(1)], None, True),
        ('{reset, 1, 2}', [reset, I(1), I(2)], None, False),
        ('{close, 1, 2}', [close, I(1), I(2)], None, False),
        ('{M, 1}', [None, I(1)], other, False),
    ]
    want = []
    for label, req, later, bound in parts:
        s.label(label)
        s.vector(0, 1, req)                     # Req in slot 0, elements in 1..
        s.newvar(5)                             # Rest
        s.cons(6, 7, ('slot', 0), ('slot', 5))  # DRS = [Req|Rest]
        # arguments: 1 CAb, 2 DRS, 3-6 F T If A, 7 A1, 8-10 AtF Att FA
        s.newvar(4)                             # CAb
        s.newvar(9)                             # A1
        s.arg(1, 4)
        s.arg(2, 6)
        s.arg(7, 9)
        for k in (3, 4, 5, 6, 8, 9, 10):
            s.newvar(10)
            s.arg(k, 10)
        s.spawn(entry - m.load, 10)
        s.run()
        s.out(9)
        want.append((label, bound))
        if later is not None:
            label += ', M = other'
            s.label(label)
            s.unifyc(1, later)
            s.run()
            s.out(9)
            want.append((label, True))
    return s, want


def check(s, m, want):
    bad = []
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    for label, bound in want:
        w = got[label][-1]
        if bound != (w[0] & ~1 == pimm.LIST):
            bad.append((label, 'A1', m.term(w) if not m.unbound(w) else None))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        n = 0
        for what, lines in s.play():
            n += len(lines)
            if what != 'load':
                print(what, len(lines), [ln for ln in lines if ln[0] in 'EO'])
        bad = check(s, s.machine, want)
        print(bad, n, s.site)
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep rdvc', PINNED)
    if not ok:
        return 1
    bad = check(s, m, want)
    if bad:
        print('pimm lockstep rdvc: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep rdvc: PASS (the guard diff at file_request_device:driver_0/10 of %s, '
          'loaded by ipl_loader:load/4, on the Bluespec core: %d trace lines identical to the '
          'reference model; A1 bound exactly when the source\'s clause commits, %d parts)'
          % (FILE, s.counts['lines'], len(want)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
