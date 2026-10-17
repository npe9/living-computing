# Listing typography: letter I vs digit 1 (and letter O vs digit 0)

A measurement record, not a rename.  Settles one question about how the
1403-chain print in `docs/jb_ax5b_ibox-5.pdf` and `docs/jb_ax4b_ibox-4.pdf`
should be read, says what a correction would and would not change, and
lists every file in this repository that carries an affected spelling.

Everything below was measured first-hand at **600 dpi** (`pdftoppm -r 600
-png -gray`), by segmenting glyph bounding boxes from pixel-column ink
profiles and reading widths, not by eye.  Where a reading is load-bearing
the pixel dump or a tight crop was inspected as well.  Scratch tooling
lived outside the repo; nothing here depends on it.

---

## 1. The primary source

`docs/C22-6531_7030xasm-sim_1960.pdf`, **printed p.10 (PDF p.11)**, read at
300 dpi, verbatim:

> A symbol is any sequence of six or fewer alphabetic and numeric characters
> conforming to the following conditions:
> 1. It contains only alphameric characters.
> 2. **Its first character is specifically alphabetic.**
> 3. It appears in the name field of an instruction, by virtue of which it is
>    "defined" and is assigned a value that is either a 24-bit binary address
>    or an integer, or occasionally both.

Two independent constraints follow, and this repository's `L`-prefixed
spellings violate the second:

* **First character alphabetic.**  `160123`, `1581`, `14412` were never legal
  STRAP-1 symbols.  Something is wrong with the reading.
* **Six characters or fewer.**  Of the **195 distinct `L1…` symbols** this
  repository now carries, **82 are seven characters long** (`L160100`,
  `L160107`, `L16010A`, `L144XW1`, `L144B1A`, …).  Those could not have
  assembled on the real STRAP-1 either.  `strap_asm.py` does not enforce the
  six-character limit, which is why nobody noticed; it *does* enforce the
  alphabetic-first rule — its symbol pattern is `[A-Za-z][A-Za-z0-9]*` — which
  is exactly why the `L` prefix had to be invented.

The `L` prefix is therefore a workaround for a misreading, and the workaround
itself breaks the same rule it was invented to satisfy.

---

## 2. Per-deck calibration

The decks are two different scans (`jb_ax5b` renders 8400×6900 at 600 dpi,
`jb_ax4b` 10200×6600), so each was calibrated separately and on its own
pages.  The calibration is two-sided:

**Upper bound on "digit".**  The machine-code and octal-address columns on the
right of every listing page contain *only* digits.  Measuring every full-height
glyph there gives the narrowest a printed digit ever is on that deck.

**Lower bound on "letter I".**  Name-field leading glyphs, plus letter-I
instances inside known words (`SIC`, `TI`, `INT`, `INDS`, `CONTINUITY`, `TIME`).

| | `jb_ax5b` | `jb_ax4b` |
|---|---|---|
| pages sampled for digit columns | 26 (pp.5–116, step 5, plus 112–114) | 11 (pp.99–189) |
| full-height glyphs measured there | 11 826 | 4 066 |
| **narrowest printed digit** | **24 px** (99 % ≥ 30) | **21 px** (99 % ≥ 31) |
| digit-column mass | 30–51 px, digit `1` at 30–42 | 33–51 px, digit `1` at 33–42 |
| glyphs ≤ 22 px in a pure-digit column | 18 of 11 826 (0.15 %), all segmentation fragments of h > 100 px merged rows | 26 of 4 066, same cause |
| **letter I** | **10–18 px**, mode 12–15 | **9–22 px**, mode 10–12 |

So on both decks there is a wide empty valley: **no printed digit is ever a
bare stroke of 9–18 px, and the letter I is never anything else.**  The two
populations do not overlap.

**Shape, not just width.**  The digit `1` on this chain has an upper-left flag
*and* a full-width base serif; the letter I has neither.  A pixel dump of
`I60S1` (ax5b p.83, 022741.00) shows the first glyph as a uniform 9–12 px
column from cap height to baseline, and the last glyph as a ~9 px stem with a
24 px flag at the top and a 33 px serif at the foot.  Width alone is a
sufficient discriminator here; the shape confirms it independently.

### Counterexample hunt

