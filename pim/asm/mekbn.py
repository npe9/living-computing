#!/usr/bin/env python3
"""Structure of the Pseudo PIM/m firmware file PMPSI.DIR/pimm.MEkbn.

What is read here (docs/pseudo_pimm_microcode.md has the evidence and
says which statements are measured and which inferred):

  file words (40-bit: 32-bit value, 8-bit tag), load address 0x4200
    0x00000-0x007ff  decode table, 1024 two-word entries (asm/psdpim.py)
    0x00800-0x008ec  descriptor 1: links, image 1 base and length, and
                     a list of decode indices (classes 0 and 1)
    0x00900-0x0b8ff  image 1: 0x5800 microinstructions, identical to
                     syspsi (the PSI-III system firmware) 0..0x57ff
    0x0b900-0x0b9a9  descriptor 2: image 2 base and length, and the
                     list of decode indices of classes 2 and 3
    0x0ba00-0x189ff  image 2: 0x6800 microinstructions, the KL1
                     microprogram

  A microinstruction is two consecutive file words, low 32 bits first,
  both tags zero.  The microinstruction at address A of the KL1
  microprogram is file words 0xba00 + 2*A and 0xba00 + 2*A + 1.

  A decode entry's second word gives the start address two ways:
    tag byte & 0x18 == 0:  address = value bits 14..0
    tag byte & 0x18 != 0:  address = (decode index >> 7) << 11
                                     | value bits 9..0,
                           and value bits 15..10 are a 6-bit tag
                           immediate (ATOM for wait_atom, VECT3o for
                           wait_vector_3, COD for code, ...).

  Microinstruction fields that are established: bits 25..23 (TR-733's
  JMPF) select the branch kind and bits 15..0 (EM1..EM3) are its
  operand: JMPF 5 takes bits 15..0 as an absolute address; JMPF 2, 3, 6
  and 7 take bits 9..0 as an address in the current 1024-word page and
  bits 15..10 as a 6-bit immediate.  The other field boundaries printed
  by --dis are TR-733 fig. 4 as measured from the figure: a hypothesis.

  Second pass (docs/pseudo_pimm_microcode.md sections 7-12), each rule
  checked on something it was not fitted to (flow(), below):
    JMPF 0     fall through
    JMPF 1     EM bit 3 set: jump to (EM & 0x7ff0) | bits 22..19 -- with
               JMPF 1 the "CNDF" bits are the low four address bits;
               EM bit 3 clear: end of the routine -- EM bit 2 clear ends
               the machine instruction, EM bit 2 set returns from a
               microsubroutine.  EM bit 1 set makes either conditional
               (the next word is the other arm).
    JMPF 4     jump to own address + EM bits 3..0, signed
    JMPF 5, 7  call (absolute, page-relative); JMPF 3, 6 page-relative
               jump; JMPF 2 page-relative conditional branch.  A JMPF 3,
               4 or 6 word with bits 22..19 non-zero is conditional
               (every word that jumps to itself is one of these).
    EM bits 15..10 are a 6-bit immediate in any word (a tag, a count).
    Bit 62 (the top bit of "CCF") is set on the straight line of every
    set_*/write_* routine and in none of 219 words of register-only
    arithmetic.  (The second pass left open whether it is "write"; the
    third pass shows it is, see below.)
    DSTF/SC1F are register selects at the figure's positions; 8 and 9
    select the register file through two different operand fields of
    the machine instruction.

  Third pass (sections 14-20), the memory datapath:
    bit 61 read strobe, bit 62 write strobe, bit 60 steps the address
    register after the access.  In a strobe word bit 58 selects MAR2
    (else MAR1) and, for a read, bit 59 selects MDR2 (else MDR1) as the
    register the data arrive in.  In a word without a strobe bits 58 and
    59 are set exactly when MDR1 / MDR2 is used.  Work registers, as SD1
    and bits 36..34 number them: 1 XR, 4 MDR1, 5 MDR2, 6 MAR1, 7 MAR2.
    Bits 36..34 (the figure's "AS1F") are the ALU's destination, not an
    input; bits 31..29 ("ADF") say what the ALU passes (4 XR; 1 YR and
    5 XR+YR are supported, not verified: the cell numbers of the
    record readings depend on 5).  Bit 57 makes DST/SC1/SC2 name the work-register file.
    SC2 = 8 / 9 is the immediate EM1 / EM2.  A register loaded in one
    word is seen by the next; a write stores the MDR as it stood before
    its own word.  Bits 17..16 = 1 stamp the tag immediate on what SD1
    loads, = 2 on the ALU result.

Usage:
    python3 asm/mekbn.py --check            the pinned checks
    python3 asm/mekbn.py --segments         the file's layout
    python3 asm/mekbn.py --entries          KL1 start address per instruction
    python3 asm/mekbn.py --dis ADDR [N]     N microinstructions of image 2 (hex ADDR)
    python3 asm/mekbn.py --tag NAME         image-2 microinstructions carrying that
                                            6-bit immediate (EM bits 15..10) with a
                                            page-relative branch or with bits 17..16
                                            non-zero ("stamp"; not JMPF 1)
    python3 asm/mekbn.py --alloc            the fixed-size allocator entries and
                                            who calls them
    python3 asm/mekbn.py --rtl ADDR [N]     register transfers and memory accesses
                                            of N microinstructions, third-pass rules
    python3 asm/mekbn.py --records          the record writes read in sections 17-18
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import kbn      # noqa: E402
import psdpim   # noqa: E402

LOAD = 0x4200
DESC1, IMG1, IMG1_LEN = 0x800, 0x900, 0x5800
DESC2, IMG2, IMG2_LEN = 0xb900, 0xba00, 0x6800
RUN1 = (0x805, 0x8eb)     # file words holding descriptor 1's index list
RUN2 = (0xb902, 0xb9a8)

# TR-733 fig. 4, positions measured from the figure (hypothesis), except
# JMP and EM, which are checked below.
FIELDS = [('CCF', 62, 58), ('DST', 56, 52), ('SC1', 51, 47), ('SC2', 46, 42),
          ('SD1', 41, 39), ('SD2', 38, 37), ('AS1', 36, 34), ('AS2', 33, 32),
          ('AD', 31, 29), ('AL', 28, 26), ('JMP', 25, 23), ('CND', 22, 19),
          ('x18', 18, 18), ('x17', 17, 16), ('EM', 15, 0)]
PAGE_RELATIVE = (2, 3, 6, 7)
ABSOLUTE = 5

# Second pass.  Every constant here is perturbed by a recorded fault
# injection (docs/pseudo_pimm_microcode.md section 12).
J1_JUMP, J1_RETURN, J1_COND = 8, 4, 2     # EM bits of a JMPF 1 word
J1_HIGH = 0x7ff0                          # EM bits that are address bits 14..4
J1_LOW = 'CND'                            # field holding address bits 3..0
J4_SIGNED = True
GOTO_COND = True
CALLS, GOTOS, BRANCH = (5, 7), (3, 6), 2
MEM_BIT = 62                              # the write strobe (third pass, section 15)
ALLOC_WORD, ALLOC_MASK = 0x0402af40000001a0, 0xfc00   # allocator entry, N in EM1
EM1_SHIFT = 10                            # the 6-bit immediate is EM bits 15..10
REGISTER_ONLY = ((0x3a48, 0x3a90), (0x3abe, 0x3ad0), (0x3af0, 0x3b28), (0x2928, 0x29b8))
WRITERS = ('set_constant', 'set_integer', 'set_value', 'set_atom', 'set_nil', 'set_list',
           'write_constant', 'write_integer', 'write_atom', 'write_value', 'write_nil')
GSET_PARAM = ("(gseb,(10:16'B800)),", "(gsesh,16'18),", "%?A:00B800(16'100entry)")
NON_WRITERS = ('put_integer', 'put_atom', 'put_nil', 'put_value', 'put_constant')


def flow(a, x):
    """(kind, target or None, falls_through) of the microinstruction x at a."""
    j, em = field(x, 'JMP'), field(x, 'EM')
    if j == 0:
        return 'next', None, True
    if j == 1:
        cond = bool(em & J1_COND)
        if em & J1_JUMP:
            return 'jump', em & J1_HIGH | field(x, J1_LOW), cond
        return ('return' if em & J1_RETURN else 'end'), None, cond
    if j == 4:
        d = em & 15
        return 'jump', a + (d - 16 if J4_SIGNED and d >= 8 else d), tested(x)
    if j == ABSOLUTE:
        return 'call', em, True
    t = a & ~0x3ff | em & 0x3ff
    if j in CALLS:
        return 'call', t, True
    return ('jump', t, tested(x)) if j in GOTOS else ('branch', t, True)


def tested(x):
    """A JMPF 3, 4 or 6 word with bits 22..19 non-zero can fall through."""
    return GOTO_COND and field(x, 'CND') != 0


def first_end(img, t):
    """Kind of the first unconditional end/return/jump met reading on from t."""
    for a in range(t, min(t + 64, len(img))):
        if not img[a]:
            return None
        kind, _, falls = flow(a, img[a])
        if not falls:
            return kind
    return None


def flow_measure(img):
    """Numbers that the rules in flow() predict; see the doc, section 8."""
    n = len(img)
    j1 = [(a, x) for a, x in enumerate(img)
          if x and field(x, 'JMP') == 1 and field(x, 'EM') & J1_JUMP]
    tg = [flow(a, x)[1] for a, x in j1]
    inside = [t for t in tg if t < n]
    out = {'j1_jump': (len(j1), len(inside), sum(1 for t in inside if img[t]), len(set(tg)))}
    j4 = [(a, x) for a, x in enumerate(img) if x and field(x, 'JMP') == 4]
    back = [(a, x) for a, x in j4 if x & 8]

    def lands(ws):
        return sum(1 for a, x in ws if 0 <= flow(a, x)[1] < n and img[flow(a, x)[1]])
    out['j4'] = (len(j4) - len(back), lands([w for w in j4 if not w[1] & 8]),
                 len(back), lands(back))
    loops = [x for a, x in enumerate(img) if x and flow(a, x)[1] == a]
    out['self_jumps'] = (len(loops), sum(1 for x in loops if not flow(0, x)[2]))
    called = {flow(a, x)[1] for a, x in enumerate(img) if x and flow(a, x)[0] == 'call'}
    ends = [first_end(img, t) for t in called if t < n]
    out['after_call'] = (ends.count('return'), ends.count('end'))
    return out


def allocators(img):
    """{address: N} of the allocator entry words.  N is the cell count for
    3..6 (put_vector_N); above 8 it may be a size-class number."""
    return {a: field(x, 'EM') >> EM1_SHIFT for a, x in enumerate(img)
            if x & ~ALLOC_MASK == ALLOC_WORD}


# ---------------------------------------------------------------------------
# Third pass (docs/pseudo_pimm_microcode.md sections 14-20): the memory
# datapath.  Every constant is perturbed by a recorded fault injection
# (section 19).  Bits 36..34 are called AS1 above after the figure; they
# behave as the ALU's DESTINATION work register, in SD1's numbering.
RD_BIT, INC_BIT = 61, 60                  # MEM_BIT (62) is the write strobe
MAR_SEL_BIT, MDR_SEL_BIT = 58, 59         # in a strobe word: MAR2 / MDR2 instead of MAR1 / MDR1
WRB_BIT = 57                              # DST/SC1/SC2 name the work-register file, not RF
XR, MDR1, MDR2, MAR1, MAR2 = 1, 4, 5, 6, 7    # work registers as SD1 and bits 36..34 number them
YR_SD2, MDR1_SD2, MDR2_SD2 = 1, 2, 3      # SD2's numbering
AS2_MDR, AS2_MAR = 2, 3                   # AS2: the selected MDR, the MAR
SRC_XR, SRC_YR, SRC_SUM = 4, 1, 5         # bits 31..29 ("AD"): what the ALU passes
SC2_EM1, SC2_EM2, SC2_WIDE = 8, 9, 0xb    # SC2 codes that are immediates
WRITE_SAME_WORD = False                   # a write stores what was loaded BEFORE its word
SIZED_ALLOC = {0x3331: 3, 0x3334: 4, 0x3337: 5, 0x333a: 6}


def bit(x, n):
    return x >> n & 1


def strobe(x):
    """'' / 'R' / 'W' / 'RW' for a microinstruction."""
    return ('R' if bit(x, RD_BIT) else '') + ('W' if bit(x, MEM_BIT) else '')


def falls_to(img, a):
    """The next word, if a is a JMPF 0 word and the next word is non-zero."""
    x = img[a]
    if x and field(x, 'JMP') == 0 and a + 1 < len(img) and img[a + 1]:
        return img[a + 1]
    return None


def came_from(img, a):
    p = img[a - 1] if a else 0
    return p if p and field(p, 'JMP') == 0 else None


def mem_measure(img):
    """Numbers the memory-datapath rules predict (doc sections 14-16)."""
    nz = [(a, x) for a, x in enumerate(img) if x]
    out = {}
    out['strobes'] = (sum(1 for _, x in nz if bit(x, RD_BIT)),
                      sum(1 for _, x in nz if bit(x, MEM_BIT)),
                      sum(1 for _, x in nz if strobe(x) == 'RW'))
    # a read is followed by a use of the MDR
    nxt = [falls_to(img, a) for a, x in nz if bit(x, RD_BIT)]
    nxt = [y for y in nxt if y]
    out['read_then_mdr'] = (sum(1 for y in nxt if field(y, 'AS2') == AS2_MDR), len(nxt))
    # words without a strobe: bit 58 whenever MDR1 is touched, bit 59 whenever MDR2 is
    quiet = [x for _, x in nz if not strobe(x)]

    def lacking(pred, n):
        ws = [x for x in quiet if pred(x)]
        return (sum(1 for x in ws if not bit(x, n)), len(ws))
    out['mdr_enable'] = (
        lacking(lambda x: field(x, 'SD1') == MDR1, MAR_SEL_BIT),
        lacking(lambda x: field(x, 'AS1') == MDR1, MAR_SEL_BIT),
        lacking(lambda x: field(x, 'SD2') == MDR1_SD2, MAR_SEL_BIT),
        lacking(lambda x: field(x, 'SD1') == MDR2, MDR_SEL_BIT),
        lacking(lambda x: field(x, 'AS1') == MDR2, MDR_SEL_BIT),
        lacking(lambda x: field(x, 'SD2') == MDR2_SD2, MDR_SEL_BIT),
        (sum(1 for x in quiet if field(x, 'AS2') == AS2_MDR and not field(x, 'CCF') & 3),
         sum(1 for x in quiet if field(x, 'AS2') == AS2_MDR)))
    # MDR1 loaded from the register file is written by the next word
    w = [falls_to(img, a) for a, x in nz if field(x, 'SD1') == MDR1]
    w = [y for y in w if y]
    out['mdr1_then_write'] = (sum(1 for y in w if bit(y, MEM_BIT)), len(w))
    # a word with no ALU input and source code "XR" passes what SD1 = XR loaded a word earlier
    ps = [came_from(img, a) for a, x in nz
          if field(x, 'AS1') == 0 and field(x, 'AS2') == 0
          and field(x, 'AD') == SRC_XR and field(x, 'AL') == 0]
    ps = [p for p in ps if p]
    out['xr_pass'] = (sum(1 for p in ps if field(p, 'SD1') == XR), len(ps))
    # a word that jumps to itself and accesses memory steps the address
    loops = [x for a, x in nz if flow(a, x)[:2] == ('jump', a)]
    out['loops'] = (len(loops), sum(1 for x in loops if strobe(x)),
                    sum(1 for x in loops if strobe(x) and bit(x, INC_BIT)))
    # bit 59 of a read names the MDR the next word takes the data from
    rp = [0, 0, 0, 0]
    for a, x in nz:
        y = falls_to(img, a)
        if strobe(x) != 'R' or not y or strobe(y) or field(y, 'AS2') != AS2_MDR:
            continue
        use = field(y, 'CCF') & 3
        if use in (1, 2):
            rp[2 * bit(x, MDR_SEL_BIT) + (use == 2)] += 1
    out['read_port'] = tuple(rp)
    # bit 58 of a strobe word names the MAR the word before loaded
    ap = [0, 0, 0, 0]
    am = [0, 0, 0, 0]
    for a, x in nz:
        p = came_from(img, a)
        if len(strobe(x)) != 1 or not p:
            continue
        if field(p, 'SD1') in (MAR1, MAR2):
            ap[2 * (field(p, 'SD1') == MAR2) + bit(x, MAR_SEL_BIT)] += 1
        if field(p, 'AS1') in (MAR1, MAR2):
            am[2 * (field(p, 'AS1') == MAR2) + bit(x, MAR_SEL_BIT)] += 1
    out['addr_port'], out['alu_dst_port'] = tuple(ap), tuple(am)
    # SC2 codes 8, 9, b are immediates: they exclude the branch kinds that need the same EM bits
    s8 = [x for _, x in nz if field(x, 'SC2') == SC2_EM1]
    s9 = [x for _, x in nz if field(x, 'SC2') == SC2_EM2]
    sb = [x for _, x in nz if field(x, 'SC2') == SC2_WIDE]
    out['sc2_immediates'] = (
        len(s8), sum(1 for x in s8 if field(x, 'JMP') == ABSOLUTE),
        len(s9), sum(1 for x in s9 if field(x, 'JMP') in (3, 5, 6, 7)),
        len(sb), sum(1 for x in sb if field(x, 'JMP')))
    # the words the exclusion does not cover: JMPF 1 (all must be ends or returns, which
    # carry no address) and SC2 = 9 with JMPF 2 (not excluded: 3 words in image 2)
    j1 = [x for x in s8 + s9 if field(x, 'JMP') == 1]
    out['sc2_other_branches'] = (len(j1), sum(1 for x in j1 if field(x, 'EM') & J1_JUMP),
                                 sum(1 for x in s9 if field(x, 'JMP') == BRANCH))
    # runs of two or more consecutive writes of MDR1: (runs, words before the last one,
    # of those loading MDR1 through SD1, last words loading it).  A write that stored
    # what its own word loads would need the load in the last word as often as before.
    runs = early = early_load = last_load = 0
    a = 0

    def w1(k):
        return k < len(img) and strobe(img[k]) == 'W' and not bit(img[k], MDR_SEL_BIT)
    while a < len(img):
        b = a
        while w1(b) and field(img[b], 'JMP') == 0 and w1(b + 1):
            b += 1
        if b > a:
            runs += 1
            early += b - a
            early_load += sum(1 for k in range(a, b) if field(img[k], 'SD1') == MDR1)
            last_load += field(img[b], 'SD1') == MDR1
        a = b + 1
    out['write_runs'] = (runs, early, early_load, last_load)
    # bit 57 qualifies a register select
    wb = [x for _, x in nz if bit(x, WRB_BIT)]
    out['wrb'] = (len(wb), sum(1 for x in wb if not field(x, 'DST') and not field(x, 'SC1')
                               and not field(x, 'SC2')),
                  sum(1 for x in wb if 8 <= field(x, 'SC1') <= 0xb),
                  sum(1 for x in wb if field(x, 'DST') >= 0x10),
                  sum(1 for x in wb if field(x, 'DST')))
    # bits 17..16 = 1 stamp the tag immediate on what SD1 loads
    x1 = [x for _, x in nz if field(x, 'x17') == 1]
    out['stamp_sd1'] = (sum(1 for x in x1 if field(x, 'SD1')), len(x1))
    # XR <- base, YR <- constant, then MAR1 <- XR + YR: the constants
    cs = []
    for a, x in nz:
        y = falls_to(img, a)
        if y and field(x, 'SD2') == YR_SD2 and field(x, 'SC2') in (SC2_EM1, SC2_EM2) \
                and field(y, 'AS1') == MAR1 and field(y, 'AS2') == 0 \
                and field(y, 'AD') == SRC_SUM and field(y, 'AL') == 0:
            cs.append(sc2_immediate(x))
    out['base_plus_constant'] = (len(cs), max(cs) if cs else None)
    return out


def sc2_immediate(x):
    em, c = field(x, 'EM'), field(x, 'SC2')
    return em >> EM1_SHIFT & 63 if c == SC2_EM1 else em >> 4 & 63 if c == SC2_EM2 else None


def regname(x, n):
    if not bit(x, WRB_BIT) and 8 <= n <= 0xb:
        return 'opd%x' % n
    return ('W%02x' if bit(x, WRB_BIT) else 'R%02x') % n


class Walk:
    """Symbolic reading of a straight path under the third-pass rules.

    Values are (tag name or None, text).  An address is (base text, offset).
    Loads made by a word become visible to the next word; a write stores
    the selected MDR as it stood before the word (WRITE_SAME_WORD False).
    Only the constructs of sections 14-16 are modelled; anything else
    makes the affected register unknown (None)."""

    def __init__(self, regs=None):
        self.r = {'XR': None, 'YR': None, MAR1: None, MAR2: None, MDR1: None, MDR2: None}
        self.regs = dict(regs or {})
        self.log = []           # (address, 'R'/'W', (base, offset) or None, data or None)

    def step(self, a, x):
        r, old = self.r, dict(self.r)
        em, x17 = field(x, 'EM'), field(x, 'x17')
        imm = kbn.TAGS.get(em >> EM1_SHIFT & 63, '%02x' % (em >> EM1_SHIFT & 63))
        new = {}
        # phase 1: register file / immediate into the work registers
        sc1, sd1 = field(x, 'SC1'), field(x, 'SD1')
        if sd1:
            name = regname(x, sc1)
            v = self.regs.get(name, (None, name)) if sc1 else None
            if v and x17 & 1:
                v = (imm, v[1])
            if sd1 == XR:
                new['XR'] = v
            elif sd1 in (MDR1, MDR2):
                new[sd1] = v
            elif sd1 in (MAR1, MAR2):
                new[sd1] = (v[1], 0) if v else None
        sc2, sd2 = field(x, 'SC2'), field(x, 'SD2')
        if sd2 == YR_SD2:
            new['YR'] = sc2_immediate(x)
        elif sd2 in (MDR1_SD2, MDR2_SD2):
            name = regname(x, sc2)
            new[MDR1 if sd2 == MDR1_SD2 else MDR2] = \
                None if sc2 in (SC2_EM1, SC2_EM2, SC2_WIDE) else self.regs.get(name, (None, name))
        # phase 2: the ALU, from the registers as the previous words left them
        src, dst, as2, al = field(x, 'AD'), field(x, 'AS1'), field(x, 'AS2'), field(x, 'AL')
        val = None
        if as2 == 0 and al == 0:
            if src == SRC_XR and old['XR']:
                val = old['XR']
            elif src == SRC_SUM and old['XR'] and old['YR'] is not None:
                val = (old['XR'][0], old['XR'][1], old['YR'])
            elif src == 0 and x17 & 2:
                val = (None, '0')
        elif as2 == AS2_MAR and al == 0 and src == 0:
            m = old[MAR2 if bit(x, MAR_SEL_BIT) and strobe(x) else MAR1]
            val = (None, m[0], m[1]) if m else None
        if val and x17 & 2:
            val = (imm,) + tuple(val[1:])
        addr = (val[1], val[2] if len(val) > 2 else 0) if val else None
        if dst in (MAR1, MAR2):
            new.setdefault(dst, addr)
        elif dst in (MDR1, MDR2):
            new.setdefault(dst, val)
        elif dst == XR:
            new['XR'] = val
        d = field(x, 'DST')
        if d:
            self.regs[regname(x, d)] = val if val and len(val) == 2 else \
                ((val[0], '%s+%d' % (val[1], val[2])) if val else None)
        # the memory access
        for kind in strobe(x):
            mar = MAR2 if bit(x, MAR_SEL_BIT) else MAR1
            mdr = MDR2 if bit(x, MDR_SEL_BIT) else MDR1
            src_regs = {**old, **new} if WRITE_SAME_WORD else old
            self.log.append((a, kind, old[mar], src_regs[mdr] if kind == 'W' else 'MDR%d' % (mdr - 3)))
            if kind == 'R':
                new.setdefault(mdr, None)
            if bit(x, INC_BIT) and old[mar] and mar not in new:
                new[mar] = (old[mar][0], old[mar][1] + 1)
        r.update(new)

    def run(self, img, path):
        for a in path:
            self.step(a, img[a])
        return self

    def writes(self):
        """[(word, 'base+offset', 'TAG:reg')] for the writes whose address is known."""
        out = []
        for a, kind, m, v in self.log:
            if kind == 'W':
                out.append(('%04x' % a, '%s+%d' % m if m else '?',
                            '%s:%s' % (v[0] or '', v[1]) if v else '?'))
        return out


def fill_after_alloc(img):
    """After a call of the N-cell allocator: offsets from W1c written on the fall-through path."""
    out = {}
    for a, x in enumerate(img):
        if not x or flow(a, x)[0] != 'call' or flow(a, x)[1] not in SIZED_ALLOC:
            continue
        w, k = Walk({'W1c': (None, 'rec')}), a + 1
        for _ in range(40):
            y = img[k]
            if not y:
                break
            kind, t, cond = flow(k, y)
            w.step(k, y)
            if kind == 'call' or kind in ('end', 'return') and not cond:
                break
            k = t if kind == 'jump' and not cond else k + 1
        offs = [m[1] for _, kd, m, _ in w.log if kd == 'W' and m and m[0] == 'rec']
        if offs:
            out['%04x' % a] = (SIZED_ALLOC[flow(a, x)[1]], offs)
    return out


# Paths read in docs/pseudo_pimm_microcode.md sections 17-18.
PATHS = {
    'mwait_first': (0x1d3b, 0x1d3c, 0x1d3d, 0x1d3e, 0x1d3f, 0x1d40, 0x1d50, 0x1d5f, 0x1d60, 0x1d61),
    'mwait_hooked': (0x1d3b, 0x1d3c, 0x1d3d, 0x1d3e, 0x1d3f, 0x1d40, 0x1d53, 0x1d62, 0x1d60, 0x1d61),
    'mwait_rival': (0x1d2c, 0x1d2d, 0x1d2e, 0x1d2f),
    'mwait_rival_close': (0x1d37, 0x1d38, 0x1d39),
    'mwait_add': (0x1d71, 0x1d72, 0x1d73, 0x1d74, 0x1d75, 0x1d76, 0x1d77),
    'suspend_trailer': (0x1c31, 0x1c32, 0x1c0c, 0x1c0d, 0x1c0e, 0x1c0f, 0x1c10),
    'new_vector_descriptor': (0x1e86, 0x1e87, 0x1e88),
    'builtin_goal_tail': (0x3d6a, 0x3d6b, 0x3d6c, 0x3d6d, 0x3d6e),
}


def records(img):
    return {name: Walk({'W1c': (None, 'rec')}).run(img, path).writes()
            for name, path in PATHS.items()}


def rtl(a, x):
    """One line of register transfers for --rtl, under the third-pass rules."""
    if not x:
        return ''
    out, em, x17 = [], field(x, 'EM'), field(x, 'x17')
    imm = kbn.TAGS.get(em >> EM1_SHIFT & 63, '%02x' % (em >> EM1_SHIFT & 63))
    wr = {XR: 'XR', MDR1: 'MDR1', MDR2: 'MDR2', MAR1: 'MAR1', MAR2: 'MAR2'}
    sc1, sd1 = field(x, 'SC1'), field(x, 'SD1')
    if sd1:
        v = regname(x, sc1) if sc1 else '?'
        out.append('%s<-%s' % (wr.get(sd1, 'w%d' % sd1), '{%s,%s}' % (imm, v) if x17 & 1 else v))
    elif sc1:
        out.append('read %s' % regname(x, sc1))
    sc2, sd2 = field(x, 'SC2'), field(x, 'SD2')
    if sd2:
        c = sc2_immediate(x)
        v = '#%d' % c if c is not None else '#wide' if sc2 == SC2_WIDE else regname(x, sc2)
        out.append('%s<-%s' % ({YR_SD2: 'YR', MDR1_SD2: 'MDR1', MDR2_SD2: 'MDR2'}[sd2], v))
    src, dst, as2, al, d = (field(x, n) for n in ('AD', 'AS1', 'AS2', 'AL', 'DST'))
    if src or dst or as2 or al or d or x17 & 2:
        e = {0: '', SRC_XR: 'XR', SRC_YR: 'YR', SRC_SUM: 'XR+YR'}.get(src, 'src%d' % src)
        r = {0: '', 1: 'r1', AS2_MDR: 'MDR', AS2_MAR: 'MAR'}[as2]
        if src == SRC_XR and as2 and not al:    # seen to pass the AS2 operand (R19<-MDR)
            e = ''
        e = ' '.join(t for t in (e, 'op%d' % al if al else '', r) if t) or '0'
        if x17 & 2:
            e = '{%s,%s}' % (imm, e)
        to = [wr.get(dst, 'w%d' % dst)] if dst else []
        to += [regname(x, d)] if d else []
        out.append('%s<-%s' % (','.join(to) or 'alu', e))
    s = strobe(x)
    if s:
        mar = 'MAR%d' % (1 + bit(x, MAR_SEL_BIT)) + ('++' if bit(x, INC_BIT) else '')
        mdr = 'MDR%d' % (1 + bit(x, MDR_SEL_BIT))
        if 'R' in s:
            out.append('%s<-[%s]' % (mdr, mar))
        if 'W' in s:            # the data register of a bit-59 write is not settled (section 16)
            out.append('[%s]<-%s(old)%s' % (mar, mdr, '?' if bit(x, MDR_SEL_BIT) else ''))
    return '; '.join(out)


PINNED = dict(
    img2_flow={'j1_jump': (2830, 2721, 2710, 1430), 'j4': (419, 418, 193, 193),
               'self_jumps': (23, 0), 'after_call': (222, 10)},
    syspsi_flow={'j1_jump': (3973, 3973, 3918, 1899), 'j4': (700, 700, 277, 277),
                 'self_jumps': (37, 0), 'after_call': (250, 13)},
    img2_entry_ends=(96, 0), syspsi_entry_ends=(122, 0),
    register_only_writes=(219, 0), writers_missing_bit=[], non_writers_with_bit=[],
    operand_selects=[True] * 5,
    alloc_sizes=[3, 4, 5, 6, 7, 8, 10, 10, 11, 12, 13, 3, 4, 5, 6, 7, 8],
    put_vector_alloc=[3, 4, 5, 6],
    suspend_size_table=['332c', 3, 4, 5, 6, 10, '334c', 8, 7],
    put_vector_size_table=[3, 4, 5, 6, 13, 12, 11, 10, '334d', 7, 8],
    third_size_table=['3326', '332d', 3, 4, 5, 6],
    gset_param=[1, 1, 1],
    img2_mem={
        'strobes': (2421, 2177, 40), 'read_then_mdr': (854, 1386),
        'mdr_enable': ((0, 833), (0, 918), (0, 355), (0, 327), (1, 483), (0, 300), (3, 3541)),
        'mdr1_then_write': (393, 628), 'xr_pass': (420, 487), 'loops': (23, 23, 19),
        'read_port': (320, 22, 15, 136), 'addr_port': (188, 10, 26, 67),
        'alu_dst_port': (946, 32, 23, 117), 'sc2_immediates': (718, 0, 211, 0, 704, 0),
        'wrb': (6318, 0, 0, 3266, 3373), 'stamp_sd1': (396, 397),
        'base_plus_constant': (133, 15), 'sc2_other_branches': (33, 0, 3),
        'write_runs': (181, 357, 196, 17)},
    syspsi_mem={
        'strobes': (3837, 2337, 512), 'read_then_mdr': (907, 1867),
        'mdr_enable': ((8, 1053), (12, 1142), (10, 607), (0, 466), (15, 967), (0, 390),
                       (43, 4505)),
        'mdr1_then_write': (258, 721), 'xr_pass': (245, 341), 'loops': (37, 36, 36),
        'read_port': (238, 28, 8, 140), 'addr_port': (244, 33, 48, 125),
        'alu_dst_port': (441, 41, 52, 255), 'sc2_immediates': (1339, 0, 426, 0, 747, 0),
        'wrb': (6148, 0, 0, 3500, 3660), 'stamp_sd1': (460, 461),
        'base_plus_constant': (10, 13), 'sc2_other_branches': (69, 0, 0),
        'write_runs': (62, 124, 54, 4)},
    # after a call of the N-cell allocator: (N, offsets written from the new record)
    fill_after_alloc={'1b4a': (3, [0, 1, 2]), '1d3a': (4, [2, 0, 1]), '1f99': (4, [0]),
                      '30f3': (6, [0, 1, 2, 3, 4, 5]), '311d': (5, [0, 1, 2, 3, 4]),
                      '312b': (6, [0, 1, 2, 3, 4, 5])},
    # (word, cell, tag:register written), doc sections 17-18
    records={
        'mwait_first': [('1d3d', 'rec+2', 'HOOKo:W11'), ('1d3e', 'rec+0', 'DREF:W16'),
                        ('1d60', 'rec+1', 'ATOMo:R06'), ('1d61', 'W16+0', 'MHOOK:rec')],
        'mwait_hooked': [('1d3d', 'rec+2', 'HOOKo:W11'), ('1d3e', 'rec+0', 'DREF:W16'),
                         ('1d60', 'rec+1', 'HOOKx:W14'), ('1d61', 'W16+0', 'MHOOK:rec')],
        'mwait_rival': [('1d2f', 'W13+3', 'MHOOK:W17')],
        'mwait_rival_close': [('1d39', 'W13+3', 'MHOOK:W12')],
        'mwait_add': [('1d73', 'rec+15', 'ATOMo:R06'), ('1d75', 'W17+2', 'HOOKo:W11'),
                      ('1d77', 'W16+0', 'MHOOK:W17')],
        'suspend_trailer': [('1c32', '?', '?'), ('1c0d', 'W15+12', ':W10'),
                            ('1c0e', 'W15+13', ':R12'), ('1c0f', 'W15+14', ':R13'),
                            ('1c10', 'W15+15', '?')],
        'new_vector_descriptor': [('1e86', '?', '?'), ('1e87', '?', 'INTo:W11'),
                                  ('1e88', '?', 'INTo:W11')],
        'builtin_goal_tail': [('3d6d', 'R1b+0', '?'), ('3d6e', 'R1b+1', ':W1a')]},
    # enqueue_goal's four writes through MAR2 (strobe, bit 58, bit 60) and the COD stamp
    enqueue_trailer=[('W', 1, 1), ('W', 1, 1), ('W', 1, 1), ('W', 1, 0), 'COD', 12],
    img1_nonzero=17496, img1_equal_syspsi=17496, img2_nonzero=18343,
    img2_equal_img1=15, image_tags_nonzero=0,
    run2_len=331, run2_distinct=324, run2_descents=0, run2_landing=331,
    run2_descents_low15_only=22, run2_landing_low15_only=319,
    run1_len=459, run1_descents=7, run1_landing=457, run1_descents_low15_only=61,
    kl1_entries=216, kl1_entries_landing=216,
    sysidat=(1040, 496, 16, 0),
    syspsi_jmp5=(1455, 1455), img2_jmp5=(2127, 1889, 238, 238, 15),
    img2_page_relative=((2, 532, 525), (3, 246, 246), (6, 1497, 1497), (7, 231, 231)),
)

# name -> tag immediate its decode entry must carry.  None of these was
# used to find the rule; the tag values are asm/kbn.py's TAGS (from the
# PIMOS inspector's source).
ENTRY_TAGS = {
    'atom': 'ATOMo', 'integer': 'INTo', 'list': 'LISTo', 'code': 'COD', 'module': 'MOD',
    'wait_atom': 'ATOMo', 'wait_nil': 'ATOMo', 'wait_integer': 'INTo', 'wait_list': 'LISTo',
    'wait_vector': 'VECTo', 'set_atom': 'ATOMo', 'put_atom': 'ATOMo', 'write_atom': 'ATOMo',
    'set_integer': 'INTo', 'put_integer': 'INTo', 'write_integer': 'INTo',
    'switch_on_non_integer': 'INTo', 'switch_on_non_atom': 'ATOMo',
    'switch_on_non_list': 'LISTo', 'collect_list': 'LISTo', 'collect_vector': 'VECTo',
}
TAG = {v: k for k, v in kbn.TAGS.items()}


def field(x, name):
    for n, hi, lo in FIELDS:
        if n == name:
            return (x >> lo) & ((1 << (hi - lo + 1)) - 1)
    raise KeyError(name)


class Firmware:
    def __init__(self):
        self.ws = psdpim.words(psdpim.member('PMPSI.DIR/pimm.MEkbn'))
        self.img1 = self._image(IMG1, IMG1_LEN)
        self.img2 = self._image(IMG2, IMG2_LEN)
        self.tb = psdpim.table(self.ws)
        self.names = psdpim.names()

    def _image(self, base, n):
        ws = self.ws
        return [ws[base + 2 * i][0] | ws[base + 2 * i + 1][0] << 32 for i in range(n)]

    def run(self, span):
        """A descriptor's list of decode indices (16-bit, high half first)."""
        out = []
        for i in range(*span):
            out += [self.ws[i][0] >> 16, self.ws[i][0] & 0xffff]
        return out[:-1]         # the last word (tag 0a) holds one index

    def entry(self, index):
        return self.tb[index >> 8][index & 255]

    def start(self, index, low15_only=False):
        """(address, tag immediate or None) of a decode entry."""
        (_, _), (v, t) = self.entry(index)
        if t & 0x18 and not low15_only:
            return (index >> 7) << 11 | v & 0x3ff, v >> 10 & 0x3f
        return v & 0x7fff, None

    def kl1_entries(self):
        """{name: (index, address, tag immediate)} for classes 2 (GMI), 3 (KLB)."""
        out = {}
        for cls, tag in ((2, 0x22), (3, 0x23)):
            named = dict(self.names[tag])
            for fam, lo, hi in psdpim.FAMILIES[tag]:
                for op in range(lo, hi + 1):
                    named.setdefault(op, '%s[%02x]' % (fam, op - lo))
            for op in range(256):
                if self.tb[cls][op] != psdpim.EMPTY:
                    idx = cls << 8 | op
                    out[named.get(op, '%d:%02x' % (cls, op))] = (idx,) + self.start(idx)
        return out


