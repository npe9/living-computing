# The framebuffer: `Lcdisp` in block RAM, scanned out over GPDI (ulx3s_plan.md step 4)

The Hobbit board's LCD, io.h `Lcdisp` at IOACK 0x3000 (`ctl` +0, `data`
+4, write-only), as a standalone device behind the plan's register port,
with its panel shown on an HDMI monitor from the ULX3S GPDI connector.
Nothing here has run on the board: the board is in use by another session.
Everything below is from Verilator, yosys and nextpnr.

| file | what |
|---|---|
| `LcdLcdisp.bsv` | `mkLcdisp`: the register port, the protocol, the panel RAM (bsc `BRAMCore` dual-clock, Verilog `BRAM2`) and its pixel-clock read port |
| `hdmi_scan.v` | 1024x768@60 timing, the quarter turn, the grey, three `tmds_enc` |
| `hdmi_tmds.v` | `tmds_enc`, `dvi_ser`: copied verbatim, see `../IP_PROVENANCE.md` |
| `lcd_pattern.v` | the test bitstream's writer: a pattern written through the port as `screenupdate` writes |
| `hdmi_lcd_top.v`, `hdmi_lcd.lpf`, `hdmi_lcd_build.sh` | the standalone test bitstream: PLL, power-on reset, the above, LEDs |
| `lcd_capture.py` | records every LCD write of the 8½ session (replayed, no QEMU) |
| `lcd_writes_8half.bin.gz` | that recording (39 KB; 7.2 MB unpacked) |
| `lcd_inject.py` | the bug injections below, as exact patches |
| `hdmi_frame_8half.png`, `hdmi_frame_pattern.png` | scanned-out frames as a monitor shows them (from the TMDS words) |
| `lcd_sim_top.v`, `lcd_tb.cpp`, `lcd_test.py` | the Verilator bench and the test against `p9term.LcdPanel` |

## The device

The protocol is `p9term.LcdPanel.write` (`tools/p9term.py`), which is
s9term's `screenupdate` (0x80026368) read as a panel (`TERM_CHOICES['lcd']`,
`docs/p9boot.md` "The LCD"):

* `ctl` (+0): `quad = ((quad << 6) | (data & 0x3F)) & 0xFF`, `col = 0`.
* `data` (+4): if `col < 768`, cells `(col, 4*quad + r)`, r = 0..3, take
  bits 2r+1..2r of `data & 0xFF`; `col += 1`.  Past column 767 it is an
  overrun (counted, `overruns` output).

The byte enables, `data` bits 31..8 and every other offset are ignored, as
the model ignores them.  A read answers 0 (the kernel never reads; the model
stops on one).  Every request gets one response.  `col` saturates at 768
instead of counting on: every column past 767 is an overrun either way, and
a 10-bit counter would wrap at 1024 and rewrite column 0 (the test covers
it).

**Storage: one byte per (quad, col)**, the four cells one `data` write
carries, at `quad * 768 + col`: 196,608 bytes, one RAM write per `data`
write.  The scan-out wants the same shape: on the turned display a line
walks the panel's y, so one byte is four consecutive display pixels.

### Block RAM, not SDRAM

`mkLcdisp` alone, `yosys synth_ecp5` (0.51), from `hdmi_lcd_build.sh`:

| cell | count |
|---|---:|
| DP16KD | 96 (16384 x 1 each: 8 bits wide, 12 deep) |
| LUT4 | 163 |
| CCU2C | 30 |
| PFUMX | 13 |
| TRELLIS_FF | 96 |

96 of the 85F's 208 block RAMs is 46% (1,572,864 bits of 3,833,856; the
plan's "about 40%" counted 18-kbit blocks as fully usable, but 2-bit cells
use the 16-kbit data part only).  The core's last whole build
(`fpga/README.md`, 2026-11-19) used 18 DP16KD, so the core and the panel
together are 114 of 208, 55%; logic is negligible (163 LUT4 of 83,640).
The read mux of the 12 deep blocks is the pixel clock's critical path and
still closes at 79-86 MHz against 65 (below).

SDRAM would save the 96 blocks but costs what this device otherwise does
not need: a share of the core's only memory port through an arbiter in the
SoC top's SDRAM controller (another agent's), a line buffer and clock
crossing for the 65 MHz scan-out, and a refresh-and-arbitration latency the
scan-out must hide.  The bandwidth is small (1024 x 768 x 2 bits x 60 Hz =
94 Mbit/s, about 12 MB/s), so it remains the fallback if the full SoC runs
out of block RAM; until then the panel is a self-contained device, which is
what the plan's contract asks for.  The device's `scan` interface (address
in, byte out two pixel clocks later) is the seam such a change would use.

