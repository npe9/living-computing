"""cards.py -- GETCHA and the card block, C22-6729 pp.77-79, 203-205.

A card: column 1 mark, 2-9 name, 10-72 statement, 73-80 identification.  A
continuation card has '*' in column 1 (p.203).  The comment character is the
quote (p.14, p.183).

deck_cards() is scaffolding, not STRAP II.  This project's decks are free form
with '!' comments, and it lays them out on cards so that GETCHA reads what a
real assembly would.
"""
import re

STMT_FIRST, STMT_LAST = 9, 72          # zero-based, half open: columns 10-72
FIELD = STMT_LAST - STMT_FIRST


class Block:
    """One card image's parts, from the first card of a block on."""

    def __init__(self, card):
        self.card = card.ljust(80)


def deck_cards(source):
    """Free-form deck lines to 80-column images, continuing long statements.

    The split of a long statement across cards is at column 72 exactly, since
    GETCHA joins continuation statement fields with nothing between them.
    """
    out = []
    for raw in source.splitlines():
        code = raw.split("!", 1)[0].rstrip()
        if not code.strip():
            continue
        if code[0] not in " \t":
            m = re.match(r"^(\S+)\s+(.*)$", code)
            name, text = (m.group(1), m.group(2)) if m else (code.strip(), "")
        else:
            name, text = "", code.strip()
        first = True
        while first or text or name:
            piece, text = text[:FIELD], text[FIELD:]
            head, name = name[:8], name[8:]
            mark = " " if first else "*"
            out.append((mark + head.ljust(8) + piece).ljust(72))
            first = False
    return out


class Getcha:
    """p.77-79.  next() returns the next statement character, as $3 holds it.

    Blanks are skipped unless gcaz is on (p.20).  At the end of a block the
    character is the false ';' with fblend on.  None means the cards ran out.
    """

    def __init__(self, cards):
        self.cards = list(cards)
        self.i = 0
        self.card = None
        self.col = STMT_LAST
        self.gcaz = False
        self.ch = None
        self.fblend = True      # "initially on", p.20
        self.fblena = False
        self.name = ""          # name buffer, embedded blanks kept
        self.named = False
        self.card_id = ""
        self.bsyst = []         # statement buffer, p.79
        self.comment_block = False
        self.statement_id = ""
        self.exhausted = False

    def start_statement(self):
        self.bsyst = []

    def _open_block(self):
        """Fetch an initial card and inspect columns 1-9 (p.77 item 3)."""
        if self.i >= len(self.cards):
            self.exhausted = True
            return False
        self.card = self.cards[self.i].ljust(80)
        self.i += 1
        self.card_id = self.card[72:80]
        self.name, self.named = "", False
        self.comment_block = False
        col1 = self.card[0]
        if col1 == "'":
            # p.79: in column 1 of an initial card the entire card is comment.
            self.comment_block = True
            self.bsyst.extend(self.card[1:72].rstrip())
            self.col = STMT_LAST
            return True
        self._read_name()
        # p.79: the name may continue on following continuation cards.
        k = self.i
        while not self.comment_block and k < len(self.cards) and self.cards[k][:1] == "*":
            more = self.cards[k].ljust(80)[1:9]
            if not more.strip():
                break
            self.name += more       # embedded blanks kept, as above
            k += 1
        self.name = self.name.rstrip()
        self.col = STMT_FIRST
        return True

    def _read_name(self):
        for c in self.card[1:9]:
            if c == "'":
                # p.79: a quote in columns 2-9 of an initial card makes the
                # entire block a comment.
                self.comment_block = True
                self.name = ""
                self.bsyst.extend(self.card[9:72].rstrip())
                self.col = STMT_LAST
                return
            self.name += c
        self.name = self.name.rstrip()
        self.named = bool(self.name.strip())

    @property
    def symbol(self):
        """p.205: a symbol is the name without its blanks."""
        return self.name.replace(" ", "").upper()

    def next(self):
        if self.card is None:
            if not self._open_block():
                self.ch = None
                return None
            if self.comment_block:
                self.ch = "'"
                return self.ch
        while True:
            if self.col >= STMT_LAST:
                # p.78 item 5: end of the statement field.
                if self.i < len(self.cards) and self.cards[self.i][:1] == "*":
                    self.card = self.cards[self.i].ljust(80)
                    self.i += 1
                    self.col = STMT_FIRST
                    self.bsyst.append("\n")    # CHOSEN: each card is a line, listing.py
                    continue
                # p.78 item 6: end of block, the false semicolon.
                self.fblend = True
                self.card = None
                self.ch = ";"
                return self.ch
            c = self.card[self.col]
            self.col += 1
            if c == " " and not self.gcaz:
                self.bsyst.append(c)
                continue
            self.bsyst.append(c)
            self.ch = c
            return c
