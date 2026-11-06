#!/usr/bin/env python3
"""DD(N) floating words, and "1.E14" as a fixed-point integer.

C28-6129 printed p.28 (PDF p.32), "Normalized Floating Point": a
DD(N) entry "is converted to a normalized floating binary number
consisting of an 11-bit signed exponent, a 48-bit fraction, and a
4-bit sign byte", with an optional S (sign byte, octal) and X (machine
exponent, decimal) suffix (printed p.27).  printed p.27 defines the E
suffix ("multiply the number that precedes it by the power of 10").
printed p.29: a B/BU entry with no entry mode "must be a decimal
integer, but may in this case be written with the aid of the E
notation".  Reference Manual 22-6530-2 printed pp.78-79: EF bit 0, EM
bits 1-10, ES bit 11, fraction 12-59, S 60, TUV 61-63.  printed p.28:
floating entries are compiled at full words.

The oracle is MCP printed p.359 (docs/MCP_Mar63_250-445.pdf PDF
p.109) lines 33-43, and the manual's own Figure 3 (C28-6129 printed
p.19), whose "DOG DD(N),28671X7,183007S7" prints "0007+
6777700000000000 +000" and "0022+ 5453370000000000 +TUV".  An expected
word is built from the printed fields: (EF/EM << 53) | (ES << 52) |
(fraction << 4) | (S << 3) | TUV.

CHECKS
  p359_l33_1e1 .. p359_l39_1e64   line 33's card, AFL10 DD(N),1.E1,
                                  1.E2,1.E4,1.E8,1.E16,1.E32,1.E64, its
                                  seven words (lines 33-39)
  p359_l40_1e128                  DD(N),1.E128 = line 40's word
  p359_l43_a1e14                  DD(BU,48),1.E14 = 2657142036440000
  fig3_x7                         DD(N),28671X7 = 0007+ 67777.. +000
  fig3_s7                         DD(N),183007S7 = 0022+ 545337.. +TUV
  dd_n_aligns_to_word             a DD(N) after a half-word B lands on
                                  the next full word
  UNREPRODUCED (reported FAIL, not counted in the exit status):
  p359_l41_1e512                  DD(N),1.E512 printed 3246+ 0..0 +000
  p359_l42_9e615                  DD(N),9.99999E615 printed 3246+
                                  7364320000000000 +000
    Both lie outside printed p.27's 10^+-308, which the assembler
    refuses; no cited rule gives the printed words (EF with EM 678 for
    two different numbers; exact exponents are 1701 and 2047).

MEASURED INJECTIONS (python3 check_dd_float.py --inject):
    control, assembler as is            PASS (12/12; the two
                                         UNREPRODUCED rows FAIL as
                                         expected)
    truncation -> round half up         FAIL p359_l38_1e32,
                                             p359_l39_1e64,
                                             p359_l40_1e128
    DD(N) not routed to the float rule  FAIL p359_l33_1e1 ..
                                             p359_l39_1e64,
                                             p359_l40_1e128, fig3_x7,
                                             fig3_s7
    E-notation integer path removed     FAIL p359_l43_a1e14
    full-word alignment removed         FAIL dd_n_aligns_to_word
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
STRAP = os.path.join(HERE, "..", "strap")
sys.path.insert(0, STRAP)

TRUNC = "frac = (v.numerator << 48) // v.denominator    # truncated: see above"
ROUND = "frac = ((v.numerator << 49) // v.denominator + 1) >> 1"
ROUTE = "    if mode == 'N':\n        return _dd_normalized(field, lineno)\n"
EPATH = "    if dec is not None and not dec[2] and dec[1].denominator == 1:"
ALIGN = "return (64 if _fmode in ('N', 'U') else 0), \\"


def fp(printed):
    """'0004+ 5000000000000000 +000' -> the 64-bit word."""
    e, f, s = printed.split()
    efem, es = int(e[:-1], 8), 1 if e[-1] == '-' else 0
    sb = 1 if s[0] == '-' else 0
    tuv = s[1:]
    tuv = (int(tuv, 8) if tuv.isdigit()
           else (4 if 'T' in tuv else 0) | (2 if 'U' in tuv else 0) | (1 if 'V' in tuv else 0))
    return (efem << 53) | (es << 52) | (int(f, 8) << 4) | (sb << 3) | tuv


P359 = [  # (line, entry, printed) -- MCP printed p.359
    (33, "1.E1", "0004+ 5000000000000000 +000"),
    (34, "1.E2", "0007+ 6200000000000000 +000"),
    (35, "1.E4", "0016+ 4704000000000000 +000"),
    (36, "1.E8", "0033+ 5753604000000000 +000"),
    (37, "1.E16", "0066+ 4341571157602000 +000"),
    (38, "1.E32", "0153+ 4734265552025560 +000"),
    (39, "1.E64", "0325+ 6047403722377717 +000"),
]


def words(asm, cards, n, at=0o144):
    """n words from word `at` after assembling `cards` at word 100(8)."""
    try:
        p = asm.assemble("        SLC, (8)144.0\n" + cards)
    except Exception as e:
        return ["ERROR " + str(e)] * n, None
    return ["%022o" % p.words.get(at + i, 0) for i in range(n)], p


def main(asm):
    fails = 0

    def check(name, got, want, counted=True):
        nonlocal fails
        ok = got == want and not got.startswith("ERROR")
        if counted:
            fails += not ok
        tag = "PASS" if ok else ("FAIL" if counted else "FAIL (UNREPRODUCED, expected)")
        print(f"{tag} {name} = {got}" + ("" if ok else f" expected {want}"))

    card = "AFL10   DD(N)," + ",".join(e for _, e, _ in P359) + "\n"
    got, _ = words(asm, card, len(P359))
    for (line, entry, pr), g in zip(P359, got):
        check(f"p359_l{line}_{entry.replace('.', '').lower()}", g, "%022o" % fp(pr))
    g, _ = words(asm, "        DD(N),1.E128\n", 1)
    check("p359_l40_1e128", g[0], "%022o" % fp("0652+ 4473510762300351 +000"))
    g, _ = words(asm, "A1E14   DD(BU,48),1.E14\n", 1)
    # a 48-bit field at bit 0 of the word: the word is the field << 16
    check("p359_l43_a1e14", g[0], "%022o" % (int("2657142036440000", 8) << 16))
    g, _ = words(asm, "DOG     DD(N),28671X7,183007S7\n", 2)
    check("fig3_x7", g[0], "%022o" % fp("0007+ 6777700000000000 +000"))
    check("fig3_s7", g[1], "%022o" % fp("0022+ 5453370000000000 +TUV"))
    _, p = words(asm, "        B,0\nFL      DD(N),1.E1\n", 1)
    check("dd_n_aligns_to_word",
          "ERROR" if p is None else "bit %d" % p.symtab.get("FL", -1),
          "bit %d" % (0o145 * 64))
    g, _ = words(asm, "        DD(N),1.E512\n", 1)
    check("p359_l41_1e512", g[0], "%022o" % fp("3246+ 0000000000000000 +000"), counted=False)
    g, _ = words(asm, "        DD(N),9.99999E615\n", 1)
    check("p359_l42_9e615", g[0], "%022o" % fp("3246+ 7364320000000000 +000"), counted=False)
    print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
    return fails


def patched(old, new):
    import types
    path = os.path.join(STRAP, "strap_asm.py")
    src = open(path).read()
    assert src.count(old) == 1, old
    m = types.ModuleType("strap_asm_injected")
    m.__file__ = path
    exec(compile(src.replace(old, new), path, "exec"), m.__dict__)
    return m


if __name__ == "__main__":
    import strap_asm
    if sys.argv[1:] == ["--inject"]:
        res = [("control", main(strap_asm))]
        print("-- injected: truncation -> round half up")
        res.append(("round", main(patched(TRUNC, ROUND))))
        print("-- injected: DD(N) not routed to the float rule")
        res.append(("route", main(patched(ROUTE, ""))))
        print("-- injected: E-notation integer path removed")
        res.append(("epath", main(patched(EPATH, "    if False:"))))
        print("-- injected: full-word alignment removed")
        res.append(("align", main(patched(ALIGN, "return 0, \\"))))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main(strap_asm))
