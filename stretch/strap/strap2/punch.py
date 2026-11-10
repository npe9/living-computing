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
    not yet run.

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
Binary cards alone carry sequence numbers.

CHOSEN: column 2 is the low 12 bits of the clock given; columns 73-80 are
blank (PUNID's identification is not written, and the card ID of a reproduced
card is not kept); LIM's n2 counts the undefined symbols' words above the
program, and n1 is the first origin card's origin; an IOD or REEL statement
must fit columns 10-62 on one card, or the deck refuses (the guide does not say
how a continued one is reproduced);
the TYPE card's options are not copied; a gap in the location counter
between units goes on the card as the image holds it, not as a new origin; a
DR's skip starts where the last data ended, so it covers its own rounding.
NOT WRITTEN: PUNFUL, PUNORG, PUNREL and the relocatable cards; TLB.  The
assembly goes on; the punch stops at the first, `unwritten` names it, and
`images` refuses.
`mcp` counts the IOD and REEL units.  `images` is the binary cards alone;
`deck` and `deck_images` the whole deck in order.
"""

ORIGIN_BITS, FLOW_BITS = 736, 800
ORIGIN_DATA, FLOW_DATA = 12 * 9 + 8, 12 * 4 + 4      # 10.8 and 5.4: card bits
DEFAULT_BRANCH = 0o41 * 64


class PunchError(Exception):
    pass


class Card:
    def __init__(self, kind, origin=0, nbits=0, value=0, skip=0, zero=False,
                 after=False, address=0):
        self.kind, self.origin, self.nbits, self.value = kind, origin, nbits, value
        self.skip, self.zero, self.after, self.address = skip, zero, after, address

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
        self._clear()
        self.flow_next = False
        self.next_at = None     # where a flow card would load

    def _clear(self):
        self.start, self.nbits, self.value = None, 0, 0
        self.skip, self.zero, self.skip_at = 0, False, None    # a skip before loading

    # -- the buffer --------------------------------------------------------------
    def _is_flow(self):
        return self.flow_next and not self.skip

    def _capacity(self):
        return FLOW_BITS if self._is_flow() else ORIGIN_BITS

    def _emit(self, unit, card):
        if card.kind == "origin" and self.first_origin is None:
            self.first_origin = card.origin
        self.cards.append(card)
        self.events.append((unit, len(self.cards) - 1))

    def _punch(self, unit, after=0, zero=False):
        """Punch what the buffer holds, with `after` bits skipped or zeroed after
        loading.  A short flow card becomes an origin card (p.23); more than an
        origin card holds goes on two (chart OV box 4)."""
        if not self.nbits and not self.skip and not after:
            return
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

    def data(self, unit, at, nbits, value):
        if nbits <= 0:
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

    def reserve(self, unit, at, size, zero, running):
        """A DR (zero False) or DRZ: chart OV."""
        end = at + size
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

    def slc(self, unit):
        """Chart OS: with PUNFUL off an SLC forces an origin card."""
        self._punch(unit)
        self._clear()
        self.flow_next = False
        self.next_at = None

    def end(self, unit, address):
        self._punch(unit)
        if address is None:
            address = (DEFAULT_BRANCH if self.edition == "N28-1081"
                       else (self.first_origin or 0))
        self._emit(unit, Card("branch", address=address))

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
        return [self._encode(c, seq, clock) for seq, c in enumerate(self.cards, 1)]

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
        out, seq = [], 0
        for how, c in self.deck():
            if how == "text":
                out.append([hollerith.column_bits(ch) for ch in c.ljust(80)])
            else:
                seq += 1
                out.append(self._encode(c, seq, clock))
        return out

    def _encode(self, c, seq, clock):
        bits = [0] * 960

        def put(at, n, v):
            for k in range(n):
                bits[at + k] = (v >> (n - 1 - k)) & 1
        row = {"origin": (9, 10, 11), "flow": (9, 11), "branch": (8, 9, 11)}[c.kind]
        for r in row:
            bits[r] = 1
        put(12, 12, clock & 0xFFF)
        put(24, 12, seq & 0xFFF)
        if c.kind == "origin":
            put(48, 1, int(c.zero))
            put(49, 1, int(c.after))
            put(50, 10, c.nbits)
            put(60, 24, c.origin)
            put(84, 24, c.skip)
            put(ORIGIN_DATA, c.nbits, c.value)
        elif c.kind == "flow":
            put(FLOW_DATA, c.nbits, c.value)
        else:
            put(60, 24, c.address)
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
