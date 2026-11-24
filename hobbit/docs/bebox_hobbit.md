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

### The display card

No Be document describes the card in slot 6 (`bebox_hardware.md` §12:
frame buffer 0xD0000000, 1 MB; registers 0xD1000000, 0x6000 bytes). Its
driver is app_server's `vgatri800600.c`, and what follows is read from
that code (`tools/beelf.py build/bebox/beboot/system/app_server --dis
_video_init1`, and the `_t_*`, `_write_*`, `_tri_*` helpers) against
two outside sources: VGADOC's Trident chapter and XFree86's Trident
register header (`docs/devices/MANIFEST.md`). No Trident data sheet for
the part was found.

- **Port layout.** VGA port p is the byte at 0xD1000000 + p:
  `_t_writecrtc` stores to 0xD10003D4/0xD10003D5, `_t_writeseq` and
  `_t_writeext` to 0xD10003C4/0xD10003C5, `_t_writegr` to 0x3CE/0x3CF,
  `_t_writeatr` reads 0x3DA (to reset the attribute flip-flop) and
  stores index and data to 0x3C0, `_t_writepel` stores the DAC index to
  0x3C8 and three components to 0x3C9.
- **Which chip.** The graphics engine is reached through an index byte at
  0xD100217A and data bytes at 0xD100217C-F, and app_server polls index
  0x90, bit 7, for busy. That is XFree86's "Graphics Engine for
  9420/9430" register file, an index port plus four data bytes, with
  STATUS 0x90, MWIDTH 0xB8, MFORMAT 0xBC, STYLE 0xC4, mixes 0xC8, colours
  0xD8/0xDC, DIMXY 0xE0, DESTLINEAR 0xE4, DESTXY 0xF8 and COMMAND 0xFC.
  XFree86 puts that index port at 0x210A, and VGADOC cites Ferraro for
  "accelerator registers at 21xAh", so 0x217A is the same family with
  x = 7. The TGUI9440 and later have a different, directly addressed
  engine at 0x2120. app_server never uses a hardware cursor, which the
  9430 added (VGADOC). So the card is a **TGUI9420DGi or a TGUI9430**.
  The code cannot tell the two apart. `_video_init1+0x42` reads the
  chip-version register (3C4 index 0Bh), but only to switch to the new
  mode registers, and does nothing with the value. OSNews's "Trident
  TGUI9430 C" (`bebox_hardware.md` §12) is consistent with this.
- **Mode.** `_video_init(2)` programs 800×600 in 256 colours.
  - CRTC: horizontal total 0x7E, display end 0x63 (800 pixels), vertical
    display end 0x257 (600 lines), offset 0x32 in double-word mode, start
    address 0. Old mode control 2 is 0x38. Its bit 4 is VGADOC's paging
    mode, which doubles the offset: 0x32 × 8 × 2 = 800 bytes, the pitch
    the engine code uses (`_tri_hline`: y × 800 + x).
  - Sequencer 4 = 0x0E (chain 4), GC 5 = 0x40 (256-colour shift), GC 6 =
    0x05, attribute 0x10 = 0x41.
  - Trident: old-mode 0Dh/0Eh, then new-mode 0Dh/0Eh, CRTC 0x1E-0x29, GC
    0x0F = 4.
  - DAC: pixel mask 0xFF, then a 3-3-2 ramp with components up to 56.
    `_init_system_cs` then loads `/system/Color_map` through `_set_pel`
    and an 8-bit gamma table (`_gamma`, 0x05..0xFF), so white is 0xFF and
    the desktop grey 0xDD. The model takes the DAC as 8 bits per colour
    (CHOICES `display`); the card's DAC mode is not documented.
- **The engine as app_server drives it.** There are two commands, both
  set up through `_write_long` (index byte, then a 32-bit word with its
  bytes reversed, so the little-endian register gets its low byte at
  0x217C).
  - Fill: 0x0A000000, from `_rect_fill_copy_tri` and `_tri_hline`.
    Destination x/y in 0xF8 and as a linear address in 0xE4, size
    (w-1, h-1) in 0xE0, colour in 0xD8, style 0xFFFF, mix 0x303.
  - Blit: 0xA8000000 + d, from `_tri_blit1` and `_copy_to_hidden`.
    Source x/y in 0xF0 and linear in 0xE8 (0x98/0x9C repeat
    0xB8/0xBC). d is 1, 2, 4 or 7 as `_tri_blit1` chooses it for a copy
    running right/down, right/up, left/down or left/up, and the two
    linear addresses are then the corner the copy starts from.
  - XFree86's `OLDGE_FILL` is 0x000A0000, one byte lower than
    app_server's 0x0A000000. app_server's value is the one modelled; the
    difference is unexplained.

