# The SIMPOS Librarian: specification for stand-in classes

Status: synthesis, 2026-11-24. SIMPOS is lost. This document collects what the held material says
about the **library** subsystem (the class and package registry), the **Librarian** (its window
program) and **library_utility** (its programmatic interface). The aim is enough detail to write
stand-in classes that look right on screen and do what the held programs need. Any gap filled by
reasoning is marked **INFERENCE**.

Companion files:
- Gaps, ranked: `gaps.md` (Librarian section).
- Reader notes cited as "(notes: X §n)". They are committed as `subsystems/notes/X.md`.

---------------------------------------------------------------------------------------------------

## 0. Scope, conventions, sources, versions

### 0.1 Scope

This document covers the 32 classes of the librarian partition (`partition_librarian.tsv`), plus
the classes that the cil copy shows sit around them: `librarian_class_generator`,
`librarian_read_term`, `librarian_menu`, and the system-menu target `librarian`. It is organized
around these subjects:
- packages and environments;
- command files;
- the Librarian window and its menus by version;
- the error menu;
- FDD (floppy) handling;
- the compiler and macro-expander interface.

Two subjects are covered elsewhere:
- The `.ptf` byte format: see `../layers/FORMATS.md`.
- The ESP language rules for packages (lookup order, `##`, preliminary references): these are
  summarized in §1.4 and are normative in `../layers/ESP.md`.

### 0.2 Conventions

**Arity counts the receiver**, as in `required/`. `:catalogue(U,Files,Ids)` is `catalogue/3`, and
`:assign(#library)` is `assign/1`. `printed/classes.tsv` does not count the receiver; its numbers
were converted.

**Citations**
- Reports (TR/TM): PDF page index, written as "TM-181 p4".
- IPSJ papers: record id and page, written as "IPSJ 36239 p5".
- Mitsubishi Denki Giho: by issue, written as "Giho 8609 p16".
- Video: segment@seconds, written as "simpos.wmv@0".
- IFS source: archive-relative path:line.
- Compiled packages: "pkg##class pred/arity (ptf)".

**Grades**

| grade | meaning |
|---|---|
| PRINTED | code or body printed in a report |
| PRINTED-INTERFACE | signature or table printed, no body |
| COPY | code that is itself a copy of SIMPOS: cil's `spec_ds##library_utility`, `librarian_class_generator`, `librarian_read_term` (§0.4) |
| USAGE | seen in a held program's source or compiled package |
| PROSE | described in text, including IFS INSTALL/README files |
| SCREENSHOT | seen on a screen image or in the video |
| INFERENCE | ours |

TRANSLATION marks our rendering of Japanese.

### 0.3 Sources by weight

| weight | source | what it gives | grade |
|---|---|---|---|
| 1 | cil/src/ds_bep.esp:1773-3518: three Librarian classes copied from SIMPOS 6.1, patched by cil's team (§0.4) | method bodies, messages, the command-list dispatcher, catalogue algorithm, natures | COPY |
| 2 | Held programs' sends to `#library` / `library_utility` (15 IFS programs; 21 compiled packages) | the required surface and argument shapes | USAGE |
| 3 | IPSJ 118681 (3J-8, Kodama and Fujimoto, 1990) | 5.0 menu, submenus, `menu_list` init-file format, internal structure | SCREENSHOT, PRINTED |
| 4 | IPSJ 36239 (SIG-DPS 31-1, Sept 1986) | 2.50 screen: menu, prompts, transcript, CLASS NAME pop-up | SCREENSHOT |
| 5 | TM-181 p4, TM-143 p3, TM-229 p6, TM-134 p71, Giho 8609 p16 | 1.x and 2.x menus and transcripts | SCREENSHOT |
| 6 | TM-785 p3, TM-786 p4-5 (Aug 1989, SIMPOS 5.0 screens) | Execute / `Command>fdd("x.com")`, FDD dialogue, error window, Really? | SCREENSHOT, PROSE |
| 7 | ICOT museum video (simpos.wmv, esp.wmv) | 9-item menu, `File Name>` dialogue | SCREENSHOT |
| 8 | IFS INSTALL files, login.com, command files (`*.com`) | menu paths users followed; command-file vocabulary | PROSE, USAGE |
| 9 | ESP manual TeX (1990), TM-388 pp92-105 | packages, environments, macro banks | PROSE |
| 10 | TR-057 p10, TM-143 p4, Giho 8810 | source/template/object model, compiler as subroutine | PROSE |

The second sweep of all held material (`sweep_2026-11-24.md`) found **no further Librarian source**. None of the
natures the cil copy names but does not define (§2.3) is defined anywhere held. It found SIMPOS's `pathname`/`name`
classes (§3.8). It also found manual titles: the 8.0 editions of the programming and ESP manuals (ICOT 1992),
and 「PSI/SIMPOS 操作説明書(I)-(III)」 (1988). None is held.

### 0.4 The cil copy (COPY grade): what it is and how far to trust it

`cil/src/ds_bep.esp` contains three classes. They are SIMPOS Librarian source, re-catalogued into
cil's package `spec_ds` (the class is used as `#spec_ds##library_utility`, ds_bep.esp:68). The
evidence:

| evidence | location |
|---|---|
| Comment: "patch class for library_utility on SIMPOS 6.1" | ds_bep.esp:1774 |
| File header: "merge patch class for library_utility", 91.1.28, by T.S. | ds_bep.esp:45 |
| PMACS edit stamp `>sys>user>yasuko>UT.esp.2, 29-Jul-88` before `class library_utility` | ds_bep.esp:3122 |
| Stamp `>sys>user>yasuko>GEN.esp.6, 28-Jul-88` before `librarian_class_generator` | ds_bep.esp:1776 |
| Before `librarian_read_term`: `icpsi123::>sys>user>soft>librarian>READ.esp.7` (26-Feb-88) and the DEC-20 file `<M-KONDOH.LIBRARIAN>ZREAD.ESP.79` (2-Jul-86) | ds_bep.esp:2327-2329 |
| Dated change comments 88/11/17 to 90/9/20, naming V4.0, V5.0, V6.0 and V6.11 | ds_bep.esp:1967, 2369, 2398, 3035 |
| Author link: "yasuko" is very probably 児玉泰子 (Kodama Yasuko), Mitsubishi, author of the 1990 Librarian customization paper | IPSJ 118681 p1 (INFERENCE) |

Trust:
- The class structure, slot list, messages and algorithms are SIMPOS's, as of 6.1 / V6.11
  (1990).
- cil's own patches cannot be told apart from SIMPOS code line by line.
- The one visible patch is that `compile/2`, `uncompile/2`, `abolish_interpretive_code/2` and
  `abolish_compiled_code/2` are empty stubs (ds_bep.esp:3358-3361). Treat those four as cil's
  doing, not SIMPOS's behaviour (INFERENCE).
- The natures that the copy references are **not** in cil. These are `librarian_version`,
  `librarian_delete`, `librarian_package`, `librarian_spy`, `librarian_reference`,
  `librarian_fdd`, `librarian_subroutine`, `as_assert_utility`, `librarian_catalogue`,
  `as_class_maker` and `compiler_error_reporter`. Every method that would come from them is
  UNSPECIFIED except for what the call sites show.

**Correction to required/NOTES.md**: the copy's package is `spec_ds`, not "spec_ms, esp_call, kl0"
(that is right only for `builtin`) (notes: ifs_libshell §4.1).

### 0.5 Versions

| version | date | Librarian evidence |
|---|---|---|
| 1.0 / 1.x | 1985 | prompt dialogue in `<< Librarian Text >>`; 12-item menu (TM-134 p71, TM-143 p3) |
| ~2.0 | Apr 1986 | `librarian_1`, 8+ items visible (Giho 8609 p16) |
| 2.10 | Jun 1986 | 9 items (TM-181 p4) |
| 2.50 | Sep 1986 | 9 items, `File Name>` / `Class Name>` prompts, CLASS NAME pop-up (IPSJ 36239 p5) |
| 4.0 | 1988 | `V4.0` changes in the copy; package resolution in `check_package` |
| 5.0 | 1988-89 | customization, init-file `menu_list`, 11-item top menu with submenus (IPSJ 118681); window title `librarian N ( default: pkg )`; Execute + `fdd("x.com")` (TM-785/786) |
| 6.0 / 6.1 / 6.11 | 1989-90 | the cil copy (remote and FDD catalogue, term-list catalogue since V6.11) |
| 7.x, 8.x, A22 | 1991-93 | held programs (papyrus, kappa2, cil, utter ...); no Librarian screen held |
| (A00) | ? | esp.wmv status line "SIMPOS Version A00" with the 9-item 2.x menu (notes: video §1) |

The held programs ran SIMPOS 3.0-7.1/A22 (notes: ifs_libshell §0). **Where sources conflict,
this spec follows the held programs and the 5.0+ evidence (cil copy, IPSJ 118681, TM-785), and
lists the 1.x/2.x forms as variants.**

---------------------------------------------------------------------------------------------------

## 1. Structure

### 1.1 The parts

IPSJ 118681 p2 Fig.4 (PRINTED figure) splits the Librarian into three parts:
- the **command execution part** (コマンド実行部);
- the **program interface part** (プログラム・インタフェース部), which does the work by calling the
  **library system**;
- the **I/O part** (入出力部), which calls the **window system**.

Replacing the I/O part replaces the windows and menus. Other subsystems can use the program
interface part alone (PROSE, TRANSLATION).

Mapped onto classes (INFERENCE, from the cil copy and the sends):

| part (Fig.4) | class(es) | evidence |
|---|---|---|
| library system | `library`: a class used only through class methods (`#library`); the registry of classes, templates, packages and environments | 46 class methods sent, 0 instance (coverage_librarian.tsv); TM-146 p5 PROSE |
| program interface part | `library_utility` and its natures (`librarian_*`, `as_assert_utility`) | COPY; IPSJ 118681 "part classes" (部品クラス) |
| command execution part | `library_utility:command/2` (the command-list interpreter) plus the menu reader | COPY ds_bep.esp:3381-3411 |
| I/O part | `librarian_io` (its `text` slot is the output pane), `librarian_menu` (`simpos##librarian_menu`, builds pop-up menus), the window classes `standard_io_window` / `pmacs_window` | COPY ds_bep.esp:1845-1856, 3189-3203, 3339-3349 |
| the program on the system menu | target atom `librarian` in every held login.com | USAGE disc/login.com:6-12, kappa2/kappa2/login.com:12-18 |

