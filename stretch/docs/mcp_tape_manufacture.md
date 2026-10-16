# Manufacturing a bootable MCP tape: feasibility, cost, and the smallest real target

Survey pass, 2026-10-16. Everything below is from page images rendered
out of `docs/` in this session; none of these five PDFs has a text
layer (`pdftotext` returns one byte per page on all of them —
measured, see §7). Pages are cited as *printed page (PDF page)*
because the PDF→printed offset is **not constant** in either MCP
volume (§1.4).

---

## 0. Verdict, with the number

**Two different projects are hiding under one question, and they are
two orders of magnitude apart.**

| Target | Size | Rule-3 checkable? | At this project's demonstrated rate |
|---|---|---|---|
| **MCP IPL bootstrap** (printed pp.2–14) | 13 printed pages, **~550 source lines**, **~385 machine-code rows**, **369 words of object code** including its own IPL control word (§4.4) | **Yes**, binary column throughout | **~4 days** of transcription |
| **All of MCP** (printed pp.1–445) | **~23,700 source lines, ~19,000 machine-code rows** | Yes, on code pages | **~198 days ≈ 6.5 months** of transcription alone — before any model work |

Arithmetic for both is in §4.

**The headline finding is that the MCP listing carries a printed
machine-code column.** `AGENTS.md` rule 3 applies in full, and
`strap/listing_oracle.py` can be pointed at MCP tomorrow without
modification: the column prints in exactly the `oooooo.oo HH` shape
that `listing_oracle.fmt_half()` already emits. This is the strongest
verification posture the project has, not the weakest.

**The recommended target is the IPL bootstrap, not MCP.** It is a
complete, self-contained, 369-word program whose *entire job is to be
booted from tape*. It is the real IBM code that the real IPL button
really ran on a real 7030, and transcribing it is roughly the size of
one-and-a-quarter `ibox1_p43_p51_span.strap` (the largest existing
program in the corpus, 421 code lines). Booting it is a genuine "we
booted IBM systems software from tape" claim.

**`C28-6379-0_MCP_Loader.pdf` is NOT that loader** and should be
dropped from the plan — see §2.3. It is the *job* loader (binary card
decks for user programs), documented as prose only.

---

## 1. What is on the 451 pages

### 1.1 It is a STRAP assembly listing with a machine-code column

`MCP_Mar63_001-249.pdf` printed p.3 (PDF 10), printed p.53 (PDF 60),
and `MCP_Mar63_250-445.pdf` printed p.309 (PDF 60) and printed p.410
(PDF 160) all carry the identical seven-column header:

```
LINE   LOCATION        BINARY OUTPUT      NAME    STATEMENT              LOCATION   <addr>
```

and a right-hand card-ID column. A representative row, printed p.53
(PDF 60) line 6:

```
 6*  002776.40   000000.44 84  001000.20 50     L(BU,1),TJBPRO(LXPP)   -IS PP REF TBL AVAILABLE   16000197
```

Two half-words, each printed as *six octal digits . two octal digits,
space, two hex digits*. That is `listing_oracle.fmt_half()`'s output
format character for character. **Rule 3 is available.** The project's
`verify_*_listing.py` pattern transfers unchanged.

**Coverage, stated as a fraction, not a yes.** The binary column is
present on code pages and absent on control-card and header pages. In
11 pages read at full resolution:

| printed page (PDF) | total lines | lines with a binary field |
|---|---|---|
| 1 (3 and 8 — duplicated) | 17 | 0 — IOD control cards |
| 2 (9) | 39 | 16 |
| 3 (10) | 52 | 39 |
| 13 (20) | 38 | ~20 — constants/messages |
| 14 (21) | 43 | 43 |
| 17 (24) | 56 | ~50 |
| 23 (30) | 56 | ~54 |
| 36 (43) | 51 | ~30 — DD text/tables |
| 53 (60) | 56 | ~50 |
| 309 (vol 2, 60) | 50 | ~44 |
| 410 (vol 2, 160) | 53 | 53 |

Three further bootstrap pages were read after this table was built —
printed p.6 (PDF 13) is a 12-line error exit, 10 of 12 with binary;
printed pp.9 and 12 (PDF 16, 19) are 56-line console-message areas
whose DD rows each print a byte value (`375`, `002`, `376`) in the
BINARY OUTPUT column, so roughly 30 of 56 are checkable.

Sample is 14 of 445 printed pages (3.1%), chosen to span both volumes,
the IPL program, the MCP body, and the table/message sections. It is
**purposive, not random** — see §4.2, where the resulting bias is
corrected. Inference of mine: pure-code pages run ~90–100% binary
coverage and the whole-listing figure is ~80%.

### 1.2 It is all of MCP, and it is indexed

Printed pp.1–2 of the index (PDF 1–2) list **97 sections, F001–F097**,
each with a two-letter deck ID and a start page:

