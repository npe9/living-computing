# Web search for SIMPOS's window system, Librarian and shell (2026-11-24)

A delegated web search, made after the searches in `../../psi_acquisition.md`
sections 1, 5, 6, 7, 9 and 10, `../../archive_search_notes.md`,
`../source_notes.md` and `../../nonlocal/lit/SOURCES.tsv`. It did not
repeat them. It went deeper into Japanese sources (IPSJ 全国大会 and SIG
papers, CiNii, NDL) and wider (Common ESP, Software Heritage, GitHub,
Usenet, Wayback, museums, booksellers). All accesses were on 2026-11-24.

"Opened" means the document was fetched and its text or page images were
read. "Located" means only a catalogue or search record was seen. All
page numbers are printed page numbers.

> **No SIMPOS or CESP code or binaries were found.** That covers source,
> binaries, tapes, disk images and emulators.
>
> The strongest code lead is a 1992 comp.lang.prolog post. It says CESP,
> whose window system is "based on" SIMPOS's, was distributed as source
> code with four volumes of documentation, on a data cartridge, to anyone
> who asked cesp-request@air.co.jp (see "Leads" below). Nobody was
> contacted. Contacting anyone needs the owner.

## Results by subsystem

### Window system

1. **IPSJ 118569, opened, new, downloaded.**
   - 木村兼江, 佐藤良治, 実近憲昭 (AI言語研究所, AIR) and 国府田明弘
     (日本ビジネスオートメーション), 「Common ESPウインドウシステムの実現方式」.
     第40回全国大会 (1990-03), pp.716-717.
     https://ipsj.ixsq.nii.ac.jp/records/118569
   - The CESP window system was developed on the basis of the
     specification of the SIMPOS window system for ESP on PSI
     (「PSI上のESP用SIMPOSウインドウシステムの仕様をベースに開発する」).
     It is built on the X Toolkit Intrinsics and Xlib, and supplied as a
     library package, not as part of the language.
   - Fig. 2 gives the class set:
     - `#window` and `#menu`
     - the mixins `#as_superior`, `#with_pane`, `#with_border`,
       `#with_label`, `#with_font`, `#as_cursor`, `#as_input`,
       `#as_output`, `#as_mouse`, `#as_graphic`, `#as_scrollbar` and
       `#as_dialogbox`
     - `#event`
   - Windows are made with `:create` and removed with `:close`. All
     window methods are synchronous.
   - It cites a manual not held anywhere we know of,
     「ESPプログラミング説明書－入出力管理編」.
   - This is the nearest thing found to a statement of SIMPOS's window
     class decomposition by its successor's implementers.

2. **IPSJ 122601, opened, new, downloaded.**
   - 田島守彦 (電総研, ETL), 「ESPプログラムのCESPシステムへの移植事例」.
     第45回全国大会 (1992), pp.5-45/46.
     https://ipsj.ixsq.nii.ac.jp/records/122601
   - The paper ports the RLS application from MELCOM PSI-II/SIMPOS to
     CESP 3.2 on a SPARCstation 2. It names the SIMPOS window classes the
     application needed and CESP lacked. They were re-created in CESP by
     multiple inheritance:
     - `standard_scrolling_menu`
     - `standard_io_window`
     - `window_without_label`
     - `as_mouse_input`
     - `labeled_sash`
     - `as_scroll`
     - and, outside the window system, `monogyny_hash_index` and
       `library_utility`
   - `choice_window` and `popup_choice_window` were made by subclassing.
     `as_markers` was new.
   - Its ESP to CESP method table:

     | SIMPOS (ESP) | CESP |
     |---|---|
     | `:kill(Window)` | `:close` |
     | `:retract_all/4` | `:abolish/4` |
     | `:write_lines/2` | `:write_line/2` |
     | `key#cr` | `key#lf` |
     | `:get_mouse_position/3` | the same, divided by the unit |
     | `:draw_line/8` | `:draw_abs_line/5` |
     | `:draw_filled_circle/5` | the same name with arity 7 |
     | `#font_13` | `"a14"` / `"a24"` |
     | `control#"c"` | `key#etx` |
     | `mouse#r` | `'mouse#r'` |
     | `key#enter`, `keypad#'0'` | no equivalent |

     Further differences:
     - `dynamic` declaration syntax differs.
     - `:read_with_click/3`, which returns the item and the l/m/r click,
       was missing from CESP and was added in 3.3.
     - The string origin is the top left in SIMPOS and the bottom left
       in CESP.
   - Timing: catalogue on PSI-II 3'30" against CESP 11'15". PSI-III
     (PSI/UX) is about 4x PSI-II.
   - **This is a primary-source list of real SIMPOS window class and
     method names with their arities.**

