# The BX-0 decks: what `ka_ex1_bx-0.pdf` and `ka_ex1b_bx-0.pdf` actually are

Reconnaissance pass, 2026-10-16. Both PDFs opened for the first time by
this project. Nothing is transcribed here; this document decides whether
a transcription is worth commissioning, and for what.

The question it was written to answer: **are these a deck oracle for the
Exchange in the way `jb_ax5b` is for the I-box?**

The short answer is that the question has three parts and they get three
different answers.

- **As a runnable deck** — a program that is assembled and then executed
  against the model — **no.** BX-0 never executes on the CPU. It has no
  instruction stream. Settled by its own printed p.2 (§1 below), and no
  amount of transcription changes it.
- **As a bit-exact encoding oracle for the Exchange control word** —
  **yes, strongly.** PDF pp.11-78 are an unbroken STRAP assembly listing
  carrying IBM's own printed machine-code and location columns for the
  program's control words. This is the same class of evidence
  that `verify_ibox1_listing.py` and `verify_ibox4_listing.py` consume
  (AGENTS.md rule 3). See §4.
- **As a behavioural test-vector oracle for the Exchange** — **yes, and
  it is better suited to a Bluespec testbench than to a CPU program.**
  Roughly forty named tests each fix a (skip, multiple, chain, count)
  setting and state the expected device output verbatim. The "operator"
  that BX-0 requires is, structurally, a testbench driving the Exchange
  directly. See §5.

What BX-0 is **not** an oracle for is the CPU↔Exchange interface — the
`RD`/`WR`/`CTL`/`LOC`/`REL`/`SEOP` instructions, acceptance, rejection
and the indicator bits. It says so itself. The documents that would
cover that exist, are named in a primary source in this repo, and are
**not in `docs/`**. See §7 — that is the single most actionable finding.

**The disk does not appear.** Not in the equipment table, not as a test
section, not in the listing. See §6.

---

## 0. Citation convention, and page numbering

Checked first, because `jb_ax5b` and `jb_ax4b` carry no printed page
numbers and `ja_ua1` carries none either.

**BX-0 is different, in two halves:**

- The **writeup** (PDF pp.1-10 of each file) is a **two-up scan**: two
  original 8½×11 portrait pages side by side on each 17×11 landscape PDF
  page. These original pages **do** carry printed page numbers, centred
  at the foot in the form `-1-` through `-15-`. PDF p.*N* holds printed
  pp. 2*N*−2 and 2*N*−1 from p.2 onward (PDF p.1 is the cover plus the
  table of contents, both unnumbered).
- The **listing** (PDF p.11 onward) is **one-up fanfold**, one printer
  page per PDF page, and carries **no legible printed page number** —
  only a smudged two-character mark in the extreme top-right corner of
  some sheets, cut off by the scan. This is exactly the `ja_ua1`
  situation.

So: writeup facts are cited here as **PDF p.*N* (printed p.*M*)**;
listing facts are cited by **PDF page only**.

Neither PDF has a text layer (`pdftotext` returns one newline per page).
Everything below was read from `pdftoppm` renders at 300-400 dpi; the
listing's machine-code column needs a half-page crop at 400 dpi to be
legible. Renders were run with the machine at load average 172 → 96;
full-file rendering at 600 dpi was not attempted and is not necessary.

---

## 1. What kind of document this is

**Title page (PDF p.1, both files, identical):**

> 7030 DPS — BX-0 — File No. KA EX1 / KA EX1A / KA EX1B / KA EX1C
>
> **BX-0 — BASIC EXCHANGE PARALLEL MAINTENANCE PROGRAM** — September 1, 1961
>
> 1. Maintenance program. Used to test data paths to and from I/O units
>    and to and from main memory independent of CPU.
> 2. Programs becoming obsolete. None.
> 3. KA EX1 and KA EX1A are applicable to systems using 48 ECS printer
>    code. KA EX1B and KA EX1C are applicable to systems using 48 BCD
>    printer code.

It **does** follow the corpus pattern, with its own section names. Table
of contents (PDF p.1):

| § | Title | Printed p. |
|---|---|---|
| 1 | PURPOSE | 1 |
| 2 | EQUIPMENT REQUIREMENTS | 1 |
| 3 | MODES OF CONTROL | 2 |
| 3.1 | Self Control | 2 |
| 3.1.1 | Procedure | 2 |
| 3.1.2 | Success Indications | 13 |
| 3.1.3 | Failure Indications | 13 |
| 3.1.4 | Supplementary Information | 14 |
| 3.2 | DCP Control (Not Applicable) | — |
| 4 | PROGRAM PHILOSOPHY | 15 |

### 1.1 The sentence that settles the "runnable deck" question

PDF p.2 (printed p.2), §3.1 *Self Control*, verbatim:

> **BX-0 is exclusively a manually operated test, since it is independent
> of the CPU. It requires the operator to manually set the bits on the
> exchange maintenance console and manually execute all instructions.**
> The output from each I/O unit test is indicated in the section
> containing the instructions for that test.

And §4 PROGRAM PHILOSOPHY, PDF p.9 (printed p.15), verbatim:

> BX-0 is designed for parallel maintenance. It uses control word
> sequences to test data paths to and from main memory and to and from
> the I/O units. The test is independent of CPU and requires the ability
> to get to and from main memory to operate.
>
> All tests start with the simplest control words and proceed to include
> the chain, multiple and skip flags. **The test is executed completely
> from BX and, therefore does not test communication paths to and from
> CPU or all of the control functions.**

"Parallel" in the title means *in parallel with the CPU* — off-line
exchange maintenance while the CPU is doing something else. The listing's
own banner line (PDF p.11) says it plainly:

> `PRNID,BX0 - BASIC EXCHANGE OFF LINE MAINTENANCE-E.W.JOHNSON`

The `PRNID` idiom is the same one `ja_ua1` opens with
(`PRINID, SSIP CBD 2-9-61 JA UA1`).

### 1.2 The relationship between the two PDFs

Four versions exist; the difference is only the printer character code
and the load address. PDF p.9 (printed p.15), §II *Explanation of File
Numbers*, verbatim table:

| File No. | Printer Code | Starting Location |
|---|---|---|
| KA EX1 | 48 ECS | 50,000 |
| KA EX1A | 48 ECS | 100,000 |
| KA EX1B | 48 BCD | 50,000 |
| KA EX1C | 48 BCD | 100,000 |

> Four versions of the BX-0 program are presently available. These
> programs differ only in the printer code used and in the starting
> location.

