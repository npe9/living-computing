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
  the `be3` and `pixels` file trees.
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
  2009 MAME-forum thread knew of none
  (<https://forums.bannister.org/ubbthreads.php?ubb=showflat&Number=47590>);
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
  older tools to extract files and resources from these images, with a
  Hobbit disassembler.
- **typewritten.org** (<https://typewritten.org/Projects/Be/9308000058.html>):
  restoration notes on serial 9308000058, the machine one of the disks
  came from.
