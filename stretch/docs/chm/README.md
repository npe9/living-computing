# Computer History Museum scans, fetched 2026-11-07

Downloaded from the CHM text archive,
`https://archive.computerhistory.org/resources/text/IBM/Stretch/pdfs/<box-folder>/<catalog>.pdf`.
None of these is mirrored on bitsavers. CHM catalog pages do not link
the PDFs: they were found by probing that URL pattern against catalog
numbers. Most are from the Kolsky papers (CHM accession X3021.2005).

**Only 102634375 has been read in the ink so far.** Every other title
below is the CHM catalog record's, not this project's reading. Rule 4
applies: cite a page only after reading it.

| catalog | box-folder | pp | catalog title / content | why it matters |
|---|---|---|---|---|
| **102634375** | 09-05 | 3 | **T. C. Chen, "The Multiplier Register on the 7030", memo to Dept. 271, 7 Sep 1961. READ.** | $MR and STM exist on K-2 and later only, not on X-1 (LASL), the 7950 or K-1 (LRL). $MR's exponent is $R.48-59 ($L.112-123), and its fraction and sign are the last 52 bits of the E-box D register. LMR = LFT's code 10010; *+ = 01110; STM = 11110. LFT, *+, M+, M+MG and D/ take two look-ahead levels on K-1, and one on improved machines with the operand in core. Times: LFT 2.8-4.4 µs on K-1; LMR 0.9-1.2 µs on K-2; *+ 6.5 µs on K-1, 3.9-4.5 µs on K-2. VFL side effects on $MR (p.2 item 8). Bears directly on MCP's STM probes (p.117 line 7, p.122 line 7). |
| 102634064 | 05-09 | 5 | Kolsky, "Simplified timing rules for SIGMA" | timing oracle candidate |
| 102632583 | 06-19 | 34 | Dirac/Bahnsen, "Proposal for a Sigma lookahead system", Dec 1957 | look-ahead design |
| 102632589 | 06-19 | 3 | look-ahead address register and forwarding | look-ahead design |
| 102632591 | 06-19 | 33 | Bloch, Sigma simulation | timing simulation |
| 102634322 | 15-26 | 86 | Cocke/Kolsky, "Stretch virtual memory concept and timing simulation program", with an SM-2 simulator appendix | may be a longer edition of TR00.03000.703 (42 pp) in docs/ |
| 102635106 | 09-06 | 17 | simulator result report | timing |
| 102635128 | 09-06 | 13 | simulator result report | timing |
| 102634001 | 03-07 | 2 | timing chart | timing |
| 102634092 | 05-10 | 3 | timing chart | timing |
| 102635057 | 06-04 | 6 | Bloch et al., "Timing in Sigma" | timing |
| 102634095 | 05-10 | 2 | data-flow schematic | E-box structure |
| 102632537 | 06-16 | 1 | VFL hardware flow | VFL unit |
| 102632307 | 06-24 | 36 | Brooks, RC-213, "Execute operations: a fourth mode" | EX / EXIC design |
| 102632361 | 06-10 | 15 | high-speed disk definition | the 353 |
| 102632367 | 06-10 | 18 | Exchange maintenance console controls | the Exchange |
| 102633953 | 03-03 | 104 | STRAP-1 manual, LASL 1959 | assembler history |
| 102634364 | 09-05 | 4 | SEVA | |
| 102634372 | 09-05 | 3 | index arithmetic bulletin | |
| 102634373 | 09-05 | 6 | progressive indexing bulletin | |

**Also at CHM but catalog-only, so it needs a request** (docs/archival_inventory.md
"CHM"): the Lowell Wood (LRL) collection, X2462.2002. It holds the VFL
diagnostic JB AV1C, the timing programs KA AT1 RAWSPEED, KA BT1 MEMTIM
and JA AT1 BASICTIM, the PAU diagnostics KC AF2/AF2B, and the SAU
diagnostic KC AV2B (records 102698893, -896 and -897). It also holds
diagnostic reference manuals, CE manuals of instruction and installation
manuals (102698889-91). Also catalog-only: the FIC "Stretch Manual of
Operation - Preliminary", May 1958, 317 pp (102633186).

The owner's untracked `docs/102634360 (1).pdf` is CHM 102634360,
from box-folder 09-05 (same byte count, 690,934).
