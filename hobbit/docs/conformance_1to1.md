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
  predate EU_S1's three operand latches and are not re-measured.  An earlier attempt
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
