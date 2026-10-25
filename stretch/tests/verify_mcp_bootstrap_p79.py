"""MCP INITIALIZATION, printed p.79 -- CHECK FOR REEL PROTECTION, and
the three messages themselves.

Thirty-nine lines, thirty-five of which compile, under one boxed
heading.  decks/mcp_bootstrap_p79.strap carries the derivations.

>>> THIS IS WHERE printed p.76's BUFFERS ARE ACTUALLY WRITTEN. <<<
p.76 is thirty-seven lines of character data whose only check was
that seventeen labels landed on their printed locations.  This page
is what the data is for: three calls to DMCP, each a branch followed
by a three-word parameter block -- a control word, a buffer address,
and a word count.

AND THE COUNTS ARE THE CHECK ON p.76 THAT p.76 COULD NOT MAKE.
T BUF01 is forty characters -- FIVE WORDS -- and the call asks for
5.0.  The "---  SET UP THE FOLLOWING UNITS  ---" message is counted
twice, once by the location counter on p.76 and once by the caller
here, two pages apart, and they agree.

>>> AND THE SUB HEADING'S COUNT IS FOUR WHERE ITS TEXT IS THREE,
WHICH IS NOT AN ERROR -- IT IS THE POINT. <<<  p.76 puts T SUBHD at
004445.00 and T PID at 004450.00, so " -- PROBLEM PROGRAM --- " is
exactly THREE words.  The call asks for FOUR, and the fourth word is
T PID, the eight blanks p.76 line 22 declares.  THAT SLOT IS FILLED
BY printed p.77: its line 26 is "SF,T PID", storing the problem
program's name after the conversion routine has turned it into IQS
characters.  So the sub heading on the operator's console is the
literal "-- PROBLEM PROGRAM ---" followed by the name of the job,
and it takes THREE PAGES to say so -- p.76 reserves the words, p.77
fills the last one, p.79 writes all four as one message.

THE MOUNTING MESSAGE IS THE SAME TRICK, INDEXED.  ",T BUFB1(T IXZ)"
and ",7.(T IXY)" index both the start and the length: T IXZ is 1.0
for overlap and 0.0 for not overlap (lines 6 and 8), and T IXY is 0,
+1.0 if not overlap, +2.0 if the reel is protected (lines 5, 9, 15).
Seven words from T BUFB1 is 004432.00 to 004441.00, covering p.76's
T BUFB1, the " MOUNT - REEL NUMBER " text, T REELX and the
" ON CHANNEL " text, stopping just short of T UNITX at 004441.20 --
and the index adds the words that reach the unit number and the
protection text, which printed p.78 has just filled in.

AND IT BRANCHES TO T PICA, WHICH IS WHERE THE RUN STOPS.  Lines 36
and 37 are "BZXF,T PICA" and "BBN,T NGATE,T PICA", both to
004604.00.  The boot run's PC trail has read 004604.00 since printed
p.75 landed, and printed p.80 line 4 is that address.

Three of printed p.77's forward stand-ins are placed here -- T P1 at
004600.00, T P2 at 004576.00 and T P3 at 004575.40 -- and T PENY was
a stand-in too.  All four agree.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  The sub heading's count 4.0 becomes the 3.0 its TEXT measures --
  1 FAIL at 004573.00, reading 000003.00 for 000004.00.  THIS IS
  THE ONE THAT MATTERS: three is what printed p.76's T SUBHD
  occupies and four is what the listing asks for, so the injection
  is the "obvious correction" a careless reader would make, and the
  listing refuses it.  The fourth word is T PID.
  The major heading's count 5.0 becomes 4.0 -- 1 FAIL at 004570.00.
  Five is exactly p.76's T BUF01, so this one has no excuse at all.
  The mounting message loses its length index T IXY -- 1 FAIL at
  004575.00, reading 000007.00 80 for 000007.00 86.  The index is
  the opcode byte's low nibble on a NULL-OPERATION row, which is
  the only place in this corpus a parameter word is indexed.
  Line 28's buffer loses its start index T IXZ -- 1 FAIL at
  004574.40, 80 for 85.
  Line 16's BB1 becomes BB -- 1 FAIL at 004565.40, reading 02 for
  0E in the second group's byte.
  Line 37's BBN becomes BB -- 1 FAIL at 004602.00, 02 for 0A.
  T SBHDI's stand-in moves ONE BIT, to T HEAD's -- 2 FAILS, at
  004570.40 and 004576.40, both reading 004455.00 for 004455.01.
  printed p.76 line 31-34 declares four one-bit flags in one word
  and a stand-in that lands on the wrong one still assembles.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p79.strap").read())

SYMBOLS = {
    # Stand-ins printed p.77 and printed p.78 have been carrying.
    "TP1":    "004600.00",
    "TP2":    "004576.00",
    "TP3":    "004575.40",
    "TP4":    "004556.40",
    "TPENY":  "004570.40",
    # Labels this page defines itself.
    "TP7":    "004563.40",
    "TWRITE": "004565.40",
    "TPEN":   "004573.40",
}

ROWS = [
    ("004555.40", "000000.32 84  002000.00 F0",
     "line 1   CM0000(BU,2),STATI(TXC)"),
    ("004556.40", "000000.63 84  001000.36 F0",
     "line 3   T P4  CM1111,SMOUNT(TXC)"),
    ("004557.40", "000000.65 84  001000.36 F0",
     "line 4   CM1111,SIMNT(TXC)"),
    ("004560.40", "000000.15 01",
     "line 5   LVI,TIXY,0"),
    ("004561.00", "000001.13 01",
     "line 6   LVI,TIXZ,1.0"),
    ("004561.40", "003273.23 80  004563.74 00",
     "line 7   BZB,TMODE,TP7"),
    ("004562.40", "000000.13 01",
     "line 8   LVI,TIXZ,0.0"),
    ("004563.00", "000001.15 05",
     "line 9   V+I,TIXY,1.0"),
    ("004563.40", "004631.02 80  006634.23 10",
     "line 13  T P7  KF,TNOP,56"),
    ("004564.40", "004565.76 C2",
     "line 14  BAE,TWRITE"),
    ("004565.00", "000002.15 05",
     "line 15  V+I,TIXY,2.0"),
    ("004565.40", "004455.00 80  004570.74 0E",
     "line 16  T WRITE  BB1,THEAD,TPENY"),
    ("004566.40", "001472.10 00",
     "line 17  B,DMCP"),
    ("004567.00", "000043.40 80",
     "line 18  ,DCCMM"),
    ("004567.40", "004424.00 80",
     "line 19  ,TBUF01"),
    ("004570.00", "000005.00 80",
     "line 20  ,5.0"),
    ("004570.40", "004455.01 80  004573.74 0E",
     "line 21  T PENY  BB1,TSBHDI,TPEN"),
    ("004571.40", "001472.10 00",
     "line 22  B,DMCP"),
    ("004572.00", "000043.40 80",
     "line 23  ,DCCMM"),
    ("004572.40", "004445.00 80",
     "line 24  ,TSUBHD"),
    ("004573.00", "000004.00 80",
     "line 25  ,4.0"),
    ("004573.40", "001472.10 00",
     "line 26  T PEN  B,DMCP"),
    ("004574.00", "000043.40 80",
     "line 27  ,DCCMM"),
    ("004574.40", "004432.00 85",
     "line 28  ,TBUFB1(TIXZ)"),
    ("004575.00", "000007.00 86",
     "line 29  ,7.(TIXY)"),
    ("004575.40", "004477.07 48",
     "line 30  T P3  CB+,TXB,TP5"),
    ("004576.00", "000002.05 07",
     "line 31  T P2  V+ICR,TXA,2.0"),
    ("004576.40", "004455.01 80  001000.00 F0",
     "line 32  CM0000(BU,1),TSBHDI"),
    ("004577.40", "004461.50 00",
     "line 33  B,TP6"),
    ("004600.00", "004455.00 80  002000.00 F0",
     "line 34  T P1  CM0000(BU,2),THEAD"),
    ("004601.00", "000000.24 1F",
     "line 35  LX,TCTWDX,0.0($15)"),
    ("004601.40", "004604.23 40",
     "line 36  BZXF,TPICA"),
    ("004602.00", "004455.02 80  004604.34 0A",
     "line 37  BBN,TNGATE,TPICA"),
    ("004603.00", "003313.04 10",
     "line 38  LX,TXA,TPPURF"),
    ("004603.40", "004461.50 00",
     "line 39  B,TP6"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.79 ")
finish(fails)
