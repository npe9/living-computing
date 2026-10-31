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

> **THREE GLYPH PAIRS BREAK ON THIS DRUM, AND THE THIRD IS THE WORST.**
>
> * **B vs 8** -- they differ mainly in one vertical stroke, which is the
>   first thing a worn drum loses. `mcp_crop.sh` renders the code column
>   at 900 dpi for this reason.
> * **O vs C** -- a worn O has a break in its upper right and reads as C
>   when zoomed ALONE. printed p.87's label read `T WCRM` in isolation
>   and is `T WORM`: the references on the same page print a closed O
>   identical to the one in `T BOID` a line above.
> * **C vs D, AND THE ORACLE CANNOT CATCH IT.** This drum prints D with
>   the bowl worn through, so at 400 dpi a D reads as a C. On printed
>   p.93 six glyphs came back D and three first-pass readings were
>   wrong: `T MDK2`, `TMDK1A` and `TMDK` had all been read with a C.
>   **The discriminator is the LEFT side**: C and 0 are round with no
>   stem; D has a straight vertical left stem and squared corners.
>
> **THE CALIBRATION GLYPH IS IN THE SAME ROW, IN AN OCTAL FIELD.**
> A half-word prints as `oooooo.oo HH` -- the first two fields are
> OCTAL, so they can only hold 0-7. **A round glyph in an octal field
> is therefore a 0 with certainty, whatever it looks like**, and it
> sets the ink level for that row's hex byte a couple of characters
> away. Printed p.95 line 49 reads, to the eye at 900 dpi:
>
> ```
> 005356.40   COC000.64 82   014000.2C BC      LFT,T IODCT(T MXA)
> ```
>
> `COC000` and `.2C` are `000000` and `.20` -- a C cannot occur in
> either field -- so this row prints 0 as an open C three times before
> it reaches the byte. Line 53's `COC011.CC 80` and line 55's
> `C70C000.00` print the same way.
>
> What this establishes is NOT that the byte is `B0`; it is that **on
> this page an open round glyph is a perfectly ordinary 0**, so "it
> looks like a C" carries almost no information. The asymmetry runs
> one way: ink dropout can open a closed glyph but never closes an
> open one, so an observed C may be a damaged 0 while an observed 0 is
> never a damaged C.
>
> **BE PRECISE ABOUT WHAT THE GAUGE IS.** It is not a per-row ink
> level -- ink varies per CHARACTER. Printed p.85 line 12 prints the
> comment `-ORIGINAL ARC` with a clean closed O and the name beside it
> as `T CRARC`, open, in the same row off the same drum. So an octal-
> field C tells you the page drops ink on round glyphs; it does not
> license converting any particular C to a 0.
>
> Comparing a byte against zeros in OTHER rows is weaker still, and is
> exactly how p.95's first reading concluded `BC` on lines 49 and 53,
> against an assembler that was right.
>
> **THE COMMENT COLUMN IS ENGLISH, AND THAT MAKES IT AN ORACLE.**
> A misprinted letter inside a known word is visible as a misspelling.
> Printed p.85 line 11 prints the name `T FMCDE` and the comment
> `-FILE MCDE`: the word is MODE, so both are O's and the symbol is
> `T FMODE`, not the `TFMCDE` the deck carried. Printed p.84 line 48
> is `T IODK` -- four letters, I O D K -- against the deck's
> `TIODCK`; its comment `-THE IOD COUNT` confirms the O. Neither
> error could fail a test, because `listing_oracle` checks LOCATIONS
> and BINARY and never label SPELLINGS, and both symbols happened to
> be referenced only inside their own deck. **When a label looks odd,
> read its comment.**

> When the two still disagree, the STATEMENT column is the tie-breaker,
> because it is what produced the bits: `LFT,T IODCT(T MXA)` has no
> second operand, and the low nibble of a VFL full word is `i2`, the
> OFFSET INDEX from the `OF7(I')` operand (`vflAddrOf`: `w[3:0]`, IBM
> bits 60-63). No `(I')` in the statement means `i2` is 0 means the
> byte ends in 0. Assemble the variant and look -- adding `, 0(T MLXA)`
> to that statement turns `B0` into `BC` and nothing else changes.

