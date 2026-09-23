#!/usr/bin/env python3
"""strap_asm.py -- a STRAP-1 assembler for the IBM 7030 "Stretch",
targeting the encodings established in stretch/bsv/StretchDecode.bsv /
StretchExecute.bsv (see opcodes.py for the shared table and citations).

SCOPE (implemented / not, and why -- mirrors the "decode completely,
execute partially, document the rest" ethos of the Bluespec model):

  Pseudo-ops:  DD, VF, XW, END, SYN, SLC, CNOP.
  Not yet:     CF, RF, DDI, CW, EXT (raise AssemblerError citing
               C22-6531 rather than silently guessing).

  CNOP (C22-6531 "CNOP": "the machine instruction NOP is compiled" to
  bridge a half-word-to-full-word rounding gap): rounds the location
  counter up to the next full word, compiling a NOP into the half-word
  skipped if there was one, nothing otherwise. Implemented as a
  zero-size, full-word-aligned statement that counts as an instruction
  for the automatic gap filler already used before every full-word
  instruction -- so the listing's explicit "CNOP" rows (docs/
  ja_ax1a_ibox-1.pdf p.45 005211.40 -> 0.30 00; p.46 005246.40 ->
  nothing) assemble to exactly what they print.

  SLC ("A | SLC, Y" -- C22-6531 p.32, "Set Location Counter"): resets
  the location counter to the bit-address expression Y; the next
  statement is compiled there, subject to the same rounding-upward
  alignment every statement already gets (a full-word instruction
  after `SLC, 5.32` lands at 6.0). Y must be evaluable when the SLC
  is reached in pass 1 -- location-counter symbols defined ABOVE it,
  or SYNs whose own chains are resolvable by then (resolved eagerly at
  that point, see assemble()) -- and must be non-negative; a forward
  reference is an AssemblerError, matching the manual's own
  restriction ("it must be evaluable by the time it is encountered in
  pass 2 of Strap-1"). A bare integer in Y counts as BITS, not words
  (p.32: "added in as a 24-bit address field; i.e., as an integral
  number of bits") -- write `2860.0` for word 2860, same as any other
  address expression here. The name field is ignored (p.32) -- an SLC
  never defines a symbol. Needed for real historical listings, whose
  routines sit at fixed addresses far above this assembler's default
  origin (I-Box 1's WEN/WEN2/VEN at octal 5454-5461, see
  programs/ibox1_wen_ven_original_addresses.strap).

  "(R)" radix literals are accepted in ANY expression, not only inside
  DD: "(8)37777", "IBR9+(8).04", "VF,(8)777777.70" -- both halves of a
  bit address in the given radix. C22-6531 defines the "(R)" entry
  mode for DD data (pp.27-28); that STRAP II applied the same prefix
  in address fields is established by the I-Box 4 listing's own
  printed machine code for those three forms (see tokenize_expr and
  verify_ibox4_listing.py). A bare "NOP," (empty address field, the
  listings' NOP-placeholder form, printed 0.30 00) compiles as
  address 0.

  SYN ("A | SYN(dds), Y" -- C22-6531 p.31): defines a symbol's value
  from its own operand expression Y, not the location counter --
  occupies no storage. An earlier version of this code treated SYN
  like a no-storage pseudo-op WITHOUT evaluating its operand and
  silently gave the name the current location counter instead -- wrong
  output with no error; that was caught during review and fixed by
  refusing to assemble SYN at all until done correctly. Now resolved
  by a forward-reference-tolerant fixpoint pass, run once every
  location-counter symbol is known: each SYN's expression may
  reference a symbol not yet resolved (another SYN, most commonly --
  C22-6531's own words, "this may possibly mean as late as pass 3 of
  Strap-1"), so unresolved SYNs are retried each round until a round
  makes no progress; whatever's left names a genuinely undefined or
  circular chain and raises with that chain shown. Verified against
  C22-6531's own worked example (p.31 "Example B": ALF=DDI(B),-142;
  JIM=SYN(B,24),389; RIP=SYN(B,24),-210; LI,ALF;+I,JIM;+I,JIM+RIP -->
  accumulator = 426, since JIM+RIP resolves to 179 through two chained
  SYN lookups -- see strap/tests or run_tests.sh). SYN's own (dds)
  modifier, when given, is also supposed to set the *data description*
  an instruction implicitly inherits by naming the symbol -- out of
  scope here, since this assembler's symtab only ever stores numeric
  values for any symbol, not per-symbol dds metadata (see
  emit_statement's SYN case for the same note in context).

  Instruction formats:
    1  Floating point            -- the N/U normalize mode bit
                                     (`unnorm`) and the sign modifiers
                                     N/A/NA (negative/absolute; suffix on
                                     the mnemonic, e.g. LN/LA/LNA -> the
                                     invSign/absSign bits, strip_fp_sign).
                                     The sign modifiers were added when
                                     the floating-point diagnostic
                                     jb_af1c needed them; verified
                                     bit-for-bit against its printed code
                                     (verify_fp_signmods.py).
    2  Misc / unconditional branch / SIC -- branch mnemonics only
       (B BR BE BD BEW NOP); R/RCZ/Z decode but are low-confidence
       (register-operand field placement not confirmed against a
       worked example). SIC ("SIC, Y(I)" -- Store Instruction Counter
       If, Reference Manual p.41) is a full-word prefix: it occupies
       one half-word itself (bits 0-23 = Y as a bit address, 24-27 =
       1000, 28-31 = I) and the NEXT statement in the source must be
       a half-word branch (B/BR/BE/BD/BEW/NOP, any CB variant, or a
       Branch on Indicator), which becomes bits 32-63 of the same
       64-bit instruction; anything else there is an AssemblerError.
       SIC itself is only half-word aligned -- the listings start
       them at either half of a word (docs/ja_ax1a_ibox-1.pdf p.50,
       ISCB2 at 005414.40), matching the Reference Manual's
       19-bit-address instruction fetch. Encoding verified against
       that page's printed machine code (verify_ibox1_listing.py).
    3  Direct index arithmetic    -- full.
    4  Immediate index arithmetic -- full (LVS excluded, see opcodes.py).
    5  Count and branch           -- full: all 16 CB[R][Z][H|+|-]
       mnemonic variants (v/refill/branch-on-zero), see opcodes.py's
       CB_CODES for the mnemonic grammar and its sourcing (pocket
       card + cross-checked against real occurrences transcribed from
       docs/jb_ax4b_ibox-4.pdf section 150).
    6  Branch on indicator        -- full (B[Z]<indicator>[Z] grammar,
       C22-6531 Appendix A footnote 2).
    7  VFL arithmetic             -- full (binary modes B/BU only;
       decimal D/DU encode but StretchExecute.bsv flags them OP
       invalid, matching the Bluespec model's own documented scope).
       Includes Immediate addressing (P=4, Appendix A footnote 4's
       I/N/NI suffixes -- only I is implemented; N/NI are parsed as
       ordinary unrecognized mnemonics, not yet stripped like I is):
       verified against C22-6578 Problem 2.2 Method 2's "LI(BU,7),127"
       and the manual's own worked bit-address derivation for it (see
       encode_vfl_immediate and strap/README.md "Gotchas").
    8  Progressive indexing        -- encoded in full: "OP(OP2)(dds),
       A24(J), OF7(J')" where OP2 in {V+I,V+IC,V+ICR,V-I,V-IC,V-ICR}
       sets the VflAddr.p field (1-3/5-7); shares the format-7 encoder,
       since it's the same instruction word shape with a different P
       value. NOT full end-to-end: J' (i2) is parsed and packed into
       the instruction word, but StretchExecute.bsv's VflInt case never
       reads vi.a.i2 -- the manual's "J' may be used to modify bits
       35-50 of the instruction" (p.21) is unimplemented on the model
       side, same as most of format 7's other unexecuted corners.
       Applies equally to Connectives (below): "OP(OP2)(dds)" is
       exactly as legal there as for VFL arithmetic, per p.75's own
       "Format" section.
    -  Connectives (Figure 6's "CONNECTIVE" row -- same full-word shape
       as format 7 above, opcode field split conn(4)+suffix(5) instead
       of abc(3)+code(6), see enc_connective/CONNECTIVE_SUFFIX) --
       C/CM/CT mnemonics, each followed immediately by exactly 4
       binary digits selecting one of 16 logical functions (Figure 20;
       classify_connective). Direct, immediate, and progressive
       addressing all share format 7's own encoding/parsing path.
       Verified against C22-6578 Problem 2.2 Method 3's "CT0110"
       (byte-equality test via XOR) -- see strap/README.md.
    9  Input-Output -- "OP1(OP2), C(I1), A(I2)" (X22-6533 pocket card).
       All six base mnemonics (RD, W, CTL, LOC, REL, CCW) and their
       SEOP forms (either spelling: "RD(SEOP)" or "RDSEOP") encode; see
       IO_OP in opcodes.py for the derived opcode bits and
       StretchIO.bsv for which of the six StretchExecute.bsv actually
       executes (RD/W/CCW/REL; CTL/LOC decode to Operation Code
       Invalid). C is deliberately NOT unit-converted -- see the
       comment at this format's emit_statement branch for why the
       channel-address field's own scaling (N<<5, not N) is
       characteristically unlike the rest of this codebase's "bare
       integer used as-is" rule and needs to be written explicitly by
       the caller until/unless verified enough to automate.
    10-12 -- BIT BRANCH is implemented (BB_CODES / enc_branch_on_bit)
       and so is TRANSMIT/SWAP (TRANSMIT_CODES / enc_transmit, added
       2026-09-22 from pocket card X22-6533 for jb_ax5b p.45's
       "TI,1,BIT0(X1),$IND").  LVS is not.  This entry used to say all
       three were unimplemented "because StretchExecute.bsv doesn't
       execute them either", which was wrong on both counts: the model
       executes Transmit forward, one word per instruction, and has a
       BranchOnBit arm.  NOTE the resulting hazard, also stated in
       opcodes.TRANSMIT_CODES: the model's Transmit arm IGNORES the
       immediate-count bit and J, so a count other than 1 assembles
       correctly and executes wrongly rather than failing loud.

UNITS -- the one subtlety worth flagging explicitly: this assembler's
internal location counter and every symbol value is a BIT count
(word*64 + bit), matching the 7030's own bit-address addressing and
the Bluespec model's BitAddr type. Two DIFFERENT 19-bit instruction
fields both look like "half-word addresses" but are NOT in the same
units:
  - A DirIndex/BranchInd/BranchOrMisc/CountBranch `addr` field names a
    MEMORY LOCATION at half-word granularity: encode as
    (bit_count >> 5) & 0x7FFFF (drop the 5 bits that select a position
    within a half-word).
  - An ImmIndex `imm` field is ALSO a 19-bit address field for the
    value operations (LVI/LVNI/V+I.../KVI/KVNI): Reference Manual p.25
    puts it into "bits 0-18 of the value field, bits 19-24 set to
    zero", so a bit-address operand is scaled >>5 exactly like the
    branch/DirIndex case, while a bare integer is inserted as an
    integer (C22-6531 p.11) -- eval_addr_field() applies that term by
    term. For the count/refill operations (LCI/LRI/C+I/C-I/KCI) the
    operand is an 18-bit integer in "bits 0-17 of the address part",
    i.e. the field's top 18 bits: (n & 0x3FFFF) << 1. An earlier
    version of this note claimed the field was an unshifted bit count
    for every ImmIndex op; that was wrong on both counts and the
    model agreed with it, so nothing noticed until
    verify_ibox1_listing.py compared "LCI,$X1,4" against the page
    (4.03 02 -- count 4 in bits 0-17) -- README.md "Gotchas" item 16.
    (The direct forms -- VF's value added via V+ -- really are
    bit-precise 25-bit fields, which is what misled the earlier note.)

A THIRD case with its own units, found later (after code already
existed that got it wrong -- see README.md "Gotchas" item 7): XW's
REFILL field packs IndexWord.refill (StretchTypes.bsv, Bit#(18)),
which StretchExecute.bsv feeds straight into st.readWord() -- a WORD
address, not a bit count, unlike VALUE/COUNT in the same XW statement.
Encode with a shift of 6 (bit_count >> 6) & 0x3FFFF, same conversion
as the A18 field above.

A FOURTH case, not a fixed shift this time: VFL Immediate addressing
(P=4)'s A24 field holds the literal operand value itself, but
LEFT-JUSTIFIED within the field's own length rather than placed at
A24's low bits -- see encode_vfl_immediate and README.md "Gotchas".
The shift amount depends on the instruction's OWN field length (dds
length, or 64 if omitted), not a fixed constant like the three cases
above. C22-6578 (p.13) frames this as one instance of a GENERAL STRAP
rule -- any bare (non-"point") integer used as an address is an
"integer address" STRAP must convert to a bit address using the
operation's implied subfield -- but this assembler implements that
conversion ONLY for the immediate-addressing case above; a bare
integer given as a normal (non-immediate) address field is NOT
converted, it's used as a raw bit count via eval_expr with no
subfield-aware scaling. Every program run through this assembler uses
dotted bit-address notation or a label for non-immediate addresses, so
this gap is untested and undocumented as a known limitation rather
than fixed -- see README.md "Next steps".
"""

