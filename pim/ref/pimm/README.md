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
first stage: `create_shoen`, `start_shoen`, termination (shoen records
in the heap, a goal's shoen in its record's status cell;
`docs/pimm_semantics.md` "Shoen").
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
`shoen:execute/4`), `lockstep_alt.py` `read_eagerly`
(`alternatively`), `not_equal` and `wait_vector_1`, `_4`, `_6`,
`lockstep_body.py` `b_divide`, `b_modulo`, `b_string` and
`enqueue_goal_to_processor`, `lockstep_elw.py` `string_operation`
waiting on an element of its vector, `lockstep_reuse.py`
`put_reused_structure` of a vector of seven or more;
`longrun_ipl.py` is the long run (not in the suite); 128
instructions on both models.  On the reference model ALONE, a
prototype: the SCSI built-ins `scsi_init` and `scsi_command` against
a small model of the front-end processor (`fep.py`), with
a merger input bound to a vector
(refused unless `Machine.ahead` is set; the core cannot yet make its
goals as the reference does, see `pimm.py`'s header); `ref_scsi.py` runs the body of `ipl:boot0` on
them, the IPL reading its list and its files through its own SCSI
stack (`python3 ref/pimm/ref_scsi.py`, about a minute).  No
garbage collection, MRB bits kept and vectors updated in place on
them but nothing reclaimed
(`docs/pimm_semantics.md` "The MRB"), of the shoen only its first
stage (no stop, abort, remove, statistics, resource), no exceptions.

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