`TridentVga` in `tools/beboot.py` models exactly this and stops on
anything else: any other port, sequencer index, engine index or command,
an engine format or mix other than app_server's, and an engine access
beyond 1 MB. A blit or fill whose linear and x/y addresses disagree also
stops, since that would mean the reading above is wrong. Operations
complete at once, so the busy bit never reads set. Input status 1's
retrace bit runs from model time and the programmed CRTC and clock
(VGADOC's clock table). A byte read from the register window reads only
that port: `sem/hobbit_sem.py`'s `_read_lanes` hook tells the bus which
lanes a byte or half-word operand uses. Without it, `_t_readsts1`'s read
of 0x3DA would also read 0x3D8, a port that is not modelled. `--screen
FILE` writes the visible picture, through the DAC, as a PNG.

### DSP3210 contract (the host's side)

This section is read from the binaries only: the Nov 1994 kernel,
`/system/vcas_server` and the VCOS files on the `be` disk. The DSP3210's
own instruction set and the VCOS kernel's DSP code are out of scope. The
VCOS files are AT&T's: `os.ldf` is "Copyright(c) 1990 AT&T Bell
Laboratories".

**Who releases the DSPs.** vcas_server does, not the kernel. The kernel
only prepares to be interrupted by them.

- `_main` → `_vcBootDsp(0)` → `_vcInit` reads the VCOS configuration:
  - `/system/vcos/system/vcos.ini`: `VcosOem= be`, `MaxDsps= 3`.
  - `/system/vcos/be.oem/vcos.cfg`: board "Rev3", `DspType= 3210_F12`,
    `DspClock= 50000000`, 8 KB on-chip memory per DSP at 0xE000.
    `[dspN] Boot= 0x3d80 HostMem onchipDSPN 1`, and `StoreMem=
    HostMem`, so the DSPs' program store is host RAM.
- Then, for each DSP, `_vcLoadArmVCOS` → `_vcArmDsp` → `_veDspStart`.
- `_veInit` maps two kernel areas into vcas_server:
  - The kernel's `phram` area (all physical RAM, kernel virtual
    0xF8000000; `_kernel_asr_init+0x406`) is cloned at vcas virtual
    **0x60000000** as "dsp ram area". So vcas address 0x60000000 + x is
    physical RAM 0x08000000 + x. `_veLogToDspPhys` is the identity, which
    means a DSP-side address *is* that 0x6000_0000-based address.
  - The area holding the board registers is cloned as "io clone"; its
    base is kept in `_io_offset`.
- `_veDspStart(n)` (n = 1..3) takes the mask from `_dsp_control_bits`:
  0x10, 0x20, 0x40 (Appendix A: reset register bits 4-6 = DSP1-3). It
  ORs the mask into **both**:
  - the processor reset register 0x0080001B (1 = run), and
  - the internal interrupt register 0x0080001F (bits 6-4: an interrupt
    to DSP3-1).

  Both go through `_ori_byte` (`ORI R8,*R4:UB`, an interlocked byte OR).
  `_veDspHalt` clears both with `_andi_byte`.
- After the observed run the reset register holds 0x72 (CPU 2 and all
  three DSPs) and the internal interrupt register 0x70.

**What is written before release.**
- `_vcLoadArmVCOS` reads the VCOS kernel module with `_vcReadRelocMod`
  and relocates it into host RAM (StoreMem = HostMem).
  - The module is `/system/vcos/mml/os`: 4,352 bytes, first halfword
    0x09DD, with section names `__ModH`, `__boot` and `__vcos` in its
    header. `os.ldf` describes it as "_boot sPROG /* this is the boot
    mover */" and "_vcos sPROG" (the code).
  - `os_doblock` is byte-identical to `os` (both sha256
    ce8e43f9...2b67); `os_nodoblock` (4,038 bytes) differs. The image
    in RAM is `os`: of the 16-byte windows found only in `os`, 286 occur
    in the run's RAM image, and of those found only in `os_nodoblock`,
    none. The DSP
    task modules (`audio`, `daa`, ...) and their `.ldf`/`.tbd`
    descriptions are under `be.oem/` and `mml/`.
