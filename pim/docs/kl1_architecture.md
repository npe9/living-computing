# The abstract KL1 machine and the PIM macro-call

Source note for the PIM/m reproduction. Two primary ICOT technical reports
define the KL1 execution model and the instruction mechanism designed for the
PIM processing element. Citations are to **printed page numbers**, not PDF
indices.

| Local file | Document | PDF pages | Printed pages |
|---|---|---|---|
| `docs/nonlocal/tr0246.pdf` | Y. Kimura and T. Chikayama, *An Abstract KL1 Machine and Its Instruction Set*, ICOT TR-246, June 1987 | 11 (cover + 10) | 1–10 |
| `docs/nonlocal/tr0389.pdf` | T. Shinogi, K. Kumon, A. Hattori, A. Goto, Y. Kimura, T. Chikayama, *Macro-call Instruction for the Efficient KL1 Implementation on PIM*, ICOT TR-389, June 1988 | 18 (cover + 17) | 1–17 |

Both are scanned images with no text layer; the content below was transcribed
from the page images. The PDF page is the printed page plus one in each file.

## 1. What the abstract machine is

TR-246 describes an *abstract* KL1 machine: a register machine with tagged
data whose instruction set is meant to be mapped onto general-purpose machines
as well as onto PIM and Multi-PSI, not onto one particular piece of hardware
(TR-246 p. 1). KL1 is the parallel logic programming language based on GHC;
KL1 programs are compiled to KL1-B and executed on the target machine
(TR-246 p. 1).

Execution is goal reduction over guarded Horn clauses. A goal is reduced in
parallel with other goals; a clause whose head unification and guard execution
succeed is selected, its body goals are executed, and unification that would
require instantiating a variable suspends (TR-246 p. 1). Reduction of `p(X)`
against `q(X)` leaves `q(X)` suspended until `X` is instantiated; a goal in
that state is a *suspended goal* (TR-246 p. 2).

The sequential implementation keeps a *ready queue* of goal records and
performs, per reduction: candidate-clause testing by head unification and guard
execution; body execution as *active unification* plus *goal body fork*; and
suspension/resumption by linking a goal record to the variable that caused the
suspension (non-busy waiting) (TR-246 pp. 2–3). The current implementation
maintains the ready queue as a stack rather than a queue (TR-246 p. 3).

## 2. Data representation

Tags are symbolic, not bit fields. "The tag can have one of the following
values" (TR-246 p. 3):

| Tag | Meaning (TR-246 p. 3) |
|---|---|
| `UREF` | uninstantiated variable; the value has no meaning |
| `REF` | reference pointer to a variable cell, either uninstantiated or hooked |
| `INT` | integer; the value is the integer itself |
| `ATOM` | symbolic atom; the value is an atom identifier |
| `LIST` | list cell; the value points to consecutive two words for car and cdr |

There is no separate structure tag: structures are built from list cells
(TR-246 p. 3). TR-246 gives **no word width and no bit assignment** for the tag;
it is an abstract machine description.

TR-389 supplies the concrete PIM representation: 40-bit KL1 data (8-bit tag and
32-bit data) placed in aligned 64-bit words in the PIM memory system, with the
MRB assigned in the tag part; instructions and some data such as strings or
floating point numbers use the full 64 bits (TR-389 p. 9). Figure 7 on the same
page draws the 64-bit word with a tag field marked from bit 63 down to 55, a
`free` field, and data in bits 31–0 — which does not agree with the text's
8-bit tag; see §8.

MRB (multiple reference bit) is one bit in a pointer recording whether the
pointed object may be referred to by other objects (`on_MRB`) or not
(`off_MRB`); an `off_MRB` area may be reclaimed after its contents are read,
giving incremental garbage collection inside dereference (TR-389 pp. 4–5).

## 3. Records and memory model

A **goal record** has fields: `Narg`, `argreg1` … `argregNarg-1`, the code
address of the predicate, and `next goal record` (TR-246 p. 3). A **suspension
record** has `next suspension record` and `suspension flag record`; a
**suspension flag record** has `goal record` and `suspension count` (TR-246
p. 3). A **suspension stack** is a marking stack that preserves the variables
which may require suspension; it is cleared when a clause is selected or
suspension processing completes (TR-246 p. 3).

