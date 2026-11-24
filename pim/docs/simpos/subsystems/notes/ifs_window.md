# ifs_window: the SIMPOS window system as the held IFS application sources use it

Agent: ifs_window. Extract root: `simpos2/extract/ifs_simpos/<archive>/`. Citations are `path:line` relative to that root; papyrus sources come from `simposspec/B/x/papyrus_src` (unpacked papyrus `source.tar`).
Grades: PRINTED, PRINTED-INTERFACE, USAGE, PROSE, INFERENCE. Arity counts the receiver. Version: unless tagged otherwise, every fact is from the held programs (SIMPOS 3.x-7.x era, files dated 1986-92, which write `mouse#l`). TM-125 (1985) facts are tagged 1985, and that document writes `mouse$l`.

TSV: `notes/ifs_window.tsv`, 1223 rows. Row kinds: class 334, option 320, keycode 219, imethod 136, command 101, nature 77, cmethod 21, menu_item 12, event 3.
The TSV is built by `work/ifs_window/mktsv.py` from the scan outputs plus `facts2.tsv`. `facts2.tsv` is the curated `facts.tsv` after `fixfacts.py`.

What the checks actually test:
- `chk.py` only tests that the member token appears within ±2 lines of the cited line.
- `fixfacts.py` does three things to curated imethod/cmethod rows:
  - Re-cites any row whose cited line was a clause head or a `before:`/`after:` demon to a plain send of the same selector/arity, keeping the demon or override site in the meaning text. Rows where no plain send exists are flagged in the meaning.
  - Renames the class column to the requirements.tsv spelling when requirements.tsv attributes that selector/arity to a window-partition class. The nature I first assigned is kept in the meaning text.
  - Regrades rows whose meaning comes from the name to INFERENCE.
- Rows where requirements.tsv has only `?` or brace sets keep my class (the defining nature by usage), and the meaning says so.
- Classes in braces (`{choice_window}`, `{standard_menu}`, ...) and the class `keycode` on menu_item, event and keycode rows are my grouping labels, not SIMPOS names.

Log: `out/fixfacts.log` (32 renames, 13 re-cites).

Generated rows:
- Option rows cite a `:create` of that same class that contains the key (from `out/creates.tsv`).
- Class rows carry the class's SIMPOS-selector overrides and its demons, as `selector/arity@line`.

Hand spot-check of 5 random option rows and 5 keycode rows: all 10 cited lines show the claimed key or constant.

Work files, all in `work/ifs_window/out/`:
- `winclasses.tsv`: 334 application classes whose nature closure reaches the window partition.
- `ovdem.txt`: every demon or SIMPOS-selector override body in those classes, all read.
- `creates.tsv`: 1771 creation sends.
- `create_keys.txt` and `create_keys_sys.tsv`: the creation keys.
- `winsends.tsv`: 8554 window-attributed sends, joined to census cls/how.
- `consts_raw.txt`: 1650 `prefix#token` hits.

Caution: the census attributes most window sends as `?`. The claims below that come with a citation were read at the call site. Counts are raw token or selector counts over all 15 programs. They include method heads and non-window receivers unless they are labelled as being from winsends.tsv. Some selectors are shared with non-window classes: kappa read/4,5 and write/5 belong to its file manager, and cil putl/4 belongs to library_utility.

## 1. Application window classes: natures and overrides

334 classes across 15 programs: kappa2 69, papyrus 50, kwic 47, sum 38, cil 33, icotext 28, cal-esp 20, txtstrct 11, gog 12, euod 10, fuzclust 8, disc 3, chal 3, knov 1, utter 1. Every class appears in the TSV as kind=class with its natures in the order written (USAGE).

### Nature order (USAGE, counted over all 334)
Mixins come first and the base class comes last. Base classes are always last or near last:
- inferior_window: last 110 of 132 uses
- temporary_window: last 11/11
- pmacs_standard_editor: last 26/26
- editor_main_window, standard_popup_menu, temporary_single_scrolling_menu: always last

Mixins are first or in the middle: as_mouse_input (120 mid), with_superior_input_buffer (31 first), with_border, with_margin (20 first), sash and labeled_sash (often first).

