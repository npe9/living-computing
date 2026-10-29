# IBM 701 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `701_Quick_Reference_Card.pdf` | [IBM 701 Quick Reference Card](https://bitsavers.trailing-edge.com/pdf/ibm/701/701_quick-reference-card.pdf) | compact encoding oracle |
| `Buchholz_IBM_701_System_Design_Oct53.pdf` | [Buchholz, IBM 701 System Design](https://bitsavers.trailing-edge.com/pdf/ibm/701/Buchholz_IBM_701_System_Design_Oct53.pdf) | contemporary implementation description |
| `24-6042-1_701_PrincOps.pdf` | [IBM 701 Principles of Operation](https://bitsavers.trailing-edge.com/pdf/ibm/701/24-6042-1_701_PrincOps.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo 24-6042-1_701_PrincOps.pdf` and visually inspect representative text, diagram, and table pages before citing them.
