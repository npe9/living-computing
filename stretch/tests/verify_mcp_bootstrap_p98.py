"""verify_mcp_bootstrap_p98.py -- MCP printed page 98 lines 20-37,
the SYN CARDS at the tail of the conversion subroutine.
docs/MCP_Mar63_001-249.pdf PDF p.105.  AGENTS.md rule 3.

>>> THIS PAGE IS NOT IN THE MERGED IMAGE, DELIBERATELY. <<<
strap/mcp_image.py lists its pages EXPLICITLY rather than globbing
decks/, so adding this file changes nothing until it is named there.
The transcribed range is printed pp.2-80 and gapless; p.98 is beyond
it, and wiring a non-contiguous page into the image is a separate
decision from preserving a verified transcription.

WHY THIS PAGE, OUT OF THE 88 THAT CARRY SYN CARDS.  It declares seven
symbols the existing decks already REFERENCE, which is what makes it
checkable against work already done.  printed pp.84-85 are bigger --
p.84 has 34 cards -- but all 38 symbols it declares were grepped
against every deck and NONE is referenced, so it proves nothing yet.

AND IT FOUND TWO LIVE BUGS, both now fixed in
decks/mcp_bootstrap_p39.strap: SYSMCD and SCORG were declared there
with NO data description -- length 0, which effLength reads as
SIXTY-FOUR -- where line 30 declares SYN(BU,2) and line 34
SYN(BU,1).  Addresses agreed; only the lengths were missing.  Same
fault as the CM1111 image bug, and hidden the same way: p.39 only
BRANCHES on them, and a branch never uses a length.

IT ALSO RETIRES A NOTE.  decks/mcp_bootstrap_p71.strap declares
"DFREE SYN, 0" under a header saying it is not defined anywhere this
project has read.  Line 27 is that card.

ONE DISPUTED GLYPH, RESOLVED WITHOUT THE INK.  Line 34's name prints
as "SCCRG" at 1800 dpi -- characters 2 and 3 are identical
open-right C's, the scan's own trap (docs/listing_typography.md 13).
It is read as SCORG on an argument independent of the glyph: line
34's LOCATION column is 002151.03, and printed p.39 line 19's left
address is 002151.03, the same bit.  Recorded as a disputed glyph
with a resolved symbol rather than as a clean read.

LINES 5-19 ARE DELIBERATELY ABSENT: fifteen VFL rows with no SYN
value, needing LBLZCR and TMX1, which no deck has read.  Including
them would mean back-deriving symbols from the check column itself.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p98.strap").read())

SYMBOLS = {
    "LXA":    "000034.00",   # line 20, dds "BU,1CC,1C" -> (BU,64,8)
    "YBCRD":  "005464.00",   # line 23
    "STATI":  "000000.32",   # line 24  0o32 = bit 26
    "SIMNT":  "000000.65",   # line 25  0o65 = bit 53
    "SMOUNT": "000000.63",   # line 26  0o63 = bit 51
    "DFREE":  "000000.00",   # line 27  -- p.71 said this was nowhere
    "YLCL2":  "005464.40",   # line 28
    "YLCL1":  "005465.00",   # line 29
    "SYSMCD": "002151.10",   # line 30  SCOMRG + bit 8
    "STERMI": "005465.40",   # line 31
    "ZFINIS": "017777.00",   # line 32
    "SMAXUB": "002153.00",   # line 33  = SBAMCP
    "SCORG":  "002151.03",   # line 34  SCOMRG + bit 3
    "XINEND": "005466.00",   # line 36
}

ROWS = [
    ("005464.00", "005464.04 00", "line 23  Y BCRD BD,$  -UNCODE PATH NOT TO BE TAKEN"),
    ("005464.40", "000000.00+",   "line 28  Y LCL2 VF"),
    ("005465.00", "000000.00+",   "line 29  Y LCL1 VF   (carries the bare listing mark)"),
    ("005465.40", "017777.00+",   "line 31  S TERMI VF,ZFINIS  -THE LAST LOC USED BY MCP"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.98 ")
finish(fails)
