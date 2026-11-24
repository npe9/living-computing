# What the surviving ESP programs require of SIMPOS: the measurement (2026-11-23)

Scratch root `<B>` = /private/tmp/claude-501/-Users-npe-src-living-computing-pim/01b03f2f-1efc-495c-9771-b09885a1fa2f/scratchpad/simposspec/B.
Nothing in the repo was edited, built or committed. No network was used, and nothing from the archives was executed.
To re-run everything (about 1 minute): `sh <B>/bin/run_all.sh`.

## Inputs

- **The 19 IFS SIMPOS archives**, from the earlier extraction
  `.../scratchpad/simpos2/extract/ifs_simpos/<archive>/`. They are grouped into 15 programs:
  - `kappa2` with `kappa2d1..3`, which are data only;
  - `kwic-esp`, counted from `kwic-esp-002` only. That archive is the second release; the first
    (`kwic-esp.tar.Z`) is left out because it would double the use counts;
  - `papyrus`, whose `source.tar` was listed (207 files, no absolute or `..` paths) and extracted
    into the new directory `<B>/x/papyrus_src`.
- **ESP files are found by content, not by extension.** A file counts if it is non-binary and
  holds a line-initial `class|macro_bank NAME has|with_macro`. There are 1,664 such files. They
  include `sum`'s 95 `.v32` files, `fuzclust`'s 65 `.grape/.comp/.eism/...` files and the
  `.mac/.MACRO` macro banks.
- **Compiled packages**, read with the project's `pim/asm/ptfdump.py` (read-only, through
  `bin/ptfside.py`; output `ptf.json`):
  - `kappa.ptf`, utter's four packages and papyrus's ten `.pak.1`;
  - psdpim's five packages and pimosobj's `paragraph`, which have no source.
- **Command and login files**: 56 `.com/.COM`/login files, read by `bin/comscan.py`.
- **For corroboration**: the OCR text of 51 SIMPOS TR/TMs (`scratchpad/simpos2/ocr`) and the ESP
  manual TeX (`inside/x/esptex`, `esptexj`).

## Method (`bin/esplex.py`, `bin/espscan.py`)

### The reader

- **Tokenizer and operator-precedence reader.** The operator table is the ESP manual's own
  ("System operators", `ESPtex/program-e.tex` lines 7816-7852): `class` 1180, `has` 1160,
  `instance` 1155, `local` 1154, `;` 1150, `nature`/`attribute`/`component` 1120, `:` fy/xfx 100,
  `!` yfx 200, `#` fy/xfx 90, `##` 50, and so on. The 700-level `= == := is < ...` operators are
  missing from that table and were added.
- **Per-file operators.** Each file's `add_operator/3` directives, and those of files it
  `include(...)`s (resolved by basename, e.g. `KP_ADDOPE.INC`), are applied before tokenizing.
  Where a file does not parse, the program-wide union of directives is tried as well.
- **JIS decoding.** ISO-2022-JP is decoded by hand (`ESC ( B/J/H`, `ESC $ @/B`, `ESC ( I`). NEC
  row-13 and other unmapped pairs become U+3013, so line numbers stay exact.
- **Splitting a class into items.** A class is split at the depth-0 `;` into items. The section
  state (class, then `instance`, then `local`) is tracked token by token. Each item is parsed
  separately at priority 1200.
- **Parse coverage.** 96,061 items were read and 213 did not parse (0.22%). 108 of those, inside
  classes, went through a token-level fallback: `: name (`, arity from the depth-1 commas,
  receiver only if `#C`.
- **Pasted editor stamps.** Lines such as `>sys>user>kaoru>kk_tr_ed.esp.19, 20-Feb-87 ...` (not
  comments) sit before 4 class headers; they are split off.

### Recording a class

For each class the scanner records:
- its natures (`pkg##` stripped);
- its slots, from `attribute`/`component`, `slot := V`, `(slot := V :- Body)` and
  `slot is Class`;
- its methods, by section, with arity;
- its local predicates;
- its macro patterns (`Lhs => Rhs [when/where Cond]`; the macro right-hand sides are walked too).

### Method arity convention: the receiver is counted

In `:m(R, A2..An)` the arity is n, so `:create(#list, X)` is `create/2`. This is **measured, not
assumed**: on the 794 kappa classes that also have source, the compiled package's class/instance
predicates match the source in name and arity 5,327 times, and are off by one 0 times. The same
holds for utter (375/0) and papyrus (979/0) (`ptf_crosscheck.txt`). The held ESP manual
(`program-e.tex`) gives no `name/arity` notation for methods. It always writes the receiver as the
first argument, e.g. `:next(Obj, Current, Next) :- next(Current, Next);` (lines 4912 and 4965)
and `:get_predicate_list(#call_counter, List, Sum)` (line 10172). Its rule that a call matches
"the same predicate name and the same number of arguments" (line 1442) applies to that written
form, so the manual counts the receiver too.

