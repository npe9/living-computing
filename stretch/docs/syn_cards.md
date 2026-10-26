<!-- PROVENANCE -- read before citing anything below. -->

> ## HOW THIS FILE WAS MADE
>
> Written 2026-10-25 by a **delegated agent** told to render and READ
> every page it quotes rather than trust `docs/ocr/`. It is research,
> not transcription, and the committing session has NOT checked it
> line by line.
>
> **Rule 4 still binds**: nothing here may be built into `bsv/` or a
> deck without opening the cited page first. These files say WHICH
> page and WHAT IT SAYS; the page is still the source.
>
> **Re-verified by the committing session, and acted on:** the two
> bugs it reports are real. `decks/mcp_bootstrap_p39.strap` declared
> `SYSMCD` and `SCORG` with no data description (length 0, which
> `effLength` reads as 64) where printed p.98 declares them
> `SYN(BU,2)` and `SYN(BU,1)`. Both now carry their dds; p.39 still
> verifies bit-exactly and the merge guard is satisfied. Its census
> correction is also confirmed structurally: `SYN(` cannot match a
> card that carries no data description, which is exactly what those
> two bugs were.

---

# MCP's SYN CARDS — a census, a page pick, and a transcription

Scratchpad output. Nothing under `bsv/`, `tests/`, `decks/` or `strap/` was
touched. Deliverables: this file, `mcp_syn_cards.strap`, `check_p98.py`.

---

## 1. THE COUNT IS WRONG, AND SO IS THE PAGE LIST

The brief says "555 declarations across 25 printed pages, clustered at
printed pp.61-64, 84-85, 98-109, 288-289 and 418-419."

**Reproducing it.** Counting `SYN(` per page over both OCR volumes gives
**296**, not 555, on **34** pages. That regex is the one the brief
describes, and it does not reach 555 on this text.

**But `SYN(` is the wrong regex anyway.** A SYN card need not carry a data
description. Printed p.105 is thirty straight cards of the form
`S FREE SYN,12.22` with `NULL` in the dds column — `SYN(` scores it **zero**.
Printed p.98, the page this task transcribes, has ten SYN cards and `SYN(`
scores it **five**.

Counting SYN in statement position (`SYN` followed by `,` or `(`) gives the
real census:

| | pages | SYN cards |
|---|---|---|
| vol. 1 (printed 1-249) | 61 | **435** |
| vol. 2 (printed 250-445) | 27 | **193** |
| **both** | **88** | **628** |

Validation: this regex scores p.98 at exactly 10, and I transcribed and
verified 10 cards there. It scores p.62 at 21 and that deck's own header
says "twenty-one are SYN cards."

**Per-page tally, vol. 1** (printed page: cards)

```
p.8:5   p.9:5   p.10:3  p.11:8  p.12:7  p.13:5  p.14:1  p.21:1  p.24:1
p.25:1  p.30:1  p.35:2  p.36:3  p.37:4  p.41:1  p.46:2  p.48:5  p.50:1
p.60:3  p.61:13 p.62:21 p.63:19 p.64:2  p.76:3  p.83:11 p.84:34 p.85:12
p.98:10 p.99:34 p.100:8 p.101:22 p.102:12 p.103:21 p.104:25 p.105:30
p.106:10 p.107:24 p.108:6 p.109:3 p.116:2 p.120:1 p.130:1 p.134:1
p.154:2 p.171:1 p.181:2 p.185:1 p.189:2 p.199:1 p.203:3 p.209:1 p.210:1
p.213:21 p.214:1 p.215:1 p.222:1 p.234:2 p.236:5 p.240:2 p.241:3 p.244:1
```

**Per-page tally, vol. 2**

```
p.264:1 p.268:3 p.269:1 p.274:1 p.276:4 p.277:2 p.286:4 p.287:13 p.288:20
p.289:19 p.291:10 p.292:11 p.293:1 p.309:2 p.310:9 p.317:3 p.357:2
p.362:8 p.375:10 p.394:4 p.410:2 p.417:10 p.418:33 p.419:13 p.432:1
p.436:5 p.437:1
```

