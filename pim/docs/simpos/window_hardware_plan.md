# The SIMPOS windowing environment in hardware: Bluespec, Bluesim, ULX3S (plan, 2026-11-25)

The owner asked, after reading `window_environment_plan.md`, to "add a plan to actually implement
this in hardware, simulation and the ulx3s". This page is that plan. H0-H3 are built (in Bluesim
and through synthesis; the status follows §6's table); H4 onward is not. Section 5's first numbers
come from one throwaway synthesis run in a scratch directory (Appendix A); H3's are the BSV
design's own (§5.1). **No board was touched:** no `openFPGALoader`, no serial port, no card.

It builds on these pages and does not repeat them:
- `window_environment_plan.md`, the software plan: its §1 display facts, §4 architecture and
  milestones M0-M11, written "S§n" and "Mn" below;
- `subsystems/window.md` ("W§n");
- `boot_route.md`;
- `../../psi/README.md`;
- `../../bsv/README.md`: the FEP emulator on the ULX3S, its synthesis numbers, the board steps;
- `../environment_audit.md` area G and `../pimos_roadmap.md` §9 (rungs P0-P5).

**Grades.** As S§0:
- PRINTED, PROSE, SCREENSHOT, USAGE and INFERENCE are the source grades. READ is
  `../psi_microword.md`'s label for "printed in the thesis", read on a page image; it counts as
  PRINTED or PROSE.
- "computed" is arithmetic done here on sourced or MEASURED numbers. "repo" points at a file in
  this repository that states the fact.
- **CHECK** marks a standard figure written from memory and not sourced in this session. Examples
  are the CEA-861/VESA DMT porch and sync numbers, the `ODDRX2F` alternative and 18 Kbit per
  DP16KD. Each must be checked against its standard or the Lattice datasheet (FPGA-DS-02012)
  before a test pins it.
- OURS marks a choice made here.
- MEASURED marks a number produced in this session by a command given in Appendix A.

**The accuracy rule.** `../../plan.md` sets the PIM/m rule: no structure invented or reordered for
FPGA convenience. The PSI display hardware is not documented beyond the facts in §1.1, so every
module below is **OURS scaffolding**, labelled as such in its file header. It is the hardware
counterpart of the software plan's Python device layer, not a reconstruction of the PSI's display
controller. Two structural facts are sourced:
- the bitmap display was a Multibus device;
- the keyboard and mouse hung off the console processor (TM-153 PDF p23, PRINTED figure; S§1.1-1.2).

---

## 0. The plan in one page

**What becomes RTL** (all OURS, as idiomatic Bluespec "boxes" with request/response interfaces,
the pattern of `../../bsv/Pimm*Box.bsv`):
1. `mkWinFbBox`: the framebuffer and the drawing primitives of S§4.1 (fill, line, glyph, copy,
   save/restore). The **same command set** as the Python device layer, so a command stream can be
   replayed into both and the two framebuffers compared byte for byte, as `pimm.py` and the PIM/m
   core are compared in lockstep.
2. `mkWinScanOut`: video timing, the 1-bit pixel fetch, a cursor overlay, TMDS encoding and a
   serializer onto the ULX3S's GPDI (HDMI-connector) DVI output.
3. `mkWinInputBox`: the keyboard and mouse front end. It plays the console processor's part and
   delivers the software plan's event records (S§4.3).
4. `mkWinLink`: a UART link to the host carrying drawing commands down and events up.

**The PSI CPU is the PIM/m PU** (§1.3). The PSI-III and the PIM/m PE are one chip, whose PU "has
capability to execute ... KL1 for PIM/m and ESP for the AI workstation" (TM-862, PROSE). Its
decode table carried KL0 and KL1 entries side by side (Nakashima thesis p.125, READ). So the CPU
route is our own PU, made to run KL0. Two routes are open:
- **(c2), first:** a KL0 front end on the Bluespec core, sharing its boxes, in lockstep with
  `psi/kl0.py`, as `pimm.py` checks the core today.
- **(c1), the fidelity target:** `PimPU`'s writable control store running the held PSI-III
  microcode `syspsi`/`sysidat`. Its field layout is read; many field values are still open.

Until (c2) runs, the CPU stays on the host: option (a). kl0/espc runs the held code and the
stand-ins on the Mac, and the board is the display and the keyboard. A soft RISC-V CPU running a
kl0 port, option (b), is dropped.

The consequence: one PU design serves as both a PIM/m PE and a PSI-III workstation CPU. That gives
SIMPOS → FEP (SCSI) → PIMOS with both ends on our hardware (§1.3; fit unmeasured).

**The display.**
- The logical frame is 1,280×944 plus a status band: 1,280×984 with the status band at the default
  S = 40, held in a 1,280×1,024 one-bit buffer.
- Native 1280×1024@60 (108 MHz pixel, 1,080 Mbit/s per lane) is **out of reach** on the ECP5 as
  built here. `ecppll` refuses a 540 MHz output ("not in range (10MHz, 400MHz)", MEASURED), and the
  skeleton's shift clock routes at 426 MHz against the 542 MHz needed (MEASURED).
- **First choice: 1920×1080@30 with the 1,280×1,024 frame letterboxed 1:1**, at 74 MHz pixel and a
  370 MHz shift clock. It closes timing on three seeds (MEASURED).
- **Second: 1280×1024 at 49 Hz with reduced blanking** (75 MHz, OURS timing). It also closes, but
  whether a monitor accepts it is unknown.
- Fallbacks: 1280×720@60 with a vertical pan; 640×480 with a 2:1 reduction, the only mode proven on
  this board (by the sibling `flute-lx50` project).

**The framebuffer in block RAM** costs **80 of the 85F's 208 DP16KD** (38%, MEASURED). The whole
display skeleton is 1,373 TRELLIS_COMB and 375 FF, about 1.6% of 83,640 (MEASURED). Window save
areas, colour, and the PIM/m core's store go to the 32 MB SDRAM.

**Input.**
- First, events from the host over the link: the same replayable event script as the software
  plan, and the browser canvas of M11.
- Then a PS/2 keyboard on US2 through a USB-OTG/PS-2 adapter, which the ULX3S manual names.
- Then a USB-HID host core for the mouse.
- The 16-bit JIS mapping and the `pf#`/`key#` names are a table (OURS): the numeric codes are not
  held (W gap G2).

**Simulation.** Bluesim benches dump the framebuffer as PBM P4, whose bit packing is the PSI's own
(MSB leftmost, 1 = a black dot). They compare it with the Python layer's dump byte for byte. They
check video timing and TMDS by decoding the serial stream back to pixels. Each check has a named
fault injection. A new `bsv/run_win_tb.sh` joins `../../run_tests.sh`.

**Milestones H0-H13** (§6): framebuffer box and PBM lockstep, glyphs, scan-out in sim, synthesis
fit, board scan-out (the owner runs it), input, the host link, the Login PIMOS screen on a monitor;
then save areas in SDRAM and colour. In parallel: KL0 on our PU (c2: H11a-c), the microcoded PU
(c1: H12), and SIMPOS → FEP → PIMOS on one board (H13).

**What the owner supplies** (§7): a monitor that takes 1080p30 over HDMI, a PS/2-capable USB
keyboard with an OTG adapter, a USB mouse, and board time, since the ULX3S is running Linux Flute
for another session.

---

## 1. What the hardware replaces

### 1.1 The PSI as built, and what is known of it

| fact | grade | cite |
|---|---|---|
| The bitmap display is a Multibus (IEEE-796) device; keyboard and mouse are on the console processor's bus | PRINTED (handwritten figure) | TM-153 PDF p23 (S§1.1, S§1.2) |
| Only the window manager touches bitmap memory (SIMPOS 1.0) | PROSE | TM-115 (W§2.5, S§1.5) |
| Frame memory is shown; each hidden window has a save area in bitmap memory "several to several tens of times" the frame memory; restacking copies between them | PROSE (TRANSLATION) | TM-225 p10 (S§1.1) |
| No KL0 instruction draws; the bulk-bit primitives are string ops; `physical_word/3`, `special_function/2`, `bus_reset` exist | MEASURED negative finding | S§1.5 |
| So the window manager drove a display controller over the I/O bus, with the rasterop there or in microcode | **INFERENCE** | S§1.5 |
| On the PSI/UX an external "SIMPOS window server" drew the SIMPOS screen; window control, mouse and keyboard stayed in SIMPOS | PROSE | Giho 65(6) 1991 PDF p86; IPSJ SIG-ARC 24478 (S§0) |

The software plan's device layer copies the PSI/UX split. SIMPOS (stand-ins in ESP) decides what to
draw; a server below a narrow primitive set draws it. The hardware plan keeps that split and moves
the server into RTL.

### 1.2 Which pieces become RTL

| piece | in the PSI | here | grade |
|---|---|---|---|
| Framebuffer and bitmap memory | display controller on Multibus (INFERENCE) | `mkWinFbBox` over block RAM (frame) and SDRAM (save areas) | OURS |
| Rasterop / drawing | controller or microcode (INFERENCE) | `mkWinFbBox` primitives = S§4.1's `fb_fill`, `fb_line`, `fb_glyph`, `fb_copy`, `fb_save`/`fb_restore`; since 2026-11-26 also `read` and `target` (§2.4's extension: drawing on areas of bitmap memory) | OURS |
| Scan-out | CRT controller (not documented) | `mkWinScanOut`: timing, fetch, cursor, TMDS, serializer | OURS |
| Keyboard and mouse | console processor (PRINTED figure) | `mkWinInputBox`: PS/2 or USB-HID front ends to event records | OURS |
| Window manager, classes, coordinator | SIMPOS software on the PSI CPU | **unchanged**: the ESP stand-ins on kl0 | — |
| The PSI CPU (KL0) | PSI-II / PSI-III hardware | host kl0 (option (a)); then our PIM/m PU running KL0 (routes (c2), (c1)) | §1.3 |

**The interface is the contract.** The box's request type is the S§4.1 primitive set, one
constructor per primitive, with the same arguments. The Python device layer (planned at M5, not
yet written: no `fb_` or framebuffer code exists in `../../psi/` as of 7042cdbb) must read and
write the same command records.

The plan fixes one rule: **the Python reference is written first** (M5 or H0, whichever lands
first), as a module that both the `SIMPOS_MODELS` hook and the bench script import. Its command
format is then frozen for the RTL. This is the `pimm.py`-vs-core pattern: the reference defines
behaviour, and the RTL is checked against it.

### 1.3 The PSI CPU: the PSI-III is the PIM/m PU

**The fact this section is built on.** The PSI-III (the PSI/UX's CPU) and the PIM/m processing
element are **one chip**:
- TM-862: "The microprocessor, called PU (Processing Unit), is also used as a key component of AI
  workstations. Thus, PU has capability to execute two different type logic programming languages,
  KL1 for PIM/m and ESP for the AI workstation" (PROSE; `../environment_audit.md` area G, via
  `../psi_acquisition.md` §3).
- `M92` p. 426 agrees: PIM/m's PE CPU is the PSI/UX (PSI-III) CPU (PROSE; `../environment_audit.md`
  area L).
- Nakashima's thesis prints the mechanism (READ, `../psi_microword.md` §3a, thesis p.125). The
  PSI-III decode table holds 512 entries for 1,024 opcode kinds, "KL0 0-511, KL1 512-1023". It is
  a cache with a KL0/KL1 flag per entry; a mismatch traps to a microprogram that reloads the entry.
  This was "used for pseudo-PIM (KL0 and KL1 on one PSI-III)".
- The thesis also says PSI-II/III machines served as a debugging bench, running "pseudo PIM"
  with KL0 and KL1 together (p.146, READ, same file §3c). The held Pseudo PIM/m file
  `pimm.MEkbn` carries both languages. Its image 1 (22,528 addresses) "is identical to `syspsi`
  `0..57ff`, the KL0 side", and its image 2 is the KL1 microprogram (MEASURED by a delegated run,
  `binary_reverse_engineering.md` §3; `../environment_audit.md` area G). So the held firmware for
  KL0 and KL1 on one PSI-III exists, as two images.

**So the "PSI CPU" question is not a new machine.** It is the PIM/m PU we are already building,
made to run KL0/ESP as well as KL1.

**What the repo has.** Two hardware lines and one reference:
- `bsv/PimPU.bsv` has the documented PU structure: D, A, R, S, E; the 32K×64 writable control
  store; the decode RAM; the tag-jump table (`M92` pp.426-428). But it runs a **diagnostic
  microcode of our own** (`asm/pimasm.py`), not the held microword (its header;
  `../environment_audit.md` rows on the pipeline and the WCS).
