# ATT92010 Hobbit execution times: Chapter 4 as data

Primary source: AT&T Microelectronics, *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual*, January 1993
(`ATT92010_Hobbit_Programmers_Reference_Jan93.pdf`), Chapter 4,
"Performance", printed pp. 4-1 to 4-7, and §2.6's Table 2-4 (p. 2-9,
§11 below). Printed page 4-N is PDF page
N + 110. Every number in `timing.csv` was read from the rendered page
image, not from the scan's OCR layer: `pdftotext` renders `1 + D` as
`1+0`, `5 + 2D` as `5+20`, `2·D` as `2.0`, `8·S` as `9.s` and
`8 + D + A` (KCALL) as `S+D+A`, so the
letters and digits of this chapter's cycle cells cannot be trusted
without the image. The images are authoritative.

`tools/check_timing.py` validates the CSV; run
`python3 hobbit/tools/check_timing.py` from anywhere. It exits 0 on the
delivered file and 1 on any violation. Its docstring records the exact
observed output for the two injected defects (one deleted row, one
blanked page cite).

## 1. The printed table numbers are 4-32 to 4-40

The chapter body says (printed p. 4-2):

> Listings of execution times for each instruction group are shown in
> Table 4-1 through Table 4-5. Delays are listed in Table 4-6 through
> Table 4-9.

The captions printed on the pages themselves are **Table 4-32** through
**Table 4-40**. This is not OCR: the rendered pages read "Table 4-32
Simple Instruction", "Table 4-33 Multi-Cycle Arithmetic Instructions",
"Table 4-34 DQM Instructions", and so on through "Table 4-40
Miscellaneous Delays". The printed sequence is exactly the body's
sequence plus 31. Keep both names: the body's names are what the
project and other documents cite; the printed captions are what a
reader turning to the page sees. `timing.csv` cites the printed
caption, `p. 4-3 Table 4-32`; the checker accepts either spelling and
maps them to the same table.

| body name | printed caption | printed page | contents |
|---|---|---|---|
| Table 4-1 | Table 4-32 | p. 4-3 | Simple Instruction (min/max) |
| Table 4-2 | Table 4-33 | p. 4-4 | Multi-Cycle Arithmetic Instructions (min/max) |
| Table 4-3 | Table 4-34 | p. 4-4 | DQM Instructions |
| Table 4-4 | Table 4-35 | p. 4-5 | Conditional Jump Instruction |
| Table 4-5 | Table 4-36 | p. 4-5 | Miscellaneous Instruction |
| Table 4-6 | Table 4-37 | p. 4-6 | Fetch and Empty Pipeline Delays |
| Table 4-7 | Table 4-38 | p. 4-6 | Operand Access Delays |
| Table 4-8 | Table 4-39 | p. 4-7 | Data Type Delays |
| Table 4-9 | Table 4-40 | p. 4-7 | Miscellaneous Delays |

Per instruction class, the page each number comes from is:

| class | page | table | rows in `timing.csv` |
|---|---|---|---|
| Simple | p. 4-3 | Table 4-32 | 38 |
| Multi-Cycle Arithmetic | p. 4-4 | Table 4-33 | 8 |
| DQM | p. 4-4 | Table 4-34 | 10 |
| Conditional Jump | p. 4-5 | Table 4-35 | 7 |
| Miscellaneous | p. 4-5 | Table 4-36 | 7 |
| Fetch and Empty Pipeline delays | p. 4-6 | Table 4-37 | 6 |
| Operand Access delays | p. 4-6 | Table 4-38 | 6 |
| Data Type delays | p. 4-7 | Table 4-39 | 2 |
| Miscellaneous delays | p. 4-7 | Table 4-40 | 3 |
| Address translation (MMU) | p. 2-9 | Table 2-4 | 13 |

Table 2-4 is not in Chapter 4: it is PRM §2.6, "MMU Performance"
(printed p. 2-9, PDF page 57), and is transcribed here because it is the
only other printed cycle table for the part (§11).

