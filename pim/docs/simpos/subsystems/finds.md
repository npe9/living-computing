# Possible SIMPOS code and binaries found in held material (2026-11-24)

SIMPOS itself is lost. This page lists everything the 2026-11-24 subsystem dive found that may be
**SIMPOS's own code or data**, as opposed to application code that calls SIMPOS. It covers the
window system, the Librarian and the shell. Everything listed stays where it is held: the IFS
archives are cited by path:line and are **not** committed (`AGENTS.md`, repo is public).

Grades: **COPY** means the file says it is a copy of SIMPOS. **DERIVED** means it is descended
from SIMPOS source by its stamps, then modified. **PRINTED** means it is printed in a report as
system code. **DATA** means a file in a SIMPOS format, not code.

## 1. The strongest find: the SIMPOS 6.1 Librarian, copied and patched (COPY)

**Where:** `cil/src/ds_bep.esp:1773-3518`, inside `ifs/natural-lang/simpos/cil.tar.gz`.

**What:** three Librarian classes that the file calls a "patch class for library_utility on SIMPOS
6.1". CIL's team took them from SIMPOS's own sources (the stamps are SIMPOS developers' files),
patched them, and catalogued them into CIL's own package `spec_ds`. Apart from the four stubbed
methods below, it is not known how far the bodies differ from stock 6.1. They may be stock, a
vendor patch, or CIL's edits. Read them as SIMPOS 6.1-era Librarian code, possibly modified.
The classes are:
- `library_utility`, the programmatic Librarian (`:3123-3518`);
- `librarian_class_generator`, the template and object generator (`:1777-2326`);
- `librarian_read_term`, the source reader and cataloguer (`:2331-3121`).

**Evidence.** The lead opened these lines himself on 2026-11-24:
- `:45`: the file history says `91. 1.28 by T.S. merge patch class for library_utility`.
- `:1774`: `% patch class for library_utility on SIMPOS 6.1`.
- `:1776`: `% mkpsi000::>sys>user>yasuko>GEN.esp.6, 28-Jul-88 ..., Edit by yasuko`.
- `:2327-2329`: three stamps on `librarian_read_term`:
  - `icpsi135::>sys>user>yasuko>READ.esp.2, 22-Jul-88`;
  - `icpsi123::>sys>user>soft>librarian>READ.esp.7, 26-Feb-88`;
  - the DEC-20 file `<M-KONDOH.LIBRARIAN>ZREAD.ESP.79, 2-Jul-86`. The Librarian was developed on
    the DEC-20 and moved to the PSI.
- `:3122-3123`: `% mkpsi000::>sys>user>yasuko>UT.esp.2, 29-Jul-88`, then `class library_utility has`.
- `:3358-3359`: `:compile(_,_);` and `:uncompile(_,_);`. CIL stubbed the real compile methods, so
  those bodies are **not** SIMPOS's.

INFERENCE, strong: "yasuko" is 児玉泰子 (Kodama Yasuko, Mitsubishi Electric Computer Systems), the
author of IPSJ 118681 (1990) on the SIMPOS Librarian's customisation (`notes/ipsj.md`).

**What it settles:**
- the Librarian's internal class structure (natures, slots);
- the `command/2` command-list interpreter, which is the semantics of `.com` command files;
- the messages and the response-time flag bits;
- the window it makes for itself.

The detail is in `librarian.md` and `notes/ifs_libshell.md` §4.1. The natures it names but does not
define are the rest of the Librarian, still lost: `librarian_version`, `librarian_delete`,
`librarian_package`, `librarian_spy`, `librarian_reference`, `librarian_fdd`,
`librarian_subroutine`, `as_assert_utility`, `librarian_catalogue`, `as_class_maker` and
`compiler_error_reporter`.

**Correction to `../required/NOTES.md`:** this copy's package is `spec_ds`
(`cil/src/INSTALL.esp:93-105`). It is not `spec_ms`. CIL's own installer uses the real
`#library_utility` (`INSTALL.esp:14`), and only its back end uses the copy (`ds_bep.esp:68`).

## 2. The interpreter's KL0 built-in module (COPY, probable)

**Where:** `cil/src/cil_kl0.esp:74`, `class builtin` in package `kl0`.

**Evidence:**
- The stamp `<M-KONDOH.SUBROUTINE>BUILT1.ESP.11, 23-Jul-86` (`:43`) has the same author and era as
  the Librarian's reader.
