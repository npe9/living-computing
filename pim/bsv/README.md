# PIM/m Bluespec sources

The model is `PimTypes`, `PimStages`, `PimALU`, `PimE`, `PimPU`; see
`../plan.md` and `../docs/pim_architecture.md`. The assembler and the
model ISA table are `../asm/pimasm.py` and `../docs/isa.md`.

The KL1-B execution path is `PimKL1B.bsv` (40-bit tagged word, 8-bit
register file, flat heap with `HP`, `step()` clock enable), separate
from the diagnostic ISA. Its testbenches are `PimKL1BTb.bsv` (REF-chain
deref through `read_variable`), `PimKL1BFailTb.bsv`,
`PimKL1BConstFailTb.bsv`, `PimKL1BStructTb.bsv` (`put_list`,
`put_constant`, `write_constant`), `PimKL1BIntTb.bsv`
(`put_integer`, `write_integer`), `PimKL1BWaitTb.bsv`
(`wait_list`, `wait_integer`), `PimKL1BSetTb.bsv` (`set_constant`,
`set_integer`, `set_nil`, `set_list` and the matching reads),
`PimKL1BArithTb.bsv` (the guard built-ins), `PimKL1BGetTb.bsv` (the
active-unification reads), `PimKL1BControlTb.bsv` (the goal queue's
FIFO order), `PimKL1BSuspendTb.bsv` (suspend's empty-queue jump),
`PimKL1BMiscTb.bsv` (put_variable/get_value), `PimKL1BSetAtomTb.bsv`
(set_atom operand c is the atom ID), `PimKL1BJumpTb.bsv` (the unconditional jump),
`PimKL1BNilTb.bsv` (put_nil/write_nil), `PimKL1BArgSlotTb.bsv`
(the 8-bit argument-slot width; a 3-bit truncation aliases slot 8 onto
slot 0), `PimKL1BSwitchTb.bsv` (the `switch_on_non_integer`,
`switch_on_non_atom` and `switch_on_non_list` type dispatch, each
injection failing only this bench), `PimKL1BSwitchVecTb.bsv`
(`switch_on_non_vector` jumps on a non-vector and halts on a vector,
whose arity the model cannot supply), `PimKL1BSwitchConstTb.bsv`
(`switch_on_constant` reaches each key's label and the else label, and
halts on an unbound value), `PimKL1BNoopTb.bsv` (the three
stand-in opcodes advance PC when the argument is bound),
`PimKL1BWaitUnboundTb.bsv` (wait halts on an unbound UREF; the
sentinel instruction never executes), `PimKL1BPutAtomTb.bsv`
(put_atom and the 0x41-0x5f quick forms write the atom ID to a
register), `PimKL1BCpTb.bsv` (the choice point stack),
`PimKL1BOtherwiseTb.bsv` (otherwise commits the choice point and jumps
to the label), `PimKL1BGuardBacktrackTb.bsv` (guard failure backtracks
to the else label), `PimKL1BBindTb.bsv` (get_constant binds a UREF in
the heap); `run_kl1b_tb.sh` builds and runs all twenty-six. The
implemented subset and the loud-failure rule for the rest are in the
module header.

Build hazard: never compile-check the model with
`bsc -g mkPimKL1B PimKL1B.bsv`. That writes a `PimKL1B.bo` recording
`mkPimKL1B` as a synthesis boundary, where each method has one port,
and every bench that calls `readReg`/`readArg` more than once in a rule
then fails with G0002 ("needs more than 1 ports") although nothing is
wrong with it. Compile through a bench. If it has happened, delete
`PimKL1B.bo` and `mkPimKL1B.{ba,cxx,h,o}` and rebuild.

The network model is `PimNU.bsv` (one NU's per-port FIFOs),
`PimLink.bsv` (one output port to one input port), `PimNURouted.bsv`
(the routed 5 × 5 crossbar with the route table and CPU-port arrival)
and `PimMesh.bsv` (a parameterized `w × h` mesh with deterministic XY
route tables). Their testbenches are `PimNUTb.bsv`, `PimLinkTb.bsv`,
`PimNURoutedTb.bsv` and `PimMeshTb.bsv`.

## The real-binary core (`Pimm*.bsv`)

A second core, built beside the bench model `PimKL1B.bsv`, that
executes the PIMOS binaries' own cells: 40-bit words with the machine's
tags, its opcodes and its relative labels, from the IPL image
`pimm_ipl.kbn`. It follows `../ref/pimm/pimm.py` instruction for
instruction and is tested by trace comparison with it.

| File | What |
|---|---|
| `PimmTypes.bsv` | cells, addresses, labels, how a reduction ends, the trace |
| `PimmMem.bsv` | the memory behind request/response: a RAM of 2^15 cells loaded with the IPL image and the stubs, and the heap's RAM (2^27 cells in all, `asm/pimm_layout.py`), not loaded; traces every write |
| `PimmRegs.bsv` | the register file and the argument registers; traces every write |
| `PimmDBox.bsv` | data box: multi-cycle dereference and unification |
| `PimmHBox.bsv` | hash box: the `hash_on_constant` table walk |
| `PimmGBox.bsv` | goal box: heap pointer, ready queue, goal records, hooks, wake-up, taking the next goal, the goal of a built-in that must wait |
| `PimmSBox.bsv` | string box: length and size, element, new string, set element; elements of 1, 8, 16 or 32 bits (1 since 2026-11-25, `lockstep_s1.py`); the order of two strings for `string_less_than` and `string_not_less_than` (R7L, `lockstep_sord.py`) |
| `PimmPBox.bsv` | passive-unification box: `wait_value` on two structures, VPIM's general passive unification with an explicit stack of 512 frames (a register file), on its own memory port (`port[10]`, `MemClients` 11) and the data box for each dereference; answers equal, not equal, wait (the variable to note) or refused (2026-11-25, `lockstep_pstruct.py`) |
| `PimmGcBox.bsv` | garbage-collection box (R7G, 2026-11-25, INFERENCE/OURS): `ref/pimm/pimm_gc.py`'s copying collector step for step, one StmtFSM per routine (block, data, word, module, code, goal, goals, shoen) and the main one: the roots (the goal box's queues, the timer box's alarm variable, the SCSI box's waiting commands, the current shoen), the scan, the links, the FNV-1 checksum and the `K gc` line; `collect_garbage` asks (exec stage), `PimmCore` `pick_or_fire` collects before the alarm; its own memory port (`port[11]`, `MemClients` 12), writes untraced (`MemPort.quiet`) |
| `PimmShBox.bsv` | shoen box (stages 1 to 3): the shoen record, the report stream, start, the count and the reductions at the end of a reduction, termination, statistics, remove (and a remove pending until termination); the exception message (the mask walk, the handler's `apply` goal, Info), stop, abort, and the check of each goal taken inside a shoen (run, park, discard); (R7L) the resource: left at create 0, taken at the end of each run from the shoen and those above it, a goal parked when none is left with `resource_low` once until allowed, `add_shoen_resource` releasing them, `allow_shoen_resource_report`, `return_resource` of what is left |
| `PimmTBox.bsv` | timer box (R7L): the processor's one alarm, `set_timer` to a time still to come; checked at each goal switch by the core's `pick_or_fire`, fired with the time, the waiting goals woken (`lockstep_timer.py`) |
| `PimmScsiBox.bsv` | SCSI box: `scsi_init` and `scsi_command` (OURS, as the reference model's: the firmware is lost), the device OUTSIDE the core on its port `scsiReq`/`scsiResp`; the commands that wait for the device, and the poll (`scsiPoll`) when the machine has run dry |
| `PimmStages.bsv` | fetch stage; execute stage (clause selection, the variables guards met unbound) |
| `PimmCore.bsv` | the modules above and the rules that move an instruction between them |
| `PimmDriverTb.bsv` | lockstep driver bench: executes a test's script of operations on the core (`../ref/pimm/driver.py`), and answers the core's SCSI port from the script's device tape, printing a `B` line per command from what the core sent |
| `generated/PimmGen.bsv`, `generated/pimm_ipl.hex` | tags, opcodes, predicate addresses, record layouts, and the image followed by the built-in stubs, written by `../asm/gen_pimm_bsv.py`; no tag or opcode is typed by hand |

`run_pimm_lockstep.sh` builds into `build_pimm/`, and for each test
(`../ref/pimm/lockstep_*.py`) writes its script, runs the driver on it
and pipes the trace into the test (with arguments, only the tests named). Forty-five tests (`scsi` in seven scripts, `scsi` and `scsi@1`..`scsi@6`: fifty runs): `jtoa` (`convert_element/2`, every
key, suspension scenarios), `conv` (`convert/2`, the whole
`jis_to_ascii` module, on strings), `get4`
(`scsi_common:get_4_bytes/4`) and `ccode`
(`scsi_common:check_completion_code/4`, which builds vectors and
atoms) `asf` (`scsi_common:analyze_standard_format/5`, which calls
`get_4_bytes/4`) and `repl` (`exception_table:replace_argument/3`,
which reads vectors) and `ground` (`shoen:ground_term/2` on lists and
vectors; `PimmVBox.bsv` is the vector box) and `rpos`
(`exception_table:replace_position/3`, with `switch_on_constant`,
which the hash box walks) and `dec0` (`ipl_file_decoder:decode_0/7`,
the IPL's file decoder, on one-word integers; `b_shift_right`) and `rss`
(`scsi_common:analyze_request_sense_command_status1/6`: the guards
`integer` and `shift_right`, `put_vector_5`) and `dect` (the IPL file
decoder on integers, lists and vectors, the test answering the
decoder's read requests through the script's `SLOT` operation;
`put_list`, `get_nil`, `wait_atom`) and `deca` (the same on atoms and
proper lists, with terms from the real `pimm_kernel360E.sav`; the test
also plays the atom table; `put_constant`; strings, with the guard
`modulo` on the divide box `PimmMBox.bsv`, a 32-step restoring
divider; vectors of 7 or more elements, the descriptor form, in
`PimmVBox.bsv`) and `gca` (`decode_module_info/6` on the module
information and whole GC areas of seven real modules; `put_atom`,
`write_nil`) and `modc` (`decode_index_table/9` and
`decode_code_area/8` on real modules, shoen's 1259 code items among
them; `b_multiply` on the multiplier in `PimmMBox.bsv`,
`write_marked_variable`, `write_integer`) and `lmod` (`load_module/7`
on four whole real modules; the general `put_vector`) and `ext` (a
call into another module: `execute_external` through the called
module's predicate entry table, in the hash box; `wait_value`,
`wait_constant`) and `ptab` (the IPL builds real modules' predicate
entry tables, `ipl_module:set_pred_table/6`, checked by the layout the
image's own tables have; fourteen instructions, among them
`tag_and_value`, `new_instruction`, `b_vector_element`,
`put_structured_constant`) and `pack` (a goal of 12 arguments: the
compiler packs those from the 11th on into a vector, `enqueue_goal`
spreads it) and `newm` (`ipl_module:load/4` builds five real modules
as module objects, `new_module`; every cell checked against the file
and the layout of the image's own modules) and `melem`
(`module_element` on three image modules, against `asm/kbndis.py`'s
table, and on a `new_module`'s; rules `modElem1`, `modElem2`) and `file`, `file3` (`ipl_file_decoder:decode/8` on two
whole real object files, one and three modules, from the magic number
to the atom table; `set_atom`, `calculate_priority_from_minimum`,
`enqueue_goal_with_priority` with the priority dropped) and `pool` (the built-in merger, under
`ipl_pool:keyed_set/2`, against a dictionary; the merger is a waiting
goal here, `PimmNBox.bsv`, not the machine's merger cell) and `merge`
(the same pool's merger with two and three inputs bound in one step:
they reach the pool in the order they were bound, as VPIM, KLIC and
PDSS pass them on at the unification; a woken `merge_in` goes on the
goal box's merger's list, `PimmGBox.bsv`, taken before the ready
queue, 2026-11-24) and `load` (`ipl_loader:load_file/9`
loads a real object file with the IPL's own buffer reader, checksum
and atom-number pool; a file with its checksum altered is refused;
`string_operation`, `change_element_size`, 32-bit strings) and `mrb`
(`set_vector_element` on a vector held twice, held once, behind a
marked and a plain reference, and over an unbound element: in place
or copied, by address and content) and `atab` (the IPL's own atom
table, `ipl_loader:atom_table/1`: names interned, read back with
`get_all`, and a real object file loaded against it; `new_atom`,
`hash`, string equality in `wait_value`, the guard
`floating_point_not_less_than`) and `cons` (the console:
`display_console`, by which the IPL's decoder shows the comment of a
real 5702h object file and a file's name; `C` and `S` trace lines) and `run` (rung R2: `hasher:hash/3`, loaded
from its object file by the IPL's own loader and atom table, is RUN
from the module object in the heap, and answers as its KL1 source
says) and `link` (`ipl_loader:load/4` whole: the IPL's file loop,
loader, atom table and linker, with the bench answering `open` and
the buffers; the console is given "IPL loading", the file's name and
"Link Modules ...", and the linker names the file's undefined
module). The bench fills a string it has made in place (`SETW`),
not through `set_string_element`. `unif`: two vectors or two lists
are unified by a goal of their own (PDSS's way; the stub
`unify_step`), nine cases with their bindings and two failures.
`s32`: `new_string` with 32-bit elements. `s1`: strings of 1-bit
elements (the string box's type 0) and the unary `string_operation`
(a vector of three), a change to 1 bit refused. `ipll`: the IPL's
`ipl_files/4` reads the held `pimos.ipl` and gives its twenty names. `p2c`: `predicate_to_code` on every predicate
of the image and the guard `code`. `apply`: `apply(Code, Args)`, with
`top:go_pimos1/2`'s own. `shoen`: the shoen in its first stage,
`create_shoen`, `start_shoen` and termination, driven through the
image's own `shoen:execute/4` (its `control/2` and `report/2` are the
consumers): a goal run in a shoen with `started`, `terminated`
reported; a shoen not started; one whose goal waits; a shoen inside a
shoen; the records' counts read from memory (`PimmShBox.bsv`;
`../docs/pimm_semantics.md` "Shoen" says what is PIM/m-sourced, what
is carried over from PDSS and VPIM, and what is ours). `shoen2`: the
shoen's second stage, `shoen_statistics` and `remove_shoen`, driven
through the image's own monitors (`ipl:ipl_monitor/3`,
`top:bios_monitor/3`, `top:top_level_monitor/4`) on `execute/4`'s
report: `started`, `terminated`, `statistics_started`,
`statistics(H, L)` (H, L checked against twice the reductions counted
on the trace), `return_resource(0, 0)`, the stream closed, `Shut =
shut`; a nested shoen whose parent now terminates; a remove before
the end; statistics of a running shoen. `shoen3`: the third stage,
through the image's own code: a reduction failure inside a shoen
(`ipl:close_fep/2` on an atom) and `shoen:raise/3`, each reported as
`exception(Kind, Info, NewCode, NewArgv)` via
`exception_table:translate/4` and answered by a monitor's `dummy/2`;
a mask of `reduction_failure` alone (`execute/7`), and `raise/3`'s Tag 3 under mask 1 (the manual's rule, not VPIM's); the raise of
`control/2` on an illegal control message; `stop` with a woken goal
parked and released by `start`; `abort` of an inner shoen by its
control stream and of an outer one by `top_level_monitor/4`, the
woken goals discarded. `alt`: `read_eagerly` (what the compiler
writes for `alternatively`), the guard `not_equal` and
`wait_vector_1`, `_4`, `_6`, on `scsi_fep_util`,
`scsi_fep_file:reply_with_attention/4`, `scsi:request_manager/3` and
`scsi:command_executer/2` (`wait_vector_1`, which the image does not
use, on code the bench writes). `body`: `b_divide` and `b_modulo`
(`scsi_fep_module:str8_to_msg/3` and `str16_to_str8/2`, and signed
operands at the stubs), `b_string` at its stub,
`enqueue_goal_to_processor` (`scsi_fep_module:create/7`; processor 0
only). `elw`: `string_operation` waits on an element of its vector
that is not yet a value (`scsi_fep_module:send_last_packet/9`, with
`b_string`'s real sites, and `builtin_utility:append_string/2`).
`reuse`: `put_reused_structure` of a vector of seven
(`scsi_fep_file:request_device_io/6`). `prio`: `current_node` (one
node: 0 of 1) on code the bench writes, and
`calculate_priority_from_current` at its stub and at the image's
`shoen:execute/7` (PDSS's formula, the range and the current priority
ours). `atom`: `top:go1/4`'s atom-number server, with
`supply_atom_number` (what it does is not sourced: its inputs dropped,
its output never bound, ours; the bench binds it) and a merger input
bound to a vector (`throw_atom_number_client/4`'s `{E, F}`; the merger
box's `spread`, the goals made through the argument registers).
`xmod`: an external call between two modules the IPL loaded
(`pimm_patch_mkdir360E.sav` through `ipl_loader:load/4`, the bench
binding the module variable as the linker would; the hash box's
dereference of the module field), about 7.4 M trace lines.
`gmul`: the guard `multiply` (the multiply box) and the register
spill `save`/`restore` (work slots in `PimmRegs.bsv`, ours), at the
four multiply sites of `scsi_fep` in `pimm_patch_scsifep360E.sav`
loaded through `ipl_loader:load/4`, about 2.1 M trace lines.
`rdvc`: the guard `diff`, at `file_request_device:driver_0/10` of
`pimm_patch_mkdir360E.sav` (loaded as for `xmod`), about 7.4 M trace
lines. `pvec`: `wait_value` on two vectors (rules `pv1`..`pv4`, since
2026-11-25 rule `pv1` and the box `PimmPBox.bsv`), the
IPL's pool `ipl_pool:keyed_set/2` given vector keys. `pstruct`:
`wait_value` on nested structures, VPIM's general passive unification
(`PimmPBox.bsv`), an OURS goal in heap cells: lists, long vectors,
strings, codes and modules as elements, goals waiting on an element of
X or Y, the 512-frame stack and its 513th push refused. `tproc`:
`Goal@processor(P)` with P unbound waits (rules `tq1`..`tq4`, the
stub `to_processor`, rules `tp0`..`tpE`; from VPIM), at the one site
of `pimm_patch_scsifep360E.sav`. `timer`: `system_timer` and
`set_timer`, the model's clock at 0 (ours). `wint`: `write_integer`
with a negative operand, at `scsi_fep:check_data_size1/6`.
`scsi`: `scsi_init` and `scsi_command` (`PimmScsiBox.bsv`) at their
sites (`scsi:create/2`, `scsi:command_executer/2`), the device on the
tape the reference model recorded: TEST UNIT READY, SEND, RECEIVE, a
reply cut in two, a command that waits finished inside a SEND and one
at a poll, an element waited for; then `ref_scsi.py`'s six IPL parts,
the IPL reading its list and its files through its own SCSI stack; the
bus bytes compared as `B` lines. Eleven fault injections into
`PimmScsiBox.bsv` and the exec stage's hook, each run against all seven
(2026-11-24, observed failure sets in `lockstep_scsi.py`'s header):
eight fail all seven; the two poll injections (a command not ready at a
poll dropped, or taken as ready) fail only `scsi`, the IPL never having
a command not ready at a poll; the copy's pad bytes from old memory
fail none (every string has zero pad).

`run_pimm_longrun.sh` is the long run, outside the suite (about two
hours; run whole on both models 2026-11-24, under the merger rule:
448,194,526 trace lines identical, every check passing, 7,435 s to the
compare on a shared machine; 447,739,516 on 2026-11-23, before the
merger timing change, which moved the count): the IPL's `load/4` on the whole held `pimos.ipl`,
twenty files, compared line by line with the reference model, the
answer checked to be `normal` with the code of `pim:go/4`
(`ref/pimm/longrun_ipl.py`).

State: 169
instructions (a recount, 2026-11-24: 168 handlers in `pimm.py`, all on
both models; 165 without our three stubs; 169 with `module_element`,
2026-11-25; the earlier 128 and 130 were
increments; the eleven since 157 are those met between the login and
the shell's prompt, `ref/pimm/lockstep_login.py`); goals as
records in memory on a ready queue; a goal that cannot choose a clause
is written back, hooked on the variables it waits for, and woken when
one is bound; a body built-in with an unbound input becomes a goal of
its stub (layouts: `../asm/pimm_layout.py`, the project's design, see
`../docs/pimm_semantics.md`). Sequential (the next fetch waits for the
instruction before it), no timing claimed. The MRB is kept, and `set_vector_element`
updates in place on it (`PimmVBox.bsv`); nothing is reclaimed and strings are always copied
(`../docs/pimm_semantics.md` "The MRB"). The shoen: `create_shoen`, `start_shoen`, termination, `shoen_statistics` and `remove_shoen`
(a goal knows its shoen, a shoen counts its goals and children and its reductions, and reports `started`,
`terminated`, `statistics_started`, `statistics`, `return_resource` and its close),
the exception message for a reduction failure and `raise`, `stop_shoen`, `abort_shoen`,
`add_shoen_resource` and `allow_shoen_resource_report` (acknowledged, no resource counted);
its profile built-ins and a unification failure inside a shoen stop the model, `resource_low` is never reported.
Not modelled: priorities (garbage collection is in since R7G,
`PimmGcBox.bsv`, below: when `collect_garbage` asks and when the heap
reaches its limit; not MRB reclamation or the free pools), built-in
exceptions (they stop the model). The bench model and its benches are
untouched and still run.

### The lockstep from a saved machine (`run_pimm_shell.sh`)

`run_pimm_shell.sh PKL [--type LINE ...]` runs PIMOS on the core from
a machine the reference saved, compared line by line with the
reference model (`../ref/pimm/lockstep_shell.py`). It is outside the
suite because the saved machines are ~1.1 GB pickles, not in git, that
the IPL's link takes 15-50 minutes to make. How they are made:

    python3 ref/pimm/longrun_ipl.py --reference --save LINK.pkl
    python3 ref/pimm/longrun_ipl.py --load LINK.pkl --go --fep --save-prompt PROMPT.pkl

The second command takes about 85 s and saves the machine at the
shell's prompt: run dry after the login, the window's `getl` held by
`fep.py`, one RECEIVE waiting in the SCSI box. The core is given the
saved heap as a file (`PimmMem.bsv`: the heap RAM loads it on the
bench `mkPimmShellTb`, so nothing is traced). It is also given what of
the machine is not in memory, by the script's RESTORE operations
(`PimmCore.restore`): the heap pointer, `new_atom`'s counter, the clock
(ticks and the instructions since the last one), the SCSI box's command
count and its waiting commands. The run queue, the merger's lists and
the current shoen are empty between runs; `lockstep_shell.py` asserts
this. The reference runs with `Machine.ahead` off. After the RESTOREs
the script is `go()`'s loop as RUN and POLL; the device is the tape of
`fep.py`'s answers, and `Fep.idle()`, the scripted events, belongs to
the reference alone.

Measured 2026-11-24, every line identical (`PINNED` in
`lockstep_shell.py`), on a shared machine, with the login record's ID
0 (`fep.py` `LOGIN`, P-f3; the checkpoints made afresh under it). With
the ID 1 every count was 20 instructions higher, the link row 30 trace
lines longer (20,107,047), and the windows from the prompt the same
length:

| From | Typed | Instructions of `go()` | Trace lines | Ends |
|---|---|---|---|---|
| the prompt | `shutdown`, `yes` | 8,587,072 to 8,766,319 (179,247) | 878,180 | `PIMOS END********`, nothing left to run, 253 goals waiting |
| the prompt | `cat <= file("pimos:pimos.groups")` | 8,587,072 to 8,760,665 (173,593) | 731,110 | `Shell>> ` again, nothing left to run, 1,224 goals waiting |
| the link | `shutdown`, `yes` | 0 to 8,766,319 | 20,107,017 | `PIMOS END********`, nothing left to run, 253 goals waiting; 21 min in all, 897 s of it the Bluesim run and compare |

Re-measured 2026-11-25 with R7L's resource model (shoen records of 11
cells, the checkpoints made afresh; every line identical, the new
counts in `PINNED`):

| From | Typed | Instructions of `go()` | Trace lines | Ends |
|---|---|---|---|---|
| the prompt | `shutdown`, `yes` | 8,595,408 to 8,775,555 (180,147) | 912,901 | nothing left to run, 250 goals waiting |
| the prompt | `cat <= file("pimos:pimos.groups")` | 8,595,408 to 8,769,465 (174,057) | 778,956 | nothing left to run, 1,222 goals waiting |
| the link | `shutdown`, `yes` | 0 to 8,775,555 | 20,435,590 | as the prompt's row |

The last row is the first time PIMOS's start, the login and the shell
have run on the Bluespec core: everything `longrun_ipl.py --go --fep`
does after the link, 221 device answers on the tape, 5,859 splices of
the merger's list (300 onto a list that is not empty). No divergence was found, so nothing in the
core was changed. The splice-order injection into the goal box (the
merger's list) fails the first row at line 8,429
(`lockstep_merge.py`'s header; on the checkpoint made with the login ID
1).

Which RESTOREs the first row checks (2026-11-24, on the checkpoint made
with the login ID 1, before P-f3; the window is the same length): each RESTORE word of
its script replaced in turn by a silent SLOT, the same length, and the
run compared again.

| RESTORE dropped | Result |
|---|---|
| 0, the heap pointer | FAIL at line 4, instruction 0: `M 77959241` on the reference, `M 32768` on the core (the reset value) |
| 1, `new_atom`'s counter | PASS: not caught |
| 2, the clock's ticks | PASS: not caught |
| 3, the instructions since the last tick | PASS: not caught |
| 4, the SCSI command count | FAIL at line 6,231, instruction 718: `R 11 0000000080` on the reference, `R 11 0000000000` on the core |
| 31, the waiting RECEIVE's push | FAIL at line 1, instruction 0: `B 7 1 0820004000 2 16384` on the reference, `Q` on the core |

So the window from the prompt runs no `new_atom` and no instruction
that reads the clock (`system_timer` and the timer instructions write
the clock's bits to a register, which the trace shows: INFERENCE from
the PASS, not counted). RESTOREs 1-3 are
unchecked by this window; they are checked by the commands past the
shell (below, "Which RESTOREs the commands check"), and so are
RESTOREs 16-26, the waiting command's fields, each dropped alone
(2026-11-25, `pwd`, the table there).

### Commands past the shell (`run_pimm_apps.sh`)

`run_pimm_apps.sh PROMPT.pkl [NAME ...]` types each command line of
`APPS` in `../ref/pimm/lockstep_shell.py` at the prompt of the saved
machine, on the reference and on the core, and compares them line by
line, the counts against `PINNED` and the window's text against
`APPS`. The checkpoint is loaded once and its heap written once; each
command is played in a process of its own (`lockstep_shell.py apps`).
Outside the suite, like `run_pimm_shell.sh`. Ends with
`pimm lockstep apps: PASS` or the names that failed. What each prints
and how it stands against the primers and manuals:
`../docs/binary_reverse_engineering.md` 1.4, "Commands past the shell".

Measured 2026-11-25 (R7L) from a prompt checkpoint made with R7L's
resource model (login ID 0, 8,595,408 instructions), every line
identical; each row re-measured so, since the shoen record grew to
11 cells (a checkpoint made before 2026-11-25 has 8-cell records and
is not loadable: make it again with the two commands above):

| Name | Typed | Instructions | Trace lines | SCSI commands on the tape |
|---|---|---|---|---|
| pwd | `pwd` | 29,867 | 238,706 | 21 |
| echo_string | `echo("a b c")` | 119,086 | 517,878 | 25 |
| echo_list | `echo([a,b,c])` | 128,432 | 549,572 | 25 |
| echo_new_atom | `echo(zorkqx)` | 122,214 | 525,706 | 25 |
| usage_echo | `usage(echo)` | 134,283 | 559,339 | 25 |
| help | `help` | 36,685 | 340,013 | 27 |
| who | `who` | 148,036 | 594,630 | 25 |
| history | `set hl=20`, `history` | 56,133 | 460,085 | 41 |
| rs | `rs`, (empty) | 191,871 | 866,760 | 36 |
| versions | `versions` | 114,507 | 640,392 | 38 |
| compile_exit | `compile`, `!exit` | 256,137 | 1,108,374 | 45 |
| compile_missing | `compile`, `sample2`, `!exit` | 319,530 | 1,859,522 | 94 |
| compile_sample1 | `compile`, `sample1`, `!exit` | 974,813 | 4,546,925 | 149 |
| compile_work | `compile`, `!package work`, `sample1`, `!exit` | 1,009,886 | 4,865,583 | 178 |
| ts | `ts`, (empty) | 160,945 | 705,103 | 34 |
| listener_sieve | `compile`, `!package work`, `sample1`, `!exit`, `listener`, `default_package(work).`, `sample1:sieve([1,2,3],E,O).` | 1,575,086 | 7,144,906 | 249 |
| pipe_echo (R7P) | `echo("a b c") \| lc` | 311,242 | 1,325,831 | 25 |
| pipe_three (R7P) | `echo("a b c") \| cat \| lc` | 501,560 | 2,123,497 | 25 |
| pipe_grep (R7P) | `grep(":-") <= file("sample1.kl1") \| lc => window("out")` | 465,694 | 2,038,170 | 42 |
| pipe_primer (R7P) | `grep(":-") <= file("sample1.kl1") \| lc` | 286,597 | 957,748 | 15 |
| ls (R7; R8's home) | `ls` | 174,299 | 804,300 | 32 |
| gc (R7G) | `gc` | 89,179 | 368,543 | 18 |
| gc_listener (R7G) | `gc`, the compile_work lines, `gc`, the listener_sieve lines | 1,752,873 | 7,880,429 | 283 |
| listener_sieve_limit (R7G 5) | listener_sieve's, heap limit 2,952,727 | 1,575,086 | 7,144,911 | 249 |
| pipe_three_limit (R7G 6) | pipe_three's, heap limit 2,000,000 | 501,560 | 2,123,508 | 25 |
| ts_limit (R7G 5) | ts's, heap limit 2,050,000 | 160,945 | 705,106 | 34 |
| ts_short (R7G 5) | ts's, heap limit 1,900,000: `gc: memory shortage` | 135,590 | 431,779 | 5 |
| ts_heap_full (R7G 5) | ts's, heap limit 2,000,000: `heap full: past the heap limit` | 135,785 | 445,203 | 5 |
| listener_pools (R7) | `listener`, `print_length(2).`, the primer's bag, keyed_bag and keyed_set goals | 967,660 | 3,847,621 | 104 |
| pkl1_held (R8) | `compile`, `!package work`, `nrev`, `!exit`: refused by the held compiler | 1,275,047 | 6,138,452 | 217 |
| pkl1_fact (R8) | the same lines for `fact_r8`, then `listener`, `default_package(work).`, `fact:fact(10,R).` | 1,335,291 | 6,328,026 | 249 |
| pkl1_nrev (R8) | ... `nrev_r8` ..., `nrev:nrev([1,2,3,4,5,6,7,8],R).` | 1,466,386 | 6,820,828 | 249 |
| pkl1_qsort (R8) | ... `qsort_r8` ..., `qsort:qsort([27,74,17,33,94,18,46,83,65,2],R).` | 1,852,929 | 8,142,420 | 249 |
| pkl1_kkqueen (R8) | ... `kkqueen_r8` ..., `top:go(9,M).` | 5,419,133 | 17,463,720 | 249 |

R7P (2026-11-25, the pipe; `../docs/binary_reverse_engineering.md`
1.4, "R7P, the pipe"): the four rows above, measured on both models
from the R7L prompt checkpoint, every line identical. No model was
changed for them. pipe_echo and pipe_three write `$$$ Line = 1 $$$`,
pipe_grep `$$$ Line = 5 $$$`; pipe_primer, the primer's line as
printed, is the held PIMOS's own failure (a reduction failure in
`task_stdio:invoke_std_handler/3`, the console's `EXCEPTION WAS
OCCURRED in PIMOS : error code:`, nothing written, the run dry with
1,373 goals waiting), the same on both models.

R7G (2026-11-25, `gc`): `collect_garbage` asks and the core's
collector (`PimmGcBox.bsv`) copies at the next goal switch, as the
reference's (`ref/pimm/pimm_gc.py`, INFERENCE/OURS by ANALOGY with
VPIM's) does; the `K gc` lines are identical, `K gc 32768 77892213
77892213 79768684 a8652141` (the heap from 77.86M cells to 1.88M), and
in gc_listener the second, `K gc 77892213 82173730 32768 2452104
638807af`, back to the heap's base; every later line (addresses
included) identical. Injections in the box (observed, each FAIL at
the line given, every other line before it identical): the links
pass clearing every link, the K line's checksum `0e81de44` (line
198,832); a mixed block's unbound variable not moved in, the K line
`... 79768686 763810b1`; a waiting SCSI command's first variable not
moved, `E error: scsi: a waiting command's variable was not free`
where the reference writes it (line 254,630).

R7G stage 5 (2026-11-25, when memory runs out; INFERENCE/OURS,
`../ref/pimm/pimm_gc.py` "When memory runs out",
`../docs/binary_reverse_engineering.md` 1.4 `gc` item 5): RESTORE 5
gives the goal box a heap limit L (`PimmGBox.setLimit`; 0, none, in
every other run). An allocation that takes hp - lo past L - 4096
(`heapInsurance`, VPIM's `_HEAP_END_INSURANCE_OFST`) raises `heapLow`,
which `PimmGcBox.requested` answers as it does `collect_garbage`; once
the heap has been collected, one past L stops the core `heap full:
past the heap limit`; a collection that leaves more than L - 4096 live
stops it `gc: memory shortage` after its K line. In lockstep (APPS
`listener_sieve_limit`, `ts_limit`, `ts_short`, `ts_heap_full`;
`lockstep_shell.py` LIMITS): every line identical, the counts in
PINNED. Injections, each a copy of `bsv/` with one line changed, run
against a kept work directory (observed 2026-11-25; every line before
the one given identical):
`low <= True` dropped (no limit request), ts_limit FAIL at line 4,107,
the reference's first `K gc` where the core picks `G 77832990`;
`heapLo <= nlo` dropped in `gcSet` (the heap in use measured from the
old half), ts_limit FAIL at line 4,220, `E error: heap full: past the
heap limit` 58 instructions in; the insurance 0, ts_limit FAIL at line
514,442, the second `K gc` not made; the hard limit's `fatal` dropped,
ts_heap_full FAIL, the core's trace goes on past the reference's stop;
the shortage's `fatal` dropped, ts_short FAIL the same way; RESTORE 5
dropped (`DROPPED` ('ts_limit', 5), `INJECT=1`), FAIL at line 4,107.

R7G stage 6 (2026-11-25, the collector's paths no session reached
before): with the limit placed so a collection falls where they are
non-empty (`lockstep_shell.py` LIMITS and GC_PATHS; `compare` fails if
the reference's run took a named path zero times), every root is now
moved in lockstep: a goal parked in a shoen (pipe_three_limit), the
goals made ready since the last pickup, the merger's `mwh`
(pipe_three_limit), a non-empty merger list `mq` (listener_sieve_limit),
`set_timer`'s armed alarm (ts_limit, ts_short) and a `to_processor`
goal's code argument (listener_sieve_limit, ts_short). Injections in
`PimmGcBox.bsv` (observed 2026-11-25, as above): the parked goal's
`SH_GOAL` not rewritten, pipe_three_limit FAIL at line 675,002, the
second `K gc`'s checksum `45f3393b` for `b318d5ed`; `to_processor`'s
code not rewritten, ts_short FAIL at line 150,833, the second `K gc`'s
checksum `9678e84c` for `ffc093ec`; the alarm's `setWakeup` dropped,
ts_limit FAIL at line 523,673, `E error: the Wakeup of set_timer is
bound`; `nMq` left the from-space list (`gbox.mqOf`),
listener_sieve_limit FAIL at line 2,388,104, the goal picked after the
second `K gc` (`G 80788823` for `G 33070`); `nMwH` left so,
pipe_three_limit FAIL at line 675,004 (`G 79850166` for `G 33042`).
(Dropping the `nMq`/`nMwH` assignment altogether fails at the first
collection, line 4,108, whatever the lists hold, so it does not test
the path; the injections above do.)

R8 (2026-11-25, `../docs/binary_reverse_engineering.md` 1.4, "R8, the
pkl1 samples"): the five `pkl1_*` rows above, measured on both models
from the R7L prompt checkpoint (made afresh from the link checkpoint,
8,595,408 instructions), every line identical. No model was changed.
As a control, the 28 rows that came before R8 were re-run on the
reference from the remade checkpoint with the new home files, and
each passed its pin and its window.
The home directory gained the four pkl1 samples (`../docs/pkl1/`) and
their adaptations `NAME_r8.kl1` (OURS, `longrun_ipl.PKL1_ADAPT`), so
`ls` was re-measured: nine lines where it had one, 174,299
instructions and 804,300 lines (was 164,287 and 768,488), PASS on both
models; and the FEP emulator's held card (`tools/mkfepcard.py --held`)
has 64 entries where it had 56, entries 54-61 the eight new files
(`run_fepemu.sh` PASS, the tapes unchanged). The answers are the
Listener's: ` R = 3628800`, ` R =[8,7,6,5,4,3,2,1]`,
` R =[2,17,18,27,33,46,65,74,83,94]`, ` M = 352`, each KLIC 2.002's;
pkl1_held pins the held compiler's refusal of the file as distributed.
Observed injections (2026-11-25, private copies, run on pkl1_fact's
kept checkpoint): `PimmMBox.bsv`'s multiplier stopped after 3 of its 32
steps: FAIL at line 1,434,053, instruction 288,310 (`R 3 0000000064` /
`R 3 0000000014`, a product of the compile itself, long before the
goal); a product of 3628800 given as 3628801: FAIL at line 6,149,926,
instruction 1,315,168 (`R 3 0000375f00` / `R 3 0000375f01`, fact's last
multiply). On the reference alone (`pimm.py` `i_b_multiply`, the same
3628801): the counts equal pkl1_fact's pin, and the window check fails
on ` R = 3628801`: the answer, not the pin, is what catches a wrong
result both models would share. `home_listing` without the version,
re-observed with the nine files: `ls` FAIL, 807,269 lines and 174,515
instructions against the pin.

R7 `ls` (2026-11-25): the home directory through 204 and 237
(`ref/pimm/fep.py` `listing`, the reply's form INFERENCE from PIMOS's
reader, `../docs/fep_services.md` U7), ` >sys>user>pmpsi>sample1.kl1.1`
then the prompt, on both models; the FEP emulator serves the same
(`PimmFepEmu.bsv`, a card entry flagged a directory), checked by the
"direct kernel" tape's section 12 (`run_fepemu.sh`).

(2026-11-25) compile_missing typed `sample1` until the home directory
served the primer's `sample1.kl1` (`longrun_ipl.HOME_FILES`, 221 and
222 in `fep.py`); it now types `sample2`, which the home lacks, the
same run but for the name (its counts and its two `DROPPED` lines
unchanged, re-run). compile_sample1 reads the file; it ended refused on
both models (first at `refused: a merger input bound to a vector of
seven or more`; since the long-vector merge, rule `mergeVecL` and
`lockstep_merge.py` `seven senders`, at `refused: wait_value: an
element (21, ...)`; since the passive-unification box, `PimmPBox.bsv`,
at `refused: new_string(15, 1)`, where the core's last line was the
string box's own stop, `E error`, so the compare failed on that line
alone; since the 1-bit strings, the unary `string_operation` and
`module_element`, 2026-11-25, `lockstep_s1.py`, `lockstep_melem.py`,
the compile runs to its end on both models: the window as
`binary_reverse_engineering.md` 1.4 has it, ending `!ERROR! module
registration error : pimos:: sample1` and the shell's prompt).
compile_work (2026-11-25) types the compiler's `!package work` first
and ends `"work:: sample1" Loaded`, the module loaded
(`binary_reverse_engineering.md` 1.4; `ref/pimm/r7_sieve.py` runs it,
reference only). ts (2026-11-25) stopped at `add_bignum` until it
was in on both models (rules `ba1`..`ba9`, `lockstep_bignum.py`); it
now ends refused on both models at `set_timer` to a time still to
come, its window empty (the compare takes the core's `E unimp`).
`new_string` of another size and `change_element_size` to 1 bit are
now refused by the exec stage (`E unimp`), before the string box.

Which RESTOREs the commands check (2026-11-24, the kept work directory
of the run above, `KEEP=1`): the RESTORE word replaced by a silent SLOT
of the same length, as in the table above, and the command compared
again (`INJECT=1`, or `run_pimm_apps.sh --inject WORK` on a kept
directory; the pinned lines are `DROPPED` in `lockstep_shell.py`;
the table below re-run that way 2026-11-25). The prediction came first,
from the reference, by a scratch probe not kept: `echo(zorkqx)`
makes one `new_atom` (counter 75,569 to 75,570); each compile reads
`system_timer` once. The checkpoint's clock is 204,335,039 steps, 236
past a tick (the timer is `(steps-1)//423`); with RESTORE 3 dropped the
core counts 423 instructions to its next tick where the reference
counts 187, so it is one tick behind only for a read fewer than 236
instructions after one of the reference's ticks: the read is 135 after
one in compile_exit (caught), 357 in compile_missing (not caught).

Re-derived for R7L's checkpoint (2026-11-25; its RESTORE 2 is 483,081
ticks, RESTORE 3 112 instructions past the last): with RESTORE 3
dropped the core counts 423 to its next tick where the reference
counts 311, so it is a tick behind only for a read fewer than 112
after one of the reference's ticks. The compile's `system_timer` read
is now 264 after one in compile_exit (not caught) and 63 in
compile_missing (caught), so the two commands traded roles: the table
below is the R7L run, and compile_exit's 3 is now the control.

| Command | RESTORE dropped | Result |
|---|---|---|
| echo_new_atom | 1, `new_atom`'s counter | FAIL at line 27,640, instruction 8,124: `R 8 0200012731` on the reference, `R 8 0200010000` on the core (the atom numbered from the reset value) |
| echo_new_atom | 2, 3 | PASS: no clock read |
| compile_exit | 1 | PASS: no `new_atom` |
| compile_exit | 2, the ticks | FAIL at line 902,215, instruction 235,341: `R 9 0000076135` / `R 9 000000022c` |
| compile_exit | 3, the instructions since the tick | PASS, as predicted: the read falls 264 past a tick, past the 112 |
| compile_missing | 2 | FAIL at line 1,568,167, instruction 289,707: `R 9 00000761b6` / `R 9 00000002ad` |
| compile_missing | 3 | FAIL at the same line, as predicted (63 past a tick): `R 9 00000761b6` / `R 9 00000761b5`, one tick short |
| pwd | 16-21: unit, lun, direction, length, the cdb's word, the cdb's length | FAIL at line 1: the trace's first command line (`B 7 1 0820004000 2 16384` on the reference) |
| pwd | 22, the buffer's word | FAIL at line 12, a write of the data |
| pwd | 23, the buffer's length | FAIL at line 4 |
| pwd | 24, 25, 26, the three outs | FAIL at lines 4,101, 4,102, 4,103, the three writes after the data |

The pwd rows (2026-11-25) drop each field of the one command waiting
in the checkpoint (unit 7, lun 1, a 5-byte cdb, direction 2, 16,384
bytes). With 21 dropped the core writes one line and goes silent, so
the compare waits for its next (16 minutes, then killed); `inject`
now runs each sim in the background into a fifo with a watchdog that
kills it (its own PID) after `INJECT_LIMIT` seconds, 600 by default,
and the compare then reads the end of the trace and prints the same
FAIL at line 1.

So each of RESTOREs 0-4, 16-26 and the waiting command's push is now
caught by some window: 0, 4 and 31 by `shutdown`/`yes`, 1 by
`echo(zorkqx)`, 2 and 3 by `compile`/`!exit`, 16-26 by `pwd`.

## FPGA flow (ULX3S / ECP5)

`PimUlx3s.bsv` and `Top.v` are a downstream check, not the architecture.
The recorded 10.22 MHz figure came from the 07:33 `nextpnr.log`, before
the WP3.1 `PimE` change, and does not reproduce. A fresh
`run_fpga_build.sh` run on the current tree reports **28.32 MHz**
(PASS at 25 MHz); a pristine `git archive HEAD` build measured
**55.35 MHz**. The earlier failing path was the store read-data mux and
cache-valid comparison gated by the E-stage valid (97.8 ns total in
that log); the fresh build no longer reports it as the limit.

Status: **not hardware-ready** until the owner re-decides WP2 on the
committed tree. Do not present the bitstream as a working PIM/m, and do
not rest any cycle-accuracy claim on it. The historical-accuracy rule in
`../plan.md` forbids reordering the documented pipeline for FPGA
convenience; a future retime must be shown not to change the documented
structure.

## Build check

`run_fpga_build.sh` reproduces the downstream ECP5 flow from a clean
tree: it regenerates `generated/*.hex`, recompiles `PimUlx3s.bsv` to
Verilog, runs Yosys, `nextpnr-ecp5 --85k --package CABGA381 --speed 6`
with `--timing-allow-fail`, and `ecppack --compress`, all in a fresh
`fpga_build/`. Required tools: `bsc` 2026.01, Yosys 0.51,
`nextpnr-ecp5` 0.6, `ecppack` (Trellis) 1.4. It prints the measured
Fmax and the WP2 gate; a timing miss is not a build failure, but missing
tools or a failed synthesis/place/route/bitstream step exits nonzero.

## The FEP emulator on the ULX3S (`../docs/scsi_plan.md` S1h)

The owner asked for "a scsi emulator on the ulx3s using either sdram,
qspi flash or the sd card". It uses the **SD card**: the 32 MB SDRAM
already holds the PIM/m local store (`PimUlx3s.bsv`, `PimSdramStore`);
the QSPI flash holds the bitstream, is a few MB, and is awkward to
rewrite from the host; the SD card is large, removable, and written by
the host, as the FEP's own disk was. The emulator plays the FEP's part
(`../ref/pimm/fep.py`, put in hardware): a processor-type SCSI target at
unit 7 (SEND on LUN 0, RECEIVE on LUN 1, TEST UNIT READY), the packet
layer and the IPL's file service (read_open 201, getb 210, close 60,
abort 70; statuses 1, 2, 5), and what `fep.py` has for PIMOS's start
(INQUIRY 12h to unit 7, five bytes `03 00 07 00 00`; TEST UNIT READY to
the absent units 0-5, Result `800h`, decided in `Fep.command` as in
`fep.py`, so in the emulator and not the adapter; `append_open` 203,
answered `[1]`), and (2026-11-24, `fep.py` with PIMOS's start reaching
the shell's prompt, `../docs/fep_services.md` §6-§7) the timer
(`create_timer` 310, `get_date_time` 304 from the clock the `setTime`
input gives, its close), `fep_attributes` 240, the pimos: files from
the card (`mkfepcard.py --held` puts the held object directory there; a
name not on the card is 5: `autoload.tbl`, `me:`, the home), the login's
string-I/O programs (601, 620 on the replier, the local and tcpip
servers, `simpos_user_device`), the window calls (104, 127, 130, 132,
141-143, 111, 112), close (60) of every kind, 112 on a read file, and
the **held requests** (the login server's io(1), a window's getl 110):
no reply when they arrive, so the core's RECEIVE stays outstanding
(`FepNotReady`, the waiting list of `PimmScsiBox` polled, as `pimm.py`
does with `fep.py`'s `None`), until the **event** (`idle`, the bench's
question when the machine has run dry, `Fep.idle()`) takes the next
entry of the card's script and answers the lowest device holding that
kind; 70 on a held device answers it `[6]`. `fep.py`'s constants are on
the card, not in hardware: the attributes message and the script
(`mkfepcard.fep_tables`), so a scripted line `fep.py` gains is a new
card. Answering as `fep.py` does byte for byte, with its OURS
choices. `putb` (111), `getb` and close on a device that only appends
still raise in `fep.py`, so they are refused here, and no log is kept
(the card stays read-only). Each file's header says what is OURS and
what comes from `fep.py` and the PIMOS source.

| file | what it is |
|---|---|
| `PimmFepEmu.bsv` | `mkPimmFepEmu`: the FEP. `Server#(FepCmd, FepAnswer)` (unit, LUN, CDB, direction, length; answer done / not ready / refused), `sendData` / `recvData` byte streams, `configure` (`fep.py`'s test options), `idle` (the event; answered on `cmd.response`), `setTime` (the FEP's clock), `maxBuffer` (16000, for `scsi_init`), and an `SdBlockClient` for the card |
| `PimmSdTypes.bsv` | the block interface: 512-byte block reads, an `err` byte on failure, no write |
| `PimmSdBlock.bsv` | `mkPimmSdBlock`: the microSD slot in SPI mode (our own design; read-only by construction; no tristate) |
| `PimmSdBlockFile.bsv`, `.c` | the card as a host image file through BDPI (Bluesim only, opened `rb`) |
| `PimmSdCardModel.bsv` | an SPI-mode card model over the image (Bluesim only), so `mkPimmSdBlock` runs before any board |
| `PimmFepEmuTb.bsv`, `.c` | the bench: replays a tape's commands, prints each answer |
| `PimmFepEmuSpiTb.bsv` | the same bench over `mkPimmSdBlock` and the card model (block-addressed v2 and byte-addressed v1 cards) |
| `fepemu_check.py` | makes the card and vectors, runs a bench, compares every answer with `fep.py`'s |
| `run_fepemu.sh` | builds the three benches and runs every tape on each (in `../run_tests.sh`; about a minute) |
| `PimmFepUlx3s.bsv`, `PimmFepTop.v`, `ulx3s_fep.lpf` | the board: `mkPimmFepSelfTest` (reads the directory, then opens, reads to the end and closes entry 0 through the emulator's command interface, checks length and sum, reports over the UART) over `mkPimmSdBlock` |
| `PimmFepUlx3sTb.bsv` | the self-test in Bluesim over the SPI reader and card model |
| `run_fepemu_fpga.sh` | the self-test in Bluesim, then yosys / nextpnr-ecp5 / ecppack |
| `../tools/mkfepcard.py` | builds a card image (format in its header), `--list` reads one |
| `../ref/pimm/record_fep.py`, `../ref/pimm/fep_tapes/` | records the commands `ref_scsi.py`'s parts give `fep.py`, two direct sequences of OURS (`direct`: what the IPL never does; `direct_kernel`: the answers for PIMOS's start and their edges), and `kernel`, recorded from PIMOS's start to PIMOS END after a typed shutdown (`--kernel PKL --type shutdown --type yes`, a machine `longrun_ipl.py --reference --save` wrote); a tape also holds the clock (`ticks N`) and the events (`idle`) |

**Verification.** `run_fepemu.sh`: each tape (one file, two files,
characters, late, odd, small buffer: every call `ref_scsi.py`'s machine
run made of `Fep.command`, retries and unanswered RECEIVEs included;
`direct`: a failed open, abort, a request in two packets, a reply cut
three times, two devices, each `FepError`; `direct_kernel`: INQUIRY,
the absent units, `append_open`, then everything from 240 to the
shell's prompt with its edges (cut replies, the clock at midnight and at
the top of 48 bits, unjis's readings of a name, overlapping device
sets, holds, events under a script of two logins and two lines), and
every `FepError` next to them; `kernel`: every call PIMOS's start made
of `Fep.command` and `Fep.idle` to PIMOS END after a typed
`shutdown` and `yes`, 8,766,319 instructions, recorded under the merger
rule and re-recorded with the login ID 0 (8,766,339 with the ID 1); 8,586,110 to the prompt before it) is replayed into a fresh
`fep.Fep` for the expected answers and into the emulator, over a card
with decoy entries (a prefix and an extension of each real name, ahead of
it), on three benches (the image file; the SPI reader with a
block-addressed card; with a byte-addressed card). 9 tapes, 827
commands and 18 events (2026-11-24, to PIMOS END: the standard I/O
window, the append-opened file's close, terminate; 714 commands and 12
events to the shell's prompt before; 293
commands before), all answers equal on all three. Injected faults and
what each was observed to fail: the header of `PimmFepEmuTb.bsv`.

**Synthesis** (`run_fepemu_fpga.sh`, yosys 0.51, nextpnr-ecp5 --85k,
2026-11-24, to the shell's prompt: the timer and its clock, 240,
string-I/O, windows, holds and the event; re-run 2026-11-24 after the
standard I/O window, the append-opened file's close and terminate were
added: 14,816 LUT4 (11,440 logic, 3,166 carry, 140 RAM), 4,259
TRELLIS_FF, 3 DP16KD, 19 I/O, **35.03 MHz** (PASS at 25 MHz); before
them): 14,799 LUT4 (11,423 logic,
3,166 carry, 140 RAM), 4,243 TRELLIS_FF, 3 DP16KD, 19 I/O; **36.69
MHz** (PASS at 25 MHz). +4,300 LUT4 and +1,078 FF over the line below
(not broken down: the eight device slots, four hold slots, the 32-byte
home buffer, the name comparator and the clock's divider are the
likely shares); no BRAM added, the constants being on the card. The
self-test now drives `setTime` from a 1/16-msec counter so the time
path is built; nothing on the board top calls `idle` (the core's
port, not yet connected, would). Before (with INQUIRY, the absent units and `append_open`): 10,499
LUT4 (8,011 logic, 2,278 carry, 140 RAM), 3,165 TRELLIS_FF, 3 DP16KD,
19 I/O; **42.50 MHz** (PASS at 25 MHz). Before them (2026-11-23):
10,039 LUT4 (7,553 logic), 3,099 FF, 3 DP16KD, 40.39 MHz: +460 LUT4,
+66 FF, no BRAM (not broken down among the 32-bit Result, the two
appending slots and the new branches); the Fmax
rose although nothing was made shorter (place-and-route's spread from
build to build, presumably: not measured). The
self-test passes in Bluesim on the `--held` image (entry 0,
`pimos:pimos.ipl`: 1,678 bytes, sum 00019246h). No board has run it.

**Pins** (`ulx3s_fep.lpf`): sd_clk H2, sd_cmd J1 (MOSI), sd_d0 J3 (MISO),
sd_d3 K2 (CS), sd_d1 H1 and sd_d2 K1 inputs, LVCMOS33, pull-up, from
`~/src/ulx3s-experiments/flute-lx50/constraints/ulx3s_85f.lpf`
lines 45-57 (verified on this board by that project) and the same as
prjtrellis `ulx3s_v20.lpf` lines 112-128. The UART is `ftdi_rxd` (L4),
the line the FPGA transmits on ("FPGA transmits to ftdi",
`ulx3s_v20.lpf` line 17). `wifi_en` is held low (the ESP32 shares the
SD pins).

**On a board: the owner's steps, none run here.** The board on this
machine runs the Flute Linux core for another session (2026-11-23):
loading this bitstream replaces it, so it waits for a window arranged
with the session lead. Use a card of your own, not the one holding the
Flute Linux boot (that card is read-only for everyone): `dd` overwrites
everything on the card it is given.
```
python3 tools/mkfepcard.py /tmp/fep.img --held        # from pim/
python3 tools/mkfepcard.py --list /tmp/fep.img
diskutil list                                          # find the card: /dev/diskN
diskutil unmountDisk /dev/diskN
sudo dd if=/tmp/fep.img of=/dev/rdiskN bs=1m           # check N twice
openFPGALoader -b ulx3s bsv/fpga_build_fepemu/ulx3s_fep.bit   # SRAM, not flash
screen /dev/tty.usbserial-* 115200
```
Expected: LEDs 0, 2 and 3 on (card ready, mounted, PASS), and every
1.3 s `PIMFEP PASS n=0000068e s=00019246 want n=0000068e s=00019246`.
FIRE1 starts again. LED 1 is a card that did not initialize; LED 4 FAIL,
with the step in LEDs 7..5 and on the line.

**The adapter to the core.** `bsv/PimmScsiBox.bsv` (being written
elsewhere) puts the device on a port of `mkPimmCore` (`scsiReq` /
`scsiResp`). The adapter between that port and this emulator, a thin
module of rules, must: (1) turn a request into a `FepCmd` (unit and LUN
as 32 bits, the CDB string's bytes and length, the direction, the
length), and for direction 1 put exactly `length` bytes of the buffer on
`sendData`, whatever the answer (pimm.py `scsi_do` hands `fep.py`
`buf[:length]`); (2) on `FepDone` give the core the answer's `result` (0, or `800h`
for an absent unit's TEST UNIT READY: 32 bits, as `scsiResp`'s), the
transferred length (`count` for direction 2, `length` otherwise, as
`scsi_do`) and, for direction 2, the `count` bytes from `recvData` to
write into the buffer string; (3) on `FepNotReady` keep the command and
offer it again later, as `Machine.scsi_poll` does (after any command
that finishes, and when the core has nothing to run), binding Id and
NewObj at once and the rest when it finishes; (4) on `FepRefused` stop
loudly (the reference raises `FepError`); (5) give `scsi_init` Info[0]
from `maxBuffer`.

## The SIMPOS window framebuffer (`WinFbBox.bsv`)

Milestones H0-H3 of `../docs/simpos/window_hardware_plan.md`.
`mkWinFbBox#(fontFile, pclk, prst)` is the SIMPOS display's drawing hardware: a
`Server#(WinFbCmd, WinFbRsp)` box with BRAMs for the 1-bit 1280×1024
frame, the window save areas, the `test_11` font and its JIS code index,
and engines for blit (fill, copy, save, restore, glyph), Bresenham lines
and the dump. It imports only standard libraries. The display hardware
is undocumented, so all of it is OURS scaffolding. The command format is
frozen in the header of `../psi/winfb.py`, the Python reference.
`WinFbBoxTb.bsv` (hand-written, committed) reads a command stream and
writes P4 PBM frames plus status files. `run_win_tb.sh` runs 11 streams
on both the box and the Python layer and `cmp`s every frame and status
file. Its header lists the injected faults and which streams catch each.
Measured cycle counts are in the box header.

**The scan-out (`WinScanOut.bsv`, H2).** `mkWinScanOut#(box.scan)` reads
the frame through the box's scan port (port B, in the pixel clock's
domain since H3; the dump uses port A). Its submodules are:
- `mkWinTiming`: one table of modes. 0 is 1920×1080@30 with the frame
  letterboxed 1:1, 1 is 1280×1024@60 DMT, 2 is 1280×1024 reduced
  blanking (OURS), 3 is 640×480 with a 2×2-OR 2:1 reduction from row
  panY. Custom timings are accepted too.
- `mkWinFetch`: one word read per 16-dot group, two in the 2:1 mode, into
  a small queue.
- `mkWinCursor`: the 16×16 mask/image overlay. It has 8 shapes, takes its
  position at the frame start, and is never written into the frame.
- `mkWinTmdsEnc` ×3: DVI 1.0 Fig. 3-5.
- `mkWinTmdsSer`: the 10:1 serializer, two bits per shift clock.

The references are `../psi/winscan.py` (modes, timing model, view,
checkers) and `../psi/wintmds.py` (TMDS encode and decode, cited by DVI
1.0 page); their unit tests are `../psi/test_winscan.py`. There are three
hand-written benches:
- `WinScanOutTb`: draws a stream, captures one frame plus a few lines of
  characters, and dumps the frame again afterwards;
- `WinTmdsEncTb`: every byte from every disparity state, plus runs and
  random data;
- `WinTmdsSerTb`: the serializer, with the pixel clock made by
  `mkClockDividerOffset(5, K)` for each K = 0..4 (all five alignments),
  a null crossing, and `WinCrossModel` (below).

`run_win_tb.sh` decodes every capture in Python and compares it with the
references clock by clock: sync levels, DE, pixels, the three channels,
the disparity bound, and the characters re-encoded. It runs 17 scan cases
(the four modes, mode 2 without a cursor, 12 small random timings). Its
header lists the scan-out injections and what each was seen to fail.
`WIN_PART=h2` runs only the scan-out part (and H3's bench).

**The board design (H3).** `WinFrame.bsv` (`mkWinFrame`) is the frame
banked by hand: 80 `mkSyncBRAMCore2` of 1,024 words (one DP16KD each),
port A in the system clock (registered request, latency 2), port B in
the pixel clock (registered request, two registered mux levels, latency
4). `WinUlx3s.bsv` holds `mkWinCore` (the box, the scan-out in the pixel
domain behind a `mkSyncFIFO` of commands, and a self-test that draws
`winscan.py`'s mode 0 test card from a load file and starts mode 0) and
the synthesized `mkWinUlx3s`, whose serializer takes the pixel word and
the pixel domain's `tog` bit over null crossings and derives its load
phase from `tog` (flute-lx50's `dvi_ser` method; the serializer's
header gives the timeline). `WinUlx3sTop.v` is the Verilog top (PLL,
reset, ODDRX1F); `ulx3s_win.lpf` cites its pin sources.
`WinUlx3sTb.bsv` runs `mkWinCore` with three clocks (system period 27,
pixel 10, shift 2 time units) and checks the self-test's frame, a whole
mode 0 frame of characters and three lines of serial bits.
`WinCrossModel.bsv` is bench-only: it turns the pixel word to garbage
when the shift domain samples it on the shift edge where it changes or
on the one before the next change (ages 0 and 4 of 0-4), so a serializer whose sample phase is not tied to
the pixel clock fails the serializer checks (H2's uncaught injection
#14 is now caught). `run_win_fpga.sh` builds the bitstream: bsc
-verilog, yosys `synth_ecp5` (with `share` left out: it merged the
multipliers of exclusive rules into one, on the system clock's critical
path), nextpnr-ecp5 `--85k --package CABGA381` on seeds 1-3, ecppack,
and `../tools/win_fpga_check.py`, which fails the build if a clock
misses its frequency, the DP16KD count is not 156, the serializer's 11
replicated flag flops were merged, or the pclk -> sclk transfer exceeds
2.70 ns (nextpnr 0.6 reports cross-domain paths but
cannot constrain them). Measured results (2026-11-25, seeds 1-3, all PASS:
sclk 384.76-418.24 MHz at 370.10, pclk 74.53-79.43 at 74.00, system
32.65-34.91 at 25; 9,671 TRELLIS_COMB, 3,612 FF, 156 DP16KD) are in the
plan's §5.1 and its H3 status. A full run took about 7 minutes (2026-11-25). Output: `build-winfpga/ulx3s_win.bit` (gitignored). The
owner programs it; no agent runs this:

```
openFPGALoader -b ulx3s bsv/build-winfpga/ulx3s_win.bit   # from pim/, SRAM only
```

LEDs: 7 the PLL lock, 0 the self-test done, 1 a self-test error (a
command status not OK), 2 toggles every 16 frames of the pixel domain
(a period of about 1.07 s at 29.9 Hz).

## Regression

`../run_tests.sh` chains the assembler selftest, the ISA table check,
the Bluesim smoke test (`run_smoke.sh`), the negative-opcode testbench
(`run_neg_tb.sh`), the KL1-B testbenches (`run_kl1b_tb.sh`), the
network-unit testbench
(`run_nu_tb.sh`), the link testbench (`run_link_tb.sh`), the routed
crossbar testbench (`run_nu_routed_tb.sh`), the mesh testbench
(`run_mesh_tb.sh`), the SDRAM-store testbench (`run_sdram_tb.sh`), the
FEP emulator against `fep.py` (`run_fepemu.sh`) and
the formal BMC (`formal/run_formal.sh`). The board build checks are
`run_fpga_build.sh`, `run_fepemu_fpga.sh` and `run_win_fpga.sh`.
