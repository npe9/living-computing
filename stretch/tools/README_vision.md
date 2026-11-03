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
