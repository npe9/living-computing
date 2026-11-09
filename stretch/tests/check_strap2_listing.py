#!/usr/bin/env python3
"""check_strap2_listing.py -- OUTPUT's listing against the two printed STRAP II
listings this project holds, line for line.

  Fig. 3, C28-6129 printed p.19 (PDF 23), read in the ink.  The cards are written
  out from the listing's right half.  Line 18's location prints 000113.0 on the
  page; the listing's own neighbours make it 000113.00, and the test expects that.
  Fig. 5, C22-6678-1 printed p.48, read in the ink.  The source is
  decks/mcpref_example2.strap with its two stand-ins replaced by the page's own
  IOD and PRNS cards, so RON is the first IOD's reference number and not a SYN.
  That deck's transcription drops the apostrophes, so only location, binary and
  name are compared.

Every field is compared.  The print positions are CHOSEN (listing.py) and are
not compared.  Also here, MIOD's numbers from pp.96-97 and 178.

MEASURED INJECTIONS, 2026-11-09, run with PYTHONDONTWRITEBYTECODE (two
injections of one size in one second otherwise reuse a stale .pyc, which faked
a result here once).  Failing checks, control all passing:
  location point moved, or hex printed as octal: 69 each, every half-word row.
  XW and CW not index form: Fig. 3 line 17 and p.48 rows 20, 21.  CW alone: rows 20, 21.
  flags printed as digits: Fig. 3 line 15.
  lower bound the first word: LOWER, twice.  Upper the last word: UPPER, twice.
  long name sharing its line: line count, lines 20, 21, 22.
  DR printing its end, not size: 7, Fig. 3 lines 16, 18, 22 and p.48 rows 22-25.
  one line per DD: 10, from line count on.  Comment mark kept: lines 3, 11.
  continuation running on: 14, from line count on.
  name's trailing blank lost: Fig. 3 line 22.
  reference number an integer, not a word: 11, p.48's ,RON rows.
  reference number not stepping: "the second IOD is reference 2".
  MCP order unchecked: "after an instruction".
  type field kept as the exit: "no exit", "null exit".
  no 103, 104, 105 or 143: the matching check alone.
"""
import os
import re
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap2 import compile_cards                 # noqa: E402
from strap2.cards import deck_cards              # noqa: E402
from strap2.listing import listing_of, loc       # noqa: E402

fails = 0


def check(label, got, want):
    global fails
    if got == want:
        print(f"PASS {label}")
    else:
        fails += 1
        print(f"FAIL {label}: got {got!r}, want {want!r}")


def card(name, stmt):
    return " " + name.ljust(8) + stmt


FIG3_CARDS = [
    card("", "SLC,64."),
    card("NEXT", "SYN,(8)17777.0"),
    card("ABLE", "LX,7,INDEX              'LOAD INDEX"),
    card("", "L(BU),BAKER"),
    card("CHARLIE", "ST(BU,4)(V+IC),.8($7)"),
    card("", "BZXCZ,CHARLIE"),
    card("", "L(N),DOG"),
    card("", "+(N),DOG+1."),
    card("", "ST(N),FOX"),
    card("", "L(BU,24),SOME VERY LONG NAME"),
    card("", "ST(BU,24),SOME OTHER LONG NAME   'TESTING LONG COMMENTS THAT"),
    "*" + " " * 8 + "WILL CARRY OVER TO THE NEXT LINE",
    card("", "B,NEXT"),
    card("DOG", "DD(N),28671X7,183007S7"),
    card("FOX", "DR(BU),(1)"),
    card("INDEX", "XW,ZEBRA,4"),
    card("ZEBRA", "DR(BU,4),(4)"),
    card("BAKER", "(8)DD(BU,12),5703"),
    card("SOME VER", ""),
    "*Y LONG N",
    "*AME     DD(BU,24),28671",
    card("SOME OTH", ""),
    "*ER LONG ",
    "*NAME    DR(BU,24),(1)",
    card("", "END,ABLE"),
]