3. **IPSJ 115459, opened, new, downloaded.** The WINCS 全国大会 version
   (1988). The journal version is already held. It describes the ESP
   window class library as fine-grained parts to be inherited.
   https://ipsj.ixsq.nii.ac.jp/records/115459

### Librarian

1. **IPSJ 118681, held since an earlier search but not cited in any
   document; opened here.**
   - 児玉泰子 and 藤本誠司 (三菱電機東部コンピュータシステム),
     「SIMPOSライブラリアンのカスタマイズ機能」. 第40回全国大会 (1990-03),
     pp.933-934. https://ipsj.ixsq.nii.ac.jp/records/118681
   - **Fig. 1 is the standard Librarian window**, titled
     "librarian 40 (default: user)".
     - Top menu: Set up / Check / Catalogue / Save / Load / Delete /
       Package / Execute / Utility / ESP tool / [Close].
     - The Set up submenu: Set up, Save state, Check menu item.
     - The Package submenu: Set default package, Define package, Define
       environment, Delete package, Delete environment, Retrieve, Other
       command, [Exit].
   - **Fig. 2 is the menu definition from the Librarian's initialisation
     file**, which is ESP-term syntax:
     ```
     menu_list := [("Set up", set_up_menu, [("Set up", set_up),
       ("Save state", save_state), ("Check menu item", check_menu_item)]),
       ("Check", check), ("Catalogue", catalogue), ("Save", save),
       ("Load", load), ("Delete", delete_menu, [("Delete", delete),
       ("Abolish", abolish), ("Forget", forget),
       ("Delete resource", delete_resource), ("[Exit]", up)]), ...]
     ```
   - The figures go on:
     - Fig. 3 is a Japanese-language menu.
     - Fig. 4 is the internal structure. There is a command execution
       part, an I/O part on the window system, and a program-interface
       part on the library system.
   - Customisation arrived in SIMPOS 5.0; 6.0 was in development.
   - It cites 「小型化PSI/SIMPOS操作説明書 基本編 (SIMPOS5.0版)」, ICOT 1988,
     which is not held.
   - **This gives the Librarian's command vocabulary, from a primary
     source.**

2. **IPSJ 117623, opened, new, downloaded.** 「Common ESPにおけるプログラム
   管理システム」 (AIR, 1989). The CESP librarian is the user interface
   of the program management system. It covers:
   - compiling in inheritance order
   - differential recompilation
   - search
   - a four-phase compile: class template, then class object, then
     machine-independent code, then machine code

   This mirrors SIMPOS's source/template/object triple (TR-057 p10).
   https://ipsj.ixsq.nii.ac.jp/records/117623

### Shell, top level and Coordinator

1. **IPSJ 117622, opened, new, downloaded.** 「Common ESPにおけるプログラ
   ミング環境」 (1989). The CESP environment is built on GNU Emacs:
   - a CESP shell, which manages subsystems
   - the librarian
   - the debugger
   - user-registered programs
   - "situation" (`error_bank`, `document_bank`)

   It differs from SIMPOS's window-based system menu.
   https://ipsj.ixsq.nii.ac.jp/records/117622