**197 name-field tokens** were measured across both decks — 125 on `jb_ax5b`
(29 pages, pp.5–116 step 4) and 72 on `jb_ax4b` (25 pages, pp.5–193 step 8).
Every token whose leading glyph exceeded 22 px was inspected individually.
All of them are ordinary alphabetic names: `START` (ax5b p.5, ax4b p.5),
`LORE2` (ax4b p.157), `CBERB2` (ax4b p.165, 21 rows), `BIT0`–`BIT35`
(ax5b p.114), plus two header/rule artifacts.

**Not one label in either deck begins with a digit-1 glyph.**  No
counterexample was found.

---

## 3. Mixed-row evidence

The strongest evidence controls for scan quality, ink weight and pitch by
putting both glyphs in the *same printed token*.  All widths in pixels at
600 dpi.

### `jb_ax5b`

| PDF p. | printed row | measurement |
|---|---|---|
| 72 | `I60110  Z,$X13  -CLR INT 1.` (022401.40) | label = **I 12**, 6 45, 0 45, **1 38**, **1 36**, 0 45.  Same row: `$X13`'s **1 = 39**; the I of `INT` = **15**; the comment's trailing **1 = 36** |
| 83 | `I60S1  SX,$X1,I60DMP` (022741.00) | label = **I 12**, 6 45, 0 48, S 48, **1 34**.  `$X1`'s 1 and `I60DMP`'s I on the same row |
| 83 | `ICK260 XW,%8¤777774.00,0,0` | **I 13**, C 44, K 45, 2, 6, 0 — already transcribed with a letter I in this repo |
| 83 | comment `-SUBROUTINE TO CLR INDS 0-19,` | **letter O 55**, **letter I 20** (SUBRO*U*TINE) and **13** (INDS), **digit 0 45**, **digit 1 39** — four characters, one row |
| 83 | comment `-CONTINUITY REG I260.` | the glyph before `260` = **13 px bare stroke**; the I of CONT*I*NUITY = 14 |
| 5 | `I58ID  %IQSZ¤DD%BU,64,8¤,I258   Z` (014005.00) | label **I 15**, 5 42, 8 45, **I 17**, D 59; operand **I 15**, 2 45, 5 47, 8 41.  *Three* letter-I glyphs on one line (`I58ID`, `%I`QSZ, `I258`) |
| 5 | `BD,I581` | **I 13**, 5 44, 8 45, **1 35** |
| 5 | banner `----I258---CHK TIME CLOCK AND INTERVAL TIMER.` | banner glyph = **12**; the I of `TIME` on the same row = 15 |
| 13 | `B,I6010` | bare I, then a flagged digit `1` two positions later |
| 112 | `I74ID` (PDF y 1868) vs `I741` (y 2177) | 4th glyph **15 px** in one, **36 px** in the other — same page, same label family, same routine |

### `jb_ax4b`

| PDF p. | printed row | measurement |
|---|---|---|
| 99 | `BD,I461` (006740.40) | **I 11**, 4 48, 6 43, **1 32**.  Independently reproduces the earlier report of `I(10) 4(47) 6(42) 1(31)` |
| 99 | `I46ID` — twice, as the name field at 006741.00 and as the operand of `LX,$X1,I46ID` at 006736.00 | **I 14**, 4 47, 6 43, **I 14**, D 47 / **I 10**, 4 48, 6 44, **I 12**, D 46.  First and fourth glyphs identical bare strokes |
| 99 | banner `----I246---TEST TRANSMIT AND SWAP.` | **11 px bare stroke** |
| 99 | ident operand `…,8¤,I246   Z` | **I 11**, 2 40, 4 45, 6 42 |
| 90 | `I4412  LX,$X15,I44XW1` (006470.00) | **I 10**, 4 47, 4 49, **1 33**, 2 40 — the exact spelling this repo writes `L14412` |
| 165 | `B,IBR13` | bare I, then a flagged digit `1` |
| 6 | `LV,$X1,I32K1` / comment `-PLACE 1 AT XE AND XH` | letter-I label and a digit `1` in prose on one page |

---

## 4. Verdict

**The leading glyph is the LETTER I.  Confidence: very high — this is settled.**

Four independent lines agree and none dissents:

1. STRAP-1's own rule forbids a digit-leading symbol (§1), and the repo's
   workaround for it breaks the same manual's six-character limit 82 times.
