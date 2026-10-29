# Symbolics 3600 primary-source inventory

Run `./fetch.sh` from this directory to retrieve the public Bitsavers
copies. The script refuses truncated or non-PDF responses, writes files
under stable names, and produces `SHA256SUMS`. Commit the PDFs and
checksum file together after checking the archive's redistribution terms.

| local file | source | role |
|---|---|---|
| `3600_TechnicalSummary_Feb83.pdf` | [Bitsavers mirror](https://bitsavers.trailing-edge.com/pdf/symbolics/3600_series/3600_TechnicalSummary_Feb83.pdf) | initial architectural description |
| `Lisp_Machine_Summary_3600_Aug83.pdf` | [Bitsavers mirror](https://bitsavers.trailing-edge.com/pdf/symbolics/3600_series/990075_Lisp_Machine_Summary_3600_Edition_Aug83.pdf) | programmer-visible machine summary |
| `3600_Microcode_Dec83.pdf` | [Bitsavers mirror](https://bitsavers.trailing-edge.com/pdf/symbolics/3600_series/3600_Microcode_Dec83.pdf) | primary microcode listing |
| `3600_Block_Diagram_1985.pdf` | [Bitsavers mirror](https://bitsavers.trailing-edge.com/pdf/symbolics/3600_series/3600_Block_Diagram_1985.pdf) | board/datapath relationships |
| `3600_Series_Basic_Field_Maint_Jul86.pdf` | [Bitsavers mirror](https://bitsavers.trailing-edge.com/pdf/symbolics/3600_series/Symbolics_3600_Series_Basic_Field_Maint_Jul86.pdf) | later 3600-series hardware and maintenance evidence |
| `Lisp_Machine_Hardware_Memos.pdf` | [Bitsavers mirror](https://bitsavers.trailing-edge.com/pdf/symbolics/3600_series/Lisp_Machine_Hardware_Memos.pdf) | design memoranda; claims require memo/date attribution |

These documents span 1983-1986. Record machine and board revisions for
every hardware claim; the later field-maintenance manual cannot silently
override the February 1983 target.

After retrieval, run `pdfinfo` on every PDF and
`shasum -a 256 -c SHA256SUMS`.
