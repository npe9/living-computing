# IBM 1401 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `A24-1401-1_1401_System_Summary_Sep64.pdf` | [IBM 1401 System Summary](https://bitsavers.trailing-edge.com/pdf/ibm/1401/A24-1401-1_1401_System_Summary_Sep64.pdf) | configuration and device summary |
| `A24-6447-0_1401_1460_Instruction_Timing.pdf` | [IBM 1401/1460 Instruction and Timing Summary](https://bitsavers.trailing-edge.com/pdf/ibm/1401/A24-6447-0_1401_1460_Instruction_and_Timing_Summary.pdf) | instruction timing oracle |
| `G24-1477-0_1401_Data_Flow.pdf` | [IBM 1401 Data Flow](https://bitsavers.trailing-edge.com/pdf/ibm/1401/G24-1477-0_1401_dataFlow.pdf) | implementation datapath description |
| `1401_Autocoder_Listing.pdf` | [IBM 1401 Autocoder Listing](https://bitsavers.trailing-edge.com/pdf/ibm/1401/1401_autocoderListing.pdf) | printed software and machine-code evidence |
| `A24-1403-5_1401_Reference_Apr62.pdf` | [IBM 1401 Data Processing System Reference Manual](https://bitsavers.trailing-edge.com/pdf/ibm/1401/A24-1403-5_1401_Reference_Apr62.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo A24-1403-5_1401_Reference_Apr62.pdf` and visually inspect representative text, diagram, and table pages before citing them.