**Clusters (>= 10 cards on a page), vol. 1:** pp.61-63, 83-85, 98-107, 213.
Printed p.64 has 2, not a cluster; p.100 and pp.104-107 ARE clusters and the
brief's list omits them entirely, because `SYN(` scores p.100/104/105/106 at
zero.

### pp.287-289 and pp.417-419 ARE REPRINTS. The brief double-counts them.

Volume 2 contains a **second assembly of the same source** at a different
origin. Printed p.288 is printed p.62 re-run: same statements in the same
order, but p.62 line 3 compiles

```
003314.00   003317.00+ 000 000024 003314    T PPREF XW,TPREFT,TPPC,$
```

and p.288's same line compiles a count of `000025` (21) where p.62's is
`000024` (20) — a different `T PPC`, so a different build, not a reprint of
the same paper. Likewise p.418's declared symbol set (`T UNTYP`, `T UNREF`,
`T UNME`, `T DSKRF`, `T DTRK`, `T DKCT`, `T SBDFT` …) is p.84's, in order.

Consequence: **pp.288-289 and 418-419 contribute no new symbol names.** The
brief's cluster list counts them as if they did. They are still worth having
— a second printing of the same card is the ideal tiebreaker for a disputed
glyph — but not as declarations.

### The count is a FLOOR

It is an OCR count of a 1963 drum-printer scan. Weak ink on a `SYN` loses a
card. Every number here is a lower bound.

---

## 2. THE PAGE PICK: printed p.98

Criterion, as set: the page declaring the most symbols the **existing decks
already reference**. Method:

1. Parse every `NAME SYN…` declaration out of `decks/mcp_bootstrap_p*.strap`.
   That is **503 distinct names** — the exact population in which a
   contradiction could be live, since those are the symbols the decks had to
   supply themselves.
2. For each printed page, count how many of those 503 appear on a line that
   also carries `SYN`, using `listing_index`'s own space-tolerant matcher
   (the listing prints `T PICA` where a deck writes `TPICA`).

Result, top of the ranking:

| page | hits | status |
|---|---|---|
| p.62 | 14 | already a deck |
| p.63 | 14 | already a deck |
| p.287 | 14 | vol-2 reprint of p.61 |
| p.288 | 14 | vol-2 reprint of p.62 |
| p.61 | 13 | already a deck |
| p.289 | 13 | vol-2 reprint of p.63 |
| **p.98** | **7** | **NEW — the pick** |
| p.103 | 5 | new |
| p.83 | 4 | new |

**The brief's candidates fail the criterion.** It proposes pp.84-85 and
98-109 as "the tables the transcribed pages already reference by name."
pp.84-85 do not. I took all 38 symbols p.84 declares — `TUNATE`, `TCHAN`,
`TUNTYP`, `TUNREF`, `TUNME`, `TDSKRF`, `TDTRK`, `TDKCT`, `TSBDFT`, `TJONME`,
`TIABEX`, `TIREF`, `TIOP`, `TITY`, `TIREEL`, `TITRK`, `TITYCD`, `TICH`,
`TIUN`, `TINO`, `TIMO`, `TIDN`, `TIDS`, `TUNLGN`, `TCHANN`, `TUNITN`,
`TIODK`, `TFIAAC`, `TSYSTM`, `TFRLAD`, `TCREEL`, `TREELK`, … — and grepped
every one against every file in `decks/`. **Zero hits.** p.84 declares the
most symbols of any page in the listing (34) and not one of them is
referenced by anything transcribed so far. It is the right page to take
*next*, when the pages that use it are read; it is the wrong page to take
*now*.

p.98 wins because its seven are exactly the non-`T` symbols the ASSIGN decks
had to derive from statement context: `STATI`, `SIMNT`, `SMOUNT`, `DFREE`,
`SYSMCD`, `SMAXUB`, `XINEND`.

---

## 3. THE TRANSCRIPTION — printed p.98 lines 20-37

