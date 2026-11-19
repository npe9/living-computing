# ICOT non-local sources — acquisition manifest

Retrieved 2026-11-19 from the AIST/ICOT archive
(`https://www.airc.aist.go.jp/aitec-icot/ICOT/`). Every file below was
fetched with `curl` and returned HTTP 200; formats were confirmed with
`file` (the `.Z` files are genuine `compress`d data, not HTML error
pages). Sizes are bytes on disk.

## 1. Source archives

All five archives live in this directory under their original archive
names.

| Local file | URL | Bytes | SHA-256 |
|---|---|---|---|
| `pimos.tar.Z` | https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc/pim-psi/pimos.tar.Z | 2932865 | `1bf96e1293d3e06955e2bed168cc53c55252dae575e9ea0c4f5bd00231ad4b75` |
| `pimosobj.tar.Z` | https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc/pim-psi/pimosobj.tar.Z | 2631847 | `2c9a8f69002a82e8518d2dddd46d2d44142e901db4dcdaae2e93b371461d3993` |
| `pimosman.tar.Z` | https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc/pim-psi/pimosman.tar.Z | 592865 | `3b808305d77b1dc6ce59e82226c6fc8b21797bdd1883df4c615d0d64e2257ab3` |
| `klic-2.002.tgz` | https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc/unix/klic/klic-2.002.tgz | 951411 | `4525acf0c6111a35ec209a7e5a4660d10d4c8d3d7ae63c508607c93da8bbfd31` |
| `pkl1.tar.Z` | https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc/unix/pkl1.tar.Z | 130871 | `70f5944926da8c5b57eca9e0cd5780213a343f8a03b9166fbd5b8e5cf74c2298` |

| Archive | Format | Entries | Uncompressed bytes |
|---|---|---|---|
| `pimos.tar.Z` | `compress`d tar (16-bit LZW) | 706 | 8577024 |
| `pimosobj.tar.Z` | `compress`d tar | 35 | 6758400 |
| `pimosman.tar.Z` | `compress`d tar | 59 | 1622016 |
| `klic-2.002.tgz` | gzip tar (dated 1995-05-23) | 472 | 5396480 |
| `pkl1.tar.Z` | `compress`d tar | 69 | 348160 |

### `pimos.tar.Z` — PIMOS source (KL1)

Top level: `pimos/` with `README`, `README.j`, `protocol/`, `src/`,
`src_util/`.

- `src/` (559 entries; 502 `.kl1` files): `bios/` (39), `debugger/` (122),
  `etc/`, `kernel/` (48), `library/` (103), `macro/` (22), `server/` (116),
  `shell/` (48), `utility/` (49), `vm/` (10).
- `src/library/` contains the whole KL1 toolchain: `compiler/` (44 `.kl1`
  files: `preproc.kl1`, `reader.kl1`, `comp.kl1`, `macroDisp.kl1`,
  `mactbl.kl1`, `optimize.kl1`, `regass.kl1`, `outp.kl1`, `pack.kl1`,
  `depend.kl1`, …), plus `assembler/`, `loader/`, `unloader/`, `kbn/`
  (KL1 binary/object format), `protocol/`, `utility/`.
- `src/vm/`: `vm.kl1`, `sim.kl1`, `DKS.kl1`, `ARGS.kl1`, `scsi_disk.kl1`,
  `convert.kl1` — the PIMOS virtual machine layer.
- `protocol/`: `profiler.prt`, `resource.prt`, `scsi.prt`, `pipeRfil.prt`.

Purpose: the complete PIMOS operating system, written in KL1, as
distributed for PIM and Multi-PSI (also runs pseudo-parallel on PSI-II /
PSI-UX). This is the best available evidence for KL1 coding style,
compiler structure, and the object/loader formats used by the PIM toolchain.

### `pimosobj.tar.Z` — bootable PIMOS object images

Top level: `object/` (35 files) with `INSTALL`, `INSTALL.j`.

- Compiled system images (`*.sav`): `pimm_bios360E.sav`,
  `pimm_debugger360E.sav`, `pimm_kernel360E.sav`, `pimm_library360E.sav`,
  `pimm_macro360E.sav`, `pimm_server360E.sav`, `pimm_shell360E.sav`,
  `pimm_utility360E.sav`, plus a dozen `pimm_patch_*360E.sav` patches.
