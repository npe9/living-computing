# `vision_ocr.swift` -- macOS Vision as an INDEPENDENT reading of the listing

    swiftc -O -o vision_ocr vision_ocr.swift
    ./vision_ocr page.png            # y <TAB> x <TAB> confidence <TAB> text

`usesLanguageCorrection` is **off**, and must stay off. The listing is
machine code, not prose; language correction invents plausible words
and that is precisely the failure rule 3 exists to prevent. Pass
`--correct` only to demonstrate how much worse it gets.

Coordinates are normalised, y measured from the top so a sort gives
reading order. The columns separate cleanly by x on every page tried:

    x ~ 0.20   LOCATION
    x ~ 0.29   BINARY half word 1
    x ~ 0.33   its HEX BYTE
    x ~ 0.37   BINARY half word 2

## MEASURED, against ground truth the decks already carry

| task | tesseract | **Vision** | our template classifier |
|---|---|---|---|
| symbol pages, name accuracy | 43% | **69%** | not tried (letters) |
| LOCATION column, characters | -- | **99.7%** | 98.0% |
| LOCATION column, whole strings | -- | **97.7%** | 82.0% |
| HEX BYTE | -- | **87.4%** | 89.3% |

Vision is clearly the better reader of the LOCATION column and it is
forty lines of Swift against a whole pipeline. Note its RECALL is
lower: it read 177 locations where the decks list 227, about 78%. It
declines rather than guesses, which for a cross-check is the right
bias.

**Apply the alphabet constraint.** Raw Vision scores 81.7% on the hex
byte and most of the loss is the LETTER `O` where the DIGIT `0`
belongs. Hex is `0-9A-F`: `O` and `Q` are not in it and `I` is not
either. Mapping O,Q->0 and I->1 takes it to 87.4%. Same for the octal
fields, which contain no `C` and no `O`.

## THE CONVERGENT NEGATIVE: C AND 0

After the alphabet constraint, **58 of Vision's 89 remaining hex
errors are `C` read where `0` is printed** (`00`->`C0` 42 times,
`01`->`C1` 12). Our template classifier, trained on 2,642 labelled
cells cut from this very drum, fails the same way: C at 78.7%, C->0
20 and 0->C 19.

So three independent methods -- tesseract, Apple's production OCR, and
a classifier trained on this drum -- all break on C against 0. The
hand-measured negative in `docs/transcription_workflow.md` (width and
openness, n=6 per class) is now very well supported. **A round glyph
is not settled by image processing.** It is settled by the corpus, by
a manual, or by the assembler.

## WHAT IT IS FOR, AND WHAT IT IS NOT FOR

A second reading of the NUMERIC columns that has never seen the
volume OCR. Ten rows of `C`-for-`0` reached the corpus because
listing blocks were pasted from that OCR; Vision reading the page
disagrees with such a row. It FLAGS; a human resolves. Rule 3 is
unchanged.

**Not used: the on-device LLM** (Foundation Models). For this task a
language model is the wrong instrument -- asked to clean up a symbol
name it will produce a plausible one, which is indistinguishable from
a reading and is the exact error this project spends its time
preventing. Vision returns what it saw; that is what is wanted.

## CROSS-READING: TWO ENGINES, SEVERAL RESOLUTIONS (2026-11-03)

`tools/multi_read.py` reads a page seven ways in one coordinate
frame: Vision on the whole page at 200/300/400 dpi, Vision on a
LINE..BINARY column crop at 300/600, tesseract (whitelisted to
`0-9A-F.*`) on the crop at 300/600. `tools/score_readers.py` pairs
every reader to the landed decks' assertions (`strap/listing_truth.py`)
by LINE NUMBER, fitted from the LINE column so one misread line number
cannot mispair a row. Nine of nine characters are compared.

