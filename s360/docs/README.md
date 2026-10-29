# IBM System/360 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `A22-6821-0_360PrincOps.pdf` | [IBM System/360 Principles of Operation](https://bitsavers.trailing-edge.com/pdf/ibm/360/princOps/A22-6821-0_360PrincOps.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo A22-6821-0_360PrincOps.pdf` and visually inspect representative text, diagram, and table pages before citing them.
