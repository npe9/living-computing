# IBM System/360 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `A22-6821-6_360_Principles_Jan67.pdf` | [IBM System/360 Principles of Operation, sixth edition](https://bitsavers.trailing-edge.com/pdf/ibm/360/princOps/A22-6821-6_360PrincOpsJan67.pdf) | architectural revision comparison |
| `A22-6825-0_360_Instruction_Timing.pdf` | [IBM System/360 Instruction Timing Information](https://bitsavers.trailing-edge.com/pdf/ibm/360/A22-6825-0_360_Instr_Timing.pdf) | model-dependent timing evidence |
| `A22-6821-0_360PrincOps.pdf` | [IBM System/360 Principles of Operation](https://bitsavers.trailing-edge.com/pdf/ibm/360/princOps/A22-6821-0_360PrincOps.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo A22-6821-0_360PrincOps.pdf` and visually inspect representative text, diagram, and table pages before citing them.
