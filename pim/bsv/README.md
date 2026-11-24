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
| `PimmSBox.bsv` | string box: length and size, element, new string, set element |
| `PimmShBox.bsv` | shoen box (stages 1 to 3): the shoen record, the report stream, start, the count and the reductions at the end of a reduction, termination, statistics, remove (and a remove pending until termination); the exception message (the mask walk, the handler's `apply` goal, Info), stop, abort, and the check of each goal taken inside a shoen (run, park, discard) |
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
and the layout of the image's own modules) and `file`, `file3` (`ipl_file_decoder:decode/8` on two
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
`s32`: `new_string` with 32-bit elements. `ipll`: the IPL's
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
lines. `pvec`: `wait_value` on two vectors (rules `pv1`..`pv4`), the
IPL's pool `ipl_pool:keyed_set/2` given vector keys. `tproc`:
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
`lockstep_shell.py`), on a shared machine:

| From | Typed | Instructions of `go()` | Trace lines | Ends |
|---|---|---|---|---|
| the prompt | `shutdown`, `yes` | 8,587,092 to 8,766,339 (179,247) | 878,180 | `PIMOS END********`, nothing left to run, 253 goals waiting |
| the prompt | `cat <= file("pimos:pimos.groups")` | 8,587,092 to 8,760,685 (173,593) | 731,110 | `Shell>> ` again, nothing left to run, 1,224 goals waiting |
| the link | `shutdown`, `yes` | 0 to 8,766,339 | 20,107,047 | `PIMOS END********`, nothing left to run, 253 goals waiting; 21 min in all, 897 s of it the Bluesim run and compare |

The last row is the first time PIMOS's start, the login and the shell
have run on the Bluespec core: everything `longrun_ipl.py --go --fep`
does after the link, 221 device answers on the tape, 5,859 splices of
the merger's list (300 onto a list that is not empty). No divergence was found, so nothing in the
core was changed. The splice-order injection into the goal box (the
merger's list) fails the first row at line 8,429
(`lockstep_merge.py`'s header).

State: 168
instructions (a recount, 2026-11-24: 168 handlers in `pimm.py`, all on
both models; 165 without our three stubs; the earlier 128 and 130 were
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
Not modelled: garbage collection, priorities, built-in
exceptions (they stop the model). The bench model and its benches are
untouched and still run.

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
`shutdown` and `yes`, 8,766,339 instructions, recorded under the merger
rule; 8,586,110 to the prompt before it) is replayed into a fresh
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
`run_fpga_build.sh` and `run_fepemu_fpga.sh`.
