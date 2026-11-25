# PDSS on a modern machine

PDSS V2.52.20 (ICOT, 1992) is a complete KL1-B abstract machine in C:
interpreter, scheduler, suspension, copying and MRB garbage collection,
shoen, exceptions, built-ins, with its own KL1 compiler (written in
KL1) and Micro PIMOS. It is the nearest surviving *source* to the
firmware that ran PIMOS (`docs/pimos_boot_requirements.md` §0.1). This
directory holds it, made portable C, and the tests that show it still
behaves as the 1992 program did.

    ./test.sh        # build src/, run a KL1 program, conformance (~30 s)
    ./test_slow.sh   # every target this host can build (several minutes)
    ./modern.sh T    # build target T into build-T/ (see "Targets")

## The source in tree: `src/`

`src/` is the PDSS V2.52.20 distribution, `docs/nonlocal/pdss.tar.Z`
(SHA-256 `3da79c34abf3bcd5f30d0b178b869ee25b4cc544de82713552721da94888c13c`),
imported with the tarball's own layout: `emulator/` (the C program),
`runtime/`, `mpimos/`, `compiler/`, `debug_utl/`, `pimos_utl/` (KL1
sources and their `.asm`), `compiler_pl/` (the Prolog-hosted bootstrap
compiler), `test/`, `sample/`, `macro/`, `emacs/`, `doc.e/`, `doc.j/`,
and the top-level `README`, `INSTALL`, `CONTENTS`, `COPYRIGHT` and
`LOG.*` files. Of the archive's 412 files, 342 are imported. The 70
left out are build products, listed in `pristine.excluded`: the 68
`*.sav` save files, which `pdssasm` rebuilds from the `*.asm`, and the
two `*.dvi` files, which TeX builds from the `.tex`. `./pristine.sh
DIR` re-extracts the archive and checks it against `pristine.sha256`,
which holds the sums of the 342 imported files.

The import is two commits. "pristine import of the PDSS V2.52.20
emulator sources" brought in `emulator/` and `COPYRIGHT`, with the
emulator then at `src/` itself; a pure rename later moved it to
`src/emulator/`. "the rest of the distribution, pristine" brought in
everything else. Every later change is an ordinary commit on top, so
`git log -- src` and `git diff <import> -- src` (or
`./pristine.sh /tmp/o && diff -ru /tmp/o src`) record every change made
to ICOT's code. Only `src/emulator/` has been changed.

