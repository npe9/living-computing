# 1:1 with the block diagram and the cycle tables

The owner's requirement (2026-11-19): the model must be **1:1 with what is
documented** — Figure 1-1's blocks at their printed sizes, and Tables
4-32…4-36's cycles, not an approximation of either. This document states,
block by block and table by table, what is printed, what the model has,
and what is missing. It is updated whenever a block or a table row
changes.

## 1. Figure 1-1 (printed p. 1-2), block by block

| printed block | printed size | module | size in the model | status |
|---|---|---|---|---|
| Prefetch buffer cache | 1024 × 3 bytes | `mkHobbitPrefetch` (`HobbitDecode.bsv:374-465`) | 128 lines × 64 bit × 3 ways = 1,024 B per way, tagged, set = `addr[9:3]` | **1:1** |
| Prefetch/decode unit | 3-stage pipeline | `mkHobbitPduS1`, `S2`, `S3` | three stages, Flute-shaped (`enq/deq/out/notEmpty`) | **1:1** |
| Decoded instruction cache | 32 × 192 | `mkHobbitDecodeStore` (`HobbitTypes.bsv:788-…`) | 32 entries of 192 bits | **1:1** |
| Stack cache | 64 × 32 × 2 | `mkHobbitStackCache` | 64 words of 32 bits, two ports (flush + EU) | **1:1** |
| Execution unit | 3-stage | `mkHobbitEuS1`, `S2`, `S3` | three stages; multi-cycle boxes for ENTER/CATCH flushes | **1:1** |
| MMU: page TLB | 2 × 32 entries | `mkHobbitMmu` | two 32-entry TLBs (text, data), 2 NPSRs | **1:1** |
| MMU: segment NPSR | 2 × 1 | `mkHobbitMmu` | two 34-bit NPSRs | **1:1** |
| Interrupts / event processing | printed order, p. 1-40 | `mkHobbitEvents` | priority order, frames, vectors | **1:1** |
| Bus interface | Appendix A | `mkHobbitBusMaster`/`mkHobbitBusMem` | pins and protocol, block transfers | **1:1** |
| Timers | p. 1-19 | `mkHobbitTimers` | two 32-bit counters, CONFIG fields | **1:1** |
| ROM/RAM, boot | — | `mkHobbitMem` (1 KB), testbench 64 KB | **not 1:1**: the model's memory is a testbench window, and the 1e kernel's map (`0x80004000`, I/O windows) is not laid out | open |
| Console DUART | `io.h`, `deveia.c` | parked WIP (`/tmp/duart-wip/`) | 26/37 checks | open (A4) |

Where a size is claimed, it is the declared array's shape, not prose:
the prefetch is three `RegFile#(Bit#(7), PfcLine)` ways (`HobbitDecode.bsv:521-523`, 128 lines each),
the stack cache is a 64-word store behind two read ports
(`HobbitStackCache.bsv`), the decoded store is 32 entries of 192 bits
(`HobbitTypes.bsv`), the MMU two 32-entry TLB arrays (`HobbitMmu.bsv`).
`tools/area_netlist.py` attributes synthesized area per block after the
ULX3S flow, which shows the blocks survive synthesis as their own
units; it does not measure array dimensions, and this document does not
claim it does.

## 2. The cycle tables

| table (printed page) | model | status |
|---|---|---|
| 4-32 Simple (p. 4-3) | `sem/` cycle rows + core | rows asserted by `smoke` and goldens |
| 4-33 Multi-cycle arithmetic (p. 4-4) | `sem/` (`MUL` takes the printed maximum, a named choice) | rows present; `MUL` min/max is data dependent and unnamed in the model |
| 4-34 DQM (p. 4-4) | `sem/` (`8·S` refused, `S` undefined) | rows present; core has no DQM |
| 4-35 Conditional jumps (p. 4-5) | folded 0, unfolded 1, mispredict 3/2/1 | **1:1** for the folded and compare-adjacent cases |
| 4-36 Miscellaneous (p. 4-5) | CATCH 1, CRET 15, KCALL 11, KRET 12, unimplemented 8 | present in `sem/`; CRET/KCALL/KRET not in the core |
| 4-6…4-9 delays (pp. 4-5…4-7) | **not charged**: the model adopts the p. 4-1 assumption "instruction fetches must access the instruction cache" | **not 1:1** while a fetch can miss |

