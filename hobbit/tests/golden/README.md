# Golden HRI traces — hand-derived references for the ATT92010 core

These six programs and their retirement traces were derived by hand from the
printed *ATT92010 Hobbit Microprocessor Programmer's Reference Manual*
(January 1993, `docs/ATT92010_Hobbit_Programmers_Reference_Jan93.pdf`).
Nothing here was produced, checked or corrected by `bsv/`, `asm/` or `sem/`,
and no cycle number in the traces was copied from either directory: every
`cyc` is derived from the printed Chapter 4 tables and Chapter 3's flush/refill
pseudocode, as written out in each `.md`. The only tool used while deriving was
the Python 3 standard library, for the arithmetic written out in each `.md`.
They are the oracle the implementation is measured against, so an
implementation must never be used to regenerate them.

One stated exception to "nothing here was produced by `asm/`": `016`
(operands in memory, outside the stack cache's window) had its parcels
assembled by `asm/hobbit_asm.py` and then checked by hand against the
encoding tables, and one of its hand-derived cycle counts was corrected
from the printed p. 3-19 loop after `sem/` disagreed. `016.md` says so
under "How this file was derived"; its state transitions and the
remaining cycle counts were derived by hand before either model ran.

Printed-page arithmetic: the PDF page is the printed page plus 8 in
Chapter 1, plus 48 in Chapter 2, plus 58 in Chapter 3. `T1-15` is the
manual's own Table 1-15.

## Files

| file | contents |
|---|---|
| `NNN.hex` | the program image in the fixed format |
| `NNN.trace` | the retirement lines for that image, one per retired instruction, program order |
| `NNN.md` | the derivation: encoding and state transition for every instruction and every trace line, with the printed page for each |
| `check_golden.py` | format and traceability checker (standard library only, no simulation) |
| `README.md` | this file: pre-state, command shape, conventions, coverage, ambiguity index |

## Fixed formats (project contract, quoted)

Memory image: text, one 32-bit word per line, 8 lowercase hex digits,
ascending addresses from 0; parcel at even address in bits 31:16, odd address
in bits 15:0; entry at 0.

Retirement line, one per retired instruction, program order:

```
HRI pc=%04x insn=%04x%04x sp=%08x>%08x msp=%08x>%08x we=%d addr=%08x data=%08x mask=%02x trap=%d cyc=%d
```

`pc` is the address of the instruction's first parcel, `insn` its first two
parcels (second `0000` for a one-parcel instruction), `sp`/`msp` before and
after, `we`/`addr`/`data`/`mask` one architectural word write (stack-cache
resident writes included), `trap` = 1 for the unimplemented-instruction trap,
and `cyc` the instruction's occupancy in core clock cycles: cycles between the
previous retirement and this one, or from the core's start for the first
record. The `cyc` model, its printed sources and its named parameters are in
"Cycle model" below.

The record is the **HRI** line, the *Hobbit Retirement Interface*: this
project's analogue of riscv-formal's RISC-V Formal Interface (RVFI), with the
fields fixed by the contract above. The prefix is part of the format, not a
label of convenience: `check_golden.py` reports a line that begins `RVFI `
(the record's former name) as a format error instead of skipping it, so a
harness left on the old spelling cannot pass by being ignored.

## Cycle model (the `cyc` field)

`cyc` is the instruction's occupancy in core clock cycles, measured at
retirement: cycles between the previous retirement and this one, and for the
first record from the core's start to its retirement. A folded branch retires
as its own record and contributes 0 (p. 4-3 note; Table 4-35, p. 4-5).

Every base time is the printed Chapter 4 value under the four assumptions of
p. 4-1: instruction fetch in the instruction cache/prefetch buffer, only the
stack-offset, immediate, register, absolute (jumps and calls only) and
program-counter-relative addressing modes, all stack-offset accesses captured
in the stack cache, and no data hazards. Under those assumptions no delay row
from Tables 4-37 to 4-40 is added. The images execute with CONFIG = 0 (caches
disabled) and several contain back-to-back dependent stack words, so the cycle
contract is a deliberate p. 4-1 abstraction, not a model of those images' cache
traffic. Section 4.2 admits a data hazard but Chapter 4 prints no hazard
penalty row, so no number is invented for one.

The first record is measured from the core's start, and the same p. 4-1
assumption is applied there: the first instruction is available when the core
starts, so its `cyc` is its base time (1 in all six programs). No Table 4-37
row—including "EU pipeline empty" = 2 (p. 4-6), a section 4.2 fetch delay—is
added; the branch refill cost this contract does charge is the printed
Table 4-35 value.

| mnemonic/form in these images | `cyc` | printed source |
|---|---|---|
| `MOV`, `ADD`, `ADD3`, `SUB`, `CMPEQ`, `CMPGT`, `NOP` | 1 | Table 4-32 (p. 4-3); its `CMP` row is the manual's only timing for the compares (timing_tables.md §6 item 3) |
| `CALL` | 1 | Table 4-32 (p. 4-3) |
| `RETURN` | 2 | Table 4-32 (p. 4-3); always indirect, no indirection delay (p. 4-3 note) |
| `POPN` | 2 | Table 4-32 (p. 4-3) |
| `JMP`, unfolded | 1 | Table 4-32 prints min 0/max 1; the p. 4-3 note gives 0 folded / 1 unfolded |
| `JMP`, folded | 0 | p. 4-3 note (no `JMP` folds in these images) |
| conditional jump | 0, 1, 2 or 3 | Table 4-35 (p. 4-5), by prediction, fold and distance from the compare |
| `ENTER` | 1 + (Q·E) | Table 4-36 (p. 4-5) |
| unimplemented opcode | 7 + A | Table 4-36 (p. 4-5) |

### Named memory parameters (model choices, not printed values)

p. 4-2 defines `A`, `D` and `Q` as memory access times for single-, double- and
quad-word accesses but prints no numeric value for any of them. The traces
therefore adopt, and label as choices:

| parameter | value | why |
|---|---|---|
| `A_CYC` | 1 | the model's memory is a single-cycle 32-bit-word BRAM: one core clock per word access |
| `D_CYC` | 2 | two 32-bit words |
| `Q_CYC` | 4 | four 32-bit words |

Only `A` (006's trap row) and `Q` (004's flushing `ENTER`) enter these traces;
`D` is fixed for completeness. `E` in `1 + (Q·E)` is read as the number of
16-byte blocks the pp. 3-19/3-20 `ENTER` flush loop moves. The loop writes a
whole block (`memory[MSP-16]` … `memory[MSP-4]`) and does `MSP-=16` once per
iteration, so a distance that is not a multiple of 16 bytes rounds up to a
whole block. A stack-offset `ENTER` whose `MSP - target <= SCSIZE` (256 bytes)
moves no block, so `E = 0` and the row costs 1: that is 003 L03 and 004 L02.
004 L04 is the immediate `ENTER`, which flushes `MSP = 0x180` down to
`SHAD = 0x100`; `0x80 = 128` bytes is 8 whole blocks, so `1 + 4·8 = 33`. The
manual never states the unit of `E` (timing_tables.md §6 item 8); this is the
reading forced by the printed flush loop, recorded as a choice.

Branch rows: Table 4-35 prices a *correctly predicted folded* conditional jump
at 0 and a *correctly predicted unfolded* one at 1. For an incorrect
prediction it prints 3, 2 and 1 for a jump immediately, one instruction and two
instructions after the compare, and 1 (unfolded) or 0 (folded) at four or
more. It prints **no folded row for an incorrect prediction 1–3 instructions
after compare** (timing_tables.md §6 item 9), so a folded mispredict in that
window cannot be priced from the table. 005 L03 is that case — `JMPTN`
immediately after `CMPEQ`, predicted N but taken — and carries the table's only
printed cost for it, 3. That 3 is the flush/refill charged to the branch's
retirement interval; the folded branch's own execution remains 0 (p. 4-3).

Totals: 001 = 8, 002 = 8, 003 = 7, 004 = 40, 005 = 11, 006 = 11 cycles.

## Pre-state assumed by every run

Identical for all six programs -- and for every later golden except
`017`, which runs with **PSW `0x00008600`** (user level, user
little-endian data, CSP = SP) because the byte order it pins is selected
by that PSW (pp. 1-3, 1-4); `017.md` states its own pre-state and the
harnesses pass it (`sem/hobbit_sem.py --psw 0x8600`,
`bsv/run_golden.sh 017`).  `023` is derived, and run on `sem/`, with this
pre-state, but the *core* runs it with PSW `0x00010200` (V = 1) and MMU
tables that map only page 0, so that a wrong-path read faults
(`023.md` "Pre-state"; `bsv/run_golden.sh 023` builds that harness); its
architectural trace is the same either way. Reset leaves SP and MSP undefined and PSW
= 0 (p. 1-35, p. 1-36), and PSW bit 9 = 0 would make the *ISP* the CSP
(Table 1-8 sheet 2, p. 1-15); the traces therefore need an explicit pre-state,
and this is it:

| register | value | authority |
|---|---|---|
| PC | `0x00000000` | execution starts at physical address 0 (p. 1-36) |
| PSW | `0x00000200` | bit 9 = 1: SP is the CSP (Table 1-8 sheet 2, p. 1-15); all other bits 0 — kernel level, physical addressing, IPL 0, both trace bits 0, V/C/F 0 |
| CONFIG | `0x00000000` | reset value: stack cache, decoded-instruction cache and prefetch buffer disabled, demand prefetching, PC extension 0, big-endian kernel data (p. 1-36, Table 1-2 pp. 1-9, 1-10) |
| SP | `0x00000100` | 32-bit stack pointer, low 4 bits do not exist (p. 1-17) |
| MSP | `0x00000180` | maximum stack pointer, `SP <= MSP <= SP+256` (p. 1-13) |
| SHAD | `0x00000100` | equal to SP, as p. 1-15 requires after a direct write of PSW bit 9 |
| ISP | `0x00000200` | interrupt stack pointer, quad-aligned (p. 1-12); never used |
| VB | `0x00000000` | vector base (p. 1-20); read only after the last line of `006` has retired |
| STB, FAULT, TIMER1, TIMER2 | `0x00000000` | reset values; unused |
| memory | the image at address 0, `0x00000000` everywhere else | see "Memory" |

Every trace keeps PSW bit 9 = 1 for its whole run, so `sp` in the HRI line
is the `SP` control register (p. 1-17) and is the CSP of every instruction;
no line of any trace runs with the ISP as CSP (`CSP = ISP` behaviour — CATCH
is a no-op, ENTER/POPN/RETURN leave MSP alone, pp. 3-10, 3-20, 3-38, 3-40 —
is deliberately outside this test set).

## The command shape

The parent's single-core Bluesim harness is `hobbit/bsv/sim_golden`, a wrapper
in the style of `hobbit/bsv/run_smoke.sh` (which elaborates with
`bsc -sim -g mkHobbitSmoke -u HobbitSmoke.bsv` and runs the result). The
wrapper takes one argument, the three-digit stem, and is invoked exactly as:

```
hobbit/bsv/sim_golden NNN
```

and each run is compared with its golden trace:

```
hobbit/bsv/sim_golden 001 > /tmp/001.out
diff -u hobbit/tests/golden/001.trace /tmp/001.out
```

The wrapper may build one elaborated testbench per stem, because a Bluesim
executable's command line belongs to the simulator and the BSV `Main` module
cannot read it: the image is selected at elaboration time, and everything the
golden data depends on is the pre-state, the standard output and the stop
rules, not how the image reaches the model. For stem `NNN` the run must:

1. load `hobbit/tests/golden/NNN.hex` in the fixed image format above at
   address 0 — the parcel at an even address in bits 31:16 of the word at that
   address — and nothing else;
2. set the pre-state of the table above (those values are the defaults; if the
   harness exposes `-sp`/`-msp`/`-psw` overrides, they must default to
   `0x00000100`, `0x00000180` and `0x00000200`) and start with PC = 0;
3. leave standard output exactly the HRI lines, one per retired instruction,
   in program order, each newline-terminated, with no banner, no timing or
   statistics lines and no trailing blank line — anything else fails the
   `diff`;
4. stop by the two stop rules below.

## Stop rules

1. A run ends immediately after retiring an instruction whose line carries
   `trap=1`. Only `006` reaches this, and its `PC = *(VB+12)` fetch (p. 1-39)
   is deliberately outside the trace.
2. Otherwise a run ends when the next PC would be the length of the image in
   bytes. Every program except `006` ends its last instruction exactly on the
   last parcel of its image, so no run ever fetches a parcel the image does
   not contain.

## Memory

The model's memory is zero-initialised and covers at least 16 Kbytes
(4096 words, addresses `0x00000000`-`0x00000fff`); every address any of the
six programs touches lies in `0x00000100`-`0x00000108`. Every stack word a
program reads is one it wrote earlier in the same run, so no trace depends on
the initial content of memory — only on the model being able to store to and
load from those addresses.

## Conventions where the fixed formats are silent

These are part of `tests/golden`'s contract because the fixed formats do not
say; they are recorded here so a mismatch is a decision, not an accident.

* **`mask` byte order.** Bit *i* of the mask denotes the byte at `addr+i`.
  Every write in these traces stores a whole word, so the mask is `0f`
  everywhere `we=1`.
* **No write.** When an instruction performs no architectural write, the line
  is `we=0 addr=00000000 data=00000000 mask=00`.
* **`sp` is SP.** PSW bit 9 = 1 throughout, so `sp` is the SP register; the
  traces would be meaningless with PSW bit 9 = 0.
* **Cache traffic is not architectural.** Stack-cache write-back and refill
  between memory and the cache are not reported; the write field names the
  instruction's own destination store. Since CONFIG bit 18 = 0 disables the
  stack cache in the pre-state, no line depends on cache policy either way.
* **`trap=1` line.** The unimplemented-instruction sequence stores the PC of
  the unimplemented opcode at CSP (p. 1-39). That store is architectural, so
  the trap line reports it (`we=1`, `addr` = CSP, `data` = the PC of the
  opcode) and nothing else. The following `PC = *(VB+12)` fetch is outside
  every trace.
* **PSW side effects.** PSW.C, PSW.V, PSW.F and PSW.E results are
  architectural (pp. 3-5, 3-13, 3-20, 3-43) but the fixed line has no field
  for them. Each `.md` states them, so a later, wider record can check them.

## Programs

| file | instructions | retired | covers |
|---|---|---|---|
| `001` | 8 | 8 | one-parcel `MOV` in its `wai5` immediate and `stk5, stk5` forms, with `stk5` scaled by four (pp. 3-32, 1-22): a store into the accumulator at `CSP+4`, an ordinary move out of it, an `ADD` whose destination receives that value, then `ADD3` writing `CSP+4` again (p. 1-7, p. 3-5) |
| `002` | 8 | 8 | three-parcel (`gen16`) `ADD` and `SUB` with 16-bit immediate and stack-offset operands (p. 1-23, Table 1-18 p. 1-24, pp. 3-5, 3-43) |
| `003` | 6 | 6 | a `CALL`/`RETURN` pair: one-parcel `CALL pcrel10` and three-parcel `RETURN stk32` (p. 3-9, p. 3-40), plus one-parcel `JMP` and `ENTER R-16` (p. 3-19) |
| `004` | 6 | 6 | `ENTER`/`POPN` in the one-parcel stack class and the three-parcel `word32`/`stk32` forms, with both documented MSP updates (pp. 3-19, 3-20, 3-38) |
| `005` | 12 | 10 | `CMPEQ` and `CMPGT` setting PSW.F to 1 and then to 0 (p. 3-13), then the same `JMPTN` **taken** with F = 1 and **not taken** with F = 0 (p. 3-28) — the `Y`/`N` letter is only the prediction — plus one accumulator write |
| `006` | 4 | 4 | `FLUSHD`, an opcode that is not implemented in hardware, taking the unimplemented-instruction trap with `trap=1` and saving its own PC 0x00000006 at CSP (p. 3-22, p. 1-39, Table 1-7 p. 1-14, Table 1-17 p. 1-22) |

Between them: one- and three-parcel fetches and execution, immediate and stack
`MOV`, dyadic `ADD`/`SUB`, `CALL`/`RETURN`, `ENTER`/`POPN`, taken and
not-taken conditional jumps, the `CSP+4` accumulator rule, and one
unimplemented opcode.

Deliberately not covered, because the first milestone's decoder does not model
them and the manual leaves their spelling or extension ambiguous: five-parcel
forms, the `CPU` register escape (`%name` spelling is unstated, inventory
section 7.3 item 15), three-parcel PC-relative branch operands, absolute
addresses above `0x0000ffff` (CONFIG bit 17), the interlocked `ADDI`/`ANDI`/
`ORI` (two architectural writes per instruction, but the fixed line carries
one), interrupts, exceptions other than the unimplemented-instruction trap,
the MMU, and any run with `CSP = ISP`.

Later goldens took some of these in (each `.md` says what it covers and
what found it): `009` `ADDI` and `022` `ORI`/`ANDI` (the accumulator's
second write made visible by a following `MOV R4, R12`, and R4 as the
destination), `023` a wrong-path operand read that faults under the MMU
(the core-only harness above).

## What `check_golden.py` enforces

Run `python3 hobbit/tests/golden/check_golden.py`; it exits non-zero and
names every violation. It does not simulate anything. Each check exists to
catch a named defect:

| check | the defect it catches |
|---|---|
| every `.hex` line is 8 lowercase hex digits | uppercase or short words, a stray separator or a comment inside an image |
| every `.trace` line begins `HRI ` and matches the fixed field list, including the trailing `cyc=<decimal>` | a line still on the retired `RVFI ` prefix (reported as a format error, never skipped), a missing or extra field, a wrong-width field, or a missing/hex/signed cycle count |
| `cyc=0` appears only on a branch | a zero-cycle ALU, store, stack or niladic record, which no printed row supports; only a folded branch is free (p. 4-3 note, Table 4-35 p. 4-5) |
| the first trace line has `pc=0000` | an image that does not start executing at its entry |
| `insn` bits 31:16 equal the image parcel at `pc` | a trace line that does not describe the instruction actually stored there |
| parcel count from bit 15 / bits 15:14 matches the `insn` field (1-parcel lines carry `insn` low half `0000`; 3-parcel lines carry the second parcel) | a one-parcel instruction written with a stale second parcel, or a truncated 3-/5-parcel instruction |
| every instruction fits inside the image | a trace that fetches past the end of its own `.hex` |
| `sp`/`msp` after-line *n* equal before-line *n+1* | a dropped or duplicated state change in one line |
| SP and MSP low 4 bits are zero | a state transition that leaves a non-existent pointer bit set (p. 1-17) |
| `we=0` implies `addr=data=mask=0`; `mask` uses only its low nibble | a phantom write reported for a no-write instruction |
| at most one `trap=1` line, and it is the last | a trap line in the middle of a trace, or a second unimplemented opcode |
| the next line's `pc` is either `pc+2*parcels` or a documented control transfer | a PC sequence that no instruction in this set can produce |
| the last line without `trap=1` ends exactly at the image end | an image whose last instruction leaves the model fetching a padding parcel, so "the run ends" would never happen |
| every `.md` has exactly one `Lnn.` entry per trace line, numbered in order, quoting that line verbatim, and citing a printed page or table | documentation that has drifted from the trace, or a line with no manual justification |
| every `Lnn.` entry carries `Cycles: N — ...` and N equals the `cyc` in the line it quotes | a cycle figure that drifted from the trace, or a record whose time was never justified in place |
