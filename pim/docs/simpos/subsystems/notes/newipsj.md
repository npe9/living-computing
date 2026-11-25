# newipsj: three IPSJ papers, read from 300 dpi page images

Held files, all read-only, all with NO text layer (pdftotext returns nothing). Every page was rendered at 300 dpi and read by eye. The tables and figures were also cropped and zoomed.
- A = lit/ipsj/118569_KJ00001338185.pdf (2 pp.)
- B = lit/ipsj/122601_KJ00001344314.pdf (2 pp.)
- C = lit/ipsj/22404_IPSJ-SE88063003.pdf (8 pp.)

Citations use the form "A p2" (PDF page index), with the printed folio in brackets.

Grades follow RULES: PRINTED-INTERFACE, PROSE, INFERENCE. Japanese renderings are labelled TRANSLATION.

Arity convention: this file counts the receiver, as required/ does. Paper B uses the same convention. This was checked against held code: B prints `:get_mouse_position/3`, and euod holds `:get_mouse_position(Display_window,X,Y)` (euod/PROOF/proof1.esp:256). The other matches:
- `:retract_all/4` matches `:retract_all(#library_utility, Obj!database_class, node, 2)` (cal-esp/cal2.12/graph.esp:237).
- `:draw_filled_circle/5` matches `:draw_filled_circle(W,X,Y,7,set)` (gog-esp/DISPB2.ESP:94).
- `:read_with_click/3` matches `:read_with_click(W,Code0,Click)` (fuzclust/src/menu.graph:121).
- `:draw_line/8` matches `:draw_line(Display,X1,Y1,X2,Y1,1,solid,set)` (euod/PROOF/proof1.esp:539).

All of these are INFERENCE, made by comparing the paper with held USAGE.

---------------------------------------------------------------------
## WINDOW (+ LIBRARIAN/OTHER rows): Paper B 122601, 田島守彦 (ETL), 「ESPプログラムのCESPシステムへの移植事例」

Bibliographic details:
- "A Case of Transplantation of ESP Programs to the CESP System".
- IPSJ 第45回(平成4年後期)全国大会 (45th national convention, latter half of 1992). Paper 2Q-10, pp. 5-45 and 5-46 (B p1 [5-45], B p2 [5-46]).
- The acknowledgements thank 田中吉廣 and 松浦聡 of AI言語研究所 (AIR), the joint-research partner.

### Setting (PROSE, TRANSLATION, B p1)
- RLS (Recursive Learning System) and RLS-Othello were developed in ESP on SIMPOS. The machine was a MELCOM PSI-II (200 ns version) with 12 MW of memory (40 bit/W).
- The application is 12 files, 107 classes and 152 KB of source. It creates huge numbers of instances at run time.
- The target was CESP 3.2, the machine-code-generating version (機械語生成版) as opposed to the emulator version (エミュレータ版). It ran on a SPARCstation 2 under OS 4.1.1, with 48 MB of main memory and 92 MB of swap. CESP's window function uses X-Window.
- §3: on SIMPOS, the OS supplies window and file resources and also the meta-predicates `:assert`, `:retract` and `:clause`. In Prolog these belong to the language. CESP has its own equivalents, but many classes and methods differ, especially in the window environment. (PROSE)
- Two porting methods:
  - (1) Define the SIMPOS classes and methods in CESP, mostly by multiple inheritance from CESP classes. 12 such classes were defined together in a dedicated file called `espclass`. An inheriting class may recursively define a method of the same name, which needs control by cutting the superclass method.
  - (2) Rewrite the program directly. This was used for hardware-level differences such as pixel counts, and for classes that will not change on the ESP side.
  - Method (1) was used wherever possible.

### SIMPOS classes the RLS port needed (§4.1, B p1-p2). All PRINTED-INTERFACE names, given in print order.
(1) "Defined directly by (multiple) inheritance of CESP classes" (CESPｸﾗｽの(多重)継承で直接定義):

