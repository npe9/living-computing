# Whirlwind I primary-source inventory

`fetch_all.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`; `fetch.sh` remains the minimal initial-corpus fetcher.

The first local source is listed below. `fetch.sh` retrieves it without rewriting the archive bytes, rejects an empty response, validates PDF magic where applicable, and writes `SHA256SUMS`. Add further primary manuals, schematics, diagnostics, and listings here with their edition and provenance.

| local file | source | role |
|---|---|---|
| `Coding_Notes_I_Aug52.pdf` | [Whirlwind Coding Notes I](https://bitsavers.trailing-edge.com/pdf/mit/whirlwind/Coding_Notes_I_Aug52.pdf) | contemporary coding conventions |
| `Whirlwind_Programming_Notes.pdf` | [Whirlwind Programming Notes](https://bitsavers.trailing-edge.com/pdf/mit/whirlwind/WhirlwindPgmgNotes.pdf) | instruction and program guidance |
| `Whirlwind_Paper_Tape_Format.pdf` | [Whirlwind Paper Tape Format](https://bitsavers.trailing-edge.com/pdf/mit/whirlwind/Whirlwind_Paper_Tape_Format.pdf) | loader/media format |
| `Magnetic_Drum_System_WWI_Jun58.pdf` | [Whirlwind I Magnetic Drum System](https://bitsavers.trailing-edge.com/pdf/mit/whirlwind/Magnetic_Drum_System_WWI_Jun58.pdf) | drum storage interface and timing |
| `Whirlwind_I_Description_Apr1955.pdf` | [Whirlwind I Computer Description](https://bitsavers.trailing-edge.com/pdf/mit/whirlwind/Whirlwind_I_descr_Apr1955.pdf) | initial architecture/programming source |

After retrieval, run `shasum -a 256 -c SHA256SUMS`. For PDFs, also run `pdfinfo Whirlwind_I_Description_Apr1955.pdf` and visually inspect representative text, diagram, and table pages before citing them.
