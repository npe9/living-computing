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
| `tests/atlas_oracle.py` | The oracle. It builds GENER's program for each expressible cell, runs it on `mkStretchCore` and reports the **residual = model − printed, in clocks of 0.3 µs**. It is a measurement and never fails on a residual. | **no**, it takes hours (an hour for the 6,265 cases of the first run; the 27,655 now generated were measured page-set by page-set) |

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
python3 tests/atlas_oracle.py --selftest          # the harness's own eight checks
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
- **Run time.** *Measured before PDF 143-189 were added.* With them
  and the four new generators, `--list` reports **27,655 cases with a
  generator** (2026-11-16; 12,353 before the generators). The
  forwarding pages alone (PDF 143-169) took 6,088 cases in 5,646 s at
  `--jobs 6`; the whole set is not timed. Their WB XOVR cases now use
  PDF 114's (150000.74)₈. The pre-forwarding full
  run was **6,265 cases in 3,618 s (about one
  hour) wall** at `--jobs 12` on a 16-CPU machine. That is two
  simulations a case, about 0.58 s a case in aggregate. The longest
  bodies (T 100WD, the conversions) dominate.

### Self-test (`--selftest`, all eight pass; suspect the probe first)

Check 0 runs first and is static (no simulation).

0. **FP encoding.** All 9,406 FP cases are assembled and every copy of
   the body is decoded: op code, (N)/(U) bit, the NEG and A sign
   modifiers, operand address and index field must be the ones the
   row, block and column name. Proven discriminating on an in-memory
   copy of the module (the file was never written): NEG and A swapped
   in the suffix map, 4,702 cases fail; the forwarding run rotated over
   four addresses, 1,856 fail. It also caught a wrong expectation of
   its own before it was committed: E+I and SHF carry their operand in
   effective-address bits 0-10, seven places up the 18-bit field
   (Ref. Manual p.102, as quoted in `StretchExecute.bsv`'s SHF and E+I
   arms), which STRAP assembles correctly.

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
5. **INTERNL / IMMED. / ACCUM. encoding** (static, 5,896 cases). The
   address field is 8.0 or (10.74)₈ for INTERNL (written as the literal
   PDF 114 prints, not the generator's constant), (444444)₁₆ with P = 4
   for IMMED., and for CV/DCV offset 0, op code 27 / 59, and a set-up
   load `L(BU,64,8)` at offset 20 (decoded at every half-word, since a
   full-word instruction may start on one). The index field and the
   invert-sign flip are checked too; the flip is checked against the
   assembled word, because a connective's own code uses that bit.
   Injections, made in memory: immediate XOR placed four bits low, 1,604
   fail; invert not applied on the immediate pages, 732 fail; INTERNL
   crossover at .73, 1,796 fail; INTERNL at 9.0, 2,112 fail; the CV
   set-up at offset 0, 384 fail; DCV assembled as CV, 192 fail. The
   set-up decode first failed all 384 clean cases, because it read only
   whole words; it was fixed before the injections.
6. **FP linearity**, on ST(N) to $X9-$X12, which writes index
   registers: 6.0000 clocks a copy at both body lengths. Injected in memory: with the I-box operands moved to
   $X12-$X15 the stores overwrite the loop count ($X15), the run does
   not halt, and the check fails.
7. **Immediate linearity**, LI(BU,64,8): 28.0000 clocks a copy at both
   body lengths, so the XORed word runs. Injected in memory: with the XOR placed four
   bits low the body is still linear, at 0.0000 clocks a copy, so the
   check also requires a copy to cost more than one clock; with that
   clause it fails, as check 5 does statically.

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

- **WB XOVR.** Without forwarding, the field starts FL//2 bits before a
  word boundary. With forwarding it starts at bit 60, which is PDF 114's
  (150000.74)₈.
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
- **VFL INTERNL** (forwarding pages only; the no-forwarding pages print
  the columns blank). The operand is at 8.0 ($L) and, with crossover, at
  (10.74)₈ = bit 60 of $L, as PDF 114 gives. CHOSEN: its value is
  whatever the page's accumulator set-up left there; PDF 113 names
  none.
- **VFL IMMED.** (PDF 171-189). Each copy is assembled with a zero
  immediate and its 24-bit address field is then set to (444444)₁₆ by
  XOR, so the field holds PDF 114's "equivalent of the standard operand"
  whatever the field length. The accumulator is set as on the direct
  page. CHOSEN: for `*I`, `*I+` and `/I` PDF 113's "memory operand was
  +1" is overruled by PDF 114's address contents, which describe this
  run.
- **CV / DCV** (ACCUM. OPERAND). The accumulator is +1 at offset 20
  (PDF 113), loaded once by `L(BU,64,8), ATLONE, 20`; the instruction's
  offset is the heading's OFFSET 0. CHOSEN: the address field, which
  the Reference Manual (printed p.72) says is "not normally used", names
  150000.0.
- **FP addresses.** External operands rotate over 100011-100014₈ (PDF
  40). CHOSEN: with forwarding, 100011₈. PDF 40 prints "1000011₈"
  (seven digits, re-read at 300 dpi), which an 18-bit FP address cannot
  hold.
- **FP I-box operands** are $X9-$X12, or $X9 with forwarding (PDF 40).
  CHOSEN: the whole memory word is put there by a VFL
  `ST(BU,64,8), $X9` in the set-up.
- **FP internal operand** is $R (PDF 40). CHOSEN: it holds the memory
  word, put there by `TI, 1, ATLFM0, 9.0` after the accumulator load.
- **FP data.** CHOSEN, since the volume prints only the captions:
  - the "normalized floating point one" is exponent +1, fraction .1₂;
  - XPFN is that word with the exponent flag on and the exponent sign
    negative; XPFP is the same with the sign positive ("flagged
    exponents superimposed");
  - U,V FLAGS is the one with data flags U and V (bits 62, 63) on;
  - "the initial operand" is read as both the accumulator and the
    memory operand: NORMALIZED 1. puts the one in both;
  - "AC EXPNT N." is read as an accumulator exponent with no flag (the
    plain normalized one);
  - on the load pages, whose captions name only the memory operand, the
    accumulator holds the normalized one;
  - the accumulator is loaded with `L(U)` so a flagged word lands as
    written, and the factor register (for `*+`) gets the same word by
    `LFT(U)`.
- **FP rows.** NEG and A are the sign modifiers, STRAP's N, A and NA
  suffixes (pocket card "L(N,A,NA)"); (N)/(U) is the normalization
  modifier. Self-check 0 decodes every copy.
- **FP KR / KMGR, AH INDICATOR ON / OFF.** CHOSEN: set once in the
  set-up by a compare of 2 against 1 (AH on) or of 1 against 2 (AL on,
  AH off), before the accumulator is loaded.
- **E+I and SHF** (PDF 71, 72). The column's number is the address
  operand, written as a STRAP literal: decimal, in effective-address
  bits 0-10 (Ref. Manual p.102, as quoted in `StretchExecute.bsv`).
  CHOSEN: 2040 is read as decimal, which
  sets the immediate's exponent-flag bit; SHF shifts left (bit 11 = 0).
- **Indexing** is by $X5 = 0 on every new page, as on the old ones.

### Not generated (989 transcribed cells with all 139 pages, 2026-11-16, after the INTERNL, FP, IMMED. and CV/DCV generators; `--list` reports 27,655 cases with a generator)

- 450 ENV cells (PDF 104), which are environment averages.
- 372 marks (`*01*`, `*24*`).
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

## The new generators (2026-11-16): INTERNL, FP, IMMED., CV/DCV

Four generators were added in one change, in the order that measures
the most cells per hour of work: the VFL INTERNL columns (one branch,
3,908 cells), floating point (9,406 cells), the VFL immediate pages
(1,604) and CV/DCV with the accumulator operand (384). With them
`--list` reports **27,655 cases with a generator** and 989 transcribed
cells without one (ENV, the marks, PDF 110, NONCON, CBR, the internal
transmit operands and the I-box refill rows, all as before).

### What the volume says, read on the page images

Every quotation below was read on the page image (pdftoppm, 110-300
dpi), not from the text layer.

- **PDF 40 (printed 34C), FLOATING POINT TIMING.**
  - "Sequences of operations were generated and timed by GENER."
  - External Operands: "Consecutive memory boxes were used where
    possible. Cases without forwarding used a repetition of four
    consecutive addresses 100011₈ to 100014₈. Cases with forwarding
    used 1000011₈."
  - I-Box Operands: "Index registers nine to twelve were used in the
    cases without forwarding and index nine in the cases with
    forwarding."
  - Internal Operands: "The right half of the accumulator, $R, was used
    for all cases. As $R was changed during the execution of successive
    double length operations a large factor of time was introduced by
    large exponent differences. This effort is illustrated in double
    add."
  - Data: "A normalized floating point one (1) was the initial operand
    unless otherwise specified. (Cases were run with flagged exponents
    superimposed.) The execution of large numbers of consectuve
    operations caused a time increase due to shifting in some cases
    (normalized add is one example). The addition of 10 thousand ones
    involves preshifting and post normalization time."
- **PDF 41 (printed 34D).** "The present measurements for /, D/, and R/
  do not give a realistic timing, since the latter is strongly data
  dependent." "Repeated 'to memory' operations lead to queuing for the
  LAAR, and the present measurements on these instructions actually
  refer to the worst possible situations". "Forwarding merely means
  using the same operand address. For fetch-type instructions,
  'forwarding on consecutive fetch' actually occurs, and only one true
  memory fetch is made for the entire sequence of 10,000 instructions."
- **The FP page headings** (PDF 42-101) name only the operation and
  "WITHOUT / WITH FORWARDING OF EXTERNAL AND I-BOX OPERANDS"; the blocks
  are captioned NORMALIZED 1., BOTH OPERANDS WITH XPFN, AC EXPNT N. MEM
  EXPNT XPFN, AC WITH XPFP. MEM WITH XPFN (the load pages: MEMORY
  OPERAND HAS XPFN / U,V FLAGS / XPFP); KR and KMGR are printed twice,
  "AH INDICATOR OFF" and "AH INDICATOR ON" (PDF 58-61, 89-92; 58 and 59
  viewed for this, the rest as transcribed); PDF 71 heads its columns
  "EFFECTIVE ADDRESSES" over ONE and 2040 (viewed), PDF 72 "SHIFT 1
  ... SHIFT 95"; the rows are (N), NEG (N), A(N), NEG A(N), (U), ... .
- **PDF 113 (printed 106).** "Each column of figures represents a
  variation of operand placement; external memory, external with word
  boundary crossover, I-box, internal (accumulator), and internal with
  word boundary crossover." "Finally, for convert (CV) and convert double
  (DCV) the accumulator was originally +1 at offset 20. This was done
  mainly for the case of double convert decimal to binary so that the
  result would always be accepted as legitimate decimal data for the
  next execution."
- **PDF 114 (printed 107).** FORWARDING / DIRECT ADDRESSING: "The
  operand locations used were: external (150000.0)₈ external with word
  boundary crossover (150000.74)₈, I-box $X0 (20.0)₈, internal (10.0)₈,
  internal with word boundary crossover (10.74)₈." IMMEDIATE ADDRESSING:
  "The 24 bit address of the instruction contained the equivalent of the
  standard operand (444 ...4)₁₆. There is, of course, no case of
  forwarding with immediate operands. The to-memory type instructions
  were deleted since they are undefined for immediate addressing."
- **PDF 115 (printed 108)**, item 5: "Actual fetch-type forwarding
  action is possible only for consecutive fetch-type VFL instructions
  with no word boundary crossover."
- **PDF 165 (printed 158)**, the typed box: "The result of a decimal to
  binary CV operation is placed in the accumulator at an offset of 68.
  For subsequent execution of identical CV instructions the operand
  appears to be a very large number."
- **Reference Manual printed p.72** (second hand: as quoted in
  StretchExecute.bsv's CV arm; the manual page was not re-read here): "In the accumulator conversion operations, CONVERT and
  CONVERT DOUBLE, no storage operand is required, and the word address,
  bit address, length, and byte size fields of the instruction are not
  normally used."

The residual tables are in "The new generators: residuals" below.

## The first full residual (2026-11-16; the model as of `77ed952`, before the per-operation VFL times)

**This table predates PDF 143-189.** The forwarding pages were measured
later ("The forwarding pages"), and the INTERNL columns, the immediate
pages, CV/DCV and the FP pages later still ("The new generators:
residuals").

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
- **CV / DCV** had no generated cells when this was written; they now
  do (see "The new generators: residuals"), and the residual is within
  0.2 clocks because the charge was fitted to the same pages.
  They are charged their pages' flat figures, read off PDF 138-139 at
  that page's accumulator (+1 at offset 20, PDF 113):
  - CV: 20 clocks binary, 74 decimal.
  - DCV: 20 clocks binary, 18 decimal.

### The forwarding pages, PDF 143-169 (first run, 2026-11-16)

This is the first run on the forwarding pages. It measures the model
after the per-operation VFL times and the batch10/batch11 merges.

- **Size and time.** 6,088 cases in 5,646 s at `--jobs 6`.
- **Not generated: 4,338 cells.** These are:
  - 3,908 INTERNL (accumulator-operand) cells;
  - 238 cells printed `*01*` or `*24*`;
  - 192 CV/DCV ACCUM. cells.
- **Overall.** 2,223 cases (37%) are exact. The median residual is
  −0.00 and the mean |residual| is 6.50 clocks.

Per column (residual = model − printed, in clocks):

| column | n | exact | mean | median | min | max |
|---|---:|---:|---:|---:|---:|---:|
| ni_ext | 1,074 | 662 | +0.30 | −0.00 | −34.04 | +27.96 |
| ix_ext | 1,074 | 666 | −0.04 | −0.04 | −34.04 | +25.93 |
| ni_ibox | 1,074 | 476 | −3.41 | −0.00 | −50.74 | +28.00 |
| ix_ibox | 1,074 | 419 | −3.84 | −0.00 | −52.74 | +27.93 |
| ni_ext_wbx | 896 | 0 | −2.24 | +4.96 | −64.40 | +60.95 |
| ix_ext_wbx | 896 | 0 | −2.26 | +4.96 | −64.47 | +60.95 |

How each column fares:

- **EXTERNL is about as close as on the no-forwarding pages.** The
  following are exact or within 0.05 clocks on every row: L, LWF, LFT,
  LTRS, `*`, `*+`, C0011 and CT0111.
- **I-BOX stores are short by 14-18 clocks, as without forwarding.**
  This covers M+, M+MG, ST, SRD, M+1 and CM0101. ST (BU,8,8) is −16.3,
  for example. PDF 114 says the I-box operand times do not change with
  forwarding, and they do not.
- **WB XOVR has no exact column.**
  - The fetch-only instructions run +5 clocks over the page. These are
    L, LWF, LTRS, `*`, LCV, LTRCV, C0011 and CT0111, and K at its
    median. So with forwarding the 7030 hides most of the second word's
    fetch, and the model does not.
  - The stores run 20-34 clocks short, as they do without forwarding.
    These are ST, SRD, CM0101, M+, M+MG and M+1.
  - `/` runs +42 over the page, on the page the volume disowns.
- **PDF 114's crossover location changes nothing.** The generator now
  places the forwarding runs' WB XOVR field where PDF 114 says the run
  put it: "external with WB crossover (150000.74)8", bit 60. Before,
  the field started FL//2 bits before the boundary.
  - The 1,792 WB XOVR cases were re-run with the old placement.
  - Every case gives the same model time to within 0.0004 clocks. The
    runs were joined row by row on (pdf, instr, block, row, column).
  - The generated body does carry the new offset. For example, PDF 151
    ST (D,64,4) is `ST(D,64,4), ATLE0+.60`; on PDF 124 it is
    `ATLE0+.32`.
  - The reason: the model charges a crossover by the second word, not
    by where in the word the field starts.
  - The fix makes the cases faithful to the page, but it does not
    explain any residual.

## The new generators: residuals (2026-11-16/17)

Each generator was run on its own pages only, with `--pdf` and, for the
INTERNL and ACCUM. columns, `--col` / `--instr` (the full run was not
made). The model is this branch's: `batch13` merged, no `bsv/` change.
Residual = model − printed, in clocks; exact means |r| ≤ 0.1.

### VFL INTERNL, PDF 143-169 (3,908 cases, 4,991 s at `--jobs 7`)

All 3,908 halt. Exact 116 (3%), median −7.10, mean −8.97, range −64.47
… +45.95, mean |r| 10.95 clocks.

| PDF | instr | n | exact | median | mean | range |
|---|---|---|---|---|---|---|
| 143 | + | 176 | 0 | −5.00 | −8.22 | −14.07 … −0.98 |
| 144 | M+ | 176 | 0 | −20.02 | −17.80 | −64.47 … −2.10 |
| 145 | +MG | 176 | 0 | −5.50 | −8.82 | −20.30 … −0.98 |
| 146 | M+MG | 176 | 0 | −24.12 | −21.39 | −64.47 … −2.10 |
| 147 | L | 176 | 0 | −4.00 | −7.88 | −13.08 … −0.98 |
| 148 | LWF | 176 | 0 | −4.00 | −7.88 | −13.08 … −0.98 |
| 149 | LFT | 160 | 0 | −8.04 | −12.33 | −18.04 … −8.00 |
| 150 | LTRS | 160 | 0 | −8.04 | −12.08 | −17.04 … −8.00 |
| 151 | ST | 176 | 0 | −5.05 | −14.44 | −30.34 … −2.10 |
| 152 | SRD | 176 | 0 | −5.05 | −14.44 | −30.34 … −2.10 |
| 153 | M+1 | 174 | 0 | −22.00 | −17.74 | −55.30 … −2.10 |
| 154 | K | 176 | 7 | −4.00 | −3.06 | −15.00 … +24.00 |
| 155 | KR | 176 | 7 | −4.00 | −3.06 | −15.04 … +24.00 |
| 156 | KE | 176 | 11 | −4.00 | −3.19 | −15.04 … +24.00 |
| 157 | KF | 176 | 21 | −4.00 | −3.00 | −13.08 … +23.96 |
| 158 | KFR | 176 | 21 | −4.00 | −3.00 | −13.08 … +23.96 |
| 159 | KFE | 176 | 34 | −4.00 | −3.18 | −13.08 … +23.96 |
| 160 | * | 88 | 0 | −4.04 | −8.11 | −13.04 … −4.00 |
| 161 | / | 40 | 0 | −13.04 | −12.44 | −55.04 … +32.95 |
| 162 | *+ | 66 | 0 | +7.96 | −1.53 | −27.04 … +10.00 |
| 163 | LCV | 160 | 8 | +2.47 | +5.45 | −14.88 … +45.95 |
| 164 | LTRCV | 176 | 0 | −9.58 | −12.32 | −19.08 … −7.07 |
| 167 | C0011 | 140 | 0 | −7.56 | −8.49 | −13.08 … −1.98 |
| 168 | CM0101 | 140 | 0 | −14.15 | −15.31 | −28.44 … −2.10 |
| 169 | CT0111 | 140 | 7 | −6.54 | −7.89 | −13.08 … −0.05 |

| column | n | exact | median | mean | range |
|---|---|---|---|---|---|
| ix_int | 1056 | 77 | −4.00 | −2.72 | −39.04 … +45.95 |
| ix_int_wbx | 898 | 0 | −13.07 | −16.39 | −64.47 … +32.95 |
| ni_int | 1056 | 39 | −4.00 | −2.86 | −39.04 … +45.95 |
| ni_int_wbx | 898 | 0 | −13.07 | −16.06 | −62.47 … +32.95 |


**The largest systematic residual: the model charges an accumulator
operand as if it were in memory.** Measured on PDF 144 (M+) and 147
(L), no-indexing columns, by re-running their EXTERNL columns beside
this run: the model's INTERNL figure equals its EXTERNL one on 91 of 96
rows (the other 5, all M+, within 2 clocks). Its INTERNL WB XOVR equals
its EXTERNL WB XOVR on M+, and on L is 8 clocks *below* it (the model
charges an internal crossover 1 clock, an external one 9). The other
pages were not re-run beside it. The 7030 does not behave this way. On the same pages, row for row, the printed INTERNL
time exceeds the printed EXTERNL one by a median of:

| instructions | INTERNL − EXTERNL | INTERNL WB XOVR − EXTERNL WB XOVR |
|---|---:|---:|
| +, +MG, L, LWF, K, KR, KE, `*`, C0011, CT0111 | +4 clocks | +10 |
| M+, M+MG, ST, SRD, M+1, CM0101 (to memory) | +4 (M+1 +3) | −4 |
| KF, KFR, KFE | +2 | +10 |
| LFT, LTRS, LTRCV | +8 | +14 |
| `*+`, LCV | −8 | +23 / +1 |

So an operand in the accumulator costs the 7030 about 1.2 µs more than
the same operand forwarded from memory, and a crossing accumulator
field (bit 60 of $L into $R) about 3 µs more, against the model's 1
clock on L (on M+ the model's internal and external crossover are the
same). The to-memory instructions store their crossing internal result
faster than their crossing external one, the reverse of the fetches.
`/` keeps the WB XOVR anomaly of the other columns (+33), and LCV's
+22 … +46 are its decimal rows of 32-64 bits.

### CV / DCV, ACCUM. OPERAND, PDF 138, 139, 165, 166 (384 cases, 1,734 s at `--jobs 2`)

All 384 halt. Exact 288 (75%); every residual is within +0.19 clocks.

| PDF | instr | n | exact | median | mean | range |
|---|---|---|---|---|---|---|
| 138 | CV | 96 | 48 | +0.10 | +0.10 | −0.00 … +0.19 |
| 139 | DCV | 96 | 96 | −0.00 | −0.00 | −0.00 … −0.00 |
| 165 | CV | 96 | 48 | +0.10 | +0.10 | −0.00 … +0.19 |
| 166 | DCV | 96 | 96 | −0.00 | −0.00 | −0.00 … −0.00 |

| column | n | exact | median | mean | range |

**This is not an independent measurement.** `bsv/StretchTiming.bsv`'s
CV and DCV charges (20/74 and 20/18 clocks) were read off these same
pages at this same accumulator, so the oracle confirms only that the
generator reproduces the conditions the charge was fitted under. The
CV +0.19 is the decimal rows: 22.14 µs is 73.8 clocks and the charge is
a whole 74. The comment there that "atlas_oracle.py has no CV/DCV
generator" is now stale; it is left for the model's owner (no `bsv/`
change in a measurement-only task). DCV, which `StretchExecute.bsv`'s
header still lists as "not built", ran and halted on all 192 cases.

### Floating point, PDF 42-101 (9,406 cases, 6,431 s at `--jobs 7`)

All 9,406 halt. Exact 436 (5%), median −1.02, mean −3.10, range −43.02
… +10.50, mean |r| 7.64 clocks (2.29 µs). The two `*01*` cells of PDF
45 are marks and are not generated.

**The probe holds.** The model's FP time depends only on the operation
(`eboxClocks`'s `Fp` arm has no data term), so within each (page,
column) its figure must be one number whatever the block and row. It is,
in all 298 groups. That alone would not exclude a rejection uniform
across rows, so the figures were also checked against `eboxClocks`: the
I-box figures rise and fall with its per-operation charges (charge →
measured: SRT 108 → 109, SLO 19 → 20, `*+` 20 → 22, `*` 9 → 11, D/ 10 →
12, R/ 8 → 10, the add class 5 → 7, `/` 4 → 8), so the operations
execute.

| PDF | instr | n | exact | median | mean | range |
|---|---|---|---|---|---|---|
| 42 | + | 128 | 0 | +4.46 | +4.79 | −1.02 … +10.50 |
| 43 | D+ | 128 | 16 | +3.96 | +4.11 | −1.58 … +9.50 |
| 44 | K | 128 | 0 | +5.24 | +4.99 | −1.02 … +10.50 |
| 45 | KMG | 126 | 0 | +5.24 | +4.97 | −1.02 … +10.50 |
| 46 | +MG | 128 | 4 | +4.46 | +4.73 | −1.02 … +10.50 |
| 47 | D+MG | 128 | 16 | +0.98 | +3.12 | −15.98 … +9.50 |
| 48 | ST | 128 | 0 | −13.88 | −14.13 | −19.15 … −9.61 |
| 49 | SLO | 128 | 0 | −18.15 | −16.90 | −25.33 … −12.00 |
| 50 | SRD | 128 | 0 | −15.40 | −15.65 | −21.18 … −10.61 |
| 51 | SRT | 128 | 0 | −16.49 | −16.74 | −22.94 … −11.04 |
| 52 | * | 128 | 0 | +6.00 | +6.00 | +2.00 … +10.00 |
| 53 | D* | 128 | 0 | +5.00 | +5.00 | +1.00 … +9.00 |
| 54 | / | 128 | 0 | −13.98 | −13.98 | −16.98 … −10.98 |
| 55 | D/ | 128 | 0 | −15.83 | −15.83 | −20.00 … −11.66 |
| 56 | R/ | 128 | 0 | −14.69 | −14.69 | −19.00 … −10.38 |
| 57 | *+ | 128 | 40 | +2.93 | +3.48 | −2.14 … +8.00 |
| 58 | KR | 128 | 0 | +5.24 | +4.99 | −1.02 … +10.50 |
| 59 | KR | 128 | 0 | +5.24 | +4.99 | −1.02 … +10.50 |
| 60 | KMGR | 128 | 0 | +5.24 | +4.99 | −1.02 … +10.50 |
| 61 | KMGR | 128 | 0 | +5.24 | +4.99 | −1.02 … +10.50 |
| 62 | F+ | 128 | 0 | +5.24 | +4.74 | −1.02 … +9.50 |
| 63 | E+ | 128 | 64 | +4.19 | +4.18 | −0.03 … +8.37 |
| 64 | L | 128 | 32 | +0.97 | +0.47 | −2.02 … +1.99 |
| 65 | LWF | 128 | 0 | +5.15 | +4.65 | −1.02 … +9.35 |
| 66 | DL | 128 | 0 | +5.02 | +4.52 | −1.02 … +9.08 |
| 67 | DLWF | 128 | 0 | +5.02 | +4.52 | −1.02 … +9.08 |
| 68 | LFT | 128 | 0 | −3.67 | −3.67 | −6.55 … −0.78 |
| 69 | M+ | 128 | 31 | −10.06 | −11.20 | −25.95 … +0.43 |
| 70 | M+MG | 128 | 29 | −10.06 | −11.29 | −25.95 … +0.43 |
| 71 | E+I | 32 | 0 | −1.00 | −1.00 | −1.00 … −1.00 |
| 72 | SHF | 96 | 32 | −1.48 | −4.73 | −22.98 … +0.02 |
| 73 | + | 192 | 0 | −0.78 | +0.52 | −7.55 … +7.47 |
| 74 | D+ | 192 | 16 | −1.02 | −0.67 | −43.02 … +7.47 |
| 75 | K | 192 | 0 | −0.02 | +0.65 | −5.98 … +7.47 |
| 76 | KMG | 192 | 0 | −0.02 | +0.65 | −5.98 … +7.47 |
| 77 | +MG | 192 | 4 | −0.78 | +0.48 | −7.55 … +7.47 |
| 78 | D+MG | 192 | 16 | −1.02 | −1.27 | −43.02 … +7.47 |
| 79 | ST | 192 | 0 | −6.30 | −10.32 | −19.15 … −5.98 |
| 80 | SLO | 192 | 0 | −12.00 | −14.10 | −25.33 … −8.00 |
| 81 | SRD | 192 | 0 | −7.30 | −11.33 | −21.18 … −5.98 |
| 82 | SRT | 192 | 0 | −11.04 | −13.51 | −22.94 … −7.04 |
| 83 | * | 192 | 0 | +2.00 | +2.32 | −5.00 … +10.00 |
| 84 | D* | 192 | 0 | +1.00 | +1.25 | −8.00 … +9.00 |
| 85 | / | 192 | 0 | −16.98 | −17.23 | −23.98 … −10.73 |
| 86 | D/ | 192 | 0 | −11.66 | −11.91 | −20.00 … −4.07 |
| 87 | R/ | 192 | 0 | −19.00 | −18.46 | −26.00 … −10.37 |
| 88 | *+ | 192 | 40 | −0.00 | −0.39 | −34.00 … +8.00 |
| 89 | KR | 192 | 0 | −0.02 | +0.65 | −5.98 … +7.47 |
| 90 | KR | 192 | 0 | −0.02 | +0.65 | −5.98 … +7.47 |
| 91 | KMGR | 192 | 0 | −0.02 | +0.65 | −5.98 … +7.47 |
| 92 | KMGR | 192 | 0 | −0.02 | +0.65 | −5.98 … +7.47 |
| 93 | F+ | 192 | 0 | −0.02 | +0.49 | −5.98 … +7.47 |
| 94 | E+ | 192 | 64 | −0.02 | +0.77 | −6.00 … +8.34 |
| 95 | L | 192 | 32 | −1.02 | −1.35 | −4.02 … +0.98 |
| 96 | LWF | 192 | 0 | −0.02 | +0.90 | −3.02 … +5.72 |
| 97 | DL | 192 | 0 | −0.02 | +0.23 | −5.98 … +5.72 |
| 98 | DLWF | 192 | 0 | −0.02 | +0.23 | −5.98 … +5.72 |
| 99 | LFT | 192 | 0 | −6.53 | −7.61 | −15.52 … −0.78 |
| 100 | M+ | 192 | 0 | −11.05 | −9.40 | −27.22 … +6.56 |
| 101 | M+MG | 192 | 0 | −11.05 | −9.54 | −27.22 … +6.56 |

| column | n | exact | median | mean | range |
|---|---|---|---|---|---|
| ea_2040 | 16 | 0 | −1.00 | −1.00 | −1.00 … −1.00 |

The model's figure against the page's median, per column, in clocks
(`ni` columns; the `ix` columns are the same in the model):

| instructions | EXTERNAL model / 7030 | I-BOX model / 7030 | INTERNAL ($R, fwd) model / 7030 |
|---|---|---|---|
| +, +MG, K, KMG, KR, KMGR, F+ (no fwd) | 15.5 / 5.5-6 | 7.0 / 6.0 (indexed 8.0) | — |
| the same, with forwarding | 15.5 / 8.0 | 7.0 / 6.0 (8.0) | 7.0 / 12.5-13 |
| L | 6.4 / 4.4 (fwd 9.0 / 8.0) | 6.0 / 6.0 (8.0) | 6.0 / 10.0 |
| LWF, DL, DLWF | 13.7 / 4.4-4.7 (fwd 13.8 / 8.0) | 7.0 / 6.0 (8.0) | 7.0 / 10-12 |
| `*`, D* | 19.0 / 9-10 | 11.0 / 9-10 | 11.0 / 16-17 |
| ST, SRD (to memory) | 6.4 / 16-17 (fwd 9.7) | 6.0 / 24-26 (25-27) | 6.0 / 12.0 |
| SLO, SRT | 20 / 32, 109 / 120 | 20 / 40, 109 / 131 | 20 / 28, 109 / 116 |
| M+, M+MG (to memory) | 15.5 / 15.4 (fwd 18.6 / 13.1) | 7.0 / 28.2 (32.2) | 7.0 / 18.1 |
| /, D/, R/ | 14-20 / 25-32 | 8-12 / 25-32 | 8-12 / 16-36 |
| LFT | 13.7 / 14.5 | 7.0 / 13.5 | 7.0 / 22.5 |
| SHF 1, 3, 6, 9, 12, 95 | 6 flat / 6, 6, 7, 8, 9 (8 indexed), 29 | | |

**The largest systematic residuals, in order of cells:**

1. **A fetch-type FP operation from memory runs at half the 7030's
   rate.** +, K, F+, E+, `*`, LWF, DL and the rest of the fetch class
   measure 13.7-19 clocks with an external operand against the page's
   4.4-10. The I-box operand of the same operation is within a clock
   (+1 on the no-indexing columns). It is the model's FP memory fetch,
   not its E-box: with forwarding (one address) the 7030 prints 8.0 and
   the model still 15.5. A likely cause, not yet traced:
   `bsv/StretchIBox.bsv`'s `fetchesOperand` returns True for one FP
   operation only (`tagged Fp .f: return f.code == fpop_L;`), and L is
   the one fetch whose external figure is near the page (6.4 against
   4.4). PDF 41: "For fetch-type instructions,
   'forwarding on consecutive fetch' actually occurs, and only one true
   memory fetch is made for the entire sequence of 10,000
   instructions." The model shows no such saving. 2,403 EXTERNAL cells are
   more than +5 clocks over the page (up to +10.5).
2. **Stores to an index register or to memory are far too cheap.** ST,
   SRD, SLO, SRT, M+ and M+MG into $X9-$X12 are 17-25 clocks short; to
   memory, ST and SRD are 10 short (PDF 41: "Repeated 'to memory'
   operations lead to queuing for the LAAR ... the worst possible
   situations"). It is the same gap as the VFL I-box stores ("What
   remains (VFL pages)"), so one store-path model would close both.
3. **An accumulator ($R) operand costs the 7030 more, and the model
   less.** The INTERNAL column is 3-6 clocks short on fetches (13 against
   7 on +), 5 on `*` (6 on D*), 15 on LFT, 26 on R/. PDF 40 itself warns that
   "$R was changed during the execution of successive double length
   operations" so D+ / D+MG's internal column (−43) is data, not
   timing. Same direction as the VFL INTERNL finding.
4. **Divide is short by 11-24 clocks** on /, D/ and R/, every column:
   `eboxClocks` charges Table 2's minimum, before the reduction loops.
   PDF 41 disowns these pages as a divide timing ("strongly data
   dependent"), so this residual says how far the minimum is from the
   GENER data, not that the model is wrong.
5. **Indexing an I-box operand costs the 7030 two clocks** (6.0 → 8.0 on
   every fetch page; 1.81 → 2.41 µs) and the model none.
6. **SHF has no shift-amount term.** The model is flat at 6 clocks; the
   7030 grows with the amount, to 29 at SHIFT 95 (−23).
7. **E+I** is −1 at both effective addresses; **`*+`** is the closest
   arithmetic page (median +2.93 without forwarding, −0.00 with).

### VFL IMMED., PDF 171-189 (1,604 cases, 5,769 s at `--jobs 3`)

All 1,604 halt. Exact 656 (41%), median −0.00, mean +3.03, range −14.04
… +61.95, mean |r| 3.73 clocks. The `*24*` marks of `/I` (24 cells)
are not generated.

| PDF | instr | n | exact | median | mean | range |
|---|---|---|---|---|---|---|
| 171 | +I | 96 | 6 | −0.54 | −0.33 | −1.00 … +3.02 |
| 172 | +MGI | 96 | 6 | −1.00 | −0.88 | −2.04 … +3.02 |
| 173 | LI | 96 | 78 | −0.00 | +0.34 | −0.00 … +3.02 |
| 174 | LWFI | 96 | 78 | −0.00 | +0.34 | −0.00 … +3.02 |
| 175 | LFTI | 88 | 88 | −0.04 | −0.02 | −0.04 … −0.00 |
| 176 | LTRSI | 88 | 88 | −0.04 | −0.02 | −0.04 … −0.00 |
| 177 | KI | 96 | 2 | +4.93 | +7.33 | +0.02 … +28.00 |
| 178 | KRI | 96 | 2 | +4.93 | +7.33 | +0.02 … +28.00 |
| 179 | KEI | 96 | 5 | +4.93 | +7.16 | +0.02 … +28.00 |
| 180 | KFI | 96 | 1 | +3.96 | +6.48 | +0.02 … +27.96 |
| 181 | KFRI | 96 | 1 | +3.96 | +6.48 | +0.02 … +27.96 |
| 182 | KFEI | 96 | 1 | +3.46 | +6.27 | +0.02 … +27.96 |
| 183 | *I | 48 | 48 | −0.00 | −0.01 | −0.04 … −0.00 |
| 184 | /I | 40 | 0 | +31.96 | +31.36 | +1.96 … +61.95 |
| 185 | *I+ | 48 | 8 | −7.04 | −6.70 | −14.04 … −0.00 |
| 186 | LCVI | 96 | 36 | −0.04 | +0.21 | −2.08 … +8.00 |
| 187 | LTRCVI | 96 | 84 | −0.04 | −0.13 | −2.08 … +1.93 |
| 188 | CI0011 | 70 | 69 | −0.00 | +0.03 | −0.04 … +2.02 |
| 189 | CTI0111 | 70 | 55 | −0.00 | +0.51 | −0.04 … +2.95 |

| column | n | exact | median | mean | range |
|---|---|---|---|---|---|

The loads, the conversions, `*I` and the connectives are exact or
within a clock on most rows: the per-operation VFL times fitted to the
direct pages carry over. **The systematic residuals:**

1. **The immediate compares (KI … KFEI) run +2 to +12 clocks over the
   page, +28 in the INVERT block.** The 7030 prints 3.61 µs (12 clocks)
   on most rows to 48 bits, and 3.61-4.20 at every field length in the
   INVERT block. The model charges by field length (KI (DU,48,4): 34
   against 22). An immediate operand longer than 24 bits is the 24-bit
   address followed by zeros (Ref. Manual p.56, as quoted in
   `strap_asm.py`'s `encode_vfl_immediate`), and the 7030 appears to
   end the compare early on it, as it does with an inverted sign on the
   direct pages ("The K family's +28").
2. **`/I` is +2 to +62 over the page**: the 7030 prints 20-25 µs at
   every field length, the model 70-138 clocks. The operand is not the
   direct page's: PDF 114 puts (444444)₁₆ in the address, so the divisor
   is large and the quotient small, where PDF 113's direct page divides
   by +1. The model's divide time does not depend on the data, so it
   cannot follow. Divide is disowned as a timing (PDF 41); this residual
   is a data effect.
3. **`*I+` is short by 2-14 clocks above 8 bits**: the 7030 grows with
   the field (13.80 → 22.21 µs), the model flattens at 60-62 clocks.

## Closing the residuals (2026-11-17)

The open items of "The new generators: residuals" were taken in order of
cells. Each change is measured with `--pdf` on the pages it affects, against
a baseline of this branch with `batch14` merged and no `bsv/` change. The
baseline was re-measured on the same pages, not copied from the tables
above. Each row gives n, exact (|r| ≤ 0.1), median and mean of the residual
in clocks. Result checks (every PASS/FAIL line of the CYCLES sections, the
VFL/FP sections, the look-ahead decks, the MCP bootstrap and P1 deck, the
smoke test and `la_levels.py`, 165 sections) were compared line by line
against the same baseline after each change.

### 1. FP operands are fetched by the look-ahead

**Diagnosis.** `StretchIBox.bsv`'s `fetchesOperand` returned True for one
FP operation, L. That was right when the look-ahead was first built
(stage 3a, 2026-09-03, commit `67140c1`): L was then the only FP operation
the E-box executed, and the other 22 fetching operations were built later
without being added. So an FP +, K, `*`, LWF, DL, M+ and so on was loaded
into a level with no operand address. At removal the E-box found no
operand, bailed, issued the read itself and waited for it
(`rl_exec_resume`). The memory access ran in series with execution. On the
7030 the look-ahead fetches the operand while earlier levels execute
(Perf. Char. Vol. 1 printed p.3-17: "floating point instructions are E-box
limited"). The I-BOX column was serial too, which is why its +1 also went.

**Fix.** `fpFetches` lists the operations `execute()`'s Fp arm reads a word
for: everything except the store class (ST, SRD, SLO, SRT) and the two
immediates (SHF, E+I). `fetchesOperand` and `prepareExec` now use it.

| PDF | instr | before n / exact / median / mean | after |
|---|---|---|---|
| 42 | + | 128 / 0 / +4.46 / +4.79 | 128 / 28 / −0.02 / −0.27 |
| 65 | LWF | 128 / 0 / +5.15 / +4.65 | 128 / 32 / +0.97 / +0.47 |
| 64 | L (control: L already fetched ahead) | 128 / 32 / +0.97 / +0.47 | unchanged, 0 cases moved |
| 73 | + (forwarding) | 192 / 0 / −0.78 / +0.52 | 192 / 28 / −1.78 / −2.31 |
| 95 | L (forwarding, control) | 192 / 32 / −1.02 / −1.35 | unchanged |
| 48, 79 | ST (stores nothing ahead, control) | 128 / 0 / −13.88 / −14.13; 192 / 0 / −6.30 / −10.32 | unchanged |
| 69 | M+ | 128 / 31 / −10.06 / −11.20 | 128 / 0 / −14.80 / −15.94 |
| 100 | M+ (forwarding) | 192 / 0 / −11.05 / −9.40 | 192 / 0 / −12.05 / −10.07 |

- PDF 42's EXTERNAL column goes from +9.70 to +0.59 (mean), and its I-BOX
  column from +0.79 to −0.21 (28 of 32 exact). PDF 73's EXTERNAL column with
  forwarding goes from +7.47 to +0.98.
- **M+ got worse, and that is the next item.** Its memory read had been
  hiding the store's cost: with the read overlapped, M+ (EXTERNAL) is now
  8.4 clocks short instead of exact.
- The forwarding pages' INTERNAL column moves by one clock the wrong way
  (+ −5.98 → −6.98). Item 3 is about that column.
- Result checks: no PASS/FAIL line changed and no CYCLES pin moved. Two
  bounded figures fell: "Floating point: L / * / + / ST" 84 → 69 and
  "Floating point: E+ / E+I / SHF" 88 → 85 clocks, both under bounds of
  100,000.

### 2. The look-ahead address register (LAAR), for floating point

**What the sources say** (read in the page images):

- Vol. 1 printed pp.3-20/3-21 (PDF 38-39), "The LAAR, Stores and Internal
  Operand Fetches":
  - "the LAAR will remain 'busy' from the time of look-ahead loading until
    the proper operand is available, is fetched, checked, and accepted by
    the MBCU."
  - An internal operand (address 3 or 5-12) also takes the LAAR, "and the
    LAAR is freed sooner."
  - "Since there is only one LAAR, if the latter is busy whenever the I-box
    decodes an instruction requiring LAAR, a wait must occur."
  - "A store into index storage is a time-consuming operation. ... the
    I-box does no further decoding until the new index contents arrives."
- Vol. 2 PDF 41 (printed 34D): "Repeated 'to memory' operations lead to
  queuing for the LAAR, and the present measurements on these instructions
  actually refer to the worst possible situations."
- Vol. 2 PDF 104, the environmental test, shows that this is queuing and
  not the store's own cost:
  - ST(U) prints 4.82 µs (16 clocks) alone.
  - With one + between stores it prints 2.51 µs averaged, which is still
    one 16-clock LAAR period per store.
  - With three + between, it prints 1.73 µs, and the effective store time
    is negative. That is p.3-21's "three or more time consuming
    instructions in between".
- Vol. 1 printed p.3-19: the I-Checker "processes information in 0.6 µs"
  and does the "store operand error check".

**The model before.** It had no LAAR. A store level retired at removal,
and the next store was loaded as soon as the I-box had prepared it.
`storeWait` held preparation only while a level storing into index storage
was pending.

**The change** (`StretchCore.bsv` `laarRetire` and the gate in
`rl_prepare`, `StretchIBox.bsv` `laarHeldByLevel` / `needsLaar`,
`StretchTiming.bsv` `laarCheckClocks` / `laarStorePost`,
`StretchStorage.bsv` `storesPending`):

- An FP level that stores, or that fetches an internal register, is not
  loaded while another level holds the LAAR or a store is still queued for
  the MBCU.
- A store releases the LAAR when its E-box time is over, after the 0.6 µs
  check (documented) and, for the FP stores that fetch nothing (ST, SRD,
  SLO, SRT), after a fitted remainder per destination.
- A store into index storage holds all decoding until the same instant,
  for every class.
- **Tried and not kept: a wait for the E-box before fetching an E-box
  register (words 7-15).** The model commits a result at removal and only
  charges its time afterwards, so the fetch of, say, $IND can be made
  while the 7030 would still be executing. The gate gained about a clock
  on one column. It moved five VFL CYCLES pins by 1-13 clocks, and its only
  source is an inference from p.3-20. So it was left out.
  - It was first withdrawn because a parallel run failed PAST T MOVE
    (XERR26 instead of XERR29). Re-run on its own with a private
    `STRETCH_TAPE`, the same tree passes: XERR29, 6,442,397 steps.
  - The failure came from the test harness: `run_mcp_assign_test.sh`
    defaults to `/tmp/mcp.assign.tape` and the other MCP runners to
    `/tmp/mcp.tape`. Those are shared by every concurrent run on the
    machine, in every worktree, and a run that regenerates the tape under
    another one corrupts it.

**The fit, and what is not on any page.**

- With the documented events alone (E-box done, the 0.6 µs check, MBCU
  acceptance), FP ST measured 7 clocks a copy against PDF 48's 16. That
  run moved PDF 48 EXTERNAL by only 0.6.
- The remainder is fitted on PDF 48 alone, one number per destination:
  memory 9, index storage 17, internal register 5. The internal value is
  from PDF 79's $R column, the only page with one.
- Held out: SRD (PDF 50), SLO (49) and SRT (51). Their Table 2 charges
  span 4 to 108 clocks, so a mechanism that belonged to the E-box would
  not carry over. These pages land within a clock (EXTERNAL) and three
  (I-BOX; SRT indexed is −2.92).
- **Not applied to the fetch-and-stores, M+ and M+MG.** PDF 69 prints M+
  at 15.42 clocks, *less* than ST's 16.00, with two more E-box cycles, so
  M+'s store path is not ST's. It takes the documented events only.
- **Not applied to VFL or the connectives.** Their E-box charges are fits
  to the back-to-back EXTERNL column, which already contains the queuing.
  Gating them too was measured: VFL ST (PDF 124) EXTERNL went from −0.07
  to +11.93, counting the queuing twice.

| PDF | instr | before (n / exact / median / mean) | after |
|---|---|---|---|
| 48 | ST (the fit) | 128 / 0 / −13.88 / −14.13 | 128 / 64 / −0.07 / −0.32 |
| 49 | SLO (held out) | 128 / 0 / −18.15 / −16.90 | 128 / 56 / −0.28 / −0.89 |
| 50 | SRD (held out) | 128 / 0 / −15.40 / −15.65 | 128 / 64 / −0.59 / −0.84 |
| 51 | SRT (held out) | 128 / 0 / −16.49 / −16.74 | 128 / 0 / −0.48 / −0.73 |
| 79 | ST, forwarding | 192 / 0 / −6.30 / −10.32 | 192 / 128 / −0.02 / −0.22 |
| 80 | SLO, forwarding (held out, $R too) | 192 / 0 / −12.00 / −14.10 | 192 / 104 / −0.00 / −0.76 |
| 69 | M+ | 128 / 31 / −10.06 / −11.20 | 128 / 0 / −7.30 / −8.44 |

By column, before → after (median):

| PDF | EXTERNAL | I-BOX (no indexing) | I-BOX (indexed) |
|---|---|---|---|
| 48 ST | −9.61 → +0.01 (32/32 exact) | −18.15 → −0.15 | −19.15 → −1.15 |
| 49 SLO | −12.00 → −0.00 (28/32) | −20.30 → −0.28 | −21.30 → −1.28 |
| 50 SRD | −10.61 → +0.01 (32/32) | −20.18 → −1.18 | −21.18 → −2.18 |
| 51 SRT | −11.04 → +0.96 | −21.94 → −1.92 | −22.94 → −2.92 |
| 79 ST, forwarding | −6.30 → +0.01 (32/32) | −18.15 → −0.15 | −19.15 → −1.15 |
| 79 ST, $R (the fit) | −6.02 → −0.02 (32/32) | | |
| 80 SLO, forwarding | −12.00 → −0.00 (28/32) | −20.30 → −0.28 | −21.30 → −1.28 |
| 80 SLO, $R (held out) | −8.00 → −0.00 (24/32) | | |
| 69 M+ | +0.08 → +2.59 (after item 1: −8.40) | −21.18 → −18.18 | −25.22 → −22.22 |

**CYCLES pins moved** (every value check unchanged; the reason is in each
deck's header):

- The index-store decode hold: `index_after_index_store` 1248 → 1479
  (seven VFL ST into $X3, 33 clocks each) and `index_after_level`
  2828 → 2864.
- `vfl_second_index` 434 → 447, from the SF(BU,18) into $3. With the
  hold removed and nothing else changed, it runs in 434 again.
- Bounded figures: "Floating point: L / * / + / ST" 84 → 79, "E+ / E+I /
  SHF" 88 → 92 and "FP sign modifiers" 68 → 79.

M+ to an index register (−18) is open. So are the VFL I-box stores: the
index-store hold moved PDF 124's I-BOX column by 4 clocks (−16.30 →
−12.28), and −12 remains. The WB XOVR stores are unchanged. Those need either a store path
fitted to the VFL pages, which would mean re-fitting the VFL E-box laws
without the queuing, or the crossing-field arms, which belong to the
G2.3 work.

### 4. Immediate compares: the operand's own bytes cost nothing

**Diagnosis.** `eboxClocks` charged KI, KRI, KEI, KFI, KFRI and KFEI like
K, by the whole field length. PDF 177-182, plain block, read row by row:

| Field | Printed |
|---|---|
| (BU,48,8) | 4.80 µs = 16 clocks |
| (BU,64,8) | 6.00 µs = 20 |
| (DU,48,4) | 6.60 µs = 22 |
| (DU,64,4) | 9.00 µs = 30 |
| (B,64,1) | 22 |
| (D,64,4) | 30 |
| any field up to 32 bits | 12, the preparation floor |

That is 10 + 2(b − 24/y) clocks, the same for all six compares. It is K's
law with the 24-bit address field's bytes taken out (three bytes in
binary, six in decimal) and without K's full-word allowance.

The immediate operand is the address field (Ref. Manual p.56), already in
the level when the E-box starts. So only the accumulator bytes beyond it
are stepped through. Nothing on the pages names this mechanism. The law
is a measurement at the atlas's operands.

**Not modelled: the INVERT SIGN blocks.** These are PDF 127-132 and
177-182, which print 12 clocks unsigned and 14 signed at every length.
Against the standard operand an inverted sign makes the signs unlike, and
that decides the compare at once. `eboxClocks` sees no data, so charging
every inverted compare that way would be a choice, not a measurement.

| PDF | instr | before (n / exact / median / mean) | after |
|---|---|---|---|
| 177 | KI | 96 / 2 / +4.93 / +7.33 | 96 / 21 / +2.95 / +3.12 |
| 178 | KRI | 96 / 2 / +4.93 / +7.33 | 96 / 21 / +2.95 / +3.12 |
| 180 | KFI | 96 / 1 / +3.96 / +6.48 | 96 / 19 / +2.95 / +3.27 |
| 182 | KFEI | 96 / 1 / +3.46 / +6.27 | 96 / 24 / +2.00 / +2.94 |
| 127 | K (control) | 272 / 81 / +1.99 / +5.09 | unchanged |

**What remains, about +2 to +3.** On these pages the remainder is the
preparation floor: the 7030 prints 12, and the model cannot go below 14,
which is `iboxCycles`' VFL decode. The cause is that `ibusy` counts down
only in `rl_prepare`'s first arm, so a 3.6 µs decode becomes 2 + 12
clocks. That one cause also gives L's +2 on the FP EXTERNAL columns
(item 1). It is open.

No CYCLES pin and no result moved. The subsets were run together with
item 6.

### 5. An indexed FP operand in index storage: one more I-box cycle

**Diagnosis.** Every fetching FP page prints its I-BOX column 0.6 µs
higher with indexing than without, while EXTERNAL does not move. For
example, + on PDF 42 and L on PDF 64 both print 8.03 indexed against 6.03.
Vol. 1 printed p.3-17's "Address indexing has no measurable effect on the
timing of floating point instructions" is about memory operands.

An I-box operand is in index storage, the store the index register is read
from. So the indexed address and the operand are two reads of that store
in turn. The operand read is made at decoding (printed p.3-23 item 4).
The 0.6 µs is p.3-18's "each indexing operation requires 0.6 µs". A
memory operand's look-ahead fetch hides the cycle, which is why the
EXTERNAL columns show none.

**Fix.** `StretchTiming.bsv` `fpIndexedIboxClocks` adds 2 clocks to
`rl_prepare`'s preparation budget for an FP fetch from words 16-31 with an
index. Stores are excluded: a store into index storage prints +0.3 µs
indexed on PDF 48, which is a different path.

| PDF, I-BOX indexed | before (after item 1) | after |
|---|---|---|
| 42 + | 32 / 0 / −2.02 | 32 / 32 / −0.02 |
| 64 L | 32 / 0 / −2.02 | 32 / 32 / −0.02 |
| 73 + (forwarding) | 32 / 0 / −2.02 | 32 / 32 / −0.02 |
| 65 LWF | 32 / 0 / −2.02 | 32 / 32 / −0.02 |
| 95 L (forwarding) | 32 / 0 / −2.02 | 32 / 32 / −0.02 |
| 54 / | 32 / 0 / −17.98 | 32 / 0 / −15.98 (see below) |
| 52 * | 32 / 0 / +1.00 | unchanged |

Every non-indexed column and every EXTERNAL column is unchanged. On *, the
E-box time hides the extra cycle, as it does on the page.

**Divide is not a gain.** PDF 54's indexed and non-indexed I-BOX residuals
were equal before the change, so the page prints no indexing cost for /.
The model now shows a 2-clock gap there that the page does not. The
divide pages are open in any case (item 7).

### 6. SHF's shift amount

**Diagnosis.** Table 2 (Vol. 1 printed p.3-4, PDF 22) charges SHF "4
cycles (shift ≤ 3)" plus "1 cycle for each additional shift of 4" before
execution, and 1 cycle of execution. `eboxClocks` charged it the add
class's flat 5 cycles. PDF 72 prints 6, 6, 7, 8, 8.5 and 29 clocks for
shifts of 1, 3, 6, 9, 12 and 95.

**Fix.** The charge is now 5 + n/4, where n is the effective-address bits
0-10 as decoded. Together with the removal clock, that gives 6, 6, 7, 8,
9 and 29.

**Limit.** An indexed shift amount is not seen, because `eboxClocks` gets
the level's instruction before its indexing is applied. Every atlas SHF
is unindexed, or indexed by an $X5 that holds 0.

| PDF 72, by column | before (n / exact / median) | after |
|---|---|---|
| SHIFT 1 | 16 / 16 / +0.02 | unchanged |
| SHIFT 3 | 16 / 16 / +0.02 | unchanged |
| SHIFT 6 | 16 / 0 / −0.98 | 16 / 16 / −0.00 |
| SHIFT 9 | 16 / 0 / −1.98 | 16 / 16 / −0.00 |
| SHIFT 12 | 16 / 0 / −2.48 | 16 / 8 / +0.50 (8.5 printed) |
| SHIFT 95 | 16 / 0 / −22.98 | 16 / 16 / −0.00 |
| page | 96 / 32 / −1.48, mean −4.73 | 96 / 88 / −0.00, mean +0.09 |

No CYCLES pin and no result moved. The main and extra subsets were run
together with item 4's change, and compared against item 2's tree.

### 7. The preparation floor: 12 clocks, not 14

The baseline for items 7-9 is `2cee08a` (items 1-6), re-measured on the
same pages in a pristine worktree, not copied from the tables above.

**Diagnosis.** In a homogeneous run a decode of N clocks cost N + 2. Two
clocks, two causes, both in `StretchCore.bsv`:

- `ibusy` counted down only in `rl_prepare`'s own arm. The decision arms
  are mutually exclusive, so the clock in which `rl_au_remove` removed
  the level just prepared stopped the I-box's clock too: one clock per
  instruction. The I-box and the E-box are separate units (Vol. 1 printed
  p.3-17, decoding "completely overlapped by concurrent E-box execution
  time").
- The level-load clock came on top of the decode: `ibusy` was set to the
  whole decode in the load clock and counted the clocks after it.

The first explains half the old "3.6 µs decode becomes 2 + 12 clocks";
measured alone (`ib` only) the floor went to 13 and nothing else in the
diagnosis changed. The second is the other clock.

**Fix.** `ib` counts `ibusy` down in rl_au_remove, rl_exec_resume (a
level's read) and rl_idx_write, as `eb` does for `ebusy` in every arm.
Not in rl_io, rl_xmit or rl_tail_write (CHOSEN: a transfer or transmit is
the instruction still in progress, T is already ~30 short, and the tail
write is the WB XOVR store path, not touched here). rl_prepare loads
`2 * iboxCycles - 1`. The I-box dispatch path (`budgetClocks`, PDF 109)
is unchanged, and PDF 109 did not move.

**What the two clocks had been hiding.** With them gone, every FP I-BOX
column went from exact to −1: the model had matched the printed 6.0
clocks as the 4-clock FP decode (printed p.3-17, "one instruction per
1.2 µs") plus the two lost clocks. The real remainder is the I-Checker's
"I-box data error check" (printed p.3-19 item 2, 0.6 µs) on an operand
fetched from index storage at decoding: `fpIboxCheckClocks`, +2, FP only
(as `fpIndexedIboxClocks`; the VFL charges are fits that contain their
I-box columns).

| PDF, column | base (n / exact / median / mean) | `ib` only | `ib` + load clock + I-Checker |
|---|---|---|---|
| 177 KI, ni_imm | 48 / 13 / +1.98 / +2.70 | 48 / 13 / +0.98 / +1.83 | 48 / 31 / −0.02 / +1.28 |
| 177 KI, ix_imm | 48 / 8 / +2.95 / +3.54 | 48 / 8 / +1.95 / +2.54 | 48 / 21 / +0.95 / +1.87 |
| 182 KFEI, ni_imm | 48 / 16 / +1.98 / +2.57 | 48 / 13 / +0.98 / +2.03 | 48 / 36 / −0.02 / +1.49 |
| 182 KFEI, ix_imm | 48 / 8 / +2.95 / +3.31 | 48 / 8 / +1.95 / +2.64 | 48 / 16 / +0.95 / +1.97 |
| 127 K, ni_ext | 48 / 20 / +1.50 / +4.58 | 48 / 21 / +0.50 / +4.20 | 48 / 28 / −0.00 / +3.99 |
| 127 K, ix_ibox | 48 / 15 / +1.95 / +4.63 | 48 / 15 / +0.95 / +4.08 | 48 / 33 / −0.00 / +3.71 |
| 42 +, ni_ext | 32 / 0 / +0.39 / +0.59 | 32 / 0 / +0.27 / +0.46 | 32 / 15 / +0.00 / +0.20 |
| 42 +, ix_ibox | 32 / 32 / −0.02 | 32 / 0 / −1.02 | 32 / 32 / −0.02 |
| 64 L, ni_ext | 32 / 0 / +1.96 | 32 / 0 / +1.58 | 32 / 0 / +1.33 |
| 64 L, ni_ibox / ix_ibox | 32 / 32 / −0.02 | 32 / 0 / −1.02 | 32 / 32 / −0.02 |
| 95 L, ni_ext (forwarding) | 32 / 0 / +0.98 | 32 / 0 / +0.98 | 32 / 0 / +1.28 |
| 95 L, $R | 32 / 0 / −4.02 | 32 / 0 / −5.02 | 32 / 0 / −5.77 (item 8) |
| 109 (I-box instructions, control) | 85 cases | unchanged | unchanged |
| 48 ST, 69 M+, 72 SHF, 124 VFL ST | | unchanged | unchanged |

The 13 pages run (42, 48, 64, 69, 72, 73, 95, 109, 116, 124, 127, 177,
182; 2,085 cases): exact 637 → 753, median −0.00 → −0.02, mean −1.58 →
−1.88 (the mean falls because the $R columns, item 8, got worse first).

**What is left on these pages.**
- The indexed immediates print 13.07 clocks (3.92 µs) at the floor, one
  clock over the unindexed 12. p.3-18 says "each indexing operation
  requires 0.6 µs", 2 clocks, and `iboxCycles` charges that; the page
  shows one. Not changed: one page, against the volume's own text.
- FP L EXTERNAL (PDF 64) prints 4.43 and the model gives 5.77. The decode
  (4) and the E-box (3 + 1) are both under it, so the floor is no longer
  the cause; not diagnosed.

### 8. An FP internal operand waits for the E-box and takes the store path

**The source.** Vol. 1 printed p.3-20 (PDF 38): the I-box, "upon decoding
an instruction whose fetch operand is an internal register, uses the LAAR
to store the internal operand address. This is because the needed operand
is not available during the decoding stage, and the mechanism for
internal operand fetch already exists for the handling of store
instructions." The model committed each level at removal and charged its
E-box time after, so an FP fetch of $R had its value long before the 7030
would, and cost nothing.

**Fix.** `headReady` (`intWait`) holds an FP head level whose operand is
address 3 or 5-12 (`fpInternalFetch`) until `fpInternalOperandClocks`
after the E-box finishes the level before it (`eboxDoneAt`, the removal
clock + charge + 1). That number is the store mechanism's own: the
I-Checker's 0.6 µs (`laarCheckClocks`) plus `laarStorePost`'s
internal-register remainder, 5, which item 2 FITTED on PDF 79's ST $R
column. It is reused, not refitted, so every fetch page below is held out.
FP only, as the LAAR. (The draft that held the fetch for words 7-15 in
every class, dropped in item 2, is not this: it moved five VFL pins and
had no time of its own.)

$R columns, PDF 73-101 (ni_int and ix_int, 32 cases each; 1,856 cases),
before → after. Before is item 7's tree for L (the base is −4.02); the
others did not move in item 7:

| PDF | instr | after (n / exact / median / mean), ni_int | before (median) |
|---|---|---|---|
| 73 | + | 32 / 16 / −0.00 / +0.18 | −6.98 |
| 75, 76, 89-92 | K, KMG, KR, KMGR | 32 / 16 / +0.48 / +0.50 | |
| 77 | +MG | 32 / 16 / −0.00 / +0.09 | |
| 79 | ST (the fit's own column, control) | 32 / 32 / −0.02 / −0.02 | −0.02 |
| 80 | SLO (stores $R; control) | 32 / 24 / −0.00 / −0.50 | |
| 81, 82 | SRD, SRT | 32 / 0 / +0.97, +0.96 | |
| 83 | * | 32 / 0 / +1.00 | |
| 84 | D* | 32 / 28 / −0.00 / −0.25 | |
| 93, 94 | F+, E+ | 32 / 32 / −0.00 | |
| 95 | L | 32 / 0 / +0.97 | −4.02 (−5.77 after item 7) |
| 96 | LWF | 32 / 0 / +0.97 | |
| 97, 98 | DL, DLWF | 32 / 16 / −1.02 / −1.02 | |
| 74, 78 | D+, D+MG | 32 / 10-12 / −1.00 / −3.0 | PDF 40: "$R was changed during ... double length operations", data |
| 85, 87 | /, R/ | 32 / 0 / −20.00 | divide, item 7 of "What remains" |
| 86 | D/ | 32 / 0 / +1.93 | |
| 88 | *+ | 32 / 18 / −0.00 / −2.13 | |
| 99 | LFT | 32 / 0 / −11.53 | |
| 100, 101 | M+, M+MG | 32 / 0 / −5.06 / −5.27 | |

The ix_int columns are the same to ±0.02. Every external and I-box column
of these pages is unaffected by construction (`fpInternalFetch` is False
for them), which the full run below confirms.

### 9. A store into index storage is time-consuming whatever the operation

**Diagnosis.** Item 2 gave the fitted store path (`laarStorePost`) to the
FP stores that fetch nothing (ST, SRD, SLO, SRT) and not to M+ and M+MG,
because PDF 69 prints M+ to memory below ST. That also left M+ into
$X9-$X12 without the index-storage remainder, and PDF 69's I-BOX columns
at −18 and −22. Printed p.3-21: "A store into index storage is a
time-consuming operation" -- a statement about the destination.

**Fix.** `laarRetire` (StretchCore) applies the remainder to every FP store
into words 16-31; memory and internal stores of M+ / M+MG still get the
documented events only. No new number: the index remainder (17) is item
2's fit on PDF 48.

| PDF, column | base (n / exact / median / mean) | after |
|---|---|---|
| 69 M+, ni_ibox | 32 / 0 / −18.18 / −17.48 | 32 / 0 / −1.18 / −0.48 |
| 69 M+, ix_ibox | 32 / 0 / −22.22 / −21.51 | 32 / 0 / −5.22 / −4.51 |
| 70 M+MG, ni_ibox (held out) | 32 / 0 / −18.18 / −17.60 | 32 / 0 / −1.18 / −0.60 |
| 100 M+, ni_ibox (forwarding, held out) | 32 / 0 / −18.18 / −17.64 | 32 / 0 / −1.18 / −0.64 |
| 101 M+MG, ni_ibox (held out) | 32 / 0 / −18.18 / −17.76 | 32 / 0 / −1.18 / −0.76 |
| 69 M+, ni_ext / ix_ext | +2.59 / +2.61 | unchanged |
| 48 ST, 79 ST (controls) | | unchanged |

The indexed columns stay 4 short: the page prints M+ indexed 4 clocks
over unindexed, and the model 0, because the store's decode hold
(`xstoreFreeAt`) hides the indexed preparation's extra clocks. Open.

### 10. LFT is a "to memory" operation; an indexed M+ into index storage

The base is master `b18e74c` (items 1-9), re-measured on the pages below
(`--rebuild`). It reproduces item 9's and the full run's medians: LFT $R
−11.53, M+ indexed I-BOX −5.22.

**What the sources say** (page images):

- Vol. 1 printed p.3-20 (PDF 38): "$Z, $IA, $MB, and $RM, $FT and $TR are
  *bona fide* main memory locations." So LFT, which writes $FT, is a store
  into memory. The same page: the I-box "uses the LAAR to store the
  internal operand address".
- Vol. 1 printed p.3-21 (PDF 39): "Since there is only one LAAR, if the
  latter is busy whenever the I-box decodes an instruction requiring LAAR,
  a wait must occur until the LAAR is free for reloading. ...
  Measurements on consecutive floating-point-to-memory operations (*ST*,
  *MT*, *LFT*, etc.) do not therefore yield realistic timing information."
- Vol. 2 printed 34D (PDF 41): "The following pages refer to 'to memory'
  operations: ... pp. 61, 92 (LFT)". Those are PDF 68 and 99.
- Vol. 1 Table 2 (printed p.3-3, PDF 21) gives LFT the same 2 + 1 cycles
  as L. That is only the E-box. PDF 68/99 print LFT at 14.5 clocks from
  memory, 13.5 from $X9 (with and without indexing) and 22.5 from $R,
  where L prints 4.4, 6 and 10.
- No page says which clocks make up M+'s indexing cost. PDF 69 prints M+
  into $X9-$X12 at 7.86 µs unindexed and 9.07 µs indexed. That is 4.0
  clocks. PDF 70 (M+MG) and PDF 100-101 (with forwarding) print the same.
  The fetch pages show 2 clocks (item 5), and ST into $X shows 1 (PDF 48).

**Diagnosis.**

- LFT. The model gave LFT no LAAR, so it ran like L. Every LFT column was
  short: EXTERNAL −8.80 (PDF 68) / −5.22 (PDF 99), I-BOX −7.52, $R −11.53.
- M+ indexed. Item 9's decode hold (`xstoreFreeAt`) absorbed the indexed
  preparation that `ibusy` charges after the load. So M+ indexed cost the
  same as unindexed.

**Changes.**

1. `StretchIBox.fpLaarStore`. LFT takes the LAAR for word 14. This is
   timing only: its `storeAddr` stays Invalid, so the hazards and the
   commit path are unchanged. `laarRetire` gives LFT `laarStorePost`'s
   memory remainder, 9, which is ST's fit reused without refitting.
2. `StretchIBox.lftDeferredLaar` and `StretchCore.lftWait`. An LFT whose
   operand is not internal is loaded, and its operand fetched, without
   the LAAR gate. It waits for the LAAR at the head instead.
   **RECONSTRUCTION.**
   - The pages print memory and $X9 a clock apart, so the operand fetch
     is hidden under the store path.
   - Gating at the load would put the fetch in series. Measured with the
     gate at the load and no remainder: EXTERNAL +1.45, I-BOX −5.52.
     Adding the remainder there would put EXTERNAL at about +10.
   - This is in tension with p.3-21, which places the wait at decoding.
3. `StretchCore.intFrom`. An FP internal operand's fetch starts when the
   E-box is done *and* the LAAR is free (`laarFreeAt`), not at E-box done
   alone. The operand address needs the one LAAR (p.3-20, p.3-21).
   - In a homogeneous run this moves only LFT and M+/M+MG from $R, the
     operations that leave a store behind them.
   - It also applies after *any* FP store. For example, an ST followed
     by + from $R now waits the ST's remainder too. No atlas page measures
     that mixed sequence.
4. `StretchTiming.fpHoldSerialClocks` and `StretchCore.xholdPc` /
   `serialPaid`. Take an FP instruction that rl_prepare held behind a
   store into index storage (words 1, 2, 16-31; not STORE WAIT's 11/12),
   that is indexed, and that fetches from index storage. It spends
   `fpIndexedIboxClocks` + `fpIboxCheckClocks` (2 + 2) before it is
   loaded, and the same is taken off its `ibusy` after the load.
   **RECONSTRUCTION**, fitted to the one difference the pages print:
   - The two clocks are the index read (p.3-18) and the operand's
     I-Checker pass (p.3-19 item 2). They are two reads of index storage
     in turn, which cannot start before the new index contents arrive.
   - Unindexed, the read is hidden (that column was already −1.18).
   - The state is tagged by the instruction's address. It is cleared by
     every preparation and by rl_recover and rl_interrupt.

**Measured** (`tests/atlas_oracle.py`, n = 32 per column; median, mean):

| PDF, column | base | after |
|---|---|---|
| 68 LFT, ni_ext / ix_ext | −8.80 / −8.77 | +0.43 / +0.47 |
| 68 LFT, ni_ibox / ix_ibox | −7.52 / −5.55 | +1.47 / +1.43 |
| 99 LFT, ni_ext / ix_ext | −5.22 / −5.22 | +0.47 / +0.47 |
| 99 LFT, ni_ibox / ix_ibox | −7.52 / −5.55 | +1.47 / +1.43 |
| **99 LFT, ni_int / ix_int ($R)** | **−11.53** | **−0.53** |
| **69 M+, ix_ibox** | **−5.22 / −4.51** | **−1.22 / −0.52** |
| 70 M+MG, ix_ibox (held out) | −5.22 / −4.64 | −1.22 / −0.64 |
| 100, 101 M+/M+MG, ix_ibox (held out) | −5.22 | −1.22 |
| 69, 70, 100, 101 ni_ibox (control) | −1.18 | unchanged |
| 69 M+ ni_ext / ix_ext (control) | +2.59 / +2.61 | unchanged |
| 100 M+, ni_int / ix_int ($R) | −5.06 | −3.07 (`intFrom`) |
| 101 M+MG, ni_int / ix_int ($R) | −5.06 | −3.07 |
| 48 ST, 79 ST (all columns), 64 L, 95 L, 42 +, 73 + (controls) | | unchanged, case for case |

Each step was measured on its own tree:

- LFT LAAR alone, with the gate at the load and no remainder: EXTERNAL
  +1.45, I-BOX ni −5.52, $R −11.53 unchanged. `intWait` bound it, not
  the LAAR.
- Adding `intFrom`: $R −9.53, M+ $R −3.07.
- Adding the head gate and the remainder: the table above.
- The serial preparation was measured on its own (M+ ix_ibox −1.22). It
  was re-measured with the address-tagged state on the final tree.

**What is left.**

- LFT I-BOX is +1.45.
- M+ from memory is still +2.6 (PDF 69) and +5.8 (PDF 100). M+ gets the
  documented events alone, while LFT and ST take the memory remainder.
  That inconsistency is open.
- ST indexed into $X prints 1 clock over unindexed (PDF 48), and the
  model gives 0. The serial step is not applied to ST, which fetches
  nothing.

### The full run on the final tree (items 7-9 and the instruction-store gate)

The tables in items 7-9 were measured on intermediate trees, each on its
own pages. This is the whole atlas, 27,655 cases, base `2cee08a` against
`4c8464a` (`tests/atlas_oracle.py --jobs 6 --tsv`, each in its own
worktree). The base TSV agrees with the 13-page base subset to the case.
`4c8464a` is before the merge of master `a169131` and the decode hold's
word-set change (`9f3108d`); see the spot check below the tables.

| | base | final |
|---|---|---|
| exact | 8,225 (30%) | 9,677 (35%) |
| mean / median | −3.08 / −0.02 | −2.74 / −0.02 |
| mean abs residual | 5.81 clocks | 5.32 clocks |
| pages better / worse / same (mean abs) | | 61 / 17 / 59 |

Per page and column, n / exact / median / mean:

| PDF, column | base | final |
|---|---|---|
| 177 KI, ni_imm | 48 / 13 / +1.98 / +2.70 | 48 / 31 / −0.02 / +1.28 |
| 177 KI, ix_imm | 48 / 8 / +2.95 / +3.54 | 48 / 21 / +0.95 / +1.87 |
| 182 KFEI, ni_imm | 48 / 16 / +1.98 / +2.57 | 48 / 36 / −0.02 / +1.49 |
| 127 K, ni_ext | 48 / 20 / +1.50 / +4.58 | 48 / 28 / −0.00 / +3.99 |
| 127 K, ix_ext | 48 / 26 / −0.00 / +3.25 | 48 / 16 / −0.00 / +2.50 |
| 42 +, ni_ext | 32 / 0 / +0.39 / +0.59 | 32 / 15 / +0.00 / +0.20 |
| 64 L, ni_ext / ix_ext | 32 / 0 / +1.96 | 32 / 0 / +1.33 (open) |
| 73 +, ni_int | 32 / 0 / −6.98 / −6.80 | 32 / 16 / −0.00 / +0.18 |
| 75 K, ni_int | 32 / 0 / −6.50 / −6.48 | 32 / 16 / +0.48 / +0.50 |
| 83 *, ni_int | 32 / 0 / −6.00 | 32 / 0 / +1.00 |
| 95 L, ni_int | 32 / 0 / −4.02 | 32 / 0 / +0.97 |
| 95 L, ni_ext | 32 / 0 / +0.98 | 32 / 0 / +1.28 |
| 99 LFT, ni_int | 32 / 0 / −16.52 | 32 / 0 / −11.53 |
| 69 M+, ni_ibox / ix_ibox | −18.18 / −22.22 (median) | −1.18 / −5.22 |
| 70, 100, 101 M+/M+MG ni_ibox (held out) | −18.18 | −1.18 |
| 100, 101 M+/M+MG ni_int | −8.05 | −5.06 |
| 109 I-box instructions, 48 / 79 ST | | unchanged |

SPOT CHECK of `9f3108d` (the merge and the word-set change) against
`4c8464a`: PDF 69 (`--rebuild`), 124 and 141 run again, every case
unmoved (`moved 0` on 128, 272 and 210 cases).

WORSE, recorded rather than hidden. Each was already too fast, and the
faster I-box widens it:
- PDF 54 / (memory): −17.98 → −19.60. PDF 85 / ix_ibox: −15.98 → −16.98.
  Divide is open ("What remains" item 7).
- PDF 68 LFT ext: −8.17 → −8.80.
- PDF 112 BAL/BZAL: one clock further off on all four rows (−51.92 →
  −52.92 on succ_consec).
- PDF 143-169, the VFL pages with a crossing field: mean abs +0.05 to
  +0.2. Exact cases on 156 KE fall 117 → 102 and on 159 KFE 135 → 107,
  while their medians stay at −0.00.

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

- **Open items for the model** (measured 2026-11-17; nothing in `bsv/`
  was changed by the measurement). In order of cells:
  1. FP fetch from memory runs at half the 7030's rate (2,403 EXTERNAL
     cells more than +5 clocks), with and without forwarding. **DONE
     2026-11-17** ("Closing the residuals", item 1): the FP operand was
     not fetched by the look-ahead.
  2. Stores to an index register, and repeated stores to memory, are
     17-25 and about 10 clocks too cheap. **DONE for FP ST/SRD/SLO/SRT
     2026-11-17** ("Closing the residuals", item 2: the LAAR, with a
     fitted store path). FP M+/M+MG to an index register **DONE
     2026-11-17** (item 9; unindexed median −18.18 → −1.18, indexed
     −22.22 → −5.22; indexed → −1.22 by item 10's serial preparation).
     LFT, a "to memory" operation (PDF 41), **DONE 2026-11-17** (item
     10: EXTERNAL +0.47, I-BOX +1.47, $R −11.53 → −0.53).
     Still open: the VFL I-box stores (about −12) and WB XOVR stores.
  3. An accumulator operand is charged as if it were external: the 7030
     adds about 4 clocks (VFL INTERNL), 10 with crossover, and 3-15 on
     the FP $R column. **OPEN.** The FP $R stores now match (item 2).
     The FP $R fetches: **DONE 2026-11-17** (item 8): the operand waits
     for the E-box and takes the store path (check, 2 documented, + the
     ST $R remainder, 5 FIT, reused; equating the two paths is CHOSEN).
     + is exact at the median, K +0.5, and L, LWF and `*` are +1 on every
     row (SRD and SRT were +1 before and did not move). M+/M+MG $R
     −5.06 → −3.07 (item 10: the fetch also waits for the LAAR). VFL INTERNL (+4 on the 7030) is still open.
  4. Immediate compares (KI … KFEI) are charged by field length.
     **DONE 2026-11-17** (item 4). Mean +7 → +3; the rest is the
     preparation floor.
  5. Indexing an FP I-box operand costs the 7030 2 clocks. **DONE
     2026-11-17** (item 5): + L LWF are exact on the I-BOX indexed columns.
  6. SHF has no shift-amount term. **DONE 2026-11-17** (item 6).
  7. Divide (FP /, D/, R/ short by 11-24; `/I` long by up to 62) is
     data-dependent in the 7030 and not in the model; the volume
     disowns these pages as a timing.
  8. The CV/DCV comment in `bsv/StretchTiming.bsv`. **DONE 2026-11-17.**
  9. The preparation floor: a VFL decode costs 14 clocks where the 7030
     prints 12. **DONE 2026-11-17** (item 7): two clocks, the removal
     clock stopping `ibusy` and the load clock on top. FP L EXTERNAL is
     still +1.33 (PDF 64): neither the decode nor the E-box is the cause
     now; not diagnosed. The indexed immediates print one clock over the
     unindexed, where p.3-18 says two.
  10. CHOSEN, not measured: the branch level's load (`2 * 6`) and
     rl_recover's `ibusy <= 12` did not get the "− 1" of item 7; `ib`
     does count down under a branch level's removal.
- **Generators still missing** (989 cells): the NONCON branch columns
  and CBR refills; internal transmit operands; PDF 110 (LVS/LVE/SVA);
  the I-box refill rows; PDF 104's environment averages. Each needs a
  fact the pages do not print, and should come from the commentary
  pages or the Reference Manual, not from guessing.
- **CHOSEN facts the new generators rest on** ("What is assumed"). The
  FP model figure does not depend on the data, so the FP block choices
  (XPFN, XPFP, U,V, AH) cannot move an FP residual today; they will
  once `eboxClocks` gains Table 2's data terms. The immediate divisor
  (PDF 114 over PDF 113) does move `/I`.
- **A full run with everything.** The four new generators were run on
  their own pages only (4,991 + 6,431 + 5,769 + 1,734 s, run
  concurrently, about 1.8 hours wall); the whole set has not been run in one pass.
- **A shorter run.** About an hour is too long for the inner loop of
  M2. A `--sample` mode with one row per column per page would run in
  minutes.
