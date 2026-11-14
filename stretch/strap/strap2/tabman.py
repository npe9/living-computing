"""tabman.py -- TABMAN, the table management routines, C22-6729 pp.40-53.

>>> A RECONSTRUCTION to the guide's text and charts (Charts RA p.43, RB p.50,
>>> RW p.52; MOVE pp.40-42), read in the ink 2026-11-13.  The host's symbol
>>> table does not use it yet (docs/strap2_7030.md step 3c); this is the
>>> specification the 7030 TABMAN (step 3b) is tested against. <<<

Storage is a BitMem, so every field is at the bit address the guide gives.

The control block (Fig. 8 p.44, the table on p.45), four words at cb:
  FX 0.0 (64) and DX 1.0 (64), index words; their value fields (bits 0-23)
  hold the function and dictionary locations.  FW 2.0 (24) first entry,
  ID 2.25 (6), LW 2.32 (24) last entry, TO 2.57 (1, 1 unordered),
  TM 2.58 (1), TEC 2.62 (1), EL 3.0 (16), AL 3.16 (16), ADDL 3.32 (16),
  N 3.48 (16) undeleted entries.

The universal control block (p.45), four half words at ucb:
  Auvtab 0.0 (24) the vle table's next free bit (built upwards),
  Auvbot 0.32 (24) its lowest usable bit, Autcb 1.0 (18) the first control
  block, Aunt 1.32 (18) the number of control blocks.
  CHOSEN: the four in that order, each in its own half word (p.45 gives
  "24 of half word", "18 of half word").  CHOSEN: Auvtab holds the address
  itself (p.45: "Word addressed contains first available bit location").

An entry (Fig. 21 p.190): bit 0 deleted, bit 1 a vle exists, the argument
(AL bits), the function (ADDL bits).
  CHOSEN: EL = 2 + AL + ADDL rounded up to a half word, since FW and LW are
  half-word addresses (p.45).
  The vle is TABMAN's (p.44): when the function is longer than ADDL, it goes
  to a vle at Auvtab with Fig. 22's head (deleted, 13-bit length, the
  table's ID in A6, a 12-bit remainder length of 0), and the dictionary's
  function field holds the vle's signed address, with the vle bit 1.  Agetv:
  the function address is the vle's address + 32 (no remainder).  An
  argument split into a vle remainder (p.44's third form, the symbol
  table's) is step 3c's, and is refused here.

The compare (Box 4 Acompi: "sets the field length ... for the size of the
argument"): the first al bits of the table's argument against the given
al bits, unsigned.  TEC is Fig. 8's "type of compare", meaning UNSPECIFIED:
TEC 0 is this compare, TEC 1 is refused (fail loud).

The exits are named, and EXITS gives each one's location relative to the
calling sequence's first parameter (tbl), where $15 points on entry
(LVI,15,$+2).  The exit itself is B,-1($15), one half word back (p.46).
  SEARCH (p.47): found +2.32, so normal at 2.0; not found +2.0, so 1.32.
  ADDUNO (p.49): +3.0, so normal at 2.32.
  ADDORD (p.48): already there +2.32+0.32 (Boxes 14, 32-33), so 2.32.
    CHOSEN (Gap 11, docs/strap2/pass2.md): Box 9's +3.32 would exit at
    3.0, the error exit, where p.46 Boxes 8-9 and p.48 say normal.  The
    text is followed: normal at 3.32.  An unordered table: ADDUNO adds the
    entry at the end and the error exit (3.0) is taken (p.48).
  ANEXT (p.51): normal at 1.32; no more vle at 0.32 (two half words).
  RSERCH (p.53, no linkage printed): not found +1.32, so 1.0; found +2.0,
    so 1.32.  CHOSEN linkage: tbl, then the given address (I).

SEARCH's not-found index words (p.47): an ordered table gives the location
of the entry with the next higher argument (after the table if none), an
unordered one the location after the table.  CHOSEN: both FX and DX hold
that location.  The search stops at the first equal argument, and Box 11
then asks whether it is deleted: a deleted one is a miss, though a later
undeleted equal argument may stand after it.  An ordered table's search,
linear or binary (p.45 Box 7) alike, finds the first entry not below the
argument; a miss leaves the index words there, so ADDORD puts a new entry
before a deleted equal one (CHOSEN: p.47 says only "the next higher").  An
unordered table's linear search finds the first equal argument.
"""
from .bits import BitMem

