#!/usr/bin/env python3
"""charsets.py -- the IBM 7030's character codes, for STRAP's entry modes.

SOURCE: Reference Manual 22-6530-2, PRINTED p.166 = PDF 169, a page
headed "Character Codes".  Four grids, captioned below each: 49, 89,
48 and 120 Character Set.

THE MANUAL PRINTS NO NUMBERS AT ALL.  Each grid is a matrix whose
columns are labelled "BITS 0-1-2-3" (0000 through 0111) and whose rows
are labelled "BITS 4-5-6-7" (0000 through 1111), with a character in
each occupied cell.  The 7030 numbers bits left to right from zero, so

    code = (column << 4) | row

and every octal constant below is this reader's arithmetic, not the
manual's ink.

WHERE THIS IS *NOT* FROM.  Three places in this repository used to say
the tables were "C28-6129 Appendix C, printed pp.47-53".  Printed
pp.47-53 is Appendix C, but Appendix C is "SYMBOLIC DESCRIPTIONS AND
MNEMONICS FOR IBM 7030" -- an instruction list with no character table
on any of its seven pages, and there is none anywhere else in that
manual.  The page range had been read off a table of contents and
never opened.  Corrected 2026-10-17; see docs/NEXT.md 5w.

READ TWICE, INDEPENDENTLY, AND THE TWO READINGS AGREE.  The grids were
transcribed once by a delegated reader at 600 dpi and once here at 150
dpi from the cell positions; the two agree on all 49 entries of the 48
set and on sixteen spot checks of the 89 set, including the four that
pin the 48 set to canonical IBM BCD (A = 0o61 at column 0011 row 0001,
J = 0o41, S = 0o22, 0 = 0o12).  The 89 set additionally obeys the
case-shift invariant the Reference Manual's printed p.153 describes --
bit 7 selects case, so every lower/upper pair sits in adjacent rows
2n/2n+1, which all 26 letters and eight symbol pairs do.

>>> WHAT NO LISTING IN THIS CORPUS CHECKS <<<

MCP's listing prints NOTHING in the BINARY OUTPUT column for an
(IQS*)DD or (A*)DD row.  Printed p.9's message blocks are six rows
each and only the three DD(BU,8) control-code rows print anything.  So
AGENTS.md rule 3 cannot check a single character code here, and no
transcription of those pages ever will.

What the listing does check -- tightly -- is the LOCATION COUNTER:
eight bits per character with the end-of-statement character not
compiled.  On printed p.9, line 9 to line 10 is 000255.20 - 000254.20
= 64 bits for the eight characters of "000000.0", and line 10 to line
11 is 000257.70 - 000255.20 = 168 bits for the twenty-one characters
of " EKJ ON CCW OF IPL CW".  That catches a dropped or doubled
character anywhere in thirty messages.  It says nothing whatever about
whether 'E' is 0o045.

THE ENTRY-MODE PREFIX, and the trailing character is not part of it.
C28-6129 printed p.16:

  "The second character in the entry mode field is known as the
   end-of-statement character.  Its presence instructs STRAP to
   perform the desired conversion until this character is reached in
   the message.  The end-of-statement character may be any legal card
   code character except ), ' (8-4), ; (11-0), and blank.  This
   character is not compiled."

So "(A*)" is mode A terminated by "*", and MCP's "(IQSX)" is mode IQS
terminated by "X" -- nothing is missing from it.  Two traps follow: an
(IQSX) message cannot contain a literal X, and an (A*) message cannot
contain a literal *.

WHICH MODE USES WHICH GRID is an INFERENCE in both cases, and a
different strength each:

  A   -> the 48 Character Set.  C28-6129 printed p.16 calls mode A
         "6-bit IBM tape BCD" and the Reference Manual's page never
         says "BCD" at all.  The identification is structural: the
         four occupied columns are exactly the IBM BCD zones (no-zone
         digits, 0-zone / and S-Z, 11-zone - and J-R, 12-zone + and
         A-I), the values come out canonical at every spot checked,
         it is uppercase-only, and only bits 2-7 are significant,
         which matches p.16's mode-A rule verbatim.  CAVEAT KEPT:
         internal BCD and 7-track tape BCD differ in a position or
         two, notably BLANK, and this grid puts BLANK at 0o00.

  IQS -> the 89 Character Set, via a two-document chain.  Reference
         Manual printed p.153 says the console keyboard's set
         "consisting of 89 codes which correspond to 88 distinct
         non-blank characters and blank, is shown in the Appendix";
         C28-6129 printed p.16 says IQS is "the set appropriate to the
         7030 console typewriter, or Inquiry Station".  The 89-cell
         count matches exactly.

  CC  -> NOT HERE.  C28-6129 p.16 names it -- "converted to 12-bit
         bytes, where each byte reflects the multiple punch actually
         read" -- and tabulates it nowhere, and all four Reference
         Manual grids are 8-bit.  The twelve bits ARE the card rows
         (12, 11, 0, 1-9), so what is wanted is a documented bit
         order, not a lookup table.  Unchecked candidates: C22-6729,
         C22-6531, C22-6678-1.

  N   -> not an entry mode at all.  It is the floating-point
         *normalized* use mode (C28-6129 printed p.15).

  P   -> ECS, the 120 Character Set, named by C28-6129 p.16.  MCP's
         listing never writes a (P..) prefix, so the grid is left
         untranscribed.

The 89 set's ten ITALIC digits are a separate glyph set in column 0111
rows 0001 through 1111 odd; they have no ASCII spelling and are kept
in a table of their own rather than fought into IQS.
"""

