# The Hobbit BeBox: surviving software, and booting it

Be Inc.'s first machine, before the PowerPC BeBox of 1995, was a
two-processor AT&T Hobbit board with three AT&T DSP3210s. A few were
hand-built in 1993-94 and lent to developers; the serial numbers on the
surviving disks are 9308000009, 9308000044 and 9308000058. This file
records what software survives, where it came from, and what the kernels
themselves say about the board (with addresses read from the code). The
board research from other sources (newsletters, interviews, photos) is
`bebox_hardware.md`; the 92010/92020 differences are the ISA work's.

## What survives

The binaries and documents are held on disk, not in git:
[`bebox/MANIFEST.md`](bebox/MANIFEST.md) lists them with sizes and
SHA-256s, and `bebox/fetch.sh` fetches them into `build/bebox/`.

- **Source.** fsck.technology's software archive, directory "BeOS Hobbit
  Prototype Release" (files dated 2019-11-08). Found through a Haiku
  forum post pointing there for Hobbit disk images and to typewritten.org
  for restoration notes
  (<https://discuss.haiku-os.org/t/beos-powerpc-a-sad-tale-of-apple-hardware/10677?page=6>).
  The archive states no licence; the software is Be's, the documents are
  marked "CONFIDENTIAL : Be Labs, Inc.". Hence manifest only.
- **Three SCSI disk images** (Be's 1993-94 file system, version 1.0, read
  by `tools/befs1.py`): `be3` from serial 9308000044 with a kernel built
  Mar 1 1994; `be` from 9308000058 and `pixels` from 9308000009, both
  with the kernel built Nov 23 1994 (byte-identical). Two `tar` dumps of
  the `be3` and `pixels` file trees. The `pixels` image's file name is
  `hobbit-930800009.img`, one digit short of a ten-digit serial; reading
  it as 9308000009 is an inference (a machine with that serial is in
  the photographs, `bebox_hardware.md` §16).
- **Nine floppies:** the installer boot floppy (the Nov 1994 kernel,
  stripped, plus the servers), the 7-disk install set, and the update of
  28 Nov 1994.
- **The hardware manual, in draft:** "Be machine hardware documentation",
  interim printouts dated 15 and 16 September 1993, written for Be Labs
  (attn. Dan Dahle) by Paula Butler and Ctein, with their cover letter:
  Slots, I/O, Joysticks, Floppy, Printer, SCSI, and Appendix A, the memory
  map. The cover letter says the DMA chapter and the developer guidelines
  were not yet drafted, Chapter 1 (Slots) was "internally inconsistent
  and inaccurate", and Appendix A had changed since Be last reviewed it.
- **No boot ROM.** No dump of the board's flash has been published. A
  2009 MAME-forum thread is reported, by a search engine's summary, to
  know of none (<https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=47590>;
  the thread itself was not retrieved, so this is weak evidence);
  archive.org's search API for "hobbit bebox" (2026-11-24) returns only
  BeOS PR2 and the BeOS Bible; typewritten.org's page on 9308000058
  (below) says nothing of a ROM dump;
  OSNews's 2009 story on a Hobbit BeBox sale hoped the buyer would dump
  it (<https://www.osnews.com/story/20869/planets-align-rare-hobbit-bebox-offered-and-sold/>);
  the one emulator that runs these disks says "No boot ROM of these
  machines survives" and does the ROM's job itself (below). `/bin/boot`
  on the 1994 disks is a user program (ELF entry 0x100000f8, user space),
  not a ROM image.

### Other people's work

- **johnrash/bebox** (<https://github.com/johnrash/bebox>, MIT, created
  2026-10-15): a Haiku-native BeBox emulator with a "Hobbit prototype"
  machine that boots these disks to the Browser. Its `design/hardware.md`
  gives a physical memory map and board-register table it attributes to
  the 1993 hardware notes and to the unstripped kernels, and its
  `src/core/hobbit/HobbitVolume.h` documents the file system that
  `tools/befs1.py` reads. It is a secondary source here: every address
  this project models is checked against the kernel code or the 1993
  manual, and cited to them.
- **hobbitbeos** on SourceForge (<https://sourceforge.net/projects/hobbitbeos/>):
  three folders, `ofs-extractor` and `resource-extractor` (2005-09-16)
  and `hobbit-disasm` (v0.01, 3.3 kB, 2006-04-26); no licence stated, no
  description. Not used here.
- **typewritten.org** (<https://typewritten.org/Projects/Be/9308000058.html>,
  dated 24 Feb 2013): restoration notes on "Rev. A" serial 9308000058,
  the machine one of the disks came from: AT keyboard, PS/2 mouse, two
  serial ports, parallel, floppy, a fixed disk, 30-pin parity SIMMs, a
  BeBus graphics card at 800x600; the PowerPC cards once fitted are
  gone. No ROM dump and no disk image are mentioned.

The install set (floppies 1-7, `archive.Z00`-`Z06` joined, then
`uncompress`: 19,353,088 B of tar, 431 entries) holds `/system/kernel`
byte-identical to the Nov 23 1994 kernel on the `be` and `pixels` disks
(SHA-256 `450716b2…`), `/bin/boot` (Nov 22 1994), apps, headers,
libraries and the VCOS DSP tree. It holds no other kernel, no ROM image
and no flash updater.

## What the kernels say about the board

Both kernels are big-endian ELF32, e_machine 0x39d, built with MetaWare
High C and not stripped, so every address below is named.
`tools/beelf.py` reads and disassembles them; `--refs LO HI` lists every
instruction with a constant in a range. The Nov 1994 kernel
(`/system/kernel` of the `be` disk) is the one cited.

**Device addresses.** The I/O window at 0x00800000 holds one 8-bit
register per word, on byte lane 3 for the PC chips (port p at
0x00800000 + 4p + 3); the 53C94 is on lane 2.

| address | what | the kernel's code |
|---|---|---|
| 0x800003 | I/O interrupt register | `_io_int_dispatch` (ANDs with `_enabled_io_interrupts`), `_Wait_Interrupt_Gone` (bit 0) |
| 0x800004 (word) / 0x800007 | CPU 1 I/O mask | `_io_int_enable`/`_io_int_disable` (interlocked word OR/AND), `_main1` |
| 0x80001B | processor reset | `_start_cpu` (bit 1 releases CPU 2), `_NMI_handler` |
| 0x80001F | internal (inter-processor) interrupts | `_set_cpu_int`, `_reset_cpu_int` |
| 0x800183, 0x800193 | keyboard controller, ports 0x60/0x64 | `_get_data`, `_put_data`, `_controller_command`, `_kb_inth`, `_mouse_inth` |
| 0x80088B, 0x80089B | joystick/"pmc", ports 0x222/0x226 | `_joy_inth`, `_write_pmc_byte`, `_send_pmc_cmd` |
| 0x800802 + 4n | 53C94 register n (lane 2) | `_init_53c94` and the SCSI driver, through pointers in data |
| 0x800842 (half word) | 53C94 pseudo-DMA port | `__pseudo_dma_reg`, `_data_xfer_in_dma`/`_out_dma` |
| 0x800BE3-0x800BFB | SER2, ports 0x2F8-0x2FE | `_scc_init` |
| 0x800DC3 | Who Am I | `_get_cpu_id` (value & 15, minus 4), `_db_kcall_handler`, `_joy_read` |
| 0x800DCB, 0x800DD3, 0x800DD7, 0x800DDF | floppy DOR, MSR, data, DIR/DCR (ports 0x372-0x377) | `_MotorOn`, `_ReadData`, `_WriteData`, `_ReadResults`, `_DiskChanged` (`_fdc_dor` etc. in data) |
| 0x800020, 0x800024, 0x80002A, 0x80002E | floppy DMA count − 1, control (1 = memory to disk), address 31:16, address 15:0 | `_NextDma`, `_StopDma`, `_MakeDmaList` (`_dma_count` etc. in data) |
| 0x800DE3-0x800DEB | printer, ports 0x378-0x37A | `_par_init`, `_io_init` |
| 0x800FE3-0x800FFB | SER1 (console), ports 0x3F8-0x3FE | `_scc_init`, `_scc_in`, `_scc_out` |
| 0x8001C3, 0x8001C7 | MC146818 clock, ports 0x70/0x71 | the RTC driver |
| 0x08000048 | memory size, left by the ROM | `_main`, `_hack_for_old_bootroms` |

**Interrupt levels** (`_init_vector_table` copies 13 handlers to VB):
level 1 `_inth_l1` → `_cpu_inth` (0x80001F), level 3 `_inth_l3` →
`_io_int_dispatch` (0x800003), level 5 `_inth_l5` → `_slot_int_dispatch`,
level 6 `_inth_l6` → `_joy_inth`, and the two timers at VB+44 and VB+48.
The kernel sets TIMER1 to -25,000 for a 1 ms tick at 25 MHz;
`_fix_3_minute_bug`, called from the idle thread, reloads it if it has
run past 75,000. The I/O interrupt bits as the kernel installs its
handlers: 0 floppy (`_InitFloppyDriver`), 1 SER1 and 2 SER2
(`_ser_init`; the 1993 draft has the serial bits the other way round,
`bebox_hardware.md` §6), 7 SCSI.

**The processor reset register.** Appendix A marks bit 0 of 0x80001B
"x" (unused) and bit 1 "Hobbit B"; `_start_cpu(1)` sets bit 1, so the
kernel and the draft agree that CPU 2 is bit 1.

**92010 or 92020.** Be's own introduction (15 Sep 1993) says the board
has two 92010s. No instruction in either kernel is 92020-only
(`beelf.py --unimpl` finds none; the ISA work's CPU-prefix-aware sweep
covered 35,378 instructions of one kernel and 32,190 of the other).
`_main1+0xf8` (0x080C12EC) compares the ID register with 0x0E33D03B and,
only if equal, prints "Running on Hobbit 020 processor" and points
`_flushpbe_vector` at `_flushpbe_020` (0x080C0120) instead of
`_flushpbe_ok` (0x080C0118, `FLUSHPBE R4`). `_flushpbe_020` tests bit 10
of the target address (`SHL3 $21`) and picks one of two unchanged
`FLUSHPBE` copies placed by address bit 10; the March and November
kernels pair them in opposite senses (ISA work). Neither kernel contains
the 92010's ID value: the model's 0x1000003B is `hobbit_sem.System`'s
default (and johnrash/bebox's choice), not a value read from Be's code;
any value other than 0x0E33D03B takes the 92010 path. `beboot.py` stays
on the default 92010 part.

One encoding matters for any decoder: MetaWare's code uses mode 7
*without* a CPU escape, which is `Roffset:UH`, the unsigned half-word
stack operand (PRM Table 1-21), e.g. `_memcpy+0x4e` (0x080DC9A6)
`MOV R12:UH,*R8:H`; 43 instructions in the Nov 1994 kernel use it.
`sem/hobbit_sem.py` executes it, and `asm/hobbit_asm.py` prints it (the
ISA work's commit b7dc9341; `beelf.py` had its own formatter until then,
and a sweep of the kernel and app_server is identical either way).

## Booting it: `tools/beboot.py`

The Hobbit BeBox board shares nothing with the Plan 9 terminal that
`tools/p9boot.py` models except the processor, so `beboot.py` is a new
board around the same `sem/hobbit_sem.py` privileged machine, one per
CPU on a shared bus (p9boot is unchanged). Every choice the sources leave
open is a named entry in its `CHOICES`; any access to something not
modelled stops the run with the PC, the device and the access.

    python3 -I tools/beboot.py --disk build/bebox/hdd-hobbit-9308000058/hobbit-9308000058.img \
        [--max-steps N] [--until TEXT] [--trace N] [--no-idle-skip]

With no ROM, the run does the ROM's job: it takes `/system/kernel` from
the disk (`tools/befs1.py`), loads its segments at their physical
addresses, stores the memory size at 0x08000048 and starts CPU 1 at the
ELF entry with the stack cache on (CHOICES `rom`, `entry-state`). CPU 2
starts at the same entry when the kernel releases it from reset.

**The board as modelled** (sources: `bebox_hardware.md`, Appendix A,
the data sheets in `docs/devices/`, and the kernel's code above):

| device | model | source |
|---|---|---|
| two ATT92010s, 25 MHz | `hobbit_sem.System` ×2, default 92010 part, ID 0x1000003B (the model's default; no kernel holds it), stepped by fewest cycles | `bebox_hardware.md` §2 |
| board registers 0x800003-0x80001F, Who Am I | `BoardRegs`, `WhoAmI` | Appendix A pp. 1-2 |
| SER1/SER2 (16C450-type) | `Uart`, transmit immediate | §10; kernel `_scc_*` |
| MC146818 clock | `Mc146818`, battery dead (VRT 0) | kernel `_rtc_*` |
| Am53C94 SCSI, 16-bit pseudo-DMA | `Ncr53c94` + `ScsiDisk` (LUN 0 only, writes to an overlay) | NCR 53C94 data sheet (Feb 1990) Table 8 p. 18, p. 33 |
| MCS3201 floppy controller, drive 1 empty | `Mcs3201` | MCS3201 data sheet §§5.2-5.6, 7.9-7.12 |
| VL82C106 keyboard controller, AT keyboard, PS/2 mouse | `Vl82c106Kbc` | VTI manual pp. 6-197..6-202 |
| printer port | `Parallel`, nothing attached | — |

**How far it boots** (Nov 23 1994 kernel, `be` disk; 2026-11-24). Each
stop below was a device the model lacked; each was added from its data
sheet and the kernel's driver, and the run went on:

1. ~3.1M instructions of `_spin_init` calibration; then the console
   banner on SER1 ("Be Labradors Kernel version of Nov 23 1994 …
   Kernel running from RAM in MULTIPROCESSOR mode / 01000000 bytes of
   RAM (16 MBytes) / starting cpu 1").
2. `_start_cpu` releases CPU 2 (0x80001B bit 1); it runs into the idle
   thread. Virtual memory on; the RTC initialised.
3. `_init_53c94` and the CAM scan: "path 0 target 0 lun 0 inqdata
   'BEBOOT  HOBBIT DISK     1994'" (6,081,674 instructions to "Disk
   cache is 4096K bytes"). The first model answered every LUN, and the
   kernel then saw eight disks; a SCSI-2 disk answers 0x7F for LUNs it
   does not have, and the model now does.
4. Stop at `_MotorOn+0x58`: DOR write 0x2D at 0x800DC8 (port 0x372).
   With the MCS3201 modelled, the floppy driver recalibrates drive 1,
   finds no diskette and says so in its own words ("PrepareMedia:
   DiskChanged TRUE twice (i.e. no disk in drive)", "fsmount failure").
5. "Volume 'be' w/size 332487 sectors mounted as id 0 on
   /dev/scsi_disk_driver_000" at 29,180,553 instructions.
6. Stop at `_wait_status+0x1c`: the keyboard controller's status port
   0x64 (0x800190), from `_kb_init`. Modelled from the VL82C106 pages;
   `_kb_init` and `_mouse_init` then pass.
7. No stop, but no progress: 311,567 interrupts in 90M instructions.
   `_ser_init` enables SER2's transmit-empty interrupt, and the first
   UART model held it asserted for as long as IER bit 1 was set. The
   VL16C452 sheet says a read of the IIR that reports THRE clears it
   (p. 6-57), and OUT2 (MCR bit 3) gates the output (p. 6-58); with
   that, the boot goes on.
8. The kernel starts user space: "Starting be:/system/debug_server...",
   "Starting be:/system/app_server...", "Waiting for picasso 59"
   (910 disk blocks read by then).
9. **Current stop**, at 40,282,356 instructions (rerun on the committed
   model, 2026-11-24; 910 disk blocks read, 1,866 interrupts): CPU 2, in
   user mode in `/system/app_server`, at `_video_init1+0x2`
   (0x100410F8), stores the byte 0x01 at physical 0xD10003C3. The bus
   word is 0xD10003C0 (lane 3) in BeBus slot 6, the display card's
   register window at 0xD1000000 (`bebox_hardware.md` §12). app_server's
   own code shows the card's layout: its helpers `_t_writecrtc` store to
   0xD10003D4/0xD10003D5, `_t_writeext` to 0xD10003C4/0xD10003C5, so
   VGA port p is the byte at 0xD1000000 + p, and 0x3C3 is the VGA
   enable register. The driver is compiled from `vgatri800600.c`
   (app_server's .comment), a Trident VGA at 800x600. No Be document
   describes the card; modelling it means reading `_video_init` and the
   `_t_*` helpers the way this file reads the kernel. Not done yet: this
   is the frontier, not the end of the boot.

The run reaches the mount (29M instructions) in about 10 minutes (CPU-bound Python,
~50k instructions/s). An idle skip (CHOICES `idle-skip`) jumps whole
laps of `_null_thread` when both CPUs are idle; `tests/test_beboot.py`
checks that a run with it ends in the same state, register for register
and word for word, as a run without it.

**Tests.** `tests/test_beboot.py`: device tests against the data-sheet
pages (no image needed), a boot test to "Disk cache is" (~2 min, skipped
with the fetch command when the disk image is absent), and, with
`BEBOOT_LONG=1`, the boot to the mount and the idle-skip check (the
default run to "Disk cache is" ends before the first skip is taken, so
the skip is checked only under `BEBOOT_LONG=1`).
