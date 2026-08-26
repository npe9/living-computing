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
| `StretchIO.bsv` | Simulated Input-Output subsystem (three fixed devices — card reader, printer, tape — standing in for the real Exchange and external units); see its own file header for the full scope statement. |
| `StretchCore.bsv` | Fetch/decode/execute, one instruction per `step()` — returns whether the instruction halted (branched to its own address, the `BEW, $` idiom), for STRAP-program runners (`../strap/gen_tb.py`) to stop on rather than a fixed step count. A progressive-indexing VFL instruction takes two `step()` calls (see "Toolchain" item 7); an RD/W input-output instruction takes as many calls as the block has words, one word drained per call, device-kind-dependent capacity (see `StretchIO.bsv`). |
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
beyond L/ST, Input-Output's `LOC` and most of `CTL` (see above), SIC
(Store Instruction Counter If), Bit Branching, `EX`/`EXIC`, Transmit
backward/`SWAP`/multi-word.

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
writes from user code beyond a few no-op cases), the interval
timer/clock actually ticking, and — the machine's defining engineering
feature — **instruction lookahead and pipelining**. `StretchCore`
fetches, decodes, and executes exactly one instruction per `step()`
call (an RD/W I/O transfer is many `step()` calls, but still no other
instruction interleaves with them — see `StretchIO.bsv`). This is a
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
   - **PHASE 2, NOT STARTED, but two "avoid the rewrite entirely"
     shortcuts have been tried directly in the model and definitively
     ruled out** (see "Toolchain" item 8's own update for the exact
     errors): `RegFile` at 8192 words hits its real 5-port cap (14
     live call sites named in the build error); `BRAM_Configure`
     doesn't support `latency: 0` at all in this `bsc`'s library. So
     the real plan: swap `mem`'s backing to `BRAM1Port`/`mkBRAM1Server`
     (latency 1) for addresses 32-and-up (0-31 stays `Reg`, per the
     Special Storage Assignment architectural boundary -- p.111, "does
     not include internal computer registers and index registers").
     The difficulty: a method call cannot itself span multiple clock
     cycles in BSV, so `readWord`'s ActionValue TYPE (now correct, from
     Phase 1) is not by itself sufficient once the answer genuinely
     isn't available same-cycle -- `StretchCore.step()` needs a new
     pending-read FSM state, the same shape as
     `pendingIdxWrite`/`ioPending`, that issues a BRAM request in one
     `step()` call and consumes the response in a later one.
     Per-instruction read count is bounded and now precisely known
     (corrected from an earlier, too-high estimate that wrongly assumed
     `readAcc`'s two reads could hit BRAM -- they can't, `addrAccLeft`/
     `addrAccRight` are 8/9, always `Reg`-backed, always instant):
     instruction fetch needs 0-2 (`readHW` at `pc`, and `pc+1` only for
     a Full-length instruction); most `execute()` case arms need
     exactly 0 or 1 BRAM-eligible read; the worst cases are `M+`/`CM`
     (`readField`'s 1 read plus `writeField`'s own internal
     read-modify-write read = 2) and `readField`'s own word-crossing
     case (`w0`, `w0+1`, both independent, known-upfront addresses,
     not a chain = 2). No general-storage read's address is EVER
     computed from another general-storage read's just-fetched value
     anywhere in the codebase -- every address comes from `Reg`-only
     state (index registers, PC), available instantly -- which is what
     bounds this to "at most 2 pending reads per instruction" rather
     than an arbitrary-depth wait state.
     **Ruled out, on advisor's explicit warning**: calling `execute()`
     twice (once to discover what it needs, once to finish with the
     value) -- this would re-fire every `st.writeWord`/`writeIndex`/
     `setIndicatorBits`/`io.writeChanCW` the reached arm performs on
     its second call, since BSV has no way to make a function's
     Actions conditionally silent on a "dry run." Also ruled out: a
     separate address-prediction function mirroring `execute()`'s own
     addressing logic -- a second source of truth for what to read,
     where a future divergence between the two produces a silently
     wrong read that this project's 9-block suite (which doesn't
     exercise every case arm) might not catch. The confirmed direction
     is explicit per-case-arm staging: each arm that needs a
     BRAM-eligible read gets manually split into its own numbered
     stages (issue read, resume with result), the same hand-written-FSM
     discipline `pendingIdxWrite`/`ioPending` already established for
     their own operations, extended to cover ~15 case arms instead of
     one operation kind each.
     **Correction: instruction fetch is NOT a separately-shippable
     first slice.** It was originally described that way here, but
     working through the actual mechanics shows it's false: a method
     call cannot span multiple clock cycles, so making `readWord`
     genuinely latency-bearing means splitting it into a request/
     response pair -- and the moment that split happens, EVERY
     Phase-1-converted call site (fetch's included, but also all
     ~26 in `execute()`'s call chain: `readField`, `readAcc`,
     `progressiveIncrement`, `readHW`, ...) needs a second conversion
     round simultaneously, from "one ActionValue call" to "issue
     request in one rule firing, collect response in a later one."
     There is no partial state where fetch uses the new request/
     response interface while `execute()`'s internal reads still use
     Phase 1's single-call convention -- they're both callers of the
     same interface, and the interface itself is what's changing.
     Fetch remains the right place to *prototype* the FSM shape first
     (it's simple: 0-2 reads, no case-arm variation) -- but the actual
     conversion, once started, is one indivisible unit covering fetch
     and every `execute()` case arm together, not a series of
     independently-mergeable slices. A future session should budget
     Phase 2 as a single sitting for exactly this reason, with the
     ~15 case arms each individually reasoned through and checked
     against the regression suite's actual coverage (not assumed
     covered) before considering it done -- the same rigor this
     project applied when the "double-invocation of execute()" and
     "separate address-prediction pass" shortcuts were rejected on
     the risk of a silently-wrong, untested case arm; a rushed per-arm
     conversion done without that same care risks the identical
     failure mode from the other direction.
     **Design consequence for addresses 0-31**: a uniform request/
     response interface -- one calling pattern for every caller, since
     callers generally don't know statically whether their address is
     BRAM-eligible (Phase 1 found only 2 of ~26 sites do) -- means even
     the always-instant `Reg`-backed special registers (addr 0-31) pay
     for a second `step()` call through `readWord`, not just genuine
     BRAM reads. `readIndex`/`readIndicators` are separate methods,
     untouched by this, and stay single-call/instant (index-register
     reads for address computation are the majority of per-instruction
     register access and would be a poor fit for an added cycle here).
     This tradeoff -- interface uniformity and reduced bug surface,
     against an extra cycle even for fast-path special-register access
     through `readWord` -- is the one a future session needs to accept
     or reject up front, before writing any Phase 2 code.
   The existing regression suite remains the correctness oracle for
   Phase 2 as well -- passing unchanged is necessary but Phase 1's own
   experience (the RELSEOP and SKIP bugs surfaced only once tape/IO
   tests were written) is a reminder that "passes unchanged" doesn't
   by itself prove every case arm's new FSM staging is correct; the
   suite doesn't exercise all ~15 case arms individually, so passing
   it is evidence, not proof, for the arms it doesn't touch.