Memory is partitioned by allocation discipline: goal records and suspension
records live in memory areas maintained by corresponding free lists; variable
cells are allocated in the garbage-collected heap; the suspension stack is
allocated at a fixed memory area (TR-246 p. 4).

KL1-B keeps the same shape: a goal-record is an argument list plus a pointer to
the compiled code for the predicate name plus control information; arguments
are atomic values or pointers to variables/structures in the heap; goals are
ready (RG), suspended (SG), or current (CG), and ready records are linked into a
ready-goal-stack (TR-389 p. 3).

## 4. Registers

TR-246's abstract register set (TR-246 p. 4):

| Register | Role |
|---|---|
| `PC` | program counter |
| `Carg` | number of arguments of the current goal |
| `argreg1` … `argregCarg-1` | the arguments |
| `SR` | structure pointer used for structure unification |
| `HP` | heap top pointer |
| `SSP` | suspension stack top pointer |
| `RQFP` | pointer to ready queue head |
| `CRFP` | pointer to free goal record list |
| `SRFP` | pointer to free suspension record list |
| `SSFP` | pointer to free suspension flag record list |
| `write_mode` | mode flag used for structure unification |

There are no hardware registers for KL1 variables in this model; all goal
arguments are temporary and may be destroyed, whereas WAM classifies variables
as temporary or permanent (TR-246 p. 10).

TR-389's PIM processing element has 32 general-purpose registers and 6
dedicated registers; each general-purpose register is an 8-bit tag plus 32-bit
data; dedicated registers are discrete LSI registers and include a condition
code register, an interrupt request register, and a tag mask register; most
instructions carry a 6-bit register specifier (TR-389 p. 9). The instruction
set can use 16 *indirect* registers in a register operand (TR-389 p. 10).

## 5. Instruction set and formats

TR-246 groups the instruction set into six classes (TR-246 p. 4): passive
unification, guard-part built-in predicates, active unification, goal
manipulation, argument preparation, and suspension. Instructions are printed as
mnemonics with register/constant/label operands; **no opcode or bit layout is
given** (TR-246 pp. 5–8). The design rules are stated on p. 4: passive-part
instructions carry a branch label for the code to test next after suspension;
a dereferenced value is written back where the reference pointer was;
argument registers are not destroyed before a clause is selected; guard
built-ins never suspend; one body goal runs tail-recursively and the rest are
linked to the ready queue; suspension processing is explicitly generated.

**Passive unification** (TR-246 p. 5): `wait_variable Xj, Ai`,
`wait_value Xj, Ai, Label`, `wait_constant C, Ai, Label`, `wait_list Ai, Label`,
`read_variable Xj, Label`, `read_value Xj, Label`, `read_constant C, Label`.
`Ai` is an argument register and `Xj` a temporary work register; `Label` is the
branch address taken on failure or suspension (TR-246 p. 5).

**Guard built-ins** (TR-246 p. 5): `integer Ai, Label`, `equal Ai, Aj, Label`,
`greater Ai, Aj, Label`, `add Ai, Aj, Ak`, `multiply Ai, Aj, Ak`,
`modulo Ai, Aj, Ak`. Their inputs must already be instantiated, so they cannot
suspend; `integer`/`wait` instructions perform the type and instantiation check
(TR-246 p. 5).

**Active unification** (TR-246 p. 6): `get_variable Xj, Ai`, `get_value Xj, Ai`,
`get_constant C, Ai`, `get_list Ai`, `unify_variable Xj`, `unify_value Xj`,
`unify_constant C`. These never suspend; resuming goals hooked on a variable is
done on the spot (TR-246 p. 6).

**Goal manipulation** (TR-246 p. 6): `create_goal Code, Arity`,
`enqueue_goal Goal/Arity`, `execute Code`, `proceed`. `create_goal` and
`enqueue_goal` are always used as a pair; `execute` is used for final recursive
execution; `proceed` pops the next goal record from the ready queue, loads its
arguments, restores the environment, and jumps (TR-246 p. 6).

