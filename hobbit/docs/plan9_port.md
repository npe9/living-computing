# Proof of concept: a Plan 9 port

**Direction (owner, 2026-11-19): the proof of concept for this machine is
a Plan 9 port.** Not a smoke test of parcels: Plan 9's own Hobbit
binaries, produced by Bell Labs' own `z` toolchain in January 1993,
running on the model.

## What the 1st Edition actually contains

`plan9-1e.tar.bz2` (sha256 `8718e279aa35b10a9391f330976d31c177bad00de40e7f0f67232ffa54fb7d77`,
downloaded whole and verified) is the last release with the Hobbit port.
Three parts matter, and only one of them is vendored in `tools/`:

| part | path in the archive | what it is |
|---|---|---|
| shipped Hobbit binaries | `hobbit/bin/` | a complete executable tree for the `z` architecture: `za`, `zc`, `zl`, `rc`, `echo`, `cat`, `ls`, `sam`, `ar`, … dated 3 Jan 1993 |
| Hobbit kernel sources | `sys/src/9/hobbit/` (41 files) | `raml.s`/`roml.s` (reset, vectors, `_vector0` = the syscall entry, `_vectors+0x00 = $syscall`), `trap.c`, `mmu.c`, `screen.c`, `cpu`, … |
| Hobbit libc sources | `sys/src/libc/hobbit/` (19 files) | `main9.s` (`_main`: `argc+0(FP)`, `argv+4(FP)`, `CALL main`, `exits("main")`), `memmove.s`, `setjmp.s`, string routines |
| toolchain sources | `sys/src/cmd/{za,zc,zl}` | the `z` assembler, compiler back end and linker; `zl/asm.c` is the encoder, and **no file in 1e defines `outcode`** (see `tools/README.md`) |
| executable header | `sys/include/a.out.h` | `struct Exec {magic, text, data, bss, syms, entry, spsz, pcsz}`, `Z_MAGIC = _MAGIC(10) = 0x197` |

So the port exists twice over: as binaries that were built at the time,
and as the kernel and library sources that produced them. The proof of
concept uses the binaries as the oracle and the sources as the rules.

Measured example (`hobbit/bin/echo`, 27,642 bytes):

```text
magic 00000197  text 00002258  data 00000374  bss 00000354
syms  00003db0  entry 00002ad0  spsz 00000000  pcsz 0000085e
```

Text is 8,792 bytes, data 880, bss 852 — a classic 1st Edition `a.out`.

The symbol table fixes the load rule: `sys/src/9/hobbit/mem.h` has
`UTZERO = UZERO+0x1000`, symbol `main` is **0x1020**, `etext` **0x3278**
= 0x1020 + 0x2258, `bdata` **0x4000**, `edata` **0x4374**, and
`_main` **0x2ad0** = the header's `entry`. So the loader maps the whole
file — 32-byte `Exec` header included — at 0x1000, which puts the text
section at 0x1020 and data at 0x4000.

**The load rule is now proof, not inference.** `/sys/src/9/port/sysproc.c`
(1e) checks `entry >= UTZERO+sizeof(Exec) && entry < UTZERO+sizeof(Exec)+text`,
attaches the file at `UTZERO` (`attachimage(SG_TEXT|SG_RONLY, tc, UTZERO, …)`,
so file offset 0 is 0x1000 and the 32-byte `Exec` sits at 0x1000…0x101f),
and records `flen = sizeof(Exec)+text`. So text starts at **0x1020**,
which is exactly the symbol `main` and exactly the `etext` arithmetic.
Every shipped binary's entry falls inside that window (`echo` 0x2ad0,
`cat` 0x12bc, `rc` 0xb9c6, `za` 0x7282, `zl` 0x995c).

**The text layout is settled, and `zl` is its oracle.** The text section
is a sequence of **32-bit words stored little-endian**, and within each
word the **high half is the earlier parcel**. Two facts pin it down:

* `zl/asm.c`'s `SPUT` writes every parcel big-endian into a buffer
  (`asm.c:3`), and while `swizflag` is set — text only, `asm.c:52` to
  `asm.c:141` — `cflush` reverses every four-byte group (`asm.c:255`–270).
  That byte reversal is exactly what turns the stream into little-endian
  words; `datblk` writes data without it.
