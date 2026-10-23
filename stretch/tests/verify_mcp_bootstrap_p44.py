#!/usr/bin/env python3
"""verify_mcp_bootstrap_p44.py -- THE CHARACTER LOCATOR TABLES and
THE TABLES, printed page 44 (../decks/mcp_bootstrap_p44.strap).
docs/MCP_Mar63_001-249.pdf PDF p.51, header "PAGE NUMBER 44".
AGENTS.md rule 3.

Eighteen printed rows with binary output and four symbol locations.

>>> ALL FOUR OF printed p.43's STAND-INS LAND. <<<

printed p.43 read four addresses off its own binary and wrote them as
SYNs because this page had not been opened:

  Q FLD   002456.00   line 4   -- p.43 line 46's LVE target
  Q       002465.00   line 21  -- p.43 line 47's LF table
  Q SAV   002472.00   line 28  -- p.43 lines 10 and 53's TI/SWAPI
  Q TB    002500.00   line 30  -- p.43 line 26's LV

Not one of them moves.  And the page's last datum ends at 002501.71,
which docs/boot_plan.md A9 recorded as printed p.45's opening address
before p.44 was rendered.

THE NULL OPERATION FIELD, THIRTEEN TIMES.  Lines 4-16 have nothing in
the operation column; C22-6531 printed p.7 calls that a NULL FIELD and
strap_asm.py has compiled it since MCP printed p.25.  What it lays
down is the address-and-index half word every full-word format begins
with -- ADDRESS(0-23) | 1000 | I(28-31) -- and the listing prints the
thirteen of them as 82.

WHAT THE TABLE IS FOR is RefMan printed p.29, "Indirect Addressing":
p.43 line 46's LVE chains through the half word at Q FLD+$3, and p.29
says that half word "is assumed to be either a half length instruction
or the first half of a full length instruction ... No check is made
for invalid operation codes."

THE TWO CNOPs DO DIFFERENT THINGS, which is the alignment trap
docs/NEXT.md recorded on jb_ax5b p.80 against p.82.  Line 20 sits at
002464.40 and compiles a NOP; line 27 sits at 002471.70 and compiles
NOTHING, printing neither a location nor a binary, because there is no
half word there to put a NOP in.  Both are checked: the NOP by its own
row, the silence by Q SAV landing on 002472.00.

NO BINARY IS PRINTED FOR LINES 21, 22, 23 AND 25, so no character code
on this page is TRANSCRIPTION-checked and none can be.  What is checked
at that standard is every row's LENGTH, by the address of the row after
it, and all four together by Q SAV.

THE SIXTY-ODD CHARACTER CODES THEMSELVES ARE MANUAL-DERIVED, which is
the weaker of the two standards docs/NEXT.md declares and is worth
saying rather than leaving as a hole: strap/charsets.py's A table is
the 48 Character Set from RefMan printed p.166, so each code has a
primary source behind it -- it is simply not IBM's assembler saying so
on this page.  The grid they come out as is its own evidence: 0o6x for
the 12 zone, 0o4x for the 11, 0o2x for the zero zone and 0o0x for
none.

A FOURTH INJECTION covers the pair of self-containment checks below.
Adding a fifth SYN stand-in to printed p.43's deck -- a symbol nothing
references, so not one compiled row moves -- gives 1 FAIL, in the
inward check, and nothing else.

THREE INJECTIONS, AND THE THIRD IS WHY THE LAST CHECK EXISTS.  Each
was run and the OBSERVED failure set written down:

  line 15 ",.66($2)" -> ",.72($2)"
      1 FAIL, 002463.40, and nothing else.
  line 21's data one character short ("ABCDEFGHI+.)" )
      1 FAIL, 002470.44 -- the colon's address, which is what pins
      the three rows above it.
  line 25's data one character short ("123456789 =-")
      ALL TWENTY-TWO ROWS AND ALL FOUR SYMBOLS PASSED.  The second
      CNOP rounds to the next word and absorbs it.  That is the
      survival the zone-width check below was added for, and with it
      the same injection gives 1 FAIL at Q+234+72.

AND "UNTAIL" IS CHECKED, NOT ASSERTED.  Line 35 is "UNTAIL,(1)",
closing the level-1 tail printed p.43 line 9 opened; C28-6129 printed
p.38 says an untail "will untail all levels up to and including the
level specified".  Discarding the pair is bit-identical only if no
name is used on both sides of the block boundary, so the last check
below SCANS EVERY OTHER MCP DECK for the thirteen symbols defined
inside it.
"""
import glob
import os
import re

