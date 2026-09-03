# STRAP-1 assembler

A host-language (Python) assembler for STRAP-1, the IBM 7030's symbolic
assembly language, targeting the encodings already established in
`../bsv/StretchDecode.bsv` / `../bsv/StretchExecute.bsv`. This is the
codesign half of this project: real historical Stretch programs, taken
from the Programming Examples manual, are assembled and run on the
Bluespec model, and any decode/execute gap they exercise is a genuine
finding about the hardware model, not a hypothetical one.

## Sources

- **C22-6531** *7030 Symbolic Assembly Program / Simulator* (1960) —
  the STRAP-1 language reference: the twelve symbolic instruction
  formats, arithmetic-expression and bit-address grammar, system
  symbols, and the pseudo-operations. `docs/C22-6531_7030xasm-sim_1960.pdf`.
- **C22-6578** *7030 Programming Examples* (Apr 1961) — the worked
  problems this assembler has actually been run against.
  `docs/C22-6578_7030_Programming_Examples_Apr61.pdf`. (Both this and
  C22-6531 above were cited from the start of this project but not
  actually present in `docs/` until the Problem 2.2 Method 2 work —
  re-fetched from bitsavers when this file's citations turned out to
  need checking against the real page images, not just memory.)
- **22-6530-2** *IBM 7030 Data Processing System Reference Manual* —
  same copy `../bsv/README.md` cites; needed here too for VFL
  Immediate addressing's exact field-packing rule (p.56 "Field
  Definition"), general addressing modes (p.20), and Connectives
  (p.75-77, Figure 20's sixteen logical functions).
  `docs/22-6530-2_7030RefMan.pdf`.
- **C28-6129** *STRAP-II* (1963, with April 1963 update) — downloaded
  alongside C22-6531 but not yet consulted; STRAP-II postdates
  STRAP-1 and this assembler has not been checked against it.
  `docs/C28-6129_STRAP-II_with_update_Apr63.pdf`.
- Opcode bit values are *not* re-derived from the manual independently
  here; `opcodes.py` copies them from `../bsv/StretchDecode.bsv` /
  `../bsv/StretchExecute.bsv`, which cite the manual/pocket-card
  sources directly. This is deliberate: it's what keeps the assembler
  and the Bluespec decoder from drifting apart — see "Codesign
  contract" below.

## Files

| File | Contents |
|---|---|
| `opcodes.py` | Mnemonic → bit-pattern tables, copied from the BSV decoder/executor. |
| `strap_asm.py` | Tokenizer, expression evaluator, two-pass assembler. Also a CLI: `python3 strap_asm.py program.strap` dumps the symbol table and memory image. |
| `gen_tb.py` | Generates a runnable Bluespec testbench (loader + run-until-halt + checks) from an assembled program. |
| `run_program.sh` | `strap_asm.py` → `gen_tb.py` → `bsc` → Bluesim in one step. |
| `programs/` | Assembled test programs (see below). |
| `run_tests.sh` | The whole regression suite in one step (pure-Python assembler tests first, then every program below on the model). |
| `test_syn.py`, `test_slc.py` | Pure-Python tests of the `SYN` and `SLC` pseudo-ops against `assemble()` directly. |
| `listing_oracle.py` | Compares assembled words against the machine code a historical listing prints beside each source line (the print format is decoded in its docstring). |
| `verify_ibox1_listing.py` | Assembles I-Box 1's WEN2/WEN/VEN verbatim at their listed addresses and compares every half-word to the machine code printed in the 1961 listing (`../docs/ja_ax1a_ibox-1.pdf` p.51). |
| `verify_ibox4_listing.py` | Same for I-Box 4 routine 150's CB/CB+/CBR/CBR+ blocks, their LX/SX setup and XW index words (`../docs/jb_ax4b_ibox-4.pdf` pp.155/159): 137 checks, the first external validation of `CB_CODES`, LX/SX and the packed index-word layout. |

## Usage

Run the full regression suite (the `bsv` hand-assembled smoke test plus
every program below):

```
cd stretch/strap
./run_tests.sh
```

Or run one program directly:

```
cd stretch/strap
./run_program.sh programs/problem_2_1.strap StretchProblem21Tb \
    "DOG_rotated:32=0x6e5d4c3b2a19087f"
```

Trailing arguments are checks of the form `LABEL:WORD_ADDR_EXPR=EXPECTED`,
checked against core storage after the program halts (see "Halting"
below). The generated `.bsv` is written into `../bsv/` and compiled
with the same pinned Homebrew toolchain as `../bsv/build.sh` (see
`../bsv/README.md` "Toolchain"); it is a build artifact, not meant to
be committed (`.gitignore`d at the repo root) — `run_tests.sh` cleans
it up automatically; after a standalone `run_program.sh` use, clean up
the same way by hand (`rm ../bsv/<Module>.bsv ../bsv/<Module>_sim*`),
same as `../bsv/build`/`../bsv/simbuild`.

## Programs assembled and verified so far

The instruction lines in each `.strap` file are copied verbatim from
the manual, with one exception (`problem_2_2_method3.strap`, noted in
its own entry below); each file's header comment says exactly what was
added (test data, an entry label, a `BEW, $` halt, padding) versus
what's original.

- **`problem_2_1.strap`** — C22-6578 Problem 2.1, "Cyclic Bit Shifting"
  (p.12): 3 instructions, rotate a 64-bit word left by 7 bits using
  VFL load/add/store with bit-address arithmetic and an
  accumulator-offset shift. Verified against an independently computed
  `rotate_left`.
- **`problem_2_2_method1.strap`** — C22-6578 Problem 2.2 Method 1,
  "Length of an Unknown File" (p.12): scans consecutive 7-bit bytes for
  an all-ones terminator using `LVI`/`L`/`K`/`V+`/`BZAL`/`B`/`BEW`,
  direct index arithmetic, and Branch-on-Indicator. Verified against
  the expected bit count for a known 4-byte test file.
- **`problem_2_2_method2.strap`** — the same problem, Method 2 (p.12):
  `LV`/`LI`/`K(V+I)`/`BAE`/`L(V-I)`/`BEW` — progressive indexing doing
  the address walk instead of Method 1's explicit index-register add,
  plus this project's first use of VFL **Immediate addressing** (`LI`
  is `L` with Appendix A footnote 4's `I` suffix, not its own
  mnemonic). Reuses Method 1's test data, so the expected result (28
  bits) is the same, letting the two methods cross-check each other.
  Getting this one to assemble at all surfaced two real STRAP-1 syntax
  gaps and one real encoding gap — see "Gotchas" items 8-10.
