# IBM 7090 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `A22-6535_7090_Operating_Guide_Jan62.pdf` | [IBM 7090 Operating Guide](https://bitsavers.trailing-edge.com/pdf/ibm/7090/A22-6535_7090_operGde_Jan62.pdf) | operator controls and procedures |
| `C28-6235-2_7090_FAP.pdf` | [IBM 7090 FAP Reference](https://bitsavers.trailing-edge.com/pdf/ibm/7090/C28-6235-2_7090_FAP.pdf) | assembler and listing conventions |
| `C28-6299_IBSYS_Programming_Systems_Analysis_Feb63.pdf` | [IBSYS Programming Systems Analysis](https://bitsavers.trailing-edge.com/pdf/ibm/7090/C28-6299_IBSYS_PgSyAn_Feb63.pdf) | system software interfaces |
| `22-6528-4_7090Manual.pdf` | [IBM 7090 Data Processing System Reference Manual](https://bitsavers.trailing-edge.com/pdf/ibm/7090/22-6528-4_7090Manual.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo 22-6528-4_7090Manual.pdf` and visually inspect representative text, diagram, and table pages before citing them.
