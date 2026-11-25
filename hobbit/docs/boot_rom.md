# The Hobbit boot ROM (Plan 9 1st Edition)

What the boot ROM of a 1993 Bell Labs Hobbit board did, read from the
release's own sources, built with the release's own tools on the
reference model, and run there from reset.  Paths below are under
`hobbit/tools/plan9-1e/sys/src/9/` unless they start with `hobbit/`.

**In one paragraph.**  The ROM is not a small monitor: it is a complete
Plan 9 kernel, configuration `rom` (`hobbit/rom`), linked to run out of
the EPROM (`hobbit/mkfile:60-63`, rule `9rom`).  `hobbit/roml.s` takes
the part from reset to virtual mode and copies the ROM's data segment
to RAM; `hobbit/rommain.c` sizes memory and starts the usual kernel
(devices, processes, IP, Datakit).  Its `/boot` is not the ordinary
boot program but `boot/romboot.c`, a monitor with the prompt `>>>`,
eight one-letter commands, and an environment kept in the timekeeper's
non-volatile RAM.  Its `b` command attaches a file server by any of the
kernel's boot methods (IL or TCP over the SONIC Ethernet, `incon` or
Datakit over a serial line), reads a Plan 9 kernel image with
`crackhdr`, copies its text and data to their physical link addresses,
leaves arguments and the environment in the page at RAMBASE (`PPage0`,
`hobbit/rom.h`), and jumps to the entry in physical mode through
`#B/boot` (`port/devboot.c`).  The ROM also carries the floating-point
interpreter every loaded kernel uses (`PPage0+0x74`), and a crashing
kernel's `softreset` jumps back into it with its registers saved for the
monitor's `r` command.

Sources the release ships for it: `hobbit/roml.s` (356 lines),
`hobbit/rommain.c` (217), `hobbit/rom.h` (47), `hobbit/rom` (the
configuration, 78), `boot/romboot.c` (784), `port/devboot.c` (135),
`hobbit/mkrom.c` (96), and the `9rom` rule of `hobbit/mkfile`.  The
release ships no ROM image (`docs/p9boot.md`, "The ROM's fpi").

## 1. The build: what the mkfile says

```
9rom:	roml.$O boot$CONF.root.$O $LIBRARY $CONF.c
	$CC $CFLAGS '-DKERNDATE='`{date -n} $CONF.c
	$LD -o $target -l -H1 -T0xC0000000 -D0xC0604000 -E0x0 roml.$O $CONF.$O boot$CONF.root.$O $LIBRARY -lc
	size 9$CONF
```

(`hobbit/mkfile:60-63`.)  `$LIBRARY` is `lib$TYPE.a` and `$CFLAGS` is
`-w -D$TYPE` (`mkfile:3,7,8`), and `$OBJ` names `${TYPE}main.$O`
(`mkfile:26`).  The ROM needs `rommain.c` (`mkfile:79` gives it its own
dependency on `rom.h`) and `-Drom`, which selects the ROM's memory map
in `hobbit/mem.h:47-55` (KZERO = VROMBASE = 0xC0000000, KDATABASE =
0xC0600000) and two extra physical segments in `hobbit/segment.h:16-19`
(`physm` at 0x80000000 and `io` at 0xB0000000).  So the ROM is built
with **`mk CONF=rom TYPE=rom 9rom`**.  That invocation is an assumption:
the mkfile defaults to `TYPE=ram` and nothing in the release records
the command line.  `roml.s` itself begins `#define rom` with an
unprintable comment about the build system (`roml.s:1`), which fits.

Every object of the kernel is therefore compiled again with `-Drom`;
the ROM shares no object with `9term`/`9cpu`.

`-T0xC0000000` puts the text at VROMBASE, where `roml.s:45-46` maps the
ROM (`NPSTE(PROMBASE, 64, STE_V)`: 64 pages, 256 KB, at physical 0).
`-D0xC0604000` puts the data at KDATABASE+0x4000, in the segment
`roml.s:48-49` maps to RAMBASE (0xC0400000 -> 0x80000000, so
KDATABASE = physical 0x80200000, "data copied to 2Mb").  `-E0x0`: the
entry is physical 0, the reset vector.

### mkrom: the EPROM image

`hobbit/mkrom.c` is a host program (`mkfile:106` cleans `[$OS].mkrom`
and `9rom.com`): `mkrom 9rom` writes `9rom.com`.  It calls libmach's
`crackhdr`, then `segment(txtoff, txtsz)` and `segment(datoff, datsz)`
(`mkrom.c:91-92`), each of which copies the file four bytes at a time,
`b0 b1 b2 b3` out as **`b2 b3 b0 b1`** (`mkrom.c:34-37`): the two
16-bit halves of every word exchanged.  Its `case FHOBBIT` (txtoff =
32, txtsz -= 32, `mkrom.c:81-89`) is for `z.out` executables; a `-H1`
file is a different type: libmach's `executable.c` lists magic
`0x161<<16` as "hobbit plan 9 boot image", `FHOBBITB`, cracked by
`hobbitboot`, which sets txtoff = `sizeof(struct mipsexec)+4` = 80
(`sys/src/libmach/executable.c:72-78, 248-255`, vendored 2026-11-24).
So `9rom.com` is the text from file offset 80, then the data, both
half-swapped, with no header.  Two small defects in `mkrom.c`: a
trailing group of fewer than four bytes is dropped (with a warning,
`mkrom.c:39-40`), and the padding loop appends `(txtsz+datsz)%4` zero
bytes (`mkrom.c:93`), the remainder, not the bytes up to a multiple
of four.

