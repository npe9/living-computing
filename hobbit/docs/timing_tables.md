# ATT92010 Hobbit execution times: Chapter 4 as data

Primary source: AT&T Microelectronics, *ATT92010 Hobbit Microprocessor
Programmer's Reference Manual*, January 1993
(`ATT92010_Hobbit_Programmers_Reference_Jan93.pdf`), Chapter 4,
"Performance", printed pp. 4-1 to 4-7. Printed page 4-N is PDF page
N + 110. Every number in `timing.csv` was read from the rendered page
image, not from the scan's OCR layer: `pdftotext` renders `1 + D` as
`1+0`, `5 + 2D` as `5+20`, `2·D` as `2.0` and `8·S` as `9.s`, so the
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
`S` is not in this list: see the errata in §6. `N` is defined but never
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
  `ADD1` (erratum, §6). `AND`, `OR`, `SUB`, `XOR` and their `3` forms
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

## 6. Conflicts, errata and silences

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
   correction.
5. **`M quad-word to M quad-word = 8 · S` (Table 4-34, p. 4-4).** `S`
   is not among the abbreviations on p. 4-2. The checker accepts `S`
   only because it is printed; it is not a defined symbol. `8 · Q` is
   the likely reading and remains unconfirmed.
6. **Quad-word fetches priced with `2D` (Table 4-37, p. 4-6).** "single
   quad-word memory" is `5 + 2D` and "2 quad-words in memory" is
   `8 + 2D`: the same `2D` memory term for twice the data, and `D`
   rather than `Q`. Both are printed; neither is explained.
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
9. **No folded incorrect-prediction rows for 1 to 3 instructions after
   compare (Table 4-35, p. 4-5).** The table prints folded rows only
   for "Correct prediction" (0) and for "4 or more instructions after
   compare (0). The intermediate folded cases are missing, which
   matches the p. 4-7 model in which a fold pairs a branch with the
   instruction immediately before it.
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
    cycle table, so Chapter 4 is the only cycle source; the data sheet
    contributes clock rates, not instructions. The March 1991 ATT2100
    specification is an earlier part and is never cited here.

## 7. Branch folding (printed p. 4-7)

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
branch is 0 cycles, and only the "4 or more instructions after compare"
row gives a folded incorrect case (also 0). An unfolded branch pays its
own cycle (1 for a correct prediction; 3/2/1 for an incorrect prediction
after 0/1/2 intervening instructions).

A `JMP` is the unconditional case: 0 cycles folded, 1 unfolded
(p. 4-3 note). Table 4-32 prices `CALL` at 1 cycle and gives it no
folded variant; Table 4-35 covers only conditional jumps.

## 8. The CSV

Header:

| column | meaning |
|---|---|
| `id` | unique row id; `t<printed table><name>`, e.g. `t437_ic_pfb` |
| `kind` | `instruction`, `dqm`, `condjump`, `misc` or `delay` |
| `group` | the printed group heading of the row's table |
| `op` | the mnemonic as printed in that table (empty where the table prints no mnemonic) |
| `variant` | the printed row text where the table is not per-mnemonic (DQM form, branch condition, delay condition) |
| `min`, `max` | the printed Min and Max cells, Tables 4-32 and 4-33 only |
| `time` | the printed Cycles/Penalty cell for every other table |
| `covers` | Table 3-1 spellings whose timing this row anchors; empty for supplementary rows |
| `source` | `p. 4-N Table 4-M`, the printed page and printed caption |
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
once each, over 87 rows (70 instruction/table rows and 17 delay rows).
The assumptions, the abbreviations and the folding rule are rules, not
rows, and live in this document.

## 9. What the checker enforces

`tools/check_timing.py`:

* parses the CSV with an exact header, unique ids, and the printed row
  count for every table (38/8/10/7/7/6/6/2/3);
* requires every row to carry a page cite whose page is the page on
  which that table is printed, and whose `kind`/`group` match the
  table;
* requires integer `min`/`max` with `min <= max` on Tables 4-32/4-33,
  and a syntactically valid cycle expression using only the p. 4-2
  symbols (plus the printed, undefined `S`) elsewhere;
* resolves every `@id` note reference to a real row and requires the
  five "delays are possible" anchors to cite at least one delay row;
* counts Table 3-1 coverage at the spelling level: 46 entries, 60
  spellings, each covered exactly once, so deleting any instruction row
  or duplicating a coverage cell fails.

The docstring records two observed injected defects: deleting
`t432_add` produces "Table 4-32 ... has 37 rows, printed lines: 38" and
"UNCOVERED spelling ADD (entry ADD[3])"; blanking `t439_dt1`'s source
produces "missing source" and "Table 4-39 ... has 1 rows, printed
lines: 2". Both exit 1.
