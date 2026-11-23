# Roadmap: from the KL1-B bench model to PIMOS running applications

Written 2026-11-19. This is the plan of record for "boot the original
PIMOS binaries on the model and run applications under it". It replaces
the five-step "Bluesim boot milestones" list that used to sit under
WP5.3 in `../plan.md`.

Every number below was measured on 2026-11-19 with the tools in
`../asm/`; the command is given where it is not obvious. Things not yet
measured are listed as unknowns, not estimated.

## 1. Where we are

**What survives.** `docs/nonlocal/pimosobj.tar.Z` holds the bootable
PIMOS 3.6 object set (file dates 1994-03-28): the IPL heap image
`pimm_ipl.kbn` (92,160 bytes) with its `.sym`/`.ldb` tables, eight
system module sets (`kernel`, `bios`, `library`, `macro`, `server`,
`shell`, `utility`, `debugger`), twelve patch sets, and the startup
files `pimos.ipl`, `pimos.conf`, `pimos.logins`, `pimos.groups`,
`*.com`. `pimos.tar.Z` holds the matching KL1 source (version string
`3.600` in `src/kernel/init/version.kl1`), including the whole
toolchain: compiler, assembler, loader, unloader. `pimosman.tar.Z` is
the manual.

**What the binaries are.** KL1-B abstract-machine code plus tagged
constants. `INSTALL` names the target as "PSI-II or PSI-UX", "Pseudo
PIM/M system or Pseudo Multi-PSI system": the files are copied to a
SIMPOS directory on a PSI and run by that machine's KL1 firmware.

**What executed KL1-B, and what survives of it.** On PIM/m and on the
PSI the KL1-B instructions were microcode. So were the goal scheduler
with priorities, suspension and resumption, garbage collection, the
shoen (task/resource/exception) mechanism, the built-in predicates,
external-module linkage, and the console and SCSI primitives. A search
on 2026-11-19 (`pimos_boot_requirements.md` §0.1) found three
survivors, now in `nonlocal/`:

- `psdpim.tar.Z`: the Pseudo PIM/m firmware itself, **binary only**,
  for a PSI-III under SIMPOS. No PSI emulator exists that we could
  find.
- `pdss.tar.Z`: **PDSS, a complete KL1-B interpreter in C** with the
  whole runtime, written by the same group to develop PIMOS. A sibling
  dialect: different save format and opcode numbering.
- `vpim.tar.Z`: the runtime of the other PIM models in PSL source,
  including the multi-PE parts.

So the runtime's behaviour can be read from source rather than
reconstructed from prose, but nothing runs our object set as it
stands. Mapping the PIM/m dialect onto PDSS's is now the main
uncertainty.

**Static census of the object set** (all 20 `.sav` files; details and
the per-opcode table in `pimos_boot_requirements.md`, reproduced by
`asm/census.py`):

| | |
|---|---|
| images that decode | 20 of 20, 502 modules (three failed until a decoder fix on 2026-11-19) |
| instruction words | 726,053 (corrected 2026-11-20: the first count left out 54,973 atom-form instructions) |
| predicates | 12,344 |
| unclassified words | 0 |
| distinct (tag, opcode) pairs used | 197, 13 of them quick forms commented out of the 1992 `inst_tab.kl1` (`put_vector_0..6`, `wait_vector_1..6`) |
| of those, with any arm in `PimKL1B.bsv` | 51 |

The 51 cover 73.4% of instruction words by static count, but that
figure flatters the model: several of the arms are stand-ins
(`try_me_else`, `fail`, `set_value`, `collect_value`, the no-op
`wait`), and the missing 146 are the ones that need a runtime. Most
used with no arm: `collect_vector` 26,833, `put_vector_2` 16,838,
`put_structured_constant` 11,628, `put_vector_3` 10,350, `save` 9,605,
`restore` 7,933, `wait_vector_2` 5,768, `write_marked_value` 5,082,
`collect_list` 4,219, `execute_external` 4,030, `put_reused_structure`
3,998, the other `*_marked_*` forms, `enqueue_goal_external` 2,096,
the vector and string built-ins, `display_console` 451.

