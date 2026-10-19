#!/usr/bin/env python3
"""prosa.py -- a PROSA record for MCP's bootstrap to read off the tape.

>>> THIS IS A FIXTURE.  ITS SHAPE IS DERIVED; ITS CONTENTS ARE
>>> CHOSEN.  READ THE TWO SECTIONS BELOW BEFORE BELIEVING ANY NUMBER
>>> THAT COMES OUT OF A RUN THAT USED IT. <<<

MCP's real PROSA is the resident supervisor, and it lives in the 451
pages of `docs/MCP_Mar63_*.pdf` that are not transcribed.  Until they
are, the bootstrap reads its PROSA dictionary out of EMPTY TAPE --
`mktape.py` writes 369 bootstrap words and a tape mark and nothing
else -- so every size it reads comes back zero.  One consequence is
visible in the boot test: printed p.4 line 28's TRANSMIT takes its
count from a dictionary entry, zero means 2^18 (Reference Manual
printed p.30, "such a count is never valid"), and the transfer walks
off the top of installed core and stops with Address Invalid.

So printed pp.15-18 are transcribed bit-exactly and HAVE NEVER
EXECUTED A SINGLE ROW.  This file is what lets them.

---------------------------------------------------------------------
WHAT IS DERIVED -- the record's SHAPE, read off transcribed rows
---------------------------------------------------------------------
MCP printed p.4 lines 19-27, which `decks/mcp_bootstrap_p4.strap`
reproduces bit-for-bit against the listing:

    X9 A 4   LX,$X12,X BUFER+1.0        - GET DICTIONARY
             SC,$X12,$X12
             LX,$X14,X BUFER+3.0        -GET INDEX
             SC,$X14,$X14
             LVS,$X1,$X12,$X14          -WORDS PRECEEDING MCP
             LX,$X11,X BUFER+5.0        - GET IPL
             SC,$X11,$X11
             LX,$X10,X BUFER+7.0        -GET MCP SIZE
             SC,$X10,$X10
    X9 A 5   T,$11,X BUFER($X1),X BS END   -MOVE MCP IPL

Four facts follow, and none of them is a guess:

1. THE DICTIONARY IS INDEX WORDS AT ODD OFFSETS from the start of the
   record -- +1, +3, +5, +7 -- because `LX` loads a whole index word
   and those are the four addresses it loads from.  What sits at the
   even offsets is not known from these rows and is filler here.

2. THE SIZES ARE IN THE COUNT FIELDS.  `SC` stores the count field of
   index J into bits 0-17 of the addressed HALF-WORD
   (`StretchExecute.bsv`'s `dixop_SC`: `nh = {x.count, 7'b0,
   h[6:0]}`), and the address is the index's OWN word -- so
   `SC,$X12,$X12` moves X12's count into X12's value and leaves the
   count field itself untouched, because bits 28-45 lie outside the
   bits that write rewrites.

3. AND THAT MOVE IS A UNIT CONVERSION, which is why the idiom exists.
   The value field is a 24-bit BIT address; bits 0-17 of it are the
   WORD part.  A count of n lands as a value of n words.  `LVS` then
   sums two of them and the listing's own comment on that row is
   "WORDS PRECEEDING MCP" -- so X1 is an offset in words, expressed
   as a bit address, ready to index `X BUFER($X1)`.

4. THE TRANSMIT'S COUNT IS X11'S, THE "GET IPL" ENTRY.  `T,$11,...`
   is a DIRECT count (Reference Manual printed p.30: "the field J...
   specifies an index register.  The count field, bits 28-45, of the
   index word in this register is used as a full word count"), and
   `SC` left that field alone.

---------------------------------------------------------------------
WHAT IS CHOSEN -- every number below
---------------------------------------------------------------------
The four sizes and the body words are invented.  They are picked to
be SMALL and DISTINGUISHABLE, not to resemble MCP:

  * the two "preceding" sizes are 3 and 5, so MCP starts at buffer
    word 8 and the sum is not a round number either side;
  * the IPL size is 6, so the move is short enough to check word by
    word and long enough that an off-by-one shows;
  * the MCP size is 12, which nothing in the transcribed pages reads
    back -- it goes into X10 and stays there;
  * every body word CARRIES ITS OWN BUFFER OFFSET in its low bits,
    so a check after the move does not have to trust this file's
    arithmetic: it reads the offset out of the moved word and
    compares it with the one MCP computed.

THAT LAST POINT IS THE WHOLE DESIGN.  A fixture that only proved the
machine copied *something* would be worth little.  This one makes the
destination say WHICH source words arrived, so if the derivation in
section 1 is wrong the check fails with the actual offset in hand.

---------------------------------------------------------------------
WHEN TO DELETE THIS FILE
---------------------------------------------------------------------
When enough of the MCP listing is transcribed to assemble the real
PROSA record.  At that point the dictionary stops being chosen and
the sizes become facts, and any test that still imports this module
is testing the fixture.
"""

