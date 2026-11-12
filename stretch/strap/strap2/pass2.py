"""pass2.py -- UITER, NPS2, DECODE, INSERT and OUTPUT's binary, C22-6729 pp.28-36,
135-172.  The phases run as p.28 draws them:

    UITER -> Pass 2a -> UITER -> Pass 2b

Pass 2a assigns location counters and tries to assemble.  Pass 2b finishes the
values and writes the binary.  Python's recursion stands in for UITER's Utab,
whose mechanics the guide does not give (pass2.md section 3).

CHOSEN, the guide's gap 2: Pass 2b starts its counter where 2a did and runs it
again, using the length each unit now has, so box 27's check has something to
check.  On a disagreement 2a's setting wins and message 6 is given (p.36).
"""
import strap_asm as _a
from . import optable
from .optable import ENTRIES, lookup, dds13, dds_parts, DEFAULT_BS, MODE_NAME
from .symtab import KIND_LABEL, KIND_SYN, KIND_UNDEF, KIND_SPECIAL, FUNCTION
from .unit import *             # noqa: F401,F403
from .value import V, F_UNDEF, F_QUEST, F_MULTI, F_PSEUDO, F_CONTAG
from .dnum import final, load_entry, DnumError
from .punch import Punch, PunchError

ABS_START = 0o41 * 64           # p.33: 41 octal, or 0 in PUNREL mode


class Unresolved(Exception):
    pass


def _fit(v, width):
    return v & ((1 << width) - 1)


def put(word, pos, width, value):
    """Field at bits pos..pos+width-1 of the 64-bit ZIOTPT."""
    shift = 64 - pos - width
    return (word & ~(((1 << width) - 1) << shift)) | (_fit(value, width) << shift)


def _orbits(word, pos, width, value):
    shift = 64 - pos - width
    return word | (_fit(value, width) << shift)


# Which reading of the multiply-defined flags to follow.  C28-6129 (1963) pp.20-21:
# MULTI on the line before the second definition, and MULTI before a statement
# referring to the symbol (its example (5)).  N28-1081 page 7 (April 1963): MULTI
# before both definitions, CONTAG before an instruction referring to it.
EDITIONS = ("N28-1081", "C28-6129")


