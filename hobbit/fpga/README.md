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

## The SoC: the privileged core on SDRAM (2026-11-24)

This is the Plan 9 board build. The `smoke.hex` build above is the
earlier one and still works.

| file | role |
|---|---|
| `bsv/HobbitSocCpu.bsv` | `mkHobbitSocCpu`: `mkHobbitCoreSystem` with its three memory faces turned into ports |
| `rtl/hobbit_soc_mem.v` | the core's clock gate, write/read service, the combinational window |
| `rtl/sdram_word.v` | one-word SDRAM controller for the W9825G6KH, written here. The board facts (CL2, the ODDRX1F clock, the DQ input register) follow the Flute ULX3S tree, which had no licence file when this was written; see `IP_PROVENANCE.md` |
| `rtl/hostlink.v`, `rtl/uart8n1.v` | the framed host link on the FTDI UART: loader, start, I/O forwarding |
| `rtl/hobbit_soc.v` | the SoC: address map, backend router, ROM block, I/O bus |
| `rtl/ulx3s_hobbit_top.v` | pins, power-on reset, DCCA, SDRAM clock ODDRX1F, DQ I/O register |
| `ulx3s_soc.lpf` | clock, button, LEDs, UART, WiFi enable, SDRAM |
| `build_soc.sh` | bsc, yosys, nextpnr, ecppack into `build/soc/`; `build_soc.sh stub` builds the periphery alone into `build/soc-stub/` |
| `rtl/cpu_stub.v` | same-ported stand-in for the core, for `build_soc.sh stub` only |
| `area_cpu.sh` | synthesis-only area of `mkHobbitSocCpu`, optionally from a variant source tree |
| `sim/run_soc.sh` | Verilator co-simulation: the SoC boots s9term against the reference |
| `sim/sdram_model.v`, `sim/soc_sim_top.v`, `sim/soc_main.cpp` | its SDRAM model, top and driver |

### The core's clock and its memory

The core is written against three memory faces:

* `HobbitMem`, which is synchronous. `readReq` registers an address and
  `readData` returns that word on the next clock.
* The MMU's table walk (`MmuTables.read`), which is combinational.
* The event unit's vector memory (`HobbitEventMem.read`), also combinational.

An SDRAM can answer none of them in time. The core also has no stall
input. The SoC therefore stalls it from outside: the core runs on a gated
copy of the system clock (an ECP5 `DCCA` whose CE changes on the falling
edge). Between two core edges the core's registers hold. Its
combinational logic meanwhile shows what the next edge will do: the read
it will register, the writes it will make, and the words its walks and
event sequence will read. `hobbit_soc_mem` makes memory agree with that
before it allows the edge:

1. On a core edge it captures the edge's writes (memory face, PTE R/M
   writeback, event frame) and its read request.
2. It performs the writes in that order and then the read. The read's
   word stays on `rdData`, and a later write to the same address updates
   it, because `mkHobbitMem`'s `readData` reads the array as it stands.
3. It registers the core's **combinational probes** and fills a
   16-entry associative window until every probe in RAM or ROM hits. A
   probe at any other address is entered as 0.
4. Then it sets `fire`, and the next rising edge is a core edge.

The probes are computed in the core (`HobbitCore.combProbes`,
`HobbitMmu.walkProbe`/`walkProbes`, `HobbitEvents.combProbes`). They
replicate the walk's predicate (translation on, no TLB hit, no NPSR hit)
for the four noted face translations. They also cover the event unit's
frame and vector translations and the vector word, plus VB, which KCALL
reads in EU_S2. Nothing in the machine reads them, so every simulation
is unchanged.

A probe that depends on a word just fetched (a page entry selected by a
segment entry) settles in a second round. The window is read through
`winRead`, so a walk that a probe failed to name would read 0. The
co-simulation below would catch that as a record mismatch.

The core counts its own clocks, so its retirements, and its `cyc`, do
not depend on how many system clocks each core clock took.
nextpnr times the gated domain and every crossing at the full system
clock period. It derives the gated clock's constraint through the DCCA
(checked on a two-register prototype before this design: "Derived
frequency constraint of 25.0 MHz for net gclk", with both crossings
reported and timed).

