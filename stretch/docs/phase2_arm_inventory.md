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
| L (Load) -- **CONVERTED, `dbee063`** | 0-1 (inlined `extractFieldBits`, 0 if immediate; crossing case = 2, independent) | 0 BRAM (`writeAcc` is addr 8/9, Reg-only) | no (read feeds a Reg write only) | problem_2_2_method2/3 (`L`, confirmed genuinely reached: both programs passed green after conversion, resolving the earlier FP-`L` disambiguation doubt) |
| ST (Store) | Reg-only (`readAcc`, addr 8/9) | 1 (`writeField`: internal RMW read + write) | yes, RMW inside `writeField` | problem_2_1, xw_refill (`ST(V+ICR)`) |
| + (Add) -- **CONVERTED, `e8384a9`** | 0-1 (inlined `extractFieldBits`, crossing case = 2) + Reg-only (`readAcc`) | 0 BRAM (`writeAcc`, Reg-only) | no | problem_2_2_method1/3 (`+,`) -- confirmed genuinely reached, both green after conversion |
| M+ (Add to Memory) | 1 (`readFieldWithHi(ea)`) + Reg-only (`readAcc`) | 1 (`writeFieldWithHi`, no internal read -- dedup landed this session) | yes (write uses the read's `hi` + computed sum) | **NONE** (grepped `opcodes.py`'s `M+` key against all programs, zero matches) |
| K (Compare) -- **CONVERTED, `e8384a9`** | 0-1 (inlined `extractFieldBits`, crossing case = 2) + Reg-only (`readAcc`) | 0 (comparison only) | no | problem_2_2_method1/2 (`K(...)`) -- confirmed genuinely reached, both green after conversion |
| progressiveIncrement (shared, when `isProgressive`) | 0-1 (refill, only P=3/7) | 0 (index write-back happens in `StretchCore.step`, separately) | no | figure7_progressive_indexing (explicit purpose of that program) |

## DirIndex (Direct Index Arithmetic, `tagged DirIndex`)

