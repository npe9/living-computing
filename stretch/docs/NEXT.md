# What to do next, and why

A standing work queue for the Stretch model, ordered by dependency.
Written so the next session starts from a decision rather than a
survey.

**This file is the plan, not the record.** The record of *how* each
piece was built lives in `docs/microarchitecture_plan.md`, in the
section comments of `strap/run_tests.sh`, and in commit messages.
When an item here is finished it shrinks to a pointer; it does not
accumulate.

## The bar

Two standards, and every test says which it meets:

* **Transcription** — a listing row checked bit-exactly by a verify
  script. The strongest oracle here.
* **Manual-derived** — hand-written from a primary source, stated as
  the weaker standard in the program's own header.

And one rule that outranks both: **a green test is only evidence about
faults its inputs could have made visible.** Every new test gets an
injection that must fail, at a named address, in *its own* check.

A corollary learned the hard way, three times in one day: **when a
summary of a test claims a rule, check the test actually contains an
input that could break it.** `interrupt_pg0.strap` has four blocks and
three of them exist because an earlier version could not see a rule —
one found by a surviving mutant, one by writing a sentence into this
file that the suite did not support, one by enumerating what the
inputs made visible.

## Done, and where the record lives

| piece | record |
|---|---|
| Storage protection, permanently protected words 1–3 | `run_tests.sh` §"Storage protection, gated on…"; plan A.3; the rule **transcribed** by `verify_ax5b_16086_listing.py` (encoding only — the behavioural test is still hand-written) |
| Address boundary registers + control bit | same file §"…the address boundary registers"; **transcribed** by `verify_ibox1_ensu_listing.py` |
| The interruption mechanism | `run_tests.sh` §"The interruption mechanism"; plan A.3 |

All three are implemented, injected, and in the mutation table. The
boundary registers have both standards. Storage protection's **rule**
now has a deck behind it (`ax5b` 16086 says word 1, DS and "when
enabled" in its own error message) but its **behaviour** test is still
hand-written, and the interruption mechanism is still
**manual-derived only** — which is what the rest of item 1 is for.

## 1. `jb_ax5b` routine 1260 — make the interrupt work deck-verified

The single highest-value item. The write-up's routine index (PDF p.2,
read first-hand, transcribed in `archival_inventory.md`) says 1260
checks *"the mask register, the Interrupt Address register, the
ability to interrupt, the Indicator register, unique interruption for
bits 0-47, I-Box indicators, Upper and Lower Bounds registers and
address monitoring."* That is everything built 2026-09-19 to -21, in
one deck routine.

**The prerequisite this file recorded never existed.** It said
"SSIP's `160S1`/`160SX1` save/restore harness, reported at `ax5b`
pp.41–44". Those pages are 1260's per-indicator blocks, 16071 (`TS`)
through 16086 (`DS`). All four transcribable ones were done without
any harness — and then the driver itself (p.45) was done too. Third
entry in this file's own "distrust a blocker recorded here" trap.
`160S1` = 022741.00 and `160SX1` = 023041.00, read off the driver's
own printed address fields; nothing has needed either. The
page-by-page record is in `archival_inventory.md` §"I-Box 5".

**16086, the DS block, is done** — `programs/ax5b_16086_ds.strap`,
bit-exact via `verify_ax5b_16086_listing.py`, record in
`run_tests.sh` §"I-Box 5 routine 1260's DS block". It is an ENCODING
oracle; storage protection's behavioural test stays hand-written.

**So are 16082 (`OP`), 16083 (`AD`) and 16071 (`TS`)** —
`ax5b_16082_op_ad.strap` and `ax5b_16071_ts.strap`, records in
`run_tests.sh`. **That is every transcribable block on pp.41–44.**
What remains there is out of reach for a stated reason: 16072–16081
are three-line `B`/`CNOP`/`DR` stubs for indicators a program cannot
provoke, 16084 needs `LVE` and 16085 needs `EX`, both deferred in
item 5.

**16071 changes item 5's timer entry.** It is a second, eight-row deck
oracle for the interval timer — Reference Manual p.44, *"Time Signal
(TS). The interval timer has become zero."* — and it is in place
*before* the timer is implemented, which is the order item 2 asks for.
Routine 1258 is no longer the only oracle, and is no longer the
cheapest.

