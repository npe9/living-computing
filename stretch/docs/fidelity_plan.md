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
- **VFL, transmit, branches, Vol. 2 PDF 102-189, 18,249 cases**, master
  `b7187d5` (stretch/ as `3997745`), re-measured 2026-11-23 (`--jobs 6`,
  TSV in the session scratchpad, not committed): median −0.02, mean
  −1.45; 36.6% exact, 48.8% within 1 clock, 61.8% within 3.

  | Pages | n | within 1 | within 3 | median | mean |
  |---|---:|---:|---:|---:|---:|
  | 102-115 I-box, branch, transmit | 167 | 17% | 43% | −4.58 | −18.73 |
  | 116-142 VFL external | 6,290 | 52% | 67% | −0.00 | −0.61 |
  | 143-169 INTERNL / forwarding | 10,188 | 43% | 55% | −0.04 | −2.05 |
  | 170-189 IMMED. | 1,604 | 78% | 90% | −0.00 | +0.97 |

  Where it is off, by cells:
  - **Word-boundary crossover columns** (`*_wbx`, 5,390 cells): 2-10%
    within 3; external median +4.9, internal −9.1. This is A6.
  - **INVERT SIGN blocks** (8,106 cells): 54% within 3 against 68%
    elsewhere. These are Table 3's unlike-sign terms and the compare's
    early end (K family mean +3.8). This is A3.
  - **The M+ family:** M+MG median −10.4, M+1 −4.3, M+ −2.1, with tails
    to −59. These are the store path (A6) and unlike signs (A3).
  - **Transmit:** T median −48 (to −152), TI −29; 0 of 58 cells within
    3. This is A7.
  - **BAL** −32, **`/I`** +32 (A3, the data-dependent divide), **SV / SC /
    SR** −7.5, **`*I+`** −7.
  - Medians at 0 everywhere else. The FP pages are close (above). What
    remains is spread, not offset.
- **Structure** (§1c-audit, against Piccolo): 6 of 8 rows match or do
  not apply. The two that differ:
  - the E-box is still largely an interpreter. When this was written,
    `vflIntOp` was about 2,200 lines and execution made 44 direct
    state writes (`ebox_roadmap.md`). Since A2 (2026-11-25) the VFL
    writes are 0 and 18 remain outside VFL;
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

