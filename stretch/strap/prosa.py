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
import iocd
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

# Where MCP's own words start inside the record, which is what
# LVS computes: the sum of the two "preceding" sizes.
MCP_AT = WORDS_BEFORE_MCP_A + WORDS_BEFORE_MCP_B

# ---------------------------------------------------------------------
# THE COMMUNICATION REGION, and its SIZE is not a choice
# ---------------------------------------------------------------------
# printed p.15 lines 17-24 are the five rows that use it:
#
#   X10   LVS,$9,$12,$11,$14         -COMPUTE NUMBER OF WORDS PRECEEDING
#         LVE,$8,X BUFER($9)         - GET (MCP)
#   X101  LC,$0,X BUFER+.32($9)      -GET SIZE OF COMM REGION
#         T,$0,X BUFER($9),S MCP     -MOVE COMM REGION
#         T,$10,X BUFER($9),0.0($8)  -PLACE MCP IN STORAGE
#
# so the word at buffer offset $9 is a DESCRIPTOR: bits 0-23 are the
# address MCP is placed at (LVE takes the address field of a half word
# as a value) and the 18-bit field at BIT 32 is the comm region's
# size, which LC loads into $0's count.
#
# >>> AND THE BIT-32 FIELD IS NOT A GUESS, because the region names
# itself.  printed p.34 line 29 is "LC,$14,S COMSZ  -GET SIZE OF MCP
# COMMUNIZIATION REGION" and S COMSZ is 002150.40 -- BIT 32 OF S MCP's
# WORD.  After "T,$0,X BUFER($9),S MCP" the descriptor IS S MCP's
# word, so the field printed p.15 reads out of the buffer and the
# field printed p.34 reads out of the comm region are the same field,
# read by the same instruction.  The fixture does not invent the
# layout; it puts the size where the program already looks. <<<
#
# >>> THE SIZE IS FIFTEEN WORDS, DERIVED.  Every communication-region
# symbol the twenty-two transcribed pages name, from
# mcp_image.build_mcp_ipl()'s symbol table:
#
#   S MCP    002150.00   S COMSZ  002150.40   S COM RG 002151.00
#   S X CHAN 002152.00   S BA MCP 002153.00   S R TAPE 002153.40
#   S W TAPE 002154.00   S READ R 002154.40   S LR BU  002155.00
#   S BA PP  002155.00   S MAX RN 002155.40   S YCO CH 002156.00
#   S YPR CH 002156.40   S DK MCP 002157.00   S SYRFT  002157.40
#   S PR IN  002160.00   S PR OUT 002160.40   S IF DMP 002161.00
#   S REJ JB 002161.40   S ROOF   002162.00   S MARK   002162.40
#   S IA     002163.00   Y UNCOD  002166.00
#
# >>> IT IS FOURTEEN, AND PRINTED p.37 SAYS SO IN ITS OWN COMPILED
# WORD.  THE DERIVATION BELOW WAS RIGHT IN METHOD AND WRONG BY ONE.
# <<<
#
# It read: "002150.00 through 002166.00 inclusive is 0o17 = FIFTEEN
# words, and that is the smallest region containing every one of them
# -- twenty-two symbols in fifteen words, mostly two to a word.  It is
# a LOWER BOUND read off the pages, not a number chosen to look round;
# a sixteenth word would be unreferenced and a fourteenth would cut
# Y UNCOD off."
#
# printed p.37 line 9 is
#
#     002150.40  000016.00+  S COM SZ  VF,S END CM-S MCP
#                            -SIZE OF COMMUNICATION REGION
#
# and 0o16 is FOURTEEN.  The one symbol the derivation had at
# 002166.00 is Y UNCOD, and p.37 lines 44-45 put S END CM and S PRIME
# there -- the END of the region and the PRIME ROUTINE's address,
# which is where MCP's initialization branches when it finishes.  So
# 002166.00 is one PAST the region, not the last word of it, and
# Y UNCOD names the routine rather than a datum in the table.
#
# A LOWER BOUND FROM USAGE CANNOT SEE THAT, and it is worth saying
# why: every symbol the derivation found was real and every address
# was right.  What it could not know is which side of the boundary
# the last one sits on, because an address used as a BRANCH TARGET
# and an address used as a TABLE SLOT look identical from the
# instruction that mentions them.  The size had to come from the
# program's own arithmetic, and p.37 line 9 is that arithmetic.
COMM_REGION_WORDS = 14

