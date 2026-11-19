# PIM/m Bluespec sources

The model is `PimTypes`, `PimStages`, `PimALU`, `PimE`, `PimPU`; see
`../plan.md` and `../docs/pim_architecture.md`. The assembler and the
model ISA table are `../asm/pimasm.py` and `../docs/isa.md`.

## FPGA flow (ULX3S / ECP5)

`PimUlx3s.bsv` and `Top.v` are a downstream check, not the architecture.
The current build synthesizes and places/routes but does **not** close
timing: `nextpnr` reports 10.22 MHz against the 25 MHz target
(`fpga_build/nextpnr.log`). The failing clock-domain path is the store
read-data mux and cache-valid comparison gated by the E-stage valid:
97.8 ns total (36.0 ns logic, 61.8 ns routing), from
`pim.pu_astage_outR[120]` through `store_cacheValid` carry chains and
the `_0_CONCAT_IF_NOT_pu_estage_eValid_42_59_AND_NOT_ETC___d1143` LUT
mux to `store_reads.data0_reg[184]`.

Status: **not hardware-ready**. Do not present the bitstream as a
working PIM/m, and do not rest any cycle-accuracy claim on it. The
historical-accuracy rule in `../plan.md` forbids reordering the
documented pipeline for FPGA convenience; a future retime must be shown
not to change the documented structure.

## Regression

`../run_tests.sh` chains the assembler selftest, the ISA table check,
the Bluesim smoke test (`run_smoke.sh`) and the formal BMC
(`formal/run_formal.sh`).
