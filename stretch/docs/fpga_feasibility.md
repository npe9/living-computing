# Running the Stretch Bluespec model on a ULX3S: a measured feasibility note

Status: **assessment, not a port.** Every number below is either a
measurement taken in this worktree (the commands are quoted so they
can be re-run) or a citation to a primary document. Where a number
could not be obtained it is in §7, "What could not be determined",
rather than estimated. Measurements taken 2026-10-16.

The target this is measured against: **a typical 7030 — six memory
units, 98,304 words — cycle-accurate, eventually running MCP and
other systems software.** One- and two-unit configurations are
measured too, but as stepping stones and as bounds, not as the goal.

## Toolchain actually present

| tool | version | path |
|---|---|---|
| `bsc` (used) | 2026.01, the Homebrew Cellar build `bsv/build.sh` pins | `/opt/homebrew/Cellar/bsc/2026.01/bin/bsc` |
| `yosys` | 0.51 (git c4b5190) | `/opt/homebrew/bin/yosys` |
| `ecppack` | Project Trellis 1.4_9 (`prjtrellis`) | `/opt/homebrew/bin/ecppack` |
| `verilator` | 5.052 | `/opt/homebrew/bin/verilator` |
| `nextpnr-ecp5` | **WORKS — see §9.0. The "unrecoverable" verdict below is RETRACTED**: §2.6 searched with `find / -maxdepth 4` and the four working arm64 builds sit at depth 6. All of §9's place-and-route used one of them. | `~/src/ulx3s-experiments/bluespec-ulx3s/toolchain/nextpnr-build/nextpnr-ecp5` |

A caveat on all wall-clock figures below: the machine was running at a
load average of 100–200 on 16 cores throughout (other work, not this).
CPU times are real; wall times are not comparable to a quiet machine.

---

## 1. Does the model generate Verilog? **Yes — unmodified, no errors, two benign warnings.**

The project has only ever used the Bluesim backend (`bsv/build.sh`
runs `bsc -sim`). The Verilog backend had never been tried. It works.

Command (from `stretch/bsv`, with the same `BLUESPECDIR` pinning
`build.sh` uses; `-g mkStretchCore` targets the design's own
synthesis boundary, declared `(* synthesize *)` at
`StretchCore.bsv:65`, deliberately **not** a testbench):

```sh
export BLUESPECDIR=/opt/homebrew/Cellar/bsc/2026.01/libexec/lib
bsc -verilog -vdir <out>/vdir -bdir <out>/vbuild -info-dir <out>/vinfo \
    -g mkStretchCore -u StretchCore.bsv +RTS -K512m -RTS
```

Result:

```
Verilog file created: .../vdir/mkStretchCore.v
[exited with code 0]
bsc ... 142.33s user 1.57s system
```

- **`mkStretchCore.v`: 102,173 lines, 4,795,128 bytes.**
- **142 s of CPU**, peak RSS 1.66 GB, inside the `+RTS -K512m` the
  project already uses.
- **Exactly two warnings, both `(G0117)` "action shadowing"**: rule
  `rl_recover` shadows `mem_writeWord`'s writes to `st_xreg_0..15` and
  `mem_setIndicatorBits`'s write to `st_indicators`; rule `rl_io`
  shadows `io_loadReaderWord`'s writes to `ioDev_printerImg_0..31`.
  Informational: a rule and an externally-called method write the same
  register in the same cycle and the rule wins. Both are
  *harness-versus-core* collisions that exist only because the
  loader methods are exposed at the top level at all (§3.5).

### 1.1 What the generated Verilog needs besides itself

Counted by grepping instantiations in `mkStretchCore.v`:

| primitive | instances | source |
|---|---|---|
| `BRAM1` | 6 | `$BLUESPECDIR/Verilog/BRAM1.v` |
| `SizedFIFO` | 7 | `$BLUESPECDIR/Verilog/SizedFIFO.v` |
| `RevertReg` | 12 | `$BLUESPECDIR/Verilog/RevertReg.v` |

That is the entire list. All three are ordinary synthesisable Verilog
shipped with bsc; `BRAM1.v` is a textbook inferrable synchronous RAM
(one `reg [DATA_WIDTH-1:0] RAM[0:MEMSIZE-1]`, written and read in a
single `always @(posedge CLK)`). No `$fopen`, no `$fgetc`, no DPI, no
`BRAM1Load`, no clock-generation primitive. The six BRAMs, verbatim:

```verilog
BRAM1 #(.PIPELINED(1'd0), .ADDR_WIDTH(32'd14), .DATA_WIDTH(32'd64),
        .MEMSIZE(15'd16384)) st_mbcu_units_0_ram_memory(...)
```

— `units_0` … `units_5`: **6 × 16384 × 64 = 6,291,456 bits = 6.29 Mbit
= 768 KiB** of main storage, confirming `NumUnits = 6`.

yosys 0.51 read this file with **no errors** and one warning
(`Encountered 'parallel_case' comment`). Worth noting because
`sangwoojun/ulx3s_bsv` (§3.2) ships a `replacetoken` utility
"required to modify bluespec-generated verilog code to be compatible
with yosys" — that was not needed here, presumably an older-yosys
problem.

### 1.2 Blocker list, classified (a) test-only / (b) small change / (c) real redesign

The headline is that the predicted blockers did not occur.

| predicted blocker | found? | class |
|---|---|---|
| `$display` in rules | **No blocker.** `StretchCore.bsv` has 2, `StretchStorage.bsv` has 2; bsc emitted them inside generated `always` blocks without complaint, and yosys ignores them. (The 5 in `StretchSmoke.bsv` and 6 in `StretchSvaWidthSweep.bsv` are testbenches, outside `mkStretchCore`; the other 11 model files have none.) | **(a)** — except `StretchStorage.bsv:328` ("store queue full, write ... LOST"), a real diagnostic that on hardware wants an LED or a status bit: **(b)**. |
| dynamic vector indexing | **Yes, pervasively — and not a blocker.** `xreg[a - addrIndexBase]`, `readerImg[i]`, `resp[t]`, `units[unitOf(q.addr)]`, `chPending[c]`. bsc elaborates all of it into muxes. | not a blocker — but it *is* why the design is large: see the measured 8,102 LUT4 for `mkStretchIO` in §2.4, which is almost entirely index muxes over 80 registers. |
| structures bsc will not synthesise | **None.** Every `Reg`, `Vector#(n,Reg#(..))`, `RWire`, `PulseWire`, `mkConfigReg`, `mkUGSizedFIFOF` and `BRAM1Port` has a Verilog implementation. | — |
| `StretchMemory.bsv` modelling timing, not hardware | **It models timing with real hardware.** `busy`/`readDue` are `Reg#(Bit#(4))` counters that delay a real BRAM to 5 clocks and hold the unit busy 7, reproducing the 2.1 µs core cycle. Synthesises fine (measured: §2.3). | **(a)** for synthesis. The *fixed* 5/7-clock contract vs. SDRAM is **(c)** — and whether it can be honoured turns on the SDRAM clock and whether the controller bursts: see §3.1. |
| `StretchIO.bsv` modelling timing, not hardware | **It models devices as registers**: `Vector#(32,Reg#(Word64))` ×2 + `Vector#(16,Reg#(Word64))` = 80 × 64 = 5,120 flip-flops of "card reader", "printer" and "tape", plus three `ControlWord` registers and `tapePos`. Measured at 5,317 TRELLIS_FF standalone. No file I/O at all. | **(a)** for synthesis; **(c)** for "means something on real hardware" — §3.6. |

**New blocker found, not on the predicted list, and it matters for
measurement rather than for the board:** `mkEBox`, `mkLookAhead` and
`mkInstrBuffers` take interface arguments, so bsc refuses to give them
their own module:

```
Separate code generation for module `mkLookAhead', which has an interface
argument, is not supported
```

They can only be elaborated inlined into `mkStretchCore`. Consequence:
**the E-box — `StretchExecute.bsv`, the single biggest file — cannot be
size-measured on its own without adding a wrapper module**, which
would be a model change and so was not made. This is why §2.5's
breakdown has a hole exactly where the largest block is. Class **(b)**
if anyone wants that number (a ten-line wrapper), but it is a model
change.

**So: the design compiles to Verilog today, unmodified, in 142 s of
CPU. The interesting failures are all downstream.**

---

## 2. How big is it?

### 2.1 The four ULX3S variants, from the primary source

Lattice **ECP5 and ECP5-5G Family Data Sheet, FPGA-DS-02012-3.4,
September 2025, Table 1.1 "ECP5 and ECP5-5G Family Selection Guide"**
(PDF downloaded during this work, text extracted with
`pdftotext -layout`):

| | LFE5U-12 | LFE5U-25 | LFE5U-45 | LFE5U-85 |
|---|---|---|---|---|
| LUTs (k) | 12 | 24 | 44 | 84 |
| sysMEM blocks (18 kb) | **32** | **56** | **108** | **208** |
| Embedded memory (kb) | 576 | 1,008 | 1,944 | 3,744 |
| Distributed RAM bits (kb) | 97 | 194 | 351 | 669 |
| 18 × 18 multipliers | 28 | 28 | 72 | 156 |
| PLLs/DLLs | 2/2 | 2/2 | 4/4 | 4/4 |

Independent corroboration of the LUT figures from the **Project
Trellis 1.4_9 database installed on this machine**
(`/opt/homebrew/share/trellis/database/ECP5/<dev>/tilegrid.json`,
counting tiles of type `PLC*`; one ECP5 PLC tile = 4 slices = 8 LUT4s):

| device | PLC tiles | × 8 = LUT4s | datasheet |
|---|---|---|---|
| LFE5U-12F | 3,036 | 24,288 | 12 k |
| LFE5U-25F | 3,036 | 24,288 | 24 k |
| LFE5U-45F | 5,481 | 43,848 | 44 k |
| LFE5U-85F | 10,455 | 83,640 | 84 k |

45F and 85F match to rounding. **The 12F and 25F have identical
tilegrids** — same `frames` (7,562), `bits_per_frame` (592),
`max_row` (50), `max_col` (72) in `devices.json`, differing only in
IDCODE (`0x21111043` vs `0x41111043`). The 12F is the 25F die sold at
a lower advertised density. What the open toolchain actually *lets*
you use on a 12F was not determined (§7).

The board: the LiteX platform file
[`litex_boards/platforms/radiona_ulx3s.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/platforms/radiona_ulx3s.py)
accepts exactly `LFE5U-12F`/`25F`/`45F`/`85F` (default 45F) and
declares `default_clk_name = "clk25"`,
`default_clk_period = 1e9/25e6` on pin `G2` — **a 25 MHz oscillator**.
Its `sdram` resource has **16 `dq` bits, 13 `a` bits, 2 `ba` bits**.

### 2.2 Main storage: measured block-RAM cost, per configuration

This is the decisive measurement, and it is a real synthesis result,
not arithmetic. `mkMemoryUnit` and `mkMBCU` were compiled to Verilog
on their own (`bsc -verilog -g mkMemoryUnit -u StretchMemory.bsv`,
likewise `-g mkMBCU`) and run through **`synth_ecp5` with bsc's
`BRAM1.v` included, so yosys had to infer and map the memory itself**:

```
=== mkMemoryUnit ===   (ONE 16384 x 64 unit, standalone)
     DP16KD                         64
     LUT4                          254
     TRELLIS_FF                    215
     TRELLIS_DPR16X4                16
     PFUMX                          82
     L6MUX21                         8
```

**One memory unit = 64 DP16KD.** yosys packs a 16384-deep × 64-wide
array into exactly 64 blocks, i.e. 16 kbit used out of each block's
18,432 bits — as expected, because the x9/x18/x36 modes that would use
the extra 2 kbit are at most 1,024 deep (data sheet §2.8).

**And the six-unit verdict does not depend on yosys's packing choice.**
Perfect packing — every one of an EBR's 18,432 bits used, which no
legal mode allows at this depth — would still need
6,291,456 / 18,432 = 341.3, i.e. **342 blocks minimum, against 208 on
the largest ULX3S.** The measured 384 and the arithmetic floor of 342
both exceed the biggest part, so the conclusion below is forced, not
an artifact of the mapper.

The whole bus-control unit, at the three configurations:

| config | `NumUnits` | `InstalledWords` | **DP16KD** | LUT4 | TRELLIS_FF | DPR16X4 |
|---|---|---|---|---|---|---|
| one unit | 1 | 16,384 | **64** | 7,139 | 670 | 16 |
| two units | 2 | 32,768 | **128** | 3,624 | 885 | 32 |
| **six units (as shipped)** | 6 | 98,304 | **384** | 9,335 | 1,745 | 96 |

DP16KD is exactly 64 × units and TRELLIS_FF is exactly additive
(670 + 215 = 885; 885 + 4×215 = 1,745). **The LUT4 column is not
monotonic — the one-unit build measures *more* LUT4 than the two-unit
build (7,139 vs 3,624). That is a measured anomaly and I did not
chase its cause**; it is most likely a yosys/abc9 artifact in the
degenerate one-element `Vector#(NumUnits, MemoryUnit)` case. It is
flagged rather than smoothed over.

Against the device EBR budgets from §2.1:

| config | blocks needed | 12F (32) | 25F (56) | 45F (108) | 85F (208) |
|---|---|---|---|---|---|
| one unit (16,384 words) | 64 | no | no | **yes** (59%) | **yes** (31%) |
| two units (32,768 words) | 128 | no | no | no | **yes** (62%) |
| **six units (98,304 words)** | **384** | no | no | no | **no (1.85× over)** |

**So, stated plainly: the typical six-unit 7030's core storage does not
fit in block RAM on any ULX3S, by a factor of 1.85, and it is not
close. The smallest ULX3S that holds a one-unit Stretch's storage in
block RAM is the 45F; the 85F holds two units.**

### 2.2.1 What a one-unit machine would actually run — measured

The one-unit configuration is not a toy: **every word the transcribed
diagnostic corpus touches is inside one 16,384-word unit.** Parsing
every listing row across all 186 `stretch/strap/verify_*.py` files
(5,375 `"<octal>.<octal>"` literals) gives word addresses from
**0o100 = 64 to 0o33270 = 14,008**, all below 16,384. (A separate
parse restricted to the leading address column of `ROWS`-style tuples
gives 0o5123 = 2,643 to 0o22347 = 9,447 — same conclusion.)

So a 45F ULX3S could run the whole transcribed corpus with storage
entirely in block RAM and **no SDRAM at all**. That is a genuine
milestone and a sensible first target — but it is not the goal, which
is the typical six-unit machine (§3.1).

Both figures agree with Buchholz's own wording, which is what makes
`NumUnits` a configuration rather than an architectural constant:
*Planning a Computer System* §14.1 says "a **typical** 7030 system
**may** have six memory units" (quoted in `StretchMemory.bsv`'s own
header). Changing it is not a departure from the 7030; it is a
different 7030.

**Cost of changing it:** `NumUnits` and `InstalledWords` are one
`typedef` each, but `unitOf` and `indexOf` hard-code the documented
4-way-then-2-way interleave split at word 65,536:

```bsv
function Bit#(3) unitOf(WordAddr a);
  if (a < 65536) return {1'b0, a[1:0]};
  else return {2'b10, a[0]};
endfunction
```

A one-unit build needs `unitOf = 0`, `indexOf = a[13:0]`; a two-unit
build needs `{2'b00, a[0]}` and `a[14:1]`. That is the whole change —
**four lines, class (b)** — and it is what was done to take the
measurements above (the diffs are in §8; the file is reverted).

### 2.3 Memory subsystem as the core instantiates it

`mkStretchStorage` — the six units, the bus control unit, the 32
special-storage registers and the 16 index registers — standalone:

```
=== mkStretchStorage ===
     DP16KD                        384
     LUT4                       13,427
     TRELLIS_FF                  4,444
     TRELLIS_DPR16X4               118
     CCU2C                          57
     PFUMX                       2,354
     L6MUX21                       187
```

384 DP16KD confirms nothing else in the storage path uses block RAM.
The 13,427 LUT4 is dominated by the seven-channel request/response
routing in `memCtl` and the special-address decode — note that it
already exceeds a 12F's entire LUT budget on its own.

