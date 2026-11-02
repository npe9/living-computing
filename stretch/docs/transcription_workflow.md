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

**AND READ THE HEADING ROW'S OWN `LOCATION` FIELD, FAR TO THE RIGHT.**
The column-heading line repeats the word `LOCATION` at the right-hand
end and prints the page's origin WORD after it — IBM's own assembler
stating where the page begins:

```
LINE   LOCATION      BINARY OUTPUT      NAME   STATEMENT      LOCATION   217056
```

It is the cheapest join check in the volume. It gives no bit offset,
so it does NOT replace line 1 and it cannot settle a `.00`/`.40`
question; what it does is confirm the origin word independently of
your own reading of the LOCATION column. Eighteen decks had found it
one at a time before it was written down here.

> **IT IS LINE 1'S LOCATION, AND IT IS BLANK WHEN LINE 1 COMPILES
> NOTHING.** Not the page's origin -- line 1's. Measured over
> sixteen pages with no counterexample. BLANK on printed pp.83, 144,
> 145, 146, 147, 149 and 151, every one of which opens with an
> asterisk banner or a comment card carrying no location. NUMBERED
> on pp.95, 120, 125, 133, 136, 138, 139, 141, 142, 143, 148, 150
> and 152, every one of which has a located line 1 -- p.148 reads
> `217432` against a line 1 at 217432.40, p.152 reads `217573`
> against a line 1 at 217573.00.
>
> **printed p.147 is the case that discriminates, and it is the one
> to remember:** its field is BLANK although the page is full of
> located rows, because its first located row is line 4
> (`217371.70 * SLC,$`) and not line 1. So the field is NOT "the
> page's first location", and a blank does not mean the page has no
> origin -- it means line 1 was a banner.
>
> An earlier guess -- that the field is dropped on pages carrying
> their own `SLC` -- was tested against the landed decks and
> **refuted** (pp.83 and 95 both carry scaffolding-only SLCs and
> differ). The reading above supersedes it.
>
> This matters because tesseract will happily invent digits out of
> the dashed rule line that runs through that field: on printed p.83
> it returned `000222`, confidently, from blank paper. Anchor on the
> word and refuse when no digits follow, the way
> `strap/mcp_survey.py`'s `page_number()` does. **A reader that
> guesses here is worse than no reader at all**, because this field's
> whole value is being an independent witness.


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

### 2a0. THE SURVEY'S LAST ENDPOINT IS WHERE THE OCR STOPPED

Every page this session has "disagreed with the survey", and the
reason is not that the survey reads badly at random. **Its upper
endpoint is `mcp_ocr`'s LAST READABLE ROW, not the page's last row.**
Diagnosed on printed p.181 and then confirmed directly:

```
  $ python3 strap/mcp_ocr.py 181   ... last line read: line 42  221132.40
  cached survey row for p.181:     221132.40          <- identical
```

p.181 has 56 lines; the OCR reads 27 of them and gives up at line 42.
So the survey's `last` field is a LOWER BOUND IN THE SAME WAY the row
count is, and for the same reason. **Both endpoints and the count are
floors.** The FIRST endpoint is usually right when line 1 is located
and wrong when line 1 is a banner.

And the cached `survey_report.txt` in a scratchpad can be staler than
the tool: printed p.171's transcriber re-ran `mcp_survey.py` and got a
first endpoint the cached file did not have. **Re-run the tool rather
than quoting the cache.**

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

### 2b. Settle a doubtful glyph, cheapest first

This drum confuses `O`/`C`, `C`/`D`, `B`/`8`, `O`/`0`, `C`/`0` and
`G`/`Q`, and dropout OPENS a closed glyph far more often than ink
CLOSES an open one. That asymmetry is a hint, not a proof. Work down
this ladder and stop at the first rung that answers:

1. **The comment column.** It is English prose, a different
   vocabulary from the statement field, and it is right there in the
   same row. printed p.138 settled `G DIAR` this way.
2. **`grep docs/ocr/` for the typeset manuals.** Different ink,
   different press, genuinely independent of the listing drum.
   `STIC` vs `STIO` was settled outright: 75 hits for `STIC` across
   two revisions, zero for `STIO`.
3. **Hand both readings to the assembler.** This is an ELIMINATOR
   and NEVER a confirmation — if one reading is not an instruction
   at all, the other wins; if both assemble, you have learned
   nothing. `BZR` fell this way ("unknown mnemonic").
4. **THE SAME STATEMENT PRINTED TWICE ON ONE PAGE.** The strongest
   rung, and the cheapest once you notice it. printed p.144 lines 14
   and 26 are the same instruction compiling to the same word,
   printed `LV,0,0.0($1)` and `LV,C,C.C($1)`; lines 17 and 28 repeat
   the trick with `$IND`/`$INC`. One page, one drum, one instruction,
   open and closed glyphs in the SAME CHARACTER POSITION — which is
   what makes it stronger than the octal-field argument below, since
   it holds position and context fixed and varies only the ink.
