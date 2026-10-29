# DEC PDP-11/20 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `PDP-11_Handbook_Second_Edition_1970.pdf` | [PDP-11 Handbook, second edition](https://bitsavers.trailing-edge.com/pdf/dec/pdp11/1120/PDP-11_Handbook_Second_Edition_1970.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo PDP-11_Handbook_Second_Edition_1970.pdf` and visually inspect representative text, diagram, and table pages before citing them.
