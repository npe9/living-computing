# The PSI, KL0, ESP and SIMPOS: what survives (P0, 2026-11-23)

Rung P0 of `pimos_roadmap.md` section 9: an acquisition search, made
because the owner put the PSI and SIMPOS in the plan and then asked
for the whole operating environment. The search was done on
2026-11-23 by a delegated agent; this page is its report, checked
against the files it fetched (`nonlocal/LIT_MANIFEST.md`, addendum of
the same date). "Opened" below means the agent opened the page or
file and quotes it; the quotations are its, and the URLs are given so
that they can be checked.

**Result in one line: SIMPOS itself, an ESP compiler or runtime for
the PSI, and any PSI emulator were not found anywhere searched.** What
survives publicly is the PSI-III firmware as binaries (already held),
the console and front-end software as compiled ESP (held), ESP
application sources (held), two of the four SIMPOS/ESP manual
volumes (held), and some 120 reports and papers (64 ICOT reports and
27 IPSJ papers newly fetched).

## 1. SIMPOS

NOT FOUND, as source, binary, tape or disk image.

- ICOT Free Software: the README's directory map and the Waseda
  mirror's listing (`https://www.uedalab.jp/AITEC_ICOT_ARCHIVES/ICOT/ifs/`)
  show only applications "on SIMPOS". `symbolic-proc/pim-psi/` holds
  psdpim and PIMOS only.
- Searched with nothing relevant found: GitHub repository search,
  Internet Archive metadata search, bitsavers (`pdf/icot/` holds the
  FGCS'92 volumes only), the Wayback index of `icot.or.jp/*` (CESP
  notes and PSI-I/II museum pages only).
- `psdpim.tar.Z` (held; IFS item 3): its catalogue page says "Source
  Code: 2.5 MB", but the archive is binaries: `PMPSI.DIR/` (`pimm.MEkbn`,
  `syspsi`, `sysinit`, `sysidat`) and five `.ptf` SIMPOS "package
  template files" to be loaded "with the SIMPOS Librarian"
  (`pimmcsp`, `pimmutil`, `pimfep`, `mpsicspR`, `pimscsi`). Its README:
  "the PSI-III is commercially available as the PSI/UX from
  Mitsubishi Electric".
