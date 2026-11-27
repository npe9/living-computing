#!/usr/bin/env python3
"""A microcode-level simulator of the PIM/m / PSI-III PU's E stage that
executes ICOT's held KL1 microprogram (rungs U1/U2 of
docs/pu_microcode_plan.md).

The microinstructions are image 2 of PMPSI.DIR/pimm.MEkbn, read from
docs/nonlocal/psdpim.tar.Z through asm/mekbn.py (third-party binary: it
is never copied into the repository, and neither is any dump of it).
Field positions are asm/mekbn.py's FIELDS (Nakashima Fig. 3-25); field
VALUES are the measured readings of docs/pseudo_pimm_microcode.md
sections 8-21, plus the rules in RULES below, each labelled.

What runs here is HELD: every microinstruction executed is the held
word at that microaddress, decoded generically; there is no Python per
KL1-B instruction in the E stage.  What is stood in is hardware the
microprogram does not give:

  - the D/A/R/S stages, which the decode entry's nano-code drives
    (setup.py, OURS per operand form, one nano-code rule INFERRED);
  - the condition multiplexer behind CNDF (COND_RULES, INFERRED each);
  - memory (a dict of 40-bit cells, OURS).

Anything met on an executed path whose meaning is not modelled raises
Unmodelled with the microaddress: "fail loud".

Values are (tag, value) with an 8-bit tag and a 32-bit value.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'asm'))
import mekbn  # noqa: E402
from mekbn import field, bit, flow  # noqa: E402
import pu_store  # noqa: E402
import pu_sysinit  # noqa: E402

M32 = 0xffffffff
# kbn.TAGS values used by name below (asm/kbn.py, from the PIMOS inspector)
INT, ATOM, LIST, REF, UNDF, VECT0 = 0x00, 0x02, 0x04, 0x06, 0x08, 0x10
VECT0x = 0x11

# Work-register numbering of SD1F / ADF / AS1F (mekbn: MEASURED).
XR, MDR1, MDR2, MAR1, MAR2 = 1, 4, 5, 6, 7
WNAME = {XR: 'XR', MDR1: 'MDR1', MDR2: 'MDR2', MAR1: 'MAR1', MAR2: 'MAR2'}


class Unmodelled(Exception):
    """A field value, table or path the simulator does not model."""

    def __init__(self, upc, what):
        Exception.__init__(self, '%04x: %s' % (upc, what))
        self.upc, self.what = upc, what


class Trap(Unmodelled):
    """Control reached the illegal / unimplemented-instruction trap 6c21
    (upper syspsi, resident under the KL1 image; 244 image-2 call sites;
    CORROBORATED, docs/pu_microcode_inference.md section 7 item 4).  A
    trap is an outcome, not a gap in the model."""


TRAP_ILLEGAL = 0x6c21
SPECIAL_EM = 0x7fff     # S9: JMPF 1 with EM = 7fff, a special form (INFERRED, open)
TGT_KL1 = 0x5300        # sysinit's KL1 tag table, 64 tags x 8 columns
TGT_COLUMN = {0x3a: 2}  # set-up EM1 -> column; only 3a -> 2 is VERIFIED


# ---------------------------------------------------------------------------
# The rules.  Each entry: the rule, its label and the evidence.  The keys
# are the names injections perturb (check_pu.py); RULES is data so that a
# rule can be switched off and the run observed.
RULES = {
    # Operand-register selects (WRBF clear): 8 = the register in the
    # opcode's low bits, 9 = x, a = y, b = z.  8/9: MEASURED by mekbn
    # (put_atom/put_integer differ in one bit, section 10).  a = y,
    # b = z: INFERRED, decided at 318f (set_variable writes its REF to
    # opda, pimm.py i_set_variable reg[y]) and 31d7 (put_variable,
    # reg[y]); b at 3a69 (add's result to opdb, pimm.py i_add reg[z]).
    'opd_fields': {8: 'op', 9: 'x', 0xa: 'y', 0xb: 'z'},
    # TGIF: 1 stamps the tag immediate on what SD1 loads, 2 on the ALU
    # result (mekbn, VERIFIED / DERIVED).  3: INFERRED, both stamps with
    # the tag taken from EM2 (thesis p.144: "EM2 can also be the DST-Bus
    # tag immediate"), decided at 3193 (write_nil: EM1 = 20, EM2 = 02,
    # and the cell written must be ATOM 0, pimm.py i_write_nil).
    'tgif3_tag': 'EM2',
    # A write with bit 59 set stores MDR2.  INFERRED (section 16 left it
    # open): decided at 31d7 (put_variable: the cell must get the UNDF
    # that 31d6 put in MDR2; MDR1 holds the link just read) and 3001
    # (collect_value: the old head stamped VECT0x is in MDR2).
    'w59_mdr2': True,
    # A write stores the MDR as it stood before its own word (mekbn
    # WRITE_SAME_WORD False; section 16, VERIFIED on new_vector).
    'write_old_mdr': True,
    # MCF (bit 18) with EM1 = 20 steps the structure pointer R02 by one.
    # INFERRED, decided at 31c7 (write_integer: one word, MCF, EM1 20;
    # pimm.py i_write_integer _sp += 1; set_integer 3182 has neither and
    # does not move sp) and 3193 (write_nil).
    'mcf_20_sp': True,
    # Switch for COND_RULES below (CNDF 9 / b: the tag compared with EM1 /
    # EM2).  In a free-list pop the word that takes the link into the head
    # register compares its tag with ATOMo, the refill's end marker
    # (3368), and the conditional end that follows goes on to the refill
    # (3378 / 337d) when they are equal.  Decided at 31fa/31fb
    # (put_vector_1), 31d1/31d2 (put_list), 318c/318f, 31d6/31d8.
    'cnd9_link': True,
    # R06 and R07 hold zero: {ATOMo, R06} is written where nil stands
    # (section 17), {UNDF, R07} where pimm.py writes UNDF 0 (31d6).
    # INFERRED (OURS as initial state).
    'zero_regs': (0x06, 0x07),
    # JMPF bit 26 (codes b, c, e) makes a page-relative or relative jump
    # conditional; codes 3, 4, 6 jump unconditionally whatever CNDF holds,
    # and their CNDF only forms COND for a later word.  INFERRED from a
    # measurement (ref/pu/README.md "Conditions"): the word after a JMPF
    # 3/4/6 word is zero or an explicit target in 47-83% of cases with or
    # without CNDF (image 2 and syspsi alike), after a b/c/e word in
    # 3-17%; all 23 self-jumping words of image 2 are c or e, 36 of 37 of
    # syspsi (ref/pu/measure.py, pinned).  Decided at 318c (set_variable:
    # JMPF 4 CNDF b must jump over set_marked_variable's words 318d-318e
    # to 318f).  This replaces mekbn.tested() (CNDF != 0) inside the
    # simulator; under it mekbn's flow pins move (measure.py
    # 'mekbn_under_bit26': the call/return separation improves).  Which
    # way a conditional b/c/e jump goes on COND is not decided: raises.
    'bit26_cond': True,
    # The timing of a conditional JMPF b/c/e/a (does it test the COND
    # its own word forms, 'same', or the previous word's, 'prev'?) is
    # UNKNOWN (inference doc 6.3 item 3): None raises; 'prev'/'same' are
    # the switch positions for an experiment.  A conditional JMPF 1
    # (end, return, jump) tests the COND the PREVIOUS executed word
    # formed: EXECUTED for ends by pu_smt (less_than / not_less_than
    # share a first word).  A word with CNDF 0 leaves COND as it was:
    # EXECUTED at put_variable 31d6-31d8 (31d6 forms COND with CNDF b,
    # 31d7 has CNDF 0, the conditional end 31d8 tests 31d6's COND and
    # matches pimm.py in both arms, the last-cell case included).  With
    # j1_cond_prev_strict (the injection 'cond_prev_strict') a COND not
    # formed by the very previous word raises, and put_variable stops.
    'cjump_time': None,
    'j1_cond_prev_strict': False,
    # A conditional JMPF 1 (EM bit 1) with EM bit 0 set is taken when
    # COND is false.  INFERRED, decided at 31fb/31d2/318f/31d8: the
    # pop's end must be taken when the link is not the end marker.  With
    # EM bit 0 clear: not decided, raises.
    'j1_bit0_false': True,
    # AS1F 3 with AS2F 0: the AS1 bus carries the constant EM2.  INFERRED
    # (thesis p.144: "AS1F modifies AS2F's meaning for constants"; open in
    # mekbn).  Decided at 3321 (the one-cell allocator loads R03 with it);
    # the words that load R03 (rassy's lc) this way carry EM2 13 beside
    # the one-cell list (3321, 3378) and 5 beside the two-cell list (332f,
    # 337b): 16 / 1 - 3 and 16 / 2 - 3, the refill's loop count for a
    # 16-word chunk (README "First routine that would not run").
    'as1f3_em2': True,
    # SC2F b, the "wide" immediate (704 words of image 2; layout open in
    # mekbn): the 10 bits EM2:EM3, zero-extended.  INFERRED.  Static
    # evidence: the 223 words whose wide value is 1a0 carry EM1 0 or a
    # TGIF 1/2 stamp tag (2071 {REFo, 1a0}, 2077 {INTo, 1a0}), so EM1 is
    # not part of the value where it is a tag.  Decided at 204b-204d
    # (start's heap-top routine: 1a0 + 4a is the parameter cell read;
    # the alternative EM1:EM2 reading, the injection 'wide_em1em2', reads
    # 1a + 4 and stops on memory never written).  A wide word whose EM1 is
    # non-zero and not a stamp raises (width UNKNOWN: 16 bits or 10).
    'sc2_wide': 'EM2:EM3',
    # A conditional JMPF 1 with EM bit 0 CLEAR is taken when COND holds:
    # the static agent's INFERRED polarity (pu_microcode_inference.md 6.3
    # item 4, "EM bit 0 = 0 ends if the condition holds"), now EXECUTED on
    # a conditional return at 2050 (start's heap-top rounding, below).
    'j1_bit0_clear_true': True,
    # CNDF 2: COND := the ALU result (32 bits) is zero (rassy's alf_zero;
    # CNDF 5 is the static agent's eq).  INFERRED, decided at 204f-2052:
    # 204f MDR2 := hp & 15 forms COND, 2050 R1f := hp & ~15 and returns
    # if COND, 2051-2052 add 16.  The contract: the heap top start
    # leaves is the parameter rounded UP to 16 (never below it: the cells
    # below are in use).  Under 'not zero' (the injection 'cnd2_nonzero')
    # an unaligned top is rounded DOWN: FAIL.  Jointly with the polarity
    # above (the pair (zero, taken if COND) and (not zero, taken if not
    # COND) are the two that satisfy the contract).
    'cnd2_zero': True,
}

# Conditions.  COND is formed by a word's CNDF and tested by a later
# conditional word (thesis p.130: condition into the flag COND one step,
# branch on it the next); it stands until a word forms a new one.  key:
# CNDF.  A rule returns a bool from the ALU's first input as the word
# saw it (the tag of a register compared with an immediate, M92 p.428).
def _cnd_tag_eq(which):
    def rule(pu, upc, x, a):
        if not RULES['cnd9_link']:
            raise Unmodelled(upc, 'CNDF %x (rule off)' % field(x, 'CNDF'))
        if a is None:
            raise Unmodelled(upc, 'CNDF %x with no ALU input' % field(x, 'CNDF'))
        return a[0] == field(x, which)
    return rule


# CNDF 9: tag of the ALU's AS1 input == EM1.  CNDF b: == EM2.
# INFERRED.  Evidence: CNDF 9 words leave EM1 free (TGIF 0 in 448 of
# 453, image 2) and their EM1 values are tags (ATOMo 105, INTo 94,
# REFo 32, VDESC 26, FPREC 24, SHREC 20, MOD 17, ...); CNDF b words often
# use EM1 for a stamp (TGIF non-zero in 24 of 56) and their EM2 values are
# tags (ATOMo 15, INTo 14, VDESC 4, ...).  Decided at 31fa and 31d1 (EM1
# ATOMo: the refill's last link is {ATOMo, 0}, 3368) and 318c, 3196, 31d6
# (EM2 ATOMo), each tested by the conditional end that follows.
def _signed(v):
    v &= M32
    return v - (1 << 32) if v >> 31 else v


def _cnd5(pu, upc, x, a):
    """CNDF 5: the word's ALU result is zero (eq).  EXECUTED up to one
    global polarity by pu_smt (inference doc 6.3 item 4); eq chosen
    INFERRED, with 'EM bit 0 = 0: end if the condition holds'."""
    if pu.alu_seen is None:
        raise Unmodelled(upc, 'CNDF 5 with no ALU operation')
    return pu.alu_seen[2] & M32 == 0


def _cnd7(pu, upc, x, a):
    """CNDF 7, by EM1: 0a lt (EXECUTED up to the polarity, inference doc
    6.3 item 4), 09 overflow of the add/subtract (INFERRED, item 5), 3a
    the case_tag_setup of a JMPF 3 multiway (handled in evaluate).  Any
    other EM1 is UNKNOWN and raises."""
    em1 = field(x, 'EM1')
    if pu.alu_seen is None:
        raise Unmodelled(upc, 'CNDF 7 EM1 %02x with no ALU operation' % em1)
    a1, b1, v = pu.alu_seen
    if em1 == 0x0a:
        if field(x, 'ALF') != 1:
            raise Unmodelled(upc, 'CNDF 7 EM1 0a (lt) without a subtract')
        return _signed(a1[1]) < _signed(b1[1])
    if em1 == 0x09:
        if field(x, 'ALF') not in (0, 1):
            raise Unmodelled(upc, 'CNDF 7 EM1 09 (overflow) without an add/subtract')
        return not -(1 << 31) <= _signed(a1[1]) + (1 if field(x, 'ALF') == 0 else -1) * _signed(b1[1]) < (1 << 31)
    raise Unmodelled(upc, 'CNDF 7 EM1 %02x (condition UNKNOWN)' % em1)


def _cnd2(pu, upc, x, a):
    """CNDF 2: the word's ALU result is zero (RULES['cnd2_zero'])."""
    if pu.alu_seen is None or pu.alu_seen[2] is None:
        raise Unmodelled(upc, 'CNDF 2 with no ALU operation')
    z = pu.alu_seen[2] & M32 == 0
    return z if RULES['cnd2_zero'] else not z


