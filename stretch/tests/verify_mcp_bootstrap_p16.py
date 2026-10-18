#!/usr/bin/env python3
"""verify_mcp_bootstrap_p16.py -- MCP INITIALIZATION, printed page 16,
"WRITE PROSA ON DISK AND FETCH FROM MCPS TAPE"
(../decks/mcp_bootstrap_p16.strap).  docs/MCP_Mar63_001-249.pdf PDF
p.23, header "PAGE NUMBER 16".  AGENTS.md rule 3.

Thirty-one printed rows, every one of them with binary output -- this
is the densest MCP page transcribed so far and the first with no
message text on it at all.

THE TWO ROWS WORTH NAMING, because they exercise encoders that the
diagnostic decks reach less often:

  line 29  "M+(BU,9),S DK MCP+9,18+9"  002157.11 80 011015.60 90
      A VFL ADD TO MEMORY with a nine-bit unsigned field, a bit
      address nine bits into a word, and an OFFSET written as the
      expression 18+9.  Both half-words have to come out right for
      this to pass, and the second is pure descriptor -- byte size,
      length, mode, offset, opcode -- with no address in it.

  line 30  "BB,$0+.25,X11 3"           000020.31 80 000653.34 02
      BRANCH ON BIT against bit 25 of index register 0, which lives
      at word 16: 0o20 = 16 and 0o31 = 25, so the printed bit address
      is the register file's, not the program's.

FOUR EXTERNALS COME FROM PAGES READ MONTHS APART and all four are
used as branch targets here, so a wrong one would print a wrong
address: X9 A (printed p.4) and X9 A 3A (p.4) on lines 31-32, X7 1
and X7 3 (p.3) on lines 36-37.  Two more, X PRO WR and S DK MCP, are
read off this page's own output and are marked as such in the deck
and in ROWS below.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p16.strap").read())

SYMBOLS = {
    "X11":    "000633.00",
    "X111":   "000636.40",
    "XERR14": "000637.40",
    "XERR15": "000640.40",
    "XERR16": "000641.40",
    "X11CCW": "000643.40",
    "XER16A": "000644.40",
    "XER16B": "000645.40",
    "X112":   "000647.00",
    "X113":   "000653.00",
}

ROWS = [
    # ---- how many words to write ----
    ("000633.00", "000041.14 30",
     "line 5   X11  LV,$6,X IPL BS  -GET FWA OF LAST READ(BIASED BY UR BIT)"),
    ("000633.40", "011406.15 0D",
     "line 6   V-I,$6,X BUFER  -COMPUTE NUMBER OF PROSA WORDS TO BE WRITTEN"),
    ("000634.00", "000026.14 50", "line 8   LC,$6,$6"),
    ("000634.40", "000653.30 42", "line 9   BXCZ,X 11 3"),
    ("000635.00", "011406.15 01", "line 10  LVI,$6,X BUFER"),
    # X PRO WR's value was READ OFF THIS ROW and line 13 -- see the deck.
    ("000635.40", "001746.15 10", "line 11  SX,$6,X PRO WR  -ASSEMBLED CW"),
    ("000636.00", "000000.16 50",
     "line 12  LC,$7,0.0  -SET UP FOR TEST OF LOCATE"),
    # ---- write PROSA and test it ----
    ("000636.40", "000000.00 80 001746.13 00",
     "line 13  X11 1  W(SEOP),0.0,X PRO WR  -WRITE PROSA"),
    ("000637.40", "000551.00 80", "line 14  X ERR 14  SIC,X ERR AD"),
    ("000640.00", "000133.03 46", "line 15  BEKJZ,X ERROR  -IF EKJ"),
    ("000640.40", "000551.00 80", "line 16  X ERR 15  SIC,X ERR AD"),
    ("000641.00", "000133.03 C6", "line 17  BUNRJZ,X ERROR  -IF UNRJ"),
    ("000641.40", "000551.00 80", "line 18  X ERR 16  SIC,X ERR AD"),
    ("000642.00", "000133.16 4A",
     "line 19  CBZ,$7,X ERROR  -IF LOCATE NOT SUCCESSFUL"),
    ("000642.40", "000636.44 46", "line 20  BCBJZ,X11 1  -IF LOCATE DONE"),
    ("000643.00", "000000.16 50",
     "line 21  LC,$7,0.0  -DONE * SET UP FOR TEST OF WRITE"),
    ("000643.40", "000000.00 80 000042.21 00",
     "line 22  X11 CCW  CCW,0.0,X IPL BS+1.0  -ATTEMPT TO GET CW"),
    ("000644.40", "000551.00 80", "line 23  X ER 16A  SIC,X ERR AD"),
    ("000645.00", "000133.03 46", "line 24  BEKJZ,X ERROR  -IF EKJ"),
    ("000645.40", "000551.00 80", "line 25  X ER 16B  SIC,X ERR AD"),
    ("000646.00", "000133.16 4A",
     "line 26  CBZ,$7,X ERROR  -IF WRITE NOT SUCCESSFUL"),
    ("000646.40", "000643.44 46", "line 27  BCBJZ,X11 CCW  -IF WRITE DONE"),
    # ---- count the arcs ----
    ("000647.00", "000011.15 10",
     "line 28  X11 2  SX,$6,$R  -ENTER NUMBER OF ARCS JUST WRITTEN"),
    # S DK MCP's value was READ OFF THIS ROW -- see the deck.
    ("000647.40", "002157.11 80 011015.60 90",
     "line 29  M+(BU,9),S DK MCP+9,18+9  -ACCUMULATE NUMBER OF ARCS"),
    ("000650.40", "000020.31 80 000653.34 02",
     "line 30  BB,$0+.25,X11 3  -PROSA REFRESHED YES* OUT"),
    ("000651.40", "000114.40 80", "line 31  SIC,X9 A 3A"),
    ("000652.00", "000104.10 00", "line 32  B,X9 A  -TO FETCH PROSA"),
    ("000652.40", "000633.10 00", "line 33  B,X11"),
    # ---- rewind and unload the MCPS tape ----
    ("000653.00", "000000.00 8F 000137.15 00",
     "line 35  X11 3  CTL(SEOP),0.0($15),(8)137  -REWIND AND UNLOAD "
     "MCPS TAPE"),
    ("000654.00", "000066.40 80", "line 36  SIC,X7 3"),
    ("000654.40", "000057.50 00", "line 37  B,X7 1  -IO TEST"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.16 "))