- 16 IFS applications in 19 archives are ESP source for SIMPOS;
  `kappa2` and `utter` also carry `.ptf` packages. `sam.tar.Z` (IFS 27)
  was never released (HTTP 404; its catalogue page links to "Sorry
  This Free SoftWare is now in preparation.").

## 2. ESP, Common ESP, KL0

- The ESP system for the PSI: NOT FOUND.
- Manuals: IFS `manuals/esp/` (held) has volumes 1 (Overview) and 3
  (Programming) of the four SIMPOS/ESP manual volumes; volumes 2
  (Operations) and 4 were not found.
- Reports, now held in `nonlocal/lit/trtm/`: TR-005, TR-044 (ESP
  Reference Manual), TR-285, TM-055, TM-134, TM-146, TM-364, TM-388
  (ESP Guide).
- Common ESP (CESP, ESP on UNIX): never in IFS; not found for download.
  Three statements, opened: a 1992 IFS newsletter ("distributed free
  of charge for academic use from AI Language Research Institute
  (AIR), Ltd.", on tape); the CMU mirror's `cesp.txt` ("CESP is not
  part of the ICOT Free Software"); `ifs/INFO.tar.Z` (1994: "available
  from MITSUBISHI ELECTRIC COMPUTER SYSTEMS(TOKYO) CORP.", Ver.3.3 for
  SunOS 4). The last is also an ESP-to-CESP conversion guide and
  records PSI specifics (built-ins `word`, `set_system_register`,
  `address` depend on "the PSI hardware (e.g., register, 40bits/word)").
- KL0: no standalone specification in the TR/TM lists. It is
  described piecemeal: TR-079 and the FGCS'84 micro-interpreter paper
  (PSI-I), TM-104, TM-444 and TM-661 (PSI-II instruction set).

## 3. PSI hardware documentation

Every TR/TM listed here is now held in `nonlocal/lit/trtm/` (page
scans, no text layer).

| Machine | Held | Depth |
|---|---|---|
| PSI-I | TM-001, TM-005, TR-013, TR-014, TR-045, TR-052, TR-075, TR-079, TR-142, TR-213, TR-219, TR-236, TR-274, TM-224; FGCS'84 hardware and micro-interpreter papers; a 1983 workshop paper (Nishikawa); Mitsubishi Denki Giho 60(9), 1986 | best documented |
| PSI-II | TR-265 (hardware architecture), TM-444, TM-661 (instruction set evaluation), TM-859 (memory architecture); IPSJ papers on memory and process management and a microprogram simulator "ZEUS" | adequate for the architecture; no microinstruction format |
| PSI-III (PSI/UX) | TR-714 (architecture, Japanese), TM-862 (summary of the ICCD'90 processor paper), TM-858 (40-bit microprocessor), TM-856 (cache); Giho 65(6), 1991 (PSI/UX series); IPSJ papers on the PIM/m element processor and the front-end processor | thin; **no microinstruction-format document found**; the ICOT museum has no PSI-III page |

TM-862, opened: "The microprocessor, called PU (Processing Unit), is
also used as a key component of AI workstations. Thus, PU has
capability to execute two different type logic programming languages,
KL1 for PIM/m and ESP for the AI workstation." That is: the PSI-III
and the PIM/m element processor are one chip, and the papers on
either describe both.

CITED-ONLY (paywalled, not fetched): New Generation Computing 1(1)
and 1(2), 1983; the SLP'87 PSI-II paper; the full ICCD'90 paper.

## 4. Emulators, microcode, surviving machines

- Emulator, simulator, FPGA or RTL of any PSI: NOT FOUND (English and
  Japanese web queries, GitHub, Internet Archive).
- Microcode: only the psdpim PSI-III binaries (held); their format is
  undocumented, and which file holds KL0 is not yet determined
  (`binary_reverse_engineering.md` section 5 has `syspsi` as the
  KL0/SIMPOS control store, from its size and INSTALL's wording).
  *Note 2026-11-23, to agree with that note: probable, not proven.
  What the files say: `README` calls `PMPSI.DIR` "KL0 and KL1
  firmware"; `boot.init` loads `pimm.MEkbn` as the KL1 `impl` file; and
  `INSTALL` copies `syspsi`, `sysinit` and `sysidat` to SIMPOS's
  `/usr/psi/simpos/csp`. So KL0 is in the `sys*` trio. What was
  measured: `syspsi` is 32,768 eight-byte records, a full 32K x 64-bit
  store, and its words `0..57ff` equal image 1 of `pimm.MEkbn`
  (`pseudo_pimm_microcode.md` §2); `sysidat` is the KL0 decode table
  (`binary_reverse_engineering.md` §4.2); `sysinit` is not
  characterised. No document names `syspsi`'s role. The CSP's micro
  loader read out of `pimmcsp.ptf`, or a PSI-III document, would
  settle it.*
  Nothing for PSI-I or PSI-II.
- Hardware: the JAIST Collection of Symbolic Processing Computers
  lists "PSI (ICOT)" and says "Related manuals and materials are also
  preserved" (`https://museum.ipsj.or.jp/en/satellite/JAIST.html`,
  opened); model and working state not stated.

## 5. SIMPOS documentation (now held)

ICOT reports on the supervisor, file system, window system and
network: TR-046, TR-055, TR-056, TR-057, TR-059, TR-061, TR-283,
TR-524, TM-009, TM-061, TM-065, TM-079, TM-100, TM-112, TM-115,
TM-125, TM-126, TM-143, TM-161, TM-181, TM-229, TM-401, TM-785,
TM-786. IPSJ: the "SIMPOS programming environment" series and papers
on TELNET, FTP and remote objects (`nonlocal/lit/ipsj/`, on disk
only). On the front-end and console processor: IPSJ 122850 (PIM/m
maintenance architecture and the console processor), TR-237, TM-306,
TM-696. Not found: a SIMPOS class-library reference.

## 6. Leads (not facts)

Where SIMPOS, the ESP system or PSI media might survive, none of
which was contacted: Mitsubishi Electric (Kamakura/Ofuna laboratories,
maker of PSI-II and PSI/UX); the successors of AIR and of Mitsubishi
Electric Computer Systems (CESP); university tape copies of CESP; the
JAIST collection (manuals and media); the authors (ESP and SIMPOS were
Chikayama's group); the JIPDEC archive team and the Waseda laboratory
that keeps the mirror; Oki Electric (PSI-I and an Oki PSI-II). The
printed TR/TM are at the National Diet Library and the Kanagawa
Prefectural Kawasaki Library. No statement was found on where ICOT's
non-free materials went. Contacting anyone is outside the repository
and needs the owner.

## 7. Not searched

Software Heritage (its API returned no JSON to an anonymous client);
the Kyoto, Tokyo, Keio and KEK mirrors; Oki's technical review and
theses; the Wayback index beyond `icot.or.jp/*` and the first 600
URLs of `ftp.icot.or.jp` (the domain-wide query returned 504).

## 8. What it means for P1..P5

There is nothing to boot. P1 (the microinstruction format) rests on
the held control store, `sysidat`, TR-714, TM-862, TM-858 and the
PIM/m processor papers, since the PIM/m element processor and the
PSI-III are the same chip; reading the format is reverse engineering,
not transcription. P4 (SIMPOS) cannot be reached with what is public:
it needs media from one of the holders in section 6, or a
reconstruction of the SIMPOS classes the held `.ptf` files call, from
the manuals and reports above (roadmap section 9).

## 9. The SIMPOS-only search (2026-11-23, second pass)

Made because the owner asked for more on SIMPOS. Delegated, like
section 1-8's search; its working notes are `simpos/source_notes.md`
(page by page, opened versus only located), its outputs
`simpos/required/old_regex_census.tsv (superseded by simpos/required/)` and `simpos/trtm_table.tsv`.

**SIMPOS itself: still NOT FOUND** (no source, binary, tape, disk
image or emulator). What it adds:

- **SIMPOS source printed in ICOT reports** (opened; PDF page
  indices): TM-100 pp4-17, the supervisor's own classes (`process`
  with its whole attribute list and `:create`, `as_program`,
  `interrupt_process`, `channel`, `bounded_channel`); TR-524 pp37-38,
  the distributed file system's classes with method bodies, p21 its
  remote-call protocol; TR-046 pp27-28 and TR-061 p13, the
  Coordinator's `default_translation_table` and `system_menu`; TR-056
  p13, p21-22 (streams, semaphores, events, `boot_process`, library
  and directory slots); TR-059 p12, p22 (buffers, `as_permanent_object`);
  TM-065 pp12-16 (file and window class skeletons); TM-125 p17 (window
  graphics methods). Not described anywhere found: the `.ptf` package
  format, the boot image, the disk format.
- **The interface the applications use**: a census of the 1,351 ESP
  files of the held IFS SIMPOS applications (`simpos/required/old_regex_census.tsv (superseded by simpos/required/)`):
  about 300 classes used and not defined there, each with the methods
  called (`symbolizer`, `library`, `process`, `directory`, `pathname`,
  windows, menus, ...). By pattern, so a few entries may be
  application classes. With the reports above, this is the
  specification a reconstruction of SIMPOS's classes would be built
  to; it is usage, not a definition, and is labelled so.
- **Librarian practice**: 55 Librarian command files in the IFS
  applications (`make_environment(E,[simpos])`, `make_package`,
  `save_package`, `use_package`, `fxds`), a complete login file
  (`gog-esp/login.com`), TM-785 p3's install-from-floppy session.
- **Versions**: 1.5 (1985), 2.19 (TM-181 screenshot), 3.0 to 7.1 and
  "6.2 OKI-PSI-II" (IFS READMEs), "SIMPOS II B00" for PSI-II (Giho
  63(7), 1989), "PSI-III and SIMPOS A22" (`kappa2`).
- **Moving pictures**: the ICOT museum's PSI video, seven segments;
  `simpos.wmv` shows SIMPOS's structure and its system menu on a real
  screen (Execute, debugger, editor, file_manipulator, librarian,
  spooler, font_editor). On disk only.
- **Every ICOT TR/TM on SIMPOS, ESP or the PSI is now held**: of 135
  title matches, 87 are related; 67 were held, 20 more fetched today
  (with 9 PSI-keyword rows, 29 files: `simpos/trtm_table.tsv`); none
  unavailable.

**Who holds manuals** (CiNii Books, opened): the JAIST library, call
number C42.4, one copy each: SIMPOS使用説明書 (MP3001-1, 1985.4),
SIMPOS操作説明書 (MP3002-1, 1985.4), SIMPOS 1.5版 changes
(SIM-I-U-GEN021, 1985.9), KL0組込述語説明書 2nd ed. (MP7002-1,
1985.4), CSP操作説明書 (MP7003-1, 1985.4): the PSI-I system's user
and operations manuals, the KL0 built-in predicate manual and the
console processor's, in the institution that keeps a PSI. No ESP,
PSI-II or PSI/UX product manual is in CiNii; the NDL refused several
queries (HTTP 429): not searched, not negative. WorldCat not searched.

**Leads added** (not contacted): JAIST (manuals and machine together);
Argonne and Lawrence Berkeley, which each received a pair of PSI-II
(an NIH grant record, Z01-CT000237-01: "installed two of the PSI-II
... in October 1990. Similar pairs of machines have been installed at
Argonne ... and Lawrence Berkeley"; ICOT Journal No. 30, 1991, "The
Struggle to Installing PSIs at Argonne"); Oki (an Oki PSI-II ran
SIMPOS 6.2); Mitsubishi's PSI/UX 350 and 400 (B2150, B2151; Giho
1991-03 p107).

For P4 this changes the method, not the verdict: SIMPOS cannot be
booted from anything public, but its supervisor, file and window
classes are partly printed, and the classes the surviving
applications call are now listed, so a reconstruction can be built
against both and tested by running those applications. Media remain
the better path, and the JAIST manuals are the nearest known primary
source.

## 10. The second broad search (2026-11-23): the PSI microinstruction formats

A delegated search of places sections 1-9 did not reach (Software
Heritage, the whole Wayback index of the ICOT hosts, the CMU AI
Repository walked whole, code hosts, Japanese and foreign mirrors,
university repositories, vendor journals). Its one primary find:

- **Hiroshi Nakashima's doctoral thesis**, 論理型言語向きプロセッサの
  アーキテクチャに関する研究 (Kyoto University, 1991; KURENAI
  hdl:2433/168749, open access; `nonlocal/lit/theses/`, on disk
  only). Chapter 3 is the PSI-I, PSI-II and PSI-III: instructions,
  tags, memory and the **microinstruction architecture**. By the
  agent's reading of the page images: Fig. 3-11 (printed p.74) the
  PSI-I microword, 63 bits; Fig. 3-19 (p.113) the PSI-II, 53 bits;
  Fig. 3-25 (p.143) the PSI-III, 64 bits, field by field (DBGF, CCF,
  WRBF, DSTF, SC1F, SC2F, SD1F, SD2F, ADF, AS1F, AS2F, ALF, JMPF, CNDF,
  MCF, TGIF, EM1-3), each with its width and explained in the text.
  The thesis's own text layer confirms the field names (TYPF, EM1,
  WRBF, MCF, TGIF and the 2-bit TYPF interpretation of PSI-I); the
  figures' widths are not yet read by the project itself. Appendix A
  is ESP/KL0 (not opened).