`mcp_syn_cards.strap`, PDF page 105, rendered at 600 dpi in four bands,
1800 dpi for four disputed glyphs.

**Scope.** 37 lines on the page. Lines 1-4 are a box heading; lines 5-19 are
the fifteen VFL rows of the CONVERSION SUBROUTINE; **lines 20-37 are the
tail, and every SYN card on the page is in it.** Lines 5-19 are deliberately
left out: they carry no SYN value, and they reference `LBLZCR` and `TMX1`,
which appear in no deck — transcribing them would mean back-deriving two
symbols from the very binary column that is supposed to check the work. A
partial page fully verified.

**18 rows transcribed. 18 verified. 0 unverified. 1 disputed glyph
(resolved).**

- 4 rows that compile a word, checked against the printed BINARY OUTPUT
- 14 symbols, checked against the printed LOCATION column (printed p.24's
  convention: a SYN row prints its VALUE there and no word)

```
$ PYTHONPATH=strap python3 strap/strap_asm.py <deck>     -- assembles
$ PYTHONPATH=strap python3 <scratchpad>/check_p98.py     -- ALL TESTS PASSED
```

### Row by row, assembled vs. printed

| line | location | printed BINARY OUTPUT | assembled | |
|---|---|---|---|---|
| 23 | 005464.00 | `005464.04 00` | `005464.04 00` | MATCH |
| 28 | 005464.40 | `000000.00+` | `000000.00+` | MATCH |
| 29 | 005465.00 | `000000.00+` | `000000.00+` | MATCH |
| 31 | 005465.40 | `017777.00+` | `017777.00+` | MATCH |

**4 of 4 rows match.** Nothing was adjusted to make the assembler agree;
the deck assembled correctly on its first run.

### Symbol by symbol, assembled vs. printed LOCATION

| line | symbol | printed | assembled | |
|---|---|---|---|---|
| 20 | `L XA` | 000034.00 | 000034.00 | MATCH |
| 23 | `Y BCRD` | 005464.00 | 005464.00 | MATCH |
| 24 | `STATI` | 000000.32 | 000000.32 | MATCH |
| 25 | `SIMNT` | 000000.65 | 000000.65 | MATCH |
| 26 | `S MOUNT` | 000000.63 | 000000.63 | MATCH |
| 27 | `D FREE` | 000000.00 | 000000.00 | MATCH |
| 28 | `Y LCL2` | 005464.40 | 005464.40 | MATCH |
| 29 | `Y LCL1` | 005465.00 | 005465.00 | MATCH |
| 30 | `SYSMCD` | 002151.10 | 002151.10 | MATCH |
| 31 | `S TERMI` | 005465.40 | 005465.40 | MATCH |
| 32 | `Z FINIS` | 017777.00 | 017777.00 | MATCH |
| 33 | `S MAXUB` | 002153.00 | 002153.00 | MATCH |
| 34 | `SCORG` | 002151.03 | 002151.03 | MATCH |
| 36 | `X IN END` | 005466.00 | 005466.00 | MATCH |

**14 of 14 match.**

### The data description column is printed in OCTAL

Every length claim below rests on this, so it is stated rather than assumed.
Line 24's card reads `SYN(BU,1)` and the dds column prints `BU,01 ,10`;
line 30's reads `SYN(BU,2)` and prints `BU,02 ,10`. A byte size of `10`
read as octal is 8 bits, the STRAP default. Printed p.84 line 7 confirms it
from the other end: `SYN(BU,48)` prints `BU,60 ,10`, and 0o60 is 48.

**Five of the ten cards are double-attested** — their dds appears in the
STATEMENT column too (lines 24, 25, 26, 30, 34). **Two rest on the octal
reading alone** and are flagged single-source in the deck:

- line 20, `L XA`, `BU,1CC,1C` → (BU,64,8)
- line 33, `S MAXUB`, `B ,31 ,01` → (B,25,1), inherited from `S BA MCP`,
  which this page does not declare

### The one disputed glyph: SCCRG / SCORG