Twenty pages (3 37 56 67 72 86 93 96 112 117 120 125 130 138 146 164
170 180 192 196), 19 scored (p.146's LINE column unread); 713
locations and 657 binary half words with truth:

| reader | LOCATION cov / acc | BINARY h1 cov / acc |
|---|---|---|
| vis_full_200 | 73.6% / 99.24% | 85.4% / 97.86% |
| vis_full_300 | 75.0% / 97.94% | 84.6% / 98.38% |
| vis_full_400 | 75.7% / 98.89% | 84.0% / 98.55% |
| vis_crop_300 | 80.9% / 98.61% | 86.6% / 98.59% |
| vis_crop_600 | 81.3% / 96.72% | 86.3% / 97.35% |
| tes_crop_300 | 56.8% / 88.64% | 16.3% / 96.26% |
| tes_crop_600 | 53.4% / 90.03% | 19.5% / 93.75% |
| vote, >=2 readers agree | 92.3% / 99.24% | 96.5% / 98.90% |
| vote, >=5 readers agree | 62.8% / 99.78% | 65.9% / 99.08% |
| **Vision AND tesseract agree** | 56.7% / **99.75%** | 21.2% / **100.00%** |

**RESOLUTION IS NOT INDEPENDENCE.** When one Vision reader is wrong,
another Vision reader reads the SAME wrong value in 50-75% of cases
on the binary field (e.g. vis_crop_300 wrong 8 times, vis_crop_600
identical 6 of them). Voting across Vision resolutions mostly counts
one error several times, which is why the >=5 vote on binary is stuck
at 99.08%. **Tesseract almost never shares an error with Vision**:
one row in the whole sample -- p.56 line 48, LOCATION 003201.00, which
vis_full_400 and tes_crop_600 both read 002201.00 (3->2); every other
cell of the matrix is 0 of N, both fields. Coincidence between the
engines is therefore bounded by sample size, NOT zero, and the
"both agree" class below carries that one miss. The two engines fail
differently -- Vision on 7->1 (12) and 0->6 (4) only; tesseract on
0->6 (24), 2->1 (19), 1->0 (8), 1->6 (7), 4->0, 0->4, 5->0, 2->0.

**THE 7->1 CASES.** Five binary rows have EVERY Vision reader against
the deck (p.93 lines 4 and 6, p.96 line 10, p.130 line 11, p.196 line
22), all 7 read as 1. One of the five was inspected on the ink (p.93
lines 4 and 6, both visible in one crop): the 7's top stroke is faint,
and it reads as 7 to the eye. The deck is right there. The other four
were not inspected; their deck values are what the assembler
reproduces. A systematic error across resolutions is
caught only by a different ENGINE.

WHAT THIS LICENSES. For pages with no deck, a numeric field is
**settled** when Vision and tesseract read the same value (99.75% /
100% measured here); a field only Vision reads is a **candidate** that
still goes through rule 3. Coverage of the settled class is the
limit: tesseract reads only ~20% of binary half words, so the agreed
set is small. Raising tesseract's coverage (per-column crops,
`--psm 7` per row) is the next lever, measured the same way.

Two probe bugs found on the way, both mine: tesseract fuses LINE and
LOCATION into one token (`12003777.40`), so whole-token matching
reported 0% coverage; and an "eight digits, period dropped" rule then
grabbed the fused line number (`12003777`). Groups are now found
inside tokens and placed at their own x by character offset (30.06 px
per character on the 5100 px page).

## EVERY PAGE, BOTH VOLUMES (2026-11-03)

`tools/read_every_page.py` reads all 451 PDF pages (vol 1: 256, vol 2:
195) into `docs/vision/all/`: Vision whole page and Vision on the two
column crops (ONE engine), tesseract on the same crops at 600 dpi (the
other). `tools/listing_reading.py` turns that into
`docs/vision/listing_reading.tsv`, one row per printed LINE with
LOCATION and BINARY half word 1 and a status for each; the suite
(`tests/check_listing_reading.py`) keeps it whole, fresh and scored.

What had to change to leave vol 1:

* **The column frame is measured per page** (strap/listing_read.py
  `geometry`). Vol 2 is a different scan: 4499 px wide, LOCATION at
  x ~0.094 not ~0.202. LOCATION = the leftmost octal column with a
  BINARY partner 13-17 cells right; "leftmost strong column" alone
  picked BINARY on four vol 2 pages.
* **The row pitch is scanned, not estimated.** On vol 2 Vision often
  keeps only the tens digit of a line number ("46*" -> "4"), and the
  pairwise-median pitch came out 2-16 px. The pitch is scanned over its
  physical bound, the best-supported points are least-squares fitted,
  and a bare single digit d stands for d or 10d..10d+9.