2. **IPSJ 118568, opened, new, downloaded.** 「Common ESPにおけるシステム
   コーディネート方式」 (1990).
   - "System coordinator" here means selective system generation (the
     linker, the info table and the indirect-word table). **It is not the
     SIMPOS Coordinator.**
   - Fig. 1 lists the CESP subsystems: librarian, compiler, editor,
     debugger, kernel, C interface, window (X), IPC, I/O libraries and
     general libraries.

   https://ipsj.ixsq.nii.ac.jp/records/118568

3. **IPSJ 120512, opened, new, downloaded.** CESP multiprocessing:
   `:fork(#emacs_process,P)`, `#process` and `:subgoal`.
   https://ipsj.ixsq.nii.ac.jp/records/120512

4. **IPSJ 118567, opened, new, downloaded.** An overview of the basic
   specification of CESP. https://ipsj.ixsq.nii.ac.jp/records/118567

5. **IPSJ 4663, opened, new, downloaded.** 情報処理 32(6) (1991)
   pp.694-703, the Common ESP survey article. Its environment section is
   based on Emacs. https://ipsj.ixsq.nii.ac.jp/records/4663

### Other SIMPOS subsystems and applications

All of these were opened, are new and were downloaded.

- **IPSJ 114011**: the call counter, a window tool that completes the
  1986 series, which is otherwise held.
- **IPSJ 114015**: SIMPOS e-mail.
- **IPSJ 116733**: MELCOM PSI network applications (1989).
- **IPSJ 22404**: SEMACS (IPSJ SE SIG, 1988).
  - It reuses Pmacs, SIMPOS's editor: 93 classes (81 unmodified and 12
    renamed), about 14,300 lines.
  - It cites the unheld 「ICOT: SIMPOS 文書編集機能説明書」 (1987).
- **IPSJ 114484** is KAPPA on PSI, and **IPSJ 117096** is SAM on PSI.
  Both are applications, of low relevance.

Records are at `https://ipsj.ixsq.nii.ac.jp/records/<id>`.

### Held CESP applications (an observation inside held material, no fetch)

These are the IFS archives `kbms-clp/cesp/cal-cesp.tar.Z` and
`natural-lang/cesp/kwic-cesp.tar.Z`. They were extracted to scratch and
read as text.

- CAL's `control.esp` declares
  `class cal_window has nature emacs_io_buffer, emacs_window;`. It uses
  `#emacs_window`, `#symbolizer`, `#library`, `#pathname` and
  `#standard_io_buffer`.
- KWIC-CESP draws its windows with Motif in C (`source/xwindow/*.c`,
  `.uil`), not with CESP window classes.

So neither shows the CESP `#window` library in use.

## Downloaded

There are 15 PDFs. Each has a line in `../../nonlocal/lit/SOURCES.tsv`
and `SHA256SUMS`. The files sit at `nonlocal/lit/ipsj/<id>_<file>.pdf`,
which is gitignored.

They are IPSJ digital library papers. IPSJ publishes them free of
charge, but no redistribution terms were found, so only the manifest is
committed.

The records are 114011, 114015, 114484, 115459, 116733, 117096, 117622,
117623, 118567, 118568, 118569, 120512, 122601, 22404 and 4663.

## Leads (recorded, NOT contacted)

1. **CESP was distributed as source.**
   - The 1992 comp.lang.prolog post (Univ. Nice author) is archived at
     https://discmaster.textfiles.com/view/28246/NN_1992_30.iso/spool/comp/lang/prolog/2249.
     It says CESP was available on request from cesp-request@air.co.jp,
     on a data cartridge with "source codes and the four volumes
     documentation".
   - The recipients would have been universities and laboratories.
   - CESP's window library re-implements the SIMPOS window spec, so a
     surviving copy would be the strongest stand-in short of SIMPOS
     itself.
   - AIR's domain later passed to an unrelated company (Wayback,
     air.co.jp from 1998).
2. **CESP manuals.** These are citation-only in CiNii, and no holding
   library was found:
   - 「CESP言語」 (1990, 1991; 3版, 3.0版)
   - 「CESP ライブラリI/II」 3版 (1991)
   - 「CESP 関連マニュアル」 (AI言語研究所)
   - "CESP Ver. A00" (1994, AI Languages Research Institute, Mitsubishi
     Denki)
   - 「Common ESP 成果発表会講演資料」 (1991)
