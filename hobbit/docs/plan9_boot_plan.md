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
| user binaries | `hobbit/bin/` (shipped) | `_main` and `main` run on the model (A0 status) |

**There is no kernel image in the release.** `plan9-1e.tar.bz2` ships no
`/9/` tree (0 entries), only the kernel *sources*, the user binaries and
the z libraries. So booting 1e has to produce the image ourselves.

## Goal A: boot and print

### A0 — the model runs 1e user code to completion of the startup

Gate: `run_p9.sh cat` executes `_main` and `main` and reaches the first
`write` syscall.  Status: `_main` and `main` now execute; the run stops
inside libc's `exits` at the first instruction the core does not
implement (`SHL3`, see the A0 status below), so reaching `write` waits
on that instruction and on the syscall shim (A1).  The "one parcel" that
blocked this was not a parcel at all: see below.

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

## A0 status (2026-11-19): closed — there was no hole

**The parcel question is answered: there is no hole, no padding and no
uninitialised text.** The text section is a sequence of 32-bit words
stored **little-endian**, and within a word the **high half is the
earlier parcel**. The `0x0000` that used to sit "next to `_main`'s first
MOV" is the **second parcel of that three-parcel MOV** — its 32-bit
source field, the stack offset 0 of `R0`.

Two independent proofs, as required:

* **`zl` links Bell Labs' own startup.** `tools/build_zl_inferno.py`
  now builds the 1e linker and `--link-main9` links `libc.a`'s
  `main9.z` with the real members defining `_clock` and `exits`
  (`argv0.z`, `atexit.z`, `_exits.z`), then prints `_main`'s parcels:

  ```
  header: magic 0x197  text 0xbc  data 0x10  bss 0x84  syms 0x5cc  entry 0x1022
  main   0x00001020      _main 0x00001022      _clock 0x00002004
  `_main` at 0x1022, parcels (address order):
    1022  0bfc                 ENTER R-16        (zl-inserted)
    1024  86dc 0000 2004       MOV R0,_clock
    102a  60a1                 MOV argc+0(FP), R4
    102c  60c2                 MOV argv+4(FP), R8
    102e  07f9                 CALL 1020
    1030  c6fd 0000 10d6 ...  MOV $_exits,R4
    103a  0433                 CALL 10a0
    103c  0ffa                 JMP 1030
  ```

  `_main` starts at its symbol address with `ENTER R-16`, which `zl`
  inserts for `TEXT _main(SB), 1, $12` (`pass.c`'s `follow()`, case
  ATEXT); its second instruction is the MOV, and its second parcel is
  0x0000.  The `CATCH R16` the shipped binaries carry after the call is
  the same function's ACALL case, and a program object with a `$2048`
  frame makes the linker emit it, which is the discriminating test.
* **All five shipped binaries, read in address order.** Every `_main`
  is `ENTER` (0x0bfc), `86dc <hi> <_clock>`, `60a1`, `60c2`, `CALL`,
  and the CALL lands **exactly on that binary's `main` symbol**:

  ```
  cat  entry 012bc  main 01020  exits 01170 : 0bfc | 86dc 0000 3004 | 60a1 60c2 | 06ac→1020 | 0805 | c6fd 0000 12da 0000 0004 | 074d→1170
  echo entry 02ad0  main 01020  exits 0141e : 0bfc | 86dc 0000 4008 | 60a1 60c2 | 80e1 ffff e544→1020 | 0805 | ...
  rc   entry 0b9c6  main 03112  exits 0ae9c : 0bfc | 86dc 0000 e098 | 60a1 60c2 | 80e1 ffff 7740→3112 | 0805 | ...
  za   entry 07282  main 02198  exits 05964 : 0bfc | 86dc 0000 8050 | 60a1 60c2 | 80e1 ffff af0a→2198 | 0805 | ...
  zl   entry 0995c  main 03c96  exits 081a6 : 0bfc | 86dc 0000 b084 | 60a1 60c2 | 80e1 ffff a32e→3c96 | 0805 | ...
  ```

  The `0xffff` in `echo`/`rc`/`za`/`zl` is the high half of a 32-bit
  CALL displacement (the long form `0x80e1` is used when the target is
  farther than the one-parcel 10-bit range): not a filler, not a hole.
  `rc`/`za`'s entry addresses are ≡ 2 (mod 4) because a one-parcel
  instruction precedes `_main`; the parcel at such an address is the
  low half of its word, and the decoder selects the half by address.