Named choices, which the manual leaves open and which are therefore not
violations: A = 1, D = 2, Q = 4 (p. 4-2 prints no memory terms); the TLB
replacement policy (p. 2-1 prints none); the prefetch fill policy.

## 1a. The stack cache's window and memory

Printed p. 1-12: "If the stack cache is enabled and the current stack
pointer is the SP, then any address greater than, or equal to, the SP and
less than the MSP hits the stack cache" — so an access **outside** that
window is an ordinary memory access, and `MSP` itself may not exceed
`SP + 256` (the cache is 64 words).

The model does that.  An operand whose word is not in `[SP, MSP)` — an
absolute address, a pointer's target, a caller's word above `MSP` — is
fetched from memory before the instruction leaves EU_S1
(`bsv/HobbitCore.bsv`, "Memory operands"; `bsv/HobbitStackCache.bsv`,
`memReq`/`memLive`/`memData`).  Before this a miss returned zero, and
that zero is what sent 1st Edition `cat`'s `RETURN R8224` to address 0:
the caller's frame sits above `MSP` after `cat`'s own `ENTER R-8224`, and
the return PC read back as 0 instead of the word the matching `CALL`
wrote.

How it is built, because the first attempt was not this:

* **One read port, registered.**  The fetch goes through the stack-cache
  box's existing memory read (the `readReq`/`readData` pair the CATCH
  refill uses), one word per clock.  Program memory keeps a single read
  port, which is what a block RAM offers; the ULX3S build
  (`fpga/build.sh`) has **not** been re-run since this change, so the
  mapping, the LUT count and the 25.66 MHz figure in `plan.md` step 9
  predate EU_S1's operand latches (four since 2026-11-20) and are not re-measured.  An earlier attempt
  read memory combinationally (`mem.peek`) from every operand site; that
  needs one RAM read port per site, which neither bsc's `mkRegFileFull`
  nor a block RAM has, and it was withdrawn before it was committed.
* **The wait is the A term.**  A fetched word costs one clock (A = 1, the
  p. 4-2 choice).  It is not part of the HRI `cyc`: the p. 4-1
  assumptions put operands in the stack cache, and Table 4-38's operand
  delays are outside them.
* **A fetched word cannot go stale.**  Every architectural write passes
  through EU_S3; a word waiting in EU_S1's latches is refreshed from
  EU_S3's write to the same address, and the bypass network covers the
  writers still in flight when the word is used.
* **Fetches wait for the box.**  No operand is fetched while an ENTER
  flush or a parked write is still moving words into memory.

Evidence: golden `016` (three-way: hand trace, `sem/`, core) and the 1e
`cat` run (`bsv/run_p9.sh`).  `016`'s injection table says exactly what
that evidence reaches: the read itself, the pointed-to word and the
RETURN are pinned; the latch refresh and the wait-for-the-box gate are
*not* reached by any test yet and rest on the argument above.  `016` also corrected `ENTER`'s flush count
in the core: the printed loop is `while ((MSP > SHAD) && (MSP - target >
SCSIZE))` (p. 3-19), and the core had dropped the `MSP > SHAD` bound.

Not modelled: a data fault on such a fetch reports the last retired PC,
not the faulting instruction's (the MMU/event path is not exercised by
these tests); and the host side of a syscall shim writes user memory
behind the cache's back (see `docs/plan9_syscalls.md`).

## 1b. Byte order (2026-11-20)

Printed p. 1-3: "The numbering of bytes, within data words, is
selectable for the User and Kernel modes. The User mode is set via the
program status word (PSW) UL-bit ... The Kernel mode is set via the
configuration register (CONFIG) KL-bit."  Figures 1-2 and 1-3 (p. 1-4)
give the two numberings; "Text is always in big-endian order."