# bit offsets from tbl: n.32 is n*64 + 32
EXITS = {
    ("SEARCH", "found"): 128, ("SEARCH", "not found"): 96,
    ("ADDUNO", "normal"): 160,
    ("ADDORD", "already there"): 160, ("ADDORD", "error"): 192,
    ("ADDORD", "normal"): 224,
    ("ANEXT", "normal"): 96, ("ANEXT", "no more"): 32,
    ("RSERCH", "not found"): 64, ("RSERCH", "found"): 96,
}


class TabmanError(Exception):
    pass


def _cb(cb, field):
    """Fig. 8's fields: (bit offset from cb, width)."""
    return {"FX": (0, 64), "DX": (64, 64), "FW": (128, 24), "ID": (153, 6),
            "LW": (160, 24), "TO": (185, 1), "TM": (186, 1), "TEC": (190, 1),
            "EL": (192, 16), "AL": (208, 16), "ADDL": (224, 16),
            "N": (240, 16)}[field]


class Tabman:
    def __init__(self, mem, ucb):
        self.mem = mem
        self.ucb = ucb
        self.afirst = True      # ANEXT's Afirst (p.51)
        self.anexta = 0         # ANEXT's next vle
        self.anextx = 0         # ANEXT's answer

    # -- the blocks ------------------------------------------------------------
    def get(self, cb, f):
        off, w = _cb(cb, f)
        return self.mem.get(cb + off, w)

    def put(self, cb, f, v):
        off, w = _cb(cb, f)
        self.mem.put(cb + off, w, v)

    def index(self, cb, f, value):
        """An index word's value field (bits 0-23)."""
        self.mem.put(cb + _cb(cb, f)[0], 24, value)

    @property
    def auvtab(self):
        return self.mem.get(self.ucb, 24)

    @auvtab.setter
    def auvtab(self, v):
        self.mem.put(self.ucb, 24, v)

    @property
    def auvbot(self):
        return self.mem.get(self.ucb + 32, 24)

    def define(self, cb, fw, ident, al, addl, ordered=True):
        """A new, empty table.  EL is filled in here (p.45: "filled by
        subroutine").  CHOSEN: an empty table's LW is FW - EL, so the next
        entry goes at LW + EL = FW."""
        for w in range(4):
            self.mem.put(cb + 64 * w, 64, 0)
        el = -(-(2 + al + addl) // 32) * 32
        self.put(cb, "FW", fw)
        self.put(cb, "ID", ident)
        self.put(cb, "LW", fw - el)
        self.put(cb, "TO", 0 if ordered else 1)
        self.put(cb, "EL", el)
        self.put(cb, "AL", al)
        self.put(cb, "ADDL", addl)

    def define_universal(self, bottom, tcb=0, nt=0):
        self.mem.put(self.ucb, 24, bottom)
        self.mem.put(self.ucb + 32, 24, bottom)
        self.mem.put(self.ucb + 64, 18, tcb)
        self.mem.put(self.ucb + 96, 18, nt)

    # -- entries ---------------------------------------------------------------
    def entries(self, cb):
        """Every entry location, deleted ones included, FW to LW."""
        el = self.get(cb, "EL")
        return list(range(self.get(cb, "FW"), self.get(cb, "LW") + 1, el))

    def deleted(self, e):
        return self.mem.get(e, 1) == 1

    def delete(self, cb, e):
        """Not a TABMAN routine: callers set the delete bit (Fig. 21) and N
        counts undeleted entries (p.45)."""
        if not self.deleted(e):
            self.mem.put(e, 1, 1)
            self.put(cb, "N", self.get(cb, "N") - 1)

    def argument(self, cb, e, al):
        return self.mem.get(e + 2, al)

    def function_address(self, cb, e):
        """Boxes 20-25: Agetv for a vle, else the function field."""
        al = self.get(cb, "AL")
        if self.mem.get(e + 1, 1):
            return self.mem.get_signed(e + 2 + al, self.get(cb, "ADDL")) + 32
        return e + 2 + al

    def _compare_setup(self, cb, al):
        if self.get(cb, "TEC"):
            raise TabmanError("TEC 1: a type of compare the guide does not describe")
        if al > self.get(cb, "AL"):
            raise TabmanError("an argument split into a vle (p.44's third form) is step 3c's")

    # -- SEARCH (p.47) ---------------------------------------------------------
    def search(self, cb, arg, al):
        self._compare_setup(cb, al)
        ordered = self.get(cb, "TO") == 0
        after = self.get(cb, "LW") + self.get(cb, "EL")
        if ordered:
            # the first entry not below the argument, by a linear or a
            # binary search alike (Box 7)
            at = next((e for e in self.entries(cb)
                       if self.argument(cb, e, al) >= arg), None)
            hit = at is not None and self.argument(cb, at, al) == arg
        else:
            at = next((e for e in self.entries(cb)
                       if self.argument(cb, e, al) == arg), None)
            hit = at is not None
        if hit and not self.deleted(at):            # Boxes 11, 14
            self.index(cb, "DX", at)
            self.index(cb, "FX", self.function_address(cb, at))
            return "found"
        loc = at if (ordered and at is not None) else after
        self.index(cb, "DX", loc)
        self.index(cb, "FX", loc)
        return "not found"

    # -- the entry itself (Box 30 AENTER) --------------------------------------
    def _enter(self, cb, at, arg, al, funct, fl):
        addl = self.get(cb, "ADDL")
        a = self.get(cb, "AL")
        self.mem.put(at, 2, 0)
        self.mem.put(at + 2, a, arg << (a - al))
        if fl > addl:
            v = self.auvtab
            self.mem.put(v, 1, 0)
            self.mem.put(v + 1, 13, (32 + fl) % (1 << 13))
            self.mem.put(v + 14, 6, self.get(cb, "ID"))
            self.mem.put(v + 20, 12, 0)
            self.mem.put(v + 32, fl, funct)
            self.auvtab = v + 32 + fl
            self.mem.put(at + 1, 1, 1)
            self.mem.put_signed(at + 2 + a, addl, v)
        else:
            self.mem.put(at + 2 + a, addl, funct << (addl - fl))

    # -- ADDUNO (p.49) ---------------------------------------------------------
    def adduno(self, cb, arg, al, funct, fl):
        self._compare_setup(cb, al)
        last = self.get(cb, "LW")
        if last >= self.get(cb, "FW") and self.deleted(last):
            at = last                       # Boxes 19, 28: replace it
        else:
            at = last + self.get(cb, "EL")  # Box 27: LW one entry on
            self.put(cb, "LW", at)
        self._enter(cb, at, arg, al, funct, fl)
        self.put(cb, "TO", 1)
        self.put(cb, "N", self.get(cb, "N") + 1)
        self.index(cb, "DX", at)
        self.index(cb, "FX", self.function_address(cb, at))
        return "normal"

    # -- ADDORD (p.48) ---------------------------------------------------------
    def addord(self, cb, arg, al, funct, fl):
        if self.get(cb, "TO") == 1:
            self.adduno(cb, arg, al, funct, fl)
            return "error"
        if self.search(cb, arg, al) == "found":
            return "already there"
        at = self.mem.get(cb + 64, 24)          # DX: next higher, or after
        el = self.get(cb, "EL")
        end = self.get(cb, "LW") + el
        self.move(at, at + el, end - at)
        self.put(cb, "LW", end)
        self._enter(cb, at, arg, al, funct, fl)
        self.put(cb, "N", self.get(cb, "N") + 1)
        self.index(cb, "DX", at)
        self.index(cb, "FX", self.function_address(cb, at))
        return "normal"

    # -- ANEXT (pp.50-51) ------------------------------------------------------
    def anext(self, ident):
        """The next undeleted vle with this ID, from the vle table's bottom
        (Afirst) or from Anexta.  Its location in Anextx."""
        p = self.auvbot if self.afirst else self.anexta
        self.afirst = False
        while p < self.auvtab:
            length = self.mem.get(p + 1, 13)
            if self.mem.get(p + 14, 6) == ident and not self.mem.get(p, 1):
                self.anextx = p
                self.anexta = p + length
                return "normal"
            p += length
        return "no more"

    # -- RSERCH (pp.52-53) -----------------------------------------------------
    def rserch(self, cb, faddr, to=None):
        """The dictionary entry whose function address is faddr.  With an
        index (to: its value), the entry is moved there; returns the new
        value as well."""
        for e in self.entries(cb):
            if self.function_address(cb, e) == faddr:
                self.index(cb, "DX", e)
                self.index(cb, "FX", faddr)
                if to is not None:
                    el = self.get(cb, "EL")
                    self.move(e, to, el)
                    return "found", to + el
                return "found", to
        return "not found", to

    # -- MOVE (pp.40-42) -------------------------------------------------------
    def move(self, frm, to, n):
        """n bits from frm to to, overlap allowed (p.41: forward or backward)."""
        if n <= 0 or frm == to:
            return
        bits = self.mem.get_str(frm, n)
        self.mem.put_str(to, bits)


def new(ucb=64 * 1000, bottom=64 * 4000):
    t = Tabman(BitMem(), ucb)
    t.define_universal(bottom)
    return t
