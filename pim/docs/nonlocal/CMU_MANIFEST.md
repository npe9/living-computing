# CMU AI Repository ICOT tree: comparison with the held IFS copies

Run 2026-11-26. Source: `https://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/icot/`
(the CMU Artificial Intelligence Repository's re-packed copy of `ftp.icot.or.jp:/ifs/`; every
file on it is dated 1995-06-13, the `.ltv` tar listings show member dates up to July 1994).
Compared against what pim already holds: the AIST-fetched IFS tree (`IFS_MANIFEST.md`,
`ifs/SHA256SUMS`), the eight archives of `MANIFEST.md`, `icot-other/` (`ICOT_OTHER_MANIFEST.md`)
and `lit/` (`LIT_MANIFEST.md`). Nothing was unpacked into the repository, built or run.

## 1. Method

- **Walk.** Every CMU directory listing (31 directories) was read sequentially with 1 s between
  requests and a generic User-Agent. Every file was sized by an HTTP HEAD (`Content-Length`;
  the Apache listing rounds sizes), and every small metadata file (`0.doc`, `0.html`, `0.lst`,
  `0.iso`, `*.ltv`, `*.txt`) was fetched. Completeness: every package named in each directory's
  `0.lst` was found in the walk, and `index.txt` names catalogue numbers [01]-[84], six of them
  marked `*preparing*` or `*updating*` with no package ([26] Qute, [27] SAM, [31] Argus/V,
  [79] Quixote KLIC version, [81] MGTP/G Prolog, [82] MGTP/N Prolog).
- **Match.** Each held archive (379 compress/gzip files under `ifs/`, `icot-other/`, `pim-m/` and
  the eight top-level archives) was listed in memory with Python `tarfile` (via `gzip -dc`).
  Each CMU `.tgz` was matched by its `.ltv` member set, (path below the top directory, size),
  against every held archive; members were also looked up among loose held files and the
  decompressed sizes of loose `.Z` files, so a CMU bundle of files AIST keeps loose is found.
  No `.ltv` line failed to parse (0 of 100 files).
- **Verify.** 20 CMU files were downloaded (11.3 MB): the 4 CMU-only and 4 different-version
  packages, and, as a check that the classes are earned, the PIM/PSI and Unix KL1 packages, the
  newsletters, `info.tgz`, `pimosman.pgz` and `patch12b.gz`. For those, members were compared by
  SHA-256 and the whole decompressed tar was hashed.
- **Not fetched.** The 79 "same members" packages and 5 re-packed bundles (their `.ltv` matches
  the held copy name for name and byte for byte), and the 5.2 GB archive.org WARC.

## 2. Classes

| Class | Meaning | Count (of 100 `.tgz`) |
|---|---|---|
| A identical content | downloaded; the decompressed tar is byte-identical to the held archive's (CMU gzipped the original tar) | 8 |
| B same members | not downloaded; `.ltv` names and sizes equal the held archive's member list | 79 |
| C same content, different packing | CMU bundles files AIST holds loose (newsletters, PIMOS and KL1 manuals) | 5 |
| D different version | same package, a different release; CMU's is the earlier one in all four | 4 |
| E CMU-only | no held counterpart | 4 |

Other CMU payload files (not `.tgz`):

| CMU file | bytes | SHA-256 | class |
|---|---|---|---|
| `symbolic/pim_psi/pimosman.pgz` | 652037 | `39c2def4a5bc53a2ee67ce7608f5057347c6279e77e6cc5526b0ab0cc2f1b7b1` | A: decompressed = held `ifs/symbolic-proc/pim-psi/pimosman.ps.Z` decompressed (sha256 `87271744d4fc7cba...`) |
| `symbolic/unix/aum/patch12b.gz` | 2130 | `335d298bf938c20b39a33b814da6b54671872f93fe10e53793eb0050b3000f2e` | A: decompressed = held `ifs/symbolic-proc/unix/aum-pat-1.2b.Z` decompressed |
| `readme.txt`, `readme_j.txt` | 14067, 15426 | see section 4 | D: the IFS top-level README "Last Modified on 27-Jun-1994"; held `ifs/README` is the 15-Apr-1996 edition. Its change log already names the PIMOS and psdpim releases of 29 Mar and 12 May 1994 that the held archives are |
| `reasonng/pimos/argus.txt` | 314 | see section 4 | E: ICOT notice that [31] Argus/V is withdrawn for updating, re-release planned for end of March 1994 (held `ifs/solver-prover/pimos/argus-v.tar.Z` is that later release) |
| `cesp.txt`, `index.txt`, `0.html` | 637, 6299, 3964 | in `LIT_MANIFEST.md` | already held, SHA-256 identical, under `lit/web/www.cs.cmu.edu/` |

