# `tools/p9boot.py` — the shipped kernel on the reference model (A4)

`tools/p9boot.py` boots `tools/plan9-1e/hobbit/s9term`, the kernel image
the 1e release ships for the Hobbit terminal, on `sem/hobbit_sem.py`, the
reference (one-instruction) model.  It loads the `-H1` image at its own
addresses, starts at the entry in kernel mode in the PRM's reset state,
and models the devices the kernel touches, from `io.h`, the device
drivers in `tools/plan9-1e/sys/src/9/hobbit/` and the PRM.  It uses the
image's own symbol table (`docs/s9term.md`) to say which function is
executing.  s9term was built from sources older than the release ships,
so every device sequence below was checked against s9term's disassembly,
not only against the C.

```sh
# The first console line (the regression test, ~2.1 M instructions, 25 s):
python3 hobbit/tools/p9boot.py hobbit/tools/plan9-1e/hobbit/s9term \
    --max-steps 4000000 --until '\n'
# On to the boot program's prompt (see "How far it gets"; ~30 s):
python3 hobbit/tools/p9boot.py hobbit/tools/plan9-1e/hobbit/s9term \
    --max-steps 400000000 --progress 20000000 \
    --until 'root is from' --out console
```

`--out DIR` writes the console bytes, one file per channel; `--until TEXT` stops once the
screen has shown TEXT; `--progress N` prints where the PC is every N
instructions.  The run prints each first-reached function with its
instruction number, every exception and interrupt the model takes (the
first 100), the model time, and the bytes of each console channel.

## The console

The kernel prints to two places, and both are captured:

* **`screenputs`** — the terminal's own screen.  The kernel draws text
  into a bitmap in RAM (`screen.c`: `gscreen.base = xalloc(...)`) and
  copies it to the LCD controller (`Lcd` below).  The harness reads the
  string at `screenputs`'s entry (arguments at CSP+4, CSP+8) rather than
  decoding pixels: a *harness tap*, which changes no state.
* **`uart0`** — s9term's `printq` also goes to Quart channel 0 (the
  `uartputs` path, `\n` as `\r\n`), which is what a serial console would
  show.  These are the bytes the device model collected.

**Bitmap screen and keyboard, the minimum chosen.**  The screen is plain
RAM plus a write-only LCD register pair that counts writes; no pixels are
interpreted.  The keyboard is Quart channel 2 (`kbdinit(2)`, 600 baud)
and the mouse channel 3 (`eiaspecial(3, ..., 1200)`); nothing is
connected to either, so they never receive a byte (QUART_CHOICES `sr`,
`isr`).  A typed reply to the boot prompt would be the next device
feature (RxRDY on channel 2 with scan codes, `kbd.c`).

## Milestones (2026-11-23)