Both models were big-endian only until 1st Edition Plan 9 was run on the
reference model: 1e sets both bits (`machine.h:24,77`), and every
shipped program except `cat` goes wrong within a few hundred
instructions without them (`docs/plan9_boot_plan.md`, A2).

* `sem/hobbit_sem.py`: `_little_endian` / `_lane_shift`; the state has
  `config_kl` for CONFIG bit 16.
* `bsv/HobbitTypes.bsv`: `dataLittle(psw, kl)` and a `little` argument
  on `byteLane`, `storeMask`, `extendLoad`, `laneData`, `mergeStore`;
  the core has `configKlR` (CONFIG bit 16 only) and `setConfigKl`.
* Golden `017` pins the user-level rule three ways (hand trace,
  reference model, core) with four injected lane bugs recorded in
  `017.md`.  The kernel-level rule (CONFIG.KL) is pinned on the
  reference model only (`tests/test_p9run.py`); **on the core it is
  untested**.
* The fetch path takes no such flag in either model.

## 1c. What running 1st Edition Plan 9 on the core found (2026-11-20)

`bsv/run_p9host.sh` runs a shipped 1e binary on the core and compares
every retirement record with the same binary on the reference model
(`docs/plan9_boot_plan.md`, A2).  The comparison stopped eleven times on
the way to `za` and `zl` running; each stop was one of these.  "Found
at" is the first record that disagreed.

| # | what | found at | fixed in | pinned by |
|---|---|---|---|---|
| 1 | Little-endian data (PSW.UL, CONFIG.KL) | reference run: `echo` jumps to 0x361d0000 | `HobbitTypes.bsv` lane functions | golden 017 |
| 2 | No on-demand prefetch fill: a fetch outside the 1 Kbyte boot window was `TR_FETCH_MISS` | known beforehand (`docs/plan9_port.md`: `echo`'s `_main` 0x2ad0 and `main` 0x1020 are in different windows); with the fill disabled `echo` stops after 5 records | `mkHobbitPrefetch.demand`, `mkHobbitDecodeStore` (`missed`/`retry`) | the 1e runs (the goldens' 1 Kbyte memory cannot miss) |
| 3 | **A misprediction resolved in EU_S3 squashed EU_S1 only**; the wrong-path instruction already in EU_S2 retired | `echo` record 48 | `redirect` rule: `if (s3.squash) s2.flush` | golden 018 |
| 4 | Both operands indirect refused as "unimplemented" (the argument was a third cache port; none is needed) | `echo` record 274 (`CMPEQ *R24.UB, *R28.UB`) | decoder; EU_S1 `pt2Mem`/`pt2Word`; EU_S2 `readPointed2`; a fourth operand latch | golden 019 |
| 5 | `CALL *Roffset`, `JMP **$addr` refused (Table 1-23 modes 0xD, 0xC) | `echo` record 367 (`CALL *R12`) | decoder `branch3`; `flowIndirect` (the RETURN path) | golden 019 |
| 6 | `ENTER *$addr` / `ENTER *Roffset` refused; and the EU used the operand *field* as the target (p. 3-20 cases 3, 4: the target is fetched) | the kernel-entry stub's first execution | decoder; EU_S1 `enterMem` | golden 019 |
| 7 | `DQM` unmodelled | `za` record 55 (`DQM $0, *R4`) | decoder `dqm`; `OP_DQM2/4`; EU_S3's frame drain; EU_S1 holds until drained | golden 019 (constant source only; a memory source still traps) |
| 8 | The unimplemented sequence's `*(CSP) = PC` never reached the stack (only the event unit's private memory) | `za`'s FMOV: the handler read 0 at `*(SP)` | EU_S3 commit issues the store through the box; `mkHobbitEventsCore` no longer writes its private copy | the `za` run |
| 9 | Stack cache: a store to a word a CATCH refill had not reached was dropped; a store in the same clock as a refill word dropped the refill word; a second CATCH or an ENTER's flush replaced a refill in flight | `za` record 3,865 | `HobbitStackCache.bsv` (per-word next value; unfilled stores go to memory); EU_S1 holds after CATCH until the box is idle | the `za` run |
| 10 | Two rules each requested the memory's one read port; bsc let one *shadow* the other (warning G0117) | `za` record 21,638 (a parcel fetched as zero) | the box owns the port and lends it (`MemPort`, `sc.textPort`); the prefetch translates and asks | the `za` run |
| 11 | With events on, `latchOperand` and `move2to3` were in a rule cycle that bsc broke by making them conflict (warning G0009) | reading the build log | `start` clears the latches through a toggle | the build has no G0009 |

