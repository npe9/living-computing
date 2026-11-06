#!/usr/bin/env python3
"""An instruction's NAME carries a dds: (BU,32,8) or (BU,64,8).
An index word's name carries one too: XW (BU), VF (B,25), CF/RF (BU,18).

C22-6531 printed p.10: "instruction-naming symbols are given field
lengths equal to the lengths of the particular instructions named
(either 32 or 64), and are defined as unsigned binary with byte size
8."  MCP printed p.233 lines 8-9 print "L,V INON" and "ST,V SC5" with
no dds; V INON and V SC5 name instructions (half words).

No single deck exercises the rule: each page SYNs its externals, and
p.233's stand-ins write the dds out (SYN(BU,32,8)), checked against
the ink by that page's !CHECKs.  The rule fires only when the label and
its use are assembled TOGETHER -- the body image (check_mcp_body_image)
-- which is where its first version broke: it stored "(BU,32,8)" WITH
parentheses, a form parse_dds reads as a mode, and the 134-page image
raised "unknown VFL mode '(BU,32,8)'" (2026-11-05).

C22-6531 printed p.19 (PDF p.20), after XW, VF, CF and RF: "the index
word pseudo-operations ... are given data descriptions by the compiler,
as though they had been defined by DD statements ... and cannot be
overruled in the pseudo-operation statement": XW (BU), VF (B, 25), CF or
RF (BU, 18).  MCP printed p.220 line 5 defines "V TSQ  VF,0", and
printed p.221 line 20 writes "M+1,V TSQ" with no dds and prints
031100.02 -- (B,25) with B's standard byte size 1 (PDF p.10).  The body
image assembled 031100.22 for it until this rule (2026-11-05): every
page's !CHECK rows were first run against the MERGED image that day,
and that row and two like it (pp.225, 228) were the only three of 7,113
that failed.

CHECKS
  half_label_equals_standin   L,X after "X B,0" (a half word) assembles
                              to what L,X does after X SYN(BU,32,8),0
  full_label_equals_standin   the same with a full-word instruction
                              (BB) and SYN(BU,64,8)
  data_label_is_not_an_instruction
                              a DD-named X keeps the DD's own dds, so
                              the check above can tell the two apart
  vf_label_equals_standin     M+1,X after "X VF,0" assembles to what it
                              does after X SYN(B,25,1)
  cf_label_equals_standin     L,X after "X CF,0" equals SYN(BU,18)
  xw_label_equals_standin     L,X after "X XW,0" equals SYN(BU)

MEASURED INJECTIONS (python3 check_instruction_label_dds.py --inject):
    control, assembler as is                   PASS
    rule stores the dds with parentheses       FAIL half_label_equals_standin
    rule removed (labels get no dds)           FAIL half_label_equals_standin
    index-word table emptied                   FAIL vf_label_equals_standin,
                                                    cf_label_equals_standin
  xw_label_equals_standin still PASSES with the table emptied: a bare
  (BU) assembles exactly as no dds does, so the XW entry is recorded
  for the manual's sake and nothing here can see it.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))

RULE = "symtab.sym_dds[up] = 'BU,%d,8' % size"
TABLE = "_INDEX_WORD_DDS = {'XW': 'BU', 'VF': 'B,25', 'CF': 'BU,18', 'RF': 'BU,18'}"


def use_word(asm, defn, use="L,X"):
    """The word `use` assembles to at word 100, the definition at 200."""
    try:
        p = asm.assemble("        SLC, 100.0\n        " + use +
                         "\n        SLC, 200.0\n" + defn + "\n")
    except Exception as e:
        return "ERROR " + str(e)
    return oct(p.words.get(0o144, 0))


def main(asm):
    fails = 0

    def check(name, got, want, same=True):
        nonlocal fails
        ok = (got == want) == same
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}"
              + ("" if ok else f" {'expected' if same else 'must differ from'} {want}"))

    check("half_label_equals_standin", use_word(asm, "X       B,0"),
          use_word(asm, "X       SYN(BU,32,8), 200.0"))
    check("full_label_equals_standin", use_word(asm, "X       BB,0.0,0"),
          use_word(asm, "X       SYN(BU,64,8), 200.0"))
    check("data_label_is_not_an_instruction", use_word(asm, "X       DD(BU,8),1"),
          use_word(asm, "X       SYN(BU,32,8), 200.0"), same=False)
    check("vf_label_equals_standin", use_word(asm, "X       VF,0", "M+1,X"),
          use_word(asm, "X       SYN(B,25,1), 200.0", "M+1,X"))
    check("cf_label_equals_standin", use_word(asm, "X       CF,0"),
          use_word(asm, "X       SYN(BU,18), 200.0"))
    check("xw_label_equals_standin", use_word(asm, "X       XW,0"),
          use_word(asm, "X       SYN(BU), 200.0"))
    print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
    return fails


def patched(old, new):
    import types
    src = open(os.path.join(HERE, "..", "strap", "strap_asm.py")).read()
    assert src.count(old) == 1, old
    m = types.ModuleType("strap_asm_injected")
    m.__file__ = os.path.join(HERE, "..", "strap", "strap_asm.py")
    exec(compile(src.replace(old, new), m.__file__, "exec"), m.__dict__)
    return m


if __name__ == "__main__":
    import strap_asm
    if sys.argv[1:] == ["--inject"]:
        res = [("control", main(strap_asm))]
        print("-- injected: the rule stores '(BU,%d,8)'")
        res.append(("parentheses", main(patched(RULE, RULE.replace("'BU,%d,8'", "'(BU,%d,8)'")))))
        print("-- injected: the rule removed")
        res.append(("removed", main(patched(RULE, "pass"))))
        print("-- injected: the index-word table emptied")
        res.append(("index words", main(patched(TABLE, "_INDEX_WORD_DDS = {}"))))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main(strap_asm))
