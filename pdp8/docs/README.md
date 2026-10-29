# DEC PDP-8 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Small_Computer_Handbook_1967_68.pdf` | [Small Computer Handbook 1967-68](https://bitsavers.trailing-edge.com/pdf/dec/pdp8/handbooks/SmallComputerHandbook_67-68.pdf) | revision and peripheral coverage |
| `Introduction_to_Programming_1969.pdf` | [Introduction to Programming (1969)](https://bitsavers.trailing-edge.com/pdf/dec/pdp8/handbooks/IntroToProgramming1969.pdf) | programming examples and conventions |
| `1966_PDP8_UsersHandbook.pdf` | [DEC PDP-8 User's Handbook](https://bitsavers.trailing-edge.com/pdf/dec/pdp8/handbooks/1966_PDP8_UsersHandbook.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo 1966_PDP8_UsersHandbook.pdf` and visually inspect representative text, diagram, and table pages before citing them.
