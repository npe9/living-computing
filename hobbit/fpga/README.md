# ULX3S board build for the ATT92010 Hobbit model

This directory turns the Bluespec Hobbit core into a bitstream for the ULX3S
(Lattice ECP5 `LFE5U-85F`, CABGA381, 25 MHz board oscillator). The program on
the board is the same `bsv/smoke.hex` image the Bluesim smoke test runs: the
build regenerates the Bluespec word table from that file, so the FPGA and the
simulator executed identical bytes.

The board adds three things to the core: the image load, the power-on reset
gate, and an HRI line writer that sends every retirement record out of the
FTDI UART in exactly the format `tests/hri_check.py` parses. The LEDs report
the core's state. The core, its golden pre-state and its retirement records
are the ones documented in `bsv/HobbitSmoke.bsv` and `bsv/HobbitCore.bsv`:

| state | value | source |
|---|---|---|
| PC | 0 | reset PC, p. 1-35 |
| CONFIG | 0 | p. 1-35 |
| PSW | 0x200 | bit 9 selects CSP = SP, Table 1-8 sheet 2, p. 1-15 |
| SHAD | 0x100 | the model always sets SHAD = SP |
| SP | 0x100 | shared pre-state |
| MSP | 0x180 | shared pre-state |

## Files

| file | role |
|---|---|
| `bsv/HobbitUlx3s.bsv` | `(* synthesize *)` board top: image load, start, HRI retirement queue, UART writer, LEDs |
| `bsv/HobbitUlx3sTop.v` | pin wrapper `ulx3s_top`: board pins and the power-on reset from BTN1 |
| `fpga/ulx3s_85f.lpf` | only the pins this design uses, plus `FREQUENCY PORT "CLK" 25 MHZ` |
| `fpga/build.sh` | image regeneration, bsc, yosys, nextpnr, ecppack |
| `fpga/build/` | every build product (gitignored) |
| `fpga/dev/Sonic.bsv`, `fpga/dev/EspLink.bsv` | the SONIC-subset descriptor engine (register port, DMA master port) and the UART link to the ESP32, replayed against p9boot.Sonic and relay.c (`fpga/dev/sonic.md`) |
| `fpga/esp32_ethrelay/` | ESP32 firmware (ESP-IDF v5.3; not yet built for the target) relaying the board's Ethernet frames over WiFi to `tools/qemu1e/hub.py`; the link protocol is tested on the host by `tests/test_ethrelay.py` (`docs/ulx3s_ethernet.md`) |

## Board behaviour

* **Clock**: 25 MHz on `CLK` (pin G2).
* **Reset**: `BTN1` (pin R1) is active high. Pressing it holds the design in
  reset; releasing it lets an 8-bit counter run from 0x00 to 0xFF (255
  clocks, 10.2 us), and then `RST_N` rises. The board then loads the 160-word
  image through the memory's synchronous write port (160 clocks), warms the
  prefetch buffer from the synchronous read port (64 words, one per clock),
  and starts the core at PC 0 when `prefetchReady()` is high.
* **`wifi_en`** (pin F1) is driven low; **`ftdi_txd`** (pin M1) is constrained
  but unused this milestone.

LEDs are active high:

| LED | meaning |
|---|---|
| `led[7]` | **faulted**: the core trapped (the unimplemented parcel at PC 0x0BA, p. 1-39). This is the model's halt state; `halted()` == `faulted()`. |
| `led[6]` | **started**: the image is loaded and `start()` has run. |
| `led[5:0]` | **PC[5:0]**: low six bits of the architectural PC. The bar walks while the program runs and freezes at `0xBA[5:0] = 0x3A` when the trap lights `led[7]`. |

## UART

`ftdi_rxd` (pin L4) is an 8N1 transmitter at 115200 baud, so 25 MHz / 115200 =
217 clocks per bit (truncated; the caller owns that number and passes it to
`mkHriWriter(217)`). The line is idle high.

One line leaves for every retirement, in order, in the format the simulation
prints and `tests/hri_check.py` parses:

```
HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d cyc=%d\n
```

