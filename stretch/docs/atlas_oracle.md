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
  16,480 printed times (35%) fall on the 0.3 µs grid. Whole-clock
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
| transcribed | **93** | FP PDF 42-101 (all 60 floating-point pages, without and with forwarding, read 2026-11-16), PDF 104 (environment averages), 106 TI, 107 T, 109 I-box, 110 LVS/LVE/SVA, 112 branch, 116-142 (all 27 VFL pages, NO FORWARDING / DIRECT) |
| other (text, flow charts) | 14 | |
| remaining | **46** | VFL with forwarding 143-169, VFL immediate 171-189 |

- **Records.** There are 16,590: 16,480 times and 110 marks. A further
  7,443 cells are printed blank. The FP pages hold 9,406 of the times and 2 of
  the marks (`*01*`, PDF 45).
- **Cross-checks** (`check_atlas_data.py`, all green). The atlas prints
  much of itself twice, and every such pair is counted as exact, near
  (1 in the last place) or far. The counts are pinned by a TALLY line
  on each page.

  | pair rule | pairs | exact | near | far |
  |---|---:|---:|---:|---:|
  | ibox (VFL) | 2,148 | 1,245 | 55 | 848 |
  | ibox (FP) | 3,711 | 1,191 | 438 | 2,082 |
  | invert (VFL) | 2,822 | 1,823 | 81 | 918 |
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
  The ibox rule on the forwarding pages mostly differs for real: with
  forwarding the no-indexing I-box operand runs faster than the
  external one (1.81 against 2.41 on KR through F+ and on L through
  DLWF).

- **Second reading.** The 726 cells shared with the earlier
  independent transcription in `perf_char_timing.py` show 0
  disagreements.
- **Reach.** The reading checks touch 16,114 of the 16,480 times. The
  other 366 are guarded only by the per-page SUM. Every FP time is
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
- **Six uncertain cells**, each with a NOTE:
  - PDF 95 L, U,V FLAGS A(N) ni_ibox `1.81?`. At 6x the last digit is
    a hollow stroke as narrow as a 1, so it is read as 1.81. The ink
    alone cannot exclude 1.80.
  - PDF 126 M+1 (DU,4,4) and (DU,8,4) ix_ext, which lie under a pencil
    stroke.
  - PDF 135 `*+` INVERT ix_ext at (B,32,1), (B,48,1) and (B,64,1),
    which are faded.

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
- **Run time.** The full run is **6,265 cases in 3,618 s (about one
  hour) wall** at `--jobs 12` on a 16-CPU machine. That is two
  simulations a case, about 0.58 s a case in aggregate. The longest
  bodies (T 100WD, the conversions) dominate.

### Self-test (`--selftest`, all four pass; suspect the probe first)

1. **Linearity.** L(BU,8,8) costs 14.0000 clocks a copy between 250 and
   500 copies and again between 500 and 1,000. The ten count branches
   cost 168 clocks in all, 0.017 a copy.
2. **The image is live.** L(BU,64,8) gives 27.998 against 14.017
   through the same binary (24.999 before the per-operation VFL times
   of 2026-11-16).
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

### Not generated (917 transcribed cells, each listed with its reason by `--list`)

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

## The first full residual (2026-11-16; the model as of `77ed952`, before the per-operation VFL times)

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

## After per-operation VFL times (2026-11-16)

`bsv/StretchTiming.bsv`'s `eboxClocks` now gives each VFL operation and
each connective its own E-box time. Each number is fitted to the
operation's own atlas page and cited there. PDF 116-142 were then re-run
with `--pdf 116 ... --pdf 142`: 6,098 cases, all of which halt, taking
about 4,000 s at `--jobs 10`, alongside a test run. The "before" figures are the table above, from
the run on `77ed952`.

That base and this one differ in StretchTiming only by SRD's
nonzero-offset term, and every atlas page is OFFSET 0. As a spot check,
PDF 117 ni_ext was re-measured on this branch's base before the change,
and its 48 cases fit max(14.02, 8 + 2·bytes + 1) row for row.

The other 167 cases (PDF 106, 107, 109 and 112) contain no VFL operation
and were not re-run.

**PDF 116-142, 6,098 cases.**

| | exact | within 1 clock | mean | median | mean \|r\| |
|---|---:|---:|---:|---:|---:|
| before | 423 (7%) | | **−18.93** | | |
| after | 2,225 (36%) | 43% | **−3.46** | −0.04 | 6.51 clocks |