- `bsv/PimmCore.bsv` (`mkPimmCore` and its `Pimm*Box`es) runs **KL1-B at the instruction level**,
  not from microcode. It is checked in lockstep against `ref/pimm/pimm.py`, and it is "sequential,
  'no timing claimed'" (`../environment_audit.md` pipeline row; `../../bsv/README.md`).
- `psi/kl0.py` executes the held `.ptf` code. Its terms are Python objects (`Var` with a `ref`;
  the choice-point height `Barrier.b` is an "OURS representation", `kl0.py`), not machine cells.

**The routes** (option (a) concerns the display and is unchanged):

| route | what | sources it stands on | state | for | against |
|---|---|---|---|---|---|
| **(a) host kl0 + display/input on the FPGA** | kl0 on the Mac; `SIMPOS_MODELS`' `bitmap_display` entries send primitives over the UART | S§4.1; the PSI/UX window-server split (PROSE) | ready to build | needs no CPU; lockstep with the Python layer is free | the CPU is not hardware; link bandwidth (§3.4) |
| **(c1) microcode: the PU runs the held PSI-III control store** | `PimPU`'s WCS loaded with `syspsi`, with the decode table `sysidat` and `sysinit`; the datapath built to the microword, so the held KL0 firmware executes KL0 | Fig. 3-25 field layout (READ), which the held stores fit (MEASURED, `../psi_microword.md` §4, §7; `asm/mekbn.py --check`); `sysidat` start addresses land 471 of 471 (MEASURED, same §4.4); TR-733 fig. 4 for PIM/m (READ); `rassy` value tables (`binary_reverse_engineering.md` §3) | **partly decoded**: the layout is read, but these remain open (`../psi_microword.md` §7 "Still open"): CCF's coding, MCF, TGIF 3, AS1F 2/3, AS2F values, JMPF 2 and bit 26, ALF 2 vs 3, EM2 operations. The decode-entry packing is open (§4.4). `sysinit` is "not characterised". That `syspsi` holds KL0 is "probable, not settled" (`../environment_audit.md` area G). The PSI-III tag and word format are "NOT FOUND in the thesis" (`../psi_microword.md` §3b). The I/O bus and timer are outside the PU (thesis p.130) | **the real machine**: the held firmware defines KL0, so nothing is interpolated at the instruction level; the same work gives a cycle-level PIM/m PU (rungs P1/P2 are "one piece of work" with it, `../environment_audit.md` area G); then `pimm.MEkbn` (Pseudo PIM/m) runs on it too | reverse engineering, "not transcription" (`../psi_acquisition.md` §8); every open field must be settled by measurement against the held words; long |
| **(c2) instruction level: a KL0 front end on our core** | a KL0 decode-and-execute front end added to the Bluespec core, reusing its boxes; checked in lockstep against `psi/kl0.py`, as `pimm.py` checks the core today | KL0 opcodes from `psi/kl0_opcodes.tsv` (each row with a known-plaintext witness, `../../psi/README.md`); the instruction format as `psi/kl0.py` decodes it from the held code (`kl0_opcodes.tsv`'s class and opcode columns; the PSI-II word `001111 \| class(2) \| code(8) \| operand(24)` of TR-265, READ, area G, is lineage only); `sysidat` "covers every opcode the six `.ptf` files use" (`../environment_audit.md` area G); the ESP object layout of Fig. A-1 (thesis App. A, READ) | not started. kl0 runs the FEP census: 829 success, 235 failure, 385 refused, with recipes (S§2.1). The boxes it could share exist and are tested: unify/deref `PimmDBox`; hashing `PimmHBox`, which ESP's method and slot tables need (Fig. A-1); strings `PimmSBox`, which KL0's bulk `and_`/`or_`/`xor_`/`copy_string_elements` need (S§1.5); timer `PimmTBox`; SCSI `PimmScsiBox`. The diagnostic KL1-B bench has a choice-point stack (`PimKL1BCpTb`, `../../bsv/README.md`) (INFERENCE: these are the boxes that fit) | **fast and checkable**: the oracle exists and is the same program the display runs on, so a lockstep failure points at one instruction; it puts SIMPOS-side code on our hardware soonest | an instruction-level model, like `mkPimmCore`: no timing claimed, not the PSI's mechanism (the PSI ran KL0 from microcode); new state KL1-B lacks (KL0's backtracking, trail, local and global stacks, cut, ESP objects); kl0.py has no cell format, so a cell encoding must be chosen (OURS) and the lockstep compared at the level of instructions and dereferenced register values, not memory cells, until kl0 gains one |
| (b) a soft RISC-V CPU running a port of kl0 | e.g. the sibling flute-lx50 core | — | **dropped**: (c2) gives the same standalone result on the right machine | stands alone | a second kl0 to keep in step, on a CPU that is not the PSI |

**Recommended staging (changed by this fact):**
1. **Display: (a)**, host kl0 over the link, H0-H9. The display boxes never depend on which CPU
   produces the command stream.
2. **CPU: (c2) first, as the main route**, in Bluesim, in parallel with the display work
   (H11a-H11c). It is a front end on the core the project already verifies. Its oracle, kl0.py, is
   the program the display plan already runs, and each step is a lockstep test. It replaces the
   host in (a) one class of programs at a time: first the boot route, then Login PIMOS.
3. **(c1) as the fidelity route** (H12), joined to rungs P1/P2. Each microword field settled in
   `asm/mekbn.py` turns into PU datapath. (c2)'s lockstep traces then become (c1)'s oracle at the
   instruction boundary: the same held `.ptf` run, two ways.

(c1) is the target the accuracy rule points at. (c2) is labelled scaffolding, as `mkPimmCore` is
today.

**The consequence: one PU design, both ends of the installation.** If one Bluespec PU runs KL1-B
(the PIM/m PE) and KL0/ESP (the PSI-III), two instances on the ULX3S are the real topology. The
thesis gives it: "FEP is a PSI-II/PSI-III", the PIM/m FEP link is "via SCSI" (p.146, READ,
`../psi_microword.md` §3c). On the board that is:
- **SIMPOS stand-ins and held `pimfep` on a PU in KL0 mode** → **SCSI** (`PimmScsiBox`) →
  **PIMOS on a PU in KL1 mode**;
- the display and input boxes hang off the KL0 PU, as the bitmap display and console processor
  hung off the PSI (TM-153 p23).

A single PU switching modes through the decode-table KL0/KL1 flag, as Pseudo PIM/m did (thesis
p.125), is the smaller variant.

Either way the held FEP half (`pimfep`) replaces `mkPimmFepEmu`. That is rung P5 of
`../pimos_roadmap.md` §9, "the held `pimfep.ptf` serves the PIM/m model's SCSI link in place of
`fep.py`", reached on hardware.

**Whether this fits is unmeasured.** `mkPimmCore` has never been synthesized (§1.4). Two cores'
block RAM is certainly beyond the 85F (§5.1), so their stores must go to the SDRAM. The 16 Mw per
PE of the real machine (thesis p.146) and the PSI-III's "up to 64 Mw" (p.123) are far beyond 32 MB
in any case: the board runs scaled-down memories, labelled as such.

### 1.4 Login PIMOS → FEP → PIMOS on one board?

**Not today**, and not with option (a) alone. Each part of the chain stands as follows:

| part | where it runs | hardware state | cite |
|---|---|---|---|
| Login PIMOS (held `pimfep` ESP: `as_pimos_login_requester`, menus, `getl`) | kl0 | host only. It needs a KL0 CPU, so (a) keeps it on the host and only (c) brings it onto the board | boot_route §5; S§4.4 |
| The FEP's answers to PIMOS (window commands 104, 127, 130, 132, 141-143, 111, 112; files; timer) | `ref/pimm/fep.py`, and `mkPimmFepEmu` in BSV | the emulator synthesizes (14,816 LUT4, 4,259 FF, 3 DP16KD, 35.03 MHz, PASS at 25 MHz) and is checked against `fep.py` on 9 tapes; **no board has run it**; nothing on its board top calls `idle` | `../../bsv/README.md` "The FEP emulator on the ULX3S" |
| PIMOS (KL1-B) on the PIM/m core `mkPimmCore` | Bluesim | **never synthesized** (no figure in the repo); its memory is a 2^27-cell model (`PimmMem.bsv`, `asm/pimm_layout.py`) that must map onto the 32 MB SDRAM; the SCSI adapter between core and emulator is specified but not written; the older bench top `PimUlx3s` is "not hardware-ready" (WP2) | `../../bsv/README.md` "FPGA flow", "The adapter to the core"; `../../plan.md` WP2 |

**What can run on one board without KL0.** PIMOS's own console reaches the screen through the FEP,
not through SIMPOS: 104 create, 127 reshape `(200,200,47,14)`, 130 title `"PIMOS CONSOLE"`, 132
font `"font:test_11.font"`, 143 show, then 111 putb `"Shell>> "` (S§4.4 item 3;
`../fep_services.md` §7.3).

`mkPimmFepEmu` already answers these commands. A thin rule module could turn their arguments into
`mkWinFbBox` commands:
- 104: a window record;
- 127 and 143: a border and a clear;
- 130: the label;
- 111: glyphs.

It would draw the 47×14 test_11 console with no KL0 at all. That is an **OURS path**: it does what
`fep.py` does in place of the held `pimfep` + `pmacs_window`. On screen it must be labelled as the
FEP stand-in's console, not SIMPOS's.

So the first single-board picture, when the core is hardware-ready, is **PIMOS → FEP emulator →
display**. The full chain Login PIMOS → FEP → PIMOS on one board needs the PU to run KL0 (route
(c2) or (c1), §1.3).

---

## 2. The display hardware

### 2.1 Resolution

| source | value | grade |
|---|---|---|
| MELCOM PSI (1986) | 1,280×960 | PROSE (Giho 60(9) PDF p13; S§1.1) |
| PSI/UX (1991) | Unix side 1,280×1,024, 256 colours; the SIMPOS screen one X window "equivalent to the PSI-II display screen" | PRINTED table + PROSE (Giho 65(6) PDF p86, p88; S§1.1) |
| SIMPOS 5.0 / PIMOS front ends | drawing area 1280×944 | PROSE TM-785; USAGE kl1graph (S§1.1) |
| Oki PSI-II | 1,600 wide | USAGE disc `exdisp.esp` (W§2.13) |
| Mitsubishi PSI-II physical size | **not held** (S§6 Q1) | — |

**Choice (OURS, following S§1.1's INFERENCE):** a 1,280-wide, one-bit frame of 944 + S lines.
- With S = 40 the frame is 1,280×984 (INFERENCE). S = 40 is two lines at test_11's line height
  `0x14` = 20, a header field that S§1.4 itself labels "line height?". It is S§1.1's "two lines of the status font", with test_11 standing in for the
  status font, which is not held.
- The buffer is **1,280×1,024**, for three reasons:
  - it is a power-friendly 80 words × 1,024 rows;
  - it holds MELCOM's 960 and the PSI/UX's 1,024;
  - it leaves 40 spare lines for a taller status band.
- The width and height are BSV parameters. The 1,600-wide Oki variant is the same design with
  100 words per row and 1,600×1,024 = 1,638,400 bits = 100 DP16KD (computed).

### 2.2 Pixel clock and the GPDI output

The ULX3S GPDI connector carries four differential pairs:
- blue `gpdi_dp[0]` A16 / `gpdi_dn[0]` B16;
- green A14 / C14;
- red A12 / A13;
- clock A17 / B18.

Source: prjtrellis `examples/ulx3s/ulx3s_v20.lpf` lines 298-306, in the local toolchain checkout
(`~/src/ulx3s-experiments/bluespec-ulx3s/toolchain/prjtrellis/`). The sibling `flute-lx50`
constraints drive only the `_dp` pins as `IO_TYPE=LVCMOS33D`, which "drives each gpdi_dp pin and
its paired _dn pin ... as the complement" (`flute-lx50/constraints/ulx3s_85f.lpf` lines 74-83).

The pins are ordinary I/O, not SERDES. A 10:1 TMDS serializer is built from `ODDRX1F` (2 bits per
clock) at 5× the pixel clock, or `ODDRX2F` at 2.5× with an edge clock (CHECK). ULX3S MANUAL.md (fetched
2026-11-25) says only "4 TMDS+- video out differential pairs", 220 nF (later 22 nF) coupling, and
mentions 800×600 and 1024×768 (for their WiFi interference). It states no maximum.

| mode | pixel clock | TMDS lane rate | ODDRX1F shift clock | status | grade |
|---|---|---|---|---|---|
| 640×480@60 | 25 MHz | 250 Mbit/s | 125 MHz | **runs on this board model**: flute-lx50's DVI, `ODDRX1F`, its README ("HDMI output") says the old shared-phase serializer routed at 122 MHz against the 125 MHz shift clock, and lx49's per-lane load flags fixed it; no post-fix figure is given | sibling project's record, not re-run here |
| 1280×1024@60 VESA DMT (htotal 1688, vtotal 1066: CHECK) | 108 MHz | 1,080 Mbit/s | 540 MHz | `ecppll -i 25 -o 540`: "Warning: Output frequency 540MHz not in range (10MHz, 400MHz)"; skeleton sclk **426.26 MHz FAIL at 541.71**, pclk 88.21 FAIL at 108.34 | MEASURED (Appendix A) |
| 1280×1024 CVT-RB-like @60 | ≈91 MHz | ≈910 Mbit/s | ≈455 MHz | over the 400 MHz PLL limit `ecppll` enforces | computed |
| **1920×1080@30 (CEA-861 VIC 34 timing, htotal 2200, vtotal 1125: CHECK), 1,280×1,024 letterboxed 1:1 at (320,28)** | 74.25 nominal; **74 MHz** from the PLL (29.9 Hz) | 740 Mbit/s | 370 MHz | skeleton **closes**: sclk 399.52 / 429.37 / 391.85 MHz, pclk 87.93 / 98.31 / 95.63 MHz on seeds 1/2/3 | MEASURED |
| **1280×1024 reduced blanking (OURS: htotal 1440, vtotal 1054)** | 75 MHz → 49.4 Hz | 750 Mbit/s | 375 MHz | skeleton **closes**: sclk 420.88, pclk 94.87 (seed 1) | MEASURED; monitor acceptance unknown |
| 1280×720@60 (CEA) | 74.25 MHz | 742.5 Mbit/s | 371.25 MHz | same clocks as the 1080p30 row; shows 720 of the 984 lines, so needs a vertical pan (a register) | computed; OURS |
| 1024×768@60 VESA | 65 MHz | 650 Mbit/s | 325 MHz | 1,024 of 1,280 columns: pan both ways, or reduce | computed; OURS |

**Caveat on "closes".** "Closes" means each clock's own Fmax passes. nextpnr checks the fabric
registers that feed the `ODDRX1F`s. It does not check:
- the I/O buffer's toggle rate at 740 Mbit/s on LVCMOS33D;
- signal quality through the coupling capacitors;
- the pclk → sclk word transfer. That transfer is reported as a 1.24-1.29 ns cross-domain delay,
  MEASURED, but not checked against the clocks' phase relation (§5.2).
- What is proven on this board model is 250 Mbit/s.
- That ECP5 boards commonly run 720p or 1080p30 DVI this way is a community lead, not verified this
  session (one web search found nothing specific; the Lattice datasheet FPGA-DS-02012 was not
  opened).
- The I/O limits and the PLL output limit must be checked against that datasheet before H4. Until
  then the 400 MHz figure is `ecppll`'s, and the rest is INFERENCE.

**Recommendation (OURS):**
- **Bring-up (H4a)**: 640×480, the proven mode, showing the frame reduced 2:1. A 2×2 OR keeps
  one-dot lines visible; the original screen is not shown at its real resolution.
- **Working mode (H4b)**: 1920×1080@30 letterbox. It is the whole 1,280×1,024 frame at 1:1, with
  no scaling, and the skeleton closes timing on three seeds.
- **Native option (H4c)**: 1280×1024 at 49 Hz with reduced blanking, if the owner's monitor takes
  it.
- **Fallback**: 1280×720@60 with a pan register, for a monitor that takes neither.

All modes are one timing table in `mkWinScanOut`, chosen by a parameter.

### 2.3 The one-bit framebuffer: block RAM versus SDRAM

| quantity | value | grade |
|---|---|---|
| 1,280×1,024×1 | 1,310,720 bits = 81,920 16-bit words | computed |
| ECP5 LFE5U-85F block RAM | **208 DP16KD** (18 Kbit each, CHECK; used here as 1,024×16 = 16 Kbit) | MEASURED (nextpnr utilisation report, "DP16KD: 80/ 208") |
| framebuffer in DP16KD | **80 blocks, 38%** | MEASURED |
| logic of the 85F | 83,640 TRELLIS_COMB / 83,640 TRELLIS_FF; 4 EHXPLLL; 56 DCCA | MEASURED (same report) |
| the board's part | `--85k --package CABGA381 --speed 6`, the repo's target (`../../bsv/run_fepemu_fpga.sh`, `run_fpga_build.sh`) | USAGE (repo) |
| SDRAM | Winbond W9825G6KH-6, 32 MB, 16-bit (`../../bsv/ulx3s_85f.lpf` line 38); a BSV controller exists (`../../bsv/Sdram_Controller.bsv`, 256-bit requests as two BL8 bursts at 25 MHz; `PimSdramStore.bsv`, Bluesim bench `run_sdram_tb.sh`) | repo |

**Frame memory in block RAM (OURS).** DP16KD is true dual-port with independent clocks:
- port A in the system domain, for drawing;
- port B in the pixel domain, for scan-out.

So the clock-domain crossing is the RAM itself, and drawing never waits on the display.

The scan-out reads one 16-bit word per 16 pixels: 4.6 M words/s at 74 MHz, which is trivial. The
skeleton's lesson (MEASURED) is that the RAM must be **banked by hand**: 80 banks, one per DP16KD,
with a registered 8:1 then 10:1 output mux.
- Inferred as one 81,920-deep array, yosys built an unpipelined 80:1 mux, and the pixel clock
  failed at 64.99 MHz.
- Banked, it reached 87.93 MHz.

**Bitmap memory (save areas) in SDRAM.** TM-225 p10 puts the save areas at "several to several
tens of times" the frame memory. That is 1.6 MB to about 6.5 MB at 1.31 Mbit per screen, far
beyond block RAM.
- A first version (H0-H7) keeps save areas in the spare block RAM. 208 − 80 − font cache leaves
  about 120 DP16KD, roughly 1.5 screens. That is ample for the Login PIMOS window, the console and
  a menu.
- H8 moves them to SDRAM through `Sdram_Controller` behind the box's own request queue.

**The SDRAM is shared.** It is already the PIM/m local store in `PimUlx3s`/`PimSdramStore`.
- With option (a) and no core on the board, the display owns it.
- In a combined bitstream it is partitioned: for example, the top 8 MB for bitmap memory and the
  rest for the PIM/m store, behind one arbiter. Whether PIMOS fits in the remaining 24 MB is
  unmeasured (§1.4).
- A one-bit scan-out from SDRAM would need 1,280×1,024/8 × 30 Hz = 4.9 MB/s, so a frame buffer in
  SDRAM is possible if block RAM runs short. It is not the first choice, because drawing would
  then share the SDRAM's queue with the core.

### 2.4 The drawing engine (`mkWinFbBox`)

Request/response, one primitive per request, answered on completion. The operations come from
W§2.5:
- `set`, `reset`, `exclusive_or`;
- `copy` and `reverse` for transfers;
- fill patterns `fix`/`light_paint` as 16×16 tiles.

| primitive (S§4.1) | datapath | cycles (OURS estimate, 16-bit port, one word per cycle) |
|---|---|---|
| `fb_fill rect, op` | edge masks + word loop; read-modify-write only at the two edge words of each row | full-screen clear 80 × 984 = 78,720 words → **3.1 ms at 25 MHz** |
| `fb_line x1,y1,x2,y2,width,style,op` | Bresenham, one dot per read-modify-write (2 cycles); horizontal runs as fills | a 1,280-dot diagonal ≈ 2,560 cycles = 0.1 ms |
| `fb_glyph font, JIS, x, y, op` | glyph-cache lookup (code → record x, y, w, h, bias); per row: read ≤ 2 strip words, shift to x, read-modify-write ≤ 2 frame words | 11×14 test_11 glyph ≈ 14 × 4 + 8 = 64 cycles = **2.6 µs**; the 47×14 console (658 glyphs) ≈ 1.7 ms |
| `fb_copy src → dst, op` | barrel shifter (16-bit funnel), direction chosen for overlap; read + write per word | full-screen scroll ≈ 157,000 cycles = 6.3 ms |
| `fb_save` / `fb_restore id` | `fb_copy` between frame memory and bitmap memory (block RAM, later SDRAM) | as copy; SDRAM adds its burst latency |

All of these are far faster than the host link (§3.4), so the box is never the bottleneck in option
(a). A 32-bit organisation (DP16KD as 512×36) would halve them; this is left for later.

The engine is one box with sub-rules (fill, line, glyph, copy), per the idiomatic-Bluespec rule:
- the datapath lives in the box;
- off-path cases (overlapping copies, clipping) are separate rules.

**Clipping** is to the request's rectangle. The stand-in window manager already does window
clipping (S§4.1), so the box clips only to the screen.

**The 2026-11-26 extension (OURS, owner-approved).** The command set frozen in `psi/winfb.py` was
itself OURS. The owner approved extending it so that SIMPOS can read dots back
(`docs/simpos/m8_stops.md` §7). Its basis:
- TM-125 p17 (PRINTED-INTERFACE) gives `get_point_value/4`;
- TM-115 p82 (PROSE) says bitmap areas are loaded from and saved to strings.

The record format and every rule are OURS:

| prim | record | answer |
|---|---|---|
| `a` read | `a0 x y w h - -` | the rectangle of the SOURCE surface, cut as a fill is cut, as data words: ceil(w'/16) per row, row-major, dots from bit 15, the last word's pad dots 0; then the status OK. A cut rectangle with no dots answers no words. |
| `b` target | `b0 which kind base pitch w h` | sets a surface register: which 0 the destination, 1 the source; kind 0 the frame (the rest ignored), kind 1 an area of the 65,536-word bitmap memory, w × h dots, row j from bit 15 of word base + j × pitch. OK; BADOP if which > 1 or kind > 1; BADSURF (6), the register unchanged, if w = 0, h = 0, pitch = 0, pitch > 255, 16 × pitch < w or base + pitch × h > 65,536. |

- Prims 8, 9 and c–f stay reserved (BADOP), so the older streams' `0x90`/`0x93` records still mean
  what they meant.
- **Drawing targets (prim `b`, step 3 of `m8_stops.md` §7; basis TM-225 p10, PROSE: a hidden
  window's output writes its save area).** Both registers are the frame at reset.
  - fill, line and glyph draw on the destination surface; read and copy take dots from the source
    surface; copy goes from the source to the destination. Each clips to its surface's w × h as
    to the frame's 1,280 × 1,024 (right and bottom edges); an area's pad dots past w are never
    written.
  - A copy between two DIFFERENT areas (base or pitch unequal) whose word ranges
    [base, base + pitch × h) meet is BADSURF and draws nothing, whatever its rectangle. One area
    onto itself (equal base and pitch, w and h free) is allowed: the RTL's direction rule for an
    overlapping copy needs one coordinate system.
  - save, restore and dump always act on the frame, whatever the registers hold.
- **Contents (OURS):** bitmap memory is 0 at reset, as the frame is. `mkWinFbBox` clears it beside
  the frame (rule `initClearB`, 65,536 cycles inside the frame's 81,920), so reset takes no longer:
  the empty stream is 163,846 cycles before and after, MEASURED with `win_measure.sh`. The
  alternative, an area undefined until written, was not taken: the finished gen streams
  (`targets`, `rand_x2_*`) read areas and pad words they never wrote.
- The RTL computes each blit's first rows, base + row × pitch, in rule `blitSetup` a cycle after
  the command is taken (one cycle more a fill, copy, glyph, read, save and restore), and a line's
  start row in rule `lSetup`. The line engine no longer multiplies per dot: its row registers step
  by ±pitch (H3 had seen a variable multiply on a RAM address miss 25 MHz).
- `bsv/WinFbBox.bsv` answers it in lockstep with the reference, checked by `bsv/run_win_tb.sh` on
  the read streams. The words leave as a dump's frame words do.
- Open item: the host link does not carry them yet. Its TX (`bsv/WinLink.bsv` `sendData`) frames
  data as 64-word records and takes 64 answers without looking at `isData`. So a read whose word
  count is not a multiple of 64 would send its status, and later answers, as data words. This was
  found by reading the rule; no read has been run through the link.
- `bsv/WinFbBox.bsv` runs the targets in lockstep too: the gen streams `targets`, `rand_x2_1..3`
  and the directed `bsv/win_streams/targets_stall.txt` (under +stall), with injections T1-T4 in
  `bsv/run_win_tb.sh`'s header. No target record has been run through the host link
  (`bsv/WinLink.bsv`).

### 2.5 Fonts

`test_11.font` (and its five FONT.DIR siblings) are in the held `docs/nonlocal/psdpim.tar.Z`, which
is in git. Their f822 layout is decoded and MEASURED (S§1.4): 21 header words, 8-word records, one
glyph strip, MSB leftmost.

| font | words (from S§1.4's MEASURED headers) | DP16KD at 1,024×16 |
|---|---|---|
| test_11 | 21 + 128×8 + 14×88 = 2,277 | 3 |
| all six FONT.DIR fonts (test_11, test_11b, test_10, tiny_7, performance, csppestate) | 15,432 | 16 |

Computed from the header table; the file-length identity is S§1.4's MEASURED check.

**Loading path (OURS).**
1. The host extracts `psdpim/FONT.DIR` from the tracked archive with the S§1.4 recipe. The archive
   is held and in git; derived images are build products, not committed.
2. On H6's link, `font_load` sends the file's words into the glyph cache: 4,554 bytes for test_11,
   0.4 s at 115,200 baud or 0.05 s at 1 Mbaud.
3. For Bluesim, the same words go into a BRAM load file generated at bench time.
4. For a standalone board (later), the files go on the SD card next to the FEP's (`tools/mkfepcard.py`
   already places held files there) and are read through `mkPimmSdBlock`.

**Code lookup.** JIS X 0208 codes are sparse, so the cache keeps a 94×94 index for rows and columns 21-7E (8,836 entries × 8
bits ≈ 5 DP16KD, OURS) from code to record. The codes outside it are test_11's control codes 0-0x1f
and its 0xffff entry (S§1.4), 33 in all, which take a small direct table beside it. The box can
then take the JIS code itself, as `fb_glyph` does, and the command format stays the same on both
sides.

**A missing glyph draws S§1.4's "missing glyph" box**, so a gap is never silent.

### 2.6 The cursor

- The text cursor is a solid block (S§3). It is drawn in the frame by the stand-ins as an XOR fill,
  as in software.
- The mouse cursor is a small arrow (SCREENSHOT esp.wmv@120). Shape numbers come from
  `set_mouse_marker/2`, whose numbering is unknown (W§2.6).

**OURS:** the mouse cursor is a 16×16 hardware overlay in `mkWinScanOut`: two 16×16 bit planes
(mask, image), a position register, and up to 8 shapes in registers. It is never written into the
frame. This keeps the lockstep exact: the PBM dump is the frame, with no cursor. The Python layer's
renderer composites the cursor only in its views, and a separate test checks the composited output
of both sides.

### 2.7 Colour, later (PSI-II, PSI/UX)

What is held about colour:
- a window palette of colour pairs, where one pair is a monochrome window (Giho 8907 p34-35, PROSE;
  W§3.7);
- `get_plane_count` gives 1/3/4/6/8 on the PSI/UX (USAGE, S§1.1);
- the PSI/UX Unix side ran 256 colours (Giho 65(6) p88).

In hardware:
- An 8-plane 1,280×1,024 frame is 10.5 Mbit, and even 4 planes (5.2 Mbit) exceed the 85F's block
  RAM (3,744 Kbit).
- So colour means **the frame in SDRAM**, with a line buffer in block RAM. Scan-out at 8 planes and
  30 Hz is 39 MB/s, within a 16-bit SDRAM's peak but shared with drawing and any core.
- A palette RAM of 256 × 24 bits maps colour numbers to RGB; the TMDS lanes then carry distinct
  R, G and B.
- The primitives gain "a colour number in place of the op" (TM-785 p29, PRINTED; W§2.5).

This is H10.

---

## 3. Input

### 3.1 Keyboard

The ULX3S has two micro-USB ports (MANUAL.md, fetched 2026-11-25):
- US1 is "main micro-USB for power, program and communication": the FTDI UART.
- US2 is "auxiliary micro-USB connected directly to FPGA pins for experimenting with user-defined
  USB cores or to connect PS/2 keyboard or mouse using USB-OTG and USB-PS/2 adapters". On v2.0.x
  and v3.0.x it "supports both device and host mode".
- The manual adds: "For PS/2 keyboard, combo USB-PS/2 keyboard is recommended, some older Logitech
  are known to work."

US2's FPGA pins (prjtrellis `ulx3s_v20.lpf` lines 191-203):
- `usb_fpga_dp` E16 / `usb_fpga_dn` F16, a differential input;
- `usb_fpga_bd_dp` D15 / `usb_fpga_bd_dn` E15, single-ended bidirectional;
- `usb_fpga_pu_dp` B12 / `usb_fpga_pu_dn` C12, the pull-up/down control.

| approach | effort | notes |
|---|---|---|
| **events over the host link** | none on the board | the host's keyboard (terminal, or M11's browser canvas) produces S§4.3 records; the same script format replays; first, so input never blocks H6-H7 |
| **PS/2 on US2** through an OTG + USB-PS/2 adapter with a combo keyboard | small: a PS/2 receiver is a clocked shift register (OURS, write it in BSV, ~200 LUT estimated) | the manual's own suggestion; **one port, so one device**: keyboard *or* mouse |
| **USB-HID host** (low-speed, HID Boot Protocol) | medium | third-party cores exist (e.g. nand2mario `usb_hid_host`: low-speed 1.5 Mbit/s from a 12 MHz clock, Boot Protocol keyboards and mice; found by web search 2026-11-25, not downloaded, licence not checked). A third-party core must not enter git without its terms (repo-is-public rule); writing our own low-speed host in BSV is the clean route but larger |
| two devices at once | needs a USB hub through a HID host, or a second port (the "ULX3S USB extension board", web result, not verified), or the mouse kept on the host link | open (§7) |

**The 16-bit JIS mapping (OURS table, symbolic).** Input arrives as JIS codes and named keys
(S§1.2). The table maps a PS/2 set-2 or HID usage code, with shift state, to an event record.
- **Printing ASCII to full-width JIS X 0208:**
  - digits to 2330-2339;
  - A-Z to 2341-235A;
  - a-z to 2361-237A;
  - space to 2121;
  - punctuation to row 1 by the JIS table (e.g. `.` 2125, `:` 2127, `_` 2132, `>` 2164).
  The rows used are those test_11 covers (S§1.4). The convention, ASCII-range text stored as
  full-width JIS (`#"A"` = 16#2341), is PROSE/USAGE in S§1.2.
- **Named keys `key#`**: lf, cr, del, enter, esc, tab, bs, bell, up, down, left, right, abort,
  help, plus the control, meta, control_meta and keypad families (USAGE, W§3.5). Physical keys are
  assigned OURS:
  - Enter → cr, keypad Enter → enter;
  - Backspace → bs, Delete → del;
  - arrows → up/down/left/right;
  - Ctrl → control, Alt → meta;
  - lf and bell as Ctrl-J and Ctrl-G.
- **`pf#0`-`pf#18`** is 19 function keys (USAGE, W§3.5; comments give `pf#8` help, `pf#9` abort).
  A PC keyboard has 12, so OURS assigns:
  - F1-F12 → pf#0-pf#11;
  - Shift-F1-F7 → pf#12-pf#18.
  Help and abort are also kept on Insert and Pause, to taste. PF16 is MENU in the kana-kanji band
  (SCREENSHOT simpos.wmv@108-113; S§1.2), so pf#16 is Shift-F5 under this table.
- **The numeric values** of `key#`, `pf#` and `mouse#` are **not held** (W gap G2; S§6 Q2). The
  input box emits symbolic records; the numbers are assigned once, in the `#` expander's OURS
  table, shared by the software and the hardware.

### 3.2 Mouse

Three buttons (SCREENSHOT psi.wmv@23). The events are single and double clicks of left, middle and
right, `mouse#l ll m mm r rr` (USAGE; `mouse#rr` PRINTED TR-046 p28).

**The hardware emits raw records** `{mouse, Button, Down/Up, X, Y, t}` and `{move, X, Y}`:
- X and Y are clamped to the frame;
- t is a millisecond stamp.

Double-click classification stays in the handler process (software, S§4.3). This keeps the event
script identical between Bluesim, the board and the pure-software runs, and it keeps the TM-112
p10 timing question in one place.

The PS/2 mouse protocol is 3-byte packets; the HID Boot Protocol mouse report is 3 bytes as well.
Both feed the same box.

### 3.3 Event scripts in simulation

The software plan's format is used unchanged (OURS, S§4.3): `{key, JIS}`, `{key, name}`,
`{mouse, Button, X, Y}`, `{move, X, Y}`. Bluesim takes it two ways:
1. **at the record level**: the bench feeds the records into the input box's output queue, for
   the display tests;
2. **at the wire level**: a host script turns each record into the PS/2 (or USB) frames that would
   produce it, by the inverse of the §3.1 table. The bench clocks those frames into the receiver's
   pins and checks that the records coming out equal the script. This is the input box's own
   round-trip test.

### 3.4 The host link

The FTDI UART is on US1 (`ftdi_rxd` L4, the line the FPGA transmits on; `ftdi_txd` M1;
`../../bsv/ulx3s_fep.lpf`). Rates in use on this board:
- 115,200 baud in the FEP self-test (`../../bsv/README.md`);
- 1,000,000 baud in flute-lx50's console (its README).

| payload | bytes | at 115,200 baud (11,520 B/s) | at 1 Mbaud (100,000 B/s) |
|---|---|---|---|
| a raw frame, 1,280×984×1 | 157,440 | **13.7 s** | 1.6 s |
| a glyph command (opcode, font, JIS, x, y, op: OURS) | 8 | 1,440 glyphs/s | 12,500 glyphs/s |
| the 47×14 PIMOS console filled | 658 × 8 | 0.46 s | 0.05 s |
| test_11 `font_load` | 4,554 | 0.4 s | 0.05 s |
| an event record up | ≤ 8 | — | — |

So the link carries **primitives, never pixels**. Frame read-back over the link (a `fb_dump`
request) is for board-side checks only.

Framing (OURS): length-prefixed records with a sequence number and a CRC-16, so a dropped byte is a
loud error, not a garbled screen. 1 Mbaud is the target; 115,200 is the fallback.

---

## 4. Simulation and verification

All benches run in Bluesim, the repo's pattern:
- `bsc -sim`;
- a script that builds, runs and compares;
- a header listing the injected faults and what each was observed to fail (AGENTS.md "How work is
  verified here" 2).

| bench | what it checks | oracle | injected fault that must fail it |
|---|---|---|---|
| `WinFbBoxTb` | a command stream (from a file) through `mkWinFbBox`; the frame dumped as **PBM P4** | the Python device layer run on the same stream, its PBM compared **byte for byte** (`cmp`), like `run_pimm_lockstep.sh` | (1) swap the MSB/LSB bit order: every glyph row differs; (2) `exclusive_or` acting as `set`: the XOR-twice-erases case fails (cf. M8); (3) the glyph record's x and y swapped: the 'A' at 16#2341 fails its 48 set dots (cf. M0); (4) the fill's right-edge mask one dot short: the border dot count fails (cf. M5) |
| `WinScanOutTb` | one frame of the selected mode: hsync/vsync/de counts per line and per frame, against the mode table | the table (VESA or CEA numbers, CHECKed against the standards before they are pinned; OURS for reduced blanking) | hsync one dot late: the line-timing check fails |
| `WinTmdsTb` | the serializer's four lanes captured for one frame; decoded by a Python TMDS decoder (OURS, stdlib) back to pixels, sync and control periods | the decoded image equals the PBM; running disparity stays bounded; control symbols in blanking | flip one disparity branch: the balance check fails; a lane's load phase off by one: every symbol misframed |
| `WinInputTb` | §3.3 wire-level round trip | the event script itself | swap make/break handling: key-up events appear as presses |
| `WinLinkTb` | host-link framing: records in, primitives out, CRC | the host-side encoder | drop one byte: the CRC failure is reported, not drawn |
| `WinFepConsoleTb` (with H7) | the FEP emulator's tape `kernel` (`../../ref/pimm/fep_tapes/`) replayed; its window commands drive the box; the console frame dumped | the Python layer driven by `fep.py` on the same tape | drop the 132 font command's effect: the console's glyph run differs |

**Why PBM P4.** It is one bit per dot, rows padded to a byte, MSB first, 1 = black. That is the PSI
bit order (TM-115 p74-76, PROSE; S§1.1), with the frame's 1 = a set (black) dot. So the BSV dump
is a straight copy of the RAM, and the Python layer writes the same bytes. PNG (S§4.2) is made from
the PBM for viewing only. Tests compare the PBM, or a SHA-256 of it, as S§4.2 suggests.

**The runner.** `bsv/run_win_tb.sh` builds the benches into its own build directory and runs every
stream and tape. It joins `../../run_tests.sh` after the FEP emulator's line; its budget is about a
minute, like `run_fepemu.sh`.

A separate `bsv/run_win_fpga.sh`, on the pattern of `run_fepemu_fpga.sh`, does the rest:
1. runs the board top's self-test in Bluesim;
2. runs yosys, nextpnr-ecp5 and ecppack;
3. prints LUT/FF/DP16KD/Fmax per clock.

It is not in the suite, and it **does not touch a board**.

**Lockstep between kl0 and hardware.** With option (a), the host runs kl0 with the device layer in
"tee" mode: every primitive is applied to the Python frame and sent to the bench (Bluesim through a
pipe, or the board through the UART). After each event step the two frames are compared by PBM
hash. This is the M5-M8 tests run against the RTL.

---

## 5. FPGA

### 5.1 Resource and timing: measured and estimated

**MEASURED, 2026-11-25:** a Verilog sizing skeleton, scratch only, deleted after the run; source and
commands are in Appendix A. It has the framebuffer, a write port, the scan-out, TMDS and the
serializer. It has no drawing engine, input or link, and its scan-out was not simulated: it
measures cost only.

Tools: yosys 0.51, nextpnr-ecp5 0.6, `--85k --package CABGA381 --speed 6`.

| build | TRELLIS_COMB | TRELLIS_FF | DP16KD | EHXPLLL | pclk Fmax | sclk Fmax | sys (25 MHz) |
|---|---|---|---|---|---|---|---|
| mode 0, 1920×1080@30 letterbox, seed 1 | 1,373 / 83,640 | 375 | 80 / 208 | 1 / 4 | 87.93 (PASS at 74.00) | 399.52 (PASS at 370.10) | 115.10 |
| mode 0, seed 2 | 1,373 | 375 | 80 | 1 | 98.31 PASS | 429.37 PASS | 113.42 |
| mode 0, seed 3 | 1,373 | 375 | 80 | 1 | 95.63 PASS | 391.85 PASS | 112.87 |
| mode 1, 1280×1024@60, seed 1 | 1,426 | 375 | 80 | 1 | **88.21 FAIL at 108.34** | **426.26 FAIL at 541.71** | 106.55 |
| mode 2, 1280×1024 RB@49, seed 1 | 1,444 | 375 | 80 | 1 | 94.87 PASS at 75.00 | 420.88 PASS at 375.09 | 112.11 |

The pclk → sclk cross-domain "Max delay" is 1.24, 1.24 and 1.25 ns (mode 0, seeds 1-3), 1.47 ns
(mode 1) and 1.29 ns (mode 2), MEASURED. It is reported, not timed against a phase relation
(§5.2). The `<async>` → 25 MHz paths are the `ftdi_txd` pin input.

yosys's own cell count for mode 0: 1,165 LUT4 + 69 CCU2C, 375 TRELLIS_FF, 80 DP16KD, 4 ODDRX1F. The
FEP emulator's figures are in yosys's LUT4 terms, so 1,165 + 2 × 69 ≈ **1,303 LUT4** is the figure
to compare with them.

The first, unbanked run failed its pixel clock at 64.99 MHz, on the 80:1 RAM output mux. Its shift
clock reached only 225.23 MHz with a mod-5 counter; a one-hot phase and per-lane load flags fixed
it, as in flute-lx50's lx49 serializer. Both runs are MEASURED; the source in Appendix A is the
fixed one.

**MEASURED, 2026-11-25: the BSV design (H3).** `../../bsv/run_win_fpga.sh` builds `mkWinUlx3s` (the
box, the banked two-clock frame, the scan-out in the pixel domain, the serializer, the self-test)
in mode 0. Tools: bsc 2026.01, Yosys 0.51 (git c4b5190229), nextpnr-ecp5 nextpnr-0.6, ecppack
(Trellis) Version 1.4; `--85k --package CABGA381 --speed 6`; yosys `synth_ecp5` with `share` left
out (it merged the multipliers of exclusive rules into one shared multiplier on the system clock's
critical path, 22.89 MHz before, 33.89 after, MEASURED).

| seed | TRELLIS_COMB | TRELLIS_FF | DP16KD | sys Fmax (25 MHz) | pclk Fmax (74.00) | sclk Fmax (370.10) | pclk → sclk |
|---|---|---|---|---|---|---|---|
| 1 | 9,671 / 83,640 | 3,612 | 156 / 208 | 34.91 PASS | 74.53 PASS | 384.76 PASS | 1.47 ns |
| 2 | 9,671 | 3,612 | 156 | 34.32 PASS | 78.72 PASS | 411.52 PASS | 1.24 ns |
| 3 | 9,671 | 3,612 | 156 | 32.65 PASS | 79.43 PASS | 418.24 PASS | 1.53 ns |

**MEASURED, 2026-11-26: after the H3 follow-up** (the box's pipelined stages, §6's H3 status).
Same tools and script. Two other changes:
- the cursor's lookup is split over two pixel clocks (`mkWinCursor`, its header);
- yosys is told to keep the cursor planes in LUT RAM.

A first build without the split failed seed 3: pclk 72.94 MHz at 74.00, on the cursor's subtract,
plane read and dot select. Seeds 1 and 2 passed at 75.35 and 77.32 (MEASURED).

| seed | TRELLIS_COMB | TRELLIS_FF | DP16KD | sys Fmax (25 MHz) | pclk Fmax (74.00) | sclk Fmax (370.10) | pclk → sclk |
|---|---|---|---|---|---|---|---|
| 1 | 10,639 / 83,640 | 4,277 | 156 / 208 | 36.50 PASS | 77.26 PASS | 417.54 PASS | 1.48 ns |
| 2 | 10,639 | 4,277 | 156 | 34.66 PASS | 80.02 PASS | 412.71 PASS | 1.48 ns |
| 3 | 10,639 | 4,277 | 156 | 34.82 PASS | 82.59 PASS | 412.71 PASS | 1.47 ns |

yosys's own counts: 7,313 LUT4 (808 more than H3), 4,277 TRELLIS_FF, 156 DP16KD, 646 PFUMX, 6
L6MUX21 and 142 TRELLIS_DPR16X4. The added DPR16X4 are the stages' small FIFOs.

**MEASURED, 2026-11-26: after the read** (§2.4's 2026-11-26 extension, rule `sCollectRead`). Same
tools and script.

| seed | TRELLIS_COMB | TRELLIS_FF | DP16KD | sys Fmax (25 MHz) | pclk Fmax (74.00) | sclk Fmax (370.10) | pclk → sclk |
|---|---|---|---|---|---|---|---|
| 1 | 10,708 / 83,640 | 4,278 | 156 / 208 | 36.23 PASS | 81.37 PASS | 418.24 PASS | 1.45 ns |
| 2 | 10,708 | 4,278 | 156 | 35.44 PASS | 84.05 PASS | 420.34 PASS | 1.26 ns |
| 3 | 10,708 | 4,278 | 156 | 31.73 PASS | 84.56 PASS | 389.26 PASS | 1.47 ns |

Against the build before it: 69 more TRELLIS_COMB, 1 more FF, the same DP16KD. yosys counts
7,366 LUT4 (53 more). The m8_stops.md §3 estimate of 200-500 LUT4 was high, because the read reuses
the blit's source stream and funnel. The system clock's lowest seed fell from 34.66 to 31.73 MHz;
it still passes 25 MHz.

yosys's own counts: 6,505 LUT4, 3,612 TRELLIS_FF, 156 DP16KD, 559 PFUMX, 32 L6MUX21, 112
TRELLIS_DPR16X4 (the cursor planes and small FIFOs), 4 ODDRX1F, 1 EHXPLLL. The 156 DP16KD are the
frame's 80 banks, the save areas' 64 and 12 for the font, the glyph index and the self-test's
stream and configuration (157 was predicted by width and depth; yosys packs one fewer). The drawing box alone was about 5,200 LUT4 in an intermediate build (it
had been 15,800 before the frame port's request was registered in one rule: bsc had inlined the 80
bank puts into every calling rule). The critical paths that remain: system, a frame bank's
output through the 80:1 mux and the funnel into the glyph bitmap's address; pixel, the cursor plane
RAMs or port B's first mux level; shift, one flop and at most one LUT. The pixel clock's margin on
seed 1 is small (0.7%). Unchecked cross-domain delays (all through synchronizers): system → pclk
8.45-10.06 ns, pclk → system 1.21-1.27 ns.

**MEASURED, 2026-11-26: after the drawing targets** (§2.4's prim `b`: the surface registers, rules
`blitSetup`, `lSetup`, `initClearB`, the line's row registers). Same tools and script.

| seed | TRELLIS_COMB | TRELLIS_FF | DP16KD | sys Fmax (25 MHz) | pclk Fmax (74.00) | sclk Fmax (370.10) | pclk → sclk |
|---|---|---|---|---|---|---|---|
| 1 | 11,690 / 83,640 | 4,549 | 156 / 208 | 36.44 PASS | 78.06 PASS | 373.83 PASS | 1.34 ns |
| 2 | 11,690 | 4,549 | 156 | 34.55 PASS | 82.71 PASS | 406.01 PASS | 1.48 ns |
| 3 | 11,690 | 4,549 | 156 | 33.55 PASS | 87.17 PASS | 384.17 PASS | 1.25 ns |

Against the read's build (10,708 / 4,278 / 156; sys 36.23, 35.44, 31.73): 982 more TRELLIS_COMB,
271 more FF and the same DP16KD. yosys counts 8,058 LUT4 (692 more than the read's 7,366) and
9 MULT18X18D in all (no count was kept for the read's build). Where the growth is was not
measured: sharing the cut between fill, copy and read (the final build) did not shrink it. The
worst seed's system clock rose from 31.73 to 33.55 MHz. The pitch multiplies moved out of `accept`, `glyph6` and the line's address
into setup cycles of their own.

The shift clock is close: seed 1's sclk is 373.83 MHz against 370.10, a 1% margin. Its path is one
flop and one LUT, and 2.3 ns of it is routing. The FIRST build of this change failed there: seed 1's
sclk was 326.26 MHz, with sys 34.18, 34.25, 33.35 and 11,682 TRELLIS_COMB. It differed from the
final build only in the cut: one per primitive, and the target's 16 × 16 multiply. INFERENCE: the
serializer's logic did not change, and the two builds are within 8 TRELLIS_COMB of each other, so
the failure is the serializer's placement, which varies from one build to the next. Any later
change to the box may fail this check again; the 3-seed PASS here is narrow. Placing the serializer in a region of
its own would be the fix, not a change to the box.

**ESTIMATED (OURS, not synthesized):**

| block | LUT4 | DP16KD | basis |
|---|---|---|---|
| scan-out + framebuffer + TMDS (above) | 1,300 | 80 | MEASURED |
| `mkWinFbBox` drawing engine (fill, line, glyph, copy, funnel shifter, masks, clipping) | 2,000-4,000 | 0 | INFERENCE; MEASURED at H3 as about 5,200 LUT4 (above) |
| glyph cache: test_11 + the 94×94 index (all six fonts: +13) | 300 | 3 + 5 (= 8; 21 with all fonts) | §2.5 |
| save areas in block RAM (H0-H7) | 100 | up to ~100 | §2.3 |
| cursor overlay | 200 | 0 | OURS |
| UART link + framing + CRC | 400 | 1 | OURS |
| PS/2 receiver + table | 300 | 1 | OURS |
| USB-HID host (later) | 1,000-2,000 | 0-2 | INFERENCE |
| **display + input + link** | **≈ 5,000-8,500** (6-10% of 83,640) | **≈ 90-110 (+ save areas)** | |
| + FEP emulator (`mkPimmFepEmu` + SD reader) | 14,816 | 3 | MEASURED, `../../bsv/README.md` |
| + SDRAM controller | small | 0 | in `PimUlx3s`'s build (not separately measured) |
| + `mkPimmCore` | **unknown** | its 2^15 × 40-bit low RAM alone is ≥ 72 DP16KD by bits, 96 at 1,024×18 × 3 wide (computed) | never synthesized (§1.4) |

**Coexistence (INFERENCE).**
- Display, input, link and FEP emulator together come to about 20,000-23,000 LUT4 and about 95-115
  DP16KD. That is a quarter of the logic and about half the block RAM, which **fits**.
- Adding `mkPimmCore`'s low RAM (96) to the framebuffer (80) and the rest (about 15-30) reaches
  191-206 of 208. That is at the edge. In a combined bitstream, the save areas must go to SDRAM
  (H8), or the core's low RAM must move there.
- The core's logic size is unmeasured. No claim is made that the core fits until it is synthesized.

### 5.2 Clocking

| clock | source | used by |
|---|---|---|
| 25 MHz | board oscillator, G2 (`ulx3s_85f.lpf`) | system domain: drawing engine, link, input, FEP emulator (35.03 MHz Fmax, PASS at 25) |
| 370 MHz shift + 74 MHz pixel | **one EHXPLLL**: `ecppll -i 25 -o 370 --clkout1 74` → CLKI_DIV 5, CLKFB_DIV 74, VCO 740 MHz, CLKOP ÷2 = 370, CLKOS ÷10 = 74 (MEASURED output) | scan-out, TMDS, serializer; the pixel and shift clocks are phase-locked from one VCO, so the serializer's load uses no synchronizer. nextpnr reports the pclk → sclk transfer (`h0 <= t0`) as a cross-domain "Max delay" of 1.24 / 1.24 / 1.25 ns (mode 0, seeds 1-3) and 1.29 ns (mode 2), MEASURED, under one 2.70 ns shift period. It is **reported, not checked** against the two outputs' phase relation, so H2 must simulate the load phase and H3 must constrain it. **H3:** the serializer takes its load phase from a pixel-domain toggle (flute-lx50's `dvi_ser` method) and `run_win_fpga.sh` fails the build if nextpnr's pclk → sclk delay exceeds 2.70 ns (1.24-1.53 ns on 3 seeds, MEASURED); the five alignments and the unsafe sample ages are simulated (`WinCrossModel.bsv`). 74.25 MHz is not reachable from 25 MHz with 371.25 on the same PLL: `ecppll -i 25 -o 371.25 --clkout1 74.25` gives 370 and 82.2222 MHz (MEASURED), so mode 0 runs at 74.00 MHz, 29.9 Hz |
| 375 + 75 MHz | `ecppll -i 25 -o 375 --clkout1 75` (VCO 750) | mode 2 |
| 12 MHz (USB low-speed) | a second PLL output, or a 48 MHz output ÷4 | the HID host (later) |

**Crossings.**
- System to pixel: through the dual-clock DP16KD, plus a 2-flop synchronizer for the few mode,
  pan and cursor registers. These are written by the system domain and sampled at the frame start
  in the pixel domain.
- Pixel to system: the frame counter and vblank, synchronized, for drawing that waits for vblank.

### 5.3 Constraints

Taken from the references above and **not invented**:
- **GPDI**: `gpdi_dp[0..3]` A16, A14, A12, A17 as LVCMOS33D (the complements B16, C14, A13, B18
  follow); prjtrellis `ulx3s_v20.lpf` lines 298-306; flute-lx50 `constraints/ulx3s_85f.lpf` lines
  74-83. HPD B20 is an input in flute-lx50's file (lines 223, 226); the same site is `gpdi_ethn` in
  the prjtrellis file, so use flute-lx50's, which is verified on this board.
- **US2**: E16/F16, D15/E15, B12/C12 (prjtrellis lines 191-203).
- **FTDI**: L4 (FPGA transmits), M1 (`../../bsv/ulx3s_fep.lpf`).
- **SDRAM**: `../../bsv/ulx3s_85f.lpf` lines 38-87.
- **SD card**: `../../bsv/ulx3s_fep.lpf`.

`bsv/ulx3s_win.lpf` is a copy, not an edit, of these lines, as `ulx3s_fep.lpf` was made. Each
group's header cites its source line range.

### 5.4 Board bring-up: the owner's steps, never run by an agent

The ULX3S on this machine runs Linux Flute for another session. Loading any bitstream replaces it,
so these steps wait for a window agreed with that session. **No agent runs them.**

```
# from pim/, after bsv/run_win_fpga.sh has built bsv/build-winfpga/ulx3s_win.bit (H3)
openFPGALoader -b ulx3s bsv/build-winfpga/ulx3s_win.bit      # SRAM, not flash
# monitor on the GPDI connector
# later, with the link (H6): python3 tools/winlink.py --port /dev/tty.usbserial-* --baud 1000000 --selftest
```

H3's bitstream has no link: it draws `winscan.py`'s mode 0 test card by itself at reset and starts
mode 0 (1920×1080 at 74.00 MHz, the frame letterboxed 1:1). LED 7 is the PLL lock, LED 0 the
self-test done, LED 1 a self-test command that returned a status other than OK, LED 2 toggles every
16 frames (the pixel domain runs). BTN1 resets.

What to see, per milestone:
- **H4a**: a test card at 640×480 (border, the 'A' glyph run, the status band), the frame reduced
  2:1.
- **H4b**: the same test card at 1:1, letterboxed in 1080p30.

If the monitor shows "no signal" in H4b, try mode 2, then the 720p fallback, and record which the
monitor takes: that is the owner's answer to §7's monitor question. LEDs show the PLL lock (LED 7),
link activity and a CRC error.

---

## 6. Milestones

Sizes are rough, in lines of BSV plus Python, tests included.

| # | milestone | test, and what it proves | mirrors | size |
|---|---|---|---|---|
| H0 | **The framebuffer box and PBM lockstep.** The Python device layer's primitive set frozen as a command format (written here if M5 has not landed); `mkWinFbBox` with `fb_fill` and an `fb_dump`; `WinFbBoxTb` | a fill stream gives a byte-identical PBM on both sides; injections (1) and (4) of §4 fail it | M5 (its primitive set) | ~600 |
| H1 | **Glyphs and the rest of the drawing set.** Glyph cache from test_11 (`font_load`), `fb_glyph`, `fb_line`, `fb_copy`, `fb_save`/`fb_restore` in block RAM | the 'A' at 16#2341 = 48 dots (S§1.4, MEASURED there); a Login PIMOS prompt run in test_11; XOR twice erases; HIDE/SHOW restores dots exactly; injections (2) and (3) fail | M0, M5, M7, M8 (their dot-count tests) | ~1,200 |
| H2 | **Video timing and TMDS in simulation.** `mkWinScanOut` (modes 0, 2, 640×480), cursor overlay, serializer; `WinScanOutTb`, `WinTmdsTb` | decoded TMDS equals the PBM; timing per mode table; the cursor composite equals the Python view's | M5 (the PNG view) | ~700 |
| H3 | **Synthesis fit.** The board top `mkWinUlx3s` (H0-H2 plus a self-test drawing a test card) through `run_win_fpga.sh` | LUT/FF/DP16KD/Fmax recorded per clock, as §5.1 but for the BSV design; mode 0 PASS on 3 seeds | — | ~300 |
| H4 | **Board scan-out (the owner runs it).** H4a 640×480 reduced; H4b 1080p30 letterbox; H4c mode 2 if the monitor takes it | a photo or the owner's note of the test card, recorded in `bsv/README.md` | — | (owner) |
| H5 | **Keyboard and mouse.** PS/2 receiver on US2, the §3.1 table, `{move}`/`{mouse}` from a PS/2 mouse (or the mouse on the link); `WinInputTb` wire-level round trip | Bluesim: the script equals the events out; injection: make/break swapped fails. Board (owner): typed keys appear in the event log over the link | M1 (keyboard), M6 (mouse) | ~500 |
| H6 | **The host link carrying kl0's drawing.** `mkWinLink`, `tools/winlink.py`; the device layer's tee mode | the M1/M4 runs of `../../psi/test_espc.py` drive Bluesim through a pipe with equal PBM hashes at every step; dropped-byte injection is caught by the CRC | M1-M5 run against the RTL | ~800 |
| H7 | **The Login PIMOS screen on a real monitor.** kl0 on the host, Login PIMOS's three prompts, menus and the echo-less password drawn by the board, keys from the board's keyboard | owner: the screen as the M2 transcript predicts; the PBM read back over the link equals the Python layer's | M1, M2, M4 | ~200 + owner |
| H7b | **PIMOS console from the FEP emulator, no KL0** (§1.4), in Bluesim first (`WinFepConsoleTb` on the `kernel` tape) | the 47×14 `PIMOS CONSOLE` with `Shell>> `, labelled as the FEP stand-in's | M4 (via fep.py) | ~400 |
| H8 | **Save areas in SDRAM**, through `Sdram_Controller` behind the box | M7's restore test on the RTL with 10 windows hidden (more than block RAM holds) | M7 | ~500 |
| H9 | **Chrome, manipulator and graphics at speed**: vblank-synchronized drawing, fill patterns | M6-M8 tests on the board through the link | M6-M8 | ~400 |
| H10 | **Colour (PSI-II/PSI-UX)**: frame in SDRAM with a line buffer, palette RAM, colour-number ops | a TM-785-style colour-pair window; 1/4/8-plane modes | — (no software milestone yet) | ~1,000 |
| H11a | **(c2) KL0 front end, first light** (Bluesim): decode of the KL0 instruction word, the cell encoding (OURS), control and unify instructions on the core's boxes (`PimmDBox`, `PimmHBox`, `PimmSBox`), backtracking state (choice points, trail, cut) | lockstep against `psi/kl0.py` per instruction (opcode, PC, dereferenced registers), on `paragraph` methods (`espc.py behave`'s oracle); injection: a wrong cut barrier fails the first cut | P3's goal on our hardware | ~2,000 |
| H11b | **(c2) the FEP census in lockstep**: every method `census --fep --recipes` runs | the success/failure/refused split equal to kl0's (829/235/385 at S§2.1), and the traces equal | — | ~1,500 |
| H11c | **(c2) the boot route and Login PIMOS on the KL0 PU**, the display boxes driven by it instead of the host | the M1/M4 screens, PBM-equal to the host run; then on the board (owner) | M1-M4 | ~800 |
| H12 | **(c1) the microcoded PU**: `PimPU`'s datapath built to Fig. 3-25, its WCS loaded with `syspsi` and `sysidat`; each field settled in `asm/mekbn.py` first | rung P2 (`../pimos_roadmap.md` §9): the held microcode decodes KL0 instructions; then P3 against (c2)'s traces at instruction boundaries; then `pimm.MEkbn` (Pseudo PIM/m) on the same datapath | P1-P3 | open (large) |
| H13 | **SIMPOS → FEP → PIMOS on one board**: a PU in KL0 mode running the stand-ins and held `pimfep`, linked by `PimmScsiBox` to a PU in KL1 mode running PIMOS (or one PU switching modes, as Pseudo PIM/m) | P5 on hardware: `pimfep` in place of `mkPimmFepEmu`; Login PIMOS → `Shell>> ` on the monitor | P5 | open; needs `mkPimmCore` synthesized and SDRAM-backed |

**Status (2026-11-25): H0 and H1 built in Bluesim.** `../../psi/winfb.py` (the Python reference; its
header freezes the command format and every OURS choice), `../../bsv/WinFbBox.bsv` (`mkWinFbBox`: all
of fill, line, glyph, copy, save/restore, dump; save areas and test_11 in block RAM),
`../../bsv/WinFbBoxTb.bsv`, `../../bsv/run_win_tb.sh` (in `../../run_tests.sh`): 11 streams PBM- and
status-identical by `cmp`; the injected faults and what each failed are in the runner's header.

**H2 built in Bluesim (2026-11-25).** `../../bsv/WinScanOut.bsv` (`mkWinScanOut`) contains:
- `mkWinTiming`, the mode table:
  - mode 0: 1920×1080@30 with the frame letterboxed 1:1 at (320,28);
  - mode 1: 1280×1024@60 DMT;
  - mode 2: 1280×1024 RB @49.4, OURS;
  - mode 3: 640×480 with a 2×2-OR 2:1 reduction from frame row panY. That is OURS, because 2:1 gives 512 rows
    for 480 lines; the default shows rows 0-959, MELCOM's 960.
- `mkWinFetch`, which reads port B through a new box scan port;
- `mkWinCursor`, the overlay of §2.6, latched at the frame start;
- `mkWinTmdsEnc` ×3;
- `mkWinTmdsSer`, the 10:1 serializer.

Timings and the TMDS encoding:
- **Modes 0, 1 and 3 are sourced**, SECONDARY, from the Linux `drm_edid.c` lines for CEA VIC 34, DMT 0x23 and
  DMT 0x04/VIC 1, fetched 2026-11-25. They match the CHECK figures of §2.2 and Appendix A. 640×480 is −H −V;
  modes 0 and 1 are +H +V.
- **Mode 2 is OURS.** Its +H −V polarity is CHECK.
- Vsync changes at the line start. That is CHECK against CEA-861's edge alignment.
- The TMDS encoder, the control characters, the bit-0-first order and the channel map are from DVI 1.0
  Fig. 3-5 p29, §3.2.3 p30 and Fig. 3-2 p26. This was read in a copy of the spec, so it is no longer CHECK.
  Fig. 3-5 prints the characters q_out[0:9], bit 0 first. The skeleton's [9:0] values agree.

The Python references are `../../psi/winscan.py` (modes, timing model, view, checkers) and
`../../psi/wintmds.py`. In `../../bsv/run_win_tb.sh`:
- 17 scan cases decode clock by clock to the reference view, and they re-encode identically. The cases are
  the four modes, mode 2 with no cursor, and 12 random small timings.
- The frame dumped after the scan still equals the Python PBM.
- The encoder bench matches `wintmds.encode` on 15,439 characters.
- The serializer bench runs at a 5:1 clock relation and carries the characters on all lanes.

16 injections are in the runner's header. One is not caught: the serializer's pixel-word sample phase is
invisible with ideal clocks in Bluesim. **The pclk → sclk load is therefore not verified by H2.** The box and
the scan-out share one clock in the bench, so the DP16KD crossing is not verified either. Both go to H3's
timing constraints (done at H3, below).

**H3 built (2026-11-25): synthesis fit, mode 0 PASS on 3 seeds** (the table in §5.1).
- `../../bsv/WinFrame.bsv` (`mkWinFrame`): the frame banked by hand into 80 DP16KD
  (`mkSyncBRAMCore2`, 1,024 words each), port A in the system clock (registered request,
  latency 2), port B in the pixel clock (registered request and two registered mux levels,
  latency 4). At H3 the box waited a cycle for every frame read (a full-screen scroll 384,637
  cycles, ~15 ms at 25 MHz); the follow-up below removed the wait.
- `../../bsv/WinUlx3s.bsv`: `mkWinCore` (the box; the scan-out in the pixel domain behind a
  `mkSyncFIFO` of commands; a self-test FSM drawing the mode 0 test card from a load file) and the
  synthesized `mkWinUlx3s` (`mkAsyncReset` per domain; null crossings to the serializer);
  `WinUlx3sTop.v` (PLL, power-on reset, ODDRX1F) and `ulx3s_win.lpf` (pins cited in §5.3).
- The serializer's load phase comes from the pixel clock (a toggle through a two-flop
  synchronizer restarts the phase), so H2's uncaught injection #14 is now caught, in Bluesim by
  `WinCrossModel.bsv` and in the build by the pclk → sclk delay check.
- `../../bsv/WinUlx3sTb.bsv`: the core on three clocks; the self-test's frame, a whole mode 0
  frame of characters and three lines of serial bits are checked. `WinTmdsSerTb` runs all five
  pixel-to-shift alignments.
- The injected faults and what each failed (OBSERVED) are in `../../bsv/run_win_tb.sh`'s header.

**H3 follow-up (2026-11-25): the drawing speed won back, and better than H1.** H3's banked frame
answers port A two cycles after a put, and the box waited a cycle on every frame read. Now:
- `../../bsv/WinMemPipe.bsv` (`mkWinMemPipe`) is a pipelined front for a RAM port. Reads run under
  credits with two in-order response ports, and each word is captured in the one cycle it is
  valid.
- The box is now stages: the blit's source stream, the funnel with a carried source word, and a
  shared read-modify-write stage with an address interlock (`mkWinPendQ`). The line is split into
  a Bresenham dot generator and a merge of each word's dots. The dump is a read stream.
- MEASURED, H3 then H1 in brackets:

  | operation | cycles (H3; H1) |
  |---|---|
  | full-screen scroll | 155,205 (384,637; 231,361), about 6.2 ms at 25 MHz |
  | xor fill 1280×984 | 157,443 (236,161; 157,441) |
  | 100 glyphs | 6,680 (12,140; 9,772) |
  | 1,280-dot diagonal | 2,196 (6,401; 5,121) |
  | save + restore 400×300 | 16,514 (62,102; 46,502) |

  The streams are `../../bsv/win_measure/`, run by `../../bsv/win_measure.sh`.
- All 11 H0/H1 streams stay byte-identical. So does a new directed stream,
  `../../bsv/win_streams/pipe.txt`: small-shift overlapping copies each way, wide x-major pens,
  merged runs and save areas. It runs with the bench refusing responses 3 cycles in 8 (`+stall`).
- The pipelining's injected faults and what each failed are in `../../bsv/run_win_tb.sh`'s header.
- `run_win_fpga.sh` passes on all 3 seeds (the table in §5.1).

**H6, the RTL half, built in Bluesim (2026-11-25).**
- `../../tools/winlink.py` freezes the link (OURS). Down, one frame a command: `A5 SEQ LEN=13`, the
  104-bit record, then CRC-16/CCITT-FALSE. Up, records `5A SEQ TYPE LEN … CRC`: status, dump data
  in 64-word records, and errors (CRC, LEN, SEQ).
- It also holds the receiver's model and the checker.
- `../../bsv/WinLink.bsv` (`mkWinLink`: UART receiver and transmitter, frame receiver, record
  sender, each its own module) puts the box behind one `Client`.
- `../../bsv/WinLinkTb.bsv` puts a host on both lines, at 4 cycles a bit, keeping 8 commands
  unanswered at most. `../../bsv/run_win_link.sh` (called by `run_win_tb.sh`) runs 6 cases:
  glyphs, lines and xor_twice clean, then a dropped byte, a flipped bit and a bad LEN.
  - Every record's CRC is checked.
  - The error records equal the model's.
  - The statuses and every dump equal `psi/winfb.py` run on the commands the model accepted.
  - So the plan's §4 injection "drop one byte: the CRC failure is reported, not drawn" is a
    passing case.
  - The RTL injections are in `run_win_link.sh`'s header.
- Not done:
  - the board top with the link at 1 Mbaud (divisor 25), and synthesis of it;
  - the device layer's tee mode and the `test_espc.py` runs through a pipe. Those are in `psi/`
    and belong to the window software's owner.

Not yet: the board (H4, the owner's step: §5.4). H4 needs the owner to load the bitstream and
report what the monitor shows; a monitor that refuses 1080p30 needs mode 2 or the 720p fallback
built (`run_win_fpga.sh` is mode 0 only), and mode 3's 640×480 is the fallback for H4a.

**Order:**
- H0-H3 are all Bluesim and synthesis. They need no board, and nothing from the owner but review.
- H4, H5 and H7 need the board, a monitor and input devices.
- H6 can go before H4: the link is checked in Bluesim through a pipe.
- H11a-H11c, the KL0 PU, run in parallel with the display work and need no board until H11c. They
  touch `bsv/`'s core, so they are scheduled with whoever is working on `mkPimmCore`.

**Known decisions that are OURS**, each to be labelled in its file and listed in a source check as
step 3l did:
- every module;
- the command format and link framing;
- the mode table's choice and the reduced-blanking timing;
- the cursor overlay and its shapes;
- the PS/2/HID-to-JIS table and the pf# assignment;
- the save-area placement;
- the 94×94 glyph index;
- S = 40.

---

## 7. Risks, open questions, and what the owner must supply

| id | risk or question | mitigation / current answer | grade |
|---|---|---|---|
| R1 | the ECP5 I/O at 740-750 Mbit/s on LVCMOS33D, through the GPDI's coupling capacitors: only 250 Mbit/s is proven on this board | check FPGA-DS-02012's DDR and I/O tables before H4; H4a first at the proven rate; 720p uses the same rate as 1080p30, so no fallback is slower except 640×480 | INFERENCE |
| R2 | the monitor may refuse 1080p30, and almost certainly some refuse the 49 Hz reduced-blanking 1280×1024 | try in the §5.4 order; the owner reports what the monitor takes; `gpdi_sda`/`gpdi_scl` (B19/E12) could read the EDID later (OURS) | — |
| R3 | US2 is one port: keyboard and mouse at once | mouse on the host link until a hub-capable HID host or a second port exists | — |
| R4 | a third-party USB-HID core's licence | do not vendor without terms (repo-is-public rule); manifest-only, or write our own | — |
| R5 | block RAM in a combined bitstream with `mkPimmCore` (§5.1) | save areas to SDRAM (H8); core low RAM to SDRAM; or the frame in SDRAM with a line buffer | INFERENCE |
| R6 | the SDRAM is shared with the PIM/m store | one arbiter, a fixed partition; option (a) has no core on the board | OURS |
| R7 | the Python device layer does not exist yet; H0 depends on it | H0 writes it if M5 has not, in the module both sides import | — |
| R8 | the board is in use by another session | all of H0-H3 and H6 in Bluesim; board steps written for the owner | — |
| R9 | (c2): kl0.py has no cell-level representation, so the first lockstep is per instruction on dereferenced values, not per memory cell; the PSI-III's own tag and word format is not printed (`../psi_microword.md` §3b) | choose the cell encoding OURS (the PIM/m 40-bit, 8-bit-tag cell is the obvious one, since the chip is shared, INFERENCE); give kl0.py a cell view later if the lockstep needs it | INFERENCE |
| R10 | (c1): the microword's open fields (§1.3), `sysinit` uncharacterised, and `syspsi` holding KL0 only "probable, not settled" | settle each by measurement in `asm/mekbn.py` before building it; (c2)'s traces become the instruction-boundary oracle | — |
| R11 | two PUs on the 85F | unmeasured until `mkPimmCore` is synthesized; the one-PU, mode-switching variant (Pseudo PIM/m) is the fallback | INFERENCE |
| Q1 | PSI-II physical resolution and status-band height | as S§6 Q1; a parameter here | INFERENCE |
| Q2 | did the PSI have a hardware mouse cursor? | unknown; the overlay is OURS and kept out of the frame | — |
| Q3 | where the PSI's rasterop lived (controller or microcode) | S§1.5 INFERENCE; for route (c1), `syspsi`'s I/O microcode may show it (P1) | INFERENCE |

**What the owner must supply:**
1. **Board time**, arranged with the Linux Flute session (H4, H5, H7).
2. **A monitor or TV with HDMI or DVI input** that takes 1920×1080@30 (TVs commonly do), and, if
   possible, one that takes 1280×1024 at 50-60 Hz. Plus an HDMI cable to the GPDI connector.
3. **A USB keyboard that also speaks PS/2** (a "combo" keyboard, per the ULX3S manual), with a
   USB-OTG adapter and a USB-to-PS/2 adapter for US2.
4. **A three-button USB mouse.** For now it stays on the host or on a second port (R3); say whether
   a ULX3S USB extension board or a hub is acceptable.
5. A decision on R4: write our own HID host, or vendor one with its licence on record.

---

## 8. Verification of this page

- The synthesis numbers in §2.2, §2.3, §5.1 and §5.2 were produced on 2026-11-25 in a scratch
  directory, from the Appendix A source and commands; the build was deleted afterwards. The board
  was not touched: no programmer, serial port or card was opened.
- The pins were read from prjtrellis `ulx3s_v20.lpf` (local toolchain checkout), flute-lx50's
  `constraints/ulx3s_85f.lpf` (read only), and this repo's `bsv/ulx3s_85f.lpf` and
  `bsv/ulx3s_fep.lpf`.
- The CPU section (§1.3) rests on `../environment_audit.md` areas G and L, `../psi_microword.md`
  §3, §3a-§3c, §4.4 and §7, `../pim_architecture.md` §5, the headers of `../../bsv/PimPU.bsv` and
  `psi/kl0.py`, and `../../bsv/README.md`. They were read for this page; nothing in them was
  re-measured.
- The ULX3S manual's US1/US2, GPDI and PS/2 statements come from one fetch of
  `github.com/emard/ulx3s/blob/master/doc/MANUAL.md` (2026-11-25). Three web searches were made:
  ECP5 DVI modes on ULX3S, a USB-HID host core, and ECP5 PLL/DDR limits. Only the HID-core result
  is used, as a lead. Nothing was downloaded.
- This is a documentation change only. The ten `asm/*.py --check` passes were run before the commit.

---

## Appendix A. The sizing skeleton (OURS; scratch; reproducible)

Write the three files below into an empty scratch directory. Generate the PLLs:

```
ecppll -n pll_a -i 25 -o 370 --clkout1 74 -f pll_a.v     # mode 0: VCO 740, 370 / 74 MHz
ecppll -n pll_b -i 25 -o 540 --clkout1 108 -f pll_b.v    # mode 1: warns "540MHz not in range (10MHz, 400MHz)", gives 541.667 / 108.333
ecppll -n pll_c -i 25 -o 375 --clkout1 75 -f pll_c.v     # mode 2: VCO 750, 375 / 75 MHz
```

Then run `./build.sh 0`, `./build.sh 1`, `./build.sh 2`, and `SEED=2 ./build.sh 0`,
`SEED=3 ./build.sh 0`. Read `b*/nextpnr.log` for "Device utilisation" and "Max frequency for
clock". The tools were yosys 0.51 (git c4b5190229), nextpnr-ecp5 0.6 and ecppack (Trellis) 1.4.
`fbskel.v` SHA-256 `b62e5463166e3da6096e6c14f86b1adb6f262910fb7fe285ed75f5daa0f78dab`.

The skeleton was **not simulated**. Its TMDS encoder and serializer are written to the DVI
algorithm but unchecked, and it measures cost only. The H2 benches are the check for the real
design.

`build.sh`:
```
#!/bin/sh
# build.sh MODE  -> b$MODE/  (yosys synth_ecp5, nextpnr-ecp5 --85k CABGA381 -6 seed 1)
set -eu
M=$1; B=b$M${SEED:+s$SEED}; rm -rf $B; mkdir $B
yosys -q -l $B/yosys.log -p "read_verilog fbskel.v pll_a.v pll_b.v pll_c.v; chparam -set MODE $M fbskel; synth_ecp5 -top fbskel -json $B/top.json" > $B/yosys.console 2>&1
nextpnr-ecp5 --85k --package CABGA381 --speed 6 --json $B/top.json --lpf fbskel.lpf --textcfg $B/top.config --log $B/nextpnr.log --seed ${SEED:-1} --timing-allow-fail > $B/nextpnr.console 2>&1
ecppack --compress --input $B/top.config --bit $B/top.bit > $B/ecppack.console 2>&1
echo "mode $M done"
```

`fbskel.lpf` (the clock and FTDI lines as `../../bsv/ulx3s_85f.lpf`; GPDI as prjtrellis
`ulx3s_v20.lpf` 298-306 / flute-lx50 74-83):
```
LOCATE COMP "clk_25mhz" SITE "G2";
IOBUF PORT "clk_25mhz" PULLMODE=NONE IO_TYPE=LVCMOS33;
FREQUENCY PORT "clk_25mhz" 25 MHZ;
LOCATE COMP "ftdi_txd" SITE "M1";
IOBUF PORT "ftdi_txd" PULLMODE=UP IO_TYPE=LVCMOS33;
LOCATE COMP "gpdi_dp[0]" SITE "A16";
LOCATE COMP "gpdi_dp[1]" SITE "A14";
LOCATE COMP "gpdi_dp[2]" SITE "A12";
LOCATE COMP "gpdi_dp[3]" SITE "A17";
IOBUF PORT "gpdi_dp[0]" IO_TYPE=LVCMOS33D DRIVE=4;
IOBUF PORT "gpdi_dp[1]" IO_TYPE=LVCMOS33D DRIVE=4;
IOBUF PORT "gpdi_dp[2]" IO_TYPE=LVCMOS33D DRIVE=4;
IOBUF PORT "gpdi_dp[3]" IO_TYPE=LVCMOS33D DRIVE=4;
LOCATE COMP "led[7]" SITE "H3";
LOCATE COMP "led[6]" SITE "E1";
LOCATE COMP "led[5]" SITE "E2";
LOCATE COMP "led[4]" SITE "D1";
LOCATE COMP "led[3]" SITE "D2";
LOCATE COMP "led[2]" SITE "C1";
LOCATE COMP "led[1]" SITE "C2";
LOCATE COMP "led[0]" SITE "B2";
IOBUF PORT "led[*]" PULLMODE=NONE IO_TYPE=LVCMOS33 DRIVE=4;
```

`fbskel.v`:
```verilog
// Window-hardware sizing skeleton (OURS, scratch only, for
// pim/docs/simpos/window_hardware_plan.md Appendix A).  NOT the design:
// plain Verilog, written to measure what the 1-bit framebuffer, a DVI
// scan-out and the TMDS serializer cost on the ULX3S 85F.
//   - framebuffer 1280 x 1024 x 1 bit = 81,920 x 16-bit words, true dual
//     port: write port in the 25 MHz system domain, read port in the
//     pixel domain;
//   - a write port fed from a pin (ftdi_txd) through a shift register, so
//     synthesis cannot trim the RAM to a constant;
//   - timing generator, 1-bit pixel fetch, 3 TMDS encoders, a 10:1
//     serializer at 5x the pixel clock into ODDRX1F (2 bits per shift
//     clock), as flute-lx50's Video_DVI.v does at 640x480.
// MODE 0: 1920x1080@30 (CEA-861 VIC 34 timing), the 1280x1024 frame
//         letterboxed 1:1 at (320,28).  Pixel 74 MHz, shift 370 MHz.
// MODE 1: 1280x1024@60 (VESA DMT), pixel 108.33 MHz, shift 541.67 MHz.
module fbskel #(parameter MODE = 0) (
  input  clk_25mhz,
  input  ftdi_txd,
  output [3:0] gpdi_dp,
  output [7:0] led
);
  // MODE 2: 1280x1024, reduced blanking (OURS: htotal 1440, vtotal 1054), 75 MHz -> 49.4 Hz
  localparam HA = MODE == 0 ? 1920 : 1280, HF = MODE == 0 ? 88 : MODE == 1 ? 48 : 48,
             HS = MODE == 0 ? 44 : MODE == 1 ? 112 : 32, HB = MODE == 0 ? 148 : MODE == 1 ? 248 : 80;
  localparam VA = MODE == 0 ? 1080 : 1024, VF = MODE == 0 ? 4 : MODE == 1 ? 1 : 3,
             VS = MODE == 0 ? 5 : MODE == 1 ? 3 : 7, VB = MODE == 0 ? 36 : MODE == 1 ? 38 : 20;
  localparam HT = HA + HF + HS + HB, VT = VA + VF + VS + VB;
  localparam X0 = MODE == 0 ? 320 : 0, Y0 = MODE == 0 ? 28 : 0;

  wire sclk, pclk, locked;
  generate if (MODE == 0)
    pll_a pll (.clkin(clk_25mhz), .clkout0(sclk), .clkout1(pclk), .locked(locked));
  else if (MODE == 1)
    pll_b pll (.clkin(clk_25mhz), .clkout0(sclk), .clkout1(pclk), .locked(locked));
  else
    pll_c pll (.clkin(clk_25mhz), .clkout0(sclk), .clkout1(pclk), .locked(locked));
  endgenerate

  // ---- framebuffer: 80 banks of 1024 x 16 (one DP16KD each), so the
  // read mux can be pipelined (an inferred 81,920-deep RAM gave an
  // unpipelined 80:1 mux, 64.99 MHz, in the first run) ------------------
  reg [33:0] sh = 0;
  always @(posedge clk_25mhz) sh <= {sh[32:0], ftdi_txd};
  wire [16:0] wa = sh[32:16];
  wire [6:0] wbank = wa[16:10];
  wire [16:0] waddr;               // pixel-domain read address, below
  reg  [16:0] raddr;
  wire [15:0] bq [0:79];
  genvar b;
  generate for (b = 0; b < 80; b = b + 1) begin : bank
    reg [15:0] m [0:1023];
    reg [15:0] q;
    always @(posedge clk_25mhz) if (sh[33] && wbank == b) m[wa[9:0]] <= sh[15:0];
    always @(posedge pclk) q <= m[raddr[9:0]];
    assign bq[b] = q;
  end endgenerate
  // ---- timing ------------------------------------------------------
  reg [11:0] hx = 0;
  reg [10:0] vy = 0;
  always @(posedge pclk) begin
    if (hx == HT - 1) begin
      hx <= 0;
      vy <= (vy == VT - 1) ? 0 : vy + 1;
    end else hx <= hx + 1;
  end
  wire de0 = hx < HA && vy < VA;
  wire hs0 = hx >= HA + HF && hx < HA + HF + HS;
  wire vs0 = vy >= VA + VF && vy < VA + VF + VS;
  wire [11:0] fx = hx - X0;
  wire [10:0] fy = vy - Y0;
  wire infb0 = de0 && hx >= X0 && hx < X0 + 1280 && vy >= Y0 && vy < Y0 + 1024;
  assign waddr = {fy[9:0], 6'b0} + {fy[9:0], 4'b0} + fx[10:4];
  // pipeline: r0 address reg, r1 bank read, r2 8:1 mux, r3 10:1 mux, r4 bit
  localparam D = 4;
  reg [D-1:0] deP, hsP, vsP, inP;
  reg [4*D-1:0] bitP;
  reg [6:0] bk1, bk2;
  reg [15:0] mux8 [0:9];
  reg [15:0] word;
  integer k;
  always @(posedge pclk) begin
    raddr <= waddr;
    bk1 <= raddr[16:10]; bk2 <= bk1;
    for (k = 0; k < 10; k = k + 1) mux8[k] <= bq[k*8 + bk1[2:0]];
    word <= mux8[bk2[6:3]];
    deP <= {deP[D-2:0], de0}; hsP <= {hsP[D-2:0], hs0}; vsP <= {vsP[D-2:0], vs0};
    inP <= {inP[D-2:0], infb0}; bitP <= {bitP[4*D-5:0], fx[3:0]};
  end
  // the pixel (MSB leftmost, TM-115 p74-76); 1 = black dot
  reg pix2, de2, hs2, vs2;
  always @(posedge pclk) begin
    pix2 <= inP[D-1] ? ~word[4'd15 - bitP[4*D-1:4*D-4]] : 1'b1;   // white paper, black ink
    de2 <= deP[D-1]; hs2 <= hsP[D-1]; vs2 <= vsP[D-1];
  end
  wire [7:0] lvl = pix2 ? 8'hff : 8'h00;
  wire [9:0] t0, t1, t2;
  tmds_enc eb (.clk(pclk), .d(lvl), .c({vs2, hs2}), .de(de2), .q(t0));
  tmds_enc eg (.clk(pclk), .d(lvl), .c(2'b00),      .de(de2), .q(t1));
  tmds_enc er (.clk(pclk), .d(lvl), .c(2'b00),      .de(de2), .q(t2));

  // ---- serializer: 10 bits per pixel clock, 2 per shift clock -------
  reg [4:0] ph = 5'b00001;          // one-hot phase
  reg ld0, ld1, ld2, ldc;            // one load flag per lane, set a clock early (flute-lx50 lx49)
  reg [9:0] s0, s1, s2, sc;
  reg [9:0] h0, h1, h2;              // the pixel-domain words, retimed into sclk
  always @(posedge sclk) begin
    ph <= {ph[3:0], ph[4]};
    ld0 <= ph[3]; ld1 <= ph[3]; ld2 <= ph[3]; ldc <= ph[3];
    if (ph[2]) begin h0 <= t0; h1 <= t1; h2 <= t2; end
    s0 <= ld0 ? h0 : s0 >> 2; s1 <= ld1 ? h1 : s1 >> 2;
    s2 <= ld2 ? h2 : s2 >> 2; sc <= ldc ? 10'b0000011111 : sc >> 2;
  end
  ODDRX1F d0 (.D0(s0[0]), .D1(s0[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[0]));
  ODDRX1F d1 (.D0(s1[0]), .D1(s1[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[1]));
  ODDRX1F d2 (.D0(s2[0]), .D1(s2[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[2]));
  ODDRX1F dc (.D0(sc[0]), .D1(sc[1]), .SCLK(sclk), .RST(1'b0), .Q(gpdi_dp[3]));

  assign led = {locked, 7'b0};
endmodule

module tmds_enc (input clk, input [7:0] d, input [1:0] c, input de, output reg [9:0] q);
  wire [3:0] n1 = d[0]+d[1]+d[2]+d[3]+d[4]+d[5]+d[6]+d[7];
  wire xn = (n1 > 4) || (n1 == 4 && d[0] == 0);
  wire [8:0] m;
  assign m[0] = d[0];
  genvar i;
  generate for (i = 1; i < 8; i = i + 1) begin : g
    assign m[i] = xn ? ~(m[i-1] ^ d[i]) : (m[i-1] ^ d[i]);
  end endgenerate
  assign m[8] = ~xn;
  wire [3:0] m1 = m[0]+m[1]+m[2]+m[3]+m[4]+m[5]+m[6]+m[7];
  wire signed [5:0] bal = ($signed({2'b0, m1}) - 6'sd4) <<< 1;  // N1 - N0 of q_m[7:0]
  reg signed [5:0] cnt = 0;
  always @(posedge clk) begin
    if (!de) begin
      cnt <= 0;
      case (c)
        2'b00: q <= 10'b1101010100;
        2'b01: q <= 10'b0010101011;
        2'b10: q <= 10'b0101010100;
        default: q <= 10'b1010101011;
      endcase
    end else if (cnt == 0 || bal == 0) begin
      q <= {~m[8], m[8], m[8] ? m[7:0] : ~m[7:0]};
      cnt <= m[8] ? cnt + bal : cnt - bal;
    end else if ((cnt > 0 && bal > 0) || (cnt < 0 && bal < 0)) begin
      q <= {1'b1, m[8], ~m[7:0]};
      cnt <= cnt + {4'b0, m[8], 1'b0} - bal;
    end else begin
      q <= {1'b0, m[8], m[7:0]};
      cnt <= cnt - {4'b0, ~m[8], 1'b0} + bal;
    end
  end
endmodule
```