| class | note |
|---|---|
| standard_scrolling_menu | |
| standard_io_window | |
| window_without_label | |
| as_mouse_input | |
| labeled_sash | |
| as_scroll | |
| monogyny_hash_index | not a window class (INFERENCE) |
| library_utility | not a window class (INFERENCE) |

Eight names are printed. §3 says the espclass file defines 12 classes, INFERENCE: the count closes as 8 here + choice_window + popup_choice_window + as_markers + marker = 12, since method (1) of §3 covers all of §4.1.

(2) "Separately define a class that inherits a CESP class, and use it": recommended when CESP and ESP have a same-named method with different behaviour, so that the CESP class is used only indirectly.
- choice_window
- popup_choice_window

(3) "Defined entirely new" (全く新しく定義):
- as_markers, with the note "define `marker` separately and use it" (markerを別に定義して利用する).

### Method/macro conversion table (§4.2, B p2). Transcribed exactly. The paper says left = ESP and right = CESP, and that many of the changes seem unnecessary. Grade: PRINTED-INTERFACE.

| ESP (SIMPOS) as printed | CESP as printed | note |
|---|---|---|
| `:kill(Window)` | `:close(Window)` | |
| `:retract_all/4` | `:abolish/4` | |
| `:write_lines/2` | `:write_line/2` | |
| `:write(W,key#cr),:write(W,key#lf)` (ONE entry: the SIMPOS newline pair) | 前半のみ, "only the first half" (TRANSLATION) | CESP needs only `:write(W,key#cr)`. The pair is printed as one comma-joined run, with the right column pushed over, laid out like the `key#enter, keypad#'0'` row. INFERENCE, backed by held USAGE of the pair: kappa2/kappa2/utility/fmp/FCWIN.ESP:53-54, 88-89; utter/source/Sancho/sancho.esp:63-64. `key#cr` and `key#lf` are both SIMPOS keycodes. |
| `:get_mouse_position/3` | (no CESP name) unitで割って使用 | "use it divided by the unit" (TRANSLATION) |
| `:draw_line/8` | `:draw_abs_line/5` | |
| `:draw_filled_circle/5` | 同名ﾒｿｯﾄﾞ/7 | "same-named method /7" |
| `#font_13` | `"a14"` または `"a24"` | "a14" or "a24" |
| `control#"c"` etc. | `key#etx` etc. | |
| `mouse#r` etc. | `'mouse#r'` etc. | quoted atom in CESP |
| `key#enter`, `keypad#'0'` etc. | なし | "none" |
| `dynamic((pl/al, ..))` | `dynamic pl/al, ..` | The glyphs look like "pl/al", which is probably meta "p1/a1", i.e. predicate/arity. This is a declaration-syntax difference. |

### §4.3 Other (B p2, PROSE, TRANSLATION)
- CESP lacked the mouse-reading method `:read_with_click/3`, which returns the item together with the click kind (l, m, r) at the same time. Implementing it in CESP was hard, so it was requested and was adopted in the latest version, 3.3.
- The string base point differs: top left in ESP, bottom left in CESP. The author calls this an unnecessary change.
- "Catalog (compile)" (カタログ(コンパイル)) has a restriction that the manual does not mention. In CESP, a class referenced by a slot-initialisation predicate must be in a separate file and catalogued beforehand.
- Terminology: SIMPOS/ESP "catalog" = compile (PROSE).

### §5 Speed comparison (B p2, PROSE, TRANSLATION)
- First measurement: **catalog (compile) time of the whole program.** The CESP program includes the espclass file. ESP on PSI-II 3'30", CESP on SS2 11'15". "ESP's catalog is more than 3x faster" (ESPのｶﾀﾛｸﾞが3倍以上速い).
- Simple programs. `ackerman/3` is the Ackermann function. `reverse/2` reverses a list and also reverses inside elements recursively. The input was a 10-level list with 10 elements per level.
  - ackerman(3,8,R): 33" vs 51"
  - reverse(L,R): 6" vs 10"
  - "That is, ESP is about 1.5x faster than CESP."
