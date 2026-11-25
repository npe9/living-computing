# What remains unknown about SIMPOS's window system, Librarian and shell (2026-11-24)

Companion to `window.md`, `librarian.md` and `shell.md` in this directory. Each subsystem's
unknowns are ranked by how much the held programs depend on them: use counts are from
`coverage/coverage_<partition>.tsv` (call sites in the 15 held IFS programs) and from the held
compiled packages. Each row names what would settle it. The three tables were drafted by the
writers of the three specs and are kept as they wrote them; this head ranks across them.

## How much is specified, read strictly

The required surface is the class and instance methods that `../required/requirements.tsv`
attributes to each partition's classes (`coverage/partition_*.tsv`). Each is compared with the
notes' fact rows by `tools/coverage.py` and `tools/class_coverage.py`.

| partition | methods | on their class, documented | name/arity documented elsewhere | meaning from use only | nothing |
|---|---|---|---|---|---|
| window | 676 | 15 | 369 | 212 | 80 |
| librarian | 114 | 1 | 14 | 78 | 21 |
| shell | 115 | 9 | 16 | 33 | 57 |
| other | 531 | 22 | 75 | 77 | 357 |

2026-11-25: `time` gained four required instance methods (get_count/2, set_count/2, get_value/5,
minus/3) when the census scan learned that `time` `now/2` returns an instance
(`../source_check_2026-11-24.md` §5 Status). `coverage/` was regenerated: other is now 535
methods, 22 / 75 / 27 + 53 / 358 (the four new rows have nothing documented); no other partition's
files changed.

| partition | classes | some method documented on the class | name documented elsewhere | use only | nothing | no methods required (nature-only or reference) |
|---|---|---|---|---|---|---|
| window | 135 | 5 | 67 | 5 | 10 | 48 |
| librarian | 32 | 1 | 8 | 7 | 2 | 14 |
| shell | 38 | 3 | 8 | 8 | 7 | 12 |

These are the counts after the second sweep (`sweep_2026-11-24.md` §4). Before it the method rows were:
- window 10 / 365 / 221 / 80;
- shell 4 / 11 / 41 / 59;
- other 5 / 73 / 81 / 372.

The class rows were window 4 / 68 / 5 / 10 and shell 2 / 8 / 9 / 7. The changes come from the 1990 ESP manual's
`stop_watch`, `standard_io_buffer`, `symbolizer` and `get_slot`/`set_slot` passages, and from the HELD-SOURCE copies of
SIMPOS's `name`, `pathname` and `e_string` (other partition). `tools/coverage.py` now counts grade HELD-SOURCE as
documentary.

Read the "documented elsewhere" column with care. It counts a name/arity documented on *any* class
in a documentary source. Some of those classes are the TM-115 font editor's own, and some are demo
code shown on screen. TM-125 lists about 45 methods without saying which class owns them.
`coverage.py` also does not read `../printed/classes.tsv`, so a few printed methods count as
use-only. One example is `process self/2` (TM-100).

The specs add meaning, from reading call sites, that the fact rows do not record:
- `librarian.md` §8 moves 18 rows from "nothing" to argument-level use.
- `shell.md` §8 counts 49% of methods, and 84% of uses, as documented or from use.
- `window.md` §8 lists the 56 selectors still without meaning.

## Across the three subsystems: the ten that matter most

