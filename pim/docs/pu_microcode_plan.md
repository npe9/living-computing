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
the hand-written interpreter goes away. Labels as in the rest of `pim/`:
HELD (a held microinstruction executed as it stands), MEASURED,
INFERENCE (a field-value meaning inferred; every one names the
microaddress and the trace line that decided it), OURS (a stand-in for
hardware or environment that the held words do not give).

## The rule that holds for every rung

- **Never write a micro-routine of our own in place of a held one.** A
  routine that cannot be run is stopped at and recorded, with its
  address and the field or table that is missing.
- **What is stood in is the hardware, never the microprogram.** The
  stand-ins are the parts of the PU that are not microcoded: the D/A/R/S
  stages that the decode entry's nano-code drives (`pim_architecture.md`
  section 2; nano-code fields, Nakashima Fig. 3-22,
  `psi_microword.md` 3a), the tag-dispatch RAM (TGT, 512 entries, not
  in `pimm.MEkbn`), the condition multiplexer behind CNDF, and the
  memory and I/O of the board. Each stand-in is a small table, labelled.
- **Fail loud.** A field value whose meaning is not modelled, met on an
  executed path, raises with the microaddress. That is how "the first
  routine that would not run" is found, and how each INFERENCE enters:
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
   INFERENCE and is listed with its evidence.
4. **Firmware-only writes** (free-list links, freed cells, goal record
   trailers, refill) are listed as expected differences, with the
   firmware as the authority: they are what the hand-written models do
   not do, not errors.

## Rungs

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
| Control store | KL0 firmware (image 1 = `syspsi` `0..57ff`) and KL1 (image 2) in one 32 Kw WCS; the decode table caches KL0/KL1 entries with a flag (thesis p.125) | KL1 only | image 2 at `0..67ff`; a branch to `6800`+ (`syspsi`'s upper store) fails loud |
| Memory | up to 64 Mw, TLB, process IDs (thesis pp.123, 141) | 16 Mw local memory, no TLB stated (`M92` p.426) | flat dict of 40-bit cells: OURS |
| I/O | PSI-III I/O bus and timer outside the PU (thesis p.130) | NU to the mesh, SCSI to the FEP (`M92` p.427) | none; a routine that reaches I/O fails loud |
| Parameters | `SYSTEM.DIR/PIMM.PARAM` (Goal Stack Entry Table, stacks), "FOR PSEUDO MULTI-PSI" | set by PIMOS boot | the registers a run needs are set by the harness: OURS, listed per case |

## Status

- 2026-11-26: plan written. U1 and U2 are the first task (`ref/pu/`);
  status lines are added below as rungs are reached.
