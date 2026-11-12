"""optable.py -- the operation tables and the system symbol table.

C22-6729 p.192 gives the shape of an entry (mnemonic, skeleton, op index) and
p.144 names the fill routines, but the guide prints no contents.  The contents
come from what the listings have already verified: operation codes from
opcodes.py and the field layouts of strap_asm.py's enc_* functions.  Those are
facts about the 7030 and not about any assembler's structure.

CHOSEN: on the host an entry is built when first looked up, since the VFL,
connective and indicator-branch mnemonics are families.  BOPSER's ordered table
is for the 7030 version, which can dump this one.  CHOSEN: the fill chains
below.  p.144 gives two examples (VFL: S24A, SOFF.  LVS: SJFLD, SBIT) and the
names of the rest; which op takes which is deduced from each format.  S18X,
SVF, SCW, SIM19 and SIMC are not on p.144's list: p.144 says the rule "according
to the function of the address", and these carry the functions that its list
leaves unnamed.
"""
from types import SimpleNamespace

import strap_asm as _a
from opcodes import (SYSTEM_SYMBOLS, MCP_PSEUDO_OPS, MCP_PSEUDO_OPS_1964,
                     INDICATOR_BITS, FP_CODES, VFL_INT_CODES, MODE_BITS,
                     UNCOND_BRANCH_CODES, MISC_CODES, DIR_INDEX_CODES,
                     IMM_INDEX_CODES, IMM_INDEX_COUNT_OPS, CB_CODES,
                     TRANSMIT_CODES, BB_CODES, IO_OP)

HALF, FULL = 32, 64

PSEUDO = {
    # Listing and punch control: wind-up only in Pass 2a (p.34).
    "PUNFUL", "PUNORG", "PUNNOR", "PUNID", "PRNS", "PRND", "NOPRNT", "SPNUS",
    "PRNID", "RESEQ", "NOSEQ", "SEM", "REM", "SKIP", "NOPUN", "PRNOR", "PUNALL",
    "PRNTALL", "TLB", "DUPLI", "PUNSYM", "PUNREL", "PUNFPC", "COMBLOCK", "ENTER",
    "SLCRCOM", "ORIGIN", "PUNCDC", "FEND",      # the last two: 6729 p.183
    # Those with work to do.
    "DD", "DDI", "DR", "DRZ", "SYN", "SLC", "SLCR", "END", "EXT", "CNOP",
    "TAIL", "UNTAIL", "LINK", "IOD", "REEL",
}
MCP_OPS = {"IOD", "REEL"}
# Produce one piece of binary of predetermined length (p.27).
FIXED_DATA = {"XW", "CF", "RF", "VF", "CW", "INDMK"}


class OpEntry:
    def __init__(self, name, **k):
        self.name = name
        self.skeleton = 0       # 64 bits, left-justified
        self.length = 0         # bits of binary
        self.align = 0
        self.fills = []         # (routine, count) as on p.144
        self.kind = None
        self.pseudo = False
        self.mcp = False
        self.dds_needed = False
        self.immediate = False
        self.ambiguous = False
        self.is_conn = False
        self.written_op = name
        self.fp_default_u = False
        self.__dict__.update(k)
        self.index = len(ENTRIES)
        ENTRIES.append(self)


ENTRIES = []                    # ZIOPX is an index in here
_cache = {}


def _half(v):
    return v << 32


def _pseudo(name):
    return OpEntry(name, pseudo=True, kind="pseudo", mcp=name in MCP_OPS)


def _fixed(name, secondary=()):
    if name == "XW":
        return OpEntry(name, length=FULL, align=FULL, kind="data",
                       fills=[("S24SNI", 1), ("S18CF", 1), ("S18RF", 1), ("SFLGS", 1)])
    if name == "CW":
        # C28-6129 printed p.14: the eight secondaries set bits 25-27.
        sec = secondary[0] if secondary else "CR"
        if sec not in _a.CW_SECONDARY:
            return None
        chain, multiple, skip = _a.CW_SECONDARY[sec]
        return OpEntry(name, length=FULL, align=FULL, kind="data",
                       skeleton=(chain << 38) | (multiple << 37) | (skip << 36),
                       fills=[("SCW", 1), ("S18CF", 1), ("S18RF", 1)])
    if name == "VF":
        return OpEntry(name, length=25, align=HALF, kind="data", fills=[("SVF", 1)])
    if name in ("CF", "RF"):
        return OpEntry(name, length=HALF, align=HALF, kind="data", fills=[("S18W", 1)])
    if name == "INDMK":
        return OpEntry(name, length=FULL, align=FULL, kind="data", fills=[("SINDMK", 64)])
    raise KeyError(name)


