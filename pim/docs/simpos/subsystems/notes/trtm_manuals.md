# trtm_manuals: SIMPOS as users met it, from three ICOT user manuals (TM-785, TM-786, TM-404) plus TM-401 and TM-430

Sources, all in `pim/docs/nonlocal/lit/trtm/`:
- **TM-785** 「PSI図形ツールのインストール方法」 + 「PSI図形ツール 説明書」. Author 東 吉郎, Aug 1989, 40pp.
- **TM-786** 「オンラインSIMPOS照会書 操作説明書」. Author 東 吉郎, Aug 1989, 12pp.
- **TM-404** 「ネットワークニュース使用手引き」. JIPDEC, Oct 1987, 39pp. **This is a UNIX/SUN manual, not SIMPOS** (see OTHER).
- **TM-401** p10-11 (file manipulator remote access) and **TM-430** (TCP/IP), checked.

Page transcriptions, one file per page:
- `work/trtm_manuals/TM-785_pNN.txt`. TM-785_p33.txt covers pp33-36.
- `work/trtm_manuals/TM-786_pNN.txt`.
- The whole of each report is also in TM-785_all.txt and TM-786_all.txt.

Citations use PDF page index; the printed folio is given as "f.N". Every Japanese gloss is TRANSLATION. Version is 1989 throughout. TM-786 shows **SIMPOS 5.0** in its screen examples, so these manuals describe SIMPOS 5.x, the same era as the held programs.

## LIBRARIAN

| Fact | Grade | Cite |
|---|---|---|
| The install procedure is literally: ① create a Librarian (ライブラリアンを生成する); ② put the floppy in unit 0; ③ select the Librarian's 「Execute」; ④ type `fdd("drawing.com")` at the `Command>` prompt, then Return; ⑤ the system asks `FDD mount ok?` and then a unit-number prompt; type `0` with no Return; ⑥ installation takes about 1 minute | PROSE (TRANSLATION) | TM-785 p3 f.1 |
| The same procedure for package `simshow` uses `Command>fdd(" simshow.com")`; it installs in about 45 seconds | PROSE | TM-786 p4 f.1 |
| The unit prompt is printed differently in the two reports. TM-785 p3 has `Input unit No. (0):0` (capital I, space before "(0)", no space after the colon). TM-786 p4 has `input unit No.(0): 0` (indented on its own line). Both were read at 400dpi. The default unit is shown as `(0)`, and the answer is one keystroke with no Return | SCREENSHOT | TM-785 p3; TM-786 p4 |
| Command language: an `fdd(FileName)` command takes a command file (`.com`) from floppy and executes it. The `.com` contents are not printed in either report | PROSE | TM-785 p3; TM-786 p4 |
| Each of these tools is installed into a package of its own name: `drawing`, `simshow`. Installation fails if the package exists ("インストールできない"), unless the user erases it | PROSE | TM-786 p4; TM-785 p3 |
| **Error window**, inverse title bar: `Error occurred in librarian_59( process 59 )`. Body: `Package drawing already exists` / `Cannot load package_template_file`. A second inverse bar reads `Error handling menu:`, with three items: `Erase existing package and continue` / `Inspect the information of this event` / `Return to librarian top level`. Read at 400dpi | SCREENSHOT | TM-785 p3 |
| In that image the word "drawing" is in a larger face than the rest, as if pasted in | SCREENSHOT | TM-785 p3 |
| Choosing "Erase existing package and continue" brings up a confirm menu titled `Really?` with items `ERASE` and `STOP`. ERASE continues the install (about 1 minute); STOP stops it | SCREENSHOT | TM-785 p3 |
| Choosing "Return to librarian top level" returns to the Librarian screen (ライブラリアンの画面) | PROSE | TM-785 p3 |
| The Librarian process is named `librarian_<n>`, here 59, with process number = n | SCREENSHOT | TM-785 p3 |
| Debugger start of a package (procedure): in the Librarian, set the package to "simshow" (パッケージを"simshow"に設定) and load all of the package's contents (全部ロード). Then type the calls in the debugger | PROSE | TM-786 p5 f.2 |
| The term "package template file" (`package_template_file`) appears as an error-message noun | SCREENSHOT | TM-785 p3 |

