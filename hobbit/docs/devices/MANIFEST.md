# Device documentation for the Hobbit board: acquisition manifest

Collected 2026-11-24 so that the board's device models (`tools/p9boot.py`,
`docs/p9boot.md` "Modelling choices") can rest on the vendors' data sheets
instead of inference.  `README.md` checks each modelling choice against
these documents.

The PDFs are held on disk in this directory but kept **out of git**
(`.gitignore`).  They are 1990-1997 vendor data books and sheets, all from
bitsavers.org except the two 53C94 sheets (MIT SIPB and hackaday.io, URLs
below), and none of them shows redistribution terms; the repository is
public.  This is the pattern of `pim/docs/nonlocal/LIT_MANIFEST.md`.
`sh fetch.sh` downloads whatever is missing and checks every file against
`SHA256SUMS` (`sh fetch.sh --check` only checks).  The files were fetched with
plain `curl` (generic user agent) from `bitsavers.trailing-edge.com` (the
53C94 sheets from their own hosts), and re-fetched fresh by `fetch.sh` to confirm the checksums.  The same paths are
on `bitsavers.org` and its mirrors (e.g. `bitsavers.mirrorservice.org`).
Nothing downloaded was executed.

Page numbers: "PDF p." is the page index in the file (what `pdftotext -f`
takes); "p." is the number printed on the page.  Every book has a fixed
offset between the two, given per row.  The text layers are OCR of scans and
wrong in places (O for 0, "IRON" for IRQN, "AST" for RST), so values that
matter were read from the page image (`pdftoppm -r 120 -f N -l N`).

## Held

| File | What is in it | Part / data sheet, date | Where in the file | Bytes | SHA-256 |
|---|---|---|---|---|---|
| `1992_National_Local_Area_Network_Databook.pdf` | National Semiconductor *Local Area Network Databook*, 1992 ed. | **DP83932B SONIC** data sheet, "Preliminary", TL/F/10492; AN-745 *DP83932 SONIC Bus Operations Guide*; AN-746 *Software Driver Programmer's Guide for the DP83932 SONIC* | data sheet p. 1-288..1-383 = PDF p. 297..392 (book p. 1-N = PDF p. N+9); AN-745 p. 1-384, AN-746 p. 1-396 | 31,700,590 | `b659e0e4a11ecc9506c9fce86660408eca18f003e7d7fa391b55b50688f60908` |
| `AN-0746.pdf` | National AN-746, *Software Driver Programmer's Guide for the DP83932 SONIC*, Wesley Lee and Mike Lui, March 1991 (standalone copy) | DP83932 | whole file | 834,639 | `e43eb0f3057136524303119ed4ae22f5e5d52353a09ba4c803cf27634050e56d` |
| `1991_Signetics_IC019_Data_Communication_Products.pdf` | Philips Components-Signetics *Data Communication Products* (IC19), 1991 | **SC26C94/SC68C94 QUART**, Preliminary Specification, **12 November 1990** | PDF p. 228..253 = p. 221..246 (p. = PDF p. − 7) | 37,588,060 | `a3db1b7ceddb24ce0203920a6fbff8af83db0ae64882c8a5c646db0d7f7712f1` |
| `1994_Signetics_Data_Communications.pdf` | Philips Semiconductors *Data Communications Products*, 1994 | **SC68C94 QUART**, Product specification, **27 April 1994**; then the article reprint *SC26C94 and SC68C94 (QUARTs) interrupt system and processor interface* (Peter Narvaez) | spec PDF p. 303..333 = p. 302..332; reprint from PDF p. 334 = p. 333 (p. = PDF p. − 1) | 77,460,303 | `c615686bc20100c71c27f5b1a5877cb8f88d22bf4b66810a4ad6fdf3dc3b3b04` |
| `WD33C93A_Data_Sheet_and_Application_Notes_Nov1990.pdf` | Western Digital *WD33C93A Data Sheet and Application Notes*, November 1990 | **WD33C93A** SCSI Bus Interface Controller | whole file, 91 pages; cited by PDF p. | 6,683,877 | `1513852c994336439ecca41c7111d7ea18e9fb5241a9d571d87f7489b0edda18` |
| `1997_IC12_Philips_I2C_Peripherals.pdf` | Philips Semiconductors *I2C Peripherals* (IC12), 1997 | **PCF8584** I2C-bus controller, Product specification, 1997 Mar 19; **PCF85xxC-2** family (PCF8582C-2 256 x 8 EEPROM), 1997 Feb 13 | PCF8584 PDF p. 556..587 = p. 555..586; PCF85xxC-2 PDF p. 631..643 = p. 630..642 (p. = PDF p. − 1) | 36,547,171 | `994ab97ef1d2801707930c868314e0a318f5b30c18ba0113b0c88c9770cff1bc` |
| `1992_SGS-THOMSON_Memory_Products_2nd_Ed.pdf` | SGS-Thomson *Memory Products* data book, 2nd ed., 1992 | **MK48T02/MK48T12** CMOS 2K x 8 TIMEKEEPER SRAM, February 1992 | PDF p. 1024..1037 = data sheet pp. 1/14..14/14 (p. 1023.. in the book) | 52,674,118 | `f7a440d4fcaf36a14fef1f675be413a867e5d476c11595bc71a3fd02e4653d39` |
| `1990_VTI_Computer_Products.pdf` | VLSI Technology *Computer Products* data manual, 1990 | **VL82C106** PC/AT Combo I/O (Hobbit BeBox, `../bebox_hardware.md` §7); **VL16C452** dual UART | VL82C106 p. 6-185..6-220 = PDF p. 440..475 (keyboard controller p. 6-197 = PDF p. 452; parallel port pp. 6-192..193 = PDF p. 447..448); VL16C452 p. 6-60/6-61 = PDF p. 315/316 (p. 6-N = PDF p. N+255 in chapter 6) | 30,319,538 | `70b0860b28d64988d8715bba51197e557e341a260e191eaab52af30eb65ad38e` |
| `MCS3201_IBM_PC_XT_AT_Floppy_Disk_Controller_1991.pdf` | Motorola **MCS3201** floppy disk controller data sheet, 1991 | Hobbit BeBox floppy controller (§8) | whole file, 26 pages | 1,209,745 | `ae038594d5423c585c1d752c678712904f97e0f5f2aa49f2f806e5bf9e3c7b5d` |
| `am53c94.pdf` | AMD **Am53C94/Am53C96** data sheet, Publication 16506 Rev. C, 1993 | Hobbit BeBox SCSI (§9). Printed page numbers match the Be draft's cites: p. 17 transfer counter, p. 22 internal state, p. 29 clock factor, p. 32 data alignment | whole file, 63 pages | 593,862 | `b24f3de1560b7880f984bdd5026da2f522022bf754dc5e19273fed2e2a195335` |
| `VGADOC_TRIDENT.TXT` | Finn Thoegersen's VGADOC 4b, the Trident chapter (`TRIDENT.TXT`): Trident SVGA registers by port and index, from vendor material and probing | Hobbit BeBox display card (`../bebox_hobbit.md` "The display card"): 3C4h index 0Bh chip version table and the old/new mode switch, index 0Dh/0Eh mode controls and the clock table | whole file, plain text; cited by register heading | 20,956 | `6de3bc454e4f98f646d3a3b36627e18579406f4d5af77adbd35a6b21cb6b915f` |
| `NCR_53C94_53C95_53C96_Data_Sheet_Feb90.pdf` | NCR 53C94/95/96 data sheet, February 1990 (image-only scan) | The original of the Am53C94's register set | whole file, 64 pages | 3,002,374 | `b084320157a0684955a4ab2f8587a776179dd8e7c15a1fce855d08af116cbdd1` |