- **IPL PROGRAM**, F001–F009, printed pp.1–98:
  IOD CARDS (1), **IPL BOOTSTRAP (2)**, MCP INITIALIZATION PROGRAM
  `$IPLD` (15), COMMUNICATION REGION FOR MCP IN IPL (37), IPL UNCODE
  (38), IPL CONVERSIONS (42), IPL DECODE (47), IPL ASSIGN (59), IPL
  MOVE (81).
- **MCP PROGRAM**, F010–F097, printed pp.99–445:
  system origin and the Channel/Unit/File Area table definitions
  (99–103), the communication region, the pseudo-op codes, dispatcher
  exit codes (104–108), Program Status / Interrupt tables and the
  MCP-furnished PTOE (109–116), **IF Analyzer (117), Receptor (122),
  Maskable Interrupts (130), Standard Fixups (131), Conceptor (135)**,
  Return (140), I/O Control READ/WRITE/LOCATE/REWIND/… (151–170),
  `$FIXUP` (174), Identifier / Control Word Check / Status Evaluation
  / Verify (177–185), Output and Input programs (201–258), the
  conversion routines (259–262), **Job Control phases 1 and 4
  (265–291)**, Console Debugger (292), Commentator (302), Disk Fetch
  (311), Memory Dump (319), **Job Control Loader (320)**, Resume Load
  (332), Debugger (335), Dump (342), System Commands (361), Job
  Control 4 Overlapped (381), Assign/Move/Unassign Overlapped
  (398–445).

So: the whole operating system, not a component. Header on every page:
`03-15-63  IBM NEW VERSION OF MCP`.

### 1.3 Dialect: STRAP-II (see §3)

### 1.4 Two scanning facts that will bite any transcriber

- **PDF 3–4 are a duplicate of PDF 8–9** (both pairs are printed
  pp.1–2, card IDs 10000003 and 11000001 — confirmed by reading all
  four). PDF 5–7 carry no header at all. Volume 1 is therefore 249
  printed pages in 256 PDF pages: 2 index + 2 duplicated + 3 blank.
- **The offset is not constant even within a volume.** Volume 2: PDF
  60 is printed page 309 (offset +249); PDF 160 is printed page 410
  (offset +250). Cite by the page's own printed `PAGE NUMBER`, which
  every page carries, and verify each one.

---

## 2. The on-tape format

Per the coordinator's reframing: above the hardware IPL we control
both ends, so the authority is MCP's own code. What follows is what
the code does, with the two utility documents as cross-checks.

### 2.1 Layer 0 — the hardware IPL (fixed; another agent owns the detail)

What MCP's own source *asserts* about layer 0, printed p.2 (PDF 9),
lines 15–27:

```
15*  000040.00                                   SLC,(8)40.0
17*  000040.00   000041.00+ 000 000560 000001    CW(CR),X IPL BS,X BS END-X IPL BS,1
                                                 -IPL CW FOR READING IN IPL BOOTSTRAP
                                                 -RECORD FROM SOURCE TAPE
                                                 -ONE IN REFILL FIELD IDENTIFIES IPLCW
24*  000041.00   000043.44 00          X IPL BS  BD,X BEGIN   -DISABLE AND START IPL
25*  000041.40   000000.00+                      VF,0         -SLOT FOR TAPE CW
26*  000042.00   000000.00+ 000 000000 000000    XW,0         -SLOT FOR DISK CW
27*  000043.00                         X VERFY   (A*)DD(BU,32,8),C911*
                                                 -SLOT FOR DATE OF SOURCE TAPE IN A-8
28*  000043.40   000547.36 10           X BEGIN  LX,$15,XW SR
```

Read off those four lines, layer 0 is:

- The IPL control word lives at **octal word 40** — the first word the
  bootstrap assembles, via `SLC,(8)40.0`.
- It is a `CW(CR)` — Control Word, Count Within Record — with
  **data address `000041.00`**, **count `0o560` = 368 words**, and
  **refill field = 1**. The comment says the 1 in the refill field is
  what *identifies* this as the IPL CW.
- The first word read in, at **octal 41**, is a `BD` (Branch Disabled)
  to `X BEGIN`. So the hardware's job ends the moment the record is in
  core and control reaches octal 41; everything after that is MCP's
  own code.

Layer 0 therefore ends at "368 words landed at octal 41, execution
begins at octal 41". That matches RefMan printed p.126 in outline;
the Exchange-side detail is another agent's.

**368 vs 369 — the listing gives both, and they count different
things.** Printed p.13 (PDF 20) line 27 defines
`X IPL K SYN, 1.0 + X BS END - X IPLBS  - SIZE OF BOOTSTRAP`, i.e.
one word plus `0o621 − 0o41` = 1 + 368 = **369**. The IPL CW's own
count field is **368**. The arithmetic reconciles exactly if the 369
counts octal 40 through 620 inclusive — the whole bootstrap
*including its own IPL control word* — while the 368 counts only what
the IPL reads in, at octal 41 through 620. Flagged as my own
reconciliation: I did not find a line that states it. The practical
consequence for a transcriber is that **both numbers are correct and
a verification must say which it is checking** — an image assembled
from `SLC,(8)40.0` to `X BS END` is 369 words long; the tape record
inside it is 368.