FIG3 = [
    (1, "000100.00", "", "", "SLC,64."),
    (2, "017777.00+", "+00000000", "NEXT", "SYN,(8)17777.0"),
    (3, "000100.00", "000112.16 10", "ABLE", "LX,7,INDEX -LOAD INDEX"),
    (4, "000100.40", "000113.20 80 000000.20 50", "", "L(BU),BAKER"),
    (5, "000101.40", "000000.10 87 204000.20 D0", "CHARLIE", "ST(BU,4)(V+IC),.8($7)"),
    (6, "000102.40", "000101.70 40", "", "BZXCZ,CHARLIE"),
    (7, "000103.00", "000107.00 60", "", "L(N),DOG"),
    (8, "000103.40", "000110.00 20", "", "+(N),DOG+1."),
    (9, "000104.00", "000111.00 E0", "", "ST(N),FOX"),
    (10, "000104.40", "000113.34 80 030000.20 50", "", "L(BU,24),SOME VERY LONG NAME"),
    (11, "000105.40", "000113.64 80 030000.20 D0", "",
     "ST(BU,24),SOME OTHER LONG NAME -TESTING LONG COMMENTS THAT"),
    (12, "", "", "", "WILL CARRY OVER TO THE NEXT LINE"),
    (13, "000106.40", "017777.10 00", "", "B,NEXT"),
    (14, "000107.00", "0007+ 6777700000000000 +000", "DOG", "DD(N),28671X7,183007S7"),
    (15, "000110.00", "0022+ 5453370000000000 +TUV", "", ""),
    (16, "000111.00", "000001.00", "FOX", "DR(BU),(1)"),
    (17, "000112.00", "000113.00+ 000 000004 000000", "INDEX", "XW,ZEBRA,4"),
    (18, "000113.00", "000000.20", "ZEBRA", "DR(BU,4),(4)"),
    (19, "000113.20", "5703", "BAKER", "(8)DD(BU,12),5703"),
    (20, "000113.34", "00067777", "SOME VERY LONG NAME", ""),
    (21, "", "", "", "DD(BU,24),28671"),
    (22, "000113.64", "000000.30", "SOME OTHER LONG NAME", ""),
    (23, "", "", "", "DR(BU,24),(1)"),
    (24, "000114.14", "000100.00", "", "END,ABLE"),
]

# p.48, location, binary, name, from line 3 of the first page.
P48 = [
    ("000041.00", "000040.10 00", "START"), ("000041.40", "000104.40 80", ""),
    # Line 5's LVE: the page prints 80, the pocket card and MCP's own listing give
    # B0.  Recorded in verify_mcpref_example2_listing.py, and pinned as B0 here.
    ("000042.00", "000055.01 B0", ""), ("000042.40", "000001.00 80", ""),
    ("000043.00", "000000.00 80", ""), ("000043.40", "000051.10 00", ""),
    ("000044.00", "000040.10 00", ""), ("000044.40", "000013.40 80", ""),
    ("000045.00", "000001.00 80", ""), ("000045.40", "000054.00 80 000055.02 E0", ""),
    ("000046.40", "000040.10 00", ""), ("000047.00", "000001.41 80", ""),
    ("000047.40", "000001.00 80", ""), ("000050.00", "000054.00 80", ""),
    ("000050.40", "000041.10 00", ""), ("000051.00", "000040.10 00", "EOJ"),
    ("000051.40", "000007.41 80", ""), ("000052.00", "000001.00 80", ""),
    ("000052.40", "000040.10 00", ""), ("000053.00", "000101.00 80", ""),
    ("000054.00", "000056.00+ 000 000017 000000", "CW"),
    ("000055.00", "000075.00+ 000 000017 000000", ""),
    ("000056.00", "000017.00", "BUF1"), ("000075.00", "000017.00", "BUF2"),
    ("000114.00", "000002.00", "EXIT"), ("000116.00", "000122.10 00", ""),
    ("000116.40", "000000.30 00", ""), ("000117.00", "000040.10 00", ""),
    ("000117.40", "000101.00 80", ""), ("000120.00", "000040.10 00", ""),
    ("000120.40", "000104.00 80", ""), ("000121.00", "000040.10 00", ""),
    ("000121.40", "000041.00 80", ""), ("000122.00", "000115.11 80 000131.34 02", "UK"),
    ("000123.00", "000040.10 00", ""), ("000123.40", "000006.01 80", ""),
    ("000124.00", "000001.00 80", ""), ("000124.40", "000040.10 00", ""),
    ("000125.00", "000005.01 80", ""), ("000125.40", "000040.10 00", ""),
    ("000126.00", "000001.40 80", ""), ("000126.40", "000001.00 80", ""),
    # the second page
    ("000127.00", "000054.00 80", ""), ("000127.40", "000040.10 00", ""),
    ("000130.00", "000013.40 80", ""), ("000130.40", "000001.00 80", ""),
    ("000131.00", "000040.10 00", "EPGK"), ("000131.40", "000010.41 80", ""),
    ("000132.00", "000001.00 80", ""), ("000132.40", "000040.10 00", ""),
    ("000133.00", "000015.00 80", ""), ("000133.40", "000001.00 80", ""),
    ("000134.00", "000142.00 80", ""), ("000134.40", "000040.10 00", ""),
    ("000135.00", "000043.40 80", ""), ("000135.40", "000142.00 80", ""),
    ("000136.00", "000003.00 80", ""), ("000136.40", "000040.10 00", ""),
    ("000137.00", "000001.40 80", ""), ("000137.40", "000001.00 80", ""),
    ("000140.00", "000054.00 80", ""), ("000140.40", "000040.10 00", ""),
    ("000141.00", "000013.40 80", ""), ("000141.40", "000001.00 80", ""),
    ("000142.00", "000001.00", "MESG"), ("000143.00", "", ""),
    ("000145.00", "000041.00", ""),
]


