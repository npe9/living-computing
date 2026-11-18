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
| `StretchIO.bsv` | Simulated Input-Output subsystem (four fixed devices — card reader, printer, tape, disk — standing in for the real Exchange, the IBM 7612 disk synchronizer, and the external units); see its own file header for the full scope statement. |
| `StretchDiskSource.bsv` | The 353 platter behind an interface, the way `StretchTapeSource.bsv` holds the 729's reel: `DiskIndex`/`ArcAddr`/`arcWords`, and a small RegFile-backed source of two arcs to test against. A unit is 2²¹ words, so the real thing is a host file or an SD card, not registers. |
| `StretchIBox.bsv` | The instruction unit's stage module `mkInstrBuffers` (1Y/2Y buffers + IC controls: `advance` once per clock, `lookup` for preparation) and, as functions, the instruction classification (E-box class, fetches an operand, stores where, progressive) and the I-box-ahead-of-look-ahead hazard test. |
| `StretchLookAhead.bsv` | The four-level look-ahead as a stage module `mkLookAhead`: `collect` every clock (operand arrivals, one fetch issue), the levels/head/tail/count for the decision arms, and their three mutations `retireHead`/`load`/`cancelAll`. |
| `check_schedule.py` | Run by `build.sh` on bsc's `-show-schedule` output: fails if any core rule is blocked by another core rule (only exported harness methods may block one) — the assertion `fire_when_enabled` cannot make at the synthesized boundary, see "Toolchain" item 10. |
| `StretchDivBox.bsv` | The divide boxes. `mkDivBox`, the one the core instantiates (once, inside `mkEBox`): a 96-by-48 iterative restoring divider behind `request`/`responseReady`/`response`, 24 quotient bits a clock, four clocks, reached by `execute()`'s `NeedBox` bail; for a floating-point divide it also walks the 7030's reduction loop for its length (`fpExtra`) -- see "The divide box" below. `mkFpDivBox`, the standalone sourced-structure FSM (trial/intermediate/last reduction, the normalisation loop) that the later timing step is to grow it into. Each has its own testbench (`mkCoreDivBoxTb`, `mkDivBoxTb`; `../tests/run_divbox_test.sh`). |
| `StretchTiming.bsv` | The per-instruction time-budget tables (`iboxCycles`, `eboxClocks`, `budgetClocks`) from IBM's Performance Characteristics, as pure functions. |
| `StretchCore.bsv` | The synthesized core (`(* synthesize *)`, one compilation unit): instantiates the stages above and the E-box and orchestrates them with per-clock RULES (`rl_la_fetch` = `la.collect()`, `rl_ic_controls` = `ibuf.advance(...)`, then one of six mutually-exclusive decision arms — see the file's rules section) plus the preparation logic and the branch-guess snapshot/recovery state. `step()` is a clock enable: one call advances the core one clock; `halted()` reports that an instruction branched to its own address (the `BEW, $` idiom), which STRAP-program runners (`../tests/gen_tb.py`) poll to stop on rather than a fixed step count. A progressive-indexing VFL instruction takes two clocks (see "Toolchain" item 7); an RD/W input-output instruction takes as many clocks as the block has words, one word drained per clock, device-kind-dependent capacity (see `StretchIO.bsv`). |
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
arithmetic, radix conversion, most I/O control, and an
interrupt system, several of them large enough to be their own
projects). Floating point is no longer on that list -- all 29 FP
operation codes execute; see "Executed" below. Neither are the two
execution operations: `EX` executes as of 2026-09-25 and `EXIC` as of
2026-09-29.

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
- **The second index of a VFL or connective instruction** (bits 60-63)
  modifies its length, byte size and offset as one field, index bits
  3-18 aligned with bits 35-50, read before any progressive update
  (Reference Manual printed p.21; `vflSecondIndex` in
  `StretchExecute.bsv`, also applied in `StretchIBox`'s `prepareExec`).
  Decoded and dropped until 2026-11-11, when MCP's binary loader's
  O-card conversion (printed p.323 lines 46-50) found it;
  `decks/vfl_second_index.strap` runs that loop. CHOSEN: a negative
  index subtracts, as for an address.
- **Direct index arithmetic** — `LX LV LC LR SX SV SC SR V+ V+C V+CR
  KV KC` (pp.22-23), all setting the index flag and index result
  indicators per p.24 (loads from the loaded word, stores from the
  unchanged one; `KV`/`KC` set the comparison indicators instead) —
  the load/store ops only gained this when I-Box 1's SIC-B,ZIND group
  tested them, see `strap/README.md` "Gotchas" item 17. **`RNX` IS
  IMPLEMENTED since 2026-11-16** (printed p.27): the old XJ stored at X0's
  old refill (through `writeWordTail`), X0's refill replaced (`writeWord`
  at word 16), XJ loaded from the new name (the deferred index write);
  old or new name in 0-31 is a no-op with AD.  `decks/rnx.strap` runs it on
  C22-6578 Problem 1.8's set-up and checks Problem 1.8's own expected words;
  `decks/ibox4_rnx_run.strap` runs jb_ax4b routine 1244 TEST 4's walk over
  names 1-31.
  `SVA` is implemented.  **`LVE` WAS IMPLEMENTED 2026-10-17** and the
  reason it had been open is worth keeping: this note used to say
  "p.20 describes it only as enabling indirect addressing... and this
  session could not find a page giving its exact bit-level behavior
  distinctly from `LV`'s".  **The page is printed p.29**, nine pages
  on, and it gives the behaviour in full -- which instruction's
  effective address is taken, that the target's operation is not
  executed, that the target's own `J` is ignored, where the result
  goes, and the one-millisecond/`USA` bound on a chain.  The earlier
  search stopped at the overview.  MCP's bootstrap (printed p.3 line
  10, `LVE,15,X1 CCW`) is what forced the question again, and
  `decks/lve_indirect.strap` now exercises all three address
  widths plus the target's index field and the target's ignored `J`.
  CHAINS, as of 2026-11-06: when the target is itself an `LVE`, the
  E-box's `resume()` forms that LVE's effective address and reads
  again, one level per read, keeping the original `J`; once 3334
  clocks (p.29's millisecond at 0.3 us) have passed since dispatch it
  stores the last address formed and turns on `USA`.  MCP's body chains
  this way (printed p.159 line 8 onto p.177 line 15, an LVE whose
  address line 11's SVA fills from the IOD).  `decks/lve_chain_usa.strap`
  tests both.  An EXECUTE
  chain still has no `USA` bound.
- **Connectives** — all sixteen logical functions (`C`/`CM`/`CT`,
  Figure 20, p.75-77), with the same direct/immediate/progressive
  addressing as VFL arithmetic above, **and p.75's byte-size
  expansion as of 2026-10-19**: a storage byte narrower than eight
  bits is zero-extended to eight before the connective is applied, so
  a 21-bit field at byte size 3 is seven bytes and 56 bits of
  accumulator, and `CM` contracts each result byte back on the way
  out. Byte size 8 is bit-identical to the flat field this arm used
  before, which is why the existing connective tests do not move; see
  `StretchVFL`'s `connExpand` for the quotations and
  `decks/connective_byte_size.strap` for the six checks and their
  injections. The accumulator OFFSET is in **bits**, and the
  connective arm's own `offSh` comment records why: it was built as a
  rounded-down byte offset on three strands of manual reading, and
  fifty-six sections of `jb_af1c` killed it, because the
  floating-point diagnostic checks every result with
  `CT0110(BU,60),ROS,4`. **Still not implemented**: Partial Field (`PF`) and
  the left-zeros/all-ones counts at word 7, consistent with `PF` not
  being implemented for VFL arithmetic, so a field of more than
  sixteen bytes is silently truncated rather than setting `PF`.
  **The left-zeros and all-ones counts ARE implemented** as of
  2026-10-20 (printed pp.75-76, `decks/connective_counts.strap`):
  both counters, over the byte-size-eight result field for `C`/`CT`
  and over the contracted field for `CM`. Until 2026-11-17 a
  documented simplification came with them -- `writeWord` did not
  write word 7's counter fields, so an `ST` or `M+` into word 7 lost
  its count bits, and the fifty unassigned bits were kept as stored.
  **Lifted 2026-11-17**, word 11's shape: a store into word 7, the
  connective counts and the FP-divide left-zeros count all arrive on
  wires, and `StretchStorage`'s `commitCounts` is the counters' one
  writer, the counts winning in the same clock (printed p.76, "set at
  the end of the connective operations"); word 7 keeps ONLY bits 17-23
  and 44-50 (printed p.36), the rest reads 0 (printed p.34, "Those bit
  positions that are not so assigned are always zero"); and a `CM`
  whose crossing tail is word 7 carries its counts in the tail word
  (`StretchExecute`'s `countsOverTail`), since the tail is written the
  next clock. `decks/vfl_word7_store.strap` W1-W4,
  `decks/vfl_cross_special_words.strap` K3.
  Verified against C22-6578 Problem 2.2 Method 3's own `CT0110`
  (byte-equality test via XOR) — see `strap/README.md`.
- **Immediate index arithmetic** — all pocket-card ops except `LVS`,
  with the field semantics of Reference Manual p.25: value operations
  place the 19-bit address part in bits 0-18 of the 25-bit value field
  (value = field << 5), count/refill operations take "bits 0-17 of the
  address part" (the field's top 18 bits). An earlier version used the
  raw field for both; found by `tests/verify_ibox1_listing.py` (I-Box
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
  `decks/ibox1_sic_cb_cbz.strap`.
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
  (`decks/bb_branch_on_bit.strap`) whose only path to its PASS
  halt requires correct condition testing plus correct modification on
  both a taken and a not-taken branch, and by `verify_bb_encoding.py`
  (encoding field-by-field vs the decoder's bit positions).
- **Count and Branch / Count, Branch and Refill**.
- **Branch on Indicator**.
- **Unconditional branching** (`B BR BE BD BEW NOP`) — `BE`/`BD`/`BEW`
  all branch identically; the enabled/disabled distinction is
  interrupt-system state this implementation doesn't have. **`BR` is
  BRANCH RELATIVE**, p.40: "causes the absolute value of the effective
  address to be added to the instruction counter contents. Bits 0-18 of
  the sum replace the instruction counter contents." The base is the
  *stepped* counter (p.39 steps it before execution), so the address
  field is a displacement in half-words. It previously executed as an
  absolute branch identical to `B` — found by
  `tests/audit_opcode_coverage.py`, then left explicitly unimplemented
  until p.40 was located rather than guessed at, and now pinned by
  `decks/br_relative.strap`. *Known limit*: p.40 says
  **absolute value**, and an effective address can only go negative via
  index modification; `effAddr19` returns an unsigned result with no
  sign beside it, so an index-modified `BR` that goes negative uses the
  wrapped value rather than the magnitude. Nothing transcribed
  exercises that.
- **Refill / Refill on Count Zero / Store Zero**.
- **Transmit** — see the `TRANSMIT`, multi-word entry below. **THIS
  BULLET WAS A STALE DUPLICATE UNTIL 2026-10-22** and is kept named
  rather than deleted, because that is how this file treats a claim
  it outgrew. It read *"forward, non-swap, immediate count of one
  only. Every other form (backward, `SWAP`, any other immediate
  count, and every *direct* count, whose register this arm does not
  read) sets OP and no-ops."* Multi-word and direct counts were built
  on 2026-10-18 and backward on 2026-10-22; the list below was
  updated and this one was not. **SWAP is the only form still
  refused.**
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
  **simulated** Exchange and five fixed devices (a disk, channel 0;
  a card reader, channel 32; a printer, channel 33; a tape drive,
  channel 34; an operator's console, channel 35) — see
  `StretchIO.bsv`'s file header for the full scope statement:
  synchronous single-block transfer (no real CPU/IO overlap, no
  interrupt propagation), the manual's WRITE "+2" control-word rule at
  termination only (this model has no double-buffer, so a CCW during a
  WRITE reads the unbuffered address), and — now that the External Units chapter
  (pp.129-149) has been read — `CTL` executing only against the tape
  channel and only two of its documented function codes (REWIND,
  BACKSPACE BLOCK, p.132); every other tape function code (SPACE
  BLOCK/FILE, WRITE TAPE MARK, BACKSPACE FILE, density/ECC/parity/
  light functions) and `CTL` on the reader/printer still fall through
  to Operation Code Invalid.
- **The operator's console, IBM 7152 + 7623, channel 35** —
  Reference Manual printed p.150, which is its whole specification in
  one page. A **WRITE** prints and keeps its place across
  instructions, because a console printer does not restart at the top
  of the page for every message and MCP writes one message as a chain
  of control words. A **READ** scans a **three-word switch register**
  — p.150 gives the console "a word weight of 3" and says a READ with
  the keyboard not enabled "is automatically terminated when the
  three words scanned from the switches have been sent to the
  exchange" — and *scans* is literal: nothing advances, so a second
  READ gets the same three words. `C22-6678-1` printed p.29 says what
  the operator puts in them, and MCP's own printed p.23 line 30
  (`BZB,X LR IN+.29`) confirms its bit numbering. Built 2026-10-22
  because MCP's printed p.22 line 5 asks for them.
  The printed output is a **256-word image** (`ConsoleWords`,
  StretchIO.bsv) — a chosen model buffer standing in for continuous
  paper, not a documented number. It was the shared 32-word device
  image until 2026-11-06, when MCP's IPL typed past it and took
  XERR05.
  *Known limits, all of them p.150's and none of them reached by
  anything that runs here*: the **keyboard** is not modelled (only
  p.150's "keyboard not enabled" case exists), the ENTER key's
  **channel signal** is never raised, the ERASE and END keys'
  **end-exception** terminations cannot happen. Its four `CTL`
  function codes *are* implemented and are the exception that proves
  the rule: 016/017/116 drive lights and 177 sounds a gong, none of
  which a model has, so all four are **accepted and do nothing** —
  and the acceptance is the point, because MCP's error routine
  identifies the console by issuing `GONG` and checking that EPGK did
  *not* come on (printed p.5 lines 45-51). 177 on a 729 IV is
  BACKSPACE FILE, which is why that arm dispatches on the unit before
  the code. Which of switch words 1 and 2
  the **numeric** switches scan into is not stated by anything read,
  so they are zero at power-on and that is recorded rather than
  guessed.
- **`LOC` now splits in two.** On a disk
  channel it is a SEEK and is implemented: Reference Manual printed
  p.160, "the right effective address… specifies the arc address",
  and it sets the arc address register the disk's READ and WRITE then
  consume arcs from. On an Exchange channel it is SELECT UNIT
  (C22-6531 Appendix A printed p.57 lists them as one operation:
  "E LOC Locate (same as Select Unit)") and still sets Operation Code
  Invalid — this model's one-unit-per-channel simplification has no
  unit-selection hierarchy for it to navigate, and MCP's ERROR
  ROUTINE is the only thing in the corpus that uses that form (printed
  p.5 line 36). Verified against purpose-written programs (no worked
  example in the manual happens to cover this) — see
  `../strap/README.md`.
- **`TRANSMIT`, multi-word, forward** — Reference Manual printed
  p.30, "Data Transmission". Any count, immediate (instruction bits
  51-54, **zero meaning sixteen**) or direct (the count field, bits
  28-45, of the index register named by J, **zero meaning 2¹⁸**, and
  **J = 0 is X0, not "no index"**). The first word moves in the
  execute arm and the rest in `StretchCore.bsv`'s `rl_xmit`, one per
  clock — `rl_io`'s shape with the device taken out. **Nothing is
  written back**: same page, "the count field in the index register
  is not changed as a result of the operation, and the index result
  indicators are not affected", which is what made it cheap.
  Protection and installed-address are checked **per word**, because
  p.30 says an invalid or protected address "is not detected…until
  the data transmission actually encounters" it — and because without
  the latter a direct count of zero wraps the address space and zeroes
  core, which is what it did the first time MCP ran it. Driven by
  `../decks/transmit_multiword.strap`.
- **`TRANSMIT` BACKWARD** — same page, and the whole difference is one
  sign: *"In backward transmission, the sending and receiving
  addresses of each successive word transmitted are obtained by
  **decrementing** the previous addresses by one. The starting
  addresses specified in the instruction are therefore the addresses
  of the **last** word in each of the two storage areas."* So the
  instruction's own addresses are the starting pair either way.
  `XmitXfer` carries a `backward` flag, `rl_xmit` decrements when it
  is set, and that is the entire change. Built 2026-10-22 because
  MCP's printed p.19 line 41 is `TB,3,0.0($11),0.0($13) -MOVE BIASED
  CTS` and the boot run reaches it. Driven by
  `../decks/transmit_multiword.strap` steps 6 and 7 — five words
  backward with a direct count, three with an immediate count, and
  the **upper-end overlap** the same page says backward is *required*
  for. **`SWAP` still sets OP**, deliberately: a two-way interchange
  is a different datapath. **"NOTHING IN THE CORPUS EXECUTES ONE"
  WAS TRUE UNTIL 2026-10-23 AND IS NOT NOW**: printed p.40 lines 24 and 28 are "SWAPI,3,$11,Y UX SAV", three
words from the UNCODE subroutine's normal exit, and line 33 is the
matched "TI,3,Y UX SAV,$11" with A0 where the SWAPs carry E0.  MCP
saves three index registers with a SWAP and restores them with
another, which is what a two-way interchange is for.
  So SWAP is an unbuilt arm with a documented caller, exactly the
  shape backward transmission was in before it was built -- and the
  run does not reach printed p.40 yet, because `S CA6` on printed
  p.43 comes first.
- **`EX` (EXECUTE)** — Reference Manual printed pp.49-50. "Bits 0-18
  of the effective address form the address of the location of a
  subject instruction that is fetched and executed." The subject may
  be of any type and any length and may live anywhere addressable,
  including in an index register (p.50's own programming note); it may
  itself be an `EX`, to any depth ("the procedure is carried to
  succeeding levels"); and the instruction counter steps past the
  `EX`, never past the subject. A subject branch whose condition is
  met actuates **EXE** (indicator 18) and the whole subject operation
  is suppressed — the branch, `BD`'s disabling, `BE`/`BEW`'s enabling,
  `CBR`'s counting and refilling, `SIC`'s store and `BB`'s bit change.
  The subject's own location is address-monitored (p.32 class 1) with
  p.50's carve-out for effective addresses below 32.00.
  **Not implemented, each stated where it belongs**: `USA`, the
  one-millisecond timeout that is the real machine's only way out of
  an `EX` chain that closes on itself (p.45 item 17); p.50's two
  special exceptions, that monitoring stays in force and interruption
  stays permitted *while the system is disabled*; and p.52-53's
  separate rule for a Class S alert arising during a subject
  instruction.
  Driven by `decks/ex_subject.strap`, `ex_exe.strap`,
  `ex_exe_bind.strap` and `ex_monitor.strap` — fifteen injections
  between them, each observed; the deck oracles are jb_ax5b routine
  1262 TEST 1A/1B/1CC, transcribed for their encoding as
  `ax5b_162_test1b.strap` and `ax5b_162_test1cc.strap`.
- **`EXIC` (EXECUTE INDIRECT AND COUNT)** — Reference Manual printed
  p.50, and it shares `EX`'s subject machinery but adds three rules of
  its own. "Bits 0-18 of the full-word addressed by **bits 0-17** of
  the effective address are used as a pseudo-instruction counter" —
  one bit narrower than `EX`'s operand, so the arm uses
  `baWord(effAddr24(...))` and not `effAddr19`. "After the subject
  instruction has been fetched but prior to its execution, the
  pseudo-instruction counter is stepped. If the subject instruction is
  half-length, the pseudo-instruction counter is stepped once; if
  full-length, twice" — bits 0-18 only; bits 19-63 of the counter word
  come back unchanged. And two address restrictions, which `EX` does
  not have: the counter "cannot occupy locations addressed between 0
  and 15" and the subject must lie at "32.00 and greater"; violating
  either actuates **AD** and the instruction is executed as a no
  operation (p.45 item 16). The counter's own location is a **Data
  Store** address (p.32, "Address monitoring for Data Store includes:
  ... 5. The effective address of EXECUTE INDIRECT AND COUNT"), so a
  protected counter actuates **DS** and the whole operation is
  suppressed before anything is fetched.
  **THE STEP COSTS ITS OWN CLOCK**, and that is forced rather than
  chosen: it is a storage write, so is much of what a subject does,
  and a module method may be called once per rule. `mkEBox` therefore
  writes the step, installs the subject and sets `subjReady`, which
  `canResume()` honours in place of the read handshake; nothing else
  in the machine can observe the extra clock, because `held` stays
  Valid throughout.
  **Not implemented**: the same four bounded negatives `EX` records
  (`USA`; p.50's two special exceptions; a Class S alert during a
  subject), plus p.51 item (d) — a subject location that is both
  protected and invalid actuates IF rather than AD.
  Driven by `decks/exic_subject.strap` (the three rules of
  routine 1262 TEST 2B, both step sizes, the straddling subject, two
  levels with two different step sizes, the counter in an index
  register, and the counter word read as data) and `exic_addr.strap`
  (both address boundaries from both sides, and the Data Store rule) —
  sixteen injections, each observed; the deck oracles are jb_ax5b
  routine 1262 TEST 2A/2B/3A/3B, transcribed for their encoding.

**VFL STORE ROUNDED (`SRD`, code 101101) executes since 2026-11-16**,
binary only, as the ST arm of `vflIntOp` with one add in front: a one
at the bit right of the offset, added to the magnitude (Reference
Manual printed p.64), nothing at offset 0 ("equivalent to a STORE").
LC is the carry out of the numeric width and PF is read from the
unrounded accumulator -- both CHOSEN, in the arm's header and
`docs/spec_factor.md` 4.6.  Timing: ST's budget plus 4 clocks at a
nonzero offset (Perf. Char. Vol. 1 Table 3, `StretchTiming.bsv`).
`decks/vfl_srd.strap` (eleven cases and a CYCLES pin, injections in its header),
`decks/repro_vfl_srd.strap` and Buchholz B.2 as printed
(`tests/verify_buchholz_b2.py printed`) are the checks.  Decimal `SRD`
is built since 2026-11-16 with the decimal set below.

**DECIMAL VFL ADD, LOAD AND STORE execute since 2026-11-16 (G2.3 stage
1): `L`, `LWF`, `+`/`-`, `+MG`/`-MG`, `M+`, `M+1`/`M-1`, `M+MG`, `ST`
signed and unsigned, `SRD`.**  The decimal sum is a SECOND BOX,
`mkDecBox` (`StretchDecBox.bsv`): 32 BCD digits, eight a clock, a pass
for the add and a second pass to recomplement when the signs are unlike
and the operand is the larger (printed p.60's "complementation and
recomplementation").  It is instantiated once in `mkEBox` beside
`mkDivBox`; `NeedBox` carries a `BoxReq` union and the answer comes back
as a `BoxRsp`.  A decimal `L` is an add to zero through the box, which
is C22-6578 printed p.14-15's own description and gives its "(1111)2
... will become (0101)2 with a carry".  Byte placement (any byte size to
four-bit digits and back, zones kept or taken from the sign byte
register) is wiring: `decCompact`, `decMergeField`, `decStoreField` in
`StretchALU.bsv`.  Which codes accept the decimal modifier is ONE
function, `vflDecimalBuilt` (`StretchVFL.bsv`), read by execute() and
by `prepareExec`.  `tests/run_decbox_test.sh` tests the box alone
(literal answers and clock counts, p.60's five examples among them);
`decks/vfl_decimal_add.strap` is the deck.  Open items: `docs/NEXT.md`,
"DECIMAL VFL ARITHMETIC (G2.3)".

**THE COMPARES, stage 2 (2026-11-16): decimal `K`/`KF`, and `KE`, `KFE`,
`KR`, `KFR` in both radices (printed pp.65-67).**  One arm.  A decimal
compare is a subtraction through `mkDecBox` (p.65's Programming Note,
item 4); the sign rule is the binary one ("-0 = +0").  `KE`/`KFE` leave
the comparison indicators alone when AE is off; `KR`/`KFR` when AH is
off, and otherwise turn AE on and AH off for a low accumulator.  The
data flags are set in every case (a reading, marked CHOSEN in the arm).
`decks/vfl_decimal_compare.strap` runs printed p.66's Figure 15 as
printed.

**LOAD TRANSIT AND SET is built in both radices, 2026-11-16**, and with
it decimal `*`, `*+` and `/`, which printed pp.68-70 define as LTRS's
action, not arithmetic: the transit register (word 15) gets the operand's
numeric part above a four-bit sign byte, the all-ones counter the
effective offset, the left zeros counter's two high-order bits the
operation's discriminator (LTRS 11, `*` 00, `/` 01, `*+` 10), and BTR or
DTR comes on (printed pp.67-68).  The counts go to location 7 through
`connCounts`, the connectives' route.  CHOSEN: a decimal operand is
loaded as four-bit digits ("Radix ... as in ADD"); the full seven-bit
offset is loaded.  Timing: since the per-operation merge, PDF 123's
measured LTRS page (44 clocks binary, 66 decimal, +16 above 48 bits),
not Table 3's row, which sits 4 clocks under it; decimal `*`, `*+`, `/`
are charged the decimal LTRS figure, CHOSEN because their own pages
(PDF 133-135) print binary rows only (`StretchTiming.bsv`).  `decks/vfl_ltrs.strap`.

**THE BINARY ARMS MADE TO AGREE, 2026-11-16 (the decimal work's three
findings).**  (1) RN is the sign bit in both radices -- printed p.47's
"negative whether zero or not" -- so `setResultIndicatorsDec` is folded
into `setResultIndicatorsF`.  (2) Binary `+`/`+MG` set LC (carry out of a
like-signed sum) and PF (operand bits past the accumulator's left end),
and binary `L`/`LWF` set PF, "as in ADD" (printed pp.60-61).
`decks/vfl_binary_add_indicators.strap`.  (3) A progressive operation
whose index refills no longer applies itself twice:
`vflRefillOutstanding` holds every arm that uses a shared trailing block
until the refill word is in hand (printed pp.21-22, "the variable field
length part ... and then the index modification portion").
`decks/vfl_progressive_refill_once.strap`.

**THE LAST TWO DECIMAL REFUSALS, 2026-11-16: `DCV` in both radices and
decimal `LFT`.**  CONVERT DOUBLE (printed p.74) is CV's arm with 20/96 for
68/48; its conversion runs in a THIRD BOX, `mkCvtBox`
(`StretchCvtBox.bsv`): double dabble sixteen bits a clock to decimal,
Horner eight digits a clock to binary, reached by the same `NeedBox` bail
(`BoxReq` is now a three-way union and `mkEBox`'s `boxKind` says which box
is held).  **Since 2026-11-17 `CV`, `LCV` and `LTRCV` use it too**, and
the inline `binaryToBcd`/`bcdToBinary` are deleted: no combinational
converter is left in `execute()` (a decimal field of another byte size
reaches the box as four-bit digits, `decFieldDigits`; LUT4 figures in
`docs/fpga_feasibility.md` §10.6).  `tests/run_cvtbox_test.sh` tests it alone;
`decks/vfl_dcv.strap` runs the Reference Manual's Figure 19 end to end
(LCV, LTRCV, `*`, DCV, decimal ST).  Timing: `eboxClocks`'s DCV row, the Vol. 2 atlas
PDF 139 point (20 binary, 18 decimal), Table 3's dependence on S unmodelled since its terms
depend on the operand.  Decimal `LFT` puts four-bit digits in FT (printed
p.69, "Radix ... as in ADD"); `decks/vfl_lft_decimal.strap`.  With both
built, `vflDecimalBuilt` was true of every code and is GONE, with the
decimal refusal in execute() and in `prepareExec`.

**THE BINARY INDICATOR SWEEP, 2026-11-16.**  Every indicator sentence of
the VFL arithmetic chapter (printed pp.58-74) read in the page images, op
by op; the table is in `docs/NEXT.md` G2.3.  Fixed: binary `M+`, `M+MG`,
`M+1`, `M-1` set LC (carry beyond the field, or an unsigned field whose
result is negative) and PF (an accumulator one-bit left of the
participating field; not for `M+1`), and add only the field-wide
accumulator operand -- `binMemAdd` in `StretchALU.bsv` (printed pp.59,
62-63, Figure 13); binary `*+` sets LC "as in ADD" (printed p.69) through
`binAccAdd`, the rule `+`/`+MG` now share; `LCV` and `LTRCV` set the data
flags (printed pp.72-73); decimal `LCV` sets PF past the accumulator's
left end; decimal `LTRCV` sets PF for a field over 15 digits and puts
only 48 bits in $TR (printed p.73).
`decks/vfl_binary_memadd_indicators.strap`.

### Decoded but not executed (sets indicator 15, OP, and no-ops —
### matches real-machine behavior for a suppressed instruction)

~~Decimal-mode VFL (`c=1`)~~ -- **gone from this list 2026-11-16: every
VFL integer code executes in both radices** (decimal `LFT` and `DCV` were
the last); ~~`RNX`~~ -- **built 2026-11-16** (above).  What remains:
Input-Output's `LOC` **on an Exchange channel** (the disk form is
executed — see above) and most of `CTL`. **Transmit's BACKWARD `SWAP`
LEFT THIS LIST ON 2026-11-08** (see below).

**AND THE VFL INTEGER LIST WAS WRONG IN BOTH DIRECTIONS, 2026-10-25.**
An exact census -- every `6'b......` arm in `vflIntOp` against
`opcodes.VFL_INT_CODES` -- says the model executes **ten of
twenty-four**:

```
EXECUTED   +(1) LCV(3) L(5) M+(9) ST(13) K(17) *(25) +MG(33)
           M+MG(41) M+1(43) KF(49)
NOT        LFT(11) KE(19) KR(21) CV(27) /(29) LTRCV(35)
           LWF(37) SRD(45) KFE(51) KFR(53) *+(57) DCV(59) LTRS(61)
```

(A census of that date. `LWF` executes since 2026-11-09, binary `SRD`
since 2026-11-16, and later entries in this file record others.  As of
2026-11-16 all twenty-four execute, `DCV` last.)

**`*` MOVED ACROSS ON 2026-10-25** and the census above already
reflects it: eleven of twenty-four. `decks/vfl_multiply.strap` is the
check and `docs/vfl_arith_spec.md` is the sourcing.

So `LCV` and `KF` were named here and DO execute, while **`*`, `/`,
`KR`, `LFT`, `LWF`, `SRD` and `*+` were not named and do not** --
seven operations missing from a list whose whole job is to say what
is missing. The two that matter for MCP are `/`, which printed p.24's
time conversion uses twice, and `*`, which printed p.72 line 19 uses
to compute a location within the machine-configuration table.

**AND THE SOURCING IS IN HAND FOR THE TWO THAT MATTER.** Reference
Manual `22-6530-2` printed **pp.68-70** specify them normatively:

* **p.68, Multiply (`*`)** — "the product of the addressed operand
  and the accumulator field specified by the offset is placed into
  the CLEARED ACCUMULATOR AT OFFSET 20. Neither operand may exceed 48
  significant numeric bits." PF if either does; result indicators as
  in ADD. **Built.** And the CE manual `R23-9694` printed p.117 says
  *why* 20: "the actual multiplication in this operation is performed
  by PAU ... the result appears at offset 20 as this is the normal
  result field (12-107) for a double-precision PAU operation", which
  also decides the product's sign — the Reference Manual never states
  it, but the PAU's own multiply (printed p.75) does: "the sign of
  the product replaces the accumulator sign ... determined by the
  rules of algebra".
* **p.69** — Load Factor (`LFT`) and Multiply and Add (`*+`), and
  "FT is a 64-bit register with word address 14".
* **p.70, Divide (`/`)** — "the entire accumulator contents to the
  left of the offset are divided by the addressed storage field ...
  the quotient is placed in the cleared accumulator at the specified
  offset, and the remainder with sign is placed in the remainder
  register (RM)". Dividend ≤ 96 significant bits, divisor ≤ 48.
  **ZD: the division is not attempted and both the accumulator and
  RM remain unchanged.** Result indicators describe the QUOTIENT.
  And RM to the bit: "Bits 0-59 of RM are replaced by the integer
  remainder with the low-order remainder bit in bit position 59."

That last sentence is checkable against the corpus right now: MCP
printed p.24 line 22 is `C0011(BU,6),$RM+.54` — bits 54-59, the
low-order six bits of the remainder, which is exactly what sixty
seconds needs. **The listing and the manual agree to the bit.**

What is still missing is an *oracle with expected values*: no
diagnostic in `docs/` exercises VFL `*` or `/`, and a grep across
every deck finds them only in `mcp_bootstrap_p24` and
`mcp_bootstrap_p72`. `C22-6578` Programming Examples (Apr 61) is
unopened and is the likeliest source of worked arithmetic.

**HOW THE LIST GOT CHECKED:** `StretchExecute.bsv`'s commit point
now prints the address of every instruction that sets OP (one
`$display` at the single `st.setIndicatorBits(ind)`, with the arms
run on an OP-cleared word so every refusal shows and not just the
first). One boot run names them all. That is the tool
`docs/NEXT.md` asked for in October, and it is three lines.

**`SWAP` LEFT THIS LIST ON 2026-10-23** — the FORWARD forms, `SWAP`
and `SWAPI`, execute. The entry used to read "Transmit **`SWAP`**
(backward moved to 'Executed' on 2026-10-22)". What is left is the
backward pair, and the reason is narrower than "not built": **nothing
in this corpus encodes one.** `tests/verify_ax4b_1246_modifiers_
listing.py` calls `SWAPB` and `SWAPBI` *card-only* — named on pocket
card X22-6533 and written by no deck — so building them would be
manual-derived with no oracle, and `rl_xmit`'s sign handling would
carry them unchanged the day one turns up.

> **>>> THAT JUSTIFICATION IS FALSE, AND THIS IS THE ONE SENTENCE IN
> THIS FILE THAT WAS LOAD-BEARING FOR A REFUSAL. <<<** "Written by no
> deck" is true; **"nothing in this corpus encodes one" is not.**
> `C22-6578`, which is in `docs/` with OCR, prints `SWAPBI` TWICE as a
> worked example:
>
> * **printed p.5, Problem 1.2, Method 1** — "Use immediate swap
>   instructions": `SWAPI, 2, DOG, CAT` **or**
>   `SWAPBI, 2, DOG +1.0, CAT +1.0`
> * **printed p.6, Problem 1.3** — `SWAPBI, K, DOG + N-K-1`
>
> So backward SWAP is **buildable with two printed oracles**, not
> blocked. It is one of the four items left on StretchExecute's scope
> list, and the cheapest of them. Found 2026-10-29 by a census of the
> worked examples; verified at the OCR before this note was written.
>
> **BUILT 2026-11-08, `SWAPB`/`SWAPBI` execute.** The arm passes the
> direction to `rl_xmit`, whose stepping already honoured it. Checked by
> `decks/problem_1_2.strap` (the printed statement, the direct-count and
> J = 16 forms comment (b) implies, and an overlap that shows the
> direction) and `decks/problem_1_3.strap` (comment (a)'s rule, N = 4 and
> N = 9). Those two decks are the injection record: see `tests/run_tests.sh`.

**WHAT CHECKS THE FORWARD FORMS:** `decks/swap_scope.strap`, five
blocks, every expected value computed from Reference Manual printed
p.30 before the arm existed. Block 1 is IBM's own `jb_ax4b` routine
1246 TEST 2C with its branch logic replaced by a storage check; block
4 overlaps the two areas by one word, which is the only way to see
the order the words are exchanged in.

*The caution this list exists for applies to its own former entry:
the claim "nothing in the corpus executes one" was true when written
and stopped being true when MCP printed pp.40-46 were transcribed.
A scope list is a measurement with a date on it.*

**TWO STALE ENTRIES WERE REMOVED FROM THIS LIST, 2026-10-19,** and
they are named rather than quietly deleted because a scope list
nobody rechecks is how a model gets credited with gaps it does not
have and absolved of ones it does:

- *"floating-point arithmetic beyond L/ST"* — **wrong, and by a
  wide margin.** `StretchFP.bsv` is 1,260 lines and **103 suite
  sections run `jb_af1c` floating-point programs ON THE MODEL**:
  add, add-to-fraction, add-to-exponent, multiply, multiply-and-add,
  divide, double-precision load/store, the sign modifiers, the
  magnitude compares, noisy mode, and the zero-multiply rules. The
  sentence predates all of it.
- *"and `LVS`"* — built 2026-10-19,
  `decks/lvs_multiple_indexing.strap`.

(SIC, Store Instruction Counter If, Bit Branching, `EX` and `EXIC`
have all moved to "Executed" — see there.)

**The Transmit entry was two-thirds FALSE until 2026-09-22**, and is
worth keeping as an example of how that happens. Only `backward` set
OP. `StretchDecode` matched sub-ops `010` (Transmit) and `110` (Swap)
in one condition and recorded *neither* — `StretchTypes`' `Transmit`
struct had no `swap` field — so a forward `SWAP` reached the execute
stage indistinguishable from a Transmit and was executed as one. And
the execute arm never read the count, so a multi-word Transmit moved
one word. Both silent: no indicator, no failure, a wrong store.
Demonstrated before fixing — `SWAPI,1,SRC,DST` left `SRC` alone and
copied it into `DST` with OP clear.

It could stay false because **nothing could express it**: this
project's assembler could not encode Transmit at all until
`TRANSMIT_CODES` landed the same day. A claim no test can break is a
claim nothing checks, which is `docs/NEXT.md`'s own corollary applied
to prose. The guard is now `decks/transmit_scope.strap`, six
blocks and five injections, one per rule — **four of whose blocks
have now flipped from asserting a refusal to asserting that the
operation happens**: three on 2026-10-18 when multi-word and
direct-count Transmit were built, and block 6 on 2026-10-22 when
backward was. Each flip was MCP asking for the operation. SWAP is the
one refusal left. **The 2026-10-22 flip also moved the deck's PASS
address back one half-word** (`BZOP,$ / BOPZ,$+.32` became a single
`BOP,$`), so the run's PC check is load-bearing in that file and not
decoration. **Block 6's injection was replaced rather than re-run**:
"remove the backward check" means nothing once the check is gone, so
the new one restores `t.backward == 1 ||` and is caught at a named
address — the run hangs on block 6's `BOP,$` at `004111.40` with
`DST6` still zero.

Per the "decode completely, execute partially" principle: every format
in Figure 6 has a `DecodedInstr` constructor and is field-extracted
correctly even where unexecuted, so the decoder is honest about what
it recognizes independent of what the datapath implements.

### An index read waits for a pending progressive write (fixed 2026-11-08)

Reference Manual printed p.21: progressive indexing "is executed in two
parts", the second writing the index register back. E-box-class instructions
already waited for that, but an I-box instruction could run ahead of it and
read the old value. The 7030 SMAC (`../decks/smac7030_shell.strap`) found this:
its frame-restore loop `ST(BU,64)(V+I),1.0($3)`, `KVI,$3,LIMIT`, `BXL,LOOP`
copied one word too many, over the operation table. `iboxHazard`
(`StretchIBox.bsv`) now holds an I-box instruction that names such a register,
as an operand, as the register modifying its address, or as a storage word
(16-31). Its R/RCZ test also read the wrong register's refill field, the one
that modifies the address and not the operand's; that is fixed too.

Test: `../decks/index_after_progressive.strap`. Its header records which cases
fail with the interlock off (KVI, V+I, CB, an indicator branch and a count
branch through X1, LX and Z of the register as storage) and which do not, so
the arms for those are not yet shown to be needed.

### A look-ahead level carries the I-box's indexing (2026-11-15)

A look-ahead level's operand and store addresses are derived when it is loaded,
and the store-close-to-fetch waits compare against them. But the E-box
re-derived the effective address from the current index registers when it
dispatched the level. An I-box instruction that wrote the register in between
moved the level's operand. The 7030 STRAP II MAIN test's driver (step 4b-i)
found this: `ST(BU,64),9.0($9)` was loaded as a level, `V+I,$9,11.0` ran ahead
of it, and the store landed in the next record. It showed only for layouts that
kept the store pending, and the first diagnosis (a stale index after an LV) was
wrong; a store and read trace in storage settled it.

The first fix, the same day, was a stall: `iboxHazard` held an index write while
a pending level was indexed by that register (`levelIndexedBy`). That stall is
gone. The level now carries what the I-box's indexing produced (`LaCarry` in
`StretchTypes.bsv`: the effective address, and a VFL instruction's length, byte
size and offset after the second index). `rl_prepare` reads the index registers
once (`carryIndex`), derives `da` and `storeAddr` from the instruction as
carried, and `rl_au_remove` hands the E-box that instruction with its index
fields cleared (`carriedInstr`), so `execute()` indexes nothing and is not
edited. This is the machine's arrangement: a level holds an operation code, the
operand, indicators and an instruction counter, and no address or index field
(Buchholz section 15.3, printed pp.238-240; 7101 CE manual R23-9732 Fig. 3.2.2,
PDF 93). An I-box index write behind a level therefore runs without waiting.

Two things are left as they were, each for a stated reason:

- **Progressive indexing still reads its register in the E-box.** The
  instruction reads and writes that register in two parts, and
  `progressiveWrites` and `progressivePending` already hold it still. Its
  second index is carried like any other.
- **The level's decoded instruction is kept beside the carried values.** The
  timing functions read it, and `eboxClocks` must not see a length the second
  index has changed; that would move times for a reason no table gives.

**An immediate VFL operand is indexed (fixed 2026-11-18).** Until this date
the carry left an immediate (`P` = 4) address field unindexed and every
`immediateOperand` call in `execute()` read the address field, so
`LI(BU,24),5($X3)` loaded 5 whatever X3 held. The Reference Manual says
otherwise: printed p.21 (PDF 24), "The codes 0 and 4, which both specify
standard address modification ... For code 4, the immediate mode is specified
and the effective address is used as the operand itself"; printed p.56 (PDF
59), bits 0-23 are "indexed by the contents of the index register specified in
the I field ... or it may be used as data". `carryIndex` now indexes `P` = 4 as
it does `P` = 0 and `carriedVflAddr` clears `i1` for both. `execute()` takes the
operand from `ea`, which is the carried value for a level and the live indexing
for an EX subject, since EX subjects are not carried. Timing is unchanged
because the timing functions read the uncarried `di`. No IBM listing we searched
writes an indexed immediate: 936 immediates were assembled across 812 decks and
none had a nonzero first index; the untranscribed diagnostic PDFs were not
searched. `decks/vfl_immediate_indexed.strap` is the
oracle and records its injections. Still open: a negative effective address
should give its magnitude (p.20, p.21), but `effAddr24` wraps it (NEXT.md).

**The store wait (2026-11-16).** The other direction is a level that stores into
an index register, and the model handled it badly. A new level indexed by j
waited for a pending level storing word 16+j (`indexStorePending`), but an I-box
index instruction did not wait at all: `ST(BU,64),$X3` then `V+I,$3,1.0` read
the old $3. This failed the same way on commit 3204601, so it predates this
work. A probe written for this change found it, and so did a reading of the 7101
I-unit flow diagrams.

Those diagrams draw the 7030's mechanism, keyed on the store's own address and
nothing else (R23-9732, I UNIT FLOW DIAGRAMS; all three read in the page
images for this change):

- Fig. 3.1.20, "ZL FP3 TRIGGER" (PDF 84, printed 1-41/1-42), under "FPL 4 E TGR
  ON": "ZOAR EQ 11 + 12 + 16 - 31 (28.42.51.1)" -> "TON STORE WAIT TGR", "BLOCK
  STORE WAIT TGR TOF", "TON I RCY REQ TGR (28.42.72.1)".
- Fig. 3.1.13 sheet 3, "ZR FP TRIGGERS" (PDF 77, printed 1-27/1-28), from
  "FPR4E": "ZOAR EQ 11 +12 + 16 - 31 (28.42.51.1)" -> "TON STORE WAIT TGR",
  "TON IRCY REQ TGR (28.42.72.1)".
- Fig. 3.1.24, "WBC TRIGGER" (PDF 88, printed 1-49/1-50), for VFL: "W EQ 11 +
  12 + 16 - 31 (28.11.55.1)" -> "VFL CL 2 . VFL 5E" -> "VFL 5 CL 2 COND STORE
  WAIT (28.21.71.1)", and the same from "ZL 11 + 12 + 16 - 31".

So `storeWait` (`StretchIBox.bsv`) is True while any pending level stores into
word 11, 12 or 16-31, and `rl_prepare` then prepares nothing until that level
retires: no I-box instruction and no new level. It replaces `indexStorePending`.
The pages draw only the trigger's turn-on. Three things are the model's
choice: that STORE WAIT holds all preparation (no box takes it as a
condition), that the store's retirement releases it, and that the I-unit
recovery costs nothing. It is a conservative wait, not a measured time. Since
2026-11-17 a field crossing into word 16-31 from word 15 is built, and the
test also checks a crossing store's second word (`storeAddr2`, CHOSEN: the
figure's hexagon tests W only); `../decks/vfl_cross_storewait.strap` is
that case (ST from word 15 into $X0, then SX,$X0; injection measured).

Test: `../decks/index_after_index_store.strap` (V+I and SV of $3 behind a
pending `ST(BU,64),$X3`). Its header records the measured injection. Two parts of
the rule are not shown to be needed by any test: its breadth (a wait only for
instructions that use register j would pass every case), and words 11 and 12,
which are in it because the pages print them (a direct-index read of either word already waits
through `levelHolds`).

Test: `../decks/index_after_level.strap`, 43 words, the halt PC and a cycle
count. Its header records the measured injections: the E-box re-indexing fails
the V+I cases and the overtaken floating store, the missing wait fails the
E-box sibling, and the old stall put back fails only the cycle count.

### The divide box (2026-11-16)

The VFL divide arm of `execute()` computed `dvd / dsrSafe` and
`dvd % dsrSafe` on 96 bits with a variable divisor. Synthesised alone that
was 118,755 LUT4 + 22,896 CCU2C, about twice the ULX3S. The division now
runs in `mkDivBox` (`StretchDivBox.bsv`). `execute()` takes a
`Maybe#(DivRsp) boxResult` and has a third answer, `NeedBox DivReq`,
beside `Complete` and `NeedOperand`. The arm returns `NeedBox` with the
dividend and divisor when it has no result, and uses the quotient and
remainder when it does. The floating-point divides `/`, `R/` and `D/`
use the same box and bail: they used to inline `fpDivFrac`'s 96 unrolled
restoring steps three times. Now `fpArithClass` reports the fractions it
needs divided in `FpCommit.divReq` and takes the answer as `divQR`.
`fpDiv`/`fpDivDouble` take the quotient and remainder as an argument.
`mkEBox` issues the request, holds the
instruction exactly as it does for an operand read (`boxWait`), and
`canResume()` becomes "the read answered, OR the box has its answer".
`resume()` then re-runs `execute()` with the answer. An instruction that
needs an operand word and then the box does both in turn. A box bail
also sets `needsRead` (to a placeholder), so every existing
`!isValid(needsRead)` guard keeps the bail free of writes. A zero divisor
never sends a request (p.70: "the division is not attempted").

**The E-box time is unchanged; the overlap is not.** `rl_exec_resume`
subtracts the clocks the box took (`ebox.boxClocks()`) from the E-box
budget it then charges. The I-box-dispatched path is charged
`budget - elapsed` already. But while the divide waits on the box, its
look-ahead level is held, and the instruction unit executes no I-box
instruction (`rl_prepare`'s `!ebox.busyFor(OwnerLA)`). The old divide
retired in its first clock and the I-box overlapped the countdown. So 8
of the 16 FP-divide decks got slower: f217b, f217wb and f217xb by 16
clocks, f217we and fp_zm_cleared by 8, f217d by 4, f217a by 2 and f217c
by 1. The first five shrink in proportion when the box is made faster
(the hold window). f217d's +4 goes away at 2 box clocks. f217a's and
f217c's are constant and not yet explained. No suite CYCLES check moved,
because none of those decks has one. The box header has the table.
(These figures are for the 4-clock box; since the FP divide's time
became Table 2's, 2026-11-17, they are stale for the FP decks.)
Getting the overlap back is an `rl_prepare` change.
The box takes 4 clocks for the VFL divide. An
overrun would print `DIVIDE BOX OVERRAN THE E-BOX BUDGET`. The 24 bits a
clock is invented, and the box header says so.

**The floating-point divide's time (2026-11-17).** For `/`, `D/` and `R/`
the box also walks the 7030's own divide algorithm for its LENGTH: one of
the multiples 1, 3/4 and 3/2 of the divisor per add cycle, chosen by
Buchholz Fig. 14.11, at most six shifts per cycle, and dummy shift cycles
beyond six (Buchholz pp.213-216). The walk runs one reduction loop a
clock beside the restoring steps, and does not touch the answer. It
reports `fpExtra`, which is Perf. Char. Vol. 1 Table 2's divide row
(printed p.3-5): the pre-shift terms (`fpDivFixedClocks`, StretchFP),
2 per additional reduction loop, 2 for a complemented final remainder,
and D/'s remainder normalization. `mkEBox.boxCharge()` hands `fpExtra`
to `rl_exec_resume`, which adds it to `eboxClocks`' zero-divisor floor of
5 (`R/` 9). A normalized 1 divided by a normalized 1 costs 25 clocks, the
atlas's 7.50 µs. The atlas residual for `/` and `R/` went from −16..−20
to +1, and for `D/` from −21 to 0. One point is RECONSTRUCTION: whether
the counter-loading second divide cycle counts as a loop. The box header
and `docs/NEXT.md` "FP DIVIDE TIME" give the reasoning. The budget is
always more than twice the walk's clocks, so it cannot overrun.

Test: `../decks/vfl_divide_box.strap` (full width, a 96-bit quotient,
the largest remainder, the four sign cases with `vfl_divide.strap`, zero
dividend and divisor). It passed unchanged on the model before the box,
`CYCLES=1196+-0` included.

### VFL time depends on the operation (2026-11-16)

**What changed.** `eboxClocks` (`StretchTiming.bsv`) used to charge every
VFL operation `8 + 2·bytes`, so L, `/` and LCV cost the same. It now
charges each operation the E-box occupancy that Perf. Char. Vol. 2's atlas
measures for it, on its own page in PDF 116-142, less the one removal
clock. The connectives are treated the same way: C is PDF 140, CM is
PDF 141 and CT is PDF 142. The arm cites a page and a cell for every
number. Each law is a fit to a printed page, not a mechanism. Where
Table 3 makes the time data-dependent, the fit holds at the atlas's
operands:

- `/` was measured dividing by one, and the atlas's authors disown that
  page as a divide timing (PDF 41).
- LCV and LTRCV were measured on the standard operand.

**Byte count.** It is Table 3's x/y, with one byte added for a sign
(Table 3's preamble, Vol. 1 printed p.3-6). A signed field no longer
than its sign byte has no data bytes.

**Why the old M+ "0.28 µs" did not hold in sequence.** That figure was
the serial budget `2·iboxCycles + eboxClocks`, which only the I-box
dispatch path charges. On the look-ahead path the 12-clock preparation
and the E-box charge run concurrently, so the throughput is
max(prep + 2, E-box + 1). An E-box charge below the preparation is
invisible in sequence. `docs/atlas_oracle.md` has the measurement and
the open question: in a homogeneous sequence the two run concurrently,
but a mixed one might run decode and E-box in series.

**Atlas residual, PDF 116-142** (6,098 cases):

| | mean | exact |
|---|---:|---:|
| before | −18.93 clocks | 423 |
| after | −3.46 clocks | 2,225 |

`docs/atlas_oracle.md` has the per-page table.

**Behaviour is unchanged, after two look-ahead fixes the new times
exposed.** The first subset run (139 sections) had the same 478 result
lines before and after. A wider one (218 sections, adding every deck that
uses a VFL or connective instruction and every `STEPS=` run) found two
that changed results: C22-6578 Problem 2.6 Method 3 (twelve of sixteen
packed fields missing) and Problem 4.7 Method 2 as printed. Both pass on
the old times. The cause was latent ordering hazards, not the times.
Progressive indexing sets the index indicators (XCZ and the rest) when
its level executes, and `iboxHazard` let I-box instructions that read or
set those indicators run ahead of a pending progressive level. Longer
VFL times moved the levels' execution past them.

1. **A branch on an index indicator read it too early.** In 2.6
   Method 3, `BZXCZ` read XCZ before a progressive ST had counted.
   - Fix: such a branch waits while any pending level is progressive
     (`anyProgressive`).
   - Test: `decks/vfl_pack_cross.strap`. Without the fix it halts at
     214 clocks with five failed fields. With it, `CYCLES=889+-0`.
2. **An index instruction's indicators were overwritten.** In 4.7
   Method 2, `V-ICR,$3` set XCZ ahead of a pending progressive
   connective, which then overwrote it with `$1`'s.
   - Fix: index arithmetic, load/store-index and count branches wait
     too (`setsIndexInd`).
   - Test: `decks/vfl_index_ind_order.strap`. Without the fix the loop
     runs 16 passes instead of 4 (2099 clocks). With it,
     `CYCLES=687+-0`.

Both fixes are conservative waits, not a model of the I-box's indicator
timing. No source tells when the real machine sets them.

3. **A level fetched the second word of a crossing store too early**
   (2026-11-17). The full suite on batch13 found this one: the 7030 STRAP
   II TABMAN test lost the vle's 6-bit length field (46, in bits 6-11 of
   the vle area's word 13).
   - What went wrong: TBEN3's `ST(BU,13),.1($4)`, with $4 at bit 62,
     writes two words. A later `ST(BU,6),.14($4)` fetched the second
     word at load. The store-close-to-fetch wait compared only the
     crossing store's first word, so the later ST merged its field into
     the old word and stored it back over the crossing store's tail.
   - How it was found: by diffing a write trace of the run against one
     made on batch12's times.
   - Fix: `levelStores` in StretchIBox. A level whose stored field crosses
     a word boundary (`storeCross`, set for VFL ST/SRD and CM) is
     compared on both words, in rl_prepare's wait, in `levelHolds` and in
     `storeWait`.
   - Basis: Perf. Char. Vol. 1 printed p.3-18, "VFL data with word
     boundary crossover represent inefficient use of LA levels". On the
     machine a crossing field takes a level per word. One level comparing
     two words is CHOSEN; the second level's cost is not modelled.
   - Test: `decks/vfl_store_cross_fetch.strap`, `CYCLES=262+-0`. Without
     the storeCross term W1 = 0x0001800000000000, and nothing else fails.
     Case 2, a branch between the stores, is the control.
   - This case was not in the 236-section subset, because the strap2_7030
     checks run outside it.

After both fixes, the 220-section subset passes with 0 FAIL lines:
every CYCLES and STEPS run, every deck using a VFL or connective
instruction, the MCP sections and the smoke test. Neither fix moved a
pin. The atlas's I-box pages, PDF 106, 107, 109 and 112 (167 cases),
are unchanged to the hundredth of a clock.

**Pins moved to measured values**, each deck's header saying why:

| deck | clocks before | clocks after |
|---|---:|---:|
| `index_after_level` | 2407 | 2828 |
| `index_after_index_store` | 1132 | 1248 |
| `vfl_srd` | 974 | 1223 |
| `vfl_progressive_index0` | 145 | 164 |
| `vfl_decimal_refused` | 140 | 163 |
| `vfl_divide_box` | 1196 | 2148 |
| `la_timing_loop` | 807 | 918 |

`la_timing_loop`'s bound moved from 900 to 1000.

The divide box's clocks are still taken out of the E-box charge, and no
DIVIDE BOX OVERRAN line appears.

MCP's own bootstrap now completes in 6,424,235 steps, against
6,423,052 before. The new VFL times account for 6,424,243 of that, and
the two hazard fixes take it down by 8. The fixes changed no cycle count
in the 220 sections. Three other MCP step counts moved by 4 to 8 steps:
- the decode stop: 6,406,963 to 6,406,955
- ASSIGN: 6,425,638 to 6,425,634
- past T MOVE: 6,442,193 to 6,442,189

**New pin.** `decks/vfl_op_timing.strap` runs eight each of L, M+, K,
`*` and `/` at (BU,64,8):

- 1193 clocks before, 1979 after.
- Injection: forcing every code to L's arm gives FAIL cycles = 1331 and
  nothing else.

CV and DCV have pages (PDF 138-139) but no oracle generator, so the
model charges them those pages' flat figures without measuring them.
CV runs in `vfl_convert.strap` and in MCP decks, but no pin is on its
time. DCV (code 59) is not built in `execute()` and fails loud, so its
arm is not run yet.

**Merged with batch10 (decimal VFL, 2026-11-16).** Most decimal arms
were already fitted to the pages' decimal rows: PDF 116-132 and 136-139
print DU/D rows, so decimal `+`, `M+`, L, ST, SRD, K and the rest keep
their laws. PDF 133-135 (`*`, `/`, `*+`) print binary rows only. Decimal
`*`, `*+` and `/` are LTRS's action, so they are charged PDF 123's decimal
LTRS figure, 66 clocks, or 82 above 48 bits. That choice is CHOSEN, not
measured. Re-pinned after the merge, every result check unchanged:

| deck | clocks before | clocks after |
|---|---:|---:|
| `vfl_srd` | 997 | 1246 |
| `vfl_ltrs` | 974 | 1214 |
| `vfl_decimal_refused` | 161 | 224 |

`vfl_ltrs` was pinned to Table 3's row (16 + 2 x/y); it now has PDF 123.

**Not modelled, or open.**

- The connective arm (C, CM, CT) has no suite pin or injection. Only the
  atlas run checks it: C0011 is 139 of 210 exact.
- Not checked: whether an EX subject that is E-box class is charged its
  own `eboxClocks`. EX is not E-box class, so it is charged on the I-box
  dispatch path's `budgetClocks`.
- The VFL store's extra time to an I-box operand (+13 to +16 clocks)
  and across a word boundary (about +30). These are a store-path
  matter, and `eboxClocks` sees no address.
- The INVERT SIGN blocks' unlike-sign terms, which depend on the data.
- The 12-clock preparation floor of K and CT. The model's floor was 14.
  FIXED 2026-11-17: see "The preparation floor" below.

### FP operands are fetched by the look-ahead (2026-11-17)

`StretchIBox.bsv`'s `fetchesOperand` was True for FP L only, from the
look-ahead's first cut (stage 3a), when L was the one FP operation built.
Every other fetching FP operation was loaded into a level with no operand
address, and the E-box read its operand at removal, in series with
execution. `fpFetches` now names them all: every operation `execute()`'s
Fp arm reads a word for, which is all but ST, SRD, SLO, SRT, SHF and E+I.
`prepareExec` uses the same list. Measured by `tests/atlas_oracle.py`
(`docs/atlas_oracle.md`, "Closing the residuals", item 1): PDF 42 (+) from
mean +4.79 to −0.27 clocks, PDF 65 (LWF) from +4.65 to +0.47. No result
check changed and no CYCLES pin moved.

### The LAAR, for floating point (2026-11-17)

Perf. Char. Vol. 1 printed pp.3-20/3-21 give the 7030 one look-ahead
address register. It is busy from the loading of a store level until the
store operand "is available, is fetched, checked, and accepted by the
MBCU". An internal-operand fetch (address 3 or 5-12) also takes it. A
second instruction that needs it waits at decoding. A store into index
storage stops all decoding until the new contents arrive. Vol. 2 PDF 41
names this queuing as the reason the FP "to memory" pages are the worst
case. PDF 104's environmental test shows that a ST with three adds between
costs nothing extra.

What the model now does:

- `StretchCore.bsv` gates the loading of an FP level that stores, or
  fetches an internal register, on `laarHeldByLevel`, `laarFreeAt` and
  `st.storesPending()`.
- `laarRetire` sets the release: E-box time, plus the I-Checker's 0.6 µs
  (`laarCheckClocks`, printed p.3-19).
- For ST, SRD, SLO and SRT it adds `laarStorePost`. That is a fit on PDF
  48 alone, one number per destination: memory 9, index 17, $R 5. It was
  held out on PDF 49-51 and lands within 1 clock (EXTERNAL) and 3 (I-BOX).
- `xstoreFreeAt` extends `storeWait` to the same instant for a store into
  index storage, in every class.
- A wait for the E-box before a look-ahead fetch of words 7-15 was tried
  and not kept: it is weakly sourced and gained about a clock. The PAST T
  MOVE failure once blamed on it came from the shared `/tmp` tape file
  that concurrent MCP runs overwrite. With a private `STRETCH_TAPE` the
  same tree passes.

The VFL and connective levels do not take the LAAR. Their E-box charges
are fits to back-to-back pages that already contain the queuing, and
gating them as well put VFL ST (PDF 124) at +11.93 clocks. M+ and M+MG
get the documented events only, because PDF 69 prints M+ below ST --
except, since 2026-11-17, into index storage: "A store into index storage
is a time-consuming operation" (printed p.3-21) is said of the
destination, so every FP store into words 16-31 takes the index
remainder (17). PDF 69's I-BOX unindexed column went from median −18.18
to −1.18 (mean −0.48; M+MG, PDF 70, held out: median −1.18, mean −0.60);
the indexed column from −22.22 to −5.22.
`docs/atlas_oracle.md` "Closing the residuals", item 2, has the tables.

### An indexed FP I-box operand (2026-11-17)

An FP fetch from index storage (words 16-31) with an index now costs 2
more preparation clocks (`fpIndexedIboxClocks`). The index register and
the operand are two reads of index storage in turn, at 0.6 µs each
(printed p.3-18). The I-BOX indexed columns of PDF 42, 64, 65, 73 and 95
went from −2.02 to −0.02.

### The preparation floor (2026-11-17)

A decode of N clocks cost the model N + 2 in a homogeneous run: a VFL
decode of 3.6 µs (12 clocks, Vol. 1 printed p.3-18) took 14, and the
immediate compares of PDF 177-182, which print 12, sat at +2. Two clocks,
two causes, both in `StretchCore.bsv`:

- `ibusy` counted down only in `rl_prepare`'s own arm. The decision arms
  are mutually exclusive, so the clock in which `rl_au_remove` removed
  the level (or `rl_exec_resume` finished a level's read, or
  `rl_idx_write` wrote a progressive level's index) stopped the I-box's
  clock as well. Now `ib` counts it down in those arms too, as `eb`
  counts `ebusy` down in every arm. Not in `rl_io`, `rl_xmit` or
  `rl_tail_write`: a transfer or a transmit is the instruction still in
  progress, and T is already short.
- The level-load clock came on top of the decode. `rl_prepare` now loads
  `2 * iboxCycles - 1`: the load clock is the first clock of the decode.
  Only the E-box-class load; the I-box dispatch path (`budgetClocks`,
  PDF 109) is unchanged and unmoved.

With both clocks given back, the FP I-BOX columns (6.0 clocks printed
for L and + from $X9, where the FP decode rate is 1.2 µs = 4) were 1
short: the model had matched them as 4 + the two lost clocks. The
remainder is the I-Checker's "I-box data error check" (printed p.3-19,
0.6 µs): `fpIboxCheckClocks` adds 2 for an FP operand in index storage.

`decks/prep_floor.strap` pins it (sixteen KI, eight L from $X9).
`docs/atlas_oracle.md` "Closing the residuals" item 7 has the tables.

### An FP look-ahead fetch yields to the instruction fetch; an indexed immediate (2026-11-17)

Two I-box supply timings, `docs/atlas_oracle.md` "Closing the
residuals" item 13, pinned by `decks/ibox_supply.strap`:

- **Bus order, FP levels.** StretchStorage's `memCtl` offers the
  look-ahead levels' operand fetches to the memory bus before the 1Y/2Y
  instruction fetches (Buchholz §14.3). For floating point the CE
  manual's logic says the reverse: R23-9732 Figure 3.1.21 (PDF 85,
  printed 1-43/1-44) turns the FP look-ahead load FPL2E on only under
  "NOT IC FETCH PRIORITY", and Blosk (TR00.722 printed p.30, PDF 32)
  describes the same cycle of his FP preparation ("Since IC controls have
  priority, the IC fetch is made ..."). `laReq` now carries whether the
  level is FP, and an FP level's fetch is held (`fpYields`) while a 1Y/2Y
  fetch waits for a unit that can take it. VFL and connective levels keep
  Buchholz's order: no VFL source was read, and a global reorder moved
  twenty VFL pins and broke `decks/int_timing_bracket.strap`
  (`docs/NEXT.md`). FP L EXTERNAL (Vol. 2 PDF 64) went from +1.33 to
  +0.46 clocks, DL (PDF 66) from +1.10 to D+0.46.
- **Indexed immediate.** An immediate VFL operand skips the word-boundary
  test (R23-9732 Figure 3.1.23, PDF 87: "IMM-bar . VFL"), so its indexing
  costs 1 clock, not iboxCycles' 2: `vflImmIndexedSaving`. PDF 177-182
  print 12 unindexed and 13 indexed at the floor. The one clock is the
  pages' difference (RECONSTRUCTION). KI's indexed column went from
  +0.95 to −0.05 (median).

What is left on FP L EXTERNAL (+0.46) is instruction supply: the body sits
in the same four interleaved units as the operands (the oracle's CHOSEN
body address), and the model returns a word 8 clocks after the bus takes
the request where Buchholz gives 1.6 µs. The 7030's own 4.43 and 4.67
clocks (L, DL) are not whole clocks, which no per-instruction charge
reproduces.

### An FP internal operand (2026-11-17)

Vol. 1 printed p.3-20: an internal operand (address 3 or 5-12) "is not
available during the decoding stage, and the mechanism for internal
operand fetch already exists for the handling of store instructions". The
model commits a level at removal and charges its E-box time after, so an
FP fetch of $R had its value at once and cost nothing; the $R columns of
PDF 73-101 were 4-7 clocks short. `headReady` (`intWait`) now holds an FP
head level with an internal operand until `fpInternalOperandClocks` after
the E-box finishes the level before it (`eboxDoneAt`): the I-Checker's
0.6 µs plus `laarStorePost`'s internal-register remainder, the store
path's number, fitted on PDF 79's ST $R column and reused here without
refitting. The fetch pages are its held-out test: F+ and E+ exact, + and
K within half a clock, L +1. FP only, as the LAAR. VFL INTERNL (+4 on the
7030) was not changed then; see the next section. `decks/fp_internal_operand.strap`;
`docs/atlas_oracle.md` "Closing the residuals" item 8.

### LFT to memory, $R behind the LAAR, indexed M+ after the hold (2026-11-17)

Three changes, sourced in `docs/atlas_oracle.md` "Closing the residuals"
item 10 and pinned by `decks/fp_to_memory_laar.strap`.

- **LFT takes the LAAR** (`StretchIBox.fpLaarStore`: word 14). This is
  timing only; its `storeAddr` stays Invalid. The sources:
  - Vol. 1 printed p.3-20 says $FT is "bona fide main memory".
  - Printed p.3-21 names LFT among the "floating-point-to-memory
    operations".
  - Vol. 2 printed 34D (PDF 41) lists the LFT pages as "to memory".

  It takes ST's memory remainder (9, not refitted). An LFT from memory or
  $X waits for the LAAR at the head (`lftWait`), not at its load
  (`lftDeferredLaar`). That choice is a RECONSTRUCTION: the pages print
  memory and $X9 a clock apart, so the fetch is hidden. It is in tension
  with p.3-21, which puts the wait at decoding.
- **An FP internal operand's fetch waits for the LAAR as well as the
  E-box** (`StretchCore.intFrom`). The address needs the one LAAR
  (p.3-20, p.3-21). In homogeneous runs this moves only LFT and M+ from
  $R. After any FP store it delays a following $R fetch, which no atlas
  page measures.
- **An indexed FP operand in index storage, prepared out of the
  index-store decode hold, spends its index read and its I-Checker pass
  (2 + 2) before the load** (`fpHoldSerialClocks`, `xholdPc`,
  `serialPaid`). This is a RECONSTRUCTION fitted to the one difference
  the pages print: M+ prints 4 clocks more indexed than unindexed.

Atlas medians, before → after:

| Column | Before | After |
|---|---|---|
| LFT $R (PDF 99) | −11.53 | −0.53 |
| LFT EXTERNAL | −8.80 / −5.22 | +0.47 |
| LFT I-BOX | −7.52 | +1.47 |
| M+ I-BOX indexed (PDF 69; 70, 100, 101 held out) | −5.22 | −1.22 |
| M+ $R | −5.06 | −3.07 |

The control columns did not move: ST, L, +, M+ unindexed and M+
EXTERNAL.

### A VFL internal operand (2026-11-17)

The same sentence of p.3-20 is not limited to floating point, and the
atlas's VFL INTERNL columns (operand at 8.0, $L; PDF 143-169) print 4
clocks over EXTERNL where the model printed the same figure. `intWait`
now also holds a VFL or connective head level whose operand is address 3
or 5-12 (StretchIBox `vflInternalFetch`) until `vflInternalOperandClocks`
(4) after `eboxDoneAt`. The 4 is a FIT on PDF 147 (L) INTERNL alone; the
FP figure (7) is not reused because its remainder is the FP store path,
which the VFL E-box fits already contain. No LAAR gate is added for VFL
(the queuing is inside those fits). `decks/vfl_internal_operand.strap`;
`docs/atlas_oracle.md` "Closing the residuals" item 11.

### After a VFL store into index storage, the next decode waits (2026-11-17)

"A store into index storage is a time-consuming operation. Whenever such
an instruction is decoded, ... the I-box does no further decoding until
the new index contents arrives" (printed p.3-21). The model charges a
decode as `ibusy` after the level it gates is loaded, so the next
instruction's decode had run out long before the hold ended, and a VFL ST
into $X0-$X3 was 12.3 clocks under PDF 124's I-BOX column (14.3 indexed).
`laarRetire` now sets `redecodeAfterHold` for a VFL or connective store
into index storage, and `rl_prepare` charges the prepared instruction's
own decode (`2 * iboxCycles - 1`, as at a load) when the hold ends. No
fitted number: the decode is `iboxCycles`', and its indexed +1 cycle gives
the page's indexed +2 clocks. NOT for FP: the FP index-store remainder
(`laarStorePost`, 17) is a fit on PDF 48 that already contains what
follows the hold. The charge is made only for an E-box-class successor:
an I-box instruction's budget already serializes its own decode from
dispatch, so charging it here would count it twice.
`decks/vfl_index_store_decode.strap`; `docs/atlas_oracle.md` "Closing the
residuals" item 12.

### An interruption is due: start nothing new (2026-11-18)

Ref. Manual p.48: interruption comes "before execution of the next
instruction". `rl_interrupt` waits for the look-ahead to drain, and
`rl_prepare` used to go on starting instructions meanwhile. An I-box
instruction started that way was committed, because the model has no
index-recovery unwind. The VFL internal-operand wait exposed this. C22-6578
Problem 2.12's `CM1111(BU,1), $SB+0.7` was held four clocks, so `LX, $2,
19.0` ran before the $VF interruption its LWF had raised, and 16 of the
hundred transposed words came out wrong. `rl_prepare` now starts nothing
while `intDue` is valid and no interruption instruction is in flight.
Levels already loaded still execute. An I-box instruction that had already
run ahead of a pending level is still not unwound (the armInterrupt note).

### Store close to fetch, for an instruction word (2026-11-17)

Perf. Char. Vol. 1 printed p.3-21: a store into "a location corresponding
to a prefetched instruction" -- "When such a store is decoded, I-box
invalidates the prefetched instructions and waits until the correct
information is available." The model invalidated a Y word only when the
store was MADE (mkInstrBuffers' program store compare), at the storing
level's removal; an instruction prepared out of 1Y/2Y before that ran as
assembled. `rl_prepare` now does not prepare an instruction whose word
(either word of a full-word one) a pending level stores (`levelStores`),
nor in the clock `st.recentStore()` reports a store to it (the level has
retired but the Y word is not yet dropped). CHOSEN: the model waits at
the stored instruction, the 7030 at the store's decoding.

The bug was latent: the base model (`2cee08a`) fails
`decks/store_into_prepared_instr.strap` case 1. The suite exposed it when
the preparation floor was fixed and the I-box ran further ahead: the 7030
TABMAN (call 24 ADDORD 3 11: TBEN2's "ST(BU,6),TBEN4+.35" sets TBEN4's own
length) and C22-6578 Problem 2.9 ("ST(BU,4),SV+0.19" into the next
instruction) both ran the unmodified instruction.

### Index storage, for the decode hold (2026-11-17)

The index-store decode hold (StretchCore `laarRetire`, `xstoreFreeAt`;
"the I-box does no further decoding until the new index contents
arrives", printed p.3-21) tested STORE WAIT's word set (11, 12, 16-31).
Printed p.3-20 says which words are index storage: "$IT, $TC and $0
through $15 are in index storage", while "an internal operand address
is ... address 3, or an address between 5 and 12 inclusive". The hold now
tests `indexStorageWord` (1, 2, 16-31); STORE WAIT's `storeWaitWord`
(Fig. 3.1.24) is unchanged. Words 1 and 2 moved no pin; no deck is known
to exercise them (untested). decks/vfl_cross_special_words.strap: 404 ->
372 (389 from this alone, the rest the preparation floor).

### Immediate compares (2026-11-17)

`eboxClocks` now charges the six immediate compares (KI ... KFEI)
10 + 2(b − 24/y). That is K's law without the bytes of the 24-bit
immediate field, which is already in the level, and without the full-word
allowance. The law is read off PDF 177-182, and the mean residual went
from +7 to +3. The inverted-sign blocks (12/14 clocks at any length) are
not modelled, because `eboxClocks` sees no data. `docs/atlas_oracle.md`
"Closing the residuals", item 4.

### SHF's shift amount (2026-11-17)

`eboxClocks` charges SHF Table 2's 4 cycles plus 1 for each further shift
of 4, plus 1 for execution: 5 + n/4 for an amount n. It used to charge
the add class's flat 5. PDF 72 is now exact at shifts of 1, 3, 6, 9 and
95, and +0.5 at 12, where the page prints 8.5. An indexed amount is not
seen (`eboxClocks` gets the decoded instruction).

### Documented simplifications (deliberate, not oversights)

- ~~**Sign-magnitude sign-bit position within a byte**~~ **FIXED
  2026-11-09.** This used the byte's top bit, which above byte size four
  is a zone bit. R23-9694 printed p.100's table puts S at bit
  min(byteSize,4)-1 of a field. The same change made binary `ST` store the
  register's flags and zones and set MOP, PF and the result indicators by the
  data field stored (printed p.63); made `L` clear the flag positions and
  built `LWF` (printed p.57); made the operand-reading arms set TF, UF and VF
  (printed p.59) and `M+` keep the operand's flags and zones (printed p.58)
  and set MOP. `decks/vfl_sign_byte.strap` is the test. The `*+`, `/` and KF
  arms get the flags by p.59's general sentence, with no case of their own.
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
  CBRZ+/CBRZ−/CBRZH groups (`decks/ibox1_p43_p51_span.strap`)
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
- ~~**Location 8 as a floating-point address is an ordinary word.**~~
  **FIXED 2026-11-16.** Reference Manual printed p.80: "in
  floating-point instructions when address 8 is used as the effective
  operand address, accumulator bit positions 0-59 and sign byte register
  bit positions 4-7 are used as the operand. ... Bits 60-63 of the
  accumulator do not serve as operand bits. For all floating-point
  single-precision operations, they remain unchanged. ... This rule
  applies to operations of both fetch and store type." The fetch is
  `fpLoc8Operand` (the word still makes its storage round trip, so no
  timing moved). The store is `fpStoreToLoc8`, a rewrite of the
  `FpCommit` record into `accLeft`/`accSign` fields, so each register
  still takes one write. A store to 8 therefore sets `$SB` bits 4-7.
  Reproducers: `decks/problem_3_fp_address_8_sign.strap`,
  `repro_fp_operand_location8.strap` and `repro_fp_store_location8.strap`.
  The witnesses are C22-6578 Problems 3.8 and 4.10. VFL operations on 8
  are untouched: p.80, "In operations other than floating point, the
  contents of the left half of the accumulator, bit positions 0-63,
  participate".
- ~~**Word 11 (Indicators): the general STORE path does not write
  it.**~~ **LIFTED 2026-11-16.** Reference Manual printed p.37: bits
  0-19 "can be read, but not loaded. Any attempt to store into these
  positions has no effect. Bit positions 20-63 may either be read or
  loaded", and a store's result in 20-63 is what it would be on an
  ordinary word holding the indicators at the start of the
  instruction -- "The setting of any of the indicators 20-63 that
  would normally occur as part of the store operation is overridden by
  this result." `st.writeWord(11)` now sets a wire (`indStW`) that
  `commitIndicators` merges over the instruction's own
  `setIndicatorBits` value in model bits 43:0, before TS and the I/O
  report are OR-ed into 0-19. Every store path that ends in
  `writeWord` reaches it: the VFL `ST` (C22-6578 Problem 3.9's
  `ST(BU, 3), $AL`, `decks/problem_3_vfl_store_to_indicators.strap`),
  the `CM` connective (MCP printed p.356 line 33,
  `CM1111(BU,1),$IND.63`, `decks/repro_cm_indicator_bit.strap`), FP
  stores. Since 2026-11-17 a VFL field crossing into a word below 32
  is built too: its second word goes through `writeWord` one clock
  later (`StretchCore`'s `rl_tail_write`; see the crossing-field `ST`
  entry below). `decks/vfl_cross_special_words.strap` crosses into and
  out of word 11 (C1-C3, 2026-11-17).

  The four index half-word stores -- `SV`, `SC`, `SR` and `SVA` --
  and `BB` and `Z` keep their older shape: they FOLD the store into
  the `ind` value the instruction writes, via
  `isIndicatorHW`/`foldIndicatorHW` in `StretchExecute.bsv`, and never
  call `writeWord(11)`. Their order differs from p.37 in one case,
  noted below (the index result indicators are applied AFTER the
  fold); nothing measured discriminates it.

  Driven out by ja_ax1a p.25's IBIN35 block
  (`decks/ibox1_bind_ind.strap`), which sets XL by hand --
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
- ~~**Transmit moves one word**, not `count` words.~~ **FIXED
  2026-10-18** (any count, immediate or direct) **and 2026-10-22**
  (backward). Left struck through rather than deleted: this list is
  the record of what the model does not do, and a limit that silently
  disappears is indistinguishable from one nobody rechecked. `SWAP`
  is the remaining Transmit limit.
- ~~**A crossing-field VFL store under progressive indexing suppresses
  the increment too, not just the store.**~~ **LIFTED FOR `ST`,
  2026-10-24, AND MCP IS WHAT LIFTED IT.** `ST` now splits a crossing
  field across two words: `StretchStorage.writeWordTail` parks the
  second word for one clock and `StretchCore`'s `busyXfer` holds off
  arming while it waits, so the progressive advance happens as p.21
  says it should. Printed p.43 line 49 of MCP's Hollerith-to-BCD
  converter is `ST(V+I)(BU,6,6),.6($5)`, and sixty-four is not a
  multiple of six: with the store refused, IBM's own card reader
  produced TEN characters out of eighty — the advance was skipped, so
  the output pointer stuck at bit 60 and every later character was
  refused at the same place — `IOD` arrived as `I`, and MCP rejected
  its own configuration card. `decks/vfl_crossing_store.strap` pins
  the semantics (twelve checks, every expectation derived before the
  arm existed) and `tests/gen_mcp_boot_tb.py`'s `mcp_ucbf1_*` pin the
  effect on MCP itself.
  **WHAT WAS STILL REFUSED until 2026-11-17**, each for a stated reason:
  `M+` kept the old guard (nothing measured needed it). The `CM`
  connective crosses since 2026-11-06, the same way and for the same
  kind of reason: MCP printed p.78 line 42, `SF(BU,40,8),TREELX`, is a
  forty-bit CONNECT TO MEMORY at bit 40, refused it left OP set, and
  MCP's body reported an OP interrupt
  (`decks/cm_crossing_field.strap`). The other three were refused
  until 2026-11-17: a crossing field whose SECOND word is below 32 --
  the machine's registers -- because the tail drained to the
  core-storage queue and did not run `writeWord`'s special-address
  dispatch; a crossing `M+`/`M+1`/`M+MG`; and a crossing field that ALSO
  needs a progressive refill, which wanted three reads of a two-slot
  prefetch. **All three are built** (`docs/NEXT.md` "GROUP B BUILT"):
  `ExecDone.tailWrite` and the off-pipe rule `rl_tail_write` (through
  `writeWord`, inside `busyXfer`, so the index part's write comes after
  it, p.22's order), the `M+` arm's `mCross`, and a three-word
  `prefetch` (`NPrefetch`). Oracle `decks/vfl_cross_tomemory.strap`.
  **ONE STORE PATH FOR M+ AND CM, 2026-11-17**: `vflFieldStore`
  (StretchExecute.bsv) writes one word or two and makes p.32's DS test on
  every word the field touches.  CONNECT TO MEMORY's two ONE-WORD stores
  (`writeFieldWithHi`, now deleted) had made none: a CM into a protected
  word was stored and DS stayed off.  On DS, M+ and CM now set neither
  their result indicators nor CM's counts (p.32, "the operation is always
  terminated"), as ST's arm already did; and ST, M+ and CM no longer run
  their progressive index part on DS (printed p.22: an exception in the
  variable field length portion suppresses "the entire operation").  CM's refill path now sets the counts (p.76;
  `cmFinish`, shared with the main path).  Oracles
  `decks/vfl_cross_protect.strap`, `decks/vfl_cross_special_words.strap`.
  **And since 2026-11-17 the refill raises DF only when it happens**:
  the four inline refill shapes (ST one word and crossing, M+, CM) raise
  p.32's class-3 DF beside the index hand-back, under the store's !DS
  guard, not up front (`refillDfNote`; printed p.32, "If an address which
  is associated with an operation is not actually used, it will not be
  monitored"); `decks/vfl_refill_df.strap`.  The refill WORD is still
  read before the store's DS is known (the prefetch order), so its clocks
  are still spent: open, docs/NEXT.md.
  The second word's time is CHOSEN (one read, one tail clock), not the
  atlas's WB XOVR column (about 30 clocks more; NEXT.md). The paragraph
  below is kept for its reasoning about the refusals that remain.
  This falls directly out of
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
  `../decks/figure7_progressive_indexing.strap`'s padding
  comment for the concrete walkthrough.
- **Address-space window**: `MemWords` (StretchStorage.bsv) is now
  the full 262,144-word address space the 18-bit `WordAddr` type
  models (raised from 256 once storage was BRAM-backed — see
  "Toolchain" item 8 for the history and cost). What's still not
  modeled is the *installed-core* limit a real installation had
  (smaller than the address space): addressing beyond it would trip
  AD, Address Invalid, on real hardware; here every address is backed.
  (Since superseded: `StretchMemory.bsv` now has an `InstalledWords`
  bound of 98,304 words, and reads past it return zero while writes are
  dropped. AD itself is still not raised there, but that address class
  is now named in the model, and storage protection's `protViolates`
  exempts it -- p.32: "An address which actuates indicator AD, address
  invalid, is not compared with the contents of the boundary registers
  and cannot actuate any of the address alarm indicators.")

### Not modeled at all

Interrupts (SINCE SUPERSEDED: the interruption mechanism itself is
implemented -- `StretchStorage`'s `intDueCalc` decides whether one is
due and where it goes, `StretchCore`'s `rl_interrupt` takes it.
SUPERSEDED AGAIN, 2026-09-25: the *timing* was wrong and is now
measured. This paragraph used to say the interruption is taken at a
QUIESCENT boundary rather than p.48's INSTRUCTION boundary, "LATER,
never earlier". How much later was never measured; it is now.
`decks/int_timing_bracket.strap` is a VFL `ST` whose store is
suppressed, bracketed `BE` / `ST` / `BD` the way `jb_ax5b` routine 1260
brackets every provoked interruption. It needed THREE instructions of
slack before the `BD` for the interruption to be taken at all -- p.48
allows zero and the deck leaves one -- and with fewer the `BD` disabled
the system first and the pending interruption evaporated, because
`intDueCalc` returns Invalid the moment `irqEn` goes false. **The cause
was one term**: `armInterrupt` waited for `ebusy == 0`, which is the
CHARGED TIME of the instruction just removed from a look-ahead level,
not a structural busy -- and `rl_prepare` does not wait for it, so
every I-box instruction that fitted inside the budget ran first. The
term is gone; `la.count() == 0 && !ebox.busy()` is the structural
condition and stays. `interruptDue()`'s own one clock of latching delay
is NOT the cause and was measured not to be: with `ebusy` dropped the
bracket program passes with the latch in place, so `StretchStorage` is
untouched. Still not modelled: an I-box-class instruction the I-box has
already run AHEAD of a pending level is committed and cannot be taken
back, so an indicator set by a level is still not reported before an
I-box instruction that overtook it -- `iboxHazard` keeps that narrow
(every unconditional branch, every branch on a non-index indicator and
every store to an E-box register drains the levels first) but does not
close it, and closing it needs the look-ahead to be able to unwind.
Also not modeled: an interruption instruction that is E-box class,
which fails loud rather than silently stepping the counter),
memory protection enforcement (addresses described as
"permanently protected" are documented but not enforced against
writes from user code beyond a few no-op cases -- SINCE SUPERSEDED:
address monitoring is now enforced for STORE-type references, both the
permanently protected words 1-3 and the area named by the boundary
registers in word 3, gated on the interrupt-system enable bit, and for
FETCH-type references in p.32's class 1 -- "the effective address of
all fetch-type operations with a direct address" -- which turns DF on;
p.32's classes 1 and 3 for DF are complete -- every fetch-type
operation with a direct address, and all eleven refill reads -- and
class 2 (LOAD VALUE EFFECTIVE) is moot since LVE decodes Operation Code
Invalid here.  IF entirely, the
MASK-DEPENDENT half of DF and DS, and the straddling rule are still
not modeled, see `StretchExecute.bsv`'s `protViolates` and `dfSignal`), the interval
timer/clock actually ticking (SINCE SUPERSEDED: both counters in word 1
now step. One oscillator at 1,024 pulses per second — Ref. Manual
printed p.34, and p.35 for "the same 1024 cycle per second oscillator"
— divides the 0.3 µs model clock by the exact rational 78125/24
(`StretchTiming.bsv`'s `oscPulseNumer`/`oscPulseDenom`, Bresenham, so
24 ticks are exactly 78125 clocks and the long-run rate does not
drift); each pulse steps the interval timer down one modulo 2¹⁹,
clears the unused bits 19-27, steps the time clock up one modulo 2³⁶,
and turns TS on when the timer goes *from one to zero*
(`StretchStorage.bsv`'s `oscillatorStep`). A store into word 1 can no
longer reach the clock half — p.35, "any attempt to store into the
right half of location 1 is suppressed" — though the AD indicator that
attempt should raise is still not modelled, and neither is p.34's
"cannot be read if indicator DF is masked on". `indicators` and
`intervalTimerAndClock` each gained a single committing rule fed by a
wire, since the oscillator writes both independently of whatever
instruction is executing. Checked by
`decks/interval_timer_steps.strap`.), and — the machine's defining engineering
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
enough of them to run RD/W/CCW/REL/CTL against four fixed devices
(the tape supports two of its real CTL function codes; the disk is
not on the Exchange at all and has its own arc-addressed LOCATE) with
no real device timing -- **and for the disk, "no timing" is a bigger
departure than it is for the others**: printed pp.161-162 give a
three-point seek model, a rotational distribution and 8 µs per word,
all of which a functionally-correct program cannot see but a
cycle-accurate one must have (docs/disk_subsystem.md §4). I/O status
IS now promoted to the indicator register and the channel address
register (Reference Manual printed p.118; rule rl_io_report,
decks/io_status_report.strap), with two documented gaps: an
instruction addressed to a channel whose report is still waiting is
not rejected with CBJ, and the scanner is not reset to the
last-addressed channel -- it simply walks 0, 32, 33, 34, 35 in
ascending order. The host builds (-D HOST_TAPE) carry a full 353,
2^21 words (StretchDiskSourceFile.bsv); every other build keeps the
two-arc source.

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
   **BOTH OF THOSE LAST TWO ARE NOW FALSE, and they were lifted the
   same way, which is the point worth keeping.** Transmit moves
   `count` words in `StretchCore`'s own `rl_xmit` rule; `ST` splits a
   crossing field via `StretchStorage.writeWordTail`, which writes a
   REGISTER where `writeWord` writes a WIRE, so the two can be called
   in one `execute()` and the second word reaches the store queue a
   clock later. The constraint was never a machine restriction — MCP
   printed p.43 line 49 depends on the crossing store and printed p.4
   line 28 on the multi-word transmit — so what the constraint
   actually forced was a STAGING DISCIPLINE, not a reduced
   instruction set. `M+` and the `CM` connective still carry the old
   refusal; see the scope list above for the three cases that remain.
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
   256: `decks/ibox1_wen_ven_original_addresses.strap`
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
   into a `.o` that every later link reuses untouched.
   (**Re-measured 2026-09-21**, with the three phases separated in an
   isolated tree: `bsc -g` -- elaborate, schedule, generate C++ --
   **119s CPU**, confirming the ~121s above independently; `bsc -e` --
   compile the generated core C++ and link -- **24s**; and the Bluesim
   executable itself **0.31s**. So elaboration is ~87% of a cold build,
   the C++ compile ~12%, and running the simulation is free. The core
   `.cxx` has grown from the 5.9 MB recorded above to **8.8 MB**, which
   is why that once-per-tree link is now 24s rather than ~10s. This is
   also the whole cost model of `tests/mutation_score.py`: every mutant
   edits the model, so every mutant pays a full core re-elaboration
   before its first test runs -- a ~2.5 minute floor.
   **CORRECTION**: this said "which is why 32 mutants cost ninety
   minutes"; that was the floor multiplied out, written as though it
   were measured, and it is wrong by 2.4x. Summing a real serial run
   gives 220 minutes of mutants plus a 13 minute baseline, near four
   hours -- most mutants are caught well past the floor, and any that
   runs the whole suite takes 13-16 minutes. `--jobs 12` brings that to
   **53 minutes wall for 183 minutes of CPU**; the remaining floor is
   the serial baseline plus the slowest single survivor, 25.6 min,
   since a survivor is by definition the mutant that runs the whole
   suite.) Time one link on
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
3. ~~Multi-word Transmit and crossing-field VFL stores, properly, as
   multi-cycle operations~~ **BOTH DONE** — Transmit 2026-10-18
   (`rl_xmit`), the `ST` crossing store 2026-10-24
   (`StretchStorage.writeWordTail`). The guess recorded here was
   right about the shape and wrong about the difficulty: it said
   `pendingIdxWrite` was "a template for this, not a ready-made
   solution: crossing-field stores need to split across a word
   boundary, not just defer a single write". Splitting across a word
   boundary turned out to be the easy half — `insertFieldBitsPair` in
   StretchVFL.bsv, twelve lines, the write-side mirror of
   `extractFieldBits`. Deferring the single write was the hard half,
   and the answer was not to touch `StretchCore`'s FSM at all: a
   method that writes a register instead of a wire is a second write
   port, and one clock of `busyXfer` is the whole stall. `M+` and
   `CM` are what is left.
4. Open question, not yet resolved either way: does a branch
   instruction immediately following a progressive-indexing
   instruction (e.g. `BZXCZ` right after `ST(V+ICR)`, as in
   `decks/figure7_progressive_indexing.strap`) read the
   index register's pre-refill or post-refill state on real 7030
   hardware? With this model's two-cycle `pendingIdxWrite` design, the
   index write (including any refill) completes on its own `step()`
   *before* the next instruction fetches, so a following branch always
   sees post-refill state here. Whether that matches the real
   machine's timing (which the manual describes only as "executed in
   two parts," not with cycle-by-cycle interleaving semantics) is
   unverified. Not exercised by any test yet — `figure7_progressive_
   indexing.strap`'s own `BZXCZ` exits the loop on the same cycle a
   refill would occur, and `decks/xw_refill.strap` (see
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
   single block against a device's one fixed image); CBJ for an
   instruction to a channel whose status report is still waiting
   (printed p.118 -- the report itself is now made, see the paragraph
   on the Exchange above); and, if real device content larger than `DeviceWords` (32)
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
