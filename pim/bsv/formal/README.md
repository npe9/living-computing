# Formal checks for the PIM/m PU

This directory runs the smoke diagnostic as a bounded model check and adds
three path properties for the PIM/m processing unit: the multi-way tag
jump, the undefined-opcode decode error, and the unwritable-register
fault.  The smoke is a riscv-formal style post-state check: the machine
runs from reset to halt, and the wrapper asserts the architectural
result the ISA model requires.  Each property has a deliberately broken
twin; the twin must fail and produce a VCD counterexample, so none of
the harnesses is vacuous.

The multi-way and fault properties need microprograms that the assembler
does not emit today.  They are built as formal-only images from the
assembler's own encodings (`gen_path_images.py` imports
`asm/pimasm.py`); no BSV source or assembler source is modified.

## Files

| file | meaning |
| --- | --- |
| `gen_verilog.sh` | builds the fixed and injected Verilog snapshots from the current BSV tree; writes the capped `formal_images/` |
| `gen_path_images.py` | writes the multi-way, decode-error and fault images (imports `asm/pimasm.py`) |
| `pim_smoke_formal.v` | smoke wrapper: reset/start, post-halt register scan, assertions |
| `pim_smoke.sby` | BMC of `build/fixed/mkPimPUFormal.v` |
| `pim_smoke_bug.sby` | smoke BMC of `build/buggy/mkPimPUFormal.v` (expected FAIL) |
| `pim_multiway_formal.v` | multi-way tag-jump wrapper, post-halt a1/a2 scan |
| `pim_multiway.sby` | multi-way BMC of `build/multiway/mkPimPUFormal.v` |
| `pim_multiway_bug.sby` | multi-way BMC of `build/multiway_bug/` (7-bit index, expected FAIL) |
| `pim_decode_error_formal.v` | decode-error wrapper: error within 20 cycles, no halt |
| `pim_decode_error.sby` | decode-error BMC of `build/fixed/` |
| `pim_decode_error_bug.sby` | decode-error BMC of `build/decode_bug/` (error swallowed, expected FAIL) |
| `pim_fault_formal.v` | fault-path wrapper: error within 20 cycles |
| `pim_fault.sby` | fault BMC of `build/fixed/` |
| `pim_fault_bug.sby` | fault BMC of `build/fault_bug/` (badWrite arm removed, expected FAIL) |
| `run_formal.sh` | regenerate and run all eight jobs, checking the expected outcomes |
| `formal_images/` | truncated smoke images and the path-test images (generated) |
| `build/` | generated netlists: `fixed`, `buggy`, `multiway`, `multiway_bug`, `decode_bug`, `fault_bug` |
| `pim_smoke/`, `pim_smoke_bug/`, `pim_multiway/`, ... | generated sby work directories; safe to delete |
| `last_run.log` | captured output of a `run_formal.sh` run (generated) |

## What is checked

### Smoke post-state

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

`pim_smoke_formal.v` drives `EN_start` high, holds `RST_N` low for two
cycles, then lets `mkPimPU` run.  The PU is multi-cycle, so "one cycle"
here means the cycle after the last instruction retires: once `halted`
is high the pipe rule is off and every architectural register and the
local store are frozen.  The wrapper has one register read port, so it
walks the five locations one per cycle and asserts each against the
model value.  Because the state is frozen, all five samples are the
same final state.  A bounded-liveness assertion fails if the machine
has not halted by cycle 70 (Bluesim retires in 48 steps), so a PASS
cannot come from asserting on a machine that never reaches the state.

All post-state assertions are gated on `RST_N == 1 && halted`.  The
generated PU registers have no initial values; Yosys therefore models
them as arbitrary (`$anyinit`) in state 0, and an ungated assertion
would fire on that arbitrary pre-reset state instead of on the machine.
The generated registers do have a `RST_N` reset input; the wrapper's
two-cycle low pulse puts them in the defined reset state.

### Multi-way tag jump (WP4.4)

`pim_multiway_formal.v` checks the E-stage `condMultiway` path with the
program in `formal_images/multiway_program.hex`:

```
0  put_imm a3, 100
1  put_imm a4, 0x17f
2  put_imm a5, 0x100
3  put_imm a6, 0x101
4  put_imm a7, 0x1ff
5  load    a0, [a3+0]     ; mem[100] = 0x01_0000002a (type int, MRB set)
6  jmp_tag a0, int, a6
7  load    a2, [a3+1]     ; mem[101] = 0xff_0000002a (type 0x7f, MRB set)
8  jmp_tag a2, int, a7
9  halt
```