# Where the comm region sits in the record: immediately past the IPL
# image, which is what printed p.15 line 17's three-register LVS
# computes -- X12 + X11 + X14, the dictionary plus the IPL plus the
# index.
# ---------------------------------------------------------------------
# THE IOCD CARDS, AND WHY THEY FIX WHERE MCP IS PLACED
# ---------------------------------------------------------------------
# printed p.17 line 8 is "LVI,$4,X IN END  -END OF ASSEMBLED" and
# line 12 "LCI,$4,14  -TEST 14 WORDS FOR FIRST IOCD", so MCP hunts
# for its configuration cards at X IN END -- 005466.00, printed p.98
# line 36's "X IN END SYN,$" -- and printed p.13 line 38 reserves
# what follows: "X BUFER SYN, X IN END+2000.0", commented "SLOTS
# LEFT FOR IOCD + IODS".  Two thousand words of slots.
#
# THE CARDS ARE NOT READ FROM A 7503.  C22-6678-1 printed p.29's
# six-step operator procedure mounts the master system TAPE and no
# deck; the cards are card IMAGES the system build put on the tape.
# So they arrive the way everything else does -- in the PROSA record
# -- and the only question is how they get from the buffer to
# X IN END.
#
# >>> printed p.15 LINE 24 IS THE ANSWER, AND IT IS ALREADY THERE:
# "T,$10,X BUFER($9),0.0($8)  -PLACE MCP IN STORAGE".  It moves X10
# words from the same buffer offset the comm region came from to the
# address the descriptor names.  Put the cards at the END of that
# block and they land at the end of where MCP is placed -- which is
# what X IN END IS: the end of the assembled image. <<<
#
# So MCP's destination is no longer a free choice.  It is
#
#     MCP_DEST_WORD = X IN END - MCP_BODY_WORDS
#
# and the cards follow the body, so the first one lands exactly at
# X IN END and printed p.17's hunt finds it on its first test --
# line 13's "BB, 1.44($4)" is bit 108 of the group, which is where
# the IOCD identifier starts.
#
# CHOSEN: how long MCP's body is, and what is on the cards.  The
# body is the comm region's own length, because the comm region IS
# the start of the block (printed p.15 lines 21 and 24 move from the
# SAME source) and nothing in the transcribed pages reads anything
# between it and X IN END.
#
# >>> AND THE CARDS DESCRIBE THE MACHINE THE MODEL ACTUALLY IS, which
# is the whole point of an IOCD deck: "the IOCD cards define the
# distribution of I-O units at initializing time" (C22-6728 printed
# p.88).  Every channel below is one bsv/StretchIO.bsv presents:
#
#     channel  0  chanDisk     an IBM 7612 and a 353 disk
#     channel 32  chanReader   a card reader
#     channel 33  chanPrinter  a printer
#     channel 34  chanTape     a tape drive
#     channel 35  chanConsole  the console
#
# THE FIRST DECK HERE SAID CHANNEL 35 WAS A TAPE, and the run said
# so: MCP processed the card, presetting all sixty-four CST entries
# to not-available and marking 35 as tape, and then its error routine
# walked the channels looking for a console and found none -- so
# NOTHING WAS WRITTEN TO THE CONSOLE AT ALL, where the run before it
# had printed "NO IOCD DETECTED".  A configuration that lies about
# the machine makes MCP correct about the wrong machine.
#
# CHOSEN: the unit rows.  A tape channel carries units and printed
# p.18 walks their columns; the single-unit equipments are punched
# with none, which is how the list ends (line 14's BRZ on an
# unpunched column).
IOCD_CARDS = [
    # (channel, equipment, unit rows) -- see strap/iocd.py for what a
    # row means and for the field map's provenance.
    (0,  "DK", ()),
    (32, "RD", ()),
    (33, "PR", ()),
    (34, "TP", (2, 0)),
    (35, "CN", ()),
]