* `zl` states the addresses itself: `asmb` starts at `pc = INITTEXT` and
  counts parcels, and its `-a` listing prints each instruction's pc with
  the words it emits. Linking `libc.a`'s `main9.z` (see
  `tools/build_zl_inferno.py --link-main9`) lists `0: 0802` (RETURN) at
  0x1020 and `2: 0bfc` (ENTER) at 0x1022 for the two functions the image
  starts with, and the file's bytes at 0x1020 are `fc 0b 02 08`: the
  little-endian word 0x08020bfc, whose high half 0x0802 sits at the even
  address 0x1020.

So the parcels of the text word at address A are `w >> 16` at A and
`w & 0xffff` at A+2, with `w = bytes[A..A+3]` read little-endian.
Reading the file instead as two little-endian 16-bit halves in file
order swaps every adjacent pair — the misreading that produced the
"two-byte hole" recorded below.

`cat`'s `_main` (0x12bc) then reads, in address order:

```text
0x12bc  0bfc             ENTER R-16           ; inserted by zl, not in main9.s
0x12be  86dc 0000 3004   MOV   R0, _clock     ; _clock = 0x3004
0x12c4  60a1             MOV   argc+0(FP), R4
0x12c6  60c2             MOV   argv+4(FP), R8
0x12c8  06ac             CALL  0x1020 = main
0x12ca  0805             CATCH R16            ; inserted by zl, not in main9.s
0x12cc  c6fd 0000 12da   MOV   $_exits, R4
        0000 0004
```

The `0x0000` that used to look like a hole is the **second parcel of the
three-parcel MOV**: `andasm` emits `prefix, lf, lt` (`asm.c`, the
`0x8000 | ...` case), the prefix is 0x86dc and `lf` is 0x0000, the stack
offset of `R0`. It is not padding, not an instruction, and not
uninitialised output.

Two instructions in that sequence are not in `main9.s`:

* `ENTER R-16` is inserted by `zl/pass.c`'s `follow()` for `TEXT
  _main(SB), 1, $12` (case ATEXT, `pass.c:144`–157: `q->as = AENTER`
  when `autosize > 0`, where `~15`-rounded `$12` is 16).
* `CATCH R16` is inserted after a `CALL` by the same function (case
  ACALL, `pass.c:118`–140: `q->as = ACATCH`, `q->to.offset = c`) when
  the callee's declared stack does not cover the code that follows. It
  is in the shipped binaries; a minimal link whose program declares `$0`
  gets none, and giving that program `$2048` makes `zl` emit `0805`
  there. So the CATCH is a property of the caller's and callee's frames,
  not of `_main`.

The call targets are the proof that the parcel order is right:
`CALL main` lands exactly on the `main` symbol in all five shipped
binaries, and the `CALL exits` that follows lands on `exits`. Under the
old swapped reading the same bytes put the first call at 0x1022 — two
bytes into `main`, not at a symbol.

**There are no registers to decode.** The machine is memory-to-memory
(PRM §1.4, printed p. 1-4: "general purpose registers are eliminated";
the stack cache "appears as normal memory"), and the 5-bit `R` fields of
Tables 1-15/1-18 are **stack offsets scaled by 4** (p. 1-22). That is
why `0x60c2` (src 6, dst 2) is `MOV argv+4(FP), R8` — 2x4 = R8 — and
`0x60a1` (src 5, dst 1) is `MOV argc+0(FP), R4`. `zl` encodes a
`D_PARAM` operand as `autosize + 4 + offset` before it is scaled
(`pass.c`'s `maxref`, the same expression as `span.c`'s operand
computation), and `_main`'s `$12` frame is rounded to 16 by `ldobj`, so
offset 0 is 20 = R20 and offset 4 is 24 = R24. The argument base is
therefore the caller's `SP+4`, with the call's return slot at `SP+0`
(`CALL` stores the return address there — see the HRI record below).
The loader and the core therefore need no register file: every operand
is a memory word.

The addressing mode in that first parcel is **0xD = `*Roffset` stack
offset indirect** (Table 1-23, printed p. 1-26), not 0xC (absolute
indirect) — exactly right for `FP-4`, and our assembler already has it
as the `Rexpr` operand form.  Written the Bell way,

```
MOV R0xbfc, *$0x4008     ->  86DC 0BFC 4008
```

our encoder reproduces the shipped binary's first three `_main` parcels
exactly; `tests/test_hobbit_asm.py` checks that against
`tools/plan9-1e/hobbit/bin/echo` itself (symbol table → `_main` → the
three parcels, low byte first), so the check cannot drift.
(`MOV *$0xbfc, *$0x4008` is a different instruction — mode 0xC — and
gives `86CC 0BFC 4008`, which is why reading the mode matters.)

That fixes **text at 0x1020 and little-endian 16-bit parcels**.  It does
*not* fix the placement rule: `zl/span.c`'s `xspan` lays instructions out
compactly (`c += p->mark`) and pads only `JMP`/`RETURN` (`rnd(c, AMOD)`)
and the text end (`rnd(c, 4)`), yet `cat` and `echo` both carry one
`0x0000` parcel after `_main`'s first MOV, which decodes as `KCALL $0x0`
and is in neither `main9.s` nor `main9p.s`.  That parcel, and `rc`/`za`'s
`_main` starting at an odd parcel boundary (entries 0xb9c6 and 0x7282,
checked across all five shipped binaries), are open — an
"even-parcel-start" rule explains `cat`/`echo` but is refuted by `rc`
and `za`, so no simple alignment rule has been adopted.
Until they are explained, the loader will decode at run time and trap
on an unimplemented parcel rather than assume a size rule.

**One anomaly remains, and it is `echo` only.** `echo`'s `_main`
(0x2ad0) begins with the same MOV to its own `_clock` (0x4008) and the
same two frame loads, but where `cat` has the call it has parcel
0xffff (no such opcode: `zl/optab.c`'s genops stop at 0x3e), and
`echo`'s `main` at 0x1020 begins with 0xffff too, while `cat` at the
same addresses is clean `main9p.s`.  Whether that is
a linker artefact of one binary or something about `echo` itself is not
known; the loader uses `cat` as its oracle and the difference is written
here rather than smoothed over.

## First boot attempt (2026-11-19)

`bsv/run_p9.sh cat` loads the 1e `cat` image (whole file at 0x1000, text
0x1020, data 0x3000, 4,317 words) into a 64 Kbyte testbench memory, fills
the 3 Kbyte prefetch window **from 0x1020** and starts at the image's
entry 0x12bc with SP = 0x800, MSP = 0xC00, PSW = 0x200.

**The startup runs, and the boundary is an instruction the core lacks.**
With the text read as little-endian 32-bit words (`tools/p9exec.py`), the
prefetch window filled from the entry's 1 Kbyte page, and SP = 0x800,
`bsv/run_p9.sh cat` retires Bell Labs' `_main`:

```
HRI pc=12bc insn=0bfc0000 sp=00000800>000007f0 msp=00000c00>000008f0 we=0 addr=00000000 data=00000000 mask=00 trap=0 cyc=197
HRI pc=12be insn=86dc0000 sp=000007f0>000007f0 msp=000008f0>000008f0 we=1 addr=00003004 data=00000000 mask=0f trap=0 cyc=1
HRI pc=12c4 insn=60a10000 sp=000007f0>000007f0 msp=000008f0>000008f0 we=1 addr=000007f4 data=00000000 mask=0f trap=0 cyc=1
HRI pc=12c6 insn=60c20000 sp=000007f0>000007f0 msp=000008f0>000008f0 we=1 addr=000007f8 data=00000000 mask=0f trap=0 cyc=1
HRI pc=12c8 insn=06ac0000 sp=000007f0>000007f0 msp=000008f0>000008f0 we=1 addr=000007f0 data=000012ca mask=0f trap=0 cyc=1
```

`insn=` prints the first two parcels, so `0bfc0000` is the one-parcel
`ENTER R-16` and `86dc0000` is the MOV's prefix with its next parcel
(0x0000, the source offset) alongside. The `ENTER` sets SP to 0x7f0 and
MSP follows it down (`MSP = SP + 0x100`); `MOV R0,_clock` stores zero at
cat's `_clock` (0x3004); the two parameter loads read the (zeroed)
argument area; and `CALL main` stores 0x12ca — the `CATCH` the linker
inserted — at [SP] and jumps to 0x1020.

The model then runs `cat`'s `main`, which with the testbench's
`argc = argv = 0` takes its "no files" path (`main` at 0x1020, 0x1022…
0x1034), calls `exits` (0x1170) and stops there:

```
HRI pc=1170 insn=0bfc0000 sp=000007d0>000007c0 msp=000008d0>000008c0 we=0 addr=00000000 data=00000000 mask=00 trap=0 cyc=5
HRI pc=1172 insn=29030000 sp=000007c0>000007c0 msp=000008c0>000008c0 we=1 addr=000007cc data=00000020 mask=0f trap=0 cyc=1
HRI pc=1174 insn=48030000 sp=000007c0>000007c0 msp=000008c0>000008c0 we=0 addr=00000000 data=00000000 mask=00 trap=0 cyc=1
HRI pc=1176 insn=18150000 sp=000007c0>000007c0 msp=000008c0>000008c0 we=0 addr=00000000 data=00000000 mask=00 trap=0 cyc=0
FAULT pc=00001178
TRAP pc=0x00001178: unimplemented opcode (Tables 1-15..1-20)
```

0x7843 is the one-parcel `SHL3 $2,R12` (`Table 1-15`, p. 1-22); the
core's one-parcel decode has no case for opcode 0x1E/0x1F
(`bsv/HobbitDecode.bsv`'s `5'h01`…`5'h1C` list). That is the first
refusal, and it is the loud refusal the model is supposed to give; the
next milestone inherits it.

Two prefetch fixes were needed earlier and remain:

* **the window can start anywhere** — `startFillAt(addr)` /
  `prefetchImageAt(addr)` (the boot image's code starts at 0x1020, not 0);
* **a filled line goes to the set its address names** (`addr[9:3]`), not
  to the fill counter — with the window at the image's base the two
  differ.

The testbench now fills the window from `p9fillbase()` (the entry's
1 Kbyte page). For `cat` that page is 0x1000…0x13ff, which holds both
`_main` (0x12bc) and `main` (0x1020); for `echo` the entry is 0x2ad0, so
the window holds the startup only and the call to `main` would be a
`TR_FETCH_MISS`, because there is no on-demand fill in the prefetch box
(`mkHobbitPrefetch`).

`run_p9.sh cat` prints exactly the records above (and `run_p9.sh echo`
the same five startup records, at 0x2ad0 addressed with `_clock` 0x4008,
then the fetch miss at 0x1020).

## Bell Labs' linker links Bell Labs' own startup (2026-11-19)

`tools/build_zl_inferno.py` builds the 1st Edition `zl` on this host with
the Inferno64 C environment.  It now links `libc.a`'s real members, not
just a hand-assembled stub:

```
$ python3 tools/build_zl_inferno.py --link-main9 \
      --libc /tmp/p9/plan9-1e/hobbit/lib/libc.a