- Display to windows was somewhat faster on the CESP system, which the author attributes to hardware display ability.
- §6 conclusion:
  - CESP catalog time is very slow.
  - Catalog order has restrictions not in the manual.
  - PSI-III (MELCOM PSI/UX) is said to run programs about 4x as fast as PSI-II (200 ns).
  - CESP machine-code programs are about 2x the emulator version.
  - AIR plans to keep only the emulator version. The PSI-III ESP : SS2 CESP (emulator) speed ratio would then be about 12, so the plan may be premature.
  - The author wishes for porting aids, in this order: an ESP-to-CESP converter, an espclass-like module, and a collection of conversion examples or a correspondence table.

---------------------------------------------------------------------
## WINDOW (CESP successor): Paper A 118569, Common ESP window system implementation

Bibliographic details:
- 木村兼江*, 佐藤良治*, 国府田明弘**, 実近憲昭*. * = (株)AI言語研究所, ** = 日本ビジネスオートメーション(株).
- 「Common ESP ウインドウシステムの実現方式」, "Implementation of Common ESP window system".
- IPSJ 第40回(平成2年前期)全国大会 (first half of 1990). Paper 4G-8, pp. 716-717 (A p1 [716], A p2 [717]).
- The month is not printed on the pages.

### What it says about SIMPOS (the only SIMPOS statements in the paper)
- §2(2) External spec (A p1): the CESP window system's external specification is not that of any particular workstation window system. It is "developed based on the specification of the SIMPOS window system for ESP on PSI" (PSI上のESP用SIMPOSウインドウシステムの仕様をベースに開発する). The reason given is that following one workstation's window system too closely would hurt portability. (PROSE)
- Nothing else in the paper is said to be SIMPOS. Fig. 2 is captioned 「CESPウインドウクラス」 ("CESP window classes"). It is the CESP basic-version library, NOT a list of SIMPOS classes.

### CESP facts (PROSE unless noted; CESP basic-spec version 1990)
- The system adopts X and supports the equivalent of the Xtoolkit Intrinsics level. It is supplied as a window library package, not in the CESP language spec.
- It is accessed through CESP window methods, just as ordinary message passing is.
- Several window classes were made with reference to Xtoolkit widgets.
- One window is one CESP object. Window attributes are held as slot values. A window-creation method creates the instance, and later operations go to that instance.
- Inheritance is CESP's own, closed within CESP; Xtoolkit inheritance is not used.
- (3) The basic version gives window operations, menu operations and graphics. It is implemented as synchronous control written explicitly by the user. The next year's extended version is to add callbacks, the translation manager, the resource manager and asynchronous processing.
- §3(1): two designs were considered, (a) integrated with the CESP processor and (b) a separate process. (a) was chosen because CESP process management was still in development.
- All window methods are synchronous, and no data is shared with other processes.
- §3(2) Fig. 1 shows the chain CESP processor ⇄ CESP interface part (written in CESP) ⇄ C interface part (C, using Xtoolkit/Xlib) ⇄ window system. Porting to a non-X window system means rewriting only the C part.
- §3(3) Fig. 2, the window classes available as the library. PRINTED-INTERFACE; the names are exact, read from a zoomed crop:

| class | function as printed (TRANSLATION) |
|---|---|
| #window | テキストウインドウ操作機能, text-window operations |
| #menu | メニュー操作機能, menu operations |
| #as_superior | 親子ウインドウ操作機能, parent/child window operations |
| #with_pane | 親子ウインドウ操作機能, parent/child window operations (same text as as_superior) |
| #with_border | ボーダ操作機能, border |
| #with_label | ラベル操作機能, label |
| #with_font | 文字フォント操作機能, character font |
| #as_cursor | カーソル操作機能, cursor |
| #as_input | 入力操作機能, input |
| #as_output | 出力操作機能, output |
| #as_mouse | マウス操作機能, mouse |
| #as_graphic | グラフィック操作機能, graphics |
| #as_scrollbar | スクロール操作機能, scroll |
| #as_dialogbox | ダイアログボックス操作機能, dialog box |
| #event | イベント操作機能, event |

  - The paper does not call these "mixins" or natures. That word is the web summary's interpretation (INFERENCE).
  - Compared with SIMPOS as held (INFERENCE): held code uses `as_graphics` (plural), `as_mouse_input` and `as_scroll`. CESP spells them `as_graphic`, `as_mouse` and `as_scrollbar`. `with_border`, `with_label`, `as_superior`, `as_input` and `as_output` share names with held SIMPOS natures.
- Methods printed: `:create` creates the CESP window object and shows it on the screen, and `:close` deletes it (A p2, PRINTED-INTERFACE, no arity given).
  - Between the two, a window can be moved, have its display changed and be iconified, have attributes set or read, and do I/O.
  - The names `:create` and `:close` are unified with CESP standard I/O.
  - INFERENCE: this matches B's `:kill(Window)` → `:close(Window)`, so SIMPOS's `:kill` was renamed in CESP.
- §3(4) data conversion: CESP tagged data is converted to and from C in the C interface part. Attribute-read methods return the slot value without asking the window.
- Reference [1] is 「ESPプログラミング説明書－入出力管理編」, which is not held. The title says "ESP", while the paper writes "CESP" for everything of its own. So it may be the PSI/SIMPOS-side ESP manual for I/O and windows, the spec basis. Unresolved (INFERENCE).

---------------------------------------------------------------------
## OTHER (Pmacs editor): Paper C 22404, SEMACS (Pmacs-based structure editor)

Bibliographic details:
- 吉武淳 (三菱電機 コンピュータ製作所), 小久保岩生 and 藤田正幸 (三菱総合研究所), 梶山拓哉 (アーティフィシャル・インテリジェンス), 坂井公 and 横田一正 (ICOT).
- 「ESPを用いて開発した汎用構造エディタSEMACS」, "Grammar-independent Structure Editor SEMACS developed by using ESP".
- IPSJ SIG ソフトウェア工学 63-3, 1988-11-25. Eight pages, folios (1)-(8) = C p1-p8.

### Pmacs / SIMPOS editor facts
- "Pmacs, the text editor on PSI" (PSI上のテキストエディタであるPmacs): C p3 [3] §2.2 and C p7 [7] §4.2.4. (PROSE)
- SEMACS = "Syntax-directed Extension of pMACS" (C p1).
- In string mode (文字列モード), almost all of Pmacs's editing commands can be used (C p3 §2.2). No command names are printed.
- SEMACS "is basically built on Pmacs" (C p7 §4.2.4).
- Tables 4.2.4-1 and 4.2.4-2 (C p8, PRINTED-INTERFACE). Values in parentheses = reused from Proton's tree-display module (カッコ内はProtonの木表示モジュールからの流用分, C p7).

| classes | Pmacs | SEMACS |
|---|---|---|
| unmodified 無修正 | 81(12) | 81(12) |
| class renamed クラス名変更 | 12 | 12 |
| classes added クラス追加 | -- | 64 |
| total 合計 | 93(12) | 157(12) |

| lines | Pmacs | SEMACS |
|---|---|---|
| unmodified | 約14,000(1000) | 約14,000(1000) |
| modified 修正 | 約300 | 約300 |
| new 新規作成 | -- | 約7,000 |
| total | 約14,300(1000) | 約21,300(1000) |

- How to read the table:
  - The "Pmacs" column is the reused base, i.e. Pmacs plus 12 Proton classes of about 1,000 lines.
  - INFERENCE: Pmacs proper is therefore 93-12 = 81 classes and about 13,300 lines, if the parenthetical counts are a subset. The table is ambiguous about this. The totals 93(12) = 81(12)+12 suggest a subset.
  - Text (C p8): the modification was about 300 lines, "only about 2% of all of Pmacs". Classes were reused almost 100% with only class renaming. The 64 new classes and 7,000 lines are about 30% of SEMACS.
