"""MCP INITIALIZATION, printed p.80 -- LOOK AHEAD -N- JOBS AND
DETERMINE THE STATUS.

Thirty-one lines, twenty-eight of which compile.  A short page, and
the one the boot run has been waiting for.
decks/mcp_bootstrap_p80.strap carries the derivations.

>>> LINE 4 IS T PICA, AND THE PC TRAIL HAS READ 004604.00 SINCE
printed p.75 LANDED. <<<  p.75 line 50 is "T L  B,T PICA  -NOT
OVERLAP JOB NOT ASSIGNED", one of the ten exits in its dispatch
table, and printed p.79 lines 36-37 branch here twice more.

>>> AND IT IS THE END OF THE ASSIGN ROUTINE. <<<  Lines 30-31 are
"T P1A  SWAPI,12,$1,T ASAVE  -RESTORE INDEXES" and "B,1.00($15)
-RETURN", and printed p.65 line 6 -- FIFTEEN PAGES BACK, the first
instruction of the routine -- is "T ASIGN  SWAPI,12,$1,T ASAVE
-SAVE INDEXES".  THE TWO ROWS ARE BYTE FOR BYTE IDENTICAL: both
compile 000021.00 80  003274.30 E0, one at 003701.00 and one at
004626.00.  They are the same instruction because SWAP is an
EXCHANGE -- it does not copy, it swaps -- so saving and restoring
twelve index registers is one operation written twice, and only the
comment differs.

So printed pp.65-80 are MCP's ASSIGN routine entire: entry, the
channel and unit scans, the dispatch table, the reject path, the
printed messages, and the return.

A FIFTH BYTE THE ASSEMBLER DISPUTED AND THE INK SETTLED.  Line 16's
opcode byte was transcribed 3B at 600 dpi and is 38.  The statement
is "LV,T IXA,T CRREF(T IXG)" -- confirmed at 1200 dpi -- and T IXG
is $8, so the index modifier in the byte's low nibble must be 8.  At
1800 dpi the glyph is an 8, and the row's own octal field prints
C0CCC00 for 0000000, five of seven glyphs open: a
listing_typography.md 13d row throughout.  Seven such disputes this
session, seven times the ink agreed with the assembler -- and the
render still happens first, because printed p.66 line 5 is the case
that went the other way.

T PICA and T P1BA were already stand-ins -- p.75 and p.79 for the
first, printed p.77 line 37's "BBZ,YSCRBT,T P1BA" for the second --
and both agree.  T JBPRO's stand-in needed the (BU,1) printed p.62
line 11 gives it: line 24 is a CONNECTIVE and takes its length from
the symbol.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  Line 30's SWAPI count 12 becomes 11 -- 1 FAIL at 004626.00,
  reading 003274.26 E0 for 003274.30 E0.  The count sits in bits
  18-23 of the second group, so twelve prints ".30" and eleven
  ".26"; printed p.65 line 6 saved TWELVE and this row restores
  them, so an off-by-one here leaves an index register holding
  ASSIGN's working value after the return.
  Line 31's return offset 1.00 becomes 0.0 -- 1 FAIL at 004627.00,
  reading 000000.10 for 000001.10.  $15 points at the PARAMETER
  BLOCK, not at the return; one word past it is the caller's next
  instruction, and zero would branch back into the parameter word
  itself.
  Line 16's index T IXG becomes the T IXA the row loads into -- 1
  FAIL at 004614.40, reading 34 for 38.  THIS IS THE ROW WHOSE BYTE
  WAS TRANSCRIBED 3B, and the injection shows what the two plausible
  index names actually produce: 8 for T IXG and 4 for T IXA.
  Neither is B.
  T JBPRO's stand-in loses the (BU,1) printed p.62 line 11 gives it
  -- 1 FAIL at 004622.00, reading 000000 for 001000.  A CONNECTIVE
  takes its length from the SYMBOL (C22-6531 printed p.31), and six
  other decks in this corpus carry T JBPRO without a dds because
  they only ever branch on it.
  Line 23's branch goes to T PICA instead of T AREJX -- 1 FAIL at
  004621.40, reading 004604 for 004360.  Both are real addresses on
  pages in the image, which is what makes the row worth checking.
  Line 28's V+ICR loses its refill -- 1 FAIL at 004625.00, 06 for
  07.
  YSCRBT's stand-in moves to bit 2, T NGATE's -- 1 FAIL at
  004617.40, reading 004455.02 for 004455.03.  printed p.76 declares
  four one-bit flags in one word and a stand-in on the wrong one
  still assembles.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p80.strap").read())

SYMBOLS = {
    # The address printed pp.75 and 79 branch to, and where the boot
    # run's PC trail has stopped for six pages.
    "TPICA": "004604.00",
    # Labels this page defines.
    "TPIC":  "004606.00",
    "TP1B":  "004612.00",
    "TP1BA": "004622.00",
    "TP1A":  "004626.00",
}

ROWS = [
    ("004604.00", "003315.20 10",
     "line 4   T PICA  LX,TIXG,TPPRUN"),
    ("004604.40", "000000.24 1F",
     "line 5   LX,TCTWDX,0.0($15)"),
    ("004605.00", "004606.23 40",
     "line 6   BZXF,TPIC"),
    ("004605.40", "003313.20 10",
     "line 7   LX,TIXG,TPPURF"),
    ("004606.00", "000000.34 8F  002000.00 F0",
     "line 8   T PIC  CM0000(BU,2),0.28($15)"),
    ("004607.00", "003264.61 30",
     "line 9   SV,TIXG,TNEXT"),
    ("004607.40", "000000.47 88  004612.34 00",
     "line 10  BZB,TLPPEN(TIXG),TP1B"),
    ("004610.40", "000000.55 8F  001000.36 F0",
     "line 11  CM1111(BU,1),0.45($15)"),
    ("004611.40", "004626.10 00",
     "line 12  B,TP1A"),
    ("004612.00", "000000.45 88  001000.07 70",
     "line 13  T P1B  CT0011,TRJECT(TIXG)"),
    ("004613.00", "004622.34 C0",
     "line 14  BZRZ,TP1BA"),
    ("004613.40", "000000.46 88  004626.34 02",
     "line 15  BB,TASGNP(TIXG),TP1A"),
    ("004614.40", "000000.10 38",
     "line 16  LV,TIXA,TCRREF(TIXG)"),
    ("004615.00", "000000.34 88  010027.20 50",
     "line 17  L,TUNCT(TIXG),46"),
    ("004616.00", "000011.10 50",
     "line 18  LC,TIXA,$R"),
    ("004616.40", "000000.45 88  001000.36 F0",
     "line 19  CM1111,TRJECT(TIXG)"),
    ("004617.40", "004455.03 80  001000.36 F0",
     "line 20  CM1111,YSCRBT"),
    ("004620.40", "003271.11 03",
     "line 21  LRI,TIXA,TREFIL"),
    ("004621.00", "003271.11 10",
     "line 22  SX,TIXA,TREFIL"),
    ("004621.40", "004360.10 00",
     "line 23  B,TAREJX"),
    ("004622.00", "000000.44 88  001000.36 F0",
     "line 24  T P1BA  CM1111,TJBPRO(TIXG)"),
    ("004623.00", "000000.34 8F  001000.36 F0",
     "line 25  CM1111(BU,1),0.28($15)"),
    ("004624.00", "000000.24 1F",
     "line 26  LX,TCTWDX,0.0($15)"),
    ("004624.40", "004626.23 42",
     "line 27  BXF,TP1A"),
    ("004625.00", "000002.21 07",
     "line 28  V+ICR,TIXG,2.0"),
    ("004625.40", "003315.21 10",
     "line 29  SX,TIXG,TPPRUN"),
    ("004626.00", "000021.00 80  003274.30 E0",
     "line 30  T P1A  SWAPI,12,$1,TASAVE"),
    ("004627.00", "000001.10 0F",
     "line 31  B,1.00($15)"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.80 ")
finish(fails)