5. **The octal-field argument.** A `C` in a field that can only hold
   an octal digit is a damaged `0`, because the machine cannot
   produce a `C` there. printed p.143 line 5 prints
   `215335.CC 80 001000.CC` — four impossible `C`s — so that row is
   demonstrably dropping ink and its doubtful byte is a `0`.

> **AND NEITHER WIDTH NOR OPENNESS SEPARATES `O` FROM `0` FROM `C`
> ON THIS DRUM.** Measured on printed p.184 at 1600 dpi, over every
> instance whose identity is already known from its English word --
> ink-segmented run widths:
>
> ```
>   letter O   124 120 104 112 108 120
>   letter C   112 116 116 112 116 116
>   digit  0   112 108 116 108 100 112      <- complete overlap
> ```
>
> and openness is no better: **four of six known O's print OPEN and
> four of six known 0's print CLOSED.** Template matching scored 0.59
> against 0.54, which is noise. printed p.197 measures the same.
>
> **So "dropout opens a closed glyph and never closes an open one" is
> a HINT ABOUT A SINGLE CHARACTER'S DAMAGE, not a way to tell these
> three apart.** Several pages have leaned on it as though it were;
> it is not a reading. Every round glyph settled in this corpus was
> settled by another page, a manual, or the compiled word -- never by
> shape. Rungs 1-5 exist because of this measurement.

> **INK VARIES PER CHARACTER, NOT PER ROW.** Rung 5 is about the row
> only far enough to show the row CAN drop ink; it does not license
> "this row is clean, therefore every glyph in it is". printed p.85
> line 12 prints `-ORIGINAL ARC` with a clean closed `O` beside
> `T CRARC` with an open one, in one row. printed p.143 used rung 5
> correctly and it called two rows on the same page OPPOSITE ways.

> **AND SETTLE A BYTE ON WHAT PRODUCED IT.** The best witness for a
> doubtful byte is usually not ink at all: it is another row on the
> page running the same operation with a known operand. If the
> statement cannot produce the byte you think you read, you misread
> the byte — or you misread the statement, and that is worth finding
> out before the page lands.

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

### 3a2. Hand the assembler the PRINTED form, and let a bad row FAIL

Every wrong-answer bug this corpus has produced was found because a
page was written AS PRINTED and allowed to fail, rather than
normalised into something that assembles. Four of them, all silent,
all invisible to every check but a row's own `!CHECK`:

* a blank inside a radix literal compiled the wrong word;
* a written-minus `-I` fired on the legitimate `+I`, inverting a sign;
* an empty address field dropped the OFFSET that followed it;
* **a blanked NAME lost its data description**, so a statement with no
  dds of its own compiled with LENGTH 0 while its ADDRESS resolved
  perfectly (printed p.164, `CM1111,S CTL(EU)`).

So: try the printed spelling first, always. If it is refused, that is
a FINDING and belongs in the report. If you must substitute to keep
the location counter honest, label it loudly and record the printed
form beside it.

> **A ROW WHOSE STATEMENT AND `!CHECK` CONTRADICT EACH OTHER IS NOT
> LOUD, IT IS SELF-CONTRADICTORY.** Leaving the printed statement with
> a printed check that it cannot produce is the right move -- the row
> fails and names the defect. Writing a statement you know is wrong
> AND a check that matches your wrong statement verifies nothing.

> **THE ONE CASE WHERE FAILING IS NOT ON OFFER: A DUPLICATE LABEL.**
> `strap_asm` refuses a repeated name outright -- `symbol 'X' multiply
> defined` -- and assembles NOTHING, so the whole page checks nothing
> rather than one row failing. printed p.166 prints `ZFRO5` on two
> cards at two addresses and had to carry a `ZFRO5DUP` stand-in that
> is not a reading of any glyph. When this happens, say so at every
> occurrence and treat it as an open question about the ASSEMBLER
> MODEL, not about your page. C28-6129's `MULTI` and `CONTAG` listing
> flags are what settle whether IBM's own assembler saw a duplicate.

### 3b. Diff the deck's OWN listing comments against its checks

A deck's own `!  NN  <location> <binary>` listing block is the
human-readable record of what the page says, and it can drift from
the `!CHECK` rows that are actually tested. Run it:

```sh
cd tests && python3 check_deck_listing_comments.py
```

