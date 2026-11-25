# ATT92020 sources: acquisition manifest

Collected 2026-11-24 for [`../att92020.md`](../att92020.md), which
establishes how the ATT92020 differs from the ATT92010 the models follow.

The PDFs are held on disk in this directory but kept **out of git**
(`.gitignore`): they are *Microprocessor Report* articles, © MicroDesign
Resources, on a UC Irvine course mirror that states no redistribution
terms, and the repository is public.  This is the pattern of
`../devices/MANIFEST.md`.  `sh fetch.sh` downloads whatever is missing and
checks every file against `SHA256SUMS` (`sh fetch.sh --check` only
checks).  They were fetched with plain `curl` (generic user agent) and
re-fetched by `fetch.sh` to confirm the checksums.  Nothing downloaded was
executed.

**No AT&T document for the 92020 was found.**  Everything here is
contemporaneous trade press (secondary).  Page numbers are the article's
own (each article's PDF page N is its page N).

## Held

| File | What it is | Pages cited | Bytes | SHA-256 |
|---|---|---|---|---|
| `MPR_v7n14_Hobbit_Family_Oct93.pdf` | Linley Gwennap, "AT&T Expands Hobbit Family", *Microprocessor Report* 7:14, 25 Oct 1993 (Microprocessor Forum report) | p. 1: 92020S binary- and pin-compatible with the 92010, prefetch buffer 3K to 6K, the Wait For Interrupt instruction, 16 vs 13.5 Dhrystone MIPS at 20 MHz, 210 mW; 92020M multiplexed bus ("each transaction requires an extra cycle"); p. 2: 92020MX = 92020M with a 3K cache, 0.6 µm process, die sizes, 132-pin PQFP or 144-pin TQFP, Table 1; p. 3: prices | 241,528 | `f5be588f580365835f6670045d77cd4f40fa39a12a03a68b7f220d1818ffec5e` |
| `MPR_v8n1_PDAs_Begin_Shipping_Jan94.pdf` | "PDAs Begin Shipping in 1993", *Microprocessor Report* 8:1, 24 Jan 1994 | p. 4: the 92020 parts are "derivatives of its existing 92010 CPU"; the 92020S "uses a larger on-chip cache"; NEC waits for the next-generation Hobbit | 169,632 | `32e5838c4de78452ff53093b1e8dfa0e97daf469b538b1f74815e871afb0d6bb` |

URLs (under `https://www.cecs.uci.edu/~papers/mpr/MPR/ARTICLES/`):
`071403.pdf`, `080104.pdf`.

## Cited, not held (web pages)

| Source | Date | What it gives | URL |
|---|---|---|---|
| AT&T Microelectronics press release, "AT&T Expands 92K Hobbit Microprocessor Family", reprinted by the Pen-Based Computing History Museum | 18 Oct 1993 | the vendor's own words: 92020S/M/MX MIPS and MIPS/W; 92020S "binary- and pin-compatible" with the 92010; a new "wait-for-interrupt" instruction for PenPoint's idle; 20 MHz at 3.3 V, 30 MHz at 5 V; 132-pin PQFP or 144-pin TQFP; JTAG on all parts | <https://penbasedcomputing.com/?p=1995> (behind a JavaScript check; read through a fetch tool, not curl) |
| CBR Staff Writer, "HOT CHIPS: AT&T's SECOND-GENERATION HOBBITS…", *Computer Business Review* | 17 Oct 1993 | 92020S: "6Kb three-way set-associative instruction cache, 256-byte stack cache", pin-compatible, 210 mW active, "one microWatt in sleep mode"; 92020M and MX prefetch buffers 6Kb and 3Kb (it calls the MX "92020MT" once) | <https://www.techmonitor.ai/technology/hot_chips_atts_second_generation_hobbits> (curl, read 2026-11-24) |
| "The AT&T Hobbit Enters Its Second Generation", *Byte*, Jan 1994 (Wikipedia cites P. Statt, p. 105), transcribed on the Higher Intellect wiki | Jan 1994 | 92020S "6-KB prefetch buffer as opposed to the 3-KB buffer on the 92010", less power, works with the 92010's support chips except the ISA controller | <https://wiki.preterhuman.net/The_AT%26T_Hobbit_Enters_Its_Second_Generation_(01/1994)> (curl, oldid 103546) |
| Be Labs, "INTRODUCTION: The Be Machine and the BeBus", rev. 9/15/93, marked "CONFIDENTIAL: Be Labs, Inc." (page scans `hobbit/build/bebox/docscans/intro1.jpg`, `intro2.jpg`; held off git by the BeBox agent, `hobbit/docs/bebox/MANIFEST.md` on branch `worktree-agent-aeb73561b39e2ec97`) | 15 Sep 1993 | "two 25 MHz CPU's (ATT 92010 "Hobbit" chips) and three 50 MHz DSP's (ATT DSP 3210 chips)"; a 25 MHz, 32-bit synchronous BeBus with arbitrated masters | read from the page image |
| johnrash/bebox, `design/hardware.md` (MIT), a Haiku BeBox emulator | commit `e1986e6e` (2026-10-21; repository HEAD `938296be`, 2026-10-22) | "two AT&T 92010 at 25 MHz. ID register 0x1000003b (mask 2); the November 1994 kernel has extra code for the 92020 (0x0e33d03b)" | <https://github.com/johnrash/bebox/blob/e1986e6e1e286ec776670bbf808629d7cdb5ec32/design/hardware.md> |
| Thom Holwerda, "Planets Align: Rare Hobbit BeBox Offered and Sold", OSNews | 28 Jan 2009 | an eBay Hobbit BeBox "powered by two AT&T Hobbit processors (ATT92010)" and three DSP3210s | <https://www.osnews.com/story/20869/planets-align-rare-hobbit-bebox-offered-and-sold/> |

## Looked at, not taken

- `bitsavers.org/components/att/hobbit/`: only the three 92010/2100
  documents already in `../` (listing read 2026-11-24).
- `bitsavers.org/components/att/1995_ATT_Product_Selection_Guide.pdf`
  (6,940,311 bytes, 94 pages): its text layer has no "Hobbit", "9201x" or
  "9202x"; the OCR was not checked page by page, so this is not final.
  The 1993 selection guide was already checked the same way
  (`../devices/MANIFEST.md`).
- MPR 6:14 (`061403.pdf`, 28 Oct 1992) and 6:15 (`061509.pdf`, 18 Nov
  1992): 92010-era; 061509 only anticipates that "future versions of the
  Hobbit processor increase their on-chip cache".
- sowerbutts.com/bebox/hobbit.htm: describes the 92010 and lists the
  December 1992 9201x data sheets; it never mentions the 92020.

## Not found

Searched 2026-11-24 (web search for "ATT92020", "92020S", "92020"
with "Hobbit", "wait for interrupt", "errata"; bitsavers `components/att/`;
archive.org metadata search for "hobbit 92020" and for *Byte* January
1994):

- **The ATT92020S/M/MX data sheets and any 92020 programmer's reference
  or supplement.**  The press release says samples were available in
  October 1993, so they existed.
- **92010 or 92020 errata.**  No AT&T errata sheet for either part
  surfaced.
- **The "EOS" / 9202x family documents** (92021M, 92021MX, 92024M data
  sheets), and the 9201x companion data sheets (December 1992), already
  listed as not found in `../devices/MANIFEST.md`.
- **The Microprocessor Forum paper** (19 Oct 1993, Rob Franzo) and any
  Hot Chips V (August 1993) Hobbit material; the Computer History
  Museum's Hot Chips 1989-1993 collection (catalog 102773945) may hold
  the latter.
- ***Byte*, January 1994** as a scan (archive.org's `byte-magazine`
  collection has no January 1994 issue).
- **MetaWare High C for Hobbit documentation**, which would define the
  `-mask5` and `-nodqm` options Be's kernels were built with
  (`../att92020.md`, "Be's kernels").
