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

The microcode is third-party and stays out of git: it is read from
`docs/nonlocal/psdpim.tar.Z` at run time, as `asm/psdpim.py` reads it.
Nothing here prints or stores image words except under `-v`, to the
terminal.

## State (2026-11-26)

**U1 reached; U2 not reached.**

- 23 cases, all PASS: 19 compared against `pimm.py` (34 held
  microinstructions executed and matched), and 4 that take the last cell
  of a free list and must enter the refill (17 held words executed up
  to the refill, where they stop, as they should).
- Multi-word routines that run as held: `set_nil`, `write_nil` (2
  words: a stamp, then a write and a structure-pointer step),
  `set_variable`, `write_variable` (3: a pop from the one-cell list, the
  new cell made `UNDF`, a `REF` to it), `put_variable` (4), `put_list`,
  `put_vector_1`, `put_vector_2` (3: a pop, the list or vector pointer,
  the structure pointer).
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

MEASURED rules are `asm/mekbn.py`'s and pinned by `mekbn.py --check`
(field positions; JMPF kinds; the strobes 61/62/60; 58/59 as MAR2/MDR2;
SD1F/ADF/AS1F numbering; SC2F 8/9 immediates; TGIF 1/2 stamps; "one
word later"; a write stores the MDR as it stood before its word).
These are used as they stand. The INFERENCE rules added here, with the
microaddress that decided each (all in `pu.py` `RULES` / `COND_RULES`
and `setup.py`):

| Rule | Decided at | Evidence |
|---|---|---|
| Operand selects `a` = y, `b` = z (8 = opcode, 9 = x are MEASURED) | `318f` (`set_variable` writes its REF to `opda`; `pimm.py` `reg[y]`), `31d7` (`put_variable`, `reg[y]`) | the `pimm.py` operand readings; `b` is not yet executed |
| TGIF 3: both stamps, the tag from EM2 | `3193` (`write_nil`: EM1 `20`, EM2 `02`; the cell must be `ATOM 0`) | thesis p.144 "EM2 can also be the DST-Bus tag immediate"; predicted at `3365`/`3366` (the refill, read not run): EM2 there is `VECT0x`, the free-cell link tag MEASURED in section 15, where EM1 would give `STRGx`. This changes `mekbn`'s trace of `1c0f` (cell 15 of `suspend`'s record), which takes EM1 |
| A write with bit 59 stores MDR2 | `31d7` (`put_variable`: the cell gets the `UNDF` of `31d6`; MDR1 holds the link) | **conflict, open:** the refill loop `3367` (CCF `16`, bits 62, 60, 59) must write MDR1, the running link, to build a list; `31d7` is CCF `12`. CCF is probably a coded field, as `rassy`'s value table says (`binary_reverse_engineering.md` section 3), and bit 59 alone does not choose the data register |
| MCF with EM1 `20` steps R02 by one | `31c7` (`write_integer`: one word, MCF, EM1 `20`; `pimm.py` `_sp += 1`; `set_integer` has neither and leaves sp), `3193` | the self-loops carry MCF with EM1 `10` (a loop counter, below): EM1 is MCF's operation |
| JMPF bit 26 (codes b, c, e) makes a jump conditional; 3, 4, 6 jump unconditionally whatever CNDF holds, and their CNDF only forms COND for a later word | `318c` (`set_variable`, JMPF 4 CNDF b, must jump over `set_marked_variable`'s `318d`-`318e`) | measured over both stores, "Conditions" below; replaces `mekbn.tested()` inside the simulator |
| CNDF 9: COND := tag of the ALU's first input = EM1; CNDF b: = EM2 | `31fa`, `31d1` (EM1 `ATOMo`), `318c`, `3196`, `31d6` (EM2 `ATOMo`), each tested by the conditional end that follows | "Conditions" below; the refill writes `{ATOMo, 0}` as the last link (`3368`) |
| A conditional JMPF 1 with EM bit 0 set is taken when COND is false | `31fb`, `31d2`, `318f`, `31d8` (a pop's end, taken unless the link was the end marker) | one fit; the opposite pairing (COND true when the link is a cell, bit 0 = taken on true) is not told apart by these words. EM bit 0 clear: raises |
| ODPF 1: the S stage loads R(10 or EMO1) into MAR2 (ODSF 0) or MAR1 (ODSF 1) | `318b` (`set_variable`), `31d0` (`put_list`) | predicted for `put_variable`, `put_vector_1/2`, `write_variable` (run); read for `proceed`, `collect_list`, the marked forms (`setup.py` header). Nano-code field positions are Fig. 3-22 right-aligned on the entry's 56 bits; only ODPF, ODSF, EMO1, EMO2 are used |
| R06 = R07 = 0 | `31d6` (`{UNDF, R07}` where `pimm.py` writes `UNDF 0`) | `{ATOMo, R06}` stands where a nil does (section 17) |

**Conditions.** Measured with scratch scripts over all words (not
pinned). The word after a JMPF 3/4/6 word is zero or an explicit
branch target in 47-83% of cases, with or without CNDF; after a JMPF
b/c/e word in 3-17% (image 2: 3: 69%/83% with/without CNDF, 4: 76%/74%,
6: 51%/47%, b: 13%/3%, c: 8%/3%, e: 11%/17%; `syspsi` the same split).
All 23 self-jumping words are c or e; 22 carry MCF with EM1 `10`, 20
of them with CNDF 6 (two b; `281f` has CNDF 2 and no MCF): INFERENCE, a
counted loop on the loop counter (`rassy`
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
  structure element at R02.
- Free lists already built (`check_pu.py` `seed_lists`), in the shape
  the firmware writes: cells `{VECT0x, next}`, the last `{ATOMo, 0}`.
- Memory: a flat dict; the goal record being built at `f1000000`, the
  lists at `f2000000`/`f3000000`.
- The Pseudo PIM/m environment is not needed for these routines: no
  routine run here touches I/O, the TLB or `syspsi`'s upper store.

## Fault injections (observed, `--inject`, in-process, no file edited)

| Injection | Observed |
|---|---|
| `tgif3_em1` (TGIF 3 tag from EM1) | `write_nil` FAILs (cell `20:0` for `02:0`); nothing else |
| `w59_mdr1` (a bit-59 write stores MDR1) | `put_variable` FAILs (no cell with `UNDF`); nothing else |
| `write_same_word` (a write stores the MDR as loaded in its own word) | `set_variable`, `write_variable` FAIL |
| `opd_a_is_z` (select `a` = z) | `set_variable`, `put_variable` FAIL (wrong register written) |
| `cnd_em_swapped` (CNDF 9 against EM2, b against EM1) | the four last-cell cases FAIL (the pop ends without entering the refill); the 19 compared cases still pass, which is why the last-cell cases exist |
| `odsf_swapped` (ODSF 0 = MAR1, 1 = MAR2) | 10 cases STOP (MAR2 / MAR1 never set): every pop |

## First routine that would not run

**The free-list refill, `3365`-`337f`**, entered at `3378` (one-cell
list) or `337d` (two-cell list) when a pop takes the last cell. It
stops at once on R1f (the heap pointer, `rassy`'s `hp`), which no case
sets; given one it stops at `3378` on **AS1F 3**, whose meaning is not
known. Read, not run, the routine also needs: MCF with EM1 `10` and
CNDF 6 (the counted loop `3367`; the count fits 16-word chunks: EM2 of
`3378` is 13 and of `337b` is 5, and 13 + 3 single writes = 16 cells,
5 + 3 = 8 two-cell blocks, if AS1F 3 is "the constant EM2"); W0d; and
the write data of CCF `16`, which conflicts with the bit-59 rule above.

**The allocator for three cells and more, `3331`-`3347`**
(`put_vector_3`..`_6`, `new_vector`, `suspend`): stops at `3331` on
R05, the base of a table of list heads in memory whose contents are set
at boot, and then needs SC2F `b` (the "wide" immediate, layout not
read) and the `pass_as2` addressing at `3343`.

## Next, for U2

In order: the refill (makes the free lists the firmware's own and drops
the seeding); `execute` (`4cc0`), `proceed` (`216c`), `try_me_else`
(`216a`); the `get_*`/`wait_*` tables, which need the tag-dispatch RAM
(TGT, not in `pimm.MEkbn`; `sysinit` `5800`-`59ff` is the first place
to look) and the S-stage tag set-up (nano-code TDPF); CCF as a coded
field. An append reduction needs all of these.
