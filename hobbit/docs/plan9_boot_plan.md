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

**One kernel image is in the release, and it is not from these
sources.** `plan9-1e.tar.bz2` ships no `/9/` tree (0 entries), but
`hobbit/s9term` is a `zl -H1` image of the `term` configuration, built
1992-11-07 from an earlier revision of the kernel and libc than the
sources the release ships (`docs/s9term.md`, found 2026-11-20/23).  It
fixes the format, configuration and link order; booting the shipped
sources still means producing the image ourselves.

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
    device register would have seen them.  (That 2,399 counted clocks,
    not requests: the meter was fixed 2026-11-23, and the reads that
    remain are wrong-path operand fetches the part makes too,
    `docs/conformance_1to1.md` §1c.)

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

**Status 2026-11-23 (later): linked; the gate as written is closed.**
The release's `zl` links `9term` on the reference model, from inputs
every one of which the release's own tools made on the model:

    python3 tools/p9kgen.py --out K                  # term.c, bootterm.root.c, kerndate, ...
    python3 tools/p9kbuild.py kernel --kgen K        # libram.a, f709cea9...
    python3 tools/p9kbuild.py link --kgen K --check  # 9term

**End to end, in one go (2026-11-23):** `python3 tools/p9kbuild.py
all --build DIR` runs the three in one fresh directory, nothing reused
(p9kgen into DIR/kgen, then `kernel --kgen DIR/kgen`, then `link --kgen
DIR/kgen --check` on the libram.a just made; DIR/all.log).  Run once,
from a snapshot of commit a7af5631 (the commit that added `all`), on the
loaded machine: p9kgen 75 programs, 915,322,786 instructions, 7,828 s;
kernel 65 programs, 523,036,991 instructions, 1,136 s (8 processes);
link 4 programs, 421,230,961 instructions, 2,742 s (zl 351,299,086,
2,270 s).  **In all 144 programs, 1,859,590,738 instructions, 11,706 s
(3 h 15 min) wall.**  `libram.a` came out
`f709cea932f1a3694a08a93f4eb013c4a0703499938d0a9cd31ba0d8515b7ea6`
(`LIBRAM_SHA256`), `9term`
`002880c011bd7418c36c036b16f450e61d1ed43e1ec963a6f5b4574a2eece1b1`,
and `--check`'s comparison with `NINETERM_SHA256` ran in a full link for
the first time and passed; check_kernel passes, p9kcmp exit 0.  At the
later commit that counts the exec frame's clock hole
(`docs/plan9_syscalls.md`), `kernel --kgen` on the same kgen products
gave the same `libram.a` and every object's size and sha256 the same;
eight compiles retire one instruction fewer (the argument strings sit 4
bytes lower).  That commit's `link --check` (which now also runs the
rule's `size 9term`) then gave the same `9term` sha256, zl's same
351,299,086 instructions, and `size` printed `224160t + 72908d +
101152b = 398220`: the header's text 224,236 less
sizeof(struct mipsexec) = 76 (libmach's `hobbitboot`, as for s9term,
`docs/plan9_port.md`), data and bss the header's; `--check` passed.
`link` (the mkfile's `9term` rule) stages a fresh tree, runs `za
raml.s`, `zc -w -Dram -DKERNDATE=721110517 term.c` and `zc -w -Dram
bootterm.root.c` (the three objects equal the ones p9kgen and the kernel
target made), then `zl -o 9term -l -R4 -H1 -T0x80004000 -E0x80004000
raml.z term.z bootterm.root.z libram.a -lgnot -lg -lc` against the
vendored `libgnot.a`, `libg.a`, `libc.a`.  The log
(`BUILD/link-term.log`) records every input's sha256.

* **The link**: zl `exits('')`, prints nothing, **351,299,086
  instructions**, 753 system calls, 2,878 s wall on the loaded machine
  (the three compiles before it 69.9 M more, about 9 min).  `9term` is
  562,452 bytes, sha256
  **`002880c011bd7418c36c036b16f450e61d1ed43e1ec963a6f5b4574a2eece1b1`**
  (`p9kbuild.NINETERM_SHA256`; `--check` fails on any other).
* **Reproducible**: the recorded command run twice more (at once), each
  in its own fresh `--build` directory, gave the same sha256 and the
  same status, instruction count, system calls, size and sha256 for
  every one of its four steps as each other, and the same image as the
  scratch run before them; 3,337 and 3,345 s wall.  (They ran before
  the sha256 was written into `NINETERM_SHA256`; `--check`'s own
  comparison was first exercised by a full link in the `all` run
  above.)
* **`p9exec` accepts it** as a `-H1` image: every constant header word,
  the file size (80 + text + data + syms + lcsize), the section bases,
  `etext/bdata/edata/end` against the header, and every one of its
  8,287 symbols inside its section (`check_kernel`, the checks asm.c and
  pass.c's `xdefine`s imply).
* **zl's own relocation/symbol checks passed**: every check in the
  vendored `sys/src/cmd/zl` reports through `diag()` (44 call sites --
  `undefined:` pass.c:302, `undefined external:` span.c:250 and
  asm.c:544, among them), which counts `nerrors` (list.c:215), and
  `errorexit()` (obj.c:209-216) removes the output and exits `"error"`
  when any was counted.  zl exited `''` with nothing on its console (the
  driver fails otherwise), so it counted none.
* **`tools/p9kcmp.py 9term`** against s9term: **every MUST item agrees**
  -- header constants, entry 0x80004000 = `_startup` and its first four
  instructions, raml.s then term.c, the libraries in link-line order,
  `kerndate` 721110517, `conffile` "term", `devchar`'s 21 characters,
  all 21 x 13 `devtab[]` functions by name, `streaminit`'s four
  `newqinfo` arguments, the 60 `initcode` bytes.  Reported, with the
  reason (the sources drifted, `docs/s9term.md`):

  | | 9term | s9term | |
  |---|---|---|---|
  | text | 224,236 | 219,968 | +4,268 |
  | data | 72,908 | 70,388 | +2,520 |
  | bss | 101,152 | 98,476 | +2,676 |
  | symbols | 232,036 (8,287) | 227,808 (8,136) | +151 records |
  | pc/line | 33,192 | 32,602 | +590 |
  | file | 562,452 | 550,846 | +11,606 |

  The text difference is accounted for object by object (35 objects
  differ in size, summing to exactly +4,268): the largest are `scsi.c`
  +1,168 (six functions the vendored file has and s9term does not),
  `kbd.c` +1,018 and `latin1.c` +170 (linked here, absent there: the
  vendored `screen.c` calls `kbdinit`), `devbit.c` +918, `devip.c` +214,
  `deveia.c` +200, `raml.s` +164 (`getcpureg`), `devscsi.c` -208,
  `rune.c` +42 (the January libc).  The functions defined only in one
  image are exactly the per-file table of `docs/s9term.md`, found there
  from the sources and here from the two links.  `-lgnot`, `-lg` and
  `-lc` load the **same members in the same order** as s9term (7, 3,
  19).  `libram.a`'s order differs in four places (`deviic`, `scsibuf`,
  `screen`/`devbit` placement) besides `kbd` and `latin1`: here those
  members keep the relative order of the generated `DEV=` list
  (`deviic` before `deveia`, `scsibuf` after `scsi`, `devbit screen kbd`
  before `devkprof`); in s9term they do not (`deviic` after `devwren`,
  `scsibuf screen devbit` after `fcall`).  Load order is by need (zl
  scans `__.SYMDEF` from the start each pass), so this says s9term's
  `libram.a` or its `term` file listed them differently; which, is not
  known.  The embedded boot program is the 27,108-byte one p9kgen
  made (s9term's is 26,796; above).

The gate -- "the image's `Exec` header passes `tools/p9exec.py` and the
relocation/symbol checks ...; the image is reproducible from a recorded
command" -- holds.  What it does not say, and is **not** shown: that this
kernel boots (A4), or that it is the bytes Bell Labs would have linked
from this tree (no oracle: s9term is older).  The link was not
attempted on the Bluespec core.  In the suite: `p9kcmp`
on s9term and on corrupted copies (`tests/test_p9kcmp.py`, each MUST
item injected, plus three injections into the tool itself recorded in
its header); the link itself is the long run, as `9term` is a build
product and not committed.

**Status 2026-11-23: the kernel library is built; not closed.**
`tools/p9kbuild.py` (the recorded command; module doc for the details)
drives the release's own binaries on the reference model in a staged
copy of the tree (`build/p9kbuild/<target>/root`, never the vendored
tree), up to 8 processes, and logs every step's status, instructions,
system calls, output size and sha256 (`build/p9kbuild/<target>.log`):

* **`libram.a` for `term`** (`python3 tools/p9kbuild.py kernel`): all
  62 objects of the mkfile's `$OBJ` -- 61 by `zc -w -Dram` (port files
  `-I. ../port/X.c`, `fcall` without `-I.`), `fprt0.s` by `za` -- and
  `raml.s` by `za`, every run `exits('')`; 481,491,651 instructions for
  the 63, 593 s wall at 8 processes on a loaded machine.  Smallest
  `latin1` (1.8 M), largest `devbit` (26.4 M); the only console output
  is zc's own `warning: scsi.c:808 param declared and not used: ur`.
  Then `ar vu libram.a $OBJ` and `rl libram.a`, as the mkfile's
  `$LIBRARY` rule says (`$RL` is `rl`, `/hobbit/mkfile`): `ar vu`
  600,951 instructions, `rl` 40,564,708 (1,129 symbols), its `ar rb`
  378,848, giving a 1,196,514-byte `libram.a`, `__.SYMDEF` then the 62
  members in `$OBJ` order, sha256
  `f709cea932f1a3694a08a93f4eb013c4a0703499938d0a9cd31ba0d8515b7ea6`.
  The whole run takes about 17 minutes.  A second run in a fresh build
  directory gave the same archive and the same status, instruction
  count, system calls, size and sha256 for every one of its 68 steps
  (initcode, init.out, 63 assemblies and compilations, ar vu, rl, ar
  rb).  Nothing to compare the objects with: the release ships no kernel
  objects.  Inputs that are *not* the release's tools, each marked in the
  log and swappable:
  * `$DEV $STREAM $MISC` come from `rc ../port/mk{dev,stream,misc}list
    term` in the mkfile.  Until rc/sed/awk run on the model they are
    `tools/p9kbuild/term.{dev,stream,misc}list`, written by hand from
    those scripts and `term`, in the scripts' output format, so the
    generated lists can replace them unchanged.  They agree with the
    shipped `s9term` (`docs/s9term.md`): its 21 devices are in the
    order of the device-character string `/ce|psMd2trikSwlaPIbT`, which
    is the dev list's order, and its streams are urp, ip, async, fcall.
  * `devtab.h` (`rc ../port/mkdevh $CONFLIST`, included by ~25 objects)
    is a Python transcription of `mkdevh`/`mkextract`: **provisional**
    (`--devtab-h FILE` swaps in a generated one).
  * **All three are now made by the release's tools** (`tools/p9kgen.py`,
    below) and `p9kbuild.py kernel --kgen DIR` takes them from its
    output.  Compared 2026-11-23: the generated `DEV`, `STREAM` and
    `MISC` lists equal the hand lists, the generated `devtab.h` equals
    the transcription, and the generated `init.h` (the release's `xd`
    and `sed`) equals the transcribed one byte for byte.  `p9kbuild.py
    kernel --kgen DIR` then rebuilds `libram.a` with the same sha256,
    `f709cea9...`, its `rl` now running its own fork of `ar`
    (40,944,389 instructions with the child; 478 s for the 63 objects
    at 8 processes).
  * `init.h` (`rammain.c` includes it): `za initcode` and `zl -l -s -o
    init.out -H2 -T0x1020 -R4 initcode.z` run on the model, but the text
    step `xd -r -1x init.out | sed ...` is transcribed from `xd.c` and
    the two sed expressions.  **Provisional, and so is `rammain.z`**
    (`--init-h FILE` swaps).
  * rl's fork: see `ar` below.
  * Every object is given mode 0664 and mtime 726010682 before `ar`
    (the shipped libc.a's member mode and its `__.SYMDEF` date), so
    `libram.a`'s sha256 is reproducible; `ar` copies both into the
    member headers.  The mkfile's `rm -f $names` is not done (the
    objects stay for inspection).
* **`ar` and `rl` are validated against the shipped `libc.a`**
  (`python3 tools/p9kbuild.py archeck`, 36 s): `ar t` lists its 141
  members; `ar x` extracts all 140 objects byte-exact; `ar vu` of them
  (dated and moded as their headers say), then `rl` (8,351,588
  instructions) and its `ar rb`, rebuild a 297,782-byte archive whose
  members and all 141 headers are byte-identical to the shipped one and
  whose `__.SYMDEF` has the same 201 entries -- offsets, names, types,
  order.  212 bytes of the table differ, all after a name's NUL: stack
  residue in libmach `readar()`'s uninitialised `Prog p`
  (`docs/plan9_syscalls.md`).  **Traced 2026-11-23**
  (`tools/p9symdef.py`): every one of the table's 2,623 bytes past a
  NUL is accounted for -- 631 left by earlier names of the same member
  (the model's `rl` writes all of them identically), 1,992 the stack at
  readar's entry, which the frames of the release's **`/mips/bin/rl`**
  predict byte for byte (big-endian: objtype's `i` and Bseek's
  argument); so do the tables of 22 more shipped Hobbit libraries.  The
  shipped tables were written by the MIPS `rl` of a cross-building host,
  and the 212 bytes are where the Hobbit's own `rl` (little-endian `i`,
  no argument word at `id[5..8]`) must differ: not an exec-environment
  difference, and nothing to fix in the runner.  For this `p9run` gained `fstat` and
  `rfork(RFNOTEG)`; `rl`'s own `fork()`/`exec("/bin/ar")`/`wait` was
  refused (one process), so `rl` stopped at that call with its table
  written and the driver ran the `ar` command line `writerl()` would
  have.  **Since the merge with the generated-inputs work (below) the
  fork is p9run's**: `rl` runs to its end with the clock fixed at the
  table's date (`run(clock=)`), and `archeck` gives the same result
  (every member and header identical, the same 212 residue bytes; `rl`
  with its child 8,592,333 instructions).
* **libc reproduction is recorded** (`python3 tools/p9kbuild.py libc
  --check`, 260 s at 7 processes): the 102 C files of `libc/hobbit`,
  `port` and `9sys` that have a member in the shipped `libc.a`,
  196,999,046 instructions, none failed; **94 byte-identical** to their
  members, and the 8 that differ are exactly `port/{memmove, memset,
  strchr, strcmp, strcpy, strlen, strncmp, strrchr}.c`, whose members
  are `libc/hobbit`'s assembler versions (A2), as found by hand on
  2026-11-20.  A 3-file sample runs in
  `tests/run_tests.sh`.

(Then: `term.c`, `boot$CONF.root`, `KERNDATE` (p9kgen, below), the link
and the comparison with s9term -- done, the status above.)

**Status 2026-11-20 (kept for the record): started, paused.**  What was
done and what was not:

* *The compiler is reproduced on the reference model.*  The shipped
  `zc`, run by `tools/p9run.py` in a tree laid out like the release
  (`/sys/include`, `/hobbit/include`, `--cwd` the source directory),
  compiles every C source of libc that has a member in the shipped
  `libc.a` (`libc/hobbit`, `port`, `9sys`; 102 files, 197 million
  instructions): **94 objects are byte-identical to the shipped members**
  and none failed.  The 8 that differ are `port/{memmove, memset,
  strchr, strcmp, strcpy, strlen, strncmp, strrchr}.c`, whose archive
  members are built from `libc/hobbit`'s assembler versions instead
  (`za` reproduces those, A2).  This was run once by hand
  (a scratch script); **it is not in the suite yet.**
* *The compiler runs on the Bluespec core.*  `zc frexp.c`: 1,651,700
  retirements agree with the reference run, 101 kernel entries (75 of
  them floating point, replayed), `frexp.z` identical to the reference
  run's and to the shipped `libc.a` member (1,902 bytes).  **In the
  suite since 2026-11-23** (`tests/run_p9host_tests.sh`, step
  `zc-frexp`, about a minute; the tree is `sys/include`,
  `hobbit/include` and the source, with `P9CWD=sys/src/libc/hobbit`).
  It needed three more
  things from the core: `DQM` with a block source (golden 021); the
  one-parcel `ENTER`'s 8-bit offset one-filled, not sign-extended
  (p. 3-20 note a -- a frame over 2,048 bytes moved SP *up*; no golden
  can hold such a frame, so this is pinned only by the run); and the
  full PC in the retirement record (it printed 16 bits).
* *The reference model* resolves Table 4-34's undefined `8.S` cell with
  a stated choice (S = A), because `zc` executes that instruction.
* *A real kernel file compiles on the reference model*: `zc -w -Dram
  trap.c` in `sys/src/9/hobbit`, 8.5 million instructions, a 23,835-byte
  object.  Nothing to compare it with yet.
* *Vendored* for this: `sys/src/9/port`, `sys/src/9/boot`,
  `sys/include`, `hobbit/include`, `sys/src/libc` (`port`, `9sys`,
  `9syscall`, `hobbit`), `hobbit/mkfile`, and **`hobbit/s9term`**, a
  kernel image the release ships (550,846 bytes) -- the candidate oracle
  for the link.

Done 2026-11-23:

* *The oracle is read.*  `docs/s9term.md`: s9term is a `zl -H1` image
  (80-byte COFF-style header, `zl/asm.c` case 1), not stripped, text
  0x35b40 / data 0x112f4 / bss 0x180ac at 0x80004000, entry `_startup`;
  KERNDATE 721,110,517 (1992-11-07); the `term` configuration (devices
  `/ce|psMd2trikSwlaPIbT`, streams urp ip async fcall); a 26,796-byte
  stripped boot program; the library members in load order.  It was
  built from *older* sources than the release ships, so it can check our
  link's format, configuration and layout, not its bytes.
* *`tools/p9exec.py` reads kernel images* (`read_kernel`,
  `check_kernel`: every header word asm.c writes, the file size, the
  section bases, `etext/bdata/edata/end`, every symbol's section);
  `tests/test_p9exec.py` pins it with four corrupted copies.
* *`libgnot.a` and `libg.a` vendored* (the `9term` link's `-lgnot -lg`),
  `docs/plan9_port.md`.
* *`zc frexp.c` on the core is in the suite* (above).
* *The compiler run's unmapped reads are traced*: 1,376 was a meter
  counting clocks; the 51 real requests are operand fetches on the
  predicted path of mispredicted conditional jumps, which PRM p. 2-3
  says the part makes too (`docs/conformance_1to1.md` §1c).

**Status 2026-11-23: the generated inputs for `term` are made by the
release's own tools.**  `tools/p9kgen.py --out DIR` lays out a copy of
the vendored tree under `DIR/root` and runs, on the reference model,
every command `mk 9term` would run to make the kernel's generated
inputs, each a shipped Hobbit binary (`awk`, `sed`, `xd`, `grep`,
`sort`, `tr`, `strip`, `ar`, `rl`, `echo`, `cat`, `za`, `zc`, `zl`).
Python plays rc only: a pipeline is run a stage at a time, each stage's
standard output buffered and handed to the next as its standard input;
the awk and sed programs are taken out of the vendored scripts by an rc
quote/here-document reader, not retyped.  The system calls this needed
(stat, fstat, notify, rfork, fork/exec/wait, `#c/pid`, `#e`, create's
permissions, fd 0/1 redirection) are in `docs/plan9_syscalls.md`.

