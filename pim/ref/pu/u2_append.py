#!/usr/bin/env python3
"""U2 harness: a whole KL1 program on ICOT's held microcode (ref/pu/pu.py)
against ref/pimm/pimm.py, instruction after instruction.

The program is the IPL image's own append/3 (scsi_fep_module, cells
6644-6658):

    6644  try_me_else 0, @6658          6651  get_bound_value 2,0,0
    6645  switch_on_non_list 0,0,8      6652  put_value 0,4,0
    6646  read_variable 3,0,0           6653  put_value 2,3,0
    6647  read_variable 4,0,0           6654  execute 3, append/3
    6648  put_reused_structure 0,0,2    6655  wait_nil 0,0,0
    6649  write_value 3,0,0             6656  get_value 1,2,0
    6650  write_variable 3,0,0          6657  proceed 0,0,0
                                        6658  suspend 3, append/3

called as append([a], [], Z): two reductions, 16 instructions on
pimm.py.  pimm.py runs it whole (Machine.run) and its trace (I, R, M
lines) is split at each I line.  The PU then executes the same
instructions in order, its state carried from one to the next (the
argument registers, R02, R11, the free lists, memory); per instruction
the D stage is the held decode table (setup.dispatch) and the
E stage is the held micro-routine to its end.  What is OURS:

  - the A stage: the instruction cell and its address (pu.pc) come from
    pimm.py's trace, in pimm.py's order (the firmware's own next-PC,
    R04, is compared where it writes one);
  - the goal switch before the first instruction: A0-A2 as pimm.py's
    goal_switch leaves them (the firmware's goal records are not run);
  - the free lists (check_pu.seed_lists) and the record area R10;
  - memory: pimm.py's cells (the image and the argument terms) at the
    same addresses, a flat dict.

Comparison (docs/pu_microcode_plan.md "What the same as pimm.py can
mean"), per instruction: every register pimm.py writes (R line) against
An under the address renaming of check_pu.Rename; every cell it writes
(M line) against the firmware's; pimm.py's sp against R02 where pimm.py
moves it; try_me_else's alternative (pimm.py Machine.alt) against R11
(the projection R11 = alt: INFERRED, below).

Prints one line per instruction, then a summary: instructions executed
and matched, held microinstructions executed, and the first stop.
Exit status 0 when every instruction executed matched and the furthest
point is the pinned one (PINNED: a STOP there is the reported furthest
point, not a failure); 1 on a FAIL or a moved furthest point.

    python3 ref/pu/u2_append.py [-v] [--inject NAME]

Before the program, start's held heap-top routine 204b-2052 runs (as
2028 calls it) on a parameter cell: first on five parameters against
its contract (R1f = the parameter rounded up to 16), then on pimm.py's
heap pointer (OURS) to give the run its R1f.

Before the program, the S-stage case that decides setup.S_ENTRY:
get_atom (entry 3800) on an unbound variable, on both models.  Every
write of the firmware to an argument register or a cell with no
pimm.py R / M line is a FAIL.

Observed 2026-11-26 (ref/pu/README.md "U2"): get_atom ok (3800-3801);
the boot contract ok on 5 parameters; 2 of 16 instructions executed
and matched (try_me_else 216a, switch_on_non_list on a list 3300-3301),
3 held microinstructions; the first stop is read_variable (6646) at
34a0, CNDF 7 with EM1 28 (its MAR1 = R02 is OURS).
Injections (in-process, no file edited), observed:
  s_imm_plus1     S_ENTRY entry + 1: get_atom FAILs (the cell bound
                  untagged, 00:00000456); append unchanged, 2 of 16,
                  2 words
  s_imm_row       every tag takes the TGT row (column TDPF, 4-word
                  rows): get_atom STOP at 3810 (CNDF a); append STOP at
                  3309 (MCF with EM1 06), 1 of 16 matched
  s_no_mar1       S_ENTRY without MAR1 = the last cell: get_atom STOP
                  at 3801 (MAR1 never set); append unchanged
  s_cond_true     S_ENTRY's COND forced true: nothing changes (get_atom
                  ok, 2 of 16): the COND part is NOT discriminated
  wide_em1em2     SC2F b read as EM bits 15..4: the boot reads memory
                  1e, never written: the contract FAILs on all 5
                  parameters, and the run STOPs in the boot
  cnd2_nonzero    CNDF 2 read as "not zero": the contract FAILs on all
                  5 (aligned +16, unaligned rounded down); the program
                  part is unchanged (2 of 16)
  bit0_clear_off  the bit-0-clear polarity unmodelled: STOP at 2050 on
                  all 5 parameters and in the boot
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'pimm'))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import pu as PU  # noqa: E402
import setup as SU  # noqa: E402
import check_pu  # noqa: E402
import pimm  # noqa: E402

APPEND = 6644           # scsi_fep_module append/3 in the IPL image (kbndis)
R_ALT = 0x11            # rassy's register-file 1, 'ap': try_me_else writes it (216a)
NFREE = 32
# The furthest point, pinned: (instructions of pimm.py's run, executed and
# matched, held microinstructions in them, the index of the first stop).
# Any change, forward or back, fails until the pin is updated.
PINNED = dict(steps=16, matched=2, words=3, stop=2)


def pimm_run():
    """append([a], [], Z) on pimm.py.  Returns (machine, the state at the
    first instruction, [(pc, cell, lines, after)]): for each instruction
    its trace lines and pimm.py's state after it (reg, sp, alt)."""
    m = pimm.Machine()
    c = m.alloc(2)
    m.mem[c] = (pimm.ATOM, 0x123)
    m.mem[c + 1] = pimm.NIL
    z = m.new_var()
    m.tr = []
    steps = []
    snap = {}

    def state():
        return {'reg': list(m.reg[:16]), 'sp': getattr(m, '_sp', None),
                'alt': getattr(m, 'alt', None)}

    orig = m.event

    def event(text):
        if text.startswith('I '):
            if steps:
                steps[-1][3].update(state())
            else:
                snap.update(state())
                snap['mem'] = dict(m.mem)
            f = text.split()
            steps.append((int(f[1]), (int(f[2][:2], 16), int(f[2][2:], 16)), [], {}))
        elif steps:
            if text.startswith('E') or text == 'Q':
                steps[-1][3].update(state()) if not steps[-1][3] else None
            else:
                steps[-1][2].append(text)
        orig(text)
    m.event = event
    m.run(APPEND, [(pimm.LIST, c), pimm.NIL, z])
    if not steps[-1][3]:
        steps[-1][3].update(state())
    return m, snap, steps


