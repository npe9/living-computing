# EDSAC primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `EDSAC_Tutorial_Guide.pdf` | [Campbell-Kelly, Tutorial Guide to the EDSAC Simulator](https://www.dcs.warwick.ac.uk/~edsac/Software/EdsacTG.pdf) | order-code and Initial Orders guide, explicitly secondary pending a usable scan of the 1951 book |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. Also run
`pdfinfo EDSAC_Tutorial_Guide.pdf` and visually inspect representative
text, diagram, and table pages before citing them.