The microprogram at uBase `0x0e` is `condMultiway` with `srcA = rs`
and `last = 0`, so the two-cycle jump actually fetches and executes the
target microinstruction.  The jump table is the model's 256-entry,
8-bit-indexed table, and the base is the micro-PC `0x0e`:

| table index | offset | target | target microinstruction |
| --- | --- | --- | --- |
| `0x01` | `0x30` | `0x3e` | `a1 <- a6 = 0x101` (correct) |
| `0x00` | `0x40` | `0x4e` | `a1 <- a5 = 0x100` (decoy) |
| `0xff` | `0x50` | `0x5e` | `a2 <- a7 = 0x1ff` (correct) |
| `0x7f` | `0x60` | `0x6e` | `a2 <- a4 = 0x17f` (decoy) |

The harness asserts, after the halt, `a1 = 0x101` and `a2 = 0x1ff`, and
`error = 0`.  An index that drops MRB (the old 7-bit `tagType` lookup)
selects the `0x00`/`0x7f` decoys and fails.  The `0xff` case is the top
entry of the 256-entry table, so the top of the 8-bit index range is
reachable; a 7-bit index cannot reach it.

The model has no S-stage multi-way table.  `M92` p.429 describes the S
stage setting up a multi-way offset from the R-fetched operand's tag,
but the model only implements the E-stage table.  This check is the
E-stage table; the paper does not state whether the S and E tables are
the same physical RAM (see `docs/pim_architecture.md`).  The base
`eUPC + offset` is the model's unconfirmed offset-from-current-micro-PC
choice (`docs/pim_architecture.md`, contradiction item 8); this image
exercises that choice and does not claim it as documented.

The jump table's read address is internal to the generated netlist and
is not an interface port.  Yosys does not resolve a dotted hierarchical
reference to it from the wrapper (it becomes an implicit, undriven
wire), so the property is checked end-to-end through the target
microprograms rather than by asserting the internal address wire.

### Decode error path (WP4.4)

`pim_decode_error_formal.v` uses
`formal_images/decode_error_program.hex`:

```
0  0x0f_00000000   undefined opcode; decode entry 0x0f has valid=0
1  halt            must never be reached
```

`PimE.cycle`'s empty-E branch sees `!dec.valid` and latches
`errorSeen`; the top-level `fault` rule turns that into `error`.
`estage.stopped()` includes `errorSeen`, so the pipe stops and the halt
at PC 1 does not retire.  The documented loud failure is checked two
ways:

* `error` must be high by cycle 20 (the assertion is at `cyc == 20`);
* `halted` must stay low after reset.

The fixed tree passes; the injected `errorSeen <= False` branch treats
the undefined opcode as a no-op, reaches the halt, and fails the
`!halted` assertion at step 11.

### Fault path (WP4.4)

`pim_fault_formal.v` uses `formal_images/fault_program.hex`:

```
0  jmp a6      (microcode at uBase 0x0d, from fault_wcs.hex)
1  halt
```

The `jmp` microinstruction writes `rselPc` (41).  `PimRegFile::write`
does not accept PC as a destination; it sets `badW`, and `PimPU`'s
`fault` rule latches `error`.  The write itself is dropped, so the
machine PC is not corrupted.  The harness asserts `error` high by cycle
20.

Model scope, labelled: the `fault` rule raises `error`, but the `pipe`
rule only checks `estage.stopped()` (`haltSeen || errorSeen`), not
`errorR`.  This fault therefore does not freeze the pipe; the program
continues to its halt and reports both `error` and `halted`.  The
property checked here is the documented loud failure, `error`;
`halted` is deliberately not constrained.  Adding a freeze would be a
model change, not a harness change.

### Injected twins

`gen_verilog.sh` builds one broken copy per property.  Nothing in the
BSV tree is edited; each patch is applied to a private copy under
`build/`:

| variant | patch |
| --- | --- |
| `buggy` | `PimE.bsv`: `eFetched <= Invalid;` (the old fetched-operand regression) |
| `multiway_bug` | `PimE.bsv`: `jumpTable.sub(zeroExtend(tagType(wordTag(av))))` |
| `decode_bug` | `PimE.bsv`: `errorSeen <= False;` in the `!dec.valid` branch |
| `fault_bug` | `PimPU.bsv`: `fault` rule drops `|| regs.badWrite()` |

