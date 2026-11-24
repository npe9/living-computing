#!/usr/bin/env python3
"""Lockstep: write_integer with a negative operand (bit 23 a sign).

    python3 ref/pimm/lockstep_wint.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_wint.py compare
    python3 ref/pimm/lockstep_wint.py --reference       the reference alone

write_integer (23:21, c24): the integer in the low 24 bits is SIGNED.
The PIMOS assembler writes an integer constant in -2^23..2^23-1
(16#"FF800000"..16#"007FFFFF") in this one-cell c24 form, masked with
16#"00FFFFFF", and any other in the two-cell c40 form (library/
assembler/klb_opr.kl1 p(c24, ..) lines 50-54, p(c40, ..) 60-81).  It
was the stop of pim:go/4 with the device (rung S0): scsi_fep's
check_data_size1/6 (bios/fep_module/scsi_fep.kl1:429-433):

    check_data_size1(E, Msg, I, N, L, Data) :- integer(E) |
        L = [-1|NL], Data = [{-1, E}|NData],
        check_data_size(Msg, ~(I+1), N, NL, NData).

compiled as put_list; write_integer 16777215; ... put_vector 2;
write_integer 16777215; write_value (asm/unlsav.py --disasm).

The site here: the same predicate in pimm_patch_scsifep360E.sav, loaded
by ipl_loader:load/4 exactly as lockstep_gmul.py loads it; the first
write_integer whose operand has bit 23 set, its predicate's entry.  A
goal check_data_size1(42, Msg, 0, 1, L, Data) with Msg, L, Data the
bench's variables: the clause commits (42 is an integer), L = [-1|_]
and Data = [{-1, 42}|_] (the oracle: the source above), and
check_data_size waits for Msg.  Then a goal with E = 0xffffff written
as an integer of the bench (16777215, not a sign): L's head is still
-1 and Data's {-1, 16777215}.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv), each
run alone (bsv/run_pimm_lockstep.sh wint) and restored from a copy,
2026-11-24:
  bit 23 not a sign (zero-extended)  E = 42, line 32: M 00ffffffff
                                     (reference) for 0000ffffff
NOT caught: a sign taken from bit 15 (the only real operand, -1, is
-1 either way); positive operands are lockstep_modc.py's (35).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_link as link  # noqa: E402

PINNED = dict(parts=3, lines=2064373)
FILE = 'pimm_patch_scsifep360E.sav'
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
ES = (42, 0xffffff)


def site(m):
    """(pc, entry, arity) of the first write_integer with bit 23 set in
    the loaded modules."""
    for a in sorted(a for a, c in m.mem.items()
                    if a >= m.load + 0x8000 and c[0] == pimm.CDESC and c[1] >> 24 == 6):
        n, gc = m.mem[a][1] & 0xffffff, m.mem[a + 1][1]
        for pc in range(a + 2 + gc, a + n + 1):
            c = m.mem.get(pc)
            if c and c[0] == 0x23 and c[1] >> 24 == 0x21 and c[1] & 0x800000:
                h = pc
                while m.mem[h][0] != pimm.PREDH:
                    h -= 1
                return pc, h + 2, m.mem[h][1] >> 24
    return None


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    link.one(s, im, names, 'load', [FILE])
    m = s.live()
    pc, entry, ar = site(m)
    assert ar == 6, ar
    s.site, s.entry = pc - m.load, entry - m.load
    for k, e in enumerate(ES):
        s.label('E = %d' % e)
        b = 3 * k
        for i in range(3):
            s.newvar(b + i)                    # Msg, L, Data
        s.argc(1, I(e))
        s.arg(2, b)
        s.argc(3, I(0))
        s.argc(4, I(1))
        s.arg(5, b + 1)
        s.arg(6, b + 2)
        s.spawn(s.entry, 6)
        s.run()                                # waits for Msg
        s.out(b + 1)
        s.out(b + 2)
    return s


def check(s, m, outs):
    bad = []
    for k, e in enumerate(ES):
        got = [m.term(w) for lab, w in outs if lab == 'E = %d' % e]
        if len(got) != 2:
            bad.append(('E = %d' % e, 'outs', got))
            continue
        L, D = got
        # pimm.Machine.term gives a list with its unbound tail dropped
        ok = isinstance(L, list) and L[:1] == [-1] and isinstance(D, list) and D[:1] == [(-1, e)]
        if not ok:
            bad.append(('E = %d' % e, L, D))
    return bad


def main(argv):
    s = script()
    if '--script' in argv:
        s.write(argv[argv.index('--script') + 1])
        return 0
    if '--reference' in argv:
        n = 0
        for what, lines in s.play():
            n += len(lines)
            if what == 'load':
                lines.clear()
        bad = check(s, s.machine, s.outs)
        print(bad, n, [(l, s.machine.term(w)) for l, w in s.outs if l.startswith('E =')])
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep wint', PINNED)
    if not ok:
        return 1
    bad = check(s, m, s.outs)
    if bad:
        print('pimm lockstep wint: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep wint: PASS (write_integer -1 at scsi_fep:check_data_size1/6 in %s, '
          'loaded by ipl_loader:load/4, on the Bluespec core: %d trace lines identical to the '
          'reference model; L = [-1|_] and Data = [{-1, E}|_] as the source writes them)'
          % (FILE, s.counts['lines']))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