So section 3's "no microinstruction-format document found" is
**corrected: found, a primary source, for all three PSIs**. Since the
PSI-III and the PIM/m element processor are one chip (TM-862), it is
the strongest document for P1 and for the PIM/m microword; checking it
against the held `syspsi` control store is the next step.

Also fetched (on disk only, no redistribution terms stated): four IPSJ
papers on IP1704, the PIM/k element chip (wanted by
`literature_gaps.md`); K. Ohno's 1998 Kyoto thesis on KL1 static
analysis; the summary of Rokusawa's 1998 Waseda thesis; Mitsubishi
Denki Giho 1988-05, 1988-10 (MELCOM PSI II, ESP, SIMPOS) and 1989-01.
CITED-ONLY at the NDL (library access): theses by K. Nakajima (Kyoto
1996, KL1 on Multi-PSI and PIM/m), Y. Kimura (Tokyo 1993), K. Shimada
(Tokyo 1993), K. Hirata, Hidaka, Naganuma.

Negative (queries in the search's log): no `ifs/` file, no
`pimm_patch.com` and no FTP capture among all 1,180 Wayback URLs of
`ftp.icot.or.jp`; nothing new among 37,619 URLs of `icot.or.jp`; the CMU
copy of ICOT's software is the same 1995 tree as held (audit §5 item
11 closed); `air.co.jp` was another company from its first capture
(1998), so the CESP distributor's site is not there; Software
Heritage, GitLab, SourceForge, the OSDN mirror, Ring Server, some 34
mirrors, Hitachi Hyoron 1985-95 (no PIM/c article): nothing.
Refused or not searched: HathiTrust, scholar.archive.org, Codeberg,
SourceHut, Usenet, Oki Technical Review, FUJITSU magazine.

