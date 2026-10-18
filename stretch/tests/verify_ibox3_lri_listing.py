#!/usr/bin/env python3
"""verify_ibox3_lri_listing.py -- IBOX-3 routine 1230 blocks I3021-I3027
(../decks/ibox3_lri.strap) against jb_ax3a pp.210-212.

LOAD REFILL IMMEDIATE, swept over every bit of the 18-bit refill field
(IBM bits 46-63) plus all-ones and all-zeros.  One of the eight modeled
index operations a coverage screen found in zero suite programs.

THE EXPECTED ROWS ARE GENERATED FROM A TABLE, and that deserves a word
because the rest of this suite writes its oracle rows out longhand.
This block is 121 half-words of twenty near-identical six-row tests,
and the only thing that varies between them is one octal immediate.
The (bit, immediate) table below was read off pp.210-212, and the row
PATTERN -- "<imm>.05 01" for the LVI, "<imm>.01 03" for the LRI, then
the same four fixed rows -- was confirmed against the printed encodings
on every test of all three pages before it was written down.  What is
generated is the repetition, not the values.
"""
from strap_asm import assemble
from listing_oracle import check_rows, finish

prog = assemble(open("../decks/ibox3_lri.strap").read())

# (what the listing calls it, its octal immediate), pp.210-212 in order.
TESTS = [(63, "1"), (62, "2"), (61, "4"), (60, "10"), (59, "20"),
         (58, "40"), (57, "100"), (56, "200"), (55, "400"), (54, "1000"),
         (53, "2000"), (52, "4000"), (51, "10000"), (50, "20000"),
         (49, "40000"), (48, "100000"), (47, "200000"), (46, "400000"),
         ("ALL ONES", "777777"), ("ALL ZEROS", "0")]
LABELS = {0: "I3021", 3: "I3022", 6: "I3023", 9: "I3024",
          12: "I3025", 15: "I3026", 18: "I3027"}

CODE_ROWS = []
hw = 0o33174 * 2                      # half-word address of I3021
def row(val, src):
    global hw
    CODE_ROWS.append(("%06o.%s" % (hw >> 1, "40" if hw & 1 else "00"), val, src))
    hw += 1

for i, (bit, imm) in enumerate(TESTS):
    tag = "test bit %s" % bit if isinstance(bit, int) else "test %s" % str(bit).lower()
    lab = LABELS.get(i, "")
    row("%s.05 01" % imm, "%s LVI, $X2, (8)%s.0   %s" % (lab, imm, tag))
    if i == 0:
        row("33175.04 00", "BD, $+.32")
    row("%s.01 03" % imm, "LRI, $X0, (8)%s" % imm)
    row("33301.01 70", "SR, $X0, I30ST")
    row("33301.04 90", "KV, $X2, I30ST")
    row("1310.00 80", "SIC, SEN")
    row("1304.32 C0", "BZXE, SERS   failed to load %s" %
        ("bit %d" % bit if isinstance(bit, int) else str(bit).lower()))

assert CODE_ROWS[-1][0] == "033270.00", CODE_ROWS[-1][0]   # the listing's last row
assert len(CODE_ROWS) == 121, len(CODE_ROWS)

if __name__ == "__main__":
    finish(check_rows(prog, CODE_ROWS, label="code"))