### Recurring recipes (USAGE)
| recipe (as written) | used for | example |
|---|---|---|
| `with_pmacs_window, as_superior, ..., inferior_window` | editor pane inside an app frame | cal-esp/deb2.12/windows.esp:9 |
| `sash, as_menu, as_single_select, as_mouse_input, with_superior_input_buffer, inferior_window` | menu pane in a frame | cal-esp/cal2.12/sccmds.esp:8 |
| `with_border, ..., as_superior, reshape_notifier, ..., inferior_window` | reshapable frame | cal-esp/cal2.12/scawin.esp:8 |
| `with_icon, with_key_select, ..., standard_superior_window` | top-level iconifiable frame | cil/src/ds_brs.esp:120 |
| `labeled_sash, as_scroll, as_output, as_graphics, as_markers, as_input, as_mouse_input, user_window` | kappa `class window` | kappa2/kappa2/utility/fmp/UTL_WIND.ESP:6 |
| `cprolog, as_standard_io_window, inferior_window, screen` | sum `class window` | sum/src/title_win.v32:11 |

The kappa list is the same, nature for nature, as the measurement-window list printed in TM-125 p20 (PROSE 1985, listings/tm0125_p20.txt). That makes `user_window` a real SIMPOS base class: it is tier A in classes.tsv but is in no partition.

### Overrides and demons (USAGE, from ovdem.txt)
| hook | what the bodies do | example |
|---|---|---|
| `:has_been_reshaped(W)` (reshape_notifier callback; 13 overrides, 6 after-demons) | `:get_inside_size`, then `:reshape(Child,X,Y,W,H)` for each pane | cal-esp/cal2.12/scawin.esp:68; kappa2/.../mdu/MDU.ESP:510; kappa2/kappa2/user_if/pb/pbwin.esp:44 |
| same, kwic | refuses the resize: restores the saved size with set_size and shows ウインドウのサイズは変更出来ません (TRANSLATION: "the window size cannot be changed") | kwic-esp-002/kwic-esp/src/windows.esp:51-57 |
| `after:create(Class,Init,W)` / `after:create_with_input` | build the sub-windows and save them in slots | txtstrct/ctx_system.esp:403 |
| `after:activate` / `before:kill` | activate or kill the child panes (20 classes) | txtstrct/ctx_system.esp:403-438; kappa FMP.ESP:72-82 |
| `after:show`, `before:deactivate` | `:read_sense(W,_)` to drain stale input | cal-esp/cal2.12/cwindow.esp:202,213 |
| `after:gett` / `before:gett,getl,getc` / `after:putt,putf` | `:put_back(W,key#lf)` / `:set_input_position(W)` / `:flash(W)` | cil/src/es_trc.esp:1401-1420; cil/src/es_wks.esp:1414-1433 |
| `before:set_title/activate/deactivate` | `:assign_window` (with_shared_window) | cil/src/ms_cfm.esp:118-128 |
| `before:/after:close` | swap the window for its icon | kappa2 MOPMWIN.ESP:31-37 |
| `after:has_been_selected` (select_notifier) | record the selection | kappa2/kappa2/user_if/pb/pbwin.esp:72 |
| `after:initiate(Class,_,W)` | `:set_mouse_marker(W,6)` | cal-esp/cal2.12/grmenu.esp:14 |
| `after:select_item(Menu,Item,_,_)` | react to a menu pick | kappa tam.esp:25 |
| `after:word_processor_mode/1,2`, `after:romaji_mode/1` | update the input-mode display | kwic-esp-002/kwic-esp/src/windows.esp:615-628 |
| `after:select_buffer`, `after:list_buffers` | papyrus buffer-switch hooks | papyrus_src/demo/EDITOR/my_select.esp.1:14,21 |
| `:goal(_)` in as_program classes | program entry point | (many) |

cal-esp's `as_graphics_menu` (grmenu.esp) re-implements the menu API on top of as_graphics:
- `read/2` is `:as_mouse_input:read(W,_,Click)`, then get_mouse_position, then a hit test.
- It also implements retrieve_item, change_item, delete_item(s), set/get_item_status and set/get_font.

This shows which methods a menu is expected to answer (USAGE).

Nature-qualified super calls (USAGE):
- `:as_mouse_input:read(W,_,Click)` (grmenu.esp:50)
- `:as_input_buffer:read_with_click(W,C,M)` (scawin.esp:202)
- `standard_popup_menu:create(Class,[items_list(I)],M)` (ccmenu.esp:37)

## 2. Creation protocol (USAGE; 1771 sends, per-class keys in out/create_keys.txt)