## 11. The PSI microwords read, and tested on the held stores (2026-11-23)

From Nakashima's thesis (section 10), read from the page images
(`psi_microword.md`; PDF page n = printed pages 2n-8, 2n-7; bit
positions assume the leftmost field is the high bit, the figures
print widths only, no code values):

- PSI-I, Fig. 3-11 (p.74): 63 bits, a 43-bit basic part and a 20-bit
  part of three types chosen by TYPF.
- PSI-II, Fig. 3-19 (p.113): 53 bits (DBGF 1, CCF 4, TYPF 3, DSTF 7,
  SC1F 6, ALF 2, SC2F 6, JMPF 3, CNDF 7, EM1 6, EM2 4, EM3 4); Table
  3-5 the emit fields. Open: p.116's text and the figure disagree on
  SC1F.
- PSI-III, Fig. 3-25 (p.143): 64 bits: DBGF 1 (63), CCF 5 (62-58),
  WRBF 1 (57), DSTF 5, SC1F 5, SC2F 5, SD1F 3 (41-39), SD2F 2, ADF 3
  (36-34), AS1F 3 (33-31), AS2F 2 (30-29), ALF 2 (28-27), JMPF 4
  (26-23), CNDF 4 (22-19), MCF 1 (18), TGIF 2 (17-16), EM1 6, EM2 6,
  EM3 4. Also the nanocode, Fig. 3-22 (p.127), 50 bits; and the
  PSI-III's pipeline (five stages, 60 ns), WCS 64 bits x 32 Kw, caches,
  TLBs, register files (section 3.3). Tag and word widths are not given.