## 2. Assumptions (printed p. 4-1)

The base times are specified under four conditions, quoted from
section 4.1:

* "Instruction fetches must access in the instruction cache"
* "Only the stack offset, immediate, register, absolute (for jumps and
  calls only), or program counter relative addressing modes are used"
* "All stack offset accesses are captured in the stack cache"
* "No data hazards occur between instructions"

The same page adds: "There are some pipeline delays that may cause an
instruction to take longer to execute. These delays (see section 4-2)
should be added to the base execution time." Section 4.1 does not limit
which instruction groups may take which delays; the per-group notes on
pp. 4-3 to 4-5 do that (see §4 below).

## 3. Abbreviations (printed p. 4-2)

Printed verbatim, in the manual's order:

| symbol | meaning |
|---|---|
| IC | decoded instruction cache |
| PDU | prefetch and decode unit |
| A | memory access time for a single word access |
| D | memory access time for a double word access |
| Q | memory access time for a quad word access |
| M | memory |
| N | number of valid entries in the stack cache |
| SC | stack cache |
| E | ENTER size |
| EU | Execution unit |

`A`, `D`, `Q`, `N`, `E` and `S` may appear in the CSV's `time` column.
`S` is not in this list: see the errata in §7. `N` is defined but never
used by any table in Chapter 4. The checker's expression grammar is
exactly this symbol set plus `S`.

## 4. Which delays may be added

The group notes name the delay tables that can apply:

| group | printed sentence | page | permitted delays |
|---|---|---|---|
| Multi-Cycle Arithmetic | "the execution times ... are data dependent. For these instructions, instruction fetch, operand access and data type delays are possible" | p. 4-3 | Tables 4-37, 4-38, 4-39 |
| DQM | "For DQM type, instruction fetch delays are possible" | p. 4-4 | Table 4-37 |
| Conditional Jump | "fetch delays are possible if the branch is not folded" | p. 4-4 | Table 4-37 |
| Miscellaneous | "instruction fetch and miscellaneous delays are possible" | p. 4-5 | Tables 4-37, 4-40 |
| Simple | no group sentence; only the JMP and RETURN notes | p. 4-3 | not restricted by any p. 4-3 note; p. 4-1's blanket additivity rule applies |

Table 4-32's two notes are part of the timing, not commentary:

> Note that RETURNs are always indirect, do not add delay for
> indirection. If an unconditional jump is folded into the previous
> instruction, it takes no time to execute; otherwise, it takes one
> cycle. (p. 4-3)

So `RETURN` is 2 cycles and never takes a Table 4-38 indirection delay;
`JMP` is 0 when folded and 1 when not, which is why its row carries
min = 0 and max = 1.

## 5. How to cite a cycle count

1. Take the base from the group table, citing the printed page and
   caption: `(PRM Table 4-32, p. 4-3)` or, under the body's numbering,
   `(PRM Table 4-1, p. 4-3)`.
2. Add only the delay tables the group note permits, citing the delay
   row: `+ 3 cycles for an IC miss contained in the prefetch buffer
   (Table 4-37, p. 4-6; row t437_ic_pfb)`.
3. Never present a single "cycles per instruction" without the
   assumptions of p. 4-1. The manual itself says it "is difficult to
   measure how long it takes to execute a single instruction" (p. 4-1).

Worked citations, using only printed numbers:

* **Simple ALU op.** `ADD` is 1 cycle, min = max = 1 (Table 4-32,
  p. 4-3). `ADD3` is also 1. `ADDI` is 2, and Table 4-32 prints it as
  `ADD1` (erratum, §7). `AND`, `OR`, `SUB`, `XOR` and their `3` forms
  are 1; `ANDI` and `ORI` are 2.
