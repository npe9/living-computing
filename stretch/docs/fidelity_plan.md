# The plan to close the gap with the documented 7030

Written 2026-11-23 at the owner's request ("Make a plan to fix all of
this"), after an assessment of the model against the documented
architecture. This file orders the work and gives each milestone its
sources, its oracle and its exit test. The record of how each piece is
built still goes where it always has: `microarchitecture_plan.md` (§1a
inventory, §1c rewrite), `NEXT.md`, `atlas_oracle.md`, the deck headers
and commit messages. When a milestone here is done it shrinks to a
pointer.

## Where the model stands (measured, not recalled)

- **Floating point, Vol. 2 PDF 42-101, 9,406 cases**, master `3997745`:
  median residual −0.00 clocks, mean +0.12; 76.8% within 1 clock,
  94.3% within 3. The worst families:
  - `*+`: mean −1.64, down to −28;
  - `D+` / `D+MG`: down to −37 on a few cases;
  - `M+` / `M+MG`: −5 … +7.3 (the EXTERNAL surplus, `atlas_oracle.md`
    item 15).
- **VFL, transmit, branches, Vol. 2 PDF 102-189: RE-MEASURE RUNNING**
  (step 0.1). The last full figures are from 2026-11-16, before
  INTERNL item 11 and the I-box supply work:
  - PDF 116-142: 36% exact, mean −3.46;
  - INTERNL PDF 143-169: 3% exact, median −7.10;
  - IMMED. PDF 171-189: 41% exact.
  The table below is to be replaced by the new run.
- **Structure** (§1c-audit, against Piccolo): 6 of 8 rows match or do
  not apply. The two that differ:
  - the E-box is still largely an interpreter (`vflIntOp` about 2,200
    lines; 44 direct state writes inside execution,
    `ebox_roadmap.md`);
  - the arithmetic is only partly in multi-cycle units (`mkPAU` and
    `mkSAU` are NOT STARTED).
- **Mechanisms the pages describe and the model does differently:**
  - wrong-way branch recovery by snapshot, not recovery levels;
  - index-recovery records standing in for pseudo-store levels;
  - E-box time as budgets (`eboxClocks`), not a unit stepping;
  - the LAAR for FP only;
  - no data forwarding;
  - ECC check cycle only;
  - I/O a synchronous state machine;
  - no maintenance console.

## The rule for "done"

The model matches the documented architecture when all of these hold:

1. Every §1a row is **done**, or is recorded as having no source (with
   the search that was made).
2. The atlas has every family within 1 clock at the median, and 90% of
   each family's cells within 3, except on pages the volume itself
   disowns as a timing (PDF 41: the divide pages). Each such exception
   is named in `atlas_oracle.md`.
3. The §1c-audit scores 8 of 8. No execution function is longer than
   about 400 lines. Execution makes no direct state writes: results
   return as commit records, the `FpCommit` pattern.
4. The suite, the MCP boot, and the IBM diagnostic decks the project
   holds pass:
   - the I-box tests `ja_ax1a`-`jb_ax5b`;
   - the floating-point test `jb_af1c`;
   - the exchange test `ka_ex1`.

## How the work runs

- **One serial track (A) for everything that edits `StretchCore.bsv`,
  `StretchExecute.bsv`, `StretchTiming.bsv` or a box.** One agent, one
  milestone, merged when green. Parallel agents on these files have
  cost more in conflicts and stale pins than they saved.
- **A parallel track (B) for work that edits none of them:**
  - reading pages into specs;
  - refreshing the inventory;
  - the assembler;
  - the host side of the disk.
- **Every track-A milestone obeys AGENTS.md:**
  - the full suite after the last edit;
  - every moved pin attributed by injection;
  - a discriminating injection per new mechanism;
  - the atlas TSV compared with master's.
- **The atlas decides between a sourced mechanism and an unsourced
  one.** It does not decide against a source. When a sourced mechanism
  moves the atlas away from the printed values, it is built behind a
  switch, measured, and the conflict is recorded for a decision. The
  FP-box level release (`NEXT.md`, 2026-11-20) is the precedent.
- **Behaviour-neutral first, timing second.** Each structural step is
  split in two:
  - (a) the structure changes with the suite's pins and the atlas TSV
    byte-identical;
  - (b) timing moves, with every moved pin traced.

  This is §1c step 2a/2b's pattern.
