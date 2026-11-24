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
| `PimmShBox.bsv` | shoen box (stages 1 and 2): the shoen record, the report stream, start, the count and the reductions at the end of a reduction, termination, statistics, remove (and a remove pending until termination) |
| `PimmScsiBox.bsv` | SCSI box: `scsi_init` and `scsi_command` (OURS, as the reference model's: the firmware is lost), the device OUTSIDE the core on its port `scsiReq`/`scsiResp`; the commands that wait for the device, and the poll (`scsiPoll`) when the machine has run dry |
| `PimmStages.bsv` | fetch stage; execute stage (clause selection, the variables guards met unbound) |
| `PimmCore.bsv` | the modules above and the rules that move an instruction between them |
| `PimmDriverTb.bsv` | lockstep driver bench: executes a test's script of operations on the core (`../ref/pimm/driver.py`), and answers the core's SCSI port from the script's device tape, printing a `B` line per command from what the core sent |
| `generated/PimmGen.bsv`, `generated/pimm_ipl.hex` | tags, opcodes, predicate addresses, record layouts, and the image followed by the built-in stubs, written by `../asm/gen_pimm_bsv.py`; no tag or opcode is typed by hand |

`run_pimm_lockstep.sh` builds into `build_pimm/`, and for each test
(`../ref/pimm/lockstep_*.py`) writes its script, runs the driver on it
and pipes the trace into the test (with arguments, only the tests named). Forty-four tests: `jtoa` (`convert_element/2`, every
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
goal here, `PimmNBox.bsv`, not the machine's merger cell) and `load` (`ipl_loader:load_file/9`
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
the end; statistics of a running shoen. `alt`: `read_eagerly` (what the compiler
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
`scsi`: `scsi_init` and `scsi_command` (`PimmScsiBox.bsv`) at their
sites (`scsi:create/2`, `scsi:command_executer/2`), the device on the
tape the reference model recorded: TEST UNIT READY, SEND, RECEIVE, a
reply cut in two, a command that waits finished inside a SEND and one
at a poll, an element waited for; then `ref_scsi.py`'s six IPL parts,
the IPL reading its list and its files through its own SCSI stack; the
bus bytes compared as `B` lines.

`run_pimm_longrun.sh` is the long run, outside the suite (about two
hours; run whole on both models 2026-11-23: 447,739,516 trace lines
identical): the IPL's `load/4` on the whole held `pimos.ipl`,
twenty files, compared line by line with the reference model, the
answer checked to be `normal` with the code of `pim:go/4`
(`ref/pimm/longrun_ipl.py`).
State: 136
instructions (a recount, 2026-11-23: 136 handlers in `pimm.py`, all on
both models since `scsi_init` and `scsi_command` joined; 134 without our
two stubs; the earlier 128 and 130 were increments); goals as
records in memory on a ready queue; a goal that cannot choose a clause
is written back, hooked on the variables it waits for, and woken when
one is bound; a body built-in with an unbound input becomes a goal of
its stub (layouts: `../asm/pimm_layout.py`, the project's design, see
`../docs/pimm_semantics.md`). Sequential (the next fetch waits for the
instruction before it), no timing claimed. The MRB is kept, and `set_vector_element`
updates in place on it (`PimmVBox.bsv`); nothing is reclaimed and strings are always copied
(`../docs/pimm_semantics.md` "The MRB"). The shoen: `create_shoen`, `start_shoen`, termination, `shoen_statistics` and `remove_shoen`
(a goal knows its shoen, a shoen counts its goals and children and its reductions, and reports `started`,
`terminated`, `statistics_started`, `statistics`, `return_resource` and its close);
its other built-ins (stop, abort, resource, profile), `raise`, `resource_low` and a failure inside a shoen stop the model or are never reported.
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

## Regression

`../run_tests.sh` chains the assembler selftest, the ISA table check,
the Bluesim smoke test (`run_smoke.sh`), the negative-opcode testbench
(`run_neg_tb.sh`), the KL1-B testbenches (`run_kl1b_tb.sh`), the
network-unit testbench
(`run_nu_tb.sh`), the link testbench (`run_link_tb.sh`), the routed
crossbar testbench (`run_nu_routed_tb.sh`), the mesh testbench
(`run_mesh_tb.sh`), the SDRAM-store testbench (`run_sdram_tb.sh`) and
the formal BMC (`formal/run_formal.sh`). The board build check is
`run_fpga_build.sh`.
