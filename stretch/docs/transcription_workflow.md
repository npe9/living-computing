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
# LOCATION, NAME and STATEMENT together -- one read
pdftoppm -f $((P+7)) -l $((P+7)) -r 400 -png -x 500 -y 800 -W 4200 -H 2950 \
         docs/MCP_Mar63_001-249.pdf /tmp/p${P}_left
# BINARY OUTPUT at 900 dpi -- B and 8 differ by one stroke
strap/mcp_crop.sh $P code 1 ; strap/mcp_crop.sh $P code 2
```

Montage multi-band renders into ONE image before reading:
`magick montage a.png b.png -tile 2x1 -geometry +10+10 out.png`.
Six reads become one.

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

### 3. Write the deck

`decks/mcp_bootstrap_pNN.strap`, in the house format: a header saying
what the page is and which PDF page it came from, the statements, and
the printed listing recorded as comments

```
!   line  8  004423.40  000000.30 00                   CNOP
```

so `listing_oracle.py` can check them.

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
