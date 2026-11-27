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

Also before the program: read_variable on a structure whose element is
a list pointer (LISTo, reached with every MRB off: pimm.py sp_single),
on both models (x, R02 and every memory write compared).  It is the
case that tells the dereference set-up at 34a1 (pu.DEREF_SETUP) from a
TGT column.

Observed 2026-11-27 (ref/pu/README.md "U2"): get_atom ok (3800-3801);
the list-element case ok (34a0-34a2, 3494); the boot contract ok on 5
parameters; 4 of 16 instructions executed and matched (try_me_else
216a, switch_on_non_list on a list 3300-3301, read_variable 3 and 4,
34a0-34a2 and 3494 each), 11 held microinstructions; the first stop is
put_reused_structure (6648): no S-stage set-up form.  (2026-11-26: 2 of
16, a stop at read_variable 34a0, CNDF 7 EM1 28.)
Injections (in-process, no file edited), observed:
  s_imm_plus1     S_ENTRY entry + 1: get_atom FAILs (the cell bound
                  untagged, 00:00000456); append unchanged, 2 of 16,
                  2 words
  s_imm_row       every tag takes the TGT row (column TDPF, 4-word
                  rows): get_atom STOP at 3810 (CNDF a); append STOP at
                  3309 (MCF with EM1 06), 1 of 16 matched
  s_no_mar1       S_ENTRY without MAR1 = the last cell: get_atom STOP
                  at 3801 (MAR1 never set); append unchanged (4 of 16)
  s_cond_true     S_ENTRY's COND forced true: nothing changes (get_atom
                  ok, 4 of 16): the COND part is NOT discriminated
  wide_em1em2     SC2F b read as EM bits 15..4: the boot reads memory
                  1e, never written (POISON since 2026-11-27): the
                  contract STOPs at 204f (the ALU input) on all 5
                  parameters, and the run STOPs in the boot
  cnd2_nonzero    CNDF 2 read as "not zero": the contract FAILs on all
                  5 (aligned +16, unaligned rounded down); the program
                  part is unchanged (2 of 16)
  bit0_clear_off  the bit-0-clear polarity unmodelled: STOP at 2050 on
                  all 5 parameters and in the boot
  (2026-11-27; s_imm_plus1 now also 4 of 16, 10 words, append's
  switch_on_non_list taking one word fewer; cnd2_nonzero 4 of 16)
  deref_imm_other the set-up's codes 0 (= EM2) and 1 (other) swapped:
                  the list-element case FAILs (3490/348f write
                  {VECTx, element} over the element); append STOPs at
                  3490 (ALU input from the POISON read at 34a2), 2 of 16
  deref_bits10    the code in TDAR bits 1-0: both STOP at 3491 (zero
                  word), 2 of 16
  deref_tgt_col0  the set-up read as TGT column 0: append PASSES, 4 of
                  16 (column 0 sends ATOMo to 3494 too); the list-element
                  case STOPs at 3492 (R11 never set): only that case
                  discriminates
  deref_tgt_col5  column EM1 & 7 = 5: the list case STOPs at 3498 (CNDF 7
                  EM1 34), append at 3492 (MCF with EM1 02), 2 of 16
  deref_tgt_col7  column 7: the list case STOPs at 3492, append at 3490,
                  2 of 16
  em1_28_tgt0     EM1 28 read as a case_tag_setup (column 0): both STOP
                  at 34a0 (no ALU input), 2 of 16
  absent_read_raise  a read of memory never written raises: append
                  STOPs at 34a2 (memory 123, the atom), 2 of 16; the
                  list case is unchanged (its 34a2 reads a cell)
  jmpf8_off       JMPF 8 raises again: both STOP at 34a1, 2 of 16

