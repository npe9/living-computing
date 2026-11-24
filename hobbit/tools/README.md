# Plan 9's Hobbit toolchain (1st Edition)

Plan 9 from Bell Labs gave each machine it supported a single-character
prefix; for the AT&T Hobbit it was `z`. This directory vendors the
`z` toolchain from the **1st Edition** source tree — the last release
that contains it — as the second oracle for this machine, beside the
printed tables of the January 1993 Programmer's Reference Manual.

It is Bell Labs' own toolchain for a Bell Labs chip, written at the time
of the chip: the archive's file dates are 3 January 1993, the same month
as the manual. That makes it the closest thing to hand that states what
the machine encodes, in code rather than in prose.

`qemu1e/` is separate from the vendored toolchain: scripts (no
binaries) that boot the release's own 386 kernels in QEMU as the 1e file
server the Hobbit terminal boots from; see
[`../docs/qemu_1e_server.md`](../docs/qemu_1e_server.md).

## Provenance

| item | value |
|---|---|
| archive | `https://9p.io/plan9/download/history/plan9-1e.tar.bz2` |
| archive sha256 | `8718e279aa35b10a9391f330976d31c177bad00de40e7f0f67232ffa54fb7d77` |
| extracted | `plan9-1e/sys/src/cmd/{za,zc,zl}`, `plan9-1e/sys/src/libmach/z.c`, `plan9-1e/sys/src/libmach/zobj.c`, `plan9-1e/license` |
| licence | MIT, Plan 9 Foundation (2021 re-release); see [`plan9-1e/license`](plan9-1e/license) |

Files are verbatim; nothing under `plan9-1e/` is edited. `SHA256SUMS`
in this directory pins them:

```
shasum -a 256 -c SHA256SUMS
```

The 2nd Edition dropped the port: `plan9-2e.tar.bz2`
(sha256 `0bb3c1446deb79b179f73886eb2419ecfac9f9964040683e3d5731f074bc2ce6`)
contains no `za`, `zc`, `zl`, or `hobbit` path. The `z` prefix was
recycled much later for RISC-V, so a modern `zc` is not this compiler.

## Inventory

| path | role |
|---|---|
| `sys/src/cmd/za/` | assembler front end: `a.y` (yacc grammar for every operand form), `lex.c` (driver; sets `thechar = 'z'`, `thestring = "hobbit"`; includes the shared `../cc/lexbody` and `../cc/macbody`), `a.h`, `l.s` (machine constants: `BY2PG`, `KZERO`, `VBADDR`, stack offsets), `mkfile` |
| `sys/src/cmd/zc/` | C compiler: `z.out.h` (opcode enum `AADD`…`AXOR3`, data types `D_*`, widths `W_*`), `enam.c` (the `anames[]` mnemonic strings), `txt.c`, `cgen.c`, `sgen.c`, `swt.c`, `list.c` |
| `sys/src/cmd/zl/` | linker: `optab.c` (per-mnemonic type, `genop` byte, `decod` string), `asm.c` (the encoder, below), `span.c` (instruction sizes and `anddec`), `pass.c`, `obj.c`, `list.c`, `l.h` |
| `sys/src/libmach/z.c`, `zobj.c` | `z.c` is 67 lines of register offsets and the `Mach` entry only (no z disassembler exists in 1e); `zobj.c` is the object-file support, and its header reads are little-endian (`Bgetc(bp)<<8` etc.) |

## What the encoder says

`zl/asm.c` is the part worth reading first: in this release it is the
only place a Hobbit instruction is turned into parcels. `za/a.y`,
`zc/txt.c` and `zc/swt.c` call `outcode()`, and **no file in the 1st
Edition tree defines it** (checked by grepping all of
`sys/src/cmd`; `2a`, `6a`, `8a`, `ka`, `va` and `za` are all in the same
state, so the gap belongs to the release, not to the Hobbit port). The
linker, by contrast, spells the encoding out:

* `andasm` emits a **five-parcel** instruction as
  `0xc000 | genop<<8 | smode<<4 | dmode`, followed by 32-bit source and
  destination — the manual's `11` length prefix and opcode[5:0]
  (printed pp. 1-24 to 1-25, Table 1-20).
* The same function emits a **three-parcel** instruction as
  `0x8000 | genop<<8 | smode<<4 | dmode`, followed by 16-bit source and
  destination — the manual's `10` prefix and Table 1-18 (p. 1-23).