* **Folded jump.** A conditional jump or an unconditional jump folded
  into the previous instruction costs **0 cycles** (p. 4-3 note for
  `JMP`; Table 4-35 "Correct prediction, folded" = 0, p. 4-5). An
  unfolded unconditional jump costs 1, and an unfolded conditional
  jump with a correct prediction costs 1 (Table 4-35).
* **CALL.** 1 cycle, min = max = 1 (Table 4-32, p. 4-3), before any
  fetch or operand-access delay. The manual prints no separate call
  sequence cost; the store of the return PC at `*(CSP)` (p. 3-9) is
  inside those cycles under the p. 4-1 assumptions.

## 6. Parameters chosen by the model

`timing.csv` keeps Chapter 4 symbolic because the manual prints no value
for its memory-access times: `A` is "memory access time for a single
word access", `D` for a double word, `Q` for a quad word (p. 4-2).
Three implementations report a per-instruction count from the same HRI
field, so the concrete values need exactly one authoritative home.
**Everything in this section is a model decision, not a manual fact**;
manual-side inputs are cited individually.

| parameter | chosen value | status and cite |
|---|---|---|
| `A_CYC` | 1 core cycle per 32-bit word | model decision; `A` is defined on p. 4-2 with no printed value, and **no bus figure draws a one-clock transfer**: Figures A-2 and A-3 (pp. A-3, A-5) have START low in bus cycles 4, 11 and 14 only and DTACK across the 6\|7, 13\|14 and 15\|16 boundaries, three, three and two clocks after their STARTs (§11) |
| `D_CYC` | 2 | model decision; `D` (p. 4-2), one cycle per 32-bit word |
| `Q_CYC` | 4 | model decision; `Q` (p. 4-2), one cycle per 32-bit word |
| `E` | 16-byte blocks moved by the ENTER flush loop, rounded up | model decision for the unit; the loop executes `MSP -= 16` per iteration (p. 3-19) and moves quad-words (p. 3-20) |

Substituting those choices:

* **ENTER** = `1 + Q·E` (Table 4-36, p. 4-5; row `t436_enter`) =
  `1 + 4·E`. With E = 8 blocks, **33 cycles**. The manual never states
  `E`'s unit, so the block count is the model's reading of the p. 3-19
  loop; that silence stays recorded in §7 item 8.
* **Unimplemented instruction** = `7 + A` (Table 4-36, p. 4-5; row
  `t436_unimplemented`) = **8 cycles**. The sequence it prices is
  `*(CSP) = PC of unimplemented opcode; PC = *(VB+12)` (p. 1-39).
  `FLUSHD` and `FLUSHDCE` take this path (pp. 3-22 and 3-23).
* **Conditional jumps** (Table 4-35, p. 4-5): correct prediction, folded
  **0**, unfolded **1**; incorrect prediction with the jump 1, 2 or 3
  instructions after its compare **3, 2, 1**, *folded or not*; four or
  more instructions after it, folded **0**, unfolded **1**. Only the
  "4 or more" row is split by folding; the three rows above it carry no
  qualifier and so apply to folded and unfolded jumps alike (§7 item 9,
  the reading decided 2026-11-24 from the page image).
* **No Table 4-37 fetch or Table 4-38 operand delay is added.** Every
  reported count adopts the p. 4-1 assumptions: instruction fetch hits
  the IC, only stack-offset/immediate/register/absolute (jumps and
  calls)/PC-relative modes are used, stack-offset accesses are captured
  in the stack cache, and no data hazards occur. The Table 4-37
  penalties stay in the CSV as data; they are not charged to the
  reported count.

The reported figures are therefore the §5 ones: a simple ALU op 1, a
folded jump 0, an unfolded jump 1, and `CALL` 1.

## 7. Conflicts, errata and silences

Each item is a printed fact plus what the manual does *not* say. The CSV
records the printed value and flags the conflict in `note`; nothing here
is silently reconciled.