**The indicator walk at 16087/16088 (p.45) is done** —
`programs/ax5b_16087_walk.strap`, and it brought **TRANSMIT/SWAP into
the assembler** (all eight mnemonics, from pocket card X22-6533; only
`TI` has a listing witness). Record in `run_tests.sh` §"…indicator
walk + TRANSMIT IMMEDIATE".

**That immediately exposed a silent bug, now fixed.** Making Transmit
encodable made two long-standing `bsv/README.md` claims testable for
the first time — and two-thirds of one was false. The decoder
discarded bit 57, so a forward `SWAP` executed as a one-word Transmit;
and the count was never read, so a multi-word Transmit moved one word.
Both silent. The decoder now captures bit 57 and the arm honours only
an immediate count of one (Ref. Manual pp.30-31: immediate 0 means
*sixteen*; a direct count lives in a register this arm never reads, so
all of them are refused). Guard:
`programs/transmit_scope.strap`, six blocks, five injections, one per
rule. Record in `run_tests.sh` §"TRANSMIT: what is honoured…".

**The boundary driver is found, and the guess it replaces was wrong
in range AND in kind.** This file said pp.66–79 held "the positive
boundary-interrupt cases" — an inference from a scouting pass, not a
page. Scanning pp.46–86 for BOUND/MONITOR on 2026-09-23 and reading
the hits gives the real layout:

| page | sub-test |
|---|---|
| p.65 | *"TEST 7 CHKS BOUNDARY CONTROL."* / *"CHK UPPER BOUNDARY DATA."* — driver at 16099/160100 |
| p.67 | tail of the upper-boundary error table (BIT10–BIT17) |
| p.68 | *"CHK LOWER BOUNDARY DATA."* (driver 160102/160103) and *"CHK BOUNDARY CONTROL BIT."* |
| pp.69–70 | the lower-boundary error table, bits 32–49 |
| **p.71** | *"FETCH FROM X-1 TO CHK UB COMP."*, *"FROM X-3 TO CHK LB COMP."* |

pp.65–70 test whether the **registers hold their bits**; **p.71** tests
whether the **comparison fires**, and p.71 is what "positive
boundary-interrupt cases" actually means.

**p.65 is transcribed and runs** — `programs/ax5b_16099_ub_data.strap`,
sixteen rows bit-exact, and it **catches a boundary fault and names
the bit**: dropping IBM bit 17 from `boundaryReg` halts it at
022263.00, the error table's eighteenth entry. Record in
`run_tests.sh` §"…TEST 7".

**p.68 is transcribed and runs too** —
`programs/ax5b_160102_lb_ctl.strap`: the lower-boundary loop and the
control-bit test, 37 rows bit-exact, and it localises a fault to the
bit (drop IBM 49 → the table's "BIT 49" entry; drop IBM 57 → `SERS`
with *"UNABLE TO SET BNDRY CNTRL TO 1."*).

**Still to do on the boundaries: p.71, the comparisons** — *"FETCH
FROM X-1 TO CHK UB COMP."* and *"FROM X-3 TO CHK LB COMP."* — which is
the one this item always wanted, and the only part that tests the
monitoring actually **firing** rather than the registers holding
their bits.

**Do not re-scout these — bounded negatives, 2026-09-21:**
`jb_af1c` never provokes an interruption (no `BE`, `BEW`, mask write,
interruption-address write or table in 282 pages; it provokes real
faults and *polls*). `ja_ax1a` deliberately prevents one — its own
writeup says it "provides an Interrupt hang-up if for some reason the
system should become enabled", and its `INT1` table is all `NOP,0`.

## 2. DF and IF — and routine 1268 is NOT their oracle

The two address-monitoring indicators the model does not implement.
p.32: DF suppresses the data fetch and terminates *if its mask bit is
one*; IF interrupts before the instruction that caused it. Both are
mask-dependent, unlike DS.