Corrections to the repo's `listings/TM-785_p03.txt`, for the caller; I have not edited it:
- The error-menu lines are now confirmed by eye at 400dpi (that file says "from OCR").
- The confirm menu's title `Really?` is missing there; it only says "確認画面 → ERASE/STOP".
- Step ③/④ is missing: ERASE leads to a re-install of about 1 minute.
- "drawing" is pasted-looking in the image.

## SHELL / system menu / login file / debugger

| Fact | Grade | Cite |
|---|---|---|
| Shell start: `$ call simshow##simshow` ("シェルから … で起動する"). The prompt is `$`, the command is `call`, and its argument is Package##Class | PRINTED | TM-786 p5 f.2 (400dpi) |
| Debugger start: `:create(#simshow##simshow, S),` then `:goal(S).` typed "from the debugger" (デバッガから). The class object is written `#Pkg##Class`. The program is started by sending `:goal/1` to the instance (arity 1 counting the receiver). INFERENCE: the class inherits `as_program` or a similar class whose `:goal` is the entry point | PRINTED | TM-786 p5 (400dpi) |
| Method-call start of another tool: `:drawing(#drawing##psi_drawing_tool)` (a class method `drawing/1`). It "runs on the process that called the method" (メソッドを呼び出したプロセス上で実行する) | PRINTED | TM-785 p6 f.1 |
| Same for the generator: `:generate(#drawing##drawing_class_generator)`, class method `generate/1`. Runs in the caller's process | PRINTED | TM-785 p25 f.20 |
| **System menu via the login file, form A** (TM-786). The text says to define the class `simshow##simshow` in the login file (ログインファイル). Example as printed: `menu :- ………… {"simshow",simshow##simshow} , …………`. The item is a stack vector `{"Label", Pkg##Class}` with a string label | PRINTED | TM-786 p5 |
| **System menu via the login file, form B** (TM-785). "Add psi_drawing_tool to items_list in the login file's menu item." Example as printed: `menu:- items_list([ {'debugger', debugger}, . {'PsiDraw', drawing##psi_drawing_tool}]).` The label here is a quoted atom | PRINTED | TM-785 p6 |
| Form B again, with more items: `menu :- items_list([ {'debugger', debugger}, {'pmacs', pmacs}, . {'DrawGen', drawing##drawing_class_generator} ] ).` | PRINTED | TM-785 p25 |
| What the examples show about the login file: (a) it contains a clause `menu :- items_list([...])`; (b) system-supplied items appear as `{'debugger', debugger}` and `{'pmacs', pmacs}`, i.e. a bare class name with no package prefix; (c) user items use `Pkg##Class` | PRINTED | TM-785 p6, p25 |
| INFERENCE: the label in form A is in a string and in form B an atom; both forms existed or were accepted. The spec should accept both | INFERENCE | TM-786 p5 vs TM-785 p6 |
| "クラスを定義する" in TM-786 means the class name is the menu item's action. The system menu instantiates the class and runs it | INFERENCE | TM-786 p5 |
| The online SIM照 has 3 equivalent start modes (debugger, shell, system menu); "the behaviour after start is identical" | PROSE | TM-786 p5 |

## WINDOW (system classes and methods visible through the application code and operating instructions)

Window-class facts from the code printed in TM-785 pp28-40 (application code: graph_drawing, generated by the tool):

