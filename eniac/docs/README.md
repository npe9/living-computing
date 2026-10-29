# ENIAC primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `ENIAC_Operating_Manual_Jun46.pdf` | [ENIAC Operating Manual](https://bitsavers.trailing-edge.com/pdf/univOfPennsylvania/eniac/ENIAC_Operating_Manual_Jun46.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo ENIAC_Operating_Manual_Jun46.pdf` and visually inspect representative text, diagram, and table pages before citing them.
