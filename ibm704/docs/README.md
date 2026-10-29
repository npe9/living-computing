# IBM 704 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `704_FORTRAN_Programmers_Reference_Oct56.pdf` | [IBM 704 FORTRAN Programmer's Reference](https://bitsavers.trailing-edge.com/pdf/ibm/704/704_FortranProgRefMan_Oct56.pdf) | original software and object conventions |
| `704_Schematics_Vol1.pdf` | [IBM 704 Schematics, volume 1](https://bitsavers.trailing-edge.com/pdf/ibm/704/704_schemVol1.pdf) | hardware implementation diagrams |
| `704_Schematics_Vol2.pdf` | [IBM 704 Schematics, volume 2](https://bitsavers.trailing-edge.com/pdf/ibm/704/704_schemVol2.pdf) | hardware implementation diagrams |
| `704_Schematics_Vol4.pdf` | [IBM 704 Schematics, volume 4](https://bitsavers.trailing-edge.com/pdf/ibm/704/704_schemVol4.pdf) | hardware implementation diagrams |
| `24-6661-2_704_Manual_1955.pdf` | [IBM 704 Manual of Operation](https://bitsavers.trailing-edge.com/pdf/ibm/704/24-6661-2_704_Manual_1955.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo 24-6661-2_704_Manual_1955.pdf` and visually inspect representative text, diagram, and table pages before citing them.
