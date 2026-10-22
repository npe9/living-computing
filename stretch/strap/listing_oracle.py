#!/usr/bin/env python3
"""listing_oracle.py -- compare what strap_asm.py assembles against the
machine code a historical STRAP listing prints beside each source
line. IBM's own assembler output, read off the page, is the strongest
encoding oracle this project has: it checks bit placement of every
field with no dependence on the Bluespec model at all.

Listing print format (worked out from docs/ja_ax1a_ibox-1.pdf p.51 and
confirmed on docs/jb_ax4b_ibox-4.pdf pp.155/159): each HALF-WORD
prints as three columns -- bits 0-17 as a 6-digit OCTAL word address
(leading zeros dropped), then "." and bits 18-23 as 2 OCTAL digits,
then a space and bits 24-31 as 2 HEX digits. So bit 18, the half-word
select of a branch target, is the top bit of the octal pair: a target
at 5455.40 prints as "5455.44 00", one at 5456.00 as "5456.35 46". A
full-word instruction or XW prints as two such groups. Two other row
shapes occur:
  - VF prints its 24-bit value as W.B (octal) followed by the sign,
    "777777.70+" -- only the value field and sign bit are printed.
  - DD(BU,64,8) prints the whole word as 22 octal digits, and
    DD(BU,32,8) prints its half-word as 11 (jb_ax5b p.43).

Usage: build a list of (octal location, printed text) rows transcribed
from the page, assemble the verbatim source (placed at the listing's
own addresses via SLC, with any symbol defined outside the transcribed
range given by SYN from its printed address), and call check_rows().
Rows whose operand is such an external symbol verify only the opcode/
modifier bits, since the address part came from the same print -- the
caller should say which rows those are; rows naming symbols defined
INSIDE the transcribed range are the real check of address placement.
"""

import sys


def fmt_half(h):
    return f"{h >> 14:06o}.{(h >> 8) & 0x3F:02o} {h & 0xFF:02X}"


def loc_bits(octal_loc):
    """'011445.40' (octal word . octal bit) -> bit count."""
    w, b = octal_loc.split(".")
    return int(w, 8) * 64 + int(b, 8)


