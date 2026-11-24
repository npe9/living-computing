# AT&T 92010 Hobbit primary-source inventory

`fetch.sh` retrieves every PDF listed in the table and regenerates
`SHA256SUMS`. It rejects truncated or non-PDF responses, writes files
under stable names, and refuses to leave a partial download in place.
Commit the PDFs and checksum file together after checking each archive's
redistribution terms.

| local file | source | role |
|---|---|---|
| `ATT92010_Hobbit_Programmers_Reference_Jan93.pdf` | [AT&T Microelectronics, Programmer's Reference Manual, January 1993](https://bitsavers.trailing-edge.com/components/att/hobbit/ATT92010_Hobbit_Programmers_Reference_Jan93.pdf) | instruction encodings (parcel formats, Tables 1-15 to 1-20), control registers, stack cache, MMU, events, Chapter 4 timings |
| `ATT92010_Hobbit_Microprocessor_Data_Sheet_Dec92.pdf` | [AT&T Microelectronics, Advance Data Sheet, December 1992](https://bitsavers.trailing-edge.com/components/att/hobbit/ATT92010_Hobbit_Microprocessor_Data_Sheet_Dec92.pdf) | package, supply and clock/power points, pin list, bus timing, block diagram |
| `ATT2100_Microprocessor_Hardware_Specification_Mar91.pdf` | [AT&T, ATT2100 Microprocessor Hardware Specification, release 1.7.2, 31 March 1991](https://bitsavers.trailing-edge.com/components/att/hobbit/ATT2100_Microprocessor_Hardware_Specification_Mar91.pdf) | earlier part: same architecture with an unimplemented floating-point status word, reserved floating-point opcodes, and control-register/`CPU`-escape syntax |
| `MicroprocessorReport_v6n2_Hobbit_Feb92.pdf` | [M. Slater, "AT&T Sampling Low-Power 'Hobbit' Processor", *Microprocessor Report* 6:2, 12 February 1992](https://www.ardent-tool.com/CPU/docs/MPR/19920212/060201.pdf) | contemporaneous history: CRISP lineage, Apple's Newton funding and switch to ARM, EO's choice, code-density and branch-folding claims — not an encoding source |

The 1991 specification is an earlier, differently numbered part: it
defines a floating-point accumulator and an FPSW register that the 1992
and 1993 documents neither implement nor list, and it reserves
floating-point opcodes that then trap. Its section numbering also
differs (its Instruction Format is 2.5, not 1.6). Preserve conflicts as
revisioned facts; cite the 1993 manual for the 92010.

The Microprocessor Report article is secondary. It is cited for the
project history and for claims the vendor documents do not make
(Apple's funding, the CRISP-to-Hobbit cache comparison, the 80%
one-parcel claim), never for an encoding.

After retrieval, run `pdfinfo` on every PDF, `shasum -a 256 -c
SHA256SUMS`, and visually inspect the encoding tables and the Chapter 4
timing tables before citing them: the scanned pages carry OCR text that
mangles opcode tables (`5` for `S`, `0` for `O`).

## Not yet acquired

Each of these would outrank the vendor manuals for a claim the corpus
cannot currently make, and each is an acquisition target:

* AT&T Microelectronics' own assembler and linker documentation, and any
  surviving object file (the BeOS DR4 disk images preserved by the BeBox
  community are the likeliest source) — Plan 9's 1st Edition Hobbit
  toolchain is now vendored in [`../tools/`](../tools/README.md), but it
  is Bell Labs' Plan 9 tool, not AT&T's, the release ships no assembler
  backend, and it has no `CLRE`;
* EO's product documentation for the 440 and 880 — for the shipped
  board's clock, memory and part numbers, which no local document
  states;
* the DSP3210 data book — for the dual-CPU/three-DSP BeBox board, now
  reconstructed in [`bebox_hardware.md`](bebox_hardware.md) from Be Labs'
  September 1993 hardware-documentation drafts, the surviving kernels and
  board photographs (no boot ROM dump survives);
* the COMPCON'93 paper "Hobbit: a high-performance, low-power
  microprocessor" and the 1987 CRISP papers (ISCA/COMPCON) — for the
  design history and for the branch-folding and instruction-frequency
  claims now taken from the Microprocessor Report article.
