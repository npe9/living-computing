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
    # U2 (2026-11-26): try_me_else's label, an A-stage address
    # calculation (nano-code DFF 1): MDR1 = the label's absolute address,
    # pc + 2 + c16 as pimm.py's i_try_me_else.  OURS (the A stage).
    'try_me_else': ('label', None),
    # read_variable: the structure element's address, R02 (sp), in MAR1,
    # as write_value's; 34a0 reads [MAR1] itself.  OURS, with support
    # (ref/pu/README.md "U2"): OS1F 6 is source (6), the structure
    # pointer, in the thesis's numbered list of S-stage set-up sources
    # (printed p.128), whose (4) WR fits OS1F 4 in every ODPF 1 entry run;
    # not fitted (read_atom has OS1F 5).  DFF 2's fetch is not used on
    # the path run: 34a0 overwrites MDR1 before anything reads it.
    # EXECUTED in append (read_variable 3 and 4 match pimm.py).
    'read_variable': (None, 'sp'),
    # the tag-test entries (entries with a tag immediate): the S stage
    # below.  (form, the operand register's field)
    'switch_on_non_list': ('s_tag', 'x'),
    'get_atom': ('s_tag', 'op'),
}
# get_atom's constant: the atom number, the instruction's low 24 bits, put
# in MDR2 by the S stage with no tag (the routine stamps it: 3800 ATOMo,
# 3804 ATOMx).  OURS: that the S stage leaves the constant in MDR2.
S_CONST = {'get_atom': 'a24'}

# The S stage's tag mechanisms (Nakashima's thesis pp.134-137, DOCUMENTED:
# (1) the tag of an operand compared with the entry's tag immediate into
# COND, the p.135 box "MDR1 = data, COND = (A[i].tag==list)"; (2) the
# multiway set-up by the memory operand's tag (TGT into TDAR); (3) the
# start address changed by that comparison, "if (data.tag==list)
# start(for_list) else start(for_others)", the operand dereferenced
# first, p.137 "repeats the fetch until the tag is not ref").  How (3)
# changes the address is not documented:
#
#   S_ENTRY (INFERRED): when the dereferenced operand's tag equals the
#   decode entry's tag immediate (the whole tag, MRB included), the
#   routine starts at the entry itself, with COND = (the operand's OWN
#   tag, before dereference, == the immediate), as in the p.135 box, and
#   MAR1 = the address of the last cell the dereference read.  Decided
#   at 3800-3801 (get_atom on an unbound variable, immediate UNDF: the
#   cell must be bound to {ATOMo, atom}, and 3800 is the word that stamps
#   ATOMo on the constant; entering at entry + 1 binds it untagged: the
#   injection 's_imm_plus1' FAILs) and run at 3300-3301
#   (switch_on_non_list on a list held directly in A0: COND true, the
#   conditional jump to 3305 not taken, 3301 R02 <- MDR1, end: two
#   words, where the thesis's Table 3-6 gives get_list one step, an open
#   tension; entry + 1 gives one word and the same registers there).
#   Discriminated: the start (s_imm_plus1) and MAR1 (s_no_mar1: STOP at
#   3801).  The COND part fits but is NOT discriminated (s_cond_true
#   changes nothing).  Joint with S_CONST (OURS) above.  Read, not run: through a REF (COND false) 3300 jumps to
#   3305-3309, which put the variable cell the list was reached through
#   on the R19 list.
#   Any other tag would take the multiway set-up (2) into a row of the
#   32-word entry; which TGT column and which row granularity is UNKNOWN
#   here (column = TDPF with 4-word rows fits switch_on_non_list's rows
#   1-4 when read, not run; get_atom's and wait_nil's do not): raises.
S_ENTRY = 0             # the injections: 's_imm_plus1' 1; 's_imm_row' 'row'


class SStageUnknown(KeyError):
    """An S-stage set-up this stand-in does not model."""


def deref(pu, w):
    """The S stage's dereference (thesis p.137): follow REF cells until
    the tag is not a REF.  Returns (data, address of the last cell read
    or None).  OURS as a mechanism stand-in (DOCUMENTED that it is done
    in the S stage, not how its result is laid out in the registers)."""
    last = None
    while w[0] & ~1 == 0x06:
        last = w[1]
        if last not in pu.mem:
            raise SStageUnknown('S-stage dereference of %x, never written' % last)
        w = pu.mem[last]
    return w, last


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
    if mdr == 'label':
        pu.wr[mekbn.MDR1] = (0, (pu.pc + 2 + sx16(v)) & 0xffffffff)
        return start
    if mdr == 's_tag':
        if imm is None:
            raise SStageUnknown('S-stage tag set-up for %s: no tag immediate' % name)
        own = pu.an[pu.ir_field(mar)]
        data, last = deref(pu, own)
        pu.wr[mekbn.MDR1] = data
        if last is not None:
            pu.wr[mekbn.MAR1] = (0, last)
        if base(name) in S_CONST:
            pu.wr[mekbn.MDR2] = (0, {'a24': v & 0xffffff}[S_CONST[base(name)]])
        if S_ENTRY == 'row':    # the injection: every tag takes a TGT row
            return start | pu.tgt[nc['TDPF']][data[0] & 63] << 2
        if data[0] == imm:
            pu.cond, pu.cond_cycle = own[0] == imm, 'S'
            return start + S_ENTRY
        raise SStageUnknown('S-stage multiway set-up: %s tag %02x, TDPF %d (row entry UNKNOWN)'
                            % (name, data[0], nc['TDPF']))
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


def dispatch(pu):
    """Decode-table dispatch from the instruction cell pu.ir, as the D
    stage does: the cell's tag picks the class (0x22 GMI = 2, 0x23 KLB = 3,
    as asm/mekbn.py kl1_entries reads the table, MEASURED in
    pseudo_pimm_microcode.md section 3), its top byte the
    opcode, and the held decode table's entry (class << 8 | opcode) the
    start address.  Returns (name, start) after the S-stage set-up.
    An empty entry or another tag raises."""
    name = decode(pu)
    return name, setup(pu, name)


def decode(pu):
    """The decode-table name of the instruction cell pu.ir (dispatch's
    D-stage half)."""
    t, v = pu.ir
    cls = {0x22: 2, 0x23: 3}.get(t)
    if cls is None:
        raise KeyError('instruction tag %02x: no KL1 decode class' % t)
    idx = cls << 8 | (v >> 24) & 255
    names = [n for n, e in pu.fw.kl1_entries().items() if e[0] == idx]
    if not names:
        raise KeyError('decode entry %03x empty' % idx)
    return names[0]