| product | made by | checked against | result |
|---|---|---|---|
| `errstr.h` | `mkerrstr` (sed) | the shipped `hobbit/errstr.h` | **identical** |
| first half of `systab.h` | `mksystab` up to its first `sam -d` (cat; sed \| tr \| sed; cat) | the first 806 bytes of the shipped `port/systab.h` | **identical**; the sam halves not run |
| `devtab.h` | `mkdevh cpu term termlocal bart rom` (awk; sort -u; awk) | -- (nothing shipped) | 286 lines |
| `term.c` | `mkdevc term` (cat, awk, echo, grep) | s9term's `devtab[]` resolved through its symbol table; `devchar`; `conffile` | **all 21 entries x 13 functions in order; devchar's characters; "term"** |
| `term.z` | `zc -w -Dram -DKERNDATE=721110517 term.c` | -- | compiles |
| `objlists` | `mkdevlist`/`mkstreamlist`/`mkmisclist term` (sed \| awk) | -- | `DEV=` 31 objects, `STREAM=` 4, `MISC=` none |
| `init.h` | `za initcode`; `zl -l -s -H2 -T0x1020 -R4`; `xd -r -1x \| sed` | s9term's `initcode[]` | **identical, 60 bytes** |
| `bootterm.c` | `../boot/mkboot term` (cat, awk) | -- | |
| `bootterm.root.c` | `zc` x 21, `ar vu`, `rl` (fork+exec of `ar`), `zc print.c`, `zl ... -lauth`, `mkroot` (strip; `xd -1x \| sed`) | s9term's `bootcode[]` (`bootlen` 26,796) | **differs**: see below |
| `bootterm.root.z` | `zc -w -Dram bootterm.root.c` | -- | |
| `KERNDATE` | not `date -n`: read back from s9term | -- | **721110517** = 1992-11-07 04:28:37 GMT, the `kerndate` word in s9term's data |