- IPL/object files: `pimm_ipl.kbn`, `pimm_ipl.ldb`, `pimm_ipl.sym`.
- Startup: `pimos.com`, `pimos.conf`, `pimos.groups`, `pimos.ipl`,
  `pimos.logins`, `shell.com`, `login.com`, `init.com`, `paragraph.ptf`.

`INSTALL` states the target is PSI-II / PSI-UX in *pseudo PIM/M* or
*pseudo Multi-PSI* mode. These are the binary counterparts to `pimos.tar.Z`
and preserve the on-disk layout expected by the KL1 loader.

### `pimosman.tar.Z` — PIMOS manual LaTeX sources

Top level: `Eman/` (59 files).

- English manual chapters: `e-kl1.tex`, `e-compiler.tex`, `e-builtin.tex`,
  `e-syntax.tex`, `e-sysman.tex`, `e-tuning.tex`, `e-debug.tex`,
  `e-error.tex`, `e-inspecto.tex`, `e-protocol.tex`, `e-server*.tex`,
  `e-shoen.tex`, `e-preproc.tex`, `e-io*.tex`, `e-stdio*.tex`,
  `e-shell.tex`, `e-task.tex`, `e-version.tex`, `e-v30.tex`, …
- Japanese originals: `kl1.tex`, `ioctrl.tex`, `top.tex`, `sub.tex`.
- Styles: `pimos.sty`, `pimdoc.sty`, `jreport.sty`, `jtitlepage.sty`,
  `psibitmap.sty`, `a4.sty`, `epic.sty`, …

This is the PIMOS user/system manual, not a PIM/m hardware manual. It is
the closest thing in the IFS set to a PIMOS programming reference.

### `klic-2.002.tgz` — KLIC 2.002, KL1-to-C compiler

Top level: `klic-2.002/` with `COPYRIGHT(.j)`, `ChangeLog`, `Configure`,
`INSTALL(.j)`, `MANIFEST`, `README(.j)`, `Makefile.tail`, `klic-version`.

- `compiler/` (53): KL1 sources (`main.kl1`, `kl1cmp.kl1`, `normalize.kl1`,
  `generate.kl1`, `macro.kl1`, `gb.kl1`, `bb.kl1`, `insert.kl1`,
  `write.kl1`, `obj.kl1`, `extern.kl1`, `version.kl1`, `util.kl1`) and
  their generated C/`.ext` counterparts, plus `klic.c/.h`, `klicdb.c`,
  `options.c`, `Makefile`.
- `runtime/` (184): `main.c`, `alloc.c`, `gc.c`, `unify` internals,
  `arith.c`, `nametable.c`, `failsusp.c`, `print.c`, `timing.c`, plus
  distributed/shared-memory back ends and Perl support scripts.
- `include/` (55): `include/klic/*.h` (`alloc.h`, `arith.h`, `basic.h`,
  `control.h`, `struct.h`, `unify.h`, `copier_body*.h`, `index.h`, …).
- `documents/` (10): `klic.tex`, `klicj.tex`, `klic.dvi`, `klicj.dvi`,
  `klic.1`, `KLIC.info`, `KLICj.info`, `klicj-info.el`.
- `test/`, `shmtest/`, `disttest/`, `rmon/`.

README: "KL1 to C compiler system: KLIC (version 2.0)", last revision
1995-04-24, Chikayama/Fujise/Sekita. This is the version-2.002 source; the
public `GunterMueller/KLIC` repository is v3.011, so v2.002 survives here.

### `pkl1.tar.Z` — portable KL1 (pre-KLIC)

Top level: `./` (69 entries) with `COPYRIGHT(.j)`, `INSTALL(.j)`,
`MANUAL`, `KLICmakefile`, `README(.j)`.

- `compiler/` (12): Perl KL1 compiler `kl1cmp.pl`, `atom.pl`, `builtin.pl`,
  `extern.pl`, `gb.pl`, `generate.pl`, `loadup.pl`, `obj.pl`, `util.pl`,
  `write.pl`, `Makefile`.
- `include/klic/` (19 headers) and `runtime/` (18 C files: `alloc.c`,
  `arith.c`, `bb.c`, `bodyblt.c`, `debug.c`, `failsusp.c`, `gc.c`,
  `main.c`, `nametable.c`, `options.c`, `print.c`, `timing.c`).
- `samples/` (10): `fact.kl1`, `qsort.kl1`, `nrev.kl1`, `kkqueen.kl1`,
  `life.kl1`, `tak.kl1`, `lips.kl1`, `cd.kl1`, `Makefile`.
- `klic` driver script.

