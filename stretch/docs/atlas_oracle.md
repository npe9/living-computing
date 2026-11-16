# The atlas oracle (source_audit.md G4.1)

**What it is.** IBM's *Performance Characteristics* Vol. 2 is a book of
measured instruction timings for the 7030. GENER, its generator
(PDF 37-39, printed 34-34B), replicates one instruction a thousand
times, closes the run with "a count branch (with an original count of
10)", executes the whole thing ten times, and prints microseconds per
instruction "±.01". The pages make up an atlas, one page per
instruction × condition. Each cell is a row (field spec, word count or
operation) against a column (indexing, operand location, WB crossover,
success or failure).

The oracle has three parts:

| file | what it is | registered in `run_tests.sh`? |
|---|---|---|
| `tests/perf_char_vol2_atlas.txt` | The transcription, read from the page images. Its header gives the format. | no (data) |
| `tests/check_atlas_data.py` | A fast self-check of the transcription: parse, coverage, redundancy tallies, second reading, sums. | **yes**, well under a second |
| `tests/atlas_oracle.py` | The oracle. It builds GENER's program for each expressible cell, runs it on `mkStretchCore` and reports the **residual = model − printed, in clocks of 0.3 µs**. It is a measurement and never fails on a residual. | **no**, it takes an hour |

M2's correctness is defined as how much of this residual it closes
(source_audit.md G4.1).

## The authors' caveats, which bound every residual

These come from the volume itself (PDF 37-39, 102, 105, 111, 113-115):

- **A figure is a throughput.** The ten count branches are in it, and
  overlap with the neighbouring copies is in it. It is not an isolated
  latency. The oracle reproduces the same sequence, so the comparison
  is like with like.
- **±0.01 µs.** That is a thirtieth of a clock. Only 5,840 of the
  28,272 printed times (37%) fall on the 0.3 µs grid. Whole-clock
  behaviour is therefore a column property, not a page property. The
  STORE pages are averages.
- **The conditions are named on each page.** Indexing uses an index
  register containing zero. A forwarding page means the same operand
  address. To-memory pages are the worst case. The divide page divides
  by one, then by zero (`*24*`). `*01*` marks an instruction-check
  reject. PF is a margin mark. Marks are transcribed as marks, never as
  times.

## Coverage

The `#KIND` lines in the data file account for every PDF page from 37
to 189:

| | pages | |
|---|---|---|
| transcribed | **139 (all)** | FP PDF 42-101 (all 60 floating-point pages, without and with forwarding), PDF 104 (environment averages), 106 TI, 107 T, 109 I-box, 110 LVS/LVE/SVA, 112 branch, 116-142 (27 VFL pages, NO FORWARDING / DIRECT), 143-169 (27 VFL pages, FORWARDING / DIRECT), 171-189 (19 VFL pages, IMMEDIATE) |
| other (text, flow charts, a dump) | 14 | |
| remaining | **0** | |

- **Records.** There are 28,644: 28,272 times and 372 marks. A further
  15,379 cells are printed blank. The FP pages hold 9,406 of the times and 2 of
  the marks (`*01*`, PDF 45). The VFL forwarding and immediate pages (PDF
  143-189, read 2026-11-16) hold 11,792 times and 262 marks.
