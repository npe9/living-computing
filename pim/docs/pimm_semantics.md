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

Evidence so far: module `jis_to_ascii` in `pimm_ipl.kbn` against
`bios/boot/jtoa.kl1` (`ref/pimm/test_jtoa.py`): `convert_element/2` on
all 65,536 keys, and `convert/2` (through `convert_loop/4`) on five
strings, with eleven observed fault injections, one of which the test
does not catch (noted at `subtract`).

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
| `proceed` | `23:60` | the goal is done; the machine takes the next ready goal | checked |
| `wait` | `23:E0 x` | guard: `r[x]` is bound; if not, note the variable and fail to the next clause | both cases checked |
| `wait_integer` | `23:A1 x c16` | guard: `r[x]` is the integer `c16` | checked (0 ends `convert_loop`; 16 selects 16-bit strings) |
| `less_than` | `23:F0 x y` | guard: `r[x] < r[y]` | weakly: the only use is `0 < N` after `N = 0` has been tried |
| `subtract` | `23:F5 x y z` | guard arithmetic: `r[z]` := `r[x] - r[y]` | **destination unverified**: the only use has `x = z` |
| `string` | `23:E5 x y z` | guard `string(S, Length, Size)`: `r[x]` is a string; `r[y]` := its length, `r[z]` := its element size in bits | checked |
| `put_value` | `23:34 x y` | `r[x]` := `r[y]` | checked |
| `put_marked_value` | `23:36 x y` | `r[x]` := `r[y]`, the value now multiply referenced | the move is checked; the MRB marking is not modelled |
| `put_variable` | `23:33 x y` | `r[x]` and `r[y]` := one fresh unbound variable | checked |
| `set_value` | `23:14 x y` | argument `x` (from 1) of the goal being built := `r[y]` | checked |
| `set_variable` | `23:13 x y` | argument `x` of the goal being built and `r[y]` := one fresh variable | inferred from `ipl:boot/0`; not yet executed |
| `enqueue_goal` | `23:63 x c16` | make a goal of the predicate at the label with the `x` built arguments and put it on the ready queue | checked. That the newest goal runs first is the model's choice, not established |
| `execute` | `23:61 x c16` | continue as a reduction of the predicate at the label, arguments already in `r[0..x)` | checked |
| `new_string` | `22:D4 x y z` | `r[z]` := a new string of `r[x]` elements of `r[y]` bits | checked |
| `b_string_element` | `22:CD x y z`, next cell `w << 24` | `r[z]` := element `r[y]` of string `r[x]`; `r[w]` := the string | checked |
| `set_string_element` | `22:D1 x y z`, next cell `w << 24` | `r[w]` := string `r[x]` with element `r[y]` set to `r[z]` | checked, including the case that matters: `r[z]` unbound when the instruction is reached |

**A body built-in whose input is unbound waits.** In `convert_loop/4`
the compiled order is `string_element`, `set_string_element`,
`enqueue_goal convert_loop`, `execute convert_element`: the element
that `set_string_element` stores is still unbound when it is reached.
The built-in becomes a waiting goal, its output register gets a fresh
variable, and it runs when `convert_element` binds the element. The
test counts one such wait per string element (201). How the machine
represents the waiting built-in is not known; PDSS's
`body_builtin_suspend` (`emulator/goal.c`) is the nearest description.

**Strings.** `{STRG, address}` points at `{CDESC, pad << 27 | type <<
24 | words}` and then `words` 32-bit cells, elements packed from the
top bit; type 3 is 8-bit elements, 4 is 16-bit (`kbnheap.kl1`
`string_cdesc`). The packing order is read from string constants in
the image (they spell their text top byte first), not from the test.
The reference model copies on `set_string_element`; the machine may
update in place when the string is singly referenced.

## Trace

Both models can write the same trace, one line per event, and are
compared on it (`ref/pimm/lockstep_jtoa.py`, `bsv/run_pimm_jtoa.sh`):

    I pc cell      an instruction is taken (pc in cells from the load
                   address; cell = tag and value, ten hex digits)
    R n cell       register n is written by an instruction
    M addr cell    a memory cell is written
    E how          the reduction ends: done, fail, susp

The Bluespec core can also end with `E unimp` (an instruction or case
it does not implement) or `E error`; the reference model raises an
exception there, so neither can appear in a matching trace. Loading a
goal's arguments is not traced. The trace has no cycle numbers: the
two models agree on what happens and in what order, not on when.

Things this predicate shows about the compiler, useful for reading the
rest: range guards compile to `put_integer` and a comparison per bound;
33 constant clauses compile to one `hash_on_constant`, placed after the
`switch_on_non_integer` and before the range clauses even though the
source has the ranges first (the clauses are mutually exclusive, so the
order does not show).