# ---------------------------------------------------------------------
# 48 Character Set -- STRAP entry mode A.  48 printable + BLANK.
# Only bits 2-7 are significant; bits 0-1 are zero throughout.
# ---------------------------------------------------------------------
A = {
       ' ': 0o000,   # col 0000 row 0000
       '1': 0o001,   # col 0000 row 0001
       '2': 0o002,   # col 0000 row 0010
       '3': 0o003,   # col 0000 row 0011
       '4': 0o004,   # col 0000 row 0100
       '5': 0o005,   # col 0000 row 0101
       '6': 0o006,   # col 0000 row 0110
       '7': 0o007,   # col 0000 row 0111
       '8': 0o010,   # col 0000 row 1000
       '9': 0o011,   # col 0000 row 1001
       '0': 0o012,   # col 0000 row 1010
       '=': 0o013,   # col 0000 row 1011
       "'": 0o014,   # col 0000 row 1100
       '/': 0o021,   # col 0001 row 0001
       'S': 0o022,   # col 0001 row 0010
       'T': 0o023,   # col 0001 row 0011
       'U': 0o024,   # col 0001 row 0100
       'V': 0o025,   # col 0001 row 0101
       'W': 0o026,   # col 0001 row 0110
       'X': 0o027,   # col 0001 row 0111
       'Y': 0o030,   # col 0001 row 1000
       'Z': 0o031,   # col 0001 row 1001
       ':': 0o032,   # col 0001 row 1010
       ',': 0o033,   # col 0001 row 1011
       '(': 0o034,   # col 0001 row 1100
       '-': 0o040,   # col 0010 row 0000
       'J': 0o041,   # col 0010 row 0001
       'K': 0o042,   # col 0010 row 0010
       'L': 0o043,   # col 0010 row 0011
       'M': 0o044,   # col 0010 row 0100
       'N': 0o045,   # col 0010 row 0101
       'O': 0o046,   # col 0010 row 0110
       'P': 0o047,   # col 0010 row 0111
       'Q': 0o050,   # col 0010 row 1000
       'R': 0o051,   # col 0010 row 1001
       '$': 0o053,   # col 0010 row 1011
       '*': 0o054,   # col 0010 row 1100
       '+': 0o060,   # col 0011 row 0000
       'A': 0o061,   # col 0011 row 0001
       'B': 0o062,   # col 0011 row 0010
       'C': 0o063,   # col 0011 row 0011
       'D': 0o064,   # col 0011 row 0100
       'E': 0o065,   # col 0011 row 0101
       'F': 0o066,   # col 0011 row 0110
       'G': 0o067,   # col 0011 row 0111
       'H': 0o070,   # col 0011 row 1000
       'I': 0o071,   # col 0011 row 1001
       '.': 0o073,   # col 0011 row 1011
       ')': 0o074,   # col 0011 row 1100
}

