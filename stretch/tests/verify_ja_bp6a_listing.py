#!/usr/bin/env python3
"""verify_ja_bp6a_listing.py -- assemble ../decks/ja_bp6a_memory_patterns.strap
(IBM's JA BP6A "MEMORY PATTERN TESTS", May 5, 1961,
docs/ja_bp6a_memory_patterns_test.pdf PDF pp.4-6) and compare every
assembled word against the machine code printed beside each line -- see
strap/listing_oracle.py.

THE WHOLE PROGRAM IS CHECKED, not a block of it: the listing is 65
lines and every symbol is defined inside it, so every address-bearing
row is a genuine address-placement check (no "ext" SYNs).

WHAT IS NOT CHECKED:
  - 100016.00, MPTDD2: the page is torn there (PDF p.5's last line);
    neither the operand past "0 525 252" nor the printed word survives.
    The deck reconstructs it from MPTDD1.
  - The two DR rows print only the reservation length ("31.00" for
    MPST1's 25 words, "1062.00" for MPST2's 562).  The oracle has no
    shape for that, so they are checked here as the distance from the
    DR's symbol to the next one (FINM1, FINM2), which is what the length
    decides.
  - PRNID, SEM, PUNFUL and the SLCs print no code.

PUNFUL.  The deck is "PUNFUL Binary" (writeup p.1, 1.1).  The printed
"PUNFUL," card is commented out in the deck (its header says why: with
it, strap_asm loads nothing), so the deck assembles to the image IPL
would have loaded, and that is the image both this check and the run
harness use.

Run standalone: `./verify_ja_bp6a_listing.py`. Wired into run_tests.sh.
"""

import os

from strap_asm import assemble
from listing_oracle import check_rows, finish, loc_bits

DECK = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "decks", "ja_bp6a_memory_patterns.strap")


def image_source():
    """The deck's text: the image both this check and run_ja_bp6a.sh use.
    A live PUNFUL card is refused rather than silently dropped."""
    text = open(DECK).read()
    for line in text.splitlines():
        if line.split("!", 1)[0].strip().upper().rstrip(",") == "PUNFUL":
            raise SystemExit("ja_bp6a: a live PUNFUL card would load nothing")
    return text


Z22 = "0" * 22

