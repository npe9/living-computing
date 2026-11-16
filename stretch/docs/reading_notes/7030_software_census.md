> **STATUS: UNVERIFIED FINDING AID.** Written by a reading agent on 2026-11-15
> from page images. Nothing here may be cited as a source: every quote must be
> re-read in the ink (the page image) before it is relied on, as AGENTS.md
> requires. Passages the agent could not read confidently are listed at the end.

# IBM 7030 software census: what the literature names, what the project holds, what is missing

Compiled 2026-11-15. Research notes only; nothing in the repository was changed.

## 0. Status labels and method

- **WEB**: I retrieved the raw page or PDF this session and read or grepped the text myself. Saved copies are in
  `/private/tmp/claude-501/-Users-npe-src-living-computing/cafb2b5a-a625-41ec-b286-ef7f699a9ef0/scratchpad/web/`.
- **REPO**: stated in the project's own docs. I say which file, and whether the repo marks it "read in the ink" or
  "delegated, not re-checked". I did not upgrade the latter.
- **REPO-OCR**: I read it this session in the repo's OCR or a PDF text layer. Not read in the ink (rule 4 still applies).
- **SEARCH**: a search engine's summary of a page I could not or did not open. Treat as UNVERIFIED until the page is read.
- **UNVERIFIED**: my recollection, no source retrieved.

Sites that refused scripted access this session, and were not worked around: FAS (`sgp.fas.org`, HTTP 202 challenge, empty
body), `media.defense.gov` (served HTML, not the PDF), `classiccmp.org` (403), `cacm.acm.org` (403). CHM catalog pages were
not fetched (the repo records that CHM refuses automated catalog fetches). These need a person with a browser.

## 1. What the project already has or knows

From `docs/programming_environment.md`, `docs/reconstruction_plan.md` §3 and §5, `docs/archival_inventory.md`,
`docs/chm/README.md`, `docs/thirdparty_software/README.md`, `docs/dtic/README.md` (all REPO).

