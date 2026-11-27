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

The microcode is third-party and stays out of git: it is read from
`docs/nonlocal/psdpim.tar.Z` at run time, as `asm/psdpim.py` reads it.
Nothing here prints or stores image words except under `-v`, to the
terminal.

## State (2026-11-26)

**U1 reached; U2 not reached.**

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
| A conditional JMPF 1 with EM bit 0 set is taken when COND is false | `31fb`, `31d2`, `318f`, `31d8` (a pop's end, taken unless the link was the end marker) | one fit; the opposite pairing (COND true when the link is a cell, bit 0 = taken on true) is not told apart by these words. EM bit 0 clear: raises |
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
    p.mem[addr] = (tag, value) # memory, a dict; a read of an absent cell raises
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

## Next, for U2

In order: the refill (makes the free lists the firmware's own and drops
the seeding); `execute` (`4cc0`), `proceed` (`216c`), `try_me_else`
(`216a`); the `get_*`/`wait_*` tables, which need the S-stage tag set-up
(nano-code TDPF), the S12 row entry and TGT columns other than 2; CCF
as a coded field; the conditional a/b/c/e timing (`RULES['cjump_time']`;
the KL0 LESST path `1046`-`1049` is where the static agent suggests
testing it). An append reduction needs all of these.
