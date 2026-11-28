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
    python3 ref/pu/u3_goals.py [-v]       U3: a multi-goal program, the boot and the scheduler held (in run_tests.sh, ~3 s)
    python3 ref/pu/u3_goals.py --inject NAME

The microcode is third-party and stays out of git: it is read from
`docs/nonlocal/psdpim.tar.Z` at run time, as `asm/psdpim.py` reads it.
Nothing here prints or stores image words except under `-v`, to the
terminal.

## State (2026-11-27)

**U1 reached; U2 not reached** (furthest point 15 of 16 instructions of
append: the second reduction's `get_value` runs the general unifier
whole, 16 words; the stop is `proceed`, the last instruction: section
"U2" below). **U3's first step reached** (2026-11-27, section "U3"): a
multi-goal program whose goal queue is made by the firmware's own
`enqueue_goal` and taken by its own `proceed`, 41 of 41 instructions
matched, 3 scheduler picks compared with `pimm.py` (2 dispatching, 1
empty), no mismatch. **U3's second step** (2026-11-27, section "U3, second
step"): the scheduler state is written by start's own boot words (199
held words) instead of the `INITIAL` stand-in, 41 of 41 matched, 2 picks
compared with `pimm.py` and the third the boot goal's (firmware only), no
harness-written state read at any pick. **Append's 16th instruction is
counted here, 16 of 16** (owner decision, 2026-11-28): in append2 the
first append goal, `try_me_else` .. `proceed`, matches `pimm.py` whole,
and the proceed's pick (pick 2) reads only state the held words wrote
after the 199-word held boot (the provenance walk;
`u3_goals.APPEND16_PINNED`). Still OURS for that count: the driver clause,
the boot entry choice (`2021`, reset_PMPF), and the parameter cell values
b4 (sspb), b6 (gseb) and b7 (gsesh). `reseed_r14` fails the pin (FAIL at
8, provenance), and so does `r13_harness`, on provenance alone (16 of 16
still match, pick 2 reads R13). The standalone `u2_append` run stays at
15 of 16, because it seeds the scheduler (why: "U3"). **U3's third step** (2026-11-28, section "U3, third
step"): suspend and resume on held routines. In a second program a goal
suspends on an unbound variable, another binds it and wakes it, and it
runs to its end: 22 of 23 instructions matched with 1 declared skip, and
4 picks, 3 compared with `pimm.py`. **U3d's first step** (2026-11-28,
section "U3d, first step"): a program compiled by the held PIMOS
compiler (a producer and two consumers of one stream) runs to its
answer, `pimm.py`'s: 64 of 68 instructions matched with 4 declared
skips, 5 picks (4 compared), 2 suspends on one variable and one bind
waking both.

