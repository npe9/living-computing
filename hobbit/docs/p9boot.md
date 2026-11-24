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

**Bitmap screen, the minimum chosen.**  The screen is plain RAM plus a
write-only LCD register pair that counts writes; no pixels are
interpreted.

**The console's input is Quart channel 0, not a scan-code keyboard.**
The shipped `screen.c` calls `kbdinit(2)` (the `kbd.c` scan-code
keyboard on channel 2 at 600 baud), but s9term has no `kbdinit` and no
`kbd.c` (`docs/s9term.md`: its `screen.c` predates `kbd.c`).  Tapping
`eiaspecial` in the run shows what the image does instead:

| step | call |
|---:|---|
| 127,557 | `eiaspecial(0, &printq, &kbdq.IOQ (0x8004fdfc), 19200)` |
| 127,705 | `eiaspecial(3, 0, &mouseq, 1200)` |

and `kbdq.putc` (kbdq+0x1034) then holds `kbdcr2nl`.  So the console is a
serial terminal on channel 0 at 19200 baud 8N1 -- output and input --
taking ASCII, CR made NL; channel 2 is never set up.  `--type
TEXT=REPLY` (CHOICES `console-input`) types REPLY on that line once the
screen has shown TEXT: `--type 'il]: =\r'` answers the prompt with
Return.  The mouse (channel 3) gets nothing.

Text reaches the screen ~0.4-0.5 M instructions before the serial line:
s9term's `putstrn` draws it first (`screenputs`, the font blitted in
software) and then calls `uartputs` (from `putstrn+0x96` / `+0xd0`):
pageinit's line is at `screenputs` at 2,131,084 and at `uartputs` at
2,621,219.  A reply typed with no `--think` delay arrives while the
prompt is still being drawn, so on channel 0 its echo (`\r\n`) comes
before the prompt; on the screen the order is the prompt, then `\n`.

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

The prompt goes to `#c/cons`, which s9term writes to the screen and then
(0.44 M instructions later, see the console above) to Quart channel 0.

Typing Return at it (`--type 'il]: =\r'`, the default counter rate) takes
`il`: `kbdcr2nl`, the echo, `etherattach` starting the
SONIC's kproc, and the screen shows

```
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
root is from (il, tcp, incon, 9600, 19200)[il]: 
sonic ether: 52 54 00 00 0b 0b
```

At **287,845,754** instructions (14.4 s of model time) `/boot` sends
its BOOTP request through the SONIC (`tests/test_p9boot.py`
`NetworkTest`, with `--pcap`):

```
52:54:00:00:0b:0b > ff:ff:ff:ff:ff:ff IP 0.0.0.0 > 255.255.255.255
UDP 68 > 67 len 372 BOOTP request htype 1 hlen 6 xid 00000000
chaddr 52:54:00:00:0b:0b file '' vend 'p9  '
```

406 bytes, IP header checksum good: the destination, the EEPROM's
address as source and in `chaddr`, type 0x0800 and `p9  ` all decode,
which checks the SONIC's byte lanes and CAM order at once.

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
frame bridge.  Answering the prompt itself needs only Return on the
console line (Quart channel 0): the default is `il`.

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
* **iic** — the PCF8584 and the PCF8582 EEPROM answer `deviic.c`
  (IIC_CHOICES, below): `iicreset` reads `io.h`'s `Eeprom`.
* **lcd** — `Lcdisp` at IOACK 0x3000 accepts and counts writes.
* **incon, IOCTL** — latches that record writes; an unexpected read
  stops the run.
* **idle-skip** — `runproc`'s idle loop retired in whole laps up to the
  next timed device event (section above); `--no-idle-skip` turns it off.