### 2.2 Layer 1 — what MCP's bootstrap does with the tape

Printed pp.2–14 (PDF 9–21), read in full at pp.2, 3, 13, 14 and
sampled between. In order:

1. **Clear lower registers and storage** (p.2 lines 28–39): index-word
   loop over the lower registers, `BMKZ` / `M+1(BU,6)` to clear
   non-maskable indicators, then a `Z,0.0($15)` / `BADZ` / `CB+` loop
   to clear core; `SV,15,X S ROOF` saves the discovered 7030 size.
   *The bootstrap sizes memory by clearing it until it faults.*
2. **FIND IPL CHANNEL NUMBER** (p.3 lines 5–11): walks channels with
   `M+1(BU,19),X1 CCW`, issues `CCW,15.32,X IPL BS` on each, tests
   `BZB,X IPL BS+.63,X1` — i.e. it finds which channel the IPL came in
   on by looking for the refill-field 1 the IPL CW left behind. Then
   `LVE,15,X1 CCW` to keep the channel number.
3. **IO TEST** (p.3 lines 17–30): the canonical status loop —
   `SIC,X ERR AD` / `BEKJZ` (exchange check) / `BUNRJZ` (unit not
   ready) / `BCBJZ` (channel busy) / `CCW,0($15),X IPL BS` /
   `BB,X IPL BS+.24` (operation complete) / `CTO011(BU,5),X IPL BS+.19`
   / `BRZ` success.
4. **SPACE OVER TAPE MARK** (p.3 lines 35–52): `SPFL(SEOP),0.0($15)`,
   then the same status loop, then `REL(SEOP),0.0($15)` to clear the
   EE/EOP status bits. **So the record boundary the bootstrap cares
   about is a tape mark, and the layout it assumes is: IPL record,
   tape mark, next thing.**
5. **Bootstrap definitions and parameters** (p.13, PDF 20):
   `X IPL K SYN, 1.0 + X BS END - X IPLBS  - SIZE OF BOOTSTRAP`,
   `X EE EOP SYN(BU,5),(2)00110  - EOF STATUS BITS`,
   `X BUFER SYN,X IN END + 2000.0  - SLOTS LEFT FOR IOCD + IODS`,
   plus 29 console error messages (`MCP PARAMETER INPUT MISSING`,
   `IMPOSSIBLE OPERATING MODE`, `SPOOL INPUT ASSIGNMENTS NOT MADE`, …).
6. **PROSA CWS** (p.14, PDF 21) — the bootstrap's last page, and the
   finding that changes the shape of the problem. Forty-two chained
   control words:

   ```
    4* 000552.00  011406.00+ 110 001001 000553   X PROSA  CW(CDSC),0     +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD
    5* 000553.00  012406.00+ 110 001001 000554            CW(CDSC),512.  +X BUFER,513,$+1.0  -FETCH ONE PROSA RECORD
   ...
   42* 000620.00  057406.00+ 000 001000 000621            CW(CR),19456.  +X BUFER,512,$+1.0
   43* 000621.00+ +00000000  NULL                X BS END SYN,$   - END OF THE MCP IPL BS ROUTINE
   ```

   Each fetches 512 words; the chain covers 19,968 words into
   `X BUFER`. `CDSC` is STRAP-II's *Count Disregarding Record, Skip
   and Chain* (C28-6129 Appendix B, printed p.46 / PDF 49).

   **And `PROSA` is a disk IOD.** Printed p.1 (PDF 3) line 1:
   `B PROSA  IOD,DISK,CDIDEX`. Printed p.2 line 26 allocates both
   `VF,0 -SLOT FOR TAPE CW` **and** `XW,0 -SLOT FOR DISK CW`.

### 2.3 Where that leaves "the MCP portion"

**The bootstrap comes off tape; the ~20K-word payload it fetches next
comes off disk.** That is what the code says, and it is the single
most consequential thing in this report after the binary column. A
tape image alone may not be sufficient to boot this MCP — a disk image
very likely has to be manufactured too, and the model has no disk
channel at all (§5).

This is a *reading of the bootstrap's own control words*, not a
settled fact: I did not trace `$IPLD` (printed pp.15–36) far enough to
see whether the disk path is conditional on a disk being present and a
tape path substituted when it is not. Printed p.2 allocating *both* a
tape CW slot and a disk CW slot is suggestive of exactly such a
choice. **This is the highest-value remaining read in the whole
document**, and it is 22 printed pages.

For context, `C22-6678-1` printed p.29 (cited in `archival_inventory.md`
as verified) says MCP boots from a master system tape. Both can be
true: tape carries the bootstrap and the system, disk is the working
store the bootstrap stages into. Flagging the tension rather than
resolving it.

### 2.4 The two utility documents — what they actually are

