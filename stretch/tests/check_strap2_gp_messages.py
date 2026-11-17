#!/usr/bin/env python3
"""check_strap2_gp_messages.py -- the numbered messages that fence the general
parenthetical integer entry (.n) (a "g.p."), and VALUE's 78, in the host STRAP
II, one card each (G3.3, docs/source_audit.md).

THE PAGES, read in the page images 2026-11-16.  C22-6729 printed pp.177-178,
"Number / Logic Area Detecting Error Condition / Message", as printed (the
message's own number ends it):

  65   MQDD     MORE THAN 1 RADIX OR PAREN. ENTRY  65
  68   GETFLD   GP ERROR  68
  78   VALUE    DIVISION BY ZERO, DIVISOR IGNORED  78
  82   GETFLD   (.0) HAS BEEN INTERPRETED AS PAREN INTEGER  82
  94   DECODE   ERROR IN GP  94
  95   DECODE   NEGATIVE GP HAS BEEN COMPLEMENTED  95
  108  GETFLD   GP IS NOT ALLOWED  108          (p.178)

The six g.p. messages are 65, 68, 82, 94, 95 and 108; the logic-area column is
the one C28-6129's own list lacks.  The page gives number, area and text, not
the condition, so each condition below has its own source or is marked:

  65  p.100 (MQDD) Boxes 27-29: "Additional GP's, exponents, or sign bytes if
      any, return to the proper section of MQDD; another radix at this point
      would be an error, and is error flagged."  A numeric DD datum followed
      by a radix.  (Was 67, INAPPROPRIATE CHAR.)
  68  DERIVED.  Appendix C, printed p.198, item 4B: n is "6 ... Value of n,
      binary", so n over 63 cannot be coded.  (Was coded modulo 64, silently:
      (.70)1 set bit 6.)  p.85 Boxes 64, 73 name 68's only stated condition,
      a lone datum after a g.p. or radix, which this check does not reach.
  78  the message's own words: the divisor is ignored.  (Was ignored with no
      message.)
  82  the message's own words: "(.0)" is taken as a g.p. with n = 0, and the
      word is made.  (Was made with no message.)
  94  DERIVED.  DECODE evaluates and inserts a g.p. (p.140 Boxes 14-15); its
      two limits are C28-6129 printed p.25's (the entry's n+1 bits within the
      statement; "the integer ... converted" to 24 bits).  (Were refused,
      unnumbered.)
  95  C28-6129 printed p.25: "a negative number is compiled as the
      complement, re 2**(n+1), of the magnitude"; the message says it was.
      (Was complemented with no message.)
  108 C28-6129 printed p.26 and C22-6729 printed p.204 (glossary): "Such
      pseudo instructions as SYN, DR, DDI, and DRZ cannot have a gp"; p.85
      Box 36, Gfnogp.  (Already 108; held here.)

Each row: the card; the number it must give; whether it refuses ("fatal": the
host's strict assemble stops, as strap_asm's oracles expect) or notes and
makes the word; for a note, a control card that must assemble to the same
words with no message; and the message as errtab prints it, typed above from
the page and NOT imported from errtab, so the table is checked against the
ink.

MEASURED INJECTIONS, 2026-11-16, each reverted from a saved copy and checked
with cmp (FAIL lines observed):
  pass1._numeric's 65 branch removed      65 refuses (number) (1): 67 instead
  getfld._checked_gp: n > 63 not refused   68 refuses, 68 refuses (number) (2)
  getfld._checked_gp: no 82 note           82 notes (number) (1)
  value.py: no 78 note                     78 notes (number) (1)
  pass2.decode: the bit-count 94 a bare AssemblerError again
                                           94 bits refuses (number) (1)
  pass2.decode: the 24-bit 94 a bare AssemblerError again
                                           94 24 bits refuses (number) (1)
  pass2.decode: no 95 note                 95 notes (number) (1)
  control: PASS 29
(The first 68 injection crashed the script at the number check, which read a
refusal's text off a list; the check was made to survive it and re-measured.)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
import strap_asm                # noqa: E402
import strap2                   # noqa: E402
from strap2 import errtab       # noqa: E402

PRINTED = {
    65: "MORE THAN 1 RADIX OR PAREN. ENTRY  65",
    68: "GP ERROR  68",
    78: "DIVISION BY ZERO, DIVISOR IGNORED  78",
    82: "(.0) HAS BEEN INTERPRETED AS PAREN INTEGER  82",
    94: "ERROR IN GP  94",
    95: "NEGATIVE GP HAS BEEN COMPLEMENTED  95",
    108: "GP IS NOT ALLOWED  108",
}

# (name, card, number, how, control card for a note)
CASES = [
    ("65", "DD(N), 1.5(8)17", 65, "fatal", None),
    ("68", "E+I, 0(.70)1", 68, "fatal", None),
    ("78", "B, 8/0", 78, "note", "B, 8"),
    ("82", "E+I, 0(.0)1", 82, "note", "E+I, 0(.1)2"),
    ("94 bits", "E+I, 0(.40)1", 94, "fatal", None),
    ("94 24 bits", "E+I, 0(.30)4096*4096", 94, "fatal", None),
    ("95", "E+I, 0(.3)-1", 95, "note", "E+I, 0(.3)15"),
    ("108", "SYN, 5(.3)1", 108, "fatal", None),
]

passes = fails = 0


def check(name, got, want):
    global passes, fails
    if got == want:
        passes += 1
        print(f"PASS {name}: {got!r}")
    else:
        fails += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def run(card):
    src = "START   NOP\n        " + card + "\n        BEW, $\n        END, START\n"
    try:
        p = strap2.assemble(src, strap_asm.DEFAULT_ORIGIN_BITS)
    except Exception as x:      # noqa: BLE001  the refusal is the result
        return "refused", str(x), None
    return "made", [n for n, _t, _u, _f in p.messages], dict(p.words)


for n, text in sorted(PRINTED.items()):
    check(f"errtab prints {n} as p.177-178 does", errtab.message(n), text)

for name, card, number, how, control in CASES:
    what, detail, words = run(card)
    if how == "fatal":
        check(f"{name} refuses: {card}", what, "refused")
        check(f"{name} refuses (number)", isinstance(detail, str) and
              f"message {number}:" in detail, True)
    else:
        check(f"{name} notes and makes the word: {card}", what, "made")
        check(f"{name} notes (number)", detail if what == "made" else None, [number])
        cwhat, cdetail, cwords = run(control)
        check(f"{name} control gives no message: {control}", cdetail, [])
        check(f"{name} same words as {control}", words == cwords and words is not None, True)

print(f"{passes} passed, {fails} failed")
sys.exit(1 if fails else 0)
