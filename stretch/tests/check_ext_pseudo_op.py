#!/usr/bin/env python3
"""check_ext_pseudo_op.py -- EXT, "Extract", against IBM's own worked
example and against the one page in the corpus that uses it.

C22-6531 printed p.35 and C28-6129 printed p.19 agree on the meaning:

  "First, Statement is compiled as is any legal machine instruction.
   Then the field beginning at I and ending at J is extracted and
   compiled in the position in the code where the EXT occurs."

so the FOLLOWING statement deposits nothing of its own and the EXT
deposits J-I+1 bits taken out of it.  Bit 0 is the first bit of that
statement, "according to 7030 custom".

>>> THE WORKED EXAMPLE IS THE ORACLE, NOT MY READING OF THE PROSE. <<<
C22-6531 printed p.35 states the whole result:

  "Example: EXT(18, 47) + (B, 18, 7), 73.16 ...  Then bits 18 through
   47 ... are extracted and placed in the program being compiled.  The
   dds (BU, 30, 8) is formed.  The location counter is advanced 30
   bits."

Two of those three are checked below -- the extracted bits and the
30-bit advance.  THE THIRD IS NOT IMPLEMENTED: this assembler's
symbols carry a value and no data description at all (see SymTab), so
there is nowhere to put "(BU, 30, 8)".  Said plainly here rather than
left for a reader to discover from a passing test.

MEASURED INJECTION.  Change the extraction loop in strap_asm's
emit_statement to count bits from the LEAST significant end --
"(word >> bit) & 1" instead of "(word >> (63 - bit)) & 1" -- and
three checks fail, with these exact values, which were RUN and not
predicted:

  ext_matches_ibm_worked_example  0xe90010a  against  0x10800970
  mcp_p149_half_word_address      0o0        against  0o437147
  mcp_p149_is_aedump_doubled      0          against  147047

Note the first one: counting from the wrong end does NOT produce
zero, it produces a plausible-looking field.  Only the p.149 row,
whose high bits are genuinely empty, collapses to 0.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "strap"))
import strap_asm                                        # noqa: E402

ORIGIN = "        SLC, (8)1000.0\n"


def _assemble(body):
    return strap_asm.assemble(ORIGIN + body)


def main():
    fails = 0

    def check(name, got, want):
        nonlocal fails
        ok = got == want
        if not ok:
            fails += 1
        print(f"{'PASS' if ok else 'FAIL'} {name} = {got} "
              f"{'' if ok else f'expected {want}'}")

    # ---- IBM's worked example, C22-6531 printed p.35 ----------------
    # The bare instruction first, so the expected field is derived from
    # the SAME assembler rather than hand-copied: the test is that EXT
    # extracts, not that "+(B,18,7),73.16" is encoded correctly.
    bare = _assemble("        +(B,18,7),73.16\n").words.get(0o1000, 0)
    want = 0
    for bit in range(18, 48):
        want = (want << 1) | ((bare >> (63 - bit)) & 1)
    got = _assemble("        EXT(18,47)\n        +(B,18,7),73.16\n")
    field = (got.words.get(0o1000, 0) >> (64 - 30)) & ((1 << 30) - 1)
    check("ext_matches_ibm_worked_example", hex(field), hex(want))

    # "The location counter is advanced 30 bits" -- and NOT rounded to
    # a half word, which is the part a careless implementation gets
    # wrong (30 is not a multiple of 32).
    adv = _assemble("        EXT(18,47)\n        +(B,18,7),73.16\n"
                    "AFTER   SYN, $\n").symtab["AFTER"]
    check("ibm_counter_advances_30_bits", adv - 0o1000 * 64, 30)

    # ---- MCP printed p.149 lines 7-8 --------------------------------
    # The page prints "EXT(0,18)" over "B,AEDUMP" and the extracted
    # field prints as 0437147.  AEDUMP is at 217463.40, so the 19 bits
    # are the half-word address: 0o217463 * 2 + 1.
    p149 = strap_asm.assemble(
        "        SLC, (8)217460.55\n"
        "AEDUMP  SYN, (8)217463.40\n"
        "        EXT(0,18)\n"
        "        B,AEDUMP\n")
    raw = p149.words.get(0o217460, 0)
    got = (raw >> (64 - 45 - 19)) & ((1 << 19) - 1)
    check("mcp_p149_half_word_address", oct(got), oct(0o437147))
    check("mcp_p149_is_aedump_doubled", got, 0o217463 * 2 + 1)

    # ---- the four permissible parameter spellings -------------------
    # C28-6129 printed p.19: "(I, J, COUNT)  (I, J)  (I, , COUNT)
    # (, J, COUNT)" -- any two of the three, the third derived.
    forms = ["EXT(18,47)", "EXT(18,47,30)", "EXT(18,,30)", "EXT(,47,30)",
             "EXT,(18,47)"]
    words = set()
    for f in forms:
        w = _assemble(f"        {f}\n        +(B,18,7),73.16\n")
        words.add(w.words.get(0o1000, 0))
    check("all_parameter_spellings_agree", len(words), 1)

    # ---- the target contributes nothing to the counter --------------
    # The whole point: without EXT the branch would occupy a half word.
    plain = strap_asm.assemble(
        ORIGIN + "        B,$\nAFTER   SYN, $\n").symtab["AFTER"]
    check("bare_branch_occupies_a_half_word", plain - 0o1000 * 64, 32)
    paired = strap_asm.assemble(
        ORIGIN + "        EXT(0,18)\n        B,$\n"
        "AFTER   SYN, $\n").symtab["AFTER"]
    check("ext_target_occupies_nothing", paired - 0o1000 * 64, 19)

    # ---- refusals ---------------------------------------------------
    for bad, why in (("        EXT(18)\n        B,$\n",
                      "one parameter is not two of three"),
                     ("        EXT(18,47)\n",
                      "EXT with nothing following it")):
        try:
            strap_asm.assemble(ORIGIN + bad)
            print(f"FAIL refused({why}) = assembled, expected AssemblerError")
            fails += 1
        except strap_asm.AssemblerError:
            print(f"PASS refused({why})")

    if fails:
        print(f"\n{fails} TEST(S) FAILED")
    else:
        print("\nALL TESTS PASSED")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