**What `PimKL1B.bsv` is today.** A decode-and-semantics harness with
26 discriminating benches. It is not the base of a machine that can
hold PIMOS: 4,096-word code and heap memories, an 8-entry goal queue,
tag values of the model's own choosing, absolute labels where the
assembler emits relative ones, a backtracking choice-point stack
standing in for KL1's commit, no suspension, no priorities, no GC, and
one ~300-line `step()` method. The `.kbn` is a heap image carrying
the real tags, so the binaries will contradict these conventions on
contact. Adding opcodes one at a time to this module (the loop the
model has been in) is **off the critical path** from here.

## 2. Definition of done: a ladder of observable rungs

Each rung is a runnable check that goes into `run_tests.sh` (or a
longer `run_boot.sh` once runs exceed a few minutes).

| Rung | Observable | Oracle |
|---|---|---|
| R1 | Every word of all 20 `.sav` files and the `.kbn` decodes or is itemised | round-trip: re-encode with the transcribed `encoder.kl1` rules, byte-identical |
| R2 | One predicate from a real PIMOS module, loaded from its `.sav`, runs to completion with arguments we construct and returns the right answer | expected value computed independently (by hand for the first; by KLIC 2.002 for the rest) |
| R3 | The same, for a predicate that suspends and is resumed | same |
| R4 | The IPL image starts and loads the module list in `pimos.ipl` | the IPL's own "Link Modules" line on the console |
| R5 | Boot log | "Link Modules ..." then "PIMOS V 3.600 20-May-93": `pim:go/4` displays `"PIMOS "` and `pimos_version:console_title` (`pimos/src/bios/boot/bios.kl1` the `:- default` branch, `kernel/init/version.kl1`: "3.600", "20-May-93"). Corrected 2026-11-23: this row asked for the manual's sequence "PIMOS booting ... / V 3.600 ... / SCSI UNITS FOUND" (`e-sysman.tex`), which is a V3.0 Multi-PSI transcript; "booting" is in no held 3.6 object file, searched 2026-11-23 as 8-bit text and as two-byte JIS (controls: "pimos" is found as 8-bit text in the bios and server files, "Version" as JIS in three; "SCSI" is found as JIS, a phrase with spaces was not searched for), and the source has the SCSI line commented out (`bios/boot/scsi_man.kl1`). Which branch the binary was compiled from is to be seen when it runs |
| R6 | Login and a shell prompt; a shell command that only needs the kernel runs | the manual's transcript for that command (`e-shell.tex`) |
| R7 | An application already inside the images runs | first choice: the PIMOS compiler compiling a one-clause module, because its output can be compared with our own decode of the same module |
| R8 | A KL1 program from source: `fact.kl1`, `nrev.kl1`, `qsort.kl1`, `kkqueen.kl1` from `pkl1.tar.Z`, compiled by PIMOS's own compiler on the model, then run | results equal KLIC 2.002's on the same source |
| R9 | A period application (candidates in §6) | its published result |

R8 is "PIMOS running applications" in the plain sense and is the
target of this plan. R9 and everything in §7 are follow-ons.

## 3. Decisions for the owner

These change the shape of the work. The plan proceeds on the stated
default until overruled.

1. **A KL1-B machine is firmware-equivalent, not PIM/m hardware.**
   `plan.md`'s historical-accuracy rule says every module must trace to
   a PIM/m block diagram. The PIM/m processing element is a
   microprogrammed CISC (`PimPU`); the microcode that made it a KL1
   machine is lost. A Bluespec module that executes KL1-B directly is
   therefore a reconstruction of the *firmware's behaviour*, and must
   be labelled so everywhere. *Default: build it, as a separate,
   clearly labelled layer (`PimKL1B*`), and keep `PimPU` as the
   hardware-accurate element. Rewriting the runtime as microcode for
   `PimPU` is not planned unless the microcode is found.*
