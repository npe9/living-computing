# PIM/m reproduction plan

## Scope

Reproduce one PIM/m processing element first, then its communication
hardware and a small deterministic mesh. "PIM" is ambiguous today with
processing-in-memory; here it always means ICOT's *Parallel Inference
Machine*. The four other PIM variants are not silently blended into the
PIM/m model.

The target is an instruction- and cycle-accounted Bluespec model able
to run surviving PIM/m machine code or microcode and, eventually, a
documented KL1 workload. If no bit-exact executable survives, the first
software oracle will be a manually assembled diagnostic derived from a
primary manual and explicitly labelled manual-derived.

## Evidence gates

1. Acquire local, checksummed copies of the 1992 ICOT proceedings,
   TR-324, PIM/m hardware and microprogramming documents, PIMOS/KL1
   documents, and any surviving listings or binaries. Record stable
   archive locations, printed-page mappings, and provenance.
2. Build an architectural inventory: word and tag formats, registers,
   instruction and microinstruction encodings, traps, memory system,
   mesh packets, routing, scheduling, and every published latency.
   Mark every field as confirmed, conflicting, or unknown.
3. Locate an independent encoding oracle. Prefer a printed listing with
   machine-code columns, then an original assembler or binary. Do not
   infer encodings from prose examples or from a later PIM variant.
4. Decide whether the surviving evidence supports cycle accuracy. If it
   does not, implement only documented transitions and report timing as
   unknown rather than borrowing it from Multi-PSI or another PIM.

## Staged implementation

1. Write a table-driven assembler/disassembler with round-trip and
   negative tests. Every opcode entry cites a document and printed page.
2. Model tagged words, the local store, register state, and fetch/decode.
   Unknown and reserved encodings stop loudly.
3. Split the processing element into Bluespec pipeline/state-machine
   modules. Arithmetic, unification, goal control, and microcode control
   get request/response interfaces where the documents describe
   multi-cycle operation.
4. Add interrupts, faults, and the documented interface to PIMOS. Run a
   single-PE diagnostic before introducing nondeterminism or a network.
5. Model a mesh link and packet flow control, prove it with two PEs, then
   build a parameterized small mesh with deterministic arbitration and
   deadlock-directed tests.
6. Add KL1 only through a documented compiler/runtime path. Preserve the
   distinction between architectural tests, runtime tests, and language
   benchmarks.

## Definition of the first milestone

The source inventory is checked in; an encoding table covers every
documented PIM/m instruction and identifies every gap; an assembler
round-trips a primary-source example; and a one-PE Bluesim smoke test
fetches, executes, and halts on that example. The full repository test
suite remains green.
