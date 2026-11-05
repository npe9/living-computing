#!/usr/bin/env python3
"""A statement ending in an operator is refused: the printed "-" is the comment mark.

C28-6129 PDF p.5: "The beginning of a comment is signaled by the
character ' (an 8-4 double punch); it is usually terminated by the end
of the card", punched with no blank before it ("CONV3L (BU,64,8),
TABLE' BEGIN CONVERSION").  The MCP listing prints that ' as "-", so
"LX,AY,ACWA-   VF INDICATES ..." (printed p.201 line 37) is the
statement LX,AY,ACWA and a comment.  strap_asm used to drop the dangling
operator, so five cards transcribed WITH the dash (pp.201, 203, 243)
assembled and checked -- right bits, wrong text.

CHECKS
  statement_assembles     LX,AY,ACWA assembles
  trailing_minus_refused  LX,AY,ACWA- is refused, naming the comment mark
  trailing_plus_refused   B,X+ is refused
  leading_minus_kept      VF,-34.0 (printed p.237 line 8) still assembles

MEASURED INJECTIONS (python3 check_comment_mark.py --inject):
    control, assembler as is            PASS
    the refusal removed                 FAIL trailing_minus_refused
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))

RULE = "    if s[-1] in '+-':\n        raise AssemblerError("
PRE = "AY      SYN, $9\nACWA    SYN, (8)223257.0\nX       SYN, (8)100.0\n        SLC, (8)200.0\n"


def outcome(asm, card):
    try:
        asm.assemble(PRE + "        " + card + "\n")
        return "assembles"
    except Exception as e:
        return "refused: comment mark" if "comment mark" in str(e) else "refused: " + str(e)


def main(asm):
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f" expected {want}"))

    check("statement_assembles", outcome(asm, "LX,AY,ACWA"), "assembles")
    check("trailing_minus_refused", outcome(asm, "LX,AY,ACWA-"), "refused: comment mark")
    check("trailing_plus_refused", outcome(asm, "B,X+"), "refused: comment mark")
    check("leading_minus_kept", outcome(asm, "VF,-34.0"), "assembles")
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
        print("-- injected: the refusal removed")
        res.append(("removed", main(patched(RULE, "    if False:\n        raise AssemblerError("))))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main(strap_asm))