- `_vcLoadArmVCOS` then patches the loaded image through `_veDspWrMem`,
  which is a plain `memcpy` into the 0x60000000 window. It writes the
  addresses of the VCOS symbols `_global` and `_pcw` and a 204-byte
  descriptor. `_vcFixupVCOSSymtab` checks the symbols, and a missing one
  gives "Error 5000: File 'os'(the vcos kernel) is corrupted or the wrong
  version".
- `_vcArmDsp` looks up `_vcLoad`. With `_bootmode` set (from vcos.cfg's
  Boot line, `_vcSetDspTable+0x592`) it writes a 32-byte **boot block at
  vcas 0x60000000, i.e. physical RAM 0x08000000**. The block is four
  words each holding one byte of `_vcLoad`'s address, most significant
  first, then four zero words. With `_bootmode` = 0 it writes only the
  4-byte address itself, to DSP address 0. Both paths then call
  `_veDspStart`.
- In the run, RAM 0x08000000-0x0800000C reads 0x60, 0x0B, 0xE5, 0x68: a
  start address of 0x600BE568, i.e. physical 0x080BE568. The loaded VCOS
  image occupies 0x080BE4EC-0x080BFF2C, just below the kernel's text at
  0x080C0100.
- So the bottom of RAM is shared with the DSPs, and a DSP's address
  0x6000_0000 + x is host RAM 0x0800_0000 + x. That would explain
  Appendix A's "2 MB DSP shadow RAM at 0x60000000". This is inferred:
  the 32-byte block's byte-per-word layout reads like a byte-wide boot
  fetch, but how a DSP3210 boots is for the DSP manual to settle.
- The same low memory holds the boot ROM's memory-size word 0x08000048
  and vcas_server's DSP heap descriptor: `_dspmorecore` writes 0x60000074
  and frees from 0x60000078.

**What the host waits for.**
- **Nothing, at boot.** `_vcArmDsp` sets its "armed" flag (`OR $1`) right
  after `_veDspStart` and returns. `_vcBootDsp` and `_main` go on to
  `_vrmInit` and the message server loop (`_msg_session_init_server`).
  No code in the boot path polls DSP memory, reads a mailbox or waits
  for an interrupt, and there is no timeout because there is no wait.
- The **DSP → CPU path** is the kernel's. `_main1` calls `_dsp_int_init`:
  - It creates three semaphores, "dsp sem" (`_dsp_sems`).
  - It registers `_interrupted_by_dsp` with `_cpu_int_set(n)` for
    message types n = 1, 2, 3.
  - The handler table is at 0x080E4CF0. Types 4 and 5 are CPU A and B:
    `_interrupt_cpu` stores `get_cpu_id() + 4`.
- A message arrives through `_mailbox` (kernel data 0x080FC098, 24
  bytes, physical RAM):
  - +0: a spinlock word.
  - +4: a "pending" byte.
  - +5: an acknowledge byte. The receiver sets it to 1.
  - +6: the source/type byte.
  - +7: an argument byte.
  - +8..+0x17: 16 bytes of payload.
- The receiving CPU is interrupted through its bit (0 = Hobbit A, 1 =
  Hobbit B) of the internal interrupt register 0x0080001F. The model
  takes that at **level 1**, VB+20 → `_cpu_inth`.
- `_cpu_inth` clears its bit (`_reset_cpu_int`: an interlocked AND on
  0x0080001F) and dispatches on the type byte. For a DSP it calls
  `_interrupted_by_dsp`, which releases `_dsp_sems[n-1]` if nothing is
  already posted.
- The waiting side is the `_wait_dsp_int(n)` kernel call (KCALL 324): an
  `_acquire_sem` with **no timeout**. `_get_cpu_mailbox` (KCALL 328)
  returns the mailbox's address. Every user binary read carries the
  stubs: app_server, ansi_server, vcas_server, storage_server, Phone.
  No call to either was found. `beelf.py --refs` on each stub address
  lists nothing; the same search lists both `_veDspStart` calls of
  `_ori_byte`. Each stub address occurs once as a word in its file, and
  that is in the symbol table, past the loaded segments, so no data
  table holds it either. `libvcos.a` names neither. Instead, the clients reach the DSPs through
  vcas_server and shared-memory FIFOs (`libvcos.a`: `_vcReadFifo`,
  `_vcGetFifoReadCount`, ...).

**If the DSPs never answer.**
- No code path tests for a missing DSP. There is no "no DSP" message, no
  probe and no read-back of the reset register beyond the
  read-modify-write.
- vcas_server's errors (2003 "Dsp%d is invalid or unavailable", 6001
  "Unable to reset it") are about configuration and ids, not a silent
  part.