2. **One PE first.** The object set targets a pseudo-parallel single
   machine, and R1-R8 need only one. *Default: single PE; the mesh
   (already built: `PimMesh.bsv`) is joined in §7.*
3. **A software lockstep model as scaffold.** Finding out what the lost
   firmware did will take many boot attempts. A plain-software
   executable spec of the same machine (same state, same step
   boundaries), run in lockstep against the Bluesim model with a trace
   diff, makes each attempt seconds instead of minutes and gives the
   Bluespec an oracle. *Default: yes, in `pim/ref/`, labelled as
   scaffold; the Bluespec model stays the deliverable and every rung
   in §2 is claimed only on the Bluespec model. PDSS is the natural
   starting point for it.* *2026-11-20: PDSS builds and runs KL1 programs
   on the development machine (`ref/pdss/`, in `run_tests.sh`).* Bluesim steps/second
   is unmeasured; Phase 0 measures it and this decision is revisited
   with the number.
4. **How authentic the I/O is.** The real machine fetched files through
   a front-end processor (a PSI running SIMPOS) over SCSI; the patch
   set includes `fepsv`, `scsifep` and `tel`, and `pimos.conf` names a
   default FEP per task. *Default: a host-side FEP stand-in that speaks
   the documented protocol (`pimos/protocol/*.prt`, `src/server`,
   `src/vm/`) to the unmodified PIMOS, serving a directory of files;
   SIMPOS itself is out of scope.*

## 4. Phases

*`binary_reverse_engineering.md` (2026-11-20) answers what reverse
engineering the binary-only components takes: the IPL image decompiles
to KL1 (`asm/kl1decomp.py`), the `.sav` set matches the held (patched)
source by predicate set (`asm/savsrc.py`), the compiled ESP packages'
container is parsed (`asm/ptfdump.py`) with the KL0 opcodes unnamed,
and the firmware's own reverse assembler is held as compiled ESP.*

*`gap_analysis.md` (2026-11-20) is the measured inventory of what is
still missing against these phases, and the order to close it in. Its
main finding for this section: `ipl:boot/0` calls `shoen:execute/4`
at its first step, so R4 needs code objects, inter-module calls, a
minimal shoen and the front-end emulation, not only more
instructions.*

Order is by what boot executes, not by static frequency. Each phase
ends in a gate; do not start the next before the gate is observed.

### Phase 0 - Ground truth (no model changes)

1. **Firmware search.** *Done 2026-11-19: PDSS, VPIM and the psdpim
   binary found; Phase 2 takes the port branch, from PDSS. See
   `pimos_boot_requirements.md` §0.1.* Find anything that executes KL1-B: the PSI-UX
   pseudo-parallel system the PIMOS README says "is distributed as a
   part of the ICOT Free Software", PDSS, VPIM (the C runtime used for
   PIM/p, /c, /i), PSI microcode listings. Look in the IFS index via
   its mirror, the Museum TR/TM lists, bitsavers, and the KLIC
   distribution's own references. Fetch TR-373 and TM-1203 (already in
   the manifest's candidate list) and read them for the runtime's
   structure. **Outcome decides Phase 2's branch:** *port* a surviving
   runtime's semantics, or *reconstruct* from TR-246, TR-389, the
   manual's `e-builtin.tex`, the compiler (`instrtbl.kl1`, `mactbl.kl1`)
   and KLIC's runtime as a cross-check.
2. **Finish the decoder.** *Done 2026-11-19, see
   `pimos_boot_requirements.md`: the first suspect below was right,
   the second was not (those words are predicate heads).* Fix the three failing images. Classify the
   33 unknown opcode values: real 1994 additions (the commented-out
   `put_vector_2` family in `inst_tab.kl1` is the first suspect for
   `0x3a`-`0x3e`) or table/constant words misread as code (suspect for
   `0x02`-`0x07`, which sit where `switch_on_constant` and
   `hash_on_constant` tables would be).
