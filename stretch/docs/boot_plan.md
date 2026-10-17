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
| 8 | **SEOP status bit 24** | `StretchIO.bsv` | ~10-20 lines |
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

### M3 — MCP's bootstrap  ·  ~4 days transcription + the disk

Printed pp.2-14, ~350 rule-3 rows, ~1.3× the largest program already
in the corpus. The IPL control word is on p.2 and verified. **It loads
from tape alone** (§5i), so M1 is sufficient to *start* it. To let it
*finish* add the disk: ~100-170 lines for the boot-sufficient subset,
since the bootstrap carries a 42-entry `PROSA CWS` table and can
report `PROSA ARC COUNT INCORRECT`.

**Before starting, read `$IPLD`, printed pp.15-36** — 22 pages, 3
sampled. It is cheap and it bounds how much disk is really needed.

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
