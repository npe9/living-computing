"""MCP INITIALIZATION, printed p.63 -- THE CHANNEL/UNIT STATUS
TABLE'S SYN CARDS, AND THE VALID CHECK TABLE.

Twenty-nine lines and only FOUR compile a word.  The other
twenty-five are comments and SYN cards, which makes this the
smallest page of the ASSIGN program and the densest in symbols.
decks/mcp_bootstrap_p63.strap carries the derivations.

INTEGER SYNs PRINT "NULL" -- lines 24, 25 and 26 do, exactly as
printed p.60's six table-length cards do, while lines 27-29 are SYNs
WITH a dds and print "BU,10 ,10".  One page, both forms, three rows
apart.

AND THE THREE NULL CARDS ARE SPENT IMMEDIATELY ABOVE THEM: line 21
is "T COMBO VF,T TYBC+T MACBC+T REQBC" compiling 000000.30+ (0o30 =
24 = 8+8+8) and line 22 is "T 2COMB VF,T TYBC+T MACBC" compiling
000000.20+ (16).  A SYN that compiles nothing, checked by the rows
that add it up.

LINE 20's XW FIXES A SYMBOL ON THE NEXT PAGE, as printed p.61 line
19 did for p.62: "T TYARA XW,T DISK,8,T TYARA" gives T DISK =
003652.0, and printed p.64 line 6 stands there.

ALL FOUR ROWS AND ALL TWENTY-THREE SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T DISK (8)3652.0 -> (8)3653.0 -- 1 FAIL, line 20's XW value.  That
  symbol is fixed by printed p.64 line 6's own address.
  T TYBC 0.8 -> 0.9 -- 3 FAIL: the symbol itself, and BOTH rows that
  add it up (line 21 reading 000000.31+ for 000000.30+, line 22
  000000.21+ for 000000.20+).  A card that compiles NULL, caught by
  the arithmetic of the two rows that spend it.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p63.strap").read())

SYMBOLS = {
    # The four words.
    "TTYARA": "003647.00",
    "TCOMBO": "003650.00",
    "T2COMB": "003650.40",
    "TVALVF": "003651.00",
    # >>> THE CHANNEL/UNIT STATUS TABLE's thirteen cards.  The
    # location column prints the resolved value in OCTAL, so each is
    # the octal of the decimal bit offset.
    "TUNTBA": "000000.00",   # 0.0
    "TMULTI": "000000.33",   # 0.27
    "TCHAVL": "000000.31",   # 0.25
    "TFDISP": "000000.33",   # 0.27 -- shares a bit with T MULTI
    "TUNAVL": "000000.34",   # 0.28
    "TUNASG": "000000.35",   # 0.29
    "TCHOWN": "000000.40",   # 0.32
    "TSEL":   "000000.47",   # 0.39
    "TVER":   "000000.50",   # 0.40
    "TEQUIP": "000000.64",   # 0.52
    "TUNITK": "000000.73",   # 0.59
    "TUNRES": "000000.76",   # 0.62
    "TOVRES": "000000.77",   # 0.63
    # >>> THE VALID CHECK TABLE's six.  The first three print NULL
    # in the binary column; their VALUE is what is checked here.
    "TTYBC":  "000000.10",   # 0.8
    "TMACBC": "000000.10",   # 0.8
    "TREQBC": "000000.10",   # 0.8
    "TTYAD":  "000000.00",   # 0.0
    "TMCAD":  "000000.10",   # T TYAD+0.8
    "TRCAD":  "000000.20",   # T MCAD+0.8 -- 0.16, and 0o20 is 16
}

ROWS = [
    ("003647.00", "003652.00+ 000 000010 003647",
     "line 20  T TYARA XW,T DISK,8,T TYARA  -THE TYPE CODE"),
    ("003650.00", "000000.30+",
     "line 21  T COMBO VF,T TYBC+T MACBC+T REQBC  -BY PASS ONE WORD"),
    ("003650.40", "000000.20+",
     "line 22  T 2COMB VF,T TYBC+T MACBC  -FOR COMPUTING THE NUMBER OF UNITS"),
    ("003651.00", "000000.00+",
     "line 23  T VALVF VF,0.0  -TO PREVENT A DOUBLE VALIDITY CHECK"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.63 ")
finish(fails)