def syspsi():
    raw = psdpim.member('PMPSI.DIR/syspsi')[256:]
    return [int.from_bytes(raw[i:i + 8], 'little') for i in range(0, len(raw), 8)]


def sorted_run(fw, run, image, **kw):
    seq = [fw.start(i, **kw)[0] for i in run]
    descents = sum(1 for a, b in zip(seq, seq[1:]) if b < a)
    landing = sum(1 for a in seq if a < len(image) and image[a])
    return descents, landing


def measure():
    fw = Firmware()
    psi = syspsi()
    got = {}
    got['img1_nonzero'] = sum(1 for x in fw.img1 if x)
    got['img1_equal_syspsi'] = sum(1 for a, x in enumerate(fw.img1) if x and x == psi[a])
    got['img1_differs'] = sum(1 for a, x in enumerate(fw.img1) if x != psi[a])
    got['img2_nonzero'] = sum(1 for x in fw.img2 if x)
    got['img2_equal_img1'] = sum(1 for a, x in enumerate(fw.img1) if x and x == fw.img2[a])
    got['image_tags_nonzero'] = sum(1 for v, t in fw.ws[IMG1:IMG1 + 2 * IMG1_LEN] if t) + \
        sum(1 for v, t in fw.ws[IMG2:IMG2 + 2 * IMG2_LEN] if t)
    # the descriptors' pointers are file words + the header's load address
    ws = fw.ws
    got['pointers'] = [
        ws[0x801] == (LOAD + 0x803, 0x1c), ws[0x802] == (LOAD + DESC2, 0x0b),
        ws[0x803] == (LOAD + IMG1, 0), ws[0x804] == (IMG1_LEN << 16, 0),
        ws[DESC2] == (LOAD + IMG2, 0), ws[DESC2 + 1] == (IMG2_LEN << 16, 0),
        # decode word 1's high half names the descriptor link word of its image
        all(fw.tb[c][op][0][0] >> 16 == LOAD + 0x801 for c in (0, 1) for op in range(256)
            if fw.tb[c][op] != ((0, 0), (0, 0))),
        all(fw.tb[c][op][0][0] >> 16 == LOAD + 0x802 for c in (2, 3) for op in range(256)
            if fw.tb[c][op] != psdpim.EMPTY),
        int.from_bytes(psdpim.member('PMPSI.DIR/pimm.MEkbn')[:4], 'little') == LOAD,
    ]
    # descriptor 2's list is exactly the populated entries of classes 2, 3,
    # in order of start address
    r1, r2 = fw.run(RUN1), fw.run(RUN2)
    populated = {c << 8 | op for c in (2, 3) for op in range(256)
                 if fw.tb[c][op] != psdpim.EMPTY}
    got['run2_is_populated_kl1'] = set(r2) == populated
    got['run2_len'], got['run2_distinct'] = len(r2), len(set(r2))
    got['run2_descents'], got['run2_landing'] = sorted_run(fw, r2, fw.img2)
    got['run2_descents_low15_only'], got['run2_landing_low15_only'] = \
        sorted_run(fw, r2, fw.img2, low15_only=True)
    got['run1_len'] = len(r1)
    got['run1_descents'], got['run1_landing'] = sorted_run(fw, r1, fw.img1)
    got['run1_descents_low15_only'] = sorted_run(fw, r1, fw.img1, low15_only=True)[0]
    ents = fw.kl1_entries()
    got['kl1_entries'] = len({fw.entry(i) for i, _, _ in ents.values()})
    got['kl1_entries_landing'] = len({fw.entry(i) for i, a, _ in ents.values()
                                      if a < IMG2_LEN and fw.img2[a]})
    # tag immediates carried by decode entries
    bad = [n for n, t in ENTRY_TAGS.items() if ents[n][2] != TAG[t]]
    bad += ['wait_vector_%d' % n for n in range(7)
            if fw.start(0x3a8 + n)[1] != TAG['VECT%do' % n]]
    got['entry_tags_wrong'] = bad
    # tag immediates in the code the put_vector_N entries start at
    pv = []
    for n in range(7):
        a = fw.start(0x338 + n)[0]
        ok = a + 1 < IMG2_LEN and any(field(fw.img2[a + k], 'EM') >> 10 == TAG['VECT%do' % n]
                                      for k in (0, 1))
        if not ok:
            pv.append(n)
    got['put_vector_tags_wrong'] = pv
    # branch kinds
    j5 = [x & 0xffff for x in psi if x and field(x, 'JMP') == ABSOLUTE]
    got['syspsi_jmp5'] = (len(j5), sum(1 for t in j5 if t < len(psi) and psi[t]))
    j5 = [x & 0xffff for x in fw.img2 if x and field(x, 'JMP') == ABSOLUTE]
    far = [t for t in j5 if t >= IMG2_LEN]
    got['img2_jmp5'] = (len(j5), sum(1 for t in j5 if t < IMG2_LEN and fw.img2[t]),
                        len(far), sum(1 for t in far if t < len(psi) and psi[t]), len(set(far)))
    rel = []
    for j in PAGE_RELATIVE:
        hits = [(a, x) for a, x in enumerate(fw.img2) if x and field(x, 'JMP') == j]
        rel.append((j, len(hits),
                    sum(1 for a, x in hits if fw.img2[a & ~0x3ff | x & 0x3ff])))
    got['img2_page_relative'] = tuple(rel)
    # sysidat is the class 0/1 half of the decode table, packed: value and
    # tag of the second word, a zero byte, the first word's low 16 bits
    raw = psdpim.member('PMPSI.DIR/sysidat')[256:]
    recs = [raw[i:i + 8] for i in range(0, len(raw), 8)]

    def same(r, index):
        (v1, _), (v2, t2) = fw.entry(index)
        return (int.from_bytes(r[:4], 'little'), r[4], r[5],
                int.from_bytes(r[6:], 'little')) == (v2, t2, 0, v1 & 0xffff)
    differ = [i for i in range(512) if not same(recs[i], i)]
    got['sysidat'] = (len(recs), 512 - len(differ),
                      sum(1 for k in range(16) if same(recs[1024 + k], 0x1a0 + k)),
                      sum(1 for r in recs[512:1024] if any(r)))
    got['sysidat_differ_1a0_1af'] = differ == list(range(0x1a0, 0x1b0))
    # --- second pass: control flow, the write bit, operand selects, allocators
    im = fw.img2
    got['img2_flow'], got['syspsi_flow'] = flow_measure(im), flow_measure(psi)
    e2 = [first_end(im, a) for a in {a for _, a, _ in ents.values()}]
    e1 = [first_end(psi, a) for a in {fw.start(i)[0] for i in r1}]
    got['img2_entry_ends'] = (e2.count('end'), e2.count('return'))
    got['syspsi_entry_ends'] = (e1.count('end'), e1.count('return'))
    ro = [x for lo, hi in REGISTER_ONLY for x in im[lo:hi] if x]
    got['register_only_writes'] = (len(ro), sum(1 for x in ro if x >> MEM_BIT & 1))

    def writes(name):           # any word of the routine's straight line has the bit
        a, hit = ents[name][1], False
        while True:
            hit |= bool(im[a] >> MEM_BIT & 1)
            if not flow(a, im[a])[2]:
                return hit
            a += 1
    got['writers_missing_bit'] = [w for w in WRITERS if not writes(w)]
    got['non_writers_with_bit'] = [w for w in NON_WRITERS if writes(w)]
    pi, pa, pv = ents['put_integer'][1], ents['put_atom'][1], ents['put_value'][1]
    wi, wa = ents['wait_integer'][1], ents['wait_atom'][1]
    got['operand_selects'] = [
        im[pi] == im[pv],                               # register operand not in the word
        im[pi] ^ im[pa] == 1 << 52,                     # DST 9 against DST 8
        (field(im[pi], 'DST'), field(im[pa], 'DST')) == (9, 8),
        (field(im[wi], 'SC1'), field(im[wa], 'SC1')) == (9, 8),
        (field(im[wi + 1], 'DST'), field(im[wa + 1], 'DST')) == (9, 8),
    ]
    al = allocators(im)
    got['alloc_sizes'] = [al[a] for a in sorted(al)]
    got['put_vector_alloc'] = [al.get(flow(a, im[a])[1]) for a in
                               (fw.start(0x338 + n)[0] for n in range(3, 7))]

    def table(addrs):           # allocator index where the target is an N-word, else the address
        return [al.get(flow(a, im[a])[1], '%04x' % flow(a, im[a])[1]) for a in addrs]
    got['suspend_size_table'] = table((0x1c40, 0x1c41, 0x1c42, 0x1c43, 0x1c44,
                                       0x1c5b, 0x1c5c, 0x1c5d, 0x1c5e))
    got['third_size_table'] = table(range(0x4e41, 0x4e47))
    param = psdpim.text(psdpim.member('SYSTEM.DIR/PIMM.PARAM'))
    got['gset_param'] = [sum(1 for ln in param if ln.replace(' ', '').startswith(w))
                         for w in GSET_PARAM]
    got['put_vector_size_table'] = table((0x31ac, 0x31ae, 0x31b0, 0x31b2, 0x31c0, 0x31c1,
                                          0x31c2, 0x31c3, 0x31c4, 0x31c5, 0x31c6))
    # --- third pass: the memory datapath
    got['img2_mem'], got['syspsi_mem'] = mem_measure(im), mem_measure(psi)
    got['fill_after_alloc'] = fill_after_alloc(im)
    got['records'] = records(im)
    got['enqueue_trailer'] = [(strobe(im[a]), bit(im[a], MAR_SEL_BIT), bit(im[a], INC_BIT))
                              for a in range(0x4c04, 0x4c08)] + \
        [kbn.TAGS.get(field(im[0x4c03], 'EM') >> EM1_SHIFT), field(im[0x4c03], 'EM') >> 4 & 63]
    return got