Build outputs never enter `src/`: `modern.sh T` copies `src/` to
`build-T/` (gitignored), builds `pdss` and `pdssasm` from
`src/emulator/` with objects in `build-T/emulator/`, and reassembles
the 52 library modules there from their `.asm` (the tarball's `make
reassm`).

### Retired: the reference port

Until 2026-11-25 the source was not kept here. `build.sh` unpacked the
tarball into `build/`, applied `port.diff` (683 lines) and added
`port_low.c`, a shim that placed heap, code and stack below 2 GB so
that PDSS's pointers-in-`int` held; it built x86_64 only (Rosetta on
Apple Silicon). That build recorded `golden/` (below). The in-tree
source supersedes it: the reference port's changes are in `src/`'s
history (commit "src/ starts from the reference port"), and with the
reference port's record sizes the modern source reproduces `golden/`
byte for byte on every target. `build.sh`, `port.diff` and
`port_low.c` were deleted; they remain in git history.

## What the modernisation changes

The 1992 source assumed a 32-bit machine (of either byte order) and K&R
C: a pointer fits in an `int` (a cell's value field holds
pointers; records hold pointers; native predicates are function
pointers stored in code), `long` is 32 bits, plain `char` is signed or
unsigned at the compiler's whim, and BSD system calls. The changes, in
commit order (`git log -- src/emulator`):

- **ANSI C.** K&R definitions to prototypes, `<varargs.h>` to
  `<stdarg.h>`, every function declared, every non-`void` function
  returns a value (324 had fallen off the end), `exit_pdss` is
  `_Noreturn`.
- **32-bit references, not pointers** (`port.h`, `arena.c`). A cell
  stays 8 bytes (`uint16 type, uint16 mrb, int32 value`), as in 1992.
  What used to be a pointer in a cell or a record is a `PREF`, a
  32-bit reference: 0 is NULL; 1..0x7FFFFFFF is a byte offset into the
  *arena*, one block from which every PDSS allocation comes (`malloc`
  and friends are `pdss_malloc` etc. in `pdss.h`); `0x80000000|i` is
  entry `i` of the *foreign table*, for the few addresses outside the
  arena (static tables, C functions of the native predicates, `argv`
  strings). `Ref(p)` makes a reference; `CellOf`, `CodeOf`, `GrecOf`,
  `SrecOf`, `PrecOf`, `MrecOf` read one back typed. `CodeOfFunction` /
  `FunctionOfCode` carry native predicates (a C function's address
  where a code address goes, as in 1992; converting function to object
  pointers is not ISO C but POSIX requires it, and these two macros
  are the only place it happens). The arena is
  `PDSS_ARENA_MB` megabytes (default 1024, untouched pages cost
  nothing on demand-paged systems).
- **No type punning, no unaligned access.** KL1-B code words are read
  and written with `memcpy` (`pdss_get32` etc. in `port.h`); floats
  live in an `int32_t` and are converted with `memcpy`; the
  assembler's and the reader's temporary areas align blocks for the
  structs they hold (they were 4-byte aligned, enough when a pointer
  was 4 bytes).
- **No undefined or implementation-defined integer behaviour.** Values
  that must wrap as 32-bit two's complement are computed unsigned and
  converted with `pdss_s32` (by arithmetic, not a cast); priorities,
  string descriptors, string elements and the packing of characters
  into string words (a byte of 0x80 or more shifted left 24) no longer
  shift into the sign bit of an `int`; integer literals at `INT32_MIN`
  no longer overflow. Byte order: strings are packed into words, and
  code words and save files read and written, by shifts and `memcpy`;
  no source views a cell's storage as bytes, and no `#if` selects on a
  machine or a byte order (checked by grep).
- **Save files** (`saveload.c`): big-endian bytes, as written by the
  1992 SPARC build, read and written by arithmetic on `uint32_t`; the
  magic numbers `0xA5C3`-`0xA5C9` and the format are unchanged. The
  1992 `.sav` files load (see "Targets").
- **Operating system** (`sysdep.h`, `sysdep.c`): everything beyond ISO
  C comes from POSIX through these two files only: BSD
  `re_comp`/`re_exec` over `<regex.h>`; `getwd` over `getcwd`; BSD
  `sigblock`/`sigsetmask` over `sigprocmask`; job-control stop;
  call-for-call wrappers of `getpid`, `pause`, `alarm`, `chdir`,
  `unlink`, `getpwnam`, `getrusage` and the directory calls; the names
  of the signals beyond ISO C's (`PDSS_SIGQUIT`, `PDSS_SIGTSTP`,
  `PDSS_SIGALRM`); the `PDSS_WORLD` test hook. `sysdep.h` includes no
  POSIX header but `<signal.h>`'s `sigset_t`, so a POSIX call anywhere
  else does not compile; `tools/posixcheck.py` (run by `test.sh`)
  checks that no other built source includes a non-ISO header or names
  a POSIX function. A port to a system without POSIX replaces
  `sysdep.h` and `sysdep.c`.
- **Bugs of the 1992 source fixed on the way**: `atom.c` modified a
  variable twice without a sequence point; `read_line`/`read_buffer`
  returned an uninitialised character after a GC restart or for a
  zero-length read; the tracer printed an `int` with `%s`; four
  `sprintf`s of a path (two of a start-up file name into 256 bytes,
  two of a directory entry, up to 1024 bytes on macOS, into 512) are
  bounded;
  `blt_code.c` passed an atom where a module entry was expected.