**This item used to say `jb_ax5b` routine 1268 was "the only known
deck test of them" and to read it first. That was a misreading, and
it is corrected.** Read first-hand 2026-09-22, the routine's own
header is *"1268 — IF AND DF CLOSE TO DS"* and its error messages are
*"EXECUTED OLD INSTRUCTION FROM EXT."* and *"LOADED OLD DATA FROM EXT
MEM."* — the wrong **value** arrived, not an indicator failed to set
(compare 1260's *"UNABLE TO TURN AD ON."*). `DF`/`IF` there are the
Data Fetch and Instruction Fetch **paths**; "close to DS" is close to
a Data Store. It is a look-ahead forwarding test, and
`archival_inventory.md` already said so in one of the two places it
described the routine.

**So DF and IF have no deck oracle anywhere read so far.** Designing
them means Reference Manual p.32 alone — the weaker standard, stated
as such in whatever program tests them, exactly as storage protection
was until `ax5b_16086_ds.strap`.

**What 1268 turned out to be good for.** Both halves are transcribed
and **run**: `ax5b_1683_df_close_to_ds.strap` (test 2, the load side)
and `ax5b_1681_if_close_to_ds.strap` (test 1A, the
instruction-fetch side). Records in `run_tests.sh`. In both, the
encoding is the discriminating standard and the run is a regression
guard — measured, neither witnesses forwarding, because the deck's
spacing is too gentle for this model's pipeline. Test 1A does witness
something the project had no direct test for: the `LX`/`SX` **index-word
round trip**, since it plants an arbitrary instruction through
`packIndexWord` and executes it.

**Left on 1268**: cases 1B and 1C, blocked on `EX` (item 5).

## 3. Smaller open pieces inside what is built

* **Interruption timing.** p.48 permits an interruption at an
  *instruction* boundary; this model takes it at a *quiescent* one
  (look-ahead empty, E-box idle). Later, never earlier. Stated in
  `StretchCore.bsv`, `run_tests.sh` and `bsv/README.md`.
* **An E-box-class interruption instruction** fails loud rather than
  stepping the counter.
* **`BEW`** — "branch enabled and wait" — is modelled as a plain
  enabling branch. `ja_ax1a` p.58 is *reported* to drive it from the
  interval timer and fall through, which would be both the real
  behaviour and a transcribable block. Not verified first-hand.

## 4. Standing practice, after every batch

`python3 strap/mutation_score.py --jobs 12` — each mutant gets its own
APFS-cloned tree, so the real model is never mutated; 53 minutes
rather than 233. It refuses to run on a dirty tree or a non-green
baseline. What remains after parallelising is the serial baseline plus
the slowest single **survivor**, because a survivor is exactly the
mutant nothing stops early.

Read the **SURVIVOR** list, and the count. Triage into *missing test*
/ *equivalent mutant* / *expected* before writing anything.

**Do NOT read the section column as "the catcher".** It is the FIRST
section to fail, because each mutant runs with `FAIL_FAST=1` — so for
a broad fault it names whatever broad test runs earliest, which says
nothing about coverage. This file used to say "a catch far from its
own subsystem is a near miss", and that rule gave the wrong answer
every time it was applied (see below). To find out whether a rule
actually has a witness, re-run that one mutant with `FAIL_FAST` unset
and read the whole list of failing sections.

**Run 2026-09-22: 32/33, survivor `ad-bound-off-by-one`** — the one
documented expected survivor. `prot-carve-out-as-or` is back in its
own section, so the regression the previous run flagged is resolved.

**ALL FOUR "NEAR MISSES" IN THAT RUN WERE WRONG**, for two different
reasons, and both were the measurement rather than the model.

*Two were a `/tmp` race.* Five test scripts — `run_fp_addr_test.sh`,
`run_fp_exp_test.sh`, `run_fp_test.sh`, `run_fp_signmod_test.sh`,
`run_scf_test.sh` — wrote a *fixed* path under `/tmp` and re-read it.
The campaign runs 12 mutants in parallel, each in its own **cloned
tree** — but `/tmp` is not cloned, so all twelve raced on one file and
`FAIL_FAST` named whichever script lost. Run serially, both
`seop-ignored-on-backspace*` mutants are caught by `io_tape` at
exactly the checks their entries name. Each script now uses
`${TMPDIR:-/tmp}/<name>.$$.strap`.

*Two were the `FAIL_FAST` label*, and this is the more embarrassing
one because the rule that produced them was written in this file.
`imm-count-low-bits` and `vfl-length-zero-is-zero` were both recorded
as "caught only by the catch-all smoke test". Re-run with `FAIL_FAST`
unset:

| mutant | sections that fail |
|---|---|
| `imm-count-low-bits` | **10**, including `IBOX-1 KCI`, `IBOX-3 LRI`, `IBOX-1 C+I`, `C-I` — named for the very instructions the rule governs |
| `vfl-length-zero-is-zero` | **38**, most of them FP and VFL sections on its own subsystem |

Both rules are heavily witnessed. **There are no near misses in this
campaign.** `mutation_score.py` now prints the column as
`first-fail:` so it cannot be read as the catcher.

**AND THE COUNT HID AN UNTESTED RULE.** Both ZM mutants reported
"caught by their own section" — truthfully — while mutating the *same*
line. p.99's ZM rule is implemented twice in `StretchFP.bsv`,
character for character, in `fpMul` and `fpMulDouble`; both mutants
used that line as their pattern and `apply()` did
`replace(old, new, 1)`. Injecting the same fault directly into
`fpMulDouble` and running the whole suite gave **3059 PASS, 0 FAIL**.
Now: `mutation_score.py` refuses a pattern that does not match exactly
once, the two mutants carry their preceding line to disambiguate them,
`zm-double-*` target the second copy, and
`programs/fp_zm_terms_double.strap` is the witness. 36 mutants.

**So: a mutation score is evidence about the sites the table names,
and nothing else.** Before trusting one, check the table can still
reach every site it claims — that check is now automatic.

`python3 strap/line_addresses.py programs/X.strap` prints every
instruction line's address in the listings' octal convention. Every
injection address a new test records should come from it, and it
reproduces the ones already recorded — which is what makes them
checkable rather than folklore.

## 4a. `EX`/`EXIC` — the oracle is read; implement from it

**The highest-leverage unimplemented instruction**, because four
already-located transcription targets wait on it: `jb_ax5b` routine
1268 cases 1B/1C (`EX,$X3`, `EX,$R`) and routine 1260 blocks 16084
(`LVE`) / 16085 (`EX`).

**Routine 1262 is its deck oracle and has been read first-hand**
(2026-09-23, PDF pp.87–110; purpose block and the p.101 EXIC blocks
transcribed in `archival_inventory.md`). Its own header: *"TEST EX
AND EXIC"*, in three parts — test 1 the execution of **all classes**
of instruction plus the indicators illegal executes set; test 2 the
`EXIC` instruction; test 3 the **illegal combinations** of the two.

**What p.101 pins down, three rules per instruction class**, each with
its own error message: `EXIC` to that class must not interrupt; the
subject instruction must actually execute; and the **pseudo-IC must be
stepped by the subject's length** (`.32` for a half-word), which the
deck checks with `V+I` then `KV`.

Pair it with Reference Manual p.45 on indicator 18 (EXE): an
instruction executed under `EX`/`EXIC` that *"attempted to change the
contents of the instruction counter"* is **suppressed**.

Design from those, then transcribe 1262 as the acceptance test — the
order item 2 asks for and did not get.

**AND IT FITS THE MACHINERY THAT IS ALREADY THERE** — read out of
`StretchExecute.bsv`'s `mkEBox` and `StretchCore.bsv`'s
`rl_exec_resume` on 2026-09-23, so this part is *verified structure*,
not a sketch. `execute()` is a pure function and Bluespec will not let
it recurse, which is the obvious reason to think `EX` is hard. It
isn't, because the E-box already has a **bail-out and resume** path
for instructions that need an operand word:

* `start()` runs `execute()`; if it returns `needsRead`, the E-box
  issues the read, stores the instruction in `held`, and returns
  Invalid;
* `resume()` collects the word into `prefetch` and **re-runs
  `execute()` with the same held instruction**.

*Proposed* (not yet built): `EX`'s arm returns `needsRead` = the
subject's address, exactly like any operand fetch. Then `resume()`,
seeing the held instruction is `EX`/`EXIC`, **decodes the fetched word
and installs the SUBJECT as the held instruction** — `execute(... ,
decode(v), emptyPrefetch, 0)` instead of re-running the `EX`. The
subject's own `needsRead` then works normally, because it is now the
held instruction. No recursion, no second `execute()` instantiation,
and the cycle it costs is one the bail-out already pays.

Two consequences that fall out of that shape and match the sources:
* the instruction counter advances past the **`EX`**, because
  `commitNext` uses the held `pc`/`len` — which is what Ref. Manual
  p.45 requires, a subject that tries to change the IC being
  *suppressed* with EXE set;
* `EXIC` additionally steps its **pseudo-IC** by the subject's length,
  which is routine 1262's third check per class (`.32` for a
  half-word).

