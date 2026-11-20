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
records, linked at known addresses in `hobbit/bin/cat`) and from
`_vector0`'s calling convention (`raml.s`), never guessed. Required at
first: `write`, `exit`/`exits`, `open`, `read`, `close`.

**Achieved 2026-11-19.**  `bsv/run_p9.sh` runs 1st Edition
`hobbit/bin/cat` on the model with `sys/src/9/hobbit/raml.s` as its
standard input:

```
P9SHIM boot pc=00001000 sp=00008000 msp=00008100 isp=00000d00 psw=00000600
P9SHIM syscall=15 read fd=0 buf=00005fd0 n=8192 -> 7532
P9SHIM syscall=20 write fd=1 buf=00005fd0 n=7532 -> 7532
P9SHIM syscall=15 read fd=0 buf=00005fd0 n=8192 -> 0
P9SHIM syscall=8 exits msg=00000000 reads=2 writes=1
P9SHIM EXIT status=0
P9SHIM CONSOLE match: .../sys/src/9/hobbit/raml.s, 7532 bytes byte-exact
```

The script fails unless the console file equals the input byte for byte
and the run ends in `exits(0)`; it is in `tests/run_tests.sh`, twice:
once with `raml.s` and once with `trap.c` (10,642 bytes), which is longer
than `cat`'s 8,192-byte buffer and so makes `read` return 8192, then
2450, then 0, and `write` take counts that are not the file's length —
values the earlier one-bit shim could not return.

**Mechanism.** The kernel's own code is not in hand as a running image,
so the shim replaces only the *kernel side* of the syscall, never the
hardware's part:

1. the model performs the whole printed event sequence on the `KCALL`
   (PRM p. 3-29): `*(ISP-12) = src`, `*(ISP-8) = PC`, `*(ISP-4) = PSW`,
   `ISP -= 16`, `PC = *(VB+0)`, `PSW &= 0xFFFF0000`;
2. the testbench supplies the **vector page** (`evmem[VB]`, VB = 0x0c00)
   whose `+0` word is the stub, and the stub is Hobbit machine code
   (`tools/p9shim.py`, assembled by `asm/hobbit_asm.py`) placed in the
   boot window's 32-byte Exec header (`0x1000..0x101f`, below the text);