| Fact | Grade | Cite |
|---|---|---|
| `:create(#standard_window, [size(1280, 944)], Window)`. The create is class-method `create/3` on `standard_window`, and the init list contains `size(W,H)` | PRINTED | TM-785 p30 f.25 (300dpi) |
| `:set_color_pair(Window, Even_number, Colors)`, instance method `set_color_pair/3`. The colour-pairs list is printed as `[{0, 0}, {2, {{30720, 5376, 18944}, {32543, 65535, 0}}}]`. INFERENCE: an even colour number takes either 0 (default) or a pair of {R,G,B} 16-bit triples (foreground/background?) | PRINTED | TM-785 p31 f.26 |
| The p29 comment says a colour number may be given as the drawing "Operation" argument if colours are set first. So the last drawing argument (Operation) is `set`/`reset`/`xor`... or a colour number | PRINTED | TM-785 p29 f.24 |
| Drawing methods are called by name through `:refute(Window, Method, Arguments)`, where Arguments is a stack vector. Generic method dispatch on a window: `refute/3`. Held code also uses `:refute(Obj,Goal,Args)` (e.g. cil/src/es_int.esp) | PRINTED | TM-785 p32 f.27 |
| Drawing method names and arg vectors are in data/2 (repo listing TM-785_p40.esp). Arities counting the receiver: `draw_line/8`, `draw_rectangle/8`, `draw_circle/7`, `draw_arc/9`, `draw_fan/9`, `draw_ellipse/8`, `draw_elliptical_arc/10`, `draw_graph/9`, `draw_polygon/9`, `draw_filled_rectangle/8`, `draw_filled_circle/7`, `draw_filled_ellipse/7` (as printed: only 3 numbers), `draw_filled_fan/9`, `draw_characters/4`. draw_line/8, draw_rectangle/8, draw_filled_rectangle/8, draw_circle/7, draw_arc/9, draw_elliptical_arc/10 and draw_characters/4 match requirements.tsv arities. draw_filled_circle (held /5) and draw_graph/draw_polygon (held /2, /5) differ | PRINTED-INTERFACE | TM-785 p40, p32-36 |
| Argument conventions (from which positions the base X/Y is added to; INFERENCE from modify/6). draw_line: x1,y1,x2,y2,width,linetype,op. Rectangle and filled rectangle: x,y,…; circle/arc/fan/ellipse: centre x,y first. draw_graph/draw_polygon: element 0 is a list of (X,Y) pairs. draw_characters: element 0 is a list of {CharCode, X, Y, W, H}, element 1 is a number, element 2 a font object (the program converts a font path name to a font object before the call) | INFERENCE | TM-785 p32-36, p40 |
| Line-type atoms: `solid`, `dotted`; fill-pattern atoms: `mesh`, `left_hatch`, `small_mesh`, `dotted`; op atoms: `set` (and numbers 2-5 as colour numbers). Attribute-window ops are `set`, `reset`, `xor(exclusive_or)`, `color` | PRINTED | TM-785 p40, p12 f.7 |
| Fonts: `:create(#font, Font_name, Font)`, class `font`, `create/3`, with a path name. Font names in use: `"font_13"`, `">sys>font>kanji_16.font"` (p40), and the logical name `font:kanji_16` in the UI (p17) | PRINTED | TM-785 p37, p40, p17 |
| `:create(#list_index, Bank)` (create/2), `:add_at(Bank, Obj, Key)` (add_at/3) and `:get_at(Bank, Obj, Key)` (get_at/3) on `list_index`; the key is a font name string | PRINTED | TM-785 p37 f.32 |
| Image-transfer logical operations, as named in the UI: `exclusive_or`, `copy`, `reverse` (default copy). Scale types: `magnify` and `expand`, "provided by the window system" (ウインドウ・システムで提供している), default expand. These are probably SIMPOS bitmap operations/methods; no signatures are given | PROSE | TM-785 p19 f.14, p20 f.15 |
| Image data files (`*.image`) can be drawn on a window "with a method the window system provides"; user-made image files must have file type `image` to be loaded | PROSE | TM-785 p21 f.16, p24 f.19 |
| Screen size 1280×944: the default drawing size equals "the screen size" (p9) and is shown as 1280/944 (p10, p23) | PROSE | TM-785 p9, p10, p23 |
| `close` (command-menu item) "erases the tool window and shows an icon" (アイコンを表示する). The window system has iconification | PROSE | TM-785 p9 f.4 |