- The comment says the module is for the local interpreter to execute KL0 built-ins (`:45`).
- It lists the predicates the interpreter must handle itself (`:45-52`) and the compiler's
  renames (`:55-69`).

INFERENCE: this is the built-in table of SIMPOS's `interpreter` class, which the debugger uses. Its
176 name/arity pairs are already in `../required/builtins.tsv`. (`notes/ifs_libshell.md` §4.2)

## 3. The SIMPOS debugger, as the base of CAL's debugger (DERIVED)

**Where:** `cal-esp/deb2.12/`, inside `ifs/kbms-clp/simpos/cal-esp.tar.Z`.

**Evidence:**
- `save.esp:10` carries the DEC-20 stamp `<SIMPOS.E.DEBUGGER>SAVE.ESP.3, 14-Apr-87 ..., Edit by
  M-TAJIMA`. That directory is the SIMPOS debugger's own.
- Later stamps run through `>sys>user>tajima>new_debugger>` and `>sys>user>tajima>debugger>`
  (1988).
- `util.esp:312, :572` carry `<ISHIBASHI.EXEC>` stamps from 1986. Ishibashi is the author of
  TM-143 and TM-181.
- CAL's own edits date from 1990-91.

**What it shows:**
- the SIMPOS debugger's structure: box-model port slots, gates and leash, the state window, and
  the save of debugger state;
- its window labels ("Debugger Menu", "Mode_Leash", "Variable", "To whiteboard", ...);
- the pane classes it is built from;
- a super-command menu.

How much is still SIMPOS's is unknown. The structure is used in `shell.md`, graded DERIVED.
(`notes/ifs_libshell.md` §4.3)

**Consequence for `../required/`:** several `as_program` rows in `requirements.tsv` are CAL-debugger
internals, among them `!debugger_window`, `set_leash/2` and `mam_do_menu/2`. They are not SIMPOS
requirements.

## 4. System code and data printed in reports (PRINTED; known before, listed for completeness)

- **Coordinator:**
  - `default_translation_table`: TR-046 p26 and p28, TR-061 p13.
  - `system_menu`: TR-046 p27.
  - Transcribed in `../printed/listings/`.
  - The 1984 system's own standard table, according to TR-061.
- **Window mixins:** `bare_window`, `with_border`, `with_label` and `window_with_border_and_label`
  (TM-065 p15-16).
- **The Librarian's standard menu definition** (`menu_list`, from its initialisation file):
  - printed as Fig. 2 of IPSJ 118681 (1990, SIMPOS 5.0), with an elision in the original;
  - the system's own data, not code;
  - transcribed in `notes/ipsj.md` and used in `librarian.md`.

## 5. Re-implementations and SIMPOS-format data (not SIMPOS, but close)

- **`cil/src/cil_esp.esp:120-254`** (package `esp_call`, 1990-91). It re-implements the SIMPOS
  macro expander's `#`-constant families: `key#`, `control#`, `pf#`, `mouse#`, `string#`. It is
  CIL's own code and the best written list of the families. It does not give their numeric values.
  (`notes/ifs_window.md`)
- **`kappa2/kappa2/utility/fmp/UTL_WIND.ESP:6`**: a `class window` whose natures are exactly TM-125
  p20's `user_window` recipe. It is application code that confirms the recipe.
- **The `.font` files in the IFS archives** (13 by name in the extracted trees; `notes/tm115.md` counts 14) (e.g. `gog-esp/suuji.font`, `kappa2 tiny_7.font`):
  - fonts in SIMPOS's own font file format, made by users (DATA);
  - the `f822` family is decoded and predicts both file sizes exactly; the 32-bit family is not
    decoded (`notes/tm115.md` F3);
  - no system font (`>sys>font>kanji_16.font`) is held.
- **Common ESP**, whose window system was built "on the basis of" SIMPOS's window specification
  (IPSJ 118569). It is not held. The 1992 distribution lead is in `web_search_2026-11-24.md`.
- **An `espclass` file**: ETL's CESP re-creation of 12 SIMPOS window classes for the RLS port
  (IPSJ 122601). It is not held, and would be worth asking for.

## 5a. Added by the second sweep (`sweep_2026-11-24.md`)

**HELD-SOURCE** means a method body in an application-carried copy of SIMPOS source. Here it is
treated as documentary, like PRINTED.

