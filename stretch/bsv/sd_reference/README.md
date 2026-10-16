# `bsv/sd_reference/` — the SD tape path, measured but NOT wired in

These files are a **reference design, not part of the build.** Nothing
in `bsv/` imports them and `build.sh` does not compile them. They are
here because they were synthesised and measured on this machine and
that work should not have to be redone; see `docs/tape_data_path.md`
for the full write-up.

| file | what it is |
|---|---|
| `TapeSource.bsv` | the agent's independent `Server#(TapeRequest,TapeResponse)` design, with a 24-bit word address, `atEnd` and `capacity` |
| `TapeSourceFile.bsv` | host-file backing via value-typed `import "BDPI"` — **built and run**, six streaming words out of a real file |
| `TapeSourceSD.bsv` | the ULX3S microSD leg |
| `TapeTb.bsv` | its testbench |
| `host_tape.c` | the BDPI C side |
| `sd_reader_shim.v`, `sdcmd_ctrl_split.v` | split-tristate SD core files, needed because yosys will not take the inout form |

**This is NOT what `bsv/StretchTapeSource.bsv` currently does**, and the
difference is deliberate. The in-tree version is the minimum change
that puts a request/ready/response boundary where a combinational value
method used to be, keeping `TapeWords = 16` and every existing test
green. This directory is where that boundary is eventually going.

**Three things here are worth taking when it goes:**

1. **The 24-bit word address.** The in-tree `TapeIndex` is four bits,
   inherited from `TapeWords = 16`. A reel is ~16 MB.
2. **`atEnd` in the response.** The in-tree version has no way to say
   "you have run off the end of the mounted image", so End Exception
   is still decided by the caller comparing against `TapeWords`. On a
   card-backed source there is nothing to compare against — the agent
   flagged that `capacity = maxBound` on the SD leg silently makes
   `io_tape.strap`'s End Exception path unreachable on hardware, and
   did not pick a home for the image's true word count. Neither have I.
3. **The `Server`/`mkConnection` idiom**, which matches
   `~/src/ulx3s-experiments/flute-ulx3s/src/Sdram_Controller.bsv` —
   the house style for an external-memory peripheral on this board.

**TWO INDEPENDENT DESIGNS CONVERGED ON REQUEST/RESPONSE** — this one
and `bsv/StretchTapeSource.bsv`, written without reference to each
other. That is the main evidence that the shape is right, and it is
worth more than either design's details.

**MEASURED, by yosys 0.51 `synth_ecp5` on this machine** (see
`docs/tape_data_path.md` for the commands and the caveats, including
that these are standalone deltas and do not account for flattening):

| | LUT4 | FF | CCU2C | DP16KD |
|---|---|---|---|---|
| whole SD tape path | 788 | 720 | 112 | 2 |
| `mkStretchIO` today | 8,102 | 5,317 | 0 | 0 |
| `mkStretchIO` with `tapeImg` removed | 7,077 | 4,293 | 0 | 0 |

Net **≈ −237 LUT4, −304 FF, +112 CCU2C, +2 DP16KD** — the SD path very
nearly pays for itself by deleting sixteen 64-bit registers, and the
carry cost is +0.27% against the ~41,070 CCU2C that
`docs/fpga_feasibility.md` says actually decides the part.
