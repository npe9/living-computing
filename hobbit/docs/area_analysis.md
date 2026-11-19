# Where the 83,272 LUT4s go

## The question

`fpga/build.sh` produces a design that nextpnr-ecp5 reports as

```
Info:             DP16KD:    26/  208    12%
Info:           TRELLIS_FF: 24642/83640    29%
Info:         TRELLIS_COMB: 83272/83640    99%
```

and then fails with `Unable to find legal placement for all cells`.  The
owner's question is how much of that 83,272 is inherent to the machine
Figure 1-1 prints (printed p. 1-2) and how much is model overhead.

The short answer is **about 14,000 LUT4-equivalents of the 83,272 is
inherent; about 38,700 is the convenience program memory; about 6,200 is
the verification apparatus; and about 24,400 is implementation
inefficiency**.  The largest single item is not the processor at all: it
is the 256 x 32 on-chip program memory, which the printed machine puts
off-chip (printed p. A-1), and its 8,192-bit write multiplexer alone is
29,394 LUT4s.

## Measurement method

Everything below comes from one of four commands.  All products of the
measurement scripts go to `${TMPDIR:-/tmp}`; nothing is written into
`bsv/`, `fpga/`, `sem/` or `tests/`.

### 1. The flat board netlist: `tools/area_netlist.py`

```
cd hobbit
python3 tools/area_netlist.py fpga/build/ulx3s_top.json
```

`fpga/build.sh` runs yosys 0.51 `synth_ecp5 -top ulx3s_top` and writes
`fpga/build/ulx3s_top.json`.  That netlist is flat, but bsc keeps the
block name in every state, wire and cell name (`core_eu_*`,
`core_sc_*`, `core_ic_*`, `core_pf_*`, `mem_*`, `q_*`, `uart_*`,
`li`/`boot`/`started`).  The script classifies every `LUT4`, `PFUMX`,
`TRELLIS_FF`, `CCU2C` and `DP16KD` by that name.  The handful of opaque
`_hNNNN` temporaries take the label propagated forward from the
flip-flops that feed them; a cell whose own name names a block is never
relabelled, because the generated name is stronger evidence than its
fan-in.  This is the only attribution available after `synth_ecp5` has
discarded the module hierarchy (the generated Verilog is one module,
`mkHobbitUlx3s`), and it is the method the table below uses.

The same JSON gives the yosys cell totals: 76,650 `LUT4`, 8,235
`PFUMX`, 24,642 `TRELLIS_FF`, 2,670 `CCU2C`, 26 `DP16KD`.  nextpnr's
`TRELLIS_COMB` is 83,272, which is 76,650 + 8,235 - 1,613: a `PFUMX`
is a mux that nextpnr packs into a LUT4 slice when the two LUTs feeding
it are in the same slice, so 1,613 of the 8,235 muxes do not add a
combinational site.  The "LUT4-equiv" column below allocates the 1,613
packed muxes proportionally, `LUT4 + 0.804 * PFUMX`, where
0.804 = (83,272 - 76,650) / 8,235.  That column is a reporting
convention, not a separate measurement; the exact LUT4 and PFUMX
columns are what yosys printed.

### 2. The blocks as their own tops: `tools/area_blocks.sh`

```
tools/area_blocks.sh            # add --keep to keep the temp tree
```

