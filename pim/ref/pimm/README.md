# PIM/m reference model (scaffold)

`pimm.py` is a host-side model of the PIM/m KL1-B machine that executes
the PIMOS binaries' own cells: it loads `pimm_ipl.kbn` through
`asm/kbn.py` and runs instructions with the machine's tags, encodings
and relative labels. It is the scaffold of roadmap decision 3
(`docs/pimos_roadmap.md`): it exists to find out what the instructions
do, cheaply, and to be the trace the Bluespec model is diffed against.
Nothing is claimed for the project on this model alone.

Rules it keeps:

- An instruction it does not implement raises `Unimplemented`. It never
  guesses and never skips.
- Every operand reading comes from object code paired with KL1 source,
  and is written down in `docs/pimm_semantics.md` with what checked it.

State: all machine state is registers and memory cells (goal records,
the ready queue, suspension records, hooked variables; layouts in
`asm/pimm_layout.py`, the project's design). One processor, newest
goal first, no priorities; body built-ins that wait become goals of a
stub (`asm/pimm_stubs.py`); 8- and 16-bit strings.  The shoen in its
first three stages: `create_shoen`, `start_shoen`, termination,
`shoen_statistics` (twice the reductions, counted per shoen) and
`remove_shoen`; a goal's reduction failure and `raise` reported as
the exception message to the innermost shoen whose mask accepts it,
`stop_shoen` (goals parked until `start`) and `abort_shoen` (goals
discarded) (shoen records in the heap, a goal's shoen in its record's
status cell; `docs/pimm_semantics.md` "Shoen").
`lockstep_repl.py` runs `exception_table:replace_argument/3`, which
reads vectors the script builds (`driver.Script.vector`), and
`lockstep_ground.py` runs `shoen:ground_term/2` on lists and vectors;
`lockstep_rpos.py` runs `exception_table:replace_position/3`
(`switch_on_constant`), `lockstep_dec0.py` the first of the IPL's file
decoder (`b_shift_right`), `lockstep_rss.py` the request-sense analysis
(`integer`, guard `shift_right`, `put_vector_5`), `lockstep_dect.py`
the file decoder on terms, answering its read requests (`put_list`,
`get_nil`, `wait_atom`; `driver.Script.live` and `SLOT`),
`lockstep_deca.py` atoms, proper lists and terms from a real `.sav`
file (`put_constant`, guard `modulo`), strings and long vectors
included, `lockstep_gca.py` whole module-information and GC areas
(`put_atom`, `write_nil`), `lockstep_modc.py` entry tables and code
areas (`b_multiply`, `write_marked_variable`, `write_integer`),
`lockstep_lmod.py` whole modules through `load_module/7` (the general
`put_vector`), `lockstep_ext.py` calls between modules
(`execute_external`, `wait_value`, `wait_constant`),
`lockstep_ptab.py` the IPL's predicate-table builder (fourteen
instructions, listed in its header), `lockstep_pack.py` a goal of
more than eleven arguments, `lockstep_newm.py` whole module objects
(`new_module`), `lockstep_file.py` and `lockstep_file3.py` whole real
object files through `decode/8`, `lockstep_pool.py` the built-in
merger under the IPL's keyed pool, `lockstep_load.py` a real file
loaded by `ipl_loader:load_file/9` with the IPL's own reader and
checksum, `lockstep_mrb.py` `set_vector_element` in place or copied
as the MRB says, `lockstep_atab.py` the IPL's own atom table
(`new_atom`, `hash`) and a file loaded against it,
`lockstep_cons.py` the console (`display_console`),
`lockstep_run.py` a predicate of a loaded module run from the heap,
`lockstep_link.py` the IPL's whole `load/4` with its linker,
`lockstep_unif.py` the unification of two vectors or lists,
`lockstep_s32.py` 32-bit strings, `lockstep_ipll.py` the IPL reading
the real `pimos.ipl`, `lockstep_p2c.py` `predicate_to_code` and
`code`, `lockstep_apply.py` `apply`, `lockstep_where.py` `scsi_where`, `lockstep_shoen.py` the shoen
(`create_shoen`, `start_shoen`, termination, through the image's own
`shoen:execute/4`), `lockstep_shoen2.py` its second stage
(`shoen_statistics`, `remove_shoen`, through the image's three
monitors, the statistics checked against the reductions counted on
the trace), `lockstep_shoen3.py` its third stage (the exception
path, `raise`, `stop_shoen`, `abort_shoen`, `current_processor`,
through the image's `exception_table:translate/4`, `shoen:raise/3`
and its monitors), `lockstep_alt.py` `read_eagerly`
(`alternatively`), `not_equal` and `wait_vector_1`, `_4`, `_6`,
`lockstep_body.py` `b_divide`, `b_modulo`, `b_string` and
`enqueue_goal_to_processor`, `lockstep_elw.py` `string_operation`
waiting on an element of its vector, `lockstep_reuse.py`
`put_reused_structure` of a vector of seven or more,
`lockstep_prio.py` `current_node` and `calculate_priority_from_current`,
`lockstep_atom.py` `top:go1/4`'s atom-number server
(`supply_atom_number`, ours as to what it does) with a merger input
bound to a vector, `lockstep_xmod.py` an external call between two
loaded modules, `lockstep_gmul.py` the guard `multiply`, `save` and
`restore` at the sites of `scsi_fep` in a loaded patch file,
`lockstep_rdvc.py` the guard `diff` at a site in another,
`lockstep_pvec.py` the guard `X = Y` on two vectors (the IPL's pool
with vector keys), `lockstep_tproc.py` `Goal@processor(P)` waiting
for an unbound P, `lockstep_timer.py` `system_timer` and `set_timer`
(the clock at 0, ours), `lockstep_wint.py` `write_integer -1`,
`lockstep_bignum.py` `multiply_bignum_by_word` and `subtract_bignum`
(after VPIM), `lockstep_login.py` the instructions met between the
login and the shell's prompt (`unbound`, the four double-precision
integer built-ins, the guards `module`, `extended_floating_point`,
`bignum_less_than` and `bignum_not_less_than`, `apply` of seven or
more, `enqueue_goal` of more than 16),
`lockstep_float.py` the single-precision float built-ins, guard and
body, against hand-written IEEE constants (`docs/float.md`),
`lockstep_scsi.py` the SCSI built-ins `scsi_init` and `scsi_command`
against a small model of the front-end processor (`fep.py`), the
device on the bench a tape the reference recorded (`driver.py` "The
device tape"; the bus compared as `B` lines), and `ref_scsi.py`'s six
IPL parts (the IPL reading its list and files through its own SCSI
stack) on both models;
`longrun_ipl.py` is the long run (not in the suite); with `--load
--go --fep` it runs `pim:go/4` through the scripted login to the
shell's `Shell>> ` (`docs/fep_services.md` §7).  The home directory's
files (`HOME_FILES`) are the primer's `sample1.kl1` and, since R8
(2026-11-25), four pkl1 samples (`docs/pkl1/`) and their adaptations
`NAME_r8.kl1` (OURS, `PKL1_ADAPT`), which `lockstep_shell.py`'s APPS
`pkl1_*` compile and run through the Listener; since 2026-11-26 all
eight samples (seventeen home files). `r8_entry_trace.py` (OURS, not in
the suite, needs a prompt checkpoint) traces why a file with one
aborted module is not loaded: the loader's `flush/6` entered with
`abnormal`. Since R9 (2026-11-26) the home also holds MGTP/G's four
files, served from the held `mgtp.tgz` (`MGTP_TGZ`), and the axioms
`q8.clause` (the manual's 8-Queens as printed) and `q6.clause` (cut to
6, OURS): twenty-three home files, which APPS `mgtp_q6`, `mgtp_q8` and
`mgtp_pf6` compile and run by the manual's procedure.
`r9_mgtp_probe.py` (OURS, likewise not in the suite) types its sessions
or APPS rows from a prompt checkpoint on the reference and measures
them: the reductions of the query's shoen by kind (`R9_TALLY`), the
list case of `mark_element` (`R9_MARKS`), and that case made wrong
(`R9_INJECT`) (`../../docs/pimos_roadmap.md` R9).
`ifs_sweep.py` and `ifs_rows.py` (OURS) are the IFS sweep
(`../../docs/ifs_apps.md`): every held IFS application for PIMOS, its
files served from the committed archives for its process only, its
documentation's lines typed from the prompt checkpoint, each row
classified by its first stop; `--run` needs the checkpoint, `--check`
(in the suite) does not: it checks the committed summary
`docs/ifs_sweep_results.json` against the pinned table, the printed
results against their archive files, and the runner's injections.
`mp1_rebuild.py` (OURS, not in the suite: it needs the prompt
checkpoint) is rung MP1(a) of `../../docs/other_pims.md` §4: PIMOS 3.6
files compiled by the held compiler from the prompt, served as home
files for this process only (`longrun_ipl.add_home_file`, so `ls`'s
pins are unchanged), each module compared with the held one; `run`,
`report` (pinned verdicts) and `inject`.
`lockstep_mklist.py` (in the suite) checks `mark_element` on a list
cell, Position 0 the car and 1 the cdr, on a code of the bench's.  168
instructions on both models (counted 2026-11-24: 168 `i_` handlers in
`pimm.py`, shoen stage 3's `stop_shoen`, `abort_shoen`, `raise`,
`current_processor`, `jump`, `set_marked_variable`, `wait_vector`, `multiply_bignum_word`, `subtract_bignum`, `get_constant`, `b_vector`, `code_to_predicate` and `add_shoen_resource` among them, then
`search_character`, `unbound`, `extended_floating_point`, `module`,
`add_extended`, `subtract_extended`, `multiply_extended`,
`divide_extended`, `allow_shoen_resource_report`, `bignum_less_than`
and `bignum_not_less_than` on the way to the prompt; 165 without our
three stubs `merge_in`, `unify_step` and `to_processor`).
`ref_scsi.py` runs the same IPL body on the reference alone
(`python3 ref/pimm/ref_scsi.py`, about a minute).  No
garbage collection, MRB bits kept and vectors updated in place on
them but nothing reclaimed
(`docs/pimm_semantics.md` "The MRB"), of the shoen no profile
instructions (refused: what they change is unsourced) and the
resource ones acknowledged with nothing counted, no
unification failure inside a shoen, no built-in exceptions.

**Several PEs (rung M1, 2026-11-26; `docs/multi_pe.md`).**
`pimm_pe.py` makes a `System` of N PEs, each a `Machine` of its own
(copied from one loaded machine), with `current_node`, `Goal@node(K)`
as a `%throw_goal` message, an unbound argument exported and the
importer's unification of it with an integer or atom sent home as
`%unify`; VPIM's logical packets, the console's message codes, a FIFO
per pair of PEs, delivery at a goal switch, the PEs in turn with a
quota. `python3 ref/pimm/m1_gc.py` (in the suite, about a minute) runs
PIMOS's own compiled `seqgc:go/0` and `gc:go/0` from
`pimm_shell360E.sav` on 1, 2 and 4 PEs under two quotas against what
their source fixes. `pimm.Machine.run` calls the same `goal_switch()`
the PEs call; one machine's traces are byte-identical to before.
Reference only: the core is one PE (rung M7).

Rung M2 (2026-11-26): reading across PEs. A goal waiting on an
external cell sends `%read`; the owner answers with `%answer_value` at
once or from a reply record hooked on its variable; the reader binds
its own variable and gives the import back with `%release`.
Structures go at level 0 (exported) and level 1 (the list cell or
vector, the elements at level 0); `current_processor`, `unbound/2` and
`get_heap_size` on the PEs. `python3 ref/pimm/m2_read.py` (in the
suite, after `m1_gc.py`) runs PIMOS's own compiled heap monitors
(`h_monitor`, `x_h_monitor` of `pimm_debugger360E.sav`) on 1, 2 and 4
PEs under two quotas, and bench cases on their `reverse` and `out`;
`M2_CACHE=PATH` keeps the loaded machine between runs.

Rung M3 (2026-11-26): the tables as the machine had them. MRB off is
white (a new entry, one `%unify` or `%release`), MRB on black (one
entry per address, WEC, 2^24 a send, given back by `%read`, `%unify`,
`%release` and coming home, reclaimed at 0); an imported ID is passed
on as VPIM does; a PE collects with live tables (`PECollector`: the
export table a root, the import table weak, a dead import released).
`python3 ref/pimm/m3_gc.py` (in the suite, after `m2_read.py`) runs
the heap monitors with collections at every quiescence and checks WEC
conservation, that every entry is named, and the bench drains. The
exported variable is retagged `EUNDF`/`EHOOK` while an entry holds it.

Rung M4 (2026-11-26): the shoen across PEs. A shoen's ID is a black
export entry of its record. A throw from it carries WTC (`wtctu`
0x400) and resource (`rsctu` 0x1000), and it cannot terminate while
any WTC is out. On the goal's PE a foster parent is made, which sends
`%ready` and is given `%supply_wtc`. It throws on, asks for WTC and
resource, forwards exceptions, answers statistics and ends with
`%terminated`. The shoen's start, stop and abort go to every live
foster parent. `python3 ref/pimm/m4_shoen.py` (in the suite, after
`m3_gc.py`) runs seven parts, each a shoen made by the image's own
`shoen:execute/4`, on 1, 2 and 4 PEs under two quotas. It checks
termination, statistics against the reductions counted on every PE,
the answers, WTC and resource accounting, and that nothing is left.
`M4_CACHE=PATH` keeps the loaded machine between runs. A code or
module word in the heap goes between PEs as its module's number and
offset. The loaded modules are roots of a PE's collector, and a
module made later (a compiled one) is fetched by the PE that needs it.

Rung M5 (2026-11-26): PIMOS boots on N PEs.

    M5_CACHE=PATH python3 ref/pimm/m5_boot.py LINK.pkl [--n N ...] [--quota Q ...] [--app sample9|qsort ...]

LINK.pkl is the checkpoint `longrun_ipl.py --reference --save` writes.
The runner collects it once with Loaded as a root (to 1,016,836 live
cells; the one-PE boot from it is unchanged, 8,595,408 instructions to
the prompt). It boots PIMOS on a System of N PEs, with the boot goal
and the FEP on PE 0. At the prompt it compiles and runs the primer's
`sample9` (placement order 0,1,2,3,0,1,2,3 on 4 PEs) or R8's qsort
with `@node`, and compares the console and window with the one-PE
run's. Its last line is `m5 boot: PASS (12 runs)`, after about 7
minutes. It is a long runner, not in the suite: docs/multi_pe.md 5, M5.

Rung M6 (2026-11-26): a period multi-node program.

    M5_CACHE=PATH M6_CACHE=DIR python3 ref/pimm/m6_mgtpn.py LINK.pkl [--run N,C,T ...] [--quota Q ...]

MGTP/N's model-distributed prover (IFS No. 91, `mgtpv0.kl1` and
`util.kl1`, served from the held tgz) is compiled at PIMOS's prompt on
N PEs and given the problem its `INSTALL.j` prints, with workers C..T.
Every run must answer `unsat`, as the print does for five workers on 6
PEs; Delta's shape, the placement and what is left are checked, and
Ncalc and reductions are pinned (they depend on the schedule). Its
last line is `m6 mgtpn: PASS (8 runs)`; a boot and compile is about 16
minutes, the queries from `M6_CACHE` about 12. `M6_INJECT=local|lifo|
nowake|oldwait` makes one fault. A long runner, not in the suite:
docs/multi_pe.md 5, M6.

    python3 ref/pimm/test_jtoa.py

