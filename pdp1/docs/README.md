# DEC PDP-1 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `F-16_PDP-1_Instruction_List_Sep61.pdf` | [PDP-1 Instruction List (1961)](https://bitsavers.trailing-edge.com/pdf/dec/pdp1/F-16_PDP-1_Instruction_List_196109.pdf) | compact encoding oracle |
| `F17_PDP1_Maintenance_1962.pdf` | [PDP-1 Maintenance Manual (1962)](https://bitsavers.trailing-edge.com/pdf/dec/pdp1/F17_PDP1Maint_1962.pdf) | logic and maintenance description |
| `F25_PDP1_IO.pdf` | [PDP-1 Input-Output Systems](https://bitsavers.trailing-edge.com/pdf/dec/pdp1/F25_PDP1_IO.pdf) | device and I/O timing |
| `F15B_PDP1_Handbook_1961.pdf` | [DEC PDP-1 Handbook](https://bitsavers.trailing-edge.com/pdf/dec/pdp1/F15B_PDP1_Handbook_1961.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo F15B_PDP1_Handbook_1961.pdf` and visually inspect representative text, diagram, and table pages before citing them.