def check():
    got = measure()
    want = dict(PINNED, img1_differs=0, pointers=[True] * 9, run2_is_populated_kl1=True,
                entry_tags_wrong=[], put_vector_tags_wrong=[],
                sysidat_differ_1a0_1af=True)   # second-pass pins are in PINNED
    bad = {k: (got.get(k), v) for k, v in want.items() if got.get(k) != v}
    if bad:
        print('mekbn: FAIL %r' % bad)
        return 1
    print('mekbn: PASS (image 1 = syspsi 0..57ff on all %d non-zero words; descriptor '
          'pointers are file word + 4200; descriptor 2 lists the %d populated KL1 decode '
          'entries in start-address order with 0 descents and every start on a non-zero '
          'microinstruction (22 descents, %d landing, if the low 15 bits are taken as the '
          'address throughout); %d entry tag immediates and 7 put_vector_N routines carry '
          'the tag kbn.TAGS predicts; JMPF 5 absolute %d/%d in syspsi; JMPF 2,3,6,7 '
          'page-relative; second pass: JMPF 1 jump targets land %d/%d in image 2 and '
          '%d/%d in syspsi, calls lead to a return %d times and to an instruction end %d, '
          'decode entries to an end %d times and to a return %d, backward JMPF 4 lands '
          '%d/%d, bit 62 is set in %d of %d register-only words)'
          % (got['img1_equal_syspsi'], got['run2_distinct'], got['run2_landing_low15_only'],
             len(ENTRY_TAGS) + 7, got['syspsi_jmp5'][1], got['syspsi_jmp5'][0],
             got['img2_flow']['j1_jump'][2], got['img2_flow']['j1_jump'][1],
             got['syspsi_flow']['j1_jump'][2], got['syspsi_flow']['j1_jump'][1],
             got['img2_flow']['after_call'][0], got['img2_flow']['after_call'][1],
             got['img2_entry_ends'][0], got['img2_entry_ends'][1],
             got['img2_flow']['j4'][3], got['img2_flow']['j4'][2],
             got['register_only_writes'][1], got['register_only_writes'][0]))
    m = got['img2_mem']
    print('mekbn: third pass: a read (bit 61) is followed by a use of the MDR %d/%d; MDR1/MDR2 '
          'need bit 58/59 in all but %d of %d strobe-free uses; after an N-cell allocator '
          'call the writes (bit 62, bit 60 stepping) fill cells 0..N-1 at %d sites; pinned '
          'record writes: %s'
          % (m['read_then_mdr'] + (sum(v for v, _ in m['mdr_enable']),
                                   sum(n for _, n in m['mdr_enable']),
                                   sum(1 for n, o in got['fill_after_alloc'].values()
                                       if o == list(range(n))),
                                   ', '.join('[%s]<-%s' % w[1:]
                                             for w in got['records']['mwait_first']))))
    return 0


