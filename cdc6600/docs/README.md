# CDC 6600 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `6000_Series_Reference_Manual_Jul65.pdf` | [Control Data 6000 Series Computer Systems Reference Manual](https://bitsavers.trailing-edge.com/pdf/cdc/Tom_Hunter_Scans/6000_Series_Computer_Systems_RefMan_Jul65.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo 6000_Series_Reference_Manual_Jul65.pdf` and visually inspect representative text, diagram, and table pages before citing them.
