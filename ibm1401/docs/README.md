# IBM 1401 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `A24-1403-5_1401_Reference_Apr62.pdf` | [IBM 1401 Data Processing System Reference Manual](https://bitsavers.trailing-edge.com/pdf/ibm/1401/A24-1403-5_1401_Reference_Apr62.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo A24-1403-5_1401_Reference_Apr62.pdf` and visually inspect representative text, diagram, and table pages before citing them.
