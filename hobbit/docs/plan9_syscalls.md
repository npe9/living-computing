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
        JMP     _main           ; the image's entry
p9stub: CMPEQ   $0, *$RDY       ; F = 1 while the host is still working
        JMPTY   p9stub          ; jump if F is true, predicted taken
        MOV     *$RES, R4       ; the result, into the accumulator
        RETURN  R0              ; back to the libc stub
```

Ten parcels (`7021 0d5d 9ffc 0000 0c14 1ffd 86cd 0c18 0004 0802`).
`RDY` = `0x0c14` and `RES` = `0x0c18` are words of the testbench's device
page, read as absolute operands.  (`JMPTY`: the T/F letter is the
condition, the Y/N letter the static prediction — `JMPFY` here would
leave the loop while the host is still working.)

The protocol:

* **The doorbell is the hardware's own frame write.**  The KCALL stores
  the id at `ISP-12` (PRM p. 3-29); the host polls that word.
* **The host does the syscall**, reading the three arguments from the
  user's stack words and moving bytes between the host file, the console
  and the user's buffer in memory.
* **The host answers in order**: doorbell cleared, `RES` written, `RDY`
  set.  The stub re-reads `RDY` from memory on every iteration, so the
  host may answer at any clock; nothing has to land between two adjacent
  stub instructions.
* **The stub returns with `RETURN R0`**, which takes the new PC from the
  user's own stack word — the address `CALL write` left there — with the
  SP unchanged, exactly as the libc stub's own `RETURN R0` would have
  done.
* **The host finishes what `KRET` would do**: the PSW from the frame's
  `ISP-4` word, `ISP += 16`, and `RDY` cleared for the next call.  The
  model has no `KRET`/`CRET` yet.

The host's writes to memory are queued behind the machine's: the
testbench memory has one write port, the machine's write always takes it,
and a host write waits one register for a free clock
(`bsv/P9BootTb.bsv`, `mkP9Mem`).

**History, because the shape changed.**  Until the core read operands
outside the stack cache (`docs/conformance_1to1.md` §1a) the stub could
read no memory word at all.  The first shim therefore signalled through
`PSW.F` with a two-step ACK word, could return only 0 or one generated
constant (the file's length), and refused every other count.  It also
could not be made correct: the host had to change `PSW.F` between the
stub's `MOV $2,*ACK` and the conditional jump two parcels later, and
whether it managed to was a matter of clock phase.  That shim is gone;
its refusals ("the machine's result channel can name only 0 and N") no
longer exist.

**Known limit.**  The host reads and writes the user's buffer in memory.
A buffer word that is also inside `[SP, MSP)` has its current value in
the stack cache, not in memory, so a program that touched such words
itself would disagree with the host.  `cat` hands its buffer to `read`
and `write` untouched.

**What the shim does not depend on: O4.**  It never reads the kernel's
eight-word `Ureg`; it reads the printed four-word frame the model
implements.  When the kernel is built (A3/A4) the `Ureg` question still
has to be settled by the experiment O4 describes — the shim's frame dump
is the same shape that experiment needs: with a known KCALL the eight
words at `ISP` show `id` at +4, `PC` at +8, `PSW` at +12 and the cause
at +0.

## Per-syscall contract as implemented

`fd` numbering follows the kernel's `newfd`: 0, 1, 2 are stdin, stdout,
stderr; `open` returns 3.  The shim serves one host file: it is stdin,
and it is what `open` opens, whatever path is named.

| id | call | arguments (`CSP+4,+8,+12`) | result (`RES`) |
|---|---|---|---|
| 1 | `errstr(buf,n)` | buf, n | 0 (no error text; copies nothing) |
| 4 | `close(fd)` | fd | 0 |
| 8 | `exits(msg)` | msg (a string pointer, 0 = none) | — the run stops; status 0 for a nil message, 1 otherwise |
| 14 | `open(path,mode)` | path, mode | 3 |
| 15 | `read(fd,buf,n)` | fd, buf, n | the bytes moved, `min(n, left)`; 0 at EOF |
| 20 | `write(fd,buf,n)` | fd, buf, n | n |

`tools/p9shim.py`'s `Shim` class is the same contract in Python, and
`tests/test_p9shim.py` (21 tests) drives it and pins the stub's parcels.

### Refusals

Every refusal stops the run with the number and the defining files, never
a plausible guess:

* an id that is not one of the six: `P9SHIM REFUSED syscall <n> …not in
  the 1e syscall table (hobbit/bin/cat stubs; hobbit/lib/libc.a members;
  raml.s _vectors)`;
* `read` from an fd other than 0 or an opened 3;
* `write` to an fd other than 1 or 2.

## The reference runner's kernel (`tools/p9run.py`, 2026-11-20)

The A1 shim above serves one file to one program.  `tools/p9run.py` is
the kernel's side for the *reference model* (`sem/hobbit_sem.py`), and it
is what the Bluespec testbench has to match next: it runs `za`, `zl`,
`echo` and `cat` from the release (A2's status in
`docs/plan9_boot_plan.md`; `tests/test_p9run.py`).

**Exec** (`sys/src/9/port/sysproc.c` `sysexec`, `sys/src/9/hobbit/trap.c`
`execregs`): with `nargs` strings totalling `nbytes`,

    ssize = 4*(nargs+1) + roundup(nbytes, 4);  if((ssize+4) & 7) ssize += 4
    argv[] at USTKTOP - ssize, the strings at USTKTOP - nbytes
    sp    = USTKTOP - QUADALIGN(ssize + 12)
    sp[0] = USTKTOP - 4;  sp[1] = nargs (the returned accumulator);
    sp[2] = USTKTOP - ssize;  msp = USTKTOP;  pc = entry

USTKTOP is KZERO = RAMBASE = 0x80000000 (`mem.h:42,58,67,73`).
`main9.s` reads `argc+0(FP)` and `argv+4(FP)`, which are `sp[1]` and
`sp[2]`.  The PSW is `PSW_UL|PSW_X|PSW_S` (0x8600): little-endian user
data, user level, CSP = SP.  The real process also has `PSW_VP`; the
runner is physical.

**Entry and return.**  The model retires the KCALL (the frame at
ISP-12/-8/-4, p. 3-29); the runner reads the id from `ISP-12`, the
arguments from the *user's* `CSP+4..+16`, does the call, stores the
result at `CSP+4`, and does KRET's part: PC from `ISP-8`, PSW from
`ISP-4`, `ISP += 16`.

| id | call | arguments | result |
|---|---|---|---|
| 1 | `errstr(buf)` | buf | 0; the last error text, 64 bytes (ERRLEN) |
| 4 | `close(fd)` | fd | 0 |
| 8 | `exits(msg)` | msg | the run ends with the string |
| 14 | `open(path, mode)` | path, mode (low 2 bits: OREAD/OWRITE/ORDWR) | the lowest free fd, or -1 |
| 15 | `read(fd, buf, n)` | fd, buf, n | bytes moved; 0 at EOF and on stdin |
| 16 | `seek(fd, off, type)` | fd, off (signed), type 0/1/2 | the new offset |
| 20 | `write(fd, buf, n)` | fd, buf, n | n; fds 1 and 2 are the console |
| 22 | `create(path, mode, perm)` | path | the lowest free fd (the file truncated), or -1 |
| 24 | `brk_(addr)` | addr | 0 |
| 25 | `remove(path)` | path | 0, or -1 |

Paths resolve inside `--root`, which is both `/` and the working
directory (`zl` finds `/hobbit/lib/libc.a` there); a path that leaves it
stops the run.  Any other id stops the run with its number and name.
This is what `za` and `zl` use; it is not the 1e system-call set
(`sys.h` has 37 numbers) and nothing here pretends to `fork`, `exec`,
`stat`, `pipe` or `notify`.

**Floating point** is not a system call: it is the
unimplemented-instruction sequence (p. 1-39) and a user-level handler,
`fprt0.s` + `fpihobbit.c` + `fpi.c`.  The reference model retires the
`trap=1` record (`*(CSP) = PC`, which is why 1e's compiler keeps nothing
in R0 across floating point) and the runner plays the handler:
`fpihobbit.c`'s opcodes (FMOV 17, FCMPGT 25, FCMPEQ 26, FSUB 40, FMUL
41, FDIV 42, FADD 43 and the `3` forms 56-59), its operand modes
(0/1 absolute F/D, 4/5 stack, 8/9 indirect, 12-14 word, 15 immediate
single), its operand order (FSUB and FDIV are destination op source;
FCMPGT sets F when source > destination), its `sequence` strings (the
`3` forms store to `CSP+4` in the *destination's* type), and its loop
over consecutive floating-point instructions.  The arithmetic is host
IEEE double, not `fpi.c`'s 53+3-bit `Internal`, so FADD/FSUB/FMUL/FDIV
may round differently from 1e in a last bit; moves, compares and integer
conversions are exact.  `za` executes one FMOV (0x26d0, `cinit`).

## The Bluespec run's kernel entry (`bsv/P9HostTb.bsv`, 2026-11-20)

The A1 shim (above) keeps running `cat` in the suite as it did.  The A2
runs use a second testbench built on the reference runner's recording
(`tools/p9run.py --record`, format in `bsv/p9host.c`), because a kernel
written twice -- once in Python for the reference model, once in
Bluespec or C for the core -- is two kernels that can disagree.  There is
one kernel, the Python one; the Bluespec run *replays* it:

* the boot memory is the recording's (`M` records): text and data at
  their real addresses, the exec frame below USTKTOP = 0x80000000, and a
  kernel page at 0x0c00 with the vector table, two stubs and their
  device words;
* memory is `p9host.c`'s sparse 32-bit store behind the core's ordinary
  `HobbitMem` interface (one registered read, one write); a write
  outside every segment stops the run;
* at each kernel entry `p9host.c` checks what the *machine* presents --
  the system-call id KCALL stored at `ISP-12`, the arguments at the
  user's `CSP+4..`, or for floating point the PC the unimplemented
  sequence stored at `*(SP)` -- against the recording, applies the bytes
  the kernel stored into the process (`B`), takes what a `write` call
  writes from the model's memory into a file (`O`), and hands back the
  recorded result (`R`).

**The stubs** (assembled by `asm/hobbit_asm.py` from `p9run.stub_source`;
the vector at `VB+0` is the first, at `VB+12` the second):

    ksys:   MOVA    R0, *$TMP        ; TMP = SP
            ENTER   *$TMP            ; flush the whole cache; MSP = SP
            MOV     $1, *$GO         ; ring: a system call
    kwait:  CMPEQ   $0, *$RDY
            JMPTY   kwait            ; wait (RDY is re-read every time)
            MOV     $0, *$RDY
            MOV     *$RES, R4        ; the result, into the accumulator
            CMPEQ   $1, *$FLAG       ; leave PSW.F as the host asks
            JMP     **$(ISP0-8)      ; the PC KCALL saved (p. 3-29)

    kfp:    MOVA R0, *$TMP ; ENTER *$TMP ; MOV $2, *$GO ; wait ;
            MOV $0, *$RDY ; CMPEQ $1, *$FLAG ; JMP **$RES

Why each line is there:

* `ENTER *$TMP` is the printed flush (p. 3-19: a source that is not a
  stack offset "flush[es] stack cache unconditionally", `SHAD = MSP = SP
  = target`; p. 3-20 case 4: the target is the word at the address).  The
  host cannot see inside the stack cache, and after this it does not need
  to: every stack word is in memory, including the arguments and any
  buffer on the stack.  This removes the A1 shim's "host writes behind
  the cache" limit.
* The wait loop is host time; `tools/p9trace_cmp.py` drops every record
  whose PC is in the kernel page, so the number of turns does not
  matter.
* `CMPEQ $1, *$FLAG` sets PSW.F from a word: for a system call the flag
  the process had before the KCALL (bit 4 of the PSW saved at `ISP-4`),
  for floating point the flag a compare produced.  The host never writes
  PSW.F while user instructions are in the pipe.
* `JMP **$addr` returns to the instruction *after* the KCALL, so libc's
  own `RETURN R0` executes on the core as it does on the reference model
  (the A1 stub returned over it).

**What the host still does to the machine:** once per system call, after
serving it, it sets the PSW to the one KCALL saved and the ISP back
above the frame (`doKret`).  That is KRET, which the model does not have.

**Testbench lessons, recorded because they cost two builds each.**  The
host's poll rule fires every clock.  In its first form it called
`setPsw`/`setIsp`, was scheduled against the pipeline's rules, and --
being the more urgent -- starved them all: the machine never retired.
In its second form it handed the KRET to another rule through a
register, which closed a scheduling cycle that bsc broke the same way.
It now reads only, and signals through a wire.

