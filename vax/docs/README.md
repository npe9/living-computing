# DEC VAX-11/780 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `VAX_Architecture_Handbook_Vol1_1977.pdf` | [VAX Architecture Handbook, volume 1](https://bitsavers.trailing-edge.com/pdf/dec/vax/handbook/VAX_Architecture_Handbook_Vol1_1977.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo VAX_Architecture_Handbook_Vol1_1977.pdf` and visually inspect representative text, diagram, and table pages before citing them.