## 5. Deferred, each its own piece of work

Decimal VFL (`c=1`) and radix conversion; `RNX`/`LVE`/`LVS`;
Transmit backward/`SWAP`/
multi-word; I/O chaining and multiple-block; `LOC` and the
unimplemented `CTL` function codes; channel status reaching the CPU
indicators; the interval timer actually ticking (deck oracles: `ax5b`
routine 1258, and the much smaller routine 1260 block 16071, already
transcribed as `ax5b_16071_ts.strap` — implementing the timer is what
would let it RUN); 19-bit address truncation (routine 1274).

Out of scope by design: cycle-accurate timing.

## 6. Open questions — record, do not guess

* `BR`'s **absolute value** clause is unexercised: an effective address
  can only go negative through index modification, and `effAddr19`
  carries no sign beside its result.
* `R/`'s ZM clear may be **unreachable** (the divisor is the
  accumulator, which a ZM-setting multiply leaves at zero). Only FP
  paths were checked.
* The **fill loop** that copies `jb_ax5b`'s three-instruction template
  at `16090` into the word-spaced table slots has not been traced. The
  table's *units* are settled — 64 full words, from `160IT` at
  023201.00 to `160DMP` at 023301.00 — with the reasoning in
  `run_tests.sh` §"The interruption mechanism".