# >>> AND THE DECK IS TERMINATED BY AN IOD CARD, which is what ENDS
# the IOCD scan rather than an error. <<<
#
# printed p.17 line 31's BZAE sends a card that is not an IOCD to
# X19, printed p.19 line 23 asks whether it is an IOD instead, and
# line 25's "BZAEZ,X ERROR  -NOT AN IOD CARD EITHER" is where the
# run used to stop -- on a group of zeros, which is neither.  So one
# IOD card is the terminator, and C22-6728 printed p.88 lists the
# three control-card types in exactly that order: IOCD, IOD, MCPP.
#
# WHAT IS ON IT: the class column and the three characters of its
# type, and nothing else.  Printed p.19 does not read an IOD card's
# other fields -- after the compare succeeds it goes straight on to
# moving the unit status table -- so punching anything there would be
# inventing a format the pages do not state.
# >>> AND IT IS A REAL IOD CARD NOW, NOT A BLANK ONE. <<<
#
# It used to be `(None, None, (), iocd.IOD_CARD_TYPE)` -- every field
# blank but the card type -- present only to END the IOCD scan.  Three
# things say that cannot work, all from documents already in the corpus:
#
#   * `C22-6728-1` printed p.66: Uncode compares the first field against
#     its mask at `Y TYPMK`, and "if not, error return is given, and no
#     information is transmitted".  A card blank but for `B` in column 1
#     takes that error return and NEVER REACHES DECODE.  The guide even
#     uses such a card as deliberate filler elsewhere (printed p.166).
#   * `C22-6678-1` printed p.96: "The IOD cards define the I-O
#     requirements of MCP and perform the same function for MCP as they
#     do for the problem program."
#   * `C22-6728-1` printed p.98: IPL assignment is a MODIFIED
#     decode-assign-move, and its minimal case -- normal IPL,
#     unoverlapped -- needs IOD cards defining a card reader and output
#     tape units.
#
# THE FIELD POSITIONS ARE VERIFIED, not derived: `C22-6678-1` printed
# pp.7-10 prints the column ruler, and the cards MCP reads at IPL are
# STRAP II's OUTPUT cards, which carry columns 63-72 punched.  See
# strap/iocd.py's IOD section.
#
# WHAT IS STILL INVENTED, and labelled: the IODNAME and the ABSOLUTE
# EXIT.  The exit is "the first word address of the I/O table of exits
# to be used when an interrupt occurs for the logical unit", which is a
# location inside MCP that no transcribed page names.  It must be
# NON-ZERO -- the guide says "a zero address denotes the absence of an
# IOD card" -- so a plausible in-range stand-in is used and marked here.
MCP_IOD_EXIT = 0o4000          # INVENTED: a word address inside MCP

# >>> printed p.98's MINIMAL CASE NEEDS A READER AND OUTPUT TAPES. <<<
# "Normal IPL, Unoverlapped (BYPASS): The card reader is assigned to
# MCP ...  The output tape units are assigned to MCP and the necessary
# tables are constructed."  One reader IOD got MCP as far as counting a
# READER request; the tapes are the rest of that sentence.
#
# THE TAPE SUBFIELDS ARE VERIFIED from `C22-6678-1` printed p.10:
#   IOD, TAPE, exit, channel, unit, mode, density, disposition
# with mode in {ODD, EVEN, ECC, null}, density in {HD, LD, null} and
# disposition in {NSAVE, CSAVE, ISAVE, SAVE, PSAVE, NULL}.
#
# TWO TAPES, AND THE UNIT SYMBOLS ARE WHY.  The same page: "A tape unit
# will be assigned for each unique unit symbol ...  A different unit
# symbol on tape IOD cards unconditionally associates them with
# different tape units."  The fixture's IOCD deck gives channel 34 two
# units, so two distinct unit symbols ask for the two that exist.
#
# THE CHANNEL FIELD IS LEFT NULL on purpose: `C22-6678-1` printed p.96
# says the initializing program "will assign these symbolic requests to
# absolute units", so naming a channel here would be the fixture
# deciding what MCP is supposed to decide.
#
# REFERENCE NUMBERS ARE 1, 2, 3 IN DECK ORDER, which is the manual's
# own rule: "The first IOD card encountered has the number 1 punched in
# this field, the second IOD ...".
MCP_IODS = [
    dict(name="MCPRDR", iod_type="READER", exit_sym="XRDEXIT",
         subfields=(), ref_number=1, absolute_exit=MCP_IOD_EXIT),
    dict(name="MCPOUT1", iod_type="TAPE", exit_sym="XTPEXIT",
         subfields=("", "OUT1", "ODD", "HD", "SAVE"),
         ref_number=2, absolute_exit=MCP_IOD_EXIT),
    dict(name="MCPOUT2", iod_type="TAPE", exit_sym="XTPEXIT",
         subfields=("", "OUT2", "ODD", "HD", "SAVE"),
         ref_number=3, absolute_exit=MCP_IOD_EXIT),
]

TERMINATOR_CARD = (None, None, (), iocd.IOD_CARD_TYPE)


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

# printed p.15 line 17: "LVS,$9,$12,$11,$14" sums THREE counts -- the
# dictionary, the IPL and the index -- so the comm region starts
# exactly here.
COMM_AT = WORDS_BEFORE_MCP_A + IPL_WORDS + WORDS_BEFORE_MCP_B