The two PDFs carry **the same writeup, byte for byte as far as read**
(cover and TOC on PDF p.1 are identical in both). They differ only in the
listing, and the listings identify themselves by their location columns:

| PDF | Pages | Listing location range | Closes with | Therefore |
|---|---|---|---|---|
| `ka_ex1_bx-0.pdf` | 78 | `100000.00` … (PDF p.78) | `END,64.0` at `000536.40` | **KA EX1A** — 48 ECS, starting location 100,000 |
| `ka_ex1b_bx-0.pdf` | 66 | `05xxxx` … `053436.00` | `END,START` at `053436.00`, value `50000.00` | **KA EX1B** — 48 BCD, starting location 50,000 |

The "Starting Location" column of the file-number table is therefore
**the literal octal location-column value**: `050000` and `100000`. That
settles the mapping in both directions.

**The 12-page difference is the `PUNFUL` card test deck (§3), and it is
only in `ka_ex1_bx-0.pdf`.** `ka_ex1b_bx-0.pdf`'s listing runs straight
to `END,START` with no second assembly; `ka_ex1_bx-0.pdf` carries the
main program *and* the punched-deck image.

**Practical consequence: transcribe `ka_ex1_bx-0.pdf`.** It is the only
one of the two that contains the card deck the reader tests need, and the
card deck is the one physical requirement the model could not otherwise
satisfy. `ka_ex1b_bx-0.pdf` is a second witness to the same program's
control words at a different load address — useful for separating
address-dependent fields from address-independent ones, and for nothing
else.

---

## 2. What running it requires — the question that decides usability

### 2.1 The equipment table

PDF p.2 (printed p.1), §2.1 *Testing Requirements*. Legend: `N` =
Necessary for Basic Testing, `A` = Additional Requirements for Full
Testing, `*` = Exception. Transcribed as printed:

| 0-8K | 8K-16K | 16K-32K | 32K-Above | Ops Console | Card Reader |
|---|---|---|---|---|---|
| | | **N** | | **N** | **N** |

| Punch | Printer | Disc | Tapes | | |
|---|---|---|---|---|---|
| **N** | **N** | *(blank)* | **N** | | |

§2.2 *Buffer Equipment Requirements*: a two-cell table headed **Disc** and
**Tapes**, **both cells blank**.

So BX-0 needs a 16K-32K memory, the operator's console, the card reader,
the card punch, the chain printer, and tape — **and no disk.**

### 2.2 The operator and the BX maintenance console

This is the real requirement. PDF p.2-3 (printed pp.2-3), §3.1.1
*Procedure*, II *Overall Procedure*, A *Reading or Writing* — the
fifteen numbered steps, condensed but with every named control kept
verbatim:

1. Place the **BX mode switch** in the **TEST MODE** position.
2. Depress **CLEAR MEMORY** pushbutton.
3. Set **"Type of Test"** to **EX MEM**.
4. "From the BX-0 listing, obtain the main memory address of control word
   desired. Place this address in the **REFILL ADDRESS** of the panel
   keys."
5. "In the **EXCHANGE MEMORY ADDRESS switch register**, enter the
   **CHANNEL NUMBER** desired and **bit 128 (Control Word Memory)**.
   Make the total parity ODD."
6. Depress the **"LOAD MEMORY"** switch.
7. Depress **SINGLE CYCLE** pushbutton twice.
8. Turn OFF the load memory switch.
9. "In the exchange memory address switch register, turn OFF bit 128.
   Parity should now be even."
10. "Be sure the channel to be used is NOT blocked by the **BLOCK CHANNEL
    switches**. All **data word transfer**, **service request**, and
    **channel signal simulation** switches should be OFF."
11. Set type of test to **Main Memory UNIT**.
12. Depress the **READ** or **WRITE** pushbutton depending upon
    instruction desired.
13. Depress the **SINGLE CYCLE** pushbutton and check **ACCEPT** response.
14. Depress the **START Key**. The instruction entered will now be
    executed.
15. "To insure proper operation, stop BX and SINGLE CYCLE through BX
    control word memory until the channel used is selected. At this time,
    examine the control word for proper interrupt status bits, data word
    address, and word count setting. Unless otherwise stated, the normal
    status bit setting is EOP. The flag bits (chain, multiple, and skip)
    should still be at their original setting."

B *Control or Locate Operations* (printed p.4), same shape:

1. BX Mode switch to **TEST MODE**. 2. **CLEAR MEMORY**. 3. Set "type of
test" to **UNIT TEST**. 4. "Set the desired channel number in the
EXCHANGE MEMORY ADDRESS switch register, even parity count. (Bit 128 must
be OFF.)" 5. "In the **C₀ - C_t panel switches**, enter the **CONTROL
CODE** or **LOCATE NUMBER** desired." 6. Depress the **CONTROL** or
**LOCATE** pushbutton. 7. Depress **SINGLE CYCLE** and check for
**ACCEPT** response. 8. Depress the **START** pushbutton and the **STOP**.

There is also an **INITIAL LOAD PROCEDURE** (printed p.2):

> The program can be loaded by normal IPL procedure. If IPL is
> inoperative, the following can be used:
> 1. By BX manipulation, place the following CW in a main memory location
>    not used by the program. — Data Word Address - SLC Value; Word Count
>    - As shown in the program listing; Refill - 0; **Chain flag - 0,
>    Multiple flag - 1**
> 2. Read by executing the CW in the location in which it was stored by
>    step 1.

### 2.3 What this means for the model

Everything in §2.2 is a *testbench* operation, not a program operation.
Writing a control word into a named channel's Exchange Storage, clearing
ES, selecting a channel, single-stepping the Exchange one cycle, reading
back the control word and checking its count/address/status — those are
method calls on a modelled `mkExchange`, and the model would have to
expose them anyway for any kind of testing.

The hard requirement is not the operator. **It is the devices.** BX-0's
success criterion is almost always a printed line, a punched card, a tape
record, or a console display. Running it therefore needs modelled
behavioural devices: chain printer (with carriage control and suppress
post-spacing), card reader, card punch (with and without ECC mode), 729
tape (with backspace, backspace-file, space-file and tape marks), and the
operator's console display and typewriter.

That is a real cost, but it is a cost the project owes anyway — `MCP`
cannot run without them — and the devices are *behavioural*, not
cycle-accurate. The Exchange side is where the timing contract lives.

**Verdict on requirement: BX-0 can be run against a modelled Exchange
with modelled devices.** It cannot be run the way a `jb_ax5b` block is
run, because there is no instruction stream to feed the CPU; it must be
driven from the testbench. It needs no analogue hardware: it is not a
marginal-timing test, there are no scope-and-probe procedures, and the
one explicitly analogue instruction in the corpus — "Turn Marginal Check
Pots to OFF" — appears in the *acceptance-test* document (§7), not here.