3. **The `.kbn`.** *Done 2026-11-20 (`asm/kbn.py`,
   `pimos_boot_requirements.md` §0.3): load address `0xE0000000`, 20
   modules, every cell placed, the machine's data tags from
   `kbnheap.kl1`.* Base address, cell layout, entry point, and the real
   tag values, from `src/library/kbn/`, `pimm_ipl.sym`/`.ldb` and the
   bytes.
4. **Address units.** *Done 2026-11-20: one address is one cell;
   labels are `target - (here + 2)` in cells.* The assembler computes labels as
   `target - (here + 2)`; settle what unit that is in a loaded image
   (the open `savaddr.py` question).
5. **Runtime inventory.** *Done 2026-11-20 (`asm/inventory.py`): 245
   mnemonics once sub-functions are broken out; the IPL image alone
   uses 144, including shoen, priority and module-object instructions,
   so no boot stage runs on the bench model's level of machine.* From the census and the source: every
   built-in (`f_r_r`, `f_r_r_r`, `r4`-`r7` types), every instruction
   that touches goals, priorities, shoen, MRB marks, external modules,
   the console and SCSI. One table: name, count in the images, source
   of its semantics, status.
   *Name map against PDSS done 2026-11-20 (`asm/namemap.py`): 125 of
   197 have a one-to-one PDSS counterpart by name and register count;
   18, carrying 29% of uses, are PIM/m's implicit-position structure
   and constant instructions that PDSS splits per position or type;
   50 are absent. A PDSS port is a translation layer, not a
   renumbering.*
6. **What I/O boot needs.** *Instruction level done 2026-11-20: the
   IPL needs a console sink and `scsi_init`/`scsi_command`; the SCSI
   exchange itself is open until the IPL is disassembled (Phase 1).*
   Read `bios/boot/*.kl1`, `src/vm/*.kl1` and
   `pimos.conf` to list every device operation between power-on and the
   shell prompt.
7. **Measure Bluesim.** *Done 2026-11-20: about 14 million steps per
   second for the bench model; speed does not shape the plan.* Steps per second of the current model on an
   existing bench.

*Gate (R1):* all images decode with zero unexplained words;
`docs/pimos_boot_requirements.md` holds items 2-6 with counts.

### Phase 1 - The machine's foundation

Rebuild the KL1-B layer on the binaries' own conventions, in the
stage/box structure the repository asks of Bluespec processors:

- the real tagged word and tag values;
- relative labels and real address units;
- memory behind a request/response interface, sized for the images
  (the kernel set alone is 408 KB of 16-bit words);
- goal records, the prioritised ready queue, `enqueue_goal`/`execute`/
  `proceed`, replacing the 8-entry queue and the choice-point stand-in
  with KL1 commit semantics (`try_me_else`/`otherwise`/`suspend`);
- full dereference chains;
- a loader path: `.sav` -> linked memory image (atom table, predicate
  table, module references), produced on the host for now;
- fetch/decode, execute, and the multi-cycle units (unifier, structure
  builder, arithmetic) as separate modules; the software lockstep model
  alongside (decision 3).

The 26 existing benches are ported to the new conventions and stay
green; their injection records are re-observed, not copied.

