# Recreating SIMPOS: what is needed, exactly (2026-11-23)

The owner asked: "Use the source listings from simpos to figure out
exactly what we need to recreate simpos." SIMPOS, the operating system
of ICOT's PSI machines, is lost as software (`../psi_acquisition.md`
§1, §9, §10). This page states what a reconstruction must provide,
measured from three kinds of evidence:

1. **What SIMPOS was**: every SIMPOS listing printed in the held ICOT
   reports, transcribed from the page images (`printed/`).
2. **What the surviving software needs from it**: every class, method,
   built-in and pathname that the 15 surviving ESP programs and the
   held compiled packages use and do not define (`required/`).
3. **What lies under it**: the ESP language, KL0, the formats of the
   held files, and the routes to running anything (`layers/`).

Three delegated agents made these. Their working files are kept as
they wrote them, and their scripts are in `../../asm/simpos_census/`
and `../../asm/simpos_layers/`. The central claim, cil's Librarian
class, was checked by opening the file. Everything else is as the
agents report it: each file gives its own method and limits.

## 1. The target, in one number

**A SIMPOS that runs every surviving ESP program provides 3,470
distinct requirements** (`required/subset_cover.tsv`). These are
classes, methods with arity and kind (class or instance), inherited
slots, built-ins, and system objects reached by pathname. There are
also 36 classes that only the compiled packages name, mostly the
supervisor and the network. The smallest program, `txtstrct`, needs
**138** of them. The order below adds one program at a time, each
step exactly satisfying the programs added so far:

    txtstrct 138 -> chal 245 -> utter 403 -> knov 580 -> disc 741 ->
    icotext 917 -> papyrus 1,100 -> sum 1,324 -> fuzclust 1,538 ->
    gog-esp 1,784 -> euod 2,017 -> cal-esp 2,314 -> kwic-esp 2,593 ->
    cil 2,941 -> kappa2 3,470

That is also the build and test order. Each program is the acceptance
test for its step, run against the reconstruction and compared with
what the program's own documents say it does.

The requirements in detail:

- **367 system classes** (`required/classes.tsv`), each with its
  evidence: 210 named `simpos##C` in a compiled package (certain); 9
  named in SIMPOS reports; 5 in the ESP manual; 9 used by two or more
  programs; **115 used by one program only and not confirmed**, which
  may be application classes missing from their archives; 3 provided
  by held packages (not SIMPOS); 4 defined in another IFS application.
- **1,436 methods on named classes and 706 on inherited natures**
  (`required/requirements.tsv`), with call counts, programs and an
  example call site. 760 more selectors have a receiver the scan could
  not type; they are listed with candidate classes.
- **93 inherited slots.**
- **353 built-in predicates** (`required/builtins.tsv`). 176 of them
  have name and arity confirmed by cil's `class builtin` in package
  `kl0` (`cil/src/cil_kl0.esp:74`), which wraps every KL0 built-in.
  That is the best built-in list held. Also 64 `a#b` constants such as
  `key#cr` and `mouse#l`.
- **1,254 pathnames** (`required/pathnames.tsv`): 318 absolute (e.g.
  `>sys>font>kanji_16.font`) and 936 logical names.
- **The Librarian's vocabulary** (`required/librarian.tsv`,
  `command_files.tsv`): `fxds/1`, `command/1`, `make_environment/2`,
  `save_environment/1`, `make_package/2`, `save_package/1`,
  `use_package/1`, `save_all_classes/0`, `load/1`, `refute/1`. The
  login files add `menu/0`, `define/0`, `package/0`,
  `shell_transient/0`.

The most used classes, with class and instance methods: `symbolizer`
27/0, `standard_io_window` 1/56, `library` 46/0, `as_program` 8/27
plus 14 slots, `pmacs_window` 7/33, `essential_window` 1/32,
`library_utility` 6/20, `list` 2/20, `standard_io_buffer` 2/21,
`standard_editor` 1/20, `standard_superior_window` 4/19,
`standard_menu` 1/19, `directory` 16/0, `process` 5/5. The other 16
of the top 30 are in `required/NOTES.md`.

**Arity convention.** `required/` counts the receiver, as the ESP
manual writes methods (`:create(#list,X)` is `create/2`;
`program-e.tex:4912`). It was checked against the compiled packages:
6,681 of 6,681 methods match in name and arity. `printed/classes.tsv`
counts arguments **without** the receiver, as the reports print them.
Add one to compare.

## 2. What is printed (the parts we can reimplement from the source)