| rank | unknown | subsystem | dependence | settles it |
|---|---|---|---|---|
| 1 | Which mixin owns each window protocol (TM-125 lists ~45 methods without owners; 369 required window methods are documented only by name) | window (G3) | 3,320 uses | 「SIMPOSプログラミング説明書(II) 入出力編」 (ICOT 1987, not held), or its successor 「小型化PSI/SIMPOS プログラミング説明書 (SIMPOS 8.0版)」 (ICOT 1992, cited INFO/cesp.j:118, not held); IPSJ 29th conv. 4E-6 (not held) |
| 2 | The `#` constants' values (`key#`, `mouse#`, `pf#`, `control#`...) as the macro expander turns them into integers | window (G2) | every read site, >600 uses | the expander's tables (cil `cil_esp.esp` re-implements the families, not the numbers); kl0.py on a held `.ptf` that compares a read code against a constant |
| 3 | `putf` directive set (only kwic's re-implementation describes it) | window (G1) | 495 uses | the I/O manual above |
| 4 | Generic object protocol booked on `as_program`: `class_object/2`, `refute/3`, `method/3`. **Owner of `get_slot/3`/`set_slot/3` settled**: class `class`, with `Obj!slot` as their macro (ESPtex/program-e.tex:5987-5988, PROSE). Their exact failure behaviour is still open | shell (1) | 338 uses (322 of them get/set_slot) | TM-388; the ESP manual has nothing on the other three |
| 5 | `library_utility` class-side `assert/retract` family: storage and persistence | librarian (2) | 287 uses | SIMPOS programming manual library section; sum's `cprolog.v32` read in full |
| 6 | `close_input/1`, `close_output/1` and the standard file classes' write-on-close and error behaviour | window (G8) | 271 uses | I/O manual file chapter |
| 7 | Pmacs default key bindings and command set | window (G6) | 223 user `:command` clauses | Pmacs part of 「SIMPOS使用説明書」 (JAIST MP3001-1); 「PSI/SIMPOS エディタ説明書」 (ICOT 1988, cited cil/man/biblio.tex:84-87, not held) |
| 8 | `nature(L)` create option: mixins added at create time, or a class selected | window (G29) | 206 uses | I/O manual; the ESP compiler |
| 9 | `library:get_class_object/3` resolution order and failure | librarian (1) | 160 uses / 11 programs | Ops 5.0 manual; kl0.py run of a held caller with a missing class |
| 10 | What a user sees when a program's `:goal` raises: error window, menu items, process naming | shell (4) | every program | 「SIMPOS操作説明書」 (JAIST MP3002-1) error-handling section |

The single most valuable unheld document for all three is the 1987 SIMPOS programming manual
volume II (I/O), cited by WINCS and IPSJ 118569 (`notes/trtm_window.md`, `notes/newipsj.md`). The
1988 「小型化PSI/SIMPOS操作説明書 基本編 (SIMPOS5.0版)」 (cited by IPSJ 118681) is the next for the
Librarian and shell. JAIST holds the 1985 manuals (MP3001-1, MP3002-1, MP7002-1;
`../../psi_acquisition.md` §9). Common ESP's window library, "based on" SIMPOS's window
specification (IPSJ 118569) and distributed as source in 1992 (`web_search_2026-11-24.md`), would
settle much of rank 1 if a copy turns up.

The second sweep (`sweep_2026-11-24.md`) adds the titles of later editions:
- 「小型化PSI/SIMPOS プログラミング説明書 (SIMPOS 8.0版)」 and 「… ESP 説明書 (SIMPOS 8.0版)」 (ICOT 1992,
  `INFO/cesp.j:116-119`);
- 「PSI/SIMPOS エディタ説明書」 (the Pmacs manual), 「… 操作説明書(I),(II),(III)」 and 「… KL0説明書」 (ICOT 1988,
  `cil/man/biblio.tex:84-97`);
- "Down-sized PSI/SIMPOS TCP/IP Network System Manual" and "… PSI Network System Manual" (cited by
  the PIMOS manual, `pimosman/Eman/e-network.tex:56,80`).

It found no copy or table of contents of the I/O volume.

The fixed-point search (`fixpoint_2026-11-24.md`) adds manual **numbers** and early titles, all
cited in digitised books or IPSJ papers, none held by any library found: 「ESP説明書（第1版）」
MP1002-1 (ICOT 1986; reported by a delegated NDL search, not re-opened), 「ESP 説明書（第2版）」
MP1005-2 (ICOT 1987, IPSJ 115299 ref. [2], read on the page image), 「SIMPOS使用操作説明書（第2版）」
MP3003-2 (ICOT 1986; reported, not re-opened), and the CESP 2.0 manuals 「CESP言語マニュアル
2.0版」 and 「CESPライブラリマニュアル2.0版」 (IPSJ 120508), and 「CESP言語2.0版」 (三菱電機東部
コンピュータシステム, 1994; reported, not re-opened). A delegated NDL search also reported (not re-opened) that MITI's gazette 通産省公報 registers
SIMPOS releases as national-project deliverables (2.0 in 1987, V4.0 in 1988, 6.0 as 5G-02-002 in
1990), at NDL only.
Still no copy or table of contents of the I/O volume. On rank 5, the class-id form of the
`library_utility` assert family suggests asserted clauses are listed among the class's predicates of category `l` (read as
local, INFERENCE) (`librarian.md`, `library_utility` class methods, USAGE); persistence remains open.