The `buggy` variant is the original regression: `PimE.bsv:131` in the
pre-rewrite tree returned the pipelined `eFetched` word instead of
`mem.sub(eEA)`.  The current E stage cannot express that exact mistake:
the R stage attaches the fetched word to the instruction it belongs to
(`R2S.fetched`, carried into `S2E` and latched as `Maybe#(Word)
eFetched`), so `rselFetch` reading it is correct by construction.  The
injection reintroduces the same observable failure by dropping the
R-stage result when E loads, so `fromMaybe(wordInt(0), eFetched)`
supplies 0 for every `rselFetch` operand.

## Running

From the repository root (`pim/`):

```sh
bsv/formal/run_formal.sh
```

The script regenerates the six netlists and the images, then runs, in
order, the fixed and broken smoke, the fixed and broken multi-way jump,
the fixed and broken decode error, and the fixed and broken fault.  It
exits 0 only if every fixed run passes and every broken run fails, and
each broken run must have written `engine_0/trace.vcd`.

or, step by step:

```sh
# 1. regenerate the Verilog snapshots and the image sets
bsv/formal/gen_verilog.sh

# 2. smoke: fixed PASS, fetched-operand twin FAIL
sby -f bsv/formal/pim_smoke.sby
sby -f bsv/formal/pim_smoke_bug.sby

# 3. multi-way tag jump: fixed PASS, 7-bit-index twin FAIL
sby -f bsv/formal/pim_multiway.sby
sby -f bsv/formal/pim_multiway_bug.sby

# 4. decode error: fixed PASS, swallowed-error twin FAIL
sby -f bsv/formal/pim_decode_error.sby
sby -f bsv/formal/pim_decode_error_bug.sby

# 5. fault: fixed PASS, removed-badWrite twin FAIL
sby -f bsv/formal/pim_fault.sby
sby -f bsv/formal/pim_fault_bug.sby
```

`sby` must run from the repository root: the `[files]` section names
sources relative to the process working directory (sby does not resolve
them relative to the `.sby` file).  The equivalent tool invocations are
`xd://sby_formal` with `{"config": "bsv/formal/pim_smoke.sby", "force":
true}`, and the same for the other seven configs; the tool already runs
from the repository root.

### Solver

All jobs use `smtbmc yices` (`[engines]`) with `mode bmc`, `depth 80`,
`vcd on`.  The default z3 engine starts to blow up around step 20 on
this design (the arrays are bit-vector indexed); yices discharges the
smoke and multi-way jobs in 35-40 seconds.  `bitwuzla` is installed but
the smtbmc bridge fails with a broken pipe on this machine.  The
multi-way broken twin is the slow injection (about two minutes); the
decode and fault jobs take a second.

## Observed results

The last run of `bsv/formal/run_formal.sh` (2026-11-19) exited 0 and
printed:

```
fixed smoke: PASS
buggy smoke: FAIL as expected (rc=2)
multiway fixed: PASS
multiway bug: FAIL as expected (rc=2)
decode error fixed: PASS
decode error bug: FAIL as expected (rc=2)
fault fixed: PASS
fault bug: FAIL as expected (rc=2)
```

The corresponding `sby` verdicts and first failing assertions were:

### Smoke, fixed tree

```
summary: engine_0 (smtbmc yices) returned pass
DONE (PASS, rc=0)
```

No trace is written on PASS.

### Smoke, fetched-operand twin

```
engine_0: ##   0:00:35  Assert failed in pim_smoke_formal: pim_smoke_formal.v:94.25-94.61
summary: counterexample trace: bsv/formal/pim_smoke_bug/engine_0/trace.vcd
summary:   failed assertion pim_smoke_formal._witness_.check_assert_pim_smoke_formal_v_94_26 at pim_smoke_formal.v:94.25-94.61 in step 53
DONE (FAIL, rc=2)
```

Line 94 is the `a4` assertion.  In the witness, at `#510 ns` the PU is
halted with no error and `scan = 0`: `readReg_r = 2`, `readReg =
0x000000002a` (`a2`), `readMem = 0x000000002a`, `pc = 17`.  At
`#520 ns` `scan = 1` and `readReg_r = 4`: `readReg = 0x0100000000` —
`a4` is `tagInt|MRB` with data 0 instead of 42.  `a5` shows the same at
`#530 ns`.  The store to address 100 and `a2` are correct, isolating
the fault to the fetch-operand path.