2. Per-deck calibration puts letter I (9–18 px) and digit 1 (30–42 px) in
   populations that do not overlap, on ~16 000 measured glyphs (§2).
3. Fifteen same-token or same-row instances across both decks and across the
   full page range show both glyphs side by side (§3).
4. 197 sampled name-field tokens, zero digit-leading labels (§2).

### Two agent reports, reconciled

Two prior agents reported opposite conclusions on `jb_ax5b`.  Both ranges were
re-measured here with one method.

* **pp.112–114 (agent A): confirmed.**  Every name-field lead on pp.112–113
  measures 12–18 px.  The wide leads my sweep flagged on p.114 are the letter
  `B` of `BIT0`–`BIT35`, not counterexamples.  The banner on p.112 is
  `---I274---TRUNCATION OF ADDRESSES.`: its leading glyph measures **13 px**,
  exactly the letter I of `TRUNCATION` **13 px** on the same printed row.
  The ident row below it reads `I74ID  %IQSZ¤DD%BU,64,8¤,I274   Z`, with a
  bare stroke in all three I positions.
* **pp.71–73 (agent B): observation right, inference backwards.**  Agent B's
  checkable claim — that on the `I60110 … -CLR INT` row the label's leading
  stroke is *the same glyph* as the I of `INT` — **is correct**: 12 px and
  15 px, both bare strokes.  What agent B did not measure is the third
  discriminating glyph on that same row.  The comment's own trailing character
  is 36 px with flag and base serif, and the label's 4th and 5th characters are
  38 and 36 px.  The row reads `I60110 … -CLR INT 1.`  The glyphs *are*
  separable on pp.71–73; every name-field lead on those three pages measures
  12–14 px while 821 digits in the same pages' numeric columns never fall
  below 30.  Agent B measured the right thing and stopped one glyph short.

The page ranges do **not** differ.  Possibility (b) — different print runs —
is refuted; possibility (c) — genuinely different labels — is refuted.

---

## 5. The naming scheme