import re
import sys

from opcodes import (
    VFL_INT_CODES, VFL_INT_MINUS_BASE, FP_CODES, DIR_INDEX_CODES,
    IMM_INDEX_CODES, UNCOND_BRANCH_CODES, MISC_CODES, INDICATOR_BITS,
    MODE_BITS, MODE_DEFAULT_BS, PROGRESSIVE_SECONDARY_OP, CONNECTIVE_SUFFIX,
    IO_OP, CB_CODES, IMM_INDEX_COUNT_OPS, SYSTEM_SYMBOLS, BB_CODES,
    TRANSMIT_CODES,
)

# Input-Output base mnemonics (before an optional "(SEOP)" modifier or
# equivalent "...SEOP" spelling folds into IO_OP's own keys -- see
# emit_statement's IO_OP branch).
IO_BASE_OPS = {'RD', 'W', 'CTL', 'LOC', 'REL', 'CCW'}


class AssemblerError(Exception):
    def __init__(self, msg, lineno=None):
        self.lineno = lineno
        super().__init__(f"line {lineno}: {msg}" if lineno is not None else msg)


# ---------------------------------------------------------------------
# Bit concatenation helper -- mirrors BSV's `{a, b, c, ...}` operator so
# each encoder below reads as the literal field order from Figure 6 /
# StretchTypes.bsv, MSB (IBM bit 0) first.
# ---------------------------------------------------------------------

def cat(*fields):
    """fields: (value, width_bits) pairs, MSB-first. Returns (int, total_width)."""
    result = 0
    total = 0
    for val, width in fields:
        result = (result << width) | (val & ((1 << width) - 1))
        total += width
    return result, total


def encode_vfl_immediate(val, field_len, lineno=None):
    """Pack `val` (an unsigned magnitude, `field_len` bits wide -- 64
    if field_len is 0, the VFL "zero means 64" convention) into the
    24-bit A24 field of a VFL-immediate (P=4) instruction, the exact
    inverse of StretchExecute.bsv's immediateOperand(). Reference
    Manual p.56 "Field Definition": "the effective address itself is
    used as the operand. The field length specifies the number of
    bits in the field starting with the LEFTMOST bit of the effective
    address... If the field length designated is greater than 24,
    zeros are added to the right" -- so a short field is left-
    justified in the 24-bit word (shifted left by 24-field_len), not
    placed at addr24's low bits the way every other address-like
    operand in this assembler is. Getting this backwards packs a
    literal like 127 as addr24=127 (which immediateOperand would then
    read back as bits 0-127 relative to a nonexistent higher radix --
    silently wrong, no error) instead of addr24=127<<17.
    """
    actual_len = 64 if field_len == 0 else field_len
    if actual_len <= 24:
        return (val & ((1 << actual_len) - 1)) << (24 - actual_len)
    # field_len > 24: on real hardware, only the top 24 bits of the
    # value are representable -- immediateOperand always zero-fills
    # the rest, it can't reproduce arbitrary low-order bits. Rather
    # than silently dropping them (the exact "wrong output, no error"
    # failure mode this session's other two fixes were about), refuse
    # to encode a value whose low (actual_len-24) bits are nonzero.
    # Not exercised by any program yet.
    low_bits = actual_len - 24
    if val & ((1 << low_bits) - 1):
        raise AssemblerError(
            f"immediate value {val} has nonzero bits in the low {low_bits} "
            f"bits of a {actual_len}-bit field -- VFL Immediate addressing "
            f"can only represent the top 24 bits there (Reference Manual "
            f"p.56: 'zeros are added to the right')", lineno)
    return (val >> low_bits) & 0xFFFFFF


# ---------------------------------------------------------------------
# Encoders -- one per DecodedInstr shape, field order copied verbatim
# from StretchSmoke.bsv's enc* functions / StretchTypes.bsv structs.
# ---------------------------------------------------------------------

def enc_vfl_full(addr24, i1, p, length, bs, offset, a, b, c, code, i2=0):
    v, w = cat((addr24, 24), (0b1000, 4), (i1, 4), (p, 3), (length, 6),
               (bs, 3), (offset, 7), (a, 1), (b, 1), (c, 1), (code, 6), (i2, 4))
    assert w == 64
    return v

def enc_connective(addr24, i1, p, length, bs, offset, conn, suffix, i2=0):
    # Same full-word shape as enc_vfl_full -- "The connective operations
    # use basically the same full-word instruction format as the
    # integer arithmetic operations" (Reference Manual p.75) -- but the
    # 9-bit opcode field (bits 51-59, enc_vfl_full's a/b/c/code) splits
    # differently here: conn (4 bits, the logical function 0-15,
    # Figure 20) + suffix (5 bits, which of C/CM/CT -- CONNECTIVE_SUFFIX
    # in opcodes.py) instead of the arithmetic sign/decimal modifiers
    # and 6-bit op code.
    v, w = cat((addr24, 24), (0b1000, 4), (i1, 4), (p, 3), (length, 6),
               (bs, 3), (offset, 7), (conn, 4), (suffix, 5), (i2, 4))
    assert w == 64
    return v

def enc_io(addr24, i1, addr18, op4, i2=0):
    # Input-Output, pocket card "INPUT-OUTPUT OPERATIONS": full word,
    # ADDRESS(24, channel address in low 7 bits after indexing) + 1000
    # (24-27) + I(28-31) + ADDRESS(18, 32-49, second effective address)
    # + a 1-bit gap (50, unused but indexable -- Reference Manual p.111:
    # "index arithmetic extends over bits 32 through 50... but only
    # bits 32 through 49 are used") + OP(4, 51-54) + 10000(55-59) +
    # I(60-63). See StretchTypes.bsv's IoOp comment for op4's bit
    # layout (bit weight-4 = SEOP flag; base op in the other 3 bits).
    v, w = cat((addr24, 24), (0b1000, 4), (i1, 4), (addr18, 18), (0, 1),
               (op4, 4), (0b10000, 5), (i2, 4))
    assert w == 64
    return v

def enc_fp(addr18, unnorm, absSign, invSign, code, idx):
    v, w = cat((addr18, 18), (unnorm, 1), (absSign, 1), (invSign, 1), (code, 7), (idx, 4))
    assert w == 32
    return v

def enc_dir_index(addr19, j, code, idx):
    v, w = cat((addr19, 19), (j, 4), (code, 5), (idx, 4))
    assert w == 32
    return v

def enc_imm_index(imm19, j, code):
    v, w = cat((imm19, 19), (j, 4), (0b10000, 5), (code, 4))
    assert w == 32
    return v

def enc_count_branch(addr19, j, v2, refill, bz, idx):
    v, w = cat((addr19, 19), (j, 4), (v2, 2), (0b1001, 4), (refill, 1), (bz, 1), (idx, 1))
    assert w == 32
    return v

def enc_branch_ind(addr19, indnum, clear, branchOn, idx):
    v, w = cat((addr19, 19), (indnum, 6), (0b1000, 4), (clear, 1), (branchOn, 1), (idx, 1))
    assert w == 32
    return v

def enc_branch_or_misc(addr19, code, misc, idx):
    lit = 0b100000 if misc else 0b000000
    v, w = cat((addr19, 19), (code, 3), (lit, 6), (idx, 4))
    assert w == 32
    return v


def enc_transmit(bitaddr24, i1, addr19, j, backward, immCount, swap, i2):
    """TRANSMIT / SWAP, pocket card X22-6533's "TRANSMIT OPERATIONS"
    field diagram (opcodes.TRANSMIT_CODES carries the diagram itself):

      |   ADDRESS   |1000| I |   ADDRESS   | J |FD|BI|10| I |
      0            18  24   28  32          51  55    58 60 63

    A1 is a 24-bit BIT address (bits 0-23) with index I1 at 28-31, the
    literal 1000 at 24-27 shared with SIC and BRANCH ON BIT; A2 is a
    19-bit HALF-WORD address at 32-50 with index I2 at 60-63; J is
    four bits at 51-54, and bits 55-59 are a (backward), b (immediate
    count) and 010 Transmit / 110 Swap.

    Confirmed against a printed instruction before being used:
    jb_ax5b p.45's "TI,1,BIT0%$X1,$IND" prints "24522.00 81
    000013.02 A0", and this function reproduces both half-words."""
    v, w = cat((bitaddr24, 24), (0b1000, 4), (i1, 4),
               (addr19, 19), (j, 4), (backward, 1), (immCount, 1),
               (1 if swap else 0, 1), (0b10, 2), (i2, 4))
    assert w == 64
    return v