| piece | state in the project |
|---|---|
| MCP (March 1963 listing, 451 pp) | **original, transcribed**, assembles bit-exact, boots, runs the command package; printed p.329 missing |
| MCP overlays 22LOADER, 22$DUMP, 22SCOMD, 22$EOJ; input program; DISK FETCH | original, transcribed as part of MCP |
| PROSA dictionary and index (11A11DIC, 11B11IND) | **reconstructed** (`strap/prosa_dict.py`) |
| UPDATE-30 (system build and librarian) | manual only (C22-6728-1 pp.228-250); bulletin C22-6718 named, not held |
| Restart (33RESTRT) | manual only (C22-6728-1 pp.102-106) |
| MCP Loader / BSS processor and segmentation | manual only (C28-6379-0); the TA/TB loader code is in the listing |
| STRAP II | internals guide only (C22-6729); 3 printed listing fragments transcribed; a 7030 reconstruction is in progress |
| SMAC I | **reconstructed**, host-side and as a 7030 program, from bulletin J28-6128 (CHM 102634360) and errata |
| SMAC II (FORTRAN's middle phases) | named only (C22-6729 p.7) |
| FORTRAN IV compiler | manual only (C22-6751); bulletin J28-6127 held; FORTRAN Analysis Guide named, not held |
| FORTRAN I/O library, math library | manual only; partial source in C22-6578 §4.9-4.11 and CHM 102633965 |
| 1401 support programs (Symbolic Update, Tape Labeling, SPI I/II, SPO) | manual only (C22-6728-1 pp.224-227, 250-259) |
| CONDEF (pre-MCP console debugger); "Primitive Supervisor" (CHM 102633932) | spec only |
| STRAP-1 and the 7030 Simulator (on 704/709/7090) | manuals only (C22-6531; CHM 102633953, 102634944) |
| 704 Simulator and 709 Simulator (running on the 7030) | named only (J22-6532 = CHM 102634122) |
| Diagnostics: DCP (KA UA1), SSIP (JA UA1), I-Box 1-5, FP (JB AF1C), three memory tests, BX-0, KA UL1, JA UC1A | **original listings held**, partly transcribed and run |
| Diagnostics not held: JB AV1C (VFL), KA AT1, KA BT1, JA AT1, KC AF2/AF2B, KC AV2B, JA EE3, JA CE1/CE2, JA ES1, JA NE4-6, JA UD1A, KA SS1 SEVA | named; several are at CHM (Lowell Wood collection), unscanned |
| MITRE and NWL Dahlgren user programs (XPSTC, MERGE, IMSCAT, CHITRAN, BI-CHI, FORSIM IV ...) | **original listings in DTIC reports**, held in `docs/dtic/` |
| LASL IVY and COLASL; AWRE S1/S2/S3; MITRE LISP 1.5 and MATHLAB | documentation trail only; no source |
| Livermore's own OS and FORTRAN (STIPIC); Purdue FORTRAN IV; TREET; HOPS and ALPHA | named in `reconstruction_plan.md` §5 item 9 |
| A machine-readable tape, deck or disk image of anything | **none known** |

## 2. bitsavers: every document, and what software it describes (WEB, mirror listing fetched 2026-11-15)

Source: `http://bitsavers.trailing-edge.com/pdf/ibm/7030/` and `/7950/`. The 7030 tree is 52 PDFs; every filename is in
`docs/` (scripted check this session: 52 of 52 present, none missing).

Top level (23):
- `22-6530-2_7030RefMan.pdf`: Reference Manual. Machine, not software.
- `C22-6531_7030xasm-sim_1960.pdf`: the 704-709-7090 Programming Package. **STRAP-1** ("produced by the Los Alamos
  Scientific Laboratory", REPO-OCR line 21) and the **7030 Simulator** (IBM).
- `C22-6578_7030_Programming_Examples_Apr61.pdf`: programming examples, including math routines.
- `C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf`: **STRAP II** internals.
- `C22-6751_7030_FORTRAN_IV_May63.pdf`: **FORTRAN IV** language manual.
- `C28-6129_STRAP-II_with_update_Apr63.pdf`: STRAP II language manual with update N28-1081.
- `X28-6131_MCP_PocketCard.pdf`, `X22-6533_7030_PocketCard.pdf`: cards.
- `7030_Opcode_List.pdf`, both Performance Characteristics volumes (these hold measured benchmark listings).
- Design and history, no software: `1956_fallJCC`, `1959_fallJCC`, `ADescriptionOfStretch_Dec59`, `Bloch_EngrDesOfStretch_1959`,
  `D22-6513_7030_genInfo_1960`, `LASL_Jun61Article`, `Planning_A_Computer_System`, `TR00.03000.703_StretchVM_59`
  (the Cocke-Kolsky timing simulator, a 704 program), `TR00.719`, `TR00.722`, `A22-6552` and `-1`.

`mcp/` (8): `MCP_Mar63_001-249` and `250-445` (**the MCP listing**), `C22-6728` and `-1` (MCP Analysis Guide, which also
documents UPDATE-30, Restart and the 1401 programs), `C22-6678-1` (MCP Reference), `J22-6559` (MCP User's Guide, Dec 1960),
`C28-6379-0` (**Loader and BSS Processor**), `N22-0085` (update).

`diag/` (16): `7030_SystemTestPrograms_Aug61` (index), `ja_ax1a`, `jb_ax2a`, `jb_ax3a`, `jb_ax4b`, `jb_ax5b` (I-Box 1-5),
`jb_af1c` (floating point), `ja_bb6b`, `ja_bm6a`, `ja_bp6a` (memory), `ja_ua1_ssip`, `ja_uc1a_maintenance_tape`,
`ka_ex1`, `ka_ex1b` (BX-0), `ka_ua1_diagnostic_ctl_pgm` (**DCP**), `ka_ul1_load_and_tape_write_util`. All are listings.

`ce/` (5): R23-9694, R23-9695, R23-9702, R23-9713, R23-9732. Hardware. R23-9732 names two more CE programs (see 3.6).

`7950/` (3, HARVEST-only): `Harvest_prelim_May57.pdf`, `Harvest_Nov1957.pdf`, `R22-9789_7950_HAP_III_Ref_Man_1962.pdf`
(**HAP III**, the Harvest assembler plus Autocoder). The repo lists these as known and not held.

There is no software image directory for the 7030 on bitsavers (REPO: `archival_inventory.md`, "no `bits/IBM/7030/`").

## 3. The census

### 3.1 IBM system software for the 7030

| item | what | documents | source/listing survives? | status |
|---|---|---|---|---|
| **MCP** | "an automatic operating system, a flexible input-output system, debugging aids, automatic interruption handling, and a first level of multiprogramming" (J22-6532) | J22-6559 (1960); CHM 102633187 Preliminary Reference, Nov 1961 (unscanned); C22-6678-0/-1; N22-0085; C22-6728/-1; X28-6131 | **Yes**: March 1963 listing on bitsavers. A later MCP (1964) is described but not listed | REPO; quote REPO-OCR from CHM 102634122 |
| MCP components: interrupt control, system operation, system I-O (IOCS), command package, input program, loader, $DUMP, $EOJ, DISK FETCH, logging hook | parts of MCP | C22-6728-1 | in the listing | REPO |
| **UPDATE 30** | system update / librarian: "A program called UPDATE 30 is available to facilitate the incorporation of changes into the current system located in the PROSA area of the disk ... see page 215 of the MCP Programming Systems Analysis Guide (C22-6728), or the bulletin published on the UPDATE 30 program (C22-6718)" | C22-6678-1 PDF p.40; C22-6728-1 pp.228-250; **bulletin C22-6718 (not held anywhere found)** | no listing known | REPO-OCR (quote); REPO |
| **Restart** (33RESTRT) | checkpoint restart | C22-6728-1 pp.102-106 | no | REPO |
| **Loader and BSS Processor** | relocatable loading, segmentation | C28-6379-0 | loader TA/TB in the MCP listing; BSS processor not | REPO |
| **PROSA** contents (the system library on disk) | MCP's type areas, plus "library areas" the repo records as LFORTRAN, LPASSONE, LPASSTWO, LSMACONE (which processor owns which is my guess from the names, not sourced) | C22-6728-1 | only MCP's type areas | REPO (names OCR only) |
| **STRAP II** | the native assembler | C28-6129; N28-1081; C22-6729; C22-6678-1 p.48 | **No listing of the assembler itself.** CHM 102633945 is one page the repo takes to be assembler code ("STRAP II" is the repo's inference; the page names no version). C22-6678-1 p.48 and N28-1081 App. E are listings STRAP II *printed for user programs*: output format, not STRAP II source | REPO |
| **SMAC I** ("System Macro Language and Processor") | macro processor, link between STRAP and FORTRAN | J28-6128 (CHM 102634360), errata 102634361; SMAC Analysis Guide (not held) | no | REPO |
| **SMAC II** | FORTRAN's middle phases (PH2) | C22-6729 p.7 only | no | REPO |
| **FORTRAN (FORTRAN IV)** | "The 7030 Fortran processor will translate Fortran statements to SMAC statements" (J22-6532) | J28-6127 (CHM 102634362, 1961); C22-6751 (May 1963); CHM 102665489 (another copy/edition, unscanned); FORTRAN Analysis Guide (not held) | no | REPO; quote REPO-OCR |
| FORTRAN library (I/O, FORMAT conversion, math functions) | runtime | C22-6751 Part II and appendices | no | REPO |
| Math subroutines | sine/cosine, log, exp, matrix | C22-6578 §4.9-4.11; CHM 102633965; conventions CHM 102633957 (May 1960) | **partial source, printed** | REPO |
| Multiple-precision programs; "noisy mode" subroutine and interpretive FP program | early routines | CHM 102634952, 102632663, 102634947; 102634131, 102634133, 102634141 (a listing), 102634146 (matrix inversion listing) | **short printed listings held, unread** | REPO (titles are CHM catalog's) |
| **1401 support programs**: Symbolic Update, Tape Labeling, SPI I, SPI II, SPO | off-line input/print/update on the 1401 | C22-6728-1 pp.224-227, 250-259 | no | REPO |
| **704 Simulator, 709 Simulator** (run ON the 7030) | "will permit 704 and 709 programs to be run on the 7030 with a minimum of reprogramming" | J22-6532 (CHM 102634122) | no | REPO-OCR (quote) |
| "installation logging routine" | example of a service routine added to MCP | J22-6532 | n/a | REPO-OCR |
| "Specifications Notebook (for Programs)", Dept. 271 | IBM's internal program specs, "available on a limited basis" | CHM 102634363 (publications list, July 1961) | not located | REPO (read in the ink) |
| IBM sort / merge / report generator for the 7030 | — | none found. The Kolsky index has only 1956-57 sorting studies (102633966, 102634921, 102634922). The one 7030 merge found is MITRE's (3.4) | — | absence is UNVERIFIED |

### 3.2 Pre-MCP and cross-hosted tools

| item | what | documents | survives? | status |
|---|---|---|---|---|
| **STRAP-1** | cross-assembler on 704/709/7090, written at LASL (Gatt, Motteler, Lewis, Evans, Thomas per CHM 102634944's catalog title) | C22-6531; CHM 102633953 (104 pp, May 1959), 102634944 (60 pp), 102633933, 102633938, 102633955/56/58 | no listing known. A SHARE distribution is plausible but I found no record | REPO; SHARE remark UNVERIFIED |
| **7030 Simulator** (704, 709, 7090) | IBM; runs STRAP-1 output | C22-6531 | no | REPO |
| "Ranch STRAP" | a STRAP for Harvest? | CHM 102635031 (1 p, Nov 1958), held, unread | — | REPO (title only) |
| **Primitive Supervisor** | binary loader, origin/flow/branch/dump cards, interrupt table, debugging macros | CHM 102633932 (66 pp, 1959) | spec only | REPO (text layer) |
| **CONDEF** | console-defining debug routine | CHM 102632570 (32 pp), 102632571 | spec only | REPO |
| SIM-2 / Sigma timing simulator (Cocke, Kolsky) | 704 program used to size look-ahead | TR00.03000.703; CHM 102634322, 102633975, 102634942 (coding form) | printouts only | REPO |

### 3.3 Diagnostics and CE programs

Held and not-held lists are in `archival_inventory.md` (REPO). Additions from this pass:

| item | what | documents | status |
|---|---|---|---|
| **XTDT1, XTDT2** | "Index Tunnel Diode Tuning Tape (Two Programs, XTDT1 and XTDT2)", cited with "Index Tunnel Diode Storage Unit, 7101 Instruction Unit IBM CEIM, Form R23-9916" | R23-9732 OCR lines 1743-1746 and 23311-23314 | REPO-OCR. Not mentioned in any repo `.md` |
| CHM 102698889 (diagnostic reference manuals 1-16, 18-28), 102698893-97 (listings incl. JB AV1C, KA AT1, KA BT1, JA AT1, KC AF2/AF2B, KC AV2B) | Lowell Wood (LRL) collection | catalog only | REPO (delegated search) |
| The DCP's own test-ID roster | a second index of programs | inside `ka_ua1` | REPO says "not checked" |

### 3.4 Site-written software (7030)

**Los Alamos (X-1)**

| item | what | documents | survives? | status |
|---|---|---|---|---|
| **IVY** | per two search summaries (paraphrase, not the report's words): an algebraic coding system for the IBM 7090 and 7030; a load-and-go, one-pass compiler-assembler | LAMS-2607, "The IVY System". A scan is indexed at `https://sgp.fas.org/othergov/doe/lanl/lib-www/la-pubs/00371060.pdf` | the report may contain the language in full; no source known | SEARCH (two search summaries agree; FAS returned HTTP 202 with an empty body to my fetch). The repo knows LAMS-2607 "catalogue only" and does not have this URL |
| **COLASL** | algebraic compiler with 2-D mathematical notation input | ACM '62 pp.44-45, doi 10.1145/800198.806099 (held in `thirdparty_software/`); LADC-5173 | no | REPO |
| LASL history | — | Lazarus et al., LA-6943-H (1978), `https://sgp.fas.org/othergov/doe/lanl/docs1/LA-6943-H.pdf` | — | not retrievable by script (HTTP 202); REPO says the same |
| **STRETCH SIN** | 1-D reactive hydrodynamics, said to be in 7030 machine language (paraphrase) | said to be named in LA-3720 (Mader and Gage, 1967); report number from a search result, not opened | unknown | SEARCH |
| **STRETCH BKW** | detonation equation-of-state code; an earlier internal 1962 report is said to exist (paraphrase) | said to be named in LA-3704 (Mader, 1967); from a search result, not opened | unknown | SEARCH |
| **2DE (7030 version)** | "a code for the IBM 7030 computer for computing two-dimensional reactive hydrodynamic problems in cylindrical geometry"; "written to make maximum use of the large capacity disk storage of the IBM 7030 (STRETCH) computer"; "presents sufficient details for a coder to be able to follow and change the code" | **LA-3629**, W. R. Gage and C. L. Mader, 1966 (author, number and date from the OSTI record `https://www.osti.gov/biblio/4454572`, fetched), 35 pp, full text at `https://www.osti.gov/servlets/purl/4454572`. Its successor LA-4846 (`https://www.osti.gov/servlets/purl/4656584`) says: "A one-component Eulerian hydrodynamic code written by Gage and Mader in STRETCH machine language"; "because of the untimely death of STRETCH, a FORTRAN version ... was needed" | **a 35-page description written for coders.** No full listing in the text layer. It does print input card formats and one STRAP calling sequence, for the ISOPLOT 4020 plotting subroutine: `LVI,$..,$+1` / `B,ISOPLOT..` followed by eight argument words (text lines 804-814; OCR-quality, index register illegible). That is the `LVI ...,$+1; B,name` form the repo's open question D-2 is about, seen at a third site | **WEB** (both PDFs fetched, quotes from their text layers). Not in the repo |
| Mader reports GMX-2-R-63-1, LA-DC-6595 | Stretch codes | OSTI catalogue | — | REPO (delegated) |

**Livermore (K-1)**

| item | what | source | status |
|---|---|---|---|
| Livermore FORTRAN compiler for Stretch | "Livermore developed a Fortran compiler for the STRETCH. Fortran was used for many smaller production jobs but the few bigger jobs remained in assembly language." | Norman Hardy memoir, `https://computer-history.info/Page4.dir/pages/IBM.7030.Stretch.dir/index.html`; same text at `http://cap-lore.com/Hardware/Stretch.html` | **WEB** |
| A "rudimentary operating system" that "normally remained in place between jobs"; later "the OS would request magnetic tapes enough in advance" | same | **WEB** |
| Code-group private operating system | Harry Nelson: "there wasn't even an operating system for the Stretch; it was under construction by IBM, and hadn't been delivered yet. We basically were able to produce our own operating system as part of the code package." (nelson.txt lines 38-40, read) | `https://computer-history.info/Page1.dir/pages/Nelson.html` | **WEB** |
| STIPIC | The interviewer (GAM) says: "It was the thing that Norman Hardy wrote to do all the I/O and things like"; Nelson answers "STIPIC? No." | same | **WEB**; the attribution is the interviewer's alone |
| "IBM's operating system and Livermore extensions that Clarence Badger and Garret Boer basically put together" | MCP as extended at LRL | same | **WEB**. Badger and Boer are not in the repo |
| The person "who saved the Livermore Stretch" and its software | Al Kossow, cctalk, July 2015 | REPO (`archival_inventory.md`; delegated) |

**AWRE Aldermaston (K-2)**

| item | what | source | status |
|---|---|---|---|
| **S1** FORTRAN | Glennie's first Stretch FORTRAN | UK National Archives ES 10/803 (1961) | REPO (delegated) |
| **S2** FORTRAN | per search summaries of the catalog record (paraphrase): the S2 compiler runs on the IBM 7030 and accepts a dialect of FORTRAN 2 called S2 | **Joan Knock and Mary U. Thomas, AWRE manual, August 1964: CHM catalog 102724621** | SEARCH (two search summaries of the CHM catalog record). **Not in the repo.** Also ES 4/995 (1968 manual for S2 and S3), REPO |
| S3 (Atlas 2), said to have been developed on the 7030 by an interpretive technique (paraphrase) | Atlas compiler bootstrapped on Stretch | Wikipedia "Alick Glennie" via search; BCS jubilee page (held as text in `thirdparty_software/`) | SEARCH / REPO |
| A paper in *The Computer Journal* on S1/S2 | — | **none found** in three searches. I could not confirm that one exists | UNVERIFIED (the task brief assumed one) |

**MITRE, then BYU**

| item | what | source | status |
|---|---|---|---|
| **LISP 1.5 for the 7030** | "LISP 1.5 was implemented on the IBM 7030 (STRETCH) computer at The MITRE Corporation by Roland Silver and Paul Heckel." | `https://softwarepreservation.computerhistory.org/LISP/other_lisp15.html` | **WEB**. That page lists no manual or source for it, only Engelman 1965. Silver is not in the repo |
| MATHLAB | on-line symbolic mathematics, in LISP | Engelman, FJCC 1965 (held) | REPO |
| XPSTC, MERGE, FORSIM IV, IMSCAT; STAPP (TM-67); "7030 Facility Manual" (Aug 1965) | MITRE programs and local documentation | DTIC reports in `docs/dtic/` | REPO |
| **SOS, "Stretch Operating System"** | "written at the BYU Scientific Computing Center as an upgrade to MCP, along with an updated variant of FORTRAN" | English Wikipedia, "IBM 7030 Stretch", Software section (raw wikitext fetched; **the line carries no citation**) | **WEB** for the sentence; the fact itself is UNVERIFIED. **Not in the repo** |
| BYU machine history | sold to BYU spring 1972, used by physics department, scrapped 1982 (Wikipedia); decommissioned 5 September 1980 according to a CHM "this day in history" page (search summary, paraphrase) | Wikipedia WEB; CHM SEARCH | dates disagree |

**NWL Dahlgren**: CHITRAN, BI-CHI, Kolmogorov test, incomplete beta function; real job decks. REPO (`docs/dtic/`).

**US Weather Bureau (General Circulation Research Laboratory, later GFDL)**: the Smagorinsky-Manabe-Holloway nine-level
general circulation model. "The MARKFORT series began with Smagorinsky's nine-level, 3-D hemispheric model ... Initially,
the model was run on the IBM STRETCH." (`https://www.pne.people.si.umich.edu/sloan/center_descriptions/i.GFDL.html`, a
University of Michigan history-of-GCMs page; fetched.) **WEB**, secondary source. Not in the repo. No code located. Wikipedia (WEB) gives delivery as June/July 1962.

**Others named in the repo, not re-checked here**: Purdue FORTRAN IV (1965); TREET (NBS, 1967). REPO.

### 3.5 HARVEST-only (IBM 7950) — separate list

Source: Samuel S. Snyder, *History of NSA General-Purpose Electronic Digital Computers*, 1964, declassified; fetched from
`https://nsarchive.gwu.edu/sites/default/files/documents/3121322/Document-02.pdf`; section "HARVEST Operational System
(HOPS)", printed pp.61-64. **WEB**, quotes from the PDF's text layer.

| item | what (Snyder) |
|---|---|
| **HOPS** | the HARVEST Operational System; "based upon an operational cycle that processes work as much as possible in batches" |
| **HCP** | "Executive, or HARVEST Control Program (HCP)"; specified by NSA after May 1960 |
| **MCP ("Machine Control Program")** | assigned to IBM in Feb 1960; implemented under task CLAGHORN (signed March 1961, extended to 30 Nov 1963). Snyder's name for it differs from the 7030's "Master Control Program"; whether it is the same code is not stated |
| **HAP** | HARVEST Assembly Program (IBM) |
| **Autocoder** | macro level above HAP; "the combination of HAP and Autocoder, called HAP III" (manual: R22-9789, bitsavers 7950) |
| **ALPHA** | "Advanced Language for Programming HARVEST"; NSA's ALPHA Language Technical Report, June 1960; "about 35 IBM personnel were implementing ALPHA" by Aug 1960; CHM 102634929 "Preliminary samples of the Alpha language" (Sept 1959, held in `docs/chm/`) |
| **JRL** | Job Request Language (NSA) |
| **GFO** | Generalized File Operators (NSA) |
| **TRACTOR File Maintenance** | catalog and file handling for the TRACTOR tape system |
| 1401 input/output programs | 729 tape preparation and printing "in the HARVEST complex" |
| **BETA** | Snyder's HOPS section does not name a BETA language. (The words BETA and ALPHA at text line 1319-1321 are labels in a console drawing of an earlier machine, not languages.) Wikipedia's 7950 article is reported to say two languages, Alpha and Beta, were designed (SEARCH). Not in the repo as a language |
| Stretch-Harvest compiler (Fran Allen) | one compiler framework for FORTRAN, ALPHA and Autocoder | CACM interview with Allen, 2008-2011 (SEARCH; the page returned 403) |
| NARA RG 457 scans at fpgacpu.ca/harvest ("Initial Harvest Control Program" 1960, "Diagnostic Library 7950" 1959) | REPO (delegated) |

Snyder also records that IBM first proposed a Harvest programming system that would be "a consolidation of work done in
connection with the AEC STRETCH system with FORTRAN", so the 7030 and 7950 compilers share ancestry (WEB).

### 3.6 Literature and people

- Buchholz, *Planning a Computer System* (1962): a 25-line grep of the OCR for STRAP, FORTRAN, compiler and supervisory
  program found no named shipped program (no hit for STRAP at all); the book was not read through. It gives the design intent for the
  supervisory program and compiler (ch. 13 area, OCR lines 11626-11721) and says "at least half of all computer time
  would be used by compiler-" (OCR line 1948). REPO-OCR.
- Codd, Lowry, McDonough, Scalzi, "Multiprogramming Stretch: feasibility considerations" (TR 00.719, held) and Codd,
  "Multiprogram scheduling" (TR 00.716, held). REPO. Their CACM publication details are UNVERIFIED.
- CHM "Stretch Reunion" oral histories, September 2002, interviewer Dag Spicer: Walter Doherty, Bill Collier, Gordon
  Smith (catalog 102636415), Peter Markstein, Stu Tucker (transcript at
  `archive.computerhistory.org/resources/text/IBM/Stretch/transcripts/Stu_Tucker_102636408.doc`); catalog numbers
  102636403, 102636405, 102636420 also appear. SEARCH. Not in the repo. Which of them wrote software is UNVERIFIED.
- Stretch users' group: CHM 102634369, 102634371 (July 1961); UK ES 10/1020 (Washington, Feb 1963). REPO.
- CHM 102663031: a bundle of FORTRAN documents said to include 7030 FORTRAN IV material. SEARCH. Not in the repo.
- A classiccmp post titled "I have a document that describes how to convert 709 Fortran to ..." appeared in a 7030
  search. SEARCH, title only (403).

## 4. Conclusions

### (a) Gap table: literature items the project does not have, ranked by importance to running the real environment

"In repo?" means mentioned anywhere in the repo's `.md` files (grep, this session).

| rank | item | why it matters | source and status | in repo? |
|---|---|---|---|---|
| 1 | **A STRAP II listing, the FORTRAN IV compiler, SMAC I/II code, the BSS processor, the FORTRAN and math libraries** | the whole language chain under MCP; none survives in any archive found | C22-6729, C22-6751, C28-6379, J22-6532 (REPO) | yes, known lost |
| 2 | **UPDATE 30 bulletin, C22-6718** | the only separate write-up of the program that builds PROSA and the system tape | C22-6678-1 PDF p.40 (REPO-OCR quote) | yes (`boot_plan.md`), not held |
| 3 | **FORTRAN and SMAC Programming Systems Analysis Guides** | the internals of two of the four system programs | C22-6728-1 p.7 (REPO-OCR) | yes, not held |
| 4 | **704 Simulator and 709 Simulator on the 7030** | IBM-shipped pieces of the package; would also let 704/709 software run | J22-6532 (REPO-OCR quote) | yes, find-only |
| 5 | **1401 support programs (SPI, SPO, Symbolic Update, Tape Labeling)** | MCP's input and print tapes are made and consumed off-line by these | C22-6728-1 (REPO) | yes, spec only |
| 6 | **BYU's SOS and its updated FORTRAN** | the last operating system run on a 7030, on the machine now partly at CHM; the latest and so the likeliest software to survive on tape or paper | Wikipedia sentence (WEB), uncited; fact UNVERIFIED | **no** |
| 7 | **Livermore's MCP extensions (Badger, Boer), Livermore FORTRAN, the code groups' own OS** | a real site's production environment; LRL's machine is at CHM | Hardy memoir, Nelson interview (WEB) | partly (STIPIC, "Livermore FORTRAN"); Badger and Boer no |
| 8 | **AWRE S2 manual, Knock and Thomas, Aug 1964, CHM 102724621** | a complete language manual for the second 7030 FORTRAN compiler, in a US archive | CHM catalog via search (SEARCH) | **no** (repo has only the Kew references) |
| 9 | **IVY report LAMS-2607 full text** | LASL's production compiler-assembler for the 7030; the report is the language definition | FAS URL above (SEARCH; blocked to scripts) | LAMS-2607 yes; the full-text URL no |
| 10 | **LASL 7030 application codes: 2DE, STRETCH SIN, STRETCH BKW** | real weapons-lab workloads, exactly what `scientific_workloads.md` §1 says to search for first | 2DE: LA-3629, OSTI 4454572, and LA-4846, OSTI 4656584 (**WEB**); SIN, BKW: LA-3720, LA-3704 (SEARCH) | partly: the repo cites Mader's Stretch codes by report number (GMX-2-R-63-1, LA-DC-6595), not by name, and not the OSTI full text |
| 11 | **MITRE LISP 1.5 (Silver and Heckel); STAPP; the 7030 Facility Manual** | a second language system on the machine that became BYU's | softwarepreservation.org (WEB); DTIC (REPO) | LISP yes; Silver no |
| 12 | **Weather Bureau / GFDL general circulation model on Stretch** | a named production workload | GFDL history via search (SEARCH) | **no** |
| 13 | **XTDT1/XTDT2 tunnel-diode tuning tapes; Form R23-9916** | CE programs; whether the Aug 1961 System Test index lists them was not checked | R23-9732 (REPO-OCR) | **no** |
| 14 | **HARVEST-only: HCP, JRL, GFO, TRACTOR File Maintenance, Autocoder, BETA, the Stretch-Harvest compiler** | not needed for a 7030; the DCP targets "7030/7950" | Snyder 1964 (WEB); BETA and Allen (SEARCH) | HOPS, ALPHA, HAP yes; the rest **no** |
| 15 | An IBM sort/merge for the 7030 | none is named in any document read; record the absence | — | n/a |

### (b) Leads for lost originals

1. **BYU, L. Tom Perry Special Collections and the Physics and Astronomy department.** BYU ran the last 7030 until
   1980-82 and is said to have written SOS and a FORTRAN variant. A site that modified MCP had MCP's source, STRAP II and
   the compiler in machine-readable form. Ask for SOS listings, system tapes, the MITRE hand-over material (the "7030
   Facility Manual"). Basis: Wikipedia (WEB, uncited); repo already names BYU for MITRE's LISP.
2. **CHM, three separate requests.** (i) 102724621, the AWRE S2 manual (SEARCH). (ii) the Lowell Wood (LRL) collection
   X2462.2002: diagnostics 102698889-97 (REPO). (iii) 102663031 (FORTRAN bundle), 102665489, 102663038, 102633187 (REPO
   and SEARCH). Also ask what came with the LRL and MITRE/BYU hardware lots: tapes, card decks, disk packs.
3. **CHM Stretch Reunion transcripts (2002)** on `archive.computerhistory.org/.../Stretch/transcripts/`: read them for the
   names of MCP, STRAP II and FORTRAN programmers and for any mention of retained listings (SEARCH).
4. **The Livermore trail.** Kossow's unnamed "person who saved the Livermore Stretch" (REPO); Norman Hardy's pages; the
   computer-history.info interview series (George Michael's project), which names Clarence Badger and Garret Boer as the
   authors of the Livermore MCP extensions (WEB). LLNL's archives for LRL "Stretch" program write-ups.
5. **LANL Research Library / OSTI.** LAMS-2607 (IVY), LADC-5173 (COLASL), the STRETCH SIN and STRETCH BKW internal
   reports (GMX-2-R-63-1 and the 1962 report LA-3704 cites), and the 2DE 7030 report (already on OSTI, 4454572). The 2DE
   report prints a calling sequence and card formats but no listing (WEB); the SIN and BKW reports are unread.
6. **UK National Archives, Kew**: ES 10/803 (S1 spec), ES 4/995 (S2/S3 manual), ES 10/1020 (users' conference, Feb 1963,
   likely the best single list of what each site was running). AWE's own archive for S1/S2 listings (REPO, delegated).
7. **IBM Corporate Archives**: name C22-6718, the FORTRAN and SMAC Analysis Guides, the "Specifications Notebook (for
   Programs)" of Dept. 271, and the STRAP II and FORTRAN program listings (REPO; C22-6718 added here).
8. **NARA RG 457 and fpgacpu.ca/harvest** for HOPS-era material; the Harvest MCP was implemented by IBM under CLAGHORN,
   so NSA records may hold an MCP or HAP listing that IBM's do not (Snyder, WEB; inference mine).
9. **GFDL / NOAA** for the Stretch-era general circulation model code and its machine-language or FORTRAN form (SEARCH).
10. **SHARE and the Stretch users' group** distributions for STRAP-1 and the 7030 Simulator on the 7090 (UNVERIFIED that
    SHARE carried them); if a 7090 tape of either survives, it runs today on existing 7090 emulators.

### (c) What would have to be synthesized, and from what

| piece | primary sources to build from | status of those sources |
|---|---|---|
| STRAP II (in progress) | C22-6729, C28-6129 + N28-1081, the three printed fragments, the MCP listing as its output | REPO, held |
| SMAC I (done), its library tape and update program | J28-6128 + errata; C22-6728-1 pp.239-242 | REPO, held |
| SMAC II and the FORTRAN IV compiler | C22-6751; C22-6729 p.7 (phase chain); J22-6532 and J28-6127 (FORTRAN emits SMAC); DTIC decks and printed output as oracles; S2 and IVY manuals as period practice only | REPO; S2/IVY SEARCH |
| FORTRAN I/O and math library | C22-6751 Part II; C22-6578 §4.9-4.11; CHM 102633965, 102633957; the multiple-precision and noisy-mode notes | REPO, held (several unread) |
| BSS processor and segmentation | C28-6379-0; C22-6751 App. D; the loader in the listing | REPO |
| UPDATE 30, and with it the real PROSA layout | C22-6728-1 pp.228-250 (C22-6718 if found) | REPO |
| Restart | C22-6728-1 pp.102-106 | REPO |
| MCP listing p.329 | loader charts C22-6728 Figs 41-43; C28-6379 App. A | REPO |
| 1401 programs (SPI, SPO, Symbolic Update, Tape Labeling) | C22-6728-1 pp.224-227, 250-259; a host-side stand-in that writes the same tape formats is enough unless a 1401 is modelled | REPO |
| Missing diagnostics (JB AV1C first) | only their write-ups in the Aug 1961 index; better found than written | REPO |
| 704/709 Simulators | nothing but a paragraph; find-only | REPO-OCR |
| Site software (IVY, COLASL, S1/S2, Livermore FORTRAN, SOS, LISP 1.5) | manuals at best; never a substitute for IBM's pieces. A workload such as 2DE could be re-coded from OSTI 4454572 if it gives enough detail, labelled as a reconstruction | WEB / SEARCH as above |

## 5. Things I looked for and did not find

- **Journal literature (IBM Systems Journal, AFIPS/JCC, CACM).** One search, no published paper on MCP, STRAP II or 7030
  FORTRAN surfaced; only the CHM and bitsavers documents came back. The ACM DL, IEEE Xplore and the IBM journal archives
  were **not searched directly**. This part of the brief is not covered.
- **SHARE.** One search, no record of a SHARE distribution of STRAP-1 or the 7030 Simulator. Paul Pierce's SHARE tape
  collection (`piercefuller.com/library/share.html`) and bitsavers' SHARE material came up as places to look; not opened.
- **IBM program catalogs (WEB, text-layer grep).** `C20-8090` "Catalog of Programs for IBM Data Processing Systems, KWIC
  Index", April 1962 (319 pp) and `C20-1604-0` "704-7094 Program Catalog", June 1964 (100 pp), both from bitsavers
  `pdf/ibm/pgmCatalog/`: **no entry containing "7030" or "STRETCH", and no STRAP assembler** (the STRAP hits are an
  unrelated 650 assembler and a 1620 regression program). So IBM did not list 7030 programs, STRAP-1 or the 7030
  Simulator in its general program library in those two editions. OCR-quality text; a miss is not proof.

- No machine-readable 7030 software of any kind, in any source opened.
- No *Computer Journal* paper on S1/S2 (three searches).
- No document naming an IBM sort, merge or report generator for the 7030.
- No source supporting the Wikipedia sentence on SOS.
- No Weather Bureau or Livermore program listing.