From `printed/STRUCTURE.md`: 102 transcriptions in `printed/listings/`
from 23 reports, read by eye at 250-300 dpi: 75 ESP files (1,166 code
lines, comments and blanks not counted) and 27 figure or table
transcriptions. The reports themselves warn that the code is
partial (TM-100 p7: "they are not complete").

| Area | What is printed | Source |
|---|---|---|
| Process and stream core | source, nearly complete except dispatch | TM-100 |
| Pools, semaphores, events, permanent objects | interfaces and key bodies | TR-056, TR-059 |
| Distributed file classes | source, with the remote-call dispatch | TR-524 App. A |
| ROAM, remote object access | wire tags; semantics complete | TR-283 |
| Windows | mixin source for 4 classes, about 45 method signatures; the rest names | TM-065, TM-125 |
| Coordinator | translation table and system menu source | TR-046, TR-061 |
| TCP/IP, TELNET, FTP | prose: prototyped as SIMPOS extensions on a socket interface giving TCP/IP functions as methods, 32 sockets per user; no class or method names | TM-430 p3 |
| GC, boot, IPL, librarian formats, scheduler, device handlers, disk format | prose only, or absent | |

By class: 255 distinct classes (`printed/classes.tsv`, 456 rows of class
and report; `-` folded to `_`, example-only names excluded), by best
tier **28 PRINTED-SOURCE** (body printed), 30 PRINTED-INTERFACE, 140
PROSE, 57 NAMED. The 28: process, interrupt_process, as_program,
stream, channel, port, bounded_channel, bounded_post_queue, semaphore,
event, tap, buffer; file, file_accessor, binary_file,
binary_file_accessor, logical_file, local_ and remote_binary_file,
local_logical_file, as_permanent_object, as_bucket; bare_window,
with_border, with_label, window_with_border_and_label, system_menu,
default_translation_table. Variants are recorded, not resolved
(semaphore's methods in TM-100 against TR-056; `:invoke` class or
instance in TM-100; `listings/VARIANTS_tm0061_vs_tm0065.txt`).
`printed/NAMED_NOT_DEFINED.md` lists everything the reports name and
never define.

**SIMPOS-level source found in an application**: cil
(`natural-lang/simpos/cil.tar.gz`) carries
- `class library_utility`, stamped `mkpsi000::>sys>user>yasuko>UT.esp.2,
  29-Jul-88` (`src/ds_bep.esp:3123`, opened). Its natures are
  `librarian_version`, `librarian_class_generator`, `librarian_delete`,
  `librarian_package`, `librarian_spy`, `librarian_reference`,
  `librarian_fdd`, `librarian_subroutine` and `as_assert_utility`, and
  it has 35 methods. It looks like a modified copy of the Librarian's
  top class.
- `coordinator` (`ms_cdn.esp:43`, "invoked from system menu").
- `class builtin` of package `kl0` (above).

## 3. What lies under SIMPOS (`layers/`)

- **ESP** (`layers/ESP.md`): specified precisely enough to write a
  compiler. The grammar is TM-388 App. A, the late dialect normative,
  TR-044's differences tabled. Covered: inheritance linearisation
  with worked examples, demon combination, slots, macros, the
  operator table and packages. Open conflicts are recorded, not
  resolved: the order of after-demons (TR-044 and TM-388 versus the
  thesis), three operator priorities (settled by TM-388's page image,
  PDF p.154), and the `=<`/`>=` mappings as printed.
- **KL0** (`layers/KL0.md`): the 40-bit word, the instruction format,
  the WAM-style groups plus the PSI's own, frames, choice points,
  exceptions, and the object descriptor's hash. 49 tag names
  (`pimmcsp##kl0_tag`) are MEASURED; their numbers are INFERENCE, 6 of
  49 confirmed. MISSING: opcode-to-mnemonic for all but about 10, the
  built-ins' opcodes, and the KL0 manual (MP7002-1, at the JAIST
  library only).
- **Formats** (`layers/FORMATS.md`): a `.ptf` is a package of **class
  templates**, not a memory image. The Librarian builds the class
  objects from it at load time (linearisation, method combination,
  hash tables). The predicate-header kind byte is decoded (class or
  instance primary, demons, slot initialisation, local, `$or$N`);
  `syspsi`'s header is measured (stamp `50.17 11-06'92`); text files
  are 16-bit JIS. The disk format exists in prose only (TR-524).
- **The microcode**: the PSI-III microword is now printed and tested
  on the held store (`../psi_acquisition.md` §11, `../psi_microword.md`).

**Dependency of what we hold.** The held compiled packages name 143
distinct `simpos##` classes. Of their 554 classes, only **102** need
no SIMPOS class when references are followed through other held
classes. That is a lower bound, read from the trailers only.
*Rechecked 2026-11-23 by the loader (`../../psi/README.md`):*