def lookup(op, mode=None, secondary=()):
    """BOPSER and MIBA together: the entry for op, or None if illegal."""
    key = (op, mode, tuple(secondary))
    if key not in _cache:
        _cache[key] = _build(op, mode, list(secondary))
    return _cache[key]


def _build(op, mode, secondary):
    if op in PSEUDO:
        return _pseudo(op)
    if op in FIXED_DATA:
        return _fixed(op, secondary)
    if op == "":
        return OpEntry("", length=HALF, align=HALF, kind="instr",
                       skeleton=_half(_a.enc_sic(0, 0)), fills=[("S24A", 1)])
    if op == "SIC":
        return OpEntry(op, length=HALF, align=HALF, kind="instr",
                       skeleton=_half(_a.enc_sic(0, 0)), fills=[("SSIC24", 1)])
    if op in UNCOND_BRANCH_CODES:
        return OpEntry(op, length=HALF, align=HALF, kind="instr", fills=[("S19IA", 1)],
                       skeleton=_half(_a.enc_branch_or_misc(0, UNCOND_BRANCH_CODES[op], False, 0)))
    if op in MISC_CODES:
        return OpEntry(op, length=HALF, align=HALF, kind="instr", fills=[("S19IA", 1)],
                       skeleton=_half(_a.enc_branch_or_misc(0, MISC_CODES[op], True, 0)))
    if op in DIR_INDEX_CODES:
        addr = "S18X" if op in ("LX", "SX") else "S19IA"
        return OpEntry(op, length=HALF, align=HALF, kind="instr",
                       fills=[("SJFLD", 1), (addr, 1)],
                       skeleton=_half(_a.enc_dir_index(0, 0, DIR_INDEX_CODES[op], 0)))
    if op == "LVS":
        return OpEntry(op, length=HALF, align=HALF, kind="instr",
                       fills=[("SJFLD", 1), ("SBIT", 16)],
                       skeleton=_half(_a.enc_imm_index(0, 0, IMM_INDEX_CODES["LVS"])))
    if op in IMM_INDEX_CODES:
        addr = "SIMC" if op in IMM_INDEX_COUNT_OPS else "SIM19"
        return OpEntry(op, length=HALF, align=HALF, kind="instr",
                       fills=[("SJFLD", 1), (addr, 1)],
                       skeleton=_half(_a.enc_imm_index(0, 0, IMM_INDEX_CODES[op])))
    if op in CB_CODES:
        v, refill, bz = CB_CODES[op]
        return OpEntry(op, length=HALF, align=HALF, kind="instr",
                       fills=[("SJFLD", 1), ("S19KF", 1)],
                       skeleton=_half(_a.enc_count_branch(0, 0, v, refill, bz, 0)))
    bi = _a.classify_branch_indicator(op)
    if bi is not None:
        n, clear, on = bi
        return OpEntry(op, length=HALF, align=HALF, kind="instr", fills=[("S19KF", 1)],
                       skeleton=_half(_a.enc_branch_ind(0, n, clear, on, 0)))
    if op in TRANSMIT_CODES:
        back, imm, swap = TRANSMIT_CODES[op]
        return OpEntry(op, length=FULL, align=HALF, kind="instr",
                       fills=[("STJFLD", 1), ("STTI", 1), ("STT19A", 1)],
                       skeleton=_a.enc_transmit(0, 0, 0, 0, back, imm, swap, 0))
    if op in BB_CODES:
        mod2, cond1 = BB_CODES[op]
        return OpEntry(op, length=FULL, align=HALF, kind="instr",
                       fills=[("S24A", 1), ("S19BBK", 1)],
                       skeleton=_a.enc_branch_on_bit(0, 0, 0, mod2, cond1, 0))
    io = _io(op, secondary)
    if io is not None:
        return io
    return _vfl_or_fp(op, mode, secondary)


def _io(op, secondary):
    seop = "SEOP" in secondary
    fixed = None
    written = op
    if op in _a.IO_FUNCTION_OPS:
        fixed = _a.IO_FUNCTION_OPS[op]
        op = "CTL"
    elif op not in _a.IO_BASE_OPS and op not in IO_OP:
        return None
    look = (op + "SEOP") if (seop and op in _a.IO_BASE_OPS) else op
    if look not in IO_OP:
        return None
    return OpEntry(written, length=FULL, align=HALF, kind="io", fills=[("SCHAN", 1), ("SIOA", 1)],
                   skeleton=_a.enc_io(0, 0, 0, IO_OP[look], 0), fixed_code=fixed,
                   code_field=look in ("CTL", "CTLSEOP", "LOC", "LOCSEOP"),
                   rel=(op == "REL"))


