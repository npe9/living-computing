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


# ---------------------------------------------------------------------
# THE IOD CONTROL CARD
# ---------------------------------------------------------------------
# `C22-6678-1` printed pp.7-10, read from docs/ocr/ and verified line by
# line (lines 794-796, 826-845, 863-868, 885-900).  The column map is
# printed on the page as a ruler over each of the four card classes:
#
#     1 | 2-9      | 10-62                   | 63-66     | 67-72    | 73-80
#     B | IODNAME  | IOD, type, exit, chan.. | I/O Ref # | Abs Exit | prog id
#
# and the manual's own words for the two right-hand fields:
#
#   "(column 63-66) and the absolute exit field (columns 67-72), Thus,
#    when writing an IOD statement, the programmer can use only columns
#    1-62."
#
#   "I/O Reference Number: Columns 63-66 are left blank by the problem
#    program.  On the output IOD cards, STRAP II converts the IODNAME to
#    an absolute number and punches this four-digit octal number in this
#    field.  The first IOD card encountered has the number 1 punched in
#    this field."
#
# >>> SO THE CARDS MCP READS AT IPL ARE *OUTPUT* CARDS AND DO CARRY
# 63-72 PUNCHED. <<<  A deck that leaves them blank is a deck of cards
# as a programmer typed them, not as STRAP II emitted them, and MCP
# reads the latter.
#
# THE STATEMENT IS COMMA-DELIMITED, NOT FIXED-COLUMN.  C22-6728-1
# printed p.66 defines a field as "a collection of characters, none of
# which is a comma, bounded on the left by a comma or column 9 of a
# card, and on the right by a comma or column 63 of a card", and
# "commas separate the statement field into subfields that are subject
# to a right-to-left drop-out" -- so trailing empty subfields may simply
# be omitted.
#
# TYPE must be one of the seven the page lists.
IOD_TYPES = ("PRINTER", "CONSOLE", "DISK", "TRACK", "TAPE",
             "READER", "PUNCH")

# The four classes and their subfields after `IOD, type, exit`:
#   PRINTER / CONSOLE : channel
#   READER  / PUNCH   : channel, mode            (ECC | NOECC; null = NOECC)
#   DISK    / TRACK   : channel, number          (arcs or tracks)
#   TAPE              : channel, unit, mode, density, disposition
# >>> THE SUBFIELD SEPARATOR MCP READS IS PUNCHED 0-3-8, NOT 4-8, AND
# THAT IS MEASURED. <<<
#
# `C22-6728-1` printed p.66 defines a statement field as "a collection
# of characters, none of which is a comma", and `C22-6678-1` printed p.7
# says "commas separate the statement field into subfields".  So the
# separator is a comma -- and the question is which PUNCHES MCP's own
# SCA6 converts into the character SBRK8 breaks on.
#
# cards.py's table, from `C22-6678` Appendix F, gives comma = 4-8 and
# quote = 0-3-8, and flags these two as "precisely the slots where the
# conventional commercial code and the 7030's 48-character set
# disagree".  MEASURED ON THE MODEL, running MCP's own SCA6 and SBRK8
# over a punched card:
#
#   separator 4-8   (Appendix F's comma) -> YUCBF2 field 1 = "IOD-READ"
#                   eight characters, the separator rendered as a dash,
#                   the field never broken, SBRK8's eight-character
#                   limit exceeded, Uncode error return, and MCP typed
#                   X ERR 22 "INCORRECT CARD TYPE WITHIN IODS"
#
#   separator 0-3-8 (Appendix F's quote) -> YUCBF2 fields 1,2,3 =
#                   "IOD", "READER", "XRDEXIT"
#
# The second is what a comma is supposed to do.  **MCP's own behaviour
# is the authority for running MCP**, so the separator here is the
# character cards.py calls a quote, and the disagreement with Appendix F
# is recorded rather than resolved -- cards.py is NOT changed, because
# tests/verify_c22_6678_appendix_f.py pins it to the manual and the
# manual is still what the manual says.
#
# WHICH OF THE THREE IS WRONG IS OPEN: our reading of Appendix F, or
# Appendix F itself, or SCA6's table being a keypunch convention away
# from the manual's.  Rendering Appendix F is on the queue in
# docs/source_audit.md.
IOD_SUBFIELD_SEPARATOR = "'"   # punches 0-3-8; see above
IOD_NAME_COLUMNS = (2, 9)        # inclusive, 1-based
IOD_STATEMENT_COLUMNS = (10, 62)
IOD_REF_COLUMNS = (63, 66)
IOD_EXIT_COLUMNS = (67, 72)


