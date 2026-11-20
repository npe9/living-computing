# Gap analysis: what is missing between today's model and PIMOS running applications

Written 2026-11-20 at the owner's request, after the IPL-image slices
through `shoen:ground_term/2`, the literature search
(`literature_gaps.md`), the firmware readings
(`pseudo_pimm_firmware.md`, `pseudo_pimm_microcode.md`) and the
database survey (`icot_databases.md`). The plan and its rungs R1-R9
are in `pimos_roadmap.md`; this note is the inventory of what still
has to exist, measured where it can be, and the order to close it in.
Numbers marked *measured* come from the tools named; everything else
is a reading of the sources and is labelled.

## 0. Where the model stands (measured)

Both models (reference `ref/pimm/pimm.py`, Bluespec `bsv/Pimm*.bsv`)
implement the same 54 instructions and agree line for line on seven
lockstep tests from four IPL modules.

| | names the models have | of names used | instructions covered |
|---|---|---|---|
| IPL image `pimm_ipl.kbn` | 54 | 143 | 11,196 of 13,156 (85.1%) |
| whole object set (20 `.sav`) | 54 | 197 | 75.9% of 726,053 |

- 54 of the IPL image's 349 predicates use only modelled
  instructions; 11 of them have been run in lockstep.
- The runtime under those instructions is this project's design, not
  the machine's (`pimm_semantics.md`, "Runtime state").

(Counted with `kbndis.Image().dis` over each predicate and
`asm/census.py`; the atom register families are counted once.)

## 1. The critical finding: boot needs the shoen at its first step

