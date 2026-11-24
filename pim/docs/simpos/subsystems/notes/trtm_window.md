# trtm_window: the SIMPOS WINDOW SYSTEM in the held ICOT TR/TM reports and the WINCS article

Agent: trtm_window. Scope: the window system, menus, fonts, mouse/keyboard input and the window side of the
Coordinator. Sources:
- lit/trtm: TM-125, TM-126, TR-046, TR-061, TR-055, TR-057, TM-065, TM-061, TM-153, TM-225, TM-224, TR-285, TM-181 (cited only).
- lit/journals: WINCS (今中 et al., コンピュータソフトウェア 8(1), Jan 1991, pp.54-70).

Machine-readable facts: `notes/trtm_window.tsv` (268 rows; arity counts the receiver). New transcriptions are
in `work/trtm_window/`:

| file | content |
|---|---|
| `tm0125_p05-07_concepts.txt` | TM-125 ch.2 (statuses, output permission, temporary/menu/choice windows) + **Fig 4 choice window** (new) |
| `TR-046_p23_p25.txt` | TR-046 Table 2 (eyed), Fig 1 window statuses, Table 3 window-relevant row |
| `TM-153_p23_p28_recheck.txt` | PSI system configuration (display/keyboard/mouse attachment); corrections to the existing TM-153 p28 listing |
| `TM-225_p08-11_window.txt` | TM-225 ch.6 window system (translated summary): functions, structure, save areas, 4 hidden-output options, input management |
| `WINCS_p12_fig5.esp` | WINCS Fig 5 synthesized natures, inline `my_window`, `draw_circle` call, `class_method`/`order` fact forms |
| `WINCS_p05_p13_screens.txt` | WINCS screenshots: attribute menu items, layout and labels |

Version tags:
- **1984 design:** TR-046, TR-055, TR-057, TR-061, TM-061, TM-065.
- **1985, SIMPOS 1.0:** TM-125, TM-126.
- **1986, SIMPOS 2.x:** TM-153 (2.00), TM-181 (2.19), TM-225 (2.5 current), TM-224.
- **1987:** TR-285.
- **1989–91, PSI II:** WINCS.

The held programs ran SIMPOS 3.0 to 7.1. Everything below predates them, and differences are flagged.

Grades used: PRINTED, PRINTED-INTERFACE, PROSE, SCREENSHOT, INFERENCE, TRANSLATION.

---------------------------------------------------------------------------------------------------
## WINDOW

### W0. Checks of the existing listings (results)
| existing file | check | result |
|---|---|---|
| tm0125_p08.txt (manipulator 12 items) | eyed PDF p8 at 130dpi | **correct** |
| tm0125_p08_classes.txt (69 names) | eyed PDF p8-13 | **correct**. The gaps print as "as single_select", "as_on off_menu" and "as choice". WINCS Fig 5 prints `as_single_select` clearly, and `as_on_off_menu`/`as_choice` are the spellings in partition_window. The TSV uses the underscore spellings (INFERENCE for the last two). |
| tm0125_p13.esp (ch.5 reference, Table 1) | eyed PDF p13-18 | **correct**. The header line "PDF pages 13-19" is right, but **Table 1 is on PDF p14 = folio 13**. |
| tm0125_p13.esp `mouse$l` glyph | re-zoomed at 600dpi (work/trtm_window/tm0125/g3.png) | The glyph is an S-shape with no crossbars, so it is **not '#'**. It is '$' in a proportional serif face, or possibly 'S'. Same glyph in `$$nil`. The 1984 reports (TR-046 p28, TR-061 p13) and the held code write `mouse#l` and `mouse#rr`. **The spec should follow `#`**; record the `$` as a TM-125 printing variant. |
| tm0125_p23.esp, tm0126_p06.* | not re-transcribed; p23 eyed at 130dpi | consistent |
| TM-153_p28_screenshot.esp | re-read at 300dpi | **Two corrections.** (1) The create call is `:create(#window,[size(416,430),position(manip…` with a **square bracket**, not `{`. (2) The version is "SIMPOS Version 2.00", and the status line also shows "SWAPPED" and "spool" boxes. See TM-153_p23_p28_recheck.txt. |
| parts/TR-046.structure.md Table 2 summary | eyed PDF p23 | **confirmed** (matches: EXPOSED waiting/done; OVERLAPPED waiting/"waiting/done"); now transcribed as TR-046_p23_p25.txt |
| parts/tm0125.structure.md "ch.5 :create/1 and /2", ":select/0" | arity convention | In receiver-counting arity these are create/2, create/3 and select/1. |