CMU wrapper files (`0.doc` 11, `0.html` 11 (the top one also in `lit/`), `0.lst` 25, `0.iso` 3, `*.ltv` 100): written by the
repository, not by ICOT; held on disk only (section 4).

## 3. Comparison table (all 100 `.tgz`)

Paths in "held counterpart" are relative to `pim/docs/nonlocal/`.

| CMU file | bytes | members (.ltv) | held counterpart | class | note |
|---|---|---|---|---|---|
| `info.tgz` | 13040 | 10 | `ifs/INFO.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `newsltr/e01_07.tgz` | 19270 | 7 | `loose files` | C same content, different packing | E01-E07 loose in `ifs/newsletter/`; all 7 members SHA-256 identical (downloaded) |
| `newsltr/j01_08.tgz` | 24535 | 8 | `loose files` | C same content, different packing | J01-J08 loose in `ifs/newsletter/`; 7 identical, J08.940701 differs by one typo (CMU `zgip`, AIST `gzip`): CMU has the earlier copy |
| `apps/pimos/aligndp.tgz` | 40673 | 21 | `ifs/exper-apps/pimos/aligndp.tar.Z` | B same members |  |
| `apps/pimos/alignsa.tgz` | 53703 | 22 | `ifs/exper-apps/pimos/alignsa.tar.Z` | B same members |  |
| `apps/pimos/cbcdss.tgz` | 557579 | 156 | `ifs/exper-apps/pimos/cbcdss.tar.Z` | B same members |  |
| `apps/pimos/celplace.tgz` | 146616 | 44 | `ifs/exper-apps/pimos/celplace.tar.Z` | B same members |  |
| `apps/pimos/cohlex.tgz` | 179093 | 117 | `ifs/exper-apps/pimos/cohlex.tar.Z` | B same members |  |
| `apps/pimos/colodex.tgz` | 220516 | 187 | `ifs/exper-apps/pimos/colodex.tar.Z` | B same members |  |
| `apps/pimos/consort.tgz` | 187025 | 84 | `ifs/exper-apps/pimos/consort.tar.Z` | B same members |  |
| `apps/pimos/desq.tgz` | 386005 | 142 | `ifs/exper-apps/pimos/desq.tar.Z` | B same members |  |
| `apps/pimos/editalgn.tgz` | 431710 | 141 | `ifs/exper-apps/pimos/editalign.tar.Z` | B same members |  |
| `apps/pimos/examds.tgz` | 509975 | 424 | `ifs/exper-apps/pimos/examds.tar.Z` | B same members |  |
| `apps/pimos/gog_kl1.tgz` | 489429 | 284 | `ifs/exper-apps/pimos/gog-kl1.tar.Z` | B same members |  |
| `apps/pimos/gpsstap.tgz` | 174914 | 274 | `ifs/exper-apps/pimos/gpsstap.tar.Z` | B same members |  |
| `apps/pimos/helic2.tgz` | 346338 | 250 | `ifs/exper-apps/pimos/helic2.tar.Z` | B same members |  |
| `apps/pimos/logisim.tgz` | 1706362 | 47 | `ifs/exper-apps/pimos/logisim.tar.Z` | B same members |  |
| `apps/pimos/lsirout.tgz` | 45231 | 23 | `ifs/exper-apps/pimos/lsirout.tar.Z` | B same members |  |
| `apps/pimos/mendels.tgz` | 544645 | 173 | `ifs/exper-apps/pimos/mendels.tar.Z` | B same members |  |
| `apps/pimos/mmi.tgz` | 250652 | 85 | `ifs/exper-apps/pimos/mmi.tar.Z` | B same members |  |
| `apps/pimos/mssd.tgz` | 568868 | 434 | `ifs/exper-apps/pimos/mssd.tar.Z` | B same members |  |
| `apps/pimos/multalgn.tgz` | 94101 | 39 | `ifs/exper-apps/pimos/multialign.tar.Z` | B same members |  |
| `apps/pimos/pmonitor.tgz` | 239687 | 61 | `ifs/exper-apps/pimos/pmonitor.tar.Z` | B same members |  |
| `apps/pimos/qxtmotif.tgz` | 569506 | 12 | `ifs/exper-apps/pimos/qxt_motif.tar.Z` | B same members |  |
| `apps/pimos/rodin.tgz` | 523938 | 187 | `ifs/exper-apps/pimos/rodin.tar.Z` | B same members |  |
| `apps/pimos/seqanal.tgz` | 93613 | 53 | `ifs/exper-apps/pimos/seqanal.tar.Z` | B same members |  |
| `apps/simpos/gog_esp.tgz` | 426969 | 223 | `ifs/exper-apps/simpos/gog-esp.tar.Z` | B same members |  |
| `apps/unix/proview.tgz` | 682620 | 168 | `ifs/exper-apps/unix/proview/proview.tgz` | D different version | 154 identical; CMU's `matrix/matrix.{c,h}` dated 1994-04-19 against AIST's 1995-05-25, and CMU puts COPYRIGHT/DOC/README/REFERENCE inside the archive (AIST keeps later copies loose beside it): CMU is the earlier release |
| `kbms_clp/cesp/cal_cesp.tgz` | 150289 | 26 | `ifs/kbms-clp/cesp/cal-cesp.tar.Z` | B same members |  |
| `kbms_clp/pimos/gdcc.tgz` | 404964 | 86 | `ifs/kbms-clp/pimos/gdcc.tar.gz` | B same members |  |
| `kbms_clp/pimos/kappa_p.tgz` | 890478 | 510 | `ifs/kbms-clp/pimos/kappa-p.tar.Z` | B same members |  |
| `kbms_clp/pimos/p_chal.tgz` | 11114 | 12 | `ifs/kbms-clp/pimos/p-chal.tar.Z` | B same members |  |
| `kbms_clp/pimos/quixote.tgz` | 1439442 | 499 | `ifs/kbms-clp/pimos/quixote.tar.gz` | D different version | 497 members identical by hash; CMU `README` and `doc/intro.tex` dated 1993-07-28/29, AIST's `doc/intro.tex` 1994-09-22 plus `doc/quixote.tex`, `doc/qxtv3.eps`: CMU is the earlier release |
| `kbms_clp/pimos/robot.tgz` | 17201 | 12 | `ifs/kbms-clp/pimos/robot.tar.Z` | B same members |  |
| `kbms_clp/pimos/voronoi.tgz` | 50901 | 37 | `ifs/kbms-clp/pimos/voronoi.tar.Z` | B same members |  |
| `kbms_clp/simpos/cal_esp.tgz` | 483985 | 110 | `ifs/kbms-clp/simpos/cal-esp.tar.Z` | B same members |  |
| `kbms_clp/simpos/chal.tgz` | 41204 | 21 | `ifs/kbms-clp/simpos/chal.tar.Z` | B same members |  |
| `kbms_clp/simpos/kappa2.tgz` | 3428056 | 831 | `ifs/kbms-clp/simpos/kappa2.tar.Z` | B same members |  |
| `kbms_clp/simpos/kappa2d1.tgz` | 3740681 | 4 | `ifs/kbms-clp/simpos/kappa2d1.tar.Z` | B same members |  |
| `kbms_clp/simpos/kappa2d2.tgz` | 3356890 | 6 | `ifs/kbms-clp/simpos/kappa2d2.tar.Z` | B same members |  |
| `kbms_clp/simpos/kappa2d3.tgz` | 8298299 | 4 | `ifs/kbms-clp/simpos/kappa2d3.tar.Z` | B same members |  |
| `kbms_clp/simpos/knov.tgz` | 121603 | 114 | `ifs/kbms-clp/simpos/knov.tar.Z` | B same members |  |
| `kbms_clp/unix/cuprolog.tgz` | 167228 | 43 | `ifs/kbms-clp/unix/cuprolog/cupsrc.tar.gz` | D different version | cu-Prolog III **3.1 (July 6, 1994)** (`src/main.c` VERSION); AIST `ifs/` has 3.94 (Jan 27, 1995), `icot-other/pub/cuprolog/cup380d.tar.Z` 3.80d (by file name): CMU is an intermediate release held nowhere else |
| `kbms_clp/unix/dp.tgz` | 193556 | 75 | `ifs/kbms-clp/unix/dp.tgz` | B same members |  |
| `kbms_clp/unix/m_qxt.tgz` | 104572 | 56 | `ifs/kbms-clp/unix/m-qxt.tgz` | B same members | 62 held members; the 6 extra are the same symlinks, which the .ltv writes as `x symbolic link to y` |
| `manuals/esp/espps.tgz` | 271649 | 2 | `ifs/manuals/esp/ESPps.tar.Z` | B same members |  |
| `manuals/esp/espps_j.tgz` | 458561 | 2 | `ifs/manuals/esp/ESPps-j.tar.Z` | B same members |  |
| `manuals/esp/esptex.tgz` | 110046 | 2 | `ifs/manuals/esp/ESPtex.tar.Z` | B same members |  |
| `manuals/esp/esptex_j.tgz` | 114654 | 2 | `ifs/manuals/esp/ESPtex-j.tar.Z` | B same members |  |
| `manuals/kl1/kl1_text.tgz` | 124969 | 45 | `ifs/manuals/kl1/kl1-text.tar.Z` | B same members |  |
| `manuals/kl1/kl1_tut.tgz` | 368067 | 4 | `loose files` | C same content, different packing | `ifs/manuals/kl1/kl1-tut.{ps,j.ps,dvi}.Z` (sizes match); CMU adds only `0.doc.~1~`, a CMU editor backup |
| `manuals/pimos/man.tgz` | 1506074 | 2 | `loose files` | C same content, different packing | `ifs/manuals/pimos/man15.ps.Z`, `man30.j.ps.Z` (decompressed sizes match) |
| `manuals/pimos/primer.tgz` | 57462 | 2 | `loose files` | C same content, different packing | `ifs/manuals/pimos/primer25.tex.Z`, `primer15.j.tex.Z` (decompressed sizes match) |
| `nlp/cesp/kwiccesp.tgz` | 717509 | 7 | `ifs/natural-lang/cesp/kwic-cesp.tar.Z` | B same members |  |
| `nlp/cesp/linguist.tgz` | 311563 | 140 | `ifs/natural-lang/cesp/linguist.tar.Z` | B same members |  |
| `nlp/cesp/morphana.tgz` | 280330 | 73 | `ifs/natural-lang/cesp/morphana.tar.Z` | B same members |  |
| `nlp/cesp/sdiv.tgz` | 43768 | 25 | `ifs/natural-lang/cesp/sdiv.tar.Z` | B same members |  |
| `nlp/pimos/dulcinea.tgz` | 521856 | 171 | `ifs/natural-lang/pimos/dulcinea.tar.Z` | B same members |  |
| `nlp/pimos/laputa.tgz` | 332622 | 63 | `ifs/natural-lang/pimos/laputa.tar.Z` | B same members |  |
| `nlp/pimos/pax.tgz` | 38790 | 20 | `ifs/natural-lang/pimos/pax.tar.Z` | B same members |  |
| `nlp/simpos/cil.tgz` | 986072 | 141 | `ifs/natural-lang/simpos/cil.tar.gz` | B same members |  |
| `nlp/simpos/disc.tgz` | 156204 | 102 | `ifs/natural-lang/simpos/disc.tar.Z` | B same members |  |
| `nlp/simpos/icotext.tgz` | 287288 | 121 | `ifs/natural-lang/simpos/icotext.tar.Z` | B same members |  |
| `nlp/simpos/sum.tgz` | 103894 | 111 | `ifs/natural-lang/simpos/sum.tar.Z` | B same members |  |
| `nlp/simpos/txtstrct.tgz` | 140820 | 31 | `ifs/natural-lang/simpos/txtstrct.tar.Z` | B same members |  |
| `nlp/simpos/utter.tgz` | 320033 | 123 | `ifs/natural-lang/simpos/utter.tar.Z` | B same members |  |
| `nlp/unix/jpnsgen.tgz` | 220579 | 105 | `ifs/natural-lang/unix/jpnsgen.tar.Z` | B same members |  |
| `nlp/unix/lug.tgz` | 394806 | 297 | `ifs/natural-lang/unix/lug.tar.Z` | B same members |  |
| `nlp/unix/lug_fse.tgz` | 846800 | 308 | `ifs/natural-lang/unix/lug-fse.tar.Z` | B same members |  |
| `nlp/unix/lug_man.tgz` | 1126222 | 77 | `ifs/natural-lang/unix/lug-man.tar.Z` | B same members |  |
| `nlp/unix/morphdic.tgz` | 1154303 | 68 | `ifs/natural-lang/unix/morphdic.tar.gz` | B same members |  |
| `nlp/unix/rdg.tgz` | 58245 | 18 | `ifs/natural-lang/unix/rdg.tar.Z` | B same members |  |
| `nlp/unix/synana.tgz` | 85016 | 22 | `ifs/natural-lang/unix/synana.tar.Z` | B same members |  |
| `reasonng/pimos/mgtp.tgz` | 20283 | 13 | `ifs/solver-prover/pimos/mgtp.tar.Z` | B same members |  |
| `reasonng/pimos/ppss.tgz` | 34740 | 22 | `ifs/solver-prover/pimos/ppss.tar.Z` | B same members |  |
| `reasonng/pimos/sme.tgz` | 96875 | 48 | `ifs/solver-prover/pimos/sme.tar.Z` | B same members |  |
| `reasonng/simpos/euod.tgz` | 156716 | 20 | `ifs/solver-prover/simpos/euod.tar.Z` | B same members |  |
| `reasonng/simpos/fuzclust.tgz` | 263734 | 77 | `ifs/solver-prover/simpos/fuzclust.tar.Z` | B same members |  |
| `reasonng/simpos/papyrus.tgz` | 2643528 | 5 | `ifs/solver-prover/simpos/papyrus.tar.Z` | B same members |  |
| `reasonng/unix/bmtp.tgz` | 53606 | 43 | `ifs/solver-prover/unix/bmtp.tar.Z` | B same members |  |
| `reasonng/unix/kore_ie.tgz` | 41589 | 32 | `ifs/solver-prover/unix/kore-ie.tar.Z` | B same members |  |
| `symbolic/pim_psi/pimos.tgz` | 1488931 | 636 | `pimos.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `symbolic/pim_psi/pimosman.tgz` | 355489 | 58 | `pimosman.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `symbolic/pim_psi/pimosobj.tgz` | 1834397 | 34 | `pimosobj.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `symbolic/pim_psi/psdpim.tgz` | 972900 | 27 | `psdpim.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `symbolic/pimos/aya.tgz` | 108698 | 37 | `ifs/symbolic-proc/pimos/aya.tar.Z` | B same members |  |
| `symbolic/pimos/exreps.tgz` | 56755 | 28 | `ifs/symbolic-proc/pimos/exreps.tar.Z` | B same members |  |
| `symbolic/pimos/kl1graph.tgz` | 130545 | 29 | `ifs/symbolic-proc/pimos/kl1graph.tar.Z` | D different version | 23 sources identical by hash; another 1992 packing of the same sources: CMU's has no COPYRIGHT and no `DOC/` figures, but keeps two earlier drafts `ppuserman.tex.`/`ppoutline.tex.` and an inner `kl1graph.tar` (396,800 B) of the same sources; AIST's has COPYRIGHT and `DOC/*.ps` |
| `symbolic/pimos/ldlib.tgz` | 65751 | 94 | `ifs/symbolic-proc/pimos/ldlib.tar.Z` | B same members |  |
| `symbolic/pimos/strtgysh.tgz` | 240831 | 47 | `ifs/symbolic-proc/pimos/strtgysh.tar.Z` | B same members |  |
| `symbolic/unix/pdss.tgz` | 1436302 | 412 | `pdss.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `symbolic/unix/pkl1.tgz` | 71683 | 63 | `pkl1.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `symbolic/unix/vpim.tgz` | 935364 | 238 | `vpim.tar.Z` | A identical content | downloaded: decompressed tar byte-identical to the held archive's |
| `nlp/simpos/kwic_esp/kwic_esp.tgz` | 1001057 | 90 | `ifs/natural-lang/simpos/kwic-esp.tar.Z` | B same members |  |
| `nlp/simpos/kwic_esp/kwice002.tgz` | 1017640 | 93 | `ifs/natural-lang/simpos/kwic-esp-002.tar.Z` | B same members |  |
| `symbolic/unix/aum/aum_1_2c.tgz` | 583201 | 790 | `ifs/symbolic-proc/unix/aum-1.2c.tar.Z` | B same members |  |
| `symbolic/unix/klic/klic1000.tgz` | 123511 | 144 | `ifs/symbolic-proc/unix/klic/klic-old/klic-1.500.tgz` | E CMU-only | KLIC **1.000** (`compiler/version.pl.tmplt`; README 1993-12-16; IFS README: new release 17 Dec 1993). Held KLIC starts at 1.500 |
| `symbolic/unix/klic/klic1100.tgz` | 144722 | 163 | `ifs/symbolic-proc/unix/klic/klic-old/klic-1.500.tgz` | E CMU-only | KLIC **1.100** (version template dated 1994-02-14) |
| `symbolic/unix/klic/klic1210.tgz` | 258737 | 167 | `ifs/symbolic-proc/unix/klic/klic-old/klic-1.500.tgz` | E CMU-only | KLIC **1.210** (top directory `testklic/`; template dated 1994-05-05) |
| `symbolic/unix/klic/klic1410.tgz` | 532611 | 272 | `ifs/symbolic-proc/unix/klic/klic-old/klic-1.500.tgz` | E CMU-only | KLIC **1.410** (`version.kl1.tmplt`, 1994-06-14; IFS README: version-up 20 June 1994) |


Held packages with no CMU counterpart are the AIST tree's later additions (after the CMU copy was
made in mid-1995): all of `contract-research/` (FY1995-98), the KLIC ports under `*/klic/`
(`bigqxt`, `GDCC4.0`, `kappa`, `CMGTP`, `MGTP-G`, `helic2/*`, `pia_klic`, `RNASA`, `alignga`,
`d-pool`), `MGTP-N`, the Unix bio tools (`HMMGene`, `Quant2`, `pathway`, `ssshmm`), `helios`,
`argus-v.tar.Z`, KLIC 1.500, 2.000-2.002, 3.001, and `icot-other/`.

## 4. What is held where

### In git: `cmu/` (ICOT Free Software)

These are ICOT Free Software. Terms: "TERMS AND CONDITIONS FOR USE OF ICOT FREE SOFTWARE",
section 2 ("Each User may also freely distribute the Program, whether in its original form or
modified, to any third party or parties, PROVIDED that the provisions of Section 3 ('NO
WARRANTY') will ALWAYS appear on, or be attached to, the Program"). That text, with its
section 3 NO WARRANTY, is kept beside the files as `cmu/COPYRIGHT` (and `cmu/COPYRIGHT.j`),
taken from CMU `info.tgz` (whose tar is byte-identical to the held `ifs/INFO.tar.Z`). CMU's
`0.doc` for the tree says the same: "Copyright (c) 1991-93 ICOT. Use, copying, modification, and
distribution permitted. See the copyright files in each package for details." The KLIC, cu-Prolog,
proview and Quixote archives each carry their own `COPYRIGHT`; `kl1graph.tgz` has none, and is
covered by the attached `cmu/COPYRIGHT`.

Each file at its CMU path below `cmu/`; checksums in `cmu/SHA256SUMS`
(`cd cmu && shasum -a 256 -c SHA256SUMS`). URL = source above + path.

| File | bytes | SHA-256 | what |
|---|---|---|---|
| `symbolic/unix/klic/klic1000.tgz` | 123511 | `b6a23da64e0291043a0bca50cc36110d37d9783961c879231279c6c67f564b09` | KLIC 1.000, Dec 1993 (E) |
| `symbolic/unix/klic/klic1100.tgz` | 144722 | `7c67c2c8b48d456a2e04c24fe5709224487e067a4224161fd68d0e75ac6c8e3a` | KLIC 1.100, Feb 1994 (E) |
| `symbolic/unix/klic/klic1210.tgz` | 258737 | `9ef4785a5b37b87e2cb4c5991f6c61b492933d2374bbd4bc0eedcb51842b517e` | KLIC 1.210, May 1994 (E) |
| `symbolic/unix/klic/klic1410.tgz` | 532611 | `2d21429421fbab61300cd54aa4e1bcc783c7e4afc881452c602c5420a50ec30b` | KLIC 1.410, Jun 1994 (E) |
| `kbms_clp/unix/cuprolog.tgz` | 167228 | `3bf3ed3a16fc78c15deaea14ec83913ef0c3ae9649f0916d93ecab0b2392c294` | cu-Prolog III 3.1, Jul 1994 (D) |
| `apps/unix/proview.tgz` | 682620 | `331a3d8416386b1756e850dfa01456357c73b13f5e41df2c6c197bbbeba8c998` | proview, Apr 1994 (D) |
| `symbolic/pimos/kl1graph.tgz` | 130545 | `867e9c48f24cdf84496803eaa3685e605c8003c25759c5c316865bdad07b52b5` | kl1graph, Jul 1992 packing (D) |
| `kbms_clp/pimos/quixote.tgz` | 1439442 | `34770e4f4d4792a5e38ec2fd9975c691576b2bfda2120a960d7140a8d007e124` | Quixote (PIMOS), Jul 1993 (D) |
| `readme.txt` | 14067 | `be03a2064dc526a65e4d07e7b30769a06bae3eaeb59163f03e6023b54d527d89` | IFS README, 27-Jun-1994 edition (D) |
| `readme_j.txt` | 15426 | `e59d4037bb605c0b8ab97a4a09bc6886f854a683ac352249507e635f05d92fab` | the same, Japanese (ISO-2022-JP) (D) |
| `reasonng/pimos/argus.txt` | 314 | `1bad6fd4c6621faa97f4c103652eb49834b48d5c7c96f50200a2fdcd93c28c65` | Argus/V withdrawal notice (E) |
| `COPYRIGHT` | 5248 | `dea063cc62c1073b33bab09547a363851fc9093d2f5a8936896c8ae4243f3744` | IFS terms incl. NO WARRANTY (member of `info.tgz`) |
| `COPYRIGHT.j` | 3794 | `5ee8b81a05b4cb735d1bcc507ef09113535c9a38d900a1a5c1e45d077a19c3d5` | the same, Japanese |

### On disk only: `cmu/meta/` (gitignored, in the main checkout)

All 155 small files the walk fetched, at their CMU paths: the CMU-written `0.doc`, `0.html`,
`0.lst`, `0.iso` wrappers, the 100 `.ltv` listings, `index.txt`, `cesp.txt`, and copies of
`readme*.txt` and `argus.txt`; plus `_files.tsv`, the walk's file list (path, listing date,
listing size, exact bytes). They are written by the repository and carry no redistribution
terms, so they stay out of git (`cmu/.gitignore`). Checksums: `cmu/meta/SHA256SUMS`.

### Downloaded for verification, not kept (duplicates of held files)

| CMU file | bytes | SHA-256 |
|---|---|---|
| `symbolic/pim_psi/pimos.tgz` | 1488931 | `04b34ab7972527175c3e55526569e2ebf74292ef5ff7cf4c3f71afefa1c47364` |
| `symbolic/pim_psi/pimosman.tgz` | 355489 | `71a73ae7ec75e018569263dfa2e05d89eee9a0529c47b6eda8ff5391f44f7448` |
| `symbolic/pim_psi/pimosobj.tgz` | 1834397 | `91573b310feda8b87c13484a811b2e055ff05dfbbed7f7449a66c3beba3b7360` |
| `symbolic/pim_psi/psdpim.tgz` | 972900 | `a0266a33c4fd4a457a8bd285e321266005899c7274cb870ecd8078d705bb43c7` |
| `symbolic/pim_psi/pimosman.pgz` | 652037 | `39c2def4a5bc53a2ee67ce7608f5057347c6279e77e6cc5526b0ab0cc2f1b7b1` |
| `symbolic/unix/pdss.tgz` | 1436302 | `4b233a6ddd957c7aca424aed20c0b0bea201c3e3ac82cf0ad9af7b29b56fef6d` |
| `symbolic/unix/pkl1.tgz` | 71683 | `b7e411515fb1b07c46f473b9c146529d94cab542ad355d7ac3772a101ad7cd26` |
| `symbolic/unix/vpim.tgz` | 935364 | `fd24c21b5f484e159245635d09992077b378c2b48dd87127e4b0b88461fc46a2` |
| `symbolic/unix/aum/patch12b.gz` | 2130 | `335d298bf938c20b39a33b814da6b54671872f93fe10e53793eb0050b3000f2e` |
| `newsltr/e01_07.tgz` | 19270 | `78e6a6d390aa4ec06dfcac3a647594915caa9fc1eb35490121dfb64a5921549a` |
| `newsltr/j01_08.tgz` | 24535 | `d88d62e244cfd77e5b36c379dc0a0a97e9b02afd262f12591e4ee9d21d5dac89` |
| `info.tgz` | 13040 | `9e4a9abac3a038a0432a9cfe02b3f21949fb3ed7e9684600a7d05a70b259944a` |

## 5. What it means for the open work

- **PIMOS, psdpim, PSI and PIM/m system files: nothing new.** CMU's `pimos.tgz`, `pimosobj.tgz`,
  `psdpim.tgz` and `pimosman.tgz` decompress to tars byte-identical to the held `pimos.tar.Z`,
  `pimosobj.tar.Z`, `psdpim.tar.Z` and `pimosman.tar.Z`: the 12 May 1994 IFS release (the CMU
  README's change log). So the CMU copy has no other PIMOS version, no other Pseudo PIM/m or
  PSI-III microcode (`psdpim/PMPSI.DIR` is the same bytes), and no Multi-PSI or real PIM/m firmware.
  `pimosman.pgz` is the held `pimosman.ps`.
- **SIMPOS, the window system, Pmacs, the ESP compiler: none.** CMU has no SIMPOS or PSI system
  file outside `psdpim`. The SIMPOS-side packages (`apps/simpos`, `kbms_clp/simpos`, `nlp/simpos`,
  `reasonng/simpos`) and the ESP manuals are all class B, the same members as the held copies.
  `kl1graph` (ESP `screen.esp`, `sys92.esp`, KL1 `window.kl1`) is the same sources in a different
  packing. `cesp.txt` confirms again that Common ESP was never part of IFS.
- **KLIC 1.x: four releases held nowhere else** (1.000, 1.100, 1.210, 1.410, Dec 1993 to Jun 1994),
  committed. They predate the earliest held KLIC (1.500). KLIC 1.000 ships a short manual
  (`documents/manual/`: `klic`, `io`, `merger`, `vectors`, `strings`, `atomfunct`, `inline`,
  `tracer`) and a `test/` directory of KL1 programs with expected outputs (`*.out.cmp`). These are
  the KLIC builds closest in time to PIMOS 3.x KL1; not yet read further.
- **Newsletters: nothing new.** CMU has E01-E07 and J01-J08; the held tree has these plus E08, E09
  and J09. The 27-Jun-1994 IFS README is an earlier edition of the held 1996 one.
- **Other versions:** cu-Prolog 3.1, an earlier proview, an earlier Quixote: off the PIM/PSI path,
  kept for completeness.