### Multi-way jump, fixed tree

```
summary: engine_0 (smtbmc yices) returned pass
DONE (PASS, rc=0)
```

The post-halt scan reads `a1 = 0x00_0000_0101` and `a2 =
0x00_0000_01ff`, and `error = 0`.

### Multi-way jump, 7-bit-index twin

```
engine_0: ##   0:01:41  Assert failed in pim_multiway_formal: pim_multiway_formal.v:85.25-85.61
summary: counterexample trace: bsv/formal/pim_multiway_bug/engine_0/trace.vcd
summary:   failed assertion pim_multiway_formal._witness_.check_assert_pim_multiway_formal_v_85_19 at pim_multiway_formal.v:85.25-85.61 in step 38
DONE (FAIL, rc=2)
```

Line 85 is the `a1` assertion.  The witness shows the decoy path: at
`#370` (`smt_step` 37) the machine is halted, `scan = 0`, `readReg_r =
1` and `readReg = 0x0000000100` — the `jump[0x00]` decoy was taken for
tag `0x01`; this is the sample the assertion rejects (sby step 38).
At `#380` (`smt_step` 38) the scan advances to `scan = 1`,
`readReg_r = 2` and `readReg = 0x000000017f` — the `jump[0x7f]` decoy
was taken for tag `0xff`.  `error = 0` throughout.

### Decode error, fixed tree

```
summary: engine_0 (smtbmc yices) returned pass
DONE (PASS, rc=0)
```

The undefined opcode at PC 0 raises `error` and the halt at PC 1 never
retires, so `halted` stays low.

### Decode error, swallowed-error twin

```
engine_0: ##   0:00:00  Assert failed in pim_decode_error_formal: pim_decode_error_formal.v:52.7-52.23
summary: counterexample trace: bsv/formal/pim_decode_error_bug/engine_0/trace.vcd
summary:   failed assertion pim_decode_error_formal._witness_.check_assert_pim_decode_error_formal_v_52_10 at pim_decode_error_formal.v:52.7-52.23 in step 11
DONE (FAIL, rc=2)
```

Line 52 is `assert (!halted)`.  The witness shows `halted = 1` and
`error = 0` at step 11: the undefined opcode was swallowed, and the
halt at PC 1 retired.

### Fault, fixed tree

```
summary: engine_0 (smtbmc yices) returned pass
DONE (PASS, rc=0)
```

The bad PC write sets `badW`; the `fault` rule raises `error` before
cycle 20.  The program also reaches its halt, as described above.

### Fault, removed-badWrite twin

```
engine_0: ##   0:00:00  Assert failed in pim_fault_formal: pim_fault_formal.v:57.40-57.54
summary: counterexample trace: bsv/formal/pim_fault_bug/engine_0/trace.vcd
summary:   failed assertion pim_fault_formal._witness_.check_assert_pim_fault_formal_v_57_12 at pim_fault_formal.v:57.40-57.54 in step 21
DONE (FAIL, rc=2)
```

Line 57 is the `error` assertion at `cyc == 20`.  The witness shows
`halted = 1`, `error = 0` at step 21: the unwritable-register write was
discarded without the loud failure.

## Inspecting a witness

```
xd://vcd_inspect  file = bsv/formal/pim_multiway_bug/engine_0/trace.vcd
```

The smoke trace has 560 `$var` entries and ends at `#540` (54 states:
2 reset + halt + 5-cycle scan); the useful window is the tail,
`#510`..`#530`.  The multi-way trace has 545 `$var` entries and ends at
`#390`; the interesting window is `#370`..`#380` (the a1 and a2
samples).  The decode-error and fault traces have 512 and 510 `$var`
entries and end at `#120` and `#220`; they include `halted`, `error`,
`pc`, `cyc` and the DUT's `pu_estage_errorSeen`, `pu_errorR`,
`pu_regs_badW`.  A plain `vcd_inspect` call (the transition cap is
2000) spends its budget on the many signals initialised at `#0`, so
for the tail raise `max_transitions` as far as allowed, or read the
time range directly from the VCD.

## Formal-only adaptations of the generated Verilog

Nothing in the BSV tree is edited.  `gen_verilog.sh` regenerates each
variant with

