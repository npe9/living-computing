# Colossus primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Colossus_Tunny_overview.html` | [Colossus and the General Report on Tunny overview](https://rutherfordjournal.org/article030109.html) | source guide; not a substitute for HW 25/4-5 or machine diagrams |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo Colossus_Tunny_overview.html` and visually inspect representative text, diagram, and table pages before citing them.
