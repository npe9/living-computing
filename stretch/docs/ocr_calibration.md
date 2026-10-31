# Reading the page number off every page, by OCR

A measurement record. Everything here was forced by a failure, and
every obvious choice was wrong at least once.

## Why bother

Transcription was going one page at a time, and **every page began by
rendering its header and confirming the number by eye**, because PDF
PAGE != PRINTED PAGE and `strap/mcp_crop.sh` warns in capitals that
the offset is NOT constant ("volume 1 duplicates pp.1-2 and carries
three blanks"). That is a manual step on a 256-page document, and it
is why the work kept stopping at whatever page attention ran out on.

`strap/mcp_survey.py` reads all of them in one run (2m30s wall, 5 jobs)
and writes `docs/mcp_page_map.json`.

## What the OCR had to survive

The field is the three glyphs after "PAGE NUMBER" in the page header.
In order, these were tried and measured:

| attempt | result on PDF 108, which prints **101** |
|---|---|
| 400 dpi, tight crop of the digits, `--psm 7`, digit whitelist | `1` |
| same crop, **no** whitelist | `Lol` |
| same crop upscaled 300% / 400% (`magick -resize`) | *empty* |
| same crop rendered at 600 / 900 dpi | *empty* |
| trim to ink + white border, with and without upscaling | *empty* |
| **400 dpi, crop WIDENED to include the words "PAGE NUMBER", no whitelist** | `PAGE NUMBER 101` |
| 400 dpi wide crop, on PDF 109 which prints **102** | `DAGE AUMBER 107` |
| **600 dpi wide crop** on the same page | `PAGE NUMBER 102` |

Three lessons, in the order they cost time:

1. **`Lol` IS THE WHOLE EXPLANATION.** This drum's `1` is an `l` and
   its `0` is an `o`. With a digit whitelist tesseract has nothing
   legal to map those shapes to, so it **drops them silently** and
   returns a short, confident, wrong number. The whitelist — the
   obvious way to help a numeric field — is what broke it.
2. **Upscaling and more dpi made it strictly worse** (empty, not
   wrong). Sharper glyphs in a mostly-white crop gave the segmenter
   less to work with, not more. The project's standing trick of
   "1200 dpi plus `-resize 300%`" is for *looking at a glyph*; it is
   the wrong instrument for *segmenting a line*.
3. **Context is what fixed it.** Keeping the words "PAGE NUMBER" in
   frame let the segmenter find a text line, and the digits came with
   it. The crop that works is the one that is *less* tightly targeted.

600 dpi, wide crop, no whitelist, `--psm 7`: **13 of 13** on PDF pages
103-115, whose printed numbers 96-108 are known independently from the
decks transcribed under them.

## Then the PARSER was wrong twice, which was worse

OCR text in hand, two "obvious" extractions each produced **confident
wrong answers**, which are far more dangerous than refusals.

**(a) "take the last run of digits" picks up the date.** The same crop
contains the distribution date `3/01`. When the page number failed to
OCR at all, the last digit run was `01`, so the tool reported **page 1**
with no indication anything had gone wrong. Pages 14 and 84 both did
this. *Fix: anchor on the word NUMBER and accept only digits after it;
return None otherwise.* A refusal is a result; a fabricated 1 is not.

**(b) A GLYPH-CONFUSION MAP MAKES IT WORSE AGAIN.** The natural next
idea is to map the drum's known confusions (`l`→1, `o`/`C`→0, `a`/`B`→8,
`T`/`q`/`?`→7) over the token. Measured, it *lowered* accuracy:

```
PDF 14   'PAGE NUMBER qT'    -> 77   (truth 7)
PDF 64   'PAGE NUMBER a7'    -> 87   (truth 57)
PDF 84   'PAGE NUMBER rai'   -> 81   (truth 17)
```

Each is a guess dressed as a reading. **The map was removed.** The
sequence below supplies the truth for free and does not guess.

## The check is global, because a local check can be fooled

The intended safeguard was "printed numbers run consecutively, so a
misread shows up as a break". Over 256 pages that found 23 suspect
pages — and it also produced **one false clean run**:

```
PDF  80- 83   offset +67   (printed 13-16)
```

Four consecutive pages, mutually consistent, all wrong: each is
printed 73-76 with the leading `7` read as `1`. **The same misreading
repeated consistently defeats a consistency check.** Scan quality is
correlated down a document, so this is not a freak event.

What is not foolable is the **global** picture, because the offset is
a property of the whole scan:

```
offset histogram over 240 clean reads:
  +7 : 226      +67 : 6      +2 : 2      +26,+1,+115 : 1 each
```

So: take the **modal offset**, accept the pages that agree with it,
and flag every page that does not. 226 of 240. The `+67` run loses,
as it should, on 226 votes to 6.

## What the map actually says

```
PDF 8 .. 256  =  printed 1 .. 249     offset +7 throughout
PDF 3, 4      =  printed 1, 2         the DUPLICATE printing
PDF 1,2,5,6,7 =  no page number       front matter and blanks
```

Two things worth noting about that result:

* **It confirms the filename.** `MCP_Mar63_001-249.pdf` contains
  printed 1-249, derived here from the pages' own headers rather than
  assumed from the name.
* **It confirms `mcp_crop.sh`'s warning, and narrows it.** That file
  says volume 1 "duplicates pp.1-2 and carries three blanks". The
  survey finds exactly that: PDF 3 and 4 are a second printing of
  pp.1-2, and five of the first seven pages carry no number. **But
  the offset is +7 for every numbered page in the volume** — the
  hazard is real and it is confined to the front matter. The `+7`
  that every deck has assumed is now verified on all 256 pages
  instead of spot-checked.

Residual: 12 misreads and 11 no-reads among 251 numbered pages (9.2%).
**All of them are detected**, and all are recoverable, because the
offset is known. None needs re-rendering.

## The standing rule, unchanged

`strap/mcp_ocr.py` already says it and it applies here: **this is a
cross-check, not a source.** The LOCATION-column OCR in the survey runs
at mcp_ocr.py's own window and resolution, whose measured accuracy is
roughly 85% of lines, and the survey uses it only to answer "does this
page carry locations, about how many, over what range" — questions that
losing one line in seven does not change. A deck is still transcribed by
reading the page.
