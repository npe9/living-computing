#!/usr/bin/env python3
"""iocd.py -- an IOCD card, punched.

MCP's I-O configuration arrives on CARDS, and printed p.17 searches
for them in core rather than reading a 7503: `C22-6678-1` printed
p.29's six-step operator procedure mounts the master system TAPE and
no deck, and printed p.13 line 38 names the two thousand words above
X IN END "SLOTS LEFT FOR IOCD + IODS".  So the cards are card IMAGES
placed on the system tape when the system was built, and anything
that wants MCP to find a device has to punch one.

>>> ONE DEFINITION, TWO USERS.  tests/gen_mcp_p17_tb.py punches a
card into a synthetic buffer so printed p.17 can be executed on its
own; strap/prosa.py punches cards into the PROSA record so the REAL
boot finds them at X IN END.  Before this module existed only the
first had a card and the second could not have agreed with it. <<<

---------------------------------------------------------------------
THE FIELD MAP IS PRINTED, and it was DERIVED first
---------------------------------------------------------------------
`C22-6728` printed p.88 = PDF p.88, "The Initialization Program /
Control Cards":

  "I-O Configuration Definitions:  The IOCD cards define the
   distribution of I-O units at initializing time.  Each card
   describes a channel. ... The IOCD cards, which do not have to be
   in order of channel number, have the following fixed fields:
   Cols. 10-13 -- Card Type: contains the characters, IOCD.
   Cols. 14-15 -- Channel Number: contains the decimal number of the
                  channel.
   Cols. 16-17 -- Equipment: must contain one of the following
                  codes:   CN Console   DK Disk   PR Printer
                           PU Punch     TP Tape   RD Reader"

and every one of those agrees with what printed p.17's own
progressive increments had already given -- see
tests/gen_mcp_p17_tb.py's header, which derived the map from the
instructions that walk it before the manual's page was found.

TWO THINGS THE MANUAL DOES NOT SAY and the program does:

  * COLUMN 1 IS A CLASS CHARACTER.  Every MCP control card carries
    one (`C22-6678-1` printed p.8) and printed p.17 line 26's
    CT0111 reads eight bits at offset 0 before anything else.
  * COLUMN 18 IS THE CHANNEL-AVAILABLE FLAG AND IT IS ACTIVE-LOW.
    printed p.17 line 43's "BB" branches AWAY, past line 44, when
    the card's bit is ONE; line 44 -- commented "-YES * CHANNEL
    AVAILABLE FLAG TO ON" -- runs only when it is ZERO.  So a
    channel that IS available is punched with the zone row 12 left
    out, and this module's default is an available channel.
  * COLUMNS 19 ONWARD ARE ONE PER UNIT.  printed p.18 line 13's
    "CT0011(V+I)(BU,12), .12($4)" reads twelve bits and advances
    twelve -- one column per unit -- and line 14's BRZ ends the list
    on an unpunched column.

---------------------------------------------------------------------
WHAT IS STILL INVENTED
---------------------------------------------------------------------
WHICH ROW a unit is punched on.  printed p.18 routes a unit two ways
depending on a bit of the column it reads, and the row that selects
each route is a reading of the code rather than of a document.  The
callers pass rows explicitly for that reason, and the testbench's
header says which measurement each row is there to make.
"""
from cards import card_words, WORDS_PER_CARD

CLASS_COLUMN = "B"      # column 1 -- C22-6678-1 printed p.8
CARD_TYPE = "IOCD"      # columns 10-13 -- C22-6728 printed p.88
FIRST_UNIT_COLUMN = 18  # zero-based; column 19 in the manual's count

# >>> AN IOD CARD'S TYPE IS THREE COLUMNS AND IT IS LEFT-JUSTIFIED IN
# THE SAME FIELD, which the comparison settles.  printed p.17 line 27
# loads FORTY-EIGHT bits of the card-type field into the accumulator
# and line 30 compares all of them against X IOCD; printed p.19 line
# 23 is "KF(BU,36),X IOD,12" -- thirty-six bits with an OFFSET of 12.
#
# Reference Manual printed p.65, COMPARE: "The contents of the
# accumulator LEFT OF THE SPECIFIED OFFSET are algebraically compared
# with the addressed operand.  The bits to the right of the offset do
# not participate in the comparison."  Twelve bits is one card column,
# so the compare is the FIRST THREE columns of the field -- 10, 11
# and 12 -- and column 13 is ignored.
#
# The two literals agree: X IOCD is 48 bits at 001747.60 and X IOD is
# 36 at 001750.40, which is 001747.60 plus 48.  Four columns and
# three, end to end, both starting at column 10 of their card.
IOD_CARD_TYPE = "IOD"


def card_text(channel, equipment, units=(), available=True,
              card_type=CARD_TYPE, tag=CLASS_COLUMN):
    """The eighty columns of one control card, as text.

    channel    the decimal channel number, two columns
    equipment  the two-letter code -- CN DK PR PU TP RD
    units      one entry per unit column, each the ROW to punch
               ("+" for row 0, "0" for row 2; see the module note)
    available  False punches the zone row in column 18, which printed
               p.17 line 43 reads as NOT available
    """
    cols = [" "] * 80
    cols[0] = tag
    for i, ch in enumerate(card_type):
        cols[9 + i] = ch
    # channel and equipment are None on a card whose other fields
    # nothing in the transcribed pages reads -- see card_type below.
    if channel is not None:
        cols[13], cols[14] = "%02d" % channel
    if equipment is not None:
        cols[15], cols[16] = equipment
    if not available:
        cols[17] = "+"
    for k, row in enumerate(units):
        cols[FIRST_UNIT_COLUMN + k] = "+" if row == 0 else "0"
    return "".join(cols)


def card(channel, equipment, units=(), available=True,
         card_type=CARD_TYPE, tag=CLASS_COLUMN):
    """One card as WORDS_PER_CARD 64-bit words."""
    return card_words(card_text(channel, equipment, units, available,
                                card_type, tag))


if __name__ == "__main__":
    text = card_text(35, "TP", units=(2, 0))
    print("columns:", repr(text[:24]), "...")
    for i, w in enumerate(card(35, "TP", units=(2, 0))):
        print("  word %2d  %016X" % (i, w))
    print("%d words per card" % WORDS_PER_CARD)
