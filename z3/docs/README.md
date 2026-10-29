# Zuse Z3 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Rojas_Universal_Computer_1998.pdf` | [Rojas, How to Make Zuse's Z3 a Universal Computer](https://www.inf.fu-berlin.de/inst/ag-ki/rojas_home/documents/1997/Universal_Computer.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo Rojas_Universal_Computer_1998.pdf` and visually inspect representative text, diagram, and table pages before citing them.
