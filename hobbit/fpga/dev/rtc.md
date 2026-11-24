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
// the MCP7940N link ("The MCP7940N" below)
method Bit#(1) i2cSclLow;                 // 1 = pull SCL low, 0 = release
method Bit#(1) i2cSdaLow;
method Action  i2cPins(Bit#(1) scl, Bit#(1) sda);   // the lines as read
method Bit#(4) mcpSeed;                   // where the time came from
method Bit#(8) mcpWrites;                 // write-backs completed
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
  been queued. Requests are served from reset, including while the
  MCP7940N seed runs ("Requests during the seed" below).

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

`mkRtc#(parameter Bit#(32) ticksPerSec, parameter Bit#(56) startBcd,
parameter Bit#(2) mcpMode, parameter Bit#(16) i2cQuarter)` takes four
Verilog parameters:

* `ticksPerSec` is the CLK frequency (at least 2).
* `startBcd` is `{year, mon, mday, wday, hour, min, sec}`. The model's
  start, 1993-01-03 12:00:00 UTC (a Sunday, `RTC_BASE`), is
  `56'h93010301120000`. `rtc_iic_check.py` derives that value from
  `Timekeeper._regs(RTC_BASE)` on each run, so the two cannot drift.
* `mcpMode` switches the board's battery-backed clock in: bit 0 seeds the
  counters from it at reset, bit 1 writes every `setrtc` back to it. 0 is
  the device as before: requests are taken from cycle 0 and the I2C lines
  are never pulled (the check verifies both). 3 is the board setting; 1
  reads the chip but never writes it, for a first hardware window.
* `i2cQuarter` is CLK cycles per quarter of an SCL bit: 63 at 25 MHz gives
  at most 99.2 kHz, with SCL low for 5.04 us and high for at least 5.04 us
  (two quarters each). The check measures both at the chip model: at
  `i2cQuarter` 2 the shortest low was 4 cycles and the shortest high 6
  (the release waits on the two-flop synchroniser), and it fails below two
  quarters.
  The I2C standard-mode minima are 4.7 us and 4.0 us; those two figures
  are from memory of the I2C specification, not from a document here.

`startBcd` is still the fallback. The counters run from it whenever
`mcpMode` bit 0 is clear, or the seed fails (`mcpSeed` says why).

## The MCP7940N

The ULX3S carries a Microchip MCP7940N real-time clock with a battery
holder (the owner's board has the battery fitted), at I2C address 0x6F on
the `gpdi_sda`/`gpdi_scl` lines, which it shares with the HDMI connector's
DDC (EEPROM at 0x50). Pins, from the ULX3S LPF in the Flute tree
(`~/src/ulx3s-experiments/flute-lx50/constraints/ulx3s_85f.lpf`, lines
149-162): **`gpdi_sda` B19, `gpdi_scl` E12**, both `IO_TYPE=LVCMOS33
PULLMODE=UP DRIVE=4`. They are not in this tree's `fpga/ulx3s_85f.lpf`
yet; the SoC top adds them. Each pin is open drain: output 0 with the
tristate enable `i2cSclLow`/`i2cSdaLow`, and the pad's input to
`i2cPins` (in Verilog, `assign gpdi_scl = sclLow ? 1'b0 : 1'bz;`). If the HDMI
work reads the monitor's EDID over the DDC, the SoC top has to arbitrate
between the two; otherwise the RTC can own the two pins. The RTC uses the
bus only at reset and after a `setrtc`. This
master assumes it is alone on the bus: it has no arbitration-loss
detection.

**Sources.** The MCP7940N data sheet (DS20005010) is not on disk, so no
page is cited. Fetching it was requested on 2026-11-24 and is waiting for
the owner's approval of the download (agents may not download on their
own); until then the facts below rest on code written against it.
`rtc_mcp7940n.h` tags each fact with its source:

* **[T]** `~/src/ulx3s-experiments/flute-lx50/test/rtc_test.c`, written
  for this chip on this board design (its notes say it has not yet run on
  the board), citing DS20005010J: the address 0x6F, ST (RTCSEC bit 7),
  VBATEN (RTCWKDAY bit 3, off at the chip's power-on), PWRFAIL (bit 4,
  cleared by writing RTCWKDAY), and the pointer-then-repeated-START read.
* **[L]** Linux 6.17-rc7 `drivers/rtc/rtc-ds1307.c` (its `mcp794xx`
  paths; `~/src/linux-cursor/linux`, read only, GPL-2.0, nothing copied):
  * OSCRUN is RTCWKDAY bit 5 (`MCP794XX_BIT_OSCRUN BIT(5)`); the driver
    refuses the time when it is clear, and when ST is clear;
  * the 12/24 bit is RTCHOUR bit 6 and PM bit 5 (`DS1307_BIT_12HR 0x40`,
    `DS1307_BIT_PM 0x20`, applied to the mcp794xx by the probe's default
    case), with 12 read as 0 before PM adds 12: the conversion here;
  * the SRAM is 64 bytes at 0x20 (`nvram_offset 0x20`, `nvram_size
    0x40`, "battery backed SRAM");
  * the seven time registers are read and written as one bulk transfer
    from register 0, which implies the pointer auto-increments.
* **[R]** RTEMS `bsps/shared/dev/rtc/mcp7940m.c` (`~/src/rtems`, read
  only, BSD-2-Clause), for the MCP7940M, the same register map without the
  battery: LPYR is RTCMTH bit 5 (`MCP7940M_RTCMTH_LPYR (0x01u << 5)`).

Still **inference**, confirmed by neither: the order used to set the time
(clear ST, wait for OSCRUN to clear, write, set ST). Linux does not do it:
it writes all seven registers, ST and VBATEN set, in one burst. The order
here is the conservative one and costs only bus time; check it against
the data sheet before the first hardware window, along with everything
above (secondary sources agree with each other, not necessarily with the
part).

**Seed (mcpMode bit 0), at reset.**

1. Read RTCSEC..RTCYEAR (pointer 0, repeated START, seven bytes).
2. Fall back if there is no ACK at 0x6F (`mcpSeed` 3), if ST or OSCRUN is
   clear (4), or if the registers are not a calendar time (5). A 12-hour
   chip is converted to 24-hour.
3. Poll RTCSEC until it changes (up to 1.5 s; 6 if it never does).
4. Read all seven again and load them. The divider restarts on that cycle,
   as on a `setrtc` load, so the counters start in phase with the chip's
   second, behind it by one burst read at most. In the tests the lag was
   at most 1,625 cycles at 8 cycles a bit. At 99 kHz the same reads take
   about 1.7 ms.
5. Recompute the weekday from the date, as on every load.

An SCL held low past 2^20 cycles of stretching gives 7. Any fallback leaves
the counters running from `startBcd` since reset. `mcpSeed` = 2 means the
time came from the chip. The seed only reads; it does not turn VBATEN on
(Linux's driver does, at probe; here the first write-back does).

**Requests during the seed.** The device does not wait for the seed: from
reset it serves every request, the clock running from `startBcd`. The
seed's load replaces the time on its cycle (a read on that cycle still
sees the old time, as with a `setrtc` load), so a program that reads the
clock in the first second or so sees `startBcd`'s time and then a jump to
the chip's. A `setrtc` that comes before the seed lands wins: the seed is
dropped (`mcpSeed` 8), and the kernel's time is written back to the chip
when the seed's reads end, so the chip then runs behind by up to that wait
(about 1.5 s at most). The NVRAM is served throughout. The earlier design
stalled every request until the seed was done; that was dropped because
the kernel or the ROM may touch the RTC or NVRAM early.

**Write-back (mcpMode bit 1), after every load.** A `setrtc` load (W
cleared with a valid time) queues the loaded time. The link then:

1. writes RTCSEC = 0 (ST off);
2. polls RTCWKDAY until OSCRUN clears (up to 1.5 s);
3. writes RTCMIN..RTCYEAR in one burst: 24-hour, weekday with VBATEN set,
   so the battery keeps the time;
4. writes RTCSEC with ST set, last, so the chip's second starts as close to
   the load as the bus allows. In the tests this happened within 3,000 bus
   cycles of the load, plus the chip's OSCRUN delay.

A second `setrtc` during a write-back is written after it, with the newer
time. Any failure (no ACK, OSCRUN never clears, stuck SCL) is fault 5; the
counters are unaffected.

## A persistent NVRAM (proposal, not built)

The NVRAM is 2040 bytes, and the board's backing for it is wanted only by
the ROM's world: romboot's `Env` (712 bytes at 0) and key.c's `Nvrsafe` (31
bytes at 1924). The MCP7940N's SRAM is 64 bytes ([L], above), so it
cannot hold the `Env`.

