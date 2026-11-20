# PIM/m KL1-B instruction semantics, from paired source and object

What each instruction does, settled one at a time from object code in
the PIMOS binaries whose KL1 source we have. This is the table both
the host reference model (`ref/pimm/pimm.py`) and the Bluespec model
are to follow. An instruction is listed only when a runnable check
depends on the reading; "inferred" marks what the check does not
exercise.

Notation: an instruction cell is `tag:op x y z`, with `x` = bits
23-16, `y` = bits 15-8, `z` = bits 7-0, `c16` = bits 15-0 signed.
`r[n]` is register n; the first argument of a goal is `r[0]`.
A label is `here + 2 + c16`, in cells.

Evidence so far: `jis_to_ascii:convert_element/2` in `pimm_ipl.kbn`
against `bios/boot/jtoa.kl1` (`ref/pimm/test_jtoa.py`, all 65,536
keys, five observed fault injections).

| Instruction | Encoding | Meaning | Evidence |
|---|---|---|---|
| `try_me_else` | `23:68 _ c16` | the next clause is at the label; a failing guard goes there | checked |
| `switch_on_non_integer` | `23:28 x c16` | if `r[x]` is bound to an integer, fall through; otherwise go to the label. An unbound `r[x]` also records the variable as one the goal is waiting on | integer and atom cases checked; the unbound case by its consequence (the goal suspends) |
| `hash_on_constant` | `23:2D x c16`, then a word, then a table | `c16` is a mask. The next cell holds the miss label, relative to itself (`its address + 2 + value`). Then `mask + 1` slots, indexed by `r[x] AND mask`: `{atom, 0}` is empty; `{integer, count << 16 \| offset}` points, `offset` cells from the slot, at `count` pairs `{key, offset}`; a matching pair's target is `offset cell + 1 + offset` | checked (three of the five injections are here) |
| `put_integer` | `23:31 x c16` | `r[x]` := integer `c16` | checked |
| `not_less_than` | `23:F1 x y` | guard: `r[x] >= r[y]`, else fail to the next clause | checked; unbound operands not exercised |
| `b_subtract` | `22:C1 x y z` | `r[z]` := `r[x] - r[y]` | checked |
| `b_add` | `22:C0 x y z` | `r[z]` := `r[x] + r[y]` | checked |
| `get_value` | `23:BC x y` | unify `r[x]` with `r[y]` | checked for integer against unbound only |
| `get_integer` | `23:B9 x c16` | unify `r[x]` with integer `c16` | checked against unbound only |
| `otherwise` | `23:6A x c16` | clauses below apply only if none above can: if a guard above was waiting on a variable, the goal suspends; else continue | both cases checked. `x` is the arity and the label is the predicate's own first instruction; what the machine uses them for is inferred (re-entry after suspension) |
| `suspend` | `23:69 x c16` | end of the clauses: suspend if a guard was waiting, else the reduction fails. Same operands as `otherwise` | suspension checked; the failure case inferred |
| `collect_value` | `23:1D x` | reclaim what `r[x]` refers to (MRB) | not modelled: a no-op in the reference model |
| `proceed` | `23:60` | the goal is done | checked |

Things this predicate shows about the compiler, useful for reading the
rest: range guards compile to `put_integer` and a comparison per bound;
33 constant clauses compile to one `hash_on_constant`, placed after the
`switch_on_non_integer` and before the range clauses even though the
source has the ranges first (the clauses are mutually exclusive, so the
order does not show).