### Forms
- `:create(#C, InitList, W)` is the main form. `:create(#C,W)` also occurs.
- pmacs_window: `:create(#pmacs_window, Init, _, W)`. The third argument is always unbound; it is probably an editor out-argument (INFERENCE).
- `:create_with_input(#C, Init, _, InputSuperior, W)` and a 4-argument form.
- editor_text_buffer:
  - `:create(#editor_text_buffer, Buf, Name, Size)`. The output is the second argument, and the call fails if Name already exists, so code falls back to `:get_buffer_instance(#editor_text_buffer,Name,Buf)` (cal-esp/deb2.12/dmenu.esp:1214-1216).
  - Also `create/3` and `create_with_parameter(#..,[],_,Name,Buf)`.
- Text-buffer accessors: `:create(#standard_input_text_buffer_accessor,Buf,Acc)` and the output variant.
- `standard_io_buffer` create/2 and create/3.
- `#font :create(#font,Path,F)`.

### Keys on SIMPOS classes (counts over all classes; per-class rows in TSV kind=option)
| key | uses | value forms |
|---|---|---|
| size/2 | 418 | dots `N,N`; character units `ch(N),ch(N)`; expressions; `size(manipulator)` 17 |
| title/1 | 364 | string (gog wraps it in a `moji(..)` macro) |
| items_list/1 | 322 | list of item vectors (§3); a list of lists for multi-column |
| position/2 | 312 | `X,Y`; `position(manipulator)` 45 (the user places it with the mouse) |
| font/1 | 243 | a font object, or the class `#font_13` |
| nature/1 | 206 | written both `nature([..])` and `nature [..]`; mixins added at creation: with_superior_input_buffer, as_menu_input, with_shared_window, with_icon, reshape_notifier, with_key_select, as_inhibit_reshape, with_no_execute_choice_item |
| label_font/1 | 153 | font object |
| label_flag/1 | 139 | always `off` |
| superior/1 | 136 | superior window object |
| choice_list/1 | 50 | choice items (§3) |
| border_width/1 | 35 | N |
| permission/1 | 33 | `out`, `show` |
| border_flag/1 | 29 | `on`/`off` |
| margin/4 | 17 | 4 numbers |
| notified/1 | 5 | |
| margin_flag/1 | 4 | |
| label_position/1 | 2 | `bottom` |
| icon/1, menu_font/1, echo_area/1 | 2, 2, 1 | `echo_area(show)` |

Keys seen only on user subclasses. The programs never pattern-match them, so SIMPOS must consume them (INFERENCE from USAGE):
- pmacs_window: `editor(#C)`, `buffer_class(#C)`, `status_window(off)`, `echo_area_pmacs(on)`, `buffer(B)`
- with_two_labels: `top_title`, `top_label_font`, `bottom_label_font`
- `mouse_marker(N)`

Two exceptions are parsed by the application itself, not SIMPOS:
- kwic `icon(Id)`: `member(icon(..),Init)`, kwic inSheet1.esp:29
- `data_count(..)`: kwic scrolls.esp

Cross-check: `PIM/docs/fep_services.md` §6.9 reads the compiled pimfep login requester. It creates a `simpos##standard_io_window` with size in ch units, `position(manipulator)` and `nature([with_icon])`, using font `"font:test_11.font"`, and then uses clear/show/putl. This is the same protocol the IFS sources use (USAGE, from the PIM docs). §6.8 records `pimos_window` inheriting `simpos##pmacs_window` and `pimos_window_editor` inheriting `simpos##standard_editor`.

TM-125 Table 1 (PROSE 1985) lists superior, position, size, title, top_title, bottom_title, `margins/4` and `units/2`. Variant: TM-125 writes `margins(L,R,H,T)`, while the held programs write `margin(..)`.

## 3. Menus and choice windows (USAGE)

### Menu item `{Label, Type, Value, Doc}`
Doc is help text shown in the status line; TM-125 p14 agrees (PROSE 1985).

Type counts: common 1627, no_select 382, string 283, choose 148, switch 76, boolean 35, do_it 26, abort 23, pick_up 5.

Other item shapes:
- Five-field `{L, common|switch|no_select, V, Doc, on|off}` for on/off menus (fuzclust/fuzclust/src/g_menu_pro.ctl:44).
- Multi-column menus use `items_list([[col1..],[col2..]])` (euod/DEF/def.esp:1319).