URLs (all under `https://bitsavers.trailing-edge.com/components/`):

- `national/_dataBooks/1992_National_Local_Area_Network_Databook.pdf`
- `national/_appNotes/AN-0746.pdf`
- `signetics/_dataBooks/1991_Signetics_IC019_Data_Communication_Products.pdf`
- `signetics/_dataBooks/1994_Signetics_Data_Communications.pdf`
- `westernDigital/WD33C93A_Data_Sheet_and_Application_Notes_Nov1990.pdf`
- `philips/_dataBooks/1997_IC12_Philips_I2C_Peripherals.pdf`
- `sgs/_dataBooks/1992_SGS-THOMSON_Memory_Products_2nd_Ed.pdf`
- `vti/databook/1990_VTI_Computer_Products.pdf`
- `motorola/_dataSheets/MCS3201_IBM_PC_XT_AT_Floppy_Disk_Controller_1991.pdf`

Not on bitsavers: `am53c94.pdf` from
<https://stuff.mit.edu/afs/sipb/contrib/doc/specs/ic/scsi/am53c94.pdf>, and the
NCR sheet from
<https://cdn.hackaday.io/files/18974811783616/NCR_53C94_53C95_53C96_Data_Sheet_Feb90.pdf>.
The Hobbit BeBox rows were added 2026-11-24 for `../bebox_hardware.md`.
`VGADOC_TRIDENT.TXT` is the copy MIT 6.1810 serves,
<https://pdos.csail.mit.edu/6.1810/2017/readings/hardware/vgadoc/TRIDENT.TXT>
(VGADOC4B.ZIP, also on the HPAVC CD-ROM at discmaster.textfiles.com); the
file states no terms, so it is held like the PDFs.

