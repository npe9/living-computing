#!/usr/bin/env python3
"""strap_asm.py -- a STRAP-1 assembler for the IBM 7030 "Stretch",
targeting the encodings established in stretch/bsv/StretchDecode.bsv /
StretchExecute.bsv (see opcodes.py for the shared table and citations).

SCOPE (implemented / not, and why -- mirrors the "decode completely,
execute partially, document the rest" ethos of the Bluespec model):

  Pseudo-ops:  DD, VF, XW, END.
  Not yet:     SYN, CF, RF, CNOP, SLC, DDI, CW, EXT (raise
               AssemblerError citing C22-6531 rather than silently
               guessing). SYN needs a forward-reference-aware pass 1
               (its value can depend on symbols defined later, per
               C22-6531's own note on SYN ordering restrictions) that
               hasn't been written; earlier code here that treated SYN
               like a no-storage pseudo-op WITHOUT evaluating its
               operand and silently gave the name the current location
               counter instead -- wrong output with no error. That was
               caught during review and fixed by refusing to assemble
               SYN at all until it's implemented correctly, since no
               program run through this assembler has needed it yet.

  Instruction formats:
    1  Floating point            -- minimal: encodes the N/U mode bit
                                     (`unnorm`) but not absSign/invSign
                                     modifiers, no (dds) support beyond
                                     that; not exercised by any program
                                     this assembler has been run
                                     against yet.
    2  Misc / unconditional branch / SIC -- branch mnemonics only
       (B BR BE BD BEW NOP); R/RCZ/Z decode but are low-confidence
       (register-operand field placement not confirmed against a
       worked example).
    3  Direct index arithmetic    -- full.
    4  Immediate index arithmetic -- full (LVS excluded, see opcodes.py).
    5  Count and branch           -- minimal: only the plain "CB"
       mnemonic (v=0/refill=0/branch-if-nonzero, matching
       StretchTb.bsv's own usage), no mnemonic table for the v/refill/
       branch-on-zero modifier combinations (see bsv/README.md's
       existing caveat on that modifier table, inherited here
       unchanged) -- not exercised by any program this assembler has
       been run against yet.
    6  Branch on indicator        -- full (B[Z]<indicator>[Z] grammar,
       C22-6531 Appendix A footnote 2).
    7  VFL arithmetic             -- full (binary modes B/BU only;
       decimal D/DU encode but StretchExecute.bsv flags them OP
       invalid, matching the Bluespec model's own documented scope).
    8  Progressive indexing        -- encoded in full: "OP(OP2)(dds),
       A24(J), OF7(J')" where OP2 in {V+I,V+IC,V+ICR,V-I,V-IC,V-ICR}
       sets the VflAddr.p field (1-3/5-7); shares the format-7 encoder,
       since it's the same instruction word shape with a different P
       value. NOT full end-to-end: J' (i2) is parsed and packed into
       the instruction word, but StretchExecute.bsv's VflInt case never
       reads vi.a.i2 -- the manual's "J' may be used to modify bits
       35-50 of the instruction" (p.21) is unimplemented on the model
       side, same as most of format 7's other unexecuted corners.
    9-12 (transmit/swap, bit branch, I-O, LVS) -- not implemented;
       these are exactly the formats StretchExecute.bsv doesn't
       execute either, so there is nothing to verify by encoding them
       yet.

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
  - An ImmIndex `imm` field (LVI et al.) sets an index register's
    24-bit VALUE field, which VF/V+/etc. all treat as a raw bit-count
    (see StretchExecute.bsv's V+ case: it adds a VF word's value
    directly into an index word's `addr` field). Encode with NO shift:
    bit_count & 0x7FFFF.
Getting this backwards was caught by cross-checking against the
worked example in C22-6531 ("SEVN VF, 0.07" added via V+ to advance a
bit-precise scan position) before any code was written against it --
see stretch/strap/README.md.
"""

import re
import sys

from opcodes import (
    VFL_INT_CODES, VFL_INT_MINUS_BASE, FP_CODES, DIR_INDEX_CODES,
    IMM_INDEX_CODES, UNCOND_BRANCH_CODES, MISC_CODES, INDICATOR_BITS,
    MODE_BITS, MODE_DEFAULT_BS, PROGRESSIVE_SECONDARY_OP,
)


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


# ---------------------------------------------------------------------
# Encoders -- one per DecodedInstr shape, field order copied verbatim
# from StretchTb.bsv's enc* functions / StretchTypes.bsv structs.
# ---------------------------------------------------------------------

