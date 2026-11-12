"""punch.py -- OUTPUT's absolute binary deck: origin, flow and branch cards.

Sources, read in the ink:
  C28-6129 pp.22-23 (PDF 26-27), with N28-1081's errata (page 18, PDF p.76):
    origin card  1.9, 1.10, 1.11; 2 ID; 3 sequence; 4 check sum; 5.0 skip (0) or
                 zero (1); 5.1 before (0) or after (1) loading; 5.2-5.11 primary
                 bit count; 6-7 24-bit origin; 8-9 secondary bit count; 10.0-10.7
                 unused; 10.8-71.11 up to 736 bits ("not 0 to 748 but 0 to 736";
                 "not through 72 but through 71").
    flow card    1.9, 1.11; 2-4 as above; 5.0-5.3 unused; 5.4-71.11 exactly 25
                 half-words, all loaded.
    branch card  1.8, 1.9, 1.11; 2-4; 5 unused; 6.0-7.11 24-bit transfer address
                 (errata's corrected format).  END or TLB with no address: 41.8
                 (errata; the 1961 text said the first origin).
    "When a DR or DRZ immediately follows an SLC" the skip goes on the origin
    card before loading; a flow card under way when a DR comes "is changed to an
    origin card"; the card before a branch card is forced to an origin card.
  C22-6729 chart OP p.150 boxes 9-11 (store binary, determine card type, buffer
    full: punch); chart OV p.155 (DR: boxes 3-13); chart OS p.152 (SLC with
    PUNFUL off forces an origin card).
  docs/bss_loader_spec.md, from MCP's own loader (listing printed pp.320-334):
    column c, row r is bit 12(c-1)+r of the card; the check sum as ACHSM reads
    (sum of the 12-bit columns 1-3 and 5-71, folded end-around), AS READ there,
    and run: MCP's transcribed loader loads an absolute deck from this punch on
    the model, sequence and check sum accepted (tests/gen_loader_deck_tb.py).

What this models, and the order it follows.  Each unit's binary goes into the
punch buffer as it is output; a card is punched when it is full (736 bits for
an origin card, 800 for a flow card), at a DR or DRZ that follows data (the card
takes the skip or zero after loading, chart OV box 13), at an SLC, at a jump in
the location counter, and at END, which then punches the branch card.  A card
that follows a full card is a flow card; any other is an origin card.  DRs in a
row with no data between add their lengths (box 8) and go on the next card as a
skip before loading.  `events` records each punch against the unit that caused
it, which is what the listing's second '*' after the location seems to mark
(docs/strap2/pass2.md section 12, DERIVED).

MCP control cards (C22-6678-1 pp.7-11, read in the ink): Hollerith, in the
card code of Appendix F p.56 (strap/cards.py).  The deck starts with NMCPA1's
two (guide p.148, p.157 boxes 15-16): `B` in column 1 and `TYPE,GO` from column
10; then `LIM,n1,n2`, six-digit octal, n1 the word holding the lowest bit used,
n2 the word after the highest (p.8).  An IOD card is reproduced as submitted,
with the reference number in columns 63-66 as four octal digits and the exit's
word address in 67-72 as six (p.9); a REEL card as submitted, 63-80 blank
(p.10).  Both go out at their own unit, before any binary card after them.
Binary cards alone carry sequence numbers.  NOSEQ and RESEQ (chart OU p.154,
N28-1081 page 2, read in the ink) punch the card in process; after NOSEQ the
sequence column is left blank, and after RESEQ the count starts again at 1.
Whether a card under NOSEQ advances the count cannot show: only RESEQ ends
NOSEQ, and RESEQ clears it.

Chart OR (C22-6729 p.151): PUNID punches the card in process, then stores the
ID, which every binary card after carries in columns 73-80 in the card code
(C28-6129 p.13, PDF 17: "columns 73-80 of every binary card"; N28-1081 page 6
says the same of the update's relocatable formats); outside the check sum.
TLB punches an origin card and a branch card (to 41.8 with no address, as END)
and the next card is an origin card; the deck goes on (C28-6129 p.39, PDF 43).
NOPUN punches the card and suppresses punching until PUNNOR (C28-6129 p.37,
PDF 41, and N28-1081's errata page 19: any punch pseudo-op ends it); PUNNOR
punches the card and starts an origin card (p.36, PDF 40).  All read in the
ink 2026-11-10.  An SLCR stops punching until the next SLC (guide p.36,
C28-6129 p.39); chart OT p.153 draws nothing for it.

CHOSEN: column 2 is the low 12 bits of the clock given; a reproduced card's
columns 73-80 are blank (its card ID is not kept); under NOPUN nothing is
punched, END's branch card included ("binary output suppressed", N28-1081
page 9); LIM's n2 counts the undefined symbols' words above the
program, and n1 is the first origin card's origin; an IOD or REEL statement
must fit columns 10-62 on one card, or the deck refuses (the guide does not say
how a continued one is reproduced);
the TYPE card's options are not copied; a gap in the location counter
between units goes on the card as the image holds it, not as a new origin; a
DR's skip starts where the last data ended, so it covers its own rounding.
PUNREL (stage 1): from the start of the program, the relocatable data and
instruction cards (6729 pp.187-188) and ORIGIN's O card; MCP's own loader
loads such a deck (tests/gen_loader_deck_tb.py rel).  CHOSEN under PUNREL:
END punches no branch card (N28-1081 page 3 says so for FORTRAN's END; the
loader does not relocate a branch card's address, p.323); the LIM card's
two half-words are punched as computed, and mean nothing to a relocated
load.  The relocation codes are the ones MCP's loader reads (p.324 l.30 -
p.325): 1000 relocates a half-word's left 18 bits, 1010 its right 18.  What
VALUE's Sinrl1/Sinrl2 mean is UNSPECIFIED (docs/bss_loader_spec.md 9); the
code counts location-counter symbols instead (value.py symbol_lc).
NOT WRITTEN: a field with more than one location-counter symbol (message
123; what IBM punched for it is UNSPECIFIED); PUNREL after absolute output; SLCRCOM; a COMBLOCK
without a name; a relocatable value in a field with no relocation position;
a low SLC under PUNFUL.  The assembly goes on; the punch stops at the first,
`unwritten` names it, and `images` refuses.
`mcp` counts the IOD and REEL units.  `images` is the binary cards alone;
`deck` and `deck_images` the whole deck in order.
"""