# start's heap-top routine (2028 calls 204b): it reads the parameter cell
# 1a0 + 4a (SC2F b immediates, RULES['sc2_wide']), rounds it up to 16
# (CNDF 2, RULES['cnd2_zero'], and the conditional return 2050) and puts
# it in R1f, rassy's 'hp'.  The cell's value comes from outside, the
# loader's memory map (PIMM.PARAM's ihp, "Initial Heap Top Pointer",
# 16'E0000000 on the held Pseudo Multi-PSI): OURS, pimm.py's own heap
# pointer for the same program, so both models' heaps start together.
PARAM_BASE = 0x1a0      # the wide immediate start's words add to (204c, 2032, 2071, ...)
PARAM_HP = PARAM_BASE + 0x4a
HEAP_TOP = 0x204b


def boot_heap_top(p, hp):
    """Run start's held 204b-2052 as a microsubroutine with the parameter
    cell = hp.  Returns the words executed; R1f is left set."""
    p.mem[PARAM_HP] = (pimm.INT, hp)
    return p.call(HEAP_TOP)


def boot_contract():
    """The contract that decides CNDF 2 (with the return's polarity):
    R1f = the parameter rounded up to 16, for aligned and unaligned
    parameters.  Returns a list of failures."""
    bad = []
    for hp in (0xe0000000, 0xe0008003, 0xe000800f, 0xe0008010, 0x1234):
        p = PU.PU()
        try:
            boot_heap_top(p, hp)
        except PU.Unmodelled as e:
            bad.append('hp %x: STOP %s' % (hp, e))
            continue
        want = (hp + 15) & ~15
        if p.r.get(0x1f, (None, None))[1] != want:
            bad.append('hp %x: R1f %s, want %x' % (hp, check_pu.fmt(p.r.get(0x1f)), want))
    return bad


