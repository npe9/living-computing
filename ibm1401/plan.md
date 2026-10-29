# IBM 1401 reproduction plan

## Scope

The initial target is a base IBM 1401 with documented feature flags kept explicit. Related models and later revisions are comparative sources, not behavior to merge silently into this model.

The model will cover variable-length fields, word marks, BCD zones, storage addressing, branches, overlap, and unit-record I/O. Encodings, state transitions, and timing claims require a primary-source page; undocumented behavior fails loudly.

## Evidence gates

1. Inventory the local documents by edition, revision, provenance, printed-page mapping, and checksum. Add schematics, maintenance material, diagnostics, listings, and original software as they are found.
2. Build a feature matrix covering programmer-visible state, encodings, exceptional conditions, storage, I/O, and published timing. Mark every entry confirmed, conflicting, or unknown.
3. Establish a bit-exact oracle: prefer printed machine-code listings or original binaries, then an original assembler. Manual-derived tests remain explicitly weaker.
4. Record configuration and revision boundaries before combining sources. Do not fill documentary gaps from descendants, replicas, or modern emulators without naming the inference.

## Staged implementation

1. Implement a table-driven assembler/disassembler and image format with round-trip, malformed-input, and primary-example tests.
2. Model storage, registers, fetch/decode, and the smallest complete integer/control subset as separate Bluespec modules. Reserved and unsupported operations stop visibly.
3. Split expensive or timed datapaths into stateful request/response boxes; model concurrency, interlocks, and arbitration only from documented rules.
4. Add exceptional conditions, operator controls, and the minimum documented I/O needed by an original diagnostic or program.
5. Run primary-source diagnostics or transcribed software, checking printed machine code before execution. Add cycle assertions only where a documented number exists.

## First milestone

The source/revision inventory is checked in; the encoding table accounts for every documented operation; an assembler round-trips a primary example; and a Bluesim smoke test fetches, executes, and halts observably on that example. The full repository regression suite remains green.
