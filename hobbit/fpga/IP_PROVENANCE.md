# IP provenance for the ULX3S build (append-only)

Every file under `hobbit/fpga/` that was not written for this project, or
that was derived from someone else's code, is listed here with its source,
licence and what was changed.  The repository is public: only permissively
licensed material is copied in.  Entries are appended, never rewritten;
each agent adds its own section.

## Quart and interrupt path (`fpga/dev/quart/`, `fpga/dev/intc/`), 2026-11-24

**Nothing third-party is copied.**  `HobbitQuart.bsv` (including its 8N1
transmitter and receiver), `HobbitIntc.bsv`, the testbenches and
`quart_trace.py` were written for this project.

Reviewed and *not* used:

- `~/src/ulx3s-experiments/flute-m50/src/Uart_Pins.bsv` (an 8N1 pin bridge
  for Flute's UART, 175 lines).  The file carries no copyright or licence
  line and its tree has no LICENSE file, so its terms are unknown; nothing
  was copied from it.  The Quart's pin logic is its own (2-flop
  synchroniser, mid-bit sampling, a one-byte hold as the SC68C94's receive
  shift register).

Used as tools or libraries, not copied into the tree:

- The Bluespec compiler's standard library (`FIFOF`, `RegFile`, `Vector`,
  `GetPut`, `StmtFSM`), and at synthesis time its Verilog cells
  (`$BLUESPECDIR/Verilog/FIFO2.v`, `RegFile.v`), read by `synth.sh` from the
  bsc 2026.01 installation.  bsc's `COPYING`: copyright Bluespec Inc.,
  BSD-3-Clause.

Behaviour sources (documents, not code): the SC68C94 product specification
(Philips, 27 April 1994) and the 1990 SC26C94/SC68C94 preliminary
specification, held out of git per `hobbit/docs/devices/MANIFEST.md`;
1st Edition Plan 9's `io.h`, `deveia.c`, `trap.c`, `devincon.c`
(`hobbit/tools/plan9-1e/`); `hobbit/tools/p9boot.py`'s device models.

## Step 5: RTC + NVRAM and IIC + EEPROM (`fpga/dev/Rtc.bsv`, `fpga/dev/Iic.bsv`), 2026-11-24

* **Copied: nothing.** Both devices are new BSV written from the Python
  models (`tools/p9boot.py` `Timekeeper` and `Iic`), the kernel drivers
  (`devrtc.c`, `deviic.c`) and the data-sheet quotations in
  `docs/devices/README.md`. No file from `~/src/ulx3s-experiments/` was read
  into or copied to this tree. Only the Flute tree's `test/rtc_test.c` was
  consulted, to confirm that the board has an MCP7940N on I2C (`rtc.md`),
  and nothing of it is used.
* **Library cells read at build time, not copied:** `RegFileLoad.v` and
  `FIFO2.v` from the bsc 2026.01 distribution (`$BLUESPECDIR/Verilog/`,
  Apache-2.0, distributed with bsc). bsc's generated Verilog instantiates
  them, and `rtc_iic_check.py` / `rtc_iic_synth.sh` read them from the
  install.
* **Data files:** `fpga/dev/iic_eeprom.hex` is generated from
  `p9boot.eeprom_image()` (`iic_eeprom.py --check`). `fpga/dev/rtc_nvram.hex`
  is 2040 zero bytes. The two `*_join.trace` files were captured from this
  repository's own model run of the release's `s9term`
  (`rtc_iic_capture.py`).

## Step 5 addendum: the MCP7940N link (`fpga/dev/RtcI2c.bsv`, `fpga/dev/rtc_mcp7940n.h`), 2026-11-24

* **Copied: nothing.** The I2C master (`RtcI2c.bsv`) and the behavioural
  MCP7940N (`rtc_mcp7940n.h`) are new. The Flute tree's `src/Board_IO.v`
  (an OpenCores-style I2C master) was not used.
* **Consulted, read-only:**
  * `~/src/ulx3s-experiments/flute-lx50/constraints/ulx3s_85f.lpf`
    lines 149-162, for the `gpdi_sda`/`gpdi_scl` sites (B19, E12) and their
    IO settings, quoted in `rtc.md`;
  * `flute-lx50/test/rtc_test.c` and `flute-lx50/linux-sw/dts-fp/flute-ulx3s.dts`,
    for the chip's address and register bits, marked `[T]` in
    `rtc_mcp7940n.h`.

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

## Owner's licence statement for npe9/flute-ulx3s, 2026-11-24

The owner stated in session on 2026-11-24 that github.com/npe9/flute-ulx3s
(every branch, including lx50, m50 and main, i.e. the trees under
`~/src/ulx3s-experiments/flute-*`) is theirs and is licensed the same as
Flute: Apache License 2.0. LICENSE was added to its main branch as commit
631c88b. Files from that repository that earlier sections recorded as having
no licence line (for example `flute-m50/src/Uart_Pins.bsv`) are therefore
Apache-2.0 and may be copied in with attribution.
