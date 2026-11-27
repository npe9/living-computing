# `ref/pu/`: ICOT's held KL1 microprogram, executed

Rungs U1/U2 of `docs/pu_microcode_plan.md`. `pu.py` is a simulator of
the PU's E stage that executes the held microinstructions of
`PMPSI.DIR/pimm.MEkbn` image 2 (the Pseudo PIM/m KL1 firmware) word by
word, decoded generically by `asm/mekbn.py`'s field layout. `setup.py`
stands in for the D/A/R/S stages the decode entry's nano-code drives.
`check_pu.py` runs one KL1-B instruction on both this simulator and
`ref/pimm/pimm.py` and compares the results.

    python3 ref/pu/check_pu.py            the U1 check (in run_tests.sh, ~2 s)
    python3 ref/pu/check_pu.py -v         with every microinstruction executed
    python3 ref/pu/check_pu.py --inject NAME
    python3 ref/pu/measure.py             the counts behind the rules, pinned
    python3 ref/pu/u2_append.py [-v]      the U2 harness: append/3 whole (in run_tests.sh, ~3 s)
    python3 ref/pu/u2_append.py --inject NAME

The microcode is third-party and stays out of git: it is read from
`docs/nonlocal/psdpim.tar.Z` at run time, as `asm/psdpim.py` reads it.
Nothing here prints or stores image words except under `-v`, to the
terminal.

## State (2026-11-27)

**U1 reached; U2 not reached** (furthest point 15 of 16 instructions of
append: the second reduction's `get_value` runs the general unifier
whole, 16 words; the stop is `proceed`, the last instruction: section
"U2" below).

- 32 cases, all PASS (80 held microinstructions executed). The 32nd
  is a held `case_branch` (`2d3e` set-up, `2d3f` JMPF 3: tags 08/0a/04
  land on `2d40`/`2d43`/`2d4e`, base | the `5300` column-2 byte). Since the
  first 28: a held call word (`scsi_init`'s `615e` calls `3320`; the
  return lands on `615f`), the refill with an HP given (stops at `3365`
  on W0d), and the step contract (evaluate twice gives equal records and
  changes nothing; commit returns `next`). Every compared case enters
  through decode-table dispatch from the instruction cell
  (`setup.dispatch`). Of the first 28 (69 words): 22 compared
  against `pimm.py` (44 executed and matched: 33 in multi-word
  routines, 11 in one-word ones); 4 that take the last cell of a free
  list and must enter the refill (17 words executed up to the refill,
  where they stop, as they should); and the one-cell allocator `3320`
  called as a microsubroutine (EXECUTED, 4 words: W1c = `{REF, cell}`,
  the cell `UNDF 0` as `pimm.py`'s `new_var` makes it, R19 left holding
  the link, one memory write; its last-cell arm stops at `3324` on R05,
  as it should). `measure.py`'s pins (the counts behind the rules) are
  checked in the same run.
- Multi-word routines that run as held: `set_nil`, `write_nil` (2
  words: a stamp, then a write and a structure-pointer step),
  `set_variable`, `write_variable` (3: a pop from the one-cell list, the
  new cell made `UNDF`, a `REF` to it), `put_variable` (4), `put_list`,
  `put_vector_1`, `put_vector_2` (3: a pop, the list or vector pointer,
  the structure pointer).
- Held out: `set_marked_variable`, `write_marked_variable`,
  `put_marked_variable` (entries `318d`, `3197`, `31d5`; 3, 3 and 4
  words) were added after every rule was fixed and passed unchanged,
  `REFx` compared exactly. (The check's `indirect` comparison had to
  accept `REFx` as well as `REFo`; no rule changed.)
- One-word routines (`set_value`, `set_integer`, `set_atom`,
  `put_value`, `put_integer`, `put_atom`, `put_nil`, `put_vector_0`,
  `write_value`, `write_integer`, `write_atom`) pass too, but they prove
  only the plumbing: their whole meaning is in the set-up, which is a
  stand-in.

**What the held words answered that `pimm.py` had chosen** (the
firmware is the authority; `pimm.py` was not changed in this task):

1. `write_variable` (`3195`-`3199`): the structure element is a
   `{REF, c}` to a NEW cell `c` taken from the one-cell list and made
   `UNDF`, and `r[x]` gets `{REF, c}`. `pimm.py` makes the element
   itself the variable ("our choice: the machine's is not known",
   `i_write_variable`). The same term after dereference; declared in
   the case as `indirect`.
2. `put_list`, `put_vector_1`, `put_vector_2`: the pointer put in `r[x]`
   has its MRB off (`LISTo`, `VECT1o`, `VECT2o`, the stamp immediates at
   `31d0`, `31f9`, `31fd`). `pimm.py` writes it with the low bit set
   ("what the machine does there (MRB) is not known",
   `pimm_semantics.md` put_vector_N). Declared as `mrb`.

## The rules, each with its evidence

