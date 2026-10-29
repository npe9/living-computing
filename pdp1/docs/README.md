# DEC PDP-1 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `F15B_PDP1_Handbook_1961.pdf` | [DEC PDP-1 Handbook](https://bitsavers.trailing-edge.com/pdf/dec/pdp1/F15B_PDP1_Handbook_1961.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo F15B_PDP1_Handbook_1961.pdf` and visually inspect representative text, diagram, and table pages before citing them.
