> **STATUS: UNVERIFIED FINDING AID.** A research agent's plan, 2026-11-16, for
> IBM's 7030 FORTRAN IV and the BSS loader path. Claims are tagged [INK],
> [OCR], [REPO-INK], [DL] or [UNVERIFIED]; only [INK] was seen in a page image,
> and even those must be re-read before they are cited. Re-checked in the ink
> by the main session: C22-6728-1 printed p.241 (generator-deck origin
> "not 1000(10)" is an error; the TOFC memory-address and size fields are for
> the FORTRAN compiler). 7090 material is an ANALOGUE, never the target.

# 7030 FORTRAN IV and the BSS path under MCP: what it takes

Research notes, 2026-11-16. Nothing in the repo was changed. Stretch only.

## 0. Labels used on every claim

| label | meaning |
|---|---|
| **[INK]** | I viewed the page image this session. The printed page is cited. |
| **[OCR]** | Tesseract or a PDF text layer read this session. A finding aid only; numbers in it are unreliable. Example: tesseract gave "38,0" for 38₁₀ on C22-6751 p.24. |
| **[REPO-INK]** | A repo document says it was read in the ink. I did not re-read it. Usually `docs/bss_loader_spec.md` (the "spec"). |
| **[DL]** | Downloaded this session and read or grepped. The local path is given. |
| **[UNVERIFIED]** | My recollection, or a search-engine summary. |

**Pages I viewed in the ink this session:**

- C22-6751 pp.15, 17, 23, 24, 28, 31, 34
- C22-6729 p.7
- C22-6728-1 pp.240, 241
- AD0646577 printed p.46 (PDF 50)
- AD0685715 printed p.79 (PDF 87) and p.89 (PDF 97)

All other C22-6751 pages (1-37) were read in OCR only. The OCR is at
`/private/tmp/claude-501/-Users-npe-src-living-computing/cafb2b5a-a625-41ec-b286-ef7f699a9ef0/scratchpad/f4/o-NN.txt`,
and 200-dpi images of the same pages are at `.../scratchpad/f4/h-NN.png`.

**Downloads** are under
`/private/tmp/claude-501/-Users-npe-src-living-computing/cafb2b5a-a625-41ec-b286-ef7f699a9ef0/scratchpad/`:

| folder | what it holds |
|---|---|
| `dl_cozx/` | `fortran.lst`, and `ibsys.tar.gz` extracted to `x/` |
| `dl_bs/` | the 7090 manuals |
| `dl_allen/cgo.pdf` | Allen's CGO 2003 keynote |
| `dl_osti/` | the three LASL decks |

---

## 1. BSS: the 7030 format and loader, what the repo has, what is missing, and the 7090 analogue

### 1.1 What IBM's documents say

The repo's `docs/bss_loader_spec.md` is thorough and page-cited. I re-derived nothing from it, and everything in 1.1 is **[REPO-INK]** unless marked otherwise.

**Two programs (C28-6379-0 p.3).**
- MCP's *resume load* program, with the loader as a subroutine.
- The *BSS processor*. In a FORTRAN environment it runs first as "a preprocessor to the MCP loader". It assigns storage, fetches library routines from disk, resolves transfer vectors, builds the relocation tables, prints the storage map, and passes control to resume load.

**Two ways to reach BSS (C28 p.7).**
- As the last link of the FORTRAN chain.
- Alone, through `B TYPE,GO,FORTRAN`.
- The March 1963 listing implements the second: job control rewrites a GO job's chain name FORTRAN as `BSS` (L p.271 ll.46-50). I confirmed the code lines in `decks/mcp_bootstrap_p271.strap` ("INTERPRET GO, AS CMPILGO,... AND FORTRAN AS BSS") **[REPO transcription, checked against print by the suite]**.

**The chain as printed.** C22-6729 p.7, Fig. 1, the bottom table **[INK]**:

| request level | MCP chain |
|---|---|
| FORTRAN IV | LPC, STRAP, LPC, BSS |
| SMAC II | LPC, STRAP, LPC |
| SMAC I | PPC, STRAP, LPC |
| STRAP | STRAP |

- "LPC" is spelled out on the diagram's side bar as "LANGUAGE PROCESSOR COORDINATOR".
- "PPC" is not expanded anywhere on the page.
- So BSS is the fourth link of a FORTRAN chain, and only of that chain.

**Card classes.**
- The March 1963 loader (`ATBL`) has 15. The 1964 manuals have 18, adding the relocatable octal cards K, A and Z. The spec's §3 table covers both.
- Card formats used by FORTRAN, cross-checked in C22-6751 App. A pp.32-34 (p.34 **[INK]**: FORTRAN Branch card, cols 1-5 ID / sequence / checksum / bit count, cols 6-72 unused):
  - FORTRAN Program card 5,6,7,9
  - Common Definition 5,7,8,9
  - Relocatable Instruction 5,7,9
  - Relocatable Data 6,7,8,9
  - FORTRAN Branch 5,6,7,8,9
- Relocation bits: `0`, `1xa0`, `1xa10`, `1xa11i`. The listing sides with C28 against C22-6728 (spec C2).

**The object-module ABI** (C22-6751 ch.13; p.31 **[INK]**).

The deck holds, in order (p.30, OCR):
1. a program card;
2. common definition cards ("vital that the original ordering ... be preserved");
3. relocatable instruction and data cards.

The transfer vector:
- Cell 0's first 18 bits are its length.
- Cells 1.. hold A8 names.
- The calling form is "`SIC,$X15` / `B, name`".

Arguments are words of `VF,a1;VF,a2` after the call (p.31 **[INK]**):
- a1 is the argument's address.
- a2 is the array base, or a1 again for a scalar.
- Example: `CALL JOE(... A(1,2,2))` → `VF, A+8.0; VF, A`.

Index registers: "A FORTRAN-coded subprogram always saves all 16 index registers upon initial entry" (p.31 **[INK]**).

Appendix C's hand-written STRAP subprogram (p.34 **[INK]**) uses a different calling form: `CNOP / LVI,$15,$+1.0 / B,SIN / VF,ZERO / VF,ZERO`.

- That is a second calling form inside the same manual (repo issue D-2). It is also seen in AD0642331 (repo, OCR) and in LA-3629 (census, WEB).
- Both forms leave the return in $X15.
- **Open question for the plan:** which form the compiler emitted. p.31 says "The formal instructions passing control must be: SIC,$X15; B,name" **[INK]**.

**Storage layout** (C28 pp.7, 9; spec §6.5; **[REPO-INK]**):
- Subprograms are placed consecutively from 33.0, with library routines above them.
- Blank common is highest, and named commons sit below it.
- The relocation table is at the base of blank common.
- C28 p.17's Example 4 map was checked octal-for-octal in the spec. It names the library pieces `FISIP*`, `IOCS*` (3037₈ = 1567 words), `SPTXT*` (an entry point of IOCS*) and `UST*`.

**Segmentation.**
- Covered by C28 pp.10-14 and C22-6751 App. D p.35 **[OCR]**.
- NODE cards define the segments, with up to 99 in all and 8 resident at once.
- A primary segment holds MAIN, FIOD, the library and the link program.
- BSS phases 1-8 build a node table; a run-time *link program* calls the loader.
- C28-6379 p.2 says this part was written by NWL Dahlgren **[REPO-INK]**.

### 1.2 What the repo already implements (read from the code and NEXT.md)

**MCP's loader** (L pp.320-334) is transcribed bit-exact, except printed **p.329**, which is missing from the scan. Since R0.3 (2026-11-16) a **RECONSTRUCTION** of it, `decks/mcp_p329_reconstruction.strap`, fills the 34 words; it is used only where a caller asks (`mcp_image.pages(..., p329=True)`).

**Run on the model** (`tests/gen_loader_deck_tb.py`; NEXT.md "BSS ON MCP'S LOADER -- done to the subprogram end, 2026-11-12"):

| mode | what it runs |
|---|---|
| `""` | absolute deck: origin, flow, zero, partial, branch, sequence and checksum |
| `rel` | PUNREL with an O card: relocatable instruction and data cards, codes `1000`/`1010` |
| `fortran` | the FORTRAN program, common definition and branch cards, each giving return code 4 outside a BSS job, as predicted |
| `bss` | a FORTRAN subprogram with three named commons plus blank common, loaded through `AFPCRD` with a **driver-built (RECONSTRUCTED) relocation table**. Codes `1x a10` and `1xa11i`, nonzero data-card loading bases, and `ARNRM2`'s transfer-vector transmit and branch return all ran. |

**STRAP II.** The host STRAP II (`strap/strap2/`, `punch.py`) punches the BSS cards: PUNREL stages 1-3, PUNFPC, ENTER, PUNCDC, COMBLOCK, SLCRCOM, FEND. `tests/check_strap2_punch.py` checks them, and grep confirms all of these names in `strap/strap2/`.

**Run since (R1, 2026-11-16):** modes `bss2` and `bsslib`. A second subprogram with `SRNXAD` ≠ 0, both from TWS (`AREADS`, p.327 ll.11-22) and as a library entry, with the loader handing the next read to resume load. See R1's status below.

**Run through the reconstructed p.329 (R0.3, 2026-11-16):** mode `octal`, C, P and D cards. The results test the reconstruction, not IBM's page.

**Not run:**
- K, A and Z cards, which are absent from the 1963 loader.

### 1.3 What is missing for BSS

**(a) The BSS processor itself** (spec §6, §7.4).
- **R2a BUILT 2026-11-17** (single segment): `decks/bss_7030.strap`, RECONSTRUCTION; the record is under R2 below.
- **R2b, table half, RUN 2026-11-17:** its relocation table is read by MCP's own resume load and loader, which load Example 4 as p.17 lays it out (`tests/check_bss_mcp_load.py`); record under R2.
- No code survives in any deck. The repo grep is in spec §7.4, and I agree with it.
- It must be RECONSTRUCTED from C28 pp.7-14:
  - the card scan;
  - the three intermediate tables (Figs. 1-3);
  - matching and library fetch;
  - allocation;
  - the relocation table (Fig. 4);
  - the map print;
  - messages pp.22-23;
  - segmentation phases 1-8;
  - the link program.
- Gaps G5-G11 in the spec are exactly what a reconstruction must CHOOSE: TWS layout, library type-area form, link-program encoding, link-table mask, node-table encodings.

