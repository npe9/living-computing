# Transcribing an MCP page, as a loop that does not stop

Written 2026-10-30 after a session that kept halting between pages. The
halts were never a decision that needed making -- they were the same
orientation work done again from scratch each time. This is that work,
written down once.

**The goal is pages per session, not a page per session.**

---

## The loop

### 1. Confirm the page and find its columns

```sh
python3 strap/mcp_columns.py 83
```

Prints the PDF page, the image size, and every column run it measures
from the page's own ink. **It replaces guessing at geometry**, and it
prints the reminder to confirm the page's own `PAGE NUMBER` header,
because the PDF offset is +7 for the pages seen so far and the tool
does not know that for pages it has not seen.

The column order, left to right, is always:

```
LINE | LOCATION | BINARY OUTPUT | NAME | STATEMENT | (comment)
```

### 2. Render and read, in two images not nine

```sh
# EVERYTHING but the line numbers, in one read.  y=480 is LINE 1 --
# see the warning below; 800 starts at line 6 and silently drops five.
pdftoppm -f $((P+7)) -l $((P+7)) -r 400 -png -x 900 -y 480 -W 4300 -H 4100 \
         docs/MCP_Mar63_001-249.pdf /tmp/p${P}_all
# BINARY OUTPUT at 900 dpi -- B and 8 differ by one stroke
strap/mcp_crop.sh $P code 1 ; strap/mcp_crop.sh $P code 2
```

Montage multi-band renders into ONE image before reading:
`magick montage a.png b.png -tile 2x1 -geometry +10+10 out.png`.
Six reads become one.

> **START AT LINE 1, WHICH IS y=480 AT 400 dpi.**  An earlier version
> of this file said `-y 800`, which starts at LINE 6.  On printed p.84
> that dropped lines 4 and 5 -- `T UNXW XW,TUNATB,0,$0` at 004653.00 and
> `T UNATB DRZ(BU,64),(50)` at 004654.00 -- and their absence turned
> into a phantom "51-word gap" between p.83's end and p.84's first
> storage, which was then written up as unexplained.  The XW plus the
> fifty-word reservation IS the 51 words.  Nothing was unexplained; five
> lines were simply not on the screen.

> **READ THE WHOLE COLUMN, NOT BAND 1.** Twice in one hour on
> 2026-10-30 a page was described from its top third and the
> description was wrong -- p.85 was called "definitions, no code" when
> its lines 29-47 are code, and T MOVE was estimated three pages out by
> averaging over pages that compile nothing. A window onto an artifact
> is not the artifact.

> **A DD OR SYN LINE PRINTS A DATA DESCRIPTION, NOT MACHINE CODE**, in
> the BINARY OUTPUT column -- `BU,100,10` is mode BU, length 0o100=64,
> byte size 0o10=8. That is the column working correctly on a
> definitions page, not the crop landing in the wrong place.

### 2a. Get a SECOND reading, by machine

```sh
python3 strap/mcp_ocr.py 86        # tesseract on the LOCATION column
```

Diff its output against the locations you read by eye. **It is a
cross-check and not a source** -- measured on printed p.86, tesseract
reads about 85% of the column correctly and drops a digit every few
lines, so transcribing from it would put a wrong word in the image.
What it is good for is DISAGREEMENT: on p.86 it flagged line 24 as
`004757.60` where the eye read `004757.00`, one zoom settled it (the
eye was right), and the other eighteen rows agreed. Two independent
readings of the same column cost one command and turn a whole-page
re-read into one zoom.

> **NOT /tmp FOR THE INTERMEDIATE PNG.** `pdftoppm` writes it and
> `tesseract` then reports *"image file not found"* for the file that
> demonstrably exists -- the two processes do not see the same `/tmp`
> here. `tempfile.mkdtemp()` honours `TMPDIR` and both see it.

### 3. Write the deck

`decks/mcp_bootstrap_pNN.strap`, in the house format: a header saying
what the page is and which PDF page it came from, the statements, and
the printed listing recorded as comments

```
!   line  8  004423.40  000000.30 00                   CNOP
```

so `listing_oracle.py` can check them.

### 3a. Write the page's verifier -- this is the step that makes it stick

Every transcribed page has one: `tests/verify_mcp_bootstrap_pNN.py`,
73 of them so far. It is short and always the same shape:

```python
from listing_oracle import check_rows, finish
from strap_asm import assemble
prog = assemble(open("../decks/mcp_bootstrap_p84.strap").read())
SYMBOLS = {"TUNXW": "004653.00", "TUNATB": "004654.00", ...}
ROWS = [("004654.00", "000062.00", "line 5  T UNATB DRZ(BU,64),(50)"), ...]
finish(check_rows(prog, ROWS, SYMBOLS, label="MCP p.84 "))
```

`check_rows` does BOTH halves -- it checks every symbol against the
LOCATION column and every row against the BINARY OUTPUT column -- so
the one call is the whole oracle. A DD printed as bare octal digits
takes a fourth element, its width in bits.

Register it in `tests/run_tests.sh` beside the others:

```
run "... printed p.84, bit-exact (MCP_Mar63 PDF p.91)" python3 verify_mcp_bootstrap_p84.py
```

> **SIGN IS PRINTED AS A SUFFIX.** A negative SYN prints `000001.00-`,
> magnitude then sign, so a check that compares a signed bit count to
> that string reports a mismatch that is not one. printed p.84 line 23's
> `T JCNME SYN(BU,48,6),-1.0` is -64 bits and prints `000001.00-`.

### 4. Join it to the image -- two mechanical edits

`strap/mcp_image.py`:

* `MCP_IPL_PAGES = [... for n in range(15, 81) ...]` -- widen the range
* `NO_DECK_PAGES = {47, 59, 60}` -- add any page that compiles nothing

A page that compiles nothing still needs the second edit, or the build
will look for a deck that does not exist.

### 5. Check, in this order

```sh
python3 -c "from mcp_image import build; ..."      # every symbol on its printed address
python3 strap/listing_oracle.py ...                # every half-word against the printed binary
cd tests && ./run_mcp_boot.sh StretchMcpBootTb     # how far the boot gets now
./run_tests.sh                                     # the whole suite
```

**The address check is the cheap one and it catches most of it.**
Assemble the page alone and compare each symbol against the LOCATION
column. On printed p.83 this caught an omission immediately: 14 of 16
symbols matched and the two that did not were short by exactly the two
words of the five lines left out.

### 6. Commit the page, then take the next one

---

## Gotchas that have cost a page each

**In entry mode the space after the comma is DATA.** `(AX)DD` and
friends take their datum literally, so

```
(AX)DD(BU,24,6), IOD X    -> 30 bits   WRONG
(AX)DD(BU,24,6),IOD X     -> 24 bits   right
```

and every symbol after the first one lands six bits late. The trailing
`X` is the terminator the assembler demands -- it errors with
*"entry-mode datum is not terminated by 'X'"* without it -- and is not
a character of the datum. A 48-bit field of 6-bit blanks is written as
seven blanks and the X.

**The address check finds this in one second.** Assemble the page alone
and compare every symbol against the LOCATION column; on printed p.83
the first run was 23 of 27 with the four misses starting exactly at the
line after the bad operand, which names the line AND the amount.

**`build()` is the IPL bootstrap, `build_mcp_ipl()` is the MCP body.**
`PAGES` is pp.2-14 and goes on the tape through `mktape.py`;
`MCP_IPL_PAGES` is pp.15-onward and is what MCP moves into place. A new
MCP page goes in the SECOND list, and looking for its symbols in
`build()`'s symbol table finds nothing and means nothing.

---

## What is known about the pages ahead

```
p.81  compiles nothing          -> NO_DECK_PAGES
p.82  compiles nothing          -> NO_DECK_PAGES
p.83  004627.40 .. 004652.00    constants, index SYNs, a 15-word save area
p.84  004736.00 .. 004737.05
p.85  004743.00 .. 004752.14    (lines 29-47; 6-23 are field offsets)
p.86  004754.00 .. 004765.76
p.87  004767.00 .. 005013.00
p.88  005014.00 = T MOVE
```

p.80 ends at 004627.00 and p.83 begins at 004627.40, so the trail is
contiguous and each page lands against the one before.

## The rules that do not bend

* **Transcribe, never infer.** A value not read off the page does not
  go in the deck. The merged image is what every MCP measurement rests
  on, and a wrong word in it is invisible until it costs an afternoon.
* **Record the printed listing in the deck**, so the oracle can check
  the page later without re-rendering it.
* Encodings and semantics come from primary sources, cited by page.
