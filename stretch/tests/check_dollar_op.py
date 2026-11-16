#!/usr/bin/env python3
""""$OP" assembles as OP, and PRND is a listing control.

C28-6129 printed p.10 (PDF p.14): "Another special use of the $
character is to prefix any operation code in this manner: $OP.  This
directs the compiler to suppress any error indications that arise in
connection with the compilation of this statement."  MCP prints it on
printed pp.53, 56, 57, 279 and 283 ("$TI,1,-1.0(L IODX),1.0(L XPP)",
"$L(BU,8),-0.8(L IODX),46") and the AX5B test listing prints "$BD,0".
"Any operation code" includes the ones spelled with a sign: printed
p.413 line 9 prints "$-(BU,18),TCHSXW,-60", the VFL subtract, and
strap_asm, which stripped the "$" only before a letter, crashed on it.
Every one prints the plain operation's binary.  Until 2026-11-06
strap_asm refused "$TI" as an unknown mnemonic and seven decks wrote
the card without its "$" -- right bits, wrong text.

C28-6129 printed p.36 (PDF p.40): "PRND -- Print Double Spaced ...
restores printing to the normal double spacing mode after the use of a
PRNS".  MCP printed pp.275 and 285 print it on line 2.  It compiles
nothing.

CHECKS
  dollar_ti_equals_ti     $TI,1,-1.0($3),1.0($4) assembles to TI's word
  dollar_l_equals_l       $L(BU,8),-0.8($3),46 assembles to L's word
  dollar_bd_equals_bd     $BD,0 assembles to BD's word
  dollar_minus_equals_minus  $-(BU,18),200.0,-60 assembles to -'s word
  dollar_kf_equals_kf     $KF(BU,8),200.0 assembles to KF's word
  dollar_cm0000_equals_cm0000  $CM0000(BU,1),200.0 assembles to CM0000's word
  dollar_unknown_is_named $QQQ(BU,8),200.0 is refused by an error that names
                          QQQ (and, in strap_asm, line 2), not a KeyError
  prnd_emits_nothing      PRND before B,0 leaves B,0 at the same word
Run without arguments, the same checks are then made on the host STRAP II
(strap2), whose refusal is "message 1: ILLEGAL OP CODE QQQ" (its strict shim
names no card for a numbered message; not changed here).

$KF AND $CM0000, 2026-11-15.  docs/NEXT.md recorded both on 2026-10-31
(commit abb99dc) as dying with a bare KeyError out of a dispatch dict, and
asked for a diagnostic.  The "$" strip of 2026-11-06 (commit bacf234, from
p.10 above) made them assemble as KF and CM0000, so there is no miss left to
diagnose; the three checks pin that, and that an operation that really is
unknown is named.  Searched 2026-11-15: 318 operation names x {OP, $OP} x
five field shapes on both assemblers, 6360 statements: none raised anything
but AssemblerError/StrapError, none with "KeyError" in its text.

MEASURED INJECTIONS (python3 check_dollar_op.py --inject), strap_asm only,
re-measured 2026-11-15 (the "$" strip's anchor had gone stale: the driver
asserted before injecting; repaired):
    control, assembler as is            PASS
    the "$" strip removed               FAIL dollar_ti_equals_ti,
                                             dollar_l_equals_l,
                                             dollar_bd_equals_bd,
                                             dollar_minus_equals_minus,
                                             dollar_kf_equals_kf,
                                             dollar_cm0000_equals_cm0000
    the sign characters dropped from    FAIL dollar_minus_equals_minus
      the "$" strip's guard
    PRND taken out of LISTING_CONTROL   FAIL prnd_emits_nothing
    an unknown operation raises a       FAIL dollar_unknown_is_named
      bare KeyError
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))

STRIP = "        op = op[1:]\n    if op:\n        op, mods = ibm_spelling"
SIGNS = "or op[1] in '+-*/'):"
PRND = "    'PRND',     # print double spaced\n"
UNKNOWN = """    raise AssemblerError(
        f"unknown mnemonic {stmt.op!r} (not a supported instruction or "
        f"pseudo-op -- see strap_asm.py module docstring)", stmt.lineno)"""


def word(asm, card, pre=""):
    """The word at 100 after assembling `card` there, or the error."""
    try:
        p = asm.assemble("        SLC, 100.0\n" + pre + "        " + card + "\n")
    except Exception as e:
        return "ERROR " + str(e)
    return oct(p.words.get(0o144, 0))


def main(asm):
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want and not got.startswith("ERROR")
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f" expected {want}"))

    check("dollar_ti_equals_ti", word(asm, "$TI,1,-1.0($3),1.0($4)"),
          word(asm, "TI,1,-1.0($3),1.0($4)"))
    check("dollar_l_equals_l", word(asm, "$L(BU,8),-0.8($3),46"),
          word(asm, "L(BU,8),-0.8($3),46"))
    check("dollar_bd_equals_bd", word(asm, "$BD,0"), word(asm, "BD,0"))
    check("dollar_minus_equals_minus", word(asm, "$-(BU,18),200.0,-60"),
          word(asm, "-(BU,18),200.0,-60"))
    check("dollar_kf_equals_kf", word(asm, "$KF(BU,8),200.0"), word(asm, "KF(BU,8),200.0"))
    check("dollar_cm0000_equals_cm0000", word(asm, "$CM0000(BU,1),200.0"),
          word(asm, "CM0000(BU,1),200.0"))
    got = word(asm, "$QQQ(BU,8),200.0")
    named = "QQQ" in got and "KeyError" not in got and got.startswith("ERROR")
    if asm.__name__.startswith("strap_asm"):
        named = named and "line 2" in got
    fails += not named
    print(f"{'PASS' if named else 'FAIL'} dollar_unknown_is_named = {got}")
    check("prnd_emits_nothing", word(asm, "B,0", pre="        PRND\n"),
          word(asm, "B,0"))
    print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
    return fails


def patched(old, new):
    import types
    path = os.path.join(HERE, "..", "strap", "strap_asm.py")
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
        print('-- injected: the "$" strip removed')
        res.append(("strip", main(patched(STRIP, "        pass\n    if op:\n        op, mods = ibm_spelling"))))
        print('-- injected: the sign characters dropped from the guard')
        res.append(("signs", main(patched(SIGNS, "or False):"))))
        print("-- injected: PRND taken out of LISTING_CONTROL")
        res.append(("prnd", main(patched(PRND, ""))))
        print("-- injected: an unknown operation is a bare KeyError")
        res.append(("unknown", main(patched(UNKNOWN, "    raise KeyError(stmt.op)"))))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        import strap2
        fails = main(strap_asm)
        print("-- the host STRAP II (strap2), the same checks")
        fails += main(strap2)
        sys.exit(1 if fails else 0)
