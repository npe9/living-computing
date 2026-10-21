# A plan to boot MCP and the rest of the extant 7030 code

Written 2026-10-16. Everything here rests on sources already read; the
page citations are to documents in `docs/` and were verified
first-hand on the dates recorded in `NEXT.md` §5h-§5k.

## 0. The one-paragraph version

**Boot the plumbing before you boot the software.** The first
milestone needs *no transcription at all*: a hand-written ten-line
program, assembled by this repo's own assembler, wrapped as a tape
image, read off a file in Bluesim and off the SD card on hardware,
IPL'd by the mechanism Reference Manual p.126 specifies. Everything
after that is content. Getting the order wrong — transcribing MCP
first and discovering the IPL path is broken — is the expensive
mistake available here.

Then: **the Diagnostic Control Program, not MCP, is the better first
real target**, because it is the harness for the 243 programs this
project has already transcribed.

---

## 1. What "all other extant code" actually is

Every item below is a scanned listing in `docs/`. The column that
matters is whether it prints IBM's own machine code, because that is
what makes transcription self-checking under `AGENTS.md` rule 3 via
`listing_oracle.py`.

| artifact | file | listing pp. | machine code? | runnable? |
|---|---|---|---|---|
| **Diagnostic Control Program** (KA UA1) | `ka_ua1_diagnostic_ctl_pgm.pdf` | 19-152 (134) | **yes**, verified | **the harness** |
| **MCP** | `MCP_Mar63_001-249/250-445.pdf` | 445 | **yes**, verified | the OS |
| Load and Tape Write Utility (KA UL1) | `ka_ul1_load_and_tape_write_util.pdf` | — | **yes** | writes IPL tapes |
| SSIP | `ja_ua1_ssip.pdf` | — | yes | the error reporter every deck branches to |
| Maintenance tape (JA UC1A) | `ja_uc1a_maintenance_tape.pdf` | — | — | 32-program tape + its own IPL |
| I-Box 1-5 | `ja_ax1a`, `jb_ax2a/3a/4b/5b` | 787 combined | yes | **243 programs already transcribed** |
| Floating point | `jb_af1c_floating-point.pdf` | — | yes | diagnostic |
| Memory tests | `ja_bb6b`, `ja_bm6a`, `ja_bp6a` | — | yes | diagnostic |
| BX-0 | `ka_ex1`, `ka_ex1b` | 11-78 | yes | **NO** — manually operated, no instruction stream |

**Named, known to have existed, and absent** — worth asking CHM /
bitsavers / Paul Pierce for by name: `JA EE3` (BX/TAPE), `JA NE4`
(printer/BX), `JA ES1D` (I/O single channel), `JA CE1`/`CE2` (tape),
`JA NE5`/`NE6` (reader/punch), and for the disk `"High-Speed
Exchange"`, `"Disk"`, and the **SEVA Disk Routine**.

**There is no machine-readable artifact of any kind** — no tape image,
no card dump, no disk image (`archival_inventory.md`). Every tape this
plan boots has to be *manufactured* from a listing with this repo's
assembler. That is the whole difficulty, and it is why §2 exists.

---

## 2. Why the Diagnostic Control Program comes before MCP

`archival_inventory.md` on KA UA1, confirmed by rendering p.60:

> "The DCP is the master harness: it IPLs, reads a schedule of
> test-program IDs, loads and checksums each named diagnostic test off
> a *master tape*, sequences their execution, formats console/printer
> output, and — via its Utility section (control sections `J1`/`J2`) —
> **builds and maintains that master tape from individual test
> decks.**"

Five reasons it outranks MCP as the first real target:

1. **It is the harness for work already done.** 243 transcribed
   programs, 37,973 lines, 184 verify scripts. DCP is what sequences
   exactly those. Nothing else in the plan makes the existing corpus
   *run as a system* rather than as 243 separate testbenches.
2. **It is self-hosting.** `J1`/`J2` build the master tape from decks,
   so once DCP runs, adding a program is a data operation, not a model
   change.
3. **No disk.** MCP requires one at p.6's minimum configuration and
   touches it during bootstrap execution (§5i). Nothing says DCP does.
4. **Its listing has the machine-code column** — verified by render,
   not assumed.
5. **Partial DCP is useful.** Memory Compare (`G5`) and Panel Dump
   (`H7`) are near-complete dumps of programmer-visible state and are
   worth having on their own.

**The honest cost.** 134 listing pages at this repo's measured
96 rows/day is **~75 days** for all of DCP — more than MCP's bootstrap
(~4 days) and far less than all of MCP (~198 days). So the sequence
below reaches a demonstrable boot long before either.

---

## 3. The milestones

### M0 — the tape path, with no transcription at all  ·  ~1 week

The point is to make "boots from a tape image" true before any content
exists to boot.