### What a read returns
- `:read(Menu,V)` returns the item's Value, or `abort` (txtstrct/ctx_system.esp:31-32).
- Multiple-select menus use pick_up items with a do_it item (knov/src/system/ap.esp:75-83).
- `:read_with_click(Menu,V,Click)` also returns the button code mouse#l/ll/m/mm/r/rr (cal-esp/cal2.12/file.esp:94).

### Choice-window items
| item shape | meaning |
|---|---|
| `{L,string,Key,Width,Default,Doc}` | text field |
| `{L,string,no_select,Key,Width,Default,Doc}` | display-only text field |
| `{L,boolean,Key,_,true\|false,Doc}` | boolean |
| `{L,choose,Key,[{Lab,Val}..],Default,Doc}` | one of N |
| `{L,choose,no_select,..}` | display-only one of N |
| `{"do_it",do_it,_,_}` / `{"clear",abort,_,_}` | execute / clear |

Sources: sum/src/sub_win.wkm:42-73, sum/src/menu_init.wkm:48-81, gog-esp/CGS_INSTALLER.esp:55-69, knov/src/system/kvs_menu.esp:84.

- `:read(Choice,X)` returns `abort` or `[{Key,Value},...]`.
- `:change_item(W,Key,Item)` replaces an item.
- TM-125 (1985) gives the variant `{item_string,item_type,elements_list,initial_element,documentation}` (PROSE 1985).

### Other menu methods
add_item/3,4, add_items/3,4, clear_items, delete_item(M,String), set_item_status(M,Id,on|off), get_item_status, retrieve_item(M,Id,Vec), retrieve_all_items, enable_menu_help_click, set_help_font, read_with_code/3,4, get_activity.

## 4. Input and events (USAGE)

### Read forms
| call | returns | cite |
|---|---|---|
| `:read(W,C)` | character code, mouse#X, or a menu value | cal-esp/cal2.12/control.esp:456 |
| `:read(Sup,Source,Code)` | which child window was used, plus the code | euod/DEF/def.esp:111 |
| `:read(W,S,D,C,X,Y)` | the full event. The doc comment (TRANSLATION) gives S as 実際に入力したウィンドウ "the window actually input to", D as 入力されたkey "the key entered", C as 入力されたコマンド "the command entered", and X,Y as x座標/y座標 | send cal-esp/cal2.12/cpwindow.esp:124; comment :130-137 |
| `:input_data(W,S,D,C,X,Y)` / `input_data(W,Code)` | pushes a synthetic event, e.g. `(W, W!current_context_window, mouse#r, display, 0, 0)` | cal-esp/cal2.12/ctree.esp:153 |
| `:read_sense(W,C)` | non-blocking; `'$$nil'` when nothing is pending | cal-esp/cal2.12/scawin.esp:213 |
| `:read_with_click(W,Code,Click)`, `/4` with Source | Click is `'$$nil'` when the event was a reshape | cil/src/es_ins.esp:658-664 |
| `:read_click_with_position(W,Click,X,Y)`, `/5` with Source | Click may be passed in bound to wait for one button | fuzclust/fuzclust/src/input_mat.clu:97 |

Mouse and display queries:
- get_mouse_position/3, get_mouse_dot_position, warp_mouse/3
- `:get_mouse(#bitmap_display,M)` then `:get_position(M,X,Y)` (kwic windows.esp:110)
- set/reset/get_mouse_marker

### Interrupts and aborts
- `:set_break` / `:reset_break` / `:break(W)` let a long scroll be interrupted.
- `key#abort` is tested in input loops (cal-esp/deb2.12/input.esp:123), as is `control#"c"`.
- Menus return `abort`.
- `:activate(W)` can fail. kwic then retries after `:set_position(W,manipulator,_)` (kwic windows.esp:84-89).
- `:activate(W,mouse)` activates at the mouse position.
- Quitting does `:self(#process,P),:exterminate(P)`.

### Constants (all in the TSV as kind=keycode, 219 rows)
- mouse#: l 87, ll 69, r 61, mm 47, m 43, rr 6. The doubled letter is a double click (USAGE).
- key#: lf (200), cr, del, enter, tab, esc, bs, bell, up/down/left/right, abort, help.
- pf#0..18 and keypad#0-9 , - .
- meta#"x", control#"x", control_meta#"x", control#left.

The full family list is in cil `cil_esp.esp:120-254`, a re-implementation of the SIMPOS `#` macro expander (USAGE; see POSSIBLE SIMPOS CODE):
- `#Char`, key#Name
- control#, meta#, control_meta#
- pf#, control_pf#, meta_pf#, control_meta_pf#
- keypad# with the same three prefixes
- mouse#Click
- string#, jis#, ascii#, words#, double_bytes#, bytes#, bits#
- `Radix#String`
- `standard#input/output/message`, which expand to `:standard_input(:self(#simpos##process))` and the like