def iod_card_text(name, iod_type, exit_sym="", subfields=(),
                  ref_number=1, absolute_exit=0, tag=CLASS_COLUMN):
    """The eighty columns of one *output* IOD card, as text.

    name           the IODNAME, columns 2-9, at most eight characters
    iod_type       one of IOD_TYPES
    exit_sym       the problem-program symbol naming the I/O table of
                   exits; may be blank on a card STRAP II has already
                   resolved into `absolute_exit`
    subfields      the remaining statement subfields for this class, in
                   order; trailing empty ones may be omitted entirely
                   (the page's right-to-left drop-out)
    ref_number     the I/O reference number, punched as FOUR OCTAL
                   DIGITS in columns 63-66
    absolute_exit  the first word address of the I/O table of exits,
                   punched as SIX OCTAL DIGITS in columns 67-72
    """
    if iod_type not in IOD_TYPES:
        raise ValueError(
            f"IOD type {iod_type!r} is not one of {IOD_TYPES} "
            f"(C22-6678-1 printed p.8)")
    if len(name) > 8:
        raise ValueError(f"IODNAME {name!r} exceeds columns 2-9")
    # exit_sym=None means "type field only, no comma-separated
    # subfields at all" -- see strap/prosa.py's TERMINATOR_IOD.
    if exit_sym is None and not subfields:
        parts = [IOD_CARD_TYPE]
    else:
        parts = [IOD_CARD_TYPE, iod_type, exit_sym or ""] + [str(x) for x in subfields]
    while parts and parts[-1] == "":
        parts.pop()                      # right-to-left drop-out
    statement = IOD_SUBFIELD_SEPARATOR.join(parts)
    lo, hi = IOD_STATEMENT_COLUMNS
    if len(statement) > hi - lo + 1:
        raise ValueError(
            f"statement {statement!r} is {len(statement)} characters; "
            f"columns {lo}-{hi} hold {hi - lo + 1}")
    cols = [" "] * 80
    cols[0] = tag
    for i, ch in enumerate(name):
        cols[IOD_NAME_COLUMNS[0] - 1 + i] = ch
    for i, ch in enumerate(statement):
        cols[lo - 1 + i] = ch
    ref = "%04o" % ref_number
    if len(ref) != 4:
        raise ValueError(f"reference number {ref_number} needs four octal digits")
    for i, ch in enumerate(ref):
        cols[IOD_REF_COLUMNS[0] - 1 + i] = ch
    ex = "%06o" % absolute_exit
    if len(ex) != 6:
        raise ValueError(f"absolute exit {absolute_exit} needs six octal digits")
    for i, ch in enumerate(ex):
        cols[IOD_EXIT_COLUMNS[0] - 1 + i] = ch
    return "".join(cols)


def iod_card(*a, **k):
    """One output IOD card as WORDS_PER_CARD 64-bit words."""
    return card_words(iod_card_text(*a, **k))


# ---------------------------------------------------------------------
# THE MCPP CARD -- MCP Parameters
# ---------------------------------------------------------------------
# Two documents agree, and both are in docs/ocr/:
#
#   `C22-6728-1` printed p.96 (lines 15586, 15633-15643):
#     "3. MCP Parameters (MCPP)"
#     "Cols. 10-13 -- Card Type: contains the characters MCPP."
#     "Cols. 14-17 -- Mode: defines the mode in which ..."
#         OFFLINE
#         ONLINE  - On-line overlapped
#         BYPASS  - Bypass (Unoverlapped)
#
#   `C22-6678-1` (lines 5079-5091):
#     "The MCPP card must be made by the installation.  The MCPP card
#      determines the normal mode ...  The format of the MCPP card is as
#      follows:  B MCPP'mode'   Where 'MODE' is one of the following:
#      BYPASS, ..."
#
# >>> "COLS. 14-17" AND THE KEYWORDS DO NOT FIT EACH OTHER, and this
# code does not pretend to resolve it. <<<  BYPASS is six characters,
# ONLINE six, OFFLINE seven; none fits four columns.  `C22-6678-1`'s
# `B MCPP'mode'` reads as "the mode simply follows MCPP", which is also
# how the statement field works everywhere else (comma- or
# blank-delimited, columns 10-62).  So the mode is placed STARTING at
# column 14 and allowed its natural length -- which satisfies both
# readings as to where it begins.  `C22-6728-1` printed p.96 is on the
# render queue in docs/source_audit.md to settle the width.
MCPP_CARD_TYPE = "MCPP"
MCPP_MODES = ("OFFLINE", "ONLINE", "BYPASS")
MCPP_MODE_COLUMN = 14


def mcpp_card_text(mode, tag=CLASS_COLUMN):
    """The eighty columns of one MCPP card, as text."""
    if mode not in MCPP_MODES:
        raise ValueError(
            f"MCPP mode {mode!r} is not one of {MCPP_MODES} "
            f"(C22-6728-1 printed p.96)")
    cols = [" "] * 80
    cols[0] = tag
    for i, ch in enumerate(MCPP_CARD_TYPE):
        cols[9 + i] = ch                      # columns 10-13
    for i, ch in enumerate(mode):
        cols[MCPP_MODE_COLUMN - 1 + i] = ch   # from column 14
    return "".join(cols)


def mcpp_card(*a, **k):
    """One MCPP card as WORDS_PER_CARD 64-bit words."""
    return card_words(mcpp_card_text(*a, **k))
