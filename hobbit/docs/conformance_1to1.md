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
| 4-34 DQM (p. 4-4) | `sem/` (`8·S` read as 8 single-word accesses, `S_CYC = A_CYC`; `SC/M quad` kept at the printed `4 + D` though the ATT2100 prints `4 + Q`, `docs/timing_tables.md` §7 item 4) + core (golden 019, 021) | rows present |
| 4-35 Conditional jumps (p. 4-5) | folded 0, unfolded 1; mispredict 3/2/1 at 1/2/3 instructions after the compare, folded *or* unfolded (only the "4 or more" row is split: folded 0, unfolded 1; `docs/timing_tables.md` §7 item 9) | `sem/` and the timing twin follow the table; the **core does not**: it prices every mispredicted folded branch 3 and folds into five-parcel hosts (`docs/cycle_accuracy_plan.md` §2.1, milestone C3) |
| 4-36 Miscellaneous (p. 4-5) | CATCH 1, CRET 15, KCALL 11, KRET 12, unimplemented 8 | present in `sem/`; CRET/KCALL/KRET not in the core |
| 4-6…4-9 delays (pp. 4-5…4-7) | **not charged**: the model adopts the p. 4-1 assumption "instruction fetches must access the instruction cache" | **not 1:1** while a fetch can miss |