Window operations that users are told to perform (application UI conventions on SIMPOS windows, 1989):

| Gesture | Effect | Cite |
|---|---|---|
| Left single click | draw / set a point; select a menu item | TM-785 p8 |
| Middle single click | select a figure (cycles through overlapping figures); cancels the last point in polyline/polygon | TM-785 p15, p18 |
| Middle double click | open the figure edit menu (消去/移動/変更/コピー) | TM-785 p18 |
| Right single click | cancel the drawing or edit in progress | TM-785 p8, p13 |
| Left double click on a menu item | open that item's options sub-menu (half-ellipse, quarter-ellipse, characters, move/copy op, scale type, eraser size) | TM-785 p14-21 |
| Left double click | end a polyline/polygon | TM-785 p15 |
| Left button held down | eraser / pencil | TM-785 p20-21 |
| Left double click (TM-786) | in the send step, opens node-name input | TM-786 p10 |
| C-x C-z | ends input in an online-SIM照 form; the title bar shows `(終了 = ^x^z)` | TM-786 p6, p8 |

Dialogue windows with a common shape: a title line, then rows of `label value-choices` with the selected value boxed or underlined, then `do_it   abort`. This shape appears as SIZE, grid, SAVE, Image Size, 文字列描画属性 and Drawing Class Generator (TM-785 p10-p26), and as プリンタ設定 (TM-786 p10). INFERENCE: one SIMPOS "item/attribute-setting window" class, i.e. the do_it/abort sheet seen throughout. Candidate classes were not resolved here; check the partition for a dialogue/sheet class.

Pop-up menus as printed have a title bar (shaded or inverse) and then items: `PSI DRAW` (drawing/image), `which ?` (draw/image), `Really?` (ERASE/STOP), `SIMPOS照会書` and others. Some have no title (TM-785 p18, p19).

## FILES, PATHS, FDD

| Fact | Grade | Cite |
|---|---|---|
| Pathnames: `>sys>simshow>Qbox>*.*` holds saved queries, `>sys>simshow>Abox>*.*` holds received answers, `>sys>font>kanji_16.font` is a font | PRINTED | TM-786 p7, p11, p12; TM-785 p40 |
| Logical-name form `font:kanji_16`, shown in a dialogue | SCREENSHOT | TM-785 p17 |
| File names carry versions: list entries look like `window_error..1`, `window_error..2`, `O/sim_error..1`, `pmacs_quest..1`. The menu shows `name..version`; the first item is `***ABORT***` | SCREENSHOT | TM-786 p7 f.4 |
| Answer-file name pattern `icpsi116-01-May-89-12-00-00.sim.1`, i.e. node-date-time.type.version | PRINTED | TM-786 p12 f.9 |
| Writing an existing output file "makes the file with the version raised by one" | PROSE | TM-785 p27 f.22 |
| File types `draw`, `image`, `esp`, `com`, `sim`. A tool adds its type when the user omits it ("ファイル識別子が無い場合、システムがファイル拡張子'draw'を付ける") | PROSE | TM-785 p22, p23, p27 |
| Users may type a "file name or file path name" into a file-name input window | PROSE | TM-785 p22 |
| FDD: applications cannot write directly to the FDD. To put files on floppy, save to the fixed disk and use the file manipulator. When copying from FDD to the fixed disk with the file manipulator, text-like data needs `copy_text` (printed reading «?», in a face where x and s look alike; no hit in the extracts) and binary images need `copy`. INFERENCE: the file manipulator had separate text-copy and binary-copy commands | PROSE | TM-785 p21 f.16 |
| No delete function in simshow; delete with the file manipulator (ファイルマニピュレータ) | PROSE | TM-786 p12 |
| Output may go to a "text buffer" (テキスト・バッファ) instead of a file; buffer-name clash produces a warning. INFERENCE: a PMACS buffer | PROSE | TM-785 p27 |