The fixed part is 116 bytes; `" cyc="` adds 5, the shortest decimal cycle
count adds 1 to 10, and the newline adds 1, so **a line is 123 to 132 bytes**.
The worst case is 132 bytes = 1320 bits = 286,440 clocks = 11.46 ms per line
at 115200 baud. The smoke image retires exactly 41 records (`sim_smoke` prints
41 HRI lines), so a board run streams about 41 lines in roughly 0.42 s to
0.47 s depending on the digit count of the cycle field.

The core presents each record for exactly one clock: `hriValid()` marks that
clock and `hri()` is the complete record, including its own SP/MSP after
values and the `cyc` stamp. The board copies every presented record straight
into the queue, so nothing is reconstructed, patched, coalesced or dropped.

The core has no stall hook (its execute and retire rules are internal), so a
retirement queue is the only lossless way to bridge a core that runs in a few
hundred clocks to a UART that needs about 10 ms per line. The queue is
`mkSizedBRAMFIFOF(48)` — 48 records × 299 bits = 14,352 bits in the ECP5's
block RAM (bsc emits `BRAM2`; 8 DP16KD in this build), not a register file, because
the 48-way push mux plus the 48:1 pop mux of a register version cost about
19k LUT4s and overran the device. The fixed smoke image retires 41, so the
48-deep FIFO never fills and no record can be dropped. A program with more
than 48 retirements would need a deeper queue or a core stall hook.

### Capturing the lines

```
stty -f /dev/tty.usbserial-XXXXXXXX 115200 cs8 -cstopb -parenb
cat /dev/tty.usbserial-XXXXXXXX
```

The lines are the same bytes `sim_smoke` prints and `tests/hri_check.py`
accepts.

## Building

```
cd hobbit/fpga
./build.sh
```

`build.sh` runs (all products in `build/`):

```
python3 ../bsv/mk_image_bsv.py ../bsv/smoke.hex SmokeImage > build/SmokeImage.bsv
bsc -verilog -g mkHobbitUlx3s -u \
    -vdir build -bdir build -info-dir build \
    -p "../bsv:$BLUESPECDIR/Libraries" ../bsv/HobbitUlx3s.bsv
yosys -p "read_verilog build/mkHobbitUlx3s.v;
          read_verilog ../bsv/HobbitUlx3sTop.v;
          read_verilog $BLUESPECDIR/Verilog/FIFO2.v;
          synth_ecp5 -top ulx3s_top -json build/ulx3s_top.json"
nextpnr-ecp5 --85k --package CABGA381 --speed 6 \
    --json build/ulx3s_top.json --lpf ulx3s_85f.lpf \
    --textcfg build/ulx3s_top.config --freq 25 --timing-allow-fail --seed 1
ecppack --compress build/ulx3s_top.config build/hobbit_ulx3s.bit
```

Notes on the flow:

* `bsc` is resolved from the newest Homebrew Cellar install unless `BSC_BIN`
  is set; `BLUESPECDIR` must be its `../libexec/lib`. `-p` replaces bsc's
  default package path, so `$BLUESPECDIR/Libraries` is listed explicitly.
  `-vdir build` keeps the generated Verilog (and `-bdir` the `.bo` files) out
  of the source tree.
* `synth_ecp5 -top ulx3s_top` uses the Verilog wrapper as the top, because the
  LPF constrains the wrapper's board pins. `mkHobbitUlx3s` is instantiated
  inside it and yosys checks the whole hierarchy.
* bsc leaves one library cell un-inlined, `FIFO2` (the decoded-instruction
  register); its Verilog from the bsc distribution is read alongside our two
  files. The library's readmem-based RAM models are not pulled in.
* `--timing-allow-fail` keeps the bitstream even when 25 MHz is missed. The
  measured frequency and critical path are reported below. **Timing closure is
  not a goal**: cycle-level behaviour does not depend on the clock frequency,
  so the board runs the same instruction sequence and the same cycle counts at
  whatever clock the tools achieve; wall-clock speed is not a goal, and
  nothing in the design was changed to gain frequency.

Tool versions used (verified on this machine):

| tool | version |
|---|---|
| bsc | `Bluespec Compiler, version 2026.01 (build 9bd39e6f3)` |
| yosys | `Yosys 0.51 (git sha1 c4b5190229616f7ebf8197f43990b4429de3e420, clang++ 16.0.0 -fPIC -O3)` |
| nextpnr-ecp5 | `"nextpnr-ecp5" -- Next Generation Place and Route (Version nextpnr-0.6)` |
| ecppack | `Project Trellis ecppack Version 1.4` |