1. **Table captions vs body text.** Captions 4-32 to 4-40, body text
   "Table 4-1 through Table 4-9" (p. 4-2). Both retained; §1.
2. **`ADD1` in Table 4-32 (p. 4-3).** Table 3-1 (pp. 3-1 to 3-2) and
   the instruction page (p. 3-6) print `ADDI`. The CSV row is `ADDI`
   with the printed form in its note. The 2-cycle value is not in
   doubt; only the spelling is.
3. **`CMP` in Table 4-32 (p. 4-3).** `CMP` is not a Table 3-1
   mnemonic. The only compare instructions are `CMPEQ`, `CMPGT` and
   `CMPHI` (p. 3-13). The single 1-cycle row is therefore the only
   timing the manual gives them, and the CSV's `covers` cell maps it to
   all three. Whether all three really share one cycle is an inference
   forced by the table, not a statement on the page.
4. **`SC/M quad-word to M/SC quad-word = 4 + D` (Table 4-34, p. 4-4).**
   A quad-word transfer is priced with the *double-word* access time
   `D`, while `Constant to M quad-word` on the same page is `1 + Q` and
   `Q` is defined as the quad-word time (p. 4-2). The manual gives no
   correction. **The ATT2100 specification prints this cell `4 + Q`**
   (2100 Table 3-4, printed p. 3-3, PDF page 105, read from the page
   image), and it is the one cell of the 2100's Chapter 3 that differs
   from PRM Chapter 4 (`docs/cycle_accuracy_plan.md` §1.1). The pattern
   of the table agrees with the 2100: the double-word rows are SC→SC 4,
   SC/M 2 + D, M→M 2·D, so the quad-word SC/M row "should" be 8/2 + Q.
   That is evidence that the PRM's `4 + D` is a misprint.
   **Decision: the model keeps the printed `4 + D`.** The PRM is the
   document for the 92010, and the 2100 is an earlier part; golden 021
   pins the cell (6, with D = 2) three ways, on the core as well, so a
   change is a core change. The timing twin's board file
   (`sem/hobbit_timing_board.txt`, `dqm_scm_qw = 2100`) charges `4 + Q`
   instead, for anyone who wants the other reading; under the model's
   A = 1 the two differ by 2 (6 against 8).
5. **`M quad-word to M quad-word = 8 · S` (Table 4-34, p. 4-4).** `S`
   is not among the abbreviations on p. 4-2. The checker accepts `S`
   only because it is printed; it is not a defined symbol. `8 · Q` is
   the likely reading and remains unconfirmed.
6. **Quad-word fetches priced with `2D` (Table 4-37, p. 4-6).** "single
   quad-word memory" is `5 + 2D` and "2 quad-words in memory" is
   `8 + 2D`: the same `2D` memory term for twice the data, and `D`
   rather than `Q`. Both are printed. The first is explained by the
   prefetch text: a quad-word piece is fetched as "two double-word I/O
   requests" (p. 1-32; DS p. 26), and "Text reads are always
   double-word transfers" (p. A-4), so a quad-word text fill costs 2D,
   not Q. Why two quad words also cost 2D stays unexplained.