Not built and not modernised: `pdssinv.c` (an inverse assembler, not
in the Makefile) and `pdssmerge.c`. (`table.c` is a template that
`assemble.c`, `atom.c` and `instr.c` include, and is modernised with
them.) `native.c`'s `a.out` native-code loader is compiled out
and reports a link error, as the reference port did.

### Record sizes

The garbage collector's schedule depends on how many bytes the goal,
suspension, shoen and merger records take, and the KL1 compiler's
output depends on the collector's schedule (shown below by moving the
schedule with the heap size). So the record layout is visible in
output.
The default layout is 1992's: a reference is 4 bytes (goal record 104
bytes, suspension 24, shoen 76, merger 32). The reference port, built
LP64, had 8-byte pointer fields in records. `-DPDSS_LP64_RECORDS`
(`PREF_PAD` in `record.h` and `cell.h`) pads each reference field of a
record to 8 bytes and reproduces those sizes; the `-lp64rec` targets
use it. It is a layout check, not a separate program: the same code
runs, only the padding differs.

With the default layout, 140 of the 186 conformance transcripts are
byte-identical to the reference port's and 182 are identical with the
GC reports removed (`gcblind.py golden build-native/conf`). The other
four are KL1 compiler outputs whose register allocation moved with
the GC schedule: `c_compiler_outp`, `c_mpimos_cmd_code`,
`c_mpimos_shell`, `c_pimos_utl_multiply_keyed_bag`. Moving the
schedule another way, with the lp64rec build and a different heap size
(`PDSS_ARGS=-h250000 ./conformance.sh build-lp64rec`), changes the
same jobs' `.asm` sums to the default build's. In the reference
port, `c_compiler_outp` ends in heap exhaustion (`golden/`); with a
heap of 230,000 cells, or with the default layout, it compiles.

So there are two goldens:

- `golden/`, recorded from the reference port. Every `-lp64rec`
  target must match it byte for byte.
- `golden32/`, recorded from `build-native` (default layout,
  arm64, clang) on 2026-11-25, after the default layout gave
  byte-identical transcripts on all the targets listed below. Every
  default-layout target must match it byte for byte.

The default could be the other way round (pad records by default and
keep one golden); 1992's sizes were chosen because they are the
program's own and give a smaller heap footprint.

## Targets

`modern.sh T` builds one target; `test_slow.sh` builds them all and
runs the conformance jobs on each. On this host (macOS 27, Apple
Silicon), 2026-11-25:

| Target | Compiler, flags | Result |
|---|---|---|
| `native` | clang, arm64, `-O2` | matches `golden32/` |
| `gcc` | GCC 15.2 (Homebrew), arm64 | matches `golden32/` |
| `x86_64` | clang `-arch x86_64`, run under Rosetta | matches `golden32/` |
| `uchar`, `schar` | `-funsigned-char`, `-fsigned-char` | match `golden32/` |
| `asan` | `-fsanitize=address,undefined`, no recovery | matches `golden32/`, no report |
| each `-lp64rec` | the above with `-DPDSS_LP64_RECORDS` | match `golden/` |
| 1992 save files | `build-lp64rec` with the shipped `.sav` (big-endian, written on a SPARC) in place of the reassembled ones | load and run; transcripts match `golden/` with GC reports removed, except `c_compiler_outp` (GC-schedule dependent: the shipped files order atoms differently) |
| 32-bit | `arm-none-eabi-gcc` 14.3 (newlib, where `int32_t` is `long`), **compile only, not run**, `-Werror=format -Werror=incompatible-pointer-types` | every source but `sysdep.c` compiles; `sysdep.c` needs POSIX headers newlib lacks |

The 32-bit compile found real faults the 64-bit builds could not: 31
places passing an `int *` where an `int32_t *` is wanted (the float
built-ins, the assembler's and the reader's float scanners, the
window and file creation built-ins), 21
`int32_t` values printed with `%d` or `%x`, and a static prototype
that disagreed with its definition (`get4c` in `saveload.c`).

