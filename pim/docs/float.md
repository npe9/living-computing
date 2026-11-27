# Floating point on PIM/m

What a PIM/m float is, which KL1-B instructions operate on it, and how
both models carry them out (2026-11-26). Each claim is labelled with what
supports it: **PRINTED** (an ICOT manual or report), **HELD-SOURCE**
(PIMOS 3.6 source, `pimos.tar.Z`), **HELD-OBJECT** (the PIMOS 3.6 `.sav`
objects, `pimosobj.tar.Z`), **SECONDARY** (VPIM, PDSS or KLIC, which
are other implementations), **INFERENCE**, or **OURS**.

## 1. The format

| Question | Answer | Support |
|---|---|---|
| Width | 32 bits, IEEE 754 single precision | see below |
| Where | the 32-bit value field of the 40-bit tagged word: immediate, not boxed | HELD-SOURCE, HELD-OBJECT |
| Tag | `30h` (`FLTo`; `FLTx` `31h` is in the console's tag list, but a tag from `20h` has no MRB bit, and no `31h` word is made) | HELD-SOURCE |
| Extended float | tag `3Fh`, boxed: a pointer to three 32-bit words | HELD-SOURCE |

The evidence for the format:

- **HELD-SOURCE.** `library/kbn/kbnheap.kl1`:144-146 writes a float into
  the IPL image as the atomic word `{FloatTag, Value}`, where `Value` is
  `tag_and_value`'s value of the float itself. `tag(float, 16#"30")` is
  at line 236. The same file (lines 35-42) writes an extended float as
  `{16#"3F", Addr}` followed by three words, which come from
  `extended_floating_point_to_binary(ExFloat, Bin0, Bin1, Bin2)`.
  `unloader/encoder.kl1`:461-470 writes the same three words.
- **HELD-OBJECT.** The 20 `.sav` files hold 103 float constants. Each is
  one tagged word `[0x0030, V1, V2]` in a code area (the second cell of
  `put_constant` and its kin). Read as IEEE single, every value is a
  plain one: `00000000` 0.0 (59 times), `3f800000` 1.0 (12), `bf800000`
  -1.0 (12), `41200000` 10.0 (9), `42c80000` 100.0 (6), `40800000` 4.0
  (2), `40000000` 2.0, `47800000` 65536.0 and `4f800000` 4294967296.0
  (once each). Read as anything else, they are not plain values. This
  was counted with `asm/unlsav.py`'s reader over every module.
- **PRINTED, for Multi-PSI.** "In Multi-PSI, inner representation of
  floating point numbers uses single precision (32 bits) in accordance
  with IEEE" (PIMOS manual, `e-syntax.tex`:243). The manual says this of
  Multi-PSI, not of PIM/m. The link to PIM/m is
  `pimos.h` `case(pimm)`, which sets `machine_type mpsi`, together with
  the held PIM/m objects above.
- **HELD-OBJECT, the microcode.** The Pseudo PIM/m firmware's decode
  table (`asm/mekbn.py --entries`) has micro-routines for `23:E6`
  (`floating_point`, 35e0), `23:FC` (35e8), `23:FD` (3649), `22:CE`
  (3651) and `22:CF` (365b). The `23:FC` routine builds its result as
  `opdb<-{FLTo,0}` (3631), a float tag with a value, and has a
  shift-and-count loop (3634-3636). INFERENCE: that loop is
  integer_to_floating_point's normalisation done in microcode.

`pimos.h` (the 1995 copy from IFS d-pool) sets `floating_point yes` and
`extended_floating_point yes` for `case(pimm)`.

### The extended float

INFERENCE: the extended float is the MC68882's 96-bit extended format.
Three things point that way:

- its body is three 32-bit words;
- its function set matches the 68881/68882's instructions one for one:
  `etox`, `etoxm1`, `twotox`, `tentox`, `lognp1`, `logn`, `log2`,
  `log10`, `sinh`, `atanh` and the rest (`inst_tab.kl1`, `22:BE`
  functions);
- the PSI-UX inference unit's FPP is an MC68882 (Giho 65(6), table 1,
  `docs/literature_gaps.md`).

It is **not modelled**. Its guards fail on anything but an extended
float, as before, and refuse an extended float (`pimm.py`
`i_extended_floating_point`, `ext_float_compare`).

