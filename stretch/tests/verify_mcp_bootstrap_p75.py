"""MCP INITIALIZATION, printed p.75 -- THE REJECT PATH, AND THE
DISPATCH TABLE THE ASSIGN ROUTINE RETURNS THROUGH.

FIFTY-THREE lines, not fifty-six -- the first short page in this run
-- of which fifty compile, with no boxed heading at all.
decks/mcp_bootstrap_p75.strap carries the derivations.

>>> IT IS WHERE THE BOOT RUN NOW STOPS. <<<  printed p.74 line 55 is
T AREJX, whose two half words run and fall through to 004361.00 --
this page's line 1, "T AREJ R,T IXA  -RELOAD IX".

>>> NINE OF ITS LABELS WERE ALREADY IN THE IMAGE, AND ALL NINE
AGREE. <<<  T AREJ, T D, T F, T H, T I, T K, T M, T N and T P have
been carried as stand-ins by printed pp.66-74, and every one lands on
the address its stand-in gives.  T M and T N are the pair that made
this page worth doing first: p.72 line 31's "BZB,T UNASG(T IXF),T M"
and p.73 line 32's "BZB,T UNASG(T IXG),T N" are the same test on
different index registers, and the two targets are the two halves of
ONE WORD, 004422.

>>> FIVE DELIBERATE HALTS IN TEN LINES. <<<  Lines 44-53 are a
dispatch table of ten exits and nothing else, and T H, T I, T M, T N
and T P are all "BD,$" -- branch disabled to its own address.  This
project had transcribed THREE halts in the whole corpus (printed p.6
line 1, printed p.52 line 55, printed p.74 line 39); this page adds
five, each commented with the impossible condition it stands for, and
four of the five are "the assign bit is already on" -- a state ASSIGN
believes it has just ruled out.

A SEVENTH WRITTEN MINUS: line 7's "-(BU,18),T CHSXW,46" compiles
022027.30 10, after printed p.18 line 35 and printed pp.69, 70, 72
and 74.

>>> AND THE STRONGEST 13d ROW YET: FOUR OF SIX ZEROS OPEN. <<<  Line
30 is "V+I,T X1,0.0" and its octal field prints at 1800 dpi as
C 0 0 C C C 0 -- six digits of a field that IS zero, four of which
dropped their left stroke.  Octal has no C (listing_typography.md
13e) so all six are zeros, and the byte's leading glyph has the same
open shape in the same row, so it is 05 and not C5 -- which printed
p.73 line 45's V+I (000000.45 05) says independently.

THE DECK HAD TWO ROWS WRONG FIRST, out of fifty: that byte, and
T P1BA's stand-in, read .40 where the branch's own bit 18 says .00.
A STAND-IN DERIVED FROM A BRANCH MUST USE THE BRANCH'S BIT 18.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.
The mutated file is the DECK, not the assembler.

  Line 30's V+I becomes V-I -- 1 FAIL at 004407.00, reading
  000000.25 0D for 05.  THAT IS THE BYTE THE DECK FIRST READ AS C5,
  and the injection shows what a real non-zero high nibble looks
  like in that position.
  T P1BA's stand-in takes the .40 the deck first read -- 1 FAIL at
  004414.00, reading 004622.74 for 004622.34.  Bit 18 of the
  BRANCH's own second group is the evidence, and the stand-in has
  to match it.
  Line 7's written minus becomes a plus -- 1 FAIL at 004365.40,
  reading 022027.20 for 022027.30.
  T N's halt becomes T M's, one half word away -- 1 FAIL at
  004422.40, reading 004422.04 for 004422.44.  The two halts are
  ONE WORD apart and differ in exactly bit 18, which is why the
  p.72/p.73 pair that branches to them is worth the check.
  Line 8's bit offset 12 becomes 12 WORDS -- 1 FAIL at 004366.40,
  reading 005005.00 for 004771.14.  "+.12" and "+12.0" differ by
  twelve words minus twelve bits, and the printed field shows both
  halves of that.
  T FREEL's stand-in dds drops from eighteen bits to eight -- 1 FAIL
  at 004373.40, reading 010027 for 022027.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p75.strap").read())

SYMBOLS = {
    # The address printed p.74 line 55 falls through to.
    "TAREJ":  "004361.00",
    # Labels this page defines and uses itself.
    "TAREJ1": "004362.40",
    "TAREJN": "004373.40",
    "TIPL4":  "004404.00",
    "TAREJ3": "004406.40",
    "TAREJ4": "004412.00",
    "TAREJ5": "004413.40",
    # The dispatch table -- nine of these eleven were stand-ins first.
    "TD":     "004416.40",
    "TF":     "004417.00",
    "TG":     "004417.40",
    "TH":     "004420.00",
    "TI":     "004420.40",
    "TK":     "004421.00",
    "TL":     "004421.40",
    "TM":     "004422.00",
    "TN":     "004422.40",
    "TP":     "004423.00",
}

ROWS = [
    ("004361.00", "000024.02 00",
     "line 1   T AREJ  R,TIXA"),
    ("004361.40", "000000.45 83  001000.36 F0",
     "line 2   CM1111,TRJECT(TIXE)"),
    ("004362.40", "000000.56 84  022027.20 50",
     "line 3   T AREJ1  L,TABSCH(TIXA),46"),
    ("004363.40", "000011.24 30",
     "line 4   LV,TX1,$R"),
    ("004364.00", "004373.74 C2",
     "line 5   BRZ,TAREJN"),
    ("004364.40", "000000.33 8A  004406.74 00",
     "line 6   BZB,TMULTI(TX1),TAREJ3"),
    ("004365.40", "002152.00 80  022027.30 10",
     "line 7   -(BU,18),TCHSXW,46"),
    ("004366.40", "004771.14 80  007027.20 D0",
     "line 8   ST(BU,7),TCAT+.12,46"),
    ("004367.40", "000000.00 8A  022027.20 50",
     "line 9   L,TUNTBA(TX1),46"),
    ("004370.40", "000011.24 30",
     "line 10  LV,TX1,$R"),
    ("004371.00", "000000.07 84  003027.20 50",
     "line 11  L,TABSUN(TIXA),46"),
    ("004372.00", "004771.57 80  003027.20 D0",
     "line 12  ST(BU,3),TCAT+.47,46"),
    ("004373.00", "000011.24 B0",
     "line 13  V+,TX1,$R"),
    ("004373.40", "000000.34 84  022027.20 50",
     "line 14  T AREJN  L,TFREEL(TIXA),46"),
    ("004374.40", "004406.74 C2",
     "line 15  BRZ,TAREJ3"),
    ("004375.00", "000011.04 30",
     "line 16  LV,TX3,$R"),
    ("004375.40", "000000.22 02",
     "line 17  Z,0.0(TX3)"),
    ("004376.00", "000000.00 84  004406.74 00",
     "line 18  BZB,TASGNI(TIXA),TAREJ3"),
    ("004377.00", "004771.25 02",
     "line 19  LCI,TX1,TCAT"),
    ("004377.40", "000000.25 5A",
     "line 20  SC,TX1,0.0(TX1)"),
    ("004400.00", "000000.35 8A  001000.00 F0",
     "line 21  CM0000,TUNASG(TX1)"),
    ("004401.00", "000000.40 8A  001000.36 F0",
     "line 22  CM1111,TCHOWN(TX1)"),
    ("004402.00", "000000.65 8A  001000.00 F0",
     "line 23  CM0000,SIMNT(TX1)"),
    ("004403.00", "000000.63 8A  001000.00 F0",
     "line 24  CM0000,SMOUNT(TX1)"),
    ("004404.00", "001472.10 00",
     "line 25  T IPL4  B,DMCP"),
    ("004404.40", "000000.00 80",
     "line 26  ,DFREE"),
    ("004405.00", "000003.00 80",
     "line 27  ,3."),
    ("004405.40", "000000.40 8A  001000.00 F0",
     "line 28  CM0000,TCHOWN(TX1)"),
    ("004406.40", "000000.22 04",
     "line 29  T AREJ3  Z,0.0(TIXA)"),
    ("004407.00", "000000.25 05",
     "line 30  V+I,TX1,0.0"),
    ("004407.40", "004412.31 42",
     "line 31  BXVZ,TAREJ4"),
    ("004410.00", "000000.76 8A  004412.34 06",
     "line 32  BBZ,TUNRES(TX1),TAREJ4"),
    ("004411.00", "000000.77 8A  001000.00 F0",
     "line 33  CM0000,TOVRES(TX1)"),
    ("004412.00", "000001.22 84  004413.74 00",
     "line 34  T AREJ4  BZB,TLAST+1.0(TIXA),TAREJ5"),
    ("004413.00", "003372.51 01",
     "line 35  LVI,TIXA,TIOREQ-1"),
    ("004413.40", "004362.51 48",
     "line 36  T AREJ5  CB+,TIXA,TAREJ1"),
    ("004414.00", "004455.03 80  004622.34 06",
     "line 37  BBZ,YSCRBT,TP1BA"),
    ("004415.00", "000000.24 1F",
     "line 38  LX,TCTWDX,0.0($15)"),
    ("004415.40", "004203.63 40",
     "line 39  BZXF,TB8Z"),
    ("004416.00", "004421.50 00",
     "line 40  B,TL"),
    ("004416.40", "004461.10 00",
     "line 44  T D  B,TSCRIB"),
    ("004417.00", "004461.10 00",
     "line 45  T F  B,TSCRIB"),
    ("004417.40", "004461.10 00",
     "line 46  T G  B,TSCRIB"),
    ("004420.00", "004420.04 00",
     "line 47  T H  BD,$"),
    ("004420.40", "004420.44 00",
     "line 48  T I  BD,$"),
    ("004421.00", "004461.10 00",
     "line 49  T K  B,TSCRIB"),
    ("004421.40", "004604.10 00",
     "line 50  T L  B,TPICA"),
    ("004422.00", "004422.04 00",
     "line 51  T M  BD,$"),
    ("004422.40", "004422.44 00",
     "line 52  T N  BD,$"),
    ("004423.00", "004423.04 00",
     "line 53  T P  BD,$"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.75 ")
finish(fails)