### 2.4 The I/O subsystem

`mkStretchIO` standalone:

```
=== mkStretchIO ===
     LUT4                        8,102
     TRELLIS_FF                  5,317
     PFUMX                       3,351
     L6MUX21                     1,202
     DP16KD                          0
```

5,317 flip-flops is the 5,120 predicted device-image bits plus the
control words. **8,102 LUT4 to index 80 registers** is the measured
price of holding 640 bytes of "card reader, printer and tape" in
flip-flops instead of one block RAM — see §3.6.

### 2.5 Whole-core cell counts: a measured partial, and an honest gap

`synth_ecp5` on the full 102k-line `mkStretchCore.v` **did not
complete.** Two attempts:

- **Run A** (`synth_ecp5` verbatim, BRAM blackboxed): entered the
  `SHARE` pass (SAT-based resource sharing) and was still in it after
  ~25 minutes with a 71 MB log; killed.
- **Run B** (identical, except the `coarse` stage expanded by hand
  from `yosys -p "help synth_ecp5"` with only `share` removed — a
  *measurement* deviation, disclosed): got past `share`, through
  `mul2dsp`, `alumacc`, `memory`, `memory_libmap`, `memory_map`,
  `dfflegalize` and `techmap`, and reached **`ABC9`, the final
  LUT-mapping pass**, where it still was after a further 25 minutes.
  No `stat` was produced. Since ABC9 is the last substantive step,
  **a re-run on an unloaded machine should produce the number**; the
  script is `runB2.ys` in this work's output directory and takes no
  further changes.

At a load average of 100–200 on 16 cores this is starvation as much as
pathology, but either way **there is no measured whole-core LUT4,
TRELLIS_FF, DP16KD or MULT18X18D figure in this note.** What there is:

| measured, standalone | LUT4 | TRELLIS_FF | DP16KD | MULT18X18D |
|---|---|---|---|---|
| `mkStretchStorage` (6 units + MBCU + special regs) | 13,427 | 4,444 | 384 | 0 |
| `mkStretchIO` | 8,102 | 5,317 | 0 | 0 |
| **sum of the two measured parts** | **21,529** | **9,761** | **384** | **0** |
| `mkEBox` (`StretchExecute.bsv`, 5,019 lines) | not measurable without a wrapper module (§1.2) | | | |
| `mkInstrBuffers`, `mkLookAhead`, decode, the core's own rules | same | | | |

Read that carefully: **21,529 LUT4 is the measured cost of two
subsystems that are strictly contained in `mkStretchCore`, and the
largest subsystem — the E-box, with its three 48 × 48 fraction
multipliers at `StretchFP.bsv:713,720,902` — is not in the total at
all.** Standalone synthesis keeps every port of each module live, so
the flattened core could optimise some of it away; equally, the core
adds everything that is missing. The sum is an indication, not a
bound in either direction.

What it does support, with real numbers:

- **The 12F (12 k LUTs) is out.** Two subsystems alone measure 21,529
  LUT4, and `mkStretchStorage` alone measures 13,427.
- **The 25F (24 k LUTs) is very unlikely**: 21,529 of 24,288 before
  the E-box. It is also already excluded on block RAM for any
  configuration (§2.2).
- **The 45F (44 k) is the plausible floor, the 85F (84 k) the safe
  choice** — and the 85F is the only part that holds even two memory
  units in block RAM, and the only one with 4 PLLs and 156
  multipliers for the FP unit. For a six-unit machine the 85F is the
  answer on every axis except block RAM, where no part works.

### 2.6 Place and route: unavailable, and here is the exact reason

```
$ nextpnr-ecp5 --version
dyld[62353]: Library not loaded: /usr/local/opt/boost-python3/lib/libboost_python38-mt.dylib
  Referenced from: /usr/local/bin/nextpnr-ecp5
```

This is **not** a `brew reinstall` away. `file` reports
`Mach-O 64-bit executable x86_64` — an Intel-Homebrew (`/usr/local`)
binary on an arm64 machine — and `otool -L` shows it wants:

```
/usr/local/opt/boost-python3/lib/libboost_python38-mt.dylib
/usr/local/opt/boost/lib/libboost_{filesystem,thread,program_options,iostreams,
                                   system,chrono,date_time,atomic,regex}-mt.dylib
/usr/local/opt/qt/lib/Qt{OpenGL,Widgets,Gui,Core}.framework/Versions/5/...
/usr/local/opt/python@3.8/Frameworks/Python.framework/Versions/3.8/Python
```

`ls /usr/local/opt` contains exactly one entry (`trilinos`): the Intel
Homebrew prefix this binary belonged to is gone. It is the Qt5 GUI
build against Python 3.8 and Boost.Python 3.8, neither of which
exists here. `brew info nextpnr-ecp5` → *"No available formula with
the name nextpnr-ecp5"* (only `nextpnr-ice40` is a formula). No
`oss-cad-suite` (`ls ~/oss-cad-suite /opt/oss-cad-suite`,
`brew list --cask | grep oss` — nothing);
`find / -maxdepth 4 -name 'nextpnr-ecp5*'` finds only the broken one.

An arm64 source build against the Homebrew `boost 1.89` and the
installed `prjtrellis 1.4_9` database is the only revival path. It was
not attempted — the task caps the time, and more to the point there is
currently **no placeable six-unit design to route**: nextpnr would
reject the netlist on 384-vs-208 EBR before saying anything about
timing.

**Therefore every number in §2.2–§2.5 is a yosys cell count: a
pre-place-and-route figure, not a routing result, and it says nothing
about timing closure.** The maximum clock the design closes at was not
measured and could not be (§7) — which is a pity, because it is the
one number that would settle §3.4.

---

## 3. What a real ULX3S bring-up would need

Almost none of it is the CPU.

### 3.1 Six units must live in SDRAM — and the emulated machine is slow enough that it works, at a specific SDRAM clock

Capacity is a non-issue: 6.29 Mbit = 768 KiB against 32 MB of
SDRAM, i.e. 2.3%. The question is latency and concurrency.