ORIGIN_BITS, FLOW_BITS, FULL_BITS = 736, 800, 960
ORIGIN_DATA, FLOW_DATA = 12 * 9 + 8, 12 * 4 + 4      # 10.8 and 5.4: card bits
# PUNREL's cards, C22-6729 pp.187-188 (read in the ink 2026-11-11), the columns
# as MCP's loader reads them (bss_loader_spec.md 4.5, 4.6; printed pp.324-326):
# a relocatable data card loads 11.0-71.11, a relocatable instruction card's
# instructions and then their relocation bits fill 9.0-71.11.
RDATA_BITS, RDATA_DATA = 12 * 61, 12 * 10
RINSTR_ROOM, RINSTR_DATA = 12 * 63, 12 * 8
# The FORTRAN program and common definition cards (6729 pp.187-188): nine
# entries a card from 9.0, seven columns each -- an A8 name (64 bits) and an
# entry address (19 bits) or a common size (18 bits).
ENTRY_AT, ENTRY_STEP, PER_CARD = 12 * 8, 12 * 7, 9
DEFAULT_BRANCH = 0o41 * 64


class PunchError(Exception):
    pass


class Card:
    def __init__(self, kind, origin=0, nbits=0, value=0, skip=0, zero=False,
                 after=False, address=0):
        self.kind, self.origin, self.nbits, self.value = kind, origin, nbits, value
        self.skip, self.zero, self.after, self.address = skip, zero, after, address
        self.ident = None
        self.seq = 0

    def __repr__(self):
        if self.kind == "branch":
            return f"Card(branch, {self.address:o})"
        return (f"Card({self.kind}, origin={self.origin:o}, nbits={self.nbits}, "
                f"skip={self.skip}{' zero' if self.zero else ''}"
                f"{' after' if self.after else ''})")


