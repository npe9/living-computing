# trtm_progsys: SIMPOS programming system / top level as printed in the held ICOT TR/TM

Organisation: the report-by-report sections below hold the evidence; this summary regroups it by
subsystem (each line points to the section). TSV beside it: trtm_progsys.tsv.

## SUMMARY BY SUBSYSTEM

### SHELL / top level
- System menu = "SIMPOS's command processor", two right clicks anywhere (TM-143 p3, TM-181 p3, TM-134
  p66, TM-229 p5). Columns EXPERTS (multi-instance) / MEDIA SYSTEMS (single). Item lists, by
  version (all SCREENSHOT):
  | version | EXPERTS | MEDIA SYSTEMS | source |
  |---|---|---|---|
  | 1.x (Nov 1985) | generalist, debugger, editor, file_manipulator, librarian, terminal | window_manipulator, network, shell, whiteboard, login, shut down | TM-143 p3 |
  | 2.10 (Jun 1986) | debugger, pmacs, librarian, file_manipulator, spooler, font_editor, edips | user process list, window manipulator, network, shell, whiteboard, kanakan initiate, garbage collection, login, shut down | TM-181 p3 |
  | 2.x (Sep 1986) | Debugger, Pmacs, File, Librarian, Font_editor, Edips, Spooler + Escher, Oekaki, Queens, Squares, Bounce | (as 2.10) | TM-229 p5 |
  The EXPERTS column is per-user: login file `menu :- items_list([{Label, [Pkg##]Class}, ...]).`
  with `{'debugger',debugger}`, `{'pmacs',pmacs}` (TM-785 p6, p25; TM-786 p5; 1989).
- Running process control: system menu -> select the running expert -> `kill` (TM-134 p67);
  start/terminate/suspend/resume (TM-143 p3, TM-229 p5). `shut down` ends everything.
- Login: user name then password; unregistered user may log in with `me`/`me` (TM-134 p66, 1.0);
  footer then `USER : me`. Login init (TM-143 p3, TM-181 p3, TM-229 p5-6): system-menu items, directory
  logical names (default `me:` = `>sys>user><login name>`, and a default directory), an init program,
  automatic creation of PS (editor, debugger ...) with window positions. "initialisation file"
  (初期化ファイル) = login file (TM-229 p5; TM-785/786 "ログインファイル").
- How a user program runs (TM-134 p67-72, TM-786 p5, TM-785 p6, TM-115 p109):
  (a) subroutine form from the debugger: `:- :new(#c,O).` `:- :initiate(O).` -> runs in the
      debugger's process;
  (b) process form: class inherits `as_program` (gets class method `:create(Class,Obj)` which calls
      `:new`), defines instance method `:goal(Obj)`; start by `:create(#process,P)`,
      `:activate(P,Obj)` -> `:goal(Obj)` runs in P; process terminates when :goal ends (success or
      failure);
  (c) from the shell: `$ call pkg##class` (1989);
  (d) from the system menu via the login file items_list (1989); TM-115 (1985) says a menu program
      should inherit `as_e_program`.
- Shell: "UNIX-like shell" of the coordinator (TM-225 p7); prompt `$`, command `call` (TM-786 p5);
  standard ports of shell and debugger = their window (TM-388 p82). 1984 design had NO shell
  (TR-057 p7) -- only the coordinator.
- Error entry: error window `Error occurred in <name>( process <n> )` + message + `Error handling
  menu:` with situation-specific items, e.g. in the debugger `Continue` / `Cancel this input` /
  `Kill this process` (TM-181 p5, 2.10), in the librarian `Erase existing package and continue` /
  `Inspect the information of this event` / `Return to librarian top level` (TM-785 p3, 1989).

### DEBUGGER / interpreter / listener
- The debugger IS the ESP listener / command interpreter (TM-181 p3-4, TM-143 p4). Goal prompt `:-`
  (1.0, TM-134 p67-71), answer `> Success !!`; bindings in `Variable Window` as
  `Var = $class,` ... `;`. Runs goals of registered methods and built-ins; interpretive and direct
  code alike, trace only in interpretive code; direct vs interpretive chosen automatically
  (TM-225 p7).
- Windows: `debugger_<n>` main; sub-windows `Variable Window`/`Variable`, command menu `Method`,
  `Step`, `Skip`, `Leap`, `Fail`, `Retry`, `No trace`; mode `PREDICATE`/`clause` (TM-181 p4, 2.10);
  `Debugger Menu`: Change State, Variable Window, Control Menu, From Last Input, From Whiteboard, To
  Whiteboard, Help; state/parameter window: mode trace/no trace/no debug, print depth/length,
  Trace/Leash grids over CALL unify pick exit EXIT / FAIL next miss redo REDO, New/Method/Compiled/
  Builtin, Spy Points (TM-126 p6, TM-125 p23, 1.00, existing listings).
- Trace line: `(17)1 CALL> :test($my_window) ? step` ; answers `step`, `skip_predicate`,
  `no_trace` (TM-181 p4-5). Ports: CALL/EXIT/FAIL/REDO + clause ports unify/next/pick/miss/exit/redo
  (TR-057 p8, TM-229 p7).
- Inspector called from the debugger, exchanges variable values with it (TM-229 p7).

### LIBRARIAN
- Command menu, 1.x (TM-143 p3): Check, Catalogue, Compile, Uncompile, Save, Load, Delete, Print,
  Info, Classes, Predicates, Execute. 2.10 (TM-181 p4; = TM-229 p6): Check, Catalogue, Compile,
  Uncompile, Save, Load, Delete, Execute, Utility. Text window `<< Librarian Text >>` (1.x);
  window `librarian_<n>`, process `librarian_<n>` (TM-785).
- Messages: `File Name:escher`, `Cataloguing "escher.esp"...`, `<class>` (indented, one per class
  defined in the file), `<class> end.`, dashed rule; `Class Name(<c>)`; `source`/`template`/`object`
  dates, `interpretive`/`compiled`; `Printed.`; prompt `Input Class Name.` with echo `@ <name>`;
  `Regist...`, `Compil...` (TM-134 p71, TM-143 p3, TM-181 p4).
- `Execute` = batch command execution (TM-229 p6); prompt `Command>`; command `fdd("x.com")` then
  `FDD mount ok?` / `Input unit No.(0):` (TM-785 p3, TM-786 p4).
- Functions (TM-229 p6): register/delete classes (interpretive or direct code), change executing
  code, save/load template files, batch commands, utilities. Packages, package environments and
  external declarations are made "by operating the SIMPOS librarian and performing a library method
  call" (TM-388 p95); a package's environment is fixed when the librarian generates the package
  (ESP manual TeX program-e.tex:5331, outside my report scope). Set current package + load package
  (TM-786 p5).
- Packages: TM-388 p92-101 (see section). `with_simpos` inherits `simpos`.
- Three forms source/template/object (TR-057 p10, TM-143 p4); rebuild rules (TM-143 p4).