### Where the sources disagree

| Point | PIM/m (above) | Other source |
|---|---|---|
| Representation | immediate single, tag 30h | VPIM: `FLT` points at two `INT` words holding an IEEE double, high half first; PIM/p: a CDESC word and 64 contiguous bits (TM-1044 `s2.tex`:304-330, SECONDARY). KLIC 2.002: 64-bit doubles (`documents/klic.tex`:1923, SECONDARY) |
| Unification of two floats | by bit pattern: "Unification of floating point numbers is performed by comparing the bit patterns of the inner representation" (`e-syntax.tex`:247, PRINTED) | VPIM compares the value (`pimm.py` `passive`'s note, SECONDARY). By bits, `+0.0` and `-0.0` do not unify; by value they do |
| Overflow | infinity: "If an overflow occurs, infinity is unified with NewFloat" (`e-builtin.tex`:509, 526, 544, 561, PRINTED) | PDSS: the built-in fails when the double result is beyond the single range (`emulator/float.c` CALC, `FLOAT_HUGE`, SECONDARY) |
| floating_point_to_integer | "ignoring decimal", towards zero (`e-builtin.tex`:582) | KLIC: `int(X)` "rounded to an integer value" (`klic.tex`:1865), but its code is the C cast `(long)` (`include/klic/gb.h`:108), which also truncates (SECONDARY) |

## 2. The instructions

The encodings are `assembler/inst_tab.kl1` (`docs/kl1_encoding.md`).
The operand packing is `klb_opr.kl1`:268-282. `f_r_r(F)` is one cell
`op << 24 | F << 16 | Reg1 << 8 | Reg2`. `f_r_r_r(F)` is two cells; the
second holds `Reg3 << 24`, an integer word (held: `22:cf000207` is
followed by `01000000`). The directions are `compiler/blt.kl1`:73-102
and 174-237 for the guards, and `active_builtin` 621-640 and
`regass.kl1`:459-475 for the body forms.

| Mnemonic | Encoding | Operands | Uses in the held objects |
|---|---|---|---|
| `floating_point` (guard) | `23:E6` r | X | 194 |
| `floating_point_equal` | `23:FC` f_r_r(0) | F1, F2 | 5 |
| `floating_point_not_equal` | `23:FC` f_r_r(1) | F1, F2 | 0 |
| `floating_point_less_than` | `23:FC` f_r_r(2) | F1, F2 | 50 |
| `floating_point_not_less_than` | `23:FC` f_r_r(3) | F1, F2 | 35 |
| `floating_point_to_integer` | `23:FC` f_r_r(4) | F in, ^I out | 18 |
| `integer_to_floating_point` | `23:FC` f_r_r(5) | I in, ^F out | 9 |
| `floating_point_add` / `subtract` / `multiply` / `divide` | `23:FD` f_r_r_r(0-3) | F1, F2, ^F | 5 / 5 / 10 / 5 |
| `b_floating_point_to_integer` | `22:CE` f_r_r(0) | F in, ^I out | 10 |
| `b_integer_to_floating_point` | `22:CE` f_r_r(1) | I in, ^F out | 49 |
| `b_floating_point_add` / `subtract` / `multiply` / `divide` | `22:CF` f_r_r_r(0-3) | F1, F2, ^F | 38 / 2 / 29 / 21 |

The use counts are over the 20 held `.sav` files (OURS: the counting
script walks `asm/unlsav.py`'s parse, as `asm/census.py` does). The
extended-float set (`23:6E`, `23:6F`, `22:BC`-`22:BF`) has 259 uses.

The semantics are PRINTED (PIMOS manual `e-builtin.tex`:423-610, "GB":
guard or body):

- **Suspend** if an input is uninstantiated.
- **Fail, Exception**:
  - if an input is not a float (or, for `integer_to_floating_point`,
    not an integer);
  - on an invalid operation: inf + -inf, inf - inf, 0 * inf, 0/0,
    inf/inf;
  - in `floating_point_to_integer`, on overflow.

  In a guard this fails the guard; in a body it is an exception
  (`e-builtin.tex`:20). The exception is `invalid_floating_point_operation`,
  code 21 (`e-shoen.tex`:544, 829; the Listener's example is
  `0.0/0.0`, `e-listener.tex`:6611-6622).
- **Overflow** gives infinity. **x/0** for x not 0 gives infinity
  (`e-builtin.tex`:561).
- **Rounding.** INFERENCE: round to nearest even. No held source
  states the mode. It is IEEE's default, and the 68882's default mode.
- **Comparisons** are numeric (IEEE). So `0.0 $=:= -0.0` succeeds,
  although the two do not unify (bit patterns).

## 3. The models

- **Reference** (`ref/pimm/pimm.py`, the float section and the
  helpers `f32`, `to_f32`, `int_to_f32`, `f32_to_int`, `f32_op`): the
  operations are computed in Python doubles and rounded once to single
  through `struct.pack('>f')`, the C cast, which rounds to nearest even.
  For +, -, * and / that single rounding is the correctly rounded single
  result, because a double holds more than 2 x 24 + 2 bits. A finite
  value too large to pack becomes the infinity of its sign. The invalid
  cases are decided from the operands, before any arithmetic.
- **Bluespec core** (`bsv/PimmFBox.bsv`, `mkPimmFBox`): the arithmetic
  is Flute's FPU, vendored as `bsv/vendor/flute/FPU.bsv` (see its
  README). That FPU is bsc's `FloatingPoint` library: the fused
  multiply-add for add, subtract and multiply, and the divider for
  divide. The box takes requests and gives responses, as the RISC-V
  cores' FBox does. The invalid cases and x/0 are decided from the
  operands, by the same checks as `pimm.py`, not from the library's
  exception flags. The conversions and comparisons are functions of
  the package: `vFloatToFixed` with `Rnd_Zero` behind an explicit range
  check, `vFixedToFloat` with `Rnd_Nearest_Even`, and `compareFP`, as
  Flute's `FBox_Core.bsv` uses them. `PimmStages.bsv` sends the operands
  and writes the answer.
- **Unification.** A float unifies with a float of the same bits, in
  both active (`unify`, `PimmDBox`) and passive (`wait_value`,
  `passive`, `PimmPBox`) unification. `wait_constant` and `diff` take it
  as atomic (`pimm.py` `atomic`, `PimmStages` `isAtomic`).
  `hash` hashes a float by its bits, as PDSS does (`emulator/blt_system.c:410`, `case FLOAT` beside ATOM and
  INT); the
  held compiler hashes a float constant when it builds a clause index.
- **set_constant** (23:10, `c8_c40`) is added on both models: goal
  argument x becomes the whole next cell. The compiler writes it for a
  float argument of a goal (PDSS `compiler/outp.kl1:429-432` maps
  `set_constant` to `set_float` there). Nothing before floats used it.
- **Not modelled, refused loudly on both models:**
  - a body form whose input is unbound. It should suspend, but no
    built-in of the `f_r_r` forms has a stub (`asm/pimm_stubs.py`
    takes none), and a new stub would change the stub table that saved
    machines hold;
  - a body form's exception (as `b_divide`'s).

  Neither occurs in the runs below.