def _vfl_or_fp(op, mode, secondary):
    mods = ([mode] if mode else []) + [s for s in secondary if s != "SEOP"]
    st = SimpleNamespace(op=op, mods=mods, lineno=None)
    try:
        kind, base, invert, immediate, p, _dds, conn = _a.classify_vfl_or_fp(st)
    except _a.AssemblerError:
        return None
    if kind in ("VFL", "CONN"):
        progressive = p
        pfield = p if p is not None else (4 if immediate else 0)
        fills = [("SIMAD" if immediate else "S24A", 1), ("SOFF", 1)]
        ambiguous = (kind == "VFL" and not mode and not secondary and not immediate
                     and base in VFL_INT_CODES and base in FP_CODES)
        if kind == "CONN":
            suffix_name, value = conn
            sk = _a.enc_connective(0, 0, pfield, 0, 0, 0, value,
                                   _a.CONNECTIVE_SUFFIX[suffix_name], 0)
            return OpEntry(op, length=FULL, align=HALF, kind="conn", fills=fills, skeleton=sk,
                           dds_needed=True, immediate=immediate, is_conn=True,
                           progressive=progressive)
        unsign, decimal = MODE_BITS[mode if mode in MODE_BITS else "BU"]
        sk = _a.enc_vfl_full(0, 0, pfield, 0, 0, 0, unsign, invert, decimal,
                             VFL_INT_CODES[base], 0)
        return OpEntry(op, length=FULL, align=HALF, kind="vfl", fills=fills, skeleton=sk,
                       dds_needed=True, immediate=immediate, ambiguous=ambiguous,
                       explicit_mode=mode, progressive=progressive)
    if kind == "FP":
        fp_base, abss, inv = base, 0, 0
        sm = _a.strip_fp_sign(base)
        if sm is not None:
            fp_base, abss, inv = sm
        if fp_base not in FP_CODES:
            return None
        family = (sm or (base,))[0]
        if mode:
            u = 1 if mode == "U" else 0
        else:
            # p.140: floating only is normalized, except E and E+I (U, p.205).
            u = 1 if family in ("E+", "E+I") else 0
        fill = "SXP10" if fp_base in ("E+I", "SHF") else "S18A"
        return OpEntry(op, length=HALF, align=HALF, kind="fp", fills=[(fill, 1)],
                       skeleton=_half(_a.enc_fp(0, u, abss, inv, FP_CODES[fp_base], 0)))
    return None


# ---------------------------------------------------------------------------
# The system symbol table, Fig. 25 p.193: location, then 13 bits of dds.
# ---------------------------------------------------------------------------
MODE_CODE = {"BU": 0b101, "B": 0b111, "DU": 0b100, "D": 0b110, "N": 0b011, "U": 0b001}
MODE_NAME = {v: k for k, v in MODE_CODE.items()}
DEFAULT_BS = {"B": 1, "BU": 8, "D": 4, "DU": 4, "N": 4, "U": 4}


def dds13(mode, fl, bs):
    """Mode 3, F.L. 6 with 0 for 64, B.S. 4 with 8 as 1000 (Fig. 29 p.201)."""
    return (MODE_CODE[mode] << 10) | ((fl & 63) << 4) | (bs & 15)


def dds_parts(d):
    return MODE_NAME.get(d >> 10, "BU"), (d >> 4) & 63, d & 15


def system_symbol(name):
    """CPLTSY's look-up: (24-bit value, 13-bit dds) or None.

    Index registers come out (BU,64,8), as Fig. 29 prints for $X2.  Indicators
    are (BU,1,8), from C28-6129 printed pp.10-11, verified by the listing rows
    cited in strap_asm.system_symbol_dds.  CHOSEN: the other registers are given
    (BU,64,8) for now.  C28's rule gives them each register's own length, which
    no listing row has been read to check.
    """
    bu = dds13("BU", 0, 8)
    n = None
    if name.startswith("X") and name[1:].isdigit():
        n = int(name[1:])
    elif name.isdigit():
        n = int(name)
    if n is not None and 0 <= n <= 15:
        return (16 + n) * 64, bu
    if name in INDICATOR_BITS:
        return 11 * 64 + INDICATOR_BITS[name], dds13("BU", 1, 8)
    for table in (SYSTEM_SYMBOLS, MCP_PSEUDO_OPS, MCP_PSEUDO_OPS_1964):
        if name in table:
            w, b = table[name]
            return w * 64 + b, bu
    return None