- The one configuration route is the DSP count. `_vcConfig` adds each
  `[dspN]` section to `_LTR`'s count, and if the count is 0 it prints
  "Error 2005: vcos.cfg: No DSP Memory Expressions entry found" and
  fails. `_vcBootDsp` then returns -1, and `_main` calls
  `_vcResetDsp(0)` and returns, so vcas_server exits without releasing
  anything. This was read, not run, and it needs an edited vcos.cfg on
  the disk.
- Model choice (CHOICES `dsp`): the reset and interrupt bits are kept as
  written and no DSP runs. That is equivalent, from the host's side, to
  leaving the DSPs in reset. With it the boot goes on with no stop:
  - All three DSPs are released at about 103M instructions.
  - By 162,819,522 instructions both CPUs are idle in `_null_thread`
    with the "Terminal 1" shell window up.
  - 8,248 interrupts and 2,419 disk blocks read; no "dsp" message on the
    console.
- What would hang is the first client that waits on a DSP: a `vcRead*`
  FIFO poll, or a `_wait_dsp_int` with no timeout. Phone and audio, for
  example, were not run.
- The console line "area_for error 03000000" printed while the servers
  start is not the DSPs. It is `_sh_init` (ansi_server, storage_server)
  probing for the shared heap at 0x03000000 before it exists, through
  the kernel's `_area_for`.

## Booting it: `tools/beboot.py`

The Hobbit BeBox board shares nothing with the Plan 9 terminal that
`tools/p9boot.py` models except the processor, so `beboot.py` is a new
board around the same `sem/hobbit_sem.py` privileged machine, one per
CPU on a shared bus (p9boot is unchanged). Every choice the sources leave
open is a named entry in its `CHOICES`; any access to something not
modelled stops the run with the PC, the device and the access.

    python3 -I tools/beboot.py --disk build/bebox/hdd-hobbit-9308000058/hobbit-9308000058.img \
        [--max-steps N] [--until TEXT] [--trace N] [--no-idle-skip] \
        [--screen FILE.png] [--save SNAP] [--resume SNAP]

`--screen` writes the display card's picture when the run ends.
`--save` pickles the whole machine; `--resume SNAP` continues it with
the current code. It is a development aid for the long runs, and a
snapshot is only as good as the code that wrote it.

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
| slot 6: Trident TGUI9420-family VGA, 1 MB | `TridentVga`: VGA/Trident registers, DAC, the old graphics engine's fill and blit, `--screen` | "The display card" above |

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
9. Stop at `_video_init1+0x2` (40,282,356 instructions): CPU 2, in user
   mode in `/system/app_server`, stores 0x01 at 0xD10003C3, the display
   card's VGA enable port, in BeBus slot 6. The card is modelled as
   described in "The display card" above.
10. With the card, app_server sets 800x600 and loads `/system/Color_map`.
    It clears the screen with an engine fill and draws its hand cursor at
    0,0 (`build/bebox/beboot/screens/desktop-80M.png`, at 80M
    instructions: a plain light-grey desktop). The console adds "Mouse
    responds with correct device type" and "Mouse enabled successfully".
    `_sysinit2` had printed "Waiting for picasso 59" and snoozed a second
    for app_server's `picasso` thread. It then starts ansi_server,
    vcas_server ("area_for error 03000000") and storage_server. It tries
    `/system/Browser` twice ("failed", "No Boot Browser"; the disk has
    only a lower-case `/system/browser`), and starts `/bin/newsh`, whose
    console prints "lseek(0, 0, 0) ->eof -1Failed-- subid 2 localid 0".
    app_server opens a window "Terminal 1": "Welcome to the new improved
    console / Running on a Hobbit / $ _"
    (`build/bebox/beboot/screens/terminal-103M.png`).
11. At 102,819,522 instructions: CPU 1, in user mode in vcas_server, at
    `_ori_byte` (0x1001CB20), called from `_veDspStart+0x36`, ORs 0x10
    into the processor reset register (0x0080001B), which releases DSP1.
    This was a stop until CHOICES `dsp`: the bits are now kept and no DSP
    runs (see "DSP3210 contract" above). vcas_server releases all three.
12. **Current state**: no stop through 162,819,522 instructions. Both
    CPUs are idle in `_null_thread`, with the "Terminal 1" shell window
    up; 8,248 interrupts and 2,419 disk blocks read. The next step is
    input: keys to the shell through the VL82C106.

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
