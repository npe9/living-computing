#!/usr/bin/env python3
"""A SYN to a SYN to an index register still names the register.

>>> WHY THIS EXISTS, AND MCP'S OWN SOURCE IS THE WITNESS. <<<
C22-6531 printed p.31 calls SYN an "EXACT SUBSTITUTION", and says the
properties of Y "are TRANSFERRED to A".  The assembler honoured that
for data descriptions (`sym_dds`) and for integer classification
(`sym_int`) but NOT for the system-symbol alias, which is what keeps
`$N`'s register-field/address-field duality.  So the alias was recorded
only one level deep.

MCP's listing, printed p.61 lines 32 and 39 (and again on printed
p.287):

    T X1    SYN, $10    -TEMPORARY INDEX
    T IXF   SYN, TX1    --MACH CONF CHANGE-- CHAN. SCAN IX

`T IXF` names index register 10 through TWO levels.  Before the fix,
`LX, TIXF, TCHSXW` -- printed p.72 line 4, the instruction that loads
the channel-status-table scan -- assembled with

    j = 1664 & 0xF = 0

because TIXF fell back to its numeric value, the bit address of word
26.  It loaded $0 instead of $10, silently, with the ADDRESS field
correct, so the value fetched was right and went to the wrong register.

>>> AND IT WAS INVISIBLE TO THE PAGE'S OWN TESTS. <<<
decks/mcp_bootstrap_p72.strap defines `TIXF SYN, $10` directly -- one
level -- so the deck assembled correctly on its own.  Only the MERGED
image, where printed p.61's chained definition wins, carried j=0.  That
is why this checks BOTH.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
sys.path.insert(0, HERE)

from strap_asm import assemble
import mcp_image

fails = 0


def check(what, got, want):
    global fails
    if got == want:
        print(f"PASS {what} = {got!r}")
    else:
        print(f"FAIL {what} = {got!r}, expected {want!r}")
        fails += 1


def j_field_at(prog, word, half=0):
    """The 4-bit J field of a half-word instruction. `half` 0 = left
    (bits 0-31), 1 = right -- three half-word LX's occupy 1.5 words,
    which this file got wrong the first time it was written."""
    v = prog.words.get(word)
    if v is None:
        return None
    hw = (v >> 32) & 0xFFFFFFFF if half == 0 else v & 0xFFFFFFFF
    return (hw >> 9) & 0xF


# ---------------------------------------------------------------------
# 1. The minimal case, written here so the rule is stated without MCP.
# ---------------------------------------------------------------------
MINIMAL = """\
        SLC, 100.0
TX1     SYN, $10
TIXF    SYN, TX1
TDEEP   SYN, TIXF
TTGT    SYN, 200.0
        LX, TIXF, TTGT
        LX, TDEEP, TTGT
        LX, TX1, TTGT
        END, 100.0
"""
p = assemble(MINIMAL)
# The three LX's are HALF-word instructions, so they land at 100.0,
# 100.40 and 101.0 -- not at three consecutive words.
check("two levels   (TIXF  SYN, TX1)  J field", j_field_at(p, 100, 0), 10)
check("three levels (TDEEP SYN, TIXF) J field", j_field_at(p, 100, 1), 10)
check("one level    (TX1   SYN, $10)  J field", j_field_at(p, 101, 0), 10)

# The address field must be untouched by the fix: 200.0 is word 200,
# and LX's 19-bit field counts half-words.
addr19 = (((p.words[100] >> 32) & 0xFFFFFFFF) >> 13) & 0x7FFFF
check("and the ADDRESS field is still word 200", addr19 // 2, 200)

# A chained SYN still carries its numeric value for anything reading the
# table directly -- the alias does not replace the value.
check("TIXF's numeric value is still word 26's bit address",
      p.symtab.get("TIXF"), 26 * 64)

# ---------------------------------------------------------------------
# 2. The real witness: the MERGED MCP image, printed p.72 line 4.
# ---------------------------------------------------------------------
TA9_WORD = 0o4215          # printed p.72 line 4, "T A9  LX,TIXF,TCHSXW"
prog = mcp_image.build_mcp_ipl()[0]
check(f"merged MCP image, word {TA9_WORD:o} (printed p.72 line 4) J field",
      j_field_at(prog, TA9_WORD), 10)

# The whole instruction word, so a future change to any field is caught
# and not just J.  Measured 2026-10-28 and identical to the standalone
# assembly of decks/mcp_bootstrap_p72.strap.
check(f"merged MCP image, word {TA9_WORD:o} left half-word",
      ((prog.words.get(TA9_WORD) or 0) >> 32) & 0xFFFFFFFF, 0x011a9410)

# >>> THE STANDALONE DECK AND THE MERGE MUST AGREE. <<<  Their
# disagreement in exactly one field is what this bug was.
with open(os.path.join(HERE, "..", "decks",
                       "mcp_bootstrap_p72.strap")) as f:
    solo = assemble(f.read())
check("standalone deck and merged image agree on printed p.72 line 4",
      j_field_at(solo, TA9_WORD) == j_field_at(prog, TA9_WORD), True)

if fails:
    print(f"{fails} TEST(S) FAILED")
    sys.exit(1)
print("ALL TESTS PASSED")
