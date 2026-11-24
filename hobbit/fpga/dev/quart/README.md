# Quart and interrupt path: ULX3S plan step 2

Step 2 of `hobbit/docs/ulx3s_plan.md` needs four devices:

| device | window (from `io.h`) | module | file |
|---|---|---|---|
| Quart, Philips SC68C94 | IOBASE + 0x100..0x1FF | `mkHobbitQuart#(clksPerBit, ctNum, ctDen)` | `HobbitQuart.bsv` |
| incon latch | IOBASE + 0x00..0x13 | `mkHobbitIncon` | `../intc/HobbitIntc.bsv` |
| IOCTL | IONAK + 0x00..0x03 | `mkHobbitIoctl` | `../intc/HobbitIntc.bsv` |
| Irq | IONAK + 0x80..0x8F | `mkHobbitIrq` | `../intc/HobbitIntc.bsv` |

Each sits behind the plan's device bus contract:
`req(addr[11:0], wdata, be[3:0], write)` takes the offset inside the
device's window, and `resp` returns one word for every request, writes
included.  The SoC top owns the address decode.

## Wiring for the SoC top

- **Interrupts.** `Irq.sources(s)` must be driven every clock, with bit n
  carrying io.h IRQ n:
  - bit 1: `quart.irq`
  - bit 5: `incon.irq` (always False)
  - bits 8, 9, 10: SCSI DMA, SONIC and SCSI from the devices that own them
  - every other bit: 0

  `Irq.il6` is the core's interrupt level 6. s9term sends every board
  interrupt to `interrupt()` at IL 6 (`CHOICES['irq-level']`).
- **Channel 0** is the console. It drives the `txd` pin and must be fed
  `rxd` every clock. The frame is 8N1 at `clksPerBit` SoC clocks per bit.
  The kernel programs 19200 baud, so a 25 MHz SoC needs `clksPerBit` =
  1302.
- **Channels 1, 2 and 3** are byte streams: `txOut[ch-1]` (Get) and
  `rxIn[ch-1]` (Put). Channel 2 is the keyboard and channel 3 the mouse.
  - Tie an unused `txOut` to an always-ready sink. If nothing drains it,
    the FIFO fills and the kernel spins on TxRDY, as it would on a dead
    line.
  - `rxIn` blocks while that receiver is disabled or its FIFO is full.
- **The C/T clock** is the SoC clock times `ctNum/ctDen`. Choose it to give
  the part's X1/16 rate, 3.6864 MHz / 16 = 230400 Hz. At 25 MHz that is
  1152/125000. The counter sets CtrRDY every 2 * count C/T clocks.
- **Reads have side effects** and must reach the device exactly once each:
  - `mr` advances the MR pointer
  - `rxfifo` and `grxfifo` pop a byte
  - `start` starts the counter
  - `stop` clears CtrRDY

  A bus that retries or speculates reads breaks the console.
- **`fault`** is sticky. `faults` counts faulting events and `faultInfo`
  holds the last one's code. The Quart's code is `{FaultKind[3:0], 0000,
  00, reg[5:0]}`; the intc devices use `{dev, write, addr[10:0]}`. Wire
  `fault` to an LED or a status register. In Bluesim every fault is also
  `$display`ed with its address.

## What is implemented

The scope is what the kernel uses. These are the counts of every Quart
access s9term makes from reset to `echo hello` at rc's prompt, in the
captured trace (6443 accesses across all four devices):

- **Quart reads:**
  - `sr` 298
  - `stop` 62, `start` 4
  - `cir` 170, `gicr` 89, `gibcr` 27, `grxfifo` 13
- **Quart writes:**
  - `txfifo` 279
  - `update` 170, `gtxfifo` 11
  - `cr`, `mr`, `csr`, `acr`, `imr`, `ctu`, `ctl`, `opr`, `iopcra`,
    `iopcrb`, `ack`, `icr`
- **Irq:** `mask0`/`mask1` read-modify-write (`setvector`), and
  `status0`/`status1` read in every `interrupt()`.
- **IOCTL:** 4 writes and 2 reads.
- **incon:** 2 writes to `csr`, no reads.

The `HobbitQuart.bsv` header gives the register-level behaviour. It
follows p9boot's `QUART_CHOICES` and the resolved contradictions in
`docs/devices/README.md`:

- FIFOs are 8 deep, and FFULL means all eight are full.
- Bids are numeric and the largest wins: a receiver holding n bytes bids
  `(n<<5)|0x0C|ch`, an empty transmitter bids `0x78|ch` with GIBC 7, and
  the counter bids `0x15` or `0x17` (channel b or d).
- `irq` = any (isr & imr), which is ICR's threshold of 0.

Anything else fails loud:

- everything p9boot's models stop on: unmodelled registers, partial
  writes, any incon read, a counter started outside timer mode or with
  count 0
- everything they accept but the RTL does not implement:
  - `bcr` or `icr` set non-zero
  - `pwrdn`, or X1/CLK ÷ 2
  - BrkStart, or the 0x80..0xF0 commands
  - a `txfifo` write while the transmitter is disabled or full
  - channel 0 set to anything but 8N1
- receive errors on the pin: overrun, framing error, or a byte arriving
  while the receiver is disabled

### Known differences from the Python model (by design)

- **Transmitter.** The model sends a byte in zero time, so its `sr` and
  `isr` always show an empty FIFO. The RTL has the real 8-byte FIFO and
  shift register.
  - TxRDY drops at eight bytes held.
  - isr TxRDY and TxEMT stay low while anything is held. isr TxRDY waits
    for an empty FIFO because MR0's reset level is "8 empty".
  - The two agree whenever the FIFO has drained, which is the condition
    the replay test enforces before each access. `QuartUnitTb` checks the
    FIFO-full behaviour against the data sheet.
