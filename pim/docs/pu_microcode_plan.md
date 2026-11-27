# Executing ICOT's held KL1 microprogram: the PU plan (rungs U1-U5)

Started 2026-11-26. The owner: "Recreate the microcode rather than make
something fake." The microcode does not have to be recreated: it is
held. `PMPSI.DIR/pimm.MEkbn` (in `docs/nonlocal/psdpim.tar.Z`, third-party
binary, kept out of git) carries the Pseudo PIM/m KL1 microprogram
(image 2, `0x6800` microinstructions) and its decode table
(`pseudo_pimm_microcode.md` sections 1-3). TM-862 says the PSI-III and
the PIM/m PE are one PU chip (`environment_audit.md` area G), so this is
the microprogram of PIM/m's own processor. Today nothing executes it:
the core (`bsv/PimmStages.bsv` `mkPimmExec`) and the reference
(`ref/pimm/pimm.py`) interpret KL1-B directly, by hand.

The goal of the rungs below is that the PU executes the held words and
the hand-written interpreter goes away.

## Three targets

One chip does not mean one machine. TM-862's "the same PU" says nothing
about the memory controller, the peripherals, the I/O bus or the native
firmware around the chip, and those are what differ:

1. **PSI-III with `syspsi`** (the ESP/KL0 control store, image 1 and the
   upper store; `sysidat`, `sysinit`): the workstation SIMPOS runs on.
   Rung U5.
2. **Pseudo PIM/m**: `pimm.MEkbn` (image 2, the KL1 microprogram) on
   PSI-III-compatible hardware: the PSI-III board's memory, TLB and I/O
   (thesis p.146). **This is the first target**, because it is the
   firmware that is held. Rungs U1-U3.
3. **Native PIM/m PE**: the same KL1 microprogram on the PIM/m board
   (16 Mw local memory, NU to the mesh, SCSI to the FEP; `M92`
   pp.426-427). No native firmware image is held; where the Pseudo
   PIM/m's board differs (the table under "Pseudo PIM/m against a PIM/m
   PE"), what the native firmware did is UNKNOWN, not assumed equal.
   Rung U4 and the multi-PE sub-rung.

## Evidence labels

Every recovered feature (a field value's meaning, a register's role, a
routine's behaviour) carries one label, the strongest that holds:

- **DOCUMENTED**: a primary source states it (thesis, `M92`, TR/TM, the
  `rassy` tables), cited by page.
- **CORROBORATED**: two independent sources agree (a document and a
  whole-image measurement, `asm/mekbn.py --check` or `ref/pu/measure.py`).
- **INFERRED**: fitted from consistency with `pimm.py` or with the held
  words' use, naming the microaddress and the trace line that decided it
  (this project's earlier label INFERENCE).
- **EXECUTED**: a held routine ran under the simulator and matched the
  oracle (`ref/pu/check_pu.py`).
- **VERIFIED**: proved against a stated contract (a property over all
  inputs, not a set of cases).
- **UNKNOWN**: no source and no fit; a run that needs it stops.

Stand-ins for hardware or environment the held words do not give are
**OURS**, whatever their label. The earlier label MEASURED (a count
over the whole image, pinned by `mekbn --check` or `measure.py`) is
still used in `pseudo_pimm_microcode.md` and `ref/pu/README.md`: read
it as CORROBORATED when a document agrees and INFERRED when the count
alone decides. Where two documents disagree, both stay
as competing hypotheses until execution decides: TR-733 fig. 4 and
Nakashima Fig. 3-25 differ in the microword's field layout
(`pim_architecture.md`, the field table after line 200: TR-733 prints
ALF as 28-26 and JMPF as 25-23, AS2F at 33-32, and leaves 63 and 57
unnamed). `ref/pu/` runs Fig. 3-25's layout, the one under which
`mekbn --check`'s whole-image pins hold. The sharpest open case is bit
26: Fig. 3-25 makes it JMPF's top bit, TR-733 ALF's third bit;
`ref/pu/` uses it as the jumps' conditional bit (INFERRED, the
successor counts pinned by `ref/pu/measure.py`), which fits Fig. 3-25.
A held routine that only TR-733's layout makes run would reopen it.
Since then `asm/pu_smt.py` (Z3, `pu_microcode_inference.md` 6.3 item
1) eliminates TR-733's layout, but only jointly with the INFERRED
allocator contract (`{alloc_1cell, write_variable}` is a minimal
killing set; without alloc_1cell TR-733 survives). The thesis layout is
therefore the working one, with that dependency stated, not a settled
fact.

## The rule that holds for every rung

- **Never write a micro-routine of our own in place of a held one.** A
  routine that cannot be run is stopped at and recorded, with its
  address and the field or table that is missing.
- **What is stood in is the hardware, never the microprogram.** The
  stand-ins are the parts of the PU that are not microcoded: the D/A/R/S
  stages that the decode entry's nano-code drives (`pim_architecture.md`
  section 2; nano-code fields, Nakashima Fig. 3-22,
  `psi_microword.md` 3a), the tag-dispatch RAM (TGT, 512 entries;
  its contents are held after all, in `sysinit` at `5300`,
  `pu_microcode_inference.md` section 5), the condition multiplexer behind CNDF, and the
  memory and I/O of the board. Each stand-in is a small table, labelled.
