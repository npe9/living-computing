# Phase 2 arm inventory: BRAM storage migration

Written before starting the actual FSM conversion (readWord ->
readWordReq/readWordResp, and staging every `execute()` case arm that
touches general storage), per advisor's explicit instruction: this is
the conversion checklist AND the coverage evidence, made durable
before the reasoning behind it is gone to a future compaction. See
`bsv/README.md` "Next steps" item 6 for the design this inventory
implements against.

## Design settled before this inventory (see bsv/README.md item 6 and
## git history for the reasoning)

- Addresses 0-31 (all "special" registers, including index registers
  16-31) stay `Reg`-backed and architecturally never move to BRAM.
  `readIndex`/`readIndicators`/`writeIndex`/`setIndicatorBits` are
  separate methods, untouched by this migration, and stay single-call/
  instant.
- `readWord` becomes a uniform two-method request/response pair
  (`readWordReq`/`readWordResp`) used by EVERY caller alike, addr<32
  included -- callers don't know an address's range until after
  computing it (Phase 1 finding: ~2 of ~26 sites do), so there is no
  caller-visible dispatch on range. addr<32's "response" is simply
  resolved out of the live Reg state at `readWordResp()` time (not
  buffered early), deferring the special-address case lookup by
  exactly one call, same as a genuine BRAM read's latency.
- `writeWord` stays a single-cycle `Action` (no response needed,
  `responseOnWrite: False`) for both Reg and BRAM addresses alike --
  only reads need the split.
- A single `BRAM1Port`/`mkBRAM1Server` (not two ports) is sufficient:
  confirmed by probe that `request.put()` + `response.get()` in the
  SAME rule is allowed (pipelined issue-next/collect-previous, the
  scheme every multi-read arm below depends on for M+1 rather than 2M
  cycles), and by inventory below that no arm ever needs a read-request
  and a write-request to BRAM in the literal same cycle -- every
  read+write co-occurrence in this codebase is a *dependent* chain
  (the write's DATA comes from the read's response), which naturally
  serializes into separate cycles anyway. Two independent puts
  (read+read or read+write) on ONE port in ONE rule were confirmed
  disallowed by `bsc` (`BramProbe3.bsv`, `(G0004)` conflict on both
  `bram_memory.put` and the write-response adapter's `wset`).
- Case arms within one `case` statement are mutually exclusive by
  construction (only one fires per rule invocation), so cross-arm
  storage-port conflicts are not a concern -- only conflicts WITHIN a
  single arm's own body matter.

## How to read the table

- **Reads**: count and addresses of `st.readWord` calls this arm makes
  (via itself or a helper: `readField`, `readAcc`, `readHW`,
  `maybeRefill`, `progressiveIncrement`, `readFieldWithHi`). Reg-only
  addresses (8, 9, and index registers via `readIndex`) are noted as
  such -- they still cost a `readWordResp` round-trip under the
  uniform interface, but touch no BRAM state.
- **Writes**: count of `st.writeWord` calls (always single-cycle,
  regardless of dependency).
- **Dependent?**: whether a write's DATA is computed from a prior
  read's response (true RMW chain, must serialize: issue read -> get
  response -> issue write) vs. independent reads whose addresses are
  all known upfront (can pipeline: issue all N requests across N
  cycles, collect responses starting one cycle behind).