### Memory map

From `tools/p9boot.py`, which follows `io.h`:

| physical | SoC |
|---|---|
| 0x00000000-0x00003FFF | ROM block RAM, 16 KB, loaded by the host (the fpi image is 13 KB at +0x20) |
| 0x00004000-0x0007FFFF | rest of PROMBASE: forwarded |
| 0x80000000-0x81FFFFFF | SDRAM, 32 MB (the kernel is told 8 MB in PPage0, as in p9boot) |
| 0xB0000000 + | IOACK: incon +0x000, iic +0x080, quart +0x100, lcd +0x3000 |
| 0xB8000000 + | IONAK: ioctl +0x000, irq +0x080, scsi +0x100, rtc +0x2000-0x3FFF |
| 0xA4400000 | SONIC |
| anything else | forwarded |

Until a device's RTL lands in `rtl/hobbit_soc.v`'s I/O bus, every I/O
access is forwarded over the host link. That includes the ROM above
16 KB and any unmapped address.

### The host link

`rtl/hostlink.v` runs on the FTDI UART (8N1, 1 Mbaud by default, CPB =
25 at 25 MHz). Multi-byte fields are big-endian.

| host → board | | board → host |
|---|---|---|
| `P` | ping | `p` st clk5 ret4 |
| `W` a4 d4 | write a word | `w` |
| `R` a4 | read a word | `r` d4 |
| `B` a4 n2 d4×n | write n words | `b` |
| `G` e4 | start at the entry (the ROM's hand-off: SP = MSP = PSW = 0) | `g` |
| `D` d4 | answer to `F` | |
| `I` l1 | interrupt level from the host's models (7 = none) | |
| | | `F` k1 a4 d4 clk5: a forwarded access (k = 0 read, 1 write); the board waits for `D` |
| | | `T` clk5: every 2^18 core clocks |

`clk5` is the core's own clock count, which is the host models' time base.
The loader (step 3) is `B` over RAM and the ROM block, then `W`s for
PPage0, then `G`. The forwarding mode (step 2) has the host answer `F`
from `tools/p9boot.py`'s device models.

### Verification of the SoC

`fpga/sim/run_soc.sh RECORDS` boots the shipped kernel (s9term) on the
whole SoC in Verilator. That covers the gated core, the adapter,
`sdram_word.v` against a behavioural W9825G6KH model with timing checks
(`sim/sdram_model.v`), and the host link at the UART pins. Every retirement
record is compared with the reference boot by `tools/p9coreboot.py`, as
`bsv/run_p9kern.sh` does for the bare core. The driver (`sim/soc_main.cpp`)
plays the host. It answers every forwarded access from the recording
(`bsv/p9kern.c`) and replays the recorded interrupt.

Result of `run_soc.sh 2893000` on 2026-11-24:

```
SOC end: the reference's last record; 2893027 records, 9920333 core clocks,
  104939750 system clocks (10.58 per core clock), 16497 forwarded reads,
  16526 forwarded writes
P9KERN devices: 181 of 181 recorded reads replayed, 0 repeated, 16316
  unrecorded (mispredicted path), ...; 16526 of 16526 writes matched, 0 differed
MATCH: 2893000 records agree in every field but cyc (2865913 also agree in cyc)
SOC console: 74 bytes, identical to the reference boot's
```

The same run's 2,893,000 HRI lines (`grep '^HRI' core.log`) are
byte-identical, `cyc` included, to the bare core's for the same records
(`bsv/run_p9kern.sh`, the same `HobbitCore.bsv`). So the gating is invisible
to the core.

The test is discriminating. Dropping the page-entry probe makes the run fail
at record 2849643, the first access to a paged stack address. The observed
lines are in `run_soc.sh`'s header.

**Unrecorded I/O reads.** `p9kern.c` calls the 16,316 unrecorded reads
"mispredicted path", meaning any read that the reference boot did not
record. `$SOC_IOLOG` (`build/socsim/io.log`) shows two different kinds,
matched against `rec/ref.hri`:

* **16,314 are read-modify-writes of halfword stores.** There are 16,256
  reads of `b0003004` and 58 of `b0003000`, the LCD. Every one is followed
  by a write to the same address 1 or 2 retirements later: 12,221 at +1,
  4,035 at +2 and 58 at +1. Every reference record of those writes is
  `insn=c6730000` with `mask=03`, a halfword store. `HobbitMem` writes whole
  words, so the core reads the word and writes it back merged. The bus
  therefore carries byte enables 4'hF and a full-word write. A device
  register whose read has side effects would see a spurious read, and the
  other halfword would be rewritten. The fix is real byte enables from the
  core's store path to the bus, which the device contract already has.
* **2 are extra reads of the SONIC `cr` (`a4400000`).** After each of the
  writes of 0x100 and 0x200, the poll reads `cr` twice, at retirements
  2681150/2681151 and 2681583/2681584. The reference has one read for each.
  These are true extra reads, either a wrong-path read or a reissue.

In this prefix every Quart read was architectural. Before the Quart's RTL
goes behind the bus (its reads pop the RX FIFO), the core needs byte-enabled
stores, and either a guarantee or a drain that keeps an I/O-space read from
being issued twice or speculatively.

### Area, Fmax and the clock (step 1)

`./build_soc.sh` (seed 1) on 2026-11-24:

```
yosys:   LUT4 97461   CCU2C 4167   TRELLIS_DPR16X4 1508   TRELLIS_FF 12480
         DP16KD 8   MULT18X18D 11
nextpnr: TRELLIS_COMB: 115955/83640   138%
         TRELLIS_FF:    12480/83640    14%
         TRELLIS_RAMW:   1508/10455    14%
         DP16KD:            8/  208     3%
         MULT18X18D:       11/  156     7%
ERROR: Unable to place cell '...LUT4_Z_27', no BELs remaining to implement
       cell type 'TRELLIS_COMB'
```

**The SoC does not fit the LFE5U-85F.** The privileged core alone is the
overrun. `./area_cpu.sh` synthesises `mkHobbitSocCpu` (the core plus its
port glue) by itself:

| variant | LUT4 | CCU2C | DPR16X4 | FF | DP16KD | MULT18 | COMB est. |
|---|---:|---:|---:|---:|---:|---:|---:|
| as built (`probes`) | 95,215 | 4,183 | 1,530 | 12,002 | 9 | 11 | 112,761 |
| probe port tied Invalid (`noprobe`) | 95,634 | 4,189 | 1,530 | 12,002 | 9 | 11 | 113,192 |
| prefetch ways stubbed to 0 (`nopf`, a lower bound) | 90,907 | 4,217 | 90 | 11,724 | 9 | 11 | 99,881 |
| bsc `-opt-undetermined-vals -unspecified-to X` (`unspecx`) | 93,827 | 4,243 | 1,530 | 11,994 | 9 | 11 | 111,493 |
| `synth_ecp5 -abc9` | 95,215 | 4,183 | 1,530 | 12,002 | 9 | 11 | 112,761 |

"COMB est." is LUT4 + 2 x CCU2C + 6 x DPR16X4. That formula reproduces
nextpnr's "Total LUT4s: 114843" for the full build exactly. The device has
83,640.

The abc9 row is identical because yosys 0.51's `synth_ecp5` already uses
abc9 by default. Even the two real savings together (the whole prefetch
store, about 12.9k, and the don't-care folding, about 1.3k) leave about
98k, still 18% over before any device is added. Fitting the privileged core
needs a redesign of its area, not a flag.

The smoke build above (11,367 LUT4) is no measure of this core.
`bsv/HobbitUlx3s.bsv` instantiates `mkHobbitCore`, which is
`mkHobbitCoreImpl(..., mkMmuTablesNull, events False, system False, ...)`
(`bsv/HobbitCore.bsv`). bsc elaborates that without the table walk, the
event sequences and the privileged machine. Its prefetch box was 1,875 LUT4
with no DPR16X4. Here the prefetch is 14,512 LUT4 plus 1,440 DPR16X4, by
cell name. That difference is the first place to look for area.

The combinational probes cost nothing measurable. The variant whose probe
port is tied to Invalid (`build/noprobe_bsv`) came out no smaller. Name-based
attribution (`yosys` cell names) puts 19.8k LUT4 under `probes`, but those
are the walk and TLB logic that the probe nets merely name.

The adapter's 16-entry window now uses a serial scan, one probe per system
clock. A parallel 22 x 16 matcher cost 26k LUT4 and is gone.

**The periphery places and meets 25 MHz.** `./build_soc.sh stub` replaces
the core with `rtl/cpu_stub.v`, a same-ported shift register that keeps every
adapter input and output live:

```
nextpnr: TRELLIS_COMB: 9998/83640 11%   TRELLIS_FF: 3550   DP16KD: 8   DCCA: 2
         Max frequency for clock '$glbnet$CLK$TRELLIS_IO_IN': 34.70 MHz (PASS at 25.00 MHz)
         Max frequency for clock 'gclk': 328.30 MHz
         CLK -> gclk 92.11 MHz, gclk -> CLK 296.47 MHz
ecppack: build/soc-stub/hobbit_soc.bit, 461,434 bytes
```

After the RTC's I2C pins were reserved (below), the same build gave
33.61 MHz for the system clock and 325.95 MHz for `gclk`, with 54
TRELLIS_IO in use; both still pass 25 MHz.

The critical path is the adapter's probe scan (`pi` into the window compare).

**The clock is the 25 MHz board oscillator, with no PLL.** The periphery
closes there with about 34% slack. The core's own Fmax is unknown until it places.
nextpnr times the gated domain at the system clock's period, so the core
must also meet 40 ns, a whole core clock in one system clock. At 10.58
system clocks per core clock in the boot above, the core clock averages
about 2.4 MHz. Wall-clock speed is not a goal (see "Building"),
and nothing depends on it except the host models' time base, which is the
core's own clock count.

What would make it fit (not done here):

* Move the prefetch ways (combinational-read `RegFile`s, replicated per
  read port into DPR16X4 plus mux trees) into DP16KD. The gated clock
  allows this: a block RAM read on the free-running clock settles inside
  the ~10 system clocks between core edges. The bound above is at most
  12.9k COMB.
* The remaining ~87k COMB is spread across the pipeline's datapath:
  stack cache, operand and result muxes, MMU, event unit. It has to
  shrink by about a third, for example by multi-cycling the rare paths on
  the gated clock or by moving the stack cache to block RAM. That is core
  work, and it needs the lead's decision on scope.

### The kernel load (step 3)

`tools/p9link.py emit OUT` writes the byte stream that loads the kernel
over the host link:

* `B` frames put the fpi image into the ROM block. These are
  `p9boot.Rom`'s words below 0x4000.
* `B` frames write RAM. This is the memory `p9boot.Boot` starts from:
  s9term's text and data plus PPage0 (memsize 8 MB, argc 0, env 0, and the
  fpi vector at +0x74).
* `G` sends the entry.

By default every word of the 8 MB is sent, because SDRAM powers up holding
no particular value. That is 8 MB at 1 Mbaud, about 90 s. `--sparse` sends
only the nonzero words (70,953 RAM and 1,582 ROM words, 768 frames,
295,514 bytes), which is correct where RAM is known to be zero.

`SOC_LOAD=1 fpga/sim/run_soc.sh N` checks the stream. The co-simulation
loads RAM and ROM through the UART pins with the sparse stream and no back
door. It sends one frame per reply (`b`, then `g`), and must then reach
the same MATCH. On 2026-11-24, `SOC_LOAD=1 run_soc.sh 2893000` gave "SOC
load: 768 replies, 0 frames unsent", then "MATCH: 2893000 records agree in
every field but cyc" and the identical 74-byte console. With the `B`
address step injected as +8, it failed at record 3 in `_startup`, where
the core fetched 00000000; the header of `run_soc.sh` has the details. This exercises `hostlink.v`'s `B`/`G` path and the
adapter's aux port, which the back-door load never touches.

Not done: the host session that sends the stream over the serial port and
then answers `F` from `tools/p9boot.py`'s device models. The models need
the board's `clk5` as their time base. Until that exists, the run
procedure below cannot be carried out.

### Device integration (pending)

The device modules are on master under `fpga/dev/`: Quart and intc, RTC and
IIC, and Lcdisp/HDMI. They are not yet in `rtl/hobbit_soc.v`'s I/O bus.
Three things block them:

* the fit (above);
* byte-enabled stores and no repeated I/O reads ("Unrecorded I/O reads"
  above), because Quart reads pop its FIFO;
* an oracle for live interrupts. Once the intc drives the core's IL, the
  recorded-interrupt replay (`armInterrupt`) no longer applies.

The parameters for when they are wired, as given by the device agents on
2026-11-24:

* `Irq.sources`, driven every clock: bit 1 = Quart `irq`; bits 5, 8, 9 and
  10 = incon, SCSI DMA, SONIC and SCSI.
* Quart: tie the unused `txOut` streams (channels 1-3) to always-ready
  sinks. At 25 MHz, `clksPerBit` = 1302 (19200 baud) and `ctNum`/`ctDen` =
  1152/125000.
* RTC: `mkRtc#(ticksPerSec, startBcd, mcpMode, i2cQuarter)`. `ticksPerSec`
  and `startBcd` default to 0 and must be set. The board setting is
  `mcpMode` 3 and `i2cQuarter` 63 at 25 MHz. Its window is 8 KB
  (`0xB8002000`-`0xB8003FFF`), so the bus offset must be 13 bits; the
  contract's 12 is too narrow.
* The I2C pins `gpdi_sda` B19 and `gpdi_scl` E12 are reserved in
  `ulx3s_soc.lpf` and released in `rtl/ulx3s_hobbit_top.v`. The RTC assumes
  it is alone on the DDC bus.
* IIC: EEPROM byte 12 is the CPU MHz (`iic_eeprom.py --clock 25`).
  `rtc_nvram.hex` and `iic_eeprom.hex` are resolved against the working
  directory.
* yosys must read bsc's `RegFileLoad.v` with `read_verilog -defer`.
* The LCD/HDMI build uses a 65/325 MHz PLL (`dev/hdmi_lcd.md`), and its
  shift clock is seed-sensitive.

### Hardware window: run procedure (not yet runnable)

No board action has been taken. The board is in use by the Linux Flute
session. There is no bitstream of the full SoC because it does not place.
The stub bitstream computes nothing and must not be loaded. When a
full-SoC bitstream exists, the procedure for an owner-approved window is:

1. Confirm with the owner that the Flute session has released the board.
   Use only the FTDI port named for the window. Do not touch the microSD.
2. `openFPGALoader -b ulx3s build/soc/hobbit_soc.bit`. This writes volatile
   SRAM; never use `-f` (flash) in a shared window.
3. LEDs: `led[5]` (SDRAM initialised) lights within 1 ms of reset.
   `led[7:6]` (stopped, running) stay dark until `G`.
4. Host: open the FTDI port at 1,000,000 baud, 8N1. Send `P`; expect
   `p` (status byte, core clock count, retired count 0).
5. Load: send `tools/p9link.py emit`'s stream without `--sparse`, one frame
   per reply (`b`), as `sim/soc_main.cpp` does with `SOC_LOAD`. Its last
   frame is `G 80004000`, answered `g`. To check the load, send `R` for a
   sample of addresses before that last frame.
6. Answer every `F` with `D` from `tools/p9boot.py`'s device models. The
   host session that does this has not been written ("The kernel load").
   The console is the Quart's channel-0 output, which the models print.
7. Afterwards: `openFPGALoader -b ulx3s -r` to restore the board to its
   flash image for the Flute session.

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