def enc_branch_on_bit(bitaddr24, i1, addr19, mod2, cond1, idx1):
    # Branch on Bit, full word (X22-6533 pocket card / RefMan p.41):
    # BIT ADDRESS(24, 0-23) + 1000(24-27) + I(4, 28-31, bit-address
    # index) + BRANCH ADDRESS(19, 32-50) + 111000000(9, 51-59) +
    # mod(2, 60-61) + cond(1, 62) + K(1, 63, X1 flag for branch addr).
    # The identifying literal is the 9-bit 111000000, which is what
    # StretchDecode.bsv keys on (w[12:4]).
    v, w = cat((bitaddr24, 24), (0b1000, 4), (i1, 4), (addr19, 19),
               (0b111000000, 9), (mod2, 2), (cond1, 1), (idx1, 1))
    assert w == 64
    return v


# ---------------------------------------------------------------------
# Expression evaluation.
#
# C22-6531 "Numbers and Symbols" / "Arithmetic Expressions": a term is
# either a symbol, a plain integer, or a bit address "W.B" (word W,
# bit B; W defaults to 0). Terms combine with +/-. A bare "$" is the
# location counter; "$N"/"$XN" (N=0-15) is index register N -- which
# expands differently depending on context (register-field vs
# address-field), per the manual's own worked example ("$5 ... by the
# index field 5 if it appears in an I or J field, or by the address
# 21.0 if it appears in an address field"). `reg_context` selects that.
# ---------------------------------------------------------------------

_TERM_SYS = re.compile(r'[A-Za-z0-9]*')
_TERM_SYM = re.compile(r'[A-Za-z][A-Za-z0-9]*')
_TERM_NUM = re.compile(r'\d+')
_TERM_RADIX = re.compile(r'\((\d+)\)(?=[\d.])')

def tokenize_expr(s, lineno=None):
    s = s.strip()
    i, n = 0, len(s)
    sign = 1
    tokens = []
    while i < n:
        c = s[i]
        if c in ' \t':
            i += 1; continue
        if c == '+':
            sign = 1; i += 1; continue
        if c == '-':
            sign = -1; i += 1; continue
        if c == '$':
            m = _TERM_SYS.match(s, i + 1)
            tokens.append((sign, 'sys', m.group(0)))
            i = m.end(); sign = 1; continue
        if c == '.':
            m = _TERM_NUM.match(s, i + 1)
            b = int(m.group(0)) if m else 0
            tokens.append((sign, 'bitaddr', (0, b)))
            i = m.end() if m else i + 1; sign = 1; continue
        radix = 10
        if c == '(':
            # "(R)" radix entry mode on a numeric term -- C22-6531 defines
            # it for DD data entries (pp.27-28, "(8) 77760" / "(2)..."),
            # and the I-Box 4 listing (docs/jb_ax4b_ibox-4.pdf pp.155,
            # 159) shows STRAP II accepting the same prefix in ADDRESS
            # fields: "XW,IBR9+(8).04,4,-1" prints as value 11445.04,
            # "(8)37777" as count 037777, "VF,(8)777777.70" as
            # 777777.70+. Both halves of a bit address take the radix
            # (".04" octal = 4 bits, ".70" octal = 56 bits), matching how
            # the listing prints bit offsets in octal. Only matched when
            # the parenthesis holds digits and is followed by a digit or
            # "." -- so a trailing "(I)" index modifier (split off before
            # this tokenizer ever runs) can't be mistaken for one.
            m = _TERM_RADIX.match(s, i)
            if not m:
                raise AssemblerError(f"cannot parse expression {s!r} at {s[i:]!r}", lineno)
            radix = int(m.group(1))
            if radix < 2 or radix > 10:
                raise AssemblerError(f"unsupported radix ({radix}) in {s!r}", lineno)
            i = m.end(); c = s[i]
        if c == '.' and radix != 10:
            m = _TERM_NUM.match(s, i + 1)
            b = int(m.group(0), radix) if m else 0
            tokens.append((sign, 'bitaddr', (0, b)))
            i = m.end() if m else i + 1; sign = 1; continue
        if c.isdigit():
            m = _TERM_NUM.match(s, i)
            j = m.end()
            if j < n and s[j] == '.':
                m2 = _TERM_NUM.match(s, j + 1)
                b = int(m2.group(0), radix) if m2 else 0
                tokens.append((sign, 'bitaddr', (int(m.group(0), radix), b)))
                i = m2.end() if m2 else j + 1
            else:
                tokens.append((sign, 'int', int(m.group(0), radix)))
                i = j
            sign = 1; continue
        if c.isalpha():
            m = _TERM_SYM.match(s, i)
            tokens.append((sign, 'sym', m.group(0)))
            i = m.end(); sign = 1; continue
        raise AssemblerError(f"cannot parse expression {s!r} at {s[i:]!r}", lineno)
    if not tokens:
        raise AssemblerError("empty expression", lineno)
    return tokens


def eval_system_symbol(name, loc_bits, reg_context, lineno=None):
    if name == '':
        return loc_bits  # bare "$" = current location counter
    up = name.upper()
    n = None
    if up.startswith('X') and up[1:].isdigit():
        n = int(up[1:])
    elif up.isdigit():
        n = int(up)
    if n is not None and 0 <= n <= 15:
        return n if reg_context else (16 + n) * 64
    if up in INDICATOR_BITS:
        return 11 * 64 + INDICATOR_BITS[up]  # word 11 (indicators), bit = number
    if up in SYSTEM_SYMBOLS:
        w, b = SYSTEM_SYMBOLS[up]        # C22-6531 Appendix A register fields
        return w * 64 + b
    raise AssemblerError(f"unsupported system symbol ${name!r}", lineno)


def eval_expr(expr, symtab, loc_bits, reg_context=False, lineno=None):
    total = 0
    for sign, kind, val in tokenize_expr(expr, lineno):
        if kind == 'int':
            term = val
        elif kind == 'bitaddr':
            w, b = val
            term = w * 64 + b
        elif kind == 'sym':
            up = val.upper()
            if up not in symtab:
                raise AssemblerError(f"undefined symbol {val!r}", lineno)
            term = symtab[up]
        elif kind == 'sys':
            term = eval_system_symbol(val, loc_bits, reg_context, lineno)
        else:
            raise AssemblerError(f"internal: bad token kind {kind}", lineno)
        total += sign * term
    return total


def eval_addr_field(expr, symtab, loc_bits, unit_shift, lineno=None, int_shift=0):
    """Evaluate an expression destined for an ADDRESS field whose unit
    is 2**unit_shift bits (5 for a 19-bit half-word-address field, 6
    for an 18-bit word-address field), applying C22-6531 p.11's rule
    term by term: bit-address terms (W.B, symbols, system symbols) are
    converted to the field's units, while plain integers "add into all
    fields as integers; that is, the units digit adds into the low-
    order position of the field". int_shift: for an operation whose
    19-bit field only uses "bits 0-17 of the effective address" (LX/SX,
    Reference Manual p.24), an integer counts full words, so it lands
    one bit up (I-Box 4 p.58: "SX,$X0,8" prints as word 8, "SV,$X0,2"
    as half-word 2 = 1.0). eval_expr(), by contrast, returns a pure
    bit count."""
    total = 0
    for sign, kind, val in tokenize_expr(expr, lineno):
        if kind == 'int':
            term = val << int_shift
        elif kind == 'bitaddr':
            w, b = val
            term = (w * 64 + b) >> unit_shift
        elif kind == 'sym':
            up = val.upper()
            if up not in symtab:
                raise AssemblerError(f"undefined symbol {val!r}", lineno)
            term = symtab[up] >> unit_shift
        elif kind == 'sys':
            term = eval_system_symbol(val, loc_bits, False, lineno) >> unit_shift
        else:
            raise AssemblerError(f"internal: bad token kind {kind}", lineno)
        total += sign * term
    return total


def eval_reg(expr, symtab, lineno=None):
    """4-bit (or 1-bit, for K fields) register-number field."""
    if expr is None:
        return 0
    return eval_expr(expr, symtab, 0, reg_context=True, lineno=lineno) & 0xF


def referenced_symbols(expr, lineno=None):
    """Programmer symbol names (uppercased) an expression's 'sym' tokens
    reference -- a pure syntax scan, unlike eval_expr, so it can be
    called before those symbols are known to exist. Used by SYN's
    fixpoint resolution (see assemble()) to test "would this expression
    evaluate cleanly right now" without triggering eval_expr's
    undefined-symbol error itself."""
    return {val.upper() for sign, kind, val in tokenize_expr(expr, lineno) if kind == 'sym'}


# ---------------------------------------------------------------------
# Statement-level parsing: name field, operation + parenthesized
# modifiers, comma-separated fields (each optionally carrying its own
# trailing parenthesized index modifier).
# ---------------------------------------------------------------------

def split_top_level(s, sepchar=','):
    parts, depth, cur = [], 0, ''
    for c in s:
        if c == '(':
            depth += 1; cur += c
        elif c == ')':
            depth -= 1; cur += c
        elif c == sepchar and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += c
    parts.append(cur)
    return parts


def split_field_trailing_paren(field):
    field = field.strip()
    if field.endswith(')'):
        depth = 0
        for k in range(len(field) - 1, -1, -1):
            c = field[k]
            if c == ')':
                depth += 1
            elif c == '(':
                depth -= 1
                if depth == 0:
                    return field[:k].strip(), field[k + 1:-1].strip()
        raise AssemblerError(f"unbalanced parens in field {field!r}")
    return field, None


def parse_statement_text(text, lineno=None):
    text = text.strip()
    i, depth = 0, 0
    while i < len(text):
        c = text[i]
        if depth == 0 and c in '(,':
            break
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
        i += 1
    op = text[:i].strip()
    rest = text[i:]
    mods = []
    while rest.lstrip().startswith('('):
        rest = rest.lstrip()
        depth, j = 0, 0
        for j, c in enumerate(rest):
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    break
        mods.append(rest[1:j])
        rest = rest[j + 1:]
    rest = rest.lstrip()
    fields = []
    if rest.startswith(','):
        fields = [f.strip() for f in split_top_level(rest[1:], ',')]
    elif rest.strip():
        raise AssemblerError(f"unexpected trailing text {rest!r}", lineno)
    return op, mods, fields


class Statement:
    def __init__(self, lineno, name, op, mods, fields, raw):
        self.lineno, self.name, self.op, self.mods, self.fields, self.raw = \
            lineno, name, op, mods, fields, raw
        self.addr = None  # filled in by pass 1: bit-count location


def iter_statements(source):
    for lineno, raw in enumerate(source.splitlines(), 1):
        code = raw.split('!', 1)[0]
        if not code.strip():
            continue
        if code[0] not in ' \t':
            m = re.match(r'^(\S+)\s+(.*)$', code)
            name, statement = (m.group(1), m.group(2)) if m else (code.strip(), '')
        else:
            name, statement = None, code.strip()
        first = True
        for sub in statement.split(';'):
            sub = sub.strip()
            if not sub:
                continue
            op, mods, fields = parse_statement_text(sub, lineno)
            yield Statement(lineno, name if first else None, op, mods, fields, sub)
            first = False


