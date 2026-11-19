# Formal smoke check for the PIM/m PU

This directory runs the same diagnostic program as the Bluesim smoke test
(`../PimSmoke.bsv`, `../run_smoke.sh`) as a bounded model check.  It is a
riscv-formal style post-state check: the machine runs from reset to halt, and
the wrapper asserts the architectural result the ISA model requires.

The check fails on a deliberately broken copy of the netlist and produces a
VCD counterexample, so the harness itself is not vacuous.

## Files

| file | meaning |
| --- | --- |
| `gen_verilog.sh` | builds `build/fixed/mkPimPU.v` from the current BSV tree and `build/buggy/mkPimPU.v` with the fetched-operand regression; writes `formal_images/` |
| `pim_smoke_formal.v` | wrapper: reset/start, post-halt register scan, assertions |
| `pim_smoke.sby` | BMC of `build/fixed/mkPimPU.v` |
| `pim_smoke_bug.sby` | BMC of `build/buggy/mkPimPU.v` (expected FAIL) |
| `run_formal.sh` | regenerate and run both jobs, checking the expected outcomes |
| `formal_images/` | truncated assembler images used by the capped memories |
| `build/`, `pim_smoke/`, `pim_smoke_bug/` | generated; safe to delete |
| `last_run.log` | captured output of the last `run_formal.sh` (generated) |

## What is checked

The diagnostic is the smoke test's program (see `../generated/program.lst`):
put immediates, add, store/load through `a3 = 100`, set MRB, dereference,
tag jump and halt.  The required final state is:

| location | value |
| --- | --- |
| `a2` | `0x00_0000_002a` (int 42) |
| `a4` | `0x01_0000_002a` (int 42, MRB set) |
| `a5` | `0x01_0000_002a` |
| `a7` | `0x00_0000_0000` (the tag-jump path skips the `put_imm a7, 99`) |
| `mem[100]` | `0x00_0000_002a` |
| `pc` | 17 |

`pim_smoke_formal.v` drives `EN_start` high, holds `RST_N` low for two cycles,
then lets `mkPimPU` run.  The PU is multi-cycle, so "one cycle" here means the
cycle after the last instruction retires: once `halted` is high the pipe rule
is off and every architectural register and the local store are frozen.  The
wrapper has one register read port, so it walks the five locations one per
cycle and asserts each against the model value.  Because the state is frozen,
all five samples are the same final state.  A bounded-liveness assertion fails
if the machine has not halted by cycle 70 (Bluesim retires in 48 steps), so a
PASS cannot come from asserting on a machine that never reaches the state.

All post-state assertions are gated on `RST_N == 1 && halted`.  The generated
PU registers have no initial values; Yosys therefore models them as arbitrary
(`$anyinit`) in state 0, and an ungated assertion would fire on that arbitrary
pre-reset state instead of on the machine.

## Running

From the repository root (`pim/`):

```sh
bsv/formal/run_formal.sh
```

or, step by step:

```sh
# 1. regenerate the two Verilog snapshots (uses the newest Homebrew bsc)
bsv/formal/gen_verilog.sh

# 2. BMC the fixed tree
sby -f bsv/formal/pim_smoke.sby

# 3. BMC the reverted-fetch tree (expected FAIL, writes a VCD)
sby -f bsv/formal/pim_smoke_bug.sby
```

`sby` must run from the repository root: the `[files]` section names sources
relative to the process working directory (sby does not resolve them relative
to the `.sby` file).  The equivalent tool invocations are
`xd://sby_formal` with `{"config": "bsv/formal/pim_smoke.sby", "force": true}`
and the same for `pim_smoke_bug.sby`; the tool already runs from the
repository root.

### Solver

Both jobs use `smtbmc yices` (`[engines]`) with `mode bmc`, `depth 80`, `vcd
on`.  The default z3 engine starts to blow up around step 20 on this design
(the arrays are bit-vector indexed); yices discharges all 80 steps in 35-50 seconds.  `bitwuzla` is installed but the smtbmc bridge fails with a
broken pipe on this machine.

## Observed results

Fixed tree (current `PimPU`/`PimE`, smoke PASS with 48 steps):

```
engine_0: ## ... Status: passed
summary: engine_0 (smtbmc yices) returned pass
DONE (PASS, rc=0)
```

No trace is written on PASS.

Reverted tree:

```
engine_0: ##  0:00:30  BMC failed!
engine_0: ##  0:00:34  Assert failed in pim_smoke_formal: pim_smoke_formal.v:94.25-94.61
summary: counterexample trace: bsv/formal/pim_smoke_bug/engine_0/trace.vcd
DONE (FAIL, rc=2)
```

