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
   `run_tests.sh` by `test_kl0.py`).* Witnesses name 91 opcodes
   (`../../psi/kl0_opcodes.tsv`); any other opcode is refused.
   - `convert/3` agrees with `pimos.vmac` on 96 names. 4 names are
     only in the FEP table and 8 only in PIMOS; none disagrees.
   - Two paragraph classes (`predicate_num_switch_icon`,
     `list_index_buffer`) give the answers their source predicts.
   - Of the 530 methods of the 104 classes, 298 run to a solution, 11
     fail cleanly and 221 are refused. The causes are ranked in
     `../../psi/README.md`. 58 of the refusals come from 15 opcodes
     not yet named.
   Cell numbering inside `.ptf` code was settled for this step: a hash
   table spans mask+1+2*keys+2 cells.
3. **An ESP compiler** producing KL0, checked structurally against
   `paragraph.ptf`. Use it to write the stand-in `simpos##` classes,
   in the order of §1 and in reference-count order (`symbolizer`,
   `string`, `process`, `font`, ...), labelled as scaffolding, with
   the printed source of §2 used verbatim wherever it exists.
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
