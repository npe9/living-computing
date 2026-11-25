# PCF8584 IIC controller + PCF8582 EEPROM on the ULX3S (`mkIic`, step 5)

`Iic.bsv` is the Hobbit board's IIC bus at IOBASE+0x80 (io.h `IICADDR =
IOACK(Iic, 0x0080)`, `data` = S0 at +0 and `ctl` = S1 at +4). It contains
three parts: the PCF8584 controller, the PCF8582 256-byte EEPROM at bus
address 0xA4, and the PCF8574 LED latch at 0x40. The latter two are the
devices deviic.c talks to. It behaves as `tools/p9boot.py` `class Iic`
(`IIC_CHOICES`), which `docs/devices/README.md` "IIC" checks against the
Philips 1997 data sheets (PDFs not in the repository; the quotations are
there).

## Interface

The device bus contract in `docs/ulx3s_plan.md`, unchanged:

```
method Action request(Bit#(12) addr, Bit#(32) wdata, Bit#(4) be, Bool write);
method ActionValue#(Bit#(32)) response;   // next cycle; writes respond 0
method Bool    irq;                       // always False (deviic.c polls)
method Bit#(8) fault;                     // sticky, 0 = none
method Bit#(8) led;                       // PCF8574 latch, last byte written
method Bit#(8) ledWrites;                 // bytes written to it, mod 256
```

`addr[2]` selects S0 or S1. `addr[1:0]` is ignored, as in the model's
board. Any higher address bit set is a fault. A read returns the byte in
bits 7:0, and a write takes `wdata[7:0]` on byte lane 0. `led` is there for
the SoC top to put on the board's LEDs (`#2/led`, deviic.c `ledputbyte`).

## Behaviour

There are no SCL/SDA pins. The bus is inside the module and every transfer
completes at once, as in the model, so PIN is already clear at the driver's
first poll. Any added latency would change the PIN-poll reads that the
replay compares. The branches are the model's, in the model's order:

* **S1 read:** PIN 0x80, LRB 0x08 (the driver's `Nak`: no acknowledge) and
  BB 0x01 (`Busfree`: no START outstanding).
* **S0 write, ESO off:** writes S0' (own address, ES1/ES2 = 00) or S2
  (clock, ES1 = 1). Any other select is a fault.
* **S0 write, ESO on, in a write transfer:**
  * to the EEPROM: the first byte sets the word pointer, and the second
    byte is held in S0 as the repeated START's address with PIN set
    (`IIC_CHOICES['repeated-start']`);
  * to the LED latch: the byte is latched;
  * to any other address: no acknowledge (LRB).
* **S0 read:** returns S0. In a read transfer with ACK set it also fetches
  the next EEPROM byte into S0. The first read after the address is the
  data sheet's "dummy read" of the address byte.
* **S1 write, ESO on:**
  * STA without STO is a (repeated) START, with S0 as the address;
  * STO without STA is a STOP;
  * PIN during a read transfer completes the byte in progress (the
    driver's 0xC0);
  * PIN otherwise sets PIN.

**Repeated START: matched to the model, not to the data sheet.**
`docs/devices/README.md` item 7 rates this choice "unsettled, probably
contradicts". By the PCF8584 sheet, the 0xA5 that `eepromread` writes to S0
before STA goes out as a data byte. The EEPROM's pointer would then advance
to 1, and a real board would read its image one byte up. The RTL follows the
model, the behaviour reference, so its reads compare. Changing this means
changing both the model and the RTL, and laying the EEPROM image out one
byte up.

## What the EEPROM holds, and who reads it

Only deviic.c reads the EEPROM, once per boot, in `iicreset` →
`eepromread`. It reads 17 bytes from word 0 into `struct Eeprom eeprom`
(io.h: the 16 bytes of the struct, plus one more stored past its end).
`iicreset` is called from `chandevreset` (`rammain.c` for the terminal and
cpu kernels, `rommain.c` for the ROM). The `rom` configuration lists `iic`,
`rtc` and `ether` (`hobbit/rom`), so the ROM kernel reads the same bytes the
same way, and its network boot uses the same ether address. No other code
in the release touches the IIC. The ROM's boot configuration (`bootfile`,
`fs`, `sysname`...) is not in the EEPROM; it is in the NVRAM (`rtc.md` "What
the NVRAM holds").

| byte | io.h field | value (`iic_eeprom.hex`) | read by |
|---|---|---|---|
| 0..4 | `magic[5]` | a6 00 d9 20 10 (`EEPROMMAGIC "A600D92010"` as hex digits) | nothing checks it |
| 5..10 | `ea[6]` | 52:54:00:00:0b:0b | devether.c `etherreset`: the SONIC's station address |
| 11 | `mask` | 00 | unused |
| 12 | `clock` | 0x14 = 20 (MHz) | clock.c `delay()`: `ms * 1000 * ROUNDUP(clock, 2) / 2` loop passes |
| 13..15 | `dsp`, `pcb`, `rev` | 00 | unused |
| 16..255 | | 00 | byte 16 is the extra 17th byte |

So the EEPROM gives the kernel two things: the **ether address** and the
**CPU clock in MHz** that `delay()` is calibrated by. It holds no boot
configuration. The values are the model's (`IIC_CHOICES['eeprom']`). The
ether address is the one `tools/qemu1e/ndb.local` gives the Hobbit, so the
1e server's bootp answers it. A 1993 board's values are not in the release.

`iic_eeprom.hex` is generated from `p9boot.eeprom_image()`:
`python3 iic_eeprom.py` writes it, and `--check` confirms it matches.
`--ea` and `--clock` make a board-specific image. The clock byte must match
the clock the core really runs at on the board (25 MHz on the ULX3S today
would be 25) for `delay()` to last the time it claims. 20 is the model's
`CPU_HZ` and is the value the compare uses.

## Faults (fail loud)

| code | when | model |
|---|---|---|
| 1 | offset outside S0/S1 (`addr[11:3]` != 0) | `Stop` "read of / write of +0x.." |
| 2 | S0 read with ESO off | `Stop` "S0 read with the serial interface off" |
| 3 | S0 write with ESO off selecting S3 (vector) or ES1+ES2 | `Stop` "write to register select" |
| 4 | write without byte lane 0 | accepted, RTL-only |

## Area (yosys 0.51 `synth_ecp5`, `rtc_iic_synth.sh`)

| LUT4 | PFUMX | L6MUX21 | CCU2C | TRELLIS_FF |
|---:|---:|---:|---:|---:|
| 230 | 55 | 32 | 8 | 99 |

The EEPROM is never written, so yosys turns the 256 x 8 `RegFileLoad` into
logic (a ROM in LUTs) instead of a RAM primitive. A new image needs a
rebuild.

## Test

`rtc_iic_check.py` (see `rtc.md` "Test") also replays these IIC sequences:

* `iic_join.trace`: every PCF8584 access s9term made in JoinReplayTest, 71
  of them: `iicreset`, `eepromread` and `release`. All 60 reads also equal
  the values recorded in that run;
* deviic.c `ledputbyte` three times (latch value and count compared with the
  model's `led` list);
* `master()` to an address with no slave (0x90), then release;
* EEPROM reads from word 5, from word 250 across 255 → 0, and 40 bytes from
  word 0;
* two EEPROM reads in one run, from words 3 and 9, with a `ledputbyte`
  between them, so the START with a write address must clear `ptr_set`;
* PIN, STA together with STO, and ESO off;
* the faults above.

The IIC reads compared were S0 104 and S1 192, with 100 writes. 5 model
`Stop`s were matched by the RTL's fault code, and 1 RTL-only fault came
where expected. Discrimination (`rtc_iic_inject.py`) injected 9 IIC bugs,
and every one made the check fail. The observed failure sets are in
`rtc_iic_check.py`'s header. One injection, START not clearing `ptr_set`
(I8), passed until the two-read sequence was added.

The EEPROM's contents come from `iic_eeprom.hex`, which is resolved
against the working directory. A missing file reads as zeros in
simulation. See `rtc.md` "Integration notes for the SoC top".