def s_stage_case():
    """The case that decides setup.S_ENTRY: get_atom (a tag immediate of
    UNDF, entry 3800) on an unbound variable, on both models from the
    same state.  pimm.py binds the cell to {ATOM, atom}.  Returns a list
    of failures."""
    import mekbn
    fw = mekbn.Firmware()
    k, atom, var = 5, 0x000456, 0xe0010000
    op = fw.kl1_entries()['get_atom'][0] & 0xe0 | k
    ir = (0x23, op << 24 | atom)
    m = pimm.Machine()
    m.mem[var] = (pimm.UNDF, 0)
    m.reg[k] = (pimm.REF, var)
    pc = len(m.cells)                 # the instruction cell, just past the code
    m.cells.append(ir)
    m.i_get_atom(pc, (ir[1] >> 16) & 255, (ir[1] >> 8) & 255, ir[1] & 255, ir[1] & 0xffff)
    p = PU.PU(fw)
    p.mem[var] = (pimm.UNDF, 0)
    p.an[k] = (pimm.REF, var)
    p.ir, p.pc = ir, m.load + pc
    try:
        name = SU.decode(p)
        n = p.run(SU.setup(p, name))
    except (PU.Unmodelled, KeyError) as e:
        return ['get_atom on an unbound variable: STOP %s' % e]
    bad = []
    if p.mem[var] != m.mem[var]:
        bad.append('get_atom on an unbound variable (%d words): cell %s, pimm.py %s'
                   % (n, check_pu.fmt(p.mem[var]), check_pu.fmt(m.mem[var])))
    if p.an[k] != m.reg[k]:
        bad.append('get_atom: A%d %s, pimm.py %s' % (k, check_pu.fmt(p.an[k]), check_pu.fmt(m.reg[k])))
    return bad


def run(verbose=False):
    m, s0, steps = pimm_run()
    sbad = s_stage_case()
    print('%s  S stage: get_atom on an unbound variable (entry 3800)%s'
          % ('FAIL' if sbad else 'ok  ', ': ' + '; '.join(sbad) if sbad else ''))
    bad = boot_contract()
    print('%s  start 204b (heap top) on 5 parameters%s'
          % ('FAIL' if bad else 'ok  ', ': ' + '; '.join(bad) if bad else ''))
    p = PU.PU()
    # the boot's heap top, from pimm.py's heap pointer (OURS, above)
    try:
        nboot = boot_heap_top(p, m.hp)
    except PU.Unmodelled as e:
        print('STOP boot 204b: %s' % e)
        return {'fail': None, 'boot_fail': bad or [str(e)], 'matched': 0, 'stop': ('boot',)}, len(steps)
    # memory: every cell pimm.py holds when the first instruction is taken
    p.mem.update(s0['mem'])
    for i, w in enumerate(s0['reg']):
        p.an[i] = w                       # OURS: the goal switch
    p.r[SU.R_REC] = (0, check_pu.REC)
    check_pu.seed_lists(p, NFREE)
    rn = check_pu.Rename()
    for a in s0['mem']:
        rn.f2p[a] = rn.p2f[a] = a          # cells present in both: the identity
    out = {'done': 0, 'matched': 0, 'words': 0, 'stop': None, 'fail': None,
           'boot_words': nboot, 'boot_fail': bad}
    for k, (pc, cellv, lines, after) in enumerate(steps):
        p.ir, p.pc = cellv, m.load + pc
        name = '?'
        n0 = len(p.trace)
        an0, mem0 = dict(p.an), dict(p.mem)
        try:
            name = SU.decode(p)
            start = SU.setup(p, name)
            p.run(start)
        except (PU.Unmodelled, KeyError) as e:
            out['words'] += len(p.trace) - n0
            out['stop'] = (k, pc, name, str(e))
            print('STOP %2d %5d %-22s %s' % (k, pc, name, e))
            break
        nw = len(p.trace) - n0
        out['words'] += nw
        out['done'] += 1
        fails = compare(p, m, rn, lines, after, name, an0, mem0)
        if fails:
            out['fail'] = (k, pc, name, fails)
            print('FAIL %2d %5d %-22s %d words: %s' % (k, pc, name, nw, '; '.join(fails)))
            break
        out['matched'] += 1
        print('ok   %2d %5d %-22s %d words' % (k, pc, name, nw))
        if verbose:
            for c in p.cycles[n0:]:
                print('      %04x %016x' % (c['micro_pc'], c['microword']))
    print('%d of %d instructions executed and matched, %d held microinstructions%s'
          % (out['matched'], len(steps), out['words'],
             '' if not out['stop'] else '; first stop: instruction %d (%d %s)'
             % out['stop'][:3]))
    return out, len(steps)


