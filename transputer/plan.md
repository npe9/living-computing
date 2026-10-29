# IMS T800 reproduction plan

## Scope

Build a cycle-accounted T800 core and links, then compose a small
network. The floating-point unit and communication links are part of
the target, not optional accelerators. Board-level systems and later
transputers remain outside the initial scope unless a diagnostic needs
a documented support chip.

## Evidence gates

1. Acquire checksummed INMOS manuals, databooks, technical notes,
   errata, occam/toolset documentation, and any surviving diagnostics or
   object files. Record document editions and silicon revisions.
2. Inventory every direct and operate instruction, prefix construction,
   workspace/process state, scheduler queue, timers, events, traps,
   reset/boot protocol, link tokens and electrical abstraction, and FPU
   operation. Every encoding and timing cites a printed page.
3. Obtain a bit-exact oracle from an original INMOS assembler/compiler,
   printed examples, or surviving binaries. Separate instruction
   encoding evidence from language/compiler behavior.
4. Turn published instruction, link, and FPU timings into an explicit
   timing table. Conflicts between manuals or speed grades remain named
   variants rather than averaged values.

## Staged implementation

1. Implement a prefix-aware assembler/disassembler and an object-image
   loader, with round-trip, malformed-stream, and cross-check tests.
2. Model the integer datapath, evaluation stack, workspace, fetch/decode,
   and memory interface as separate Bluespec modules. Unsupported
   instructions stop loudly.
3. Add process scheduling, low/high-priority queues, timers, alternate
   and channel operations, validated first on one core with small occam
   kernels and architectural diagnostics.
4. Implement the FPU as a stateful request/response box with documented
   rounding, exceptions, overlap, and latency. Use bit-pattern oracles,
   not host floating-point equality.
5. Implement one serial link endpoint and boot-from-link, test two chips
   under backpressure, then construct a parameterized network. Network
   tests must cover simultaneous traffic, blocked channels, and reset.
6. Add only those support-chip or board models required by an original
   program, behind documented interfaces.

## Definition of the first milestone

The architectural inventory covers the complete T800 instruction
space; the assembler round-trips primary-source and original-tool
examples; and a one-core Bluesim smoke test boots a small image, runs
integer/prefix and scheduler operations, and halts observably. The full
repository test suite remains green.