7. **Tables 4-38 and 4-40 duplicate each other.** "Operand Access
   Delays" (p. 4-6) and "Miscellaneous Delays" (p. 4-7) print three
   byte-identical indirect-operand rows: `1`, `1 + A`, `1 + 2A`.
   Section 4.2 lists them as separate delay types ("followed by the
   Data Type and Miscellaneous Delay tables", p. 4-6), but never says
   whether both apply to one access. Adding both would double-count an
   indirect operand. The CSV keeps both tables and flags the
   duplication; do not add them without evidence.
8. **`ENTER = 1 + (Q · E)` (Table 4-36, p. 4-5).** `E` is "ENTER size"
   (p. 4-2), but no page states its unit, and the same table prices
   `CATCH` at a flat 1 even though the CATCH description refills the
   stack cache in 16-byte blocks (p. 3-10) exactly as ENTER does
   (pp. 3-19 to 3-21). The `Q · E` term therefore cannot be
   reconstructed from the manual with confidence.
9. **Table 4-35's unqualified rows (p. 4-5): decided 2026-11-24.** The
   page image (PDF page 115) prints seven rows: "Correct prediction,
   folded" 0; "Correct prediction, unfolded" 1; "Incorrect prediction,
   jump after compare" 3; "... jump 2 instructions after compare" 2;
   "... jump 3 instructions after compare" 1; "Incorrect prediction,
   unfolded, 4 or more instructions after compare" 1; "Incorrect
   prediction, folded, 4 or more instructions after compare" 0. **Only
   the "4 or more" row is split into folded and unfolded. The three rows
   "jump after compare" (3), "2 instructions after" (2) and "3
   instructions after" (1) carry no folded/unfolded qualifier, so they
   apply to folded and unfolded jumps alike.** This is the reading of
   the reference model (`sem/hobbit_sem.py`, `_conditional_jump_cycles`,
   whose docstring says so) and of the timing twin
   (`sem/hobbit_timing.py`). An earlier version of this item said that
   the table prints *no* folded incorrect row for 1 to 3 instructions,
   which read strictly would leave those cases with no printed value at
   all; that contradicted the reference model, and it is withdrawn. The
   Bluespec core charges a flat 3 for every mispredicted folded branch
   (`HobbitCore.bsv`), which is wrong at distances 2 and 3 and at 4 or
   more under either reading: milestone C3 of
   `docs/cycle_accuracy_plan.md`.
10. **`CPU` is 0 cycles (Table 4-32, p. 4-3) but a CPU-prefix IC miss
    costs 1 (Table 4-37, p. 4-6).** Not a contradiction: one is the
    base time, the other a fetch penalty; recorded so neither is
    dropped.
11. **`N` is defined but never used (p. 4-2).** No table charges for
    stack-cache occupancy. The manual is silent on the cost of a
    partially full stack cache beyond the ENTER term.
12. **Data sheet.** The December 1992 Advance Data Sheet repeats
    "single-cycle instruction execution for most instructions" and a
    "peak rate of better than one cycle per instruction" and names two
    operating points (250 mW at 3.3 V, 20 MHz; 900 mW at 5.0 V,
    30 MHz), all on its printed p. 1. It prints no per-instruction
    cycle table, so Chapter 4 (with Table 2-4) is the only cycle source.
    It does print timing *rules* the PRM's Chapter 4 does not: the
    demand and aggressive prefetch modes ("Demand fetching is the
    default mode after reset", p. 26); the fold hosts ("selected
    single-parcel instructions or a three-parcel instruction", p. 26);
    that a three-parcel jump never folds (p. 27); "usually no entries
    need to be restored and CATCH takes only one clock cycle" (p. 31);
    and the TIMER events, clock cycles or "completed instructions
    (folded branches are not counted)" (pp. 32–33). The March 1991
    ATT2100 specification is an earlier part; it is cited only as
    evidence beside a PRM cell (item 4), never as the source of a
    value.

## 8. Branch folding (printed p. 4-7)

Section 4.3 states that each decoded instruction has a *next address*
field, and that when the PDU detects a non-branching operation followed
by a branch it folds the two into a single instruction/branch operation.
"A one-parcel branch will fold into a previous one- or three-parcel
instruction and execute together except when the previous instruction
is" one of exactly three classes:

1. another jump of any kind;
2. any one-parcel instruction with a five-bit opcode in the range
   `00000` → `00111`;
3. any three-parcel monadic instruction (the manual's example is
   opcode `000000`).

The second class is enumerable from Table 1-15 (p. 1-22): one-parcel
opcodes `0x00`–`0x07` are `KCALL` (0x00), `CALL` (0x01), the stack
class `CATCH`/`ENTER`/`RETURN`/`POPN` (0x02), `JMP` (0x03) and the four
conditional jumps `JMPFN`/`JMPFY`/`JMPTN`/`JMPTY` (0x04–0x07). The third
class is the Table 1-19 monadic group (p. 1-24). The manual does not
enumerate what "another jump of any kind" includes beyond the encodings
(nor whether `CALL`/`KCALL` count as jumps for this rule); the CSV
records the rule's cost consequences, not a guessed classification.

The cost consequence is in Table 4-35: a correctly predicted folded
branch is 0 cycles, an unfolded one 1. An incorrectly predicted branch
pays 3/2/1 after 0/1/2 intervening instructions, folded or not, and 0
(folded) or 1 (unfolded) four or more instructions after its compare
(§7 item 9).

A `JMP` is the unconditional case: 0 cycles folded, 1 unfolded
(p. 4-3 note). Table 4-32 prices `CALL` at 1 cycle and gives it no
folded variant; Table 4-35 covers only conditional jumps.

## 9. The CSV

Header:

| column | meaning |
|---|---|
| `id` | unique row id; `t<printed table><name>`, e.g. `t437_ic_pfb` |
| `kind` | `instruction`, `dqm`, `condjump`, `misc`, `delay` or `translation` (Table 2-4) |
| `group` | the printed group heading of the row's table |
| `op` | the mnemonic as printed in that table (empty where the table prints no mnemonic) |
| `variant` | the printed row text where the table is not per-mnemonic (DQM form, branch condition, delay condition) |
| `min`, `max` | the printed Min and Max cells, Tables 4-32 and 4-33 only |
| `time` | the printed Cycles/Penalty cell for every other table |
| `covers` | Table 3-1 spellings whose timing this row anchors; empty for supplementary rows |
| `source` | `p. 4-N Table 4-M` (or `p. 2-9 Table 2-4`), the printed page and printed caption |
| `note` | conflicts, errata, and `@id` references to delay rows |

Cycle cells are kept verbatim, including the manual's centred dot and
its juxtaposed products (`5 + 2D`, `2·D`, `1 + (Q·E)`).

`covers` conventions, needed for the seven Table 3-1 entries that have
no printed line of their own (four anchor rows cover them):

* `CMP` (the printed non-mnemonic) anchors `CMPEQ`, `CMPGT`, `CMPHI`;
* `Unimplemented opcode` (printed) anchors `FLUSHD` and `FLUSHDCE`,
  which take the unimplemented-instruction sequence (p. 3-22, p. 3-23);
* `DQM` is anchored by Table 4-34's first form, "Constant to SC
  double-word"; the other nine forms are the same entry;
* `JMP(F/N)(Y/N)` is anchored by Table 4-35's first row, "Correct
  prediction, folded", and covers all four spellings.

Coverage is therefore 46 Table 3-1 entries and 60 spellings, exactly
once each, over 100 rows (70 instruction/table rows, 17 delay rows and
13 Table 2-4 translation rows).
The assumptions, the abbreviations and the folding rule are rules, not
rows, and live in this document.

## 10. What the checker enforces

`tools/check_timing.py`:

* parses the CSV with an exact header, unique ids, and the printed row
  count for every table (38/8/10/7/7/6/6/2/3, and 13 for Table 2-4);
* requires every row to carry a page cite whose page is the page on
  which that table is printed, and whose `kind`/`group` match the
  table;
* requires integer `min`/`max` with `min <= max` on Tables 4-32/4-33,
  and a syntactically valid cycle expression using only the p. 4-2
  symbols (plus the printed, undefined `S`) elsewhere, and only `A` in
  Table 2-4 (p. 2-9 defines no other symbol);
* resolves every `@id` note reference to a real row and requires the
  five "delays are possible" anchors to cite at least one delay row;
* counts Table 3-1 coverage at the spelling level: 46 entries, 60
  spellings, each covered exactly once, so deleting any instruction row
  or duplicating a coverage cell fails.

The docstring records four observed injected defects (re-run
2026-11-24): deleting `t432_add` produces "Table 4-32 ... has 37 rows,
printed lines: 38" and "UNCOVERED spelling ADD (entry ADD[3])";
blanking `t439_dt1`'s source produces "missing source" and "Table 4-39
... has 1 rows, printed lines: 2"; writing `D + 3` for
`t24_read_nonpaged`'s `A + 3` produces "symbol 'D' in Table 2-4, which
defines only A (p. 2-9)"; citing `t24_text_tlb_hit` on p. 2-8 produces
"malformed source" and "Table 2-4 (p. 2-9) has 12 rows, printed lines:
13". All four exit 1.

## 11. Outside Chapter 4: address translation and the bus

**Table 2-4, Address Translation Performance (PRM §2.6, printed p. 2-9,
PDF page 57; read from the page image).** "These performance numbers do
not include the time required to access the actual item. In the table
an A represents the I/O delay for a single word access." Thirteen rows,
all in `timing.csv` as `t24_*`:

| condition | penalty |
|---|---|
| Text reference, micro-TLB miss, TLB/NPSR miss, paged segment walk, R bit modified | 3A + 3 |
| Text reference, micro-TLB miss, TLB/NPSR miss, paged segment walk, R bit previously set | 2A + 3 |
| Text reference, micro-TLB miss, TLB/NPSR miss, nonpaged segment walk | A + 1 |
| Text reference, micro-TLB miss, TLB/NPSR hit | 1 |
| Text reference, micro-TLB hit | 0 |
| Data read, TLB/NPSR miss, paged segment walk, R bit modified | 3A + 3 |
| Data read, TLB/NPSR miss, paged segment walk, R bit previously set | 2A + 3 |
| Data read, TLB/NPSR miss, nonpaged segment walk | A + 3 |
| Data read, TLB/NPSR hit | 0 |
| Data write, TLB/NPSR miss, paged segment walk, R and/or M bit modified | 3A + 3 |
| Data write, TLB/NPSR miss, paged segment walk, R and M bit previously set | 2A + 3 |
| Data write, TLB/NPSR miss, nonpaged segment walk | A + 3 |
| Data write, TLB/NPSR hit and M bit previously set | 0 |

Silences: a data write that hits the TLB/NPSR with M not yet set has no
row; the nonpaged walk is A + 1 for text and A + 3 for data, with no
reason given; there is no data micro-TLB. The ATT2100's Table 6-1
(2100 p. 6-6) prints the same costs (`docs/cycle_accuracy_plan.md` §1.1). Like Tables 4-37..4-40 these are
penalties outside the p. 4-1 assumptions, and no `cyc` charges them yet
(milestone C9 of `docs/cycle_accuracy_plan.md`).

**A = 1 is a choice with no figure behind it.** `bsv/HobbitBus.bsv`'s
header (lines 47-50, as of 2026-11-24) says Figure A-3 "shows START in
consecutive bus cycles 14 and 15" and that this makes A = 1 true at the
bus. The page images (Figure A-2 p. A-3, PDF page 121; Figure A-3
p. A-5, PDF page 123; both re-read at 200 dpi) say otherwise: START is
low in bus cycles **4, 11 and 14** only, and DTACK is low across the
6|7, 13|14 and 15|16 boundaries. No figure draws START and DTACK in one
clock, and no figure draws START in two consecutive cycles. The nearest
is the last beat of each block transfer: START in 14, DTACK in 15. The
module's interface comment (lines 289-293) calls the one-clock
transaction "the zero-wait-state case of the printed protocol"; no
printed waveform shows that case either. So A = 1 rests on the model's
memory (one registered word a clock), not on Appendix A. The header is
**not edited here**, because `bsv/` is being changed by another agent;
the correction is listed for milestone C3.