---

## 3. Document structure and page spans

### `ka_ex1_bx-0.pdf` — 78 PDF pages

| PDF pp. | Layout | Content |
|---|---|---|
| 1 | 2-up | Cover; Table of Contents |
| 2 | 2-up | printed 1-2: PURPOSE; EQUIPMENT REQUIREMENTS; §3 MODE OF CONTROL; Initial Load Procedure; Overall Procedure A (steps 1-4) |
| 3 | 2-up | printed 3-4: A (steps 5-15); B Control or Locate Operations; **III. INDIVIDUAL TEST PROCEDURE AND OUTPUT**; A. Chain Printer Tests PRT 1-4A |
| 4 | 2-up | printed 5-6: PRT 5-9; B. Card Reader Tests 1-7; C. Tape Unit Tests |
| 5 | 2-up | printed 7-8: Tape Tests 1-5; D. Operator's Console Tests, Test 1 |
| 6 | 2-up | printed 9-10: console tests (**not read this pass**) |
| 7 | 2-up | printed 11-12: console Tests 8-9; Typewriter Tests; **E. Card Punch Tests**, punch format tables |
| 8 | 2-up | printed 13-14: Card Punch Test Procedure; 3.1.2 Success / 3.1.3 Failure Indications; **3.1.4 Supplementary Information — the STRAP control-word table** |
| 9 | 2-up | printed 15: Explanation of File Numbers; §4 PROGRAM PHILOSOPHY — and **Figure 1, PROGRAM SUMMARY** |
| 10 | — | not read this pass |
| **11 - ~68** | **1-up fanfold** | **Main BX-0 STRAP assembly.** Opens `PRNID,BX0 - BASIC EXCHANGE OFF LINE MAINTENANCE-E.W.JOHNSON`. Locations `100000.00` upward |
| **~69 - 78** | **1-up fanfold** | **Second STRAP assembly, `PUNFUL`** — the punched card test deck itself. Locations `000100.00` → `000536.40`, closing `END,64.0` |

Octal location sampled against PDF page, to calibrate any transcription
brief:

| PDF p. | Location range | Section |
|---|---|---|
| 13 | `100000.00` - `100015.00` | printer control words, PRT1-PRT9 |
| 20 | ~`100307.00` - `100312.00` | card reader control words, CARD16-CARD19 |
| 30 | `101106.00` - `101137.00` | tape test print records, RCRD12-RCRD16 |
| 40 | `101456.00` - `101676.00` | typewriter reserved areas, TYPR1-TYPR14 |
| 50 | `102125.30` - `102135.10` | `BLACK ALPHABET` character data |
| 60 | `102363.00` - `102445.00` | card punch ECC-mode control words, PCH6 |
| 70 | `000100.00` - `000131.00` | `PUNFUL` — CARD1, CARD2 |
| 78 | `000535.00` - `000536.40` | `PUNFUL` — `@CRD 19 IDENT`, `NOP`, `END,64.0` |

The `PUNFUL` assembly is worth calling out. Its own comment block,
PDF p.70, verbatim:

> `SLC VALUE IS MEANINGLESS`
> `PUNFUL`
> `@ THIS IS TEST PATTERN DECK 1. RESULTS CAN BE`
> `@ EASILY DETERMINED BY USING CHKRDR CONTROL WORD`
> `@ SEQUENCE,AND/OR DATA DISPLAY.`
> `@ A SECOND PATTERN DECK WILL BE MADE AVAILABLE`
> `@ WHICH CONTAINS SPECIAL PATTERN CARDS.CHECKS ARE`
> `@ MADE BY DISPLAYING MEMORY.USE TEST DECK 2 IF`
> `@ PRINTER OPERATION IS DOUBTFUL.....`

This is the *content of the physical card deck* that the card reader test
requires. **The model does not need the cards; it has their bit patterns.**
That removes the one requirement in §2 that could not otherwise be met —
"Place reader test deck in card reader" (printed p.5) — because the deck
is in the PDF, assembled, with locations printed.

### `ka_ex1b_bx-0.pdf` — 66 PDF pages

Same writeup on PDF pp.1-10 (cover and TOC verified identical). Listing
from PDF p.11 in the same one-up fanfold format, the 48-BCD build
(**KA EX1B**), assembling in the `05xxxx` range.

It has **no second assembly**. Its last page, PDF p.66, closes the main
program directly:

```
PRES22   DR%BU,64,8¤,13                               15.00      053403.00
PRES23   DR%BU,64,8¤,13                               15.00      053420.00
END      DR%BU,64,8¤,1                                 1.00      053435.00
         END,START                                 50000.00      053436.00
```

Note `END` used here as an ordinary symbol on a one-word reserve,
immediately before the `END,START` pseudo-op — a transcription trap worth
recording. The `50000.00` in the machine-code column is the entry point,
confirming the file-number table's "Starting Location 50,000" for EX1B.

The same page also shows the punch read-in areas (`PRES3`…`PRES23`) with
their ECC / non-ECC distinction annotated in the comment column
(`-READ-IN AREA`, `-READ-IN AREA-ECC`, `-NON-ECC MODE`), which is useful
for sizing the punch test's buffers.

---

## 4. The printed assembly listing — the encoding oracle

**Yes, there is a printed assembly listing with the column structure this
project transcribes.** It is the headline finding.

### 4.1 Column structure

The fanfold listing is wide (17″ landscape). Left to right:

`symbol` · `operation and operands` · `@comment` · **`machine code`** · **`location`**

A representative block, PDF p.13, the first control words of the program,
read at 400 dpi in two crops and reassembled:

```
START    NOP                            @START OF TEST                 0.30 00                       100000.00
         NOP                            @PRINTER SECTION               0.30 00                       100000.40
PRT1     CW%CR¤,LINE1,17,0              @EXECUTE THIS CONTROL TO TEST   100016.00 00 000420.00 00    100001.00
PRT2     CW%CD¤,LINE2,51,0              @MF TEST- ALL CHARACTER PRINT.  100037.00 20 001460.00 00    100002.00
PRT3     CW%CD¤,LINE3,31,0              @MF TEST,END CODE TEST-         100122.00 20 000760.00 00    100003.00
PRT4     CW%CR¤,BXWC1,1,0               @BX WORD COUNT -1- TEST.-       100161.00 00 000020.00 00    100004.00
PRT4A    CW%CR¤,BXWC2,2,0               @BX WORD COUNT -2- TEST.        100163.00 00 000040.00 00    100005.00
PRT5     CW%CDSC¤,LINE1,17,$&1.         @CHAIN FLAG/MULTIPLE FLAG TEST  100016.00 60 000422.00 07    100006.00
         CW%CDSC¤,LINE2,51,$&1.         @DO ALL ABOVE FUNCTIONS         100037.00 60 001462.00 08    100007.00
         CW%CDSC¤,LINE3,31,$&1.         @WITH CF AND MF SET 1           100122.00 60 000762.00 09    100010.00
         CW%CDSC¤,BXWC1,1,PRT4A                                         100161.00 60 000022.00 05    100011.00
```

