# The Hobbit BeBox ("Be machine", board "Sako"): hardware dossier

What Be Inc.'s pre-PowerPC machine was, part by part, to the depth needed for
a board model that boots its surviving software. Researched 2026-11-24.

This dossier leans on work on another branch that is not merged yet:
`worktree-agent-aeb73561b39e2ec97` (commit 8315ce07) holds the scan and
disk-image manifests (`hobbit/docs/bebox/`) and the software side's boot
model (`tools/beboot.py`). Until it merges, those paths do not exist on this
branch.

Each claim is tagged with the kind of evidence behind it:

| tag | evidence |
|---|---|
| **[S]** | Be Labs' draft *Be machine hardware documentation*, 15/16 Sep 1993 (page scans; "Sources" §1). Cited as `chapterN/pageM` exactly as the scan file is named (the case of `Page`/`page` varies). |
| **[K]** | The surviving kernels, read for this dossier: the physical-object table dumped from the ELF data, strings, and functions disassembled with `asm/hobbit_asm.py`, using `tools/bebox_kphys.py`, `tools/bebox_ksyms.py` and `tools/bebox_kdis.py` (Sources §2). |
| **[P]** | Photographs of surviving boards, read here (Sources §3). |
| **[E]** | Only the third-party emulator `johnrash/bebox` says so (Sources §4). Its rows drawn from "the September 1993 hardware notes" are the same scans as [S] and not independent. Only its "(found)" rows are independent, and this dossier re-checked only the ones marked [K]. |
| **[H]** | Secondhand history: Be Newsletter, bebox.nu, a book caption, owners' pages. |
| **[PPC]** | Carried over from the PowerPC BeBox by inference. |
| **[G]** | A guess, labelled as one. |

The cover letter that came with the drafts (`letter.jpg`) grades its own
chapters. The introduction is clean. Ch. 1 (Slots) is "internally inconsistent
and inaccurate", especially on arbitration and timing. Ch. 2 (I/O) is clean
except for joystick and SCSI. Ch. 3 (Joysticks) and ch. 9 (SCSI) are
unreviewed alphas. Chs. 4-6 are clean, ch. 7 (Floppy) "reasonably clean" and
ch. 8 (Printer) clean. Appendix A (Memory) "changed after last Be review". A
DMA chapter and a developer-guidelines chapter were never drafted. Where [S]
and [K] disagree below, [K] wins: the kernel ran on the board.

## 1. Summary: the board to model

| block | what it is | confidence |
|---|---|---|
| CPUs | 2 × AT&T ATT92010 "Hobbit", 25 MHz, on the shared bus; no external cache | high [S][P] |
| DSPs | 3 × AT&T DSP3210 at 50 MHz, bus masters with arbitration priority | high [S][P] |
| bus | "BeBus": synchronous 25 MHz, 32-bit, essentially the ATT92010 bus; 6 slots, 96-pin Metral; slots 1, 3 and 5 add a 24-pin DSP connector | high [S] |
| flash | 0.5 MB flash EEPROM at 0x00000000 (Am29F010 parts); no dump survives | high for map [S][K], part [P] |
| I/O window | 4 KB at 0x00800000: one 8-bit register per 32-bit word | high [S][K] |
| RAM | 0x08000000, two banks of four 30-pin parity SIMMs (1 MB or 4 MB), 4 to 32 MB | high [S][K][H] |
| DSP RAM | 2 MB "shadow RAM" at 0x60000000 | high for map [S][K] |
| combo I/O | VLSI VL82C106-class: two 16C450 UARTs, PS/2 keyboard/mouse controller, 146818A RTC, PS/2 parallel port | part inferred [S] |
| floppy | Motorola MCS3201 at ISA 0x370 (secondary), DMA by a board-level engine | high [S][P] |
| SCSI | AMD Am53C94 (NCR 53C94 second source), register lane 2, 16-bit pseudo-DMA | high [S][K] |
| interrupts | board registers at 0x800003-0x80001F: I/O sources, slot sources, internal (CPU/DSP) bits; per-CPU masks; Hobbit levels 1/3/5/6 | high [S][K] |
| console | SER1 (COM1, ISA 0x3F8), 19200 8N1 on a real machine | high [K][H] |
| video | not on the motherboard: a Trident VGA card in the slot at 0xD0000000 | medium [K][E][H] |
| Ethernet, phone, audio | slot cards at 0x90000000, 0xA0000000, 0xC0000000; chips unknown | map high [K], parts unknown |

## 2. CPUs

- **Count and part.** "Two 25 MHz CPU's (ATT 92010 'Hobbit' chips)" in the
  standard configuration [S `intro1.jpg`]. The ATT92010 is named again where
  the doc explains the slot interrupts [S `chapter1/page12`]. Surviving chips
  are marked `HOBBIT / BL-ATT92010-CN / 9309A` on S/N 9308000017
  [P `strickland_5841494811_b.jpg`]. bebox.nu reads the same date code, 9309A
  [H, quoted on the Haiku forum, 2012]. The silkscreen calls them CPU1 and
  CPU2; the register maps call them Hobbit A and Hobbit B.
- **Not the 92020.** No source puts a 92020 on a BeBox. The emulator notes
  that the November 1994 kernel carries extra code for the 92020 ID
  (0x0e33d03b) beside the 92010's 0x1000003b [E]. That is software
  readiness, not hardware.
- **Clock.** 25 MHz [S `intro1.jpg`, `chapter1/Page1`]. The bus clock signal
  is `CLK34`, "the 25-MHz BeBus clock", with a 40 ns period
  [S `chapter1/page8`, `Page17`]. `CLK34` is the Hobbit's own phase-3/4 clock
  input (ATT92010 data sheet, `docs/ATT92010_Hobbit_Microprocessor_Data_Sheet_Dec92.pdf`),
  so the CPUs and the bus share one clock. The datasheet's rated points are
  20 MHz at 3.3 V and 30 MHz at 5 V. Rev 1 already ran at 25 MHz
  [H, Shibata caption 6].
