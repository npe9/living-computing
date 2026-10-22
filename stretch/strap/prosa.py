#!/usr/bin/env python3
"""prosa.py -- a PROSA record for MCP's bootstrap to read off the tape.

>>> THIS IS A FIXTURE.  ITS SHAPE IS DERIVED; ITS CONTENTS ARE
>>> CHOSEN.  READ THE TWO SECTIONS BELOW BEFORE BELIEVING ANY NUMBER
>>> THAT COMES OUT OF A RUN THAT USED IT. <<<

MCP's real PROSA is the resident supervisor, and it lives in the
pages of `docs/MCP_Mar63_*.pdf` that are not transcribed -- which, as
of 2026-10-22, means printed p.37 onward: pp.2-36 ARE transcribed and
bit-exact, and printed p.37 starts a new source deck, "THE
COMMUNICATION REGION FOR MCP".  WITHOUT THIS FILE the bootstrap reads
its PROSA dictionary out of EMPTY TAPE -- `mktape.py` writes 369
bootstrap words and a tape mark and nothing else -- so every size it
reads comes back zero.  One consequence is
visible in the boot test: printed p.4 line 28's TRANSMIT takes its
count from a dictionary entry, zero means 2^18 (Reference Manual
printed p.30, "such a count is never valid"), and the transfer walks
off the top of installed core and stops with Address Invalid.

That was why printed pp.15-18 were transcribed bit-exactly and had
NEVER EXECUTED A SINGLE ROW.  This file is what lets them, and they
do: the boot test moves them to 000621.00 and runs them.

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
WHAT IS REAL -- the thing being moved
---------------------------------------------------------------------
**THE WORDS MCP MOVES ARE MCP.**  Printed pp.15-18 are transcribed
bit-exactly (`decks/mcp_bootstrap_p15.strap` through `p18`) and they
ASSEMBLE CONTIGUOUSLY AT 000621.00, which is X BS END -- printed
p.15 line 7 is `SLC,X BS END`.  Eighty words, every one of them set,
no gap and no overlap across the four pages.

That is also where printed p.4 line 28's TRANSMIT puts them.  So the
record carries the real image at the offset the dictionary names, and
the destination of the move is the address the code was assembled
for.  `IPL_WORDS` below is therefore DERIVED -- it is the image's
length -- and not chosen.

---------------------------------------------------------------------
WHAT IS CHOSEN -- the two offsets and the filler
---------------------------------------------------------------------
  * the two "preceding" sizes are 3 and 5, so MCP starts at buffer
    word 8 and the sum is not a round number either side;
  * the MCP size is 12, which nothing in the transcribed pages reads
    back -- it goes into X10 and stays there;
  * the FILLER around the image -- every word that is not the
    dictionary and not MCP -- carries ITS OWN BUFFER OFFSET in its
    low bits.

THAT LAST POINT IS STILL THE WHOLE DESIGN, and it does more work now
than when the body was filler end to end.  If the derivation in
section 1 is wrong by even one word, the move lands FILLER at X BS
END, and the check fails with `0x5A5A...0007` -- a value that says
which offset MCP actually computed.  Landing plausible-looking code
there instead would be a far worse failure, because it would look
like a working machine executing the wrong thing.

---------------------------------------------------------------------
WHEN TO DELETE THIS FILE
---------------------------------------------------------------------
When enough of the MCP listing is transcribed to assemble the real
PROSA record.  At that point the dictionary stops being chosen and
the sizes become facts, and any test that still imports this module
is testing the fixture.
"""
import mcp_image

# The record's own geometry.  Printed p.14's control words read it in
# 513-word chunks with a 512-word STRIDE, and `tape_words()` below is
# what that costs once the image is longer than one chunk.  The read
# ends in End Exception at the end of the tape -- which is what the
# bootstrap already handles as END OF PROSA FILE (printed p.4's
# X DONE).
#
# >>> THE COUNT AND THE STRIDE DIFFER BY ONE AND THAT IS NOT A
# TYPOGRAPHICAL ACCIDENT.  printed p.14 line 4 is
# "CW(CDSC),0+X BUFER,513,$+1.0" and line 5 is
# "CW(CDSC),512.+X BUFER,513,$+1.0": each control word reads 513
# words and the next one starts 512 words further into the BUFFER, so
# consecutive records OVERLAP BY ONE WORD -- the one-word header
# C22-6728 printed p.215 describes, read into the previous record's
# last word.
#
# THE FIXTURE WAS 92 WORDS AND NEVER SAW IT.  Extending the image to
# printed pp.15-36 made it 739, and the second control word then read
# tape word 513 into buffer offset 512 -- shifting every word after
# the first chunk down by one.  The boot test said so exactly: the
# word that should have held the image's last word held the fixture
# filler tagged 735 instead of 734, which is the off-by-one with its
# own offset written in it.  That is what BODY_TAG is for. <<<
CHUNK_COUNT  = 513            # printed p.14, every control word
CHUNK_STRIDE = 512            # printed p.14, line 5 minus line 4
DICT_AT = (1, 3, 5, 7)        # derived: see section 1

