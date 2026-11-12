"""pass1.py -- MAIN and its pseudo-operation routines, C22-6729 pp.14-27, 79-134.

One statement, one trip round the chart (AA-AE), one unit written.  Box numbers
in the comments are the chart's.

Not yet here, each refused loudly by the check at the end of the module's
tests: MIBA's and MBSPEC's corrections, the coprocessor, DUPLI, the relocation
pseudo-ops' effects.  A numeric DD keeps its text for OUTPUT, not Fig. 26's
double precision form: see mqdd().
"""
from .bits import BitMem
from .cards import Getcha
from .coded import encode, Expr
from .getfld import Getfld, FieldError, ALNUM
from . import optable
from .optable import lookup, ENTRIES, dds13, DEFAULT_BS, MODE_CODE
from .symtab import (SymbolTable, KIND_LABEL, KIND_SYN, KIND_UNDEF)
from .unit import *             # noqa: F401,F403
from .value import Value
from .dnum import Number, Dbl, Scan, store_entry

SECONDARY = set(optable._a.PROGRESSIVE_SECONDARY_OP) | set(optable._a.CW_SECONDARY) | {"SEOP"}
MODES = set(MODE_CODE)
SECONDARY_FIRST = {s[0] for s in SECONDARY}    # p.22's question character block


class Messages:
    """ERR's list, keyed by unit (pp.37-39), kept to print in Pass 2b."""

    def __init__(self):
        self.items = []
        self.fields = []

    def add(self, number, text, unit=0, fatal=True, field=0):
        """`text` is the host's detail, for StrapError; the listing prints the
        number's own message from errtab.  `field`, Fig. 3's 4-bit field
        number (p.38), is not yet counted by the passes: 0 (CHOSEN)."""
        self.items.append((number, text, unit, fatal))
        self.fields.append(field)


