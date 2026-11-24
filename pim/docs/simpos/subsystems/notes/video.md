# video: ICOT museum PSI video (Mitsubishi "MELCOM PSI" promotional video)

Source: `pim/docs/nonlocal/lit/web/icot-museum-video-psi/` (seven .wmv + .html).
Citation form: `<segment>@<seconds>` = time into that .wmv (ffmpeg pts). All screen facts are
grade SCREENSHOT unless marked; the video is 320x240 VHS-quality, so every on-screen read is
"best reading" and uncertain glyphs are marked `[?]`.
Work dir (frames, not committed): `scratchpad/simposdive/work/video/` (fps1_*/ = 1 fps for all 7
segments, sc_*/ = scene-change >0.2 frames, dense/ = 10 fps bursts, zoom/ = averaged 4-8x crops,
sheets/ = contact sheets, scripts/ = the extraction scripts).

## 0. The media

| segment | duration s | video | audio | html title (PROSE, TRANSLATION) |
|---|---|---|---|---|
| psi | 139.27 | wmv3 320x240 | wmav2 16 kHz mono | "This is PSI" |
| icot | 297.60 | same | same | "ICOT and PSI" |
| esp | 169.60 | same | same | "What's ESP" |
| simpos | 166.53 | same | same | "PSI's software SIMPOS" |
| prolog | 195.33 | same | same | "PROLOG is the best for AI" |
| melco | 210.73 | same | same | "Mitsubishi Electric and PSI" |
| closing | 136.60 | same | same | "Conclusion" (結び) |

- Every segment carries a mono audio track (Japanese narration presumably; NOT transcribed).
- The .html pages hold no captions or narration transcript, only a short museum summary each
  (PROSE, TRANSLATION, summarised):
  - simpos.html: SIMPOS = kernel (カーネル, manages PSI hardware) + I/O management (入出力管理,
    high-logical-level I/O) + programming system (プログラミングシステム, supports ESP
    programming); human interface lets one program "sensibly with the mouse".
  - esp.html: all PSI software modules are written in ESP (Extended Self-contained Prolog),
    Prolog + object orientation, usable as both system-description and user language.
  - psi.html: inference engine + knowledge base + man-machine interface, display, mouse;
    "over 40,000 inferences per second", main memory "up to 80 MB", tagged words.
  - prolog.html: unification + backtracking; worked example (which year did the Red team win
    Kohaku AND Hiroshima Carp become Japan champion).
  - icot/melco/closing.html: background only, nothing on SIMPOS.
- The earlier coarse pass `scratchpad/simpos2/extract/video_simpos/` holds f01..f21 (21 frames,
  not 22) + montage1.png. The montage matches simpos.wmv (structure diagram, edips.esp screen,
  system menu, "window definition" and "multi-process" cartoons); individual f-frames not
  re-checked one by one.

## 1. Versions and hardware

| fact | where | grade |
|---|---|---|
| Status line "USER : demo" / "SIMPOS Version A00" | esp@108-109 | SCREENSHOT |
| Status line "USER : KCM" / "SIMPOS Version 2.50" | melco@50, melco@157-158 | SCREENSHOT |
| caption "新世代コンピュータ技術開発機構 ICOT(1986.10)" over the ICOT office shots | icot@4.9-10 | SCREENSHOT (dates the icot footage, not necessarily the screens) |
| icot@22 screen has the same bottom status strip; text illegible ("SIMPOS Version ?.??") | icot@22 | SCREENSHOT |
| simpos.wmv shows NO version string. It shows the same `move_win` demo as esp.wmv (window title `librarian_1` in simpos, `librarian_2` in esp), so it is probably the same session/version A00 | simpos@117-125 vs esp@110-121 | INFERENCE |
| Machine is branded "MELCOM PSI" (caption "〈AIワークステーション MELCOM PSI〉", nameplate on cabinet) | psi@8.6, psi@31-35, esp@16-22, prolog@0-7 | SCREENSHOT |
| Hardware = PSI-I generation: tall floor-standing cabinet ("mini-computer size" per psi.html) beside a desk with separate CRT, keyboard and 3-button mouse; psi.html figures (40K LIPS, 80 MB) are PSI-I-class, not PSI-II (~330K LIPS, compact) | psi@23-35, psi.html | INFERENCE (spec numbers from memory of the literature, not checked against a repo source) |
| Mouse: three buttons, Mitsubishi-branded, on a blue pad | psi@23 (sc idx 6), simpos@84-89 | SCREENSHOT |
| Keyboard: separate, large, with numeric pad and rows of function keys; status line names PF0-PF6, PF10, PF16 | simpos@84-89, simpos@108-113 | SCREENSHOT |
| "A00" reads like an internal/pre-release build tag rather than a 1.x/2.x number; 2.50 dates ~1986-87 | - | INFERENCE |

