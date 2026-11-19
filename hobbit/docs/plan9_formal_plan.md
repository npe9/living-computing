# Reaching formal verification for the Hobbit model

**Answer to the question this document exists for: no.** Neither
`plan.md` nor `docs/plan9_boot_plan.md` leads to formal proof by itself —
they lead to *running* Plan 9 1e on the model. Today verification here is
trace comparison and hand-derived goldens:

* the HRI record is the DUT/spec boundary (`HobbitTypes.bsv:80-102`),
  one record per retired instruction, and `tests/hri_check.py` diffs the
  core's records against `sem/hobbit_sem.py`'s;
* `tests/golden/` breaks ties, one hand-derived trace per program;
* `grep -rln 'sby\|smtbmc' bsv tests tools` finds no proof harness at
  all, and the README says so: "not a yosys formal proof".

This document is the missing track. It is written so that each stage is
a property, a tool, a bound and an artefact — the same discipline as the
rest of the directory.

Tools present on this machine (checked): `yosys 0.51`, `sby`, `z3`,
`boolector`, `yices`, plus the harness devices `yosys_equiv`, `sby_formal`,
`smtbmc`, `formal_model`, `proof_artifact`.

## What "full formal" is taken to mean here

Unbounded, whole-machine functional correctness is not a tractable target
and will not be claimed. The target is **machine-checked correctness of
every claim the model makes**, as four property families:

| family | property | bound |
|---|---|---|
| \(F_1\) instruction equivalence | for each implemented instruction, RTL and the printed semantics agree on the HRI record and the architectural post-state | per instruction, symbolic operands |
| \(F_2\) structural invariants | one write per array per cycle, at most one retirement per cycle, pipeline drains, prefetch tags | k-induction |
| \(F_3\) MMU and events | translation deterministic; event priority respects p. 1-40; TLB/table coherence after flushes | k-induction + BMC |
| \(F_4\) device contracts | bus Appendix A handshake, DUART framing/status, timer count/overflow | k-induction |
| \(F_5\) boot reachability | from the 1e reset state, the first \(N\) retirements of the kernel match a hand-derived trace; no unimplemented-instruction or fetch-miss trap before the console write | bounded, \(N\) stated |

## F0 — the interface and the record

Before any proof, three things must exist:

1. **A Verilog/RTLIL entry point per unit**, produced by `bsc -verilog`
   from the same module the simulator uses (`mkHobbitCore`,
   `mkHobbitMmu`, `mkHobbitEvents`, `mkHobbitBus`), so a proof cannot be
   about a different design. `tools/formal_build.sh` (new) emits them
   with the bsc version recorded.
2. **A mechanised specification side per instruction.** `sem/` is Python;
   proofs need SMT. The plan is to generate, for each instruction, an
   SMT-LIB contract from the sem's table (reviewable text, checked
   against the same goldens), so the proof compares RTL against a
   formula that is a *transcription* of the Python, not a second model.
   The transcription itself is validated by the existing 56 HRI records
   (diff the SMT contract's evaluation against `sem/hobbit_sem.py` on
   every golden state).
3. **Proof artefacts**: each `sby` run records bound, solver, tool
   versions and hashes via the `proof_artifact` device, so "proved"
   always means "proved at this hash with this bound".

## F1 — instruction equivalence (first real milestone)

Shape: for instruction \(i\), drive `mkHobbitCore` from a start state
with the instruction at 0, memory words holding **symbolic** operands
(`anyseq`) constrained by the addressing modes, events disabled, one
clocks-per-instruction window; assert

* the retired HRI record equals the SMT contract's record field for
  field (`pc`, `insn0/1`, `sp/msp` before and after, `we/addr/data/mask`,
  `trap`, `cyc`);
* the architectural post-state (memory words written, accumulator, SP/MSP)
  equals the contract's.

Order: the instructions the 1e user binaries actually execute first
(`MOV`, `CALL`, `CMPEQ`, `CMPGT`, `ADD`, `SUB`, `ADD3`, `ENTER`,
`CATCH`, `POPN`, `RETURN`, `JMP*`, and the new `SHL3`/`SHR3`), then the
rest of Table 3-1. Refusals stay refusals: an instruction the sem
refuses gets a proof that the RTL traps with the same record.

## F2 — structural invariants

`bsc` already rejects double writes; the proofs here are the ones it
cannot do: at most one RB (retirement) per cycle; from any reachable
state the pipeline drains within a stated number of cycles (bounded
liveness, the deadlock that cost a day is the example); the prefetch
window's valid/tag invariant.

## F3 — MMU and events

* translation determinism and the identity of TLBs after `FLUSHPTE`/STB;
* the p. 1-40 priority order as a theorem: no two events are taken in
  one cycle, and an event of higher priority is never masked by a lower
  one — the event testbench tests examples, this proves the order;
* the frame words an event writes match Table 1-26 with the offsets
  settled by O4 of the kernel inventory.

## F4 — devices

* bus: `DTACK` within the modelled clock after `START`, `BERR` mutually
  exclusive with `DTACK`, `BGRANT`/`BGACK` exclusivity (Appendix A);
* DUART: 8N1 framing, status bits, interrupt masking (after A4's model
  exists — the parked work in `/tmp/duart-wip/` is the starting point);
* timers: count/overflow/vector properties from pp. 1-19, 1-20.

## F5 — boot reachability

Once A3 produces a 1e kernel image: BMC from the reset state
(`PSW=0`, `VB=0`, PC = image entry, `raml.s`'s first instructions) for
\(N\) retirements, checking the HRI stream against a hand-derived trace
of the boot path, and asserting that no `TR_FETCH_MISS`/unimplemented
trap occurs before the first console write. \(N\) is stated per run; this
is reachability, not a proof of the OS.

## Process

Every A/B milestone in `docs/plan9_boot_plan.md` gains its F harness in
the same change: a new instruction arrives with its F1 proof, a new
device with its F4 proof. The suite gains a `prove` stage that runs the
harnesses at their recorded bounds; a failing proof blocks the
milestone. Bounds are named in every result — "proved for k=40" is a
result, "proved" alone is not.

## Order

1. **F0** — `tools/formal_build.sh`, the SMT contract generator and its
   validation against the 56 golden records, artefact recording.
2. **F1** — the ten instructions 1e's binaries use, then Table 3-1.
3. **F2** — invariants, starting with "one retirement per cycle" and
   pipeline drain.
4. **F3** — translation determinism and the event order.
5. **F4** — bus contracts, then DUART and timers as their models land.
6. **F5** — boot reachability behind A3/A4.
