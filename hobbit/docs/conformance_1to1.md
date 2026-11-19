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

Sizes are checked against the netlist with `tools/area_netlist.py`, so
"1:1" means "present in the synthesized design at that shape", not
"asserted in prose".

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

## 3. What "1:1" adds to the boot work

The boot (A0…A5) needs none of the open rows except the DUART. The
conformance work is ordered after it, but two items are written down now
because they change how instructions are added:

1. **Fetch and empty-pipeline delays** (Tables 4-6…4-9) must be charged
   once the prefetch can miss — the current zero-delay assumption is
   exactly "fetches always hit", which the 3 KB buffer makes false.
2. **`MUL`'s data-dependent cell** (Table 4-33 min 3 / max 20) needs the
   printed dependence, not a constant, before the row is called 1:1.
