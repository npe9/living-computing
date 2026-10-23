#!/usr/bin/env python3
"""verify_mcp_bootstrap_p46.py -- THE BREAKDOWN ROUTINE's re-entry,
save area and tables, printed page 46
(../decks/mcp_bootstrap_p46.strap).
docs/MCP_Mar63_001-249.pdf PDF p.53, header "PAGE NUMBER 46".
AGENTS.md rule 3.

Twenty printed rows with binary output and fifteen symbol locations.

>>> THIS PAGE DEFINES EVERY ONE OF printed p.45's FOURTEEN STAND-INS
AND NOT ONE OF THEM MOVES. <<<

Three of them are index registers (lines 22-24, "QX INN SYN,$1" and
its two fellows), one is the integer 6 (line 33), and the other ten
are addresses.  p.45 read all fourteen off its own binary.

AND THE TWO dds p.45 HAD TO WRITE BY HAND ARE PRINTED HERE: lines 30
and 32 are "(A*)DD(BU,Q KSIZ,Q KSIZ)" -- (BU,6,6) -- which is what
p.45's bare "KF,Q CMA" and "KF,Q BLNK" print as 006600.  Line 9 here
is the same row and checks it again.

THREE MORE SWAPs AND NOW THERE ARE NINE.  Lines 2-4 are the mirror of
p.45 lines 47-49: p.45 swapped the live index registers into Q SAV on
the way out of the error, these swap them back on the way in, under
line 1's "-RE-ENTRY POINT FOLLOWING ERROR RETURN".  Line 5's
"TI,2,Q SAV4,$L" is p.45 line 50's transmit reversed.

THE PAGE CORRECTED THE ASSEMBLER IN FOUR PLACES, and the deck header
has them.  The one this file checks directly is the first:

  VF IS TWENTY-FIVE BITS.  C22-6531 printed p.18: "THE LOCATION
  COUNTER STANDS AT BIT 25 at the end of the operation."  strap_asm
  carried a note saying so while returning a whole half word anyway,
  because "nothing in the corpus distinguishes the two".  LINES 29
  AND 30 DO: "Q SKIP VF,.16" is at 002556.00 and the next row,
  "Q CMA (A*)DD(...)", is at 002556.31 -- bit 25.  The four symbols
  in that one word chain 0 -> 25 -> 31 -> 49, and all four are
  checked below.

AND THAT FOUND A MISSING LINE IN ANOTHER DECK: printed p.8 line 30 is
a "CNOP" that mcp_bootstrap_p7_p8.strap had omitted, invisible while
VF claimed a half word and the first thing to fail when it stopped.

SIX INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  "Q KSIZ SYN,6" -> "SYN,8" -- 6 FAILs: QCOUNT and Q BLNK move two
  bits, lines 9 and 12 carry 010000/110000 instead of 006600/106000,
  line 31 reads 600003, and the Q KSIZ check itself.
  Line 20's bare "XW" deleted -- 13 FAILs: every symbol from Q SAV6
  on moves a word, and lines 6 and 7 follow them.
  "XW,0.,9,QWCF9" -> "...,8,..." -- 1 FAIL, line 28's count.
  AND ONE IN THE ASSEMBLER, which is the one that matters here:
  statement_size's VF arm put back to (HALF, HALF) -- 5 FAILs, all
  three symbols in word 002556 seven bits out, line 9's address
  002556.40 for 002556.31, and line 31 reading 154000 for 000014.
  Line 32's Q BLNK given TWO blanks instead of one -- this SURVIVED
  every row, every symbol and the image build, and is why the
  printed-p.47 check below exists; with it, 1 FAIL.
  AND ONE AGAINST THE MERGE: printed p.45's "Q KSIZ SYN,6" changed to
  "SYN,7" so the two pages disagree -- mcp_image dies with "QKSIZ is
  defined twice: printed p.45 and printed p.46, and they disagree:
  bit 7 against bit 6", which is the failure path the new
  agreeing-SYN acceptance had to keep.
"""
from listing_oracle import check_rows, finish, loc_bits
from strap_asm import assemble, iter_statements, statement_size

