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
  - DD(BU,64,8) prints the whole word as 22 octal digits.

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


def render(prog, octal_loc, printed):
    """Render the assembled content at octal_loc in the same shape as
    the listing's printed text, so the two compare as strings."""
    bits = loc_bits(octal_loc)
    word = prog.words.get(bits // 64, 0)
    half = (word >> 32) if bits % 64 == 0 else (word & 0xFFFFFFFF)
    toks = printed.split()
    if len(toks) == 1 and printed[-1] in "+-":
        # VF: 24-bit value as W.B octal, then the sign bit.
        mag, sign = half >> 8, (half >> 7) & 1
        return f"{mag >> 6:06o}.{mag & 0x3F:02o}{'-' if sign else '+'}"
    if len(toks) == 1 and len(toks[0]) == 22:
        return f"{word:022o}"
    if len(toks) == 4:
        return f"{fmt_half(word >> 32)} {fmt_half(word & 0xFFFFFFFF)}"
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
    for loc, printed, note in rows:
        want = norm(printed)
        got = render(prog, loc, want)
        ok = got == want
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {label}{loc} {note}: assembled {got!r}, listing {want!r}")
    return fails


def finish(fails):
    if fails:
        print(f"{fails} TEST(S) FAILED")
        sys.exit(1)
    print("ALL TESTS PASSED")