- **Before an agent starts, check the disk:** at least 12 GiB free.

## Phase 0: the baseline (track B, now)

**0.1 Re-measure the whole atlas on master.** PDF 42-101 is done (above).
PDF 102-189 is running at `--jobs 6`. Exit: a per-family table (n,
exact, within 1, median, mean, range) in `atlas_oracle.md`. This file's
phase order is then re-checked against it.

**0.2 Refresh §1a from the code, not from the table.** Known stale
rows:
- "Decimal VFL, radix conversion, VFL multiply/divide: open"
  (`mkDecBox`, `mkCvtBox` and `mkVflBox` exist; G2.3 stages 1-3 are
  built);
- FP "divide ... open" (built 2026-11-17);
- "Interrupt system: open" (indicators, mask and interruption are
  executed, and recovery was built 2026-11-20; establish which of Ref.
  Manual pp.43-50 is still missing).

Exit: each row's status is backed by a named deck or a grep. Each
"planned" row names the milestone below that closes it.

**0.3 Read the per-cycle sources into specs, before A3/A4 need them.**
ARITHMETIC-UNIT HALF DONE 2026-11-23: `sau_pau_spec.md` (20 PAU timing
charts, Figs 3.8.1-3.8.20, PDF 225-244; the SAU flow diagrams, Figs
3.11.1-3.11.14, PDF 255-268, print no clock, so the serial unit's per-step
time is Buchholz p.209's 0.6 µs per byte pair; no figure covers the
connectives). LEFT: the LA flow diagrams and the memory timing.
- R23-9732 (7101 CE manual) Figs 3.8.1-3.8.19, the PAU/SAU per-cycle
  charts (source_audit.md G5 item 4, printed pp.225-243; Fig. 3.8.15
  and 3.8.19 already read, `ebox_roadmap.md`).
- The LA flow diagrams, pp.95 and 99-119 (G5 item 6).
- The memory timing, §4 Procedure 1, pp.273-279 (G5 item 5).
- Buchholz §14.4 (the serial and parallel units, A/B and C/D
  registers).
- CE 3.11.x (decimal).

Each figure becomes a cycle table in a new `docs/sau_pau_spec.md`. It
is read from the page image with the page cited, and each figure's
row count is checked. Exit: every figure A3/A4 builds from has a table,
or a note that it is illegible.

## Phase 1: finish the look-ahead overlap (track A)

**A1. Level release for the divide, decimal and VFL boxes.** RUNNING
(branch `rewrite-box-release`). Exit as its brief:
- one switch per box;
- the atlas decides each box;
- interlock, landing and hold-store decks per released box.

## Phase 2: the E-box stops being an interpreter

**A2. Split `vflIntOp` and the connectives, behaviour-neutral.**
- Replace the inlined arms with per-family pure functions that return
  a `VflCommit`, the `FpCommit` pattern (`ebox_roadmap.md` step 2).
  One caller applies the commit.
- Count the direct state writes before and after.
- Exit:
  - the suite and the atlas TSV are byte-identical;
  - no execution function over about 400 lines;
  - VFL direct writes go to 0, so the 44 fall to whatever is left
    outside VFL.
- It is large. Commit one family per milestone: add/load, store,
  connectives, multiply/divide, conversions, decimal.

**A3. `mkSAU`, the serial arithmetic unit.**
- One multi-cycle module, stepping a byte at a time per the 0.3
  tables and Buchholz §14.4. It absorbs `mkDecBox` (the serial adder),
  `mkVflBox` and `mkCvtBox`.
- VFL E-box time then comes from the stepping. The `eboxClocks` VFL
  arm is deleted term by term, each term measured.
- Done in two halves:
  - (a) the box with today's clock counts: atlas byte-identical;
  - (b) the counts from the stepping.
- The known trap: `NEXT.md` "THE VFL TIMING IS SOLVED EXACTLY -- AND
  APPLYING IT BREAKS THE BOOT" (2026-10-26). Cutting the budget to the
  atlas figure broke the MCP IPL, because the budget was hiding a
  memory access the model then had no look-ahead to overlap. The
  look-ahead now fetches operands (atlas items 1, 11, 13). Even so,
  (b) must run the MCP boot after each budget term it removes, and a
  term whose removal breaks the boot names the memory access it was
  covering before anything else moves.