## OTHER (network, printing, node names, versions)

| Fact | Grade | Cite |
|---|---|---|
| SIMPOS version in the screen examples: `SIMPOS版名 : 5.0`, `Firm版名 : 1.02`, `CSP版名 : 2.23` (first digit of the CSP value is blurred, «?»). Example dated 29-May-89 | SCREENSHOT | TM-786 p8 f.5 (600dpi; source scan is coarse) |
| TM-786 p6 form shows a default `SIMPOS版名` value read as `5.0HC` «?» (blurred at 600dpi; perhaps `5.0` plus a suffix). Date 14-Jun-89 | SCREENSHOT | TM-786 p6 |
| Node names `icpsi116` (own PSI), `icpsi203` (server); node-name prompt `ノード名を入力して下さい  :` | SCREENSHOT | TM-786 p6, p10 |
| Printer-settings sheet `プリンタ設定`: ノード 自PSI/他PSI; プリンタ シリアル/レーザ; `do_it abort`. Other-PSI printing prompts `レーザプリンタのノード名を入力して下さい  : icpsi???` | SCREENSHOT | TM-786 p10 f.7 |
| Messages: `送信されました` (sent), `セーブできません` (printed as the failure message for send) | PROSE | TM-786 p10 |
| Save prompt `ファイル名を入力して下さい  : simsho_error` saves under `>sys>simshow>Qbox` | SCREENSHOT | TM-786 p11 |
| The application menus of simshow (initial menu, sub-menu, `閲覧`, `終 了` YES/N O), PSI DRAW and the command menu are transcribed in the page files. They are application, not SIMPOS | SCREENSHOT | TM-786 p6-11; TM-785 p7-24 |
| SIMPOS manual cross-reference: 「操作説明書（II）I-2.2.4 カラー・ボード」. A colour board was a SIMPOS-provided facility documented in the SIMPOS Operating Manual vol. II, sec. I-2.2.4 (not held) | PROSE | TM-785 p13 f.8 |
| TM-401 p10-11 (f.9-10): the file manipulator's remote-access functions are a numbered prose list: directory display, copy, append, delete (recoverable until expunged), expunge, undelete, purge old versions, attributes, display as characters, hex dump, rename, create directory, delete directory, password security with 3 access-range levels. **These are function descriptions, not printed menu-item strings**; STRUCTURE.md's "menu items are listed in … TM-401 p10" overstates it | PROSE | TM-401 p10, p11 (eyed) |
| TM-430: nothing about user operation; already covered by STRUCTURE.md (ftp/telnet prototyped as SIMPOS extensions; socket interface as methods) | PROSE | TM-430 p3 (eyed) |
| **TM-404 is about UNIX on SUN/VAX**: JUNET news, readnews/vnews/rn/vn, postnews, `.newsrc`, `/usr/local/bin/Newuser`, passwd, terminal-server login `CS100>>c icot32` then `login:`/`password:`, dec2jis, FTP from VAX to SUN. **Nothing about SIMPOS/PSI**; exclude it from all SIMPOS rows | PROSE | TM-404 p3-5, p8, p13 eyed; rest OCR |

## p40 re-check, and notes on the TSV