### W1. Class catalogue (TM-125 ch.4, PDF p8-13 = folio 7-12; 1985)
The report says SIMPOS has "about 120 classes", grouped into three types:
- **stand-alone:** usable by itself;
- **mixin:** supplies a function and is used as a superclass;
- **internal:** used by the window system, not by the user.

69 distinct names are listed with roles; with_mouse_scroll is listed twice. All 69 are in the TSV (kind=class,
grade PROSE), with the role text. Summary by group:

- **Stand-alone (20):** window, window_without_label, window_with_two_labels, superior_window,
  labeled_superior_window, menu, multi_column_menu, temporary_menu, temporary_multi_column_menu,
  multiple_select_menu, multiple_select_multi_column_menu, temporary_multiple_select_menu,
  temporary_multiple_select_multi_column_menu, submenu, menu_item, choice_window, choice_item, marker,
  popup_choice_window, window_region.
  - menu = single select, single column.
  - temporary_menu = single select, single column, temporary.
  - submenu = a menu that is a sub-window of another window.
  - menu_item has slots for the item string, return value, item type and documentation.
- **Mixin, primitive (17):** basic_window, user_window, as_inferior, as_superior, as_inside, bare_window,
  with_border, with_label, with_two_labels, with_margin, as_relation, external, as_temporary_window,
  as_popup_window, sash, labeled_sash, two_labeled_sash.
  - Every window inherits basic_window. Every user-defined window class inherits as_inferior.
  - as_superior is needed to have sub-windows. as_inside manages the inside area (window minus border, label
    and margins). bare_window makes the object and allocates the bitmap area.
  - as_relation allocates sub-windows and is inherited by as_superior.
  - external carries user-process ⇄ window-manager-process communication.
  - Popup window = a temporary window that is not removed when the mouse exits.
  - sash = border + margins; labeled_sash adds a label; two_labeled_sash adds two labels.
- **Mixin, output control (8):** as_output, as_cursor, as_string_output, as_scroll, as_dot_scroll,
  with_mouse_scroll (mouse scroll by mouse movement and by button clicks), as_graphics, as_markers.