**(b) The library on disk.** BSS fetches "from the FORTRAN library on disk".
- The listing reads a library entry by a 36-bit `LB`-prefixed type-area name (spec G7).
- No such type areas are in `strap/prosa.py` or `prosa_dict.py`. I checked by grep: no FORTRAN, BSS, LPC or LFORTRAN.

**(c) Printed p.329**, needed for P and D cards, hex A-F, and short C cards. **RECONSTRUCTED (R0.3, 2026-11-16)**; a second copy (F3) is still the way to replace it with IBM's code.

**(d) The MCP choice** (spec G2): the 1963 listing (15 classes) or the 1964 manuals (18 classes, plus "set blank common to +∞"). This is the owner's decision.

**(e) The front end that feeds BSS a real job.**
- E2 (operator START), E3 (a file-backed reader) and E4 (a first job) are **not done**.
- MCP idles polling for a JOB card (`programming_environment.md`; boot_plan.md l.2358-2386).
- Until then every loader run is a testbench driving the loader's calling sequence directly.

### 1.4 The 7090 analogue: FORTRAN II Monitor "BSS Control", not IBLDR

**The name.** "BSS" is a 709/7090 FORTRAN II Monitor term ("BSS Control", "BSS loader" in R23-9673 [DL]). That the 7030 *inherited* the name, and that it expands the same way ("Binary Symbolic Subroutine" is C28-6379's expansion as the task gives it), is my **inference** from the shared name and function.

**The direct analogue is the FORTRAN II Monitor's BSS Control record.** Its source survives:

- **Source** [DL]: `scratchpad/dl_cozx/x/FORTRAN/9F07.fap` (3920 lines in all: DEBUG plus BSS Control plus Library Search; by the TTL lines in `fortran.job`, 17432 / 20189 / 21062 / 22268, BSS Control is about 870 lines and Library Search about 1,200; title "32K 709/7090 FORTRAN MONITOR DEBUG, BSS CONTROL AND LIBRARY SEARCH"), and its twin `9F32.fap`.
  - Inside `fortran.job`: "RECORD 8 OR 33 BSS CONTROL" and "RECORD 9 OR 34 LIBRARY SEARCH".
  - Processor 7090-FO-928, version 3, mod level 35.
  - From `http://www.bitsavers.org/bits/IBM/www.cozx.com/709x/ibsys.tar.gz`, verified to download, and its assembled listing `.../709x/fortran.lst` (7.0 MB, verified).
  - The tarball's README: "gleaned from the IBSYS tapes from Paul Pierce's web site".
- **Internals manual** [DL]: *Programming Systems Analysis Guide, 709/7090 32K FORTRAN*, R23-9673 (1961), `http://www.bitsavers.org/pdf/ibm/7090/R23-9673-FortranAnalysisGuide_1961.pdf`, 133 pp, text layer.
  - It is the 7090 member of the same "Analysis Guide" series as the lost 7030 FORTRAN Analysis Guide (C22-6728-1 p.7, repo OCR).
  - Its "BSS CONTROL RECORD (RECORD 7 OR 43)" section: the guide says 7/43, the mod-35 source says 8/33. Cite each to its own source.

What R23-9673 says BSS Control does [DL, text layer]:
- It accepts column-binary cards (A2), FAP or FORTRAN binary from tape (B3), and library subroutines (A1).
- It "peels off" transfer vectors.
- It keeps a table of BCD program names, a *missing-subroutine table* and a transfer-vector table, together called "the Snapshot".
- It searches the library (up to two passes) for the missing names.
- It saves relocated programs on B1, then rewrites "the Transfer Vector table ... to TTR's with their proper relocated addresses".
- It handles CHAIN (overlay) jobs.

The source shows the card handling [DL, 9F07 / fortran.job l.20189ff]:
- A word count is held in 9L.
- Program, absolute and control cards are flagged in the 9-row bits.
- A control card carries the program break and COMMON.
- Relocatable cards carry relocation bits in 8L/8R.
- The program card carries the program name.
- There is a 50-entry missing-routine limit (`NMMSP EQU 50`).
- The checksum code is commented out in mod 35.

**How it matches the 7030 BSS** (structural, labelled ANALOGUE):

| 7090 FORTRAN II BSS (R23-9673; 9F07) | 7030 BSS (C28-6379; C22-6751) |
|---|---|
| program card per subprogram, names, program break, COMMON size | FORTRAN Program card (size, blank-common size, up to 9 entries) |
| transfer vector of BCD names at the start of each program | transfer vector of A8 names at cell 1, length in cell 0 |
| missing-subroutine table → library search | third-table names matched against first-table entries → library fetch from disk |
| TV entries replaced by `TTR` to the relocated address | third-table word 2 "replaced by a branch; NOP to the absolute transfer address" (C28 Fig. 3) |
| COMMON at the top of storage | blank common highest, named below (named common is new in 7030 FORTRAN IV, C22-6751 App. B p.34 [INK]) |
| relocated programs staged on tape B1, then an absolute load | subprograms staged on disk (TWS), relocation tables in core, MCP resume load reads them |
| CHAIN jobs (tape links) | NODE segmentation with a run-time link program |

**IBLDR** (the IBJOB loader, 1962-63) is the later 7090 design.
- It is the closer analogue for **segmentation only**.
- *IBJOB Processor: Overlay Feature of IBLDR*, C28-6331 (May 1963) [DL, OCR of pp.1-4], `http://www.bitsavers.org/pdf/ibm/7090/C28-6331_IBLDR_overlay_1963.pdf`:
  - "main link" resident with "the Overlay subroutine and the tables";
  - "dependent links" overlaid by "logical origin";
  - induced only by a CALL to a deck in a non-resident link.
- That is the same tree-of-segments model as 7030 NODE/primary segment/link program, and it is contemporary.
- **IBLDR's own source is NOT in the cozx tarball.** `IBJOB/ibjob.map` only names records IBLDRM..IBLDRS and calls the loader (grep [DL]).
- A lead: Paul Pierce's tape `ST470-1` ("Symbolic Input Tape #1(A) IBSYS, IBJOB, IOCS, EDITOR", `http://www.piercefuller.com/oldibm/709x/tape/st470-1.html`, page verified; contents not inspected).
- IBLDR's binary-deck format (control dictionary etc.) is **[UNVERIFIED]**. C28-6275-2 (`.../7090/C28-6275-2_7090_IBJOB.pdf`, downloaded, no text layer) was not read.

**Verdict.**
- Model the 7030 BSS processor's *flow* (scan, missing table, library search, TV patch) on FORTRAN II BSS Control, whose source can be read line by line.
- Model the *segmentation and link program* on IBLDR Overlay where C28-6379 is silent.
- Every borrowed choice gets a label: ANALOGUE: 7090 FORTRAN II 9F07, or ANALOGUE: C28-6331.

---

## 2. FORTRAN IV: language, compiler structure, library, analogues

### 2.1 The language C22-6751 defines

**Statement format** (p.5 [OCR]):
- 72-column records, up to 9 continuations;
- "C" in column 1 marks a comment;
- labels of fewer than 6 digits;
- blanks are ignored outside Hollerith.

**Types and constants** (pp.5-6 [OCR]):
- Integer, real and logical types, with explicit type statements.
- Integer constants have 1-11 digits.
- Real constants have fewer than 15 digits.
- Arrays have up to 3 subscripts, in the restricted forms `c*v±c'`.

**Expressions** (p.6 [OCR]): no mixed mode. A real may enter an integer expression only as a function argument; an integer may enter a real expression only as an argument, subscript or exponent.

**Statements** (pp.7-21 [OCR]):
- Logical operators and the relations `.GT. .GE. .LT. .LE. .EQ. .NE.`.
- `IF(t)S`, the logical IF. The arithmetic IF is still accepted "without flow analysis" (p.34 [INK]).
- GO TO in its unconditional, computed and assigned forms, plus ASSIGN.
- DO with nesting rules; CONTINUE, PAUSE, STOP, RETURN, END.
- I/O (Ch.5, p.10 [OCR]):
  - `READ f,list`, `PRINT`, `PUNCH`;
  - `READ(u)`, `WRITE(u)` (binary);
  - `READ(u,f)`, `WRITE(u,f)`;
  - END FILE, BACKSPACE, REWIND;
  - FORMAT with E/F/I (H, A, X, / and others on p.11-12, OCR).
  - A FORMAT may be an array read at run time (p.11 [OCR]).
- Subprograms (pp.14-18): FUNCTION (typed), SUBROUTINE, CALL, EXTERNAL; statement functions.
- Declaratives (pp.18-20): DIMENSION with variable dimensions, EQUIVALENCE, COMMON (blank and `/name/`), INTEGER, REAL, LOGICAL, FREQUENCY.
- DATA and BLOCK DATA (pp.20-21).

**Built-in (in-line) functions** (p.15 Fig. 2 [INK]). There are 21, and the system "has the capacity for more":
- ABS, IABS, AINT, INT, AMOD, MOD;
- AMAX0, AMAX1, MAX0, MAX1, AMIN0, AMIN1, MIN0, MIN1;
- FLOAT, IFIX, SIGN, ISIGN, DIM, IDIM;
- SQRT, which is listed among the open functions.

**Closed library functions** "among those distributed" (p.17 [INK]): ALOG, SIN, COS, EXP, ATAN, TANH.

**Data representation** (pp.23-24 [INK]):
- Real: a normalized float, with a 12-bit signed exponent in bits 0-11, a 48-bit fraction in 12-59, the fraction sign at 60, and 3 flag bits unused.
- Integer: an unnormalized float with exponent fixed at 38₁₀. The diagram's ruler reads 0, 10 11 12, 49 50, 60 63, with the binary point at 49/50, so the integer occupies fraction bits 12-49 (38 bits, matching the exponent) and bits 50-59 are an empty fraction tail. It "enables the floating point instruction set to be used". Integer multiply therefore needs double-precision ops (p.24).
- Logical: bit 59, operated on "principally by CONNECT instructions".
- Zero fractions with different exponents must compare equal (p.24).

**Differences from 709/90 FORTRAN II** (App. B p.34 [INK]).
- Changes:
  - logical IF;
  - generalized I/O;
  - sense lights and switches dropped;
  - EQUIVALENCE may not reorder COMMON;
  - unified function naming;
  - B/F modal punches dropped;
  - no implicit multiplication.
- Additions:
  - type statements;
  - logical and relational operators;
  - EXTERNAL;
  - named COMMON with dimensions;
  - variable DIMENSION;
  - DATA.

The 1961 bulletin J28-6127 (CHM 102634362) [DL text layer, repo copy `docs/chm/102634362.pdf`] says 7030 FORTRAN compiles FORTRAN II programs "without change ... as long as they use only the FORTRAN II language described in 709/7090 Reference Manual, C28-6054-2".
- So IBM itself defined 7030 FORTRAN against 7090 FORTRAN II.
- That is the strongest licence for using the 7090 FORTRAN II manual and compiler as the structural analogue.

### 2.2 The job interface: what MCP sees

**Control cards** (C22-6751 p.28 [INK]):

- `B JOB, id` and `B TYPE, COMPILE|COMPILGO|GO, FORTRAN`.
- `T SUBTYPE, deck-description, list-option, punch-option`.
- Deck descriptions:
  - `FORTRAN`;
  - **`A1` "SMAC source statements"**;
  - `STRAP` "STRAP II code";
  - `BIN`;
  - `DATA`;
  - `FIOD` "unprocessed FORTRAN-oriented IOD deck".
- List options: `LSTRAP`, null, `NOLIST`. Punch options: `PBIN`, `NOPUN`, null.
- The FIOD subprogram must be first and ends with END in column 10 (p.28).
- IOD naming (pp.25-26 [OCR]):
  - **The programmer** punches the unit number followed by `B` (binary: disk or binary tape) or `D` (decimal: printer, decimal tape, pseudo-IODs). The NWL deck's `2D` and `12B` show this.
  - **The compiler** only prefixes `K` to an alphabetic IOD name, and deletes the exit field ("by STRAP time, it will be void").
- After compilation the processed IODs come back as binary input, with STRAP adding two fields (p.29 [OCR]).

**Termination** (p.23 [INK]):
- A main-program RETURN, end of data, or PAUSE plus operator action is a "good stop".
- STOP, a bad I/O operation, or PAUSE is a "bad stop" with a dump.
- Both return to MCP.

**Interrupts** (p.23 [INK]):
- "The Stretch Compiling System inserts a call to an initializing routine as the first executable statement of each main program". It is fetched from the library and sets the FORTRAN mask and a Program Table of Exits in $X15's refill field.
- All object I/O goes through "the Input-Output Control Subroutine (actually a whole family of library subroutines linked in a fairly complex fashion)". It issues `$CHEX` dynamically on first use of each IOD, and its I/O Table of Exits sits inside IOCS.

**What real decks show** [INK]:
- AD0646577 printed p.46 (NWL, 1967): `T SUBTYPE,FIOD` / `B 2D IOD,$READER` / `B 3D IOD,$PRINTER` / `B 5D IOD,TAPE,,,,EVEN,,SAVE` / `B REEL,PUL` / `B 12B IOD,DISK,,,2899` / `B 10B IOD,DISK,,,101` / `END` / `T SUBTYPE,FORTRAN,LMAP,PBIN`, then a main program with COMMON, EQUIVALENCE, EXTERNAL and computed GO TO.
- AD0685715 printed p.89: `T SUBTYPE,FORTRAN,LMAP,LSTRAP` and a subroutine with named `COMMON /MTXCOM/`.
- **`LMAP` is not among the list options of C22-6751 p.28 (May 1963).** The DTIC decks (1966-68) target a later compiler release. Expect other differences.
- AD0685715 printed p.79 (PDF 87) is a hand-written STRAP subprogram (symbolic only, no object column).
- **No compiler-generated STRAP (LSTRAP output) was found.** This is a *weak* negative:
  - I scanned five DTIC reports (AD0685715, AD0642331, AD0646577, AD0663887, AD0665291) and the three LASL decks.
  - The scan was a regex over poor OCR text layers, needing at least 3 STRAP tokens per page.
  - It hit only AD0685715 PDF pp.87, 88 and 93, and I viewed only p.87.
  - Re-check by eye before relying on it.

### 2.3 What the compiler's structure must have been

**Evidence, strongest first.**

1. **C22-6729 p.7 Fig. 1 [INK]** is the whole compiling chain:
   - One box, "PROCESSOR (SMAC AND FORTRAN IV)", holds PH3 SYNTAX (FORTRAN IV input), then PH2-1 DATA GLEAN (SMAC II input enters here), then PH2-2 EXPANSION / PH2-3 INDEXING, then PH1 EXPANSION (SMAC I input enters here).
   - It sits beside "LPC (LANGUAGE PROCESSOR COORDINATOR)" and feeds STRAP II, which produces LISTING and BINARY.
   - So FORTRAN IV is the top level of a three-level macro-language processor:
     - level 3 is FORTRAN;
     - level 2 is SMAC II (data glean, expansion, indexing);
     - level 1 is SMAC I (macro expansion into STRAP).
   - The output is STRAP II source, which is then assembled.
   - The SUBTYPE deck description "A1" (p.28) fits a language-level name for SMAC I. That is my inference; "A2" for SMAC II is not printed.
2. **C22-6728-1 pp.240-241 [INK]**, UPDATE-30's Generator Librarian, describes the processor's data:
   - "four generator libraries: LFORTRAN, LPASSONE, LPASSTWO, LSMACONE", each with a table of contents type area (TFORTRAN, TPASSONE, TPASSTWO, TSMACONE).
   - "the table of contents ... is used by compilers to locate generators for expansion of FORTRAN and MACRO statements".
   - "Generator libraries are composed of variable length blocked records, each generator being a record ... blocked in memory image form".
   - The TOFC is three-word entries, one per statement in the library: name; record number (bits 0-17 of word 2) "to be used for ZTAKE by the librarian or the compiler"; sort field; control bits.
   - "The memory address field is used only during compilation by the FORTRAN compiler. The size field is created by the librarian for use by the FORTRAN compiler."
   - Control bits 1.52 and 1.53 (synonyms) are "tested by ... the FORTRAN compiler". That sentence is on p.242, which I read in OCR only (it prints "1.63"), so it is **not [INK]**.
   - At most 300 entries per library.
   - Generator binary decks: the origin must be 1000₁₀ ("Origin out of range (not 1000(10))"), and flow cards range 1000-3045₁₀.
   - **Therefore FORTRAN statements were expanded by binary generators kept on disk, as in SMAC I.** The FORTRAN compiler is a generator-driven macro compiler, not a hand-coded translator.
   - The four libraries map plausibly to PH3 (LFORTRAN), PH2's passes (LPASSONE, LPASSTWO) and PH1 (LSMACONE). That mapping is **inference**.
   - **Note for `docs/smac_7030.md`:** its CHOSEN "each generator is assembled at origin 0" conflicts with p.241's generator-deck origin 1000₁₀. This needs a reading of whether that origin is a word address and whether it is the load or the assembly origin.
3. **C22-6728-1 p.208 [OCR]**: "When FORTRAN, Autocoder, or STRAP II is the first processor in the chain, input must be requested from system input."
4. **J22-6532 (repo)**: "The 7030 Fortran processor will translate Fortran statements to SMAC statements" (census, REPO-OCR).
5. **Allen.**
   - Allen 1981 (IBM JRD 25(5), pp.535-548) was **not retrieved this session**. The repo says it reads "The system was not a success; compilation time was unacceptable" (`archival_inventory.md` l.1818-1822, marked read). The task's "Autocoder-like IL ... macros for a macro assembler" paraphrase is **[UNVERIFIED by me]**.
   - What I did retrieve [DL `dl_allen/cgo.pdf`, Allen's CGO 2003 keynote, `https://cgo-conference.github.io/cgo2003/keynote/FranAllenCGO.pdf`]:
     - a "Stretch-Harvest Compiler" diagram: Fortran / Autocoder / ALPHA translations to IL, then OPTIMIZATION, then REGISTER ALLOCATION, then ASSEMBLER, then object code;
     - and the line **"Stretch compiler for Fortran replaced with simpler, faster compiler"**.
   - **Two readings, not decided** (see Q1):
     - (a) The generator chain *is* Allen's Stretch(-Harvest) compiler as shipped, and the "simpler, faster compiler" that replaced it came later and is undocumented. It may be what compiled the `LMAP`-era decks. For this reading:
       - the task's paraphrase of Allen ("emitted macros for a macro assembler");
       - Autocoder named as a chain processor on C22-6728-1 p.208 [OCR];
       - "compilation time was unacceptable" (repo quote), which fits a multi-phase chain.
     - (b) The chain *is* the simpler replacement, and the IL/optimizer compiler never shipped. For this reading: the CGO diagram's IL → OPTIMIZATION → REGISTER ALLOCATION pipeline looks nothing like Fig. 1's syntax/glean/expansion/indexing phases.
   - **Either way the plan stands.** The C22-6729/C22-6728-1 chain is the only documented IBM design, so it is the reconstruction target.

**Consequences for a reconstruction.**
- The 7030 FORTRAN IV to rebuild is: a **PH3 syntax phase** turning FORTRAN statements into SMAC II-level statements; **PH2** data glean (symbol, storage and COMMON/EQUIVALENCE allocation), expansion and indexing (subscript and DO index-register assignment, plausibly where Stretch's index registers were allocated); then **PH1 SMAC I expansion** to STRAP II text with PUNREL/PUNFPC/ENTER/PUNCDC/COMBLOCK/FEND.
- The generators live in LFORTRAN/LPASSONE/LPASSTWO/LSMACONE on PROSA, addressed through TOFC/ZTAKE.
- The repo already has SMAC I's Generator Language and a 7030 SMAC that compiles generators (`docs/smac_7030.md`). That is the right substrate.

### 2.4 The library the compiler needs

**From the 7030 sources:**
- Initializing routine: mask, Program Table of Exits, correction routines (p.23 [INK]).
- IOCS family: format conversion E/F/I/A/H/X; list I/O; binary blocked tape and disk I/O; decimal unblocked tape (1-17-word records, p.26 [OCR]); system reader, printer and punch; END FILE/BACKSPACE/REWIND on tape, and on disk as a pseudo tape mark, previous record and first arc (p.27 [OCR]); dynamic `$CHEX`.
- Closed math: ALOG, SIN, COS, EXP, ATAN, TANH (p.17 [INK]).
- Exponentiation (`**`) and integer multiply helpers (p.24 [INK] implies them).
- Termination and dump paths into MCP: `B,$MCP` / `,$ABEOJ` (App. C, p.35 [OCR]).
- The BSS link program for segmented jobs.

Names seen in C28 p.17's map **[REPO-INK]**: `FISIP*` (7 words, perhaps the initializing routine; name-based inference), `IOCS*` (1567 words), `SPTXT*`, `UST*`.

Partial primary sources in the repo: C22-6578 §4.9-4.11 math routines; CHM 102633965 and 102633957 (repo-listed).

A **find lead**: CHM 102663031 "includes an 'IBM 7030 FORTRAN IV Library Subroutines, System Bulletin'" (`archival_inventory.md` l.1809-1811, repo; not scanned).

### 2.5 7090 analogues, verified to exist (bitsavers checked 2026-11-16 by directory listing)

All are under `http://www.bitsavers.org/pdf/ibm/7090/` unless another location is given.

| piece | file | why it matters | status |
|---|---|---|---|
| FORTRAN II language | `C28-6054-4_7090_FORTRANII.pdf`, `C28-6054-5_FORTRANII_Apr64.pdf` | J28-6127 names C28-6054-2 as the compatibility baseline | listed; not read |
| FORTRAN II operations (monitor, BSS decks) | `C28-6066-6_FORTRANII_oper.pdf` | user-level BSS deck and control cards | downloaded (`dl_bs/`), no text layer, not read |
| **FORTRAN II internals** | `R23-9673-FortranAnalysisGuide_1961.pdf` | the same Analysis Guide series as the lost 7030 one: monitor, BSS Control, sections I-VI, library, generated tables | **[DL]**, text layer, BSS section read |
| **FORTRAN II source** (7090-FO-928 v3 m35) | `http://www.bitsavers.org/bits/IBM/www.cozx.com/709x/ibsys.tar.gz` → `FORTRAN/9F*.fap`, `library.job`; listing `.../709x/fortran.lst` | compiler 35,099 lines (9F13 11,691; 9F18 7,457; 9F22 3,664; 9F23 6,820; 9F30 5,467); BSS Control 3,920; FAP 10,823; library 9,292 lines (math, complex, double, I/O: 9IOH, 9IOS, 9IOB, 9CHN, 9XIT ...) | **[DL]**, measured with `wc` |
| FORTRAN II I/O package | `J28-6190-3_FORTRAN_II_IOPkg_Apr66.pdf` | I/O library structure | listed; not read |
| FORTRAN IV (IBJOB IBFTC) language | `C28-6274-1_7090_FORTRANIV.pdf`, `C28-6274-2_FORTRANIV_Jun64.pdf`, `C28-6390-3_v13_F4_Apr66.pdf` | the contemporaneous FORTRAN IV dialect | listed; C28-6274-1 downloaded, no text, not read |
| **IBFTC source** | same tarball, `IBFTC/*.map` (7 sections, 55,304 lines) and `IBFTC/rtl/` (97 `.map` routines, 18,749 lines) | a second structural model, closer in date and language | **[DL]**, measured |
| IBJOB, IBLDR | `C28-6275-2_7090_IBJOB.pdf`, `C28-6389-1_v13_IBJOB_Jun65.pdf`, `C28-6331_IBLDR_overlay_1963.pdf` | loader and overlay | C28-6331 read pp.1-4 OCR; others not read |
| IBSYS analysis | `C28-6299_IBSYS_PgSyAn_Feb63.pdf` | supervisor internals | listed |
| IOCS | `C28-6100-2_7090_IOCS.pdf`, `9IOCS_Study_Guide_Mar62.pdf` | — | listed |
| FAP, MAP | `C28-6235-*`, `C28-6311-*`, `C28-6392-*` | macro assemblers that FORTRAN fed | listed |
| CUC FORTRAN IVA design workbook | `http://www.bitsavers.org/pdf/ibm/7094/CUC_FORTAN_IVA_System_Design_Workbook_1963.pdf` | a 1963 compiler design document | listed; not read |
| Paul Pierce tapes | `http://www.piercefuller.com/oldibm-shadow/709x.html` | IBSYS/IBJOB/IBFTC symbolic tapes (possible IBLDR source on ST470-1), SHARE "Yale" distribution tapes 29-3542 | page verified; contents not inspected |

**Which analogue for what.**
- **FORTRAN II** (9F, R23-9673) for the BSS flow and for the language baseline IBM named.
- **IBFTC/IBLDR** for FORTRAN IV dialect points (typed functions, logical IF, named COMMON, DATA) and for overlay.
- **Neither** for compiler architecture. The 7030 compiler was a generator/macro chain, unlike both 7090 compilers (FORTRAN II's six hand-coded sections; IBFTC emitting to IBMAP).

---

## 3. A staged plan

**Ordering principle.** Find first. Then make the BSS and runtime path run with STRAP-coded and hand-written subprograms, which needs no compiler. The compiler comes last, because it depends on everything else.

**Sizes** are in pages of source documents to read and rough 7030 words of code.
- The 7030 sizes are scaled from analogues and from C28 p.17.
- The 7090 counts are lines of FAP, not 7030 words. Use them as ratios only.

### F: find, in parallel with everything; it never blocks R

| # | lead | ask for | source of the lead |
|---|---|---|---|
| F1 | CHM 102663031 | scan; holds "IBM 7030 FORTRAN IV Library Subroutines, System Bulletin" | `archival_inventory.md` l.1809 (repo) |
| F2 | CHM 102665489 | the other copy or edition of C22-6751; compare for LMAP and later options | `chm/README.md` l.362 (repo) |
| F3 | IBM Corporate Archives, NARA RG 457 | the FORTRAN and SMAC Analysis Guides (named, C22-6728-1 p.7), the FORTRAN compiler, the BSS listing; Allen's final Stretch-Harvest report to NSA | census §5 (repo) |
| F4 | NWL Dahlgren (now NSWCDD) | the BSS segmentation code: C28-6379 p.2 credits NWL; the DTIC decks are NWL's | C28 p.2 [REPO-INK] |
| F5 | MITRE archives | the "7030 Facility Manual" (Aug 1965), cited by AD0642331 | dtic README (repo) |
| F6 | BYU ("SOS" and updated FORTRAN), LRL (Livermore FORTRAN) | listings or tapes | census, unverified |
| F7 | Paul Pierce SHARE "Yale" tapes | grep for STRAP-1, the 7030 simulator or any 7030 FORTRAN item; they run on existing 7090 emulators | page verified; content unknown |
| F8 | Allen 1981 | get the text and quote it exactly, in place of paraphrases | not retrieved |

### R0. Prerequisites outside FORTRAN (already on the road; the FORTRAN path cannot run under MCP without them)

- **R0.1** E2 operator START, E3 a file-backed card reader, E4 a first (non-BSS) job.
  - `programming_environment.md`. Oracle: MCP's own console and print text.
- **R0.2** The MCP version decision, 1963 or 1964 (spec G2). It fixes K/A/Z, +∞ blank common and message texts. Owner's call.
- **R0.3** Printed p.329, reconstructed (34 words at fixed addresses, spec §7.2), or found (F3).
  - Oracle: 6728-0 p.85 chart and C28 pp.4-5, with existing labels fixing the entry addresses.
  - **STATUS 2026-11-16: NOT FOUND; RECONSTRUCTED.** The record follows.
#### R0.3, the record (2026-11-16)

- **Searched, not found.** The volume-1 PDF and both OCR texts (no TA00044x-49x serial, no `22LOADER` p.329 card); C22-6728 and -1 (prose and charts, no code); C28-6379-0 (card formats); `docs/chm/README.md` and `archival_inventory.md` (no other edition held). F3 (IBM Archives, NARA RG 457) is outside the repository.
- **Reconstructed**, labelled RECONSTRUCTION: `decks/mcp_p329_reconstruction.strap`, 49 statements, 68 half words, 235112.00-235153.40. Its header lists the pages read in the ink (L pp.327 ll.32-50, 328, 330, 331 ll.1-23; 6728 p.85 and Figure 42; C28 pp.4-5, 21; 6728-1 p.94 as an analogue) and says, line by line, what is CITED and what CHOSEN.
  - CITED: the span and its fall-through ends; the eight addresses AOIGN3, AOIGN1, AOCTH1, AOCTL6, APCARD, APCRD2, APCRD4 and APCRD4+1.; that the page names AOCT4A, AOCTH2, APCRD5, ADCRD1, ADCRD2, AERR6, AERR7 and APT168 (`check_never_used_symbols.py`'s ABSENT list).
  - CHOSEN: every instruction. Each has its reason in the deck.
- **What the landed pages force** (the deck's (a)-(c)): P and D cards skip the decimal-point test, so AOCTL6 must do it; a P or D continuation reaches APCRD2 only with ALOWWD = 0 (p.328 ll.9-12, as read); nothing landed turns ADCRDI off, so the page turns both ADCRDI and APCRDI off at APCRD4.
- **Two first-run findings, fixed in the deck:** a connective resets the counts (Ref. Manual p.76), so AOCTH1 cannot read the digit row from $LZC after it; and a continuation C card needs $2 reset to AOXW3.
- **Checks.** `tests/check_p329_reconstruction.py` (placement, landed words unchanged, the names; injections in its header). `gen_loader_deck_tb.py` mode `octal`: C cards with hex, a short card, a continuation, an ignored half word and an ignored card, two P cards (half and full word) and a D card, against absolute assembly, ALL TESTS PASSED, three measured injections in its header.
- **Open:** P/D continuations (need ALOWWD = 0); 12-0 and 12-7..12-9 in a hex column (only 12-0 is rejected); C28's "last half word not stepped" exception (a later loader); a 1 punch in a P card's origin point turns AOIGNI on but the patch is still inserted.

- **R0.4** The disk path for TWS and library reads (`AREADS`, p.327 ll.11-22) under the loader.
  - Oracle: the existing loader `bss` mode, extended to `SRNXAD` ≠ 0.

- **R0.5 How MCP reaches the chain.** Nothing above says how `TYPE,COMPILGO,FORTRAN` becomes fetched type areas.
  - Read L pp.266-274 (job control, the TYPE card; p.271 is already transcribed) for the chain table, the processor type-area names and the entry convention.
  - Add PROSA type areas for the LPC, the SMAC/FORTRAN processor, STRAP II and BSS (`prosa_dict.py` has none today).
  - Oracle: the listing's own name constants (e.g. `YFORTR (AX)DD(BU,48,6),FORTRAN` p.274, `ABSSID`).
  - **STATUS 2026-11-16: READ; names recorded; no area added.** The record is below.

#### R0.5, as read in the ink (2026-11-16)

**Where the listing is.** `docs/MCP_Mar63_250-445.pdf`. For printed pages 250-328 the PDF page is the printed page minus 249: p.266 is PDF 17 and p.274 is PDF 25. From p.330 on it is minus 250, because p.329 is missing from the scan: p.395 is PDF 145. Viewed as 150-200 dpi images this session:
- pp.267, 268, 270, 271, 272, 273, 274, 395 and 396 in full;
- p.266 ll.10-30, p.269 ll.9-54 and p.397 ll.1-23;
- for R1 and the names, p.291 ll.6-31, p.324 ll.10-29, p.326 ll.37-45, p.327 ll.1-28, p.332 ll.27-42 and p.334 ll.1-19.

Cited from the transcription only, and not re-read: p.103 (`SJCTWS`), p.384 (`YC4B5`) and p.386 (`WJC4G`). The transcriptions in `decks/mcp_bootstrap_p*.strap` were the finding aid.

**The plan's premise was wrong about where the chain is.**
- Pp.266-274 are JOB CONTROL PHASE 1 and UNCODE ("UNCODE SUBROUTINE TO DECIPHER SYSTEM CARDS", p.270 ll.24-25). They decode the TYPE card. They hold no chain table.
- The chain is in the `$EOJ` overlay (PUNID `22$EOJ`), at pp.395-397, under the banner "THE COMPILE AND GO SUB ROUTINES" (p.395 l.25).

**1. The TYPE card (pp.266-274).**
- UNCODE turns the card into 6-bit BCD: "CONVERT CARDS TO 6-BIYT BCD" (p.270 l.34, so printed), `BD,SCA6`.
- It breaks the card into 8-character fields at `YUCBF2`: "BREAK CARD INTO FIELDS" (p.270 l.39), `BD,SBRK8`.
- It hands the fields back: "TRANSMIT BROKEN OUT / CARD TO REQUESTED AREA" (p.273 ll.35-36).
- `YTOPGO` (p.271 l.23, "GO - SET COUNT FIELD TO PROPER / VALUE + GO TO NORMAL RETURN") compares field 2 with `YGOMK` "GO", `YCOMMK` "COMPILE", `YCNGMK` "COMPILGO" and `YUPDAT` (p.271 ll.25-32; the constants are p.273 l.44 and p.274 ll.6, 8, 12).
- For GO, `YBSSGO` (p.271 ll.43-50) makes the job a compile-and-go job with BSS as its processor: `L(BU,48),YUCBF2+2.` "-INTERPRET GO, AS CMPILGO,..." / `KF(BU,48),YFORTR` "-AND FORTRAN AS BSS" / `BZAE,YTOPCG` / `LF(BU,48),ABSSID` / `SF(BU,48),YUCBF2+2.`
- `YFORTR` is `(AX)DD(BU,48,6),FORTRAN X` (p.274 l.13). `ABSSID` is `(A*)DD(BU,48,6),BSS *` (p.291 l.8; that page was not re-read this session).
- `YC1TC BB,.41+Y1UCXW,YC1SCN` carries the remark "- BRANCH IF A COMPILE JOB" (p.266 l.26).

**2. The processor-control type area (p.395).**
- `YCOJB1` (p.395 ll.44-56) forms the name and fetches it: `L(BU,48),YUCBF2+2.0` / `LFI(BU,12),YCCIN,48` / `ST(BU,48),YDFCTA,12` / `B,DMCP` / `,DFETCH` / `YDFCTA DR(BU),(1)` / `,0` / `LVE, ,SJCTWS` / `,0` / `YCIODC ,0`.
- `YCCIN` is `(AX)DDI(BU,12,6),PCX`, its value printed `+00004763` (p.396 l.29).
- Reading the VFL offset from the accumulator's right end gives the name as **"PC" followed by the first six characters of the TYPE card's third field**:
  - field 3 sits in accumulator bits 80-127;
  - "PC" sits at 68-79;
  - the store takes the 48 bits that end 12 from the right, bits 68-115.
  - The offset reading is from the Reference Manual, printed p.56 (PDF 59), read in the ink: "The *offset field*, bits 44 through 50, specifies the number of bits by which the right end of the accumulator operand is offset from the right end of the accumulator."
  - `LFI` is a connective. At byte size 6 it would spread "PC" into two 8-bit bytes (p.75, as quoted in `bsv/StretchVFL.bsv`). Its printed second half-word, `414030.06` (p.395 l.48), has a byte-size field of 000, which means 8, so "PC" sits flat at bits 68-79. This was checked by assembling the line with strap_asm and comparing it with the printed binary.
  - **Run on the model** (`gen_loader_deck_tb.py pcname`): the three statements as printed give `PCFORTRA` and `PCBSS   `. Written with byte size 6 instead of the printed 8, both names come out wrong. The loader's own name-building (`LB` + 36 bits, p.327 ll.23-25) was also run, in R1's `bsslib` mode.
- **DERIVED:** a COMPILE or COMPILGO FORTRAN job fetches **`PCFORTRA`**. A GO,FORTRAN job fetches **`PCBSS   `** (the last three characters are strap_asm's blank fill of `ABSSID`; no listing prints A-mode bits).
- The fetched area goes into `SJCTWS`, "TWS FOR JC" (p.103 l.55).
- This 12-bit type + 36-bit area form agrees with `YMPFCH`, MCP's own overlay fetcher (p.269 ll.13-25, "SPECIAL PACKAGE TO PULL MCP PROGRAMS FROM THE DISK"): `(AX)DD(BU,12,6),22X` followed by a 36-bit area such as `$DUMP`, `SCOMD`, `$EOJ` (ll.45, 48, 54).

**3. The chain table: the PC area's content, in KSILO (p.396 ll.3-28).**
- The PC area's first card is the chain. `BD,SCA6` on 80 columns from `SJCTWS` carries the remark "-CONVERT COMPILER NAMES TO BCD." (ll.4-7).
- `B,SBRK8` from column 2 (`YUCBF1+.6`, `CF,71.`) into `YUCBF2`, with the field count kept in `YPCCT`: "-BREAK OUT CARD" (ll.8-13).
- Then:
  - `Z,KSILO` / `SC,$15,KSILO`: KSILO's count field is the number of compilers;
  - `LI(BU,18),4096.` / `-(BU,18),SSYRFT` / `ST(BU,18),KSILO+1.0` "-TELL COMPILERS HOW BIG TWS IS.";
  - `T,$15,YUCBF2,KSILO+2.0`: the compiler names, one per word, from **KSILO+2.0** on (ll.16-22).
- **So the chain table is KSILO+2.0 onward, one 48-bit type-area name per word, copied from the PC area's first card.** The listing does not print the card.
- The area may hold more cards than that one. P.396 ll.23-28 go on: `CM1111(BU,1),YCIDBT` "-SET READ SOURCE BIT" / `LV,$13,SJCTWS` / `V+I,$13,15.0` / `LC,$13,YCIODC` / `B,YC4B5`, which is p.384 l.24's "READ 1 CARD FROM SOURCE" (from the transcription, not re-read), with the source just past that card. What further cards the area holds is not printed.

**4. Stepping the chain and the entry convention (p.396 ll.30-56, p.397 ll.1-15).**
- `YC4INT` steps it:
  - `LV,$14,KSILO+.32` / `V+I,$14,1.0` / `KV,$14,KSILO` "-HAS LAST COMPILER RUN" / "-IS THIS THE LAST COMPILER" / `CM1111(BU,1),KSILO+.25` "-SET FLAG" / `SV,$14,KSILO+.32` "-UPDATE COMPILER POINTER" (ll.32-38);
  - then `L(BU,48),KSILO+1.0($14)` / `ST(BU,48),YDFCS` "-COMPILER TYPE AREA INTO SFETCH" / `LX,$13,YDKCRS` / `B,WJC4G` (ll.39-42).
- **Entry convention: each compiler is a binary deck stored as a type area, loaded by MCP's own loader.**
  - `YDFCS` (p.274 l.16) is the type area that resume load reads cards from: `TI,1,YDFCS,YRLDTA` then `B,DMCP / ,DFETCH / YRLDTA` (p.332 ll.8, 33-35), 15 words per card and 34 cards per arc (p.332 ll.27-30).
  - `WJC4G` (p.386 l.8) sets the loader limits and calls resume load (`,DRESLD`, p.386 l.25).
  - So a compiler is entered the way any binary deck is: by its branch card, through the loader's branch return.
  - This last step is my reading of pp.332 and 386, which I read in the deck, not re-read in the ink.
- After the last compiler, `YLASTC` (ll.47-56): `L(BU,48),YTWSTA-` "LOAD TYPE AREA FOR COMPILED P.P." / `ST(BU,48),YDFCS` / "COMPUTE NUMBER OF TWS ARCS LEFT." / "-SET READ SOURCE TO P.P." / `LF(BU,18),KSILO+2.` "-CHECK FOR BSS LOADER".
  - p.397 continues: `KFI,YBSSID` / `BZAE,YBB` / `LX,$14,KSILO+8.` "-TAKE P.+. LIMITS FROM KSILO" / ... `CM1111(BU,1),YTSP` "-SET UP FOR SPEC. BSS CASE" (ll.1-9).
  - `YBSSID (AX)DDI(BU,18,6),BSSX` prints `+00622222` (l.10). `YTWSTA (AX)DD(BU,48,6),))))))))X` (l.19).

**What this settles, and what it does not.**
- *Settled names:*
  - `PCFORTRA` and `PCBSS   ` (the PC areas);
  - `))))))))` (the compiled program on TWS; also the loader's `ATWSTA`, p.291 l.30);
  - the `LB` type of a library routine (`ALB`, p.291 l.29);
  - the 18-bit key `BSS`, with which KSILO+2.0 must begin for the BSS path.
  - These are now constants in `strap/prosa_dict.py` (`PC_TYPE`, `TWS_AREA`, `LIBRARY_TYPE`, `BSS_KEY`, `pc_area`), checked by `check_prosa_dict.py` against the two printed DDI values.
- ***Not settled, and not invented:***
  - the type-area names of the LPC, the SMAC/FORTRAN processor, STRAP II and the BSS processor;
  - the PC areas' card content, i.e. the chain itself.
  - For BSS, only the first three characters are fixed.
  - **So no type area for any of the four processors is added to `prosa_dict.py`.** An area needs its words, and the listing gives none.
- **A tension, recorded and not resolved.** C22-6729 p.7 prints the FORTRAN IV chain as "LPC, STRAP, LPC, BSS". If that were the PC card, KSILO+2.0 would begin with the LPC's name, and the loader's BSS test (p.324 ll.13-15, p.332 ll.4-5, p.396 l.56) would fail for a COMPILGO FORTRAN job. Either the LPC rewrites KSILO, or C22-6729's chain is not the PC card's, or that chain belongs to a later MCP. The March 1963 listing plainly supports one BSS case: GO,FORTRAN, whose PC area `PCBSS` must list a BSS-prefixed name first.
- **R0.6 STRAP II as a 7030 program (E6).** It is at step 3b (TABMAN) per `docs/strap2_7030.md`. Every "under MCP" step from R2b onward that assembles anything needs it, and R5f needs it outright. Until then the host STRAP II (`strap/strap2/`) is scaffolding.

### R1. Close the loader's remaining paths with driver-built tables (small; test only)

- Add a second subprogram to `gen_loader_deck_tb.py bss`, then a library entry: `LB`+name type area, spec G7, CHOSEN form.
- Then C, P and D cards (after R0.3).
- Oracle: absolute-assembly equality, the pattern the suite already uses.
- Inject: a wrong `SRNXAD` chain, a wrong named-common index width.
- Size: about 1 day of testbench work; no new 7030 code.
- **STATUS 2026-11-16: the second subprogram and the library entry ran. C, P and D were NOT built (R0.3).** Details and injections are in `tests/gen_loader_deck_tb.py`'s header.
  - **`bss2`, 29 checks.** Table 1's `SRNXAD` points at a second table, so `ARNRM2`-`ARNRM5` (p.327 ll.1-22) run with a next table. The second subprogram (four named commons, so `i` is 3 bits; BL2 shared, at index 1 where the first has it at 2; a two-word vector) then loads equal to its absolute assembly and ends the job through `ARNRM4`.
    - `YRLDTA` holds `))))))))`.
    - `$13` holds `AREADS` (p.331 l.40) with its value increased by the disk address (CHOSEN 557, arc 1 word 45) and its count reduced by (557 mod 512) // 15 = 3. That is p.327 ll.12-19 as read, now run.
    - Injections: a wrong `SRNXAD` failed 17 checks and ran out the step cap (the whole second subprogram, the chain end and `$13`). A wrong `i` width (punch.py) failed exactly the second subprogram's 6 instruction words.
  - **`bsslib`, 29 checks plus the end return's.** Table 2's bit 63 is 1. `YRLDTA` holds `LB` and the planted 36 bits (CHOSEN `SINE  `; spec G7), and `$13` holds `AREAD1`.
  - **How a library routine ends.** Its card count is set to 0 (p.324 l.28) and is decremented before it is tested (p.326 ll.41-44), so no card ends it. A first run measured the count wrapping and the vector left untransmitted. The end comes from resume load.
    - DFETCH's second return is `B,YLERR` (p.332 ll.40-41).
    - `YLERR` handles the "CASE WHERE BRANCH CARD IS MISSING" (p.334 ll.2-3). On a BSS job with a library table it goes to `YAERR1`, "-FETCH END RETURN ON A BSS JOB": `LI(BU,18),1.` "-LIBRARY ROUTINE WAS READ" / `ST(BU,18),ARCDCT` / `B,ARNORM` (p.334 ll.12-16, read in the ink).
    - The driver plays that end return. It is CHOSEN that the LB area's end gives it; DFETCH's end-of-area behaviour was not re-read.
    - ARNRM1 then counts 1 to 0. Both vector words are sent and the job ends through the branch return.
    - Injection: p.334 l.14 as `LI(BU,18),2.` fails exactly the two vector words, the branch address and the PC.
  - Control: a card count planted in a library table changes nothing (p.324 l.24).
  - **C, P, D: run through the reconstructed p.329** (R0.3 below, mode `octal`).

### R2. RECONSTRUCT the BSS processor as a 7030 program (medium; about 2-4K words, a guess; basis: 9F07's BSS Control of about 870 FAP lines plus Library Search of about 1,200, scaled up for the 7030's segmentation phases and three tables)

**Sources.** C28-6379 pp.7-14, 22-23 (all of it); C22-6728-1 pp.88-94; C22-6751 App. A/D. Analogue: 9F07 and R23-9673 for scan and library-search mechanics.

**Order.**
1. **R2a**, single segment: the scan (spec §6.3), the three tables (Figs. 1-3), matching and library fetch, allocation (spec §6.5), the relocation table (Fig. 4), the storage map, KSILO words 8-11, and messages.
   - Oracle: **C28 p.17 Example 4's map**. Every origin, size and common address is given in octal, and the arithmetic is already checked in the spec.
   - Build Example 4's subprograms as STRAP-punched stubs of the printed sizes, run BSS, and compare the map line for line.
   - Inject: drop the "largest common wins" merge and watch the common origins move.
   - **STATUS 2026-11-17: BUILT, single segment, staged; the map reproduces p.17.** The record follows.
2. **R2b**, under MCP: `B TYPE,GO,FORTRAN` invoking BSS through the p.271 rewrite, with output on the printer.
   - **STATUS 2026-11-17: the table half RUN.** BSS's relocation table and KSILO 8-11, as the deck leaves them, are read by MCP's own resume load and loader, which load Example 4 as p.17 lays it out; C10 and C11 settled. The record follows R2a's. Still open: BSS reached through `B TYPE,GO,FORTRAN` and p.271, and the map on MCP's printer.
   - Oracle: C22-6751 p.30's Example 4 deck shape and C28 p.22 messages.
3. **R2c**, segmentation and the link program.
   - Sources: C28 pp.10-14 phases 1-8 and Figs. 5, 6, 8.
   - Analogue: C28-6331 IBLDR overlay, for the link program's encoding (spec G8-G10), labelled.
   - Oracle: C28 Fig. 6 and Fig. 8's printed legal and illegal transfers, plus the segmented-job error messages.
   - Size: comparable to R2a.

**Labels.** Every guess is CHOSEN, citing spec G-numbers. The header is RECONSTRUCTION.

#### R2a, the record (2026-11-17)

**Pages read in the ink** (C28-6379-0, PDF = printed): pp.7, 8, 9, 10, 12, 13, 15, 16, 17 (at 400 dpi for the map), 18, 19, 22, 23. Pp.18-19 (Appendix A) label card columns and print some field widths; the bit offsets within a column in the deck are derived from those widths, and are CHOSEN where a page does not draw them. The loader lines the deck cites (L pp.171, 324-327, 331, 333) come from the transcriptions in `decks/` and were not re-read for R2a.

**The oracle, transcribed** from p.17 into `tests/check_bss_example4.py` (`MAP_SUB`, `MAP_COM`): ten subprogram rows and five common rows. The spec's octal sums (§6.5) agree with it.

**Built:** `decks/bss_7030.strap`, labelled RECONSTRUCTION, 759 words of code at 200000-201366 (octal). It does the following:
- scans the subprogram decks: the program card with its continuations, common definition cards, the first instruction card's index word, the vector's data cards, and size from instruction and base-0 data cards;
- ignores T, super T, B, absolute, C, P and D cards (p.9 items 7, 10, 11);
- builds the three tables of Figs. 1-3;
- matches names and fetches from the library, repeating until every third-table entry is linked;
- allocates storage: subprograms from 33.0, the library above them in fetch order, blank common at the top, named commons below it in second-table order;
- merges duplicate commons, the largest winning (p.8 item 2, p.9 step 4, p.12 Phases 2-3), and checks for overlap;
- builds the relocation table in the loader's layout, with the library entries in disk order;
- sets KSILO words 8-11;
- prints the storage map;
- prints messages, RUN on the model: 2; 3 (T.V. INCOMPLETE, ILLEGAL TYPE OF CARD, INCORRECT CARD ORDER, RELOCATION TABLES ARE TOO LARGE, and the console line); and 10;
- has code WRITTEN but NOT RUN for: TOO MANY NAMED COMMONS, TOO MANY TRANSFER VECTORS, continuation program cards (C1; p.18's blank-columns-6-8 mark is not tested), and the ERRC 20/21/22 halts.

Every convention is CITED or CHOSEN in the header (C1-C15). The deck's I/O is labelled SCAFFOLD: a TWS core image in the loader's arc geometry, a library directory standing in for the `LB` areas, and a print buffer.

**The comparison, row by row.** On the model, every row matched at the first run, and the control passes 35 checks in 305,759 steps.

| row | printed and got |
|---|---|
| `*MAIN*` | 000041 000010.0 000745 NO |
| `STEP` | 001006 000022.0 000441 NO |
| `RANDM` | 001447 000000.0 000007 NO (its card says all 1's, so the 7 is the scan's) |
| `POLY` | 001456 000022.0 000346 NO |
| `DERIV` | 002024 000022.0 000271 NO |
| `VALUE` | 002315 000022.0 000134 NO |
| `FISIP*` | 002451 000001.0 000007 YES |
| `IOCS*` | 002460 000002.0 003037 YES |
| `SPTXT*` | 002460 001124.0 E. P. YES |
| `UST*` | 005517 000001.0 000002 YES |
| blank | 213713 000014 (the origin is by construction: the test plants U = 213766 for T = 43 words, rule C7) |
| `DIFF` | 213703 000010 |
| `A` | 213535 000146 |
| `STE` | 213527 000006 |
| `POL` | 213363 000144 |

Two halves of the test check different things:
- The calls, the common declarations and the library's disk order are CHOSEN by the test so that the rows discriminate.
- The relocation table (43 words) and KSILO 8-11 are compared with the test's own reckoning of rules C3-C14. KSILO 9-11 are planted with a 0xAA sentinel, so a field the deck never writes shows; ERRC starts at 255 in the byte the test reads. That half tests the deck against its own rules, not against a page.

**Injections**, measured and restored by copy and cmp. Observed sets are in the test's header.
- **Largest-wins dropped for named commons:** A becomes 213603 000100, STE 213575 and POL 213431, plus 5 table words.
- **Largest-wins dropped for blank common:** blank's amount reads 000000.
- **The data card's secondary count dropped from the extent:** RANDM's size reads 000002, and rows 4-10 and 17 table words move.
- **The library sorted by fetch order, not disk order:** 4 table words fail.
- **KSILO+11.0 never written:** KSILO+11 fails (the sentinel survives).

**Not built.** Each item fails loudly or is listed:
- the O card (ERRC 20);
- a data or block-data subprogram (ERRC 22);
- message 1's sequence and check-sum checks;
- DEFINE and DEFI with messages 8-9;
- K, A and Z cards;
- the storage taken by B IOD and REEL cards;
- messages 4-7;
- the print and console through MCP.

**Not yet run (at R2a):** BSS's table fed to MCP's loader. That is R2b, which must also settle:
- the 36-bit library name (rule C10, spec C8/G7);
- whether the card count should include the FORTRAN branch card (rule C11).

Both are settled, and the table is fed, in R2b's record below.

#### R2b, the record (2026-11-17): BSS's table read by MCP's loader

**Pages read in the ink for R2b** (PDF page in brackets):
- MCP listing, printed p.291 [PDF 42] ll.8, 27-30 (ABSSID, ARCDCT, ALB `(A*)DD(BU,12,6),LB`, ATWSTA `(A*)DD(BU,48,6),))))))))`); p.324 [75] ll.12-29 (AFPCRD); p.326 [77] ll.36-47 (ARNORM, ARNRM1, ARNRM2); p.327 [78] ll.1-30 (ARNRM2-5, ARNRM3's `LF(BU,36,6),0($1)` printed `044600.06 70`); p.331 [81] ll.24-40 (ATBL, AREAD1 `XW,-15.,0,,7`, AREADS `XW,-13.,35,,7`); p.332 [82] ll.1-56 (resume load, the read loop, the `$FETCH` call, YLOAD/YLOADA/YRLLL/YLJSLT/YLBRA/YBCENC); p.334 [84] ll.1-16 and 51 (YSUKFX, YLERR, YAERR1/2, YSUKM's text).
- C28-6379-0 pp.7, 9, 10 (PDF = printed): card order, item 9, the table's contents (7)/(8), Fig. 4 and its notes.
- C22-6728 (6728-0) p.82 (PDF = printed): Fig. 39 and its legend.
- From transcriptions only, NOT re-read (each cited as such where used): p.333 ll.1-28 (YARSL; the deck's `!CHECK` lines agree with the print), p.384 ll.19-20 and p.396 l.47 (who sets KSILO+1.19 and SCORG), p.250 l.45 (who sets REJJOB.60), p.108 l.5 (DMCP = 32.0).

**C10, the library name: SETTLED, 36 bits of A6.** The loader reads `LF(BU,36,6),0($1)` (p.327 l.24, binary `044600.06 70`: 36 bits at byte size 6) behind `LF(BU,12,6),ALB,48` and stores `SF(BU,48,6),YRLDTA`, the type-area name `$FETCH` is given (p.332 l.35). 6728-0 p.82 Fig. 39 draws the library word 0 as SRDKAD bits 0-35 with an empty box to 62 and SRLIB at 63, and its legend says `SRDKAD SYN(BU, 36, 6), 0.0` "a 36-bit field containing a type-area name for a library subprogram". ALB and ATWSTA (p.291 ll.29-30) are `(A*)DD(BU,n,6)`: type-area names are six-bit characters. So word 0 bits 0-35 are six A6 characters, and that is CITED. C28 p.10's note, "The first 48 bits of the first word contain the entry point name", is not what this loader reads; bits 36-47 are never read (p.324 l.24 sends a library entry's count to 0 before it is used), so nothing there is testable, and the deck does not widen its field to meet the note (recorded, spec C8). RECONSTRUCTION: which name goes in (the subprogram's first entry point, C9) and that the library's type area for it is "LB" + that name, six characters blank-padded (spec G7: no page names the LB areas). The deck's rule C10 (A8 to A6 by dropping each character's two high bits) is exact for the 48-character set, whose codes are all below 64 (strap/charsets.py, Reference Manual p.166).

**C11, the card count: SETTLED, the FORTRAN branch card is not counted.** C28 p.7: "Input to the BSS processor consists of a collection of subprograms, each of which begins with a FORTRAN program card", the card order A-G "within each subprogram" has no branch card, and "The last subprogram must be followed by a FORTRAN branch card"; p.9 item 9: it "is used to signal end-of-deck to the BSS processor"; Fig. 4 (p.10) "Number of Cards in Subprogram", Fig. 39 "Count of cards in subprogram". The branch card belongs to the deck, not to a subprogram. MEASURED LIMIT: the loader cannot tell. A FORTRAN branch card it reads goes AFPCRD -> ARNRM1 and is counted like any card (p.324 l.12, 6728-0 p.81), so with the last entry's count one HIGH (it then takes the branch card) the job still loads exactly; only the number of cards `$FETCH` served shows it (below). R1's mode `bss` driver counted the branch card; that was its CHOSEN table, for a deck with no BSS, and this record supersedes it for BSS's.

**Built and run:** `tests/check_bss_mcp_load.py`.
- **Run 1, BSS:** check_bss_example4's machinery, on Example 4's subprograms rebuilt as stubs of p.17's sizes that also reference every common they declare and blank common, put a data word in each named common, and carry 160 data words in *MAIN*, so the 53 input cards cross a 34-card arc (POLY straddles it; DERIV and VALUE start in arc 1). BSS still prints p.17's map row for row.
- **Run 2, MCP:** the LOADER image (pp.99-334), with BSS's table words and KSILO 8-11 copied in exactly as run 1 left them. Planted as MCP leaves them for a GO job: KSILO+2 = BSS (p.271), KSILO+1.19 = 1 (p.384 ll.19-20 put the TYPE card's bits there; which TYPE sets it is not established), SICBU a sentinel; the image already holds SCORG = 0 (p.396 l.47 "SET TOGO (ZERO)") and REJJOB.60 = 0 (p.332 l.54 BBZ: a 1 is "JOB CANNOT BE RUN BECAUSE OF INPUT DIFFICULTIES"). SCAFFOLD: TWS and the LB areas as core images, and `$FETCH` as a stub at word 32 (DMCP). The stub tells the `$FETCH` call from `$RET` by SICBU, which only p.333 l.2 writes; it serves 15 words from word YDFRDA of the area YRLDTA names, or the end return past an LB area's end. No IBM word is changed. Entry at YRESL1 (p.332 l.2); from there IBM's code runs: YARSL, ARNRM5, the read loop, ALOADR, YLERR/YAERR1 for each library routine, ARNRM4, YBCENC, p.333 ll.1-5.
- **Oracle:** each subprogram assembled ABSOLUTE at p.17's printed origin with its commons at p.17's printed common origins; each vector B,entry;NOP with p.17's entry; SICBU = *MAIN*'s entry 000051.0; the loader's error word YLJSLT unchanged; `$FETCH` served exactly the subprogram cards (53 TWS + 12 LB), never the branch card.
- **Result:** run 2, 214 bench checks pass (212 checks, the PC at DONE, the cycle bound), 341,736 cycles; the library order the loader read was UST*, IOCS*, FISIP* (disk order), and IOCS*'s second entry SPTXT* reached VALUE's vector. Run 3/4, no library calls (so VALUE, on TWS and followed by the branch card, is the last entry): 202 pass (200 checks), 280,355 cycles.

**The sign bit, checked.** LV takes a half word's bit 24 as the index value's sign (the model, `StretchExecute.bsv` dixop_LV; the stub's first bug was LV on YDFRDA, whose `,0` prints `000000.00 80`). BSS writes only the 24-bit fields of KSILO+9 and +10 (deck rule C12), so their bits 24-31 are as MCP left them. That is harmless on this path, as read: YARSL takes KSILO+9.32 with LR (p.333 l.26), a refill without sign, and ARNRM5 writes it back with SV (p.327 l.10) before AFPCRD's LV (p.324 l.17) reads it; ARNRM4's LV of KSILO+10 (p.327 l.28) passes only the address on by SVA. MEASURED: a variant deck clearing those bits whole and the committed deck both load correctly, 341,736 cycles each; the deck is unchanged. (YARSL's LR, p.333 l.26, is from the transcription, not re-read in the ink.)

**Measured** (observed sets in the test's header; the deck injections rerun on the committed deck, same sets):
- C11, count one HIGH on the last entry (no-library run): only `fetches_53_no_branch_card` fails (54 served), 282,079 cycles; every loaded word passes. Count one LOW: only `loaded_213542` fails (VALUE's last card, its word in A, not loaded).
- The disk address one card late (deck, after SCPR1L, `+I(BU,18),15`): 4 fail: `loaded_1006` (STEP's first word), `loaded_1447` and `loaded_1455` (RANDM's), and the fetch count (67 served, not 65); 348,818 cycles.
- The library name left in A8 bits (deck, RT3 `ST(BU,36)` for `SF(BU,36,6)`): 11 fail: YRLDTA names no LB area, so `$FETCH` stops at NOAREA (the PC check), 53 cards are served (the TWS ones only), SICBU keeps its sentinel, and eight words of FISIP*, IOCS* and UST* (2451-2462, 3604, 5517-5520) stay unloaded.
- The common origins one half word late in the table (deck, RT5 `V+I,$13,3.0` for `2.32`): the step cap is reached and 52 fail, read mid-run (so not a clean set): words of every subprogram, its vector and its common references among them.

### R3. The FORTRAN runtime library as STRAP II subprograms (medium-large)

**R3a. ABI ruling** (repo D-2): SIC vs LVI. Read AD0642331 pp.58-59 and LA-3629 in ink.
- Recommendation: emit p.31's `SIC,$X15;B` (the "must be" form) from the compiler, and accept both in the library, since both leave $X15.

**R3b. Initializing routine** (FISIP*?), from p.23 [INK].
- Oracle: mask and $X15 contents after entry, against p.23's text.

**R3c. Math: ALOG, SIN, COS, EXP, ATAN, TANH, SQRT and the `**` helpers.**
- Sources: C22-6578 §4.9-4.11 (IBM's own 7030 code), CHM 102633965.
- Oracle: printed C22-6578 results; DTIC numeric outputs.

**R3d. IOCS family.**
- Format conversion (E, F, I, A, H, X, /, run-time FORMAT arrays), list I/O, system reader/printer/punch through MCP, binary blocked tape/disk, decimal tape, END FILE/BACKSPACE/REWIND, dynamic `$CHEX`.
- Sources: C22-6751 pp.10-13, 23-27; C22-6678-1 MCP I/O; MCP listing IOCS.
- Analogue: 9F00 "FORTRAN COMMON I/O PACKAGE" (2,769 lines) and library 9IOH/9IOS, for decomposition only.
- Size: about 1500-2500 words. IOCS* is 1567 words in C28 p.17's map [REPO-INK].
- Oracle: **the DTIC decks' printed outputs and LA-3416's "LISTING OF INPUT CARDS AND PRINTED OUTPUT"** [DL, grep], compared column for column.

**R3e. STOP/RETURN/PAUSE/dump paths** to `$MCP`/`$ABEOJ`. Oracle: p.23's good-stop and bad-stop lists.

**Test vehicle until R5.** The C22-6751 App. C STRAP subprogram (pp.34-35, transcribed), plus hand-translated STRAP equivalents of small DTIC programs.

### R4. Generator libraries and PROSA (medium)

- Build LFORTRAN/LPASSONE/LPASSTWO/LSMACONE and TFORTRAN.. type areas in the C22-6728-1 p.241 TOFC format: three-word entries, record number for ZTAKE, sort, control bits, memory address, size; at most 300 entries.
- Then UPDATE-30's librarian (SMADDMAC, SMREPLAC, SMYNONYM [so printed, p.241], SMUPDATE, SMDELETE, SMRENAME, SMARANGE), which the repo already lists as M-3.
- Sources: C22-6728-1 pp.228-250 (pp.240-241 [INK]). Oracle: the librarian's error list p.241.
- Resolve the origin-1000₁₀ question against `smac_7030.md` first.

### R5. RECONSTRUCT FORTRAN IV as the PH3 / PH2 / PH1 chain under the LPC (large: the biggest item)

**Sources.**
- The language: C22-6751.
- The chain and COMREC: C22-6729 pp.7-9 [p.7 INK].
- The library form: C22-6728-1.
- SMAC I: J28-6128.
- The IOD rewriting rules: C22-6751 pp.25-29.

**Analogues** (labelled), for phase algorithms where 7030 documents are silent:
- R23-9673 (FORTRAN II sections, generated tables, DO/subscript handling);
- IBFTC source for FORTRAN IV semantics.

**Order.**
1. **R5a. LPC.** Chain coordination and COMREC words 7.32-24.63 (C22-6729 p.8 [OCR]), and the MCP chain "LPC, STRAP, LPC, BSS". Only its interface is documented, so it is mostly CHOSEN.
2. **R5b. PH1** = the existing SMAC I, already reconstructed. Verify that its output feeds STRAP II under the LPC.
3. **R5c. PH3 syntax.** FORTRAN statements become SMAC II-level macro statements, emitted through LFORTRAN generators.
4. **R5d. PH2-1 data glean.** Symbol table, types, DIMENSION/COMMON/EQUIVALENCE/DATA, storage. Then **PH2-2/2-3**: expansion, then indexing (DO loops, subscripts to index registers).
5. **R5e. Object conventions** to reproduce:
   - transfer vector at cell 1, length in cell 0;
   - `VF,a1;VF,a2` argument words;
   - all 16 index registers saved;
   - integer-as-float-with-exponent-38;
   - logical in bit 59;
   - the initializing-routine call first in MAIN;
   - FORTRAN Program card size "all 1's" when FORTRAN generates it (C28 p.7, REPO-INK).

   **Oracles.**
   - *Behavioural, strongest available:* compile and run the DTIC programs (AD0646577 CHITRAN and its siblings AD0663887 and AD0665291; AD0685715) and the LASL decks (NECKLACE LA-3115-MS with its UHTREX sample; LA-3416 with printed output; HOTFLO LA-3428). Compare printed output digit for digit.
   - *Interface:* BSS accepts the deck, and the map is plausible.
   - *Language coverage:* every example statement in C22-6751, run as its own test.
   - **There is no oracle for generated code.** No LSTRAP listing is known (§2.2). Generated STRAP must be labelled RECONSTRUCTION, and only its behaviour can be checked.

   **Transcription first.** The DTIC/LASL decks need transcribing with the project's listing discipline. They are OCR-poor scans: read in the ink, card by card.

   **Size.** 7090 FORTRAN II's compiler is 35,099 FAP lines; IBFTC is 55,304 lines plus 18,749 library lines [DL, `wc`]. The 7030 version is generator-driven, so much of the code becomes generator-library content. Expect the largest single reconstruction in the project, comparable to or larger than STRAP II.

6. **R5f. FORTRAN IV under MCP end to end.**
   - `B TYPE,COMPILGO,FORTRAN` → LPC → STRAP II → LPC → BSS → resume load → run → output.
   - Depends on R0, R2, R3, R4, and E6 (STRAP II as a 7030 program under MCP).

### R6. The DTIC/LASL jobs as the acceptance suite

Status of each candidate oracle as checked this session:

| deck | source cards | input data | printed output | basis |
|---|---|---|---|---|
| AD0646577 CHITRAN (NWL 1967) | **confirmed**: FIOD and FORTRAN main start, printed p.46 [INK] | not checked | not checked | ink p.46 |
| AD0685715 IMSCAT (1968) | **confirmed**: FORTRAN subroutine p.89 [INK]; STRAP subprogram p.79 [INK] | not checked | not checked (repo cites App. III) | ink |
| AD0663887, AD0665291 (NWL) | `SUBTYPE` not grepped; repo says "the same kind of deck" | not checked | not checked | repo |
| AD0642331 XPSTC (MITRE) | STRAP-level calling sequence only (OCR) | — | — | repo OCR |
| LA-3115-MS NECKLACE | `SUBTYPE,FORTRAN` cards present (grep) | sample problem "NEK-IV (UHTREX)" named (grep) | not checked | [DL] grep |
| LA-3416 | not grepped for SUBTYPE | — | contents line "LISTING OF INPUT CARDS AND PRINTED OUTPUT" (grep) | [DL] grep |
| LA-3428 HOTFLO | `SUBTYPE,FORTRAN` cards present (grep) | not checked | not checked | [DL] grep |

Two limits on "digit for digit":
- Several programs read tape or disk data (e.g. AD0646577's `IOD,TAPE,...,SAVE` and two disk files), which may not be printed. Those runs need the data reconstructed, or cannot be compared.
- A reconstructed math or conversion library can differ from IBM's in the last digits. Compare to a tolerance first, and record every differing digit as a finding about the library, not as a pass.


The scientific-workloads track (`docs/scientific_workloads.md`) starts after this.

---

## 4. Open questions, and what is unknowable

**Q1. Allen's compiler versus the shipped compiler.**
- Is the C22-6729 Fig. 1 generator chain Allen's Stretch compiler as shipped, later replaced by an undocumented "simpler, faster" one? Or is the chain itself that replacement? Both readings and their evidence are in §2.3 item 5; it is not decided.
- Allen's CGO slide says "Stretch compiler for Fortran replaced with simpler, faster compiler" [DL].
- Fig. 1 does show a processor and phases consistent with a macro chain [INK].
- The DTIC decks' LMAP suggests at least one later release.
- To settle it, get Allen 1981's text (F8) and look for a dated FORTRAN processor version string in any DTIC listing header.

**Q2. The calling sequence (D-2).** `SIC,$X15;B,name` (p.31, "must be") versus `LVI,$15,$+1;B,name` (App. C; AD0642331; LA-3629). Which did the compiler emit? Not determined. The first place to look is AD0642331 pp.58-59: it is held, its OCR shows `LVI, 15, $+1`, and I have not read it in the ink.

**Q3. The transfer-vector length word.**
- p.31 says "first 18 bits of cell zero must contain an integer" and shows `XW,,ENDTV-BEGINTV` (a count field) [INK].
- App. C uses `XW,,2` [INK].
- C22-6729 p.184 uses `DD(BU),1.0` (NEXT.md open item, message 45).
- The loader reads `SRTVL`. The 7030 FORTRAN II-era answer is unknown.

**Q4. PPC and "A2".** What "PPC" (C22-6729 p.7) is. Whether a SMAC II deck description exists (only `A1` is printed).

**Q5. Generator origin.** The C22-6728-1 p.241 binary-deck origin 1000₁₀ versus `smac_7030.md`'s CHOSEN origin 0.

**Q6. Library contents and names.**
- Beyond the six closed functions, and FISIP/IOCS/SPTXT/UST, the library list is unknown until F1.
- What FISIP, SPTXT and UST stand for is unknown. My guesses are FORTRAN initialization, special text and a utility, and they are names-based guesses only.

**Q7. Segmentation encodings** (spec G8-G11). The link-program encoding, link-table mask, node-table encodings and TWS arc headers are not printed. Choosing from the IBLDR Overlay analogue is a reconstruction, not a recovery.

**Q8. LMAP and later options.** What LMAP produces, and what else the 1966-68 compiler changed. No manual edition later than May 1963 is held (F2 may answer).

**Unknowable without a find:**
- the internals of every phase (PH3, PH2-1..3), including their tables and diagnostics;
- the generator libraries' contents;
- the exact generated code;
- BSS's code size and in-core layout;
- the checksum algorithm (spec G3).

A reconstruction can be behaviourally faithful (same decks in, same printed output, same BSS map and messages) but not bit-faithful. Every generated word is RECONSTRUCTION until F1-F4 turn something up.

**Things I could not do or did not check:**
- C28-6066-6, C28-6274-1 and C28-6275-2 have no text layer and were not read.
- IBLDR's deck format is unverified.
- The LASL decks were grepped, not read.
- C22-6751 pp.1-14, 18-22 and 25-37 are OCR only.
- C28-6379 itself was not re-read; I relied on the spec.