class Pass2:
    def __init__(self, p1, origin_bits=None, edition="N28-1081"):
        if edition not in EDITIONS:
            raise ValueError(f"edition {edition!r}: one of {EDITIONS}")
        self.edition = edition
        self.p1 = p1
        self.units = p1.units
        self.mem = p1.units.mem
        self.st = p1.st
        self.val = p1.val
        self.msg = p1.msg
        self.origin = ABS_START if origin_bits is None else origin_bits
        self.np2ind = False
        self.image = _a.Image()
        self.end_pc = None
        self.hilo = []
        self.undef_at = None
        self.printed = {}       # what OUTPUT prints for a unit, listing.py
        self.punch = Punch(edition)     # OUTPUT's binary cards, punch.py
        self._full_image = None         # PUNFUL's bits: punched, not loaded
        self.rel = False        # PUNREL mode (p.33), set by _punrel_scan
        self.region = None      # SLCRCOM's common: None the program, 0 blank, k named
        self.unit_region = {}   # unit -> its region, from Pass 2a
        self.slcrcom_reg = {}   # SLCRCOM unit -> the region it sets
        self.comblocks = {}     # COMBLOCK unit -> its common number
        self.common_images = {} # region -> what is assembled in that common
        self.common_of = {}     # COMBLOCK name's f -> its common number
        self.reloc = {}         # unit -> [(bit in its binary, "L" or "R")]
        self.spnus = False      # NSPRES, p.35: SPNUS seen
        self.val.multi_ref = F_CONTAG if edition == "N28-1081" else F_MULTI

    # ---------------------------------------------------------------------------
    def run(self):
        self._punrel_scan()
        self.uiter(first=True)
        self.pass_a()
        self.punch.ncommon = len(self.comblocks)
        if any(n == 37 for n, *_ in self.msg.items):
            self.punch.unwritten = ("a byte size over 8 (message 37): its truncation "
                                    "is not printed (C22-6729 p.137 box 29)")
        self.uiter(first=False)
        self.pass_b()
        self.lists = self.nundsy()      # OUTPUT's end, p.157
        return self

    def _punrel_scan(self):
        """PUNREL mode from the start (p.33: the location counter starts at 41
        octal, "or 0 in PUNREL mode").  CHOSEN: the mode holds when PUNREL comes
        before any statement that takes a location; a PUNREL after one is the
        mixed absolute and relocatable deck C28-6129 allows (N28-1081 page 2)
        and this does not write: _punch_unit refuses it."""
        for unit in self.units.intin():
            e = self._entry(unit)
            if e.name == "PUNREL":
                self.rel = True
                break
            if not e.pseudo or e.name in ("DD", "DDI", "DR", "DRZ", "SLC", "SLCR",
                                          "CNOP", "END", "TLB", "EXT"):
                break
        if self.rel:
            if self.origin == ABS_START:
                self.origin = 0
            self.val.count_lc = True

    # -- UITER, chart GB p.136 ----------------------------------------------------
    def uiter(self, first):
        st = self.st
        self.val.vcundf = True      # pp.32-33
        self.val.have_counters = False
        if not first:
            # Uhl and undefined symbols: special symbols first, since the bounds
            # stand on them; then every undefined symbol at the next full word
            # above the upper limit, in the order encountered (p.205, C28 p.20).
            top = self.origin
            for absc, symc in self.hilo:
                at = self.val.counter_value(absc, symc)
                if at is not None:
                    top = max(top, at)
            self.upper = (top + 63) // 64 * 64
            at = self.upper
            for name, f in list(st.dictionary.items()):
                if st.get(f, "ZKIND") == KIND_UNDEF and not st.get(f, "ZST26"):
                    st.put(f, "ZST1", 1)
                    st.put(f, "ZDDS", dds13("N", 0, 4))
                    st.put(f, "ZST3", 1)
                    self.val._enter(f, at, 0, 0, 0)
                    at += 64
            self.top_word = at // 64
        for name, f in list(st.dictionary.items()):
            if st.get(f, "ZST0"):
                continue
            got = self.val.symbol_value(f)
            if got is None:
                if not first and st.get(f, "ZKIND") != KIND_UNDEF:
                    self.msg.add(7, f"NO VALUE FOR {name}", 0)   # MACHER
                continue
            st.put(f, "ZST0", 1)

    # -- Pass 2a, chart FA-FD ------------------------------------------------------
    def pass_a(self):
        self.np2ind = True
        self.val.vcundf = True
        self.abs, self.sym = self.origin, 0
        self.hilo.append((self.abs, self.sym))
        self.val.have_counters = True
        for unit in self.units.intin():
            self.unit_a(unit)
        self.hilo.append((self.abs, self.sym))

    def slcrcom_region(self, unit):
        """SLCRCOM's common: 0 blank, k named; "bad" if not a common."""
        if not self.units.get(unit, ZINFLD):
            return 0
        v = self.val.read_field(self.mem, unit + FIXED_BITS)
        if v.nullf:
            return 0
        if v.sym is not None:
            return self.common_of.get(v.sym, "bad")
        return v.I if v.avail and 0 < v.I <= len(self.comblocks) else "bad"

    def _set_dollar(self):
        self.val.abs, self.val.sym = self.abs, self.sym
        self.val.cur_region = self.region

    def _entry(self, unit):
        return ENTRIES[self.units.get(unit, ZIOPX)]

    def _round_a(self, unit, e):
        """Boxes 12A-12B [33]."""
        unit_bits = self.rounding(unit, e)
        if not unit_bits:
            return
        if not self.sym:
            self.abs = (self.abs + unit_bits - 1) // unit_bits * unit_bits
            return
        r = self.st.get(self.sym, "ZROUND")
        have = 64 if r == 2 else 32 if r == 1 else 0
        if have >= unit_bits:
            self.abs = (self.abs + unit_bits - 1) // unit_bits * unit_bits
            return
        f = self.st.special()
        self.st.put(f, "ZABS", self.abs)
        self.st.put(f, "ZSYM", self.sym)
        self.st.put(f, "ZROUND", 2 if unit_bits == 64 else 1)
        self.abs, self.sym = 0, f

    def rounding(self, unit, e):
        u = self.units
        if u.get(unit, ZIEXT2):
            return 0
        if e.name in ("DD", "DDI", "DR", "DRZ"):
            if u.get(unit, ZIFDSF):
                mode, _f, _b = dds_parts(u.get(unit, ZIDDS))
                if mode in ("N", "U"):
                    return 64
            return 0
        if e.name == "CNOP":
            return 64
        if e.pseudo:
            return 0
        return e.align

    def unit_a(self, unit):
        """Box 54, p.25: the error flags VALUE met are ORed into the unit."""
        self.val.flags = 0
        self._unit_a(unit)
        self._or_flags(unit)

    def _or_flags(self, unit):
        bits = self.val.flags | self.definition_flags(unit)
        self.val.flags = 0
        if bits:
            u = self.units
            u.put(unit, ZIFLAGS, u.get(unit, ZIFLAGS) | bits)

    def definition_flags(self, unit):
        """The flags on a statement that defines an erroneous symbol: C28-6129
        p.20 (2) and (3), N28-1081 page 7.  CHOSEN: QUEST on every definition,
        as p.20's "the statement that contains the symbol"; PSEUDO on the base
        of a circular chain, which UITER found (p.32)."""
        f = self.p1_named(unit)
        if not f:
            return 0
        st = self.st
        bits = 0
        if st.get(f, "ZST23"):
            if self.edition == "N28-1081" or st.dictionary.get(st.name_of[f]) != f:
                bits |= F_MULTI
        if st.get(f, "ZST22"):
            bits |= F_QUEST
        if st.get(f, "ZST4"):
            bits |= F_PSEUDO
        return bits

    def _unit_a(self, unit):
        u = self.units
        st = self.st
        e = self._entry(unit)
        self._round_a(unit, e)
        self._set_dollar()              # Box 13
        f = self.p1_named(unit)
        name = e.name
        self.unit_region[unit] = self.region
        if f:
            self.val.region[f] = self.region
        if name == "COMBLOCK":
            # Named commons are numbered from 1 in order (6729 pp.185-186;
            # 6751 p.30: "the original ordering ... be preserved").
            k = self.comblocks.setdefault(unit, len(self.comblocks) + 1)
            if f:
                self.common_of[f] = k
        if name == "SYN":
            # NSYN: its $ is the counter here; try once more now.
            if f:
                st.put(f, "ZABS", self.abs)
                st.put(f, "ZSYM", self.sym)
                st.put(f, "ZCTR", 1)
                self.val.symbol_value(f)
                if st.get(f, "ZEXPR"):
                    # its own expression, for the flags of the symbols in it
                    self.val.read_field(st.mem, st.get(f, "ZEXPR"))
            return
        # Boxes 14F, 17: the counters go in the unit and its symbol.
        u.put(unit, ZIADAB, self.abs & ((1 << 25) - 1))
        self.mem.put_signed(unit + ZIADSY[0], ZIADSY[1], 0)
        self.store_sym(unit)
        if f:
            st.put(f, "ZABS", self.abs)
            st.put(f, "ZSYM", self.sym)
            st.put(f, "ZCTR", 1)
        if name == "SLC" or name == "SLCR":
            self.nslc(unit, e)
            self.region = None      # CHOSEN: an SLC leaves the common
            return
        if name == "SLCRCOM":
            # 6729 p.187: Pass 1 marks the symbols that follow relative to
            # the common; "Pass 2's job is to set the location counter to
            # zero."  A blank field is blank common, #0; a name, the common
            # number in its COMBLOCK entry; CHOSEN: an integer, that number.
            self.region = self.slcrcom_region(unit)
            self.slcrcom_reg[unit] = self.region
            self.abs, self.sym = 0, 0
            return
        if name in ("END", "FEND"):
            # p.19: 2a scans every expression so all undefined symbols are entered.
            if u.get(unit, ZINFLD):
                self.val.read_field(self.mem, unit + FIXED_BITS)
            self.hilo.append((self.abs, self.sym))
            return
        if name == "TLB":
            if u.get(unit, ZINFLD):
                self.val.read_field(self.mem, unit + FIXED_BITS)
            return
        if name == "CNOP":
            self.cnop_a(unit)
            return
        if name == "SPNUS":
            self.spnus = True       # NSPRES, p.35
        if e.pseudo and name not in ("DD", "DDI", "DR", "DRZ", "EXT"):
            return
        # Boxes 14A-14K
        if name == "EXT":
            self.decode_ext_a(unit)
            return
        if u.get(unit, ZIEXT2):
            return
        if name in ("DD", "DDI"):
            self.advance_dd(unit)
            return
        if name in ("DR", "DRZ"):
            self.advance_dr(unit)
            return
        self.decode(unit, final=False)
        self.abs += ENTRIES[u.get(unit, ZIOPX)].length

    def p1_named(self, unit):
        if not self.units.get(unit, ZIFNME):
            return 0
        # p.33 "compute and save the location of the function"; Fig. 20 has no
        # field for it and p.13 matches units to entries by order.  CHOSEN: a
        # host map from Pass 1, which the 7030 version replaces with that scan.
        return self.p1.named_of.get(unit, 0)

    def store_sym(self, unit):
        """ZIADSY: CHOSEN, the special symbol's function address, which 2b needs."""
        self.units.put(unit, ZIADSY, self.sym)

    def nslc(self, unit, e):
        """NSLC [34-35]: adjust both counters; an entry for hi-lo."""
        addr = unit + FIXED_BITS
        v = self.val.read_field(self.mem, addr)
        if v.avail:
            self.abs, self.sym = v.total, 0
        else:
            f = self.st.special()
            self.st.put(f, "ZEXPR", addr_copy(self, addr, v.next))
            self.abs, self.sym = 0, f
        if e.name == "SLC":
            self.hilo.append((self.abs, self.sym))

    def cnop_a(self, unit):
        pass

    def decode_ext_a(self, unit):
        i, j, count = self.ext_params(unit)
        if count is None:
            raise Unresolved("EXT parameters are not known in Pass 2a")
        self.abs += count

    def ext_params(self, unit):
        addr = unit + FIXED_BITS
        vals = []
        for _k in range(self.units.get(unit, ZINFLD)):
            v = self.val.read_field(self.mem, addr)
            addr = v.next
            vals.append(None if v.nullf else v.total)
        vals += [None] * (3 - len(vals))
        i, j, n = vals[:3]
        given = sum(x is not None for x in (i, j, n))
        if given < 2:
            raise _a.AssemblerError("EXT needs any TWO of I, J and COUNT (C28-6129 printed p.19)")
        if n is None:
            n = j - i + 1
        elif i is None:
            i = j - n + 1
        elif j is None:
            j = i + n - 1
        return i, j, n

    def dd_length(self, unit, final):
        """KFNA [140]: field length x number of fields."""
        u = self.units
        if u.get(unit, DD_NUMERIC):
            mode, fl, bs = self.dd_dds(unit)
            return (fl or 64) * u.get(unit, ZINFLD)
        mode, fl, bs = self.dd_dds(unit)
        return u.get(unit, ZINFLD) * (bs or 8)

    def dd_dds(self, unit):
        """Evaluate a symbolic f.l. or b.s. kept first in the coded area."""
        u = self.units
        mode, fl, bs = dds_parts(u.get(unit, ZIDDS))
        p = unit + FIXED_BITS
        if u.get(unit, ZIFSFL):
            v = self.val.read_field(self.mem, p)
            p = v.next
            if not v.avail:
                raise Unresolved("symbolic field length")
            fl = v.total & 63
        if u.get(unit, ZIFSBS):
            v = self.val.read_field(self.mem, p)
            if not v.avail:
                raise Unresolved("symbolic byte size")
            bs = v.total & 15
        return mode, fl, bs

    def advance_dd(self, unit):
        try:
            self.abs += self.dd_length(unit, False)
        except Unresolved:
            self._dd_later(unit)

    def _dd_later(self, unit):
        """14J [34]: a new relative symbolic counter.  The length is the count
        times the f.l. (numeric) or the b.s. (alphabetic), which is the one
        coded expression the special symbol has to keep."""
        u = self.units
        p = unit + FIXED_BITS
        fl_at = bs_at = None
        if u.get(unit, ZIFSFL):
            fl_at = p
            p = self.val.read_field(self.mem, p).next
        if u.get(unit, ZIFSBS):
            bs_at = p
        at = fl_at if u.get(unit, DD_NUMERIC) else bs_at
        if at is None:
            # What is unknown does not touch the length: the b.s. of a numeric DD.
            mode, fl, bs = dds_parts(u.get(unit, ZIDDS))
            self.abs += u.get(unit, ZINFLD) * (fl or 64 if u.get(unit, DD_NUMERIC) else bs or 8)
            return
        v = self.val.read_field(self.mem, at)
        if v.avail:
            self.abs += u.get(unit, ZINFLD) * (v.total or 64)
            return
        f = self.st.special()
        self.st.put(f, "ZABS", self.abs)
        self.st.put(f, "ZSYM", self.sym)
        self.st.put(f, "ZDIMX", addr_copy(self, at, v.next))
        self.st.put(f, "ZDIMN", 1)
        self.st.put(f, "ZFLM", u.get(unit, ZINFLD))
        self.abs, self.sym = 0, f

    def _dr_dims(self, unit):
        """The dimension fields after any symbolic dds, and how many."""
        u = self.units
        p = unit + FIXED_BITS
        for flag in (ZIFSFL, ZIFSBS):
            if u.get(unit, flag):
                p = self.val.read_field(self.mem, p).next
        return p, u.get(unit, ZINFLD)

    def dr_size(self, unit):
        mode, fl, bs = self.dd_dds(unit)
        p, n = self._dr_dims(unit)
        size = fl or 64
        for _k in range(n):
            v = self.val.read_field(self.mem, p)
            p = v.next
            if not v.avail:
                return None
            # A zero dimension reserves nothing: IBM's own example writes
            # "COMLAST DR(N), 0" to name the end of blank common (C22-6729
            # p.184, read in the ink 2026-11-11).
            if v.total < 0:
                raise _a.AssemblerError(f"DR dimension {v.total} is negative")
            size *= v.total
        return size

    def advance_dr(self, unit):
        size = self.dr_size(unit)
        if size is not None:
            self.abs += size
            return
        # 14J: the dimension needs a symbol Pass 2a does not yet have.
        mode, fl, bs = self.dd_dds(unit)
        p, n = self._dr_dims(unit)
        end = p
        for _k in range(n):
            end = self.val.read_field(self.mem, end).next
        f = self.st.special()
        self.st.put(f, "ZABS", self.abs)
        self.st.put(f, "ZSYM", self.sym)
        self.st.put(f, "ZDIMX", addr_copy(self, p, end))
        self.st.put(f, "ZDIMN", n)
        self.st.put(f, "ZFLM", fl or 64)
        self.abs, self.sym = 0, f

    # -- DECODE, chart DC p.139 ----------------------------------------------------
    def decode(self, unit, final):
        u = self.units
        if final:
            self.reloc.pop(unit, None)
        e = ENTRIES[u.get(unit, ZIOPX)]
        p = unit + FIXED_BITS
        fields = []
        n = u.get(unit, ZINFLD)
        dds = None
        explicit = u.get(unit, ZIFDSF)
        if explicit:
            mode, fl, bs = self.dd_dds(unit) if self._dds_known(unit) else dds_parts(u.get(unit, ZIDDS))
            for flag in (ZIFSFL, ZIFSBS):
                if u.get(unit, flag):
                    p = self.val.read_field(self.mem, p).next
            dds = (mode, fl, bs)
        if u.get(unit, ZIFPMN):
            v = self.val.read_field(self.mem, p)
            p = v.next
            if v.dds is not None:
                m, fl, bs = dds_parts(v.dds)
                dds = (m, fl, bs)
        for _k in range(n):
            v = self.val.read_field(self.mem, p)
            p = v.next
            fields.append(v)
        # Box 5: the convention dds, after the symbol's own (implicit, p.205).
        if e.dds_needed or e.ambiguous:
            e, dds = self._establish(unit, e, dds, fields, explicit, final)
        word = e.skeleton
        word = self._fill(unit, e, word, fields, dds, final)
        for v in fields:
            for bit, value in v.gps:
                # C28-6129 printed p.25: counted from the statement's bit zero.
                if final and bit + 1 > e.length:
                    raise _a.AssemblerError(f"parenthetical integer entry (.{bit}) needs {bit + 1} bits but this statement compiles only {e.length} (C28-6129 printed p.25)")
                if final and abs(value) >= 1 << 24:
                    raise _a.AssemblerError(f"parenthetical integer entry (.{bit}) evaluates to {value}, more than the 24 significant bits the entry converts (C28-6129 printed p.25)")
                word = _orbits(word, 0, bit + 1, value)
        u.put(unit, ZIOPX, e.index)
        u.put(unit, ZILBO, e.length if e.length < 128 else 0)
        u.put(unit, ZIOTPT, word)
        self.unavailable = [v for v in fields if not v.avail]
        return e

    def _dds_known(self, unit):
        try:
            self.dd_dds(unit)
            return True
        except Unresolved:
            return False

    def _establish(self, unit, e, dds, fields, explicit, final=True):
        implicit = False
        if dds is None and fields and fields[0].dds is not None:
            dds = dds_parts(fields[0].dds)
            implicit = True
        # p.24: two or more fields on an ambiguous op makes it VFL.
        if e.ambiguous and dds is not None and dds[0] in ("N", "U") and len(fields) < 2:
            e = lookup(e.written_op, dds[0], ())
            return e, dds
        if e.ambiguous and explicit:
            e = lookup(e.written_op, dds[0], ())
        if e.is_conn and implicit and dds[0] in ("N", "U"):
            dds = ("BU", 0, 4)
        if e.kind == "fp":
            return e, dds
        if dds is None:
            dds = ("BU", 0, 8)     # p.140: (BU,64,8); immediate (BU,24,8) below
            if e.immediate:
                dds = ("BU", 0, 8)
        if dds[0] in ("N", "U") and not e.is_conn:
            if implicit:
                dds = ("BU", 0, 8)
                if final:   # DECODE runs in 2a and 2b; the message once, from 2b
                    self.msg.add(91, "MODE INCONSISTENT WITH OP", unit, fatal=False)
            else:
                raise _a.AssemblerError(f"mode {dds[0]} on the VFL op {e.written_op}")
        if not e.is_conn and getattr(e, "explicit_mode", None) != dds[0]:
            e = lookup(e.written_op, dds[0], self._secondaries(e))
        return e, dds

    def _secondaries(self, e):
        p = getattr(e, "progressive", None)
        if p is None:
            return ()
        names = {v: k for k, v in _a.PROGRESSIVE_SECONDARY_OP.items()}
        return (names[p],)

    # -- INSERT, p.144 --------------------------------------------------------------
    def _fill(self, unit, e, word, fields, dds, final):
        self.filling = (unit, final)    # for an inserter's message
        limit = sum(n for _r, n in e.fills)
        if e.kind in ("vfl", "conn"):
            word = put(word, 35, 6, dds[1])
            word = put(word, 41, 3, dds[2])
        vals = list(fields)
        if e.kind == "io":
            if e.fixed_code is not None:
                vals = vals + [_literal(e.fixed_code)]
            elif e.rel and len(vals) == 1:
                vals = vals + [_literal(0)]
        k = 0
        for routine, count in e.fills:
            fn = getattr(self, "i_" + routine)
            if count == 1:
                if k < len(vals):
                    word = fn(word, vals[k], e, dds)
                    self._reloc_field(routine, vals[k])
                else:
                    word = fn(word, _literal(0), e, dds)
                k += 1
            else:
                for v in vals[k:]:
                    word = fn(word, v, e, dds)
                    self._reloc_field(routine, v)
                k = len(vals)
        return word

    # Where each inserter puts an address that relocation can reach: the first
    # 18 bits of a half-word ("L", address) or its last 18 ("R", refill), the
    # relocation bits' two choices (C22-6729 p.188; the loader, printed p.325
    # lines 9-16).  Any other field cannot carry relocation bits.
    RELOC_AT = {
        "S18A": (0, "L"), "S19IA": (0, "L"), "S18X": (0, "L"), "S19KF": (0, "L"),
        "S24A": (0, "L"), "SSIC24": (0, "L"), "STTI": (0, "L"), "SIM19": (0, "L"),
        "SIMC": (0, "L"), "SIMAD": (0, "L"), "SXP10": (0, "L"), "SCHAN": (0, "L"),
        "S24SNI": (0, "L"), "SCW": (0, "L"), "S18W": (0, "L"), "SVF": (0, "L"),
        "S19BBK": (32, "L"), "STT19A": (32, "L"), "SIOA": (32, "L"),
        "S18RF": (46, "R"),
    }

    def _reloc_field(self, routine, v):
        """INSERT's relocation check (C22-6729 p.185; bss_loader_spec.md 9): in
        PUNREL mode a field whose value counts a location-counter-dependent
        symbol is relocated.  More than one is message 123 (6729 p.178; 121 in
        C28-6129 Appendix p.55), and since what VALUE then returns is
        UNSPECIFIED, the deck stops there."""
        if not self.rel or not v.lc:
            return
        unit, final = getattr(self, "filling", (0, True))
        if not final:
            return
        if v.lc > 1:
            self.msg.add(123, "MORE THAN 1 LOC. CTR. DEP. SYMBOL", unit, fatal=False)
            self.punch.unwritten = self.punch.unwritten or "relocation of more than 1 location counter symbol"
            return
        at = self.RELOC_AT.get(routine)
        if at is None:
            self.punch.unwritten = self.punch.unwritten or f"a relocatable value in the {routine} field"
            return
        self.reloc.setdefault(unit, []).append(at + (v.reg,))

    # Absolute values from Sinb, Sini, Sinx, by the address's function (p.144).
    @staticmethod
    def _a18(v):
        return (v.B >> 6) + v.I

    @staticmethod
    def _a19(v):
        return (v.B >> 5) + v.I

    @staticmethod
    def _a24(v):
        return v.B + v.I

    @staticmethod
    def _idx(word, v, pos=28):
        return put(word, pos, 4, v.X) if v.xq else word

    def i_S18A(self, word, v, e, dds):
        return self._idx(put(word, 0, 18, self._a18(v)), v)

    def i_S19IA(self, word, v, e, dds):
        return self._idx(put(word, 0, 19, self._a19(v)), v)

    def i_S18X(self, word, v, e, dds):
        # p.24 of the Reference Manual: LX and SX use bits 0-17 of the effective
        # address, so an integer counts words in this 19-bit field.
        return self._idx(put(word, 0, 19, (v.B >> 5) + (v.I << 1)), v)

    def i_S19KF(self, word, v, e, dds):
        word = put(word, 0, 19, self._a19(v))
        return put(word, 31, 1, v.X) if v.xq else word

    def i_S24A(self, word, v, e, dds):
        return self._idx(put(word, 0, 24, self._a24(v)), v)

    i_SSIC24 = i_S24A

    def i_S19BBK(self, word, v, e, dds):
        word = put(word, 32, 19, self._a19(v))
        return put(word, 63, 1, v.X) if v.xq else word

    def i_SOFF(self, word, v, e, dds):
        word = put(word, 44, 7, self._a24(v))
        return self._idx(word, v, 60)

    def i_SJFLD(self, word, v, e, dds):
        return put(word, 19, 4, (v.B >> 6) + v.I)

    def i_STJFLD(self, word, v, e, dds):
        return put(word, 51, 4, (v.B >> 6) + v.I)

    i_STTI = i_S24A

    def i_STT19A(self, word, v, e, dds):
        word = put(word, 32, 19, self._a19(v))
        return self._idx(word, v, 60)

    def i_SIM19(self, word, v, e, dds):
        return put(word, 0, 19, self._a19(v))

    def i_SIMC(self, word, v, e, dds):
        return put(word, 0, 19, self._a18(v) << 1)

    def i_SBIT(self, word, v, e, dds):
        n = ((v.B >> 6) + v.I) & 15
        return word | (1 << (63 - n))

    def i_SIMAD(self, word, v, e, dds):
        # p.144, and the Reference Manual p.56's left-justified immediate.
        length = dds[1] or 64
        if v.B and not v.I:
            a = v.B
        elif length <= 24:
            a = ((v.B >> (24 - length)) + v.I) << (24 - length)
        else:
            value = v.B + v.I
            low = length - 24
            if value & ((1 << low) - 1):
                raise _a.AssemblerError(
                    f"immediate value {value} has nonzero bits below a "
                    f"{length}-bit field's top 24 (Reference Manual p.56)")
            a = value >> low
        return self._idx(put(word, 0, 24, a), v)

    def i_SXP10(self, word, v, e, dds):
        if v.B:
            word = put(word, 0, 18, self._a18(v))
        else:
            mag = abs(v.I)
            word = put(word, 0, 18, ((1 if mag > 1023 else 0) << 17) |
                       ((mag & 0x3FF) << 7) | ((1 if v.I < 0 else 0) << 6))
        return self._idx(word, v)

    def i_SCHAN(self, word, v, e, dds):
        return self._idx(put(word, 0, 24, self._a24(v)), v)

    def i_SIOA(self, word, v, e, dds):
        if e.code_field:
            a = (v.B >> 6) + v.I
        else:
            a = (v.B + v.I) >> 6
        word = put(word, 32, 18, a)
        return self._idx(word, v, 60)

    def i_S24SNI(self, word, v, e, dds):
        t = v.B + v.I
        word = put(word, 0, 24, abs(t))
        word = put(word, 24, 1, 1 if t < 0 else 0)
        return word

    def i_SFLGS(self, word, v, e, dds):
        return put(word, 25, 3, v.B + v.I)

    def i_S18CF(self, word, v, e, dds):
        return put(word, 28, 18, self._a18(v))

    def i_S18RF(self, word, v, e, dds):
        return put(word, 46, 18, self._a18(v))

    def i_SCW(self, word, v, e, dds):
        return put(word, 0, 18, self._a18(v))

    def i_S18W(self, word, v, e, dds):
        return put(word, 0, 18, self._a18(v))

    def i_SVF(self, word, v, e, dds):
        t = v.B + v.I
        word = put(word, 0, 24, abs(t))
        return put(word, 24, 1, 1 if t < 0 else 0)

    def i_SINDMK(self, word, v, e, dds):
        bit = (v.B & 63) if v.B >= 11 * 64 and v.B < 12 * 64 else v.B + v.I
        if not 0 <= bit <= 63:
            raise _a.AssemblerError(f"INDMK bit {bit} is outside a word's bits 0-63 (C28-6129 printed p.19)")
        unit, final = getattr(self, "filling", (0, True))
        if word >> (63 - bit) & 1 and final:
            self.msg.add(121, "BIT ADDRESSED TWICE IN LVS OR INDMK", unit)
        return word | (1 << (63 - bit))

    # -- Pass 2b ---------------------------------------------------------------------
    def pass_b(self):
        self.np2ind = False
        self.val.vcundf = False
        self.abs, self.sym = self.origin, 0
        self.running = self.origin
        self.val.have_counters = True
        pending = None
        unit = 0
        for unit in self.units.intin():
            pending = self.unit_b(unit, pending)
        self.punch.finish(unit)
        # LIM (C22-6678-1 p.8): n1 the word holding the lowest bit loaded or
        # reserved (the first origin card's origin), n2 the word after the
        # highest, the undefined symbols' words counted (CHOSEN).
        starts = [c.origin for c in self.punch.cards if c.kind == "origin"]
        high = getattr(self, "top_word", self.upper // 64)
        self.punch.lim = (min(starts) // 64 if starts else high, high)
        return self

    # -- NUNDSY, charts EG and EH pp.170-171, text p.172 ----------------------------
    def nundsy(self):
        """The symbol lists OUTPUT ends with.  One iteration of the vles (ANEXT):
        an undefined symbol is listed at once with its address; the unused, the
        multiply defined with contradictions and the circular are stacked and
        listed after, the unused with addresses and the others by name only.  A
        legal multiple gets message 131 instead (box 13).  Only the first 50
        characters of a name print (p.172).  SPNUS suppresses the unused list
        (box 10A).

        CHOSEN: a symbol counts as used if the vle the dictionary holds was
        referenced, since a later definition's vle is never looked up; and a
        name with two vles is listed and given 131 once."""
        st = self.st
        lists = {"undefined": [], "unused": [], "multiple": [], "circular": []}
        seen = set()

        def address(f):
            got = self.val.symbol_value(f)
            return None if got is None else got[0] + got[1]

        for f in st.vles:
            name = st.name_of.get(f, "")
            kind = st.get(f, "ZKIND")
            if not name or name.startswith("\xff") or kind == KIND_SPECIAL:
                continue
            short = name[:50]
            if st.get(f, "ZST1"):                               # box 4
                lists["undefined"].append((short, address(f)))  # boxes 8, 9
                continue
            if (not self.spnus and kind != KIND_UNDEF          # boxes 10A, 10B
                    and st.dictionary.get(name) == f and not st.get(f, "ZST24")):
                lists["unused"].append((short, address(f)))     # box 11
            if st.get(f, "ZST22"):                              # box 12
                if ("q", name) not in seen:
                    seen.add(("q", name))
                    self.msg.add(131, f"MULT. DEFINED SYM WITH NO CONTRADICTION {short}",
                                 0, fatal=False)
                continue
            if st.get(f, "ZST23"):                              # box 14
                if ("m", name) not in seen:
                    seen.add(("m", name))
                    lists["multiple"].append((short, None))
                continue
            if st.get(f, "ZST4"):                               # box 16
                lists["circular"].append((short, None))
        return lists

    def comrec_errors(self):
        """The communication record's error bits STRAP II sets (C22-6729 p.8;
        N28-1081 page 7): 41 for symbols in error, 42 for p.8's list, 43 for any
        message.  p.8's list for 42 is, in order, the conditions of messages 1-7
        (pp.176), so 42 is messages 1-7 (DERIVED), plus "symbolic statement too
        long", an I-O message with no number that strap2 never gives.  Not the
        serious messages (1-28, or 1-18 in the update), and not the host's
        `fatal`, which only decides what assemble(strict=True) refuses.  CHOSEN:
        a legal multiple (QUEST) does not set 41, since C28-6129 p.20 calls it
        legal; p.8 names "multiply-defined" and N28-1081 "multiply defined"
        without saying which."""
        st = self.st
        bits = set()
        for name, f in st.dictionary.items():
            if name.startswith("\xff"):
                continue
            if (st.get(f, "ZST1") or st.get(f, "ZST23") or st.get(f, "ZST4")
                    or st.get(f, "ZSTCTG")):
                bits.add(41)
        for number, _text, _unit, _fatal in self.msg.items:
            bits.add(43)
            if 1 <= number <= 7:
                bits.add(42)
        return bits

    def location_2a(self, unit):
        u = self.units
        absc = self.mem.get(unit + ZIADAB[0], ZIADAB[1])
        symc = u.get(unit, ZIADSY)
        return self.val.counter_value(absc, symc), absc, symc

    def unit_b(self, unit, pending):
        """CHOSEN: the flags are ORed again in 2b.  p.25 names Pass 1 and 2a, but
        a symbol defined through an undefined one is only complete, and so only
        contagious, after the second UITER."""
        self.val.flags = 0
        before = self.running
        # WHAT IS ASSEMBLED UNDER PUNFUL IS NOT LOADED (C28-6129 pp.23, 36): it
        # goes on full cards.  Its bits are kept in a scratch image the punch
        # reads, so code assembled over them later (MCP printed pp.2, 15: the
        # header DDs at 000041.00 and 000621.00, overlaid by the program) is
        # not an overlap.  The SLC skips stay the real image's.
        loaded = self.image
        reg = self.unit_region.get(unit)
        if reg is not None:
            # After SLCRCOM the counter starts again at zero in the common
            # (6729 p.187): its data is a separate space, not the program's.
            self.image = self.common_images.setdefault(reg, _a.Image())
        elif self.punch.punful:
            if self._full_image is None:
                self._full_image = _a.Image()
                self._full_image.skips = loaded.skips
            self.image = self._full_image
        else:
            self._full_image = None
        try:
            pending = self._unit_b(unit, pending)
            self._or_flags(unit)
            self._punch_unit(unit, before)
        finally:
            self.image = loaded
        return pending

    def _punch_unit(self, unit, before):
        """OUTPUT's punch buffer (punch.py): what this unit put out, in order."""
        pu = self.punch
        e = self._entry(unit)
        printed = self.printed.get(unit)
        kind = printed[0] if printed else None
        if pu.unwritten:
            return
        if e.mcp:
            pu.mcp += 1
            try:
                pu.text_card(unit, self.mcp_card(unit, e))
            except PunchError as x:
                pu.unwritten = f"{e.name}: {x}"
            return
        # PUNFPC / PUNCDC mode ends at any other statement (C22-6729 p.186).
        if pu.group is not None and (pu.group.kind, e.name) not in (
                ("fprog", "ENTER"), ("comdef", "COMBLOCK")):
            pu.group_end(unit)
        if e.name in self.RELOC_OPS:
            self._relocation_op(unit, e, printed)
            return
        if e.name == "SLCRCOM":
            if not self.rel:
                self.msg.add(136, "RELOCATABLE PSEUDO-OP., NOT IN PUNREL MODE", unit, fatal=False)
                return
            pu.slcrcom(unit, self.slcrcom_reg.get(unit))
            return
        if e.name == "PUNID" and pu.punful:
            self.msg.add(127, "PUNID IN PUNFUL SEQUENCE -- STATE. IGNORED", unit, fatal=False)
            return
        if e.name == "PUNFUL":
            pu.punful_(unit)
            return
        if e.name == "PUNID":
            p = self.units.get(unit, ZIOTPT)
            if p:                   # message 55 left no ID
                pu.punid(unit, "".join(chr(self.mem.get(p + 8 * k, 8)) for k in range(8)))
            return
        if e.name == "NOPUN":
            pu.nopun(unit)
            return
        if e.name == "PUNNOR":
            pu.punnor(unit)
            return
        if e.name == "PUNORG":
            pu.punorg_(unit)
            return
        if e.name == "NOSEQ":
            pu.noseq_(unit)
            return
        if e.name == "RESEQ":
            pu.reseq(unit)
            return
        if e.name == "SLCR":
            # Guide p.36: "If OUTPUT receives a unit of an SLCR, OUTPUT stops
            # punching cards until the next SLC unit is encountered" (chart OT
            # p.153 draws nothing for it); C28-6129 p.39: none of the statements
            # after appear in the binary output.  CHOSEN: the card in process
            # goes out first, as at every other stop.
            pu.slc(unit)
            pu.relative = True
            return
        if e.name == "SLC":
            pu.relative = False
        if pu.suppressed or pu.relative:
            return
        if kind == "TLB":
            pu.tlb(unit, printed[2])
            return
        if e.name == "PUNREL":
            if pu.rel:
                return
            # PUNFPC and PUNCDC may come first (p.184's example): Pass 1's
            # Punrel bit, not the order, puts OUTPUT in PUNREL mode (p.186).
            if self.rel and all(c.kind in ("fprog", "comdef") for c in pu.cards):
                pu.punrel_(unit)
            else:
                # Not written: a PUNREL after absolute output (_punrel_scan).
                pu.unwritten = "PUNREL after absolute output"
            return
        if kind == "SLC":
            pu.slc(unit, printed[1])
        elif kind == "END":
            pu.end(unit, printed[2])
        elif kind == "DR":
            pu.reserve(unit, printed[1], printed[2], e.name == "DRZ", before)
        elif self.running != before:
            start = before
            if kind in ("INSTR", "NUM", "ALPHA") and printed[1] < before:
                start = printed[1]
            n = self.running - start
            if n > 0:
                if pu.rel:
                    at = printed[1]
                    pu.rel_data(unit, start, n, self._image_bits(start, n),
                                kind == "INSTR",
                                [(at + b, side, reg) for b, side, reg in self.reloc.get(unit, ())])
                else:
                    pu.data(unit, start, n, self._image_bits(start, n))

    RELOC_OPS = ("ORIGIN", "PUNFPC", "ENTER", "PUNCDC", "COMBLOCK", "FEND")

    def _relocation_op(self, unit, e, printed):
        """The relocation pseudo-ops but PUNREL and SLCRCOM (C22-6729 pp.183,
        186-188; N28-1081 page 3, all read in the ink 2026-11-11).  Pass 2
        "does not accept relocation pseudo-ops if it is not in PUNREL mode"
        (p.186): message 136, and nothing punched (CHOSEN: a FEND then ends
        the assembly as an END would, with END's branch card)."""
        pu = self.punch
        name = e.name
        if not self.rel:
            self.msg.add(136, "RELOCATABLE PSEUDO-OP., NOT IN PUNREL MODE", unit, fatal=False)
            if name == "FEND":
                pu.end(unit, printed[2] if printed else None)
            return
        if name == "FEND":
            pu.fend(unit)
            return
        if name == "PUNCDC":
            pu.group_start(unit, "comdef")
            return
        fields = []
        p = unit + FIXED_BITS
        for _ in range(self.units.get(unit, ZINFLD)):
            v = self.val.read_field(self.mem, p)
            if not v.avail:
                self.msg.add(7, "ASSEMBLY ERROR", unit)
                return
            fields.append(None if v.nullf else v)
            p = v.next

        def words(k):
            # An 18-bit field: an integer counts full words, a bit address
            # is in bits (C28-6129 p.33).  N28-1081 page 3: "If either is not
            # a full word, STRAP will round it up to the next higher full
            # word."  CHOSEN for COMBLOCK's size too.
            v = fields[k] if k < len(fields) else None
            if v is None:
                return 0
            return (((v.B + 63) >> 6) + v.I) & 0o777777
        if name == "ORIGIN":
            if not fields or fields[0] is None:
                self.msg.add(7, "ASSEMBLY ERROR", unit)
                return
            pu.origin_card(unit, fields[0].total)
            return
        if name == "PUNFPC":
            pu.group_start(unit, "fprog", words(0), words(1))
            return
        label = self.p1.print_names.get(unit, ("",))[0] or ""
        if len(label) > 8:
            # CHOSEN: the first eight characters are punched.  NOT EXERCISED:
            # a card's name field is columns 2-9, so no test reaches this.
            self.msg.add(139, "NAME LONGER THAN 8 CH. ON COMBLOCK OR ENTER", unit, fatal=False)
        if name == "ENTER":
            # The entry address, a nineteen-bit field (p.186): an integer
            # counts half-words (C28-6129 p.33).  CHOSEN: a point inside a
            # half-word gives its half-word.
            v = fields[0] if fields else None
            at = self._a19(v) if v is not None else 0
            if not pu.group_add(unit, "fprog", label[:8], at & 0o1777777):
                self.msg.add(138, "ENTER STATEMENT, NOT IN PUNFPC MODE", unit, fatal=False)
            return
        # COMBLOCK.  "If the statement does not have a name, an error message
        # is given, and the address field is still encoded" (p.186); the
        # message's number is not printed, so the deck stops here.
        if not label:
            pu.unwritten = pu.unwritten or "a COMBLOCK without a name (p.186: an error message, its number not printed)"
            return
        if not pu.group_add(unit, "comdef", label[:8], words(0)):
            self.msg.add(137, "COMBLOCK STATEMENT WHEN NOT IN PUNCDC MODE", unit, fatal=False)

    def statement_text(self, unit):
        """The statement as Pass 1 kept it (Zilsst bytes after the coded fields)."""
        u = self.units
        start = (unit + FIXED_BITS + u.get(unit, ZILCFD) + 63) // 64 * 64
        return "".join(chr(self.mem.get(start + 8 * k, 8)) for k in range(u.get(unit, ZILSST)))

    def mcp_card(self, unit, e):
        """An IOD or REEL card as submitted (C22-6678-1 pp.9-10): B, the name in
        2-9, the statement in 10-62; an IOD's reference number and exit word
        address in 63-66 and 67-72, octal.  CHOSEN: a null exit punches 000000,
        and an exit not on a full word punches the word holding it."""
        name = (self.p1.print_names.get(unit, ("",))[0] or "")
        lines = [t.rstrip() for t in self.statement_text(unit).split("\n") if t.strip()]
        if len(name) > 8 or len(lines) != 1 or len(lines[0]) > 53:
            raise PunchError(f"{e.name} card does not fit columns 2-62: {name!r} {lines!r}")
        text = "B" + name.ljust(8) + lines[0].ljust(53)
        if e.name == "IOD":
            u = self.units
            exit_ = 0
            if u.get(unit, ZINFLD):
                v = self.val.read_field(self.mem, unit + FIXED_BITS)
                exit_ = v.total // 64 if v.avail else 0
            text += f"{u.get(unit, ZILPMS) & 0o7777:04o}{exit_ & 0o777777:06o}"
        return text.rstrip()

    def _image_bits(self, at, n):
        v = 0
        words = self.image.words
        for k in range(at, at + n):
            v = (v << 1) | ((words.get(k // 64, 0) >> (63 - k % 64)) & 1)
        return v

    def _unit_b(self, unit, pending):
        u = self.units
        e = self._entry(unit)
        name = e.name
        if name == "SYN":
            return pending
        at, absc, symc = self.location_2a(unit)
        if at is None:
            self.msg.add(7, "NO LOCATION IN PASS 2B", unit)
            return pending
        self.val.abs, self.val.sym = absc, symc
        self.val.cur_region = self.unit_region.get(unit)
        if name == "SLCRCOM":
            self.printed[unit] = ("SLCRCOM", 0)
            self.running = 0
            return pending
        if name in ("SLC", "SLCR"):
            v = self.val.read_field(self.mem, unit + FIXED_BITS)
            if not v.avail:
                self.msg.add(7, "ASSEMBLY ERROR", unit)
            if name == "SLC" and v.total > self.running:
                self.image.skips.append((self.running, v.total - self.running))
            if v.total < 0:
                raise _a.AssemblerError(f"SLC operand evaluates to {v.total} bits, negative (C22-6531 p.32)")
            self.printed[unit] = ("SLC", v.total)
            self.running = v.total
            return pending
        if name in ("END", "FEND"):
            v = self.val.read_field(self.mem, unit + FIXED_BITS) if u.get(unit, ZINFLD) else None
            if v is not None and not v.avail:
                self.msg.add(7, "ASSEMBLY ERROR", unit)
            if v is not None and not v.nullf:
                t = v.total
                if t % 32:
                    raise _a.AssemblerError("END target is not half-word aligned")
                self.end_pc = t // 32
            self.printed[unit] = ("END", at, None if v is None or v.nullf else v.total)
            return pending
        if name == "TLB":
            # C28-6129 p.39: like END, but the assembly goes on.  Chart OR: the
            # address goes in the print line.
            v = self.val.read_field(self.mem, unit + FIXED_BITS) if u.get(unit, ZINFLD) else None
            if v is not None and not v.avail:
                self.msg.add(7, "ASSEMBLY ERROR", unit)
            self.printed[unit] = ("TLB", at, None if v is None or v.nullf else v.total)
            return pending
        if name == "CNOP":
            return self.cnop_b(unit, at, pending)
        if name == "EXT":
            i, j, n = self.ext_params(unit)
            return (unit, at, i, n)
        if u.get(unit, ZIEXT2):
            self.ext_b(unit, pending)
            return None
        if e.pseudo and name not in ("DD", "DDI", "DR", "DRZ"):
            return pending
        if name in ("DD", "DDI"):
            self.dd_b(unit, at)
            return pending
        if name in ("DR", "DRZ"):
            self.dr_b(unit, at, name)
            return pending
        # Instructions and index words
        e = self.decode(unit, final=True)
        self._gap(at, e)
        word = u.get(unit, ZIOTPT)
        self._check_unavailable(unit)
        self.deposit(at, e, word)
        self.printed[unit] = ("INSTR", at, e.length, e.name)
        self.running = at + e.length
        return pending

    def _check_unavailable(self, unit):
        if self.unavailable:
            self.msg.add(7, "ASSEMBLY ERROR", unit)

    def _gap(self, at, e):
        """strap_asm's gap rule: rounding before an instruction fills with zeros
        to a half word and NOPs beyond (p.33 box 12E makes a CNOP a NOP)."""
        if at == self.running or e.kind in ("data",):
            return
        self._fill_gap(self.running, at)

    def _fill_gap(self, start, at):
        size = at - start
        if size <= 0:
            return
        pad = (-start) % 32
        if pad:
            self.image.deposit(start, min(pad, size), 0)
            start += pad
            size -= pad
        for off in range(0, max(size, 0), 32):
            self.image.deposit_half((start + off) // 32,
                                    lookup("NOP").skeleton >> 32)

    def cnop_b(self, unit, at, pending):
        self._fill_gap(self.running, at)
        self.running = at
        return pending

    def deposit(self, at, e, word):
        if e.length == 64:
            self.image.deposit_word_instr(at, word) if at % 32 == 0 else self.image.deposit(at, 64, word)
        elif e.length == 32:
            self.image.deposit_half(at // 32, word >> 32)
        else:
            self.image.deposit(at, e.length, word >> (64 - e.length))

    def dd_b(self, unit, at):
        u = self.units
        mode, fl, bs = self.dd_dds(unit)
        loc = u.get(unit, DD_LOC)
        if u.get(unit, DD_NUMERIC):
            self._numeric_b(unit, at, mode, fl or 64, bs, loc)
            return
        n = u.get(unit, ZILPMS)
        text = "".join(chr(self.mem.get(loc + 8 * k, 8)) for k in range(n))
        tag = u.get(unit, ZIOTPT) & 3
        pos = at
        if tag == 2:
            self._cc_b(unit, at, bs, text)
            return
        from charsets import ENTRY_MODES
        table = ENTRY_MODES[{0: "A", 1: "IQS", 2: "CC", 3: "P"}[tag]]
        width = bs or 8
        for ch in text:
            if ch not in table:
                raise _a.AssemblerError(f"character {ch!r} is not in the character set (Reference Manual printed p.166)")
            self.image.deposit(pos, width, table[ch])
            pos += width
        self.printed[unit] = ("ALPHA", at)
        self.running = pos

    def _cc_b(self, unit, at, bs, text):
        """Entry mode CC (C28-6129 p.16, PDF 20): each character "converted to
        12-bit bytes, where each byte reflects the multiple punch actually read
        in the appropriate card column".  The punches are C22-6678-1 App. F
        p.56's (strap/cards.py).  The byte's bit order is the column as the
        reader delivers it, row 12 high, then 11, 0, 1-9: READ in MCP's own
        loader, whose card-type table ATBL (printed p.331 lines 24-38) compares
        column 1 as read with 4200 for B, 2010 for O, 1300 for 0-2-3 and so on
        (tests/check_strap2_punch.py G9).  It is also what
        makes MCP's PUNFUL header cards (printed pp.320, 335, 361, 381) read
        back as the control cards they spell.  Message 84 without byte size 12
        (CHOSEN: 12 is used anyway); 79 for a character App. F does not give
        punches for (CHOSEN: punched blank)."""
        import cards as hollerith
        if bs != 12:
            self.msg.add(84, "CC ENTRY MODE WITHOUT BS 12", unit)
        pos = at
        for ch in text:
            try:
                v = hollerith.column_bits(ch)
            except ValueError:
                self.msg.add(79, f"INCORRECT CARD CODE CHAR. {ch!r}", unit)
                v = 0
            self.image.deposit(pos, 12, v)
            pos += 12
        self.printed[unit] = ("ALPHA", at)
        self.running = pos

    def _numeric_b(self, unit, at, mode, fl, bs, p):
        """OUTPUT's numeric DD [26, 158-159]: each Fig. 26 entry to its final
        bits, then each g.p. ORed in (C28-6129 printed p.25)."""
        pos = at
        # C28-6129 p.30 d: "DD(BU, 12(.2)7, 8)": a g.p. on the field length is
        # ORed into every field.
        every = []
        if self.units.get(unit, ZIFSFL):
            every = self.val.read_field(self.mem, unit + FIXED_BITS).gps
        while True:
            fn, num, sbits, xexp, gps, more, p = load_entry(self.mem, p, self.val.read_chain)
            try:
                self.image.deposit(pos, fl, final(mode, fl, bs, num, fn, sbits or None, xexp))
            except DnumError as err:
                self.msg.add(err.number, str(err), unit)
            for bit, value in every + gps:
                self.image.or_into(pos, bit + 1, value)
            pos += fl
            if not more:
                break
        self.printed[unit] = ("NUM", at, mode, fl, bs, (pos - at) // fl)
        self.running = pos

    def dr_b(self, unit, at, name):
        size = self.dr_size(unit)
        if size is None:
            self.msg.add(7, "DR DIMENSION NOT EVALUATED", unit)
            return
        if name == "DR":
            self.image.reserve(at, size)
        else:
            mode, fl, bs = self.dd_dds(unit)
            width = fl or 64
            for k in range(size // width):
                self.image.reserve_zero(at + k * width, width)
        self.printed[unit] = ("DR", at, size)
        self.running = at + size

    def ext_b(self, unit, pending):
        """Chart OP boxes 3, 4: construct the requested extract from the second
        unit, compiled apart.  Its $ is 0, as strap_asm found the listings need."""
        ext_unit, at, i, count = pending
        keep = (self.image, self.val.abs, self.val.sym, self.running)
        scratch = _a.Image()
        self.image = scratch
        self.val.abs, self.val.sym = 0, 0
        self.running = 0
        try:
            e = self._entry(unit)
            if e.name in ("DD", "DDI"):
                self.dd_b(unit, 0)
            elif e.pseudo:
                self.msg.add(122, "EXTRACT FROM A PSEUDO OP", unit, fatal=False)
            else:
                e = self.decode(unit, final=True)
                self.deposit(0, e, self.units.get(unit, ZIOTPT))
        finally:
            self.image, self.val.abs, self.val.sym, self.running = keep
        word = scratch.words.get(0, 0)
        field = 0
        for bit in range(i, i + count):
            field = (field << 1) | ((word >> (63 - bit)) & 1 if bit < 64 else 0)
        self.image.deposit(at, count, field)
        self.printed[ext_unit] = ("EXT", at, count)
        self.running = at + count


def _literal(n):
    v = V()
    v.I = n
    return v


def addr_copy(p2, start, end):
    return p2.st.store_coded(p2.mem.get_str(start, end - start))
