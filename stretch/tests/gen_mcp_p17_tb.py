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

  INVENTED -- the card's CONTENTS, X IOCD's 48-bit pattern, and the
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

DECK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    os.pardir, "decks", "mcp_bootstrap_p17.strap")

CARD_AT_WORD = 3          # the card sits three words into the buffer,
                          # so the hunt has to step to find it
IDENT  = 0x800000000ABC   # X IOCD's pattern; leading bit set, as the
                          # hunt requires
LETTER = 0xABC            # the card's equipment letter
TENS   = 0x08             # 7-bit column, three zeros left of the punch
UNITS  = 0x0400           # 16-bit column, five zeros left of the punch
EQP_CODE = 6              # the code the matching table entry carries
CHANNEL  = 35             # tens 3, units 5 -- what the two columns encode
EQP_ENTRIES = [(273, 0), (546, 0), (819, 0), (LETTER, EQP_CODE), (1092, 0),
               (1365, 0), (1638, 0), (1911, 0), (2184, 0), (2457, 0)]


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
    if len(sys.argv) != 2:
        print("usage: %s ModuleName" % sys.argv[0], file=sys.stderr)
        sys.exit(1)

    try:
        prog = assemble(open(DECK).read())
    except AssemblerError as e:
        print("error: %s" % e, file=sys.stderr)
        sys.exit(1)

    S = prog.symtab
    words = dict(prog.words)

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
    for w in range(S["XINEND"] // 64, S["XINEND"] // 64 + 16):
        words.setdefault(w, 0)

    card = S["XINEND"] + CARD_AT_WORD * 64
    put(words, card + 0,   8,  0xFF)     # card type (0xFF: 8 ones, to tell it from the 0xAA fill)
    put(words, card + 108, 48, IDENT)    # identifier; bit 108 is the zone bit
    put(words, card + 158, 7,  TENS)
    put(words, card + 170, 16, UNITS)
    put(words, card + 192, 12, LETTER)
    # CHANNEL AVAILABLE IS ACTIVE-LOW HERE, and the page's own
    # structure says so.  Line 43 is "BB, .12($4), X134" commented
    # "-IS CHANNEL AVAILABLE", and it branches AWAY -- past line 44 --
    # when the bit is ONE.  Line 44, "CM0000(BU,1), .25($3)", is the
    # one commented "-YES * CHANNEL AVAILABLE FLAG TO ON", and it
    # runs only when the card's bit is ZERO.  So a zero here is what
    # turns the CST's not-available flag off.
    #
    # Set to one on the first run, which left the flag standing and
    # is how the sense was identified: every other check passed and
    # that single bit did not move.

    # ---- X IOCD, a 48-bit field that CROSSES a word boundary ------
    put(words, S["XIOCD"], 48, IDENT)

    # ---- X EQP T: ten 29-bit entries, 24-bit letter + 4-bit code --
    for i, (letter, code) in enumerate(EQP_ENTRIES):
        base = S["XEQPT"] + 29 * i
        put(words, base, 24, letter)
        put(words, base + 24, 4, code)

    # ---- the three halts ------------------------------------------
    end_of_page = max(prog.words) * 64 + 64      # first word past line 54
    exits = {"after_line_54": end_of_page,
             "X19":    S["X19"],        # "NOT AN IOCD CARD"
             "XERROR": S["XERROR"]}     # "NO IOCD DETECTED" / wrong code
    for name, addr in exits.items():
        w, _ = divmod(addr, 64)
        words[w] = words.get(w, 0) | halt_at(addr)

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
    preset   = (1 << (63 - 25)) | (1 << (63 - 29))   # not available, not assigned
    filled   = (preset & ~(1 << (63 - 25))) | (EQP_CODE << (63 - 55))
    checks.append(("p17_cst_entry_for_channel_35", str(cst_word), filled))
    # A neighbour, to show only the addressed entry moved.
    checks.append(("p17_neighbour_still_preset", str(cst_word + 1), preset))

    print(generate(sys.argv[1], prog, checks,
                   pc_check=end_of_page // 32,
                   cycle_bound=2000000,
                   step_cap=4000000))


if __name__ == "__main__":
    main()