- **Cross-checks** (`check_atlas_data.py`, all green). The atlas prints
  much of itself twice, and every such pair is counted as exact, near
  (1 in the last place) or far. The counts are pinned by a TALLY line
  on each page.

  | pair rule | pairs | exact | near | far |
  |---|---:|---:|---:|---:|
  | ibox (VFL) | 4,296 | 2,234 | 237 | 1,825 |
  | ibox (FP) | 3,711 | 1,191 | 438 | 2,082 |
  | invert (VFL) | 8,106 | 5,287 | 257 | 2,562 |
  | vfwd, PDF 143-169 against 116-142 (EXTERNL, WB XOVR, ACCUM.) | 4,132 | 2,232 | 418 | 1,482 |
  | vfwdib, the same on I-BOX OPERAND | 2,148 | 2,007 | 94 | 47 |
  | index, INTERNL / IMMED. under NO INDEXING against INDEXING | 2,756 | 1,722 | 488 | 546 |
  | immf, IMMED. (171-189) against EXTERNL with forwarding | 1,600 | 731 | 157 | 712 |
  | immn, IMMED. against EXTERNL without forwarding | 1,600 | 929 | 48 | 623 |
  | neg (FP), NEG row against its unnegated row | 4,702 | 4,422 | 144 | 136 |
  | fwd (FP), PDF 73-101 against PDF 42-70 | 3,710 | 2,461 | 166 | 1,083 |
  | branch noncon | 40 | 40 | 0 | 0 |
  | quoted, PDF 104 against 109 | 38 | 32 | 6 | 0 |
  | quotefp, PDF 104 FP captions against PDF 48-68 | 12 | 2 | 6 | 4 |
  | rows, PDF 104/109/110 | 254 | 250 | 4 | 0 |

  `fwd` and `quotefp` were added with the FP pages. With forwarding,
  ST through `*+` (PDF 79-88) print the same external and I-box figures
  as without (PDF 48-57), exact except one SLO cell and the alternating
  2.70/2.71 of `*`, which are within the last digit; the far pairs are where forwarding helps. The
  `quotefp` figures (ST(U) 4.82, SLO(U) 9.59, SRD(U) 5.10, L(U) 1.34,
  DL(U) 1.41, LFT(U) 4.35) lie within 0.02 µs of the no-forwarding
  sheets' NORMALIZED (U) external, no-indexing figure. Which column the
  environment test used is an assumption, stated in the checker.
  `vfwd`, `vfwdib`, `index`, `immf` and `immn` were added with the VFL
  forwarding and immediate pages. PDF 114 says of the I-box operand,
  "there should be no difference in times between no forwarding vs.
  forwarding, and this was indeed the case"; `vfwdib` bears that out
  (2,007 exact and 94 near of 2,148). 40 of its 47 far pairs are on
  PDF 143 (+), on the signed rows (B and D) of both blocks:
  - With forwarding, the signed rows print the times of the unsigned rows:
    (B,8,1) is 4.96 against PDF 116's 4.80, and (D,8,4) is 5.07, close to
    (DU,8,4)'s 5.09.
  - The INVERT block shows none of PDF 116's recomplement cost:
    INVERT (B,8,1) is 4.96 against 7.20, and (D,64,4) 13.50 against
    23.41.
  The same pattern runs through every column of PDF 143, so it is the
  page and not a misread. The other 7 are M+1 INVERT cells on PDF 153. PDF 114 says the immediate run used
  the standard operand in the address field and states no relation to
  the memory pages, so both pairings are counted. Neither fits
  throughout: +I follows the forwarding page, and the compares KI..KFEI
  run below both (3.61 against 4.20).
  The FP ibox rule on the forwarding pages mostly differs for real: with
  forwarding the no-indexing I-box operand runs faster than the
  external one (1.81 against 2.41 on KR through F+ and on L through
  DLWF).

- **Second reading.** The 726 cells shared with the earlier
  independent transcription in `perf_char_timing.py` show 0
  disagreements.
- **Reach.** The reading checks touch 28,058 of the 28,272 times. The
  other 214 are guarded only by the per-page SUM. Every FP time is
  reached, by `neg` at least; the INTERNAL columns and PDF 71-72 are
  reached by `neg` alone. Reach counts rows, not depth: a misread
  repeated down a whole column passes `neg`, which compares within a
  column. On PDF 42-70 and 73-101 the `fwd` and `ibox` rules compare
  across pages and columns, but a misread in a constant INTERNAL column
  would still pass.