Line 34's NAME column prints five characters with no blank, and at 1800 dpi
**characters 2 and 3 are identical open-right C's. The ink says `SCCRG`.**

It is read as `SCORG`, on an argument that does not depend on any glyph:
**line 34's LOCATION is 002151.03, and printed p.39 line 19
(`CM0000(BU,1),SCORG`) has a left address of 002151.03.** Same bit, same
symbol.

Corroborating but weaker, and recorded as such: p.39 line 19's own STATEMENT
renders at 1800 dpi with a visibly **closed O**, plainly different from the
open C beside it, on the same row off the same printer; and p.98 line 34's
own statement column prints `SCOMRG+.3` with a closed O two characters
along. The page can print both letters; the NAME column prints two C's.

Recorded as **disputed glyph, resolved symbol**.

### One glyph that was disputed and is now settled: D FREE / C FREE

Line 27's NAME begins with a weakly inked letter. Settled at 1800 dpi
against the same page's own letters: the `C` in `UNCODE` (line 23's comment)
is a round open bowl with no vertical stroke; the `D` in `BCRD` has a
straight vertical left with square corners. Line 27's glyph has the straight
vertical. **`D FREE` → `DFREE`.** (`SFREE` is a different symbol and exists
— printed p.105 line 1 declares `S FREE SYN,12.22`.)

---

## 4. CONTRADICTIONS WITH decks/ — the live-bug report

p.98 is **authoritative** over pp.39 and 40 for these symbols: p.98
*declares* them; pp.39 and 40 only *reference* them, and their decks had to
reconstruct a declaration from statement context. I did not edit `decks/`.

### (a) `SYSMCD` — CONTRADICTION, latent at the row, LIVE at the merge

| | |
|---|---|
| deck | `decks/mcp_bootstrap_p39.strap:141` — `SYSMCD  SYN, (8)2151.10` |
| listing | p.98 line 30 — `SYSMCD SYN(BU,2),SCOMRG+.8`, dds column `BU,02 ,10` |
| address | **agrees** — SCOMRG is (8)2151.0, +8 bits = 002151.10 |
| length | **0 vs 2** |

Latent at p.39 itself: line 18 is `BZB, SYSMCD, YUER`, a branch on one bit,
whose printed word `002151.10 80 002311.34 00` carries a branch target, not
a length — so p.39's row is correct either way. But a merged image built from
both decks has a **length-0 `SYSMCD`** where IBM declared `(BU,2)`, and the
new agreement guard will reject the merge. This is precisely the failure
class of the 2026-10-25 note: a symbol declared WITH its data description on
one page and WITHOUT it on another.

A pointer, **not evidence** — it is OCR and OCR is a finding aid only: the
index shows a vol-2 row that looks like `CM0000(BU,2),SYSMCD`, a two-bit
field with the dds on the statement. If that row renders as it reads, it is
an independent confirmation of the length. It has not been rendered.

### (b) `SCORG` — CONTRADICTION, latent at the row, LIVE at the merge

| | |
|---|---|
| deck | `decks/mcp_bootstrap_p39.strap:142` — `SCORG   SYN, (8)2151.03` |
| listing | p.98 line 34 — `SCORG SYN(BU,1),SCOMRG+.3`, dds column `BU,01 ,10` |
| address | **agrees** — 002151.03 both |
| length | **0 vs 1** |

Latent at p.39's own rows: line 19 is `CM0000(BU,1), SCORG`, carrying its
own `(BU,1)`, so the symbol's dds is never consulted and the printed word is
right either way. **The severity is identical to (a):** the merge guard fires
on *declarations disagreeing*, not on a compiled word changing. A merged
image carries a length-0 `SCORG` where IBM declared `(BU,1)`, and the guard
will reject it.

### (c) `SMAXUB` / `SBAMCP` — not a contradiction, but an unrecorded identity

| | |
|---|---|
| decks | `p40.strap:105` `SMAXUB SYN, (8)2153.0`; `p28/p31/p32/p33/p72` `SBAMCP SYN, (8)2153.0` |
| listing | p.98 line 33 — `S MAXUB SYN,S BA MCP`, dds column `B ,31 ,01` |