Save files are byte-identical across all default-layout targets (each
transcript carries the `.asm` and `.sav` sums, and `libsav` the sums of
all 52 reassembled libraries), so a `.sav` written by one target is
the file any other writes, and swapping them between targets is
implied. They do not depend on the record layout either:
`golden/libsav.out` (reference port) and `golden32/libsav.out` are
identical. 16 of the 52 reassembled libraries are
byte-identical to the shipped SPARC files; the other 36 differ only in
the order of their atom tables, and the shipped ones load (above).

AddressSanitizer inside the arena: under `-fsanitize=address`,
`arena.c` poisons each block's header, the slack between the size asked
for and the size class, and freed blocks (but the free-list link), so
ASan sees overflows and uses after free in PDSS's own memory. Checked
by a two-line program that writes one byte past a 10-byte block (ASan
reports it) and one that writes into a freed block (ASan reports
use-after-poison). Not covered: the KL1 heap and code areas are each
one large block, so an access within them is not checked.

The foreign table grows by one entry per distinct outside address and
never shrinks. `PDSS_FOREIGN_TRACE=1` prints each new entry. Measured:
9 entries for one 4-queens run, still 9 for three 8-queens runs with a
12,000-cell heap (6 collections); 14 for the KL1 compiler on
`queens.kl1`, 16 on `compiler/comp.kl1`. The count follows the static
tables and native predicates a run touches, not the work done.

Leads (not tested here; exact commands):

- Linux x86_64 or arm64, gcc or clang: `./test.sh && ./test_slow.sh`
  (the `x86_64` target is macOS-only; on Linux use `native`). Docker is
  installed on this host but its daemon was not running:
  `docker run --rm -v "$PWD":/w -w /w/pim/ref/pdss gcc:14 sh -c './test.sh'`.
- Big-endian: no big-endian toolchain with a C library is installed
  (`m68k-elf-gcc` has no libc; `qemu-system-ppc`/`-s390x` are
  installed without a guest). On a big-endian Linux (s390x, ppc64):
  `./test.sh && ./test_slow.sh`. The save-file code is byte-order free
  by construction and the 1992 SPARC files load on little-endian.
- 32-bit with a C library: `CC="gcc -m32" ./modern.sh native` on an
  x86_64 Linux with multilib, then `./conformance.sh build-native`
  against `golden32/`.
- Windows: replace `sysdep.c` (regex, signals, `getcwd`) and the
  direct POSIX uses listed above; the rest is ISO C.

Remaining compiler warnings with `-Wall -Wextra` (Apple clang 21,
arm64): 661 `-Wpointer-sign` (`CHAR` is `unsigned char` and is passed
to the `str*` functions; same representation), 8 `-Wsign-compare`
(unsigned loop bounds against `int` counts), and 18 unused variables,
parameters, a label and two functions. GCC 15 adds 13
`-Wimplicit-fallthrough` (the 1992 code's deliberate fall-throughs;
the two in `iosub.c` were read: the inner switch returns or continues
on every value it can take), 2 `-Wformat-truncation` (the bounded
path `snprintf`s, intended), and 6 `-Wmaybe-uninitialized`:

- `gc_dead.c` `func2`: used only when `argn != 0`, where it is set.
  False positive.
- `string.c` `get_print_image` `str`, `length`: set in each of the
  four cases of a switch on the argument's type; its caller
  `blt_b_get_print_image` checks the *dereferenced* type but passes
  the undereferenced cell, so a reference argument would reach the
  switch with none of its cases. Lead (a possible 1992 bug, not
  reached by any conformance job).
- `goal.c` `popup_suspension_stack` `srec`: in the `MHOOK` case, when
  the goal already hangs on the merger variable, no record is taken
  and the code after the switch writes `srec->other` with the previous
  iteration's record (or, on the first, an unset pointer). Lead
  (possible 1992 bug, not reached by any conformance job; left as it
  was).
- `goal.c` `move_suspension_queue` `tmp_grec` and `emulate.c`
  `new_grec`: set on the paths the callers take (a non-empty queue; a
  goal-creating instruction before use), not proved. Not changed.