class Punch:
    def __init__(self, edition="N28-1081"):
        self.cards = []
        self.events = []        # (unit, card index)
        self.mcp = 0
        self.control = []       # (binary cards before it, text), in deck order
        self.lim = None
        self.unwritten = None   # the first pseudo-op whose cards are not written
        self.edition = edition
        self.first_origin = None
        self.ident = None       # PUNID's eight characters, columns 73-80
        self.suppressed = False # NOPUN
        self.relative = False   # after an SLCR, until an SLC
        self.noseq = False      # NOSEQ, until RESEQ
        self.punorg = False     # PUNORG, until PUNNOR
        self.punful = False     # PUNFUL, until PUNNOR, PUNORG or PUNREL
        self.full_slc = False   # PUNFUL: an SLC has been seen (chart OS "1ST SLC")
        self.full_at = None     # PUNFUL: the bit the next full-card bit is
        self.full_bits, self.full_value, self.full_origin = 0, 0, None
        self.count = 0          # the sequence number of the last card
        self._clear()
        self.flow_next = False
        self.next_at = None     # where a flow card would load
        self.rel = False        # PUNREL: relocatable cards
        self._ri_clear()
        self.group = None       # PUNFPC or PUNCDC mode: the card being filled

    def _ri_clear(self):
        self.ri_start, self.ri_bits, self.ri_value = None, 0, 0
        self.ri_reloc = {}      # half-word of the card -> "L" or "R"

    def _clear(self):
        self.start, self.nbits, self.value = None, 0, 0
        self.skip, self.zero, self.skip_at = 0, False, None    # a skip before loading

    # -- the buffer --------------------------------------------------------------
    def _is_flow(self):
        # PUNREL: every relocatable data card carries its own origin; there is
        # no relocatable flow card (C22-6729 pp.187-188 list none).
        return self.flow_next and not self.skip and not self.punorg and not self.rel

    def _capacity(self):
        if self.rel:
            return RDATA_BITS
        return FLOW_BITS if self._is_flow() else ORIGIN_BITS

    def _emit(self, unit, card):
        if self.rel and card.kind == "origin":
            card.kind = "rdata"
        if card.kind == "origin" and self.first_origin is None:
            self.first_origin = card.origin
        if card.kind == "full":
            # C28-6129 p.36: "without checksum, first word address,
            # identification, and so on".  CHOSEN: no sequence count either.
            card.seq = 0
            self.cards.append(card)
            self.events.append((unit, len(self.cards) - 1))
            return
        card.ident = self.ident
        if self.noseq:
            card.seq = 0
        else:
            self.count += 1
            card.seq = self.count
        self.cards.append(card)
        self.events.append((unit, len(self.cards) - 1))

    def _punch(self, unit, after=0, zero=False):
        """Punch what the buffer holds, with `after` bits skipped or zeroed after
        loading.  A short flow card becomes an origin card (p.23); more than an
        origin card holds goes on two (chart OV box 4).  In PUNFUL mode, the
        full card in process (CHOSEN: a short one is filled out with zeros)."""
        if self.rel and self.ri_bits:
            self._punch_ri(unit)
        if self.punful:
            if self.full_bits:
                n = FULL_BITS - self.full_bits
                self._emit(unit, Card("full", self.full_origin, FULL_BITS,
                                      self.full_value << n))
                self.full_bits, self.full_value, self.full_origin = 0, 0, None
            return
        if not self.nbits and not self.skip and not after:
            return
        if self.rel and self.nbits > RDATA_BITS:
            raise PunchError("a relocatable data card holds 732 bits")
        full = self._is_flow() and self.nbits == FLOW_BITS and not after
        if full:
            self._emit(unit, Card("flow", self.start, self.nbits, self.value))
            end = self.start + self.nbits
        else:
            if self.nbits > ORIGIN_BITS:
                rest = self.nbits - ORIGIN_BITS
                self._emit(unit, Card("origin", self.start, ORIGIN_BITS,
                                      self.value >> rest))
                self.start += ORIGIN_BITS
                self.nbits, self.value = rest, self.value & ((1 << rest) - 1)
            origin = self.skip_at if self.skip else self.start
            if origin is None:
                origin = self.start
            skip, z, aft = (self.skip, self.zero, False) if self.skip else (after, zero, True)
            if self.skip and after:
                raise PunchError("a card with a skip both before and after loading")
            self._emit(unit, Card("origin", origin, self.nbits, self.value,
                                  skip, z, aft and bool(after)))
            end = (self.start if self.start is not None else origin + skip) + self.nbits
        self.next_at = end + (after if after else 0)
        self.flow_next = full
        self._clear()

    def _full(self, unit, at, nbits, value):
        """PUNFUL: 80 columns of column binary, nothing else (C28-6129 pp.23,
        36).  Bits go on in order; a full card goes out at once."""
        if self.full_at is None:
            self.full_at = at
        if at < self.full_at:
            raise PunchError(f"PUNFUL: data at {at:o} below the counter {self.full_at:o}")
        if at > self.full_at:
            # CHOSEN: a gap the counter left (rounding) goes on the card as
            # zeros, as chart OS does with an SLC above the counter.
            self._full_bits(unit, at - self.full_at, 0)
        self._full_bits(unit, nbits, value)

    def _full_bits(self, unit, nbits, value):
        while nbits:
            if not self.full_bits:
                self.full_origin = self.full_at
            take = min(FULL_BITS - self.full_bits, nbits)
            rest = nbits - take
            self.full_value = (self.full_value << take) | (value >> rest)
            self.full_bits += take
            value &= (1 << rest) - 1
            nbits = rest
            self.full_at += take
            if self.full_bits == FULL_BITS:
                self._punch(unit)

    def data(self, unit, at, nbits, value):
        if nbits <= 0:
            return
        if self.punful:
            self._full(unit, at, nbits, value)
            return
        if self.start is None:
            if self.skip:
                if at != self.skip_at + self.skip:
                    self._punch(unit)
                    self.flow_next = False
            elif self.flow_next and at != self.next_at:
                self.flow_next = False
            self.start = at
        elif at != self.start + self.nbits:
            # a jump in the counter: what the buffer holds goes out first.
            self._punch(unit)
            self.flow_next = False
            self.start = at
        while nbits:
            room = self._capacity() - self.nbits
            take = min(room, nbits)
            rest = nbits - take
            self.value = (self.value << take) | (value >> rest)
            self.nbits += take
            value &= (1 << rest) - 1
            nbits = rest
            if self.nbits == self._capacity():
                end = self.start + self.nbits
                self._punch(unit)
                self.flow_next = True
                self.next_at = end
                if nbits:
                    self.start = end

    # -- PUNREL ------------------------------------------------------------------
    def punrel_(self, unit):
        """PUNREL (C22-6729 p.186; C28-6129, N28-1081 page 2): the card in
        process goes out, and relocatable cards follow.  It ends a PUNFUL
        (chart OR, see `punful`)."""
        self._end_full(unit)
        self._new_origin()
        self.suppressed = False
        self.rel = True

    # -- PUNFPC / ENTER, PUNCDC / COMBLOCK, FEND (C22-6729 pp.183, 186-188) -----
    def group_start(self, unit, kind, size=None, common=None):
        """PUNFPC ("fprog") or PUNCDC ("comdef"): OUTPUT "goes into PUNFPC
        mode and sets up the format" (p.186).  The card in process goes out
        first (CHOSEN, as at ORIGIN)."""
        self.group_end(unit)
        self._punch(unit)
        self._new_origin()
        c = Card(kind)
        c.size, c.common, c.entries = size, common, []
        self.group = c

    def group_add(self, unit, kind, name, value):
        """An ENTER or COMBLOCK: False if not in its mode (messages 138, 137).
        "When either a non-ENTER statement is encountered or the card is
        full, the Fortran Program Card is punched.  Additional Fortran Cards
        are in the same format except that the program size and amount of
        blank common used fields are blank" (p.186)."""
        if self.group is None or self.group.kind != kind:
            return False
        if len(self.group.entries) == PER_CARD:
            more = Card(kind)
            more.size, more.common, more.entries = None, None, []
            self._emit(unit, self.group)
            self.group = more
        self.group.entries.append((name, value))
        return True

    def group_end(self, unit):
        """A statement other than ENTER or COMBLOCK leaves the mode and punches
        the card -- the first one even with no entries (a PUNFPC with no
        ENTER is a data subprogram, bss_loader_spec.md 6.3)."""
        if self.group is not None:
            c, self.group = self.group, None
            self._emit(unit, c)

    def fend(self, unit):
        """FEND (N28-1081 page 3): "Either END or FEND may terminate a FORTRAN
        program or subprogram.  If FEND is used, STRAP will produce a FORTRAN
        branch card."  5.0-71.11 not used (6729 p.187)."""
        self.group_end(unit)
        self._punch(unit)
        self._new_origin()
        self._emit(unit, Card("fbranch"))

    def origin_card(self, unit, at):
        """ORIGIN,N (C22-6729 p.183): the special origin card, column 1 O and
        "xxxxxx.0" in columns 2-9 (p.188), which the loader reads as six octal
        digits into its origin counter (printed p.323 l.45 - p.324 l.11).  It
        goes out between the binary cards, after the one in process.  CHOSEN:
        a location below a full word gives its word; columns 72-80 are blank."""
        self._punch(unit)
        self._new_origin()
        self.control.append((len(self.cards), "O%06o.0" % (at // 64)))

    def rel_data(self, unit, at, nbits, value, instr, reloc):
        """One unit's binary in PUNREL mode.  Instructions, XW, CW, VF, CF, RF
        go on relocatable instruction cards with their relocation bits; DD's
        and DR's on relocatable data cards, which carry none (C22-6729 p.188:
        "instructions, XW's, CF's, and RF's only (i.e., no DD's or DR's)")."""
        if not instr:
            if reloc:
                self.unwritten = self.unwritten or "a relocatable value on a data card"
                return
            if self.ri_bits:
                self._punch_ri(unit)
            self.data(unit, at, nbits, value)
            return
        if self.nbits or self.skip:
            self._punch(unit)
            self.flow_next = False
        if self.ri_bits and at != self.ri_start + self.ri_bits:
            self._punch_ri(unit)
        if not self.ri_bits:
            if at % 32:
                self.unwritten = self.unwritten or f"a relocatable instruction card at {at:o}, not on a half-word"
                return
            self.ri_start = at
        new = dict(self.ri_reloc)
        for b, side in reloc:
            half, off = divmod(b - self.ri_start, 32)
            if off != {"L": 0, "R": 14}[side] or new.get(half, side) != side:
                self.unwritten = self.unwritten or f"a relocatable field at {b:o} that no relocation bits reach"
                return
            new[half] = side
        if self._ri_room(self.ri_bits + nbits, new) > RINSTR_ROOM:
            self._punch_ri(unit)
            self.ri_start = at
            new = {}
            for b, side in reloc:
                new[(b - at) // 32] = side
        self.ri_value = (self.ri_value << nbits) | value
        self.ri_bits += nbits
        self.ri_reloc = new

    @staticmethod
    def _ri_codes(nbits, reloc):
        """One set per half-word, a short last one included (the loader's
        ARBCD7, printed p.325 lines 43-53): 0, or 1x00 / 1x10 (x reserved, 0)."""
        out = ""
        for h in range((nbits + 31) // 32):
            side = reloc.get(h)
            out += "0" if side is None else ("1000" if side == "L" else "1010")
        return out

    def _ri_room(self, nbits, reloc):
        return nbits + len(self._ri_codes(nbits, reloc))

    def _punch_ri(self, unit):
        if not self.ri_bits:
            return
        c = Card("rinstr", self.ri_start, self.ri_bits, self.ri_value)
        c.codes = self._ri_codes(self.ri_bits, self.ri_reloc)
        end = self.ri_start + self.ri_bits
        self._ri_clear()
        self._emit(unit, c)
        self.next_at = end
        self.flow_next = False

    def reserve(self, unit, at, size, zero, running):
        """A DR (zero False) or DRZ: chart OV."""
        if self.rel and self.ri_bits:
            self._punch_ri(unit)
        end = at + size
        if self.punful:
            # Boxes 1-2, p.158: "blank words and/or cards must be punched
            # equivalent to the DR length."
            start = self.full_at if self.full_at is not None else at
            self._full(unit, start, max(0, end - start), 0)
            return
        if self.nbits and self.skip:
            # The card already skips before loading and cannot skip after as
            # well (CHOSEN): it goes out, and this DR starts the next card's skip.
            self._punch(unit)
            self.flow_next = False
        if self.nbits:
            # box 13: the card skips (or zeroes) after loading, and goes out.
            gap = end - (self.start + self.nbits)
            self._punch(unit, after=gap, zero=zero)
            self.flow_next = False
            return
        if self.skip and self.zero != zero:
            # box 3: a DRZ in process when a DR comes, or the reverse.
            self._punch(unit)
        if self.skip:
            self.skip = end - self.skip_at          # box 8: lengths added
        else:
            self.skip_at = self.next_at if self.next_at is not None else running
            if self.skip_at is None or self.skip_at > at:
                self.skip_at = at
            self.skip, self.zero = end - self.skip_at, zero
        self.flow_next = False

    def slc(self, unit, value=None):
        """Chart OS (C22-6729 p.152): with PUNFUL off an SLC forces an origin
        card.  With PUNFUL on: the first SLC (since PUNFUL; see below) stores the new value,
        whatever was punched before it; one equal to
        the counter does nothing; one above it has the difference processed as
        a DRZ in PUNFUL mode; one below turns on the low-SLC indicator and keeps
        the counter for comparison.  NOT WRITTEN: what OUTPUT does after a low
        SLC (no chart page shows the comparison); the deck stops there."""
        if self.punful and value is not None:
            if not self.full_slc:
                # "1ST SLC" is asked before any comparison.  The chart names no
                # scope; READ as first since PUNFUL was turned on, because MCP
                # printed p.99 needs it: pp.2-98 and p.99 are one assembly
                # (p.98 ends with UNTAIL, not END, and p.99 line 9 opens at
                # 005466.00 = X IN END), SLCs on pp.2 and 15 come before it,
                # and an assembly-wide "first" would punch line 11's jump from
                # 005476.34 to 215000.00 as some 14,000 full cards of zeros.
                self.full_slc = True
                self.full_at = value
            elif value < self.full_at:
                self.unwritten = "PUNFUL low SLC"
            elif value > self.full_at:
                self._full(unit, self.full_at, value - self.full_at, 0)
            return
        self._punch(unit)
        self._clear()
        self.flow_next = False
        self.next_at = None

    def end(self, unit, address):
        self._punch(unit)
        if self.rel:
            # CHOSEN: in PUNREL mode END punches no branch card.  The branch
            # card's address is not relocated by the loader (printed p.323
            # lines 26-35), and N28-1081 page 3: "If END is specified, no
            # branch card will be punched" (said of a FORTRAN program, whose
            # FEND punches the FORTRAN branch card).
            return
        if address is None:
            address = (DEFAULT_BRANCH if self.edition == "N28-1081"
                       else (self.first_origin or 0))
        self._emit(unit, Card("branch", address=address))

    def _new_origin(self):
        """Chart OR: "turn on origin card indicator": the next card is an origin card."""
        self._clear()
        self.flow_next = False
        self.next_at = None

    def punid(self, unit, ident):
        """Chart OR, PUNID: punch the card in the existing mode, store the new ID."""
        self._punch(unit)
        self.flow_next = False
        self.ident = ident

    def punful_(self, unit):
        """Chart OR, PUNFUL: punch the card in the existing mode, turn on the
        PUNFUL indicator.  It ends a NOPUN (N28-1081 errata page 19)."""
        self._punch(unit)
        self._new_origin()
        self.suppressed = False
        self.punful = True
        self.full_at = None
        self.full_slc = False   # chart OS "1ST SLC"

    def _end_full(self, unit):
        self._punch(unit)
        self.punful = False
        self.full_at = None

    def nopun(self, unit):
        """Chart OR, NOPUN: punch the card, turn on the NOPUN indicator."""
        self._punch(unit)
        self._new_origin()
        self.suppressed = True

    def punnor(self, unit):
        """Chart OR, PUNNOR: punch the card, turn on the origin card indicator;
        ends a NOPUN (N28-1081 errata, page 19), and a PUNFUL (C28-6129 p.36)."""
        self._end_full(unit)
        self._new_origin()
        self.suppressed = False
        self.punorg = False

    def punorg_(self, unit):
        """Chart OR, PUNORG: punch the card in the existing mode, turn on the
        origin and PUNORG indicators: every card after is an origin card
        (C28-6129 p.36).  Like any punch pseudo-op it ends a NOPUN (N28-1081
        errata page 19).  CHOSEN: PUNNOR ends it ("restores normal punching")."""
        self._end_full(unit)
        self._new_origin()
        self.suppressed = False
        self.punorg = True

    def tlb(self, unit, address):
        """Chart OR, TLB: punch an origin card and a branch card, turn on the
        origin card indicator.  The assembly and the deck go on (C28-6129 p.39)."""
        self.end(unit, address)
        self._new_origin()

    def noseq_(self, unit):
        """Chart OU (C22-6729 p.154), NOSEQ: punch the card in the existing mode,
        turn on the bit to prevent punching sequence numbers."""
        self._punch(unit)
        self.flow_next = False
        self.noseq = True

    def reseq(self, unit):
        """Chart OU, RESEQ: punch the card, turn the bit off, clear the sequence
        number field: the next card is 1 (N28-1081 page 2)."""
        self._punch(unit)
        self.flow_next = False
        self.noseq = False
        self.count = 0

    def text_card(self, unit, text):
        """An MCP card, punched at its unit (chart OP boxes 15, 16)."""
        self.control.append((len(self.cards), text))

    def finish(self, unit):
        """After the last unit.  STRAP II's deck ends at END; a deck without one
        (a transcribed page) has its last card punched here, and no branch card
        (CHOSEN)."""
        self._punch(unit)

    # -- card images -------------------------------------------------------------
    def images(self, clock=0):
        """Each binary card as 80 twelve-bit columns, row 0 the high bit."""
        if self.unwritten:
            raise PunchError(f"{self.unwritten}: its cards are not written, so the deck stops there")
        return [self._encode(c, c.seq, clock) for c in self.cards]

    def deck(self):
        """The whole deck in order: ("text", card) or ("binary", Card)."""
        if self.unwritten:
            raise PunchError(f"{self.unwritten}: its cards are not written, so the deck stops there")
        out = [("text", "B         TYPE,GO")]
        if self.lim is not None:
            out.append(("text", f"B         LIM,{self.lim[0]:06o},{self.lim[1]:06o}"))
        k = 0
        for at, text in self.control + [(len(self.cards), None)]:
            while k < at:
                out.append(("binary", self.cards[k]))
                k += 1
            if text is not None:
                if len(text) > 80:
                    raise PunchError(f"control card longer than 80 columns: {text!r}")
                out.append(("text", text))
        return out

    def deck_images(self, clock=0):
        """The whole deck as columns: control cards in the card code."""
        import cards as hollerith          # strap/cards.py, Appendix F
        out = []
        for how, c in self.deck():
            if how == "text":
                out.append([hollerith.column_bits(ch) for ch in c.ljust(80)])
            else:
                out.append(self._encode(c, c.seq, clock))
        return out

    def _encode(self, c, seq, clock):
        if c.kind == "full":
            return [(c.value >> (12 * (79 - i))) & 0xFFF for i in range(80)]
        bits = [0] * 960

        def put(at, n, v):
            for k in range(n):
                bits[at + k] = (v >> (n - 1 - k)) & 1
        # Column 1's bits: bit b is row 12, 11, 0, 1, ..., 9 for b = 0..11,
        # so digit row d is bit d + 2 (C28-6129's "1.9" is bit 9, row 7).
        row = {"origin": (9, 10, 11), "flow": (9, 11), "branch": (8, 9, 11),
               "rdata": (8, 9, 10, 11),         # 6,7,8,9 punches (6729 p.187)
               "rinstr": (7, 9, 11),            # 5,7,9 punches (6729 p.188)
               "fprog": (7, 8, 9, 11),          # 5,6,7,9 (p.188)
               "comdef": (7, 9, 10, 11),        # 5,7,8,9 (p.187)
               "fbranch": (7, 8, 9, 10, 11)}[c.kind]   # 5,6,7,8,9 (p.187)
        for r in row:
            bits[r] = 1
        put(12, 12, clock & 0xFFF)
        put(24, 12, seq & 0xFFF)
        if c.kind == "rdata":
            put(48, 1, int(c.zero))
            put(49, 1, int(c.after))
            put(50, 10, c.nbits)
            put(60, 24, c.origin)
            put(84, 24, c.skip)
            put(108, 12, 0)                 # loading base 0: the program
            put(RDATA_DATA, c.nbits, c.value)
        elif c.kind == "rinstr":
            put(48, 12, c.nbits)            # "excluding the relocation bits"
            put(60, 24, c.origin)
            put(RINSTR_DATA, c.nbits, c.value)
            for k, ch in enumerate(c.codes):
                bits[RINSTR_DATA + c.nbits + k] = int(ch)
        elif c.kind == "origin":
            put(48, 1, int(c.zero))
            put(49, 1, int(c.after))
            put(50, 10, c.nbits)
            put(60, 24, c.origin)
            put(84, 24, c.skip)
            put(ORIGIN_DATA, c.nbits, c.value)
        elif c.kind == "flow":
            put(FLOW_DATA, c.nbits, c.value)
        elif c.kind in ("fprog", "comdef"):
            from .a8 import a8
            if c.kind == "fprog" and c.size is not None:
                put(60, 18, c.size)         # 6.0-7.5, program size
                put(78, 18, c.common)       # 7.6-8.11, blank common
            for k, (name, value) in enumerate(c.entries):
                at = ENTRY_AT + ENTRY_STEP * k
                for j, ch in enumerate(name.ljust(8)[:8]):
                    put(at + 8 * j, 8, a8(ch))
                # 14.4-15.10 entry address (19 bits); 14.4-15.9 size (18)
                put(at + 64, 19 if c.kind == "fprog" else 18, value)
        elif c.kind == "fbranch":
            pass
        else:
            put(60, 24, c.address)
        if c.ident is not None:
            import cards as hollerith          # strap/cards.py, Appendix F
            for k, ch in enumerate(c.ident):
                put(12 * (72 + k), 12, hollerith.column_bits(ch))
        cols = [int("".join(map(str, bits[12 * i:12 * i + 12])), 2) for i in range(80)]
        cols[3] = checksum(cols)
        return cols


def checksum(cols):
    """ACHSM as read (docs/bss_loader_spec.md 5.3): columns 1-3 and 5-71."""
    s = sum(cols[0:3]) + sum(cols[4:71])
    while s >> 12:
        s = (s & 0xFFF) + (s >> 12)
    return s


def load(cards):
    """What the loader's absolute path does with the cards (C28-6379 p.4, the
    loader as read): returns {bit address: bit} loaded, and the branch address."""
    mem, at, branch = {}, None, None
    for c in cards:
        if c.kind == "branch":
            branch = c.address
            continue
        if c.kind == "origin":
            at = c.origin
            if c.skip and not c.after:
                if c.zero:
                    for k in range(c.skip):
                        mem[at + k] = 0
                at += c.skip
        for k in range(c.nbits):
            mem[at + k] = (c.value >> (c.nbits - 1 - k)) & 1
        at += c.nbits
        if c.kind == "origin" and c.skip and c.after:
            if c.zero:
                for k in range(c.skip):
                    mem[at + k] = 0
            at += c.skip
    return mem, branch
