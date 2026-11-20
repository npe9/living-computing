# PIM/m KL1-B instruction semantics, from paired source and object

What each instruction does, settled one at a time from object code in
the PIMOS binaries whose KL1 source we have. This is the table both
the host reference model (`ref/pimm/pimm.py`) and the Bluespec model
are to follow. An instruction is listed only when a runnable check
depends on the reading; "inferred" marks what the check does not
exercise.

**Operand directions from source.** PIMOS's compiler
(`library/compiler/blt.kl1`) has a clause per built-in naming the
instruction it emits and which operands are read and written.
`asm/bltdir.py` reads all 87 guard and 120 body built-ins out of it;
every operand is marked. It agrees with each reading below that a run
has checked (`b_add`, `b_subtract`, `new_string`, `b_string_element`,
`set_string_element`, `string`, and `not_less_than a,b` = `a >= b`,
which the compiler emits for `X1 >= X2` and, operands swapped, for
`X1 =< X2`). The source is the 1992 release and the binaries are from
1994, so a run still outranks the table where the two could differ.

Notation: an instruction cell is `tag:op x y z`, with `x` = bits
23-16, `y` = bits 15-8, `z` = bits 7-0, `c16` = bits 15-0 signed.
`r[n]` is register n; the first argument of a goal is `r[0]`.
A label is `here + 2 + c16`, in cells.

Evidence so far: module `jis_to_ascii` in `pimm_ipl.kbn` against
`bios/boot/jtoa.kl1` (`ref/pimm/test_jtoa.py`): `convert_element/2` on
all 65,536 keys, and `convert/2` (through `convert_loop/4`) on five
strings, with eleven observed fault injections, one of which the test
does not catch (noted at `subtract`). A second module's predicate,
`scsi_common:get_4_bytes/4` against `bios/scsi/scsi_common.kl1`, is run
by `ref/pimm/lockstep_get4.py`, its oracle the source's own
`Int := ...` expression; `check_completion_code/4`, the first to build
structures, by `ref/pimm/lockstep_ccode.py`, its oracle the three
source clauses parsed from the text; `analyze_standard_format/5`, the
first to call another predicate, by `ref/pimm/lockstep_asf.py`. From a
third module, `exception_table:replace_argument/3`, the first to read
structures, by `ref/pimm/lockstep_repl.py`, its oracle the seven
source clauses parsed from the text. From a fourth, `shoen:ground_term/2`
with `ground_term/4`, `wait_vector/6` and `wait_and_unify/3`, on lists
and vectors, the first to run several goals at once, by
`ref/pimm/lockstep_ground.py`. The whole `jis_to_ascii` module also runs on the
Bluespec core in lockstep with the reference model (see Trace): every
instruction in the table is implemented there. Three readings no run
of this module can check, on either model, and injections confirm it:
`subtract`'s destination, `less_than` at equality, and whether
`execute` clears the alternative clause (`ref/pimm/lockstep_conv.py`).