*Gate (R2):* a real predicate from a PIMOS module runs and returns the
right answer. *Amended 2026-11-20:* first from the IPL image, which is
already linked (`jis_to_ascii:convert_element/2`, then
`convert_loop/4`, then `convert/2`; source `bios/boot/jtoa.kl1`), with
PDSS running the same source as the answer oracle; the `.sav` loader
follows. *2026-11-20: `convert_element/2` runs from the image on the
host reference model (`ref/pimm/`) and agrees with its source on all
65,536 keys. Not R2: R2 is claimed on the Bluespec model only. PDSS
cannot be the oracle for this predicate, because its `#"X"` is ASCII
where PIMOS's is 16-bit JIS; the oracle is the source text.*
*Later the same day: **R2's first step is met on Bluespec.** The new
core (`bsv/Pimm*.bsv`: memory, data box, hash box, fetch and execute
stages) runs `convert_element/2` from the image for every 16-bit key,
an atom and an unbound argument, and its trace is identical, line for
line (2,015,622 lines), to the reference model's, which agrees with the
source (`bsv/run_pimm_lockstep.sh`). Still owed for R2 proper:
`convert_loop/4` and `convert/2` on Bluespec, and a predicate loaded
from a `.sav`. Goal records, the ready queue and hooks are now memory
cells in both models, and suspension and wake-up are in lockstep.*
*Then: **the whole module runs on Bluespec.** `convert/2`, through
`convert_loop/4` and `convert_element/2`, from the image, turns 16-bit
strings into the 8-bit strings its source gives (full-width
"PIMOS 3.6" among them), in lockstep with the reference model
(`ref/pimm/lockstep_conv.py`). That is the amended R2 gate for the IPL
image; what R2 still owes is a predicate loaded from a `.sav`.*
*2026-11-23: **R2 is met as written.** `hasher:hash/3`
(`pimm_patch_hash360E.sav`; source `src/utility/pool/hash.kl1`) is
loaded by the IPL's own `load_file/9`, reader, checksum and atom
table, and then run from the module object in the heap on both
models (`ref/pimm/lockstep_run.py`); its answers for integers, an
atom, a string, a list and a vector are those the KL1 source gives
(for the atom and the string the source says `builtin:hash`, whose
function here is PDSS's, not known to be PIM/m's).
The test stands in for the file's buffers and starts the goal
itself: the IPL's linker (`ipl_link_table`) and a call between
loaded modules are not run yet.*
*The same day, towards R4: `ipl_loader:load/4` runs whole on both
models for a list of ONE file (`ref/pimm/lockstep_link.py`): the
console is given "IPL loading", the file's name and "Link Modules
...", and the IPL's linker answers `abnormal` with "Undefined Module
Found" and the module the file calls and does not hold. R4 itself
needs the list in `pimos.ipl`; a second file of 41,359 words was
tried on the reference model alone and needs 1.29 M cells (about 31
a file word, 0.9 M of them goal and suspension records never reused);
the unification of two vectors it also needs is in
(`lockstep_unif.py`), and so is the memory (2^27 cells): that file
loads and links on both models (`lockstep_link.py` part 2).
On the reference model alone, 2026-11-23, the twenty files of the
held `pimos.ipl`, in its order, load and link NORMALLY (73 M cells,
fifteen minutes); `predicate_to_code` then gives the code of
`pim:go/4` and the answer is `normal(Atoms, Modules, Comments, Code)`:
10,032 atoms, 480 modules; eight modules are in two files and each
ends as its later file's (`ref/pimm/longrun_ipl.py --reference`).
`top:go_pimos1/2` applies that code (`apply`, `lockstep_apply.py`).
The linker reports ONE
undefined module, the first it meets: a normal link needs every
module the files name.*

### Phase 2 - The runtime

The port branch: semantics from PDSS's C (VPIM for what PDSS lacks),
mapped by name onto the PIM/m table, with the PIMOS binaries deciding
wherever the dialects differ. In dependency order:

1. suspension and resumption (`wait`, `suspend`, hooking goals on
   variables, waking on bind) - *gate R3*;
2. structures: vectors, strings, structured constants, the
   `put_/write_/collect_` families and the MRB (`*_marked_*`) forms
   with reuse (`put_reused_structure`, `collect_*`);
3. the built-ins, in the order the boot trace hits them;
4. `save`/`restore`, `execute_external`/`enqueue_goal_external` and
   module linkage;