**0.1 Re-measure the whole atlas on master. DONE 2026-11-23** (above).
The order below stands: A3 (unlike signs, `/I`) and A6 (crossover, the
M+ store path) hold the most cells; A7's transmit is the largest
per-cell error. Exit: a per-family table (n,
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
LA/I-BOX/MEMORY HALF DONE 2026-11-23: `ibox_la_spec.md` (Figs 3.1.6-3.1.24, 3.2.1-3.2.27, §4 Procedure 1; no flow diagram prints a time).
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

DONE 2026-11-25, six commits, one per family, on the batch51 base
(`StretchExecute.bsv` only, plus these docs):
- `VflCommit` (accumulator trio, factor, remainder, transit, field store
  and its core tail) and `commitVfl`. `execute()` applies it after
  `vflIntOp` and after `connectiveOp`, in the same arm and rule as the
  writes it replaces. `vflFieldStore` became the pure
  `vflFieldStorePlan`, with the same DS predicate. `writeAcc`,
  `writeAccFlags` and `vflFieldStore` are deleted, since nothing calls
  them now.
- The thirteen opcode arms were moved verbatim into eight family
  functions. Each is a plain function over `VflCtx` (the preamble's
  values) and `VflArm` (the call's running state). The only text
  changed is at the write sites.
- Lines per function:

  | family | function | lines |
  |---|---|---|
  | add/load | `vflLoadAddFamily` (L, LWF, +, +MG) | 306 |
  | add/load | `vflCompareFamily` (K ... KFR) | 224 |
  | store | `vflStoreFamily` (ST, SRD) | 346 |
  | store | `vflMemAddFamily` (M+, M+1, M+MG) | 315 |
  | multiply/divide | `vflMulDivFamily` (*, LFT, *+, /) | 391 |
  | conversions | `vflConvertFamily` (LCV, CV) | 282 |
  | conversions | `vflConvertTransitFamily` (LTRCV, DCV) | 213 |
  | decimal | `vflDecimalFamily` (LTRS, decimal *, *+, /) | 110 |
  | dispatcher | `vflIntOp` (was 2,200) | 381 |
  | connectives | `connectiveOp` | 336 |

  `vflIntOp` keeps one Action, the unimplemented-code `$display`, and
  `connectiveOp` keeps two. Neither writes state.
- Direct state-write call sites, comments stripped. A site is a call of
  `st.writeWord`, `writeWordTail`, `writeIndex`, `setIndicatorBits`,
  `setConnectiveCounts` or `setLeftZerosCount`, or of a local Action
  helper that makes one.
  - VFL (`vflIntOp` + `connectiveOp`): **25 → 0**. That is 22 + 3:
    `vflIntOp`'s 22 were 13 `writeAcc`/`writeAccFlags`, 6 `writeWord`,
    1 `writeWordTail` and 2 `vflFieldStore`, which counts 1 site for 3
    words.
  - Inside execution (the plan's "44" metric: not `commitFp`, not the
    helper bodies): **43 → 18**. What is left is `execute` 9,
    `dirIndexOp` 7, `ioOpExec` 1 and `mkEBox` 1.
  - Whole file: 60 → 34. Of the 34, `commitVfl` has 8, `commitFp`
    has 7 and the `writeHWWithWord` helper has 1. (An earlier count of 40
    in this section was taken before `writeAcc` and `writeAccFlags`,
    with three sites each, were deleted.)
  - What the zero covers: `vflIntOp`, `connectiveOp` and the family
    functions. Two of `execute`'s nine remaining sites are VFL's: the
    `st.setConnectiveCounts` calls that apply `connCounts` for LTRS and
    for the connectives. They were already a return-and-apply channel
    before A2 (`VflOutcome.connCounts`), and are left as they were.
- Verified:
  - The atlas TSVs (`--tsv`) are byte-identical (`cmp`) to the
    pre-edit baseline for every family state. The VFL pages, PDF
    102-189, are 18,238 cases. The FP pages, PDF 64-101, are 6,592
    cases and were run for the first and last states.
  - The full suite was run in a frozen copy of each state: 15,139 PASS
    on each, the same as the base. The only FAIL lines are the two
    `UNREPRODUCED, expected` p359 lines, twice each. The sorted
    PASS/FAIL lines differ from the base only in temp-directory names
    and in Python's set order within two assembler messages.
  - The smoke section (`make run`, `check_schedule.py`) was run for
    each state on its own.
  - bsc's `mkStretchCore.sched` is identical to the baseline once
    generated signal numbers are normalised.
- Not met: "no execution function over about 400 lines" holds for the
  VFL functions only. `execute` (about 1,540 lines), `fpArithClass`
  (767), `ioOpExec` (495) and `dirIndexOp` (427) are outside A2's
  scope, and so is `mkEBox`, a module of 496 lines.
- No box module changed, so the F1 per-box LUT4 figures stand.
- Left open:
  - The families are plain functions, but they are not free of `st` as
    `fpStoreClass` and `fpArithClass` are. They READ through it: 11
    `st.readAccSign`, 10 `readAcc(st)`, 4 `protViolates(st, ...)`, 3
    `dfSignal(st, ...)` and 1 `st.readFactor`, plus
    `vflFieldStorePlan`'s `protViolates`. Passing those values in is the
    next step toward boxes that can be tested without storage, and
    needs its own verification run.
  - No injection has yet pinned `commitVfl`'s field-to-word mapping
    (for example, swapping `accLeft` and `accRight`). The atlas cannot
    see a swap like that. The suite's value checks are the oracle; the
    injection the roadmap asks for is still to be run.

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

HALF (a) DONE 2026-11-25 (`bsv/StretchSAU.bsv`; `mkEBox`'s three dispatch
sites in `StretchExecute.bsv`; the box testbenches; these docs):
- `mkSAU`: one `(* synthesize *)` module, `request(SauReq)` /
  `responseReady` / `response`, CRegs with the rules on port 0 and the
  methods on port 1 (mkDivBox's discipline), no implicit conditions.
  `SauReq` is a tagged union of the old requests (`DecReq`, `VflReq`,
  `CvtReq`), so the twelve `needsBox` sites in the VFL family functions are
  untouched. `boxKindOf` still numbers the classes 1 (adder), 2
  (converter), 3 (multiplier): StretchCore's `boxReleases` releases the
  level for 1 and 3, not 2, and needed no edit.
- Shared: one state machine, one operand register (`rg_a`: the augend, the
  converter's source, the multiplicand), one result register (`rg_r`: the
  sum, the conversion, the product register), the carry and one counter;
  the add and the recomplement pass through ONE digit-step chain (mkDecBox
  had two). Only one class is ever in flight (mkEBox holds one instruction,
  and an I-box instruction beside it is refused if it would ask a box).
- Rates unchanged, so clocks unchanged: add 8 digits a clock (4, or 8 to
  recomplement), multiply 12 bits (4), convert 16 bits to decimal (6) and 8
  digits to binary (4).
- The old `StretchDecBox.bsv`, `StretchVflBox.bsv`, `StretchCvtBox.bsv` are
  marked SUPERSEDED and are no longer imported or built. They are not
  deleted: AGENTS.md asks first for deleting files not created in the
  session. Removing them is one `git rm` of the three paths.
- Tests: the three box sections of `run_tests.sh` now build `mkSauAddTb`,
  `mkSauCvtTb` and `mkSauMulTb` (the old vectors, literal answers and clock
  counts) on `mkSAU`; a fourth, `mkSauMixTb` (`run_saumix_test.sh`), issues
  the classes back to back to catch state one class leaves for the next.
  Injections, each in a scratch copy, observed sets in the file header:
  sauComp always nines' (add 11-13, the old set); the recomplement pass
  not complementing (add 1, 7, 12 and mix 0); the multiplier's group top
  bit dropped (mul 2, 4-8 and mix 2); dabble at six (cvt 0, 3, 4 and mix
  1); the converter's request not clearing `rg_r` (cvt 1-7 and mix 1, not
  mix 4). The recomplement pass adding the addend is an equivalent mutant:
  the addend has left the register by then.
- Verified, each run in a frozen copy of the tree beside a frozen copy of
  the base (aa415e55), on a private STRETCH_TAPE, with STRETCH_HALT_REPORT=1:
  - The atlas TSVs (`atlas_oracle.py --tsv`) are byte-identical (`cmp`) to
    the base's: VFL pages PDF 102-189, 18,238 cases; FP pages PDF 64-101,
    6,592 cases.
  - The full suite: 15,155 PASS against the base's 15,146; the only FAIL
    lines are the two `UNREPRODUCED, expected` p359 lines, twice each, in
    both. The sorted PASS/FAIL lines differ only by the box testbenches'
    renamed lines (32 old box lines, 32 SAU lines, plus mkSauMixTb's 7),
    temp-directory names, Python's set order in two assembler messages,
    and two `check_schedule.py` lines that the smoke section's `tail -20`
    window shows in one log and not the other (the schedule check passes
    all 16 in direct compiles of both trees).
  - All 384 HALTREPORT lines (every program's halt clock and read count,
    pinned or not) are identical, in order.
  - bsc's `mkStretchCore.sched`, with signal numbers normalised, differs
    from the base only where the canResume predicates name `sau` for
    `decBox` / `cvtBox` / `vflBox`; the rule order lines are identical.
    `check_schedule.py` passes.
- F1 area (`fpga/synth_core.sh OUT TOP hier`, yosys `-noabc9`, each box
  and the unit measured in the same session, 2026-11-25):

  | module | LUT4 | CCU2C | TRELLIS_FF | MULT18X18D |
  |---|---|---|---|---|
  | mkDecBox | 1,099 | 84 | 401 | 0 |
  | mkVflBox | 404 | 30 | 149 | 3 |
  | mkCvtBox | 6,003 | 504 | 269 | 0 |
  | sum | 7,506 | 618 | 819 | 3 |
  | **mkSAU** | **7,001** | **574** | **406** | 3 |

  −505 LUT4 (−7%), −413 FF (−50%). (§11's figures, 1,098 and 5,987, were
  another run of the same script; abc's mapping varies by a few LUTs.)
  F1's rule is NOT met by (a): the converter's 16-bit double dabble and
  8-digit Horner chains are about 6,000 of the LUT4, and the multiplier is
  a 48 x 12 array. Both go when (b) steps them a bit or a digit a pass.

WHERE (b) STARTS: the eboxClocks terms the unit now owns. Each class below
reaches `mkSAU`; for each, `StretchTiming.bsv`'s `eboxClocks` VflInt arm
charges the whole E-box time and StretchCore's `rl_exec_resume` subtracts
`boxClocks` (the unit's own 4-8 clocks) from it. (b) replaces, per class,
the arm's term by the unit's stepping and deletes that subtraction for the
SAU kinds:
- adder (boxKind 1), the `x/y + z` and recomplement terms (Table 3, Fig.
  3.11.9 / 3.11.11 / 3.11.12):
  - `+`, `+MG`, binary and decimal (`vflLoadAddFamily`): eboxClocks'
    `000001, 100001` row, `12 + 2b`;
  - `L`, `LWF`, DECIMAL only (an add to zero): the same row;
  - `M+`, `M+1`, `M+MG`, decimal (`vflMemAddFamily`): the `001001, 101001`
    row and M+1's flat 21/22;
  - `SRD`, decimal, at a nonzero digit offset only (the round's add of
    five; `vflStoreFamily`): the `001101, 101101` row and `srdRound`;
  - `K`, `KE`, `KR`, `KF...`, decimal (`vflCompareFamily`): the `10 + 2b`
    and `8 + 2b` rows, and the immediate compares' adjustment.
- converter (boxKind 2), Table 3's `x + u/8`, `t/4`, `s` terms (Figs
  3.11.4-3.11.7, 3.11.13-14): `LCV` (`vflConvertFamily`), `CV`, `LTRCV`
  and `DCV` (`vflConvertTransitFamily`): the `000011`, `100011`, `011011`
  and `111011` rows.
- multiplier (boxKind 3): `*` and `*+` binary (`vflMulDivFamily`): the
  `011001` and `111001` rows. These move to A4's `mkPAU` with the
  multiplier, and the SAU keeps the byte-assembly loop (MPY 1, Fig.
  3.11.1) and, for `*+`, the add of the product into AB (Fig. 3.11.10).
- NOT reaching the unit, so (b) cannot yet delete their terms: binary `L`,
  `LWF`, `M+` family and K family, `ST` and every `SRD` but the decimal
  round (computed inline in the
  family functions); `LFT`, `LTRS` and decimal `*`/`*+`/`/` (the LTRS
  action); `/` (mkDivBox, the PAU's); the connectives (`connectiveOp`).
  Each must first send its byte loop through the adder.

HALF (b), FIRST STEP DONE 2026-11-25: THE ADDER TERMS OF L, LWF, + AND +MG
(`bsv/StretchSAU.bsv`, `StretchExecute.bsv`'s `vflBinAddSteps` /
`vflDecAddSteps` and `boxOwnClocks`, `StretchCore.bsv`'s `rl_exec_resume`,
`StretchTiming.bsv`'s `sauSteppedRowClocks`, `StretchVFL.bsv`'s `vflBytes`):
- What changed:
  - The four classes' requests carry their passes (`SauAddSteps`: the
    field's data bytes and sign pass, from `vflBytes`, the count
    `eboxClocks` uses; where z is looked at; os/r and x/y for the
    recomplement). The binary L and LWF arms do not reach the unit, so
    their row is untouched.
  - `mkSAU` answers such a request after 2 clocks a pass (Buchholz printed
    p.209; Table 3's .6 a byte, Vol. 1 printed p.3-7): the field's passes,
    Table 3's z (glossary printed p.3-10: a pass for each byte the carry,
    or with unlike signs the borrow, propagates into), and on "CD > AB"
    the recomplement, os/r + x/y + z + 1 for `+`, 1 for `+MG`. It reports
    that count (`ownClocks`).
  - `rl_exec_resume` then charges the `eboxClocks` row LESS its byte term
    (`sauSteppedRowClocks`, 2 clocks a byte with the sign byte) and takes
    NO box clocks off: the subtraction is dropped for these four. Every
    other class keeps half (a)'s contract (row charged whole, box clocks
    subtracted): the M+ family, the K family, decimal SRD's round, the
    converter and the multiplier.
  - The add datapath is now 16 digits a clock (was 8), so the sum is never
    later than the stepping (a one-pass field is 2 clocks). It is still
    not the byte-wide datapath the passes describe: the clock count is
    the stepping's, the width is F1's.
  - An UNSTEPPED add still answers at half (a)'s 4 clocks (8
    recomplemented). MEASURED on a first full run that let them answer at
    the new datapath's 2 / 4: M+, M+MG, M+1 and the K family moved 246
    atlas cases (88 toward, 158 away; one-digit fields 1 clock faster, the
    relocation's signature below). With half (a)'s time kept they do not
    move at all (the full-atlas table below).
- A borrow that runs off the left end (the recomplement case) is NOT
  stepped: z = 0 there. Counted, it put `+MG` INVERT (DU,64,4) 34 clocks
  over PDF 118 (16 digit passes to the end + 1), where Table 3 charges +MG
  ".6" alone. DERIVED reading: Fig. 3.11.9's EHOM1 test ends the loop.
- The three steps, measured one at a time, on the pages of these
  instructions (PDF 116, 118, 120, 121; forwarding 143, 145, 147, 148;
  immediate 171-174; 3,260 cases), each against the step before.
  "toward/away" = |residual| fell/rose by more than 0.05 clock:

  | step | within 1 before -> after | within 3 before -> after | toward | away |
  |---|---|---|---|---|
  | relocation (byte term moved into the unit, no z, no recomplement) | 1,807 -> 1,811 | 2,312 -> 2,314 | 44 | 28 |
  | + Table 3's z (`sauStepZ`) | 1,811 -> 2,066 | 2,314 -> 2,303 | 798 | 344 |
  | + the recomplement (`sauStepRecomp`) | 2,066 -> 2,106 | 2,303 -> 2,300 | 40 | 12 |
  | all three against the base | 1,807 -> 2,106 | 2,312 -> 2,300 | 858 | 376 |

  - The relocation is not neutral, and says where the hold sits: a
    one-byte field's box hold is 2 clocks now (was 4) and its level
    retires 2 clocks sooner, with the same total. 28 cases (one-byte `+`,
    `+MG` (BU,1,8) / (BU,8,8) and decimal L, LWF (DU,4,4) / (D,4,4), INDEXING
    EXTERNL) come out 1 clock faster, away from the page (-1.05 -> -2.05);
    44 forwarding cases (PDF 143-148, ix_ext) move +0.25 toward it. Not
    diagnosed further.
  - z's 344 away: 304 are in the two WB XOVR columns, where the model was
    already 3-5 clocks OVER the page before this (the crossover's own
    charge, "WB XOVR in general" in `atlas_oracle.md`), and z adds the same
    carries there as in every other column. The other 40 are signed fields,
    binary (B,n,1) 0 -> +0.53 and decimal (D,8,4) 0 -> +0.89: every one
    stays within 1 clock. No non-crossover case leaves the 1-clock band.
    KEPT, on that reading; the crossover excess is the store/fetch path's
    (A6), not the adder's. CHECKED on the TSVs: after z, `+` and `+MG`
    sit in both WB XOVR columns at a median +4.99, the same constant as L
    and LWF (+4.97, which have no z and did not move): z brings the adds
    ONTO the crossover's constant, it does not overshoot it. This keeps a
    term against the brief's per-column rule (0 toward, about 80 away in
    each WB XOVR column), and is the owner's call; the alternative,
    `sauStepZ := False`, leaves the 3,260 cases at 1,811 within 1 and
    2,314 within 3.
  - The recomplement's 12 away are WB XOVR INVERT SIGN (`+MG` (BU,64,8)
    +3 -> +5). Its 40 toward are the same instruction's other columns
    (-2 -> 0).
- MCP boot (the six `run_mcp_*` IPL / P1 sections, `STRETCH_HALT_REPORT`),
  after the relocation and after all three: every check passes both times.
  Halt clocks against the base: relocation -10, -10, -10, +8, +25; all
  three -2, -2, -2, +16, +65 (boot, decode, assign, past-move, p1deck);
  after the relocation and z alone (recomplement off, the final tree's
  unstepped timing) -2, -2, -2, +16, +33, every check passing.
  No term broke the boot, so no budget term was found covering a memory
  access.
- THE WHOLE VFL ATLAS (PDF 102-189, 18,238 cases) against the half (a)
  base: within 1 clock 8,905 -> 9,204, within 3 11,286 -> 11,274; 858
  toward, 376 away -- exactly the 3,260-case table's moves, and no case of
  any other instruction moves. Exact cases 7,099 -> 7,769, mean |residual|
  5.16 -> 5.13 clocks. Per instruction (within 1 before -> after, toward /
  away): `+` 308 -> 406, 302 / 206; `+MG` 281 -> 426, 380 / 162; `+I` 64 ->
  96, 84 / 0; `+MGI` 38 -> 62, 84 / 0; L and LWF 462 -> 462, 4 / 4 each;
  LI, LWFI unchanged.
- MOVED PINS (both MODEL pins, both from the relocation alone: the same
  count with z and the recomplement switched off, in scratch copies):
  `decks/vfl_srd.strap` CYCLES 1290 -> 1294 (its decimal L(DU,16,4) holds
  its level 8 clocks, not 4) and `decks/dec_box_release.strap` CYCLES 859
  -> 868 (its decimal L and + likewise). The atlas's own L and + pages at
  those fields do not move; no page measures these sequences.
- THE FULL SUITE, in the worktree after the merge of master (f69982ed),
  private STRETCH_TAPE, STRETCH_HALT_REPORT=1, 2026-11-25 19:57-22:04:
  "All regression tests passed"; the only FAIL lines are the two
  `UNREPRODUCED, expected` p359 lines, twice each. Halt clocks that moved
  (10 of 384 HALTREPORT lines; no read count moved): MCP-DECODE 6,304,300
  -> 6,304,298; ASSIGN 6,322,789 -> 6,322,787; PAST T MOVE 6,339,173 ->
  6,339,189; MCP p.1 IOD deck 6,734,459 -> 6,734,524; decimal-adder box
  release 859 -> 868 (pinned); Figure 14 sign-modifier deck 162 -> 168;
  MCP per-card path p.17 692 -> 694; +MG Figure 12 544 -> 548;
  look-ahead L/+/ST/V+/CB loop 924 -> 916; Figure 7 progressive indexing
  708 -> 694. None but the pinned one is pinned.
- Unit test: `mkSauStepTb` (`tests/run_saustep_test.sh`), ten literal
  vectors. Injections, each in a scratch copy: `sauStepZ` off fails 1, 2,
  3, 5 (the carry and borrow vectors); `sauStepRecomp` off fails 4 and 7
  (7 on `ownClocks`, since the datapath's recomplement still takes 4).
- NOT RE-MEASURED: mkSAU's F1 area (the 7,001 LUT4 above is half (a)'s;
  the 16-digit chain, the carry register and the request's 128-bit add are
  new); the FP atlas pages (the FP halt lines are unchanged). No suite
  check pins z or the recomplement THROUGH THE CORE: both moved pins come
  from the relocation alone (candidates: the Figure 12 `+MG` and Figure 14
  decks, whose unpinned halt clocks moved).
- LEFT for (b): the M+ family (Table 3: .6(x/y), unlike AB > CD .6(x/y +
  1); M+1 .6(c + 1)), the K family (.6(x/y + w/r) and the early exit on an
  inverted sign, the +28), decimal SRD's round (no page at a nonzero
  offset: `vfl_srd.strap`'s pin and Table 3 decide it), then the
  converter rows; the relocation's one-byte -1 (above) undiagnosed; the
  byte-wide datapath (F1). The multiplier terms are A4's.

HALF (b), STEP 2 DONE 2026-11-26: THE DECIMAL M+ FAMILY (M+, M+MG, M+1)
(`StretchSAU.bsv`'s `SauStepCls` / `SauStMem` / `SauStOne`, `StretchExecute.bsv`'s
`vflDecFieldSteps`, `StretchTiming.bsv`'s `sauRowWithUnit`, which replaces
`sauSteppedRowClocks`):
- Pins for step 1's terms through the core came first (commit 73dc325b):
  `fig14_sign_modifiers.strap` CYCLES=168 and `plus_mg.strap` CYCLES=548.
  `sauStepRecomp := False` gives 162 / 546; `sauStepZ := False` leaves both
  at 168 / 548, so z is still unpinned through the core.
- `SauAddSteps` carries a `cls`, the Table 3 row group (Vol. 1 printed p.3-7,
  PDF 25, read in the image), and the unit steps each class by its own
  equation:
  - M+, M+MG: .6(x/y); "Unlike signs AB > CD, add .6(x/y + 1)". There is no
    z.
  - M+1: .6(c + 1); unlike signs .6(x/y) for the true result, .6(2x/y + 1)
    for the complement.
  - The switches are `sauStepMemRecomp`, `sauStepOneCarry` and
    `sauStepOneComp`.
- The row's own term is now taken out per class (`sauRowWithUnit`).
  Step 1's `2b` cut would underflow M+1's flat 21/22.
  - M+ and M+MG are charged max(R, 17 - f + u). R is the row, f = 2 for a
    whole unsigned word, u = the unit's clocks. With like signs this is
    exactly R. The row's floor of 21 + b at one or two bytes stays a
    floor, which is not the adder's.
  - M+1 is charged max(R, 15 + u). The INVERT rows of PDF 126 print 16 +
    2b from (DU,16,4) up, Table 3's true-result count over a fixed 16.
- Only DECIMAL M+ reaches the unit. Binary M+, M+MG and M+1 are computed
  inline and their rows did not move. Their INVERT rows (BU and B) carry
  the same -2..-26 residuals.
- Atlas, the M+ pages (PDF 117, 119, 126; forwarding 144, 146, 153; 2,150
  cases). Each run is in a frozen copy with `--rebuild`. A first `all`
  run reused the relocation's simulator, because rsync keeps the source
  mtime, and showed no moves. It was discarded.
  - CORRECTED 2026-11-26 (step 3). The `all` run recorded at commit
    fee9be22 was ALSO partly stale. bsc's `-u` reused a `.bo` compiled
    with `sauStepOneComp` off, so that run equals a fresh run with that
    switch off, case for case.
  - The table below is the fresh re-measurement: `meas.sh` touches the
    synced sources, and the tree is 6af7078f plus step 3, which touches
    no M+ path.

  | step | within 1 before -> after | within 3 before -> after | toward | away |
  |---|---|---|---|---|
  | relocation, with M+1's unlike x/y (`sauStepMemRecomp`, `...OneCarry`, `...OneComp` off) | 572 -> 630 | 984 -> 1,046 | 151 | 75 |
  | + all three switches on | 630 -> 738 | 1,046 -> 1,157 | 271 | 13 |
  | of which `sauStepOneComp` (the M+1 complement; the rest is M+ / M+MG's recomplement) | 732 -> 738 | 1,157 -> 1,157 | 31 | 11 |
  | all against batch55 | 572 -> 738 | 984 -> 1,157 | 396 | 54 |

  - **Relocation.** M+1's unlike signs now cost .6(x/y). This takes PDF
    126's INVERT (D,32..64,4) from -10..-26 to within 0.4 (121 toward for
    M+1).
    - The 75 away are all 2 clocks or less: the one-byte hold shift of
      step 1, which is not diagnosed further, plus WB XOVR columns already
      23 or more under the page (A6).
    - 22 of the 75 stay within 1 clock.
  - **The recomplement.**
    - M+MG's decimal INVERT rows, D and DU at every field and every
      column, land within 0.75 clocks: for example (DU,48,4) ni_ext goes
      from -26.0 to -0.01.
    - M+'s unsigned INVERT rows move HALF way, for example (DU,32,4) from
      -18 to -9. M+ rewrites its own operand, and in the model the
      atlas's repetitions alternate: 0 - 444 recomplements and stores
      444, then 444 - 444 = 0 does not. The page recomplements on every
      repetition. One candidate is that the machine recomplements on
      equal magnitudes as well (a nines'-complement end-around carry).
      That candidate is NOT implemented, because no source has been
      found.
    - M+ (DU,64,4) INVERT goes from -17 to +17. In the model every
      repetition recomplements there, while the page charges half. This
      is not explained.
    - The term is KEPT: 240 toward, 2 away. The 2 away are M+ (DU,64,4),
      both inside 0.05 of the same magnitude on the other side.
  - **M+1's c term** moves no atlas case (a fresh `sauStepOneCarry :=
    False` run is identical case for case). With the atlas's operand +1,
    no M+1 repetition carries out of a digit. `mkSauStepTb` carries it.
  - **M+1's complement term** moves the unsigned INVERT rows (PDF 126,
    153): 31 toward, 11 away.
    - Toward: for example PDF 153 (DU,16,4) ni_ext goes from -1.83 to
      +0.94, and (DU,8,4) ni_ibox from -2.23 to +0.23.
    - Away, 5 cases: (DU,4,4) and (DU,8,4) cells that move by 0.5 to 3
      clocks, all still within 1.7.
    - Away, 6 cases: PDF 153's INTERNAL columns at (DU,32..64,4), which
      go from about 0 to +9..+17. Every one of those cells' operands is
      the oracle's own CHOSEN value: the accumulator's left word, which M+1
      rewrites at each repetition (`atlas_oracle.py`, "The operand is
      whatever the accumulator set-up left there ... CHOSEN"). At the same
      fields, the external and I-box columns, whose operand the page
      gives, do not move and stay within 1.
    - The term is KEPT on its source (Table 3's comment column). The
      large excess is in cells the page does not define.
- `mkSauStepTb`: vectors 10-16 (literal sums and clocks). Injections, each
  in a frozen copy:
  - `sauStepMemRecomp := False` fails 11 (4 against 10);
  - `sauStepOneCarry := False` fails 13 (2 against 8);
  - `sauStepOneComp := False` fails 16 (8 against 18);
  - nothing else fails.
- MCP boot sections (`STRETCH_HALT_REPORT=1`, private tape): every check
  passes. Halt clocks are unchanged from batch55: boot 6,321,488, decode
  6,304,298, assign 6,322,787, past-move 6,339,189, p1deck 6,734,524. MCP
  runs no decimal M+.

HALF (b), STEP 3 DONE 2026-11-26: THE DECIMAL K FAMILY (K, KE, KR, KF, KFE, KFR)
(`StretchSAU.bsv`'s `SauStCmp` / `SauStCmpF`, `sauStepCmpW`, `sauStepCmpEarly`,
`sauStepCmpWLiteral`; `StretchExecute.bsv`'s compare request):
- Source: Table 3 (Vol. 1 printed p.3-8, PDF 26, read in the image). K, KE
  and KR cost .6(x/y + w/r). KF, KFE and KFR cost .6(x/y). The glossary
  (printed p.3-10, PDF 28) defines w as "the number of accumulator
  significant bits greater than the field length".
- The decimal compare is a stepped subtraction in mkSAU. The row's K arm
  is 7 + u (`sauRowWithUnit`, from step 2). The immediate compares are
  not stepped and keep half (a)'s contract.
- **w.** It is stepped as ONE pass when the accumulator has a significant
  digit beyond the field, and none when it has none. This is DERIVED: the
  loop past the field ends at the first nonzero byte, which decides the
  compare. PDF 127-129 print K exactly one byte over KF at every field
  below 64 bits against the standard 64-bit operand, and no extra byte at
  a whole unsigned word (w = 0).
- **The literal w/r** counts every digit up to the accumulator's highest
  significant one. It is kept as a switch and REJECTED by measurement.
- **The early exit (the +28).** A compare that the signs decide (unlike
  signs, neither one zero) takes the sign pass, one data pass and K's w
  pass. PDF 127-132's INVERT SIGN blocks print 12 clocks unsigned and 14
  signed at every length. The early exit is DERIVED from sau_pau_spec.md
  section 5 (3 of the 9 paths of Fig. 3.11.12 reach TON SIR without
  EOC1/EOC2). The pass count is read off the pages.
- Atlas: the K pages (PDF 127-132; forwarding 154-159; immediate 177-182;
  4,896 cases). Each run is in a frozen copy with `--rebuild`.
  - A first `all` run was identical to the `w` run and was discarded.
    The cause was not the testbench: `rsync -a` restored StretchSAU.bsv
    with its old mtime, so bsc's `-u` reused the `.bo` compiled with the
    switch off. `meas.sh` now touches the synced sources.
  - The table's last column pair is toward / away.

  | step | within 1 before -> after | within 3 before -> after | toward | away |
  |---|---|---|---|---|
  | relocation (K's 10 against KF's 8 taken out of the row; `sauStepCmpW`, `sauStepCmpEarly` off) | 2,114 -> 1,948 | 2,816 -> 2,830 | 268 | 492 |
  | + w | 1,948 -> 2,114 | 2,830 -> 2,794 | 268 | 340 |
  | + the early exit | 2,114 -> 2,264 | 2,794 -> 3,050 | 408 | 76 |
  | all against batch55 | 2,114 -> 2,264 | 2,816 -> 3,050 | 410 | 258 |
  | literal w/r instead (against all) | 2,264 -> 1,974 | 3,050 -> 2,676 | 32 | 560 |

  - Per instruction, all against batch55: K and KR 106 toward / 62 away
    each, KF and KFR 99 / 67 each. KE, KFE and the immediates do not
    move.
  - **The relocation and w, split by cell** (`tsvdiff.py --rows`; WBX =
    the WB XOVR columns, which are A6's; INV = the INVERT SIGN block).
    - The relocation's 492 away:
      - 196 are non-WBX plain cells going from -0.0 to -2.0: K's extra
        byte taken out, which w puts back;
      - 252 are WBX;
      - 44 are non-WBX INV.
    - w's 340 away:
      - 164 are non-WBX INV, already +2..+28 above the page. Their excess
        is the early exit, which is off at that stage: with it on, those
        rows land (below).
      - 164 are WBX.
      - Only 12 are non-WBX plain cells, each within 2.05 (for example
        (D,8,4) ix_ext -1.05 -> -2.05).
    - w's 268 toward include 184 non-WBX plain cells: the relocation's
      -2s restored.
    - All three terms against batch55, 258 away: 208 WBX, 34 non-WBX INV
      (the early exit's ix_ext cells below) and 16 non-WBX plain cells,
      every one within 2.05.
    - w is KEPT: its source is Table 3's w/r, and its away cells are
      attributed (the then-absent early exit, A6's WBX columns).
  - **The early exit.**
    - The decimal INVERT rows land on the page: for example K INVERT
      (DU,16,4) ni_ext goes from +5.97 to -0.02.
    - Of the 76 away:
      - most are `_int_wbx` columns, which go to -9.1 (A6's WB XOVR
        timing);
      - the rest are ix_ext INVERT cells, which go to about -2.05. The
        page prints 16.07 there, 2 clocks over the signed direct column
        (14.0) and 4 over the unsigned (12.03); the model's indexed
        column is 2 over its direct one. The missing clocks are in the
        indexed path, not in the unit, so they are not attributed to this
        term.
    - The term is KEPT.
- `mkSauStepTb`: vectors 17-21. Injections, each in a frozen copy:
  - `sauStepCmpW := False` fails 18 and 20 (4 against 6 each);
  - `sauStepCmpEarly := False` fails 20 (10 against 6) and 21 (8 against
    2);
  - `sauStepCmpWLiteral := True` fails 18 (8 against 6);
  - nothing else fails.
- Decks: every K deck and both pins pass unchanged (vfl_decimal_compare,
  vfl_compare_field, vfl_compare_offset).
- MCP boot sections: every check passes, and the halt clocks are
  unchanged from step 2.
- Binary K is computed inline and does not reach the unit. Its rows did
  not move.

HALF (b), STEP 4 DONE 2026-11-26: DECIMAL SRD'S ROUND (`SauStRnd`, `sauRndPasses`)
- Sources:
  - Fig. 3.11.11 Part 2 (R23-9732 PDF 265; `sau_pau_spec.md`) draws the
    round as two cycles before the store loop: [TOF HK TON RSU] and [TOF
    RSU TON RND].
  - Table 3 (Vol. 1 printed p.3-7, PDF 25) charges SRD a pre-execution of
    3.0 us against ST's 1.8: 1.2 us, two 0.6 us cycles.
  - The two sources agree with each other and with eboxClocks' 4-clock
    `srdRound`.
- The decimal round (nonzero offset) is now a stepped request of two
  passes, and the row's SRD arm is R - 4 + u (`sauRowWithUnit`).
- No pin moves: `vfl_srd.strap` stays at CYCLES=1294 and the reproducer
  passes. No atlas page times SRD at a nonzero offset, so there is no
  atlas table.
- `mkSauStepTb` vector 22. Injection observed: `sauRndPasses := 1` fails
  22 alone (2 against 4).
- MCP boot sections: every check passes, and the halt clocks are
  unchanged from step 2.

HALF (b), STEP 5 DONE 2026-11-26: THE CONVERTERS (LCV, LTRCV, CV, DCV)
(`StretchVFL.bsv`'s `vflCvtFieldPasses`, `StretchSAU.bsv`'s `SauCvtSteps` /
`sauStepCvtAcc`, `sauRowWithUnit`'s converter arms):
- Source: Table 3 (Vol. 1 printed pp.3-8, 3-9, PDF 26-27, read in the
  image), in 0.6 us passes:

  | instruction | B-D | D-B |
  |---|---|---|
  | LCV | .6(x + u/8 + 1) | .6(x/y + t/4 + u/8 + 4) |
  | LTRCV | .6(x + 3), + .6(FLc/8 - 1) beyond 48 bits | .6(x/y + 16), + .6(t/8 - 1) beyond 48 bits |
  | CV | .6(s + u/8 + 1) | .6(s/4 + 1) |
  | DCV | .6(s + u/8 + 1), full word 63.0 us | .6(s/4 + 2) |

- `CvtReq` carries `SauCvtSteps {fixed, accS}`.
  - `fixed` holds the passes the FIELD decides (`vflCvtFieldPasses`).
  - With `accS`, the unit adds s from the source and, binary to decimal,
    u/8 from its result: the accumulator terms of CV and DCV.
  - The unit's time is max(2 x passes, the datapath's own clocks).
- The row's own part is taken out per class:
  - LCV and LTRCV: R - 2 x field passes + u.
  - CV and DCV: less the passes their equation counts at the accumulator
    the row was fitted to ("+1 at offset 20", PDF 113: s = 1, u/8 = 1),
    so that accumulator keeps the row's time and any other is charged
    its own s and u.
- **DCV D-B is NOT stepped from the data.** Its s/4 is held at the fitted
  1 (3 passes).
  - MEASURED: with the term on, the model's CHOSEN DCV D-B field (every
    digit from the offset to the left end) gives s/4 = 6 at the atlas's
    first DCV (the accumulator reads 0x100000). Each repetition then
    re-reads the previous binary result as BCD, so the operand grows: a
    trace of PDF 139 (D,16,4) shows v growing from 0x100000 to
    0xbc48e3997634329059a98000000 over twelve repetitions.
  - PDF 139 and 166 print a flat 18 clocks at every field. The term
    moved all 96 of those cells by +55.8 clocks.
  - Either the CHOSEN field or the term's reading is wrong. Which is
    OPEN; nothing attributes the excess elsewhere.
- Atlas, the converter pages (PDF 136-139, 163-166, 186, 187; 2,000
  cases): against batch55, within 1 1,076 -> 1,076, within 3 1,408 ->
  1,408, 0 toward, 0 away. Every atlas converter cell is at the operand
  its row was fitted to, so nothing moves by construction. The steps
  show off the atlas.
- Pins and decks:
  - `vfl_dcv.strap` CYCLES 1027 -> 1440, re-pinned. Its B-D DCVs convert
    up to 80 significant bits (10^24) and now take their s and u. The
    cause is MEASURED: `sauStepCvtAcc := False` gives 1027 again, with
    every value check passing.
  - `cwf_df_fetch_type.strap` CYCLES 6110 -> 6164, re-pinned after the
    first full suite run caught it. The switch's terms reach only the CV
    and DCV B-D requests (the only ones carrying `accS`), and the deck
    has one CV(BU) and one DCV(B); which of the two takes how much was
    not traced. The cause is MEASURED: `sauStepCvtAcc := False` gives
    6110 / 581 again, with every check passing.
  - `vfl_convert.strap` (CV and LTRCV, MCP's time conversion) has no
    cycle pin. It now reads 616 (598 at batch55) and passes.
- `mkSauStepTb` vectors 23-27 (conversions, compared on r and clocks).
  Injections observed:
  - `sauStepCvtAcc := False` fails 24 (6 against 26), 25 (4 against 10)
    and 26 (4 against 6);
  - the field term ignored (`rg_cnp` set to 1 + s instead of `fixed` +
    s) fails 26 (4 against 6) and 27 (6 against 22);
  - nothing else fails.
  - Vector 23 does not discriminate (the datapath floor).
  - No check sees `vflCvtFieldPasses`' formula THROUGH THE CORE. The
    atlas cancels it by construction, and no deck pin moves with it. The unit
  still supports a D-B `accS` (vector 26); only the core's DCV D-B
  request leaves it off.
- MCP boot sections: every check passes. The halt clocks MOVE:

  | section | batch55 | `sauStepCvtAcc` off (measured before DCV D-B's `fixed` went 2 -> 3) | final |
  |---|---|---|---|
  | boot | 6,321,488 | 6,321,488 | 6,321,488 |
  | decode | 6,304,298 | 6,304,298 | 6,304,298 |
  | assign | 6,322,787 | 6,322,787 | 6,322,807 |
  | past-move | 6,339,189 | 6,339,195 | 6,339,215 |
  | p1deck | 6,734,524 | 6,734,452 | 6,734,492 |

  - Steps 2-4 leave every MCP halt clock unchanged, so the moves are the
    converters'.
  - The accumulator terms account for the difference between the switch-
    off column and the final one: assign +20, past-move +20, p1deck +40.
  - NOT ATTRIBUTED: the moves that remain with the switch off, past-move
    +6 (memory reads -2) and p1deck -72.
    - LCV and LTRCV cancel by construction at u = 2 x passes. So those
      moves are not the field term as such, unless the datapath floor
      (max(2 x passes, the box's clocks)) exceeds the passes there.
    - MEASURED 2026-11-26, after the suite: with `boxOwnClocks` gated
      back to `boxKind == 1` (converters stepped but not unit-owned;
      reverted, no diff), assign 6,322,787 and p1deck 6,734,524 return
      to batch55.
      - So p1deck's -72 is the unit-owned charge route itself. A `sauOwn`
        instruction is charged `sauRowWithUnit` instead of the level
        path's budget against `boxK`, and drops `boxX`. This is a
        mechanism, not a sourced time.
    - Past-move stays at 6,339,195 (reads 599,502) with the gate back.
      Its +6 / -2 is outside that route and is OPEN.
  - A trace of the assign section shows seven LCVs (9 field passes, no
    accumulator term) and three CV / DCV B-D. Two of the B-D convert 34:
    s = 6 bits, u/8 = 1, so 8 passes against the fitted 3, +10 clocks
    each. That is assign's +20 exactly.
  - Past-move's memory reads go 599,504 -> 599,502.

HALF (b), WHAT IS LEFT AFTER STEP 5 (2026-11-26). This supersedes the
"LEFT for (b)" line under step 1.
- Every class the plan named now steps in mkSAU: the adds (step 1), the
  M+ family (2), the K family (3), SRD's round (4) and the converters (5).
- BINARY M+, M+MG, M+1 and K are computed inline and do not reach the
  unit. Their INVERT rows keep their residuals.
- OPEN, undiagnosed:
  - step 1's one-byte hold shift;
  - M+'s unsigned INVERT half way (the alternating repetitions) and M+
    (DU,64,4) INVERT at +17;
  - M+1's complement on PDF 153's internal columns (the CHOSEN operand);
  - the K ix_ext INVERT cells at -2 (the indexed path);
  - DCV D-B's s/4 against the CHOSEN field (step 5);
  - MCP past-move's +6 clocks / -2 reads from the converter patch,
    outside the unit-owned route (step 5);
  - the unit-owned route's own effect on p1deck (-72), a mechanism with
    no sourced time (step 5);
  - the WB XOVR columns, which are A6's.
- NOT RE-MEASURED:
  - mkSAU's F1 area;
  - the full VFL atlas in one run (each step measured its own pages);
  - z through the core (`sauStepZ` still moves no pinned deck).
- The byte-wide datapath (F1) remains. The multiplier terms are A4's.

**A4. `mkPAU`, the parallel arithmetic unit.**
- `mkFpBox` and `mkDivBox` are absorbed into one unit with its A/B and
  C/D registers (Buchholz §14.4; CE 3.8.x).
- The open decision "one parallel-unit multiplier, not two"
  (`NEXT.md`, 2026-11-19) is settled here from the charts.
- Also from the stepping: `*+`'s sum (the −28 tail), COMPARE, and the
  square root (`NEXT.md` "THE FP BOX'S REMAINING CLASSES").
- Exit: the FP pages hold or improve on today's 76.8% within 1 clock,
  and `*+` / `D+` meet the rule.

*A4 record, 2026-11-26.*

- **Step 1, RELOCATION (done).** `mkPAU` (`bsv/StretchPAU.bsv`) is
  one `(* synthesize *)` module with one `request(PauReq)`, one
  `responseReady` and one `response` (`PauRsp`, tagged FP or divide).
  It holds the FP class (mkFpBox's multiply passes and the add's
  one-clock datapath) and the divide class (mkDivBox's restoring
  steps and the 7030 reduction-loop walk).
  - Registers: `rg_ab` (96 bits, the "AB 12-107" span) is the
    multiply's product register and the divide's dividend/quotient
    register. `rg_cd` (48 bits, "C 12-59") is the multiplicand and
    the divisor. Both are shared by the two classes (Buchholz §14.4
    p.208, PDF 233; `sau_pau_spec.md` §2 item 1).
  - The FP request clears a pending divide's walk. Two separate boxes
    never had to.
  - Every class steps exactly as its old box did.
  - `mkEBox` asks one `pau` where it asked two boxes. These are the
    only `StretchExecute.bsv` lines touched.
  - `StretchFpBox.bsv` and `StretchDivBox.bsv` were removed with
    `git rm` (owner approval, 2026-11-25). Their headers are kept
    inside StretchPAU.bsv under their own headings, and the docs'
    pointers now read "StretchPAU.bsv (was ...)".
  - Verified:
    - The unit benches pass: `mkPauFpTb` (the old mkFpBoxTb vectors),
      `mkPauDivTb` and `mkFpDivSketchTb` (the old mkDivBox benches),
      47 checks in all.
    - The NEW `mkPauMixTb` passes 7/7. It runs the classes back to
      back with a stale-register order, and its vector 6 is a divide
      abandoned two clocks in.
    - Its injections were observed:
      - P (the FP request not clearing the walk): mix 6 alone fails
        (22 clocks, want 4).
      - Q (the divide not clearing the remainder): mix 3 fails, as do
        mkPauDivTb 1, 4-8 and 10-12.
    - The full suite is GREEN (2026-11-26). Its only FAIL lines are the
      two expected `UNREPRODUCED` p359 ones.
    - All 386 HALTREPORT lines are identical, in order, to a GREEN run
      of the base (e9c4b96b).
    - The FP atlas (PDF 42-101, 9,406 cases) at the base is 76.8% /
      94.3% within 1 / 3, which is the plan's baseline reproduced.
    - The relocated tree's own atlas was not run, to save machine time.
      What stands in for it is the step-3 tree's atlas: that tree
      contains the relocation, and on it every one of the 9,086 cells
      off the `*+` pages has a model time identical to the base (largest
      difference 0.0).
- **Step 2, ONE MULTIPLIER OR TWO: ONE (settled from the sources).**
  The sources were re-read for A4, and the answer is one multiplier,
  with the divider shared the same way. Decision 3 below and
  `sau_pau_spec.md` §6 already recorded it. The sources:
  - Buchholz §14.4, printed p.208 (PDF 233, text layer): "a parallel
    unit for floating-point operations and a serial unit for
    variable-field-length operations"; "The two units use the same
    arithmetic registers"; and "variable-field-length binary multiply
    and divide operations are performed by the parallel unit".
  - Buchholz Fig. 14.7, printed p.210 (PDF 235): one multiplier
    ("12 bits of the multiplier are handled in one cycle").
  - R23-9732 Fig. 3.8.18, printed 8-22 (PDF 242, left; the page is
    dated 2/1/62). Re-read on the page image 2026-11-26: "IDENTICAL TO
    FLOATING POINT MULTIPLY BETWEEN THESE POINTS FOR BOTH SAU MULTIPLY
    AND MULTIPLY AND ADD", "A CHECKER RETURNS CONTROL TO SAU", "SAU
    RESUMES CONTROL (BEGINS ADDITION)".
  - R23-9732 Figs. 3.11.1 (PDF 255) and 3.11.10 (PDF 264): the SAU
    waits for the PAU to multiply and transfer the result to AB.
    Fig. 3.11.8 (PDF 262) is the VFL divide's "PAU START VFL DIVIDE",
    and 3.8.19 gives "REDUCTION CYCLES JUST LIKE FP".
  - What it means for the model:
    - FP `*`/`D*`/`*+` and both divides are now in `mkPAU` (step 1).
    - The VFL binary multiply is still mkSAU's `rl_mul`
      (StretchSAU.bsv). Moving it into `mkPAU` changes mkSAU's
      internals, which this item was told to leave alone, so it is
      left OPEN as the one remaining piece of "one multiplier".
    - The move is SAU byte assembly, then a PAU request, then an SAU
      unload, which is the shape the VFL divide already has.
    - It changes no time while only one instruction is in the E-box.
- **Step 3, STEPPING `*+`'s SUM (done; the plain add measured, held
  off).** `*+` is now one chained `FpMulAdd` request: four multiply
  passes, then an add pass on `rg_ab`'s product (`pauChainMulAdd`).
  The answers are unchanged; `mkPauStepTb` checks them bit for bit
  against the arm's old `fpAddDouble`.
  - Table 2's `*+` execution terms (printed p.3-4, PDF 22) come from
    that pass's own counts and are charged through `fpExtra` and
    `mkEBox.boxCharge`, the divide's route:
    - "1 cycle for each additional pre-shift of 4" (`pauMaPreshift`);
    - "2 cycles for each additional norm. of 6" (`pauMaNorm`);
    - "2 cycles if recomplement is necessary" (`pauMaRecomp`).
  - A further term is CHARTED but OFF: Fig. 3.8.13's "IF ACCUMULATOR
    EXPONENT IS SMALLER USE THIS TIMING", three periods
    (`pauMaAccSmaller`). That path is the accumulator going through the
    pre-shifter, which Table 2's pre-shift term already charges. The
    chart's periods are not Table 2's cycles, and the only cells it
    moves are moved away (below).
  - Atlas, PDF 57/88 (`*+`, 320 cells), one term at a time:

    | terms on | `*+` within 1 | within 3 | median | the cells that move |
    |---|---|---|---|---|
    | none (base; chain on is within 0.05 of it everywhere) | 23.8% | 88.8% | -1.00 | |
    | + pre-shift | 25.0% | 98.8% | -1.00 | 40 toward, 0 away |
    | + normalization | 25.0% | 98.8% | -1.00 | NEG `int` 43.0 -> 63.0 (printed 56) |
    | + recomplement (shipped) | 25.0% | 98.8% | -1.00 | NEG `int` 63.0 -> 65.0 |
    | + acc-smaller (not shipped) | 26.2%* | 98.8% | -1.00 | NEG `int` 65.0 -> 68.0, away |

    \* Only the four NEG `int` cells differ in charge from the row
    above. The other four of the 84 cross the within-1 line by
    run-to-run noise: cells sit at -1.000 +- 0.001, and the line is
    exactly 1.

  - WHY THE PRE-SHIFT TERM MOVES THE NORMALIZED ROWS (worked, not
    fitted):
    - The atlas runs 10,000 `*+` into one accumulator (BODY_COPIES x
      LOOP_COUNT), so the accumulator counts 1, 2, 3, ... The product
      1 x 1 is .01 x 2^2, unnormalized (p.99), so the shift is
      e(acc) - 2.
    - ceil((s-3)/4) is 1 for acc in [32, 512), 2 for [512, 8192) and 3
      for [8192, 10001]. The mean is (480 + 2 x 7680 + 3 x 1809) /
      10000 = 2.13 clocks, which is the printed (N) - (U) difference
      exactly (7.24 us - 6.60 us = 24.13 - 22.00 clocks). The model
      moves 21.00 -> 23.13.
    - (U) does not move, and neither does IBM's: an unnormalized sum
      loses its carry (the LC indicator), so the exponent stays at 2.
    - Reading "each additional ... of 4" as a floor gives 1.57 and
      misses this, so the ceiling is kept.
  - WHAT REMAINS on `*+`:
    - Every ext/ibox row is -1.00. That is Table 2's "1 cycle if
      immediate next operation is floating point". The model charges
      this term on NO instruction: the D* and `/` calibrations carry a
      removal clock where it would be (NEXT.md "FP DIVIDE TIME"). It
      is recorded, not built: charged on `*+` alone, the same term
      would contradict D+/DL/D*, whose cells already sit at 0 without
      it.
    - The −28 tail is PDF 88's NEG `int` cells. Their internal operand
      `$R` is a CHOSEN set-up inside the accumulator's low half, so
      NEG `*+` cancels to a residue and each later add aligns it 62
      places and normalizes it back. With the three shipped terms the
      tail is +9 (65 against 56); it is not resolved.
    - FIXED 2026-11-26 (it was OPEN, found after the green run): the
      recomplement test on exact cancellation.
      - Table 2 Note 1 (printed p.3-6, PDF 24; `spec_timing.md`):
        "Recomplementing will only occur if the complemented (following
        pre-shift) fraction is larger in magnitude than unshifted
        fraction."
      - `fpBoxAddSumR`'s `recomp = sub && t[96] == 0` was also true when
        the two magnitudes are EQUAL, so an exact cancellation was
        charged 2 clocks that the note excludes. It is now
        `recomp = sub && t[96] == 0 && d.fb != fsh`. The sum is unchanged
        (~t, zero either way).
      - Bench: `mkPauStepTb` vector 10, acc -(.01 x 2^2) + 1 x 1, extra
        0, sum zero. With the old test, step 10 alone fails
        ("fpExtra = 2, want 0") and the other four PAU benches pass;
        reverted by the exact inverse edit.
      - Decks: the six `*+` decks of the table below (F216B/C/D,
        F219T-Y, Buchholz B.3, Problem 3.6) were run with and without
        the fix under STRETCH_HALT_REPORT=1. No halt moves (790, 400,
        836, 881, 986, 762 both ways), so no pin moves.
      - Suite on 3d410ee3: GREEN (only the two expected `UNREPRODUCED`
        p359 FAIL lines); 386 HALTREPORT lines identical to batch58's.
        `mkPauStepTb` is in the suite ("PAU STEPPING"), so vector 10 is
        under regression.
      - Atlas (PDF 42-101, 9,406 cells, its own build-atlas, run before and
        after on the same tree): 76.8% / 94.6% within 1 / 3 both ways
        (7,226 / 8,898 cells; the before run reproduces A4's step-3 figure
        exactly). Compared cell by cell, exactly 8 cells move, all PDF 57
        NEG `*+` ext columns ((N), A(N), (U), A(U), ni and ix), each by
        -0.0002 clock: the one exact cancellation in 10,000 adds, 2
        clocks / 10,000. Every other model time is identical.
  - **`*+` and the rule for done (item 2): HALF MET.**
    - Within 3 is met: 98.8%, against 88.8% before.
    - The median MISSES by 0.0014. It is -1.0014 before and after,
      printed -1.00 to two places, and the rule's test is |median| <= 1.
    - The missing clock is the uncharged "1 cycle if immediate next
      operation is floating point" (above). Charging it would put the
      median at 0, but it is not built, for the reason given there.
  - **Whole FP atlas, PDF 42-101, 9,406 cells:**
    - before: 76.8% within 1 (7,222), 94.3% within 3 (8,866);
    - after: 76.8% within 1 (7,226), 94.6% within 3 (8,898).
    - Only the 320 `*+` cells can move, because pauAddStep is off and a
      plain add's fpExtra is then 0.
  - **The plain add's terms (`pauAddStep`; also the forced zero,
    `pauAddForcedZero`, Table 2 printed p.3-3, PDF 21), measured and
    held OFF.** Over the `*+` step, the whole atlas goes from 76.8% to
    77.3% within 1 and from 94.6% to 95.1% within 3.
    - Toward:
      - D+: 81.2% -> 88.8% within 1, 98.8% -> 100% within 3.
      - D+'s −37 tail (PDF 74/78 NEG `int`, 13.0 -> 49.99 against the
        printed 50.03) is reproduced exactly, by 15 + 20 + 2 under the
        ceiling reading.
      - `+`: 89.1% -> 91.6% within 1.
    - Away (274 cells in all):
      - M+ / M+MG already run long (median +0.78, for a reason in the
        store path rather than this unit), and their median goes to
        +0.82 / +2.69.
      - +MG's NEG rows go from -1.0 to +3.0. The forced-zero and
        recomplement terms are the candidates; this was not traced.
    - It waits for the M+ store path. D+ already meets the rule
      (median -0.02, 98.8% within 3).
  - **Suite: GREEN** (2026-11-26). The only FAIL lines are the two
    expected `UNREPRODUCED` p359 ones, and no pin moved. Six
    STRETCH_HALT_REPORT halts moved, of 386; every other halt is
    identical, in order, to the base.
    - Each moved deck was re-run in a scratch copy:
      - (A) with every step-3 switch off (pauChainMulAdd and pauMa*),
        which gives every base value back;
      - (B) with the chain on and the terms off.
    - Each deck header records its own:

    | deck | base | (A) | (B) | shipped | cause |
    |---|---|---|---|---|---|
    | F216B | 774 | 774 | 790 | 790 | the chain |
    | F216C | 399 | 399 | 399 | 400 | the terms |
    | F216D | 834 | 834 | 836 | 836 | the chain |
    | F219T-Y | 867 | 867 | 867 | 881 | the terms |
    | Buchholz B.3 | 980 | 980 | 986 | 986 | the chain |
    | Problem 3.6 | 480 | 480 | 480 | 762 | the terms |

    - The chain's add pass makes the unit answer `*+` in 5 clocks, not
      4. Box clocks come off the budget, so the cost shows only in the
      hold behind a `*+`. That is the open hold-cost mechanism (NEXT.md
      "ONE PARALLEL-UNIT MULTIPLIER"), not a sourced time.
    - Problem 3.6's +282: its accumulator holds 2^80, and each of its
      sixteen `*+` aligns a small product about 75 places, 18 Table 2
      cycles each.
  - Unit bench `mkPauStepTb`, 10 vectors (11 since the exact-cancellation
    fix) (`tests/run_paustep_test.sh`):
    - literal clocks: 5 chained, 4 when the preparation answers, 1 for
      a plain add;
    - literal terms.
    - Each switch was injected in a scratch copy, and each failed
      exactly the vectors recorded in its header. mkPauFpTb,
      mkPauDivTb, mkFpDivSketchTb and mkPauMixTb passed every time.
- **COMPARE and the SQUARE ROOT: left undone, with the reasons.**
  - COMPARE (K, KMG, KR, KMGR) already meets the rule: 96-98% within
    1, 100% within 3, median 0.00. The atlas's operands have exponents
    +1 and -1 (`atlas_oracle.py` FP_BLOCKS), so their difference is at
    most 2, under Table 2's "pre shift <= 3", and nothing an unchanged
    compare does adds a term.
    Moving `fpCompare` into the unit is structure with no measurable
    time, and is left for the E-box arm work.
  - SRT meets the rule (60.0% within 1, 100% within 3). Fig. 3.8.10
    gives no countable time. Table 2's 2 + 106 is already charged, and
    its "+1 if begun on a B pulse" is a phase the model does not track.

**A5. `ebusy` becomes response readiness; the look-ahead's `Whole`
entries split** (`ebox_roadmap.md` steps 5 and 7).
- The look-ahead holds a level per PART of an instruction, as G1.1
  says ("a level is a PART of an instruction").
- `headReady` waits on the units' `responseReady`, not a counter.
- Exit: `ebusy` has 0 hits. The §1c-audit "expensive datapath" row
  matches.

*A5 record, 2026-11-26.*

- **Step 1, `ebusy` INTO THE UNITS (done, behaviour-preserving).**
  - The census first. `ebusy` was charged in two places only:
    - `rl_au_remove`: a branch level's Blosk fig.10 `2 * 6`, or the whole
      `eboxClocks` row for a level that completes at removal (no unit
      runs for it);
    - `rl_exec_resume`, a look-ahead level completing after a read or a
      unit: the row less the unit's clocks (`budget - boxK`), or for a
      stepped SAU add the row's fixed part (`sauRowWithUnit - u`).
    So the BOXED instructions already wait on `responseReady` for the
    part a unit steps (the level is held in `mkEBox` and `headReady`
    has `!ebox.busy()`); what `ebusy` counted after the answer is the
    part no unit steps yet, and for the unboxed paths the whole row.
  - Now: `mkSAU` and `mkPAU` each have a TERMINATION (`terminate(n)`,
    `holdTerm()`, `terminated()`, StretchSAU.bsv / StretchPAU.bsv, the
    interface note). `mkEBox.terminate(fp, n)` hands the clocks owed to
    `mkPAU` for a floating-point instruction and to `mkSAU` for every
    other one (CHOSEN: while the head waits on both units, which unit
    holds the time moves no clock). `headReady` waits on
    `ebox.unitsTerminated()`. `ebusy`, its `eb` decrement and its eleven
    writes are gone: 0 hits in `bsv/` (the history comments name it
    "the E-box countdown").
  - THE ONE NON-OBVIOUS RULE KEPT: `ebusy` counted down only in a clock
    in which an instruction-unit arm fired. With a crossing store's tail
    parked (`st.storeTailPending()` alone in `busyXfer`) no arm fires, so
    it stood still. The units' count is held the same way: each arm
    sends `eArm`, and in the clock after one with no arm `rl_term_hold`
    holds both units (the count is stored as n + 1 so that the read after
    the units' own decrement sees what `ebusy` held).
  - Verified:
    - SHADOW RUN: the new readiness beside `ebusy`, with a rule printing
      `FAIL A5 TRIPWIRE` on any clock where `ebusy == 0` and
      `unitsTerminated()` differ. The suite, run in a scratch copy of
      bsv/*.bsv, decks, strap and tests: 0 tripwire lines over 381
      HALTREPORT programs. (The copy lacked bsv/'s non-.bsv files and
      docs/, so the MCP, host-tape, smoke and OCR sections failed to
      build there; they are covered by the real run below.)
    - The tripwire is discriminating: on the SHADOW build, with
      `rl_term_hold` disabled (`False &&` in its guard), the crossing-store
      decks printed it (vfl_crossing_store, cm_crossing_field,
      vfl_cross_tomemory; the clock lists were cut by the probe's own
      `head -8` and are not recorded). That build is gone.
    - INJECTIONS ON THE SHIPPED TREE (1c140c22, in the worktree, each
      reverted by the inverse edit, `git status` clean after), six decks
      with their full run_tests.sh arguments:

      | deck | base | hold off (`rl_term_hold (False && ...)`) | count n, not n + 1 |
      |---|---|---|---|
      | vfl_crossing_store | 401 | 396 | 388 |
      | cm_crossing_field | 329 | 324 | 323 |
      | vfl_cross_tomemory | 1193 | 1193 | 1190 |
      | vfl_cross_storewait (`CYCLES=283+-0`) | 283 | 283 | 279, **FAIL** |
      | Buchholz B.3 | 986 | 986 | 986 |
      | Problem 3.6 | 762 | 762 | 729 |

      - Hold off: NO suite check fails on these decks; only the
        HALTREPORT comparison with the base sees it (-5 on two decks).
        So the hold is guarded by the HALTREPORT diff, not by a pin.
      - Off by one: the storewait CYCLES pin fails ("cycles = 279, want
        283 +- 0") and every deck that retires a level moves.
    - The six `*+` decks: halts identical (790, 400, 836, 881, 986, 762).
    - Full suite on the committed tree (1c140c22): GREEN, only the two
      expected `UNREPRODUCED` p359 FAIL lines; all 386 HALTREPORT lines
      identical, in order, to batch58's GREEN run (the base of this
      branch, the same stretch/ tree as the Step 0 run, also identical).
- **Exit, measured honestly: `ebusy` has 0 hits; the "expensive datapath"
  row does NOT yet fully match.** Piccolo's boxes own their whole
  multi-cycle time. Here the units own it as two parts: the stepped part
  (passes, reduction loops) and a termination count that is still the
  timing table's remainder. The roadmap's own wording ("Countdowns
  remain only where the machinery is not yet modelled", step 5) is what
  this is; the count now lives in the unit that will step it. The
  §1c-audit row is updated to say so.
- **WHAT IS LEFT OF A5, in order:**
  1. Unboxed paths into the units. Every instruction that completes at
     removal (`eboxClocks` row, no unit) and the branch level's 12 are
     pure termination counts. Each family moves when its unit steps it:
     the connectives and VFL logic into mkSAU's passes, as A3 did the
     adds; the plain FP add's terms are measured in A4 and held off
     (`pauAddStep`).
  2. The termination's rule-of-arms hold. Removing it is a TIMING change
     (a crossing store's E-box time one clock shorter when nothing else
     is pending: -5 on vfl_crossing_store and cm_crossing_field, above); measure it on the WB XOVR atlas columns (PDF 143-169)
     with A6, not here.
  3. Roadmap step 7, the `Whole` split. NOT STARTED in this session, and
     it is not a behaviour-preserving step: Table A-2's levels are parts
     (`spec_lookahead.md` §5: a VFL ST takes 3 levels, M+ crossing with
     progressive indexing 6 in a ring of 4), so level occupancy and
     look-ahead pins move. What §5 says: the E-box must consume a
     sequence of parts, not one `di` (`execute()`'s signature is the
     obstacle it names), and of its two allocation shapes it leaves the
     choice "not settled", warning that shape 2 deadlocks on six levels.
     PROPOSAL (this session's, not a source's): (a) the part sequence
     first; (b) one-at-a-time allocation with a residual count (shape
     1); (c) start with the one-level FP operations (Table A-2: one
     level, op + opnd -- not `*+`, M+, LFT or D/, which take two), then
     the two-level FP ones, then VFL (2-3, doubled on a crossing). Whether
     the one-level FP step is time-neutral is unmeasured; each step
     records the pins it moves.
  4. Unit benches for the termination. DONE 2026-11-27: mkSauStepTb and
     mkPauStepTb each end with a 24-clock script (terminate(n) with n = 3,
     0, 2, 5 then 1, 4; a hold after a terminate and one while idle; a
     request beside the count) checking terminated() in every clock
     against a literal table. Four injections in each unit (n stored for
     n + 1; the hold ignored; terminate adding instead of replacing;
     responseReady waiting on the count) each fail only script lines
     (observed sets in the bench headers); the step vectors pass under all
     four, so the script is the only bench guard.
  5. Stale text, left as it was after the green run (decks and tests are
     not edited after it): `tests/run_tests.sh` (the df_data_fetch_alarm
     / interrupt notes, about line 12582-12615), `decks/int_timing_bracket.strap`
     (header, lines 54-119) and `decks/df_data_fetch_alarm.strap` (line
     176) describe `ebusy` and rl_interrupt's `ebusy <= eb;` as live;
     `bsv/README.md` (lines 1399, 1882-1888) and `docs/NEXT.md` (229,
     4896-4928, 6066) likewise. In the model that decrement is now the
     arm's `eArm.send`, with the same effect.

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
- Transmit. DIAGNOSED 2026-11-23 (`atlas_oracle.md` "furthest off"
  2, which gives the change with a citation for each term). Per word,
  charge by destination: 10 clocks to core or internal, 14 to index
  storage (Table 9; PDF 107). The model now charges the source read
  instead (2 from index storage, 10 or 17 from core). Fixed cost:
  F = 38 / 32 clocks for T, F − 2 for TI, where the model has 15. The
  generator's I-BOX TO I-BOX block is fixed (18.0 → 19.0), and
  `--selftest` check 0b now covers the transmit generator.
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

**A11a. The memory cycle, before the exchange.** `memCycleClocks = 7`
(2.1 µs, Buchholz) against the CE procedure's Busy trigger of 1800 ns =
6 clocks (§4 Procedure 1, PDF 274) and Perf. Char.'s 2.2 µs recycle and
1 µs readout (p.3-15); `memReadClocks = 5` against the CE's 5th sample
pulse for an LA level and 5th-6th for 1Y/2Y (`ibox_la_spec.md` §12 item
7). `NEXT.md` §5f measured the cycle at 2.4 µs once. Settle which
figure the shipped machine had, with the atlas as the arbiter only
between readings the sources allow; every pin will move.

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

**A13. The rest of the interrupt and execute rules** (rows §1a had no
milestone for, found by the 2026-11-24 refresh; Ref. Manual pp.43-51):
- MK, IK, IJ and EK are defined and never set, and CBJ is never set.
- An E-box-class instruction at the interruption address (p.49, "may be
  of any type"; `rl_prepare` says it is unbuilt).
- p.50's two disabled-state exceptions.
- A Class S alert during an EX/EXIC subject instruction.
- EX/EXIC's 1 ms USA end (LVE has one).
- AD for an instruction counter stepped past the end of storage.
- EXIC's p.51 item (d); IF beside EXE under EXECUTE.
- The stale "IF is not implemented at all" comment in `StretchCore.bsv`
  (IF is built).
Exit: a deck per item, with its injection; §1a's interrupt and EXIC rows
done.

## The board: the model must also FIT (added 2026-11-24)

The project's target is the ULX3S-85F (`fpga_feasibility.md`), and this
plan said nothing about it. The last whole-core place-and-route
(2026-10-16, §9.3.6a) measured:
- `TRELLIS_COMB` at 375,223 against 83,640 (448%);
- `DP16KD` at 384 against 208 (184%);
- `TRELLIS_IO` at 1,066%, from the unwrapped ports.

A model that matches every page and does not fit has not met the goal.

- **F0. Re-measure on master.** Every multi-cycle box since 2026-10-16
  should have moved COMB. Run it when no suite is running: it took about
  3 hours at full load. Record per-module LUT4 in `fpga_feasibility.md`.
  **RUN 2026-11-25** (`fpga_feasibility.md` §11, `fpga/synth_core.sh`,
  reconstructed). Per-module yosys figures: 686,817 LUT4 (`-noabc9`,
  an upper bound) and 102,219 FF in all. 82% of the core's flip-flops
  are two fixtures held in registers: `mkDiskSourceSmall` (65,536) and
  the console capture `consoleImg` (16,384). Move them out (D3, a BRAM
  or UART console), then re-run F0 fixture-free to read the core's own
  logic. nextpnr was not run.
  **FIXTURES MOVED TO BLOCK RAM, 2026-11-25** (`fpga_feasibility.md`
  §11.1). Both are now `BRAMCore`s with a written mask. The disk read
  keeps its one-clock latency, so no cycle count moved. The console's
  testbench read became a request and a response. The re-run gives
  369,181 LUT4, 21,517 FF and 392 DP16KD for the whole design; the
  core's own logic is 344,369 LUT4 and 19,310 FF. The fixtures were 48%
  of the core's LUT4. Still in registers: the reader, printer and tape
  images (5,120 bits).
- **F1. A design rule for A3/A4.**
  - The units are built at the machine's own widths: the SAU a byte pair
    per 0.6 µs step (Buchholz p.209), the PAU's one shared multiplier
    tree (Fig. 14.7).
  - A unit that wraps a combinational 64-bit function in a request and
    response does not count.
  - Each A-milestone reports its LUT4 delta (per-module `yosys stat`,
    minutes, not the 3-hour run) beside its atlas delta.
- **F2. Core storage to SDRAM.** This is the 184% DP16KD, done the
  same way as the disk plan's D3 (`~/.claude/plans/zazzy-noodling-sloth.md`).
- **F3. The I/O boundary.** The 1,066% IO is unwrapped ports. Write a
  ULX3S top (D4's). The console paper's testbench port
  (`io.readConsoleReq`/`readConsoleResp`, since 2026-11-25) is the port
  a UART drain would read on the board.
- Exit: nextpnr places and routes the six-unit core on an 85F. If it
  cannot, partitioning is recorded as an owner decision with the
  measured numbers.

**MCP: from stubs to MCP's own paths (added 2026-11-24).** IPL
completes, and MCP runs a job card through UNCODE, its loader and job end
(`boot_plan.md`; `NEXT.md` "THE BSS PROCESSOR, RECONSTRUCTED"). The run
leans on stubs: the dispatcher, `$RET`, and `$SCR`/`$FETCH` over core
images instead of the disk.
- **M-a. DONE 2026-11-24.** `check_bss_mcp_go.py` passes with the stub
  deleted. Every `$FETCH` is now DISK FETCH (pp.311-318), run against the
  disk saved by the same post-IPL run. BSS, PCBSS and the LB areas are on
  the tape (PROSA_EXTRA, RECONSTRUCTION). TWS's words are planted
  (SCAFFOLD). The remaining stubs are listed in the test header. As
  first written:
  Replace `$FETCH`'s core-image stub with MCP's own fetch from
  the 353. The simulated disk now holds what IPL writes (D2, merged
  `19b7234`: P1 writes arcs 0-32, 33 arcs, measured), so the stub's
  reason is gone. Exit: `check_bss_mcp_go.py` passes with the stub
  deleted.
- **M-b.** Then `$SCR`, `$RET` and the dispatcher, each the same way.
- **M-c.** A warm start needs C22-6678-1 p.32's "Disk IPL" card deck,
  which the repo does not hold. Search for it (G5), and reconstruct it
  only if it is lost, labelled RECONSTRUCTION.
- STRAP II and FORTRAN IV compiling under MCP, and the DCP (boot plan
  M4), follow. Their code status is in `archival_inventory.md`.

**IBM's own diagnostics as oracles, not yet run** (`archival_inventory.md`):
- The three memory tests, `ja_bp6a` (6 pp), `ja_bm6a` and `ja_bb6b`,
  gate A11a, the memory cycle. `ja_bp6a` is RUN (2026-11-24,
  `decks/ja_bp6a_memory_patterns.strap`, bit-exact against
  `verify_ja_bp6a_listing.py`; details in `archival_inventory.md`). It
  gives A11a no timing: the document states no unit-busy or cycle time.
  Its PDF p.1 puts the two A boxes at 40 (octal) and the four B boxes at
  100000, the reverse of `StretchMemory.bsv`'s map. That is open for
  A11a, and the model is not changed yet. `ja_bm6a` is RUN (2026-11-25,
  `decks/ja_bm6a_unique_adr.strap`, bit-exact against
  `verify_ja_bm6a_listing.py`, 264 checks). It gives A11a no timing
  either. Its limits put the lower memories at 100-77777 and the upper
  at 100000-277777 (PDF pp.4-8), agreeing with `ja_bp6a`, and its error
  message takes the box number from the address's low two bits (PDF
  pp.5, 9). It types on channel 39 (`TYPE SYN,19.32`, PDF p.11), where
  the model has no unit, so its run reads the message it builds in core.
  Upper memories and one whole pass are clean on the model; the
  100-pass O.K. is not reached. `ja_bb6b` is RUN (2026-11-26,
  `decks/ja_bb6b_worst_pattern.strap`, bit-exact against
  `verify_ja_bb6b_listing.py`, 574 checks, no row torn). It gives A11a
  no timing either. It writes runs of all-ones and all-zeros words, 8
  long in the upper memories and 4 in the lower, re-phased at 200000
  and 40000 (PDF pp.5, 12-13, 20), checks them, inverts them and checks
  again; a bad word makes it hang on `BRGZ,$`, and X14 counts passes
  (writeup PDF pp.1-2). That the runs are two words per interleaved box
  is an inference; the document states no interleaving. Its second
  half drives the machine's ERROR INJECTION (bit 58 of location 3,
  R23-9695 section 9, printed pp.114-115) for single ECC errors, and
  the model has no ECC or injection, so that half runs as plain stores.
  The checkerboards and one whole pass are clean on the model, and X14
  steps. An injected stuck-at-0 data bit (150000-150777) is caught:
  the program hangs on its `BRGZ,$` naming 150000. Observed, cause
  not investigated: the model's `halted()` does not rise on that hang. All three tests are now run; none states a memory timing, and
  all three put the A boxes low, the reverse of `StretchMemory.bsv`'s
  map.
- I-Box 2 and 3 (`jb_ax2a`, `jb_ax3a`, surveyed only) gate A8.
- BX-0 (`ka_ex1`) gates A11.

Transcribe and check each against its printed machine-code column with
`listing_oracle.py` (track B) before its milestone starts.

**Tooling:** `atlas_oracle.py` builds into the shared `bsv/build`, and a
suite run after it in the same tree failed the smoke test's schedule
check (2026-11-23, transmit diagnosis). Give it its own `-bdir`.

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
   the one-LAAR reading of Perf. Char. as a switch. Read 2026-11-23 (`ibox_la_spec.md`): Fig 3.2.2
   sheet 2 (PDF 94, printed 2-4) assigns LAAR 1 if free, else LAAR 2
   (spot-checked on the image), and the level's FROM bit picks which LAAR
   the TBC sends (Fig 3.2.12). Perf. Char. p.3-21 (PDF 39) says one.
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
A10 → A11 → A12, with A13 taken when a core slot is free between
them (its items are small and independent).

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