The script copies the current `bsv/HobbitTypes.bsv`,
`bsv/HobbitDecode.bsv`, `bsv/HobbitStackCache.bsv` and
`bsv/HobbitUart.bsv` to a temp directory, adds a wrapper package that
instantiates one block per top, gives it minimal stubs for its
neighbours (a register as the memory, a register as the prefetch, a
counter as the decode store's PDU), and runs the same

```
bsc -verilog -g <top> ...
yosys -p "read_verilog <top>.v; ...; synth_ecp5 -top <top> -json ..."
```

as `fpga/build.sh`.  The stubs exist so the block under test is not
constant-folded away; they are not models and are subtracted or noted
where they matter.  The current `HobbitStackCache.bsv` is being
rewritten by another agent; an earlier snapshot did not compile (a
`memWrQ.deq`/`clear` conflict inside `boxStep`), but the final run of
the script compiles it and reports 10,884 LUT4 / 2,501 FF.  The flat
table's 14,953 is the 10:00 build; the two are both reported below.

**Caveat, stated up front:** sums of separately synthesised blocks do
not add to the flattened whole.  bsc inlines the blocks into one
module before yosys sees them, and yosys then optimises across the
former boundaries.  The UART is 1,699 LUT4 standalone but 1,167 in the
flat netlist (its prefix formatter shares logic with the surrounding
state); the program memory is 27,370 LUT4 standalone but 35,247 in the
flat netlist (the flat one has three write sources, the standalone
`mkHobbitMem` has one, and the flat one's testbench-only `peek` port is
pruned); the 3 KB prefetch is 41,052 LUT4 in the current source but
only 191 in the 83,272 build because that build has the old 64-word
stand-in.  The flat table is the authority for the 83,272; the
standalone table is the authority for what the block costs when it is
built the way the source says.

### 3. The candidate fixes: `tools/area_experiments.sh`

```
tools/area_experiments.sh       # optionally: ... path/to/ulx3s_top.json
```

The script runs the flat attribution, greps the flat netlist for the
testbench-only method names, and synthesises four small reference
modules with the same `synth_ecp5` flow: a 256 x 32 memory with a
single write port and a registered read, the same with an explicit
block-RAM output register, a 64 x 32 register file with one write port
and a combinational 64:1 read, and a 32 x 192 register file with one
write port and a combinational 32:1 read.  It also builds the current
UART writer as its own top and tries the synthesis knobs on it.

### 4. The flow itself

`fpga/build.sh` is the reference flow: bsc 2026.01 with
`BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib`, yosys 0.51
`synth_ecp5 -top ulx3s_top`, nextpnr-ecp5 0.6 `--85k --package
CABGA381 --speed 6 --freq 25 --timing-allow-fail`, ecppack 1.4.  The
83,272 `TRELLIS_COMB` figure and the 368-cell headroom are from
`fpga/build/pnr_sa2.log` (`nextpnr-ecp5 ... --placer sa --seed 2`),
which is the same netlist `fpga/build/ulx3s_top.json` and the table
below describe.

### Page and file cites

The "necessary" column is anchored to the printed manual:

* Figure 1-1, printed p. 1-2: the 3 KB three-way prefetch buffer, the
  32 x 192-bit decoded instruction cache, the 64 x 32 x 2 stack cache,
  the 3-stage prefetch/decode pipeline, the 3-stage execution unit,
  and the MMU with 2 x 32-entry page TLBs and 2 x 1 NPSRs.
* p. 1-1: the 3 KB encoded instruction cache and the 256-byte stack
  cache.
* pp. 1-32/1-33: the prefetch/decode unit's next-PC/alternate-next-PC
  job and the branch-folding rule.
* p. 4-2: the decoded instruction cache is 32 entries; the p. 4-1
  assumptions make an in-cache fetch and stack-cache operand free.
* p. A-1: the program and data memory is off-chip over the bus.

The "reason" column cites the current source file and line for the
implementation pattern.  The current worktree is mid-rewrite (the 3 KB
prefetch and the 192-bit `DecEntry` were added on 19 November, the
three-stage EU and the stack cache are being rewritten), so a line
number identifies the pattern, not the exact 10:00 build; the flat
netlist numbers are the 10:00 build's.

## The flat 83,272 design, block by block

`python3 tools/area_netlist.py fpga/build/ulx3s_top.json` prints this
table.  LUT4 + PFUMX are the yosys cells; LUT4-equiv is the
`LUT4 + 0.804 * PFUMX` reporting column; the block rows sum to the
flat netlist totals.

| block | LUT4 | PFUMX | LUT4-equiv | FF | CCU2C | BRAM | classification | reason |
|---|---:|---:|---:|---:|---:|---:|---|---|
| Prefetch window (64-word direct-mapped stand-in) | 191 | 2 | 193 | 2,064 | 8 | 0 | necessary block, but under-modelled | Figure 1-1 p. 1-2 prints 3 KB/3-way; this build has a 64-word, 2,048-bit window. The current source's 3 KB register array is 41,052 LUT4 / 22,539 FF (standalone, below) — it must be BRAM. `bsv/HobbitDecode.bsv:391,440` |
| PDU (3-stage) | 0 | 0 | 0 | 0 | 0 | 0 | necessary | The 10:00 build folds the old PDU into the decode-store row; the current three-stage PDU is 1,037 LUT4 / 355 FF standalone. pp. 1-32/1-33 |
| Decoded store (32 entries) | 6,826 | 211 | 6,996 | 8,448 | 232 | 0 | necessary block; 331-bit entry is implementation | Figure 1-1 p. 1-2 / p. 4-2 print 32 x 192 bits. The flat `core_ic_ic` is 10,592 bits = 32 x 331; the current source's `DecEntry` is 192 bits and its block is 4,498 LUT4 / 6,246 FF (standalone). The 32 x 192 array with one write port is 194 LUT4 / 0 FF as a LUT RAM (below). `bsv/HobbitDecode.bsv:753,760` |
| Stack cache (64 x 32) | 14,953 | 2,167 | 16,695 | 2,285 | 475 | 0 | necessary block; array is implementation | 64 x 32 words is 2,048 bits and 2,285 FF here. The 12,239 LUT4 + 1,996 PFUMX named `core_sc_cache` are the `Vector` update and the 64:1 read mux, not the array; the current rewrite is already 10,884 LUT4 (10,719 of it the array). A 64 x 32 register file with one write port and a combinational read is 132 LUT4 / 64 PFUMX / 0 FF (below). p. 1-5/1-12; `bsv/HobbitStackCache.bsv:127,344` |
| Execution unit | 16,335 | 1,206 | 17,305 | 1,767 | 548 | 17 | necessary core + verification + implementation | The 17 BRAM and 1,043 FF / 2,506 LUT4 of `core_eu_outQ` are the old 64 x 599 `HriPair` retirement queue; the current source's `traceQ` is 64 x 299 (8 BRAM) `bsv/HobbitCore.bsv:583`. The 330-bit `cur` and the 299-bit `fbrRec` are the wide decoded-instruction copy. pp. 1-32/1-33 |
| Program memory (256 x 32) | 35,247 | 4,248 | 38,662 | 8,200 | 0 | 1 | convenience memory + implementation | The machine's memory is off-chip (p. A-1). The 29,394 LUT4 named `mem_m$D_IN` are the 8,192-bit next-state mux for the three write sources; the 8,192 FF are the array. A 256 x 32 memory with one write port and a registered read is 46 LUT4 / 33 FF / 1 DP16KD (below). `bsv/HobbitTypes.bsv:558,574` |
| HRI retirement queue (48 x 299) | 940 | 50 | 980 | 882 | 1,163 | 8 | verification | The board's `mkSizedBRAMFIFOF(48)`; 1,163 CCU2C is 43% of all carry cells in the design. `bsv/HobbitUlx3s.bsv:124,130` |
| HRI presentation (`present`/`pendFold`) | 585 | 288 | 817 | 578 | 0 | 0 | verification | The core's one-record-at-a-time presentation registers; the HRI is the verification interface (plan gate 5). `bsv/HobbitCore.bsv:783` in the current source; the flat build's `core_present`/`core_pendFold` |
| UART writer | 1,167 | 56 | 1,212 | 398 | 223 | 0 | verification (board only) | The 116-byte fixed HRI line and its `cyc` formatter; 1,167 LUT4 in the flat netlist, 1,699 standalone from the current double-dabble source. `bsv/HobbitUart.bsv:106,236,302` |
| Board glue, incl. LED | 16 | 1 | 17 | 11 | 4 | 0 | board glue (not the chip) | Image load, boot counter, LEDs. `bsv/HobbitUlx3s.bsv:141`; `bsv/HobbitUlx3sTop.v` |
| Shared / unattributed | 390 | 6 | 395 | 9 | 17 | 0 | implementation / attribution residual | Opaque temporaries whose fan-in crosses blocks; the 8-bit power-on counter's 8 FF are here |
| **Total** | **76,650** | **8,235** | **83,272** | **24,642** | **2,670** | **26** | | |

The table's `LUT4-equiv` sum is 83,272 by construction; the LUT4 and
PFUMX columns sum to 76,650 and 8,235, which is 84,885, and the 1,613
difference is the packed PFUMX.  The flat netlist is a single module;
the block split is the only decomposition yosys leaves, and the last
row is what the name/ propagation method could not assign.

## The blocks as their own tops

`tools/area_blocks.sh` (current sources, stubs for neighbours):

| top | LUT4 | PFUMX | FF | CCU2C | DP16KD | note |
|---|---:|---:|---:|---:|---:|---|
| `mkAreaMem` (256 x 32 `mkHobbitMem`) | 27,370 | 11,545 | 8,200 | 0 | 0 | the `Vector` update plus two read muxes (`readData`, `peek`); the flat board prunes `peek` and adds the third write source |
| `mkAreaDecode` | 629 | 106 | 0 | 179 | 0 | the parcel decoder; small |
| `mkAreaPf` (current 3 KB, 128 sets x 3 ways x 64 bits) | 41,052 | 6,572 | 22,539 | 4 | 0 | the current source's register-array 3 KB prefetch: by itself larger than every non-memory block of the 83,272 design |
| `mkAreaPdu` (3 stages) | 1,037 | 152 | 355 | 133 | 0 | includes the 629-LUT4 decoder |
| `mkAreaIc` (current 192-bit store) | 4,498 | 210 | 6,246 | 128 | 0 | includes the 224-FF stub PDU; the store itself is ~4,496 LUT4 / 6,022 FF |
| `mkAreaUart` (current writer) | 1,840 | 408 | 398 | 161 | 0 | double-dabble serial decimal; the direct `UartOnly` wrapper in `area_experiments.sh` is 1,699 / 317 — the 141-LUT4 difference is package-boundary constant folding, not a different source |
| `mkAreaStubMem` | 33 | 0 | 32 | 0 | 0 | the stub's own area |
| `mkAreaStubPfTop` | 34 | 0 | 64 | 32 | 0 | the stub's own area |
| `mkAreaStubPduTop` | 2 | 0 | 224 | 96 | 0 | the stub's own area |
| `mkAreaSc` (current rewrite) | 10,884 | 2,944 | 2,501 | 372 | 0 | the current three-stage box; 10,719 of the LUT4 is the 64 x 32 `Vector` array, against the 132-LUT4 reference |

The stack-cache row is the current rewrite; the flat table's 14,953
LUT4 / 2,285 FF is the 10:00 build.  The rewrite is 4,069 LUT4
smaller, but 10,719 of its 10,884 LUT4 is still the 64 x 32 `Vector`
update and its 64:1 read mux; the 132-LUT4 `reg_64x32` reference below
is the intended array.  The flat `core_sc_cache` attribution is
12,239 LUT4 + 1,996 PFUMX + 2,048 FF.

## The reference implementations

`tools/area_experiments.sh` (same `synth_ecp5`; the reference modules
are complete tops):

| module | LUT4 | PFUMX | FF | CCU2C | DP16KD | what it is |
|---|---:|---:|---:|---:|---:|---|
| `mem_reg` | 46 | 5 | 33 | 0 | 1 | 256 x 32, one write port, registered read address; yosys infers one DP16KD |
| `mem_bram` | 47 | 6 | 74 | 0 | 1 | the same with an explicit output register |
| `reg_64x32` | 132 | 64 | 0 | 0 | 0 | 64 x 32, one write port, combinational 64:1 read; yosys infers LUT RAM (`DPR16X4`) |
| `reg_32x192` | 194 | 0 | 0 | 0 | 0 | 32 x 192, one write port, combinational 32:1 read; LUT RAM |
| UART, default | 1,699 | 317 | 398 | 161 | 0 | current writer |
| UART, `synth_ecp5 -abc2` | 1,649 | 271 | 398 | 160 | 0 | two ABC passes: 50 LUT4 less, 2.9% |
| UART, `synth_ecp5 -noabc9` | 2,491 | 470 | 398 | 286 | 0 | worse |
| UART, `share -aggressive` pre-pass | 0 | 0 | 0 | 0 | 0 | the pass collapses the RTL to an empty design in this flow; not usable |

The four reference modules are the intended hardware for the four
arrays.  The point is not that a 256 x 32 memory "costs 46 LUT4"; it is
that the 35,247-LUT4 flat memory and the 46-LUT4 reference have the
same read timing, the same 256 x 32 shape and the same one-word-per-
clock contract.  The difference is that the flat source writes a
`Vector` with `update` from three sources and reads it through a
dynamic index, while the reference writes one `reg` array from one
source and reads it through a registered address; yosys recognises the
second as a memory and the first as 8,192 flip-flops plus a 8,192-bit
mux.

## Verdict

The 83,272 `TRELLIS_COMB` (76,650 LUT4 + 8,235 PFUMX - 1,613 packed)
splits as follows.  "LUT4-equivalent" is the table's reporting column;
the shares are of 83,272.

| bucket | LUT4-equiv | share | basis |
|---|---:|---:|---|
| Necessary (inherent to the printed machine, current ISA subset) | **14,000** | 16.8% | 192-bit decoded store 4,666 + three-stage PDU 1,156 + 64 x 32 stack cache 2,337 + 3 KB prefetch 0 LUT4 (2-3 DP16KD) + execution unit estimate 6,000; MMU 0 (not implemented at this subset) |
| Verification overhead | **6,200** | 7.4% | HRI queue 980 + HRI presentation 817 + UART 1,212 + EU outQ 3,032 + the HRI record mux inside the EU ~160 |
| Convenience memory | **38,662** | 46.4% | the flat program memory 35,247 + its 4,248 PFUMX (p. A-1 puts it off-chip) |
| Implementation inefficiency | **24,410** | 29.3% | the residual: 83,272 - 14,000 - 6,200 - 38,662 |
| **Total** | **83,272** | **100%** | nextpnr `TRELLIS_COMB` |

The arithmetic is exact for the last row by definition: 14,000 + 6,200
+ 38,662 + 24,410 = 83,272.  The residual is the implementation bucket,
and the per-block evidence for it is:

* the stack-cache array's 12,239 LUT4 + 1,996 PFUMX vs the 132 + 64
  reference;
* the decoded store's 6,826 LUT4 + 8,448 FF vs the 194-LUT4 / 0-FF
  32 x 192 reference and the current 192-bit 4,498-LUT4 block;
* the EU's 8,273 LUT4 over the 6,000 estimate after subtracting the
  outQ and HRI;
* the 191-LUT4 stand-in prefetch, the 388-LUT4 unattributed row and
  the 2-LUT4 shared row.

Those per-block implementation items sum to about 23,800, within 600
LUT4 of the 24,410 residual; the 600 is the estimate in the "necessary"
EU and the fact that the 10:00 build's decode-store row also contains
its old PDU.  The four totals are a budget, not a partition to the last
LUT4: yosys optimised across the block boundaries and the current
worktree is not the 83,272 build.

### What does not add up

1. **76,650 vs 83,272.**  The per-block LUT4 column sums to 76,650; the
   nextpnr number includes 8,235 PFUMX and subtracts the 1,613 that
   share a LUT4 slice.  The LUT4-equiv column is the bridge, not a
   measurement.
2. **The standalone blocks are not the flat design.**  The UART is
   1,699 (direct wrapper) or 1,840 (shared-package wrapper) and 1,167
   flat; the memory 27,370 and 35,247; the IC 4,498 and 6,826; the
   prefetch 41,052 (current 3 KB) and 191 (the 10:00 64-word stand-in);
   the PDU 1,037 and 0 (folded); the stack cache 10,884 (current) and
   14,953 (flat).  The flat
   numbers are the design; the standalone numbers are the block's
   source-level cost.
3. **The 83,272 build is not the printed machine.**  It has a 64-word
   prefetch stand-in, a 331-bit decoded-store entry instead of 192, the
   one-instruction-at-a-time EU, no MMU and no bus.  The "necessary"
   14,000 is for the blocks the build does implement; a faithful 3 KB
   prefetch in *registers* would add 41,052, and a faithful MMU would
   add the TLB/NPSR state.  The machine's inherent blocks are not free;
   they are simply much smaller than the current arrays when built as
   memories.
4. **The 368-cell placement failure is not a 368-LUT4 logic shortage.**
   The design is at 99.6% and nextpnr cannot legalise the last cells.
   Freeing the top three fixes (below) frees ~59,100 LUT4-equivalent
   (59,075 net of the three references), not 368.
5. **The current worktree is a different design.**  The 3 KB prefetch
   (41,052 LUT4 as registers), the 192-bit decoded store (4,498), the
   three-stage PDU (1,037), the current stack cache (10,884) and the new
   EU (`traceQ` 64 x 299, 8 BRAM)
   are the current rewrite, not the 10:00 flat build.  The 3 KB
   prefetch is the urgent warning: *if the current fidelity rewrite is
   built as written, it adds 41,052 LUT4 to an already-full device.*

## Ranked fixes

The savings are measured where a measurement exists; the full-design
effect is the LUT4-equiv column unless marked estimate.  "Risk" is
what can go wrong in the RTL, not schedule.

### 1. Program memory: one write port / BRAM — save ~35,200 LUT4, 8,167 FF

The flat memory is 35,247 LUT4 + 4,248 PFUMX + 8,200 FF + 1 DP16KD.
The 29,394 LUT4 named `mem_m$D_IN` are the 8,192-bit next-state mux
for the image loader, the stack-cache flush and the EU write; the
8,192 FF are the `Vector#(256, Word)` array (`HobbitTypes.bsv:558,574`).
The reference 256 x 32 with one write port and a registered read is
**46 LUT4 + 33 FF + 1 DP16KD** (`mem_reg`), so the saving is the whole
35,201 LUT4 / 8,167 FF; the LUT4-equiv saving is 38,612 (the block's
38,662 minus the 50 LUT4-equiv of the reference).

The fix is to mux the write address, data and byte enables at 32 bits
(plus the one-hot write enable) into one write port, then use
`BRAM2`/`BRAM1` or a plain `reg` memory.  The read timing does not
change: the board already registers the read address and returns the
array output the next cycle, which is exactly the DP16KD timing.  Risk:
write-port arbitration for the boot loader versus the stack-cache
flush/EU write (the image load is over before the core starts, and the
flush/EU writes are already disjoint in the SC); read-during-write on
the same address (the memory is never read and written on the same
word in one cycle; the current array's read-first behaviour is the
BRAM default).  This is the single largest saving and the lowest risk.
The memory is convenience in the first place: the printed machine's
memory is off-chip (p. A-1), so the alternative is the real bus and
external SRAM, which removes the same 38,662 from the FPGA.

### 2. Stack-cache array: one write port, LUT RAM — save ~12,100 LUT4, 1,932 PFUMX, 2,048 FF

The flat `core_sc_cache` is 12,239 LUT4 + 1,996 PFUMX + 2,048 FF: the
`cache` is a `Vector#(64, Word)` written by `update` from the refill
and the EU, and read through a 64:1 mux (`HobbitStackCache.bsv:127,344`).
The reference `reg_64x32` — one write port, a 32-bit write address and
data, a combinational 64:1 read — is **132 LUT4 + 64 PFUMX + 0 FF**.
Against the flat build the saving is 12,107 LUT4 + 1,932 PFUMX +
2,048 FF (13,661 LUT4-equiv, the flat array's 13,844 less the
reference's 183); against the current 10,884-LUT4 rewrite it is
10,719 LUT4 + 2,880 PFUMX + 2,469 FF (12,852 LUT4-equiv).  The SC
control (2,154 LUT4 in the flat estimate, 132 in the current rewrite)
is already counted in the "necessary" SC.

Risk: the cache has two writes that can occur in one clock — the CATCH
refill writes at or above the fill watermark and the EU writes below
it.  The existing code merges them into one `update`, which is exactly
the 8,192-bit mux; the fix muxes the 32-bit data/address and uses one
write enable and one write port, which the current code's disjointness
argument already permits.  `reset` writes all 64 words; model it as a
write enable on every entry for one cycle or as a per-entry valid bit,
not as a second full-width mux.  The read must stay combinational, so
this is a register file/LUT RAM, not a DP16KD.

### 3. Decoded store: 32 x 192 array as one-write LUT RAM/BRAM — save ~6,600 LUT4, 8,448 FF

The flat 10:00 store is 331 bits per entry (10,592 source bits, 8,448
Implemented FF), 6,826 LUT4 and 211 PFUMX; the printed entry is 192
bits (p. 1-2, p. 4-2).  The current source already has `DecEntry =
192` and a 4,498-LUT4 / 6,246-FF block (`HobbitDecode.bsv:753,760`;
the 6,246 includes the 224-FF test stub).  The reference `reg_32x192`
with one write port and a combinational 32:1 read is **194 LUT4 + 0 FF**
(LUT RAM).  Against the flat 6,826 LUT4 / 8,448 FF the saving is
6,632 LUT4 + 8,448 FF (6,802 LUT4-equiv, the block's 6,996 less the
reference); against the current 192-bit 4,498 LUT4 / 6,246 FF it is
4,304 LUT4 + 6,022 FF (4,474 LUT4-equiv).

The three array fixes together replace 59,502 LUT4-equivalent of
array (memory 38,662 + stack cache 13,844 + decoded store 6,996) with
427 LUT4-equivalent of reference (50 + 183 + 194), a net 59,075; the
flat design would fall from 83,272 to about 24,200 LUT4-equivalent.
Against the current rewrite's smaller 192-bit store and 10,884-LUT4
stack cache the same three are 55,938, leaving about 27,300.

Risk: the EU's `lookup` is combinational in the issue cycle, so the
array must be LUT RAM or a combinational register file, not a DP16KD;
the tag/valid (`decEntryFull` and the 26-bit PC tag) and the
`fill`/`install` rule stay.  The 192-bit width is the printed width;
the 138-bit excess in the 331-bit entry is the next/alternate-PC pair,
which the printed format does not store and the p. 4-7 note recomputes.

### 4. Current 3 KB prefetch: BRAM, not a register array — save ~41,000 LUT4, 22,500 FF (current tree, not the 83,272)

The current source's 3 KB prefetch is
`Vector#(128, Vector#(3, Maybe#(PfcLine)))` (`HobbitDecode.bsv:391`),
read through a three-way 64-bit mux (`lineAt`, line 440) and written
by the fill.  Standalone it is **41,052 LUT4 + 6,572 PFUMX + 22,539 FF**
— more than the entire 83,272 design's non-memory part; its
LUT4-equiv is 46,336.  The printed
3 KB is inherent (Figure 1-1, p. 1-2), but a 3 KB/3-way cache belongs
in 2-3 DP16KD (24,576 data bits + 8,448 tag bits = 33,024 bits, three
ways of 128 x 86 bits, so 3 DP16KD or 2 if the tags are packed); the
LUT4 cost is the tag comparison and the line selection, a few hundred,
not 41,000.  The 83,272 build does not contain this block (its
prefetch is the 191-LUT4 64-word stand-in), so this saving applies to
the next build.

Risk: the PDU reads three 64-bit lines per fetch, and a DP16KD has two
ports; the 3-way set needs either three parallel banks (3 DP16KD, one
read each) or a one-cycle bank select.  The current `lineAt` is
combinational; a BRAM read is synchronous, so the PDU S1 stage must
absorb the read cycle.  That is a pipeline-depth change, and the p. 4-1
in-cache assumption prices the fetch at zero, so the cycle counts are
not affected; the structural 3-stage PDU already has a stage to put it
in.  Do not leave the 3 KB as a `Vector` register array.

### 5. EU retirement queue: 64 x 599 -> 8 x 299 or a direct hand-off — save ~2,500 LUT4, 1,000 FF, 17 BRAM

The flat 10:00 build's `core_eu_outQ` is 17 DP16KD and 2,506 LUT4 +
1,043 FF; a 64-deep, 599-bit `HriPair` queue.  The current source's
`traceQ` is 64 x 299 (8 BRAM) at `HobbitCore.bsv:583`, so the rewrite
has already halved the width; a smaller queue (8-16 records) or a
direct hand-off to the board's 48-deep queue would remove most of the
remaining BRAM and the LUT4/FF around it.  The board queue is 48 deep
and the smoke retires 41, so a small EU queue is enough if the board's
slide is the only consumer.

Risk: the EU has no stall hook in the 10:00 build; a full outQ stalls
the commit and changes the `cyc` stamps.  The 64-deep queue exists to
avoid that.  The current three-stage EU has its own `traceQ`; the
queue depth must be chosen against the longest run of back-to-back
commit records, not against the 48-deep board queue alone.  This is a
verification-cost removal, not a machine change.

### 6. `synth_ecp5 -abc2` — save ~2,400 LUT4 estimate (50 measured on the UART)

On the UART writer the default flow is 1,699 LUT4 / 317 PFUMX / 161
CCU2C; `synth_ecp5 -abc2` (two ABC passes) is 1,649 LUT4 / 271 PFUMX /
160 CCU2C, a 50-LUT4, 2.9% saving.  A proportional full-design estimate
is 83,272 * 0.029 = 2,415 LUT4, which would put the build under the
83,640 limit without an RTL change; it is an estimate because the UART
is small and mux-heavy in a different way from the memory.  `-noabc9`
is *worse* (2,491 LUT4), so the default ABC9 flow is the right one;
`-abc2` is the only two-pass variant worth trying.  The
`share -aggressive` pre-pass was tried and collapses the design to
zero cells in this flow (the pass removes the top's logic; the
`synth_ecp5` internal `share` is the one that runs), so it is not a
lever.

Risk: synthesis time roughly doubles; the mapping is still LUT4; the
behaviour is unchanged.  Run it on the full board and check nextpnr
placement before touching RTL.

### 7. UART writer — save 0 LUT4; the CCU2C is the lever

The flat UART is 1,167 LUT4 / 223 CCU2C / 398 FF; the current writer is
1,699 / 161 / 398 standalone; the old combinational `decDigits` is
1,731 / 1,378 / 399 and its conversion-free form is 1,439 LUT4.  The
serial double-dabble (`HobbitUart.bsv:236,302`) is already in the
current source.  The LUT4 difference between the old combinational
writer and the serial one is only 32 (1,731 -> 1,699); the conversion
is about 260 LUT4 of the writer, and the 116-byte line formatter is
the other 1,439.  The real win in the old-to-new change is the
**1,217 CCU2C** (1,378 -> 161), which is 45% of the design's 2,670
carry cells; at 99% utilisation the carry cells decide legalisation,
so the serial formatter is worth keeping even though it does not move
the LUT4 count.  Removing the UART from the chip (a board build with
only the LEDs) saves 1,212 LUT4-equivalent + 223 CCU2C + 398 FF; the
HRI stream is the board's verification purpose, so that is a product
decision, not a bug.

### 8. Unused interface pruning — 0 LUT4; already done

The flat netlist has no `cacheWord`, `readMem`, `minSp`, `maxSp`,
`refills`, `instrs`, `folded` or `peek`; the yosys JSON has zero
occurrences of each (the names survive only in the generated Verilog
comments).  `opt_clean` already removed the testbench-only methods, so
there is nothing to reclaim.  The only caveat is that a block built as
its own top (as `area_blocks.sh` does) cannot prune them: the
standalone `mkAreaMem` is 27,370 LUT4 partly because its `peek` output
is a real port; the board's flat memory prunes it.

## What surprised the measurement

* The program memory's write mux is 29,394 LUT4, 38% of the whole
  design, and it is a `Vector` `update` from three sources, not a
  memory.  The single-write 256 x 32 reference is 46 LUT4 and one
  DP16KD.
* The current 3 KB prefetch is 41,052 LUT4 / 22,539 FF as a register
  array — one block larger than the whole 83,272 design's non-memory
  part.  The printed 3 KB is inherent; the register array is not.
* The four simple memory/register-file references (46, 132, 194 LUT4)
  are three orders of magnitude below the corresponding flat arrays
  (35,247, 12,239, 6,826).  The `Vector#(N, T)` + `update` idiom is
  the single biggest implementation cost in the model.
* Unused-interface pruning is a non-candidate: yosys already does it.
  The `share -aggressive` pre-pass is a non-candidate: it empties the
  design.  The `-abc2` flow is a small but real 3% lever.
* The board's 48 x 299 retirement queue alone accounts for 1,163 of the
  2,670 CCU2C cells (43%), more than the EU.  The carry cells, not the
  LUT4 count, are what nextpnr legalises last at 99% occupancy.
* The current worktree's stack cache compiles at 10,884 LUT4, down from
  the 10:00 build's 14,953, but 10,719 of that is still the 64 x 32
  `Vector` array; the `reg_64x32`-style single write port is the rest of
  the fix.  An earlier snapshot of the rewrite did not compile at all
  (a `memWrQ.deq`/`clear` rule conflict).

## Reproduction

```
cd hobbit
python3 tools/area_netlist.py fpga/build/ulx3s_top.json
tools/area_blocks.sh
tools/area_experiments.sh
```

The first command needs `fpga/build/ulx3s_top.json` (run
`fpga/build.sh` or its yosys step).  The second needs bsc 2026.01 and
yosys 0.51 with the ECP5 cells; the third needs the UART source and the
JSON.  All three are stdlib/shell/Python-3 only and write only to
`${TMPDIR:-/tmp}`.

## Confirmation in Bluespec itself (2026-11-19)

The reference modules above are Verilog. The same shapes were then written in
Bluespec and synthesised through the board's own flow, because the question
was whether the *Bluespec* idiom reproduces them:

| prototype (BSV) | shape | LUT4 | PFUMX | FF | DP16KD | DPR16X4 |
|---|---|---:|---:|---:|---:|---:|
| `mkMemProto` | `RegFile#(Bit#(8), Bit#(32))`, one `upd`, registered read address | 39 | – | 97 | **1** | – |
| `mkScProto` | `RegFile#(Bit#(6), Bit#(32))`, one `upd`, combinational `sub` | 56 | 7 | 39 | **1** | – |
| `mkIcProto` | `RegFile#(Bit#(5), Bit#(192))`, one `upd`, combinational `sub` | 200 | – | 10 | – | **96** |

(The FF counts include the prototypes' drive counters; the arrays themselves
are the 1 DP16KD / 96 DPR16X4 and the tens of LUT4.)

Two practical consequences:

1. **`RegFile` is a library cell, not inlined.** bsc's Verilog instantiates a
   module named `RegFile`, so the synthesis source list must include
   `$BLUESPECDIR/Verilog/RegFile.v` — exactly as it already includes
   `FIFO2.v`, `BRAM2.v` and `SizedFIFO.v`. Without it, yosys stops with
   ``Module `\RegFile' referenced in module ... is not part of the design``.
   `RegFileLoad.v` is the companion for an initialised file-backed array.
2. **One `upd` call site is the rule.** `RegFile`'s port accounting is
   static: every statically reachable `sub`/`upd` call site is a port, and the
   total is capped at 5. Mux the writer(s) into a single `Action` first; for
   the prefetch's three way-reads plus one write (4 ports) that is still
   inside the cap.
