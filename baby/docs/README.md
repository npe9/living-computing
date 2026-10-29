# Manchester Baby / SSEM primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Manchester_Computer_50_SSEM.html` | [University of Manchester Computer 50 SSEM archive](https://www.curation.cs.manchester.ac.uk/computer50/www.computer50.org/index.html?man=true) | institutional technical archive; locate cited contemporary reports before encoding |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo Manchester_Computer_50_SSEM.html` and visually inspect representative text, diagram, and table pages before citing them.