The swap is about the EPROM programmer, not the CPU: the code needs the
ROM to read, through the CPU, exactly the words `zl` wrote (text parcels
big-endian in each word, PRM p. 1-4 note; data little-endian under
CONFIG.KL), because `roml.s:67-75` copies the data out of the ROM with
plain halfword loads and stores.  How the board's EPROMs sat on the bus
(two 16-bit parts, or four bytes) is not in the release.

`tools/p9kbuild.py` `mkrom()` is a transcription (libmach is a library
for the host it ran on; the release ships `mkrom.c`'s source only).

### Built on the model (2026-11-24)

```sh
python3 hobbit/tools/p9kgen.py --out K --conf rom                 # TYPE=rom
python3 hobbit/tools/p9kbuild.py kernel --conf rom --kgen K --build B
python3 hobbit/tools/p9kbuild.py link   --conf rom --kgen K --build B [--check]
```

Every program is the release's own Hobbit binary run on
`sem/hobbit_sem.py` by `tools/p9run.py` (`docs/plan9_port.md`).
`--conf rom` implies `--type rom` (`-w -Drom`, `rommain`, `roml.s`,
`librom.a`).  One run, on a heavily loaded machine:

| stage | programs | instructions | wall |
|---|---:|---:|---:|
| p9kgen (rom.c, devtab.h, init.h, objlists, bootrom.c, libboot, `zl -o bootrom.out ... -lauth`, mkroot) | 75 | 1,441,786,197 | 11,341 s (mkroot's `sed`: 1.2 G instructions, 9,408 s) |
| kernel: 59 objects with `-Drom`, `ar vu`, `rl` | 61 | 433 M + 37 M | 742 s + 387 s |
| link: `za roml.s`, `zc rom.c`, `zc bootrom.root.c`, **`zl -o 9rom -l -H1 -T0xC0000000 -D0xC0604000 -E0x0 roml.z rom.z bootrom.root.z librom.a -lc`**, `size 9rom` | 5 | 270 M (zl 163,617,627) | 1,547 s |

Two things the release's tree needed: `hobbit/lib/libmach.a` (the boot
program `romboot.c` includes `<mach.h>`, whose `#pragma lib
"libmach.a"` makes zl link it for `crackhdr`), vendored from the same
archive with `sys/src/libmach/executable.c` (`tools/README.md`); and
nothing else -- every object compiled, and zl printed nothing.

Products (`tools/p9kbuild/`, committed; `p9kbuild.NINEROM_SHA256`):

* **`9rom`**: 485,646 bytes, sha256 `b83c5f86d7fedac4...44ae85`;
  `size 9rom` prints `183972t + 64600d + 62164b = 310736` (the header's
  text 184,048 less 76, as for 9term); text 0xC0000000..0xC002CEF0, data
  0xC0604000..0xC0613C58, bss to 0xC0622F2C; entry 0; 7,467 symbols;
  `p9exec.check_kernel` passes with the link's -D and -E.  `librom.a`
  1,049,612 bytes, sha256 `4a19874b...`.
* **text + data = 248,648 bytes**, which fits the ROM's 256 KB segment
  (262,144) with 13,496 bytes to spare.
* **`9rom.com`**: 248,648 bytes, sha256 `b6bedfa054ff18b2...73f78c7`;
  (184,048+64,600) % 4 = 0, so no padding.

The image was made once; it was not rebuilt a second time to show the
build is reproducible (the 9term build was, `docs/plan9_boot_plan.md`
A3).  KERNDATE is s9term's (p9kgen's choice).

## 2. From reset to `main` (`hobbit/roml.s`)

At reset the Hobbit is in physical mode with PSW = 0 and CONFIG = 0
(PRM p. 1-35) and fetches from physical 0, the first word of the EPROM.

