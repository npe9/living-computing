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