# ---------------------------------------------------------------------
# VFL/FP mnemonic + data-description resolution (C22-6531 "Data
# Description": how the compiler disambiguates a mnemonic that could be
# either a VFL or a floating point op).
# ---------------------------------------------------------------------

def parse_dds(mod_text, lineno=None):
    """Returns (mode:str, length_expr:str|None, bs_expr:str|None)."""
    parts = [p.strip() for p in split_top_level(mod_text, ',')]
    mode = parts[0].strip().upper()
    length = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
    bs = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
    return mode, length, bs


def classify_connective(op):
    """C/CM/CT + exactly 4 binary digits (X22-6533 pocket card
    "CONNECTIVES" table: xxxx00111 = C "Connect" (result -> accumulator),
    xxxx01111 = CM "Connect to Memory" (result -> storage), xxxx10111 =
    CT "Connect for Test" (result discarded, indicators only); xxxx is
    the connective function 0-15, Reference Manual Figure 20). Returns
    (suffix_name, conn:int) or None. Tries CM/CT before C so "CM0101"
    doesn't match the shorter "C" prefix first.
    """
    for name in ('CM', 'CT', 'C'):
        if op.startswith(name) and len(op) == len(name) + 4:
            digits = op[len(name):]
            if all(ch in '01' for ch in digits):
                return name, int(digits, 2)
    return None


def strip_fp_sign(op):
    """An FP op mnemonic may carry a sign-modifier suffix (pocket card
    X22-6533 "L(N,A,NA)" etc.; the FP diagnostic jb_af1c writes them as
    LN/LA/LNA): N = negative sign (invert), A = absolute sign (force
    positive), NA = both. Returns (base, absSign, invSign) if `op` is a
    known FP op with such a suffix, else None. Verified bit-for-bit
    against jb_af1c's printed machine code (verify_fp_signmods.py):
    LA(U)->22007.60 sets absSign, LN(U)->.50 sets invSign, LNA(U)->.70
    both. Tried longest suffix first (NA before N/A) and only when the
    remainder is a real FP op, so LWF/LFT/SLO/SRT etc. are untouched.
    """
    for suf, a, i in (("NA", 1, 1), ("N", 0, 1), ("A", 1, 0)):
        if op.endswith(suf) and op[:-len(suf)] in FP_CODES:
            return (op[:-len(suf)], a, i)
    # The written-minus forms jb_af1c uses for ADD TO MEMORY (F204B,
    # p.55-58): M- is M+ with the negative sign modifier (printed code
    # 22355.50 A0 vs M+'s .40), M-A is M+ with both (.70; M+A is .60).
    # Same pocket-card rule as "-" being "+" with the N modifier.
    # STORE ROOT's negative form puts its N INSIDE the mnemonic: SRT is
    # the plain store, SRTA takes the absolute modifier (and is reached
    # by the suffix loop above, SRT being a real FP op), but the
    # negative one is spelled "Store Negative RooT".  jb_af1c F218B
    # prints SRT .46, SRTA .66, SNRT .56 and SNRTA .76, so SNRT is SRT
    # with the invert-sign modifier and SNRTA with both.  Third family
    # in this file whose modifier letters are not a trailing suffix,
    # after the written-minus forms below and E+AI/E-I/E-AI.
    if op == "SNRT":
        return ("SRT", 0, 1)
    if op == "SNRTA":
        return ("SRT", 1, 1)
    if op == "M-":
        return ("M+", 0, 1)
    if op == "M-A":
        return ("M+", 1, 1)
    # Likewise ADD TO MAGNITUDE's written-minus forms (F205, pp.66-72):
    # -MG is +MG with N (.52 20 beside +MG's .42), -MGA with both (.72;
    # +MGA is .62).
    if op == "-MG":
        return ("+MG", 0, 1)
    if op == "-MGA":
        return ("+MG", 1, 1)
    # And ADD MAGNITUDE TO MEMORY's (F206B, pp.78-84): M-MG is M+MG with
    # N (.52 A0 beside M+MG's .42), M-MGA with both (.72). M+MGA needs no
    # rule -- the generic "A" suffix above strips to M+MG, which is a real
    # FP op; M-MG/M-MGA cannot, since M-MG is not.
    if op == "M-MG":
        return ("M+MG", 0, 1)
    if op == "M-MGA":
        return ("M+MG", 1, 1)
    # And ADD DOUBLE's (F208B, pp.96-97): D- is D+ with N (022054.54 20
    # beside D+'s .44), D-A with both (.74; D+A is .64). D+A needs no
    # rule -- the generic "A" suffix above strips to D+, which is a real
    # FP op. D-/D-A cannot, since "D-" is not.
    if op == "D-":
        return ("D+", 0, 1)
    if op == "D-A":
        return ("D+", 1, 1)
    # And ADD DOUBLE TO MAGNITUDE's (F209B, pp.102-103), the same shape
    # again: D-MG is D+MG with N, D-MGA with both. D+MGA needs no rule,
    # since the generic "A" suffix strips to D+MG, which is a real op.
    if op == "D-MG":
        return ("D+MG", 0, 1)
    if op == "D-MGA":
        return ("D+MG", 1, 1)
    # And ADD TO FRACTION's (F212-XB, jb_af1c p.123), the same shape a
    # sixth time: F- is F+ with N, F-A with both.  The listing prints
    # F+A%U as "22055.65 20" and F-A%U as "22055.75 20" -- the same
    # address and the same code, differing only in the invSign bit.
    # F+A needs no rule, since the generic "A" suffix above strips to
    # F+, which is a real FP op; "F-" is not, so these do.
    if op == "F-":
        return ("F+", 0, 1)
    if op == "F-A":
        return ("F+", 1, 1)
    # And ADD TO EXPONENT's (F213B, jb_af1c pp.128-129), the seventh
    # and last of the family: E- is E+ with N, E-A with both.  The
    # listing prints E-%U as "22020.55 60" beside E+%U's ".45 60" and
    # E-A%U as ".75 60" beside E+A%U's ".65 60" -- the same address and
    # code, differing in the invSign bit alone.  E+A needs no rule,
    # since the generic "A" suffix strips to E+, a real FP op.
    if op == "E-":
        return ("E+", 0, 1)
    if op == "E-A":
        return ("E+", 1, 1)
    # ADD IMMEDIATE TO EXPONENT (F213-XB, jb_af1c pp.135-136) is the
    # one family whose modifier letters sit INSIDE the mnemonic rather
    # than at the end, because the "I" belongs to the operation:
    # E+I, E+AI, E-I, E-AI.  The trailing-suffix loop above cannot
    # reach them -- "E+AI" ends in I -- so all three need their own
    # rule, unlike E+A/F+A/D+A which the generic "A" strips.  The
    # listing prints them ".47", ".67", ".57" and ".77", the same two
    # modifier bits in the same place as every other FP op.
    if op == "E+AI":
        return ("E+I", 1, 0)
    if op == "E-I":
        return ("E+I", 0, 1)
    if op == "E-AI":
        return ("E+I", 1, 1)
    # SHIFT FRACTION's direction mnemonics (F212, jb_af1c pp.115-121).
    # SHF's direction is bit 11 of the effective address, and Reference
    # Manual p.102 adds "the sign of the shift -- bit 11 of the
    # effective address, or shift amount -- is subject to modification
    # by the sign modifiers". So STRAP spells the direction with the
    # sign modifiers and leaves the ADDRESS carrying the amount alone:
    # SHFL is A (absolute -> sign 0 -> left), SHFR is A+N (absolute
    # then inverted -> right). The listing prints SHFL(U),1 as
    # "200.67 20" and SHFR(U),1 as "200.77 20" -- the SAME address 200
    # (= amount 1 << 7, direction bit CLEAR in both), differing only in
    # bits 19-20. Emitting n*128+64 for SHFR would be wrong twice over:
    # the address would not match the listing, and N would invert a
    # set bit back to a LEFT shift.
    # SHFA/SHFN/SHFNA (F212B's modifier-combination tests) need no rule
    # here -- the generic suffix loop above strips them, since the
    # remainder "SHF" is itself a real FP op.
    if op == "SHFL":
        return ("SHF", 1, 0)
    if op == "SHFR":
        return ("SHF", 1, 1)
    return None


def classify_vfl_or_fp(stmt):
    """Returns ('VFL'|'FP'|'CONN'|None, base_op, invert, immediate,
    p_progressive, dds_mods, conn).

    p_progressive is None for standard address modification, else the
    VflAddr.p value 1-7 (C22-6531 "Progressive Indexing": a VFL/
    Connective op may carry a *second* parenthesized operation --
    V+I/V+IC/V+ICR or V-I/V-IC/V-ICR -- alongside its data description,
    format 8 "OP(OP2)(dds), A24(J), OF7(J')"). dds_mods is stmt.mods
    with that secondary-op group removed, if present, so callers
    always find the real (M,L,BS) dds at dds_mods[0].

    The secondary op's parenthesized group can come BEFORE the dds
    (Reference Manual Figure 7's own worked example: "L(V+I)(BU,7,8)")
    or AFTER it (C22-6578 Problem 2.2 Method 2's "K(BU,7)(V+I)") --
    both are real, both from primary sources, so this scans every mod
    for the secondary-op keyword rather than assuming mods[0]. A
    fixed-position check would have silently mis-encoded the
    dds-first ordering as non-progressive (P=0, no error), exactly the
    wrong-output-no-error failure mode this project has caught and
    fixed elsewhere (see README.md "Gotchas" item 7).

    `conn` is `(suffix_name, conn_value)` from classify_connective when
    kind is 'CONN' (Reference Manual p.75: "The connective operations
    use basically the same full-word instruction format as the
    integer arithmetic operations... Immediate addressing is also
    handled the same way" -- so Connectives share this function's
    progressive-op/dds handling rather than getting a separate one),
    else None.
    """
    op = stmt.op
    invert = 0
    immediate = False
    base_op = op
    if op == '-':
        base_op, invert = VFL_INT_MINUS_BASE, 1

    dds_mods = []
    p_progressive = None
    for m in stmt.mods:
        key = m.strip().upper()
        if key in PROGRESSIVE_SECONDARY_OP:
            if p_progressive is not None:
                raise AssemblerError(
                    f"{op} has more than one progressive-indexing secondary op", stmt.lineno)
            p_progressive = PROGRESSIVE_SECONDARY_OP[key]
        else:
            dds_mods.append(m)

    conn = classify_connective(base_op)
    if conn is not None:
        return 'CONN', base_op, invert, immediate, p_progressive, dds_mods, conn

    # The "I"-immediate suffix (Appendix A footnote 4: a VFL op may be
    # suffixed I/N/NI for Immediate/Negative/Negative-Immediate
    # addressing) is tried whether or not an explicit dds is present --
    # C22-6578 Problem 2.2 Method 2's "LI(BU,7), 127" has both. Applied
    # here, before the has_dds branch below, so both orderings share
    # one check instead of the dds-present path silently skipping it
    # (which previously made "LI(BU,7), 127" fail as an unknown op
    # instead of being recognized as L with immediate addressing).
    if base_op not in VFL_INT_CODES and base_op.endswith('I') and base_op[:-1] in VFL_INT_CODES:
        base_op, immediate = base_op[:-1], True

    has_dds = bool(dds_mods) and dds_mods[0].strip() != ''
    if has_dds:
        mode = dds_mods[0].split(',')[0].strip().upper()
        if mode in ('N', 'U'):
            return 'FP', base_op, invert, immediate, p_progressive, dds_mods, None
        if mode in MODE_BITS:
            return 'VFL', base_op, invert, immediate, p_progressive, dds_mods, None
        raise AssemblerError(f"unknown data-description mode {mode!r}", stmt.lineno)

    in_vfl, in_fp = base_op in VFL_INT_CODES, base_op in FP_CODES
    if not in_vfl and not in_fp and strip_fp_sign(base_op) is not None:
        return 'FP', base_op, invert, immediate, p_progressive, dds_mods, None
    if in_vfl and not in_fp:
        return 'VFL', base_op, invert, immediate, p_progressive, dds_mods, None
    if in_fp and not in_vfl:
        return 'FP', base_op, invert, immediate, p_progressive, dds_mods, None
    if in_vfl and in_fp:
        # C22-6531 p.9, case 1: ambiguous op with no dds assembles as
        # VFL with data description (BU, 64, 8).
        return 'VFL', base_op, invert, immediate, p_progressive, dds_mods, None
    return None, base_op, invert, immediate, p_progressive, dds_mods, None