# The record's own geometry.  Printed p.14's control words read it in
# 513-word chunks with a 512-word stride; this record is far shorter
# than one chunk, so the read ends in End Exception at the end of the
# tape -- which is what the bootstrap already handles as END OF PROSA
# FILE (printed p.4's X DONE).
DICT_AT = (1, 3, 5, 7)        # derived: see section 1

# Chosen sizes, in words.
WORDS_BEFORE_MCP_A = 3        # X12, "GET DICTIONARY"
WORDS_BEFORE_MCP_B = 5        # X14, "GET INDEX"
IPL_WORDS          = 6        # X11, "GET IPL"  -- the TRANSMIT's count
MCP_SIZE_WORDS     = 12       # X10, "GET MCP SIZE"

# Where MCP's own words start inside the record, which is what
# LVS computes: the sum of the two "preceding" sizes.
MCP_AT = WORDS_BEFORE_MCP_A + WORDS_BEFORE_MCP_B

RECORD_WORDS = 24             # chosen: comfortably past MCP_AT+IPL_WORDS

# A body word carries its own offset.  0x5A5A is a pattern no part of
# the bootstrap or the control words uses, so a stray one is obvious
# in a dump.
BODY_TAG = 0x5A5A000000000000


def body_word(offset):
    """The fixture word that belongs at buffer offset `offset`."""
    return BODY_TAG | offset


def index_word(value=0, sign=0, flag=0, spare=0, count=0, refill=0):
    """Mirrors StretchTypes.bsv's packIndexWord field for field:
    addr 0-23, sign 24, flag 25, spare 26-27, count 28-45, refill 46-63."""
    return (((value & 0xFFFFFF) << 40) | ((sign & 1) << 39)
            | ((flag & 1) << 38) | ((spare & 3) << 36)
            | ((count & 0x3FFFF) << 18) | (refill & 0x3FFFF))


def record():
    """The PROSA record, as a list of 64-bit words.

    Word 0 of this list lands at X BUFER, because printed p.14's first
    control word is `CW(CDSC),0+X BUFER,513,$+1.0`.
    """
    words = [body_word(i) for i in range(RECORD_WORDS)]
    sizes = (WORDS_BEFORE_MCP_A, WORDS_BEFORE_MCP_B,
             IPL_WORDS, MCP_SIZE_WORDS)
    for offset, n in zip(DICT_AT, sizes):
        words[offset] = index_word(count=n)
    return words


if __name__ == "__main__":
    ws = record()
    print(f"{len(ws)} words; MCP's own words start at buffer offset "
          f"{MCP_AT}, and {IPL_WORDS} of them move to X BS END")
    for i, w in enumerate(ws):
        kind = "DICTIONARY" if i in DICT_AT else ""
        print(f"  +{i:2d}  {w:016x}  {kind}")
