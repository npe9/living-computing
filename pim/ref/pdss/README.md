# PDSS on a modern machine

PDSS V2.52.20 (ICOT, 1992) is a complete KL1-B abstract machine in C:
interpreter, scheduler, suspension, copying and MRB garbage collection,
shoen, exceptions, built-ins, with its own KL1 compiler (written in
KL1) and Micro PIMOS. It is the nearest surviving *source* to the
firmware that ran PIMOS (`docs/pimos_boot_requirements.md` §0.1), and
this directory makes it run.

    ./test.sh        # build, then compile and run a KL1 program on it

The source is not copied here. `build.sh` unpacks
`docs/nonlocal/pdss.tar.Z` into `build/` (untracked), applies
`port.diff`, adds `port_low.c`, compiles, and reassembles the KL1
libraries from their `.asm` files.

## The source in tree: `src/`

`src/` is the PDSS V2.52.20 distribution, `docs/nonlocal/pdss.tar.Z`
(SHA-256 `3da79c34abf3bcd5f30d0b178b869ee25b4cc544de82713552721da94888c13c`),
imported unedited with the tarball's own layout: `emulator/` (the C
program), `runtime/`, `mpimos/`, `compiler/`, `debug_utl/`,
`pimos_utl/` (KL1 sources and their `.asm`), `compiler_pl/` (the
Prolog-hosted bootstrap compiler), `test/`, `sample/`, `macro/`,
`emacs/`, `doc.e/`, `doc.j/`, and the top-level `README`, `INSTALL`,
`CONTENTS`, `COPYRIGHT` and `LOG.*` files. Of the archive's 412 files,
342 are imported. The 70 left out are build products, listed in
`pristine.excluded`: the 68 `*.sav` save files, which `pdssasm` rebuilds
from the `*.asm`, and the two `*.dvi` files, which TeX builds from the
`.tex`. `./pristine.sh DIR` re-extracts the archive and checks it
against `pristine.sha256`, which holds the sums of the 342 imported
files.

The import is two commits. "pristine import of the PDSS V2.52.20
emulator sources" brought in `emulator/` and `COPYRIGHT`, with the
emulator then at `src/` itself; a pure rename later moved it to
`src/emulator/`. "the rest of the distribution, pristine" brought in
everything else. Every later change is an ordinary commit on top, so
`git log -- src` and `git diff <import> -- src` (or
`./pristine.sh /tmp/o && diff -ru /tmp/o src`) record every change made
to ICOT's code.

## What the port changes

PDSS assumes a 32-bit machine in three ways. The port keeps the source
32-bit-minded and fixes the environment, so the diff stays small (683
lines over 27 files, most of it mechanical):

| Assumption | Where | What the port does |
|---|---|---|
| A pointer fits in an `int` (`cell.h`: `int value` holds pointers; K&R functions returning pointers are implicitly `int`) | everywhere | Nothing in the source. The program is built x86_64, linked non-PIE at 1 MB with a 64 KB page zero, and `port_low.c` gives it a heap (`malloc` family) and a stack below 2 GB, so every pointer PDSS can see does fit. |
| `long` is 32 bits | `klb.h` code-word macros (`GetInt`, `GetRelAddr`, `RADDR`, ...) | `long` becomes `int` there. This was the one real crash (the assembler walked a label chain 8 bytes at a time). |
| K&R C as 1992 compilers took it | 22 files | forward declarations for `static` functions used before their definition; `<varargs.h>` in `goal.c`/`exception.c` replaced by eight fixed pointer arguments; `main`'s `CHAR **argv`; `static FILE *file = stdout`; `a.out.h` native-code loading compiled out; BSD `re_comp`/`re_exec` supplied over POSIX regex; `config.h` paths made relative. |

Consequences:

- **macOS on Apple Silicon needs Rosetta.** arm64 does not allow the
  small page zero. `build.sh` exits 77 and `test.sh` reports SKIP where
  x86_64 cannot run.