1. `TapeSource` already exists and is request/response (committed
   today). Add **`mkTapeSourceFile`** behind it: value-typed
   `import "BDPI"`, which is **proven** — built and run, six streaming
   words out of a host file (`bsv/sd_reference/`, and the pattern is
   from the user's own `~/src/alto-bluespec/src/Disk.bsv`). Amend
   `StretchIO.bsv`'s header, which still claims `$fopen`/`$fgetc`
   being Actions forces pre-loaded `Vector`s.
2. Widen `TapeIndex` from 4 bits. A reel is ~16 MB; the 24-bit word
   address in `bsv/sd_reference/TapeSource.bsv` is the shape to take,
   with `atEnd` in the response so End Exception stops depending on a
   caller-side capacity compare.
3. **`mktape.py`** in `strap/`: assembled program → tape image. Per
   `ka_ul1`, an IPL tape is written by ONE `W` with **no tape mark, no
   label, no preamble**, and its first word is the control word the
   hardware's refill will fetch. This is a short script.
4. **`mkTapeSourceSD`** for the board. Measured at ≈ −237 LUT4,
   −304 FF, +112 CCU2C net. **Put the reader in the 25 MHz domain**,
   not the 3.33 MHz core clock: a 512-byte sector refills in 0.98 ms
   at 25 MHz against 7.37 ms at core clock, versus 8.19 ms of buffered
   play — 8× margin instead of 11%.

**Exit test:** a file-backed tape and an SD-backed tape deliver the
same bytes to the same `TapeSource` interface.

### M1 — IPL, still with no transcription  ·  ~1-2 weeks

The five model items, in `docs/tape_unit_contract.md` §2.2's order,
which is the right one (see `NEXT.md` §5k's correction):

| | item | where | status |
|---|---|---|---|
| 5 | **chaining** | `StretchCore.bsv` | **done** 2026-10-16, untested as a feature |
| 8 | **SEOP status bit 24** | `StretchIO.bsv` | **BLOCKED — see `NEXT.md` §5o.** p.121 sources "set at issue" and says nothing about clearing; the contract's "cleared at completion" is an inference, and the model hangs on the wrong reading |
| 6 | **the IPL mechanism** | both | ~60-120 lines |
| 7 | **channel signal** (not-ready→ready) | `StretchIO.bsv` | ~20-30 lines |
| — | a chaining **test** | `gen_tape_tb.py` | `pack_cw` already takes `chain`/`refill` |

The IPL mechanism is fully specified by RefMan printed p.126: plant
the fixed control word (data address 4, chain 1, count 1, refill 4) in
the signalling channel's control-word location; READ; the refill
chains to location 4, which now holds the word just read off the tape;
continue; send the initial-start signal; the CPU executes the
instruction at that word's data address **without placing it in the
instruction counter**. EOP, EE and CS must **not** be set on
completion.

**Exit test — and this is the one that matters:** a ten-line program
written by hand, beginning `BD` as p.126 requires, assembled, wrapped
by `mktape.py`, IPL'd from a file in Bluesim and from the SD card on
the board, halting on a known PC. **No listing transcribed. If this
works, every later milestone is content.**

### M2 — the first real artifact: KA UL1  ·  ~1 week

`ka_ul1`'s tape-write routine is **ten instructions** (PDF p.17,
header `@@@TAPE WRITE`) and its listing prints machine code. It is the
smallest extant IBM program that does something structural, and it
*writes IPL tapes* — so running it closes the loop with `mktape.py`:
the model can then produce its own boot media the way the real machine
did. It needs `LOC`, `W`, `UNLOAD` distinct from `REWIND`, and the
SEOP poll from M1.

### M3 — MCP's bootstrap  ·  TRANSCRIPTION DONE 2026-10-17

**ALL THIRTEEN PAGES ARE TRANSCRIBED AND IN THE SUITE** — printed
pp.2 through 14, roughly 495 checks across seven verifiers:

| printed pages | what | checks |
|---|---|---|
| 2 | clear registers, size core by faulting | 22 |
| 3 | find IPL channel, IO TEST, **space over tape mark** | 56 |
| 4 | FETCH PROSA, move the MCP IPL over the bootstrap | 49 |
| 5-6 | the ERROR ROUTINE, hunting for a console | 68 |
| 7-8 | `X ERR DD`, the error table, and its definitions | 90 |
| 9-12 | the error messages | 146 |
| 13 | three more messages, BOOTSTRAP DEFINITIONS | 23 |
| 14 | PROSA CWS — 39 chained control words | 41 |

One row of the 495 is a documented standoff (printed p.3 line 6's
`CCW,15.32,X IPL BS` prints `0011` where X22-6533 requires `1000`),
and the thirty-one `(IQS*)DD` message rows check their LENGTH only
because the listing prints no bytes for them.

**WHAT THE TRANSCRIPTION ITSELF SETTLED**, none of it known when this
plan was written:

* **The tape has a tape mark on it.** Printed p.3's SPACE OVER TAPE
  MARK means the bootstrap record is followed by one and the
  bootstrap spaces past it before reading anything else.
  `mktape.py` writes none and the model cannot space over one.
* **The bootstrap copies the next stage over itself** (printed p.4's
  `T,$11,X BUFER($1),X BS END`), which is why the tape mark has to be
  passed first.
* **39 chained PROSA control words, not 42**, each fetching 513 words
  512 words further along; the last is the only `CW(CR)` and is what
  stops the channel.
* **The size question is answered by a row**: `X IPL K` = 369 words
  including the control word, `X BS END - X IPL BS` = 368 without.

### M3 IS DONE: IT RUNS, 2026-10-18

**MCP's bootstrap executes end to end on the model**, off a tape
built by `mcp_image.py` + `mktape.py --cw-in-image --tape-mark` from
the thirteen transcribed pages, and hands off to printed p.15's MCP
INITIALIZATION. In the suite as "MCP'S OWN BOOTSTRAP RUNS".

| printed page | what it does | the evidence |
|---|---|---|
| 2 | clears the registers, **sizes core by faulting** | `X S ROOF` = word 98,304 = `InstalledWords` |
| 3 | finds the IPL channel by walking them | `X1 CCW`'s channel field 31 → **34** |
| 3 | `LVE` keeps the channel number | `$X15` = 1088 |
| 3 | IO TEST status loop | no error site ever ran |
| 3 | **spaces over the tape mark** | reaches FETCH PROSA |
| 4 | fetches PROSA, hits end of file, sets the marker | **word 16 bit 25** |
| 4 | moves the MCP IPL, branches to `X 10` | PC halts at 0 |

**The two checks that carry the claim.** Printed p.4 line 37's
`CM1111(BU,1),$0 +.25  -END OF PROSA FILE` sets word 16 bit 25, and
**nothing earlier in all thirteen pages writes it** — that bit is the
difference between finishing and stopping somewhere quiet. And
`X ERR AD` is **zero**: every error site does `SIC,X ERR AD` before
branching, and the instruction counter is never zero inside the
bootstrap, so zero means no error site ever ran. The indicator
register holds `XCZ`, `XVZ`, `RZ` and **neither OP nor AD** — the
model refused nothing.

**It halts at PC 0 and that is the hand-off, not a failure.**
Printed p.4's `B,X 10` goes to `000622.00`, one word past `X BS END`,
so the machine runs into the zeros above the image; a zero half-word
is `BE,0`, which branches to zero, and at zero it branches to itself.

> **CORRECTION, 2026-10-18 — THE TWO CHECKS DID NOT CARRY WHAT THEY
> SEEMED TO.** The run above never reached `B,X 10` at all. Printed
> p.4 line 29 is `REL(SEOP),0.0($X0)` — RELEASE **DISK**, channel
> zero — and with no disk installed the model rejected it with Unit
> Not Ready; line 30 branched to `X ERR 12`, on printed p.15 and
> outside the image; the machine ran into zeros there instead. Worse,
> a zero half-word is BRANCH ENABLED, which enabled the interrupt
> system with UNRJ pending, and **the interrupt reset the indicator
> register** — so `mcp_indicators_word11 = 0xA040`, the value this
> section read as "the model refused nothing", was measuring the
> register after a wipe. Giving channel 0 a disk removed the
> rejection, and the first thing that appeared was an **OP** bit that
> had been set all along by printed p.4 line 28's eleven-word
> `TRANSMIT`. See `docs/NEXT.md` "THE NEXT MCP BLOCKER IS TRANSMIT".
>
> What survives unchanged: `X ERR AD` = 0, `X S ROOF` = 98,304 words,
> the channel walk reaching 34, `$X15` = 1088, and the load itself.
> MCP still sizes the machine, finds its channel, spaces the tape
> mark and reads PROSA to end of file. What it does **not** do is
> move itself into storage.

### What had to close first, and why the order is the lesson

**None of the three was top of the predicted list.** The list was
`SPFL`, tape marks, `LOC`, `GONG`, the disk. What the model actually
reported, in order:

1. **Address Invalid on a store past installed core.** Printed p.2's
   clearing loop has **no terminating count** — AD is the only thing
   that ends it. The model raised AD for floating-point operands and
   nowhere else, so after twelve million steps the index had wrapped
   the 24-bit address field and was clearing from word 6 again.
   RefMan printed **p.21** (this repo cited p.20 in two places).
2. **`LVE`** (printed p.3 line 10). `bsv/README.md` had said it was
   left unimplemented because no page gave its behaviour distinctly
   from `LV`'s. **The page is printed p.29** — and `StretchExecute`'s
   own `SVA` arm already cited p.29 for the section immediately
   below it.
3. **`SPFL`** (printed p.3 line 35) and a tape mark for it to find.

**`LOC` and `GONG` were never reached**, because both are only in the
ERROR ROUTINE and the bootstrap never errs. They remain open and are
tracked in `NEXT.md` item 5 — but they are not on this path, and
building them first would have been work done for a guess.

**The disk was never reached either.** `FETCH PROSA` reads from the
TAPE, gets End Exception at the end of the reel, and printed p.4's
`X DONE` handles that as END OF PROSA FILE. So the disk is an M4
question, not an M3 one.

**Still open for M3+**: `$IPLD`, printed pp.15-36 — 22 pages, 3
sampled — which is now the actual next thing, because `X 10` is its
first instruction.

### M3+ — pp.15-18 ARE TRANSCRIBED, 2026-10-18, and they name the gate

Four pages, 118 printed rows, every one bit-exact against the
listing: `decks/mcp_bootstrap_p15.strap` through `p18`.

| printed page | what it does |
|---|---|
| 15 | MCP INITIALIZATION: move the communication region, patch the machine's own size into it, **LOCATE the disk to arc zero** |
| 16 | **WRITE PROSA ON DISK** and fetch from the MCPS tape; rewind and unload the tape when PROSA is refreshed |
| 17 | **PROCESS IOCD CARDS SETTING UP CST AND LST** — MCP reads its own configuration off punched cards |
| 18 | the unit-status half of the same, up to eight units per channel |

**THE GATE IS NOW NAMED, AND IT IS THE DISK AFTER ALL — but one page
later than the old guess said.** M3's note above is still right that
the disk was never reached *by the bootstrap*. Printed p.15 line 26
is the first disk instruction MCP executes.

**SAY PRECISELY WHAT IS AND IS NOT MEASURED HERE.** The boot test
still loads only the bootstrap image, printed pp.2-14 — `mcp_image.py`
deliberately excludes pp.15+, because the bootstrap is the tape record
and MCP proper is what the bootstrap *loads* — so the run still halts
at PC 0 exactly as the table above describes, and **nothing in this
repo has yet executed a single row of pp.15-18.** What is measured is
the transcription: 118 rows, bit-exact. What is read off the code
rather than run is everything below.

What the model will do when those rows do run is not a guess either,
but it is an inspection and not a measurement: `StretchExecute.bsv`'s
`3'b011` arm is one line, `ind = setOpInvalid(ind)`, with the comment
"LOC: not implemented". So the predicted next stop is a LOCATE — a
better place to stop than PC 0, because the next thing to build stops
being a guess.

What pp.15-16 ask of a disk, read off the transcriptions rather than
off the manual (`docs/disk_subsystem.md` §5.4's caveat 1 is
discharged there):

```
  p.15 line 26   LOC(SEOP),0.0,0.0            -POSITION TO ARC ZERO
  p.16 line 13   W(SEOP),0.0,X PRO WR         -WRITE PROSA
  p.16 line 22   CCW,0.0,X IPL BS+1.0         -ATTEMPT TO GET CW
```

and `CCW` is **MCP's write-completion poll**, not a convenience: it
reissues the `CCW` while channel-busy keeps refusing it, and the one
that finally succeeds is where the arc count comes from.

**AND p.17 ANSWERS "WHICH DEVICES".** MCP does not know its own
configuration. It reads one IOCD card per unit, converts the channel
number out of Hollerith, looks a two-letter equipment code up in
`X EQP T`, and fills in the channel and unit status tables. So the
set of devices the model must present is whatever the IOCD deck says
— which makes `strap/cards.py` and the 7503 reader part of booting
MCP, not just part of running diagnostic decks.

**Two operations moved from UNIMPLEMENTED to ENCODING_ONLY** in the
opcode ratchet because of p.17, and the pair is worth reading: `KF`
is the compare that decides whether a card IS an IOCD card, and
`LCV` is the radix conversion that turns its Hollerith channel digits
into a channel number. The two operations the model cannot execute
are the two standing between MCP and knowing what devices it has.

**The order this sets for M3+**, in the order MCP will hit them:

1. ~~`LOC` on a disk channel, the arc register, `RD`/`W` streaming
   arcs, the short-write tail zero-fill, and `CCW`~~ — **BUILT the
   same day**, `disk_subsystem.md` §9a, nineteen checks.
2. ~~A MULTI-WORD `TRANSMIT`~~ — **BUILT the same day**,
   `decks/transmit_multiword.strap`, fifteen checks.
3. ~~`LVS`, multiple indexing~~ — **BUILT 2026-10-19**,
   `decks/lvs_multiple_indexing.strap`, five checks. With it, **the
   bootstrap's indicator word has no `OP` bit: the model refuses
   nothing MCP executes.**

### M3++ — THE GATE IS NOW DATA, and this is the order from here

*Written 2026-10-19, after the three items above closed in two days.*

The bootstrap stops with `AD` and that indicator is the **tape**, not
the model: `mktape.py` writes 369 bootstrap words and a mark, so MCP
reads its PROSA dictionary out of empty tape, the `TRANSMIT`'s count
comes back zero — "never valid", Reference Manual printed p.30 — and
the transmit halts at the top of installed core. Everything below is
ordered by what unblocks what.

#### A. The critical path: make MCP run further

**A1. A PROSA RECORD ON THE TAPE.** The gate. Printed p.4 lines
19-27 give the dictionary's shape without any guessing — `LX,$X12,
X BUFER+1.0`, `LX,$X14,X BUFER+3.0`, `LX,$X11,X BUFER+5.0`,
`LX,$X10,X BUFER+7.0`, each followed by `SC,$Xn,$Xn` to bring the
count field into the value so `LVS` can sum it. So the record is
index words at odd offsets, carrying *sizes* in their count fields,
and `X1 = LVS(X12, X14)` is "words preceding MCP".
*Synthetic first, faithful later* — see the note below, because that
choice is the one judgement call in this plan.
**Unblocks: printed pp.15-18, which are transcribed and have never
executed a single row.**

**A2. `KF` AND `LCV` IN THE MODEL — DONE, 2026-10-19/20.** Printed
p.17 line 30 is the compare that decides whether a card IS an IOCD
card and line 34 is the radix conversion that turns its Hollerith
channel digits into a channel number. **They were the two operations
standing between MCP and knowing what devices it has, and both are
now built**: `KF` from printed p.65 (`decks/compare_field.strap`),
`LCV` from printed pp.71-73 (`decks/load_converted.strap`). Neither
is in `ENCODING_ONLY` any more.

`LCV` looked like the harder of the two and was not, because this
plan was wrong about what one bit meant. It said building `LCV`
"means building decimal mode, not one arm", on the grounds that the
VFL arm refuses the decimal modifier outright. But printed p.71 says
the radix modifier "describes the format of the ORIGINAL field and
also determines the type of conversion" — on a radix conversion it
selects a DIRECTION. Letting code `000011` past that one guard was
most of the work. **Decimal arithmetic is still unimplemented**, so
B1/B2 are untouched; only the conversion is built, and only
decimal-to-binary, which is the direction MCP uses.

**A2a. WORD 7'S CONNECTIVE COUNTS — DONE, 2026-10-20, the day it was
found.** `decks/connective_counts.strap` is in the suite. The
account below is kept because the scheduling is the part worth
re-reading, and `docs/NEXT.md` has the full list of what did not
work.

~~THE BLOCKER A2 UNCOVERED.~~
Closing A2 did not make printed p.17 run. Lines 32-36 convert the
channel number out of Hollerith by taking CONNECT FOR TEST's
**left-zeros count** as the digit — `$LZC` is word 7 bit 17 — and the
model does not implement the counters at all. The specification is
settled (Reference Manual printed pp.75-76) and
`decks/connective_counts.strap` is already written against it, but
the implementation is a scheduling refactor of `execute()`'s result
channel rather than an instruction: word 7 gains a second writer in a
rule that already has one, and four successive fixes each moved the
conflict rather than removing it. `docs/NEXT.md` has the full
account and the route that should work. **Do this before A3**, which
cannot be tested without it.

**A3. IOCD CARD IMAGES ON THE SYSTEM TAPE.**
~~An IOCD card deck for the reader.~~ **CORRECTED 2026-10-19 before
anything was built on it** — see `docs/mcp_io_tables.md`. The IOCD
cards are not read from a 7503 at initialization: `C22-6678-1`
printed p.29's six-step operator procedure takes the master system
TAPE plus console binary keys and mounts no deck, printed p.17
SEARCHES `X BUFER` rather than issuing a card read, and printed p.13
line 38 names that buffer "SLOTS LEFT FOR IOCD + IODS". They are card
IMAGES placed on the tape when the system was built, which is what
the off-line IBM 1401 is for.

So A3 is about the tape's content.

**THE CARD'S FIELD MAP IS NOW DERIVED, 2026-10-21**, from p.17's own
increments rather than from an outside source — the same method the
PROSA dictionary's shape got from printed p.4. Under progressive
indexing the effective address IS the index register's value and the
instruction's address field is the INCREMENT, so the walk down a card
reads straight off the rows that do it:

| offset | len | field | instruction | advance |
|---|---|---|---|---|
| 0 | 8 | card type | `CT0111(V+I)(BU,8), 1.44($4)` | 108 |
| 108 | 48 | IOCD identifier | `L(V+I)(BU,48), .48+.2($4)` | 50 |
| 158 | 7 | tens column | `CT0011(V+I)(BU,7), .12($4)` | 12 |
| 170 | 16 | units column | `CT0011(V+I)(BU,16), .22($4)` | 22 |
| 192 | 12 | equipment letter | `L(V+I)(BU,12), .24($4)` | 24 |
| 204 | 1 | channel available | `BB, .12($4)` | — |

and two more facts fall out:

* **The hunt's test falls on the identifier's leading bit.** Line 13
  is `BB, 1.44($4)` commented "-IF ZONE BIT OF IOCD", and 1.44 is 108
  bits — exactly where the identifier starts. So `X IOCD` must have
  its top bit set.
* **The hunt steps a whole word.** `CB+` is "Add one in bit position
  17" and bit 17 of a 24-bit bit address is 64 bits, which is what
  line 12's "-TEST 14 WORDS FOR FIRST IOCD" means.

`decks/mcp_p17_card.strap` runs the whole per-card path — hunt,
identify, convert, look up — over a synthetic card built to that map,
and the equipment table's 29-bit entry layout is derived the same way
(`decks/mcp_p17_equipment_code.strap`).

**WHAT IS STILL INVENTED**, and must stay labelled: the card's
CONTENTS, `X IOCD`'s 48-bit pattern, and `X EQP T`'s ten entries. All
three live on untranscribed pages.

**AND THE PAGE ITSELF NOW EXECUTES, 2026-10-21.**
`tests/run_mcp_p17.sh` runs `decks/mcp_bootstrap_p17.strap` — the
bit-exact transcription, not a paraphrase — against a synthetic card
built to the map above. It clears the working area with a 1000-word
TRANSMIT, hunts for the card, identifies it, converts the channel
number to 35, presets 64 CST entries, indexes to the right one,
clears the not-available flag, looks up the equipment code and stores
it. The entry for channel 35 comes out `0x400000600`: available, not
assigned, equipment code 6.

**The CST's one-word-per-channel indexing is derived too.** Line 37
takes the channel out of `$R` — word 9, the accumulator's right half,
where the conversion left it at offset 46, i.e. IBM bits 12-17 of
that word. `LV` copies bits 0-24 into the value field, whose address
part is bits 0-23, so the address comes out `channel << 6`: one word
per channel, which is what makes line 22's "preset 64 entries" and
line 20's `64.0` to the UST base consistent.

**Two fixture traps worth knowing**, both found by running it:
* **The harness's fill pattern is card-shaped.** Unwritten core is
  `0xAAAA...` and bit 44 of that is SET, so `BB, 1.44($4)` finds a
  card in uninitialised memory on its first test. The buffer has to
  be explicitly zeroed — standing in for the rest of the assembled
  system that would really be there.
* **Channel-available is active-low.** Line 43's `BB` branches AWAY,
  past line 44, when the card's bit is ONE; the row commented "-YES *
  CHANNEL AVAILABLE FLAG TO ON" runs only when it is ZERO.

**p.18 IS NOW RUNNING WITH p.17, 2026-10-21, so the test is the card
LOOP and not one pass through it.** p.18 starts at `(8)713.0`,
contiguous with p.17's last row at `000712.00`, and ends with `B,
X131` — back into p.17 line 26. They were always one program; they
are now run as one, and the run exits at `X 19`, the row the page
itself comments "X 19 IS THE NORMAL END", which is the loop running
out of cards.

**THE CARD STRIDE IS A PUNCHED CARD.** p.18 line 43 is `V+I, $13,
15.0` — advance to the next card by FIFTEEN WORDS. Fifteen 64-bit
words is 960 bits, and 960 = 80 columns × 12 rows: one IBM card as a
bit image, with nothing left over. The field map above was derived
from the increments WITHIN a card; this is the number that says a
card ends where a card ends. It is also the first hard constraint on
what the IOD cards on the tape have to look like, which is the rest
of this item.

**THE 29TH BIT OF AN EQUIPMENT ENTRY IS A TAPE FLAG, NOT A SPARE.**
The entry was derived from p.17 lines 46-54 as 24 bits of Hollerith
letter + a 4-bit code + 1 spare. p.18 line 2 is `BZB, -.1($1), X18`,
commented "-TAPE EQUIPMENT TYPE ENTRY", and `X18` is `(8)740.40` —
the empty low half of p.18's last word, i.e. the first instruction of
**untranscribed p.19**. So p.19 is where tape units are handled, and
the structure's own page is still missing while the second program to
read it has now named its last field.

**AND THE CST ENTRY IS DERIVED ONE PRINTED LINE AT A TIME**, which is
the form these expectations should take from here: preset (p.17
l.22), `CM0000` clearing the not-available bit (l.44), equipment
code (l.54), UST address (p.18
l.5), "meaningless assign" bit off (l.7), MULTI bit on (l.9), and
then X17's `CM0000(BU,17)` taking SEVENTEEN bits of the address back
out again (l.42) — because line 33's `BXE, X17`, "NO UNITS AT ALL ON
MULTI CHANNEL", fires for a card with no unit entries. A channel with
no units gets no unit status table. One correction en route: `SV`
stores the value AND its sign, so the 24-bit address is at bits 0-23
and the sign at 24; writing it as one 25-bit field put every bit of
it one place too low.

**What is left of A3** is narrower than it was: getting this data to
MCP the way the real system would — on the tape, as card images
placed there when the system was built — rather than preloaded by a
testbench. That needs more of MCP's loader than is transcribed, and
it is a separate job from proving the page works, which is done.

**p.40 WAS READ, 2026-10-19, AND IT MOVED THE ITEM ALONG TWICE.**

First, it NAMES THE CARD AND PLACES IT. Under "Initial Preparation
of the MCP Deck for Updating", step A lists what the punched MCP
assembly tape produces, in order:

```
 1. JOB card              11. HED card MCP Mainleg Type Area
 2. TYPE card             12. Binary cards with PUNID 11D11MCP
 3. LIM card              13. HED card MCP Loader Type Area
 4. IOD cards             14. Binary cards with PUNID 22LOADER
 5. HED card MCP Bootstrap Type Area      ... (through 20)
 6. Binary cards with PUNID 11E11BSP      21. BRANCH card.
 7. HED card IPL Type Area
 8. Binary cards with PUNID 11C11IPL
```

The cards are **IOD** cards, they sit FOURTH — immediately before the
bootstrap's own binary deck — and this page independently corroborates
two PUNIDs the transcription already carries: `11E11BSP` is the
header of the bootstrap listing pages, and `11C11IPL` is the operand
of printed p.15 line 5's `PUNID,11C11IPL`, the statement that proves
pp.3-15 and pp.16+ are one assembly.

**The column format is still not in hand**, but the page says where
it is: "For a complete writeup of the UPDATE 30 program, see page 215
of the MCP Programming Systems Analysis Guide (C22-6728), or the
bulletin published on the UPDATE 30 program (C22-6718)."
**`C22-6728` IS IN `docs/`** — the standing lesson again — and
printed p.215 = PDF 215 in the base revision. Read it; pp.216-217
already show IOD cards being used by name ("the third IOD card (for
the change tape, named CHT)", "a REEL card must be added behind the
third IOD", "IOD and REEL cards for the new IPL tape ... named
NWIPL"), so an IOD card carries at least a device name. C22-6718 is
NOT in `docs/` and is not on bitsavers.

**SECOND, AND LARGER: p.215 GIVES THE MASTER TAPE'S LAYOUT**, which
is item A1's problem, not A3's:

> "The master tape contains two binary files in odd parity, high
> density. **The first is a single record containing the IPL
> bootstrap program. The second consists of 513-word records each
> containing an image of an arc of PROSA on the disk.** Each change
> affects an entire logical unit of PROSA called a type area."

**AND THAT IS NOT NEW, WHICH IS THE INTERESTING PART.** This
paragraph first called it "a hard constraint on the PROSA fixture
that was guessed at before". It was not guessed at:
`decks/mcp_bootstrap_p14.strap` derived 513-and-512 from MCP's own
chained control words, including the one-word header per record, and
`strap/prosa.py` already says so in its header. The fixture is
shorter than one chunk deliberately.

So p.215 is an **independent second witness to a derivation**, plus
three things the derivation could not give: that there are two binary
FILES (hence the tape mark that printed p.3 only implied), that the
tape is odd parity and high density, and that each record is an image
of a disk ARC — which ties the 513 to `arcWords = 512` in
`bsv/StretchDiskSource.bsv`. Three sources, one number.

See `docs/mcp_tape_manufacture.md` §2.0, which carries the correction
in full.

**AND THE TABLES IT FILLS IN ARE ALREADY SPECIFIED.** `C22-6728-1`
Appendix A, printed pp.261-268, gives the Channel and Unit Status
Tables bit by bit, and it agrees with the transcription of printed
pp.17-18 on every bit those pages touch — including three bits whose
sense is NEGATIVE (1 means *not* available, *not* assigned) and
including which of the two tables each bit lives in.
`docs/mcp_io_tables.md` has the comparison. That is the
specification an IOCD fixture is built against, and it is also an
independent check on two pages of transcription.

**A4. THE OPERATOR'S CONSOLE (7152 + 7623).** The largest remaining
device and the one MCP's minimum configuration names that nothing
answers. MCP's ERROR ROUTINE already walks the channels looking for
it (printed p.5, `GONG`), so the model's refusal of `GONG` and of
Exchange `LOC` are part of this item rather than separate ones.

**A5. FOUR TAPES INSTEAD OF ONE.** `C22-6678-1` printed p.6's
minimum is four 729 IVs. `StretchTapeSource` is already an interface
with two implementations, so this is a vector of them and a channel
map, not new mechanism.

#### B. The ISA tail — not on MCP's path, cheap, closes the audit

Seven mnemonics set Operation Code Invalid, in three clusters:

**B1.** radix conversion — `CV`, `DCV`, `LCV`, `LTRCV`
**B2.** compare variants — `KE`, `KF`, `KFE`, `KFR`
**B3.** `LTRS`, `RNX`

and four gaps below mnemonic granularity: `LOC` on an Exchange
channel (SELECT UNIT), `TRANSMIT` backward and `SWAP`, decimal-mode
VFL, and most `CTL` function codes.

`LCV` is in B1 and `KF` is in B2, so A2 is a slice of both — which is
the argument for doing each family whole rather than cherry-picking
the two MCP needs.

#### C. Hygiene

**C1. `step()` → a `running` register.** Raised 2026-10-19: Bluespec
has a clock, and `tick` is a clock *enable* whose only load-bearing
job is keeping the core frozen while the harness loads storage one
word per clock. A `Reg#(Bool)` with `start`/`stop` is the same gate,
more idiomatic, and drops `EN_step`/`RDY_step` from the synthesised
boundary. Touches one generator (`tests/gen_tb.py`) and therefore
every testbench, plus the `CYCLES<=N` bounds, which would read the
core's own `clk` instead of the harness's counter. **Its own commit,
green either side.**

#### D. Cycle accuracy — deliberately second, per the stated ordering

**D1. Device timing.** None exists. `docs/disk_subsystem.md` §4 has
the 353's three-point seek, its rotational distribution and 8 µs per
word waiting to be imposed; the tape and reader have nothing.

**D2. The interrupt hole.** An I-box-class instruction that has
overtaken a pending look-ahead level is committed and cannot be taken
back, so an indicator set by a level is still not reported before it.
`iboxHazard` keeps it narrow; closing it needs the look-ahead to
unwind.

#### The one judgement call: synthetic PROSA

A1 can be done two ways.

*Faithful* means transcribing enough of the 451-page listing to
assemble the real PROSA record — the honest answer, and the eventual
one, but it is the whole of MCP rather than a step toward it.

*Synthetic* means building a record whose **format** is read off the
transcribed rows (which is real evidence) and whose **contents** are
a labelled fixture: a dictionary with chosen sizes and a body of
recognisable words. It makes pp.15-18 execute tomorrow, and it makes
every later transcription worth doing because there is somewhere for
it to run.

**Recommendation: synthetic first**, in a file that says so in its
first line, with the faithful record as the thing it is eventually
replaced by. The risk is the usual one — a fixture quietly becoming
evidence — and the mitigation is the one this repo already uses on
`charsets.py` and `cards.py`: say at length, in the file, what is
derived and what is chosen.

### M4 — the Diagnostic Control Program  ·  ~75 days, in slices

Transcribe in this order, each useful alone:

1. **The STRETCH MAINTENANCE COMPOOL**, PDF pp.129-130, 65 `SYN`
   entries. `archival_inventory.md` calls it "the Rosetta stone that
   resolves symbols referenced by *every other* 7030 diagnostic deck"
   — without it every other listing's symbols dangle. Two pages.
   **UNBLOCKED, 2026-10-16: see `NEXT.md` §5m.** The operator prints
   as `&` at 600 dpi but is addition — 11 of 11 rows check out against
   their own printed addresses, including one row where the glyph is
   absent entirely. Transcribe as `+` with the print recorded as a
   substitution, the way the corpus already handles `%8@n`.
2. **Panel Dump** (`H7`, pp.125-129) — dumps LC, index/boundary/
   channel registers, both accumulator halves, indicator/mask/
   remainder/factor/transit. A near-complete state dump is a debugging
   instrument for everything else here.
3. **Memory Compare** (`G5`, pp.92-93).
4. The IPL and schedule reader — makes DCP boot.
5. `J1`/`J2`, the master-tape builder — makes it self-hosting.

### M5 — the rest of the corpus under DCP

Once M4.4 and M4.5 exist, adding one of the 243 transcribed programs
to the master tape is a data operation. SSIP (`ja_ua1_ssip.pdf`) is
the error reporter every deck's `SIC,SEN / BZXL,SERS` pair branches
to, and is needed for failures to be legible rather than silent.

---

## 4. The hardware track, which is NOT on this path

Everything above runs in Bluesim. The ULX3S is **blocked on a
rewrite**, and two independent measurements say so:

- **Area:** nextpnr places no configuration on any ULX3S.
  `TRELLIS_COMB` 433-826%, while block RAM, multipliers and
  flip-flops are all comfortable. 4.3× over.
- **Depth:** `depth_census.py` reports **844 LUT levels** at
  `st_indicators`, through a divide. At the 0.436 ns/level
  carry-chain rate measured in `fpga_feasibility.md` §9 — the fastest
  path type on the part — that is 367.7 ns = **2.72 MHz against a
  3.333 MHz target.** The design misses its own clock on depth alone,
  before area.

So M0's `mkTapeSourceSD` is worth building and testing in isolation,
and the SD card is worth having working, but **"boots off the SD card
on real hardware" is gated on the multi-cycle E-box rewrite**, not on
anything in §3. Build the rewrite's instrument first — the `mkEBox`
wrapper, 2-3 days (`NEXT.md` §5j) — and use `depth_census.py` (36 s,
no P&R) as the per-commit regression metric.

---

## 5. Order of work, condensed

```
NOW      the COMPOOL (2 pages)          unblocks every other listing
         chaining test                  pack_cw already supports it
M0  1w   TapeSource file + SD, mktape.py
M1  2w   SEOP, IPL, channel signal  ->  BOOTS A TAPE IMAGE
M2  1w   KA UL1                     ->  the model writes its own tapes
M3  1w+  MCP bootstrap + disk       ->  IBM's OS starts
M4  ~75d DCP in slices              ->  the harness for 243 programs
M5       the corpus under DCP       ->  "all other extant code"

parallel: mkEBox wrapper, then the E-box rewrite, measured by
          depth_census.py -- the only route to hardware
```

**The single highest-value cheap action in this document** is the
two-page COMPOOL transcription, because every other listing in
`docs/diag/` depends on it. **The single highest-risk assumption** is
that DCP needs no disk; nothing has checked, and it should be checked
before M4 starts, the same way `$IPLD` should be read before M3.