Cited, not held: XFree86/X.Org's Trident driver header `trident_regs.h`
(Alan Hourihane, 1992-2003, MIT-style licence), section "Graphics Engine
for 9420/9430": the old engine's index port and register names (STATUS
0x90, MWIDTH 0xB8, MFORMAT 0xBC, STYLE 0xC4, FMIX/BMIX 0xC8, FCOLOUR 0xD8,
BCOLOUR 0xDC, DIMXY 0xE0, DESTLINEAR 0xE4, DESTXY 0xF8, COMMAND 0xFC, busy
bit 0x80).  Read from Debian's xserver-xorg-video-trident 1:1.4.0-3,
<https://sources.debian.org/data/main/x/xserver-xorg-video-trident/1:1.4.0-3/src/trident_regs.h>,
13,706 bytes, SHA-256
`79afccda5b1bda799e75dd7713f590431dbdd52f44db0a581d076a7a70517b34`.

### Dates against the board

The kernel `s9term` was built 1992-11-07 (`docs/s9term.md`), so the board is
1992 or a little older.

- The QUART has two editions here, and they disagree (see README §Quart).
  `io.h` follows the **1994** register map at 0x2D..0x2F, and `eiaintr`'s byte
  loop only works with the 1994 byte-count coding.  So the 1994 product
  specification describes the part the kernel was written for, and the 1990
  preliminary is kept as the earlier reading.
- The SONIC sheet is the "B" revision, marked Preliminary, in a 1992 book. It
  is the right date for the board.
- The WD33C93A sheet (Nov 1990) and the MK48T02 sheet (Feb 1992) are
  contemporary with the board.
- The PCF8584 and PCF8582 sheets are from **1997**. The PCF8582 sheet covers
  the later C-2 revision, not the PCF8582(A) a 1992 board would carry.  No
  1990-1992 Philips I2C data book is on bitsavers.

## Looked at, not taken

- `national/_dataBooks/1993_National_Local_Area_Networks.pdf` (74,877,887
  bytes) and `1995_National_Ethernet_Databook.pdf` (71,978,411 bytes).  These
  are later editions of the SONIC material.  The 1992 book is the closest in
  date to the board.  `national/_appNotes/AN-0745.pdf` (July 1995 revision),
  AN-0691 (a 68030 SONIC adapter), AN-0859 and AN-0877 (EISA SONIC boards)
  are on bitsavers too.
- `westernDigital/WD33C93A_SCSI_Bus_Controller_1991.pdf` (4,222,321 bytes,
  © 1991) and `westernDigital/79_000199_WDC_WD33C93A_SCSI_Bus_Interface_Controller.pdf`
  (3,594,215 bytes, undated) are other editions of the WD33C93A sheet.
- `sgs/_dataBooks/1994_SGS-THOMSON_Memory_Products_Databook_3rd_Ed.pdf`
  (later edition) and `1989_SGS-THOMSON_Zero_Power_Memories_Application_Notes.pdf`
  (2,113,433 bytes).
- `att/1993_ATT_Microelectronic_Products_Selection_Guide.pdf` (12,575,995
  bytes).  The text layer has no Hobbit, 9201x or CRISP entry.  Its
  "Mobile Personal Comm." section lists no Hobbit parts.  The OCR is poor, so
  a page-by-page image check would be needed to call this final.

## Not found

- **The board.** No manual, schematic or name survives online (README
  §The board).
- **The AT&T Hobbit companion chips (ATT92011 system management, 92012
  PCMCIA, 92013 ISA bridge, 92014 video).** Their data sheets existed: a
  BeBox history page cites them as December 1992.  No copy was found on
  bitsavers (`components/att/`, `components/att/hobbit/`), archive.org
  (metadata search) or by web search.  The kernel does not use them anyway
  (README §The board).
- **The "Bart's LCD" interface** (`io.h` `Lcdisp`).  It is a 768 x 1024,
  2-bit display fed one row-group at a time through two byte ports
  (`screen.c`).  No controller part is named anywhere in the release, and
  none was identified.
- **The keyboard.** It is serial, on a Quart port at 600 baud with odd parity
  (`kbd.c` `kbdinit`), and takes a "no click" command byte and LED bits back.
  No keyboard model or protocol document was found.  `deviic.c`'s header
  plans a later "keyboard and finger-mouse" on the IIC bus.
- **A 1990-1992 PCF8582(A) / PCF8584 data sheet** (see "Dates" above).
- **A Trident TGUI9420/9430 data sheet.**  Not on bitsavers
  (no `components/trident/`), no sheet on vgamuseum.info's TGUI9420DGi
  page (its Trident spec sheets found are for later parts: Blade, ProVidia),
  and none found by web search (2026-11-24).  VGADOC notes that Ferraro's *Programmer's Guide to the
  EGA, VGA and Super VGA Cards* (3rd ed.) documents "the accelerator
  registers at 21xAh"; that book was not found online.
- **AT&T DSP3210 Information Manual** (for the Hobbit BeBox's three DSPs,
  `../bebox_hardware.md` §13).  Not on bitsavers (`components/att/dsp/` has
  DSP16 and DSP32C material only).  Found later (2026-11-24) on GitHub, the
  September 1991 edition: it is listed, fetched and checked in
  `../dsp3210/MANIFEST.md`, and used in `../dsp3210.md`.