### 1.2 Class hierarchy

```
library                          (class methods only; no held instance)
library_utility                  natures, in order (COPY ds_bep.esp:3125-3133):
    librarian_version, librarian_class_generator, librarian_delete,
    librarian_package, librarian_spy, librarian_reference,
    librarian_fdd, librarian_subroutine, as_assert_utility
  librarian_class_generator      nature librarian_read_term          (ds_bep.esp:1777)
    librarian_read_term          natures librarian_catalogue, as_class_maker,
                                         compiler_error_reporter      (ds_bep.esp:2331)
librarian_io                     I/O object with slot `text`          (ds_bep.esp:3192)
librarian_menu                   simpos##librarian_menu; :create_menu_for_save/2, :read_items/4
library_error                    raised with :raise(#library_error,_,_,String)
esp_macro_expander               macro expander: :new/2, :expand_goals/3 (+ TM-388 :expand_clause/5)
esp_macro_expander_for_compiler  the default macro class for cataloguing; nature of every
                                 compiled macro bank in the held .ptf (88 records)
macro_preprocessor, esp_compiler, kl0_compiler, esp_operator_pool,
as_esp_parser, as_esp_unparser, syntax_error            compiler side
fdd_volume, fdd_volume_utility, fdd_binary_file, fdd_binary_file_tap,
fdd_multi_volume, file_backup                           floppy side
frozen_term, version, undefined_method                  utilities the partition carries
```

**Combination constraints** (COPY and USAGE):
- A user class may take `library_utility` as a nature.
  - papyrus's `papyrus_library` does so (papyrus_src/demo/DATA_BASE/library.esp.1:5-8). It then
    sends `:check/3`, `:make_package/3`, `:catalogue/3` and `:string_to_term/3` to itself.
  - The required set's "self-inherited>single-nature" rows come from this.
- `create/2` of `library_utility` uses `:new(Class,UT)`, so a subclass gets an instance of itself
  (COPY ds_bep.esp:3138).
- The copy's natures shadow simpos classes of the same name only because own-package classes are
  found first (ESP package rule, §1.4). A stand-in should define `library_utility` in `simpos`
  with all its natures. The nature list above is the 6.1 order.

### 1.3 Source, template, object

| form | what | where | grade, source |
|---|---|---|---|
| class source | ESP text; 2.50+ may hold several classes per file (`demo.esp` = 7 classes) | user files | SCREENSHOT IPSJ 36239 p5. VARIANT: TR-057 p10 (1984 design): one class per source file |
| class template | per-class info: slots, method and local-predicate code, inherited and referenced class names; the "object module" | in memory; saved to a **template file** | PROSE IPSJ 36239 §4(6), Giho 8810 Table 1 |
| template file path | `>sys>library>Package_name>template>Class_name.template` | | COPY ds_bep.esp:2364-2378 comment (V5.0, "for auto catalogue") |
| class object | built from templates along inheritance by the "object composer" (linkage editor); the "load module" | in memory only | PROSE Giho 8810 p46 Fig.7 |
| package template file | a package's class templates in one file, `.ptf` | anywhere; loaded with `load_package_template` | USAGE gog-esp/CGS_INSTALLER.esp:381; format: `../layers/FORMATS.md` |
| package environment file | `.env` | loaded with `load_environment_for_package_template` | USAGE gog-esp/CGS_INSTALLER.esp:379, 374-376 (`cgs_env.env`) |
| source registration | on catalogue the library records which file and version a class came from, unless `source_file_mode` is off | | COPY ds_bep.esp:2989-3006; PROSE ESP overview (1990) |
| code kinds | interpretive and direct-execution (compiled), chosen per class | | PROSE TM-181 p4, IPSJ 36239 §4(6) |

**Rebuild rule** (TM-143 p4, PROSE; repo STRUCTURE.md §9):
- Changing methods, demons or slots re-registers every inheriting class.
- A local-predicate change re-registers only that class.
- Referencing classes are not rebuilt.
- Related classes are auto-loaded; the transcript line is `<class> auto loaded.` (Giho 8609
  p16 SCREENSHOT).

### 1.4 Packages and environments

Normative statements, PROSE: ESP manual TeX program-e.tex:5250-5934 (1990); TM-388 pp92-101.

- **Package.** A package is a class-name space, generated by the Librarian. Its name is an atom,
  unique in the system. Class names are unique within a package.
- **Environment.** A package has at most one package environment, fixed when the package is
  made. An environment inherits packages and other environments, in order.
  - The usual environment is `with_simpos`, which inherits `simpos`.
  - The 1990 manual calls the standard environment `simpos` itself.
  - The held code uses both `simpos` and `cgs_env` as environment names: cil/src/INSTALL.esp:228
    and gog-esp/cgscmp.com:2-4.
- **Lookup of a bare class name.**
  1. The own package.
  2. Classes **externally declared** (外部宣言, public) in packages that the environment
     inherits, earlier inheritance first.
  3. If neither applies, `Pkg##Class` is needed.

  TM-388 p95 Fig. (PRINTED) gives a worked example (notes: trtm_progsys "TM-388 p95").
- **External declaration.** It is made "by operating the SIMPOS librarian and performing a library
  method call" (TM-388 p95). The method that does this is not identified. Candidates:
  `define_public_classes/2` on `#library` (COPY ds_bep.esp:1961), and the package-menu item
  "Define package". cal's INSTALL asks the user to "Set the following classes as public class
  using librarian" (cal-esp/INSTALL:32-33, PROSE).
- **Static binding.**
  - Names bind at catalogue time.
  - Cataloguing a class that refers to a not-yet-catalogued class registers only the referent's
    **name**. These are "name-only" classes; compare `#library:is_name_only_class/3`.
  - Order therefore matters, which is why command files catalogue macro banks first
    (program-e.tex:5688-5932; USAGE gog-esp/cgscmp.com).
- **`use_package(P)`** in a source file sets the package for the following classes of that file
  only (COPY ds_bep.esp:2808-2810; TM-388 p103). With none, the process's default package is used.
- **Default package per process.**
  - Read with `:get_package(Process,P)`, set with `:set_package(Process,P)`.
  - The Librarian title shows it: `librarian 49 ( default: user )` (IPSJ 118681 p1 Fig.1).
  - When `check_package` substitutes a package, the copy retitles the output window and resets
    the process package (COPY ds_bep.esp:3023-3040).
- **Login.** The `package :- Name.` clause of login.com sets the user's default package at login
  (USAGE disc/login.com:57 and others; shell spec).

---------------------------------------------------------------------------------------------------

## 2. Classes and methods

Each table lists every method the held programs require (coverage_librarian.tsv: class, kind,
arity, uses / programs), plus the methods the cil copy defines. Status values:
- **UNSPECIFIED**: no evidence beyond the call shape.
- **UNSPECIFIED (shape)**: the arguments can be read from the call site, but not the semantics.

### 2.1 `library` (the registry; class methods only)

Receiver `#library` in every case. No held program creates an instance. Grades are USAGE unless
COPY (sent from the cil copy) is stated. The order is: lifecycle, lookup, catalogue internals,
then debugger-only.

**Binding and lookup**