> **THIS USED TO BE A FIVE-LINE RECIPE PASTED INTO THIS DOCUMENT AND
> IT WAS WRONG THREE WAYS.** Three separate transcribers reported it
> misfiring before anyone measured it against the whole corpus. It is
> a script now for the third reason, which is the one a snippet
> cannot fix:
>
> 1. it kept only the FIRST line at a location, so a printed `SLC,$`
>    -- which emits nothing and therefore prints the SAME location as
>    the card below it -- shadowed the emitting row;
> 2. its pattern did not allow the SECOND asterisk after the
>    LOCATION, so every marked row captured a leading `"* "`.
>    Measured over 156 decks: **67 false mismatches**, zero once the
>    asterisk is allowed;
> 3. **the block is a CONVENTION written FOUR ways** -- `! line 12`,
>    `!  12*`, `! line 12*` and `!  12` -- and the pattern read only
>    two of them. It then reported "119 of 156 decks carry no
>    parseable block" as a fact about the DECKS when it was a fact
>    about the regex. **Widened: 101 of 156 decks, 2472 checks
>    compared, 0 mismatches.** A transcriber caught this by
>    re-laying-out their own deck to suit the tool, which is exactly
>    the wrong way round.
>
> The script prints its own REACH -- decks covered, rows parsed,
> checks compared -- and FAILS if it compared nothing. Silence can
> never be mistaken for verification. That is the whole difference,
> and it is why the recipe is gone rather than corrected in place.

### 4. Join it to the image -- AND WHICH IMAGE DEPENDS ON THE PAGE

>>> THERE ARE TWO IMAGES AND THEY ARE DIFFERENT ASSEMBLIES. <<<
printed p.98 closes the tail block with `UNTAIL,(2)` and printed p.99
moves the origin with `SLC,(8)215000.`, so a NAME MAY DENOTE ONE
THING IN pp.15-98 AND ANOTHER IN THE BODY. Putting a body page into
the bootstrap's list is not "widening a range", it is merging two
assemblies, and the merge refuses it -- *"SMCP is defined twice:
printed p.37 and printed p.103, and they disagree: bit 72192 against
bit 4620288"*.

| your page | what to edit |
|---|---|
| **pp.15-99**, the IPL bootstrap | `strap/mcp_image.py`'s `MCP_IPL_PAGES` range |
| **pp.99 and after**, MCP's body | `tests/check_mcp_body_image.py`'s `FIRST, LAST` and its `body_page_count` |

Either way, a page that compiles nothing needs an entry in
`strap/mcp_image.py`'s `NO_DECK_PAGES` as well, or the build looks
for a deck that does not exist. printed p.100 is the worked example:
sixteen comment cards, both data columns empty on every row.

> **THIS SECTION WAS STALE AND SAID THE WRONG THING**, down to
> quoting `range(15, 81)` and `NO_DECK_PAGES = {47, 59, 60}` long
> after both had moved. A body-page transcriber following it would
> have broken the IPL image. Caught by printed p.169's transcriber,
> who could not edit `docs/` and said so instead.

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
the *same printed word*, and those are invisible to it forever. Six
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