- **Mixin, input control (9):** as_input (keyboard), as_mouse_input, with_default_mouse (detects mouse movement
  and shows the cursor), with_translation_table (input code to the user's own code), with_superior_input_buffer
  (shares the superior's input buffer), with_mouse_scroll (again), with_window_region (mouse-sensitive area),
  with_line_selection (each line selectable like a menu item), as_notification (supports the "notify" output
  permission: a notify window appears when output is requested while unshown).
- **Mixin, menus and choice windows (8):** as_single_select, as_multiple_select, as_select, as_multiple_column,
  as_menu (every menu inherits it), as_on_off_menu (an on_off-type item is reversed when selected), as_submenu
  (each column of a multi_column menu is a submenu), as_choice (manages choice items).
- **Internal (8):**
  - window_manager: the window-manager process.
  - display: the bitmap display = screen + status_line.
  - screen: the logical screen.
  - status_line: bottom of display; shows system statuses, date, time, user name and selected window.
  - logical_mouse: a single_object.
  - window_message: user-process ⇄ window-manager IPC message.
  - single_object: limits the object count of a class.
  - window_manipulator: controls the manipulator menu.

Concrete nature lists printed anywhere:
| class | nature list | grade | cite |
|---|---|---|---|
| (TM-125 measurement window) | labeled_sash, as_scroll, as_output, as_graphics, as_markers, as_input, as_mouse_input, user_window | PRINTED | TM-125 p20 (folio 19), 1985 |
| bare_window | with_display, as_inside, * | PRINTED | TM-065 p15, TM-061 p8 (1984) |
| with_border | as_inside, * (slots border_x, border_y, border_area_width, border_area_height; border_flag := on, border_width := 2) | PRINTED | TM-065 p15 |
| with_label | as_inside, *, as_label | PRINTED | TM-065 p16 |
| window_with_border_and_label | bare_window, with_border, with_label | PRINTED | TM-065 p16 |
| my_window1 (WINCS) | with_margin, with_label, with_border, as_superior, as_input_buffer, inferior_window | PRINTED | WINCS p12 Fig 5 |
| my_window2 (WINCS) | with_margin, with_label, with_border, as_scroll, as_output, as_graphics, as_markers, as_input, as_mouse_input, inferior_window | PRINTED | WINCS p12 |
| my_window3 (WINCS) | with_margin, with_label, with_border, as_menu, as_single_select, as_mouse_input, inferior_window | PRINTED | WINCS p12 |
| my_window (WINCS) | as_output, as_graphics, inferior_window | PRINTED | WINCS p2 |
| my_window (TM-153 1986) | window | PRINTED | TM-153 p26 |
| escher (TM-153 screenshot) | as_program | SCREENSHOT | TM-153 p28 |

- **Version note (INFERENCE).** WINCS (late 1980s) uses `inferior_window` as the basic class where TM-125 (1985)
  has `user_window` or `labeled_sash`.
- **Class counts.** WINCS says SIMPOS provides "about 40 window classes" (PROSE, WINCS p3). TM-125 says "about
  120 classes" in the window system. TM-225 and TR-285 give 1,400 classes for all of SIMPOS.
- **Classes in WINCS but not in TM-125:** inferior_window, popup_window, temporary_window, as_input_buffer.
  All four are in the required-class partition.

### W2. Inheritance constraints (WINCS, from ICOT's 1987 manual 「SIMPOSプログラミング説明書(II)―入出力編―」, ref [12])
| constraint | grade | cite |
|---|---|---|
| Every window needs at least one basic class (the source says one of the three is indispensable; exclusivity not stated): inferior_window, popup_window or temporary_window (WINCS menu: 階層 / テンポラリ / ポップアップ) | PROSE | WINCS p7, p8 |
| as_menu requires as_mouse_input (the converse does not hold) | PROSE | p3, p8 |
| as_single_select requires as_menu | PROSE | p9-10 |
| as_menu cannot be combined with as_graphics | PROSE | p3 |
| as_menu cannot be combined with as_output in one window. WINCS's fix is to add as_superior and split into children (parent gets as_input_buffer, Fig 5) | PROSE/PRINTED | p7-10, p12 |
| Order: with_label before inferior_window; with_label before as_output; as_output before inferior_window | PROSE/PRINTED fact form | p3, p11 |
| WINCS-emitted order (INFERENCE that this mirrors the manual): with_margin, with_label, with_border, [as_superior, as_input_buffer / as_scroll, as_output, as_graphics, as_markers, as_input, as_mouse_input / as_menu, as_single_select, as_mouse_input], basic class last | PRINTED | p12 |

### W3. Window states and per-state I/O (all variants; do not harmonise)
| source (year) | states | I/O rule |
|---|---|---|
| TR-046 Table 2 (1984), PDF p23, eyed | SELECTED: kbd done, mouse done, out done. SHOWN: kbd waiting, mouse done, out done. EXPOSED: input waiting, out done. OVERLAPPED: input waiting, out "waiting/done". DEACTIVATED: not available | PRINTED-INTERFACE |
| TR-057 Table 3-1 (1984), PDF p6 | Selected done/done/done; Shown wait/done/done; Exposed wait/wait/**wait**; **Deexposed** wait/wait/wait; Deactivated fail/fail/fail. The text names "overlapped" but the table row says Deexposed. | PRINTED-INTERFACE |
| TR-046 / TR-057 definitions | selected = connected to the keyboard (only one). shown = completely displayed on screen, and its superior is shown; mouse clicks are interpreted by its own key table. exposed = completely displayed on its superior but the superior is not shown. overlapped = partly or fully hidden by a sibling. deactivated = not managed, dot image kept in bitmap memory | PROSE (TR-046 p9-10, TR-057 p6) |
| TR-046 Fig 1 (PDF p25), eyed | A selected; B shown; B1 shown; B2 overlapped; C overlapped; C1 exposed (child of an overlapped parent); C2 overlapped | PRINTED (figure) |
| TR-055 (1984) PDF p18-19 (folio 15-16) | shown (one of them selected; only the selected window gets keyboard), de-exposed (partially or fully covered; no input, output "with certain restrictions"), de-activated | PROSE |
| TM-125 (1985) p5-6 | two orthogonal pairs. **exposed/deexposed** is a status among siblings of one superior. **shown/unshown**: shown iff the window and all its ancestors are exposed. Output is governed by the per-window **output permission**: WAIT, NOTIFY, OUTPUT, SHOW (W4) | PROSE |
| TM-126 (1985) p7 | per window "fully visible or not". A fully visible window is the default selection target. The selected window's text cursor blinks and its name is shown on the bottom line. Mouse clicks go to the fully visible window under the mouse cursor | PROSE (TRANSLATION) |
| TM-225 (1986, SIMPOS 2.5) p11 | selected window = the window that has the keyboard-input function and is top of the stacking order; changed by the user's mouse. Mouse input goes to the window under the mouse marker (マウスマーカ) | PROSE (TRANSLATION) |

### W4. Output permission / hidden-window output (all variants)
- **TM-125 p6 (1985):** WAIT, NOTIFY, OUTPUT, SHOW, chosen per window. (PROSE)
  - WAIT: wait until fully shown.
  - NOTIFY: the system's NOTIFY WINDOW tells the user that the window wants to output; requires the
    as_notification mixin.
  - OUTPUT: write immediately into the window's saved bitmap; only the shown part appears.
  - SHOW: force the window shown, then output. This changes the selected window.
  - The authors recommend WAIT and NOTIFY.
- **TM-125 p7 Fig 4 (1985):** the ATTRIBUTE choice window shows PERMISSION with the alternatives
  "out(put?) / wait / show / notify", with wait highlighted (current). (SCREENSHOT)
- **TM-225 p10-11 (1986):** four options. (PROSE, TRANSLATION)
  - ① The requesting process waits until the window is unhidden. **This is the default.**
  - ② Write to the save area; the unhidden part shows on screen.
  - ③ Force unhidden, then output.
  - ④ A temporary notify window appears, and the user picks ① or ③ by mouse.
  - Use: hiding a tool's window stops the tool at its first output.
- **Implementation (TM-225 p10; TM-126 p5):**
  - A shown window draws into frame memory. A hidden window's image lives in a per-window **save area** in the
    display's bitmap memory, which is "several to several tens of times" the frame memory.
  - Restacking copies between save areas and frame memory.
  - Redisplay keeps a rectangle decomposition of the screen, recording which windows cover each rectangle
    (TM-126 Fig 2).
  - Grade: PROSE.

### W5. Methods (TM-125 ch.5, PDF p13-18 and p22; 1985). Signatures and meanings are in the TSV.
The report never says which class defines each method, so every class attribution in the TSV is INFERENCE.

Arity counts the receiver:
- **Create:** create/2 (Class,^W); create/3 (Class, Initiation, ^W).
- **Setters:** set_size/3, set_position/3, set_superior/2.
- **Menu items:**
  - add_item/3 (Menu, Item, Position 0..n);
  - add_item/4 (Menu, Item, Column, Position);
  - delete_item/2 (Menu, Item_string).
- **Border, label, margins:**
  - set_border_width/2 (default 2 dots);
  - set_label_position/2 (atom top or bottom);
  - set_title/2, set_top_title/2, set_bottom_title/2;
  - set_margins/5 (Left, Right, Head, Tail, in dots).
- **Lifecycle:** activate/1, show/1, deactivate/1 (image kept), hide/1.
- **Text output:**
  - write/2 (Character), insert/2, delete/2 (cursor not moved);
  - move_cursor/3, clear_line/1;
  - scroll/2 (+ = up);
  - open_rows/3, move_rows/4.
- **Graphics:**
  - get_point_value/4, set_point_value/4 (pixel 0/1);
  - draw_line/5 and /8 (Line_width default 1, Line_type default "fixed line", Alu default exclusive-or);
  - draw_rectangle/5 and /8;
  - draw_string/4 and /5 (X,Y = top-left of the first letter).
- **Markers:** create_marker/2, draw_marker/2, erase_marker/2, move_marker/4, set_marker_type/3 (box or line),
  set_marker_size/4, get_marker_list/2.
- **Input:** read/2, read_sense/2.
- **Kill:** kill/1. Windows are registered to the creating process and killed with it.
- **Select:** select/1 (PROSE, p22).

Additions from other sources:
- `:draw_circle(W,X,Y,R,1,solid,set)` = draw_circle/7. This gives value atoms for Line_type (`solid`) and
  Alu (`set`). PRINTED, WINCS p3.
- `class_method(as_graphics, draw_line, [5, object, x1,y1,x2,y2])` (the 5 counts the receiver). PRINTED,
  WINCS p12.
- :putc/2 is the character-output method shared by windows, files and counters. PROSE, TR-285 p11 (1987).
- TM-153 p26 (1986) uses :write_lines/2 and :write/2 with `key#lf` and `key#cr`. PRINTED (existing listing).

### W6. Creation options
- **Table 1 verbatim** (TM-125 PDF p14, folio 13). PRINTED-INTERFACE.
  - Columns: Initiation | Remarks | Default Value.
  - Rows:

    | Initiation | Remarks | Default Value |
    |---|---|---|
    | superior(Superior) | the superior window | screen |
    | position(X,Y) | window position in the superior window | (0,0) |
    | size(Width,Height) | window size | inside size of superior window |
    | title(String) | the label title | blank |
    | top_title(String) | the top_label title | blank |
    | bottom_title(String) | the bottom_label title | blank |
    | margins(Left,Right,Head,TAil) | the margins | 1 dot |
    | units(Width,Height) | the inside units (the grid size in the window) | 1 dot |

  - The full table, as printed, is already in listings/tm0125_p13.esp.
- **Menu and choice-window additions:**
  - menu: `items_list([{item_string,item_type,item_id,documentation},...])`;
  - choice window: `choice_list([{item_string,item_type,elements_list,initial_element,documentation},...])`.
  - documentation is shown on the status line. PRINTED-INTERFACE, p14-15.
- **Container syntax varies:**
  - Prolog list `[...]` in TM-125 p14 and in the TM-153 p28 screenshot;
  - vector `{...}` in the TM-153 p26 listing and the TM-181 p4 screenshot.
- **Later options seen in screenshots:** `font(Font)`, `label_font(Font)`, `title("漢字ウインド…")`. SCREENSHOT,
  TM-181 p4, 1986.
- **ATTRIBUTE choice window** (TM-125 Fig 4, SCREENSHOT, 1985). It shows the attribute set the window manipulator
  edits:
  - SIZE(WIDTH), SIZE(HEIGHT), POSITION(X), POSITION(Y), MOUSE_MARKER, LABEL, NAME;
  - MARGIN(LEFT|RIGHT|HEAD|TAIL) = 1, BORDER = 2;
  - PERMISSION (out / wait / show / notify);
  - FONT and LABEL_FONT (an illegible default / ank_24 / kanji_24);
  - LABEL_POSITION (top / bottom), BACKGROUND (white / black);
  - buttons do_it and abort.
  - Example values: 1000 × 500 at (200,200).
  - **LABEL and NAME are separate attributes.**
  - Weak reads in Fig 4: the highlighted values (wait, top, white) are inferred by elimination from low-resolution inverse boxes, and the window name KOEBUG is uncertain. Treat these as «?».

### W7. Input codes and event formats
- **:read/2 result kinds** (TM-125 p18, PRINTED-INTERFACE):
  1. Keyboard: a character code. Codes are 16-bit, based on JIS kanji code (TR-061 p6; TM-125 p6).
  2. Mouse: `mouse$r`, `mouse$m`, `mouse$l` (single clicks) and `mouse$rr` (right double click). In 1984 and in
     held code these are `mouse#l` and `mouse#rr`; see W0.
  3. with_translation_table: the translated code.
  4. with_mouse_scroll: `scroll_request(Offset)`.
  5. Menu: the selected item's item_id. A temporary menu returns `abort` if the mouse exits.
  - read_sense/2 returns `$$nil` when no input is pending.
- **Key codes printed (1984):**
  - `control#"k"`, `"l"`, `"a"`, `"s"`, `"m"`, `"b"`, `"v"`, `"r"`, `"w"`; `mouse#l`, `mouse#rr` (TR-046/TR-061 translation table);
  - `key#lf`, `key#cr` (TM-153 p26).
- **Mouse device** (TR-046 p14, PROSE):
  - reports relative motion;
  - the window manager tracks position and the "mouse_owning window", and draws that window's mouse-cursor
    pattern, which each process may define;
  - click meaning comes from the process's translation table;
  - clicks go only to shown windows, and a default meaning applies outside them.
- **Selection by mouse** (TM-125 p22): clicking the **left** button on a partly or fully shown window selects it.
  Fully hidden windows are reached via the manipulator's MENU item.
- **Click information:** no event format beyond the single and double click codes is described in any of
  these reports. `with_click_information` is NOT mentioned. NEGATIVE.

### W8. Translation table and Coordinator window side (1984)
- **Translation table** (TR-046 p13-15; TR-061 p6-9):
  - It is a class instance in a slot of `e_window`.
  - `default_translation_table` is the standard; user tables inherit it and override keys.
  - Interface: `:look_up(Table, Window, KeyCode, Destination, Command, HelpString)` = look_up/6. The help string
    is used by HELP. The table runs inside the window manager.
  - The full printed table (13 clauses) is in the existing listings TR-046_p28.esp and TR-061_p13.esp.
  - Commands are sent to `#coordinator` as `{Cmd, E_process, Arg3, Arg4}`. Cmd is one of kill, lull, arouse,
    status, visit, memorize, broadcast, remember, invoke_system_menu, read, write.
  - Default: pass the character through ("send character as it is"). PRINTED.
- **How a program gets a window:**
  - **Coordinator path (1984).** An expert is created from an e_program; "The e_window and the e_port are also
    created automatically" (TR-061 p7). The expert talks through its e_window. PROSE.
  - **Direct path (1985-86).** The program creates a window itself: `:create(#window, Options, W)` then
    `:activate(W)` (TM-125 p19, TM-153 p26/p28). The program's class has `nature as_program` with `:goal/1` as
    the entry point (TM-153 p28 screenshot). PRINTED / SCREENSHOT.
  - Since 1986, programs may also use `#standard_io_window` (TM-181 p4 screenshot, existing listing).
- **System menu:**
  - It is a `#multi_column_menu` built by class `system_menu` from the expert directory (Experts column) plus
    invariant MEDIA SYSTEMS items `'window'` and `'file'` created with `:create(#menu_item, 'window', common,
    window, _, Item)` = create/6 (TR-046 p27 Fig 3, PRINTED).
  - It is invoked by `mouse#rr` or `control#"s"`.
  - The SIMPOS 2.19 screenshot (TM-181 p3) shows two columns:
    - Experts: debugger, pmacs, librarian, file_manipulator, spooler, font_editor, edips;
    - MEDIA SYSTEMS: user process list, window manipulator, network, shell, whiteboard, kanakan initiate,
      garbage collection, login, shut down.

### W9. Window manipulator (system-level window operations)
- **Menu (TM-125 p8, 1985), invoked from the system menu.** PRINTED-INTERFACE.
  1. SHOW: show the whole of a partly shown window.
  2. HIDE: move a partly shown window to the bottom of the window list.
  3. RESHAPE: point to the top-left and bottom-right corners with the mouse.
  4. MOVE: by mouse.
  5. EXPAND: as large as possible without hiding a fully shown window.
  6. MENU: select a window from a submenu listing the windows.
  7. PERMISSION: output permission, via a submenu.
  8. ATTRIBUTE: via the choice window (Fig 4, W6).
  9. HARDCOPY.
  10. SUPERIOR: move the "editing base" to the superior window.
  11. INFERIOR: move it to an inferior window.
  12. EXIT.
- **Other sources:**
  - TM-126 p5 names MOVE, RESHAPE, SHOW and HIDE.
  - TR-046 p9 (1984) names the operations move_window, select_window and reshape_window.
  - TM-225 p9 (1986) describes the manipulator as changing position, size and similar attributes interactively
    by mouse **and keyboard**.
  - TM-125 p8 has no item named KILL, BURY or EXPOSE. NEGATIVE.

### W10. Fonts
- **1985 (TM-125 PDF p24, folio 23):** only two fonts were released, "Alpha-numeric font and kanji font". A prototype font
  editor exists. Multi-font is supported but hard to use within one window; variable pitch is planned. PROSE.
- **Default character cell 13 × 19 dots** ("13 dots wide, and 19 dots hight"). PRINTED, TM-125 p20.
- **Font names `ank_24` and `kanji_24`** are visible in the 1985 ATTRIBUTE choice window, as alternatives for
  FONT and LABEL_FONT. The highlighted current font name is illegible. SCREENSHOT, TM-125 p7.
- **Font object creation (1986):** `:create(#font, "font:ascii_16…", F)` and `"font:kanji_2…"`, the strings
  truncated in the photo. This suggests font file paths of the form `font:<name>`, i.e. a `font:` logical
  directory or device prefix (INFERENCE). SCREENSHOT, TM-181 p4 (existing listing).
- **TM-225 p8 (1986):** every window may use different fonts including kanji. The font editor is a
  mouse-oriented interactive editor. PROSE.
- No font file format or font size table is in these reports. NEGATIVE.

### W11. Screen geometry and hardware
| fact | grade | cite |
|---|---|---|
| Display 1280 × 864 pixels; keyboard, pointing device, 8" floppy, Winchester disk | PROSE | TM-224 p11 (folio 10), Aug 1986 |
| "1200 x 912 (or 1280 x 864)" black and white bitmapped display | PROSE (OCR, tr0046/p-06.txt line 12) | TR-046 PDF p6 (1984) |
| "モノクロ 1200*900 ドット" | PRINTED (handwritten figure) | TM-153 p23 (Jan 1986) |
| Keyboard and mouse hang off the **console processor** (console bus). The bitmap display, disks, FDD, tape, laser printer and LAN are on the Multibus (IEEE-796) | PRINTED (figure) | TM-153 p23 |
| Character cells at 13×19: 1280/13 ≈ 98 columns, 864/19 ≈ 45 rows (≈ 92 × 48 at 1200 × 912) | INFERENCE | — |
| Status line at the bottom of the display (part of `display` = screen + status_line) | PROSE | TM-125 PDF p13 (folio 12) |
| Coordinates: position(X,Y) relative to the superior; draw_string anchor at the top-left of the first letter; units(Width,Height) grid default 1 dot | PRINTED-INTERFACE | TM-125 p14, p17 |

### W12. Label, border, margin drawing and screen look
- **Fig 5 (TM-125 PDF p10, folio 9), PRINTED (figure):**
  - the label is a strip along the top inside the border, with text left-aligned ("This is Label");
  - the margin lies between the border and the inside;
  - the border default is 2 dots and the margins default to 1 dot.
- **Refresh order (TM-065 p15-16, 1984):** `bare_window:refresh` clears the area; then `after :refresh` demons in
  with_border and with_label redraw the border (4 lines) and the label. PRINTED.
- **Screenshots, label placement.**
  - Most labels are **black inverse-video bars with white text, left-aligned at the top-left** of the window.
    Seen in TM-125 Fig 2/6 (`editor_2`, `debugger_2`), WINCS (`tms window`, `menu/6`, `my_window`) and TM-153
    (`English-Japanese`, `network`).
  - Some labels sit at the **bottom**. The 1986 editor window `editor_1` has its label under the ARG> pane
    (TM-153 p28). In TM-125 Fig 4 the label `debugger_1` appears at both the top and the bottom edge
    (with_two_labels? INFERENCE).
- **Default window naming (SCREENSHOT, INFERENCE as to rule):**
  - instance names look like `<program>_<n>`: `editor_1`, `debugger_2`, `librarian_1`, `file_manipulator_1`;
  - a menu is labelled `menu/6` (WINCS). The TM-125 Fig 4 status-line text read as `[…_choice_menu/4]` is «?» (illegible halftone) and does not support the rule;
  - the selected-window field shows class-like names such as `[debugger_choice_menu_without_label]`
    (TM-125 Fig 6; TM-126 Fig 4).
- **Status line (SCREENSHOT):** two inverse rows at the bottom.
  - Row 1 left: "USER : <name>". Row 2 left: "SIMPOS Version 1.00" (1985) or "2.«?»0" (1986, TM-153 p28; reads 2.00 at 300dpi but noisy).
  - TM-125 Fig 2 (PDF p4) shows the middle field holding the selected window's label text `[EDIPS(string)[46,27] escher.esp]`, i.e. the field displays the selected window's name/label (INFERENCE).
  - Middle: "[selected window name]" in a box.
  - Right: date, weekday and time, e.g. "17-Jul-85 Wednesday 15:39:48".
  - 1986 adds "SWAPPED" and "spool" indicator boxes (TM-153 p28).
  - The documentation strings of menu items are shown on the status line (TM-125 p14, PROSE).
- **Background, cursors, scroll bar (SCREENSHOT):**
  - The screen background is a grey stipple (all photos).
  - The text cursor is a solid black block (WINCS p5).
  - The mouse cursor is an arrow, or a small x over a menu (WINCS p5-6).
  - A scroll bar appears as a vertical line inside the window (WINCS p11 + PROSE).
- **Menus (SCREENSHOT):**
  - multi-column menus can have column titles, e.g. "network": TOOLS / MANIPULATOR / DEMO (TM-153 p28);
  - choice windows show the current alternative in reverse video (TM-125 p7).

### W13. Temporary, popup, menu and choice windows
- **Temporary window (TM-125 p6-7):**
  - appears at the mouse cursor and disappears when the cursor leaves;
  - is never hidden by ordinary windows;
  - is taken off the screen (not hidden) when no longer needed;
  - saves the screen image it covers. PROSE.
- **Popup window:** a temporary window that stays when the mouse exits (TM-125 PDF p11, folio 10).
- **Menu window** (TM-125 p7; TR-046 p14):
  - mouse input only: no keyboard input and no output;
  - appears at the mouse position;
  - sized by item count and the longest item string;
  - the window system builds the bitmap. PROSE.
- **Temporary menu** (TR-055 PDF p20, folio 17): shown on a click of a specific mouse button; the selection is input to the
  process; leaving the menu cancels it. PROSE.
- **Choice window:** see W6.

### W14. Icons, bell, click information
- **Icons:**
  - WINCS's 1989 attribute menu has 「アイコンを表示する」 [show an icon] under parent-window classes
    (SCREENSHOT, WINCS p5), so an icon mixin existed by PSI II (presumably `with_icon`, INFERENCE).
  - TR-046 p12 (1984) says iconic input was "deliberately rejected". PROSE.
  - Icon behaviour is not described in any of the in-scope reports.
- **Bell, click information:** not found. NEGATIVE.

---------------------------------------------------------------------------------------------------
## LIBRARIAN / SHELL / OTHER (incidental, from these pages only)
- TM-125 Fig 2 (1985): a librarian-like dialog prompts "Input Class Name.", "Input Source File Name." and answers
  "Registrating..." / "Registrated." Its menu tails include …eck, …pile, …ve, …ad, …ete, …int, …fo,
  …sses, …icates. Existing listing tm0125_p04.txt. SCREENSHOT.
- TM-125 Fig 4: a debugger_1 interaction shows `:- :makew(#top|v1).`«?» (low-res read) → `> Success !!`; `> Fail !!`.
  The top-level answer format is "Success !!" / "Fail !!". SCREENSHOT.
- File pathname with node: `@@psi000::>sys>user>wincs>wincs>finished.esp.5`. PRINTED, WINCS p12.
- System menu items "shell" and "login": W8 (TM-181 p3).
- TM-225 p6: `:create(#process,P)`, `:activate(P,Program)`, `:terminate(P)` (existing listing).

---------------------------------------------------------------------------------------------------
## POSSIBLE SIMPOS CODE
- **TR-046 Fig 2/4 and TR-061 Fig 2: `default_translation_table` (1984).** These are presented as the system
  standard table ("the ESP program for the system standard table", TR-061 p9). They are the closest to actual
  SIMPOS source in scope. Existing listings; not new.
- **TR-046 Fig 3: `system_menu` class (1984), abridged.** Existing listing.
- **TM-065 p15-16 / TM-061 p8: `bare_window`, `with_border`, `with_label`, `window_with_border_and_label`.**
  Described as illustrations of SIMPOS constructs, with bodies elided. Existing listings.
- Nothing new found in this pass is SIMPOS source. The WINCS listings are **generated application classes**;
  only their nature combinations reflect SIMPOS. No binaries.

## CHECKED, NOTHING (for window topics)
- TM-126 p2 (intro), p4 (design philosophy), p8 (conclusion): no technical window facts beyond W3 and W4.
- TM-125 p1 (cover), p24-25 (future plans and references; future plans summarised in the structure file).
- TR-046 PDF 22 Table 1 and PDF 24 Table 3: design criteria only (the one window row is in TR-046_p23_p25.txt).
- TR-055 p21-22 (network, conclusions).
- TM-224: everything except p11 is CPU, KL0 and memory architecture. Contact sheet of all 16 pages.
- TM-153: handwritten Japanese text pages p2-p22 (OCR unusable; contact sheet only).
- TR-285 p4, p12, p14: general statements only (window system benefited from multiple inheritance; first pilot
  took seconds per character in summer 1984).
- In-scope OCR grep for icon, click, font, bell and cursor (in Latin script and katakana): no icon, bell, font-file or
  click-information content beyond what is cited above.

## PAGES READ
- **Eyed in this pass:**
  - TM-125 PDF p2-25, all pages (p7 Fig 4 at 500dpi; p18 glyph at 600dpi; p4 at 90dpi plus the existing 300dpi listing). p1 is the cover.
  - TM-126 p2-8, all pages (p3 and p6 at about 90dpi plus the existing 300dpi listings).
  - TR-046 PDF 22-25.
  - TM-153 p23 (150dpi), p28 (300dpi); contact sheet of all pages.
  - TM-225 p8-12 (130dpi).
  - TM-224 p11 (150dpi); contact sheet of all pages.
  - WINCS p2 (part), p3 (top), p5, p6 (top), p11 (top and bottom), p12, p13 (top), all at 200dpi.
- **OCR only:**
  - TR-046 p9-16 (prose);
  - TR-061 p7-10;
  - TR-055 PDF p18-23;
  - TR-057 p6;
  - TR-285 p4, p11, p12, p14;
  - WINCS p1-17 text.
- **Not re-read (relied on existing listings):** TM-065 p11-16, TM-061 p8-9, TM-181 p3-4, TR-061 p12-13,
  TR-046 p26-28.

## OPEN QUESTIONS
1. **Where are `mouse$` / `mouse#` and `$$nil` defined?** Is the TM-125 '$' a typesetting substitution? Held code
   uses `#`. Need a 1985 code listing.
2. **What are the 1987 manual's (ref [12], 「SIMPOSプログラミング説明書(II)―入出力編―」) exact class names?** In
   particular the classes behind 「プロセス間共有」, 「子ウインドウのサイズを設定」 and 「アイコンを表示する」.
   with_shared_window, with_pane and with_icon are in the required list but unconfirmed. Is the manual held
   anywhere?
3. **Do Line_type and Alu have other values?** Only `solid` and `set` are printed (WINCS). TM-125 gives the
   defaults "fixed line" and "exclusive or" without atom names.
4. **What is the highlighted default font name in TM-125 Fig 4?** It is illegible. Is the ank_24/kanji_24 naming
   related to the 1986 "font:ascii_16" / "font:kanji_2…" strings?
5. **What is the display resolution?** 1280×864 (TM-224) vs 1200×900 (TM-153) vs 1200×912 (TR-046). The PSI
   versus PSI II difference is unknown.
6. **How do statuses and permissions map onto the later classes?** The held programs use the
   expose/deexpose/select notifiers (`deexpose_notifier`, `select_notifier`, `reshape_notifier` are in the
   required list); none appear in these reports.
7. **Window naming:** is `menu/6` / `…_choice_menu/4` the default title rule `<class>/<n>` for unnamed windows,
   and `editor_1` the Coordinator's expert-name rule?
8. **How do the 1984 Coordinator e_window and the 1985+ direct `:create(#window…)` path coexist?** And does
   `as_program` (TM-153) replace e_program?