| method | uses/progs | arguments and meaning | grade | citation |
|---|---|---|---|---|
| assign/1 | 35/6 | `:assign(#library)`. Sent before a lookup sequence, by `library_utility:create/2` and by installers. Meaning unknown: binds the library for the current process (INFERENCE). Stand-in: succeed | USAGE, COPY | kappa2/kappa2/utility/tool/LOADER.ESP:160-163; cil/src/INSTALL.esp:44; ds_bep.esp:3155; pimfep, pimmcsp (ptf) |
| get_class_object/3 | 160/11 | `(#library, Name, ^ClassObj)`. Name is an atom `c`, a quoted atom `'pkg##c'`, or the term `##(Pkg,C)`. Resolves by the package rules of §1.4 and **loads on demand** (INFERENCE: the cal and cgs code call it straight after catalogue). Fails if absent | USAGE | cal-esp/cal2.12/control.esp:224; gog-esp/CGS_INSTALLER.esp:362 (`'cgs##cgs_main'`); pimfep (ptf) `##(pimfep,fep_message_assembler)` |
| make_class_object/2 | 28/5 | `(#library, ClassId)`. Builds (loads) the class object from its template / template file | USAGE | cil/src/INSTALL.esp:249; ptf: after `check_info(...,template_file)` |
| check_info/3 | 33/5 | `(#library, ClassId, Kind)`, Kind ∈ {`object`, `template`, `template_file`}. Succeeds if that form exists. `object` = loaded | USAGE, COPY | LOADER.ESP:170 (`object`); pimscsi_fep (ptf) (`template_file`); ds_bep.esp (all three) |
| check_class_id/3 | 11/3 | `(#library, Name, ^Info)`. `Info is 0` = not loaded (cal-esp/deb2.12/purs.esp:420-422). cil comment: "8 =< Info means loaded" (cil/src/ms_cdn.esp:69-74). INFERENCE: Info is a state code, 0 = unknown | USAGE | as cited |
| get_class_id/5 | 17/3 | `(#library, Package, ClassName, ^ClassId, _)` | USAGE | cal-esp/deb2.12/init.esp:960; kappa2/kappa2/kernel/hlc/HLCLIB.ESP:92 |
| get_class_id/6 | 1/1 | one more output than /5. UNSPECIFIED (shape) | COPY | ds_bep.esp:1921 |
| get_class_id_in_package/6 | 2/2 | lookup restricted to one package. UNSPECIFIED (shape) | COPY, USAGE | ds_bep.esp:2720; kwic-esp |
| get_class_id_in_environment/6 | 2/1 | lookup through a package's environment. UNSPECIFIED (shape) | COPY | ds_bep.esp:2828 |
| get_exist_class/4 | 1/1 | `(#library, ClassId, _, ^Descriptor)`. The Descriptor answers `:check_info(D,template)` | USAGE | cal-esp/deb2.12/pmod.esp:532-533 |
| get_class_descriptor/6 | 3/1 | `(#library, C, _, _, ^Id, ^CD)`. CD takes `:check_info(CD,template)` and `write_class_template` (§2.2 save) | COPY | ds_bep.esp:1976, 2060-2107 |
| is_name_only_class/3 | 2/1 | true for a preliminary (name-only) registration (§1.4). UNSPECIFIED (shape) | COPY | ds_bep.esp:1981 |
| is_ipl_class_object/2 | 2/1 | `(#library, ClassId)`. True for classes in the IPL (system) image; the CAL debugger skips them | USAGE | cal-esp/deb2.12/pmod.esp:387 |
| get_names/4 | 1/1 | UNSPECIFIED (shape) | COPY | ds_bep.esp:3059 |
| get_version/6 | 1/1 | `(#library, ClassName, _,_,_,_)`. Succeeds if the class is registered (the HLC compiler's test) | USAGE | HLCLIB.ESP:90 |
| get_direct_superclasses/3 | 2/2 | `(#library, ClassId, ^[Self|Supers])`. The first element is the class itself (pmod.esp:404-405 drops it) | USAGE | cal-esp/deb2.12/pmod.esp:404 |
| get_direct_referred_classes/3 | 1/1 | `(#library, ClassId, ^Ids)`. Classes the class references | USAGE | pmod.esp:410 |
| get_changed_classes/2 | 1/1 | `(#library, ^Ids)`. Classes changed since their last save. Drives "save changed classes" | COPY | ds_bep.esp:1841 |
| get_predicates/4 | ptf only | `(#library, #character, c, [to_hankaku|_])`. A class's predicates, selected by a name list (not in requirements.tsv) | USAGE | pmacs_window_process half_size/1 (ptf, pimmcsp/mpsicsp) |
| get_predicates_with_information/4, get_all_predicates_with_information/4 | 1/1 each | UNSPECIFIED (shape) | USAGE | cil/src/ms_mdm.esp:2131-2133 |
| get_a_code/7 | 11/3 | `(#library, ##(Pkg,Class), l, [], Functor, Arity, ^Code)`. The code of one local (`l`) predicate | USAGE | cal-esp/deb2.12/purs.esp:153 |
| get_a_name/8 | 2/2 | `(#library, Id, ^Class, ^Ca, ^Ty, ^Na, ^Ar, _)`. The reverse map from a code id to class, category, type, name and arity | USAGE | cal-esp/deb2.12/output.esp:605 |
| stick_predicate_tap/2 | 1/1 | `(#library, ^Tap)`. A tap (iterator) over predicates | USAGE | pmod.esp:516 |
| set_error_mode/1, reset_error_mode/1 | 1/1 each | library error reporting on and off (the CAL debugger's `library_error_mode(on|off)`) | USAGE | cal-esp/deb2.12/purs.esp:525-526 |

**Packages**

| method | uses/progs | arguments and meaning | grade | citation |
|---|---|---|---|---|
| check_package/2 | 13/3 | `(#library, P)`. Package P exists | USAGE, COPY | cal-esp/deb2.12/init.esp:974; ds_bep.esp:3150 |
| check_package/3 | 5/1 | `(#library, P0, ^P)`. The package actually used for P0; may differ (substitution: the title and process package are reset) | COPY | ds_bep.esp:2809, 3027 |
| make_package/2 | 3/2 | `(#library, P)`. Create a package; the environment is set next | USAGE | cil/src/INSTALL.esp:225-228 |
| make_package_forcedly/2 | 1/1 | create, replacing an existing package (INFERENCE) | USAGE | cil/src/ms_ist.esp:857 |
| change_environment_in_package/3 | 2/1 | `(#library, P, Env)`, e.g. `simpos` | USAGE | INSTALL.esp:228 |
| delete_package/2 | 2/1 | `(#library, P)` | USAGE | ms_ist.esp:858 |
| delete_package_forcedly/2 | 1/1 | delete even if not empty (INFERENCE) | USAGE | gog-esp/CGS_INSTALLER.esp:374 |
| delete_environment_forcedly/2 | 1/1 | `(#library, Env)` | USAGE | CGS_INSTALLER.esp:376 |
| save_package_template/3 | 1/1 | `(#library, Package, PtfPath)`. Write the package's templates as one file | USAGE | ms_ist.esp:388 |
| load_package_template/3 | 1/1 | `(#library, Package, PtfPath)` | USAGE | ms_ist.esp:859 |
| define_public_classes/2 | 1/1 | `(#library, Ids)`. Make the classes external (public), "load_all_and_public" | COPY | ds_bep.esp:1945-1962 |

**Catalogue internals** (used by the copy's catalogue, §2.2)

| method | uses/progs | arguments and meaning | grade | citation |
|---|---|---|---|---|
| catalogue_class/2 | 1/1 | `(#library, '##'(Pkg,Name))`. Register a new class name | COPY | ds_bep.esp:2723 |
| make_class_template_from_internal_format/4 | 1/1 | `(#library, Name, ExpandedDef, Version)`. Build the template from macro-expanded source; Version = `:now(#date_time,V)` | COPY | ds_bep.esp:2867 |
| make_class_template_from_source/3 | 1/1 | `(#library, ProgTerm, ^ClassId)`. Build from a **term** (HLC generates ESP terms) | USAGE | HLCLIB.ESP:94 |
| make_class_template/2 | 1/1 | `(#library, ClassName)`. Rebuild the template from the template file | USAGE, COPY | HLCLIB.ESP:91; ds_bep.esp load path |
| write_class_template/2 | 2/2 | `(#library, ClassId)`. Write the template file | USAGE | HLCLIB.ESP:95; cil/src/ms_mdm.esp:1954 |
| update_class_source_file/4 | 1/1 | `(#library, C, File, Version)`. Record the source file (§1.3) | COPY | ds_bep.esp:3003 |
| abolish_class_object/2 | 1/1 | discard a class object before rebuilding | COPY | ds_bep.esp:2729 |
| abolish/2 | 2/1 | abolish the classes read so far, on catalogue error | COPY | ds_bep.esp:1995, 2426-2429 |
| register/2 | 2/1 | `(#library, [Id])`. Register without compiling | COPY | ds_bep.esp:2127 |
| delete/2 | 2/2 | `(#library, ClassId)`. Delete a class | USAGE | cil/src/ms_mdm.esp:1960 |

### 2.2 `library_utility`: the programmatic Librarian

`:create(#library_utility,U)` gives an object with no window. Messages go nowhere until
`:set_output(U,W)` is called. A user class may also inherit it (§1.2).

**Slots** (COPY ds_bep.esp:3170-3177)
- `standard_output := not_defined`
- `text_window := not_defined`
- `flash_flag := off`
- `package`
- `name` ("login user name (key of dispol)")
- `library_environment` (a `monogyny_list_index`; the modes)
- `yank_on_off := off`
- `debug_flag := off`

Also used: `process` (set by create), `response_time_flag`, `skipped_classes` and `subclass_check`
(inherited).

**Class methods**

| method | uses/progs | meaning | grade | citation |
|---|---|---|---|---|
| create/2 | 48/11 | `(Class, ^UT)`. The steps, in order: `:new`; store the process; name = the login user's local name (`simpos` → `me`); assign the named yank buffers `class`, `file`, `package`; package = the process package if `:check_package(#library,P)`, else `simpos`; `:assign(#library)` | COPY; USAGE everywhere | ds_bep.esp:3136-3155 |
| create/3 | (copy) | `(Class, ^UT, W)`. Create/2, then `:create_window(UT,W)` | COPY | ds_bep.esp:3160-3162 |
| assert/3, asserta/3, assertz/3 | 79/3, 2/2, 54/3 | `(#library_utility, DbClassName, Clause)`. Add a clause to a **catalogued class** used as a database. The class is made by cataloguing a term such as `class C with_macro macro_data has local end` (cal) or a generated `class Name has :data(_,L,R):- ...` (papyrus). The clause is passed quoted with `` `` `` in papyrus. Owner nature: `as_assert_utility` (INFERENCE) | USAGE | cal-esp/cal2.12/graph.esp:88-93, 176; papyrus_src/demo/DATA_BASE/library.esp.1:191, 139-150; sum/src/main.wkm:82 |
| retract/3 | 76/4 | `(#library_utility, DbClassName, Clause)` | USAGE | graph.esp:215; library.esp.1:198 |
| retract_all/4 | 76/4 | `(#library_utility, DbClassName, Functor, Arity)`, e.g. `node, 2`. CESP renamed it `abolish/4` (IPSJ 122601 p2 §4.2) | USAGE | graph.esp:237; library.esp.1:23 |

Asserted clauses live in class templates. This is why the Librarian's save offers to "save all
asserted predicates" (sum/INSTALL:26-29, PROSE; INFERENCE).

**A second, class-id form** (USAGE; `fixpoint_2026-11-24.md` round 1, `notes/fixpoint.tsv`).
examds's `wb_lib` (a Prolog-style assert/listing library for its workbench, 1992) calls the same
class methods with a **class id** from `:class_id(Class,^Id)` instead of a class name:
- `assert/4`, `asserta/4`, `assertz/4` as `(#library_utility, ClassId, Clause, ^Ref)`, returning a
  clause reference (`examds/examds/wb_lib/astret.esp:11-23`);
- `retract/3` `(#library_utility, ClassId, Clause)` and `retract_all/4` `(.., ClassId, Name, Arity)`
  (`:26-33`);
- `clause/4` `(#library_utility, ClassId, Head, ^Body)` (`wb_lib/clause.esp:16`).
To clear a class, `wb_lib` maps `retract_all/4` over `:get_predicates_with_information(#library,
Id, l, ^List)`, whose elements are `{Name, Arity, Category, Code}` (`astret.esp:34-44`); its listing
reads one predicate with `:get_a_code(#library, Id, l, _, Name, Arity, ^Code)` (`wb_lib/listing.esp`).
So the asserted clauses are the class's **local** predicates (category `l`). This bears on gap rank 5
(storage); persistence is still open.

**Instance methods required by held programs**

| method | uses/progs | arguments and meaning | grade | citation |
|---|---|---|---|---|
| load/2 | 18/6 | `(UT, ClassIds)`. Rebuild the class objects from the template files. Prints `Loading <id>...` per class (or `Remote loading <id>...` when the process `node_name` is not `"my_node"`). Each class runs under `:catch(Process,"Skip this class",#library,make_class_template,{Id})`. Errors are printed (§6) | COPY; USAGE | ds_bep.esp:1829-1831, 1967-2012; LOADER.ESP:196; sum/src/main.wkm:69 |
| catalogue/3 | 15/7 | `(UT, Sources, ^ClassIds)`. Sources is a list of path strings (wildcards allowed), **or since V6.11 class terms, or term lists** (e.g. `[use_package(P), Term]`). Reads, macro-expands, makes templates and objects, registers the source, and pushes the ids to the `class` yank buffer. Algorithm in §5.4 | COPY; USAGE | ds_bep.esp:1805-1809, 2398-2400, 2593-2613; cil/src/INSTALL.esp:232; graph.esp:93; library.esp.1:139 |
| catalogue/2, catalogue/4 | (copy) | /2 drops the ids. /4 is `(UT, Paths, Options, ^Ids)`: Option `save` saves afterwards; `compile`, `compiled` and `check_subclass` are accepted and do nothing (6.1) | COPY | ds_bep.esp:1799-1816, 2046-2055 |
| save/2 | 8/4 | `(UT, ClassIds)`. Write each class's template file: `Saving <id>...` then ` end.` | COPY; USAGE | ds_bep.esp:1836-1838, 2060-2107; cil/src/INSTALL.esp:233; sum main.wkm:143 |
| set_package/2, get_package/2 | 8/2, 5/2 | `(UT, Pkg)`: the package used for catalogue / load. get_package reads `:get_package(Process,P0)` through `check_package/3` | COPY; USAGE | ds_bep.esp:3240-3243; CGS_INSTALLER.esp:341, 345 |
| set_output/2 | 4/3 | `(UT, Out)`. If Out's class is `#librarian_io`, then text_window = `Out!text` and flash on. Otherwise text_window = Out, and flash on iff Out has `flash/1` | COPY; USAGE | ds_bep.esp:3189-3203; CGS_INSTALLER.esp:343; kwic dbDM.esp:1127 |
| remove_output/1 | 7/3 | unset output and text window; flash off | COPY; USAGE | ds_bep.esp:3204-3207 |
| delete/2 | 3/2 | `(UT, ClassIds)`. Delete classes from the library. Owner `librarian_delete` (INFERENCE) | USAGE; Fig.2 command `delete` | kwic-esp-002/kwic-esp/src/dbDM.esp:1132 |
| get_classes_with_wildcard/5 | 1/1 | `(UT, Package, WildcardString, all, ^Ids)`, e.g. `"name*"` | USAGE | dbDM.esp:1131 |
| get_class_names/4 | 2/1 | `(UT, Package, all, ^Ids)`. All class names of a package | USAGE | papyrus_src/demo/DATA_BASE/manipulator.esp.1:754 |
| get_packages_with_wildcard/3 | 2/1 | `(UT, WildcardString, ^Pkgs)`. Package names matching a pattern such as `"*_type"` | USAGE | manipulator.esp.1:727 |
| get_class_id_atom_list/4 | 2/1 | `(UT, NameString, '$$local', ^Ids)`. Ids of the classes whose name matches the string, in the local package (INFERENCE on `'$$local'`) | USAGE | sum/src/main.wkm:68, 142 |
| get_direct_superclasses/3 | 3/2 | `(UT, Pkg##Class, ^[Self|Natures])`. Also used as an existence test for a package's class | USAGE | CGS_INSTALLER.esp:371; library.esp.1:205 |
| check/3 | 3/1 | `(UT, [ClassId], ^[InfoList])`. The data behind the **Check** command (§5.5). InfoList is a list of `{LabelString, Status}`, labels padded to 9 characters (`"object   "`, `"  file   "`), Status `none` or a value | USAGE | library.esp.1:86-101; matches TM-181 p4 Check output |
| make_package/3 | 2/1 | `(UT, Package, Env)`, e.g. `simpos`. Create a package with its environment | USAGE | library.esp.1:138, 144 |
| delete_package/2 | 1/1 | `(UT, Package)`, after deleting its classes | USAGE | manipulator.esp.1:830 |
| save_package_template/3 | 1/1 | `(UT, Package, FileName)`: write a `.ptf` | USAGE | manipulator.esp.1:685 |
| load_package_template/3 | 1/1 | `(UT, Package, PtfPath)` | USAGE | CGS_INSTALLER.esp:381 |
| load_environment_for_package_template/3 | 1/1 | `(UT, Env, EnvPath)`: load a `.env` before the `.ptf` | USAGE | CGS_INSTALLER.esp:379 |
| string_to_term/3 | 1/1 | `(UT, String, ^Term)`. Parse with the ESP reader | USAGE | library.esp.1:258 |

**Further instance methods of the 6.1 copy** (COPY; not sent by held programs, except where a
row's citation says otherwise)

| method | summary | citation |
|---|---|---|
| command/2 | the command-list interpreter, §5.2 | ds_bep.esp:3182, 3381-3411 |
| register/2,3 | read class names without compiling, then `:register(#library,[Id])`; prints `class <Id>...`, then `   <Id> end.` or `   <Id> fail.` | :1818-1827, 2124-2133 |
| save_changed_classes/1 | `get_changed_classes`, then save | :1840-1843 |
| save_non_saved_classes/1 | pop-up save menu built by `simpos##librarian_menu` (`create_menu_for_save/2`, `set_position(M,350,250)`, `activate(M,mouse)`, `read_items/4`), then save; with no `librarian_menu` raises library_error (§6) | :1845-1856 |
| get_classes_from_source/3 | per file prints `- <path> -` and the ids; FDD files are read whole through `fdd_binary_file` | :1858-1862, 2139-2192 |
| read_and_get/5, close_and_get/4, get_temp_list/3 | helpers | :1864-1871 |
| read_term_and_catalogue/3, catalogue_remote_or_fdd/5, catalogue_by_tap/6, close_and_abolish/3, set_operators/4, special_terms/4 | catalogue internals (librarian_read_term) | :2398-2461 |
| reset_output/2, set_name/2, get_name/2, check_window_object/2 | output and name bookkeeping | :3208-3223 |
| set_mode/1 | copy the process's `catalogue_mode`, `error_mode`, `skip_mode`, `source_file_mode` into `library_environment` | :3225-3226, 3368-3376 |
| set_mode/3, get_mode/3 | `:set/get_library_environment(Process,Name,Mode)` | :3228-3238 |
| message/2,3,4, writef/3, writet/2 | to text_window, with flash and abort polling | :3245-3261 |
| putl/2,3,4, putf/3, putt/2 | to standard_output | :3263-3276 |
| display_text_window/6, response_time/5, display_response_time/6, set_response_time_flag/2 | timing display (§3.6) | :3279-3337 |
| get_library_utility/2 | returns itself ("dummy") | :3335 |
| create_window/2 | `standard_io_window [size(manipulator),permission(out),position(manipulator)]`, show, set_output | :3339-3343 |
| create_pmacs_window/2 | `pmacs_window [size(manipulator),position(manipulator)]`, activate, set_output | :3345-3349 |
| check_subclass/2 | | :3351-3352 |
| compile/2, uncompile/2, abolish_interpretive_code/2, abolish_compiled_code/2 | **stubs in the copy** (§0.4). The real ones switch between interpretive and compiled code (TM-181 p4 PROSE) | :3358-3361 |

**Methods the copy calls on itself that must come from the unheld natures** (COPY
ds_bep.esp:2331-3121): `make_all_classes/2,3`, `add_class_name/2`, `add_class_names/2`,
`add_file_name/2`, `add_discordant_class/2`, `remove_discordant_class/2`,
`get_package_and_class/4`, `term_to_string/3`, `zero_position/4`, `mumble/3`, `new/2`, `refute/3`.
All are UNSPECIFIED. `mumble/3` is evidently a formatted message (`"... :\n\q",[Term]`).

**Methods implied by command-file items**: see §5.2. These include `fxds/2`,
`make_environment/3`, `save_environment/2`, `save_package/2`, `use_package/2`,
`save_all_classes/1`, `refute/2` and `fdd/2`. All are UNSPECIFIED, with the owner nature as
INFERENCE.

### 2.3 Mixins: `librarian_*`, `as_assert_utility`, `librarian_catalogue`, `as_class_maker`, `compiler_error_reporter`

None is held. Each appears as one `nature` row (cil, ds_bep.esp:3123, 2331). What each probably
supplies, by name and by the calls the copy makes (all INFERENCE):

| mixin | probable content |
|---|---|
| librarian_version | version and timestamp handling (`:now(#date_time,V)` versions, the V5.0 auto-catalogue) |
| librarian_class_generator | HELD (COPY): catalogue/2,3,4, register/2,3, load/2, save/2, save_changed/non_saved, get_classes_from_source/3 |
| librarian_read_term | HELD (COPY): class methods `make_class_template_from_source/3`, `make_class_template_from_catalogued/4`, `make_class_template_for_auto_catalogue/4`; read_term_and_catalogue/3 and the catalogue algorithm |
| librarian_delete | delete/2, abolish, forget, delete_resource (the Fig.2 Delete submenu) |
| librarian_package | make_package/3, delete_package/2, set/get_package, environments, package templates, `make_environment`, `use_package`, `save_package` |
| librarian_spy | spy points for the debugger |
| librarian_reference | get_direct_superclasses/3, get_class_names/4, wildcard searches, inheritance/reference views ("Utility") |
| librarian_fdd | floppy routes, `fdd/2` (the Execute `fdd("x.com")` command) |
| librarian_subroutine | `make_all_classes`, `add_*`, `mumble`, `term_to_string`, `string_to_term/3` |
| as_assert_utility | class-side assert/asserta/assertz/retract/retract_all |
| librarian_catalogue, as_class_maker, compiler_error_reporter | catalogue bookkeeping, `make_class` (bit 32 "make_class (as_class_maker)", ds_bep.esp:3288-3303), error reporting with the `Error found by esp_macro_expander:` header (TM-181 p5) |

### 2.4 The Librarian program, `librarian_io`, `librarian_menu`, `library_error`

| item | facts | grade | citation |
|---|---|---|---|
| `librarian` (system-menu target) | Item `{"librarian",librarian}` in the first column of every held login.com. Selecting it sweeps a window and starts a Librarian process | USAGE, PROSE | disc/login.com:6-12; utter/INSTALL:28-38 |
| process name | `librarian_59 ( process 59 )`: name `librarian_<n>`, n = process number (1989) | SCREENSHOT | TM-785 p3 |
| window name | `librarian_1`, `librarian_2` (1986): a per-program instance counter | SCREENSHOT | TM-181 p4; IPSJ 36239 p5; esp.wmv@117 |
| title (5.0+) | `librarian 49 ( default: user )`: process name plus default package. Built in the copy as `Lib_name + " ( default: " + Pkg + " )"` from `:get_name(Process,…)` | SCREENSHOT, COPY | IPSJ 118681 p1 Fig.1 (eyed at 600 dpi: "49"; Fig.3 "48"; `web_search_2026-11-24.md` reads "40", which the 600 dpi crop does not support); ds_bep.esp:3029-3036 |
| `librarian_io` | an I/O object whose `text` slot is the output pane (`UT!text_window := Output!text`) | COPY | ds_bep.esp:3192, 3222 |
| `librarian_menu` | `simpos##librarian_menu`; `:new`, `:create_menu_for_save(Obj,^Menu)`, `:read_items(Obj,Menu,^Ids,_)` | COPY | ds_bep.esp:1845-1856 |
| `library_error` | `:raise(#library_error,_,_,String)` (raise/4); the message string is the fourth argument | COPY | ds_bep.esp:1856 |

A process-name variant: the 1989 error window says `librarian_59`, while the 1990 title says
`librarian 49`. Both may be renderings of one name (INFERENCE). A stand-in should use
`librarian_<pno>` for the process and the error title, and `librarian <pno> ( default: <pkg> )`
for the window title.

### 2.5 Compiler side

| class | method | uses/progs | meaning | grade | citation |
|---|---|---|---|---|---|
| esp_macro_expander | new/2 | 16/4 | `:new(#esp_macro_expander,E)` | USAGE | gog-esp/CGS_INSTALLER.esp:232 |
| esp_macro_expander | expand_goals/3 | 36/4 | `(E, Goals0, ^Goals)`; also used to evaluate a read term (gog reads an install file and expands it) | USAGE; PRINTED-INTERFACE TM-388 p102-105 | cil/src/cil_esp.esp:160; CGS_INSTALLER.esp:233 |
| esp_macro_expander | expand_clause/5 | (manual) | PRINTED-INTERFACE | | TM-388 p102-105 |
| esp_macro_expander | expand_definition/5 | (copy, CAL) | `(MacroObj, Def, Pkg, Name, ^Expanded)` | COPY | ds_bep.esp:2703-2740; cal-esp/deb2.12/cm.esp:700 |
| esp_macro_expander_for_compiler | (nature) | 88 records | the copy's default macro class (`'simpos##esp_macro_expander_for_compiler'`, ds_bep.esp:3040). Every compiled macro bank in the held .ptf has it as a nature (ptf) | COPY, USAGE | notes: ptf §LIBRARIAN |
| macro_preprocessor | preprocess/3 | 1/1 | `(#macro_preprocessor, Def0, ^Def)` for `macro_bank` terms | COPY | ds_bep.esp:2667 |
| esp_compiler | compile/4 | 1/1 | `(#esp_compiler, ClassId, ExpandedDef, ^InternalFormat)`. InternalFormat is an 8-vector whose last element is the local-predicate list | USAGE | cal-esp/deb2.12/cm.esp:703-704 |
| kl0_compiler | compile_one_predicate/6 | 1/1 | `(#kl0_compiler, ClassId, from_debugger, LocalPred, ^Module, ^Code)`. "The compiler is simply a subroutine of the library subsystem. It compiles a single predicate" (TR-057 p10 PROSE) | USAGE | cm.esp:705 |
| esp_operator_pool | create/2 | 3/2 | `:create(#esp_operator_pool,P)`, then `:add_operator(P,Name,Type,Prec)` | USAGE | euod/BUP/bup.esp:333-336 |
| as_esp_parser | new/2; refute/3; gett/2,3,4 | 1/1 each | a nature giving an ESP reader over a string slot: `:refute(Obj,gett,Args)`, `:gett(Obj,^Term[,CVI[,NVI]])` (CVI/NVI: variable-name info, INFERENCE) | USAGE | kwic-esp-002/kwic-esp/src/functions.esp:383-455 |
| as_esp_unparser | new/2; refute/3; putt/2,3,4 | 1/1 each | the writer counterpart | USAGE | functions.esp:476-572 |
| syntax_error | (ref) | | raised on read errors | USAGE | cil/src/ds_fep.esp:968 |

**Macro-bank default conflict.**
- The 1990 manual: with no `use_macro`, "esp_macro expander" is assumed (program-e.tex:7721-7733,
  PROSE).
- The 6.1 copy: `simpos##esp_macro_expander_for_compiler`.
- Stand-in: use `esp_macro_expander_for_compiler` as the catalogue default, and make it a
  subclass of `esp_macro_expander` (INFERENCE).

### 2.6 Floppy, backup and utility classes of the partition

These are file-system classes. They are placed here because the Librarian's FDD routes use them.
All are USAGE.

| class | method | uses/progs | arguments and meaning | citation |
|---|---|---|---|---|
| fdd_volume | create/2 | 4/2 | `:create(#fdd_volume,V)` | cil/src/ms_ist.esp:1772 |
| fdd_volume | mount/3 | 7/2 | `(V, DeviceDir, Unit)`, with DeviceDir from `:retrieve(#directory,D,">device>fdd1")` and Unit 0 | ms_ist.esp:1774 |
| fdd_volume | link/2 | 3/2 | `(V, ">fd0")`: graft into the tree | ms_ist.esp:1775 |
| fdd_volume | dismount/1 | 16/2 | `(V)` | ms_ist.esp:1780; CGS_INSTALLER.esp:111 |
| fdd_volume | get_sub_info/2 | 6/2 | `(V, ^{_,_,FileCount,FreeSectors,_})`; a sector is 256 bytes, and cil allows up to 70 files | ms_ist.esp:1856-1859 |
| fdd_volume | file_names/2 | 3/2 | `(V, ^Names)` | ms_ist.esp:1922 |
| fdd_volume | get_physical_units/2 | 3/1 | `(#fdd_volume, ^Units)` | kappa2/kappa2/utility/bck/BCKCMN.ESP:471 |
| fdd_volume_utility | initialize/3 | 4/2 | `(#fdd_volume_utility, Unit, VolumeName)`, e.g. `0, "spec"`: format a floppy | ms_ist.esp:1769 |
| fdd_binary_file | open/3 | 3/2 | `(#fdd_binary_file, ^F, Path)` | ds_bep.esp:2163; BCKCMN.ESP:631 |
| fdd_binary_file | open/5 | 2/1 | `(#, ^F, Path, OpenMode, RequestMode)` | BCKFIF.ESP:1849 |
| fdd_binary_file | make/3, make/4 | 3/1, 1/1 | `(#, ^F, Path[, Sectors])` | BCKCMN.ESP:639; ms_ist.esp:1803 |
| fdd_binary_file | make_only/3, make_only/4 | 2/1, 1/1 | as make, without opening (INFERENCE) | BCKFIF.ESP:1821; kappa2/kappa2/utility/fmp/KFILMP.ESP:737 |
| fdd_binary_file_tap | create/3 | 6/1 | `(#, ^Tap, FileObj)` | BCKCMN.ESP:632 |
| fdd_binary_file_tap | read/2, write/2, at_end/1 | 5, 6, 2 | `(Tap, Buffer)`; at_end = end of file | BCKFIF.ESP:1883, 1899, 1972 |
| fdd_multi_volume | remove_at/3 | 1/1 | `(#superuser##fdd_multi_volume, _, ">file_backup")` | CGS_INSTALLER.esp:112 |
| file_backup | create/2; set_output/2; set_input/2; restore/3 | 1/1 each | `superuser##file_backup` (package `superuser`): `restore(B, Drive, Directory)` restores a floppy backup into the directory. Also the shell command `far` (kappa2/kappa2/login.com:89) | CGS_INSTALLER.esp:97-105 |
| frozen_term | freeze/3 | 18/3 | `(#frozen_term, Term, ^F)`; then `melt(F,^T)` | disc/conv.esp:331; knov/src/system/rule_net.esp:109 |
| version | version/2 | 1/1 | `(#version, ^String)`; values the kappa code tests: "2.5", "2.50", "2.52", "3.0", "3.1", "3.11", "3.12", "4.0", "4.0A", "4.0B" | kappa2/kappa2/kernel/flm/FILEM1.ESP:57-69 |
| undefined_method | raise/2 | ptf | `:raise(#undefined_method, ...)` | pimscsi (ptf) |

---------------------------------------------------------------------------------------------------

## 3. Data formats

### 3.1 Class and package names

| form | example | where | grade |
|---|---|---|---|
| bare atom | `cgs_main` | resolved by §1.4 | USAGE |
| quoted atom with `##` | `'cgs##cgs_main'`, `'superuser##file_backup'` | get_class_object/3; login.com shell_transient | USAGE |
| term `##(P,C)` (written `P##C`) | `##(pimfep,fep_message_assembler)` | get_class_object/3 (ptf); get_a_code/7 | USAGE |
| class object | `#c`, `#p##c` | | PROSE program-e.tex:5339-5389 |

### 3.2 check_info kinds and check/3 info list

- `check_info/3` takes the kind `object`, `template` or `template_file`. The first two are also
  sent to a class descriptor (USAGE, COPY).
- `check/3` returns, per class, a list of `{Label, Status}`. The labels are those of the Check
  screen (§5.5), padded to 9 characters: `"object   "`, `"  file   "` (USAGE library.esp.1:86-101).
  - INFERENCE: the full set is `"source   "`, `"template "`, `"  <kind> "`, `"  file   "`,
    `"object   "`, `"  <kind> "`, with Status `none` or a date.

### 3.3 Library environment (per-process modes)

| name | values | effect | grade, citation |
|---|---|---|---|
| catalogue_mode | ? | (copied into the utility by set_mode/1) | COPY ds_bep.esp:3368-3376 |
| error_mode | on / off | off holds the librarian error messages (installers turn it off) | USAGE cil/src/INSTALL.esp:47-48 |
| skip_mode | ? | INFERENCE: skip a failing class instead of asking | COPY |
| source_file_mode | on / off | off skips `update_class_source_file` | COPY ds_bep.esp:2989-3006 |
| node_name | `"my_node"` = local | otherwise load prints `Remote loading` | COPY ds_bep.esp:1969-1970 |

These are accessed with `:get_library_environment(Process,Name,^Mode)`,
`:set_library_environment(Process,Name,Mode)` and
`:check_library_environment(Process,Name,Value)` on `process` (shell spec).

### 3.4 Command-file term form

A command file holds **one list term**. `%` comments are allowed, including at the end of a line
(USAGE gog-esp/cgscmp.com; kappa2 `*.COM`).

Paths are strings, absolute (`">sys>user>cgs>source>utility>location.macro"`) or logical
(`"hlc:HLC.MAC"`). Logical names come from the user's login.com `define` clause, so kappa's files
work only as user `kappa` (PROSE kappa2/INSTALL:38).

Item vocabulary and meaning: §5.2.

### 3.5 Librarian initialization file: `menu_list`

IPSJ 118681 p2 Fig.2 (PRINTED, SIMPOS 5.0; the figure elides the end):
- `menu_list := [Item, ...]`.
- An item is `(Label, Command)` or `(Label, SubmenuName, [Item, ...])`.
- Label is a string. Command and SubmenuName are atoms.
- The command `up` returns to the parent menu.

| level | label | command |
|---|---|---|
| top | "Set up" | set_up_menu → { "Set up" set_up; "Save state" save_state; "Check menu item" check_menu_item } |
| top | "Check" | check |
| top | "Catalogue" | catalogue |
| top | "Save" | save |
| top | "Load" | load |
| top | "Delete" | delete_menu → { "Delete" delete; "Abolish" abolish; "Forget" forget; "Delete resource" delete_resource; " [Exit]" up } |
| top | (elided in Fig.2; Fig.1 shows Package, Execute, Utility, ESP tool, [Close]) | — |

How the file is used (PROSE, TRANSLATION, IPSJ 118681 p2 §4):
- The user edits the file and saves it; the next Librarian built gets the new menu.
- New commands come from a class that inherits the system Librarian classes plus a class defining
  the command (§7).
- The file's name and location are not given: see gaps. In 6.0 a choice among several init files
  was planned (§5 of the paper).

### 3.6 Response-time flag bits (COPY ds_bep.esp:3279-3303)

| bit | step timed | phase |
|---|---|---|
| 512 / 256 / 257 | predicate, slot, classes: menu on / menu off / menu off with output to file | |
| 128 | write_class_template | COM |
| 64 | make_class_template | COM |
| 32 | make_class (as_class_maker) | CAT |
| 16 | make_class_template_from_internal_format | READ |
| 8 | abolish_class_object | READ |
| 4 | catalogue_class | READ |
| 2 | expand_definition | READ |
| 1 | gett | READ |

The display (`display_text_window/6`) prints `- <Type> -`, `- Time: … -` and `- Heap: N words -`,
with ` hrs. ` / ` min. ` / ` sec. `.

### 3.7 Source-file terms accepted by catalogue (COPY ds_bep.esp:2239-2263, 2618-2876)

- Definitions:
  - `class Name [with_macro M] has ... end`
  - `macro_bank Name has ... end`
- Directives:
  - `add_operator(Op,Type,Prec)`, where Op may be a list
  - `remove_operator/1,2`
  - `use_macro(M)`: auto-loads M
  - `use_package(P)`
  - `include("f")`: resolved against the includer's directory, read once
  - `register(C1,C2,...)`: registers names only
- Anything else is "illegal" (§6).
- The operator pool is preloaded with `macro_bank fx 1180`, `with_macro xfx 1140`,
  `==> xfx/xf 1099` and `with fx/yfx 1098`.

### 3.8 Files and directories the Librarian touches

| path | use | grade, citation |
|---|---|---|
| `>sys>library>Pkg>template>Class.template` | template file (V5.0+) | COPY ds_bep.esp:2364-2378 |
| `>sys>librarian>esp>` | scratch copy of a remote or FDD source before catalogue (the copy is deleted and expunged afterwards; the class is marked "discordant") | COPY ds_bep.esp:2553-2564, 3073-3089 |
| `*.ptf`, `*.env` | package template / environment files | USAGE CGS_INSTALLER.esp:379-381 |
| `>fd0`, `>device>fdd1` | floppy link point and device | USAGE ms_ist.esp:1772-1775 |

**Pathname and file-name syntax.** The Librarian's catalogue routes on `:remote_or_local(#pathname,...)` (§5.4).
The rules for the names it handles come from SIMPOS's own `world` classes `pathname` and `name`, held in
CESP-ported copies (HELD-SOURCE; `sweep_2026-11-24.md` §2.1):
- a file name is `ident.type.version`;
- the ident has 1-44 characters and the type 0-10, neither with a dot;
- the illegal characters are `>`, `*`, `?`, `:` and space (morphana/_simpos/name.esp:83-96, :163-164);
- directory components are joined with `>`. A directory part may be `Node::>`, `Logical_name:` or `...>Name`
  (morphana/_simpos/pathname.esp:89-92, :93-111).

`remote_or_local/6` itself is not in the copy.

---------------------------------------------------------------------------------------------------

## 4. Screen behaviour and menus

### 4.1 Starting it

1. The user double-clicks the right button: the system menu opens.
2. The user left-clicks `librarian`. The cursor changes, and the user sweeps the two corners of
   the window.

PROSE: utter/INSTALL:30-38; gog-esp/INSTALL.e:44-46.

The 5.0 install manuals say "create a Librarian" (ライブラリアンを生成する) (TM-785 p3, TM-786 p4,
TRANSLATION).

The programmatic equivalent is `:create(#library_utility,U,W)` or `:create_window/2`, which use
`size(manipulator)` and `position(manipulator)` (COPY ds_bep.esp:3339-3343).

### 4.2 Layout

- The window has a left column holding the command menu and a right text pane for the dialogue
  (TM-181 p4, IPSJ 36239 p5, IPSJ 118681 Fig.1; SCREENSHOT).
- 1.x: the menu pane titled `Command…` and a separate text window titled `<< Librarian Text >>`
  (TM-143 p3, TM-134 p71, SCREENSHOT).
- Operation (PROSE, TRANSLATION, IPSJ 118681 p1 §2):
  1. click a command;
  2. type its parameter (e.g. a source file name) into the text window.

  Almost everything is menu-driven.

### 4.3 Command menu by version (verbatim item texts)

| version | items, in order | grade, source |
|---|---|---|
| 1.x (Nov 1985) | Check, Catalogue, Compile, Uncompile, Save, Load, Delete, Print, Info, Classes, Predicates, Execute (12) | SCREENSHOT TM-143 p3 (all 12 legible on a re-check at high resolution; status line "SIMPOS Version 1.5x", 17-Nov-85) |
| ~2.0 (Apr 1986) | Check, Catalogue, Compile, Uncompile, Save, Load, Delete, Execute, … (rest hidden) | SCREENSHOT Giho 8609 p16 |
| 2.10 (Jun 1986) | Check, Catalogue, Compile, Uncompile, Save, Load, Delete, Execute, Utility (9) | SCREENSHOT TM-181 p4 |
| 2.50 (Sep 1986) | same 9 | SCREENSHOT IPSJ 36239 p5 = TM-229 p6 (same paper; checked by eye 2026-11-24) |
| video (status "A00" in esp.wmv) | same 9, labels `librarian_1` / `librarian_2` | SCREENSHOT simpos.wmv@0-5, @117-122; esp.wmv@117 |
| 5.0 (1988-90), standard | Set up, Check, Catalogue, Save, Load, Delete, Package, Execute, Utility, ESP tool, [Close] (11). Set up, Delete, Package, Utility and ESP tool have submenus | SCREENSHOT IPSJ 118681 p1 Fig.1 |

**5.0 submenus** (each a separate window with a title bar; SCREENSHOT IPSJ 118681 Fig.1):

| submenu title | items |
|---|---|
| `set_up_menu` | Set up / Save state / Check menu item |
| `package` | Set default package / Define package / Define environment / ---- / Delete package / Delete environment / ---- / Retrieve / ---- / Other command / ---- / [Exit] |
| (Delete, from Fig.2) | Delete / Abolish / Forget / Delete resource / [Exit] |
| Utility, ESP tool | not expanded in the figure: UNSPECIFIED |

**Items named only in user prose** (PROSE):
- `Package` → `Other Command` → `Load package template`. It prompts `Directory Name>`; a window
  is created; the user selects `LOAD ALL`; "packages are created" (utter/INSTALL:40-58).
- `Package` → `Other command` → `Load one package`: input the file names (papyrus/INSTALL:39-41).
- `package` command → `set_default_package` (kwic-esp/INSTALL.j:106-107, TRANSLATION).
- `save` → its `menu` subcommand → `SAVE ALL` (kwic-esp/INSTALL.j:111).
- "Save templates" (kappa2/INSTALL:40).
- "catalog" item with a comma-separated wildcard list `BUP>*.esp,CALC>*.esp,...` (euod/INSTALL:43-50).

The Japanese relabelling in IPSJ 118681 Fig.3 (SCREENSHOT, customized):
- Top menu: 初期設定, パッケージの設定, クラスの登録, クラスのロード, クラスの削除,
  パッケージ メニュー, ユーティリティ メニュー, アイコン.
- package menu: パッケージの登録, パッケージ環境の登録, パッケージファイルの作成,
  パッケージ環境ファイルの作成, 拡張機能.

This shows that labels and grouping are free; the commands are fixed names.

**Menu-to-command map for a stand-in.** Fig.2 gives the commands for the first six top items. For
the rest (INFERENCE):

| item | command |
|---|---|
| Package / Set default package | set_package |
| Define package | make_package |
| Define environment | make_environment |
| Delete package | delete_package |
| Delete environment | delete_environment |
| Execute | execute (§5.1) |
| [Close] | close the Librarian |

### 4.4 Operand pop-up (2.x)

The pop-up is titled `CLASS NAME`. It has fixed items `DO IT`, `EXIT`, `ALL BUT SELCTED` (sic) and
`FROM WHITE BOARD`, then class names; selected names are marked with a box or an `x`. It is a
multi-select menu (SCREENSHOT IPSJ 36239 p5; TM-229 p6 has `ALL BUT SELECTED`, low confidence).

The 6.1 save menu is built by `librarian_menu:create_menu_for_save/2` at position (350,250) and
read with `read_items/4` (COPY ds_bep.esp:1845-1856). INFERENCE: it is the same kind of pop-up.

### 4.5 Transcript conventions (verbatim)

| line | when | grade, source |
|---|---|---|
| `File Name>demo` | Catalogue prompt and echo (2.50) | SCREENSHOT IPSJ 36239 p5; esp.wmv@117 |
| `File Name:escher` | 1.x / 2.10 form | SCREENSHOT TM-143 p3, TM-181 p4 |
| `Catalogging "demo.esp"...` | start of a file | SCREENSHOT IPSJ 36239 p5, Giho 8609 p16; COPY ds_bep.esp:2029 |
| `    as_demo_program` (indented) | each class as it is read | SCREENSHOT; COPY prints `   <Name>` |
| `as_demo_program end.` | each class done | SCREENSHOT |
| `eight_puzzle_window auto loaded.` | a needed class auto-loaded | SCREENSHOT Giho 8609 p16 |
| `- - - - - - - -` | rule between commands | SCREENSHOT |
| `Class Name>[test]` | class prompt with the default in brackets | SCREENSHOT IPSJ 36239 p5 |
| `PREDICATE` between rules | output of a command (INFERENCE: Utility/predicate) | SCREENSHOT IPSJ 36239 p5 |
| `Input Class Name.` / `@ name` / `Regist…` / `Compil…` | 1.0 prompt dialogue | SCREENSHOT TM-134 p71 (partly hidden) |
| `Printed.` | 1.x Print | SCREENSHOT TM-134 p71 |
| `Loading <id>...`, `Saving <id>...`, ` end.` | load, save | COPY ds_bep.esp:1991, 2096 |

**Spelling of "Catalogging".**
- The double-g form is attested in the 6.1 copy, IPSJ 36239 and Giho 8609.
- The trtm notes render it `Cataloguing` from low-resolution scans.
- The video reading is `Cataloging`.
- **Follow the copy: `Catalogging`.**

### 4.6 Error window and error-handling menu

**Layout**
- The title bar is inverse: `Error occurred in <name>( process <n> )`.
- Then the message lines.
- A second inverse bar reads `Error handling menu:`.
- Then the situation's items.

**The Librarian case** (SCREENSHOT TM-785 p3, 1989, read at 400 dpi):

```
Error occurred in librarian_59( process 59 )
Package drawing already exists
Cannot load package_template_file
Error handling menu:
  Erase existing package and continue
  Inspect the information of this event
  Return to librarian top level
```

- "Erase existing package and continue" opens a confirm menu titled `Really?` with items `ERASE`
  and `STOP` (SCREENSHOT TM-785 p3).
  - ERASE deletes the package and reinstalls (about 1 min).
  - STOP stops.
- "Return to librarian top level" returns to the Librarian screen (PROSE).
- The 2.10 debugger case shows the same layout: `Error found by esp_macro_expander:` / message /
  `Continue`, `Cancel this input`, `Kill this process` (TM-181 p5).
- During catalogue and load, each class is wrapped in `:catch(Process,"Skip this class",...)`, so
  the error menu offers **"Skip this class"** (COPY ds_bep.esp:2007, 2100). The sum INSTALL
  says "If error message is displayed, skip that class" (sum/INSTALL:18-22, PROSE).

### 4.7 Abort

While the Librarian prints, it polls `:read_sense(Out,C)`. A middle click (`mouse#mm`), `control#"c"`
or `key#abort` prints `aborted.` and fails the command (COPY ds_bep.esp:3477-3488).

---------------------------------------------------------------------------------------------------

## 5. Command language and dialogues

### 5.1 Execute

- Execute is "batch command execution" (コマンドの一括実行): it calls a series of Librarian
  commands at once (TM-229 p6, IPSJ 36239 §4(6), PROSE).
- Prompt `Command>` (TM-785 p3, TM-786 p4, gog-esp/INSTALL.e:49-50).

**What users typed at `Command>`** (variants, recorded and not harmonized):

| typed | effect described | version | source |
|---|---|---|---|
| `fdd("drawing.com")` | run the command file from floppy; asks `FDD mount ok?`, then `Input unit No. (0):0` (one keystroke, no Return); installs in about 1 min | 5.0 (1989) | TM-785 p3 (SCREENSHOT/PROSE); TM-786 p4 has `input unit No.(0): 0` |
| `fxd("cgscmp.com").` | run the command file from the fixed disk | ? (1992-93) | gog-esp/INSTALL.e:50 PROSE |
| `CATALOG.COM` | (prompt unnamed) | 7-8 / A22 | kappa2/INSTALL:39 PROSE (Japanese: "type CATALOG.COM at the prompt") |

INFERENCE on the names: `fdd` = floppy-disk drive and `fxd` = fixed disk.

**The conflict with the copy.** In the 6.1 copy, `fxd(P)` as a command-list item means
**catalogue P** (§5.2). It does not mean "execute the command file P".
- The gog prose and the copy cannot both be literal unless Execute treats a lone `fxd("x.com")`
  as "read a command file".
- Spec, following the held programs:
  - At the Execute prompt, `fxd(File)` and `fdd(File)` with a file of type `com` **read the file's
    list and run it through command/2**.
  - A bare file name is accepted too (kappa).
  - Inside a command list, `fxd(P)` catalogues P (the copy).
- Labelled INFERENCE. A stand-in that does both satisfies every held source.

### 5.2 The command-list interpreter `library_utility:command/2` (COPY ds_bep.esp:3381-3411)

The interpreter walks the list left to right. For each item it computes (Name, ArgVector), then
does `:refute(UT, Name, ArgVector)`, i.e. it **sends the item as a method to the
library_utility**. ESP writes `f(a,b)` as the vector `{f,a,b}`.

| item | becomes | method called (arity counts UT) |
|---|---|---|
| `fxd("path")` (a string) | `catalogue {["path"]}` | catalogue/2 |
| `fxd(List)` (anything else) | `catalogue {List}` | catalogue/2 |
| `save(C)`, C an atom | `save {[C]}` | save/2 |
| `load(C)`, C an atom | `load {[C]}` | load/2 |
| `delete(C)`, C an atom | `delete {[C]}` | delete/2 |
| an atom `a` | `a {}` | a/1 |
| `f(A0..An)`, 1 ≤ n+1 ≤ 6 arguments | `f {A0..An}` | f/(n+2) |

**Failure behaviour**
- If the method fails, the item is **silently ignored** (`do_command`'s catch-all clause).
- `illegal command` is printed only for an item that is neither an atom nor a compound with 1-6
  arguments.
- The copy then tries to print the item. The variable in the head is anonymous, so an unbound
  variable is printed, which is a bug in the copy. A stand-in should print the item.

**What the held command files therefore require** (USAGE + COPY dispatch; implied methods
UNSPECIFIED unless shown):

| item as written | uses | implied method | meaning | citation |
|---|---|---|---|---|
| `make_environment(Env,[Pkg,...])` | 1 | make_environment/3 | create environment Env inheriting the packages | gog-esp/cgscmp.com:2 |
| `save_environment(Env)` | 1 | save_environment/2 | write the `.env` | cgscmp.com:3 |
| `make_package(Pkg,Env)` | 1 | make_package/3 (papyrus calls it directly) | | cgscmp.com:4 |
| `save_package(Pkg)` | 1 | save_package/2 | write the package (template) | cgscmp.com:5 |
| `use_package(Pkg)` | 1 | use_package/2 | set the current package (= set_package/2, INFERENCE) | cgscmp.com:6 |
| `fxds([Path,...])` | 44 | fxds/2 | catalogue the files **in the order given** (macro banks first). The copy does not special-case it; INFERENCE: = catalogue/2 | cgscmp.com:7-214; kappa2 *.COM |
| `save_all_classes` | 1 | save_all_classes/1 | save every catalogued class | cgscmp.com:215 |
| `command("x.COM")` | 34 | command/2 with a **string** | run another command file (nesting). In the copy, command/2 only accepts a list, so this item would silently do nothing. Real SIMPOS must read the file: UNSPECIFIED, and a stand-in must implement it | kappa2/kappa2/CATALOG.COM:2-6, kernel/CATALOG.COM:7-29 |
| `load(kappa##kappa_loader)` | 1 | load/2 with a `##` term (the atom guard fails, so it goes through the generic path) | load (make) the class. A stand-in should accept a single id as well as a list | kappa2/kappa2/init/ipl.com:7 |
| `refute(Goal)` | 1 | refute/2 | execute a goal, here a class-method call `:ipl_load(#kappa##kappa_loader,[...],270)` | ipl.com:8-11 |
| `fdd("x.com")` | (prose) | fdd/2 | from floppy (owner `librarian_fdd`, INFERENCE) | TM-785 p3 |

In kappa's ipl.com, 270 is a class count for a progress meter (USAGE
kappa2/kappa2/utility/tool/LOADER.ESP:27, 96-101).

### 5.3 The FDD dialogue (TM-785 p3, TM-786 p4; SCREENSHOT and PROSE, 5.0)

The sequence:
1. Create a Librarian.
2. Floppy in unit 0.
3. Select `Execute`.
4. Type `fdd("drawing.com")` and press Return.
5. `FDD mount ok?` appears.
6. `Input unit No. (0):` appears; type `0` with no Return.
7. The install runs.

If the package already exists, the error window of §4.6 appears. The `.com` contents for these
tools are not printed.

### 5.4 Catalogue: the dialogue and the algorithm

**Dialogue** (2.50 SCREENSHOT, IPSJ 36239 p5):
- Click `Catalogue`; the prompt is `File Name>`.
- Type `demo`. The type `.esp` is added (`Catalogging "demo.esp"...`).
- The transcript follows §4.5.
- The 5.0+ prompt text is not seen. The kwic INSTALL types a quoted wildcard path
  (`catalogue "ltbroot:source>kwic>*.mac"`, kwic-esp/INSTALL.j:108-110).

**Algorithm** (COPY ds_bep.esp:2018-2041, 2618-3068):
1. `:retrieve(#directory,FileObj,Name,Path)`; on failure print `File <f> not found.`.
2. Route on `:remote_or_local(#pathname,...)` and `:is_fdd(FileObj)` into `local_disk`,
   `local_fdd`, `remote_disk` or `remote_fdd`. Non-local files are first copied to
   `>sys>librarian>esp>`.
3. Print `Catalogging "<path>"...`.
4. Read the terms with the operator pool of §3.7, then for each class or macro_bank:
   1. `expand_definition` with the macro class (default `simpos##esp_macro_expander_for_compiler`);
   2. print `   <Name>`;
   3. `catalogue_class` if the class is new;
   4. `abolish_class_object` if it has an object;
   5. `make_class_template_from_internal_format`.

   Macro banks go through `macro_preprocessor` and are made at once.
5. `update_class_source_file`, unless `source_file_mode` is off.
6. `make_all_classes`. Then "load_all_and_public": `define_public_classes`.
7. Push the file and class ids to the `file` / `class` named yank buffers, unless
   `:named_yank_flag(#named_yank_buffer_subsystem,off)`.

Asked "save all asserted predicates?" at save: sum/INSTALL:26-29 (PROSE). The exact prompt text
is not held.

### 5.5 Check (TM-181 p4, SCREENSHOT 2.10)

```
Class Name(my_window)
«?» my_window «?»
source   27-Jun-86 17:57:13
template 27-Jun-86 17:57:13
   interpretive
   file     «none?»
object   27-Jun-86 17:57:17
   compiled
- - - - - - - - - - - - - - - -
```

These are the labels papyrus's `check/3` matches (§3.2). That is USAGE confirming SCREENSHOT.

---------------------------------------------------------------------------------------------------

## 6. Messages and error texts

All are verbatim. `<x>` marks a substitution. The source is the COPY (ds_bep.esp) unless noted.

| message | when | line |
|---|---|---|
| `illegal command` | command-list item of the wrong shape | 3387 |
| `aborted.` | user abort while printing | 3488 |
| `Catalogging "<path>"...` | catalogue start | 2029 |
| `File <f> not found.` | catalogue source missing | 2022 |
| `file <f> not found.` | get_classes_from_source | 2155 |
| `file not found :\n   "<f>"` | read_term | 2664 |
| `include file not found:\n   <f>` | include | 2773 |
| `illegal source specification :\n<term>` | catalogue argument not a file or term | 2605 |
| `illegal source term specification :\n<term>` | V6.11 term input | 2613 |
| `illegal definition :\n<term>` | unknown top-level term | 2677, 2775 |
| `illegal operator definition : \n<term>` | bad add_operator | 2248, 2788-2805 |
| `illegal macro definition :\n<term>` | | 2854 |
| `   copy failed.` | remote or FDD copy to `>sys>librarian>esp` | 2556 |
| `Loading <id>...` / `Remote loading <id>...` | load | 1991 |
| `Class <c> template file not found ` | load | 1982, 1999 |
| `Class <c> not catalogued` | load | 1967-2012 |
| `Load <id> failed.` | load | 2012 |
| `Saving <id>...` then ` end.` | save | 2096 |
| `Class <c> template not found.` | save | 2079, 2090 |
| `Class <c> not catalogued.` | save | 2060-2107 |
| `Save <id> failed.` | save | 2107 |
| `class <Id>...` / `   <Id> end.` / `   <Id> fail.` | register | 2124-2133 |
| `- <path> -` | get_classes_from_source | 1858-1862 |
| `This system has no librarian window interface!!\nYou cannot use this command.` | library_error from save_non_saved_classes without librarian_menu | 1856 |
| `- <Type> -`, `- Time: … -`, `- Heap: N words -`, ` hrs. ` ` min. ` ` sec. ` | response-time display | 3306-3322 |
| `Package <p> already exists` / `Cannot load package_template_file` | load package template onto an existing package (5.0) | SCREENSHOT TM-785 p3 |
| `Error found by esp_macro_expander:` + `illegal slot assignment: A := A` | macro-expander error header (debugger, 2.10) | SCREENSHOT TM-181 p5 |
| `<class> auto loaded.` | auto-load | SCREENSHOT Giho 8609 p16 |
| `FDD mount ok?`, `Input unit No. (0):` | fdd | SCREENSHOT TM-785 p3 |
| `Really?` ERASE / STOP | confirm erase | SCREENSHOT TM-785 p3 |

---------------------------------------------------------------------------------------------------

## 7. Stand-in notes (minimum behaviour the held programs need, in build order)

All of this section is INFERENCE built on the cited evidence.

1. **`library` as a registry over the loader.**
   - The repo's loader (`pim/psi/librarian.py`, OURS) already builds class objects from `.ptf`
     templates.
   - Wrap it as class methods on `#library`:
     - `assign/1` (succeed);
     - `get_class_object/3` (resolve per §1.4, load on demand, accept all three name forms of
       §3.1);
     - `make_class_object/2`, `check_info/3` (`object`, `template`, `template_file`);
     - `check_package/2,3`, `get_class_id/5`, `check_class_id/3`.
   - This covers 160+35+33+28+17+13+11 = 297 of the 366 uses of `library` (81 %).
   - The ptf demand-load sequence is assign → check_info(template_file) → make_class_object →
     get_class_object.
2. **Packages.**
   - `make_package/2`, `make_package_forcedly/2`, `change_environment_in_package/3`,
     `delete_package(_forcedly)/2`, `delete_environment_forcedly/2`.
   - `load_package_template/3` (a `.ptf`), `save_package_template/3`.
   - The environment `.env` format is unknown, so keep environments as in-memory lists.
3. **`library_utility` core.**
   - `create/2,3`, `set_output/2`, `remove_output/1`, `get_package/2`, `set_package/2`.
   - `load/2`, `save/2` (templates to files).
   - `catalogue/3` over files **and terms**, needed by cal's and papyrus's database classes and by
     txtstrct.
   - Catalogue needs an ESP compiler. Until it exists, the stand-in can only accept classes
     already present as templates, and must fail loudly otherwise.
4. **Database methods.** The class-side `assert/assertz/asserta/retract/retract_all` on a
   catalogued class: 287 uses, mainly sum. Implement them as dynamic clauses attached to the
   class template.
5. **Queries.** `check/3` (the §5.5 label list), `get_class_names/4`,
   `get_packages_with_wildcard/3`, `get_classes_with_wildcard/5`, `get_class_id_atom_list/4`,
   `get_direct_superclasses/3`, `string_to_term/3`, `delete/2`, `make_package/3`,
   `delete_package/2`.
6. **The Librarian program and window.**
   - Title `librarian <pno> ( default: <pkg> )`; process name `librarian_<pno>`.
   - The 5.0 menu of §4.3, driven by a `menu_list` term (§3.5); the commands of §4.3's map.
   - `File Name>` / `Class Name>[default]` prompts, the transcript lines of §4.5, `Catalogging`
     spelling, rules between commands.
   - The CLASS NAME multi-select pop-up.
   - The 2.x 9-item menu as a switch for the video era.
7. **Execute and command files.**
   - `Command>` prompt.
   - Accept `fxd("x.com")`, `fdd("x.com")` and a bare file name: read the list term and run §5.2
     with the extra items `command/1`, `fxds/1`, `make_environment/2`, `save_environment/1`,
     `save_package/1`, `use_package/1`, `save_all_classes`, `refute/1`, `load/1` (any id form).
   - `fdd` performs the `FDD mount ok?` / `Input unit No. (0):` dialogue.
8. **Errors.**
   - The error window of §4.6, with "Skip this class" during catalogue/load.
   - The package-exists menu with Really? ERASE/STOP.
   - The `library_environment` `error_mode off` must suppress the menu (installers rely on it).
9. **Compiler-side classes** for the CAL debugger and kwic tools: `esp_macro_expander`
   (`new/2`, `expand_goals/3`), `esp_operator_pool`, `as_esp_parser`/`as_esp_unparser`,
   `esp_compiler:compile/4`, `kl0_compiler:compile_one_predicate/6`. These need the ESP and KL0
   compilers (OURS), so last.
10. **FDD classes** (`fdd_volume` and the rest) over a host-file floppy image, and `version/2`.
    Return a string in kappa's accepted set, e.g. `"4.0B"`. kappa has no branch for later
    versions, so its version check fails for 5.x+ strings: this is a held-program constraint.

Customization (user classes inheriting the Librarian plus a command class, IPSJ 118681 §4) needs
the `librarian_*` natures to be real classes, so a stand-in should keep the 6.1 nature list of
§1.2 even when the natures are empty.

---------------------------------------------------------------------------------------------------

## 8. Coverage

**Command:**

```
cd pim/docs/simpos/subsystems && python3 -I tools/coverage.py
```

It reads `notes/*.tsv` against `required/requirements.tsv` and writes `coverage/coverage_librarian.tsv`.

**Result** (2026-11-24, librarian partition):

| status | methods | use-weighted |
|---|---|---|
| DOC-class | 1 | 36 |
| DOC-unowned | 14 | 98 |
| USAGE | 67 | 748 |
| USAGE-unowned | 11 | 13 |
| NONE | 21 | 64 |
| **total** | **114** | **959** |

**Reading it**
- **DOC-unowned is a name match on some other class's documented method**, e.g. `create/2` or
  `new/2`. It is not documentation of the Librarian. Only `expand_goals/3` (TM-388) is documented
  on its own class.
- The Librarian surface is therefore **USAGE-dominated**: 78 % of uses rest on held programs and
  the cil COPY, not on printed interfaces.
- This document lifts some of the 21 NONE rows to USAGE by reading their call sites (§2.2, §2.6):
  - `library_utility` `check/3`, `make_package/3`, `get_packages_with_wildcard/3`,
    `get_class_names/4`, `string_to_term/3`;
  - the 5 `fdd_volume` instance methods and `fdd_volume_utility:initialize/3`;
  - `fdd_binary_file` `open/3,5` and `make_only/3,4`;
  - `fdd_binary_file_tap` `at_end/1`;
  - `file_backup` `set_input/2` and `restore/3`.

  That is 18 rows / 61 uses, with argument shapes but not always semantics.
- Still NONE in meaning: `macro_preprocessor:preprocess/3` (COPY call shape only) and
  `as_esp_parser:gett/3` / `as_esp_unparser:putt/3` (no held body).

**Coverage of the screen**
- The menus are covered for 1.x, 2.10, 2.50 and 5.0 (top level, two submenus, Delete).
- The Utility and ESP tool submenus, the 5.0 prompts, and the init-file name are not covered:
  see gaps_librarian.md.