- **`problem_2_2_method3.strap`** — the same problem again, Method 3's
  *algorithm* (p.13): `CT0110` — a **Connective** (this project's first;
  `CT` = "Connect for Test", `0110` = the XOR function, Figure 20) doing
  the byte-equality test progressively, branching on the connective's
  own `$RZ` indicator (`BRZ`) instead of an arithmetic-compare
  indicator like Method 2's `BAE`. NOT a verbatim transcription: two of
  Method 3's seven lines (`LVE, $1, VF1` and `V+, $1, VF1`, its own
  `LVE`-loaded/`SIC`-encoded setup and teardown) are substituted for
  Method 2's own already-verified `LV`/`VF` setup and `L(V-I)` teardown
  — `LVE` and `SIC` are both unimplemented, and this session could not
  pin down their exact bit-level semantics from the sources at hand;
  see the file's own header for the full account and exactly what's
  substituted. Same expected result (28 bits) as Methods 1/2. Verified
  the connective function selector is actually read, not just decoded:
  swapping `CT0110` for `CT0000` (the always-0 connective) and
  confirming the loop now exits on its first iteration (`$1` = 7, one
  record, not 28) before restoring the real test.
- **`figure7_progressive_indexing.strap`** — Reference Manual
  22-6530-2 Figure 7, "Progressive Indexing" (p.22): a ten-record loop
  that adds field T to field R and stores the result in field S for
  each record, using `L(V+I)`/`+(V-I)`/`ST(V+ICR)` — format 8's
  secondary-operation syntax — plus `LX`, the `XW` control-word
  pseudo-op, and `BZXCZ`. Verified against an independently computed
  `R+T` for all ten records. Getting this one to actually pass its
  *own* ten records (not just compile) surfaced a real interaction
  with the crossing-field-store simplification — see the file's own
  padding comment and `../bsv/README.md`'s "Documented simplifications".