Both opened in full this session (18 and 21 pages, rendered at 150 dpi).

**`ka_ul1_load_and_tape_write_util.pdf` — "LOADER AND TAPE WRITE
UTILITY, KA UL1, October 13, 1961".** Writeup pp.1–3, then a complete
STRAP listing pp.4–18 with a printed binary column. It is a *card*
loader: a punful deck placed in front of a punid deck, IPL'd from the
card reader, which loads the deck into core and then **optionally
writes an IPL tape** under maintenance switch 37 (switches 12–17 pick
the channel, 21–23 the drive; channel 32 drive 0 if all zero).

The tape-write routine is page 17, complete and short enough to quote
its shape:

```
TA1  BZB,MNREG&,37,B5         @BRANCH IF NO WRITE TAPE.
     ...                      @CALCULATE CONTROL WORD.
     ST%BU¤,END               @TAPE WRITE CW.
     ST%BU¤,0%$X3¤            @IPL CW.
     ST%BU¤,1.0%$X3¤          @IPL BD.
     LOC%$EOP¤,0%$X1¤,0%$X2¤  @LOC TAPE.
     W%$EOP¤,0%$X1¤,END       @WRITE IPL TAPE.
     UNLOAD%$EOP¤,0%$X1¤      @UNLOAD TAPE.
     B,B5                     @START PROGRAM.
```

**This corroborates §2.1 exactly**: an IPL tape is one `LOC` + one
`W` of a single record, and the thing written begins with an IPL
control word followed by an IPL branch descriptor. Same two-word
preamble MCP's bootstrap expects. No disagreement between the two
sources on layer 0/1.

What it is *not*: it does not write an MCP system tape. It writes a
single-program diagnostic IPL tape. Treat it as a worked example of
the format, which is what the coordinator asked for.

**`ja_uc1a_maintenance_tape.pdf` — "MAINTENANCE TAPE, JA UC 1A, MNT
TP 1".** "Stores J Series Programs on tape with ability to select and
operate one, or more, or all programs." Writeup + flowcharts, pp.1–~6;
remaining pages the listing. Record layout (printed p.3): **one record
per program**; the control routine is re-read each time a program is
loaded and occupies locations 64–192 decimal (the flowchart says
`(8)100-177`); maintenance switches 0–31 each select one program;
forward tape movement loads that record, backward movement is
Backspace or Rewind. Its own front page says "Programs becoming
obsolete — JA UC1", consistent with the note already in
`archival_inventory.md` §5.

Relevant, but it is the *diagnostic* tape, not MCP's.

**`C28-6379-0_MCP_Loader.pdf` — the brief's premise is wrong here, and
so was mine until I checked.** `archival_inventory.md` §4 already
records this file as **read in full**, as "Loader and BSS Processor",
prose only, zero loader source. Spot-checking PDF p.7 confirms it: the
page is the BSS (Binary and Symbolic Subroutine) processor
description, "operates as a preprocessor to the MCP loader in a
FORTRAN environment", with card-order rules and card-class formats. It
documents the loader that loads *user programs* at job time from
binary card decks and the disk. **It has nothing to do with the IPL
and settles nothing about the system tape.** It should come off the
plan.

---

## 3. STRAP-1 vs STRAP-II: the delta is additive, and most of it is cosmetic

**MCP's source is STRAP-II.** Printed p.2 (PDF 9) lines 3–10 open with
`PUNFUL`, `PUNORG`, `PUNID,11E11BSP`, `RESEQ`, `PRNS`, `TAIL,(2)G` —
every one of these is in C28-6129's "Additional Pseudo Operations"
(printed pp.36–37 / PDF 40–41) or Appendix B, and `TAIL,(n)SYMBOL` is
the *multi-level* tailing form, which is STRAP-II only.

The direction that matters is **assembling STRAP-II source with a
STRAP-1 assembler**, and C28-6129's own Introduction (printed p.1 /
PDF 5) does *not* address that. What it says is the converse:

> "Any program that can be assembled by STRAP-I … can be assembled by
> STRAP-II without modification. Thus, all the specifications defined
> in the 704-709-7090 Programming Package Manual (IBM Form No.
> C22-6531-1) for STRAP-I are also applicable to STRAP-II, **with the
> exception of the behavior of two pseudo operations that control the
> format of the output listing, and one new restriction of the use of
> radix 16.**"

Useful anyway: it means the *language core* is shared and the delta is
confined to additions (plus those two carve-outs). Appendix C (printed
p.47 / PDF 50) confirms the instruction set at the top: "The following
list of mnemonics may be used with Strap-1 and Strap-2." **No
machine-instruction mnemonic work is needed.**

Appendix B (printed p.46 / PDF 49) is the complete pseudo-op roster —
53 entries. Split by whether they touch the memory image:

**Parse-and-discard (no effect on the object code) — 17 of the 53 plus
the body-text extras:**
`PRND PRNID PRNS PUNFUL PUNID PUNNOR REM SEM` from Appendix B, and
from the body text `PUNORG NOPUN NOPRNT SPNUS PUNSYM PUNALL RESEQ`.
These control the listing and the punched deck. A STRAP-1 assembler
reading a transcription can skip all of them in a single pass.

**Semantic (changes the image or the symbol table) — the real work:**
- `TAIL` / untail, including multi-level `TAIL,(n)SYM` — appends a
  tail to every symbol until changed, up to ten levels. MCP uses it
  from the second page onward, so **the symbol table needs scoping**.
  This is the one genuinely structural change.
- `DR` / `DRZ` (Data Reservation, with and without zeroing) — storage
  reservation with array dimensions. MCP uses `DR(N),(16)` and
  `DR(BU),(100)` (vol 2 printed p.309).
- `SLCR` (Set Location Counter Relative) — like SLC but suppresses
  punching and makes following symbols relative; allowed below octal
  41 where SLC is not.
- `TLB` (Terminate Loading and Branch) — an END that doesn't end the
  assembly.
- The DD character-set prefixes `(A*)`, `(CC*)`, `(IQS*)`, `(IQSX)`,
  `(N)`, seen throughout the MCP listing, which select the character
  encoding of a DD's text.
- The control-word family — `CW CCR CD CDSC CF CR RF SCCR SCR SCD
  SCDSC` — and the I/O-function family — `BS CRDRUN ERG EVEN GONG HD
  KLN LD NOECC ODDECC ODDNEC REW RLF RLN SKIP SP SPFL TILF UNLOAD WEF`.
  The bootstrap needs `CW(CR)`, `CW(CDSC)`, `SPFL`, `UNLOAD` at
  minimum.
- Section II's entry modes (printed pp.24–35): F entry mode, radix
  specifier, field entry mode.

**Against what the project has today.** `strap/strap_asm.py`
implements `DD VF XW END SYN SLC CNOP` (7) and recognizes-but-stubs
`CF RF DDI CW EXT` (5). So of Appendix B's 53, **7 are done, 5 are
stubs, 41 are absent** — but 17-plus of those 41 are parse-and-discard.

**Estimate for the assembler work, for the bootstrap only:**
`TAIL` (multi-level, with scoping), `CW(CR)`, `CW(CDSC)`, `DR`, the
`(A*)`/`(IQS*)` DD prefixes, plus discarding `PUNFUL PUNORG PUNID
RESEQ PRNS SEM`. My inference, flagged as such: that is days of
assembler work, not weeks, and it is *bounded* because the bootstrap
is 13 pages and I can enumerate every pseudo-op it uses by reading
them. **This question does not dominate the cost estimate.** The
transcription volume does.

---

## 4. The honest size-up

### 4.1 The project's demonstrated rate

| Measure | Value | Source |
|---|---|---|
| Calendar span | 2026-08-24 → 2026-10-16 = **53 days** | `git log` first and last commit dates |
| Transcribed programs | **242** `.strap` files | `ls strap/programs/*.strap` |
| Code lines (non-comment, non-blank) | **15,984** | `grep -vcE '^\s*(!\|$)'` summed |
| Rule-3 verified machine-code rows | **5,100** | octal-location row literals across the 181 `verify_*_listing.py` |
| Mean program size | **66 code lines** | 15,984 / 242 |
| Largest program | **421 code lines** (`ibox1_p43_p51_span.strap`) | measured |

Derived rates: **302 code lines/day**, **96 rule-3 rows/day**.

### 4.2 MCP's size

**The sample is purposive, not random, and a plain mean of it is
biased low.** Of the 14 pages now read at full resolution, 8 come from
printed pp.1–14 — 3% of the document — because that is where the
bootstrap is, and those front pages are systematically short (banner
pages, a 12-line error exit, control cards). Separating them:

| Stratum | Pages read | Lines | Mean |
|---|---|---|---|
| Front (printed 1–14) | 1, 2, 3, 6, 9, 12, 13, 14 | 17, 39, 52, 12, 56, 56, 38, 43 | **39.1** |
| Body (printed 15–445) | 17, 23, 36, 53, 309, 410 | 56, 56, 51, 56, 50, 53 | **53.7** |

Weighting each stratum by its true page count:

```
  14 front pages × 39.1 lines  =     547
 431 body pages  × 53.7 lines  =  23,145
                                  -------
 445 printed pages             ≈  23,700 source lines
 23,700 × ~0.8 binary coverage ≈  19,000 machine-code rows
```

The body stratum is 6 pages of 431 (1.4%), spread across both volumes
and four punids; its six values span 50–56, so the stratum mean is
tight even on a small sample. The unweighted figure would have been
46.5 lines/page → ~20,700 lines, i.e. **the bias was ~15% low**.

*An OCR-based line count was attempted as corroboration on 11
independently sampled pages and is not reported as a number: it
returned 10–31 lines on pages my own reads put at 38–56, i.e. it
undercounts by 40–70% on this typeface, consistent with §5 Rank 5.*