# Chosen sizes, in words.
WORDS_BEFORE_MCP_A = 3        # X12, "GET DICTIONARY"
WORDS_BEFORE_MCP_B = 5        # X14, "GET INDEX"
MCP_SIZE_WORDS     = 12       # X10, "GET MCP SIZE"

# Where MCP's own words start inside the record, which is what
# LVS computes: the sum of the two "preceding" sizes.
MCP_AT = WORDS_BEFORE_MCP_A + WORDS_BEFORE_MCP_B


def mcp_ipl_image():
    """Printed pp.15-36, assembled: (first_word_address, [words]).

    Contiguous by construction -- printed p.15 line 7 is
    `SLC,X BS END` and every page after it starts where the one
    before it ended -- and this asserts it rather than assuming it,
    because a hole would silently become a zero word in the record
    and a zero half-word is BRANCH ENABLED to location zero.

    >>> A RESERVATION IS THE ONE LEGITIMATE HOLE, and it is PROVED
    rather than allowed.  printed p.21's "X LR IN DR(BU),(3)" and
    "X ZEROS DR(BU),(3)" leave 001034-001041 empty and printed p.36's
    "X MSG BK DR(BU),(100)" leaves 002000-002143; DR emits nothing
    because the storage is meant to be left as the loader found it.
    The assembler records every DR's range, so this function can
    require that the set of missing words is EXACTLY the set of
    reserved ones -- a transcription that lost a word still fails,
    and a reservation no longer has to be special-cased by address.

    The reserved words go into the record as ZEROS, which is what the
    loader leaves in freshly cleared core, and that choice is checked
    by the one thing that would notice: X MSG BK is a message block
    MCP fills, and X LR IN is a buffer it reads only after writing. <<<
    """
    prog, _, _, _ = mcp_image.build_mcp_ipl()
    lo, hi = min(prog.words), max(prog.words)
    reserved = prog.reserved_words()
    missing = {a for a in range(lo, hi + 1) if a not in prog.words}
    if missing != reserved:
        lost = sorted(missing - reserved)
        spare = sorted(reserved - missing)
        raise SystemExit(
            "prosa.py: printed pp.15-36 do not account for every word.\n"
            + (f"  words MISSING with no reservation: "
               f"{[f'{a:06o}' for a in lost]}\n" if lost else "")
            + (f"  words RESERVED but present: "
               f"{[f'{a:06o}' for a in spare]}\n" if spare else "")
            + "  a missing word reads as zero, and a zero half word is "
              "BRANCH ENABLED to location zero")
    return lo, [prog.words.get(a, 0) for a in range(lo, hi + 1)]


MCP_IPL_AT, MCP_IPL_WORDS = mcp_ipl_image()
IPL_WORDS = len(MCP_IPL_WORDS)   # X11, "GET IPL" -- the TRANSMIT's
                                  # count.  DERIVED: the image's length.

# A few words of filler past the image, so that a transmit which ran
# one word long would copy something recognisable rather than falling
# off the end of the record.
RECORD_WORDS = MCP_AT + IPL_WORDS + 4

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
    # MCP's own image, at the offset the dictionary names.
    words[MCP_AT:MCP_AT + IPL_WORDS] = MCP_IPL_WORDS
    return words


def tape_words(buf=None):
    """The record as it must be WRITTEN TO TAPE for printed p.14's
    control words to assemble `buf` at X BUFER.

    Control word n reads CHUNK_COUNT words into buffer offsets
    [CHUNK_STRIDE*n, CHUNK_STRIDE*n + CHUNK_COUNT - 1], so the tape
    carries each boundary word TWICE -- once as the last word of one
    chunk and once as the first of the next.  Writing the buffer
    image out flat instead puts every word after the first chunk one
    place too early.
    """
    if buf is None:
        buf = record()
    out, n = [], 0
    while CHUNK_STRIDE * n < len(buf):
        out.extend(buf[CHUNK_STRIDE * n:CHUNK_STRIDE * n + CHUNK_COUNT])
        n += 1
    return out


if __name__ == "__main__":
    ws = record()
    print(f"{len(ws)} words; MCP's own words start at buffer offset "
          f"{MCP_AT}, and {IPL_WORDS} of them -- printed pp.15-18, "
          f"assembled at {MCP_IPL_AT:#o} -- move to X BS END")
    for i, w in enumerate(ws):
        if i in DICT_AT:
            kind = "DICTIONARY"
        elif MCP_AT <= i < MCP_AT + IPL_WORDS:
            kind = f"MCP {MCP_IPL_AT + i - MCP_AT:06o}"
        else:
            kind = ""
        print(f"  +{i:2d}  {w:016x}  {kind}")