Also before the program (2026-11-27, third session): put_reused_structure
off append's path (reuse_cases): 3,0,2 on a LISTo held in A0, on both
models under the declared difference 'reuse' (tells the operand field y
from x), and 0,0,2 on a LISTx, which must NOT be reused in place: the
model goes on into the allocating arm and stops at 31ee (R04, pc, never
set: REUSE_SHARED_STOP).  Declared differences, as U1's: 'reuse'
(DECLARE_REUSE: the firmware reuses a single-referenced structure in
place, pimm.py never reuses) and 'indirect' (DECLARE_INDIRECT:
write_variable's element is a REF to a new cell).

Observed 2026-11-27, third session: every case above ok; 10 of 16
instructions executed and matched, 20 held microinstructions (+
put_reused_structure 31ec-31ed, write_value 31c9, write_variable
3195-3199, get_bound_value 3880, put_value 31da twice); the first stop
is execute (6654): no set-up form.  The old injections, re-run with the
new rules (the only changes from above): s_imm_plus1 now also STOPs
append at 3881 (get_bound_value entered past its first word: a zero
word), 7 of 16; s_no_mar1 FAILs append at get_bound_value (the binding
written over the wrong cell), 7 of 16; s_cond_true, cnd2_nonzero and
deref_tgt_col0 leave append at 10 of 16 (their other cases as above).
New injections, observed:
  odpf3_entry     the ODPF 3 start ignores the tag (always the entry):
                  append STOPs at 31e9 (ALU input from a read never
                  written: 31e8 read [MAR1] for a descriptor), 4 of 16;
                  both reuse cases STOP at 31e8 (MAR1 never set)
  odpf3_bits10    the code in bits 1-0 (start 31e9): append STOPs at
                  31a3 (case_branch with no set-up), 4 of 16; both reuse
                  cases STOP at 31e9
  em1_29_off      COND = the MRB is OFF: append STOPs at 31ee (R04 never
                  set, the allocating arm), 4 of 16; the LISTo case STOPs
                  there too; the LISTx case FAILs (ended at 31ed after 2
                  words: a shared list reused in place)
  sc2f1_reg       SC2F 1 read as a register R01: append and both reuse
                  cases STOP at 31ec (R01 never set), 4 of 16
  prs_operand_x   the operand taken from x, not y: append PASSES (10 of
                  16: x = y = 0); the 3,0,2 case FAILs (A3 and R02 =
                  {INT, 9}, A3's old value): only that case discriminates
  no_reuse_decl   the declaration 'reuse' off: append FAILs at
                  put_reused_structure (A0 and R02 the reused cell, not
                  pimm.py's new one), 4 of 16; the 3,0,2 case FAILs
  no_indirect_decl the declaration 'indirect' off: append FAILs at
                  write_variable (the new cell f2000000, the element a
                  REF to it, A3 the REF), 6 of 16
  gbv_mdr2_x      get_bound_value's MDR2 from x, not y: append FAILs at
                  get_bound_value (the variable cell bound to a REF to
                  itself), 7 of 16

Observed 2026-11-27, fifth session: every case above ok; 12 of 16
instructions executed and matched, 25 held microinstructions (+ execute
4cc0-4cc3, the fast path, and the second reduction's try_me_else 216a);
the first stop is switch_on_non_list (6645) on nil: the S-stage
multiway set-up for a tag other than the immediate (row entry UNKNOWN).
execute is compared on R04 (the firmware's next PC) against pimm.py's
next instruction, tag COD (seed_execute, compare_execute: the flags and
the STALE registers are OURS).  The old injections give the same
results as listed above, except that those that left append at 10 of
16 now leave it at 12 (s_cond_true, cnd2_nonzero, deref_tgt_col0,
prs_operand_x).  New injections, observed:
  cjump_same      a conditional jump tests its own word's COND: append
                  STOPs at 4cc1 (the COND 4cc1 forms is STALE: MDR1 - R0d),
                  10 of 16
  cjump_false     JMPF b taken when COND is false: STOP at 4cc5 (AS1F 3
                  with AS2F 1, not modelled), 10 of 16
  slit_pending    the slit-check flag set (an event pending): STOP at 4cc5,
                  as cjump_false, 10 of 16
  interrupt_pending  interrupt_all set: 4cc3 does not end; 4cc4 R04 :=
                  the old pc, 4cd3 calls 4cf4: STOP at 1c2c (CNDF 7 EM1 0d),
                  10 of 16, 28 words
  flags_swapped   EM1 19 read as interrupt_all, 21 as slit_check: nothing
                  changes (both clear): which flag is which is NOT
                  discriminated
  as1f2_off       AS1F 2 unmodelled: STOP at 4cc0, 10 of 16
  mcf_unknown_raise  MCF 06 / 07 raise: STOP at 4cc1 (MCF with EM1 07)
  jmpf8_flag_off  JMPF 8 on a flag condition raises: STOP at 4cc2
  cnd3_off        CNDF 3 unmodelled: nothing changes (4cc1's COND is
                  STALE before the rule is asked): NOT discriminated
  execute_mdr1    the label put in MDR1: append FAILs at execute (R04 =
                  {COD, e0008000}, MDR2's old value, for {COD, e00019f4})
  tgif3_em1       TGIF 3's tag from EM1: append FAILs at execute (R04
                  tag 21 BLT for COD)
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
PINNED = dict(steps=16, matched=12, words=25, stop=12)


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
            marks.append(len(m.tr) + 1)
        elif steps:
            if text.startswith('E') or text == 'Q':
                steps[-1][3].update(state()) if not steps[-1][3] else None
        orig(text)
    marks = []
    m.event = event
    m.run(APPEND, [(pimm.LIST, c), pimm.NIL, z])
    if not steps[-1][3]:
        steps[-1][3].update(state())
    # The R and M lines go to m.tr directly (pimm._Regs / _Mem), not
    # through event(): each instruction's lines are the slice of m.tr
    # from its I line to the next.  (Before 2026-11-27 they were taken
    # from event() alone, which never sees them: every instruction had
    # no R / M lines, and a firmware write was reported as a stray.)
    for k, st in enumerate(steps):
        end = marks[k + 1] - 1 if k + 1 < len(marks) else len(m.tr)
        st[2].extend(ln for ln in m.tr[marks[k]:end] if ln[:2] in ('R ', 'M '))
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


def read_list_element_case():
    """The case that discriminates the dereference set-up at 34a1
    (pu.DEREF_SETUP) from a TGT column: read_variable on a structure whose
    element is a list pointer (LISTo), the structure reached with every
    MRB off (pimm.py sp_single: the element is taken unmarked).  The
    4-way code 'other' runs row 3494 (x := the element, R02 + 1); TGT
    column 0, which sends an atom to 3494 too (and so passes append),
    sends LISTo to 3492.  Returns a list of failures."""
    import mekbn
    fw = mekbn.Firmware()
    x, sp, cell = 3, 0xe0020000, 0xe0030000
    op = fw.kl1_entries()['read_variable'][0] & 0xff
    ir = (0x23, op << 24 | x << 16)
    m = pimm.Machine()
    elem = (pimm.LIST, cell)
    m.mem[sp] = elem
    m.mem[cell] = (pimm.ATOM, 0x77)
    m._sp, m.sp_single = sp, True
    m.i_read_variable(0, x, 0, 0, 0)
    p = PU.PU(fw)
    p.mem[sp] = elem
    p.mem[cell] = (pimm.ATOM, 0x77)
    p.r[SU.R_SP] = (0, sp)
    check_pu.seed_lists(p, NFREE)
    p.ir, p.pc = ir, 0
    mem0 = dict(p.mem)
    try:
        name = SU.decode(p)
        n = p.run(SU.setup(p, name))
    except (PU.Unmodelled, KeyError) as e:
        return ['read_variable on a list element: STOP %s' % e]
    bad = ['read_variable on a list element: firmware wrote %x := %s, pimm.py no write'
           % (a, check_pu.fmt(p.mem[a])) for a in sorted(p.mem) if p.mem[a] != mem0.get(a)]
    if p.an.get(x) != m.reg[x]:
        bad.append('read_variable on a list element (%d words): A%d %s, pimm.py %s'
                   % (n, x, check_pu.fmt(p.an.get(x)), check_pu.fmt(m.reg[x])))
    if p.r[SU.R_SP][1] != m._sp:
        bad.append('read_variable on a list element: R02 %s, pimm.py sp %x'
                   % (check_pu.fmt(p.r[SU.R_SP]), m._sp))
    return bad


def reuse_cases():
    """put_reused_structure off append's path (the 31ec-31ed rules):
    (1) 3,0,2 on a list held directly in A0 with its MRB off: on both
    models, under the declared difference 'reuse' (A3 and R02 against
    pimm.py's reg[3] and sp; A0 untouched) -- tells the operand field y
    from x, which append (0,0,2) cannot;  (2) 0,0,2 on a list with its MRB
    ON (LISTx, shared): the contract is that it is NOT reused in place,
    so the routine must not end at 31ed; it goes on into the allocating
    arm, where the model stops at 31ee (MCF with EM1 08, not modelled):
    pinned as REUSE_SHARED_STOP.  Returns a list of failures."""
    import mekbn
    fw = mekbn.Firmware()
    op = fw.kl1_entries()['put_reused_structure'][0] & 0xff
    bad = []
    cell = 0xe0040000
    for tag, (x, y, z) in ((pimm.LIST, (3, 0, 2)), (pimm.LIST | 1, (0, 0, 2))):
        ir = (0x23, op << 24 | x << 16 | y << 8 | z)
        m = pimm.Machine()
        m.mem[cell], m.mem[cell + 1] = (pimm.ATOM, 1), pimm.NIL
        m.reg[0], m.reg[3] = (tag, cell), (pimm.INT, 9)
        m.tr = []
        m.i_put_reused_structure(0, x, y, z, ir[1] & 0xffff)
        p = PU.PU(fw)
        p.mem[cell], p.mem[cell + 1] = (pimm.ATOM, 1), pimm.NIL
        p.an[0], p.an[3] = (tag, cell), (pimm.INT, 9)
        check_pu.seed_lists(p, NFREE)
        p.ir, p.pc = ir, 0
        an0, mem0 = dict(p.an), dict(p.mem)
        what = 'put_reused_structure %d,%d,%d on %s' % (x, y, z, check_pu.fmt((tag, cell)))
        try:
            name = SU.decode(p)
            n = p.run(SU.setup(p, name))
        except (PU.Unmodelled, KeyError) as e:
            if tag & 1 and getattr(e, 'upc', None) == REUSE_SHARED_STOP:
                continue            # the shared list went on into the allocating arm
            bad.append('%s: STOP %s' % (what, e))
            continue
        if tag & 1:
            bad.append('%s: ended after %d words (%04x), a shared list reused in place'
                       % (what, n, p.trace[-1][0]))
            continue
        rn = check_pu.Rename()
        for a in mem0:
            rn.f2p[a] = rn.p2f[a] = a
        lines = [ln for ln in m.tr if ln[:2] in ('R ', 'M ')]
        after = {'sp': m.sp}
        bad += ['%s: %s' % (what, f) for f in
                compare(p, m, rn, lines, after, name, an0, mem0)]
    return bad


REUSE_SHARED_STOP = 0x31ee

# execute (6654, entry 4cc0; U2 2026-11-27, fifth session).  What the
# harness gives it, OURS:
#   - the hardware flags pu.FLAG_CONDS tests: no asynchronous event
#     pending (slit_check) and no interrupt (interrupt_all), as on one PE
#     with no GC request, message or signal (pimm.py has none either);
#   - R0d, W1f and R04 as STALE (pu.STALE: values the harness does not
#     know).  R0d is a scratch register (47 writers in image 2, none on
#     the path run before execute); W1f is written at boot (20a8, W1f := 0,
#     read not run) and by proceed's 21a1-21fe; R04, rassy's 'pc', is the
#     A stage's program counter, which the harness does not model.  On
#     the fast path (4cc0-4cc3) R0d and W1f feed only 4cc1's compare and
#     XR, which no word tests or keeps (cjump_time 'prev'), and R04's old
#     value goes to W14 (not compared): a STALE value reaching an
#     argument register, a cell, an address or a tested COND would STOP
#     or FAIL the run, so their values are shown not to matter here.
EXECUTE_FLAGS = {'slit_check': False, 'interrupt_all': False}
EXECUTE_STALE = (('R', 0x0d), ('W', 0x1f), ('R', 0x04))
R_PC = 0x04             # rassy's second bank 4, 'pc'
COD = 0x26              # kbn tag COD (the code-address tag 4cc2 stamps from EM2)


def seed_execute(p):
    p.flags.update(EXECUTE_FLAGS)
    for f, n in EXECUTE_STALE:
        {'R': p.r, 'W': p.w}[f][n] = PU.STALE


def compare_execute(p, m, after):
    """execute: the firmware's next PC, R04, against pimm.py's next
    instruction (the I line after execute's).  The tag must be COD (4cc2
    stamps EM2 under TGIF 3, RULES['tgif3_tag']; the slow-path words
    4cc4, 4ccf stamp COD on R04 too).  pimm.py's i_execute also counts a
    reduction and clears alt; neither has a firmware register compared
    here."""
    want = after.get('next_pc')
    r04 = p.r.get(R_PC)
    if want is None:
        return ['execute: no next instruction in pimm.py\'s trace']
    if PU.is_stale(r04) or r04 is None or r04 != (COD, m.load + want):
        return ['R04 (pc): firmware %s, pimm.py next instruction {COD, %x}'
                % (r04 if PU.is_stale(r04) or r04 is None else check_pu.fmt(r04),
                   m.load + want)]
    return []


def run(verbose=False):
    m, s0, steps = pimm_run()
    rbad = reuse_cases()
    print('%s  put_reused_structure off the path: 3,0,2 on LISTo (reused), 0,0,2 on'
          ' LISTx (not reused)%s' % ('FAIL' if rbad else 'ok  ',
                                     ': ' + '; '.join(rbad) if rbad else ''))
    sbad = s_stage_case()
    print('%s  S stage: get_atom on an unbound variable (entry 3800)%s'
          % ('FAIL' if sbad else 'ok  ', ': ' + '; '.join(sbad) if sbad else ''))
    lbad = read_list_element_case()
    print('%s  read_variable on a list element (the 34a1 set-up)%s'
          % ('FAIL' if lbad else 'ok  ', ': ' + '; '.join(lbad) if lbad else ''))
    bad = boot_contract()
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
    seed_execute(p)
    rn = check_pu.Rename()
    for a in s0['mem']:
        rn.f2p[a] = rn.p2f[a] = a          # cells present in both: the identity
    out = {'done': 0, 'matched': 0, 'words': 0, 'stop': None, 'fail': None,
           'boot_words': nboot, 'boot_fail': bad + sbad + lbad + rbad}
    for k, (pc, cellv, lines, after) in enumerate(steps):
        p.ir, p.pc = cellv, m.load + pc
        after['next_pc'] = steps[k + 1][0] if k + 1 < len(steps) else None
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
    base = SU.base(name)
    covered = set()         # firmware cells a declared difference accounts for
    if base == 'put_reused_structure' and DECLARE_REUSE:
        fails += declare_reuse(p, rn, lines, an0, mem0)
    if base in ('write_variable', 'write_marked_variable') and DECLARE_INDIRECT:
        covered |= declare_indirect(p, m, rn, lines, mem0, notes)
    # what the firmware wrote that pimm.py did not: an argument register or
    # a cell changed by the routine with no R / M line for it
    rl = {int(ln.split()[1]) for ln in lines if ln.startswith('R ')}
    ml = {m.load + int(ln.split()[1]) for ln in lines if ln.startswith('M ')}
    for i in sorted(set(p.an) | set(an0)):
        if p.an.get(i) != an0.get(i) and i not in rl:
            fails.append('reg %d: firmware wrote %s, pimm.py no write'
                         % (i, check_pu.fmt(p.an.get(i))))
    for a in sorted(set(p.mem) | set(mem0)):
        if p.mem.get(a) != mem0.get(a) and rn.f2p.get(a, a) not in ml and a not in covered:
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
    if base == 'execute':
        fails += compare_execute(p, m, after)
    if base == 'try_me_else':
        # INFERRED projection: R11 (rassy's 'ap') holds the alternative
        # clause, pimm.py's alt (a cell index; the firmware an address)
        r11 = p.r.get(R_ALT)
        want = m.load + after['alt']
        if r11 is None or r11 != (pimm.REF, want):
            fails.append('R11: firmware %s, pimm.py alt {REF, %x}' % (check_pu.fmt(r11), want))
    if after.get('sp') is not None and base in ('switch_on_non_list', 'read_variable',
                                                'put_reused_structure'):
        r02 = p.r.get(SU.R_SP)
        if r02 is None or rn.f2p.get(r02[1], r02[1]) != after['sp']:
            fails.append('sp: firmware R02 %s, pimm.py %x' % (check_pu.fmt(r02), after['sp']))
    return fails


# The declared difference 'reuse' (as U1's 'indirect' and 'mrb' in
# check_pu.py): the firmware reuses a single-referenced structure in
# place (31ec-31ed: x and R02 := the dereferenced pointer, no cell
# written, no free list popped), where pimm.py never reuses
# (i_put_reused_structure: z new cells, "no reference counts here, so
# nothing is ever reused"; pimm_semantics.md).  Declared only when the
# firmware's x holds the source structure's own address; then pimm.py's
# z new cells are paired with the z reused cells under the renaming, so
# that what write_* put in them later is compared cell by cell.  A
# firmware that allocated is compared with no declaration.
DECLARE_REUSE = True


def declare_reuse(p, rn, lines, an0, mem0):
    x, y, z = p.ir_field('x'), p.ir_field('y'), p.ir_field('z')
    w = an0.get(y)
    while w is not None and w[0] & ~1 == pimm.REF:
        w = mem0.get(w[1])
    fv = p.an.get(x)
    if w is None or fv is None or fv[1] != w[1]:
        return []
    got = [ln.split()[2] for ln in lines if ln.startswith('R %d ' % x)]
    if len(got) != 1:
        return ['reuse: pimm.py wrote reg %d %d times' % (x, len(got))]
    a = int(got[0][2:], 16)
    for i in range(z):
        fa, pa = w[1] + i, a + i
        for k in (rn.p2f.pop(pa, None),):
            if k is not None:
                rn.f2p.pop(k, None)
        old = rn.f2p.pop(fa, None)
        if old is not None:
            rn.p2f.pop(old, None)
        rn.f2p[fa], rn.p2f[pa] = pa, fa
    return []


# The declared difference 'indirect' (U1's, check_pu.py; README "What
# the held words answered" item 1): write_variable (3195-3199) puts in
# the structure element a {REF, c} to a NEW cell c, popped from the
# one-cell list and made UNDF, and gives x {REF, c}; pimm.py makes the
# element itself the variable.  The same term after dereference.
# Declared per M line of pimm.py whose firmware cell holds a REF to a
# cell the firmware wrote in this instruction (a free-list cell: the
# seeded lists are in memory before) holding pimm.py's value:
# that new cell is paired with pimm.py's cell, and the element written
# with the REF is accounted for.
DECLARE_INDIRECT = True


def declare_indirect(p, m, rn, lines, mem0, notes):
    covered = set()
    for ln in lines:
        f = ln.split()
        if f[0] != 'M':
            continue
        pa = m.load + int(f[1])
        pv = (int(f[2][:2], 16), int(f[2][2:], 16))
        fa = rn.p2f.get(pa, pa)
        fv = p.mem.get(fa)
        if not fv or fv[0] & ~1 != pimm.REF or fv[1] in rn.f2p \
                or p.mem.get(fv[1]) == mem0.get(fv[1]) or p.mem.get(fv[1]) != pv:
            continue
        notes.append('heap %x: firmware {REF, new cell %x}, pimm.py the cell itself' % (pa, fv[1]))
        rn.f2p.pop(fa, None)
        rn.p2f.pop(pa, None)
        rn.pair(fv[1], pa)
        covered.add(fa)
    return covered


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
    # U2 read_variable (2026-11-27): the dereference multiway set-up at 34a1
    'deref_imm_other': lambda: PU.DEREF_CODE.update(imm=1, other=0),
    'deref_bits10': lambda: setattr(PU, 'DEREF_SHIFT', 0),
    'deref_tgt_col0': lambda: (setattr(PU, 'DEREF_TGT_COLUMN', 0), setattr(PU, 'DEREF_SHIFT', 0)),
    'deref_tgt_col5': lambda: (setattr(PU, 'DEREF_TGT_COLUMN', 5), setattr(PU, 'DEREF_SHIFT', 0)),
    'deref_tgt_col7': lambda: (setattr(PU, 'DEREF_TGT_COLUMN', 7), setattr(PU, 'DEREF_SHIFT', 0)),
    'em1_28_tgt0': lambda: (PU.COND_UNKNOWN.clear(), PU.TGT_COLUMN.update({0x28: 0})),
    'absent_read_raise': lambda: PU.RULES.update(absent_read_poison=False),
    'jmpf8_off': lambda: PU.RULES.update(jmpf8_setup=False),
    # U2 put_reused_structure .. put_value (2026-11-27, third session)
    'odpf3_entry': lambda: setattr(SU, 'ODPF3_SHIFT', None),
    'odpf3_bits10': lambda: setattr(SU, 'ODPF3_SHIFT', 0),
    'em1_29_off': lambda: PU.RULES.update(em1_29_mrb='off'),
    'sc2f1_reg': lambda: PU.RULES.update(sc2f1_ir=None),
    'prs_operand_x': lambda: SU.FORMS.update(put_reused_structure=('s_odpf3', 'x')),
    'no_reuse_decl': lambda: globals().update(DECLARE_REUSE=False),
    'no_indirect_decl': lambda: globals().update(DECLARE_INDIRECT=False),
    'gbv_mdr2_x': lambda: SU.S_CONST.update(get_bound_value='x'),
    # U2 execute (2026-11-27, fifth session)
    'cjump_same': lambda: PU.RULES.update(cjump_time='same'),
    'cjump_false': lambda: PU.CJUMP_TAKEN_ON.update({0xb: False}),
    'slit_pending': lambda: EXECUTE_FLAGS.update(slit_check=True),
    'interrupt_pending': lambda: EXECUTE_FLAGS.update(interrupt_all=True),
    'flags_swapped': lambda: PU.FLAG_CONDS.update({0x19: 'interrupt_all', 0x21: 'slit_check'}),
    'as1f2_off': lambda: PU.RULES.update(as1f2_yr=False),
    'mcf_unknown_raise': lambda: PU.MCF_UNKNOWN.clear(),
    'jmpf8_flag_off': lambda: PU.RULES.update(jmpf8_flag=False),
    'cnd3_off': lambda: PU.RULES.update(cnd3_sign=False),
    'execute_mdr1': lambda: SU.LABEL_ODSF.update({2: 'MDR1'}),
    'tgif3_em1': lambda: PU.RULES.update(tgif3_tag='EM1'),
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