Cost (the recorded full run, 2026-11-23, one process on a loaded
machine): 74 programs, 908,516,178 instructions, 4,462 s.  Without the
boot program (`--no-boot`): 36 programs, 30,391,046 instructions,
217 s.  The long pole is mkroot's `sed` over `xd -1x`'s 1,695 lines of
the 27,108-byte boot image: **733,075,888 instructions, 3,332 s** (the
`s/ (..)/0x\1,/g` substitution costs ~27,000 instructions a byte); then
`zc bootterm.root.c` 60,064,630 (215 s), `xd -1x` 15,258,918, the 21
boot-library compiles 1.8-7.6 M each, the boot link 10,385,478.  Slow,
not impractical: the 1e `sed` stays the authority, and no host tool
stands in for any stage.  The suite runs a sample
(`tests/test_p9run.py` `KernelInputs`: `mkstreamlist`, `init.h`, 15 s);
`build/` is not in git: the products are remade by the command.

**The boot program does not reproduce s9term's, and the difference is
libc's, not the boot code's.**  Our `bootterm.out` (stripped) has text
0x5e30, data 0xb94, bss 0x4d0; s9term's `bootcode[]` has text 0x5cf8 and
the same data and bss.  The 2,964 data bytes are identical, function
pointers included.  Function by function (`bootterm.out`'s symbols laid
over s9term's bytes): every boot function from `main` to `getpasswd`,
and libc's `fmtinstall`/`numbconv`/`sconv`/..., sit at the same
addresses, and are either identical or differ in a few bytes (call
targets beyond the shift; not checked operand by operand); libc's
`convS2M` is where the shift starts -- everything after it is 268 bytes
lower in s9term -- and the rune functions (`chartorune`, `runetochar`,
`runelen`, `fullrune`, `utflen`) and the libc assembler routines after
them are not found in s9term at all.  Together with `devchar` (s9term
holds its `L""` string one byte per character; the shipped `zc` emits
16-bit runes), this says **s9term (whose `kerndate` is 7 November
1992) was linked against an earlier libc than the shipped `libc.a` (3
January 1993)**.  The boot program built here is the one the shipped
tree builds; s9term is not a byte oracle for anything linked with libc.
That also bounds the kernel-link gate: the image built from this tree
will not be byte-identical to s9term.

Not done at the time (the link is now done: the first status of this
section); the cost decision -- about 100 files at ~8 million instructions each is an
hour on the reference model and several on the core, so the full build
belongs in a recorded long run with a sample in the suite; and, for
the generated inputs, `mksystab`'s sam halves (no sam on the model).

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

The file server s9term's `/boot` needs (it is a terminal: root over IL
17008 after BOOTP) is a 1e 386 machine in QEMU, serving the whole 1e
release from a kfs made by 1e's own tools; a shipped 9pc terminal boots
its root from it over the same frame boundary the model's SONIC will
use. See [`qemu_1e_server.md`](qemu_1e_server.md) and `tools/qemu1e/`.

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