- **Cache and MMU.** These are on-chip only: the 3 KB prefetch buffer, the
  decoded-instruction cache, the stack cache and the dual-TLB MMU of the
  92010 (`docs/isa_inventory.md`). Nothing in [S] or [P] shows an external
  cache.
  - The bus carries an optional `NCACHE-`/`CACHE` signal: the master's view
    of whether an access is cachable [S `chapter1/page4`, `page11`].
  - The kernel's source names include `hob/vm_hobbit.c` [K], so paging uses
    the Hobbit MMU.
  - The emulator boots with CONFIG = 0x001c0000 (stack cache, instruction
    cache and prefetch on) [E]. That is the emulator standing in for the lost
    boot ROM.
- **CPU identity.** The "Who Am I" register at 0x800DC3, bits 3-0, gives
  the current bus master: 4 = CPU 1, 5 = CPU 2 [S `appendix/page2`].
  `_get_cpu_id` returns `(*0x800dc3 & 15) - 4` [K].
- **Starting CPU 2.** The Processor Reset Register is at 0x80001B; 0 holds a
  processor in reset, 1 lets it run.
  - [S `appendix/page2`]: bit 1 = Hobbit B, bits 4-6 = DSP 1-3; bits 0, 2,
    3 and 7 are "x".
  - [K]: `_start_cpu(1)` takes the mask byte 0x02 from `_cpu_masks` (= 01 02).
    It clears that bit, spins 2000 µs, then sets it again. `_start_cpu(0)`
    refuses.
  - So Hobbit A has no reset bit: it runs from power-on. The emulator's "bit
    0 CPU 1" [E] is its own model, which the kernel never exercises.

## 3. Memory map

Physical, as seen by the CPUs. All words are big-endian: byte 0 is bits
31-24 [S `appendix/page1`, `page3`].

| range | contents | evidence |
|---|---|---|
| 0x00000000-0x0007FFFF | flash EEPROM, "0.5 Mbyte currently implemented" | [S `appendix/page3`]; the kernel maps `rom` 0x1000+0x7F000 [K] |
| 0x00800000-0x00800FFF | I/O window, "4 Kbytes currently implemented" | [S `appendix/page3`]; kernel `io` 0x00800000+0x1000 [K] |
| 0x08000000-… | RAM | [S `appendix/page3`]; kernel `phram` 0x08000000 [K]; the ROM tests from 0x08000000 [H typewritten] |
| 0x60000000-0x601FFFFF | 2 MB DSP "shadow RAM" | [S `appendix/page3`, `page4`]; the kernel has the name `dsp ram` among `sako/dsp.c`'s strings [K] |
| 0x80000000-0xDFFFFFFF | six slots of 256 MB each, selected by A<31:28> | [S `appendix/page3`, `chapter1/page4`, `page12`] |
| 0xE0000000-0xFFFFFFFF | reserved | [S `appendix/page3`] |

**Slot numbering.** Appendix A puts Slot 1 at 0x80000000 and Slot 6 at
0xD0000000 [S `appendix/page3`]. The emulator labels 0x90000000 "slot 1" and
0xD0000000 "slot 5" [E]. This dossier follows Be's numbering, on this
evidence:

- The DSP connector is on slots 1, 3 and 5, and "in the standard
  configuration" those slots carry telephony, video and audio
  [S `intro1.jpg`, `chapter1/Page2`].
- The Nov 1994 kernel puts `phone_regs` at 0xA0000000 and `audio_regs` at
  0xC0000000 [K]. Those are Be's slots 3 and 5, both DSP slots.
- The March 1994 kernel had `audio_regs` at 0x80000000, Be's slot 1 and also
  a DSP slot, and named 0xC0000000 `slot_c` [K]. The audio card moved between
  DSP slots.
- The kernel's own names (`slot_8`, `slot_c`) use the address nibble.

The slot interrupt bit of a card is (Be slot − 1): bit 0 is Slot 1
[S `appendix/page1`]. The emulator's 1 << its-slot-number lands on the same
bit, so its hardware is right; only its labels differ.

**The kernel's table of physical objects.** These are entries of {name, 1,
base, size}, read from the Nov 1994 kernel's data at 0x080E1280 [K]:

| name | base | size | reading |
|---|---|---|---|
| `phram` | 0x08000000 | 0 (sized at boot) | RAM |
| `rom` | 0x00001000 | 0x7F000 | flash above its first 4 KB |
| `io` | 0x00800000 | 0x1000 | I/O window |
| `slot_8` | 0x80000000 | 0x1000 | slot 1 (DSP slot), unassigned |
| `ether_regs` | 0x90000000 | 0x1000 | Ethernet card, slot 2 |
| `ether_sleep` | 0x98000000 | 0x1000 | same card, second decode |
| `phone_regs` | 0xA0000000 | 0x1000 | telephone card, slot 3 (DSP) |
| `hw_devel1`, `hw_devel2`, `hw_devel3` | 0xB0000000, 0xB1000000, 0xBFFC0000 | 0x2000, 0x2000, 0x40000 | development card, slot 4 |
| `audio_regs` | 0xC0000000 | 0x1000 | audio card, slot 5 (DSP) |
| `vga_new` | 0xD0000000 | 0x100000 | frame buffer, slot 6 |
| `vga_new_reg` | 0xD1000000 | 0x6000 | video registers |

The March 1994 kernel's table (at 0x0821C1A8, file offset 0x1C1A8) has the
same layout with `audio_regs` at 0x8, `slot_c` at 0xC, and `phram` fixed at
0x08000000 + 8 MB. It is preceded by an entry `ram` with flag 2 and base and
size 0 [K].

