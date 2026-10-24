"""MCP INITIALIZATION, printed p.58 -- THE DISPATCHER'S TWO RETURNS.

Thirty-two compiled rows (lines 5-6 and 12-41), checked bit-exactly
against the listing.  decks/mcp_bootstrap_p58.strap carries the
derivations; this file carries the rows and what the injections did.

>>> THE PAGE THE BOOT RUN STOPPED AT. <<<  Until 2026-10-24 the run
ended by branching into zeroed storage at 003237.40 -- printed p.54's
"L NORM  SYN,(8)3237.40", a stand-in for an untranscribed page.  Line
5 here IS that symbol, and mcp_image.py's merge turns it, and
L ERROR, from stand-ins into checked definitions.

SIXTEEN STAND-INS FROM pp.51-54 ARE RE-DERIVED FROM THIS PAGE'S OWN
BINARY and all sixteen agree -- see the deck's header for the row
each came out of.  The sharpest is L XNT: line 23's "SC,L XNT,L XNT"
pins it TWICE in one row, once as the address (000031 = word 0o31 =
16+9) and once as the J field (".23" -> 1001).

MEASURED INJECTIONS -- the observed sets, run through tests/inject.py.

  L SAVE (8)2602.0 -> (8)2603.0 -- 2 FAIL, lines 13 and 36.  The save
  and the restore of one index, at the same address, so the pair
  moves together and neither can be a misreading of the other.
  T LPPEN loses its (BU,1) -- 2 FAIL, lines 31 and 35, each reading
  000000 for 001000 in the SECOND group: the field LENGTH.  THIS IS
  THE INJECTION THAT MATTERS, because it is the finding.  printed
  p.53 writes T LPPEN only as "CM1111(BU,1),T LPPEN(L XPP)", so its
  dds never had to exist; p.58 lines 31 and 35 write the operation
  BARE, and a bare VFL statement takes its operand symbol's dds
  (C22-6531 printed p.31: "data properties (dds) associated with Y
  ... are transferred to A").  With no dds on the SYN the length came
  out zero.  p.53's deck was given the same (BU,1) so the two SYNs
  stay identical for mcp_image.merge, and p.53 is still 1-for-1.
  T LAST 0.18 -> 0.17 -- 1 FAIL, line 20, reading 000000.21 for
  000000.22.  Used once.
  L IODX $3 -> $2 -- 2 FAIL, lines 5 and 39, the page's two
  SWAPIs, each reading 000022 for 000023.  A stand-in from printed
  p.52 that this page re-derives.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p58.strap").read())

SYMBOLS = {
    # >>> printed p.54's TWO STAND-INS, placed here from this page's
    # own location counter.
    "LNORM":  "003237.40",
    "LERROR": "003241.00",
    # Labels this page defines and uses itself.
    "LERRA":  "003245.40",
    "LERR3":  "003247.40",
    "LERR1":  "003251.00",
    "LERR2":  "003253.00",
    "LERR4":  "003262.40",
}

ROWS = [
    ("003237.40", "002571.00 80  000023.20 E0",
     "line 5   L NORM  SWAPI,8,L TY,L IODX  -SWAP 8 INDICES."),
    ("003240.40", "000002.10 0F",
     "line 6   B,2.0($15)  -DISPATCHER NORMAL RETURN."),
    ("003241.00", "002601.51 80  001000.36 F0",
     "line 12  L ERROR  CM1111(BU,1),L FINB,0.0  -SET FINAL BIT TO 1."),
    ("003242.00", "002602.23 10",
     "line 13  SX,L XNT,L SAVE  -SAVE INDEX."),
    ("003242.40", "000000.24 14",
     "line 14  LX,L WORKX,0.0(L XPP)"),
    ("003243.00", "003253.31 46",
     "line 15  BXVZZ,L ERR2"),
    ("003243.40", "000000.34 84  010027.20 50",
     "line 16  L,T UNCT(L XPP),46"),
    ("003244.40", "003253.34 C6",
     "line 17  BRZZ,L ERR2"),
    ("003245.00", "000011.24 50",
     "line 18  LC,L WORKX,$R"),
    ("003245.40", "000000.22 1A",
     "line 19  L ERRA  LX,L XNT,0.0(L WORKX)"),
    ("003246.00", "000000.22 8A  003247.74 00",
     "line 20  BZB,T LAST(L WORKX),L ERR3  -END OF IOREQ TABLE"),
    ("003247.00", "003373.25 01",
     "line 21  LVI,L WORKX,T IOREQ"),
    ("003247.40", "003251.30 46",
     "line 22  L ERR3  BXCZZ,L ERR1"),
    ("003250.00", "000031.23 50",
     "line 23  SC,L XNT,L XNT"),
    ("003250.40", "000000.22 09",
     "line 24  Z,0.0(L XNT)  -ZERO FREEL SLOT."),
    ("003251.00", "000000.22 0A",
     "line 25  L ERR1  Z,0.0(L WORKX)  -ZERO IOREQ SLOT."),
    ("003251.40", "003245.65 48",
     "line 26  CB+,L WORKX,L ERRA  -BACK ON NON-ZERO COUNT."),
    ("003252.00", "002603.12 10",
     "line 27  LX,L XIO,L SAVEY  -RESET THE IOREQ INDEX"),
    ("003252.40", "002604.14 10",
     "line 28  LX,L XFR,L SAVEZ  -RELOAD THE FREEL TABLE INDEX"),
    ("003253.00", "000000.22 04",
     "line 29  L ERR2  Z,0.0(L XPP)  -ZERO PPREF SLOT."),
    ("003253.40", "000000.45 84  001000.36 F0",
     "line 30  CM1111(BU,1),T RJECT(L XPP)  -SET THE REJECT BIT"),
    ("003254.40", "000000.47 84  001000.00 F0",
     "line 31  CM0000,T LPPEN(L XPP)  -RESET THIS LPPEN BIT"),
    ("003255.40", "000011.37 50",
     "line 32  SC,15,$R  -ERROR FLAG TO ACC"),
    ("003256.00", "002613.11 10",
     "line 33  SX,L XPP,LASTPP  -SAVE ADR. OF LAST PP ENTERED"),
    ("003256.40", "000002.11 07",
     "line 34  V+ICR,L XPP,2.0  -STEP PPREF INDEX."),
    ("003257.00", "000000.47 84  001000.36 F0",
     "line 35  CM1111,T LPPEN(L XPP)  -SET THE NEXT LPPEN BIT"),
    ("003260.00", "002602.22 10",
     "line 36  LX,L XNT,L SAVE  -RESTORE INDEX."),
    ("003260.40", "002601.62 80  003262.74 04",
     "line 37  BZBZ,L OVBIT,L ERR4  -IF OVERLAP MODE"),
    ("003261.40", "002720.00 80  000024.06 E0",
     "line 38  SWAPI,3,L NOSAV,L XPP  -RESET INDEXES TO OVERLAP MODE"),
    ("003262.40", "002571.00 80  000023.20 E0",
     "line 39  L ERR4  SWAPI,8,L TY,L IODX  -SWAP 8 INDEXES"),
    ("003263.40", "000001.37 5F",
     "line 40  SC,$15,1.0($15)  -SAVE THE ERROR FLAG"),
    ("003264.00", "000001.50 0F",
     "line 41  B,1.32($15)  -DISPATCHER ERROR RETURN."),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.58 ")
finish(fails)
