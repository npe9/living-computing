#!/usr/bin/env python3
"""verify_mcpref_example2_listing.py -- C22-6678-1 printed p.48,
"PROGRAMMING EXAMPLE 2: CARD-TO-TAPE ROUTINE" (../decks/
mcpref_example2.strap), against the machine code STRAP II printed
beside it (VERSION 03/15/64).  Read in the ink at 220 dpi.

WHY THIS PAGE.  It is genuine STRAP II output for a PROBLEM PROGRAM
run under MCP.  It pins three things no other source here does:
  1. the assembled value of every MCP pseudo-operation it uses, from
     STRAP II's own system-symbol table: $MCP 40.0, $SCR 104.40,
     $WAIT 13.40, $WS 1.41, $WEFS 7.41, $EOJ 101.0, $ABEOJ 104.0,
     $RET 41.0, $BSPS 6.01, $ERGS 5.01, $W 1.40, $UNLDS 10.41,
     $IODEF 15.0, $COMM 43.40 (all octal W.B);
  2. the calling-sequence parameter half-word ",X", which assembles
     to X's address with 80 in bits 24-31;
  3. the listing layout a reconstructed STRAP II must print
     (docs/reconstruction_plan.md S-1; the deck header lists it).

WHAT IT FOUND.  $WEFS, $BSPS and $UNLDS were not in the scaffolding
assembler's table, which held only the codes the March 1963 MCP listing
prints.  They are now in strap/opcodes.py's MCP_PSEUDO_OPS_1964, which
is C22-6678-1 Appendix A (printed p.42) entire, read in the ink.  That
table is kept beside the 1963 one rather than merged into it.  This
page's values agree with both tables wherever a table has the name.

ONE ROW IS A RECORDED DISAGREEMENT: line 5's LVE (see the note at the
end of this file).

NOT CHECKED: the DR(N) size lines (000017.00 at 56.00 and 75.00,
000002.00 at 114.00, 000001.00 at 142.00) and END's 000041.00, because
they print a size or a transfer address, not memory.  The SYMBOLS
check covers the reservations instead: BUF2 - BUF1 = 15 words, and so
on.  The (IQS*) message prints no code.

PROVEN DISCRIMINATING.  The injections and their observed failure sets
are in tests/run_tests.sh beside this test's entry.
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap_asm import assemble                              # noqa: E402
from listing_oracle import check_rows, finish               # noqa: E402

prog = assemble(open(os.path.join(HERE, "..", "decks",
                                  "mcpref_example2.strap")).read())

ROWS = [
    ('000041.00', '000040.10 00', '3 START B,$MCP'),
    ('000041.40', '000104.40 80', '4 ,$SCR'),
    ('000042.40', '000001.00 80', '6 ,1.0'),
    ('000043.00', '000000.00 80', '7 ,0'),
    ('000043.40', '000051.10 00', '8 B,EOJ'),
    ('000044.00', '000040.10 00', '9 B,$MCP'),
    ('000044.40', '000013.40 80', '10 ,$WAIT'),
    ('000045.00', '000001.00 80', '11 ,RON'),
    ('000045.40', '000054.00 80 000055.02 E0', '12 SWAPI,1,CW,CW+1.0'),
    ('000046.40', '000040.10 00', '13 B,$MCP'),
    ('000047.00', '000001.41 80', '14 ,$WS'),
    ('000047.40', '000001.00 80', '15 ,RON'),
    ('000050.00', '000054.00 80', '16 ,CW'),
    ('000050.40', '000041.10 00', '17 B,START'),
    ('000051.00', '000040.10 00', '18 EOJ B,$MCP'),
    ('000051.40', '000007.41 80', '19 ,$WEFS'),
    ('000052.00', '000001.00 80', '20 ,RON'),
    ('000052.40', '000040.10 00', '21 B,$MCP'),
    ('000053.00', '000101.00 80', '22 ,$EOJ'),
    ('000054.00', '000056.00+ 000 000017 000000', '23 CW CW,BUF1,15'),
    ('000055.00', '000075.00+ 000 000017 000000', '24 CW,BUF2,15'),
    ('000116.00', '000122.10 00', '28 B,UK'),
    ('000116.40', '000000.30 00', '29 NOP'),
    ('000117.00', '000040.10 00', '30 B,$MCP'),
    ('000117.40', '000101.00 80', '31 ,$EOJ'),
    ('000120.00', '000040.10 00', '32 B,$MCP'),
    ('000120.40', '000104.00 80', '33 ,$ABEOJ'),
    ('000121.00', '000040.10 00', '34 B,$MCP'),
    ('000121.40', '000041.00 80', '35 ,$RET'),
    ('000122.00', '000115.11 80 000131.34 02', '36 UK BB,EXIT+1.09,EPGK'),
    ('000123.00', '000040.10 00', '37 B,$MCP'),
    ('000123.40', '000006.01 80', '38 ,$BSPS'),
    ('000124.00', '000001.00 80', '39 ,RON'),
    ('000124.40', '000040.10 00', '40 B,$MCP'),
    ('000125.00', '000005.01 80', '41 ,$ERGS'),
    ('000125.40', '000040.10 00', '42 B,$MCP'),
    ('000126.00', '000001.40 80', '43 ,$W'),
    ('000126.40', '000001.00 80', '44 ,RON'),
    ('000127.00', '000054.00 80', 'p2 1 ,CW'),
    ('000127.40', '000040.10 00', 'p2 2 B,$MCP'),
    ('000130.00', '000013.40 80', 'p2 3 ,$WAIT'),
    ('000130.40', '000001.00 80', 'p2 4 ,RON'),
    ('000131.00', '000040.10 00', 'p2 5 EPGK B,$MCP'),
    ('000131.40', '000010.41 80', 'p2 6 ,$UNLDS'),
    ('000132.00', '000001.00 80', 'p2 7 ,RON'),
    ('000132.40', '000040.10 00', 'p2 8 B,$MCP'),
    ('000133.00', '000015.00 80', 'p2 9 ,$IODEF'),
    ('000133.40', '000001.00 80', 'p2 10 ,RON'),
    ('000134.00', '000142.00 80', 'p2 11 ,MESG'),
    ('000134.40', '000040.10 00', 'p2 12 B,$MCP'),
    ('000135.00', '000043.40 80', 'p2 13 ,$COMM'),
    ('000135.40', '000142.00 80', 'p2 14 ,MESG'),
    ('000136.00', '000003.00 80', 'p2 15 ,3.0'),
    ('000136.40', '000040.10 00', 'p2 16 B,$MCP'),
    ('000137.00', '000001.40 80', 'p2 17 ,$W'),
    ('000137.40', '000001.00 80', 'p2 18 ,RON'),
    ('000140.00', '000054.00 80', 'p2 19 ,CW'),
    ('000140.40', '000040.10 00', 'p2 20 B,$MCP'),
    ('000141.00', '000013.40 80', 'p2 21 ,$WAIT'),
    ('000141.40', '000001.00 80', 'p2 22 ,RON'),
]

SYMBOLS = {'START': '000041.00', 'EOJ': '000051.00', 'CW': '000054.00',
           'BUF1': '000056.00', 'BUF2': '000075.00', 'EXIT': '000114.00',
           'UK': '000122.00', 'EPGK': '000131.00', 'MESG': '000142.00'}

fails = check_rows(prog, ROWS, SYMBOLS, label='p.48 ')

# >>> ONE ROW DISAGREES, AND IT IS PINNED RATHER THAN HIDDEN. <<<
# Line 5, "LVE,,CW+1.0", prints 000055.01 80: bits 23-27 = 11000.  The
# pocket card (X22-6533, DIRECT INDEX ARITHMETIC) gives LVE as 11011,
# and MCP's own March 1963 listing prints "LVE,,AMR" as 224032.01 B0
# (strap_asm.py, eval_reg's note), which is 11011 too.  No direct index
# op is 11000.  This LVE is never executed: it is the third half-word
# of a $SCR calling sequence (B,$MCP / ,$SCR / LVE,,CW+1.0 / ,1.0 / ,0),
# which MCP reads as data.  So the 1964 assembler may treat it specially,
# or the page may be wrong.  UNEXPLAINED.  The scaffolding assembler is
# NOT changed on one print.  This check fails if either side moves.
from listing_oracle import render                             # noqa: E402
got = render(prog, '000042.00', '000055.01 80')
ok = got == '000055.01 B0'
fails += not ok
print(f"{'PASS' if ok else 'FAIL'} p.48 000042.00 5 LVE,,CW+1.0: "
      f"assembled {got!r}, pinned as 'B0' (page prints '80'; see above)")
finish(fails)