- **Linux is untested.** The recipe is `-m32`, which needs none of the
  low-memory shim; it is written in `build.sh` and has never been run.
- **This is not a 64-bit port.** A real one widens the cell and removes
  the implicit-`int` pointer returns. It is not needed to use PDSS as a
  reference, and this build is the oracle such a port would be checked
  against.

## What has been verified

`test.sh`, from a clean unpack:

1. `pdssasm` reassembles all 52 library modules (runtime 5, Micro PIMOS
   35, compiler 12). The shipped `.sav` files were assembled on a SPARC
   and are not used. A reassembled file is the same size as the shipped
   one and differs in the order of its atom table; they have not been
   compared beyond that.
2. PDSS boots Micro PIMOS to its `| ?-` prompt.
3. PDSS's KL1 compiler, running on the port, compiles `queens.kl1`
   (the tape's `sample/queen.kl1` plus counting and printing
   predicates).
4. The result, loaded and run, prints the two 4-queens solutions and
   the counts 2, 4 and 92 for 4, 6 and 8 queens (38,979 reductions for
   8).
5. 8 queens twice with a 12,000-cell heap: four copying collections,
   same answers.

Observed fault injections (2026-11-20; `PDSS_INJECT` in `build.sh`):

- `RADDR` back to `long`: `pdssasm` fails on the first library module;
  build FAIL.
- integer `=\=` computing `<` (`COMPARE_INT(!=)` to `COMPARE_INT(<)` in
  `emulate.c`): the libraries still build, the queens run prints a GC
  report instead of solutions and dies with a bus error; FAIL. (The
  crash under a runaway computation is itself unexplained.)
- Both restored with `PDSS_REBUILD=1`; PASS.

Not verified: PDSS's own `test/` directory (551 KB of KL1 tests) has
not been run; the tracer, the Emacs window interface, file and timer
devices, floating point, and MRB-GC specifically are unexercised.

## Conformance baseline (2026-11-25)

`conformance.sh ROOT` runs 185 jobs from `jobs.txt` on a PDSS tree and
compares each normalised transcript with `golden/` (plus the
reassembled libraries' `.sav` sums, `golden/libsav.out`): every one of
the 80 programs in PDSS's `test/` under `stat/1`, every `sample/`
program (the deadlock samples case by case), `emulator/sample.kl1`,
and the KL1 compiler on all 68 KL1 sources of `runtime/`, `mpimos/`,
`compiler/`, `debug_utl/` and `pimos_utl/`. A transcript includes the
console output, the reduction counts, the GC reports (only the msec
fields are removed), the emulator's exit status, and the sha256 of the
`.asm` and `.sav` the job wrote. Two recordings are byte-identical.
The whole run takes about 20 s.

`check_headers.py` compares each `test/` program's output with its own
header comment, which is ICOT's expected output: 73 of 80 match, and
the 7 that do not are listed with their causes in
`headers_expected.txt` (two stale headers, three `pow(0.0,0.0)` cases
where IEEE libm returns 1.0, a substring bound, and
`code_to_predicate` on a built-in module).

Building the baseline found three port bugs, now fixed in `port.diff`:

- `float.c` called `atof` undeclared, so it returned an `int`: every
  float constant was garbage and 13 float tests printed `*`.
- `alloc_cells_to_free_list` (`memory.c`) compared `HeapRest()`, a
  pointer difference that was 32-bit `int` on the original, with an
  `unsigned`. Under LP64 the comparison is signed, and past the GC
  warning line the free list overran the heap: segmentation faults
  compiling `compiler/outp.kl1`, `debug_utl/mpimos_xref.kl1` and others,
  depending on file-name length.
- `blt_code.c` passed a module-name atom to `find_predicate`, which
  takes a module entry, and dereferenced address 1 (`test/b_code_e.kl1`).
  This is a bug in the 1992 source.

Observed injections: removing the `atof` fix fails 56 jobs; removing
the `HeapRest` fix fails 3 (`c_mpimos_file`, `c_compiler_blt`,
`c_compiler_outp`).

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