A twelfth and a thirteenth came from numbers the comparison does not
compare:

* **`cyc`.**  A folded unconditional `JMP` was prefetched down its
  fall-through, "mispredicted" every time, squashed and charged 3 where
  p. 4-3 gives a folded `JMP` 0 (`predictedTaken` did not list `JMP`).
  3,808 of `za`'s records.  Golden 020.
* **Reads outside the process's segments.**  `bsv/p9host.c` counts reads
  of addresses in no segment.  After the `JMP` fix the count on `za` went
  from 5 to 2,399, and the addresses were 0x4, 0x8, 0xc, ...: EU_S1 was
  fetching a memory operand through a pointer whose newest value was
  still unexecuted in EU_S2's input slot -- a table scan read `4*i`
  before the `ADD` of the table's base had run.  The right word was
  always fetched afterwards, so no value was wrong and no record
  differed; but it is a bus read the program never asked for, and a
  device register would see it.  `fetchOperand` now waits for that slot
  to empty; the count is back to 55 (observed on the same run: 2,399
  without the gate, 55 with).

  **The ones that remain are legitimate (traced 2026-11-23).**  Two
  findings, on `zc frexp.c` (then 1,376: 1,332 of address 0, 44 of
  0x80000000) and checked on `za` and `zl`:

  1. *The meter counted clocks, not reads.*  `mkP9HostMem`'s `fetch`
     rule reads its registered address on every clock (it must: the
     word may be written), and `p9h_read` counted each of those, so one
     request was counted again until the next request, and the five
     clocks before the first request -- the address register at its
     reset value, 0 -- were five "reads of address 0" on every run.
     The testbench now reports each *request* once (`p9h_request`).
     Same runs, same clocks, new counts: `echo`, `cat`, `hello` 0, `za`
     2, `zl` 9, `zc` 51 (was 1,376).  Removing the `!s2Taken` gate
     again makes `za` 1,174, so the alarm (100) still fires on the
     defect it was set for.
  2. *Every remaining request is an operand fetch by an instruction on
     the predicted path of a conditional jump that mispredicted.*  With
     `$display`s in `fetchOperand`, in the stack-cache box's port
     arbiter and in `redirect` (a local build, not committed), all 51 of
     `zc`'s requests came from EU_S1's operand fetch (none from the
     prefetch or the CATCH refill), at four instructions, each followed
     within two retirements by an EU_S3 squash:

     | pc (zc) | function | requests | instruction | why its operand is unmapped |
     |---|---|---|---|---|
     | 0x129e2 | `dotsearch` | 39 | `CMPEQ *R28, …` (`9fed 001c …`) | follows `CMPEQ $0,R28; JMPTN` (0x129de/0x129e0, `for(t1 = t; t1 != T; t1 = t1->down)`), predicted *not* taken; when `t1` is nil the jump is taken and the fall-through reads `*0` |
     | 0x12a72 | `dotsearch` | 10 | `CMPEQ $0, *R28` (`9ffe 0000 001c`) | the second such loop: `CMPEQ $0,R28; JMPTN` at 0x12a6e/0x12a70 |
     | 0x1960e | `strchr` | 1 | `CMPEQ *R4.B, R8.B` (`9f84 0004 0008`) | loop head after `ADD $1,R4; JMPFY` (predicted taken); the string's NUL is at 0x7fffffff, so the predicted next pass reads 0x80000000 |
     | 0x19832 | `strlen` (libc `strlen.s`) | 1 | `CMPEQ $0, *Rn.B` (`9ff8 …`) | the same: one past a NUL at 0x7fffffff |

     `za`'s 2 are the 0x80000000 case in the same two libc routines
     (`strchr` 0x78b6, `strlen` 0x7ada) and `zl`'s 9 the nil case
     (`zaddr` 0x4a86, `dodata` 0x6210), each likewise followed by a
     squash.  The value read through is right -- the pointer is the
     newest one, nil or one past the end -- it is the *path* that is
     wrong.  And on the reference model, which executes only the
     retiring path, the same programs make **no** reads outside their
     segments (`tools/p9archreads.py`: `zc` 0, `za` 0 and 0, `zl` 0;
     with the stack dropped from the legal set, as a control, `zc`
     80,636), so none of the core's 51 belongs to a retired instruction.
     `tests/run_p9host_tests.sh` checks that for `zc` on every run.

  The part does this too.  PRM §2.2 p. 2-3, *Read fault*: "This fault
  can be ignored if the read was requested because of a mispredicted
  branch" -- the chip issues data reads for instructions on a
  mispredicted path, and §1.10.1 p. 1-33 has the PDU issue instructions
  down the predicted path "into the pipeline without any
  discontinuity".  So these are modelled behaviour, not a defect, and no
  golden is added for them.  What the model does *not* do is the second
  half of that sentence: it has no read fault to suppress (addressing is
  physical in these runs and `p9host.c` serves any address).  The
  earlier guess here -- the refill engine reading one word past its
  bound -- was wrong for these runs: no refill request went outside a
  segment.