def classify_branch_indicator(op):
    """Try op as B[Z]<indicator>[Z]. Returns (indnum, clear, branchOn) or None."""
    for prefix, branchOn in (('BZ', 0), ('B', 1)):
        if not op.startswith(prefix):
            continue
        rest = op[len(prefix):]
        if not rest:
            continue
        if rest.upper() in INDICATOR_BITS:
            return INDICATOR_BITS[rest.upper()], 0, branchOn
        if rest.endswith('Z') and rest[:-1].upper() in INDICATOR_BITS:
            return INDICATOR_BITS[rest[:-1].upper()], 1, branchOn
    return None


# ---------------------------------------------------------------------
# Pass 1: sizes only (never needs the symbol table -- see module
# docstring's UNITS note for why DD's size doesn't depend on resolving
# any address expression).
# ---------------------------------------------------------------------

HALF, FULL = 32, 64

def dds_length_bits(mods, lineno=None):
    if not mods or not mods[0].strip():
        return 64
    mode, length_expr, _ = parse_dds(mods[0], lineno)
    if length_expr is None:
        return 64
    n = eval_expr(length_expr, {}, 0, lineno=lineno) % 64
    return 64 if n == 0 else n


def is_half_word_branch(op):
    op = op.upper()
    return (op in UNCOND_BRANCH_CODES or op in CB_CODES
            or classify_branch_indicator(op) is not None)


def enc_sic(addr24, idx):
    """SIC's own half-word (Reference Manual p.41 format): bits 0-23
    storage address (bit address), 24-27 literal 1000, 28-31 index."""
    return ((addr24 & 0xFFFFFF) << 8) | (0b1000 << 4) | (idx & 0xF)


def statement_size(stmt):
    """Returns (alignment_bits, size_bits). alignment 0 = no rounding."""
    op = stmt.op.upper()
    if op == 'DD':
        return 0, dds_length_bits(stmt.mods, stmt.lineno) * max(1, len(stmt.fields))
    if op == 'VF':
        return HALF, HALF
    if op == 'XW':
        return FULL, FULL
    if op == 'END':
        return 0, 0
    if op == 'SYN':
        return 0, 0  # defines a symbol by value, occupies no storage (C22-6531 p.31)
    if op == 'SLC':
        return 0, 0  # moves the location counter, occupies no storage (C22-6531 p.32)
    if op == 'CNOP':
        return FULL, 0  # align to a full word; the gap filler emits the NOP
    if op in ('CF', 'RF', 'DDI', 'CW', 'EXT'):
        raise AssemblerError(
            f"pseudo-operation {op} not implemented by this assembler yet "
            f"(see strap_asm.py module docstring / C22-6531)", stmt.lineno)
    # Instruction.
    if op == 'NOP' and not stmt.fields:
        return HALF, HALF  # bare "NOP", see emit_statement
    if op == 'SIC':
        return HALF, HALF  # its embedded branch is the following statement
    if op in UNCOND_BRANCH_CODES or op in MISC_CODES:
        return HALF, HALF
    if op in DIR_INDEX_CODES:
        return HALF, HALF
    if op in IMM_INDEX_CODES:
        return HALF, HALF
    if op in CB_CODES:
        return HALF, HALF
    if classify_branch_indicator(op) is not None:
        return HALF, HALF
    # Full-word INSTRUCTIONS (Branch on Bit, I/O, VFL, Connective) are
    # 64 bits wide but only HALF-word aligned: the instruction counter
    # is half-word granular, and "the full word taken from storage will
    # start at bit 32 of the addressed location and continue to bit 31
    # of the next higher location" (Reference Manual p.39). Real STRAP
    # output confirms it -- the floating-point diagnostic jb_af1c packs
    # a full-word Connective (CT0110...) at octal 011652.40, half-word 1,
    # directly after a half-word FP compare with no gap. So alignment is
    # HALF (they sit wherever the location counter is), size is FULL,
    # and emit_statement deposits them with the bit-precise 64-bit
    # deposit (crossing the word boundary when at an odd half-word),
    # NOT deposit_full, which is reserved for word-aligned DATA (XW).
    if op in BB_CODES:
        return HALF, FULL  # Branch on Bit, full-word instruction (p.41)
    if op in TRANSMIT_CODES:
        # TRANSMIT/SWAP, full-word instruction that may sit at an ODD
        # half-word -- jb_ax5b p.45 places two of them at 021377.40 and
        # 021400.40, each straddling a word boundary (Ref. Manual p.39).
        return HALF, FULL
    if op in IO_BASE_OPS or op in IO_OP:
        return HALF, FULL
    kind, *_ = classify_vfl_or_fp(stmt)
    if kind == 'VFL' or kind == 'CONN':  # both are full-word (p.75 "Format")
        return HALF, FULL
    if kind == 'FP':
        return HALF, HALF
    raise AssemblerError(
        f"unknown mnemonic {stmt.op!r} (not a supported instruction or "
        f"pseudo-op -- see strap_asm.py module docstring)", stmt.lineno)


# ---------------------------------------------------------------------
# Image: a sparse map word_addr -> 64-bit value, with a bit-precise
# deposit primitive for DD (VFL fields are bit-addressable in the
# 7030's own architecture; this Python-side image builder isn't bound
# by the Bluespec model's one-write-per-rule limitation, so DD may
# freely cross a word boundary -- see stretch/strap/README.md).
# ---------------------------------------------------------------------

class Image:
    def __init__(self):
        self.words = {}
        self._written = {}  # word_addr -> bitmask of bits already deposited,
                             # to catch a size-computation/alignment bug
                             # silently corrupting a word via OR instead of
                             # raising -- the same protection fieldCrosses
                             # gives on the hardware side (see StretchVFL.bsv).

    def deposit(self, loc_bits, width_bits, value):
        value &= (1 << width_bits) - 1
        remaining, pos = width_bits, loc_bits
        while remaining > 0:
            word_addr, bit_in_word = divmod(pos, 64)
            take = min(64 - bit_in_word, remaining)
            chunk = (value >> (remaining - take)) & ((1 << take) - 1)
            shift = 64 - bit_in_word - take
            field_mask = ((1 << take) - 1) << shift
            prior = self._written.get(word_addr, 0)
            if prior & field_mask:
                raise AssemblerError(
                    f"internal: two statements deposited overlapping bits "
                    f"in word {word_addr} (bit {pos}, {take} bits) -- likely "
                    f"a size-computation or alignment bug", None)
            self._written[word_addr] = prior | field_mask
            self.words[word_addr] = self.words.get(word_addr, 0) | (chunk << shift)
            remaining -= take
            pos += take

    def deposit_half(self, hword_addr, value):
        self.deposit(hword_addr * 32, 32, value)

    def deposit_full(self, loc_bits, value):
        assert loc_bits % 64 == 0
        self.deposit(loc_bits, 64, value)

    def deposit_word_instr(self, loc_bits, value):
        # A full-word INSTRUCTION (Branch on Bit, I/O, VFL, Connective):
        # 64 bits that are only HALF-word aligned and so may straddle a
        # word boundary -- bits 32-63 of word N, then bits 0-31 of word
        # N+1 (Reference Manual p.39). Unlike deposit_full (word-aligned
        # DATA), the location need only be half-word aligned; the
        # bit-precise deposit() handles the crossing and the overlap
        # check.
        assert loc_bits % 32 == 0
        self.deposit(loc_bits, 64, value)


# ---------------------------------------------------------------------
# Top-level assembler.
# ---------------------------------------------------------------------

# Word addresses 0-31 are the Special Storage Assignment range (word 0
# = permanently-protected Zero, always reads 0 and discards writes;
# 1-15 = CPU registers including the accumulator at 8/9; 16-31 = index
# registers X0-X15 -- see StretchTypes.bsv / StretchStorage.bsv). A
# STRAP program's code and data must not be assembled into that range
# unless it specifically means to address one of those registers by
# its special meaning: placing ordinary code/data at word 0, for
# example, silently reads back as 0 no matter what was "stored" there
# (this is exactly how a real 7030 installation would leave word 0
# alone too). Ordinary storage starts at word 32.
DEFAULT_ORIGIN_BITS = 32 * 64


class AssembledProgram:
    def __init__(self, words, symtab, end_pc):
        self.words = words          # dict word_addr(int) -> value(int)
        self.symtab = symtab        # dict SYMBOL(str) -> bit-count(int)
        self.end_pc = end_pc        # half-word PC (int) from an END statement, or None