## 2. WINDOW system (screen layout)

| fact | where | grade |
|---|---|---|
| Monochrome bitmapped screen, light (white) background, black text; overlapping rectangular windows with thin single-line black borders, no drop shadows | simpos@0-10, esp@110-121 | SCREENSHOT |
| Resolution impression: a full screen holds ~40+ text lines of the small ASCII font and ~80+ columns; consistent with a ~1000x800-class display. Not measurable from the video | simpos@61-62, esp@129-149 | INFERENCE |
| Window label (title) bar = a strip inside the top border, separated by a horizontal rule, holding the window's name left-aligned in the small font: `debugger_1`, `librarian_1`, `librarian_2`, `pmacs_1`, `file_manipulator_2`, `move_win` | simpos@0, @117, @124, @56; esp@118 | SCREENSHOT |
| Window names are `<program>_<n>` with a per-program instance counter (file_manipulator_2 created while another existed; debugger_1, pmacs_1, librarian_1/_2) | same | SCREENSHOT + INFERENCE (counter semantics) |
| Labels also occur at the BOTTOM of a window: `Action_Window` label sits in a bar along the bottom edge; another window has `Output_Window_2` (top), `Ga_Window`[?] (top), `Input_Buffer` (top) | melco@54-55, melco@147, melco@60, melco@50 | SCREENSHOT (application windows of a Mitsubishi NL-DB demo) |
| A user-made window with `:background(Win,black)` shows white-on-black text and a black label bar (`move_win`) with white label text | esp@118-121 | SCREENSHOT |
| Large-font window title centred in a box: `ExtKernel` (application menu window) | prolog@14-17 | SCREENSHOT |
| Bottom-of-screen system strip: a black (reverse) band across the whole screen bottom, below all windows. Left: two lines `USER : <name>` and `SIMPOS Version <v>`; then a reverse-video (white) box holding a window name (`Input_Buffer` in melco, `editor_wo[?]...` in esp). Right end (icot@22): another reverse box and a text field, illegible | esp@108-109, melco@50, melco@158, icot@22 | SCREENSHOT |
| The reverse-video box in that strip names the window that currently owns keyboard input | - | INFERENCE |
| The same bottom band is used for kana-kanji conversion: line 1 echoes romaji input after `>` (`>jinnkou_`), then shows hiragana `じんこう`, then a numbered candidate list `0.人工 1.人口 2.じんこう`; line 2 is a key-help line `>MENU(PF16) PF10=ON_OFF, PF0-PF6=MANAGE…` (truncated) | simpos@108-113 | SCREENSHOT |
| The chosen kanji is inserted in the target window (pmacs_1 shows `人工` then `人工知能`) | simpos@114-116 | SCREENSHOT |
| Fonts: ASCII fixed-pitch small font for labels, menus and editor text; kanji/kana at a larger cell size (a kanji is ~2 ASCII cells wide); big ASCII font in reverse status band. Menus and window titles have no proportional font | simpos@108-116, melco@147 | SCREENSHOT |
| Text cursor: solid black block (`?- █`, `人工知能█`) | simpos@0, @114 | SCREENSHOT |
| Mouse cursor: a small diagonal arrow on screen backgrounds (white arrow on the black move_win window); when on a menu a small `×` mark sits left/right of the highlighted item | esp@120 (arrow), simpos@132 (`× Inspector`), esp@165 (`×` by "Do it") | SCREENSHOT (shape partly INFERENCE at this resolution) |
| Menu highlight: the item under the mouse is boxed with a thin rectangle (not inverted) | simpos@1-5 none; simpos@10.9 `pmacs` boxed; @60 `file_manipulator` boxed; @117 `HIDE` boxed; @132 `Inspector` boxed | SCREENSHOT |
| Multiple-select menu: chosen items shown in reverse video (white text on black bar); a boxed `Do it` button at bottom-left | esp@163-169 | SCREENSHOT |
| Pop-up menus have a title bar (`SYSTEM MENU`, `top menu`, `Debugger Menu`, `Select files`, `WHICH ?`, `file_manipulator`) above centred items | see §4 | SCREENSHOT |
| Window creation by rubber-band: after choosing `create`, an empty outline rectangle is swept with the mouse and the new window (`file_manipulator_2`) appears at that size/place | simpos@49 (popup) -> @53-55 (outline) -> @56 (window) | SCREENSHOT (sequence; edit continuity INFERENCE) |
| No icons visible anywhere (no iconified windows on the background) | all screen shots | SCREENSHOT (negative) |
| Editor windows (PMACS) are split into panes, each with an Emacs-style mode line (see §5) | simpos@0, esp@108, esp@133-149 | SCREENSHOT |
| Cartoon slides (not screens): "ウィンドウ定義" (window definition) shows overlapping coloured rectangles on a monitor; "マルチプロセス機能" (multi-process) shows tiled task windows (原価計算, 給与計算, 仕入先リスト, 見積計算, 信用評価, 記帳指令) plus a red "メニュー" button | simpos@62-70, simpos@99-107 | SCREENSHOT (illustration, PROSE-level) |