Both decks have the right address, independently derived, and p.98 shows
**why** they coincide: they are the same symbol by construction, not by
accident. The decks record neither the link nor the inherited `(B,25,1)`
data description. Worth carrying forward so a future page does not "discover"
the coincidence again, the way p.56 and p.62 had to for `T FREEL`/`T UNCT`.

Loose end, **reported as a pointer and not resolved**: printed p.83 appears
to carry the reverse card, `SYN,SMAXUB`, under a name the OCR renders as
`T BAMCP` (and p.417, its vol-2 reprint, the same). As printed that is
circular with p.98 line 33. It is not resolvable from OCR and should be the
first thing checked when p.83 is rendered.

### (d) `DFREE` — CONFIRMED, and a deck note can be retired

`decks/mcp_bootstrap_p71.strap:102` declares `DFREE SYN, 0` and line 34 of
that deck's header says: *"DFREE COMPILES ZERO. It is not defined anywhere
this project has [read]."*

**Printed p.98 line 27 is that card:** `D FREE  SYN,0`, dds column `NULL`,
location `000000.00+`. The derivation is confirmed and the note is now
false — DFREE is defined, here.

### (e) Six confirmations, no contradiction

| symbol | decks | p.98 | |
|---|---|---|---|
| `STATI` | `SYN(BU,1), 0.26` (p69, p70, p78, p79) | line 24 `SYN(BU,1),.26` | agrees |
| `SIMNT` | `SYN(BU,1), 0.53` (p70, p75, p79) | line 25 `SYN(BU,1),.53` | agrees |
| `SMOUNT` | `SYN(BU,1), 0.51` (p70, p75, p79) | line 26 `SYN(BU,1),.51` | agrees |
| `XINEND` | `SYN, (8)5466.0` (p13, p15, p17) | line 36 `SYN,$` at 005466.00 | agrees |
| `YBCRD` | `SYN, (8)5464.0` (p39) | line 23 label at 005464.00 | agrees |
| `STERMI` | `SYN, (8)5465.40` (p39) | line 31 label at 005465.40 | agrees |

`decks/mcp_bootstrap_p70.strap:62-64` wrote: *"THREE SYMBOLS THAT ARE NOT
'T' NAMES: SIMNT 0.53, SMOUNT 0.51 and DMCP 001472.0 — lines 54, 55 and 56,
the unload path. Like STATI they suggest tables declared outside the ASSIGN
program."* They were, and p.98 is one of those outside pages: it declares
two of that trio (`SIMNT`, `SMOUNT`) plus `STATI`, all three at the values
the decks had derived. (`DMCP` is not on this page.)

### Two new symbols this page contributes

- `ZFINIS SYN, (8)17777.0` — line 32, and line 31's `STERMI VF,ZFINIS`
  compiles `017777.00+` against it. 0o17777 is 8191: the last word of an
  8192-word memory. The comment reads "THE LAST LOC USED BY MCP."
- `LXA SYN, TMLXA` at 000034.00 — line 20. 0o34 is word 28, which is index
  register `$12`. `TMLXA` itself is not declared on this page; p.83 appears
  to carry it and is the page to check.

---

## 5. WHAT TO DO NEXT

1. **Resolve (a) and (b) before the next merge.** `SYSMCD` needs `(BU,2)`
   and `SCORG` needs `(BU,1)` in `decks/mcp_bootstrap_p39.strap`. Both are
   length-0 today. Neither changes a compiled word on p.39, so both tests
   will still pass after the fix — which is exactly why they went unnoticed.
2. **Take p.84 next.** 34 declarations, the most of any page, and zero
   overlap with anything transcribed — so it is pure gain rather than
   cross-check, and it is the page pp.83 and 85 lean on.
3. **Stop using `SYN(` to find declaration pages.** It scores printed
   pp.100 and 104-107 at zero and they hold 97 cards between them.