from listing_oracle import check_rows, finish, loc_bits, read_bits
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p44.strap").read())

SYMBOLS = {
    # THE FOUR printed p.43 PREDICTED.
    "QFLD": "002456.00",
    "Q":    "002465.00",
    "QSAV": "002472.00",
    "QTB":  "002500.00",
}

ROWS = [
    # THE CHARACTER LOCATOR TABLE: thirteen null-operation half words,
    # stepping one six-bit character apiece, 0 through 72.
    ("002456.00", "000000.00 82", "line 4   Q FLD  ,0($2)"),
    ("002456.40", "000000.06 82", "line 5   ,.6($2)"),
    ("002457.00", "000000.14 82", "line 6   ,.12($2)"),
    ("002457.40", "000000.22 82", "line 7   ,.18($2)"),
    ("002460.00", "000000.30 82", "line 8   ,.24($2)"),
    ("002460.40", "000000.36 82", "line 9   ,.30($2)"),
    ("002461.00", "000000.44 82", "line 10  ,.36($2)"),
    ("002461.40", "000000.52 82", "line 11  ,.42($2)"),
    ("002462.00", "000000.60 82", "line 12  ,.48($2)"),
    ("002462.40", "000000.66 82", "line 13  ,.54($2)"),
    ("002463.00", "000000.74 82", "line 14  ,.60($2)"),
    # THE TWO THAT CROSS THE WORD BOUNDARY, and the only reason the
    # step is checked rather than assumed: 66 and 72 bits print as
    # word 1 plus 2 and 8 bits.
    ("002463.40", "000001.02 82", "line 15  ,.66($2)"),
    ("002464.00", "000001.10 82", "line 16  ,0.72($2)"),
    # THE FIRST CNOP, which has a half word to fill.
    ("002464.40", "000000.30 00", "line 20  CNOP"),
    # THE COLON, written as an octal code because the 48-character set
    # has no graphic for it.  Six bits, two octal digits.
    ("002470.44", "32", "line 24  DD(BU,6,6),(8)32  -SPECIAL FOR COLON", 6),
    # Q TB's four zone offsets: 13 characters times 6 bits apiece.
    ("002500.00", "000000.00+", "line 30  Q TB  VF,0  -FOR 12 ZONE"),
    ("002500.40", "000001.16+", "line 31  VF,78  -FOR THE 11 ZONE"),
    ("002501.00", "000002.34+", "line 32  VF,156  -FOR THE ZERO ZONE"),
    ("002501.40", "000003.52+", "line 33  VF,234  -FOR THE NO ZONE"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.44 ")

# ---------------------------------------------------------------------
# EACH ZONE IS THIRTEEN CHARACTERS WIDE -- the one thing on this page
# that NO printed binary pins, measured instead from the two tables
# that are printed.
#
# THE SECOND CNOP ABSORBS THE ERROR.  Line 27 rounds the location
# counter to the next WORD, so a table row one character short still
# leaves Q SAV on 002472.00 and every row above still matches.  That
# was measured, not assumed: dropping the last character of line 25
# passes all twenty-two rows and all four symbols above.  Dropping it
# from line 21 does NOT, because the colon's own address, 002470.44,
# sits between.  So lines 21, 22 and 23 are pinned by the colon row
# and LINE 25 IS PINNED BY NOTHING ON THE PAGE.
#
# What pins it is the two tables' PRINTED binary read together:
#   Q FLD   thirteen null-operation half words, 0 through 72 bits
#           (checked above) -- the code indexes thirteen characters.
#   Q TB    0, 78, 156, 234 (checked above) -- the rows are 78 bits
#           apart, which is thirteen six-bit characters.
# So the thirteenth character of every zone must be present, and the
# listing prints what they are: "/" closes three of the four rows and
# the colon closes the zero zone, which line 24 gives as octal 32.
# ---------------------------------------------------------------------
Q_AT = loc_bits("002465.00")
SLASH, COLON = 0o21, 0o32
for zone, (off, want, what) in enumerate(
        [(0, SLASH, "12 zone"), (78, SLASH, "11 zone"),
         (156, COLON, "zero zone"), (234, SLASH, "no zone")]):
    got = read_bits(prog, Q_AT + off + 12 * 6, 6)
    label = (f"MCP p.44 Q+{off}+72 the {what}'s thirteenth character")
    if got == want:
        print(f"PASS {label}: {got:02o}")
    else:
        print(f"FAIL {label}: assembled {got:02o}, want {want:02o}")
        fails += 1

# ---------------------------------------------------------------------
# THE TAIL BLOCK IS SELF-CONTAINED, MEASURED.
#
# printed p.43 line 9 opens a level-1 tail "A" and printed p.44 line 35
# closes it.  strap_asm.py discards both, which is bit-identical only
# if every symbol the block defines is also used only inside it -- a
# name on both sides of the boundary would be mangled on one side only
# in the real assembly and not at all in ours.
#
# So scan every OTHER MCP deck for the thirteen names.  A hit is not
# necessarily wrong, but it is the exact condition strap_asm.py's
# LISTING_CONTROL note says to watch for, and it would have to be
# looked at rather than discovered later.
# ---------------------------------------------------------------------
TAILED = ["QGO", "QP", "QNO", "QNOZ", "QER", "QCK", "QST", "QCHK",
          "QFIN", "QFLD", "Q", "QSAV", "QTB"]
INSIDE = {"mcp_bootstrap_p43.strap", "mcp_bootstrap_p44.strap"}

leaks = []
for path in sorted(glob.glob("../decks/mcp_bootstrap_p*.strap")):
    name = os.path.basename(path)
    if name in INSIDE:
        continue
    for lineno, line in enumerate(open(path), 1):
        code = line.split("!", 1)[0]
        for tok in re.findall(r"[A-Z][A-Z0-9]*", code):
            if tok in TAILED:
                leaks.append(f"{name}:{lineno} {tok}")

if leaks:
    print("FAIL MCP p.44 tail block is not self-contained (outward): "
          + ", ".join(leaks[:8]))
    fails += 1
else:
    print(f"PASS MCP p.44 tail block self-contained outward: none of "
          f"the {len(TAILED)} symbols printed p.43 line 9's TAIL,A "
          f"covers appears in any other MCP deck")

# AND THE OTHER DIRECTION, which is the half the scan above does not
# cover: a reference from INSIDE the block to a name defined outside
# it would be mangled on one side only too.
#
# printed p.43 defines exactly two names before its "TAIL,A" --
# S CA6 and S CA8, the routine's two entries -- and carries exactly
# four SYN stand-ins, which are the four printed p.44 defines INSIDE
# the block.  So if no code line after the TAIL mentions S CA6 or
# S CA8, every symbol the block references is one the block defines,
# and the deck assembling at all is what says there are no others.
P43 = "../decks/mcp_bootstrap_p43.strap"
p43 = [ln.split("!", 1)[0] for ln in open(P43)]
tail_at = [i for i, ln in enumerate(p43) if re.search(r"\bTAIL\b", ln)]
syns = sorted(m.group(1) for ln in p43
              for m in [re.match(r"([A-Z][A-Z0-9]*)\s+SYN,", ln)] if m)
outside = sorted(m.group(1) for ln in p43[:tail_at[0]]
                 if not re.search(r"\bSYN,", ln)
                 for m in [re.match(r"([A-Z][A-Z0-9]*)\s", ln)] if m)
# The scan stops at the deck's own END.  "END, S CA6" is scaffolding
# this project adds so each page assembles alone -- the listing's one
# END is at the end of the whole program, not on p.43 -- so counting
# it as a reference inside the block would be measuring the deck
# rather than the listing.
end_at = [i for i, ln in enumerate(p43) if re.match(r"\s+END,", ln)]
body = p43[tail_at[0] + 1:end_at[0]] if end_at else p43[tail_at[0] + 1:]
inward = [f"p43:{i + 1} {n}"
          for i, ln in enumerate(body, tail_at[0] + 1)
          for n in outside if re.search(r"\b" + n + r"\b", ln)]

if len(tail_at) != 1:
    print(f"FAIL MCP p.44 printed p.43 has {len(tail_at)} TAIL lines, "
          f"expected 1 -- the block boundary is not where this check "
          f"thinks it is")
    fails += 1
elif sorted(syns) != sorted(SYMBOLS):
    print(f"FAIL MCP p.44 printed p.43's stand-ins are {syns}, but "
          f"this page defines {sorted(SYMBOLS)} -- a stand-in for a "
          f"symbol defined somewhere else crosses the block boundary")
    fails += 1
elif inward:
    print("FAIL MCP p.44 tail block is not self-contained (inward): "
          + ", ".join(inward[:8]))
    fails += 1
else:
    print(f"PASS MCP p.44 tail block self-contained inward: printed "
          f"p.43's four stand-ins are exactly this page's four "
          f"symbols, and neither of the two names it defines outside "
          f"the block ({', '.join(outside)}) is referenced inside it")

finish(fails)
