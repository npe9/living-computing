#!/usr/bin/env python3
"""Lockstep: the guard instruction multiply, at its sites in the kernel's
scsi_fep module.

    python3 ref/pimm/lockstep_gmul.py --script FILE     write the script
    sim_pimm_driver | python3 ref/pimm/lockstep_gmul.py compare
    python3 ref/pimm/lockstep_gmul.py --reference       the reference alone

multiply(Integer1, Integer2, ^NewInteger), 23:F6 r_r_r
(library/assembler/inst_tab.kl1:209; directions iio,
library/compiler/blt.kl1:29-30): "Fail, Exception: if either ... is
not an integer; if an overflow occurs" (PIMOS manual,
e-builtin.tex:268-283); as a guard it fails.  It was the first stop of
pim:go/4 with the device (rung S0, docs/scsi_plan.md), in
scsi:check_lun/4, which is in the 96,474-word pimm_bios360E.sav.

The sites here are in the smaller file that holds the module whose
code the kernel's FEP link uses: pimm_patch_scsifep360E.sav (7,139
words, one module, scsi_fep, the four guard multiplies of the file),
loaded by ipl_loader:load/4 as lockstep_xmod.py loads its file (the
link is abnormal: the file calls modules it does not hold).  The
source is bios/fep_module/scsi_fep.kl1:
  send_packet1/8, lines 313-319 and 334-349:
      L >= 0, Pos1 := Pos + ~(((L+3)/4)*4), Size >= Pos1 | ...
  send_packet3/10, lines 394-416:
      L1 := ((L+3)/4)*4 - Pos, Size - 8 >= L1 | ...
The predicate of each site is the PREDH head before it (arity 8 and
10), and a goal is started at its first instruction.  Size is left
unbound, so each goal computes the product and suspends on Size (both
bodies call modules the file does not hold, which the lockstep cannot
play); a send_packet1 goal is then given a Size that commits no clause
(less than Pos1 and not the buffer's length), and fails.

Oracle, arithmetic written here, not either model: every multiply
executed writes its destination register with ((L+3)/4)*4, the
quotient truncated towards zero (as the guard divide, lockstep_body.py);
the trace's R line after each multiply's I line is checked.  Operands:
L = 0, 1, 3, 4, 5, 2147483640 (a product of 31 bits) in send_packet1;
L = -11, -5, -2147483645 (negative operands and a large negative
product) in send_packet3.

The predicate send_packet1/8 begins by spilling registers: save r, POS
and restore r, POS (23:19, 23:1A r_c16, inst_tab.kl1:23, 25; the
compiler's spill, library/compiler/regass.kl1 outputCode/6; TM-1044's
save(Reg, POS)/restore(POS, Reg) on "work memory", as listed in
docs/literature_gaps.md), so they are run here too: each send_packet1
part saves to slots 0, 32 and 33 and restores from slot 0.  Checked:
the V line after each save names its slot, and the R line after each
restore is the slot's last V value.

Observed fault injections into the Bluespec (bsv/PimmStages.bsv), each
run alone (bsv/run_pimm_lockstep.sh gmul) and restored from a copy,
2026-11-23 (first difference in each case: part 1, send_packet1 Pos 16
L 0):
  the product written + 1 (gMultiplied)   line 97: R 20 0000000001 for
                                          R 20 0000000000
  the product written to r[x]             line 97: R 18 for R 20
  save to slot POS + 1                    line 55: V 1 for V 0
  restore leaves the register as it is    line 61: R 0 0200000000 for
                                          R 0 07e005d6f6
NOT caught: restore always from slot 0 (every restore here is from
slot 0).

NOT run: an overflow (no site of this file can overflow: |((L+3)/4)*4|
is at most |L+3|, and an overflow of L+3 fails the add first), a
non-integer operand and an unbound one (the guards before it, L >= 0
and the add, take those first).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import driver  # noqa: E402
import pimm  # noqa: E402
import lockstep_link as link  # noqa: E402

PINNED = dict(parts=16, lines=2065776)
FILE = 'pimm_patch_scsifep360E.sav'
I = lambda v: (pimm.INT, v & 0xffffffff)           # noqa: E731
NIL = (pimm.ATOM, 0)
PACKET1 = [(16, 0), (16, 1), (16, 3), (16, 4), (16, 5), (0, 2147483640)]   # Pos, L
PACKET3 = [(-11, 0), (-5, 4), (-2147483645, 8)]                           # L, Pos


def product(L):
    q = abs(L + 3) // 4
    return (-q if L + 3 < 0 else q) * 4


def sites(m):
    """(pc, its predicate's first instruction, the arity) of each guard
    multiply in the loaded modules, ascending."""
    out = []
    for a in sorted(a for a, c in m.mem.items()
                    if a >= m.load + 0x8000 and c[0] == pimm.CDESC and c[1] >> 24 == 6):
        n, gc = m.mem[a][1] & 0xffffff, m.mem[a + 1][1]
        for pc in range(a + 2 + gc, a + n + 1):
            c = m.mem.get(pc)
            if c and c[0] == 0x23 and c[1] >> 24 == 0xf6:
                h = pc
                while m.mem[h][0] != pimm.PREDH:
                    h -= 1
                out.append((pc, h + 2, m.mem[h][1] >> 24))
    return out


def script():
    im = pimm.kbndis.Image()
    names = {name: n for n, name in im.sym.items()}
    s = driver.Script()
    link.one(s, im, names, 'load', [FILE])
    m = s.live()
    found = sites(m)
    entry = {ar: e - m.load for _pc, e, ar in found}
    want = []
    for pos, L in PACKET1:
        label = 'send_packet1, Pos %d, L %d' % (pos, L)
        s.label(label)
        s.string(0, 8, [0] * 16)               # Buffer
        s.string(1, 8, [1, 2, 3])              # D
        s.vector(2, 3, [I(L), ('slot', 1)])    # {L, D}
        s.cons(5, 6, ('slot', 2), NIL)         # [{L, D}]
        for i in (8, 9, 10, 11):
            s.newvar(i)                        # Size, Send, Tail, Result
        for a, sl in ((1, 8), (2, 0), (5, 5), (6, 9), (7, 10), (8, 11)):
            s.arg(a, sl)
        s.argc(3, I(pos))
        s.argc(4, I(16))                       # DevID
        s.spawn(entry[8], 8)
        s.run()                                # suspends on Size
        want.append((label, product(L), 'E susp'))
        label += ', Size 15'
        s.label(label)
        s.unifyc(8, I(15))
        s.run()                                # no clause commits
        want.append((label, product(L), 'E fail'))
    for L, pos in PACKET3:
        label = 'send_packet3, L %d, Pos %d' % (L, pos)
        s.label(label)
        s.string(0, 8, [0] * 16)
        s.string(1, 8, [1, 2, 3])
        for i in (8, 9, 10, 11):
            s.newvar(i)                        # Size, Send, Tail, Result
        for a, sl in ((1, 8), (2, 0), (6, 1), (8, 9), (9, 10), (10, 11)):
            s.arg(a, sl)
        s.argc(3, I(16))
        s.argc(4, I(L))
        s.argc(5, I(pos))
        s.argc(7, NIL)                         # Data
        s.spawn(entry[10], 10)
        s.run()                                # suspends on Size
        want.append((label, product(L), 'E susp'))
    s.found = [(pc - m.load, e - m.load, ar) for pc, e, ar in found]
    return s, want


def check(s, parts, want):
    bad = []
    if sorted(ar for _p, _e, ar in s.found) != [8, 8, 10, 10]:
        bad.append(('sites', s.found))
    for label, prod, end in want:
        lines = parts.get(label, [])
        got = []
        for k, ln in enumerate(lines):
            if ln.startswith('I ') and ln.split()[2][:4] == '23f6':
                z = int(ln.split()[2][-2:], 16)
                nx = lines[k + 1].split() if k + 1 < len(lines) else []
                got.append(nx[:2] == ['R', str(z)] and int(nx[2], 16))
        if not got or any(g != (0x00 << 32 | prod & 0xffffffff) for g in got):
            bad.append((label, 'products', got, prod & 0xffffffff))
        if end not in lines:
            bad.append((label, 'no %s' % end))
        # restore gives the register what save put in the slot
        slots, saves, restores = {}, 0, 0
        for k, ln in enumerate(lines):
            f = ln.split()
            if f[0] == 'V':
                slots[f[1]] = f[2]
            elif f[0] == 'I' and f[2][:4] in ('2319', '231a'):
                r, pos = int(f[2][4:6], 16), str(int(f[2][6:], 16))
                if f[2][:4] == '2319':
                    saves += 1
                    ok = lines[k + 1].split() == ['V', pos, None] or (
                        lines[k + 1].split()[:2] == ['V', pos])
                else:
                    restores += 1
                    ok = lines[k + 1].split() == ['R', str(r), slots.get(pos)]
                if not ok:
                    bad.append((label, 'save/restore', ln, lines[k + 1]))
        if label.startswith('send_packet1') and (saves < 1 or restores < 1):
            bad.append((label, 'saves and restores', saves, restores))
    return bad


def main(argv):
    s, want = script()
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
        bad = check(s, kept, want)
        print(bad, n, s.found, [(k, len(v)) for k, v in kept.items()])
        return 1 if bad else 0
    ok, m = driver.compare(s, sys.stdin, 'pimm lockstep gmul', PINNED)
    if not ok:
        return 1
    bad = check(s, kept, want)
    if bad:
        print('pimm lockstep gmul: FAIL %r' % (bad[:3],))
        return 1
    print('pimm lockstep gmul: PASS (the guard multiply at the four sites of scsi_fep in %s, '
          'loaded by ipl_loader:load/4, on the Bluespec core: %d trace lines identical to the '
          'reference model; every product ((L+3)/4)*4 as written here, %d operands, negative and '
          'of 31 bits)' % (FILE, s.counts['lines'], len(PACKET1) + len(PACKET3)))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