(The `¤` is this project's convention for the STRAP field separator; see
`docs/listing_typography.md`.)

### 4.2 It is self-consistent, and checkable now

Two relationships fall out of the sample above without any further
reading, and both can be checked against `exchange_and_io.md` §3.2
immediately:

**The flag field.** The second machine-code group is the flag byte:

| Mnemonic | Skip | Mult | Chain | Printed flag byte |
|---|---|---|---|---|
| `CR` | 0 | 0 | 0 | `00` |
| `CD` | 0 | 1 | 0 | `20` |
| `CCR` | 0 | 0 | 1 | `40` *(PDF p.60)* |
| `CDSC` | 0 | 1 | 1 | `60` |

So, in this field's octal rendering, **multiple = 20, chain = 40**, and
they add. `CCR`'s `40` comes from the card-punch section on PDF p.60
(`CW%CCR¤,PWD6,8,$&1.` → `102603.00 40 000202.04 F4`), which is an
independent witness on a different page.

**The count field.** The third machine-code group is the word count, and
it equals **count × 16 + 2 if the chain flag is set**, printed in octal.
Fourteen samples, drawn from PDF pp.13, 20 and 60, with no exceptions:

| Source count | Chain | Printed | Check (count×16 + 2·chain, octal) |
|---|---|---|---|
| 1 | 0 | `000020` | 16 → `000020` |
| 2 | 0 | `000040` | 32 → `000040` |
| 15 | 0 | `000360` | 240 → `000360` *(p.20)* |
| 17 | 0 | `000420` | 272 → `000420` |
| 31 | 0 | `000760` | 496 → `000760` |
| 51 | 0 | `001460` | 816 → `001460` |
| 130 | 0 | `004040` | 2080 → `004040` *(p.60)* |
| 1 | 1 | `000022` | 16+2 → `000022` |
| 5 | 1 | `000122` | 80+2 → `000122` *(p.60)* |
| 8 | 1 | `000202` | 128+2 → `000202` *(p.60)* |
| 15 | 1 | `000362` | 240+2 → `000362` *(p.20)* |
| 17 | 1 | `000422` | 272+2 → `000422` |
| 31 | 1 | `000762` | 496+2 → `000762` |
| 51 | 1 | `001462` | 816+2 → `001462` |

The chain flag therefore appears **twice** in the printed rendering —
once in the flag group (`40`) and once as the low bit of the count group
(`+2`). The natural reading is that these are two different renderings of
overlapping bit ranges of the same 64-bit word, the count group running
far enough down the word to catch the chain bit. **That is an inference,
not a source statement**, and it is the sort of thing the Reference
Manual's bit-level control-word diagram would settle.

**The refill field.** The fourth group is the **low byte of the refill
target address, in hexadecimal**. Nine samples, all exact:

| Source refill | Resolves to (octal) | Low byte | Printed |
|---|---|---|---|
| `$&1.` at `100006` | `100007` | `07` | `07` |
| `$&1.` at `100007` | `100010` | `08` | `08` |
| `$&1.` at `100010` | `100011` | `09` | `09` |
| `PRT4A` | `100005` | `05` | `05` |
| `$` at `100012` | `100012` | `0A` | `0A` |
| `$` at `100013` | `100013` | `0B` | `0B` |
| `$` at `100014` | `100014` | `0C` | `0C` |
| `$` at `100015` | `100015` | `0D` | `0D` |
| `$&1.` at `102363` | `102364` | `F4` | `F4` *(p.60)* |

That also explains the `F4, F5, F6 … FF, 00, 01 …` run down PDF p.60: it
is the low byte of a block of consecutive control-word addresses rolling
over, not a counter.

So **all four printed groups are decoded**: data word address, flag byte,
count (+chain bit), and refill low byte. Only the `.NN` suffix that STRAP
appends to the address-style groups (`000202.04`, `000322.05`) is left
undecoded; it is the bit-offset part of STRAP's `word.bit` address
notation and varies with the refill's high bits.

This is the property that makes the listing an oracle in the AGENTS.md
rule-3 sense: **a STRAP assembler that implements the `CW` pseudo-op can
be checked against IBM's own output, bit by bit, with
`listing_oracle.py`, before anything is executed at all.** No Exchange
model is needed to collect that win.

### 4.3 The mnemonic table, from the document itself

PDF p.8 (printed p.14), §3.1.4 *Supplementary Information*, I *Strap Code
Control Word Format*. This is a **primary-source assembler table** and is
transcribed here in full because it is short, load-bearing, and feeds
`strap/` directly:

> The format for a Strap Coded Control Word is as follows:
> **`CW(OP), Data Word Address, Word Count, Refill`**, where 'OP' is
> coded as in the table below:

| OP | Skip Flag | Multiple Flag | Chain Flag | Operation |
|---|---|---|---|---|
| `CR` | 0 | 0 | 0 | Count Within Record |
| `CCR` | 0 | 0 | 1 | Chain Counts Within Record |
| `CD` | 0 | 1 | 0 | Count Disregarding Record |
| `CDSC` | 0 | 1 | 1 | Count Disregarding Record, Skip and Chain |
| `SCR` | 1 | 0 | 0 | Skip, Count Within Record |
| `SCCR` | 1 | 0 | 1 | Skip, Chain Counts Within Record |
| `SCD` | 1 | 1 | 0 | Skip, Count Disregarding Record |
| `SCDSC` | 1 | 1 | 1 | Skip, Count Disregarding Record, Skip and Chain |

All eight (skip, multiple, chain) combinations have a name, and the names
are the ones used throughout the listing.

### 4.4 Other statement types in the listing

Beyond `CW`, the listing uses the ordinary STRAP data pseudo-ops, which
the assembler already handles or nearly does:

- `%8¤DD%BU,8,8¤,000` — an 8-bit byte constant (print control byte).
- `% AZ¤DD%BU,8,8¤,TEXT…Z` — alphanumeric text, `Z`-terminated. These
  carry a location but **no printed machine code**, so they are an oracle
  for address progression and field length, not for character encoding.