* **The pitch bound** spans both measurements, which disagree: ink fit
  49.81-50.36 px, Vision line positions 49.58 (q10-q90 49.32-49.69).
* **Vision on column crops** nearly doubles its vol 2 coverage (PDF
  p.34: 45 location groups against 26 whole-page). Same engine: two
  Vision readings agreeing are still `vision-only`.

Measured against the 164 landed pages, nine of nine characters:

| status | LOCATION share / right | BINARY h1 share / right |
|---|---|---|
| agreed | 67.8% / 100.00% | 62.7% / 99.88% |
| agreed-out-of-order | 0.1% / 33% (the flag works) | -- |
| conflict | 7.3% / 99.05% either value | 4.6% / 99.59% either value |
| vision-only | 18.0% / 99.03% | 26.6% / 99.07% |
| tesseract-only | 2.2% / 93.70% | 1.5% / 89.74% |
| unread / not paired | 4.6% | 4.6% |

**Agreement is ~99.9%, not proof.** Six agreed fields were wrong, all
the same mechanism: a faint 7 that BOTH engines read as 1 (one broken 0
read as 6). The two LOCATIONS were caught by the order check; the four
BINARY ones were inspected on the ink and are in
`tests/vision_adjudicated.tsv`. Binary has no ordering to catch them.

**On the 241 printed pages with no deck** (197-439): 221 paired, 9,518
lines; LOCATION agreed 6,438, BINARY agreed 5,527. Headers: vol 1 is
PDF - 7 on all 230 read; vol 2 is +249 to PDF p.79 and +250 after
(printed 329 is not in the scan); printed 249 is missing too; no
number is read twice. 20 printed pages >= 197 do not pair (200 235
239 245 252 275 285 286 296 310 360 383 390 391 393 394 410 411 416
417); PDF vol 2 pp.190-195 (SYMBOLS NEVER USED, statistics) are not
listing pages.

## THE PROGRAMMING-ENVIRONMENT MANUALS (2026-11-03)

`tools/read_manuals.py` reads eleven manuals, 1,166 PDF pages, into
`docs/vision/manuals/STEM/pNNN.tsv` (every box, with width and height:
`tools/vision_ocr.swift --boxes`) and `docs/vision/manuals/STEM.txt` in
reading order: a page is cut into bands at each line that crosses the
gutter, and each band is read left column then right (C22-6729 p.10
has a full-width table above two-column prose). Language correction
OFF. **A finding aid, like docs/ocr/: not a source** (docs/ocr/README.md).

No ground truth exists for these, so the measure is comparative --
the share of words of four or more letters that are in
/usr/share/dict/words, and the share of Vision's distinct words on a
page that tesseract also found on that page:

| manual | pages | Vision dict | tesseract dict | Vision in tesseract |
|---|---|---|---|---|
| 22-6530-2 7030 Reference Manual | 175 | 78.2% | 78.3% | 98.3% |
| C22-6678-1 MCP Reference | 57 | 76.7% | 76.3% | 98.1% |
| C22-6728-1 MCP SAG | 280 | **74.3%** | 65.1% | 94.5% |
| C22-6728 MCP SAG | 270 | **73.8%** | 64.4% | 93.2% |
| C22-6729 STRAP II SAG | 211 | **75.4%** | 70.1% | 94.5% |
| C22-6751 FORTRAN IV | 37 | 76.3% | **none -- never OCR'd** | -- |
| C28-6129 STRAP II | 79 | 78.0% | 78.0% | 95.8% |
| C28-6379-0 MCP Loader | 24 | 77.8% | 77.9% | 96.7% |
| J22-6559 MCP User's Guide | 19 | 77.3% | 77.8% | 97.2% |
| N22-0085 MCP Ref update | 12 | 78.7% | 78.3% | 99.0% |
| X28-6131 MCP pocket card | 2 | 83.3% | 79.9% | 74.4% |

