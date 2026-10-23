#!/usr/bin/env python3
"""verify_mcp_bootstrap_p48.py -- RESERVATIONS, TABLES AND COUNTERS,
the DECODE program's storage, printed page 48
(../decks/mcp_bootstrap_p48.strap).
docs/MCP_Mar63_001-249.pdf PDF p.55, header "PAGE NUMBER 48".
AGENTS.md rule 3.

Twenty-three printed rows with binary output and thirty-one symbol
locations.

>>> PRINTED p.47 COMPILES NOTHING, so this page follows printed p.46
directly. <<<

p.47 is twenty-three lines and the only one that is not a comment is
line 1's "SLC,$" at 002556.67 -- where printed p.46's Q BLNK ends, to
the bit.  The rest is THE DECODE PROGRAM LINKAGE FORMAT written out as
a worked call, and it is recorded in docs/boot_plan.md; there is no
deck for it because there is nothing to compile and nothing to check.

>>> THE BIT CHAIN AT THE END IS A SECOND WITNESS FOR VF = 25 BITS. <<<

Line 44 is "L NO6  VF,.06" at 002601.00 and line 45 is at 002601.31 --
BIT 25.  printed p.46 lines 29-30 forced that correction (C22-6531
printed p.18, "THE LOCATION COUNTER STANDS AT BIT 25") and this page
confirms it independently, then chains eight more rows off it without
a single byte boundary -- .31, .40, .51, .52, .53, .62, .63, .73,
every one of them printed.  All nine are in SYMBOLS below, so the
chain is checked end to end.

EIGHT MORE INDEX-REGISTER SYNs, lines 33-40, "L IODX SYN,$3" through
"L WORKX SYN,$10" -- the shape printed p.46 introduced.  The listing
prints their LOCATION as the register's own bit address, 000023.00
through 000032.00, and that is what the symbol checks compare.

AND LINE 5 CARRIES BOTH A dds AND A BIT ADDRESS: "L IREF
SYN(BU,12),0.52" prints location 000000.64 -- 0o64 is 52, so the
source is DECIMAL and the location column OCTAL, which is this
listing's habit everywhere.  The dds column prints "BU,14 ,10",
octal for (BU,12,8).

THE COUNTS ARE INTEGERS, NOT ADDRESSES, and the listing's own
arithmetic says so: lines 15-17 write "32-2" and "16-2" where the
count column prints 000036 and 000016.

LINE 46 IS listing_typography.md 13d's SHAPE -- a row where the drum
lost several glyphs at once, "L ICSCR ... -ICDSQ COLNTER", and
"COLNTER" gives it away before anything else is read.  The name is
transcribed "L IOSCR" and NO COMPILED BIT DEPENDS ON THE SPELLING:
the symbol is referenced nowhere on this page, and the nine bits it
reserves are checked by line 47's address.  The deck's header says
what to come back to if a later page references it.

THREE INJECTIONS, OBSERVED FAILURE SETS WRITTEN DOWN:

  "T IOC SYN,80" -> "SYN,81" -- 2 FAILs, lines 13 and 24, the only
  two rows that use it, and no symbol moves: a count is not a size.
  Line 44's "VF,.06" -> "VF,.07" -- 1 FAIL, line 44's row, and NO
  symbol moves either, which is the point: VF's twenty-five bits are
  its SIZE and the value is independent of it.
  Line 45's "DRZ(BU,7),(1)" -> "DRZ(BU,8),(1)" -- 9 FAILs: the seven
  symbols from L IOSCR to L INFAD each shift one bit, AND lines 47
  and 48's one-bit data read the wrong bit.  That is the bit chain
  doing its job, and the two row failures are the part a symbol
  check alone would not have caught.
"""
from listing_oracle import check_rows, finish
from strap_asm import assemble

prog = assemble(open("../decks/mcp_bootstrap_p48.strap").read())

SYMBOLS = {
    # The field definition, line 5: a dds and a bit address together.
    "LIREF":  "000000.64",
    # The refill index words, lines 9-18.
    "LPPURF": "002557.00",
    "LPPREF": "002562.00",
    "LIOTBX": "002563.00",
    "LFSTRX": "002564.00",
    "LSYMUX": "002565.00",
    "LSYMCX": "002566.00",
    "LNTPUX": "002567.00",
    "LXTYPE": "002570.00",
    # The swap area, line 22.
    "LTY":    "002571.00",
    # >>> THE EIGHT INDEX-REGISTER SYNs, lines 33-40.  The listing
    # prints each register's own bit address.
    "LIODX":  "000023.00",
    "LXPP":   "000024.00",
    "LXIO":   "000025.00",
    "LXFR":   "000026.00",
    "LXSU":   "000027.00",
    "LXSC":   "000030.00",
    "LXNT":   "000031.00",
    "LWORKX": "000032.00",
    # >>> THE BIT CHAIN, lines 44-52.  Nine addresses, none of them
    # on a byte boundary, and the first of them is what says VF is
    # twenty-five bits.
    "LNO6":   "002601.00",
    "LTAPEC": "002601.31",
    "LIOSCR": "002601.40",
    "LFINB":  "002601.51",
    "LNTB":   "002601.52",
    "LCOUNT": "002601.53",
    "LCVBIT": "002601.62",
    "LBLZOR": "002601.63",
    "LINFAD": "002601.73",
    # The four tables this page predicts, read off its own binary.
    "LSYMU":  "002620.00",
    "LSYMC":  "002660.00",
    "LNTPU":  "002700.00",
    "LDISK":  "002723.00",
}