| instructions | reached |
|---:|---|
| 0 | `_startup` (physical, PSW = 0) |
| 2,064 | `_virtual` — the first instruction after the CRET that turns on the MMU |
| 125,203 | `main` |
| 125,437 | `confinit` |
| 2,088,445 | `mmuinit` |
| 2,127,625 | first `print` (pageinit's) |
| 2,131,084 | `screenputs` has the whole first line |
| 2,621,219 | first byte on Quart channel 0 (`uartputs`) |
| 2,635,067 | `clockinit` |
| ~2,650,000 | `chandevreset`: `iicreset`, `eiareset`, `rtcreset`, `inconreset`, `dkreset`, `scsireset`, `wrenreset`, `etherreset` |
| 2,859,426 | `touser` — the first CRET to user mode (initcode) |
| 2,859,432 | first exception: the CRET's CATCH read fault on the user stack, handled by `fault` |
| 2,869,118 | `sysexec` of `/boot` |
| 2,877,513 | `/boot` running in user mode, demand-paging its text |
| 2,907,111 | `alarmkproc`; then `runproc` idles waiting for the clock |

The first console line, byte for byte, on both channels:

```
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
```

## How far it gets

At the counter rate the hardware formula gives (one tick per 0.569 s,
QUART_CHOICES `counter-period`) the run reaches `/boot`'s prompt after
**286,970,654 instructions** and 14.367 s of model time, 26 clock
interrupts, in about 30 s of host time: 284,013,188 of those
instructions are laps of the idle loop that the idle skip (below)
retires without executing.

With `--counter-period 0.04` (25 Hz) the same prompt comes after
**22,530,554 instructions** (1.145 s of model time, 26 clock
interrupts).  That count was measured first without the idle skip (6
minutes of host time) and is reproduced exactly with it (29 s), which
`tests/test_p9boot.py` `PromptTest` pins:

| instructions | reached |
|---:|---|
| 3,291,609 | the first `clockintr` (Quart CtrRDY through `eiaintr`) |
| 22,488,849 | `/boot` after its `sleep(1000)`: `sysopen("#c/cons")` |
| 22,504,334 | `envopen`/`envread` of `#e/cputype`, `#e/terminal` |
| 22,526,752 | an ENTER into the next user stack page: exception 8 by p. 3-21's check, mapped by `fault`, restarted |
| 22,530,554 | the prompt is on the screen |

The screen then holds, byte for byte (`--out` writes it):

```
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
root is from (il, tcp, incon, 9600, 19200)[il]: 
```

The prompt goes to `#c/cons`, which s9term writes to the screen only;
Quart channel 0 carries the kernel's own `print` output (the first line).

Without `--counter-period` the clock ticks every 0.569 s of model time,
and `sleep(1000)` (25 ticks) needs ~14 s of model time; with the idle
skip that costs nothing, so the override is no longer needed to get
anywhere.

## The idle skip (CHOICES `idle-skip`)

s9term's idle loop is `runproc`'s `while(runhiq.head==0 &&
runloq.head==0);` after `spllo()` (port/proc.c), which in the image is
four instructions at `runproc+0x08..+0x1e` (0x8000649a):

```
+0x08  dffc 0000 0000 8004 d300   compare $0 with runhiq.head (runhiq+8)
+0x12  1007                       JMPFN +0x20: a process is ready, leave
+0x14  dffc 0000 0000 8004 d418   compare $0 with runloq.head (runloq+8)
+0x1e  1ff5                       JMPTY +0x08: both empty, again
```

It stores nothing, so only an interrupt can end it.  `find_idle_loop`
checks these parcels in the loaded image and refuses to run otherwise.
With the PC at the head, both heads 0, IPL 7, no interrupt asserted, no
timer interrupt enabled, and the last two laps of equal cost, the
harness retires N laps at once: `steps += 4N`, `cycles += N x lap`,
with N the largest number that still ends *before* the next timed
device event (the Quart counter, a scripted console byte, an inbound
frame).  The laps executed after that, the interrupt and everything
after it are the unskipped run's, instruction for instruction:

| run | instructions | cycles | host time |
|---|---:|---:|---:|
| to the prompt, 25 Hz, no skip (before the skip existed) | 22,530,554 | | ~6 min |
| the same with the skip (19,573,088 retired by 25 skips) | 22,530,554 | 22,890,723 | 29 s |
| 3.4 M instructions at a 4 ms tick, no skip / skip (7 skips) | 3,400,000 | 3,757,855 | 34 s / 27 s |

and in the last row the two runs end with the same PC, PSW, stacks,
interrupt and exception lists, functions reached, console bytes, Quart
state and every RAM word (`IdleSkipEquivalenceTest`).  The Hobbit has no
idle, halt or wait instruction (none of Table 3-1's 46 mnemonics, pp.
3-1..3-2, `docs/isa_inventory.md` §2), and s9term spins, so this loop is
the only idle state there is.  With
nothing timed pending, the loop could never end, and the run stops
saying so.

### The clock rate (QUART_CHOICES `counter-period`), reconsidered

s9term's `clockinit` (0x8000f780) loads the counter with a constant:
`acr = 0xF0` (BRGSet2|TimerD16), `ctu:ctl = 0xFFFF` (`MOV $0xffff`,
then `>>8` and `&0xff` into ctu and ctl), where the shipped source
computes `Crystal/(2*16*HZ)` = 4608.  Its HZ is 25 (`tsleep` divides by
MS2HZ = 40; mem.h `HZ 25`).  So the image's software assumes 25 ticks a
second and programs a count that, by the 68C94's timer formula with the
3.6864 MHz crystal deveia.c names, gives 1.76 a second.  Nothing in the
release says which is wrong (a different crystal on the 1992 board, a
counter clock not divided by 16, or a kernel whose clock ran slow); the
default stays the formula, and `--counter-period 0.04` stays a stated
deviation, now needed for nothing but shorter model time.

## The root file system: what `/boot` asks the machine for

s9term's `/boot` (`bootcode`, 26,796 bytes in the image's data) offers,
in order, `il, tcp, incon, 9600, 19200` (the method table's strings,
read from the image: `il`, `tcp`, `incon "config 1 64 restart dk"`,
`9600 "#t/eia1"`, `19200 "#t/eia1"`); the default is **il**.  There is
no `local` method in this image (the release's `termlocal` adds one).
From `sys/src/9/boot/ip.c` and `async.c`, and the strings in the image:

* **il** (default) and **tcp** — 9P over IL (port 17008, auth 17024) or
  TCP, on IP over the **SONIC** ethernet (`#l/ether`, DP83932 at
  0xA4400000, IRQ 9).  `/boot` first broadcasts **BOOTP** on UDP 67 for
  its IP address, mask, gateway and file server address (or prompts "My
  IP address" etc.), then ARPs.  It needs: (1) an ethernet address —
  `myetheraddr` reads `#l/ether`'s address, which `devether.c` takes from
  the IIC EEPROM (`eeprom.ea`), now zero (CHOICES `iic`): the IIC/
  PCF8582 must answer with a real address; (2) the SONIC's transmit
  (`cr` Txp, the TDA descriptors in RAM) and receive (RRA/RDA
  descriptors, Rxen, `isr` PktRx, IRQ 9) — SONIC_CHOICES `no-network` is
  the minimum that passes `reset()` and stops at the first transmit.
  The join to a 1e file server elsewhere is a frame transport for those
  descriptors (e.g. a host tap or socket carrying ethernet frames to
  QEMU's NE2000), with a BOOTP answer from either side.  The 1e 386 file
  server speaks IL, so this is the direct path.
* **incon** — Datakit over the incon board (`#i/ctl`, `dkmux`): needs a
  Datakit peer, not a 9P server.
* **9600 / 19200** — `#t/eia1`, i.e. **Quart channel 1** at 9600 or
  19200 baud, with `push async` and `push dkmux` (`config 1 16 restart dk
  4`) and then `dkconnect`: Datakit URP over the serial line, again a
  Datakit peer rather than raw 9P.  Its needs from the machine are small
  (RxRDY/RxAvail on channel 1, QUART_CHOICES `sr`, `cir`) but the far
  end must speak Datakit.

So the shortest path to a QEMU 1e file server is **il over the SONIC**:
an IIC EEPROM with an ethernet address, SONIC transmit/receive, and a
frame bridge.  Answering the prompt itself needs a keyboard byte on
Quart channel 2 — or none at all: pressing return takes the default,
`il`.

## Modelling choices

Each is also a `CHOICES`/`*_CHOICES` entry in `tools/p9boot.py`, printed
nowhere else.  Where the release is silent they are choices, stated as
such.

### The board (`CHOICES`)

* **memsize** — 8 MB of RAM at 0x80000000; `PPage0.memsize` = 8 MB.  The
  ROM measures memory (`rommain.c` `meminit`); a 1993 board's size is not
  in the release.  The first console line depends on it (1364 pages).
* **ram-init** — RAM the image does not load reads as 0.
* **ppage0** — the ROM's hand-off page (`rom.h` `PPage0`): memsize,
  argc = 0, `env.nentry` = 0, everything else 0, except:
* **fpi-vector** — PPage0+0x74, which `_virtual` copies into VB+8 and
  VB+12 (the trapped-niladic and unimplemented-instruction vectors),
  holds a sentinel in the ROM's range: the release ships no ROM image
  (the floating-point interpreter lives there), so reaching it stops the
  run.
* **reset** — PC = the entry, PSW = CONFIG = SHAD = 0 (p. 1-35);
  SP = MSP = ISP = VB = STB = 0 (undefined after reset, p. 1-36).  The
  ROM's state at its jump to the kernel is not known.
* **irq-level** — every board interrupt reaches the part at IL 6:
  s9term's vector table sends only interrupt 6 to `interrupt()`.
* **irq-status** — `Irq.status0/1` are the raw requests (bit n = io.h
  IRQ n); IL 6 is asserted while `status & mask` ≠ 0.
* **clock** — model time is the sum of the records' Chapter 4 cycles at
  20 MHz, the lower of the data sheet's two rated clocks.  It paces the
  Quart counter, the kernel's clock interrupt.
* **iic** — the PCF8584 never reports the bus free, so the EEPROM (ether
  address, `eeprom.clock`) stays zero and `delay()` waits for nothing.
* **lcd** — `Lcdisp` at IOACK 0x3000 accepts and counts writes.
* **incon, IOCTL** — latches that record writes; an unexpected read
  stops the run.

### Quart (`QUART_CHOICES`, `io.h` `Quart`/`Duart`, `deveia.c`)

* **sr** — TxRDY|TxEMT while the transmitter is enabled: a byte written
  leaves at once.  RxRDY never: nothing is connected.
* **cr** — the enable/disable bits and MrReset/RxReset/TxReset change
  state; the rest are accepted and ignored.
* **isr** — TxRDYa/TxRDYb while enabled; CtrRDY once the counter expires,
  until a read of `stop`.
* **counter** — started by a read of `start`; CtrRDY every
  2·count/(3.6864 MHz/16) s.
* **counter-period** — s9term's `clockinit` is older than the release's:
  it writes ctu = ctl = 0xFF (count 65535), a CtrRDY every 0.569 s by the
  formula, while its `tsleep` divides by MS2HZ = 40 (HZ = 25).  The
  default follows the count; `--counter-period 0.04` gives the 25 Hz the
  software assumes, a stated deviation that makes `sleep(1000)` in
  `/boot` last 25 ticks of 0.04 s instead of 25 of 0.569 s.
* **cir** — a write of `update` latches the highest pending enabled
  source: the counter (cir 0x14, gicr = 2·duart), then a transmitter
  (cir 0x08, gicr = channel, gibcr = 1); nothing pending reads 0.
* **irq** — IRQ 1 while any isr bit is enabled in its DUART's imr.

### WD33C93 (`WD_CHOICES`, `scsi.c`)

* **reset** — after Creset the chip interrupts with status 0x01 if the
  own-ID register has Eaf, else 0x00 (the WD33C93A's two reset codes).
* **no-targets** — every selection ends in selection timeout (0x42).
* **irq** — IRQ 10 while Intrpend is set.

### SONIC (`SONIC_CHOICES`, `devether.c`)

* **no-network** — the commands `reset()` waits on (Rrra, Lcam) complete
  at once and read back clear; nothing is received, `isr` stays 0; a
  transmit command stops the run.

## What the reference model gained (`hobbit_sem.System`)

All of it exists only when a `State` carries a `System`; without one the
user-level model is unchanged (`tests/test_sem_extended.py`, the golden
programs and `test_p9run.py` are green).  Unit tests:
`tests/test_sem_system.py`, each proved discriminating by injection
(observed failures in its header).

* The CPU escape (0x2C00): mode 7 of the following instruction names a
  control register, 1..12 (Table 1-24, p. 1-26); writes at user level
  are exception 5; register 0 or > 12 is exception 6.  SP writes also set
  MSP; PSW, STB masked to their defined bits; CONFIG.KL switches the
  byte order.
* CSP = ISP when PSW bit 9 is clear (p. 1-12): ENTER, RETURN and POPN
  move the ISP, CATCH is a no-op, stack-offset operands use the ISP.
* SHAD follows the CSP; KCALL, KRET, CRET set it (p. 1-16).
* CONFIG.SE gates the stack cache; CONFIG.PX extends 16-bit absolutes
  with the PC's bits 31:29 (p. 1-23).
* The MMU (Chapter 2): STB → STE → (nonpaged base/bound or PTE), the
  C/S/U/W/V checks, R and M written back; faults 7/8/9 with FAULT.
* The exception (p. 1-38), interrupt (p. 1-37), unimplemented-
  instruction and trapped-niladic sequences (p. 1-39); KCALL's frame and
  every vector read are made at kernel level whatever the PSW's level.
* CRET's CATCH portion (p. 3-15) runs under the restored PSW, block by
  block; a fault is exception 8 at the restored PC with SP kept — 1e's
  `trap.c` relies on it for the first entry to user mode (its "CRET
  fails" and "CATCH/ENTER read fault" comments).
* ENTER's store check of the target and new MSP (p. 3-21): exception 8
  after the flush, SP unchanged, so the kernel maps the next user stack
  page and the ENTER restarts.
* TIMER1/TIMER2 count (Table 1-2), not yet used by s9term.

Not modelled: the TLBs and their flushes (no-ops; the walk is made on
every access), the instruction cache and prefetch, tracing, NMI edge
sensitivity, bus errors other than "no device".

## What blocks next

1. **Input.**  `/boot` now reads the reply from `#c/cons`: the keyboard
   is Quart channel 2 (`kbd.c` scan codes at 600 baud).  A return key
   (RxRDY/RxAvail on channel 2 and `kbd.c`'s code for it) takes `il`.
2. **The network** for `il`: the IIC EEPROM's ethernet address and the
   SONIC's descriptor-driven transmit and receive (above), then a frame
   bridge to the file server.
3. s9term's clock rate (QUART_CHOICES `counter-period`): whether the
   board's counter ran from a faster clock than the release's formula
   assumes is not settled by anything in the release (above).
