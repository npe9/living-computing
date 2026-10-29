# DEC PDP-11/20 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `1120_System_Manual.pdf` | [PDP-11/20 System Manual](https://bitsavers.trailing-edge.com/pdf/dec/pdp11/1120/1120_SystemManual.pdf) | system-level implementation |
| `KA11_Processor_Manual_Sep70.pdf` | [KA11 Processor Manual](https://bitsavers.trailing-edge.com/pdf/dec/pdp11/1120/KA11_ProcessorMan_Sep1970.pdf) | processor logic and timing |
| `1120_System_Schematics_Feb70.pdf` | [PDP-11/20 System Schematics](https://bitsavers.trailing-edge.com/pdf/dec/pdp11/1120/1120_SystemSchems_Feb70.pdf) | hardware implementation diagrams |
| `PDP-11_Handbook_Second_Edition_1970.pdf` | [PDP-11 Handbook, second edition](https://bitsavers.trailing-edge.com/pdf/dec/pdp11/1120/PDP-11_Handbook_Second_Edition_1970.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo PDP-11_Handbook_Second_Edition_1970.pdf` and visually inspect representative text, diagram, and table pages before citing them.
