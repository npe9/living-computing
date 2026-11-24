# MK48T02 timekeeper + NVRAM on the ULX3S (`mkRtc`, step 5)

`Rtc.bsv` is the Hobbit board's timekeeper at IONAK+0x2000..0x3FFF
(`docs/ulx3s_plan.md` step 5): 2040 bytes of NVRAM and the MK48T02's eight
clock registers. It behaves as `tools/p9boot.py` `Timekeeper`
(`CHOICES['rtc']`) does, which `docs/devices/README.md` "MK48T02 timekeeper"
checks against the SGS-Thomson data sheet (Feb 1992). The PDFs are not in
the repository (`docs/devices/MANIFEST.md`), so the data-sheet statements
here are the page-cited quotations in that README.

The IIC bus and its EEPROM are in `iic.md`. Both devices are tested by
`rtc_iic_check.py` (see "Test" below).

## Interface

The interface follows the device bus contract in `docs/ulx3s_plan.md`, with
one deviation:

```
method Action request(Bit#(13) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
method ActionValue#(Bit#(32)) response;   // one per request, writes too (0)
method Bool    irq;                       // always False: no interrupt pin
method Bit#(8) fault;                     // sticky, 0 = none
```

* **The address is 13 bits, not 12.** The window is 8 KB: 2048 byte-wide
  registers, one per 32-bit word (io.h `Nvram { uchar val; uchar pad[3]; }`
  and `RTCdev`'s `ulong`s). The SoC top passes `pa - (IONAK+0x2000)`, bits
  12:0.
* Bits 1:0 of the address are ignored, as the model's board ignores them
  (`Board.read`/`write` drop them). A read returns the byte in bits 7:0
  with 0 above it. A write takes `wdata[7:0]` and needs byte lane 0
  (`be[0]`). s9term's stores are full words (mask 0xF in the trace); the
  NVRAM's `uchar val` stores would be lane 0 under CONFIG.KL.
* Latency: a register read or any write responds on the next cycle. An NVRAM
  read responds one cycle later, because the block RAM's address is
  registered. A new request is taken only after the previous response has
  been queued.

| offset | register |
|---|---|
| 0x0000..0x1FDF | NVRAM byte `off>>2`, 0..2039 (io.h NVRAMLEN 2040) |
| 0x1FE0 | control: W 0x80 (devrtc.c RTCWRITE), R 0x40 (RTCREAD); S and calibration 4:0 are stored but have no effect |
| 0x1FE4..0x1FFC | sec, min, hour, wday, mday, mon, year, in BCD (data sheet register map 7F9..7FF) |

## Behaviour (`Timekeeper`, branch for branch)

* **Freeze.** A control write with R or W set, when neither was set,
  copies the seven clock registers to a held set. Reads return the held set
  until it is dropped. While W is set, clock-register writes go to the held
  set.
* **Load.** A control write that clears W, when W was set, loads the held
  set into the counters. The held set is then dropped, even if R stays set.
  Fields the driver did not write keep their snapshot values. The
  one-second divider restarts, so the next second comes exactly
  `ticksPerSec` cycles after the load. That is what the model's
  `offset = t - clock()` does. The quotations in `docs/devices/README.md`
  do not say how the part's divider behaves after a load.
* **Drop.** A control write with neither R nor W drops the held set.
* **Day of week.** `setrtc` never writes `wday`. The model recomputes it
  from the date at every load (it goes through `calendar.timegm`), and the
  RTL does the same: `weekDay` is Sakamoto's rule with the century folded
  in, 1 = Sunday, the model's `(tm_wday + 1) % 7 + 1`. On the real part
  the day is one more counter register (the README's register map lists
  "day 01-07" next to the others). By inference, not from a quotation, it
  is not recomputed from the date, so a real board would show the old
  weekday after a set. Nothing in the kernel reads `wday` (`rtctime` skips it). The
  RTL follows the model here, the behaviour reference, so that every read
  compares. The 300-date sequence pins this choice.
* **Counting.** BCD counters run from the start time and tick once every
  `ticksPerSec` cycles. Months have 28/29/30/31 days. Every year divisible
  by 4 is a leap year, because 00..99 stand for 1970..2069 as in devrtc.c
  `rtctime`. Year 99 is followed by 00, which reads back as 2000. The
  counters keep running while the registers are frozen. The ST, KS and FT
  bits are not modelled: they read 0, and the kernel never sets them.

### Start time and clock

`mkRtc#(parameter Bit#(32) ticksPerSec, parameter Bit#(56) startBcd)`
takes two Verilog parameters. `ticksPerSec` is the CLK frequency (at
least 2). `startBcd` is `{year, mon, mday, wday, hour, min, sec}`. The
model's start, 1993-01-03 12:00:00 UTC (a Sunday, `RTC_BASE`), is
`56'h93010301120000`. `rtc_iic_check.py` derives that value from
`Timekeeper._regs(RTC_BASE)` on each run, so the two cannot drift.

**No battery on this path.** The ULX3S does carry an MCP7940N on its I2C bus
(the Flute tree's `test/rtc_test.c`). This module does not use it. Time
restarts from `startBcd` at every configuration, and the NVRAM restarts from
`rtc_nvram.hex` (2040 zero bytes, as in the model). Seeding the time from the
MCP7940N would need the board's I2C bus, which is shared with the HDMI DDC,
so it is left to the SoC top.

## What the NVRAM holds

The kernel keeps nothing in the NVRAM. It only offers the NVRAM as `#r/nvram`
(devrtc.c `rtcread`/`rtcwrite`, byte by byte, limited to NVRAMLEN), and
opening it needs `cpuserver` (`rtcopen`). s9term never touches it: the
traced run has no NVRAM access. Two programs in the 1e source use it:

* `boot/romboot.c` (the `rom` kernel configuration, `cpuserver = 1`) keeps
  the ROM's environment at offset 0: `envinit` reads an `Env` (hobbit
  `rom.h`: `int nentry; uchar sum[4]; Entry entry[11]`, with `name[16]` and
  `value[48]`, 712 bytes). Its defaults are `sysname=hobbit`, `station=99`,
  `bootfile=/hobbit/9cpu`, `bootmode=d` and `fs=incon!nj/astro/Nfs`.
* `boot/key.c` keeps the machine key at offset 1024+900 = 1924: an
  `Nvrsafe` (auth.h: `machkey[7]`, `machsum`, `authkey[7]`, `authsum`,
  `config[14]`, `configsum`, 31 bytes).

A board image with a preset environment or key is a different
`rtc_nvram.hex`.

## Faults (fail loud)

`fault` latches the first code. The access still gets a response (data 0),
and simulation prints `RTC FAULT n: ...`.

| code | when | model |
|---|---|---|
| 1 | clock register written without the held set and W | `BusError` "written without RTCWRITE" |
| 2 | W cleared with a held set that is not a calendar time (non-BCD, month not 1..12, day past the month's end, hour > 23, min/sec > 59) | `ValueError` from `timegm` for a bad month. For a bad day `timegm` silently normalises, so the RTL faults where the model does not (tested as RTL-only) |
| 3 | write without byte lane 0 | accepted (the model ignores the mask), RTL-only |
| 4 | W cleared with nothing held (W set again after a load that left R set) | `TypeError` (the model crashes) |

## Integration notes for the SoC top

* `rtc_nvram.hex` and `iic_eeprom.hex` are named without a directory in
  the generated Verilog (`RegFileLoad #(.file(...))`). They resolve against
  the working directory of the simulator or of yosys. In simulation a
  missing file is only a warning, and the memory then reads as zeros. For
  the EEPROM that means ether address 0 and `clock` 0. Copy the files next
  to the build, or run from `fpga/dev/` as the scripts here do.
* yosys must read bsc's `RegFileLoad.v` with `read_verilog -defer`. Without
  it, yosys elaborates the module's default `file = ""` and stops with
  "Can not open file `` for $readmemh". `fpga/build.sh` reads its library
  cells without `-defer` today.
* bsc's generated Verilog gives the two parameters a default of 0, so
  override `ticksPerSec` and `startBcd` at instantiation (or `chparam`).
* `rtc_iic_check.py` is not wired into `tests/run_tests.sh`. It needs bsc
  and Verilator, and it runs in about 20 s.

## Area (yosys 0.51 `synth_ecp5`, `rtc_iic_synth.sh`, 25 MHz)

| LUT4 | PFUMX | L6MUX21 | CCU2C | TRELLIS_FF | DP16KD |
|---:|---:|---:|---:|---:|---:|
| 555 | 51 | 15 | 99 | 219 | 1 |

The NVRAM is one DP16KD. The counters, the held set, the weekday and the
validity check make up the rest. The tens digit is multiplied by 10 with
shifts, because `* 10` had cost three MULT18X18D. Placement and timing are
for the SoC top's build.

## Test

`python3 hobbit/fpga/dev/rtc_iic_check.py` (about 20 s) compiles both
packages with bsc 2026.01 and builds each with Verilator and
`rtc_iic_tb.cpp`. It then replays every access sequence into the RTL and
into a fresh model at the cycle the RTL took each access. The model's clock
is `Fraction(cycle, 1000)`, exact, with the RTL built at `ticksPerSec =
1000`. It compares every read and every fault. The RTC sequences are:

* `rtc_join.trace`: every timekeeper access s9term made in
  `tests/test_p9boot.py` JoinReplayTest. `rtc_iic_capture.py` captures it,
  about 3 minutes. The accesses are 10: one `setrtc` at model second 15.2,
  setting the server's time 1993-01-03 12:00:48. s9term never reads the
  clock or the NVRAM in that run, which is why the synthetic sequences
  exist. Cycles are scaled 20 MHz / 20000, so model seconds stay seconds.
* phase: one read per sequence at an exact cycle, at reset (cycles 0, T-2,
  T-1, T, T+1, 2T-1, 2T, 2T+1) and after a load at four skews
  (load+2, +T-1, +T, +T+1, +2T-1, +2T), and after a load on the cycle
  where the divider wraps (load % T == T-1), where the load must win over
  the tick;
* the freeze, held-set, R-with-W, W-cleared-with-R-set and control-bit
  corners; devrtc.c `setrtc` then `rtctime`;
* 19 rollovers: minute, hour, day, the ends of 31- and 30-day months, Feb 28
  and 29 of 1993, 1996 and 2000, 1999 to 2000, 2069 to 1970, and the epoch;
* 300 random dates from 1970 to 2069, each set and then read back
  (including wday);
* all 2040 NVRAM bytes, with romboot's `Env` at 0 and an `Nvrsafe` at 1924
  written first;
* the faults above.

Last run, from an empty `build/`: 84 of 84 sequences agree (RTC and IIC
together). The RTC reads compared per register were control 1137, sec
473, min 436, hour 436, wday 433, mday 437, mon 437, year 436 and NVRAM
2040, with 3571 writes. 4 model refusals were matched by the RTL's fault
code, and 2 RTL-only faults came where expected.

Discrimination (`rtc_iic_inject.py`) injected 10 RTC bugs. Every one made
the check fail. The observed failure sets are in `rtc_iic_check.py`'s header.
The first run of the divider injection (R1) passed: the phase probes had
been spaced by the access gap. They are now one per sequence, checked to
land on their exact cycle.

## Trace format

`rtc_join.trace` and `iic_join.trace` have one access per line:
`cycle op off data mask result function`. Here `cycle` is model cycles at
20 MHz; `op` is R or W; `off` is the offset in the device window; `mask`
is the byte mask (bit 3 = bits 31:24); `result` is the value the model
returned (`-` for a write); and `function` is the kernel function from
s9term's symbol table.