prog = assemble(open("../decks/mcp_bootstrap_p46.strap").read())

SYMBOLS = {
    "QBRK8": "002536.00",
    "QSPAC": "002543.00",
    # The save area, lines 16-21.  002553 is line 20's unnamed XW,
    # "-STORE $R", which is why Q SAV6 is two words after Q SAV4.
    "QSAV1": "002547.00",
    "QSAV2": "002550.00",
    "QSAV3": "002551.00",
    "QSAV4": "002552.00",
    "QSAV6": "002554.00",
    # >>> THE FOUR IN ONE WORD, 0 -> 25 -> 31 -> 49.  This is the
    # chain that proved VF is twenty-five bits.
    "QWCF9": "002555.00",
    "QSKIP": "002556.00",
    "QCMA":  "002556.31",
    "QCOUNT": "002556.37",
    "QBLNK": "002556.61",
}

ROWS = [
    # >>> THREE MORE SWAPs, the mirror of printed p.45 lines 47-49.
    ("002536.00", "000021.00 80  002547.02 E0",
     "line 2   Q BRK8  SWAPI,1,QX INN,Q SAV1  -RESET INDEXES"),
    ("002537.00", "000022.00 80  002550.02 E0", "line 3   SWAPI,1,QX OUT,Q SAV2"),
    ("002540.00", "000023.00 80  002551.02 E0", "line 4   SWAPI,1,QX CF9,Q SAV3"),
    # p.45 line 50 reversed.
    ("002541.00", "002552.00 80  000010.04 A0", "line 5   TI,2,Q SAV4,$L  -RESET $L AND $R"),
    ("002542.00", "002554.36 10", "line 6   LX,$15,Q SAV6"),
    ("002542.40", "002556.04 B0", "line 7   V+,QX OUT,Q SKIP  -SKIP TO BEG OF NEXT OUTPUT"),
    ("002543.00", "002526.02 4A", "line 8   Q SPAC  CBZ,QXINN,QRSTR  -TEST FOR LAST INPUT CHAR"),
    # >>> THE dds TRAVELS, AGAIN: no data description is written and
    # the row prints 006600, Q CMA's own (BU,Q KSIZ,Q KSIZ).
    ("002543.40", "002556.31 80  006600.23 10",
     "line 9   KF,Q CMA  -TEST FOR COMMA.  FIRST CANNOT BE A COMMA"),
    ("002544.40", "002507.76 C2", "line 11  BAE,Q NEXT"),
    ("002545.00", "000000.06 81  106000.06 70",
     "line 12  LF(V+I)(BU,Q KSIZ),Q KSIZ(QX INN)  -LOAD NEXT INPUT CHAR"),
    ("002546.00", "002543.10 00", "line 13  B,Q SPAC"),
    # THE SAVE AREA: six index words, every field zero.  "XW," with a
    # null value field, and line 20 "XW" with no comma at all.
    ("002547.00", "000000.00+ 000 000000 000000", "line 16  Q SAV1  XW,  -STORE INDEXES"),
    ("002550.00", "000000.00+ 000 000000 000000", "line 17  Q SAV2  XW,"),
    ("002551.00", "000000.00+ 000 000000 000000", "line 18  Q SAV3  XW,"),
    ("002552.00", "000000.00+ 000 000000 000000", "line 19  Q SAV4  XW,  -STORE $L"),
    ("002553.00", "000000.00+ 000 000000 000000", "line 20  XW  -STORE $R"),
    ("002554.00", "000000.00+ 000 000000 000000", "line 21  Q SAV6  XW,  -STORE $15"),
    # The one index word with contents: count 9, refilling itself.
    ("002555.00", "000000.00+ 000 000011 002555",
     "line 28  QW CF9  XW,0.,9,QWCF9  -NO. OF CHARS PER OUTPUT FIELD"),
    # >>> THE VF THAT PROVED THE POINT: 25 bits, and line 30 starts
    # at bit 25 of the same word.
    ("002556.00", "000000.20+", "line 29  Q SKIP  VF,.16  -NO. OF BIT BETWEEN FIELDS"),
    # Eighteen bits at bit 31 of the word -- not on any boundary, so
    # the width is given rather than guessed.
    ("002556.37", "000014", "line 31  QCOUNT  DD(BU,18),(8)000014  -MAX. NO. FIELDS", 18),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.46 ")

# ---------------------------------------------------------------------
# Q KSIZ IS AN INTEGER, NOT AN ADDRESS, so it cannot go in SYMBOLS.
# Line 33 is "Q KSIZ  SYN, 6" and the listing prints its value as
# "+00000006" with "NULL" where a dds would be.  Everything on this
# page and on printed p.45 that writes "(BU,Q KSIZ)" compiles a byte
# size of six because of it.
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# >>> Q BLNK IS THE LAST DATUM ON THE PAGE AND printed p.47 LINE 1 IS
# WHAT PINS ITS LENGTH. <<<
#
# Nothing on THIS page can: Q CMA is held from above by QCOUNT's
# 002556.37, but Q BLNK has no successor here, and the content cannot
# discriminate either -- a blank is 0o00 and so is a second blank.
# MEASURED: giving it two blanks instead of one passes every row,
# every symbol and the image build.
#
# printed p.47 line 1 is "SLC,$" at 002556.67, which is bit 55 -- Q
# BLNK's 002556.61 is bit 49, and 49 + 6 is 55 TO THE BIT.  Two
# blanks would end at bit 61 and the listing says otherwise.  The same
# shape as printed p.42's last datum ending exactly on S CA6 and
# printed p.44's ending exactly on printed p.45's "SLC,$".
# ---------------------------------------------------------------------
_P47_SLC = "002556.67"
qblnk = [st for st in iter_statements(open("../decks/mcp_bootstrap_p46.strap").read())
         if st.name and st.name.upper() == "QBLNK"]
if len(qblnk) != 1:
    print(f"FAIL MCP p.46 expected one Q BLNK statement, found {len(qblnk)}")
    fails += 1
else:
    _, width = statement_size(qblnk[0], prog.symtab)
    want = loc_bits(_P47_SLC) - loc_bits("002556.61")
    if width == want:
        print(f"PASS MCP p.46 Q BLNK is {width} bits, which is printed "
              f"p.47 line 1's SLC,$ at {_P47_SLC} minus Q BLNK's own "
              f"002556.61")
    else:
        print(f"FAIL MCP p.46 Q BLNK compiles {width} bits; printed p.47 "
              f"line 1's SLC,$ at {_P47_SLC} leaves room for {want}")
        fails += 1

if prog.symtab.get("QKSIZ") == 6:
    print("PASS MCP p.46 Q KSIZ = 6 (line 33, an integer SYN used three "
          "rows above where it is defined)")
else:
    print(f"FAIL MCP p.46 Q KSIZ = {prog.symtab.get('QKSIZ')!r}, want 6")
    fails += 1

# AND THE THREE INDEX-REGISTER SYNs, lines 22-24.  Their VALUE is the
# register's bit address, which is what the listing prints in the
# location column -- 000021.00+, 000022.00+, 000023.00+ -- while the
# rows that USE them carry the register number.  Both halves matter,
# so both are checked: the value here, the use in line 12's 81.
for name, want_word in (("QXINN", 0o21), ("QXOUT", 0o22), ("QXCF9", 0o23)):
    got = prog.symtab.get(name)
    if got == want_word * 64:
        print(f"PASS MCP p.46 {name} value = {want_word:06o}.00, the index "
              f"register's own address")
    else:
        print(f"FAIL MCP p.46 {name} value = {got!r}, want {want_word * 64}")
        fails += 1

finish(fails)
