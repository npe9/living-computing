#!/usr/bin/env python3
""""$OP" assembles as OP, and PRND is a listing control.

C28-6129 printed p.10 (PDF p.14): "Another special use of the $
character is to prefix any operation code in this manner: $OP.  This
directs the compiler to suppress any error indications that arise in
connection with the compilation of this statement."  MCP prints it on
printed pp.53, 56, 57, 279 and 283 ("$TI,1,-1.0(L IODX),1.0(L XPP)",
"$L(BU,8),-0.8(L IODX),46") and the AX5B test listing prints "$BD,0".
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
  prnd_emits_nothing      PRND before B,0 leaves B,0 at the same word

MEASURED INJECTIONS (python3 check_dollar_op.py --inject):
    control, assembler as is            PASS
    the "$" strip removed               FAIL dollar_ti_equals_ti,
                                             dollar_l_equals_l,
                                             dollar_bd_equals_bd
    PRND taken out of LISTING_CONTROL   FAIL prnd_emits_nothing
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))

STRIP = "        op = op[1:]\n    # `entry` rather than None"
PRND = "    'PRND',     # print double spaced\n"


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
        res.append(("strip", main(patched(STRIP, "        pass\n    # `entry` rather than None"))))
        print("-- injected: PRND taken out of LISTING_CONTROL")
        res.append(("prnd", main(patched(PRND, ""))))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main(strap_asm))
