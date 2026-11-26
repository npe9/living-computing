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
    (setup.py, OURS per operand form, one nano-code rule INFERENCE);
  - the condition multiplexer behind CNDF (COND_RULES, INFERENCE each);
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


# ---------------------------------------------------------------------------
# The rules.  Each entry: the rule, its label and the evidence.  The keys
# are the names injections perturb (check_pu.py); RULES is data so that a
# rule can be switched off and the run observed.
RULES = {
    # Operand-register selects (WRBF clear): 8 = the register in the
    # opcode's low bits, 9 = x, a = y, b = z.  8/9: MEASURED by mekbn
    # (put_atom/put_integer differ in one bit, section 10).  a = y,
    # b = z: INFERENCE, decided at 318f (set_variable writes its REF to
    # opda, pimm.py i_set_variable reg[y]) and 31d7 (put_variable,
    # reg[y]); b at 3a69 (add's result to opdb, pimm.py i_add reg[z]).
    'opd_fields': {8: 'op', 9: 'x', 0xa: 'y', 0xb: 'z'},
    # TGIF: 1 stamps the tag immediate on what SD1 loads, 2 on the ALU
    # result (mekbn, VERIFIED / DERIVED).  3: INFERENCE, both stamps with
    # the tag taken from EM2 (thesis p.144: "EM2 can also be the DST-Bus
    # tag immediate"), decided at 3193 (write_nil: EM1 = 20, EM2 = 02,
    # and the cell written must be ATOM 0, pimm.py i_write_nil).
    'tgif3_tag': 'EM2',
    # A write with bit 59 set stores MDR2.  INFERENCE (section 16 left it
    # open): decided at 31d7 (put_variable: the cell must get the UNDF
    # that 31d6 put in MDR2; MDR1 holds the link just read) and 3001
    # (collect_value: the old head stamped VECT0x is in MDR2).
    'w59_mdr2': True,
    # A write stores the MDR as it stood before its own word (mekbn
    # WRITE_SAME_WORD False; section 16, VERIFIED on new_vector).
    'write_old_mdr': True,
    # MCF (bit 18) with EM1 = 20 steps the structure pointer R02 by one.
    # INFERENCE, decided at 31c7 (write_integer: one word, MCF, EM1 20;
    # pimm.py i_write_integer _sp += 1; set_integer 3182 has neither and
    # does not move sp) and 3193 (write_nil).
    'mcf_20_sp': True,
    # The free-list pop's exhaustion test.  CNDF 9 in the word that takes
    # the link into the head register sets COND := "the link is a cell"
    # (tag VECT0x), tested by the conditional end in the next word, whose
    # other arm calls the refill (3378 / 337d).  INFERENCE: pushes stamp
    # the link VECT0x (3000, 216c; MEASURED section 15); decided at
    # 31fa/31fb (put_vector_1), 31d1/31d2 (put_list).
    'cnd9_link': True,
    # R06 and R07 hold zero: {ATOMo, R06} is written where nil stands
    # (section 17), {UNDF, R07} where pimm.py writes UNDF 0 (31d6).
    # INFERENCE (OURS as initial state).
    'zero_regs': (0x06, 0x07),
    # JMPF bit 26 (codes b, c, e) makes a page-relative or relative jump
    # conditional; codes 3, 4, 6 jump unconditionally whatever CNDF holds,
    # and their CNDF only forms COND for a later word.  INFERENCE from a
    # measurement (ref/pu/README.md "Conditions"): the word after a JMPF
    # 3/4/6 word is zero or an explicit target in 47-83% of cases with or
    # without CNDF (image 2 and syspsi alike), after a b/c/e word in
    # 3-17%; all 23 self-jumping words are c or e.  Decided at 318c
    # (set_variable: JMPF 4 CNDF b must jump over set_marked_variable's
    # words 318d-318e to 318f).  This replaces mekbn.tested() (CNDF != 0)
    # inside the simulator; mekbn's pins do not depend on the difference.
    'bit26_cond': True,
    # A conditional JMPF 1 (EM bit 1) with EM bit 0 set is taken when
    # COND is false.  INFERENCE, decided at 31fb/31d2/318f/31d8: the
    # pop's end must be taken when the link is not the end marker.  With
    # EM bit 0 clear: not decided, raises.
    'j1_bit0_false': True,
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
# INFERENCE.  Evidence: CNDF 9 words leave EM1 free (TGIF 0 in 448 of
# 453, image 2) and their EM1 values are tags (ATOMo 105, INTo 94,
# REFo 32, VDESC 26, FPREC 24, SHREC 20, MOD 17, ...); CNDF b words often
# use EM1 for a stamp (TGIF non-zero in 24 of 56) and their EM2 values are
# tags (ATOMo 15, INTo 14, VDESC 4, ...).  Decided at 31fa and 31d1 (EM1
# ATOMo: the refill's last link is {ATOMo, 0}, 3368) and 318c, 3196, 31d6
# (EM2 ATOMo), each tested by the conditional end that follows.
COND_RULES = {9: _cnd_tag_eq('EM1'), 0xb: _cnd_tag_eq('EM2')}


class PU:
    def __init__(self, fw=None):
        self.fw = fw or mekbn.Firmware()
        self.img = self.fw.img2
        self.an = {}            # the An/Xn register file (RF, 32 words): pimm.py reg[]
        self.r = {}             # WRBF clear, selects 01-07, 0c-1f: R01 .. R1f
        self.w = {}             # WRBF set: W00 .. W1f
        self.wr = {XR: None, 'YR': None, MAR1: None, MAR2: None, MDR1: None, MDR2: None}
        self.mem = {}
        self.mstk = []
        self.cond = None        # COND, set by the previous word (None = not formed)
        self.ir = None          # the KL1-B instruction (tag, value) in the E stage
        self.trace = []         # (upc, word)
        self.writes = []        # (upc, address, (tag, value))
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
        raise Unmodelled(upc, 'SC2F %x immediate' % sc2)

    def alu(self, upc, x, old):
        as1, as2 = mekbn.alu_in(x)
        a = {0: (0, 0), XR: old[XR], MDR1: old[MDR1], MDR2: old[MDR2],
             MAR1: old[MAR1], MAR2: old[MAR2]}.get(as1, 'open')
        if a == 'open':
            raise Unmodelled(upc, 'AS1F %d' % as1)
        b = {0: (0, 0), 1: old['YR'], 2: old[MDR1], 3: old[MDR2]}[as2]
        if a is None or b is None:
            raise Unmodelled(upc, 'ALU input never set (AS1F %d, AS2F %d)' % (as1, as2))
        self.as1_seen = a
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
        tag = a[0] if as1 else b[0]
        if field(x, 'TGIF') & 2:
            tag = self.stamp_tag(x)
        return (tag, v & M32)

    def step(self, upc):
        """Execute the word at upc; return the next upc or None at the
        end of the machine instruction."""
        if upc >= len(self.img):
            raise Unmodelled(upc, 'outside image 2 (syspsi upper control store)')
        x = self.img[upc]
        if not x:
            raise Unmodelled(upc, 'zero microinstruction')
        self.trace.append((upc, x))
        old = dict(self.wr)
        new = {}            # work register -> value
        regw = []           # register-file writes
        if bit(x, 63):
            raise Unmodelled(upc, 'DBGF')
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
                raise Unmodelled(upc, 'S1 and S2 load one register')
            new[d] = v
        # phase 2: the ALU, to ADF and DSTF
        dst, d = field(x, 'ADF'), field(x, 'DSTF')
        res = None
        self.as1_seen = None
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
        # memory: bit 61 read, 62 write, 60 step; 58 MAR2, 59 MDR2
        rd, wr = bit(x, mekbn.RD_BIT), bit(x, mekbn.MEM_BIT)
        if rd or wr:
            mar = MAR2 if bit(x, mekbn.MAR_SEL_BIT) else MAR1
            mdr = MDR2 if bit(x, mekbn.MDR_SEL_BIT) else MDR1
            if old[mar] is None:
                raise Unmodelled(upc, '%s never set' % WNAME[mar])
            addr = old[mar][1]
            if rd and wr:
                raise Unmodelled(upc, 'read and write in one word')
            if wr:
                if mdr == MDR2 and not RULES['w59_mdr2']:
                    raise Unmodelled(upc, 'write with bit 59 (data register open)')
                if mdr == MDR2 and RULES['w59_mdr2'] == 'MDR1':
                    mdr = MDR1          # injection only
                data = old[mdr] if RULES['write_old_mdr'] else {**old, **new}[mdr]
                if data is None:
                    raise Unmodelled(upc, 'write of %s, never set' % WNAME[mdr])
                self.mem[addr] = data
                self.writes.append((upc, addr, data))
            if rd:
                if addr not in self.mem:
                    raise Unmodelled(upc, 'read of memory %x, never written' % addr)
                if mdr in new:
                    raise Unmodelled(upc, 'read data and a load meet in %s' % WNAME[mdr])
                new[mdr] = self.mem[addr]
            if bit(x, mekbn.INC_BIT):
                if mar in new:
                    raise Unmodelled(upc, 'step and a load meet in %s' % WNAME[mar])
                new[mar] = (old[mar][0], (addr + 1) & M32)
        elif bit(x, mekbn.INC_BIT):
            raise Unmodelled(upc, 'bit 60 without a strobe')
        # commit (a register loaded in a word is seen by the next word)
        self.wr.update(new)
        for (f, n), v in regw:
            {'W': self.w, 'A': self.an, 'R': self.r}[f][n] = v
        # condition formed by this word, for the next
        kind, target, falls = flow(upc, x)
        # flow()'s third item is "can fall through": for a jump, end or
        # return that is "conditional"; a call returns, a branch is
        # conditional by kind
        conditional = falls if kind in ('jump', 'end', 'return') else kind == 'branch'
        jf, cnd, em = field(x, 'JMPF'), field(x, 'CNDF'), field(x, 'EM')
        prev_cond = self.cond
        own = cnd and mekbn.jk(x) != 1
        if own:
            rule = COND_RULES.get(cnd)
            if rule is None:
                raise Unmodelled(upc, 'CNDF %x (condition not known)' % cnd)
            self.cond = rule(self, upc, x, self.as1_seen)
        # sequencing
        if kind == 'jmpf2':
            raise Unmodelled(upc, '4-bit JMPF 2')
        if mekbn.jk(x) in (3, 4, 6):
            if not RULES['bit26_cond']:
                raise Unmodelled(upc, 'JMPF %x (bit 26 rule off)' % jf)
            conditional = bool(jf & 8)
            if conditional and own:
                raise Unmodelled(upc, 'JMPF %x with its own CNDF %x (timing not decided)'
                                 % (jf, cnd))
        taken = True
        if mekbn.jk(x) == 1 and kind in ('jump', 'end', 'return'):
            if kind == 'jump' and em & 4:
                raise Unmodelled(upc, 'JMPF 1 jump with EM bit 2 (dispatch)')
            if conditional:
                if not em & 1 or not RULES['j1_bit0_false']:
                    raise Unmodelled(upc, 'conditional JMPF 1 with EM bit 0 clear')
                if prev_cond is None:
                    raise Unmodelled(upc, '%s? with no condition formed' % kind)
                taken = not prev_cond
            elif em & 1:
                raise Unmodelled(upc, 'JMPF 1 %s with EM bit 0' % kind)
        elif conditional and kind != 'next':
            if prev_cond is None:
                raise Unmodelled(upc, '%s? with no condition formed' % kind)
            taken = prev_cond
        if not taken:
            return upc + 1              # the other arm is the next word
        if kind == 'branch':
            raise Unmodelled(upc, 'JMPF 2 branch')
        if kind == 'next':
            return upc + 1
        if kind == 'jump':
            return target
        if kind == 'call':
            self.mstk.append(upc + 1)
            return target
        if kind == 'return':
            if not self.mstk:
                raise Unmodelled(upc, 'return with an empty micro stack')
            return self.mstk.pop()
        if kind == 'end':
            return None
        raise Unmodelled(upc, 'flow kind %s' % kind)

    def run(self, upc, limit=2000):
        """Run from upc to the end of the machine instruction."""
        n0 = len(self.trace)
        try:
            while upc is not None:
                if len(self.trace) - n0 >= limit:
                    raise Unmodelled(upc, 'micro step limit')
                upc = self.step(upc)
        except Unmodelled as e:
            # held words completed before the stop (the stopping word's
            # entry in the trace is not counted)
            e.words = len(self.trace) - n0 - (1 if self.trace and self.trace[-1][0] == e.upc
                                              else 0)
            raise
        if self.mstk:
            raise Unmodelled(self.trace[-1][0], 'end with %d return(s) pending' % len(self.mstk))
        return len(self.trace) - n0