Two things are worth keeping from this beyond the fixes.

**Why the goldens did not find them.**  Every one of 3, 9 and 10 needs
state the 1 Kbyte, run-once, cache-full goldens never reach: a loop's
second pass (a warm decoded-instruction store), a cache that is being
refilled while the program runs, a fetch that misses while the data side
is busy.  The goldens pin what an instruction *does*; the long run pins
what instructions do to each other.

**What bsc said.**  Items 10 and 11 were in the compiler's warnings
before they were in a trace (G0117 "shadows the effects of", G0009
"created a conflict ... to break the following cycle"), and the two
testbench bugs made on the way were G0010s (an every-clock rule "treated
as more urgent" than the pipeline's).  A scheduling warning that names a
rule which fires every clock is a bug report.

**The reference model's side.**  The reference model treated the stack
cache as invisible, which is exact only for words a program wrote before
reading.  `za` copies a structure with a never-assigned member, off the
stack.  The reference model now keeps the cache's 64 words when
`State.cache` is set (ENTER's flush and CATCH's fill from the printed
loops, pp. 3-19, 3-10), and `tools/p9run.py` sets it.  For such
uninitialised reads the agreement between the models is by construction:
the slot index (address bits 7:2) and the zero a never-written slot reads
are the core's choices, adopted.  `tests/test_p9run.py`
`StackCacheContents` tests the model's flush, fill and window against the
printed loops; nothing independent says what the *real* part's slot
would have held.

**Injections (observed 2026-11-20).**  The golden-level ones are in
`018.md`, `019.md` and `020.md`.  Against the long runs, each bug put in
alone, the simulator rebuilt, and the file restored from a saved copy:

| injected bug | run | observed |
|---|---|---|
| a prefetch miss never requests a fill | `echo` | stops after 5 records, at the first `CALL` out of the boot window (clock limit) |
| the unimplemented sequence's store not applied to the stack | `za` | the first floating-point entry: `trap PC 0x00000000 at *(SP), the recording has 0x000026d0`; 139 records |
| the host does not do KRET's PSW and ISP | `echo` | record 1,808: the second KCALL's frame is at `0xce4`, 16 bytes low |
| the reference model without the cache's contents (`State.cache = None`) | `za` | record 29,664: `data` (`MOV *R4, *R8` copying a never-written stack word) |
| no hold after CATCH | `za`, `echo` | **every record still matched** |
| a store to a not-yet-refilled word not sent to memory | `za` | **every record still matched** |
| both of the last two together | `za` | record 22,545 (`pc`, `insn`, `data`), and the next system call's id is wrong |
| the prefetch treats a word as its own when the box did not grant the port | `za` | **every record still matched** |
| that, together with no hold after CATCH | `za` | record 21,638: a parcel fetched as zero -- the original symptom |
| the refill's word dropped when a store coincides (with no hold after CATCH) | `za` | **every record still matched** |
| three operand latches | `za`, `echo` | **every record still matched** |
| operand fetch not gated on the box being idle; a latch not refreshed by EU_S3's write; the arriving word not overridden by a same-clock write | `za`, `zl` | **every record still matched** (each alone) |

So, plainly: the hold after CATCH and the box's handling of a store
during a refill are *redundant for these runs* -- either one alone
passes, both removed fails -- and with the hold in place the box's path
and the port's "not granted" path are not reached.  Both are kept: the
hold also covers a second CATCH or an ENTER arriving during a refill,
which the box's fix does not.  Untested, and resting on argument: the
refill word surviving a coinciding store; the fourth operand latch; the
hold after DQM; and the three operand-latch mechanisms listed in
`tests/golden/016.md`.

**What the long runs do not compare: `cyc`.**  It is reported
(`tools/p9trace_cmp.py --cyc`).  After the folded-`JMP` fix (golden
020), `echo` agrees in `cyc` on all 1,808 records and the program `za`
and `zl` built on all 319; `za main9.s` on 125,110 of 125,572 and `zl`
on 696,100 of 697,197.  Every remaining difference is a conditional jump
(one-parcel opcodes 0x04..0x07), in three classes on `za main9.s`:

| reference | core | count | reading |
|---|---|---|---|
| 1 | 0 | 224 | the core folds a correctly predicted jump the reference model counts as unfolded |
| 2 | 3 | 161 | a misprediction the reference model places two instructions after its compare and the core places right after it |
| 1 | 3 | 77 | a jump the reference model counts as correctly predicted and unfolded, and the core as mispredicted |

These are open.  They are disagreements between the two models about
fold eligibility and compare distance in particular instruction
sequences, not yet traced to a page, and a cycle-accuracy claim for the
core does not extend to them.

## 2a. Documented instruction interactions not yet modelled

Printed p. 3-2 ("Certain combinations of instructions may produce
unexpected results…") states three hardware consequences the model now
silently ignores. They are listed here because "1:1" includes them:

1. **Wide result visible after a byte/half-word ADD, SHL or MUL.** If the
   truncated destination overflows but the 32-bit result fits, the next
   instruction may compute with the *untruncated* value when it is a
   divide or a right shift using that destination, or when its own
   destination is wider; two intervening instructions force the
   truncated value. The model always truncates.
2. **C/V setting needs two instructions of separation** before an
   instruction that reads the PSW through the CPU prefix, unless the
   flags are queried with TESTC/TESTV. The model lets a PSW read see the
   flags immediately.
3. **An ENTER may not follow the invalidation of the page it enters** by
   fewer than two instructions, so the memory table can update. The
   model does not enforce the spacing (it is a software restriction with
   a hardware consequence).

## 3. What "1:1" adds to the boot work

The boot (A0…A5) needs none of the open rows except the DUART. The
conformance work is ordered after it, but two items are written down now
because they change how instructions are added:

1. **Fetch and empty-pipeline delays** (Tables 4-6…4-9) must be charged
   once the prefetch can miss — the current zero-delay assumption is
   exactly "fetches always hit", which the 3 KB buffer makes false.
2. **`MUL`'s data-dependent cell** (Table 4-33 min 3 / max 20) needs the
   printed dependence, not a constant, before the row is called 1:1.