- **`xw_refill.strap`** — not from a manual worked example; written to
  close a gap advisor review found in the Figure 7 test above (see
  "Gotchas" item 7): a minimal program that forces exactly one
  progressive-indexing refill (`XW`'s `COUNT`=1) and checks that the
  refilled index register holds a *different*, distinctive control
  word's contents verbatim, proving the refill read the right word at
  the right (word-address, not bit-address) units.
- **`io_reader_printer.strap`** — not from a manual worked example
  either; this project's first purpose-written program for a feature
  (Input-Output) the manual documents but doesn't happen to walk
  through a worked instance of. Exercises `RD`, `W`, `CCW`, `REL` and
  their `SEOP` forms against `StretchIO.bsv`'s two simulated devices (a
  card reader, channel 32; a printer, channel 33), plus several
  discriminating checks: a wrong-unit `RD` given to the printer
  (Exchange Program Check); a channel address reached through an index
  register with no device installed (Unit Not Ready Reject, the latter
  deliberately indexed rather than a literal to exercise the
  channel-address field's own index arithmetic per p.111); a
  `SKIP`-flagged `RD` (checked against sentinel words that must survive
  untouched); and a `WSEOP` + `RELEASE SEOP` sequence built specifically
  to distinguish a correct `EOP`-suppression from an incorrect one (see
  "Gotchas" item 13's "post-milestone review" update — this last check
  is what caught a real bug in `REL`'s original implementation).
  Expected
  control-word values are derived by a companion script, `gen_io_tb.py`
  (see its own header) — this assembler's `DD` can't resolve a label to
  a numeric address the way a control word's `dataAddr` field needs, so
  `CTLW1`/`CTLW2` are zero-initialized placeholders in the `.strap`
  source, patched to real values in Python after assembly, the same
  "derive the expected result with a small script mirroring the
  hardware's own packing logic" approach Figure 7 above already uses.
  Verified against the Reference Manual's own control-word-update rules
  (p.124), with one documented, deliberate deviation (this model's
  `WRITE` doesn't reproduce the real Exchange's "+2" double-buffering
  quirk — see `StretchIO.bsv`). The channel-address field's own unit
  quirk (the 7-bit channel number sits at instruction bits 12-18, not
  the field's low-order bits, so a literal channel number must be
  written pre-scaled by `<<5`) was caught and confirmed load-bearing by
  the usual adversarial revert: breaking the model's bit-extraction
  formula predictably broke most, but not quite all, of the checks — an
  interesting finding in its own right (documented in the commit that
  landed this program): two of this specific test's channel constants
  (1024, 1056) happen to alias under one specific wrong formula, a
  coincidence of the chosen test values rather than a flaw in the
  design, and the majority of checks still caught the regression
  cleanly.
- **`io_tape.strap`** — the tape drive's own test, `StretchIO.bsv`'s
  channel 34, added the same session `CTL` first executed against a
  real device. Where `io_reader_printer.strap` proves RD/W/CCW/REL
  work, this program's whole point is proving tape POSITION is a real,
  persistent, mutable register: two successive `RD`s must return
  different data (position carries across instructions, unlike the
  reader/printer's always-restart-at-0 `devIdx`); `CTL` REWIND (octal
  136) must reset it to 0, proven by re-reading the tape's *original*
  first words, not wherever a prior `W` left off; `CTL` BACKSPACE
  BLOCK (octal 176) must move it back by exactly one, proven by
  re-reading a word already read once before; BACKSPACE BLOCK at the
  load point (position already 0) must reject with Exchange Program
  Check rather than wrap or go negative (p.136); and a count exceeding
  the tape's own (deliberately small, 16-word) capacity must trigger
  End Exception against *that* capacity, not the reader/printer's
  32-word one. 27 checks total, all passing; every one of the four
  properties above was separately confirmed load-bearing by the usual
  adversarial revert (position-restart-at-0, wrong EE capacity, and
  the load-point EPGK guard were each reverted in turn — see "Gotchas"
  item 14). Expected values derived the same way as
  `io_reader_printer.strap`'s, in a companion script
  (`gen_tape_tb.py`) that walks the exact same position transitions
  the `.strap` file's own header comment documents step by step.
- **`ibox1_wen_ven_original_addresses.strap`** — I-Box 1's WEN2/WEN/VEN
  indicator routines (`../docs/ja_ax1a_ibox-1.pdf` p.51; the I-Box
  family as a whole is documented in `../docs/archival_inventory.md`,
  alongside `ibox1_wen_ven_indicators.strap`, `ibox4_cb_count_branch.strap`
  and `ibox4_cbr_refill.strap`) placed at the *listing's own* addresses
  via `SLC` — words 2860–2865 and 3138–3139 (octal 5454–5461, 6102–6103).
  The first program to fetch, branch and load data above the model's
  old 256-word simulated core (`MemWords` is now the full 18-bit
  space). Two oracles: the model (5 indicator checks, both directions
  each, same as the low-address version) and the listing itself —
  `verify_ibox1_listing.py` assembles the verbatim lines, `BD,$` hangs
  included, and matches all nine printed half-words bit for bit.
  Verified discriminating by putting `MemWords` back to 256: all 5
  model checks then fail (fetches above the window read 0).

Every run above is a true end-to-end test: STRAP source text through
the Python assembler, through the *same* Bluespec decoder/executor
already verified by `../bsv/StretchSmoke.bsv`'s hand-assembled smoke
test, to a checked result.

## Codesign contract

The point of building this in the same repository as the Bluespec
model, sharing one opcode table, is that an instruction this assembler
emits should decode, on the model, to exactly what the assembler
intended — not "probably the same encoding, re-derived twice." Several
of the bugs and gaps caught while getting these programs to pass were
caught *because* of this: they showed up as the real decoder/executor
producing real (if wrong, or genuinely limited) behavior on assembler
output, not as a Python-side unit test passing in isolation. See
"Gotchas found by running real programs" below.

## Units: the one subtlety worth internalizing before editing this code

The assembler's location counter and every symbol value are a **bit
count** (`word*64 + bit`), matching the 7030's own `BitAddr` type. Two
different 19-bit instruction fields both look like "half-word
addresses" but are **not** in the same units — getting this backwards
was the first bug caught (see below):

- A branch/DirIndex/CountBranch/BranchInd **address field** names a
  *memory location* at half-word granularity: encode as
  `(bit_count >> 5) & 0x7FFFF`.
- An `ImmIndex` **imm field** (`LVI` et al.) sets an index register's
  24-bit VALUE field directly, which `V+`/`VF`/etc. all treat as a raw
  bit count (see `StretchExecute.bsv`'s `V+` case: it adds a `VF`
  word's value straight into an index word's `addr` field). Encode
  with **no shift**: `bit_count & 0x7FFFF`.
- An Input-Output instruction's **channel-address field** (`RD`/`W`/
  `CTL`/`LOC`/`REL`/`CCW`'s `C` operand) is left completely
  UNCONVERTED by this assembler, unlike the two cases above — but it
  is NOT simply "the channel number" either: the Reference Manual
  (p.111) places the 7-bit channel number at instruction bits 12-18 of
  the 24-bit address field, not the field's low-order bits, so the raw
  field value a program must write is `channel_number << 5`
  (`chanReader`=32 → `1024`, `chanPrinter`=33 → `1056`, `chanTape`=34 →
  `1088` — see `StretchIO.bsv`). This assembler doesn't auto-scale it,
  deliberately: see `strap_asm.py`'s `IO_OP` emit comment for why
  guessing a new subfield-aware conversion wasn't the right call here
  versus just documenting it.
- An Input-Output instruction's **second field** (`A`, the `RD`/`W`/
  `CTL`/`LOC`/`REL`/`CCW`'s `A` operand) is converted DIFFERENTLY
  depending on the operation, a genuine exception to "when in doubt,
  match an existing precedent" this codebase otherwise follows: for
  `RD`/`W`/`CCW`, `A` is a control-word core-storage address, converted
  `>>6` exactly like XW's REFILL field. For `CTL`/`LOC`, `A` is a raw
  code (a control-function code or a unit selection address, p.111) —
  NOT an address of anything — and gets NO conversion, the same "bare
  integer used as-is" treatment as `C`. This distinction only became
  visible once `CTL` had a real tape behavior to test against; before
  that, `CTL`/`LOC` decoded to Operation Code Invalid unconditionally,
  so the (wrong) `>>6` conversion on their `A` field was silently
  never exercised.

## Gotchas found by running real programs

Genuine findings from getting these programs to actually pass — this
is exactly the kind of bug real-program testing is for, as opposed to
hand-written unit tests that only exercise what their author already
had in mind:

1. **The address-field unit bug above.** Caught by hand-verifying the
   assembler's encoding of `BZAL, $+1.0` against a hand-computed target
   address *before* writing the encoder, using the worked example in
   C22-6531 itself (a location-counter-relative branch that should
   land exactly on the following `BEW, $`).

2. **Word address 0 is not general storage.** `StretchStorage.bsv`
   implements the Special Storage Assignment table faithfully: word 0
   ("Zero") always reads 0 and discards writes; words 1–15 are CPU
   registers (the accumulator lives at 8/9); 16–31 are the index
   registers. A STRAP program's ordinary code and data must not land
   in that range. `strap_asm.py`'s `assemble()` defaults to originating
   assembly at word 32 (`DEFAULT_ORIGIN_BITS`) for exactly this reason.
   Caught by `problem_2_1.strap` silently rotating nothing: `DOG`
   landed at word 0, so the store back to it was discarded and the
   load before it always read 0.

3. **Full-word instruction alignment leaves a gap straight-line code
   falls through into.** A VFL instruction is a 64-bit unit and must
   start word-aligned; when it follows a half-word instruction that
   didn't fill a whole word (`LVI` then `L(BU,7,8),...` in Problem 2.2),
   the location counter rounds up and skips a half-word. Left
   unfilled, that half-word reads back as all zeros, which decodes as
   `BE` (Branch Enabled) to address 0 — a real, wrong instruction, not
   a no-op. C22-6531's `CNOP` pseudo-op describes precisely this
   padding ("the machine instruction NOP is compiled" to bridge a
   rounding gap); `assemble()` applies that fill automatically at every
   alignment gap that precedes an instruction, rather than requiring
   an explicit `CNOP` before every full-word instruction. A gap before
   a *data* pseudo-op (e.g. `VF`'s own "LC stands at bit 25" rounding
   after a bit-precise `DD`) is left alone: dead space no program
   counter ever visits.

4. **A weak test can pass for the wrong reason.** Problem 2.1's first
   test value (`0x0123456789ABCDEF`) has its top 7 bits all zero, so
   the middle `+(BU,7),DOG` instruction adds zero — the rotate came out
   right even if that instruction's encoding were broken, because `L`'s
   57-bit left-shift alone already produces the correct low 7 bits.
   Caught in review, not by the test itself (it was passing); fixed by
   switching to a test value with nonzero top 7 bits
   (`0xFEDCBA9876543210`) so all three instructions are load-bearing.
   A related review finding, fixed the same way, was in the model
   itself, not the assembler: `StretchExecute.bsv`'s `V+`/`V+I`/`V-I`/
   `CountBranch` cases were deriving the index word's flag bit (XF)
   from whether the arithmetic result was nonzero, rather than
   preserving whatever the program had set it to — the manual treats
   bit 25 as ordinary program data the XF indicator mirrors, not
   something the ALU computes. Neither of Problem 2.1/2.2 exercises the
   flag bit, so this was a code-review catch, not a test failure; it's
   recorded here as a reminder that passing tests bound what's been
   *checked*, not what's *correct*.

5. **A crossing-field store's suppression cascades through progressive
   indexing.** Getting Figure 7's ten-record loop to actually pass (not
   just decode) meant hitting this directly: with `LIST` word-aligned,
   records 6 and 9's `S` field crosses a word boundary, so `ST(V+ICR)`
   is suppressed (`../bsv/README.md`'s crossing-field-store
   simplification) — and per the manual's own rule that a suppressed
   VFL portion suppresses the whole instruction, the index-register
   advance is skipped too, misaddressing every record after it. Fixed
   by padding `LIST` to a bit offset where none of the ten records'
   `S` fields cross (see the file's own comment for the walkthrough),
   not by changing the model: this is a real, documented limitation
   surfacing in a real program, not a bug to route around silently.

6. **A cross-arm write combination that had never occurred before
   broke `bsc`'s conflict prover, with no correctness bug in the code
   it was rejecting.** This is a toolchain finding, not an assembler
   or model bug per se — full account in `../bsv/README.md`
   "Toolchain" item 7. Recorded here too because it was progressive
   indexing's *assembler-side* implementation (this file's
   `PROGRESSIVE_SECONDARY_OP` table and the format-8 parsing in
   `classify_vfl_or_fp`) that was ready and waiting for the execute()
   side to catch up, which is what actually surfaced the bsc issue.

7. **`XW`'s REFILL field was encoded in the wrong units, and the only
   test exercising it couldn't catch that.** Every other address-like
   operand in this assembler (`VALUE`, branch targets, `ImmIndex`
   fields) is a bit count — see "Units" above. `IndexWord.refill`
   (`StretchTypes.bsv`, `Bit#(18)`) is the one exception: it's a *word*
   address, fed straight into `st.readWord(refill)` by
   `StretchExecute.bsv`'s `maybeRefill` and `BranchOrMisc`'s R/RCZ.
   `strap_asm.py`'s `XW` handler evaluated a label operand (the normal
   case — a self-referential refill to a control word like `CTLWD`)
   the same way as every other operand, packing a raw bit address into
   an 18-bit word-address field with no error and no crash: it just
   silently refilled from the wrong word (usually word 0, all zeros)
   whenever a refill actually fired. Caught by advisor review, not by
   `figure7_progressive_indexing.strap`'s own checks — that program's
   `BZXCZ` exits the loop exactly when its count reaches zero, the
   same cycle a refill would trigger, so the refill path was encoded,
   compiled, and silently never taken by the one program written to
   test it. Fixed by shifting the operand right 6 bits (bit address →
   word address, matching `emit_fp_instruction`'s existing `A18`
   conversion) before packing. Closed by a dedicated test,
   `xw_refill.strap` (see "Programs assembled and verified so far"
   above): not a Figure-7 variant, because a refill replaces the
   *entire* index word (`unpackIndexWord(st.readWord(refill))` in
   `StretchExecute.bsv`'s `progressiveIncrement`) — a mid-loop refill
   in Figure 7 would reset `VALUE` back to `LIST` too and reprocess
   records from the start, not resume where it left off. Verified the
   test actually discriminates the bug, not just the encoding: with
   the fix reverted it failed exactly as predicted (`readWord()` on an
   out-of-range bit address falls into `StretchStorage.bsv`'s
   `MemWords`-bound check and returns 0, i.e. an all-zero index word,
   not a coincidentally-correct one), and passed once restored.

8. **A VFL op's immediate-address suffix (`LI` etc.) only worked when
   no `(dds)` was given.** Appendix A footnote 4: an op like `L` may be
   suffixed `I`/`N`/`NI` for Immediate/Negative/Negative-Immediate
   addressing — `strap_asm.py`'s `classify_vfl_or_fp` already stripped
   the `I` suffix and set `immediate=True`, but only in the branch
   taken when `stmt.mods` had no dds group at all. C22-6578 Problem
   2.2 Method 2's `LI(BU,7), 127` has an explicit dds, so it hit the
   other branch, which returned with `base_op="LI"` unstripped — an
   `AssemblerError: KeyError 'LI'` at emit time, not a silent
   miscompile, but still a real gap in a construct the manual uses in
   its own worked example. Fixed by trying the suffix strip
   unconditionally, before either branch.

9. **Progressive indexing's secondary-op parenthetical can come before
   *or* after the dds, and only "before" was handled.** Every existing
   test (Figure 7, `xw_refill.strap`) happened to write it first —
   `L(V+I)(BU,7,8)`. C22-6578 Problem 2.2 Method 2 writes it *second*
   — `K(BU,7)(V+I)` — and `classify_vfl_or_fp` only ever checked
   `stmt.mods[0]` for the secondary-op keyword. With mods in the other
   order, that check silently missed it: `p_progressive` stayed
   `None`, the instruction assembled as ordinary direct-indexed
   addressing (P=0) instead of progressive (P=1), and — because
   direct addressing doesn't advance the index register the way
   progressive addressing does — the compare loop's index value never
   changed, producing an infinite loop rather than a wrong answer.
   Caught immediately (`run_tests.sh`'s step cap fired), not silently,
   but the *encoding* itself was still wrong with no error at
   assembly time — exactly the kind of gap real-program testing here
   is for. Fixed by scanning every mod for the secondary-op keyword
   instead of assuming a fixed position, verified by reverting the fix
   and confirming the step-cap failure reproduces, then restoring it.

10. **VFL Immediate addressing's operand isn't packed like every other
    address-like field — it's left-justified within its own field
    length, not placed at the low bits.** Reference Manual p.56
    "Field Definition": "the field length specifies the number of
    bits in the field starting with the *leftmost* bit of the
    effective address" — so `LI(BU,7), 127`'s `A24` field must hold
    `127 << (24-7)`, not `127`. This is independently confirmed by
    C22-6578 itself (p.13, the paragraph right after Method 2): STRAP
    must convert a bare "integer address" like `127` into a bit
    address using the instruction's *implied subfield* (here, the
    7-bit field length rather than a VFL address's usual 24), arriving
    at bit address `260096.0` — exactly `127 << 17`, matching
    `encode_vfl_immediate`'s formula by two independent routes (the
    BSV model's decode-side `immediateOperand`, and the manual's own
    worked arithmetic for this exact instruction). Verified the fix is
    load-bearing, not just plausible: reverting `encode_vfl_immediate`
    to a plain unshifted pack produced a clean, non-coincidental wrong
    answer (`0x23...` instead of `0x1c...`), not a lucky pass. Note
    C22-6578 frames "integer address → bit address via the implied
    subfield" as a *general* STRAP rule, but this assembler implements
    the conversion only for the immediate-addressing case above — a
    bare integer given as a normal (non-immediate) address field is
    used as-is via `eval_expr`, with no subfield-aware scaling. Every
    program here uses dotted bit-address notation or a label for
    non-immediate addresses, so that gap is untested, not fixed — see
    "Next steps".

11. **`(radix)digits` literals only work inside `DD`, not in general
    expressions.** C22-6578's own Method 3 writes `LI(BU,7), (2)1111111`
    — the manual treats a radix literal as usable anywhere a number is
    (same as the decimal `127` it's equal to). `strap_asm.py`'s
    `parse_dd_literal` (the `(\d+)([0-9A-Za-z]+)` regex match) is
    called only from `DD`'s own field parsing, not from the general
    `eval_expr` every instruction operand goes through — so the exact
    line as printed fails to assemble (`cannot parse expression
    '(2)1111111'`), a clean error, not a silent misparse. Worked
    around in `problem_2_2_method3.strap` by writing `127` instead
    (the two are declared equal by the manual's own comment on the
    same instruction in Method 1: "or decimal 127"). Not fixed — see
    "Next steps".

12. **Two manual-worked-example instructions (`LVE`, `SIC`) turned out
    to be genuine dead ends, not just unimplemented.** Chasing C22-6578
    Problem 2.2 Method 3's exact transcription led to `LVE` ("Load
    Value Effective", Reference Manual p.20's "indirect addressing")
    and `SIC` ("Store Instruction Counter If", used in Method 3 purely
    as a source of a specific bit pattern, per its own comment (a)
    "loads the magnitude of the dummy SIC instruction"). Both are
    already listed as out of scope in `../bsv/README.md` ("RNX/LVE/SVA
    ... out of scope"; SIC likewise). This session tried to pin down
    exact bit-level semantics for both, from the general p.20
    "Address Modification" text and the Direct Index Arithmetic
    chapter (pp.22-27), and could not find enough to implement either
    with confidence — p.20 describes LVE only at the conceptual level
    ("the effective address is used to obtain a second level effective
    address"), never at the instruction-format/field level the way LX
    through KC each get their own paragraph. `SIC` is different:
    `StretchDecode.bsv` already has a bit-format for it from an earlier
    milestone (address + index + an embedded half-word branch
    instruction, sourced from p.~100's "bits 32-63 specify the
    half-word branch instruction used") — it's *decoded*, just not
    executed (`bsv/README.md`'s "Decoded but not executed" list). What
    this session couldn't pin down is the STRAP-level assembler syntax
    and the semantic condition under which the instruction counter
    actually gets stored, needed to write and verify a real SIC line
    rather than just decode one. Rather than guess and risk a
    falsely "verified" result, `problem_2_2_method3.strap` substitutes
    Method 2's own already-verified `LV`/`VF` setup and `L(V-I)`
    teardown for Method 3's `LVE`/`SIC` ones, keeping the actual new
    feature under test (the `CT0110`/`BRZ` connective compare) exactly
    as printed. See that file's own header comment for the full
    account, and `../bsv/README.md`'s "Direct index arithmetic" for
    the model-side note.
13. **Input-Output landed as a whole new subsystem, not just a new
    opcode.** Unlike every prior milestone (a new instruction executing
    against existing storage), `RD`/`W`/`CTL`/`LOC`/`REL`/`CCW` needed
    a whole simulated device layer (`StretchIO.bsv`) and a genuinely
    multi-cycle transfer FSM in `StretchCore.bsv` (one word drained per
    `step()` call, generalizing the two-cycle `pendingIdxWrite`
    mechanism to N cycles) before there was anything to assemble
    against. Two real gaps found before any STRAP code was written:
    (a) `execute()`'s original three-way write-conflict risk (general
    storage, index register, *and now* a device word, all potentially
    in one rule) meant the transfer had to be threaded out as a
    descriptor and drained by the caller, exactly like progressive
    indexing's index write already is — not a new problem, but the
    first case needing the *same* fix generalized past one deferred
    write; (b) attempting to size `StretchStorage`'s memory for a
    DCP-sized program (`MemWords` 256→8192) to make room for real I/O
    content sent `bsc`'s elaborator to 1.5TB+ RAM with no sign of
    finishing — killed, not chased further; a real fix needs a
    BRAM-backed storage module, not a bigger `Vector`, and is out of
    scope for this milestone (see `../bsv/README.md` "Toolchain" item
    8). Also found the channel-address field's `<<5` unit quirk (see
    the "Units" section above) and, via the adversarial revert on it,
    an unrelated coincidence worth knowing about if this test's own
    constants are ever changed: `chanReader<<5` (1024) and
    `chanPrinter<<5` (1056) alias to the same wrong channel under one
    specific incorrect bit-extraction formula (`1056 mod 128 == 32`),
    which let 4 of 10 checks pass despite the deliberately broken
    build (the 3 `DEST` transfer checks plus the unrelated `UNRJ`
    indicator check) — the other 6 (every control-word and printer-
    content check) still failed as predicted, so the revert test still
    did its job, but a cleaner set of test constants would avoid the
    coincidence entirely.

    **Update, same day: post-milestone review caught two real bugs, not
    just untested code.** `StretchIO.bsv`'s header claimed `SKIP` "IS
    honored"; it wasn't — `IoXfer` had no `skip` field at all, and the
    transfer FSM's read arm was an unconditional `st.writeWord`, so a
    skip-flagged `RD` wrote core storage exactly like a normal one, the
    opposite of what the header said. Separately, `REL`'s code
    unconditionally set `cw.eop = 1`, ignoring its own `SEOP` flag,
    contradicting the manual's explicit statement (p.121) that "no EOP
    indication is ever given at the completion of a RELEASE SEOP" —
    `RELSEOP` decoded correctly but executed identically to plain
    `REL`. Both are one-line fixes (a `skip` field plus one `if` in the
    FSM's read arm; one `if (!seop)` guard on `REL`'s `cw.eop = 1`),
    but neither was caught by the original test program, which never
    exercised `SKIP` or `RELSEOP` at all — a gap in test *coverage*,
    not just a documentation slip. Fixed both, extended
    `io_reader_printer.strap` with a `SKIP`-flagged `RD` (checked via
    sentinel words in a `DEST2` block that must survive completely
    untouched) and a `WSEOP` + `RELSEOP` sequence specifically
    constructed so the bug and the fix produce different `EOP` bits
    (`CCWF_after_RELSEOP`), then adversarially reverted each fix in
    turn: the `SKIP` revert produced exactly the 3 predicted `DEST2`
    failures and nothing else; the `RELSEOP` revert produced exactly
    the 1 predicted `CCWF` failure and nothing else. Both reverts
    restored and the full regression suite reconfirmed passing before
    this note was written.

14. **The tape drive needed real primary source before it could be
    real, not a renamed card reader.** The user's original request
    named "tape drives" explicitly; the reader/printer milestone had
    stopped short of them, and `CTL`/`LOC` had stayed unimplemented
    because the External Units chapter (Reference Manual pp.129-149)
    was, at that point, genuinely unread — the earlier `StretchIO.bsv`
    said so plainly. This session actually read it (pp.111, 126-137)
    before writing any tape code, and it settled three design questions
    that would otherwise have been guesses: (a) CONTROL's right
    effective address is a raw function code, not a core-storage word
    address the way RD/W/CCW's is (p.111) — meaning `strap_asm.py`'s
    existing `>>6` word-address conversion for that field was *wrong*
    for `CTL`/`LOC` specifically, a real bug in the assembler caught
    only because there was finally a real CTL behavior to test the
    conversion against; (b) the exact octal function codes for REWIND
    (136) and BACKSPACE BLOCK (176), and the load-point rejection rule
    (p.136: "the tape cannot be moved... beyond the load point. Any
    backspace instructions given with the tape in this position are
    terminated with an exchange-program-check indication"); (c) LOCATE
    exists to select one of up to eight tape units behind a shared tape
    control (p.133) — a hierarchy this model deliberately sidesteps by
    putting exactly one tape unit directly on its own channel, the same
    shape as the reader and printer, documented as a simplification
    rather than left as an unread gap. Two devices (`isReader`/
    `isPrinter`) had already been called out by post-milestone review
    as a shape that "does not survive a third device" — generalized
    into a `DeviceKind` enum + `kindOf` function in `StretchIO.bsv`
    before writing the tape's own storage, exactly where the advisor
    said the investment belonged for a future microcontroller port.
    The property that actually makes a tape a tape — position
    persisting across instructions, rather than every `RD`/`W`
    restarting at device index 0 like the reader/printer do — needed a
    dedicated `TapePos` register one bit wider than the tape's own
    index type (the same "room for one past the end" idiom `IoXfer`'s
    `devIdx` already used relative to `DeviceIndex`), threaded through
    `StretchExecute.bsv`'s transfer-start logic and `StretchCore.bsv`'s
    per-word FSM. Three properties were adversarially reverted in
    turn — position always restarting at 0, the End Exception capacity
    check using the reader/printer's `DeviceWords` instead of the
    tape's own smaller `TapeWords`, and the load-point BACKSPACE
    rejection — and each produced exactly the predicted failures (12,
    1, and 7 respectively) with nothing else breaking, then was
    restored and reconfirmed. `io_tape.strap`'s 27 checks passed
    cleanly on the very first real run, with no debugging needed beyond
    the adversarial-revert passes themselves — a contrast with the
    reader/printer milestone's own first-pass 6/10 partial-fail
    surprise (item 13), attributable to reading the primary source
    fully before implementing rather than mid-implementation.
15. **The listings print their own machine code — the strongest
    encoding oracle available, and it was sitting unused.** Every I-Box
    and DCP page prints, beside each source line, the word IBM's own
    assembler produced: per half-word, bits 0-17 as a 6-digit octal
    word address, "." and bits 18-23 as two octal digits, then bits
    24-31 as two hex digits (a full word is two such groups; `VF`
    prints its 24-bit value as W.B plus a sign; `DD(BU,64,8)` prints
    22 octal digits). Decoded from I-Box 1's WEN block (`BRGZZ,$+1.0`
    at 5455.00 printing as `5456.35 46` pins bit 18 as the half-word
    select) and then applied to I-Box 4 routine 150 pp.155/159 —
    `verify_ibox1_listing.py` and `verify_ibox4_listing.py`, on the
    shared `listing_oracle.py`. Results: all 9 WEN half-words and all
    137 I-Box 4 checks match bit for bit, first run. That is the first
    validation from outside this project of `CB`/`CB+`/`CBR`/`CBR+`
    (previously pocket-card-only), `LX`/`SX`, `VF`, `NOP`, `BD`/`B`,
    the VFL `L` field packing — and of the packed index-word layout
    `StretchTypes.bsv` assumes: the listing's `XW,IBR9+(8).04,4,-1`
    printing as `11445.04 00 000117.77 FF` puts count=4's low bit at
    bit 43 and the refill at 46-63, and `XW,IBRA9+(8).04,3,IBRA10`
    carries IBRA10's word address 011610 verbatim in its refill field
    (count at bits 28-45, refill a word address — exactly
    `packIndexWord`, and exactly item 7's `>>6` conversion). That
    closes the caveat `ibox4_cb_count_branch.strap`'s header had
    recorded ("not proof the model's packing matches real 7030
    hardware"). Discrimination checked by injection: encoding `CB+`
    with `CB-`'s code fails exactly the 4 `CB+` rows; shifting the
    XW count field one bit fails exactly the 6 XW rows; nothing else
    moves. Two assembler gaps the verbatim source exposed and closed
    on the way: `(R)` radix literals in address expressions
    (`(8).04`, `(8)37777`, `VF,(8)777777.70`) and the bare `NOP,`
    placeholder form. Symbols defined outside the transcribed range
    (`LORE*`, `CBER*`) are `SYN`'d from the same printed column, so
    their rows verify only opcode/modifier bits — said so in the test,
    not glossed. **Reusable: for any future transcription, transcribe
    the printed-code column alongside the source and run it through
    `listing_oracle.py` before running anything on the model — it
    finds encoding bugs with no model, no expected-value derivation,
    and no bug injection needed.**

## Halting

A runner needs a way to know when the program is done rather than
stepping a fixed count. STRAP's own idiom for this is `BEW, $` — branch
to the location counter's own value, i.e. branch to itself
(C22-6531 p.14, and used verbatim at the end of every example program
above). `StretchCore.step()` (see `../bsv/StretchCore.bsv`) returns
`True` when an instruction's computed next-PC equals its own address,
and `gen_tb.py`'s generated runner steps (with a hard cap as a
safety net) until that fires. A progressive-indexing instruction takes
two `step()` calls to complete (see `../bsv/README.md`'s "Toolchain"
item 7); both return `False`, so this doesn't affect halt detection.

## Scope

Mirrors the "decode completely, execute partially, document the rest"
approach of the Bluespec model itself — see each module's docstring,
especially `strap_asm.py`'s, for exactly which of the twelve symbolic
instruction formats and which pseudo-operations are implemented, not
implemented (and why), or implemented but not yet exercised by any
program run through this assembler.

`SLC` ("Set Location Counter", C22-6531 p.32) is implemented as of the
original-addresses milestone — see `strap_asm.py`'s docstring for the
rules pinned down (bit-count operand, no forward references, name
field ignored) and `test_slc.py` for each one under test.

Notably **not** implemented yet: multi-word Transmit — the same gap
`../bsv/README.md`'s "Next steps" names on the execute side. Also not
implemented: `LVE`/`SIC` (see "Gotchas" item 12), VFL Immediate's
`N`/`NI` suffixes, and `(radix)digits` literals outside `DD` (item 11).
Progressive indexing (format 8) and Connectives *were* both in this
list as of earlier milestones; both are now implemented on both sides
(assembler and `StretchExecute.bsv`) and verified — progressive
indexing against Figure 7, Connectives against Problem 2.2 Method 3's
`CT0110` — above. Input-Output (`RD`/`W`/`CTL`/`LOC`/`REL`/`CCW`) is
new this milestone too: `RD`/`W`/`CCW`/`REL` are implemented on both
sides and verified against `io_reader_printer.strap` (above). `CTL`
executes, but only against the tape channel and only its two
implemented function codes (REWIND, BACKSPACE BLOCK) — verified
against `io_tape.strap`; CTL issued to the reader/printer, and every
other tape function code the External Units chapter documents (SPACE
BLOCK/FILE, WRITE TAPE MARK, BACKSPACE FILE, density/ECC/parity/light
functions), still falls through to Operation Code Invalid. `LOC`
assembles but is not executed at all — see `StretchIO.bsv`'s
"INSTRUCTIONS" for why (a documented simplification, not an unread
chapter, now that the External Units chapter has in fact been read).
See `../bsv/README.md`'s "Executed" section and `StretchIO.bsv`.

**What's actually been assembled and run**, as opposed to merely
present in `opcodes.py`'s tables, is much narrower than what's
implemented: `L`, `LI`, `+`, `ST`, `K` (VFL, binary unsigned, direct,
immediate, and progressive addressing), `CT` (one Connective, `CT0110`
= XOR, progressive addressing), `LVI`, `LX`, `LV`, `V+`,
`BZAL`/`BAE`/`BRZ`/`BZXCZ` (Branch on Indicator), `B`, `BEW`, `NOP`,
`RD`, `W`, `CCW`, `REL`, `CTL` (Input-Output, direct and
index-register-selected channel addressing, all three simulated
devices — reader, printer, tape), `DD`, `VF`, `XW`, `END`. Of the
Input-Output SEOP forms, `W SEOP` and `REL SEOP` are exercised (the
latter caught a real bug — `REL SEOP` originally ignored its own
`seop` flag and set EOP unconditionally, found by post-milestone
review, not a test program, and fixed with a distinguishing test added
in the same commit); `RD SEOP`, `CTL SEOP`, and `LOC SEOP` are encoded
and generated by `IO_OP` but have never been assembled into a test —
`RD SEOP` shares the exact same suppress-EOP code path `W SEOP`
already exercises, so it's lower-risk than `REL SEOP` was, but
"lower-risk" is not "verified." The other ~75 VFL/FP/DirIndex/ImmIndex
mnemonics in `opcodes.py`, every other Connective (only `CT0110`, plus
`CT0000` transiently as a discriminating check — see "Programs
assembled and verified so far" above), the `-` → invert-bit path,
`CB`, `LOC`, and floating point end to end are implemented against the
same tables and citations as everything else here, but have never been
exercised by an assembled-and-run program — treat them as unverified
until one has.

## Next steps

0. **Transcribe real historical STRAP source, not just worked
   examples.** `../docs/archival_inventory.md` inventories bitsavers'
   `diag/`/`ce/`/`mcp/` collections: the Diagnostic Control Program
   manual (`diag/ka_ua1_diagnostic_ctl_pgm.pdf`) turns out to contain a
   complete, unbroken ~130-page STRAP source listing, with two
   self-contained routines (Memory Compare, Panel Dump) that need no
   I/O emulation and are assemble-and-run candidates today — see that
   doc for the recommended transcription order (the shared MAINTENANCE
   COMPOOL symbol table first) and for the five I-Box diagnostic
   programs recommended as the next inventory target after that.
1. `CNOP`, `CF`, `RF`, `DDI`, `CW`, `EXT` — pseudo-ops C22-6531
   defines that no program exercised yet (`SYN` and `SLC` were on
   this list; both are now implemented and tested).
2. Verify the opcode table exhaustively against `7030_Opcode_List.pdf`
   (the rendered pages, not its noisy OCR — see `../bsv/README.md`
   "Next steps", inherited here unchanged).
3. Format 8's `J'` (`i2`) field: encoded but not executed (see the
   "Scope" note on format 8 above) — `StretchExecute.bsv`'s `VflInt`
   case would need to read `vi.a.i2` and apply the manual's "modify
   bits 35-50 of the instruction" behavior (p.21). No program has
   needed this yet (`figure7_progressive_indexing.strap` writes `, 0`).
4. VFL Immediate addressing's `N`/`NI` suffixes (Negative/Negative-
   Immediate, Appendix A footnote 4) — only `I` is stripped by
   `classify_vfl_or_fp` today; `N`/`NI` fail loud (`AssemblerError`,
   unrecognized mnemonic) rather than being silently mis-handled, but
   no program has needed them yet either.
5. The general "bare integer address → bit address via the implied
   subfield" rule (C22-6578 p.13) is implemented only for VFL
   Immediate addressing (`encode_vfl_immediate`) — see "Gotchas" item
   10's note. A bare (non-"point") integer given as a normal address
   field elsewhere is used as-is, unconverted. Untested (every program
   here uses dotted notation or labels for non-immediate addresses),
   not yet a confirmed bug.
6. ~~`(radix)digits` literals (`parse_dd_literal`) outside `DD` — see
   "Gotchas" item 11.~~ Done: `(R)` prefixes now parse in any
   expression (item 15), needed by the I-Box 4 listing's own
   `(8).04` / `(8)37777` / `VF,(8)777777.70` forms.
7. `LVE`/`SIC` — see "Gotchas" item 12; would need primary-source
   material this session didn't find (or a decision to reverse-engineer
   the exact bit patterns from first principles instead).
8. Connectives' `BS`<8 byte-padding, Partial Field, and the left-
   zeros/all-ones counts at word 7 (p.75-77) — see
   `../bsv/README.md`'s "Connectives" scope note.
9. Input-Output: `SKIP`, `W SEOP`, `REL SEOP`, and the End Exception
   path are all now exercised (`io_reader_printer.strap`,
   `io_tape.strap` — see "Gotchas" items 13-14; the tape's own
   deliberately-small `TapeWords` made EE reachable with an ordinary
   count for the first time). `CTL` now executes, but only against
   tape and only two of the External Units chapter's documented
   function codes (REWIND, BACKSPACE BLOCK) — SPACE BLOCK/FILE, WRITE
   TAPE MARK, BACKSPACE FILE, and the density/ECC/parity/light
   functions are real, primary-sourced codes (p.130-132) this
   implementation still doesn't execute (SPACE FILE/BACKSPACE FILE/
   WRITE TAPE MARK need a tape-mark concept this word-addressed model
   doesn't have; the rest have no observable effect on a model with no
   framing/parity/light state to toggle). `LOC` is not implemented at
   all — this model's one-tape-unit-per-channel simplification
   sidesteps the channel→control→unit selection hierarchy LOC exists
   to navigate (see `StretchIO.bsv`'s "INSTRUCTIONS"); implementing it
   for real would mean modeling multiple tape units behind a shared
   control, a bigger step than anything else in this list. Still
   untested: `RD SEOP` and `CTL SEOP`/`LOC SEOP` (encoded, never
   assembled into a program — `RD SEOP` is lower-risk since it shares
   `W SEOP`'s already-exercised code path, but "lower-risk" isn't
   "verified"). Also worth doing: give `DD` (or a new pseudo-op) the
   ability to resolve a label to a numeric value, which would let a
   control word's `dataAddr` field be written directly in STRAP source
   instead of needing a companion Python patcher like `gen_io_tb.py`/
   `gen_tape_tb.py` — worth doing generally, not just for I-O, if more
   programs end up needing label-valued `DD` fields.
