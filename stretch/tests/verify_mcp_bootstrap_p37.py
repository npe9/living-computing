#!/usr/bin/env python3
"""verify_mcp_bootstrap_p37.py -- THE COMMUNICATION REGION FOR MCP,
printed page 37 (../decks/mcp_bootstrap_p37.strap).
docs/MCP_Mar63_001-249.pdf PDF p.44, header "PAGE NUMBER 37".
AGENTS.md rule 3.

Twenty-three printed rows with binary output and twenty-eight symbol
locations -- every row on the page.

>>> THIS IS THE PAGE MCP'S INITIALIZATION WAS BRANCHING TO. <<<

With the console switch register built, the boot run gets through
printed pp.15-36 without entering an error site and branches to
002166.00.  Line 45 of this page is "S PRIME  SYN,$", the first word
past the end of the communication region, and line 31 is
"S PR IN  VF,S PRIME  -ENTRY TO PRIME ROUTINE".  So MCP had finished
initialization and handed off, which is a different thing from
getting lost, and nothing but this page could say which.

>>> IT DEFINES TWENTY-ONE SYMBOLS pp.15-36 HAVE BEEN SYNNING. <<<

strap/mcp_image.py's merge() carried 44 EXTERNAL names across printed
pp.15-36 -- used there, defined nowhere transcribed, each held up by
one page's stand-in SYN.  Twenty-one of them are defined here:

  S MCP      002150.00    S YCOCH    002156.00
  S COM SZ   002150.40    S YPRCH    002156.40
  S COM RG   002151.00    S DKMCP    002157.00
  S XCHAN    002152.00    S SYRFT    002157.40
  S BAMCP    002153.00    S PR IN    002160.00
  S R TAPE   002153.40    S PR OUT   002160.40
  S W TAPE   002154.00    S IF DMP   002161.00
  S READ R   002154.40    S REJ JB   002161.40
  S BA PP    002155.00    S ROOF     002162.00
  S MAXRN    002155.40    S MARK     002162.40
                          S IA       002163.00

EVERY ONE WAS DECODED OUT OF AN INSTRUCTION ON A PAGE TRANSCRIBED
BEFORE THIS ONE WAS OPENED.  The merge now checks each stand-in
against the definition instead of against itself -- the
pp.7-8/pp.9-13 cross-check again, and the strongest form of it so
far, because these twenty-one come from nine different pages.

S BA PP at 002155.00 is a second witness for printed p.36 line 34's
"S LR BU  SYN, S BA PP", which that page's own verifier already
pins at the same address from the other direction.

LINE 34 IS listing_typography.md 13 FOR THE THIRTEENTH TIME, and the
easiest instance yet: the page prints "000000.C4 00" and the field
is the OCTAL bit address, which cannot hold a C.  "BD,0" assembles
to 000000.04 00.

TWO ROWS PRINT NO BINARY.  Lines 42 and 43 are "(AX)DD(BU)"
character data and the BINARY OUTPUT column is empty, exactly as it
is for the (IQS*) message rows on printed pp.9-12.  NO CHARACTER
CODE IS CHECKED OR CAN BE.  What is checked is the counting: eight
characters at eight bits is one word each, and S END CM lands at
002166.00 only if both are exactly that.  Line 43's blanks were
counted by COLUMN ALIGNMENT against line 42 at 900 dpi -- its two
slashes sit under line 42's two slashes.

THE SYN ROWS (14, 15, 44, 45, 46) print their RESOLVED VALUE in the
LOCATION column rather than the counter, so they are checked through
SYMBOLS below and not through ROWS.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p37.strap").read())

SYMBOLS = {
    "SMCP":   "002150.00",
    "SCOMSZ": "002150.40",
    "SCOMRG": "002151.00",
    "SXCHAN": "002152.00",
    # Lines 14 and 15: the listing prints these SYNs' RESOLVED values
    # in the LOCATION column -- 002152.34+ and 002152.00+ -- and 0o34
    # is 28 decimal, so "SYN,S XCHAN+.28" lands on the count field's
    # first bit of the index word line 13 compiled.
    "SCHANK": "002152.34",
    "SCHANS": "002152.00",
    "SBAMCP": "002153.00",
    "SRTAPE": "002153.40",
    "SWTAPE": "002154.00",
    "SREADR": "002154.40",
    "SBAPP":  "002155.00",
    "SMAXRN": "002155.40",
    "SYCOCH": "002156.00",
    "SYPRCH": "002156.40",
    "SDKMCP": "002157.00",
    "SSYRFT": "002157.40",
    "SPRIN":  "002160.00",
    "SPROUT": "002160.40",
    "SIFDMP": "002161.00",
    "SREJJB": "002161.40",
    "SROOF":  "002162.00",
    "SMARK":  "002162.40",
    "SIA":    "002163.00",
    # The two (AX) rows print no binary; these three addresses are
    # what measures them.  S DATE and S TODAY are one word each, so
    # S END CM can only land at 002166.00 if both are eight
    # characters of eight bits.
    "SDATE":  "002164.00",
    "STODAY": "002165.00",
    "SENDCM": "002166.00",
    "SPRIME": "002166.00",
    "SPRIMR": "002166.40",
}

ROWS = [
    ("002147.40", "000000.30 00", "line 6   CNOP"),
    ("002150.00", "000000.00+",
     "line 7   S MCP  VF,0  -SLOT FOR BASE ADDRESS OF MCP"),
    # THE ONE ARITHMETIC ROW ON THE PAGE, and the one worth the most:
    # S END CM - S MCP is 002166.00 - 002150.00 = 0o16 words, printed
    # 000016.00.  FOURTEEN WORDS.  Nothing states that number; it is
    # the extent of everything between the two labels, which is the
    # same kind of measurement printed p.36 is built out of.
    ("002150.40", "000016.00+",
     "line 9   S COM SZ  VF,S END CM-S MCP  -SIZE OF COMMUNICATION REGION"),
    ("002151.00", "100000.00+ 000 000000 000000",
     "line 11  S COM RG  XW,(8)100000.0,  -THE SYSTEM WORD FLAG"),
    ("002152.00", "000000.00+ 000 000050 000000",
     "line 13  S XCHAN  XW,0,40,0  -BASE ADDRESS OF CHAN STATUS TABLE"),
    ("002153.00", "000000.00+",
     "line 17  S BAMCP  VF,0  -BASE ADDR OF THE MCP SYMB I/O LOC TBL"),
    ("002153.40", "000001.00+",
     "line 18  S R TAPE  VF,1.0  -THE SPOOL READ TAPE IOD REF NO."),
    ("002154.00", "000002.00+",
     "line 19  S W TAPE  VF,2.0  -THE SPOOL WRITE TAPE IOD REF NO."),
    ("002154.40", "000003.00+",
     "line 20  S READ R  VF,3.0  -THE SPOOL READER IOD REF NO."),
    ("002155.00", "000000.00+",
     "line 21  S BA PP  VF,0  -BASE ADDRESS OF PP IO LOCATION TABLE"),
    ("002155.40", "000000.00+",
     "line 23  S MAXRN  VF  -S MAX RN THE MAX REFERENCE NO FOR PP"),
    # BOTH CHANNEL SLOTS START AT THE SAME VALUE, and that is IBM's
    # doing, not a transcription slip: the comments distinguish them
    # and the compiled words do not.  It also settles a question the
    # boot run raised -- finding S YCOCH and S YPRCH equal at the END
    # of initialization is not by itself evidence that anything
    # copied one into the other.
    ("002156.00", "000026.04+",
     "line 25  S YCOCH  VF,22.4  -THE CHANNEL NUMBER OF THE CONSOLE"),
    ("002156.40", "000026.04+",
     "line 26  S YPRCH  VF,22.4  -THE CHANNEL NUMBER OF THE PRINTER"),
    ("002157.00", "000000.00+",
     "line 28  S DKMCP  VF,0  -MCP RESET TRACK FOR DISK"),
    ("002157.40", "000000.00+",
     "line 29  S SYRFT  VF,0  -VARIABLE POINTER FOR PP DISK ASSIGN"),
    # THE TWO FORWARD REFERENCES THAT NAME WHERE MCP WENT.  S PRIME
    # and S PRIM R are defined on lines 45 and 46, nine rows below,
    # and these two words are how the rest of MCP finds them.
    ("002160.00", "002166.00+",
     "line 31  S PR IN  VF,S PRIME  -ENTRY TO PRIME ROUTINE"),
    ("002160.40", "002166.40+",
     "line 32  S PR OUT  VF,S PRIM R  -SAVED ADDRESS JOE PRIME ROUTINE"),
    # THE ONLY INSTRUCTION ON THE PAGE, in the middle of a data
    # region: a Branch Disabled to 0.0, which is a halt, planted
    # where a runaway instruction fetch would land.
    ("002161.00", "000000.04 00",
     "line 34  S IF DMP  BD,0  -INSTRUCTION FETCH TRAP INSTRUCTION"),
    ("002161.40", "000000.00+",
     "line 35  S REJ JB  VF,0.0  -THE NUMBER OF JOBS TO REJECT"),
    ("002162.00", "000000.00+", "line 37  S ROOF  VF,0  - TOP OF STORAGE"),
    ("002162.40", "000000.00+",
     "line 38  S MARK  VF  -THE NEXT VACANT REEL SLOT FOR PP"),
    ("002163.00", "000000.00+",
     "line 40  S IA  VF,0  - LOCATION OF INTERRUPT TABLE"),
    ("002163.40", "000000.30 00", "line 41  CNOP"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.37 ")
finish(fails)
