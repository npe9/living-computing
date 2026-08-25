# IBM 7030 "Stretch" — Bluespec implementation

A non-pipelined, ISA-level Bluespec SystemVerilog model of the IBM 7030
instruction set, built from the primary sources (all under
`stretch/docs/`, pulled from bitsavers.org):

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
| `StretchStorage.bsv` | Unified memory-mapped register file + core storage. |
| `StretchVFL.bsv` | Variable-field-length bit extract/insert. |
| `StretchALU.bsv` | Sign-and-magnitude arithmetic primitives. |
| `StretchExecute.bsv` | Execute stage for the in-scope opcode subset. |
| `StretchCore.bsv` | Fetch/decode/execute, one instruction per `step()` — returns whether the instruction halted (branched to its own address, the `BEW, $` idiom), for STRAP-program runners (`../strap/gen_tb.py`) to stop on rather than a fixed step count. A progressive-indexing VFL instruction takes two `step()` calls (see "Toolchain" item 7). |
| `StretchTb.bsv` | Hand-assembled smoke test (predates the STRAP assembler; kept as a decoder/executor regression test independent of it). |

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
arithmetic, full floating point, I/O channels, and an interrupt
system, several of them large enough to be their own projects).

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
  KV KC` (pp.22-23). Not implemented: `RNX`, `LVE`, `SVA` -- `LVE`
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
- **Immediate index arithmetic** — all pocket-card ops except `LVS`.
- **Count and Branch / Count, Branch and Refill**.
- **Branch on Indicator**.
- **Unconditional branching** (`B BR BE BD BEW NOP`) — `BE`/`BD`/`BEW`
  all branch identically; the enabled/disabled distinction is
  interrupt-system state this implementation doesn't have.
- **Refill / Refill on Count Zero / Store Zero**.
- **Transmit** — forward only, **one word per instruction** (see
  "Toolchain" below for why).
- **Floating point `L`/`ST`** only (plain data movement; see FpWord in
  StretchTypes.bsv for the register layout).

### Decoded but not executed (sets indicator 15, OP, and no-ops —
### matches real-machine behavior for a suppressed instruction)

Decimal-mode VFL (`c=1`), radix conversion, floating-point arithmetic
beyond L/ST, Input-Output, SIC (Store Instruction Counter If), Bit
Branching, `EX`/`EXIC`, Transmit backward/`SWAP`/multi-word.

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
- **Count-and-Branch "add half"/"add one" units**: best-effort reading
  of the pocket card legend (`+1`/`+2` raw units respectively) rather
  than a confirmed table — see StretchExecute.bsv.
- **Immediate index arithmetic semantics** (`LVI`, `V+I`, etc.) are
  extrapolated from the *direct* forms' documented semantics plus the
  mnemonic table, not independently confirmed against manual prose.
- **Accumulator model**: the real accumulator (words 8/9 "Left/Right
  Half" plus a separate 8-bit sign-byte register, word 10) is modeled
  here as one 128-bit sign-magnitude value; the separate sign-byte
  register is storage-addressable but not consulted by the ALU.
- **Word 11 (Indicators) cannot be written via a generic STORE.**
  Real hardware allows writing bits 20-63 directly; here the execute
  stage owns the single per-instruction write to `indicators` (see
  "Toolchain"), so a STORE targeting word 11 is a no-op. Indicators
  remain fully readable and are still set by every instruction that
  defines them.
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
- **Address-space window**: `MemWords` (StretchStorage.bsv) bounds
  simulated core to 256 words near address 0, not the full
  262,144-word address space the 18-bit `WordAddr` type models —
  a Bluesim elaboration-time/capacity choice (see "Toolchain" below
  for just how much it costs to raise), not an architectural one.

### Not modeled at all

Interrupts, memory protection enforcement (addresses described as
"permanently protected" are documented but not enforced against
writes from user code beyond a few no-op cases), I/O channels and the
exchange, the interval timer/clock actually ticking, and — the
machine's defining engineering feature — **instruction lookahead and
pipelining**. `StretchCore` fetches, decodes, and executes exactly one
instruction per `step()` call. This is a genuine, load-bearing scope
cut: Stretch's fame rests on its microarchitecture as much as its ISA,
and that is future work, not something this session attempted.

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
   equivalent hand-written `rule`). `StretchTb.bsv` uses an explicit
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
plus a sixth, purpose-written program (`xw_refill.strap`) closing a gap
the worked examples happened not to exercise. Getting each to pass
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

## Next steps

1. Verify the decoder against `7030_Opcode_List.pdf`'s assembled-word
   listings (its OCR is noisy on digits; check against the rendered
   page images, not the OCR text, the same way the format tables in
   this file were established).
2. Extend execute() coverage in the order real STRAP programs are
   likely to need it: decimal VFL, floating point arithmetic beyond
   L/ST (Connectives landed this session — see "Executed" above).
   Connectives' own `BS`<8 padding and Partial Field/word-7-counts are
   a narrower, self-contained extension if a program ever needs them.
   `LVE` and `SIC` remain open — see "Direct index arithmetic" above
   and `strap/README.md`'s Problem 2.2 Method 3 writeup for what's
   been ruled out so far.
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