| Instruction | Encoding | Meaning | Evidence |
|---|---|---|---|
| `try_me_else` | `23:68 _ c16` | the next clause is at the label; a failing guard goes there | checked |
| `switch_on_non_integer` | `23:28 x c16` | if `r[x]` is bound to an integer, fall through; otherwise go to the label. An unbound `r[x]` also records the variable as one the goal is waiting on | integer and atom cases checked; the unbound case by its consequence (the goal suspends) |
| `hash_on_constant` | `23:2D x c16`, then a word, then a table | `c16` is a mask. The next cell holds the miss label, relative to itself (`its address + 2 + value`). Then `mask + 1` slots, indexed by `r[x] AND mask`: `{atom, 0}` is empty; `{integer, count << 16 \| offset}` points, `offset` cells from the slot, at `count` pairs `{key, offset}`; a matching pair's target is `offset cell + 1 + offset` | checked (three of the five injections are here) |
| `switch_on_constant` | `23:2C x c16`, then `c16` pairs | Each pair is `{key, {integer, else << 16 \| offset}}`; both 16-bit fields are labels relative to the pair's second cell (`its address + 2 + value`). The pairs are compared in order with `r[x]` dereferenced (tag and value); a match goes to its `offset` label, no match to the last pair's `else` label. Every pair carries the same else label. An unbound `r[x]` is noted and takes the else label (the first pair's), as `hash_on_constant` takes its miss label: this last point is our reading by analogy, not from a source | encoding from `library/assembler/klb_opr.kl1` (`r_c16_c16_16s_sw`, `make_label`), checked against the image's `replace_position/3`; run in `lockstep_rpos.py` |
| `put_integer` | `23:31 x c16` | `r[x]` := integer `c16` | checked |
| `not_less_than` | `23:F1 x y` | guard: `r[x] >= r[y]`, else fail to the next clause | checked; unbound operands not exercised |
| `b_subtract` | `22:C1 x y z` | `r[z]` := `r[x] - r[y]` | checked |
| `b_add` | `22:C0 x y z` | `r[z]` := `r[x] + r[y]` | checked |
| `equal` | `23:F2 x y` | guard: `r[x] = r[y]`, integers | checked |
| `and` | `23:EA x y z` | guard arithmetic: `r[z]` := `r[x]` and `r[y]` | checked |
| `get_atom` | `23:C0+r`, atom in the low 24 bits | unify `r[r]` with the atom | checked (`scsi_common:check_completion_code/4`) |
| `put_vector_N` | `23:38+N x` | `r[x]` := a new vector of N cells; the structure pointer is set to its first cell | checked for N = 2, 3, 4. The pointer's tag is written with the low bit set, as the image builder writes every pointer; what the machine does there (MRB) is not known |
| `write_atom` | `23:23`, atom in the low 24 bits | store the atom at the structure pointer and advance it | checked |
| `write_value` | `23:25 x` | store `r[x]` at the structure pointer and advance it | checked |
| `write_variable` | `23:24 x` | the element at the structure pointer becomes a new unbound variable, `r[x]` a reference to it; advance | checked with `x` = 31 only (`analyze_standard_format/5`): the cell and the register are in the trace, nothing reads the register. That the variable is the element itself is our choice |
| `switch_on_non_list` | `23:2A x`, label | guard: `r[x]` a list, the structure pointer is set to its car; otherwise go to the label (an unbound `r[x]` is noted first) | checked (`shoen:ground_term/2`). |
| `switch_on_non_vector` | `23:2B x y`, then a cell holding the label | a vector: `r[y]` := its number of elements (the compiler's `index.kl1` calls the register `Ari` and switches on it), the structure pointer at its first; otherwise go to the label (an unbound `r[x]` is noted first) | checked (`shoen:ground_term/2`) |
| `vector` | `23:E4 x y` | guard `vector(X, ^Size)`: `r[y]` := the number of elements | checked |
| `vector_element` | `23:EE x y z` | guard `vector_element(V, I, ^E)`: `r[z]` := element `r[y]`, a reference if it is an unbound variable; fails outside 0..size-1 | checked, except the index equal to the size |
| `mark_element` | `23:1C x y` | MRB marking of an element: nothing, no reference counts | runs; nothing to observe |
| `new_vector` | `22:D3 x y` | body `new_vector(Size, ^V)`: `r[y]` := a vector of `r[x]` cells of integer 0 (PIMOS manual) | checked for 1..6 |
| `set_vector_element` | `22:D0 x y z`, then `w4 w5` | body `set_vector_element(V, I, New, ^Old, ^V1)`: `r[w5]` := a copy of `r[x]` with element `r[y]` replaced by `r[z]`, `r[w4]` := the old element. Does not wait for `New` (manual: suspends on Vector or Position only). Always a copy, as `put_reused_structure` | checked on vectors made by `new_vector`; copying an unbound element is not exercised |
| `put_nil` | `23:32 x` | `r[x]` := nil, the atom 0 (`library/kbn/kbnatom.kl1`: "The atom number of '[]' is fixed to zero") | checked |
| `wait_vector_N` | `23:A8+N x` | guard: `r[x]` is a vector of N cells; the structure pointer is set to its first | checked for N = 2, 3, 5 (`exception_table:replace_argument/3`), including the wrong size and an unbound `r[x]` |
| `read_variable` | `23:B4 x` | `r[x]` := the element at the structure pointer; advance. An element that is an unbound variable is taken as a reference to it | checked |
| `put_reused_structure` | `23:2F x y n` | `r[x]` := a structure of n cells to fill with `write_*`, under the tag of the structure in `r[y]` | checked for vectors of 2, 3, 5. The machine reuses `r[y]`'s cells when nothing else refers to them (MRB); the models keep no reference counts and always take new cells, which is what the machine does for a shared structure |
| `get_bound_value` | `23:BD x y` | unify `r[x]` with `r[y]` (as `get_value`; the name says `r[y]` is known to be bound) | checked for a vector against an unbound variable |
| `b_and`, `b_or` | `22:C7`, `22:C8 x y z` | `r[z]` := `r[x]` and / or `r[y]`, bitwise | checked (`scsi_common:get_4_bytes/4`) |
| `b_shift_left` | `22:C5 x y z` | `r[z]` := `r[x] << r[y]`, 32 bits | checked for a count of 8; a count outside 0..31 is an exception in PDSS (`blt_basic.c`) and stops the model |
| `b_shift_right` | `22:C6 x y z` | `r[z]` := `r[x] >> r[y]`, logical (manual, `shift_right`: "Logically shifts Integer to the right"), 32 bits | checked (`lockstep_dec0.py`), logical against arithmetic by the 8-bit strings of `lockstep_deca.py`; a count outside 0..31 is an exception, not modelled |
| `shift_right` (guard) | `23:E9 x y z` | `r[z]` := `r[x] >> r[y]`, logical; an unbound operand is noted and the guard fails; a non-integer or a count outside 0..31 fails the guard (manual: "Fail, Exception") | checked, logical against arithmetic included (`lockstep_rss.py`); the count limit is not run |
| `integer` (guard) | `23:E2 x` | succeeds if `r[x]` is an integer; unbound is noted and fails (manual: suspend), anything else fails | checked, except the unbound case (a `wait` always precedes it) |
| `modulo` (guard) | `23:F8 x y z` | `r[z]` := remainder of `r[x]` by `r[y]`; an unbound operand is noted and fails; a non-integer or a zero divisor fails the guard (manual: "Fail, Exception"). The remainder takes the dividend's sign, as PDSS's C `%` (`emulator/blt_basic.c`): for negative operands that is PDSS's behaviour, not established for PIM/m. On the Bluespec the divide box takes 32 steps; the count is ours | checked for a small positive length mod 2 only (`lockstep_deca.py`); negative operands and the zero divisor are NOT run |
| `put_vector_1`, `_5`, `_6` | `23:39`, `3D`, `3E` | as `put_vector_2..4` | `_5` checked; `_1`, `_6` not run |
| `put_list` | `23:2E x` | two new cells, car then cdr, filled by the two `write_*` that follow; `r[x]` := a list pointer to them | checked (`lockstep_dect.py`) |
| `put_constant` | `23:30 x`, then a cell | `r[x]` := the whole next cell (`klb_opr.kl1` `r_c40`); two cells | checked for an integer constant (`lockstep_deca.py`); the tag being carried is NOT checked |
| `get_nil` | `23:BA x` | unify `r[x]` with `[]` (the atom 0) | checked |
| `wait_atom` | `23:80+r`, atom in the low 24 bits | guard: `r` dereferenced must be that atom; unbound is noted and fails | checked |
| `get_value` | `23:BC x y` | unify `r[x]` with `r[y]` | checked for integer against unbound only |
| `get_integer` | `23:B9 x c16` | unify `r[x]` with integer `c16` | checked against unbound only |
| `otherwise` | `23:6A x c16` | clauses below apply only if none above can: if a guard above was waiting on a variable, the goal suspends; else continue | both cases checked. `x` is the arity and the label is the predicate's own first instruction; what the machine uses them for is inferred (re-entry after suspension) |
| `suspend` | `23:69 x c16` | end of the clauses: suspend if a guard was waiting, else the reduction fails. Same operands as `otherwise` | suspension checked; the failure case inferred |
| `collect_value` | `23:1D x` | reclaim what `r[x]` refers to (MRB) | not modelled: a no-op in the reference model |
| `proceed` | `23:60` | the goal is done; the machine takes the next ready goal | checked |
| `wait` | `23:E0 x` | guard: `r[x]` is bound; if not, note the variable and fail to the next clause | both cases checked |
| `wait_integer` | `23:A1 x c16` | guard: `r[x]` is the integer `c16` | checked (0 ends `convert_loop`; 16 selects 16-bit strings) |
| `less_than` | `23:F0 x y` | guard: `r[x] < r[y]` | weakly: the only use is `0 < N` after `N = 0` has been tried |
| `subtract` | `23:F5 x y z` | guard arithmetic: `r[z]` := `r[x] - r[y]` | the run cannot tell (the only use has `x = z`); the destination is from the compiler's table, `asm/bltdir.py`: `iio` |
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

**Vectors and terms.** A vector of 1 to 6 elements is `{VECTn,
address}` pointing at its n element cells, with no header; the empty
vector is `{VECT0, 0}`; 7 or more have a descriptor (`{VECT, a}` ->
`{VDESC, a+3}`, `{INT, n}`, `{INT, n}`, elements). A list cell is
`{LIST, address}` -> car, cdr. This is `library/kbn/kbnheap.kl1`
`heap/10`, the code that lays out the image's constants. A compound
term `f(a, b)` is the vector `{f, a, b}`: `check_completion_code`
builds `abnormal(no_status(C, D))` as a 3-vector inside a 2-vector, and
the test reads it back by atom name. Vectors of up to 6 are built, read
and updated (`put_vector_N`, `wait_vector_N`, `read_variable`,
`new_vector`, `set_vector_element`; `bsv/PimmVBox.bsv`), and list cells
are read and rebuilt (`switch_on_non_list`, `put_reused_structure`);
`put_list` is not run yet, and the long vector form (7 or more, with a
descriptor) stops both models.

**Strings.** `{STRG, address}` points at `{CDESC, pad << 27 | type <<
24 | words}` and then `words` 32-bit cells, elements packed from the
top bit; type 3 is 8-bit elements, 4 is 16-bit (`kbnheap.kl1`
`string_cdesc`). The packing is checked against the image itself:
`test_jtoa.py` reads the IPL's message strings with it ("Illegal IPL
File", "Unable to Decode Constant").
The reference model copies on `set_string_element`; the machine may
update in place when the string is singly referenced.

## Trace

Both models can write the same trace, one line per event, and are
compared on it (`ref/pimm/lockstep_jtoa.py`, `bsv/run_pimm_lockstep.sh`):

    I pc cell      an instruction is taken (pc in cells from the load
                   address; cell = tag and value, ten hex digits)
    R n cell       register n is written
    A n cell       argument register n (of the goal being built) is written
    M addr cell    a memory cell is written
    E how          the reduction ends: done, fail, susp
    G addr         the goal record at addr is taken from the ready queue
    W addr         the suspended goal at addr is woken
    Q              the ready queue is empty

Every register and memory write is traced, whoever makes it: an
instruction, the scheduler taking a goal, a wake-up, or the bench
making a variable or a goal. In the Bluespec the `M` line is printed
where the write reaches the RAM, not where it is requested. The
Bluespec core can also end with `E unimp` (an instruction or case it
does not implement) or `E error`; the reference model raises an
exception there, so neither can appear in a matching trace. The trace
has no cycle numbers: the two models agree on what happens and in what
order, not on when.

## Runtime state

How the PIM/m firmware kept goals, the ready queue and suspended goals
is lost with it. What follows is **this project's design**, shaped
after PDSS (`emulator/record.h`, `goal.c`) and fixed in
`asm/pimm_layout.py`, which both models read. It will grow (priorities,
the shoen a goal belongs to, MRB) and is not a claim about the machine.

**What the literature says against it** (`docs/literature_gaps.md`
section 0, a search made 2026-11-20). PIM/m's KL1 system was converted
from the Multi-PSI/V2 microprogram (Taki, FGCS'92), so Multi-PSI/V2
reports carry over and VPIM (the other PIMs) is a design reference
only. Against those sources this design is wrong or unconfirmed in
these ways, none yet changed in the models:

- one ready list, where the machines have a goal stack per priority
  (newest-first within a priority is confirmed);
- `HOOK` -> suspension record always, where the documented siblings use
  `HOOK` -> the goal record itself for a single waiter and `MHOOK` ->
  suspension records sharing a flag record for several;
- a status word in the goal record, which no source shows;
- waking on variable-to-variable binding, where VPIM and PDSS merge the
  hook chains;
- a heap that only grows, where PIM/m has free pools, MRB reclamation
  and a copying collector.

A waiting built-in as a hooked goal, the low tag bit as the MRB, and
the string descriptor agree with the sources. PIM/m's own field-level
layouts were not found in print; the firmware binary we hold
(`psdpim`'s `pimm.MEkbn`) may hold them; its microprogram is not read.
The console's inspector for the multiple suspension record offers
`prev`, `next`, `goal`, `rival` (`pseudo_pimm_firmware.md`); whether
those are its fields is not established.

- **Heap.** A heap pointer register; cells are taken in order and never
  returned. Running out stops both models.
- **Goal record**, 4 + n cells: `{INT, next record in the ready queue
  or 0}`, `{INT, status}` (0 ready, 1 suspended, 2 taken),
  `{INT, code address}`, `{INT, n}`, then the n arguments. Addresses in
  cells are absolute.
- **Ready queue.** A register holding the newest ready record; a new or
  woken goal goes on the front and the front goal runs next (PDSS's
  default, `enqueue` to the head of its priority's queue). No
  priorities yet.
- **Unbound variable.** `{UNDF, 0}`, or `{HOOK, first suspension
  record}` when goals wait on it. Dereferencing stops at either.
- **Suspension record**, 2 cells, one per (goal, variable):
  `{INT, next suspension record on this variable or 0}`,
  `{INT, goal record}`.
- **Suspending.** `otherwise`/`suspend` write a new suspended record
  (entry = the instruction's label, arguments `r[0..arity)`) and hook it
  on each variable the guards met unbound, in the order met. A variable
  met twice is hooked twice; the status cell makes the goal wake once.
  The record the goal came from is not reused.
- **Binding** writes the value over the variable's cell, then walks its
  suspension list, newest first: each goal still suspended becomes
  ready and goes on the queue (so the oldest waiter runs first). A
  hooked variable bound to another unbound variable wakes its goals
  too; they run, find the second variable and suspend on it. PDSS
  merges the lists instead; this is simpler and costs reductions.
- **A waiting built-in is a goal.** A body built-in with an unbound
  input becomes a suspended goal whose code is a stub from a fixed
  table placed after the image (`asm/pimm_stubs.py`: the built-in on
  `r[0..n)`, a `get_value` per output, `proceed`), with the
  instruction's operands as arguments, a fresh variable for each
  output, hooked on the first unbound input. PDSS does the same with
  its `dc_*` pseudo-code (`body_builtin_suspend`). Because a stub is
  ordinary code, a test can also spawn one directly.

Things this predicate shows about the compiler, useful for reading the
rest: range guards compile to `put_integer` and a comparison per bound;
33 constant clauses compile to one `hash_on_constant`, placed after the
`switch_on_non_integer` and before the range clauses even though the
source has the ranges first (the clauses are mutually exclusive, so the
order does not show).