- *Following natures and the trailer's referenced-classes vector, the
  count is **104**.*
- *Following natures alone, it is **338**.*
- *The probe behind 102 is not deterministic: it gave 102 or 103 on
  reruns. It also counted one slot name as a class.*

## 4. What is lost and must be written (the reconstruction's own parts)

Labelled OURS whenever built:
1. **The Librarian's loader**: templates to class objects. It is
   needed by every route. The after-demon order is a switch until a
   source settles it. cil's `library_utility` shows its interface, not
   its loader.
2. **The supervisor's dispatch, scheduler and memory manager**: TM-100
   prints the process core but not dispatch; GC is firmware.
3. **The window system's bodies** beyond four mixins; the font and
   screen machinery.
4. **The file system's on-disk format** (prose only) and the device
   handlers.
5. **The network's TCP/IP socket classes, TELNET and FTP** (TM-430:
   prose, no names) and the PSI-NET layers; the IPSJ TELNET/FTP papers
   (`nonlocal/lit/ipsj/`) are not yet read.
6. **The boot**: `boot_process` is described; the IPL is "written in
   ESP" and loaded from floppies; no byte layout is held.
7. **KL0's opcode table**: it is to be named from known plaintext
   (`.ptf` against source, e.g. kappa's 696 classes with source) and
   from `sysidat`, the decode table (`../psi_microword.md`).

## 5. The route (from `layers/OPTIONS.md`, adopted)

No route has SIMPOS itself, so every route needs the loader of §4.1
and stand-in `simpos##` classes. In order:

1. **The loader first**, with the after-demon order as a switch.
   *Status 2026-11-23: built, OURS, in `../../psi/` (`librarian.py`,
   tested in `run_tests.sh`).* All 1,455 held classes, from eleven
   packages, load and build. That covers trailers, natures, the TM-388
   linearisation, method combination, slots and the Fig. A-1 tables.
   Against the held ESP source, nature lists agree in 917 of 917
   classes and slots in 3,673 of 3,674. Every method and local
   disagreement is attributed to a macro bank, an unparsed source item
   or the 3200/3500 version skew (`../../psi/README.md`).
2. **A KL0 interpreter** running compiled `.ptf` code. Start on the
   102 (now 104) classes that need no SIMPOS. Verify on
   `fep_command_code_table:convert/3` against PIMOS's command-code
   names, then on the paragraph classes against their source. Name
   each opcode only from a known-plaintext witness.
   *Status 2026-11-24: started, OURS, `../../psi/kl0.py` (tested in
   `run_tests.sh` by `test_kl0.py`).* Witnesses name 96 opcodes
   (`../../psi/kl0_opcodes.tsv`); any other opcode is refused.
   - `convert/3` agrees with `pimos.vmac` on 96 names. 4 names are
     only in the FEP table and 8 only in PIMOS; none disagrees.
   - Two paragraph classes (`predicate_num_switch_icon`,
     `list_index_buffer`) give the answers their source predicts.
   - Of the 530 methods of the 104 classes, 303 run to a solution, 11
     fail cleanly and 216 are refused. The causes are ranked in
     `../../psi/README.md`. 52 of the refusals come from 13 opcodes
     not yet named.
   Cell numbering inside `.ptf` code was settled for this step: a hash
   table spans mask+1+2*keys+2 cells.
3. **An ESP compiler** producing KL0, checked structurally against
   `paragraph.ptf`. Use it to write the stand-in `simpos##` classes,
   in the order of §1 and in reference-count order (`symbolizer`,
   `string`, `process`, `font`, ...), labelled as scaffolding, with
   the printed source of §2 used verbatim wherever it exists.
   *Status 2026-11-24: started, OURS, `../../psi/espc.py` (tested in
   `run_tests.sh` by `test_espc.py`).* It emits only opcodes with a
   row in `kl0_opcodes.tsv` and refuses any other construct by name.
   - Structure, against the held `.ptf` (`espc.py check`). Paragraph:
     all 109 classes with source compile. Natures and demon sets agree
     in 109 of 109, slots and the method sets in 108. The two misses
     are the 3200/3500 version slot and two unparsed items of
     `h_grade`. Of 1,051 predicates compared, 247 are cell for cell
     identical (991 and 243 before the string built-ins, step 3b).
     That is 23.5% of the compared predicates and 11.6% of all 2,123
     held predicates of those classes. Kappa2: all 739
     classes compile now that macro banks are expanded (`with_macro`,
     TM-388 §3.7.3; before, 404 were refused whole); 9,971 predicates
     compared, 1,323 exact (13.3%), and 10,641 and 1,361 with the
     string built-ins. 109 of the exact ones have source clauses a
     bank rule changed: the structural witness of the expansion.
     Utter compares 521, 101 exact (19.4%); 10 of its
     classes use banks whose source is not held. The
     differences are classified in `../../psi/README.md`. The largest
     classes are held code using opcodes not in the table (212 in
     paragraph) and differences of moves and environment only (189).
   - Behaviour (`espc.py behave`). The compiled paragraph classes run
     alone in a library, so every class a call reaches was compiled
     here. They give the same answers as `paragraph.ptf` to every call
     `test_kl0.py` makes. The exception is `paragraph_version`, which
     gives the source's "3200". Over kl0's census of `paragraph.ptf`,
     88 methods have the same outcome, and none has a different
     outcome.
   - Stand-ins, in `../../psi/standin/` and labelled scaffolding.
     The owner allowed interpolating SIMPOS (2026-11-24). Each method
     is labelled PRINTED (verbatim) or INTERPOLATED (with its sources:
     the interface, the call sites, the manuals). The stand-ins are:
     `process` (ours; its `self/2` is called by the printed
     `stream`, but its body is not printed) and `stream` (TM-100
     Fig. 3.6 printed source, with three marked corrections to the
     print). They were chosen by what pimfep's methods reach first,
     not by reference count. Called with unbound arguments, the
     pimfep methods refuse at `process:self/2` (46 methods),
     `stream:create/2` (15) and `process:create/3` (14). None of them
     reaches `symbolizer` or `string` first, although their code sends
     `string:append/3` 24 times and `symbolizer:get_number/3` 10 times.
     `pimfep##pimos_timer:on_after/4` used to refuse at
     `simpos##process:self/2`. It now refuses at
     `simpos##process:tag_catch/9`.
   - *2026-11-24, later:* kl0's `new/2` runs slots initialised by
     code. The calling convention is measured: all 424 held
     initialisers have arity 1, with the value in A0. The semantics
     are TM-388 §3.5 pp.49-50. `process` now carries the printed
     TM-100 Fig. 3.1 body. The classes that body and `stream` create
     or inherit are interpolated stand-ins: `list`, `post_queue`,
     `waiting_queue`, `process_clock`, `with_link` and
     `waiting_frame`.
     - `pimos_timer:stream/2` now succeeds, and the printed
       `put/2`/`get/2` run first in, first out.
     - Over pimfep and pimscsi (`kl0.py census --fep`), 195 methods
       stopped at `new/2`. Now none do: 14 more succeed, 112 reach a
       SIMPOS call and 69 reach an unnamed opcode.
     - The next blocking classes are `channel:create/2` (69 methods),
       `hash_index:create/3` (58), `list_index:create/2` (20) and
       `process:create/3` (14). See `../../psi/README.md`.
   - *2026-11-24, step 3b:* the compiler expands `with_macro` macro
     banks (TM-388 §3.7.3; above). Four string built-ins have
     known-plaintext rows (blt 0b, 1c, 23, 2b), and class `class`'s
     `:refute` (TM-388 p.46) is modelled. New interpolated stand-ins:
     `string` (`append/3`, `copy/3`) and `process`'s `tag_catch/5`,
     `/6`, `/9`, which call through `:refute` (TR-285 §4.2: catch is
     a multiple-level cut; no throw is modelled), and a partial
     `symbolizer` (`string_to_list/3`, `list_to_string/3`). Its other
     25 selectors are not stood in: no witnessed built-in converts
     atoms and strings, and number conversion needs `X/Y`.
     - `pimos_timer:on_after/4` now gets through `tag_catch/9` into
       its own `do_on_after/3` and stops at
       `process:allow_forced_event/1`.
     - Census of pimfep and pimscsi: 515 of 1,228 methods succeed (501
       before), 51 fail cleanly, 662 refuse; none changed between
       success and failure. The next blockers: `channel:create/2` (114
       methods), `hash_index:create/3` (58), `list_index:create/2`
       (20), `process:create/3` (14),
       `process:allow_forced_event/1` (9).
   - *2026-11-24, step 3c:* stand-ins for those blockers. PRINTED,
     verbatim: `channel` (TM-100 Fig. 3.7), `bounded_channel` and
     `bounded_post_queue` (Figs. 3.10, 3.11; their demons run).
     INTERPOLATED: `post_queue_for_message`, `semaphore`, `list_index`
     and `hash_index` (on the entry layout that kappa2's
     `KPPOOL.ESP` and `SVHSH_IDX.ESP` read from the base classes),
     `process:create/3`, `allow_forced_event/1` and slot accessors, and
     a minimal `standard_editor` (`get_window/2`, the unloaded ancestor
     of `pimfep##pimos_window_editor`). An espc argument-placement bug
     found on the way is fixed (no `check` count moved).
     - Census of pimfep and pimscsi: 605 of 1,229 methods succeed (515
       before), 63 fail cleanly (12 on an empty index or queue), 561
       refuse; none changed between success and failure.
     - The next blockers: missing opcodes (blt 06 65 methods, pmi b0
       29, pmi b4 21, ...); the `lock/1` of four pimfep tables, in a
       `simpos##` ancestor; `trace:trace/1`,
       `common_network:is_installed/1`,
       `network_listener_buffer:create/4` (5 each); and class
       `pmacs_window`, without which `pimos_window_editor`'s window is 0.
   - *2026-11-24, step 3c, second part:* nine opcode rows from known
     plaintext:
     - `add` (blt 40);
     - `integer`, `unbound`, `bound` (blt 01, 10, 16);
     - `stack_vector` (blt 06);
     - `equal_string` (blt 68), `string_tail` (blt 33);
     - `substring` (blt 32) and `search_character` (blt 5c), two cells
       long.

     Three HELD-SOURCE classes: morphana's `_simpos/` `name`,
     `e_string` and `pathname`, SIMPOS's own as copied for Common ESP
     (ICOT Free Software). In `pathname`, the port's `/` is restored to
     `>`, and its commented-out clauses are restored, each marked. The
     symbolizer's `get_number/3` and `get_number_string/3` work on
     integers.
     - Census: 607 succeed, 101 fail (38 more, the census's unbound
       arguments failing a type test), 521 refuse.
     - pmi b0 has no witness. (Corrected at step 3d: it has, below.)
     - The next blockers: blt 6e (38, in `fep_message_assembler`, no
       source), pmi b0 29, pmi b4 21, the SIMPOS calls above, and
       `alarm_watch:create/2`.
   - *2026-11-24, step 3d, opcodes:* all three blockers have witnesses
     in kappa2, paragraph and utter (`../../psi/README.md` "Step 3d").
     - `vector_to_list` (blt 6e; only the tail `[]` runs),
       `set_subvector` (blt 34, two cells), `{}` (pmi b0) and a
       four-element vector (pmi b4);
     - add_immediate, subtract_immediate and put_variable_t with the
       result in a second register.
     - espc puts `{}` and four-element vectors; `check` gains 31 exact
       predicates and loses none.
     - Census: still 607 / 101 / 521, but 93 refused methods get
       further. They now stop at the census's unbound arguments, at
       pmi ca and c6, and at SIMPOS (`undefined_method:raise/2`, 16).
4. **The PSI-III microcode emulator** becomes the authority on what
   each opcode does once the microword work lands. On its own it is a
   bare machine with nothing to load.

The first deliverable that matters to PIM/m: `pimfep.ptf` and
`pimscsi.ptf` running on 1-3 as PIM/m's front end (roadmap P5,
`../scsi_plan.md` S7). Their own SIMPOS requirements are in
`required/ptf_class_refs.tsv`.

## 6. What would change this page

Media (`../psi_acquisition.md` §6, §9 leads) would replace most of §4.
The JAIST library's KL0 manual (MP7002-1) and SIMPOS manuals
(MP3001-1, MP3002-1) would settle §3's KL0 gaps and much of §4.

## 7. The window system, the Librarian and the shell (2026-11-24)

`subsystems/window.md`, `librarian.md` and `shell.md` specify SIMPOS's
three user-facing subsystems for stand-in builders. Each claim is cited
and graded, and tagged with a version from 1.00 to 7.x/A22. The sources
are TR/TM pages read by eye, the IPSJ papers, the IFS sources, the
`.ptf` packages run under `../../psi/kl0.py`, and the ICOT museum video.
Also in `subsystems/`:
- `gaps.md`: what is still unknown, ranked;
- `finds.md`: possible SIMPOS code. `cil/src/ds_bep.esp` carries a
  patched copy of three SIMPOS 6.1 Librarian classes, and `cal-esp`
  has a debugger derived from SIMPOS's;
- `classes_added.tsv`: classes found beyond `printed/` and `required/`;
- `notes/`, `listings/`, `coverage/` and `tools/`: the evidence and
  the measurement against `required/`.
