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

**The text layout is settled, and `cat` is its oracle.** With the load
rule above and parcels read low byte first, disassembling `cat`'s
`_main` (0x12bc) reproduces `sys/src/libc/hobbit/main9p.s` instruction
for instruction:

```text
0x12bc  86dc 0bfc 3004   MOV  clock-4(FP), _clock(SB)   ; _clock is at 0x3004
0x12c4  60c2             MOV  argc+0(FP), R4
0x12c6  60a1             MOV  argv+4(FP), R8
0x12c8  ...              CALL main(SB)  -> 0x1020
```

(our disassembler prints `MOV R20,R4` / `MOV R24,R8` for the two
frame-relative loads, and `CALL -0x29a`, because Plan 9's pseudo-register
names are not its syntax)

**There are no registers to decode.** The machine is memory-to-memory
(PRM §1.4, printed p. 1-4: "general purpose registers are eliminated";
the stack cache "appears as normal memory"), and the 5-bit `R` fields of
Tables 1-15/1-18 are **stack offsets scaled by 4** (p. 1-22). That is
why `0x60c2` (src 6, dst 2) is `MOV argv+4(FP), R8` — 2x4 = R8 — and
`0x60a1` (src 5, dst 1) is `MOV argc+0(FP), R4`, and why the first
instruction's field `0x0bfc` is `FP-4` and its
destination `0x3004`/`0x4008` is `_clock`.  (That `FP` is 0xC00 is an
inference from `0xbfc + 4`; the vendored tree defines no `FP` constant —
it lives in the missing `cc` front end — so it is labelled an inference,
not a citation.)  The loader and the core
therefore need no register file: every operand is a memory word.

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

`bsv/run_p9.sh echo` loads the 1e `echo` image at 0x1000/0x1020/0x4000
(`tools/p9exec.py --image`, 4,317 words) into a 64 Kbyte memory, warms
the prefetch and starts at the entry 0x2ad0 with SP = 0x800, MSP = 0xC00,
PSW = 0x200 (`bsv/P9BootTb.bsv`).  Result: **`FAULT pc=00002ad0`** and
no retirement — the fetch missed.

The cause is stated by the model itself (`HobbitDecode.bsv`,
`HobbitPrefetch`): the instruction window is 64 words warmed once, and
"a fetch whose line is absent is a model limitation, and the PDU turns
it into TR_FETCH_MISS so the core retires a loud trap record rather than
aliasing a line silently".  The smoke never meets this because it starts
at 0, inside the warmed window.

So the next task is not in the loader: **the PDU needs a refill on a
fetch miss** — MMU-translated line fetch, the Table 4-7 fetch/empty
pipeline delay, and the line installed in place of the warmed window —
before any Plan 9 program can run past its first line.  The loader
scaffolding (image, entry package, `startAt(pc, sp, msp, psw)`, 64 Kbyte
testbench memory) is in place and is what the refill will be tested with.

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
