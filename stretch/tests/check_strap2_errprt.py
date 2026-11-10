#!/usr/bin/env python3
"""check_strap2_errprt.py -- STRAP II's error list: ERRNUM and ERRPRT.

Sources, read in the ink 2026-11-09:
  C22-6729 pp.37-39 (five lists; Fig. 6's record: page, line, field, number),
    p.158 box 35 (ERRPRT sorts into page and line sequence, after NUNDSY's lists,
    before OEDIT's time message), pp.176-179 (the numbered messages, each ending
    in its own number).
  C28-6129 p.20: a message references the LAST line the statement occupies.
  N28-1081 (April 1963) page 13: the revised list, "printed at the end of the
    listing, in sequence by page and line number", an extra asterisk "following
    the line number and asterisk on all lines containing an error", and 1-18
    serious; pages 14-15, the rest of the list.

The deck: a KF whose symbol is N-mode (message 91, found in Pass 2b) on line 2;
a SYN with neither name nor address (43, 44, Pass 1) on line 3; a legal multiple
(131, NUNDSY, no unit); an illegal op on a statement continued onto a second card
(1, Pass 1) across a page boundary at four lines a page.  Detection order is 43,
44, 1, 91, 131; the printed order must be page and line.

MEASURED INJECTIONS, 2026-11-09, PYTHONDONTWRITEBYTECODE=1, control all passing:
  ERRPRT unsorted:                       A1, A2, A3, B1
  first line, not last, of a statement:  A1, A2, B1, D1
  page not stepped at the page limit:    A1, A2, B1
  host's text printed, not the table's:  A2, B1
  update's list ignored (guide's used):  B1
  error list after the seconds:          C1
  no extra '*' in the 1963 form:         D1
  extra '*' in the 1961 form too:        D2
  serious bounds swapped:                F1, F2
  91 recorded in 2a as well:             A1, A2, A4
  121 recorded in 2a as well:            G1
  121 with no unit:                      G1
"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "strap"))
from strap2 import compile_cards                 # noqa: E402
from strap2.listing import listing_of            # noqa: E402
from strap2.errtab import message, serious       # noqa: E402

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


CARDS = [card("", "SLC,64."), card("", "KF,X"), card("", "SYN"), card("X", "DR(N),1"),
         card("Y", "SYN,5"), card("Y", "SYN,5"), card("", "FOO,1,"), "*        2",
         card("", "END,0")]
p2 = compile_cards(CARDS)


def listing(**kw):
    return listing_of(p2, p2.p1.print_names, lines_per_page=4, **kw)


# A. The guide's list, the 1961 form.
lst = listing()
check("A1 records: page, line, field, number, in page and line order",
      lst.records, [(0, 0, 0, 131), (1, 2, 0, 91), (1, 3, 0, 43), (1, 3, 0, 44),
                    (2, 4, 0, 1)])
text = lst.text("1", 3).splitlines()
errs = [t for t in text if t.startswith("PAGE ")]
check("A2 the table's words, each ending in its number", errs,
      ["PAGE   0  LINE  0  FIELD  0  MULT. DEFINED SYM WITH NO CONTRADICTION  131",
       "PAGE   1  LINE  2  FIELD  0  MODE INCONSISTENT WITH OP  91",
       "PAGE   1  LINE  3  FIELD  0  SYN WITHOUT A NAME  43",
       "PAGE   1  LINE  3  FIELD  0  SYN WITHOUT AN ADDRESS FIELD  44",
       "PAGE   2  LINE  4  FIELD  0  ILLEGAL OP CODE  1"])
check("A4 91 recorded once, though DECODE runs in 2a and 2b",
      [m[0] for m in p2.msg.items].count(91), 1)
check("A3 detection order differs from the printed order",
      [m[0] for m in p2.msg.items] != [r[3] for r in lst.records], True)

# B. The update's list.
errs = [t for t in listing(errors="N28-1081").text().splitlines() if t.startswith("PAGE ")]
check("B1 N28-1081's words for 1", errs[-1],
      "PAGE   2  LINE  4  FIELD  0  ILLEGAL OPERATION CODE  1")
try:
    listing(errors="C28-6129")
    check("B2 a list with no table refuses", "accepted", "ValueError")
except ValueError:
    check("B2 a list with no table refuses", "ValueError", "ValueError")

# C. Lists, then errors, then the seconds (p.158 boxes 34-36).
ix = {k: next(i for i, t in enumerate(text) if t.startswith(k))
      for k in ("SYMBOLS DEFINED BUT NOT USED", "PAGE ", "    THIS ASSEMBLY")}
check("C1 lists, errors, seconds",
      ix["SYMBOLS DEFINED BUT NOT USED"] < ix["PAGE "] < ix["    THIS ASSEMBLY"], True)

# D. The extra '*' (N28-1081 page 13), on each line an error references.
t63 = listing(mark="*", quote="-", form="1963").text().splitlines()
check("D1 1963: '**' on exactly the lines errors reference",
      [t[:4] for t in t63 if t[2:4] == "**"], [" 2**", " 3**", " 4**"])
check("D2 1961: none", [t for t in text if t[2:4] == "-*"], [])

# E. A clean deck prints no error list.
clean = compile_cards([card("", "SLC,64."), card("", "B,0"), card("", "END,0")])
check("E1 nothing to print", [t for t in listing_of(clean, clean.p1.print_names).text()
                              .splitlines() if t.startswith("PAGE ")], [])

# F. Serious messages: 1-28 in the guide, 1-18 in the update.
check("F1 20 serious in the guide", serious(20, "C22-6729"), True)
check("F2 20 not serious in the update", serious(20, "N28-1081"), False)
check("F3 29 serious in neither", (serious(29), serious(29, "N28-1081")), (False, False))
check("F4 a spare prints SPARE", message(21, "N28-1081"), "SPARE  21")

# G. An inserter's message (INSERT, 121) belongs to its unit and is recorded once.
twice = compile_cards([card("", "SLC,64."), card("", "INDMK,3,3"), card("", "END,0")])
tl = listing_of(twice, twice.p1.print_names)
check("G1 121 once, on line 2", tl.records, [(1, 2, 0, 121)])

print("errprt: FAILED" if fails else "errprt: all passed")
sys.exit(1 if fails else 0)