| lines | what |
|---|---|
| 12-13 | `_startup`: `JMP *$(PROMBASE+6)`.  The image's first parcels are `80f3 0000 0006`: a three-parcel jump to physical 6, the instruction after it; on the model the PC goes 0 -> 6 (`tests/test_p9rom.py` `test_reset_vector`).  Why the ROM jumps to its own fall-through is not said; it does make the PC an explicit absolute address before anything else |
| 15-17 | `FLUSHP; FLUSHI`; CONFIG = PM\|PE\|IE\|SE\|PX\|KL (little-endian kernel, `hobbit/machine.h`); PSW = 0 |
| 19-27 | save the reset-time MSP, ISP, SP, SHAD, VB, STB, FAULT and the JTAG ID into PPage0 (0x80000040..0x64): what the monitor's `r` prints after a crash |
| 29 | PPage0+0x74 = `$fprt0(SB)`, the floating-point interpreter's entry (VROMBASE-relative) |
| 31-32 | ISP = physical MACHADDR+ISPOFFSET; `ENTER` |
| 34-43 | STB = physical KSTBADDR (0x80201000); clear the segment table and the page before it (two pages, from ISP down, 16 bytes per `DQM`) |
| 45-55 | four segment-table entries: VROMBASE -> ROM (64 pages, valid, kernel read-only); 0xC0400000 -> RAMBASE (1024 pages = 4 MB, cached, writable); IOBASE and IOBASE+0x08000000 (the I/O "ACK" and "NACK" spaces, 4 pages each, uncached) |
| 57-62 | build a CRET frame: PC = `_virtual`, PSW = VP\|UL\|S; `FLUSH; CRET` -- the MMU is on from the next instruction |
| 64-75 | `_virtual`: ISP = virtual; copy `etext`..: the data image in the ROM to KDATABASE+0x4000 (`bdata`) up to `edata`, a halfword at a time |
| 77-107 | VB = VBADDR (KDATABASE): the fourteen vectors (`_vector0` syscall .. `_vectorD` FP exception); the niladic and unimplemented-instruction vectors are `fprt0` |
| 109-120 | `m` = `mach0` = MACHADDR; clear the BSS; `CALL main` |

`gotopc` (`roml.s:173-186`), `softreset` (`:338-352`) and the exception
entry (`:214-320`) are described below.

## 3. The kernel in the ROM (`hobbit/rommain.c`)

`main` (`rommain.c:20-52`): `machinit`, `confinit` (which sizes
memory), `xinit`, `printinit`; clear IOCTL and both interrupt masks,
wait 10 ms, then IOCTL = IOENABLE|SCSIENABLE (`:34-38`; the RAM kernel
sets only IOENABLE, `rammain.c:104`); Quart channel 0 as the console at
19200 baud (`eiasetup(0, EIAADDR)`, `eiaspecial(0, &printq, &kbdq,
19200)`, `:40-41`); then the ordinary kernel start: `mmuinit`,
`pageinit`, `procinit0`, `initseg`, `clockinit`, `chandevreset`,
`streaminit`, `swapinit`, `userinit`, `schedinit`.

**Memory sizing** (`meminit`, `:65-91`).  Starting 1 MB above
`&PPage0.memsize` (0x80000080), for each 1 MB step `va` it maps the
4 MB segment holding `va` one-to-one (physical = virtual, 0x80xxxxxx)
up to and including `va`'s page, reads the word at `va`, writes a new
pattern (0x12345678, then +0x3141526 per step) to `PPage0.memsize`,
and stops when the word at `va` has changed -- i.e. when `va` aliases
`memsize`.  `memsize` is then `va - &memsize`: a whole number of MB.
There is no bus-error path: the board must alias RAM above its size
(partial decoding).  `confinit` (`:93-119`) then gives the ROM kernel
only the first 4 MB as page pool (`npage0`) and fixed small tables
(20 processes, 200 user pages).

**Devices** (`hobbit/rom`): `root cons env pipe proc srv mnt dup iic eia
rtc incon dk scsi wren ether arp iproute ip boot`, streams `urp ip
async fcall`; boot methods `il tcp incon 9600 19200`; `cpuserver = 1`;
no screen (`screenputs` is a stub, `rom:55-59`).  So the ROM touches:
the Quart (console, and eia1 for the serial Datakit methods), the
interrupt controller and IOCTL, the timekeeper RAM (NVRAM + clock), the
IIC bus and its EEPROM (the Ethernet address), the incon (Datakit)
interface, the WD33C93A SCSI controller, and the SONIC Ethernet.
`devboot.c` (`#B`) adds `boot` (write a PC: `gotopc`) and `mem`.

## 4. The monitor (`boot/romboot.c`)

