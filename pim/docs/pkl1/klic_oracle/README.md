# The KLIC 2.002 answer oracle for R8 (OURS)

This is how the answers of APPS `pkl1_fact`, `pkl1_nrev`, `pkl1_qsort`
and `pkl1_kkqueen` (`ref/pimm/lockstep_shell.py`) were checked. It is
our own build of held source, made in scratch on 2026-11-25 and not
kept. It is not in the suite. KLIC 2.002 is ICOT Free Software: its
terms are the same as pkl1's (`../COPYRIGHT`, NO WARRANTY).

## Build

1. Extract `docs/nonlocal/klic-2.002.tgz` (held, not in git) into an
   empty directory.
2. Do not run `Configure`: it needs a `libc.a` to scan, which macOS
   does not have. Write its three outputs by hand instead, from its
   templates (Configure lines 864-1063):
   - `config.h` here becomes `include/klic/config.h`. It defines
     `#undef ASYNCIO` and `#undef USEULIMIT`.
   - `Makefile.head` here, followed by the tarball's `Makefile.tail`,
     becomes `Makefile`. It sets `KL1CMP = false`, so the shipped C
     translation of the compiler is used, and `PARALLEL = 0`.
   - In both files, `PREFIXDIR` stands for the build directory.
3. Apply `klic-2.002-clang.diff` with `patch -p1`. It changes two
   things:
   - the gcc-only idiom "a `volatile` function does not return",
     which clang rejects (`NoReturn`);
   - an early `extern` of an array of a struct type that is not yet
     complete (`options.h`).
4. Run `make all`, then `make install`.

The result is a native arm64 build. Its 21 bundled test programs each
match their `.out.cmp` when each is run in its own directory.

## Goals

- Modules `fact`, `nrev` and `qsort` are used exactly as in
  `../fact.kl1`, `../nrev.kl1` and `../qsort.kl1`, with their `top`
  modules dropped.
- From `../kkqueen.kl1`, the module line becomes
  `:- module kkqueen.`, and `top/0` is dropped.
- `main.kl1` and `main_go9.kl1` are the entry points. They print with
  `io:outstream`, as KLIC's own `test/fact.kl1` does.
- `go(9)` was a separate run.

Run them like this:

    klic -o oracle main.kl1 fact.kl1 nrev.kl1 qsort.kl1 kkqueen.kl1 && ./oracle
    klic -o o9 main_go9.kl1 kkqueen.kl1 && ./o9

Their output is `oracle.out` and `oracle_go9.out`, in this order:

- fact(10)
- fact(12)
- nrev of [1..8]
- qsort of the ten
- go(6)
- go(8)
- nrev's own `make_list(30)` and its reverse
- go(9), the separate run

The build is 64-bit, so an integer has 60 bits. On a 32-bit host of
the period an integer had 28 bits, and fact(12) would not fit.

## R8's second half (2026-11-26)

The same build, made again in scratch from the same recipe, and run on
`tak`, `cd`, `lips` and `life`, and on the samples' own larger inputs
(APPS `pkl1_tak`, `pkl1_cd`, `pkl1_lips`, `pkl1_life`, `pkl1_nrev30`,
`pkl1_qsort50`).

This time KLIC is given exactly the text the FEP serves PIMOS: each
`NAME_r8.kl1` is `docs/pkl1/NAME.kl1` with `longrun_ipl.PKL1_ADAPT`'s
edits made (`longrun_ipl.adapted`), `:- public` lines and all. KLIC
2.002 accepts the `:- public` lines and life's `display_console` guard,
so there is no separate KLIC edit: the oracle and PIMOS compile the
same source. (The first half's `main.kl1` used its own trimmed modules;
their answers are the same.)

KLIC keeps a predicate database (`klic.db`) in the directory it builds
in, so two programs with a module of the same name (`top` is in lips,
life and kkqueen) must be built in directories of their own:

    klic -o o main_life.kl1 life_r8.kl1 && ./o
    klic -o o main_lips.kl1 lips_r8.kl1 && ./o
    klic -o o main_cd.kl1 cd_r8.kl1 && ./o
    klic -o o main_r8b.kl1 tak_r8.kl1 nrev_r8.kl1 qsort_r8.kl1 && ./o

Their output, with each exit status, is `oracle_r8b.out`:

- life(5,6,6,2,2) and its count N = 19
- lips: make_list(30), repeat(3) of nrev on it, then its nrev
- cd: `done`, exit 0. count_down binds nothing, so the line only shows
  that the program ran to its end. The control is count_down(-1),
  which no clause takes: KLIC's runtime stops with a fatal error and
  exit 255 (it tries to open its tracer on /dev/tty).
- tak(9,6,3) 6 and tak(18,12,6) 7
- nrev of nrev.kl1's own 30 ([30..1] reversed)
- qsort of qsort.kl1's own list50