- `%16¤DD%BU,8,8¤,2C,2D,2E,…` — hexadecimal byte lists (the
  `BLACK ALPHABET` and ECC character tables, PDF p.50). **These do carry
  a printed per-byte octal column**, so they *are* a character-encoding
  oracle.
- `DR%BU,64,8¤,n` — reserve *n* 64-bit words; prints its length.
- `SLC,64,0`, `NOP`, `END,64.0`.

---

## 5. The test map

Section III, *INDIVIDUAL TEST PROCEDURE AND OUTPUT*, runs from printed
p.4 to printed p.13 and is organised by device, lettered A-E. Banners
verbatim.

### A. Chain Printer Tests — printed pp.4-5

Note: "Chain Printer" is the *device* (a chain-train line printer), not
the chain flag. Verbatim:

> **PRT 1** operates with chain, multiple, and skip flags zero. Printout is:
> `THIS LINE OF PRINT CHECKS THE ABILITY TO PRINT.   AB -- YZ12-90%./- #$&*%`
>
> **PRT 2** operates with multiple flag only set. Printout is an all
> character print, three lines, each identified. Failure will cause only
> one line to be printed.
>
> **PRT 3** operates with multiple flag set and tests the ability to
> recognize end codes. Printout is three lines each identified. On
> failure - All data will be on one line.
>
> **PRT 4** tests BX for word count of 1. Printout is WDCT 1- for sucess
> WDCT 1 FAILURE - on failure
>
> **PRT 4A** tests BX for word count of 2. The printout is: WORD COUNT 2
> - On success WORD COUNT 2 FAILURE - on failure.
>
> **PRT 5** operates with multiple and chain flags set. Printout is all
> data from the above tests, a total of 109 64-bit words.
>
> **PRT 6** is a scoping loop which prints the all character print data.
>
> **PRT 7** is a scoping loop which prints the end code print data.
>
> **PRT 8** is a Suppress Post Spacing test loop. It will suppress post
> spacing 4 times in each line. For success, all data will be on one
> line, with normal spacing.
> `PRT 8 - NOW IS A SUPPRESS POST SPACING TEST LOOP.`
>
> **PRT 9** is a test of the Select Report functions. It prints according
> to the Select Report key depressed. If no Select Report keys are
> depressed all of the select report data will be printed. The test
> operates in a continuous loop.
> `PRT 9 - THIS LINE SHOULD BE PRINTED IF SELECT REPORT 'a' IS DEPRESSED.`

### B. Card Reader Tests — printed pp.5-6

> Place reader test deck in card reader and make reader ready. The test
> deck is numbered octally in column 80. … The first test operates with
> skip, chain, and multiple flags set. The sequence of data is as follows:

| # | Banner, verbatim |
|---|---|
| 1 | **One Card Read.** `CARD 1 ..... FIRST CARD READ ... DATA IS IN IQS FORMAT. WORD COUNT ON READ WAS 15. READER PATTERNS IN LATER TEST` |
| 2 | **Word Count 1 Test.** On success - `WDCT1` On failure - `WDCT 1 FAILURE IF THIS PRINTS OR IS IN MEMORY  WD CNT-1 was not handled by BX .....` |
| 3 | **Word Count 2 Test.** On success - `WORD COUNT - 2` - On failure - `WORD COUNT - 2 - FAILURE` |
| 4 | **Skip Flag Test.** On success - `THIS IS THE SKIP READ AREA ..... CARD 4 - SKIP FLAG TEST` On failure - `IF THIS PRINTS SKIP FLAG FAILED.` |
| 5 | **Multiple Flag Test** - 3 cards read. Lines of print begin `CARD 5 / CARD 6 / CARD 7`. "If only one card reads, MF failed and remainder of test will be out of sequence." |
| 6 | **Long Read Test** - 10 cards read. Lines begin `CARD 8` … `CARD 17` |
| 7 | **Chain Flag Only Test.** For success - `CARD 18. TWO CARD READ WITH MF-0. ONLY ONE CARD SHOULD READ ....` On failure - `THIS CARD SHOULD NOT BE READ CARD 19` |

### C. Tape Unit Tests — printed pp.6-7

> Execute the control words and control instructions at the proper time
> by following the program listing. … Since most tape operations require
> control conditions such as rewind, backspace, etc., the tape test
> requires that the operator perform these operations from BX following
> the program listing. Many of the tests are designed specifically to
> test a particular control function and, therefore, must be run as
> specified by the program listing. Correct operation is evidenced by the
> correct printout as shown under the description of each of the five
> tests.

| # | Banner, verbatim |
|---|---|
| 1 | **Simple Data and Rewind.** Check read-in area manually. Data: "An all 1's 8-bit byte shifts left continuously until an all 0's word is reached. Following this an all 1's word, a 101010 word, and a 010101 word." |
| 2 | **Data and backspace test.** Success: `TEST 2. DATA AND BACKSPACE TEST THIS IS RECORD 1 - TEST TWO .... 10 WORDS, CDSC...` / `TEST 2. RECORD 2 - 15 WORDS, CDSC .. DATA FOLLOWS --- AB ... YZ01 ... 89 -------- RECORD 3 IS BKSP TEST.` / `TEST 2. BACKSPACE WORKED IF THIS LINE 3` / `TEST 2. TEST 2 RECORD 4.  10 WORDS CR. XXXXXXXXXXX`. Failure: `IF THIS PRINTS, BACKSPACE FAILED ..` |
| 3 | **Tape Mark Recognition Test.** Success: `TAPE MARK RECOGNITION RECORD 1.` Failure: `IF THIS PRINTS, TAPE MARK FAILED.` |
| 4 | **Backspace file test.** Success: `TEST 4. BACKSPACE FILE TEST TEST 4. BACKSPACE FILE TEST PASSED......` Failure: `TEST 4. BACKSPACE FILE FAILED.` |
| 5 | **Space File Test.** Success: `TEST 5.  SPACE FILE TEST PASSED.` Failure: `SPACE FILE, TEST 5.  FAILED. XXXXXXXXXXXX` |

Followed by, verbatim:

> Also included is a sequence of control words which reproduce the
> program on tape. The tape can then be loaded by IPL procedure.

### D. Operator's Console Tests — printed pp.7-11

> In the operator's console tests the following is provided.
> 1. Constants for writing on the console display and typewriter.
> 2. Reserved locations for reading the console switches and typewriter.
> 3. Extended typewriter write operations tests.