1. **SIMPOS's `world` classes `pathname`, `name` and `e_string` (HELD-SOURCE, CESP-ported).**
   - Where: `morphana/_simpos/pathname.esp`, `name.esp` and `e_string.esp`, inside
     `ifs/natural-lang/cesp/morphana.tar.Z` (LAX, 1992).
   - Provenance: `pathname.esp:6` is stamped `icpsi372::>sys>simpos7D>supervisor>world>PNAM1.esp`.
     It is the only held stamp from a SIMPOS release tree.
   - `name.esp:6` and `e_string.esp:6` are stamped from a 1988 user copy of the same `world`
     directory.
   - Coverage: 34 class methods; every `name` and `e_string` method the held programs call, and
     `pathname`'s `append/4`, `last_name/4` and `get_last/4`.
   - What it settles: the file-name rules. An ident is 1-44 characters, a type 0-10. The illegal
     characters are `> * ? :` and space. The form is `ident.type.version`.
   - The pathname port changed the separator to `/`. SIMPOS's `Node::>`, `Logical_name:` and
     `...>Name` cases survive as comments, one marked "Patch 6.13" (`pathname.esp:79-92`).
2. **CAL debugger operation manual, 2.12 (DERIVED documentation).**
   - Where: `cal-esp/deb_jman/debug.tex`, dated 1992, describing the debugger of §3 on SIMPOS 7.0.
   - It gives the Debugger Menu items, the trace command meanings, and the Mode_Leash, State and
     Spy windows.
   - It gives the leash levels as target/gate vectors and the init file `me:cal_debugger.ini`.
   - It cites the SIMPOS programming manual's section 「標準入出力（ホロフラスティング）」 and the
     operation manual's 「インスペクタ」.
3. **CESP substitutes for SIMPOS mixins, documented as such (CESP substitute; not SIMPOS code).**
   - `linguist/doc/Manual/Soft/software1.tex:802-920` says `with_margin` and `as_markers` replace
     SIMPOS's classes, the latter "with the same function".
   - It says `as_outputs` implements part of `as_output`.
   - Source: `linguist/prog/with_marker.esp` and `with_margin.esp`.
   - Gives the `create_marker/7` arguments and the marker types `box`, `line` and `reverse`.
   - Gives `get_margins/5` as `(W,^L,^R,^Head,^Tail)`.
   - Also: `morphana/_simpos/bfiles.esp` (binary_file family), `kwic-cesp` `for_rename.esp`
     (as_esp_parser/unparser), `linguist/prog/window.esp` (CESP compositions of
     `standard_io_window`, `standard_menu`, ...).
4. **The held ESP manual, read for the remaining gaps (PRINTED/PROSE, 1990).**
   - `get_slot/3` and `set_slot/3` are methods of class `class`; `!` is their macro
     (`ESPtex/program-e.tex:5987-5988`).
   - The `stop_watch` method table (`:10018-10045`).
   - A `standard_io_buffer` round trip (`:6736-6745`) and `symbolizer` atoms and numbers
     (`:6750-6765`).
5. **Manual citations.**
   - 「小型化PSI/SIMPOS プログラミング説明書 (SIMPOS 8.0版)」 and 「… ESP 説明書 (SIMPOS 8.0版)」,
     ICOT 1992 (`INFO/cesp.j:116-119`).
   - 「PSI/SIMPOS エディタ説明書」, 「… 操作説明書(I),(II),(III)」 and 「… KL0説明書」, ICOT 1988
     (`cil/man/biblio.tex:84-97`).
   - "Down-sized PSI/SIMPOS TCP/IP Network System Manual" and "… PSI Network System Manual"
     (`pimosman/Eman/e-network.tex:56,80`).
   - None of these is held. No copy or table of contents of 「入出力管理編」 was found.
6. **SIMPOS's TCP/IP configuration file** (HELD-SOURCE, application-carried copy). fuzclust's
   `install/net_config.dat` (52 lines, "version SIMPOS 7_han 91/07/19") is a sample copy of
   `>sys>tcpip>net_config.dat`. It holds the TCP/IP menu classes, the boot and server classes, and
   the spawn table, in which services 5, 6, 8 and 9 are `simpos##talk_input`, `talk_output`,
   `x_server` and `remote_printer`. Transcribed in `shell.md` §2.3. The PIMOS manual
   (`Eman/e-network.tex:22-56`, PRINTED) prints the spawn excerpt. `e-strio.tex:25-27` says in
   English that `as_resource` inherits `as_program`, and that windows and filters inherit
   `as_resource`. The commented-out Japanese original (`:20-23`) says instead that the two must not
   be inherited together. This is an open conflict (`sweep_2026-11-24.md` §2.6).