def resolve_syns(syn_stmts, symtab, final):
    """Resolve SYN symbols by fixpoint (see assemble() for the rule
    this implements). Returns the list of (NAME, stmt) pairs still
    unresolved. final=True: anything left is an error, classified
    precisely as undefined vs. circular; final=False (an SLC asking
    for whatever is resolvable so far): just return the leftovers."""
    pending = list(syn_stmts)
    while pending:
        progressed = False
        still_pending = []
        for up, stmt in pending:
            if not stmt.fields or not stmt.fields[0].strip():
                raise AssemblerError("SYN needs a value operand", stmt.lineno)
            missing = [s for s in referenced_symbols(stmt.fields[0], stmt.lineno)
                       if s not in symtab]
            if missing:
                still_pending.append((up, stmt))
                continue
            symtab[up] = eval_expr(stmt.fields[0], symtab, stmt.addr, lineno=stmt.lineno)
            progressed = True
        if not progressed:
            if not final:
                return still_pending
            # Classify each stuck symbol precisely rather than lumping
            # every failure under one vague "undefined or circular"
            # message (caught by advisor review -- the original message
            # pointed a plain undefined-symbol typo at a nonexistent
            # cycle). A symbol is "undefined" if ANY path through its
            # still-missing dependencies eventually names something
            # that isn't even a candidate (stuck) SYN -- i.e. a
            # dependency that will never resolve, transitively, not
            # just directly (A -> B -> undefined must blame the
            # undefined leaf, not call A circular just because its
            # *direct* dependency B happens to still be stuck too).
            # What's left after removing every such chain is genuinely
            # circular: every dependency path loops back among stuck
            # symbols forever with no escape.
            still_names = {up for up, stmt in still_pending}
            direct_missing = {
                up: [s for s in referenced_symbols(stmt.fields[0], stmt.lineno) if s not in symtab]
                for up, stmt in still_pending}

            def reaches_undefined(name, seen=frozenset()):
                if name in seen:
                    return False
                for dep in direct_missing.get(name, []):
                    if dep not in still_names or reaches_undefined(dep, seen | {name}):
                        return True
                return False

            by_name = {up: stmt for up, stmt in still_pending}
            undefined = [up for up in still_names if reaches_undefined(up)]
            circular = [up for up in still_names if up not in undefined]
            parts = []
            if undefined:
                parts.append('undefined: ' + ', '.join(
                    f"{up} (needs {by_name[up].fields[0]!r})" for up in undefined))
            if circular:
                parts.append('circular: ' + ', '.join(
                    f"{up} (needs {by_name[up].fields[0]!r})" for up in circular))
            raise AssemblerError(
                f"SYN symbol(s) never resolve -- {'; '.join(parts)}",
                still_pending[0][1].lineno)
        pending = still_pending

    return []