The euod software keyboard (euod/DEF/def.esp:1318-1640) lays out the whole PSI keyboard with key-cap codes, plus break, capslock, ctrl, shift and meta. `pf#8` is help and `pf#9` is abort; this comes only from `%help` / `%abort` source comments at lines 1553-1554, beside key-cap codes 16#"0078" and 16#"0077".

TM-125 (1985) variant: it writes `mouse$l` and lists `scroll_request(Off)` as an input code (PROSE). Neither appears in the held code.

## 5. Standard io text protocol (USAGE)

### Output
- putl/1 writes a newline; putl/2 writes a string, then a newline.
- putb(W,S,Len).
- putc(W,Code) takes a 16-bit JIS code or key#lf.
- putt/2, and putt/4, which threads a variable-name table.
- putf/3 (905 uses) and putf/2 (689 uses).
- write/2, write_line/2,3,4, write_line_tail/4, write_lines/2, put_line/2.

### Input
gett/2, gett/4, getl/2, getc/2, get1/2, getb/3, end_of_input/1, put_back/2, get_with_prompt/3.

### Screen and window control
- clear/1, clear_buffer/1, clear_line/1, beep/1, flash/1.
- move_cursor(W,Col,Row), get/set_cursor_position, erase_cursor/draw_cursor.
- set_font/get_font, set_label_font.
- set_color_pair(W,I,{{R,G,B},{R,G,B}}) with 16-bit RGB (kappa2 pdim.esp:590).
- `:get_plane_count(#bitmap,N)` tells colour from monochrome.
- Term printing: set/get_(un)parsing_operator, unquote_atom.

### putf directives
Evidence:
- Usage counts across the held programs.
- kwic `fncSPutf.esp` (414 lines), the class `fncPutfToString`, which re-implements putf into a string. It reflects what kwic's authors believed putf does; it is not SIMPOS code.

Grade: INFERENCE for the table as a whole, since it rests on kwic's re-implementation. The directives also seen in real putf calls, and so USAGE for their form, are `\n`, `\Nn`, `b`, `s`, `d`, `c`, `q` and `f`.

Syntax: a backslash, then optional numeric prefix parameters (digits; `.` separates them; `@` takes a value from the arguments), then modifiers such as `<`, then a command letter. A plain `\n` is a newline, with a count (`\2n`).

| command | meaning |
|---|---|
| `b` | blanks; the count is the product of the parameters (`\4b`, `\.@b`) |
| `c` | a character, `\N.Mc` |
| `d`, `o`, `x` | a number in radix 10, 8 or 16 |
| `i` | a number in radix R, `\N.M.Ri` |
| `s` | a string, `\N.Ms`; `<` left-justifies |
| `q` | a quoted term |
| `Q` | toggles quoting |
| `[..\;..\]` | choose the Nth alternative |
| `k` | skip arguments |
| `m` | repeat arguments |
| `{..\}` | iterate |
| `f` | a float, seen in gog as `\6.6.4f` |

Some uses have a backslash before a letter that is not in this table: `\C`, `\W`, `\u`, and one before a kanji. Their meaning is unknown.

A Prolog-style io layer (read_term, put, write_term, new_line, tab) is mapped onto pmacs window methods via `:undefined_method` delegation (cal-esp/deb2.12/pmod.esp:54-110).

### Graphics
| call | notes |
|---|---|
| draw_line/5,8 | `(W,X1,Y1,X2,Y2,Width,solid,set)` |
| draw_string/5,6 | `(W,X,Y,S,Font,set\|reset)` |
| draw_filled_rectangle/6,8 | |
| transfer/8 | `(..,copy)` |
| copy/9 | between windows |
| paint/5 | |
| hardcopy | `(W,laser_printer)` |
| background | `(W,black\|white)` |
| set_permission | `(W,out)` |
| create_marker/7 | |

## 6. PMACS window, standard_editor, editor_text_buffer (USAGE)

The disc exshow.esp:23-35 sequence:
1. Create the window.
2. `get_editor`
3. `reset` the buffer
4. `read_file(E,B,File,_)`
5. `set_input_buffer`
6. `get_interpreter`
7. `:command_interpret(I)`