class Pass1:
    def __init__(self, cards):
        self.g = Getcha(cards)
        self.units = Units(BitMem())
        self.mem = self.units.mem
        self.st = SymbolTable()
        self.msg = Messages()
        self.val = Value(self.st, self.msg)
        self.tails = {}         # TAILOR: text -> number, p.125
        self.levels = [0] * 11  # 1..10
        self.getfld = Getfld(self.g, self._sysym, self._tail_on, self._sysym_changed)
        self.block_named = False
        self.first_of_block = True
        self.block_symbol_done = False
        self.check_digit = 0
        self.named_of = {}
        self.legal_old = {}     # MULTI's legal case: new vle -> the old one
        self.def_units = {}     # name -> the units that define it, in order

    def _sysym(self, name):
        return optable.system_symbol(name)

    def _sysym_changed(self, written, used):
        """C22-6729 p.75 box 41: MBSPEC altered a system symbol, error 129."""
        self.msg.add(129, f"SS ${written} CHANGED INTO ${used}", self.unit, fatal=False)

    # -- TAILOR, pp.74-75, 123-125 ------------------------------------------------
    def _tail_number(self, text):
        if text not in self.tails:
            self.tails[text] = len(self.tails) + 1
        return self.tails[text]

    def _tail_on(self, text, written=None):
        levels = list(self.levels)
        for k, t in enumerate(written or (), 1):
            levels[k] = self._tail_number(t) if t else 0
        n = max((i for i, v in enumerate(levels) if v), default=0)
        if not n:
            return text
        return text + "*" + "".join(_level_char(levels[i]) for i in range(1, n + 1))

    # -- the chart ----------------------------------------------------------------
    def run(self):
        g = self.g
        while True:
            unit = self._box2()
            if g.fblend:        # Boxes 3-4
                g.fblena, g.fblend = True, False
                self.first_of_block = True
                g.card = None
            g.bsyst = []
            c = g.next()        # Box 5
            if c is None:
                self._end_of_file(unit)
                return self
            ended = self._statement(unit, c)
            if ended:
                return self

    def _box2(self):
        """MAIN, initialize [19-20]: round Ibuffw, zero the fixed format."""
        unit = (self.units.ibuffw + 63) // 64 * 64
        for off in range(0, FIXED_BITS, 64):
            self.mem.put(unit + off, 64, 0)
        self.units.put(unit, ZIFALL, 1)
        self.getfld.radix = 0
        self.bcfldx = unit + FIXED_BITS
        self.unit = unit
        self.fields = 0
        self.entry_mode = None
        self.print_names = getattr(self, "print_names", {})
        self.ext2 = getattr(self, "ext_pending", False)
        self.ext_pending = False
        return unit

    def _statement(self, unit, c):
        g = self.g
        u = self.units
        u.put(unit, ZICDID, _card_id(g.card_id))
        if self.ext2:
            u.put(unit, ZIEXT2, 1)
        if c == "'":            # Box 7: a comment, first thing in the block
            return self._comment(unit, g.named and self.first_of_block)
        if c == ";":            # Boxes 9H-9G
            if not g.fblend and not self.first_of_block:
                return self._make_drz(unit)
            if g.fblend and not g.fblena:
                # A false ';': a real one already ended the block.  No unit.
                return False
            return self._comment(unit, g.named)
        if c == "$":            # p.25: suppress, before the instruction
            u.put(unit, ZISUPP, 1)
            c = g.next()
        if c == "(":            # Box 11
            self._entry_mode()
            c = g.ch
        # Boxes 12-15: the operation, up to eight characters.
        op = ""
        while c is not None and c not in ",;'(":
            op += c.upper()
            c = g.next()
        if len(op) > 8:
            return self._illegal(unit, op)
        self.op = op
        self.modifiers = []
        self.mode = None
        self.fl_expr = self.bs_expr = None
        self.pmode = None
        if op == "EXT":
            return self._mx(unit)
        while g.ch == "(":      # Boxes 24-26
            self._modifier(unit)
            g.next() if False else None
        mode = self.mode if self.mode in MODES else None
        entry = lookup(op, mode, tuple(self.modifiers))
        if entry is None:       # Box 17 not found: MIBA, then MBSPEC [22, 92-95]
            for test in optable.mbspec(op):
                entry = lookup(test, mode, tuple(self.modifiers))
                if entry is not None:
                    # p.93 box 10: a successful search with Llbts.8 on gives
                    # the error message.  N28-1081 p.13: only 1-18 are serious,
                    # so the assembly goes on with the changed op.
                    self.msg.add(129, f"OP {op} CHANGED INTO {test}", unit, fatal=False)
                    op = self.op = test
                    break
        if entry is None:
            return self._illegal(unit, op)
        u.put(unit, ZIOPX, entry.index)
        self._store_dds(unit)
        if entry.mcp:           # Boxes 30A-32 [23, 97]
            return self._miod(unit, entry)
        self.fiod = True        # "should not be any more MCP-type" [97]
        if entry.pseudo:
            return self._pseudo(unit, entry)
        # Box 34 MEA
        u.put(unit, ZILBO, entry.length)
        u.put(unit, ZIFBO, 1)
        u.put(unit, ZIFP2, 1)
        u.put(unit, ZIOTPT, entry.skeleton)
        self._collect_fields(unit, entry)
        return self._wind_up(unit, entry)

    # -- Box 11, the entry mode [21] ---------------------------------------------
    def _entry_mode(self):
        g = self.g
        text = ""
        g.gcaz = True
        c = g.next()
        while c is not None and (c != ")" or not text):
            text += c
            c = g.next()
        g.gcaz = False
        g.next()
        self.entry_mode = text

    # -- Boxes 24-26: secondary op, or dds ---------------------------------------
    def _modifier(self, unit):
        g = self.g
        g.next()
        tok = ""
        while g.ch is not None and g.ch not in ",)":
            tok += g.ch.upper()
            g.next()
        if tok[:1] in SECONDARY_FIRST and tok not in SECONDARY and tok not in MODES:
            # Boxes 24-26 [22]: when "the character after the ( is one of ...
            # the legal first characters for a secondary op", MAIN looks the
            # rest up in the secondary op table: "Once again MBSPEC may be
            # called upon to help."  Altered: error 129 (p.178, OP OR SS).
            for test in optable.mbspec(tok):
                if test in SECONDARY:
                    self.msg.add(129, f"SECONDARY OP {tok} CHANGED INTO {test}", unit, fatal=False)
                    tok = test
                    break
        if tok in SECONDARY or (self.op == "CW" and tok):
            self.modifiers.append(tok)
            if g.ch != ")":
                raise FieldError(33, "NOT CLOSED BY PAREN")
            g.next()
            return
        if tok == "P":          # p.23: P-mode, a symbol's dds taken over
            x = self.getfld.field()
            self.pmode = encode(x)
            if g.ch != ")":
                raise FieldError(33, "NOT CLOSED BY PAREN")
            g.next()
            return
        if tok and tok not in MODES:
            raise FieldError(91, f"MODE {tok}")
        self.mode = tok or None
        if g.ch == ",":
            x = self.getfld.field()
            if not x.null:
                self.fl_expr = x
            if g.ch == ",":
                x = self.getfld.field()
                if not x.null:
                    self.bs_expr = x
        if g.ch != ")":
            raise FieldError(33, "NOT CLOSED BY PAREN")
        g.next()

    def _store_dds(self, unit):
        """p.23: VALUE each dds expression now if it can be done, else keep it
        first in the coded area and leave the symbolic indicator on."""
        u = self.units
        if self.mode is None and self.fl_expr is None and self.bs_expr is None and not self.pmode:
            return
        fl, bs = 0, None
        for which, x in (("fl", self.fl_expr), ("bs", self.bs_expr)):
            if x is None:
                continue
            s = encode(x)
            self.mem.put_str(self.bcfldx, s)
            v = self.val.read_field(self.mem, self.bcfldx)
            if v.avail and not v.gps:
                if v.B:
                    # C22-6729 p.176, MAIN's message 38, "BIT STYLE NO. IN
                    # DDS"; p.137 boxes 20, 29: "(Bit and integer values are
                    # combined.)" -- the combined value is used.
                    self.msg.add(38, "BIT STYLE NO. IN DDS", unit, fatal=False)
                if which == "fl":
                    fl = v.total
                    if fl > 64:
                        # C22-6729 p.176: MAIN's message 36, "FIELD LENGTH
                        # GREATER THAN 64"; p.137 box 20, the same test for a
                        # symbolic one: "an error message to be given and the
                        # field length to be truncated".  READ: truncated as
                        # C28-6129 p.33 uses the word, the high-order bits
                        # dropped from the dds's six-bit field (0 for 64), so
                        # 72 is 8.  The width is not printed for this case.
                        self.msg.add(36, "FIELD LENGTH GREATER THAN 64", unit, fatal=False)
                        fl &= 63
                    u.put(unit, ZIFFLF, 1)
                else:
                    bs = v.total
                    cc = (self.entry_mode or "").strip().upper()[:2] == "CC"
                    # C28-6129 p.30: "If the byte size is omitted in entry mode
                    # CC, BS = 12 is implied" -- the card code's twelve rows,
                    # so 12 is a byte size CC takes (MCP pp.2, 15, 99, 256 ...
                    # write (CC*)DD(BU,,12)).  READ: message 37 is for others.
                    if bs > (12 if cc else 8):
                        # p.176, message 37, "BYTE SIZE GREATER THAN 8"; p.137
                        # box 29: "an error message and the byte size to be
                        # truncated".  UNSPECIFIED: to what -- 9 to 15 fit the
                        # dds's four-bit field (Fig. 29 p.201, 8 as 1000), so
                        # the field does not decide it.  Pass 2 refuses the
                        # deck (pass2.run).
                        self.msg.add(37, "BYTE SIZE GREATER THAN 8", unit, fatal=False)
                    u.put(unit, ZIFBSF, 1)
            else:
                self.bcfldx += len(s)
                u.put(unit, ZIFSFL if which == "fl" else ZIFSBS, 1)
        mode = self.mode or "BU"
        if bs is None:
            bs = DEFAULT_BS[mode]
        u.put(unit, ZIDDS, dds13(mode, fl, bs))
        self.raw_fl = fl
        u.put(unit, ZIFDSF, 1)
        if self.mode is not None or self.fl_expr is not None or self.bs_expr is not None:
            u.put(unit, ZIFDDS, 1)
        if self.pmode:
            u.put(unit, ZIFPMN, 1)
            u.put(unit, ZILPMS, len(self.pmode))
            self.mem.put_str(self.bcfldx, self.pmode)
            self.bcfldx += len(self.pmode)

    # -- Boxes 35-37: the address fields -----------------------------------------
    def _collect_fields(self, unit, entry):
        g = self.g
        u = self.units
        limit = sum(n for _r, n in entry.fills)
        n = 0
        while g.ch == ",":
            x = self.getfld.field()
            s = encode(x)
            self.mem.put_str(self.bcfldx, s)
            self.bcfldx += len(s)
            n += 1
            if n > limit:
                raise FieldError(40, "EXTRA FIELDS")
        u.put(unit, ZINFLD, n)
        u.put(unit, ZIFALL, 0)

    # -- Box 38 onward: the wind-up ----------------------------------------------
    def _wind_up(self, unit, entry):
        g = self.g
        u = self.units
        while g.ch is not None and g.ch != ";":     # Box 38 MEDAF
            g.next()
        if g.ch is None:
            g.ch = ";"
            g.fblend = True
        end_coded = self.bcfldx
        # Box 39-44: the print image at a full word.
        text = "".join(g.bsyst).rstrip()
        if text.endswith(";"):
            text = text[:-1].rstrip()
        u.put(unit, ZILCFD, end_coded - unit - FIXED_BITS)
        start = (end_coded + 63) // 64 * 64
        image_at = start
        for k, ch in enumerate(text):
            self.mem.put(start + 8 * k, 8, ord(ch) & 255)
        u.put(unit, ZILSST, len(text))
        end = start + 8 * len(text)
        # Boxes 40-49
        if self.first_of_block and g.named:
            u.put(unit, ZIFNME, 1)
            self.check_digit = (self.check_digit + 1) % 10
            u.put(unit, ZINAME, self.check_digit)
            self.print_names[unit] = (g.name, self._tail_on(g.symbol))
            self._form_symbol(unit, entry)
        self.first_of_block = False
        u.intout(unit, end)     # Box 57
        self.image_at = image_at
        return entry.name in ("END", "FEND")     # FEND: N28-1081 page 3

    def _form_symbol(self, unit, entry):
        """Boxes 45-53.  CHOSEN: entered here, on the block's first unit.  The
        chart waits for the last unit, which nothing downstream can tell."""
        g = self.g
        st = self.st
        u = self.units
        name = self._tail_on(g.symbol)
        kind = KIND_SYN if entry.name in ("SYN", "IOD") else KIND_LABEL
        f, there = st.addord(name, kind)
        if there:
            f = self._multi(name, f, unit, kind)
        self.def_units.setdefault(name, []).append(unit)
        st.put(f, "ZKIND", kind)
        st.put(f, "ZST1", 0)
        st.put(f, "ZSTCNT", self.check_digit)
        if kind == KIND_SYN:
            st.put(f, "ZEXPR", self.syn_expr)
        self.named_of[unit] = f
        u.put(unit, ZIADSY, 0)
        # Box 49: what carries over from unit to entry [13, 25].
        if u.get(unit, ZIFDSF):
            st.put(f, "ZDDS", u.get(unit, ZIDDS))
            st.put(f, "ZST3", 1)
            p = unit + FIXED_BITS
            if u.get(unit, ZIFSFL):
                v = self.val.read_field(self.mem, p)
                st.put(f, "ZFLX", self._copy_coded(p, v.next))
                p = v.next
            if u.get(unit, ZIFSBS):
                v = self.val.read_field(self.mem, p)
                st.put(f, "ZBSX", self._copy_coded(p, v.next))
        elif entry.name in optable.FIXED_DATA:
            # strap_asm._INDEX_WORD_DDS, from C28-6129 p.18 ff.
            d = {"XW": dds13("BU", 0, 8), "VF": dds13("B", 25, 1),
                 "CF": dds13("BU", 18, 8), "RF": dds13("BU", 18, 8)}.get(entry.name)
            if d is not None:
                st.put(f, "ZDDS", d)
                st.put(f, "ZST3", 1)
        elif entry.kind in ("instr", "fp", "vfl", "conn", "io"):
            st.put(f, "ZDDS", dds13("BU", entry.length, 8))
            st.put(f, "ZST3", 1)
        old = self.legal_old.get(f)
        if old and st.get(old, "ZST3"):
            # Chart RE boxes 14, 16: an earlier dds cannot be overruled (p.127).
            for k in ("ZDDS", "ZFLX", "ZBSX", "ZST3"):
                st.put(f, k, st.get(old, k))

    def _copy_coded(self, start, end):
        s = self.mem.get_str(start, end - start)
        return self.st.store_coded(s)

    def _multi(self, name, f, unit, kind):
        """MULTI, chart RE p.126 and text p.127.  Legal only when the new and the
        old definitions are both SYN (boxes 1, 12) with equal values (box 13):
        then a new vle, the dictionary repointed, and the old dds and index
        holding (boxes 14-23).  Otherwise contradictory: a basic vle for this
        definition, the dictionary unchanged, so the first stands (box 2-3).

        CHOSEN: both vles carry the mark, so a reference finds it whichever the
        dictionary holds, and NUNDSY names the symbol once.  Box 13 runs in Pass
        1, where a value may not be known yet: the values are equal when the
        two coded expressions are the same, or when both are known and their
        bit addresses agree (p.127's A SYN,32.0 and A SYN(BU,32),32.0($2))."""
        st = self.st
        if st.get(f, "ZKIND") == KIND_UNDEF:
            return f
        if kind == KIND_SYN and st.get(f, "ZKIND") == KIND_SYN and self._values_equal(f):
            nf = st.replace(name, KIND_SYN)
            st.put(nf, "ZST22", 1)
            st.put(f, "ZST22", 1)
            st.put(nf, "ZOLDF", f)
            self.legal_old[nf] = f
            return nf
        st.put(f, "ZST23", 1)
        nf = st.orphan(name, kind)
        st.put(nf, "ZST23", 1)
        return nf

    def _values_equal(self, old):
        st = self.st
        a, b = st.get(old, "ZEXPR"), self.syn_expr
        if not a or not b:
            return False
        saved = self.val.flags
        va = self.val.read_field(st.mem, a)
        vb = self.val.read_field(st.mem, b)
        self.val.flags = saved
        if st.mem.get_str(a, va.next - a) == st.mem.get_str(b, vb.next - b):
            return True
        return va.avail and vb.avail and va.total == vb.total

    # -- Boxes 9H, 7: comment and DRZ(N),1 --------------------------------------
    def _comment(self, unit, named):
        g = self.g
        while g.ch is not None and g.ch != ";":
            g.next()
        if named:
            return self._make_drz(unit)
        e = lookup("PRNOR")     # the comment unit: prints, does nothing
        self.units.put(unit, ZIOPX, e.index)
        self.units.put(unit, ZIFALL, 1)
        self.op = "COMMENT"
        return self._wind_up(unit, e)

    def _make_drz(self, unit):
        """p.21: a name on nothing is DRZ(N),1 for the unit."""
        g = self.g
        e = lookup("DRZ")
        self.units.put(unit, ZIOPX, e.index)
        self.units.put(unit, ZIDDS, dds13("N", 0, 4))
        self.units.put(unit, ZIFDSF, 1)
        self.units.put(unit, ZIFDDS, 1)
        self.units.put(unit, ZIFP2, 1)
        self.units.put(unit, ZIFBO, 1)
        s = encode(_abs_field(1))
        self.mem.put_str(self.bcfldx, s)
        self.bcfldx += len(s)
        self.units.put(unit, ZINFLD, 1)
        self.units.put(unit, ZIFALL, 0)
        self.op = "DRZ"
        return self._wind_up(unit, e)

    def _illegal(self, unit, op):
        """Boxes 19-22: the unit becomes SIC,$15; BE,0 and the error is given.
        CHOSEN: the host keeps the message and stops the deck being used."""
        self.msg.add(1, f"ILLEGAL OP CODE {op}", unit)
        e = lookup("PRNOR")
        self.units.put(unit, ZIOPX, e.index)
        self.op = "COMMENT"
        return self._wind_up(unit, e)

    # -- Box 63 ff., the pseudo-operations [26-27] -------------------------------
    def _miod(self, unit, e):
        """MIOD [96-97].  The type field is spaced over, erased as p.97 says;
        for an IOD the exit address is encoded; the reference number goes in
        Zilpms; and the name goes in the symbol table.  Zifp2 off, Zifall on, so
        that NMCP and not DECODE has the unit, as the text says; charts 11 and
        14 print the opposite, and p.97's reason decides.

        DERIVED: the name's value is the reference number as a word address.
        C22-6678-1 p.48 line 11 prints ",RON" as 000001.00 80 for the first IOD.
        No page says it; that is the one print."""
        g = self.g
        u = self.units
        if getattr(self, "fiod", False):
            self.msg.add(102, "ILLEGAL SEQ. OF MCP CARDS", unit, fatal=False)
        u.put(unit, ZIFP2, 0)
        u.put(unit, ZIFALL, 1)
        if e.name == "REEL":
            if g.named:
                self.msg.add(105, "REEL CARD DOESNT NEED NAME", unit, fatal=False)
            return self._wind_up(unit, e)
        if not g.named:
            self.msg.add(103, "IOD CARD SHOULD HAVE NAME", unit)
        n = 0
        if g.ch == ",":
            self.getfld.field()     # the type, encoded and not kept
        if g.ch == ",":
            x = self.getfld.field()
            if not x.null:
                s = encode(x)
                self.mem.put_str(self.bcfldx, s)
                self.bcfldx += len(s)
                n = 1
            else:
                self.msg.add(143, "EXIT ADDR IS NULL", unit, fatal=False)
        else:
            self.msg.add(104, "I/O TBL OF EXITS ADDR NULL", unit, fatal=False)
        u.put(unit, ZINFLD, n)
        self.iod_refs = getattr(self, "iod_refs", 0) + 1
        u.put(unit, ZILPMS, self.iod_refs)
        self.syn_expr = self.st.store_coded(encode(_word_field(self.iod_refs)))
        return self._wind_up(unit, e)

    def _pseudo(self, unit, e):
        u = self.units
        name = e.name
        if name in ("DD", "DDI"):
            self._mqdd(unit, e)
        elif name in ("DR", "DRZ"):
            self._mqr(unit, e)
        elif name == "SYN":
            self._mqs(unit, e)
        elif name in ("SLC", "SLCR", "END", "TLB", "ORIGIN", "PUNFPC", "ENTER",
                      "COMBLOCK", "SLCRCOM"):
            self._mql(unit, e)
        elif name == "PUNID":
            self._mpunid(unit)
        elif name == "TAIL":
            self._mqtail(unit)
        elif name == "UNTAIL":
            self._mqt(unit)
        elif name == "CNOP":
            u.put(unit, ZIFP2, 0)
        elif name == "LINK":
            self._mqlink(unit)
            return self._wind_up(unit, ENTRIES[u.get(unit, ZIOPX)])
        return self._wind_up(unit, e)

    def _mpunid(self, unit):
        """MPUNID (C22-6729 p.27): the ID's characters from GETCHA with Gcaz on,
        blanks significant, padded with blanks to eight, kept in the unit's work
        area with Ziotpt's value field pointing at them for OUTPUT.  C28-6129
        p.13 (PDF 17): "the first 8 characters following the comma".  No comma:
        message 55.  CHOSEN: characters past the eighth are dropped."""
        g = self.g
        u = self.units
        if g.ch != ",":
            self.msg.add(55, "NO COMMA AFTER PUNID", unit, fatal=False)
            return
        g.gcaz = True
        text = ""
        c = g.next()
        while c is not None and c != ";":
            text += c
            c = g.next()
        g.gcaz = False
        ident = text[:8].ljust(8)
        p = self.bcfldx
        for k, ch in enumerate(ident):
            self.mem.put(p + 8 * k, 8, ord(ch) & 255)
        self.bcfldx += 64
        u.put(unit, ZIOTPT, p)

    def _one_field(self, unit, nogp=False):
        g = self.g
        n = 0
        while g.ch == ",":
            x = self.getfld.field(nogp=nogp)
            s = encode(x)
            self.mem.put_str(self.bcfldx, s)
            self.bcfldx += len(s)
            n += 1
        self.units.put(unit, ZINFLD, n)
        return n

    def _mql(self, unit, e):
        """MQL: Pass 2 indicators, and the field encoded [27]."""
        self._one_field(unit, nogp=True)
        self.units.put(unit, ZIFALL, 0)

    def _mqr(self, unit, e):
        """MQR, MDIMRF [116-120]: null dds gets N,64,4, error 46 (p.27)."""
        u = self.units
        g = self.g
        if not u.get(unit, ZIFDSF):
            u.put(unit, ZIDDS, dds13("N", 0, 4))
            u.put(unit, ZIFDSF, 1)
        u.put(unit, ZIFBO, 1)
        u.put(unit, ZIFP2, 1)
        u.put(unit, ZIFALL, 0)
        n = 0
        if g.ch == ",":
            g.next()
            parens = g.ch == "(" and self._dim_parens()
            have = True
            if parens:
                g.next()
            while True:
                x = self.getfld.field(nogp=True, have_first=have)
                have = False
                s = encode(x)
                self.mem.put_str(self.bcfldx, s)
                self.bcfldx += len(s)
                n += 1
                if not (parens and g.ch == ","):
                    break
            if parens:
                if g.ch != ")":
                    raise FieldError(54, "DIMENSION NOT CLOSED")
                g.next()
        u.put(unit, ZINFLD, n)

    def _dim_parens(self):
        """Is this '(' the whole dimension list, closed at the field's end?  A
        field like (A+1)*2 is an expression, and (8)10 a radix."""
        g = self.g
        card, col, depth = g.card, g.col, 1
        while card is not None and col < 72:
            c = card[col]
            col += 1
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    break
        while card is not None and col < 72 and card[col] == " ":
            col += 1
        return card is not None and (col >= 72 or card[col] in ",;'")

    def _mqs(self, unit, e):
        """MQS [121-122]: the dds and the address go to the symbol's vle."""
        g = self.g
        u = self.units
        self.syn_expr = 0
        if not g.named:
            self.msg.add(43, "SYN HAS NO NAME", unit)
        if g.ch == ",":
            x = self.getfld.field(nogp=True)
            self.syn_expr = self.st.store_coded(encode(x))
        else:
            self.msg.add(44, "SYN HAS NO ADDRESS", unit)
            self.syn_expr = self.st.store_coded(encode(_abs_field(0)))
        u.put(unit, ZIFP2, 0)
        u.put(unit, ZIFALL, 0)

    def _mqdd(self, unit, e):
        """MQDD, MQDALF [98-103].

        An alphabetic DD is converted here, as p.102 says, and a numeric DD to
        Fig. 26's double precision form, as p.26 says.
        """
        g = self.g
        u = self.units
        u.put(unit, ZIFP2, 1)
        u.put(unit, ZIFBO, 1)
        u.put(unit, ZIFDD, 1)
        u.put(unit, ZIFALL, 0)
        if not u.get(unit, ZIFDSF):
            mode = "BU" if self._is_alpha() else "N"
            u.put(unit, ZIDDS, dds13(mode, 0, DEFAULT_BS[mode]))
            u.put(unit, ZIFDSF, 1)
            if not self._is_alpha():
                self.msg.add(42, "STRAP ASSIGNED DDS", unit, fatal=False)
        u.put(unit, DD_LOC, self.bcfldx // 1)
        if self._is_alpha():
            self._mqdalf(unit)
        else:
            self._numeric(unit)

    def _is_alpha(self):
        m = self.entry_mode
        return bool(m) and not m.strip().isdigit() and m[:-1].strip().upper() in ("A", "IQS", "CC", "P")

    def _mqdalf(self, unit):
        g = self.g
        u = self.units
        mode = self.entry_mode[:-1].strip().upper()
        term = self.entry_mode[-1]
        if g.ch != ",":
            raise FieldError(84, "ALPHABETIC DD HAS NO FIELD")
        g.gcaz = True
        text = ""
        c = g.next()
        while c is not None and c != term:
            if g.fblend and c == ";":
                break
            text += c
            c = g.next()
        g.gcaz = False
        if c == term:
            g.next()
        else:
            raise FieldError(85, "ENTRY-MODE DATUM NOT TERMINATED")
        # Text in A8 or CC is 8 or 12 bits a character; kept as ASCII host codes
        # until OUTPUT converts it by the mode's table (charsets.py).
        p = self.bcfldx
        for ch in text:
            self.mem.put(p, 8, ord(ch) & 255)
            p += 8
        self.bcfldx = p
        u.put(unit, ZINFLD, len(text))
        u.put(unit, ZILPMS, len(text))
        self.alpha_mode = mode
        u.put(unit, DD_CC, 1 if mode == "CC" else 0)
        u.put(unit, ZIOTPT, u.get(unit, ZIOTPT) | _mode_tag(mode))
        u.put(unit, DD_LOC, (self.bcfldx - 8 * len(text)))

    def _numeric(self, unit):
        """MQDD's loop [98-100], MQDNUM and DNUM (dnum.py): each field to Fig. 26."""
        g = self.g
        u = self.units
        u.put(unit, DD_NUMERIC, 1)
        op_fn, op_radix = self._op_entry()
        p = self.bcfldx
        u.put(unit, DD_LOC, p)
        n = 0
        while True:
            if g.ch == ",":
                g.next()
            elif n:
                break
            n += 1
            p = self._numeric_field(p, op_fn, op_radix, g.ch == ",")
            if g.ch == ",":
                self.mem.put(p - 1, 1, 1)       # e: the format repeats
            elif g.ch is not None and g.ch not in ";'":
                raise FieldError(67, f"INAPPROPRIATE CHARACTER {g.ch!r} IN A DD")
            else:
                break
        self.bcfldx = p
        u.put(unit, ZINFLD, n)

    def _op_entry(self):
        m = (self.entry_mode or "").strip().upper()
        if not m:
            return None, 0
        if m[0] == "F" and m[1:].isdigit():
            return int(m[1:]), 0
        if m.isdigit():
            return None, int(m)
        raise FieldError(45, f"ENTRY MODE {m} ON A NUMERIC DD")

    def _numeric_field(self, p, fn, radix, _more):
        """Boxes 6-29: entry mode, number, S and X in either order, then g.p."""
        g = self.g
        gf = self.getfld
        chain = Expr()
        chain.null = True
        if g.ch == "(" and not gf._peek_gp():
            # 14 MQDEMB: a field's own entry mode overrules the operation's.
            got = self._field_entry()
            if got is not None:
                fn, radix = got
        value = Number(Dbl())
        if g.ch is not None and g.ch not in ",;'(":
            value = Scan(g, radix).expression()
        elif g.ch == "(" and not gf._peek_gp():
            value = Scan(g, radix).expression()
        sbits = xexp = None
        while g.ch is not None and g.ch.upper() in ("S", "X"):
            if g.ch.upper() == "S":
                g.next()
                v = 0
                while g.ch is not None and g.ch in "01234567":
                    v = v * 8 + int(g.ch)
                    g.next()
                # p.27: inserted by a logical OR.
                sbits = (sbits or 0) | v
            else:
                g.next()
                x = Scan(g, 10)._unary()
                xexp = int(x.v.exact())
        gf.gp_radix = radix
        gf.gp_chain(chain)
        gf.gp_radix = 0
        # encode(): "1111 0" for the null head, then the chain with its final 0.
        bits = encode(chain)[5:]
        return store_entry(self.mem, p, fn, value, sbits, xexp, bits, False)

    def _field_entry(self):
        """'(F7)' or '(8)': the entry mode, or None if this parenthesis opens an
        expression.  Decided by looking ahead, as GETFLD's radix prefix is."""
        g = self.g
        card, col = g.card, g.col
        text = ""
        while card is not None and col < 72 and card[col] != ")":
            text += card[col]
            col += 1
        t = text.replace(" ", "").upper()
        fn = None
        radix = 0
        if t[:1] == "F" and t[1:].isdigit():
            fn = int(t[1:])
        elif t.isdigit():
            radix = int(t)
        else:
            return None
        while g.ch != ")":
            g.next()
        g.next()
        return fn, radix

    def _mx(self, unit):
        """MX [128-129]: three fields L, LP, N with no g.p., ZIFP2 on, ZIFALL off.
        Printed both as EXT(I,J,N) and EXT,(I,J,N) (strap_asm._ext_params)."""
        g = self.g
        u = self.units
        e = lookup("EXT")
        u.put(unit, ZIOPX, e.index)
        u.put(unit, ZIFP2, 1)
        u.put(unit, ZIFALL, 0)
        u.put(unit, ZIFBO, 1)
        if g.ch == ",":
            g.next()
        if g.ch != "(":
            raise FieldError(107, "EXT HAS NO PARAMETERS")
        n = 0
        while True:
            x = self.getfld.field(nogp=True)
            s = encode(x)
            self.mem.put_str(self.bcfldx, s)
            self.bcfldx += len(s)
            n += 1
            if g.ch != ",":
                break
        if g.ch != ")":
            raise FieldError(107, "EXT NOT CLOSED")
        g.next()
        u.put(unit, ZINFLD, n)
        self.ext_pending = True
        return self._wind_up(unit, e)

    def _mqlink(self, unit):
        """MQLINK [32]: the unit becomes LVI,15,$+2."""
        u = self.units
        e = lookup("LVI")
        u.put(unit, ZIOPX, e.index)
        u.put(unit, ZILBO, e.length)
        u.put(unit, ZIFBO, 1)
        u.put(unit, ZIFP2, 1)
        u.put(unit, ZIFALL, 0)
        u.put(unit, ZIOTPT, e.skeleton)
        g2 = Getcha([(" " * 9 + ",15,$+2").ljust(72)])
        g2.next()
        keep = self.getfld.g
        self.getfld.g = g2
        n = 0
        while g2.ch == ",":
            s = encode(self.getfld.field())
            self.mem.put_str(self.bcfldx, s)
            self.bcfldx += len(s)
            n += 1
        self.getfld.g = keep
        u.put(unit, ZINFLD, n)

    # -- TAIL and UNTAIL [123-125] ----------------------------------------------
    def _mqtail(self, unit):
        g = self.g
        level = 1
        c = g.next() if g.ch == "," else g.ch
        if c == "(":
            digits = ""
            c = g.next()
            while c is not None and c in "0123456789":
                digits += c
                c = g.next()
            if c != ")":
                raise FieldError(61, "TAIL LEVEL NOT CLOSED")
            c = g.next()
            level = int(digits or "1")
        text = ""
        while c is not None and c in ALNUM:
            text += c.upper()
            c = g.next()
        if not text:
            self.msg.add(59, "TAIL HAS NO SYMBOL", unit)
            return
        self.levels[min(level, 10)] = self._tail_number(text)

    def _mqt(self, unit):
        g = self.g
        c = g.next() if g.ch == "," else g.ch
        level = 1
        if c == "(":
            digits = ""
            c = g.next()
            while c is not None and c in "0123456789":
                digits += c
                c = g.next()
            level = int(digits or "1")
            if c == ")":
                g.next()
        if level == 10:
            self.levels = [0] * 11
        elif level == 9:
            for i in range(1, 10):
                self.levels[i] = 0
        else:
            self.levels[level % 8 or 8] = 0

    def _end_of_file(self, unit):
        """No END card.  STRAP II needs one; decks in this project may stop."""
        self.no_end = True


def _level_char(n):
    return "%02d" % n


def _mode_tag(mode):
    return {"A": 0, "IQS": 1, "CC": 2, "P": 3}[mode]


def _abs_field(n):
    from .coded import Datum
    x = Expr()
    x.data.append(Datum("abs", n))
    return x


def _word_field(n):
    """n., a word address, as GETFLD codes it (Box 58)."""
    x = _abs_field(n)
    x.ops.append((".L", 1))
    return x


def _card_id(text):
    v = 0
    for ch in (text or "").ljust(8)[:8]:
        v = (v << 8) | (ord(ch) & 255)
    return v