ROWS = [
    # TABLE INDICES FOR REFILL USE: ten self-refilling index words.
    ("002557.00", "003370.00+ 000 000002 002557",
     "line 9   L PPURF  XW,T PURFT,T UPPC,$  -NOT OVERLAP PP REF."),
    ("002560.00", "003514.00+ 000 000024 002560",
     "line 10  XW,T UIORQ,T UIOC,$  -NOT OVERLAP I/O REQ."),
    ("002561.00", "003623.00+ 000 000024 002561",
     "line 11  XW,T UFRE,T UFRC,$  -NOT OVERLAP FIRST REEL"),
    ("002562.00", "003317.00+ 000 000024 002562", "line 12  LPPREF  XW,T PREFT,T PPC,$"),
    ("002563.00", "003373.00+ 000 000120 002563", "line 13  LIOTBX  XW,T IOREQ,T IOC,$"),
    ("002564.00", "003541.00+ 000 000062 002564", "line 14  LFSTRX  XW,T FSTRE,T FRC,$"),
    # "32-2" and "16-2" print as 000036 and 000016 -- the listing's
    # own arithmetic, in octal.
    ("002565.00", "002620.00+ 000 000036 002565",
     "line 15  L SYMUX  XW,L SYMU,32-2,$  -SYMBOLIC TAPE INDEX"),
    ("002566.00", "002660.00+ 000 000016 002566",
     "line 16  L SYMCX  XW,L SYMC,16-2,$  -SYMBOLIC CHANNEL INDEX"),
    ("002567.00", "002700.00+ 000 000016 002567",
     "line 17  L NTPUX  XW,L NTPU,16-2,$  -NON-TAPE INDEX REFILL"),
    ("002570.00", "002723.00+ 000 000011 002570",
     "line 18  L XTYPE  XW,L DISK,9,$  -THE TYPE CODE INDEX"),
    # SWAP AREA FOR EIGHT MCP-DECODE INDICES.  Line 22's bare "XW" is
    # a null value field, all four groups zero.
    ("002571.00", "000000.00+ 000 000000 000000", "line 22  L TY  XW"),
    # And these six REFILL to the index words above rather than to
    # themselves -- the one difference from lines 12-17, and the
    # whole reason the block is called a swap area.
    ("002572.00", "003317.00+ 000 000024 002562", "line 23  XW,T PREFT,T PPC,LPPREF"),
    ("002573.00", "003373.00+ 000 000120 002563", "line 24  XW,T IOREQ,T IOC,LIOTBX"),
    ("002574.00", "003541.00+ 000 000062 002564", "line 25  XW,T FSTRE,T FRC,LFSTRX"),
    ("002575.00", "002620.00+ 000 000036 002565", "line 26  XW,L SYMU,32-2,L SYMUX"),
    ("002576.00", "002660.00+ 000 000016 002566", "line 27  XW,L SYMC,16-2,L SYMCX"),
    ("002577.00", "002700.00+ 000 000016 002567", "line 28  XW,L NTPU,16-2,L NTPUX"),
    ("002600.00", "000000.00+ 000 000000 000000", "line 29  XW"),
    # >>> THE ROW THAT CONFIRMS VF = 25 BITS, by what follows it.
    ("002601.00", "000000.06+", "line 44  L NO6  VF,.06  -FOR IX BUMMPING"),
    # The one-bit data, printed as a single digit.
    ("002601.51", "1", "line 47  L FINB  DD(BU,1),1  -FINAL BIT", 1),
    ("002601.52", "0", "line 48  L NTB  DD(BU,1),0  -NON-TAPE BIT", 1),
    ("002601.62", "0", "line 50  L CVBIT  DD(BU,1),0  -OVERLAPPED JOB", 1),
    ("002601.73", "0", "line 52  L INFAD  DD(BU,1),0  -INFINITE-DISK", 1),
]

fails = check_rows(prog, ROWS, SYMBOLS, label="MCP p.48 ")
finish(fails)