```sh
bsc -verilog -g mkPimPUFormal -p .:$BLUESPECDIR/Libraries -u PimPUFormal.bsv
```

from a private copy of `PimTypes`, `PimStages`, `PimALU`, `PimE`,
`PimPU`, and `PimPUFormal`, and then makes two changes to the generated
netlist:

1. **Memory caps.**  `RegFileLoad` instances are reduced to the
   addresses the selected diagnostic can touch.  The smoke uses the
   tight 16/16/128 caps; the multi-way image needs the full 256-entry
   jump table and micro-PCs up to `0x6e`, so that variant uses a
   128-entry WCS and a 256-entry jump table.  The images are assembled
   from the same `asm/pimasm.py` encodings into `formal_images/`; the
   shared `../generated` directory is not touched.

   | memory | smoke / decode / fault | multiway | evidence |
   | --- | --- | --- | --- |
   | local store / program | 128 words | 128 words | smoke PC 0..12 + data 100; multiway PC 0..9 + data 100/101; error/fault programs PC 0..1 |
   | WCS | 16 | 128 | smoke WCS 0..14; multiway WCS 0..14 plus `0x3e/0x4e/0x5e/0x6e`; error/fault WCS 0..14 |
   | decode table | 16 | 16 | smoke opcodes 0..14; decode error entry `0x0f`; fault opcode `0x0d`; multiway opcodes 1, 2, 8, 0x0e |
   | jump table | 16 (never read) | 256 | multiway indexes `0x00`, `0x01`, `0x7f`, `0xff`; the other programs never use `condMultiway` |

   The cap is performance, not abstraction convenience: with the full
   64K x 40 / 32K x 64 images, `write_smt2` emits one array-init
   equality per address (~100k constraints) and the solver never
   finishes the initial state.  The multi-way table is 256 entries
   (8-bit index) and the capped WCS is 128 entries; both cover every
   address the image reads.  The `.hi` rewrites are asserted per
   instance by `gen_verilog.sh`, and the fresh bsc values are checked
   (`16'd65535`, `15'd32767`, `8'd255`); a bsc output change stops the
   script instead of silently building a different model.

2. **Store write gated by reset.**  `RegFileLoad` has no reset port,
   and the arbitrary pre-reset state of the PU can have a store write
   enabled.  The first clock edge would then commit that write before
   the reset takes effect, corrupting memory (observed: program word 0
   overwritten).  The generated local-store instance's write enable
   becomes `.WE(store_mem$WE & RST_N)`.  In the BSV the pipe rule is
   off while `running` is false, so this only restores the reset
   invariant; it does not change post-reset behaviour.

The multi-way program and the two path microprograms are data, not
netlist rewrites: `gen_path_images.py` writes `multiway_program.hex`,
`multiway_wcs.hex`, `multiway_decode.hex`, `multiway_jump.hex`, the
`decode_error_*` set and the `fault_*` set.  The fault WCS entry at
`0x0d` is the only changed microinstruction (`dst = rselPc`); the
multi-way WCS entry at `0x0e` is the only changed standard routine
(`condMultiway`, `srcA = rs`, `last = 0`), plus the four target
microinstructions.

## Scope and trust

* `mode bmc` with depth 80 is a bounded check, not an inductive proof.
* A solver PASS is not a kernel proof; record it as
  `kernel_checked: false` if it is entered as a proof artifact.  The
  existing `proof_artifacts/` entries cover the smoke; the three path
  checks are reported BMC runs and are not entered there.
* The multi-way check covers the two tags `0x01` and `0xff` and the
  four table entries above.  It does not enumerate all 256 tags; it
  proves the two poles (MRB-only and type+MRB) and the top of the index
  range, and the 7-bit twin shows the defect is observable.
* The multi-way table index is an 8-bit `Bit#(8)` and the table is 256
  entries, so the index is structurally in range.  The target micro-PC
  is a 15-bit value and the WCS is 32K entries; the formal image uses
  target addresses `0x3e`..`0x6e`.  The internal read-address wire is
  not an interface port, so the check is end-to-end.
* The fault property checks the `error` flag only.  The model does not
  gate the pipe on `errorR`, so this fault does not freeze the machine;
  that is a labelled model gap, not a harness omission.
* The S-stage multi-way table is not modelled; the paper does not say
  whether S and E share the physical table.  This check is the E-stage
  table.
* The Bluesim smoke remains the executable reference; these checks
  exercise the same RTL through the generated netlist.