### Attributing each send: the `how` column

| how | rule |
|---|---|
| `class` | the receiver is `#C` or `#p##C` |
| `create-bound` | the receiver variable was the single fresh variable of `:create*/new` sent to a class. This is not done when the user class defines its own `create*`, since it may be a factory (9,305 sends left unbound for that reason). |
| `self` / `self-inherited` | the receiver is the head's first argument |
| `slot-*` | `X!slot`, with the slot type learned from initialisers and `Obj!slot := X` |
| `unattributed` | the receiver's type is unknown and no class in the program defines that `name/arity` |
| `ambiguous-user-or-system` | the receiver's type is unknown and the program defines that `name/arity`, but the selector is also attested directly on a system class somewhere in the corpus (175 selectors, 7,658 uses). These are written as `?`/`ambiguous` rows. Untyped sends of a program-defined selector that no system class is seen with count as internal. |

- A local predicate inherits argument types from its call sites; this runs as three passes.
- A send counts as **internal** if `name/arity` is defined:
  - in the target class's user closure;
  - in a user class that inherits the target (the mixin case);
  - or, for untyped receivers, anywhere in the program.
- **Inherited sends are attributed to the set of external natures**, `{n1|n2|...}`:
  - for a mixin with no external nature of its own, the set is its descendants' external natures;
  - if the set is empty, the target is `<root>` (see the method names below);
  - a one-member set is assigned to that member;
  - a set is "refined" to a member when exactly one member has that selector attested directly
    elsewhere.

### What counts as defined, and what is required

- **Defined in a program** means its source classes plus the class ids of its own compiled
  packages (kappa: 797; utter: 104; papyrus: 207 across its 10 `.pak`).
- **A class defined in a different IFS program** is still listed, but its `how` carries
  `(other-IFS-app:P)`.
- **Built-ins** are goals that are neither a send, a control construct, a local of that class nor
  a user macro.
  - Each built-in is checked against the KL0 built-in wrapper class found in cil (see the next
    section) and against the words of the ESP manual TeX.
  - Arithmetic inside arguments, which the compiler expands, is not seen.

## A find: SIMPOS-level source inside `cil`

`cil` (natural-language), in its own packages `spec_ms`, `esp_call` and `kl0`, carries classes
named like SIMPOS's:
- **`library_utility`** (`cil/src/ds_bep.esp:3123`). Its header says
  `mkpsi000::>sys>user>yasuko>UT.esp.2, 29-Jul-88`. Its natures are `librarian_version`,
  `librarian_class_generator`, `librarian_delete`, `librarian_package`, `librarian_spy`,
  `librarian_reference`, `librarian_fdd`, `librarian_subroutine` and `as_assert_utility`. It has
  35 methods, among them `create/2,3`, `compile/2`, `command/2` and `set_output/2`.
- **`coordinator`** (`ms_cdn.esp:43`, "coordinator invoked from system menu").
- **Two `builtin` classes.**
  - `cil_kl0.esp:74`, in package `kl0`, wraps every KL0 built-in as `:name(_, A..):- !, name(A..)`.
    That gives **176 KL0 built-in name/arity pairs**, the best built-in list held. Its header
    comment also lists KL0's renames (`set_substring -> copy_string_elements/5`, ...).
  - `cil_esp.esp:33`, in package `esp_call`, has nature `kl0##builtin`.

These look like a modified copy of the Librarian's top class and of the KL0 interface, and
deserve a closer read. They also make `library_utility` show as "defined in another IFS app" for
the 11 other programs that use it. Those are uses of SIMPOS's `library_utility`, and they are
kept in the requirement set.

## Results (numbers in `summary.json`)

### Totals

- 15 programs, 1,664 ESP files, 2,274 classes defined, 83,983 sends.
- **367 named external classes.** This includes 36 `simpos##` classes named only by the compiled
  packages; those rows have kind `ptf-ref`. By evidence tier (`classes.tsv`):

| tier | classes |
|---|---|
| A: in a compiled package as `simpos##C` | 210 |
| P: provided by a held package rather than SIMPOS (`pimfep##as_pimos_string_io_device`, `pimfep##net_spawn_user`, `pimscsi##mbus_allocator`) | 3 |
| M: named in the ESP manual TeX (`call_counter`, `search_table`, `font_editor`, `esp_compiler`, `bitmap_display`) | 5 |
| B: named in the TR/TM OCR | 9 (+12 weak one-word names) |
| C: used by two or more programs | 9 |
| D: one program only, unconfirmed | 115 |
| X: defined in another IFS app | 4 |

  Tier D mixes probable SIMPOS classes with application classes missing from the archives:
  - probable SIMPOS: `librarian_*`, `debugger_*`, `standard_popup_*`, `kl0_compiler`,
    `ftp_user`, `editor_*`;
  - application classes missing from their archives: sum's `gen_*_win`, icotext's `imi_*`,
    kappa2's `kappaP`.