* **console-input** — the console line is Quart channel 0 (section "The
  console"); `--type TEXT=REPLY` types REPLY there once the screen shows
  TEXT, `--think SECONDS` after it.

### Quart (`QUART_CHOICES`, `io.h` `Quart`/`Duart`, `deveia.c`)

* **sr** — TxRDY|TxEMT while the transmitter is enabled: a byte written
  leaves at once.  RxRDY while the receive FIFO holds a byte, FFULL at
  three.
* **rx** — typed bytes arrive one character time apart (1 start bit,
  mr1's data and parity bits, mr2's stop bits at csr's rate under
  BRGSet2: 0.52 ms at 19200 8N1) into a three-byte FIFO; a byte that
  finds it full, or the receiver disabled, waits on the line (no overrun
  is modelled).  grxfifo/rxfifo pop; an empty FIFO reads 0.
* **cr** — the enable/disable bits and MrReset/RxReset/TxReset change
  state; the rest are accepted and ignored.
* **isr** — TxRDYa/TxRDYb while enabled; CtrRDY once the counter expires,
  until a read of `stop`; RxRDYa/RxRDYb while the FIFO is not empty
  (uartsetup's mr1 has bit 6, FFULL interrupts, clear).
* **counter** — started by a read of `start`; CtrRDY every
  2·count/(3.6864 MHz/16) s.
* **counter-period** — s9term's `clockinit` is older than the release's:
  it writes ctu = ctl = 0xFF (count 65535), a CtrRDY every 0.569 s by the
  formula, while its `tsleep` divides by MS2HZ = 40 (HZ = 25).  The
  default follows the count; `--counter-period 0.04` gives the 25 Hz the
  software assumes, a stated deviation that makes `sleep(1000)` in
  `/boot` last 25 ticks of 0.04 s instead of 25 of 0.569 s.
* **cir** — a write of `update` latches the highest pending enabled
  source: the counter (cir 0x14, gicr = 2·duart), then a receiver (cir
  0x0C RxAvail, gicr = channel, gibcr = bytes in its FIFO), then a
  transmitter (cir 0x08, gicr = channel, gibcr = 1); nothing pending
  reads 0.  The order is a choice: the bidding registers (bcr) that set
  it on the part are written by eiasetup but not modelled.
* **irq** — IRQ 1 while any isr bit is enabled in its DUART's imr.

### WD33C93 (`WD_CHOICES`, `scsi.c`)

* **reset** — after Creset the chip interrupts with status 0x01 if the
  own-ID register has Eaf, else 0x00 (the WD33C93A's two reset codes).
* **no-targets** — every selection ends in selection timeout (0x42).
* **irq** — IRQ 10 while Intrpend is set.

### IIC and the EEPROM (`IIC_CHOICES`, `deviic.c`)

No PCF8584 or PCF8582 data sheet is in the release or the repository;
the behaviour is inferred from `deviic.c`'s code and comments.

* **bus** — S1 reads PIN (clear once a byte has gone or come), LRB
  ("Nak", set when no slave acknowledged), BB ("Busfree", set with no
  START outstanding); S0' and S2 are written through the ES1 select
  before ESO; transfers complete at once.  On the bus: the EEPROM (0xA4)
  and the LED latch (0x40); other addresses are not acknowledged.
* **repeated-start** — `eepromread` writes the read address 0xA5 to S0
  after the word address, reads S1, waits, then sets STA: the byte is
  taken as the repeated START's address, not written to the EEPROM.
* **receive** — the first S0 read after the address returns the address
  byte (the driver: "We get some junk back"); each S0 read with ACK set
  starts the next byte; the control write 0xC0 (ACK off) completes the
  byte in progress.  So `eepromread` stores 17 bytes: the 16 of
  `Eeprom` and one past it, into `rtclock` (EEPROM byte 16 = 0).
* **eeprom** — magic `a6 00 d9 20 10` (`EEPROMMAGIC "A600D92010"` read as
  hex digits; nothing checks it), ether address **52:54:00:00:0b:0b**
  (`--ea`; locally administered, and the address `tools/qemu1e/ndb.local`
  gives the Hobbit, so the 1e server's `ip/bootp` answers it), mask 0,
  clock 20 (MHz: `delay()` loops `ms*1000*clock/2` times, consistent
  with CHOICES `clock`), dsp, pcb, rev 0.  The values of a 1993 board
  are not in the release.  Reading it adds 6,535 instructions before the
  prompt (22,537,089 at 25 Hz).

### SONIC (`SONIC_CHOICES`, `devether.c`)

No DP83932 data sheet is in the release or the repository.  Every point
is what s9term's `devether.c` relies on; where the driver leaves a
detail open, QEMU's model of the same part (`hw/net/dp8393x.c`, read
2026-11-23 from qemu master) is followed, and each such point says so.

* **registers** — io.h's words, 16 bits wide; reset state `cr =
  Rst|Stp|Rxdis`; writing `cr` with Rst clear while in reset only leaves
  reset (QEMU), which `reset()`'s `cr = Rst; dcr = ...; cr = 0` needs.
* **isr** — write-one-to-clear (the driver writes back what it read);
  IRQ 9 while `isr & imr`.
* **rra** — Rrra (and each used-up buffer) reads the 4-word resource at
  `urra:rrp`, advances `rrp` by 16 and wraps it at `rea`; completes at
  once.
* **cam** — Lcam reads `cdc` entries of (cep, cap0..2) at `urra:cdp`
  (the upper half from urra: QEMU), each cap two address bytes low byte
  first (the driver's `cap0 = ea[1]<<8|ea[0]`), then the enable word;
  isr Lcd.
* **transmit** — Txp sends from `utda:ctda` (size, fragment count, per
  fragment ptr0/ptr1/size, link), at once (no line time, no collisions),
  writes status 0x0001 (PTX: neither Host 0 nor Interface ~0, as the
  driver tests), sets `ctda` to the link and goes on unless the link has
  EOL; then isr Txdn.  `ctda` keeping the EOL link makes the next bare
  `cr = Txp` (etheroput) start at the next descriptor (QEMU does the
  same).  No FCS on transmit.
* **receive** — an accepted frame goes into the current buffer with its
  CRC-32 FCS, padded to 4 bytes; the descriptor at `urda:crda` gets
  status Prx (|Bc, |Lpkt when fewer than `eobc` words remain), byte count
  (+4, which etherkproc subtracts), buffer address, sequence number;
  then, unless its link has EOL, `in_use = 0` (Host), `crda = link`, isr
  Pktrx; with EOL the descriptor is kept (isr Rde) and its link re-read
  at the next frame (QEMU).  Lpkt reads the next resource, so with
  `eobc` = buffer words − 2 each frame has its own buffer and buffers
  advance with descriptors, as `etherkproc`'s `rb[rh]` needs.
  Descriptor words are written zero-extended (QEMU's 32-bit mode; the
  driver compares the whole word with Host = 0).
* **filter** — Pro (unicast), Brd (broadcast), an enabled CAM entry;
  transmitted frames are not looped back.
* **dma** — physical addresses (PADDR is the identity) through the
  board's RAM, bytes in the little-endian lanes the kernel uses
  (CONFIG.KL); the first frame checks it.

### The wire (`ETHER_CHOICES`)

`--pcap FILE` writes every frame both ways, stamped with model time.
`--ether-peer HOST:PORT --ether-local HOST:PORT` exchanges frames with
a UDP peer, one raw ethernet frame per datagram (QEMU's `-netdev dgram`
framing); idle model time then runs at the wall clock (the idle skip
waits on the socket for as long as the model time to the next event),
busy time at the model's ~100,000 instructions/s.  `--ether-replay
PCAP` answers with a recorded session's frames; `--ether-script PCAP`
delivers frames at their timestamps.  With nothing attached, a transmit
stops the run.

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

1. **The join** with the 1e file server in QEMU (`tools/p9join.py`,
   below).
2. s9term's clock rate (QUART_CHOICES `counter-period`): whether the
   board's counter ran from a faster clock than the release's formula
   assumes is not settled by anything in the release (above).
