# The 1e syscall entry and the A1 shim's contract

What the model's syscall shim matches, taken from the 1e kernel's own
entry code (`tools/plan9-1e/sys/src/9/hobbit/raml.s`), from the 1e libc
stubs (`hobbit/lib/libc.a`, linked into `hobbit/bin/cat`), and from the
printed manual. Nothing here is inferred from usage.

## Entry: what the hardware does

`KCALL src` (PRM p. 3-29, printed):

```
disable interrupts
*(ISP-12) = src                  /* R4 with respect to the new ISP */
*(ISP-8)  = PC of the next instruction
*(ISP-4)  = PSW
ISP -= 16
SHAD = ISP
PC = *(VB+0)
PSW = PSW & 0xFFFF0000
enable interrupts
```

The model implements exactly that (`bsv/HobbitCore.bsv`, the KCALL
architectural write and the two-word frame tail; `docs/isa_inventory.md`
§1.9).  So after a KCALL the frame is four words at the new ISP:

| frame word | contents | who writes it |
|---|---|---|
| `ISP+0` | free; the kernel's cause code | the handler (`MOV $0x00,R0`) |
| `ISP+4` | the KCALL `src`, i.e. **the syscall id** | the hardware |
| `ISP+8` | the return PC (address after the KCALL) | the hardware |
| `ISP+12` | the saved PSW | the hardware |

**Correction to the earlier reading of `raml.s`.**  The dispatch
sequence `MOV %ISP,R4; MOV *R4,R8` (`raml.s:257-258`, `:280-281`) reads
`*(ISP)`, which is the *cause code* the handler itself wrote (`MOV
$0x00,R0` at `raml.s:231`, `$0x01`…`$0x04` in the other vectors), not the
syscall number.  The id is the KCALL's `src` word at `ISP+4`.  The
kernel's `MOV R20,R8 /* id */` (`raml.s:245`) does not read the id in
this frame either: `R20` is `CSP+80`, a word of the handler's own stack —
one more symptom of the `Ureg` discrepancy **O4** in
`docs/plan9_kernel_inventory.md`, which this shim does not depend on
(see below).

The syscall path and the exception path share `_exception`: vector 0
only sets `R0 = 0` first (the cause code the dispatcher reads).

## The vector table (`raml.s:286-301`)

| offset | entry | what |
|---|---|---|
| +0x00 | `$syscall` | system call (this is the `VB+0` word a KCALL reads) |
| +0x04 | `$trap` | exception |
| +0x08 | `$trap` | niladic trap |
| +0x0C | `$trap` | unimplemented instruction |
| +0x10 | `$trap` | non-maskable interrupt |
| +0x14…+0x24 | `$trap` | interrupts 1–5 |
| +0x28 | `$interrupt` | interrupt 6 — the board's IRQ controller |
| +0x2C/+0x30 | `$trap` | timer 1 / timer 2 |
| +0x34 | `$trap` | FP exception |

The kernel sets `VB = 0x80000000` (`raml.s:51`); the shim sets its own
`VB` from the testbench (0x0C00, `bsv/P9BootTb.bsv`).

## The libc stubs: id, arguments, result

The user side is the 1e libc's own code.  In `hobbit/bin/cat` (the same
members are in `hobbit/lib/libc.a`: `write.z`, `read.z`, `open.z`,
`close.z`, `_exits.z`, `errstr.z`) every stub is two instructions, a
`KCALL` whose **source is the syscall number** and `RETURN R0`:

| id | symbol | address in cat | parcels | call |
|---|---|---|---|---|
| 1 | `errstr` | 0x10f2 | `80F0 0000 0001 0802` | `KCALL $1` |
| 4 | `close` | 0x10ee | `0001 0802` | `KCALL $4` |
| 8 | `_exits` | 0x12da | `0002 0802` | `KCALL $8` |
| 14 | `open` | 0x10fa | `80F0 0000 000E 0802` | `KCALL $14` |
| 15 | `read` | 0x1102 | `80F0 0000 000F 0802` | `KCALL $15` |
| 20 | `write` | 0x110a | `0005 0802` | `KCALL $20` |

