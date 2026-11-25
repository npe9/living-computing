# SONIC subset and ESP32 link (plan step 6): `Sonic.bsv`, `EspLink.bsv`

The FPGA side of the ULX3S Ethernet (`docs/ulx3s_ethernet.md` §6), in
BSV, to `docs/ulx3s_plan.md`'s device bus contract:

* **`mkSonic`** (`Sonic.bsv`) is the DP83932 subset that 1st Edition
  devether.c uses: `tools/p9boot.py`'s `Sonic` and `SONIC_CHOICES`.
  It has the register port (12-bit offset, wdata, byte enables, write →
  one response per request, irq a level). It masters memory for
  descriptors and buffers through a DMA port (`SonicDma`: one-word
  requests, posted writes, read data in order). It exchanges frames with
  the link through a frame port (`FrameByte` rx/tx).
* **`mkEspLink`** (`EspLink.bsv`) is the UART link to the ULX3S's ESP32:
  8N1 at `clksPerBit` clocks a bit (`mkEspLink25M`: 25 MHz / 2.5 Mbaud =
  10), with RTS flow control. It speaks the relay's packet format
  (COBS, a type byte, CRC-32, a 0x00 delimiter;
  `fpga/esp32_ethrelay/main/relay.h`). Its frame port is the SONIC's.