3. **CESP user institutions** named in papers: ETL (田島守彦), 拓殖大学
   (until 1997), 港湾短大, ASTEM (Fortran interface report, 1991) and
   Oki (CESP development, 沖電気研究開発 58 (1991) p.77).
4. **People.**
   - The AIR authors: 実近憲昭, 中澤修, 田中吉廣, 松浦聡, 佐藤良治,
     木村兼江, 内田洋一, 鳥居悟, 佐藤泰典 and 萩原つね子.
   - The authors from 三菱電機東部コンピュータシステム, who wrote the
     Librarian customisation paper: 児玉泰子 and 藤本誠司.
5. **SIMPOS manual titles not held anywhere found:**
   - 「ESPプログラミング説明書－入出力管理編」 (cited by IPSJ 118569)
   - 「小型化PSI/SIMPOS操作説明書 基本編 (SIMPOS5.0版)」 1988 (IPSJ 118681)
   - 「小型化PSI ESP 説明書 (SIMPOS 3.1版)」 1988
   - 「SIMPOS 文書編集機能説明書」 1987 (IPSJ 22404)
   - 「SEMACS 使用説明書」 1988
6. **Located only, not opened:**
   - bit 22(1)-(12) (1990), 「ESPerへの道」, a 12-part ESP tutorial.
   - 沖電気研究開発 54(1) (1987) pp.37 and 43, on PSI architecture and its
     programming environment.
   - 沖電気研究開発 57 (1990) p.59 (森健, 岩永理美子, the ESP programming
     environment).
   - The Oki CESP article (NDL R000000004-I3726327, digitised).
   - 日本の科学と技術 26(232) (1985) pp.56-66 (dl.ndl.go.jp/pid/2295748)
     and エレクトロニクス 30(2) (1985) pp.103-105 (pid/3281141). Both
     are digitised but can be read only at NDL.
   - The JSSST 1988 SEMACS paper.

## Negative results

| Source | Result |
|---|---|
| IPSJ digital library | 全国大会 coverage starts at the 33rd meeting (1986-10). Talks from 1983 to spring 1986 are not online. |
| IPSJ record neighbours | Records walked by ID found nothing further: 118674-118690, 118585-118596, 118562-118573, 117617-117626, 120504-120514, 114003-114005 and 114018-114022. |
| CiNii Research / Books | No CESP, ESP or 小型化PSI manual is held in any library. Only the five JAIST SIMPOS items already recorded. |
| NDL Search | No more manuals. Rate-limited (429), retried with spacing. |
| 三菱電機技報 | Every PSI issue was already held: 8609, 8707, 8802, 8812, 8907, 9106 and 9111. |
| GitHub repository search | Searched simpos, cesp, icot, kl0, "esp prolog" and others. The only hits were the owner's own repositories. |
| Software Heritage | It served a bot challenge, which was not bypassed. Not searched. |
| Wayback (CDX) | aitec.icot.or.jp: 0 captures. www.air.co.jp: 14. air.co.jp: about 5,000, an unrelated company from 1998. mecs.co.jp: 175, not examined. Filtered queries failed while the Internet Archive was intermittently offline. |
| Discmaster | Filenames only: Guile `simpos.h/.c` and a BBS `CESP.BAT`, both unrelated. |
| CHM catalogue | No PSI or SIMPOS items found. |
| IPSJ computer museum and 未来技術遺産 | The MELCOM PSI page was already held. Nothing new. |
| Auction and bookseller listings | Web searches found no SIMPOS, PSI or CESP manuals or media for sale. |
| IFS newsletter No.4 (1992) | Its CESP and AIR statement was already known. |
| Feigenbaum & Shrobe, FGCS 9 (1993) | Fetched (Stanford copy) and read. A general survey with nothing on SIMPOS's internals. Not added to the manifest. |