Two conventions that are not questions and cost a session each when
forgotten: Reference Manual **PDF page = printed page + 3**, and
`ja_ua1_ssip` is cited by **PDF page** because its listing carries no
printed page numbers.

## Traps this project has paid for

* A bare `*` or `L` assembles as **VFL**, not floating point. Write
  `*(N)`, `L(N)`.
* Give any data section an explicit `SLC`: `DD` emits at the location
  counter, so growing code silently overruns its own constants.
* Compute octal addresses with a helper. Every one written by eye in
  this project has been wrong.
* **Never edit a file while a suite or campaign is reading it** —
  worst of all `run_tests.sh`, which `sh` reads by BYTE OFFSET as it
  goes, so editing a comment anywhere above the live line shifts every
  later offset and the shell resumes mid-token. Kill the run and
  restart; there is no salvaging it.
* A verify script cannot tell you a **label** is on the wrong row: it
  checks what a symbol resolves to, and a misplaced symbol still
  resolves.
* When a rule has more than one implementation, each copy needs its own
  witness. `effAddr18/19/24` (3 copies), the SEOP rule (6), ZM's clear
  (16). **The MUTATION TABLE is subject to this rule too**, and broke
  it: two ZM mutants both hit `fpMul` because their pattern also
  matched `fpMulDouble` and `apply()` replaced only the first, so one
  copy of p.99's rule was untested by the suite *and* invisible to the
  campaign — 3059 PASS against a deliberate fault. A pattern matching
  twice is a tooling bug, not a mutant; `mutation_score.py` now
  refuses one.
* **A hang address read at the step cap is accurate to one half-word,
  not exactly.** The instruction counter oscillates between a
  self-branch and the half-word after it; the cap samples whichever
  clock it lands on. Measured: caps of 30000/30001 report one, 30002
  the other.
* **Bit offsets are printed in octal and written in decimal.** The
  listings and every address in `run_tests.sh` use octal (`004107.40`
  is bit 32); a program's source is decimal unless a `(8)` radix prefix
  says otherwise — and `(8)` applies to *both* halves of a bit address.
  Use `line_addresses.py`; do not convert by eye.
* **A zero half-word decodes as `BE, 0`** — BranchOrMisc code 000 is
  BRANCH ENABLED. Any program that runs off its own end into untouched
  storage turns the interruption system on.