The SoC top (another agent's) connects the register port at 0xA4400000,
irq to IRQ 9, the DMA port to its SDRAM arbiter, and `txd`/`rxd`/`rts` to
pins L1/N3/H1 (`docs/ulx3s_ethernet.md` §2).

## Design: the model's DMA order, one word at a time

The engine is one `StmtFSM` that handles one register access or one
received frame at a time. It runs Rrra, Lcam, Txp and the receive path
as sequences that make **exactly the DMA accesses p9boot.Sonic makes, in
its order**: one 32-bit word per request, and one read outstanding. That
order is what lets a trace of the model be replayed into the RTL word for
word. It is slow (a read waits for its data before the next request), but
a 10 Mb/s-class link needs about 320 k words/s (§6.3), and the arbiter
has far more than that.

Two choices differ from the first version of the specification in
`docs/ulx3s_ethernet.md` §6, which has been corrected to match:

* **Frames are buffered whole**, in a 2 KB receive buffer and a 2 KB
  transmit buffer (`RegFile` 2048 x 8 each). A received frame is
  accepted (filter, CRC for the FCS) only when its `last` byte arrives,
  and is then written to memory. A frame whose `last` carries `bad` never
  touches memory. A transmitted frame is gathered from its fragments
  first, then sent. This keeps the DMA order the model's: the model
  writes the buffer and then the descriptor.
* **No address check**: the model has none (its PADDR is the identity),
  so the RTL has none either. The arbiter owns the address map.

**isr after the data.** The isr bits an operation raises (Lcd, Txdn,
Pktrx, Rde) are collected and applied only after the operation's last
DMA write has been accepted by the arbiter. irq therefore never rises
ahead of the buffer and descriptor words it announces. No register
access is served before then either. The first version set Pktrx on the
kept-descriptor path before the frame's writes were issued; the replay
compares irq only between events, so it passed. `SonicReplayTb` now also
checks, every clock, that irq does not rise before all of the event's DMA
words have been taken (S12 below).

Where the model raises `Stop`, the RTL sets a sticky `fault`, puts a code
in `faultInfo` (the list is in `Sonic.bsv`'s header), and abandons the
command or frame. The register write is still answered.

The link (`EspLink.bsv`):

* **TX** gathers the frame (2 KB), then sends `COBS(0x45 | frame |
  crc32) 0x00`. Before each code byte the COBS encoder scans ahead to the
  next zero (at most 254 bytes), as `relay_encode` does, including the
  final 0x01 code after a full 254-byte block. A frame over 1518 bytes is
  dropped and counted (`txTooLong`), since `relay_encode` refuses it. No
  start bit begins once RTS has been high for 3 clocks: 2 for the
  synchroniser and 1 for the start register.
* **RX** samples mid-bit (2-flop synchroniser), counts framing errors
  but passes the byte on, and decodes as `relay_feed` does. A streaming
  COBS decoder feeds the type byte and a 4-byte delay line, which keeps
  the CRC out of the frame. At the 0x00 it applies `relay_feed`'s checks
  in `relay_feed`'s order: wire overflow (1530 bytes), COBS, length ≥ 5,
  CRC, type, and frame length 14..1518. A 0x45 packet's frame bytes go to
  the SONIC as they are decoded, through a 2 KB BRAM FIFO, and its last
  byte carries `bad` when a check failed. Other types are swallowed.
  The counters are `relay_dec`'s (good, bad_crc, bad_cobs, bad_len,
  overflows, bad_type), plus framing, lost and txTooLong.

## Tests

```
sh hobbit/fpga/dev/sonic_run_tests.sh      # the SONIC against p9boot.Sonic
sh hobbit/fpga/dev/esplink_run_tests.sh    # the link against relay.c
sh hobbit/fpga/dev/sonic_synth.sh          # yosys synth_ecp5 cell counts
```

### The SONIC: traces of p9boot.Sonic replayed into the RTL

`sonic_trace.py capture` runs the reference model through
`tests/test_p9boot.py`'s replayed join, which takes about 4 minutes: BOOTP,
ARP, then IL to the recorded 1e file server, init, rc and `echo hello`.
It records every register access, every DMA word the model's SONIC makes,
every frame offered to it and every frame it sends. Each register access
also records the irq level after it. The result is
`sonic_tests/join_echo.trace.gz`.

`sonic_directed.py` drives a fresh model through the paths the join never
takes. The result is `sonic_tests/directed.trace.gz`. The join has none
of these:

* several frames packed into one buffer;
* the Rrra wrap;
* the filter's refusals;
* EOL, Rde and mpt, and the kept-descriptor path;
* chained transmit descriptors with odd and empty fragments;
* a second Txp from ctda;
* isr write-one-to-clear against imr;
* Rst;
* two frames whose last byte carries `bad`, a link CRC error. These are
  "B" events: the model is not called, and the RTL must make no DMA and
  leave irq alone. One is 2045 bytes, longer than the RTL's buffer, so it
  must be dropped without a fault.

The same docstring lists every case.

`sonic_run_tests.sh` re-checks each trace against a fresh model first
(`sonic_trace.py check`), so the trace is what the model does. It then
replays the trace into `mkSonic` (`SonicReplayTb.bsv`) through a DMA
arbiter that stalls requests and delays read data by an LFSR pattern. It
compares:

* every register read value;
* the irq level after every event;
* every DMA request as it is made (read or write, address, write data,
  byte enables), with reads answered with the model's data;
* the number of DMA words per event;
* every transmitted frame, byte for byte;
* the frame count per event;
* that no fault is raised;
* every clock, that irq does not rise before the event's DMA words are
  all made.

| trace | events | register reads / writes | frames offered | DMA words | frames sent | mismatches |
|---|---|---|---|---|---|---|
| `join_echo.trace.gz` | 2336 | 1134 / 863 | 339 | 51329 | 276 | 0 |
| `directed.trace.gz` | 90 | 35 / 42 | 11 (+2 bad) | 253 | 3 | 0 |

### The link: against the ESP32's own C

`esplink_run_tests.sh` builds `esplink_ref.c` with
`fpga/esp32_ethrelay/main/relay.c`, the file the firmware compiles.
`esplink_vectors.py` then takes every expected value from it:

* **TX:** the RTL is given the 276 frames the SONIC sent in the join,
  plus edge cases. These are lengths 248..262 of nonzero bytes, so the
  254-byte COBS blocks end at every position against the type byte and
  the CRC. There are also 0xFF runs, zeros, 1 and 14 bytes, two
  1518-byte frames, and a 1519-byte frame that must be dropped. Its
  `txd` is decoded and compared byte for byte with `relay_encode`, while
  RTS is driven high in random spans.
* **RX:** the 339 frames the SONIC received in the join are
  `relay_encode`d and driven onto `rxd` with random gaps. Bad input is
  interleaved:
  * `tests/test_ethrelay.py`'s `test_bad_packets_dropped` stream;
  * status packets;
  * a body one byte too long;
  * 1530 wire bytes that decode past the body limit;
  * exactly `RELAY_MAX_WIRE + 1` wire bytes;
  * 4- and 5-byte bodies;
  * a 1518-byte frame;
  * idle zeros;
  * one byte with a bad stop bit.

  Each frame out of the rx port whose `last` is not `bad` must equal the
  next good frame `relay_feed` returned. At the end the counters must
  equal `relay_dec`'s.

Result: 299 frames sent (30157 link bytes, one dropped as too long). On
the receive side, 171361 link bytes gave 340 frames, matching relay.c's
counts: good 342 (340 frames and 2 status), bad_crc 2, bad_cobs 3,
bad_len 3, overflows 2, bad_type 1, plus framing 1. There were 0
mismatches, over 18.6 M clocks.

### Discrimination

Each injection below was applied to the RTL by exact string replacement,
the runner was run, and the replacement was reversed. `git diff` of the
file was clean afterwards. The failures listed are the **observed** ones.

**The SONIC** (`sonic_run_tests.sh`, both traces, on the committed
traces and RTL):

| | injection in `Sonic.bsv` | `join_echo` | `directed` (first mismatch) |
|---|---|---|---|
| S1 | FCS not inverted (`fcs <= rxCrc`) | FAIL, 534 | FAIL, 9: the FCS words of each received frame (DMA write data) |
| S2 | isr write-one-to-SET | FAIL, 2264 | FAIL, 27: the isr read after `W isr ffff`, then irq |
| S3 | broadcast accepted without rcr Brd | pass | FAIL, 1238: frame 3 written to memory, beyond the model's DMA words |
| S4 | mpt not incremented | pass | FAIL, 2: the two mpt reads |
| S5 | fragment descriptors 16 bytes apart, not 12 | pass | FAIL, 9: the second fragment's descriptor reads |
| S6 | Lpkt at `rbwc <= eobc`, not `<` | pass | FAIL, 1143: frame 9's status word (0x41, not 0x01), then an extra Rrra |
| S7 | rrp wraps at rea + 16, not rea | FAIL, 1232 | FAIL, 1: the rrp read after frame 10 (0120, not 0100) |
| S8 | irq = isr != 0 (imr ignored) | FAIL, 4 | FAIL, 10: irq high while imr masks isr |
| S9 | rcr Pro ignored | pass | FAIL, 595: frame 10 not received (irq, DMA count, isr) |
| S10 | a `bad` frame accepted | pass | FAIL, 1235: the bad frame written to memory |
| S11 | a `bad` frame over 2 KB faults (the first version's behaviour) | pass | FAIL, 46: fault 6 from that event on |
| S12 | Pktrx raised on the kept-descriptor path before the frame's writes (the first version's behaviour) | pass | FAIL, 2: "irq rose after 118 of the event's 138 DMA words" |

The join alone misses S3-S6 and S9-S12. devether.c never:

* sends a broadcast with Brd clear;
* runs out of descriptors;
* uses more than one fragment;
* sets Pro.

It also sets eobc so that every frame takes Lpkt, and no link error
occurs in the join.

The directed trace is there for those paths. Its first version passed
four injections:

* S6, because no frame left exactly eobc words;
* S9, because frame 10 was dropped for want of a descriptor, so Pro was
  never exercised;
* S11 and S12, because neither case was in it.

Frame 9's length, frame 10's descriptor and the two bad frames were
then added. S11 found a real bug: a link-bad frame over 2 KB raised
fault 6. A review of the code found S12's bug, the isr ordering
described above. Both are fixed, and the counts above are from the
committed traces and RTL.

**The link** (`esplink_run_tests.sh`):

| | injection in `EspLink.bsv` | observed |
|---|---|---|
| E1 | RTS ignored (`uartTxStart` without `rts2 == 0`) | FAIL, 6527: "a start bit at cycle 3350, RTS high 3 clocks before", and so on |
| E2 | COBS blocks of 255 | FAIL, 4777: tx byte 22310 (RTL 00, C ff) onward; no SUMMARY (timeout) |
| E3 | decoder inserts a zero after a 0xFF block too | FAIL, 290: rx frame 31 onward differ from the C's; 21 more dropped as bad |
| E4 | the type byte left out of the CRC | FAIL, 2: stats (good 0, bad_crc 347), "only 0 good frames" |
| E5 | frame length minimum 13, not 14 | FAIL, 3: rx frames 43 and 44 (the runt is passed on); stats good +1, bad_len -1 |
| E6 | wire overflow one byte later (1531) | FAIL, 1: stats overflows 1, bad_cobs 4 (the `RELAY_MAX_WIRE + 1` packet) |
| E7 | framing errors not counted | FAIL, 1: stats framing 0 |
| E8 | tx frames of 1519 bytes accepted | FAIL, 1532: tx bytes 30157 onward "beyond the C's bytes" (the 1519-byte frame was sent) |
| E9 | no final 0x01 code after a full 254-byte block | FAIL, 4997: tx byte 22308 (RTL 00, C 01) onward; no SUMMARY (timeout) |

## Size (yosys `synth_ecp5`, no place and route)

`sonic_synth.sh`, yosys `synth_ecp5`, 2026-11-24, each module alone:

| module | LUT4 | TRELLIS_DPR16X4 | PFUMX / L6MUX21 | CCU2C | TRELLIS_FF | DP16KD |
|---|---|---|---|---|---|---|
| `mkSonic` | 5898 | 264 | 876 / 206 | 567 | 2770 | 1 |
| `mkEspLink25M` | 2062 | 260 | 344 / 76 | 221 | 582 | 3 |

Together that is about 8000 LUT4, plus 524 distributed-RAM cells, about
10% of the 85F's 83640 LUTs. Two 2 KB frame buffers (`RegFile` 2048 x 8,
read asynchronously) are mapped to distributed RAM:

* one of `mkSonic`'s two (the other became the DP16KD);
* `mkEspLink`'s transmit buffer.

Moving them to block RAM (BRAM2, a registered read) would free the 524
distributed-RAM cells (an estimate, not measured). It needs the read loops restructured, and the replay
tests will check that. The register file (64 x 16) and the 16-entry CAM
account for most of `mkSonic`'s flip-flops. The 3 DP16KD of the link are
the 2 KB receive FIFO.

## Not done

* Nothing has run on the board: it is in use by another session. No
  bitstream and no pin wrapper exist yet; the SoC top will instantiate
  these modules.
* The SONIC traces cover what devether.c and the directed script do.
  Registers the model only stores (tcr, dcr2, ...) are checked as
  storage.
* The link's 16-bit counters are not yet on any register: they are for
  a debug readout once the SoC top has one.
* Fault codes 1-5 are never raised by either trace. The model raises
  `Stop` there, so no trace of it can contain them. They are fail-loud
  guards checked by reading only. Only fault 6's "not for a bad frame"
  side is tested (S11).
* There is no joint simulation of EspLink feeding mkSonic. Each is
  tested against its own reference, through the same `FrameByte` port.
* The ESP32 side (`main.c`) has never been compiled for the target. The
  RTS polarity (high = stop) and the 3-clock latency are what
  `docs/ulx3s_ethernet.md` §2 specifies, and are unconfirmed against the
  real firmware.
* These runners are not in `tests/run_tests.sh`, as the quart and rtc
  device runners are not. They need bsc, about 5 minutes for the SONIC
  (most of it the Python check of the join) and 15 s for the link.
