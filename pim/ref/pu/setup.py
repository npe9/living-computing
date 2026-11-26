"""The D/A/R/S stand-in: what the PU's non-microcoded stages leave in the
E stage's registers before the first microinstruction of a KL1-B
instruction runs (docs/pu_microcode_plan.md; M92 p.428, thesis
pp.125-129).

On the machine these stages are driven by the decode entry's nano-code
(Nakashima Fig. 3-22: ACF address calculation, DFF fetch kind, OS1F/OS2F
set-up sources, ODSF set-up destination, EMO1/EMO2 emits, TDPF the tag
branch set-up; docs/psi_microword.md 3a).  The held entries carry those
bits (asm/psdpim.py reads the table), but only some of their meanings
are decoded.  So:

  NANO_ODPF1 (INFERRED, generic): an entry whose nano-code field at
  Fig. 3-22's ODPF position is 1 pops a free list: the S stage loads the
  head register R(10 | EMO1) into MAR2 when ODSF is 0 and into MAR1 when
  ODSF is 1.  Fitted on set_variable (318b reads [MAR2], EMO1 9, ODSF 0)
  and put_list (31d0 reads [MAR1], EMO1 a, ODSF 1); predicted and met by
  every other ODPF 1 entry run here: put_variable, put_vector_1/2,
  write_variable.  Of the whole table, 14 entries have ODPF 1; read (not
  run), the others fit too: set_list, the *_marked_variable forms (pops
  through the MAR ODSF names), proceed (EMO1 0, ODSF 1: MAR1 := R10, the
  finished goal's record, which 216c-216d push on the R1b list,
  pseudo_pimm_microcode.md section 18), collect_list (EMO1 a, ODSF 2:
  the old R1a head is what 30a8 writes from MDR2, so ODSF 2 would be
  MDR2).  rassy's register-file names (binary_reverse_engineering.md
  section 3: 0 cgp, 9 fvp, 10 flp, 11 fgp, 15 hp) name R10, R19, R1a,
  R1b, R1f as the current goal pointer and the free variable, list and
  goal-record pointers and the heap pointer, as M92 p.427 lists them.
  Only ODSF 0 and 1 are run; any other raises.

  EMO2_TAG (MEASURED, pseudo_pimm_microcode.md section 3): the tag a
  constant operand carries is the entry's tag immediate (EMO2): INTo for
  the *_integer forms, ATOMo for the *_atom forms.

  FORMS (OURS): which operand goes where, per operand form, from
  pimm.py's operand readings (docs/pimm_semantics.md).  The A-stage
  address of a goal argument is R10 + argument number (R10: the goal
  record being built, pseudo_pimm_microcode.md section 18), of a
  structure element R02 (the structure pointer).
"""
import mekbn

R_REC, R_SP = 0x10, 0x02


def sx16(v):
    v &= 0xffff
    return v - 0x10000 if v & 0x8000 else v


def sx24(v):
    v &= 0xffffff
    return v - 0x1000000 if v & 0x800000 else v


NANO = {'ACF': (49, 47), 'DFF': (45, 44), 'ODPF': (35, 33), 'OS1F': (32, 30),
        'OS2F': (29, 27), 'ODSF': (26, 25), 'TDPF': (22, 20), 'EMO1': (19, 16),
        'EMO2': (15, 10), 'MAF': (9, 0)}
NANO_ODPF1 = True       # switch for injections
ODSF_MAR = {0: 'MAR2', 1: 'MAR1'}   # NANO_ODPF1's destination (check_pu.py injects a swap)


def nano(fw, idx):
    """The decode entry as one 56-bit number: first word's low 16 bits,
    second word's tag byte and value (Fig. 3-22 right-aligned on it)."""
    (v1, _), (v2, t2) = fw.entry(idx)
    n = (v1 & 0xffff) << 40 | t2 << 32 | v2
    return {k: n >> lo & ((1 << (hi - lo + 1)) - 1) for k, (hi, lo) in NANO.items()}


def base(name):
    """pimm.py's method name for a decode-table name."""
    if name.startswith('put_vector_N['):
        return 'put_vector_%d' % int(name[13:15], 16)
    return name.split('[')[0]


# operand form: (MDR1 source, MAR1 source)
#   MDR1: 'y' / 'x' register, 'c16' / 'c24' / 'a24' a constant (tag EMO2)
#   MAR1: 'arg_x' R10 + x, 'arg_op' R10 + the opcode's low four bits, 'sp' R02
FORMS = {
    'set_value': ('y', 'arg_x'), 'set_integer': ('c16', 'arg_x'),
    'set_atom': ('a24', 'arg_op'), 'set_nil': (None, 'arg_x'),
    'set_variable': (None, 'arg_x'), 'set_marked_variable': (None, 'arg_x'),
    'write_marked_variable': (None, None), 'put_marked_variable': (None, None),
    'put_value': ('y', None), 'put_integer': ('c16', None), 'put_atom': ('a24', None),
    'put_nil': (None, None), 'put_list': (None, None), 'put_variable': (None, None),
    'put_vector_0': (None, None), 'put_vector_1': (None, None), 'put_vector_2': (None, None),
    'write_value': ('x', 'sp'), 'write_integer': ('c24', 'sp'), 'write_atom': ('a24', 'sp'),
    'write_nil': (None, 'sp'), 'write_variable': (None, None),
}


def setup(pu, name):
    """Load the E-stage registers for the instruction pu.ir; return the
    start microaddress."""
    fw = pu.fw
    idx, start, imm = fw.kl1_entries()[name]
    nc = nano(fw, idx)
    form = FORMS.get(base(name))
    if form is None:
        raise KeyError('no set-up form for %s' % name)
    t, v = pu.ir
    mdr, mar = form
    if mdr in ('x', 'y'):
        pu.wr[mekbn.MDR1] = pu.an[pu.ir_field(mdr)]
    elif mdr:
        val = {'c16': sx16(v), 'c24': sx24(v), 'a24': v & 0xffffff}[mdr]
        pu.wr[mekbn.MDR1] = (nc['EMO2'], val & 0xffffffff)
    if mar:
        rec, sp = pu.r.get(R_REC), pu.r.get(R_SP)
        a = {'arg_x': lambda: rec[1] + pu.ir_field('x'),
             'arg_op': lambda: rec[1] + (pu.ir_field('op') & 15),
             'sp': lambda: sp[1]}[mar]()
        pu.wr[mekbn.MAR1] = (0, a & 0xffffffff)
    if nc['ODPF'] == 1 and NANO_ODPF1:
        head = pu.r[0x10 | nc['EMO1']]
        reg = {'MAR1': mekbn.MAR1, 'MAR2': mekbn.MAR2}.get(ODSF_MAR.get(nc['ODSF']))
        if reg is None:
            raise KeyError('ODPF 1 with ODSF %d: not run here' % nc['ODSF'])
        pu.wr[reg] = (0, head[1])
    return start