* The **one-parcel** forms are selected per operand class by the
  `decod` strings in `optab.c`, e.g. `"cs14->ns14->"` for the dyadic
  immediate/stack form: `c`/`n`/`s` are the 5-bit operand classes, `14`
  is the five-bit opcode split 1+4 around the length bit, `>` means the
  operand is scaled by four while `-` leaves it unscaled, and the
  source lands in bits 9:5 and the destination in bits 4:0 — the field
  layout of Table 1-15 (p. 1-22) and of its "five-bit offset values are
  multiplied by four" rule.
* `and10asm` emits the stack and monadic two-byte forms; `andpcasm` the
  PC-relative `CALL`/`JMP` forms and the five-parcel fallback.

## Cross-check against the manual

[`check_optab.py`](check_optab.py) compares `zl/optab.c` with two
transcribed manual tables and is the gate that keeps this directory
honest:

```
python3 hobbit/tools/check_optab.py
```

Observed on 2026-11-19, first run:

* **check 1** — the `genop` byte of every mnemonic in Tables 1-18/1-20
  equals the manual's opcode[5:0]: **35 checked, 0 mismatches**
  (ADD `0x23`, ADD3 `0x33`, MOV `0x06`, CMPEQ `0x1f`, DQM `0x07`, …).
* **check 3** — the one-parcel opcodes Plan 9 folds to, parsed out of the
  `decod` strings exactly as `asm.c` parses them, against the Table 1-15
  entries on p. 1-22: **10 mnemonics checked, 0 mismatches** (ADD, ADD3,
  AND, AND3, CMPEQ, CMPGT, MOV, MOVA, SHL3, SHR3 — including `MOV.WS`
  `0x0a` and `ADD3.WS` `0x0d`, which are easy to miss).
* **check 2** — Table 3-1's 46 mnemonic entries expand to 60 spellings,
  and **45 of 46 entries** have a Plan 9 mnemonic spelled as the manual
  spells it. The missing one is `CLRE` ("clear PSW enter guard bit",
  manual p. 1-22, a niladic): the string `clre` appears nowhere in the
  vendored tree. That is a statement about Plan 9's coverage, not about
  the chip, and the script pins the gap: any other absence fails.
* 50 `optab.c` entries lie outside the Tables 1-18/1-20 grid. Ten of them
  are the folded one-parcel forms that check 3 covers; the rest are
  unchecked: the Table 1-19 monadics (`CALL`, `CATCH`, `ENTER`, `RETURN`,
  `POPN`, `LDRAA`, `KCALL`, `KRET`, `FLUSH*`, the four conditional
  `JMP`s), the Table 1-17 niladics (`CPU`, `KRET`, `NOP`, `CRET`,
  `TESTV`, `TESTC`), and 26 floating-point mnemonics (`FADD`, `FMUL3`,
  `FSQRT`, …) that the 92010 manual marks `unimp` and traps — Plan 9
  kept the names from the architecture's floating-point definition.

## Limits

* **Not buildable from this release.** With `outcode` absent, `za`
  cannot be linked even with the 1st Edition tree, `mk`, `yacc` and Plan
  9 libc; the two checked-in `cc` archives (`cc.a2`, `cc.a8`) hold only
  the shared compiler objects (`y.tab`, `lex`, `mpatof`, `mac`, `dcl`,
  `com`, `con`, `sub`, `compat`), so neither supplies a backend. This
  directory is a reference, not a tool.
* **Not AT&T Microelectronics' toolchain.** The manual's printed
  assembler syntax (`MUL $0x7F,R4:B`, `MOV R4:B, R8:L`,
  `MOV $new, %SHAD`, the control-register `CPU` escape) is the syntax to
  implement. Plan 9's spelling of an
  instruction is evidence about encoding, not about AT&T's assembler,
  and its absence of `CLRE` is not evidence that the chip lacks it.

AT&T's own assembler and any surviving Hobbit object file — the BeOS DR4
disk images preserved by the BeBox community are the likeliest source —
therefore remain the top acquisition target. See
[`../docs/README.md`](../docs/README.md).

## The 1st Edition's own Hobbit binaries and sources (added 2026-11-19)

The same archive, `plan9-1e.tar.bz2`, also carries the *shipped* result
of the port, which is what the proof of concept runs
([`../docs/plan9_port.md`](../docs/plan9_port.md)):

