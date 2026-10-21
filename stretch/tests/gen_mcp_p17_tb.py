#!/usr/bin/env python3
"""gen_mcp_p17_tb.py -- run the REAL transcribed printed p.17 against
a synthetic IOCD card.

decks/mcp_bootstrap_p17.strap is checked bit-for-bit against the
listing by verify_mcp_bootstrap_p17.py and has never executed a row.
This runs it: not a paraphrase of the page, the page.

WHY A TESTBENCH OF ITS OWN rather than letting the MCP boot test
reach p.17.  gen_tb's `ipl=True` path deliberately preloads NOTHING
-- "core storage starts empty and the tape fills it" -- because
preloading would let the boot test pass even if the IPL read moved
nothing.  The IOCD cards, X IOCD's pattern and the equipment table
live at addresses the transcribed tape does not carry (they are on
untranscribed pages), so putting them in core means preloading, and
preloading them into THAT test would weaken the one invariant it
exists to protect.  Here there is no IPL and nothing to undermine.

WHAT IS DERIVED AND WHAT IS INVENTED, the same split prosa.py makes:

  DERIVED -- the card's field map, read off p.17's own progressive
  increments (see decks/mcp_p17_card.strap and docs/boot_plan.md A3):
  card type at 0, the 48-bit IOCD identifier at 108, the tens column
  at 158, the units at 170, the equipment letter at 192, the
  channel-available bit at 204.  The hunt's "BB, 1.44($4)" tests bit
  108 -- the identifier's leading bit -- and "CB+" steps one word.
  The equipment table's 29-bit entries are derived the same way.

  AND THE GEOMETRY IS NOW CORROBORATED FROM OUTSIDE MCP, which
  matters because the map and the stride were both derived from the
  SAME page's increments.  C22-6728 printed p.215 says information on
  the master tape "is written in column binary card image", and a
  column-binary card image is 80 columns of 12 rows = 960 bits =
  fifteen 64-bit words = p.18 line 43's "V+I, $13, 15.0".  Printed
  p.216 shows MCP's control cards with a tag in column 1 and the
  operation field starting in COLUMN 10.  Divide p.17's offsets by
  twelve and every one of them lands on a column:

      0    col 1              the tag field
      108  cols 10-13         FOUR columns = four characters, "IOCD"
      158  col 14 rows 0-6    the digit rows of a tens digit
      170  col 15 rows 0-9    the digit rows of a units digit
      192  col 17             one column = one character
      204  col 18 row 12      a zone punch
      216+ cols 19, 20, ...   one column per unit

  Nothing in p.17 says "column" and the number 12 never appears on
  it.  This also explains line 13's comment "-IF ZONE BIT OF IOCD":
  bit 108 is column 10 ROW 12, the zone row, and column 10 holds the
  "I".  The hunt finds a card by testing the zone punch of a letter.

  AND X IOCD'S PATTERN HAS NOW CROSSED THE LINE TOO.  It is no longer
  a constant chosen to have its top bit set; it is the four
  characters IOCD punched through C22-6678-1 printed p.56's Appendix
  F and packed in printed p.138's bit order -- 0x801408840820 -- and
  its top bit is set because "I" is 12-9, a 12-zone letter.  That is
  what line 13's "-IF ZONE BIT OF IOCD" is testing.

  INVENTED -- the card's remaining CONTENTS and the equipment
  table's ten entries.  All three live on pages nobody has
  transcribed; they are chosen here only to be consistent with each
  other.  Nothing this test reports is evidence about what a real
  IOCD card looked like.

THREE HALTS ARE PLANTED, and they are the fixture's other half.  The
page runs off its own end into p.18, and branches to X 19 and
X ERROR, none of which is in this deck.  A "BEW,$" at each turns
those into distinguishable stopping points, so the PC says which exit
the page took -- the same shape as the three exits in
decks/mcp_p17_card.strap.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "strap"))

from gen_tb import generate
from strap_asm import assemble, AssemblerError
from cards import column_bits, card_words, WORDS_PER_CARD

DECKS = [os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      os.pardir, "decks", "mcp_bootstrap_p%d.strap" % n)
         for n in (17, 18, 19)]
DECK = DECKS[0]

CARD_AT_WORD = 3          # the card sits three words into the buffer,
                          # so the hunt has to step to find it
CHANNEL  = 35             # what columns 14-15 spell
EQP_CODE = 6              # the 4-bit code the matching table entry carries

# >>> THE IOCD CARD'S COLUMN FORMAT IS PRINTED, and this fixture now
# punches a real one.  C22-6728 printed p.88 = PDF p.88, "The
# Initialization Program / Control Cards": <<<
#
#   "I-O Configuration Definitions:  The IOCD cards define the
#    distribution of I-O units at initializing time.  Each card
#    describes a channel. ... The IOCD cards, which do not have to be
#    in order of channel number, have the following fixed fields:
#      Cols. 10-13 -- Card Type: contains the characters, IOCD.
#      Cols. 14-15 -- Channel Number: contains the decimal number of
#                     the channel.
#      Cols. 16-17 -- Equipment: must contain one of the following
#                     codes:   CN Console   DK Disk   PR Printer
#                              PU Punch     TP Tape   RD Reader"
#
# Every one of those agrees with what p.17's increments had already
# given: four columns of keyword at 10-13, two channel digits at
# 14-15, and a TWO-LETTER equipment code at 16-17 of which line 46
# reads the SECOND letter.  The page also says "there must be one
# card for each channel physically in the system WHETHER THAT CHANNEL
# IS AVAILABLE OR NOT", which is the availability flag line 43 tests.
#
# AND IT EXPLAINS WHY ONE COLUMN IS ENOUGH: the six codes' second
# letters are N, K, R, U, P and D -- all distinct.  MCP never needs
# the first letter.
EQUIPMENT_CODES = ["CN", "DK", "PR", "PU", "TP", "RD"]
CARD_EQUIPMENT  = "TP"    # Tape -- see below for why it must be tape
LETTER = column_bits(CARD_EQUIPMENT[1])

# (letter column, equipment code, IS-TAPE flag).
#
# THE 29th BIT IS "IS TAPE", AND AN EARLIER NOTE HERE HAD THE SENSE
# BACKWARDS.  p.18 line 2 is "BZB, -.1($1), X18" commented "-TAPE
# EQUIPMENT TYPE ENTRY", and this file first recorded a 1 as meaning
# "not a tape".  C22-6728 printed p.90, Figure 44 "The Initialization
# Program - Chart 1", settles it the other way: the decision box "IS
# EQUIPMENT TAPE" goes to X18 on NO and to "SET UP STATUS TABLES FOR
# UNITS" on YES.  So the transcribed path IS the tape path, a 1 here
# means IT IS A TAPE, and X18 -- the first instruction of
# untranscribed p.19 -- is where everything else goes.
#
# THAT ALSO EXPLAINS THE EIGHT.  p.18 line 4 sets the unit counter to
# EIGHT and the loop walks up to eight unit columns; Figure 44's X18
# branch, for disk and console, instead says "SET UNIT COUNT TO TWO".
# A tape channel carries many units and a disk channel two.  The card
# therefore has to be TP for p.18 to be the page under test.
EQP_ENTRIES = [(column_bits(c[1]), EQP_CODE if c == CARD_EQUIPMENT else 0,
                1 if c == "TP" else 0)
               for c in EQUIPMENT_CODES]


def put(words, bitoff, nbits, val):
    """Deposit `nbits` of `val` at IBM bit offset `bitoff`."""
    for i in range(nbits):
        if (val >> (nbits - 1 - i)) & 1:
            w, b = divmod(bitoff + i, 64)
            words[w] = words.get(w, 0) | (1 << (63 - b))


def halt_at(bitaddr):
    """BEW,$ assembled AT bitaddr -- the encoding embeds its own
    target, so it has to be assembled where it will sit."""
    w, b = divmod(bitaddr, 64)
    src = "        SLC, (8)%o.%o\nH       BEW, $\n        END, H\n" % (w, b)
    return assemble(src).words[w]


def main():
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3
                                      and sys.argv[2] not in ("units",
                                                              "units8")):
        print("usage: %s ModuleName [units|units8]" % sys.argv[0],
              file=sys.stderr)
        sys.exit(1)
    # "units" punches UNIT COLUMNS onto the card, which is what sends
    # printed p.18 down its OTHER arm -- lines 13-24's per-unit loop
    # and lines 32-37's count.  Without them line 33's "BXE, X17"
    # fires at once and lines 34-37 never run; those four rows are
    # where this session's unsigned-subtract repair actually lives.
    #
    # "units8" punches EIGHT, which is p.18's LAST untested branch:
    # eight units run the counter out, so line 28's CB+ stops
    # branching and line 30 -- "CM1111(BU,1), .59($3)", commented
    # "UNIT COUNT IN CST TO 8" -- runs INSTEAD of lines 34-37's
    # subtract.  The two arms write the same field by different means
    # and that is the point of testing both.
    unit_mode = sys.argv[2] if len(sys.argv) == 3 else None

    # BOTH PAGES, because they are one program.  Printed p.17 ends at
    # 000712.00 with a full word and printed p.18 begins at
    # 000713.00; p.18's last instruction is "B, X131", which is
    # p.17's line 26.  They are a LOOP over the IOCD card deck, and
    # running either alone would be running half of it.
    #
    # Assembled separately and merged by ADDRESS: each deck SYNs the
    # other's labels to the same absolute values, so the branch
    # targets agree without a merged source.  Their words do not
    # overlap -- 0o655-0o712 and 0o713-0o740.
    progs = []
    for d in DECKS:
        try:
            progs.append(assemble(open(d).read()))
        except AssemblerError as e:
            print("error in %s: %s" % (d, e), file=sys.stderr)
            sys.exit(1)
    prog = progs[0]
    S = {}
    for pr in progs:
        S.update(pr.symtab)
    # >>> THE PAGES SHARE A WORD AND THE MERGE MUST NOT CLOBBER IT.
    # <<<  printed p.18's last instruction is a HALF word at
    # 000740.00 and printed p.19's first is the OTHER HALF of that
    # same word, 000740.40.  A plain dict update lets p.19's word
    # replace p.18's, which deletes p.18 line 45's "B, X131" -- and a
    # zero half-word is "BE" to address zero, so the machine runs the
    # whole card loop correctly and then branches to 0.  Every data
    # check still passed; only the PC said anything was wrong.
    #
    # Merging by OR is right here BECAUSE the contributions are
    # disjoint -- each deck writes one half and leaves the other zero
    # -- and that is ASSERTED rather than assumed, so two decks
    # claiming the same bits fail loudly instead of combining into
    # nonsense.
    words = {}
    for pr in progs:
        for w, v in pr.words.items():
            if w in words and (words[w] & v):
                raise SystemExit(
                    "decks overlap at word %o: %016x and %016x share bits"
                    % (w, words[w], v))
            words[w] = words.get(w, 0) | v

    # ---- the card, at X IN END ------------------------------------
    #
    # >>> THE BUFFER MUST BE EXPLICITLY ZEROED, and finding out why
    # cost a run. <<<  gen_tb fills unwritten core with 0xAAAA...,
    # and bit 44 of that pattern is SET -- so the hunt's very first
    # test, "BB, 1.44($4)" against a word nobody wrote, FINDS A CARD.
    # The page then walked fill, CONNECT FOR TEST counted four ones
    # in 0xAA, LOAD read 0xAAAAAAAAAAAA, the compare against X IOCD
    # failed and p.17 took its "NOT AN IOCD CARD" exit -- a perfectly
    # sensible response to a card-shaped piece of noise.
    #
    # On a real machine this region holds the rest of the assembled
    # system, so it is never fill; zeroing it here is the fixture
    # standing in for that.  Sixteen words is more than the hunt's
    # fourteen.
    # Far enough for the hunt (14 words) AND for the loop to walk off
    # the end of the one card: p.18 line 43's "V+I, $13, 15.0"
    # advances by FIFTEEN WORDS, which is 960 bits -- eighty columns
    # of twelve rows, one punched card exactly.  The stride IS the
    # card.
    for w in range(S["XINEND"] // 64, S["XINEND"] // 64 + 40):
        words.setdefault(w, 0)

    card = S["XINEND"] + CARD_AT_WORD * 64

    # ---- the unit columns, and A UNIT IS A PUNCHED COLUMN ---------
    #
    # >>> DERIVED, and it is the same derivation the card's field map
    # came from: the increments ARE the geometry. <<<  p.18 line 13 is
    # "CT0011(V+I)(BU,12), .12($4)" -- read TWELVE bits, advance
    # TWELVE.  Twelve bits is twelve rows, so a unit entry is ONE
    # COLUMN of the card, and the stride confirms it from the other
    # end: 80 columns x 12 rows = 960 bits = p.18 line 43's 15 words.
    #
    # Lines 16-17 then test individual ROWS of that column, ten and
    # twelve bits BACK from where the read left $4:
    #   BB, 0.0-.10($4), X152     row at column+2
    #   BB, 0.0-.12($4), X151     row at column+0
    # and a column with neither punched falls to line 19's
    # "SIC, XERRAD" / "B, XERROR" -- "IOCD PUNCHED INCORRECTLY".
    #
    # p.17's walk left $4 at card+216: 0 -> +108 (line 26) -> +158
    # (28) -> +170 (32) -> +192 (35) -> +216 (46's 12-bit read with a
    # 24-bit advance).  So the units begin at column 18 of the card,
    # which is where the first unit column goes.
    #
    # TWO UNITS, PUNCHED DIFFERENTLY ON PURPOSE.  The page's comments
    # read backwards against what X15 1 and X15 2 do -- line 16 is
    # commented "-UNIT AVAILABLE" and goes to X15 2, which does NOT
    # set the bit named "UNIT AVAILABLE BIT ON".  Punching both units
    # the same way would measure nothing about that.  Unit 1 takes
    # the X15 2 route and unit 2 the X15 1 route, so the two UST
    # words differ in exactly one bit and the routing is a fact
    # rather than a reading of the comments.
    UNIT_COLS = 8 if unit_mode == "units8" else 2
    # Which ROW each unit is punched on, and so which route it takes.
    # In the two-unit case the second unit is punched on row +0 so the
    # two UST words differ; with eight the count is what is under test
    # and they are all alike.
    UNIT_ROWS = [0 if (UNIT_COLS == 2 and k == 1) else 2
                 for k in range(UNIT_COLS)]
    # >>> WITH EIGHT UNITS, TWO MORE COLUMNS ARE PUNCHED PAST THEM, and
    # without them the test is vacuous. <<<  Punching exactly eight
    # leaves two things that could have stopped the loop -- the counter
    # running out, or the ninth column being blank and line 14's BRZ
    # taking it -- and the run cannot tell them apart.  It also cannot
    # tell which arm wrote the count, because the subtract would give
    # 8 - 0 = 8, the same answer line 30 gives.
    #
    # Punching columns 9 and 10 removes both ambiguities at once: the
    # counter becomes the ONLY thing that can stop the loop, and "the
    # ninth column was never read" becomes a measurement.  They are
    # punched on row +0, the X15 1 route, so a loop that ran on would
    # write a UST word with bit 28 set -- visibly different from the
    # eight before it, not merely present.
    EXTRA_COLS = 2 if UNIT_COLS == 8 else 0

    # >>> AND NOW THE WHOLE CARD IS PUNCHED AS TEXT. <<<  Every field
    # above is a character or a punch in a column, so the fixture is
    # an eighty-column line run through strap/cards.py -- the same
    # path decks/ take to the 7503 -- instead of bits deposited at
    # computed offsets.  Nothing here knows a bit address.
    #
    #   col 1       "B", the class character every MCP control card
    #               carries (C22-6678-1 printed p.8).  Line 26 reads
    #               eight bits here and DISCARDS them -- it is a
    #               CONNECT FOR TEST whose job is the advance to 1.44.
    #   cols 10-13  "IOCD"
    #   cols 14-15  "35", the channel number in decimal
    #   cols 16-17  "TP", Tape
    #   col 18      BLANK -- channel available.  The flag is
    #               ACTIVE-LOW: line 43's "BB, .12($4), X134" branches
    #               AWAY, past line 44, when the bit is ONE, and line
    #               44 -- "-YES * CHANNEL AVAILABLE FLAG TO ON" --
    #               runs only when it is ZERO.  Punching it ("+", a
    #               12-row punch) left the CST's not-available flag
    #               standing while every other check passed, which is
    #               how the sense was identified.
    #   cols 19+    one column per unit.  A punch in row 12 is the
    #               character "+" and a punch in row 0 is "0", so
    #               even these are text.
    cols = [" "] * 80
    cols[0] = "B"
    for i, ch in enumerate("IOCD"):
        cols[9 + i] = ch
    cols[13], cols[14] = "%02d" % CHANNEL
    cols[15], cols[16] = CARD_EQUIPMENT
    if unit_mode:
        for k, row in enumerate(UNIT_ROWS):
            cols[18 + k] = "+" if row == 0 else "0"
        for k in range(UNIT_COLS, UNIT_COLS + EXTRA_COLS):
            cols[18 + k] = "+"
    for i, w in enumerate(card_words("".join(cols))):
        words[card // 64 + i] = w
        # With two units the next column is left ZERO, which is how
        # the list ends: CT0011 copies the storage field, so an
        # unpunched column gives a zero result and line 14's BRZ goes
        # to X16 1.  So the two modes reach the two arms by two
        # different mechanisms, which is why both are run.

    # ---- X IOCD and X IOD, ADJACENT LITERALS ----------------------
    #
    # X IOCD is 48 bits at 001747.60 and X IOD is 36 bits at
    # 001750.40 -- and 001747.60 plus 48 bits IS 001750.40, so the
    # two card keywords sit end to end with nothing between them.
    # Both addresses were recovered from instruction encodings on
    # different pages (p.17 line 30 and p.19 line 23) before either
    # literal had been seen, and they fit exactly.
    #
    # Four columns of "IOCD" and three of "IOD", punched through the
    # same card code the card itself uses.
    put(words, S["XIOCD"], 48,
        int("".join("%03x" % column_bits(c) for c in "IOCD"), 16))
    put(words, S["XIOD"], 36,
        int("".join("%03x" % column_bits(c) for c in "IOD"), 16))

    # ---- X EQP T: ten 29-bit entries, 24-bit letter + 4-bit code --
    for i, (letter, code, nottape) in enumerate(EQP_ENTRIES):
        base = S["XEQPT"] + 29 * i
        put(words, base, 24, letter)
        put(words, base + 24, 4, code)
        put(words, base + 28, 1, nottape)

    # ---- the two halts --------------------------------------------
    #
    # With both pages in, the only exits that leave them are X 19 and
    # X ERROR, and both are on pages nobody has transcribed.  A
    # "BEW,$" at each makes them distinguishable stopping points, so
    # the PC says which one the loop took.
    #
    # X 19 IS WHERE THE IOCD LOOP LEAVES OFF, not where the program
    # ends, and this comment used to say the page called it "the
    # normal end".  IT DOES NOT.  Printed p.17 line 31's comment is
    # "-NOT AN IOCD CARD"; the other phrase was mine and was quoted
    # elsewhere as if it were the listing's.
    #
    # What X 19 actually is, from printed p.19 line 23:
    #
    #     X19   KF(BU,36),XIOD,12     -COMPARE AGAINST * IOD *
    #
    # thirty-six bits = three columns = "IOD", followed by
    # "X ERR 19  SIC,X ERR AD" / "BZAEZ,X ERROR" commented "-NOT AN
    # IOD CARD EITHER".  C22-6728 printed p.88 lists the three
    # control-card types in that order: IOCD, IOD, MCPP.
    #
    # So p.18 goes back to X131 for the next card; when that card
    # does not match X IOCD, p.17 line 31's BZAE sends it to X 19,
    # which asks whether it is an IOD card instead.  Reaching this
    # halt means the IOCD cards were processed and initialization
    # moved on -- not a failure.
    # >>> ONLY X ERROR IS A HALT NOW, and the other two had to come
    # out in the same change that added printed p.19 to DECKS. <<<
    # X18 is p.19's FIRST INSTRUCTION (000740.40) and X19 is its line
    # 23 (000756.40).  Planting "BEW,$" at either would overwrite a
    # real row of a transcribed page with a stop, and the page would
    # appear to do nothing while every check still passed for the
    # wrong reason.
    #
    # X ERROR is still a halt because it is still on an untranscribed
    # page -- printed p.5 line 5 -- and it is now the ONLY exit from
    # the three pages, which is correct: p.19 line 25's "BZAEZ,X
    # ERROR" is where a card that is neither IOCD nor IOD goes.
    exits = {"XERROR": S["XERROR"]}     # printed p.5 -- still untranscribed
    for name, addr in exits.items():
        w, _ = divmod(addr, 64)
        words[w] = words.get(w, 0) | halt_at(addr)
    end_of_page = S["XERROR"]

    prog.words.clear()
    prog.words.update(words)

    # The PC check below is what says which exit the page took; a
    # check that the halt word is the halt word would be a tautology
    # and is deliberately not here.
    checks = []
    # >>> THE CHANNEL STATUS TABLE ENTRY THE PAGE FILLED IN. <<<
    #
    # Derived, not observed.  Printed p.17 line 37 takes the channel
    # number out of $R -- word 9, the accumulator's RIGHT half, where
    # the conversion left it at offset 46, i.e. IBM bits 12-17 of that
    # word.  LV copies bits 0-24 into the value field, whose ADDRESS
    # part is bits 0-23, so the address comes out `channel << 6` --
    # ONE WORD PER CHANNEL, which is what makes line 22's "preset 64
    # entries" and line 20's "64.0" to the UST base consistent.
    #
    # Line 42's "V+, $3, $5" then indexes from X BUFER, so channel 35
    # lands 35 words in.  Line 44 clears the not-available bit the
    # preset set, and line 54 stores the equipment code at bits 52-55.
    cst_word = (S["XBUFER"] + (CHANNEL << 6)) // 64

    def put_field(word, ibm_lo, ibm_hi, val):
        """Set IBM bits ibm_lo..ibm_hi (bit 0 = MSB) of a 64-bit word."""
        nbits = ibm_hi - ibm_lo + 1
        mask  = ((1 << nbits) - 1) << (63 - ibm_hi)
        return (word & ~mask) | ((val & ((1 << nbits) - 1)) << (63 - ibm_hi))

    # The preset entry (p.17 line 22) and then, in printed order, every
    # instruction on the path that writes into it.  Each line of this
    # derivation is a line of the listing; nothing here is observed.
    preset = (1 << (63 - 25)) | (1 << (63 - 29))   # not available, not assigned

    # $15 is the base of the unit status table area: p.17 line 18 loads
    # X BUFER, line 20 adds 64.0 -- sixty-four WORDS, which is why the
    # channel status table can be one word per channel and still not
    # collide with the UST.
    ust_bits = S["XBUFER"] + 64 * 64

    entry = preset
    entry = put_field(entry, 25, 25, 0)          # p.17 l.44 -- channel IS available
    entry = put_field(entry, 52, 55, EQP_CODE)   # p.17 l.54 -- the equipment code
    # SV stores the value AND its sign: the 24-bit address lands at IBM
    # bits 0-23 and the sign at 24, so the address field is 24 bits wide
    # and NOT 25 -- writing it as one 25-bit field puts every bit of it
    # one place too low.
    entry = put_field(entry,  0, 23, ust_bits)   # p.18 l.5  SV   -- UST address in
    entry = put_field(entry, 24, 24, 0)          #           and its sign
    entry = put_field(entry, 29, 29, 0)          # p.18 l.7  CM0000 -- "MEANINGLESS
                                                 #                     ASSIGN BIT"
    entry = put_field(entry, 27, 27, 1)          # p.18 l.9  CM1111 -- MULTI bit on
    if not unit_mode:
        # p.18 line 33's "BXE, X17" is the branch marked "NO UNITS AT ALL
        # ON MULTI CHANNEL": line 32 compares $15's count against 8, line
        # 4 had just SET it to 8, and this card carries no unit entries,
        # so the compare is equal and control reaches X17.  Line 42 then
        # clears SEVENTEEN bits -- not twenty-four -- so the low seven
        # bits of the UST address it just stored survive in bits 17-23.
        entry = put_field(entry, 0, 16, 0)       # p.18 l.42 X17 -- clear address
    else:
        # WITH UNITS ON THE CARD, X17 IS NOT REACHED: line 38's "B, X171"
        # jumps over it, so the UST address SURVIVES in the entry -- which
        # is the whole point of line 5 having put it there.
        #
        # And lines 34-37 run instead:
        #   LFI(BU,18), 8.0        load eight
        #   -(BU,18), $15+.28      minus what is LEFT of the counter
        #   ST(BU,4), .59($3)      insert the number of units
        #
        # THE COUNT FIELD IS BITS 59-62, derived from the pair of rows
        # that write it: line 37 stores FOUR bits at offset .59, and line
        # 30 -- the "eight units" arm -- sets ONE bit at the same offset
        # and is commented "UNIT COUNT IN CST TO 8".  A single bit at the
        # left of a four-bit field IS eight, so the field runs 59-62 and
        # not 56-59.
        #
        # AND "8.0" IS EIGHT, not 512.  The immediate sits in the 24-bit
        # address field, where the deck header records it assembling to
        # 000010.00 -- word 8, bit 0 -- and an 18-bit operand taken from
        # that field's bits 0-17 is the WORD number: 512 >> 6 = 8.  The
        # subtrahend is the same shape: "$15+.28" is word 31 bit 28, and
        # eighteen bits from there is exactly the count field.
        if UNIT_COLS == 8:
            # EIGHT UNITS TAKE THE OTHER ARM.  Line 28's CB+ has run
            # the counter to zero, so it stops branching and falls into
            # line 30, "CM1111(BU,1), .59($3)" -- ONE bit at the left
            # of the four-bit field, which IS eight.  Lines 32-37 are
            # not reached at all, so this run says nothing about the
            # subtract and the two-unit run says nothing about this.
            entry = put_field(entry, 59, 62, 8)
        else:
            entry = put_field(entry, 59, 62, UNIT_COLS)
    checks.append(("p17_cst_entry_for_channel_35", str(cst_word), entry))
    # A neighbour, to show only the addressed entry moved.
    checks.append(("p17_neighbour_still_preset", str(cst_word + 1), preset))

    # The index word that decided which way line 33 went.  $15 lives at
    # word 31 (index registers occupy words 16-31).
    ust_reg = put_field(0, 0, 23, ust_bits + (64 * UNIT_COLS if unit_mode else 0))
    ust_reg = put_field(ust_reg, 28, 45, 8 - UNIT_COLS if unit_mode else 8)
    if unit_mode:
        # ONE "CB+" PER UNIT, and the pocket card gives CB+ as "Add one
        # in bit position 17" -- bit 17 of a 24-bit bit address is 64
        # bits, ONE WORD, so the value walks the UST one entry at a time
        # while the count runs down.  Two units: value +2 words, count 6,
        # and 8 - 6 = 2 is what lines 34-37 put in the CST entry above.
        checks.append(("p18_ust_pointer_and_count", "31", ust_reg))

        # >>> THE TWO UST ENTRIES, which is where the unit loop's work
        # actually lands. <<<  X15 1 and X15 2 write bits of ($15):
        #   .28  unit available      (X15 1 only)
        #   .29  unit not assigned
        #   .27  tape disposition
        #   .39  select status
        # so an entry is ONE WORD -- which CB+'s one-word step confirms
        # independently.  Unit 1 took the X15 2 route and unit 2 the
        # X15 1 route, so the two words differ in exactly bit 28.
        ust_w = ust_bits // 64
        common = (1 << (63 - 29)) | (1 << (63 - 27)) | (1 << (63 - 39))
        for k, row in enumerate(UNIT_ROWS):
            # Row +0 goes to X15 1, which sets .28 and then falls into
            # X15 2; row +2 goes straight to X15 2 and skips it.
            want = common | ((1 << (63 - 28)) if row == 0 else 0)
            checks.append(("p18_ust_entry_%d_via_x15%d"
                           % (k, 1 if row == 0 else 2), str(ust_w + k), want))
        # THE ENTRIES PAST THE LAST ONE, which say the loop stopped
        # where it was supposed to rather than running on.  With two
        # units the card stopped it; with eight the COUNTER stopped it,
        # over two columns that are punched and were never read, which
        # is the only thing in either run that separates line 30's arm
        # from lines 32-37's.
        for k in range(UNIT_COLS, UNIT_COLS + max(EXTRA_COLS, 1)):
            checks.append(("p18_ust_entry_%d_untouched" % k,
                           str(ust_w + k), 0))
    else:
        # Reaching X17 means the count was never decremented, so the word
        # still holds the 8 that line 4's "LCI, $15, 8.0" put there and
        # the value is still the UST base -- the unit loop never ran.
        checks.append(("p18_ust_counter_untouched", "31", ust_reg))

    print(generate(sys.argv[1], prog, checks,
                   pc_check=end_of_page // 32,
                   cycle_bound=2000000,
                   step_cap=4000000))


if __name__ == "__main__":
    main()