Vision is level with tesseract on the typeset manuals and clearly
better on the TYPEWRITTEN System Analysis Guides (+5 to +9 points),
which are the ones that specify MCP's and STRAP II's internals. The
FORTRAN IV manual has a text layer for the first time. Known misreads:
small capitals (FORTRAN's "READ" in small caps reads "BEAD").

## BINARY HALF WORD 2 AND THE STATEMENT DRAFT (2026-11-03)

**Half word 2** sits 14 cells right of half word 1 on both volumes (330
of 331 vol 1 groups, 216 of 220 vol 2). It is a third column crop,
read like the other two. On 1,628 landed full-word lines: agreed 72.4%
/ **100.00%**, vision-only 16.4% / 98.50%. On 3,511 HALF-word lines a
half word 2 was reported 14 times; the nine `agreed` ones are all
full-word instructions (CM, BB, BZB, LF, TI) whose deck `!CHECK`
records only half word 1 -- the truth is short, not the reading.

**NAME + STATEMENT** is read from bin + 28 to bin + 76.5 cells (the
NAME heading is at +31, the right-hand LOCATION heading at +77, on 199
/ 181 page headers). Folded onto the printer's character set (no
lowercase, accents or Cyrillic: Vision returns `В,2.0($15)` and
`CМОCОС`). Scored against the decks' source STATEMENTS, labels
dropped because decks rename them (`XSROOF` for printed `S ROOF`),
spaces and remark dropped: **41.5% of 6,001 lines** end with the
deck's statement. That is a FLOOR on Vision, not a measurement of it:
a deck is not always the printed text in its operands either (printed
p.156 line 28 prints `XW,S SCR PM($12),1,$`, the deck has
`XW,SSCRPM,1,$`), and those count as misses. Both sides are cut at the
first spaced `-` (the remark), so a statement such as `SYN, 1.0 +
XBSEND - XIPLBS` is compared only up to `XBSEND`. Typical misses: `(` read `I`/`1`, `(8)` read `[8]`,
`*` read `#`, `$0` read `$O`, a run of the statement dropped.

**There is no second engine for text.** Tesseract on the same crop
reads 8% of statements exactly (10 pages, 423 lines), and when it
agrees with Vision it is right 20 times in 26. So the statement column
is a DRAFT for rule 3, never a reading. The check on a draft is the
assembler: transcribe, assemble, and compare against the BINARY the
two engines read at ~99.9%. That closes the loop the image cannot,
including C against 0 in the hex byte.

## REPAIRING THE STATEMENT DRAFT (2026-11-03)

`tools/statement_repair.py` turns a draft into a candidate deck card
with constraints, not guesses: STRAP's operand grammar (`0.01$9)` ->
`0.0($9)`, `SCCHT.22` -> `SCCW+.22` since `SYM.22` is not STRAP), the
mnemonics the corpus uses (`CMIIII` -> `CM1111`), and the symbols known
from OTHER landed pages (82% of a page's symbols are; scored
leave-one-page-out so no page repairs itself).

Two findings changed the reading itself:

* **NAME and STATEMENT split by COLUMN.** The statement column opens
  38 cells right of BINARY h1 (7,409 mnemonic-opening tokens at +38,
  1,432 at +37/+39/+40; NAMEs at +29..+36). Guessing the split from
  the words failed because a one-letter name fragment `K` is also the
  mnemonic K.
* **Whole page vs text crop.** Vision on the NAME+STATEMENT crop at
  600 dpi keeps the one-letter fragments that open MCP names (`K K
  TAPE`, read `TAPE` off the whole page) but reads statements worse.
  Both are kept (`.vtext.tsv`), each for what it reads best.

Leave-one-page-out, 6,392 lines:

| | statement equals the deck's |
|---|---|
| raw draft (ends with it) | 42.9% |
| repaired, split by guess | 51.7% |
| **repaired, split by column, whole page** | **54.2%** |
| repaired, split by column, text crop | 50.9% |
| either of the two | 66.3% |
| the two agree (44.8% of lines) | 86.6% right |

**LABEL** (pp.100+, whose decks keep the printed name): 71.6% of 630
from the crop's NAME column, against 32% from the whole page.

The 12-point gap between "whole page" and "either" is the choice the
assembler makes: of two candidate cards, the one that assembles to the
agreed binary. That is the next lever and it is also rule 3's loop.