> The reason C/D is the dangerous one: `listing_oracle` checks LOCATIONS
> and BINARY, never label SPELLINGS. A misspelled label that nothing
> references assembles perfectly and is simply wrong. What caught it on
> p.93 was an INTERNAL INCONSISTENCY -- two lines read as the same name
> `TM6C` yet compiled to different addresses -- not an external check.
> A symbol another page references is safe (the merge would fail on an
> undefined symbol); one that nothing references rests on ink alone, so
> read those at 1800 dpi against a known-good instance of each candidate.

> **AND WHEN THE AMBIGUOUS GLYPH IS IN A MNEMONIC, HAND BOTH
> READINGS TO THE ASSEMBLER — ONE OF THEM MAY NOT BE AN
> INSTRUCTION.** This is cheaper than the manuals and strictly
> decisive when it fires. printed p.134 line 44 reads `BOPZ` or
> `BCPZ` depending on how its round glyph is taken, and the volume
> OCR is no help: it carries the same card six times, four as BOPZ
> and two as BCPZ. Measured:
>
> ```
>   BOPZ  assembles, and prints the page's own 216607.47 C6
>   BCPZ  "unknown mnemonic 'BCPZ'"
> ```
>
> The operation set is small and fixed, so an O/C or B/8 confusion
> usually produces a string that is not an operation at all. Note the
> tell this does NOT give you: both spellings being valid means the
> test is silent, not that either is right — `C0011` and `C0001` are
> both real. Use it as an eliminator, never as a confirmation.

> **WHEN THE INK CANNOT SETTLE A NAME, GREP THE MANUALS. IT IS THE
> CHEAPEST CHECK IN THIS REPOSITORY AND IT IS ROUTINELY DECISIVE.**
>
> `docs/ocr/` holds OCR text for every manual. The listings are a
> drum print and ambiguous; the manuals are typeset and are not. One
> `grep` answers what an afternoon of 1800-dpi crops cannot:
>
> ```
> $ grep -o 'STIC\|STIO' docs/ocr/C22-6728*_MCP_Sys_Analysis_Guide.txt | sort | uniq -c
>   75 STIC
> ```
>
> Zero STIO, in two revisions of a different document -- and the
> prose says what it is: *"the saved IC is stored in STIC"*, with
> the listing's own statement form printed at
> *"(SIC,STIC; B,SIFAD)"*. **STIC is STored Instruction Counter.**
>
> That question had resisted everything else. Printed pp.110 and 111
> read the last glyph C, printed p.112 read it O, and neither reading
> was safe: this drum opens round glyphs constantly -- p.110's own
> lines 35 and 36 are the SAME instruction, both compiling
> `000000.30 00`, printed `NCP` and `NOP` -- so "it looks like a C"
> carries almost no information, and a count of nine known glyphs on
> printed p.106 had tesseract reading all five certain O's as C.
> Shape was exhausted. The manual took one command.
>
> **Grep the ADDRESS as well as the name.** A symbol's name is the
> OCR-fragile part and its octal address usually is not, so
> `grep 215265` finds defining cards that `grep STIC` misses.
> `docs/ocr/MCP_Mar63_001-249.txt` is a full-volume OCR of the
> listing itself and is under-used for exactly this: it is far too
> garbled to transcribe from, and it is an excellent index of where a
> symbol is DEFINED on a page nobody has opened yet.

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

### A BIT OFFSET IS OCTAL INSIDE `(8)`, DECIMAL ONLY WHEN BARE

Every `SLC` in these decks is written `(8)NNNN.FF`, and **inside an
`(8)` literal BOTH parts are base 8**, so the bit offset is written
EXACTLY AS THE PAGE PRINTS IT. Measured through `eval_expr`:

```
  (8)5450.40  -> word 5450 . bit 40      (0o40 = 32 decimal)
  (8)5450.32  -> word 5450 . bit 32      (0o32 = 26 decimal)
  (8)5450.8   -> ERROR: invalid literal for int() with base 8: '8'
      5450.32 -> word 12512 . bit 40     (both parts decimal)
```

The `.8` error is the proof: 8 is not an octal digit, so the fraction
really is parsed in base 8.