### Window menu (per-window operations)

Upper-case items in a narrow pop-up at the right edge of the screen, cut off by the camera
frame at the bottom (simpos@117-118, librarian_1 / pmacs_1 visible beside it):
1 `SHOW`, 2 `HIDE` (boxed = being chosen), 3 `RESHAPE`, 4 `MOVE`, 5 `EXPAND`, 6 `MENU`,
7 `PERM…` (rest cut off), 8 `ATT…` (rest cut off). Possibly more below. SCREENSHOT.

## 3. SHELL / top level

### SYSTEM MENU (simpos@9.6-11.3, again simpos@59.7-62.0)

A pop-up titled `SYSTEM MENU` with two columns. Read from the 10 fps burst and averaged crops.

| col | row | item | confidence |
|---|---|---|---|
| L | 1 | `Experts` | good (header or item? unresolved) |
| L | 2 | `8puzzle` | good |
| L | 3 | `debugger` | good |
| L | 4 | `edips` | good |
| L | 5 | `pmacs` | good (boxed at @10.9) |
| L | 6 | `file_manipulator` | good (boxed at @60) |
| L | 7 | `librarian` | good |
| L | 8 | `spooler` | good |
| L | 9 | `font_editor` | good |
| R | 1 | `MEDIA SYSTEMS` | good (upper case; header or item? unresolved) |
| R | 2 | `user process list` | good |
| R | 3 | `window manipulator` | good |
| R | 4 | `network` | good |
| R | 5 | `shell` | good |
| R | 6 | `whiteboard`[?] | moderate (shape `wh…board` at @60.0) |
| R | 7 | two words, illegible (`re…` / `…` ) | poor |
| R | 8 | `garbage collect[ion]`[?] | moderate |
| R | 9 | short word, `login`/`logout`[?] | poor |
| R | 10 | two short words, illegible | poor |

Notes:
- No `editor` item: the editor is listed by name (`pmacs`), plus `edips` (an application in
  this demo; a window `edips.esp` is open). `Experts`, `8puzzle`, `edips` are demo/application
  entries, so the menu is user-extensible (application entries above system tools in the left
  column). INFERENCE.
- This contradicts the earlier summary in `pim/docs/simpos/source_notes.md:39` (which lists
  "debugger, editor, file_manipulator, librarian, spooler, font_..."): the frames show `pmacs`,
  not `editor`.
- Selecting `file_manipulator` (@10.9 shows `pmacs` boxed; @60 shows `file_manipulator` boxed)
  is followed by a small pop-up titled with the program name (`file_manipulator`) containing
  `create` and a second item cut off (`k…`); the analogous pop-up in prolog@14-15 is titled
  `WHICH ?` with items `create`, `kill`. So the system-menu dialogue is: choose program ->
  `create` (a new instance) or `kill` (an existing one) -> rubber-band the new window.
  SCREENSHOT (sequence) + INFERENCE (that both pop-ups are the same mechanism).

