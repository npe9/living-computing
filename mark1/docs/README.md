# Manchester Mark 1 / Ferranti Mark 1 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Manchester_Mark_1_documents.html` | [University of Manchester Mark 1 document index](https://curation.cs.manchester.ac.uk/digital60/www.digital60.org/birth/manchestercomputers/mark1/documents/index.html) | institutional index to Turing's handbook and facsimiles; not itself an encoding oracle |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo Manchester_Mark_1_documents.html` and visually inspect representative text, diagram, and table pages before citing them.
