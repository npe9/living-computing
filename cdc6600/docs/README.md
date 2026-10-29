# CDC 6600 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `6600_Computer_System_Reference_Aug63.pdf` | [CDC 6600 Computer System Reference Manual (1963)](https://bitsavers.trailing-edge.com/pdf/cdc/Tom_Hunter_Scans/6600_Computer_System_RefMan_Aug63.pdf) | original model-specific reference |
| `6600_CPU_Training_Vol1_Mar67.pdf` | [CDC 6600 CPU Training Manual, volume 1](https://bitsavers.trailing-edge.com/pdf/cdc/Tom_Hunter_Scans/6600_CPU_TrainingManual_Vol1_Mar67.pdf) | CPU implementation and control |
| `6600_CPU_Training_Vol2_Mar67.pdf` | [CDC 6600 CPU Training Manual, volume 2](https://bitsavers.trailing-edge.com/pdf/cdc/Tom_Hunter_Scans/6600_CPU_TrainingManual_Vol2_Mar67.pdf) | CPU implementation continuation |
| `6000_Series_Reference_Manual_Jul65.pdf` | [Control Data 6000 Series Computer Systems Reference Manual](https://bitsavers.trailing-edge.com/pdf/cdc/Tom_Hunter_Scans/6000_Series_Computer_Systems_RefMan_Jul65.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo 6000_Series_Reference_Manual_Jul65.pdf` and visually inspect representative text, diagram, and table pages before citing them.