### 4.3 Division

```
All of MCP, rows:   19,000 / 96 rows/day   = 198 days ≈ 6.5 months
All of MCP, lines:  23,700 / 302 lines/day =  78 days ≈ 2.6 months
```

The **rows** figure is the binding one, because rule 3 requires the
printed machine code be transcribed alongside the source. Call it
**six to seven months of transcription at the pace this repository has
actually sustained**, and that is transcription only — it excludes the
interrupt system, the exchange as a real bus requester, the disk
channel, the console, and the tape record/tape-mark model, none of
which exist yet (§5).

**Flagged as my own inference: the rate will not transfer linearly,
and it will transfer badly.** The existing corpus is 242 *independent*
programs averaging 66 lines, with boundaries chosen by the
transcriber to be self-contained and individually runnable. MCP is one
program in 97 sections with `TAIL`-scoped symbols crossing section
boundaries, meaning partial transcriptions do not assemble in
isolation the way `ax5b_162_test1a.strap` does. The honest reading of
198 days is "a lower bound given no new difficulties".

### 4.4 The bootstrap

Seven of the bootstrap's 13 printed pages (pp.2, 3, 6, 9, 12, 13, 14
= PDF 9, 10, 13, 16, 19, 20, 21) were read at full resolution — 54%
of it, not a corner of it.

```
lines: 39, 52, 12, 56, 56, 38, 43  →  296 / 7 = 42.3 lines/page
13 printed pages × 42.3            ≈  550 source lines

rows with a printed value, same 7 pages:
  p.2  16/39   p.3  39/52   p.6  10/12   p.9 ~30/56
  p.12 ~30/56  p.13 ~20/38  p.14 43/43      ≈ 188/296 = 64%
                                   (the message pages print each DD's
                                    byte value — 375 / 002 / 376 — in
                                    the BINARY OUTPUT column, so they
                                    are rule-3 checkable too)
550 × 0.64                         ≈  350 machine-code rows
350 / 96 rows/day                  ≈  3.6 days, call it 4
```

**Object-code size as a second, free oracle — but state which number
you are checking.** Per §2.1: an image assembled from `SLC,(8)40.0`
through `X BS END` is **369 words** (octal 40–620 inclusive); the tape
record the IPL reads is **368 words** (octal 41–620), which is the IPL
CW's own count field `0o560`. A transcription that lands on neither is
wrong independently of the binary column.

**~1.3× the largest existing program in the corpus** (421 code lines).
Days, not months.

---

## 5. Cheaper routes, ranked

### Rank 1 — Transcribe the IPL bootstrap only (pp.2–14), rule-3 verified

Not on the brief's list; it is what the evidence points at. ~4 days of
transcription (§4.4), a bounded assembler delta (§3), and it produces
*the* artifact: a 369-word IPL record that is real IBM code, written
to a tape image whose two-word preamble is specified by MCP's own
source and corroborated by `ka_ul1` (§2.4).

Model work it requires, from reading `bsv/StretchIO.bsv` and
`bsv/StretchExecute.bsv`:

| Needed by the bootstrap | Status today |
|---|---|
| `CCW` (Copy Control Word) | implemented (`StretchExecute.bsv:3389`) |
| `REL` / `REL(SEOP)` | implemented (`:3379`) |
| `RD` / `W` on channel 34 | implemented, with a `gen_tape_tb.py` driver and `run_tape_test.sh` already in the suite |
| `SIC`, `BEKJZ`/`BUNRJZ`/`BCBJZ` indicator branches | implemented (used by the existing corpus) |
| **`SPFL` (SPACE FILE)** | **not implemented** — falls to the `default:` arm at `StretchExecute.bsv:3372` and sets Operation Invalid |
| **`LOC`** | **not implemented** — `StretchExecute.bsv:3376`, explicit |
| **`UNLOAD` distinct from `REWIND`** | conflated; `18'o136, 18'o137` share one arm |
| **Tape marks / records** | **absent** — `tapeImg` is a flat `Vector#(TapeWords, Reg#(Word64))`, `TapeWords = 16`, no record or file-mark structure |
| **An IPL mechanism at all** | **absent** — `StretchIO.bsv:288` says so in as many words: "matching the p.126 'initial power-on' reset description closely enough for a simulated system with **no IPL**" |

That is five concrete, individually small model additions, each with a
primary source (RefMan pp.126, 130–132) and each testable in the
existing tape testbench. This is normal work for this project, not a
new category of work.

### Rank 2 — Ask the surviving archives, in parallel, for zero cost

**I did not perform an external search this session** and am relying
on `archival_inventory.md`'s recorded bitsavers sweep (all 52 PDFs
under `pdf/ibm/7030/`, with `bits/IBM/7030/` returning 404) plus its
standing statement that no machine-readable artifact has been found.
That is a *recorded* negative, not one I re-established.

The asks, concretely:

- **Computer History Museum** (`collection@computerhistory.org`, and
  the Software Preservation Group) — ask specifically for *IBM 7030
  magnetic tapes or card decks in the collection, whether or not
  read*, naming the Los Alamos (LASL), AWRE Aldermaston, MITRE,
  NSA/Harvest, and IBM Poughkeepsie/Mohansic installations. CHM holds
  unread media it does not catalogue at the file level.
- **Paul Pierce's collection** (`paul@piercefuller.com`) — he has read
  and published IBM 7xxx tape images (704/709/7090 system tapes)
  including from 1960s site backups. The specific ask: *any 7-track
  tape labelled 7030, Stretch, STRAP, or MCP*, and whether his reader
  can handle the 7030's tape format.
- **Los Alamos National Laboratory Archives / National Security
  Research Center** — LASL ran a Stretch 1961–1971 and wrote IVY and
  COLASL for it (see `docs/thirdparty_software/README.md`). Ask for
  the records-retention listing for the 7030 era, not the catalogue.
- **bitsavers** (`aek@bitsavers.org`) — ask whether anything 7030 sits
  in the unprocessed queue, and offer the manufactured artifact back.
- **The simh / 7030 emulator community** — there is at least one 7030
  emulation effort; ask what test material it runs and where that came
  from.

Zero cost, weeks of latency, low probability. Worth sending on day one
and not waiting for.

### Rank 3 — A minimal bootable stand-in exercising the same I/O path

Write a ~30-line STRAP program that is laid out exactly like the
bootstrap's first page — IPL CW at octal 40, `BD` at octal 41, the
`CCW`/`SIC`/`BEKJZ` status loop, `SPFL`, `REL` — and boot *that* from
a manufactured tape image. It is not IBM's code and buys no historical
claim, but it is the right **first** step: it forces the five model
additions in Rank 1 into existence against a program small enough to
debug, and it makes the tape-image writer real. Then Rank 1 drops onto
working infrastructure.

Recommended as a *prerequisite* to Rank 1, not an alternative to it.

### Rank 4 — Load core directly, which is what the model does today

Keeps working. It is the correct way to run everything in
`strap/programs/`. It simply does not answer "we booted from tape",
and the gap between it and Rank 1 is now measured (five model
additions, ~4 days of transcription) rather than unknown. Its real
role is as the fallback for *MCP* even after the bootstrap boots: if
the disk question in §2.3 resolves badly, loading the MCP body
directly into core and letting the transcribed bootstrap branch into
it is a legitimate, honestly-labelled halfway house.

### Rank 5 (last) — OCR the listing and assemble it

**Measured, not guessed.** Printed p.3 (PDF 10) rendered at 600 dpi
grayscale, `tesseract --psm 6 -c preserve_interword_spaces=1`, ground
truth from my own full-resolution read of the same page, 39 binary
fields:

| | Binary fields recovered exactly |
|---|---|
| Raw tesseract output | **0 / 39 (0%)** |
| After a hand-built, column-aware normalisation (C/O/U/G→0, l/i→1, B→8, S→5, applied **only** in the octal positions) | **17 / 39 (44%)** |

(Measurement script and both texts are in the session scratchpad;
reproducible with `tesseract` 5 against `pdftoppm -r 600 -gray`.)

The failure is systematic, not noise: this drum printer's `0` is read
as `C` almost everywhere (`COC551.CC` for `000551.00`). And the
obvious fix is a trap — the last two characters of each group are
**hex**, where `C` is a legal digit. Printed p.3 line 20's true value
is `000133.03 C6`: a blanket C→0 corrupts it to `000133.03 06`, and
the corruption is *silent* because the result is still well-formed.
The statement column fares better but still produces semantic
corruptions, e.g. `REL(SECP),0.20($15)` for `REL(SEOP),0.0($15)` —
a wrong operand address that assembles cleanly.

A 56% residual error rate on the exact column that rule 3 depends on,
with silent well-formed failure modes, means OCR output would have to
be verified character by character against the page — which is the
manual transcription this route was supposed to avoid, plus the extra
work of distrusting a plausible-looking draft. **OCR is not a shortcut
on this typeface.** The existing corpus's method (read the page,
measure glyphs at 600 dpi where a digit matters, per
`docs/listing_typography.md`) is not merely safer, it is faster.

---

## 6. The smallest artifact that is a real claim

**The MCP IPL bootstrap, printed pp.2–14.**

It qualifies on every axis:

- **Real IBM systems software.** Header: `03-15-63 IBM NEW VERSION OF
  MCP`; section banner `MCP INIALIZATION BOOTSTRAP` [IBM's typo];
  deck `11E11BSP`.
- **Complete and self-contained** — established from 7 of its 13
  pages, so this is partly my inference. It begins at
  `SLC,(8)40.0` / the IPL CW at octal 40 and ends at
  `X BS END SYN,$  - END OF THE MCP IPL BS ROUTINE` at octal 621, and
  the middle pages I read (pp.6, 9, 12 — the error exit and the
  console-message area) introduce **no pseudo-op outside the §3 list**
  (`BD SIC B REL(SEOP) BEKJ CCW BB DD CNOP SYN` and the `(IQS*)` DD
  prefix) and **no symbol defined outside pp.2–14**. Pages 4, 5, 7, 8,
  10, 11 are unread; the inference is that they resemble pp.6/9/12.
- **It is exactly the thing being claimed.** Its entire purpose is to
  be loaded from tape by the IPL and to bring up the system. "We
  booted MCP's IPL bootstrap from a manufactured tape image on an FPGA
  7030" is a precise, defensible, and unusual sentence.
- **Verifiable to this project's standard.** Binary column on every
  code line, plus the independent 369-word size check (§4.4).
- **Small.** ~550 source lines, ~1.3× the largest program already in
  the corpus (`ibox1_p43_p51_span.strap`, 421 code lines).
- **The model is close.** Five named gaps, all of them ordinary
  (§5 Rank 1).

The honest caveat, stated up front rather than discovered later: the
bootstrap's last page fetches ~20K words off **disk** (§2.2 item 6,
§2.3). Booting the bootstrap means running it to the point where it
issues that chain. Whether it completes depends on the disk question,
which is 22 unread printed pages away. **Getting the bootstrap to the
PROSA chain is already the claim; getting past it is the next
project.**

### Recommended order

1. Read `$IPLD` printed pp.15–36 (PDF ≈22–43) to settle tape-vs-disk
   (§2.3). 22 pages. Do this before committing to anything else.
2. Rank 3: minimal stand-in, forcing `SPFL`, `LOC`, `UNLOAD`, tape
   records/marks, and an IPL mechanism into `StretchIO.bsv`.
3. Rank 2 asks, sent in parallel on day one.
4. Rank 1: transcribe pp.2–14 with the machine-code column, verify
   with `listing_oracle.py`, boot it.
5. Decide on all of MCP with the §4.3 number in hand, by then
   calibrated against a real 13-page sample.

---

## 7. Bounded negatives — what was searched, and how

Stating these as claims with their searches attached, per `AGENTS.md`.

- **No text layer in any of the five PDFs.** `pdftotext <f> - | wc -c`
  returns exactly one byte per page for `MCP_Mar63_001-249.pdf` (256),
  `MCP_Mar63_250-445.pdf` (195), `C28-6379-0_MCP_Loader.pdf` (24),
  `ka_ul1_load_and_tape_write_util.pdf` (18),
  `ja_uc1a_maintenance_tape.pdf` (21) — i.e. form feeds only. Every
  finding here is from rendered page images.
- **I sampled, I did not read 451 pages.** Read at full resolution:
  MCP vol 1 PDF 1, 2, 3, 4, 8, 9, 10, 13, 16, 19, 20, 21, 24, 30, 43,
  60; MCP vol 2 PDF 60, 160; `ka_ul1` PDF 1, 2, 4, 6, 8, 17;
  `ja_uc1a` PDF 1, 3; `C28-6379` PDF 7; `C28-6129` PDF 4, 5, 16, 17,
  40, 41, 43, 49, 50. Header-only checks (OCR) on MCP vol 1 PDF 5, 6,
  7, 11, 12. That is **18 of 451 MCP pages read in full (4.0%)**, of
  which 8 are the 14 front pages and 6 are body pages — a
  distribution that matters for §4.2 and is corrected for there.
- **Six of the bootstrap's 13 pages are unread** (printed pp.4, 5, 7,
  8, 10, 11). §6 says so in the sentence that makes the claim.
- **"Is there a machine-code column" is answered, not inferred.** Four
  pages spanning both volumes and three different punids
  (`11E11BSP`, `11D11IPL`, `11D11MCP`, `22$EOJ`) all show it.
- **I did not search outside `docs/` this session.** No web search, no
  archive contact. Route 5(b)'s negative is `archival_inventory.md`'s,
  dated 2026-09-03, not mine.
- **I did not trace `$IPLD`.** Printed pp.15–36 were sampled at pp.17,
  23, 36 only — enough to see that it is IOCD-card processing building
  the CST and UST, not enough to settle the tape/disk question. Said
  plainly in §2.3.
- **I did not read the STRAP-II System Analysis Guide**
  (`C22-6729`, 211 pp.) for this. `archival_inventory.md` §2 already
  covers it; nothing in §3 above depends on it.
- **RefMan printed p.126 (the hardware IPL) was not opened here** —
  another agent owns the Exchange side. §2.1 reports what *MCP's
  source* asserts about layer 0, which is independent evidence for the
  same mechanism, and flags it as such.
- **The lines/page figure rests on 14 pages (3.1%), stratified.** The
  body-page mean — the one that drives the whole-MCP number — rests on
  6 pages of 431 (1.4%), whose values span 50–56. The purposive
  sampling and the ~15% bias it introduced are stated and corrected in
  §4.2 rather than left for a reader to find. The OCR corroboration
  failed and is reported as failed rather than quietly dropped.