### Debugger

| fact | where | grade |
|---|---|---|
| Window `debugger_1`, prompt `?- ` followed by block cursor | simpos@0-5, @126-127 | SCREENSHOT |
| Goal typed in it: `?- :make(#move_win,A).` (args after `#move_win` partly cut); answer shown on next line as ` A= ?move_win` where `?` is a `$`-like glyph; then a fresh `?- █` | esp@118-121 | SCREENSHOT |
| Running the goal opens the black `move_win` window with label `move_win` and text `MELCOM PSI` | esp@118-121 | SCREENSHOT |
| `Debugger Menu` pop-up items in order: `State`, `Set Spy`, `From last input`, `Input string`, `Inspector`, `To whiteboard`, `From whiteboard`, `Re-display` | simpos@129-137 (best crop @132) | SCREENSHOT |
| Subtitles name the shots デバッガ (debugger) and インスペクタ (inspector); the inspector itself is not shown open | simpos@124-133 | SCREENSHOT |
| `whiteboard` (a cut/paste buffer shared between tools) appears both in the Debugger Menu and (probably) in the SYSTEM MENU | - | INFERENCE |

### Login / user

- Only the status strip shows the user: `USER : demo` (esp@108), `USER : KCM` (melco@50). No login
  window is shown. A file `login.cmd.2` is listed in the user's directory (esp@163-169), i.e. a
  per-user login command file with version number 2. SCREENSHOT; purpose INFERENCE.

## 4. LIBRARIAN

| fact | where | grade |
|---|---|---|
| Librarian window (`librarian_1`) is a tall narrow window whose body is a fixed vertical command menu: `Check`, `Catalogue`, `Compile`, `Uncompile`, `Save`, `Load`, `Delete`, `Execute`, `Utility` (in this order, nine items) | simpos@0-5 (whole list), @117-122 (with label) | SCREENSHOT |
| Same menu in `librarian_2`; beside it an output pane showing `File Name>move_win…` then `Cataloging "move_wi…` (the prompt-and-echo of a Catalogue command) | esp@117.6-121 | SCREENSHOT |
| Subtitle ライブラリアン (librarian) over it | simpos@119-122 | SCREENSHOT |
| After cataloguing, the class is usable from the debugger: `:make(#move_win, …)` | esp@118-120 | SCREENSHOT |

## 5. Editor (PMACS) and file system

| fact | where | grade |
|---|---|---|
| Editor window label `pmacs_1`; subtitle スクリーンエディタ (screen editor) | simpos@112-116 | SCREENSHOT |
| Mode line, Emacs style, in a bar under the text pane: `PMACS(esp)(87,26) *-1* move_win…` ; `PMACS(esp)(68,16) *-2* demo>8pzl.esp.1` ; `…(48,14) *-1* --Top-` ; `…>8pzl.esp.1 --0%--` ; `…me>fdd_utility.esp.1 --2[?]%-` | esp@108, esp@133-134, simpos@0, esp@139, esp@139-149 | SCREENSHOT |
| Mode-line fields: editor name, major mode `(esp)`, a `(n,m)` pair (cursor position or window size), `*-<n>*` (buffer number/modified flag), file path, and scroll position `--Top-` / `--0%--` | - | INFERENCE |
| Echo/minibuffer line below the mode line: `Visit File(move_win.esp): █` | esp@108-109 | SCREENSHOT |
| Echo line after reading a file: `Read! >sys>user>demo>8pzl.esp.1` | esp@133-134 (1 fps frame; moderate legibility) | SCREENSHOT |
| Path syntax: `>`-separated absolute paths from a root `>sys>user>demo>…` (Multics-like), and every file name ends with a version number: `8pzl.esp.1`, `fdd_utility.esp.1`, `8boad.esp.37`, `8mes.esp.12`, `8win.esp.4`, `8video.txt.1`, `login.cmd.2` | esp@133-169 | SCREENSHOT |
| Another window label/mode line `[46-11] edips.esp` (bracketed pair before the file name) | simpos@6-10 | SCREENSHOT |
| `file_manipulator_2` window: inner pop-up titled `top menu` with items `listing`, `world`, `mount volume`, `dismount volume`, `initialize volume`, `copy volume`, `sync`, `MT utility`, `ipl maintenance` | simpos@56-59 | SCREENSHOT |
| `Select files` multi-select menu (user's directory): `8_solve.esp.1`, `8boad.esp.37`, `8mes.esp.12`, `8pzl.esp.1`, `8solv.esp.1`, `8video.txt.1`, `8win.esp.4`, `login.cmd.2`; button `Do it` | esp@163-169 | SCREENSHOT (it is the demo application's own menu class, see §6) |