- **Requirement rows** (`requirements.tsv`, 3,578 rows):
  - 1,436 class/instance methods on named classes;
  - 706 on nature sets or `<root>`;
  - 760 unattributed and 175 ambiguous selectors (`?`), each with candidate classes that have
    the same selector attested directly;
  - 93 inherited slots;
  - plus nature, `#ref` and `ptf-ref` rows.
- **`<root>` methods** (self-sends in a class with no external nature):
  - attested ESP object protocol: `new/2` (class, 481 uses), `get_slot/3`, `set_slot/3`,
    `class_object/2`;
  - the rest are mixins whose combining class is not in the archive.

### Built-ins, constants and pathnames (`builtins.tsv`, `pathnames.tsv`)

- 353 built-in predicates:
  - 176 appear in the cil KL0 table;
  - 81 are words in the ESP manual TeX;
  - 149 are in neither (operators, `cut_and_fail`, `relative_cut`, other system macros, and
    some mis-scoped locals: see the column for locals of the same name elsewhere).
- 51 user macros, kept apart.
- 64 `a#b` constants:
  - `key#cr`, `mouse#l`, `standard#output`;
  - and the macro forms `string#"..."`, `16#"..."` and `double_bytes#{...}`.
- 1,254 pathnames: 318 absolute (`>sys>user>...`, `>sys>spec>...`, `>sys>font>kanji_16.font`,
  `>sys>csp>PMPSI.DIR`) and 936 logical-name forms (`font:`, `me:`, `user:`, kappa's 30 logical
  directories).

### Compiled packages (`ptf_class_refs.tsv`)

- 269 external `pkg##class` references; 212 of them are `simpos##`.
- 36 `simpos##` classes that no source sends to:
  - the supervisor and network layer: `boot_process`, `interrupt_process`, `trap_process`,
    `memory_manager`, `tcpip_*`, `telnet_terminal`, `network_*`;
  - `esp_macro_expander_for_compiler`, an implicit compile-time requirement (88 class records).
- Selectors that psdpim's packages send and do not define: `ptf_unattributed_selectors.tsv`.

### Librarian and login vocabulary (`librarian.tsv`, `command_files.tsv`)

- Commands: `fxds/1` (44), `command/1` (34), `make_environment/2`, `save_environment/1`,
  `make_package/2`, `save_package/1`, `use_package/1`, `save_all_classes/0`, `load/1`,
  `refute/1` (with `:ipl_load(#kappa##kappa_loader, [...], 270)`).
- Login files: `menu/0` (`area_limit/1`, `items_list/1`), `define/0` (`"name" := ["dir"]`
  logical names), `package/0`, `shell_transient/0`.

## Minimal and full sets

- **Criterion: the fewest distinct SIMPOS-side keys** (`programs.tsv`). A key is one of:
  - a named class/kind/method/arity;
  - a nature-set method, collapsed to (kind, selector, arity);
  - an unattributed or ambiguous selector, collapsed to selector/arity;
  - a slot;
  - a `#ref` class;
  - a built-in, a constant or a directive.

  User macros, and classes of another IFS app, are excluded (the latter go to the column
  `needs_classes_of_other_ifs_apps`). The cil-defined `library_utility`, `coordinator`, `message`
  and `builtin` count as SIMPOS.
- **Minimal: `txtstrct`, 138 keys.** This is 21 files and 30 classes, with:
  - 31 named system classes;
  - 29 methods on named classes, among them:
    - `symbolizer` x5, `string.append/3`;
    - `standard_input_file.create/3`, `getc/2`, `getl/2`, `end_of_input/1`,
      `standard_output_file.create/3`;
    - `library_utility.create/2`, `catalogue/3`, `save/2`;
    - `pmacs_window.create/3`, `popup_choice_window`, `temporary_window`, `inferior_window`,
      `font.create/3`, `character.is_control/2`, `to_lowercase/3`;
  - 7 nature-set methods;
  - 4 slots;
  - 34 unattributed editor and window selectors;
  - 30 built-ins.

  The full list is `per_program/txtstrct.tsv`. The next smallest is chal (146), but chal also needs
  cal-esp's `cal_window`.