**The linker's crash had a single cause.** `diag`'s 1993 varargs hack
`doprint(..., &(&a)[1])` (`list.c:212`) passed a pointer into the
caller's frame as a `va_list`; on arm64 the callee reads the format
string's bytes as the `%s` argument, which is the `EXC_BAD_ACCESS` in
`_platform_strlen` (`lldb`: `x0 = 0x656e696665646e75`, the ASCII
`"undefine"`, callers `patch()` → `diag` → `doprint`).  `va_start`/
`va_end` is the fix.  Five further host-port defects were found and
fixed the same way (all in patched copies of the vendored sources, listed
in `tools/build_zl_inferno.py`): `Rlent.offset` must be 32-bit (28-byte
1e symbol entries), `$ZLLIB` must replace `/hobbit/lib`, `ldobj` must
zero its `Prog`s, Inferno's fmt has no `%f` and must not be handed the
1993 `%P` conversion, and the installed `%A/%D/%P` text is unavailable.

**The model now runs the startup.** `tools/p9exec.py` reads the text as
little-endian words and writes the model image; `bsv/run_p9.sh cat`
retires ENTER, the MOV to `_clock`, the two parameter loads and the CALL;
`main` runs; the run stops in libc's `exits` at the first instruction the
core lacks — one-parcel `SHL3 $2,R12` (0x7843) at 0x1178:

```
HRI pc=12bc insn=0bfc0000 sp=00000800>000007f0 ... cyc=197
HRI pc=12be insn=86dc0000 ... we=1 addr=00003004 data=00000000 mask=0f
HRI pc=12c4 insn=60a10000 ... we=1 addr=000007f4
HRI pc=12c6 insn=60c20000 ... we=1 addr=000007f8
HRI pc=12c8 insn=06ac0000 ... we=1 addr=000007f0 data=000012ca
...
FAULT pc=00001178
TRAP pc=0x00001178: unimplemented opcode (Tables 1-15..1-20)
```

`echo` retires the same five startup records (at 0x2ad0, `_clock`
0x4008, `insn=80e1ffff` for the long CALL) and then stops with
`TRAP pc=0x00001020: fetch missed the 3 KB prefetch window`, because its
entry (0x2ad0) and `main` (0x1020) cannot share one 1 Kbyte boot window
and `mkHobbitPrefetch` has no on-demand fill.

Still open for A0/A1, in order: the kernel's call frame (`argc`/`argv`
are zero today, so `cat` takes its `argc = 0` path and exits), one-parcel
`SHL3`/`SHR3` in `HobbitDecode.bsv` (0x1E/0x1F), then the user-side
trap (`CPU` escape) and the `write`/`exits` shim.

## A4 status (DUART): model written, gate red, parked (2026-11-19)

A first `mkHobbitDuart` exists but its gate is **not** green: 26 of 37
checks pass, the receive path works end to end (`rx_data`, `rx_irq`,
`isr_rx_ready`), and the transmit path never starts because the
testbench's bus-driving rule and the device's shift rule starve each
other (`bsc` reports "rule step can never fire" in one ordering and
"duart_shift" starvation in the other; `descending_urgency` remedies the
symptom in one direction only).  The fix belongs in the design, as the
one-rule-per-behaviour rule in `skill://hobbit` says: a device stage
should advance its own shifter in the same rule that accepts its
register writes, not in a competing one.

The work is preserved at `/tmp/duart-wip/` (`HobbitDuart.bsv`,
`HobbitDuartTb.bsv`, `run_duart.sh`) and is **not** in the suite, so the
repository gate stays honest.  Its register map cites `io.h:1,20,32-96`,
`mem.h:43`, `deveia.c:18-81,351-422,481-483,501-563,600-615`.

Also corrected here: `BD19200` is **0xCC** (`deveia.c:54`), not 0xBB —
the DUART agent caught that against the inventory.

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

1. **A0** — closed: there is no parcel; the startup runs to the core's first refusal.
2. **A1** — syscall shim (`write`, `exits`, `open`, `read`, `close`).
3. **A2** — `za`/`zl` bootstrap on the model; compare with shipped objects.
4. **A3** — assemble and link the kernel; image checks.
5. **A4** — DUART model + boot to console; byte-exact banner gate.
6. **A5** — `rc`, disk `cat`, on-model `za`.
7. **B** — devices in the order of the table, each with its gate.

Steps 1–2 are small and unblock everything; 3–4 are the long pole and
depend on the model's ISA being complete enough for `za` (a large C
program), which A0/A1 will measure honestly.
