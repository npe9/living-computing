# Search of places with files for SIMPOS, ESP and Common ESP software (2026-11-24, second file search)

A delegated search, made after `web_search_2026-11-24.md`, `web_search2_2026-11-24.md`,
`sweep_2026-11-24.md`, `fixpoint_2026-11-24.md`, `../../psi_acquisition.md` and
`../../archive_search_notes.md`. Those covered GitHub *repository* search, Wayback CDX of many
Japanese FTP hosts, the CHM catalogue, CiNii, NDL, IPSJ, KAKEN and the held IFS archives, and are
not repeated. This search went to places that hold **files**: code search engines, code forges,
Software Heritage, live and archived FTP mirrors, archive.org's software, CD-ROM and full-text
search, Discmaster, Usenet archives, and the KLIC, KL1 and PDSS distributions still published.

All accesses were on 2026-11-24 (US Eastern; the logs' UTC stamps read 2026-11-25T00:46Z to
01:25Z). Nobody was contacted. Nothing was bought, no form was submitted, no terms were accepted
and no bot challenge was bypassed. No query carried personal data. Every download went into its own
new directory in the session scratch space, was read with `grep` or `python3 -I`, and was not
executed. Nothing downloaded is kept: no file is added to `../../nonlocal/lit/`.

> **FOUND: nothing.** No SIMPOS, ESP or CESP source, binary, tape image or disk image was found in
> any place searched. No ICOT Free Software or AITEC CD-ROM image is on archive.org or Discmaster.
> Every hit that carries ESP or SIMPOS material is a copy of something already held (the CMU AI
> Repository's ICOT area, which is the IFS tree), or a printed description already cited.

## How each engine was checked first (positive controls)

A zero from an engine counts only if that engine returned something known that day.

| engine | control | result |
|---|---|---|
| GitHub code search (REST `search/code`, via `gh api`) | `as_class_with_lock` | 21 hits, all in this repository's `pim/` (stand-in and census files): the index covers this public repository |
| Sourcegraph public stream API | `repo:^github\.com/golang/go$ file:README` | 66 hits. But `as_class_with_lock` and `standard_io_window`, which are in this repository, gave 0: Sourcegraph.com does not index this repository, so its index is a small subset of GitHub. Its negatives are weak |
| Wayback CDX | `ftp.icot.or.jp`, whole domain | 1,180 URLs, the count `../../psi_acquisition.md` §10 recorded; `ftp.ring.gr.jp` 33,455 URLs, the count `web_search2_2026-11-24.md` recorded |
| archive.org full-text search (`services/search/beta/page_production`, backend `fts`) | `"Kowalski logic for problem solving"` | 341 hits, all real citations |
| archive.org advanced search | `simpos` | 9 hits, among them the CIA reading-room false positives and a 1987 parts catalogue: the engine works, the term is rare |
| Software Heritage origin search | `simpos` | HTTP 200, 435 origins, no challenge this time |

## Results by place

Each row gives the queries, the result and the grade: **NOTHING** (searched, no relevant file),
**UNREACHABLE** (not searched, with the reason), or a pointer to the leads below.

### 1. Code search

| place | queries | result | grade |
|---|---|---|---|
| **GitHub code search** (57 queries; logs `gh.log`, `gh3.log` in scratch) | Identifiers that occur only in SIMPOS or ESP: `library_utility`, `librarian_read_term`, `librarian_class_generator`, `standard_io_window`, `popup_standard_io_window`, `standard_superior_window`, `standard_scrolling_menu`, `pimos_window_editor`, `pmacs_window`, `monogyny_hash_index`, `as_pimos_string_io_device`, `class_with_lock`, `as_class_with_lock`, `esp_macro_expander`, `emacs_window emacs_io_buffer`, `standard_io_buffer`, `tcpip_mail_receiver`, `symbolizer get_atom`, `e_string nonspace`, `pathname last_name get_last`, `list_index hash_index nature`, `as_resource as_program`, `as_program nature`. Path stamps and hosts: `simpos7D`, `icpsi`, `mkpsi000`, `M-KONDOH`, `simpos##`, `pimfep`, `mpsicsp`, `lversion lib50`. File types: `extension:esp` with `nature`, `symbolizer`, `instance attribute`, `library_utility`, `class_object`; `extension:kl0`, `extension:ptf`. Words: `simpos`, `SIMPOS ESP`, `SIMPOS ICOT`, `Common ESP`, `CESP librarian`, `CESP AIR`, `ICOT ESP PSI`, `KL0 PSI`, `KL0 ESP`, `PSI-II SIMPOS`, `PSI/UX`, `Pmacs`, `ESP言語`, `逐次型推論マシン`, `make_environment simpos`, `use_package simpos`, `save_package make_package`, `librarian catalogue esp` | Every hit on a SIMPOS identifier, path stamp or `.esp` query is in this repository. The only other ICOT-related hits are `ashok-khanna/cmu-ai-repository` (`areas/icot/symbolic/pim_psi/psdpim.html`, `areas/icot/readme*.txt`), a mirror of the CMU AI Repository (row 2 below). The word queries hit Spanish "simposio", ESP32 firmware and word lists. `has nature` and `Common ESP` are too common to use | NOTHING |
| GitHub code search, limits | The REST code search drops punctuation, so `>sys>simpos`, `:create(#` and `simpos##` reduce to their words. It searches default branches only and skips large files | Exact-punctuation search needs the web UI with a login: lead L1 | (lead) |
| **Sourcegraph** (public stream API; log `sg.log`, `sg2.log`) | `">sys>simpos"`, `"simpos##"`, `":create(#"`, `as_class_with_lock`, `library_utility nature`, `standard_io_window`, `"::>sys>"`, `"has nature"`, `pmacs_window`, `icpsi`, `"#symbolizer"`, `file:\.esp$ "instance attribute"`, `file:\.esp$ nature`, `file:\.kl0$`, `file:\.ptf$`, `CESP librarian`, `"Common ESP"`, `monogyny_hash_index`, `file:\.kl1$ "module"` | 0 hits except `icpsi` (106, Go `go.sum` hashes and C++ `gicp`) and `.ptf` (67, unrelated formats in electronics, bioinformatics and Panda3D repositories). The control above shows the index is narrow | NOTHING (weak) |

### 2. Code forges and repository archives

| place | queries | result | grade |
|---|---|---|---|
| **GitHub repository search** (new terms only) | `klic`, `kl1`, `pdss`, `icot`, `fifth generation computer`, `esp prolog`, `pimos`, `psi prolog`, `multi-psi`, `guarded horn clauses` | Two ICOT-derived repositories, both read: (a) **`GunterMueller/KLIC`** ("Forked from" the Waseda KLIC page; 6,649 tree entries, read through the API): KLIC 3.01 unpacked, plus `SOURCES/` with `klic-3.005-extio-shared.tar.gz`, `klic-3.01.tgz`, `klic-3.011.tgz`, `klic-3.013.tgz` and `klic-3.014.tgz` (26 MB each), `ghcsystem-swi.tgz` and `klint-v22.tgz`. No path names ESP, SIMPOS, PSI, KL0, CESP, PDSS or PIMOS. KLIC is a UNIX KL1 system and carries no ESP. The same owner's ~600 repositories include many Prologs and no other ICOT system. (b) **`ashok-khanna/cmu-ai-repository`** (mirror of the CMU AI Repository, 72,583 tree entries): its `areas/icot/` holds 1,150 entries, the 8.3-named copies of the IFS archives (`apps/simpos/gog_esp.gz`, `kbms_clp/simpos/kappa2*.gz`, `nlp/simpos/cil.gz`, `manuals/esp/esptex.gz`, ...), `cesp.txt` and `info.gz`. This is the CMU copy `../../psi_acquisition.md` §10 already found to be the held 1995 tree. Every name checked against `../../nonlocal/IFS_MANIFEST.md` is held (for example `kwic_esp/kwice002.gz` is the held `kwic-esp-002.tar.Z`). Also seen and not ICOT: `CesarBallardini/kl1c`, `suharahiromichi/kl1` (a 4 KB GHC example) | NOTHING new |
| **GitLab** project API (anonymous) | `simpos`, `common esp`, `cesp`, `icot`, `klic`, `kl1`, `pimos`, `pdss`, `esp prolog`, `fifth generation` | HTTP 200. Only unrelated projects: simposio sites, ESP32, `ovf/fleng` (FLENG, a modern GHC-family language, not ICOT's) | NOTHING |
| GitLab code (blob) search | `library_utility`, `standard_io_window`, `simpos` | HTTP 401: needs a signed-in user | UNREACHABLE (lead L2) |
| **Codeberg** API | the same ten words; `library_utility`, `standard_io_window` | HTTP 429 on every request: "Search and filtering is seeing a high influx of requests ... your search request will not be processed" | UNREACHABLE (rate-limited) |
| **Bitbucket** | `simpos`, `icot`, `klic` | No anonymous search API (HTTP 404, "There is no API hosted at this URL"). Bitbucket repository names were covered only through Software Heritage's origin list (next row) | UNREACHABLE (no API) |
| **Software Heritage** origin search (no challenge this time) | `simpos`, `cesp`, `icot`, `klic`, `kl1`, `pdss`, `pimos`, `kl0`, `fifth-generation`, `fgcs`, `esp-prolog`, `psi-ux`, `aitec` (13 queries, up to 1,000 origins each) | 3 to 649 origins per term, all substring noise (`simposio`, `cespedes`, `klicky`, `nicotine`, `aitech`, Bitbucket `icoteq-eng`). The only ICOT-derived origin is `code.launchpad.net/~ubuntu-branches/ubuntu/intrepid/klic/intrepid`, Ubuntu's packaging of KLIC (no ESP). Software Heritage has no anonymous search by file content, so files inside archived repositories were not searched | NOTHING (origin names only) |
| **SourceForge** directory search | `simpos`, `klic`, `kl1`, `esp prolog`, `icot`, `pdss`, `guarded horn` | HTTP 404 (no results) or unrelated projects (`b4udignl`, `retavortaro`, `poggpl`); `/projects/klic/` 404 | NOTHING |
| **OSDN** | `osdn.net/search/?q=kl1`, `/projects/klic/`, `ja.osdn.net/search/?q=ESP+Prolog` | No connection (curl status 000; the site is offline) | UNREACHABLE |
| OSDN and SourceForge.jp file mirrors at JAIST | `https://ftp.jaist.ac.jp/pub/osdn.net/` and `/pub/sourceforge.jp/` listed whole (3,535 project directories each) | No project named for KLIC, KL1, KL0, ICOT, ESP, SIMPOS, Prolog, PSI, PIMOS, PDSS, GHC or FGCS (the regex matched only `esperanzalinux`, `whitespacejs` and similar) | NOTHING |

### 3. Mirrors, at the path level

| place | what | result | grade |
|---|---|---|---|
| Live mirrors: `ftp.jaist.ac.jp`, `ftp.iij.ad.jp`, `ftp.ring.gr.jp`, `www.ring.gr.jp`, `ftp.riken.jp`, `ftp.kddilabs.jp`, `ftp.tsukuba.wide.ad.jp`, `ftp.yz.yamagata-u.ac.jp`, `ftp.sra.co.jp`, `ftp.u-aizu.ac.jp`, `ftp.nara.wide.ad.jp` | the paths `/pub/icot/`, `/pub/ifs/`, `/pub/lang/prolog/`, `/pub/esp/`, `/pub/cesp/`, `/pub/lang/esp/`, `/pub/klic/`, `/pub/lang/klic/`, `/pub/misc/icot/`, `/pub/ICOT/`, `/pub/AI/`, `/pub/ai/`; and the top-level listings | 144 probes. The eight hosts that answered (`ftp.jaist.ac.jp`, `ftp.iij.ad.jp`, `ftp.ring.gr.jp`, `www.ring.gr.jp`, `ftp.riken.jp`, `ftp.tsukuba.wide.ad.jp` by HTTP and HTTPS, `ftp.yz.yamagata-u.ac.jp`) gave HTTP 404 for all twelve paths, 96 in all. The same servers served real listings that day (for example JAIST `/pub/osdn.net/`; the `/pub/lang/` listings of IIJ (perl, ruby), Ring (egcs, perl, ruby) and Yamagata (CPAN only)), so the 404s are real. `ftp.kddilabs.jp`, `ftp.sra.co.jp`, `ftp.u-aizu.ac.jp` and `ftp.nara.wide.ad.jp` did not connect (URLError, 48 probes) | NOTHING (8 hosts); UNREACHABLE (4 hosts, no connection) |
| Wayback CDX, whole domains not queried before (log `cdx.log`, `cdx2.log`) | Every capture's URL tested against a regex for `simpos`, `cesp`, `/esp/`, `icot`, `kl0`/`kl1`, `psi-ii`/`iii`/`ux`, `/ifs/`, `melcom`, `multi-psi`, `pdss`, `klic`, `pimos`, `aitec`. The first run's regex matched bare `icot` and was noisy ("apricot", "nicotine"); the second run used word boundaries | 35 hosts. **First run** (URL counts): `ftp.nuie.nagoya-u.ac.jp` 4, `ftp.kddlabs.co.jp` 164, `ftp.center.osaka-u.ac.jp` 8, `ftp.sfc.keio.ac.jp` 0, `ftp.csl.sony.co.jp` 2,750, `ftp.cs.kyoto-u.ac.jp` 0, `ftp.kuis.kyoto-u.ac.jp` 5, `ftp.is.titech.ac.jp` 1,509, `ftp.ipl.t.u-tokyo.ac.jp` 441, `ftp.cs.cmu.edu` 496, `sunsite.unc.edu` 119,095, `ftp.uni-koeln.de` 52,302, `ftp.sics.se` 314, `ftp.dnai.com` 1, `ftp.tut.ac.jp` 0, `ftp.hokudai.ac.jp` 0, `ftp.kyushu-u.ac.jp` 1,413, `ftp.cc.u-tokyo.ac.jp` 0, `ftp.ecei.tohoku.ac.jp` 0, `ftp.jp.netbsd.org` 8,641, `ftp.riken.go.jp` 200,000 (the query limit), `ftp.fujitsu.co.jp` 3,397, `mitsubishielectric.co.jp` 200,001 (the limit; stylesheet captures), `uedalab.jp` 613, `ueda.info.waseda.ac.jp` 59,547. **Second run**: `ftp.waseda.ac.jp` 0, `oki.co.jp` 11,020, `ftp.ae.keio.ac.jp` 0, `ftp.ntt.jp` 0, `ftp.funet.fi` 300,000 (the limit), `ftp.aist.go.jp` 0, `osdn.net` 300,000 (the limit), `osdn.jp` 300,000 (the limit), `sourceforge.jp` 300,000 (the limit), `melco.co.jp` 105,691 (`uedalab.jp` answered 503 this time; its first-run list stands). Hits read: `ftp.funet.fi` 2 (Slackware `klickety`); `osdn.net` 8 (CVS project `cjklicht`); `osdn.jp` 7 and `sourceforge.jp` 2 (`klick` projects, and `sfnet_simpos`, whose archived page (2015-07-10) is a 2010 Python project `simpos.py`, renamed PySimp: not SIMPOS); first-run hits were substring noise or the ICOT museum pages. `ueda.info.waseda.ac.jp` holds the AITEC/ICOT archive mirror: 1,234 regex hits, of which 8 URLs are under `ICOT/ifs/` or `ICOT/Free-Software/` (`pimos.tar.Z`, `pimosobj.tar.Z`, `pimosman.tar.Z`, `pimosman.ps.Z`, helic2 `cui.tgz` and `beginer-j`, KLIC `tutorial.tex`), each listed in `../../nonlocal/IFS_MANIFEST.md`; the rest are Museum and AITEC Report pages. Hosts at the limit were searched only up to it | NOTHING (31 hosts with captures or none); limits noted |

### 4. archive.org

| place | queries | result | grade |
|---|---|---|---|
| **Advanced (metadata) search** | `simpos`, `"common esp"`, `cesp`, `icot`, `逐次型推論マシン`, `kl0`, `"melcom psi"`, `aitec`, `klic`, `第五世代コンピュータ`, `"fifth generation" AND mediatype:software`, `"新世代コンピュータ"`, `"prime time freeware"`, `title:(ICOT)`, `subject:(ICOT)`, and title searches for bit, Interface, 情報処理, 日経エレクトロニクス and 月刊プログラマーズ | **No software or CD-ROM item for ICOT, IFS, AITEC, KLIC, SIMPOS, ESP or CESP.** The ICOT items are bitsavers scans of the FGCS'92 proceedings (`bitsavers_icotFifthGstems1992Volume2_67051359` and its companion volume), which are printed documents; the other `title:(ICOT)` hits are a hearing-aid company's court cases and an unrelated "ICOT" classroom tool. `"prime time freeware"`: the book scan `primetimefreewar0000unse` (the printed index of Prime Time Freeware for AI 1-1, a 1994 CD of the CMU AI Repository) is on archive.org; **the CD itself is not** (only Prime Time Freeware for UNIX 3-1, `PTF-F4U31`, is). Its ICOT content would be the CMU tree already held. Interface magazine is present only as 2003-2006 CD-ROM editions; bit, 情報処理 and 日経エレクトロニクス are not on archive.org as issues | NOTHING |
| **Full-text search** (OCR text of scanned items; logs `iafts*.log`, `fts_simpos_all.log`) | `SIMPOS` (all 1,373 hits paged through), `"Common ESP" ICOT` (192), `"Common ESP"`, `SIMPOS ESP class nature` (0), `"逐次型推論マシン"` (0; the OCR of Japanese is split by spaces), `PSI SIMPOS ESP 推論` (3), `library_utility` (2,812, all CDC, IBM ISPF and DEC "library utility"), `standard_io_window` (0), `"standard_superior_window"` (0), `"KL0" PSI`, `"ESPerへの道"` (0), `"MELCOM PSI"` (29), `"ICOT Free Software"` (20), `AITEC ICOT CD-ROM` (0), `CESP "AI言語研究所"` (0) | **No ESP listing.** The relevant hits are printed descriptions: BYTE 1985-04, Electronics Week 1984, I/O 1985-02, ASCII 1984-08 and 月刊プログラマーズ・ページ 1991-03 (Japanese magazines; their OCR text was downloaded and read around each hit: overviews of PSI, KL0, ESP and SIMPOS, no code), ICLP'86 and MFCS'86 proceedings (lending-library items, lead L3), and Fujitsu Sci. Tech. J. 26(1) 1990 (ExReps on PSI-II, with SIMPOS 4.2 screens; already cited in `window.md` §1). `"ICOT Free Software"` finds only the IPADIC licence text in third-party manuals | NOTHING (documents only) |
| **Discmaster** (file-name search over about 50,000 CD-ROM and archive images; log `dm.log`) | `icot`, `pimos`, `kl1`, `klic`, `pdss`, `simpos`, `esptex`, `kappa2`, `gog_esp`, `cal_esp`, `psdpim` | No ICOT Free Software disc. ICOT-related files: FreeBSD 5.x ports `lang/pdss` (the PDSS port; PDSS is held) and the Kahaner reports `ftp.cs.arizona.edu/japan/savekahaner.reports/icot*` (five ONR text reports on ICOT, 1991-94, read: narrative only, for example "Some 500 PSIs" and "SIMPOS ... is written solely in ESP"). Everything else is substring noise (Scilab `icot.sci`, a game's `icot_*` actors, `KAPPA2.EXE`) | NOTHING |

### 5. Usenet

| place | what | result | grade |
|---|---|---|---|
| **Utzoo (Wiseman) archive** on archive.org | item `utzoo-wiseman-usenet-archive` | Its description says the archive "has been removed from this URL and is not currently accessible to the public" (2020); only a listing and checksums remain | UNREACHABLE (withdrawn) |
| `FULL-USENET-BACKUP-2020-Oct-comp.lang.prolog` (10,498,866-byte 7z; downloaded, unpacked with `bsdtar`, 24,970 messages) | regex for SIMPOS, Common ESP, CESP, `air.co.jp`, `library_utility`, `standard_io_window`, PSI-II, PSI/UX, MELCOM | 0 hits. The messages date from 1995 on, almost all 2003-2020, so the 1987-94 traffic searched by `web_search2_2026-11-24.md` (IA `usenet-comp`) is not in it | NOTHING |
| giganews `usenet-comp.sources` (25 mbox files, 8.4 MB; downloaded) and `usenet-net.sources` (16 KB) | the same regex plus `icot`, `kl0` | 3,705 messages, 2002 on; no hit except spam and header noise | NOTHING |
| fj.* (`usenet-fj`, `ancientfj-2004-10-18`, `gna-fj`), comp.lang.prolog and comp.object.logic (`usenet-comp`) | | Already searched by `web_search2_2026-11-24.md`; not repeated. Ring Server also mirrors `ancientfj` at `/pub/misc/ancientfj/` (seen in its listing; presumed the same collection, not re-read) | (done before) |

### 6. KLIC, KL1 and PDSS distributions still published

| place | result | grade |
|---|---|---|
| `GunterMueller/KLIC` on GitHub (KLIC 3.005-3.014) | no ESP, SIMPOS or PSI file (row 2) | NOTHING |
| Ubuntu `klic` packaging (Launchpad, via Software Heritage) | KLIC only | NOTHING |
| FreeBSD ports `lang/pdss` (seen on CD images in Discmaster) | a port of PDSS, which is held (`../../nonlocal/pdss.tar.Z`) | NOTHING |
| the CMU AI Repository's `areas/icot/symbolic/unix/klic/` (klic1000, klic1100, klic1210, klic1410) | KLIC 1.x; UNIX only | NOTHING |

KLIC and PDSS are KL1 systems for UNIX. None of the copies found carries ESP, a PSI tool or
SIMPOS material, so they add nothing for SIMPOS.

## Leads for the owner

None is a known software archive. Each is a place where a search could not be completed without an
account or a person.

- **L1. GitHub's web code search** (needs a signed-in browser session). It matches punctuation and
  regular expressions, which the API does not. Queries to run: `">sys>simpos"`,
  `"simpos##"`, `/::>sys>[a-z]/`, `":create(#"` with `nature`, `/class [a-z_]+ has\s+nature/`,
  `"library_utility" NOT repo:<this repository>`, `path:*.esp nature instance`.
- **L2. GitLab blob search** (needs a GitLab account): `library_utility`, `standard_io_window`,
  `simpos##`, `as_class_with_lock`.
- **L3. Two archive.org lending-library books** (borrowing needs an archive.org account):
  `isbn_3540167838` (MFCS'86 proceedings; its OCR shows a PSI screen with
  "CAP_LA SIMPOS Version 2.20 02-May-86", Fig. 14, an application paper) and
  `thirdinternation0225inte_m8r5` (ICLP'86 proceedings; a paper on ESP and SIMPOS). Printed papers,
  not code; worth reading for screens only.
- **L4. Codeberg** answered HTTP 429 to every anonymous request. A retry later, or a signed-in
  search, would close it.
- **L5. Prime Time Freeware for AI, Issue 1-1** (1994 CD-ROM of the CMU AI Repository). The disc is
  not on archive.org. If a copy turns up it would carry the CMU ICOT area, already held, so it is
  listed only for completeness.

The earlier leads (CESP recipient sites, Mitsubishi Electric's IT group, JAIST, NDL) stand as
recorded in `fixpoint_2026-11-24.md` §4.

## Places with nothing

Fifteen places returned nothing new:
1. GitHub code search
2. GitHub repository search (new terms)
3. Sourcegraph (weak; narrow index)
4. GitLab project search
5. Software Heritage origin search
6. SourceForge
7. the OSDN and SourceForge.jp mirrors at JAIST
8. eight live Japanese mirrors (path probe)
9. Wayback CDX of 35 hosts
10. archive.org metadata search
11. archive.org full-text search
12. Discmaster
13. the 2020 comp.lang.prolog Usenet backup
14. giganews comp.sources and net.sources
15. the KLIC, KL1 and PDSS distributions

Unreachable:
- GitLab code search (login)
- Codeberg (HTTP 429)
- Bitbucket (no anonymous search API)
- OSDN (offline)
- the Utzoo archive (withdrawn)
- four live mirrors (`ftp.kddilabs.jp`, `ftp.sra.co.jp`, `ftp.u-aizu.ac.jp`, `ftp.nara.wide.ad.jp`; no connection)

## Downloads (scratch only, not kept)

| what | size | SHA-256 | read with |
|---|---|---|---|
| `FULL-USENET-BACKUP-2020-Oct-comp.lang.prolog.24833.mbox.7z` / `comp.lang.prolog.(24833).mbox.7z` | 10,498,866 | `43157f28518be8d2571fed7061ecf3248ed99de42092d2eae29bc3dbffba4de2` | `bsdtar -x`, `grep` |
| `usenet-comp.sources/*.mbox.gz` (25 files) | 8.4 MB in all | not recorded | `gzip -dc`, `grep` |
| `IO_198502_djvu.txt` (I/O 1985-02), `ASCII_August_1984_djvu.txt`, `PP199103_djvu.txt`, Fujitsu STJ V26 N01 `_djvu.txt` | 628,834; 1,870,396; 544,985; 332,597 | not recorded | `grep`, `sed` |
| the five Kahaner reports `icot-sci`, `icot.692`, `icot.94`, `icot.94a`, `icot.kl1` (via Discmaster) | 5,027 to 47,339 | not recorded | `grep` |

None is a SIMPOS or ESP file, none has redistribution terms that matter here, and none is added to
`../../nonlocal/lit/`.