5. shoen, priorities and exceptions (the IPL starts PIMOS "at priority
   4050"); the shoen's first stage (`create_shoen`, `start_shoen`,
   termination) is on both models, `ref/pimm/lockstep_shoen.py`;
6. garbage collection - only when a run exhausts memory; until then
   size memory to avoid it and record that.

Each item gets directed benches with observed injections, and a
predicate-level test against real PIMOS code.

*Gate:* the kernel's initialisation predicate runs to its first device
request.

### Phase 3 - Boot

1. Console (`display_console`) to the testbench's stdout.
2. The loader path the IPL itself uses, in two tiers as before:
   (A) modules preloaded into memory, IPL entered after the fetch;
   (B) the IPL fetches them through the SCSI/FEP interface.
3. The FEP stand-in (decision 4): enough of the protocol for the boot
   file service.

*Gates:* R4, then R5.

### Phase 4 - A usable PIMOS

1. The rest of the FEP services: login, files, the window/terminal the
   shell wants (`pimos.logins`, `login.com`, `shell.com`).
2. Whatever the shell, the servers and the library hit next in the
   trace.
3. GC, if not already forced.

*Gates:* R6, then R7.

### Phase 5 - Applications

Compile and run the `pkl1` samples under PIMOS on the model; compare
with KLIC 2.002. *Gate:* R8. Then one period application (R9).

## 5. Named unknowns

*Literature search, 2026-11-20 (`literature_gaps.md`): what is in print
and on the ICOT mirrors for each unknown below, for PIM/m and the other
PIMs, with a table of where our invented runtime layouts disagree with
the documented siblings. Two leads change the plan's options: the
64-bit microinstruction field layout is published (TR-733 fig. 4), so
the Pseudo PIM/m firmware we hold (`pimm.MEkbn`) may be readable, and
with it the machine's real goal-record, suspension and GC layouts;
and `psdpim`'s `PIMM.PARAM` and `boot.init` give the firmware's memory
map and the boot sequence (clear, init, impl, patch, ipl, start).
Neither binary has been decoded.*

*Same day, first reading (`pseudo_pimm_firmware.md`,
`asm/psdpim.py --check`): the firmware file's head is the decode
table, one entry per opcode, agreeing with `kl1_encoding.md` in both
directions; `wait_different_value` and `scsi_transfer` are not in the
firmware; the console text gives the field order of the shoen record
(24), the foster-parent record (14), and the import/export entries (the multiple
suspension record's menu offers `prev`, `next`, `goal`, `rival`, not
established as fields). `scsi_transfer`, used once in the object set,
is the only instruction PIMOS uses that this firmware lacks. A second
pass (`pseudo_pimm_microcode.md`, `asm/mekbn.py --check`) found where
each microinstruction is and which decode-entry bits are its address,
so the goal, suspension and scheduling routines can now be located;
none has been read.*

*A third pass, same day (`pseudo_pimm_microcode.md` sections 7-13):
the branch kinds (jump, call, return, end of instruction, short
relative) and two register-select fields are verified, and `suspend`
is seen to allocate first through a `HOOK`-stamping allocator and the
multiple-waiter code from a 4-cell allocator with `HOOK`, `DREF` and
`MHOOK` stamps. The record layouts were NOT recovered: the memory
datapath fields (where a read or write takes its address and data)
are not worked out, and that is the next step.*

*A fourth pass, 2026-11-20 (`pseudo_pimm_microcode.md` sections
14-20): the memory datapath is settled (read strobe, write strobe,
address step, the work registers, write timing), verified on held-out
code in both images. The multiple-suspension record's four fields and
their tags are read: `{DREF, variable}`, a next-waiter link, `{HOOK,
goal record}`, `{MHOOK, next record of the same goal}`; their cell
order (prev, next, goal, rival, as the console menu has it) depends on
one addressing rule that is supported but not verified. The goal
record is only partly read (16 cells is an inference; arity, priority
and the goal stack entry table not recovered). Next: verify that
addressing rule on a layout known from elsewhere.*