### EDITORS
- Pmacs (TM-229 p6, TM-225 p7, TM-181 p4): emacs-like, 100+ commands, named buffers shared across
  processes, kana-kanji, ESP-programmable commands; every character-I/O window of the PS is a "window
  with Pmacs functions". Pop-up menu (2.x, TM-229 p6): ABORT, List Buffers, Save All Files, Set Font,
  Set Same Font, Set Window Size, «?», To Whiteboard. Echo line `Find File:`; file write message
  `<file> > write end`. 93 classes / ~14,300 lines (TM-639 p9).
- Edips (TR-057 p9, TM-143 p3): structure editor; 1.x menu kill/meta_kill, duplicate/meta_duplicate,
  move/meta_move, insert_file/write_file, from_whiteboard/to_whiteboard, yank«?»/file_name; status
  `EDIPS(string)[61,28] >sys>user>demo>`, messages `reading...`, `<path> >read end` (TM-126 p6).
- SEMACS (TM-639): Pmacs extension, string mode + structure mode.

Conventions: citation "TM-229 p6" = PDF page index of lit/trtm/tm0229.pdf (folio in brackets).
Grades: PRINTED, PRINTED-INTERFACE, USAGE, PROSE, SCREENSHOT, INFERENCE; TRANSLATION marks my
translation of Japanese. «?» = illegible.

## TM-229 (1986-09-29, SIMPOS 2.x; screens show "SIMPOS Version 2.«?»0") -- NEW pages p5 right col, p6-p9

### SHELL / user interface rules (TM-229 p5 [-4-], right column; eyed 300dpi) PROSE, TRANSLATION
- (2) ユーザ・インタフェースの統一化 (unification of the user interface), rules imposed on the PS:
  1. Every window that does character(-string) input/output uses a "window with Pmacs functions"
     (Pmacs機能付ウィンドウ) = a standard I/O window in which Pmacs editing functions work while a
     string is being typed; so all in-line editing of typed input is done by Pmacs.
  2. Menus are classified in two kinds, with uniform meaning of mouse input:
     (1) menus whose items are OPERATIONS -- operations are fixed, so a fixed-length menu;
     (2) menus whose items are the OBJECTS of an operation -- variable, so a variable-length menu
         (scrollable menu etc.).
- (3) ログイン処理 (login processing): per-user environment set at login "by an initialisation file
  etc." (初期化ファイル等):
  1. system-menu item setting: the system menu "plays the role of SIMPOS's command processor";
     callable at any time; start, terminate, suspend, resume processes. Two columns EXPERTS and
     MEDIA SYSTEMS; EXPERTS programs may be invoked several times (multiple instances), MEDIA
     SYSTEMS only one each. A user can add his own program to EXPERTS and delete unused EXPERTS
     programs.
  2. logical names for directories (ディレクトリの論理名); also the default directory used when no
     directory is given.
  3. initialisation program run at login (初期化プログラムの設定).
  4. (p6 top) PSの自動生成の設定: at login, PS such as the editor and debugger can be created
     automatically and their windows shown at specified positions.
- System menu screenshot p5 (already in listings/TM-229_p03-05.txt): Experts {Debugger, Pmacs, File,
  Librarian, Font_editor, Edips, Spooler} + demo column {Escher, Oekaki, Queens, Squares, Bounce};
  MEDIA SYSTEMS {user process list, window manipulator, network, shell, whiteboard, kanakan
  initiate, garbage collection, login, shut down}. SCREENSHOT. (Note "File" here vs
  "file_manipulator" in TM-181; capitalised items in 1986-09.)

### Programming cycle (TM-229 p6 [-5-] (4) プログラム開発手順) PROSE, TRANSLATION
- ESP program development on SIMPOS = repetition of: create/edit source with the editor; register
  (登録) the class with the librarian, converting it to executable code (compile); step-execute and
  debug with the debugger; examine object state (slot values) with the inspector.

### EDITOR: Pmacs (TM-229 p6 (5) エディタ) PROSE, TRANSLATION
- "The SIMPOS editor is called Pmacs", a screen editor taking many features of emacs.
- 100+ commands; editing units character, word, line, page.
- The buffer holding edited text is accessible BY NAME from any process; so several Pmacs can edit
  the same text (buffer) and one Pmacs can edit several texts.
- Japanese input (kana-kanji conversion) built in: romaji -> kana or kanji.
- User-customisable; commands can be added by programming in ESP.
- Screenshot (p6 lower left; SCREENSHOT, low res): Pmacs window editing an ESP class (`class
  «?» has / nature «?»_program; ... :create(...)`), with a pop-up menu titled «?» (prob. "EDITOR
  MENU" or "PMACS MENU") items, top to bottom: `ABORT`, `List Buffers`, `Save All Files`,
  `Set Font`, `Set Same Font`, `Set Window Size`, `«?»` (highlighted, ~18 chars), `To Whiteboard`.
  Mode line under text: `Pmacs «?»(ESP)«?» >sys>user>«?»` (illegible). Footer "USER : «?»  SIMPOS
  Version 2.«?»0".
- p7-8 (10) 日本語入力機能: all chars JIS 16-bit; kana-kanji conversion built into the keyboard
  (software) so any program can input kana/kanji; additionally Pmacs gives word-processor-like
  Japanese input: converts a specified region of romaji text to kanji/kana; multiple candidates
  shown one by one as 「次候補」(next candidate) or all at once in a menu for selection. "All PS
  that do input use windows with Pmacs functions, so Japanese can be input with Pmacs functions."
  A document formatting/output system for Pmacs Japanese text with fonts also exists.
  Screenshot p7: conversion kinds 漢字変換, 単語変換, 文節変換, ひらがな変換, カタカナ変換; modes 逐次変換 /
  一括変換 (successive / batch); candidate menu `0. «?» 1. «?» 2. せんたくする`. SCREENSHOT.

### LIBRARIAN (TM-229 p6 (6) ライブラリアン) PROSE, TRANSLATION
- "All classes handled by SIMPOS are managed by the library (ライブラリ). The user interface providing
  the library's functions is the librarian (ライブラリアン)." Functions:
  1. クラスの登録, 削除 (register/delete classes): generate and manage executable code from ESP source.
     Executable code is either 解釈実行コード (interpretive code) or 直接実行コード (direct-execution
     = compiled code); the user specifies which to generate. Registered classes can be deleted.
  2. 実行コードの変更 (change executing code): specify whether interpretive or direct code is used.
  3. テンプレート・ファイルのセーブ, ロード: save to a file / load into main memory a TEMPLATE holding the
     class's own information (slot info, method and local-predicate code, inherited class names,
     referenced class names, ...).
  4. コマンドの一括実行 (batch command execution): call a series of librarian commands at once;
     convenient for registering many classes in the same combination in one go.
  5. 各種のユーティリティ機能: search various information about OS and user classes.
