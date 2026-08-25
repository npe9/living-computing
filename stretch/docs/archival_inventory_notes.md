# Archival inventory notes (raw agent reports, pre-synthesis)

Working scratch for the "enumerate diag/ce/mcp" pass. Will be folded into
a proper docs/archival_inventory.md (or README updates) once all reports
are in. Not yet committed to git.

## Download gotcha (found by agent 1)
bitsavers.org 403s a bare `curl -sL <url>` (blocks default curl UA).
Fix: `curl -sL -A "Mozilla/5.0" -e "http://bitsavers.org/" <url>`.

---
## 1. MCP Loader manual (C28-6379-0, mcp/) -- COMPLETE

Source: http://bitsavers.org/pdf/ibm/7030/mcp/C28-6379-0_MCP_Loader.pdf
Real title: "Loader and BSS Processor" (7030-27). ~half the doc is the
FORTRAN Binary/Symbolic Subroutine (BSS) processor, not the loader itself.

Verdict: NOT a loader listing. Zero STRAP source for the MCP loader's own
internals -- behavior given only as prose, per-card-class. What IS fully
specified: 18 binary-card class formats (Appendix A pp.18-21, column-by-
column), 5 internal table layouts (Figs 1-5,7), diagnostic message strings
(Appendix B pp.22-23). Enough to write a functionally-compatible
reimplementation of deck parsing/relocation, not to recover IBM's actual
loader code. Missing MCP-side interface (disk I/O, IOCS, $MCP/$RESLD
semantics) -- push to C22-6678 MCP Reference Manual next.

BONUS for STRAP assembler project: pp.15-16 have genuine compact STRAP
source examples (PUNREL, PUNNOR, ORIGIN, SYN, SLC, SEM, PUNFPC, ENTER,
DRZ, DR, XW, END; system symbols $MCP, $SPR, $ABEOJ, $ABSUB, $RESLD) --
small enough to use as a hand-checkable syntax test corpus.

Named routines/entry points: $RESLD (resume load), $MCP, MCP loader
(subroutine of $RESLD, pp.4-6), BSS processor (pp.7-13), Link program
(segmentation supervisor, pp.13-14), MCP dump routine, FIOD subprogram,
*MAIN* entry point.

Real source-level pages: p.4 (card class dispatch table), p.7 (deck
grammar), p.8/p.10/p.12 (table bit-layouts), pp.15-16 (STRAP examples,
HIGHEST VALUE), p.17 (worked storage map), pp.18-21 (Appendix A, full
wire format -- single most implementation-ready section), pp.22-23
(Appendix B, diagnostics).

## 2. STRAP II System Analysis Guide (C22-6729, top-level) -- COMPLETE