- Section 3.4: PIM/m uses the PSI-III CPU; up to 256 PEs of 16 Mw, 32
  a cabinet; the FEP on SCSI with a 600 MB disk per 8 PEs.

Tested (MEASURED, scripts in `asm/psi_microword/`): `syspsi` and the
KL1 image in `pimm.MEkbn` are 64-bit little-endian words that read
consistently under the thesis's PSI-III layout and worse under TR-733
fig. 4's, which `asm/mekbn.py` uses: the two differ in bits 36..23,
and the measurements favour the thesis there (bit 26 in the jump
field, ALF 2 bits with EM2 the operation, ADF/AS1F/AS2F at
36-34/33-31/30-29). TR-733 prints ALF 3 and JMPF 3, so the documents
conflict as printed. `sysidat` is not microcode but a decode table:
471 of 471 start addresses land on code in `syspsi` (baseline 74.5%).
`sysinit` is mostly text and data. Strength: strong for bit 26, ALF
and bits 36-29; moderate for MCF, TGIF, DBGF; code values only from
`rassy`. Next: move `mekbn.py`'s FIELDS to this layout and rerun its
`--check`. *Done 2026-11-23 (`psi_microword.md` section 7): FIELDS
follow Fig. 3-25; `--check` passes, with `xr_pass`,
`base_plus_constant`, `sc2_other_branches` (both images), one record
cell and `img2_page_relative` re-pinned and new layout pins added. 4-bit JMPF 2 turned out not to be page-relative,
and ALF 2/3 (EM2 the operation) occurs with a branch that needs EM2 in
1 of 3,063 words of `syspsi` and 0 of 1,803 of the KL1 image (about
1,265 and 732 by chance).*

Appendix A (pp.237-263) is the ESP object model and KL0 execution
control (exceptions, remote cut, `on_backtrack`, `bind_hook`), not an
instruction list; Appendix C (pp.278-285) a WAM instruction list.