> **AND THE GAP IS NOT UNIVERSAL: A VFL OPERAND, AND A `SIC`, READ
> EVERY BIT.** This note first said the half-word gap applied to
> everything, then said `SIC` was *the* exception. Both were too
> narrow. Measured, varying only the SYN's offset:
>
> ```
>   SYN offset ->   .00        .01        .37        .40        .41
>   SIC,X:          216577.00  216577.01  216577.37  216577.40  216577.41
>   ST(BU,40),X:    216577.00  216577.01  216577.37  216577.40  216577.41
>   L(BU,18),X:     216577.00  216577.01  216577.37  216577.40  216577.41
>   CM1111(BU,1),X: 216577.00  216577.01  216577.37  216577.40  216577.41
>   B,X:            216577.10  216577.10  216577.10  216577.50  216577.50
>   LVI,$1,X:       216577.03  216577.03  216577.03  216577.43  216577.43
> ```
>
> **The division is by INSTRUCTION CLASS, not by one mnemonic.** A
> VFL operation and a `SIC` carry a full 24-bit bit address, so a row
> using one is a READING of its operand. A branch or an index
> operation spends the low bits on its own operation field and shows
> only bit 32.
>
> printed p.184 found the VFL half (its `ST(BU,40),K DRAG` prints
> `221250.50`, matching K DRAG's own LOCATION), pp.171 and 176 the
> SIC half. **So before writing "the bit offset is unobservable",
> look for a VFL row or a SIC** -- either settles the symbol
> outright, and an indexed SIC does NOT (it prints the displacement
> instead).

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
> **>>> BUT THE MERGE CHECKS THE ORIGIN ANYWAY, WHENEVER ANOTHER
> PAGE SYNs ONE OF YOUR LABELS. <<<** This is the way out of the
> substitution, and it was missed for a long time. A hard `SLC`
> cannot disagree with the ARRIVING COUNTER -- but it can disagree
> with a landed deck that already placed one of the symbols this
> page DEFINES, and `mcp_image.merge` refuses when it does.
> Measured on printed p.177, moving its origin one half word and
> re-merging:
>
> ```
>   origin as printed    -> merge OK
>   origin shifted .40   -> REFUSED
>      FAIL KFRONT: printed p.117 SYNs bit 4747264,
>                   printed p.177 places it at bit 4747520
> ```
>
> printed p.117 had SYNned `KFRONT` at `(8)220700.0` long before
> anyone opened p.177. So **the origin of any page that defines a
> previously-SYNned symbol is CHECKED, not asserted** -- and the
> check is free, because the body-image test already runs the merge.
>
> **So say which case you are in.** If no landed deck references any
> label you define, the origin really is an assertion and the note
> belongs in the deck. If one does, run the injection and say that
> it is checked.

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

**5. `DR` AND `DRZ` PRINT THE SAME THING.** A reservation prints its
COUNT in the BINARY OUTPUT column, not its storage, so the oracle
cannot tell a reservation that plants nothing from one that plants
zeros. Measured, varying nothing else:

```
  DR(BU,64),(13)   ->  000000.00 00
  DRZ(BU,64),(13)  ->  000000.00 00
```

C22-6531 p.35 makes `DRZ` a `DR` whose words "are all set to zero",
so on a 13-word buffer the difference is 13 words of zero content in
the merged image — invisible to every `!CHECK` on the page and
decisive for anything that later reads that buffer. `decks/
mcp_bootstrap_p136.strap` quoted these cards as `DRZ` and the page
prints `DR`; it was caught by RENDERING printed p.137 line 20 at 1200
dpi, because nothing else could catch it. **Read the Z off the ink,
and never off a passing run.**

> **BUT A TRAILING `Z` ON A BRANCH IS FULLY VISIBLE — DO NOT
> OVER-READ THIS ITEM.** The blindness is about RESERVATIONS, not
> about the letter Z. On a branch-and-clear the clear bit is `0x04`
> of the printed byte, and an ordinary `!CHECK` catches it. Measured,
> everything else fixed:
>
> ```
>   BUSAZ,$+.32  ->  217354.50 C6        BUSA,$+.32  ->  217354.50 C2
>   BADZ,$+.32   ->  217354.50 46        BAD,$+.32   ->  217354.50 42
> ```
>
> printed p.145 carries both. So flag a reservation's `Z` as
> ink-only, and do NOT flag a branch's.
>
> **BUT THERE ARE TWO BRANCH Z's AND THEY MOVE DIFFERENT BITS.**
> This note recorded only the SUFFIX form until printed p.183
> measured the other. Reasoning from one to the other is a coin
> flip:
>
> ```
>   SUFFIX Z -- SETS 0x04        INFIX Z -- CLEARS 0x02
>     BUSA  C2  ->  BUSAZ  C6      BAE  C2  ->  BZAE  C0
>     BAD   42  ->  BADZ   46      BXE  C2  ->  BZXE  C0
>                                  BXL  42  ->  BZXL  40
> ```
>
> Either way the Z IS visible, which is the point that matters --
> but do not predict the byte of one family from the other.

**6. A ONE-BIT IMMEDIATE PINS ONLY THE VALUE'S PARITY.** An
immediate operand is LEFT-JUSTIFIED in the 24-bit A24 field
(Reference Manual printed p.56, "Field Definition", quoted at
`strap_asm.py`'s A24 note), so a `(BU,1)` immediate puts the symbol's
LOW BIT at the top of the field and nothing else shows. Measured on
`LI(BU,1),X,46`, varying only the SYN:

```
  X = 0      ->  000000.00 80 401027.20 50
  X = 1.0    ->  000000.00 80 401027.20 50
  X = 0.32   ->  000000.00 80 401027.20 50
  X = 2.0    ->  000000.00 80 401027.20 50
  X = 8      ->  000000.00 80 401027.20 50
  X = 1      ->  400000.00 80 401027.20 50
  X = 3      ->  400000.00 80 401027.20 50
```

printed p.163 line 40 is such a row and its first draft claimed the
printed `000000.00` pinned `S TD DEN` to zero. **It does not** -- it
establishes only that the value is EVEN. That `S TD DEN` is exactly 0
comes from printed p.108's defining card, a different page. This is
not the half-word gap in another costume either: there the low bits of
an ADDRESS are invisible, here a fully-specified value is reduced to
one bit.

> None of these is a defect in the oracle. They are the edge of what
> comparing one word against one word can establish, and the answer
> to all six is the same: **a second, independent reading** — the
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