Source: http://bitsavers.org/pdf/ibm/7030/C22-6729_7030_STRAP_II_Sys_Analysis_Guide.pdf
211 pages, ~135 sampled directly, remaining ~76 pages are individual
subroutine write-ups following an identical template, already enumerated
by index tables on pp.63-64/138 (names/purposes/pages known even where
full text wasn't read).

Verdict: BEST document found so far. Sufficient to reconstruct STRAP II's
LOGIC AND DATA STRUCTURES as a specification/pseudocode source -- NOT
verbatim transcribable STRAP source. ~50 routines each fully documented:
exact calling sequence/register conventions, full restrictions, complete
bit-layout of every buffer/table touched, box-by-box flow-chart detailed
enough to read as structured pseudocode. Appendices give complete
bit-level formats for every internal data structure (expanded instruction
unit, symbol table, coded-expression encoding, all relocatable binary
card formats) + full 148-entry error-message catalog. pp.111-113 even
derive the division algorithm (Newton-Raphson reciprocal expansion) used
by DD precision arithmetic -- real algorithmic depth, not just prose.

Preface says verbatim STRAP-mnemonic source for STRAP II itself lives in
a SEPARATE document: "STRAP II Assembly Listing" (Form C28-6129).
NOTE: bitsavers's own listing labels C28-6129 as "STRAP-II Reference
Manual, including updates, Apr63" -- need to check when fetched whether
it's actually the assembly listing the SAG's preface refers to, or the
user-facing language reference manual (a different document that may
share/reuse the form number across revisions). Flagged, not yet resolved.

Named routines (major, ~50 total, full list in report): MAIN (Pass1
driver), NPS2 (Pass2 driver), ERRIN/ERR/ERRNUM/ERRPRT (error handling),
MOVE, TABMAN family (SEARCH/ADDORD/ADDUNO/ANEXT/RSERCH), VALUE (+VSKIP/
VDIMEN/VMOVE, expression eval), XERR (disk retry), BOPSER (op-table
binary search), CCA8, CPLTNM, CPLTSY, GETCHA, GETFLD, GNLOAD, INTOUT,
MBSPEC, MIBA, MIOD, MQDD family (DD statement processing incl. DNUM,
MQDDPA/MQ1/MQ2/MQ3/MQLL4/MQDDPP precision arithmetic), MQP, MQR, MDIMRF/
MDIMRT, MQS (SYN), MQTAIL/MQT (TAIL/UNTAIL), MULTI, MX (EXTract), XINIT,
XINPUT, UITER, DECODE, INTIN, INSERT (~18 sub-forms), NEXT, NMCP, OUTPUT
(8-chart flow), NAMEIN, OPPUN, OEDIT, OPLIST, NPNSYM/NQBTP, NUNDSY,
MACHER (post-mortem dump handler).

Real source/algorithm pages: 12-19+28-36 (full Pass1/Pass2 box-by-box
flowcharts w/ real internal register names), 37-62 (Common-section
subroutines, bit-layout figs 3-11), 63-137 (Pass1 subroutines incl.
division-algorithm derivation pp.111-113), 138-172 (Pass2 subroutines),
173-179 (148-entry error catalog + index-register assignment table +
STRAP II's own disk overlay map), 180-182 (external coprocessor I/O
protocol), 183-188 (ONE COMPLETE WORKED STRAP II SOURCE EXAMPLE + 6
relocatable card format specs), 189-194 (Appendix A: bit diagrams of
every internal data structure), 195-196 (Appendix B: full mnemonic
reference), 197-201 (Appendix C: complete coded-expression bit spec w/
2 worked examples), 202/208-209 (naming conventions, boot-deck map).

Next step recommended by agent: fetch C28-6129 to cross-check/transcribe
real STRAP mnemonics against the algorithms already extracted here.

## 3. MCP System Analysis Guide (C22-6728-1, mcp/) -- COMPLETE

Source: http://bitsavers.org/pdf/ibm/7030/mcp/C22-6728-1_7030_MCP_Sys_Analysis_Guide.pdf
280 pages, scanned (no text layer), ~110 pages sampled: front matter/TOC,
full Interrupt Control (12-46), Job Control (47-70,95-101), System I/O
intro (123-126), Actuator I/O (181-192), Commentator/Debugging (210-224),
Appendix A I/O tables (260-268).

Verdict: Preface states outright it "complement[s] the MCP program
listing" -- it is EXPLICITLY a companion to a separate MCP STRAP source
listing, NOT the listing itself (confirms/refines the earlier informal
"large parts of source-level structure recoverable" read -- it's really
architecture+symbol-map recoverable, not source). Excellent for
reconstructing MCP's ARCHITECTURE AND CONTROL-FLOW LOGIC: complete
interrupt-dispatch mechanism (SIT/SIPT, PTOE format, maskable-interrupt
routine, receptor state machine, IF analyzer/identifier calling
convention, 4-buffer low-register-save logic, 36-entry error-code table),
job-control state machine (JC1/JC4, decode/assign/move, 3 I-O assignment
tables fully bit-mapped), I/O control table layouts at the bit level
(Appendix A: Channel Status Table, Unit Status Table, Unit Area Table).
Missing: full STRAP instruction bodies for almost every routine --
flowcharts describe WHAT in English boxes, not HOW in STRAP mnemonics.
Real STRAP snippets are calling-sequence/linkage only (pp.12-13,15,50,
53-55,66,191), not routine bodies.

Named routines (very large set, full detail in report), organized by
subsystem:
- Interrupt Control (pp.12-46): YFX**/YMFIC/YSFIC/YMFL/YMFP/YPREL/
  YPREFX/YAXTYP/SFPTE/YMSF/WLODE/JWLODE/WCONA/WRAMPP/KSTORE/KUNSTC/
  KQIN/KGATE/KSIGNL/KSINGL/KOOOL/KCSIN/KMTCSQ/SFAKE1/KNORM/KHEX/
  KSERCH/KPACK/KCLUB/KRELAY+bookkeeping labels/KSUPP family/CWAIT/
  CMINTD/PCONE1/PCONE2/PCSRD/receptor chart-4 mount labels/RVFCSG etc/
  SIFAE/SIFAD/MTC1/MTC2A/MIFTTT/KFRONT/KNOGO/KOPOK/KKNI/CRETN/CRETPP/
  CRETBU/MUP1/SDISP/SDSPDS (36-entry error table pp.42-43)/SPRIME/
  SPRIMR/MPR7/MPRMQK
- Job Control (pp.47-70): SCR1/SCAN/SEJSCN/SONL/SOFFL/SBYP/SEOF/SREW/
  SJC1/$EOJ/$ABEOJ/SJC4/$RESLD/SLOG1-4/YC11ST/YC1A/YC1A1/YC1SCN/SKOM/
  YUNCOD/SCOMD/LDECOD/YC4NO/SSCR4/$SCR/SSPEOJ/$SPU/$DUMP/$FETCH/$COMM/
  $TIME/ZSPLPR/SPRIME/$RET/YMPFCH/SA6IQS/SBRK8/TASIGN/TMOVE/TJUNAS/YPR/
  YRDFSO/SCA6/YC4B2/WJ4PA/WJ4PF/WJ4PFF/YCOJB/YC4INT/WJC4Q/YLASTC/
  WREJJB/YRESTR + PP Reference Table / I-O Request Table / First Reel
  Number Table / current-reel-on-drive table field names (p.68-69)
- Actuator I/O (pp.181-200): ZSTART/EWR1/EWR31/EWR18/ZDISK1/ZSTEVL/
  SEVLMK/SEVLTB/BCWCR/KKLOC/KGLOC/KMOON/KFINI/KDISK/KSEOPT/WREL/WFC/
  EELG/ZUNLDB/SBDTA/SBCDP/SBUNLD/SBSCRT/SCBMNR/ZREWST/BKLNR/BRLNR/
  BRLFR/BTIFR/WGONG/SCABLT/MIOREJ
- Commentator (pp.210-214): JCOMM/SCOMM/JJOIN/JSTKR/JDWTST/JSTCW/JIOGO/
  MSETIO/JTERM/JRECLN/MSTACK/MTABLE/MCHECK/MFIXUP/JEXITD/JSTEX/ZTIME/
  JSITX/KFECRG/KSTRG
- Debugging Aids (pp.215-224): RAEDUMP/AWDUMP/APUMP1-8/PHOLD/PHOLDB/
  PDBO/PDBBEG/PE1-4/PSTR/PSC/PA1/PEBK/PH/PDKL/PDUM/PMES/YABEX/TFCHLR/
  TSTLR/FFXP
- IPL/Restart (pp.95-101): XIPLBS/XBSEND/X9A/X11/X13/SUCAR/SUSAN/X131/
  X19/X184/SB22/X37/X378/XMODE1
- System I/O (pp.123-126): VBF1/VBF4/VTSA/VTSB/VONLIB/VOFFLB/VBYPAN/
  VOFFLN/VBYPAF/VONLIN + CR/SC/WT/RT/ST/Q/E functional symbols

Real source-level pages: 12-13/15 (YFX**/PTOE STRAP skeletons, generic
templates not per-instance bodies), 33-34 (IF analyzer/identifier
entry/exit symbol tables), 37 (concrete numeric offsets), 50 (Table 4,
real STRAP calling sequences for SKOM family), 53-55 (Tables 5-7,
DENSEST real STRAP linkage code in the doc -- JC4 package/service-op/
subroutine calling conventions), 66 (uncode linkage w/ full param
layout), 191 (EMK1A/EWR18/RVFY -- actual status-eval mask/branch
fragment), 260-268 (Appendix A bit-field layouts of I/O control tables).

Recommendation from agent: locate the actual "MCP program listing" the
Preface refers to as a companion document -- separate from this Analysis
Guide -- worth a dedicated follow-up search on bitsavers/elsewhere.

## 4. Diagnostic Control Program manual (ka_ua1, diag/) -- COMPLETE **BIGGEST FIND**

Source: http://bitsavers.org/pdf/ibm/7030/diag/ka_ua1_diagnostic_ctl_pgm.pdf
154 pages, ~130 sampled. Bundles TWO documents: pp.1-18 operator/procedure
manual (prose), pp.19-152 (!) is a COMPLETE, CONTINUOUS STRAP ASSEMBLY
SOURCE LISTING of the DCP itself -- single control section F1
("PRINID KA UA1 DIAGNOSTIC CONTROL PROGRAM FOR 7030/7950 EDP SYSTEM BY
J.C. HANNIGAN"), octal 004000-016500, terminated `END,F1` on p.152.

**This is the biggest find of the pass: real, complete, unbroken STRAP
source code, not description of source code.** Every page 19-152 is a
full fanfold-printout scan: STRAP mnemonics (SIC, B, BB, BBZ, RXH, LX,
SX, LVI, SVA, DR%BU, DD%BU, XW, CNOP, SYN...), octal source-address
column, AND machine-code-encoding column (op/tag/index bytes) -- a
genuine assembler listing. No OCR text layer (scan only) -- needs manual/
OCR transcription, but font quality good, STRAP punctuation (%,&,@,$)
distinguishable, octal digits clean.

Verdict: combined with the STRAP assembler already built in this repo,
likely SUFFICIENT TO REASSEMBLE A WORKING, BIT-FAITHFUL COPY OF THE DCP
-- not just document its behavior. Every major subsystem present in
source form: mode/IPL selection, card-deck-format parsing, schedule-table
maintenance, per-test checksum gen/verify, tape read/write/retry, all
print/dump/compare/panel-dump utilities, and the Utility section (J1/J2)
that BUILDS AND MAINTAINS THE MASTER DIAGNOSTIC-LIBRARY TAPE from
individual test decks -- i.e. exactly the "how are individual tests
loaded and sequenced" mechanism, in full.

Caveats: (1) individual test programs (ibox/FP/memory-pattern/etc.) are
NOT embedded here -- called by ID against schedule table, must be
recovered from their own separate diag/ PDFs; (2) no I/O environment --
DCP assumes tape drives/card reader/printer/typewriter console and
%SEOP channel-command primitives; a Bluespec model would need these
device semantics emulated for the DCP to actually RUN, not just
assemble; (3) nothing transcribed yet -- scan only, ~130 pages of source
needed, large but tractable (one continuous listing, not scattered
fragments); (4) pp.1-18 procedural front matter, low reconstruction
value but short, worth reading for control-card semantics.

Named control sections/routines (very large set -- see full report for
complete table): F1 (top-level), EDCP1-6 (restart entries), ECTL1-4,
EQAV1-12 (equipment tables), EEIPL/EEA/EEB/EEBS/EEBF/EEC/EED/EEDR/EETERM,
ELUP1/3/F, EHLTC/EHLTF/ESSW/EMIR/ECHECK, EPNC/EPCD/EPBW/EPOH/EPRC (print
entries), ESSS/ESMI/ETINT, F1A-F1A7 (initial setup, mode checks), F1B
family (card-reader entry, card-type decode), F1C/D/E, F5A-C, F6T
(master interrupt table)/F6A-F, G1A-L (sense-switch ctl), G2A-D (common
halt), G3A-C (manual intervention), G4/G4A-F/G4AA-AL (error-halt/print),
**G5A-C/G5BR*/G5BM*/G5BS6 (complete Memory Compare routine, pp.92-93)**,
G6A/B, H1A-A7/H1B family/H1V* (print/typewriter/line-printer, incl. full
octal-BCD char conversion table), H2A/B, H3A/B (binary-word), H4A/B
(octal-hex dump), H5A (register-compare), H6A (print headings),
**H7A-AI (complete Panel Dump routine, pp.125-129 -- dumps LC, INT ADD
REG, UB, LB, BCB, MAINT BITS, CHAN ADD, AOC, LZC, LH/RH ACC, indicator/
mask/remainder/factor/transit regs -- near-complete map of 7030
programmer-visible state)**, H7B/C, **"STRETCH MAINTENANCE COMPOOL,
NOVEMBER 20 1961" (p.131 -- shared SYN table, the Rosetta stone linking
symbols across ALL 7030 diagnostic decks in bitsavers diag/, not just
this one)**, ACA-H/ADA-D/AIDNTA/B, **J1A1/J1A (Utility control routine)
and J2* family (pp.133-152, complete tape build/update/duplicate/
checksum machinery)**.

Real source pages: 19-152 CONTINUOUS (the whole listing). Prose only:
1-10 (manual sections 1-5), ~10-15 (Appendix A/B). Mixed: ~15-18
(Appendix C sample printouts + a hand-filled LC-SAP coding form example).

PRIORITIZATION NOTE from agent: this is the single most valuable
transcription target found in diag/ so far -- real STRAP code AND the
harness tying every other diagnostic test together.

## 5. System Test Programs overview (7030_SystemTestPrograms_Aug61, diag/) -- COMPLETE

Source: http://bitsavers.org/pdf/ibm/7030/diag/7030_SystemTestPrograms_Aug61.pdf
"Operating Procedures -- 7030 DPS (STRETCH) -- Systems Test Programs",
IBM CCC Kingston Diagnostic Engineering, Aug 25 1961, subtitle "STRETCH
SYSTEM CERTIFICATION". 46 pages, fully read. Scopes itself precisely: NOT
an index to the entire diag library, but to the ACCEPTANCE/CERTIFICATION
sequence an engineer runs on a freshly-installed machine, in run order.

Source-level listings: NONE. 100% prose + 2 flowcharts (CONTROL RECORD,
RETURN FROM PROGRAM). Confirmed intentional: doc states "Each program
deck has an associated program writeup and listing" -- i.e. actual STRAP
listings live in the SEPARATE per-program diag PDFs this doc indexes.

Index/roadmap (full table in report) -- 22 programs w/ maint-switch seq
#, program ID, equipment tested, writeup file#, notes, page:
0=JA AX1(I-Box1,unconditional branch/direct-imm index arith/SIC),
1=JA UA1(SSIP utility, load first, all others depend on it),
2=JB AX2(I-Box2, store-zero/compare), 3=JB AX3(I-Box3, index ld/st),
4=JB AX4(I-Box4, direct index arith/transmit/swap),
5=JB AX5(I-Box5, clock/timer/mask-indicator/interrupt/boundary/execute/
lookahead/addr-truncation), 6=JB AF1C(FP circuitry), 7=JB AV1C(VFL
circuitry), 8=KA BT1(mem timer), 9=KA AT1(raw speed), 10=JB AC1(I-Box
I-checker, parity), 11=JA BM6A(mem addressing), 12=JA BB6B(mem worst
pattern), 13=JA CE2(tape all channels), 14=JA EE3(BX/tape preliminary),
15=JA NE6(punch), 16=JA NE5(reader, consumes punch's deck), 17=JA NE4
(printer/BX), 18=JA ES1D(I/O single channel, op console), 19=JA CE1
(tape 0-6), +JA AT1(basic timer/Livermore, card-loaded only, runs under
STPPK), +KA SS1(SEVA, full arith cross-check, separate tape).
Plus infra (not on cert list): MNT TP1/JA UC1 (maintenance tape
dispatcher) and TP LD1/JA UD1 (tape load, builds maint tape from PUNFUL
decks) -- BOTH EXPLICITLY FLAGGED "Programs becoming obsolete" in their
own text.

KEY CROSS-CONFIRMATION: this agent independently predicted, from the
"becoming obsolete" flag on JA UC1/UD1 plus a KA-vs-JA/JB prefix pattern,
that ka_ua1_diagnostic_ctl_pgm and ka_ul1_load_and_tape_write_util are
the almost-certain SUCCESSORS to this obsolete loader/dispatcher infra --
which matches (confirms independently) agent 4's finding that
ka_ua1_diagnostic_ctl_pgm.pdf actually IS the DCP's full STRAP listing.

Other findings: revision-letter drift is systematic and predictable --
Program List names and bitsavers filenames agree with each other; each
writeup's own page header lags one revision letter behind (e.g. list
"JB AF1C"/writeup "JB AF1B"/bitsavers "jb_af1c"). Expect every individual
diag PDF to be one revision ahead of what this Aug-1961 index describes.
Two folio numbers (-16-, -21-) are missing from the scan in slots that
line up suspiciously well with ja_bp6a_memory_patterns_test and
ka_ex1/ka_ex1b_bx-0 -- unconfirmed hypothesis, worth checking directly.

Useful control-plane detail: maintenance-switch semantics (switches 0-31
select program by seq#, 32 bypass printout, 33-38 SSIP options incl.
stop-on-error/loop-and-print/loop-indefinitely, 37 loop/repeat, 63
continue/acknowledge); memory map (control/dispatch resides 64-192,
(8)100-(8)777 reserved for Tape Loader, all maint/test programs must run
above (8)1000); deck-format tags PUNFUL (normal)/PUNNOR/PUNID (special,
SEVA/Basic Timer).

Recommended inventory order (from agent): (1) ka_ua1_diagnostic_ctl_pgm
+ ka_ul1_load_and_tape_write_util [ka_ua1 already done as #4 above --
CONFIRMED the prediction]; (2) the 5 I-Box tests ja_ax1a..jb_ax5b [most
direct STRAP/Bluespec cross-validation value, enumerate specific
instruction classes]; (3) ja_ua1_ssip [foundational dependency]; (4)
ja_bp6a + ka_ex1/ka_ex1b [folio-gap check]; (5) jb_af1c_floating-point +
jb_av1c VFL test [Stretch's signature FP/VFL extensions].

## Post-hoc verification (advisor-directed, before synthesis)

1. C28-6129 identity RESOLVED: downloaded, read pp.1-6. It is "Reference
   Manual STRAP-II: 7030 Assembly Program" (c) 1961 IBM -- a LANGUAGE
   REFERENCE MANUAL for programmers writing STRAP-II source (input
   format, pseudo-ops, DD statement rules, address arithmetic, output
   listing format). NOT the "STRAP II Assembly Listing" the SAG's
   preface refers to as a separate document containing STRAP II's own
   source. That listing is NOT on bitsavers under this form number --
   say so plainly, don't recommend re-fetching it.

2. DCP source listing continuity VERIFIED across all 3 unsampled gaps
   the original agent skipped (pp.61-70, 121-124, 136-144 in its own
   page-range accounting): read PDF pages 59-72, 119-127, 134-146
   directly. Octal address column runs completely unbroken across all
   three ranges (e.g. 006650->007777->010000-ish continuous through
   gap 1; 014173->014632 continuous through gap 2, covering exactly the
   H6/H7 Panel Dump routines; 015062->015662 continuous through gap 3,
   covering the J2 tape-utility routines). No discontinuities, no
   missing folios, no scan gaps found anywhere checked. "Complete and
   unbroken" is now an earned claim, not an assumption from partial
   sampling.