def enc_vfl_full(addr24, i1, p, length, bs, offset, a, b, c, code, i2=0):
    v, w = cat((addr24, 24), (0b1000, 4), (i1, 4), (p, 3), (length, 6),
               (bs, 3), (offset, 7), (a, 1), (b, 1), (c, 1), (code, 6), (i2, 4))
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
        if c.isdigit():
            m = _TERM_NUM.match(s, i)
            j = m.end()
            if j < n and s[j] == '.':
                m2 = _TERM_NUM.match(s, j + 1)
                b = int(m2.group(0)) if m2 else 0
                tokens.append((sign, 'bitaddr', (int(m.group(0)), b)))
                i = m2.end() if m2 else j + 1
            else:
                tokens.append((sign, 'int', int(m.group(0))))
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


def eval_reg(expr, symtab, lineno=None):
    """4-bit (or 1-bit, for K fields) register-number field."""
    if expr is None:
        return 0
    return eval_expr(expr, symtab, 0, reg_context=True, lineno=lineno) & 0xF


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


def classify_vfl_or_fp(stmt):
    """Returns ('VFL'|'FP'|None, base_op, invert, immediate, p_progressive, dds_mods).

    p_progressive is None for standard address modification, else the
    VflAddr.p value 1-7 (C22-6531 "Progressive Indexing": a VFL/
    Connective op may carry a *second* parenthesized operation --
    V+I/V+IC/V+ICR or V-I/V-IC/V-ICR -- ahead of its data description,
    format 8 "OP(OP2)(dds), A24(J), OF7(J')"). dds_mods is stmt.mods
    with that leading secondary-op group stripped off, if present, so
    callers always find the real (M,L,BS) dds at dds_mods[0].
    """
    op = stmt.op
    invert = 0
    immediate = False
    base_op = op
    if op == '-':
        base_op, invert = VFL_INT_MINUS_BASE, 1

    dds_mods = stmt.mods
    p_progressive = None
    if dds_mods and dds_mods[0].strip().upper() in PROGRESSIVE_SECONDARY_OP:
        p_progressive = PROGRESSIVE_SECONDARY_OP[dds_mods[0].strip().upper()]
        dds_mods = dds_mods[1:]

    has_dds = bool(dds_mods) and dds_mods[0].strip() != ''
    if has_dds:
        mode = dds_mods[0].split(',')[0].strip().upper()
        if mode in ('N', 'U'):
            return 'FP', base_op, invert, immediate, p_progressive, dds_mods
        if mode in MODE_BITS:
            return 'VFL', base_op, invert, immediate, p_progressive, dds_mods
        raise AssemblerError(f"unknown data-description mode {mode!r}", stmt.lineno)

    # No explicit dds: try the "I"-immediate suffix (Appendix A footnote 3)
    # before falling back to the ambiguous-op default.
    if base_op not in VFL_INT_CODES and base_op.endswith('I') and base_op[:-1] in VFL_INT_CODES:
        base_op, immediate = base_op[:-1], True

    in_vfl, in_fp = base_op in VFL_INT_CODES, base_op in FP_CODES
    if in_vfl and not in_fp:
        return 'VFL', base_op, invert, immediate, p_progressive, dds_mods
    if in_fp and not in_vfl:
        return 'FP', base_op, invert, immediate, p_progressive, dds_mods
    if in_vfl and in_fp:
        # C22-6531 p.9, case 1: ambiguous op with no dds assembles as
        # VFL with data description (BU, 64, 8).
        return 'VFL', base_op, invert, immediate, p_progressive, dds_mods
    return None, base_op, invert, immediate, p_progressive, dds_mods


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
    if op in ('SYN', 'CNOP', 'SLC', 'CF', 'RF', 'DDI', 'CW', 'EXT'):
        raise AssemblerError(
            f"pseudo-operation {op} not implemented by this assembler yet "
            f"(see strap_asm.py module docstring / C22-6531)", stmt.lineno)
    # Instruction.
    if op in UNCOND_BRANCH_CODES or op in MISC_CODES:
        return HALF, HALF
    if op in DIR_INDEX_CODES:
        return HALF, HALF
    if op in IMM_INDEX_CODES:
        return HALF, HALF
    if op == 'CB':
        return HALF, HALF
    if classify_branch_indicator(op) is not None:
        return HALF, HALF
    kind, *_ = classify_vfl_or_fp(stmt)
    if kind == 'VFL':
        return FULL, FULL
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
    loc = origin_bits
    for stmt in statements:
        align, size = statement_size(stmt)
        old_loc = loc
        if align:
            loc = ((loc + align - 1) // align) * align
        # Only a gap immediately before an INSTRUCTION is reachable by
        # straight-line execution and needs NOP-filling; a gap before a
        # data pseudo-op (e.g. VF's "LC stands at bit 25" rounding
        # after a bit-precise DD, C22-6531 p.18) is dead space no
        # program counter ever visits, and is left as-is.
        is_instruction = stmt.op.upper() not in ('DD', 'VF', 'XW', 'END')
        if loc != old_loc and is_instruction:
            gaps.append((old_loc, loc - old_loc))
        stmt.addr = loc
        if stmt.name:
            up = stmt.name.upper()
            if up in symtab:
                raise AssemblerError(f"symbol {stmt.name!r} multiply defined", stmt.lineno)
            symtab[up] = loc
        loc += size

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
        refill = (eval_expr(stmt.fields[2], symtab, loc, lineno=stmt.lineno) >> 6) & 0x3FFFF \
            if len(stmt.fields) >= 3 and stmt.fields[2].strip() else 0
        flagbit = eval_expr(stmt.fields[3], symtab, loc, lineno=stmt.lineno) & 0x1 \
            if len(stmt.fields) >= 4 and stmt.fields[3].strip() else 0
        packed = (mag << 40) | (sign << 39) | (flagbit << 38) | (count << 18) | refill
        image.deposit_full(loc, packed)
        return

    if op == 'END':
        return  # end_pc is set by the caller (assemble()), not here.

    # -- Instructions --------------------------------------------------
    if op in UNCOND_BRANCH_CODES or op in MISC_CODES:
        if len(stmt.fields) != 1:
            raise AssemblerError(f"{op} takes exactly one address field", stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[0])
        target_bits = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        addr19 = (target_bits >> 5) & 0x7FFFF
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
        target_bits = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        addr19 = (target_bits >> 5) & 0x7FFFF
        idx = eval_reg(paren, symtab, stmt.lineno)
        image.deposit_half(loc // 32, enc_dir_index(addr19, j, DIR_INDEX_CODES[op], idx))
        return

    if op in IMM_INDEX_CODES:
        if len(stmt.fields) != 2:
            raise AssemblerError(f"{op} takes J and immediate fields", stmt.lineno)
        j = eval_reg(stmt.fields[0], symtab, stmt.lineno)
        imm_bits = eval_expr(stmt.fields[1], symtab, loc, lineno=stmt.lineno)
        imm19 = imm_bits & 0x7FFFF  # NOT shifted -- see module docstring UNITS.
        image.deposit_half(loc // 32, enc_imm_index(imm19, j, IMM_INDEX_CODES[op]))
        return

    if op == 'CB':
        # Format 5: OP,J,B19(K). Minimal encoding only -- v (value
        # increment) always 00/unchanged, refill always 0, branch on
        # count-nonzero -- matching StretchTb.bsv's own hand-assembled
        # usage of this format. No mnemonic table for the v/refill/
        # branch-on-zero modifier combinations yet; see module
        # docstring.
        if len(stmt.fields) != 2:
            raise AssemblerError("CB takes J and branch-address fields", stmt.lineno)
        j = eval_reg(stmt.fields[0], symtab, stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[1])
        target_bits = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        addr19 = (target_bits >> 5) & 0x7FFFF
        idx = eval_reg(paren, symtab, stmt.lineno) & 0x1
        image.deposit_half(loc // 32, enc_count_branch(addr19, j, 0, 0, 0, idx))
        return

    bi = classify_branch_indicator(op)
    if bi is not None:
        indnum, clear, branchOn = bi
        if len(stmt.fields) != 1:
            raise AssemblerError(f"{op} takes exactly one address field", stmt.lineno)
        base, paren = split_field_trailing_paren(stmt.fields[0])
        target_bits = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        addr19 = (target_bits >> 5) & 0x7FFFF
        idx = eval_reg(paren, symtab, stmt.lineno) & 0x1
        image.deposit_half(loc // 32, enc_branch_ind(addr19, indnum, clear, branchOn, idx))
        return

    kind, base_op, invert, immediate, p_progressive, dds_mods = classify_vfl_or_fp(stmt)
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
        addr24 = eval_expr(base, symtab, loc, lineno=stmt.lineno) & 0xFFFFFF
        i1 = eval_reg(paren, symtab, stmt.lineno)

        offset, i2 = 0, 0
        if len(stmt.fields) >= 2 and stmt.fields[1].strip():
            base2, paren2 = split_field_trailing_paren(stmt.fields[1])
            offset = eval_expr(base2, symtab, loc, lineno=stmt.lineno) & 0x7F
            i2 = eval_reg(paren2, symtab, stmt.lineno)

        p = p_progressive if p_progressive is not None else (4 if immediate else 0)
        code = VFL_INT_CODES[base_op]
        image.deposit_full(loc, enc_vfl_full(addr24, i1, p, length_field, bs_field,
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
        base, paren = split_field_trailing_paren(stmt.fields[0])
        target_bits = eval_expr(base, symtab, loc, lineno=stmt.lineno)
        addr18 = (target_bits >> 6) & 0x3FFFF
        idx = eval_reg(paren, symtab, stmt.lineno)
        image.deposit_half(loc // 32, enc_fp(addr18, unnorm, 0, 0, FP_CODES[base_op], idx))
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
