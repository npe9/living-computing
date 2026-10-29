# UNIVAC I primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Preliminary_Description_UNIVAC.pdf` | [Preliminary Description of the UNIVAC](https://bitsavers.trailing-edge.com/pdf/univac/univac1/Preliminary_Description_of_the_UNIVAC.pdf) | early architecture revision |
| `UNIVAC1_Maintenance_Manual_Jan58.pdf` | [UNIVAC I Maintenance Manual](https://bitsavers.trailing-edge.com/pdf/univac/univac1/UNIVAC1_Maintenance_Manual_Jan58.pdf) | hardware logic and maintenance |
| `UNIVAC_Programming_Jan53.pdf` | [UNIVAC Programming Manual (1953)](https://bitsavers.trailing-edge.com/pdf/univac/univac1/UNIVAC_Programming_Jan53.pdf) | original instruction and coding guidance |
| `UNIVAC1_Reference_Card.pdf` | [UNIVAC I Reference Card](https://bitsavers.trailing-edge.com/pdf/univac/univac1/UnivacI_RefCard.pdf) | compact encoding oracle |
| `UNIVAC1_Operating_Manual_1954.pdf` | [UNIVAC I Operating Manual](https://bitsavers.trailing-edge.com/pdf/univac/univac1/UNIVAC1_Operating_Manual_1954.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo UNIVAC1_Operating_Manual_1954.pdf` and visually inspect representative text, diagram, and table pages before citing them.