- **Greedy cover** (`subset_cover.tsv`): txtstrct 138 → chal 245 → utter 403 → knov 580 →
  disc 741 → icotext 917 → papyrus 1,100 → sum 1,324 → fuzclust 1,538 → gog-esp 1,784 →
  euod 2,017 → cal-esp 2,314 → kwic-esp 2,593 → cil 2,941 → kappa2 3,470.
  - **The full source-side set is 3,470 keys.** The 36 `simpos##` classes seen only in compiled
    packages come on top of it.
  - Each prefix satisfies exactly the programs in it, so no program comes free with a smaller one.
  - kappa2 alone needs 1,359 keys (169 named classes).
- `units.tsv` breaks programs into subdirectories (e.g. euod's demonstrations). It counts sends in
  raw form and ignores dependencies between directories.

## Checks against the compiled code (the known-plaintext oracle)

For each compiled class that also has source, the compiled package's selector cells were compared
with the scanner's sends (`ptf_crosscheck.txt`):

| program | selectors found by both | recall | found only in source |
|---|---|---|---|
| kappa2 | 11,032 | 96.7% | 109 |
| utter | 660 | 86.3% | 56 |
| papyrus | 2,112 | 93.2% | 33 |

The compiled-only cells are mostly data functors (`,/3`, `^/3`, `->/3`) and kappa's `@/2` macro
expansion. ptfdump's selector cells cannot tell a send from a functor, so recall is a lower bound.

## The old regex census (`docs/simpos/required/old_regex_census.tsv (superseded by simpos/required/)`), checked row by row

The comparison is in `old_census_crosscheck.tsv`:
- 249 of its 300 classes are confirmed;
- 118 classes are new (82 found in the source, plus the 36 seen only in compiled packages);
- 14 of its rows are **package names, not classes**: `spec_ms`, with its "328 uses", is the
  package of `#spec_ms##look_up` etc. in cil; also `lax`, `laxobj`, `sax`, `simpos`, `ict4`,
  `jo_*`, `tjbunmyaku`, `fts`, `superuser`;
- 16 are classes defined in an IFS program or its `.ptf` (kappa's `kappaupt_*`, `cgs`, `ltb_*`,
  `solver`, ...);
- 21 are regex debris (`_`, `b`, `k`, `x`, `class`, `nature(s)`, `natures1/2`, `end_of_nature`,
  `putf`, ...).

Its method lists have no arity and no class/instance split. Its per-class "uses" counted
`#C` references together with sends; `classes.tsv` now separates them.

## Limits

- **Dynamic dispatch.** About 11,800 sends (760 distinct selectors) have an unknown receiver,
  and 7,658 more are ambiguous. Their
  candidate classes are only suggestions. Nature sets (706 methods) are not resolved to one class,
  because the method tables of the SIMPOS window mixins are not held.
- **Typing is per clause and flow-insensitive.** Disjunction scoping is ignored, and only the
  single-fresh-variable `create*`/`new` binding is used.
- **Hidden requirements.**
  - Macro expansion is not performed, so sends produced by system macros are not seen (the
    compiled packages show kappa's `@` expanding to `@/2` sends).
  - Neither are the implicit compile-time classes (`esp_macro_expander_for_compiler`).
  - Arithmetic in arguments is not seen either.
- **The cil override is hand-set.** Treating cil's four SIMPOS-named classes as SIMPOS is a
  judgement, recorded in `report.py`.
- **Exclusion is per program.** Two programs that define the same class name each exclude it.
  Classes in tier D may be application classes that are absent from their archives.
- **Built-in attestation.** The ESP manual TeX does not hold a built-in list, so most built-ins
  are attested only by the cil KL0 table (1990-91). JAIST's KL0 manual (MP7002-1) would settle
  the rest.
- **Unread items.** 213 items did not parse, mainly in knov and papyrus; 108 of them were
  token-scanned. 18 files hold unmapped JIS pairs, which only affects strings.
- **Command files are few.** Only 56 command/login files exist; the other programs give their
  Librarian steps in their INSTALL prose, which was not parsed.

## Files

- `requirements.tsv`
- `classes.tsv`
- `builtins.tsv`
- `pathnames.tsv`
- `librarian.tsv`, `command_files.tsv`
- `per_program/<program>.tsv`
- `programs.tsv`, `subset_cover.tsv`, `units.tsv`
- `ptf_class_refs.tsv`, `ptf_unattributed_selectors.tsv`, `ptf_crosscheck.txt`
- `old_census_crosscheck.tsv`
- `summary.json`
- raw scans: `raw/*.json`, `ptf.json`, `com.json`
- scripts: `bin/` (`esplex.py`, `espscan.py`, `ptfside.py`, `comscan.py`, `report.py`,
  `ptf_crosscheck.py`, `run_all.sh`; `survey.py`, `t1.py` and `t2.py` are development probes)
