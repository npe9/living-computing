# The 1e syscall entry, for A1 of the boot plan

What the model's syscall shim must match, taken from the kernel's own
entry code in `tools/plan9-1e/sys/src/9/hobbit/raml.s`. This is the
contract A1 implements; nothing here is inferred from usage.

## Entry

```
TEXT _vector0(SB), $16            /* syscall */
        MOV     $0x00, R0
_exception:
        MOV     %SP, R16
        SUB3    R16, %MSP
        CMPHI   R4, $SCSIZE
        AND3    $PSW_X, R28       /* was it user mode? */
        MOV     %FAULT, R12
        JMPFY   _mspok
        MOV     R16, %MSP
_mspok:
        CMPEQ   $0, R4
        MOV     R20, R8           /* id */
        MOV     %MSP, R20
        OR      $PSW_S, %PSW      /* switch to SP */
        MOV     %SP, %SHAD
        JMPFY   _wasuser
```

`raml.s:229-250`. Consequences for the shim:

* the syscall path and the exception path **share `_exception`**: vector
  0 only sets `R0 = 0` first (the cause code the dispatcher reads);
* `R20` on entry carries the *id* the entry moves to `R8` — that is the
  register the user side fills;
* `R4` is tested against `SCSIZE` and against zero, and `%FAULT` is
  saved to `R12` before the branch — all of these assume the frame the
  Hobbit pushes on an event (PRM pp. 1-36…1-39), whose offsets are the
  open question **O4** in `docs/plan9_kernel_inventory.md`;
* the user branch `_wasuser` runs `ENTER $(USERADDR+SPOFFSET-16)`,
  `CATCH R16`, then dispatches.

## Dispatch

Both branches end in the same four instructions (`raml.s:255-262`,
`278-284`):

```
        MOV     %ISP, R4
        MOV     *R4, R8           /* syscall number, first word of the frame */
        SHL     $2, R8            /* word index into _vectors */
        ADD     $_vectors(SB), R8
        MOV     *R8, R8
        CALL    *R8
```

So the **syscall number is the first word of the interrupt-stack frame**
(`*(ISP)`), and the handler is `_vectors[number]` — a 32-bit vector
table, not a byte table.

## The vector table (`raml.s:286-301`)

| offset | entry | what |
|---|---|---|
| +0x00 | `$syscall` | system call |
| +0x04 | `$trap` | exception |
| +0x08 | `$trap` | niladic trap |
| +0x0C | `$trap` | unimplemented instruction |
| +0x10 | `$trap` | non-maskable interrupt |
| +0x14…+0x24 | `$trap` | interrupts 1–5 |
| +0x28 | `$interrupt` | interrupt 6 — the board's IRQ controller (all board IRQs, per the inventory) |
| +0x2C | `$trap` | timer 1 |
| +0x30 | `$trap` | timer 2 |
| +0x34 | `$trap` | FP exception |

The model already implements the hardware side of these as the event box
(`bsv/HobbitEvents.bsv`), which vectors through `VB` — the kernel sets
`VB = 0x80000000` (`raml.s:51`), so the model's `VB`-relative vectors and
this table coincide once the kernel runs.

## What A1 has to provide

1. the trap/vector path from the model's event box to a *hand-written*
   handler stand-in: on `_vectors+0x00`/`+0x04`, the shim sees the frame
   and the id;
2. the Plan 9 syscall numbers the programs use (`write`, `exits`,
   `open`, `read`, `close` at first), taken from the 1e libc's own
   tables, not from memory;
3. the actual services: `write` copying to the model's UART, `exits`
   stopping the run with a status.

## Open, to be settled by the first run

* **Where the user side puts the number.** `R20` on entry is the id,
  and the number must also be the first word of the frame; the libc stub
  that does both has not yet been located in the 1e tree (the syscall
  stubs are not in `sys/src/libc/hobbit/`; candidates are the shared
  libc sources assembled per machine).
* **O4**, the frame layout, which decides the offsets the shim reads.
