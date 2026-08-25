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
  Definition") and general addressing modes (p.20).
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
the manual; each file's header comment says exactly what was added
(test data, an entry label, a `BEW, $` halt, padding) versus what's
original.

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

Every run above is a true end-to-end test: STRAP source text through
the Python assembler, through the *same* Bluespec decoder/executor
already verified by `../bsv/StretchTb.bsv`'s hand-assembled smoke
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

## Gotchas found by running real programs

Genuine findings from getting these two programs to actually pass —
this is exactly the kind of bug real-program testing is for, as
opposed to hand-written unit tests that only exercise what their
author already had in mind:

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

Notably **not** implemented yet: multi-word Transmit — the same gap
`../bsv/README.md`'s "Next steps" names on the execute side.
Progressive indexing (format 8) *was* in this list as of the previous
milestone; it's now implemented on both sides (assembler and
`StretchExecute.bsv`) and verified against Figure 7 above. Problem
2.2 Method 2 (also progressive indexing) is a ready-made next test
case, already transcribed from the manual.

**What's actually been assembled and run**, as opposed to merely
present in `opcodes.py`'s tables, is much narrower than what's
implemented: `L`, `+`, `ST`, `K` (VFL, binary unsigned, direct and
progressive addressing), `LVI`, `LX`, `V+`, `BZAL`/`BAE`/`BZXCZ`
(Branch on Indicator), `B`, `BEW`, `NOP`, `DD`, `VF`, `XW`, `END`. The
other ~75 VFL/FP/DirIndex/ImmIndex mnemonics in `opcodes.py`, the `-`
→ invert-bit path, the `I`-suffix immediate-addressing path (Appendix
A footnote 3), `CB`, and floating point end to end are implemented
against the same tables and citations as everything else here, but
have never been exercised by an assembled-and-run program — treat them
as unverified until one has.

## Next steps

1. `CNOP`, `SLC`, `CF`, `RF`, `DDI`, `SYN` (as a symbol-defining op,
   not just a no-storage placeholder), `CW`, `EXT` — pseudo-ops
   C22-6531 defines that no program exercised yet.
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
5. Problem 2.2 Method 3 (p.13: "Use connective and branch on `$RZ`")
   — transcribed in the manual right after Method 2 but needs a
   Connective op (`CT0110`) this assembler doesn't implement yet
   (Connectives aren't in `VFL_INT_CODES`/`StretchExecute.bsv` at all
   — see the "Connectives" item in `../bsv/README.md` "Next steps").
6. The general "bare integer address → bit address via the implied
   subfield" rule (C22-6578 p.13) is implemented only for VFL
   Immediate addressing (`encode_vfl_immediate`) — see "Gotchas" item
   10's note. A bare (non-"point") integer given as a normal address
   field elsewhere is used as-is, unconverted. Untested (every program
   here uses dotted notation or labels for non-immediate addresses),
   not yet a confirmed bug.
