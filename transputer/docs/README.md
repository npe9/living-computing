# IMS T800 primary-source inventory

Run `./fetch.sh` from this directory to retrieve the public archive
copies. The script refuses truncated or non-PDF responses, writes files
under stable names, and produces `SHA256SUMS`. Commit the PDFs and
checksum file together after checking each archive's redistribution terms.

| local file | source | role |
|---|---|---|
| `Transputer_Architecture_Reference_Manual_Jul87.pdf` | [transputer.net book archive](https://www.transputer.net/fbooks/tarch/tarch.pdf) | family architecture, links, boot, and occam execution model |
| `Transputer_Databook_2nd_Ed_1989.pdf` | [transputer.net INMOS archive](https://transputer.net/ibooks/72-trn-203-01/tdata2nd.pdf) | T800 engineering data plus family comparison |

The 1987 architecture manual and 1989 databook describe different
document and possibly silicon revisions. Preserve conflicting timings
and behaviors as revisioned facts until INMOS errata resolves them.

After retrieval, run `pdfinfo` on every PDF and
`shasum -a 256 -c SHA256SUMS`.
