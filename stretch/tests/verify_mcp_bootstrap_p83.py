#!/usr/bin/env python3
"""printed p.83 against its own listing.

The MOVE routine's constants, the index-register names, and the SAVE
AND RESTORE AREA FOR INDEXES.  docs/MCP_Mar63_001-249.pdf PDF p.90.

WHAT THIS PAGE IS WORTH CHECKING FOR, beyond the page itself:

  * THE X-REGISTER WORD MAPPING, from the listing's own column.
    "T MX1 SYN,$1" prints 000021.00 and 0o21 = 17, which is X1; X0-X15
    occupy words 16-31.  "T MLXA SYN,$12" prints 000034.00 = word 28.
    The page confirms the mapping without reference to the model.

  * THE CHAINED SYN.  Line 32 is "T MXH SYN,T MX1" -- a SYN whose
    target is itself a SYN of $1 -- and it prints 000021.00, TMX1's own
    word.  strap_asm.py recorded sys_alias only ONE level deep until
    2026-10-30, which made "LX,TIXF,TCHSXW" on printed p.72 assemble
    with j=0 and cost the boot sixteen million steps.
    tests/verify_syn_chain_reg.py pins the fix with its own injection;
    this is the printed page that needs it.

  * S MAXUB at 002153.00, recovered from line 17's own value, agrees
    with printed pp.28 and 40 and with p.98 line 33's
    "S MAXUB SYN,S BA MCP".
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p83.strap").read())

SYMBOLS = {
    "TMMAX":  "004630.00",
    "TMIOD":  "004630.14",
    "TMREEL": "004630.44",
    "TLBL":   "004630.74",
    "TNCP":   "004631.02",
    "TM6BL":  "004631.10",
    "TERFLG": "004632.00",
    "TLIMB":  "002155.00",
    "TSYRFT": "002157.40",
    "TBAMCP": "002153.00",
    "TMAXRF": "002155.40",
    "TMARK":  "002162.40",
    "TMX1":   "000021.00",
    "TMXA":   "000022.00",
    "TMXB":   "000023.00",
    "TMXC":   "000024.00",
    "TMXD":   "000025.00",
    "TMXE":   "000026.00",
    "TMXF":   "000027.00",
    "TMXG":   "000030.00",
    "TMXEE":  "000031.00",
    "TMXI":   "000032.00",
    "TMXGA":  "000033.00",
    "TMXH":   "000021.00",
    "TMLXA":  "000034.00",
    "TSIOXW": "004633.00",
    "TDKSAV": "004652.00",
}

ROWS = [
    ("004627.40", "000000.30 00", "line 7   CNOP"),
    ("004632.00", "000000.00+",   "line 14  T ERFLG  VF,0"),
    ("004632.40", "000000.30 00", "line 39  CNOP"),
    # >>> LINE 40'S DRZ IS NOT A BINARY-OUTPUT ROW. <<<  The listing
    # prints 000017.00 beside it and 0o17 = 15, which is the
    # RESERVATION'S COUNT, not the word stored at 004633.00 -- that
    # word is zero, because a DRZ reserves zeros.  Checking it as a
    # row compares the count against the content and fails for a
    # reason that says nothing.  printed p.84 line 5 prints 000062.00
    # for DRZ(BU,64),(50) and 0o62 = 50, the same convention twice.
    # The symbol check above still pins where the reservation STARTS,
    # and the next page's first address pins where it ends.
    ("004652.00", "000000.00+",   "line 42  T DKSAV  VF,0"),
]

finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.83 "))
