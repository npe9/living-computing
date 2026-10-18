#!/usr/bin/env python3
"""test_fields.py -- pure-Python regression test for strap_asm.py's
address-field unit rules and system symbols, each pinned to a row of
IBM's own assembler output in the I-Box 4 listing (docs/jb_ax4b_ibox-4
.pdf pp.58-62, 191-192), rendered in listing_oracle.py's print format.

C22-6531 p.11: integers "add into all fields as integers; that is, the
units digit adds into the low-order position of the field", bit
addresses convert to the field's units. So the SAME integer means a
word in LX/SX (18-bit word-address field, p.24), a half-word in every
other branch/direct-index field, and a word in XW's refill field.
System symbols: C22-6531 Appendix A (p.56) -- $R is word 9, the right
half of the accumulator, which is what section 138's "KV,$X15,$R"
compares against.

Run standalone: `./test_fields.py`. Wired into run_tests.sh.
"""

import sys
from strap_asm import assemble
from listing_oracle import fmt_half

FAILS = 0


def check(label, src, printed, half=0):
    """Assemble one statement at word 100 and compare its (first or
    second) half-word with the listing's printed form."""
    global FAILS
    p = assemble("        SLC, 100.0\nX       " + src + "\n        END, X\n")
    w = p.words.get(100, 0)
    got = fmt_half(w >> 32) if half == 0 else fmt_half(w & 0xFFFFFFFF)
    if len(printed.split()) == 4:
        got = f"{fmt_half(w >> 32)} {fmt_half(w & 0xFFFFFFFF)}"
    want = printed
    ok = got == want
    FAILS += not ok
    print(f"{'PASS' if ok else 'FAIL'} {label}: {src!r} -> {got!r}, listing {want!r}")


# I-Box 4 p.58, routine 1381
check("SX integer = word",        "SX,$X0,8",        "000010.01 10")
check("SV integer = half-word",   "SV,$X0,2",        "000001.01 30")
check("SV odd half-word",         "SV,$X1,1",        "000000.43 30")
check("LX integer 0",             "LX,$X1,0",        "000000.02 10")
check("LX octal integer = word",  "LX,$X0,(8)40",    "000040.00 10")
check("R,$X15 (word 31)",         "R,$X15",          "000037.02 00")
check("KVI radix bit address",    "KVI,$X15,(8)0.40","000000.77 04")
check("SR,$X15,$X14 (word 30)",   "SR,$X15,$X14",    "000036.37 70")
check("KV,$X15,$R ($R = word 9)", "KV,$X15,$R",      "000011.36 90")
check("SC,$X15,$X1",              "SC,$X15,$X1",     "000021.37 50")
check("L(BU),$X15 (word 31)",     "L(BU),$X15",      "000037.00 80 000000.20 50")
check("L(BU),4 = bit 4 (24-bit field, raw)", "L(BU),4", "000000.04 80 000000.20 50")
check("L(BU),(8)40.0",            "L(BU),(8)40.0",   "000040.00 80 000000.20 50")
# p.192 / p.191 data
check("XW refill integer = word", "XW,0,0,16",       "000000.00 00 000000.00 10")
check("XW count integer",         "XW,0,512,0",      "000000.00 00 020000.00 00")
check("XW value octal address",   "XW,(8)20.00,0,0", "000020.00 00 000000.00 00")
# other Appendix A symbols
check("$UB = 3.0",  "LC,$X1,$UB",   "000003.02 50")
check("$LB = 3.32", "LC,$X1,$LB",   "000003.42 50")
check("$IND+.32 = 11.32", "SR,$X1,$IND+.32", "000013.43 70")

if FAILS:
    print(f"{FAILS} TEST(S) FAILED"); sys.exit(1)
print("ALL TESTS PASSED")