- **Receive pin.** It cannot hold bytes "on the line" as the model does.
  One byte waits in the shift register, and the next is an overrun fault.
  The stream channels block instead, which matches the model.
- **RxReset and TxReset** flush their FIFO (data sheet, 1994 p. 316). The
  model only disables, so the two differ only if a reset arrives with data
  held. The kernel resets only at `uartsetup`.
- **Irq status** is sampled one clock after `sources`.

## Verification

```sh
sh hobbit/fpga/dev/quart/run_tests.sh          # ~3 min
sh hobbit/fpga/dev/quart/synth.sh              # yosys synth_ecp5 alone
```

`run_tests.sh` runs two testbenches.

`QuartUnitTb` covers the RTL-only behaviour: 53 checks against the data
sheet and 8N1 timing.

`QuartReplayTb` replays each trace into the RTL. `quart_trace.py vectors`
replays the same trace into fresh p9boot models, which supply the
expected answers. Every read value, every fault, the Quart irq and IL6
after every access, and every transmitted byte are compared. The traces:

- **`tests/kernel_echo.trace.gz`**: captured by `quart_trace.py capture`
  from the run `docs/p9boot.md` documents, s9term from reset through
  `echo hello` with `join_echo.pcap`. The wrapped run reaches the same
  715,866,474 instructions as the unwrapped one, so recording does not
  perturb it. The trace holds 6443 accesses, 62 counter expiries, 13 bytes
  typed into channel 0 and the 290 bytes of the console's output. The
  fresh model reproduces all 12,886 captured values before the RTL sees
  them.
- **`tests/bids_fifo.trace`**: reaches what the kernel trace does not:
  FFULL at eight, every bid ordering, the counter's channel d, channels 1
  to 3, and `grxfifo`/`gtxfifo`. Its expected values were written from
  the data sheet, so the Python replay checks the model as well.
- **`tests/faults.trace`**: every fail-loud case. `ERR` means the model
  stops and the RTL must fault exactly once. `RTLERR` means the model
  accepts and the RTL must fault.

To capture a fresh kernel trace, pass p9boot.py's own arguments after
`--`:

```sh
python3 hobbit/fpga/dev/quart/quart_trace.py capture OUT.trace -- \
    hobbit/tools/plan9-1e/hobbit/s9term --max-steps 800000000 ...
```

Replay is event-driven. A `t` record moves the model's clock to the
counter's expiry, and the testbench waits for the RTL counter to expire
the same number of times. The RTL must not expire more often than that:
it is checked before every access. The period in clocks is checked
separately by the unit test.

### Discrimination (injected bugs, observed failures)

Each bug was injected into the committed RTL, the whole of
`run_tests.sh` was run, and the patch was reversed with `git apply -R`.
`git diff` was clean afterwards. Each row lists the tests that failed (all
others passed) and the mismatch counts observed on 2026-11-24.

| injected bug (file) | what it breaks | observed failures |
|---|---|---|
| FFULL at 3 held instead of 8 (`HobbitQuart.bsv` sr) | contradiction 1, FIFO depth | bids_fifo 1 (sr 0x0f vs 0x0d with seven held); kernel_echo 2 (sr while `echo hello` is typed) |
| the smallest bid wins (`winner`) | contradiction 2, priority | bids_fifo 10 (cir/gibcr/grxfifo); kernel_echo 8 (cir 0x78 vs 0x7a/0x79/0xac, gicr, gibcr) |
| transmitter bids 0x08\|ch with GIBC 1 (the old model) | contradiction 3 | bids_fifo 3; kernel_echo 44 (cir 0x08 vs 0x78, gibcr 1 vs 7) |
| the counter bids channel a/c (0x14) | contradiction 4 | bids_fifo 2 (cir 0x16, gicr 2); kernel_echo 124 (cir 0x14, gicr 0 at every clock tick) |
| counter reload one tick long (`ctr <= rl`) | period in clocks | unit 2 (22 clocks between expiries, want 20; 1281 for 9 fractional periods, want 1260). The replay passes: it is event-driven, which is why the unit test exists |
| channel 0 transmits MSB first | the 8N1 pin | faults 1, kernel_echo 287 (every console byte). The unit waveform check also fails, but as reported it shows only the summary of the first failing test |
| IL6 ignores the Irq masks (`HobbitIntc.bsv`) | the interrupt level | faults 1 (IL6 1 with SONIC/SCSI requesting and mask1 cleared) |
| IOCTL accepts any offset | fail-loud | faults 2 (read and write of +0x004 did not fault; the model stopped) |

The kernel trace alone catches five of the eight injections. The directed
traces catch the other three, and the unit test catches the timing bug
that no trace can.

## Synthesis (yosys 0.51 `synth_ecp5`, each module alone, no place and route)

`synth.sh`, 2026-11-24:

| module | LUT4 | PFUMX | L6MUX21 | CCU2C | FF | DPR16X4 | cells |
|---|---:|---:|---:|---:|---:|---:|---:|
| `mkHobbitQuartSynth` (25 MHz parameters) | 1265 | 159 | 69 | 138 | 617 | 16 | 2274 |
| `mkHobbitIrq` | 109 | 18 | 0 | 8 | 103 | 0 | 239 |
| `mkHobbitIoctl` | 308 | 132 | 67 | 8 | 127 | 0 | 643 |
| `mkHobbitIncon` | 47 | 2 | 0 | 22 | 111 | 0 | 183 |

The Quart's eight FIFOs sit in 16 distributed RAMs (`RegFile`). Most of
the IOCTL's LUTs are the two-deep 32-bit response FIFO and its mux. The
whole step-2 set comes to about 1,730 LUT4, about 2% of the 85F.
