# PIM/m Bluespec sources

The model is `PimTypes`, `PimStages`, `PimALU`, `PimE`, `PimPU`; see
`../plan.md` and `../docs/pim_architecture.md`. The assembler and the
model ISA table are `../asm/pimasm.py` and `../docs/isa.md`.

The KL1-B execution path is `PimKL1B.bsv` (40-bit tagged word, 8-bit
register file, flat heap with `HP`, `step()` clock enable), separate
from the diagnostic ISA. Its testbenches are `PimKL1BTb.bsv` (REF-chain
deref through `read_variable`), `PimKL1BFailTb.bsv`,
`PimKL1BConstFailTb.bsv`, `PimKL1BStructTb.bsv` (`put_list`,
`put_constant`, `write_constant`), `PimKL1BIntTb.bsv`
(`put_integer`, `write_integer`) and `PimKL1BWaitTb.bsv`
(`wait_list`, `wait_integer`); `run_kl1b_tb.sh` builds and runs
all six. The implemented subset and the loud-failure rule for the
rest are in the module header.

The network model is `PimNU.bsv` (one NU's per-port FIFOs),
`PimLink.bsv` (one output port to one input port), `PimNURouted.bsv`
(the routed 5 × 5 crossbar with the route table and CPU-port arrival)
and `PimMesh.bsv` (a parameterized `w × h` mesh with deterministic XY
route tables). Their testbenches are `PimNUTb.bsv`, `PimLinkTb.bsv`,
`PimNURoutedTb.bsv` and `PimMeshTb.bsv`.

## FPGA flow (ULX3S / ECP5)

`PimUlx3s.bsv` and `Top.v` are a downstream check, not the architecture.
The recorded 10.22 MHz figure came from the 07:33 `nextpnr.log`, before
the WP3.1 `PimE` change, and does not reproduce. A fresh
`run_fpga_build.sh` run on the current tree reports **28.32 MHz**
(PASS at 25 MHz); a pristine `git archive HEAD` build measured
**55.35 MHz**. The earlier failing path was the store read-data mux and
cache-valid comparison gated by the E-stage valid (97.8 ns total in
that log); the fresh build no longer reports it as the limit.

Status: **not hardware-ready** until the owner re-decides WP2 on the
committed tree. Do not present the bitstream as a working PIM/m, and do
not rest any cycle-accuracy claim on it. The historical-accuracy rule in
`../plan.md` forbids reordering the documented pipeline for FPGA
convenience; a future retime must be shown not to change the documented
structure.

## Build check

`run_fpga_build.sh` reproduces the downstream ECP5 flow from a clean
tree: it regenerates `generated/*.hex`, recompiles `PimUlx3s.bsv` to
Verilog, runs Yosys, `nextpnr-ecp5 --85k --package CABGA381 --speed 6`
with `--timing-allow-fail`, and `ecppack --compress`, all in a fresh
`fpga_build/`. Required tools: `bsc` 2026.01, Yosys 0.51,
`nextpnr-ecp5` 0.6, `ecppack` (Trellis) 1.4. It prints the measured
Fmax and the WP2 gate; a timing miss is not a build failure, but missing
tools or a failed synthesis/place/route/bitstream step exits nonzero.

## Regression

`../run_tests.sh` chains the assembler selftest, the ISA table check,
the Bluesim smoke test (`run_smoke.sh`), the negative-opcode testbench
(`run_neg_tb.sh`), the KL1-B testbenches (`run_kl1b_tb.sh`), the
network-unit testbench
(`run_nu_tb.sh`), the link testbench (`run_link_tb.sh`), the routed
crossbar testbench (`run_nu_routed_tb.sh`), the mesh testbench
(`run_mesh_tb.sh`), the SDRAM-store testbench (`run_sdram_tb.sh`) and
the formal BMC (`formal/run_formal.sh`). The board build check is
`run_fpga_build.sh`.