## Programming the board

`openFPGALoader` is installed here; when `build.sh` succeeds, the bitstream
is the ecppack output. (The rebuilt design currently does not fit, so
`build/hobbit_ulx3s.bit` is not produced — see Results below.)

```
openFPGALoader -b ulx3s build/hobbit_ulx3s.bit         # volatile SRAM
openFPGALoader -b ulx3s -f build/hobbit_ulx3s.bit      # SPI flash
```

## Results of the final design (2026-11-19)

`./build.sh`, after the array conversion (every storage array is a `RegFile`,
one write port each; see `docs/area_analysis.md`) and the single-rule stage
fix. bsc emits Verilog that instantiates `RegFile`, `BRAM2`, `SizedFIFO` and
`FIFO2`; `build.sh` discovers each and reads its bsc library model.

```
yosys:   Number of cells: 19776
           LUT4 11367   PFUMX 1407   CCU2C 1094
           TRELLIS_FF 5066   TRELLIS_DPR16X4 654   DP16KD 18

nextpnr: TRELLIS_COMB: 18041/83640    21%
         TRELLIS_FF:    5066/83640     6%
         DP16KD:          18/  208     8%
         TRELLIS_IO:      13/  365     3%
         Max frequency for clock '$glbnet$CLK$TRELLIS_IO_IN':
             25.66 MHz (PASS at 25.00 MHz)   [an earlier placement: 37.66 MHz]

ecppack: build/hobbit_ulx3s.bit   593,803 bytes
```

So the design **places and closes timing on the LFE5U-85F**: 21% of the
combinational cells, 6% of the flip-flops, 18 of 208 block RAMs, and the
25 MHz board clock met. The whole flow takes about 108 s on this machine.
Attribution of the 11,367 LUT4 (`tools/area_netlist.py`):

| block | LUT4 | PFUMX | FF | BRAM |
|---|---:|---:|---:|---:|
| prefetch (3-way, 3 x 1 KB) | 1875 | 289 | 178 | 0 |
| PDU | 312 | 44 | 346 | 0 |
| decoded store (32 x 192) | 1264 | 57 | 38 | 0 |
| stack cache (64 x 32) | 2508 | 340 | 341 | 1 |
| program memory (256 x 32) | 1040 | 184 | 297 | 1 |
| HRI queue (48 deep) | 313 | 4 | 882 | 8 |
| HRI presentation | 1008 | 2 | 459 | 0 |
| UART writer | 1292 | 87 | 397 | 0 |
| board glue | 111 | 31 | 12 | 0 |

For comparison, the same design with `Reg#(Vector#(...))` storage needed
83,272 LUT4 (99.6%) and did not place; the memory alone was 35,247 LUT4
there. The array idiom was the area problem.

**Superseded runs, kept as flow evidence.** Before the array conversion the
BRAM-queue build reached `TRELLIS_COMB 83272/83640 (99%)`, `TRELLIS_FF
24642 (29%)`, `DP16KD 26` and failed placement
(`ERROR: Unable to find legal placement for all cells`); `--placer heap`
failed identically and `--placer sa` seed 1 hit an 1800 s timeout still
placing. The pre-`cyc` build reached 126,259 LUT4 (150%). Neither produced a
bitstream.

## Pre-`cyc` baseline (superseded, kept as flow evidence)

Before the core gained the `cyc` field and the single-port synchronous
memory, the same flow was run end to end to prove the tool path early. bsc
2026.01 produced `build/mkHobbitUlx3s.v` (1,060,374 bytes) and yosys 0.51
`synth_ecp5 -top ulx3s_top` finished (170,120 cells). nextpnr-ecp5 accepted
the LPF and packed the design, then ran out of logic:

```
Info:     Total LUT4s:     126259/83640   150%
Info:      Total DFFs:     23621/83640    28%
ERROR: Unable to place cell 'hobbit.IF_IF_core_pcReg_..._LUT4_Z_3', no BELs remaining to implement cell type 'TRELLIS_COMB'
```