**Adopted from the static agent** (`docs/pu_microcode_inference.md`
section 7, labels as there): the control store `kl1_wcs`
(CORROBORATED); sequencer S1-S8, with S8 `case_branch` (INFERRED,
mechanism DOCUMENTED); S9 (JMPF 1 EM `7fff`) and S10 (JMPF 2) raise; the
`5300` TGT, column 2 for EM1 `3a` (VERIFIED), other columns raise; the
`6c21` trap; CNDF 5 = eq, CNDF 7 EM1 `0a` = lt, `09` = overflow (up to
one global polarity; not yet met on an executed path here); the timing
of conditional a/b/c/e a switch, `cjump_time`, None by default (raises;
since U2's fifth session 'prev', below).
Its datapath confirmations (bit 62 write, 58 MAR2, 59 MDR2 on reads,
TGIF 1/2, old-MDR write, ALF 0/1, the SD1F/AS1F/AS2F/ADF values) are the
rules this simulator already ran; TR-733's elimination rests jointly on
the allocator contract, which `check_pu`'s allocator case executes.

MEASURED rules are `asm/mekbn.py`'s and pinned by `mekbn.py --check`
(field positions; JMPF kinds; the strobes 61/62/60; 58/59 as MAR2/MDR2;
SD1F/ADF/AS1F numbering; SC2F 8/9 immediates; TGIF 1/2 stamps; "one
word later"; a write stores the MDR as it stood before its word).
These are used as they stand. The INFERRED rules added here, with the
microaddress that decided each (all in `pu.py` `RULES` / `COND_RULES`
and `setup.py`):

| Rule | Decided at | Evidence |
|---|---|---|
| Operand selects `a` = y, `b` = z (8 = opcode, 9 = x are MEASURED) | `318f` (`set_variable` writes its REF to `opda`; `pimm.py` `reg[y]`), `31d7` (`put_variable`, `reg[y]`) | the `pimm.py` operand readings; `b` is not yet executed |
| TGIF 3: both stamps, the tag from EM2 | `3193` (`write_nil`: EM1 `20`, EM2 `02`; the cell must be `ATOM 0`) | thesis p.144 "EM2 can also be the DST-Bus tag immediate"; predicted at `3365`/`3366` (the refill, read not run): EM2 there is `VECT0x`, the free-cell link tag MEASURED in section 15, where EM1 would give `STRGx`. This changes `mekbn`'s trace of `1c0f` (cell 15 of `suspend`'s record), which takes EM1 |
| A write with bit 59 stores MDR2 | `31d7` (`put_variable`: the cell gets the `UNDF` of `31d6`; MDR1 holds the link) | **conflict, open:** the refill loop `3367` (CCF `16`, bits 62, 60, 59) must write MDR1, the running link, to build a list; `31d7` is CCF `12`. CCF is probably a coded field, as `rassy`'s value table says (`binary_reverse_engineering.md` section 3), and bit 59 alone does not choose the data register |
| MCF with EM1 `20` steps R02 by one | `31c7` (`write_integer`: one word, MCF, EM1 `20`; `pimm.py` `_sp += 1`; `set_integer` has neither and leaves sp), `3193` | 22 of the 23 self-loops carry MCF with EM1 `10` (a loop counter, below), so EM1 may select MCF's operation; but `3365`/`3366` carry CNDF 6 with EM1 `0f` and no MCF, so EM1 may belong to the condition instead. Any other MCF use raises |
| JMPF bit 26 (codes b, c, e) makes a jump conditional; 3, 4, 6 jump unconditionally whatever CNDF holds, and their CNDF only forms COND for a later word | `318c` (`set_variable`, JMPF 4 CNDF b, must jump over `set_marked_variable`'s `318d`-`318e`) | measured over both stores, "Conditions" below; replaces `mekbn.tested()` inside the simulator |
| CNDF 9: COND := tag of the ALU's first input = EM1; CNDF b: = EM2 | `31fa`, `31d1` (EM1 `ATOMo`), `318c`, `3196`, `31d6` (EM2 `ATOMo`), each tested by the conditional end that follows | "Conditions" below; the refill writes `{ATOMo, 0}` as the last link (`3368`) |
| A conditional JMPF 1 with EM bit 0 set is taken when COND is false | `31fb`, `31d2`, `318f`, `31d8` (a pop's end, taken unless the link was the end marker) | one fit; the opposite pairing (COND true when the link is a cell, bit 0 = taken on true) is not told apart by these words. EM bit 0 clear: raised in U1; decided in U2 (`j1_bit0_clear_true`, below) |
| ODPF 1: the S stage loads R(10 or EMO1) into MAR2 (ODSF 0) or MAR1 (ODSF 1) | `318b` (`set_variable`), `31d0` (`put_list`) | predicted for `put_variable`, `put_vector_1/2`, `write_variable` (run); read for `proceed`, `collect_list`, the marked forms (`setup.py` header). Nano-code field positions are Fig. 3-22 right-aligned on the entry's 56 bits; only ODPF, ODSF, EMO1, EMO2 are used |
| AS1F 3 with AS2F 0: the first ALU input is the constant EM2 (the result tag from AS2) | `3321` (the allocator loads R03, `rassy`'s `lc`, with EM2 13), `3378` | thesis p.144 (AS1F modifies AS2F's meaning for constants). The value is not compared with any oracle: the evidence is arithmetic, EM2 13 beside the one-cell list (`3321`, `3378`) and 5 beside the two-cell list (`332f`, `337b`), 16 - 3 and 16 / 2 - 3, a 16-word refill chunk. The injection `as1f3_off` shows only that the rule is needed at `3321` |
| R06 = R07 = 0 | `31d6` (`{UNDF, R07}` where `pimm.py` writes `UNDF 0`) | `{ATOMo, R06}` stands where a nil does (section 17) |

**Conditions.** `measure.py` (pinned, run by `check_pu.py`). The word
after a JMPF 3/4/6 word is zero or an explicit branch target in 47-83%
of cases, with or without CNDF; after a JMPF b/c/e word in 3-17%
(image 2, with/without CNDF: 3 69%/83%, 4 76%/74%, 6 51%/47%, b 13%/3%,
c 8%/3%, e 11%/17%; `syspsi`: 3 49%/68%, 4 59%/70%, 6 51%/54%, b
7%/40%, c 5%/6%, e 8%/13%; the one exception, `syspsi`'s JMPF b without
CNDF, is 6 of 15 words). Self-jumping words: all 23 of image 2 are c
or e, 36 of 37 of `syspsi` (the other, `syspsi` `4de1`, JMPF 3 with
CNDF 7, would loop until a trap or interrupt under this rule). As a
held-out test, `mekbn`'s own flow measures under the bit-26 rule in
place of `tested()`: after a call, returns/ends go from 222/10 to 234/9
(image 2) and 250/13 to 264/7 (`syspsi`); decode entries still reach an
end and never a return (96 to 107 ends in image 2, 125 to 119 in
`syspsi`). The call/return separation improves; `mekbn.py` and its
pins are not changed. In image 2, 22 of the 23 self-jumping words carry
MCF with EM1 `10`, 20 of them with CNDF 6 (two b; `281f` has CNDF 2 and
no MCF): INFERRED, a counted loop on the loop counter (`rassy`
names register 3 of the second bank `lc`, and `3378` loads R03 before
the refill's loop). CNDF 9 words leave EM1 free (TGIF 0 in 448 of 453)
and their EM1 values are tags (`ATOMo` 105, `INTo` 94, `REFo` 32,
`VDESC` 26, `FPREC` 24, `SHREC` 20, `MOD` 17); CNDF b words use EM1 for
a stamp in 24 of 56 and their EM2 values are tags (`ATOMo` 15, `INTo`
14, ...). CNDF 1 words subtract (ALF 1 in nearly all): an arithmetic
condition, not run.

## OURS (the stand-ins)

- `setup.py` FORMS: which operand the S stage puts in MDR1 and which
  address in MAR1, per operand form, from `pimm.py`'s operand readings:
  a goal argument at R10 + argument number (R10 = `cgp` in `rassy`'s
  register names, M92 p.428 "CGP to locate a goal argument"), a
  structure element at R02. Reading the select `10 | n` with WRBF clear
  as `rassy`'s register-file entry n is INFERRED: it fits every register
  the routines run here use (R10 `cgp`, R19 `fvp`, R1a `flp`, R1f `hp`)
  and those sections 17-18 found (R13 `cfpp`, R14 `gsp`); `rassy` gives
  names and numbers, not the select encoding.
- Free lists already built (`check_pu.py` `seed_lists`), in the shape
  the firmware writes: cells `{VECT0x, next}`, the last `{ATOMo, 0}`.
- Memory: a flat dict; the goal record being built at `f1000000`, the
  lists at `f2000000`/`f3000000`.
- HP (R1f) = `{REF, f4000000}` in the allocator, held-call and
  refill-with-hp cases: the allocator reads it at `3322`, the refill at
  `3378`. No case checks what is done with it beyond that.
- The Pseudo PIM/m environment is not needed for these routines: no
  routine run here touches I/O or the TLB. The control store is
  `pu_store.Stores.kl1_wcs` (image 2, then `syspsi` from `6800`,
  resident: CORROBORATED by the static agent), so `scsi_init`'s `615e`
  is held code; `6c21` raises `Trap` (the illegal-instruction trap).
- The tag-dispatch RAM is not a stand-in: `sysinit`'s table at `5300`
  (`asm/pu_sysinit.py`), column 2 for set-up EM1 `3a` only. The tag
  a set-up dispatches on is taken from its ALU input (INFERRED; a
  set-up with no ALU input, `1d3f`, raises).

## Fault injections (observed, `--inject`, in-process, no file edited)

| Injection | Observed |
|---|---|
| `tgif3_em1` (TGIF 3 tag from EM1) | `write_nil` FAILs (cell `20:0` for `02:0`); nothing else |
| `w59_mdr1` (a bit-59 write stores MDR1) | `put_variable`, `put_marked_variable` FAIL (no cell with `UNDF`) |
| `write_same_word` (a write stores the MDR as loaded in its own word) | `set_variable`, `write_variable` and their marked forms FAIL |
| `opd_a_is_z` (select `a` = z) | `set_variable`, `put_variable` and their marked forms FAIL (wrong register written) |
| `cnd_em_swapped` (CNDF 9 against EM2, b against EM1) | the four last-cell cases FAIL (the pop ends without entering the refill) and the allocator run FAILs (W1c `06:f2000000`), as does the refill with an HP (6 in all); the 22 compared cases still pass, which is why the last-cell cases exist |
| `odsf_swapped` (ODSF 0 = MAR1, 1 = MAR2) | 15 cases STOP (MAR2 / MAR1 never set): every pop, the refill with an HP, the step contract |
| `as1f3_off` (AS1F 3 unmodelled) | both allocator runs, the held call and the refill with an HP STOP (4); the last-cell cases without an HP stop on R1f before reaching AS1F 3 and still pass |
| impure `evaluate` (COND set before commit; a scratch monkeypatch, not an `--inject`) | the step contract FAILs; nothing else |
| `cond_prev_strict` (a conditional JMPF 1 must test a COND formed by the very previous word) | `put_variable` (twice, with the last-cell case) and `put_marked_variable` STOP at `31d8`: `31d7` (CNDF 0) stands between the forming word `31d6` and the end, so COND survives a CNDF-0 word (EXECUTED) |

## First routine that would not run

**The free-list refill, `3365`-`337f`**, entered at `3378` (one-cell
list) or `337d` (two-cell list) when a pop takes the last cell. It
stops at once on R1f (the heap pointer, `rassy`'s `hp`), which no case
sets. Given one (a scratch probe, not in the check), AS1F 3 now runs
(the rule above) and the routine stops at `3365` on a read of work
register W0d, never set (now a case in the check, "refill with hp").
Who sets R1f and W0d first is UNKNOWN: image 2 has 17 words that write
R1f (three below the lowest decode entry, at `0159`, `019a`, `029b`),
14 that write R05 and 4 that write W0d (after the entries of
`collect_garbage`, `proceed`, `merge`, `enqueue_goal_with_priority`),
none of them run. Read, not run, it also needs: MCF with EM1 `10` and
CNDF 6 (the counted loop `3367`, 13 or 5 iterations) and the write data
of CCF `16`, which conflicts with the bit-59 rule above.

**The allocator for three cells and more, `3331`-`3347`**
(`put_vector_3`..`_6`, `new_vector`, `suspend`): stops at `3331` on
R05, the base of a table of list heads in memory whose contents are set
at boot, and then needs SC2F `b` (the "wide" immediate, layout not
read) and the `pass_as2` addressing at `3343`.

## The step interface (for a harness)

`pu.py` is importable on its own (`sys.path` to `ref/pu` and `asm`).

    p = PU(fw)                 # fw: asm/mekbn.Firmware(); state empty
    p.ir = (tag, value)        # the instruction cell (the opd selects read it)
    p.an[i], p.r[n], p.w[n]    # argument registers, register file, work registers
    p.wr[...]                  # XR, YR, MAR1, MAR2, MDR1, MDR2
    p.mem[addr] = (tag, value) # memory, a dict; a read of an absent cell gives
                               # pu.POISON, which raises when used (RULES['absent_read_poison'])
    rec = p.evaluate(upc)      # one microcycle from the OLD state; changes nothing
    nxt = p.commit(rec)        # applies rec at once; returns rec['next']
    nxt = p.step(upc)          # evaluate + commit
    n = p.run(upc)             # to the routine's end; returns words executed
    n = p.call(upc)            # a microsubroutine, to its return
    setup.setup(p, name)       # OURS: the D/A/R/S stand-in; returns the start address
    name, start = setup.dispatch(p)   # the held decode table from p.ir, then setup

Each record (`rec`, also appended to `p.cycles`) has `cycle`, `micro_pc`,
`microword`, `reg_reads`, `reg_writes`, `wr`, `mem_reads`, `mem_writes`,
`cond`, `cond_cycle` (the cycle whose word formed COND), `tdar`
(`(cycle, byte)` of the last case_tag_setup), `mcf`, `flags` (the sw
flags an MCF sets or resets in this word), `alf` (the set_alf latch
after it), `push`, `pop`, `next`
(`None` at an end, `-1` a return to a `call`); the format is in `docs/pu_microcode_plan.md` "The trace". Any
field value not modelled raises `Unmodelled(upc, what)` (reaching
`6c21` raises its subclass `Trap`), with
`.words` the words executed before it when raised from `run`/`call`.
The decoded rules are module dictionaries, `RULES` and `COND_RULES`, so
a harness can change one (as `check_pu.py --inject` does) without
editing the file.

## U2: append/3 on the held microcode (2026-11-26, second session; 2026-11-27, third to seventh)

**U2 not reached. Furthest point: 15 of 16 instructions executed and
matched (49 held words), then a stop at the sixteenth, `proceed`.** The
seventh session (2026-11-27) took it from 14 of 16: `get_value 1,2,0`
(nil against the unbound Z1) runs the general unifier whole (16 words,
row 14 below): `case_tag_setup` in general (EM1 `30`-`3f`), JMPF b
decided as a conditional call, the dereference subroutine `0c15` /
`0e38` / `0e60`-row returning, the binding at `0864`, the sw01 flag.
The sixth
session (2026-11-27) took it from 12 of 16: `switch_on_non_list` on nil
branches to the label (`3310`-`3311`, `2447` JMPF 2, `2440`, `2461`,
`241d`), then the alternative clause's `wait_nil` (`3980`, `3985`), and
`get_value` runs `38b0`-`38b3`. The fifth
session (2026-11-27) took it from 10 of 16 (stop `execute`, no set-up
form): `execute`'s fast path `4cc0`-`4cc3` runs and the second
reduction's `try_me_else` after it. The fourth took it from 4 of 16
(stop `put_reused_structure` `31e8`); before that 2 of 16, a stop at
`read_variable` (`34a0`). Plus a held boot routine run (start's heap
top, `204b`-`2052`, 6 or 8 words).

**A harness bug, fixed 2026-11-27:** `pimm.py` writes its R and M trace
lines straight into `Machine.tr` (`_Regs`, `_Mem`), not through
`event()`, and the harness took each instruction's lines from `event()`
alone. So no instruction had an R or M line to compare, and any register
the firmware wrote counted as a stray write. The first two
instructions write neither, so their result stands; now each
instruction's lines are the slice of `Machine.tr` between its I line and
the next (`read_variable` 3 has `R 3 0200000123`).

`u2_append.py` runs the IPL image's own `append/3` (`scsi_fep_module`,
cells 6644-6658) as `append([a], [], Z)`: two reductions, 16
instructions on `pimm.py`. The PU executes the same instructions in
`pimm.py`'s order with its state carried over (registers, R02, R11,
free lists, memory); the D stage is the held decode table, the E stage
the held routine. OURS: the A stage (cell and address from `pimm.py`'s
trace), the goal switch before the first instruction (A0-A2 as
`pimm.py` leaves them), the seeded free lists, memory as `pimm.py`'s
cells. OURS too: `read_variable`'s MAR1 = R02 (`setup.FORMS`), only so
that it stops at a microaddress. Per instruction, every R and M line of `pimm.py`'s trace is
compared under `check_pu.Rename`; `sp` against R02; try_me_else's
alternative against R11. Two **declared differences**, as U1's
`indirect` and `mrb` in `check_pu.py` (both in `u2_append.py`, each
with an injection that turns it off and FAILs):

- `reuse` (`DECLARE_REUSE`): `put_reused_structure` on a structure whose
  pointer has its MRB off reuses the cells in place (`31ec`-`31ed`: x
  and R02 := the pointer, no cell written, no list popped); `pimm.py`
  never reuses (`i_put_reused_structure`: z new cells, "no reference
  counts here, so nothing is ever reused"). Declared only when the
  firmware's x holds the source's own address; `pimm.py`'s z new cells
  are then paired with the reused ones, so `write_value` and
  `write_variable` after it are compared cell by cell. The firmware is
  the authority (TR-466 4.2: "When the input cons cell is
  single-referenced, it can be reused as the new output cons cell");
  `pimm.py` is not changed here (another agent owns it).
- `indirect` (`DECLARE_INDIRECT`): U1's `write_variable` difference
  (below, "What the held words answered" item 1) carried over.

| # | Instruction | Words | Result |
|---|---|---|---|
| boot | start's heap top `204b`-`2052` (called as from `2028`) | 6 (aligned) / 8 | R1f = the parameter cell `1a0 + 4a` rounded up to 16, on 5 parameters (contract) and on `pimm.py`'s heap pointer |
| 0 | `try_me_else 0, @6658` (`216a`) | 1 | ok: R11 = `{REFo, load + 6658}`, `pimm.py`'s `alt` |
| 1 | `switch_on_non_list 0,0,8` on a list (`3300`-`3301`) | 2 | ok: R02 = the car's address, `pimm.py`'s `sp`; COND true, the jump to `3305` not taken |
| 2 | `read_variable 3,0,0` (`34a0`-`34a2`, `3494`) | 4 | ok: A3 = `{ATOMo, a}`, R02 + 1 (`pimm.py`'s `sp`) |
| 3 | `read_variable 4,0,0` (the same words) | 4 | ok: A4 = `{ATOMo, 0}` (nil), R02 + 1 |
| 4 | `put_reused_structure 0,0,2` (`31e8` entry, `31ec`-`31ed` run) | 2 | ok under the declared `reuse`: the ODPF 3 start for a tag other than the immediate `1e` is `31ec`; x := A0 (`{LISTo, c}`), R02 := it, COND (EM1 `29`) false, end; `pimm.py`'s new cells paired with `c`, `c + 1` |
| 5 | `write_value 3,0,0` (`31c9`) | 1 | ok: `[R02]` := A3 (`{ATOMo, a}`) into the reused car, R02 + 1 |
| 6 | `write_variable 3,0,0` (`3195`-`3199`) | 3 | ok under the declared `indirect`: a cell popped from R19 made UNDF, the cdr and A3 := `{REFo, it}` |
| 7 | `get_bound_value 2,0,0` (`3880`) | 1 | ok: the S stage dereferences A2 to Z's UNDF cell (immediate UNDF: the entry itself, MAR1 = the cell), MDR2 := A0; `3880` writes `[MAR1]` := `{LISTo, c}` (`pimm.py`: Z bound to the new list) |
| 8 | `put_value 0,4,0` (`31da`) | 1 | ok: A0 := A4 (nil) |
| 9 | `put_value 2,3,0` (`31da`) | 1 | ok: A2 := A3 |
| 10 | `execute 3, append/3` (`4cc0`-`4cc3`) | 4 | ok: the fast path. Set-up MDR2 := the label (OURS); `4cc0` YR := R0d, R15 := YR (AS1F 2), COND := slit_check (clear); `4cc1` XR := W1f, MDR1 - YR (CNDF 3, STALE, untested), JMPF b to `4cc5` tests `4cc0`'s COND: not taken; `4cc2` XR := `{COD, R04}`, R04 := `{COD, MDR2}` (TGIF 3, EM2 = COD), COND := interrupt_all (clear); `4cc3` W14 := XR, MCF EM1 06, end (COND false). R04 = `{COD, load + 6644}`, `pimm.py`'s next instruction |
| 11 | `try_me_else 0, @6658` (`216a`) | 1 | ok: R11 = the alternative, as instruction 0 |
| 12 | `switch_on_non_list 0,0,8` on nil (`3300` entry; `3310`-`3311`, `2447`, `2440`, `2461`, `241d`) | 6 | ok: the label branch. The S stage: row 4 (`setup.S_OTHER_ROW`), TDAR := column 7's byte for ATOMo, 0 (`setup.S_TDAR`), MDR2 := A0 (OURS); `3310` XR := R04, YR := c16, COND := MDR2 is REFo (false); `3311` XR + YR; `2447` YR := 1, MDR2 := mrb_off(MDR1), JMPF 2 to `2440` \| 0; `2440` x := MDR2 (nil, unchanged), JMPF e to `2461` (taken: COND false), COND := COL (false); `2461` R04 := XR + YR = `{COD, pc + 2 + 8}`, MCF 08 (pipeline_cancel), JMPF e to the end `241d`. R04 = `pimm.py`'s next instruction (6655), with the A stage's R04 = pc + 1 (OURS) |
| 13 | `wait_nil 0,0,0` (`3980`, `3985`) | 2 | ok: the S-stage COND (own tag ATOMo == the immediate; pinned by `s_cond_false`, which FAILs instruction 1) takes `3980`'s JMPF a (if cond) to `3985`; `3980` forms CNDF 2 on x's value (zero: nil), `3985` ends on it |
| 14 | `get_value 1,2,0` (`38b0`-`38b3`, `0c0c`, `0c15`, `0e38`, `0e75`, `0e72`, `0c0d`, `0c0e`, `0802`, `0840`, `0841`, `0864`, `09d0`) | 16 | ok: nil bound into Z1's cell (`pimm.py`'s M line). x (nil, not UNDF) takes row 4: `38b0` MAR2 := A1, COND := its tag is REFo (CNDF 8, false); `38b1` a conditional call (JMPF 9) not taken; `38b2` MDR2 and MAR2 := A2 (SD1F 3), COND := its tag is a REF, MRB ignored (CNDF c, true); `38b3` W1c := MAR2, jump `0c0c`; `0c0c` W1d := MAR1 (STALE, dead), `case_tag_setup mdr2 7` (column 0 of A2's REFo: 0), JMPF b: a call, taken on `38b2`'s COND; `0c15` W1b := MDR1, MDR2 := [MAR2] (Z1's UNDF cell), case_branch `0e38` \| 0; `0e38` W1c := MAR2, `case_tag_setup mdr2 2` (column 5 of UNDF: 18), page jump `0e75`; `0e75` MCF reset_sw01, case_branch `0e60` \| 18; `0e72` MDR1 := W1b, return; `0c0d` XR := W1d, `case_tag_setup mdr1 1` (column 6 of nil: 0); `0c0e` MAR1 := W1c, jump `0802`; `0802` as1_3 - MDR1 (UNKNOWN source: COND and the set_alf latch POISON), case_branch `0840` \| 0 on `0c0d`'s set-up; `0840` `case_tag_setup mdr2 0` (column 7 of UNDF: 4); `0841` COND := alf_equal (POISON), case_branch `0860` \| 4; `0864` [MAR1] := MDR1 (the cell := nil), COND := sw01 (clear), page jump `09d0`; `09d0` MDR1 := mrb_on(MDR1), end if not COND (taken) |

Before the program, `read_variable` on a structure whose element is a
list pointer (`LISTo`, the structure reached with every MRB off,
`pimm.py`'s `sp_single`) runs on both models: x := the element, R02 + 1,
no memory write (`34a0`-`34a2`, `3494`, ok). It is the case that tells
the dereference set-up from a TGT column (below). And one S-stage case
decides `S_ENTRY` on its own:
`get_atom` (entry `3800`, tag immediate UNDF) on an unbound variable,
on both models from the same state: the cell must be bound to
`{ATOMo, atom}` (`3800`-`3801`, 2 words, ok). Every write the firmware
makes to an argument register or a cell with no `pimm.py` R or M line
for it is a FAIL too (probed in-process: a stray A9 and a stray cell
write both FAIL at instruction 0).

**New rules** (in `pu.py` `RULES` / `COND_RULES`, `setup.py`):

| Rule | Label | Decided at | Evidence; injection (observed) |
|---|---|---|---|
| `setup.S_ENTRY`: when the dereferenced operand's tag equals the entry's tag immediate EMO2 (MRB included), the routine starts at the entry itself, with COND = (the operand's own tag, before dereference, == the immediate) and MAR1 = the last cell the dereference read | INFERRED (mechanism DOCUMENTED, thesis pp.134-137) | `3800`-`3801` (get_atom on an unbound variable); run at `3300`-`3301` | thesis p.135: "COND = (A[i].tag==list)" set by the S stage, and p.137 the start address changed by the tag compare; `3800` is the word that stamps ATOMo on the constant, so entering past it binds the cell untagged. Injections: `s_imm_plus1` (entry + 1): get_atom FAIL (cell `00:00000456`, `pimm.py` `02:00000456`), append unchanged (2 of 16, 2 words: entry + 1 gives the same registers at `3301`); `s_imm_row` (every tag takes the TGT row, column TDPF, 4-word rows): get_atom STOP at `3810` (CNDF a), append STOP at `3309` (MCF EM1 06), 1 of 16; `s_no_mar1` (MAR1 not loaded): get_atom STOP at `3801`; `s_cond_true` (COND forced true): nothing changes, so the COND part fits but is NOT discriminated. Joint with `setup.S_CONST` (MDR2 = the untagged atom, OURS). The list case takes 2 words where Table 3-6 gives get_list 1 step: an open tension |
| `RULES['sc2_wide']`: SC2F b is EM2:EM3 (10 bits), zero-extended; EM1 non-zero and not a TGIF 1/2 stamp raises | INFERRED | `204b`-`204d` | static: words loading 1a0 carry EM1 0 or a stamp tag (`2071` `{REFo, 1a0}`, `2077` `{INTo, 1a0}`). Injection `wide_em1em2` (EM bits 15..4): the boot reads memory `1e`, never written: STOP, boot contract FAILs on all 5 parameters (since 2026-11-27 the read gives POISON and the stop is at `204f`, the ALU input) |
| `COND_RULES[2]` / `RULES['cnd2_zero']`: CNDF 2 = the ALU result is zero (`rassy`'s `alf_zero`) | INFERRED | `204f`-`2052` | contract: start's heap top is its parameter rounded UP to 16 (never below: the cells below are in use). Injection `cnd2_nonzero`: all 5 parameters FAIL (aligned +16, unaligned rounded down) |
| `RULES['j1_bit0_clear_true']`: a conditional JMPF 1 with EM bit 0 clear is taken when COND holds | INFERRED by the static agent (6.3 item 4); now EXECUTED on a return | `2050` | jointly with CNDF 2 above (the pairs (zero, taken if COND) and (not zero, taken if not) are the two that pass). Injection `bit0_clear_off`: STOP at `2050` on every parameter |
| R11 holds try_me_else's alternative (`rassy`'s register-file 1, `ap`) | INFERRED projection | `216a` | `R11 <- {REFo, MDR1}`; the fail paths of `wait_*` (`3982`-`3983`, `39a6`-`39a7`) load XR from R11 and write R04 (`pc`). The label is the A stage's (OURS: MDR1 = pc + 2 + c16) |
| `pu.DEREF_SETUP`: CNDF 7 with EM1 `2d` (JMPF 0 sequencing) is the dereference multiway set-up: TDAR := code << 2 from the tag of the AS1 input (MDR1 at `34a1`, the element `34a0` read); code 1 = other (not a REF, not the EM2 immediate) | INFERRED (mechanism DOCUMENTED: thesis printed p.133, section 3.3.4.1, the three-way "ref / equal to the microinstruction's immediate / other" code in TDAR bits 3-2, and the KL1 four-way that also tells a ref's MRB) | `34a1` | the oracle wants row `3494` (x := the element, MCF EM1 20 steps R02) for an atom (both of append's `read_variable`s) and for a list pointer (the list-element case). Static: `34a2` (after `2d`) and `343a` (after `2f`, `read_atom`..`read_constant`) branch on bases `3490` and `3492`, whose 2-word rows interleave in `3490`-`349f`; the other `2d` site (`41b6` -> `41b0`) has 4-word rows. No column of `5300` sends ATOMo to `3494` and every tag to a row's first word (scratch script, 8 columns: only column 0 sends ATOMo to `3494`, and it sends LISTx to the zero word `3491`, REFx to `3493`). The other codes are read from the rows, NOT run, and raise: 0 = equal to EM2 (`1e` at `34a1`: `3490` stamps VECTx on the element and writes it back), 2 = REFo (`3498` puts the cell pointed to on the R19 list, then the `3440` table), 3 = REFx (`349c`, the `3460` table, no freeing). `3440`-`3453` and `3460`-`3471` are case tables that fit `5300` column 5 exactly (REFo 0, REFx 1, INTo/ATOMo/VECT0o/FLTo 2, the `x` tags 3, INTx 4 ... VECT0x 7 re-stamped `o`, UNDF/HOOK 12) behind set-ups with EM1 `34`: read, not run (EM1 `34` -> column 5 is not adopted). Injections (observed): `deref_imm_other` (codes 0 and 1 swapped): append STOPs at `3490` (ALU input from the POISON read), 2 of 16; the list-element case FAILs (`3490`-`348f` write `{VECTx, ...}` over the element). `deref_bits10` (code in TDAR bits 1-0): both STOP at the zero word `3491`. `deref_tgt_col0` (the set-up read as TGT column 0): **append still passes, 4 of 16**; the list-element case STOPs at `3492` (R11 never set): that case is what discriminates. `deref_tgt_col5` (EM1 & 7): append STOPs at `3492`; `deref_tgt_col7`: append STOPs at `3490`, the list case at `3492` |
| `pu.COND_UNKNOWN`: CNDF 7 with EM1 `28` is a condition whose meaning is UNKNOWN; COND := POISON, which raises if a later word tests it | INFERRED (that it is a condition, not a set-up) | `34a0` | 24 of the 54 EM1-`28` words of image 2 carry a conditional JMPF a/e; its only other word with a branch two words on (`572c`) has a JMPF b there, not a case_branch; at `34a0` the set-up for `34a2` is `34a1`'s. Nothing tests the COND before `read_variable` ends: it contributes nothing on the executed path, NOT discriminated. Injection `em1_28_tgt0` (`28` a case_tag_setup, column EM1 & 7): STOP at `34a0` (no ALU input) |
| `RULES['jmpf8_setup']`: JMPF 8 sequences as JMPF 0 in a word whose CNDF 7 is a dereference set-up | INFERRED, admitted only in that combination; every other JMPF 8 word raises | `34a1` | thesis printed p.144 (7): part of the condition generation moved from CNDF to JMPF; what bit 26 adds to a set-up is not decided (the twins `0517`/`051c`, EM1 `2b` with JMPF 0 and 8, are both followed by a case_branch). Injection `jmpf8_off`: STOP at `34a1` in append and in the list case |
| `RULES['absent_read_poison']`: a read of a cell never written gives the MDR the value POISON; using it (ALU input, write data) raises | OURS | `34a2` | `34a2` reads [MAR1] where MAR1 holds the element itself (an atom, not an address); only the REF rows use what it reads. Injection `absent_read_raise` (the old rule): STOP at `34a2`. `check_pu.py`'s injections give the same results as before |
| `read_variable`'s MAR1 = R02 (`setup.FORMS`) | OURS, with support | `34a0` | the entry's OS1F is 6 and the thesis's list of S-stage set-up sources (printed p.128) numbers (6) the structure pointer S, as it numbers (4) WR, which fits OS1F 4 in every ODPF 1 entry run (R(10 \| EMO1)); but `read_atom`/`read_integer` have OS1F 5, so the numbering is not fitted. DFF 2 (printed p.127: the R stage's three fetch kinds) is not used on this path: `34a0` reads [MAR1] itself and nothing reads what an S-stage fetch would leave in MDR1 before `34a0` overwrites it |
| `setup.ODPF3_SHIFT`: an entry with nano-code ODPF 3 and a tag immediate starts at entry \| code << 2: code 0 when the dereferenced operand's tag equals the immediate (MRB ignored), 1 otherwise | INFERRED (mechanism DOCUMENTED: thesis printed p.129, ODPF generates the start address, its low bits modified by the tag test; p.136, `add`: "if (data.tag==int) start(for_int) else start(for_others)"; p.133, the code in TDAR bits 3-2) | `31ec` | static (scratch census of the decode table): 25 entries have ODPF 3, 19 with a tag immediate; 14 of those 19 (all INTo) reach the failure exit XR := R11, R04 := XR from entry + 4, `less_than`..`modulo` at entry + 4 itself (entry + 8 is the next entry: no third row), `shift_left`..`exclusive_or` after further tests (`3b23`); the 4 `*_extended` call `0d87` there. `put_reused_structure` (immediate `1e`, the vector with a descriptor): `31e8` reads `[MAR1]` and tests VDESC, `31ec` is the other row. ODPF 4 and 6 (`get_atom`, `switch_on_non_list`) keep `S_ENTRY`; since the sixth session ODPF 6 takes `S_OTHER_ROW` for another tag held directly, and other cases raise. Injections (observed): `odpf3_entry` (always the entry): append STOPs at `31e9` (ALU input from a read never written), 4 of 16, both reuse cases at `31e8`; `odpf3_bits10`: append STOPs at `31a3` (case_branch with no set-up), both reuse cases at `31e9` |
| `RULES['em1_29_mrb']`: CNDF 7 with EM1 `29` forms COND := the MRB (tag bit 0) of the AS1 input is ON | INFERRED | `31ec`-`31ed` | the contract: a structure whose pointer has its MRB on is shared and must not be reused in place; MRB off, it is reused (TR-466 4.2, printed p.7; thesis printed p.138, Fig. 3-23: the S stage tells E whether the data is collectable). `31ed` ends when COND is false (`j1_bit0_false`); else `31ee` calls `31a1` and `31f0` jumps to `put_list` (allocation). `pu_smt` side contract `reuse_kl1` (31ec-31ed, MDR1 LISTo or LISTx; `docs/pu_microcode_inference.md` 6): every value relation, never and always eliminated; mrb_on and mrb_off survive, coupled to the end polarity; under the adopted one mrb_on only. Static: `0ac9`-`0acb`, `0ace`-`0ad0` form it from MDR2 alone and stamp EHOOKo/x or EUNDFo/x by it. Not decided: whether the S stage's chain report (SRP) takes part (append's list is held directly, no REF: the two agree). Side cases in `u2_append.py`: 3,0,2 on LISTo reused (ok), 0,0,2 on LISTx goes on to `31ee` (pinned `REUSE_SHARED_STOP`: R04, pc, never set). Injection `em1_29_off`: append STOPs at `31ee`, 4 of 16; the LISTx case FAILs (ended at `31ed`: a shared list reused) |
| `RULES['sc2f1_ir']`: SC2F 1 (WRBF clear) puts an IR field on S2, the low 16 bits sign-extended, tag 0; not a register R01 | INFERRED; width NOT discriminated | `31ec` | thesis printed p.129: the S1 bus reaches every register except IR, the S2 bus RF, WR and IR, and IR has field extraction (rassy: `ir/8`, `ir/16`, `ir/24`, signed forms). Static: 46 words read select 1 through SC2F; the 8 label words `32f0`-`32ff` add it to R04 (pc) and jump to the label branch `2447` (`pimm.py`: pc + 2 + sx16(c16)); `wait_vector` (`3a03`, `3a06`, `3a0b`) subtracts it from the vector's length (`pimm.py`: c16). (rassy's second bank, 1 `sr` ... 5 `ir`, names SC1F-side registers; its numbering of S2 sources is not recovered.) `put_reused_structure` is `r_r_c8`: where y is not 0 the c8 and c16 readings differ and the read raises (`setup.IR_C8`). On the path run the value is loaded into MDR2 and not used. Injection `sc2f1_reg` (read as R01): STOP at `31ec` (R01 never set) |
| `get_bound_value`'s set-up (`setup.FORMS`, `S_CONST`): the S-stage test on A[x] (immediate UNDF, `S_ENTRY`), MDR2 := A[y] | OURS, with support | `3880` | `pimm.py` `i_get_bound_value` unifies reg[x] with reg[y]; OS1F 3 is the thesis's (3) "the RF entry named by r0-r3" (printed p.128; not fitted: `get_atom` has OS1F 1). `3880` = `3800`-`3801` without the stamp. Injections: `gbv_mdr2_x` (MDR2 := A[x]): FAIL at instruction 7 (the cell bound to a REF to itself); `s_no_mar1` now FAILs append there too, `s_imm_plus1` STOPs append at `3881` (zero word): append now discriminates `S_ENTRY`'s start and MAR1 |
| `put_reused_structure`'s operand y (`setup.FORMS`) | OURS (`pimm.py`'s reading) | `31ec` | append's 0,0,2 cannot tell y from x; the side case 3,0,2 does: injection `prs_operand_x` FAILs it (A3 and R02 = A3's old `{INT, 9}`), append passes |
| `pu.FLAG_CONDS`: CNDF 7 with EM1 `19` is COND := the slit-check flag, EM1 `21` the interrupt_all flag | INFERRED (DOCUMENTED that CNDF 7's EM1 selects a rare condition: thesis printed p.144) | `4cc0`, `4cc2` | the numbering is `rassy`'s 40 condition constants in the order the class holds them (`ptfdump.py pimmutil rassy`: `cond alf_zero` .. `cond ovf_trap`), EM1 = the position; since the sixth session HELD-SOURCE: `cndf/7`'s arm 7 calls `cndf_others/5` (@3321), a hash switch on EM1 whose key k takes pool slot `00dc` + k (k = `00`..`27`). Three checks fit it: position 9 is `over_flow` and 10 `less`, where EM1 `09` (overflow) and `0a` (lt) were found apart from rassy (pu_smt); positions 21-31 (`exsw00` .. `COL`) carry the numbers rassy's own flag set/reset tables give those flags (`--pairs`: `set_slit_check` 25, ... `set_COL` 31). So `19` = 25 = `slit_check`, `21` = 33 = `interrupt_all` (rassy's keys). Slit check: events (GC request, packet arrival, other PEs' signals) latched in flags and polled once per reduction (`docs/literature_gaps.md` [P1] s.5.4; TR-715 3.3 for PIM/m, `docs/multi_pe.md`). Static: 37 EM1-`19` words, many with no ALU operation (a flag, not an ALU relation). The flags' values are OURS (`u2_append.EXECUTE_FLAGS`, both clear; an unset flag raises). pu_smt `execute_fast`: under 'prev', the condition `4cc0` forms must be `never` for every register content (data-independent). Injections: `slit_pending` STOPs at `4cc5`, `interrupt_pending` at `1c2c` (via `4cc4`, `4cd3`); `flags_swapped` changes nothing: which flag is which is NOT discriminated |
| `RULES['cjump_time']` = 'prev' with `pu.CJUMP_TAKEN_ON` {b: taken on COND} | INFERRED | `4cc1` | a conditional JMPF a/b/c/e tests the COND the previous executed word formed: thesis printed p.130 (condition into COND one step, branch the next, DOCUMENTED); the ends' 'prev' (EXECUTED, pu_smt); at `4cc1` (which forms CNDF 3 itself) 'same' would leave `4cc0`'s slit check untested on every path; static census of non-self conditional jumps, own CNDF / only the word before has one: b 4 / 27, a 51 / 97, c 23 / 123, e 45 / 94. pu_smt side contract `execute_fast` (no event: `4cc1` not taken for any register content), with the decided datapath fixed: with CNDF 3 = lt only ctime 'prev' survives (pinned). Polarity: b only (taken on COND: the fast path `4cc2`-`4cc3` sets R04 := the label); a, c, e raise. Injections: `cjump_same` STOPs at `4cc1` (its own COND is STALE), `cjump_false` STOPs at `4cc5` |
| `RULES['as1f2_yr']`: AS1F 2 is YR (as it stood before the word) | INFERRED | `4cc0` | AS1F is in SD1F's numbering (MEASURED), whose 2 is `yr` in rassy's adder-source table; thesis printed p.126: XR, YR, MDR1/2 reach AS1. Static: 446 words AS1F 2 / AS2F 0, 157 of them ALF 3 operations on it alone. R15 := YR is not compared. Injection `as1f2_off`: STOP at `4cc0` |
| `RULES['cnd3_sign']`: CNDF 3 = the ALU result is negative | INFERRED, NOT discriminated | `4cc1` | rassy's short condition table in the class's order `carry, zero, sign, same_tag, equal, lc_one` read as CNDF 1-6: 2 (zero, decided at `204f`), 5 (eq, pu_smt) and 6 (the lc loops) fit. At `4cc1` its input is STALE and nothing tests it; `cnd3_off` changes nothing |
| `RULES['jmpf8_flag']`: JMPF 8 sequences as JMPF 0 in a word whose CNDF 7 is a flag condition | INFERRED, admitted only there | `4cc2` | as `jmpf8_setup`; what bit 26 adds is not decided. Injection `jmpf8_flag_off`: STOP at `4cc2` |
| `pu.MCF_UNKNOWN` {06, 07}: MCF with these EM1 is an operation of UNKNOWN meaning on state not held here; recorded in the cycle record (`mcf`), no register or memory changed | INFERRED (that nothing run here reads it) | `4cc1` (07), `4cc3` (06) | thesis printed p.144: MCF is counter/flag control. 06: 75 words, 59 in words that put a freed cell on R19 (wait_*, switch_on_*, `3309`), 4 at execute's ends; 07: 11 words, all at goal or reduction boundaries (proceed `2170`/`217a`/`2212`, execute, execute_external, suspend, merge, the boot `20a8`); rassy's reset table numbers 6 reset_SUSPF and 7 reset_CGCF: not decided. Injection `mcf_unknown_raise`: STOP at `4cc1` |
| `execute`'s set-up (`setup.FORMS` 'label_mdr2'): MDR2 := pc + 2 + c16, no tag | OURS, with support | `4cc2` | `pimm.py`'s `i_execute`; nano-code OS1F 2 (the thesis's (2) "an operand field", printed p.128) and ODSF 2 (MDR2, as for collect_list); the held words use MDR2 as the code address (`4cc2`, `4ccf`, `4cd3`). Injection `execute_mdr1`: FAIL at execute (R04 = MDR2's old value) |
| `pu.STALE` and `u2_append.seed_execute`: R0d, W1f (and, until the sixth session, R04) hold values the harness does not know (STALE) before execute; a STALE value may be copied and pass the ALU (result and COND STALE), but a test, a memory write, an address or a comparison with `pimm.py` STOPs or FAILs | OURS | `4cc0`-`4cc3` | R0d is a scratch register (47 writers, none run before), W1f is written at boot (`20a8` W1f := 0) and by proceed, R04 (rassy's `pc`) is the A stage's. That the run reaches its end with them STALE shows their values do not matter on the fast path; `tgif3_em1` FAILs execute (R04 tag `21`) |
| `u2_append.A_STAGE_R04`: while an instruction is in E, R04 (rassy's `pc`) is `{COD, pc + 1}`, given by the harness before each instruction; `compare_next_pc`: a firmware that changed R04 branched there (must be `pimm.py`'s next instruction), else it falls through to pc + 1 | OURS, with support | `3310`, `2461` | the label branch adds c16 to R04 and then 1 (`2447` YR := #1, `2461` R04 := XR + YR) where `pimm.py`'s target is pc + 2 + c16; `switch_on_constant`'s rows `2420`, `242c`, `243c` read the instruction's second cell at [R04] (`pimm.py` `cells[pc + 1]`). Injection `r04_pc` (R04 = pc): FAIL at 12 (the label - 1), and the VECT0o case |
| `RULES['jmpf2_case']`: JMPF 2 is a case_branch, target (upc + EM3, signed as JMPF 4) \| TDAR | INFERRED (kind HELD-SOURCE) | `2447` | rassy's jmpf table (`ptfdump.py pimmutil rassy --list`, `jmpf/9` @2a5c, a switch on the JMPF value): arm 2 'base' 'case_branch' formatted by `short/3`, as arm 4 (goto, JMPF 4); arm 3 'base' 'case_branch' by `long/4` (S8). MEASURED: 15 of the 16 JMPF 2 words of image 2 put upc + EM3 on a 16-word boundary (all but `0207`): `2447` -> `2440`, `2455` -> `2450`, `31a1` -> `31a0` (also `31a3`'s base), `2401`, `2425`, `2437`, `323c`, `327c`, `32bd`, `34bf`, `4192`, `0d9c`, `0105`, `0107`, `0205`. Unsigned gives the same count, but `2450`'s rows do not write R04: injection `jmpf2_unsigned` FAILs (no branch); `jmpf2_off` STOPs at `2447` |
| `setup.S_OTHER_ROW`: an ODPF 6 entry whose dereferenced operand's tag is not the immediate's (MRB ignored), held directly with its MRB off, starts at entry \| 4 << 2 (chain code 0); other chains raise | INFERRED (mechanism DOCUMENTED, thesis pp.134-138) | `3310` | the 32 words behind `switch_on_non_list` (`3300`) are 8 rows of 4, rows 4-7 all the label computation; `switch_on_non_integer` / `_atom` (`32e0` / `32e2`) interleave the same rows (`32f0`-`32fe` the label). Row 0 for a directly held operand is the entry (`S_ENTRY`), so chain code 0 is that operand; rows 1-3 (a marked list, a freed variable cell, both) read, not run. TGT column TDPF by the tag (`s_imm_row`) sends LISTo to row 2. Injection `other_row_entry` (every tag at the entry): FAIL at 12 (nil taken for a list, a cell freed) |
| `setup.S_TDAR`: the S stage loads TDAR with the TGT byte of the dereferenced operand's tag from column 7 - TDPF | INFERRED (mechanism DOCUMENTED, thesis printed p.134 (2) and Fig. 3-22's TDPF) | `2447` | table shapes (image 2): TDPF 4 (`switch_on_non_vector`, `2400`) column 3, VECT1..6 = 8..18 on the six rows `2408`-`2412` that differ only in EM1 1..6; TDPF 2 (`write_marked_value` `3240`, `put_marked_value` `3280`) column 5 byte for byte (INTx 4 .. VECT0x 7 re-stamped o at `3244`-`3247`); TDPF 0 (`switch_on_constant` `2420`, `hash_on_constant` `2430`, the label branch `2440`) column 7: constants 0, structures 2, UNDF 4, hooks 6, EXREF 8, MGHOK/EXMRF 10 (those four to `24b1`), REF and the rest 12. Cross-check, HELD-SOURCE: rassy names CNDF 7 EM1 `3a` `case_tag_setup mdr1 5` and it is the column-2 set-up VERIFIED at `2d3e`, so `case_tag_setup` k reads column 7 - k too. Injections: `tdar_col_tdpf` STOPs at `2444` (MRP); `tdar_col6` passes append (ATOMo 0 in both) and only the side case `switch_label_case` ({VECT0o, 0}: 6 in column 6) STOPs at `2446` |
| `setup.S_MDR2_OWN`: the S stage leaves the operand as it was before the dereference in MDR2 (ODSF 2) | OURS, with support | `3310` | the free-a-cell rows put MDR2 on the R19 list (`3309` R19 := MDR2, [MAR1] := the old head): the REF the dereference went through; `3310` tests it for REFo. Injection `mdr2_own_off`: append passes (the old MDR2 is not a REFo either); the VECT0o case STOPs at `3310`: that MDR2 is loaded is discriminated, its value (the operand before the dereference) NOT |
| `CJUMP_TAKEN_ON` a: on COND, e: on not COND (b: on COND, as before) | HELD-SOURCE (the polarity); INFERRED that rassy reads the field as the hardware does | `2440`, `2461` (e), `3980` (a) | rassy's `jmpf/9` arms 8-f each take one more pool constant through a relative `pmi 49` operand; resolved, arms 8-f land on slots `00af`-`00b6`: `00af`-`00b2` 'if cond', `00b3`-`00b6` [if, [not, cond]] (one slot each; `jmpf/10` on `00b7`-`00be`), so 8-b are taken if cond and c-f if not. Joint: e's polarity, `S_MDR2_OWN` and COL are tied in append (`e_mdr2_col`, all three flipped: e on COND, MDR2 a REFo, COL true, passes 14 of 16 and the VECT0o case); rassy breaks the tie. Injections `e_on_true`: FAIL at 12 (`2441`-`2445` write [MAR1]); `a_on_false`: FAIL at 13 (`3981` writes [MAR1]). The same table makes b "call long if cond": adopted in the seventh session (`RULES['jmpf_b_call']`, below), the S7 conflict decided. (`e_mdr2_col` passes 15 of 16 since then: the tie stands through `get_value`.) |
| `RULES['em2_mrb']`: ALF 2/3 with EM2 20 = MRB off, 30 = MRB on (the AS1 input with tag bit 0 cleared / set) | INFERRED (names HELD-SOURCE) | `2447` | rassy's `special_operation/4` (@3030, a switch on EM2): 0 '+' .. 15 shift_right_arithmetic, 32 'mrb_off', 48 'mrb_on'. The rows agree: `32e4`/`32ec` (an integer or atom marked) clear the MRB where the list rows `3304`/`330c` stamp LISTx. Injection `mrb_swapped`: FAIL at 12 (A0 := `{ATOMx, 0}`) |
| `FLAG_CONDS` 1e MRP, 1f COL; `setup.S_REPORTS_DIRECT` COL false for an operand held directly | INFERRED (names HELD-SOURCE: rassy `cndf_others` keys 1e, 1f; the flag tables' set_/reset_MRP 30, _COL 31); the value OURS | `2440`, `2461` | thesis printed p.138 Fig. 3-23: the S stage's dereference reports two chain bits (every MRB off; the first two pointers' MRBs off) to E. With no pointer followed there is nothing to collect. Injection `col_true`: FAIL at 12 (`2462`, `247b`-`2480` put a cell on the R19 list) |
| `MCF_NAMED` 08 = pipeline_cancel, recorded only | INFERRED (rassy's flag-control table, position 8, between reset_CGCF 7 and set_cc 9) | `2461` | the MCF 08 words load R04 (`2453`, `245d`, `2461`, `31ee`, `2035`): a branch discards the prefetched instructions; this simulator has no pipeline. Injection `mcf08_raise`: STOP at `2461` |
| `RULES['cnd8_s1']`: CNDF 8 / a: the S1-bus value's tag == EM1 / EM2; CNDF c: the same with the MRB ignored | INFERRED (HELD-SOURCE arms, MEASURED source) | `38b0` (8), `38b2` (c) | rassy's `cndf/7`: arms 8, 9 'tag =' EM1, a, b 'tag =' EM2, c, d 'tag / 5 =' EM1, 8/a/c on one operand and 9/b/d on the other. Census: all 217 CNDF 8 and 20 CNDF a words read an S1 source (114 / 9 for the condition alone), every CNDF 9 / b / d word has an ALU input; CNDF c's 100 EM1 are all 'o' tags. Needed to reach `0c0c`, NOT discriminated (no comparison before the stop): `cnd8_off` STOPs at `38b0` |
| `RULES['sd1_pairs']`: SD1F 2 = MDR1 and MAR1, 3 = MDR2 and MAR2 | INFERRED (HELD-SOURCE; DOCUMENTED that such codes exist) | `38b2` | rassy's `sd1f/2` (@2959): 2 ', mdr1 mar1', 3 ', mdr2 mar2'; thesis printed p.144: "codes include writing the same value to MAR1+MDR1 and MAR2+MDR2". Not discriminated: `sd1_pairs_off` STOPs at `38b2` |
| `RULES['jmpf9_call_if']`: JMPF 9 is a call taken if cond; only the arm not taken is modelled | INFERRED (HELD-SOURCE) | `38b1` | rassy `jmpf/9` arm 9 'call' with em1_not_free and em2_not_free and 'if cond'. The target (EM absolute or mekbn's JMPF 1 reading) is not decided: taken, it raises (`s_imm_row`'s get_atom now stops there, `3811`). `jmpf9_off` STOPs at `38b1` |
| `wait_nil`, `get_value` set-up (`setup.FORMS`): the S-stage test on x | OURS (`pimm.py`'s operand readings) | `3980`, `38b0` | `get_value`'s row 0 (x unbound) loads A[y] into MDR2 and MAR2 (`38a0`, SD1F 3) to bind it with |
| `pu.CASE_TAG_SETUP`: CNDF 7 with EM1 `30`-`3f` is `case_tag_setup mdrN k` (EM1 even MDR1, odd MDR2, k = (EM1 - `30`) >> 1): TDAR := the TGT byte of that MDR's tag (old value), column 7 - k | INFERRED (names HELD-SOURCE: rassy `cndf_others/5` keys `30`-`3f`, slots `0106`-`0115`; column: `3a` = mdr1 5 is column 2, VERIFIED at `2d3e`) | `0c0c`, `0e38`, `0c0d`, `0840` | MEASURED (168 words): CCF bit 58 goes with mdr1 (69 of 103), bit 59 with mdr2 (49 of 62, 4 mdr1). Shapes met: `0c0c` column 0 (REFo `0e38`, REFx `0e3b`, the rest call the trap `6c21`: the routine is called for a REF only); `0e38` column 5 (20 rows `0e60`-`0e73`, UNDF 18 -> `0e72`, a return; bound atomic values free the cell, `0e62`); `0c0d` column 6, `0840` column 7. The old rule (the AS1 input's tag, `TGT_COLUMN`) gives the same at `2d3e` (`check_pu.py` unchanged). Injections: `cts_as1` STOPs at `0c15` (no set-up), `cts_col_k` at `0c15` (REFo 12 overlaps `0e38`), `cts_mdr_swapped` at `6c21` (the trap) |
| `RULES['jmpf_b_call']`: JMPF b is a page-relative call taken if cond | INFERRED (kind HELD-SOURCE: rassy `jmpf/9` arm b 'call' long 'if cond'); decides `docs/pu_microcode_inference.md` S7's conflict | `0c0c` (taken), `4cc1` (not taken) | the twins `0c0f`, `0c12` (JMPF 7, the same word otherwise) call `0c15`; every row behind it returns. MEASURED (scratch census of image 2, the words reachable from each target before a return or an end, calls taken as returning): JMPF b 47 targets, 38 only returns, 9 both, 0 only ends; JMPF 7 144 / 42 / 4, f 24 / 6 / 0; page jumps JMPF 6 338 / 185 / 510, e 130 / 15 / 218. `4cc1`'s slit path has a conditional return at `4cd2` into `4cc2`. Injection `jmpf_b_jump` (mekbn's page jump): STOP at `0e72` (return with an empty micro stack); `cjump_false` / `slit_pending` now call `4cc5` and STOP at `4cc6` (JMPF c polarity) |
| `RULES['case_wide']`: a JMPF 3 case_branch ORs the whole TGT byte when the base's low bits are free of it | INFERRED | `0e75` | base `0e60`, column 5's 0..19 on 20 rows `0e60`-`0e73` (S8's "low 4 bits" was the `2d3f` / `31a3` tables'). Injection `case_4bit`: STOP at `0e75` (UNDF 18) |
| `RULES['tdar_holds']`: TDAR stands from its set-up across JMPF 1 words to a later case_branch | INFERRED (rassy names `tdar` among the registers) | `0802` | the twins `0c0d` -> `0c0e` -> `0802`, `0c10` -> `0c11` -> `0800`, `0c13` -> `0c14` -> `0801` all set up two words before the JMPF 3, a JMPF 1 jump between. Injection `tdar_one_word`: STOP at `0802` |
| `pu.MCF_FLAG_OPS`, `FLAG_CONDS` `10`-`12`: MCF EM1 `03`/`04`/`05` reset sw00/sw01/sw02, `0b`/`0c`/`0d` set them; CNDF 7 EM1 `10`-`12` reads them | INFERRED (names HELD-SOURCE: rassy `mc1/2` @355b, `mc2/3` @357b; EM1 = mc1 key << 4 \| mc2 key) | `0e75` (04), `0864` (`11`) | rassy's mc1 keys 1/2/3 are '-- lc', '++ gr', '++ sr' (slots `0116`-`0118`), and two rules decided apart fit EM1 = key << 4: MCF `20` = R02 + 1 (`mcf_20_sp`; rassy's bank names 2 `gr`) and `10` beside CNDF 6 in the counted loops (lc). So `08` = pipeline_cancel, `06` reset_SUSPF, `07` reset_CGCF (kept recorded-only). Static: sw01 is set by the dereference rows that follow a REF with its MRB on (`0e3b`, `0e61`, `0e63`, MCF `0c`) and reset at the REFo start (`0e75`); `09d0` ends when it is clear, else `09d1` rewrites the binding with the MRB on: the variable reached through a shared pointer. Injection `sw01_set`: FAIL at 14 (the cell `{ATOMx, 0}`, `pimm.py` `{ATOMo, 0}`) |
| `pu.ALF_CONDS`, `MCF_NAMED` `01` set_alf; `RULES['as1f3_open_unknown']`: AS1F 3 with AS2F not 0 gives an UNKNOWN result (raises if written); a COND or latch from it is POISON | names HELD-SOURCE (rassy positions 0-8 `alf_zero` .. `alf_less_zero`; mc2 key 1); the rest OURS | `0802`, `0841` | `0802`'s EM bits are the JMPF 3 base, so `as1f3_em2` does not apply; its CNDF 5 and set_alf feed only `0841`'s alf_equal, and `0864` forms a new COND before any test: NOT discriminated. Injection `as1f3_open_raise`: STOP at `0802` |
| `setup.S_MAR1_DIRECT_STALE`: for an ODPF 6 entry whose operand is held directly, MAR1 is STALE | OURS | `0c0c` | W1d := MAR1 and XR := W1d copy it and nothing reads them on the path. It turns old injections' writes through MAR1 into STOPs (`u2_append.py` header). Injection `s_mar1_kept` (the old carried value): append passes, 15 of 16: not used, as claimed |

`check_pu.py` still passes unchanged with these rules (32 cases, 80
words: the CNDF 2 rule, the bit-0-clear polarity and the 2026-11-27
rules meet no U1 word; nor do the fourth session's ODPF 3 start, EM1
`29` and SC2F 1 rules, nor the fifth session's flag conditions, timing,
AS1F 2, CNDF 3 and MCF rules, nor the sixth session's JMPF 2 / 9, a / e
polarity, CNDF 8 / a / c, SD1F 2 / 3, MRB, MRP / COL and MCF 08 rules
(re-run 2026-11-27 sixth session: same output for every case and every
injection), and `check_pu.py`'s 8 injections give the
same counts as in "Fault injections"; its step contract now expects the
record's `mcf` key).

**The boot.** `start` (`2028`, entry `37b`) is the KL1 firmware's
initialisation, called from outside: `204b` (heap top into R1f), `2053`
(calls the refill entries `3376`, `337b`, `3380`, `3382`-`3395` for every
free list, and `2070`-`208d`, read not run, reads parameter pairs at
`1a0 + aa`..`b2`: unexplained), `209f` (with `20bc` R07 := 0: held evidence for the
`zero_regs` rule's R07, read not run), `20c2`, `20e7`, then R0e and R10.
`execute_first_predicate` (`2032`) loads R04 (`pc`) with
`{REFo, [1a0 + 4b]}`, PIMM.PARAM's `bmadr` "Boot Module Address" by its
place (INFERRED); it stops at `2035` on MCF with EM1 08. Only `204b` is
run. The parameter cells are outside values (PIMM.PARAM, loaded by the
KL0 side): OURS.

**Never-set registers, a census** (image 2 below `6800`, reads / writes):
R05 549 / 14, W0d 82 / 4 (`0d93`, `21e4`, `42ac`, `4c61`: save/restore-
like sequences, not boot), R07 44 / 1 (`20bc`, in `start`), R06 118 / 12.
R05 is read as a base (`1a0 + R05`, `{INTo, R05}` where 0 belongs) and
no routine of `start` writes it: probably a constant or hardware source,
like R06/R07; not settled.

**`read_variable` (`34a0`-`34a2`, `3494`), run.** The entry has no tag
immediate (EMO2 `0d` is start-address bits, not a tag), so it is not
an S-stage tag test. Nano-code ACF 0, DFF 2, OS1F 6, ODSF 3, TDPF 0,
EMO1 9. `34a0` MAR2 := R02, MDR2 := R19, MDR1 := [MAR1] (the element),
CNDF 7 EM1 `28` (a condition, UNKNOWN); `34a1` MAR1, W1d := MDR1, the
dereference set-up (CNDF 7 EM1 `2d`, JMPF 8); `34a2` R19 := {VECT0x,
MDR2}, MDR1 := [MAR1], case_branch `3490` | code << 2; for anything
not a REF and not the immediate, `3494`: x := MAR1 (the element), MDR2
:= [MAR2++], MCF EM1 20 (R02 + 1), end. The element is taken as it is,
with no MRB marking: `pimm.py` takes it unmarked only when the structure
was reached with every MRB off (`sp_single`); append's list is, and its
elements are atoms, which `pimm.py` never marks. Where the firmware
marks an element of a shared structure is not found (EM1 `28` is a
candidate: a condition formed and, on this path, not tested).
`read_variable_without_deref` (`345a`-`345c`) writes `opd9` (x) from
`[MAR1]` and branches (JMPF a, conditional: `cjump_time`) into the
MRB-marking `case_branch` at `35c0`. Not run.

**`cjump_time`** (the timing of conditional a/b/c/e): 'prev' since the
fifth session, decided at `4cc1` (the rules table above). Polarity
executed for b (`4cc1`, not taken; `0c0c`, taken, a call since the
seventh session), e (`2440`, `2461`, taken on a false
COND) and a (`3980`, taken on a true one), rassy's 'if cond' / 'if not
cond' (sixth session); c raises. Untested: c, and
the boot's fill loop `209b`-`209e` (a counted loop: which count it
fills under 'prev' needs the loop counter's MCF EM1 10 and CNDF 6).

**The S12 row entry**, decided in the sixth session (the rules table
above, `setup.S_OTHER_ROW`, `S_TDAR`): the fifth session's lead (TGT
column 0 picks the row) is not adopted. Two mechanisms are at work, as
the thesis's (2) and (3) (printed p.134): the start row is the match
bit and a 2-bit chain code (rows 4-7 the other tags, row 4 an operand
held directly), and the TGT byte goes to TDAR for a later case_branch,
from column 7 - TDPF (column 7 for TDPF 0, not column 0). Column 0
(REFo 0, LISTx 1, LISTo 2, REFx 3, other 4) is not met. Rows 1-3 of
the immediate's side (a marked list `3304`, a freed variable cell
`3308`-`3309`, both and `247b` at `330c`) and rows 5-7 are read, not
run, and raise.

## Next, for U2

`proceed` (instruction 15, the last) is where append stops, at `216c`
(read of R1b, never set), and it is not run here for a reason, not for
want of a rule. Its routine is the goal scheduler: `216c`-`216d` push the
finished goal's record (MAR1 = R10, NANO_ODPF1) on R1b's list (rassy's
`fgp`, the goal-record free list), `216d` takes XR := R14 (the next goal
in the ready queue) and forms R15 := `as1_2 - YR` with set_alf in the
word that also loads YR := R0d; `216e` R10 := the next goal; `216f`
branches on the latched alf_zero, then on R14's tag against ATOMo (an
empty queue, INFERRED from that test); the empty-queue arm `217a`-`217b`
(CNDF a, MCF 07 reset_CGCF, a JMPF 9 to `21b2`) and `217c` (CNDF 7 EM1
`1a`, PMPF) lead into the idle path. Three things block a real
comparison. (1) No observable: `pimm.py`'s `i_proceed` is `chain += 1`
and the event `E done`, no R or M line, and as the last instruction it
has no next PC; its run loop, not the machine, picks the next goal, and
the goal records and the ready queue R14 exist only in the firmware (the
goal switch is OURS). An "ok" would be vacuous. (2) State the harness
would have to invent: R1b, R14 (the queue's empty form), R0d and R15
(priorities, by their use at `4cc0`-`4cc5`: INFERENCE). A probe in the
session scratchpad, R1b and R14 seeded (OURS), runs `216c`-`216e` and
stops at `216f`, whose branch tests alf_zero: POISON. (3) That alf_zero
is latched from `as1_2 - YR` in a word that loads YR itself. Under the
adopted ALU timing (`as1f2_yr`: YR as it stood before the word, on both
inputs) the difference is 0 for every input. So either the AS2 input
sees the S2-bus load of the same word, or AS1F 2 is not YR there. That
is a timing question for the datapath, not for proceed. A U2 that ends
at 16 of 16 needs a `pimm.py` (or a scheduler model) that exposes the
goal queue, and that question decided.

So U2 stands at 15 of 16 with every KL1-B instruction of the clause
bodies matched. What was left open on the path run:

- `0802`: AS1F 3 with AS2F 2 (`as1_3 - MDR1`), source UNKNOWN; its
  CNDF 5 and set_alf feed only `0841`'s alf_equal (POISON, overwritten at
  `0864`). The atomic-against-atomic rows (`0860`, end if alf_equal)
  would test it.
- `0c0c`'s W1d := MAR1 and `0c0d`'s XR := W1d (MAR1 STALE for an operand
  held directly): dead on this path. The twins `0c10` / `0c13` restore
  MAR1 from W1d, which is where it matters (`38ae` / `38af` callers).
- MCF `06` / `07` are now named by rassy's `mc2` (reset_SUSPF /
  reset_CGCF), still recorded only.
- The candidate EM1 values met earlier: `0d` = 13 `lc_zero` (at `1c2c`,
  on the interrupt path).

`execute`'s other paths, read, not run: the slit-check path `4cc5`-`4cd2`
(needs AS1F 3 with AS2F 1, `as1_3 shift_left YR`; EM3 is 1 at `4cc5`:
1 << R0d, a priority bit, INFERENCE) and the interrupt path `4cc4`
(R04 := the old pc), `4cd3` (W10 := `{COD, label}`, call `4cf4`),
`4cd4` (jump `4c11`, the goal switch: R10's goal records).

The lead written before this session, corrected by reading
`31e8`-`31ff`: the 16 words before `put_vector_N[00]` are NOT four
4-word rows. Only `31e8` (the immediate, a vector with a descriptor:
`[MAR1]` read and tested for VDESC) and `31ec` (every other tag) are
start rows (`setup.ODPF3_SHIFT`); `31ee`'s call to `31a1` returns into
`31ef`, and `31f0`-`31f2` and `31f4`-`31f7` are continuations (`31f4`
uses YR and MDR2 set by earlier words). Off append's path, read, not
run: the allocating arm (`31ee` XR := R04, MDR2 := n - 1, call `31a1`
(R04 := XR, a 4-bit JMPF 2); `31ef` R02 := MDR1; `31f0` a JMPF 9 to
`put_list`), the descriptor row (`31e9` -> `31f3`, the n from IR, `31f4`
the case_branch `31a3` on base `31a0`: `31a4` pops R1a's list, `31a8`
R19's). `get_atom`'s 4-word rows (`3800` UNDF via MRB off, `3804` via
MRB on, `3808`/`380c` HOOK, `3810`.. compares) are an ODPF 4 layout,
still raised for any tag but the immediate.

Then the boot beyond `204b` (the refill and list builders: MCF EM1 10
and CNDF 6, the counted loop; CCF as a coded field) to drop the seeded
lists. The other dereference set-ups (EM1 `2a`, `2b`, `2f`) and the REF
/ immediate rows of `2d` are read, not run; EM1 `28` (`read_variable`'s
`34a0`) is still a condition of UNKNOWN meaning (its sibling `29` is
now the MRB test; the S stage's SRP/COL reports, Fig. 3-23, and rassy's
condition names MRP and COL are candidates, not tested).