`romboot` (`:700-784`) opens `#c/cons` three times, prints
`Hobbit ROM <ctime of #c/time>` (on the model `Sat Nov  7 04:28:37 GMT
1992`: `#c/time` is the kernel's boot time, which is KERNDATE, and our
build takes KERNDATE from s9term (721110517) -- so the date is our
build's stamp, not that of any real ROM), detaches the default text segment at
0x80000000 and attaches the physical segment `physm` there for 4 MB
(`:719-724`): from then on the boot process addresses physical RAM
directly, and PPage0 (`rom.h`) is a structure at user address
0x80000000.  `envinit` (`:84-103`) reads the `Env` from `#r/nvram`
(the MK48T02 timekeeper's RAM at IONAK+0x2000, offset 0, `rom.h:15-19`,
`devrtc.c:282-290`) into PPage0+0x300 and adds any missing permanent
entry (`:32-39`):

| name | default |
|---|---|
| sysname | hobbit |
| station | 99 |
| bootfile | /hobbit/9cpu |
| bootmode | d |
| fs | incon!nj/astro/Nfs |

(eleven entries of a 15-character name and 47-character value; the
`sum` field is never computed or checked.)  It then sets `#c/user` to
`none` -- after `envinit`, because only the host owner may open the
NVRAM (`:726-735`).  If `bootmode` begins with `a` it prints
`autoboot: hit any key (except ^P) within 5 seconds to abort` and, if
no key comes in 5 s, runs `b` (`:742-754`).  Then the loop: print
`>>>`, read a line, split it into at most 7 fields, run the command;
an empty line shows the next location; anything else prints `eh?`.

| command | function | what |
|---|---|---|
| `e` | `envcmd` :125 | list the environment; `e name` show one; `e name value` set; `e -d name` delete (not a permanent one); `e -i` clear and reload the defaults; every change is written back to `#r/nvram` |
| `g [-b\|-h\|-w] [addr [count]]` | `getcmd` :281 | display memory (address `#hex` or C number); width from the address's alignment or the flag; faults are caught (`probe`) and print `?` |
| `-` | `minuscmd` :336 | step back one and display |
| `p [-b\|-h\|-w] [addr [value [count]]]` | `putcmd` :345 | store |
| `b [-s fs] [file] [args...]` | `bootcmd` :486 | boot (below) |
| `r` | `registers` :557 | the registers saved at the last reset/softreset (PPage0+0x40..0x6C) |
| `w addr` | `walkcmd` :592 | walk the MMU tables (from the saved STB) for a virtual address |
| `x prog [args]` | `execcmd` :638 | attach the file server (`fs`) and exec a program from it |

### `b`: finding, loading and entering a kernel

`bootcmd` (`:486-555`):

1. `fs` = `-s` argument or env `fs`; the file = first argument not
   starting with `-`, else env `bootfile`.
2. Unless the file name starts with `#` (a device file of the ROM
   kernel, e.g. a raw `#w` SCSI partition), `attach(fs)`
   (`:458-484`): find the method whose name prefixes `fs` (`il`, `tcp`,
   `incon`, `9600`, `19200`; the text after `!` is the address), run
   its config (IL/TCP: `boot/ip.c` `ipconfig`, BOOTP over the SONIC;
   `incon`: the Datakit interface; `9600`/`19200`: Datakit over
   `#t/eia1`, `boot/async.c`) and connect, `nop` and `session`, then
   mount it after `/`.
3. `open` the file; `crackhdr` (libmach); print the file name, then
   `\n<text>+<data>+<bss>`.
4. `readseg` (`:438-456`) reads text and data with 8 KB reads straight
   to their link addresses -- which, through `physm`, are the physical
   addresses: a RAM kernel is linked at 0x80004000 (`mkfile:52`).  BSS
   is not cleared here (the kernel's own start clears it).
5. PPage0.argc = remaining arguments + 1 and `argv[1..]` = those
   arguments (pointers into PPage0.argbuf, which are physical addresses
   valid for the loaded kernel); `argv[0]` is left as it was.
6. Clear PPage0's 16 vectors "so it has a chance to get back to the
   ROM" (`:541-546`).
7. Open `#B/boot`, print ` entry: 0x<entry>`, sleep 500 ms, write the
   4-byte entry: `bootwrite` (`devboot.c:114-117`) does `splhi();
   gotopc(pc)`.

`gotopc` (`roml.s:173-186`): PSW = VP|UL, ISP -> SHAD, build a KRET
frame with PC = the entry and **PSW = 0**, VB = 0, CONFIG =
PM|PE|IE|SE|PX|KL, `FLUSH; KRET`.  The kernel starts in physical mode,
interrupts masked, little-endian, with VB = 0.

### The hand-off (`hobbit/rom.h`, PPage0 at physical 0x80000000)

| offset | field | written by | read by the RAM kernel |
|---|---|---|---|
| 0x000 | vectors[16] | cleared by `b` | -- |
| 0x040-0x064 | msp isp sp shad vb stb fault id at reset | `roml.s:19-27` | -- (`r`) |
| 0x04C, 0x050, 0x068, 0x06C | config, psw, r0, r16 at softreset | `raml.s:304-307` (a RAM kernel's softreset) | -- (`r`) |
| 0x074 | fpi entry (`fprt0` in the ROM) | `roml.s:29` | `raml.s:85-86` copies it into the niladic and unimplemented vectors |
| 0x080 | memsize | `rommain.c:90` | `rammain.c:142-168` (meminit, confinit) |
| 0x100 | argc, argv[8] (0x104), argbuf[220] (0x124) | `romboot.c:536-539, 760` | `rammain.c:82-83` (arginit) |
| 0x200 | Env (nentry, sum[4], 11 x {name[16], value[48]}) | `romboot.c:93` | `rammain.c:47-73`: sysname, station, fs |

**The offsets in `rom.h`'s comments are wrong.**  The header says fpi
is at 0x84, argc at 0x200 and Env at 0x300; the struct as declared puts
`fpi` at 0x84 (unused: every reader and writer uses 0x74, a `spare`
word), but argc at **0x100** and Env at **0x200**, because
`spare0x0088[30]` ends at 0x100, not 0x200.  The compiler follows the
struct: on the model, after `romboot` has run, PPage0+0x100 holds argc,
+0x104 a pointer to +0x124 (the command typed), and +0x200 `nentry` = 5
with `sysname` at +0x208 (a memory dump at `>>>`, 2026-11-24).  Two
consequences: the ROM's own `softreset` (`roml.s:340-342`) saves PSW,
CONFIG and R0 at RAMBASE+0x124/0x128/0x12C -- inside `argbuf`, where the
next command line overwrites them, and not where `registers` reads them
(so after a ROM-kernel crash `r` shows CONFIG, PSW and r0 as 0; seen on
the model, section 5); and `tools/p9boot.py`'s `PPAGE0_ARGC` (0x200) and
`PPAGE0_ENV` (0x300), taken from the comments, are the wrong words
(harmless there: it writes zeros into zeroed RAM; left as an open item
for that file).

The loaded kernel keeps the ROM mapped: `raml.s:36` maps VROMBASE onto
PROMBASE for 128 pages, user-executable, so user processes' floating
point runs `fprt0` in the ROM.  Its `softreset` (`raml.s:302-313`, the
second panic, `trap.c:75-77`) saves CONFIG, PSW, R0, R16 into PPage0 and
KRETs to PROMBASE with CONFIG = 0: a warm restart of the ROM, whose
`r` then shows the crash.

### What the manual says, and where it disagrees

booting(8) of the same release (`sys/man/8/booting`, section "Hobbit",
in the archive, not vendored; also at
typewritten.org/Manual/Bell/Plan9/1ed/man8/booting.html, dated
"January 03, 1993") documents the `>>>` prompt, `e` and `e -i`, and
boots with `b -- incon!nj/astro/Nfs` (default kernel) or `b
/sys/src/9hobbit/9cpu -- incon!nj/astro/Nfs`, saying the second form
"will also initialize the bootfile variable" and that "Hobbit boards
boot only using incon".  Against `romboot.c`:

* `b` never writes `bootfile` (no `envput` in `bootcmd`).
* `ARGBEGIN` consumes `--` (`sys/include/libc.h:350-358`), so in `b --
  incon!nj/astro/Nfs` the first remaining argument, `incon!...`, is
  taken as the file name (`romboot.c:504-506`), and in the second form
  `incon!...` becomes `argv[1]` for the loaded kernel.  The second
  reading fits the RAM kernel, whose `arginit` passes its arguments on
  to its own `/boot` (`rammain.c:60-87`); the first does not boot the
  default kernel.  Either the manual describes another revision of the
  monitor or the source has changed since.  On the model (section 5),
`b -- #c/time` prints `#c/time...` and fails in `crackhdr`: the word
after `--` is the file.

## 5. On the reference model

`tools/p9rom.py` runs the committed `tools/p9kbuild/9rom` on the
reference model with `tools/p9boot.py`'s device models (Quart, Irq,
IOCTL, timekeeper/NVRAM, IIC/EEPROM, WD33C93A, SONIC, incon latch, the
LCD), the EPROM at physical 0 and RAM at 0x80000000 that aliases every
MEMSIZE (default 8 MB) except over device ranges.  Its choices are in
`p9rom.ROM_CHOICES`.  It starts at **PC 0 in the reset state** (PSW 0,
CONFIG 0, VB 0, PRM p. 1-35): nothing of the ROM is skipped or faked.
The console is Quart channel 0; `--type 'WAIT=REPLY'` types on it.

```sh
python3 hobbit/tools/p9rom.py --until '>>>' --milestones        # ~8 s
python3 hobbit/tools/p9rom.py --type '>>>=e\r' --until '>>>'
```

### Reset to `>>>`: 681,566 instructions, 0.036 s of model time

| step | milestone |
|---:|---|
| 0 | `_startup` at physical 0; step 1 is the JMP to 6 |
| 2,070 | `_virtual`: the MMU is on (VROMBASE), `_copy` starts |
| ~196,000 | `_copy` done (the data segment, halfword by halfword) |
| 273,717 | `meminit`: the alias is found at 0x80800080, memsize = 8 MB |
| 275,355 | `eiasetup`, `eiaspecial` (Quart channel 0, 19200) |
| 283,897 | first `print`: `200 free pages, 800K bytes, swap 800K, ...` |
| 292,606 | `chandevreset`: iic (EEPROM), eia, rtc, incon, dk, scsi (`resetscsi`, `ctlrreset`), wren, ether (`etherreset`, SONIC reset, RRA, CAM) |
| ~453,000 | `touser`: the first user process (initcode -> `/boot`) |
| 681,566 | `Hobbit ROM Sat Nov  7 04:28:37 GMT 1992` and `>>>` |

The uart0 bytes, pinned by `tests/test_p9rom.py`:

```
200 free pages, 800K bytes, swap 800K, highwater 40K, headroom 48K
Hobbit ROM Sat Nov  7 04:28:37 GMT 1992
>>>
```

Checked on the way (`tests/test_p9rom.py`): RAM at the data addresses
equals the image's data segment when `main` is entered (less `m` and
`mach0`, which `roml.s:109-110` sets); PPage0+0x74 = `fprt0`; memsize
4, 8 and 16 MB for those RAM sizes; and with RAM that does not alias,
`meminit` takes a bus error at 0x80800080 -- the ROM really needs
partial decoding.  `_copy` reads one halfword past the data image
(`CMPHI R4, $edata` is tested before the copy, so the copy at R4 =
edata happens too): one ROM read at physical 0x3CB48 = text+data,
harmless (it lands in the BSS, which is then cleared).  The events on
the way are the user processes' demand-paging faults, the first being
`touser`'s CRET onto the not-yet-present user stack page (0xBFFFFFF0).

### The monitor's commands (observed)

```
>>>e
sysname=hobbit
station=99
bootfile=/hobbit/9cpu
bootmode=d
fs=incon!nj/astro/Nfs
>>>r
     MSP 00000000     ISP 00000000      SP 00000000
  CONFIG 00000000     PSW 00000000    SHAD 00000000
      VB 00000000     STB 00000000   FAULT 00000000
      ID 1000003b      r0 00000000     r16 00000000
>>>g #80000080
#80000080	#00800000
>>>zork
eh?
```

From a zeroed NVRAM `envinit` writes the five defaults (the NVRAM then
holds `nentry` = 5 and the entries, pinned by the test).  `r` after a
cold reset shows the reset values and the JTAG ID the model reports.

**`w` crashes the monitor after a cold reset.**  `walkcmd` reads the
table at `ppage0->stb` (`romboot.c:605`), the STB saved at reset -- 0
after power-on -- so it dereferences user address 0xC00 without the
`probe` guard `g` uses:

```
>>>w #c0000000
boot 1: suicide: sys: trap: read fault addr=0xc00 pc=0x499c
panic: boot process died: sys: trap: read fault addr=0xc00 pc=0x499c
200 free pages, 800K bytes, swap 800K, highwater 40K, headroom 48K
Hobbit ROM Sat Nov  7 04:28:37 GMT 1992
>>>r
     MSP ffffed40     ISP ffffefc0      SP ffffed30
  CONFIG 00000000     PSW 00000000    SHAD ffffefc0
      VB c0600000     STB 80227800   FAULT 00000c00
      ID 1000003b      r0 00000000     r16 00000000
```

The panic is the warm restart working as designed: `trap.c` `reboot`
-> `softreset` -> KRET to physical 0 with CONFIG 0, the ROM runs again
from `_startup`, and its reset path saves the dying kernel's MSP, ISP,
SP, SHAD, VB, STB and FAULT (0xC00, the bad address), which `r` shows.
CONFIG, PSW and r0 read 0 because `roml.s`'s `softreset` stored them in
`argbuf` (section 4).  After such a restart STB is valid and `w` works.

**A failed `b` restarts the ROM too**: `b -- #c/time` prints
`#c/time...boot: not a header I understand: bad arg in system call`,
`fatal` exits `/boot`, the kernel panics ("boot process died") and
softresets back to `>>>`.

### `b` with the default `fs` (incon): stops at the Datakit interface

`e bootmode a` then `b` with `fs=incon!nj/astro/Nfs`: `attach` runs the
incon method and the run stops at `inconpoll` reading the incon's csr
(IOACK+0x4), which the harness does not model (`p9boot` models the
incon as a write-only latch; there is no Datakit here).  This is the
only boot method booting(8) says Hobbit boards used.

### `b -s il /hobbit/s9term`: over the network from the 1e file server

`--join OUT` boots the 1e 386 file server in QEMU (`tools/p9join.py`'s
`start_server`, `docs/qemu_1e_server.md`; lockstep clock) with the
SONIC on its wire (UDP ports 10931/10932), and `--kernel` names the
image the ROM should load so the hand-off can be checked against it:

```sh
sh hobbit/tools/qemu1e/build.sh                       # once, ~15 min
python3 hobbit/tools/p9rom.py --join hobbit/build/rom/join1 \
    --kernel hobbit/tools/plan9-1e/hobbit/s9term \
    --type '>>>=b -s il /hobbit/s9term\r' --until 'root is from' \
    --max-steps 400000000 --progress 10000000
```

Without a network the same `b` stops at the first frame: `sonic ether:
52 54 00 00 0b 0b` is printed and the SONIC transmits a BOOTP request.

**Observed 2026-11-24: the ROM loaded s9term from the file server and
started it.**  uart0, byte for byte (CR LF as LF):

```
200 free pages, 800K bytes, swap 800K, highwater 40K, headroom 48K
Hobbit ROM Sat Nov  7 04:28:37 GMT 1992
>>>b -s il /hobbit/s9term
sonic ether: 52 54 00 00 0b 0b
arp: rcvd for 10.9.0.1
nop...session.../hobbit/s9term...
219968+70388+98476 entry: 0x80004000
1364 free pages, 5456K bytes, swap 27856K, highwater 272K, headroom 340K
```

The last line is **s9term's own first console line**, the same bytes
`tools/p9boot.py` gets when it loads s9term itself (`docs/p9boot.md`,
"The first console line"): s9term sized its memory from the ROM's
PPage0.memsize (8 MB -> 1364 pages).  On the wire (281 frames,
`build/rom/join1/hobbit.pcap`, not committed): BOOTP request and reply
(10.9.0.2, the server's file field `/hobbit/s9term`, which `romboot`
does not use), ARP, the IL connection to 17008 (the server's console
logs the BOOTP reply and "il call for il17008"), then the 9P exchange,
with the file's data frames between model time 1.45 s and 6.40 s.

The hand-off, captured at the first kernel-mode instruction in RAM
(step 139,546,042): **PC 0x80004000** (s9term's entry), **PSW 0**,
**VB 0**, **CONFIG 0x3F0000** (PM|PE|IE|SE|PX|KL, `gotopc`); RAM at
s9term's text and data addresses equal to the file's 219,968 and 70,388
bytes, word for word; PPage0 memsize 0x800000, fpi 0xC00227C0
(`fprt0` in the ROM), argc 1 with argv[0] = `b` (the command word left
in argbuf: `bootcmd` sets argv[1..] only, "we don't really care what
the 0'th argument is", `9/boot/romboot.c:530-538`), and the
NVRAM's Env at 0x200.

The run ended at its 400,000,000-instruction limit (20.0 s of model
time, several hours of host time with QEMU in lockstep) with s9term
idling in `runproc`, before its `root is from` prompt.  That is a
matter of time, not a fault: the hand-off came at 6.997 s of model time
(`build/rom/join1.out`), and at the Quart counter's hardware rate s9term
reaches that prompt 14.367 s after its own start (`docs/p9boot.md`,
"How far it gets"), so about 21.4 s here; this harness has no idle skip
to get there sooner.  The prompt would show on uart0 as well as the
screen (`docs/p9boot.md`, "The console"), so `--until 'root is from'`
can match given a higher `--max-steps`.  Not run further.  What s9term
gets from the ROM differs from `tools/p9boot.py`'s PPage0: argv[0] is
`b`, fpi points into the ROM (`fprt0`) rather than at a stand-in, and
the Env is the NVRAM's.  This path is a live run (QEMU, wall clock); it
is not in the regression suite.

## 6. What the ULX3S port needs from this

The ULX3S here is the 85F (`fpga/README.md`: LFE5U-85F, 25 MHz clock,
FTDI UART on `ftdi_rxd`/`ftdi_txd`, 208 DP16KD block RAMs of 18 Kbit =
468 KB; `fpga/ulx3s_85f.lpf:7` notes the board's SDRAM and SD card,
unused so far).  What the real ROM requires, from sections 2-4 and the
access counts of a model run to `>>>` (every bus access counted per
device, 2026-11-24):

**Memory map** (physical):

| range | what | needed by |
|---|---|---|
| 0x00000000.. 256 KB | ROM: text + data image, 248,648 bytes (`roml.s:46`) | reset vector, all ROM-kernel text (1,343,997 word reads to `>>>`) |
| 0x80000000.. | RAM, >= 4 MB, **aliasing above its size** | PPage0 (0x80000000), the ROM kernel's data/bss/stacks at +2 MB (KDATABASE, to 0x80222F2C), `confinit`'s 4 MB page pool, loaded kernels at 0x80004000 |
| 0xB0000000 (ACK) / 0xB8000000 (NACK) | I/O spaces, each 4 pages mapped (`roml.s:51-55`) | the devices below |
| 0xA4400000 | SONIC registers (`io.h:208`, mapped by `mmuiomap`) | etherreset |

**Devices the ROM touches before `>>>`**, in order of first access
(model run): IOCTL (IONAK+0, `main`: 4 writes), the interrupt controller
(IONAK+0x80: masks), **the Quart** (IOACK+0x100: console channel 0,
the clock's counter/timer; 336 accesses), **the IIC controller and its
EEPROM** (IOACK+0x80: `iicreset` reads the Ethernet address), the incon
(IOACK+0: 2 writes in `inconreset`), **the WD33C93A** (IONAK+0x100:
`resetscsi` issues a reset and waits for its interrupt status), **the
SONIC** (`etherreset`: `while(sonic->cr & Rrra)` and `& Lcam` spin
forever if the commands do not complete -- injection 4 of
`tests/test_p9rom.py` shows exactly this hang), and **the timekeeper**
(IONAK+0x2000: NVRAM for the environment, 712 reads and 3,560 writes;
IONAK+0x3FE0 the clock).  With no Quart there is no console and no
clock tick; with no SONIC the ROM never reaches `/boot`; the SCSI and
IIC parts must at least answer the sequences deviic.c and scsi.c wait
on.  To boot anything, `b` then needs one of: the SONIC with a network
(IL/TCP, BOOTP), the incon/Datakit, or a Datakit line on Quart channel
1 -- or a kernel already on a `#w` SCSI partition.

**So the original ROM is not the right first program for the board.**
It is a 250 KB multi-device CPU-server kernel; running it on the ULX3S
means implementing (or stubbing faithfully) the Quart, the interrupt
controller, the timekeeper, the IIC/EEPROM, the WD33C93A and the SONIC
(plus a network to use it), and putting >= 4 MB of aliasing RAM in the
SDRAM.  It is the right *later* target: once those devices exist it is
a strong, period-correct test of all of them, and the hand-off it
defines (PPage0) is what every 1e RAM kernel expects.

**A minimal replacement ROM is better for first bring-up**, and the
ROM's own interface says exactly what it must do.  A loader of a few
hundred bytes in BRAM at physical 0:

1. reset path as `roml.s:12-17`: CONFIG = PM|PE|IE|SE|PX|KL, PSW = 0;
   stay physical (no STB needed: a RAM kernel's `raml.s` builds its own
   tables);
2. receive a `-H1` image over the FTDI UART (or read it from the SPI
   flash), and put text and data at their link addresses in SDRAM
   (0x80004000 for 9term/9cpu); BSS need not be cleared (`raml.s` does);
3. fill PPage0 with what the RAM kernel reads (`rammain.c`, at the
   struct's real offsets): memsize at 0x80 (a multiple of 1 MB),
   fpi at 0x74 (`raml.s:85-86` copies it into two vectors: point it
   at an `fprt0` in the ROM -- `tools/p9kbuild/fpi.rom`, 6,328 bytes of
   text, `docs/p9boot.md` -- or at a trap), argc = 0 at 0x100 (or
   arguments in argbuf), and an Env at 0x200 (nentry = 0, or sysname /
   station / fs);
4. jump as `gotopc` does (`roml.s:173-186`): PSW = 0, VB = 0, the
   entry.

The RAM kernel then needs a console: s9term talks to Quart channel 0 at
19200 baud, so the FPGA needs a Quart-compatible UART (the 68C94's
register map, `io.h:32-96`, as much of it as deveia.c uses) mapped to
the FTDI pins; the rest of the board (clock interrupt, LCD, SONIC...) as
`docs/p9boot.md` lists for s9term.  Keep the ROM at physical 0 and
mapped at VROMBASE: a RAM kernel maps 128 pages of PROMBASE
user-executable (`raml.s:36`) and every user floating-point instruction
traps into the ROM's interpreter.

## 7. Sources found outside the release

* booting(8), 1st Edition, "Hobbit" (above): the only description of
  the ROM from the time found.  boot(8) of the same release explains
  the `method!address` form (`incon!nj/astro/Nfs`: Datakit through the
  incon interface, default address `Nfs`).
* Nothing was found on 9fans or comp.os.plan9 about the Hobbit ROM or
  who wrote the port (searches 2026-11-24 for the port, McKie/Pike,
  "The Various Ports" -- only later editions of that paper turned up,
  without a Hobbit section).  Tech Monitor, 4 March 1994, lists "the
  Hobbit RISC" among Plan 9's five architectures, with no detail.

## 8. Tests

`tests/test_p9rom.py` (in `tests/run_tests.sh`, ~30 s): the 9rom link
line is the mkfile's; mkrom's order and padding on a made-up image; the
committed image's sha256, `9rom.com` = mkrom(9rom), text+data within the
ROM STE; the reset vector's first two instructions; uart0 to `>>>`
byte for byte at instruction 681,566; the data segment in RAM at `main`;
memsize and the fpi word; `e`'s output and the Env in NVRAM; memsize for
4 and 16 MB; the bus error without aliasing.  Four injections (ROM
words big-endian; mkrom without the swap; no aliasing; aliasing over the
SONIC's range) and the failures observed are in the test's header.
Not covered: the hand-off capture and the loaded-image comparison
(`record_handoff`, `compare_loaded` in `tools/p9rom.py`) run only on the
live join path; their result above was observed once, and no test shows
the comparison failing on a corrupted image.

## 9. Open questions

* Which `mk` invocation built the real ROM (`TYPE=rom` is inferred) and
  what KERNDATE it had; the release ships no image, so nothing here can
  be compared with a real EPROM.
* booting(8) vs `romboot.c` on `--` and on `b` setting `bootfile`:
  another revision of the monitor, or a manual written ahead of (or
  behind) the code?
* Why `_startup` begins with a jump to its own next instruction.
* How the board's EPROMs were wired (what mkrom's half swap
  corresponds to), how RAM above the fitted size decoded (the ROM
  assumes it aliases), and the incon/Datakit interface, which no model
  here implements.
* The 9rom build was run once; a second build to show it reproducible
  (as was done for 9term) has not been run.
* Found here, not fixed here: `tools/p9boot.py`'s `PPAGE0_ARGC` and
  `PPAGE0_ENV` follow `rom.h`'s wrong comments (section 4); `roml.s`'s
  softreset saves PSW/CONFIG/R0 inside `argbuf` (section 4), which
  clobbers the arguments if a crash comes back to the ROM; and `_copy`
  reads one halfword past the data image (section 5), harmless only if
  the EPROM decodes past its end.  Whether the real boards relied on
  that last read returning anything in particular is unknown.