**Slot card ROM.** The draft requires every card to carry a byte-wide
configuration ROM on data lines 7-0, at the top of the card's address space,
for the OS to read at boot [S `chapter1/Page2`]. The kernel has `_get_slot_rom_addr` (4 bytes) and
`_get_slot_resources` (2 bytes), so in Nov 1994 these were stubs [K]. A model
can leave the ROMs out.

## 4. RAM

- **Type and layout.** Eight 30-pin SIMM sockets, each SIMM with three DRAM
  packages (×9, parity) [P `strickland_5841616027_b.jpg`]. 30-pin ×9
  "1 MB and 4 MB parity SIMMs", two banks, not necessarily matched; a jumper
  picks 60 or 70 ns timing [H typewritten #58]. Eight ×9 SIMMs make two
  32-bit banks of four [G, arithmetic].
- **Sizes.** The ROM's sizing tries bank pairs "16/16, 16/4, 16/0, 4/4"
  [H typewritten #58 boot log]. The kernel knows 4, 8, 16, 20 and 32 MB [E].
- **Boot contract.**
  - The ROM writes the size to low RAM; the emulator puts it at 0x08000048
    [E].
  - The kernel has the message "Old boot roms - assuming 8 meg (lowmem was
    %.8x)" [K], which confirms the handoff.
  - A warm reset skips the test: "Warmstart: remembered memory size is
    00800000" [H typewritten].
- **Parity.** "Writing address parity / checking address parity" appear in
  the ROM's test [H typewritten]. No [S] page documents a parity-error
  interrupt.

## 5. ROM

- **Size and place.** Flash EEPROM, 0.5 MB, at 0x00000000 [S `appendix/page3`];
  the kernel maps 0x1000-0x7FFFF of it as `rom` [K].
- **Parts.** One socketed DIP-32 is legible as AMD `AM29F010-120PC`
  (128 KB, 120 ns, © 1991) beside the "COMBO I/O" chip
  [P `strickland_5841550383_b.jpg`]. Three or four more socketed DIP-32 chips
  with numbered green stickers are visible next to the SIMMs
  [P `strickland_5841616027_b.jpg`]. Four Am29F010s on a 32-bit bus would make
  exactly 0.5 MB [G: arithmetic plus partial view; the other markings are not
  legible].
- **Contents.** No dump survives. The software agent searched; the emulator
  author found none [E]. What the ROM does is known only from its console
  output (memory test, sizing, warm start [H typewritten]) and from its
  handoff: it loads `/system/kernel` (ELF, machine 0x39D) and enters it
  [E, and the kernel's ELF header [K]]. A model has to stand in for it.

## 6. Interrupts

The interrupt controller is board logic, not an AT&T 9201x companion chip.
All its registers are 8 bits wide, at byte lane 3 of their word
[S `appendix/page1`, `page2`]:

| address | register | bits (7 … 0) |
|---|---|---|
| 0x800003 | I/O interrupt (1 = interrupting) | 7 SCSI, 6 mouse, 5 keyboard, 4 RTC, 3 printer, 2 and 1 serial (see below), 0 floppy |
| 0x800007 | I/O mask, CPU 1 (1 = not masking) | same |
| 0x80000B | I/O mask, CPU 2 | same |
| 0x80000F | slot interrupt (also joystick "Port D" data) | 5..0 = slots 6..1 |
| 0x800013 | slot mask, CPU 1 | same |
| 0x800017 | slot mask, CPU 2 | same |
| 0x80001B | processor reset (0 = reset) | 6/5/4 DSP 3/2/1, 1 Hobbit B |
| 0x80001F | internal processor interrupts | 6/5/4 DSP 3/2/1, 1 Hobbit B, 0 Hobbit A |
| 0x800DC3 | who am I | 7-4 joystick B2, B1, A2, A1 buttons; 3-0 current bus master (0 DMA, 1-3 DSP 1-3, 4-5 CPU 1-2, 6-11 slots 1-6) |

**Serial bits: the draft and the kernel disagree.**

- The draft gives Serial 1 = bit 2 and Serial 2 = bit 1, twice
  [S `appendix/page1`, `chapter6/page2`].
- Both surviving kernels do the opposite [K].
  - Nov 1994, `_ser_init`: unit 0 uses port 1016 (0x3F8, SER1), calls
    `_io_int_set(1, _sera_inth)` and enables bit 1. Unit 1 uses port 760
    (0x2F8, SER2) with bit 2.
  - Mar 1994, `_ser_init` (0x08214CD8): unit 0 loads the register addresses
    0x800FE3-0x800FFB (SER1) and calls `_int3_set(1, _sera_inth)`; unit 1
    loads 0x800BE3-0x800BFB (SER2) and calls `_int3_set(2, _serb_inth)`.
    `_int3_set(n, h)` stores h in slot n of the I/O handler table, and the
    dispatcher calls slot n for bit n.
  - The two kernels are 6 and 14 months newer than the draft, and agree with
    each other, so the board as it ran had SER1 on bit 1.
- **Model SER1 = bit 1 and SER2 = bit 2.** The emulator agrees [E].

**Other bits and handlers.**

- Keyboard bit 5, mouse bit 6 and RTC bit 4 come from [S `chapter4/page3`,
  `chapter5/page2`]. Floppy bit 0 is [S `chapter7/page4`]. Printer bit 3 is
  [S `chapter8/page2`]; it is the only bit software must clear, by writing
  0x08 to 0x800003.
- SCSI bit 7 is marked "[?]" in the alpha draft [S `chapter9/page3`]. The
  emulator wires the SCSI controller to bit 7 and boots [E].
- `_io_int_dispatch` ANDs `*0x800003` with its enabled set and calls
  handlers 0-7 in order [K]. `_io_int_enable` ORs into the word at 0x800004,
  whose low byte is 0x800007, the CPU 1 mask [K].

**Hobbit interrupt levels** [K, the `_inth_lN` entry points]:

| level | source | kernel handler |
|---|---|---|
| 1 | internal processor interrupts (0x80001F) | `_cpu_inth` |
| 3 | I/O devices (0x800003) | `_io_int_dispatch` |
| 5 | slots (0x80000F) | `_slot_int_dispatch` |
| 6 | joystick controller | `_joy_inth` |

Which board line drives which Hobbit interrupt pin is not in [S]; this table
is the kernel's view.

**Inter-processor interrupts.** `_set_cpu_int(n)` ORs `_cpu_masks[n]`
(0x01 for CPU 1, 0x02 for CPU 2) into 0x80001F; `_reset_cpu_int` clears the
current CPU's own bit [K]. So the register is written to raise and to clear.
The message itself goes through a mailbox in RAM, read by `_cpu_inth` [K].

**DSP interrupt bits.** Bits 4-6 [S `appendix/page2`]. The emulator says
2-4 [E], but it does not emulate the DSPs, so nothing tested that.

## 7. I/O window and the combo I/O chip

**Address rule.** A PC port number p maps to 0x800000 + 4p + 3. The printer
chapter states it as "data-sheet address * 4 + 800003" [S `chapter8/page2`].

| function | ISA ports | Be addresses | evidence |
|---|---|---|---|
| joystick | 0x03; 0x17, 0x18 | 0x80000F; 0x80005F, 0x800063 | [S `chapter2/page4`, `chapter3/page2`] |
| keyboard and mouse | 0x60, 0x64 | 0x800183, 0x800193 | [S `chapter2/page4`, `chapter4/page1`] |
| RTC | 0x70, 0x71 | 0x8001C3, 0x8001C7 | [S `chapter5/page1`] |
| SER2 | 0x2F8-0x2FF | 0x800BE3-0x800BFF | [S `chapter2/page4`] |
| floppy | 0x372-0x377 | 0x800DCB-0x800DDF | [S `chapter2/page4`, `page5`] |
| LPT | 0x378-0x37A | 0x800DE3-0x800DEB | [S `chapter2/page5`] |
| SER1 | 0x3F8-0x3FF | 0x800FE3-0x800FFF | [S `chapter2/page5`] |
| SCSI | regs 0-0xF, lane 2 | 0x800802 + 4·reg; 16-bit pseudo-DMA at 0x800842 | §9 |
| floppy DMA | — | 0x800020-0x80002F | [E] (§8) |

**The part: VLSI VL82C106 "PC/AT Combo I/O chip" [inferred].**

- The drafts cite "VLSI" by page: keyboard controller "6-197", printer
  "6-192-193", serial "6-61" [S `chapter4/page1`, `chapter8/page1`,
  `chapter6/page1`].
- In VLSI Technology's 1990 *Computer Products* data manual
  (`docs/devices/1990_VTI_Computer_Products.pdf`), the VL82C106 runs from
  6-185 to 6-220.
  - Its keyboard-controller programmer interface is p. 6-197 (PDF p. 452).
  - Its parallel-port register description is pp. 6-192-193 (PDF p. 447-448).
  - Pages 6-59..6-63 fall in the VL16C452 sheet, whose UARTs the VL82C106
    reuses (p. 6-61 = the IIR table, PDF p. 316).
- The VL82C106 combines two VL16C450 UARTs, a parallel port, a PS/2 or AT
  keyboard/mouse controller and a 146818A RTC (6-185, PDF p. 440). That is
  exactly the I/O list of [S `chapter2/page1`] minus floppy and SCSI.
- A large windowed ceramic QFP sits under the silkscreen "COMBO I/O" (U400)
  [P `strickland_5841550383_b.jpg`]. The window suggests an engineering
  sample [G]. Its marking is not legible.
- The drafts also cite "Mo …" (e.g. "Mo C-17", "Mo A8-1") and "LapKat p.
  A5-2". These are unidentified reference documents.

**Consequences for the model.**

- **UARTs** are 16C450-class: the draft lists no FIFO control register
  [S `chapter2/page4`, `page5`]. The baud clock is not 1.8432 MHz.
  - "Baud Rate = 114,688 / DL" [S `chapter6/page12`], so the UART input
    clock is 16 × 114,688 = 1,835,008 Hz.
  - The table on [S `chapter6/page13`] gives −0.45 % error at every
    standard rate from 50 to 38,400 baud: DL = 12 gives 9557 baud and
    DL = 6 gives 19,115.
  - The emulator uses a 16550 at 1.8432 MHz [E]. That is close enough for
    a byte-level console but not the documented part or clock.
- **Keyboard controller.** "The keyboard controller uses the PS/2 command set
  contained in ROM" [S `chapter4/page1`]: an 8042-type controller with PS/2
  mouse support. On a real machine, a Fujitsu FKB4700 keyboard makes the ROM
  loop on "ate kbd data: 000000ff"; IBM Model M and generic AT keyboards
  work, and a 2-button PS/2 mouse works [H typewritten].
- **RTC.** 146818A-compatible, indexed through 0x8001C3/0x8001C7, interrupt
  on bit 4 [S `chapter5`]. Its backup battery is an external Rayovac 844,
  4.5 V [P `strickland_5842090860_b.jpg`].
- **Joysticks.** Two 15-pin ports. Coordinates are multiplexed through
  0x80005F under channel bits in 0x800063; buttons appear in Port D
  (0x80000F) and in "Who Am I" [S `chapter3`, alpha]. The Nov 1994 kernel
  talks to a "PMC" microcontroller (`_send_pmc_cmd`, `_wait_pmc_ready`,
  `_pmcbuf`) [K]; the emulator puts it at ISA 0x222/0x226 [E]. That is later
  than the draft and not documented.

## 8. Floppy

- **Controller.** Motorola MCS3201: "Chapter 7 … [MCS3201 p.12-13]" and
  similar cites throughout [S `chapter7`]. A chip marked `…S3201FN QHKM9222`
  with the Motorola logo sits next to the "FDC" header
  [P `strickland_5841550383_b.jpg`]. Data sheet:
  `docs/devices/MCS3201_IBM_PC_XT_AT_Floppy_Disk_Controller_1991.pdf`.
- **Formats.** Two drives; 360K, 720K, 1.2M and 1.44M; 250, 300 and 500 kb/s
  [S `chapter7/page1`].
- **Address.** The secondary PC address: DOR 0x372 → 0x800DCB, MSR 0x374 →
  0x800DD3, data 0x375 → 0x800DD7, DIR/CCR 0x377 → 0x800DDF
  [S `chapter2/page4`, `page5`].
- **Interrupt.** Bit 0, gated by DMAIE in the DOR [S `chapter7/page4`].
- **DMA.** The drafts say transfers go through "the DMA controller", a bus
  master (CBM 0) [S `chapter7/page5`, `appendix/page2`]. The DMA chapter was
  never written [S `letter.jpg`].
  - The emulator, from the kernel's `sako/flopdma.c`, puts the DMA
    registers in the I/O window: count − 1 at 0x800020 (writing it starts
    the transfer), direction at 0x800024, address bits 31-16 at 0x80002A and
    15-0 at 0x80002E [E].
  - The kernel does have `sako/flopdma.c` [K]; the register layout was not
    re-checked here.

## 9. SCSI

- **Part.** "Chapter 9 : The SCSI Controller [AMD Am53C94]"
  [S `chapter9/page1`]. Its page cites match AMD's Am53C94/Am53C96 data
  sheet, Publication 16506 Rev. C (1993), page for page:
  [p.17] transfer counter, [p.22] internal state, [p.29] clock factor and
  [p.32] data alignment. Held as `docs/devices/am53c94.pdf`; NCR's original
  53C94 sheet (Feb 1990) is beside it. The emulator calls it an NCR 53C94
  [E]; the two are the same register set.
- **Registers: lane 2.**
  - The alpha draft lists 0x80080B, 0x80080F, … for registers 2-F (lane 3)
    and 0x800802/0x800803 for the transfer count [S `chapter2/page5`,
    `chapter9/page4`-`page24`].
  - Both kernels' data say `_reg_base` = 0x00800802, `__cmd_reg` = 0x0080080E
    and `__fifo_reg` = 0x0080080A (Nov 1994; Mar 1994 at 0x0821F3D0-F3E4).
    `_init_53c94` steps the registers by 4 from `_reg_base` (clock factor at
    +36, i.e. register 9) [K].
  - So register n is at 0x800802 + 4n. Both kernels, written for the running
    board, contradict the alpha draft, which is wrong here. The emulator
    agrees with the kernels [E].
- **Pseudo-DMA.** A 16-bit pseudo-DMA port at 0x800842/0x800843; the draft
  asks "WHAT DOES THIS DO?" [S `chapter9/page24`]. The emulator's reading:
  each 16-bit access moves the next two bytes of a DMA transfer, and the
  board holds the CPU until the chip has them [E].
- **Clock.** The draft's selection-timeout example uses a 25 MHz clock and
  clock factor 5 [S `chapter9/page13`]. Clock factor 5 means 20.01-25 MHz
  [S `chapter9/page18`]. The kernel writes 5 to the clock factor register
  [K `_init_53c94`]. So the 53C94 runs from the 25 MHz bus clock [inferred].
- **Interrupt.** I/O bit 7 (see §6).

## 10. Serial and console

- **Ports.** Two 16C450-class UARTs: SER1 (COM1) at ISA 0x3F8 and SER2 at
  0x2F8 (§7). The baud clock is §7's.
- **Console.** The surviving machine's console is "ttya" at 19200 8N1
  [H typewritten]. The kernel's unit 0 is the 0x3F8 port [K `_ser_init`];
  the emulator shows the kernel's progress on serial port 1 [E]. The kernel
  also has `/dev/modem` and `/dev/midi` drivers (`sako/modem.c`,
  `sako/midi.c`) [K], and the back panel has "some variety of analog
  telephone adapter" [H typewritten]. These are slot or DSP devices, not
  further UARTs [G].
- **Back panel** of #58: two serial ports, one parallel port, a phone adapter,
  an AT keyboard port, a PS/2 mouse port and a floppy [H typewritten].

## 11. Ethernet

No Ethernet on the motherboard [S `chapter2/page1` lists none]. The kernel
maps an Ethernet card at 0x90000000 (`ether_regs`) with a second decode at
0x98000000 (`ether_sleep`) [K]. The chip is not named anywhere found. The
emulator does not emulate it [E]. The 1994 system starts without it [E].

## 12. Video

No video on the motherboard [S `chapter2/page1`]. The display is a slot
card at 0xD0000000 (frame buffer, 1 MB) and 0xD1000000 (registers, 0x6000),
named `vga_new` [K].

- OSNews (2009) names a "Trident TGUI9430 C" in a Hobbit BeBox [H]. The name
  is unchecked; Trident's TGUI94x0 family has a GUI accelerator in that
  register range [G].
- The emulator reads the window servers (`vgatri640480.c`) as a Trident VGA
  at its VGA port numbers plus a graphics engine. The engine is reached
  through index 0x217A and 32-bit data at 0x217C, at 640×480 or 800×600 in
  256 colours [E].
- On #58 the card puts out VGA at 800×600, 54.6 kHz horizontal and 82 Hz
  vertical [H typewritten].
- Earlier revisions had graphics cards Sakoman built himself
  [H bebox.nu 1990, 1992-93].

## 13. The DSP3210s and how the CPUs talk to them

- **Parts.** Three AT&T DSP3210 at 50 MHz [S `intro1.jpg`].
  - The chips are marked `DSP3210 / F12 072 / 9309S 9655574 / © 91 AT&T`,
    silkscreen DSP1-DSP3 [P `strickland_5841494811_b.jpg`]. bebox.nu reads
    the date code as 9308 [H].
  - Wikipedia's "three AT&T 9308S digital signal processors" turns this date
    code into a part number.
- **Which DSP serves which slot.** Each DSP has its own slot (1, 3 or 5), whose
  24-pin Metral connector carries that DSP's serial I/O (DI, ICK, ILD, DO,
  OCK, OLD …) and 8-bit BIO port straight to the card
  [S `chapter1/Page2`, `page28`-`page31`]. The pin table on page 30 is
  blank in the draft.
- **On the bus.** The DSPs are bus masters in the arbiter's Group 1. They
  always win over Group 2 (DMA, CPUs, slots) and may keep the bus as long as
  they keep requesting it [S `chapter1/page6`, `Page7`]. Ch. 1 is the
  draft's least reliable chapter.
- **DSP memory map** [S `appendix/page4`, citing the DSP3210 manual pp.
  3-9..3-10]:
  - On chip: boot ROM at 0; memory-mapped I/O at 0x400-0x41F (ibuf 0x404,
    obuf 0x408, ioc 0x40C, bioc 0x41B, bio 0x41E); RAM1 at 0xE000 and RAM0
    at 0xF000, each 1K × 32.
  - Off chip: everything from 0x10000 is Be machine memory. Once the DSP
    has run its internal boot code it continues at 0x60000000, in the shadow
    RAM.
- **How the CPUs talk to them.**
  1. *Shared memory.* The 2 MB at 0x60000000 is the DSPs' boot and working
     memory; the OS protects it [S `appendix/page4`]. The kernel's
     `sako/dsp.c` strings include `dsp ram` and `dsp sem` [K].
  2. *Reset.* The Processor Reset Register bits 4-6 hold or release DSP 1-3
     [S `appendix/page2`]. A CPU writes code into the shadow RAM and then
     releases the DSP, which boots from 0x60000000 [G, from the two facts].
  3. *Interrupts.* Bits 4-6 of 0x80001F are the DSPs' internal interrupt
     bits [S].
     - `_dsp_int_init` registers `_interrupted_by_dsp` for internal-interrupt
       types 1, 2 and 3 through `_cpu_int_set` [K].
     - `_interrupted_by_dsp` releases the semaphore in `_dsp_sems[n]` [K].
     - So a DSP signals a CPU through level 1, with the type in the RAM
       mailbox read by `_cpu_inth` [K].
     - How a CPU interrupts a DSP was not found; DSP3210 pins are needed
       [G: probably the same 0x80001F bits].
  4. *Software.* The kernel source `sako/dsp.c` [K]. The `be3` disk holds
     DSP code: `system/vcos/mml/*.s`, including `g711e.s`, `throttle.s` and
     `src1t2.s` (sample-rate converters) [disk listing: the software agent's
     `be3` file-system dump]. "VCOS" is AT&T's real-time OS for the DSP3210.
- **Data book.** Not found online (Sources, "Searched").
- **What a model needs.** A boot needs none of this: the 1994 system starts
  without the DSPs, and its sound server reports an error [E]. A model can
  hold the DSPs in reset, keep the 2 MB at 0x60000000 as plain RAM, and
  never raise bits 4-6.

## 14. Bus, GeekPort and glue

- **BeBus** [S `chapter1`]:
  - Synchronous, 25 MHz, 32-bit address and data, up to one word per 40 ns
    cycle (100 MB/s burst).
  - It "closely (but not identically)" follows the ATT92010's own bus
    signals: `STC-` (start), `DTACK-`, `BM<3:0>` byte masks, `IOCNT<1:0>`
    double and quad transfers, `LOCK-`, `RETRY-`, `BERR-`, `NCACHE-`, `D/T-`,
    `BREQ-`/`BGRANT-` per device, `SEL-` and `SIRQ-` per slot, and `CLK34`
    [S `chapter1/Page7`-`page12`].
  - This is the bus `bsv/HobbitBus.bsv` already models from PRM Appendix A.
  - A watchdog asserts `DTACK-`+`BERR-` 127 clocks after `STC-` with no
    answer [S `chapter1/page5`].
  - Arbitration is a wrap-around list in two groups (§13) [S `chapter1/page6`].
- **Slots.** Six, 96-pin Metral; slots 1, 3 and 5 add the 24-pin DSP
  connector [S `intro1.jpg`, `chapter1/Page2`, `Page15`]. "Rev2 … ISA-like
  slots", and Rev 3 changed the connector, which "remained in the released
  Hobbit machines" [H r/beos summary of Shibata].
- **GeekPort.** None. The 1993 drafts document joystick, serial, parallel,
  keyboard, mouse, floppy and SCSI, and no GeekPort or A/D port; the OCR of
  all 176 pages has no "geek". The GeekPort is a PowerPC BeBox feature (§15).
- **Glue.**
  - [P]: bus buffers marked with a "Q" logo near the combo chip (U402, U403,
    U406), and a large PLCC with a sticker, marking illegible, beside the
    SIMMs [P `strickland_5841616027_b.jpg`]. Owner's caption on the windowed
    part: "custom logic" [H].
  - [G]: the arbiter, the interrupt registers, the I/O-window lane steering,
    the floppy DMA engine and the pseudo-DMA wait states are probably in
    programmable logic (PALs/EPLDs).
  - No schematic, PAL equation or part list survives online.

## 15. What carries over from the PowerPC BeBox

The PowerPC BeBox (MAME `src/mame/be/bebox.cpp`, `bebox_m.cpp`, `bebox.h` at
commit `dfc4d33d47030cb35ae6cbbc5c2a8a9a214383fd`; NetBSD/bebox) shares
little silicon with the Hobbit board:

| function | Hobbit board | PowerPC BeBox (MAME) |
|---|---|---|
| bridge | none (CPUs on the BeBus) | MPC105, PCI, Intel 82378ZB SIO (`bebox.cpp` lines 154, 166) |
| super I/O | VL82C106 + MCS3201 | Intel 82091AA AIP (`bebox_m.cpp` header comment) |
| SCSI | Am53C94 | NCR 53C810 on PCI (`bebox.cpp` line 158) |
| UARTs | two 16C450 | four 16550 (`bebox.cpp` lines 113-114, 139-140) |
| RTC | 146818A in the combo | MC146818 / BQ3285 (`bebox.cpp` line 197; `bebox_m.cpp` table) |
| flash | 0.5 MB at 0 | at 0xFFF00000 (`bebox.cpp` lines 101-102) |

What does carry over is the **glue-register scheme** [PPC]. The PowerPC
board also has:

- per-CPU interrupt masks (0x7FFFF0F0 CPU 0, 0x7FFFF1F0 CPU 1);
- an interrupt-source register (0x7FFFF2F0);
- a cross-processor interrupt register (0x7FFFF3F0);
- a processor-reset register (0x7FFFF4F0).

These are `bebox.cpp` lines 94-98. The Hobbit board's 0x800007/0x80000B
masks, 0x800003/0x80000F sources, 0x80001F internal interrupts and 0x80001B
resets are the same idea at byte width. So are the joystick buttons in a
register and the PC-port I/O layout. The GeekPort, MIDI, infrared and the
A/D converter are PowerPC-only (`bebox_m.cpp` port table).

## 16. Revisions, serial numbers, dates

| when | what | evidence |
|---|---|---|
| mid 1990 | Gassée and Sakoman leave Apple | [H bebox.nu 1990] |
| end 1990 | **Rev 1**: wire-wrapped and hand-wired; one Hobbit at 25 MHz, memory and one serial port | [H Shibata caption 6, `shibata_rev1.jpeg`]; Sakoman's own words: "a single processor, memory, and a serial port. The next version added slots and bus arbitration, the one after that additional processors, then various flavors of I/O" [H bebox.nu 1990] |
| 1991 | **Rev 2**: printed circuit board, still one CPU and one serial port, daughter cards with I/O plug in; label "Be Motherboard revision 2" | [H Shibata caption 7, `shibata_rev2.jpeg`] |
| ? | **Rev 3**: first with two CPUs (still Hobbit) and three DSP3210s | [H Shibata caption 8] |
| ? | **Rev 4**: Rev 3 with its bugs fixed; label "Be Machine board revision 4"; CPUs and DSPs in sockets | [H Shibata caption 8, `shibata_rev4.jpeg`] |
| ? | **Rev 5**: surface-mounted parts | [H r/beos 2024 summary of Shibata; caption not seen] |
| Aug-Sep 1993 | the machines that survive: S/N 9308000009, …017, …044, …058, labelled "Rev. A"; chips with date codes 9309 (Sep 1993). Surface-mounted QFP CPUs and DSPs [P], which fits Rev 5 [G] | serial label and chips [P `strickland_5842009852_b.jpg`, `strickland_5841494811_b.jpg`]; "BeBox Rev. A (Hobbit) - S/N 9308000058" [H typewritten]; disks of …009, …044, …058 (software agent's manifest) |
| 15-16 Sep 1993 | the hardware documentation drafts | [S `letter.jpg`] |
| 1 Mar 1994, 23 Nov 1994 | the surviving kernels' build dates | software agent's manifest |
| July 1994 | EO shut down, then AT&T ended the Hobbit; software ran on the Hobbit machines until then | [H bebox.nu 1994]; "AT&T canceled the Hobbit processor line" [H Be Newsletter 1-3, Horowitz, 20 Dec 1995] |
| 1994 | transition machine: PowerPC add-in cards in a Hobbit box ("2 PPCs, 2 Hobbits, 3 DSPs"), designed by Glenn Adler | [H bebox.nu 1994]; #58 holds `/binp` and `/systemp` PowerPC files [H typewritten] |
| 3 Oct 1995 | dual PowerPC 603 BeBox (Joe Palmer) shown | [H Be Newsletter 1-3; bebox.nu] |

Other dating evidence:

- About 30 Hobbit machines were hand-built in Sakoman's garage [H, bebox.nu
  as relayed by a 2007 blog; not seen first-hand].
- The serial format 9308xxxxxx suggests August 1993 [G].
- Steve Horowitz: "dual-Hobbit … with three DSP chips on the motherboard",
  "proprietary" bus, and "memory, hard disks, mice, and keyboards were all
  borrowed" [H Be Newsletter 1-3].
- bebox.nu (1997 page "why ppc"): each of the five AT&T chips cost about $35
  [H].

## 17. Open questions for the model

1. The **boot ROM** is lost, so a model must provide its contract. The
   emulator's version [E]:
   - load `/system/kernel` from the boot volume;
   - store the RAM size at 0x08000048;
   - start CPU 1 at the ELF entry with the PSW on the stack.
   
   The CPU state at entry, the vector base and the ROM's own use of the
   flash and NVRAM need the software agent's work.
2. The **floppy-DMA register layout** (§8) is emulator-only. Disassemble
   `sako/flopdma.c` the way §6 did `_ser_init`.
3. The **DSP side**: the DSP3210 Information Manual, and how a CPU interrupts
   a DSP.
4. The **slot cards**: Ethernet chip, telephone card, audio card. The kernel
   names `ether_regs`, `phone_regs` and `audio_regs`, with no part numbers.
5. The **Hobbit interrupt pins**: the draft never says which board line goes
   to which Hobbit interrupt input. Levels 1/3/5/6 are from the kernel's
   handlers.

## Sources

1. **Be machine hardware documentation**, interim drafts dated 9/15/93 and
   9/16/93. Paula Butler and Ctein to Dan Dahle, Be Labs, 16 Sep 1993.
   Marked "CONFIDENTIAL : Be Labs, Inc."; paraphrased here, with only short
   phrases quoted.
   - 176 JPEG page scans plus `letter.jpg`, `intro1.jpg` and `intro2.jpg`,
     from fsck.technology, "BeOS Hobbit Prototype Release/Documentation
     (Loose Files)".
   - Held out of git. The manifest, `fetch.sh` and SHA-256 sums are in
     `hobbit/docs/bebox/` on branch `worktree-agent-aeb73561b39e2ec97`
     (commit 8315ce07), which fetches them to `hobbit/build/bebox/docscans/`.
   - Read here from the page images; OCR (tesseract) only for search.
2. **Surviving kernels**, extracted by the software agent from the disk
   images (`hobbit/build/bebox/kernels/`; same manifest):
   - `hobbit-9308000058.kernel`, built 23 Nov 1994: sha256
     `450716b22c33ed105684cdbe660b73e1843f2308b66fa76f2a153be112167b0b`;
   - `Hobbit-9308000044.kernel`, built 1 Mar 1994: sha256
     `1c91a68995d6bb6e0fed7dc36d0141d83deb0b6bd258c5dfb76112c8b7f57aaf`.
   
   Both are big-endian ELF, machine 0x39D, with symbol tables. The source-file
   names (`sako/*.c`, `isa/*.c`, `hob/*.c`) are in the kernels' strings. The
   [K] reads are reproducible with three read-only tools in this repository:

   ```
   python3 -I tools/bebox_kphys.py KERNEL phram rom io ether_regs audio_regs
   python3 -I tools/bebox_ksyms.py KERNEL _ser_init _reg_base _cpu_masks
   python3 -I tools/bebox_kdis.py asm KERNEL _ser_init _start_cpu _get_cpu_id
   ```

   `bebox_kdis.py` runs `asm/hobbit_asm.py` `disassemble_parcels` on a
   symbol's bytes and names call targets and data addresses.
3. **Photographs** (held out of git: `docs/bebox_photos/MANIFEST.md`):
   - Colin M. Strickland's Flickr album "Original BeBox", 17 Jun 2011
     (S/N 9308000017, Rev. A);
   - Fumihiko Shibata, *BeBox GuideBook*, photos 5-8 with captions, as
     posted to the Haiku forum,
     <https://discuss.haiku-os.org/t/original-bebox-introduction-at-agenda-96/9512/8>.
4. **johnrash/bebox** emulator (MIT), <https://github.com/johnrash/bebox>,
   commit `938296b`: `design/hardware.md` "The Hobbit prototype",
   `src/core/hobbit/HobbitBoard.h`, `HobbitMachine.{h,cpp}`,
   `HobbitVideo.h`, `Ncr53c94.h`.
5. **typewritten.org**, "BeBox Rev. A (Hobbit) - S/N 9308000058", 24 Feb
   2013, <https://typewritten.org/Projects/Be/9308000058.html>.
6. **Data sheets** (held out of git: `docs/devices/MANIFEST.md`):
   - VLSI 1990 *Computer Products* (VL82C106, VL16C452);
   - Motorola MCS3201 (1991);
   - AMD Am53C94 (Pub. 16506 Rev. C);
   - NCR 53C94 (Feb 1990).
7. **History:**
   - Be Newsletter 1-3, Steve Horowitz, "'Our' Toy Story", 20 Dec 1995,
     <https://www.haiku-os.org/legacy-docs/benewsletter/Issue1-3.html>;
   - bebox.nu history pages 1990, 1992-93, 1994 and "why ppc", via the
     Wayback Machine (2003-2004 captures of
     `http://www.bebox.nu/history.php?s=history/…`);
   - r/beos "BeBox Hobbit prototypes" (Jan 2024), Wayback capture
     20250706003118;
   - OSNews, "Planets Align: Rare Hobbit BeBox Offered and Sold", 28 Jan 2009,
     <https://www.osnews.com/story/20869/>;
   - Wikipedia "BeBox", for its error only.
8. **MAME**: `src/mame/be/bebox.cpp`, `bebox_m.cpp`, `bebox.h` at
   `dfc4d33d47030cb35ae6cbbc5c2a8a9a214383fd`.

**Searched, nothing at chip level.**

- Computer History Museum catalogue: only PowerPC BeBoxes (102657397,
  X1480.97).
- comp.sys.be and Usenet via web search: only the 1996 FAQ.
- The Joe Palmer interview (bebox.nu `news.php?lookat=65` and
  `history/joepalmerinterview`): the Wayback capture of the latter is empty.
- The Osaka 2001 BeOS Symposium (Sakoman lecture) slides were not reached.
- AT&T DSP3210 Information Manual: not on bitsavers (`components/att/dsp/`
  has DSP16 and DSP32C only) and not found by web search.
- The 9201x companion chips: not used on this board (§6).
- The eBay listing behind the OSNews 2009 story and a classiccmp post about
  a Hobbit purchase: not reached (HTTP 403).