## The video mode: 1024x768@60, the panel turned a quarter turn

**Chosen: VESA DMT 1024x768 at 60 Hz**: 65.000 MHz pixel clock, 1344 x 806
total (h 1024 + 24 front porch + 136 sync + 160 back porch; v 768 + 3 + 6 +
29), both syncs active low, 60.004 Hz.  Each display pixel is one panel
cell, the whole panel is visible, and nothing is scaled.

**Rejected: 768x1024 letterboxed in 1280x1024@60.**  That mode's pixel
clock is 108 MHz, so TMDS is 1080 Mb/s a lane and the 10:1 serializer's
DDR shift clock 540 MHz: above the ECP5 PLL's output range (`ecppll -i 25
-o 540` prints `Warning: Output frequency 540MHz not in range (10MHz,
400MHz)`) and far above what `ODDRX1F` from fabric registers closes (this design's shift
clock reaches 293-370 MHz depending on the seed, below).  A gearbox
(`ODDRX2F` with `ECLKSYNCB`/`CLKDIVF`) would still need a 540 MHz edge
clock from the same PLL.  Reduced blanking (CVT-RB, 91 MHz, 910 Mb/s)
has the same problem.  1024x768@60 is 650 Mb/s a lane, 325 MHz.

**Clocks** (`hdmi_lcd_top.v`, as `ecppll -i 25 -o 325` computes them):
`EHXPLLL` CLKI_DIV 1, CLKFB_DIV 13 from CLKOP, CLKOP_DIV 2 -> **325 MHz
shift clock** (VCO 650 MHz, inside 400-800), CLKOS_DIV 10 -> **65 MHz pixel
clock**, both 0 degrees.  The device's own port runs on the board's 25 MHz
in the test top (the SoC top will give it the core's clock); the RAM is the
only thing that crosses.

**Rotation.** Display pixel (X, Y) shows panel cell (x, y) = (767 - Y, X):
the panel's top row is the display's left column and its left column the
display's bottom row.  A monitor pivoted a quarter turn clockwise (its left
edge up, the common pivot direction) then shows the panel upright.

**Shade.** s9term's `getcolor` (0x80026aa0) gives bitmap pixel 0 white and
the kernel sends `~pixel` to the panel, so panel level 3 is white and 0
black.  getcolor itself is binary (every non-zero pixel black); levels 1 and
2 are drawn as greys, `grey = 85 * level` on all three channels, exactly as
`LcdPanel.grey()` and p9boot's `--screen`/`--lcd` dumps draw them.  Cells
never written are level 0, black, as in the model.

## The test bitstream

`sh hobbit/fpga/dev/hdmi_lcd_build.sh [SEED]` (seed 2 by default; products
in `hobbit/fpga/build/lcd/`, gitignored): bsc 2026.01, yosys 0.51,
nextpnr-ecp5 0.6, ecppack 1.4; about 20 s.  `lcd_pattern` writes the
pattern once after the power-on reset (LED 0 lights when done; LED 1 is the
PLL lock, LED 2 blinks from the frame count); the scan-out runs from
configuration on.

nextpnr, seed 2 (`--85k --package CABGA381 --speed 6`, the LPF's
`FREQUENCY` lines constrain all three clocks; the final post-route figures):

| | |
|---|---|
| TRELLIS_COMB | 671 / 83,640 (0.8%) |
| TRELLIS_FF | 187 / 83,640 |
| DP16KD | 96 / 208 (46%) |
| EHXPLLL | 1 / 4 |
| SIOLOGIC (the four `ODDRX1F`) | 4 / 141 |
| board clock, 25 MHz | 86.28 MHz, PASS |
| **pixel clock, 65 MHz** | **82.80 MHz, PASS** (critical path: block RAM out, read mux, `DOB_R2`) |
| **shift clock, 325 MHz** | **369.96 MHz, PASS** (critical path: `dvi_ser`'s phase detector `t2 -> ph`) |
| pixel -> shift clock crossing | 2.04 ns max delay (a 3.08 ns shift-clock period); nextpnr reports this path but its PASS lines do not judge it.  The words are stable for 5 shift clocks around `dvi_ser`'s load, and the PLL puts every pixel edge on a shift edge (CPHASE 1 and 9 differ by 4 shift periods) |
| bitstream | `hdmi_lcd_top.bit`, 538,110 bytes |

The shift clock is the tight one and depends on placement.  Seeds 1-8, the
same netlist (`Max frequency`, last report):

| seed | pixel (65) | shift (325) |
|---:|---:|---:|
| 1 | 81.37 | 328.73 |
| 2 | 82.80 | 369.96 |
| 3 | 85.64 | **292.74 FAIL** |
| 4 | 79.15 | 351.25 |
| 5 | 80.47 | **315.96 FAIL** |
| 6 | 79.21 | 336.70 |
| 7 | 81.78 | 341.88 |
| 8 | 83.44 | 337.38 |

Six of eight seeds close, so the build script pins seed 2 and the number is
re-checked on every build (`grep 'Max frequency' build/lcd/nextpnr.log`).
In the SoC the scan-out's placement will move; if the shift clock stops
closing there, the options are a seed sweep, a location constraint on
`dvi_ser` near the GPDI pins (bank 0, the top edge), or `ODDRX2F` gearing
to halve the fabric clock.

**Hardware run (not done; for an approved window).**  Program to SRAM only
(`openFPGALoader -b ulx3s hobbit/fpga/build/lcd/hdmi_lcd_top.bit`), monitor
on GPDI.  Expect LEDs 0 and 1 on and 2 blinking, and the picture of
`build/lcd/test/frame_pattern.png`: on the unpivoted monitor, four grey
bars (white at the top to black at the bottom) on the left, diagonal
stripes in the middle, a checkerboard on the right, a black border.
Restore the board with `openFPGALoader -b ulx3s -r`.

## Verification

`python3 hobbit/fpga/dev/lcd_test.py` (about 15 s; `--quick` skips the
recorded session) builds `mkLcdisp` with bsc and the bench with
Verilator 5.052 (`-DBSV_NO_INITIAL_BLOCKS`, so the RAM starts at 0 like
ECP5 block RAM, not at BRAM2's simulation fill), and runs three sequences,
each compared with `p9term.LcdPanel` fed the same requests:

1. **synthetic** (21,237 requests): what the recording does not exercise.
   Rows never written (compared with the model's zeros), `ctl` words with
   junk above bit 5 and three `ctl` writes in a row, `data` junk above
   bit 7 under every byte-enable value, offsets 1, 2, 3, 5, 6, 7, 8, 0xC,
   0x800, 0xFFC (ignored), reads (answered 0, no effect), 1,100 `data`
   writes after one `ctl` (332 overruns), a `ctl` resetting the column, and
   20,000 random requests (seed 20261124).  The whole panel is read back
   through the RAM's pixel-clock port after requests 120, 1,237 and 11,237
   and at the end; the overrun count and one response per request are
   checked.
2. **pattern**: `lcd_pattern.v`, the bitstream's own writer, drives the
   port (197,120 requests); its panel and one scanned frame are compared
   with the same pattern written in Python.
3. **recorded**: every LCD write s9term made in the 8½ session of
   `docs/p9boot.md` "8½ as `tor`" (below), compared whole at a quarter,
   half, three quarters and the end; then one frame.

Every scanned frame is taken from the TMDS words, not from the RAM: the
bench decodes all three lanes (DVI 1.0 3.2.3), re-encodes them with its own
encoder written from the specification (not from `tmds_enc`) and expects
the RTL's exact word on every pixel clock, so the transition-minimizing
choice and the DC balance are checked; it checks red = green = blue, the
raster (1344 x 806 totals, HSYNC 136 clocks and VSYNC 6 lines both active
low, the 24-clock front porch, 35 lines from VSYNC to the first active
line, no DE in vertical blanking); then `lcd_test.py` turns the frame back
to portrait by the mapping above, written again independently of
`hdmi_scan.v`, and compares it with `LcdPanel.grey()`.

### The recording

`python3 hobbit/fpga/dev/lcd_capture.py` replays the session exactly as
`tests/test_p9term.py` `EightHalfReplayTest` does with `P9TERM_8HALF=ls`
(`tests/net/8half.pcap` and the live run's input log, no QEMU; boot, login
as `tor`, 8½, the button-3 menu, a New window swept from (60, 640) to
(700, 1000), `ls` typed in it) and logs every `Lcdisp` write.  The run of
2026-11-24 (18.5 min of host time):

| | |
|---|---|
| stop | `input script: stop (at-cycle 2988614887)`, step 2,985,469,493, as the live run |
| bitmap | sha256 of the pixels `a908ac29…`, the live run's `ls` checksum |
| writes | 5,426 `ctl`, 1,429,096 `data`, 0 overruns: 1,434,522 requests |
| panel | every one of the 786,432 cells written, all equal to 3 − the bitmap (p9boot's `panel_check`) |
| recording | sha256 `9244e19c…6bf6418` (unpacked), replayed into a fresh `LcdPanel` = the live panel |

The four comparison points are distinct screens (the quarter point
differs from the end in 85,511 of the 196,608 RAM bytes, the half and
three-quarter points in 2,797 and 2,603).

### Results (2026-11-24)

`python3 hobbit/fpga/dev/lcd_test.py`: **23 checks, PASS**, 13 s.

* synthetic: 21,237 requests, 21,237 responses, overruns 332 = the
  model's; the panel equal to the model's after 120, 1,237, 11,237 and all
  requests (0 of 786,432 cells differ).
* pattern: 197,120 requests from `lcd_pattern.v` = the Python pattern's;
  panel and frame equal.
* recorded: 1,434,522 requests and responses, 0 overruns; the panel equal
  at all four points; the frame (2 VSYNC, 1,612 HSYNC, 1,536 DE runs
  checked, every TMDS word equal to the reference encoder's) turned back to
  portrait equals `LcdPanel.grey()` and **equals `tests/net/8half_ls.png`
  byte for byte** (0 of 786,432 differ): the live run's screenshot of
  s9term's bitmap, through the kernel's LCD writes, the RTL, the RAM, the
  scan-out and TMDS.

`hdmi_frame_8half.png` is that frame as the 1024x768 monitor shows it (the
8½start window on the left, the New window with `term% ls`, `bin`, `lib`,
`tmp` on the right, read with the monitor pivoted clockwise);
`hdmi_frame_pattern.png` the test bitstream's picture.  The same files,
and the portrait versions, are rewritten in `hobbit/fpga/build/lcd/test/`
on every run.

Not covered: the serializer (`dvi_ser`, shift registers into the
vendor's `ODDRX1F`) is not simulated; it is copied unchanged from the
owner's 640x480 design at 125 MHz, and here only its timing at 325 MHz is
checked (nextpnr, above).  And the bench runs the two clocks one after the other,
not interleaved, so the RAM's clock crossing is exercised only as a
dual-clock RAM, never with writes landing mid-frame.  A write during a
frame shows up in that frame or the next, which the panel tolerates.

### Bug injections (OBSERVED, 2026-11-24)

`python3 hobbit/fpga/dev/lcd_inject.py --full`: each bug put into the RTL
alone, the whole `lcd_test.py` run, and the exact patch reversed (the
driver checks each file's sha256 is back; `git diff` was clean
afterwards).  Every injection failed, and only the checks below; the
exact lines are in `lcd_test.py`'s header.

| injected bug | synthetic | pattern | recorded |
|---|---|---|---|
| `quad` shifted 4 bits, not 6 | panel x4 | panel, frame | panel x4, frame, png |
| `ctl` does not reset `col` | overruns, panel x4 | panel, frame | overruns, panel x4, frame, png |
| `col` wraps at 1024 (not saturated) | overruns, panel x3 | - | - |
| `data` honours byte enable 0 | panel x4 | - | - |
| `data` decoded from `addr[2]` alone | panel x4 | - | - |
| the byte's four rows reversed in scan-out | | frame | frame, png |
| grey inverted | | frame | frame, png |
| rotation the other way | | frame | frame, png |
| cell index one pixel clock early | | frame | frame, png |
| HSYNC active high | | raster | raster |
| `tmds_enc` never takes the DC-balance branch | | TMDS words | TMDS words |
| `tmds_enc`'s xnor tie-break inverted | | TMDS words | **-** |

Two things this shows.  The synthetic sequence is what catches the
column wrap, the byte enables and the offsets: the 8½ recording never
writes past column 767, uses only +0 and +4, and every one of its writes
carries the same byte enables, 0x3 (p9boot's mask for the kernel's
stores), so a device that looked at enable 0 behaves the same on it.  (It
does exercise junk above the low byte: 877,966 of its writes have bits
31..8 non-zero, the kernel's `~m`.)  And the encoder bugs leave the decoded picture intact; only the
word-exact comparison with the specification's encoder sees them, and the
xnor tie-break only under the pattern's greys (the 8½ screen is levels 0
and 3 only, bytes 0x00 and 0xFF, never four ones).
