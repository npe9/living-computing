#!/usr/bin/env python3
"""verify_c22_6578_a4_addresses.py -- C22-6578 Appendix A4.8's
integer-address and point-notation identities, checked by assembling
both spellings and comparing the machine words.

THE RULE, printed p.63 (PDF 64), section A4.8.1 "Integer Addresses":

    "The bit address equivalent of an integer address is decided by
    the environment, which defines a subfield.  The integer address is
    treated as an integer of the subfield (e.g., the non-zero bit for
    the integer 1 would occupy the rightmost position of the
    subfield).  Then the left margin of the subfield is placed in
    juxtaposition with the leading bit of the address field, leading
    to a bit address identification.

    Where the environment seems to suggest more than one subfield, as
    is frequently so in immediate type instructions, the smallest one
    is to be adopted."

and the table that goes with it:

    Instruction              Subfield Size
    Floating point           at most 18 bits
    VFL                      at most 24 bits
    most others              at most 19 bits
    VFL immediate            at most the field length
    E +- I, SHF              11 bits + sign
    immediate index arith.   at most the size of the field in question
                             in the index register

WHY THIS FILE EXISTS.  `strap/README.md` "Next steps" item 5 recorded
the general rule as implemented for VFL Immediate only, and said of
everywhere else: "A bare (non-'point') integer given as a normal
address field elsewhere is used as-is, unconverted.  Untested (every
program here uses dotted notation or labels for non-immediate
addresses), not yet a confirmed bug."

**It was a bug, in the floating-point path**, and this appendix is
what pins it: `SRT(N), 215` is equivalent to `SRT(N), 215.0`, so a
bare integer in an FP address is a WORD count.  `strap_asm.py` called
`eval_expr`, which returns a pure BIT count, so it meant three words.
Fixed 2026-10-19 by calling `eval_addr_field` with the field's own
unit, which also brings the per-term half of C22-6531 p.11's rule
with it.

All 271 decks in `decks/` assemble byte-identically across that
change -- checked by hashing every image before and after, not
assumed -- because every one of them writes dotted addresses or bare
labels in a non-immediate address field, exactly as README item 5
said.

WHAT A PASS MEANS.  These are EQUIVALENCES, not values: the two
spellings must assemble to the same word.  That is a weaker claim
than a listing oracle -- it cannot catch both spellings being wrong
together -- but it is IBM's own statement of what the assembler must
do, and it is the only source in the corpus that states it.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "strap"))

from strap_asm import assemble

# printed p.63's six examples and p.64's three, each "X is equivalent
# to Y".  The parenthetical notes are the page's own.
EQUIVALENCES = [
    ("SRT(N), 215",        "SRT(N), 215.0",        "floating point: subfield at most 18 bits"),
    ("M+1(BU,63,8), 17",   "M+1(BU,63,8), 0.17",   "VFL: subfield at most 24 bits"),
    ("CBRH, $4, 28",       "CBRH, $4, 14.0",       "most others: subfield at most 19 bits"),
    ("E-(N), 17",          "E-(N), 17.0",          "E +- I: 11 bits + sign"),
    ("*I(BU,7,8), 127",    "*I(BU,7,8), 260096.0", "VFL immediate: (127.0).2**11 = 260096.0"),
    ("V+I, $3, 13",        "V+I, $3, 6.32",        "immediate index arith (25 > 19)"),
    ("C-I, $3, 13",        "C-I, $3, 13.0",        "immediate index arith (18 < 19)"),
]

# printed p.64, A4.8.2(c): "A 'point' placed in front of or behind a
# symbolized integer converts it into a bit address; a 'point' placed
# in front or behind a symbolized bit address, however, has no effect
# on the latter."  Worked with M defined as 5 and JOE as 817.35.
POINTS = [
    (".M",      "0.5",      "leading point on a symbolized integer"),
    ("M.",      "5.0",      "trailing point on a symbolized integer"),
    (".JOE",    "817.35",   "leading point on a symbolized bit address: no effect"),
    ("JOE.",    "817.35",   "trailing point on a symbolized bit address: no effect"),
    ("M.M",     "5.5",      "integer on both sides of the point"),
    ("JOE.JOE", "1634.70",  "bit address on both sides: 817.35 + 817.35"),
]

# KNOWN GAP, and this list is a RATCHET: a pair here that starts
# PASSING is reported as news, exactly as tests/audit_opcode_coverage.py
# treats its UNIMPLEMENTED set.  Both are the same narrow case -- a
# TRAILING point on a symbolized INTEGER -- and neither is used
# anywhere in decks/.  Recorded rather than fixed because it lives in
# the expression tokenizer, which every address in the corpus goes
# through, and it has no witness beyond this appendix.
KNOWN_GAP = {"M.", "M.M"}


def words_of(src):
    prog = assemble(src)
    return [prog.words[a] for a in sorted(prog.words)]


def instr_pair(a, b):
    tmpl = "        SLC, (8)2000.0\nS       %s\n        BEW, $\n        END, S\n"
    return words_of(tmpl % a), words_of(tmpl % b)


def point_pair(a, b):
    tmpl = ("        SLC, (8)2000.0\nM       SYN, 5\nJOE     SYN, 817.35\n"
            "S       BEW, %s\n        END, S\n")
    return words_of(tmpl % a), words_of(tmpl % b)


def main():
    failures = 0
    unexpected_pass = 0

    print("-- A4.8.1, integer addresses (printed p.63, and p.64's tail) --")
    for a, b, note in EQUIVALENCES:
        wa, wb = instr_pair(a, b)
        if wa == wb:
            print("PASS %-22s == %-22s   %s" % (a, b, note))
        else:
            print("FAIL %-22s != %-22s   %s" % (a, b, note))
            print("       %s" % [hex(x) for x in wa])
            print("       %s" % [hex(x) for x in wb])
            failures += 1

    print("-- A4.8.2(c), point notation (printed p.64) --")
    for a, b, note in POINTS:
        wa, wb = point_pair(a, b)
        same = (wa == wb)
        if a in KNOWN_GAP:
            if same:
                print("NEWS %-22s == %-22s   %s" % (a, b, note))
                print("       this pair is in KNOWN_GAP and now PASSES; remove it.")
                unexpected_pass += 1
            else:
                print("GAP  %-22s != %-22s   %s" % (a, b, note))
        elif same:
            print("PASS %-22s == %-22s   %s" % (a, b, note))
        else:
            print("FAIL %-22s != %-22s   %s" % (a, b, note))
            failures += 1

    if unexpected_pass:
        print("\n%d KNOWN_GAP pair(s) now pass -- update the list." % unexpected_pass)
        sys.exit(1)
    if failures:
        print("\n%d TEST(S) FAILED" % failures)
        sys.exit(1)
    print("\nALL TESTS PASSED (%d equivalences, %d point identities, "
          "%d known gaps)" % (len(EQUIVALENCES), len(POINTS) - len(KNOWN_GAP),
                              len(KNOWN_GAP)))


if __name__ == "__main__":
    main()