The after range is −67.50 … +60.95.

**The other four pages, re-run after the change** (167 cases, PDF 106,
107, 109 and 112): every page matches the first full run exactly, in
count, exact, mean, median and range. The VFL change did not leak into
the I-box pages. Neither did the two look-ahead fixes made with it
(`bsv/README.md`, "VFL time depends on the operation"). Measured, all
6,265 cases have a mean of −3.87.

| PDF | instr | n | exact | mean | median |
|---|---|---:|---:|---:|---:|
| 106 | TI | 28 | 0 | −30.92 | −29.35 |
| 107 | T | 30 | 0 | −61.31 | −48.35 |
| 109 | I-box | 85 | 15 | −3.27 | −2.55 |
| 112 | branch | 24 | 4 | −5.89 | −2.05 |

PDF 116-142 were measured before those two fixes. As a spot check,
PDF 120 (L) and PDF 141 (CM), 482 cases, were re-run after them. Every
case's model time is identical to the earlier run.

| PDF | instr | n | exact before | exact after | mean before | mean after | median before | median after | worst after |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 116 | + | 272 | 26 | 62 | -5.65 | -2.73 | -4.00 | -0.54 | -34.04 |
| 117 | M+ | 272 | 0 | 30 | -27.37 | -18.46 | -26.28 | -17.30 | -59.44 |
| 118 | +MG | 270 | 24 | 22 | -3.57 | -0.66 | -3.54 | -0.54 | -6.78 |
| 119 | M+MG | 272 | 0 | 20 | -31.48 | -22.57 | -28.64 | -18.44 | -67.50 |
| 120 | L | 272 | 60 | 182 | -2.87 | +0.04 | -3.00 | -0.00 | -6.55 |
| 121 | LWF | 272 | 60 | 182 | -2.87 | +0.04 | -3.00 | -0.00 | -6.55 |
| 122 | LFT | 248 | 0 | 176 | -36.99 | -0.03 | -35.04 | -0.04 | +4.96 |
| 123 | LTRS | 248 | 0 | 176 | -37.96 | -1.19 | -35.04 | -0.04 | -4.04 |
| 124 | ST | 272 | 0 | 40 | -22.62 | -13.50 | -24.79 | -16.33 | -33.34 |
| 125 | SRD | 272 | 0 | 40 | -24.61 | -14.23 | -24.79 | -16.33 | -33.34 |
| 126 | M+1 | 268 | 0 | 0 | -19.00 | -18.85 | -20.25 | -16.27 | -60.34 |
| 127 | K | 272 | 42 | 97 | +2.46 | +3.65 | +0.93 | +1.94 | +28.00 |
| 128 | KR | 272 | 43 | 97 | +1.32 | +2.40 | +0.02 | -0.00 | +28.00 |
| 129 | KE | 272 | 43 | 97 | +1.32 | +2.40 | +0.02 | -0.00 | +28.00 |
| 130 | KF | 272 | 27 | 83 | +3.12 | +3.11 | +1.95 | +1.95 | +27.96 |
| 131 | KFR | 272 | 28 | 83 | +1.97 | +1.95 | +1.00 | -0.00 | +27.96 |
| 132 | KFE | 272 | 28 | 83 | +1.97 | +1.95 | +1.00 | -0.00 | +27.96 |
| 133 | `*` | 136 | 0 | 96 | -18.06 | +1.46 | -19.49 | -0.00 | +5.00 |
| 134 | / | 92 | 0 | 32 | -84.39 | +8.95 | -71.04 | -0.04 | +60.95 |
| 135 | `*+` | 126 | 0 | 96 | -40.16 | +0.38 | -41.04 | -0.04 | +16.96 |
| 136 | LCV | 272 | 6 | 72 | -69.41 | +1.52 | -71.03 | +0.96 | +8.00 |
| 137 | LTRCV | 272 | 0 | 164 | -73.84 | +1.22 | -77.04 | -0.04 | +5.00 |
| 140 | C0011 | 210 | 13 | 139 | -6.90 | +1.53 | -6.00 | -0.00 | +5.00 |
| 141 | CM0101 | 210 | 0 | 37 | -27.13 | -13.31 | -31.33 | -16.42 | -23.47 |
| 142 | CT0111 | 210 | 23 | 119 | -3.52 | +1.35 | -2.59 | -0.00 | +5.00 |

By column, after (compare with the by-column table above):