What is NOT a gap any more: the owner of `get_slot`/`set_slot` (class `class`); the `stop_watch` method set; SIMPOS
file-name syntax (HELD-SOURCE `name`/`pathname`, `sweep_2026-11-24.md` §2.1); the Librarian's structure and its command-list interpreter (cil's copy
of the SIMPOS 6.1 Librarian, `finds.md`); the system menu, Librarian, debugger and window menus by
version (screens of 1.00, 2.10, 2.50, A00, 5.0); the window creation vocabulary and menu item
formats (held code and compiled packages, kl0 runs).


## Window system (from `window.md`)

These are the unknowns, ranked by how much depends on them. Weight is in uses (held call sites) or n_programs.

**Settling sources** (none held):
- **IOM**: 「SIMPOSプログラミング説明書(II) 入出力編」 (1987).
- **ESP-IO**: 「ESPプログラミング説明書－入出力管理編」.
- **USE**: SIMPOS使用説明書.
- **4E-6**: IPSJ 29th national convention 4E-6 (Iima), 「SIMPOSのウインドウサブシステム」.
- **JAIST**: JAIST manuals MP3001-1, MP3002-1.

| # | unknown | weight | what would settle it |
|---|---|---|---|
| G1 | Full putf directive set and semantics. kwic's re-implementation is the only detailed source; the meanings of `\C \W \u` and kanji escapes are unknown | putf/2,3: 495 uses | IOM; ESP-IO; any held SIMPOS putf source |
| G2 | Numeric values of the `#` constants (mouse#, key#, pf#, control#...): the expander's tables | every read site (read/2 etc. >600) | ESP compiler/expander source; kl0 runs; IOM appendix |
| G3 | Which mixin owns each protocol (as_output vs as_standard_io_window...). TM-125 never says | 365 DOC-unowned methods, 3432 uses | 4E-6; IOM class reference |
| G4 | Behaviour of the nature-only mixins: as_mouse_input (12 programs), as_graphics (12), as_superior (11), as_input (11), with_superior_input_buffer (10), as_single_select (10), as_output (10), with_border (9), with_icon (8), with_click_information (5), with_bell (4), with_key_select (3), as_menu_input (3), select_notifier (2), deexpose_notifier (1) | 48 classes | IOM; 4E-6 |
| G5 | Output permission semantics in 3.x+: which of wait/notify/out/show exist, and the default | 33 held option uses | IOM; USE |
| G6 | Pmacs default key bindings and command set (100+ commands) | 223 user `:command` clauses build on it | Pmacs manual in USE; JAIST |
| G7 | `get_parsing_operator/2`, `set_parsing_operator/2`, the unparsing pair, set_max_depth/length: argument form. Depth/length elision is the programming manual's section 「標準入出力（ホロフラスティング）」 (title only, cal-esp/deb_jman/debug.tex:236) | 22+5+4+2+2+2 uses | ESP-IO; that section |
| G8 | close_input/1, close_output/1: is the file written on close only; is there an error on a missing file | file classes, 271 uses | IOM file chapter |
| G9 | Held 32-bit `.font` file format (the f822 layout is decoded) | 243 font option uses, 220 font creates | font editor source; a held font file dissected further |
| G10 | `read/6` field meanings beyond the cal comment; `read_with_code/3,4` | read/6 in cal, paragraph | IOM input chapter |
| G11 | `reshape/5` owner, and whether its arguments are outer or inside size | 72 uses | IOM; 4E-6 |
| G12 | `get_activity/2` second argument (`1`?) | 3 uses | IOM |
| G13 | `set_mouse_marker/2` numbering (6 = ?) | ~10 uses | IOM; video close-ups |
| G14 | Status-line (bottom band) middle box: selected window or window under the mouse | screen chrome | USE; better video copy |
| G15 | Window naming rule (`<prog>_<n>` vs `<class>/<N>`) | screen chrome, set_name | USE; 4E-6 |
| G16 | Screen size per release (1200×900 ... 1280×944) | layout code | hardware manuals; USE |
| G17 | The 6th argument of `draw_filled_rectangle/8` (`0`) | ptf paragraph | TM-785 class text; IOM graphics chapter |
| G18 | `create_marker/7` arguments. **Partly settled (CESP substitute)**: linguist's `as_markers`, documented as having "the same function" as SIMPOS's, takes `(W,X,Y,Width,Height,Type,^M)` with Type `box`/`line`/`reverse` (sweep_2026-11-24 §2.2) | kwic | IOM, to confirm |
| G19 | Menu kind `string` inside items_list (vs choice_list) | 283 uses | IOM menu chapter |
| G20 | Exact editor semantics beyond call shape: `set_current_buffer/2`, `clear_input/1`, `other_window/1`, `mark/1`: exact editor semantics | 20, 13, 8, 6 uses | Pmacs manual |
| G21 | `get_border_width/2`, `get_superior/2`: return form (outputs assumed). `get_margins/5` is `(W,^L,^R,^Head,^Tail)` in the CESP substitute for SIMPOS's `with_margin` (sweep_2026-11-24 §2.2) | 12, 3, 4 uses | IOM |
| G22 | `call_color_manipulator/2` and the colour API (set_color/2,3) beyond Giho 8907 | 9 uses | TM-785 full text; PSI-II manuals |
| G23 | `exe_help_menu/3`, `enable_menu_help_click/1`, `set_help_font/2`: menu help protocol | 7+2 uses | IOM |
| G24 | Temporary-menu exit in 3.x+: `abort` returned, or fail as in 1.0 | menu sites | IOM |
| G25 | `do_` manager methods: still exposed after 1.0? | 0 held uses | 4E-6 |
| G26 | System-menu item list per release, window side | screen | USE; video |
| G27 | Window-manipulator items after 1.0 (video truncates `PERM… ATT…`) | screen | better video copy; USE |
| G28 | Pmacs mode-line `[a,b]` field meaning | screen | Pmacs manual |
| G29 | `nature(L)` create option: added at create, or class selection | 206 uses | IOM; ESP compiler |
| G30 | `flash/1` precise effect (buffered output flush vs screen flash) | 100+ uses | IOM |
| G31 | 56 UNSPECIFIED selectors in window.md Appendix A (list: `coverage/out/unspec.tsv`) | 1-22 uses each | case by case |

## Librarian (from `librarian.md`)

Companion to `pim/docs/simpos/subsystems/librarian.md`. Use counts come from coverage_librarian.tsv /
requirements.tsv (uses / programs). "Settles it" names the cheapest source that would.

Key unheld manuals:
- 「小型化PSI/SIMPOS操作説明書 基本編 (SIMPOS5.0版)」 (ICOT 1988, cited by IPSJ 118681). Called "Ops 5.0" below.
- The SIMPOS manual set's volume 2, Operations (操作編), not held (notes: ifs_libshell §3.5).
- JAIST holdings MP3001-1 / MP3002-1 (SIMPOS manuals).

| # | gap | dependence | settles it |
|---|---|---|---|
| 1 | Exact semantics of `library:get_class_object/3`: does it load on demand, what is the resolution order for `'p##c'` vs `##(p,c)`, and does it fail or raise on absence? | 160 / 11 | Ops 5.0 / MP3001-1 programming volume (library methods); else a kl0.py run of a held .ptf that calls it with a missing class, observing the caller's recovery code |
| 2 | Class-side `assert/assertz/asserta/retract/retract_all` on `library_utility`: storage (template vs object), persistence on save, interaction with `:node(DB,...)` calls on an instance | 287 / 4 (sum 248) | 「SIMPOSプログラミング説明書」 library section; sum/src/cprolog.v32 read in full (not yet done) for its expectations |
| 3 | `library_utility:catalogue/3` without a window, in 7.x: accepted source forms (paths, wildcards, terms, term lists), and the Ids it returns for a failed class | 15 / 7, plus every install | the cil copy is 6.1/V6.11. A 7.x Librarian copy (none known); otherwise Ops 5.0 |
| 4 | What `:assign(#library)` binds | 35 / 6 + ptf | programming manual; a disassembly of a held ptf caller only shows the call |
| 5 | `check_class_id/3` Info codes (0 = not loaded; "8 =< Info means loaded") | 11 / 3 | the programming manual, or more held callers (grep all IFS for check_class_id) |
| 6 | How Execute reads a command file: `fxd("x.com")` vs bare `CATALOG.COM` vs `fdd("x.com")`; who handles a nested `command("x.COM")` item (the copy's command/2 takes a list only) | kappa 34 command items, 44 fxds; all installs | Ops 5.0 (Execute chapter); TM-785/786 drawing.com / simshow.com contents (not printed; perhaps on the ICOT FTP mirrors) |
| 7 | Meaning of `fxds` vs `fxd` inside a list (the copy maps only `fxd`) | 44 / 2 | Ops 5.0; any held 5.x+ .com using `fxd(` (grep found none) |
| 8 | `.env` package-environment file format, and `save_environment` | gog install | a held `.env` file (none held; cgs_env.env is named only) |
| 9 | `.ptf` load semantics when the package exists: error `Package X already exists` → menu. What does `load_package_template/3` do under error_mode off? | 2 installs | TM-785 p3 shows only the interactive case; a kl0.py run cannot settle it; Ops 5.0 |
| 10 | 5.0 Utility and ESP tool submenu items | screen fidelity | IPSJ 118681 Fig.1 does not expand them; Ops 5.0; ICOT museum video at later versions |
| 11 | The elided rest of the Fig.2 `menu_list` (Package, Execute, Utility, ESP tool command names) | screen + customization | Ops 5.0; IPSJ 118681 p2 re-read at 600 dpi (the ellipsis is printed, so probably unrecoverable) |
| 12 | Name and location of the Librarian initialization file | customization | Ops 5.0; any held user directory listing (none) |
| 13 | 5.0+ prompt texts for Catalogue / Save / Load / Delete (`File Name>`? `Class Name>`?) | screen | Ops 5.0; video of a late SIMPOS |
| 14 | The unheld natures librarian_version/delete/package/spy/reference/fdd/subroutine, as_assert_utility, librarian_catalogue, as_class_maker, compiler_error_reporter | all methods implied in §2.2-2.3 | another SIMPOS-copy in a held archive (grep all IFS and ICOT-FTP material for `librarian_package`); none found so far |
| 15 | `get_class_id/5,6`, `get_class_id_in_package/6`, `get_class_id_in_environment/6`: the extra outputs | 22 / 5 | the cil copy's local callers (read ds_bep.esp:1915-1925, 2715-2725, 2825-2830 more closely); programming manual |
| 16 | `check/3` full label list and status values (dates? atoms?) | 3 / 1 + Check screen | TM-181 p4 at higher resolution (only 96 ppi held); papyrus's other callers |
| 17 | `get_classes_with_wildcard/5` and `get_class_names/4`: the `all` argument's other values | 3 / 2 | programming manual |
| 18 | `get_class_id_atom_list/4`'s `'$$local'` argument | 2 / 1 | sum/src/main.wkm context; manual |
| 19 | Real `compile/2` / `uncompile/2` (stubbed in the copy): interpretive vs direct code switching and the menu commands Compile/Uncompile (gone from the 5.0 top menu?) | screen 2.x | TM-181/229 PROSE only; Ops 5.0 |
| 20 | Execute's `fdd` dialogue in full: what if the answer is not 0; error texts | install fidelity | TM-785/786 show the success path only |
| 21 | Error-handling menu for catalogue errors: the items besides "Skip this class" | every failing catalogue | sum/INSTALL prose only; Ops 5.0 |
| 22 | "Save all asserted predicates?" prompt text and choices | sum install | sum/INSTALL:26-29 prose only |
| 23 | Default macro bank: `esp_macro_expander` (1990 manual) vs `esp_macro_expander_for_compiler` (copy); the relationship between the two classes | 88 ptf records; 52 uses | the programming manual macro chapter; a kl0.py disassembly of a held macro bank's nature use |
| 24 | `esp_compiler:compile/4` InternalFormat 8-vector layout; `kl0_compiler:compile_one_predicate/6` outputs | 1 / 1 (CAL debugger) | layers/KL0.md work; MP7002-1 (KL0 manual, JAIST) |
| 25 | `fdd_volume` / `fdd_binary_file` semantics (sector size 256, 70-file limit, open modes) | 47 / 2 | 「SIMPOSプログラミング説明書(II) 入出力編」 (1987); MP3002-1 |
| 26 | `file_backup` (`superuser##`) and the shell `far` command: restore format | 4 / 1 | same I/O manual; a held backup floppy image (none) |
| 27 | `version:version/2` string for 5.x-7.x and A22 (kappa only accepts ≤ "4.0B") | 1 / 1, blocks kappa on later versions | TM-786 p8 shows `SIMPOS版名 : 5.0`; the exact string format (with or without suffix) is still open |
| 28 | Process name vs title: `librarian_59` (1989 error window) vs `librarian 49` (1990 title) | screen | Ops 5.0 screenshots |
| 29 | Spelling `Catalogging` in 7.x (the copy, 1986 screens) vs `Cataloging` (video reading) | screen | re-read esp.wmv@117-121 frame at full resolution |
| 30 | `as_esp_parser` / `as_esp_unparser` CVI/NVI arguments | 10 / 1 | programming manual I/O volume |
| 31 | `library:get_a_code/7` / `get_a_name/8` argument categories (`l` = local; other values) | 13 / 4 | the CAL debugger (cal-esp/deb2.12) read further; the SIMPOS debugger manual |
| 32 | Remote catalogue / remote load (`node_name`) behaviour | 0 held uses | out of scope for held programs |

## Shell and top level (from `shell.md`)

Ranking key (reordered by use count): use counts from coverage_shell.tsv / requirements.tsv (uses/programs), then how many held
install procedures pass through the feature. "Settle by" names the most specific source known.
Spec: pim/docs/simpos/subsystems/shell.md.

| # | unknown | dependence | what is known | settle by |
|---|---|---|---|---|
| 1 | Exact contract of `get_slot/3`, `set_slot/3` (instance and class), and owner and contract of `class_object/2`, `refute/3`, `method/3` (booked on as_program) | 161+151+6+4+8+7+1 = 338 uses | get/set_slot are methods of class `class`, `Obj!slot` their macro (ESPtex/program-e.tex:5987-5988, PROSE; done 2026-11-24); the manual has nothing on the other three | TM-388 App. G (:refute); other.md agent's findings |
| 2 | `messenger` look and `confirm` result: does confirm return yes/no, what buttons, where it appears, does show/2 wait or time out | show/2 86/2, show/3 14/2, confirm/2 14/3, confirm/3 4/2 | callers never test an answer | a screenshot of a messenger box (none held); kl0.py run of a compiled sender (remote_pimfep_executor message/3) to see following code; 入出力編 manual 1987 |
| 3 | `stop_watch` details left: the time object's methods (`get_count/2` by use only); whether stop fails when stopped | 93/6 | create/start/stop/reset/show PRINTED with a method table; show gives a time instance and is valid only after stop; no measurement across two days (ESPtex/program-e.tex:10018-10045; done 2026-11-24) | the time class in the programming manual |
| 4 | What `:activate/2` does when the program's `:goal/1` raises an uncaught error: which window, which menu items, which process is named | process activate 60/12; every program | 2.10 debugger-input error window (TM-181 p5); librarian 5.0 (TM-785 p3) | 「SIMPOS操作説明書」 (operation manual, not held) error-handling section; any screenshot of a user-process error (search IPSJ 33rd conv. 4D-x papers, not held) |
| 5 | Full 7.x system menu (MEDIA SYSTEMS / "others" submenu): items, order, logout confirm text | every install procedure (gog, fuzclust, utter, cal-esp) | 2.50 list; 7.x prose names logout, others>user>maintenance>register, TCP-IP>reset network, process manipulator | SIMPOS 7.x operation manual; a PSI-II/UX video or photo; JAIST manuals |
| 6 | Login dialogue text of 3.0-8.x (prompt exact spacing, failure message, `me`/`me` still allowed?) | every held program's first step | 7.x transcript `user     > ` / `password > `; 1.0 me/me | 「SIMPOS操作説明書」; PIMOS FEP login stand-in source in pimmcsp (already read: "Enter SIMPOS user name>") |
| 7 | Login file: other heads (initial program, auto-created PS with window positions, mail), defaults when `menu` absent, string vs atom labels | all held login.com; TM-229 p5-6 features | menu/define/package/shell_transient + coordinator information/3 items | 「SIMPOS操作説明書」 login-file chapter; kwic-esp/doc/classSpec.IO1 (read for information/3 context); any other login.com on held media |
| 8 | Shell grammar: pipes, output redirection, background, other built-ins, error texts, whether `call` waits | kappa 12 transient commands; kwic, cil install lines | `$`, call, alias, +/-/& options, `{` stdin (INFERENCE) | 「SIMPOS操作説明書」 shell chapter; kwic-esp/doc (grep shell); papyrus PIMOS shell is NOT SIMPOS |
| 9 | Exact semantics of `process create/3` mode list and `set_area_limit_execution/7` (which element is which area limit, priority, query mode; what `nil,nil` are) | create/3 9/3, set_area_limit 2/1 + every kappa .SHELL; ptf 4 variants | four 4-lists seen; priority words small/middle (INFERENCE) | 「SIMPOSプログラミング説明書」 supervisor/process chapter (not held); JAIST MP3001-1/MP3002-1; kl0.py run of pimfep##pimos_timer create_timer/9 with a traced `process` stub to see which elements are tested |
| 10 | `get_arguments/2` / `parse_arguments/2` / `save_arguments/2` exact element formats; how the shell tokenizes `-s12`, quoted strings, pathnames with `>` | 10/1 + 3/1 + kwic | sign-then-name convention agreed by kwic and kappa | run kappa .SHELL ptf code under kl0 with a stub get_arguments to see what is parsed; kwic v2_tool.mac read in full |
| 11 | `trace_exception_handler` (set_trace_switch/2, set/reset_exception_handler/1, trace_enable/1) and the switch value 3 | 15/1 (cal-esp) | CAL debugger tracing only | KL0 machine manual / tracer description (TM-? KL0 reference); cal-esp/deb2.12/cm.esp:700-760 read in full |
| 12 | `coordinator information/3` value format for structured items (conjunction vs list), failure behaviour | 3/1 + ptf 2 callers | keys and caller fallbacks | kwic-esp/doc/classSpec.IO1; kwic dbUtil.esp make_AliasTable in full; pimfep superviser listing under kl0 |
| 13 | `as_server_program` protocol (give_answer values, convert_con_req fields, service registration name) | 21 uses / 3 programs | talk example | IPSJ network papers 4D-8/4D-11 (not held); pimfep remote_pimfep_invoker listing (ptf, held) |
| 14 | `user` object methods beyond local_name/initial_mode; `user_list` index type; ranks list (general, superuser, ...) | 5 uses + pimfep | identify/4, login_user/2, user/2, user_list/2 | TR-524 p15-18 (ranks, passwords, OCR only so far: eye it); kappa SVCTL.ESP user code |
| 15 | `world` methods beyond create/define/set_default_logical_name; how `define :- "me" := [...]` re-binds me: | define item in every login.com | pimfep simpos_user create/4 | TR-056 p24-25 (world), eyed pages; file manipulator "Define worlds" (disc/INSTALL:23-25) |
| 16 | What the system-menu item pop-up offers (create/kill; suspend/resume?) and when it appears | every menu start | video create/k…, WHICH ? create/kill; TM-143 start/stop/suspend/resume | better copy of simpos.wmv; TM-143 p3 re-eye at higher dpi; 操作説明書 |
| 17 | MEDIA SYSTEMS rows 7-10 of the A00 video menu | display fidelity | 2.50 printed list | higher-bitrate copy of the ICOT museum video |
| 18 | 2.10 goal prompt `:-` vs `?-`; whether 2.x+ still prints `> Success !!` / `> Fail !!` | listener fidelity | 1.00 `:-`+Success; 2.00 `?-`+bindings | TM-181 p4 at 600 dpi; Giho 8609 p20 re-eye for a Fail case |
| 19 | Debugger Menu of 5.x-7.x (A00 list vs CAL labels) and the leash command words beyond step/skip_predicate/no_trace | cal-esp only | 1.00, 2.x, A00 menus; the CAL debugger's 1992 manual (DERIVED, SIMPOS 7.0): Debugger Menu `Mode_Leash`/`State`/`Set_spy`/`Inspector`/`Re_display`/`Abort`/`[Exit]`, commands step/skip/leap/fail/retry/print/notrace, leash levels full/tight/half/loose/no (cal-esp/deb_jman/debug.tex; shell.md §5.4.4) | SIMPOS debugger manual (not held); how much of CAL's is SIMPOS's stays open |
| 20 | `interpreter` interpret/2 and create/3 contracts | 6/3 | interpret a goal (INFERENCE) | cil/src/cil_kl0.esp:300-330 read; cal-esp/deb2.12/deb.esp:200-230 read |
| 21 | `throw raise/1,2` catcher side: how a program catches a tag (catch/3? situation?) and what an uncaught throw does | 12/4 | tags list | grep held source for the catching construct (`:catch(`, `situation`), TR-285 p10-11 eyed |
| 22 | `event make_message_string/4` and the event class hierarchy | 2/1 | name only | TR-087 p9-10, TR-285 eyed; kwic searchMan.esp:320-330 |
| 23 | `as_program exit/1` and `cut_off/1`: when SIMPOS calls them (kill, logout, shut down) | demons in pimfep/pimmcsp/pimscsi; 19 IFS definitions | INFERENCE only | kl0.py run of exterminate on a pimfep program with a tracing stub; 入出力編/supervisor manual |
| 24 | `initiation_table/2`, `current_state/2`: the process saver and login auto-start | 2 uses (cal, cil) | comments "SIMPOS process saver" | cil/src/ms_cdn.esp:530-560 read in full; 操作説明書 login chapter |
| 25 | `abort_handler` / coordinator abort menu: which key shows it, its items | kwic 1 site, pimfep superviser | slots and swap protocol | kwic-esp/src/searchMan.esp:270-340 read in full; ptf listing of abort_handler sends |
| 26 | Boot of 3.0+ from disk: IPL modes, which file is read, how ipl.com files are chosen | kappa ipl.com | 1.00 floppy boot; 1990 IPL modes prose | ESPtex/overview-e.tex:1150-1180 eyed; kappa2/INSTALL ipl instructions |
| 27 | `user_process_profile get_user_profile/5`, `network_login_user login_user_list/3`, `process post/1`, `trace trace/1,2`, `debugger_recorder save/3`, `dummy_debugger new/2` | 1-3 uses each | call sites only | read each call site's surrounding code; kl0.py run for the ptf ones |
| 28 | `call_counter` setters (17 methods) | 17/1 | named in ESP manual TeX | ESPtex/program-e.tex:10198-10233 read in full |
| 29 | Status line in 5.x-7.x (fields, indicators, colour on PSI-II) | display fidelity | 1.00-2.50 | TM-785/786 page images (screens 5.0) re-eyed for the bottom band |
| 30 | Logout effects (process kill order, `exit/1` calls, saver) | session end | `logout -> yes` | 操作説明書 |
