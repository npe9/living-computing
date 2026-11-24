# Xerox Alto

The Xerox Alto was an experimental personal computer for interactive
bitmapped graphics and networked work. Its architecture combined a
microprogrammed processor with a display-oriented memory system, keyboard and
mouse input, and Ethernet connectivity.

See [`plan.md`](plan.md) and [`docs/README.md`](docs/README.md). The initial
source is Chapter 33, printed p. 549, of *Computer Structures: Principles and
Examples* (1982).

## Status

A Bluesim model of the **Alto II** that runs the historical control PROMs
and boots a PARC Diablo pack (`diags.dsk`) to the Alto Executive in 60 M
microcycles (about 45 s of Bluesim on an Apple-silicon Mac).

| piece | where | evidence |
|---|---|---|
| microengine: R/S/T/L/M/IR, 74181-style ALU, shifter (incl. Nova DNS/MAGIC), 16-task priority switch | `bsv/CPU.bsv`, `ALU.bsv`, `Shifter.bsv`, `AltoTypes.bsv` | boot smoke test |
| 256 KW memory, XM bank registers, I/O page | `bsv/AltoMem.bsv`, `Devices.bsv` | boot smoke test |
| Diablo 31 controller (KSEC/KWD) over a host-loaded `.dsk` | `bsv/Disk.bsv`, `sim/host.c` | boot smoke test |
| display sync generator (DVT/DHT/DWT/CURT), PBM field dump | `bsv/Display.bsv` | boot smoke test (the frame *is* the check) |
| keyboard / mouse I/O page (idle; scripted typing via `ALTO_TYPE`) | `bsv/Devices.bsv`, `sim/host.c` | none yet |
| 3 Mb/s Ethernet interface (task 7, 16-word FIFO, STARTF/ICMD/OCMD) | `bsv/Ethernet.bsv` | boot smoke test, indirectly (the Executive's Pup time request) |

Not modelled: Trident, Orbit/Dover, general Ethernet beyond the Pup time
reply, Alto I timings, 3K CRAM.

## Provenance of this directory

Imported 2026-11-24 from the separate repository `alto-bluespec`
(first commit e47186b, 2026-08-29), **including that repository's
uncommitted working tree as of 2026-11-24** (the Ethernet interface and
the changes that let the Executive set its clock). The files were copied
unchanged except for the layout (`src/` → `bsv/`) and the `Makefile`.
That repository's design note: the micromachine, disk controller and
memory cycle follow the *Alto Hardware Manual* (May 1979), not the
ContrAlto emulator; "Gaps" below lists where that does not yet hold.

## Build and run

Needs `bsc` (Homebrew `bsc` 2026.01 is the default; override
`BSC_HOME=`), plus the locally held files listed in
[`rom/MANIFEST.md`](rom/MANIFEST.md) and
[`disks/MANIFEST.md`](disks/MANIFEST.md).

```sh
make sim
make run DISK=disks/diags.dsk CYCLES=60000000
make smoke
```

| variable | meaning |
| --- | --- |
| `ALTO_DISK` | Diablo `.dsk` (Bitsavers packing: dummy word + header + label + 256 data words per sector, little-endian) |
| `ALTO_CYCLES` | stop after this many microcycles (default 2e6) |
| `ALTO_TRACE` | `1` prints PC / task / µPC every 1000 cycles |
| `ALTO_FRAME` | output PBM path, written on shutdown if a field completed |
| `ALTO_TYPE`, `ALTO_TYPE_AT` | characters to press on the keyboard, and the cycle to start (default 55e6) |
| `ALTO_TIME` | Pup time reply, seconds since 1901-01-01 GMT (default mid-1985) |
| `ALTO_ETHER_DEBUG` | `1` logs Ethernet TX/RX |

`sim/host.c` also writes `alto_frame_f<N>.pbm` snapshots into the
current directory at some fields; run from a scratch directory (the
smoke test does).

## Tests

`tests/run_smoke.sh` boots `diags.dsk` for 60 M microcycles and compares
the SHA-256 of the display field with `tests/golden/diags_exec_60M.sha256`.

* **Standard: regression only.** The golden hash was recorded from this
  model on 2026-11-24, after the frame was inspected by eye (Executive
  banner, `OS Version 18/16`, and the `>` prompt). It detects change,
  not correctness. Two runs gave the same hash.
* **Discrimination, observed 2026-11-24.** Injected: in `bsv/ALU.bsv`,
  `AluBusMinusTMinus1`'s carry `s >= 0` → `s > 0` (borrow wrong only when
  BUS = T + 1). Observed: the frame hash changed (`94e4c4d0…` instead of
  `3198b137…`) and the script reported FAIL. Reverted; the file is
  byte-identical to the imported one.

## Gaps against the repository's method (AGENTS.md)

These keep the model below the bar the rest of the repository uses;
they are the work list for this directory.

1. **No primary oracle.** The printed Alto microcode listings (source
   beside assembled octal) would play the role Stretch's IBM listings
   play: check the PROM images word by word against print.
2. **Citations are by manual section (`§6.1`), not printed page**, and
   the *Alto Hardware Manual* is not yet in `docs/` with a checksum.
3. **ContrAlto influence.** `bsv/AltoTypes.bsv:191` (constant PROM gated
   for BS ≥ 4) and `bsv/CPU.bsv:101` (field start blocks DHT/DWT) cite
   ContrAlto. Each must be traced to the manual or recorded as an open
   question.
4. **Unimplemented is not yet loud.** Undefined F1/F2/BS encodings fall
   through `default:` arms instead of stopping the simulation.
5. **Deliberate deviations, to be documented with numbers:** seek time
   is accelerated for Bluesim (word time 56 clocks and SECLATE ≈ 86 µs
   are the hardware figures); the Pup time reply is synthesised by the
   host, not by a modelled network.
6. **Display polarity unverified.** The dumped field shows white text on
   black; the Executive is normally black on white. Either the PBM
   writer or the model's polarity handling is inverted.
7. **PROM provenance.** The upstream dump files and the decoding into
   `rom_arrays.h` are not recorded (`rom/MANIFEST.md`).