def squeeze(s):
    return re.sub(r" +", " ", s)


def run_fig3():
    p2 = compile_cards(FIG3_CARDS)
    fatal = [m for m in p2.msg.items if m[3]]
    check("Fig. 3 assembles with no error", fatal, [])
    lst = listing_of(p2, p2.p1.print_names)
    check("Fig. 3 line count", len(lst.lines), len(FIG3))
    for ln, want in zip(lst.lines, FIG3):
        n, a, b, name, s = ln.fields()
        check(f"Fig. 3 line {want[0]}", (n, a, b, name, squeeze(s)), want)
    low, high = lst.bounds()
    check("Fig. 3 LOWER MEMORY BOUND", loc(low), "000077.00")
    check("Fig. 3 UPPER MEMORY BOUND", loc(high), "000115.00")
    text = lst.text("011000101", 32)
    for frag in ("000077.00 LOWER MEMORY BOUND", "000115.00 UPPER MEMORY BOUND",
                 "BINARY OUTPUT", "00000032 SECONDS", " 1- 000100.00"):
        check(f"Fig. 3 prints {frag!r}", frag in text, True)
    return lst


def run_p48():
    # Lines 1 and 2 as printed, for the deck's stand-ins: its SLC, and RON's SYN.
    src = open(os.path.join(HERE, "..", "decks", "mcpref_example2.strap")).read()
    kept = [s for s in src.splitlines()
            if not s.startswith("        SLC, (8)41.0") and not s.startswith("RON     SYN")]
    cards = ["BRON      IOD,TAPE,EXIT,,,ODD,HD,CSAVE", card("", "PRNS")]
    p2 = compile_cards(cards + deck_cards("\n".join(kept)))
    check("p.48 assembles with no error", [m for m in p2.msg.items if m[3]], [])
    lst = listing_of(p2, p2.p1.print_names, mark="*")
    check("p.48 line 1", lst.lines[0].fields()[1:4] , ("", "", "RON"))
    check("p.48 line 2", lst.lines[1].fields()[1:], ("", "", "", "PRNS"))
    lines = lst.lines[2:]
    check("p.48 line count", len(lines), len(P48))
    for k, (ln, want) in enumerate(zip(lines, P48)):
        check(f"p.48 row {k} at {want[0]}", (ln.location, ln.binary, ln.name), want)


def numbers(cards):
    return [m[0] for m in compile_cards(cards).msg.items]


def run_iod():
    """MIOD, C22-6729 pp.96-97, 178.  The numbers are its error table's."""
    p2 = compile_cards(["BX        IOD,TAPE,EXIT", "BY        IOD,DISK,EXIT",
                        card("", ",X"), card("", ",Y"),
                        card("EXIT", "DR(N),2"), card("", "END,0")])
    check("the second IOD is reference 2",
          (p2.image.words[0o41] >> 32, p2.image.words[0o41] & 0xFFFFFFFF),
          ((1 << 14) | 0x80, (2 << 14) | 0x80))
    check("an IOD takes no location: the first code is at 000041.00",
          sorted(p2.image.words)[:1], [0o41])
    check("no name: 103", 103 in numbers(["B         IOD,TAPE,E", card("", "END,0")]), True)
    check("no exit: 104", 104 in numbers(["BX        IOD,TAPE", card("", "END,0")]), True)
    check("null exit: 143", 143 in numbers(["BX        IOD,TAPE,", card("", "END,0")]), True)
    check("after an instruction: 102",
          102 in numbers([card("", "B,$MCP"), "BX        IOD,TAPE,E", card("E", "DR(N),1"),
                          card("", "END,0")]), True)
    check("first, not 102",
          102 in numbers(["BX        IOD,TAPE,E", card("", "B,$MCP"), card("E", "DR(N),1"),
                          card("", "END,0")]), False)
    check("a REEL with a name: 105",
          105 in numbers(["BX        REEL,1", card("", "END,0")]), True)
    check("a REEL without one: no 105",
          105 in numbers(["B         REEL,1", card("", "END,0")]), False)


run_fig3()
run_p48()
run_iod()
print("listing: FAILED" if fails else "listing: all passed")
sys.exit(1 if fails else 0)