Named choices, which the manual leaves open and which are therefore not
violations: A = 1, D = 2, Q = 4 (p. 4-2 prints no memory terms, and no
Appendix A figure draws a one-clock transfer: `docs/timing_tables.md`
§11); the TLB replacement policy (p. 2-1 prints none); the prefetch fill
policy. Table 2-4's translation penalties (p. 2-9) are in `timing.csv`
and charged by neither model yet.

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
     defect it was set for.  Re-run 2026-11-24 (the suite, Bluesim,
     commit 137212b1's core): `echo`, `cat`, `hello` 0, **`za` 0**,
     `zl` 9, `zc` 49.
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

Traced 2026-11-24 (`docs/cycle_accuracy_plan.md` §2.1,
`tools/cyc_classify.py`): the first is the core folding into a
*five-parcel* host, which p. 4-7 excludes ("a previous one- or
three-parcel instruction"); the second and third are *folded*
mispredicts, which the core prices at a flat 3 whatever the compare
distance, where Table 4-35 prints 2 and 1.  `zc frexp.c` (1,651,700
records, 20,343 differing in `cyc`, re-run 2026-11-24) has the same
three, 18,588, 1,298 and 441, and adds a fourth (16 records: a jump
after a trap's return, where the core's compare distance is reset by
the redirect).  Of zc's first class, 11,772 are the *unconditional*
one-parcel `JMP` (opcode 0x03) folded into a five-parcel host: so "every
remaining difference is a conditional jump" holds for `za` but not for
`zc`.  The core is to be fixed (plan
milestone C3); until then a cycle-accuracy claim for the core does not
extend to them.

## 1d. What booting s9term on the core found (2026-11-23)

`bsv/run_p9kern.sh N` boots the shipped kernel image `s9term` on the
privileged core (`mkHobbitCoreSystem`) from the ROM's hand-off and
compares its retirement records with the reference boot's
(`tools/p9boot.py` on `hobbit_sem` with a `System`), every field but
`cyc`, record by record; device reads are replayed from the reference
boot by record number and device writes checked against it
(`docs/p9boot.md`, "The boot on the core").  The core first had to gain
the privileged machine -- the CPU escape and the control registers,
CSP = ISP, CRET, KRET, the flushes, CONFIG.PX/KL (`docs/p9boot.md`
lists them) -- which is new behaviour, not a finding.  With it, the
comparison stopped twice before record 2,825,000 (rows 1, 2), and six
more times before 2,893,000 once interrupts were delivered and the boot
went on into `/boot` (rows 3-8; record numbers from row 3 on are the
reference's as merged 2026-11-23, which reaches `netadd` at 2,681,671
rather than row 2's 2,658,001):

| # | what | found at | fixed in | pinned by |
|---|---|---|---|---|
| 1 | The interlocked `ORI`/`ANDI`/`ADDI` (opcodes 0x01..0x03, pp. 3-37, 3-8, 3-6) were decoded as unimplemented and trapped | record 126,600, in `tas` (`ORI $1, *lock`), 3,397 records after `main` | `OP_ORI/ANDI/ADDI`; EU_S2 computes `dst OP src` and the accumulator's old-value write, which EU_S3 issues the next clock through the frame drain (`xw`); EU_S1 drains before and holds after (the pp. 3-8/3-37 Notes); R4 as the destination is the old value (p. 3-6 note) | golden 022 (and 009 now runs on the core) |
| 2 | **A wrong-path operand read that faulted raised the exception.**  The data face latches an MMU fault when the read is made, and the core started the event sequence at once -- for a read EU_S1 made on the predicted path of a branch that then mispredicted | record 2,658,001, in `netadd`: `CMPEQ $0,R24; JMPTN` predicted not taken, taken when the pointer is nil, and the fall-through's `CMPEQ *R24,R0` read virtual 0 | the orchestrator classifies a data fault on the clock it appears (`dfOperand`: EU_S1's operand fetch, which the box's `memLive` names); such a fault holds EU_S1, lets the older instructions complete, and is taken at EU_S1's PC only when they have (p. 1-37: the faulting instruction has not completed); a squash first drops it | golden 023 (run on the MMU core, PSW.V = 1) |
| 3 | **The recorded interrupt** (`docs/p9boot.md`, choice 3) is new behaviour; bringing it up found two defects in the new code: the queue's guarded `first` lifted "not empty" into every rule that read EU_S3's boundary, the commit rule among them, so nothing retired once the queue emptied; and the event's flush left the held instruction in EU_S3, which then retired after the interrupt | record 2,848,972 (level 6, in `spllo`): first a stall, then an extra `RETURN` record at 2,848,973 | an unguarded queue (`mkUGSizedFIFOF`, `notEmpty` tested at each use); EU_S3's `dropHeld` drops the held instruction on an event flush | the boot only (to 2,893,000); one interrupt, so more than one is untested, and so is the host/fold split at a boundary |
| 4 | `CATCH` with an absolute or stack-offset-indirect target (`CATCH *$addr`, `CATCH *Roffset`; p. 3-10: "MSP = *(addr)", "MSP = *(offset + SP)") was decoded as a bad mode and trapped | record 2,849,530, the interrupt return's `CATCH *R4` | decoded; EU_S1 reads the target word as it does for ENTER's memory forms (`word32Mem`) and passes the immediate form on | golden 024 |
| 5 | **CRET's CATCH portion that faults** (p. 3-15; p. 3-11: exception 8): the core retired CRET with MSP at the target and took the exception at the CRET's own PC with MSP left at the target | record 2,883,347, `touser`'s CRET to `/boot`: the user stack page is not mapped yet | CRET's record waits in EU_S3 until the portion ends (`pendCretRec`); a read fault during it is taken at the restored PC (`cretPc`), the record goes out with MSP at the blocks filled (the fault address rounded down to 16), and the stack cache is reset there (`hobbit_sem` `_cret_catch`) | the boot only |
| 6 | **FAULT read 0 after a fault**: the control-register box kept its own FAULT, which only a CPU write changed, while the event unit set its own | record 2,883,355, the fault handler's `CPU MOV FAULT, ...` | one FAULT, the event unit's (`setFault` for a CPU write); a read or write fault stores the word-aligned address (p. 1-39) | the boot only |
| 7 | **KCALL from user level faulted on its own frame**: the first frame word is written in KCALL's commit clock and was translated under the caller's PSW, so the kernel's interrupt stack refused it (a write fault, exception 9) | record 2,888,578, `/boot`'s first system call | EU_S3 tells the data face to translate that write at kernel level (`kernelNow`); the other two words drain under the kernel's PSW.  p. 3-29 says a fault on these writes resets the part and does not say at which level they are made; the kernel level is the reference's reading (`hobbit_sem.System`) and the only one under which 1e's system calls work | the boot only |
| 8 | **An exception's record carried a write**: on the privileged machine every trap's record had the unimplemented sequence's `*(CSP) = PC`; the reference's exception record (`_system_exception`) has none | record 2,886,867, `/boot`'s first fetch fault | only `TR_UNIMP` writes in `mkHobbitCoreSystem` (the other cores unchanged); an operand read fault, which the core takes before the instruction commits, now makes its own `trap=1` record (`evRecPend`, counted in `instrs`) | the write: the boot only.  The operand-fault record: no case before 2,893,000, untested |

Injections, each reverted by its exact reverse and the diff checked:

* `xw: False && ...` (no accumulator write): golden 022 fails at L03,
  `data` 0 for 5.  Nothing else ran past the first failure (hri_check
  stops there).
* `res = r` for R4 as the destination (ignore the p. 3-6 note): golden
  022 fails at L05, `data` 0 for 9.
* `dfOperand = False && ...` (the fault taken when it appears, as
  before): golden 023 matches L01..L10 and fails at L11, `pc` 0 for
  0x28 -- the event vector (0 in that harness) instead of the branch
  target.

Golden 023 pins one half of finding 2: a squash drops the held fault.
The other half -- a held operand fault taken at EU_S1's PC once it is
the oldest instruction -- is not exercised by anything yet: the boot's
faults before 2,893,000 are a CRET's CATCH portion, a fetch fault and a
KCALL frame write, none of them an operand read.  The interlocked drain
and hold (finding 1) likewise have no discriminating test (see the table
below).

Rows 3 and 5-8 are pinned by the boot alone, and not by an injection on
the final tree.  The evidence is the sequence in which they were found.
The boot stopped at the record each row names, with the field given, and
each fix moved the first difference past it: 2,848,973 (`pc`),
2,849,530 (`we`/`trap`), 2,883,347 (`msp_after`), 2,883,355 (`data`),
2,886,867 (`we`) and 2,888,579 (`pc`).  None of them is in the suite's
300,000-record sample.  A golden for each would need the privileged
machine in `run_golden.sh` and in the reference's CLI.  Neither has
one.

**The privileged machine against the boot sample.**  It is new
behaviour, so its evidence is the boot itself; each of these was
injected into a copy of `HobbitCore.bsv` and run against the 300,000-
record sample (`build/coreboot/inject_all.sh`, not committed; the copy
restored byte for byte after each):

| injection | observed |
|---|---|
| CONFIG.PX ignored | fails at record 2,096 (just after `_virtual`), every field |
| stack operands from SP when CSP = ISP | fails at record 11 (`_startup`), `addr` |
| CRET restores only PSW bits 31:16 | fails at record 2,065, `sp_after` |
| CRET's CATCH portion dropped | **every record still matched** |
| a RETURN with CSP = ISP returns to the next PC | **every record still matched** |
| ENTER's PSW.E never written | **every record still matched** |
| an SP write leaves MSP alone | **every record still matched** |
| a CPU instruction does not serialize | **every record still matched** |
| no drain before an interlocked instruction | **every record still matched** |

So the sample pins PX, the ISP as the stack base and CRET's PSW; the
CRET CATCH, the ISP-mode RETURN, PSW.E, the SP-write rule, the CPU
serialization and the interlocked drain rest on argument and on the
long run (to 2,825,000 then, 2,893,000 now; not re-run under
injection).  KRET is first reached at 2,849,530+ and user level at
2,886,866, after the sample.

The 16,172 "unrecorded" device reads p9kern.c counts by record
2,825,000 are the same kind of read as finding 2 and as §1c's
`dotsearch` reads: requests the reference boot never made, answered 0,
and none retired (the trace matched).  By address (`P9KSPEC=1`, the
same run): 16,128 of 0xB0003004 and 42 of 0xB0003000 -- the LCD
display (`io.h` `LCDADDR`, `IOACK(Lcdisp, 0x3000)`), which the
reference boot never reads -- and 2 of 0xA4400000, the SONIC
(`SONICADDR`).  That they are wrong-path operand fetches is the reading
of §1c's traced case, not traced again here.  All 102 reads the
reference made were requested and answered from the recording, and all
16,366 device writes matched.  On the reference as merged 2026-11-23
(p9boot's EEPROM, rtc and SONIC models; the idle skip off for the
recording) the same run records 161 reads and 16,373 writes to record
2,825,000: all 161 replayed, all 16,373 matched, the same 16,172
unrecorded reads, and the trace and the 74-byte console identical.  To
record 2,893,000 (the same reference, with the interrupt and `/boot`):
181 reads replayed, 16,526 writes matched, and 16,316 unrecorded reads.
By address (`P9KSPEC=1`, that run) these are 16,256 of 0xB0003004, 58
of 0xB0003000 and 2 of 0xA4400000: the same LCD and SONIC registers.
None of them retired.

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