**The `Env`: a sector of the configuration SPI flash.** The SPI flash is
the one place on the board that keeps 2 KB without power. The plan:

* Keep the NVRAM in its block RAM as now.
* At reset, copy a flash area into the NVRAM before the first request is
  taken, like the seed.
* Write it back after the NVRAM goes quiet, for example 2 s after the last
  NVRAM write. A rewrite is an erase of one 4 KB sector and 8 page programs
  of 256 bytes.
* Use two sectors in turn, each with a sequence number and a checksum, so
  that a power cut during a write leaves the previous copy. At reset, take
  the valid copy with the higher number.
* Writes are rare (`envput` from the ROM's console), so wear (on the order
  of 100,000 erase cycles per sector for common parts, from memory) is not
  a concern.

That needs:

* an SPI flash master behind the RTC, its pins driven through `USRMCLK`
  (the Flute tree's plan, `notes/ulx3s-peripherals-plan.md`);
* the flash's size, read by JEDEC ID on the board;
* an area agreed with the other users of the flash: the bitstream at 0,
  and the Flute session's boot images. This board is shared, so the
  sectors have to be chosen with that session, not assumed. The top of
  the flash is the natural place.

**What the 64-byte SRAM covers.** The 31-byte `Nvrsafe` fits, with 33 bytes
to spare. Mapping NVRAM 1924..1954 onto MCP SRAM 0x20..0x3E (read at seed
time, written through on every write in that range) would keep the
machine key across power cycles on the battery alone, without the flash.
That is only worth doing if a boot program that calls `key()` runs on the
board. s9term's boot does not open `#r/nvram` (the traced run has no NVRAM
access). The flash scheme covers the `Nvrsafe` anyway, so the SRAM is the
cheaper first step, not the whole answer.

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
| 5 | an MCP7940N write-back failed (no ACK, OSCRUN never cleared, SCL stuck) | no model: the model has no chip |

