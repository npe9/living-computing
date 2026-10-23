#!/usr/bin/env python3
"""verify_mcp_bootstrap_p38.py -- UNCODE SUBROUTINE TO DECIPHER SYSTEM
CARDS, printed page 38 (../decks/mcp_bootstrap_p38.strap).
docs/MCP_Mar63_001-249.pdf PDF p.45, header "PAGE NUMBER 38".
AGENTS.md rule 3.

Thirty-six printed rows with binary output -- every row on the page
that compiles anything -- and nineteen symbol locations.

>>> THIS IS WHERE MCP WENT. <<<

printed p.37 line 45 puts S PRIME at 002166.00 and line 31 points
S PR IN at it.  The boot run's PC trail says MCP's initialization
branched to half-word 2284, which is 002166.00.  LINE 4 OF THIS PAGE
IS THAT ADDRESS, and its name is Y UNCOD -- the last external
strap/mcp_image.py still carried there.  The PRIME ROUTINE and the
UNCODE SUBROUTINE are the same entry, which neither page says on its
own.

>>> AND FOURTEEN FORWARD REFERENCES ARE PREDICTIONS. <<<

This page uses fourteen symbols it does not define, every one of them
at an address LATER than any page transcribed so far (002213 through
002502, where p.38 itself ends at 002213.00).  Each is SYN'd here
from THIS PAGE'S OWN BINARY OUTPUT and nothing else:

  Y UX SAV 002324.00   Y UCBF2  002337.00   Y JCCER  002303.40
  Y UER    002311.00   Y JCBC   002213.00   Y REELC  002276.00
  S CA6    002422.00   Y TCPGO  002214.40   Y REL MK 002360.00
  Y UCBF1  002327.00   Y LIMC   002246.00   Y TYPMK  002355.00
  S BRK8   002502.00   Y IODC   002266.40

READING THEM REQUIRED THE HALF-WORD BIT LAYOUT, not just the octal.
A half-word prints `wwwwww.bb XX`, and the `.bb` pair is bits 18-23:
bit 18 the HALF-WORD SELECTOR, bits 19-22 the J field, bit 23 the
first bit of the operation code.  So line 30's `.32` and line 40's
`.36` are bit 18 CLEAR -- the FIRST half word, `.00` -- while line
31's `.72`, line 34's `.50` and line 35's `.72` are bit 18 SET, which
is `.40`.  Three of the fourteen are at `.40` for that reason and
would have been wrong by half a word without it.

THE CHECK THAT THEY ARE RIGHT IS THE ROWS THEMSELVES: every one of
the thirty-six below renders identically to the listing, and six of
them carry one of these addresses in a field the listing prints.
Y UER appears in FOUR rows (8, 36, 38, 41) with three different
operation codes and agrees in all of them.

WHAT THE PAGE DOES.  Lines 4-12 save three index registers, take the
card's address out of $14, load twelve bits and compare them against
(2)100010000000 -- a "B" in the card code, the class column every
IOCD and IOD card carries (C22-6728 printed p.88) -- and call S CA6
to convert the card to six-bit BCD.  Lines 21-41 then compare the
card's first forty-eight bits against Y TYPMK and walk the
dispositions: JOB, T.O.P., LIM, IOD, REEL.

LINES 13-15 AND 18-20 ARE ARGUMENTS, NOT INSTRUCTIONS, and that is
why they are VF/CF/VF triples sitting between two branches.
"LVI,$15,$+1.0" plants the return address in $15 and "BD,<routine>"
goes; the half-words after the branch are the call's parameters, and
the routine steps over them on the way back.  A transcription that
read them as code would still assemble -- which is why their
ADDRESSES are checked below as well as their contents.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p38.strap").read())

SYMBOLS = {
    # The five this page DEFINES.
    "YUNCOD": "002166.00",
    "YUECS":  "002174.00",
    "YUSB8C": "002200.00",
    "YIPL1":  "002201.00",
    "YMKEAR": "002207.00",
    # The fourteen it PREDICTS.  Listed here so a future page that
    # defines one of them is checked against this reading rather
    # than against itself -- the same way printed p.37 was just
    # checked against the twenty-one stand-ins pp.15-36 carried.
    "YUXSAV": "002324.00",
    "YUER":   "002311.00",
    "SCA6":   "002422.00",
    "YUCBF1": "002327.00",
    "SBRK8":  "002502.00",
    "YUCBF2": "002337.00",
    "YJCBC":  "002213.00",
    "YTCPGO": "002214.40",
    "YLIMC":  "002246.00",
    "YIODC":  "002266.40",
    "YJCCER": "002303.40",
    "YREELC": "002276.00",
    "YRELMK": "002360.00",
    "YTYPMK": "002355.00",
}

ROWS = [
    # THE FIRST ROW IS THE WHOLE POINT OF THE PAGE: 002166.00, which
    # is where MCP's initialization branched.  Its left address is
    # 000033.00 -- word 0o33 is 27, which is index register $11, the
    # first of the three "SAVE UNDICIES" moves.
    ("002166.00", "000033.00 80  002324.06 A0",
     "line 4   Y UNCOD  TI,3,$11,Y UX SAV  -SAVE UNDICIES"),
    ("002167.00", "000001.73 BE",
     "line 5   LVE,$13,1.32($14)  -GET LOCATION OF HOLLERITH"),
    ("002167.40", "000000.00 8D  014000.20 50",
     "line 6   L(BU,12),0.0($13)  -CARD AND TEST FOR B"),
    ("002170.40", "420000.00 80  414000.23 10",
     "line 7   KFI(BU,12),(2)100010000000"),
    ("002171.40", "002311.36 C4",
     "line 8   BZAEZ,Y UER  -IF NOT A B GIVE ERROR RETURN"),
    ("002172.00", "002174.33 30",
     "line 9   SV,$13,Y UECS  -LOCATION OF CARD TO EDIT CALLING"),
    ("002172.40", "000001.32 3E", "line 10  LV,$13,1.0($14)  -DISP. TO $13"),
    ("002173.00", "002174.37 01",
     "line 11  LVI,$15,$+1.0  -CONVERT CARS TO 6-BIYT BCD"),
    ("002173.40", "002422.04 00", "line 12  BD,S CA6"),
    # THE FIRST CALL'S ARGUMENTS.  CF compiles a bare eighteen-bit
    # count with no bit part and no sign -- "000120" is 80 decimal,
    # which is the number of columns on a card.
    ("002174.00", "000000.00+", "line 13  Y UECS  VF,0.0"),
    ("002174.40", "000120", "line 14  CF,80  -eighty card columns", 18),
    ("002175.00", "002327.00+", "line 15  VF,Y UCBF1"),
    ("002175.40", "002176.77 01", "line 16  LVI,$15,$+1.0  -BREAK CARD INTO FIELDS"),
    ("002176.00", "002502.04 00", "line 17  BD,S BRK8"),
    ("002176.40", "002327.66+", "line 18  VF,Y UCBF1+.54"),
    ("002177.00", "000065", "line 19  CF,53.", 18),
    ("002177.40", "002337.00+", "line 20  VF,Y UCBF2"),
    ("002200.00", "000001.00+", "line 21  Y USB8C  VF,1."),
    ("002200.40", "000001.33 01",
     "line 22  LVI,$13,1.0  -ERROR RETURN- VALID ONLY FOR"),
    # A BRANCH TO THE NEXT HALF WORD, which is a no-op in effect and
    # a placeholder in intent: "JOB CARD SO FAKE DISPOSITION".
    ("002201.00", "002201.40 00", "line 23  Y IPL1  BE,$+.32"),
    ("002201.40", "002337.00 80  060000.20 50",
     "line 25  L(BU,48),Y UCBF2  -NORMAL RETURN TEST FIRST"),
    ("002202.40", "002355.00 8D  060000.21 10",
     "line 26  K(BU,48),Y TYPMK($13)  -FIELD IN CARD"),
    ("002203.40", "000001.33 04", "line 27  KVI,$13,1.0  -TEST DISPOSITION"),
    ("002204.00", "002207.36 C4",
     "line 28  BZAEZ,Y MKEAR  -IF FIRST FIELD IS NOT CORRECT"),
    ("002204.40", "002213.32 C6", "line 30  BXEZ,Y JCBC  -DISP. WAS JOB"),
    ("002205.00", "002214.72 46",
     "line 31  BXLZ,Y TCPGO  -CARD WAS T.O.P. - GO TYPE"),
    ("002205.40", "000002.33 04", "line 32  KVI,$13,2.0"),
    ("002206.00", "002246.32 C6", "line 33  BXEZ,Y LIMC  -CARD WAS A LIM."),
    ("002206.40", "002266.50 00", "line 34  B,Y IODC  -CARD WAS AN IOD."),
    ("002207.00", "002303.72 C2", "line 35  Y MKEAR  BXE,Y JCCER"),
    ("002207.40", "002311.32 42", "line 36  BXL,Y UER"),
    ("002210.00", "000002.33 04", "line 37  KVI,$13,2.0  -DISP. 2.0 OR 4.0"),
    ("002210.40", "002311.32 C6",
     "line 38  BXEZ,Y UER  -DISPOSITION WAS LIM- TO ERROR RETURN"),
    ("002211.00", "002360.00 80  060000.21 10",
     "line 39  K(BU,48),Y REL MK  -TESTR FOR REEL CARD"),
    ("002212.00", "002276.36 C6", "line 40  BAEZ,Y REELC"),
    ("002212.40", "002311.10 00", "line 41  B,Y UER"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.38 ")
finish(fails)