# ---------------------------------------------------------------------
# 89 Character Set -- STRAP entry mode IQS, the console typewriter.
# Bit 0 is zero throughout; bit 7 selects case for the letter pairs.
# ---------------------------------------------------------------------
IQS = {
       ' ': 0o000,   # col 0000 row 0000
       '&': 0o040,   # col 0010 row 0000
       '+': 0o041,   # col 0010 row 0001
       '$': 0o042,   # col 0010 row 0010
       '=': 0o043,   # col 0010 row 0011
       '*': 0o044,   # col 0010 row 0100
       '(': 0o045,   # col 0010 row 0101
       '/': 0o046,   # col 0010 row 0110
       ')': 0o047,   # col 0010 row 0111
       ',': 0o050,   # col 0010 row 1000
       ';': 0o051,   # col 0010 row 1001
       "'": 0o052,   # col 0010 row 1010
       '"': 0o053,   # col 0010 row 1011
       'a': 0o054,   # col 0010 row 1100
       'A': 0o055,   # col 0010 row 1101
       'b': 0o056,   # col 0010 row 1110
       'B': 0o057,   # col 0010 row 1111
       'c': 0o060,   # col 0011 row 0000
       'C': 0o061,   # col 0011 row 0001
       'd': 0o062,   # col 0011 row 0010
       'D': 0o063,   # col 0011 row 0011
       'e': 0o064,   # col 0011 row 0100
       'E': 0o065,   # col 0011 row 0101
       'f': 0o066,   # col 0011 row 0110
       'F': 0o067,   # col 0011 row 0111
       'g': 0o070,   # col 0011 row 1000
       'G': 0o071,   # col 0011 row 1001
       'h': 0o072,   # col 0011 row 1010
       'H': 0o073,   # col 0011 row 1011
       'i': 0o074,   # col 0011 row 1100
       'I': 0o075,   # col 0011 row 1101
       'j': 0o076,   # col 0011 row 1110
       'J': 0o077,   # col 0011 row 1111
       'k': 0o100,   # col 0100 row 0000
       'K': 0o101,   # col 0100 row 0001
       'l': 0o102,   # col 0100 row 0010
       'L': 0o103,   # col 0100 row 0011
       'm': 0o104,   # col 0100 row 0100
       'M': 0o105,   # col 0100 row 0101
       'n': 0o106,   # col 0100 row 0110
       'N': 0o107,   # col 0100 row 0111
       'o': 0o110,   # col 0100 row 1000
       'O': 0o111,   # col 0100 row 1001
       'p': 0o112,   # col 0100 row 1010
       'P': 0o113,   # col 0100 row 1011
       'q': 0o114,   # col 0100 row 1100
       'Q': 0o115,   # col 0100 row 1101
       'r': 0o116,   # col 0100 row 1110
       'R': 0o117,   # col 0100 row 1111
       's': 0o120,   # col 0101 row 0000
       'S': 0o121,   # col 0101 row 0001
       't': 0o122,   # col 0101 row 0010
       'T': 0o123,   # col 0101 row 0011
       'u': 0o124,   # col 0101 row 0100
       'U': 0o125,   # col 0101 row 0101
       'v': 0o126,   # col 0101 row 0110
       'V': 0o127,   # col 0101 row 0111
       'w': 0o130,   # col 0101 row 1000
       'W': 0o131,   # col 0101 row 1001
       'x': 0o132,   # col 0101 row 1010
       'X': 0o133,   # col 0101 row 1011
       'y': 0o134,   # col 0101 row 1100
       'Y': 0o135,   # col 0101 row 1101
       'z': 0o136,   # col 0101 row 1110
       'Z': 0o137,   # col 0101 row 1111
       '0': 0o140,   # col 0110 row 0000
       '1': 0o142,   # col 0110 row 0010
       '2': 0o144,   # col 0110 row 0100
       '3': 0o146,   # col 0110 row 0110
       '4': 0o150,   # col 0110 row 1000
       '5': 0o152,   # col 0110 row 1010
       '6': 0o154,   # col 0110 row 1100
       '7': 0o156,   # col 0110 row 1110
       '8': 0o160,   # col 0111 row 0000
       '9': 0o162,   # col 0111 row 0010
       '.': 0o164,   # col 0111 row 0100
       ':': 0o165,   # col 0111 row 0101
       '-': 0o166,   # col 0111 row 0110
       '?': 0o167,   # col 0111 row 0111
}

# The ten italic digits of the 89 set, column 0111, odd rows.  They
# share their spelling with the upright digits in column 0110, so they
# cannot live in IQS; nothing in MCP's listing asks for them.
IQS_ITALIC_DIGITS = {
    '0': 0o141, '1': 0o143, '2': 0o145, '3': 0o147, '4': 0o151,
    '5': 0o153, '6': 0o155, '7': 0o157, '8': 0o161, '9': 0o163,
}

# STRAP entry modes this assembler can convert, by name.  CC is
# deliberately absent: see the module docstring.
ENTRY_MODES = {
    'A':   A,
    'IQS': IQS,
}