**Argument preparation** (TR-246 p. 7): `put_variable Xj, Ai`,
`put_value Xj, Ai`, `put_constant C, Ai`, `set_variable Xj, Gi`,
`set_value Xj, Gi`, `set_constant C, Gi`, `put_list Ai`, `set_list Gi`,
`write_variable Ai`, `write_value Ai`, `write_constant C`. `Set_*` writes into
a goal record's argument save area, `Put_*` rearranges registers before tail
recursion, `Write_*` stores a structure element and always runs in write mode
(TR-246 p. 7).

**Suspension** (TR-246 p. 7): `suspend Goal/Arity`, which drains the suspension
stack, hooks the goal record onto each variable, and allocates a suspension flag
record with count 1 if the goal is not already hooked.

**Indexing** (TR-246 pp. 8–9): `switch_on_term Ai, Lc, Ll, Lv` selects the
clause group by tag (constant, list, structure, uninstantiated) and jumps to a
failure label if none matches; the compiler orders clauses so that same-name,
same-type clauses are contiguous. The report's footnote on p. 9 identifies this
as the read-mode unification of WAM. A specialized active-unification
instruction `get_list_value(Xj, Ai)` is also introduced (TR-246 p. 8).

TR-389 writes KL1-B instructions with a `B` suffix (`wait_constant_B`,
`get_list_value_B`, `proceed_B`, `suspend_B`, …) and cites references [2, 6]
for an explanation of each instruction (TR-389 p. 3, footnote 1–2).

## 6. The macro-call instruction

### Motivation

KL1-B is the virtual machine language between KL1 and the parallel inference
machine hardware, the analogue of WAM for Prolog; it "represents the abstract
architecture of the parallel inference machine" (TR-389 p. 2). Three KL1
properties defeat conventional machines: polymorphic unification over
dynamically built linked structures, a small execution context switched
frequently by synchronisation, and single assignment needing incremental
garbage collection (TR-389 p. 2).

Emulator experiments found that most KL1-B instructions contain a run-time data
type check and that the instruction's action varies with the argument type even
though only part of the instruction is selected by the check; expanding KL1-B
into plain RISC code therefore does not implement it efficiently (TR-389 p. 2).
Software simulation also found that naive expansion inflates static code enough
to raise common-bus traffic and seriously degrade a PIM cluster (TR-389 p. 6).
The alternative, a microprogrammed HLIC, wastes dispatch because many type
checks fall through to the next KL1-B instruction and some KL1-B instructions
are simple register moves (TR-389 p. 6).

### Mechanism

Each processing element has two instruction streams, *external* and *internal*;
external instructions are the compiled user program and internal instructions
form macro-bodies in the internal instruction memory (IM), written by system
designers like an HLIC microprogram (TR-389 pp. 1, 6). The two sets share most
RISC-like instructions, including KL1-specific ones (TR-389 p. 7).

A macro-call instruction "first test[s] the data type of a register given as its
operand, then will or will not invoke its macro-body in the internal instruction
memory (IM) depending on the result" (TR-389 p. 6). Its form is (TR-389 p. 7):

```
MacroCall if cond, Address with reg0, reg1/immed1, reg2/immed2, ..., regn/immedn
```

`Address` is the entry address in the IM; `reg/immed` is a register number or a
short immediate constant; `cond` is one of `And`, `NotAnd`, `Or`, `NotOr`,
`Xor`, `NotXor`, `XorMask`, `NotXorMask` (TR-389 p. 7). The condition is a
logical operation between the tag of `reg0` and the tag of `reg1` or an
immediate tag; `XorMask`/`NotXorMask` additionally use the tag mask register,
and some macro-calls carry an immediate tag mask to avoid updating that
register (TR-389 p. 7). Hardware flags such as the ALU condition code or an
interrupt flag are readable as the tag of dedicated registers and can therefore
be macro-call conditions (TR-389 p. 7).

The PE has only a **two-way** tag condition in macro-calls and tag branches,
not a hardware multi-way branch, because multi-way branching is costly in a
pipelined processor and run-time branches are biased (TR-389 p. 7).

Internal instructions address the macro-call's operands through *indirect
registers*: each indirect register corresponds to an operand position, and one
kind yields the operand as an immediate value while the other yields the
contents of the register named in the macro-call operand (TR-389 p. 7). This
lets one macro-body serve several KL1-B instructions; the report shows
`wait_list_B` reused for a `VECT4` test by changing the immediate tag
(TR-389 p. 13). Each internal instruction has an `eoi` bit marking the exit
point from the macro-body, so a body can finish at any non-branch instruction
without overhead (TR-389 pp. 8, 12).