`tools/p9shim.py` holds the same table and its unit test decodes each id
back out of those parcels, so a wrong number or a wrong parcel beside it
fails.

**Arguments** are the user's first three stack words, the accumulator
first: `CSP+4`, `CSP+8`, `CSP+12` (`R4`, `R8`, `R12`).  Cat's call sites
are the witness: `MOV $1,R4; MOVA R32,R8; MOV R28,R12; CALL write`
(0x1a8, 0x1ae, 0x1b6) and `MOV R4,R28` immediately after the call
(0x1ba) — the result is read from the accumulator.  `_main`'s own frame
is the same convention (`MOV argc+0(FP),R4; MOV argv+4(FP),R8`).

**Result** in the accumulator, `CSP+4`.  Why `RETURN R0` leaves it
there: `RETURN src` computes `PC = *(CSP+src)` and `CSP += src & ~0xF`
(PRM p. 3-40), so a source offset of 0 reads the word at the CSP and
moves nothing.  The stub therefore returns with the caller's frame
untouched, and whatever the kernel left in the accumulator is the
result.

`exits` is special: its argument is a *string pointer*
(`main9.s`'s `MOV $_exits<>+0(SB),R4`, the `"main"` datum, and cat's
`MOV $0,R4` before the call on the `argc == 1` path).  A successful
`exits` ends the run; the shim reports status 0.

## The A1 shim: what the testbench does, and why it has this shape

The kernel side of the syscall is replaced; the hardware's part is not.
The stub is Hobbit machine code assembled by `asm/hobbit_asm.py`, placed
in the boot window's Exec header (`0x1000..0x101f`, the 32 bytes the
loader owns; text begins at 0x1020):

```
        MOV     $1, R4          ; argc = 1: cat reads its stdin
        JMP     *$_main         ; the image's entry
p9stub: JMPFN   p9stub          ; spin while PSW.F == 0
        MOV     $0, R4          ; default result (close, errstr, EOF)
        KCALL   $0              ; dispatch: VB+0 names the result handler
p9ret:  RETURN  R0              ; back through the user's own stack
p9fd:   MOV     $3, R4          ; open -> first fd after 0,1,2
        RETURN  R0
p9count:MOV     R12, R4         ; read/write: the user's n
        RETURN  R0
p9size: MOV     $<file length>, R4   ; the bytes actually transferred
        RETURN  R0
```

Sixteen parcels, exactly the Exec header.

The three model facts that fix this shape (all measured, not assumed):

1. **An operand outside `[SP, MSP)` reads as zero.**  The model's operand
   path is the stack cache and the box's defined miss is 0
   (`docs/isa_inventory.md` §1.6; `bsv/HobbitStackCache.bsv`, `readWord`).
   A stub entered with the interrupt stack as CSP therefore *cannot read
   any memory word* — not the event frame, not a doorbell word.  It can
   only write memory and branch on `PSW.F`.
