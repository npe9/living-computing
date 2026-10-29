# PIM primary-source inventory

Run `./fetch.sh` from this directory to retrieve the public archive
copies. The script refuses truncated or non-PDF responses, writes files
under stable names, and produces `SHA256SUMS`. Commit the PDFs and
checksum file together after checking the archive's redistribution terms.

| local file | source | role |
|---|---|---|
| `FGCS92_Volume_1.pdf` | [ICOT, FGCS '92 proceedings, volume 1](https://www.bitsavers.org/pdf/icot/Fifth_Generation_Computer_Systems_1992_Volume_1.pdf) | PIM overview and the PIM/p and PIM/m implementation papers |
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
