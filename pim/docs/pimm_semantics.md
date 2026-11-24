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
| `write_nil` | `23:22` | store `[]` (atom 0) at the structure pointer and advance it | checked (`lockstep_gca.py`) |
| `put_vector` (general) | `23:3F x`, size in the low 16 bits | `r[x]` := a new vector of that many cells in the long form (descriptor), the structure pointer at its first element; `load_module` builds `module/9`, ten cells, with size 10. Sizes below 7 are refused (the image has 7, 8 and 10 only) | checked for 10 (`lockstep_lmod.py`); the size's upper byte is NOT checked |
| `execute_external` | `23:62 n`, label | the same goal goes on at a predicate of another module. The label locates a four-cell predicate descriptor in the caller's GC area (TM-662 fig. 2: cache field, `{REFx}` to a cell holding `{REFo}` to the module, key `{atom, arity << 24 \| name + arity}`, module name). The called module's code area begins with its predicate entry table: `{INT, mask}`, `mask + 1` slots indexed by key AND mask, a slot `{INT, count << 16 \| offset}` to pairs `{key, {INT, off}}`, the code at the off cell + off. Read from the image: all 59 entries of its 20 modules follow it, and all 76 calls resolve. The cache field (filled on first call on Multi-PSI/V2) is NOT used or written: what the machine writes is not known; both models look up at every call and refuse a non-zero cache | checked: 49 of the 76 calls land where `asm/kbndis.py` finds the predicate by its head (`lockstep_ext.py`). A second pair in a slot and the caller's guard state are NOT checked |
| `wait_value` | `23:A4 x y` | the guard `X = Y` on two arguments (TR-246 p. 5); an unbound one is noted and the guard fails. Atomic values and strings: two strings are the same when their descriptors and every word are (PDSS `emulator/passive.c` `passive_unify`), a string and an atomic value are not; lists, vectors, and one variable twice, are refused by both models | checked on integers (`lockstep_ext.py`) and on strings equal and unequal (`lockstep_atab.py`: the pool's keys); a string against an atomic value is not run |
| `wait_constant` | `23:A0 x`, then a cell | the guard `X = constant`, the constant the whole next cell; two cells. Atomic values only | checked for -2^31 (`lockstep_ext.py`) |
| `tag_and_value` (guard) | `23:76`, function 4: `y z`, third register in the next cell's top byte | `r[z]` := the tag, the third := the value of `r[y]`'s cell, as integers; an unbound one is noted and the guard fails; two cells. Sources: PDSS `emulator/blt_system.c`; `library/unloader/encoder.kl1` writes instruction cells with it and the `.sav` files hold their tags as the image has them. Whether a tag's MRB bit is returned is NOT established: the tag is returned as it stands | the value is checked (`lockstep_ptab.py`); the tag only as both models agree |
| `new_instruction` | `22:D5 x y z` | `r[z]` := the cell with tag `r[x]` and value `r[y]` (`decoder.kl1` `decode_atomic`, `encoder.kl1` `decode_pred_hash_key`). Both models refuse reference and pointer tags (4..1Fh) | checked for tag 2: the keys it makes are the image's (`lockstep_ptab.py`) |
| `b_vector_element` | `22:CC x y z`, fourth register in the next cell | `vector_element(V, I, ^E, ^V1)`: `r[z]` := element, the fourth := the vector (manual) | checked (`lockstep_ptab.py`) |
| `add` (guard) | `23:F4 x y z` | `r[z]` := `r[x]` + `r[y]`; an overflow fails the guard (manual) | the sum is checked; the overflow is NOT run |
| `wait_nil` | `23:A2 x` | guard: `r[x]` is `[]` | run (`lockstep_ptab.py`); another atom there is NOT run |
| `wait_list` | `23:A6 x` | guard: `r[x]` is a list; the structure pointer at its car | checked |
| `read_atom` | `23:B3`, atom in the low 24 bits | the element at the structure pointer must be that atom; an unbound one is noted and the guard fails | run; another atom there is NOT run |
| `switch_on_non_atom` | `23:29 x`, label | next if `r[x]` is an atom, else the label; an unbound one is noted | checked (`lockstep_ext.py`) |
| `write_marked_value`, `set_marked_value` | `23:27 x`, `23:16 n y` | as `write_value`, `set_value`, with the MRB of the source register and of the copy set (see "The MRB") | checked: both writes are traced |
| `set_integer` | `23:11 n`, c16 | goal argument n := the signed 16-bit integer | checked for non-negative operands |
| `put_structured_constant` | `23:37 x`, label | `r[x]` := the cell at the label, a place in the GC area holding the pointer to a constant built outside the module (TM-662). A `{REFx}` there is `module#M`: a reference to the image's module-table cell, or in a loaded module to the variable the linker binds to the module object; the register gets the cell as it stands and its users dereference it (`ipl:boot/0` passes `module#ipl` to `predicate_to_code`). Run on the reference model alone by `pim:go/4` after the whole link (`longrun_ipl.py --reference --go`); NOT yet in a lockstep test: its image sites lead into shoen | checked: three error clauses return their string (`lockstep_ptab.py`) |
| `collect_list`, `collect_vector` | `23:1E x`, `23:1F x n` | MRB reclamation of a list cell or vector: nothing here, as `collect_value` (no reference counts) | run |
| `enqueue_goal` with more than 11 arguments | `23:63 n`, label | a goal has 11 argument slots: the compiler packs the arguments from the 11th on into a vector passed as the 11th (`library/compiler/pack.kl1`, `max_goal_slots`). The called predicate reads `r10`, `r11`, ... with no code to unpack, so the firmware spreads the vector; where is not known. Both models spread it as the goal is made and keep every argument in their own record. Refused: no vector, another size, more than 16 arguments | checked for 12 (`lockstep_pack.py`) and 13 (`lockstep_file.py`); the refusals are NOT run |
| unification of two lists or two vectors (any instruction that unifies) | — | not done on the spot: a ready goal of the stub `unify_step` (`22:01`, OURS, `asm/pimm_stubs.py`) with arguments X, Y, 0 unifies the elements one pair each time the step is taken, an element taken with its MRB on if its structure's is. From PDSS (`emulator/unify.c` `make_unify_vector_vector_goal_and_enqueue`, `dc_unify_vector_vector2`); PIM/m's own way is not known. Vectors of seven or more are refused | `lockstep_unif.py`; the MRB rule is not caught by it |
| `scsi_where` | `22:A0 x` | `r[x]` := `[{0, 0, 0, 6}]`: one SCSI port, cluster 0, processor 0, port 0, own unit 6. The grammar and the single-FEP value are the PIMOS source's stand-in for the built-in (`bios/boot/scsi_conf.kl1`); what the firmware read is not known | checked (`lockstep_where.py`, a bench-made code) |
| `predicate_to_code` | `22:F3 x y z`, a fourth register in the next cell | `r[w]` := the code of predicate `r[y]`/`r[z]` in the module object `r[x]`, or the vector `{Module, Name, Arity}` if the module has none (PIMOS manual `e-builtin.tex`; PDSS differs). A code is `{COD, first instruction}`: the target is assumed (`lockstep_p2c.py` header) | checked on the image's 349 predicates (`lockstep_p2c.py`) |
| `apply` | `22:F1 x y` | `apply(Code, Args)`: a new ready goal of the code `r[x]` with the elements of the vector `r[y]` as its arguments; waits for either (PIMOS manual `e-builtin.tex`). The goal is made as PDSS makes it (`emulator/blt_system.c` `blt_b_apply`): each element taken with its MRB on if the vector's is. The manual's exceptions (not a code, not a vector, the count differs from the predicate's) are refused, as is a vector of seven or more | checked, with the IPL's own `apply` site (`lockstep_apply.py`) |
| `create_shoen` | `22:E0 x y z`, four more registers in the next cell | `create_shoen(MinPrio, MaxPrio, ExcepMask, Code, Argv, ^Report, ^Shoen)`, format `r7`. **PIM/m-sourced**: the encoding and the directions (`assembler/inst_tab.kl1`:332-362, `klb_opr.kl1`:144-154, `compiler/blt.kl1`:567-569), and that the outputs may be the input registers (the image's `shoen:execute/4`, cell 15553, is `22:e0040506 / 00:00010001`: Code and Report both `r0`, Argv and Shoen both `r1`), so every input is read before an output is written. The manual does not document it. **What it does is not PIM/m-sourced** ("Shoen" below): the three first operands are waited for, must be integers and are dropped; a shoen record, a fresh Report variable, the handle `{SHREC, record}`, and one parked goal `apply(Code, Argv)` of the new shoen. Code and Argv are not waited for. Refused: a priority or mask that is not an integer (`shoen:execute1/7` passes vectors) | checked (`lockstep_shoen.py`, through the image's `execute/4` and through its stub); the refusal is not in the suite (observed by hand on both models, the test's header) |
| `start_shoen` | `22:E1 x y` | `start_shoen(Shoen, ^NewShoen)` (encoding and directions **PIM/m-sourced**, `inst_tab.kl1`, `blt.kl1`:537-601; the image's `control/2`, cell 15755). A dormant shoen: 8 is reported first, then it is started and its parked goal goes on the ready queue (the order is VPIM's, **carried over**); `r[y]` := the same handle (**ours**). Refused: a shoen that is not dormant, anything but a handle | checked (`lockstep_shoen.py`); a second start is refused on both models, observed by hand (the test's header), not in the suite |
| `code` (guard) | `23:FA x y z`, a fourth register in the next cell | succeeds if `r[x]` is a code (whole tag 26h), with `r[y]` := arity, `r[z]` := its module, the fourth := its offset from the module's descriptor cell; anything else fails (PIMOS manual) | checked, outputs from the trace (`lockstep_p2c.py`) |
| `atom` (guard) | `23:E1 x` | "If X is an atom, this predicate succeeds, otherwise it fails" (PDSS manual); an unbound X is noted | run succeeding only (`lockstep_link.py`: the IPL's link table); a non-atom is not run |
| `floating_point` (guard) | `23:E6 x` | "If X is a floating point, this predicate succeeds, otherwise it fails" (PDSS manual); an unbound X is noted. The type test only | run failing only (`lockstep_run.py`) |
| `divide` (guard) | `23:F7 x y z` | `r[z]` := `r[x] / r[y]`; a non-integer, a zero divisor or the overflow (the least integer by -1) fails the guard (manual: "failure or exception"). Truncated towards zero as PDSS's C `/`, not established for PIM/m | run on 3 / 2 (`lockstep_run.py`); a negative operand, zero and the overflow are not run |
| `shift_left` (guard) | `23:E8 x y z` | `r[z]` := `r[x] << r[y]`, 32 bits; a count outside 0..31 fails the guard (manual), as `shift_right` | checked (`lockstep_run.py`, against the module's source); the count limit is not run |
| `put_marked_variable` | `23:35 x y` | as `put_variable`, both references with the MRB on (PDSS `emulate.c` `KL1B_PUT_MARKED_VARIABLE`) | checked: both register writes are traced |
| `read_variable_without_deref` | `23:A7 x` | as `read_variable`. The compiler writes it for `read_variable` when the clause collects the structure and not the element (`library/compiler/regass.kl1` `convertIfNotCollected`); the machine's `read_variable` dereferences what it takes at once and this does not, and here neither does (the instruction that uses the register dereferences) | checked (`lockstep_run.py`: the list hashed) |
| `display_console` | `23:7F x` | `display_console(X)`: "displays the current value of X on the console window, even if this variable is unbound" (PDSS manual): it does not wait and cannot fail. Here the console is the trace: a `C` line with the dereferenced value and, for a string, an `S` line for its descriptor and each word. Displayed when the instruction is executed, so a clause tried again displays again. How PIM/m's console SHOWED a value (an integer's digits, where a line ends) is not known and not modelled | checked on 8-bit strings (`lockstep_cons.py`: a real file's comment and a file's name, through the IPL's `display_console/1` and `jis_to_ascii`); a non-string or unbound value is not run |
| `new_atom` | `22:D2 x` | `new_atom(^Atom)`: `r[x]` := an atom no other holds, without a name ("creates a new atom ... The atom has no printing name", PDSS manual). The number is OURS: a counter up from 10000h, clear of the image's 486 atoms. PDSS counts down from the top of its table; PIM/m gave each processor a range (`supply_atom_number`, the server in `pimos::top`) whose first value is not known | checked (`lockstep_atab.py`): one atom per name, none of the image's |
| `hash` | `22:F6 x y z` | `hash(X, ^Value, ^NewX)`: "unifies Value with a hash code computed according to X, and also unifies NewX with X" (PDSS manual); waits for X. The code is PDSS's (`emulator/blt_system.c` `blt_b_hash`): an atom's or integer's value, -1 for a list, a vector's size, a string's word count plus a mix of its first and last words. PIM/m's function is lost with the firmware: any function gives a correct table, so WHERE an entry lies in a hashed table is not the machine's. Long vectors and other types are refused | run on strings (the IPL's atom table); a constant function in both models passes the test, as it must |
| `floating_point_not_less_than` (guard) | `23:FC`, function 3: `y z` | "If both Float1 and Float2 are floating points and the value of the former is larger than, or equal that of the latter, this predicate succeeds. Otherwise it fails" (PDSS manual); an unbound one is noted. No floating point here: two floats are refused | run failing only (the IPL's pool tries it on every key that is neither atom nor integer) |
| `new_module` | `22:D6 x y` | `new_module(Vector, ^Module)`: `r[y]` := `{MOD, a}` -> `{CDESC, 06 << 24 \| n}` and the vector's other n elements as they are, the shape of the image's 20 modules. `library/loader/loader.kl1`: "First Element is for CDESC created by new_module"; its caller puts `06000000h \/ (size - 1)` in element 0. A copy on both models (whether the machine converts in place is not known). A reference to a variable is kept (the loader leaves one where another module will be). Refused: an element 0 that is not that integer, an unbound cell in the vector itself | checked (`lockstep_newm.py`); the refusals are NOT run |
| `set_atom` N | `23:00`..`0F`, atom in the low 24 bits | goal argument N := the atom (`assembler/inst_tab.kl1`) | checked (`lockstep_file.py`) |
| `calculate_priority_from_minimum` | `22:ED x y` | `r[y]` := the logical priority for the relative priority `r[x]`, 0..4096, in the shoen's range (manual). No shoen here: the range is taken as 0..4096, so the result is the operand. **The range is ours** | both models agree; nothing reads the value |
| `enqueue_goal_with_priority` | `23:64 x`, label; arity in the next cell's top byte | as `enqueue_goal`, two cells (`assembler/klb_opr.kl1` `p(r_c16_c8_exe)`; the image's five sites agree with their `set_*` count). `r[x]` must be an integer and is **dropped**: one ready queue here, a goal stack per priority on the machine, so the order goals run in is not the machine's. More than 11 arguments is refused | checked (`lockstep_file.py`) |
| `enqueue_goal_to_processor` | `23:65 x`, label; arity in the next cell's top byte | `Goal@processor(N)`: as `enqueue_goal_with_priority`'s operands (`assembler/klb_opr.kl1` `p(r_c16_c8_exe)`), `r[x]` the processor (TM-1044 `enqueue_to_processor(.., Rprocessor, ARITY)`, as listed in `literature_gaps.md`). **One processor here, number 0 (ours)**: for 0 the goal is made as `enqueue_goal` makes it; any other number is refused | checked (`lockstep_body.py`, `scsi_fep_module:create/7`: the goal runs `$bar2/2` into `scsi:create/2`, which waits for its first argument and fails on a non-integer); the refusal is NOT run |
| `read_eagerly` | `23:6B` | what the compiler writes for `alternatively.` (`compiler/indexornot.kl1` `compile_one_block`). The clauses after it are tried "not only when the first clause fails but also when it suspends" (TR-483 2.4.4); the instruction: "if external references are on the suspension stack, perform Eager Read on them", no branch (TM-1044 s3; both quotations from `literature_gaps.md`, the reports not reopened). One processor has no external references: **nothing is done**; the variables noted so far stay noted | checked (`lockstep_alt.py`): `scsi_fep_util:set_attention/1`, `close_attention/1`, `close_device/2`, and `scsi_fep_file:reply_with_attention/4`, where a goal reaches `suspend` past it with the variables the earlier clauses noted and suspends (an injection that forgets them is caught there) |
| `scsi_init` | `22:DF x y z` | `scsi_init(^Obj, ^TargetInterruptVector, ^Info)`, three outputs (`compiler/blt.kl1`). **The values are OURS**, those of the stand-in `bios/scsi/scsi_blt.kl1` (in the image at cell 13952): `1`, `{0,0,0}`, `{16000,8,4,0}`. `Info` element 0 is the largest transfer; `scsi_fep_module` makes its two packet buffers that long. The 16000 is the DEVICE's (`fep.py` `MAX_BUFFER`): it is asked (the trace's `B init`), and on the core comes over the port (`bsv/PimmScsiBox.bsv`). Order: `Obj` written, the device asked, then each vector's cells and its register. Refused without a device (`Machine.fep`; on the bench, no tape) | checked (`lockstep_scsi.py`, at its site `scsi:create/2`, the device's size 1000); `ref_scsi.py` on the reference |
| `scsi_command` | `22:DB`, seven registers (four in the next cell) | `scsi_command(Obj, {Unit, LUN, CDB, Length, Dir, Buffer, 0}, ^Data, ^TransferredLength, ^Id, ^Result, ^NewObj)` (`compiler/blt.kl1`). From its callers (`scsi:command_executer/2`, `scsi_processor`, `scsi_common`): Dir 0/1/2 = none/out/in, `Result` 0 = success, `Data` the whole buffer again (the caller's next buffer) with what was received written in. **OURS**: it waits for every element of the vector, as `string_operation` does (the stub's goal on the first unbound one); `Id` counts commands; `NewObj` = `Obj`; `Data` for bytes received is a NEW 8-bit string as long as the buffer (the bytes, then the rest of the buffer's, pad zero), for none the buffer itself; `TransferredLength` is the bytes received for Dir 2, else `Length`; a command the device cannot finish yet gives `Id` and `NewObj` at once and leaves the other three as new variables, unbound until the device has the reply; the waiting commands are held outside memory (Python's list; the core's box, at most four), given to the device again after any command that finishes (before its outputs are written) and when the machine has run dry (`Machine.scsi_poll`; the script's `POLL`), oldest first, a finished one's three variables unified in order. Every try is one `B` line (Trace). The device is `ref/pimm/fep.py`; on the core it is outside, on a port. Refused: a vector not of seven, a seventh element that is not 0, a length over the buffer, a CDB or buffer not of 8-bit elements | checked (`lockstep_scsi.py`: at its site `scsi:command_executer/2`, TEST UNIT READY, SEND, RECEIVE, a reply cut in two, a command that waits finished inside a SEND and one at a poll, an element waited for; the refusals NOT run). `ref_scsi.py`'s IPL parts on the reference only (they need the merger's vectors). Injections in both tests' headers |
| `b_string` | `22:CB x y z`, fourth register in the next cell | body `string(X, ^Size, ^ElementSize, ^NewString)`: "The size of string X is unified with Size, the element bit width is unified with ElementSize, and X is unified with NewString" (PIMOS manual, `e-builtin.tex` line 844; directions in `compiler/blt.kl1`) | checked at its stub (`lockstep_body.py`: 8-, 16- and 32-bit strings, the empty string, an unbound X) and at three of its five real sites (`lockstep_elw.py`, `scsi_fep_module:send_last_packet/9` and `copy_str8_elements/7`) |
| `b_divide`, `b_modulo` | `22:C3`, `22:C4 x y z` | `divide` and `modulo` in a body (manual, `e-builtin.tex` lines 285, 303: quotient, remainder), the guards' arithmetic (truncation towards zero, the dividend's sign: PDSS's, not established for PIM/m); a zero divisor is the built-in's exception, refused | checked (`lockstep_body.py`): `scsi_fep_module:str8_to_msg/3` on replies whose string is not last (a wrong quotient misplaces what follows), `str16_to_str8/2` on even and odd lengths, and eleven signed pairs at the stubs with the answers written out; the refusals are NOT run |
| `not_equal` | `23:F3 x y` | guard `not_equal(Integer1, Integer2)`, `X =\= Y`: "Succeeds if Integer1 is not equal to Integer2" (manual, `e-builtin.tex` line 206) | checked on integers, succeeding and failing (`lockstep_alt.py`, `scsi_fep_file:reply_with_attention/4`, its only site in the image); an unbound or non-integer operand is NOT run |
| `wait_vector_1`, `_4`, `_6` | `23:A9`, `23:AC`, `23:AE` | as `wait_vector_2` | checked (`lockstep_alt.py`): 4 in `scsi:request_manager/3`, with the wrong size; 6 in `scsi:command_executer/2` up to its `scsi_command` (passing with an unbound first element, failing on the size); 1 has NO site in the IPL image and is run on six cells of code the bench writes into the heap |
| `merge` | `22:F0 x y` | `merge(In, ^Out)` "creates a built-in constant time merger" (manual); as compiled the first operand is the OUTPUT stream as given, the second receives the input (`compiler/blt.kl1`). **Not the machine's merger**: PIM/m's input is a cell of its own tag (`MGHOK`) pointing at a record {output}{number of inputs} (TR-466 3.3) and acts at unification; here the input is a variable with a goal waiting on it, whose code is the stub `merge_in` (`22:00`, ours, an opcode the firmware's decode table leaves empty; refused elsewhere), and the output appears after a goal switch. The logic is the manual's. A vector on the input adds as many inputs as it has elements ("When a vector is unified to an MHV, as many input streams (MHVs) as the arity of the vector are added to the merger process and each element of the vector is unified to each new input stream", TR-466 3.3): REFERENCE MODEL ONLY, run by `ref_scsi.py` (`scsi_fep_general:request_device_io/5` binds two merger inputs to `{J, K}`); the Bluespec refuses it. Why it is still so (2026-11-23): the reference writes each new input's goal record straight from cells, no register written, and the core's goal box makes a record only from the registers or the argument registers, whose writes are in the trace; either the reference goes through the argument registers (as its `apply` does) or the goal box gets a third way to make a record. Not decided. Refused: an output that is not a variable, a non-stream | checked against a dictionary through `ipl_pool:keyed_set/2` (`lockstep_pool.py`); the refusals are NOT run |
| `put_vector_0` | `23:38 x` | `r[x]` := the empty vector `{VECT0, 0}` | checked (`lockstep_pool.py`) |
| external call from a LOADED module | as above | the descriptor's module field is dereferenced to the module object `{MOD, descriptor cell}`: in the image through the module table, in a module the IPL loaded through the variable its linker bound (`ipl_link_table:unify_modules/1`). Checked on the image by `lockstep_ext.py`; from a loaded module only on the reference model, by `pim:go/4` after the whole link (2026-11-23: it ran past its first external call). No lockstep test has two linked loaded modules: the smallest closed set of files is some 49 M cells |
| `set_nil`, `enqueue_goal_external` | `23:12 n`; `23:66 n`, label | goal argument n := `[]`; `enqueue_goal` with the predicate found as `execute_external` finds it (`klb_opr.kl1` `p(c8_c16_ext)`) | checked (`lockstep_load.py`) |
| `string_operation` | `22:B0 x y z`, fourth register in the next cell | `string_operation(Op, Vector, ^NewS1, ^NewS2)`, what the compiler makes of `binary_string_operation` with `Vector = {Pos1, Str1, Len, Pos2, Str2}` (`compiler/blt.kl1` `specialPredicate`): operation Op (0..15, the manual's table) on Len elements; NewS1 is a copy of Str1 with them replaced, NewS2 is Str2. An element of the vector that is not yet a value is waited for, as an operand is (the manual says the built-in waits; `builtin_utility:append_string/2` needs it): the goal of the stub waits on the first such element in order, and tries again when woken (checked, `lockstep_elw.py`: `scsi_fep_module:send_last_packet/9`, `append_string/2`, and the elements bound out of order at the stub). Refused: the vectors of four and three (shifting, unary), the exceptions | checked for operation 3, the IPL's (`lockstep_load.py`); the other 15 are NOT run |
| `change_element_size` | `22:DA x y z` | to 8, 16 or 32 bits: "the smallest index element occupies the highest order bits", widening pads with zeros (manual). The same words under another descriptor; 32-bit strings are type 5, no padding (`kbnheap.kl1` `string_cdesc`) | checked for 16 to 32 (`lockstep_load.py`); narrowing and a padded result are NOT run |
| `string_element` (guard), `exclusive_or` (guard), `b_exclusive_or` | `23:EF x y z`, `23:EC x y z`, `22:C9 x y z` | element, or the guard fails outside the string; exclusive or | checked (`lockstep_load.py`): the IPL's checksum over a real file comes to 0, and to an error with one word altered |

| `write_integer` | `23:21`, integer in the low 24 bits | store the integer at the structure pointer and advance it. Whether bit 23 is a sign is not established (no such operand in the image): both models refuse it | checked for 35 (`lockstep_modc.py`) |
| `write_marked_variable` | `23:26 x` | as `write_variable`; the variable is referenced more than once, so `r[x]` gets `REFx` | the write and the register are checked (`lockstep_modc.py`) |
| `b_multiply` | `22:C2 x y z` | `r[z]` := `r[x]` * `r[y]`; a non-integer or an overflow is the built-in's exception (manual, `multiply`), not modelled: both models stop. On the Bluespec a 32-step shift-and-add multiplier in `PimmMBox.bsv`; the count is ours | checked for N * 2, N at most 15 (`lockstep_modc.py`); large or negative operands and the overflow are NOT run |
| `put_atom` | `23:40`+r, atom in the low 24 bits | `r` := the atom; the register is the opcode's low five bits, as for `get_atom` | checked for register 0 only (`lockstep_gca.py`): a wrong register field is NOT caught |
| `write_value` | `23:25 x` | store `r[x]` at the structure pointer and advance it | checked |
| `write_variable` | `23:24 x` | the element at the structure pointer becomes a new unbound variable, `r[x]` a reference to it; advance | checked with `x` = 31 only (`analyze_standard_format/5`): the cell and the register are in the trace, nothing reads the register. That the variable is the element itself is our choice |
| `switch_on_non_list` | `23:2A x`, label | guard: `r[x]` a list, the structure pointer is set to its car; otherwise go to the label (an unbound `r[x]` is noted first) | checked (`shoen:ground_term/2`). |
| `switch_on_non_vector` | `23:2B x y`, then a cell holding the label | a vector: `r[y]` := its number of elements (the compiler's `index.kl1` calls the register `Ari` and switches on it), the structure pointer at its first; otherwise go to the label (an unbound `r[x]` is noted first) | checked (`shoen:ground_term/2`) |
| `vector` | `23:E4 x y` | guard `vector(X, ^Size)`: `r[y]` := the number of elements | checked |
| `vector_element` | `23:EE x y z` | guard `vector_element(V, I, ^E)`: `r[z]` := element `r[y]`, a reference if it is an unbound variable; fails outside 0..size-1 | checked, except the index equal to the size |
| `mark_element` | `23:1C x y` | the MRB of element `r[y]` of the vector `r[x]` is set, in the vector (PDSS `KL1B_MARK_ELEMENT`); both registers are dereferenced; a cell that is itself an unbound variable is left | checked (`lockstep_ptab.py`: the cell write) |
| `new_vector` | `22:D3 x y` | body `new_vector(Size, ^V)`: `r[y]` := a vector of `r[x]` cells of integer 0 (PIMOS manual) | checked for 1..6 |
| `set_vector_element` | `22:D0 x y z`, then `w4 w5` | body `set_vector_element(V, I, New, ^Old, ^V1)`: `r[w5]` := `r[x]` with element `r[y]` replaced by `r[z]`, `r[w4]` := the old element. Does not wait for `New` (manual: suspends on Vector or Position only). In place, `r[w5]` being `r[x]`, when the vector is reached with every MRB off; otherwise a copy (see "The MRB") | checked on vectors made by `new_vector`; both ways, by address and content, in `lockstep_mrb.py` |
| `put_nil` | `23:32 x` | `r[x]` := nil, the atom 0 (`library/kbn/kbnatom.kl1`: "The atom number of '[]' is fixed to zero") | checked |
| `wait_vector_N` | `23:A8+N x` | guard: `r[x]` is a vector of N cells; the structure pointer is set to its first | checked for N = 2, 3, 5 (`exception_table:replace_argument/3`), including the wrong size and an unbound `r[x]`; for 1, 4, 6 see the row `wait_vector_1`, `_4`, `_6` above |
| `read_variable` | `23:B4 x` | `r[x]` := the element at the structure pointer; advance. An element that is an unbound variable is taken as a reference to it | checked |
| `put_reused_structure` | `23:2F x y n` | `r[x]` := a structure of n cells to fill with `write_*`, under the tag of the structure in `r[y]` | checked for vectors of 2, 3, 5; a vector of seven or more gets a descriptor of its own (checked, `lockstep_reuse.py`: `scsi_fep_file:request_device_io/6` rebuilding `{201, ...}`, the image's one such site; fewer than seven cells under a long vector's tag is refused by both models, NOT run). The machine reuses `r[y]`'s cells when nothing else refers to them (MRB); the models keep no reference counts and always take new cells, which is what the machine does for a shared structure |
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
| `put_marked_value` | `23:36 x y` | `r[y]`'s MRB is set, then `r[x]` := `r[y]` (TR-248: "for reference duplication"; PDSS marks the source first) | checked: both register writes are traced |
| `put_variable` | `23:33 x y` | `r[x]` and `r[y]` := one fresh unbound variable | checked |
| `set_value` | `23:14 x y` | argument `x` (from 1) of the goal being built := `r[y]` | checked |
| `set_variable` | `23:13 x y` | argument `x` of the goal being built and `r[y]` := one fresh variable | inferred from `ipl:boot/0`; not yet executed |
| `enqueue_goal` | `23:63 x c16` | make a goal of the predicate at the label with the `x` built arguments and put it on the ready queue | checked. That the newest goal runs first is the model's choice, not established |
| `execute` | `23:61 x c16` | continue as a reduction of the predicate at the label, arguments already in `r[0..x)` | checked |
| `new_string` | `22:D4 x y z` | `r[z]` := a new string of `r[x]` elements of `r[y]` bits: 8, 16 or 32 (the manual allows 1 to 32; others are refused) | checked (`lockstep_s32.py` for 32) |
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
the long form (7 or more) is made, read and updated by the same
built-ins since `lockstep_deca.py`. Its layout has that one source
(the image holds no long vector); why the length is there twice is not
known, and both models read the first and write both. The guard `vector` on a long vector is checked by `lockstep_gca.py`
(every module's information vector has 8 elements);
`switch_on_non_vector` on one is written but NOT run; unifying two long vectors is not modelled.

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
    C cell         display_console is given this value
    S cell         ... and, for a string, each of its cells: the
                   descriptor, then the words
    B init         scsi_init asks the SCSI device its buffer size
    B u l cdb d n [bytes]
                   a SCSI command is given to the device (each try:
                   a command that waits is given again by each poll):
                   unit u, LUN l, the CDB's bytes in hex, direction d
                   (0 none, 1 out, 2 in), length n, and for a SEND
                   (d = 1, n > 0) the n bytes sent, in hex

Every register and memory write is traced, whoever makes it: an
instruction, the scheduler taking a goal, a wake-up, or the bench
making a variable or a goal. In the Bluespec the `M` line is printed
where the write reaches the RAM, not where it is requested. The
Bluespec core can also end with `E unimp` (an instruction or case it
does not implement) or `E error`; the reference model raises an
exception there, so neither can appear in a matching trace. The trace
has no cycle numbers: the two models agree on what happens and in what
order, not on when.

The SCSI device is not in either model's trace: on the reference it is
`ref/pimm/fep.py`, and on the bench the answers it gave, recorded while
the reference played the same script (`Machine.scsi_tape`) and written
after the script as a tape (`ref/pimm/driver.py` "The device tape":
the buffer size, "not ready", or Result and the bytes received). The
Bluespec bench prints each `B` line from what the core put on its port,
the reference from what it gave its device, so the bus is compared and
only the answers are replayed. "Not ready" is the device's answer at a
try, so a command waits at the same point on both; the dry-machine
poll is the script's `POLL`, placed where the reference ran dry with a
command waiting.

## The MRB

The low tag bit of a reference or pointer (tags 04h to 1Fh; `REFo` 06,
`REFx` 07) is kept as the multiple reference bit by both models, since
2026-11-23. One thing is done on its strength: `set_vector_element`
updates in place when the vector is reached with every MRB off
(PDSS `blt_basic.c`: `if (Mrbof(vect) == MRBOFF)`), and copies
otherwise, the copy's elements marked. Nothing is reclaimed
(`collect_*` do nothing; strings and `put_reused_structure` still
copy). The rules are PDSS's
(`emulator/deref.c`, `emulate.c`, `blt_basic.c`, V2.52), the sibling
whose code we hold; PIM/m's own are described in `M92` pp. 429-430 and
TR-248 (`literature_gaps.md` section 3) and agree where they speak.

- **Dereference.** If any reference on the way has its MRB on, the
  result has (`deref.c`: `SetAll(reg, ..., MRBON)`). Otherwise the
  value is taken as its cell holds it.
- **Marked instructions.** `put_marked_value`, `set_marked_value`,
  `write_marked_value` set the MRB of the source register, then copy;
  `write_marked_variable` gives `REFx`.
- **Elements.** What is taken from a cell that goes on holding it has
  its MRB on: the guard and body `vector_element`, the merger's copy of
  a message, a packed goal's arguments, the copy `set_vector_element`
  makes. The body `vector_element` and `mark_element` also set it in
  the cell. `read_variable` after `wait_vector_N` takes the element as
  it is when the vector word's MRB is off (PDSS `read_element`: "if
  (Mrbof(ptr) == MRBON) SetMrbof(car, MRBON)").
- **Off:** the result of `new_vector`, the copy `set_vector_element`
  makes (in place the vector's word is given back as it was, which
  is off), and a new variable's two references.
- **On:** every other structure pointer, as before (`put_vector_N`,
  `put_list`, constants in a module), and whatever the test driver
  passes from a slot, which it keeps.

Ours, not the sources': integers and atoms are never marked (PDSS
marks them; nothing reads the bit); the guard `vector_element` marks
its result whatever the vector's MRB (PDSS only when it is on); list
cells are always treated as multiply referenced; the copy in
`set_vector_element` marks the new vector's elements but does not go
back and mark the old one's (PDSS does; the old vector is only reached
by marked pointers); an element cell that is itself an unbound
variable is taken as `REFx`, and is never overwritten in place: such
a vector is copied (the cell is the variable; PDSS, whose variables
are cells too, does the same by another route, not followed here).
A marked vector is copied whole, where the Multi-PSI had a
mutable-array scheme. All of these err towards "on", which
costs copies and never correctness.

What the in-place update rests on: that every way a second reference
to a vector can arise sets a bit. `lockstep_mrb.py` checks five ways
by address and content, and the module objects the loader builds are
checked cell by cell against their files (`lockstep_newm.py`,
`lockstep_load.py`); paths the scripts do not run are not checked.

Checked (when the MRB went in; the suite had 23 tests then and has 39
on 2026-11-23, `bsv/run_pimm_lockstep.sh`, all on both models): the 23 lockstep tests agree line for line, and for 22 of them
the reference model's trace before the change equals the trace after
it once the lines the marking adds are dropped and the bit masked
(`jtoa`, whose count did not move, was not compared). Twelve
injections into the Bluespec FAILed (dereference forgetting a marked
link, at the first or a later link; each half of a marked instruction;
`write_marked_variable`; `read_variable` never marking; `wait_vector`
always single; the vector box's elements; `mark_element`'s write;
`new_vector` and the copy coming back marked; the driver's slots).
**Not caught**: `read_variable` marking although the vector is single
(no test reads a vector whose word is unmarked: `put_vector_N` marks),
and the merger taking a message unmarked (every message so far is
already marked or an unbound cell).

## Runtime state

How the PIM/m firmware kept goals, the ready queue and suspended goals
is lost with it. What follows is **this project's design**, shaped
after PDSS (`emulator/record.h`, `goal.c`) and fixed in
`asm/pimm_layout.py`, which both models read. It will grow (priorities,
MRB) and is not a claim about the machine.

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
  or 0}`, `{INT, shoen << 2 | status}` (0 ready, 1 suspended, 2 taken;
  the shoen is the goal's shoen record as an address relative to the
  load address, 0 for the root, so a goal outside every shoen has the
  plain status: "Shoen" below), `{INT, code address}`, `{INT, n}`,
  then the n arguments. Addresses in cells are absolute.
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

### Shoen (stage 1: create, start, terminate)

Three tiers, kept apart:

- **PIM/m-sourced** (the IPL image, PIMOS's compiler, assembler, macros
  and manual): the encodings and operand directions of `create_shoen`
  and `start_shoen` (rows above); the handle's tag, 38h `SHREC`
  (`debugger/inspector/tagtbl.kl1`); the report stream's integer
  codes, 8 `started` and 12 `terminated`, which the image's
  `shoen:report/2` (cell 15818) translates (`macro/pimos/pimos/
  pimos.vmac`:177-199 agrees); that a shoen is dormant until `start`
  and that `terminated` reports its end (manual, `e-shoen.tex`:
  117-262); the protocol of `shoen:execute/4`, `control/2`, `report/2`.
- **Carried over from the siblings, not PIM/m-sourced**: counting a
  shoen's goals and its child shoen and ending it at zero (PDSS
  `emulator/emulate.c`:340, `shoen.c`:123-178 and 280-309); the first
  goal being an `apply` (PDSS `dc_apply`) and being parked until the
  shoen is started (PDSS `goal.c`:310-334); `started` reported before
  the state changes and `terminated` alone while the control stream
  is open (VPIM `functions/f_shoen_control.psl.c`:324-330,
  `f_shoen_with_fp.psl.c`:86). VPIM's own message numbers are not
  used.
- **Ours**: everything below about records and cells.

The design:

- **Shoen record**, 5 cells in the heap (`asm/pimm_layout.py`):
  `{INT, count}` the shoen's live goals plus its live child shoen;
  `{INT, status}` 0 dormant, 1 started, 2 terminated; `{INT, the
  parent's record, or 0}` (the root has no record); a reference to
  the report stream's unbound tail; `{INT, the goal record of the
  first goal}`. The handle is `{SHREC, the record's address}`.
- **A goal's shoen** is in its record's status cell (above). The
  machine has a register, the current shoen: that of the goal last
  taken from the ready queue, and the root's (0) once the queue is
  empty, so what a bench makes between runs is the root's. A goal
  record written during a reduction (a new goal, a suspension, a
  waiting built-in, the goal of a unification or of a merger input)
  belongs to the current shoen. Waking keeps a goal's shoen.
- **Counting.** Every goal record written while a shoen is current
  adds one to its count, after the record's last cell; the end of
  every reduction of a goal of that shoen (`proceed` or a suspension,
  not `execute`) takes one off. So a suspension nets nothing and a
  `proceed` is one less. The root is not counted: no memory traffic,
  and every trace made before the shoen existed is unchanged.
- **`create_shoen`**: Code and Argv go to argument registers 1 and 2
  as they are; then the record (count 1, dormant, parent = the
  current shoen), a fresh Report variable, the first goal (code:
  `apply`'s stub of `asm/pimm_stubs.py`; suspended, on no queue and
  on no variable; it belongs to the new shoen and is the 1 of its
  count), and one more on the parent's count unless that is the root.
- **`start_shoen`**: 8 on the report stream, status started, then the
  first goal becomes ready and goes on the queue as a woken goal does
  (a `W` line).
- **Termination.** When a count reaches 0: status terminated, 12 on
  the report stream, then one off the parent's count, and so on up.
- **A message on the report stream**: two new cells `{INT, code}`
  `{UNDF}`; the record's tail, followed through references, is bound
  to the list cell with the ordinary wake of the goals waiting on it;
  the record's tail becomes the new cell. A tail someone has bound to
  a value is refused.
- **No resource model: 6 (`resource_low`) is never reported.** Ours,
  and probably not the machine's: VPIM reports it for a shoen with no
  limit left, and every caller of `execute/4` in the image grants
  resource only when it is told `resource_low`.
- **Refused, loudly** (the reference model raises `Unimplemented`,
  the Bluespec ends `E unimp`): `stop_shoen`, `abort_shoen`,
  `remove_shoen`, `shoen_statistics`, `add_shoen_resource`,
  `allow_shoen_resource_report`, `shoen_profile`,
  `create_profiling_shoen`, `raise`, and a goal that FAILS inside a
  shoen (that is the exception path).
- **What follows for the image's own `execute/4`** (observed,
  `lockstep_shoen.py`): its `control/2` and `report/2` belong to the
  shoen that called it, and end only through `remove_shoen` and the
  closing of the report stream. So a shoen whose code is `execute/4`
  does not terminate in stage 1 even after the shoen it made has, and
  the step "a child's end brings its parent to 0" is never run.

Things this predicate shows about the compiler, useful for reading the
rest: range guards compile to `put_integer` and a comparison per bound;
33 constant clauses compile to one `hash_on_constant`, placed after the
`switch_on_non_integer` and before the range clauses even though the
source has the ranges first (the clauses are mutually exclusive, so the
order does not show).
