# DEC VAX-11/780 primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `AA-H307-TE_VAX11_780_Data_Path_Feb79.pdf` | [VAX-11/780 Data Path Description](https://bitsavers.trailing-edge.com/pdf/dec/vax/780/AA-H307-TE_VAX-11_780_Data_Path_Description_197902.pdf) | CPU datapath and micro-operation detail |
| `EK-11780-UG-001_Hardware_Users_Guide_Feb79.pdf` | [VAX-11/780 Hardware User's Guide](https://bitsavers.trailing-edge.com/pdf/dec/vax/780/EK-11780-UG-001_VAX-11_780_Hardware_Users_Guide_197902.pdf) | system hardware interfaces |
| `EK-MM780-TD-001_Cache_and_SBI_Apr78.pdf` | [VAX-11/780 Translation Buffer, Cache and SBI Control](https://bitsavers.trailing-edge.com/pdf/dec/vax/780/EK-MM780-TD-001_Translation_Buffer_and_Cache_and_SBI_Control_Technical_Description_197804.pdf) | memory-system timing and control |
| `EK-FP780-TD-001_Floating_Point_Dec78.pdf` | [FP780 Technical Description](https://bitsavers.trailing-edge.com/pdf/dec/vax/780/EK-FP780-TD-001_FP780_Technical_Description_197812.pdf) | floating-point implementation |
| `VAX_Architecture_Handbook_Vol1_1977.pdf` | [VAX Architecture Handbook, volume 1](https://bitsavers.trailing-edge.com/pdf/dec/vax/handbook/VAX_Architecture_Handbook_Vol1_1977.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo VAX_Architecture_Handbook_Vol1_1977.pdf` and visually inspect representative text, diagram, and table pages before citing them.