**The rule "a STRAP bit offset is written decimal and printed octal"
is TRUE ONLY FOR A BARE DECIMAL LITERAL.** Applied to an `(8)` SLC it
lands six bits low — `(8)5450.32` for a printed `.40`. That wording
was given to four transcription agents in their briefs on 2026-10-30
and it was wrong; it is recorded here so it is not repeated. No deck
was corrupted by it, because every landed `SLC` writes the printed
octal (`(8)5154.40` for p.91's first row at 005154.40), but the error
can HIDE: on printed p.98 a wrong `SLC` still produced the right
address for the next row, because a half-word instruction realigned
the counter. A misread origin is not guaranteed to show up as a
failing check.

> **SAME-ROW CALIBRATION IS NECESSARY BUT NOT SUFFICIENT.** Two rows
> found while transcribing pp.97 and 98 drop ink in one field and not
> another, within one row off one drum:
>
> * printed p.97 line 10 prints its octal field as `.CC` for `.00`
>   while its hex byte prints a clean closed `0`.
> * printed p.97 line 9's byte reads `FC` at 1200 dpi and its own
>   octal field `001000.36` is well inked, so the row's calibration
>   points the WRONG WAY. It is `F0`, settled by printed p.18, which
>   prints `CM1111(BU,1)` six times and every one is `001000.36 F0`.
>
> So an octal-field C tells you the page CAN drop ink; it never tells
> you a particular glyph did. Settle the byte on what produced it --
> the statement, the same instruction on another page, or the index
> rule (the low nibble is `i2`, 0 when there is no second operand).

### A SIC/BRANCH PAIR CAN STRADDLE A PAGE BREAK

`SIC` must be immediately followed by a half-word branch (Reference
Manual printed p.41), and `strap_asm` enforces it:

```
  SIC alone     -> "SIC must be immediately followed by a half-word branch"
  SIC + branch  -> assembles
```

That is right — real STRAP read the next CARD and never saw a page
break. But a LISTING PAGE can end between the two. printed p.131's
line 48 is `Y FX AD  SIC,Y PREL` at 216440.00 and its branch is
printed p.132's line 1.

**Do not invent the branch to make the page assemble.** A stub would
deposit a word at 216440.40 that this page does not print and that
the NEXT page owns, and the deck would then disagree with p.132 for
as long as nobody looked. The right move is what p.131 did: leave the
orphaned `SIC` out of the deck, carry it in the listing block with no
`!CHECK`, and say why.

**Bound the loss explicitly** rather than leaving it open:

* its bits are the SAME STATEMENT as four other rows on that page,
  all of which ARE checked;
* its location is pinned by the deck's counter arriving at exactly
  216440.00; and
* printed p.110 independently SYNs `YFXAD` at `(8)216440.0`.

So the row is unchecked and nothing about it is unknown. When the
neighbouring page lands, the pair can be rejoined if anyone wants it
under a single check.

### WHAT THE ORACLE CANNOT SEE

`listing_oracle` compares assembled bits against printed bits, and
that is a strong check — but a deck can be wrong in ways that produce
the *same printed word*, and those are invisible to it forever. Three
are known, all measured, and they bound what "bit-exact" means here.

**1. AN EXTERNAL BACK-DERIVED FROM A BRANCH OR AN `LVI` IS KNOWN ONLY
TO THE HALF WORD.** Most decks SYN their externals by reading the
address out of a printed instruction. Measured, with the symbol's bit
offset varied and everything else fixed:

```
  SYN value        LVI,$1,T prints    B,U prints
  ...216577.00     216577.03 01       216531.10 00
  ...216577.03     216577.03 01       216531.10 00
  ...216577.37     216577.03 01       216531.10 00     (bit 31)
  ...216577.40     216577.43 01       216531.50 00     (bit 32)
```

Every offset from 0 to 31 encodes identically; only bit 32, the
half-word select, shows. So `YINDTR` at `216577.00` and at
`216577.03` are indistinguishable, **and so is every other value in
between**. Writing `.00` is a CONVENTION, not a reading. The printed
`.03` on an `LVI` and the `.10` on a branch are operation bits, not
address bits — p.110 found the same for `BD`, which prints `.04`.

The practical rule: **when you SYN an external off a printed
instruction, say in the deck that its bit offset is unobservable.**
Do not let a passing `!CHECK` imply you read it.

> **BUT THE HALF WORD ITSELF IS CHECKED, AND THAT CATCHES REAL
> ERRORS.** Bit 32 shows, so a symbol that is really at `.40` and
> written `.00` FAILS. printed p.122 wrote `.0` for two externals and
> the oracle refused both — `K ST CS` is 216272.40 and `K RELAY` is
> 216314.40 — which is why writing `.0` by habit is safe to do and
> safe to check. The invisible part is only the bit WITHIN the half
> word.

**2. A HARD `SLC` CANNOT DISAGREE WITH THE ARRIVING COUNTER.** It
overrides it, silently. printed p.111's agent tested this rather than
asserting it: setting `SIT` to `(8)215024.0` moves all forty-eight of
that page's locations together and **all forty-eight `!CHECK` rows
still pass**. So a deck whose page prints `SLC,$` and which writes a
hard origin instead is asserting that origin, not checking it. Where
a page prints `SLC,$`, the join to the previous page has to be
compared BY HAND — and pp.101 and 108 carry an `SLC` their pages do
not print at all.

> **BUT A PRINTED `SLC,$` IS THE BEST FORWARD-JOIN WITNESS THERE IS,
> and it is the PAGE that supplies it, not the deck.** An `SLC`
> emits nothing, so **its printed LOCATION _is_ the counter arriving
> from the previous page** — a free, independent reading of the join,
> printed by IBM's own assembler. printed p.114 line 4 is
> `215163.00 *  SLC,$`, which is what confirms that printed p.113's
> twelve interrupt slots end at 215162.40 and nothing fell off the
> bottom of that page.
>
> So the loss is entirely in the SUBSTITUTION. A deck that writes a
> hard `SLC,(8)nnnn.` for a printed `SLC,$` throws the witness away
> and asserts the value instead. **Record the printed location in the
> `!CHECK` note even though no check can use it**, and when the
> neighbouring page lands, compare the two by hand — it costs one
> line and it is the only thing that closes the join.

**3. A `!CHECK` THE DECK NEVER WROTE IS NOT A FAILURE.**
`verify_mcp_page.py` checks what the deck DECLARES, so a deck
declaring two checks for a twenty-four-row page passes having
verified almost nothing. `strap/mcp_coverage_report.py` compares each
deck against an independent OCR of its page for exactly this, and
printed p.86 was checking six of its rows and none of the scan-table
data beside them.

**4. A VFL OFFSET IS PINNED ONLY MOD 128.** The offset field is seven
bits (IBM 44-50), so it wraps. Measured, varying nothing else:

```
  +(BU,18), X, 55     ->  022033.00 80 022033.60 10
  +(BU,18), X, 183    ->  022033.00 80 022033.60 10
  +(BU,18), X, -73    ->  022033.00 80 022033.60 10
```

printed p.129 line 14 computes `55-S DD` into such a field, so that
row establishes only `S DD` ≡ 0 (mod 128). `S DD = 0` exactly comes
from printed p.108's defining card, a different page. This is not the
half-word gap in another costume: there the invisible part is the low
bits of an address, here a fully-specified value wraps.

> None of these is a defect in the oracle. They are the edge of what
> comparing one word against one word can establish, and the answer
> to all four is the same: **a second, independent reading** — the
> next page's first location, a manual, or the page's own English.

> **AND BE SURE THE SECOND READING IS INDEPENDENT.**
> `docs/ocr/MCP_Mar63_*.txt` is an OCR of THE LISTING ITSELF, so the
> OCR of page N is not a witness for page N — it is the same ink read
> by a worse reader, and it inherits every one of this drum's
> confusions. printed p.129 nearly recorded `C Q2BIG` as having a
> second witness on printed p.123; the "witness" was p.123's OCR of
> p.129's own card. The volume OCR is an excellent index of where a
> symbol is DEFINED on some OTHER page, and worthless as corroboration
> of the page it came from.
>
> The same applies to a count: four OCR hits spelling a name one way
> and two the other is not a 4-2 vote, because all six readings share
> the drum and the reader. printed p.134's `BOPZ`/`BCPZ` split exactly
> that way and was settled by the assembler instead.
