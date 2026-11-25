# ULX3S bring-up plan: the Hobbit and its devices on hardware

Goal: run 1st Edition Plan 9 on the Bluespec Hobbit core on a ULX3S
(ECP5 LFE5U-85F, 32 MB SDRAM, GPDI/HDMI, ESP32, FTDI UART, microSD),
bringing devices up one at a time. IP is reused from the owner's Flute
SoC trees in `~/src/ulx3s-experiments/` (read-only; only permissively
licensed files are copied in, with provenance in `fpga/IP_PROVENANCE.md`).

The board is shared with another session that runs Linux Flute on it.
Nothing here programs or detects the board, opens its serial port, or
touches its microSD until the owner approves a hardware window. Until
then every step is proved in Verilator/Bluesim against the Python device
models in `tools/p9boot.py` / `tools/p9term.py`, which already boot the
kernel to rc on the reference model.

## Memory map (from tools/p9boot.py, which follows io.h)

| range | device | Python model | RTL plan |
|---|---|---|---|
| 0x00000000-0x0007FFFF | PROM | `rom` | BRAM (boot ROM, see docs/boot_rom.md) |
| 0x80000000 + 8 MB | RAM | flat | SDRAM (32 MB on board) |
| 0xB0000000+0x00 | incon (interrupt controller) | `incon` | step 2 |
| 0xB0000080 | IIC (PCF8584 + PCF8582 EEPROM) | `Iic` | step 5 |
| 0xB0000100-0x1FF | Quart SC68C94 (console ch 0, keyboard ch 2, mouse ch 3) | `Quart` | step 2 |
| 0xB0003000 | LCD `Lcdisp` ctl(+0)/data(+4), write-only | `p9term.LcdPanel` | step 4 -> HDMI |
| 0xB8000000 (IONAK) +0x00 | ioctl | `ioctl` | step 2 |
| IONAK +0x80 | irq | `Irq` | step 2 |
| IONAK +0x100 | WD33C93A SCSI | `scsi` | later (SD-backed disk) |
| IONAK +0x2000-0x3FFF | MK48T02 RTC + NVRAM | `rtc` | step 5 |
| 0xA4400000 | SONIC DP83932 | `Sonic` | step 6, ESP32/PMOD (docs/ulx3s_ethernet.md) |

## Device bus contract

Each device is a standalone module (BSV preferred; Verilog only for
reused IP) behind one simple register port, so the devices can be built
and tested in parallel and dropped into the SoC top unchanged:

    req:  addr[11:0] (offset in the device window), wdata[31:0],
          byte-enable[3:0], write
    resp: rdata[31:0], one response per request, any latency
    irq:  level output(s)

The SoC top (`fpga/` + `bsv/HobbitUlx3s*.bsv`) owns address decoding,
the SDRAM, clocks and reset, and the core's bus. Each device ships
with a Verilator or Bluesim test that replays the same access sequence
into the RTL and the Python model and compares results.

## Steps, in order

1. **Core + SDRAM + UART, synthesis only.** LUT/BRAM/DSP and Fmax of
   the current core with the Flute tree's SDRAM controller; pick the
   clock; map RAM to SDRAM.
2. **Console.** Quart subset (channel 0 TX/RX, status, interrupt bits
   the kernel uses) on the FTDI UART, with incon/irq/ioctl so the
   kernel's interrupt path works. A forwarding mode can send any
   not-yet-built device's accesses over the UART to the Python models
   on the host, so the kernel can boot before every device is RTL.
3. **Kernel load.** Preload the kernel into SDRAM (UART download, or
   the real ROM's path once docs/boot_rom.md says what it is).
4. **Framebuffer.** `Lcdisp` emulation: the ctl/data write protocol
   of `LcdPanel` fills a 768 x 1024 x 2-bit buffer (196 KB: BRAM fits,
   measured 96 of the 85F's 208 DP16KD, 46%, and 114 of 208 with the
   core's 18; or SDRAM), scanned out over GPDI as
   HDMI. The portrait panel goes on a 1024 x 768 display rotated, or
   letterboxed on 1280 x 1024; the agent records the choice.
5. **RTC + IIC EEPROM.** Small devices; the RTC can start from a
   value loaded at configuration time.
6. **Ethernet.** SONIC-subset descriptor engine, with frames carried
   over the ESP32 to `tools/qemu1e/hub.py` by UDP, and later a PMOD PHY
   (see docs/ulx3s_ethernet.md for the survey and recommendation).
7. **Disk.** WD33C93A subset backed by an SD card image (on a card of
   our own, never the Flute session's card).

## Hardware windows

Every step lands with a bitstream and a written run procedure. The
owner approves a window with the Flute session; during it only the
FTDI port named in the procedure is used, and the board is restored
with `openFPGALoader -b ulx3s -r` afterwards.