### Pipeline behaviour

The PE issues one external instruction per machine cycle through a four-stage
`D A T B` pipeline; internal instructions add stages `S` (set IM address) and
`C` (fetch internal instruction) before the same `D A T B` (TR-389 p. 11).
Target cycle time is 50 ns (TR-389 p. 11). Ordinary branch targets are fetched
at stage `B`, costing up to three extra cycles, whereas a macro-call starts the
IM fetch at stage `D` and tests its condition at stage `A`, so a taken
macro-call costs only one extra cycle; delayed macro-call variants exist
(TR-389 p. 11).

### Worked example

`wait_list_B` tests the tag of its argument: if `LIST`, the instruction
finishes; otherwise the type selects the next operation (TR-389 p. 12). Its
macro-call is `MacroCall wait_type (if) NotXorMask (with) ai, LIST, acp`, where
`acp` is an alternative clause pointer for the `Label` operand (TR-389 p. 12).
The macro-body (Figure 10, TR-389 p. 13) uses indirect registers `r0`, `r2`,
and `edi`, tests the tag, dereferences on `REF`, and handles unbound and MRB
cases before jumping out to `acp`. The append example (Figure 11, TR-389 p. 14)
compiles ten KL1-B instructions into six macro-calls plus eight RISC-like
instructions, of which three macro-calls actually enter their bodies; the
report estimates over 600K RPS for that program including MRB collection
(TR-389 p. 13).

### PIM instruction set around the macro-call

The appendix lists operand notation and principal instructions (TR-389
pp. 16–17): operand fields include 8/32/40-bit immediates, an 8-bit immediate
tag, 8/16/24/32-bit address offsets, an 8-bit return-address offset, and a
16-bit internal memory address. Branch instructions are external, internal, and
macro-call; macro-call forms are `MacroCallCond Rt1, Rt2/imtg, [R3,R4,R5,] iaddr`,
its delayed form, unconditional `MacroCall R1, [R2,R3,R4,R5,] iaddr`, and the
delayed form (TR-389 p. 16). ALU instructions operate on 32-bit data, 8-bit
tags, or 40-bit values; memory instructions transfer 8, 16, 32, 32-plus-tag, or
64 bits, include `WriteTag`, and provide `PUSH`/`POP` for free lists plus
`MRBRead` and `DEREF` for MRB maintenance (TR-389 pp. 10, 17).

## 7. Relationship to PIM/m and PIM/p

Neither document names PIM/m or PIM/p. TR-246 (1987) refers only to "the PIM"
and Multi-PSI, and says the abstract machine is intended to be mapped onto
general-purpose machines as well as PIM and Multi-PSI (TR-246 p. 1). TR-389
(1988) describes "a parallel inference machine prototype, PIM", planned to
include 128 processor elements, with eight PEs per cluster over a shared memory
and common bus, 16 clusters, and an inter-cluster hypercube network (TR-389
pp. 1, 8).

[INFERENCE] The 1988 PIM in TR-389 is the pre-1992 prototype from which the
PIM/m and PIM/p implementations descend; the two reports do not establish which
1992 variant, if either, retained the macro-call and internal-instruction
design. Treat any PIM/m- or PIM/p-specific claim as unverified from these
sources.

The concrete numbers in TR-389 differ from the PIM/m model's own cited
architecture: TR-389 has 32 general-purpose plus 6 dedicated registers and a
four-stage `D A T B` pipeline (TR-389 pp. 9, 11), while `bsv/PimTypes.bsv`
records an An/Xn register file, WR control registers, and five stages
`D A R S E` for PIM/m from the 1992 paper. The two must not be merged.

## 8. Model implications

To execute KL1-B on the PIM/m Bluespec model, the following are required beyond
the current smoke-test instruction set:

1. **Tagged 40-bit word with MRB in the tag.** Already present in
   `bsv/PimTypes.bsv`, consistent with TR-389 p. 9. The tag set should
   distinguish `UREF` from `REF` (TR-246 p. 3); the model's `tagVar`/`tagRef`
   split is the right shape, but its numeric values remain model-defined.
