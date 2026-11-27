# Vendored: Flute's FPU

`FPU.bsv` is Flute's floating-point unit, `src_Core/CPU/FPU.bsv` from
https://github.com/bluespec/Flute at commit
`9b2b056527429e509c719c417a588b3ea594949b`. It is used under the Apache
License 2.0; `LICENSE` beside this file is Flute's own copy. Flute has
no NOTICE file. The copyright line is Bluespec, Inc.'s (2013-2019) and
is kept in the file header.

The PIM/m core wraps it as `mkPimmFBox` (`pim/bsv/PimmFBox.bsv`), with
request/response methods. It is instantiated once inside `mkPimmExec`
and does the four PIM/m float operations, add, subtract, multiply and
divide, in IEEE single with round to nearest even (`docs/float.md`).

## Changes from the original

- The `` `ifdef``s are resolved for this configuration: single precision
  only (ISA_D off), the divider on (INCLUDE_FDIV), no square root
  (INCLUDE_FSQRT off). The text of the branches kept is unchanged.
- `import ISA_Decls :: *;` is removed. The two declarations the file
  uses from that package, `typedef Bit #(0) Token;` and the `FpuOp`
  enum, are copied in from Flute's `src_Core/ISA/ISA_Decls.bsv` at the
  same commit.

Nothing else was changed. Flute's `FBox_Core.bsv` and `FBox_Top.bsv`
are not vendored, because they are bound to RISC-V decoding. The
conversions and compares in `PimmFBox.bsv` follow FBox_Core's use of
the bsc `FloatingPoint` library (`vFloatToFixed`, `vFixedToFloat`,
`compareFP`) and say so in comments.

Build: put `-p vendor/flute:+` (with the build's other paths) on the bsc
command line. `run_pimm_lockstep.sh`, `run_pimm_shell.sh` and
`run_pimm_apps.sh` do this.