| Arm | Reads | Writes | Dependent? | Coverage |
|---|---|---|---|---|
| LX -- **CONVERTED, `de97419`** | 1 (inlined, no half-select) | 0 | no | figure7, xw_refill |
| SX | 0 | 1 (`st.writeWord`, value from `readIndex`, Reg-only) | no | **NONE** (grepped for standalone `SX`, zero matches) |
| LV -- **CONVERTED, `de97419`** | 1 (inlined half-select) | 0 | no | problem_2_2_method2/3 (`LV,`) |
| SV | 1 (`readHWWithWord(ea)`) | 1 (`writeHWWithWord`, no internal read -- dedup landed this session, commit `b24e51b`) | yes (write uses the read's raw word + new half) | **NONE** |
| LC -- **CONVERTED, `de97419`** | 1 (inlined half-select) | 0 | no | **NONE** -- verified by hand against the original readHW-based code, statement by statement, since the suite can't reach this arm |
| SC | 1 (`readHWWithWord(ea)`) | 1 (`writeHWWithWord`, deduped) | yes | **NONE** |
| LR -- **CONVERTED, `de97419`** | 1 (inlined half-select) | 0 | no | **NONE** -- same hand-verification as LC |
| SR | 1 (`readHWWithWord(ea)`) | 1 (`writeHWWithWord`, deduped) | yes | **NONE** |
| V+/V+C/V+CR | 1 (`readHW(ea)`) + 0-1 (`maybeRefill`, only V+CR) | 0 (index write-back only, Reg-only) | no | **NONE** as a standalone DirIndex opcode (the `V+I`/`V+ICR` strings that DO appear in figure7/xw_refill/method2/3 are the VflInt *progressive-addressing suffix*, a different namespace per `opcodes.py`'s own comment -- confirmed by reading, not assumed) |
| KV -- **CONVERTED, `de97419`** | 1 (inlined half-select) | 0 | no | **NONE** -- same hand-verification as LC |
| KC -- **CONVERTED, `de97419`** | 1 (inlined half-select) | 0 | no | **NONE** -- same hand-verification as LC |

**DirIndex is the least-covered format in the whole inventory**: only
LX and LV (both pure single-read, no-write arms) have any test
coverage at all. SV/SC/SR/KV/KC/V+/V+C/V+CR/SX are all unexercised.

## ImmIndex (Immediate Index Arithmetic, `tagged ImmIndex`) -- **V+ICR/V-ICR CONVERTED, `3d8cd90`**

All arms are index-register-only (read via `readIndex`, write via the
`idxWriteVal`/`doIdxWrite` path -> `st.writeIndex` in the caller) with
ONE exception: V+IC/V+ICR/V-IC/V-ICR call `maybeRefill` (0-1 read,
independent, refill address known from the index word already read;
only the ICR/-ICR variants can actually trigger it, per `maybeRefill`'s
own condition). V+ICR/V-ICR converted to the prefetch/bail-out shape,
inlining `maybeRefill`'s condition directly rather than calling it. No
arm here ever touches BRAM general storage directly. Coverage: likely
shares DirIndex V+CR's already-established finding (the `V+I`/`V+ICR`
strings appearing in STRAP programs are VFL's progressive-addressing
suffix, a different namespace, not this standalone opcode -- see
DirIndex's own row above) but not independently re-verified here;
treat as **NONE**, not chased further given the low risk (at most one
independent read, no write dependency).

## CountBranch (`tagged CountBranch`) -- **CONVERTED, `3d8cd90`**

0-1 read (inlining `maybeRefill`'s own condition, only when
`cb.refill == 1 && count==0`), independent address, no write
dependency. **Coverage: NONE, confirmed by grep** -- the `CB` mnemonic
(`strap_asm.py`'s own name for this format) does not appear in any
STRAP program at all, not just the refill variant; the whole
instruction is untested by any assembled program. `StretchSmoke.bsv`'s
own hand-assembled Count-and-Branch loop (the "3*10 via CB loop" check)
exercises CountBranch's non-refill path only (`refill=0` in its
`encCountBranch` call) -- the refill path specifically has no coverage
anywhere, smoke test included.

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
| C (Connect -> accumulator field) -- **CONVERTED, `72fe53e`** | 0-1 (inlined `extractFieldBits`, crossing case = 2), 0 if immediate + Reg-only (`readAcc`) | 0 BRAM (`writeAcc`, Reg-only) | no | **NONE** (grepped for bare `C` + 4-bit conn prefix pattern, zero matches -- only `CT` suffix forms appear) |
| CM (Connect to Memory -> storage field) | 1 (`readFieldWithHi(ea)`, guaranteed non-immediate) + Reg-only (`readAcc`) | 1 (`writeFieldWithHi`, dedup landed this session) | yes | **NONE** (same grep) |
| CT (Connect for Test, discarded) -- **CONVERTED, `72fe53e`** | 0-1 (inlined `extractFieldBits`, crossing case = 2) + Reg-only (`readAcc`) | 0 | no | problem_2_2_method3 (`CT0110(V+I)`) -- confirmed genuinely reached, but its specific field (INFO's 4 bytes, 28 bits total) never crosses a word boundary at any loop iteration, so this coverage does NOT exercise the crossing-field path (checked, not assumed) |
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
| L (code 0000110) | 1 (`st.readWord(ea)`) | 0 BRAM (`writeAcc`, Reg-only) | no | **VflInt-vs-FP ambiguity partially resolved**: converting VflInt L (commit `dbee063`) and getting problem_2_2_method2/3 green confirms every `L(BU,...)`-style modifier'd call site really does dispatch to VflInt's L, not FP's -- so those programs are NOT evidence for FP L specifically. Whether FP's plain, unmodified `"L"` (no modifiers) is reachable from any current program is still not traced through `strap_asm.py`'s dispatch; treat as **NONE** until checked, not as an open question. |
| ST (code 0001110) | Reg-only (`st.readWord(addrAccRight)`) | 1 (`st.writeWord(ea, v)`) | yes (write's value is the Reg-read's response) | same status as L above -- VflInt's ST is separately confirmed covered (problem_2_1, xw_refill), FP's is not |
| anything else | 0 (OP-invalid) | 0 | n/a | n/a |

**Action item before converting this arm**: resolve whether FP's
plain `"L"`/`"ST"` (no modifiers) is reachable from `strap_asm.py`'s
dispatch at all, so this arm's actual test coverage is known (likely
NONE) rather than left as an open question.

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

## Conversion order (revised by advisor mid-Phase-2: interface-first with
## the OLD Vector backing kept alive alongside the new methods, call
## sites and their FSM staging migrated incrementally with a green
## regression suite at every step, backing swapped to real BRAM ONLY
## once every caller already tolerates a deferred response -- not the
## single big-bang "readWord -> readWordReq/readWordResp AND swap to
## BRAM in one step" originally sketched below step 1's own text,
## which would have meant one long uncompilable window with no green
## checkpoint in between)

1. DONE (`a1378f0`): add `readWordReq`/`readWordResp` and
   `readAccLeft`/`readAccRight` to `StretchStorage.bsv` ALONGSIDE the
   existing `readWord` -- purely additive, `mem` still
   `Vector#(256,Reg#(Word64))`, nothing yet calls the new methods.
2. DONE (`25be1c8`): convert `readAcc`/`writeAcc` (StretchExecute.bsv)
   and Fp ST's direct `addrAccRight` read to the new dedicated
   accessors, dropping `readAcc`'s `ActionValue` wrapper entirely --
   these never needed the general request/response path to begin with
   (compile-time-constant addresses, see "Design settled" above).
3. DONE (`98aaba9`): `StretchCore.step()`'s instruction fetch, staged
   across 2 (Half) or 3 (Full-length) step() calls via a new
   `fetchPending` register. First genuine multi-cycle conversion;
   chosen first for exactly the reasons originally given (0-2 reads,
   no case-arm variation, exercised by every program). Necessitated
   fixing `StretchSmoke.bsv`'s hand-written, hardcoded step counts
   (`stepCount < 24` -> `< 70`, RNX's single `core.step()` call -> 2),
   which had baked in the old "1 instruction = 1 step() call"
   assumption -- `strap/gen_tb.py`'s generated testbenches needed no
   changes, since they already loop on `step()` until it returns
   `True` rather than counting raw calls.
4. DONE (`cc0a690`): `StretchCore.step()`'s `ioPending` W-direction
   (memory->device) read, staged via a new `ioReadIssued` flag --
   2 step() calls per word moved instead of 1. RD-direction
   (device->memory) untouched, still 1 call per word (only
   `st.writeWord`, which stays single-cycle throughout this whole
   migration). Required restructuring the 3-way branch (capacity-
   exceeded / issue-read-and-wait / process-word) so each ends in its
   own `return False` -- bsc's (P0030) rejected a shared trailing
   return once one branch needed an early one.
5. IN PROGRESS. Arms with 0-1 independent reads and no write
   dependency (lowest risk, in roughly coverage order): VflInt L/K/+
   (covered), DirIndex LX/LV/LC/LR/KV/KC (LX/LV covered, LC/LR/KV/KC
   not), ImmIndex/CountBranch refills (not separately risky),
   Connective C/CT (CT covered, C not), BranchOrMisc R/RCZ/Z (not
   covered).
   - DONE (`dbee063`): **VflInt L**, the first arm converted and the
     one that established the actual mechanism the rest of this step
     (and steps 6-8) now follow: `execute()` gained a
     `Vector#(2,Word64) prefetch`/`Bit#(2) prefetchCount` input and a
     `Maybe#(WordAddr) needsRead` output; an arm checks
     `prefetchCount` before doing anything else and, if the value it
     needs isn't there yet, sets `needsRead` and does NOTHING further
     (no writes, no `ind`/`next`/`doIdxWrite`/`vflPending`/`ioStart`
     mutation) -- verified per arm, not assumed, since this is exactly
     what makes calling `execute()` again for the same instruction
     safe (the earlier-rejected double-invocation shortcut's problem
     was re-firing side effects; a bailed call here performs none).
     `StretchCore.step()` drives it via a `startExecute()` local
     helper (first attempt, `prefetchCount=0`) and a new `execPending`
     FSM state (resumes a bail by collecting one more prefetch slot
     and re-invoking `execute()`). The 2-slot bound comes from L's own
     worst case (a crossing field's `w0`/`w0+1`) -- NOT a general
     bound for every remaining arm; M+/CM's crossing-plus-refill
     combination (see "Design settled" above) could need a 3rd slot
     and hasn't been hit yet. Progressive indexing's shared
     post-`case` block (all VflInt arms) is now also guarded on
     `needsRead`, since it would otherwise run and set `vflPending`
     even on a bailed-out arm.
   - DONE (`e8384a9`): **VflInt K and +**, same shape as L (both check
     `prefetchCount` before doing anything, bail via `needsRead`,
     handle both the non-crossing and crossing field cases). With
     these three converted, `StretchVFL.bsv`'s plain (non-`WithHi`)
     `readField` function is unused everywhere in this codebase --
     grepped, confirmed, not removed (dead code isn't a correctness
     issue; noted for a future cleanup pass rather than acted on now).
   - DONE (`de97419`): **DirIndex LX, LV, LC, LR, KV, KC**. Half-word
     reads (`readHW`'s own shape) never cross a word boundary, so each
     needed exactly 0-1 reads, simpler than VflInt's crossing case.
     LC/LR/KV/KC have no test coverage (grepped, confirmed) -- verified
     by hand against the original readHW-based code, statement by
     statement, rather than relying on the suite. SX (write-only) and
     V+/V+C/V+CR (combines a read with `maybeRefill`'s own conditional
     read) are unchanged -- SX needs no Phase 2 work at all, V+/V+C/V+CR
     is deferred to whichever step handles arms needing 2 sequential
     but non-crossing reads.
   - DONE (`3d8cd90`): **ImmIndex V+ICR/V-ICR and CountBranch's
     refill**. CountBranch's refill path has NO coverage anywhere
     (confirmed: the `CB` mnemonic doesn't appear in any STRAP
     program, and the smoke test's own CountBranch usage sets
     `refill=0`) -- flagged explicitly, not assumed safe.
   - DONE (`72fe53e`): **Connective C and CT**, correctly handling the
     crossing case (2 reads) -- C/CT, unlike CM, are not restricted to
     non-crossing fields, since neither writes to general storage.
   - **Regression found and fixed en route, `c4bf213`**: the earlier
     M+/CM dedup commit (`e17b38e`) had changed C/CT/CM's SHARED read
     call from `readField` (crossing-capable) to `readFieldWithHi`
     (single-word only) -- but the crossing guard only ever excluded
     CM, not C/CT. A crossing C or CT would have silently lost its
     field's low word ever since `e17b38e` landed. Not caught by the
     suite: `CT0110`'s only coverage (`problem_2_2_method3`) doesn't
     happen to cross a word boundary with its actual field parameters
     (verified, not assumed -- see the CT row above). Fixed by
     splitting the shared read: CM keeps `readFieldWithHi` (guaranteed
     non-crossing by its own guard, needs the raw word for its
     writeback); C/CT went back to crossing-capable `readField` before
     being converted to the prefetch/bail-out mechanism in the same
     step above.
   - Remaining in this step: R, RCZ, Z (BranchOrMisc). Each should
     reuse the SAME `prefetch`/`needsRead` protocol L established --
     no new mechanism design expected, just applying it arm by arm.
   - **Build-time finding, unrelated to correctness, worth knowing
     before converting more arms**: Bluesim's code generator inlines
     `step()`'s entire body (which itself inlines `execute()`'s whole
     instruction dispatch) at EVERY textual `core.step()` call site in
     a testbench's source -- not once per module. `StretchSmoke.bsv`
     had 3 such call sites at one point this session (`run`,
     `stepRnx1`, `stepRnx2`) and its generated `mkStretchTb.cxx` was
     27.8MB, ~4x every OTHER generated testbench's 6.76MB (which each
     have exactly 1 call site, via `strap/gen_tb.py`'s single
     loop-until-halted `run` rule). Merged back to 2 call sites
     (`e104dc4`), dropping to 22.1MB. As `execute()` keeps growing with
     each arm converted, each inlined copy grows too -- keep any
     future hand-written testbench (unlike `gen_tb.py`'s generated
     ones, which already only ever have one call site) to as few
     `core.step()` call sites as the FSM genuinely requires, using a
     counted-loop rule (`stepCount < N`) rather than N separate rules
     when multiple `step()` calls are needed in sequence.
6. NOT STARTED. SV/SC/SR (already deduped, see above -- just needs FSM
   staging now).
7. NOT STARTED. The genuinely dependent RMW arms, most-covered first:
   VflInt ST (covered) and Fp ST (coverage unresolved -- resolve
   first), then the uncovered ones: VflInt M+, Connective CM, Transmit
   (no mnemonic exists -- consider adding one, or explicitly flag as
   untestable as currently scoped), Fp L (coverage unresolved).
8. NOT STARTED. IoOp's RD/W control-word-adoption read (covered, low
   complexity -- could have moved earlier, grouped last only because
   it's naturally adjacent to the `ioPending` FSM work in step 4).
9. NOT STARTED, LAST. Once every call site above tolerates a deferred
   response: swap `StretchStorage.bsv`'s `mem` from
   `Vector#(256,Reg#(Word64))` to `BRAM1Port`/`mkBRAM1Server` (latency
   1) for addr>=32, delete the now-unused old `readWord` method and
   its `lookupWord` duplication, bump `MemWords` past 256 in a
   SEPARATE later commit (advisor: isolate latency-handling from
   capacity, one candidate cause per commit).

Each step builds and passes the full regression suite before moving to
the next; per advisor, passing unchanged is necessary but not
sufficient evidence for arms this suite's 8 programs don't exercise --
those are named explicitly above, not left implicit.