- **Discriminating injections.** Each injection was made on a saved
  copy, which was then restored and confirmed identical with `cmp`.
  - PDF 120 ni_ext 6.00→6.60 makes 3 checks fail.
  - PDF 109 LX 5.73→5.13 makes 3 checks fail.
  - PDF 107 100WD, an unreached cell, makes only SUM fail.
  - FP, 2026-11-16. Each was made on a copy of the file; the original
    was never written, and `cmp` against HEAD was clean afterwards.
    - PDF 88 `*+` NORMALIZED (U) ni_ext 6.60→6.90 makes 4 checks fail:
      `fwd`, `ibox`, `neg` and SUM.
    - PDF 72 SHF NOT INDEXED (U) shift_95 8.70→8.40, a cell only
      `neg` reaches, makes 2 checks fail: `neg` and SUM.
    - PDF 104 ST(U) quoted 4.82→4.80 makes 2 checks fail: `quotefp`
      (3, 6, 3 against 2, 6, 4) and SUM.
  - VFL forwarding and immediate, 2026-11-16, made the same way:
    - PDF 147 L (B,32,1) ni_ibox 6.60→6.90: `ibox`, `invert`, `vfwdib`, SUM.
    - PDF 143 + (BU,32,8) ni_int 7.36→7.66: `index`, `invert`, SUM.
    - PDF 165 CV (B,8,1) ni_accum 6.00→6.60: `invert`, `vfwd`, SUM.
    - PDF 171 +I (B,32,1) ni_imm 6.76→6.16: `immf`, `index`, `invert`,
      SUM. `immn` does not fail: its pair was far and stays far.
    - PDF 188 CI0011 (BU,16,4) ix_imm 6.00→6.60: `immf`, `immn`, `index`,
      SUM.
- **Eight uncertain cells**, each with a NOTE:
  - PDF 95 L, U,V FLAGS A(N) ni_ibox `1.81?`. At 6x the last digit is
    a hollow stroke as narrow as a 1, so it is read as 1.81. The ink
    alone cannot exclude 1.80.
  - PDF 126 M+1 (DU,4,4) and (DU,8,4) ix_ext, which lie under a pencil
    stroke.
  - PDF 135 `*+` INVERT ix_ext at (B,32,1), (B,48,1) and (B,64,1),
    which are faded.
  - PDF 146 M+MG INVERT (D,16,4) ni_ext_wbx `19.87?`, where the 19 is
    broken ink.
  - PDF 168 CM0101 (BU,32,1) ni_int_wbx `31.93?`, where the first decimal
    is a fragment.
- **Headings read by glyph or by order, each NOTEd.**
  - PDF 145's mnemonic is illegible. Its INSTR is +MG because of where
    it falls in the run. The ink then tests it: its I-BOX column agrees
    with PDF 118 (+MG) in all 96 pairs, and with PDF 116 (+) in only 52.
  - PDF 153 prints M+ followed by a glyph this printer uses for both I and
    1. It is read as M+1.
  - PDF 169's faint C is read as CT0111.
- **How PDF 143-189 were read.** Seven independent readers worked from
  300 dpi tiles of the page images, with no other sheet open.
  - Most pages were re-read column by column on a second cut. On PDF
    143-148 the second pass compared against the tiles already viewed,
    not a new cut. On PDF 171-174 it was a spot check.
  - A detector then listed every far pair whose difference was unique in
    a column that otherwise agrees. Those on PDF 145, 148, 153, 154, 156,
    162, 164, 168 and 169 were re-read on new crops, and all stand as
    printed.
  - The detector's hits on the M+ invert block (PDF 144) and on the
    to-memory INTERNL tails (143) repeat across rows and pages. They were
    judged real from that repetition, not re-read cell by cell.
  - Where the volume repeats a page, the data rows diff identical:
    KI/KRI/KEI (177-179), and KFI/KFRI/KFEI (180-182, where 182 had a
    different reader).
  - The 262 indicator marks on these pages are in no TALLY and no SUM.

## How to run

