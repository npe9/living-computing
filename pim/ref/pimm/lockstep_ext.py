#!/usr/bin/env python3
"""Lockstep: a call into another module, and wait_value / wait_constant.

    python3 ref/pimm/lockstep_ext.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_ext.py compare

execute_external.  scsi_fep_file:check_send_status/6, first clause
(read from the object code, asm/kl1decomp.py):

    check_send_status(abnormal, _, _, _, A, B) :- true |
        A = [], scsi_fep_util:device_abnormal(B).
    device_abnormal(A) :- vector(A, B), vector_element(A, 1, C) |
        C = 5, set_value(2, B, 0, A).
    set_value(A, B, _, _) :- B = A | true.               (wait_value)
    otherwise.
    set_value(A, B, C, D) :- integer(A), wait(D), vector_element(D, A, E) |
        C = E, F := A + 1, set_value(F, B, C, D).

so a vector of N unbound elements comes back with element 1 = 5 and
elements 2..N-1 = 0.  Both models find the predicate from the
four-cell descriptor and the called module's predicate entry table
(TM-662; pimm.Machine.i_execute_external).  The independent check is
on the address: the instruction executed after execute_external is at
the address asm/kbndis.py's Image.external gives, which finds a
module's predicates by their head cells and names, not by the table.
(The held source bios/fep_module/fep_util.kl1 is a different text and
is not used.)

The same address check is made at every execute_external of the image
that can be entered today: the goal is started at the instruction
itself with unbound arguments (a use of the driver, not something the
machine does), 59 of the 76 sites, 18 of the 23 predicates
called.  The others' targets begin with an instruction not modelled.

wait_constant.  ipl_pool:hash_int/2 (object code):

    hash_int(-2147483648, A) :- true | A = 0.            (wait_constant)
    hash_int(A, B) :- integer(A), A >= 0 | A = B.
    hash_int(A, B) :- integer(A), -2147483648 < A, A < 0 | C := 0 - A, C = B.

Oracle: the absolute value, 0 for -2^31.

New here: execute_external, wait_value, wait_constant.

Observed fault injections into the Bluespec, 2026-11-20, each FAILed
where shown and was restored:
  external: code = off cell + 1 +    the first call: the instruction after the
    off                              predicate's first is executed
  external: table one cell low       the first call: no predicate found
  external: slot from 3 bits         the call at 259 to ipl_module:load/4: not found
  wait_value always succeeds         the first call: set_value/4 stops at once
  wait_constant always fails         hash_int(-2^31): the second clause is tried
  wait_constant steps one cell       the same: the constant is executed
  wait_constant compares 16 bits     hash_int(0): taken for -2^31

Not caught:
  - the external call taking the first pair of a slot without
    comparing keys: no call entered here goes to a predicate that is
    not the first of its slot;
  - the external call leaving the caller's guard state (the next
    clause, the noted variables) in place: no call here is made from
    a clause with either;
  - wait_value comparing values without tags: only integers meet.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402

PINNED = dict(parts=72, lines=3325, entered=59, targets=18)
SIZES = (3, 5, 2, 6)
INTS = (-(1 << 31), 0, 5, -7, -(1 << 31) + 1, (1 << 31) - 1)


def script():
    im = pimm.kbndis.Image()
    s = driver.Script()
    names = {name: n for n, name in im.sym.items()}
    css = pimm.predicate(im, 'scsi_fep_file', 'check_send_status/6')
    hint = pimm.predicate(im, 'ipl_pool', 'hash_int/2')
    # the one execute_external of check_send_status/6 and where kbndis
    # says it goes
    calls = [a for a in range(css, css + 19) if im.dis(a).startswith('execute_external')]
    assert len(calls) == 1
    mod, pred, target = im.external(calls[0])
    assert (mod, pred) == ('scsi_fep_util', 'device_abnormal/1')
    want = []

    def call(label, n, late):
        s.label(label)
        s.newvar(0)
        if late:
            s.newvar(1)
        else:
            s.vector(1, 8, [None] * n)
        s.argc(1, (pimm.ATOM, names['abnormal']))
        for a in (2, 3, 4):
            s.argc(a, (pimm.INT, 0))
        s.arg(5, 0)
        s.arg(6, 1)
        s.spawn(css, 6)
        s.run()
        m = s.live()
        ins = [int(line.split()[1]) for line in m.tr if line[0] == 'I']
        k = ins.index(calls[0])
        assert ins[k + 1] == target, (label, ins[k + 1], target)
        if late:
            s.vector(2, 8, [None] * n)
            s.unify(1, 2)
            s.run()
        s.out(0)
        s.out(1)
        want.append((label, ([], (None, 5) + (0,) * (n - 2))))

    for n in SIZES:
        call('external call, a vector of %d' % n, n, False)
    call('external call, the vector bound late', 4, True)

    def hash_int(label, v, late):
        s.label(label)
        s.newvar(0)
        s.newvar(1)
        if not late:
            s.unifyc(0, (pimm.INT, v & 0xffffffff))
        s.arg(1, 0)
        s.arg(2, 1)
        s.spawn(hint, 2)
        s.run()
        if late:
            s.unifyc(0, (pimm.INT, v & 0xffffffff))
            s.run()
        s.out(0)
        s.out(1)
        want.append((label, (v, 0 if v == -(1 << 31) else abs(v))))

    # Every execute_external of the image, entered at the instruction
    # itself with all its arguments unbound: the call must land where
    # kbndis says.  What the called predicate then does (most suspend
    # on an argument) is only compared between the two models.  Sites
    # whose target at once needs an instruction not modelled yet are
    # left out, and counted.
    sites = [a for a, (t, _v) in enumerate(im.cells)
             if t == 0x23 and im.dis(a).startswith('execute_external')]
    s.sites, s.entered, s.targets = len(sites), 0, set()
    for a in sites:
        n = im.cells[a][1] >> 16 & 255
        trial = driver.Script()
        for i in range(n):
            trial.newvar(i % 14)
            trial.arg(i + 1, i % 14)
        trial.spawn(a, n)
        trial.run()
        try:
            m = trial.live()
        except pimm.Unimplemented:
            continue
        mod, pred, target = im.external(a)
        ins = [int(line.split()[1]) for line in m.tr if line[0] == 'I']
        assert ins[0] == a and ins[1] == target, (a, ins[:2], target)
        s.label('the call at %d to %s:%s' % (a, mod, pred))
        for i in range(n):
            s.newvar(i % 14)
            s.arg(i + 1, i % 14)
        s.spawn(a, n)
        s.run()
        s.entered += 1
        s.targets.add((mod, pred))

    for v in INTS:
        hash_int('hash_int(%d)' % v, v, False)
    hash_int('hash_int, bound late to -2^31', -(1 << 31), True)
    hash_int('hash_int, bound late to -9', -9, True)
    return s, want


def check(s, m, want):
    got = {}
    for label, w in s.outs:
        got.setdefault(label, []).append(w)
    bad = []
    for label, exp in want:
        t = tuple(m.term(w) for w in got[label][-2:])
        if label.startswith('external'):
            v = m.deref(got[label][-1])
            n = m.vsize(v)
            t = (t[0], tuple(None if m.unbound(m.deref(m.taken(v[1] + i)))
                             else m.term(m.taken(v[1] + i)) for i in range(n)))
        if t != exp:
            bad.append((label, t, exp))
    return bad


def main(argv):
    s, want = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    pinned = dict(PINNED)
    entered, targets = pinned.pop('entered'), pinned.pop('targets')
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep ext', pinned)
    if not ok:
        return 1
    bad = check(s, m, want)
    if (s.entered, len(s.targets)) != (entered, targets):
        bad.append(('sites entered, targets', s.entered, len(s.targets)))
    if bad:
        print('pimm lockstep ext: FAIL, answers differ: %r' % (bad[:3],))
        return 1
    print('pimm lockstep ext: PASS (a call into another module, execute_external, and the '
          'guards wait_value and wait_constant on the Bluespec core: %d goals, %d trace '
          'lines identical to the reference model; %d of the image\'s %d external calls '
          'entered, each landing where asm/kbndis.py finds the predicate, %d predicates; '
          'the answers as the object code reads)'
          % (s.counts['parts'], s.counts['lines'], s.entered, s.sites, len(s.targets)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
