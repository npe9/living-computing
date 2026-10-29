# Burroughs B5000 primary-source inventory

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `B5000_Descriptor_Definition_1961.pdf` | [The Descriptor: A Definition of the B 5000 Information Processing System](https://bitsavers.trailing-edge.com/pdf/burroughs/LargeSystems/B5000_5500_5700/5000-20002-P_The_Descriptor_-_A_Definition_of_the_B_5000_Information_Processing_System_196102.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo B5000_Descriptor_Definition_1961.pdf` and visually inspect representative text, diagram, and table pages before citing them.