- **p40 re-checked at 300dpi.** `draw_filled_ellipse` has 6 elements as printed: `{200, 0, 100, 1, dotted, set}`. This is likely a source slip; `draw_ellipse` has 7.
- **Quote characters on p40.** Char codes print as `16#'2341'` and font names as `'font_13'` and `'>sys>font>kanji_16.font'`, all in SINGLE quotes. The repo's TM-785_p40.esp has double quotes, and its "«?» on quote style" note should be resolved to single quotes.
- **p36 at 300dpi.** `draw_filled_fan` really does use `adjusts` (the list form), unlike `draw_fan`. This looks like a generator bug in the printed example.
- **TSV class-column placeholders.** `librarian`, `shell`, `login_file`, `system_menu`, `window`, `file_system`, `file_manipulator` and `system` are placeholders, not SIMPOS class names.
- **Held login.com files not searched.** I did not grep them for `items_list` / `fdd(`. Open questions 1 and 3 might become USAGE facts there.

## POSSIBLE SIMPOS CODE

None. The only code printed is application code: the generated `graph_drawing` class (TM-785 pp28-40) and command-line fragments. They show calls *into* SIMPOS (`standard_window`, `font`, `list_index`, `set_color_pair`, `refute`, `draw_*`), not SIMPOS bodies. The `.com` files `drawing.com` and `simshow.com` are named but their contents are not printed.

## CHECKED, NOTHING

- TM-785 p1, p2, p4, p5: cover, title sheets and contents.
- TM-785 p14-16, p18-24: application drawing/editing UI only (recorded in the page files; no SIMPOS facts beyond those above).
- TM-785 pp33-36, 38-39: modify/adjust/copy_element boilerplate; ESP builtins stack_vector/2, new_stack_vector/2 and vector_element/3 only.
- TM-786 p1-3: cover, title and contents.
- TM-404, all 39 pages: UNIX news, nothing on SIMPOS.
- TM-430 p1-4: nothing about operation.

## PAGES READ

Eyed means read from the rendered image (130dpi full page unless noted).

TM-785:
- PDF pp2-39 eyed at 130dpi; p40 eyed at 300dpi; p1 (cover) OCR only.
- Zoomed (300-400dpi): p3 (command lines, error window), p6 (start code), p7 (tool window), p17 (font line), p21 (FDD/copy lines), p29, p30, p31, p32, p36 (top), p37, p40. p28 at 130dpi only.

TM-786:
- PDF pp2-12 eyed at 130dpi; p1 (cover) OCR only.
- Zoomed: p4 (400dpi), p5 (400dpi, debugger and shell lines), p6 (400/600dpi form), p7 (path), p8 (400/600dpi form fields).

TM-401:
- PDF p10 and p11 eyed; p9 and p12 rendered but not read.

TM-430:
- p3 eyed; p1, p2 and p4 not eyed. They were covered by an earlier pass (STRUCTURE.md says read by eye).

TM-404:
- p3, p4, p5, p8 and p13 eyed.
- All other pages are OCR only. That includes the command/screen pages pp6, 7, 9-12 and the `.signature` page p22, all UNIX. A re-grep of the OCR for PSI rendered as `P ?S ?[1Il|]`, or for SIMPOS, found no hits.

## OPEN QUESTIONS

1. Contents of `drawing.com` / `simshow.com`. These are Librarian command files that create a package and load classes from FDD. Not printed.
2. Which command is `Execute` in the Librarian menu, and what other Librarian commands exist? Only Execute is named. The Librarian's other screen elements are not shown.
3. Is the login-file `menu` clause `menu :- items_list([...])` (TM-785), or does TM-786's elided form imply another layout? Are both string and atom labels allowed?
4. The `$ call Pkg##Class` shell command. What does `call` do with a class: create, then `:goal`?
5. TM-786 p6 SIMPOS version string (`5.0HC`?) and the CSP version first digit.
6. `copy_text` vs `copy_test` in the file manipulator.
7. Which SIMPOS class is the do_it/abort setting sheet, and which provides the `Really?` ERASE/STOP confirm used by the Librarian?
8. The SIMPOS 操作説明書(II) (Operating Manual II) is referenced but not held.
