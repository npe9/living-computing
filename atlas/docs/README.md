# Atlas primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Atlas_Provisional_Programming_Manual_catalog.html` | [Ferranti Atlas Provisional Programming Manual catalog record](https://www.computinghistory.org.uk/det/15674/Ferranti-Atlas-Provisional-Programming-Manual/) | primary-manual locator only; not an encoding oracle |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo Atlas_Provisional_Programming_Manual_catalog.html` and visually inspect representative text, diagram, and table pages before citing them.