> **Test 1 and 2. Write Operation.** 1. Execute the control words - write
> having the console channel selected. 2. After each control word is
> executed, check the display for the data indicated.
>
> **Test 1.** Chain, multiple and skip flags zero.
> Word one - 1. Byte number word which numbers the 8-bit bytes left to
> right 0-7. 2. All 1's word 3. All 0's word 4. Alternate 1's and 0's
> 8 bit bytes.

Printed pp.9-10 (PDF p.6) carry Tests 3-7 and were **not read this
pass**. Printed p.11 (PDF p.7) resumes:

> **Test 8. Chain and multiple flags set.**
> 1. Read 40 characters, no flags set.
> 2. Read 40 characters, chain, read 32 more.
> 3. Read 8 words multiple flag mode.
> 4. Read 25 words with multiple flag set.
> 5. Read 10 words with the multiple flag set, chain, read 8 more words.
>
> **Test 9. Chain, multiple and skip flags set.**
> 1. Skip 5 words, read 3 with chain flag only set.
> 2. Skip 4 words in multiple block mode, chain, read 5 more words.
>
> In the read tests with the multiple flag set, and an end code is
> entered, the next three words will be read from the console switches.

> **Typewriter Tests**
> 1. Backspace test loop. Loops and types - `This is a BACKSPACE test.`
> 2. Ripple test. Types 26 lines upper case letters.
> 3. All character ball movement test. Loops and types all characters.

### E. Card Punch Tests — printed pp.11-13

> Tables of punch formats for checking pattern cards.
> 1. Non ECC-Mode, 15 words per card - Starting bit position. *(15-row
>    Word/Column/Row table)*
> 2. ECC Mode, 13 words per card. All words begin with the C-bits in
>    Row 12. *(13-row Word/Column table)*
> 3. Table of bits on which the ECC bits are based. *(C-0, C-1, C2, C-4,
>    C-8, C-16, C-32 → data bit lists; `C-T is based on overall parity
>    including ECC bits.`)*

> **Card Punch Test Procedure** — 1. Make card punch ready. 2. Execute the
> control words with a write instruction to the card punch. 3. Examine the
> cards if in the pattern tests, or if in the extended tests use the
> control words provided for the card reader and printer to check the data.
>
> **Test 1. Punch Pattern Cards.** Non ECC Mode - Punches a diagonal
> pattern from Column 1, Row 12, to Column 12, Row 9, a total of 13 cards
> punched. ECC Mode - 1. Punch 9 cards and floats a '1' in the C-bits.
> 2. Punch 9 cards and floats a '0' in the C-bits.
>
> **Test 2. Extended Punch Tests.** This test uses printer data and the
> card reader and chain printer for checking. Each test card is identified
> with an octal number in the last column.

§3.1.2 and §3.1.3 (printed p.13) add nothing: "The success indications
are indicated in the detailed test procedure." / "The failure indications
are listed in the detailed test procedure."

### Figure 1, PROGRAM SUMMARY (PDF p.9)

> PROGRAMS OBSOLETED — None.
> FUNCTION — To test the data paths to and from the I/O units and to and
> from main memory independent of CPU.
> BASIC CONTROLS — Controlled manually from the BX console.
> MANUAL INTERVENTIONS — Not applicable.
> SUCCESS INDICATIONS — Correct data in memory, and correct printouts.
> FAILURE INDICATIONS — Failure printouts and incorrect data in main memory.

---

## 6. Figure 36 coverage, and the disk

### 6.1 Against `exchange_and_io.md` §3.3

`exchange_and_io.md` reproduces Reference Manual Figure 36 — the sixteen
rows of (Multiple, Chain, Count, End-of-Block) → action — and notes that
14 of the 16 are untested by anything this project has.

**BX-0 reaches all four (Multiple, Chain) quadrants**, each by name, and
on more than one device:

| Multiple | Chain | Mnemonic | Where BX-0 exercises it |
|---|---|---|---|
| 0 | 0 | `CR` | PRT 1, PRT 4, PRT 4A; Card Reader "no flags set" (Test 8.1); Console Test 1 |
| 1 | 0 | `CD` | PRT 2 (multiple only), PRT 3 (multiple + end codes); Card Reader Multiple Flag Test (5) and Long Read Test (6); Console Test 8.3, 8.4 |
| 0 | 1 | `CCR` | **Card Reader Chain Flag Only Test (7)** — "TWO CARD READ WITH MF-0. ONLY ONE CARD SHOULD READ"; Console Test 8.2, 9.1; card punch PCH6 (PDF p.60) |
| 1 | 1 | `CDSC` | PRT 5; Card Reader first test; Console Test 8.5; Tape Tests 2 and 4; punch extended tests |

Skip is covered independently by `SCR`/`SCD`/`SCDSC`: Card Reader Skip
Flag Test (4), Console Test 9.1 and 9.2.

**Honest limit.** The *count-zero* and *end-of-block* axes of Figure 36
are not separately named in the test banners, so this pass cannot say
which of the sixteen individual rows are hit. What can be said is that
the test design is explicitly a walk across the flag space — PROGRAM
PHILOSOPHY says "All tests start with the simplest control words and
proceed to include the chain, multiple and skip flags" — and that two
rows which are *structurally hard to reach any other way* are named
outright:

- **Chain with multiple off** (rows `0,1,*,*`) — Card Reader test 7 and
  Console test 8.2/9.1 are explicitly this case.
- **Count exhausted at a word count of exactly 1 and exactly 2** (the
  `count → 0` transition) — PRT 4, PRT 4A and Card Reader tests 2 and 3,
  all with named success and failure strings.

Determining the exact Figure 36 row set needs the transcription. That is
a reasonable thing to commission; it is not a reason to doubt the value.

### 6.2 The disk — it is not here

Asked because MCP needs the disk and the model has nothing for it.

**Neither deck exercises the disk or the 7612 Disk Synchronizer.**
Three independent confirmations:

1. §2.1 *Testing Requirements* (printed p.1): the **Disc** cell is
   **blank** while Punch, Printer and Tapes all carry `N`.
2. §2.2 *Buffer Equipment Requirements* (printed p.1): a two-cell table,
   **Disc** and **Tapes**, **both blank**.
3. Section III is lettered **A** Chain Printer, **B** Card Reader,
   **C** Tape Unit, **D** Operator's Console, **E** Card Punch, and then
   §3.1.2 begins. There is no disk section and no letter **F**.

This is consistent with `exchange_and_io.md` §1.4, "The disk is *not* on
the Exchange" — a BX-only off-line test would have no way to reach it.