2. **KL1 machine registers.** `HP`, `SR`, `SSP`, `write_mode`, `Carg`/argument
   registers, and the four free-list pointers `RQFP`, `CRFP`, `SRFP`, `SSFP`
   (TR-246 p. 4), plus a tag mask register for masked macro-call conditions
   (TR-389 p. 7). The model's register space is An/Xn, WR control registers,
   `SP`/`PC`, and E-stage temporaries; none of the KL1 pointers above exist.
3. **Goal and suspension records.** The goal record (`Narg`, argument
   registers, code address, next pointer) and the suspension/flag records with
   their free lists (TR-246 p. 3) are needed before
   any KL1-B instruction can run; the model has no goal-record allocator.
4. **Macro-call dispatch.** An external instruction that tests a tag condition
   and conditionally enters an IM macro-body, with 16 indirect registers
   addressed by operand position and an `eoi` exit bit (TR-389 pp. 7–8, 10).
   The model has a writable control store but no documented macro-call field
   layout or indirect-register numbering.
5. **Two-way tag branch.** TR-389 restricts the PE to two-way tag conditions
   (p. 7), whereas `PimTypes.bsv` records two-, three-, and multi-way tag-check
   jumps for PIM/m. This is an unresolved architectural conflict, not a detail
   to paper over.
6. **Dereference with MRB and free lists.** `DEREF`/`MRBRead` and `PUSH`/`POP`
   (TR-389 pp. 10–11) are required for KL1-B's embedded incremental collection;
   the model has only a simple `deref` and MRB set/clear.
7. **Memory widths.** 8/16/32-bit, 32-bit-plus-tag, and 64-bit transfers
   (TR-389 p. 10) are needed for atoms, tagged cells, and floating point/string
   data.

What remains unknown:

- **Instruction encodings are in the PIMOS assembler, not in TR-246 or
  TR-389.** TR-246 gives mnemonics only; TR-389 gives operand notation
  (p. 16) and instruction lengths of four, six, or eight bytes (p. 11)
  but no field positions. The PIMOS source archive
  (`docs/nonlocal/pimos.tar.Z`) supplies the actual table:
  `pimos/src/library/assembler/inst_tab.kl1` lists 263 encodings as
  `t(mnemonic, Tag, Op, Type)` clauses, and `klb_opr.kl1` gives the
  operand packing rules. The full transcription is in
  `docs/kl1_encoding.md`. The encoding is PIMOS-derived, not printed in
  TR-246 or TR-389, and the tag word plus data word is six bytes, which
  does not reconcile with TR-389's four/eight-byte counts without a
  surviving listing.
- **Tag bit layout.** The text says an 8-bit tag (TR-389 p. 9) while Figure 7 on
  the same page marks the tag field at bits 63–55 with bits 54–32 `free`. The
  MRB's position inside the tag is not stated.
- **Indirect-register numbering and macro-call operand encoding** are not
  printed; only "16 indirect registers" and "each corresponds to an operand
  position" (TR-389 pp. 7, 10).
- **Macro-body contents.** Only `wait_list_B` is printed (TR-389 p. 13); there
  is no complete internal-instruction or microcode listing.
- **Complete KL1-B instruction set.** TR-389 defers to references [2, 6] for
  the full set (p. 3). The corpus does contain a complete set: the PIMOS
  assembler's `inst_tab.kl1` lists 263 encodings, and its `p(...)` operand
  clauses cover the types those entries name. What is still absent is a
  printed KL1-B manual with prose semantics for each mnemonic; the table
  gives encodings and operand types, not per-instruction descriptions.
- **Inter-cluster packet format and routing** are not given; TR-389 only names
  the multiple-hypercube network (p. 8).
- **Whether PIM/m retains this design.** Neither report mentions PIM/m or
  PIM/p, so the macro-call/IM mechanism cannot be attributed to either 1992
  variant without a further source.

Consequently the first KL1 workload on this model can be assembled with the
PIMOS assembler's own table: `inst_tab.kl1` supplies the encodings and
`klb_opr.kl1` the operand packing. The result is PIMOS-derived, not printed in
TR-246 or TR-389, and it must not be described as historical PIM/m execution
until a PIM/m-specific source confirms the same encodings.
