# Cray-1 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `2240003E_CRAY-1_Pocket_Card_1977.pdf` | [CRAY-1 Pocket Card (1977)](https://bitsavers.trailing-edge.com/pdf/cray/CRAY-1/2240003E_CRAY-1_Pocket_Card_1977.pdf) | compact instruction and register oracle |
| `CRAY-1_Preliminary_Reference_RevA_Jun75.pdf` | [CRAY-1 Preliminary Reference, revision A](https://bitsavers.trailing-edge.com/pdf/cray/CRAY-1/CRAY-1_PrelimRefRevA_Jun75.pdf) | pre-production architecture revision |
| `Nelson_Timing_Codes_CRAY-1_May81.pdf` | [Timing Codes on the CRAY-1](https://bitsavers.trailing-edge.com/pdf/cray/CRAY-1/Nelson_TimingCodesOnTheCray-1_May81.pdf) | documented timing evidence |
| `2240004C_CRAY-1_Hardware_Reference_Nov77.pdf` | [CRAY-1 Hardware Reference Manual](https://bitsavers.trailing-edge.com/pdf/cray/CRAY-1/2240004C_CRAY-1_Hardware_Reference_Nov77.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo 2240004C_CRAY-1_Hardware_Reference_Nov77.pdf` and visually inspect representative text, diagram, and table pages before citing them.