## 5b. Added by the fixed-point search (`fixpoint_2026-11-24.md`)

No new SIMPOS method body (HELD-SOURCE) was found. Provenance and usage only:
- **CIL's 4.0 manual names MTC as its author.** `cil/man/manual.tex:3-5` is 「CIL第4.0版説明書」,
  author line 三菱電機株東部コンピュータシステム株式会社, dated 平成3年3月 (March 1991). That MTC
  also wrote (or ported) CIL itself, the program that carries the SIMPOS 6.1 Librarian copy (§1), is
  an INFERENCE. If so, the copy came through the same company as 児玉泰子's Librarian
  customisation paper (IPSJ 118681) and CESP's 1994 seller, which would strengthen §1's
  inference that "yasuko" is 児玉泰子. The `mkpsi` host prefix of her stamps (`mkpsi000`) recurs only on CAL
  (`mkpsi124`, `mkpsi221`: tajima, cal, machida) and on cbcdss and kappa2 user files; that `mk`
  names an MTC machine is an INFERENCE.
- **SIMPOS's pool subsystem** (プールサブシステム) is named in held code: cal's
  `cal2.12/translate.esp:22-33` (1990) calls `list_index` "the pool subsystem's list index" and stores
  stack vectors converted to heap vectors. IPSJ 113884 (1986, PROSE) says the same of the PSI port of
  ICOT's microprogram assembler, and IPSJ 114360 (EXTKERNEL on MELCOM PSI) represents its working
  memory with "the pool's lists that SIMPOS provides". So `list`, `list_index`, `hash_index`,
  `monogyny_*_index` and `cascade_index` belong to one subsystem, "pool" (INFERENCE from the names).
- **Front-end usage census** (`tools/fe_census.py`, `notes/fixpoint_fe.tsv`): the ESP front ends of
  the PIMOS applications send 285 class/method/arity keys to SIMPOS classes (files selected by content,
  after a recursive unpack), 46 of them not sent by the 15 census programs. The curated rows with meanings are `notes/fixpoint.tsv`.

## 6. Checked and not found

- **Held compiled packages** (`notes/ptf.md`):
  - None of the 1,662 classes in the 11 `.ptf` and 10 papyrus `.pak` files is in package `simpos`.
  - None has the unqualified name of a SIMPOS class. The nearest miss, `kappa##window`, has nature
    `user_window`.
  - The headers name `lversion lib50` but no SIMPOS release.
- **Reports:** TM-115, TM-785, TM-786, TM-181, TM-143, TM-229 and TM-388 print user example code
  and SIMPOS screen text only. TM-115 says `as_general_font` is under a page of system source; it
  is not reproduced.
- **The ICOT museum video:**
  - it shows SIMPOS's menus as rendered (system menu, Librarian, debugger, window menu,
    file_manipulator);
  - the source code on screen is demo application code;
  - no binary is visible (`notes/video.md`).
- **The IFS archives:** no binary, boot image or `.ptf` of a SIMPOS package (`ifs_libshell`,
  `ifs_window`).
- **Second sweep, every held file:** the second sweep unpacked recursively, 36,151 non-empty files
  (`sweep_2026-11-24.md` §5). It found:
  - no other `patch class` and no other `<SIMPOS.` or `>sys>simpos` stamp;
  - no definition of any of the eleven missing Librarian natures;
  - no `.ptf`/`.pak` beyond the 21 catalogued;
  - no SIMPOS string table in any binary;
  - no text of the I/O manual.
  The 1,417 held report PDFs have no text layer, so they could not be text-searched.
- **Places that hold files, searched from outside** (`search_files_2026-11-24b.md`): GitHub code
  search (57 queries), Sourcegraph, GitLab, Software Heritage, SourceForge, the OSDN mirrors, eight
  live Japanese FTP mirrors, Wayback CDX of 35 more hosts, archive.org metadata and full-text search,
  Discmaster, two Usenet archives, and the KLIC and PDSS distributions. No SIMPOS, ESP or CESP file
  was found; the only ICOT files were copies of the held IFS tree. No ICOT Free Software or AITEC
  CD-ROM image is on archive.org or Discmaster.
