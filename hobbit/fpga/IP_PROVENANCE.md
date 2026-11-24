# IP provenance for the ULX3S build (append-only, shared)

Every file in `hobbit/fpga/` that came from somewhere else gets a section
here: what it is, where it came from (path and commit), its licence, and
what was changed. The policy is in `docs/ulx3s_plan.md`: only permissively
licensed files are copied from `~/src/ulx3s-experiments/`, which is read-only.
Add new sections at the end. Do not edit other sections.

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

## Step 5 addendum 2: secondary sources for the MCP7940N's registers, 2026-11-24

* **Copied: nothing.** The MCP7940N data sheet is still not on disk. Its
  download waits for the owner's approval. Two drivers written against the
  part were read, outside this repository and read-only, to check the
  register facts `rtc.md` had marked as inference:
  * Linux 6.17-rc7 `drivers/rtc/rtc-ds1307.c` (GPL-2.0), its `mcp794xx`
    paths, at `~/src/linux-cursor/linux`;
  * RTEMS `bsps/shared/dev/rtc/mcp7940m.c` (BSD-2-Clause), at `~/src/rtems`.
* Only bit positions and register addresses are cited (tags `[L]`, `[R]` in
  `fpga/dev/rtc_mcp7940n.h`). No code from either driver is used.
