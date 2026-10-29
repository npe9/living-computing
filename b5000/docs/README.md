# Burroughs B5000 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `5000-21005_B5000_Operating_Characteristics_1963.pdf` | [B5000 Operating Characteristics (1963)](https://bitsavers.trailing-edge.com/pdf/burroughs/LargeSystems/B5000_5500_5700/5000-21005_B5000_operChar_1963.pdf) | processor, memory, and I/O characteristics |
| `118991660_B5000_System_Special_Instructions_1965.pdf` | [B5000 System Special Instructions (1965)](https://bitsavers.trailing-edge.com/pdf/burroughs/LargeSystems/B5000_5500_5700/118991660_B5000_SysSpecialInstructions_196502.pdf) | privileged and system instruction supplement |
| `B5000_Descriptor_Definition_1961.pdf` | [The Descriptor: A Definition of the B 5000 Information Processing System](https://bitsavers.trailing-edge.com/pdf/burroughs/LargeSystems/B5000_5500_5700/5000-20002-P_The_Descriptor_-_A_Definition_of_the_B_5000_Information_Processing_System_196102.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo B5000_Descriptor_Definition_1961.pdf` and visually inspect representative text, diagram, and table pages before citing them.