## Conformance

`conformance.sh ROOT` runs 186 jobs from `jobs.txt` on a PDSS tree and
compares each normalised transcript with a golden directory
(`PDSS_GOLDEN`, default `golden/`): every one of the 80 programs in
PDSS's `test/` under `stat/1`, every `sample/` program (the deadlock
samples case by case), `emulator/sample.kl1`, the KL1 compiler on all
68 KL1 sources of `runtime/`, `mpimos/`, `compiler/`, `debug_utl/` and
`pimos_utl/`, and the reassembled libraries' `.sav` sums (`libsav`). A
transcript includes the console output, the reduction counts, the GC
reports (only the msec fields are removed), the emulator's exit
status, and the sha256 of the `.asm` and `.sav` the job wrote. The
whole run takes about 20 s. `PDSS_JOBS` (a regular expression) runs a
subset; `PDSS_ARGS` adds emulator arguments, e.g. a heap size.

`check_headers.py` compares each `test/` program's output with its own
header comment, which is ICOT's expected output: 73 of 80 match, and
the 7 that do not are listed with their causes in
`headers_expected.txt` (two stale headers, three `pow(0.0,0.0)` cases
where IEEE libm returns 1.0, a substring bound, and
`code_to_predicate` on a built-in module).

Building the baseline found three port bugs: `float.c` called `atof`
undeclared; `alloc_cells_to_free_list` compared a pointer difference
with an `unsigned`, which overran the heap under LP64; and `blt_code.c`
passed a module-name atom to `find_predicate` (a bug in the 1992
source).

## Fault injections

Each injected into `src/emulator/` from a backup copy, `./test.sh` run,
and reverted from the backup (2026-11-25). Observed:

- **Truncated pointer** (`port.h` `pdss_ref` returns an outside address
  cut to 32 bits instead of a foreign-table entry, what a naive 64-bit
  port does): the libraries still reassemble; the KL1 compiler dies
  with a bus error; `pdss: FAIL (KL1 compile)`.
- **Wrong tag shift** (`cell.h` `StringTypeof` shifts the string
  descriptor by 23 instead of 24): `pdss: FAIL (KL1 compile)`.
- **Dropped GC root** (`gc.c` no longer calls `gc_io_table`): queens
  and its 12,000-cell-heap run still pass; conformance fails 46 of 186
  jobs, the same set as the 46 whose `golden32/` transcript has a GC
  report, on the live-cell counts of the GC report; with the GC reports removed (`gcblind.py`) all 186 match.
  Only the byte-exact transcript catches it, which is why the GC
  reports stay in.

The 2026-11-20 injections into the reference port (`RADDR` back to
`long`; `=\=` computing `<`) and the baseline's (`atof` undeclared:
56 jobs fail; the `HeapRest` comparison: 3) are in git history with
the port they were made on.

## What it is for

PDSS is a sibling dialect, not PIM/m's: 73 of the 197 instructions
PIMOS uses have the same name and register count, 18 (29% of uses) are
split differently, 50 are absent (`asm/namemap.py`). It cannot load the
PIMOS `.sav` files. Its use is as an executable description of the
KL1-B runtime (suspension, goal scheduling, MRB, shoen, exceptions,
the built-ins) to read and to experiment against while the PIM/m
runtime is built: roadmap decision 3 in `docs/pimos_roadmap.md`.

## Licence

PDSS is ICOT Free Software. `src/COPYRIGHT` (Japanese: `src/COPYRIGHT.J`)
is the package's "TERMS AND CONDITIONS FOR USE OF ICOT FREE SOFTWARE".
Section 2 allows free use, modification, copying and distribution, on
the condition in section 3 that its NO WARRANTY text goes with any
distribution. `src/` is such a distribution, and the terms come with it
unedited. The IFS archive's own statement of the terms is cited in
`docs/nonlocal/IFS_MANIFEST.md`, "Terms of use". The changes made here
fall under the same terms.