* **A program cannot poll DS while enabled.** DS is permanently masked,
  so raising it interrupts at once and the mechanism turns it off
  before the next instruction. Observe protection violations through
  the interruption routine; put its marker in words 4–31, which p.31
  exempts from monitoring, or the marker store violates too and the
  machine interrupts forever.
* **Reverting an injection with `cp` can leave a stale
  `__pycache__`**: CPython compares source mtime at one-second
  granularity, so a restore inside the same second is not noticed and
  the injected bytecode is reused. Cost one wrong injection result,
  where injection 2 appeared to break a row injection 1 had broken.
  `rm -rf strap/__pycache__` on both sides of every injection.
* **A direct-index address is HALF-WORD granular**, 18-bit word plus a
  one-bit half-word select — so an encoding oracle cannot see a
  special register's bit offset within its half-word. Measured:
  moving `$LB` from (3,32) to (3,33), (3,40) or even (3,63) fails
  nothing; (3,31) and (4,32) do. That bits 32-49 are the lower
  boundary comes from the pocket card and p.31, not from any listing
  row. Found by trying the obvious injection and watching it survive.
* **A substitution can discard the thing that makes a test useful.**
  Routine 1260's boundary driver branches into an EIGHTEEN-entry
  error table, `B,160B17($X3)`, indexed — so the halt address names
  which bit failed. A first transcription collapsed it to one hang;
  an injected bit-17 fault then branched past its end into untouched
  storage, decoded `BE,0` and ran to 0. Still "caught", but unable to
  say what. When a deck spaces a table, the spacing is the diagnosis.
* **A summary column is not a measurement.** `mutation_score.py`
  printed the first failing section; this file read it as "the
  catcher" and built a near-miss rule on it. Every application of
  that rule was wrong. The tell: ask what the number would look like
  if the thing it names were merely *earliest* rather than *causal* —
  and if you cannot tell the two apart from the summary, go get the
  raw output. Both retractions today came from reading full logs
  instead of a one-line attribution.
* **An instrument that runs in parallel needs its isolation checked,
  not assumed.** `mutation_score.py` gives each mutant its own cloned
  tree — and five test scripts then wrote a FIXED `/tmp` path outside
  it, so twelve jobs raced on one file and the campaign blamed
  whichever script lost. Ask what a parallel job touches that the
  clone does not cover: `/tmp`, build caches, `__pycache__`. Three
  separate bugs this session were the same shape — shared state behind
  apparent isolation. A fourth was self-inflicted: running a test in a
  tree a background job was mid-rebuild in, which `bsc` reported as a
  stale `.bo`.
* **When one document says a thing twice, check it does not say two
  different things.** `archival_inventory.md` described routine 1268
  in two paragraphs twenty lines apart — once as the deck test of the
  DF/IF *indicators*, once as a look-ahead *forwarding* test. Only the
  second was right, and `NEXT.md` item 2 was built on the first for a
  year of work. A summary is not a source; the routine's own header
  settled it in one reading.
* **A deck can be the WEAKER test.** Routine 1268's forwarding check
  passes on this model even with the store-queue drain removed,
  because it spaces its store and load one instruction apart — tight
  enough for the real machine's look-ahead, not for this model's
  shallower pipeline. The hand-written `ebox_register_close_to_fetch`
  catches what the 1961 diagnostic misses. Transcription is the
  stronger standard for *encodings*; it is not automatically the
  stronger standard for *behaviour*.
* **A claim nothing can express is a claim nothing checks.**
  `bsv/README.md` said Transmit backward/`SWAP`/multi-word all set
  indicator 15; only `backward` did, for as long as the assembler
  could not encode a Transmit at all. The corollary above is usually
  applied to tests; it applies to prose too, and the tell is the same
  — ask what input could falsify the sentence, and check that one
  exists.
* **Distrust a blocker recorded in this file.** THREE times the thing
  stopping work was a claim here, not anything in the machine: "64 call
  sites need refactoring" (43 wrote constants that could never trip the
  rule), "the control-bit polarity needs Appendix C" (p.31 states it
  outright), and "1260 needs SSIP's `160S1` harness, reported at
  pp.41–44" (pp.41–44 are the per-indicator blocks, one of which was
  transcribed the same morning with no harness at all). Re-derive an
  obstacle before accepting it.