def compare(p, m, rn, lines, after, name, an0, mem0):
    fails, notes = [], []
    # what the firmware wrote that pimm.py did not: an argument register or
    # a cell changed by the routine with no R / M line for it
    rl = {int(ln.split()[1]) for ln in lines if ln.startswith('R ')}
    ml = {m.load + int(ln.split()[1]) for ln in lines if ln.startswith('M ')}
    for i in sorted(set(p.an) | set(an0)):
        if p.an.get(i) != an0.get(i) and i not in rl:
            fails.append('reg %d: firmware wrote %s, pimm.py no write'
                         % (i, check_pu.fmt(p.an.get(i))))
    for a in sorted(set(p.mem) | set(mem0)):
        if p.mem.get(a) != mem0.get(a) and rn.f2p.get(a, a) not in ml:
            fails.append('heap %x: firmware wrote %s, pimm.py no write'
                         % (a, check_pu.fmt(p.mem.get(a))))
    for line in lines:
        f = line.split()
        if f[0] not in ('R', 'M'):
            continue
        i, w = int(f[1]), f[2]
        pv = (int(w[:2], 16), int(w[2:], 16))
        if f[0] == 'R':
            if not rn.same(p.an.get(i), pv, False, notes, 'reg %d' % i):
                fails.append('reg %d: firmware %s, pimm.py %s'
                             % (i, check_pu.fmt(p.an.get(i)), check_pu.fmt(pv)))
        else:
            pa = m.load + i
            fa = rn.p2f.get(pa, pa)
            if not rn.same(p.mem.get(fa), pv, False, notes, 'heap'):
                fails.append('heap %x: firmware %s, pimm.py %s'
                             % (pa, check_pu.fmt(p.mem.get(fa)), check_pu.fmt(pv)))
    base = SU.base(name)
    if base == 'try_me_else':
        # INFERRED projection: R11 (rassy's 'ap') holds the alternative
        # clause, pimm.py's alt (a cell index; the firmware an address)
        r11 = p.r.get(R_ALT)
        want = m.load + after['alt']
        if r11 is None or r11 != (pimm.REF, want):
            fails.append('R11: firmware %s, pimm.py alt {REF, %x}' % (check_pu.fmt(r11), want))
    if after.get('sp') is not None and base in ('switch_on_non_list',):
        r02 = p.r.get(SU.R_SP)
        if r02 is None or rn.f2p.get(r02[1], r02[1]) != after['sp']:
            fails.append('sp: firmware R02 %s, pimm.py %x' % (check_pu.fmt(r02), after['sp']))
    return fails


def _no_mar1():
    d = SU.deref
    SU.deref = lambda pu, w: (d(pu, w)[0], None)


def _cond_true():
    s = SU.setup

    def setup(pu, name):
        start = s(pu, name)
        if SU.FORMS.get(SU.base(name), (None,))[0] == 's_tag':
            pu.cond = True
        return start
    SU.setup = setup


INJECT = {
    's_no_mar1': _no_mar1,      # S_ENTRY's MAR1 part not loaded
    's_cond_true': _cond_true,  # S_ENTRY's COND part forced true
    's_imm_plus1': lambda: setattr(SU, 'S_ENTRY', 1),
    's_imm_row': lambda: setattr(SU, 'S_ENTRY', 'row'),
    'wide_em1em2': lambda: PU.RULES.update(sc2_wide='EM1:EM2'),
    'cnd2_nonzero': lambda: PU.RULES.update(cnd2_zero=False),
    'bit0_clear_off': lambda: PU.RULES.update(j1_bit0_clear_true=False),
}


def main(argv):
    if '--inject' in argv:
        nm = argv[argv.index('--inject') + 1]
        INJECT[nm]()
        print('injected: %s' % nm)
    out, n = run('-v' in argv)
    got = dict(steps=n, matched=out['matched'], words=out.get('words'),
               stop=out['stop'][0] if out['stop'] else None)
    if '--inject' not in argv and got != PINNED:
        print('FAIL the furthest point moved: %s, pinned %s (update PINNED)' % (got, PINNED))
        return 1
    return 1 if out['fail'] or out['boot_fail'] else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
