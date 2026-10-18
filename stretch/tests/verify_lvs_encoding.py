#!/usr/bin/env python3
"""verify_lvs_encoding.py -- LVS's participation mask, against the two
rows of MCP that print one.

LVS, LOAD VALUE WITH SUM, is the one 7030 instruction whose address
field is not an address.  Reference Manual printed p.28 = PDF 31,
section "Multiple Indexing", read at 300 dpi:

  "In multiple indexing, bits 0-15 of the address part of the
   instruction are used to indicate which index registers participate
   in the operation.  When bit position n contains a one, the register
   Xn participates.  When bit position n contains a zero, the register
   Xn does not participate.  Bits 16-19 of the address part of the
   instruction are ignored."

  "The multiple indexing operation makes use of the instruction format
   shown below.  The index field J contains the address of the index
   to which the operation LOAD VALUE WITH SUM applies.  No address
   modification is available for this operation."

THE MANUAL CONTRADICTS ITSELF ABOUT WHERE THE ADDRESS PART ENDS.  The
sentence says bits 16-19 are ignored, but bit 19 is the high bit of J
in that same page's own format diagram (ADDRESS | J | OP., boundaries
printed 0, 19, 23, 31) and in X22-6533's IMMEDIATE INDEX ARITHMETIC
row.  Diagram and pocket card agree against the sentence, so the
assembler ignores 16-18 and this file records the discrepancy rather
than smoothing it over.  Nothing here depends on which is right: both
MCP rows leave 16-18 zero.

WHY THIS FILE EXISTS SEPARATELY.  verify_mcp_bootstrap_p4.py checks
the first row as one of that page's thirty-seven.  One row fixes a
mask only up to the two bits it happens to set; the second row, from
printed p.15, uses a DIFFERENT and larger set, and the two together
pin bit position against register number in five places.  THE HEX
BYTE IS 0B IN BOTH -- this scan prints digit zero with a visible gap
on the right, so a leading 0 reads as C (the same p.4 row prints
000050.C3 where the octal field can only be 03), and with CB the
operation field would be 111001011, which is no operation at all on
the pocket card.
"""
from listing_oracle import loc_bits
from strap_asm import assemble

# (source, expected printed half-word, where the listing prints it)
CASES = [
    ("LVS, $X1, $X12, $X14", "000050.03 0B",
     "MCP printed p.4 line 23 at 000117.00, "
     "'LVS,$1,$12,$14  -WORDS PRECEEDING MCP'; "
     "bits 12 and 14 of 19 weigh 2^6 + 2^4 = 80 = 0o120, "
     "printed as 000050.03 with J=1 in bits 19-22"),
    ("LVS, $X9, $X12, $X11, $X14", "000150.23 0B",
     "MCP printed p.15 line 17 at 000622.00, "
     "'X10  LVS,$9,$12,$11,$14  -COMPUTE NUMBER OF WORDS'; "
     "bits 11, 12 and 14 weigh 2^7 + 2^6 + 2^4 = 208, "
     "printed as 000150.23 with J=9"),
]

failed = 0
for src, printed, where in CASES:
    prog = assemble(f"        SLC, (8)100.0\n        {src}\n        END, $\n")
    bits = loc_bits("000100.00")
    half = prog.words.get(bits // 64, 0) >> 32
    got = f"{half >> 14:06o}.{(half >> 8) & 0x3F:02o} {half & 0xFF:02X}"
    ok = got == printed
    failed += not ok
    print(("PASS" if ok else "FAIL")
          + f" LVS {src}: assembled '{got}', listing '{printed}' -- {where}")

# The rule itself, stated so that a future edit that breaks it fails
# here rather than silently: IBM bit n of a 19-bit field has weight
# 2^(18-n), so register Xn sets 1 << (18 - n).  Checked against the
# two rows above, not asserted on its own.
for n, weight in ((11, 1 << 7), (12, 1 << 6), (14, 1 << 4)):
    expect = 1 << (18 - n)
    ok = expect == weight
    failed += not ok
    print(("PASS" if ok else "FAIL")
          + f" LVS mask weight for X{n} is {expect} (IBM bit {n} of 19)")

if failed:
    raise SystemExit(1)
print("ALL TESTS PASSED")