- No Pmacs class, buffer or window class names are printed anywhere in the paper.
- Held code shows `pmacs_window` and the `with_pmacs_window` nature (required/requirements.tsv). That is USAGE, not from this paper.
- Buffers (C p7 §4.2.1, PROSE): a SEMACS buffer (バッファ) is an instance object. It holds as internal state:
  1. text information
  2. structure information (itself an instance object, a has_a relation; §4.2.2)
  3. edit mode
  4. grammar name

  Switching buffers switches grammar and resumes editing in the prior state.
  - C p5 §3.3(2) mentions "another window (buffer)" (他のウインドウ(バッファ)), equating windows with buffers.
  - INFERENCE: this buffer model is SEMACS's extension, but the buffer and window concept comes from Pmacs.
- SEMACS structure-mode commands (C p3-p4 §2.2, PROSE; SEMACS, not SIMPOS):
  - Mode switching, four commands: struct→string (the area becomes text to edit); struct→string (delete the area's contents); string→struct (parse the area); string→struct (return to the previous structure-mode area).
  - Tree display, an extended version of the tree-display module of ICOT's expert-system tool Proton.
  - Grammar guide (文法案内): the possible expansions of the area's top category are shown as a menu window. One mouse click expands; "another click" shows detail recursively.
  - Area movement by parent, child or sibling, or by mouse.
  - Search and replace.
  - Others: delete/restore the area; insert/delete list elements; save/load the syntax tree; holophrasting.
  - The area is shown in reverse video, and unexpanded nonterminals are shown as `$symbol`.
  - Parser: LDT, an improved BUP, from Sakai 1986.
- Development took 5 people, not full time, for under a year (C p7 §4.1.3).
- Used in CAP (proof editor for PDL) and Kappa (schema-maintenance tool) (C p6 §3.5).
- Acknowledgement (C p8): 佐藤裕幸 of ICOT 第4研究室 advised on Pmacs. INFERENCE: probably a Pmacs author or maintainer.

### SIMPOS document editing
- The ONLY mention is reference [3]: "ICOT: SIMPOS 文書編集機能説明書, 1987" (SIMPOS Document Editing Function Manual) (C p8). It is not cited in the body text that I could find. The paper says nothing else about it.
- Reference [4] is "ICOT: SEMACS 使用説明書, 1988" (SEMACS user's manual). Neither manual is held.

---------------------------------------------------------------------
## LIBRARIAN (from B)
- In SIMPOS/ESP, "catalog" (カタログ) = compile (B p2 §4.3, PROSE).
  - INFERENCE: SIMPOS cataloguing goes through the Librarian. B does not say so.
- RLS + RLS-Othello (12 files, 107 classes, 152 KB) catalogue in 3'30" on PSI-II (200 ns) (B p2 §5, PROSE).
- The catalog-order restriction not in the manual is a CESP restriction, not a SIMPOS one (B p2 §4.3).
- `library_utility` is in partition_librarian.tsv. Its class method `retract_all/4` becomes CESP `abolish/4` (B p2 §4.2).

## SHELL
- Nothing in any of the three papers.

## POSSIBLE SIMPOS CODE
None. The papers print no SIMPOS code bodies. B's table and class list are interface names only. The `espclass` file B describes, CESP re-implementations of 12 SIMPOS classes, would be a valuable CESP-side emulation of SIMPOS window classes if it survives somewhere (RLS at ETL/AIST). It is not held.

## Corrections to web_search_2026-11-24.md (lines 25-110, 195-210)
1. 118569, Fig. 2:
   - It is captioned 「CESPウインドウクラス」. These are CESP library classes, not SIMPOS's class set.
   - The paper does not call them mixins.
   - The claim that it is "the nearest thing to a statement of SIMPOS's window class decomposition" overstates it. Only §2(2) says the spec is based on SIMPOS's.
   - Its spellings differ from held SIMPOS (`as_graphic`/`as_graphics`, `as_mouse`/`as_mouse_input`, `as_scrollbar`/`as_scroll`).
   - #with_pane has the same description as #as_superior (parent-child).
   - The date "1990-03" is not printed; the page says only 平成2年前期. Paper no. 4G-8.
2. 122601, method table:
   - `:kill(Window)` → `:close(Window)`, with arguments printed on both sides.
   - "`key#cr`→`key#lf`" is WRONG. The ESP entry is the newline pair `:write(W,key#cr),:write(W,key#lf)`, and CESP keeps only the first half (前半のみ).
   - `:get_mouse_position/3` has no CESP name: "use it divided by the unit".
   - The table also has a row `dynamic((pl/al, ..))` → `dynamic pl/al, ..`.
   - `#font_13` → `"a14"` or `"a24"` is correct.
   - Arity convention: the receiver IS counted (matches held code), so the arities are directly comparable with requirements.tsv.
3. 122601, class list:
   - Group (1) is defined directly by (multiple) inheritance.
   - Group (2) is made by subclassing CESP classes: choice_window and popup_choice_window.
   - Group (3) is all-new: as_markers, with `marker` defined separately.
   - The espclass file holds 12 classes: 8 + 2 + as_markers + marker (INFERENCE).
   - library_utility is a librarian-partition class, not "outside the window system" generically.
4. 122601, timing:
   - The 3'30" vs 11'15" measurement is **catalog (= compile) time**. It is stated explicitly, and the CESP side includes espclass. The paper says ESP is "more than 3x faster".
   - The 1.5x figure is for ackerman/reverse only.
   - Window display was somewhat faster on CESP.
   - PSI-III ≈ 4x PSI-II (200 ns), as "it is said". CESP machine-code ≈ 2x emulator. PSI-III : CESP emulator ≈ 12.
   - The year is 1992, latter half (平成4年後期); pp. 5-45 and 5-46; paper no. 2Q-10.
5. 22404:
   - "12 renamed" is right, but the table's parenthetical (12) / (1000) is the share reused from Proton's tree-display module. Pmacs proper may be 81 classes and about 13,300 lines.
   - About 300 lines were modified, about 2% of Pmacs.
   - SEMACS total is 157 classes and about 21,300 lines.
   - No Pmacs class names are printed.
   - The SIMPOS 文書編集機能説明書 is only in the reference list.
   - Date 1988-11-25, SIG SE 63-3.

## PAGES READ
- Every page was rendered at 300 dpi and read by eye.
- Zoomed crops:
  - A p2: Fig. 2
  - B p2: §4.1 class list, §4.2 table, the dynamic row, §4.3
  - C p8: tables 4.2.4-1 and -2
- Downscaled full pages only, all legible: A p1; B p1 (start of the class list); B p2 §5 timing; C p1-p7.
- OCR: none used.

## CHECKED, NOTHING
- A p1: no SIMPOS class or method names, only the spec-basis sentence.
- C p1-p2, p4-p6: SEMACS grammar, examples and parser only; no SIMPOS/Pmacs names.
- SHELL: nothing. LIBRARIAN: only B's catalog facts (see the LIBRARIAN section). B also mentions SIMPOS supplying files and `:assert/:retract/:clause` as OS facilities, and `library_utility` (INFERENCE: probably SIMPOS library utility, not the Librarian UI).

## OPEN QUESTIONS
- B: confirm that `marker` is the 12th espclass class.
- B: is "pl/al" a placeholder for p1/a1 (pred/arity)?
- C: is the Proton parenthetical a subset of 93 or additional to it?
- A: is ref. [1] 「ESPプログラミング説明書－入出力管理編」 a SIMPOS manual (ICOT) or an AIR/CESP manual? It is not identified on the page.
