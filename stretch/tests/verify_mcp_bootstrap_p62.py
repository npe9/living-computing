"""MCP INITIALIZATION, printed p.62 -- THE ASSIGN PROGRAM'S THREE
TABLES AND THEIR SYN CARDS.

Fifty-six lines: twelve compile a word, six are DRZ reservations,
twenty-one are SYN cards.  decks/mcp_bootstrap_p62.strap carries the
derivations.

>>> THIS PAGE DECLARES WHAT FOUR EARLIER PAGES HAD TO DERIVE, AND
ELEVEN FOR ELEVEN ARE CONFIRMED. <<<  T UNCT (BU,8) 0.28, T RJECT
0.37, T LPPEN (BU,1) 0.39, T LREFN (BU,12) 0.40, T IODCT (BU,12)
0.52, T RLSYM 0.11, T LAST 0.18, T FREEL 0.28, T TYPE (BU,4) 0.03,
T IOREQ 003373.0 and T UIORQ 003514.0 were each inferred on pp.55-58
from a length field's arithmetic, an octal pair in a location, or a
row that wrote no dds at all.  Here are IBM's own cards for them, and
every value agrees.

THE (BU,1) ON T LPPEN IS THE ONE WORTH NAMING TWICE: printed p.58
lines 31 and 35 write "CM0000,T LPPEN(L XPP)" with no dds on the
statement, so the length could ONLY come from the symbol, and the
deck gave it SYN(BU,1) on that reasoning alone.  Line 14 here is that
card.

AND T FREEL AND T UNCT ARE BOTH 0.28 BECAUSE THEY ARE IN DIFFERENT
TABLES, which p.56's deck called "a coincidence worth not re-deriving
later".  T UNCT is in the PP REFERENCE TABLE's SYN block and T FREEL
in the I/O REQUEST TABLE's.  The page shows it rather than arguing
it.

THE ASSEMBLER GAINED ONE THING FOR THIS PAGE: dr_count now evaluates
its dimension against the SYMBOL TABLE.  It used to use an empty one,
so only a literal could resolve -- enough while every DR read was
"(3)" or "100".  Six rows here are "DRZ(BU,64),(T PPC)" and the like,
and line 42 is "T UIOC-1", an EXPRESSION in a symbol.

ROWS DELIBERATELY ABSENT, as printed p.24 established: a DRZ row
prints its SIZE, not a word (20, 20, 80, 19, 50, 20 -- printed p.60's
six SYN cards spent), and a SYN row prints its VALUE, checked in
SYMBOLS below.

ALL TWELVE ROWS AND ALL THIRTY-TWO SYMBOLS PASSED ON THE FIRST RUN.

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  T PPC 20 -> 21 -- 5 symbols and the line 2 XW.  p.60's one SYN card
  is spent four ways on this page (two DRZ sizes and two XW counts),
  so changing it moves T PURFT, T IOREQ, T UIORQ, T FSTRE and T UFRE
  as well as the printed count.
  T LPPEN 0.39 -> 0.38 -- 1 FAIL in SYMBOLS, bit 38 for bit 39.
  Line 21's "(.39)1" -> "(.38)1" -- 1 FAIL, reading 000200 for
  000100.  A bit further left in the count field doubles the printed
  octal, which is what makes the encoding legible.
  Line 42's "T UIOC-1" -> "T UIOC" -- 4 FAIL, and the cascade is the
  point: one extra word moves T FSTRE and T UFRE, AND changes line
  43's VF from 000000.40+ to 000000.00+ and line 47's CNOP from
  000000.30 00 to 000000.00 00, because the CNOP no longer has to
  pad.  The "-1" is load-bearing in four places.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p62.strap").read())

_XW0 = "000000.00+ 000 000000 000000"

SYMBOLS = {
    # The words this page defines.  T PREFT and T PPREF are the two
    # printed p.61 line 19's single XW predicted, to the bit.
    "TPPURF": "003313.00",
    "TPPREF": "003314.00",
    "TPPRUN": "003315.00",
    "TPREFT": "003317.00",
    "TPURFT": "003370.00",
    "TIOREQ": "003373.00",
    "TUIORQ": "003514.00",
    "TFSTRE": "003541.00",
    "TUFRE":  "003623.00",
    # >>> THE PP REFERENCE TABLE's SYN CARDS (lines 9-17). <<<
    "TCRREF": "000000.00",
    "TUNCT":  "000000.34",   # 0.28 = 0o34  -- pp.54 and 58 derived it
    "TJBPRO": "000000.44",   # 0.36
    "TRJECT": "000000.45",   # 0.37         -- p.58 derived it
    "TASGNP": "000000.46",   # 0.38
    "TLPPEN": "000000.47",   # 0.39         -- p.58 FORCED its (BU,1)
    "TLREFN": "000000.50",   # 0.40         -- p.56 derived (BU,12)
    "TIODCT": "000000.64",   # 0.52         -- p.56 derived (BU,12)
    "TPNAME": "000001.00",
    # >>> THE I/O REQUEST TABLE's SYN CARDS (lines 30-39). <<<
    "TASGNI": "000000.00",
    "TUNOBT": "000000.01",
    "TPRINT": "000000.02",
    "TTYPE":  "000000.03",   # p.54 derived 0.3, p.55 line 5 the width
    "TABSUN": "000000.07",
    "TRLSYM": "000000.13",   # 0.11         -- p.55 derived it
    "TLAST":  "000000.22",   # 0.18         -- pp.57 and 58 derived it
    "TIODSQ": "000000.23",   # 0.19
    "TFREEL": "000000.34",   # 0.28         -- p.56 derived it
    "TABSCH": "000000.56",   # 0.46
    # The first reel table and the channel status table.
    "TREELN": "000000.00",
    "TCHSXW": "002152.00",
}

ROWS = [
    ("003313.00", "003370.00+ 000 000002 003313",
     "line 2   T PPURF XW,T PURFT,T UPPC,$  -CONSTANT IX FOR THE NOT OVERLAP TBL"),
    ("003314.00", "003317.00+ 000 000024 003314",
     "line 3   T PPREF XW,T PREFT,T PPC,$  -CONSTANT IX FOR THE PP REF TBL"),
    ("003315.00", "003317.00+ 000 000024 003314",
     "line 4   T PPRUN XW,T PREFT,T PPC,T PPREF  -THE NEXT JOB TO BE RUN POINTER"),
    ("003316.00", _XW0,
     "line 5   XW  -A BLANK WORD MUST PRECEED THE PP REF"),
    ("003317.00", "003373.00+ 000 001100 000000",
     "line 6   T PREFT XW,T IOREQ,0,(.39)9  -INITIAL ENTRY WITHIN THE PP REF TBL"),
    ("003370.00", _XW0,
     "line 19  T PURFT XW,0  -NOT OVERLAP PP REF WORD NO. 1"),
    ("003371.00", _XW0,
     "line 20  XW,0  -NOT OVERLAP PP REF WD NO. 2"),
    ("003372.00", "000000.00+ 000 000100 000000",
     "line 21  XW,0(.39)1  -NECESSARY FOR LAST ENTRY BIT"),
    ("003513.00", "000000.40+",
     "line 29  VF,0.32  -DO NOT REMOVE - MARKS LAST WORD"),
    ("003514.00", _XW0,
     "line 41  T UIORQ XW,0  -THE NOT OVERLAP I/O REQ TBL"),
    ("003540.00", "000000.40+",
     "line 43  VF,0.32  -DO NOT REMOVE - MARKS LAST WORD"),
    ("003540.40", "000000.30 00",
     "line 47  CNOP  (the one that had to PAD)"),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.62 ")
finish(fails)