`MANUAL` (1993-07-09, Chikayama) is an early KL1 language/implementation
note and warns "PLEASE DO NOT EXPECT THIS VERSION TO BE A COMPLETE
SYSTEM". It predates KLIC and is useful for looking at the KL1-to-C
translation before the v2 rewrite.

## 2. PIM/m-specific documents downloaded from the Museum

Found by searching `Museum/TRTM/TR/TRlist.html` and
`Museum/TRTM/TM/TMlist.html`. All are scanned/image PDFs. Each URL was
fetched and returned HTTP 200; `file` reports PDF 1.4.

| Local file | TR/TM | Title | Bytes | SHA-256 |
|---|---|---|---|---|
| `tr/TR-0564.pdf` | TR-564 (1990-05, 8 pp) | PIM/m 要素プロセッサのアーキテクチャ (Nakajima et al.) | 504396 | `5c0bad41b0136c8295e868fb44a8bce01e0b022698294a2706412a2e7bba425c` |
| `tr/TR-0742.pdf` | TR-742 (1992-03, 12 pp) | Architecture and Implementation of PIM/m (Nakajima et al.) | 736608 | `93acb2819e89badee78ccf3ebccce4230c1f9e4d55f76da00ad384d38f10df16` |
| `tr/TR-0799.pdf` | TR-799 (1992-08, 24 pp) | A VLSI Chip Set for a Large Scale Parallel Inference Machine: PIM/m (Machida et al.) | 970826 | `6dcc76f5bd1821f94ce7192a06c0302e7c377d747b180a051490349bf833a3de` |
| `tm/TM-1074.pdf` | TM-1074 (1991-07, 25 pp) | 並列推論マシン (PIM/m) 用 VLSI (Furutani et al.) | 665742 | `b8482c9e756ade90f32d682f4309e29f2c4f8f8434c546dfe42e30f30523d8e1` |
| `tm/TM-1159.pdf` | TM-1159 (1992-02, 5 pp) | A VLSI Chip Set for a Large Scale Parallel Inference Machine: PIM/m (Machida et al.) | 332910 | `0211e3740523ec10cf895732407dacd72a410ca7ec608822f33dc955d9ef93c7` |

Source URL pattern: `https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/trNNNN.pdf`
and `.../TM/TMpdf/tmNNNN.pdf`.

### PIM/m hardware photos

`pim-m/pim-m-E.html` (the "Photo Exhibition of PIM/m" page,
`Museum/MACHINE/pim-m-E.html`, HTTP 200, 2384 bytes,
SHA-256 `685295afc531da15078093f511ab0c3924295e90b5803c1a467642922063d647`)
and its nine full-size JPEGs in `pim-m/photos/`:

| File | Bytes | SHA-256 |
|---|---|---|
| `pim-m-1.jpg` (system) | 32564 | `1b2e0b9ef415e0f23db734b0cf49e6e557181cc043d073ec1c81e13235a326a0` |
| `pim-m-15.jpg` (cabinet) | 24604 | `aff9ab6d8e69c03394bfe683063df4ff9118d4011347ede3c14009486ae40b68` |
| `pim-m-16.jpg` (cabinet rear) | 28597 | `480331c09e574e44ad564f5b6697863c9758a274feaeae13ea4a447864c53a9b` |
| `pim-m-2.jpg` (cabinet interior) | 37540 | `fe177fa459a956ee7869c1509d1a7c6585e41be4f29f6e72b10daf9cb891ab61` |
| `pim-m-21.jpg` (cabinet interior) | 71767 | `241ef979a97510d0b682e138f4c17ee496201911ab13d7b2bded73714f1a7ced` |
| `pim-m-22.jpg` (board close-up) | 136842 | `3e1c638e4fe302fab451259c0432828305601936814e88ff343dde0c7cbf3dcf` |
| `pim-m-3.jpg` (processor board) | 38434 | `b04b0c79b7c58e8d78ea4a4c98e3d4b61ae6c1066222d9984725cb075972f6dc` |
| `pim-m-31.jpg` (memory board) | 94789 | `fcf508f40527f55331ada41586bcdba1389d3cbbc5eddfc3e3f402e04b188a3e` |
| `pim-m-32.jpg` (network board) | 93370 | `b34fd8d6e5a1d110df71555baef902cbe91ca7074036c76872af36b3f9a0dd67` |

## 3. Candidate documents (recorded only, not downloaded)

Checked by HTTP HEAD on 2026-11-19. None is PIM/m-exclusive (or it would
have been downloaded above); they matter to KL1 implementation and PIM/m
context but cover several models.

