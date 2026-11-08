# Reconstruction plan: every IBM piece, what the documents allow, and in what order

Written 2026-11-07, in answer to the owner's question: "have you done an
audit of all of the available documentation we have? have you made it
into a plan about how to reconstruct as much as we know?"

Before this file, no such audit existed. `source_audit.md` audits four
documents in depth. `archival_inventory.md` records what has been
searched for and fetched. Neither one walks the whole corpus asking
"what can be rebuilt from this, and how faithfully?".

This file does. It sits under the owner's fidelity rule
(`programming_environment.md`):
1. find IBM's piece;
2. if it is lost, reconstruct IBM's piece from IBM's documentation,
   labelled RECONSTRUCTION, with its sources;
3. project tools are scaffolding only.

## 0. How the audit was made, and how far to trust it

The corpus is **195 PDFs**:
- 53 in `docs/`;
- 130 in `docs/chm/` (122 catalogued items plus 8 other-folder copies,
  §6);
- 9 in `docs/dtic/`;
- 3 elsewhere.

Four read-only auditors each took one slice and reported depth, coverage
and gaps per document:
- A: MCP and its parts;
- B: languages;
- C: hardware, CE and diagnostic manuals;
- D: the CHM engineering scans.

Their reports are model output, so they carry no authority of their own.
The claims the plan's decisions rest on were re-read in the ink before
being written here (the table below). The other page references come
from the auditors' image reads, or are marked OCR only. Each is
re-checked in the ink when the step that uses it starts. Claims
checked in the ink for this plan:

| claim | page read |
|---|---|
| R23-9732 §3.11 is the SAU's trigger-level flow diagrams, with an ALD page in every box | PDF 256, Fig. 3.11.2 "VFL ADD 1 TO MEMORY", dated 1/1/63 |
| §3.11 has never been used | grep of the repo. The only hit is a generic "CE 3.11.x" in `microarchitecture_plan.md` l.88. The `NEXT.md` hits are `exchange_and_io.md` §3.11, a different document |
| a page of STRAP II's own code survives | CHM 102633945: 33 statements of the DR/DRZ size computation, locations 000246.40-000277.40, `ZI...($3)`/`ZO...($5)` unit fields. **Transcribed 2026-11-07** (`decks/strap2_chm102633945.strap`, `tests/verify_strap2_chm102633945.py`, 40 checks, all agree with the scaffold) |
| look-ahead forwarding "is removed from K-2 and subsequent machines" | CHM 102634374 p.2 (Chen to Campbell, 28 Aug 1961) |
| a per-instruction table of I-box, look-ahead, LAAR, SAU and PAU use exists | CHM 102633951 p.1 (T.C.C., Oct 1960) |
| MCP, STRAP II, FORTRAN and SMAC I each had an Analysis Guide ("one of a set of four") | C22-6728-1 printed p.7 |
| C22-6729 App. C is an expression *encoding*, not a grammar | C22-6729 printed p.198. `source_audit.md` is corrected |
| the seven "multiprogramming memos" first filed were the wrong documents | first pages of both folders' copies (§6) |
| C22-6678-1 printed p.48 is genuine STRAP II output (VERSION 03/15/64) for a problem program, and p.47 is a SMAC source program | both pages at 110-220 dpi; p.48 transcribed with its code column |
| C22-6678-1 App. A, printed p.42, lists 77 MCP pseudo-op codes | the page at 100 dpi |

Depth key: **L** listing with machine code; **I** internals (data flow,
sequencing, tables); **S** programmer-visible spec; **M** mention.

## 1. Where the documents fork

**The owner's rule, 2026-11-07: "we should do everything and preserve
every option, the goal is to capture history."** So a fork in the
record is never settled by discarding a branch. Each historical variant
stays buildable and selectable, and is labelled with its source.

**D-1. Which 7030?** Chen's 1961 memos, read in the ink, split the
machines:
- **X-1 (LASL) and K-1 (LRL):** look-ahead data forwarding; no
  multiplier register $MR, so no LMR, STM or `*+`; a branch on an
  arithmetic result is guessed "probably unsuccessful".
- **K-2 and later:** no forwarding; $MR present (CHM 102634374 p.2,
  102634375); a different guess for arithmetic-result branches
  (102634376 p.7, read by auditor D).