ROWS = [
    # PDF p.4 -- the load chain's control words, then MPATA (Part I).
    ("000775.00", "776.00 60 000040.01 FE",    "CW(CDSC),510.,2,510"),
    ("000776.00", "1000.00 60 001520.01 FF",   "CW(CDSC),512.,FINM1-MPATA,$+1.0"),
    ("000777.00", "100000.00 20 022320.01 FF", "CW(CD),32768.,FINM2-MPATB,$"),
    ("001000.00", "62.05 02",                  "MPATA  LCI,$X2,50"),
    ("001000.40", "0.30 00",                   "       NOP,0.0"),
    ("001001.00", "100000.00 80 001034.04 20", "       T,$X2,MPATB,MPST1"),
    ("001002.00", "1013.02 10",                "MPATA1 LX,$X1,MPAXW1"),
    ("001002.40", "6.05 02",                   "       LCI,$X2,6"),
    ("001003.00", "1014.00 81 100000.02 A0",   "MPAT1  TI,1,MPTDA1($X1),32768."),
    ("001004.00", "100000.00 80 100001.02 20", "       T,$X1,32768.,32769."),
    ("001005.00", "4.43 80 001003.34 02",      "       BB,4.35,MPAT1"),
    ("001006.00", "1.03 05",                   "       V+I,$X1,1.0"),
    ("001006.40", "1003.04 48",                "       CB,$X2,MPAT1"),
    ("001007.00", "4.44 80 001002.34 02",      "       BB,4.36,MPATA1"),
    ("001010.00", "62.05 02",                  "       LCI,$X2,50."),
    ("001010.40", "0.30 00",                   "       NOP,0."),
    ("001011.00", "1034.00 80 100000.04 20",   "       T,$X2,MPST1,MPATB"),
    ("001012.00", "100000.10 00",              "       B,MPATB"),
    ("001012.40", "0.30 00",                   "       NOP,0"),
    ("001013.00", "0.00 03 777760.02 0B",      "MPAXW1 XW,0,65535,$"),
    ("001014.00", Z22,                         "MPTDA1 0S"),
    ("001015.00", "1777777777777777777777",    "MPTDB1 1S"),
    ("001016.00", "1252525252525252525252",    "MPTDC1 1010"),
    ("001017.00", "0525252525252525252525",    "MPTDD1 0101"),
    ("001020.00", "0000000000060000000001",    "MPTDE1 0S ECC"),
    ("001021.00", "1777777777757777777777",    "MPTDF1 1S ECC"),
] + [
    (f"{0o1022 + i:06o}.00", Z22, f"buffer word {i + 1}") for i in range(10)
] + [
    # PDF p.5
    ("001065.00", "0.30 00",                   "FINM1  NOP,0"),
    ("001065.40", "0.30 00",                   "       NOP,0"),
    ("100000.00", "1062.05 02",                "MPATB  LCI,$X2,562"),
    ("100000.40", "100.00 80 100033.04 20",    "       T,$X2,64.0,MPST2"),
    ("100001.40", "100012.02 10",              "MPATB2 LX,$X1,MPAXW2"),
    ("100002.00", "6.05 02",                   "       LCI,$X2,6"),
    ("100002.40", "100013.00 81 000040.02 A0", "MPAT2  TI,1,MPTDA2($X1),32.0"),
    ("100003.40", "40.00 80 000041.02 20",     "       T,$X1,32.,33."),
    ("100004.40", "4.43 80 100002.74 02",      "       BB,4.35,MPAT2"),
    ("100005.40", "1.03 05",                   "       V+I,$X1,1.0"),
    ("100006.00", "100002.44 48",              "       CB,$X2,MPAT2"),
    ("100006.40", "4.45 80 100001.74 02",      "       BB,4.37,MPATB2"),
    ("100007.40", "1062.05 02",                "       LCI,$X2,562"),
    ("100010.00", "100033.00 80 000100.04 20", "       T,$X2,MPST2,64.0"),
    ("100011.00", "1000.10 00",                "       B,MPATA"),
    ("100011.40", "0.30 00",                   "       NOP"),
    ("100012.00", "0.00 01 776762.00 0A",      "MPAXW2 XW,0,32735,$"),
    ("100013.00", Z22,                         "MPTDA2 0S"),
    ("100014.00", "1777777777777777777777",    "MPTDB2 1S"),
    ("100015.00", "1252525252525252525252",    "MPTDC2 1010"),
    # 100016.00 MPTDD2: TORN, not checked.
    # PDF p.6
    ("100017.00", "0000000000060000000001",    "MPTDE2 0S ECC"),
    ("100020.00", "1777777777757777777777",    "MPTDF2 1S ECC"),
] + [
    (f"{0o100021 + i:06o}.00", Z22, f"buffer word {i + 1}") for i in range(10)
] + [
    ("101115.00", "0.30 00",                   "FINM2  NOP,0.0"),
    ("101115.40", "0.30 00",                   "       NOP,0.0"),
]

SYMBOLS = {
    "MPATA": "001000.00", "MPATA1": "001002.00", "MPAT1": "001003.00",
    "MPAXW1": "001013.00", "MPTDA1": "001014.00", "MPTDB1": "001015.00",
    "MPTDC1": "001016.00", "MPTDD1": "001017.00", "MPTDE1": "001020.00",
    "MPTDF1": "001021.00", "MPST1": "001034.00", "FINM1": "001065.00",
    "MPATB": "100000.00", "MPATB2": "100001.40", "MPAT2": "100002.40",
    "MPAXW2": "100012.00", "MPTDA2": "100013.00", "MPTDB2": "100014.00",
    "MPTDC2": "100015.00", "MPTDD2": "100016.00", "MPTDE2": "100017.00",
    "MPTDF2": "100020.00", "MPST2": "100033.00", "FINM2": "101115.00",
}


def main():
    prog = assemble(image_source())
    fails = check_rows(prog, ROWS, SYMBOLS, label="ja_bp6a ")
    # The DR rows: printed "31.00" and "1062.00" are the reservation
    # lengths in words (octal); check them as symbol distances.
    for dr, nxt, printed in (("MPST1", "FINM1", "31.00"),
                             ("MPST2", "FINM2", "1062.00")):
        got = (prog.symtab[nxt] - prog.symtab[dr]) // 64
        want = int(printed.split(".")[0], 8)
        ok = got == want
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} ja_bp6a {dr} DR length {printed}: "
              f"assembled {got:o}, listing {want:o}")
    # END,MPATA prints "1000.00" at 101116.00.
    ok = prog.end_pc == loc_bits("001000.00") // 32
    fails += not ok
    print(f"{'PASS' if ok else 'FAIL'} ja_bp6a END,MPATA 1000.00: "
          f"assembled half-word {prog.end_pc}")
    finish(fails)


if __name__ == "__main__":
    main()