| Candidate | URL | Status | Size |
|---|---|---|---|
| PIM model comparison (family-wide, has a PIM/m section) | `.../Museum/MACHINE/pim-spec-E.html` | 200 | 8098 |
| same, Japanese | `.../Museum/MACHINE/pim-spec-J.html` | 200 | 8967 |
| TR-246 An Abstract KL1 Machine and Its Instruction Set | `.../Museum/TRTM/TR/TRpdf/tr0246.pdf` | 200 | 818007 |
| TR-373 KL1 の実現方式と並列 OS の記述 | `.../Museum/TRTM/TR/TRpdf/tr0373.pdf` | 200 | 996751 |
| TR-389 Macro-call Instruction for the Efficient KL1 Implementation on PIM | `.../Museum/TRTM/TR/TRpdf/tr0389.pdf` | 200 | 1120478 |
| TR-460 The FGCS Computing Architecture | `.../Museum/TRTM/TR/TRpdf/tr0460.pdf` | 200 | 531429 |
| TR-659 PIM Architecture and Implementations | `.../Museum/TRTM/TR/TRpdf/tr0659.pdf` | 200 | 505283 |
| TM-140 Current Research Status of PIM | `.../Museum/TRTM/TM/TMpdf/tm0140.pdf` | 200 | 653595 |
| TM-1067 PIM/p 用 KL1 処理系の実装 (PIM/p, not m) | `.../Museum/TRTM/TM/TMpdf/tm1067.pdf` | 200 | 656488 |
| TM-1203 KL1 による PIMOS の実現について | `.../Museum/TRTM/TM/TMpdf/tm1203.pdf` | 200 | 610578 |
| FGCS'92 PIM/m paper (already in `../FGCS92_Volume_1.pdf`) | `.../Museum/FGCS/FGCS92en-proc1/92ePIM-2.pdf` | 200 | 1529601 |
| FGCS'92 PIM/p paper | `.../Museum/FGCS/FGCS92en-proc1/92ePIM-1.pdf` | 200 | 1682846 |
| IFS abstract, PIMOS | `.../Museum/IFS/abst/004-J.html` | 200 | 4254 |
| IFS abstract, pkl1 | `.../Museum/IFS/abst/072-J.html` | 200 | 1913 |
| IFS abstract, KLIC v2.002 | `.../Museum/IFS/abst/085-J.html` | 200 | 4231 |
| TR index (source of the TR search) | `.../Museum/TRTM/TR/TRlist.html` | 200 | — |
| TM index (source of the TM search) | `.../Museum/TRTM/TM/TMlist.html` | 200 | — |

`...` = `https://www.airc.aist.go.jp/aitec-icot/ICOT`.

Notes on the comparison page: it states that "the PE of PIM/m has a
CISC-like micro programmable instruction set", and that PIM/m targets
"rigid compatibility with the Multi-PSI" with up to 256 PEs on a 2-D mesh.
It is HTML with no per-model document links; the local mirror
`https://www.uedalab.jp/AITEC_ICOT_ARCHIVES/ICOT/Museum/MACHINE/pim-spec-E.html`
also returned 200 (8095 bytes).

## 4. Verification commands

Every command was run in `pim/docs/nonlocal` unless noted.

```sh
# download + HTTP status + size (one line per archive)
base=https://www.airc.aist.go.jp/aitec-icot/ICOT/ifs/symbolic-proc
for u in $base/pim-psi/pimos.tar.Z $base/pim-psi/pimosobj.tar.Z \
         $base/pim-psi/pimosman.tar.Z $base/unix/klic/klic-2.002.tgz \
         $base/unix/pkl1.tar.Z; do
  f=$(basename "$u"); code=$(curl -sS -L --fail -o "$f" -w '%{http_code}' "$u")
  echo "$code $(stat -f%z "$f") $f"
done

# format check: must not be HTML
file *.Z *.tgz

# checksums
shasum -a 256 *.Z *.tgz tr/*.pdf tm/*.pdf pim-m/pim-m-E.html pim-m/photos/*.jpg

# listing
for f in pimos pimosobj pimosman pkl1; do
  gzip -dc $f.tar.Z | tar -tf - | wc -l
done
tar -tzf klic-2.002.tgz | wc -l

# candidate statuses
for u in ...; do curl -sSI "$u" | head -1; done
```

Observed totals: 706 / 35 / 59 / 69 / 472 entries respectively.
