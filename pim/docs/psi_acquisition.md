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