## A5 status, reference side (2026-11-23): the gate is met on the reference model

On `sem/hobbit_sem.py` (tools/p9boot.py, the shipped s9term) with its
root from the 1e 386 file server in QEMU (tools/p9join.py), a scripted
console session ran: `echo hello`, `ls /hobbit | wc`, `cat
/lib/ndb/local` (byte-identical to the release's file), `cd /usr/none`,
**`za hello.s`, `zl hello.z -lc`**, `ls -l`, `sum hello.z z.out` (the
same sums as the shipped za/zl/sum give under p9run), and `z.out`, which
printed `hello 1e`.  840,583,000 instructions, 42.2 s of model time,
732 s of host time.  Transcript, checks and commands: docs/p9boot.md
"Commands at rc's prompt"; `tests/net/a5_screen.txt`, `a5_uart0.txt`.
"A modelled disk image" in the gate is the server's kfs, a disk image
reached over IL: s9term is a diskless terminal (its WD33C93 finds no
targets), as the 1992 Hobbit terminals were.

What it took, each in docs/p9boot.md:

* **One time base** (ETHER_CHOICES `lockstep`): QEMU paused while the
  model is busy and run until the server's own tick counter catches up
  with model time; `-icount shift=4`.  Server IL resends to the prompt
  fell from 407 to 1-5; six consecutive live runs to `% ` and two more
  had no failure.
* **The user**: `none`'s home as 1e's PC install floppy has it
  (`/usr/none/lib/profile`, empty) on the server's kfs; init's
  `rc -c` then runs termrc and exits cleanly, and init restarts rc.
* **The ROM's fpi** (CHOICES `fpi-rom`): za's floating point goes
  through the unimplemented-instruction vector to the boot ROM's
  interpreter, which the release ships as source; `tools/p9kbuild.py
  fpi` builds it with the shipped za/zc/zl on the model (mkfile's
  `fpi.out` rule, linked in the ROM's segment).
* `JoinReplayTest` replays the recorded session through `echo hello`
  without QEMU (~3 min).

Not done: the Bluespec core has not run any of this; 8½ (bitmap and
mouse) is not modelled; the server's ack-0 IL sync race is a 1e bug,
not removed, not seen since (0 of 612 probe dials, 0 of 9 live runs).

## The Hobbit on the 1e network (2026-11-24): authenticated log-in, `cpu`, 8½ as glenda

On the reference model, s9term joins the three-machine 1e network of
`tools/qemu1e` (fs9: file and auth server; cpu9: a CPU server) through
`tools/qemu1e/hub.py` (`tools/p9join.py --hub`, one lockstep time base
over both QEMUs): glenda's wrong password is refused and her right one
accepted by fs9's check service (no `password not checked!`), and
`cpu -h cpu9` from the Hobbit's rc runs commands on cpu9 with the
Hobbit's name space on `/mnt/term`; with her profile's 8½ gate, 8½
starts for glenda as it does for tor.  `tests/test_p9hub.py` replays
the log-in in the suite (and `cpu`, with `P9HUB_CPU=1`).  Details:
docs/p9boot.md "On the 1e network", "8½ as glenda";
docs/qemu_1e_server.md 5d, 5e.

## A4/A5 status, our 9term (2026-11-24): the kernel built here boots and passes the A5 script

The `9term` A3 linked (sha256 `002880c0...`) boots on the reference
model with its root from the 1e server in QEMU (`p9join.py --image`) and
runs A5's command script to `end of script` and `% `: 603,242,715
instructions, 30.3 s of model time, 839 s of host time, 1221 frames; the
screen is s9term's (`tests/net/a5_screen.txt`) byte for byte except
pageinit's line (1362 free pages, not 1364: the kernel is three pages
larger).  Its `/boot`, built against the shipped libc and so not
s9term's binary, offers the same transports, takes `il`, sends the same
BOOTP request and joins.  Every other difference (no serial console, a
scan-code keyboard on Quart channel 2, the release's 25 Hz clock, BSS
size, IL resend timing) follows from the source drift docs/s9term.md
records; the table and the commands are in docs/p9boot.md, "Our 9term".
No bug in the build or in the reference model was found; the harness
gained typing on `kbd.c`'s keyboard (`tools/p9scancode.py`, p9boot
CHOICES `console-keyboard`).  The live run's pcap replays without QEMU
to the same instruction and the same screen.  In the suite:
`tests/test_own9term.py` (first line; Return at `/boot`'s prompt as scan
codes; the encoder against kbd.c), which skips its image tests, printing
the build command, where `build/p9kbuild/9term` is absent.

