# Full functional completeness and correctness

**The goal, as the owner states it: the model must be functionally complete
and provably correct — every documented feature of the AT&T 92010, and
every behaviour it claims proved for all executions, not for examples and
not up to a bound.**

An earlier version of this document called whole-machine correctness
"not tractable". That was wrong for a *machine*: the Hobbit is a finite
state machine, the ISA is a finite table, and refinement can be proved
per instruction and then composed. What is intractable is reasoning about
the *operating system* built on it, and that is not what is claimed here.

**Sequencing (owner, 2026-11-19): this track comes after Plan 9 boots.**
The boot work in `docs/plan9_boot_plan.md` — A0 through A5 — is the
work now; C1…C5 and P1…P5 below are the target that follows it, and no
boot milestone is delayed to build a proof harness. What continues
*meanwhile*, because it is what the boot itself needs, is the ordinary
evidence discipline: every instruction and device the boot requires
lands with its page cites and its discriminating tests, and each such
change is written so that its formal harness can be added afterwards
without redesign (a stated contract boundary, one rule per behaviour,
named assumptions).

Two words are therefore defined operationally, and every gate below
measures one of them.

## Completeness — every documented feature, nothing refused

The model today is deliberately partial ("decode completely, execute
partially, document the rest"). That convention is **retired** for this
machine: a refusal is a defect unless the *hardware* itself takes the
unimplemented-instruction sequence for that encoding (e.g. `FLUSHD`, no
data cache, PRM p. 3-22).

Completeness gates, all mechanically checked:

| id | gate | how it is measured |
|---|---|---|
| C1 | every Table 3-1 instruction executes in the core and in `sem/`, in every printed width and parcel form (1/3/5), every addressing mode of Table 1-23, and the CPU-escape registers of Table 1-24 | a generated matrix over the instruction inventory; zero `Unsupported`/`Unimplemented` outcomes for Table 3-1 rows |
| C2 | the documented state is complete: PSW (every printed bit), CONFIG, VB, STB, ISP/SP/MSP/SHAD/CSP, the accumulator, both timers, TLB/NPSR contents | state inventory versus PRM Tables 1-1…1-14, each bit cited |
| C3 | every device the 1e Hobbit port drives is modelled — console DUART, keyboard, screen/Incon, RTC, SCSI, SONIC/Ethernet, IIC/EEPROM, FPU, timers, board IRQ controller (`docs/plan9_kernel_inventory.md` §3) | one model + one end-to-end test per row |
| C4 | the machine-level behaviours of chapters 1–4 are implemented: prefetch and decode, stack cache and CATCH/POPN/ENTER/RETURN, MMU, event priority, bus protocol, cycle counts of Tables 4-32…4-36 | the feature inventory in `docs/` with no open item that says "not modelled" |
| C5 | **no refusal is reachable from 1e software**: the shipped binaries and the kernel run to their own ends, and a scan of every trap/refuse site in `bsv/` and `sem/` finds either a hardware-justified trap or nothing | a scripted scan plus the boot of A3/A4 |

## Correctness — proved for all executions

Correctness means refinement: for every program, the RTL's observable
sequence (the HRI records, the UART, the bus) is one the semantics
produce. That decomposes:

| id | theorem | method |
|---|---|---|
| P1 | **per-instruction equivalence**: for every instruction, all operand values, all addressing modes, RTL's retirement record and architectural post-state equal `sem/`'s contract | `sby` in `prove` mode over a generated SMT contract per instruction (symbolic operands, no bounds) |
| P2 | **pipeline refinement**: the core's steady state is the sequential composition of P1's step relation — fetch never changes semantics, stalls only delay, folding matches Table 4-35 | k-induction over pipeline invariants (one retirement per cycle, drain, slot handoff) composed with P1 |
| P3 | **MMU and events**: translation is deterministic and equals the printed walk; TLB/NPSR contents remain coherent with the tables under every flush; the p. 1-40 order is respected and exactly one event is taken | k-induction on the MMU/event boxes and the core's event path |
| P4 | **devices**: each device refines its printed specification — bus Appendix A handshake and timing, DUART framing/status/interrupts, timers, RTC, SCSI, SONIC, IIC | k-induction per device, contracts from the same sources the models cite |
| P5 | **the platform**: with C3 complete and P4 proved, the 1e kernel's boot is a program on a proved platform; the boot's own correctness is reachability of the stated behaviour (console write, no spurious trap) | bounded reachability used as *evidence*, with the unbounded claim coming from P1–P4 |

**Assumptions are named, never hidden.** The model makes choices the
manual leaves open — A=1/D=2/Q=4 (p. 4-2 prints no values), TLB
replacement policy, the 3 KB prefetch window's contents. Correctness is
stated relative to those choices, each recorded in `docs/` with its
reason; a proof never silently assumes more than the documents say.

**Every proof carries its provenance**: tool versions, the RTL hash, the
contract hash, whether the run was `prove` or `bmc`, and the bound when
one exists, recorded through the `proof_artifact` device. "Proved" alone
is never written; "proved for all inputs, k-induction depth n, hash h"
is.

## Where this leaves the existing verification

The HRI comparison and the goldens do not go away; they become the
*validation of the contract generator* (P1 needs `sem/` transcribed to
SMT, and 56 golden records plus 18 assembler checks are the evidence
that the transcription is faithful) and the regression net that keeps
the proved machine executing real programs. Nothing that is green today
is deleted to make a proof easier.

## Order of work

1. **C1 first, because it shrinks P1's surface to something provable and
   because it is the owner's first word**: complete Table 3-1 in `sem/`
   and the core, mode by mode, with the matrix gate.
2. **F0/P1 tooling**: `tools/formal_build.sh` (Verilog per unit from the
   same modules), the SMT contract generator and its golden validation,
   artefact recording; then P1 for the instructions 1e uses, then the
   rest of the table.
3. **P2 invariants**, then **P3**, then **P4** device by device (DUART
   first, since A4 needs it), then **C3** for the devices 1e drives.
4. **C2, C4** continuously, each with its citation, as the instruction
   and feature work proceeds.
5. **C5/P5**: A3/A4 of the boot plan, with the scan and the reachability
   evidence.

Each milestone in `docs/plan9_boot_plan.md` ships its completeness row and
its proof in the same change; the repository suite gains a `prove` stage
that re-runs every harness and fails on any regression.
