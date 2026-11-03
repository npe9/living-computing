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
at 99.08%. **Tesseract shares no error with Vision**: 0 of 37, 0 of
35, ... in every cell of the matrix, both fields. The two engines fail
differently -- Vision on 7->1 (12) and 0->6 (4) only; tesseract on
0->6 (24), 2->1 (19), 1->0 (8), 1->6 (7), 4->0, 0->4, 5->0, 2->0.

**THE 7->1 CASES.** Five binary rows have EVERY Vision reader against
the deck (p.93 lines 4 and 6, p.96 line 10, p.130 line 11, p.196 line
22), all 7 read as 1. Inspected on the ink at p.93: the 7 has a broken
top stroke and reads as 7 to the eye; the deck is right, and the
assembler reproduces it. A systematic error across resolutions is
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
