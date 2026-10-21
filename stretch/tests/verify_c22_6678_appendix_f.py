#!/usr/bin/env python3
"""verify_c22_6678_appendix_f.py -- strap/cards.py against the printed
character-code table.

>>> C22-6678-1 printed p.56 = PDF p.56, "APPENDIX F. CHARACTER CODES",
TABULATES THE CARD CODE DIRECTLY, and strap/cards.py used to assert
that no 7030 document did. <<<  The header reads: "The following table
lists the octal codes, by character, for eight-bit IQS, six-bit BCD,
and the corresponding column binary punches.  The IQS codes given for
the letters and numbers are for upper case.  For lower case letters,
simply change the last bit of the upper case code to a 0 bit."

This file transcribes all four columns and does two things with them.

1. THE PUNCHES ARE THE SOURCE.  cards.punches() now reads them out of
   Appendix F, so this half checks the transcription against itself --
   which is worth having anyway, because a typo in a 49-row table is
   otherwise invisible until a deck punches the wrong hole.

2. THE OLD DERIVATION IS KEPT AS A CROSS-CHECK AND MEASURED.
   cards.punches_from_grid() builds the same answer out of the 48
   Character Set grid on Reference Manual printed p.166, on the
   argument that the grid's four occupied columns ARE the four zone
   punches and its sixteen rows ARE the digit punches.  That argument
   gets 46 of 49 right.  THE THREE IT MISSES ARE THE POINT:

       char   Appendix F   the grid derivation
       '      0-3-8        4-8            <- transposed
       ,      4-8          0-3-8          <- transposed
       ;      11-0         not in the grid at all
       :      NO PUNCHES   0-2-8

   The quote and the comma have each other's punches; the 7030's set
   spends 11-0 on a semicolon and gives the colon no card code at all.
   The derivation was justified on the grounds that the card code
   "belongs to the CARD and the keypunch, not to the computer" -- true
   of the letters and digits, false of exactly this punctuation, which
   is the only place it could have mattered.

   THE EXCEPTION LIST IS A RATCHET.  It is spelled out below and the
   count is asserted.  If a future change to either path moves a
   character into or out of it, this fails.

ALSO CHECKED: the IQS codes are consecutive odd octal values for the
letters, which is the table's own stated structure ("for lower case
letters, simply change the last bit of the upper case code to a 0
bit" -- so upper case is odd), and the BCD codes are six bits.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                os.pardir, "strap"))
import cards

# (character, IQS octal, BCD octal, Punches) exactly as printed.
# None means the cell is BLANK on the page.
APPENDIX_F = [
    ("A", 0o055, 0o61, "12-1"), ("B", 0o057, 0o62, "12-2"),
    ("C", 0o061, 0o63, "12-3"), ("D", 0o063, 0o64, "12-4"),
    ("E", 0o065, 0o65, "12-5"), ("F", 0o067, 0o66, "12-6"),
    ("G", 0o071, 0o67, "12-7"), ("H", 0o073, 0o70, "12-8"),
    ("I", 0o075, 0o71, "12-9"), ("J", 0o077, 0o41, "11-1"),
    ("K", 0o101, 0o42, "11-2"), ("L", 0o103, 0o43, "11-3"),
    ("M", 0o105, 0o44, "11-4"), ("N", 0o107, 0o45, "11-5"),
    ("O", 0o111, 0o46, "11-6"), ("P", 0o113, 0o47, "11-7"),
    ("Q", 0o115, 0o50, "11-8"), ("R", 0o117, 0o51, "11-9"),
    ("S", 0o121, 0o22, "0-2"),  ("T", 0o123, 0o23, "0-3"),
    ("U", 0o125, 0o24, "0-4"),  ("V", 0o127, 0o25, "0-5"),
    ("W", 0o131, 0o26, "0-6"),  ("X", 0o133, 0o27, "0-7"),
    ("Y", 0o135, 0o30, "0-8"),  ("Z", 0o137, 0o31, "0-9"),
    ("0", 0o140, 0o12, "0"), ("1", 0o142, 0o01, "1"),
    ("2", 0o144, 0o02, "2"), ("3", 0o146, 0o03, "3"),
    ("4", 0o150, 0o04, "4"), ("5", 0o152, 0o05, "5"),
    ("6", 0o154, 0o06, "6"), ("7", 0o156, 0o07, "7"),
    ("8", 0o160, 0o10, "8"), ("9", 0o162, 0o11, "9"),
    (" ", 0o000, 0o20, "none"),
    ("+", 0o041, 0o60, "12"),     ("$", 0o042, 0o53, "11-3-8"),
    ("=", 0o043, 0o13, "3-8"),    ("*", 0o044, 0o54, "11-4-8"),
    ("(", 0o045, 0o34, "0-4-8"),  ("/", 0o046, 0o21, "0-1"),
    (")", 0o047, 0o74, "12-4-8"), ("'", 0o050, 0o33, "0-3-8"),
    (";", 0o051, 0o52, "11-0"),   (",", 0o052, 0o14, "4-8"),
    ('"', 0o053, None, None),
    (".", 0o164, 0o73, "12-3-8"), (":", 0o165, None, None),
    ("-", 0o166, 0o40, "11"),     ("?", 0o167, None, None),
]

# The characters where the grid derivation and the printed table part
# company.  Four entries, named, with what each side says.
KNOWN_GRID_GAP = {
    "'": ({0, 3, 8}, {4, 8}),
    ",": ({4, 8}, {0, 3, 8}),
    ";": ({11, 0}, None),          # not in the 48 grid at all
    ":": (None, {0, 2, 8}),        # no card code printed; grid invents one
}

fails = []


def check(name, got, want):
    ok = got == want
    print("%-4s %s = %s%s" % ("PASS" if ok else "FAIL", name, got,
                              "" if ok else ", expected %s" % (want,)))
    if not ok:
        fails.append(name)


def rows(spec):
    return set() if spec == "none" else {int(x) for x in spec.split("-")}


def main():
    # ---- 1. cards.punches() IS Appendix F --------------------------
    bad = []
    blanks = []
    for ch, _iqs, _bcd, spec in APPENDIX_F:
        if spec is None:
            try:
                cards.punches(ch)
                bad.append("%r should have no card code" % ch)
            except ValueError:
                blanks.append(ch)
            continue
        try:
            got = cards.punches(ch)
        except ValueError:
            bad.append("%r raised" % ch)
            continue
        if got != rows(spec):
            bad.append("%r: %s vs printed %s" % (ch, sorted(got), spec))
    check("punches_match_appendix_f", bad, [])
    # Three characters are printed WITH an IQS code and NO punches.
    # That is a fact about the character set, not a gap in the scan.
    check("characters_with_no_card_code", blanks, ['"', ":", "?"])

    # ---- 2. the grid derivation, measured --------------------------
    agree, differ = [], {}
    for ch, _iqs, _bcd, spec in APPENDIX_F:
        want = None if spec is None else rows(spec)
        try:
            got = cards.punches_from_grid(ch)
        except ValueError:
            got = None
        if got == want:
            agree.append(ch)
        else:
            differ[ch] = (want, got)
    check("grid_derivation_agrees_on", len(agree), len(APPENDIX_F) - 4)
    check("grid_derivation_gap_is_exactly", differ, KNOWN_GRID_GAP)

    # ---- 3. the table's own stated structure -----------------------
    # "For lower case letters, simply change the last bit of the upper
    # case code to a 0 bit" -- so every upper-case IQS code is ODD.
    letters = [(c, i) for c, i, _, _ in APPENDIX_F if c.isalpha()]
    check("letter_iqs_codes_are_odd",
          [c for c, i in letters if i % 2 == 0], [])
    # A-I, J-R and S-Z each step by 2, which is what makes the first
    # claim mean anything: the letters occupy consecutive IQS slots.
    for name, run in (("a_to_i", "ABCDEFGHI"), ("j_to_r", "JKLMNOPQR"),
                      ("s_to_z", "STUVWXYZ")):
        codes = [i for c, i, _, _ in APPENDIX_F if c in run]
        steps = {b - a for a, b in zip(codes, codes[1:])}
        check("iqs_%s_steps_by_two" % name, steps, {2})
    # BCD is six bits.
    check("bcd_codes_fit_six_bits",
          [c for c, _, b, _ in APPENDIX_F if b is not None and b > 0o77], [])

    # ---- 4. the one value this whole page was opened for -----------
    # p.17 line 30 compares 48 bits against X IOCD.  Four columns of
    # Appendix F's punches, packed by the bit order the Reference
    # Manual prints on p.138, give the card's keyword.
    ident = 0
    for ch in "IOCD":
        ident = (ident << 12) | cards.column_bits(ch)
    check("iocd_keyword_as_punched", "0x%012x" % ident, "0x801408840820")
    # And its leading bit -- the one p.17 line 13 tests, commented
    # "-IF ZONE BIT OF IOCD" -- is set, because I is 12-9 and the 12
    # row comes first.
    check("iocd_leading_bit_is_the_i_zone_punch", (ident >> 47) & 1, 1)

    print("ALL CHECKS PASSED" if not fails
          else "%d CHECK(S) FAILED" % len(fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