## 4. The checks

- `ref/pimm/lockstep_float.py` (in `bsv/run_pimm_lockstep.sh` and so in
  the suite): hand-assembled clauses for every instruction above, guard
  and body, run on both models and compared line by line, except the
  `23:E6` type guard: its success on a float is exercised only by the
  `float_klic` row (outside the suite), its failure by `lockstep_run.py`.
  The `passive` and `active` parts unify floats by their bits (vectors
  of floats included). The expected
  words are IEEE single constants written by hand, not computed by
  either model. The cases cover:
  - rounding to nearest even (1/3, 2^24 + 1, 2^24 + 2 + 1, the integer
    16777217);
  - overflow to infinity and x/0;
  - each invalid case failing the guard;
  - subnormal results, including a tie;
  - +0.0 against -0.0 in a comparison;
  - the integer range limits of floating_point_to_integer;
  - non-floats.
- **The KLIC comparison** (section 5).
- **MP1** (section 6).

## 5. The KLIC comparison

`docs/float/flt.kl1` (OURS) uses `$:=`, `float()`, `int()`, `$<`,
`$=:=`, `$>` and `$>=`, a list of floats, and a loop that halves a
float. Every value in it is exact in single, so a single-precision
machine and KLIC's doubles must agree.

The program is run two ways:

- **On PIM/m.** It is compiled by the held compiler at the shell's
  prompt and run in the Listener (`ref/pimm/lockstep_shell.py` APPS
  `float_klic`, served as `HOME>flt.kl1` for that row only).
- **On KLIC 2.002.** It is built from the held tarball by
  `docs/pkl1/klic_oracle/README.md`'s recipe and run with
  `docs/float/main_flt.kl1`. Its output is `docs/float/oracle_flt.out`.

The results (OBSERVED 2026-11-26):

- `go(R)`: KLIC prints `[3,-8,125,15,lt,eq,gt,10]`. The Listener on
  PIM/m answers ` R =[3,-8,125,15,lt,eq,gt,10]`: the same.
- `show(A)`: KLIC prints `3.750000`, and the Listener answers
  ` A = 3.750000E+0`. That is PIMOS's own float printer, which is held
  code running on the model. The value is the same; only the printed
  form differs.

The row compiles the file (`Compile Succeeded : flt`) and runs both
queries in 2,829,790 instructions from the prompt checkpoint. Its
counts are pinned in `lockstep_shell.py` PINNED, and its window text in
APPS. It runs on both models through `bsv/run_pimm_apps.sh` (outside
the suite: it needs the prompt checkpoint).

On the way the row met three things the models lacked. Each one is now
on both models:

- `hash` of a float: the compiler hashes the constant 0.5 when it
  indexes `sum/3`'s clauses;
- a float as an atomic value in passive and active unification, as
  `wait_value` meets it;
- `set_constant` (23:10), which puts a float argument into a goal.

A finding on KLIC 2.002 (SECONDARY): `I := int(A)` in the same body as
`A $:= ...` reads A before it is bound and answers 0. That is why
flt.kl1 converts in a goal of its own that waits (`toint/2`). PIMOS's
compiler runs body built-ins in order, and A is bound by then.

## 6. What PIMOS gets past

MP1 (`ref/pimm/mp1_rebuild.py`) used to stop on `bufutil.kl1` and
`token.kl1` at `integer_to_floating_point`: the compiler converts on
its way. Re-run with floats on 2026-11-26, one file each:

- `bufutil` now compiles. It is the same as the held module but for the
  order (2396 cells against 2396): `same-but-order`, like 17 others.
- `token` now compiles, but `differs` (3180 cells against 3180). The
  first difference is the target of `enqueue_goal` at [1414]; 59 lines
  differ. That is the same kind of difference as `mklib`'s and
  `variable`'s: INFERENCE, predicates placed in another order. Not
  explained.

Both are pinned in `mp1_rebuild.py` PINNED.

## 7. Injections

Each injection went into a backup that was restored with `cp` and
checked with `cmp`. The failure sets below are the ones OBSERVED.

- **Reference, wrong rounding.** `pimm.py` `to_f32` was changed to
  round toward zero (one ulp down when the nearest-even result is
  larger in magnitude). `lockstep_float.py --reference` failed `arith0`,
  `body0` (2^24 + 2 + 1: 4b800001 for 4b800002), `arith3`, `body3`
  (1/3, 1.5/2.25 and BIG/TEN, each one ulp low), `toflt` and `btoflt`
  (16777219, a tie: 4b800001 for 4b800002, and 2^31 - 1:
  4effffff for 4f000000). Nothing else failed. So no subtract or
  multiply row has a result that rounds away from zero: a gap in the
  rows, not in the models (both use the same rounding path).
- **Reference, wrong tag.** `integer_to_floating_point` was changed to
  write an INT word. `toflt` failed (the first three rows: tag 0 for
  30h). The body form, a separate instruction, still passed.
- **Core, wrong rounding.** `PimmFBox.bsv` asked the FPU for
  `Rnd_Zero` instead of `Rnd_Nearest_Even`. `run_pimm_lockstep.sh float`
  failed at the first rounded result: the core wrote `R 3 304b800001`
  where the reference wrote `304b800002` (arith0, 2^24 + 2 + 1).
- **Core, wrong tag.** `PimmStages.bsv`'s conversion was changed to make
  its cell with `tag_INTo`. The lockstep failed at `R 2 004b800000`
  against `304b800000` (toflt's first row).