Line 94 is the `a4` assertion.  In the witness, at `#510 ns` the PU is halted
with no error and `scan = 0`: `readReg_r = 2`, `readReg = 0x000000002a`
(`a2`), `readMem = 0x000000002a`, `pc = 17`.  At `#520 ns` `scan = 1` and
`readReg_r = 4`: `readReg = 0x0100000000` — `a4` is `tagInt|MRB` with data 0
instead of 42.  `a5` shows the same at `#530 ns`.  The store to address 100 and
`a2` are correct, isolating the fault to the fetch-operand path.

## Inspecting the witness

```
xd://vcd_inspect  file = bsv/formal/pim_smoke_bug/engine_0/trace.vcd
```

The trace has 557 signals and ends at `#540` (54 states: 2 reset + halt +
5-cycle scan).  The useful window is the tail, `#510`..`#530`; the hierarchy
lists `pim_smoke_formal.{halted,error,scan,readReg,readReg_r,readMem,pc}` and
the DUT's `dut.regs_aRegs_*`, `dut.estage_eFetched`, `dut.regs_pcR`.  A plain
`vcd_inspect` call (the transition cap is 2000) spends its budget on the 557
signals initialised at `#0` and does not reach the tail, so for the tail raise
`max_transitions` as far as allowed, or read the time range directly from the
VCD; the values above were read from the full trace.

## Formal-only adaptations of the generated Verilog

Nothing in the BSV tree is edited.  `gen_verilog.sh` regenerates with

```sh
bsc -verilog -g mkPimPU -p .:$BLUESPECDIR/Libraries -u PimPU.bsv
```

from a private copy of `PimTypes`, `PimStages`, `PimALU`, `PimE`, `PimPU`, and
then makes two changes to the generated netlist:

1. **Memory cap.**  `RegFileLoad` instances are reduced to the addresses this
   diagnostic can touch: local store 128 words, WCS/decode/jump 16.  The
   images are assembled into `build/images` by `gen_verilog.sh`
   (`asm/pimasm.py --out-dir`) and truncated; the shared `../generated`
   directory is not touched.  The reason for the cap is performance, not
   abstraction convenience: with the full
   64K x 40 / 32K x 64 images, `write_smt2` emits one array-init equality per
   address (~100k constraints) and the solver never finishes the initial
   state.  The cap is sufficient here:

   | memory | used range | evidence |
   | --- | --- | --- |
   | local store / program | PC 0..12, data 100 | assembler listing `program.lst`; the only store is at `a3+0`, `a3=100` |
   | WCS | 0..14 | all nonzero `wcs.hex` entries; every microinstruction has `last=1`, `next=0`, no `condMultiway` |
   | decode | 0..14 | nonzero `decode.hex` entries are opcodes 0..14, each mapping to uBase 0..14 |
   | jump table | never read | the only tag condition used is `condTagEq` (uPC 14), not multiway |

   Yosys still emits init constraints for every capped address (including
   zeros), so the images are fully defined inside the cap.

2. **Store write gated by reset.**  `RegFileLoad` has no reset port, and the
   arbitrary pre-reset state of the PU can have a store write enabled.  The
   first clock edge would then commit that write before the reset takes
   effect, corrupting memory (observed: program word 0 overwritten).  The
   generated local-store instance's write enable becomes
   `.WE(store_mem$WE & RST_N)`.  In the BSV the pipe rule is off while
   `running` is false, so this only restores the reset invariant; it does not
   change post-reset behaviour.

These two rewrites are asserted by `gen_verilog.sh`; if a bsc output change
renames the ports or parameters the script stops instead of silently building
a different model.

## The reverted regression

The original bug was `PimE.bsv:131` in the pre-rewrite tree: `rselFetch`
returned the pipelined `eFetched` word instead of `mem.sub(eEA)`.  The current
E stage cannot express that exact mistake: the R stage now attaches the fetched
word to the instruction it belongs to (`R2S.fetched`, carried into `S2E` and
latched as `Maybe#(Word) eFetched`), so `rselFetch` reading it is correct by
construction.

`build/buggy` therefore reintroduces the same defect at its new location: the
E-load branch drops the R-stage result,

```
eFetched <= Invalid;      // was: eFetched <= x.fetched;
```

so `fromMaybe(wordInt(0), eFetched)` supplies 0 for every `rselFetch` operand.
That is the same observable failure as the old regression (loads deliver a
stale/absent fetched value) and it is what the `a4` counterexample shows.  The
real `PimE.bsv` is untouched.

## Scope and trust

* `mode bmc` with depth 80 is a bounded check, not an inductive proof.
* A solver PASS is not a kernel proof; record it as
  `kernel_checked: false` if it is entered as a proof artifact.
* The Bluesim smoke remains the executable reference; this directory checks
  the same post-state through the generated RTL.