- 32 cases, all PASS (83 held microinstructions executed since U3; 80 before). The 32nd
  is a held `case_branch` (`2d3e` set-up, `2d3f` JMPF 3: tags 08/0a/04
  land on `2d40`/`2d43`/`2d4e`, base | the `5300` column-2 byte). Since the
  first 28: a held call word (`scsi_init`'s `615e` calls `3320`; the
  return lands on `615f`), the refill with an HP given (stops at `3367`
  since U3, at `3365` on "W0d" before), and the step contract (evaluate twice gives equal records and
  changes nothing; commit returns `next`). Every compared case enters
  through decode-table dispatch from the instruction cell
  (`setup.dispatch`). Of the first 28 (69 words): 22 compared
  against `pimm.py` (44 executed and matched: 33 in multi-word
  routines, 11 in one-word ones); 4 that take the last cell of a free
  list and must enter the refill (17 words executed up to the refill,
  where they stop, as they should); and the one-cell allocator `3320`
  called as a microsubroutine (EXECUTED, 4 words: W1c = `{REF, cell}`,
  the cell `UNDF 0` as `pimm.py`'s `new_var` makes it, R19 left holding
  the link, one memory write; its last-cell arm runs into the refill and
  stops there (at `3367` since U3, `3365` on "W0d" before), as it should; R05 there is the EM1 immediate,
  `pu.S1_IMM`). `measure.py`'s pins (the counts behind the rules) are
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
*U3 (2026-11-27):* "W0d" is read as R(10 | EM1) = R1f there
(`RULES['wsel_d_em1']`), and CCF is rassy's table (`RULES['ccf_rassy']`,
16 = write_stack ++ mar1 MDR1, the conflict resolved by HELD-SOURCE): the
refill now runs `3365`-`3366` (MAR1 := R1f) and stops at `3367`, whose
word both loads MAR1 and steps it (not modelled). Section "U3".

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
eighth session (2026-11-27) read the datapath from rassy's own tables
(the ALU sources, the constant, the EM immediates, `ext_ir`) and ran
`proceed`'s routine whole in 15 side cases against `pimm.py`'s `pick`
("Next, for U2"): the next goal's code, arguments, record and queue
match; append itself stays at 15 of 16, with the reason given there.
The seventh session (2026-11-27) took it from 14 of 16: `get_value 1,2,0`
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
| 13 | `wait_nil 0,0,0` (`3980`, `3985`) | 2 | ok: the S-stage COND (own tag ATOMo == the immediate; pinned by `s_cond_false`, which FAILed instruction 1 (since the seventh session a STOP at that write, MAR1 being STALE for an operand held directly; the old FAIL wrote through the previous instruction's carried MAR1: STOP at `3309`)) takes `3980`'s JMPF a (if cond) to `3985`; `3980` forms CNDF 2 on x's value (zero: nil), `3985` ends on it |
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
| `RULES['em1_29_mrb']`: CNDF 7 with EM1 `29` forms COND := the MRB (tag bit 0) of the AS1 input is ON | INFERRED | `31ec`-`31ed` | the contract: a structure whose pointer has its MRB on is shared and must not be reused in place; MRB off, it is reused (TR-466 4.2, printed p.7; thesis printed p.138, Fig. 3-23: the S stage tells E whether the data is collectable). `31ed` ends when COND is false (`j1_bit0_false`); else `31ee` calls `31a1` and `31f0` jumps to `put_list` (allocation). `pu_smt` side contract `reuse_kl1` (31ec-31ed, MDR1 LISTo or LISTx; `docs/pu_microcode_inference.md` 6): every value relation, never and always eliminated; mrb_on and mrb_off survive, coupled to the end polarity; under the adopted one mrb_on only. Static: `0ac9`-`0acb`, `0ace`-`0ad0` form it from MDR2 alone and stamp EHOOKo/x or EUNDFo/x by it. Not decided: whether the S stage's chain report (SRP) takes part (append's list is held directly, no REF: the two agree). Side cases in `u2_append.py`: 3,0,2 on LISTo reused (ok), 0,0,2 on LISTx goes on to `31ee` (pinned `REUSE_SHARED_STOP`: R04, pc, never set). Injection `em1_29_off`: append STOPs at `31a1` (called by `31ee`; since the eighth session on its JMPF 2), 4 of 16; the LISTx case FAILs (ended at `31ed`: a shared list reused) |
| `RULES['alu_sources']` = 'rassy': the ALU's input pair by AS1F and AS2F as rassy names it (supersedes `as1f2_yr`, `as1f3_em2`, `as1f3_open_unknown`) | HELD-SOURCE (the table); INFERRED that the hardware does what rassy prints | `216d`, `4cc0`, `0802`, `3378` | `ptfdump.py pimmutil rassy --list`: `as1f_and_as2f/6` (@29b1) is a switch on AS1F. 0 `0` and 1 `xr`, and 4-7 `mdr1`, `mdr2`, `mar1`, `mar2`, each paired with `as2f/2` (@2efc: 0 `0`, 1 `yr`, 2 `mdr1`, 3 `mdr2`). 2 calls `with_constant/2` (@2f1c): AS1 is `[mdr1, mdr2, mar1, mar2][AS2F]`, AS2 the constant. 3 calls `special_case/5` (@800): AS2F 0 `0` and 1 `xr` with the constant, 2 `mar1` and 3 `mar2` against `xr`. Held-out check: `220f` (AS1F 3 AS2F 1, EM2 12) is MAR1 := R14 + 12, the cell 12 that `enqueue_goal`'s `4c03` (AS1F 2 AS2F 2, EM2 12) writes. So the "word that loads YR and uses it" (`216d`, `4cc0`) does not read YR at all: `4cc0` is R15 := MDR1 - EM2 2, and `216d` R15 := R15 - 1. `0802` is MAR1 against XR. NOT discriminated on a pinned run (append 15 of 16, `check_pu` unchanged): nothing compared reads the words it changes. Injection `alu_old` (the three old rules): append unchanged |
| `RULES['alu_const']` = 'EM2': the ALU constant is EM2, or EM1 when EM2 is used by another field (`em2_busy`), else it raises | HELD-SOURCE | `216d`, `3378` | rassy's `alf/7` prints the constant through `$or$70` / `$or$71` (@3d09 / @3d1a): EM2, or EM1 when the slot `em2_not_free` is set. Census (image 2) of AS1F 2 words with ALF 0/1: EM2 is 1 in 68 of 155 (AS2F 0, add), 52 of 97 (sub), ... 156 of 402 (AS1F 3 AS2F 1, add): an increment. With ALF 2/3, EM2 is the operation and EM1 the constant. `pu.em1_busy` / `em2_busy` follow rassy's `em1_not_free` / `em2_not_free` setters (jumps, CNDF a/b/d, TGIF 3, SC2F 9/a/b/c ...). Injection `const_em3`: append and `check_pu` unchanged (NOT discriminated there) |
| `pu.S1_IMM`, `S2_IMM` (`EM_IMM`): S1 selects 5/6/7 are the immediates EM1/EM2/EM3, S2 select `d` is EM3 (WRBF clear); supersedes `zero_regs` | HELD-SOURCE (the listing); INFERRED that the hardware reads the field rassy prints | `3324`, `216d` | rassy `sc1f/7` (@21bf; `set_up_sc1f/3` @c68 passes SC1F, WRBF, EM1, EM2, EM3): 0-4 `dr`, `sr`, `gr`, `lc`, `pc`, and 5/6/7 print hex EM1/EM2/EM3; `sc2f/8` (@24b7) prints EM3 for `d`. Fits the never-set census (R05, R06, R07: 549 reads, 14 DSTF writes): `{ATOMo, R06}` where nil stands is EM2 0, `{UNDF, R07}` at `31d6` EM3 0, `1a0 + R05` a parameter cell `1a0` + EM1. The allocator's last-cell arm now runs past `3324` (R05 is EM1) into the refill and stops at `3365` (W0d), as the refill case does; `check_pu` 81 words (was 80). Injection `em_imm_off` (the old `zero_regs`): `check_pu` PASS at 80 words (both stops are in the refill set): NOT discriminated |
| `RULES['sc2f1_ir']` = 'ext_ir': SC2F 1 puts the IR field that EM2 & 15 names on S2 (`pu.EXT_IR`), with or without WRBF | HELD-SOURCE | `31ec`, `4c00` | rassy `ext_ir/2` (@2e72), a switch on EM2 & 15: 0 and 8 `ir`; 1 `ir/16`, 2 `ir/24`, 3 `(ir>>16)/16`, 4 `ir/8`, 5 `(ir>>8)/8`, 6 `(ir>>16)/8`, 7 `(ir>>24)/8`; 9-f the signed forms. `sc2f/8`'s arm 1 sets `em2_not_free` and does not test WRBF. Census of SC2F 1 loads, EM2 & 15: 1 in 4, 4 in 3, 5 in 1, 6 in 18, 7 in 5, 9 in 22. `31ec` (`put_reused_structure`, `r_r_c8`) has 4 = c8; the label words `32f0`-`32ff` 9 = s16 (`pimm.py` sx16(c16)); `wait_vector` `3a03` / `3a06` 1 = c16; `enqueue_goal` `4c00` 6 = the x field (the arity; it was read as W01). Decides the width the old row left open. Injections: `ext_ir_off` (the old c16s reading) append unchanged; `sc2f1_reg` (read as R01) STOP at `31ec` |
| `setup.EXECUTE_MDR1_STALE`: at `execute`'s entry MDR1 is STALE | OURS | `4cc0` | `4cc0` is now R15 := MDR1 - 2 (above); the execute nano entry has EMO1 5 (`crr`), an S-stage source not decided, so MDR1 is not given and R15 stays STALE. Injection `execute_mdr1_carried` (MDR1 as the previous instruction left it): append unchanged |
| `get_bound_value`'s set-up (`setup.FORMS`, `S_CONST`): the S-stage test on A[x] (immediate UNDF, `S_ENTRY`), MDR2 := A[y] | OURS, with support | `3880` | `pimm.py` `i_get_bound_value` unifies reg[x] with reg[y]; OS1F 3 is the thesis's (3) "the RF entry named by r0-r3" (printed p.128; not fitted: `get_atom` has OS1F 1). `3880` = `3800`-`3801` without the stamp. Injections: `gbv_mdr2_x` (MDR2 := A[x]): FAIL at instruction 7 (the cell bound to a REF to itself); `s_no_mar1` now FAILs append there too, `s_imm_plus1` STOPs append at `3881` (zero word): append now discriminates `S_ENTRY`'s start and MAR1 |
| `put_reused_structure`'s operand y (`setup.FORMS`) | OURS (`pimm.py`'s reading) | `31ec` | append's 0,0,2 cannot tell y from x; the side case 3,0,2 does: injection `prs_operand_x` FAILs it (A3 and R02 = A3's old `{INT, 9}`), append passes |
| `pu.FLAG_CONDS`: CNDF 7 with EM1 `19` is COND := the slit-check flag, EM1 `21` the interrupt_all flag | INFERRED (DOCUMENTED that CNDF 7's EM1 selects a rare condition: thesis printed p.144) | `4cc0`, `4cc2` | the numbering is `rassy`'s 40 condition constants in the order the class holds them (`ptfdump.py pimmutil rassy`: `cond alf_zero` .. `cond ovf_trap`), EM1 = the position; since the sixth session HELD-SOURCE: `cndf/7`'s arm 7 calls `cndf_others/5` (@3321), a hash switch on EM1 whose key k takes pool slot `00dc` + k (k = `00`..`27`). Three checks fit it: position 9 is `over_flow` and 10 `less`, where EM1 `09` (overflow) and `0a` (lt) were found apart from rassy (pu_smt); positions 21-31 (`exsw00` .. `COL`) carry the numbers rassy's own flag set/reset tables give those flags (`--pairs`: `set_slit_check` 25, ... `set_COL` 31). So `19` = 25 = `slit_check`, `21` = 33 = `interrupt_all` (rassy's keys). Slit check: events (GC request, packet arrival, other PEs' signals) latched in flags and polled once per reduction (`docs/literature_gaps.md` [P1] s.5.4; TR-715 3.3 for PIM/m, `docs/multi_pe.md`). Static: 37 EM1-`19` words, many with no ALU operation (a flag, not an ALU relation). The flags' values are OURS (`u2_append.EXECUTE_FLAGS`, both clear; an unset flag raises). pu_smt `execute_fast`: under 'prev', the condition `4cc0` forms must be `never` for every register content (data-independent). Injections: `slit_pending` STOPs at `4cc5` (since the seventh session, JMPF b a call, at `4cc6`: JMPF c polarity), `interrupt_pending` at `1c2f` (via `4cc4`, `4cd3`; `1c2c` until the eighth session, whose lc_zero runs it); `flags_swapped` changes nothing: which flag is which is NOT discriminated |
| `RULES['cjump_time']` = 'prev' with `pu.CJUMP_TAKEN_ON` {b: taken on COND} | INFERRED | `4cc1` | a conditional JMPF a/b/c/e tests the COND the previous executed word formed: thesis printed p.130 (condition into COND one step, branch the next, DOCUMENTED); the ends' 'prev' (EXECUTED, pu_smt); at `4cc1` (which forms CNDF 3 itself) 'same' would leave `4cc0`'s slit check untested on every path; static census of non-self conditional jumps, own CNDF / only the word before has one: b 4 / 27, a 51 / 97, c 23 / 123, e 45 / 94. pu_smt side contract `execute_fast` (no event: `4cc1` not taken for any register content), with the decided datapath fixed: with CNDF 3 = lt only ctime 'prev' survives (pinned). Polarity: b only (taken on COND: the fast path `4cc2`-`4cc3` sets R04 := the label); a, c, e raise. Injections: `cjump_same` STOPs at `4cc1` (its own COND is STALE), `cjump_false` STOPs at `4cc5` (since the seventh session at `4cc6`, JMPF c polarity: `4cc5` is called and its AS1F 3 / AS2F 1 result is UNKNOWN) |
| `RULES['as1f2_yr']`: AS1F 2 is YR | RETRACTED (eighth session) | `4cc0` | superseded by `alu_sources` above: rassy's AS1F 2 is `with_constant`, MDR1 / MDR2 / MAR1 / MAR2 against the constant, not YR (the old reading took SD1F's numbering for AS1F's). Kept as the injection `as1f2_off` / `alu_old` |
| `RULES['cnd3_sign']`: CNDF 3 = the ALU result is negative | INFERRED, NOT discriminated | `4cc1` | rassy's short condition table in the class's order `carry, zero, sign, same_tag, equal, lc_one` read as CNDF 1-6: 2 (zero, decided at `204f`), 5 (eq, pu_smt) and 6 (the lc loops) fit. At `4cc1` its input is STALE and nothing tests it; `cnd3_off` changes nothing |
| `RULES['jmpf8_flag']`: JMPF 8 sequences as JMPF 0 in a word whose CNDF 7 is a flag condition | INFERRED, admitted only there | `4cc2` | as `jmpf8_setup`; what bit 26 adds is not decided. Injection `jmpf8_flag_off`: STOP at `4cc2` |
| `pu.MCF_UNKNOWN` {06, 07}: MCF with these EM1 is an operation of UNKNOWN meaning on state not held here; recorded in the cycle record (`mcf`), no register or memory changed | INFERRED (that nothing run here reads it) | `4cc1` (07), `4cc3` (06) | thesis printed p.144: MCF is counter/flag control. 06: 75 words, 59 in words that put a freed cell on R19 (wait_*, switch_on_*, `3309`), 4 at execute's ends; 07: 11 words, all at goal or reduction boundaries (proceed `2170`/`217a`/`2212`, execute, execute_external, suspend, merge, the boot `20a8`); rassy's reset table numbers 6 reset_SUSPF and 7 reset_CGCF: since the seventh session HELD-SOURCE by rassy's MCF decoder (`MCF_FLAG_OPS` row below); what they do is still not modelled. Injection `mcf_unknown_raise`: STOP at `4cc1` |
| `execute`'s set-up (`setup.FORMS` 'label_mdr2'): MDR2 := pc + 2 + c16, no tag | OURS, with support | `4cc2` | `pimm.py`'s `i_execute`; nano-code OS1F 2 (the thesis's (2) "an operand field", printed p.128) and ODSF 2 (MDR2, as for collect_list); the held words use MDR2 as the code address (`4cc2`, `4ccf`, `4cd3`). Injection `execute_mdr1`: FAIL at execute (R04 = MDR2's old value) |
| `pu.STALE` and `u2_append.seed_execute`: R0d, W1f (and, until the sixth session, R04) hold values the harness does not know (STALE) before execute; a STALE value may be copied and pass the ALU (result and COND STALE), but a test, a memory write, an address or a comparison with `pimm.py` STOPs or FAILs | OURS | `4cc0`-`4cc3` | R0d is a scratch register (47 writers, none run before), W1f is written at boot (`20a8` W1f := 0) and by proceed, R04 (rassy's `pc`) is the A stage's. That the run reaches its end with them STALE shows their values do not matter on the fast path; `tgif3_em1` FAILs execute (R04 tag `21`) |
| `u2_append.A_STAGE_R04`: while an instruction is in E, R04 (rassy's `pc`) is `{COD, pc + 1}`, given by the harness before each instruction; `compare_next_pc`: a firmware that changed R04 branched there (must be `pimm.py`'s next instruction), else it falls through to pc + 1 | OURS, with support | `3310`, `2461` | the label branch adds c16 to R04 and then 1 (`2447` YR := #1, `2461` R04 := XR + YR) where `pimm.py`'s target is pc + 2 + c16; `switch_on_constant`'s rows `2420`, `242c`, `243c` read the instruction's second cell at [R04] (`pimm.py` `cells[pc + 1]`). Injection `r04_pc` (R04 = pc): FAIL at 12 (the label - 1), and the VECT0o case |
| `RULES['jmpf2_case']`: JMPF 2 is a case_branch, target (upc + EM3, signed as JMPF 4) \| TDAR | INFERRED (kind HELD-SOURCE) | `2447` | rassy's jmpf table (`ptfdump.py pimmutil rassy --list`, `jmpf/9` @2a5c, a switch on the JMPF value): arm 2 'base' 'case_branch' formatted by `short/3`, as arm 4 (goto, JMPF 4); arm 3 'base' 'case_branch' by `long/4` (S8). MEASURED: 15 of the 16 JMPF 2 words of image 2 put upc + EM3 on a 16-word boundary (all but `0207`): `2447` -> `2440`, `2455` -> `2450`, `31a1` -> `31a0` (also `31a3`'s base), `2401`, `2425`, `2437`, `323c`, `327c`, `32bd`, `34bf`, `4192`, `0d9c`, `0105`, `0107`, `0205`. Unsigned gives the same count, but `2450`'s rows do not write R04: injection `jmpf2_unsigned` FAILs (no branch); `jmpf2_off` STOPs at `2447` |
| `setup.S_OTHER_ROW`: an ODPF 6 entry whose dereferenced operand's tag is not the immediate's (MRB ignored), held directly with its MRB off, starts at entry \| 4 << 2 (chain code 0); other chains raise | INFERRED (mechanism DOCUMENTED, thesis pp.134-138) | `3310` | the 32 words behind `switch_on_non_list` (`3300`) are 8 rows of 4, rows 4-7 all the label computation; `switch_on_non_integer` / `_atom` (`32e0` / `32e2`) interleave the same rows (`32f0`-`32fe` the label). Row 0 for a directly held operand is the entry (`S_ENTRY`), so chain code 0 is that operand; rows 1-3 (a marked list, a freed variable cell, both) read, not run. TGT column TDPF by the tag (`s_imm_row`) sends LISTo to row 2. Injection `other_row_entry` (every tag at the entry): FAIL at 12 (nil taken for a list, a cell freed; since the seventh session a STOP at that write, MAR1 being STALE for an operand held directly; the old FAIL wrote through the previous instruction's carried MAR1: STOP at `3309`) |
| `setup.S_TDAR`: the S stage loads TDAR with the TGT byte of the dereferenced operand's tag from column 7 - TDPF | INFERRED (mechanism DOCUMENTED, thesis printed p.134 (2) and Fig. 3-22's TDPF) | `2447` | table shapes (image 2): TDPF 4 (`switch_on_non_vector`, `2400`) column 3, VECT1..6 = 8..18 on the six rows `2408`-`2412` that differ only in EM1 1..6; TDPF 2 (`write_marked_value` `3240`, `put_marked_value` `3280`) column 5 byte for byte (INTx 4 .. VECT0x 7 re-stamped o at `3244`-`3247`); TDPF 0 (`switch_on_constant` `2420`, `hash_on_constant` `2430`, the label branch `2440`) column 7: constants 0, structures 2, UNDF 4, hooks 6, EXREF 8, MGHOK/EXMRF 10 (those four to `24b1`), REF and the rest 12. Cross-check, HELD-SOURCE: rassy names CNDF 7 EM1 `3a` `case_tag_setup mdr1 5` and it is the column-2 set-up VERIFIED at `2d3e`, so `case_tag_setup` k reads column 7 - k too. Injections: `tdar_col_tdpf` STOPs at `2444` (MRP); `tdar_col6` passes append (ATOMo 0 in both) and only the side case `switch_label_case` ({VECT0o, 0}: 6 in column 6) STOPs at `2446` |
| `setup.S_MDR2_OWN`: the S stage leaves the operand as it was before the dereference in MDR2 (ODSF 2) | OURS, with support | `3310` | the free-a-cell rows put MDR2 on the R19 list (`3309` R19 := MDR2, [MAR1] := the old head): the REF the dereference went through; `3310` tests it for REFo. Injection `mdr2_own_off`: append passes (the old MDR2 is not a REFo either); the VECT0o case STOPs at `3310`: that MDR2 is loaded is discriminated, its value (the operand before the dereference) NOT |
| `CJUMP_TAKEN_ON` a: on COND, e: on not COND (b: on COND, as before) | HELD-SOURCE (the polarity); INFERRED that rassy reads the field as the hardware does | `2440`, `2461` (e), `3980` (a) | rassy's `jmpf/9` arms 8-f each take one more pool constant through a relative `pmi 49` operand; resolved, arms 8-f land on slots `00af`-`00b6`: `00af`-`00b2` 'if cond', `00b3`-`00b6` [if, [not, cond]] (one slot each; `jmpf/10` on `00b7`-`00be`), so 8-b are taken if cond and c-f if not. Joint: e's polarity, `S_MDR2_OWN` and COL are tied in append (`e_mdr2_col`, all three flipped: e on COND, MDR2 a REFo, COL true, passes 14 of 16 and the VECT0o case); rassy breaks the tie. Injections `e_on_true`: FAIL at 12 (`2441`-`2445` write [MAR1]); `a_on_false`: FAIL at 13 (`3981` writes [MAR1]); since the seventh session a STOP at that write, MAR1 being STALE for an operand held directly; the old FAIL wrote through the previous instruction's carried MAR1: STOP at `2445` and `3981`. A STOP on STALE is weaker evidence than a FAIL against `pimm.py`: it shows the wrong polarity uses a value the harness does not know. The same table makes b "call long if cond": adopted in the seventh session (`RULES['jmpf_b_call']`, below), the S7 conflict decided. (`e_mdr2_col` passes 15 of 16 since then: the tie stands through `get_value`.) |
| `RULES['em2_mrb']`: ALF 2/3 with EM2 20 = MRB off, 30 = MRB on (the AS1 input with tag bit 0 cleared / set) | INFERRED (names HELD-SOURCE) | `2447` | rassy's `special_operation/4` (@3030, a switch on EM2): 0 '+' .. 15 shift_right_arithmetic, 32 'mrb_off', 48 'mrb_on'. The rows agree: `32e4`/`32ec` (an integer or atom marked) clear the MRB where the list rows `3304`/`330c` stamp LISTx. Injection `mrb_swapped`: FAIL at 12 (A0 := `{ATOMx, 0}`) |
| `FLAG_CONDS` 1e MRP, 1f COL; `setup.S_REPORTS_DIRECT` COL false for an operand held directly | INFERRED (names HELD-SOURCE: rassy `cndf_others` keys 1e, 1f; the flag tables' set_/reset_MRP 30, _COL 31); the value OURS | `2440`, `2461` | thesis printed p.138 Fig. 3-23: the S stage's dereference reports two chain bits (every MRB off; the first two pointers' MRBs off) to E. With no pointer followed there is nothing to collect. Injection `col_true`: FAIL at 12 (`2462`, `247b`-`2480` put a cell on the R19 list) |
| `MCF_NAMED` 08 = pipeline_cancel, recorded only | INFERRED (rassy's flag-control table, position 8, between reset_CGCF 7 and set_cc 9) | `2461` | the MCF 08 words load R04 (`2453`, `245d`, `2461`, `31ee`, `2035`): a branch discards the prefetched instructions; this simulator has no pipeline. Injection `mcf08_raise`: STOP at `2461` |
| `RULES['cnd8_s1']`: CNDF 8 / a: the S1-bus value's tag == EM1 / EM2; CNDF c: the same with the MRB ignored | INFERRED (HELD-SOURCE arms, MEASURED source) | `38b0` (8), `38b2` (c) | rassy's `cndf/7`: arms 8, 9 'tag =' EM1, a, b 'tag =' EM2, c, d 'tag / 5 =' EM1, 8/a/c on one operand and 9/b/d on the other. Census: all 217 CNDF 8 and 20 CNDF a words read an S1 source (114 / 9 for the condition alone), every CNDF 9 / b / d word has an ALU input; CNDF c's 100 EM1 are all 'o' tags. Needed to reach `0c0c`, NOT discriminated (no comparison before the stop): `cnd8_off` STOPs at `38b0` |
| `RULES['sd1_pairs']`: SD1F 2 = MDR1 and MAR1, 3 = MDR2 and MAR2 | INFERRED (HELD-SOURCE; DOCUMENTED that such codes exist) | `38b2` | rassy's `sd1f/2` (@2959): 2 ', mdr1 mar1', 3 ', mdr2 mar2'; thesis printed p.144: "codes include writing the same value to MAR1+MDR1 and MAR2+MDR2". Not discriminated: `sd1_pairs_off` STOPs at `38b2` |
| `RULES['jmpf9_call_if']`: JMPF 9 is a call taken if cond; only the arm not taken is modelled | INFERRED (HELD-SOURCE) | `38b1` | rassy `jmpf/9` arm 9 'call' with em1_not_free and em2_not_free and 'if cond'. Since the eighth session the taken arm calls the absolute EM (`jmpf9_vlong`, "Next, for U2"; `s_imm_row`'s get_atom now runs past `3811` and stops at `0cd9`). `jmpf9_off` STOPs at `38b1` |
| `wait_nil`, `get_value` set-up (`setup.FORMS`): the S-stage test on x | OURS (`pimm.py`'s operand readings) | `3980`, `38b0` | `get_value`'s row 0 (x unbound) loads A[y] into MDR2 and MAR2 (`38a0`, SD1F 3) to bind it with |
| `pu.CASE_TAG_SETUP`: CNDF 7 with EM1 `30`-`3f` is `case_tag_setup mdrN k` (EM1 even MDR1, odd MDR2, k = (EM1 - `30`) >> 1): TDAR := the TGT byte of that MDR's tag (old value), column 7 - k | INFERRED (names HELD-SOURCE: rassy `cndf_others/5` keys `30`-`3f`, slots `0106`-`0115`; column: `3a` = mdr1 5 is column 2, VERIFIED at `2d3e`) | `0c0c`, `0e38`, `0c0d`, `0840` | MEASURED (165 words), CCF bits 59..58 by parity: mdr1 00 8, 01 69, 10 4, 11 22; mdr2 00 7, 01 0, 10 49, 11 6 (a correlation; the rule does not rest on it). Shapes met: `0c0c` column 0 (REFo `0e38`, REFx `0e3b`, the rest call the trap `6c21`: the routine is called for a REF only); `0e38` column 5 (20 rows `0e60`-`0e73`, UNDF 18 -> `0e72`, a return; bound atomic values free the cell, `0e62`); `0c0d` column 6, `0840` column 7. The old rule (the AS1 input's tag, `TGT_COLUMN`) gives the same at `2d3e` (`check_pu.py` unchanged). Injections: `cts_as1` (the tag from the AS1 input, the old rule's source) STOPs at `0c0c` (AS1 is MAR1, STALE), `cts_col_k` at `0c15` (REFo 12 overlaps `0e38`), `cts_mdr_swapped` at `6c21` (the trap) |
| `RULES['jmpf_b_call']`: JMPF b is a page-relative call taken if cond | INFERRED (kind HELD-SOURCE: rassy `jmpf/9` arm b 'call' long 'if cond'); decides `docs/pu_microcode_inference.md` S7's conflict | `0c0c` (taken), `4cc1` (not taken) | the twins `0c0f`, `0c12` (JMPF 7, the same word otherwise) call `0c15`; every row behind it returns. MEASURED (scratch census of image 2, the words reachable from each target before a return or an end, calls taken as returning): JMPF b 47 targets, 38 only returns, 9 both, 0 only ends; JMPF 7 144 / 42 / 4, f 24 / 6 / 0; page jumps JMPF 6 338 / 185 / 510, e 130 / 15 / 218. `4cc1`'s slit path has a conditional return at `4cd2` into `4cc2`. Injection `jmpf_b_jump` (mekbn's page jump): STOP at `0e72` (return with an empty micro stack); `cjump_false` / `slit_pending` now call `4cc5` and STOP at `4cc6` (JMPF c polarity) |
| `RULES['case_wide']`: a JMPF 3 case_branch ORs the whole TGT byte when the base's low bits are free of it | INFERRED | `0e75` | base `0e60`, column 5's 0..19 on 20 rows `0e60`-`0e73` (S8's "low 4 bits" was the `2d3f` / `31a3` tables'). Injections: `case_low4` (S8 literally, byte & 15) FAILs at 14 (UNDF 18 -> `0e62`, the row that frees a cell bound to an atomic value: the cell gets the free-list link, nil is written at 0); `case_4bit` (a byte over 15 raises) STOPs at `0e75`, a guard |
| `RULES['tdar_holds']`: TDAR stands from its set-up across JMPF 1 words to a later case_branch | INFERRED (rassy names `tdar` among the registers) | `0802` | the twins `0c0d` -> `0c0e` -> `0802`, `0c10` -> `0c11` -> `0800`, `0c13` -> `0c14` -> `0801` all set up two words before the JMPF 3, a JMPF 1 jump between. Injection `tdar_one_word`: STOP at `0802` (a guard: needed, NOT discriminated) |
| `pu.MCF_FLAG_OPS`, `FLAG_CONDS` `10`-`12`: MCF EM1 `03`/`04`/`05` reset sw00/sw01/sw02, `0b`/`0c`/`0d` set them; CNDF 7 EM1 `10`-`12` reads them | INFERRED (names HELD-SOURCE: rassy `mc1/2` @355b, `mc2/3` @357b; EM1 = mc1 key << 4 \| mc2 key) | `0e75` (04), `0864` (`11`) | rassy's mc1 keys 1/2/3 are '-- lc', '++ gr', '++ sr' (slots `0116`-`0118`), and two rules decided apart fit EM1 = key << 4: MCF `20` = R02 + 1 (`mcf_20_sp`; rassy's bank names 2 `gr`) and `10` beside CNDF 6 in the counted loops (lc). So `08` = pipeline_cancel, `06` reset_SUSPF, `07` reset_CGCF (kept recorded-only). Static: sw01 is set by the dereference rows that follow a REF with its MRB on (`0e3b`, `0e61`, `0e63`, MCF `0c`) and reset at the REFo start (`0e75`); `09d0` ends when it is clear, else `09d1` rewrites the binding with the MRB on: the variable reached through a shared pointer. Injection `sw01_set`: FAIL at 14 (the cell `{ATOMx, 0}`, `pimm.py` `{ATOMo, 0}`) |
| `pu.ALF_CONDS`, `MCF_NAMED` `01` set_alf; (superseded since the eighth session by `alu_sources`: `0802` is MAR1 against XR) a COND from the latch is POISON | names HELD-SOURCE (rassy positions 0-8 `alf_zero` .. `alf_less_zero`; mc2 key 1); the rest OURS | `0802`, `0841` | `0802`'s EM bits are the JMPF 3 base (AS1F 3 AS2F 2 takes no constant); its CNDF 5 and set_alf feed only `0841`'s alf_equal, and `0864` forms a new COND before any test: NOT discriminated. Injection `as1f3_open_raise`: STOP at `0802` |
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
`1a0 + aa`..`b2`: unexplained), `209f` (with `20bc` R07 := 0, read not run; since the eighth
session R07 as an S1 source is the EM3 immediate, `pu.S1_IMM`), `20c2`, `20e7`, then R0e and R10.
(Since U3's second step `u3_goals.py` runs `3380` (R1b's refill), `209f`-`20a8`,
`20e7`-`210b` whole and `202d`-`2030`, section "U3, second step".)
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

### `proceed`, the goal scheduler (eighth session, 2026-11-27)

The append run still stops at `proceed` (`216c`, R1b never set), and
U2 is still 15 of 16. What changed is that the routine itself now runs
whole in **side cases**: `u2_append.proceed_cases`, 15 cases, all ok.
They give the firmware a ready queue built from `pimm.py`'s own
(`Machine.record`), in the firmware's record layout, and compare the
dispatch with `pimm.py`'s `pick`:

- the next goal's code address (R04 = `{COD, code}`);
- every argument register A0..An-1;
- R10 (the dispatched record) and R14 (the queue after the pick,
  `pimm.py`'s `rq`);
- that no cell is written but the finished record, which is pushed on
  R1b's list (declared, like `reuse`: R1b := the record, its cell 0 :=
  `{VECT0x, old R1b}`).

The cases are a queue of one goal (R14 left nil), and two goals whose
newest has arity 0 to 11. Arities fall on both sides of `2218`'s lc :=
arity - 3, and each of the loop's exits `2219`-`2222` is taken by some
case. For an empty queue, with crr (R15) not
exhausted (through `2170`'s call) and exhausted (through `216f` ->
`217a` -> `217b`'s taken JMPF 9; each route is checked in the trace),
the firmware enters the empty arm `21b2`. It dispatches nothing (R04 and the A registers as they were)
where `pick` returns 0, and stops at `21b3` (an ALF 3 shift, not
modelled: pinned, `EMPTY_STOP`).

The words, read with this session's rules (each row below):

| words | what they do |
|---|---|
| `216c`-`216d` | push the finished record (MAR1 = R10) on R1b; R15 := R15 - 1 (with_constant, EM2 1), set_alf; YR := 12 (EM3 immediate) |
| `216e`-`216f` | R10 := R14; to `217a` if R15 - 1 is negative (`216e`) or zero (`216f`, alf_zero); COND := R14 is nil |
| `2170` | MAR1 := R14 + 12 (AS1F 3 AS2F 1, constant 12); call `21b2` if nil |
| `2171`-`2173` | R16 := R16 - 1; R04 := cell 12; MDR1 := cell 13; past `2213` while R16 - 1 is not 0 |
| `2213`-`2216` | R12 := cell 13 (priority); cell 14 against R13 (CNDF 5 in the JMPF 9 word `2214`; `2215`'s JMPF f calls `2250` unless they are equal); R14 := cell 15; RFAR := 0; MCF set_SUSPF, rf_lock |
| `2218`-`2223` | lc := cell 0 - 3; A[rfar++] := cells 1, 2, ... (DSTF c), the loop leaving on sign, lc_zero or lc_one with '-- lc' |
| `2224` | end (MCF rf_unlock) |

The rows decided for it, all in `pu.py` (HELD-SOURCE: from rassy's
listing, `ptfdump.py pimmutil rassy --list`):

| Rule | Status | Evidence | Injection (observed) |
|---|---|---|---|
| `pu.cndf_free`, `RULES['jmpf9_cndf']`: CNDF forms a condition in a JMPF 9 word (not in JMPF 1) | HELD-SOURCE | rassy's jmpf/9 arm 1 calls `special_jump/8` (@30ec), a 15-key switch on CNDF; arm 9 prints with `vlong/2` (@32da), which marks em1/em2_not_free only (`elong/5` @32df marks `cndf_used`). Static: the 10 JMPF 9 words with a CNDF all carry an ALU add or subtract | `jmpf9_cndf_off`: the 13 queued cases STOP at `2250` (`2215` tests `2213`'s interrupt flag instead and calls) |
| `RULES['jmpf9_vlong']`: a taken JMPF 9 calls the absolute EM | HELD-SOURCE plus static; NOT discriminated by execution | arm 9 prints its target with `vlong` (the whole EM), as arm 5 (JMPF 5, the absolute call) does; arms 6, 7, a, b, e, f use `long/4` (@32cd, page-relative). Static: `21b8`'s EM is `6c21`, the trap, outside the page. Executed taken at `217b` (EM `21b2`), where the page-relative reading lands on the same word | `jmpf9_taken_raise`: the crr-exhausted empty case STOPs at `217b` (a guard: the arm is needed) |
| `RULES['jmpf_f_call_ifnot']`: JMPF f is a page-relative call taken if NOT cond | HELD-SOURCE (the kind) | rassy jmpf/9 arm f: 'call', `long`, the 'if not cond' slot (arm b is 'if cond') | `jmpf_f_off`: the 13 queued cases STOP at `2215` |
| `RULES['dstf_c_rfar']`: DSTF c (WRBF clear) writes A[RFAR] and steps RFAR (R06) | INFERRED (name HELD-SOURCE) | `dstf/5` key 12 prints pool slot 95 '++ rfar', after `@ r0` .. `@ r1b1` for keys 8-b; second bank 6 is `rfar` | `rfar_off`: the 12 cases with arity > 0 FAIL on every A register |
| `RULES['lc_ops']` = 'old': MCF EM1 `10` is '-- lc' (R03 - 1); CNDF 6 lc_one, CNDF 7 EM1 `0d` lc_zero, on lc as it stood before the word | INFERRED (names HELD-SOURCE) | mc1's key 1 '-- lc' (slot `0116`); the short condition table's sixth `lc_one`; cndf_others key `0d` `lc_zero`; R03 is the second bank's `lc` | `lc_new` (the conditions see the decremented lc): arity 4 STOPs at `222b`; arities 5-11 FAIL (the last argument not loaded) |
| `pu.alf_cond`, `ALF_LATCHED`: alf_zero is formed from the set_alf latch (the result was 0); alf_sign and alf_equal stay POISON (nothing run tests them) | INFERRED (names HELD-SOURCE) | rassy position 0; formed at `216e` on `216d`'s R15 - 1 and tested by `216f` | `alf_poison`: all 15 STOP at `216f`; `alf_zero_false` (always false): the crr-1 empty case FAILs (the empty arm not reached through `217b`) |
| `MCF_NAMED` `0e` set_SUSPF; `MCF_SUB` (`0a`, 2) rf_lock, (`02`, 2) rf_unlock: recorded only | HELD-SOURCE | `set_up_mcf/3` (@cdd): mc2 keys 2 / a are reset / set switches on EM bits 8-4; key e set_SUSPF | none (nothing reads them) |

The datapath rows of the same session are discriminated here, where
append could not discriminate them:

- `alu_old` and `em_imm_off`: all 15 cases STOP at `216d`.
- `const_em3`: the 13 queued cases STOP at `217c` (R15 - 12 takes the
  crr branch), and the crr-8 empty case FAILs on its route.

`as1f3_xr_off` (0802's source), `ext_ir_off` and `execute_mdr1_carried`
are still NOT discriminated (no word on the path uses them), and nor is
the JMPF 9 target reading.

The stand-in (`u2_append.seed_proceed`, OURS), each item:

- R1b: one free record.
- R15 (crr) and R16 (ccc): 8, so the budget branches fall to the
  dispatch. That they are reduction / switch budgets is INFERENCE from
  the decrements; the cases where they run out are not compared.
  (U3 reads R16 further: a queue length or a live-goal count, OPEN;
  section "U3".)
- R12 and R13: the current priority and foster parent. Every queued
  goal carries R13 in cell 14 (one shoen). `parent_other` (another
  parent): 13 STOPs at `2250`, the other-shoen path, not modelled.
- W1f: 0 (start's `20a8` writes it 0).
- R14: the head of `pimm.py`'s queue as `{HOOKo, record}`; the empty
  queue is nil (INFERRED: `216f` / `217a` test R14's tag against ATOMo,
  and `enqueue_goal`'s `4c06` puts the old R14 in cell 15).
  `empty_int0` (the end as `{INT, 0}`): the empty cases STOP (`2173`,
  `217c`), and the one-goal case FAILs on R14. `empty_fw_goal` (the
  firmware given a goal while `pimm.py`'s queue is empty): the crr-8
  empty case FAILs ("pimm.py picks no goal; the firmware dispatched
  R04"), the crr-1 one STOPs at `217c`.

The record layout is INFERRED from the firmware's own writers:

| cell | holds | evidence |
|---|---|---|
| 0 | `{GOAL, arity}` | `enqueue_goal` `4c00` YR := the IR's x field (`ext_ir` 6); `4c01` stamps it GOAL (TGIF 3, EM2 `3c`); `4c03` writes it at R10 |
| 1..n | the arguments | `set_*` write R10 + x, with x from 1; `pimm.py`'s enqueue takes argv[1:x+1] |
| 12 | `{COD, code}` | |
| 13 | priority (R12) | |
| 14 | foster parent (R13) | |
| 15 | link | |

Cells 12-15: `4c03` MAR2 := R10 + 12, then four writes of `{COD, W10}`,
R12, R13, R14 in that order; suspend's `1c0d`-`1c10` the same.

Injections on the layout:

- `rec_code_13` (cells 12 and 13 swapped): the 13 queued cases FAIL on
  R04.
- `args_from_2`: the 12 cases with arity > 0 FAIL on the A registers.

**One declared difference.** The loop loads at least two registers
(`2219` and `2223` are unconditional). So a goal of arity 0 or 1 also
gets A0 / A1 from its record's cells 1-2, which `pimm.py` leaves. The
compare admits exactly that: the register equals the record's own cell.
`free_undeclared` (the freed record's write not declared) FAILs all 15.

**Why append itself stays at 15 of 16 (a counting choice, not an
impossibility).** At append's `proceed`,
`pimm.py`'s queue is empty, so its `pick` returns 0 and the run ends.
`i_proceed` writes no R or M line. Taking the sixteenth instruction as
matched would compare the empty case above, but only by seeding the
main run's R1b, R15, R16, R12 and R13 with values neither model holds
(OURS). The empty side case is exactly that comparison; counting it
as the sixteenth instruction is left to the reviewer. The empty
arm's own end (the shift at `21b3`, a return or `21b5`'s priority
search over the Goal Stack Entry Table at fixed cells `b6` / `b7`,
PIMM.PARAM's gsesh / gseb by place: INFERENCE) is not run.

What is left open on proceed's paths (updated by U3, section "U3"; the
second step changes only the crr-exhausted item: PMPF is now given, so
`crr_two` stops one word later, at `217d`'s JMPF d):

- Now run (U3): proceed after `enqueue_goal` in one run, on records,
  R14, R10 and R1b the firmware wrote itself (`u3_goals.py`, 2
  dispatching picks), and the empty arm `21b2` reached through `2170`
  on an R14 the firmware's own dequeue left (the third pick).
- The crr-exhausted dispatch (`217a` -> `217c`, CNDF 7 EM1 `1a`,
  PMPF): reached only under U3's injection `crr_two` (STOP at `217c`).
- The other-parent call `2250` (CNDF d): reached only under U3's
  injection `ccf_bits` (cells 13 / 14 written from MDR1).
- The interrupt call `2214` -> `22a5`.
- R16 exhausted (`2173` falling to `2174`): partly run under U3's
  injection `r16_zero` (`2174`-`2177`, `3349`, `12e0`-`12e2`; STOP at
  `12e3`, 'cond PMPF', a flag not given). `12e0`-`12ea` add R15 to a
  cell of R13's record and clear R15 (read, not run past `12e2`).
- Arities over 11 (`2222`).
- The shift operations (ALF 3 by EM2); also enqueue_goal's slit-check
  arm `4c08` (U3 injection `slit_pending`: STOP at `4c08`).

**What would close it** (and what U3 should be; its first step is
done, section "U3") is a multi-goal program on the held microcode, in which
`proceed` and `execute` hand over between goals through the scheduler
above. For example, a clause that enqueues a body goal
(`enqueue_goal` `4c00`-`4c07`, whose writes are the layout's evidence)
and then proceeds into it. That needs the main run's scheduler state
carried from the firmware's own writes (R14 and R1b set by
`enqueue_goal` and `proceed`, not seeded), and `pimm.py`'s trace
compared at each goal switch.

So U2 stands at 15 of 16 with every KL1-B instruction of the clause
bodies matched. What was left open on the path run:

- `0802`: AS1F 3 with AS2F 2 is MAR1 against XR since the eighth
  session (rassy `special_case`, `alu_sources`); its CNDF 5 and set_alf
  feed only `0841`'s alf_equal (now formed, `alf_cond`), which `0864`
  overwrites before any test: NOT discriminated. The atomic-against-
  atomic rows (`0860`, end if alf_equal) would test it.
- `0c0c`'s W1d := MAR1 and `0c0d`'s XR := W1d (MAR1 STALE for an operand
  held directly): dead on this path. The twins `0c10` / `0c13` restore
  MAR1 from W1d, which is where it matters (`38ae` / `38af` callers).
- MCF `06` / `07` are now named by rassy's `mc2` (reset_SUSPF /
  reset_CGCF), still recorded only.
- EM1 `0d` = 13 `lc_zero` is decided in the eighth session (`lc_ops`,
  run in proceed's argument loop); `1c2c` on the interrupt path is not
  run.

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

## U3: several goals on the held scheduler (2026-11-27, first session)

**First step reached: 41 of 41 instructions executed and matched (162
held microinstructions), 3 scheduler picks compared with `pimm.py`, 2
dispatching and 1 empty, no mismatch.** `u3_goals.py` (in
`run_tests.sh`, pinned: steps, matched and picks) runs a driver clause
that enqueues two goals of the IPL image's `append/3` and proceeds:

    driver(L1, M1, Z1, L2, M2, Z2):
        set_value 1,0  set_value 2,1  set_value 3,2  enqueue_goal 3, append/3
        set_value 1,3  set_value 2,4  set_value 3,5  enqueue_goal 3, append/3
        proceed

as `driver([a], [], Z1, [b], [], Z2)`. The driver is OURS (the test's
input: three held KL1-B cell kinds, no micro-routine); every E stage is
held. The picks: the driver's `proceed` dispatches `append([b], [], Z2)`
(the newest, as `pimm.py`'s `pick`), whose `proceed` dispatches
`append([a], [], Z1)`, whose `proceed` finds the queue empty and enters
the empty arm `21b2` (pinned stop `21b3`, as in U2's side cases).
(`[b, c]` as the second list was tried first: `read_variable` on the
cdr gives LISTo on the firmware, LISTx on `pimm.py`, whose `sp_single`
is set only by `wait_vector`; not declared here, `pimm.py` belongs to
another agent.)

**The queue is the firmware's.** `set_value` (`3187`) writes the record
R10 + x; `enqueue_goal` (`4c00`-`4c07`) writes cell 0 `{GOAL, n}`, cells
12-15 (`{COD, label}`, R12, R13, the old R14), R14 := `{HOOKo, record}`,
R10 := a record popped off R1b, R16 + 1, R15 - 1; `proceed` pushes the
finished record on R1b, takes R14's head, and R14 := its cell 15. At
every pick the harness checks that R14 and every record cell `proceed`
reads were last written by a held word (`Prov`); the injection
`reseed_r14` (the harness rewrites R14, same value, after the second
enqueue) FAILs at the first pick on that check alone. It also walks
every register (R, W) and record cell each pick's words read, in order,
and pins those whose last writer is the harness (`RESIDUAL_PINNED`, the
OURS state still under the scheduler): R13 and W1f at picks 1 and 2,
W1f at the empty pick. R13 (the foster parent, read at `2173` and
`2213`) and W1f (`2224`, `21b2`) are written by no held word of the
run; everything else `proceed` reads, R14, R10, R1b, R12, R15, R16 and
the record cells included, was last written by held words. Compared per
instruction: `set_value`'s cell against `pimm.py`'s argv line;
`enqueue_goal`'s record against `pimm.py`'s new record (arity, every
argument under the renaming, code, link mapped record to record, R14,
R10); each pick's R04, R10, R14 (as `pimm.py`'s rq after the pick),
A0..An-1 (its R lines) and the freed record (declared, as U2's
'free'); the other instructions through U2's `compare`.

**What is not the firmware's: the state before the first instruction**
(*superseded by the second step*, which runs these boot words; kept as
the first step's record) (`u3_goals.INITIAL`, OURS; no instruction of the program writes these
before reading them). Each cites the held boot word that writes it, read
not run: R1b's free records (linked through cell 0 as `216c` pushes)
and the R10 the driver builds into (`202d`-`202f`); R14 = nil (the
boot's first record gets `{ATOMo, R06}` as link at `210a`-`210b`, R06 =
0 there: INFERENCE); R12 = `{INT, 0}` (`2102`); R13 = `{FPREC, root}`
(`20eb`); R15 = `{INT, 17}` (`20a6`-`20a7`, one arm of `209f`'s PMPF
test); W1f = 0 (`20a8`); R16 = 1 (an OPEN choice, below). R14 = nil and R16 pull against each
other: the boot's R06 = 0 that gives R14 = nil also gives R16 = 0 at
`20a0`-`20a1`. Plus U2's stand-ins
(the A stage, the first goal switch, the cell free lists, memory). The
empty pick's nil is the initial R14, carried by the firmware: `4c07`
put it in the first record's cell 15 and `2216` took it back.

**What it does not run.** None of the six "not yet run on proceed's
paths" items runs in the main run: crr exhausted (`217c`), the
other-parent call (`2250`), R16 exhausted (`2174`-), the 4c08 shift,
interrupts, arities over 11. The first four are reached only under
injections or the R16 = 0 run, and stop there.

**Why append's own pin stays at 15 of 16.** Run alone, append's
`proceed` reads R1b, R14, R15, R16, R12 and R13 that only the stand-in
above gives, so its sixteenth instruction would be counted on OURS
scheduler state. In U3 the same held `proceed` at append's sixteenth
cell runs twice (picks 2 and 3) on firmware-written queue state, with
the initial values above still under it. The condition for moving the
pin (no OURS scheduler seed) is not met for the standalone run, so
`u2_append.PINNED` is unchanged. Closing it needs the boot (`209f`,
`20e7`-`210b`) run held: `209f` stops on CNDF 7 EM1 `1a` (PMPF, a flag
no source here gives).

Rules decided in this session (each in `pu.py` / `setup.py`, with its
injection in `u3_goals.py`, observed):

| Rule | Status | Evidence | Injection (observed) |
|---|---|---|---|
| `RULES['ccf_rassy']`: the memory operation is rassy's CCF value table (`CCF_RASSY`), not the strobe bits one by one | HELD-SOURCE | rassy `ccf/2` (@1b5b), a 32-key switch on CCF (bits 62..58; `set_up_ccf/2` @c44: the word's high half >> 26 & 1f); each key's relative `pmi 29` operand resolved (slot = cell + 2 + c16) to pool slots `0076`-`008e`: 08-0b read mar1/2 mdr1/2, 0c read ++ mar1 mdr1, **0d read ++ mar2 mdr2**, 10-13 write, 14 write ++ mar1 mdr1, **15 write ++ mar2 mdr2**, **16 write_stack ++ mar1 mdr1**, 17 write_stack ++ mar2 mdr2, 0e set_misc_command, 0f cancel, 18-1f unify_write .. exec_misc_write. It agrees with the bit reading except on 0d, 15, 16, 0e and 0f. Of those, only 15 is discriminated by execution (`ccf_bits`); 0d, 16, 0e and 0f are changed on the held source alone (0d runs at `2222` in failing U2 side cases only; 16 at `3367` is not reached). Decided at `4c05`/`4c06` (CCF 15): cells 13 and 14 get R12 and R13 (the conflict section 18 of `pseudo_pimm_microcode.md` left open). `write_stack` stored as `write` (INFERRED). 0f 'cancel' leaves MAR2 / MDR2 STALE (`3494`, read_variable's end, uses neither: NOT discriminated); 0e and 18-1f raise | `ccf_bits`: STOP at `2250` at the first pick (cell 14 holds R1b's link, not R13: the other-parent call) |
| `RULES['wsel_d_em1']`: a select d (SC1F / SC2F / DSTF) with WRBF set is R(10 \| EM1), EM1 0-f | INFERRED (from the image) | the 4 such writers carry EM1 0, 9, b, 2 (`21e4` R10 after a `3349` pop, as `202f`); at `4c01` (EM1 5) MAR1 := R15, so `4c02` is R15 := R15 - 1 as `216d` and `4cc0`. Held-out: the refill `3365`/`3366` (EM1 f) take MAR1 := R1f, the heap pointer; `check_pu.py`'s refill cases now stop at `3367` (a stepping write that also loads MAR1), re-pinned. EM1 10-3f raise, and so does a word whose other fields also consume EM1 (`em1_other_use`): 53 of the 99 select-d words are admitted; 14 use EM1 elsewhere too (`0517`, `0ab4`-`0abc`, `1989`, `357c`, `3c39`, `4172`, `4c5f`, `63d6`, `75a4`, `79c9`), counter-evidence kept. rassy's `sc1f/7` arm d not decoded | `wsel_d_off`: STOP at `4c01` (W0d never set) |
| `RULES['jmpf8_goto_if']`: JMPF 8 in a word with no CNDF is a short goto (upc + signed EM3) taken if COND (the word before's) | HELD-SOURCE (the kind), INFERRED (the timing) | rassy `jmpf/9` arm 8 (@2afb): 'goto', `short/3`, the 'if cond' slot `00af`. At `4c01` COND is `4c00`'s slit_check (CNDF 7 EM1 19); taken, `4c08` (a priority-bit shift, as execute's `4cc5`). Tension recorded: rassy's arm covers `34a1` and `4cc2` too, which still fall through (`jmpf8_setup`, `jmpf8_flag`) | `jmpf8_goto_off`: STOP at `4c01`; `slit_pending` (the flag set): STOP at `4c08` (ALF shift, not modelled) |
| `setup.FORMS['enqueue_goal']`: the label in MDR1 (DFF 1, as `try_me_else`); the pop of R1b (ODPF 1, EMO1 b) with its head in MAR2 (ODSF 2, `ENQ_HEAD`) | INFERRED | the four DFF 1 entries all take a label; `4c00` copies MDR1 to W10 and `4c03` stamps it COD into cell 12; `4c00` reads [MAR2], `4c04` R1b := it, `4c05` R10 := `{HOOKo, old R1b}`. collect_list's ODSF 2 (read, not run) was read as MDR2: kept apart | `enq_head_mar1`: STOP at `4c00` (MAR2 never set); `enq_label_mdr2`: STOP at `4c04` (STALE written); `enq_label_plus1`: FAIL at instruction 3 (cell 12 one past `pimm.py`'s code) |
| `setup.EXECUTE_MDR1_EMO1`: execute's S stage puts R(10 \| EMO1) = R15 in MDR1 | INFERRED | EMO1 5 (rassy crr); `4cc0` R15 := MDR1 - 1, as `216d` and `4c02`. U2's run (no R15) keeps STALE | `execute_mdr1_stale`: STOP at the second pick, `216e` (crr STALE) |
| `u3_goals.INITIAL` R16 = 1 (*settled by the second step: R16 = 2 from `20a0`-`20a1`, the queue + 1*) | OPEN (two readings, both run) | R16 (rassy 'ccc') counts up at `4c06`-`4c07`, down at `2171`-`2172`; running out (`2173` -> `2174`) charges R15 to R13's record (`2177` calls `12e0`-`12ea`). Read as the queue's length: every R14 push in the image (census of the 21 R14 writers: `080c`-`080e`, `4c06`/`4c07`, `4c15`/`4c11`, `1f23`/`1f1b`) steps R16 too, `2170`'s empty test comes before the decrement, and the boot's `20a0`-`20a1` gives R16 = 0 with the R06 = 0 behind R14 = nil; then R16 = 0. Read as the foster parent's live goals (driver included): R16 = 1; a wake (`080e`) stepping R16 counts against it. The main run takes 1 (3 picks); a second pinned run takes 0 (`PINNED_R16_0`: 24 of 41, 1 pick, STOP at `12e3`). Undecided | `r16_zero`: STOP at the second pick, `12e3` (cond PMPF, a flag not given), as the second run |
| `u3_goals.INITIAL` R15 = 17 (*run held since the second step: `20a6`-`20a7` under PMPF reset*) | stand-in, cited `20a7` | crr: R15 - 1 at each enqueue, execute and proceed | `crr_two`: STOP at the first pick, `217c` (crr exhausted: PMPF) |

The comparison's own injections: `setv_addr_op` (set_value's
cell address from the operand) FAILs at instruction 0 on the cell
compare; `rec_poke` (the harness rewrites a record cell before the
enqueue) at 3 on the argument compare; `rfar_off` (U2's) at the first
pick on A0 and A2; `empty_int0` (initial R14 `{INT, 0}`) at 3 on the
link compare (the empty pick's own compare is therefore discriminated
only by the pinned stop `21b3`); `pg_swap` (the record map crossed
after the second enqueue) FAILs at the first pick on R10 and R14;
`free_undeclared` (the freed record's write not declared) FAILs at the
second pick (at the first, the pushed record's cell 0 is rewritten with
the value it already held, R1b's own link: no change to see).

Fields newly identified: CCF as rassy's value table (HELD-SOURCE; five
keys read differently from before); select d with WRBF (INFERRED); JMPF 8
outside set-up and flag words (HELD-SOURCE kind). Also met: R15 comes
out of `enqueue_goal` with tag GOAL (`4c01`'s TGIF 3 stamps the S1 load
into MAR1 as well as the ALU's `{GOAL, n}`); only its value is tested
(`216d`-`216f`, set_alf), so the tag is not discriminated.

## U3, second step: the boot held (2026-11-27, second session)

**The scheduler state is the firmware's from the start.** `u3_goals.py`
now runs start's own boot words before the driver (199 held words,
pinned per routine) and the first step's `INITIAL` stand-in is gone:
41 of 41 instructions executed and matched (173 held microinstructions),
3 picks, 2 compared with `pimm.py` and the third the boot goal's
(firmware only), no mismatch.

What the boot runs (`u3_goals.boot`), and what each part writes:

| Words | Writes | Replaces (first step's stand-in) |
|---|---|---|
| `2021` (entry `2001`'s word) | PMPF := reset | (the flag was not given: `209f` stopped) |
| `204b`-`2052` | R1f (unchanged from U2) | |
| `3380` -> `336b`-`3375` (R1b's refill, `2065`'s call) | 8 records of 16 cells carved from R1f, chained through cell 0, nil-ended; R1f += 80 | R1b's free list (NREC records) |
| `209f`-`20a8` | R11 := `{INTo, 36}`; R16 := `{INTo, 2}`; R15 := `{INTo, 17}`; W1f := 0 | R16 = 1, R15 = 17, W1f = 0 |
| `20e7`-`210b` (whole) | R13 := `{FPREC, record 0}` and its 16 cells; `[1a0 + 4f]` := R13; R12 := `{INTo, 0}`; R14 := `{HOOKo, record 1}`, the boot goal (`{GOAL, 0}`, code `{COD, 34}`, priority 0, parent R13, link nil); `[[b6]]` := R14 | R13, R12, R14 = nil |
| `202d`-`2030` | R10 := record 2 (`3349`) | R10 |

So 8 of 8 first-step stand-ins (5 `INITIAL` entries: R14, R12, R13, R15,
R16; plus R1b's list, R10 and W1f) are now written by held words; 0
remain. `boot_check` pins that R13, R14 and R10 are the refill's first
three records and the other five stay on R1b. The walk over every pick
finds no harness-written register or cell (the first step had R13 and
W1f); what the harness still gives is listed under "Still OURS" below.

**Held answers.** The boot's goal record means the firmware's queue is
never empty under the program: after the two appends, the third
`proceed` dispatches the boot goal (R04 := `{COD, 34}`, R10 := its
record, R14 := nil), where `pimm.py`'s queue is empty (Q). The pick is
counted apart and checked against the boot's own writes only; where the
firmware's link or R14 is the boot record and `pimm.py`'s is 0, the
compare takes it as the declared difference. The empty arm `21b2` is
therefore no longer reached in U3 (it still runs in `u2_append.py`'s
proceed side cases, empty queue with crr 8). R1b's refill links its
records `{VECT0x, next}` (the first) and `{REFo, next}` (the rest:
`3370`'s TGIF stamp); the first step's seed had VECT0x throughout.

**PMPF (the open item (a)): found, partly.** HELD-SOURCE:
- the name and number: rassy's condition list position 26 (`cond PMPF`,
  CNDF 7 EM1 `1a`) and its flag tables `reset_PMPF` / `set_PMPF` 26
  under MCF sub-switch keys 2 / a (`ptfdump.py pimmutil rassy --pairs`);
- the writers, by a scan of image 2 (MCF EM1 02 / 0a with EM2 & 1f =
  1a): `2014` and `2021` reset, `2022` set, `68e2` reset. The first three
  are the firmware's entry vector `2000`-`2004`: `2000` jumps to `200b`
  (cold start; `2014` resets PMPF on its way), `2001` to `2021` (reset),
  `2003` to `2022` (set), both then `2023`; no held word of image 2 or
  `syspsi` branches to `2001` or `2003` (flow-target scan), so the entry
  is chosen from outside;
- the CSP (Pseudo PIM/m `pimmcsp.ptf`, PRINTED strings): "$GO/PIMos
  <Start Address> ... <Start Address> = 2000 (Multi-PSI) ... = 200
  (Pseudo MPSI)", and `$GO` takes a "Micro Start Address" on the
  Multi-PSI, a "KL1 Start Address" on the Pseudo MPSI.

INFERENCE: PMPF is the Pseudo-Multi-PSI flag ("PMP" is PIMM.PARAM's own
abbreviation, `pmp_ncas` "PMP Network Comm. Area Size"). Its two arms at
`209f`-`20a7` fit: set, crr (R15) is read from the cell `10 +` start's
operand a (a per-PE reduction limit, as the CSP's pseudo-PE scheduler
prints "Reduction Limit = "); reset, crr := 17. NOT established: which
entry the held system's Pseudo MPSI start takes (no held source names
`2001` or `2003`). The harness takes the reset (`2021`; the Multi-PSI
cold start `2000` resets too), OURS, and pins the other value as a
second run: entered at `2003` (`2022`), the boot stops at `20a3`, the
read whose address is start's operand (STALE).

**R16 (the open item (b)): settled by held words.** `20a0` puts
`{INTo, EM2}` = `{INTo, 2}` in XR (SC1F 6 is the EM2 immediate,
`pu.S1_IMM`) and `20a1` moves it to R16; the same boot queues exactly
one goal (`2104`). So R16 = the queue's length + 1: the goal about to
run (the boot module's first goal; here the driver) counts. Checked
after the boot and after every `enqueue_goal` and `proceed`
(`r16_check`): it holds throughout. The first step's "queue length"
reading (R16 = 0) is refuted, and the README's earlier "`20a0`-`20a1`
gives R16 = 0" (read before `S1_IMM`) is withdrawn. The foster parent's
record cell 3 is `{INTo, 2}` as well (`20ef`, the EM2 immediate):
noted, not tested. The pinned R16 = 0 second run is retired; the
injections `r16_zero` and `r16_plus1` (post-boot rewrites) FAIL at the
boot check.

**R13 and W1f (the open item (c)).** Both are now written by the boot
(`20eb`, `20a8`); `RESIDUAL_PINNED` is empty at all three picks.

**Still OURS** (each read by the boot or the program, from the walks):
the entry choice (`2021`); the parameter cells `1a0 + 4a` (the heap top,
`pimm.py`'s heap pointer as U2), `a0` (`{INT, 0}`, meaning not read) and
`b6` (`GSEB`: PIMM.PARAM's `gseb` (10 : 16'B800) taken as area << 24 |
address, INFERENCE on the encoding; the boot uses `[b6]` as an address,
so `b6` holds the table base, where the first step's "b6 / b7 = gsesh /
gseb by place" put the shift count first); start's cell and its operand
A0 (STALE; `20a1` reads it, `20a6` overwrites what it fed); R0d (STALE,
`3375`; since U3d W1c, `3375`'s select d read as W(EM1)); which of start's calls run (2053's other refills, `2070`,
`208e`, `209f`'s tail `20a9`-`20c0`, which reads cells `b8` / `ba`, and
`20c2` are not run). Unchanged from U2 / the first step: the A stage,
the driver's A0-A5, the cell lists R19 / R1a, `pimm.py`'s memory cells.

Rules decided in this session (each in `pu.py`, its injection in
`u3_goals.py`, observed):

| Rule | Status | Evidence | Injection (observed) |
|---|---|---|---|
| `FLAG_CONDS[0x1a]` = PMPF | HELD-SOURCE (name, number); INFERRED (that it is the flag the MCF words write) | rassy position 26; formed at `209f`, tested at `20a1` | `pmpf_cond_off`: STOP in the boot, `209f` |
| `MCF_SUB_FLAGS`: MCF EM1 02 / 0a with EM2 & 1f = 1a resets / sets PMPF (only key 1a admitted) | HELD-SOURCE (rassy sub-switches), INFERRED (one flag for both lists) | `2021` executed (and `2022` in the second run) | `mcf_pmpf_off`: STOP at `2021` |
| `CJUMP_TAKEN_ON[0xc]` = False: JMPF c is "goto short if not cond" | HELD-SOURCE (rassy jmpf/9 arm c, the 'if not cond' slots) | `20a1`: taken under PMPF reset (to `20a6`) | `c_on_true`: STOP at `20a3`, as the second run |
| `RULES['sc2_wide_mcf']`: a wide (SC2F b) word whose EM1 MCF consumes is EM2:EM3 | INFERRED (as the stamp case) | `20a8` (YR := b8, MCF EM1 07); 6 such words in image 2 | `wide_mcf_off`: STOP at `20a8` |
| `RULES['alu_with_one']`: ALU add_with_one (rassy EM2 3) is a + b + 1 | INFERRED (the name, HELD-SOURCE) | `3370`: the refill's links land on the next record's cell 0 (16-aligned chain) | `with_one_plain` (a + b): FAIL at the boot check (R10 STALE, the list broken) |
| `CCF_RASSY[0x04]` 'wait': no memory operation | INFERRED (the name) | `202f` (R10 := MDR1 after the pop); 7 words in image 2 | `ccf_wait_raise`: STOP at `202f` |

Checks added, each discriminated: `boot_check` (`empty_int0`,
`with_one_plain`, `r16_*`), `r16_check` (`r16_zero`, `r16_plus1`), the
boot walk and the program walk (`r13_harness`: R13 at all three picks
and in the program walk, no STOP or FAIL, caught by the pins only).

**Injection shifts, re-diffed against a clean snapshot of c6c048bf**
(every injection of `u3_goals.py`, `u2_append.py`, `check_pu.py` and
`measure.py`, 111 runs before, 121 after): `check_pu.py` and
`measure.py` unchanged; `u2_append.py` changes only in stop messages at
the same words (`a_on_false`, `const_em3`: the side cases' `217c` stop
is now "flag PMPF, value not given" instead of "condition UNKNOWN";
`empty_fw_goal`, `empty_int0` likewise; `cjump_false`, `slit_pending`:
`4cc6`'s JMPF c is now polarity-decided and stops on its STALE
condition instead). In `u3_goals.py`: `ccf_bits` and `jmpf8_goto_off`
now change their rule after the boot (same stops as before, `2250` and
`4c01`); made before the boot they stop in it (`ccf_bits_boot` at
`334e`, `jmpf8_goto_off_boot` at `3370`); `free_undeclared` FAILs at the
first pick (was the second: the refill's cell 0 differs from the push's
value); `crr_two` stops at `217d` (was `217c`); `empty_int0`, `r16_zero`
FAIL at the boot check (were INITIAL edits); the R16 = 0 second run is
gone. Every other injection is unchanged.

**Append's pin stays at 15 of 16.** In U3 append's `proceed` runs at
picks 2 and 3 on state written only by held words (the pick walk is
empty), but `u2_append.py`'s standalone run still seeds the scheduler
(`seed_proceed`, OURS) and is unchanged. Run after the boot, the
standalone append's `proceed` would dispatch the boot goal while
`pimm.py` ends (Q): a firmware-only pick, not a comparison. Whether that
counts as the sixteenth instruction is left to the owner.

**`pimm.py`'s `sp_single` for lists (the open item (d)): tried, not
landed.** Setting `sp_single` in `wait_list` and `switch_on_non_list`
from the list pointer's MRB (as `wait_vector` does) makes the `[b, c]`
program match on the held firmware (52 of 52, 2 picks compared, the
boot goal's pick; without it FAIL at instruction 12, `read_variable`,
reg 4 LISTo against LISTx). But the full suite's `pimm lockstep shoen`
then FAILs at part 0, trace line 185 (`R 3`: the changed reference
model `04e0008047`, unmarked, against the Bluespec core's `05e0008047`): the
Bluespec `PimmCore` implements the old rule and runs in lockstep with
`pimm.py`. The change needs the core changed with it (outside this
rung), so it was reverted; the patch is described here so the core's
owner can take both together.

## U3, third step: suspend and resume held (2026-11-28)

**A goal suspends, is woken by a binding and runs to its end, all on
held micro-routines.** `u3_goals.py` runs a second program, `suspend`:
the driver clause `driver([], [], X, X, [], Z)` (OURS input) enqueues
`append(X, [], Z)` and `append([], [], X)`. The first suspends on the
unbound X, the second binds X to nil and wakes it, the woken goal runs
to its end, then the boot goal. Of `pimm.py`'s 23 instructions, 22 are
executed and matched, and 1 is skipped as a declared difference
(`guard_to_alt`, below). That is 225 held microinstructions after the
boot's 199. There are 4 picks: 3 compared with `pimm.py` (the first goal,
the second at the suspend, and the woken goal at the second goal's
`proceed`) and the boot goal's (firmware only). `main()` pins it as a
second run (`SUSP_PINNED`). The `append2` run is unchanged: 41 of 41,
173 words.

**The held path, routine by routine.**

- **Noting (inside `switch_on_non_list`).** The S stage's
  through-pointer row 5 (`3314`; `setup.S_CHAIN_ROW` from Fig. 3-23's
  two chain reports) runs `2447` -> `2444` -> `24b1` -> `3a34` -> `3a33`
  -> `3a3c`-`3a3f`. This is the first noting: R18 (sst) := `{REFx, X}`,
  R17 (ssp) := `[b4] - 1` (sspb - 1, the empty stack), and SUSPF is set.
  R04 := R11, the alternative. That is the `suspend` instruction (6658).
- **`suspend`** (`1c08`-`1c81`, 54 words). It re-uses the running goal's
  record R10:
  - cell 0 `{GOAL, 3}`;
  - cells 1-3 are A0-A2, copied by the counted `1c2c`-`1c32` loop on
    `++ rfar`;
  - cell 12 `{COD, label}`, cell 13 R12, cell 14 R13, cell 15 nil.

  `1c60`-`1c66` compare sspb with ssp and take the single-waiter case.
  `1c70`-`1c81` write X := `{HOOKx, record}`, whose MRB is that of the
  noted reference (`1c66`'s tag0 of R18, tested at `1c80`). The record
  `1c09` popped goes back on R1b (`2209` -> `339f`). Then the pick
  (`220a`-`2224`) dispatches `append([], [], X)`.
- **The wake (`get_value`, 48 words).** `0867` -> `0a5c`-`0a5e` bind X to
  `{ATOMx, 0}`. `0a24` -> `0b20`-`0b23` walk the waiters. `4d1a`-`4d1e`
  find the GSET entry of the woken goal's priority (its cell 13) and of
  the current one (R12) through `4d38`/`4d3a`. With `[b6]` gseb and `[b7]`
  gsesh this is entry `[b6] + (prio >> [b7]) << 2`. The two are equal
  (priority 0), so the record is pushed on R14 (cell 15 := the old R14,
  the boot record). The next `proceed` dispatches it (pick 3).
- **The resumed goal.** It runs `try_me_else` and `switch_on_non_list`
  (row 5 again, now on nil through the REFx: COND false at `2440`, to the
  label), then `wait_nil`, `get_value` and `proceed` (pick 4: the boot
  goal).

**Compared, and declared** (`u3_goals.cmp_suspend`, `cmp_wake`,
`cmp_pick`):

- **The suspension record**, projected on `pimm.py`'s structure, cell by
  cell. Its arity, arguments and code (G_ARGN, G_ARGS, G_CODE) are
  compared against the firmware's cells 0, 1-3 and 12. X is checked as
  `{HOOK, record}`, with the MRB of the goal's argument, against
  `pimm.py`'s hook chain, every entry of which is the goal. Nothing else
  may be written, and R1b must be given back.
- **Declared at the suspend.** `pimm.py` writes a new record, its status
  and link cells, and one hook cell per noting. It notes X twice
  (`switch_on_non_list`, then `wait_nil`); the firmware notes it once
  (`double_hook_undeclared` FAILs). The firmware's cells 13-15 are checked
  against its own registers.
- **Declared: `guard_to_alt`.** The firmware's guard fails to the
  alternative at once (R04 = R11). `pimm.py` jumps to the label and fails
  the next guard on the same variable. Each `pimm.py` step skipped is a
  guard that writes nothing (`guard_alt_undeclared` FAILs).
- **The wake.** Every `pimm.py` M line except the woken record's own
  cells is compared. The woken record must head R14, its link must be the
  old R14 (`same_link`: the boot record where `pimm.py`'s queue is empty),
  and A0-An-1 must be unchanged.
  - Declared: `pimm.py`'s status cell, and the MRB of the bound atom. The
    firmware writes `{ATOMx, 0}` through a REFx; `pimm.py` keeps an MRB on
    pointers only (`atom_mrb_undeclared` FAILs).
- **Declared: `deref_reg`.** A guard that dereferenced its register
  leaves the end of the chain there, MRB off. The resumed
  `switch_on_non_list` writes A0 := `{ATOMo, 0}`, where `pimm.py` keeps
  the REF (`deref_reg_undeclared` FAILs).
- **R16 (ccc)** is checked after the boot, at every `enqueue_goal`,
  `proceed`, `suspend` and wake. It now counts the queue + 1 + the goals
  suspended: suspend's held path leaves the count alone (R16 = 3 with one
  goal queued), read as ccc counting live goals (INFERRED;
  `r16_queue_only` FAILs at the suspend).

**Provenance.** The pick walks are empty at picks 1-3. What the suspend
and the wake read whose last writer is the harness is pinned
(`SUSP_RESIDUAL_PINNED`):
- the suspend reads cell `b4`;
- the wake reads cells `b6` and `b7`.

Every other instruction of the program reads R17, R18, R19, `b4`, `b6`
and `b7` (`SUSP_PROG_RESIDUAL_PINNED`):
- **R17 and R18** are STALE (OURS, `SUSP_STALE`). No boot word writes
  them. `3a33`/`3a3c` read them before `3a3e`/`3a3f` write them, and
  nothing tests `3a3c`'s STALE compare.
- **R19** is `check_pu.seed_lists`' cell list, read by `wait_nil`'s
  `3980` as in U2.
- **The parameter cells are OURS values:**
  - `b4` = sspb (PIMM.PARAM `(10 : 16'400)` as area << 24 | address,
    INFERENCE on the encoding). It is discriminated: `sspb_zero` makes
    ssp `ffffffff` and takes the many-variable path, stopping at `3334`.
  - `b7` = gsesh (`16'18`). It is not discriminated, because the priority
    is 0.

The A file's provenance is now tracked too (`Prov.commit`).

**Rules decided in this step** (`pu.py` / `setup.py`; the observed
injection result follows each one, from `--inject`):

| Rule | Label | Decided at | Injection: observed |
|---|---|---|---|
| `setup.S_CHAIN_ROW`: row 4 \| (SRP false) \| COL << 1 | INFERRED (reports DOCUMENTED, Fig. 3-23) | `3314` (rows 5) | `chain_row_off`: STOP 10 (row UNKNOWN); `chain_row_srp`: unchanged (WEAK: 3310's CNDF 9 is false too) |
| `setup.S_CHAIN_MAR1_PTR`: MAR1 = the last pointer, tagged | INFERRED | `24b1`, `3a34` | `chain_mar1_bare`: FAIL 10 (A0 untagged) |
| `cnd_noalu_poison` 'zero': CNDF 2 / 3 with no ALU are zero true / sign false | INFERRED | `3314` -> `2440` (resumed switch) | `cnd_noalu_poison`: STOP 19 at `2440`; `cnd_noalu_raise`: STOP 10 at `3314` |
| `MCF_SUB[(02, 4)]` f_jump, no state | HELD-SOURCE (name) | `3a34` | `f_jump_raise`: STOP 10 at `3a34` |
| `SUSP_FLAG_OPS` 'usage': MCF 07 / 0f reset / set SUSPF, 06 / 0e CGCF; conds 13 CGCF, 14 SUSPF | INFERRED (rassy's lists pair them the other way) | `3a3e`, `1c60`, `1c0f` | `susp_flags_rassy`: STOP 10 at `3a41` (STALE) |
| `FLAG_CONDS[20]` interrupt, false (OURS value) | HELD-SOURCE (name) | `1c0d` (JMPF b) | `interrupt_pending`: STOP 12 at `1c18` |
| `jmpf8_goto_cndf`: JMPF 8 goto if COND in a CNDF 2 word | INFERRED | `3a3c` | `jmpf8_cndf_off`: STOP 10 at `3a3c` |
| `sc2_a_imm`: SC2F a (WRBF clear) = EM2 << 4 \| EM1 | HELD-SOURCE (consumes EM1 and EM2), INFERRED (layout, census) | `3a3c` (b4) | `sc2_a_opd`: suspend STOP 12 at `3334` (ssp = ffffffff); append2 MOVED (boot residual gains A00) |
| `ALF_LATCHED` alf_high: a above b, unsigned | INFERRED (name) | `1c2e`/`1c2f`, `1c64` | `alf_high_reversed`: STOP 12 at `1c36`; `alf_high_signed`: unchanged (sspb positive) |
| `src_c_rfar`: SC1F/SC2F c reads A[rfar], RFAR stepped | HELD-SOURCE (name list), INFERRED | `1c30` | `src_c_rfar_off`: STOP 12 at `1c30` |
| `em1_28_s1_mrb` / `em1_28_s1_read`: cond tag0 = the S1 value's tag bit 0 (read for the condition alone) | HELD-SOURCE ('cond tag0'), INFERRED (S1) | `1c0e`, `1c66` -> `1c80` | `em1_28_false`: FAIL 12 (X `{HOOKo, record}`); `em1_28_read_off`: STOP 12 at `1c66` |
| `long_em1_free`: JMPF 3/6/7/b/e/f leave EM1 free (long/4) | HELD-SOURCE | `4d1b` | `long_em1_busy`: STOP 16 at `4d1b` |
| `adf2` 'yr': ADF 2 is YR | INFERRED | `4d1b`-`4d1e` | `adf2_none`: STOP 16 at `4d20` (the GSET path: SC2F b with CNDF 9's EM1, width UNKNOWN); `adf2_pair`: STOP 16 at `4d3e` |
| `sc2_e_em2`: SC2F e (WRBF) = R(10 \| EM2) | HELD-SOURCE (names, em2_not_free), INFERRED | `4d1c` | `sc2_e_off`: STOP 16 at `4d1c` |
| `alu_gset`: reverse_sub b - a, shift_right_32m by 32 - b, shift_left (at `4d3d`) | HELD-SOURCE (names), INFERRED | `4d3b`-`4d3d` | `gset_ops_off`: STOP 16 at `4d3b`; `reverse_sub_plain`, `shr_by_b`: unchanged (priority 0, not discriminated) |

**Declarations and checks** (`u3_goals.py`, observed): `guard_alt_undeclared`
FAIL 10 (R04 against `pimm.py`'s next instruction); `double_hook_undeclared`
FAIL 12; `atom_mrb_undeclared` FAIL 16; `deref_reg_undeclared` FAIL 19;
`r16_queue_only` FAIL 12 (R16 3, queue 1 + 1); `sspb_zero` STOP 12 at
`3334` (the many-variable path). 24 of the 28 new injections move the
suspend run; the 4 that do not (`alf_high_signed`, `chain_row_srp`,
`reverse_sub_plain`, `shr_by_b`) are recorded as not discriminated.
Every new injection leaves `append2` unchanged except `sc2_a_opd`.

**Existing injections re-diffed** against a clean 03fb0ffd snapshot (all
145 outputs of `check_pu`, `u2_append`, `u3_goals`, `measure`):
`check_pu` and `measure` are unchanged. In `u2_append`, `cnd2_nonzero`
and `deref_tgt_col5` now FAIL where they stopped on 'MCF with EM1 02'
(f_jump), and `interrupt_pending` stops at `1c31` (was `1c2f`).
`mcf_unknown_raise` also turns `susp_flags` off, and is otherwise
unchanged. In `u3_goals`, the append2 part of every output is unchanged
except `c_on_true`, which stops at `20a4` (was `20a3`; `sc2_a_imm`), and
the wording of the R16 lines ('+ 0 suspended'). Each output now also
carries the suspend run.

**Tried and withdrawn.**
- **A signed `alf_high`.** It was needed while `3a3c`'s SC2F a read A0
  (R17 = `[X] - 1` = `ffffffff`); `sc2_a_imm` made it unnecessary.
- **SC2F b with an EM1 condition (CNDF 9).** It was met at `4d20`, on the
  GSET path that `adf2` 'yr' no longer takes.
- **The boot's 4-cell refill (`3384`) and a step/load rule at `3367`.**
  They were needed only by the many-variable path (`1d3a`).

**The PMPF-set run** now stops at `20a4`: `20a1`'s SC2F a gives b0, and
`20a3` reads parameter cell b0, the reduction limit, which no harness
gives. Before, it stopped at `20a3` on start's operand a. Start's operand
A0 is no longer read by the boot.

**Not reached:**
- the many-variable path (`1d20`-`1d61`: the suspension stack walked from
  sspb, a MHOOK record per variable, the 4-cell allocator `3334`);
- a woken goal of another priority (`4d1f`-`4d23`, the GSET entry and
  W1f's bit);
- a wake of several goals;
- `sp_single` (not needed by this program).

## U3d, first step: a compiled KL1 program to its answer (2026-11-28)

**A program compiled by the held PIMOS compiler runs on the held firmware
to its answer, and the answer is `pimm.py`'s.** The program is a producer
and two consumers of one stream (`u3_goals.STREAM_SOURCE`, 7 lines, OURS):

    :- module pc.
    :- public go/3.
    go(L, A, B) :- c(S, A), c(S, B), g(L, S).
    g([], S) :- S = [].
    g([X|L], S) :- S = [X|S1], g(L, S1).
    c([], R) :- R = [].
    c([X|S], R) :- R = [X|R1], c(S, R1).

It was chosen because it is the smallest program that needs what U3 had
not run: a second goal suspending on a variable another goal already
waits on, and one bind waking two goals. nrev was rejected: its compiled
body is `enqueue_goal append; execute nrev`, and with a newest-first queue
each `append` is picked only after its input is bound, so it never
suspends (seen on `pimm.py`).

**The code is the compiler's, not ours.** PIMOS 3.6's KL1 compiler
(`library/compiler`) ran on `pimm.py` from the prompt checkpoint with
the lines `compile`, `!package work`, `pc`, `!exit`, as R7 / R8 compile.
It answered `Compile Succeeded : pc` and `"work:: pc" Loaded`. The module
`work::pc` has 62 cells. Its cells 15-61, the code of the three
predicates, are pinned as `u3_goals.STREAM_CELLS`, 47 cells with their
disassembly. The descriptor (cells 0-14) is left out: it holds an
absolute pointer.

`ref/pu/u3d_compile.py PROMPT.pkl` makes them again and checks them. It is
out of the suite because it needs the 1.1 GB checkpoint (md5
`75c7b1c62509fdf1d6926b0719f10dc5`); it takes 30 s and 0.97 M `pimm.py`
instructions. It checks the cells are position free: `go([1], A, B)` and
`go([1, 2], A, B)` at two placements give the same answer and the same
counts. Observed: PASS.

The compiler made three choices of its own:

- `g` and `c` compile to the same code;
- `go`'s body enqueues `g(L, S)`, then `c(S, B)`, and executes `c(S, A)`;
- `S` is made by `set_marked_variable`.

**The run** (`u3_goals.py`, third program, `go([1], A, B)` after the
199-word boot):

- **The consumers suspend.** `c(S, A)` suspends on S (`1c70`-`1c81`, as in
  U3's third step). Then `c(S, B)`, dispatched by that suspend, notes S,
  which is now `{HOOKx, record}`, and suspends too. This is new held
  code: `1c66`'s tag case takes `1c73` on the HOOK, and `1c82`-`1c83`
  write the new record's cell 15 := the variable's old hook. `1c86` /
  `1c81` then write S := `{HOOKx, new record}`. So the waiters are a chain
  of goal records linked through cell 15, newest first: the ready
  queue's own link. No new rule was needed for this.
- **The producer binds S and wakes both.** `g([1], S)` runs, and its
  `get_bound_value 1,6` binds S to `[1|S1]` (67 words: `3894` row 5,
  `0cd4`, `0c0a` -> `0c60`, the unifier, then the wake path `4d1a`-`4d1e`
  twice). The two woken records go on R14 in the order `pimm.py` gives:
  the oldest waiter is the head. No new rule was needed for the wake
  order either.
- **To the end.** The producer runs on to its end. Then the two
  consumers run, one after the other, to theirs. The second takes the
  stream the first has re-stamped. Then the boot goal runs.

**Counts** (`STREAM_PINNED`):

- instructions: 68 on `pimm.py`, 64 executed and matched, 4 skipped as
  declared (`guard_to_alt`);
- 407 held microinstructions after the boot;
- 5 picks, 4 compared with `pimm.py`, and the boot goal's;
- 2 suspends, and 1 bind that wakes 2 goals;
- the answer, read out of the firmware's memory by `fw_term`:
  `A = [1], B = [1]`, `pimm.py`'s.

The append2 and suspend runs are unchanged (41 of 41, 22 of 23 + 1),
except their boot residual (R0d -> W1c, below).

**Rules decided in this step** (`pu.py` / `setup.py`; the observed
injection result follows each one, from `--inject`, on the stream run):

| Rule | Label | Decided at | Injection: observed |
|---|---|---|---|
| `pu.RULES['wsel_d_w_em1']`: select d (DSTF, SC1F) with WRBF clear names W(EM1), EM1 10-1f; EM1 under 10, or EM1 used by another field (`pu.em1_other_field`), raises | INFERRED (census) | `3894` (W18 := MDR2, the value; `0c0a` reads W18 back after the call), `3375` (boot: W1c, read into w2 and unused) | `wsel_d_w_off` (R0d again): STOP 24 at `0c0a` (W18 never set); append2 and suspend MOVED (boot residual) |
| `setup.S_CHAIN_ODPF4`: S_CHAIN_ROW's rows (4 \| (SRP false) \| COL << 1) for an ODPF 4 entry reached through pointers on another tag | INFERRED | `get_bound_value` on `{REFx, S}`, S hooked: row 5 (`3894`) | `chain_odpf4_off`: STOP 24 (row UNKNOWN) |
| `setup.S_CHAIN_MATCH`: on the immediate's side, an ODPF 6 operand reached through a chain with an MRB on takes row 1 \| COL << 1 | INFERRED | the resumed consumer's `switch_on_non_list` on `{REFx, S}`, S a list: `3304` (A0 := `{LISTx, cell}`) | `chain_match_off`: FAIL 35 (the entry `3300` -> `3305`-`3309` frees S's cell, which the other consumer still holds) |
| `setup.S_TDAR_ODPF3`: the ODPF 3 start loads TDAR from the TGT, column 7 - TDPF, as S_TDAR | INFERRED | `put_reused_structure` on a shared list: `31ee` -> `31a1`'s case_branch -> `31a4` (the R1a pair list) | `tdar_odpf3_off`: STOP 38 at `31a1` |
| `FORMS['read_variable_without_deref']` = read_variable's (MAR1 := R02) | OURS (`pimm.py`'s reading), support `345a` | `345a` | `rvwd_form_arg`: FAIL 19 |
| `FORMS['wait_atom']` (the register in the opcode's low 5 bits), `S_CONST` MDR2 := the atom | OURS, support `3960` (MDR1 - MDR2) | `3960` | `wait_atom_plus1`: FAIL 31 (R04); `wait_atom_own`: unchanged (the operand is the constant here): NOT discriminated |
| `FORMS['get_nil']` (x) | OURS, support rows `3820`-`382e` | `3820` | `get_nil_form_y`: STOP 32 at `0d22` |
| `u3_goals` boot: W1c STALE | OURS (stand-in, replaces R0d) | `3375` | `w1c_unset`: STOP in the boot at `3375` (all three runs) |

For `wsel_d_w_em1`, the census of image 2 is as follows (scratch, every
word):

- **DSTF-d words with WRBF clear:** 47 of 47 carry EM1 10-1d (34 of them
  admitted by `em1_other_field`).
- **SC1F-d words with WRBF clear:** 151 of 152 carry EM1 10-1f (122
  admitted). The exception is `32d2`, EM1 09.
- **With WRBF set:** all 4 DSTF-d words and all 62 SC1F-d words carry
  EM1 0-f (`wsel_d_em1`).

Two words are executed through the new branch: `3375` and `3894`. Read,
not run: `3888` (row 2's W18 :=) and `0cf8` (W1d, which `3889` writes).

No word now reads R0d on any path run: `4cc0`'s select d is SC2F, the
EM3 immediate. The "47 writers" of R0d that `u2_append` counted are
these DSTF-d words.

**Declarations and checks in `u3_goals.py`** (observed):

- `guard_to_alt` now also skips the next clause's `try_me_else` when its
  alternative is the firmware's R04 (`RETRY_SAME_ALT`; the compiled code
  puts one between the switch and `wait_atom`). `guard_alt_retry_off`:
  FAIL 8.
- `cmp_suspend` takes a variable with waiters already. Cell 15 must be
  the variable's old hook (`chain_link_nil`: FAIL 16). The firmware's
  chain, followed through cell 15, must be `pimm.py`'s hook list with
  each goal once (`waiters_raw`: FAIL 11; it also moves `suspend`, whose
  `pimm.py` hooks X twice).
- `cmp_suspend` also checks the variable through the address renaming,
  and declares a given-back record's cell 0 restamped `{VECT0x, the same
  link}`, as proceed's freed record. `free_undeclared` now FAILs at 11.
- `cmp_wake`: the woken records are walked in `pimm.py`'s W order. The
  third step's loop ran reversed, which is right for one waiter only
  (`wake_loop_reversed`: FAIL 24). The heap is compared through the
  renaming.
- `cmp_set_variable`: `set_marked_variable`'s record cell against
  `pimm.py`'s argv, which pairs the new variable cells (`setvar_form_op`:
  FAIL 1).
- **Declared: `read_indirect`.** U1's `indirect` (`write_variable`'s
  `{REF, new cell}`) met again by a reader of a shared structure. The
  firmware's register is `{REFx, new cell}` and the element is re-stamped
  MRB on in place; `pimm.py` takes the value. `read_indirect_undeclared`:
  FAIL 37. It is carried by copies (`put_value`):
  `read_indirect_carried_off`: FAIL 42.
- **Declared: `mrb`.** U1's declaration, met in `put_reused_structure`
  on a shared list. The firmware takes two new cells and gives x the
  pointer MRB off; `pimm.py` gives it MRB on. The two structures' cells
  are paired one by one. `fresh_mrb_undeclared`: FAIL 38. It is carried
  by copies: `fresh_mrb_carried_off`: FAIL 41.
- `put_reused_structure` always sets sp (`SP_SET_REUSED`): the new cells
  lay where the old sp pointed. `sp_set_reused_off`: FAIL 38.
- `deref_reg` also accepts the end MRB on when the chain had an MRB on
  (`pimm.py`'s deref marks so; `3304`). `deref_reg_marked_off`: FAIL 35.
- The answer: `answer_poke` (the car of A's list 2 after the run): FAIL
  at the answer.

**Provenance.** The pick walks are empty (`STREAM_PICK_RESIDUAL_PINNED`).
What the suspends and the wake read last written by the harness
(`STREAM_RESIDUAL_PINNED`):

- the first suspend reads A01, `go`'s A (the program's input, OURS, as
  the driver's arguments), and `b4`;
- the second suspend reads `b4`;
- the wake reads `b6` and `b7`.

The rest of the program reads (`STREAM_PROG_RESIDUAL_PINNED`):

- R17 and R18 (STALE);
- R19 and R1a, and the seeded cells `f2000000`-`f2000003`, `f3000000` and
  `f3000002` (`check_pu.seed_lists`). R1a is new: the consumers'
  `put_reused_structure` takes pairs from it;
- `b4`, `b6` and `b7`.

The boot residual is now W1c (was R0d) for all three runs.

**Open tension, recorded:**

- `S_CHAIN_MATCH` is applied only when SRP is false. With SRP true,
  `switch_on_non_list` and `wait_nil` free the same cell whether row 0
  (COND false) or row 2 is taken. For `get_nil` (`3828`),
  `get_bound_value` (`3888`) and `get_value` (`38a8`), however, row 2
  first calls `0cf1` / `0cf0`, a walk that frees a pointer cell.
- The stream run takes row 0 through a REFo at `get_nil` (instructions
  32, 49, 66) and at `get_bound_value` (41, 58). `pimm.py` frees nothing,
  so this is NOT discriminated.

**Re-diff of the existing injections** against a clean 3901e926 snapshot:
the outputs of `check_pu.py`, `u2_append.py`
and `u3_goals.py` under the 145 injections that existed, compared by
content (the new stream section cut, R0d -> W1c in the boot residual
normalised): 140 unchanged, 5 changed, each still caught:

- `u2_append em1_29_off`: was STOP 4 at `31a1` (case_branch without a
  set-up), now FAIL 6 at `write_variable` (`S_TDAR_ODPF3` gives `31a1`
  its set-up);
- `u2_append em_imm_off`: the 216d stops now say "select d with EM1 01
  not decided" (was "R0d never set"); the append run stops at 10, `4cc0`
  (EM1 19 then used by another field), where it stopped at 15;
- `u3_goals chain_row_srp`: append2 and suspend unchanged, stream STOP
  24 at `0c74` (row 4 for row 5): no longer WEAK;
- `u3_goals double_hook_undeclared`: the message only ("once per goal");
- `u3_goals with_one_plain`: still FAIL at the boot check; R10 now reads
  `{HOOKo, e000804f}` where it read STALE.

On stream, 49 of the 55 existing `u3_goals` injections move it; 6 leave
it unchanged (`alf_high_signed`, `atom_mrb_undeclared`, `enq_head_mar1`,
`rec_poke`, `reverse_sub_plain`, `shr_by_b`), each already caught on
append2 or suspend, or recorded weak there.

**Not reached** (the program does not need them):

- `execute`'s slit check `4cc5` and the goal switch `4c11`: no event is
  pending on one PE, and the flags are not forced;
- the many-variable suspend (`1d20`-`1d61`, the 4-cell allocator `3334`);
- a woken goal of another priority (`4d1f`-`4d23`);
- `sp_single`: the consumers read a shared stream, met as the declared
  differences above, and `pimm.py` and PimmCore are unchanged.

## U3d, second step: the held paths U3 had not run (2026-11-28)

Three paths that the first step did not reach, each driven by a program
compiled by the held PIMOS 3.6 compiler on `pimm.py`. The sources are
OURS. `u3d_compile.py` re-makes each program's cells, each on a fresh
load of the prompt checkpoint, and checks them; the runs are in
`u3_goals.py`. **None of the three runs to its end.** Each stops,
pinned, at the first word that no held source or decided rule carries
further. No scheduler state is seeded. The stops:

| path | program (`u3_goals`) | held words executed | pinned stop |
|---|---|---|---|
| (a) crr run out in `execute` | `slice`: `go(A) :- b(A), a` x 15 | 15 `enqueue_goal`s (the 5th's refill `4c0b` -> `3380`, 141 words, declared), then `execute` at crr 2: `4cc0`-`4cc2`, `4cc4`, `4cd3`, `4cf4`, `1c2c`-`1c32`, `4cf6`-`4cf7`, `4d02`, `4d00`-`4d01`, `4cd4`, the goal switch `4c11`-`4c12`, `4c25`-`4c2e`, `4c13`-`4c15` (31 words) | cell 33: `4c15` ends with R04 = 33 (`4d00`-`4d01`) and nothing writes that cell or gives it |
| (a) crr run out in `proceed` | `crr_proceed`: `go(A) :- a` x 11`, b(A)` | 3 proceeds that pick; the 4th at crr 1: `216d`-`217d`, `217d`'s JMPF d calls `219b`, `219c` makes 10, and `219e` reads it | `219f`: cell 10 (area 5's Extended Control Registers, constant area) was never written |
| (b) suspend on two variables | `twovar`: `p([], _, A)`, `p(_, [], A)`, `q(X, _)` | the first `wait_atom` notes X (`3978`-`3979` -> `3950` -> `3a38`-`3a3f`); the second notes Y and pushes X onto the suspension stack (`3a3c`, `3a41`-`3a43`, `[10000400] := X`, declared); then `suspend` runs `1c08`-`1c10` and `1c60`-`1c65` (stack not empty), the many-variable path `1d20`-`1d21`, `1d3a` "call 3334", and the allocator `3334`-`3336` | `3343`: cell 1a4 (size 4 in a table at 1a0, area 5's MPQ) was never written |
| (c) another priority | `prio`: `q(X)@priority(*, 100)` | `put_integer`, then the builtin `calculate_priority_from_minimum` (entry `1dda`): `1dda`-`1de6` (range check, cells 9 and 10 of R13's record, the shoen's range, written by the boot), "call 1d92", `1d92`-`1d93` | `1d94`: CNDF 1, rassy's "cond carry", whose value for that ALU operation no rule gives |

Of the words the brief names, these ran: `4c11` and `3334`, plus
`1d20`-`1d21` and `1d3a` of `1d20`-`1d61`. These did not: `4cc5`,
`1d22`-`1d61` and `4d1f`-`4d23`.

- `4cc5`, execute's slit-check arm, is reached only with slit_check set.
  Seven held words set it (`W1f |= mask` with `set_slit_check`, all EM2
  19). On the paths run, `21a1` sits behind cell 10 (the `crr_proceed`
  stop), and `4d25` sits behind (c), the wake of another priority's goal.
  The flag is not poked.
- `1d22`-`1d61` lie behind cell 1a4.
- `4d1f`-`4d23` lie behind `1d94`: `prio`'s q never runs.

**Answers.** No run reaches `b(A)` or the clause bodies, so none has an
answer to compare. `u3d_compile.py` checks `pimm.py`'s own answers
(slice and crr_proceed: A = ok; twovar and prio: A = x) at two
placements. `twovar` checks that `pimm.py`'s suspend hooks two distinct
variable cells (`TWOVAR_PIMM_HOOKS`). The pinned runs check that the
firmware's writes up to the stop are `pimm.py`'s, or declared.

**(a), what execute's slow path does.** Under the goto reading of JMPF 8
(below), `execute` with crr below 3 (4cc0's EM2 2 taken off, 4cc1's CNDF
3) leaves the fast path. The running goal's record R10 becomes a ready
goal:

- cell 0 is {GOAL, n};
- cells 1..n are A0..An-1, copied by suspend's counted copy `1c2c`;
- cell 12 is {COD, label};
- cell 13 is R0e, checked equal to R12;
- cell 14 is R13;
- cell 15 is the old R14.

R14 becomes {HOOKo, record}, R10 a fresh record off R1b, R16 + 1, and
R15 4cc0's 0 plus 1. Then R04 := {INT, 33}. `cmp_execute_slice` compares
all of this with `pimm.py`'s execute, which runs on in the same goal, as
the requeue of that goal.

The slow path gives no new quota: an OURS proceed tried at cell 33 met
crr 1, and so proceed's own run-out arm. The reload is the work of the
code at 33, as the boot's is (`20a6`, from R05 + b0).

`4cf6`-`4d02` read cell 70, the Console Break Control Table, for the
csbrk flag (`pu.FLAG_CONDS[0x23]`, OURS false). It is the run's one
residual, and its value meets nothing tested.

`1c31` reads W15, left by the last `enqueue_goal`'s `4c01`. `1c32`
overwrites the MAR1 that read makes, unread. A program with no enqueue
before its run-out execute stops at `1c31`: W15 is never written.

**(b), the suspension stack.** The second noting compares R18, the cache,
with the new variable. When they differ it pushes R18 at R17 + 1 and
moves R17 there. That cell is in area 5's suspension stack (A:000400,
PIMM.PARAM's map; SSPB), which `pimm.py` keeps as a Python list. The
write is declared (`declare_susp_push`, OURS), only for exactly that
cell and value.

`1c64` then finds R17 = [b4]: the stack is not empty, so suspend takes
the many-variable path. `1d3a` calls the allocator's size-4 row `3334`:
MAR1 := R05 (4), MDR1 := 1a0, MDR2 := R06 (3). `3335` makes W1d :=
{VECT4o, 1a4}, `3336` makes lc := 3, and MDR1 := [1a4]. The boot's
heap-top routine reads the same table at 1a0 + 4a (cell 1ea, given by
the harness, OURS). The table's size-4 entry has no source.

**(c), the pragma.** The held compiler compiles `@priority(*, 100)` to
`put_integer 3, 100; calculate_priority_from_minimum 3, 3;
enqueue_goal_with_priority 3, @35`. `pimm.py` drops the priority: it has
one ready queue, and its `calculate_priority_from_minimum` has no shoen
(Y = X, OURS). The firmware's builtin reads the shoen's range from the
foster parent's record, cells 9 and 10, held from the boot: {INT,
ffffffff} and {INT, 0}. It scales max - min (shift_right_32m 20) and
calls the step routine `1d92`, which stops at CNDF 1 (carry).

X = 2000 instead takes `1def` (W10 := 8, `1924`), read as the range
check's error exit (310) and not followed.

**New rules.** Each was run under its injection, with the observed
result below.

| rule | label | where executed | injection: observed |
|---|---|---|---|
| `RULES['jmpf8_flag']` = goto (JMPF 8 in a flag word: short goto if cond) | kind HELD-SOURCE (rassy jmpf/9 arm 8); in flag words INFERENCE (fall-through lets crr go negative without bound in an execute chain) | `4cc2` | `jmpf8_fall`: slice MOVED (the fast path runs on; STOP 17 at `219f`) |
| `RULES['jmpf_d_call_ifnot']` (JMPF d: call vlong if not cond) | kind HELD-SOURCE (rassy arm d, vlong, pmi 49 'if not cond'); timing INFERENCE | `217d`, `1ddc` | `jmpf_d_off`: crr_proceed STOP 16 at `217d`, prio STOP at `1ddc` |
| `RULES['sc2_wide_cndf7']` (wide SC2F b with CNDF 7: EM2:EM3) | INFERENCE | `4cf6` | `wide_cndf7_off`: slice STOP 15 at `4cf6` |
| `FLAG_CONDS[0x23]` csbrk | name HELD-SOURCE (rassy cond position 35); meaning INFERENCE; value OURS (false) | `4cf7` | `csbrk_set`: slice STOP 15 at `4d03` (cell 70's value read) |
| shift_left at `4c28` (GSET_SHIFT_WORDS) | INFERENCE | `4c28` | `gset_4c28_off`: slice STOP 15 at `4c28`; the value (W1f = 0) is NOT discriminated |
| shift_left at `219c` | INFERENCE | `219c` | `gset_219c_off`: crr_proceed STOP 16 at `219c` |
| `declare_refill` (the R1b refill `4c0b` -> `3380` checked and declared) | OURS | the 5th `enqueue_goal` | `refill_undeclared`: slice FAIL 4, crr_proceed FAIL 5 |
| `cmp_execute_slice` (the slow path compared as a requeue) | OURS | slice, instruction 15 | caught by the existing injections that move slice (see the re-diff) |
| `u2_append.EXECUTE_CRR` = 8 | OURS (a crr seed) | U2's `execute` | `execute_crr_stale`: STOP 10 at `4cc2` |
| `RULES['jmpf3_s_tdar']` (JMPF 3 takes the S stage's TDAR) | INFERENCE (the 3940 table lands UNDF on the noting `3a38`) | `3979` | `jmpf3_s_tdar_off`: twovar STOP 6 at `3979` |
| `setup.S_TDAR_ODPF4` (ODPF 4 chain rows load TDAR) | INFERENCE | `3978` | `tdar_odpf4_off`: twovar STOP 6 at `3979` |
| `guard_to_alt` with nothing skipped (`ALT_FIRST_SKIP` 0) | OURS (declared difference) | twovar's two `wait_atom`s | `alt_first_skip`: twovar FAIL 6 (R04 {REFo, alt}) |
| `declare_susp_push` (the suspension-stack push) | OURS (declared) | `3a42` | `susp_push_undeclared`: twovar FAIL 8 (heap 10000400) |
| `RULES['sc2_wide_em1']` (a free EM1 in a wide word ignored) | INFERENCE (rows `3331`-`333a`: EM1 3-6 beside the same 1a0) | `3334` | `wide_em1_raise`: twovar STOP 9 at `3334`; `wide_em1_16`: twovar MOVED (reads cell 11a4) |
| `RULES['wrbf_low_r']` (WRBF switches only selects 10-1f) | INFERENCE (rassy's name lists; the `++ rfar` pattern after the static 'W06' writers) | `3335`, `4c12`, `4c27` | `wrbf_low_w`: twovar STOP 9 at `3335` (W06) |
| `JMPF8_GOTO_CNDF` + 3 | kind HELD-SOURCE (arm 8); timing INFERENCE | `1d93` | `jmpf8_cndf3_off`: prio STOP at `1d93` |
| `setup.FORMS` calculate_priority_from_minimum ('x', None) | OURS (nano-code ACF 5, DFF 2 undecided) | `1dda` | `prio_form_off`: prio STOP at the builtin |

**Residuals pinned** (last writer the harness, read on the path):

- slice: cell 70 (program walk);
- crr_proceed: cell 10 (the 4th pick's walk);
- twovar: suspend cells 1a4 and b4; program R17, R18, R19, 1a4, b4,
  f2000000, f2000001;
- prio: none.

The boot residual (W1c, cells 1ea, a0, b6) is unchanged.

**The u2_append seed.** `u2_append`'s `execute` now needs crr, which its
standalone run does not hold. `EXECUTE_CRR = 8` is an OURS seed of R15,
named here because it stands beside the owner's "never seed scheduler
state". Without it, `execute_crr_stale` stops at 10, `4cc2`. U2's pin is
unchanged.

**Re-diff of the existing injections** against a clean 1a4c11ba snapshot.
The outputs of `check_pu.py`, `u2_append.py` and `u3_goals.py` were
compared by content under the 166 injections that existed, with the four
new programs' sections cut. 152 are unchanged. 14 changed, and each is
still caught:

- `u2_append cjump_same`: `execute` now passes, since crr is given; the
  proceed side cases still FAIL.
- `u2_append cnd3_off`: now STOP 10 at `4cc1`, where it passed (stronger).
- `u2_append execute_mdr1`: STOP 10 at `1c31` (W15), where it FAILed on R04.
- `u2_append interrupt_pending`: the same STOP at `22a5`, now reported by
  CNDF 7 (the wide immediate before it is read).
- `u3_goals crr_two`: STOP 8 at `219f`, cell 10 (was `217d`).
- `u3_goals susp_flags_rassy`, `sc2_a_opd`, `sspb_zero`: STOP at `3343`,
  cell 1a4 (were `3331` / `3334`, the wide immediate).
- `u3_goals alf_high_reversed`: STOP at `1c36` reads R05 (was W05).
- `u3_goals interrupt_pending`: suspend now passes `1c18`, whose wide
  immediate is read. It moves twovar only.
- `u3_goals adf2_none`, `sc2_e_off`: FAIL at 16, where they stopped.
- `u3_goals execute_mdr1_stale`: STOP 19 at `4cc2` (stronger).
- `u3_goals wsel_d_off`: `enqueue_goal` passes (R0d by `wrbf_low_r`);
  STOP at 8 in proceed, and stream STOP 6 at `4cc2`.

Of the existing `u3_goals` injections, 25 also move one or more of the
new programs (the re-diff's summary, scratch).