def word_at(prog, bits):
    """The 64 bits starting at half-word-aligned bit offset `bits`. A
    full-word INSTRUCTION may sit at an odd half-word (bits % 64 == 32),
    in which case it straddles two words -- bits 32-63 of word N hold
    the instruction's bits 0-31, and bits 0-31 of word N+1 hold its bits
    32-63 (Reference Manual p.39). See strap_asm.Image.deposit_word_instr."""
    if bits % 64 == 0:
        return prog.words.get(bits // 64, 0)
    hi = prog.words.get(bits // 64, 0) & 0xFFFFFFFF
    lo = prog.words.get(bits // 64 + 1, 0) >> 32
    return (hi << 32) | lo


def read_bits(prog, bits, width):
    """The `width` bits starting at bit-count `bits`, as an integer."""
    out = 0
    for i in range(width):
        w, b = divmod(bits + i, 64)
        out = (out << 1) | ((prog.words.get(w, 0) >> (63 - b)) & 1)
    return out


def render(prog, octal_loc, printed, width=None):
    """Render the assembled content at octal_loc in the same shape as
    the listing's printed text, so the two compare as strings.

    `width` is the datum's width IN BITS, and callers pass it for a
    DD whose printed form is bare octal digits.  THE DIGIT COUNT DOES
    NOT DETERMINE THE WIDTH: a three-digit group is 7, 8 or 9 bits
    and the listing prints the same three digits for all of them, so
    guessing from the print is guessing.  MCP printed p.35's
    equipment table has DD(BU,24), DD(BU,4) and DD(BU,1) adjacent --
    8, 2 and 1 digits -- and reading 9 bits where the deck wrote 4
    would silently pull in the next datum's bits.  The widths the
    oracle guesses (3 -> 8, 6 -> 18, 11 -> 32, 22 -> 64) are kept for
    the callers that predate this and are the only widths those
    programs use."""
    bits = loc_bits(octal_loc)
    word = prog.words.get(bits // 64, 0)
    half = (word >> 32) if bits % 64 == 0 else (word & 0xFFFFFFFF)
    toks = printed.split()
    if width is not None:
        if len(toks) != 1 or not all(c in "01234567" for c in toks[0]):
            raise ValueError(
                f"width given for a row whose printed form is not bare "
                f"octal digits: {printed!r}")
        return f"{read_bits(prog, bits, width):0{-(-width // 3)}o}"
    if len(toks) == 1 and printed[-1] in "+-":
        # VF: 24-bit value as W.B octal, then the sign bit.
        mag, sign = half >> 8, (half >> 7) & 1
        return f"{mag >> 6:06o}.{mag & 0x3F:02o}{'-' if sign else '+'}"
    if len(toks) == 1 and len(toks[0]) == 22:
        return f"{word:022o}"
    if (len(toks) == 1 and len(toks[0]) == 3
            and all(c in "01234567" for c in toks[0])):
        # AN 8-BIT DD, printed as three octal digits.  MCP's printed
        # p.9 writes the control codes around every console message
        # this way -- "DD(BU,8),(2)1111 1101" prints 375.
        #
        # This one cannot use `half`: an 8-bit datum sits at an
        # arbitrary bit offset (p.9 puts them at 000254.00 and
        # 000254.10), so the byte is cut out of the word by hand.
        off = bits % 64
        return f"{(word >> (64 - off - 8)) & 0xFF:03o}"
    if (len(toks) == 1 and len(toks[0]) == 6
            and all(c in "01234567" for c in toks[0])):
        # A COUNT OR REFILL FIELD, printed as six octal digits and
        # nothing else -- no bit position, no sign, no hex byte.
        # C22-6531 printed p.19: CF "COUNT FIELD" compiles "an 18-bit
        # integer in POSITIONS 0-17" of the half word it rounded to,
        # and RF is the same with Refill substituted; the same page
        # gives both the data description (BU,18).  Eighteen bits is
        # six octal digits exactly, which is why the listing can print
        # one without any of the punctuation the other field pseudo-
        # ops need.
        #
        # MCP printed p.26 lines 16 and 30 are the first in this
        # corpus: "CF,1.0" and "CF,1", both printing 000001.
        return f"{(half >> 14) & 0x3FFFF:06o}"
    if len(toks) == 1 and len(toks[0]) == 11:
        # DD(BU,32,8): the listing prints a 32-bit datum as its own
        # half-word, 11 octal digits (jb_ax5b p.43's "00000003740").
        return f"{half:011o}"
    if len(toks) == 4 and toks[0][-1] in "+-":
        # AN INDEX WORD OR A CONTROL WORD, which the listing prints in
        # four groups rather than as two half-words:
        #     vvvvvv.vv+ fff cccccc rrrrrr
        # bits 0-23 as word.bit, the sign bit 24 as + or -, the three
        # flag bits 25-27 as three separate digits, the 18-bit count
        # (28-45) and the 18-bit refill/chain address (46-63).
        #
        # ONE RENDERER SERVES BOTH, which is not obvious.  XW's first
        # group is a 24-bit value field; CW's ADDRESS is only 18 bits
        # (0-17) with the status bits 18-24 zero beneath it.  But an
        # 18-bit address sitting in bits 0-17 IS addr << 6 read as 24
        # bits, so printing bits 0-23 as word.bit gives the address in
        # the word position and .00 in the bit position either way.
        # Verified against MCP printed p.2's CW (000041.00+ 000 000560
        # 000001) and p.14's CW(CDSC) (011406.00+ 110 001001 000553).
        w = word_at(prog, bits)
        val = (w >> 40) & 0xFFFFFF          # bits 0-23
        sign = (w >> 39) & 1                 # bit 24
        f = (w >> 36) & 0x7                  # bits 25-27
        count = (w >> 18) & 0x3FFFF          # bits 28-45
        refill = w & 0x3FFFF                 # bits 46-63
        return (f"{val >> 6:06o}.{val & 0x3F:02o}{'-' if sign else '+'} "
                f"{(f >> 2) & 1}{(f >> 1) & 1}{f & 1} "
                f"{count:06o} {refill:06o}")

    if len(toks) == 4:
        # A full-word instruction, read across the word boundary if it
        # is at an odd half-word.
        w = word_at(prog, bits)
        return f"{fmt_half(w >> 32)} {fmt_half(w & 0xFFFFFFFF)}"
    return fmt_half(half)


def norm(printed):
    """Zero-pad the listing's word-address columns to 6 octal digits
    (the page drops leading zeros: '0.30 00', '5456.35 46')."""
    out = []
    for tok in printed.split():
        if "." in tok:
            w, rest = tok.split(".", 1)
            tok = f"{int(w, 8):06o}.{rest}"
        out.append(tok)
    return " ".join(out)


def check_rows(prog, rows, symbols=None, label=""):
    """rows: [(octal_loc, printed, note)] -- note is free text shown in
    the PASS/FAIL line (e.g. the source line). symbols: {NAME: octal
    location} the assembled symbol table must reproduce. Returns the
    number of failures, printing one PASS/FAIL line per check."""
    fails = 0
    for name, loc in (symbols or {}).items():
        got, want = prog.symtab[name], loc_bits(loc)
        ok = got == want
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {label}{name} at {loc}: assembled bit {got}, listing bit {want}")
    for row in rows:
        # A row is (location, printed text, note) and may carry a
        # fourth element, the datum's WIDTH IN BITS, for a DD printed
        # as bare octal digits -- see render().
        loc, printed, note = row[0], row[1], row[2]
        width = row[3] if len(row) > 3 else None
        want = norm(printed)
        got = render(prog, loc, want, width)
        ok = got == want
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {label}{loc} {note}: assembled {got!r}, listing {want!r}")
    return fails


def finish(fails):
    if fails:
        print(f"{fails} TEST(S) FAILED")
        sys.exit(1)
    print("ALL TESTS PASSED")
