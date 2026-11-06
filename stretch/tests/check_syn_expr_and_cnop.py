#!/usr/bin/env python3
"""A SYN to an expression carries its final symbol's dds, and a CNOP's
fill may land inside an earlier DRZ.

SYN.  C22-6531 printed p.31: "THE MEANING OF SYN IS ALWAYS ONE OF EXACT
SUBSTITUTION", and printed p.11: an expression takes "the data
description of the final symbol".  MCP printed p.291 is "A FPCI
SYN,ALL.9" with ALL a DRZ(N), and printed p.327 line 6 prints
"CM0000,AFPCI" as 232543.11 80 000400.00 F0 -- length 64, byte size
4, ALL's (N) through the SYN.  strap_asm carried a dds only through a
SYN to a BARE symbol, so the row assembled 000000.00 F0.

CNOP.  MCP printed p.319 line 14 reserves "Y MPBUF DRZ(BU),1088 -RESERVE
ROOM FOR OVERLAID AREA" and p.320 line 10 is "SLC,YMPBUF": the loader
is assembled into that reservation, which reserve_zero() allows (p.116).
strap_asm laid every CNOP's NOP fill down BEFORE emitting a statement,
so p.321 line 42's CNOP inside the buffer was "already written" when
the DRZ came, and the merged body image refused.

CHECKS
  syn_expr_takes_final_dds   CM0000,B with B SYN,A.9 and A DRZ(N)
                             assembles as CM0000,A.9 does
  syn_expr_control_bare      the same through a bare SYN (always held)
  cnop_inside_drz_assembles  DRZ, SLC back into it, a half word, CNOP
  cnop_fill_is_a_nop         ... and the gap holds the NOP half word

MEASURED INJECTIONS (python3 check_syn_expr_and_cnop.py --inject):
    control, assembler as is              PASS
    the expression-SYN rule removed       FAIL syn_expr_takes_final_dds
    the CNOP fill moved back before       FAIL cnop_inside_drz_assembles,
      the statements                           cnop_fill_is_a_nop
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))

RULE = "                if _names and _names[-1] in symtab.sym_dds:\n"
FILL_NOTE = "    # >>> THE CNOP FILL GOES IN AFTER THE STATEMENTS, NOT BEFORE. <<<\n"


def words(asm, src, at=(0o144, 0o145)):
    try:
        p = asm.assemble("        SLC, 100.0\n" + src)
    except Exception as e:
        return "ERROR " + str(e)
    return " ".join(oct(p.words.get(a, 0)) for a in at)


def main(asm):
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want and not str(got).startswith("ERROR")
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got}" + ("" if ok else f" expected {want}"))

    data = "        SLC, 200.0\nA       DRZ(N),1\nB       SYN,A.9\nC       SYN,A\n        SLC, 100.0\n"
    check("syn_expr_takes_final_dds", words(asm, data + "        CM0000,B\n"),
          words(asm, data + "        CM0000,A.9\n"))
    check("syn_expr_control_bare", words(asm, data + "        CM0000,C\n"),
          words(asm, data + "        CM0000,A\n"))
    ov = ("BUF     DRZ(BU),8\n        SLC,BUF\n        B,BUF\n        CNOP\n"
          "        L,BUF\n")
    got = words(asm, ov, at=(0o144,))
    check("cnop_inside_drz_assembles", "ERROR" not in got, True)
    nop = words(asm, "        B,0\n        NOP\n", at=(0o144,))
    full = words(asm, ov, at=(0o144,))
    want = None if "ERROR" in nop or "ERROR" in full else int(nop, 8) & 0xFFFFFFFF
    check("cnop_fill_is_a_nop",
          None if "ERROR" in full else int(full, 8) & 0xFFFFFFFF, want if want is not None else -1)
    print("ALL TESTS PASSED" if not fails else f"{fails} TEST(S) FAILED")
    return fails


def patched(edit):
    import types
    path = os.path.join(HERE, "..", "strap", "strap_asm.py")
    src = edit(open(path).read())
    m = types.ModuleType("strap_asm_injected")
    m.__file__ = path
    exec(compile(src, path, "exec"), m.__dict__)
    return m


def no_rule(s):
    assert s.count(RULE) == 1
    return s.replace(RULE, "                if False:\n")


def fill_first(s):
    a = s.index(FILL_NOTE)
    b = s.index("    return AssembledProgram(", a)
    block = s[a:b]
    s = s[:a] + s[b:]
    c = s.index("    end_pc = None\n    for stmt in statements:")
    return s[:c] + block + s[c:]


if __name__ == "__main__":
    import strap_asm
    if sys.argv[1:] == ["--inject"]:
        res = [("control", main(strap_asm))]
        print("-- injected: the expression-SYN rule removed")
        res.append(("rule", main(patched(no_rule))))
        print("-- injected: the CNOP fill moved back before the statements")
        res.append(("fill", main(patched(fill_first))))
        print("INJECTIONS: " + ", ".join(f"{n} -> {'FAIL' if r else 'PASS'}" for n, r in res))
    else:
        sys.exit(main(strap_asm))