- **Fail loud.** A field value whose meaning is not modelled, met on an
  executed path, raises with the microaddress. That is how "the first
  routine that would not run" is found, and how each INFERRED enters:
  one at a time, with the address that forced it.
- **A field rule never bends to reproduce a `pimm.py` design choice.**
  Where a fit contradicts a pin of `asm/mekbn.py --check` (which rests
  on the whole image and on `syspsi`), the fit loses.

## What "the same as `pimm.py`" can mean

`pimm.py`'s runtime layouts are this project's design ("the firmware
being lost", its header): it bump-allocates the heap, keeps the goal
being built in an `argv` array, makes `collect_value` a no-op, and lays
out goal and suspension records its own way (`asm/pimm_layout.py`). The
firmware takes cells from free lists (`R19`/`R1a`/`R1b`, section 15 of
`pseudo_pimm_microcode.md`), writes the goal being built into a record
(`R10` + argument), frees cells, and has its own record layouts
(sections 17-18). A literal memory-write trace therefore cannot match,
and the comparison is defined as:

1. **Registers.** After each KL1-B instruction the argument registers
   An (`pimm.py` `reg[i]`) must hold the same value under an address
   renaming: a bijection from firmware heap addresses to `pimm.py` heap
   addresses, built as the run goes (the first time a firmware cell
   stands where `pimm.py` has a cell, the pair is fixed; a later
   conflict is a FAIL).
2. **Heap terms.** Every cell `pimm.py` writes must be written by the
   firmware with the same tag and the renamed value (a structure cell,
   a variable cell, a binding).
3. **Projections.** `pimm.py` `argv[i]` corresponds to the firmware
   cell `R10 + i` (the goal record being built); `pimm.py` `sp`
   corresponds to `R02` (the structure pointer). Each projection is
   INFERRED and is listed with its evidence.
4. **Firmware-only writes** (free-list links, freed cells, goal record
   trailers, refill) are listed as expected differences, with the
   firmware as the authority: they are what the hand-written models do
   not do, not errors.

## Rungs

U1-U5 are the large rungs. Inside them, the owner's milestones are the
sub-rungs, in this order (not M-numbered: M is taken by the multi-PE and
window rungs):

| Sub-rung | Milestone | In rung | State (2026-11-26) |
|---|---|---|---|
| U1a | straight-line held code executes | U1 | EXECUTED (one-word and multi-word routines) |
| U1b | branches: conditional and unconditional jumps, micro call and return, COND formed and used | U1 | EXECUTED (tallied over `p.cycles` of the whole check): JMPF 0 (next), JMPF 1 end and return (unconditional, and conditional with EM bit 0), the jumps JMPF 4 and 6, the calls JMPF 5 (`615e`, a held call word) and 7, two pushes and two pops; COND formed by CNDF 9/b and used by a later word. JMPF 3 `case_branch` (S8) at `2d3f`. A CNDF-0 word leaves COND standing (EXECUTED at `put_variable` `31d6`-`31d8`). Conditional JMPF b EXECUTED since U2 (`4cc1`, not taken: `cjump_time` 'prev', INFERRED, pu_smt `execute_fast`); e and a since U2's sixth session (`2440`, `2461`, `3980`: rassy's 'if cond' / 'if not cond'), JMPF 2 (S10) as a short case_branch (`2447`), JMPF 9 as a conditional call not taken (`38b1`). Raise: conditional c, JMPF 1 EM `7fff` (S9), JMPF 1 multiway with EM bit 2 (S2b, low-bit source UNKNOWN), d/f, a taken JMPF 9, 8 outside a set-up or flag word |
| U1c | the free-list allocator `3320`-`3324` on memory | U1 | EXECUTED: called by a held call word (`scsi_init`'s `615e`) and returning to `615f`, W1c `{REF, cell}` as `pimm.py`'s `new_var`; its last-cell arm reads R05 (UNKNOWN) |
| U1-dispatch | decode-table dispatch from the instruction cell | U1 | EXECUTED: `setup.dispatch` takes class from the tag, opcode from the top byte, the start from the held table; every compared case enters through it |
| U1d | `set_variable`, `write_variable` | U1 | EXECUTED, with the marked forms |
| U2a | tagged terms: lists, vectors, constants built and read | U2 | lists and vectors built EXECUTED; a structure's elements read EXECUTED (`read_variable`, `34a0`-`34a2`, `3494`: two atoms in append, a list pointer in a standalone case, x := the element and R02 + 1 as `pimm.py`); a REF or the immediate (VECTo) element read, not run |
| U2b | tag dispatch | U2 | EXECUTED for the mechanism at `2d3f` (set-up `2d3e`, CNDF 7 EM1 `3a`, sysinit `5300` column 2, the static agent's VERIFIED column); `2ed7` and `3c61` run the same way in a probe. UNKNOWN: the other EM1 columns, the tag source of a set-up word with no ALU input (`1d3f`), and S2b. The dereference multiway set-up (thesis printed p.133: a ref / immediate / other code in TDAR bits 3-2, a KL1 four-way splitting ref by MRB) INFERRED for CNDF 7 EM1 `2d` (`pu.DEREF_SETUP`), executed for the code 'other' only (`34a1` -> `3494`); EM1 `28` is a condition, meaning UNKNOWN (`pu.COND_UNKNOWN`, untested on the path run). Since the seventh session every CNDF 7 EM1 `30`-`3f` is rassy's `case_tag_setup mdrN k` (`pu.CASE_TAG_SETUP`: the named MDR's tag, TGT column 7 - k), EXECUTED in `get_value`'s unifier for columns 0, 5, 6 and 7 (`0c0c`, `0e38`, `0c0d`, `0840`); a case_branch takes the whole byte where its base allows (`0e75`: 20 rows), and TDAR stands across a JMPF 1 word (`0802`) |
| U2c | one unification instruction | U2 | one case EXECUTED standalone (`get_atom` on an unbound variable, `3800`-`3801`, matches `pimm.py`); in a whole program since 2026-11-27 (fourth session) `get_bound_value` on an unbound variable (`3880`, append's eighth instruction: Z bound to the reused list); since the sixth session `wait_nil` on nil (`3980`, `3985`) and the start of `get_value` on a non-variable x (row 4, `38b0`-`38b3`, stop at `0c0c` in the general unifier); the S stage's other-tag row for ODPF 6 entries (`setup.S_OTHER_ROW`) and its TDAR (`setup.S_TDAR`, column 7 - TDPF) INFERRED; chains other than a directly held operand raise. The S stage's start-address change (thesis pp.134-137) INFERRED for the immediate's own tag (`setup.S_ENTRY`): the routine starts at the entry with COND = (own tag == immediate), decided by `get_atom` on an unbound variable (`3800`-`3801`, bound to `{ATOMo, atom}` as `pimm.py`; entry + 1 FAILs) and run on `switch_on_non_list` on a list (`3300`-`3301`), in `ref/pu/u2_append.py`. Seventh session: the general unifier EXECUTED in a whole program (`get_value 1,2,0`, nil against an unbound variable reached through a REFo: dereference subroutine `0c15` called by a JMPF b, the binding at `0864`, 16 words; the cell matches `pimm.py`'s M line) |
| U2d | `proceed` / `execute` | U2 | `execute` EXECUTED on its fast path in append (`4cc0`-`4cc3`, 2026-11-27 fifth session: R04 = `{COD, label}`, `pimm.py`'s next instruction; the slit-check and interrupt flags, CNDF 7 EM1 `19` / `21`, INFERRED from rassy's condition list, clear by the harness); its slit-check path `4cc5` and goal switch `4c11` not run; `proceed` reached (seventh session); in append it stops at `216c` (R1b, the goal-record list, never set: `pimm.py`'s proceed has no register or memory effect, and its queue is empty there). Since the eighth session its routine, the goal scheduler, is EXECUTED whole in 15 side cases (`u2_append.proceed_cases`). They use a ready queue from `pimm.py`'s `record`, in the firmware's record layout (INFERRED from `enqueue_goal`'s and suspend's writes), with the scheduler registers OURS, and compare the dispatch with `pick`: R04, A0..An-1, R10, R14, and the freed record declared. Arities 0-11; the empty queue enters the empty arm `21b2` and stops at `21b3` (a shift). Rules decided there: JMPF 9 CNDF and absolute target, JMPF f, DSTF c `++ rfar`, the lc ops, alf_zero. `ref/pu/README.md` "Next, for U2" |
| U2e | clause selection and guards (`try_me_else`, `wait_*`) | U2 | `try_me_else` EXECUTED (`216a`: R11 = `{REFo, label}`, `pimm.py`'s `alt`) and `switch_on_non_list`'s list case, in a whole append run, then the first clause's body and `execute`, and the second reduction's `try_me_else`, the label branch of `switch_on_non_list` on nil (`2447`, JMPF 2) and `wait_nil`: 14 of 16 (sixth session); 15 of 16 with `get_value` (seventh session); stop at `proceed` |
| U3a | suspend | U3 | not reached |
| U3b | bind and resume | U3 | not reached |
| U3c | several goals (the ready structure, goal switch) | U3 | not reached |
| U3d | a compiled KL1 program to its answer | U3 | not reached |
| U3e | PIMOS boot | U3 | not reached |
| U4a | Bluespec PU in lockstep with `ref/pu/` | U4 | not reached |
| U4b | several PEs | U4 | not reached |

### The trace: one record per microcycle

`ref/pu/pu.py` `PU.evaluate` returns, and `PU.commit` appends to
`PU.cycles`, one record per microcycle, the format the Bluespec PU's
lockstep comparison (U4a) will read:

| Field | Meaning |
|---|---|
| `cycle` | microcycle number since the PU was made |
| `micro_pc` | the microaddress executed |
| `microword` | the 64-bit held word |
| `reg_reads` | `[(select name, value)]`, every register-file or work-register read |
| `reg_writes` | `[(select name, value)]`, the register-file write (DSTF) |
| `wr` | work-register writes (MAR1/2, MDR1/2, XR, YR) |
| `mem_reads`, `mem_writes` | `[(address, (tag, value))]` |
| `cond` | COND after the word |
| `cond_cycle` | the cycle whose word formed COND |
| `tdar` | `(cycle, byte)`: the TGT byte the last case_tag_setup selected |
| `mcf` | the EM1 of an MCF operation recorded only (`pu.MCF_UNKNOWN`, of UNKNOWN meaning, and since the sixth session `pu.MCF_NAMED`, 08 pipeline_cancel; since the seventh, 01 set_alf and the sw flag operations `pu.MCF_FLAG_OPS`), else `None` (U2, 2026-11-27) |
| `flags` | `{flag: value}` the word's MCF sets or resets (sw00-sw02), committed with it (seventh session) |
| `alf` | the set_alf latch after the word (`pu.ALF_CONDS` reads it; POISON when latched from an UNKNOWN result) |
| `push`, `pop` | micro-stack activity |
| `next` | the next micro_pc (`None` at an end, `-1` a return to the caller) |

The step is decode, evaluate everything from the OLD state, then commit
all at once, as hardware does; an unmodelled field value raises
`Unmodelled(upc, what)` naming the microaddress and the field, never a
default.


### U1: one KL1-B instruction's micro-routine executes

A Python simulator of the PU's E stage (`ref/pu/`) runs the held
micro-routine from the decode entry's start address to its end, from a
machine state set up to match a `pimm.py` state, and the result agrees
under the comparison above.

- **Oracle:** `pimm.py`'s `i_<name>` on the same state (the same
  instruction cell, the same registers).
- **Unknown:** the nano-code's meaning (what the S stage leaves in
  MAR1/2, MDR1/2 for each instruction: OURS per operand form until the
  Fig. 3-22 fields are decoded); the condition codes (CNDF values);
  AS1F 2/3, TGIF 3, MCF, EM bit 0 of JMPF 1, 4-bit JMPF 2, bit 26;
  what a write with bit 59 set stores (section 16 "not settled"); the
  initial free-list contents (OURS unless the firmware's own refill,
  `3365`-`337f`, builds them).
- **Done when:** several instructions whose routines are more than one
  word (the free-list pops, a call into the allocator and its return,
  a stamp, a push) agree; one-word routines (`set_value`,
  `put_integer`, ... ) count only as plumbing, because all their
  semantics is in the stand-in set-up.

### U2: a small program gives the same trace as `pimm.py`

An append reduction (the image's `append/3`, or the R-series `sample1`
program) runs instruction after instruction on the simulator, the decode
table choosing each routine, with no Python per instruction other than
the D/A/R/S stand-in.

- **Oracle:** `pimm.py`'s trace (`Machine.tr`: `R`, `A`, `M` lines)
  of the same program, compared as in the section above.
- **Unknown, beyond U1:** the tag-dispatch table (TGT; which row of a
  `get_*`/`wait_*` entry's eight-row table is which tag,
  `pseudo_pimm_microcode.md` section 9) is not in the microinstructions;
  `sysinit` `0x5800`-`0x59ff` (512 records of data,
  `psi_microword.md` 4.3) is the first place to look, then inference row
  by row from what each row's held words do. Goal switch (`proceed`
  `216c`, `execute` `4cc0`, `enqueue_goal` `4c00`) and the ready
  structure (section 18: `R14`, cell 15) must run as held. The
  instruction fetch (PC, the A stage) is OURS.
- **Done when:** the program terminates with the same answer and every
  register and heap comparison of every instruction passes.

### U3: PIMOS boots on the microcode simulator

The IPL image (`pimm_ipl.kbn`, the same cells `pimm.py` runs) executes
on the simulator up to the point `pimm.py`'s long runs reach
(`longrun_ipl.py`), with the FEP/SCSI device as today (`fep.py`).

- **Oracle:** `pimm.py`'s IPL run and its pinned counts.
- **Unknown:** every routine PIMOS touches: suspension and resumption
  (page `2c00`, `1c08`, the multiple-suspension record), the shoen
  (`create_shoen` `1694`), GC (`collect_garbage` `02d5`), the built-ins,
  the SCSI built-ins (on the Pseudo PIM/m the PSI-III's I/O, below),
  the 238 branches into `syspsi`'s upper control store (`6c06`-`7de7`,
  section 2), the Goal Stack Entry Table (`PIMM.PARAM` `gseb`).
- **Done when:** the same boot milestones and the same final heap
  terms as `pimm.py`.

### U4: the Bluespec PU, with the WCS loaded from the held image

The D/A/R/S/E pipeline of `M92` pp. 426-429 (`pim_architecture.md`
sections 2-6) in Bluespec, the 32 K x 64 WCS loaded at elaboration or
by a loader from the held image (never committed: generated into
`build/` from `psdpim.tar.Z`, as `psdpim.py` reads it), the decode RAM
from the held decode table, the stand-in tables of U1-U3 as RAMs. It
runs in lockstep with the U simulator, microinstruction by
microinstruction, and replaces `mkPimmExec`'s hand-written sequencer.
The separate boxes stay only where the hardware had separate units: the
network unit (NU), the cache unit (CU: I-cache 1 Kw, D-cache 4 Kw), the
FPP; not a box per instruction family.

- **Oracle:** the U simulator's per-microinstruction state (registers,
  MAR/MDR, COND, the micro-PC), and then the existing core benches
  (`bsv/PimmStages.bsv` suite) unchanged in what they check.
- **Unknown:** cycle timing beyond `M92`'s two-cycle tag branch and the
  "one word later" visibility (`pseudo_pimm_microcode.md` 16); pipeline
  interlocks (nano-code LKF); the bench `bsv/PimStages.bsv` has the
  documented pipeline with hand-assembled microcode and is the starting
  point.
- **Done when:** the core suite passes with the sequencer removed.

### U5: the held PSI-III ESP control store on the same PU

`syspsi` (32 K words, image 1 of `pimm.MEkbn` is its first `0x5800`),
`sysidat` (the KL0 decode table, classes 0/1) and `sysinit` (an
initialisation microprogram at `0x5000` with tables and messages,
`psi_microword.md` 4.3) loaded into the same PU: the PSI-III that SIMPOS
runs on.

- **Oracle:** the SIMPOS work in `psi/` (`docs/simpos/`), whatever of
  SIMPOS's KL0 behaviour is pinned there; the KL0 instruction semantics
  are less documented than KL1's.
- **Unknown:** the KL0 instruction set at the bit level (Appendix A of
  the thesis is a language description, not an instruction set,
  `psi_microword.md` 5); the PSI-III's I/O and memory map; which part
  of `sysinit` initialises what.
- **Done when:** a KL0 program from a held SIMPOS image runs to the
  same result as the `psi/` model.

## Pseudo PIM/m against a PIM/m PE

The held firmware is the Pseudo PIM/m: PIM/m's KL1 microprogram running
on a PSI-III workstation board, for debugging (thesis p.146). What
differs from a PIM/m PE, and so what the simulator stands in:

| Area | Pseudo PIM/m (PSI-III board) | PIM/m PE | In `ref/pu/` |
|---|---|---|---|
| Control store | KL0 firmware (image 1 = `syspsi` `0..57ff`) and KL1 (image 2) in one 32 Kw WCS; the decode table caches KL0/KL1 entries with a flag (thesis p.125) | KL1 only | image 2 at `0..67ff`, then `syspsi` from `6800` up, resident (`pu_store.Stores.kl1_wcs`, CORROBORATED); `6c21` is the illegal-instruction trap, raised as `Trap` |
| Memory | up to 64 Mw, TLB, process IDs (thesis pp.123, 141) | 16 Mw local memory, no TLB stated (`M92` p.426) | flat dict of 40-bit cells: OURS |
| I/O | PSI-III I/O bus and timer outside the PU (thesis p.130) | NU to the mesh, SCSI to the FEP (`M92` p.427) | none; a routine that reaches I/O fails loud |
| Parameters | `SYSTEM.DIR/PIMM.PARAM` (Goal Stack Entry Table, stacks), "FOR PSEUDO MULTI-PSI" | set by PIMOS boot | the registers a run needs are set by the harness: OURS, listed per case |

## Estimates (2026-11-26, after U1)

Honest, and in sessions of the length that reached U1.

- **U2 (after the third session, below):** three to five more
  sessions. Each instruction of append has cost one S-stage or set-up
  question (`read_variable`'s was the dereference set-up, settled
  for 'other'; `put_reused_structure`'s start for a tag that is
  not the immediate was the ODPF 3 start, fourth session; next
  `execute`'s set-up, EM1 `19` and the conditional JMPF timing, then
  the S12 rows of `get_*`/`wait_*`, which
  disagree with the simplest column reading) and the branch to a label
  needs the 4-bit JMPF 2 (S10). Earlier estimate, for the record:
- **U2 (first estimate):** two to four sessions. In order: the refill (AS1F 3 now
  INFERRED; still the initial R1f and W0d, the counted loop, CCF as a
  coded field), the allocator for three cells
  and more (the list-head table at R05, SC2F `b`), `execute`, `proceed`,
  `try_me_else`, then the `get_*`/`wait_*` tables, which need the
  tag-dispatch RAM (not in `pimm.MEkbn`; found in `sysinit` or inferred
  row by row) and the S stage's tag set-up. Each new routine has so far
  cost one or two field rules.
- **U3:** many sessions (ten or more, unchanged; it cannot start before
  U2's S-stage model exists), and the rung most at risk. PIMOS
  boot touches suspension and resumption, the shoen, GC, the built-ins
  and the SCSI built-ins, each a family of routines with its own
  unknowns, and the Pseudo PIM/m board's TLB traps, interrupts and I/O
  have no PIM/m counterpart to compare with. A routine that needs
  hardware no source describes would stop U3 there.
- **U4:** the generic E-stage datapath is small (one decoder, two
  phases, COND, a micro stack), two or three sessions to build and run
  in lockstep with `ref/pu/` on U2's program. Replacing `mkPimmExec`
  keeps the core suite green only once U3's coverage exists, so U4's
  "done" is gated by U3.
- **U5:** not estimated; the KL0 instruction set at the bit level is
  not documented.

## Status

- 2026-11-26: plan written. U1 and U2 are the first task (`ref/pu/`);
  status lines are added below as rungs are reached.
- 2026-11-26: **U1 reached.** `ref/pu/check_pu.py` (in `run_tests.sh`):
  22 instructions agree with `pimm.py`, 44 held microinstructions
  executed and matched (33 in multi-word routines: the free-list pops of
  `set_variable`, `write_variable`, `put_variable` and their marked
  forms, held out, `put_list`, `put_vector_1/2`; the stamps of `set_nil`,
  `write_nil`; 11 in one-word routines that only test the plumbing), and
  four last-cell cases reach the refill (17 more words). Nine INFERRED
  rules, each with the microaddress that decided it, the counts behind
  them pinned (`ref/pu/measure.py`), and six observed fault injections:
  `ref/pu/README.md`. **U2 not reached.**
  The first routines that would not run: the free-list refill
  (`3365`-`337f`, at `3378` on AS1F 3) and the allocator for three cells
  and more (`3331`, the list-head table at R05 and the SC2F `b`
  immediate). Needed for U2 after them: `execute`, `proceed`,
  `try_me_else`, the `get_*`/`wait_*` tables (the tag-dispatch RAM, not
  held in `pimm.MEkbn`), and CCF read as a coded field.
- 2026-11-26: the step split into evaluate and commit (the per-cycle
  record above); **U1c**: the allocator `3320` called as a
  microsubroutine EXECUTED (4 words: `{REF, cell}` in W1c, the cell
  `pimm.py`'s `new_var` gives, the link left in R19). AS1F 3 (constant
  EM2 on the first ALU input) INFERRED at the refill's `3378`. The
  refill now stops at `3378` reading R1f (HP), never set; with an HP
  given (OURS, a case in the check) it runs on to `3365` and stops
  reading work register W0d. Who sets them first is UNKNOWN. Image 2
  has 17 words that write R1f (three at `0159`, `019a`, `029b`, below
  the lowest decode entry `02d5`; the others after the entries of
  `collect_garbage`, `new_module`, `execute_first_predicate`,
  `switch_on_non_list`), 14 that write R05 and 4 that write W0d (after
  the entries of `collect_garbage`, `proceed`, `merge`,
  `enqueue_goal_with_priority`); `syspsi` has 159, 22 and 4. None of
  these routines has been run. Also added: decode-table dispatch from
  the instruction cell (`setup.dispatch`), a held call word (`615e`
  into `3320`, return to `615f`), and a step-contract check (evaluate
  twice gives equal records and leaves the state unchanged; commit
  returns `next`). PASS, 31 cases, 80 held microinstructions.
- 2026-11-26: adopted the static agent's results
  (`pu_microcode_inference.md` section 7, merged from master): the KL1
  control store `image 2 ++ syspsi[6800:]`; S8 `case_branch` with the
  TGT from `sysinit` `5300` (only set-up EM1 `3a` -> column 2; any
  other column raises); `6c21` as the trap; S9 and S10 raise; CNDF 5 =
  eq and CNDF 7 EM1 `0a` = lt, `09` = overflow (INFERRED polarity, not
  yet executed here); the timing of a conditional a/b/c/e jump is the
  switch `RULES['cjump_time']` (None raises). One point the execution
  settles: the static agent's "a conditional end tests the previous
  word's condition" cannot mean the very previous word. At
  `put_variable` `31d6`-`31d8`, the COND that `31d6` (CNDF b) forms is
  tested by the conditional end `31d8` after `31d7` (CNDF 0), so a
  CNDF-0 word leaves COND standing (EXECUTED; the injection
  `cond_prev_strict` stops `put_variable` and its marked form). The
  layout result (TR-733 eliminated) rests jointly on the allocator
  contract (inference doc 6.3 item 1); `ref/pu`'s allocator `3320` run
  is that contract executed, so it is not independent evidence for the
  layout. PASS, 32 cases, 80 held microinstructions.
- 2026-11-26 (second session): **U2 not reached; furthest point 2 of 16
  instructions.** `ref/pu/u2_append.py` (in `run_tests.sh`, its furthest
  point pinned) runs the IPL image's `append/3` as `append([a], [], Z)`
  instruction after instruction with the PU's state carried over:
  `try_me_else` (`216a`) and `switch_on_non_list` on a list (`3300`-`3301`)
  executed and matched (3 held words), then a stop at `read_variable`
  at `34a0` (CNDF 7 with EM1 28: the TGT column is UNKNOWN; its MAR1 =
  R02 is OURS). Before it, the
  firmware's own boot routine for the heap top (`start` `2028` calls
  `204b`-`2052`) runs on a parameter cell and gives R1f (the first of
  the "never set" registers, set by held code; the cell's value is
  OURS, `pimm.py`'s heap pointer, standing for PIMM.PARAM's `ihp`). New
  rules, each INFERRED with its deciding address and an observed
  injection (`ref/pu/README.md` "U2"): the S stage's entry start with
  COND for the immediate's tag (`setup.S_ENTRY`, decided by get_atom at
  `3800`-`3801`, thesis pp.134-137 DOCUMENTED mechanism),
  SC2F b = EM2:EM3 (`204b`), CNDF 2 = ALU result zero (`204f`-`2052`,
  by the round-up contract), the EM-bit-0-clear polarity EXECUTED
  (`2050`). Not settled: the S12 row entry, JMPF 2, `cjump_time` (not
  attempted), R05 /
  W0d (a census: R05 549 reads, 14 writes, none in `start`).
- 2026-11-27 (third session): **U2 not reached; furthest point 4 of 16
  instructions** (was 2), 11 held words. `read_variable` runs
  (`34a0`-`34a2`, `3494`) twice in append and once standalone on a
  list element, matching `pimm.py` (x and sp; no memory write). Decided
  (`ref/pu/README.md` "U2", each with observed injections): CNDF 7
  EM1 `2d` is the dereference multiway set-up of thesis printed p.133
  (TDAR := code << 2 from the AS1 tag; 'other' = 1 executed; = EM2,
  REFo, REFx read from the rows of `3490`-`349f`, not run, raise),
  INFERRED; JMPF 8 sequences as JMPF 0 in that word only, INFERRED;
  EM1 `28` is a condition of UNKNOWN meaning (COND := POISON, not
  tested on the path), NOT discriminated; a read of a cell never
  written gives POISON (OURS; `34a2` reads through the element
  itself); `read_variable`'s MAR1 = R02 stays OURS, supported by OS1F 6
  = the thesis's source (6) S (printed p.128), not fitted. A TGT-column
  reading of `2d` was eliminated by a scratch script (no column of
  `5300` sends ATOMo to `3494` and every tag to a row's first word);
  column 0 passes append itself, so the list-element case is what
  discriminates. A harness bug was fixed: `pimm.py`'s R and M lines
  bypass `event()`, so no instruction had any to compare. The stop is
  `put_reused_structure` (`31e8`): no S-stage set-up form; its operand
  is a list and its immediate VECTo, so it needs the S stage's start
  for a tag that is not the immediate (S12).
- 2026-11-27 (fourth session): **U2 not reached; furthest point 10 of
  16 instructions** (was 4), 20 held words: `put_reused_structure`
  (`31ec`-`31ed`), `write_value`, `write_variable`, `get_bound_value`
  (`3880`), `put_value` twice match `pimm.py`. Decided (`ref/pu/README.md`
  "U2", each with observed injections): the ODPF 3 start, entry | code
  << 2 with code 0 = the operand's tag is the immediate, 1 = other
  (thesis printed pp.129, 133, 136; 14 of the 19 ODPF 3 entries with an
  immediate reach the R11 failure exit from entry + 4), INFERRED; CNDF 7
  EM1 `29` = the MRB of the AS1 input is on (contract: a shared
  structure is not reused in place, TR-466 4.2; `pu_smt` side contract
  `reuse_kl1` keeps only the MRB test, mrb_on under the adopted
  polarity), INFERRED; SC2F 1 = an IR field on the S2 bus, not a
  register R01 (thesis printed p.129), INFERRED, width not
  discriminated; `get_bound_value`'s set-up (MDR2 := r[y]) OURS. Two
  declared differences in the harness: `reuse` (the firmware reuses a
  single-referenced list in place, `pimm.py` never does) and U1's
  `indirect`. The stop is `execute` (`4cc0`): no set-up form; its first
  word forms COND with CNDF 7 EM1 `19` (UNKNOWN) and its second is a
  conditional JMPF b (`cjump_time`).
- 2026-11-27 (fifth session): 12 of 16 (`execute`'s fast path and the
  second `try_me_else`), stop at `switch_on_non_list` on nil
  (`ref/pu/README.md` "U2").
- 2026-11-27 (sixth session): **U2 not reached; furthest point 14 of 16
  instructions** (was 12), 37 held words: `switch_on_non_list` on nil
  branches to the label (`3310`-`3311`, `2447`, `2440`, `2461`, `241d`;
  R04 = `pimm.py`'s next instruction, now compared for every
  instruction), `wait_nil` (`3980`, `3985`) matches, and `get_value`
  runs `38b0`-`38b3`. Decided (`ref/pu/README.md` "U2", each with
  observed injections): JMPF 2 (S10) = a case_branch on upc + EM3,
  from rassy's jmpf table (HELD-SOURCE) and 15 of 16 aligned bases;
  the S stage's other-tag row (match << 2 | chain code) and its TDAR
  (TGT column 7 - TDPF, from the shapes of four tables); the JMPF a / e
  polarity (rassy's 'if cond' / 'if not cond' pool); EM2 20/30 = MRB
  off/on, MCF 08 = pipeline_cancel, CNDF 8/a/c on the S1 bus, SD1F 2/3
  pairs, JMPF 9 a conditional call (all rassy tables); EM1 1e/1f the S
  stage's MRP/COL reports; R04 = pc + 1 in E (OURS, with support). The
  stop is `0c0c` (CNDF 7 EM1 `3f`, which rassy's `cndf_others` table
  names `case_tag_setup mdr2 7`: TDAR from TGT column 0, not yet
  modelled; reached by a JMPF b that rassy reads as a conditional call:
  an open conflict). Rassy's EM1 keys also make the earlier flag names
  (`19`, `21`, `1e`, `1f`) HELD-SOURCE rather than by position.
- 2026-11-27 (seventh session): **U2 not reached; furthest point 15 of 16
  instructions** (was 14), 49 held words: `get_value 1,2,0` runs the
  general unifier whole (16 words) and binds Z1's cell to nil as
  `pimm.py`. Decided (`ref/pu/README.md` "U2", each with observed
  injections): `case_tag_setup` mdr1 / mdr2 k for EM1 `30`-`3f` (rassy,
  HELD-SOURCE names; column 7 - k); JMPF b a conditional CALL (rassy, the
  `0c0f` / `0c12` twins, and a census: no b target reaches only ends),
  which settles the S7 conflict; whole-byte case_branch (`0e75`); TDAR
  standing across a JMPF 1 word (`0802`); rassy's MCF decoder (`mc1` /
  `mc2`): sw00-sw02 set / reset, set_alf, and the names of 06 / 07; the
  sw01 test (CNDF 7 EM1 `11`). The stop is `proceed` (`216c`), and the
  sixteenth instruction is left with a reason: `pimm.py`'s proceed has
  no observable to compare, the routine needs scheduler state neither
  model holds, and its first branch tests an ALU difference that the
  adopted YR timing makes identically zero (`ref/pu/README.md` "Next,
  for U2").