def fmt(a, x):
    s = '%04x %016x ' % (a, x)
    if not x:
        return s
    s += ' '.join('%s=%x' % (n, field(x, n)) for n, _, _ in FIELDS if field(x, n))
    j, em = field(x, 'JMP'), field(x, 'EM')
    kind, t, falls = flow(a, x)
    if j == 1:
        s += '   %s%s%s' % (kind, '' if t is None else ' %04x' % t, ' ?' if falls else '')
        s += ' bit0' if em & 1 else ''         # EM bit 0: not understood
    elif j == 4:
        s += '   jump %04x' % t
    elif j == ABSOLUTE:
        s += '   call %04x' % em
    elif j in PAGE_RELATIVE:
        s += '   %s %04x' % (kind, t)
    if j != 1 and (j in PAGE_RELATIVE or field(x, 'x17')) or j == 1 and not em & J1_JUMP and em >> 10:
        s += ' imm %02x %s' % (em >> 10, kbn.TAGS.get(em >> 10, ''))
    return s


def main(argv):
    if '--check' in argv:
        return check()
    fw = Firmware()
    if '--segments' in argv:
        print('load address %04x, %d words' % (LOAD, len(fw.ws)))
        for name, a, b in (('decode table', 0, 0x800), ('descriptor 1', DESC1, 0x8ed),
                           ('image 1 (= syspsi 0..57ff)', IMG1, IMG1 + 2 * IMG1_LEN),
                           ('descriptor 2', DESC2, 0xb9aa),
                           ('image 2 (KL1 microprogram)', IMG2, IMG2 + 2 * IMG2_LEN)):
            print('  %05x-%05x  %s' % (a, b - 1, name))
        return 0
    if '--entries' in argv:
        for name, (idx, a, t) in sorted(fw.kl1_entries().items(), key=lambda kv: kv[1][1]):
            print('%04x  %03x  %-34s %s' % (a, idx, name,
                                            '' if t is None else 'imm %02x %s'
                                            % (t, kbn.TAGS.get(t, ''))))
        return 0
    if '--dis' in argv:
        i = argv.index('--dis')
        a = int(argv[i + 1], 16)
        n = int(argv[i + 2]) if len(argv) > i + 2 else 16
        for k in range(a, min(a + n, IMG2_LEN)):
            print(fmt(k, fw.img2[k]))
        return 0
    if '--rtl' in argv:
        i = argv.index('--rtl')
        a = int(argv[i + 1], 16)
        n = int(argv[i + 2]) if len(argv) > i + 2 else 16
        for k in range(a, min(a + n, IMG2_LEN)):
            x = fw.img2[k]
            kind, t, cond = flow(k, x) if x else ('', None, False)
            ctl = '' if kind in ('', 'next') else '  | %s%s%s' % (
                kind, '' if t is None else ' %04x' % t,
                '?' if cond and kind not in ('call', 'branch') else '')
            print('%04x %016x  %s%s' % (k, x, rtl(k, x), ctl))
        return 0
    if '--records' in argv:
        for name, ws in records(fw.img2).items():
            print(name)
            for w in ws:
                print('    %s  [%s] <- %s' % w)
        return 0
    if '--tag' in argv:
        t = TAG[argv[argv.index('--tag') + 1]]
        for a, x in enumerate(fw.img2):
            if not x or field(x, 'EM') >> 10 != t or field(x, 'JMP') == 1:
                continue
            if field(x, 'x17'):
                print('stamp   ' + fmt(a, x))
            elif field(x, 'JMP') in PAGE_RELATIVE:
                print('branch  ' + fmt(a, x))
        return 0
    if '--alloc' in argv:
        al = allocators(fw.img2)
        for t in sorted(al):
            sites = ['%04x' % a for a, x in enumerate(fw.img2) if x and flow(a, x)[1] == t]
            print('%04x  index %2d  %s' % (t, al[t], ' '.join(sites)))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