**So the disk still has no oracle of any kind in this repo.** That is
unchanged by this pass and remains the binding constraint on MCP.

---

## 7. What BX-0 does *not* cover, and the documents that would

BX-0 says it in its own words (PROGRAM PHILOSOPHY, printed p.15): "does
not test communication paths to and from CPU **or all of the control
functions**."

Concretely, BX-0 gives no evidence about:

- `RD` / `WR` / `CTL` / `LOC` / `REL` / `SEOP` instruction semantics.
- Acceptance latency, the reject path, and the "a few microseconds"
  wait (`exchange_and_io.md` open question 3).
- The channel indicators and the per-instruction response summary
  (Figure 40, `exchange_and_io.md` §3.8-3.9).
- Interrupt delivery to the CPU.
- IPL as executed by the CPU — BX-0 describes IPL only as a *loading*
  method for itself, and gives a by-hand fallback.
- Memory-cycle contention between the Exchange and the CPU — the whole
  of `exchange_and_io.md` §4. BX-0 runs while the CPU is doing something
  else, but it never checks what that costs.

### 7.1 The documents that would cover it — named, and missing

`docs/7030_SystemTestPrograms_Aug61.pdf` (46 pp., the acceptance-test
schedule, August 1961) carries a **PROGRAM LIST** on its printed pp.1-2
(PDF pp.6-7) giving each diagnostic's maintenance-switch sequence number
and the equipment it tests. Transcribed in full, since it is the map:

| Program | Maint. Sw. Seq. No. | Equipment Tested | In `docs/`? |
|---|---|---|---|
| JA AX1 | 0 | I-Box | ✅ `ja_ax1a_ibox-1.pdf` |
| JA UA1 | 1 | SSIP-Utility Routines | ✅ `ja_ua1_ssip.pdf` |
| JB AX2 | 2 | I-Box | ✅ |
| JB AX3 | 3 | I-Box | ✅ |
| JB AX4 | 4 | I-Box | ✅ |
| JB AX5 | 5 | I-Box | ✅ |
| JB AF1C | 6 | Floating Point Circuitry | ✅ |
| JB AV1C | 7 | Variable Field Length Cktry | ❌ |
| KA BT1 | 8 | Mem Timer | ❌ |
| KA AT1 | 9 | Raw Speed 1 | ❌ |
| JB AC1 | 10 | I-Box, I-Checker | ❌ |
| JA BM6A | 11 | Memory Addressing | ✅ |
| JA BB6B | 12 | Memory Worst Pattern | ✅ |
| **JA CE2** | 13 | **Tape 7 (All Channels)** | ❌ |
| **JA EE3** | 14 | **BX/TAPE** | ❌ |
| JA NE6 | 15 | Punch | ❌ |
| JA NE5 | 16 | Reader | ❌ |
| **JA NE4** | 17 | **Printer/BX** | ❌ |
| **JA ES1D** | 18 | **I/O Single Channel (Operators Console)** | ❌ |
| **JA CE1** | 19 | **Tape 0-6** | ❌ |
| JA AT1 | — | Basic Timing Test (Livermore) | ❌ |
| KA SS1 | — | SEVA-Systems | ❌ |

Two things follow.

**First, BX-0 (KA EX1) is not on this list at all.** It is not part of the
acceptance-test tape sequence, because it is not a tape-loaded,
SSIP-controlled, CPU-resident diagnostic. That independently corroborates
§1.1 from a second primary source.