| column | n | exact | mean | median |
|---|---:|---:|---:|---:|
| ni_ext | 1,074 | 596 | +0.39 | −0.00 |
| ni_ibox | 1,074 | 506 | −3.58 | −0.00 |
| ix_ext | 1,074 | 686 | −0.14 | −0.05 |
| ix_ibox | 1,074 | 437 | −4.04 | −0.00 |
| ni_ext_wbx | 901 | 0 | −7.16 | −4.00 |
| ix_ext_wbx | 901 | 0 | −7.49 | −4.04 |

The fit was made to the EXTERNL OPERAND columns, and those are now
centred on zero: means of +0.39 and −0.14, with 60% exact.

### Why the "0.28 µs" M+ budget did not survive in sequence

This is the diagnosis, and it is structural. Nothing was lost.

- `budgetClocks` is the serial sum `2·iboxCycles + eboxClocks` that the
  0.28 µs claim was computed from. It is charged only on the I-box
  dispatch path, and a VFL instruction never takes that path.
- A VFL instruction is E-box class, so it goes through a look-ahead
  level. There `rl_prepare` charges `ibusy = 2·iboxCycles` (12 clocks)
  when the level is loaded, and `rl_au_remove` charges
  `ebusy = eboxClocks` when it is removed. The two counters run
  concurrently.
- A homogeneous sequence therefore runs at max(preparation + 2, E-box + 1):
  - The +1 is the removal clock: `rl_au_remove` fires on `ebusy == 0`,
    so a charge of N occupies N + 1 clocks.
  - The +2 over the 12-clock preparation was measured and not traced.
- PDF 117's ni_ext column fits max(14.02, 8 + 2·bytes + 1) on all 48
  rows.

The overlap itself is real, and the pages show it. On PDF 120, L's
INDEXING columns equal its NO INDEXING ones from (BU,32,8) on. The
indexed preparation's extra time is hidden once the E-box is the longer
of the two.

What was wrong is that the E-box charge was too small ever to be the
longer. So each new number is the occupancy the page measures, less
the removal clock. GENER's homogeneous sequences cannot tell this apart
from a VFL decode that runs *in series* with the E-box. Which of the two
the 7030 does is **open**, and it matters only for mixed sequences.

### What remains (VFL pages)

- **Stores to the I-box and stores across a word boundary.** These are
  M+, M+MG, ST, SRD, M+1 and CM. ni_ext is now within about 1 clock.
  ni_ibox / ix_ibox print 13-16 clocks more, and the WB XOVR columns
  about 30 more: M+1 (BU,8,8) is 34.2 and 51.2 against the model's 21.0.
  These are not E-box time. They are the fetch-and-store's path to an
  index register or to two words (Vol. 1 printed p.2-3 item 6, and
  p.3-18: "VFL data with word boundary crossover represent inefficient
  use of LA levels"). `eboxClocks` sees no address, so they belong in
  the store path. Not modelled.
- **WB XOVR in general.** No column is exact; the median is −4.
- **The INVERT SIGN blocks** are Table 3's unlike-sign terms, such as
  "add .6(x/y + 1)" for M+. They depend on the data, and `eboxClocks`
  sees no data. M+ (DU,48,4) INVERT is still −35.
- **Small fields of K, KF and CT.** These are prep-bound. The 7030 floor
  is 12 clocks (3.61 µs), and the model's is 14, so the residual is +2.
  This is the I-box preparation, not the E-box.
- **The K family's +28.** The 7030 ends a compare with an inverted sign
  early. This was item 3 above, and it is unchanged.
- **`/` under WB XOVR.** The page prints the crossover column *faster*:
  (B,64,1) is 94 clocks against 144 without crossover. The model adds
  to it, so the residual is +61. The page is disowned as a divide timing
  (PDF 41), and it is left as printed.
- **CV / DCV** have no generated cells, so the oracle cannot measure them.
  They are charged their pages' flat figures, read off PDF 138-139 at
  that page's accumulator (+1 at offset 20, PDF 113):
  - CV: 20 clocks binary, 74 decimal.
  - DCV: 20 clocks binary, 18 decimal.

## Where the model is furthest off

1. **The model's VFL time did not depend on the operation** (as of
   `77ed952`; ADDRESSED 2026-11-16, see "After per-operation VFL times"
   below, which re-measures PDF 116-142). Take the
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

- **Transcribe the other 46 pages:** VFL forwarding (143-169) and
  immediate (171-189). The VFL generator should reach them with an
  addressing switch.
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