Not done: our 9term on the Bluespec core; 8½ (now that the keyboard
types, the display and mouse are what `tor`'s profile wants).

## A4 status, reference side (2026-11-23): s9term boots to init, root from the 1e server

`tools/p9boot.py` boots the shipped kernel image `s9term` on the
reference model (`sem/hobbit_sem.py` with a `System`: CPU-prefixed
control registers, CSP = ISP, the Chapter 2 MMU, the event sequences),
with a device model for each board register the kernel touches (Quart,
Irq, WD33C93, SONIC, IIC, LCD, incon), every unknown a stated choice.
Details, milestones and choices: `docs/p9boot.md`.

* 2,131,084 instructions: pageinit's line, byte-exact on the screen
  (`screenputs`) and, as `\r\n`, on Quart channel 0:
  `1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K`.
  Pinned by `tests/test_p9boot.py` (in the suite).
* 2,859,426: `touser`, the first CRET to user level (initcode), then
  `sysexec("/boot")` and `/boot` demand-paging in user mode; the clock
  interrupt (the Quart counter) is taken.
* 22,530,554: `/boot`'s prompt on the screen, `root is from (il, tcp, incon, 9600, 19200)[il]: ` (with `--counter-period 0.04`, a stated choice); it waits for a keyboard byte.  Its default transport, `il`, needs the SONIC ethernet and the IIC EEPROM (docs/p9boot.md).
* Idle skip (CHOICES `idle-skip`): `runproc`'s four-instruction idle
  loop is retired in whole laps up to the next timed device event, the
  run otherwise unchanged instruction for instruction (pinned: the 25 Hz
  prompt run still takes 22,530,554 instructions, now in 29 s instead of
  6 min).  At the formula's own clock rate the prompt comes after
  286,970,654 instructions (286,977,189 with the EEPROM; 286,977,105
  since the exception record costs `9 + D + A`, 2026-11-24), 14.4 s of
  model time, ~30 s of host time, so
  `--counter-period` is no longer needed.
* Console input: s9term's console is a serial terminal on Quart channel
  0 (`eiaspecial(0, &printq, &kbdq, 19200)`, `kbdq.putc = kbdcr2nl`;
  the image has no `kbd.c`).  Return typed there (`--type`) takes `il`:
  287,427,906 instructions (before the EEPROM: `sonic ether: 00 00 00 00 00 00`), then the
  first BOOTP transmit.
* EEPROM and SONIC: the PCF8584/PCF8582 answer deviic.c (ether address
  52:54:00:00:0b:0b, the one the QEMU server's ndb gives the Hobbit), the
  DP83932 is modelled as devether.c uses it (CAM, RRA/RDA, TDA, isr/imr,
  IRQ 9; QEMU's dp8393x.c followed where the driver is silent), and
  /boot's BOOTP request leaves at 287,845,754 instructions (287,845,670
  since the exception record's cost, 2026-11-24), decoding
  byte for byte (`--pcap`).
* The join (tools/p9join.py): s9term on the model, its SONIC's frames
  on QEMU's `-netdev dgram` pair to the 1e 386 file server
  (docs/qemu_1e_server.md), boots with its root from that server to
  **`init: starting /bin/rc`** at 310,933,347 instructions (15.6 s of
  model time, 150 s of host time, 277 frames): BOOTP from the server's
  ip/bootp, ARP, IL to il!10.9.0.1!17008, user none, the time written to
  the timekeeper, /hobbit/init from the server.  Its recording
  (`tests/net/join_init.pcap`) replays without QEMU, byte for byte and
  to the same instruction (`JoinReplayTest` now replays the longer A5
  recording, above).  The one device it needed beyond the SONIC: the
  MK48T02-style timekeeper at IONAK 0x2000/0x3FE0 (CHOICES `rtc`; the
  first live run stopped at setrtc).  No CRET was clamped on this
  path; the clamp (a CRET with MSP > SP + 256, notify()'s frames;
  CHOICES `cret-msp`) is what the no-server path needs: ten BOOTP
  requests, ten alarm notes, `My IP address[0.0.0.0]: `.  A later live run went on: `/bin/rc` from the server ran on the Hobbit
  (`Can't cd /usr/none`, `init: rc exit status: rc 9:can't cd`, as the
  server prints for glenda), and init's restart reached **rc's `% `
  prompt** at 618,458,635 instructions (31.0 s model time, 456 s host).
  The live join is not deterministic: one
  run was rejected by an ack-0 IL sync from the server (docs/p9boot.md).

The gate as written above (the boot banner and prompt on the UART) is
not met yet: s9term prints no banner of its own; the first text after
pageinit's line is `/boot`'s prompt.  The Bluespec-side DUART below is
unchanged.

## A4 status, core side (2026-11-24): s9term on the Bluespec core, record for record, into `/boot`

`bsv/run_p9kern.sh N` boots the same image on `mkHobbitCoreSystem` and
compares every retirement record with the reference boot's (every field
but `cyc`), device reads replayed and device writes checked, interrupts
delivered at the reference's instruction boundary (docs/p9boot.md, "The
boot on the core").  Every record matches through 2,893,000 on the
reference as merged 2026-11-23: `main` (125,203), `mmuinit`
(2,088,445), the console line, the first interrupt (2,848,972),
`touser` (2,883,341), `/boot` in user mode (2,886,866) and its first
system call (2,888,578).  Since 2026-11-24 every record matches through
**22,537,091** (re-pinned on the Quart's SC68C94 bids), where `/boot` prints `root is from` (PromptTest's
choices), after three fixes: precise store faults (2,893,033), no
retirement during an event sequence (3,298,054), ENTER's store check
(22,533,287).  Next: the join (BOOTP, `init: starting /bin/rc`, the
prompt), with SONIC's DMA replayed and the core on Verilator.  Findings:
docs/conformance_1to1.md §1d.  The suite runs the first 300,000
records, on Bluesim and on Verilator.

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