```
cd stretch
python3 tests/atlas_oracle.py --selftest          # the harness's own four checks
python3 tests/atlas_oracle.py --list              # what is / is not expressible
python3 tests/atlas_oracle.py --pdf 120 --rows    # one page, every case
python3 tests/atlas_oracle.py --jobs 12 --tsv out.tsv   # everything
```

It needs bsc 2026.01 at `/opt/homebrew/Cellar/bsc/2026.01`. The script
sets `BLUESPECDIR` and `PATH` itself.

- **The testbench is built once.** `bsv/StretchAtlasTb.bsv` is a
  gitignored build product. It is generated with a fixed start address
  and a fixed 1,200-word FASTLOAD image named by a relative path. It is
  rebuilt only when a hand-written `bsv/*.bsv` is newer. Each case
  writes its image in its own temp directory and reruns the one
  binary.
- **Per-instruction clocks are measured by subtraction.** The figure is
  (cycles of the full program − cycles of a baseline with an empty body
  and no count branch) / 10,000.
- **Run time.** *Measured before PDF 143-189 were added.* With them,
  `--list` reports **12,353 cases with a generator** (2026-11-16). The run
  time of that set is unmeasured, and by the per-case rate below it is
  about two hours. The forwarding pages' WB XOVR cases will run with the
  generator's FL//2 field placement, not PDF 114's (150000.74)₈. The full
  run was **6,265 cases in 3,618 s (about one
  hour) wall** at `--jobs 12` on a 16-CPU machine. That is two
  simulations a case, about 0.58 s a case in aggregate. The longest
  bodies (T 100WD, the conversions) dominate.

### Self-test (`--selftest`, all four pass; suspect the probe first)

1. **Linearity.** L(BU,8,8) costs 14.0000 clocks a copy between 250 and
   500 copies and again between 500 and 1,000. The ten count branches
   cost 168 clocks in all, 0.017 a copy.
2. **The image is live.** L(BU,64,8) gives 24.999 against 14.017
   through the same binary.
3. **Baseline.** Set-up and halt take 109 clocks, against 140,277 for
   the sequence.
4. **Branch chain.** A successful CB costs 15.0000 clocks a copy at
   both body lengths. This check was proven discriminating: with the
   first generator's bug re-injected, it fails (0.0068 against 152.38
   clocks a copy).

### Three probe bugs found and fixed before any figure was believed

- **Branch targets.** Each copy was aimed at the *next word*. Count and
  indicator branches are half-words, two to a word, so the chain
  doubled its stride on every branch and ran off the body into data.
  That produced about 76 "clocks" per successful branch.
- **Indexed half-word branches.** These were indexed by $X5, but their
  index field is the one-bit K, which selects $X1 only (the
  assembler's `enc_count_branch`; the model's `evalBranch`). They now
  use $X1 = 0, and the count is kept in $X2.