- Screenshot (p6 right; SCREENSHOT, LOW CONFIDENCE, scan is below text legibility): librarian window
  with a left command menu of 9 items (title «?»); item shapes fit: `«?»` (short), `Catalogue`,
  `«?»` (highlighted), `«?»`, `Save`, `Load`, `Delete`(?), `Execute`(?), `Utility`(?) -- INFERENCE:
  the 9 items correspond to functions 1-5 above (Catalogue/Uncatalogue, code change, Save/Load
  template, Execute = batch, Utility). Text pane: `File Specification`, `Cataloguing "demo.esp"...`,
  then class names indented, then `<class> end.` lines, a dotted rule, `PREDICATE`, dotted rule,
  `File Specification`, `Cataloguing "test.esp"`, `test`, `test end.`, dotted rule,
  `Class Specification«?»`. A pop-up multiple-select menu over it: `DO IT`, `EXIT`,
  `ALL BUT SELECTED`, `FROM WHITE BOARD`, then class names (`test`, `demo_program`, `«?»`, ...,
  one boxed = selected). -> menu kind (2) (objects as items) with as-multiple-select style
  controls. Footer `USER : «?»  SIMPOS Version 2.«?»`, `«?»-Sep-86 «?»day`.

### DEBUGGER / INTERPRETER (TM-229 p6-7 (7)) PROSE, TRANSLATION
- "The debugger/interpreter provides execution and symbolic tracing of ESP programs, and can call
  goal sequences made of interpretive code, direct-execution code and KL0 built-in predicates."
- Trace works per predicate AND per clause by the P&C model (Procedure and Clause Box Control Flow
  Model, Fig. 4-1 p7): previously one knew only that a predicate call failed; now which clause
  failed. Also: spy points (スパイ・ポイント) so that no trace is done until a given goal call; debugging
  in a multi-process environment.
- Fig 4-1 (p7, eyed): PROCEDURE box with 3 clause rows; each row Head box and Body box; labels
  `unify`/`next` (into/out of head), `pick`/`miss` (head<->body), `exit`/`redo` (body out/in);
  outer `CALL`/`FAIL` left, `EXIT`/`REDO` right. Same as TR-057 Fig 4-1 (lower-case clause ports).
- Screenshot p7 (bounce demo being debugged; SCREENSHOT, low conf.): window `debugger_1` with a
  `Variables` pane; trace lines of the form
  `(14)(9) CALL builtin add(32,7,_«?») ? step`, `(14)(9) EXIT builtin add(32,7,39)`,
  `(15)(9) CALL builtin divide(«?»)`, `(16)(«?») CALL> «?»(«?») ? step`, then `unify`/`pick` lines.
  INFERENCE: format "(<invocation no.>)(<depth>) <PORT> [builtin] <goal>", and " ? " is the leash
  prompt, answered here with the command `step`. An `inspector_1` window shows an object's slots
  (names like `«?»_buffer`, `«?»_process_«?»`, `error_«?»`), a `History` pane (`Variables`,
  `Predicate`, `«?»`) and a command pane (`exit`, `parameters`, `erase`, `from_WB`?).

### INSPECTOR (TM-229 p7 (8) インスペクタ) PROSE, TRANSLATION
- Shows object state (slot values) and details of the various KL0 data types; display, search,
  change. Menu-style display: debugging almost by mouse alone.
- Called FROM the debugger; returns control to the debugger when done. They exchange data: e.g.
  change a variable's value received from the debugger and return it; or give a value to an unbound
  debugger variable on the inspector side, return control and continue execution.

### MANIPULATORS (TM-229 p8 [-7-] (11)) PROSE, TRANSLATION
- Utilities offered by menu selection:
  1. window manipulator: change window position, size and other attributes.
  2. file manipulator: list file names, copy/delete files, pattern search, word count; via the
     network also files on other PSIs and general-purpose machines.
  3. spooler manipulator: display spooled print output, cancel, change output order.
  4. magnetic-tape manipulator: initialise MT; save/restore disk files to tape.
- (9) font editor (p7): create/modify fonts (shape, size, pitch) interactively; also icons; all by mouse.

### Versions (TM-229 p9 [-8-] 6.(1) 開発経緯) PRINTED table, TRANSLATION
- 1982/6 ICOT founded (KL0 design starts); 83/5 SIMPOS group (design starts); 83/12 PSI #1;
  84/3 firmware done; 84/11 FGCS'84 demo (no PS); 84/12 SIMPOS 0.7 (many bugs); 85/2 0.8 (somehow
  usable); 85/4 1.0; 85/9 1.5 (UI improved); 86/3 2.0 (reliability, functions); 86/7 2.5 (network
  strengthened); 86/12 (planned) 3.0 「ユーザ・インタフェース統一化」 (UI unification). ~40 members.
- Size (2.5): source 232,202 lines; 1,380 classes; 18,601 predicates (p9, digits eyed at 25%: «?»).
- References list cites 石橋他 "SIMPOSにおけるプログラミング環境" (= TM-181) and 近山他 "SIMPOSのプログラミング環境"
  情報処理学会第33回全国大会 '86.10 (not held as TM?).

NOTE ON GRADES ABOVE (TM-229 screenshots): the TM-229 scan is below glyph resolution (600dpi
renders show the same blocks). Every menu item, trace line and window label quoted above from
TM-229 p6/p7 screenshots and not printed elsewhere is INFERENCE from word shapes, NOT
SCREENSHOT-grade: the librarian items `Delete`, `Execute`, `Utility`, the pop-up title "EDITOR
MENU", the 7th Pmacs item, and the trace-line text `(14)(9) CALL builtin add(...) ? step`.
The Pmacs items `ABORT`, `List Buffers`, `Save All Files`, `Set Font`, `Set Same Font`,
`Set Window Size`, `To Whiteboard`, the librarian `Catalogue`, `Save`, `Load` and the pop-up
`DO IT`, `EXIT`, `ALL BUT SELECTED`, `FROM WHITE BOARD` are legible enough for SCREENSHOT (low
confidence). Only these go into the TSV.

## TM-134 「ESPプログラミング」 (Mitsubishi; Sept 1985; SIMPOS 1.0) p66-72 [folio 62-68] -- NEW, eyed at native 96ppi x2
The most concrete printed account of how a user program is compiled and run. TRANSLATION mine.

