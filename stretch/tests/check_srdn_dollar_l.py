#!/usr/bin/env python3
"""check_srdn_dollar_l.py -- "SRDN,$L" is the VFL STORE ROUNDED, (BU,64,8),
offset 0, in both assemblers, because $L carries a VFL dds.

THE QUESTION (docs/NEXT.md, the location-8 items): C22-6578 printed p.43
ends COSF, Problem 4.9 Method 1, with "SRDN,$L" (Method 2, the same page,
prints "SRD(N), $L", with the floating dds).  SRDN is both a VFL
and a floating-point mnemonic (C22-6531 Appendix A printed p.57: "V SRD 5"
and "F SRD 7"; footnote 5 gives the VFL form an N suffix, footnote 7 the
floating form N, A and NA).  If STRAP gave $L a floating-point dds the
statement would be the floating SRD the analysis wants; if not, the VFL one.

SETTLED FROM THE INK, 2026-11-16 (page images; C28-6129 has no text layer
worth trusting):
  C28-6129 printed p.10 (PDF 14), class 2, "Special Register Symbols":
    "STRAP also assigns a data description to each symbol with a use mode
    of binary unsigned (BU), a byte size of 8 and a field length equal to
    the length of the register.  When a system symbol for a special
    register appears in the principal address field of a VFL instruction,
    no data description need be explicitly written out in that
    instruction."  The table under it: "Left half of accumulator  $L  8.0".
    Its own example: "L, $IND ... the dds (BU, 64, 8) has been attached to
    the system symbol."
  C28-6129 printed p.6 (PDF 10): "in cases where the operation mnemonic is
    the same for VFL and floating point instructions, it is the data
    description that tells STRAP to which class the operation belongs".
  C22-6531 (STRAP I) printed p.56 (PDF 57): "$ L 1 Left Half of
    Accumulator 8 0-63", footnote 1 (printed p.58): "This mnemonic is a
    system symbol.  It must be prefixed by the character "$" whenever
    used."  No dds; STRAP I's rule for an op that "could be either VFL or
    floating-point" is C22-6578 printed p.30's "assumed VFL".
So under both assemblers "SRDN,$L" is VFL SRD, (BU,64,8), at offset 0 --
and by the Reference Manual (printed p.64) "A STORE ROUNDED with zero offset
specified is equivalent to a STORE": it stores the accumulator's right half,
bits 64-127, into word 8.  The book's COSF is wrong in the ink.  Nothing in
either assembler needed fixing; this pins it.

Checks:
  sym_dds     strap2's system-symbol look-up gives $L word 8.0 and
              (BU,64,8) -- the dds the class follows from
  srdn_word   strap2 and strap_asm: "SRDN,$L" assembles to the word of
              "SRDN(BU,64,8),$L" and not to "SRDN(N),$L"'s
  srdn_fields that word decoded by the model's own field positions
              (bsv/StretchDecode.bsv vflAddrOf/decodeFullWord): address
              8.0, length 64, byte size 8, offset 0, unsigned, negative,
              binary, code 101101
  p10_oracle  C28-6129 p.10's printed example: "L, $IND" is
              "L(BU,64,8), $IND", in both

MEASURED INJECTIONS (each on a copy, reverted by cmp):
  strap2 optable.system_symbol gives the registers dds13("N", 0, 8)
      FAIL sym_dds; FAIL srdn_word (strap2) -- p.6's rule then makes it
      the floating SRDN; srdn_fields (strap2) and p10_oracle (strap2) fail
      with it.  strap_asm's lines pass (it takes p.7's no-dds case 1).
"""
import io
import os
import sys
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
with contextlib.redirect_stdout(io.StringIO()):
    import strap_asm as A                   # noqa: E402
    import strap2                           # noqa: E402
    from strap2 import optable              # noqa: E402

fails = 0


def check(label, ok, detail=""):
    global fails
    print("%s %s%s" % ("PASS" if ok else "FAIL", label, (" -- " + detail) if detail else ""))
    if not ok:
        fails += 1


def word(asm, stmt):
    src = "        SLC, 1000.0\nA       %s\n        END, A\n" % stmt
    with contextlib.redirect_stdout(io.StringIO()):
        p = asm(src)
    return p.words[1000]


ASMS = [("strap2", lambda s: strap2.assemble(s, strict=True)),
        ("strap_asm", A.assemble)]

got = optable.system_symbol("L")
check("sym_dds $L is 8.0, (BU,64,8)",
      got == (8 * 64, optable.dds13("BU", 0, 8)),
      "got %r" % (got,))

for name, asm in ASMS:
    w = word(asm, "SRDN,$L")
    vfl = word(asm, "SRDN(BU,64,8),$L")
    fp = word(asm, "SRDN(N),$L")
    check("srdn_word %s: SRDN,$L = SRDN(BU,64,8),$L" % name,
          w == vfl and w != fp,
          "%016x, VFL %016x, FP %016x" % (w, vfl, fp))
    # StretchDecode.bsv: addr w[63:40], i1 w[35:32], p w[31:29],
    # length w[28:23] (0 = 64), bs w[22:20] (0 = 8), offset w[19:13],
    # op9 w[12:4] = unsign, invert, decimal, code6.
    f = dict(addr=w >> 40, i1=(w >> 32) & 15, p=(w >> 29) & 7,
             length=(w >> 23) & 63, bs=(w >> 20) & 7, offset=(w >> 13) & 127,
             unsign=(w >> 12) & 1, invert=(w >> 11) & 1, decimal=(w >> 10) & 1,
             code=(w >> 4) & 63)
    want = dict(addr=8 * 64, i1=0, p=0, length=0, bs=0, offset=0,
                unsign=1, invert=1, decimal=0, code=0b101101)
    check("srdn_fields %s: 8.0, (BU,64,8), offset 0, N, code 101101" % name,
          f == want, "got %r" % f)
    check("p10_oracle %s: L, $IND = L(BU,64,8), $IND" % name,
          word(asm, "L, $IND") == word(asm, "L(BU,64,8), $IND"))

print("ALL CHECKS PASSED" if not fails else "FAILED (%d)" % fails)
sys.exit(1 if fails else 0)
