# The E-box: from an interpreter in a rule to arithmetic hardware

**Direction set by the project owner, 2026-10-28.** The diagnosis, in
their words: *"the repository now has idiomatic rule-level
orchestration, but its execution semantics are still written like a
large software interpreter embedded inside a rule."*

And the sentence that reframes the whole timing effort:

> **"You aren't trying to emulate Stretch's timings, you are trying to
> REPRODUCE them."**
>
> **"Stalls etc should happen as actual stalls, not as faked rules."**

With one scope limit, also theirs: **cycle accuracy, not timing
accuracy.** A Bluespec rule firing is a clock edge, so sub-cycle delay
has nowhere to live — which is what `docs/microarchitecture_roadmap.md`
already says under "What stays out".

## What is already idiomatic and must be preserved

Stated by the owner, and worth writing down so a later refactor does
not undo it:

* `step()` is only a clock enable, and behaviour lives in rules.
  (Since 2026-10-28 there is no `step()` at all: the core owns a run
  latch. See that commit.)
* Instruction buffering, look-ahead, storage, memory and the E-box are
  modules with interfaces.
* Mutually exclusive rules express the core control transitions.
* `mkCReg` explicitly represents required same-cycle ordering.
* `DecodedInstr` is a tagged union with typed payloads.
* Memory uses request/response handshakes and return tags.
* Long memory-dependent execution goes through start/busy/resume.
* Off-pipe work — I/O, transmit, recovery, interrupts — has its own
  rules.

**It does not need FIFOs between every stage, and not every submodule
needs `(* synthesize *)`.** Combinational `out` methods with atomic
enq/deq handoff in one orchestration rule is normal Bluespec practice.

## The reference, and it is checked out locally

`~/src/Flute/src_Core/CPU/IntMulDiv.bsv` — read 2026-10-28, and it is
the shape the arithmetic should take:

```bluespec
typedef enum { Div_RDY, Div_START, Div_LOOP1, Div_LOOP2, Div_DONE } DivState
   deriving (Eq, Bits, FShow);

rule rl_loop1 (rg_state == Div_LOOP1);          // shift while it can
rule rl_loop2 (rg_state == Div_LOOP2);          // subtract while it can
method Bool result_valid = (rg_state == Div_DONE);
```

**No budget appears anywhere.** `rl_loop1` shifts while
`denom2 <= numer>>1`; `rl_loop2` subtracts while `numer >= denom`; the
cycle count is whatever the data required, and the consumer stalls
because `result_valid` is false.

`~/src/Piccolo` and `~/src/CHERI-Piccolo` are also present if a second
opinion on stage structure is wanted.

> **>>> WHY THIS IS THE KEY TO CYCLE ACCURACY AND NOT JUST TIDINESS.
> <<<** The Stretch timing tables are conditional on OPERAND VALUES:
> Table 2 adds cycles "for each additional pre-shift of 4", "for each
> additional norm. of 6", "if recomplement is necessary"; the divide
> loop is "data dependent"; Table 3's `M+` says "Unlike signs AB > CD,
> add .6(x/y + 1)". The roadmap's old plan was to feed the operands to
> `eboxClocks`. **If the box iterates, those numbers EMERGE instead** —
> they stop being a table to reproduce and become a consequence of the
> hardware.

## The recommended order (the owner's, verbatim in substance)

1. Introduce a pure `prepareExec` result and **eliminate the
   "call execution to discover the operand" protocol**. Today
   `rl_prepare` calls `ebox.exec` with no operands so that `execute()`
   "bails out" with `needsRead` — which makes execution serve as both a
   supposedly side-effect-free query and the operation that commits
   architectural effects. Every instruction arm must then do no
   irreversible work before noticing an operand is missing: a fragile
   contract.
2. Define typed `ExecRequest`, `ExecCompletion` and explicit commit
   records.
3. **Extract one genuinely iterative operation — divide is the best
   forcing case — into a request/response box.**
4. Generalise into `mkPAU` and `mkSAU`, the historical parallel and
   serial arithmetic machinery.
5. **Replace `ebusy` with actual response readiness** for boxed
   operations. Countdowns remain only where the machinery is not yet
   modelled.
6. Move decode/preparation fully into an I-box stage output bundle.
7. Split whole-instruction look-ahead entries into the historical
   operation / operand / store / recovery entries. (`LaKind` already
   admits this: every live entry is `Whole`.)
8. Add forwarding and accurate SAU/PAU overlap.

## Separate commit from calculation

Execution helpers currently call `st.writeWord`, `st.writeIndex`,
`st.setIndicatorBits` and the accumulator writes directly. Returning
effects as data instead — a single `ExecCompletion` applied by one
commit rule — buys a single architectural commit point, easier
suppression on alarms and protection violations, easier branch
recovery, less scheduler coupling, and boxes that can be tested without
instantiating storage.

**Not every write must go through one universal structure**, but
arithmetic should not mutate global architectural state halfway through
its own calculation.

## What NOT to do

Also the owner's, and these are the traps:

* Do not insert FIFOs between all stages.
* Do not mark every module `(* synthesize *)`.
* Do not pipeline combinational helpers merely to shorten files.
* Do not replace typed `DecodedInstr` variants with flat opcode records.
* Do not turn every pure arithmetic helper into a module.
* Do not split well-tested functions arbitrarily: **preserve the
  primary-source citations and the semantic seams.**

Pure functions are idiomatic for genuinely combinational bounded work.
Modules are warranted when the component owns state, consumes multiple
clocks, arbitrates a resource, or supports independent concurrency.

## The oracle for every step

The full suite — 5621 PASS / 0 FAIL as of 2026-10-28 — plus, for the
boxed operations, Volume 2's per-instruction atlas, which is throughput
measured on a machine WITH overlap. `docs/microarchitecture_roadmap.md`
M2 is where that becomes the oracle; the measured `VflInt` residual is
0.281 µs mean and 1.20 worst.
