# DSP3210 documentation: acquisition manifest

Collected 2026-11-24 for the Hobbit BeBox's three AT&T WE DSP3210s
(`../bebox_hardware.md` §13, `../dsp3210.md`).

The PDFs are on disk in this directory and kept **out of git**
(`.gitignore`). They are scans of 1991-93 AT&T Microelectronics
publications that show no redistribution terms, and the repository is
public. This follows `../devices/MANIFEST.md`. `sh fetch.sh` downloads
whatever is missing and checks every file against `SHA256SUMS`;
`sh fetch.sh --check` only checks. A fresh fetch into an empty directory
reproduced the five DSP3210 checksums. Nothing downloaded was executed.

## Source

The five DSP3210 files come from <https://github.com/Wrangler491/AA3000-DSP>, a
hobbyist's repository for the Amiga AA3000's DSP3210 daughter board. It
has no licence file. `fetch.sh` pins commit
`bfaf15154222735eb156f13b0f6ea440225e459d` (2024-08-23).

The uploader split the manual into four page ranges. The scans have no
text layer, so every value was read from the page image
(`pdftoppm -r 150`), with OCR used only to find pages.

**Why this is the right edition.** Be's own DSP header for the board
(`mmio.h` in Be's sources, quoted only by page here) cites "DSP3210
Information Manual" pages 9-4/9-5, 9-20 and 9-23 for the MMIO register
layout. Those pages carry those registers in this September 1991 edition,
and its table of contents matches.

**The codec.** `AD1849K.pdf` comes from the ALSA project's manuals
mirror, <https://sunsite2.icm.edu.pl/Linux/alsa/manuals/ad/1063_0.pdf>.
It is Analog Devices' own data sheet and carries their copyright, with
no redistribution terms, so it stays out of git like the rest. The
analog.com URLs tried for it (`.../obsolete-data-sheets/AD1849.pdf`,
`.../data-sheets/AD1849.pdf`) failed; the Aalborg University component
library also lists one. Why this part: Be's `audio.tbd` on the Nov 1994
disk says the frame control word "is exactly what the AD1849 codec
expects" (`../dsp3210.md`, "The audio path"). The data sheet's page
numbers are printed (`-11-`); the page index of the PDF is the same.

## Held

| File | What | Pages | Bytes | SHA-256 |
|---|---|---|---|---|
| `DSP3210_Information_Manual-1-46.pdf` | *WE DSP3210 Digital Signal Processor Information Manual*, AT&T Microelectronics, September 1991: front matter, ch. 1-3 | PDF 1-46 of the 288 | 10,156,511 | `16ea091aa6363c7e0346286cca5a07810729493335e39b6c874cf807773ceaab` |
| `DSP3210_Information_Manual-47-134.pdf` | same: ch. 3-4 (instruction set) | 47-134 | 18,384,128 | `8c915125849e752812f8e60be8e00e97acad0b52308f61c647a450cd5267fc3c` |
| `DSP3210_Information_Manual-135-226.pdf` | same: ch. 5-9 | 135-226 | 21,308,846 | `c47e6be510ca60069ff7f8e566aa0d109fb14e6b0b65dfaf8cd1ac78d9332875` |
| `DSP3210_Information_Manual-227-288.pdf` | same: ch. 10-12 (encoding tables, registers), Appendix A (boot ROM listing) | 227-288 | 12,146,664 | `b04ee4bda3b1ec8e795453e38d5f9088dd33074fcf13d4b14696b3ccf2cb2069` |
| `ATT_DSP3210_DSP_The_Multimedia_Solution.pdf` | AT&T data sheet *DSP3210 Digital Signal Processor: The Multimedia Solution* (39 pp.) | whole | 2,975,600 | `1de05d033187bb7b230c34bc509056ccc202bb4b2fb5addbbaf53b8f1612e95f` |
| `AD1849K.pdf` | Analog Devices *AD1849K Serial-Port 16-Bit SoundPort Stereo Codec* data sheet, REV. 0 (PDF created 1997) | 28 pp. | 300,619 | `d40df2a808eb0b61d56a9e52d4284cc84313606a754680d6449c1f6532dfc44b` |

**Page numbers.** The page numbers printed in the manual are chapter-page
(e.g. 4-31). They map to the page index of the whole 288-page scan as
follows (PDF page = printed page number within the chapter + offset):

| Chapter | Offset |
|---|---|
| 3 | +32 |
| 4 | +48 |
| 5 | +136 |
| 6 | +142 |
| 7 | +162 |
| 8 | +178 |
| 10 | +228 |
| 12 | +250 |

Appendix A is at PDF 269-272. Subtract the first page of a file's range
(minus one) to get the index within that file. For example, p. 4-31 is
scan page 79, which is page 33 of `-47-134.pdf`.

## Looked at, not taken

- The datasheetarchive copies of the DSP3210 data sheet (27 and 39 pp.)
  duplicate the data sheet held above.
- Dave Haynie's A3000+ documents describe the Amiga board, not the chip.
- The Tektronix 070-8737-00 support manual covers a DSP3210 inside a
  Tek instrument and adds nothing about the instruction set.
- bitsavers `components/att/dsp/` holds DSP16 and DSP32C material only.
  The DSP32C manual shares the DAU's float format, but it was not needed
  once the 3210 manual was found.