2. **The host can write no machine state the machine can read**, except
   PSW (through the core's testbench `setPsw`), `VB`/the vector page
   (`eventMemWrite`), the ISP/SHAD, and a restart.  Writing the user's
   accumulator or its buffer from the testbench is impossible: the
   accumulator lives in the stack cache.
3. **The model has no `KRET`, no `CRET` and no CPU-register
   instructions.**  `bsv/HobbitDecode.bsv`'s niladic decode implements
   only `NOP`; everything else traps (`TR_UNIMP`, `TR_CPU`).

So the shim's protocol is:

* **The doorbell is the hardware's own frame write.**  The KCALL stores
  the id at `ISP-12` (PRM p. 3-29); the frame lives on the interrupt
  stack, outside `[SP, MSP)`, so it is in memory and the host polls and
  clears that word.  This is the boot plan's reserved doorbell word,
  with the hardware writing the id instead of the stub — the stub cannot
  read the id, and does not need to: the host has it.
* **The stub waits on `PSW.F`**, the only host-writable bit the machine
  can read: `JMPFN p9stub` loops while F = 0 (JMPF = jump if F = 0,
  PRM p. 3-28; `JMPFN` is `JMPF` with a predict-not-taken bit).
* **The result is delivered by a result handler the host selects**
  through the vector page: after the syscall the host writes the
  handler's address into `evmem[VB]` and releases the stub; the stub's
  `KCALL $0` jumps there.  The vector page is the one host-writable word
  a KCALL reads, so it is the shim's dispatch table.  The handlers set
  the accumulator from a value the machine actually has: the user's own
  `n` (`MOV R12,R4`), the fd it allocated (`3`), zero, or the generated
  count ("the bytes this shim transferred").
* **The return is `RETURN R0`**, which takes the new PC from the user's
  own stack word — the address `CALL write` left there — with the SP
  unchanged, exactly as the libc stub's own `RETURN R0` would have done.
  The model unwinds the *call*; the host restores what `KRET` would have
  restored (the PSW, from the frame's `ISP-4` word, and the ISP) through
  the core's testbench surface, because no instruction can.

**What the shim does not depend on: O4.**  It never reads the kernel's
eight-word `Ureg`; it reads the printed four-word frame the model
implements.  When the kernel is built (A3/A4) the `Ureg` question still
has to be settled by the experiment O4 describes — the shim's frame dump
is the same shape that experiment needs: with a known KCALL the eight
words at `ISP` show `id` at +4, `PC` at +8, `PSW` at +12 and the cause
at +0.

## Per-syscall contract as implemented

`fd` numbering follows the kernel's `newfd`: 0, 1, 2 are stdin, stdout,
stderr; the first `open` returns 3.  Offsets are per fd.

| id | call | arguments (`CSP+4,+8,+12`) | result | handler |
|---|---|---|---|---|
| 1 | `errstr(buf,n)` | buf, n | 0 (no error text; copies nothing) | `p9ret` |
| 4 | `close(fd)` | fd | 0 | `p9ret` |
| 8 | `exits(msg)` | msg (a string pointer, 0 = none) | — the run stops, status 0 | — |
| 14 | `open(path,mode)` | path, mode | 3 (the shim serves one file; a different path is refused) | `p9fd` |
| 15 | `read(fd,buf,n)` | fd, buf, n | the bytes moved; 0 at EOF | `p9ret` (0), `p9count` (n), `p9size` (the file, when the request exceeds it) |
| 20 | `write(fd,buf,n)` | fd, buf, n | n | `p9count` |

`errstr`'s buffer is in the stack cache, so this shim cannot copy a
message into it; it reports the empty string and returns 0.  Nothing on
the boot path calls it (cat's `argc == 1` path is `cat(0, "<stdin>")`
then `exits(0)`), and a program that printed the buffer would see
whatever was there.

### Refusals

Every refusal stops the run with the number and the defining files, never
a plausible guess:

* an id that is not one of the six: `P9SHIM REFUSED syscall <n> …not in
  the 1e syscall table (hobbit/bin/cat stubs; hobbit/lib/libc.a members;
  raml.s _vectors)`;
* `read` from an fd other than 0 or 3, `write` to an fd other than 1 or
  2;
* a partial `read` whose count is neither the request nor the whole file:
  the result handler's count is an immediate generated from the host file
  (see below), and a count no handler can name is refused rather than
  returned wrong;
* an `open` whose path is not the shim's file.

### The generated count, and why

`read`'s count is data the host knows and the machine cannot receive:
the only host-to-machine channels are `PSW.F` (one bit), the vector page
(a code address) and the ISP.  So the shim's `p9size` handler carries
the file's length as a 16-bit immediate, generated by
`tools/p9shim.py --emit` from the same file table that serves the read;
the count returned is the count actually moved.  Requests that the
whole-file immediate cannot describe are refused (above).  This is a
limit of the model's operand path, not of the syscall: with the p. 1-5
off-chip operand path modelled, the host could write the accumulator
directly and no generated immediate would be needed.
