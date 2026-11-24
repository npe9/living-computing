# Provenance of IP reused in hobbit/fpga

Append-only and shared by every agent bringing up a ULX3S device
(`hobbit/docs/ulx3s_plan.md`).  The repository is public: a file copied in
from elsewhere is listed here with its source, the exact revision, a
checksum, and its licence terms as found.  Files whose source states no
redistribution terms are flagged for the owner.

## hobbit/fpga/dev/hdmi_tmds.v (step 4, the framebuffer; 2026-11-24)

| | |
|---|---|
| copied | modules `tmds_enc` (TMDS encoder, DVI 1.0 3.2.3) and `dvi_ser` (10:1 serializer through four `ODDRX1F`), lines 380-481, verbatim, no edits |
| from | `~/src/ulx3s-experiments/flute-lx50/src/Video_DVI.v` |
| repository | `github.com/npe9/flute-ulx3s` (the `origin` of that checkout), branch `lx50`, commit `8aaf3603f9716c39ac607f3531f180f2e02b3d74` |
| sha256 of the source file | `88ad876db6ecf37e124ddc3cabace67345dfc47fe89ea8aae2a6888ff82d5b0c` |
| author | the repository owner (written in the owner's Flute SoC sessions; not part of Bluespec's Flute) |
| licence as found at 8aaf3603 | none stated: `Video_DVI.v` has no licence header and that checkout has no top-level LICENSE (the tree's `Flute/LICENSE` covers Bluespec's Flute under `Flute/` only) |
| licence | **Apache License 2.0.** The owner stated on 2026-11-24 that npe9/flute-ulx3s is theirs and is licensed the same as Flute, every branch (lx50 included); `LICENSE` (Apache-2.0, a copy of Flute's) was pushed to flute-ulx3s `main` as commit `631c88b` (relayed by the lead, not fetched here). `hdmi_tmds.v` carries `SPDX-License-Identifier: Apache-2.0` and the attribution above. |
| status | cleared for the public repository |

Nothing else under `hobbit/fpga/dev/lcd*` or `hdmi*` is copied: the pin
sites in `hdmi_lcd.lpf` are facts about the board, read from the same
tree's `constraints/ulx3s_85f.lpf`; the PLL parameters are `ecppll -i 25
-o 325`'s; the bsc library cells (`BRAM2.v`, `FIFO2.v`) are read from the
bsc installation at build time and not copied.