def assemble(source, origin_bits=DEFAULT_ORIGIN_BITS):
    statements = list(iter_statements(source))

    # Pass 1: sizes + symbol table. Rounding a full-word instruction's
    # location up past a half-word instruction that didn't fill a whole
    # word leaves a gap that straight-line execution would otherwise
    # fall through into (fetching whatever happens to be there, which
    # decodes as a real -- and wrong -- instruction: an all-zero
    # half-word is BE, Branch Enabled, to address 0). C22-6531's CNOP
    # pseudo-op describes exactly this padding ("the machine instruction
    # NOP is compiled" to bridge a half-word-to-full-word rounding gap);
    # this assembler applies that same fill automatically wherever
    # alignment forces a gap, rather than requiring an explicit CNOP
    # before every full-word instruction.
    symtab = {}
    gaps = []
    syn_stmts = []  # SYN statements: named but NOT assigned the location
                     # counter (unlike every other pseudo-op/instruction)
                     # -- their value comes from evaluating their own
                     # operand expression instead, which may reference a
                     # symbol not yet defined at this point in the source
                     # (C22-6531 p.31: "this may possibly mean as late as
                     # pass 3 of Strap-1"). Resolved in a separate
                     # fixpoint pass below, once every location-counter
                     # symbol above is already known. This is exactly the
                     # bug this module's docstring describes fixing:
                     # SYN's name must NEVER just take the current `loc`.
    loc = origin_bits
    for n, stmt in enumerate(statements):
        if stmt.op.upper() == 'SIC':
            nxt = statements[n + 1] if n + 1 < len(statements) else None
            if nxt is None or not is_half_word_branch(nxt.op):
                raise AssemblerError(
                    f"SIC must be immediately followed by a half-word branch "
                    f"(B/BR/BE/BD/BEW/NOP, CB..., B<ind>...) -- it is one 64-bit "
                    f"instruction with it (Reference Manual p.41); found "
                    f"{nxt.op if nxt else 'end of program'!r}", stmt.lineno)
        if stmt.op.upper() == 'SLC':
            # C22-6531 p.32: Y must already be evaluable here. Any SYN
            # seen so far whose chain is resolvable now is resolved
            # first (the manual's own ordering rule: SYNs an SLC depends
            # on "should occur before any SLC with an address involving
            # the name of the SYN card"); whatever is still pending
            # after that is a genuine forward reference for THIS SLC.
            syn_stmts[:] = resolve_syns(syn_stmts, symtab, final=False)
            if not stmt.fields or not stmt.fields[0].strip():
                raise AssemblerError("SLC needs a location operand", stmt.lineno)
            missing = [sym for sym in referenced_symbols(stmt.fields[0], stmt.lineno)
                       if sym not in symtab]
            if missing:
                raise AssemblerError(
                    f"SLC operand {stmt.fields[0]!r} references {', '.join(missing)}, "
                    f"not yet defined at this point -- SLC cannot forward-reference "
                    f"(C22-6531 p.32)", stmt.lineno)
            new_loc = eval_expr(stmt.fields[0], symtab, loc, lineno=stmt.lineno)
            if new_loc < 0:
                raise AssemblerError(
                    f"SLC operand {stmt.fields[0]!r} evaluates to {new_loc} bits, "
                    f"negative (C22-6531 p.32: must be positive)", stmt.lineno)
            # p.32: "Any symbol A appearing in the name field is
            # ignored." Ignored here too -- stmt.name is deliberately
            # NOT entered into symtab, so a later reference to it
            # fails loud as undefined rather than silently meaning
            # the new location.
            loc = new_loc
            stmt.addr = loc
            continue
        align, size = statement_size(stmt)
        old_loc = loc
        if align:
            loc = ((loc + align - 1) // align) * align
        # Only a gap immediately before an INSTRUCTION is reachable by
        # straight-line execution and needs NOP-filling; a gap before a
        # data pseudo-op (e.g. VF's "LC stands at bit 25" rounding
        # after a bit-precise DD, C22-6531 p.18) is dead space no
        # program counter ever visits, and is left as-is.
        is_instruction = stmt.op.upper() not in ('DD', 'VF', 'XW', 'END', 'SYN', 'SLC')
        if loc != old_loc and is_instruction:
            gaps.append((old_loc, loc - old_loc))
        stmt.addr = loc
        if stmt.name:
            up = stmt.name.upper()
            if up in symtab:
                raise AssemblerError(f"symbol {stmt.name!r} multiply defined", stmt.lineno)
            if stmt.op.upper() == 'SYN':
                syn_stmts.append((up, stmt))
            else:
                symtab[up] = loc
        loc += size

    # Resolve SYN symbols by fixpoint: each SYN's value is its own
    # operand expression (C22-6531 p.31, "A | SYN(dds), Y" -- "the
    # newly defined symbol A is that whenever A is written in the
    # program, the effect is the same as if Y had been written"), which
    # may itself reference another SYN symbol not yet resolved, or a
    # location-counter symbol already known from the pass above. Retry
    # until a full round makes no progress; whatever's left references a
    # genuinely undefined or circular chain.
    resolve_syns(syn_stmts, symtab, final=True)

    # Pass 2: evaluate + emit.
    image = Image()
    for gap_start, gap_size in gaps:
        if gap_size % HALF != 0:
            raise AssemblerError(
                f"alignment gap at bit {gap_start} is {gap_size} bits, not a "
                f"whole number of half-words -- cannot fill with NOP", None)
        for off in range(0, gap_size, HALF):
            image.deposit_half((gap_start + off) // HALF, enc_branch_or_misc(0, UNCOND_BRANCH_CODES['NOP'], False, 0))

    end_pc = None
    for stmt in statements:
        emit_statement(stmt, symtab, image)
        if stmt.op.upper() == 'END' and stmt.fields and stmt.fields[0].strip():
            target_bits = eval_expr(stmt.fields[0], symtab, stmt.addr, lineno=stmt.lineno)
            if target_bits % 32 != 0:
                raise AssemblerError("END target is not half-word aligned", stmt.lineno)
            end_pc = target_bits // 32

    return AssembledProgram(image.words, symtab, end_pc)


def emit_statement(stmt, symtab, image):
    op = stmt.op.upper()
    loc = stmt.addr

    if op == 'SYN':
        # No storage element -- the symbol's value was already resolved
        # into symtab by assemble()'s fixpoint pass above (SYN's value
        # comes from its operand expression, not the location counter,
        # and evaluating it there rather than here is what lets a SYN
        # symbol be referenced by name -- as any other symbol -- from
        # statements the fixpoint pass hasn't reached yet). A SYN's own
        # (dds) modifier, when given, is defined by C22-6531 to also set
        # the *data description* an instruction implicitly inherits by
        # naming this symbol (mode/length/byte-size) -- this assembler's
        # symtab only ever stores numeric values, not per-symbol dds
        # metadata, for any pseudo-op (DD included), so that part of
        # SYN's own spec is out of scope here, same class of gap as
        # every other implicit-dds-inheritance rule this assembler
        # doesn't model.
        return

    if op == 'SLC':
        return  # location counter already moved in pass 1; no storage

    if op == 'CNOP':
        return  # any NOP it implies was emitted by assemble()'s gap filler

    if op == 'DD':
        length = dds_length_bits(stmt.mods, stmt.lineno)
        pos = loc
        for f in stmt.fields:
            image.deposit(pos, length, parse_dd_literal(f, stmt.lineno))
            pos += length
        return

    if op == 'VF':
        if len(stmt.fields) != 1:
            raise AssemblerError("VF takes exactly one value field", stmt.lineno)
        val = eval_expr(stmt.fields[0], symtab, loc, lineno=stmt.lineno)
        sign = 1 if val < 0 else 0
        mag = abs(val) & 0xFFFFFF
        image.deposit_half(loc // 32, (mag << 8) | (sign << 7))
        return

    if op == 'XW':
        # "XW, VALUE, COUNT, REFILL, FLAG" (C22-6531). VALUE is a
        # sign-magnitude 25-bit field like VF's (raw bit-count units,
        # no shift) -- it holds the index register's bit-address addr
        # field (StretchTypes.bsv IndexWord.addr, Bit#(24), IBM bits
        # 0-23). COUNT is 18-bit unsigned, same units as written. But
        # REFILL (IndexWord.refill, Bit#(18), IBM bits 46-63) is a
        # *word* address -- it feeds st.readWord(refill) directly
        # (StretchExecute.bsv's maybeRefill and BranchOrMisc's R/RCZ),
        # and WordAddr is Bit#(18) full-word units, NOT the bit-count
        # units every other address-like operand in this assembler
        # uses. A label operand here (the common case: self-refill to
        # a control word like CTLWD) evaluates to a bit address like
        # every other symbol, so it must be shifted right 6 bits (same
        # bit-count -> word-address conversion as the A18 field in
        # emit_fp_instruction, see the ">> 6" there) before packing --
        # WITHOUT the shift this silently refills from the wrong word
        # (usually word 0) with no error. Found by advisor review: the
        # only test that exercises XW's refill (figure7_progressive_
        # indexing.strap) never reads a record past the refill point,
        # so this bug produced a passing test before being caught.
        if not stmt.fields or not stmt.fields[0].strip():
            raise AssemblerError("XW needs at least a VALUE field", stmt.lineno)
        val = eval_expr(stmt.fields[0], symtab, loc, lineno=stmt.lineno)
        sign = 1 if val < 0 else 0
        mag = abs(val) & 0xFFFFFF
        count = eval_expr(stmt.fields[1], symtab, loc, lineno=stmt.lineno) & 0x3FFFF \
            if len(stmt.fields) >= 2 and stmt.fields[1].strip() else 0
        # REFILL is an 18-bit WORD-address field: a label's bit count
        # scales >>6, a bare integer counts words (I-Box 4 p.192's
        # "BIT59 XW,0,0,16" prints refill 000000.00 10 = word 16).
        refill = eval_addr_field(stmt.fields[2], symtab, loc, 6, lineno=stmt.lineno) & 0x3FFFF \
            if len(stmt.fields) >= 3 and stmt.fields[2].strip() else 0
        # XW's FOURTH OPERAND IS THREE BITS, IBM 25-27 -- the index
        # flag plus the two spare bits -- not one.  This read `& 0x1`
        # and `<< 38` until 2026-09-23, so ",4" and ",2" both encoded
        # as ZERO and ",1" set the FLAG (IBM 25) instead of the second
        # spare bit (IBM 27).
        #
        # THE ORACLE IS jb_ax5b p.114's OWN BIT TABLE, three adjacent
        # rows that can only be read one way:
        #     BIT25  XW,0,0,0,4  ->  0.00 40   IBM bit 25
        #     BIT26  XW,0,0,0,2  ->  0.00 20   IBM bit 26
        #     BIT27  XW,0,0,0,1  ->  0.00 10   IBM bit 27
        # and p.84's "XW,$+1.07,(8)300000,(8)014000,4" prints its flag
        # bit set, which `& 0x1` turned off.
        #
        # BSV 36-38 is IBM 25-27 (63 - 27 = 36).  Only one program used
        # a non-zero fourth operand before this fix --
        # op_ad_indicators.strap's WOTHER, whose contents are never
        # inspected (it is the operand of an out-of-scope LVE).
        flagbits = eval_expr(stmt.fields[3], symtab, loc, lineno=stmt.lineno) & 0x7 \
            if len(stmt.fields) >= 4 and stmt.fields[3].strip() else 0
        packed = (mag << 40) | (sign << 39) | (flagbits << 36) | (count << 18) | refill
        image.deposit_full(loc, packed)
        return

    if op == 'END':
        return  # end_pc is set by the caller (assemble()), not here.

    # -- Instructions --------------------------------------------------
    if op == 'SIC':
        if len(stmt.fields) != 1:
            raise AssemblerError("SIC takes exactly one address field", stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[0])
        target_bits = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        idx = eval_reg(paren, symtab, stmt.lineno)
        image.deposit_half(loc // 32, enc_sic(target_bits, idx))
        return

    if op in UNCOND_BRANCH_CODES or op in MISC_CODES:
        if op == 'NOP' and not stmt.fields:
            stmt.fields = ['']  # bare "NOP" (docs/ja_ax1a_ibox-1.pdf p.50, 005433.00)
        if len(stmt.fields) != 1:
            raise AssemblerError(f"{op} takes exactly one address field", stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[0])
        # An empty address field ("NOP," -- the form the I-Box listings
        # use for a NOP placeholder, docs/jb_ax4b_ibox-4.pdf p.155/159,
        # printed as 0.30 00, i.e. address 0) compiles as address 0,
        # same as the listing's own explicit "NOP,0." form.
        # 19-bit half-word-address field: bit-address terms >>5, bare
        # integers as half-words (C22-6531 p.11) -- see eval_addr_field.
        addr19 = 0 if not base.strip() else \
            eval_addr_field(base, symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFF
        idx = eval_reg(paren, symtab, stmt.lineno)
        if op in UNCOND_BRANCH_CODES:
            image.deposit_half(loc // 32, enc_branch_or_misc(addr19, UNCOND_BRANCH_CODES[op], False, idx))
        else:
            image.deposit_half(loc // 32, enc_branch_or_misc(addr19, MISC_CODES[op], True, idx))
        return

    if op in DIR_INDEX_CODES:
        if len(stmt.fields) != 2:
            raise AssemblerError(f"{op} takes J and address fields", stmt.lineno)
        j = eval_reg(stmt.fields[0], symtab, stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[1])
        # LX/SX address full words ("bits 0-17 of the effective
        # address", p.24), so a bare integer counts words; every other
        # direct index op addresses a half-word (bits 0-18).
        addr19 = eval_addr_field(base, symtab, loc, 5, lineno=stmt.lineno,
                                 int_shift=1 if op in ('LX', 'SX') else 0) & 0x7FFFF
        idx = eval_reg(paren, symtab, stmt.lineno)
        image.deposit_half(loc // 32, enc_dir_index(addr19, j, DIR_INDEX_CODES[op], idx))
        return

    if op in IMM_INDEX_CODES:
        if len(stmt.fields) != 2:
            raise AssemblerError(f"{op} takes J and immediate fields", stmt.lineno)
        j = eval_reg(stmt.fields[0], symtab, stmt.lineno)
        if op in IMM_INDEX_COUNT_OPS:
            # Count/refill immediates: "bits 0-17 of the address part"
            # (Reference Manual p.25) -- an 18-bit integer in the TOP
            # 18 bits of the 19-bit field. I-Box 1's "LCI,$X1,4" prints
            # as 4.03 02 (docs/ja_ax1a_ibox-1.pdf p.50): 4 in bits 0-17.
            # A LABEL operand is a WORD address, not a bit count.
            # jb_ax5b p.86's "C+I,$X1,160DMP" prints "23301.03 00" --
            # 160DMP's WORD, 023301, sitting in bits 0-17 -- and
            # eval_expr returns its BIT address, which wrapped.
            # eval_addr_field with shift 6 is what XW's refill field
            # already uses for the same reason: "a label's bit count
            # scales >>6, a bare integer counts words", so LCI,$X1,18
            # is unchanged.
            n = eval_addr_field(stmt.fields[1], symtab, loc, 6,
                                lineno=stmt.lineno)
            imm19 = (n & 0x3FFFF) << 1
        else:
            # Value immediates: the field is bits 0-18 of a bit address
            # (p.25: "bits 0-18 of the value field ... bits 19-24 set to
            # zero"), so a bit-address term is scaled >>5 like any other
            # 19-bit address field, while a bare integer is inserted as
            # an integer into the field (C22-6531 p.11), i.e. "LVI,$1,100"
            # yields value 100<<5 = 50.0. The DCP listing's
            # "V-I,$X15,1.0" -> 1.37 0D (1.0 = field 2) is the check.
            imm19 = eval_addr_field(stmt.fields[1], symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFF
        image.deposit_half(loc // 32, enc_imm_index(imm19, j, IMM_INDEX_CODES[op]))
        return

    if op in CB_CODES:
        # Format 5: OP,J,B19(K). Full mnemonic table -- see opcodes.py
        # CB_CODES for the mnemonic grammar and its sourcing.
        if len(stmt.fields) != 2:
            raise AssemblerError(f"{op} takes J and branch-address fields", stmt.lineno)
        j = eval_reg(stmt.fields[0], symtab, stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[1])
        addr19 = eval_addr_field(base, symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFF
        idx = eval_reg(paren, symtab, stmt.lineno) & 0x1
        v, refill, bz = CB_CODES[op]
        image.deposit_half(loc // 32, enc_count_branch(addr19, j, v, refill, bz, idx))
        return

    bi = classify_branch_indicator(op)
    if bi is not None:
        indnum, clear, branchOn = bi
        if len(stmt.fields) != 1:
            raise AssemblerError(f"{op} takes exactly one address field", stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[0])
        addr19 = eval_addr_field(base, symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFF
        idx = eval_reg(paren, symtab, stmt.lineno) & 0x1
        image.deposit_half(loc // 32, enc_branch_ind(addr19, indnum, clear, branchOn, idx))
        return

    if op in TRANSMIT_CODES:
        # TRANSMIT / SWAP, Strap Format "OP, J, A1(I1), A2(I2)"
        # (X22-6533 pocket card, pcard-1's TRANSMIT heading).  A1 is a
        # BIT address, so its base is evaluated to raw bits (>>0, like
        # SIC's and BRANCH ON BIT's B); A2 is a HALF-WORD address
        # (bit-address terms >>5, like BRANCH ON BIT's A).
        if len(stmt.fields) != 3:
            raise AssemblerError(
                f"{op} takes J, A1(I1) and A2(I2) fields "
                "(pocket card: OP, J, A1(I1), A2(I2))", stmt.lineno)
        j = eval_expr(stmt.fields[0], symtab, loc, lineno=stmt.lineno)
        # J is FOUR bits (51-54).  With the immediate-count modifier it
        # IS the count, so a count that does not fit has to be refused
        # rather than truncated -- every numeric field this project has
        # silently truncated has cost a session (see docs/NEXT.md's
        # trap list).
        if not 0 <= j <= 15:
            raise AssemblerError(
                f"{op}'s J field is 4 bits (pocket card, bits 51-54); "
                f"{j} does not fit", stmt.lineno)
        a1base, a1paren = split_field_trailing_paren(stmt.fields[1])
        a2base, a2paren = split_field_trailing_paren(stmt.fields[2])
        bitaddr24 = eval_expr(a1base, symtab, loc, lineno=stmt.lineno) & 0xFFFFFF
        i1 = eval_reg(a1paren, symtab, stmt.lineno) & 0xF
        addr19 = eval_addr_field(a2base, symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFF
        i2 = eval_reg(a2paren, symtab, stmt.lineno) & 0xF
        backward, immCount, swap = TRANSMIT_CODES[op]
        image.deposit_word_instr(loc, enc_transmit(bitaddr24, i1, addr19, j,
                                                   backward, immCount, swap, i2))
        return

    if op in BB_CODES:
        # BRANCH ON BIT, Strap Format "OP,B,(I),A(K)" (X22-6533 pocket
        # card): field 0 is the BIT address B with an optional 4-bit
        # index I; field 1 is the branch address A with the optional
        # X1-only flag K (like CB's K). B is a bit address, so its base
        # is evaluated to raw bits (>>0, same as SIC's address); A is a
        # half-word branch address (bit-address terms >>5).
        if len(stmt.fields) != 2:
            raise AssemblerError(f"{op} takes B (bit address) and A "
                                 "(branch address) fields", stmt.lineno)
        bbase, bparen = split_field_trailing_paren(stmt.fields[0])
        abase, aparen = split_field_trailing_paren(stmt.fields[1])
        bitaddr24 = eval_expr(bbase, symtab, loc, lineno=stmt.lineno) & 0xFFFFFF
        i1 = eval_reg(bparen, symtab, stmt.lineno) & 0xF
        addr19 = eval_addr_field(abase, symtab, loc, 5, lineno=stmt.lineno) & 0x7FFFF
        idx1 = eval_reg(aparen, symtab, stmt.lineno) & 0x1
        mod2, cond1 = BB_CODES[op]
        image.deposit_word_instr(loc, enc_branch_on_bit(bitaddr24, i1, addr19,
                                                  mod2, cond1, idx1))
        return

    if op in IO_BASE_OPS or op in IO_OP:
        # "OP1(OP2), C(I1), A(I2)" (X22-6533 pocket card "INPUT-OUTPUT
        # OPERATIONS"): OP2, if present, must be SEOP; C is the channel
        # address, A is the second effective address -- a control-word
        # address for RD/W/CCW, ignored for REL, but for CTL/LOC a raw
        # code (a control-function code or a unit selection address,
        # p.111: "control information which is decoded by the external
        # unit (CONTROL)... a selection address (LOCATE)") -- NOT a
        # core-storage address at all. See StretchIO.bsv's "CONTROL
        # FUNCTIONS" for what this implementation does with it.
        #
        # UNITS -- C is a plain, UNCONVERTED address field, exactly
        # like any other non-immediate address field in this assembler
        # (see the module docstring's "general... bare integer" note):
        # this codebase does not guess a subfield-aware scaling it
        # hasn't verified, and the channel-address field is a genuinely
        # unusual case -- the Reference Manual (p.111) puts the 7-bit
        # channel number at IBM bits 12-18 of this 24-bit field, NOT at
        # its low-order bits, so a literal channel number N is NOT the
        # right operand value; N<<5 is (confirmed independently by
        # direct bit-position derivation and by advisor review). For
        # RD/W/CCW/REL, A is converted from this assembler's bit-count
        # units to a WORD address the same way XW's REFILL field and
        # the FP A18 field already are (>> 6) -- a repeat of an
        # already-verified pattern. For CTL/LOC, A is a raw code, not
        # an address of anything, so it gets NO conversion at all --
        # the same "bare integer used as-is" treatment as C, and a
        # genuinely different case from RD/W/CCW/REL's A, caught only
        # once CTL had a real behavior (tape CONTROL functions) to
        # test the conversion against.
        seop_mod = bool(stmt.mods) and stmt.mods[0].strip().upper() == 'SEOP'
        lookup = (op + 'SEOP') if (seop_mod and op in IO_BASE_OPS) else op
        if lookup not in IO_OP:
            raise AssemblerError(
                f"unrecognized I-O mnemonic/modifier combination "
                f"{stmt.op!r}{stmt.mods!r}", stmt.lineno)
        if len(stmt.fields) != 2:
            raise AssemblerError(f"{op} takes channel and address fields", stmt.lineno)
        base1, paren1 = split_field_trailing_paren(stmt.fields[0])
        chan_bits = eval_expr(base1, symtab, loc, lineno=stmt.lineno)
        i1 = eval_reg(paren1, symtab, stmt.lineno)
        base2, paren2 = split_field_trailing_paren(stmt.fields[1])
        addr2_bits = eval_expr(base2, symtab, loc, lineno=stmt.lineno) if base2.strip() else 0
        i2 = eval_reg(paren2, symtab, stmt.lineno)
        addr24 = chan_bits & 0xFFFFFF
        is_code_field = lookup in ('CTL', 'CTLSEOP', 'LOC', 'LOCSEOP')
        addr18 = (addr2_bits & 0x3FFFF) if is_code_field else ((addr2_bits >> 6) & 0x3FFFF)
        image.deposit_word_instr(loc, enc_io(addr24, i1, addr18, IO_OP[lookup], i2))
        return

    kind, base_op, invert, immediate, p_progressive, dds_mods, conn = classify_vfl_or_fp(stmt)
    if kind == 'CONN':
        suffix_name, conn_value = conn
        mode, length_expr, bs_expr = ('BU', None, None) if not dds_mods or not dds_mods[0].strip() \
            else parse_dds(dds_mods[0], stmt.lineno)
        if mode not in MODE_BITS:
            raise AssemblerError(f"unknown VFL mode {mode!r}", stmt.lineno)
        length_field = 0 if length_expr is None else eval_expr(length_expr, symtab, 0, lineno=stmt.lineno) & 0x3F
        bs_field = (MODE_DEFAULT_BS[mode] if bs_expr is None
                    else eval_expr(bs_expr, symtab, 0, lineno=stmt.lineno)) & 0x7

        if not stmt.fields or not stmt.fields[0].strip():
            raise AssemblerError(f"{op} needs an address field", stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[0])
        raw_val = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        addr24 = (encode_vfl_immediate(raw_val, length_field, stmt.lineno) if immediate
                  else raw_val & 0xFFFFFF)
        i1 = eval_reg(paren, symtab, stmt.lineno)

        offset, i2 = 0, 0
        if len(stmt.fields) >= 2 and stmt.fields[1].strip():
            base2, paren2 = split_field_trailing_paren(stmt.fields[1])
            offset = eval_expr(base2, symtab, loc, lineno=stmt.lineno) & 0x7F
            i2 = eval_reg(paren2, symtab, stmt.lineno)

        p = p_progressive if p_progressive is not None else (4 if immediate else 0)
        suffix = CONNECTIVE_SUFFIX[suffix_name]
        image.deposit_word_instr(loc, enc_connective(addr24, i1, p, length_field, bs_field,
                                                offset, conn_value, suffix, i2))
        return

    if kind == 'VFL':
        mode, length_expr, bs_expr = ('BU', None, None) if not dds_mods or not dds_mods[0].strip() \
            else parse_dds(dds_mods[0], stmt.lineno)
        if mode not in MODE_BITS:
            raise AssemblerError(f"unknown VFL mode {mode!r}", stmt.lineno)
        unsign, decimal = MODE_BITS[mode]
        length_field = 0 if length_expr is None else eval_expr(length_expr, symtab, 0, lineno=stmt.lineno) & 0x3F
        bs_field = (MODE_DEFAULT_BS[mode] if bs_expr is None
                    else eval_expr(bs_expr, symtab, 0, lineno=stmt.lineno)) & 0x7

        if not stmt.fields or not stmt.fields[0].strip():
            raise AssemblerError(f"{op} needs an address field", stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[0])
        raw_val = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        addr24 = (encode_vfl_immediate(raw_val, length_field, stmt.lineno) if immediate
                  else raw_val & 0xFFFFFF)
        i1 = eval_reg(paren, symtab, stmt.lineno)

        offset, i2 = 0, 0
        if len(stmt.fields) >= 2 and stmt.fields[1].strip():
            base2, paren2 = split_field_trailing_paren(stmt.fields[1])
            offset = eval_expr(base2, symtab, loc, lineno=stmt.lineno) & 0x7F
            i2 = eval_reg(paren2, symtab, stmt.lineno)

        p = p_progressive if p_progressive is not None else (4 if immediate else 0)
        code = VFL_INT_CODES[base_op]
        image.deposit_word_instr(loc, enc_vfl_full(addr24, i1, p, length_field, bs_field,
                                              offset, unsign, invert, decimal, code, i2))
        return

    if kind == 'FP':
        if not stmt.fields or not stmt.fields[0].strip():
            raise AssemblerError(f"{op} needs an address field", stmt.lineno)
        # C22-6531 p.9 case 3: with no explicit dds, a floating-point-
        # only op is normalized unless it's E+/E+I, which default to
        # unnormalized. absSign/invSign are not implemented (always 0)
        # -- see module docstring.
        if stmt.mods and stmt.mods[0].strip():
            fp_mode = stmt.mods[0].split(',')[0].strip().upper()
        else:
            fp_mode = 'U' if base_op in ('E+', 'E+I') else 'N'
        unnorm = 1 if fp_mode == 'U' else 0
        # Sign modifiers (N/A/NA suffix): A -> absSign, N -> invSign.
        fp_base, absSign, invSign = base_op, 0, 0
        sm = strip_fp_sign(base_op)
        if sm is not None:
            fp_base, absSign, invSign = sm
        base, paren = split_field_trailing_paren(stmt.fields[0])
        idx = eval_reg(paren, symtab, stmt.lineno)
        if fp_base == "E+I" and base.strip()[:1] in "+-":
            # ADD IMMEDIATE TO EXPONENT takes its addend as a SIGNED
            # EXPONENT when written with an explicit sign, which is how
            # jb_af1c F213-X spells it ("E+I%U,+2047", "E+I%U,-1791").
            # Reference Manual p.102: "the addend is bits 0-11 of the
            # effective address".  Those twelve bits are an ordinary
            # exponent field -- EF, a ten-bit magnitude, then ES -- and
            # they sit in the 18-bit address field at bits 17, 16-7 and
            # 6.  An out-of-range magnitude keeps its LOW TEN BITS with
            # EF marking the overflow, the same representation
            # fpMakeExp stores and fpExpFull reads back (see
            # StretchFP.bsv); +2047 is therefore EF 1 with a magnitude
            # field of 1023, printed 777600, and -1791 is EF 1 with 767
            # and ES 1, printed 677700.  Verified against all five
            # immediates F213XA prints.
            #
            # Without a sign the field stays an ordinary effective
            # address, which is how fp_exp_shift.strap writes it
            # ("E+I(N), 128.0" for +1); the two forms are told apart by
            # the sign alone, exactly as the listing tells them apart.
            v = eval_expr(base.strip().lstrip("+"), symtab, loc, lineno=stmt.lineno)
            mag = abs(v)
            addr18 = (((1 if mag > 1023 else 0) << 17)
                      | ((mag & 0x3FF) << 7)
                      | ((1 if v < 0 else 0) << 6))
        else:
            target_bits = eval_expr(base, symtab, loc, lineno=stmt.lineno)
            addr18 = (target_bits >> 6) & 0x3FFFF
        image.deposit_half(loc // 32, enc_fp(addr18, unnorm, absSign, invSign, FP_CODES[fp_base], idx))
        return

    raise AssemblerError(f"unhandled mnemonic {stmt.op!r}", stmt.lineno)


_DD_RADIX_LITERAL = re.compile(r'^\((\d+)\)([0-9A-Za-z]+)$')

def parse_dd_literal(field, lineno=None):
    field = field.strip()
    m = _DD_RADIX_LITERAL.match(field)
    if m:
        radix, digits = int(m.group(1)), m.group(2)
        return int(digits, radix)
    try:
        return int(field, 10)
    except ValueError:
        raise AssemblerError(f"cannot parse DD literal {field!r} "
                              f"(only decimal and (radix)digits are supported)", lineno)


# ---------------------------------------------------------------------
# CLI: assemble a file, print the symbol table and the sparse memory
# image (for gen_tb.py, or for eyeballing).
# ---------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} program.strap", file=sys.stderr)
        sys.exit(1)
    with open(sys.argv[1]) as f:
        src = f.read()
    try:
        prog = assemble(src)
    except AssemblerError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    print("Symbols:")
    for name, val in sorted(prog.symtab.items()):
        print(f"  {name:<8} bit {val} = word {val//64}.{val%64}"
              f"  (halfword {val//32})")
    print("Image:")
    for addr in sorted(prog.words):
        print(f"  word[{addr}] = {prog.words[addr]:016x}")
    if prog.end_pc is not None:
        print(f"END target: halfword {prog.end_pc}")