Key bindings are instance clauses `:command(Editor, Input, Method);`. Input is a mouse#/key#/control#/meta# code or a menu value.
- 223 such clauses; papyrus `my_input` alone has 153.
- Prefix tables are `:control_c(..)` and `:control_x(..)` (cal-esp/deb2.12/dedit.esp:93-120).
- 101 bindings with `#` codes are in the TSV, kind=command.

kappa KMACS.ESP:67-93 dispatches a right-click menu by name: `:command(Self,mouse#r,kappa_menu)` binds the click, `:method(E,Item,1)` tests that the method exists, `:refute(E,Item,{})` calls it, and `:exception(E,"msg")` reports an error.

Methods used:
- Editor: get_window, current_buffer, set_current_buffer, select_buffer, insert, find_file, two_windows, mark, word_processor_mode, romaji_mode, add_history, clear_input, carriage_return.
- Window: get_editor, get_interpreter, set_input_buffer, show_buffer, set_echo_font, clear_echo_area, put_back, set_input_position.
- Buffer: assign, insert_string, move_to_last, current_position, move_begin_of_line, delete/3, reset.

## 7. Fonts (USAGE)

`:create(#font, Path, F)`. Path forms:
- `"font:kanji_16.font"`
- `"font:kanji_16"`
- `">sys>font>kanji_16.font"`

Fonts seen: tiny_7, test_11, font_13 (the default; 13x19 per TM-125, PROSE 1985; also usable as the class `#font_13`), kanji_16, kanji_28, cap_11, grape_16/28, scroll.font, kanji_cal.font.

Related calls:
- `:system_font(#window_subsystem,F)`.
- Icons: `:add_icon(#window_subsystem, icon, "font:fmp.icon", 24)`, then `:set_icon(W,24)` (kappa FMP.ESP:41).
- `:get_size(#screen,W,H)`.
- `:create(#font_editor,FE)`.

## POSSIBLE SIMPOS CODE
- **cil `src/cil_esp.esp`** (package esp_call, ICOT 1990-91): ESP builtin, syntax and `#`-macro tables re-implementing the SIMPOS macro expander's constant families. It is the best written statement of the `#` constants.
- **kappa `utility/fmp/UTL_WIND.ESP:6`**: `class window` uses the TM-125 p20 nature recipe verbatim. It is an application class (ICOT 1992 copyright), but it confirms the SIMPOS `user_window` recipe.
- **sum `src/title_win.v32:11`**: `class window` mixes in `screen`, which overlaps a SIMPOS name.
- **kwic `fncSPutf.esp`**: a putf re-implementation, not SIMPOS code, but the most detailed putf semantics held.
- **cal-esp `grmenu.esp`**: as_graphics_menu re-implements the menu API.
- **cal-esp `deb2.12`**: the CAL debugger, which uses SIMPOS debugger_gate and debugger_error. It is application code.
- cil library_utility, coordinator and message are already in NOTES.

No verbatim copy of a SIMPOS window-system class was found.

## PAGES READ
- No PDF pages were looked at.
- Read: `PIM/docs/simpos/` STRUCTURE.md §7 and §11, `listings/tm0125_p13.esp`, `listings/tm0125_p20.txt`.
- Also read: `PIM/docs/simpos/README.md` §2 and §4. It says windows are "mixin source for 4 classes, about 45 method signatures"; the window bodies are among the lost parts. Also `PIM/docs/fep_services.md` §6.8-6.9.

## OPEN QUESTIONS
- Natures that are in no partition: `as_inhibit_reshape`, `with_keeping_status` (tier A), `user_window`.
- The third argument of pmacs_window create/4.
- What get1/2 does.
- The unknown putf escapes `\C`, `\W`, `\u`.
- The exact meaning of permission/1 values beyond out and show.
- The vkey key-cap code numbering (16#"0078" etc.).
- Mouse-marker numbering (6 = wait?).
- Many of the 265 window selectors in requirements.tsv were checked only by count, not by reading the call site.

## CHECKED, NOTHING
- No held program defines a class named like a SIMPOS window-system class except `window` (kappa, sum).
- No program pattern-matches creation keys other than kwic `icon/1` and `data_count`.
- `scroll_request` and `mouse$` do not occur in the held code.
- `:new`: 657 `:new(` sends exist, but no `:new(#C,..)` names a window-partition class (`out/new_classes.txt`). Every window and menu is made with `:create`/`:create_with_input`.
