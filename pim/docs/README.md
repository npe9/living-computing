# PIM primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

Run `./fetch.sh` from this directory to retrieve the public archive
copies. The script refuses truncated or non-PDF responses, writes files
under stable names, and produces `SHA256SUMS`. Commit the PDFs and
checksum file together after checking the archive's redistribution terms.

| local file | source | role |
|---|---|---|
| `FGCS92_Volume_2.pdf` | [ICOT FGCS '92 Proceedings, volume 2](https://bitsavers.trailing-edge.com/pdf/icot/Fifth_Generation_Computer_Systems_1992_Volume_2.pdf) | additional PIM, KL1, and evaluation papers |
| `FGCS92_Volume_1.pdf` | [ICOT, FGCS '92 proceedings, volume 1](https://bitsavers.trailing-edge.com/pdf/icot/Fifth_Generation_Computer_Systems_1992_Volume_1.pdf) | PIM overview and the PIM/p and PIM/m implementation papers |
| `ICOT_TR-324_Parallel_Inference_Machine_Research.pdf` | [AIST ICOT archive, TR-324](https://www.airc.aist.go.jp/aitec-icot/ICOT/Museum/TRTM/TR/TRpdf/tr0324.pdf) | architecture rationale and execution model |

The [ICOT PIM comparison](https://www.uedalab.jp/AITEC_ICOT_ARCHIVES/ICOT/Museum/MACHINE/pim-spec-E.html)
is HTML and should be saved separately with its images and retrieval
date if it becomes an architectural source. It distinguishes all five
PIM variants and must not be treated as a PIM/m programming manual.

After retrieval, run:

```sh
pdfinfo FGCS92_Volume_1.pdf
pdfinfo ICOT_TR-324_Parallel_Inference_Machine_Research.pdf
shasum -a 256 -c SHA256SUMS
```

## ICOT archive and GitHub status

Archive root: `https://www.airc.aist.go.jp/aitec-icot/ICOT/` works as a path
prefix only; the bare URL returns 404. The browsable entry is
`https://www.airc.aist.go.jp/aitec-icot/ICOT/HomePage-J.html`. Technical
reports live under `Museum/TRTM/TR/TRpdf/trNNNN.pdf`; conference papers under
`Museum/FGCS/...`; free software under `Museum/IFS/abst/` (abstract page) and
`ifs/symbolic-proc/...` (tarball). All 17 table URLs answered HTTP 200 on
2026-11-18. The TR PDFs are scanned images with no text layer; read the page
image when transcribing.

| Document | ICOT URL | Local | GitHub |
|---|---|---|---|
| PIM/m architecture and implementation (FGCS 1992) | `Museum/FGCS/FGCS92en-proc1/92ePIM-2.pdf` | `FGCS92_Volume_1.pdf` | `npe9/living-computing` |
| PIM/p architecture and implementation (FGCS 1992) | `Museum/FGCS/FGCS92en-proc1/92ePIM-1.pdf` | `FGCS92_Volume_1.pdf` | same |
| PIM overview (FGCS 1992) | `Museum/FGCS/FGCS92en-proc1/92eRERR-1.pdf` | `FGCS92_Volume_1.pdf` | same |
| PIMOS/KL1 operating system (FGCS 1992) | `Museum/FGCS/FGCS92en-proc1/92eRERR-2.pdf` | `FGCS92_Volume_1.pdf` | same |
| PIM research (TR-324) | `Museum/TRTM/TR/TRpdf/tr0324.pdf` | `ICOT_TR-324_...pdf` | same |
| An Abstract KL1 Machine and Its Instruction Set (TR-246) | `Museum/TRTM/TR/TRpdf/tr0246.pdf` | — | — |
| Macro-call Instruction for Efficient KL1 on PIM (TR-389) | `Museum/TRTM/TR/TRpdf/tr0389.pdf` | — | — |
| The FGCS Computing Architecture (TR-460) | `Museum/TRTM/TR/TRpdf/tr0460.pdf` | — | — |
| PIM Architecture and Implementations (TR-659) | `Museum/TRTM/TR/TRpdf/tr0659.pdf` | — | — |
| Design of the PIM hardware system (FGCS 1988) | `Museum/FGCS/FGCS88en-proc1/88eR&D-2.pdf` | — | — |
| KLIC: portable KL1 (FGCS 1994) | `Museum/FGCS/FGCS94en-proc/94ePIKL1.pdf` | — | — |
| PIMOS source (KL1, 502 files) | `Museum/IFS/abst/004.html`; `ifs/symbolic-proc/pim-psi/pimos.tar.Z` | — | `npe9/pimos` (public) |
| KLIC source (KL1-to-C); v2.002 tarball | `Museum/IFS/abst/085.html`; `ifs/symbolic-proc/unix/klic/klic-2.002.tgz` | — | `GunterMueller/KLIC` is KLIC 3.011, not v2.002; v2.002 survives only as the ICOT tarball |
| Portable KL1 experimental (pkl1) | `Museum/IFS/abst/072.html`; `ifs/symbolic-proc/unix/pkl1.tar.Z` | — | — |

Notes:

- The PIMOS tarball also has `pimosobj.tar.Z` and `pimosman.tar.Z` variants.
- `ifs/symbolic-proc/unix/pkl/pkl.tar.Z` returns 500; the abstract page's
  `unix/pkl1.tar.Z` path is the working one.
- `npe9/living-computing` carries the PIM docs PDFs and the Bluespec model
  sources (`pim/asm/pimasm.py`, `pim/bsv/Pim*.bsv`). The model is work in
  progress: the smoke test currently fails (`FAIL: did not halt within 10000
  steps`, with `a2`, `a4_mrb`, `a5`, `a7_skipped` and `mem100` mismatches).
  Generated images and simulator binaries are build products and stay
  untracked; `pim/bsv/run_smoke.sh` is a source script and is tracked.
- No PIM/m microprogramming manual was found in the archive. TR-659 covers
  architecture and implementations; the FGCS 1992 PIM/m paper covers the
  implementation. Record the microprogramming gap rather than inferring it.