(the cell name in the error is abbreviated here with `...`; the rest is
verbatim). nextpnr also printed `TRELLIS_COMB: 126749/83640 (151%)` and
`TRELLIS_FF: 23621/83640 (28%)`. There was no bitstream and no Fmax to
report because place-and-route never reached timing. The cause was the old
`mkHobbitMem`: a 256×32 register array read combinatorially through six
ports. The pin constraints, device, package, `--freq`, and `ecppack` were
independently proven in the same run window with a tiny module that has
exactly this wrapper's ports: the LPF was accepted, nextpnr placed it
(9 LUT4, 8 DFF, 457.04 MHz) and ecppack wrote a 280,209-byte bitstream.

This baseline is not the shipped design; the numbers below are the rebuilt
one.

## Verification before the board

The relay and the queue were checked in Bluesim with a throwaway harness (not
part of the repository) that instantiates `mkHobbitUlx3s`, receives
`ftdi_rxd` at 217 clocks per bit and reassembles the lines. In the rebuilt
(`cyc`-carrying, synchronous-memory) design the board produced exactly 41
lines, 5043 bytes, and all 41 were byte-identical to the 41 HRI lines the
core printed in the same run; every line was 123 bytes (the smoke's cycle
counts are 0 to 8, one decimal digit), and the whole stream took 11,548,517
clocks (about 462 ms at 25 MHz). The pre-`cyc` build was checked the same way
(41 lines, 4797 bytes, 10,414,387 clocks).

## Credits

**Flute: a free and open-source RISC-V CPU and SoC.**
© 2021 Rishiyur S. Nikhil and Bluespec, Inc., Apache License 2.0. The board
boundary here follows Flute's structure — a wrapper that owns clock and reset
(`src/ULX3S_Top.bsv`, `src/ClockHacks.bsv`), with the core module seeing only
its memory port, its `rst_n` argument and its retirement trace port. No Flute
source is copied; see `docs/bluespec_architecture.md` for the reference-tree
commit and the licence terms.

**bsc BRAMFIFO library.** `mkSizedBRAMFIFOF` (48 × 299 bits) is a module of the
Bluespec compiler's standard library (`BRAMFIFO.bo`, Apache-2.0 with the bsc
distribution), not of Flute; it is what puts the retirement queue in block RAM.

### Library cells bsc does not inline

bsc emits some library modules by instantiation instead of inlining them, and
yosys stops with ``Module `\RegFile' referenced ... is not part of the
design'' unless the model is read. `build.sh` scans the generated Verilog for
instantiated library cells and reads `$BLUESPECDIR/Verilog/<cell>.v` for each,
so `RegFile.v` is picked up automatically when an inferred memory appears
(`RegFileLoad.v` too, if the array carries a load file), alongside
`SizedFIFO.v` and `BRAM2.v` today.

`RegFile#(addr, T)` is also the Bluespec idiom that infers memory at all:
measured in BSV on this flow (`docs/area_analysis.md`), 256×32 with one `upd`
and a registered read address is 1 DP16KD + 39 LUT4, 64×32 with a
combinational read is 56 LUT4 + 1 DP16KD, and 32×192 with a combinational read
is 200 LUT4 + 96 DPR16X4 — against 35,247 / 12,107 / 6,826 LUT4 for the same
arrays written as `Reg#(Vector#(N,T))` with `update`. That is the size
difference the core's array conversion is closing.

### Placer/seed sweep on the BRAM-queue netlist (measurement, not final design)

On the 48-record block-RAM queue netlist (83,272/83,640 LUT4), the analytic
placer fails:

```
nextpnr-ecp5 --85k --package CABGA381 --speed 6 --json build/ulx3s_top.json \
  --lpf ulx3s_85f.lpf --textcfg build/top_heap2.config --freq 25 \
  --timing-allow-fail --seed 2 --placer heap
=> ERROR: Unable to find legal placement for all cells, design is probably at utilisation limit.
```

The simulated-annealing placer did not finish: `--placer sa --seed 1` was
stopped by a 1800 s timeout (`rc=124`) before legalizing, and `--placer sa
--seed 2` was not reached (the enclosing job's 3600 s limit). No
`build/sa1.config` or `build/sa2.config` was produced and no bitstream was
written. At 99.6 % LUT occupancy this netlist does not place with either
placer; the remaining headroom has to come from area (the core's
`RegFile`/memory conversion and the writer's serial `cyc` conversion), not
from placer choice.