runs module `jis_to_ascii` from the image against an oracle built from
its source and PIMOS's own ASCII-to-JIS table: `convert_element/2` for
every 16-bit key, and `convert/2` on strings, where it turns
full-width "PIMOS 3.6" into the 8-bit string `PIMOS 3.6`.

## Lockstep

With `m.tr = []` the model writes one line per event (instruction
taken, register write, memory write, end of reduction; the format is in
`docs/pimm_semantics.md`). `lockstep_jtoa.py` compares that trace with
the Bluespec core's, line for line. A test is one script of operations
(`driver.py`: make a variable, spawn a goal, run, bind, print) that the
Bluespec driver bench (`bsv/PimmDriverTb.bsv`) executes and the
reference model plays:

    bsv/run_pimm_lockstep.sh

The whole `jis_to_ascii` module is in lockstep: `lockstep_jtoa.py`
(`convert_element/2` on every key, and goals suspending and waking) and
`lockstep_conv.py` (`convert/2` on strings, with waiting built-ins).
`lockstep_get4.py`, `lockstep_ccode.py` and `lockstep_asf.py` run three
predicates of a second module, `scsi_common`; the second builds vectors
and atoms, the third calls the first.

Next: the next module with source (`builtin_utility`, `scsi_common`),
one instruction group at a time, the reference model no more than one
step ahead of the Bluespec; and a `.sav` loader. The reference model is
kept no more than one such step ahead of the Bluespec.