## 6. Application code visible on screen (USAGE-grade evidence of the API; not SIMPOS code)

Only short fragments; lines run off the right edge, so arities are given only where the
closing parenthesis is visible.

- `move_win.esp` (simpos@123-125, esp@110-117), shown in `pmacs_1`:
  `class move_win has` / `nature as_output, with_label, inferior_window;` /
  `:make(Class,Win) :- :create(Class,[size(300,200)…` (cut) / `:background(Win,black),` /
  `:write_line(Win," MELCOM PSI…` (cut) / `:activate(Win);` / `instance` / `move(Win) :- …`.
  So: a window class built from natures `as_output, with_label, inferior_window`; created with
  `:create(Class, [size(300,200), …], …)` (attribute list incl. `size(W,H)`); then
  `:background(Win,black)` (2 args), `:activate(Win)` (1 arg).
- `fdd_utility.esp` (esp@129-149): `class fdd_utility has nature as_program; instance
  :goal(_):- get_path(Flag), :create(#fdd_utility_window, [position(man[?]ipulator…` (cut),
  `(Flag == to_fdd, !, :set_title(W, " FDD ==> F…") ; :set_title(W, " …"))`, `:activate(W),
  repeat, get_pathname(Flag, Pathname, …), check_pathname(…)`; later a prompt
  `" Another copying ? (y/n): "` and `:getc(W, Ans)`, `(Ans == "y", !, fail ; true);`.
  -> `as_program` nature with a `:goal(_)` instance-method entry (goal/1: the one argument
  is the receiver); window titled
  with `:set_title/2`; character input `:getc/2`.
- Same file: `class fdd_utility_file_menu has nature labeled_sash, as_scrolling_menu,
  as_multiple_select, as_mouse_input, temporary_window; end.` (comment header
  `% FDD UTILITY WINDOW %`) (esp@155-162). This is the "Select files" menu of §5.
- `8pzl.esp` (esp@129-139): `attribute board, message_window, window;`
  `goal(Class) :- … set_board(Class, Class!board), set_message_window(Class, Class!message_window)`
  — slot access syntax `Class!slot`.
- print utility (esp@23-42, prolog@160-182): `print_all([],_,_,_) :- !.`
  `print_all([Pathname|Rest], Window, …) :- :write_file_name(Window,…), :open(#binary_file, File, …`
  (cut), `:size(File, Size)`, `:new_buffer(File, Size/2…` (cut), `:read(File)`,
  `:get_data(File, Buffer…` (cut), `make_printer_object(…)`, `print_out(Buffer, Printer…)`,
  `:close(File)`, `:release(Printer_obj)`, `:write_complete(Window…)`, `print_all(Rest,…)`;
  `make_printer_object(serial, …) :- :get(#printer, Printer…), :set_font(Printer, kanji…)`;
  `make_printer_object(laser, …) :- :get(#laser_printer, Printer…), :set_font(Printer, an[k?]…)`.
  -> class objects `#binary_file`, `#printer`, `#laser_printer`; `:size/2`, `:read/1`
  (receiver only), `:close/1`, `:set_font/2` (font names `kanji…`, `an…`).

## 7. Structure diagram 〈SIMPOSの構成〉 (simpos@18-47)

A hemisphere ("onion") built up layer by layer (SCREENSHOT; labels TRANSLATION):
- Centre: ハードウェア (hardware).
- Flat base bands under the centre, from inside out: カーネル (kernel), 入出力管理 (I/O
  management), プログラミングシステム (programming system).