/tmp/zl-inferno/zl/zl
link: .../zl -o .../main9-link.out .../main-empty.z .../main9.z .../argv0.z .../atexit.z .../_exits.z
  ZLLIB=/tmp/p9/plan9-1e/hobbit/lib
  header: magic 0x197  text 0xbc  data 0x10  bss 0x84  syms 0x5cc  entry 0x1022
  main   0x00001020
  _main  0x00001022
  _clock 0x00002004
  exits  0x000010a0
  `_main` at 0x1022, parcels (address order):
    00001022  0bfc  op02
    00001024  86dc  op06 smd dmc ['0x0000', '0x2004']
    0000102a  60a1  op18
    0000102c  60c2  op18
    0000102e  07f9  CALL 1020
    00001030  c6fd  op06 smf dmd ['0x0000', '0x10d6', '0x0000', '0x0004']
    0000103a  0433  CALL 10a0
    0000103c  0ffa  JMP 1030
  check: `_main` is ENTER R-16 then MOV R0,_clock(0x2004)
```

That answers the parcel question from the 1e side, and it agrees with
all five shipped binaries:

* `_main` starts with `ENTER R-16` (`0x0bfc`), which `zl` inserts
  (`pass.c`, `follow()`); then `MOV R0,_clock` as three parcels whose
  **second is 0x0000** — the source offset of `R0`, which is the value
  the old notes mistook for a hole.
* `main` is a program symbol, so the link supplies a one-instruction
  program object (`RETURN`); it is linked first, which puts `main` at
  the text base 0x1020 exactly as in `cat` and `echo`.  `main`'s body
  cannot change `_main`'s parcels, only the `CALL`'s displacement (ours
  is the short one-parcel form because `main` is adjacent; `echo`'s
  `main` is 0x1abc away, so its CALL is the three-parcel long form
  `0x80e1 ffff e544`).
* The `CATCH R16` that the shipped binaries carry after `CALL main` is a
  second `follow()` insertion (case ACALL); it appears when the
  program's declared frame does not cover the following code.  The
  dummy program's `$0` frame gets none; a `$2048` frame makes `zl`
  emit `0805` there, which is the discriminating experiment.

The host port needed six edits to get this far, all in the build script
and all in patched *copies* of the vendored sources:

* `diag`'s 1993 varargs hack `doprint(..., &(&a)[1])` (`list.c:212`)
  passed a pointer into the caller's frame as a `va_list`.  On arm64 the
  callee reads the format string's bytes as the `%s` argument, which is
  the reported `EXC_BAD_ACCESS` in `_platform_strlen`: lldb showed
  `x0 = 0x656e696665646e75` — the ASCII `"undefine"` from
  `"undefined: %s\n%P\n"` — and the caller was `patch()`'s
  `diag("undefined: %s\n%P\n", ...)` via `doprint`.  `va_start`/`va_end`
  is the fix.
* `Rlent.offset` was a host `long`, making the 1e symbol entry 32 bytes
  instead of 28 (`zc/z.out.h:147`); the shipped archives then read
  "bad or out of date".
* the library directory `/hobbit/lib` is taken from `$ZLLIB`, because
  `libc.a`'s `atexit.z` carries an `AHISTORY` record with
  `to.offset = -1` (a real auto-library directive) that otherwise sends
  `loadlib` to a path that does not exist here.
* `ldobj` now zeroes each `Prog`; the 1993 code reads uninitialised
  `hunk` for `AHISTORY`'s `D_NONE` operands (`obj.c:614` has the
  zeroing commented out), which can turn any history record into a
  spurious library request.
* Inferno's fmt has no `%f` (`lib9/dofmt.c`), so the timing prints are
  integer milliseconds, and `%P` is dropped: Inferno's fmt *does* call
  installed conversions, with its own `va_list`, which the `Fconv`
  protocol does not match — that was a second SIGBUS, in `asmb`'s
  listing.  `listinit` now installs nothing, and `strconv` refuses
  loudly if it is ever reached.
* `main9.z`'s records are read with `zl`'s own grammar
  (`ANAME`/`ATEXT`/`AMOV`/`ACALL`/`AJMP`/`ADATA`/`AGLOBL`/`AEND`), which
  `tools/build_zl_inferno.py --link-main9` now prints; the startup is
  the seven records `main9.s` has, plus the linker's `ENTER`.

What the port still does not do: `zl -a`/`-W` print parcel words, not
the symbolic `%A/%D/%P` text (no 1e fmt engine), and the shipped
archives' auto-library directive needs `ZLLIB` to be set (the script
does that for the demo).

## Bell Labs' own startup records (2026-11-19)

`hobbit/lib/libc.a` in the same distribution ships `main9.z`, and its
records (the format `zl/obj.c`'s `ldobj` reads) state `_main` exactly:

```
ATEXT  _main $12
AMOV   REG R0        -> EXT _clock
AMOV   PARAM argc+0  -> REG R4
AMOV   PARAM argv+4  -> REG R8
ACALL  EXT main
AMOV   ADDR _exits   -> REG R4
ACALL  EXT exits
AJMP   _loop
ADATA / AGLOBL / AEND
```

That settles the encoder question from the 1e side, independently of
any host port: a call is `ACALL` with an `EXT` operand, stack operands
are `D_AUTO`/`D_PARAM` with negative or frame-relative offsets, and
`R0`/`R4`/`R8` are register operands (`D_REG`).

Against the linked `cat` at 0x12bc the parcels read (low byte first)

```
86dc 0bfc 3004 | 0000 | 60c2 60a1 | 0805 ...
MOV R0,_clock  | ???? | MOV argv,R8 MOV argc,R4 | CALL main
```

so three of the four startup instructions and the call are identified
parcel for parcel.  The one unexplained parcel is the `0x0000` between
the first MOV and the two parameter loads — the same filler seen in
`echo`/`zl` (`0xffff`) and the reason the model's run stops at 0x12c2.
Everything else the model needs is now known.

## What the two parameter loads encode (2026-11-19)

`main9.z` says `AMOV argc+0(FP), R4` and `AMOV argv+4(FP), R8`, with the
parameters declared `D_PARAM` at offsets 0 and 4.  The linked one-parcel
forms in `cat` are `0x60a1` and `0x60c2`, i.e. source fields 5 and 6 and
destination fields 1 and 2 — and with the p. 1-22 rule that the 5-bit
fields are stack offsets scaled by four, that is offsets **20 and 24**
for sources 0 and 4, and registers **R4 and R8** for destinations 1 and
2 (1x4, 2x4) exactly.

So the encoder's rule is `field = offset/4 + 5` for a `D_PARAM`
operand (names): the parameter area sits five words above the frame
reference the source offset counts from.  That is a rule to check
against a second function, not yet a citation.

Two details remain: the linked order is `argv` before `argc` (the
source records have the reverse), and the stray `0x0000` parcel between
the first MOV and them.

## Definition of the proof of concept

**`echo` from `plan9-1e/hobbit/bin/` runs on the model and prints its
argument over the model's UART, byte for byte, and exits with status 0.**
Then the same for one file-reading program (`cat` over a one-file
"kernel" shim), which proves `open`/`read`/`close`/`write`.

That is a port in the sense that matters here: the code executing is
Bell Labs' compiled Hobbit user code, against Bell Labs' own calling
convention and syscall vector, and the model supplies only what the
kernel would — the instructions retire through the model's pipeline and
each prints its HRI record.

## Stages and gates

1. **Executable loader** (`bsv/` + `tools/`): parse `struct Exec`
   (`sys/include/a.out.h`), place text at 0x1000, data after it, zero
   bss, set the entry. Gate: the loaded image of `hobbit/bin/echo` is
   byte-identical to its text+data fields, and nothing outside the
   declared sizes is read; a deliberate off-by-one in the header parse
   must change the first executed parcel.
2. **Startup ABI**: `_main` from `sys/src/libc/hobbit/main9.s` needs
   `argc` at `FP+0` and `argv` at `FP+4`, then `CALL main`, and
   `exits("main")` after `main` returns. Gate: the call chain from the
   entry point to `main` of the shipped binary is traced, with the frame
   pointer and stack pointer values checked against `raml.s`'s stack
   layout (PRM pp. 1-10…1-13 for the frame conventions).
3. **Syscall path**: vector 0 (`_vector0`, `raml.s:230`;
   `_vectors+0x00 = $syscall`, `raml.s:287`). Identify the user-side trap
   from the libc sources and the `CPU` escape (`zl/optab.c`:
   `{ ACPU, TNNAD, 0x00, 0 }`), then implement in the shim exactly the
   calls `echo` issues. Gate: an unimplemented syscall traps loudly with
   its number, never returns a plausible zero.
4. **Proof**: for a fixed `argv`, the UART text equals the expected
   output exactly (5,043 byte oracle discipline: an independent
   expectation, not a copy of a run), and `exits` reports 0. Negative
   control: flip one byte in the loaded text and the output must differ.
5. **Second program**: `cat` over a one-file shim — `open`, `read`,
   `write`, `close` — same gate.

## What this does and does not claim

- It is **not** a kernel boot: the syscalls are a host shim, not
  `sys/src/9/hobbit/`. Booting the 1e Hobbit kernel (`raml.s`, `trap.c`,
  `mmu.c`) is the milestone after this, and needs the MMU (now modelled)
  and the bus (plan step 7).
- It **is** stronger than the current smoke test: the instructions
  executed are chosen by Bell Labs' compiler from Bell Labs' C sources,
  so the instruction mix is not one we designed to be easy.
- **The Plan 9 way is to hand-assemble, not to extend the tools.** Where
  an instruction or a stub is needed, it is written in the assembler's
  own idiom — `TEXT`/`DATA` and macros, the parcels spelled out in the
  source — exactly as the 1e tree does for its hand-written bits; the
  model gains no instructions for the port, and `za`'s missing
  `outcode` is not to be supplied. The toolchain sources stay an oracle:
  `zl/asm.c`'s encoder checks the parcel spellings, `zl` links what the
  macros emit.

## Next steps, in order

0. Hand-assembly idiom, for anything this work has to emit: `TEXT`,
   `DATA` and the 1e macro style, parcels spelled out in the source and
   linked by `zl`. No `outcode`, no new mnemonics, no model changes to
   accommodate a stub.
1. Vendor the 1e material this needs into `hobbit/tools/plan9-1e/`
   (`hobbit/bin/echo`, `hobbit/bin/za`, `hobbit/bin/zl`,
   `sys/src/9/hobbit/`, `sys/src/libc/hobbit/`, `sys/include/a.out.h`),
   with `SHA256SUMS`; nothing edited.
2. Write `tools/p9exec.py`: header parse and load plan, independent of
   `bsv/` (the loader rule will be checked against it).
3. Write the loader as a Bluespec module and an image generator
   (`mk_image_bsv.py` learns the `Exec` header), then a testbench that
   starts at the entry with a stack and traces the first 40 retirements.
4. Identify the trap instruction from the shipped binary's first
   `main9.s` sequence and implement `write`/`exits` in the shim.
5. Record the byte-exact UART output gate in `tests/`.