- **The loop counter.** GENER's count register was $X14. A 13-word
  TRANSMIT into 18.0 (PDF 105: the I-box operands are in "$2 through
  $14") overwrote it, and two cases never halted. It is now $X15. The
  352 other cases re-run with that change gave identical model
  figures. The other 25 pages of the table below come from the full
  run with $X14 and were not re-run, because nothing in those bodies
  writes an index register above $X5.

### What is assumed, because the volume does not print it

The report echoes this list in its header:

- **WB XOVR.** The field starts FL//2 bits before a word boundary.
- **Indexing.** The index register is $X5 = 0. Half-word branches use
  $X1, their only choice.
- **Invert sign.** The VFL invert-sign modifier bit (0x800 in the word)
  is XORed into the assembled copy.
- **Accumulator.** It starts as the standard operand (444…4)₁₆ unless
  PDF 113 says otherwise.
- **Operand locations.**
  - External operands rotate over 150000.0-150003.0 (octal).
  - I-box operands rotate over $X0-$X3 (PDF 114).
- **I-box page.** External operands are at 10000₈ and 50000₈. Internal
  operands are 7.0, 8.0 and 9.0.
- **Transmit.** The I-box block is 18.0 ($X2 up) for both source and
  destination, so ibox_ibox transmits onto itself. The count is in
  $X1.
- **Branch success.** Each copy branches to the next copy. The
  condition is set once in the set-up and stays set.

### Not generated (917 transcribed cells as of the 93-page run; with all 139 pages `--list` reports 16,291: 9,406 FP cells (no FP generator), 3,908 INTERNL cells of PDF 143-169, the marks, CV/DCV, and the immediate pages, reported as "no generator for VFL instruction LI" and so on)

- 450 ENV cells (PDF 104), which are environment averages.
- 192 CV and DCV cells, whose accumulator addressing the page does not
  give.
- 108 marks (`*01*`, `*24*`).
- 45 cells on PDF 110.
- 40 NONCON branch cells. GENER's count when a branch skips part of
  the thousand is not printed.
- 30 cells with INTERNAL transmit operands.
- 16 CBR cells, where the refill word is not described.
- 36 I-box cells:
  - the twin rows V+CR, V-ICR and RCZ, where the page does not say
    which twin is the refill case;
  - R;
  - RNX, which the model does not implement.

## Today's residual (2026-11-16; the model as of `77ed952`, since `bsv/` is untouched on this branch)

**This table predates PDF 143-189.** When the oracle is next run, it will
pick up the forwarding pages on its own. `vfl_case` already has a
`forwarding=yes` branch with one operand address. The INTERNL columns and
all the immediate pages will report "not generated" (see What remains).

There are 6,265 cases, and all of them halt. Exact means |residual| ≤
0.1 clock. Negative means **the model is faster than the 7030**.

**All 6,265 cases:**

| exact | within 1 clock | mean | median | range | mean \|r\| |
|---:|---:|---:|---:|---|---:|
| 442 (7%) | 11% | **−18.92** | **−7.08** | −151.82 … +28.96 | 20.75 clocks (6.2 µs) |

Per page (clocks):

| PDF | instr | n | exact | mean | median | min | max |
|---|---|---:|---:|---:|---:|---:|---:|
| 106 | TI | 28 | 0 | −30.92 | −29.35 | −77.88 | −7.15 |
| 107 | T | 30 | 0 | −61.31 | −48.35 | −151.82 | −28.22 |
| 109 | I-box | 85 | 15 | −3.27 | −2.55 | −12.08 | −0.02 |
| 112 | branch | 24 | 4 | −5.89 | −2.05 | −52.92 | +5.48 |
| 116 | + | 272 | 26 | −5.65 | −4.00 | −39.04 | +1.95 |
| 117 | M+ | 272 | 0 | −27.37 | −26.28 | −68.44 | −7.00 |
| 118 | +MG | 270 | 24 | −3.57 | −3.54 | −10.04 | +1.95 |
| 119 | M+MG | 272 | 0 | −31.48 | −28.64 | −78.50 | −7.00 |
| 120 | L | 272 | 60 | −2.87 | −3.00 | −9.04 | +2.00 |
| 121 | LWF | 272 | 60 | −2.87 | −3.00 | −9.04 | +2.00 |
| 122 | LFT | 248 | 0 | −36.99 | −35.04 | −56.02 | −18.03 |
| 123 | LTRS | 248 | 0 | −37.96 | −35.04 | −56.02 | −23.00 |
| 124 | ST | 272 | 0 | −22.62 | −24.79 | −44.34 | −7.00 |
| 125 | SRD | 272 | 0 | −24.61 | −24.79 | −44.34 | −7.00 |
| 126 | M+1 | 268 | 0 | −19.00 | −20.25 | −42.30 | +19.80 |
| 127 | K | 272 | 42 | +2.46 | +0.93 | −7.07 | +28.96 |
| 128 | KR | 272 | 43 | +1.32 | +0.02 | −7.55 | +28.96 |
| 129 | KE | 272 | 43 | +1.32 | +0.02 | −7.55 | +28.96 |
| 130 | KF | 272 | 27 | +3.12 | +1.95 | −6.57 | +28.96 |
| 131 | KFR | 272 | 28 | +1.97 | +1.00 | −7.05 | +28.96 |
| 132 | KFE | 272 | 28 | +1.97 | +1.00 | −7.05 | +28.96 |
| 133 | * | 136 | 0 | −18.06 | −19.49 | −24.02 | −8.00 |
| 134 | / | 92 | 0 | −84.39 | −71.04 | −119.07 | −54.03 |
| 135 | *+ | 126 | 0 | −40.16 | −41.04 | −46.03 | −29.98 |
| 136 | LCV | 272 | 6 | −69.41 | −71.03 | −143.07 | +1.95 |
| 137 | LTRCV | 272 | 0 | −73.84 | −77.04 | −145.07 | −6.42 |
| 140 | C0011 | 210 | 13 | −6.90 | −6.00 | −11.00 | +1.95 |
| 141 | CM0101 | 210 | 0 | −27.13 | −31.33 | −70.47 | −6.08 |
| 142 | CT0111 | 210 | 23 | −3.52 | −2.59 | −7.04 | +1.98 |

VFL pages 116-142, by column:

| column | n | exact | mean | median |
|---|---:|---:|---:|---:|
| ni_ext | 1,074 | 74 | −15.14 | −7.02 |
| ni_ibox | 1,074 | 74 | −19.11 | −10.05 |
| ix_ext | 1,074 | 208 | −15.08 | −7.00 |
| ix_ibox | 1,074 | 33 | −18.98 | −9.98 |
| ni_ext_wbx | 901 | 21 | −23.29 | −9.04 |
| ix_ext_wbx | 901 | 13 | −23.38 | −9.00 |

## Where the model is furthest off

1. **The model's VFL time does not depend on the operation.** Take the
   192 (field, column, block) groups on PDF 116-139, outside WB XOVR.
   Every instruction in a group, from L and + to M+, ST, `*`, `/`, LFT,
   LCV and LTRCV, gets the *same* model figure. That figure is set by
   field length alone, for example 14 / 17 / 21 / 25 clocks for
   (BU,8/32/48/64,8). The 7030 does not behave this way:
   - `/` (BU,64,8) is 96 clocks against the model's 25.
   - LCV and LTRCV (BU,64,8) are 168-170 clocks against 25.
   - M+ is printed 4-8 clocks over L at every field.

   The largest residuals in the whole atlas (−145 clocks) are this one
   fact. Divide, the conversions, `*+`, the M+ family and LFT/LTRS
   account for most of the aggregate −18.9 mean.

   **Checked against the probe and against the source.**
   - The probe: the assembled copies differ in the operation field, for
     example L …1050, M+ …1090, `/` …11d0, LCV …1030 and ST …10d0 at
     (BU,64,8). The invert-sign XOR lands on the modifier: …1850 for
     the inverted L.
   - The source: `bsv/StretchTiming.bsv`'s `eboxClocks` `VflInt` arm
     (line 181 onward) computes `8 + 2 * bytes` (line 208) from the
     field alone, with no per-operation case. The budget is
     `2 * iboxCycles + eboxClocks` (line 267), and `iboxCycles` gives
     VflInt a flat 6 or 7 (line 98). So the source charges every VFL
     operation alike, and the measurement shows the same thing.
   - The VflInt comment's "0.28 µs" against this same M+ page
     (PDF 117, printed 110) was the budget's figure. For M+ (BU,8,8)
     the budget is 2·6 + 10 = 22 clocks, which is the printed 22.1.
     Back to back in GENER's sequence the model measures 14. The
     budget is right but is overlapped away. The oracle measures the
     throughput the page measured, and there M+ sits 7-11 clocks low
     on every row. Why the budget does not survive in sequence is not
     diagnosed here.
2. **Transmit is missing a fixed cost of about 30 clocks.** T and TI
   are low by roughly 30 clocks at one word. The external-to-external
   per-word slope roughly matches (about 10 clocks a word in both). To
   and from the I-box, the model moves a word in about 2 clocks where
   the 7030 takes about 14 (T ibox_ibox 11WD: 35 against 187). That
   last figure rests on an assumption: the generator's I-box block is
   18.0 for both source and destination, so ibox_ibox transmits a block
   onto itself. PDF 105 says only that the index operands were in
   $2-$14, and no self-test checks the transmit generator.
3. **Comparison with an inverted sign.** The 7030 ends early (K…
   INVERT (DU,64,4) prints 3.61 µs, 12 clocks); the model runs the
   whole field (41 clocks). This gives the only large *positive*
   residuals (+29).
4. **WB crossover** is the worst column family (median −9). The model
   charges the crossover differently for decimal (−7) and binary (+2)
   on PDF 120, and neither matches the page.
5. **Branches.** The model charges 15 clocks for a CB whether it
   succeeds or not, and 13-14 for BXL/BAL. The 7030 is 16/15 for CB and
   about 66 for a successful BAL (PDF 112 prints 19.78 µs). BAL was
   measured in an ARITH RESULT IND environment the page does not spell
   out, so that residual (−52) is the least trustworthy in the table.
6. **Closest.** These are near, not exact:
   - L and LWF: 22% exact, median −3.
   - The K family: about 15% exact, median 0 to +2.
   - The I-box page (PDF 109): LX ext_direct is −0.08, and the rest
     sit at −0.5 to −2.5.

## What remains

- **Generators for the new VFL pages.** The transcription is complete,
  but `tests/atlas_oracle.py` was not changed with it. Another agent
  owns the VFL generator. Three things are needed:
  - **Forwarding, PDF 143-169.** PDF 114 gives the locations: external
    (150000.0)₈, external with WB crossover (150000.74)₈, I-box $X0
    (20.0)₈, internal (10.0)₈, internal with WB crossover (10.74)₈. The
    generator's forwarding branch uses ATLE0 and $X0 and starts the WB
    crossover at FL//2. PDF 114's .74 offsets are what the page used,
    and the INTERNL columns (`ni_int`, `ni_int_wbx`, `ix_int`,
    `ix_int_wbx`) need an internal-operand placement it does not have.
  - **Immediate, PDF 171-189 (`addressing=immediate`, columns
    `ni_imm`/`ix_imm`).** PDF 114: "The 24 bit address of the
    instruction contained the equivalent of the standard operand
    (444...4)₁₆." The mnemonic map is `IMM_BASE` in
    `check_atlas_data.py`.
  - **CV/DCV with forwarding (PDF 165, 166).** These have the same
    accumulator gap as 138/139. PDF 165's typed box: "The result of a
    decimal to binary CV operation is placed in the accumulator at an
    offset of 68. For subsequent execution of identical CV instructions
    the operand appears to be a very large number."
- **FP residuals are unmeasured.** `atlas_oracle.py --list --pdf 42`
  (or any page 42-101) reports "no generator for class FP" for every
  cell, 9,406 times in all. A generator needs the following, from PDF
  40-41 and PDF 113-115:
  - the normalized-1 operand, added ten thousand times;
  - the external operands at 100011-100014₈ without forwarding, and
    at 1000011₈ with it;
  - the I-box operands in index registers 9-12, or 9 alone with
    forwarding;
  - the internal operand `$R`;
  - the setup for each block caption (XPFN, XPFP, U,V flags, AH
    indicator).

  Some of these PDF 40-41 does not print. They should be read from the
  commentary or the Reference Manual, not guessed.
- **Generators still missing:**
  - CV/DCV accumulator addressing;
  - the NONCON branch columns and CBR refills;
  - internal transmit operands;
  - PDF 110 (LVS/LVE/SVA);
  - the I-box refill rows.

  Each needs a fact the pages do not print, and should come from the
  commentary pages or the Reference Manual, not from guessing.
- **A shorter run.** About an hour is too long for the inner loop of
  M2. A `--sample` mode with one row per column per page would run in
  minutes.
