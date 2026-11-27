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

**U1 reached; U2 not reached** (furthest point 4 of 16 instructions of
append: section "U2" below).

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
of conditional a/b/c/e a switch, `cjump_time`, None by default (raises).
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
(`(cycle, byte)` of the last case_tag_setup), `push`, `pop`, `next`
(`None` at an end, `-1` a return to a `call`); the format is in `docs/pu_microcode_plan.md` "The trace". Any
field value not modelled raises `Unmodelled(upc, what)` (reaching
`6c21` raises its subclass `Trap`), with
`.words` the words executed before it when raised from `run`/`call`.
The decoded rules are module dictionaries, `RULES` and `COND_RULES`, so
a harness can change one (as `check_pu.py --inject` does) without
editing the file.

## U2: append/3 on the held microcode (2026-11-26, second session; 2026-11-27, third)

**U2 not reached. Furthest point: 4 of 16 instructions executed and
matched (11 held words), then a stop at the fifth
(`put_reused_structure`, no S-stage set-up form).** Before 2026-11-27: 2
of 16, a stop at `read_variable` (`34a0`). Plus a held boot routine
run (start's heap top, `204b`-`2052`, 6 or 8 words).

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
alternative against R11.

| # | Instruction | Words | Result |
|---|---|---|---|
| boot | start's heap top `204b`-`2052` (called as from `2028`) | 6 (aligned) / 8 | R1f = the parameter cell `1a0 + 4a` rounded up to 16, on 5 parameters (contract) and on `pimm.py`'s heap pointer |
| 0 | `try_me_else 0, @6658` (`216a`) | 1 | ok: R11 = `{REFo, load + 6658}`, `pimm.py`'s `alt` |
| 1 | `switch_on_non_list 0,0,8` on a list (`3300`-`3301`) | 2 | ok: R02 = the car's address, `pimm.py`'s `sp`; COND true, the jump to `3305` not taken |
| 2 | `read_variable 3,0,0` (`34a0`-`34a2`, `3494`) | 4 | ok: A3 = `{ATOMo, a}`, R02 + 1 (`pimm.py`'s `sp`) |
| 3 | `read_variable 4,0,0` (the same words) | 4 | ok: A4 = `{ATOMo, 0}` (nil), R02 + 1 |
| 4 | `put_reused_structure 0,0,2` (`31e8`) | 0 | STOP: no S-stage set-up form (`setup.FORMS`): its entry has the tag immediate `1e` and ACF 4, DFF 2, ODPF 3, OS1F 1, OS2F 4, ODSF 1, TDPF 4, EMO1 4; the operand is a list, so it is the S12 row entry (not settled) |

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

`check_pu.py` still passes unchanged with these rules (32 cases, 80
words: the CNDF 2 rule, the bit-0-clear polarity and the 2026-11-27
rules meet no U1 word).

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

**`cjump_time`** (the timing of conditional a/b/c/e): not attempted in
this session; no word of the U2 run reaches one.

**The S12 row entry** (a tag-test entry entered at a row by the tag):
for `switch_on_non_list` (TDPF 0), TGT column 0 (REFo 0, LISTx 1, LISTo
2, REFx 3, every other tag 4) with 4-word rows reads well: row 1
`{LISTx}` then `3301`, row 2 frees the variable cell a single-reference
list was reached through (`3305`-`3309`: [MAR1] := R19, R19 := MDR2),
row 4 the branch to the label through `2447`, a 4-bit JMPF 2 (S10,
UNKNOWN). `get_atom`'s rows (section 9 of `pseudo_pimm_microcode.md`)
do not fit column 0, and `wait_nil` (TDPF 1) does not fit column 1 with
4-word rows. Not adopted; any tag but the immediate raises.

## Next, for U2

In order, as the harness stops on them: `put_reused_structure` (`31e8`,
entry tag immediate `1e` VECTo, TDPF 4; append's operand is a list, so
the S stage does not take the immediate's start, and where it starts
instead is the S12 question: p.135's "start(for_others)" says a second
start address, and the thesis's p.129 says TDPF sets up the E stage's
multiway (a column for a later case_branch), not the start; `31e9`
jumps to `31f3`, whose conditional end tests CNDF 9 VDESC and reads
R01, never set; it calls `31a1`, a 4-bit JMPF 2. A lead, read not
run: `31ec`-`31ed` (entry + 4) put the operand in x and in R02 and end
conditionally, the reuse in place of a single-reference list, so
"start(for_others)" may be entry + 4 here; `get_atom`'s `3804` stamps
ATOMx, which does not obviously fit the same reading); then
`write_value`, `write_variable` (run in U1), `get_bound_value`,
`put_value`, `execute` (`4cc0`), `wait_nil`, `get_value`, `proceed`
(`216c`). The 4-bit JMPF 2 (`2447`, `31a1`). Then the boot beyond
`204b` (the refill and list builders: MCF EM1 10 and CNDF 6, the
counted loop; CCF as a coded field) to drop the seeded lists; the
conditional a/b/c/e timing (`RULES['cjump_time']`; the boot's fill
loop `209b`-`209e` and the KL0 LESST path `1046`-`1049` are where it can
be tested). The other dereference set-ups (EM1 `2a`, `2b`, `2f`) and
the REF / immediate rows of `2d` are read, not run.
