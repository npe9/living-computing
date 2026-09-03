#!/usr/bin/env python3
"""verify_ibox1_listing.py -- assemble I-Box 1's WEN2/WEN/VEN routines
VERBATIM (docs/ja_ax1a_ibox-1.pdf p.51, plus their WEN6/WEN7 constants
from p.59) at the listing's own octal addresses, via SLC, and compare
every assembled half-word bit-for-bit against the machine code the
1961 listing itself prints beside each source line.

This is the strongest oracle this project has for the assembler's
encodings: not a value the model computes at run time, but the actual
output of IBM's own STRAP on the same source, read off the page. It
is also the first test that exercises SLC for its real purpose --
placing a historical routine at the address it was assembled at, far
above this assembler's default origin (word 32) and above the
256-word simulated core the model had before MemWords was raised.

Listing print format, worked out from the page (each half-word prints
as three columns): bits 0-17 as a 6-digit OCTAL word address, then
bits 18-23 as 2 OCTAL digits after a ".", then bits 24-31 as 2 HEX
digits. A full-word instruction prints as two such groups. E.g. WEN2's
Load, "6103.00 80 000000.20 50": word address 6103 (octal, = WEN7),
bits 18-23 = 00, bits 24-31 = 0x80, then 0, 0o20, 0x50 for the second
half. The same convention is checked here against the branch and BD
half-words too, which pin down the half-word bit (a target of
"$+1.0" from 5455.00 printing as 5456.35, not 5456.00: bit 18 is the
half-word select, bits 19-23 hold the top of the indicator/op field).

Run standalone: `./verify_ibox1_listing.py`. Wired into run_tests.sh.
"""

import sys

from strap_asm import assemble

# Transcribed verbatim from p.51 (WEN2/WEN/VEN block, "START OF TEST"),
# with the octal location column and both machine-code columns. The
# constants' definitions (p.59) print no machine-code column for
# all-zero/all-one data worth checking beyond their addresses.
SOURCE = """
        SLC, 2860.0            ! octal 5454.0
WEN2    L(BU,64,8), WEN7       ! -LOAD ONES
        BRGZZ, $+1.0
        BD, $
        SLC, 2862.0            ! octal 5456.0
WEN     L(BU,64,8), WEN6       ! -LOAD ZEROS
        BRZZ, $+1.0
        BD, $
        SLC, 2864.0            ! octal 5460.0
VEN     L(BU,64,8), WEN7
        BRGZZ, $+1.0
        BD, $
        SLC, 3138.0            ! octal 6102.0
WEN6    DD(BU,64,8), 0
WEN7    DD(BU,64,8), 18446744073709551615
        END, WEN2
"""

# (octal location, printed machine code) -- one entry per half-word as
# the listing prints them; a full-word instruction's two groups are
# joined here into one entry at its word address.
LISTING = [
    ("005454.00", "006103.00 80 000000.20 50"),  # WEN2  L%BU,64,8=,WEN7
    ("005455.00", "005456.35 46"),               #       BRGZZ,$+1.0
    ("005455.40", "005455.44 00"),               #       BD,$
    ("005456.00", "006102.00 80 000000.20 50"),  # WEN   L%BU,64,8=,WEN6
    ("005457.00", "005460.34 C6"),               #       BRZZ,$+1.0
    ("005457.40", "005457.44 00"),               #       BD,$
    ("005460.00", "006103.00 80 000000.20 50"),  # VEN   L%BU,64,8=,WEN7
    ("005461.00", "005462.35 46"),               #       BRGZZ,$+1.0
    ("005461.40", "005461.44 00"),               #       BD,$
]

SYMBOLS = {"WEN2": "005454.00", "WEN": "005456.00", "VEN": "005460.00",
           "WEN6": "006102.00", "WEN7": "006103.00"}


def fmt_half(h):
    return f"{h >> 14:06o}.{(h >> 8) & 0x3F:02o} {h & 0xFF:02X}"


def loc_bits(octal_loc):
    w, b = octal_loc.split(".")
    return int(w, 8) * 64 + int(b, 8)


def main():
    fails = 0
    prog = assemble(SOURCE)
    for name, loc in SYMBOLS.items():
        got, want = prog.symtab[name], loc_bits(loc)
        status = "PASS" if got == want else "FAIL"
        fails += status == "FAIL"
        print(f"{status} {name} at {loc} (octal) = bit {got}, listing says {want}")
    for loc, printed in LISTING:
        bits = loc_bits(loc)
        word = prog.words.get(bits // 64, 0)
        if bits % 64 == 0 and len(printed) > 12:
            got = f"{fmt_half(word >> 32)} {fmt_half(word & 0xFFFFFFFF)}"
        else:
            half = (word >> 32) if bits % 64 == 0 else (word & 0xFFFFFFFF)
            got = fmt_half(half)
        status = "PASS" if got == printed else "FAIL"
        fails += status == "FAIL"
        print(f"{status} {loc}: assembled {got!r}, listing prints {printed!r}")
    if fails:
        print(f"{fails} TEST(S) FAILED")
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
