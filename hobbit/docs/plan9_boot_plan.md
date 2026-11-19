# Plan 9 1e on the Hobbit model: boot to the UART, then all the devices

Two goals, in order: **(A)** the 1st Edition Hobbit kernel boots on the
model and prints on the serial console; **(B)** every device the 1e
Hobbit port drives is modelled and exercised by real 1e software.
Every claim carries a path and page or file cite, as elsewhere in this
directory.

## What the sources say

| item | where | state |
|---|---|---|
| Hobbit kernel port | `tools/plan9-1e/sys/src/9/hobbit/` (40 files) | sourced, not built |
| reset / vectors / `_vector0` syscall entry | `raml.s` (`_vectors+0x00 = $syscall`, `raml.s:287`), `roml.s` | read |
| kernel C entry | `rammain.c` (RAM loader), `rommain.c` (ROM) | read |
| serial console | `deveia.c` — the only kernel file that names the DUART/Quart registers of `io.h` (`IRQQUART`, `Eiaaddr`) | identified |
| keyboard / display | `kbd.c`, `screen.c`, `devincon.c` | sourced |
| storage | `scsi.c`, `scsibuf.c`, `sd` drivers in port | sourced |
| clock / RTC | `clock.c`, `devrtc.c` | sourced |
| Ethernet / IIC | `devether.c`, `deveia.c`, `deviic.c` | sourced |
| MMU | `mmu.c`; model has `HobbitMmu` | modelled, untested against kernel code |
| user binaries | `hobbit/bin/` (shipped) | run on the model: first instruction retires |

**There is no kernel image in the release.** `plan9-1e.tar.bz2` ships no
`/9/` tree (0 entries), only the kernel *sources*, the user binaries and
the z libraries. So booting 1e has to produce the image ourselves.

## Goal A: boot and print

### A0 — the model runs 1e user code to completion of the startup

Gate: `run_p9.sh cat` executes `_main` and `main` and reaches the first
`write` syscall. Blocked today by one parcel: the `0x0000` between
`_main`'s first MOV and the two parameter loads (`0xffff` in `echo`).
Resolve it from Bell Labs' own `main9.z` records, linked by the rebuilt
`zl` (or read straight out of the shipped binary at a second site), and
then implement whatever the run demands next — the model refusing loudly
is the contract and the guide.

### A1 — a host shim for the syscalls the startup and `za`/`zl` need

Gate: `cat` prints a file over the shim's `write`; `exits` returns 0.
Syscalls are taken from libc's own stubs (`hobbit/lib/libc.a` member
records) and from `_vector0`'s calling convention (`raml.s`), never
guessed. Required at first: `write`, `exit`/`exits`, `open`, `read`,
`close`.

### A2 — the toolchain bootstraps on the model

The release ships `hobbit/bin/{za,zc,zl}` as Hobbit executables. With A0
and A1 in place, run `za` on the model, assemble one file from
`sys/src/9/hobbit`, and compare its object with the shipped `.z` member
for the same source: byte for byte where the source is unchanged.

Gate: `za` reproduces a shipped object; `zl` (shipped) links it.

### A3 — build the kernel

Assemble and link `sys/src/9/hobbit` (`mkfile` names its files) on the
model, producing a 1e Hobbit kernel image. Gate: the image's `Exec`
header passes `tools/p9exec.py` and the relocation/symbol checks the
`zl` sources define; the image is reproducible from a recorded command.

### A4 — boot to the console

Model side: the DUART registers of `io.h` (`Eiaaddr`, the `Duart`/
`Quart` structs), their interrupt (IRQQUART 0x0002, `IOACK`), and a UART
that puts bytes on the model's `txd` — the same 8N1 writer already
proven by `run_board_tb.sh`.

Kernel side: reset at `raml.s`'s start, MMU tables built by `mmu.c`,
then `rammain.c` to the console. Gate: **the model prints 1e's boot
banner and prompt on the UART**, byte-exact against a captured reference
(the distribution's own console output for the same kernel revision, or
a hand-derived transcript), and the HRI stream shows the boot executing.

### A5 — usability gates

Gate: a shell (`rc`) from `hobbit/bin` runs over the console, `cat`
reads a file from a modelled disk image, and `za` assembles a program
*inside* the boot. That is "1e is running", not "the model can run one
binary".

## Goal B: all the devices

Inventory is fixed by the port's own files; each row is a milestone with
the same shape: registers and interrupts from `io.h`, a model module
behind the bus face (`HobbitBus`), a testbench that drives the model,
and an end-to-end gate using real 1e software.

| device | kernel file(s) | first gate |
|---|---|---|
| serial console (DUART/Quart) | `deveia.c`, `io.h` | A4 |
| keyboard | `kbd.c` | keystrokes reach `rc` |
| display / screen | `screen.c`, `devincon.c` | console window bytes match |
| RTC | `devrtc.c`, `clock.c` | `date` prints the model's clock |
| SCSI host adapter | `scsi.c`, `scsibuf.c` | `cat` of a file from a disk image |
| Ethernet (EIA/AUI) | `deveia.c`, `devether.c` | `ip/ipconfig`-equivalent over a model NIC |
| IIC bus | `deviic.c` | EEPROM read path |
| FPU | `fpi.c`, `fpihobbit.c` | a floating program's results |
| timers | model `HobbitTimers` | kernel clock ticks |
| MMU | `mmu.c` vs `HobbitMmu` | kernel page tables translate |

Each device milestone must keep the repository suite green and add its
own discriminating test (inject the specific bug, record the observed
failure set, revert).

## Order of work

1. **A0** — the parcel, then run the startup to the first syscall.
2. **A1** — syscall shim (`write`, `exits`, `open`, `read`, `close`).
3. **A2** — `za`/`zl` bootstrap on the model; compare with shipped objects.
4. **A3** — assemble and link the kernel; image checks.
5. **A4** — DUART model + boot to console; byte-exact banner gate.
6. **A5** — `rc`, disk `cat`, on-model `za`.
7. **B** — devices in the order of the table, each with its gate.

Steps 1–2 are small and unblock everything; 3–4 are the long pole and
depend on the model's ISA being complete enough for `za` (a large C
program), which A0/A1 will measure honestly.