# MCP's body: the comm region's own length -- see the IOCD note.
MCP_BODY_WORDS = COMM_REGION_WORDS
# +2: the IOD terminator and the MCPP card after it.  C22-6728 printed
# p.88 gives the order IOCD, IOD, MCPP, and MCP read the IOD and then
# reported X ERR 22, "INCORRECT CARD TYPE WITHIN IODS" (printed p.8
# line 14) -- it wanted the next legal card type and found none.
MCPP_MODE = "BYPASS"   # printed p.98 case 1: normal IPL, unoverlapped
CARD_WORDS = iocd.WORDS_PER_CARD * (len(IOCD_CARDS) + len(MCP_IODS) + 1)
# X10, "GET MCP SIZE": the body plus the cards, because printed p.15
# line 24 moves the whole block.
MCP_SIZE_WORDS = MCP_BODY_WORDS + CARD_WORDS
# DERIVED: the block has to END at X IN END plus its cards, so that
# the first card lands where printed p.17 line 8 points $4.
XINEND_WORD = mcp_image.build_mcp_ipl()[0].symtab["XINEND"] // 64
MCP_DEST_WORD = XINEND_WORD - MCP_BODY_WORDS
CARDS_AT = COMM_AT + MCP_BODY_WORDS   # inside the record

# A few words of filler past everything, so that a transmit which ran
# one word long would copy something recognisable rather than falling
# off the end of the record.
RECORD_WORDS = COMM_AT + max(COMM_REGION_WORDS, MCP_SIZE_WORDS) + 4

# A body word carries its own offset.  0x5A5A is a pattern no part of
# the bootstrap or the control words uses, so a stray one is obvious
# in a dump.
BODY_TAG = 0x5A5A000000000000


def body_word(offset):
    """The fixture word that belongs at buffer offset `offset`."""
    return BODY_TAG | offset


def comm_descriptor(mcp_dest_word, size_words):
    """The word at buffer offset COMM_AT -- see the long note above.

    bits  0-23  the address MCP is placed at, as a BIT address,
                because LVE takes the address field of a half word
                and printed p.15 line 24 then uses it as "0.0($8)"
    bits 32-49  the comm region's size in words, which is S COMSZ
    """
    return ((((mcp_dest_word * 64) & 0xFFFFFF) << 40)
            | ((size_words & 0x3FFFF) << 14))


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
    # The communication region, at the offset printed p.15 line 17's
    # three-register LVS computes.  Its FIRST word is the descriptor;
    # the rest keep their buffer-offset filler, because nothing in the
    # transcribed pages reads a value out of them -- they are read as
    # a block by the TRANSMIT and written field by field afterwards.
    # >>> THE COMM REGION IS THE DESCRIPTOR AND THEN ZEROS, and the
    # zeros are the point.  A tagged filler word here is not inert:
    # printed p.5 line 19 is "LV,$X1,S YCOCH  -GET CONSOLE CHANNEL
    # SLOT CONTENT" and line 20 "BZXVZ,X2AERR  -IF CHANNEL NUMBER
    # PRESENT", so a non-zero S YCOCH sends the error routine
    # straight to GONG on whatever channel it read instead of walking
    # the exchange to find one.  With filler there MCP believed in a
    # console on a channel made of 0x5A5A and printed NOTHING; with
    # zeros it walks, exactly as it does when no console has been
    # declared.
    #
    # S YCOCH is S MCP + 6 words, so this is not a hypothetical: the
    # region is fifteen words and the fixture was filling all of them.
    # NOTHING IN THE TRANSCRIBED PAGES SAYS WHAT THE REGION ARRIVES
    # CARRYING, so it arrives empty, which is also what a region the
    # program fills in looks like before it is filled. <<<
    for k in range(1, COMM_REGION_WORDS):
        words[COMM_AT + k] = 0
    words[COMM_AT] = comm_descriptor(MCP_DEST_WORD, COMM_REGION_WORDS)
    # The IOCD cards, at the end of the block printed p.15 line 24
    # places -- so they land at X IN END.
    deck = [(c, e, u, iocd.CARD_TYPE) for c, e, u in IOCD_CARDS]
    for _ in MCP_IODS:
        deck.append(TERMINATOR_CARD)
    deck.append((None, None, (), iocd.MCPP_CARD_TYPE))
    iod_n = 0
    for n, (channel, equipment, units, kind) in enumerate(deck):
        at = CARDS_AT + n * iocd.WORDS_PER_CARD
        if kind == iocd.MCPP_CARD_TYPE:
            cw = iocd.mcpp_card(MCPP_MODE)
        elif kind == iocd.IOD_CARD_TYPE:
            # the IOD cards, punched as STRAP II would emit them
            cw = iocd.iod_card(**MCP_IODS[iod_n])
            iod_n += 1
        else:
            cw = iocd.card(channel, equipment, units, card_type=kind)
        words[at:at + iocd.WORDS_PER_CARD] = cw
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