- **Coverage**: which STRAP program(s) exercise this arm, established
  by grepping `strap/programs/*.strap` and `strap/opcodes.py` for the
  arm's mnemonic(s) -- NOT assumed. "NONE" means grepped and confirmed
  absent; "not yet disambiguated" means the mnemonic search was
  inconclusive (usually because the same mnemonic string is used by
  two different opcode formats and telling them apart requires tracing
  `strap_asm.py`'s parse, not done here) and should be resolved before
  converting that arm, not assumed safe.

## VflInt (VFL Integer arithmetic, `tagged VflInt`)

| Arm | Reads | Writes | Dependent? | Coverage |
|---|---|---|---|---|
| L (Load) | 0-1 (`readField(ea)`, 0 if immediate; crossing case = 2, independent) | 0 BRAM (`writeAcc` is addr 8/9, Reg-only) | no (read feeds a Reg write only) | problem_2_2_method2/3 (`L`, though see FP note below on disambiguating from FP's `L`) |
| ST (Store) | Reg-only (`readAcc`, addr 8/9) | 1 (`writeField`: internal RMW read + write) | yes, RMW inside `writeField` | problem_2_1, xw_refill (`ST(V+ICR)`) |
| + (Add) | 0-1 (`readField(ea)`) + Reg-only (`readAcc`) | 0 BRAM (`writeAcc`, Reg-only) | no | problem_2_2_method1/3 (`+,`) |
| M+ (Add to Memory) | 1 (`readFieldWithHi(ea)`) + Reg-only (`readAcc`) | 1 (`writeFieldWithHi`, no internal read -- dedup landed this session) | yes (write uses the read's `hi` + computed sum) | **NONE** (grepped `opcodes.py`'s `M+` key against all programs, zero matches) |
| K (Compare) | 0-1 (`readField(ea)`) + Reg-only (`readAcc`) | 0 (comparison only) | no | problem_2_2_method1/2 (`K(...)`) |
| progressiveIncrement (shared, when `isProgressive`) | 0-1 (refill, only P=3/7) | 0 (index write-back happens in `StretchCore.step`, separately) | no | figure7_progressive_indexing (explicit purpose of that program) |

## DirIndex (Direct Index Arithmetic, `tagged DirIndex`)

| Arm | Reads | Writes | Dependent? | Coverage |
|---|---|---|---|---|
| LX | 1 (`st.readWord(ea[18:1])`) | 0 | no | figure7, xw_refill |
| SX | 0 | 1 (`st.writeWord`, value from `readIndex`, Reg-only) | no | **NONE** (grepped for standalone `SX`, zero matches) |
| LV | 1 (`readHW(ea)`) | 0 | no | problem_2_2_method2/3 (`LV,`) |
| SV | 1 (`readHWWithWord(ea)`) | 1 (`writeHWWithWord`, no internal read -- dedup landed this session, commit `b24e51b`) | yes (write uses the read's raw word + new half) | **NONE** |
| LC | 1 (`readHW(ea)`) | 0 | no | **NONE** |
| SC | 1 (`readHWWithWord(ea)`) | 1 (`writeHWWithWord`, deduped) | yes | **NONE** |
| LR | 1 (`readHW(ea)`) | 0 | no | **NONE** |
| SR | 1 (`readHWWithWord(ea)`) | 1 (`writeHWWithWord`, deduped) | yes | **NONE** |
| V+/V+C/V+CR | 1 (`readHW(ea)`) + 0-1 (`maybeRefill`, only V+CR) | 0 (index write-back only, Reg-only) | no | **NONE** as a standalone DirIndex opcode (the `V+I`/`V+ICR` strings that DO appear in figure7/xw_refill/method2/3 are the VflInt *progressive-addressing suffix*, a different namespace per `opcodes.py`'s own comment -- confirmed by reading, not assumed) |
| KV | 1 (`readHW(ea)`) | 0 | no | **NONE** |
| KC | 1 (`readHW(ea)`) | 0 | no | **NONE** |

**DirIndex is the least-covered format in the whole inventory**: only
LX and LV (both pure single-read, no-write arms) have any test
coverage at all. SV/SC/SR/KV/KC/V+/V+C/V+CR/SX are all unexercised.

## ImmIndex (Immediate Index Arithmetic, `tagged ImmIndex`)

All arms are index-register-only (read via `readIndex`, write via the
`idxWriteVal`/`doIdxWrite` path -> `st.writeIndex` in the caller) with
ONE exception: V+IC/V+ICR/V-IC/V-ICR call `maybeRefill` (0-1 read,
independent, refill address known from the index word already read).
No arm here ever touches BRAM general storage directly. Coverage not
separately chased since these arms carry effectively zero Phase-2
risk (at most one independent Reg-or-BRAM read, no write dependency).

## CountBranch (`tagged CountBranch`)

0-1 read (`maybeRefill`, only when `cb.refill == 1`), independent
address, no write dependency. Low risk; coverage not separately
chased for the same reason as ImmIndex.

## BranchInd (`tagged BranchInd`)

Zero storage access of any kind (pure indicator test + index-only
branch target). No Phase 2 work needed for this arm at all.

## BranchOrMisc (`tagged BranchOrMisc`)

| Arm | Reads | Writes | Dependent? | Coverage |
|---|---|---|---|---|
| B/BR/BE/BD/BEW/NOP | 0 | 0 | n/a | all 8 programs (BEW alone is the halt idiom every program ends with) |
| Z (Store Zero) | 0 | 1 (`st.writeWord(..., 0)`) | no | **NONE** (grepped for standalone `Z` opcode usage, zero matches) |
| R (Refill, unconditional) | 1 (`st.readWord` at refill address) | 0 | no | **NONE** |
| RCZ (Refill on Count Zero) | 0-1 (conditional on `x.count==0`) | 0 | no | **NONE** |
| EX/EXIC | 0 (OP-invalid, out of scope) | 0 | n/a | n/a |

## Transmit (`tagged Transmit`)

1 read (`st.readWord(srcBase)`) + 1 write (`st.writeWord(dstBase,
srcVal)`), genuinely dependent (the write's data IS the read's
response) -- the same RMW shape as M+/CM/SV/SC/SR.

**Coverage: NONE, and structurally so** -- there is no assembler
mnemonic for Transmit in `opcodes.py` at all (grepped for `"T"`,
`Transmit`, `"TR"`, `"TM"`; zero matches). This instruction cannot
currently be assembled by any STRAP program in this project. Highest-
priority arm to either get a dedicated test for, or explicitly flag as
untested-by-construction in the Phase 2 commit.

## Connective (`tagged Connective`)

| Arm | Reads | Writes | Dependent? | Coverage |
|---|---|---|---|---|
| C (Connect -> accumulator field) | 0-1 (`readField(ea)`, 0 if immediate) + Reg-only (`readAcc`) | 0 BRAM (`writeAcc`, Reg-only) | no | **NONE** (grepped for bare `C` + 4-bit conn prefix pattern, zero matches -- only `CT` suffix forms appear) |
| CM (Connect to Memory -> storage field) | 1 (`readFieldWithHi(ea)`, guaranteed non-immediate) + Reg-only (`readAcc`) | 1 (`writeFieldWithHi`, dedup landed this session) | yes | **NONE** (same grep) |
| CT (Connect for Test, discarded) | 0-1 (`readField(ea)`) + Reg-only (`readAcc`) | 0 | no | problem_2_2_method3 (`CT0110(V+I)`) |
| progressiveIncrement (shared) | 0-1 (refill) | 0 | no | not separately exercised via Connective (figure7 exercises this path via VflInt instead) |

**C and CM are both unexercised.** CM in particular is the arm this
session's `writeFieldWithHi` refactor most directly changed the shape
of (see the refactor commit's own coverage note) -- its correctness
rests on `extractFieldBits`/`insertFieldBits` being the same pure
arithmetic `readField`/`writeField` already used, not on any test
program actually reaching it.

## Fp (`tagged Fp`, L/ST only implemented)

| Arm | Reads | Writes | Dependent? | Coverage |
|---|---|---|---|---|
| L (code 0000110) | 1 (`st.readWord(ea)`) | 0 BRAM (`writeAcc`, Reg-only) | no | **not yet disambiguated** -- `opcodes.py` line 66 defines FP's `"L"` at code `0b0000110`, but VflInt ALSO has an `"L"` mnemonic (different code, `6'b000101`) used by every `L(...)` call site actually seen in the programs (`L(BU,7,8)`, etc. -- always with byte-size/length modifiers). Every "L" usage found by grep in this inventory's VflInt row is presumed VflInt-format based on the modifier syntax, not confirmed by tracing `strap_asm.py`'s dispatch. FP's plain, unmodified `"L"` may or may not be reachable from any current program; not resolved here. |
| ST (code 0001110) | Reg-only (`st.readWord(addrAccRight)`) | 1 (`st.writeWord(ea, v)`) | yes (write's value is the Reg-read's response) | same disambiguation gap as L above |
| anything else | 0 (OP-invalid) | 0 | n/a | n/a |

**Action item before converting this arm**: resolve the L/ST
mnemonic-format ambiguity by reading `strap_asm.py`'s dispatch (likely
keyed on modifier presence or operand count), so FP's actual test
coverage is known rather than assumed either way.

## IoOp (`tagged IoOp`)

| Arm | Reads (of `st`) | Writes (of `st`) | Coverage |
|---|---|---|---|
| Unit Not Ready Reject | 0 | 0 | io_reader_printer (CCWC, wrong-unit case exercises the wrongUnit path, not this one specifically -- DevNone path not separately confirmed) |
| CTL (REWIND/BACKSPACE, tape) | 0 (only `io.readChanCW`/`writeChanCW`, ioDev's own registers -- no BRAM interaction, no Phase 2 work needed) | 0 | io_tape |
| LOC | 0 (OP-invalid) | 0 | n/a |
| REL | 0 (`io.*` only) | 0 | io_reader_printer, io_tape |
| CCW | 0 | 1 (`st.writeWord(effA2, ...)`, value from `io.readChanCW`, not a storage read) | io_reader_printer, io_tape |
| RD/W wrongUnit | 0 | 0 (`io.*` only) | io_reader_printer (CCWC) |
| RD/W normal | 1 (`st.readWord(effA2)`, the control-word adoption read) | 0 (`ioStart` handed to `StretchCore.step`'s existing `ioPending` FSM) | io_reader_printer, io_tape (both RD and W paths) |

IoOp is the best-covered format in this inventory for its
BRAM-relevant arm (RD/W normal). The `ioPending` FSM itself (in
`StretchCore.bsv`, not `execute()`) does its own per-word
`st.readWord`/`st.writeWord` calls across multiple `step()` calls --
already naturally staged one operation per call, but each individual
`st.readWord` there still needs adapting to the new two-call
convention (see "StretchCore.step() fetch and ioPending" below).

## StretchCore.step() itself (not part of `execute()`)

- **Instruction fetch**: 0-2 reads (`readHW` at `pc`, and `pc+1` only
  for `Full`-length), both independent, both-known-upfront addresses
  (pipeline-friendly, 2-3 cycles total). Exercised by every program
  (every instruction fetch goes through this).
- **ioPending FSM's per-word transfer**: exactly one `st` operation per
  `step()` call, never both a read and a write in the same call --
  W-direction (device<-memory) does `st.readWord(x.memAddr)` (BRAM-
  eligible, needs the new 2-call convention nested inside this FSM's
  existing per-word loop); RD-direction (memory<-device) does
  `st.writeWord(x.memAddr, ...)` only (single-cycle, no change needed
  beyond what's already there). Exercised by io_reader_printer and
  io_tape for both directions.
- **pendingIdxWrite (progressive indexing part 2)**: `st.writeIndex`
  only, Reg-only, no BRAM interaction, no Phase 2 work needed.

## Follow-up opportunity found while building this inventory -- DONE (commit `b24e51b`)

SV/SC/SR (DirIndex half-word stores) had the exact same redundant-read
shape M+/CM had before this session's `writeFieldWithHi` refactor --
`readHW(ea)` fetched the full word to extract one half, then
`writeHW(ea, ...)` internally re-read the SAME word to do its own
read-modify-write. Fixed the same way: `readHWWithWord` returns the
raw 64-bit word alongside the extracted half, `writeHWWithWord` skips
the internal read using that word. Landed as its own commit, verified
under the (still same-cycle at that point) regression suite, before
any Phase 2 FSM work touches these three arms. The table above
reflects the deduped shape already; step 5 of the conversion order
below is now just "convert SV/SC/SR" (no separate dedup-first step
needed).

## Conversion order (per advisor: storage interface -> fetch -> arms in this order)

1. `StretchStorage.bsv`: `readWord` -> `readWordReq`/`readWordResp`,
   swap `mem` to `BRAM1Port`/`mkBRAM1Server` for addr>=32.
2. `StretchCore.step()`'s instruction fetch (0-2 independent reads, no
   case-arm variation, all 8 programs exercise it -- best-covered
   place to prove the FSM shape works at all).
3. `StretchCore.step()`'s `ioPending` W-direction read (already
   isolated to one call site, both directions covered by 2 programs).
4. Arms with 0-1 independent reads and no write dependency (lowest
   risk, in roughly coverage order): VflInt L/K/+ (covered), DirIndex
   LX/LV/LC/LR/KV/KC (LX/LV covered, LC/LR/KV/KC not), ImmIndex/
   CountBranch refills (not separately risky), Connective C/CT (CT
   covered, C not), BranchOrMisc R/RCZ/Z (not covered).
5. SV/SC/SR (already deduped, see above -- just needs FSM staging now).
6. The genuinely dependent RMW arms, most-covered first: VflInt ST
   (covered) and Fp ST (coverage unresolved -- resolve first), then
   the uncovered ones: VflInt M+, Connective CM, Transmit (no mnemonic
   exists -- consider adding one, or explicitly flag as untestable as
   currently scoped), Fp L (coverage unresolved).
7. IoOp's RD/W control-word-adoption read (covered, low complexity --
   could move earlier, listed last only because it's naturally grouped
   with the `ioPending` FSM work in step 3).

Each step should build and pass the full regression suite before
moving to the next; per advisor, passing unchanged is necessary but
not sufficient evidence for arms this suite's 8 programs don't
exercise -- those are named explicitly above, not left implicit.