- What falls out of the stepping, each with its own atlas columns as
  the exit:
  - Table 3's unlike-sign terms (the INVERT SIGN blocks, M+ (DU,48,4)
    INVERT −35);
  - the inverted-sign compare ending early (the K family's +28);
  - the VFL `/I` data dependence.
- Exit: the VFL pages, PDF 116-189, meet the "done" rule. Only the
  pages PDF 41 disowns are excepted.

**A4. `mkPAU`, the parallel arithmetic unit.**
- `mkFpBox` and `mkDivBox` are absorbed into one unit with its A/B and
  C/D registers (Buchholz §14.4; CE 3.8.x).
- The open decision "one parallel-unit multiplier, not two"
  (`NEXT.md`, 2026-11-19) is settled here from the charts.
- Also from the stepping: `*+`'s sum (the −28 tail), COMPARE, and the
  square root (`NEXT.md` "THE FP BOX'S REMAINING CLASSES").
- Exit: the FP pages hold or improve on today's 76.8% within 1 clock,
  and `*+` / `D+` meet the rule.

**A5. `ebusy` becomes response readiness; the look-ahead's `Whole`
entries split** (`ebox_roadmap.md` steps 5 and 7).
- The look-ahead holds a level per PART of an instruction, as G1.1
  says ("a level is a PART of an instruction").
- `headReady` waits on the units' `responseReady`, not a counter.
- Exit: `ebusy` has 0 hits. The §1c-audit "expensive datapath" row
  matches.

## Phase 3: the store and fetch paths

**A6. The store path.**
- The VFL fetch-and-store to an index register (ni_ibox / ix_ibox:
  13-16 clocks short) and across a word boundary (WB XOVR: about 30
  short; Vol. 1 printed p.2-3 item 6, p.3-18).
- The LAAR for every store level, not only FP (Perf. Char. Vol. 1
  printed pp.3-19..3-21; `NEXT.md` "D/ AND THE LAAR").
- Data forwarding and store-close-to-fetch cases (2)-(3) (Buchholz
  §15.4; Perf. Char. pp.3-20..21).
- p.3-22's 0.9-1.2 µs per I-box store level.
- Exit: the WB XOVR columns and the forwarding pages, PDF 143-169,
  meet the rule.

**A7. Transmit and branches.**
- Transmit's fixed cost of about 30 clocks, and its 14-clock word to
  and from the I-box (`atlas_oracle.md` "furthest off" 2). First check
  the generator's I-box block assumption, which no self-test covers.
- CB 16/15 clocks, and BXL/BAL.
- Exit: PDF 102-112 meet the rule, or the BAL environment the page
  does not spell out is recorded as the reason.

## Phase 4: the I-box as the pages draw it

**A8. Explicit I-box register stages.**
- The Y-to-Z transfer, index fetch, modification and WBC as stages
  (Blosk pp.13-14, 31; CE Figs 3.1.6-3.1.24).
- Index storage's destructive read and two-cycle write, and word 17's
  timer path (Blosk p.11).
- The updated-indicator register, with index-indicator branches
  resolved in the I-box (Blosk p.17).
- The five look-ahead counters' separate interlocks, now collapsed
  into head/tail (Buchholz §15.3).
- Done as (a) structure, byte-identical, then (b) the timing.
- Exit: the I-box atlas pages (PDF 106-112) hold. The `ja_ax*` /
  `jb_ax*` I-box diagnostics pass on the model.

**A9. Recovery by levels, as the machine did it.**
- Branch wrong-way recovery and interruption recovery come from
  pseudo-store levels, not snapshot records (Perf. Char. p.3-22; Blosk
  p.33; Buchholz §15.6).
- What `NEXT.md` lists after the store levels:
  - interruptions from sources other than a level;
  - a BD in the latch clocks;
  - the time housecleaning takes (record that no page gives it, if
    none does);
  - stores made ahead into words 0-31 or by T/SWAP/RNX;
  - the two untraced +1 moves;
  - the not-taken SIC's empty store level.
- Exit: the `stored` backstop is reached by a deck, or deleted as
  unreachable. Every recovery deck passes with the records gone.

## Phase 5: the rest of the machine

**A10. ECC: correction and its indicators, and the I-checker
conflicts** (Blosk p.15; Perf. Char. p.3-19). Exit: a deck that
injects a single-bit error in a storage word, sees it corrected and
the indicator set, and a double-bit error detected.

**A11. The exchange as a bus requester with real overlap.**
- Memory-cycle stealing, the priority order and the byte-demand weights
  (`exchange_and_io.md` §4, Buchholz ch.16).
- The disk synchronizer's timing (`disk_subsystem.md` §4).
- I/O stops being a synchronous state machine.
- Exit:
  - `ka_ex1` (BX-0) passes;
  - a deck shows computing continue under a tape read, with the
    printed cycle-stealing cost;
  - the MCP boot still passes.

**A12. The maintenance console** (Blosk p.6): start/stop,
display/store, single step, repeat mode, the index-storage test. It
goes as far as the pages specify, as testbench-visible controls.

## Track B, beside track A

- 0.2 and 0.3 above.
- G3, the assembler (`strap/`; `NEXT.md` "ASSEMBLER COMPLETENESS"):
  - the blank after a radix specifier;
  - decimal-mode `DD`;
  - a blanked name followed by anything;
  - the integer in parentheses on a plain symbol;
  - printed p.166's label printed twice.
- G5, the render-and-mine queue (`source_audit.md`), feeding 0.3.
- The 353 disk plan (`~/.claude/plans/zazzy-noodling-sloth.md`
  D1-D6):
  - D2 (the host image file) and D4 (board bring-up) touch no core
    file, so they run here;
  - D1 and D3 edit `rl_io` and go on track A, after A11 settles
    `rl_io`'s shape.

## Decisions that are the owner's

Each is listed with a recommendation. None blocks the work: the
recommendation is built behind a switch until it is decided.

1. **D/ and the LAAR** (`NEXT.md` "D/ AND THE LAAR", atlas item 14):
   the sources say D/ takes the LAAR, and the atlas has room only if
   the divide is 2 clocks shorter. *Recommend:* follow the sources, and
   settle the divide's length from Fig. 3.8.16 in A4. Read 2026-11-23
   (`sau_pau_spec.md` §7): Fig. 3.8.16 gives D/ = `/` + 5 for one
   remainder-normalization pass (+2 a further pass), one clock under
   Table 2's `/` + 6; the chart draws no wait for the remainder's store.
2. **The shipped machine's two LAARs** (`NEXT.md` 2026-10-25):
   *recommend:* model the shipped machine, the one MCP ran on. Keep
   the one-LAAR reading of Perf. Char. as a switch.
3. **One parallel multiplier or two: SETTLED BY THE SOURCES, one**
   (`sau_pau_spec.md` §6, 2026-11-23). Fig. 3.8.18 says the SAU multiply
   is "IDENTICAL TO FLOATING POINT MULTIPLY"; Figs. 3.11.1 and 3.11.10
   say "WAIT FOR PAU TO MULT AND XFER RESULT TO AB"; Buchholz p.208 and
   Fig. 14.7 show one CSA tree. The divider is shared the same way
   (3.11.8; 3.8.19). A3/A4 build VFL `*` and `/` as an SAU
   byte-assembly, a PAU request, then an SAU unload. No longer the
   owner's decision.
4. **CE Vol. III's word-4 contradiction:** *recommend:* keep the
   Reference Manual's reading (current behaviour), and record the CE
   reading.
5. **The multi-computer word-6 option:** *recommend:* leave it out.
   The project models a single-CPU installation; build it only if a
   source shows MCP depending on it.

## Order, and why

Phase 0 runs now. Then A1 → A2 → A3 → A6 → A7 → A4 → A5 → A8 → A9 →
A10 → A11 → A12.

- A3 comes early because the VFL family is the largest remaining
  timing gap, and the serial unit is also the rewrite's largest
  structural gap: one piece of work closes both.
- A6 and A7 follow because their residuals are measured and their
  causes diagnosed.
- A4 after them: FP is already close.
- A8 and A9 change mechanism more than numbers, so they come once the
  numbers are settled and can show a regression.
- I/O last: MCP already runs on today's I/O, and A11 can be checked
  against a stable core.

The order is re-checked against step 0.1's numbers when they land.