`mcpSeed` is not a fault. A fallback to `startBcd` is the designed
behaviour when the chip is absent, and it reports which case it was:

| mcpSeed | meaning |
|---|---|
| 0 | seeding (requests are served, from `startBcd`) |
| 1 | mcpMode bit 0 clear: `startBcd` |
| 2 | the chip's time |
| 3 | no ACK at 0x6F |
| 4 | ST or OSCRUN clear: the chip's oscillator is not running |
| 5 | the chip's registers are not a calendar time |
| 6 | the chip's second never changed within 1.5 s |
| 7 | SCL held low (stretch timeout) |
| 8 | a `setrtc` came before the seed landed: the kernel's time kept |

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
* bsc's generated Verilog gives the four parameters a default of 0, so
  override `ticksPerSec`, `startBcd`, `mcpMode` and `i2cQuarter` at
  instantiation (or `chparam`).
* The I2C pins: see "The MCP7940N". The SoC top adds `gpdi_sda` (B19) and
  `gpdi_scl` (E12) to its LPF, and wires them open drain. With `mcpMode` 0
  they can be left unconnected (`i2cPins` tied to 1).
* `rtc_iic_check.py` is not wired into `tests/run_tests.sh`. It needs bsc
  and Verilator, and it runs in about 70 s.

## Area (yosys 0.51 `synth_ecp5`, `rtc_iic_synth.sh`, 25 MHz)

| LUT4 | PFUMX | L6MUX21 | CCU2C | TRELLIS_FF | DP16KD |
|---:|---:|---:|---:|---:|---:|
| 1585 | 201 | 29 | 205 | 602 | 1 |