`ipl:boot/0`, the image's start, does this and little else
(`asm/kbndis.py`, cells 7809-7828): build a code object with
`predicate_to_code`, then `enqueue_goal_external shoen:execute/4`,
then `ipl_monitor/3` and `wait_finish/1`. `shoen:execute` reaches
`create_shoen`, `start_shoen`, `add_shoen_resource`. So rung R4 ("the
IPL image starts") cannot be reached by adding ordinary instructions:
it needs code objects, inter-module calls and a first shoen. Gaps
B2, B3 and C1 below are on the path to the very first console line.

## 2. Gaps, by layer

Each gap: what is missing, what it blocks, what there is to build it
from, and how it would be checked.

### A. Instructions with settled meaning (work, not research)

| | Missing (IPL uses) | Source to build from | Check |
|---|---|---|---|
| A1 | Lists and structure completion: `put_list` 179, `get_nil` 112, `collect_vector` 139, `collect_list` 89, `wait_nil` 59, `write_marked_value` 94, `write_integer` 62, `write_nil`, `write_marked_variable`, `set_integer`, `set_atom`, `set_nil`, `set_marked_*`, `read_atom`, `read_eagerly`, `wait_value`, `wait_list`, `wait_constant` | compiler source, PIMOS manual, the patterns already run | lockstep on a source-backed predicate, as now |
| A2 | Atoms: `wait_atom` 94, `put_atom` 49, `switch_on_non_atom` 30, `atom`/`integer` type guards 77 | same; encoding now doubly witnessed | same |
| A3 | Vector sizes 0, 1, 5, 6 and the general `put_vector`/`wait_vector`; long vectors (7 or more, with a `VDESC` descriptor): made, read and updated since `lockstep_deca.py` (2026-11-20), the size guards on them not run | `library/kbn/kbnheap.kl1` gives the layout | image constants as fixtures |
| A4 | Constants: `put_structured_constant` 132, `put_constant` 61, `switch_on_constant` 77 (*done 2026-11-20, `lockstep_rpos.py`*) | `klb_opr.kl1`, `kbn.kl1` | same |
| A5 | Arithmetic and comparison: `add`, `shift_right`, `shift_left`, `multiply`, `divide`, `modulo`, `exclusive_or`, `not_equal` and their body forms | manual; `asm/bltdir.py` directions | same; exceptions are B5 |
| A6 | Strings: `string_operation` 16, `change_element_size`, guard `string_element`, body `string`; string types other than 8 and 16 bit | manual; `kernel/builtin/string.kl1` | `builtin_utility` predicates with source |
| A7 | **Unification of two structures.** The models unify variables and atomic values only; vector-vector, list-list and string-string stop | standard; PDSS `unify.c` for order of binding | a lockstep scenario per shape |
| A8 | Inter-module: `execute_external` 76 (done 2026-11-20, `lockstep_ext.py`: through the called module's predicate entry table; the cache field not modelled), `enqueue_goal_external` 16 (open) | the entry format is decoded (`kbndis.Image.external`) | call across two IPL modules |

A1-A8 raise the IPL image's predicate coverage from 54 of 349 to most
of it. They are the bulk of the remaining instruction *count* and
carry no open question.

### B. Instructions and runtime where something is not known

| | Missing | What is not known | Where the answer may be |
|---|---|---|---|
| B1 | Object-set-only control: `save` 9,605 and `restore` 7,933 uses, `read_variable_without_deref` 20,625, `jump` 1,474, `diff` 791 | `save`/`restore` semantics (flagged since Phase 0); none occurs in the IPL image, so they gate R5 onward, not R4 | compiler source (`library/compiler`), microcode entries `3211`/`3215` once the datapath is read |
| B2 | Code and module objects: `predicate_to_code` 13, `code`, `module`, `module_element`, `new_module`, `new_instruction`, `new_atom`, `export_entry`, `apply`, `hash`, `merge` | the layout of a `COD`/`MOD` object and of a module built at run time. The IPL *is* a loader: it builds modules in memory with these | TM-662 (module format, agrees with our images), `ipl_module`'s object code, `library/kbn/kbn.kl1` |
| B3 | The shoen: `create_shoen`, `start_shoen`, `stop_shoen`, `abort_shoen`, `remove_shoen`, `add_shoen_resource`, `shoen_statistics`, `raise`, reports on the report stream, resource (reduction) accounting | record field order is now known for the Pseudo PIM/m console (24 and 14 fields); behaviour is in the PIMOS manual (`e-shoen.tex`) and TR-483; the exact report protocol the kernel expects is in `kernel/builtin/shoen.kl1` (source held) | manual + source; lockstep on `shoen:` predicates |
| B4 | Priorities and placement: `enqueue_goal_with_priority`, `enqueue_goal_to_processor`, `calculate_priority_from_current`/`_from_minimum`, `current_node`, `current_processor` | our ready queue is one LIFO list; the machine has a goal stack per priority (256-entry table in `PIMM.PARAM`). Priority encoding is not known | manual (priority pragmas), `PIMM.PARAM`, microcode at `4c5c` |
| B5 | Built-in exceptions. Every built-in error stops the model today (`Unimplemented('built-in exception ...')`) | how an exception becomes a report to the shoen (`exception(Info, Goal, NewGoal)`), and the info codes | `kernel/builtin/excpt_tbl.kl1` (source held, partly running already), manual |
| B6 | Suspension layout: ours is `HOOK` -> suspension record always | the machine's: `HOOK` vs `MHOOK`, record fields, merge on variable-variable binding | microcode at `1c08`, `1d3a`; blocked on the memory datapath fields (`pseudo_pimm_microcode.md` section 13) |
| B7 | Goal record layout | not in print, not in the console text | same microcode pass |
| B8 | MRB and reclamation; garbage collection. The heap only grows, in 1 M cells; `put_reused_structure`, `set_vector_element`, `set_string_element` always copy; `collect_*` and `mark_element` do nothing | whether PIMOS's boot fits in a no-GC heap of feasible size (not measured); the collector's algorithm for PIM/m (copying, per the papers) | measure heap use at R4/R5 first; then TR-469, `PIMM.PARAM` |
| B9 | Floats (59 names in the object set, 3 in the IPL image), bignum (9 names) | formats beyond the tag | manual; `kbnheap.kl1`; low priority, 0.1% of instructions |

*The IPL's file decoder has near-source (found 2026-11-20).*
`ipl_file_decoder` (41 predicates, the module that reads `.sav` files
at boot) is a variant of `library/unloader/decoder.kl1`: 27 predicates
match a source predicate by name and arity. It is not that file
compiled (`set_status/3`, `check_cdr/4` and the input protocol differ:
the image's decoder builds requests with unbound variables for a
reader to fill, where the source consumes a list of words). So its
oracle is the data: real `.sav` term streams decoded independently by
`asm/unlsav.py`. `lockstep_dec0.py` is the first step (one-word
integers); `lockstep_dect.py` the second: integers, lists and vectors,
with the test playing the reader (the decoder asks with `[W|Rest]` for
a word and `{V, Rest}` for 32 bits). `lockstep_deca.py` the third: atoms and proper
lists, the test also playing the atom table (`put(Id, Name, Atom)`,
`get(Id, Atom)`) and the reader's string request `{Buf, Out, Rest}`,
on terms cut from the real `pimm_kernel360E.sav`, strings included
(17 real terms; the guard `modulo` and a divide box; vectors of 7 or
more, the descriptor form, made by `new_vector` and filled by
`set_vector_element`). `lockstep_gca.py` the fourth:
`decode_module_info/6` on the module information and the whole GC
area of seven real modules, the largest (shoen, 30 elements) among
them; all 42 modules of the kernel file hold only kinds it handles.
`lockstep_modc.py` the fifth: `decode_index_table/9` and
`decode_code_area/8` on three real modules (shoen: 15 entries, 1259
code items, two tables), item by item against `asm/unlsav.py`. So
every part of a module after its two names now decodes on both
models. `lockstep_lmod.py` the sixth: `load_module/7` on four
whole real modules, first word to last (the general `put_vector`).
Since then (2026-11-20): calls between modules
(`lockstep_ext.py`), and the first part of the IPL's module builder
`ipl_module:load/4`, the predicate entry table (`lockstep_ptab.py`;
`tag_and_value` and `new_instruction` of B2 are done), and goals of
more than eleven arguments (`lockstep_pack.py`), and the whole of
`ipl_module:load/4`: five real modules become module objects
(`lockstep_newm.py`, `new_module`), each cell as the file and the
layout of the image's own modules say. What that does not show: that
code in a built module runs (both models fetch code from the image,
not from the heap), and modules over about 2700 file words do not fit
(every `set_vector_element` copies the vector). A built external-call
descriptor has five cells where the image's own have four.

Then whole files: `ipl_file_decoder:decode/8`, the predicate the
IPL's loader calls, on two real patch files from magic number to atom
table (`lockstep_file.py`, `lockstep_file3.py`); B4's minimum is in
(`calculate_priority_from_minimum` over a range of ours,
`enqueue_goal_with_priority` with the priority dropped). Still stood
in for by the test: the reader (`ipl_loader:read_unload_file/7`, the
sum check) and the atom table (`ipl_loader:decode_atom/3`), both real
IPL code that can replace the stand-ins. Left waiting: the file name
on the console (C1). Next: `ipl_loader:load_file/9` with the IPL's
own reader and atom table in place of the test's, which needs a
stand-in only for the file's bytes (C2); then console output (C1),
so that the name and a 5702h file's comment are displayed.

### C. The world outside the processor

| | Missing | Notes |
|---|---|---|
| C1 | Console: `display_console` 61, `put_console` 71, `read_console`, `get_console`, `halt` | the first observable of R4. Semantics of the argument (string? character?) to settle from `ipl`'s uses and the microcode entries |
| C2 | The front-end processor over SCSI: `scsi_command`, `scsi_init` and the five `scsi_fep_*` modules that speak to it (no source for those modules in `pimos.tar.Z`) | the IPL reads `pimos.ipl` and the `.sav` files *from the FEP*. We must emulate the FEP end: either at the `scsi_command` built-in (need the packet format, from `scsi_fep_module`'s object code and `pimfep.ptf`), or above it by answering the IPL's file requests. This is the largest piece of new design before R4 |
| C3 | Atom-number service: `supply_atom_number`, `new_atom`, `top:throw_atom_number_client` | atoms are numbered by a server at boot; `pimm_ipl.sym` gives the IPL's numbers |
| C4 | Timer, date, and the FEP services PIMOS opens after boot (window, file, string_io) | R5-R6. The PIMOS internal file system is not in the released source (`icot_databases.md` section 6) |
| C5 | A `.sav` loader for tests (owed for R2 as written) | `asm/unlsav.py` decodes; relocation and atom renumbering are what the IPL's own loader does, so B2 and C3 inform it |
| C6 | More than one processing element: export/import tables, messages, weighted reference counts | field names known from the console (`pseudo_pimm_firmware.md`); defer: configure one PE. Distributed Pool and multi-node Kappa-P need it |

*Correction from `icot_software_survey.md` (2026-11-20), spot-checked
here.* C2 is better specified than the row above says. The released
PIMOS source has the kernel's own FEP client, `src/bios/fep_module/`
(`scsi_fep.kl1` and nine more files), and
`src/macro/pimos/pimos/pimos.vmac` defines the FEP command numbers
(`fep#ipl => 400`, `fep#symbol => 500` among them; those two are used
nowhere else in the source, so they are probably the IPL's device
classes: inference). What has no source is the IPL-time side: the
image's `scsi_fep_*` and `ipl_scsi` modules. The survey reports the
packet layout from `scsi_fep.kl1`; not rechecked here.

*Second correction, from `binary_reverse_engineering.md` (2026-11-20).*
The IPL-time side of C2 is now read from the object code:
`asm/kl1decomp.py` decompiles all 349 predicates of the IPL image to
KL1 clauses (checked here on `check_cdr/4`, `set_status/3`,
`replace_position/3` and `boot/0` against hand readings). Sections 1.3
and 1.4 of that note give the boot sequence to the first front-end
request (`read_open` of `"pimos:pimos.ipl"` through SCSI SEND/RECEIVE
on unit 7, then `getb` until end of file, then each `.sav`) and the
packet format. `fep#ipl` and `fep#symbol` are NOT used by the IPL,
against the inference above. That note is the specification for the R4
front-end stand-in; its byte-level derivations are the agent's and
have not been executed.

Also from it: `asm/kbndis.py` names function-numbered opcodes by their
first table entry, so the image's 9 "`export_entry`" are
`tag_and_value` and its 8 "`floating_point_equal`" are other float
operations; B2's list above and the census inherit this. *Fixed in
`kbndis.py` the same day (the function number is the x field): it now
prints 9 `tag_and_value`, 4 `floating_point_not_less_than` and 4
`floating_point_to_integer`; `asm/census.py` still counts by opcode.* And the image's source-backed modules are older text than
the held source where datable, so a source oracle must keep asserting
the clauses it uses, as the tests do.

### D. The Bluespec side specifically

- It has kept pace one for one, so its gaps are A-C above plus:
- **Cycle accuracy has not started.** The published numbers are few
  (step counts for `append`, 60 ns cycle, the five pipeline stages);
  the microprogram, once readable, gives per-instruction step counts.
  No timing claim is made today.
- Every built-in exception and every unmodelled case is `E unimp`; a
  boot will need them to be real.
- Memory is one RAM with a request queue; no cache, no TLB, no
  address translation. `PIMM.PARAM`'s area map is not used.

### E. Verification debts (recorded where they arose, collected here)

- Not caught by any run: `calculate_priority_from_minimum`'s result
  register (and its value is read by nothing); a file whose atom table
  has names; a 5702h file's comment; `new_module`'s refusals; integer keys in a
  built `hash_on_constant` table; the guard `add`'s overflow; `wait_nil` and
  `read_atom` offered another atom; `set_integer` with a negative
  operand; `execute_external` to a predicate that is not
  first in its slot, and from a clause with guard state; `wait_value`
  on atoms; the general `put_vector`'s size above 255;
  `b_multiply` beyond N * 2 (a step short, the
  overflow); `put_atom` on a register other than 0; a
  long vector through `switch_on_non_vector`, and the vector box's
  range check;
  `put_constant` dropping the constant's tag;
  `modulo` with a zero divisor or a negative operand (not reached);
  `integer` on an unbound operand;
  `switch_on_constant` comparing an unbound key (not observable: every
  pair has the same else label); `execute` keeping the old alternative clause;
  `less_than` at equality; `vector_element` at index = size;
  `set_vector_element` copying an unbound element; either vector
  built-in waiting on an input; `write_variable`'s register read back
  through a list only.
- `kl1_encoding.md`'s open question whether `r_r_c16_i` is one word or
  two is answered by the run (`switch_on_non_vector` is two) and the
  doc should say so.
- PDSS: its own `test/` directory has never been run on our port; one
  bus error is unexplained.
- The agents' fault injections on `asm/mekbn.py` were not rerun here.
- `literature_gaps.md` and `icot_databases.md` citations are the
  agents'; only spot checks were made.

### F. Applications (after R6)

- R7, the PIMOS compiler from the images: needs B1 (`save`/`restore`
  dominate compiled library code), B8 (it will not fit a no-GC heap,
  expected, not measured), floats only if the program has them.
- Database candidates, in the survey's order: PIMOS pools (IPL has
  `ipl_pool`, 27 predicates, 4 runnable today); Distributed Pool (C6);
  Kappa-P on one node with front-end storage (C2-style shim, R7 first
  because it ships as source).

## 3. Order of work

The dependency chain to the first console line (R4), shortest first:

1. **A1, A2, A4, A7, A8** — finish the ordinary instruction set on
   source-backed predicates. No unknowns. Takes the 54 runnable
   predicates to most of the image.
2. **C1** — console output, so runs become observable as PIMOS's own
   messages.
3. **B2** — code and module objects, from TM-662 and `ipl_module`.
4. **B3 (minimum) + B4 (minimum)** — one shoen that can be created,
   started and report termination; priorities as a number carried but
   one queue. Enough for `ipl:boot/0` to proceed.
5. **C2 + C3** — the FEP emulation and atom numbers: the IPL can ask
   for `pimos.ipl` and load modules. **R4.**
6. **B5, B1, A3 long vectors, A5, A6, C4** — what the loaded kernel
   needs. **R5**, the boot log.
7. **B8** — measure heap use; add collection when a run needs it.
8. **R6-R8**, then F.

In parallel, not on the chain but changing its design:

- **The microcode's memory datapath** (B6, B7): one more pass, aimed
  at the one-cell allocator and `write_variable`, then `suspend` and
  the multiple-waiter code. If it lands, replace our suspension and
  goal-record design with the firmware's before step 4 builds a shoen
  on top of it; if it does not, realign to the Multi-PSI/V2 design as
  documented and label it.
- **The Bluespec rewrite** stays one slice behind the reference model
  at most; each step above lands on both.

## 4. What would change this list

- Finding the firmware's goal and suspension layouts (changes B6, B7,
  and how B3 and B4 are built).
- Finding source or a specification for the `scsi_fep_*` modules or
  the FEP side (shrinks C2).
- A measurement that boot fits in a no-GC heap (defers B8 past R5), or
  that it does not (moves B8 before R5).
