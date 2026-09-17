# IBM 7030 "Stretch" — Bluespec implementation

**Direction as of 2026-09-03: this model is being rebuilt as a
cycle-accurate replica of the 7030 corresponding to every documented
feature and to the folklore** — interleaved memory units behind the
memory bus control unit, the instruction unit with its 1Y/2Y buffers
and index storage, the four-level look-ahead, and the serial/parallel
arithmetic units, with cycle timing per IBM's own Performance
Characteristics — per the staged plan and the feature inventory in
`../docs/microarchitecture_plan.md`. Stages 0-3 of that plan and the
idiomatic-Bluespec rewrite (§1c) have landed: the model is now the
memory units and bus control unit, the instruction unit with 1Y/2Y,
the four-level look-ahead with branch guessing, and the E-box as a
request/result box, as stage modules under one synthesized core (see
"Files"); the serial/parallel arithmetic-unit timing is the open
half. The instruction-set description below (the "Executed" / "Not
modeled" sections) is architectural and still accurate; where it says
"non-pipelined" it is describing the 2026-09-03 starting point. The
model is built from the primary sources (all under `stretch/docs/`,
pulled from bitsavers.org):

- **22-6530-2** — *IBM 7030 Data Processing System Reference Manual*
  (the authority for everything cited "p.NN" below; OCR sidecar text
  and page images were both consulted — the images for every bit-field
  diagram, since OCR mangles diagrams badly).
  `docs/22-6530-2_7030RefMan.pdf` — cited from this project's start
  but not actually present in `docs/` until `../strap/`'s Problem 2.2
  Method 2 work needed to check a page image directly; re-fetched from
  bitsavers then. (Same gap, same fix, as C22-6531/C22-6578 below —
  see `../strap/README.md` "Sources".)
- **X22-6533-1** — *IBM 7030 Reference Card* ("pocket card"): the
  primary source for exact instruction-format bit layouts and opcode
  values used throughout the decoder (`docs/pcard-*.png`).
- **7030_Opcode_List.pdf** — cross-check listing of every assembled
  opcode in octal/hex; not yet used to exhaustively verify the decoder
  (see "Next steps").
- **C22-6531** — *7030 Symbolic Assembly Program / Simulator* (STRAP-1
  language reference) and **C22-6578** — *7030 Programming Examples*:
  the sources for `../strap/`, the STRAP assembler and the worked
  programs it runs against this model — see `../strap/README.md`.

## Files

| File | Contents |
|---|---|
| `StretchTypes.bsv` | Word/format types, bit-numbering convention, Special Storage Assignment addresses, indicator names, `DecodedInstr`. |
| `StretchDecode.bsv` | Half/full-word length + format decode. |
| `StretchMemory.bsv` | The six interleaved 16K-word memory units (2.1 µs cycle, read data after ~1.6 µs) and the memory bus control unit — stage 1 of `../docs/microarchitecture_plan.md`. |
| `StretchStorage.bsv` | The CPU's side of storage: the special-register words 0-31, an in-order store queue and one outstanding read to the MBCU, with the `responseReady`/`writeReady` handshake every caller polls. |
| `StretchVFL.bsv` | Variable-field-length bit extract/insert. |
| `StretchALU.bsv` | Sign-and-magnitude arithmetic primitives. |
| `StretchExecute.bsv` | The execute datapath for the in-scope opcode subset (`execute`), and `mkEBox`, the E-box as a request/busy/result box: `start` runs an instruction and, if it needs an operand word, issues the read and holds the instruction (`busy`, `busyFor(owner)`, `canResume`) until the core's resume arm calls `resume`; `exec` is the bare one-shot datapath for the preparation arm's operand-address probe. |
| `StretchIO.bsv` | Simulated Input-Output subsystem (three fixed devices — card reader, printer, tape — standing in for the real Exchange and external units); see its own file header for the full scope statement. |
| `StretchIBox.bsv` | The instruction unit's stage module `mkInstrBuffers` (1Y/2Y buffers + IC controls: `advance` once per clock, `lookup` for preparation) and, as functions, the instruction classification (E-box class, fetches an operand, stores where, progressive) and the I-box-ahead-of-look-ahead hazard test. |
| `StretchLookAhead.bsv` | The four-level look-ahead as a stage module `mkLookAhead`: `collect` every clock (operand arrivals, one fetch issue), the levels/head/tail/count for the decision arms, and their three mutations `retireHead`/`load`/`cancelAll`. |
| `check_schedule.py` | Run by `build.sh` on bsc's `-show-schedule` output: fails if any core rule is blocked by another core rule (only exported harness methods may block one) — the assertion `fire_when_enabled` cannot make at the synthesized boundary, see "Toolchain" item 10. |
| `StretchTiming.bsv` | The per-instruction time-budget tables (`iboxCycles`, `eboxClocks`, `budgetClocks`) from IBM's Performance Characteristics, as pure functions. |
| `StretchCore.bsv` | The synthesized core (`(* synthesize *)`, one compilation unit): instantiates the stages above and the E-box and orchestrates them with per-clock RULES (`rl_la_fetch` = `la.collect()`, `rl_ic_controls` = `ibuf.advance(...)`, then one of six mutually-exclusive decision arms — see the file's rules section) plus the preparation logic and the branch-guess snapshot/recovery state. `step()` is a clock enable: one call advances the core one clock; `halted()` reports that an instruction branched to its own address (the `BEW, $` idiom), which STRAP-program runners (`../strap/gen_tb.py`) poll to stop on rather than a fixed step count. A progressive-indexing VFL instruction takes two clocks (see "Toolchain" item 7); an RD/W input-output instruction takes as many clocks as the block has words, one word drained per clock, device-kind-dependent capacity (see `StretchIO.bsv`). |
| `StretchSmoke.bsv` | Hand-assembled smoke test (predates the STRAP assembler; kept as a decoder/executor regression test independent of it). |

## Bit-numbering convention

IBM numbers bits left-to-right, bit 0 = MSB. BSV numbers right-to-left,
bit 0 = LSB. IBM bit `i` of a `Bit#(n)` value is BSV index `n-1-i`; an
IBM field spanning bits `[a,b)` is the BSV slice `[n-1-a : n-b]`. Every
field-extraction function cites the IBM bit range it implements.

## Scope

This targets **ISA-level correctness for a documented subset**, not a
cycle-accurate replica of the real machine (which pipelined and
looked ahead — its most famous engineering feature; see "Not modeled"
below) and not the complete instruction set (which includes decimal
arithmetic, radix conversion, `EX`/`EXIC`, most I/O control, and an
interrupt system, several of them large enough to be their own
projects). Floating point is no longer on that list -- all 29 FP
operation codes execute; see "Executed" below.

### Executed

- **VFL binary integer arithmetic** — `L`, `ST`, `+` (and `-`, which
  is `+` with the invert-sign modifier), `M+`, `K`, in **binary mode
  only** (`c=0`); direct, immediate (`P`=0/4), and **progressive
  indexing** (`P`∈{1,2,3,5,6,7}) addressing.
  Reference Manual pp.~86-95 ("Field Definition", "Sign Control"),
  p.21 ("Progressive Indexing") for the `P`∈{1,2,3,5,6,7} modes: the
  effective address is the index register's own value field directly,
  and afterward the instruction's address part is added (1-3) or
  subtracted (5-7) into that same register, optionally counting down
  (2/3, 6/7) and refilling on count zero (3, 7) — verified end to end
  against the manual's own Figure 7 worked example, see
  `../strap/README.md`.
- **Direct index arithmetic** — `LX LV LC LR SX SV SC SR V+ V+C V+CR
  KV KC` (pp.22-23), all setting the index flag and index result
  indicators per p.24 (loads from the loaded word, stores from the
  unchanged one; `KV`/`KC` set the comparison indicators instead) —
  the load/store ops only gained this when I-Box 1's SIC-B,ZIND group
  tested them, see `strap/README.md` "Gotchas" item 17. Not implemented: `RNX`, `LVE`, `SVA` -- `LVE`
  specifically was investigated for `../strap/`'s Problem 2.2 Method 3
  and left unimplemented: p.20 describes it only as enabling "indirect
  addressing" ("the effective address is used to obtain a second level
  effective address"), and this session could not find a page giving
  its exact bit-level behavior distinctly from `LV`'s -- see
  `strap/README.md`'s Method 3 writeup.
- **Connectives** — all sixteen logical functions (`C`/`CM`/`CT`,
  Figure 20, p.75-77), with the same direct/immediate/progressive
  addressing as VFL arithmetic above. **Scope**: byte size is assumed
  to be 8 (the manual's own recommended usage — "a byte size of eight
  should be specified" to avoid padding); the `BS`<8 high-order-zero
  padding p.75 "Byte Size" describes is not implemented. Partial Field
  (`PF`) and the left-zeros/all-ones counts at word 7 (also described
  in that section) are not implemented either, consistent with `PF`
  not being implemented for VFL arithmetic. Verified against C22-6578
  Problem 2.2 Method 3's own `CT0110` (byte-equality test via XOR) —
  see `strap/README.md`.
- **Immediate index arithmetic** — all pocket-card ops except `LVS`,
  with the field semantics of Reference Manual p.25: value operations
  place the 19-bit address part in bits 0-18 of the 25-bit value field
  (value = field << 5), count/refill operations take "bits 0-17 of the
  address part" (the field's top 18 bits). An earlier version used the
  raw field for both; found by `strap/verify_ibox1_listing.py` (I-Box
  1's `LCI,$X1,4` prints as `4.03 02`), see `strap/README.md` "Gotchas"
  item 16.
- **SIC (Store Instruction Counter If)** — Reference Manual pp.41-42: a
  full word whose right half is an ordinary half-word branch (B-family,
  CB-family, or Branch on Indicator); the branch runs with its own
  semantics via the shared `evalBranch`, and if it is taken the 19-bit
  address of the next instruction in storage is stored into bits 0-18
  of the half-word at the SIC's effective address, other bits
  untouched (read-modify-write through the prefetch/bail mechanism,
  after any refill read the embedded CBR needed). Targets below 16.0
  set AD and store nothing; SIC+NOP is a full-word no-op. Can start at
  either half-word boundary (the listings do). Verified by running
  I-Box 1's SIC-CB/SIC-CBZ test groups verbatim with their own
  self-modifying pass/fail chain intact —
  `strap/programs/ibox1_sic_cb_cbz.strap`.
- **Branch on Bit (BB family)** — Reference Manual p.41: a full word
  that tests one bit anywhere in storage at the effective bit address.
  If the bit matches instruction bit 62 (1 for `BB*`, 0 for `BZB*`)
  the branch to the effective 19-bit address is taken; then, *whether
  or not the branch was taken*, the bit is set per instruction bits
  60-61 (`00` unchanged, `01` zero, `10` invert, `11` one) — giving the
  eight mnemonics BB/BB1/BBN/BBZ and BZB/BZB1/BZBN/BZBZ. Read-modify-
  write through the same prefetch/bail mechanism SIC uses; `00`
  (unchanged) issues no write, so it raises no store hazard. Read-only
  locations (which per p.41 stay unchanged under any write attempt)
  are not modeled — the special registers 0-31 are Reg-backed and no
  test branches on a bit within one. Verified by a self-checking chain
  (`strap/programs/bb_branch_on_bit.strap`) whose only path to its PASS
  halt requires correct condition testing plus correct modification on
  both a taken and a not-taken branch, and by `verify_bb_encoding.py`
  (encoding field-by-field vs the decoder's bit positions).
- **Count and Branch / Count, Branch and Refill**.
- **Branch on Indicator**.
- **Unconditional branching** (`B BR BE BD BEW NOP`) — `BE`/`BD`/`BEW`
  all branch identically; the enabled/disabled distinction is
  interrupt-system state this implementation doesn't have.
- **Refill / Refill on Count Zero / Store Zero**.
- **Transmit** — forward only, **one word per instruction** (see
  "Toolchain" below for why).
- **Floating point** — all 29 operation codes have execute arms: `L`/
  `ST` and the `LWF`/`LFT`/`DL`/`DLWF` load family, `+`/`+MG`/`M+`/
  `M+MG`/`D+`/`D+MG`/`F+`/`E+`/`E+I`, `*`/`*+`/`D*`, `/`/`R/`/`D/`,
  the compares `K`/`KR`/`KMG`/`KMGR`, and `SHF`/`SLO`/`SRD`/`SRT`.
  Driven by jb_af1c, which is the most heavily transcribed tape here.
  (This bullet used to read "`L`/`ST` only, plain data movement"; that
  went stale as the F20x families landed. See FpWord in
  StretchTypes.bsv for the register layout.)
- **Input-Output** — `RD`, `W`, `CCW` (Copy Control Word), `REL`
  (Release), `CTL` (Control), and their `SEOP` forms, against a
  **simulated** Exchange and three fixed devices (a card reader,
  channel 32; a printer, channel 33; a tape drive, channel 34) — see
  `StretchIO.bsv`'s file header for the full scope statement:
  synchronous single-block transfer (no real CPU/IO overlap, no
  interrupt propagation), the documented deviation from the manual's
  WRITE "+2" control-word rule (this model has no double-buffer to
  reproduce it with), and — now that the External Units chapter
  (pp.129-149) has been read — `CTL` executing only against the tape
  channel and only two of its documented function codes (REWIND,
  BACKSPACE BLOCK, p.132); every other tape function code (SPACE
  BLOCK/FILE, WRITE TAPE MARK, BACKSPACE FILE, density/ECC/parity/
  light functions) and `CTL` on the reader/printer still fall through
  to Operation Code Invalid, as does `LOC` entirely (this model's
  one-tape-unit-per-channel simplification has no unit-selection
  hierarchy for LOC to navigate — see `StretchIO.bsv`
  "INSTRUCTIONS"). Verified against purpose-written programs (no
  worked example in the manual happens to cover this) — see
  `../strap/README.md`.

### Decoded but not executed (sets indicator 15, OP, and no-ops —
### matches real-machine behavior for a suppressed instruction)

Decimal-mode VFL (`c=1`), radix conversion, floating-point arithmetic
beyond L/ST, Input-Output's `LOC` and most of `CTL` (see above),
`EX`/`EXIC`, Transmit backward/`SWAP`/multi-word. (SIC, Store
Instruction Counter If, and Bit Branching both moved to "Executed" —
see there.)

Per the "decode completely, execute partially" principle: every format
in Figure 6 has a `DecodedInstr` constructor and is field-extracted
correctly even where unexecuted, so the decoder is honest about what
it recognizes independent of what the datapath implements.

### Documented simplifications (deliberate, not oversights)

- **Sign-magnitude sign-bit position within a byte**: the manual gives
  an exact bit position for the *accumulator* sign byte ("fifth bit
  position from the left") but this implementation uses the byte's
  MSB uniformly for both the accumulator and general storage fields —
  see StretchALU.bsv header.
- **Byte-size (`BS`) field encoding**: no explicit 3-bit-code table was
  located in the excerpted manual text; `0` is treated as meaning 8
  (mirroring the `LENGTH` field's own "0 means 64" convention), values
  1-7 as literal. See StretchVFL.bsv.
- **Count-and-Branch "add half"/"add one" units**: settled. Reference
  Manual p.41's table: H adds "one in bit position 18" of the value
  field, + and − add or subtract "one in bit position 17" — a
  half-word (32 bits) and a word (64 bits) of bit address. The earlier
  best-effort reading (+1/+2/−2 raw bits, recorded here as
  unconfirmed) was wrong by a factor of 32; I-Box 1's CBR+/CBR−/CBRH/
  CBRZ+/CBRZ−/CBRZH groups (`strap/programs/ibox1_p43_p51_span.strap`)
  hang at their first value test under it and pass under the table's
  units. See `strap/README.md` "Gotchas" item 18.
- **Immediate index arithmetic semantics** (`LVI`, `V+I`, etc.) were
  originally extrapolated from the *direct* forms plus the mnemonic
  table — and were wrong (field treated as a raw integer). Now
  implemented from Reference Manual p.25's per-operation prose, see
  "Executed" above.
- **Accumulator model** (settled 2026-09-05 by jb_af1c F204C): words
  8/9 are the 128 magnitude bits and the sign lives in the sign byte
  register, word 10, IBM bits 0-7 -- sign in bit 4 ("fifth bit
  position from the left"), data flags T/U/V in bits 5-7 (Ref. Manual
  p.82) -- used by both the VFL accumulator helpers (`StretchALU`
  `accToSM`/`packAcc`, `StretchExecute` `readAcc`/`writeAcc`) and the
  floating-point arms (`StretchFP` `sbSign`/`sbWith`). Until F204C the
  VFL sign sat in bit 0 of word 8 over a 127-bit magnitude and word 10
  kept its LOW byte; the diagnostic's full-64-bit checks of the left
  half and its CM1111/CT1100 on `10.0` exposed both.
- **Word 11 (Indicators): the index half-word stores now write it; the
  general STORE path still does not.** Real hardware allows writing
  bits 20-63 directly (Reference Card footnote c). The execute stage
  still owns the single per-instruction write to `indicators` (see
  "Toolchain"), so `st.writeWord(11)` remains a no-op; instead the four
  index half-word stores -- `SV`, `SC`, `SR` and `SVA` -- FOLD their
  half-word into the `ind` value that write uses, via
  `isIndicatorHW`/`foldIndicatorHW` in `StretchExecute.bsv`. The `BB`
  arm already did this for a single bit. Other store-type instructions
  targeting word 11 are still no-ops.

  Driven out by ja_ax1a p.25's IBIN35 block
  (`strap/programs/ibox1_bind_ind.strap`), which sets XL by hand --
  `LX` to zero, `LV` of a word with value bit 20 set, then
  `SV,$X1,$IND+.32`, landing 32+20 = 52 = XL -- because no index
  operation touches XL. Before the change the block hung at IBIN36
  (004063.40, the deck's own "hang up if bit off"); after it, it runs
  to the end. The XE and XH blocks that follow (pp.25-26) do the same
  with value bits 21 and 22, landing on indicator bits 53 and 54, so
  the store's bit PLACEMENT is pinned and not merely its existence: a
  fold keeping only bit 52 passes the XL block and halts at the XE
  block's first check.

  Two things there rest on the footnote rather than on a listing, and
  are marked as such in the code: the LOW half's preservation of IBM
  0-19 (the deck only ever stores to the high half), and the ORDER
  when a store's half-word overlaps the index result indicators the
  same instruction sets -- the store is applied first, then
  `setIndexResultIndicatorsF`. The deck does not discriminate either.
- **Transmit moves one word**, not `count` words (see "Toolchain").
- **A crossing-field VFL store under progressive indexing suppresses
  the increment too, not just the store.** This falls directly out of
  the crossing-field simplification above combined with the manual's
  own rule (p.22 PROGRAMMING NOTES: "If an exception condition is
  detected during the variable field length portion of the operation,
  the entire operation will be suppressed") — on real hardware this
  "exception condition" essentially never arises for a plain crossing
  store (which real hardware handles), so the rule mostly covers
  genuine errors; here, because *this model's* simplification turns
  an ordinary crossing store into that same suppressed-operation path,
  progressive indexing's index-register advance is skipped right along
  with it. A loop relying on that advance (as `../strap/`'s Figure 7
  test program does) will misaddress every subsequent iteration if any
  record's stored field happens to cross a word boundary — found by
  assembling and running that exact test program with an unlucky data
  alignment before choosing a luckier one; see
  `../strap/programs/figure7_progressive_indexing.strap`'s padding
  comment for the concrete walkthrough.
- **Address-space window**: `MemWords` (StretchStorage.bsv) is now
  the full 262,144-word address space the 18-bit `WordAddr` type
  models (raised from 256 once storage was BRAM-backed — see
  "Toolchain" item 8 for the history and cost). What's still not
  modeled is the *installed-core* limit a real installation had
  (smaller than the address space): addressing beyond it would trip
  AD, Address Invalid, on real hardware; here every address is backed.

### Not modeled at all

Interrupts, memory protection enforcement (addresses described as
"permanently protected" are documented but not enforced against
writes from user code beyond a few no-op cases), the interval
timer/clock actually ticking, and — the machine's defining engineering
feature — **instruction lookahead and pipelining**. (Since superseded:
the look-ahead and the instruction unit now exist as rules in
`StretchCore.bsv`, and `step()` advances one clock, not one
instruction — see the Files table and `../docs/microarchitecture_plan.md`.
An RD/W I/O transfer still lets no other instruction interleave with it
— see `StretchIO.bsv`.) At the time of writing this was a
genuine, load-bearing scope cut: Stretch's fame rests on its
microarchitecture as much as its ISA, and that is future work, not
something this session attempted. I/O channels and the exchange ARE
now simulated (see "Executed" above and `StretchIO.bsv`), but only
enough of them to run RD/W/CCW/REL/CTL against three fixed devices
(the last of which -- tape -- only supports two of its real CTL
function codes) with no real device timing, no LOC, and no
CPU-indicator-register or Channel-Address-register propagation of I/O
status.

## Toolchain

Getting a *working* `bsc` took real effort, worth recording so it
isn't repeated:

1. The `bsc` on `PATH` (`~/.cabal/bin/bsc`, cabal-built from
   `~/src/bsc`) has no bundled standard library (no `Prelude.bo`
   anywhere reachable, and hand-building `~/src/bsc/src/Libraries`
   with that same compiler hit `Unbound variable` errors compiling
   `Vector.bs` against a freshly-built `Array.bo` — a version/build
   mismatch never fully root-caused).
2. **Fix**: `brew install bsc` (2026.01) provides a complete, matched
   compiler + library. Use it explicitly — it is not first on `PATH`:
   `bsv/build.sh` sets `BLUESPECDIR` and invokes
   `/opt/homebrew/Cellar/bsc/2026.01/bin/bsc` directly.
3. `mkAutoFSM`/`StmtFSM`'s `seq` block mis-scheduled sequential,
   independent `writeWord` calls as false write/write conflicts
   (reproduced with a two-line `seq`, confirmed absent with an
   equivalent hand-written `rule`). `StretchSmoke.bsv` uses an explicit
   phase-register FSM instead.
4. **A plain `Reg` (and `RegFile`, even the "WCF" variant — despite
   the name, that only relaxes *read/write* conflict-freedom, not
   *write/write*) accepts at most one `<=`/`upd()` per rule.** This
   is the real constraint behind several design choices here:
   indicators are computed as one `Word64` and written once per
   instruction (`setIndicatorBits`, threaded via a local `ind`
   variable through the whole `execute()` case — see
   StretchExecute.bsv header); a VFL store whose field crosses a word
   boundary is OP-invalid rather than split across two writes
   (`fieldCrosses` in StretchVFL.bsv); Transmit moves one word, not a
   run of `count` words.
5. **`RegFile`'s Verilog primitive hard-caps reads at 5 ports**
   (`sub[5]` in `RegFile.bs`), and `execute()` has far more than 5
   textual call sites that read a word in a given instruction (each
   one provisions its own port regardless of runtime mutual
   exclusivity between case arms). Fix: general core storage is a
   `Vector#(MemWords, Reg#(Word64))` instead — reading a `Reg` is an
   unrestricted value method, so there's no port ceiling, at the cost
   of the bounded `MemWords` capacity noted above. `MemWords` matters
   a lot in practice: 4096 drove `bsc`'s elaborator past 10GB RAM and
   climbing (killed before it finished); 256 elaborates in seconds.
   Raise it only with that tradeoff in mind.
6. Elaborating the full `execute()` case can overflow `bsc`'s default
   Haskell RTS stack (`Stack space overflow: current size 33608
   bytes`). `build.sh` passes `+RTS -K512m -RTS` to both the `-g` and
   `-e` invocations.
7. **Adding progressive indexing's index-register write (a 2nd
   `st.writeIndex` call site inside `execute()`'s VflInt case) produced
   spurious G0004 "uses methods that conflict in parallel" errors on
   `core_st_xreg_N.write(...)`, even though the two calls are on
   tagged-union arms (`vi.code` L vs. ST) that are mutually exclusive
   by construction.** Bisection (temporarily stripping the conflicting
   arm down to its bare minimum, one change at a time, rebuilding after
   each) isolated the trigger precisely: it reproduces whenever **two
   or more `case (vi.code)` arms each call `st.writeWord` (directly, or
   via `writeAcc`/`writeField`) *and* conditionally write an index
   register** — the arm count, the presence of `ActionValue` binds,
   `Maybe`/`Tuple2` vs. flat local variables, and even *where* the
   final `st.writeIndex` call textually lives (inside `execute()`, or
   moved to its caller) all turned out not to matter; every one of
   those variants still failed once a second general-storage-writing
   arm gained an index write. No other format in this file has an arm
   doing both, which is why the previous 13-ish `writeIndex` call
   sites (spread across DirIndex/ImmIndex/CountBranch/BranchOrMisc,
   each doing *either* a memory write *or* an index write, never both
   in the same arm) never hit this. **Fix**: progressive indexing's
   index-register write happens on a genuinely separate call to
   `StretchCore.step()` — matching the manual's own description (p.22
   PROGRAMMING NOTES: "An operation in which progressive indexing is
   specified is executed in two parts"). `execute()` returns the
   pending write as a `Maybe` instead of performing it; `step()` checks
   for a pending write before fetching anything, and if present,
   performs just that write on its own cycle. See the `pendingIdxWrite`
   register in `StretchCore.bsv` and the comment on `execute()`'s
   return type in `StretchExecute.bsv`.
8. **`MemWords` does not scale the way item 5 above implied it might.**
   Raising it from 256 to 8192 (a Vector of 8192 `Reg#(Word64)`, tried
   in order to fit a DCP-sized program) sent `bsc`'s elaborator to
   1.5TB+ virtual memory with no sign of finishing after 5+ minutes —
   killed, not waited out. This isn't a bigger version of the same
   256-elaborates-in-seconds tradeoff item 5 describes; it's a
   different regime entirely, and the combinational read-mux a
   `Vector#(N, Reg)` compiles to is the suspected reason (each of the
   many per-instruction reads provisions a mux over all N registers).
   **CONFIRMED, not just suspected, in a later session**: a throwaway
   probe module (`mkBRAM1Server`, 8192 words, request/response
   read-after-write) elaborated in 0.275 seconds and ran correctly in
   Bluesim — the exact same word count that hung the `Vector` version
   for 5+ minutes at 1.5TB+ RAM. The BRAM library is present in this
   `bsc` installation (`Libraries/BRAM.bo`, `BRAMCore.bo`) and works in
   both Bluesim and (per `Verilog/BRAM1.v` etc. being present)
   synthesis, so the elaboration-cost blocker is solvable, cheaply,
   and confirmed rather than assumed.
   
   What is NOT solved yet, and is the real remaining size of this
   undertaking: `execute()`'s many arms currently assume
   `st.readWord`/`st.writeWord` are combinational (same-cycle), and a
   BRAM read genuinely is not -- the probe's own read took two
   separate rule firings (`request.put` then `response.get`), not one.
   Critically, **the address split can't be pushed to call sites**:
   `readWord`'s ~26 call sites across `StretchExecute.bsv` (18),
   `StretchVFL.bsv` (4), and `StretchCore.bsv` (4) overwhelmingly pass
   a *runtime-computed* `WordAddr` (index-register-modified effective
   addresses, `XW` refill fields, Transmit source/dest addresses --
   see e.g. `effA2`, `ea`, `x.refill` at their call sites), not a
   compile-time-known address in either the 0-31 special-register
   range or the 32-and-up general-storage range. Only two call sites
   (`addrAccLeft`/`addrAccRight`) are statically known. This means the
   0-31-stays-`Reg`/32-plus-becomes-`BRAM` split the Special Storage
   Assignment table itself justifies architecturally (the Exchange
   already can't touch locations 0-31, so it's not an arbitrary cut)
   still requires `StretchStorage`'s `readWord` interface to become
   uniformly latency-bearing (an `ActionValue`, or a request/response
   pair) for every caller, not just the ones that happen to address
   general storage -- which means most of `execute()`'s ~26 read/write
   call sites, not a handful, need converting from a single
   combinational expression into a multi-cycle sequence. That is a
   materially larger rewrite than the I/O subsystem's `ioPending` FSM
   (which added multi-cycle behavior to exactly one operation kind);
   it touches the core control structure of every instruction that
   reads or writes general storage. Correctly identifying the size and
   shape of the remaining work was itself the deliverable of the
   investigation session; the actual conversion is now under way as
   two separate, separately-verified phases -- see "Next steps" item 6
   for the current status of each.

   **Two cheap "maybe no rewrite is needed" alternatives were tried
   and both definitively ruled out, in a later session again** (worth
   recording so no future session re-tries either): (1) `RegFile` at
   8192 words, tried directly in the real model (not a synthetic
   probe) by swapping `mem`'s backing and rebuilding: rejected at
   compile time with `(G0002) 'mem.sub' needs more than 5 ports`,
   naming 14 distinct live call sites -- confirms the original design
   comment's claim about `RegFile`'s 5-port cap is real and applies
   even in Bluesim (not just Verilog synthesis, which this project
   never targets anyway), and that bsc's conflict analysis does NOT
   collapse mutually-exclusive `case`-statement arms into a shared
   port -- it treats every statically-reachable call site as
   potentially live. (2) `BRAM_Configure{latency: 0}` (same-cycle
   BRAM, which would keep `readWord` effectively combinational with no
   FSM needed): this `bsc`'s `BRAM.bsv` explicitly rejects it at
   elaboration ("latency must be either 1 or 2") -- not a design
   choice to work around, a hard floor in the library itself. Between
   these two results, there is no shortcut: real multi-cycle handling
   (Phase 2, `mem` on real BRAM plus a per-instruction pending-read FSM
   in `StretchCore.step()`) is confirmed necessary, not merely likely.

   **Resolved.** After the BRAM migration (docs/phase2_arm_inventory.md
   step 9) landed green, `MemWords` was raised straight to 262,144 —
   the whole 18-bit space — as its own commit: the smoke test builds
   in ~40s wall clock and every regression block passes unchanged.
   One wrinkle: at exactly 2^18 the bound no longer fits in a
   `Bit#(18)` literal (`bsc` T0051), so `memInRange` compares one bit
   wider than `WordAddr`. First program to actually run above word
   256: `strap/programs/ibox1_wen_ven_original_addresses.strap`
   (I-Box 1's WEN2/WEN/VEN at their listed octal 5454–5461, constants
   at 6102–6103), verified discriminating by putting 256 back and
   watching all five of its checks fail.

   **The elaboration-cost curve was also measured, not just bounded at
   the two endpoints already known (256 seconds, 8192 hangs)**: 512
   words took 1m54s to elaborate (vs. 256's few seconds), and 1024
   words did not finish within a 2-minute timeout. This is a steep,
   likely combinatorial cliff starting almost immediately past 256,
   not a gentle slope -- doubling `MemWords` roughly from "seconds" to
   "two minutes" in one step. Confirms `Vector#(N, Reg)` is not a
   viable path to anything past a few hundred words, reinforcing (2)
   above rather than opening a middle-ground option.

## Codesign: the STRAP assembler

The user's stated goal for this line of work is **codesign**: a STRAP
assembler that can compile real, historical Stretch programs and run
them on this model, using real programs to drive out decode/execute
bugs and scope gaps instead of only hand-written test vectors. That
assembler now exists, at `../strap/` (`strap/README.md`), sharing this
model's opcode table directly rather than re-deriving it. It has
assembled and run five worked (or worked-algorithm) examples from the
Reference Manual and `C22-6578_7030_Programming_Examples_Apr61.pdf`
end to end (STRAP source → assembler → this decoder/executor → a
checked result matching an independent calculation) — Problems 2.1 and
2.2 Methods 1, 2, and 3 (3's own two unimplementable lines, `LVE`/`SIC`,
substituted for verified equivalents — see `strap/README.md`), and
Reference Manual Figure 7 (progressive indexing, ten-record loop) —
plus four purpose-written programs closing gaps the worked examples
happened not to exercise: `xw_refill.strap` (the `XW` pseudo-op's
`REFILL` field), `io_reader_printer.strap` (the simulated card reader
and printer — RD/W/CCW/REL/SKIP, including a wrong-unit RD given to
the printer, a channel address with no device installed, and a
distinguishing test that caught a real bug in `REL SEOP`'s original
implementation — see `strap/README.md`'s Gotchas item 13), and
`io_tape.strap` (the simulated tape drive — RD/W/CCW plus CTL's REWIND
and BACKSPACE BLOCK, proving tape position persists across
instructions rather than restarting like the reader/printer's does —
Gotchas item 14). Getting each to pass
caught real bugs or gaps in this model as it stood, not hypothetical
ones: an inverted index-flag-bit derivation (`StretchExecute.bsv`'s
`V+`/`V+I`/`V-I`/`CountBranch` cases were computing the index flag from
the arithmetic result instead of preserving the program-set flag bit);
a bsc scheduler limitation on combining a general-storage write with an
index-register write in the same case arm (see "Toolchain" item 7); the
crossing-field-store / progressive-indexing interaction above; and, on
the assembler side, an address-field unit conversion, the Special
Storage Assignment range needing to stay off-limits to ordinary code,
an XW refill-field unit bug, two STRAP-1 syntax gaps in Immediate
addressing and progressive indexing's secondary-op ordering, and VFL
Immediate addressing's own field-packing rule (see `strap/README.md`
"Gotchas found by running real programs" for the full account of all
of these).

9. **Why a build is slow, profiled -- with two disproven hypotheses
   (2026-09-04).** A clean `bsc -g` (elaborate + generate Bluesim) of
   one testbench takes ~121s, CPU-bound not GC/memory-bound (GHC
   productivity 94.2%, max residency 458MB). `-show-elab-progress` puts
   essentially all of it inside the *single* `run` rule body --
   `StretchCore.step()` inlined into the testbench's rule; submodule
   instantiation is cheap. So the cost is elaborating the one big
   combinational rule.
   - **Hypothesis A (WRONG): the four `execute()` call sites in `step()`
     cost 4x.** BSV inlines functions, so it looked like four copies of
     the ~1450-line E-box. Tested by wrapping `execute` in a module
     (`mkEBox`) instantiated once and calling its `exec` method at all
     four (mutually-exclusive) sites -- the idiomatic mkFBox/mkMBox
     pattern from Bluespec's Piccolo/Flute. Result: **126s, no change.**
     `bsc` was already sharing/folding the copies; replication is not
     the cost. (The experiment reverted.)
   - **Hypothesis B (WRONG): the combinational FP arithmetic.** Tested
     by stubbing out the two 48x48 -> 96-bit multiplies in `fpMul` and
     the up-to-95-place normalization barrel-shift in `fpNormalize96`.
     Result: **118s, no change.** The wide FP datapath is not the cost
     either. (Reverted.)
   So there is NO single "weird elaboration" hotspot: the ~120s is the
   aggregate elaboration of the whole `step()`/`execute()`/look-ahead
   logic as one giant combinational rule, with pervasive `primExtract`
   (bit slicing) and `DecodedInstr`-Bits unfolding (G0024) spread across
   it. The user's read was right about the STRUCTURE though -- this is
   "weird Verilog, not Bluespec": one monolithic combinational `execute`
   in one rule, rather than the idiomatic Bluespec CPU (Piccolo/Flute):
   **separate pipeline-stage MODULES with a small orchestration rule,
   and the expensive datapath (FP, multiply, divide) as MULTI-CYCLE
   stateful sub-modules ("boxes") rather than giant combinational
   functions.** (This item originally said the stages communicate
   "through FIFOs". Corrected 2026-09-07 after actually reading
   Piccolo's `CPU.bsv` instead of describing it from memory: its stages
   hand off through combinational `.out` bundles and `enq`/`deq` inside
   one `rl_pipe` rule, and its only FIFOs are at the reset, GDB and
   trace edges -- none between stages. Building to the old wording
   would have moved this model AWAY from the reference. See the audit
   in plan §1c.) That restructure is the real fix --
   and it doubles as the cycle-accuracy goal, since the real 7030 E-box
   *is* multi-cycle serial (SAU) and parallel (PAU) units (plan item 5).
   The "it splits the design across compilation units so no single rule
   elaborates everything" argument that stood here is **hypothesis C,
   and it is also disproven** (measured 2026-09-07, plan 1c-audit): the
   `(* synthesize *)` boundary of item 10 already captured that win, and
   the per-testbench elaboration behind it is **0.73s**. A clean tree
   costs 139s wall / 117s user once, then ~2s per testbench (0.73s
   elaborate + 1.29s link). Whole suite measured the same day: 228.77s
   wall on a warm tree (129 sections, zero failures), ~6.3 min from
   cold. A second boundary at `mkEBox` would shave a
   fraction of a one-time 2.5 min and is not worth doing -- and by the
   audit's own table it would move the model AWAY from Piccolo, whose
   stage modules carry no `(* synthesize *)` either. So the remaining
   case for the restructure is cycle-accuracy alone, not build time, and
   it narrows to the multi-cycle-box half: live for `D/`, deferred for
   the rest. The full version of it would be a fundamental rewrite of
   `StretchCore`/`StretchExecute`, not a local patch -- which, with no
   build-time case left, is a further reason to take only the piece
   that has a reason. The simulation itself is milliseconds; it is all
   elaboration + codegen + link -- which is why builds run in the
   background here.
10. **The fix that worked: `(* synthesize *)` on `mkStretchCore`
   (2026-09-04, plan §1c step 5a).** After step 4 made the core
   rule-based, the testbench's `run` rule became trivial (`step()` is
   a clock-enable pulse) and the elaboration cost moved wholly inside
   `mkStretchCore` -- so synthesizing it as its own module makes it
   ONE compilation unit built once per suite run and linked by every
   testbench: ~117s for the core, then ~0s elaborate + ~10s link per
   testbench, versus ~120s each before (the suite: ~12 min -> ~3.5
   min). Re-measured 2026-09-07 and refined: the per-testbench
   elaborate is 0.73s and the link is **1.29s**, not ~10s. The ~10s is
   real but is paid ONCE -- it is the first link after a clean tree
   compiling `simbuild/mkStretchCore.cxx` (5.9 MB of generated C++)
   into a `.o` that every later link reuses untouched. Time one link on
   a fresh tree and multiply by 66 and you overstate the suite's link
   cost about ninefold. Two constraints the boundary imposes on testbenches: no rule
   may call `core.setPC` together with a `core.mem.*` method (KPNS
   #29), and the exported bus-channel methods (`laReq`, `fetchReq`,
   ...) are assumed callable in any clock, so the every-clock core
   rules that share those channels carry no `fire_when_enabled`.

## Next steps

0. **Real historical source, not just worked examples, is now a
   transcription target.** `docs/archival_inventory.md` catalogues an
   archival pass over bitsavers' `diag/`/`ce/`/`mcp/` collections: pages
   19–152 of the 7030 Diagnostic Control Program manual
   (`diag/ka_ua1_diagnostic_ctl_pgm.pdf`) are a complete, unbroken STRAP
   source listing (~130 pages, continuity independently verified) — the
   largest block of real Stretch source found anywhere in this project
   so far. Two self-contained routines in it (Memory Compare, Panel
   Dump) need no tape/channel I/O and are runnable/verifiable on this
   model today; see that doc's "Recommended next steps" for the
   transcription order (shared symbol table first).
1. Verify the decoder against `7030_Opcode_List.pdf` (now in `docs/`,
   99 pp)'s assembled-word listings (its OCR is noisy on digits; check
   against the rendered page images, not the OCR text, the same way the
   format tables in this file were established).
2. Extend execute() coverage in the order real STRAP programs are
   likely to need it: decimal VFL, floating point arithmetic beyond
   L/ST (Connectives landed this session — see "Executed" above).
   Connectives' own `BS`<8 padding and Partial Field/word-7-counts are
   a narrower, self-contained extension if a program ever needs them.
   `LVE` remains open — see "Direct index arithmetic" above and
   `strap/README.md`'s Problem 2.2 Method 3 writeup for what's been
   ruled out so far. `SIC` is done (see "Executed").
3. Multi-word Transmit and crossing-field VFL stores, properly, as
   multi-cycle operations (needs `StretchCore`'s FSM to support an
   instruction that isn't done after one `step()` — the `pendingIdxWrite`
   two-cycle mechanism added for progressive indexing is a template for
   this, not a ready-made solution: crossing-field stores need to split
   across a word boundary, not just defer a single write).
4. Open question, not yet resolved either way: does a branch
   instruction immediately following a progressive-indexing
   instruction (e.g. `BZXCZ` right after `ST(V+ICR)`, as in
   `strap/programs/figure7_progressive_indexing.strap`) read the
   index register's pre-refill or post-refill state on real 7030
   hardware? With this model's two-cycle `pendingIdxWrite` design, the
   index write (including any refill) completes on its own `step()`
   *before* the next instruction fetches, so a following branch always
   sees post-refill state here. Whether that matches the real
   machine's timing (which the manual describes only as "executed in
   two parts," not with cycle-by-cycle interleaving semantics) is
   unverified. Not exercised by any test yet — `figure7_progressive_
   indexing.strap`'s own `BZXCZ` exits the loop on the same cycle a
   refill would occur, and `strap/programs/xw_refill.strap` (see
   `strap/README.md` "Gotchas" item 7) has no branch after its
   refilling instruction — so this is a real gap, not a guess dressed
   up as a finding.
5. Extend the simulated Input-Output subsystem (`StretchIO.bsv`), now
   that the External Units chapter (pp.129-149) has actually been
   read: the tape's remaining CTL function codes (SPACE BLOCK/FILE,
   WRITE TAPE MARK, BACKSPACE FILE — need a tape-mark concept this
   word-addressed model doesn't have yet; density/ECC/parity/light
   functions have no observable effect on this model's storage-level
   abstraction and may not be worth implementing even as no-ops);
   `LOC` and real multi-unit selection (would mean modeling several
   tape units behind one shared control, replacing the current
   one-tape-unit-per-channel simplification — a bigger step than
   anything else in this list, see `StretchIO.bsv` "INSTRUCTIONS");
   chaining and multiple-block operation (currently decoded into the
   control word but ignored by the transfer FSM — every RD/W is a
   single block against a device's one fixed image); propagating
   EOP/EPGK/UK/EE/CS into the CPU's own indicator register and the
   Channel Address register (word 5) — needed before a BI- or
   SIC-based wait loop (like real DCP source uses) can observe I/O
   completion, since this model currently exposes status only via
   `CCW`; and, if real device content larger than `DeviceWords` (32)
   or `TapeWords` (16) is ever needed, `StretchIO`'s Vector-based
   device images have the same elaboration-cost ceiling as item 8
   above.
6. **The BRAM-backed storage rewrite** — the single prerequisite every
   other DCP-scale-transcription item in this file and
   `docs/archival_inventory.md` ultimately depends on. "Toolchain" item
   8 above has the full finding: a throwaway `mkBRAM1Server` probe at
   8192 words elaborated in 0.275s (vs. the plain-`Vector` version's
   5+ minute, 1.5TB+ RAM hang), so the elaboration-cost blocker is
   confirmed solvable, cheaply. Being done as two separate, separately-
   verified phases (advisor's own framing: "never more than one revert
   from green"):
   - **PHASE 1, DONE**: `StretchStorage.readWord` changed from a plain
     value method to `ActionValue#(Word64)`, with `mem` still the
     same `Vector#(256, Reg#(Word64))` -- so every answer is still
     same-cycle underneath, and this phase changes only the CALLING
     CONVENTION (`<-` bind inside an action/actionvalue context) at
     all ~26 call sites, plus every helper function in their call
     chain that wasn't already `Action`/`ActionValue`-typed
     (`readHW`/`writeHW`, `readAcc`, `progressiveIncrement`,
     `maybeRefill`, `readField`/`writeField` in `StretchVFL.bsv`) and
     `StretchCore.step()`'s own instruction-fetch reads. Also updated:
     `StretchSmoke.bsv`'s hand-written checks and `gen_tb.py`'s
     generated `check{i}` rule (both used to call `core.mem.readWord`
     as a bare expression). Full regression suite (1 smoke test + 8 STRAP programs, 9 test blocks) passes
     unchanged. This deliberately proves the *protocol* conversion is
     correct in isolation, before *latency* is introduced at all --
     any bug at this stage is unambiguously a call-site conversion
     bug, not a BRAM-timing bug, by construction.
   - **PHASE 2, IN PROGRESS.** Two "avoid the rewrite entirely"
     shortcuts were tried directly in the model and definitively ruled
     out before Phase 2 started (see "Toolchain" item 8's own update
     for the exact errors): `RegFile` at 8192 words hits its real
     5-port cap (14 live call sites named in the build error);
     `BRAM_Configure` doesn't support `latency: 0` at all in this
     `bsc`'s library. The real plan, and its full current status
     (which arms are converted, which aren't, exact commit hashes, and
     the coverage evidence per arm), now lives in
     `docs/phase2_arm_inventory.md` rather than here -- that file is
     the living document; this entry is a pointer plus the headline
     findings worth knowing before reading it.
     **Revised sequencing** (advisor's mid-Phase-2 correction to the
     original one-big-conversion plan): rather than changing
     `readWord`'s type and every one of its ~26 callers' calling
     convention in one uncompilable window, `readWordReq`/
     `readWordResp` were added ALONGSIDE the existing `readWord`
     (kept, unchanged, still `Vector`-backed) so call sites and their
     `StretchCore.step()` FSM staging could be migrated and verified
     incrementally, one arm at a time, always green. The backing swaps
     to real `BRAM1Port`/`mkBRAM1Server` only as the LAST step, once
     every caller already tolerates a deferred response -- at that
     point it's purely a change to where the answer comes from, not
     when it's collected, since every caller already waits a cycle
     either way.
     **A genuine discovery that revised an earlier claim**: this
     README previously said instruction fetch was "not a separately-
     shippable first slice" because splitting `readWord` into request/
     response would force every caller to convert simultaneously. That
     reasoning was sound for the ORIGINAL single-interface-change plan
     -- but the revised sequencing above (old `readWord` kept alive)
     sidesteps it entirely: fetch DID ship as an independent, separately-
     committed, separately-verified step, followed by the `ioPending`
     FSM as another. The two are not in tension -- the earlier
     reasoning was correct about the plan as it stood at the time; the
     plan itself changed shape.
     **`readAcc`/`writeAcc` don't need the request/response path at
     all**: `addrAccLeft`/`addrAccRight` (8, 9) are compile-time
     constants baked into the helper, never a runtime-computed
     effective address -- genuinely different from the ~24 call sites
     Phase 1 found can't know their address's range statically.
     Dedicated `readAccLeft`/`readAccRight` accessors stay plain,
     always-instant value methods, removing what would otherwise be a
     round trip from nearly every VflInt and Connective arm. This also
     narrows the "design consequence for addresses 0-31" this README
     used to describe here: the accumulator specifically is exempted,
     though every OTHER special register still pays for a
     `readWordReq`/`readWordResp` round trip through the general path
     once its callers convert, for the reason originally given (callers
     generally don't know their address's range until after computing
     it).
     Per-instruction read count is bounded and precisely known:
     instruction fetch needs 0-2 reads; most `execute()` case arms need
     0-1; the worst cases (`M+`/`CM`, deduped this session via
     `readFieldWithHi`/`writeFieldWithHi`; `SV`/`SC`/`SR`, deduped via
     `readHWWithWord`/`writeHWWithWord`) need exactly 1 read plus a
     dependent write, not 2 independent reads as an earlier, corrected
     estimate assumed. See `docs/phase2_arm_inventory.md`'s "Design
     settled" section for the full reasoning (single BRAM port
     suffices; writes stay single-cycle throughout; case arms are
     mutually exclusive so cross-arm port conflicts aren't a concern).
     **Ruled out, on advisor's explicit warning**: calling `execute()`
     twice (dry-run then real run) -- would re-fire every `st.writeWord`/
     `writeIndex`/`setIndicatorBits`/`io.writeChanCW` the reached arm
     performs, since BSV has no way to make a function's Actions
     conditionally silent. Also ruled out: a separate address-
     prediction function mirroring `execute()`'s own addressing logic
     -- a second source of truth that could silently diverge for an
     untested case arm. The confirmed (and now partially executed)
     direction: explicit per-case-arm staging, extending the
     `pendingIdxWrite`/`ioPending` hand-written-FSM pattern arm by arm,
     verified against the regression suite (and its actual per-arm
     coverage, not assumed) at every step -- see
     `docs/phase2_arm_inventory.md`'s conversion-order list for exactly
     which arms are done and which remain.
   The existing regression suite remains the correctness oracle for
   Phase 2 as well -- passing unchanged is necessary but Phase 1's own
   experience (the RELSEOP and SKIP bugs surfaced only once tape/IO
   tests were written) is a reminder that "passes unchanged" doesn't
   by itself prove every case arm's new FSM staging is correct; the
   suite doesn't exercise all ~15 case arms individually, so passing
   it is evidence, not proof, for the arms it doesn't touch.