| path | what |
|---|---|
| `plan9-1e/hobbit/bin/echo`, `cat`, `rc`, `za`, `zl` | prebuilt `z`-architecture executables, dated 3 January 1993 — Bell Labs' own compiled user code for this chip, including the assembler and linker |
| `plan9-1e/sys/src/9/hobbit/` | the Hobbit kernel port (41 files): `raml.s`/`roml.s` reset and vectors (`_vector0` is the syscall entry, `_vectors+0x00 = $syscall`), `trap.c`, `mmu.c`, `screen.c`, `cpu`, … |
| `plan9-1e/sys/src/libc/hobbit/` | the Hobbit libc assembly (19 files), including `main9.s` (`_main`: `argc+0(FP)`, `argv+4(FP)`, `CALL main`, `exits("main")`) |
| `plan9-1e/sys/include/a.out.h` | `struct Exec` and `Z_MAGIC = _MAGIC(10) = 0x197` |

Added 2026-11-23 for A3's library step, from the same archive (sha256
re-verified that day) and pinned in `SHA256SUMS`:
`plan9-1e/hobbit/bin/rl` (`$RL` in `/hobbit/mkfile`: writes an archive's
`__.SYMDEF`, then forks `ar` to insert it), and the sources the runner and
`tools/p9kbuild.py` cite for `ar`, `rl` and the `init.h` text step:
`plan9-1e/sys/src/cmd/ar.c`, `rl.c`, `xd.c`.

The kernel link (A3): `tools/p9kgen.py` makes the generated inputs,
`tools/p9kbuild.py kernel --kgen K` builds `libram.a`, and
`tools/p9kbuild.py link --kgen K --check` runs the shipped `zl` to make
`9term` (351 M instructions on the reference model, sha256 `002880c0...`);
`tools/p9kbuild.py all --build DIR` runs the three in one fresh directory.
`tools/p9kcmp.py IMAGE` compares any `-H1` image with the shipped
`plan9-1e/hobbit/s9term`, failing only on what must agree
(`docs/s9term.md`).  `plan9-1e/hobbit/bin/size` and `sys/src/cmd/size.c`
(2026-11-23) are the `9term` rule's last command.

Added 2026-11-24 for the boot ROM (`../docs/boot_rom.md`), from the same
archive (sha256 re-verified that day) and pinned in `SHA256SUMS`:
`plan9-1e/hobbit/lib/libmach.a` (the ROM's boot program, `romboot.c`,
includes `<mach.h>`, whose `#pragma lib "libmach.a"` makes `zl` link it
for `crackhdr`) and `plan9-1e/sys/src/libmach/executable.c` (what
`crackhdr` returns for a `-H1` image, which `mkrom.c` depends on).
`tools/p9symdef.py ARCHIVE` accounts for every byte of an archive's
`__.SYMDEF` past a name's NUL: libmach's `readar()` replayed, and the
stack bytes `/mips/bin/rl`'s frames leave (the shipped tables were
written by the MIPS `rl`, not the Hobbit one; `docs/plan9_syscalls.md`).

`hobbit/bin/echo` measures: `magic 0x197`, text 0x2258 loaded at 0x1000,
data 0x374, bss 0x354, entry 0x2ad0, `syms` 0x3db0 — a 1st Edition
`a.out`, so the loader needed for the port is a header parse and three
copies.

This also corrects the first bullet under **Limits**: the *sources* of
`za` cannot be built in this release (`outcode` is missing), but the
release ships working `za` and `zl` **executables**, and they are the
machine's encoder oracle as binaries as well as in source.

## Building the linker on this host (Inferno64)

`python3 tools/build_zl_inferno.py` builds the 1st Edition `zl` from
`sources with the owner's Inferno64 tree (its `lib9`/`libbio` headers and
libraries, built by `makemk.sh`) — **not** plan9port, whose renamed libc
(`p9malloc`, new `Fmt`) does not fit 1993 code.  Measured 2026-11-19:

```
$ python3 tools/build_zl_inferno.py
/tmp/zl-inferno/zl/zl
$ /tmp/zl-inferno/zl/zl
??none??: usage: zl [-options] objects
```

The script copies the vendored sources into a build directory and
patches the copies (never the repository): `<u.h>`/`<libc.h>` shims to
Inferno's `<lib9.h>`; `Ieee` taken from `zc/z.out.h`; BSD `ar_hdr`
members; the linker's own allocator renamed past Inferno's `k*` macros;
`strconv`, `doprint`, `argv0` and a `cputime` supplied; `fmtinstall`
hooks cast to Inferno's `Fmt*`.  Every edit is listed in the script.

Next: hand-assemble a `z` object and link it with this `zl`, so the
executable the model runs is produced by Bell Labs' own linker.