3. the **doorbell is the hardware's own frame write**: the host polls
   `ISP-12`, decodes the arguments from the user's stack
   (`CSP+4/+8/+12`, the 1e libc stub's convention), does the syscall
   against a host file, and clears the word;
4. the result comes back through **two memory words** the stub reads as
   absolute operands — `RES`, then `RDY` — and the stub puts `RES` in the
   accumulator and returns with the model's own `RETURN R0`;
5. the host then does the rest of `KRET`: the PSW from the frame's
   `ISP-4` word and `ISP += 16`.

**What it took in the core** (each found by this run, each its own
evidence):

* *Operands outside the stack cache read as zero.*  They are memory
  (p. 1-5, p. 1-12) and are now fetched from memory
  (`docs/conformance_1to1.md` §1a, golden `016`).  This was the
  `RETURN R8224 -> pc 0` failure, and it is also what lets the stub read
  the host's result: the earlier shim had one host-writable bit, `PSW.F`,
  could return only 0 or one constant, and could not be made race-free.
* *`ENTER`'s flush ignored `MSP > SHAD`* (p. 3-19): `cat`'s
  `ENTER R-8224` flushed 514 blocks the cache never held.  Fixed with
  golden `016` L12.
* *`KCALL`'s frame tail* drained from a starved rule (`bd1c6af`).

**Known limits, recorded not hidden.**

* The host copies `read`/`write` data to and from user *memory*.  Buffer
  words inside `[SP, MSP)` have their current value in the stack cache,
  so a program that itself touched those words would disagree with the
  host; `cat` passes its buffer through untouched.  A kernel entry that
  flushes the cache is the real answer (A3/A4).
* `cat`'s *error* path (`fprint` after a failed `write`) leaves the
  3 Kbyte prefetch window and stops with `fetch missed the 3 KB prefetch
  window`: the instruction supply has no on-demand fill yet.  The success
  path stays inside the window.
* The model has no `KRET`/`CRET`; the host restores PSW and ISP through
  the core's testbench surface.
* **The run says nothing about byte order.**  The shim's byte lanes are
  big-endian and 1e's are little-endian (PSW_UL); `cat` passes because
  it never reads a byte of its buffer.  See A2's status.
* An earlier note here said a `KCALL` executed *inside* the stub
  deadlocks the pipeline.  The stub no longer does that, and the claim
  has not been re-tested since the frame-tail fix; treat it as open.

### A2 — the toolchain bootstraps on the model

The release ships `hobbit/bin/{za,zc,zl}` as Hobbit executables. With A0
and A1 in place, run `za` on the model, assemble one file from
`sys/src/9/hobbit`, and compare its object with the shipped `.z` member
for the same source: byte for byte where the source is unchanged.

Gate: `za` reproduces a shipped object; `zl` (shipped) links it.

**Status 2026-11-20: reached on the Bluespec core.**  The gate as
written -- "`za` reproduces a shipped object; `zl` (shipped) links it" --
holds on the core for these runs (`tests/run_p9host_tests.sh`, in the
suite), each compared retirement by retirement with the same binary on
the reference model:

| run on the core | retirements compared | also agree in `cyc` | kernel entries | clocks | result |
|---|---|---|---|---|---|
| `za main9.s` | 125,572 | 125,110 | 16 | 607,737 | `main9.z`, 309 bytes, **byte-identical to the shipped `libc.a` member** |
| `za hello.s` | 107,164 | 106,785 | 16 | 520,579 | `hello.z`, 255 bytes |
| `zl -o hello hello.z -lc` | 697,197 | 696,100 | 60 | 2,268,867 | `hello`, 2,014 bytes, linked against the shipped `libc.a` |
| `hello` (the program just linked) | 319 | 319 | 2 | 957 | prints `hello 1e` |
| `echo hello world` | 1,808 | 1,808 | 2 | 10,259 | prints `hello world` |
| `cat trap.c` | 388 | 388 | 8 | 1,662 | 10,642 bytes, byte-exact |

(The gate's text names a file of `sys/src/9/hobbit`.  The release ships
no kernel objects -- one loose `.z` in the whole tree, `lib/c++/__ctdt.z`
-- so the shipped object to reproduce is a `libc.a` member, and `main9.s`
is the source of the startup every binary begins with.)

"Compared" means every HRI field but `cyc` agrees on every record
(`tools/p9trace_cmp.py`); the files and the console are what the *model*
wrote, taken from its memory at each `write` call.  What ran on the core
is `main9.s` and `hello.s` through `za` and one link through `zl` -- not
all twelve libc sources; those are reproduced on the reference model
only (below).

How the run is built (`bsv/run_p9host.sh`; details in
`docs/plan9_syscalls.md`): `tools/p9run.py` runs the binary on the
reference model and records the boot memory and every kernel entry;
`bsv/P9HostTb.bsv` boots that memory on the core, with `bsv/p9host.c`
(Bluesim BDPI) as a sparse 32-bit memory and a *replayer* that checks the
machine's system-call id and arguments against the recording at each
entry and hands back the recorded result.  The machine executes KCALL's
frame, the unimplemented-instruction sequence for floating point, and two
kernel-entry stubs itself; the host does KRET's PSW and ISP.

**What the core needed.**  Each of these was found by the record-by-record
comparison stopping, in this order, and each is its own defect or missing
piece (`docs/conformance_1to1.md` §1c has the detail and the tests):

1. little-endian data (golden 017);
2. on-demand prefetch fill -- `echo`'s `_main` and `main` are not in one
   1 Kbyte window;
3. **a mispredicted branch resolved in EU_S3 did not squash the
   wrong-path instruction already in EU_S2** -- it retired.  Needs a warm
   decoded-instruction store, i.e. a loop's second pass; `echo`'s 48th
   retirement (golden 018);
4. both operands indirect (`CMPEQ *R24.UB, *R28.UB`), refused by the
   decoder as "unimplemented" (golden 019);
5. `CALL *Roffset` and `JMP **$addr`, refused likewise (golden 019);
6. `ENTER *$addr` / `ENTER *Roffset`: refused by the decoder, and the EU
   took the operand *field* as the target where p. 3-20 says the target
   is fetched from memory (golden 019);
7. `DQM` with a constant source (golden 019; a source in memory is still
   not modelled and fails loudly);
8. the unimplemented-instruction sequence's `*(CSP) = PC` reached only
   the event unit's private memory, never the stack, so a handler that
   returns through the stack read a stale word -- and that private
   memory aliases addresses onto its vector table;
9. the stack cache dropped a store to a word a `CATCH` refill had not
   reached yet, and dropped the refill's word when a store coincided
   with it; and a second stack operation could replace a refill in
   flight.  None of this could happen while every run began with a full
   cache;
10. the prefetch fill and the stack cache each called the memory's one
    read port, and bsc composed them with one request *shadowing* the
    other (its G0117 warning said so): the fill installed the wrong
    word.  The box now owns the port and lends it;
11. with events enabled, the operand-latch rule and a pipeline rule were
    in a scheduling cycle that bsc broke by making them conflict;
12. (cycles only) a folded unconditional `JMP` was prefetched down its
    fall-through, "mispredicted" every time, and charged 3 where p. 4-3
    gives it 0 -- 3,808 of `za`'s records (golden 020);
13. (bus reads only) EU_S1 fetched a memory operand through a pointer
    whose newest value was still unexecuted in EU_S2 -- 2,399 reads of
    addresses the program never uses on `za`.  No value was wrong; a
    device register would have seen them.

And one thing the *reference model* needed: `za` copies a stack word it
never wrote.  What that reads is whatever the cache slot last held, so
the reference model now keeps the cache's 64 words when asked to
(`State.cache`).  The slot index and the zero for a never-written slot
are the core's, so for uninitialised reads the two models agree by
construction, not independently.

**Known limits of the core run.**

* Addressing is physical; a real 1e process runs with `PSW_VP`.
* The cache starts empty (MSP = SP) and is emptied at each kernel entry
  by the stub's `ENTER`; the real kernel returns with it loaded.
* After KCALL the PSW says CSP = ISP, and the printed `ENTER` would then
  move the ISP and flush nothing.  The core's execution unit does not
  model CSP = ISP (only the event unit reads PSW bit 9), so the stub's
  `ENTER` flushes the user's stack as intended; that is a property of the
  model, not of the part.
* KRET does not exist in the model; the host sets the PSW and ISP.
* Floating point is replayed from the reference run's emulation
  (`fpihobbit.c`'s decode, host doubles), not executed by 1e's handler.
* `cyc` is reported, not compared.  The records that agree in everything
  else and differ in `cyc` (462 on `za main9.s`) are all conditional
  jumps, in three classes, and are open (`docs/conformance_1to1.md`
  §1c).
* The ULX3S build has not been re-run with any of this.

**The reference model's run** (the oracle; `tests/test_p9run.py`):

* the shipped `za` assembles **every** assembler source of
  `sys/src/libc/hobbit` into an object byte-identical to the member of
  the shipped `hobbit/lib/libc.a` (3 January 1993) built from it:

  | source | instructions | source | instructions |
  |---|---|---|---|
  | `argv0.s` | 56,027 | `strchr.s` | 116,470 |
  | `main9.s` | 125,572 | `strcmp.s` | 690,377 |
  | `main9p.s` | 215,997 | `strcpy.s` | 545,325 |
  | `memmove.s` | 1,643,575 | `strlen.s` | 92,122 |
  | `memset.s` | 759,201 | `strncmp.s` | 163,931 |
  | `setjmp.s` | 190,011 | `strrchr.s` | 131,429 |

* the shipped `zl` links an object `za` has just made against the
  shipped `libc.a` (697,197 instructions, 60 system calls), and the
  linked program runs and prints its line;
* `echo hello world` prints `hello world` (1,808 instructions) and `cat`
  copies a named file.

What the reference run established before any Bluespec work:

1. **1e runs the Hobbit little-endian.**  `l.s` sets CONFIG.KL and a
   process's PSW carries PSW_UL (`machine.h:24,77`; `raml.s` builds the
   first CRET's PSW as `PSW_VP|PSW_UL|PSW_S`).  PRM pp. 1-3/1-4: the bit
   selects the numbering of bytes within data words; text is always
   big-endian.  Neither model had the mode.  Both have it now
   (`docs/conformance_1to1.md` §1b; golden `017` pins the user-level
   rule three ways; CONFIG.KL on the core is untested).
   `echo` jumps to 0x361d0000 without it (a function pointer read
   byte-reversed out of `doprint`'s format table).  **A1 did not see
   this and could not:** `cat` never looks at a byte, and the shim put
   bytes into words and took them out through the same (big-endian)
   lanes.
2. **Floating point is the unimplemented-instruction sequence.**  `za`'s
   `cinit` executes `FMOV $0.0, nullgen.dval` (five-parcel opcode 0x11,
   "unimp" in Table 1-20) 138 instructions in.  The chip performs
   `*(CSP) = PC; PC = *(VB+12)` (p. 1-39) and 1e's user-level handler
   (`fprt0.s`, `fpihobbit.c`, `fpi.c`) emulates the instruction.  The
   reference model now retires the `trap=1` record for every "unimp"
   dyadic opcode instead of refusing it, and `p9run` plays the handler
   (a transcription of `fpihobbit.c`'s decode; arithmetic in host
   doubles).  The core already decodes these as `TR_UNIMP`.
3. **The exec frame** is `sysexec`/`execregs`: `argc` is the returned
   accumulator at `CSP+4`, `argv` the pointer at `CSP+8`, the vector and
   strings just below USTKTOP = 0x80000000, `msp = USTKTOP`.
4. **System calls used by `za` and `zl`:** `brk_`, `open`, `create`,
   `read`, `write`, `close`, `seek`, `remove`, `exits` (and `errstr` on
   the failure paths).
5. **A quirk worth knowing before reading a trace:** `main9.s`'s
   `MOV $_exits<>+0(SB), R4` and its `DATA _exits<>+0(SB), $"main"` do
   not name the same symbol in `za`'s output (static in the MOV, extern
   in the DATA -- the bytes are in the shipped `main9.z`), so in every
   shipped binary the exit string `_main` passes is the address of
   libc's `_exits` *function* (`cat`: `MOV $0x12da, R4`).  A program
   that returns from `main` exits with the status `"\x02\x08\x02"`,
   the first bytes of `KCALL $8; RETURN R0`.

The vendored tree holds ten of the release's 387 `hobbit/bin` files:
`cat echo rc za zl`, and since 2026-11-20 `zc mk cpp yacc ar`, taken
from the same tarball (`plan9-1e.tar.bz2`, sha256 in
`docs/plan9_port.md`, re-verified that day) for A3.  Nothing has been
done with the new five beyond loading them on the reference model with
no arguments: `zc` and `ar` print their usage lines, `cpp` copies an
empty standard input, `mk` stops at `rfork` and `yacc` at `stat` --
system calls `tools/p9run.py` refuses, which is where A3 starts.
(`tools/p9exec.py`'s `_main` check rejects `zc`: its `_clock` is beyond
16 bits, so the startup's MOV is the five-parcel form.  The check is too
narrow, not the binary wrong; `p9run` does not use it.)

Also vendored that day, because `tools/p9run.py` and the docs cite them
as the authority for the system-call numbers and the exec frame:
`sys/src/libc/9syscall/sys.h` and `sys/src/9/port/sysproc.c`.

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

A0 and A1 are closed (see A1 above).  What they left open for A2 on the
Bluespec side: the kernel's call frame is still minimal (`argc = 1`, no
`argv` strings, set by the shim's first two stub instructions), the
instruction supply has no on-demand fill, so a program that leaves the
3 Kbyte prefetch window stops, and -- found 2026-11-20 by running the
binaries on the reference model -- the core had no little-endian data
mode, which every 1e program but `cat` depends on (A2's status above;
added with golden `017`).

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
2. **A1** — closed 2026-11-19: `cat` prints `raml.s` byte-exactly over the shim and exits 0.
3. **A2** — closed 2026-11-20: on the Bluespec core `za` reproduces the shipped `main9.z` and `zl` links what `za` assembled; the linked program runs.
4. **A3** — assemble and link the kernel; image checks.
5. **A4** — DUART model + boot to console; byte-exact banner gate.
6. **A5** — `rc`, disk `cat`, on-model `za`.
7. **B** — devices in the order of the table, each with its gate.

Steps 1–2 are small and unblock everything; 3–4 are the long pole and
depend on the model's ISA being complete enough for `za` (a large C
program), which A0/A1 will measure honestly.