That is with `mcpMode 3`, `i2cQuarter 63`. **Switching the link off does
not get the area back**: with `mcpMode 0` it was still 1594 LUT4 and 480
TRELLIS_FF (measured at 1674 for mode 3, before the changes below). Presumably yosys cannot prove the FSM's state registers
constant once the mode is fixed, but that is a hypothesis, not checked. Before the MCP7940N link (commit 821a5c62) it was 555
LUT4, 219 TRELLIS_FF. The link (the I2C master, the seed and write-back
FSM, the seven-byte buffer, the BCD/12-hour conversion and the second
validity check, and the poll counters) costs about 1,100 LUT4, about 1.3%
of the 85F. One cheap pass was made:

* Converting a 12-hour hour by table instead of through binary saved 52
  LUT4.
* Registering one shared `fromMcp` result cost 57 LUT4 and 46 FF more, and
  was dropped: bsc already shares it.
* Serving requests during the seed (the `seeded` guard gone, a second load
  wire) moved the count from 1674 to 1637, before the table.

The rest is the StmtFSM's state decoding, the 32-bit cycle and poll
counters, and the master's 20-bit stretch counter. Those are guesses; it
is not measured per part.

The NVRAM is one DP16KD. The counters, the held set, the weekday and the
validity check make up the rest. The tens digit is multiplied by 10 with
shifts, because `* 10` had cost three MULT18X18D. Placement and timing are
for the SoC top's build.

## Test

`python3 hobbit/fpga/dev/rtc_iic_check.py` (about 70 s) compiles both
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
* the faults above;
* 52 MCP7940N sequences. Two more builds are used, `mkRtc_m1` and
  `mkRtc_m3` (`mcpMode` 1 and 3, `ticksPerSec` 100000, `i2cQuarter` 2).
  Their I2C lines go to `rtc_mcp7940n.h`, a cycle-level behavioural chip
  written for this test (its own source tags say which facts are
  inference). The sequences cover:
  * seeds at four phases of the chip's second;
  * all 24 twelve-hour values (12 AM to 11 PM);
  * a seed across the year end;
  * a chip that stretches SCL;
  * the nine fallbacks;
  * five write-back cases;
  * mode 1, which must leave the chip alone;
  * requests during the seed: a `setrtc` that supersedes it, NVRAM and
    clock accesses while it runs, and five single reads on exact cycles
    around the seed's load (61168..61172; the load is at 61170, checked).

  Each sequence checks the seed status, every clock read against the model
  (running from `startBcd`, then from the chip's time after the seed's load
  cycle unless a `setrtc` came first; the seed lag is bounded at 2,000
  cycles), the SCL low and high times (at least two quarters), the write-back count and fault, the chip's registers at the
  end against the time last set, and that the chip saw no I2C protocol
  violation and no time write while its oscillator ran.

Last run, from an empty `build/`, 2026-11-24 (44 s): 136 of 136
sequences agree (RTC, IIC and MCP7940N together). 41 seeds came from the
chip, with a lag of at most 1,625 cycles; 11 fell back; 367 accesses were
taken while a seed ran; 793 clock reads were compared in the MCP
sequences; 4 write-back sequences were checked to the chip's registers. The RTC reads compared per register were control 1137, sec
473, min 436, hour 436, wday 433, mday 437, mon 437, year 436 and NVRAM
2040, with 3571 writes. 4 model refusals were matched by the RTL's fault
code, and 2 RTL-only faults came where expected.

Discrimination (`rtc_iic_inject.py`) injected 10 RTC bugs, 9 IIC bugs and
13 MCP7940N-link bugs (M1-M13: the seed alignment, the OSCRUN check,
12-hour PM, the calendar check, the write-back's OSCRUN wait, VBATEN, ST,
the oscillator stop, the master's read ACK, clock stretching, a seed that
overwrites an earlier `setrtc`, requests stalled during the seed, and one
row of the 12-hour table). Every one
made the check fail. The observed failure sets are in `rtc_iic_check.py`'s header.
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
