# IAS Machine primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Planning_and_Coding_Part_II_Vol_II_Apr48.pdf` | [Planning and Coding of Problems, part II volume II](https://bitsavers.trailing-edge.com/pdf/ias/Planning_and_Coding_of_Problems_for_an_Electronic_Computing_Instrument_Part_II_Volume_II_Apr48.pdf) | original programming and order-code design |
| `IAS_Final_Report_Jan54.pdf` | [IAS Electronic Computer Project Final Report](https://bitsavers.trailing-edge.com/pdf/ias/IAS_Final_Report_Jan54.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo IAS_Final_Report_Jan54.pdf` and visually inspect representative text, diagram, and table pages before citing them.