- Ring 1 around the hardware (appears with the kernel band, simpos@26): メモリ (memory, purple),
  デバイス (device, grey), 漢字…[?] (blue, second word illegible; kanji processing/dictionary?),
  green segment illegible, yellow segment illegible (`[I/O]`?).
- Ring 2 (appears with 入出力管理, simpos@32): ウィンドウ (window, green), ネットワーク (network,
  purple), ファイル (file, grey).
- Ring 3 (appears with プログラミングシステム, simpos@37-39): エディタ (editor, yellow) with the
  side label `(PMACS)`, デバッガ (debugger, blue), ライブラリアン (librarian, purple).
So kernel = memory/device/(kanji?)/… ; I/O management = window, network, file;
programming system = editor (PMACS), debugger, librarian. Agrees with simpos.html (PROSE).

## 8. Other screens (applications, not SIMPOS)
- prolog@14-41: `ExtKernel` menu window (スキーマエディタ schema editor, ブラウザ browser,
  エクスプレイン explain), a `WHICH ?` pop-up (`create`/`kill`), then a Japanese menu with
  reverse-video selected items and a text window whose bottom-left label reads `sate`[?].
- melco@50-62, @135-160: Japanese natural-language DB query demo (windows `Input_Buffer`,
  `Action_Window`, `Output_Window_2`); romaji input such as `> daha shozoku = keirino mono@`,
  `> salary >= 30desu@`; numbered-choice prompts (1) 削除 2) そのまま使用 3) 値の変更 …).
  melco@168-190: machine translation (`I need to go.`) and an estimation system (見積りシステム)
  with a `処理をどうぞ` pop-up `終了 / 翻訳 / 御破算`.
- icot@21-60, @186-260: blue-tinted screens (DUALS-V2 discourse system, parse trees); only the
  bottom status strip is recognisable.
- closing@75-104: AceKit, satellite-diagnosis expert system, other machines.

## POSSIBLE SIMPOS CODE
None. All on-screen source is demo application code (move_win, fdd_utility, 8pzl, print_all);
no SIMPOS source or binary is shown. The menus (SYSTEM MENU, librarian menu, window menu,
Debugger Menu, file_manipulator top menu) are SIMPOS's own UI as rendered, i.e. the strongest
primary evidence of SIMPOS ~2.5/A00 menu contents.

## PAGES READ (frames eyed)
- simpos.wmv: every second (fps1, 167 frames) eyed on contact sheets; 10 fps bursts at
  9.0-11.4, 48.0-49.6, 59.0-62.2, 116-118, 122.5-126; averaged zoom crops of every menu.
- esp.wmv: every second eyed; 10 fps bursts 22.5-23.5, 24-32, 117.5-122; zooms of 108, 119-121,
  129-169.
- prolog.wmv: every second eyed (sheets 01-10); zooms 14-20, 37.
- melco.wmv: scene sheet + fps1 sheets 03-04 (40-79 s); zooms 50, 147, 158.
- icot.wmv: scene-change sheet only + zooms 22, 52.
- psi.wmv, closing.wmv: scene-change contact sheets only.
- All seven .html pages read in full.

## CHECKED, NOTHING
- psi.wmv: hardware/branding only, no SIMPOS screen chrome.
- closing.wmv: other ICOT/Mitsubishi systems, no SIMPOS chrome identified at scene level.
- icot/melco/closing/prolog/psi/esp .html: no narration transcript.

## OPEN QUESTIONS
1. SYSTEM MENU right column rows 6-10 (whiteboard?, ?, garbage collection?, login/logout?, ?)
   need a better copy of the video (the museum's original or a higher-bitrate rip).
2. Are `Experts` and `MEDIA SYSTEMS` headers (category labels) or selectable items?
3. Window menu items 7-8 (`PERM…`, `ATT…`) full spelling; any items below them.
4. What is the `(87,26)` / `[46-11]` pair in the PMACS mode line (cursor line,col? window size?).
5. Debugger answer glyph in ` A= ?move_win` (`$`? `#`?).
6. Inner-ring labels of the structure diagram (blue 漢字…, green, yellow).
7. "Version A00" vs "2.50": internal build naming vs release numbering?
8. Narration audio (all segments) is untranscribed; it may name more menu items.