**Second, the CPU-side Exchange diagnostics exist and are named.**
`JA EE3` ("BX/TAPE"), `JA NE4` ("Printer/BX") and `JA ES1D` ("I/O Single
Channel") are, by their position in this list, exactly the `jb_ax5b`
class: tape-loaded, maintenance-switch-sequenced, SSIP-framework programs
that run on the CPU. Those would be the runnable deck oracles for the
CPU↔Exchange instruction interface. **None of them is in `docs/`.**

The same document also confirms the BX maintenance console as a distinct
unit alongside the CPU's (printed p.2, §3.1 *Initial Setups*):

> **CPU Maintenance Console** — 1. Set to Maintenance Mode 2. Set to
> Normal all other switches 3. Turn Marginal Check Pots to OFF
> **BX Maintenance Console** — 1. Set Mode Select Rotary Switch to Normal
> 2. Set to Normal all other switches 3. Turn Marginal Check Pots to OFF
> **Power Distribution Frame** — 1. Set all Memory Control Switches to
> Normal 2. Turn Marginal Check Pots to OFF
> **Peripheral Equipment** — 1. Setup for Normal Operation.

---

## 8. A partial answer to `exchange_and_io.md` open question 4

Open question 4 of `exchange_and_io.md` reads: "There is no 7619 CE manual
in `docs/`. … The register list at Perf. Char. p.A-9 is the deepest
internal view available here."

BX-0's operating procedure is deeper than that in one specific respect:
it is a **control inventory of the BX maintenance console**, which is a
view into the 7619's own state. Everything below is named verbatim in the
procedure (printed pp.2-4), and each implies a piece of Exchange state:

| Control | What it implies about the 7619 |
|---|---|
| **BX mode switch** — TEST MODE / (Normal) | A maintenance mode distinct from normal operation |
| **"Type of Test"** — `EX MEM` / `Main Memory UNIT` / `UNIT TEST` | Three distinct operation classes the console can initiate |
| **EXCHANGE MEMORY ADDRESS switch register**, with **bit 128 = Control Word Memory**, parity ODD with it set and EVEN with it clear | ES is addressed by *channel number plus a bit selecting control-word vs data space* — matching `exchange_and_io.md`'s "one control word and two data words per channel" — and the address register is **parity-checked** |
| **LOAD MEMORY** switch | A console write path into ES |
| **CLEAR MEMORY** pushbutton | A bulk ES clear |
| **SINGLE CYCLE** pushbutton | The Exchange can be stepped one cycle at a time; two depressions complete an ES write (step 7) |
| **REFILL ADDRESS** of the panel keys | The refill (chain) address is a console-settable field |
| **BLOCK CHANNEL switches** | Per-channel inhibit, independent of the channel's own state |
| **data word transfer**, **service request**, **channel signal simulation** switches | The console can *simulate the device side* of the channel interface — i.e. the 7619 has injectable stimulus at the channel boundary |
| **READ / WRITE pushbuttons** | Console-initiated equivalents of the CPU's `RD`/`WR` |
| **CONTROL / LOCATE pushbuttons** with **C₀-C_t panel switches** | Console-initiated `CTL`/`LOC` with a settable function-code/locate-number field, named `C₀`…`C_t` |
| **ACCEPT response** | The accept/reject handshake is observable at the console, one cycle after the operation is keyed |
| **START / STOP** | Free-running vs stopped Exchange |
| **Mode Select Rotary Switch**, **Marginal Check Pots** *(from the acceptance-test doc, §7.1)* | A multi-position mode selector, and analogue marginal-check — which BX-0 itself never uses |

This does not replace a 7619 CE manual. It does establish the console's
*functional* interface, and — more usefully for `bsv/` — it is a list of
the methods a modelled `mkExchange` would need to expose in order to be
testable at all. They are the same methods BX-0 needs.

---

## 9. Verdict

**The Exchange does have an oracle. It is not the oracle the brief was
looking for, and it is in some ways a better one.**

Stated precisely, so it can be acted on:

1. **BX-0 is not a runnable deck in the `jb_ax5b` sense and never will
   be.** It is an off-line, manually-operated exchange maintenance
   procedure plus the control-word and data tables it operates on. There
   is no instruction stream. Printed p.2 and PROGRAM PHILOSOPHY both say
   so, and the acceptance-test schedule corroborates by omitting it.

2. **BX-0 *is* a bit-exact encoding oracle for the Exchange control
   word, available immediately and cheaply.** PDF pp.11-78 are an
   unbroken STRAP listing with IBM's own printed machine-code and
   location columns. All four printed groups decode, and the decoding was
   checked mechanically rather than by eye: the flag byte
   (multiple = 20, chain = 40, octal, additive) on 4 samples, the count
   group (count × 16 + 2·chain) on 14 samples, and the refill byte (low
   byte of the target address, hex) on 9 samples — drawn from PDF pp.13,
   20 and 60, sheets 47 apart, with no exceptions. This is consumable by
   `listing_oracle.py` with **no Exchange model at all** — it tests the
   assembler, and through the assembler it pins the control-word format
   that `exchange_and_io.md` §3.2 reconstructs from the Reference Manual.
   That makes it a cross-check on the manual, which is exactly what
   rule 4 wants.

   Two honest limits on this claim. **Only four of the eight (skip,
   multiple, chain) combinations were observed in the machine-code
   column** — `CR`, `CD`, `CCR` and `CDSC`, all with skip = 0. The other
   four are named in the §3.1.4 table and are implied by the Skip Flag
   Test and Console Test 9, so skip-set control words are almost
   certainly in the listing, but this pass did not land on a page
   carrying one. And **the number of control words in the listing was not
   counted**; the sampled pages carry between 4 and 40 apiece across
   roughly 58 sheets, which is the most that should be said without
   counting them.

3. **BX-0 *is* a behavioural test-vector oracle for the Exchange's
   data-transfer core.** About forty named tests, each fixing a flag
   setting and a word count and stating the expected device output
   verbatim, across five devices. Every operator action it demands —
   write ES, clear ES, select a channel, single-cycle, read back the
   control word and check count/address/status, simulate a service
   request — is a testbench method. The one physical requirement that
   looked blocking, the punched reader test deck, is **in the PDF**: the
   `PUNFUL` assembly on PDF pp.~69-78 is the deck's bit image with
   printed locations.

4. **The cost is the devices, not the Exchange.** Running BX-0 against
   the model needs behavioural models of the chain printer, card reader,
   card punch, 729 tape and operator's console. That work is owed to MCP
   regardless. It does not need cycle accuracy, and it does not need any
   analogue hardware.

5. **The disk is absent, and that is now confirmed rather than assumed.**
   MCP's disk requirement has no oracle anywhere in this repo.

6. **The real gap is the CPU↔Exchange instruction interface, and the
   documents that would close it are named.** `JA EE3` (BX/TAPE),
   `JA NE4` (Printer/BX) and `JA ES1D` (I/O Single Channel), from the
   acceptance-test schedule's own program list, are the `jb_ax5b`-class
   decks for the Exchange. **Acquiring them is a higher-value action than
   anything else identified in this pass.** Until then, `RD`/`WR`/`CTL`/
   `LOC`/`REL`/`SEOP`, acceptance, rejection, the indicators and
   interrupt delivery must be built to a manual-only standard — but the
   control word, the flag logic, the counting and the chaining need not
   be, because BX-0 covers them.

### Suggested next step, if the transcription is commissioned

Not the whole listing. The highest-value slice is **PDF pp.11-21** of
`ka_ex1_bx-0.pdf`, the printer and card-reader control-word sections
(locations `100000.00` to roughly `100312.00`). That is about ten
fanfold pages, it contains the PRT 1-9 and CARD 1-19 control words, it
spans all four observed (multiple, chain) quadrants, and every one of its
machine-code groups is printed.

Its value is **validating a `CW` pseudo-op in `strap/` against IBM's own
assembler** across a few hundred words rather than the handful decoded by
hand in §4.2 — not settling the field encodings, which §4.2 already
settles. A secondary payoff: it is the slice most likely to contain the
first skip-set (`SCR`/`SCD`/`SCDSC`) control words, which would close the
one coverage gap noted in §9.2.

---

## Appendix: what was *not* read in this pass

Stated as bounded negatives, in the style of `exchange_and_io.md` §7.

1. **PDF p.6 of `ka_ex1_bx-0.pdf`** (printed pp.9-10): Operator's Console
   Tests 3 through 7. The console test map in §5.D jumps from Test 1/2 to
   Test 8.
2. **PDF p.10** of the same file: the page between Figure 1 and the start
   of the listing. Probably blank or a continuation of Figure 1.
3. **The bulk of the listing.** PDF pp.11-78 were sampled at pp.11, 13,
   20, 30, 40, 50, 60, 70 and 78. The boundary between the main assembly
   and `PUNFUL` is between PDF p.60 and p.70 and was not pinned exactly.
4. **`ka_ex1b_bx-0.pdf`'s listing** beyond PDF pp.1, 2, 13 and 66. Its
   identity as KA EX1B is established from its location range and its
   closing `END,START` (§1.2); the body was not read line by line.
5. **Any control word with the skip flag set.** Four of the eight
   mnemonics were seen in the machine-code column; `SCR`, `SCCR`, `SCD`
   and `SCDSC` were not (§9.2).
6. **The number of control words in the listing.** Not counted.
7. **Why the count group carries the chain bit** (§4.2). The arithmetic
   is established on 14 samples; the bit-level reason was inferred, not
   chased into the Reference Manual's control-word diagram.
8. **The `.NN` bit-offset suffix** on the address-style machine-code
   groups (`000202.04`). Observed to vary with the refill's high bits;
   not decoded.