| Unknown | Resolved in |
|---|---|
| Does any KL1-B firmware or emulator survive? | resolved: PDSS (C source, sibling dialect), VPIM (PSL source), psdpim (the real firmware, binary) |
| How far the PIM/m dialect differs from PDSS's, instruction by instruction | by name: done (`asm/namemap.py`); by operand order and behaviour: Phase 1, from the eight IPL modules that have source |
| `.kbn` base address, layout, entry | resolved (Phase 0.3): in the file's header; `asm/kbn.py` |
| The machine's tag values, including unbound, reference and hook | resolved: `debugger/inspector/tagtbl.kl1` names 59 tags; the meaning of the low `o`/`x` bit is inferred (MRB) |
| The 33 opcode values absent from the 1992 table | resolved: 13 real quick forms; the rest were predicate-head and float words |
| Label address units | resolved (Phase 0.4): cells; `target - (here + 2)` |
| Why `library`, `macro`, `patch_macro` do not parse | resolved: tagged float constants in the GC area |
| The built-ins' exact behaviour where the manual is silent | Phase 2, by trace against PIMOS's own use of them |
| Bluesim throughput, and so the wall-clock cost of a boot | measured (Phase 0.7): about 14 million steps/s for the bench model |
| How much of the FEP protocol the boot and shell need | Phase 0.6 |
| Whether the IPL image expects state left by the PSI's own loader | Phase 3 |

## 6. Acquisition list

- KL1-B firmware or emulators: acquired 2026-11-19 (`pdss`, `vpim`,
  `psdpim`). Still wanted: any PSI-III emulator or microcode listing.
- TR-373 "KL1 no jitsugen houshiki to heiretsu OS no kijutsu" and
  TM-1203 "KL1 ni yoru PIMOS no jitsugen ni tsuite" (URLs in
  `nonlocal/MANIFEST.md` §3).
- `pimosman.ps.Z` (the typeset manual; we hold only the LaTeX).
  *`icot_software_survey.md` (2026-11-20) found it on the AIST mirror,
  with the PIMOS 1.5 and 3.0 manuals, the primer and the ESP manuals;
  that survey is the full inventory of ICOT software held, public and
  lost, and its section 5 is the acquisition list. Not fetched yet.*
- Multi-PSI KL1 implementation reports (the distributed
  implementation, export/import tables, weighted reference counts) for
  §7.
- Database software as an R9 candidate: `icot_databases.md` (a survey,
  2026-11-20) covers how ICOT did databases and what survives. The
  nearest candidates, in its order of feasibility: PIMOS pools (already
  in PIMOS), Distributed Pool (IFS, 10,947 lines of KL1, needs several
  nodes and no I/O), then Kappa-P (IFS, 151,683 lines of KL1) on one
  node with pages kept by the front end, which needs a host shim for an
  8-operation page-file protocol and the PIMOS KL1 compiler, since it
  ships as source for PIMOS 3.4/3.45. Not fetched; nothing tried.
- Period KL1 applications for R9: the benchmarks the FGCS'92 PIM/m
  paper reports, and the IFS KL1 programs (theorem provers, puzzle
  and search benchmarks) once the IFS index is reachable.

## 7. After R8

- Multiple PEs: goal distribution (`@node` pragmas), inter-PE messages
  over the existing mesh, distributed unification and the export
  tables. Needs its own firmware evidence.
- Timing: only where a published figure exists (`plan.md` evidence
  gate 4).
- FPGA: memory budget for the images on the ULX3S, and the SD card as
  the block device.

## 8. What stops now

The one-opcode-per-commit loop on the current `PimKL1B.bsv`. Its
benches stay in the suite; no further instructions are added to that
module except to support a Phase 0 measurement.