COND_RULES = {9: _cnd_tag_eq('EM1'), 0xb: _cnd_tag_eq('EM2'), 5: _cnd5, 7: _cnd7, 2: _cnd2}


class PU:
    def __init__(self, fw=None):
        self.fw = fw or mekbn.Firmware()
        st = pu_store.stores()
        # the KL1 control store: image 2, then syspsi from 6800 up,
        # resident (CORROBORATED, inference doc sections 4 and 7 item 1)
        self.img = st.kl1_wcs
        # the tag-dispatch RAM: sysinit's KL1 table at 5300, [column][tag]
        self.tgt = pu_sysinit.tgt(st, TGT_KL1)
        self.tdar = None        # (cycle, byte) the last case_tag_setup selected
        self.cond_cycle = None  # the cycle whose word formed COND
        self.an = {}            # the An/Xn register file (RF, 32 words): pimm.py reg[]
        self.r = {}             # WRBF clear, selects 01-07, 0c-1f: R01 .. R1f
        self.w = {}             # WRBF set: W00 .. W1f
        self.wr = {XR: None, 'YR': None, MAR1: None, MAR2: None, MDR1: None, MDR2: None}
        self.mem = {}
        self.mstk = []
        self.cond = None        # COND, set by the previous word (None = not formed)
        self.ir = None          # the KL1-B instruction (tag, value) in the E stage
        self.pc = None          # its address (the A stage's, OURS: set by a harness)
        self.trace = []         # (upc, word)
        self.writes = []        # (upc, address, (tag, value))
        self.cycles = []        # one record per microcycle (README "Trace format")
        self._reads = []
        for z in RULES['zero_regs']:
            self.r[z] = (0, 0)

    # -- operand fields of the instruction in the E stage
    def ir_field(self, which):
        t, v = self.ir
        return {'op': (v >> 24) & 31, 'x': (v >> 16) & 255, 'y': (v >> 8) & 255,
                'z': v & 255}[which]

    def sel_name(self, x, sel):
        if bit(x, mekbn.WRB_BIT):
            return ('W', sel)
        opd = RULES['opd_fields']
        if sel in opd:
            return ('A', self.ir_field(opd[sel]))
        return ('R', sel)

    def read_sel(self, upc, x, sel):
        if sel == 0 and not bit(x, mekbn.WRB_BIT):
            return (0, 0)
        f, n = self.sel_name(x, sel)
        store = {'W': self.w, 'A': self.an, 'R': self.r}[f]
        if n not in store:
            raise Unmodelled(upc, 'read of %s%02x, never set' % (f, n))
        self._reads.append(('%s%02x' % (f, n), store[n]))
        return store[n]

    def write_sel(self, x, sel, v, out):
        out.append((self.sel_name(x, sel), v))

    def stamp_tag(self, x):
        t = field(x, 'TGIF')
        if t == 3:
            return field(x, 'EM2') if RULES['tgif3_tag'] == 'EM2' else field(x, 'EM1')
        return field(x, 'EM1')

    def imm2(self, upc, x, sc2):
        if sc2 == mekbn.SC2_EM1:
            return (0, field(x, 'EM1'))
        if sc2 == mekbn.SC2_EM2:
            return (0, field(x, 'EM2'))
        if sc2 == mekbn.SC2_WIDE and RULES['sc2_wide'] == 'EM2:EM3':
            if field(x, 'EM1') and field(x, 'TGIF') not in (1, 2):
                raise Unmodelled(upc, 'SC2F b with EM1 %02x not a stamp (width UNKNOWN)'
                                 % field(x, 'EM1'))
            return (0, field(x, 'EM') & 0x3ff)
        if sc2 == mekbn.SC2_WIDE and RULES['sc2_wide'] == 'EM1:EM2':
            return (0, field(x, 'EM') >> 4)         # injection only
        raise Unmodelled(upc, 'SC2F %x immediate' % sc2)

    def alu(self, upc, x, old):
        as1, as2 = mekbn.alu_in(x)
        a = {0: (0, 0), XR: old[XR], MDR1: old[MDR1], MDR2: old[MDR2],
             MAR1: old[MAR1], MAR2: old[MAR2]}.get(as1, 'open')
        if as1 == 3 and as2 == 0 and RULES['as1f3_em2']:
            a = (0, field(x, 'EM2'))
        if a == 'open':
            raise Unmodelled(upc, 'AS1F %d' % as1)
        b = {0: (0, 0), 1: old['YR'], 2: old[MDR1], 3: old[MDR2]}[as2]
        if a is None or b is None:
            raise Unmodelled(upc, 'ALU input never set (AS1F %d, AS2F %d)' % (as1, as2))
        self.as1_seen = a
        self.alu_seen = (a, b, None)
        alf = field(x, 'ALF')
        if alf == 0:
            v = a[1] + b[1]
        elif alf == 1:
            v = a[1] - b[1]
        else:
            op = mekbn.alu_op(x)
            if op == 'pass_as2':
                v = b[1]
            elif op == 'and':
                v = a[1] & b[1]
            elif op == 'or':
                v = a[1] | b[1]
            elif op == 'xor':
                v = a[1] ^ b[1]
            else:
                raise Unmodelled(upc, 'ALU operation %s' % op)
        self.alu_seen = (a, b, v)
        tag = a[0] if as1 and as1 != 3 else b[0]
        if field(x, 'TGIF') & 2:
            tag = self.stamp_tag(x)
        return (tag, v & M32)

    def step(self, upc):
        """One microcycle: evaluate every operation of the word at upc from
        the OLD state, then commit them together.  Returns the next upc,
        or None at the end of the machine instruction."""
        cyc = self.evaluate(upc)
        self.commit(cyc)
        return cyc['next']

    def evaluate(self, upc):
        """The microcycle's effects, as a record (TRACE FORMAT in README):
        nothing in the machine state changes here.  Any field value the
        simulator does not model raises Unmodelled(upc, field)."""
        if upc >= len(self.img):
            raise Unmodelled(upc, 'micro_pc outside the control store')
        if upc == TRAP_ILLEGAL:
            raise Trap(upc, 'illegal-instruction trap')
        x = self.img[upc]
        if not x:
            raise Unmodelled(upc, 'zero microinstruction')
        self._reads = []
        old = dict(self.wr)
        new = {}            # phase-2 register -> value
        regw = []           # phase-1 register-file writes ((file, n), value)
        memw, memr = [], []
        if bit(x, 63):
            raise Unmodelled(upc, 'DBGF set')
        # phase 1: S1 bus (SC1F -> SD1F), S2 bus (SC2F -> SD2F)
        sc1, sd1 = field(x, 'SC1F'), field(x, 'SD1F')
        if sd1:
            if sd1 not in WNAME:
                raise Unmodelled(upc, 'SD1F %d' % sd1)
            v = self.read_sel(upc, x, sc1)
            if field(x, 'TGIF') & 1:
                v = (self.stamp_tag(x), v[1])
            new[sd1] = v
        sc2, sd2 = field(x, 'SC2F'), field(x, 'SD2F')
        if sd2:
            if sc2 in (mekbn.SC2_EM1, mekbn.SC2_EM2, mekbn.SC2_WIDE):
                v = self.imm2(upc, x, sc2)
            else:
                v = self.read_sel(upc, x, sc2)
            d = {1: 'YR', 2: MDR1, 3: MDR2}[sd2]
            if d in new:
                raise Unmodelled(upc, 'SD1F and SD2F load one register')
            new[d] = v
        # phase 2: the ALU, to ADF and DSTF
        dst, d = field(x, 'ADF'), field(x, 'DSTF')
        res = None
        self.as1_seen = None
        self.alu_seen = None
        if dst or d or field(x, 'ALF') or field(x, 'AS1F') or field(x, 'AS2F'):
            res = self.alu(upc, x, old)
            if dst:
                if dst not in WNAME:
                    raise Unmodelled(upc, 'ADF %d' % dst)
                if dst in new:
                    raise Unmodelled(upc, 'ADF and a bus load one register (%s)' % WNAME[dst])
                new[dst] = res
            if d:
                self.write_sel(x, d, res, regw)
        # MCF
        if bit(x, 18):
            if field(x, 'EM1') == 0x20 and RULES['mcf_20_sp']:
                sp = self.r.get(2)
                if sp is None:
                    raise Unmodelled(upc, 'MCF 20 with R02 unset')
                regw.append((('R', 2), (sp[0], (sp[1] + 1) & M32)))
            else:
                raise Unmodelled(upc, 'MCF with EM1 %02x' % field(x, 'EM1'))
        # memory (CCF): bit 61 read, 62 write, 60 step; 58 MAR2, 59 MDR2
        rd, wr = bit(x, mekbn.RD_BIT), bit(x, mekbn.MEM_BIT)
        if rd or wr:
            mar = MAR2 if bit(x, mekbn.MAR_SEL_BIT) else MAR1
            mdr = MDR2 if bit(x, mekbn.MDR_SEL_BIT) else MDR1
            if old[mar] is None:
                raise Unmodelled(upc, 'CCF: %s never set' % WNAME[mar])
            addr = old[mar][1]
            if rd and wr:
                raise Unmodelled(upc, 'CCF %02x: read and write in one word' % field(x, 'CCF'))
            if wr:
                if mdr == MDR2 and not RULES['w59_mdr2']:
                    raise Unmodelled(upc, 'CCF %02x: write data register' % field(x, 'CCF'))
                if mdr == MDR2 and RULES['w59_mdr2'] == 'MDR1':
                    mdr = MDR1          # injection only
                data = old[mdr] if RULES['write_old_mdr'] else {**old, **new}[mdr]
                if data is None:
                    raise Unmodelled(upc, 'CCF: write of %s, never set' % WNAME[mdr])
                memw.append((addr, data))
            if rd:
                if addr not in self.mem:
                    raise Unmodelled(upc, 'CCF: read of memory %x, never written' % addr)
                if mdr in new:
                    raise Unmodelled(upc, 'CCF: read data and a load meet in %s' % WNAME[mdr])
                new[mdr] = self.mem[addr]
                memr.append((addr, self.mem[addr]))
            if bit(x, mekbn.INC_BIT):
                if mar in new:
                    raise Unmodelled(upc, 'CCF: step and a load meet in %s' % WNAME[mar])
                new[mar] = (old[mar][0], (addr + 1) & M32)
        elif bit(x, mekbn.INC_BIT):
            raise Unmodelled(upc, 'CCF: bit 60 without a strobe')
        # condition generation (from the old state) and use
        kind, target, falls = flow(upc, x)
        # flow()'s third item is "can fall through": for a jump, end or
        # return that is "conditional"; a call returns, a branch is
        # conditional by kind
        conditional = falls if kind in ('jump', 'end', 'return') else kind == 'branch'
        jf, cnd, em = field(x, 'JMPF'), field(x, 'CNDF'), field(x, 'EM')
        prev_cond = self.cond
        cond_new, cond_cycle = prev_cond, self.cond_cycle
        tdar = self.tdar
        cycle = len(self.trace)
        if cnd == 7 and mekbn.jk(x) == 0 and field(x, 'EM1') in TGT_COLUMN:
            # case_tag_setup (thesis p.131): the TGT byte of the tag of
            # the ALU's first input, column by EM1 (only 3a -> 2 VERIFIED)
            if self.as1_seen is None:
                raise Unmodelled(upc, 'case_tag_setup with no ALU input')
            col = TGT_COLUMN[field(x, 'EM1')]
            tdar = (cycle, self.tgt[col][self.as1_seen[0] & 63])
        elif cnd == 7 and mekbn.jk(x) == 0 and field(x, 'EM1') not in (0x09, 0x0a):
            raise Unmodelled(upc, 'CNDF 7 EM1 %02x: TGT column or condition UNKNOWN'
                             % field(x, 'EM1'))
        elif cnd and mekbn.jk(x) != 1:
            rule = COND_RULES.get(cnd)
            if rule is None:
                raise Unmodelled(upc, 'CNDF %x (condition not known)' % cnd)
            cond_new, cond_cycle = rule(self, upc, x, self.as1_seen), cycle
        # sequencing
        if kind == 'jmpf2':
            raise Unmodelled(upc, 'JMPF 2 (4-bit; kind not known)')
        if jf in (8, 9, 0xd, 0xf):
            raise Unmodelled(upc, 'JMPF %x (bit 26 with this kind not decided)' % jf)
        if mekbn.jk(x) == 1 and em == SPECIAL_EM:
            raise Unmodelled(upc, 'JMPF 1 EM 7fff (S9, special form UNKNOWN)')
        if kind == 'branch' or (jf & 8 and mekbn.jk(x) in (3, 4, 6)):
            # conditional JMPF a / b / c / e: timing UNKNOWN (a switch)
            if RULES['cjump_time'] is None:
                raise Unmodelled(upc, 'JMPF %x conditional: timing UNKNOWN' % jf)
            raise Unmodelled(upc, 'JMPF %x conditional: polarity not decided' % jf)
        if jf == 3:
            # S8 case_branch: base | the TGT byte's low 4 bits, set up by
            # the word just before (a CNDF 7, JMPF 0 word)
            if tdar is None or tdar[0] != cycle - 1:
                raise Unmodelled(upc, 'JMPF 3 case_branch without a set-up in the word before')
            if target & 15:
                raise Unmodelled(upc, 'JMPF 3 case_branch base %04x not 16-aligned' % target)
            if tdar[1] > 15:
                raise Unmodelled(upc, 'JMPF 3 TGT byte %02x over 15' % tdar[1])
            target |= tdar[1]
        if mekbn.jk(x) in (3, 4, 6):
            if not RULES['bit26_cond']:
                raise Unmodelled(upc, 'JMPF %x (bit 26 rule off)' % jf)
            if jf & 8:
                raise Unmodelled(upc, 'JMPF %x conditional jump (polarity not decided)' % jf)
            conditional = False
        taken = True
        if mekbn.jk(x) == 1 and kind in ('jump', 'end', 'return'):
            if kind == 'jump' and em & 4:
                # S2b: a multiway, low target bits ORed in at run time
                # from a source not identified (INFERRED, inference doc 2.2)
                raise Unmodelled(upc, 'JMPF 1 EM bit 2: multiway, low-bit source UNKNOWN')
            if conditional:
                if em & 1 and not RULES['j1_bit0_false']:
                    raise Unmodelled(upc, 'JMPF 1 conditional with EM bit 0 set (rule off)')
                if not em & 1 and not RULES['j1_bit0_clear_true']:
                    raise Unmodelled(upc, 'JMPF 1 conditional with EM bit 0 clear')
                if prev_cond is None:
                    raise Unmodelled(upc, 'JMPF 1 %s? with no condition formed' % kind)
                if RULES['j1_cond_prev_strict'] and self.cond_cycle != cycle - 1:
                    raise Unmodelled(upc, 'JMPF 1 %s?: COND not formed by the previous word' % kind)
                taken = not prev_cond if em & 1 else bool(prev_cond)
            elif em & 1:
                raise Unmodelled(upc, 'JMPF 1 %s with EM bit 0' % kind)
        elif conditional:
            raise Unmodelled(upc, 'conditional %s (not decided)' % kind)
        push = pop = False
        if not taken:
            nxt = upc + 1               # the other arm is the next word
        elif kind == 'next':
            nxt = upc + 1
        elif kind == 'jump':
            nxt = target
        elif kind == 'call':
            nxt, push = target, True
        elif kind == 'return':
            if not self.mstk:
                raise Unmodelled(upc, 'JMPF 1 return with an empty micro stack')
            nxt, pop = self.mstk[-1], True
        elif kind == 'end':
            nxt = None
        else:
            raise Unmodelled(upc, 'flow kind %s' % kind)
        return {'cycle': len(self.trace), 'micro_pc': upc, 'microword': x,
                'reg_reads': list(self._reads), 'wr': new, 'reg_writes': regw,
                'mem_reads': memr, 'mem_writes': memw,
                'cond': cond_new, 'cond_cycle': cond_cycle, 'tdar': tdar,
                'push': upc + 1 if push else None, 'pop': pop,
                'next': nxt}

    def commit(self, c):
        """All of a microcycle's state changes at once."""
        self.wr.update(c['wr'])
        for (f, n), v in c['reg_writes']:
            {'W': self.w, 'A': self.an, 'R': self.r}[f][n] = v
        for a, d in c['mem_writes']:
            self.mem[a] = d
            self.writes.append((c['micro_pc'], a, d))
        self.cond, self.cond_cycle, self.tdar = c['cond'], c['cond_cycle'], c['tdar']
        if c['push'] is not None:
            self.mstk.append(c['push'])
        if c['pop']:
            self.mstk.pop()
        self.trace.append((c['micro_pc'], c['microword']))
        self.cycles.append(c)
        return c['next']

    def call(self, upc, limit=2000):
        """Run a microsubroutine from upc to its return, as a call word
        would (sub-rung "the allocator": 3320)."""
        self.mstk.append(-1)
        n0 = len(self.trace)
        try:
            while upc != -1:
                if upc is None:
                    raise Unmodelled(self.trace[-1][0], 'end inside a microsubroutine')
                if len(self.trace) - n0 >= limit:
                    raise Unmodelled(upc, 'micro step limit')
                upc = self.step(upc)
        except Unmodelled as e:
            e.words = len(self.trace) - n0
            raise
        return len(self.trace) - n0

    def run(self, upc, limit=2000):
        """Run from upc to the end of the machine instruction."""
        n0 = len(self.trace)
        try:
            while upc is not None:
                if len(self.trace) - n0 >= limit:
                    raise Unmodelled(upc, 'micro step limit')
                upc = self.step(upc)
        except Unmodelled as e:
            # held words completed (committed) before the stop
            e.words = len(self.trace) - n0
            raise
        if self.mstk:
            raise Unmodelled(self.trace[-1][0], 'end with %d return(s) pending' % len(self.mstk))
        return len(self.trace) - n0