### 6.5 プログラム作成・実行のマシン操作 (machine operation for making and running a program) (p66-68)
- Refers to "SIMPOS操作説明書" (SIMPOS operation manual) and its IPL section, and "SIMPOS使用説明書"
  (SIMPOS user's manual: processes, files, windows). NOT HELD.
- (1) login (p66): after SIMPOS boots it waits for user name then password; a registered user types
  his name and password; an UNREGISTERED user types "me" for both (+CR) and is logged in as a
  general user; the screen returns to blank. PROSE. Footers then show `USER : me` (p68 SCREENSHOT).
- (2) system menu (p66): two consecutive clicks of the mouse RIGHT button show the system menu;
  tools (debugger, editor, librarian ...) chosen by moving the mouse and clicking LEFT. PROSE.
- (3) editor (p66): choose the editor in the system menu; open a window of any size by mouse
  (left click, move, left click); type the program class by class, and "send it to a disk file by
  keyboard operation". PROSE.
- (4) ライブラリアンによるコンパイル (p66): choose the librarian in the system menu; it generates the
  class TEMPLATE and the CLASS OBJECT. "considering class inheritance and method calls, do
  `Catalogue,Compile` in the following order": trigonometric_function, with_user_window,
  hypocycloid_drawer (note: the first two may be swapped). PROSE; command names `Catalogue` and
  `Compile` PRINTED in Latin letters.
- (5) デバッガからのプログラム実行 (p67): choose the debugger in the system menu; after the prompt
  `":-"` type a goal; programs are started "in the conventional subroutine-call form":
    `:- :new(#hypocycloid_drawer,Obj).` CR -> Obj = an instance
    `:- :initiate(Obj).` or `:- :initiate(Obj,Radius).` CR -> the object runs, its window appears and
    waits for keyboard input; when it ends the prompt `:-` reappears. PRINTED (dialogue).
- (6) 操作終了の処置 (p67): "show the system menu, select the debugger and "kill"" -> the debugger and
  the object's window vanish. Selecting "shut down" in the system menu makes all windows vanish and
  ends. PROSE. INFERENCE: selecting a running EXPERTS program in the system menu offers `kill`
  (cf. TM-143 p3 "start/stop/suspend/resume by mouse").
- Fig 6-3 (p68) SCREENSHOT, legible; footer `USER : me`, `SIMPOS Version 1.00`, selected window
  `debugger_3`, `13-Jul-85 Saturday 16:20:06`. Window `debugger_3` (name at top and bottom):
  ```
  :- :new(#hypocycloid_drawer,Object1).
  > Success !!
  :- :initiate(Object1,351).
  > Success !!
  :- :new(#hypocycloid_drawer,Object2).
  > Success !!
  :- :initiate(Object2).
  > Success !!
  :- _
  ```
  sub-window `Variable Window`: `Object1 = $hypocycloid_drawer,` / `Object2 = $hypocycloid_drawer;`
  (objects print as `$<class name>`; bindings separated by `,`, last ends `;`). A
  `«?»nipulator_1` (window manipulator) window with item `abort`. User windows titled
  `< Hypocycloid >` with prompt `Ratio(2,3,..<350)= 3`.

### 6.6 プロセスの作り方 (how to make a process) (p69-71)
- (p69) The 6.5 example is subroutine-form: called by a method call from the debugger it runs ON
  THE DEBUGGER'S PROCESS, and the debugger is suspended until it ends. PROSE.
- Requirements for a program to run as an independent process (p69) PRINTED-INTERFACE+PROSE:
  (a) inherit the SIMPOS class `as_program`; this automatically adds the class method
      `:create(Class,Object)`: "when :create is called, `:new(Class,Object)` in that goal creates the
      instance object, which is passed in the 2nd argument."
  (b) the instance method heading the goal sequence executed at start has ONE argument (the
      instance): `:goal(Object)`.
- p70 PRINTED code (example user class; only changed parts printed):
  ```
  class hypocycloid_drawer has
  nature as_program,with_user_window;
  component default_radius:= 200;
  :create(Class,Radius,Obj):- integer(Radius),
          Radius>100,Radius=<360,Class!default_radius:=Radius,
          :create(Class,Obj);
  after   :create(Class,Obj):- Obj!radius:=Class!default_radius,
          Obj!size_x:= 2*(Obj!radius+20),
          Obj!size_y:= Obj!size_x+54,
          Obj!center_x:= Obj!radius+14,
          Obj!center_y:= Obj!radius+24,
          :get_number_string(#symbolizer,Obj!radius-1,String),
          set_substring(Obj!prompt,13,3,String),
          Class!default_radius:= 200;          % 初期値の更新対策
  instance component
          prompt:= "Ratio(2,3,..<   )= ",radius:=200,
          size_x,size_y,center_x,center_y;
  :goal(Obj):- W=Obj!window, :set_size(W,Obj!size_x,Obj!size_y),
          :set_title(W,"   < Hypocycloid >"),:activate(W),
          operate(Obj,W);
  local
  operate(Obj,W):- get_ratio(Obj,W,Ratio),
          hypocycloid(Obj,W,Obj!radius,Ratio),
          :write_lines(W,"Any key(End= ^Z)?"),        % 変更・追加
          :read(W,control#"z"),!,:kill(W);
  operate(Obj,W):- :operat(Obj,W);
  ```
  (96ppi scan: `*`/`+` operators probable; the last clause prints `:operat(Obj,W)` as is.)
  Text: object creation `:new` is left to the inherited as_program method `:create(Class,Object)`;
  instance-slot setup is in an AFTER demon of `:create(Class,Object)`. USAGE of SIMPOS methods:
  nature as_program; `#symbolizer:get_number_string/4`; window `:set_size/3`, `:set_title/2`,
  `:activate/1`, `:write_lines/2`, `:read/2` (arg control#"z"), `:kill/1`; built-in set_substring/4.
- (3) プロセスの起動法 (p71): from the debugger (itself an object running as a process):
    `:- :create(#hypocycloid_drawer,Radius,Object).` or `:create(#hypocycloid_drawer,Object).`
    `:- :create(#process,Process).`  -> a process instance object is secured
    `:- :activate(Process,Object).`  -> hands the instance to the process; `:goal(Object)` is called
       and execution starts. `:activate` returns at once and `:-` reappears.
  PRINTED (dialogue) + PROSE: "the debugger on the left and the one on the right are independent
  processes".
- Fig 6-4 (p71) SCREENSHOT, legible: `debugger_1`: `:- :create(#hypocycloid_drawer,300,Cyc).`
  `> Success !!` `:- :create(#process,Proc).` `> Success !!` `:- :activate(Proc,Cyc).`
  `> Success !!` `:-`; Variable Window `Cyc = $hypocycloid_drawer, Proc = $process;`.
  User window `< Hypocycloid >`: `Ratio(2,3,..<299)= 6` / `Any key(End=^Z)?`; an editor message
  line `hypocycloid_drawer.esp > write end`. `file_manipulator_1` with menu column `abort` /
  `parent` / `refresh` / `make`. A LIBRARIAN text window titled `<< Librarian Text >>`, left part
  visible (right hidden under debugger_1), lines:
  ```
  Printed.
  Input Class Name.
  @ hypocycloid_drawer
  Input «hidden»
  @ hypo«hidden»
  Regist«hidden»
  Regist«hidden»
  Input «hidden»
  @ hypo«hidden»
  Compil«hidden»
  Compil«hidden»
  (the Input/@/Regist/Regist/Input/@/Compil/Compil group repeats once more)
  ```
  SCREENSHOT (SIMPOS 1.0, 1985). INFERENCE: the 1.0 librarian is a prompt dialogue in a text
  window: it prints `Input Class Name.` (or `Input «...»`), the typed answer is echoed after `@ `,
  then two progress lines per step (`Regist...` begin/end for Catalogue = registration,
  `Compil...` begin/end for Compile).

### 6.7 プロセスの終結とデータ保存 (p72) PROSE, TRANSLATION
- When the goal sequence called by `:goal(Object)` finishes, success OR failure, the process
  TERMINATES; the instance and its slot data vanish. Ways to keep data: (1) a file; (2) do not end
  the process (wait for a restart through a SIMPOS stream); (3) class slots: save by a class method
  just before termination, restore in the after-demon of `:create` of the next instance. (2) and
  (3) survive only until "shut down".

## TM-225 「AIワークステーションPSIのプログラミング環境」 (Aug 1986) p6-8 [folio 5-7] -- NEW, eyed native x2
PROSE, TRANSLATION.
- 5. プログラミングシステム: a set of support tools; design policy: use under a multi-window
  environment (several tools' windows at once); menu orientation: command input by mouse menu
  selection, "manual-less operation", in harmony with keyboard command input.
- (1) コーディネータ: "similar to the command interpreter of a general system"; by menus it starts,
  controls and terminates system-supplied or user-made tools. "It also has a UNIX-like shell
  (UNIX風のシェル), and program execution by it is also possible." The coordinator always runs in the
  background; callable at any time; can force-terminate a running program. The window manipulator,
  called VIA the coordinator, changes size/position of each tool's windows.
- (2) エディタ: EMACS-like; 100+ commands, multiple buffers, user command addition/change; kana-kanji
  Japanese input/editing. Also a structure editor for automatic editing following ESP syntax.
- (3) ライブラリ: all programs (classes) managed as a kind of database; SIMPOS system classes and user
  classes managed exactly alike. The interactive program operating the library = the librarian:
  convert source to interpretive code, compile, register to / delete from the library, search
  management information.
- (4) デバッガ/インタプリタ: runs programs registered in the library and debugs interpretive-form
  programs. Registered programs exist in machine-language form or interpretive form; direct
  hardware execution or interpreter execution is selected AUTOMATICALLY by the form. Interpretive
  form: trace, variable display; plus inspector (object state) and performance measurement.
- p8: tools run simultaneously, "jumping between tools".

## TM-115 "PSI Font Editor Implementation Notes" (Touati, May 1985) p92, p109 -- OCR (clean English)
- Class `font_editor` "inherits the class as_program, and is used when the user wants to run the
  font editor as an independent process. When an instance of this class is activated, it creates an
  instance of the class font_executive, and calls the top level loop of this instance." (p109)
- "For a more user-friendly interface, it would be better to inherit the class as_e_program and to
  add an entry "font_editor" in the system menu" (p109). PROSE. => in SIMPOS 1.0 a class
  `as_e_program` existed for programs started from the system menu (INFERENCE: e = EXPERTS).
- §6.8.2 instance method `:goal` (Instance): "creates an instance of the class font_executive, and
  calls the method :execute_orders of this instance." PRINTED-INTERFACE (OCR `:g0al`).

## TM-388 ESP Guide (English) p82 [70], pp92-105 [80-93] -- OCR read; package figures eyed later (see PAGES READ)
- p82 PRINTED: macros `standard#input`, `standard#output`, `standard#message` expand to the standard
  input/output/message port of the current process; "For the debugger and the shell, the initial
  value will be the window." -> the shell and debugger are processes whose standard ports are their
  own window.
- 3.8 Package (p92-101): package name = atom, unique; a class's package is decided when stored --
  "in SIMPOS, it is determined usually when the class is catalogued". Forms `class-name` and
  `package-name##class-name` in `#class`, `nature`, `Pkg##class:method(...)`, `with macro Pkg##bank`.
  Binding happens when classes are stored (at macro expansion).
- Package environment (p93-95): at most one per package; may multiple-inherit packages and other
  package environments; "the most general use ... is to use the package environment `with_simpos`
  that inherits system package `simpos`". Unqualified names resolve to (1) every class of the own
  package, (2) classes declared EXTERNAL (public) in packages inherited, directly or not, by the own
  package's environment; earlier inheritance order wins. Others only as `pkg##class`.
- 3.8.3 (p95): "Generation of a package or a package environment and external declaration of a class
  can be accomplished by operating the SIMPOS librarian and performing a library method call. For
  details, see "SIMPOS OPERATION MANUAL" and "SIMPOS PROGRAMMING MANUAL"" (both NOT HELD). Patterns
  (p95-98): personal package + env inheriting simpos; shared package `utility` + environment
  `with_utility` inheriting `utility` and `simpos`; per-user packages for versions -- releasing a
  class = "restore (i.e., recatalogue) it in package user_b".
- 3.8.4 Restrictions (p98-101): names bind statically at macro expansion, so cataloguing order
  matters; cataloguing a class that references a not-yet-existing class stores ONLY ITS NAME in the
  package; deleting `p0##a1` leaves a2 without a referent until a2 is restored (re-catalogued).
- 3.9 ESP program in PSI (p102-105): a source FILE may contain class definitions, macro bank
  definitions (`macro_bank ... end.`; stored before classes using it; a macro bank is stored as a
  class, "can also be saved by the librarian", auto-loaded), operator declarations
  `add_operator(Op,Type,Pre).`, `remove_operator(Op,Type).`, `remove_operator(Op).` (effective to end
  of file), macro declaration `use_macro([pkg##]class).`, package declaration
  `use_package(package-name).` (effective only within the file), `include("file-name").`
  Macro banks inherit SIMPOS class `esp_macro_expander`: `:expand_clause(Obj,Head0,Body0,^Head,^Body)`,
  `:expand_goals(Obj,Goals0,^Goals)`. PRINTED-INTERFACE. If no package is named "the default
  package of the process being currently executed is assumed" (p103).

## TM-181 「SIMPOSにおけるプログラミング環境」 (Ishibashi et al., 1986; screens SIMPOS 2.10, 27-Jun-86) -- re-eyed p3-p5 at native 96ppi x3-6
### Text (TRANSLATION, PROSE)
- p3 (4) プログラムの作成/実行手順: create/modify source with the editor; convert to executable code
  with the LIBRARIAN "(compiler)"; run or debug with the DEBUGGER "(command interpreter)"
  (デバッガ(コマンド・インタプリタ)).
- p3 (2) login: per-user init on login: system-menu items (e.g. add "my program"); directory logical
  names, default `me:` (`>sys>user>`<login name>); initialisation program. (3) system menu = SIMPOS's
  command processor, callable any time by two right clicks; EXPERTS several instances, MEDIA
  SYSTEMS one each; start/terminate/suspend/resume by mouse.
- p4 (5) editor: Pmacs (Emacs-type) and Edips (structure editor). Pmacs has kana-kanji conversion; it
  has an editing area called a BUFFER and can also be used as an editable I/O window.
- p4 (6) librarian: generates executable code from ESP source and manages it. Executable code is of
  two kinds, interpretive and direct-execution: classes being debugged use interpretive code,
  finished classes direct code. The librarian also searches information about OS and user classes.
- p4 (7) debugger/interpreter: "the debugger is for debugging but also works as an ESP LISTENER
  (ESPリスナ) that executes programs interactively". From the debugger TOP LEVEL one can run goal
  sequences of methods already registered by the librarian and ESP built-ins; method calls work the
  same for interpretive and direct code; trace and execution control only for interpretive code.
  Besides tracing, the INSPECTOR shows object contents (slot values) and data structures.
- p5 (13) situation: errors and help handled as exception events uniformly from system to user
  programs; on an error "the applicable recovery methods are shown as a menu, so the user recovers
  by menu selection only".
### Screenshots (SCREENSHOT unless marked; SIMPOS 2.10)
- p3 system menu (already listings/TM-181_p03_system_menu.txt). CORRECTION: footer reads
  `SIMPOS Version 2.10` (also on p4 and p5 screens), not 2.19; user `ishibashi`; `27-Jun-86 Friday`.
- p4 LIBRARIAN window `librarian_1`, command menu column (legible):
  `Check` / `Catalogue` / `Compile` / `Uncompile` / `Save` / `Load` / `Delete` / `Execute` / `Utility`
  (9 items; same count and shapes as TM-229 p6, which therefore = this list). Text pane:
  ```
  File «?»:my_window            (prob. "File Name:my_window")
  Cataloguing "my_window.esp"...
     my_window
  my_window end.
  - - - - - - - - - - - - - - - -
  Class Name(my_window)
  «?» my_window «?»
  source   27-Jun-86 17:57:13
  template 27-Jun-86 17:57:13
     interpretive
     file     «none?»
  object   27-Jun-86 17:57:17
     compiled
  - - - - - - - - - - - - - - - -
  _
  ```
  INFERENCE: the second block is the output of `Check` for class my_window: per form
  (source/template/object) a timestamp; the template's code kind (interpretive) and whether it is
  saved to a template file ("file «none?»"); the object's code kind (compiled).
- p4 DEBUGGER window `debugger_4` with sub-windows `Variable` (shows `W`), a command menu
  `Method` / `Step` / `Skip` / `Leap` / `Fail` / `Retry` / `No trace`, and a mode menu `PREDICATE`
  (selected) / `clause`. Transcript (96ppi, «?» where uncertain):
  ```
  «?:»- :create(#my_window,W).
   «?» $my_window
  «?:»- :test(W).
   (17)1 CALL> :test($my_window) ? step
   (22)2 CALL> :putl($standard_io_window,"Pmacs ...") ? skip_predicate
   (22)2 EXIT> :putl($standard_io_window,"Pmacs ...") ? no_trace        (p5 screen)
  «?:»- X := W.
  ```
  => trace line format "(<invocation no.>)<depth> <PORT>> <goal> ? <answer>"; long string
  arguments abbreviated as `"Pmacs ..."`; objects shown as `$<class>`; the leash prompt is ` ? ` and
  the answers seen are `step`, `skip_predicate`, `no_trace` (INFERENCE: typed, or inserted by
  clicking the Step / Skip / No trace menu items). The goal prompt is `:-` or `?-` (glyph unclear at
  96ppi; TM-134 1.0 shows `:-` clearly).
- p4 PMACS window `pmacs_1` showing class my_window (cf. listings/TM-181_p04_screenshot.esp),
  echo line `Find File:pmacs.esp«?»: my_window.esp`; a temporary window titled `漢字ウインドウ`
  containing `Pmacsのカナ漢字変換で入力した。` (output of :test). Footer selected-window field shows
  `editor_echo_area_window/2` on one screen (Pmacs's echo area is its own window).
- p5 ERROR on entering `X := W.` at the debugger (SIMPOS 2.10, 19:20:44) -- the error window:
  ```
  Error occurred in debugger_4( process «?»7 )
  Error found by esp_macro_expander:

  illegal slot assignment: A := A
  ---------------------------------
  Error handling menu:
    Continue
    Cancel this input
    Kill this process
  ```
  SCREENSHOT (legible). Compare TM-785 p3 (1989, librarian): `Error occurred in librarian_59(
  process 59 )` / `Package drawing already exists` / `Cannot load package_template_file` /
  `Error handling menu:` / `Erase existing package and continue` / `Inspect the information of
  this event` / `Return to librarian top level`. => error window layout is stable 1986-89:
  title line `Error occurred in <window/process name>( process <n> )`, message lines, then a menu
  titled `Error handling menu:` whose items depend on the situation.

## TM-143 (Nov 1985, SIMPOS 1.x) p3 -- re-eyed native x5
- System menu screenshot, now legible enough (upgrade from low confidence): title `SYSTEM MENU`;
  EXPERTS: `generalist`, `debugger`, `editor`, `file_manipulator`, `librarian`, `terminal`;
  MEDIA SYSTEMS: `window_manipulator`, `network`, `shell`, `whiteboard`, `login`, `shut down`.
  SCREENSHOT.
- LIBRARIAN 1.x screenshot: menu pane titled `Command«?»`, items `Check` / `Catalogue` / `Compile` /
  `Uncompile` / `Save` / `Load` / `Delete` / `Print` / `Info` / `Classes` / `Predicates` / `Execute`
  (12 items); text window `<< Librarian Text >>`: `File Name:escher` / `Cataloguing "escher.esp"...`
  / `escher end.` / dashed rule. SCREENSHOT (Print/Info/Classes/Predicates legible at x6, medium
  confidence). INFERENCE: by 2.10 Print/Info/Classes/Predicates were grouped under `Utility`.
- EDITOR (Edips, 1985) window `editor_«?»` editing `class escher has instance attribute window;
  :«init»(Obj) :- !, :create(#window,W), :set_size(W,626,652), :set_position(W,50,120),
  :set_title(W,"Escher"), Obj!window := W, :activate(W);` with a pop-up 2-column menu (title «?»):
  `kill` | `meta_kill`; `duplicate` | `meta_duplicate`; `move` | `meta_move`; `insert_file` |
  `write_file`; `from_whiteboard` | `to_whiteboard`; `yank«(window_kill)?»` | `file_name`.
  SCREENSHOT, low-medium confidence. Debugger beside it: `:- :new(#escher,E).` / `E= $escher`(?) /
  `:- :init(E).` with a `Variable` pane showing `E`.
- p3 (5) editor text (by eye): the editor has a text-editing mode and a STRUCTURE-EDITING mode that
  edits while aware of the syntax; the syntax rules are user-definable through the transducer so it
  also edits non-ESP structures; the display position and the TARGET (ターゲット: the operand range of
  an edit) are pointed with the mouse. PROSE. (This 1985 "editor" = Edips.)
- p3 (6) librarian (OCR + by eye): two kinds of executable code, INTERPRETIVE code and MACHINE code;
  classes under debugging use interpretive, finished classes machine code. p4: debugger = ESP
  listener; same text as TM-181 (TM-181 is a revision of TM-143).

## Running a user program -- the three ways, as printed 1989 (TM-786, TM-785; SIMPOS ~5-7)
TM-786 「オンラインSIMPOS照会書 操作説明書」 (Aug 1989) p4-5 [folio 1-2], eyed native x2:
- Install (p4): (1) ライブラリアンを生成する (create a librarian); (2) floppy in unit 0; (3) choose the
  librarian's `Execute`; (4) type `Command>fdd("simshow.com")` + return; (5) `FDD mount ok?` /
  `input unit No.(0): 0` -- type unit number 0 (no return needed); (6) installed in ~45 s. If
  package simshow exists an error occurs: choose to continue (existing package deleted and
  regenerated) or stop. PRINTED dialogue + PROSE. (TM-785 p3 same, prompt printed `Input unit No.`.)
- 2. 起動方法 (p5) "three ways; behaviour after start is identical":
  (1) DEBUGGER: in the librarian set the package to "simshow" and load all of package simshow;
      then from the debugger: `:create(#simshow##simshow,S),` `:goal(S).`
  (2) SHELL: from the shell: `$ call simshow##simshow`  (=> shell prompt `$`, command `call`
      taking a pkg##class).
  (3) SYSTEM MENU: define the class `simshow##simshow` in the LOGIN FILE; example:
      ```
      menu :- ..............
              {"simshow",simshow##simshow} ,
              ..............
      ```
  PRINTED (fragments) + PROSE.
TM-785 「PSI図形ツールのインストール方法」 (Aug 1989) p6 [folio 1], p25, eyed native x2:
- 2.1 起動方法 (p6): (1) by method call `:drawing(#drawing##psi_drawing_tool)` -- "runs on the process
  that called the method"; (2) from the system menu: add psi_drawing_tool to `items_list` of the
  `menu` item of the login file:
  ```
  menu:-
        items_list([
                    {'debugger',debugger},
                        .
                    {'PsiDraw',drawing##psi_drawing_tool}]).
  ```
- 3.1 (p25): `:generate(#drawing##drawing_class_generator)`; login file example
  `menu :- items_list([ {'debugger',debugger}, {'pmacs',pmacs}, . {'DrawGen',drawing##drawing_class_generator} ]).`
  -- "add an item with drawing_class_generator as the CLASS NAME". PRINTED.
  => login-file system-menu entry = `{Label, [Pkg##]ClassName}`; the standard EXPERTS are ordinary
  entries named by class: `debugger`, `pmacs` (INFERENCE: classes debugger and pmacs in package
  simpos). Labels printed with single quotes in TM-785, double quotes in TM-786 (string vs atom:
  both evidently accepted or one is a typo -- OPEN).

## Coordinator / experts (TR-057 p7-9, TR-087 p6-7, TM-079 p14) -- OCR (clean English) / eyed (TM-079 p14)
- TR-057 p7 §4: the programming system is "a collection of expert processes"; an expert process has
  an independent communication window called `e_window`. The user invokes, controls and terminates
  any expert through its e_window. PROSE.
- §4.1 Coordinator: "In SIMPOS, there is no explicit supervising process such as Shell in Unix"; a
  work-behind process named Coordinator (not itself an expert) manages the set of experts, via "the
  associated key command table of the window". Functions: send a user's key command through the
  window to an expert; create, delete and activate an expert via `system_menu`; get and process
  special commands from an expert; help communication between experts via the whiteboard. PROSE.
- Whiteboard: an expert puts a message, another picks it up on the user's instruction, one mouse
  click (p8). Each user has a DIRECTORY TO CREATE EXPERTS: experts' names and program names; user
  may change it and the command table; it inherits from the system's common directory (the
  standard set of experts) (p8). Each expert has its own key command table; the Coordinator lets the
  user change it only when the window accepts the "change key command table" command (p8). PROSE.
- TM-079 p14 (1984, handwritten, eyed): same; adds inter-expert message box `e_ポート` (e_port) for
  pre-agreed pairs vs whiteboard for ad-hoc; experts controlled by menu window and mouse clicks; the
  expert-name -> program-name table is settable per user. PROSE.
- TR-087 p6 cites "Kurokawa and ..." for coordinator details (not held). VERSION NOTE: by 1986
  (TM-225 p7) the coordinator "also has a UNIX-like shell" -- i.e. the `shell` MEDIA SYSTEMS item.
- TR-057 p8-9 debugger: DEC-10 Prolog-like; new: P&C box model, calls between interpretive and
  compiled code ("Debugger cannot trace in the compiled code ... treats the invocation of compiled
  codes just like a simple built-in predicate invocation"; if interpretive code is invoked from
  compiled code, tracing restarts with no trace information), multi-window UI: at break points the
  user can select control options, look at ancestors or spy points, check slot values, see class
  definitions through the library subsystem, all in sub-windows by mouse. PROSE.
- TR-057 p9 Edips: macro customisation, few commands, "failsoft with many recovery environments";
  operator-precedence grammar with user-definable parentheses; 6 token categories (atom, prefix,
  infix, postfix operator, left, right parenthesis); 2-3 precedence levels for ESP; parser and
  pretty printer are separate utilities shared with compiler, interpreter, debugger. PROSE.
- TR-057 p10 library: class source file / class template file / class object file per class on
  secondary storage (templates and objects exist in main storage and are saved/restored); one class
  per source file; template from one source file, predicates kept as interpretive code, compiled on
  user request, then both kept; templates can be saved/restored before compiling; all predicate
  calls via indirect references (uniform interp./compiled invocation); "The compiler is simply a
  subroutine of the library subsystem. It compiles a single predicate from interpretive codes ...
  The user can specify which code should be used for building up a new class object. The template
  file is automatically rebuilt after the compilation." PROSE (1984 design).

## Debugger built-ins (TR-044 ESP Reference Manual, Feb 1984, p42 [folio 38, App. A-5]) PRINTED-INTERFACE
- KL0 "Debugging Aid" built-ins: `ancestor(N, ^Clause)`, `frame(N, Stack, ^Frame)`,
  `read_console(^X)`, `display_console(?X)`. (Basis of ancestors display; console I/O for the
  pre-window debugger, cf. TR-087 p10-11.) TR-044 has no package mechanism (packages postdate it).

## SEMACS / Pmacs size (TM-639, Dec 1988) p4, p9 eyed native x2
- SEMACS = "Syntax-directed Extension of pMACS", a structure editor built by reusing Pmacs classes.
  In string mode "almost all editing commands of Pmacs, the text editor on PSI" are available (p4).
  SEMACS buffers are instance objects (p8).
- Table 4.2.4-1/2 (p9) PRINTED: Pmacs = 93 classes (12) and ~14,300 lines (1000) [parenthesised
  figures unexplained]; SEMACS reused 81(12) classes unchanged, renamed 12, added 64 classes /
  ~7,000 lines; Pmacs modifications ~300 lines (~2% of Pmacs).
- Reference (3) "ICOT: SIMPOS文書編集機能説明書, 1987" (SIMPOS document-editing manual) NOT HELD.

## TM-388 p95 [83] package-environment figure (eyed native x1.6) PRINTED
- Package P0 (contains c0) has environment env1; env1 inherits (left to right) package P1 and
  environment env2; env2 inherits P2 and P3. P1 = {*c0, c1, *c2}, P2 = {*c2, c3}, P3 = {*c1, c3}
  (* = external). Resolution in P0: c0 -> P0's own c0; c1 -> P3 (P1's c1 is not external);
  c2 -> P1 (higher order than P2); c3 -> error (no external c3). `p2##c2` reaches a non-preferred
  or non-external class. Confirms OCR text.

## TM-146 「ESPプログラミング・ヒント集」 (近山 et al.) p5, p8 -- OCR, PROSE, TRANSLATION
- ESP has no linkage editor ("partially exists in ESP but the user need not be aware"); to change or
  add a class "compile the class definition and add it to the system". The "program management
  system" managing source and object code of all classes is what SIMPOS calls the LIBRARY; it
  manages class sources and object modules (class objects) together and registers/deletes classes
  on request. SIMPOS's own classes are registered in the library (p5).

## POSSIBLE SIMPOS CODE
- None. Every code fragment in these reports is USER example code (hypocycloid_drawer, escher,
  my_window, login-file menu clauses). The screenshots show only SIMPOS user-interface TEXT (menus,
  prompts, messages); no SIMPOS source or binary is printed. The closest are interfaces only:
  as_program `:create/2`, i.e. `:create(Class,Obj)` (TM-134 p69; the `/3` form there is the
  user's own hypocycloid_drawer method), esp_macro_expander `:expand_clause/5`, `:expand_goals/3`
  (TM-388 p102-105), the TR-044 debugging built-ins.

## CORRECTIONS TO EXISTING LISTINGS (repo not edited; for the caller)
- `pim/docs/simpos/printed/listings/TM-181_p03_system_menu.txt`: the footer version is
  `SIMPOS Version 2.10` (read on the p3, p4 and p5 screens), not 2.19.
- The TM-143 p3 system menu and 12-item librarian menu can be upgraded from low confidence to
  legible SCREENSHOT (native x5-6). Print/Info/Classes/Predicates are medium confidence.
- TM-229 p6/p7 screenshot text is mostly below glyph resolution. Only the items listed in the
  NOTE ON GRADES are SCREENSHOT; the rest is INFERENCE.

## PAGES READ
- Eyed (page image): TM-229 p5-p9; TM-181 p3-p5; TM-143 p3-p4; TM-134 p66-p72; TM-225 p6-p8;
  TM-126 p6; TM-125 p23; TM-079 p14; TM-388 p95 figure; TM-785 p3, p6, p25; TM-786 p4-p5;
  TM-639 p4, p8-p9; TR-044 p42; TM-143 p6; TM-079 p15-p17.
- Spelling re-check: on TM-181 p3 at 300dpi the item reads `kanakan initiate`, though the 3rd
  letter could be an s. The other items are `font_editor` and `edips` (lower case), and the column
  header is `Experts` (capitalised, beside `MEDIA SYSTEMS`).
- Per-report accounting for the brief's ranges:
  - TM-181 has 5 pages. p3-p5 were eyed; p1-p2 were OCR-triaged (cover; p2 is the OS kernel and
    window intro).
  - TM-143 has 8 pages. p3-p4 and p6 were eyed. p6 lists window component classes (out of scope;
    the window agent covers it). p5 (files, network), p7 (cross-development tools, DEC-2060) and p8
    (performance) were OCR-triaged only.
  - TM-229 has 9 pages. p5-p9 were eyed; p1-p4 were OCR only (intro, KL0, kernel).
  - TM-225 has 16 pages. p6-p8 were eyed. p1-p5 and p9-p16 are NOT READ: the OCR is too garbled
    to triage, and by their position they are the intro, PSI hardware and KL0 sections.
  - TM-079: p14-p17 were eyed. p15 (debugger) and p17 (library) match TR-057 p8-p10. p16 (editor)
    matches TR-057 p9 and adds the precedence levels: logical `:-` `,` `;`, functional `+` `-` `*`
    `/`, predicate `<` `>` `=`. p18 (conclusion) was OCR only.
  - TM-388: p85-p91 (macro chapter) were OCR only. p91 says only that a macro bank must be stored
    before use. p106-p110 are the built-ins chapter (OCR only, out of scope).
  - TR-087: p3-p4 were OCR-triaged (subsystem list; the execution environment is program,
    library, world, universe). p6-p11 were OCR. p2, p5, p12 and p13 were OCR-triaged; p13 holds
    the Kurokawa coordinator reference.
- OCR only: TM-229 p1-p4; TM-181 p1-p2; TM-143 p1-p2; TR-057 p7-p10; TR-087 p6-p11; TM-115 p92, p109;
  TM-388 p82, p92-p105 and App. G; TM-146 p5, p8; TM-364; TR-285; TM-634; TR-226, TR-227, TR-281;
  TM-189; TM-009; TM-055 and TM-075 (fresh tesseract in work/ocr2); TM-404.

## CHECKED, NOTHING
- TM-404: UNIX netnews, nothing on SIMPOS PS.
- TM-634 (Fujitsu ACE): no SIMPOS programming-system UI.
- TR-226, TR-227, TR-281, TM-189 (PROTON): nothing on running programs under SIMPOS, nor on the
  librarian, debugger or shell.
- TM-055, TM-075: no programming-system content.
- TR-285: only the situation-stack top-level loop. No menus, no commands.
- TM-364: window material only; no compile/load/run pages.
- TM-388 App. G: meta call via `:refute` and assert/retract via pools. These are language matters
  only, with nothing on the librarian or debugger.
- TM-009: nothing in scope.
- TM-126: only p6 (the Edips screen) is in scope.
- PMACS key commands: no Pmacs key-command table is printed in any held report. There are only the
  pop-up menu (TM-229 p6), the `Find File:` echo line (TM-181 p4) and a "100+ commands, emacs-like"
  statement. The likely source, SIMPOS文書編集機能説明書 (1987), is not held. Edips has only its
  1985 menu.

## OPEN QUESTIONS
- Login-file labels are printed with single quotes in TM-785 and double quotes in TM-786. Is the
  label an atom or a string, or are both accepted?
- The 7th Pmacs pop-up item (TM-229 p6) and that menu's title are illegible.
- required/requirements.tsv lists `as_program` CLASS method `goal/2`. The reports print only
  the INSTANCE method `:goal(Obj)` (goal/1, user-defined). Is goal/2 a class-side starter (for
  example `:goal(Class,Obj)`) in later versions?
- TSV note: debugger rows are filed under subsystem `shell` and editor rows under `other`, to match
  the partition files. Window rows whose receiver is `Obj!window` (from with_user_window) have an
  empty class.
- Is the 2.10 debugger goal prompt `:-` or `?-`? 1.0 shows `:-`.
- What do the 2.10 `Utility` sub-commands contain? Probably the old Print/Info/Classes/Predicates
  (INFERENCE).
- No printed logout text or procedure was found. Is "login" in MEDIA SYSTEMS also the way to log
  out or change user? Unknown.
- Where is the user profile/login file kept, and what is its name? The reports only say "login
  file" (ログインファイル) and "initialisation file" (初期化ファイル).
- How does the debugger get control on an uncaught error in a user process? Only the debugger's own
  error menu (TM-181 p5) is printed.
- Not held: "SIMPOS OPERATION MANUAL" (SIMPOS操作説明書), "SIMPOS PROGRAMMING MANUAL", SIMPOS使用説明書,
  SIMPOS文書編集機能説明書 (1987), and Kurokawa's coordinator paper (cited in TR-087).