The model today is a K-1 for $MR, and `boot_plan.md` records that as a
stated choice ("THE MODEL IS A K-1 FOR $MR"). Its branch guess,
not-taken, is also the X-1/K-1 rule. But the strongest
microarchitecture source in hand, the CE manual R23-9732 (Jan 1963),
documents $MR hardware: Fig. 3.3.15 "Load Multiplier Register" and
timing charts 3.8.12/3.8.14 (OCR captions). So the cycle-level
documentation describes a K-2-class machine.

**Both machines are kept, as build options.** One option is X-1/K-1:
forwarding, no $MR, and the "probably unsuccessful" guess. The other
is K-2 and later: no forwarding, $MR (LMR, STM, `*+`), and the K-2
guess. Each difference is a named switch, cited to Chen's page. The
model today is the X-1/K-1 setting of all three. The K-2 setting is
added when the E-box rewrite reaches the PAU's multiply path and the
look-ahead's forwarding logic, using R23-9732's $MR flows. MCP runs on
both kinds: it probes for STM, and C22-6728-1 printed p.277 says why.

**A third variant is named, not documented: the "Development
Improvement Package" (DIP).** Eric Smith's Stretch page (Wayback,
2025-08-25) says it was "primarily an overhaul of lookahead to improve
performance", installed midway through the program, and that "the
manuals were never updated to include DIP". Chen's K-2 changes may be
the same thing. Look for it in the 7101 logic volumes (§5 item 7). Kept
as a named option until documented.

**The same rule applies to the software's two dates.** The listing is
the March 1963 MCP. C22-6678-1 (June 1964) describes a later one, and
its STRAP II example prints "VERSION 03/15/64". Where the two differ,
both are kept: for example, `strap/opcodes.py` holds the 1963 listing's
pseudo-op codes and Appendix A's 1964 codes as two tables.

**D-2. FORTRAN's calling sequence.** C22-6751 printed p.31 gives
`SIC,$X15; B,name` with `VF` argument words. That manual's own App. C
example, and AD0642331 pp.58-59 (OCR only), give `LVI,$15,$+1; B,name`.
Both are read in the ink before any library routine is written (§3,
F-3). If both are genuine, both are supported. The two forms leave the
same return address in $X15.

## 2. Hardware: the cycle-accurate 7030

The order follows the mandated E-box rewrite (`AGENTS.md`;
`microarchitecture_plan.md` §1c) and the goal set G1-G5
(`source_audit.md`).

| unit | sources (depth) | achievable | unmined, by value | oracle |
|---|---|---|---|---|
| **SAU** (serial/VFL unit) | R23-9732 §3.11 SAU flow diagrams, PDF 255-268 (I); Perf Char Vol2 VFL atlas, printed pp.110-186 (measured) | **flow-level, trigger by trigger.** Per-cycle counts wait on G1.0 (the A/B clock relation) | **all of §3.11.** Nobody has used it. It is the only structural source for `mkSAU` | Vol2 VFL timings; the VFL decks |
| **PAU** (parallel/FP unit) | R23-9732 §3.3 flows, Figs 3.3.1-3.3.24, PDF 120-147 (I); §3.8 timing charts (I); jb_af1c (L) | flow level | §3.3's figures: zero citations so far, and they pair one-to-one with §3.8's charts. §3.8: 10 of 19 charts unread (G5 item 4) | af1c `fp_*`/`pau_*` decks (116); Vol2 FP timings |
| **I-box and look-ahead** | TR00.722 (I); R23-9732 §3.1 (28 figs) and §3.2 (I); Buchholz ch.15; Perf Vol1 Table A-2; CHM 102633948/950/951 (I, Chen 1960); 102632589, 102635128 (I, 1958 design) | structure complete: 13 named LA timers, the stage split | §3.1 Figs 3.1.6-3.1.28 (sequencers; OCR captions); **102633951's table is the spec for the stage split**; 102633950's register list (W, GLAR, the LA level fields and tag bits) | Vol2 atlas; Vol2 printed p.97 environmental test (§4) |
| **memory and BSM** | Perf Char; Buchholz §14.1; R23-9732 §4 Procedure 1 (select pulse 200 ns, 150 ns after SP); Cocke-Kolsky printed p.82 (bus priority: high-speed exchange, basic exchange, virtual memory, IAU) | ordering and phases | ja_bm6a, ja_bb6b, ja_bp6a: untranscribed (§5) | bm6a's own "O.K." printout |
| **interrupts and indicators** | RefMan; jb_ax5b (L); R23-9732 §3.7 error tables, PDF 205-224 (OCR captions) | full | §3.7: indicator-setting conditions for MK, IDC, OP, AD, ZDS, ZDF | the ax5b decks (36) |
| **exchange, 7503 reader/punch** | RefMan ch.12; R23-9702 (I); CHM 102632512/531 (memos behind IO_OP and the zero-count rule) | full for the 7503 | cite 102632531 at `StretchCore.bsv` l.670-676 | ka_ex1/ka_ex1b (BX-0), untranscribed: they need a device-level harness, not a CPU stream |
| **1403 printer, 7152 console** | R23-9695 ch.7 (S): console codes, binary switches, 1403 carriage codes | spec level | **ch.7: never cited.** It is the only source for these encodings | MCP's console text (`check_console_text.py`) |
| **729 tape, 353 disk** | A22-6552-1, D22-6513 (M); RefMan; ja_uc1a, ka_ul1 (L) | behavioural only: no CE manual for either is held | the 1958-59 memos (729 power-on parity and density; disk ECC on parallel faces), but check each against the RefMan first, since several are superseded (§6) | the IPL paths of ka_ul1 and ja_uc1a |
| **maintenance console** | R23-9713 (I/S); R23-9732 Table 3.4.1, §3.5 | panels and keys | R23-9713 §3 logic (p.14), §6 scanner (p.32), §8 error injection (p.38) | bb6b run with injection |