The conjecture (letter **I** + the routine's digits + a suffix) **holds**, with
one refinement and one genuine disagreement.

**Agreements** — every label measured sits in a routine whose digits it carries:

| routine | body labels | continuity | ident | konstants / data |
|---|---|---|---|---|
| 1258 (ax5b p.5) | `I58`, `I581` | `IC258`, `ICK258` | `I58ID` | `I58K1`, `I58K2` |
| 1244 (ax4b p.90) | `I4412` | `IC244`, `ICK244` | — | `I44XW1-3`, `I44D1`, `I44D2` |
| 1246 (ax4b p.99) | `I46`, `I461` | `IC246` | `I46ID` | — |
| 1260 (ax5b pp.72, 83) | `I60S1`, `I60110`–`I60114`, `I6011A`, `I60210` | `IC260`, `ICK260` | — | `I60K7`, `I60AD1/2`, `I60DMP` |
| 1274 (ax5b pp.112–113) | `I74`, `I741`, `I742`, `I743` | `IC274` | `I74ID` | `I74K1`–`I74K4`, `I74PSI` |

Every cell above was resolved glyph-by-glyph except the ax4b p.90 row, where
only `I4412` was measured by name; the other ten name-field tokens on that page
all lead with a 10–12 px bare stroke but were not individually decoded.  The
repo's `L144D1`, `L144D2`, `L144XW1-3`, `IC244`, `ICK244` are listed here from
`verify_ibox4_rnx_nop_listing.py`'s own transcription, corrected only in the
leading glyph.

**Refinement.**  Body labels take the routine's last **two** digits (`I58`,
`I60`, `I74`, `I46`, `I44`); continuity registers take `IC`/`ICK` plus the last
**three** (`IC258`, `IC260`, `IC274`, `IC246`, `IC244`).  The suffix decoding
conjectured is borne out by the deck's own comments: `IC260  XW,0,0,0,0
-CONTINUITY REG I260.`, `LX,$X1,I46ID  -UPDATE IDENT.`

**Disagreement.**  The constant pool on ax5b p.114, headed
`-COMMON CONSTANTS FOR FETCH ONLY`, defines `I00LC`, `I00Z`, `I000`, `I00VO`,
`I00CO`.  All five begin with a 12–15 px bare stroke, so the *letter-I reading
holds*; but `I00` maps to no routine I could identify.  Likewise `IDF1`,
`DPET13`, `RET`, `SEN`, `SERS`, `SSW` are SSIP/DCP externals outside the scheme
entirely.  The scheme predicts the *form* of routine-local labels; it does not
cover the common blocks.

**Open: is the routine "1246" or "I246"?**  Every place the deck prints the
routine's own identifier it prints a letter I — the section banners
(`----I258---`, `----I246---`, `---I274---`), the ident data word
(`%IQSZ¤DD%BU,64,8¤,I246`), and running prose (`-CONTINUITY REG I260.`).  I
found no page in either deck where these identifiers appear with a digit-1
glyph.  Whether the decimal routine numbers this project uses ("routine 1260")
come from external IBM documentation or are themselves a misreading of the
banners is **not settled here**.  It does not affect the verdict in §4.

---

## 6. Letter O vs digit 0 — a separate, weaker result

Raised because `strap/programs/ax5b_1258_test2.strap` states, in its header:

> This printer's letter O and digit 0 are the same glyph

**That sentence is wrong.**  Same-row measurements:

* ax5b p.83, `-SUBROUTINE TO CLR INDS 0-19,`: **letter O = 55 px**,
  **digit 0 = 45 px** — one printed comment, both characters.
* ax4b p.6, `-XL SHOULD BE 0`: letter O = 49, digit 0 = 42.  Next row
  (`-XH SHOULD BE 0`): 48 and 43.

Letter O runs **15–22 % wider** than digit 0 on both decks.  That is a real,
repeatable difference, but it is a *ratio* result, not the 3× gulf that
separates I from 1, and it is within reach of ink weight and skew.

**The p.114 alias row.**  ax5b p.114 prints, at the head of the constant pool,
a row whose name field is `SENO` and whose operand is `SEN?`.  Measured in a
local window (the page is skewed, so the whole-row line finder is unusable
there): the label's 4th character = **54 px**, the operand's 4th character =
**42 px**, on the same printed line.  Direction and magnitude both point to
`SENO  SYN,SEN0` — a letter-O label aliased to a digit-zero symbol.

A second, glyph-independent argument supports the same reading: a symbol
cannot be `SYN`'d to *itself* — the definition would be circular and could not
have produced the printed value `1311.00+ +00000000`.  The two spellings must
differ.

**Confidence: moderate, direction only.**  n = 3 calibration pairs, one
instance of the row, on a skewed page, with a 1.29 ratio against a calibrated
1.15–1.22.  Worth recording; not worth a rename on its own.

---

## 7. What a correction would — and would not — change

### It would change **no check anywhere in this repository.**

Verified, not assumed:

* **`strap/listing_oracle.py` `check_rows(prog, rows, symbols=None, label="")`.**
  Rows are `(octal_loc, printed, note)`.  The third field, `note`, is used in
  exactly one place: interpolated into the `PASS`/`FAIL` line that is printed.
  It is never parsed and never asserted on.  So every disputed spelling that
  lives in a `note` string — which is where nearly all of them live — is
  documentation.
* **The `symbols=` argument** *is* asserted: `prog.symtab[name] == loc_bits(loc)`.
  But the name is only a key that must exist in the assembled symbol table.
  Renaming consistently in the `.strap` and its `verify_*.py` leaves the
  assertion identical; renaming in only one place raises `KeyError`
  immediately.  It is a consistency requirement, not a correctness one.
* **Nearly every disputed symbol is a `SYN`'d external address** —
  `L160DMP SYN, (8)23301.0`, `L100Z SYN, (8)24502.0`, `LIC258 SYN, (8)14006.0`.
  The name is arbitrary; the assembled bits come from the octal address on the
  right of the `SYN`, which is transcribed from the listing's own printed
  address column and is unaffected by the glyph question.
* **No `.bsv` file carries an affected spelling** (checked: zero matches).
  Nothing in the model depends on these names.
* **No emitted bit depends on a disputed glyph.**  The one place where the
  characters would be *encoded* rather than merely *named* is the routine's
  ident word — `I58ID %IQSZ¤DD%BU,64,8¤,I258   Z` at 014005.00.  That row is
  **deliberately not transcribed and not checked**: `ax5b_1258_test1.strap`
  records "014005.00 is NOT transcribed … the machine-code column is blank",
  and `verify_ax5b_1258_test1_listing.py` lists "THE IDENT WORD at 014005.00,
  and the %IQSZ macro's expansion" under what the file cannot see.  Had it been
  transcribed and checked, the digit-1 reading *would* have been a real
  encoding error.  It was not.  No other disputed token sits in a data or
  literal field.

### It would change **spelling, in prose and in symbol names.**

And it would fix two things that are currently wrong on their own terms:

* **82 of 195 distinct `L1…` symbols are over STRAP-1's six-character limit.**
  The corrected forms are all six or fewer: `L160107` (7) → `I60107` (6),
  `L14412` (6) → `I4412` (5), `L1581` (5) → `I581` (4), `L1581D` (6) →
  `I58ID` (5).
* **The repository already reads the same glyph both ways, and in one case
  spells the same symbol two different ways.**  `L100Z` and `L1000` appear in
  `ax5b_160102_lb_ctl.strap`, `ax5b_1258_test2.strap` and their verify scripts;
  `I00Z` and `I000` — the *same* constants, at the same addresses — appear in
  `verify_ibox4_refill_nop_listing.py`, `verify_ibox4_rcz_zerogate_listing.py`,
  `verify_ibox2_load_index_listing.py`.  Similarly `IC258`/`ICK258`,
  `IC244`, `IC262`, `I30ST`, `I22WRK`, `I38XW3`, `I38K1`, `I3021` are already
  spelled with a letter I, while `L160S1`, `L162ITE`, `L14412` are not.
* The starkest case: `ax5b_1258_test2.strap` line 166 defines
  `LIC258  SYN, (8)14006.0` — an `L` prefixed onto a name whose own trailing
  comment on the same line reads `! from LX,$X13,IC258`.  The file records the
  letter-I reading and then prefixes `L` to it anyway.

### Two transcriptions are misread in the source text, not merely prefixed

These are worth flagging separately because no mechanical `L…` → `I…` rename
would fix them:

* `strap/programs/ax5b_1258_test1.strap` (line 43) and
  `strap/verify_ax5b_1258_test1_listing.py` (line 20) quote the ident row as
  `1581D  %IQSZ*DD%BU,64,8*,1258   Z`.  Measured, it is
  **`I58ID  %IQSZ¤DD%BU,64,8¤,I258   Z`** — the label's *fourth* character is
  also a letter I (17 px), not a digit 1, and the operand is `I258`, not `1258`.
  Cross-checked against the identical rows for routines 1246 (`I46ID … ,I246`,
  ax4b p.99) and 1274 (`I74ID … ,I274`, ax5b p.112).
* The same file's header quotes the section banner as `----1258---CHK TIME
  CLOCK AND INTERVAL TIMER.`  Measured, the banner glyph is a 12 px bare
  stroke: **`----I258---`**.

---

## 8. Files carrying affected spellings

From `grep`.  **A repo-wide rename is not proposed here** — it is the owner's
call, and dozens of committed, passing files use these names.

### 47 files containing `L1…` symbols

`docs/archival_inventory.md`, `docs/NEXT.md`

`strap/programs/`: `ax5b_1258_test1.strap`, `ax5b_1258_test2.strap`,
`ax5b_160_test8b.strap`, `ax5b_160_test8c.strap`,
`ax5b_160_test8c_disabled.strap`, `ax5b_160102_lb_ctl.strap`,
`ax5b_160105_compare.strap`, `ax5b_16071_ts.strap`, `ax5b_16082_op_ad.strap`,
`ax5b_16086_ds.strap`, `ax5b_16087_walk.strap`, `ax5b_16099_ub_data.strap`,
`ax5b_160k_constants.strap`, `ax5b_160s1_clr_inds.strap`,
`ax5b_162_exic_classes.strap`, `ax5b_162_test1b.strap`,
`ax5b_162_test1cc.strap`, `ax5b_162_test3a.strap`, `ax5b_162_test3b.strap`,
`ax5b_1681_if_close_to_ds.strap`, `ax5b_1683_df_close_to_ds.strap`,
`fp_arith_f209d1_5.strap`, `ibox4_rnx_nop.strap`

`strap/`: `verify_ax5b_1258_test1_listing.py`, `verify_ax5b_1258_test2_listing.py`,
`verify_ax5b_160_test8b_listing.py`, `verify_ax5b_160_test8c_listing.py`,
`verify_ax5b_160_test8c_disabled_listing.py`, `verify_ax5b_160102_listing.py`,
`verify_ax5b_160105_listing.py`, `verify_ax5b_16071_listing.py`,
`verify_ax5b_16082_16083_listing.py`, `verify_ax5b_16086_listing.py`,
`verify_ax5b_16087_listing.py`, `verify_ax5b_16099_listing.py`,
`verify_ax5b_160k_listing.py`, `verify_ax5b_160s1_listing.py`,
`verify_ax5b_162_exic_listing.py`, `verify_ax5b_162_test1b_listing.py`,
`verify_ax5b_162_test1cc_listing.py`, `verify_ax5b_162_test3a_listing.py`,
`verify_ax5b_162_test3b_listing.py`, `verify_ax5b_1681_listing.py`,
`verify_ax5b_1683_listing.py`, `verify_ibox4_rnx_nop_listing.py`

### Bare (un-prefixed) digit-leading spellings in prose and quoted rows

`162ITE` (63), `160S1` (53), `1000` (45), `160SX1` (35), `162PSI` (30),
`16088` (30), `162INT` (26), `16086` (26), `160K7` (21), `160AD1` (21),
`100O` (21), `162EXI` (20), `160IT` (20), `160127` (17), `100Z` (14),
`162XW1` (13), `160DMP` (13), `16071` (13), `160107` (13), `14419` (12),
`162SUB` (11) and ~80 more, spread over the same files plus the file headers.

### Filenames

21 `strap/programs/ax5b_1*.strap` and 21 matching `strap/verify_ax5b_1*_listing.py`
encode the routine or block number in the filename (`ax5b_160s1_clr_inds.strap`,
`ax5b_16087_walk.strap`, `ax5b_1258_test1.strap`, `verify_ax5b_160s1_listing.py`,
…).  A correction would touch these only if the owner wants filenames to match.

### `strap/run_tests.sh`

Carries the spellings in **five comment lines** (813, 960, 3791, 3997, 4117) —
`L16088`, `L162104`, `LICK258`, `L158K1`, `L158K2`, `L1587A`.  No executable
line is affected.

### Negative results, recorded because they bound the blast radius

* **No `.bsv` file** carries an affected spelling — zero matches across
  `stretch/bsv/`.
* **No `check_rows` assertion** depends on a disputed spelling other than as a
  symbol-table key that must match its own `.strap` (§7).
* **No transcribed and checked row** puts a disputed token in a data or literal
  field; the one candidate, the ident word, is explicitly excluded from every
  transcription.

---

## 9. What is still open

* Whether the routine numbers this project writes as 1244/1246/1258/1260/1274
  are printed anywhere in these decks in a *numeric* form.  Every printed
  instance I found — banners, ident words, prose comments — uses a letter I
  (§5).
* The `I00…` common-constant family maps to no routine I could identify (§5).
* Letter O vs digit 0: direction established, `SENO SYN,SEN0` supported, but on
  n = 3 calibration pairs and one instance, on a skewed page (§6).
The circularity argument in §6 is *not* on this list.  A symbol defined as
itself has no value on any pass, and the row printed `1311.00+ +00000000`;
that is sufficient on its own to conclude the label and the operand are
different spellings, independent of how STRAP-1 resolved external `SYN`
operands.  What stays at moderate confidence is only *which* spelling is
which — that rests on the 54-vs-42 px width measurement.


---

## 10. A GLYPH TRAP THIS DOCUMENT DID NOT COVER: rule lines forge serifs

Added 2026-09-29, after it produced a wrong reading that reached a
committed research note.

**The listing draws dashed rule lines across some comment rows.** Where
one crosses a glyph, it adds a horizontal stroke at cap height — and a
`1` with a rule through its top reads convincingly as a serifed letter
`I`.

The case: routine 1262's TEST 1C header at 023442.40, PDF p.92. It was
recorded as printing `-TEST IC, CHK MISC CNTRLS OF EX.` and the reading
was generalised to *"the comment column prints 1C as IC throughout"*.
**Measured at 600 dpi, the deck prints `1C`.** The apparent top bar is
the row's dashed rule at y376-380, spanning **x2755-2814 — 59 px where
the glyph itself spans 24.**

**What settles it without needing the rule's span**, and the check to
reuse: this printer's letter `I` is a **bare stroke with no serifs at
either end** — the `I` of `MISC` nine cells along the same row is 13 px
and plainly barefoot. The disputed glyph has a **bottom serif**, which
no letter `I` on this chain has, and which the digit `1` of `1CA` on
the very next row also has. A rule line can forge a top bar; it cannot
forge a foot.

**The rule, stated for reuse: any glyph verdict taken on a row this
listing RULES THROUGH is suspect until the rule's own x-span is
measured against the glyph's — and check the BOTTOM of the glyph,
which no horizontal rule can touch.**

Consequence worth recording: with this corrected, the comment column
and the label column **agree** about digit-versus-letter on the same
page — `1C`/`1CA`/`1CB` in the comments beside `I6218`/`I6219`/`I6220`
in the labels — where before they appeared to disagree. An apparent
disagreement between two columns of one listing is itself a signal that
one of the readings is wrong.

### AND THE FIRST GUESS ABOUT WHERE ELSE IT APPLIED WAS WRONG

This section originally ended: *"Not yet checked: PDF p.103's `ICB` at
TEST 2CB. The same artefact is the likely explanation and is explicitly
NOT asserted."* It was checked on 2026-10-16 and **the likely
explanation is wrong. p.103 really does print a letter I.**

The row **is** ruled through, so the warning above applies — but **the
rule misses the glyph by six pixels**: rule at y1971-1976, y1977 blank,
glyph y1978-2045. And the glyph is a bare stroke, 17 px wide, that
*tapers* at top and bottom (3,5,6,7,8,9 px entering; 6,6,4 px leaving)
rather than carrying a flag and a foot. Against the calibration on that
same page — the digit `2` of `-TEST 2C,` and `-TEST 2CA,` both measure
**41 px**, the letter `I` of `MONITOR` on the **same row** measures 13 —
17 px sits in the letter-I population and nowhere near the digit one.
Re-measured on p.92 for contrast: that `1` has an upper-left flag AND a
**37 px base serif**, bbox 37 wide.

**It happened TWICE on p.103 and not at all on p.92**: 024020.40's
`-TEST ICC, CHK EXIC OF BRANCH AND EXE.` carries the same bare stroke
at 21 px. **That is what rules it a DECK TYPO rather than damage or an
artefact** — a duplicated card would have reproduced p.92's digit, so
this is a keypunch that went wrong the same way twice.

**The lesson is about the correction, not the glyph.** Having found one
rule-line artefact, the natural move was to assume the next
digit-read-as-letter had the same cause. It did not. **A newly-named
trap is a hypothesis about other cases, not a finding about them** —
and the measurement that distinguishes them is cheap. Note the two
verdicts stay separate in the transcription: *the glyph is a letter I*
is measured; *`2CB` is what belongs there* is an inference from the
comment being character-for-character p.92's and the label column
reading `I6272` between `I6271` and `I6273`.

## 11. HEX `B` READ AS `8`, AND 600 dpi WAS NOT ENOUGH

Found 2026-10-17 on MCP's printed p.2 (`MCP_Mar63_001-249.pdf` PDF
p.9), line 34, the trailing byte of a full-word VFL instruction.

The listing prints `006000.22 B0`. **It was read as `80` at 200 dpi
and again at 600 dpi**, and only at **900 dpi** does the glyph resolve:
a `B` has a flat left stem with two bowls hanging off it, while an `8`
is two closed loops with no straight edge. At lower resolutions the
stem and the left side of the upper bowl merge into a loop.

**THIS SECTION'S EARLIER RULE WAS NOT ENOUGH.** §2 says render at 600
dpi, not 200, and crop to one column — both were done here and both
gave the wrong character. The hex column is harder than the octal
columns because `B` and `8` are the only pair in `0-9A-F` that differ
mainly in one vertical stroke, and that stroke is the first thing a
worn drum printer loses.

**THE RULE:** in the two-hex-digit byte at the end of a half-word,
`B` and `8` need 900 dpi. The octal columns do not — they have no
letters.

**AND THE CHECK THAT CATCHES IT WITHOUT RE-RENDERING:** a wrong byte
here is a wrong *operation code*, and the operation codes are
tabulated on the pocket card `X22-6533_7030_PocketCard.pdf`, which is
in `docs/`. `80` decoded to a nine-bit operation field of `100101000`,
and **no entry on that card ends in `000`** — every integer-arithmetic
and radix-conversion code ends in `1`. An opcode that is not on the
card is a misread byte until proven otherwise.

---

## 12. AN UNEXPLAINED MARKER IN MCP's LOCATION COLUMN

Transcribing MCP printed p.3 (2026-10-17) turned up a character that
is neither data nor typography: **an asterisk printed after the
LOCATION value, in its own fixed column, on a minority of rows.**

**Where it was seen, first hand:**

| printed page | lines | the rows |
|---|---|---|
| 2 | 5 | `000051.34 *` — `(CC*)DD(BU,,12),` … `11E11BSP*` |
| 3 | 5, 28, 50 | `M+1(BU,19),X1 CCW`; `BRZ,0.0`; `REL(SEOP),0.0($15)` |
| 4 | 20, 38 | `SC,$12,$12`; `REL(SEOP),0.0($15)` |
| 5 | 26, 46 | `B,X 1B ERR`; `BEKJ,X 6 ERR` |
| 13 | 6, 20 | two `(IQS*)DD(BU,64,8)` message rows |

A delegated sweep of printed pp.6–12 reported the same mark on p.6
line 9 and "at a regular ~11–12-line pitch" on pp.7–9. That part is
second-hand and was not re-read here.

**What it is not.** It is not the asterisk every LINE number carries.
It is **not a gap marker**: the obvious reading — that it flags a
location the assembler skipped to — dies on p.3 line 28, which looked
like it followed a half-word gap at 200 dpi and does not at 600
(line 27 sits at `000065.40`, not `000065.00`, and its full word ends
exactly where line 28 begins). None of the eleven instances follows a
gap. It does not track the card-identification column, and it is not
"the second statement punched on one card" — p.3 lines 7 and 8 share
card 11000047 and neither carries it. The marked statements have no
operation, operand form, index register or alignment in common: a
VFL instruction, two branches, two `REL`s, a `SC`, and four `DD`s.

**The one pattern that survives contact with the data** is that the
line-pitch between consecutive marks grows with the number of lines
on the page — p.13 (38 lines) 14, p.4 (41) 18, p.5 (56) 20, p.3 (52)
22–23 — which is what a mark at a fixed PHYSICAL distance down the
form would do. But a fixed physical position would put p.3's first
mark and p.5's first mark at the same height, and they are at rows 5
and 26 of similarly dense pages, so that is not the whole story
either. **Recorded as open.**

**Why it is safe to transcribe past it.** It sits in the LOCATION
column, and all three of p.3's instances are in that page's checked
set and match the listing's own BINARY OUTPUT character for
character. Whatever it means, it does not change an assembled bit.

---

## 13. DIGIT ZERO READ AS `C` — the MCP scan's own glyph trap

Section 6 measured letter O against digit 0 on the `ax4b`/`ax5b`
decks and found a 15–22 % width ratio. **The MCP scan has a different
and sharper confusion, and it is with `C`.**

`docs/MCP_Mar63_001-249.pdf` renders digit zero with a visible gap at
the right of the ring — ink the drum did not lay down, or the scan
did not keep — so a zero at the start of a two-character group reads
as a `C`. It is not subtle at 200 dpi and it does not go away at
900: printed p.4 line 23's binary output reads

```
000050.C3 0B        (what the eye gives)
000050.03 0B        (what it is)
```

Both the `C3` and the `CB` on that one row are wrong readings of a
leading zero. **The octal field settles the first without any
argument** — an octal digit cannot be `C` — and that is the tell to
reach for: this listing's own column types rule out most of the
confusions it creates.

**The second one is settled by arithmetic, not by looking.** With
`CB`, the instruction's nine-bit operation field (bits 23–31) would
be `111001011`, which appears nowhere on X22-6533. With `0B` it is
`100001011` = `LVS`, which is what the statement column says. See
`strap/verify_lvs_encoding.py`.

**The rule, which now has three instances behind it** — `B0` read as
`80` on MCP p.2 line 34, again on p.3 line 10, and `0B` read as `CB`
on p.4 line 23: **decode the operation field before trusting the
glyph.** Re-rendering at a higher resolution (§11) is the second
move, not the first. The opcode tells you what the byte must be; the
render only confirms it.