**The arithmetic, checked.** The model defines one Bluespec clock as
one 7030 machine cycle = **0.3 µs** (`StretchMemory.bsv` header,
citing *7030 Performance Characteristics* vol. 1 p. 3-2, "the basic
machine cycles, which is presently 0.3 microsecond"). So:

| | at a 3.333 MHz core clock | at a 25 MHz core clock |
|---|---|---|
| one model clock | 300 ns | 40 ns |
| `memReadClocks = 5` (1.6 µs read-out) | 1,500 ns | 200 ns |
| `memCycleClocks = 7` (2.1 µs core cycle) | 2,100 ns | 280 ns |
| 2.1 µs in 50 MHz SDRAM clocks | **105** | **14** |
| 2.1 µs in 100 MHz SDRAM clocks | **210** | **28** |

Note which window actually binds: it is **`memReadClocks = 5`, the
1,500 ns read window at 3.333 MHz**, not the 7-clock busy window.
Data must be presented 5 model clocks after the request; the extra two
clocks are regeneration during which the unit merely refuses new work.

**The arrival rate, which is what makes this tractable.** Two
structural facts from the model, not estimates:

- `memCtl` (`StretchStorage.bsv:323`) sets `busUsed` and issues **at
  most one memory request per model clock** — so requests reach memory
  no faster than one per 300 ns.
- each unit accepts one request per `memCycleClocks = 7` — so **at
  most six requests per 2,100 ns**, i.e. one per 350 ns sustained.

So the back end does not have to serve six simultaneous accesses in
one window; it has to sustain one 64-bit word every 350 ns and deliver
each within 1,500 ns of its own request. Sized against the actual
controller in §3.2 (counted from its FSM, not assumed):
~27 SDRAM clocks for a 64-bit word with the row open, ~32 with a
precharge first.

| SDRAM clock | service time / 64-bit word | sustainable at 350 ns? | worst queueing latency vs. 1,500 ns |
|---|---|---|---|
| 50 MHz | 540–640 ns | **no** | — |
| 100 MHz | 270–320 ns | **yes, marginally** (320 < 350) | ≈ 420 ns + refresh ≈ 570 ns — **passes, 2.6× margin** |
| 166 MHz (the part's rating) | 163–193 ns | **yes, comfortably** | ≈ 250 ns + refresh ≈ 340 ns — **passes, 4.4× margin** |

(The queueing figure is the standard single-server calculation with
300 ns inter-arrivals: request *k* starts at
max(arrival, previous finish), so the queue builds to at most six
during a burst and drains inside the unit's own 2,100 ns cycle.
Refresh is one `tREF` row every 7.8 µs, ~15 controller clocks.)

- **At 3.333 MHz the design works with a 100 MHz SDRAM clock and has
  real margin at 166 MHz.** 50 MHz — LiteX's ULX3S default — is
  **not** sufficient with a non-bursting controller.
- **At 25 MHz the core needs a 64-bit word every 42 ns sustained**
  (one per model clock) and each delivered inside 200 ns. No SDR SDRAM
  on a 16-bit bus does that: 4 × 16 bits at 166 MHz is 24 ns of pure
  data transfer before any overhead. **A 25 MHz core clock is not
  feasible with this memory system.** That is the clearest reason to
  prefer the architecturally correct clock, and it is a measured
  reason rather than a stylistic one.
- **A burst-capable controller changes the picture substantially**: one
  ACTIVATE plus one burst-of-4 READ is ~9–12 clocks for a 64-bit word
  instead of 27–32, which makes 50 MHz sufficient. LiteDRAM and
  EMARD's `sdram_16bit` burst; `ulx3s_bsv`'s `Sdram.bsv` does not
  (§3.2). **If the SDRAM clock has to stay low, the controller must
  burst; if the controller cannot burst, the SDRAM clock must be
  ≥ 100 MHz.** Pick one deliberately.

**Recommendation: run the core at 3.333 MHz.** Reasons, in order:

1. It is the only configuration in which the timing model is
   *literally* true rather than proportionally true — one model clock
   is one machine cycle, so `memCycleClocks = 7` means 2.1 µs on the
   bench, and `StretchTiming.bsv`'s per-instruction budgets are
   wall-clock-correct. For a project whose stated goal is a
   cycle-accurate recreation, that is worth more than speed.
2. It is the configuration with enough slack that the SDRAM interposer
   can be *proved* to meet the contract rather than measured to
   usually meet it (§3.3).
3. It makes timing closure a non-issue: 300 ns per path on a part
   whose LUT delay is ~0.3 ns. Even a design that only closes at
   15 MHz is 4.5× faster than it needs to be — which is why §2.6's
   missing Fmax number, while a real gap, is probably not a real risk.
4. 25 ÷ 7.5 = 3.3333 MHz is awkward for a counter but trivial for an
   `EHXPLLL`.

The cost is that the machine runs at 7030 speed, so a program that
took a minute on real iron takes a minute on the board. That is
arguably the point — and in any case **the measurement above says the
25 MHz alternative is not actually on the table once storage is in
SDRAM.** A faster-than-Stretch Stretch is only available in the
one-unit BRAM configuration (§2.2.1), where memory is on-chip and the
core clock is limited by nothing but timing closure. That is one more
reason the one-unit build is a useful stepping stone and not a
consolation prize: it is the only configuration in which "how fast can
this thing go" is even a question. Whatever is chosen, make the core
clock a build parameter and write the choice down, rather than leaving
it a silent assumption.

### 3.2 The SDRAM driver: not Flute. There is a better one, and it is for this board.

> **CORRECTION, and it is the useful kind.** The sweep below is of the
> **upstream** `bluespec/Flute` on GitHub, and for that repository it
> is correct and exhaustive. It is also beside the point: the user
> said they had a Flute with an SDRAM driver, and they do —
> `~/src/ulx3s-experiments/flute-ulx3s/src/Sdram_Controller.bsv`, 434
> lines, a local fork, read first-hand and written up in
> `docs/sdram_local.md`. **A confident negative about something the
> user says they have is evidence the search is aimed wrong**, not
> evidence they are mistaken; this one was aimed at the wrong
> repository, as §2.6's nextpnr negative was aimed at the wrong depth.
> The paragraph is left standing because what it proves about upstream
> is still true and still worth knowing.

**`bluespec/Flute` has no SDRAM driver, and this was checked
exhaustively rather than by looking in the likely place.** The
repository's complete file list was fetched
(`api.github.com/repos/bluespec/Flute/git/trees/HEAD?recursive=1`):
**1,922 paths, `"truncated": false`.** Matching every path against
`sdram|sdr|dram|phy|ddr`, case-insensitively, yields **eight hits, none
of them a memory controller**:

```
Tests/isa/rv32mi-p-ma_addr          Tests/isa/rv32mi-p-ma_addr.dump
Tests/isa/rv32mi/ma_addr.S          Tests/isa/rv64mi-p-ma_addr
Tests/isa/rv64mi-p-ma_addr.dump     Tests/isa/rv64mi/ma_addr.S
src_Core/Near_Mem_VM_WB_L1_L2/src_LLCache/procs/lib/MMIOAddrs.bsv
src_Testbench/Fabrics/AXI4/AXI4_Addr_Translator.bsv
```

— six misaligned-address ISA tests and two files whose names merely
contain "Addr". For completeness: `src_Testbench/SoC/` holds
`Mem_Controller.bsv`, `Boot_ROM.bsv`, `UART_Model.bsv`, `Timer.bsv`,
`SoC_Fabric.bsv`, `SoC_Map.bsv`, `SoC_Top.bsv`,
`External_Control.bsv`, `AXI4_Accel_IFC.bsv` —
`Mem_Controller.bsv` is an AXI4-attached memory *model* — and all
twenty entries under `builds/` are `bluesim`, `iverilog` or
`verilator`. There is no FPGA build in the repository at all. Flute's
real-hardware memory comes from vendor DDR controllers in separate
projects (AWSteria/Catamaran), not from anything portable to an ECP5.
**So "pull in Flute's SDRAM driver" names a component that does not
exist, and the plan needs re-pointing.**

**What does exist, and is a much better fit:
[`sangwoojun/ulx3s_bsv`](https://github.com/sangwoojun/ulx3s_bsv)** —
"Bluespec environment for working with the ulx3s board and its lattice
ecp5 fpga", with "UART, Mult18x18D, PLL, SDRAM access imported to
Bluespec". Its `src/` is:

```
BRAMSubWord.bsv  Mult18x18D.bsv  PLL.bsv  Sdram.bsv
SimpleFloat.bsv  Top.bsv  Uart.bsv  ulx3s_bsv.lpf
```

`src/Sdram.bsv` was downloaded and read directly (313 lines; the
quotations below are from the file, not from a summary). It is
**written in BSV, not a BVI import of a Verilog core**:

```bsv
interface Ulx3sSdramUserIfc;
	method Action req(Bit#(24) addr, Bit#(16) data, Bool write);
	method ActionValue#(Bit#(16)) readResp;
endinterface

module mkUlx3sSdram#(Clock sdram_clk, Integer clock_mhz) (Ulx3sSdramIfc);
```

with timing constants

```bsv
Bit#(4) delay_tRP = 3;   Bit#(4) delay_tMRD = 2;
Bit#(4) delay_tRCD = 3;  Bit#(4) delay_tRC = 9;
Bit#(4) delay_CL = 3;
Integer rf_cycles  =   clock_mhz * 78 / 10;
```

(a refresh every 7.8 µs, correct for this part), a pin interface of
`Bit#(13) sdram_a`, `Bit#(2) sdram_ba`, `Bit#(2) sdram_dqm` and
`Inout#(Bit#(16)) sdram_d` — matching the LiteX platform file's
13/2/16 exactly — and a `reqQ`/`readRespQ` FIFO pair around a
seven-state FSM (`IDLE, REFRESH1, REFRESH2, CONFIG, RDWR, READREADY,
WAIT`) with open-row tracking per bank (`open_bank`, `open_rows`).

**Three things follow from reading it, and they drive §3.1's
arithmetic.** First, 16-bit data and a 24-bit address = 16 M × 16 =
the board's 32 MB. Second, **it does not burst**: one `req` moves one
16-bit half-word, so a 64-bit Stretch word is four round trips. Third,
counting its own FSM — `IDLE` dequeue (1) + `RDWR` issue (1) +
`WAIT` for `delay_CL` (3) + `READREADY` (1) ≈ **6 controller clocks per
16-bit read with the row open**, plus `delay_tRCD` (3) for an
ACTIVATE on a closed bank, plus `delay_tRP` (3) for a row conflict.
Hence **~27 clocks per 64-bit word with the row open, ~32 with a
precharge**, which is the number §3.1 is sized against.

It also carries an honest caveat on line 8 of its own source:
`// TODO clock either needs to be shifted, or commands need to be held
for longer` — so the clock-phase work (EMARD's `sdram_pnru_*` and
`sdram_pnru_68k_180deg` variants exist precisely because phase matters
on this board) is not done for you.

That repository is the whole bring-up kit, not just the SDRAM: a
`PLL.bsv` for §3.4, a `Uart.bsv` for §3.5, a `ulx3s_bsv.lpf` for the
pin constraints this project has none of, and a `Top.bsv` to copy. It
is the single highest-leverage thing to read before starting.

Other options, for the record:

- **LiteDRAM via LiteX.**
  [`litex_boards/targets/radiona_ulx3s.py`](https://github.com/litex-hub/litex-boards/blob/master/litex_boards/targets/radiona_ulx3s.py)
  builds a working ULX3S SoC: `GENSDRPHY` (or `HalfRateGENSDRPHY` for
  `--sdram-rate 1:2`), `self.add_sdram("sdram", phy=self.sdrphy,
  module=...)` with `MT48LC16M16` by default (`AS4C32M16`,
  `AS4C16M16` as options), `sys_clk_freq = 50e6`, all four device
  variants. Brings UART, bootloader and a wishbone fabric with it.
  The cost is adopting LiteX/Migen as a build dependency and a
  wishbone↔Stretch adapter; the benefit is that everything in §3.4
  and §3.5 comes free and already works on this board.
- **EMARD's hand-written controllers**, in
  [`emard/ulx3s-misc/examples/sdram`](https://github.com/emard/ulx3s-misc/tree/master/examples/sdram):
  ten variants — `sdram_16bit`, `sdram_ctrl`, `sdram_fpga`,
  `sdram_mist`, `sdram_mistery`, `sdram_pnru`, `sdram_pnru_68k`,
  `sdram_pnru_68k_180deg`, `sdram_pnru_99k`, `memtest_mister`
  (listing read from the GitHub API during this work). Verilog/VHDL,
  smaller and more predictable than LiteDRAM — which matters when the
  requirement is a *latency bound*, not throughput. `memtest_mister`
  in particular is the thing to run first on the actual board.
- **Project Trellis ships no memory controller.** It is a bitstream
  database plus `ecppack`. The answer to "does one exist in Project
  Trellis" is **no, and that is not what Trellis is.**

### 3.3 The interposer: concurrency is the design problem, not bandwidth

The thing that must survive is not throughput, it is that
`StretchMemory.bsv` models **six units that are independently busy**.
That independence is the whole point — Buchholz §14.1: "four
consecutive word addresses lie in four different memory units" — and
it is what the four-level look-ahead has to overlap against. Collapse
six units onto one channel naively and `free()` becomes a global
mutex: the look-ahead stops overlapping, and every `CYCLES<=` bound
in the suite shifts.

The shape that preserves it, and it is a small shape:

- **Keep `mkMemoryUnit` exactly as it is, minus the BRAM.** It already
  *is* the model of an independently busy unit: `busy`, `readDue`,
  `tagReg`, and the `free()`/`dataReady()` handshake. Six instances
  keep six independent busy counters. Nothing about `mkMBCU`'s
  priority scheme or `mkStretchStorage`'s seven channels needs to
  change.
- **Replace each unit's `BRAM1Port` with a port on a shared SDRAM
  scheduler.** A unit issues one request per 7 model clocks; six units
  issue at most six requests per 7 model clocks = 2,100 ns. The
  scheduler is a 6-deep request queue plus a 6-slot response store,
  running in the SDRAM clock domain, that must deliver each 64-bit
  word (4 × 16-bit) within the 5-model-clock read window. §3.1's
  arithmetic says the queue is stable and the window is met at
  **100 MHz with a 2.6× latency margin, 166 MHz with 4.4×, and not at
  all at 50 MHz with a non-bursting controller.** That is a
  configuration choice to be made deliberately, and it is the
  worst-case figure §3.3 exists to pin down — but it is still derived
  from the controller's own FSM constants, not from a timing report on
  real silicon (§7).
- **The per-unit busy counts stay honest because they are still
  counters in the model**, not measurements of the SDRAM. The
  scheduler's job is to make the counters' promise true, not to
  replace them. That is exactly the right division: the timing model
  stays declarative and sourced, and the hardware is held to it. If
  the scheduler ever *cannot* meet the window, the honest response is
  a visible overrun counter, not a silent stall — a status bit a test
  can read, in the spirit of the model's "fail loud, never silently"
  convention.
- **The address map is trivial**: `unit × 16384 + index` words, × 4 for
  16-bit granularity = 393,216 SDRAM half-words for all 98,304 Stretch
  words, well inside `Bit#(24)`.
- **Cycle accuracy survives, and this is the key claim.** A 2.1 µs
  emulated core cycle with a 150 ns physical access inside it is not
  an approximation — the physical memory finishes early and waits.
  The model's timing is the authority; the SDRAM is merely fast enough
  not to be noticed. `CYCLES<=` bounds and the interruption-boundary
  work are unaffected *provided* the window is never missed, which is
  why the worst-case proof is the deliverable, not a benchmark.

Class **(c)** — a real redesign of `StretchMemory.bsv`'s back end —
but a well-bounded one, and much less frightening than it looked
before the clock arithmetic was done.

### 3.4 Clocking

25 MHz in on pin `G2`. One `EHXPLLL` (2 PLLs on 12F/25F, 4 on
45F/85F) producing an SDRAM clock (50–100 MHz) and a 3.3333 MHz core
clock, plus the phase-shifted SDRAM clock `Sdram.bsv`'s own TODO asks
for. `ulx3s_bsv`'s `src/PLL.bsv` already wraps `EHXPLLL` for
Bluespec. The generated `mkStretchCore` is single-clock (`CLK`,
`RST_N`) with no clock-domain-crossing primitives in it, so the
interposer of §3.3 owns the system's only domain crossing. **Class
(b)**, a day or two.

### 3.5 Nothing in the repository targets a board, and the testbench cannot be ported — only replaced

There is no `.lpf`, no board top-level, no PLL, and no
`yosys`/`nextpnr`/`ecppack` rule anywhere in `stretch/`. `bsv/Makefile`
has three targets (`sim`, `run`, `clean`), all Bluesim. The whole FPGA
flow is new work.

How the model is driven today (`strap/gen_tb.py`): a phase counter and

1. `rule load` calls `core.mem.writeWord(addr, 64'h…)` **once per
   phase**, one program word per clock, for every word of the image;
2. optional `rule loadReader` / `rule loadTape` into
   `core.io.loadReaderWord` / `core.io.writeTapeWord`;
3. `core.setPC(end_pc)`;
4. `rule run (… && !core.halted() && stepCount < cap) core.step()`;
5. `rule afterRun` compares `core.mem.readWord(addr)` and
   `core.io.readPrinterWord(i)` against expected values, and the halt
   PC.

Every one of those is a method on the synthesised boundary, and they
are all still there in the Verilog. Counting port declarations in
`mkStretchCore.v`: **129 top-level ports — 75 outputs and 54 inputs**,
many 64 bits wide: `CLK`, `RST_N`, `EN_step`/`RDY_step`, `halted`,
`getPC`, `setPC_a`, then the entire `mem` and `io` test
sub-interfaces (`mem_writeWord_{a,v}`, `mem_readWordReq_a`,
`mem_readWordResp`, `mem_fetchReq/Resp`, `mem_laReq/Resp`,
`mem_readIndex_j`, `mem_snapshotIndex`, `mem_restoreIndex`,
`io_loadReaderWord_*`, `io_readPrinterWord_*`, `io_readTapeWord_*`, …).

**On a board none of those has a driver.** What replaces the
testbench:

- **UART, and it is the right answer.** The FT231X gives a USB-serial
  link (EMARD's `doc/MANUAL.md` names the part; the board's published
  spec advertises 3 Mbit USB-serial and 500 kbit JTAG), and
  `ulx3s_bsv/src/Uart.bsv` already imports it into Bluespec. A
  receive FSM that takes address/word pairs and drives
  `mem_writeWord`, plus a transmit side for
  `readWord`/`getPC`/`halted`, makes `gen_tb.py`'s phase machine map
  almost one-for-one onto a serial command protocol — **which is the
  only path by which the existing 389-section corpus becomes a
  hardware regression suite.** Class (b) individually; load-bearing.
- **Boot ROM in EBR.** Bake one program into the bitstream (bsc ships
  `BRAM1Load.v`, unused by this model) and copy it to storage with a
  small FSM. Fine for a demo, a bitstream rebuild per program.
  Class (b).
- **LiteX.** Wrap `mkStretchCore` as a LiteX module and the UART,
  SDRAM, clocking, bitstream build and a host-side `litex_term`
  loader all arrive working on this exact board. Class (b)+(c).
- **The ESP32.** EMARD's manual: it "can provide standalone web
  interface for uploading bitstream into FPGA and its config FLASH" —
  a *bitstream* loader, no help for poking storage without an extra
  ESP32↔FPGA SPI link. Not the short path.
- **JTAG.** The ECP5 has a user-accessible `JTAGG` primitive and
  `openFPGALoader`/`ujprog` can reach it, but Bluespec supplies no
  debug module and this project has no JTAG infrastructure. **Class
  (c)**, most work for least immediate return.
- **Observation, cheaply.** `halted` is one bit and can drive an LED,
  so "did it halt" is nearly free; the eight user LEDs can show part
  of `getPC`. "Halted at the right PC with the right words in storage"
  needs the readback path.
- **The test ports themselves.** Either the loader drives them (so
  they stay) or they are dead ports yosys prunes, taking a lot of mux
  logic with them. §2.3/§2.4's counts include all of them, which is
  part of why the sums look large.

### 3.6 Does `StretchIO.bsv` mean anything on hardware? Partly.

Measured in §2.4: 8,102 LUT4 and 5,317 flip-flops of "card reader,
printer and tape", with no device behind them.

- **It still works** — an RD from channel 32 returns whatever was
  loaded into `readerImg`, a W to channel 33 lands in `printerImg`, so
  I/O test programs run and can be checked through the same readback
  path as storage. The I/O model is not broken by hardware; it is a
  simulation now running on an FPGA.
- **Making it mean something** — printer on the UART, tape on the
  micro-SD card the board has — is a new subsystem, not a port.
  `StretchIO.bsv`'s header explains that real file I/O was avoided
  because `$fopen`/`$fgetc` are Actions; the hardware equivalent is an
  SD-card block driver. **Class (c), and optional** — nothing in the
  CPU depends on it.
- **One concrete hardware win**: the device images are registers. All
  three (80 words = 640 bytes) fit in **one** DP16KD. Converting them
  would shed most of that 8,102 LUT4 and 5,317 FF. **Class (b)**, and
  worth doing — it is the cheapest large utilisation saving visible in
  any of these measurements.

---

## 4. Effort estimate, broken into pieces

Each item is engineer-days for someone already fluent in this codebase
and in the ECP5 open flow. "Critical?" means: on the path to *the
typical six-unit machine running a program on a ULX3S with results
observable*.

| # | piece | class | days | critical? |
|---|---|---|---|---|
| 1 | Verilog generation | — | **0 — done and measured (§1)** | — |
| 2 | Revive `nextpnr-ecp5`: install `oss-cad-suite` (prebuilt darwin-arm64, chipdbs included) or build arm64 from source against Homebrew boost 1.89 + the installed `prjtrellis 1.4_9` | — | 0.5–2 | yes — nothing routes without it |
| 3 | Board wrapper: `ulx3s_bsv`'s `.lpf` adapted, `EHXPLLL` for 25 MHz → ≥100 MHz SDRAM clock + 3.3333 MHz core clock + the phase-shifted SDRAM clock, `yosys`/`nextpnr`/`ecppack` Makefile rules | (b) | 2–3 | yes |
| 4 | **Finish the whole-core synthesis measurement** that did not complete here (§2.5), on a quiet machine, and add the `mkEBox` wrapper needed to size the E-box and count `MULT18X18D` | (b) | 0.5–1 | yes — it decides 45F vs 85F |
| 5 | **SDRAM back end**: replace each `mkMemoryUnit`'s `BRAM1Port` with a port on a shared scheduler over `Ulx3sSdramUserIfc` (or a bursting controller), keeping the six busy counters; worst-case-latency proof; a Bluesim model of the scheduler so the existing suite still passes unchanged | **(c)** | **8–15** | yes |
| 6 | UART loader/observer: receive FSM driving `mem_writeWord`/`setPC`/`step`, transmit side for `readWord`/`getPC`/`halted`, a readable cycle counter (§6), and a host-side runner replacing `gen_tb.py`'s phase machine with a serial protocol | (b) | 5–8 | yes |
| 7 | Re-verification: the FPGA build gives the same answers as Bluesim on a meaningful subset of the 389-section suite, including `CYCLES<=` bounds | — | 3–5 | yes |
| 8 | **Stepping stone, worth doing first**: one-unit BRAM build on a 45F — item 3 + a four-line `StretchMemory.bsv` change (§2.2) + a baked-in boot ROM + LED on `halted`. Runs the entire transcribed corpus (§2.2.1) with no SDRAM at all. | (b) + a documented configuration change | 2–4 | no, but it de-risks everything after it |
| 9 | Alternative to 5+6: adopt LiteX as the SoC wrapper (bursting LiteDRAM, UART, clocking, bitstream, host loader, all already working on this board) and write only the adapter — which is the same bounded-latency interposer item 5 needs | (b)+(c) | 6–12 | — (replaces 5+6) |
| 10 | Move `StretchIO`'s three device images from 5,317 flip-flops into one DP16KD (§3.6) | (b) | 1 | no — but it is the cheapest large utilisation saving measured here |
| 11 | Real I/O devices (SD card as tape, UART as printer/console) | (c) | 10+ | no |
| 12 | Console / front panel (§5) | (c) | 10+ | no |

- **Shortest path to first light** (items 2, 3, 8): **3–7 days**, and it
  is a 16,384-word Stretch on a 45F running the real diagnostic corpus
  from a baked-in image, with an LED for "halted". A demo with real
  provenance.
- **Shortest path to the typical six-unit machine, verified against
  Bluesim** (items 2–7): **20–35 days**, dominated by item 5.
  Via LiteX (items 2, 3, 4, 7, 9): **13–24 days**, at the cost of a
  new build dependency.
- **A usable machine that boots systems software** is item 11 and 12
  plus the interrupt and channel work in §5, which is not a hardware
  estimate and is not attempted here.

All of this assumes item 4 comes back showing the core fits a 45F or
85F. If it does not, add a partitioning effort that is not estimated
here.

---

## 5. From here to a machine someone could boot and use

Limited to what the hardware and the code support; everything else is
flagged as outside what was looked at.

**What exists and would work on a board today:** the CPU — instruction
unit with 1Y/2Y, the four-level look-ahead with branch guessing, the
E-box, the interruption mechanism, 98,304 words of storage, and a
halt signal. That synthesises (§1) and, with §3.1–§3.5 done, executes
the transcribed diagnostic corpus.

**What stands between that and a usable machine, from the hardware
side:**

1. **No console.** A 7030 operator sits at a console with an interval
   timer, indicator lights, address switches and a typewriter. The
   model has `getPC`, `halted`, the indicator register at word 11 and
   the interval timer at word 1 — the *state* a console displays
   exists; the console does not. The board offers 8 LEDs, an OLED
   header and HDMI/DVI output (EMARD's board features list), so a real
   front panel is buildable, but it is a project of its own and
   nothing in `stretch/` points at it.
2. **No loader, so no "run a program".** §3.5. Today a program is
   compiled into a generated testbench. On a board, "load a deck and
   press start" needs the UART protocol to exist.
3. **`StretchIO.bsv` drives nothing real.** §3.6. For systems
   software this is the binding gap, not a cosmetic one: an operating
   system needs a console device, a tape or disk to load from, and a
   printer. The model has register-backed stand-ins for reader,
   printer and tape, and the file header is explicit that chaining,
   multiple-block operation, `LOCATE`, and genuine CPU/IO overlap are
   not implemented. **An OS that drives channels asynchronously will
   not run against a synchronous one-word-per-clock transfer model.**
4. **No interrupt system to speak of.** `StretchIO.bsv`'s header says
   the indicator bits it would set (`ind_EPGK`, `ind_UK`, `ind_EE`,
   `ind_EOP`, `ind_CS`) are "NOT propagated", and `bsv/README.md`
   puts the interrupt system out of scope. `StretchStorage.bsv` does
   have `intDueCalc` computing the effective interruption address from
   indicators ∧ mask, so the mechanism is started. Systems software is
   mostly interrupt handling, so this is on the critical path to MCP
   and is not a hardware problem at all.
5. **No disk.** The 7030's systems software loads from the 7612 disk
   synchroniser; the model has a 16-word tape. The board has micro-SD.
6. **Cycle accuracy is charged-time, not structural** — see §6, which
   is the one place where the hardware view has something to say that
   the simulation view does not.

Not looked at, and deliberately left for the roadmap: what MCP
actually requires of the machine, how much of the ISA is still
unimplemented, and whether any MCP image survives.

---

## 6. What cycle accuracy would need from the hardware that ISA-level does not

A synthesis-side view, offered because it changes what the FPGA is
for.

`StretchTiming.bsv` is a **charged-time** model: `iboxCycles`,
`eboxClocks` and `budgetClocks` are tables of per-instruction clock
counts taken from IBM's *Performance Characteristics* and Blosk's
figures, and `StretchCore.bsv` spends them. `StretchMemory.bsv` is
different in kind — `busy`/`readDue` are structural, a real counter
making a real unit unavailable, and the look-ahead genuinely overlaps
against it. So the model is already a hybrid: structural where the
7030's parallelism lives, charged where the arithmetic units' internal
timing lives.

What hardware adds, and what it does not:

- **Hardware does not make charged time structural.** Putting a table
  lookup on an FPGA yields a table lookup. A 48 × 48 multiplier mapped
  to `MULT18X18D`s has its own real latency, and the model currently
  overrides that with a budget from a table. On hardware those two
  numbers can *disagree* — the physical multiplier may finish in 3
  clocks while the table charges 8. The model will still be right
  (it is charging IBM's number) but the FPGA will be doing something
  structurally different from a 7030's serial arithmetic unit. **That
  is fine, and should be said out loud rather than discovered.**
- **Hardware does make one thing honest that simulation cannot**: a
  structural SAU/PAU — the serial arithmetic unit actually taking a
  cycle per byte because it actually processes a byte per cycle — is
  *cheaper* on an FPGA than the combinational E-box the model has
  today. A byte-serial datapath is small; a 5,019-line combinational
  one is 100k lines of Verilog. The idiomatic-Bluespec rewrite
  (`AGENTS.md`, plan §1c) and the FPGA both want the same thing: a
  multi-cycle box with a request/response interface. **The FPGA is an
  argument for finishing that rewrite, not an extra task alongside
  it.**
- **What cycle accuracy needs from the board** is narrow and already
  identified: a core clock whose period *is* the machine cycle (§3.1's
  3.333 MHz recommendation), and a memory back end that cannot be
  late (§3.3). Nothing else about the hardware bears on it.
- **What hardware takes away** is the free observability the testbench
  has. `CYCLES<=` bounds work in Bluesim because `gen_tb.py` counts
  `step()` calls. On a board nobody counts them unless a cycle
  counter is built and made readable — so a cycle counter register is
  not optional instrumentation, it is **the** instrument, and it
  belongs in the first UART protocol (§3.5).

Note for the record: `bsv/README.md`'s Scope section currently
disclaims cycle accuracy. Nothing measured here contradicts that —
this section is about what the hardware would demand if the goal is
pursued, not a claim that it is met.

---

## 7. What could not be determined

- **Whole-core cell counts.** `synth_ecp5` on the 102k-line
  `mkStretchCore.v` did not finish (§2.5): once in the SAT-based
  `share` pass, once (share removed) in the following `opt`, under a
  load average of 100–200. **There is no measured whole-core LUT4,
  TRELLIS_FF, DP16KD or MULT18X18D number in this note.** The
  subsystem measurements in §2.2–§2.4 are real; the total is not.
- **The E-box's size**, specifically, and therefore the
  `MULT18X18D` count for the three 48 × 48 fraction multipliers at
  `StretchFP.bsv:713,720,902`. `mkEBox` takes interface arguments, so
  bsc will not give it its own module (§1.2) and a wrapper would be a
  model change. This is the largest single hole in §2.
- **Whether the design places and routes, and its maximum clock.**
  **ANSWERED IN §9, AND THE ANSWER IS NO: nothing places.** The
  one-unit core is at 826% `TRELLIS_COMB` on a 45F and 433% on an
  85F, so Fmax does not exist to be measured and the 3.333 MHz target
  is moot until the logic gap closes. `nextpnr-ecp5` was never
  unrecoverable (§9.0). What follows was the plan when this was still
  open, and the cheapest way to get it was
  `oss-cad-suite`, which ships a prebuilt darwin-arm64
  `nextpnr-ecp5` with chipdbs.
- **Why the one-unit MBCU measures more LUT4 than the two-unit one**
  (7,139 vs 3,624, §2.2). Measured, not explained.
- **Whether the open toolchain lets a 12F use the full 25F die.** The
  Trellis tilegrids are identical (§2.1); what `nextpnr-ecp5 --12k`
  does with that was not checked, because nextpnr does not run here.
- **Worst-case SDRAM read latency measured on real hardware.** §3.1's
  27/32-clock service time is counted from `ulx3s_bsv/src/Sdram.bsv`'s
  own FSM and delay constants, and the queueing figures from the
  model's own one-request-per-clock issue rate — so they are derived,
  not guessed, but nothing was run on a board and no controller
  timing report was consulted. In particular the SDRAM part's
  `tRC`/`tRFC` in nanoseconds (as opposed to the controller's
  clock-count approximations) were not checked against the specific
  chip fitted, and the board ships at least three different parts
  across revisions (§3.1).
- **Whether a 100–166 MHz SDRAM PHY closes timing on a -6 speed-grade
  ECP5**, which §3.1's conclusion depends on. Needs nextpnr (§2.6).
- **Whether the 389-section suite is runnable over a serial link in
  acceptable time.** Needs image sizes, per-section clock counts (the
  model reports them) and a protocol throughput figure. Not computed.
  `strap/run_tests.sh` was not run, per the task's instruction.
- **Power**, and whether an 85F at this utilisation fits the board's
  USB budget. Not investigated.
- **How much of §2.3/§2.4's logic is the 129 test ports.** Measuring
  it needs a wrapper exposing only `step`/`halted`/`getPC` — a model
  change, so not made.
- **Anything about MCP**: its requirements, its availability, or what
  fraction of the ISA it needs. Outside what was looked at.

---

## 8. Local changes made to the repository

`git status` is clean apart from this file. **No model change was
needed to generate Verilog or to take any §2.3–§2.5 measurement.**

Two temporary edits were made to `bsv/StretchMemory.bsv` **solely to
measure the one- and two-unit configurations in §2.2**, and both were
reverted (`git status --porcelain` shows only
`?? stretch/docs/fpga_feasibility.md`). They are not part of any
recommendation. For the record, the one-unit edit was:

```diff
-typedef 6     NumUnits;
+typedef 1     NumUnits;
-typedef 98304 InstalledWords;
+typedef 16384 InstalledWords;

 function Bit#(3) unitOf(WordAddr a);
-  if (a < 65536) return {1'b0, a[1:0]};
-  else return {2'b10, a[0]};
+  return 0;
 endfunction

 function UnitIndex indexOf(WordAddr a);
-  if (a < 65536) return a[15:2];
-  else begin
-    Bit#(18) rel = a - 65536;
-    return rel[14:1];
-  end
+  return a[13:0];
 endfunction
```

and the two-unit edit was the same with `NumUnits = 2`,
`InstalledWords = 32768`, `unitOf = {2'b00, a[0]}` and
`indexOf = a[14:1]`.

All build products (the generated Verilog, the yosys logs and stats,
the downloaded data sheet) were written outside the repository.


## 9. Place and route, Fmax, and the MBCU anomaly — the measurements §7 could not take

*Appended 2026-10-16 to a copy of `docs/fpga_feasibility.md`. This
section does not modify §1–§8; where it corrects them it says so
explicitly. Same rule as the rest of the note: every number is a
measurement whose command is quoted, or it is in §9.9 "still not
measurable".*

All work was done outside the repository, in
`<scratch>/out_pnr/`. The only repository file touched was
`bsv/StretchMemory.bsv`, for the documented one-unit configuration
change; it is reverted and diffed in §9.8.

### Summary of what §9 establishes

| | result | where |
|---|---|---|
| `nextpnr-ecp5` | **works natively** — four arm64 builds already on this machine; §2.6's "unrecoverable" is wrong | §9.0 |
| **`MULT18X18D`** | **36** — fits a 45F (72) at 50 %; excludes 12F/25F (28) | §9.3.1 |
| Whole-core `DP16KD` | **384**, identical to `mkStretchStorage` alone — nothing else in the core uses block RAM | §9.3.3 |
| Whole-core `TRELLIS_FF` | **12,449** (28 % of a 45F) — §2.5's 9,761 sum was a slight under-estimate | §9.3.3 |
| **Whole-core `CCU2C`** | **41,060 ⇒ ≈ 82,120 TRELLIS_COMB for carry alone. The six-unit core does not fit an 85F on this path** | **§9.3.4** |
| **One-unit core `CCU2C`** | **41,070 — the same. The carry logic is all CPU, so the one-unit build does not fit a 45F either** | **§9.3.5** |
| Six-unit block RAM | nextpnr **refuses to place** on the 85F — §2.2's arithmetic is now a router result | §9.5.3 |
| One-unit `mkMBCU` on a 45F | **91.57 MHz**, 59.3 % DP16KD, worst path is the BRAM's own clk-to-q | §9.5.1 |
| `mkStretchIO` on a 45F | **98.83 MHz** | §9.5.5 |
| **Whole-core LUT4** | **283,931 (6u) / 271,449 (1u)** — both runs completed late in the work | §9.3.6a/b |
| **Does any config fit any ULX3S?** | **No. `TRELLIS_COMB` 433–826 % of the part, on every configuration tried. Combinational logic, not block RAM, is the binding constraint** | **§9.3.6c** |
| **One-unit 45F Fmax** | **does not exist — the one-unit core does not place on a 45F (826 % COMB).** Block RAM (59 %), multipliers (50 %), FFs (35 %) and IO (4 %) all fit; logic does not | §9.3.6b |
| Whole-core Fmax | **not measurable**: never reaches timing analysis. Bounded above at ≈ 91.57 MHz by the two subsystems that did route | §9.5.6 |
| `share` (the one thing that could overturn §9.3.4/5) | **does not terminate**, 3rd attempt; root-caused to register-file mux cross-products | §9.3.6 |
| MBCU 1u-vs-2u LUT4 anomaly | **explained: abc9's LUT mapper**, not bsc and not the interleave edit | §9.6 |
| "Turn abc9 off, then" | **no** — abc9 is 2.6× *better* on `mkStretchIO`; the 1-unit MBCU is an outlier | §9.6.1 |
| Dropping `share` | costs **exactly zero** LUT4 on `mkStretchIO`… but that control does not transfer to the core's 41,060 CCU2C | §9.6.1, §9.3.4 |
| 12F vs 25F die | **`--12k` exposes the full 25F die**: 24,288 LUT4, 56 DP16KD | §9.5.4 |
| Machine load | **never quiet**: 459 `qemu` processes, load 90–183 throughout, and agent jobs run at nice 5 against their nice 0 | §9.1 |

---

## 9.0 First, a correction: `nextpnr-ecp5` was never unrecoverable

**§2.6 and §7 are wrong on this point, and the error is consequential**
— it is the sole reason the note has no routing result and no Fmax.

§2.6's diagnosis of `/usr/local/bin/nextpnr-ecp5` is *correct*: it is
`Mach-O 64-bit executable x86_64`, it wants
`libboost_python38-mt.dylib`, nine further Intel boost libraries, four
Qt5 frameworks and Python 3.8 from a `/usr/local` Homebrew prefix that
no longer exists, and it is indeed not a `brew reinstall` away. What
§2.6 got wrong was the search: it concluded from `brew info`,
`ls /opt`, `brew list --cask` and
`find / -maxdepth 4 -name 'nextpnr-ecp5*'` that no working build
existed. **`-maxdepth 4` was the mistake.** Four working native arm64
builds sit at depth 6 under a sibling project:

```
$ T=~/src/ulx3s-experiments/bluespec-ulx3s/toolchain
$ file -b $T/nextpnr-build/nextpnr-ecp5
Mach-O 64-bit executable arm64
$ $T/nextpnr-build/nextpnr-ecp5 --version
"nextpnr-ecp5" -- Next Generation Place and Route (Version eb4f15c)
$ $T/nextpnr-0.11.1-build/nextpnr-ecp5 --version
"nextpnr-ecp5" -- Next Generation Place and Route (Version nextpnr-0.11.1)
```

plus `nextpnr-build-coherent` and `nextpnr-build-homebrew` (both
`eb4f15c`), and a native `ecppack` at
`$T/prjtrellis-install/bin/ecppack`.

All measurements below use **`nextpnr-build/nextpnr-ecp5`
(eb4f15c)**, because `~/src/ulx3s-experiments/flute-ulx3s/Makefile:13`
selects exactly that binary — so it is the build already proven in a
real ULX3S bitstream flow on this machine, rather than merely the one
that answers `--version`.

**No source build was needed and none was attempted.** §4 item 2
("Revive `nextpnr-ecp5` … 0.5–2 days") is therefore **already done, at
zero cost**, and should be struck from the effort table.

There is a second, richer local resource §1–§8 did not use at all:
**`~/src/ulx3s-experiments/HANDOFF.md`** (1,879 lines), a record of
real ULX3S Bluespec timing work on this machine. It supplies the Fmax
methodology used in §9.5 and two findings quoted below that bear
directly on this note's conclusions.

## 9.1 Machine load: still not quiet, and this must be said plainly

§2's caveat ("load average of 100–200 … other work, not this") **still
applies to every wall-clock figure in this section.** The contention
was *not* from other Stretch agents and did not go away:

```
$ uptime
11:03  up 28 days, 23:27, 58 users, load averages: 124.46 127.92 147.75
11:19  ...                          load averages: 132.20 124.53 131.31
$ pgrep -f qemu-system-x86_64 | wc -l
     459
```

**459 `qemu-system-x86_64` processes**, each `-smp 2`, all from
`/Users/npe/src/inferno64-branches/parallelgc/.qemu/...` — a different
project entirely. On 16 cores that is roughly 8× oversubscription, and
it persisted for the whole of this work (observed range 106–152).

So the hoped-for "retry it on a quiet machine" **did not happen,
because no quiet machine was available.** That matters for how §9.3's
result should be read: the whole-core synthesis blockers reported in
§2.5 were re-observed here under the same contention, and two
independent sibling runs were caught in them live:

```
$ ps -o pid,etime,%cpu,rss,command -p 80186
  PID  ELAPSED  %CPU    RSS COMMAND
80186 01:33:28   4.0 1171648 yosys ... synth_ecp5 -top mkStretchCore   <- in SHARE
$ ps -o pid,etime,%cpu,rss,command -p 99065
99065 01:16:38   0.0  12304 yosys -l runB2.log -s runB2.ys             <- in ABC9_EXE
```

one stuck in `SHARE` at 1 h 33 m, one stuck in `ABC9_EXE` with its log
frozen for 50 minutes. **§2.5's two failure modes are real and
reproducible, not merely starvation** — see §9.2, which is how this
section got numbers anyway. The clincher on that distinction: over its
first 1 h 22 m the sibling's `abc9` child accumulated only **9 min 49 s
of CPU**, while this section's stock `abc` on the same design was
making visible progress within two minutes. abc9 is not slow here
because the machine is busy; it is slow here.

### 9.1.1 And a scheduling detail that explains more than the load does

The load figure alone understates the problem, because the competing
work has *higher priority than this work*:

```
$ ps -o pid,nice,stat,%cpu -p <this section's bsc>
  PID NI STAT  %CPU
76393  5 RN     4.7          <- agent job: nice 5
$ (sample of the 459 qemu processes)
 2496  0 R      1.2          <- competing work: nice 0
```

**Agent jobs here run at nice 5; the 459 `qemu` processes run at
nice 0.** Each individual `qemu` is only using ~1 % of a core, but
there are 459 of them at a better priority, so a single-threaded
`bsc` or `yosys` gets throttled to **4–20 % of one core**. `bsc` on
the one-unit core took **19 minutes of wall clock to spend 2 m 16 s of
CPU**. `renice -n 0` exits 0 but silently does nothing, because a
non-root process cannot lower its own nice value on macOS:

```
$ renice -n 0 -p 76393 ; echo "rc=$?" ; ps -o pid,nice -p 76393
rc=0
  PID NI
76393  5          <- unchanged
```

So "retry it on a quiet machine" was not available at any point during
this work, and **the honest reading of §2.5's failure is a combination
of two genuine tool pathologies (`share`, `abc9`) and a ~20×
scheduling handicap** — not one or the other. Anyone re-running this
should either stop the `qemu` fleet or run the synthesis at nice 0 from
a normal shell.

---

## 9.2 Method: how the whole-core measurement was made to terminate

Three changes to §2.5's approach, all disclosed, all justified by
measurement rather than convenience.

**(a) `stat` before LUT mapping, not only after.** This is the change
that actually rescues the measurement. `DP16KD` is fixed by
`memory_libmap`/`memory_map` and **`MULT18X18D` is fixed by `mul2dsp`
inside the coarse stage** — both long before `abc`. §2.5 reached ABC9
twice and extracted nothing because its only `stat` was at the end. A
`stat` after `map_ffs` banks DP16KD, MULT18X18D and TRELLIS_FF
**even if LUT mapping never finishes.**

**(b) `share` dropped**, exactly as §2.5's Run B did: the coarse stage
is pasted verbatim from `yosys -p "help synth_ecp5"` with only `share`
removed. `share` is SAT-based resource sharing, so in principle
dropping it makes the area figures an **upper bound**. §9.1's live
evidence (a sibling stuck in `SHARE` at 1 h 33 m) says this is not
optional. **And §9.6.1 measures the cost of the deviation at exactly
zero** — `mkStretchIO` maps to 8,102 LUT4 with `share` and 8,102
without it, identical to the cell. So this deviation is, at least on
one real subsystem of this design, free rather than merely bounded.

**(c) `-noabc9`.** §2.5 did not try this. The reason is simply that
**abc9 is where the whole-core runs hang**: both of §2.5's attempts
that reached LUT mapping stopped in `ABC9_EXE`, and a sibling run was
caught there live during this work with its log frozen for 50 minutes
(§9.1). Stock `abc` is the only mapper that terminates on this
netlist.

**This deviation is NOT free, and unlike (a) and (b) it is not an
upper bound in a harmless direction.** §9.6.1 measures abc9 against
stock abc on four netlists from this model and finds abc9 *usually
better* — 2.6× better on `mkStretchIO`, 1.4× better on the two-unit
`mkMBCU`, neutral on the six-unit `mkStretchStorage`, and 2.26× worse
only on the degenerate one-unit `mkMBCU`. **So any whole-core LUT4
figure taken with `-noabc9` is a pessimistic upper bound, possibly by
~2.5×, and must not be used to exclude a device.** DP16KD,
MULT18X18D and TRELLIS_FF are mapper-independent and carry no such
caveat, which is precisely why change (a) matters so much.

**(d) RTLIL checkpoints** (`write_rtlil` after coarse and after
`map_ffs`) so that a hang costs minutes, not the whole run.

Script: `out_pnr/synth_core.sh`; generated yosys scripts in
`out_pnr/logs/*.ys`. Unlike §2.5's Run B, `BRAM1.v` is read **as real
Verilog, not `-lib`/blackboxed**, so yosys must infer and map the
memory and `DP16KD` is a measured mapping result. (Run B blackboxed
it, which is why it could not have reported DP16KD at all.)

### 9.2.1 The harness, and why place-and-route needs one

**`mkStretchCore` cannot be given to nextpnr as a top module. This is
a hard measured fact, not a toolchain problem:**

```
$ python3 (count input/output port declarations in mkStretchCore.v)
input ports 54 bits 1724
output ports 75 bits 2170
TOTAL port bits 3894
```

**3,894 port bits against ~197 usable IO on CABGA381.** §3.5 counted
the 129 ports but not their bit width; the consequence is that IO
placement fails before timing is ever considered. Every one of those
ports is a `gen_tb.py` test method (§3.5).

Tying them to constants is *not* an acceptable fix: yosys would
constant-propagate away most of the index-mux logic that §2.3/§2.4's
counts consist of, understating both area and the critical path. So
`out_pnr/mk_harness.py` generates a **non-pruning pin-count-reduction
harness**:

- every core **input** is driven by a flip-flop, and the input plane is
  a **shift register** (`in_r <= {in_r[N-2:0], lfsr[0]}`) fed by a
  64-bit maximal-length LFSR. A shift register, not a broadcast,
  specifically so that no two input FFs hold the same value and
  `opt_merge` cannot dedup the plane into one copy and invent
  false high-fanout nets. Fanout per FF is 2, and no combinational
  logic is inserted in front of any core input;
- every core **output** is captured directly into a flip-flop;
- the output plane is then XOR-reduced to one LED through a
  **pipelined** tree, ≤ 8 bits per stage (≤ 2 LUT4 levels). Pipelining
  matters: one flat XOR of 2,170 bits would itself become the critical
  path and understate the core's Fmax;
- `CLK` and `RST_N` are real pins and are never driven from the LFSR.

Every path through the core is therefore a genuine
FF → core logic → FF path. **The harness was validated against a real
design before use** (`out_pnr/validate_flow.sh`, on the one-unit
`mkMBCU`):

| | LUT4 | TRELLIS_FF | DP16KD |
|---|---|---|---|
| `mkMBCU` alone, `-noabc9` | 3,165 | 670 | 64 |
| `mkMBCU` + harness, `-noabc9` | 3,189 | 932 | 64 |
| harness cost | **+24 (+0.8 %)** | +262 | 0 |

**+0.8 % LUT4 is the measured proof that the harness neither prunes
the core nor adds meaningful logic of its own.**

Two netlists are therefore produced per configuration, for two
different purposes, so that no area has to be subtracted from
anything: **core alone → yosys `stat`** (comparable with §2.3/§2.4),
**core + harness → nextpnr** (P&R and Fmax).

## 9.3 The whole core: MULT18X18D measured at last, and the multipliers fit

§2.5 and §7 both say there is "no measured whole-core LUT4,
TRELLIS_FF, DP16KD or MULT18X18D figure in this note", and call the
multiplier count "the largest single hole in §2". **The multiplier
count is now measured.**

The run (`out_pnr/synth_core.sh core6`, script
`out_pnr/logs/core6.ys`, full log `out_pnr/logs/core6.log`) got
through `coarse` — including `mul2dsp` — in about 7 minutes of wall
time at load average 118–133, and wrote the stage-A statistics and an
RTLIL checkpoint. From `out_pnr/logs/core6.statA`:

```
=== mkStretchCore ===     (whole core, 6 units, after `coarse`, minus `share`)
   Number of cells:              33802
     MULT18X18D                     36       <-- never measured before
     $mux                        10062
     $logic_and                   9807
     $eq                          2556
     $alu                         2291
     $logic_or                    3932
     $ne                          1368
     $macc                          28
     $mem_v2                        20
     $div                            3
     $shiftx                        13
```

### 9.3.1 MULT18X18D = 36, and what it means

**36 `MULT18X18D`.** This is a real mapping result: `mul2dsp` ran with
the stock `synth_ecp5` arguments (`DSP_A_MAXWIDTH=18`,
`DSP_B_MAXWIDTH=18`, `DSP_A_MINWIDTH=2`) and the count is what it
produced. Against the device budgets from §2.1:

| device | 18×18 multipliers | core needs 36 | headroom |
|---|---|---|---|
| LFE5U-12F | 28 | **no — 8 short** | — |
| LFE5U-25F | 28 | **no — 8 short** | — |
| LFE5U-45F | 72 | **yes** | 50 % used |
| LFE5U-85F | 156 | **yes** | 23 % used |

**So the floating-point unit's multipliers fit on a 45F with half the
DSP column spare, and they are a third reason the 12F and 25F are
out** — §2.5 excluded those two on LUT4 and §2.2 excluded them on
block RAM; they are now also excluded on multipliers. That is a new
result: §2.5 could only say "the 85F … [is] the only one with … 156
multipliers for the FP unit", implying the count might be large. It is
not. 36 is comfortable.

The arithmetic is consistent with §2.5's expectation that this is the
three 48 × 48 fraction multipliers at `StretchFP.bsv:713,720,902`: a
48 × 48 product decomposes into ⌈48/18⌉ = 3 by 3 = **9 `MULT18X18D`
per multiplier**, and 3 × 9 = 27, with the remaining 9 accounted for
by narrower multiplies elsewhere (28 `$macc` cells survive alongside).

**Cross-check, and it holds:** the *one-unit* core (§9.3.3), a
separately generated 99,673-line netlist, also reports **exactly 36
`MULT18X18D`** — as it must, since `NumUnits` does not touch the
floating-point unit. Two independent elaborations agreeing on the
figure is the best confirmation available without hand-counting the
DSP instances.

### 9.3.2 A new finding not on anyone's list: three real dividers

`$div = 3` in the stage-A netlist. These are not an artifact — they
are five literal divisions in the generated Verilog, which yosys's
coarse stage shares down to three:

```
$ grep -n ' / ' mkStretchCore.v
67187:  assign bytes__h1337050 = x__h1337092 / y__h1337093 ;
   ... 5 occurrences, all named bytes__h*
$ grep -n 'assign \(x__h1337092\|y__h1337093\) ' mkStretchCore.v
81349:  assign x__h1337092 = x__h1337094 - 8'd1 ;
88276:  assign y__h1337093 = { 4'd0, bsz__h1337049 } ;
```

So each is **`(fieldLength − 1) / byteSize`, 8 bits by 8 bits, with a
genuinely variable divisor** — the direct consequence of the 7030's
variable-field-length byte size (1–8 bits) being a *runtime* value.
The ECP5 has no divider primitive, so these map to LUT logic.

At 8 × 8 bits that is modest (a few hundred LUT4 each, not thousands),
so it is not a feasibility problem. It is worth recording for two
reasons: nothing in §1.2's blocker list anticipated a divider at all,
and a variable-divisor divide is exactly the kind of thing that lands
on the critical path. §9.5 reports whether it did.

### 9.3.3 The whole-core block RAM, flip-flop and carry counts

The run reached the post-`map_ffs` checkpoint, which fixes everything
except LUT mapping (`out_pnr/logs/core6.statB`). **This is the
whole-core cell count §2.5 and §7 both state does not exist:**

```
=== mkStretchCore ===   (whole core, 6 units, unwrapped, pre-LUT-mapping)
   Number of cells:             503256
     DP16KD                        384
     MULT18X18D                     36
     TRELLIS_FF                 12,449
     TRELLIS_DPR16X4               118
     CCU2C                      41,060
     $_MUX_                    255,130
     $_OR_                      88,047
     $_AND_                     80,374
     $_NOT_                     21,660
     $_XOR_                      3,973
```

Three of these are mapper-independent and so are solid:

| | whole core (measured here) | §2.5's "sum of the two measured parts" | what the core adds |
|---|---|---|---|
| **DP16KD** | **384** | 384 | **0** |
| **TRELLIS_FF** | **12,449** | 9,761 | **+2,688** |
| **MULT18X18D** | **36** | 0 | **+36** |

- **DP16KD = 384 for the whole core, identical to `mkStretchStorage`
  alone (§2.3).** So §2.3's inference that "nothing else in the storage
  path uses block RAM" extends to the entire core: the I-box, look-ahead
  and E-box use none at all. The six-unit EBR verdict of §2.2/§9.5.3 is
  the whole machine's EBR verdict.
- **TRELLIS_FF = 12,449.** §2.5 was careful to say its 9,761 sum "is an
  indication, not a bound in either direction". It was a slight
  *under*-estimate: the E-box, look-ahead, instruction buffers and the
  core's own rules contribute 2,688 flip-flops on top of storage and
  I/O. 12,449 of 43,848 on a 45F is **28 %** — flip-flops are not a
  constraint on any part from the 45F up.

### 9.3.4 The finding that actually threatens the 85F: 41,060 CCU2C

`CCU2C` is the ECP5's carry/arithmetic primitive. It is produced by
`alumacc` + `arith_map` from the netlist's 2,291 `$alu` cells (plus
wide `$eq`/`$ne` comparators), it is **not** touched by LUT mapping,
and **each CCU2C occupies a whole slice — i.e. two LUT4 slots.**

The claim that LUT mapping does not touch it is not just read off the
pass order; it is measured. Two netlists here have both a `statB`
(pre-LUT) and a `statC` (post-LUT) reading, and the counts are
identical:

| netlist | CCU2C at `statB` | CCU2C at `statC` |
|---|---|---|
| `mkStretchStorage` 6u + harness | 95 | **95** |
| `mkStretchIO` + harness | 4 | **4** |

**The conversion factor was calibrated empirically**, because the
conclusion below rests on it (`out_pnr/ccu2c_calib.sh`). A purpose-built
netlist of 64-bit adders — almost pure carry, so the reading is not
confounded by LUT4 — was synthesised and placed on a 45F:

```
yosys:    CCU2C 96    LUT4 72    PFUMX 10    TRELLIS_FF 13,057
nextpnr:  TRELLIS_COMB  278 / 43848
```

(Three 64-bit adders survive `opt`, 3 × 32 = 96 CCU2C.) So
278 − 72 = 206 COMB are attributable to 96 CCU2C:
**2.15 TRELLIS_COMB per CCU2C**, as the architecture implies. The same
relation holds on the §9.5 netlists:

| netlist | yosys LUT4 | yosys CCU2C | LUT4 + 2×CCU2C | nextpnr TRELLIS_COMB |
|---|---|---|---|---|
| purpose-built adders | 72 | 96 | 264 | **278** |
| `mkStretchIO` + harness | 20,583 | 4 | 20,591 | **20,597** |
| `mkMBCU` 1u + harness | 3,189 | 4 | 3,197 | **3,299** |
| `mkStretchStorage` 6u + harness | 14,825 | 95 | 15,015 | **15,785** |

Applying 2.0–2.15× to the whole core:

**41,060 CCU2C ⇒ ≈ 82,120 TRELLIS_COMB consumed by carry logic alone,
before a single LUT4 of control or multiplexing is placed.**

Against §2.1's device budgets (and nextpnr's own figures, which match):

| device | TRELLIS_COMB available | carry alone needs ≈ 82,120 |
|---|---|---|
| LFE5U-45F | 43,848 | **1.87× over — impossible** |
| LFE5U-85F | 83,640 | **98.2 % used, leaving ≈ 1,520 for everything else** |

**Read plainly: on this synthesis path the six-unit `mkStretchCore`
does not fit an 85F either, and it is the arithmetic, not the memory,
that does it.** That is a materially worse outlook than §2.5's "the
45F is the plausible floor, the 85F the safe choice", and it is the
single most consequential number in this section.

**But it is an upper bound, and here the caveat is not a formality.**
§9.2's deviation (b) drops `share` — and `share` is *precisely* the
pass whose job is to prove two arithmetic operators mutually exclusive
and merge them. §9.6.1 measured dropping `share` as costing exactly
zero, but **that control was `mkStretchIO`, which has 4 CCU2C; it says
nothing about a netlist with 41,060.** The core is the one design in
this note where `share` would be expected to matter enormously, and it
is also the one design on which `share` has never terminated (§9.1:
two attempts, one caught live at 1 h 33 m).

So the honest statement is:

- **Measured:** with `share` omitted, the six-unit core's carry logic
  alone requires ≈ 82,120 of the 85F's 83,640 TRELLIS_COMB.
- **Not measured, and now the most valuable single measurement
  outstanding:** the same count with `share` enabled. If `share`
  merges even a third of those adders the 85F becomes comfortable
  again; if it merges few, the six-unit core needs partitioning across
  parts regardless of what happens to the SDRAM question.
- **Either way the 45F is out for the six-unit core**, since even a
  2× improvement from `share` leaves ≈ 41,000 against 43,848 with
  nothing left over. §2.5 excluded the 45F only "plausibly"; on
  arithmetic it is now excluded with a measured margin.

This also explains, retrospectively, *why* `share` does not terminate
on this netlist: it is a SAT-based pairwise analysis over 2,291 `$alu`
cells, which is a far larger problem than it faces on any subsystem.

### 9.3.5 The one-unit core, and the news is bad for the 45F

The one-unit configuration — §2.2.1's "genuine milestone", the build
that runs the entire transcribed diagnostic corpus with no SDRAM — was
generated (`NumUnits = 1`, 99,673 lines of Verilog; the generated file
contains **exactly one `BRAM1` instance**, confirming the edit took)
and run through the same flow. Pre-LUT-mapping
(`out_pnr/logs/core1h.statB`, harness included):

```
=== stretch_harness (one-unit mkStretchCore + harness) ===
     DP16KD                         64
     MULT18X18D                     36
     TRELLIS_FF                 15,506
     TRELLIS_DPR16X4                38
     CCU2C                      41,070
```

Two of these behave exactly as §2.2 predicts, which is reassuring:

- **DP16KD = 64**, one unit's worth — 59 % of a 45F, as §2.2's table
  says and §9.5.1 already routed.
- **TRELLIS_FF = 15,506** minus the harness's ≈ 4,236 ⇒ ≈ 11,270 for
  the core, against the six-unit core's 12,449. The 1,179 difference is
  five absent memory units at §2.2's measured 215 FF each = 1,075.
  **§2.2's additivity claim holds at whole-core scale.**

**And then the number that matters:**

> **`CCU2C` = 41,070 in the one-unit core, against 41,060 in the
> six-unit core — a difference of ten cells in forty-one thousand.**

**The carry logic is essentially all CPU — E-box, look-ahead,
instruction unit — and essentially none of it is memory.** Dropping
from six memory units to one removes 320 block RAMs and 1,179
flip-flops and leaves the arithmetic untouched, which in hindsight is
obvious and in prospect was not measured by anyone.

The consequence is the most important correction in this section:

| | ≈ TRELLIS_COMB for carry alone | 45F (43,848) | 85F (83,640) |
|---|---|---|---|
| one-unit core | ≈ 82,140 | **1.87× over** | **98 % used** |
| six-unit core | ≈ 82,120 | **1.87× over** | **98 % used** |

**So on this synthesis path the one-unit build does not fit a 45F
either — and not for the reason anyone was watching.** §2.2 and
§2.2.1 establish that its *storage* fits a 45F comfortably (64 of 108
DP16KD) and conclude "a 45F ULX3S could run the whole transcribed
corpus with storage entirely in block RAM and no SDRAM at all". That
claim is about block RAM and it is correct about block RAM. **It is the
carry logic, not the storage, that decides the part** — and the
one-unit build is no cheaper there than the six-unit one.

The `share` caveat of §9.3.4 applies identically and is the reason
this is stated as a bound rather than a verdict: 41,070 CCU2C is what
the design costs *with resource sharing omitted*, and sharing is
exactly the optimisation that would attack it. **The one-unit build's
device question therefore reduces to the same single unmeasured
quantity as the six-unit build's: what `share` does to 2,291 `$alu`
cells.** §9.3.6 reports the attempt to find out.

For the record, a useful side-reading from the calibration netlist:
**pure 64-bit carry chains on a 45F close at 143.45 MHz** — so carry
is a capacity problem here, not a speed problem.

**One thing this section wanted and did not get.** §9.5.3 turned the
block-RAM verdict into a *router refusal* rather than arithmetic, and
the same was attempted for carry: a synthetic netlist of 1,284
registered 64-bit adders was built to match the core's CCU2C count,
and yosys did produce **40,661 CCU2C** — within 1 % of the core's
41,070, so the construction was right. But the fold needed to stop
`opt` pruning the adders contributed **29,300 LUT4** of its own, which
would have made any placement failure un-attributable to carry alone;
and the second attempt went into `ABC9_EXE` at load 291 and was
stopped. **So §9.3.4/§9.3.5's capacity verdict rests on calibrated
arithmetic (2.15 COMB per CCU2C, §9.3.4) and not on a nextpnr
refusal.** That is a weaker footing than §9.5.3's and is flagged as
such; the calibration itself is measured, but the conclusion drawn
from it is not.

### 9.3.6 What `share` would do: still unmeasured, but now root-caused

§9.3.4 and §9.3.5 both reduce to one question — what `share` does to
2,291 `$alu` cells. It was attacked directly
(`out_pnr/share_probe.sh`): rather than re-run the full flow that never
terminates, the **post-coarse RTLIL checkpoint** from §9.2(d) was
reloaded and `share` run on that alone, with a hard 25-minute cap.

```
=== share probe: limit 1500s ===
TIMEOUT after 1500s -- killing; share did NOT terminate on this netlist
```

**`share` does not complete even when handed the already-coarsened
netlist and nothing else to do.** Three attempts now — §2.5's Run A,
the sibling caught live at 1 h 33 m in §9.1, and this one — have failed
to get a figure out of it.

But the log says *why*, which no previous attempt recorded. `share`
spends its time enumerating **activation patterns**: for each
arithmetic cell, the set of control-signal combinations under which it
is live, so that mutual exclusivity can be proved. After 25 minutes and
13,172 lines of log it was still enumerating patterns for a *single*
cell:

```
Activation pattern for cell $shl$...mkStretchCore.v:67884$44951:
  { ... \MUX_st_maintenanceBits$write_1__SEL_4 ... } = 3'110
  { ... \MUX_st_intervalTimerAndClock$write_1__SEL_4 ... } = 3'110
  { ... \MUX_st_interruptionAddress$write_1__SEL_4 ... } = 3'110
  { \MUX_st_xreg_15$write_1__SEL_4 \MUX_st_xreg_15$write_1__SEL_3
    \MUX_st_xreg_15$write_1__SEL_2 \EN_mem_restoreIndex ... } = 6'100010
  { \MUX_st_xreg_14$write_1__SEL_4 ... } = 6'100010
  ... (st_xreg_13, 12, 11, 10, 9, ... )
```

Every one of those patterns is a *different write-select combination of
a different special-storage or index register*. **The explosion is
driven by exactly the structure §1.2 identified as the source of this
design's size**: "dynamic vector indexing — yes, pervasively", the
`xreg[a - addrIndexBase]` muxes, the 32 special-storage registers and
16 index registers that §2.3 counts and the 80 device-image registers
that §2.4 measures at 8,102 LUT4. `share` has to cross-product its
arithmetic cells against all of them.

So the three facts fit together into one explanation rather than three
coincidences:

1. the design's size comes from register-file index muxes (§1.2, §2.4);
2. `share` is quadratic in exactly those muxes, so it never finishes
   (§9.1, here);
3. without `share`, the arithmetic is unshared, and unshared arithmetic
   is 41,070 CCU2C — which is what does not fit (§9.3.4, §9.3.5).

**And that makes §3.6's and §4 item 10's recommendation much more
important than "the cheapest large utilisation saving".** Moving
`StretchIO`'s 80 device-image registers into one DP16KD, and the same
treatment for the special-storage and index register files, would
attack the mux population that (a) inflates LUT4, (b) makes `share`
intractable, and therefore (c) leaves the arithmetic unshared. It is
plausibly the single change that decides whether this design fits an
ECP5 at all — though that is a hypothesis this note cannot test, not a
measurement.

---

### 9.3.6a LATE RESULT: the six-unit core finished, and nextpnr has now ruled on it

**Both of the caveats in §9.3.7 below were overtaken by events.** The
six-unit whole-core synthesis completed at 14:42 — about three hours
after it started, at load 118–282 — and the resulting netlist was put
through nextpnr. Everything in this subsection is therefore a
**router-reported figure for the entire six-unit `mkStretchCore`**,
and it supersedes the estimates in §9.3.4.

Final synthesis (`out_pnr/logs/core6.statC`, `-noabc9`, `share`
dropped):

```
=== mkStretchCore ===   (whole core, 6 units, unwrapped, fully mapped)
     LUT4                      283,931
     CCU2C                      40,936
     PFUMX                      53,221
     L6MUX21                    17,821
     TRELLIS_FF                 12,449
     DP16KD                        384
     MULT18X18D                     36
     TRELLIS_DPR16X4               118
```

and nextpnr's own device utilisation against the **85F, the largest
ULX3S part** (`out_pnr/logs/core6_unc.log`):

```
Info: Device utilisation:
Info:         TRELLIS_COMB:  375223/  83640   448%
Info:           TRELLIS_FF:   12449/  83640    14%
Info:               DP16KD:     384/    208   184%
Info:           MULT18X18D:      36/    156    23%
Info:           TRELLIS_IO:    3894/    365  1066%
Info:         TRELLIS_RAMW:     118/  10455     1%
ERROR: Unable to place cell 'io_readPrinterWord[43]$tr_io',
       no BELs remaining to implement cell type 'TRELLIS_IO'
```

**Four of this note's open questions are closed by that one table:**

1. **`TRELLIS_COMB` 375,223 / 83,640 = 448 %.** The six-unit core needs
   **4.5× the logic of the largest ULX3S.** This is nextpnr's figure,
   not an inference — §9.3.4's calibrated prediction was ≈ 365,800,
   which came within **2.6 %**, so the 2.15-COMB-per-CCU2C calibration
   is also vindicated.
2. **`DP16KD` 384 / 208 = 184 %**, confirming §2.2's "1.85× over" for
   the whole core and not merely for `mkStretchStorage`.
3. **`MULT18X18D` 36 / 156 = 23 %** — §9.3.1's count confirmed by the
   router, and comfortably within budget.
4. **`TRELLIS_IO` 3,894 / 365 = 1,066 %** — §9.2.1's port-count
   blocker, demonstrated rather than computed. (The 85F's CABGA381
   offers 365 IO, not the 45F's 245; the design still needs 10.7×
   that.) This is the error the run actually died on.

**And the verdict survives the `-noabc9` caveat by a wide margin.**
§9.6.1's worst observed abc9 advantage is 2.6×. Granting it in full to
the LUT4 column only:

```
283,931 / 2.6 ≈ 109,000 LUT4  +  ~81,900 COMB of carry  ≈ 191,000
                                              vs 83,640 on the 85F
```

— **still 2.3× over.** So the conclusion does not depend on the
mapper choice: **the six-unit `mkStretchCore` as it stands today does
not fit the largest ULX3S, on logic, by somewhere between 2.3× and
4.5×.** That is a far harder result than §2.5's "the 85F is the safe
choice", and it is the headline of this section.

**One correction to §9.3.4 on a detail:** CCU2C is *not* perfectly
invariant across LUT mapping after all. It reads 41,060 at `statB` and
**40,936** at `statC` — a 0.3 % reduction. The two netlists where both
stats were available (95→95, 4→4) happened to be exactly stable and
led me to state invariance too strongly. The effect is negligible and
changes nothing, but the claim should be "essentially unchanged",
not "unchanged".

### 9.3.6b LATE RESULT: the one-unit core too — and this is the answer to the priority question

The one-unit core finished fifteen minutes after the six-unit one and
was routed on both parts. **This is the direct answer to "the one-unit
45F Fmax", and the answer is that the number does not exist, for a
measured reason.**

Final synthesis (`out_pnr/logs/core1h.statC`, one unit + harness):

```
     LUT4                      271,449      CCU2C          40,946
     PFUMX                      54,160      L6MUX21        17,991
     TRELLIS_FF                 15,505      DP16KD             64
     MULT18X18D                     36      TRELLIS_DPR16X4    38
```

Note first that **the one-unit core is only 4.4 % smaller than the
six-unit core in LUT4** (271,449 vs 283,931) and identical in CCU2C —
confirming §9.3.5's finding from the far side of LUT mapping.

nextpnr, **LFE5U-45F** (`out_pnr/pnr/core1h-45k-50M-s3.log`):

```
Info:           TRELLIS_IO:      10/    245     4%
Info:               DP16KD:      64/    108    59%
Info:           MULT18X18D:      36/     72    50%
Info:           TRELLIS_FF:   15505/  43848    35%
Info:         TRELLIS_COMB:  362285/  43848   826%
ERROR: Unable to place cell 'core.mem_fetchResp_LUT4_Z_38_B_LUT4_Z_2_A_LUT4_Z_1',
       no BELs remaining to implement cell type 'TRELLIS_COMB'
```

and on the **85F**:

```
Info:               DP16KD:      64/    208    30%
Info:           MULT18X18D:      36/    156    23%
Info:           TRELLIS_FF:   15505/  83640    18%
Info:         TRELLIS_COMB:  362285/  83640   433%
ERROR: Unable to place cell
  'core.st_xreg_8$D_IN_PFUMX_Z_9_BLUT_LUT4_Z_D_LUT4_Z_A_LUT4_Z_A_LUT4_Z_1_C_LUT4_...',
       no BELs remaining to implement cell type 'TRELLIS_COMB'
```

**Everything §2.2 and §2.2.1 said would fit, fits** — block RAM at
59 % of a 45F exactly as predicted, multipliers at 50 %, flip-flops at
35 %, and the harness's IO at 4 %. **The design fails on combinational
logic alone, by 8.3× on the 45F and 4.3× on the 85F.**

The cell the 85F run failed on is, illustratively,
`core.st_xreg_8$D_IN_PFUMX_...LUT4_Z_...` — **a write-mux feeding index
register 8**, the same register-file multiplexer structure §1.2
flagged, §2.4 priced, and §9.3.6 found strangling `share`. **Treat
that as an illustration, not as evidence**: at 433 % utilisation
nextpnr would have failed on *something*, and which cell it reaches
first is an artifact of placement order. The real argument for that
structure being the problem is the three independent lines in §9.3.6,
not this cell name.

### 9.3.6c The consolidated verdict

| configuration | part | TRELLIS_COMB | DP16KD | MULT18X18D | TRELLIS_FF | result |
|---|---|---|---|---|---|---|
| six-unit core *(unwrapped)* | 85F | **375,223 / 83,640 = 448 %** | 384/208 = 184 % | 36/156 = 23 % | 12,449 = 14 % | **fails** |
| one-unit core *(harnessed)* | 45F | **362,285 / 43,848 = 826 %** | 64/108 = 59 % | 36/72 = 50 % | 15,505 = 35 % | **fails** |
| one-unit core *(harnessed)* | 85F | **362,285 / 83,640 = 433 %** | 64/208 = 30 % | 36/156 = 23 % | 15,505 = 18 % | **fails** |

*Provenance differs between rows and is worth stating: the six-unit
figure comes from the **unwrapped** netlist, which nextpnr reports
after packing and then dies on IO (3,894/365) before placing logic;
the one-unit figures come from the **harnessed** netlist, which clears
IO at 4 % and dies on logic. Both are post-pack nextpnr utilisation of
the same kind, so they are comparable — but that is why the
near-identical LUT4 counts give 448 % and 433 % of the same part.*

*And the harness is not what makes the one-unit figure large: the
harness contributes ~311 `$reduce_xor` cells plus registers (< 1 % of
271,449 LUT4), and the independently synthesised **unwrapped**
six-unit core measures 283,931 LUT4 — slightly more, with no harness
at all. The 826 % is the design, not the measurement apparatus.*

**No configuration of this design fits any ULX3S, and the binding
constraint is combinational logic, not block RAM.** The note's entire
device discussion — §2.2's EBR tables, §2.5's "45F plausible floor,
85F safe choice", §4's effort estimates — is organised around block
RAM, which turns out to be the *easy* axis.

**Does the `-noabc9` caveat rescue it? No.** Granting abc9 its largest
observed advantage (2.6×, §9.6.1) to the LUT4 column alone:

```
one-unit:  271,449/2.6 ≈ 104,400 LUT4 + ~81,900 carry ≈ 186,000 COMB
                                                vs 83,640 on the 85F
```

**still 2.2× over.** The verdict is robust to the mapper choice. The
only measurement that could still change it is `share` (§9.3.6), which
has now failed to terminate three times — and note that `share` would
have to remove **more than half of all combinational logic**, far
beyond anything it plausibly does.

**So the honest headline for this section is not an Fmax. It is that
Fmax is the wrong question for this design today**: it never reaches
timing analysis, because it never places. §3.1's judgement that
timing closure would be "a non-issue" at 3.333 MHz looks correct
(§9.5.6 measures two subsystems at 91–107 MHz), and is simply not what
stands in the way.

### 9.3.7 LUT4 itself: still not measured, and it no longer matters much

*(Superseded by §9.3.6a, which reports the completed figures. Retained
because its reasoning — that the verdict did not depend on LUT4 — was
written before the run finished and was borne out: the carry estimate
alone already exceeded the device, and LUT4 only widened the gap.)*

Stock `abc` did reach the whole core — both the six-unit and one-unit
runs entered `map_luts` and `abc` was still working when this section
closed. It is not hung in the abc9 sense (it accumulates CPU steadily,
unlike the sibling abc9 of §9.1 which burned 11 minutes of CPU in
95 minutes of wall clock), it is simply a very large problem. The log
records how large, which is itself a measurement nobody had:

```
Extracted 449184 gates and 510186 wires to a netlist network
  with 61000 inputs and 62937 outputs.
```

**449,184 gates in a single abc invocation.** (It is consistent with
§9.3.3's pre-mapping cell list: 255,130 + 88,047 + 80,374 + 21,660 +
3,973 = 449,184 exactly.) For comparison, the whole of `mkStretchIO` —
which takes under a minute — is a few thousand.

**So there is still no measured whole-core LUT4 figure** (see §9.9).
What has changed is that **the device verdict no longer waits on it**:

- `CCU2C` is fixed before LUT mapping and is unaffected by it. At
  41,060–41,070 it already accounts for ≈ 82,120 TRELLIS_COMB, which
  on its own exceeds the 45F's entire 43,848 and leaves ≈ 1,520 of the
  85F's 83,640 (§9.3.4, §9.3.5).
- LUT4 can therefore only make the picture worse, never better. Any
  completed figure would be added to 82,120, not compared with it.

That is why §9.3.4/§9.3.5's conclusions are stated as results rather
than as "pending abc". **The missing LUT4 number would refine the
utilisation; it cannot overturn the verdict.** The one quantity that
*could* overturn it is `share` (§9.3.6), and that is the measurement
which failed.

---

## 9.4 How Fmax is reported here, and one methodological trap ruled out

`HANDOFF.md` contains a warning that governs how this section reports
everything (§9.1 of that file, around line 1065):

> *"best step4 seed 1.8% margin vs baseline 15.7%; nextpnr 'PASS at 25'
> on 1.8% is not hardware margin."*

That project lost real hardware runs to thin-margin setup violations
that nextpnr had declared a PASS. Its spec consequently requires
*"MARGIN: >=12% at seed 3, >=10% min across the sweep"* over an
8-seed sweep. **So no number below is reported as a pass/fail at one
frequency.** Each is an achieved Fmax with its seed spread and its
worst-path endpoints.

The command, matching the Flute Makefile's own invocation
(`flute-ulx3s/Makefile:159`) for package and seed handling:

```sh
nextpnr-ecp5 --45k --package CABGA381 --json <netlist>.json \
    --lpf <lpf> --textcfg <out>.config --report <out>-report.json \
    --seed <N> --timing-allow-fail
```

`--timing-allow-fail` is deliberate: without it nextpnr aborts when the
LPF constraint is missed and writes no report, so a failing constraint
would yield no Fmax at all. Fmax is read from the report JSON's
`fmax.<clock>.achieved` for the **global clock net**
(`$glbnet$CLK$TRELLIS_IO_IN`); the Flute reports show nextpnr also
emits an IO-input pseudo-domain whose "achieved" figure (754 MHz in
one of theirs) is meaningless, and that is excluded.

### 9.4.1 The trap: is the achieved figure an artifact of the constraint?

A real worry, because nextpnr is timing-driven and could stop
optimising once the LPF constraint is met — in which case a loose
constraint would understate Fmax and the whole section would be
reporting the constraint back to itself. **Tested, on the validated
one-unit `mkMBCU` netlist, same seed, three constraints spanning 6×:**

| LPF constraint | achieved Fmax | verdict line |
|---|---|---|
| 25 MHz | **91.57 MHz** | PASS at 25.00 MHz |
| 50 MHz | **91.57 MHz** | PASS at 50.00 MHz |
| 150 MHz | **91.57 MHz** | FAIL at 150.01 MHz |

**Identical to two decimal places across the whole range, including a
constraint it fails.** For this toolchain and this design family
nextpnr-ecp5 eb4f15c reports the true post-routing critical path and
the constraint only selects the PASS/FAIL wording. So the achieved
figures below are genuine maxima, not constraint echoes, and the
50 MHz constraint used throughout is an arbitrary and harmless choice.

Seeds, by contrast, *do* move the result (HANDOFF's sweeps span
27.9–30.3 MHz on one design), so **the seed sweep, not the constraint,
is the spread measure reported below.**

---

## 9.5 Place and route: the first routing results this project has

Every number in this subsection is a **post-routing** result from
`nextpnr-ecp5` (eb4f15c), not a yosys cell count — the distinction
§2.6 was careful to draw and could not cross.

### 9.5.1 The one-unit memory subsystem on a 45F: 91.57 MHz

`mkMBCU` with `NumUnits = 1` — one 16,384-word unit plus the bus
control unit — placed and routed on an **LFE5U-45F, CABGA381**:

```
Info: Max frequency for clock '$glbnet$CLK$TRELLIS_IO_IN': 91.57 MHz (PASS at 50.00 MHz)
```

| resource | used | available (45F) | % |
|---|---|---|---|
| TRELLIS_COMB | 3,299 | 43,848 | 7.5 % |
| TRELLIS_FF | 932 | 43,848 | 2.1 % |
| **DP16KD** | **64** | **108** | **59.3 %** |
| TRELLIS_RAMW | 16 | 5,481 | 0.3 % |
| TRELLIS_IO | 10 | 245 | 4.1 % |

**The 59.3 % DP16KD figure is §2.2's central prediction confirmed by a
router rather than by arithmetic**: §2.2's table says "one unit
(16,384 words) | 64 | … | **yes** (59%)" for the 45F. It is exactly
right.

Worst path, from the report JSON — **both endpoints inside the core**,
so this is the core's Fmax and not the harness's:

```
10.92 ns total: 5.85 ns logic+cell / 5.08 ns routing, 5 segments
  from: core.units_0_ram_memory.RAM.0.45   (DP16KD, port DOA0)
  to:   core.units_0_raw_TRELLIS_FF_Q_18   (setup)
```

The critical path is **the block RAM's own clock-to-output delay
feeding the unit's data register** — 5.6 ns of the 10.92 ns is the
DP16KD itself. That is the architecturally correct answer for a memory
unit, and it means the figure is close to a floor set by the hard
macro: no amount of logic restructuring moves it much.

**Against the 3.333 MHz target (§3.1): 91.57 / 3.333 = 27.5× margin.**

### 9.5.2 What the one-unit *core* number would add

§9.5.1 is the **memory subsystem**, not the whole one-unit machine.
The one-unit `mkStretchCore` additionally contains the E-box, the
four-level look-ahead, the instruction unit and the three VFL dividers
of §9.3.2, any of which can be slower than a BRAM read. **The MBCU
figure must not be quoted as the one-unit core's Fmax.** The core
measurement's status is in §9.9.

### 9.5.3 The six-unit verdict, now a router refusal rather than arithmetic

§2.2's central negative result — 384 DP16KD against 208 on the 85F,
"1.85× over" — was arithmetic plus a yosys cell count. It is now a
**place-and-route result.** The six-unit `mkStretchStorage` netlist
was handed to nextpnr for the **85F, the largest ULX3S part**:

```
$ nextpnr-ecp5 --85k --package CABGA381 --json stg6h.json ...
ERROR: Unable to place cell 'core.mbcu_units_2_ram_memory.RAM.0.37',
       no BELs remaining to implement cell type 'DP16KD'
  exit=125
```

**The router runs out of block RAM part-way through memory unit 2 of
6.** §2.2's conclusion was correct and is now demonstrated rather than
predicted: *the typical six-unit 7030's core storage does not fit in
block RAM on any ULX3S.* §3.1's SDRAM plan is not optional.

The synthesis figures for that netlist (`-noabc9`, harness included):

```
=== stretch_harness (mkStretchStorage, 6 units) ===
     DP16KD                        384
     LUT4                       14,825
     TRELLIS_FF                  7,841
     TRELLIS_DPR16X4               118
     CCU2C                          95
```

Subtracting the harness (3,186 input+output FFs plus its reduction
tree) from 7,841 FF and 14,825 LUT4 recovers ≈ 4,400 FF and ≈ 13,400
LUT4 — **matching §2.3's 4,444 TRELLIS_FF and 13,427 LUT4 to within
0.5 %.** Two things follow. First, it is an independent check that the
harness is faithful. Second, and usefully, **on this netlist `-noabc9`
and abc9 agree**, where on the degenerate one-unit `mkMBCU` they
differ by 2.26× (§9.6) — consistent with `HANDOFF.md`'s "abc9 a no-op
on this design" and confirming that the §9.6 pathology is specific to
small, shallow netlists rather than general.

### 9.5.4 Answered: yes, the open toolchain gives a 12F the whole 25F die

§7 asks "**whether the open toolchain lets a 12F use the full 25F
die** … what `nextpnr-ecp5 --12k` does with that was not checked,
because nextpnr does not run here." It runs now, and the answer is
unambiguous. `nextpnr-ecp5 --12k --package CABGA381` prints its own
device inventory:

```
Info: Device utilisation:          --12k                 --45k (for contrast)
Info:         TRELLIS_COMB:   20597/  24288    84%        20597/  43848
Info:           TRELLIS_FF:    6078/  24288    25%         6078/  43848
Info:               DP16KD:       0/     56     0%             0/    108
Info:           MULT18X18D:       0/     28     0%             0/     72
Info:           TRELLIS_IO:      10/    197     5%            10/    245
Info:              EHXPLLL:       0/      2     0%             0/      4
```

**`--12k` offers 24,288 LUT4 and 56 DP16KD — the 25F's numbers, not
the 12F's advertised 12 k LUTs and 32 EBR.** 24,288 is exactly §2.1's
tilegrid count (3,036 PLC tiles × 8), and 56 is the data sheet's
*25F* sysMEM figure against the 12F's 32. So Project Trellis and
nextpnr simply describe the shared die, and a design using 84 % of it
was accepted on `--12k` without complaint.

§2.1's inference — "the 12F is the 25F die sold at a lower advertised
density" — is therefore not merely a tilegrid coincidence: **the open
flow will actually let you use the extra silicon.** Two caveats, both
real: this is what the *tool* permits, not what Lattice warrants (the
parts are presumably binned, so the extra logic is untested and may
not meet timing or yield), and it does not rescue either part for this
design, which is excluded on multipliers (§9.3.1), block RAM (§2.2)
and almost certainly LUT4.

### 9.5.5 The I/O subsystem on a 45F: 98.83 MHz — and a lesson about mapping

`mkStretchIO` (§2.4: 8,102 LUT4, 5,317 FF, no block RAM) went through
the same harness → synth → nextpnr flow on a 45F, **twice**, because
the first attempt produced a result worth not misreporting.

**Attempt 1, the `-noabc9` netlist** (cell D of §9.6.1, 20,583 LUT4 /
20,597 TRELLIS_COMB = 47 % of a 45F) — **failed to place, on all
three seeds tried**:

```
=== ioh dev=45k constraint=50MHz seed=1 ===  exit=125
ERROR: Unable to find legal placement for all cells, design is probably
       at utilisation limit.
   (identically for seeds 3 and 5)
```

Failing to place at 47 % nominal utilisation is startling, and the
tempting explanation is mux packing: the netlist carries 7,374 `PFUMX`
and 4,599 `L6MUX21`, which compete for the one F5MUX / FXMUX per
slice and so constrain packing far beyond what the LUT4 count
suggests.

**Attempt 2 tested that explanation instead of assuming it**, by
routing the *abc9* netlist of the same module through the same harness
and the same nextpnr call (`out_pnr/io_abc9_pnr.sh`):

| | LUT4 | PFUMX | L6MUX21 | 45F placement | Fmax |
|---|---|---|---|---|---|
| `-noabc9` | 20,583 | 7,374 | 4,599 | **fails, 3/3 seeds** | — |
| abc9 | **8,117** | 3,436 | 1,219 | **places** | **98.83 MHz** |

**It places.** So the mux-packing story is wrong, or at least not
needed: the failure was the `-noabc9` mapping, which inflates not just
LUT4 (2.5×) but `PFUMX` (2.1×) and `L6MUX21` (3.8×) with it. This is
§9.6.1's warning arriving in concrete form — **a `-noabc9` netlist can
fail to place where the abc9 netlist of the same module routes with
half the device free.**

Results for the abc9 netlist on a 45F, both seeds run:

| seed | Fmax |
|---|---|
| 1 | **98.83 MHz** |
| 3 | **106.51 MHz** |

(a 7.8 % seed spread, in line with the 27.9–30.3 MHz spreads
`HANDOFF.md` reports; far short of its 8-seed discipline, see §9.9)

and a third confirmation that the harness is faithful: 8,117 LUT4
wrapped against **8,102** standalone, **+15 LUT4, +0.2 %**.

### 9.5.6 Two measured subsystem Fmax figures, and what they bound

| design (1 unit where applicable), on LFE5U-45F | Fmax | worst path |
|---|---|---|
| `mkMBCU` — one memory unit + bus control | **91.57 MHz** (seed 3) | DP16KD clk-to-q → unit data FF, 10.92 ns (5.85 cell / 5.08 route) |
| `mkStretchIO` — reader/printer/tape images | **98.83 / 106.51 MHz** (seeds 1 / 3) | abc9 netlist |

Both are **27–32× the 3.333 MHz target** of §3.1. Since both modules
are strictly contained in `mkStretchCore`, and the `mkMBCU` critical
path in particular (block RAM output to its own data register) exists
unchanged inside the core, these bound the whole core's Fmax **from
above at ≈ 91.57 MHz** — they cannot establish that the core closes,
only that these two subsystems are not what would stop it.

§3.1's point 3 argued that "even a design that only closes at 15 MHz
is 4.5× faster than it needs to be — which is why §2.6's missing Fmax
number, while a real gap, is probably not a real risk." **On the
evidence now available that judgement looks right**, and the risk has
moved decisively from timing to capacity (§9.3.4, §9.3.5).

---

## 9.6 The MBCU anomaly, explained: it is abc9, and it is not the interleave edit

§2.2 measured `mkMBCU` at **7,139 LUT4 with one unit** and **3,624
with two**, flagged the non-monotonicity, and guessed it was "most
likely a yosys/abc9 artifact in the degenerate one-element
`Vector#(NumUnits, MemoryUnit)` case". §7 listed it as measured but
unexplained.

**The guess named the right culprit for the wrong reason. It is abc9 —
but nothing about the degenerate one-element Vector is involved, and
the `unitOf`/`indexOf` edit is not at fault.**

First, the suspicion that it was a methodology difference is ruled
out: `u1.ys` and `u2.ys` from the original work are byte-identical
apart from the input filename. Both read the real `BRAM1.v` and both
run stock `synth_ecp5`.

Second, bsc's own output is *monotonic in the right direction* — the
one-unit `mkMBCU.v` is the **smaller** file:

```
750 u1/v/mkMBCU.v        1187 u2/v/mkMBCU.v
```

and the `BRAM1` instantiation parameters are identical in both
(`ADDR_WIDTH 14`, `DATA_WIDTH 64`, `MEMSIZE 16384`), so the degenerate
Vector did not elaborate to anything pathological.

**The bisect.** Identical script on both netlists, `stat` at three
stages (`out_pnr/mbcu_bisect.sh`, logs in `out_pnr/mbcu/`):

| stage | 1 unit | 2 units | monotonic? |
|---|---|---|---|
| **A** after `coarse` (generic cells) | 253 cells; 73 `$mux`, 7 `$pmux` | 387 cells; 121 `$mux`, 13 `$pmux` | **yes**, 1 < 2 |
| **B** after `map_ffs` (pre-LUT) | 4,892 cells; 2,477 `$_MUX_` | 6,511 cells; 3,531 `$_MUX_` | **yes**, 1 < 2 |
| **C** after `map_luts` (abc9) | **13,162 cells; 7,139 LUT4** | **7,069 cells; 3,624 LUT4** | **NO — inverted** |

**The one-unit design is strictly smaller than the two-unit design at
every stage of synthesis until abc9, and only abc9 inverts it.** So
the anomaly is created entirely inside the LUT mapper. It is not bsc
elaboration, not the interleave edit, and not the one-element Vector.

**The control that proves it.** Same flow, `-noabc9`
(`out_pnr/mbcu_noabc9.sh`):

| flow | 1 unit LUT4 | 2 units LUT4 | ratio 1u/2u |
|---|---|---|---|
| `synth_ecp5` (abc9, the default) | **7,139** | **3,624** | **1.97× — inverted** |
| `synth_ecp5 -noabc9` | **3,165** | **5,147** | **0.61× — monotonic** |

With stock `abc` the ordering is restored and sensible: one unit costs
3,165 LUT4, two units 5,147, an increment of 1,982 for the second
unit. DP16KD (64 / 128) and TRELLIS_FF (670 / 885) are unchanged by
the mapper choice, confirming §2.2's observation that those two
columns are exactly additive.

**What abc9 actually does here.** Compare the pre-mapping mux count
with the mapped mux/LUT resources:

| | `$_MUX_` in (stage B) | LUT4 + PFUMX + L6MUX21 out (stage C) | expansion |
|---|---|---|---|
| 1 unit | 2,477 | 7,139 + 3,386 + 1,883 = **12,408** | **5.0×** |
| 2 units | 3,531 | 3,624 + 1,611 + 781 = **6,016** | **1.7×** |

abc9 is depth-oriented (`abc9 -W 300` targets wire delay), and on the
*smaller* netlist it evidently buys depth with very aggressive logic
duplication — roughly 5× the mux resources it was given, against 1.7×
on the larger one. The one-unit netlist is the degenerate case not
because Bluespec elaborated it badly but because its mux cones are
shallow enough that abc9's duplication heuristic runs away.

**This is a toolchain artifact with a one-flag fix, and it has no
bearing on the feasibility conclusions.** §2.2's EBR verdict rests on
DP16KD, which is unaffected. But it does carry one real consequence
for this note: **`-noabc9` lowers the one-unit `mkMBCU` from 7,139 to
3,165 LUT4, a 56 % reduction, so §2's LUT4 figures are pessimistic
wherever abc9 was used.** Corroborating evidence from a different
ECP5 Bluespec design on this machine, `HANDOFF.md`:

> `reqq -abc9  1-4  IDENTICAL to baseline (abc9 a no-op on this
> design; never improves mapping here)`

### 9.6.1 But do *not* conclude "turn abc9 off" — measured, and the opposite is usually true

The obvious inference from §9.6 is "use `-noabc9` for this model". **I
drew that inference, then tested it, and it is wrong.** The one-unit
`mkMBCU` is an outlier, not a representative case.

`mkStretchIO` was run through four controlled cells (`out_pnr/ioctl/`,
script `out_pnr/io_controls.sh`), because the harnessed run in §9.5.4
differed from §2.4 in *two* ways at once (no `share` **and**
`-noabc9`) and that confounds them:

| cell | `share` | LUT mapper | LUT4 |
|---|---|---|---|
| **A** fully stock | kept | abc9 | **8,102** |
| **B** stock `-noabc9` | kept | abc | **21,153** |
| **C** `share` dropped | dropped | abc9 | **8,102** |
| **D** both (what §9.2 uses) | dropped | abc | ≈ 20,430 |

**Cell A reproduces §2.4's 8,102 LUT4 exactly**, which validates this
whole section's setup against the original work byte-for-byte.

**Cell C is identical to cell A — 8,102, to the cell.** So §9.2's
deviation (b), dropping the `share` pass, **costs nothing at all** on
this netlist. That is worth knowing on its own: `share` is the pass
that cost the previous assessment one of its two whole-core runs
(1 h 33 m and counting, §9.1), and it buys zero LUT4 here. Dropping it
is not even an upper bound in practice; it is free.

**Cell B is therefore the decisive one: 21,153 with `share` still in
place.** So the 2.6× inflation is *abc9's absence*, nothing to do with
`share`. On `mkStretchIO`, **abc9 is 2.6× better than stock abc.**

Putting all four measurements of abc9-vs-abc on this codebase
together:

| netlist | abc9 | stock abc | abc9 verdict |
|---|---|---|---|
| `mkMBCU`, 1 unit | 7,139 | 3,165 | **2.26× worse** |
| `mkMBCU`, 2 units | 3,624 | 5,147 | 1.42× better |
| `mkStretchStorage`, 6 units | 13,427 | ≈ 13,400 | neutral |
| `mkStretchIO` | 8,102 | 21,153 | **2.6× better** |

**So abc9 is normally the right choice on this design and the one-unit
`mkMBCU` is a pathological outlier.** The §9.6 diagnosis stands
unchanged — the inversion is created in `map_luts` and nowhere else —
but the remedy is not a blanket flag. `HANDOFF.md`'s "abc9 a no-op on
this design" is itself design-specific and does not generalise either.

**Recommendation, corrected: measure both mappers; prefer abc9; and
distrust any LUT4 figure taken from a degenerate small configuration.**

**And one consequence that must be stated loudly, because it qualifies
§9.3:** since the whole-core runs can only be made to terminate with
`-noabc9` (abc9 hangs, §9.1), **the whole-core LUT4 figure is an upper
bound that may be pessimistic by something like the 2.6× seen on
`mkStretchIO`** — which is itself one of the larger blocks inside the
core. A whole-core LUT4 of *N* under `-noabc9` is therefore consistent
with a real abc9 figure well under *N*, and must not be used to
exclude a device. DP16KD, MULT18X18D and TRELLIS_FF are unaffected by
the mapper choice (measured, three times over), so the §9.3
block-RAM, multiplier and flip-flop conclusions carry no such caveat.

---

## 9.7 What this changes in §4's effort table

- **Item 2, "Revive `nextpnr-ecp5` … 0.5–2 days": strike it.** Four
  working native arm64 builds and a native `ecppack` already exist on
  this machine (§9.0). Cost: zero.
- **Item 4, "Finish the whole-core synthesis measurement … 0.5–1 day":
  partly done and newly scoped.** `MULT18X18D = 36` is measured
  (§9.3), which was the specific number item 4 existed to get. What
  remains of it is the LUT4 total, and §9.2 shows the recipe that gets
  past the two hangs (`share` dropped, `-noabc9`, `stat` before LUT
  mapping, RTLIL checkpoints). The item's note that it "decides 45F vs
  85F" still holds for LUT4, but on multipliers the 45F is already
  shown sufficient.
- **A new item belongs on the list, and it is cheap: the measurement
  harness.** §9.2.1's finding — 3,894 port bits against ~197 IO — means
  *no* board build can instantiate `mkStretchCore` as it stands. The
  129 test ports must be replaced by a real top level (§3.5's UART
  loader) before anything can be placed. That is not extra work, it is
  work item 6 was already going to do, but item 3 ("board wrapper")
  should say explicitly that it is a hard blocker rather than a
  convenience: **until it exists, the only placeable artifact is a
  harness.**
- **Item 10 (move `StretchIO`'s device images into one DP16KD) gains a
  second justification.** §9.6 shows `-noabc9` alone removes 56 % of
  the one-unit `mkMBCU`'s LUT4; the two savings are independent and
  both cheap.

---

## 9.8 Local changes to the repository: the one-unit edit, and its revert

Per §2.2.1 and §8, the one- and two-unit configurations need a
four-line change to `bsv/StretchMemory.bsv`. It was re-made here to
generate the one-unit `mkStretchCore.v`, and **reverted**. The edit
made (identical to §8's record):

```diff
-typedef 6     NumUnits;
+typedef 1     NumUnits;
-typedef 98304 InstalledWords;            // 4 x 16K interleaved + 2 x 16K interleaved
+typedef 16384 InstalledWords;            // 4 x 16K interleaved + 2 x 16K interleaved

 function Bit#(3) unitOf(WordAddr a);
-  if (a < 65536) return {1'b0, a[1:0]};
-  else return {2'b10, a[0]};
+  return 0;
 endfunction

 function UnitIndex indexOf(WordAddr a);
-  if (a < 65536) return a[15:2];
-  else begin
-    Bit#(18) rel = a - 65536;
-    return rel[14:1];
-  end
+  return a[13:0];
 endfunction
```

Revert verification is in §9.8.1. No other repository file was
modified, nothing was committed, and `strap/run_tests.sh` was not run.
All build products — generated Verilog, yosys logs, RTLIL
checkpoints, nextpnr reports and bitstream configs — are in
`<scratch>/out_pnr/`, outside the repository.

### 9.8.1 Revert proof

```
$ shasum stretch/bsv/StretchMemory.bsv
e99e719a45c854523e5f09bd642177cfb51e2dbf   <- byte-identical to the
                                              pre-edit copy taken first
$ git diff --stat -- stretch/bsv/StretchMemory.bsv
(no output)
$ git status --porcelain -- stretch/bsv/
(no output)
$ git status --porcelain
(no output — the whole worktree is clean)
```

---

## 9.9 What is *still* not measurable, and what moved out of this list

### Closed by this section

| §7 item | status now |
|---|---|
| "Whether the design places and routes" | **partly closed.** `nextpnr-ecp5` works (§9.0) and real routing results exist (§9.5). |
| `MULT18X18D` for the FP unit | **closed: 36** (§9.3.1), confirmed twice. |
| "Why the one-unit MBCU measures more LUT4 than the two-unit one" | **closed: abc9's LUT mapper** (§9.6), with a control run and a four-netlist survey (§9.6.1). |
| "Whether the open toolchain lets a 12F use the full 25F die" | **closed: yes** — `--12k` reports 24,288 LUT4 and 56 DP16KD (§9.5.4). |
| The six-unit block-RAM verdict (arithmetic only in §2.2) | **upgraded to a routing result**: nextpnr refuses on DP16KD at unit 2 of 6 on the 85F (§9.5.3). |

### Still open, and why

- **Anything measured on real hardware.** No ULX3S board was
  connected, no bitstream was loaded, nothing was clocked. Every
  figure here is a tool report. `ecppack` exists natively (§9.0) but
  was not run, so **not even a bitstream was produced** — one step
  short of something you could program.
- **Worst-case SDRAM read latency on silicon**, and whether a
  100–166 MHz SDRAM PHY closes timing on a -6 speed grade. §3.1's
  27/32-clock figures remain derived from `Sdram.bsv`'s own FSM
  constants. Nothing here touched the SDRAM path: the designs routed
  are all block-RAM ones. **This is now the largest unmeasured
  quantity in the whole note**, because §9 removed the toolchain
  excuse and the six-unit machine still depends entirely on it.
- **The E-box in isolation.** §1.2's blocker stands unchanged: `mkEBox`
  takes interface arguments, so bsc will not give it its own module
  and a wrapper would be a model change. §9.3's whole-core figures
  include it but cannot attribute anything to it. Note that §9.2.1's
  harness does *not* solve this — the harness reduces pins on an
  existing synthesis boundary, it cannot create one.
- **How much of §2.3/§2.4's logic is the 129 test ports.** §9.2.1
  deliberately *preserves* that logic rather than measuring it; the
  question needs a wrapper exposing only `step`/`halted`/`getPC`,
  which is still a model change.
- **Whole-core Fmax, including the one-unit 45F figure that was the
  point of this exercise.** Both whole-core runs *did* finish
  (§9.3.6a/b) and both *were* handed to nextpnr — but neither reaches
  timing analysis, because **neither places**: 433–826 % `TRELLIS_COMB`
  on every part and configuration tried. **Fmax for the whole core is
  therefore not merely unmeasured but currently unmeasurable**, and
  will stay so until the design's combinational logic shrinks by
  roughly 4×. §9.5.6 bounds it above at ≈ 91.57 MHz from the two
  subsystems that did route, which is the closest thing to an answer
  available.
- **An abc9 whole-core mapping.** The figures above are `-noabc9`;
  abc9 does not terminate on this netlist (§9.1), so the *shipped*
  mapping's exact utilisation is unknown. §9.3.6c shows the verdict
  survives even granting abc9 its largest observed advantage, so this
  is a precision gap, not a verdict gap.
- **What `share` does to the arithmetic**, which is the one quantity
  that could overturn §9.3.4/§9.3.5's capacity verdict. Three attempts,
  none terminating (§9.3.6).
- **Timing margin as `HANDOFF.md` means it.** §9.5's figures are single
  or few-seed results. The 8-seed discipline that project requires
  (min ≥ 10 %, seed 3 ≥ 12 %) was not completed for any design here,
  so no number below should be treated as a ship-grade margin.
- **Power**, unchanged from §7, and not investigated.
- **Whether the 389-section suite is runnable over a serial link in
  acceptable time**, unchanged from §7. `strap/run_tests.sh` was not
  run, per instruction.
- **Anything about MCP**, unchanged from §7.

### How this section ended

Both whole-core runs were left running rather than killed, and **both
finished** — the six-unit at 14:42 and the one-unit at 14:55, roughly
three hours after starting, at loads of 118–282. Both were then routed
(§9.3.6a, §9.3.6b), which is why this section ends with a verdict
rather than a pending item. The artifacts are:

```
out_pnr/logs/core6.statC   core6.json (445 MB)   logs/core6_unc.log
out_pnr/logs/core1h.statC  core1h.json (436 MB)  pnr/core1h-{45k,85k}-50M-s3.log
out_pnr/logs/*.coarse.il   *.premap.il           (RTLIL checkpoints)
```

**The thing to do next is not another measurement, and it is also not
one more item on §4's list.** Every device axis except combinational
logic has been measured and fits; logic overruns by **4.3× even on the
largest part**; and the structure most implicated is the register-file
index multiplexing (§9.3.6's three convergent lines).

**But the arithmetic has to be faced honestly.** §4 item 10 and §3.6
propose moving `StretchIO`'s device images into one DP16KD, and §2.4
prices that whole block at **8,102 LUT4 — about 3 % of 271,449.** Even
eliminating all three register files outright does not approach a 4×
reduction. So:

- moving register files into block RAM is **a** direction, not **the**
  fix, and the block RAM to do it with is certainly available (a
  one-unit build uses 30 % of an 85F's EBR);
- **nothing currently in §4's effort table addresses a 4× logic
  overrun.** Items 2–9 are all about getting a design that fits onto a
  board; none of them makes the design fit. The roadmap needs
  rethinking at the level of §6's observation that *"a byte-serial
  datapath is small; a 5,019-line combinational one is 100k lines of
  Verilog"* — i.e. the idiomatic-Bluespec / multi-cycle-E-box rewrite
  that `AGENTS.md` plan §1c already contemplates, which §6 argues the
  FPGA is "an argument for finishing". **This section is now a
  measured argument for exactly that, and the strongest one available:
  4.3×.**

Before committing to any of it, measure one register file's conversion
in isolation. A 4× gap is not closed by guesswork.

### A new one, discovered here

- **Whether `mkStretchCore` can be placed at all in any configuration.**
  §9.2.1 shows it has 3,894 port bits against ~197 IO, so the answer
  for the design *as it stands* is **no** — what §9.5 routes is the
  core plus a harness that reduces those pins. **Nothing resembling a
  board build exists until §3.5's UART loader replaces those ports**,
  and no measurement here substitutes for that.

---