**Superseded designs to keep out of the model:**
- 102632541: a disk of 4M words at 3.5 µs;
- 102632587: the 1958 FP set;
- 102632559/560: "true zero";
- the 1957 "Delta" exchange;
- 102632583/102634001: the half-µs memory;
- Chen's 1961 redesign (102634376 §3 onward).

Auditor D's table lists them with their status codes. Design-era
timings (102635057 "Timing in Sigma", 1959; 102634064; 102634123) are a
**sanity band** for G1, never a target. The as-built figures come from
Perf Char and R23-9732.

## 3. Software: the 7030 programming environment

| piece | in hand | sources (depth) | achievable | gaps | first step | oracle |
|---|---|---|---|---|---|---|
| **M-1 MCP** (March 1963) | transcribed; boots; runs the command package | the listing (L); C22-6728 and -1 (I); C22-6678-1, N22-0085 (S) | **complete** except printed p.329 | **p.329** (LOADER TA000449-499, 235112.00-235153.40) | keep hunting a second copy. Else reconstruct p.329 from the loader charts (C22-6728 Figs 41-43) and C28-6379 App. A, labelled | the listing's own code columns; the loader card formats |
| **M-2 PROSA dictionary and index** | **RECONSTRUCTED** (`strap/prosa_dict.py`) | C22-6728 printed p.164; DISK FETCH code | done | the true order and alignment of UPDATE-30's output | (M-3) | P1 boot; `check_prosa_dict.py` |
| **M-3 UPDATE-30** (system build and librarian) | none | C22-6728-1 pp.228-250 (I; p.228 read in the ink: 2-file master tape, 513-word arc records); the HED cards DEL/REP/ADD/LIB, library areas LFORTRAN/LPASSONE/LPASSTWO/LSMACONE, origin 12400₈ (OCR only) | **most**, flowchart level | the code | write the spec from pp.228-250 in the ink; then make `prosa.py` *be* UPDATE-30's output format, and finally a 7030 UPDATE-30 | the dictionary MCP reads; the master-tape layout `prosa.py` already passes |
| **M-4 Restart** (33RESTRT) | none | C22-6728-1 pp.102-106, Figs 52-55 (I); C22-6678-1 p.31 (S) | most | the code. It also documents a **later MCP** than the listing: YSICADD, YIPLREQ and YARPBRP occur nowhere in the March 1963 listing | transcribe Figs 52-55; write 33RESTRT against the listed MCP's symbols, saying where it assumes hooks the listing lacks | its messages and options (C22-6678-1) |
| **M-5 loader card classes** | the TA/TB code | C22-6678-1 p.13 (18 classes, in the ink); N22-0085 (14, OCR only); C28-6379 App. A | full | which list the March 1963 loader takes | list the column-1 codes TA decodes; diff against both | the listing |
| **L-1 BSS processor and segmentation** | none | C28-6379-0 pp.7-13, App. A (S); C22-6751 App. D | partial (external) | internals | find first: it travels with FORTRAN | DTIC decks |
| **S-1 STRAP II** | none; `strap_asm.py` is scaffolding | **C22-6729** (I, deep: passes, COMREC, unit and symbol formats p.190, cards p.187, errors pp.176-179, App. G deck); C28-6129 (S); **C22-6678-1 printed p.48 (L): a genuine STRAP II listing of a problem program, "VERSION 03/15/64", transcribed and checked (`decks/mcpref_example2.strap`)**; C22-6678-1 App. A printed p.42 (the MCP pseudo-op entries of STRAP II's system-symbol table) | **most**, behaviourally | the code; the BOPSER opcode-table contents; GETFLD's syntax-matrix cells (pp.83-84 give only the legends); absolute card formats (C28-6129 pp.22-23) | CHM 102633945 transcribed and checked (2026-11-07). Then a STRAP II in C22-6729's phase structure (Pass 1, UITER, 2a, iteration, 2b), first host-side, then as a 7030 program under MCP | the MCP listing's code columns (they are STRAP II's output); 102633945; the error numbers |
| **S-2 SMAC I** (macro language) | none | **J28-6128, "SMAC Language Processor" bulletin, June 1961, 14 pp (CHM 102634360; held 2026-11-07, see `chm/README.md`)**. It is a full functional description: the statement and card format; the one-pass processor (shell, branch table, subroutines, generators); generators as logic plus skeletons; all 13 Generator Language operations (MBGEN, MEXIT, MBSKL, MEGEN, MMVPT, MOUT, MGETL, MKPEQ, MKPNEQ, MKCEQ, MKCNEQ, MOUTF, MOUTV) with worked examples; skeleton syntax `/n/`, `/Q/`, `//`; index-register rules; branch-table entries. Its errata: CHM 102634361, which renames MKPEQ to MKPEQI and the others likewise. Also: the MCP macros and their expansions (C22-6678-1 p.14 and the pseudo-op pages); a real SMAC program (C22-6678-1 p.47); the generator libraries (C22-6728-1 pp.239-242) | **most: the language and the generator language are specified.** Missing: the code, the branch table's addresses, and the generator library's contents | the SMAC Analysis Guide | **DONE host-side, 2026-11-08:** `strap/smac.py` (RECONSTRUCTION; all 13 operations, both errata spellings, card blocks, inner macros) and `strap/smac_mcp.py` (all 77 Appendix A pseudo-ops as Generator Language generators; $SCR and $FETCH as printed on pp.20-21; transcription in `mcp_macros.md`). Host limit: STRAP statements in generator LOGIC need a 7030 and fail loud. **7030 version begun 2026-11-08** (`decks/smac7030_shell.strap`): shell, MBGEN, MEXIT, MOUTF, MOUTV and substitution run on the model; the rest is `smac_7030.md` steps 3-5 | both met: `check_smac_bulletin.py` (24 checks: every worked example, N = 3, 4, 0) `check_smac_mcpref_example1.py` (50: p.47 expanded, assembled, and its calling sequences equal to p.48's printed code), and `check_smac7030.py` (on the model: p.47's 84 cards equal `smac.py`'s) |
| **F-1 FORTRAN IV compiler** | none | C22-6751 (S + object ABI); C22-6729 p.7 (the chain FORTRAN → PH3 → PH2-1/2/3 → PH1 SMAC → STRAP II, under an LPC) | **outline** | every phase's internals; the generator libraries; the FORTRAN Analysis Guide (named on C22-6728-1 p.7, not held) | fix the object ABI (C22-6751 ch.13, App. A/C) and rule on D-2; then a translator that emits STRAP II source, as IBM's did | DTIC decks' printed output (AD0685715 App. III) |
| **F-2 FORTRAN I/O library** | none | C22-6751 Part II; MCP's IOCS (in the listing) | partial | internals | STRAP subprograms on MCP's I/O, with Program/CDC cards | DTIC outputs |
| **F-3 math library** | none | C22-6578 §4.9-4.11 (source); CHM 102633965 (its typescript ancestor); 102633957 (conventions) | partial | the library's names and argument checks | transcribe 4.9-4.11; wrap in the ABI after D-2 | AD0685715 numbers |
| **P-1 1401 programs** (Symbolic Update, Tape Labeling, SPI I/II, SPO) | none | C22-6728-1 pp.224-227, 250-259 (I); C22-6678-1 p.6 | partial to most | 1401 code | spec SPI I and SPO first: they define the system-input and print-output tape formats | tape formats MCP reads |
| **C-1 CONDEF** (pre-MCP console debugger) | none | CHM 102632570 (S, 32 pp); 102632571 (examples) | most, as a spec | code | later; it is pre-MCP | 102632571's examples |
| **X-1 704/709 simulators on the 7030; the 7030 simulator on the 709** | none | J22-6532 (M); C22-6531 p.38ff (S) | none / outline | everything | **find only**; do not reconstruct | — |

**What blocks a real first job (E4).** The DTIC decks show it. The
March 1963 MCP skips T cards: printed p.266, line 41, "CHECK FOR T
CARD". So `T SUBTYPE,FORTRAN` decks fit the front end as it stands.
What they need is FORTRAN IV and the BSS processor. A first job
therefore uses a STRAP II-shaped binary deck. Until S-1 runs, that deck
comes from the scaffolding assembler, labelled as such.

## 4. Unmined sections, ranked

Each item names its target and the step that consumes it.

1. **R23-9732 §3.11 SAU flow diagrams, PDF 255-268.** Target: `mkSAU`,
   the mandated E-box rewrite. Start with VFL add, Fig. 3.11.9 (OCR
   caption).
2. **CHM 102633951 / 102633950 / 102633948 (Chen, Oct 1960).** Target:
   the stage split, `microarchitecture_plan.md` §1c. Extract 102633951
   as a table in the plan.
3. **R23-9732 §3.3 PAU flows, PDF 120-147**, paired with §3.8.
   Target: `mkFBox`.
4. **CHM 102633945.** Target: S-1. DONE 2026-11-07: every printed row agrees with the scaffold; the page marks negative-offset statements "CV".
5. **Perf Char Vol2 printed p.97 (PDF 104), the floating-point
   environmental test.** It measures a subject op inside 1-8-deep
   backgrounds, which is direct overlap data. Method on pp.95-96.
   Target: G1. It is not in `perf_char_timing.py`.
6. **R23-9732 §3.1 Figs 3.1.6-3.1.28 and §3.2.** Target: I-box
   sequencers, G5 item 6.
7. **R23-9732 §2 check procedures, PDF 12-50.** The A/B clock-phase
   relation in nanoseconds may be here. G1.0 needs it before any cycle
   count.
8. **C22-6728-1 pp.228-250 (UPDATE-30)** → M-3; **pp.102-106 (Restart)**
   → M-4.
9. **R23-9732 §3.7 error tables, PDF 205-224.** Target: interrupts.
10. **R23-9695 ch.7.** Target: console and printer codes.
11. **ja_bm6a (11 pp), then ja_bb6b (20 pp).** Target: memory and
    ECC, as self-checking oracles.
12. **The 7030 Opcode List (99 pp), as an exhaustive encoding sweep.**
    A second oracle for every op in every mode, independent of the
    decks.
13. **R23-9713 §3, §6, §8.** Target: maintenance console, error
    injection.

## 5. Lost: what to find, in priority order

Each item carries where it was named; `archival_inventory.md` has the
search record.
1. **Printed p.329 of the MCP listing.** A second copy of the March
   1963 listing anywhere.
2. **The FORTRAN and SMAC I Programming Systems Analysis Guides**
   (C22-6728-1 p.7). (J28-6128, the SMAC Language Processor bulletin,
   is FOUND: CHM 102634360.)
3. **A STRAP II listing.** 102633945 proves one was printed.
4. **The FORTRAN IV compiler and BSS processor**, as listings or
   decks. Trails: NWL (the DTIC decks' site), AWRE
   (`thirdparty_software/`).
5. **Diagnostics named in the acceptance index but not held:** JB AV1C
   (VFL), KA BT1, KA AT1, JB AC1, JA AT1 "Basic Timing Test
   (Livermore)", KA SS1 SEVA. CHM 102634364 describes SEVA but is not
   the program.
6. **A CE manual for the 729 and the 353/7612.**
7. **Not scanned, but held by CHM**: request scans (`chm/README.md`,
   "Not scanned"). These include the **7101 logic-diagram volumes**
   (Lowell Wood collection), the 7612 logic volume, 27 diagnostic
   reference manuals, and the **November 1961 MCP Preliminary Reference
   Manual**.
8. **Named, not found**: C22-6719 "7030 Timing Guide" (1962);
   A22-6530-1 (the 1960 Reference Manual).
9. **Non-IBM 7030 software, to find, never to stand in for IBM's**:
   AWRE's FORTRAN S1/S2/S3 (Glennie; S2 had the first dynamic arrays);
   Livermore's own FORTRAN and operating system (Norman Hardy's STIPIC,
   per the Harry Nelson interview); Purdue's FORTRAN IV (1965); TREET
   (NBS, 1967); HOPS and ALPHA on Harvest.

## 6. Corrections made by this audit

- **CHM: one catalog ID can name different documents in different
  box-folders.** Eight fetched IDs were the wrong documents. The
  catalogued copies are now filed under the ID; the others are kept as
  `<id>_<folder>.pdf`. `chm/README.md` "One catalog ID, two folders"
  has the list. The real multiprogramming memos (1957-60) are now held,
  among them Codd's **TR 00.716 "Multiprogram Scheduling"** (28 pp, new
  to the repo) and TR 00.719. The 1955-56 papers that had been filed
  under their IDs are Stretch-origin history (Dunwell's AEC proposal,
  Carlson's LASL T-1-101 and others), kept.
- `source_audit.md`: the "COMPLETE FORMAL GRAMMAR" heading is corrected
  to an encoding (§0).
- Numbers come from the ink, not the OCR. The master-tape record is 513
  words (C22-6728-1 p.228); the OCR reads 518. The repo already uses
  513.
- Catalog dates are unreliable. 102633933 is dated July 1959 on its
  pages, though catalogued 1957 (OCR only). 102633975 is Nov 1957.
  102634120/121/123 are 1959-60 school handouts, not 1965.

## 7. The order of work

**The owner's order, 2026-11-07:** "use that to implement a best effort
reimplementation of the translation and a best effort strap ii. Once we
have both of those implement fortran on top of that." So the language
chain leads: SMAC I and STRAP II, then FORTRAN IV on top of both, as
IBM built it (C22-6729 p.7: FORTRAN → SMAC II → SMAC I → STRAP II).
Everything else in this plan is still done; "do everything". The
hardware track (the mandated E-box rewrite) and MCP's `//////` loop
continue alongside. The host-side language work does not wait for
them, but running the processors **under MCP** (E2-E4) does.

1. **Oracles.** C22-6678-1 p.48 (done: `verify_mcpref_example2_listing.py`).
   Then CHM 102633945 (done: `verify_strap2_chm102633945.py`), then a printed-format spec of the STRAP II
   listing from p.48 and C28-6129 pp.18-23.
2. **How the chain is wired under MCP.** MCP's TYPE/COMPILGO code
   (printed p.266 and around it) names the processors it fetches. That
   fixes their PROSA type-area names and entry convention. C22-6729
   p.180, the coprocessor hook, and p.7, the request chain, say how
   SMAC hands text to STRAP II.
3. **S-2 SMAC I.** Host-side DONE 2026-11-08: the processor and the MCP
   macro library, both in J28-6128's own Generator Language (no
   reconstructed definition language is needed: the bulletin specifies
   it). Remaining: the library tape and update program (format not in
   J28-6128; CHOSEN C1 in `strap/smac.py`), STRAP statements in
   generator logic (needs the 7030-hosted SMAC), and SMAC as a 7030
   program, after STRAP II.
4. **S-1 STRAP II**, phase by phase from C22-6729: Pass 1, UITER, 2a,
   iteration, 2b, with COMREC, unit and symbol formats, cards, errors
   and listing. It is written host-side first, as an executable
   specification, and is NOT `strap_asm.py` restructured, which stays
   scaffolding. Then it is written as a 7030 program assembled by the
   host-side one. Completeness is checked by self-hosting: the 7030
   STRAP II assembles its own source to the same bits.
5. **F-1..F-3 FORTRAN IV** on top: its phases (PH3 syntax, PH2-1..3
   data glean, expansion and indexing, which is SMAC II) emitting SMAC
   I, through STRAP II, to the BSS loader.
6. Alongside: E1's `//////` loop and E2-E5; SAU from §3.11 (extract
   102633951 into `microarchitecture_plan.md` §1c first); the UPDATE-30
   spec (M-3); PAU §3.3 with §3.8; bm6a and bb6b; §3.1/§3.2; M-4
   Restart; M-5 loader classes; P-1 1401 formats.

Each step follows AGENTS.md: a page read in the ink behind every
format, a test with a measured injection, the suite green, one
milestone per commit.
