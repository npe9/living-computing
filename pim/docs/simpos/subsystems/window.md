# The SIMPOS window system: a specification for stand-ins (2026-11-24)

SIMPOS's window system is lost. No class body survives. This page puts together everything the held reports, papers,
video, IFS application sources and compiled packages say about it. It is written so that someone can build
stand-in classes that look right on screen and behave the way the held programs need. Where the evidence runs out,
the page says so, and anything filled in by interpolation is graded INFERENCE.

The window system covers windows, menus, choice windows, fonts and bitmaps, mouse and keyboard input, the
standard-I/O text protocol, the Pmacs editor seen as a window component, the window manipulator, and the screen
chrome. The Librarian and the shell/system menu have their own pages (`librarian.md`, `shell.md`). This page covers
them only where they put up windows.

## 0. Scope, conventions, sources

### 0.1 Conventions

- **Arity counts the receiver**, as `required/` does: `:create(#window,Opts,W)` is `create/3` and `:kill(W)` is
  `kill/1`. `printed/classes.tsv` does not count the receiver, so add 1 to its arities. TM-125's own reference also
  omits the receiver, so its ":create/1 and /2" are create/2 and create/3 here.
- **Class method or instance method.** A class method is marked `c:`. It is sent to the class object `#name`.
- **Grades:**

  | grade | meaning |
  |---|---|
  | PRINTED | an ESP body was printed in a report |
  | PRINTED-INTERFACE | a signature, table or menu was printed, with no body |
  | PROSE | the source describes it in words |
  | SCREENSHOT | seen on a screen image or in the video |
  | USAGE | seen in held application source or in compiled packages |
  | COPY | the code is itself a copy of SIMPOS code |
  | INFERENCE | mine |

  TRANSLATION marks a Japanese source rendered in English.
- **Citations.**

  | source | form | example |
  |---|---|---|
  | report | PDF page index, with the folio in brackets when the notes give it | "TM-125 p14 [13]" |
  | IPSJ paper | record id and page | "IPSJ 36239 p5" |
  | journal | name and page | "Giho 8609 p20"; "WINCS p12" = JSSST Computer Software 8(1) 1991 |
  | video | segment@seconds | "simpos.wmv@117" |
  | IFS source | archive-relative path:line | "cal-esp/cal2.12/scawin.esp:213" |
  | compiled package | package, class, predicate, then "(ptf)" | "pimfep.ptf pimfep##pimos_fep_superviser create_window/1 (ptf)" |

  "(notes: X §n)" points to the reader's notes, committed under `subsystems/notes/`.
- **Status letters** (from `coverage_window.tsv`, see §8):

  | letter | status | meaning |
  |---|---|---|
  | D | DOC-class | documented on that class |
  | d | DOC-unowned | documented, owner class not stated |
  | U | USAGE | meaning only from use, same class |
  | u | USAGE-unowned | meaning only from use, other class |
  | N | NONE | no evidence |

- **Quotes.** Quotations from papers are kept under 15 words. IFS code is described rather than transcribed.
  Listings from ICOT TR/TM reports are transcribed; most are already in `printed/listings/`.

### 0.2 Versions

| tag | date | what it is |
|---|---|---|
| 1984 design | 1984 | TR-046, TR-055, TR-057, TR-061, TM-061, TM-065. Pre-release |
| 1.0 | 1985 | TM-112, TM-115, TM-125, TM-126, TM-134. The status line reads "SIMPOS Version 1.00" (TM-115 p25; TM-134 p68) |
| 1.5 | autumn 1985 | TM-143 (1.x system menu) |
| 2.0 / 2.10 | spring 1986 | Giho 8609, TM-153 ("SIMPOS Version 2.00", TM-153 p28), TM-181 |
| 2.50 | Sept 1986 | IPSJ 36239, TM-225, Giho 8609 Fig. 8. The museum video shows "2.50" (melco.wmv@50) |
| A00 | ? | a version string seen only in the video (esp.wmv@108). Unplaced. Compare Mitsubishi's "SIMPOS II B00" (Giho 8907 p34), which is product numbering |
| 3.0 | end 1986 | planned, with "unified UI": every character-I/O window becomes a Pmacs window (IPSJ 114007 §6; IPSJ 36239 p8) |
| 4.2 | Sept 1989 | FSTJ 26(1) p99 status line |
| PSI-II | 1989 | WINCS (JSSST 1991, received 1989-07). About 40 window classes, inferior_window as the base |
| 5.0 | 1989 | TM-785 and TM-786 |
| held programs | 3.0-7.1 / A22 | IFS sources dated 1986-92 ("held 3.x-7.x"). Compiled packages stamped 1991-94 ("ptf 1991"-"ptf 1994"), library format `lib50` (notes: ptf.md §0) |

**Rule.** Where sources conflict, this spec follows the held programs, and the older form is listed as a VARIANT
with its version. The main variants are collected in Appendix B.

### 0.3 Sources, by weight

| weight | source | what it gives | notes |
|---|---|---|---|
| 1 | compiled packages (11 .ptf + 10 papyrus .pak.1, 1991-94), run under kl0 with SIMPOS sends stubbed | exact create attribute lists, menu and choice item vectors, mouse dispatch, demons that prove a SIMPOS primary exists | ptf.md |
| 1 | IFS application sources (15 programs; 334 window classes, 1771 creates) | the whole protocol as used: natures, options, items, events, keycodes, Pmacs bindings | ifs_window.md, ifs_libshell.md |
| 2 | TM-125 (1985) ch. 4-5 | the only printed method reference (about 45 signatures), Table 1 options, item vectors, read codes, the 69-name class catalogue, manipulator menu | trtm_window.md; `printed/listings/tm0125_p13.esp`, `tm0125_p08*.txt` |
| 2 | WINCS (1991, from ICOT's 1987 「SIMPOSプログラミング説明書(II) 入出力編」) | base classes, mixin order and combination constraints, generated recipes | trtm_window.md W2; ipsj.md WINCS |
| 2 | TR-046 / TR-061 (1984) | the Coordinator translation table (PRINTED ESP), window states | `printed/listings/TR-046_p28.esp`, `TR-061_p13.esp` |
| 3 | TM-115 / TM-112 (1985) | font format, manager/user method split, the status line, mouse gestures | tm115.md |
| 3 | IPSJ 36239, 114007, 114008, 114012 (1986); Giho 8609, 8907, 9106; FSTJ 26(1) | screenshots of menus, status line, Pmacs mode line, window slots; colour windows | ipsj.md |
| 3 | TM-785 / TM-786 (1989, SIMPOS 5.0) | `draw_*` argument vectors, colour pairs, dialogue look | trtm_manuals.md; `printed/listings/TM-785_p40.esp` |
| 4 | museum video (2.50 / A00) | system menu, window menu, editor and librarian screens | video.md |
| 4 | IPSJ 122601 (1992) | which SIMPOS classes an ESP-to-CESP port had to re-create, and the ESP-to-CESP method table | newipsj.md (supersedes the `web_search_2026-11-24.md` items 1-2) |
| — | IPSJ 118569 (CESP window library, 1990) | names CESP classes only. It says the CESP spec is "based on" SIMPOS's, but its Fig. 2 is **not** a SIMPOS class list | newipsj.md, correction 1 |
| 4 | linguist (CESP, 1991): its manual names its `with_margin`, `as_markers` and `as_outputs` as substitutes for SIMPOS's classes | argument forms of `create_marker/7` and `get_margins/5`; the marker types. CESP substitute, an analogy only | sweep_2026-11-24.md §2.2 |
| 4 | the 1990 ESP manual (`ESPtex/program-e.tex`); CAL's debugger manual (1992) | a `standard_io_buffer` example; the programming manual has a standard-I/O section on holophrasting (print depth/length, G7) | sweep_2026-11-24.md §2.3-2.4 |

**How far the kl0 runs can be trusted.** The "(kl0 run)" facts come from the ptf reader's harness
(`tools/ptf_stubrun.py`). It uses `../../../psi/kl0.py` read-only, stubs every SIMPOS send, and adds
five opcode handlers that kl0 lacks:
- `pmi b4`, `pmi b7` and `blt 40` are witnessed against paragraph source.
- `pmi b5` and `pmi b6` (taken as put_vector_5/6) are INFERENCE from the opcode series.

So a 5- or 6-element vector recovered by a run is INFERENCE in its *shape* unless held source shows
the same shape. One example is the choice item `{Label,string,Name,Width,Default,_}`. Choice items
are also seen in held source (§3), and there they are USAGE.

**Missing.** No SIMPOS window-system source or binary is held: no `simpos##` class is defined in any of the 1,662
compiled templates (notes: ptf.md "POSSIBLE SIMPOS CODE"). The nearest material is:
- printed mixin bodies from 1984: `bare_window`, `with_border`, `with_label` (TM-065 p15-16);
- the 1984 `default_translation_table` (TR-046 p28);
- cil's COPY of `library_utility`, which creates windows (notes: ifs_libshell.md §4.1.1).

---

## 1. Class hierarchy

### 1.1 The three kinds of class

TM-125 sorts its "about 120 classes" into three kinds (TM-125 p8-13 [7-12], PROSE, 1.0):
- **stand-alone**: usable by itself;
- **mixin**: supplies a function and is meant to be used as a superclass;
- **internal**: used by the window system, not by users.

WINCS gives a different count, "about 40 window classes" (WINCS p3, PROSE, PSI-II). All of SIMPOS had about 1,380
classes in 2.50 (IPSJ 36239 p1).

A user window is a class whose `nature` list combines mixins and ends with a **base class**:

```
class my_window has nature with_margin, with_label, with_border,
                           as_scroll, as_output, as_graphics, as_markers,
                           as_input, as_mouse_input, inferior_window; end.
```

This is WINCS Fig. 5 `my_window2` (WINCS p12, PRINTED, generated code).

### 1.2 Base classes (one is required)

| base | meaning | grade, cite | version |
|---|---|---|---|
| `inferior_window` | ordinary window inside a superior. Called 階層ウィンドウ ("hierarchical window") in WINCS | PROSE WINCS p5, p7-8. Last nature in 110 of 132 held uses (USAGE, notes: ifs_window.md §1) | PSI-II; held |
| `temporary_window` | appears at the mouse; removed (not hidden) when no longer needed; never hidden by ordinary windows; saves and restores the screen under it. A temporary menu disappears when the mouse leaves it (TM-125 p6-7) | PROSE TM-125 p6-7; WINCS p5 | 1.0; held (last in 11/11) |
| `popup_window` | a temporary window that stays when the mouse leaves | PROSE TM-125 p11 [10]; WINCS p5 | 1.0; PSI-II |
| `user_window` | the 1985 basic window class ("a basic window class", TM-115 p40). Every user-defined class inherits `as_inferior` (TM-125 p8) | PROSE TM-115 p40; USAGE `kappa##window` (kappa2/kappa2/utility/fmp/UTL_WIND.ESP:6) | 1.0; still present in kappa (1992) |
| `screen` | the logical screen. It is the default superior (TM-125 Table 1). sum uses it as a nature (sum/src/title_win.v32:11) | PROSE TM-125 p13; USAGE | all |

WINCS says one of `inferior_window`, `popup_window`, `temporary_window` is indispensable (WINCS p7-8, PROSE). It does
not say they are exclusive. `user_window` (1.0) plays the same role as `inferior_window` (PSI-II): WINCS uses
`inferior_window` where TM-125 has `user_window` (INFERENCE that it is a rename). Both survive in held code.

Partition note: `user_window` is in `partition_shell.tsv`, not the window partition. The ifs_window notes say it is
in no partition, which is wrong.

### 1.3 Mixins

**Placement.** Mixins are written first and the base class last (WINCS p11-12, PRINTED fact form; held programs
agree: notes: ifs_window.md §1). The order WINCS emits is:
1. sash mixins (`with_margin`, `with_label`, `with_border`);
2. structure (`as_superior`, `as_input_buffer`);
3. output (`as_scroll`, `as_output`, `as_graphics`, `as_markers`);
4. input (`as_input`, `as_mouse_input`), or the menu group (`as_menu`, `as_single_select`, `as_mouse_input`);
5. the base class.

That this order mirrors ICOT's manual is INFERENCE.

**Grades for the table below.** Roles come from TM-125 p8-13 (PROSE, 1.0) unless another cite is given. Uses count
the held programs (`n_programs` in `partition_window.tsv`). "nature-only" means no method is sent to the mixin by
name; it is used only as a nature, so it is invisible to the method coverage in §8.

| mixin | role | progs | evidence beyond TM-125 |
|---|---|---|---|
| `with_border` | draws the border (4 lines); default width 2 dots. Slots border_x, border_y, border_area_width, border_area_height; border_flag := on, border_width := 2 | 9 | PRINTED TM-065 p15 (body with `after :refresh`) |
| `with_label` | the label strip (title). Provides slot `title` (TM-115 p41) | 7 | PRINTED TM-065 p16 |
| `with_two_labels` | top and bottom labels | 3 | USAGE: `top_title`, `top_label_font`, `bottom_label_font` options |
| `with_margin` | margins between border and inside; default 1 dot | 7 | Table 1 |
| `sash` | border plus margins: "a frame delimiting the area" (TM-115 p42) | 5 | USAGE nature list: pimmutil.ptf class pimmutil##scrolling_view_window |
| `labeled_sash` | sash plus label | 7 | USAGE, typical in held code |
| `two_labeled_sash` | sash plus two labels | 0 | TM-125 only |
| `as_inside` | manages the inside area (window minus border, label, margins) | 0 | PRINTED TM-065 (as nature of bare_window) |
| `as_superior` | may have inferior windows. WINCS: 子ウィンドウを持つための機能 ("the function for having child windows") | 11 | PRINTED fact WINCS p5 |
| `as_relation` | allocates sub-windows; inherited by as_superior | 0 | TM-125 only |
| `as_input_buffer` | reads input made in inferior windows (superior side) | 4 | PROSE TM-115 p41 |
| `with_superior_input_buffer` | input made here is read from the superior (inferior side). In 1985 it "shares the superior's input buffer" | 10 | PROSE TM-115 p40; USAGE (often first in the list) |
| `as_output` | text output | 10 | |
| `as_cursor` | text cursor | 0 | |
| `as_string_output` | string output | 0 | |
| `as_scroll` | scrolling | 4 | |
| `as_dot_scroll` | dot-wise scrolling | 0 | |
| `with_mouse_scroll` | scroll by mouse movement and by button clicks; read returns `scroll_request(Offset)` (1985) | 2 | USAGE pimmutil scrolling_view_window |
| `as_graphics` | graphics output | 12 | |
| `as_markers` | markers (rubber boxes and lines) | 7 | |
| `as_input` | keyboard input | 11 | |
| `as_mouse_input` | mouse input | 12 | most-used mixin |
| `with_default_mouse` | detects mouse movement and shows the cursor | 7 | |
| `with_translation_table` | translates input codes to the user's codes (§5.1) | 0 | TM-125 p18 |
| `with_window_region` | mouse-sensitive regions | 0 | |
| `with_line_selection` | each line selectable like a menu item | 0 | |
| `as_notification` | supports permission NOTIFY | 0 | TM-125 p6 |
| `as_menu` | every menu inherits it | 7 | |
| `as_single_select` / `as_multiple_select` / `as_select` | selection policy | 10 / 4 / 0 | |
| `as_multiple_column` | multi-column layout | 7 | |
| `as_submenu` | each column of a multi-column menu is a submenu | 0 | |
| `as_on_off_menu` | an on/off item is reversed when selected | 4 | |
| `as_choice` | manages choice items | 2 | |
| `as_scrolling_menu` | variable-length (scrollable) menu | 5 | USAGE (video fdd_utility, esp.wmv@155) |
| `as_menu_input` | a menu whose input is read through the superior or the program (INFERENCE from use). Added at create time: `nature([as_menu_input])` | 3 | USAGE ptf.md W1 |
| `as_temporary_window` / `as_popup_window` | the 1985 temporary and popup mixins | 0 | PROSE TM-115 p92 |
| `with_icon` | the window can be closed to an icon (§4.3) | 8 | USAGE; `nature([with_icon])` at create (fep_services.md §6.9) |
| `with_shared_window` | shared between processes (WINCS プロセス間共有, INFERENCE on the name). `:assign_window/1` before set_title, activate and deactivate (cil/src/ms_cfm.esp:118-128) | 5 | USAGE nature list: paragraph.ptf class paragraph##profiler_view_window |
| `with_key_select` | keyboard selection; probably the capital letter in items such as "seT up" (INFERENCE, ptf.md W2) | 3 | USAGE nature list: pimmcsp.ptf class pimmcsp##csp_schedule_rule_temporary_superior_window |
| `with_click_information` | read reports which button was clicked (INFERENCE from name and use with read/2 before-demons) | 5 | USAGE ptf.md W8 |
| `with_bell` | bell (beep) | 4 | USAGE nature list: pimmcsp.ptf class pimmcsp##csp_schedule_rule_temporary_superior_window |
| `with_keeping_status` | keeps item on/off status (INFERENCE). Tier A, but in **no** partition | — | USAGE pimmcsp |
| `with_pane` | child-size setting (INFERENCE from the WINCS 子ウィンドウのサイズを設定 attribute) | 2 | USAGE nature list: kappa.ptf class kappa##pbwin |
| `with_pmacs_window` | gives an application frame a Pmacs editor pane | 6 | USAGE cal-esp/deb2.12/windows.esp:9 |
| `as_standard_io_window` | the mixin form of standard_io_window | 6 | USAGE sum/src/title_win.v32:11 |
| `with_no_execute_choice_item` | choice window without the do_it item (INFERENCE from the name and the `..._with_no_execute` classes) | 2 | USAGE nature list: kappa.ptf class kappa##kappaMOP_choice_menu_with_no_execute |
| `as_inhibit_reshape` | refuses reshape (INFERENCE). In no partition | — | USAGE `nature([...])` option |
| `reshape_notifier` / `select_notifier` / `deexpose_notifier` | call `:has_been_reshaped(W)`, `:has_been_selected(W)` and (INFERENCE) a deexpose hook | 8 / 2 / 1 | USAGE (demons prove the primaries: ptf.md §2) |
| `with_character` | c:`get_character_font/2` | 1 | UNSPECIFIED (1 use) |
| `pmacs_request` | Pmacs request message (INFERENCE) | 3 | nature-only |

**Internal classes** (TM-125 p13, PROSE, 1.0):

| class | role |
|---|---|
| `window_manager` | the window-manager process |
| `display` | screen plus status_line |
| `screen` | the logical screen |
| `status_line` | the system line at the bottom of the display |
| `logical_mouse` | a single_object |
| `window_message` | user process ⇄ window manager message |
| `single_object` | limits a class to N instances |
| `window_manipulator` | the manipulator menu |

### 1.4 Combination constraints

All of these are from WINCS, which took them from ICOT's 1987 manual (ref. [12]).

| rule | grade, cite |
|---|---|
| Exactly one base class must be present: inferior_window, popup_window or temporary_window. ("At least one" is printed; exclusivity is INFERENCE.) | PROSE WINCS p7-8 |
| `as_menu` requires `as_mouse_input`; the converse does not hold | PROSE WINCS p3, p8 |
| `as_single_select` requires `as_menu` | PROSE WINCS p9-10 |
| `as_menu` excludes `as_graphics` | PROSE WINCS p3 |
| `as_menu` excludes `as_output` in one window. The fix is `as_superior` plus child windows, with the parent taking `as_input_buffer` | PROSE/PRINTED WINCS p7-10, p12 |
| `with_label` comes before `inferior_window`; `with_label` comes before `as_output`; `as_output` comes before `inferior_window` | PROSE + fact form, WINCS p3, p11 |

**Exception.** TM-115 prints `font_multiple_select_multi_column_menu` with **no** `as_menu` but with
`as_multiple_column, as_multiple_select` (TM-115 p42, PROSE, 1.0). That is a 1985 exception to the `as_menu` rule,
or a typo.

### 1.5 Recipes: nature lists, in order

| class (owner) | nature list | grade, cite | version |
|---|---|---|---|
| measurement window (TM-125); identical to `kappa##window` | labeled_sash, as_scroll, as_output, as_graphics, as_markers, as_input, as_mouse_input, user_window | PRINTED TM-125 p20 [19]; USAGE kappa2/kappa2/utility/fmp/UTL_WIND.ESP:6 | 1.0; 1992 |
| `bare_window` | with_display, as_inside, * | PRINTED TM-065 p15, TM-061 p8 | 1984 |
| `window_with_border_and_label` | bare_window, with_border, with_label | PRINTED TM-065 p16 | 1984 |
| WINCS `my_window1` (frame) | with_margin, with_label, with_border, as_superior, as_input_buffer, inferior_window | PRINTED WINCS p12 | PSI-II |
| WINCS `my_window2` (text and graphics) | with_margin, with_label, with_border, as_scroll, as_output, as_graphics, as_markers, as_input, as_mouse_input, inferior_window | PRINTED WINCS p12 | PSI-II |
| WINCS `my_window3` (menu pane) | with_margin, with_label, with_border, as_menu, as_single_select, as_mouse_input, inferior_window | PRINTED WINCS p12 | PSI-II |
| WINCS `my_window` | as_output, as_graphics, inferior_window | PRINTED WINCS p2 | PSI-II |
| video `move_win` | as_output, with_label, inferior_window | SCREENSHOT esp.wmv@110-117 | 2.50/A00 |
| video `fdd_utility_file_menu` | labeled_sash, as_scrolling_menu, as_multiple_select, as_mouse_input, temporary_window | SCREENSHOT esp.wmv@155-162 | 2.50/A00 |
| TM-115 font_inferior_window | with_superior_input_buffer, as_input, as_mouse_input, as_output, as_graphics, user_window | PROSE TM-115 p40 | 1.0 |
| TM-115 font_superior_window | as_input_buffer, as_superior, user_window | PROSE TM-115 p41 | 1.0 |
| TM-115 font_multiple_select_menu | sash, with_superior_input_buffer, as_menu, as_multiple_select, as_mouse_input, user_window | PROSE TM-115 p42 | 1.0 |
| TM-115 font_temporary_window | sash, as_input, as_mouse_input, as_output, as_temporary_window, user_window | PROSE TM-115 p92 | 1.0 |
| menu pane in a frame (held) | sash, as_menu, as_single_select, as_mouse_input, with_superior_input_buffer, inferior_window | USAGE cal-esp/cal2.12/sccmds.esp:8 | held |
| editor pane in a frame (held) | with_pmacs_window, as_superior, ..., inferior_window | USAGE cal-esp/deb2.12/windows.esp:9 | held |
| top-level iconifiable frame (held) | with_icon, with_key_select, ..., standard_superior_window | USAGE cil/src/ds_brs.esp:120 | held |
| one-line message box `pimmutil##output_msg` | with_border, as_menu, as_single_select, as_mouse_input, temporary_window | USAGE (ptf) | ptf 1992 |
| `pimmutil##scrolling_view_window` | sash, with_superior_input_buffer, with_mouse_scroll, as_graphics, as_mouse_input, inferior_window | USAGE (ptf) | ptf 1992 |
| `pimmcsp##csp_schedule_rule_temporary_superior_window` | with_click_information, with_key_select, as_superior, as_input_buffer, with_bell, reshape_notifier, temporary_window | USAGE (ptf) | ptf 1991 |
| `paragraph##what_shell_window` | as_graphics, reshape_notifier, as_mouse_input, labeled_sash, superior_window | USAGE (ptf) | ptf 1992 |

### 1.6 Composite (ready-made) classes, by family

None of these composites has a printed nature list. The decomposition is INFERENCE from the names and from the
methods sent to them. One exception: TM-181 p3 says `standard_io_window` has "10 natures, which expand to 40 classes,
121 slots and 527 methods" (STRUCTURE.md §7, SKETCHED, 2.x). Prefixes:

| prefix | meaning (INFERENCE unless cited) |
|---|---|
| `standard_` | complete, labelled, bordered, top-level |
| `essential_` | the same, without the extras (label-less use; often `label_flag(off)`) |
| `temporary_` / `popup_` | the base class (§1.2) |
| `scrolling` | as_scrolling_menu |
| `multi_column` | as_multiple_column |
| `multi_select` / `multiple_select` | as_multiple_select |
| `on_off` | as_on_off_menu |
| `_with_superior_input_buffer` | that mixin |
| `_with_no_execute` | no do_it item |

| family | classes in the partition |
|---|---|
| plain windows | `window` (1.0 stand-alone), `window_without_label`, `window_with_two_labels` (1.0), `standard_window`, `essential_window`, `standard_temporary_window`, `essential_temporary_window`, `standard_popup_window`, `temporary_window`, `popup_window`, `inferior_window`, `cal_window` (an application name, tier C) |
| superiors | `superior_window`, `labeled_superior_window`, `standard_superior_window`, `standard_popup_superior_window`, `standard_temporary_superior_window` |
| text I/O | `standard_io_window`, `temporary_standard_io_window`, `as_standard_io_window` |
| editor | `pmacs_window`, `with_pmacs_window`, `editor_main_window`, `editor_buffer_window`, `standard_editor`, `pmacs_standard_editor`, `editor_command_interpreter`, `editor_text_buffer`, `editor_yank_buffer`, `named_yank_buffer_subsystem` |
| single-select menus | `menu`, `standard_menu`, `temporary_menu`, `standard_temporary_menu`, `standard_popup_menu`, `menu_with_superior_input_buffer`, `multi_column_menu`, `standard_multi_column_menu`, `temporary_multi_column_menu`, `standard_temporary_multi_column_menu`, `multi_column_menu_with_superior_input_buffer`, `cascade`, `cascade_index` |
| scrolling menus | `standard_scrolling_menu`, `essential_scrolling_menu`, `essential_scrolling_menu_with_superior_input_buffer`, `standard_temporary_scrolling_menu`, `temporary_scrolling_menu`, `temporary_single_scrolling_menu`, `standard_popup_scrolling_menu` |
| multiple-select menus | `multiple_select_menu`, `multiple_select_multi_column_menu`, `temporary_multiple_select_menu`, `temporary_multiple_select_multi_column_menu`, `standard_multi_select_menu`, `standard_temporary_multi_select_menu`, `multiple_select_scrolling_menu`, `multiple_select_scrolling_menu_with_superior_input_buffer`, `standard_multi_select_scrolling_menu`, `standard_temporary_multi_select_scrolling_menu`, `standard_popup_multi_select_scrolling_menu`, `temporary_multiple_scrolling_menu` |
| on/off menus | `scrolling_on_off_menu`, `scrolling_on_off_menu_with_superior_input_buffer`, `essential_on_off_menu` |
| choice windows | `choice_window`, `standard_choice_window`, `temporary_choice_window`, `standard_temporary_choice_window`, `popup_choice_window`, `standard_popup_choice_window`, `choice_window_with_no_execute`, `temporary_choice_window_with_no_execute` |
| files and buffers (text protocol, §2.8) | `standard_input_file`, `standard_output_file`, `standard_io_buffer`, `standard_input_text_buffer_accessor`, `standard_output_text_buffer_accessor` |
| system | `screen`, `bitmap`, `bitmap_display`, `window_subsystem`, `font`, `font_13`, `font_editor`, `color_manipulator` |
| one-program names, probably application classes (tier D) | `net_talk_window`, `kappaREP_select_menu`, `ras_with_input_window`, `ras_with_font_key_assignment`, `kakari_attribute_menu`, `imi_attribute_menu`, `imi_attribute_sub_menu`, `gen_menu_win`, `you_menu_win`, `utls_icon`, `with_cwi`, `as_turning_menu`, `cal_op_menu`, `cal_file_menu` |

**1985 names not used by the held programs** (TM-125 p8-13): `window_region`, `marker`, `menu_item`, `choice_item`,
`submenu`, `temporary_multiple_select_multi_column_menu`. Of these, `marker` and `menu_item` are real:
- IPSJ 122601 had to re-create `marker` for CESP (newipsj.md, §4.1(3)).
- The 1984 system menu creates items with `:create(#menu_item, 'window', common, window, _, Item)`, which is
  c:create/6 (TR-046 p27, PRINTED).

**Classes the 1992 RLS port re-implemented for CESP** (IPSJ 122601 p1-2 §4.1, PRINTED-INTERFACE):
- defined directly by multiple inheritance: standard_scrolling_menu, standard_io_window, window_without_label,
  as_mouse_input, labeled_sash, as_scroll;
- made by subclassing CESP classes: choice_window and popup_choice_window;
- written from scratch: as_markers, with `marker` defined separately.

This is an independent list of what a real mid-size application used.

---

## 2. Protocols and classes

TM-125 never says which class defines which method (trtm_window.md W5). The held programs mostly send to
composites (`standard_io_window`, `standard_menu`, ...), and the census often cannot attribute a send (`?`). So this
section describes each **protocol** once, with the mixin that most likely owns it (INFERENCE unless cited). §2.14
then lists, for every class in the partition, exactly which methods the held programs send to it. Appendix A is the
generated dictionary of all 194 distinct required selectors with their best evidence.

### 2.1 Life cycle and geometry (every window)

The 1985 sequence (TM-125 p13, PROSE):
1. define the class;
2. `:create` it;
3. set attributes;
4. `:activate`;
5. operate;
6. `:kill`.

Held programs follow the same sequence. When a class wants panes, they are built in an `after:create` demon and
activated or killed in `after:activate` / `before:kill` demons (txtstrct/ctx_system.esp:403-438; kappa FMP.ESP:72-82,
USAGE).

| method | meaning | grade, cite | version |
|---|---|---|---|
| c:`create/2` `(Class,^W)` | create with default options | PRINTED-INTERFACE TM-125 p13 | 1.0 |
| c:`create/3` `(Class,Options,^W)` | create; options are §3.2. The window is not shown until `activate` | PRINTED-INTERFACE TM-125 p13-14; PRINTED Giho 8609 p20; USAGE (1499 uses) | all |
| c:`create_with_input/4,5` `(Class,Opts,[_],InputSuperior,^W)` | create with the input superior given | USAGE txtstrct/ctx_system.esp:408; tour##tt_window_manager (ptf) | held |
| `activate/1` | schedule the window for display on its superior; held code treats it as "show now" | PRINTED-INTERFACE TM-125 p16; PROSE Giho 8609 p19 | all |
| `activate/2` `(W,mouse)` | activate at the mouse position (menus, popups) | USAGE kwic-esp-002/kwic-esp/src/windows.esp:140; cil library_utility `:activate(Menu,mouse)` (COPY, ifs_libshell.md §4.1.2) | held |
| `show/1` | show the window, raising it fully | PRINTED-INTERFACE TM-125 p16 | all |
| `hide/1` | hide it on the superior; uncovered parts keep their last image | PRINTED-INTERFACE TM-125 p16 | all |
| `deactivate/1` | take it off the screen schedule without killing it; the image is kept | PRINTED-INTERFACE TM-125 p16 | all |
| `kill/1` | delete the window and release its bitmap. Windows are registered to the creating process and die with it | PRINTED-INTERFACE TM-125 p18 | all |
| `close/1` | close to an icon. kappa swaps the window for its icon in `before:/after:close` (kappa2/kappa2/utility/mop/MOPMWIN.ESP:31-37). pimfep binds it to `mouse#mm` | USAGE; pimfep##pimos_fep_superviser refute_command/3 (ptf) | held |
| `expose/1` | bring to front (INFERENCE from name) | USAGE icotext/src/kei_command_menu.esp:72 | held |
| `select/1` | make it the keyboard (input) window | PROSE Giho 8609 p19; PROSE TM-125 p22 | 2.0 |
| `set_size/3` `(W,Wd,Ht)` | resize. `set_size(W,manipulator,_)` lets the user sweep the new size | PRINTED-INTERFACE TM-125 p15; USAGE pimfep device set_size/3 (ptf) | all |
| `set_position/3` `(W,X,Y)` | move, in the superior's coordinates. `set_position(W,manipulator,_)` lets the user place it | PRINTED-INTERFACE TM-125 p15; USAGE (ptf W4; kwic windows.esp:84-89) | all |
| `reshape/5` `(W,X,Y,Wd,Ht)` | move and resize at once; `reshape(W,manipulator,_,_,_)` sweeps it | USAGE cal-esp/cal2.12/cpwindow.esp:85 (72 uses, unattributed); pimfep reshape_by_mouse (ptf) | held |
| `get_size/3`, `get_position/3` | outer size; position in the superior | PRINTED-INTERFACE TM-115 p50, p63 | all |
| `get_inside_size/3` | inside (client) size in dots; used to lay out panes | SCREENSHOT IPSJ 36239 p5; USAGE | 2.50; held |
| `set_text_size/3`, `get_text_size/3` `(W,Cols,Rows)` | Pmacs-window size in characters | USAGE pimfep device reshape/7, get_inside_size/3 (ptf.md W6) | ptf 1994 |
| `set_inside_units/3` `(W,UX,UY)`, `get_inside_units/3` | grid unit for inside coordinates. The default is the `font_13` space cell (TM-115 p41); TM-125 Table 1 gives "1 dot". VARIANT | PROSE TM-115 p41, p80; SCREENSHOT IPSJ 36239 p5; USAGE | 1.0-held |
| `set_superior/2`, `get_superior/2` | re-parent; read the parent | PRINTED-INTERFACE TM-125 p15; get_superior UNSPECIFIED | 1.0 |
| `get_activity/2` | probably answers whether the window is active (INFERENCE). Called as `:get_activity(Menu,1)` (euod/PROOF/proof2.esp:3521); pimfep reads a slot `activity` inherited from pmacs_window (ptf.md W6) | USAGE + INFERENCE | held |
| `has_been_reshaped/1`, `has_been_selected/1` | callbacks from `reshape_notifier` / `select_notifier`, overridden by the user (§2.12) | USAGE (demons) | held |

**Failure.** `:activate(W)` can fail. kwic then retries after `:set_position(W,manipulator,_)`
(kwic-esp-002/kwic-esp/src/windows.esp:84-89, USAGE). INFERENCE: activation fails when the window would extend off
the screen. TM-115 p29 says the manager "does not allow a window to go out of the screen" (PROSE, 1.0).

### 2.2 Label, border, margins, fonts, appearance

| method | meaning | grade, cite |
|---|---|---|
| `set_title/2`, `get_title/2` | label string | PRINTED-INTERFACE TM-125 p15; USAGE (111 uses) |
| `set_top_title/2`, `set_bottom_title/2` | the two labels of with_two_labels | PRINTED-INTERFACE TM-125 p15 |
| `set_label_position/2` `(W,top\|bottom)` | where the label is drawn | PRINTED-INTERFACE TM-125 p15 |
| `set_label_flag/2` | label on or off (INFERENCE from the option `label_flag(off)`) | UNSPECIFIED (1 use) |
| `get_label_height/2` | label height in dots, for layout | USAGE cil/src/ds_brs.esp:280 |
| `set_border_width/2`, `get_border_width/2` | border width in dots, default 2 | PRINTED-INTERFACE TM-125 p15 (printed "set border_width"); get: UNSPECIFIED (12 uses), INFERENCE: returns the width |
| `set_margins/5` `(W,L,R,Head,Tail)`, `get_margins/5` | margins in dots, default 1. The CESP substitute for SIMPOS's `with_margin` has `get_margins(W,^Left,^Right,^Head,^Tail)`, plus `set_margin_flag/2` and `get_margin_flag/2` | PRINTED-INTERFACE TM-125 p16; get: CESP substitute linguist/prog/with_margin.esp:21-34, software1.tex:802-827 (sweep_2026-11-24 §2.2); held uses 3 |
| `set_font/2` `(W,FontObj)`, `get_font/2` | text font. Also resets the cursor size from the font's space character | PRINTED-INTERFACE TM-112 p16; PROSE TM-115 p16-17; USAGE (174) |
| `set_label_font/2` | label font | USAGE (55) |
| `background/2` `(W,black\|white)` | background colour; with black, text is drawn white on black (`move_win`, esp.wmv@118) | USAGE paragraph p_wshell.esp:74-78; SCREENSHOT |
| `set_name/2` `(W,String)` | window **name**, distinct from its title. TM-125 Fig. 4 has separate LABEL and NAME attributes. INFERENCE: the name is what the status line shows | USAGE euod/RULED/ruled1.esp:623 (call shape); meaning INFERENCE |
| `set_mouse_marker/2` `(W,N)`, `reset_mouse_marker/?`, `get_mouse_marker/?` (arity not recorded) | mouse-cursor shape number. `6` is set after a menu is created (cal-esp/cal2.12/grmenu.esp:16); the numbering is unknown | USAGE cal-esp/cal2.12/grmenu.esp:16 |
| `set_icon/2` `(W,IconId)` | icon glyph for with_icon, an id registered with `window_subsystem:add_icon/4` | USAGE kappa2/kappa2/user_if/pb/pbm.esp:341; kappa FMP.ESP:41 |
| `set_permission/2` `(W,out\|show\|...)` | output permission (§4.1) | USAGE gog-esp/DISPB3.ESP:377 |
| `set_color/2,3`, `set_color_pair/3` | colour windows (§3.7) | PRINTED TM-785 p31; USAGE |
| `hardcopy/2` `(W,laser_printer)` | print the window | USAGE euod/DEF/def.esp:910; manipulator item HARDCOPY (TM-125 p8) |

### 2.3 Window text output (character-cell level)

This is the TM-125 level, owned by `as_output` / `as_cursor` (INFERENCE). Coordinates are character cells unless
`set_inside_units` changed them. A `standard_io_window` adds §2.4 on top.

| method | meaning | grade, cite |
|---|---|---|
| `write/2` `(W,Code)` | write one character at the cursor and advance | PRINTED-INTERFACE TM-125 p16, TM-112 p16 |
| `write_line/2` `(W,String)` | write a string at the cursor. 1985: fails if a code has no glyph in the font | PRINTED-INTERFACE TM-112 p16; USAGE |
| `write_lines/2` `(W,String)` | write a string that may contain `key#lf` line breaks (TM-153 p26 uses `key#lf`) | PRINTED-INTERFACE TM-112 p16; PRINTED TM-134 p70 |
| `write_line/3` `(W,Row,String)`, `write_line/4` `(W,Row,Col,String)`, `write_line_tail/4` `(W,Row,Col,String)` | write at a row/column. INFERENCE: `_tail` clears to the end of the line after writing | USAGE fuzclust/fuzclust/src/matrix.clu:298; knov/src/system/cg.esp:307, eg.esp:62 |
| `put_line/2` | write a line (message windows) | USAGE kwic-esp-002/kwic-esp/src/windows.esp:148 |
| `insert/2`, `delete/2` | insert or delete a character at the cursor; the cursor does not move on delete | PRINTED-INTERFACE TM-125 p16 |
| `move_cursor/3` `(W,Col,Row)`, `get_cursor_position/3` | cursor position | PRINTED-INTERFACE TM-125 p16; USAGE disc/util.esp:262 |
| `erase_cursor/1`, `draw_cursor/1` | hide or show the text cursor (a solid block, IPSJ 36239 p5, simpos.wmv@0) | SCREENSHOT IPSJ 36239 p5; USAGE |
| `clear_line/1` | clear from the cursor to the end of the line | PRINTED-INTERFACE TM-125 p16 |
| `clear/1` | clear the window and home the cursor (INFERENCE) | USAGE (35); fep_services.md §6.9 |
| `scroll/2` `(W,Offset)` | scroll; positive = up | PRINTED-INTERFACE TM-125 p16 |
| `open_rows/3`, `move_rows/4` | insert rows; move rows Row1..Row2 by Offset | PRINTED-INTERFACE TM-125 p16-17 |
| `beep/1` | ring the bell | USAGE (69) |
| `flash/1` | make buffered output visible (Appendix A) | USAGE pimfep.ptf pimfep##pimos_window_editor (kl0 run) |
| `view_next_screen/1`, `view_previous_screen/1`, `view_two_windows/1`, `other_window/1` | Pmacs page and split commands, sent to a window (INFERENCE) | UNSPECIFIED (1, 1, ?, 8 uses) |

**Newline.** In ESP on SIMPOS a newline written character-wise is the pair `:write(W,key#cr), :write(W,key#lf)`.
The CESP port needed only the first half (IPSJ 122601 p2 §4.2, PRINTED-INTERFACE). Held code uses the pair
(kappa2/kappa2/utility/fmp/FCWIN.ESP:53-54; utter/source/Sancho/sancho.esp:63-64, USAGE).

### 2.4 The standard I/O text protocol

Who shares it:
- `standard_io_window` (windows);
- `standard_io_buffer` (memory);
- `standard_input_file` / `standard_output_file` (files);
- the text-buffer accessors;
- `pmacs_window` and `library_utility` (COPY, ifs_libshell.md §4.1.1).

ESP defines character, line and structure I/O device-independently in a standard I/O class; device classes define
per-character I/O and inherit it (IPSJ 36239 p3-4, PROSE, 2.50). Since 3.0 every character-I/O window is a "window
with Pmacs function" (Pmacs機能付ウィンドウ). Input echo and system output go into an editor buffer, so earlier
lines can be edited and re-sent (IPSJ 114007 §6; IPSJ 36239 p4 rule 1; TM-229 p5, PROSE). The held compiled code
confirms the mechanism: the PIMOS window device is a `pmacs_window` driven through `standard_editor`
(fep_services.md §6.8, USAGE).

**Output** (owner `as_standard_io_window` / standard_io; INFERENCE)

| method | meaning | uses | grade, cite |
|---|---|---|---|
| `putl/1` `(S)` | write a newline | 70 | USAGE cal-esp/cal2.12/control.esp:246 |
| `putl/2` `(S,String)` | write the string, then a newline | 428 | PRINTED Giho 8609 p20 Fig. 8; USAGE |
| `putb/3` `(S,String,Len)` | write the first Len characters, no newline | 79 | USAGE cal-esp/deb2.12/pmod.esp:68 |
| `putc/2` `(S,Code)` | write one character (`#">"`, `key#lf`) | 27 | PRINTED Giho 8609 p20; PROSE TR-285 p11 |
| `putt/2` `(S,Term)` | write a term in ESP syntax, honouring the unparsing operators and `unquote_atom` | 148 | USAGE cal-esp/cal2.12/ccwindow.esp:65 |
| `putt/4` `(S,Term,VarsIn,VarsOut)` | write a term, threading a variable-name table | 33 | USAGE cal-esp/deb2.12/output.esp:516 |
| `putf/2` `(S,Format)`, `putf/3` `(S,Format,Args)` | formatted output (directives below) | 130 / 365 | USAGE euod/BUP/bup.esp:1781 |
| `unquote_atom/1` | print atoms unquoted from now on (INFERENCE) | 17 | USAGE papyrus_src/demo/TREE/winop.esp.1:8 |
| `set_unparsing_operator/2`, `get_unparsing_operator/2`, `set_max_depth/2`, `set_max_length/2` | operator pool and print limits for putt (INFERENCE). Depth/length elision is "holophrasting": CAL's debugger manual sends the reader to the SIMPOS programming manual's section 「標準入出力（ホロフラスティング）」 for it (cal-esp/deb_jman/debug.tex:232-237) | 2-4 | UNSPECIFIED |

**Input**

| method | meaning | uses | grade, cite |
|---|---|---|---|
| `getl/2` `(S,^String)` | read a line as a string | 153 | USAGE cal-esp/deb2.12/dmenu.esp:796 |
| `gett/2` `(S,^Term)` | read a term, terminated by full stop and return; on a window the user types it. The 1986 screenshot shows `Input X>100.` | 138 | PRINTED Giho 8609 p20; SCREENSHOT Fig. 10 |
| `gett/4` `(S,^Term,VarsIn,VarsOut)` | read a term with a variable-name table | 13 | USAGE cal-esp/cal2.12/control.esp:245 |
| `getc/2` `(S,^Code)` | read one character | 15 | SCREENSHOT esp.wmv@143; USAGE |
| `get1/2` | unknown (ifs_window.md open question) | — | USAGE (notes: ifs_window.md §5); UNSPECIFIED |
| `getb/3` `(S,^String,^Size)` | whole buffer contents | 6 | USAGE cil/src/ms_ist.esp:1813 |
| `end_of_input/1` | succeeds at the end of a file or buffer | 54 | USAGE cal-esp/cal2.12/control.esp:201 |
| `put_back/2` `(S,Code)` | push a code back onto the input | 1 | USAGE cil/src/es_trc.esp:1402 |
| `get_with_prompt/3` | prompt in the echo area and read the answer | 2 | USAGE cal-esp/deb2.12/dedit.esp:318 |
| `set_input_position/1` | mark the end of output as the start of user input (called before gett, getl, getc) | 4 | USAGE cil/src/es_trc.esp:1405 |
| `clear_buffer/1`, `clear_input/1` | discard pending input | 9 / 13 | USAGE; clear_input UNSPECIFIED |
| `read_sense/2` | non-blocking read (§2.7) | | |
| `set_parsing_operator/2`, `get_parsing_operator/2` | operator pool for gett (INFERENCE) | 5 / 22 | UNSPECIFIED |
| `reread/1`, `size/2` | buffer only: rewind to read what was written; character count | 4 / 4 | USAGE cil/src/ds_bep.esp:1488-1491 |

**putf directives.** Grade USAGE for the forms seen in real calls. The full table is INFERENCE: it rests on kwic's
re-implementation `fncSPutf.esp`, the most detailed putf semantics held, but not SIMPOS code (notes: ifs_window.md §5).

Syntax: `\`, then optional numeric parameters (digits, separated by `.`; `@` takes a parameter from the argument
list), then modifiers (`<` = left-justify), then a command letter.

| directive | meaning |
|---|---|
| `\n`, `\Nn` | newline(s) |
| `\Nb` | N blanks; the count is the product of the parameters (`\4b`, `\.@b`) |
| `\c`, `\N.Mc` | a character |
| `\d` `\o` `\x` (`\X`) | a number in radix 10, 8 or 16 (`\2x`, `\5d`) |
| `\N.M.Ri` | a number in radix R |
| `\s`, `\N.Ms`, `\<s` | a string (`<` left-justifies) |
| `\q` | a quoted term |
| `\Q` | toggle quoting |
| `\f` | a float (`\6.6.4f`, gog) |
| `\[..\;..\]` | choose the Nth alternative |
| `\k` | skip arguments |
| `\m` | repeat |
| `\{..\}` | iterate |

`\C`, `\W`, `\u` and a backslash before a kanji also occur; their meanings are unknown. The compiled packages use
`\d \q \x \X \s \c` and widths such as `\2x`, `\5d` (notes: ptf.md S1). The arguments of putf/3 are a list:
`:putf(Buffer,"% Source file : \s",[Pathname])` (cil/src/ds_bep.esp:1484, USAGE).

**Term I/O through the editor.** cal maps a Prolog-style layer (read_term, put, write_term, new_line, tab) onto
Pmacs window methods by delegating through `:undefined_method` (cal-esp/deb2.12/pmod.esp:54-110, USAGE). Any object
that defines the protocol above is a valid I/O target.

### 2.5 Graphics (owner `as_graphics`, INFERENCE; WINCS prints `class_method(as_graphics, draw_line, [5,...])`)

Conventions:
- **Coordinates** are dots in the inside area. With `set_inside_units` they are units. `draw_string` is anchored at
  the **top-left** of the first letter (TM-125 p17, PRINTED-INTERFACE). CESP changed this to bottom-left (IPSJ 122601
  §4.3).
- **Op** (the ALU operation) is the last argument:
  - `set`, `reset` (USAGE, PRINTED WINCS p3);
  - `exclusive_or` (IPSJ 36239 p5; TM-115 p43). This is the 1985 default: "default is exclusive or", TM-125 p17;
  - `xor`, `color` (TM-785 p12);
  - `copy`, `inverse` (TM-115 p43);
  - `reverse` (TM-785 p19, for image transfer).

  A colour number may stand in place of the op once colours are set (TM-785 p29, PRINTED).
- **Line style:** `solid`, `dotted` (TM-785 p40). TM-125's default is "fixed line" = `solid` (INFERENCE).
- **Fill pattern:** `fix`, `light_paint` (ptf.md W5); `filled` (IPSJ 36239 p5); `mesh`, `left_hatch`, `small_mesh`,
  `dotted` (TM-785 p40).

| method | arguments (receiver first) | grade, cite | version |
|---|---|---|---|
| `draw_line/5` | W,X1,Y1,X2,Y2. Width 1, solid, exclusive-or by default | PRINTED-INTERFACE TM-125 p17; PRINTED WINCS p12 | 1.0, PSI-II |
| `draw_line/6` | W,X1,Y1,X2,Y2,Op in paragraph; W,X1,Y1,X2,Y2,Width in gog (`...,1)`). **VARIANT** | USAGE paragraph percent_menu_window up/5 (ptf; notes: ptf.md W5); gog-esp/KE_WINDOW.ESP:453 | held |
| `draw_line/7` | W,X1,Y1,X2,Y2,Width,Style | USAGE gog-esp/KE_WINDOW.ESP:454 (55 uses) | held |
| `draw_line/8` | W,X1,Y1,X2,Y2,Width,Style,Op | PRINTED-INTERFACE TM-125 p17 (misprinted "X1, X2, X2, Y2"); PRINTED-INTERFACE TM-785 p40; USAGE | all |
| `draw_rectangle/5`, `/7`, `/8` | W,X,Y,Wd,Ht [,Width,Style [,Op]] | PRINTED-INTERFACE TM-125 p17; IPSJ 36239 p5 (`...,1,filled,exclusive_or`); USAGE gog-esp/KE_WINDOW.ESP:349, fuzclust/fuzclust/src/window.net:102 | all |
| `draw_filled_rectangle/6`, `/8` | W,X,Y,Wd,Ht,Op / W,X,Y,Wd,Ht,?,Pattern,Op (the 6th argument is unknown) | USAGE ptf.md W5; PRINTED-INTERFACE TM-785 p40 | held, 5.x |
| `draw_circle/7` | W,CX,CY,R,Width,Style,Op | PRINTED WINCS p3 | PSI-II |
| `draw_filled_circle/5`, `/7` | W,X,Y,R,Op (gog-esp/DISPB2.ESP:94); /7 per TM-785 p40 | USAGE; PRINTED-INTERFACE | held, 5.x |
| `draw_arc/9`, `draw_fan/9`, `draw_ellipse/8`, `draw_elliptical_arc/10`, `draw_filled_ellipse/7`, `draw_filled_fan/9`, `draw_polygon/9`, `draw_graph/9` | centre-first shapes; the polygon/graph element 0 is a list of points | PRINTED-INTERFACE TM-785 p40 (vectors; arity INFERENCE from vector length) | 5.x |
| `draw_graph/2`, `draw_polygon/2` | W,[(X,Y),...] | USAGE kwic-esp-002/kwic-esp/src/scrolls.esp:1135 | held |
| `draw_characters/4` | W,[{Code,X,Y,W,H}...],N,Font | PRINTED-INTERFACE TM-785 p40 | 5.x |
| `draw_string/4` | W,X,Y,String | PRINTED-INTERFACE TM-125 p17, TM-112 p16; USAGE euod/DEF/def.esp:2427 | all |
| `draw_string/5` | 1985: W,X,Y,String,Op. Held: W,X,Y,String,Font. **VARIANT** | PRINTED-INTERFACE TM-125 p17; USAGE cal-esp/cal2.12/grmenu.esp:195 | 1.0 vs held |
| `draw_string/6` | W,X,Y,String,Font,Op | USAGE paragraph c_p_meter (ptf.md W5) | held |
| `get_point_value/4`, `set_point_value/4` | read or write pixel 0/1 | PRINTED-INTERFACE TM-125 p17 | 1.0 |
| `transfer/8` | W,SX,SY,DX,DY,Wd,Ht,Op: block move inside a window | USAGE cil/src/es_gin.esp:855 | held |
| `copy/9` | between windows: Dst/Src,SX,SY,DX,DY,Wd,Ht,Op. Direction is INFERENCE | USAGE icotext/src/util_scroll.esp:211 | held |
| `paint/5` | W,X,Y,Pattern,Op | USAGE kappa2/kappa2/user_if/pb/pdim.esp:606 | held |
| `execute_graphics_command/2` | W,[draw_line({...}),...]: a batch of `{Op,{Args}}` | USAGE paragraph p_icon.esp:61 (ptf.md W5) | held |
| `refute/3` | W,MethodName,ArgVector: call any draw method by name | PRINTED TM-785 p32 | 5.x |
| `redraw_inside/2`, `draw_bars/5`, `restore/7` | application-held (paragraph) | — | — |
| image `load/5` on `#image_file` | draw an `.image` file into a window | USAGE pimfep superviser create_window/1 (ptf.md W1); PROSE TM-785 p21 | held, 5.x |

**Manager methods (1.0).** In 1.0 processes had no direct access to bitmap memory. Methods that move bitmap areas
ran inside the window manager, named `:do_x` beside the user method `:x` (`:get_size`/`:do_get_size`). The request
mechanism is not printed (TM-115 p43, p81-85, PROSE). Bitmap areas:
- are allocated, loaded, transferred and freed;
- have widths that must be multiples of 16;
- are not cleared on allocation (TM-115 p44, p79, p82).

The method names are not printed. No held program uses a `do_` method. INFERENCE: this split is internal by 3.x.

### 2.6 Markers and the mouse position (owner `as_markers` / `as_mouse_input`)

| method | meaning | grade, cite |
|---|---|---|
| `create_marker/2` `(W,^M)`; `create_marker/7` | create a marker. The CESP substitute that claims "the same function as" SIMPOS's `as_markers` takes `(W,X,Y,Width,Height,Type,^M)`, where Type is `box`, `line` or `reverse` | PRINTED-INTERFACE TM-125 p17; USAGE (ifs_window.md §5); CESP substitute linguist/prog/with_marker.esp:21-25, :216, linguist/doc/Manual/Soft/software1.tex:831 (sweep_2026-11-24 §2.2) |
| `draw_marker/2`, `erase_marker/2`, `move_marker/4` `(W,M,X,Y)` | show, hide, move | PRINTED-INTERFACE TM-125 p17 |
| `set_marker_type/3` `(W,M,box\|line)`, `set_marker_size/4`, `get_marker_list/2` | marker attributes | PRINTED-INTERFACE TM-125 p17 |
| `get_marker_position/4` | marker position (INFERENCE). The CESP substitute has only `/3` `(W,^X,^Y)`, so it does not settle `/4` | UNSPECIFIED (2 uses); linguist/prog/with_marker.esp:79 |
| `get_mouse_position/3` `(W,^X,^Y)` | mouse position in window units | SCREENSHOT IPSJ 36239 p5; USAGE. The CESP port divides by the unit (IPSJ 122601) |
| `get_mouse_dot_position/3` | the same in dots (INFERENCE) | UNSPECIFIED (1 use) |
| `warp_mouse/3` `(W,X,Y)` | move the mouse | USAGE kwic-esp-002/kwic-esp/src/inSheet2.esp:903 |
| c:`get_mouse/2` on `#bitmap_display`, then `:get_position(M,X,Y)` | mouse position on the screen | USAGE kwic windows.esp:110 |

### 2.7 Input and events

**Read forms** (owner `as_input` / `as_mouse_input` / `as_input_buffer`)

| call | returns | grade, cite | version |
|---|---|---|---|
| `read/2` `(W,^Code)` | blocks until input arrives. Code is a character code, a mouse code, a translated code (with_translation_table), `scroll_request(Off)` (with_mouse_scroll, 1985), the menu item's id, or `abort` (temporary menu left) | PRINTED-INTERFACE TM-125 p18; USAGE | all |
| `read/2` on a plain window | also returns the atom `deactivate` as an event | USAGE paragraph p_MAIN.esp:22-31 (ptf.md W4) | held |
| `read/3` `(Sup,^Source,^Code)` | read through a superior: which child the input came from, plus the code | USAGE euod/DEF/def.esp:111; PROSE TM-115 p27, p105 | 1.0; held |
| `read/6` `(W,^Source,^Data,^Cmd,^X,^Y)` | full event: source window, key, command (click code), position. The doc comment (TRANSLATION) names them 実際に入力したウィンドウ ("the window actually input to"), 入力されたkey, 入力されたコマンド, x/y座標 | USAGE cal-esp/cal2.12/cpwindow.esp:124, comment :130-137; paragraph p_menu.esp:47 | held |
| `read_sense/2` | like read but does not block; returns the atom `'$$nil'` when nothing is pending | PRINTED-INTERFACE TM-125 p18; USAGE cal-esp/cal2.12/scawin.esp:213 | all |
| `read_with_click/3` `(W,^Code,^Click)` | the value plus the button (`mouse#l`...). Click is `'$$nil'` when the event was a reshape | USAGE cal-esp/cal2.12/file.esp:94; cil/src/es_ins.esp:658-664; IPSJ 122601 §4.3 | held |
| `read_with_click/4` | with Source | USAGE | held |
| `read_click_with_position/4` `(W,Click,^X,^Y)`, `/5` with Source | wait for a click. Click may be bound to wait for one button | USAGE fuzclust/fuzclust/src/input_mat.clu:97, sh_window.net:84 | held |
| `read_with_code/3,4` | unknown | USAGE (ifs_window.md §3) | held |
| `input_data/2` `(W,Code)`, `input_data/6` `(W,Src,Data,Cmd,X,Y)` | push a synthetic event onto the window's input | USAGE euod/DEF/def.esp:415; cal-esp/cal2.12/ctree.esp:153 | held |
| `set_break/1`, `reset_break/1`, `break/1` | let a long output be interrupted | USAGE (ifs_window.md §4) | held |

**Rules.**
- In 1.0 a program could read only from the **selected** window. A click in an unselected window goes to the window
  manager: a single left click selects that window, and anything else is ignored (TM-115 p111; TM-112 p9-10, PROSE).
  "The next release" was to allow reading from unselected windows (TM-115 p111). The held programs read mouse
  events from any window they own (USAGE), so follow that.
- Mouse clicks go to the shown window under the mouse cursor (TM-126 p7; TM-225 p11, PROSE TRANSLATION).
- Keyboard input goes to the selected window (§4.1).
- Kana-kanji conversion happens below the window system, in the keyboard handler, so any program that reads the
  keyboard gets kanji (IPSJ 114007 §4; IPSJ 36239 p2, PROSE).
- **Abort polling.** Long operations poll `:read_sense(W,C)` and stop on `mouse#mm`, `control#"c"` or `key#abort`
  (library_utility, COPY: cil/src/ds_bep.esp:3477-3488; cal-esp/deb2.12/input.esp:123-129, USAGE).

### 2.8 Files and buffers: the same text protocol off-screen

These classes carry no window semantics. They are in the window partition because they share §2.4. coverage.py
marks their create/3 and create/2 "documented" only because a window method of the same name is printed (§8).

| class | create form | other methods | grade, cite |
|---|---|---|---|
| `standard_input_file` | c:`create/3` `(#standard_input_file, ^Stream, Path)`. **The output is the second argument.** It fails if the file does not exist, so code tries `"cal.init"` and then `"me:cal.init"` | gett/2,4, getl/2, getc/2, getb/3, end_of_input/1, **close_input/1**, set/get_parsing_operator/2 | USAGE cal-esp/cal2.12/control.esp:190-193; pimfep (ptf: `me:pimos.feps`, `pimos:pimfep.error`) |
| `standard_output_file` | c:`create/3` `(#standard_output_file, ^Stream, Path)` | putt/2,4, putl/1,2, putf/2,3, putb/3, putc/2, unquote_atom/1, set_unparsing_operator/2, **close_output/1** (writes the file) | USAGE cal-esp/cal2.12/control.esp:356-360; papyrus (ptf: `demo:INIT_FILE>lemma.cl`) |
| `standard_io_buffer` | c:`create/2` `(#standard_io_buffer, ^B)`; c:`create/3` `(#.., SizeOrName, ^B)` | the full put and get set, plus reset/1 (empty), reread/1, size/2, getb/3. Use: build text with putf/putt, then reread and getb it into a string. The 1990 ESP manual's example: two putl lines are read back as two terms by gett; putt `[1,2]` then putt `p(1,2)` reads back by getl as `"[1,2]p(1,2)"`, so putt writes no separator (the manual prints `put1`/`get1`) | USAGE cal-esp/cal2.12/control.esp:409; cil/src/ds_bep.esp:1484-1491; fuzclust/fuzclust/src/struct.eism:338; PRINTED ESPtex/program-e.tex:6736-6745, ESPtex-j/program-j.tex:6470-6480 |
| `standard_input_text_buffer_accessor`, `standard_output_text_buffer_accessor` | c:`create/3` `(#.., EditorTextBuffer, ^Accessor)` | read or write an editor buffer as a stream | USAGE papyrus_src/demo/EDITOR/my_reader.esp.1:23, pmacs_pretty.esp.1:21 |

Pathnames are SIMPOS paths: `>sys>user>demo>x.esp.3`, logical names `me:`, `font:`, `pimos:`, and a node prefix
`i3psi7::`. See `shell.md` and STRUCTURE.md §6.

### 2.9 Menus

**Kinds.**
- Menus take mouse input only: no keyboard input and no output.
- A menu window is sized automatically from the item count and the longest item. It appears at the mouse
  (TM-125 p7; TR-046 p14; TM-115 p25, PROSE).
- 2.50 distinguishes two kinds (IPSJ 36239 p4, PROSE): fixed-length operation menus, and variable-length (scrollable)
  menus whose items are the objects of operations.

**Creation.** c:`create/3` with `items_list(Items)` (§3.3). Multi-column menus take a list of columns. The title comes
from `title(..)`; `label_flag(off)` suppresses it.

**Reading.**
- `:read(Menu,^Id)` returns the chosen item's id, or `abort` (txtstrct/ctx_system.esp:31-32, USAGE).
- On a temporary menu, `read` returns `abort` when the mouse leaves (TM-125 p18). In 1.0 the read failed instead
  (TM-115 p93).
- On a multiple-select menu, `pick_up` items toggle and the `do_it` item ends the selection. The result is then
  read with `retrieve_all_items/2` or `read_items/4` (knov/src/system/ap.esp:75-83; COPY ds_bep.esp, `read_items`).
- `read_with_click/3` also gives the button.

| method | meaning | grade, cite |
|---|---|---|
| `add_item/3` `(M,Item,Pos)`, `add_item/4` `(M,Item,Col,Pos)` | insert an item vector at position 0..n | PRINTED-INTERFACE TM-125 p15 |
| `add_items/3` `(M,Items,Pos)` | insert several (`:add_items(M,L,0)`) | USAGE (ptf.md W2) |
| `delete_item/2` `(M,ItemString)` | delete by label | PRINTED-INTERFACE TM-125 p15 |
| `delete_items/?` | delete several items (INFERENCE; arity not recorded) | USAGE (notes: ptf.md W2) |
| `clear_items/1` | remove all items | USAGE cal-esp/deb2.12/create.esp:544 |
| `change_item/3` `(M,Id,NewItem)` | replace an item (menus and choice windows) | USAGE sum/src/menu_init.wkm:49 |
| `get_item/2`, `get_item_vector/2`, `get_item_value/3`, `set_item_value/3` | item access | USAGE (ptf.md W2) |
| `retrieve_item/3` `(M,Id,^Vector)`, `retrieve_all_items/2` | item vectors (with current on/off status) | USAGE cal-esp/cal2.12/astree.esp:216 |
| `set_item_status/3` `(M,Id,on\|off)`, `get_item_status/3` | on/off state (on/off and multiple-select menus) | USAGE knov/src/system/ap.esp:199 |
| `set_top_title/2`, `set_menu_title/2` | menu titles | USAGE kwic-esp-002/kwic-esp/src/windows.esp:750 |
| `enable_menu_help_click/1`, `set_help_font/2` | show item documentation on a help click (INFERENCE) | USAGE papyrus_src/demo/EDITOR/input_editor.esp.1:30 |
| `select_item/4` | user hook after a pick (an after-demon on SIMPOS's primary) | USAGE kappa tam.esp:25; (ptf §2) |

**Look.**
- The item under the mouse is boxed with a thin rectangle (simpos.wmv@10.9, @117, @132, SCREENSHOT).
- The selected items of a multiple-select menu are shown in reverse video (esp.wmv@163-169).
- A small `×` mark sits by the highlighted item (simpos.wmv@132).
- Pop-up menus have a title bar above centred items (§4.5).
- The window system can "blacken the currently executed command" (TM-115 p111, PROSE, 1.0).

These are VARIANTS of highlighting by version: boxed in 2.50 and A00, blackened in 1.0.

### 2.10 Choice windows (attribute sheets)

A choice window is a sheet of labelled fields. Each field is a text field, a boolean or a one-of-N choice. The
current value of a one-of-N field is shown in reverse video (TM-125 p7 Fig. 4, SCREENSHOT). The bottom row holds
`do_it` and `abort` (TM-125 Fig. 4; TM-785 p10-26, SCREENSHOT/PROSE).

| method | meaning | grade, cite |
|---|---|---|
| c:`create/3` with `choice_list(Items)` | §3.4 | PRINTED-INTERFACE TM-125 p14-15; USAGE |
| `read/2` `(C,^Result)` | `abort`, or `[{Key,Value},...]` for the editable fields | USAGE (ifs_window.md §3) |
| `change_item/3` `(C,Key,NewItem)` | replace a field | USAGE sum/src/menu_init.wkm:49 |
| `retrieve_item/3` | read a field | USAGE cal-esp/cal2.12/astree.esp:216 |

The `..._with_no_execute` classes and the `with_no_execute_choice_item` mixin have no do_it item (INFERENCE). Their
values are read by the program, as with `csp_break_choice_menu` (ptf.md W8).

### 2.11 Pmacs as a window component: `pmacs_window`, `standard_editor`, `editor_text_buffer`, `pmacs_standard_editor`

**What Pmacs is** (PROSE: IPSJ 114007; TM-229 p6; Giho 8609; SCREENSHOT video):
- an Emacs-like screen editor with over 100 commands;
- text lives in **buffers**, registered in a buffer pool and reachable **by name from any process**;
- implemented as a gap buffer;
- a command interpreter sends messages to an `editor` object, so users extend commands by subclassing the editor in
  ESP ("program macros");
- also keyboard macros and state variables;
- 93 classes and about 14,300 lines (IPSJ 22404 tables, PRINTED-INTERFACE; Pmacs proper may be 81 classes,
  newipsj.md);
- released to users in 2.0 (IPSJ 114007 §7).

**The objects** (USAGE: disc/exshow.esp:23-35, which sends create/3, `:create(#pmacs_window,[title(Buf)|Init],W)` at :24, then `:get_editor(W,E)` at :28; create/4 is kwic-esp src/inEditor1.esp:151 and mendels comp_win.esp:54-62, with `nature([with_superior_input_buffer])` and `superior(..)` in Opts; corrected 2026-11-24, `../source_check_2026-11-24.md`; pimfep##pimos_window_editor, ptf.md W6):

```
:create(#pmacs_window, Opts, _, W)    % create/4; 3rd argument always unbound (INFERENCE: editor out-arg)
:get_editor(W, E)                     % window -> its editor (a standard_editor)
:get_interpreter(W, I)                % window -> its command interpreter (slot original_buffer)
:get_window(E, W)                     % editor -> window
:current_buffer(E, B) / :set_current_buffer(E, B)
:read_file(E, B, File, _)             % load a file into a buffer
:set_input_buffer(W, B)               % make B the window's input buffer
:command_interpret(I)                 % run the editor loop until exit
```

| class | role | key methods (meaning from use) | grade |
|---|---|---|---|
| `pmacs_window` | the editor window; also the base of every "window with Pmacs function". Slots `activity` (read by pimfep, INFERENCE) | c:create/3,4, c:create_with_input/4,5; get_editor/2, get_interpreter/2, set_input_buffer/2, show_buffer/1, current_buffer/2, set_echo_font/? (arity not recorded), clear_echo_area/1, set_text_size/3, get_text_size/3, plus the full §2.4 protocol (putf, putl, getl, gett ...), flash/1, beep/1, set_title/2, set_font/2 | USAGE nature list: pimfep.ptf class pimfep##pimos_window |
| `standard_editor` | the editor object. Bindings are instance clauses `:command(E,Input,Method)`, with prefix tables `:control_c(..)` and `:control_x(..)` | get_window/2, current_buffer/2, set_current_buffer/2, select_buffer/2, insert/2, find_file/2, mark/1, other_window/1, two_windows/1, clear_input/1, carriage_return/1 (input-line end; demons in pimfep and pimmcsp), exception/2 (show an error message), method/3, refute/3, execute_command/2 | USAGE (ptf §2 proves carriage_return/1) |
| `pmacs_standard_editor` | the Pmacs editor proper, as subclassed by papyrus | select_buffer/1,2, list_buffers/1 (after-demons proved), two_windows/1, backward_character/1, goto_beginning/1, exchange_point/1, next_term/1, push_to_yank/3, write_file/4, cursor_with_mouse/1, show_menu/1 | USAGE (papyrus_src/demo/EDITOR/); most meanings INFERENCE from the name |
| `editor_text_buffer` | a named text buffer in the pool | c:create/4 `(#.., ^Buf, Name, Size)` (fails if Name exists); c:create/3 `(#.., ^Buf, Size)` unnamed; c:create_with_parameter/5; c:get_buffer_instance/3 `(#.., Name, ^Buf)`; c:get_buffer_instance_list/2; c:rename_buffer/3; c:kill/2. Instance: reset/1, assign/1, insert_string/2, move_to_last/1, current_position/2, move_begin_of_line/1, delete/3 | USAGE cal-esp/deb2.12/dmenu.esp:1214-1219 |
| `editor_main_window` | the Pmacs window class seen in document processing (`editor_main_window/5`, IPSJ 114012 Fig. 2) | get_interpreter/2, get_editor/2, clear_echo_area/1, get_with_prompt/3 | SCREENSHOT + USAGE |
| `editor_yank_buffer`, `named_yank_buffer_subsystem` | named yank (kill) buffers `class`, `file`, `package`, used by library_utility | c:get_named_yank/3, c:add_named_yank/3, c:named_yank_flag/2 | COPY cil/src/ds_bep.esp:2312, :3515 (notes: ifs_libshell.md §4.1.1); meanings INFERENCE |
| `with_pmacs_window` | mixin giving a frame a Pmacs pane | — | USAGE nature list: kappa.ptf class kappa##pb_status_window |

**`editor_text_buffer` navigation** (USAGE, `fixpoint_2026-11-24.md` round 1, `notes/fixpoint.tsv`).
MENDELS ZONE's scrolling window (`mendels/mendels/swindow.esp:240-300, 427`) draws a buffer line by
line with `move_to_first/1`, `current_position(B,^Pos)`, `see_current_line(B,^String)` (the current
line, position unchanged), `next_line(B,0)`, `previous_line(B,0)` and `move_to(B,Pos)`, and appends
with `move_to_last/1`, `insert_string(B,S)` and `:insert(B, key#lf)` for a newline.

**Screen form** (SCREENSHOT: IPSJ 36239 p5-6; IPSJ 114012 Fig. 2; esp.wmv@108-149):
- text pane;
- a reverse mode line, e.g. `PMACS(esp)[65,26] demo i3psi7::>sys>user>hiroyuki>demo.esp --74%--`, with these
  fields:
  - editor name;
  - major mode in parentheses;
  - `[a,b]`, meaning unknown (window size in characters? INFERENCE);
  - `*-n*`, the buffer number;
  - the path or buffer name;
  - `--Top--` / `--N%--`;
- an echo line below, e.g. `Visit File(move_win.esp):`, `Read! >sys>user>demo>8pzl.esp.1`, `Find File:`.

The video has round brackets `(87,26)`; the 1986 screenshots have `[48,17]`. VARIANT.

**EDITOR MENU** (pop-up; IPSJ 36239 p5, SCREENSHOT, 2.50): `ABORT`, `List Buffers`, `Save All Files`, `Set Font`,
`Set Echo Font`, `Set Window Size`, `From Whiteboard`, `To Whiteboard`. TM-229 p6 (2.x) has `Set Same Font` in place
of `Set Echo Font` and an illegible 7th item. VARIANT.

**Key bindings** (USAGE: 223 `:command` clauses; ifs_window.tsv kind=command):
- `:command(E, mouse#r, kappa_menu)` (kappa2/kappa2/utility/fmp/KMACS.ESP:67);
- `:control_c(E, control#"i", input_string)` (cal-esp/deb2.12/dedit.esp:105);
- `:control_x(E, control#"z", exit)` (dedit.esp:120).

Pmacs's own default bindings are not held (gap G6).

### 2.12 Notifiers and the demons that prove SIMPOS primaries

Rule (TM-388 §3.4): a held class that has a `before:` or `after:` demon on a selector, with no held primary anywhere
in its linearisation, **proves** that a SIMPOS class in its order supplies the primary (notes: ptf.md §2, USAGE).
Window rows:

| selector | demon kind | SIMPOS owner (requirements, or candidates) |
|---|---|---|
| c:create/3 | after | inferior_window, superior_window, pmacs_window, essential_window, standard_superior_window, standard_scrolling_menu, editor_main_window |
| c:create/4 | after | pmacs_window |
| c:create/2 | after | standard_io_buffer |
| c:initiate/2, c:initiate/3 | after | ? (scrolling_view_window; as_graphics_menu). INFERENCE: create calls `initiate` |
| kill/1 | before | superior_window, inferior_window, pmacs_window, standard_superior_window |
| activate/1 | before, after | superior_window, standard_superior_window, reshape_notifier |
| deactivate/1 | after | inferior_window |
| set_position/3 | after | inferior_window |
| has_been_reshaped/1 | after | reshape_notifier or the superior |
| has_been_selected/1 | after | select_notifier |
| read/2 | before | {with_click_information, with_key_select, superior_window} |
| close/1 | before, after | ? |
| select_item/4 | after | scrolling_on_off_menu (?) |
| clear/1, initial_set_default/1 | before / after | ? (as_graphics_menu) |
| putf/3, putl/2 | after | ? (pb_status_window) |
| carriage_return/1 | before, after | standard_editor |
| select_buffer/1,2, list_buffers/1 | after | pmacs_standard_editor |

**`has_been_reshaped/1`** is called after the user reshapes the window. Typical bodies call `:get_inside_size`, then
`:reshape(Child,X,Y,W,H)` for each pane (cal-esp/cal2.12/scawin.esp:68; paragraph what_shell_window, USAGE). kwic
refuses the reshape instead: it restores the saved size and shows ウインドウのサイズは変更出来ません ("the window
size cannot be changed") (kwic-esp-002/kwic-esp/src/windows.esp:51-57, USAGE).

### 2.13 Screen, bitmap, window_subsystem, fonts

| call | meaning | grade, cite |
|---|---|---|
| c:`get_size/3` on `#screen` `(^W,^H)` | screen size in dots (used to centre windows) | USAGE cal-esp/cal2.12/scawin.esp:219; pimfep (ptf) |
| c:`get_plane_count/2` on `#bitmap` | number of display planes; 1 = monochrome | USAGE gog-esp/DISPB1.ESP:36; paragraph (ptf) |
| c:`get_mouse/2` on `#bitmap_display` | the logical mouse object | USAGE kwic-esp-002/kwic-esp/src/windows.esp:110 |
| c:`system_font/2` on `#window_subsystem` | the default system font object | USAGE cal-esp/deb2.12/create.esp:299 |
| c:`add_icon/4` on `#window_subsystem` `(icon, "font:fmp.icon", Id)` | register an icon glyph file under a number, for `set_icon/2` | USAGE kappa2/kappa2/utility/fmp/FMP.ESP:41; kappa##kappaMDU (ptf) |
| c:`create/3` on `#font` `(#font, Path, ^F)` | load a font file into a font object. **Path second, output third**: the reverse of file streams | PRINTED TM-785 p37; SCREENSHOT TM-181 p4; USAGE (220 uses) |
| `#font_13` | a class object usable directly as a font: `font(#font_13)` | USAGE kappa (ptf.md W1). PROSE: default font, 13×19 cell (TM-125 p20; TM-115 p27) |
| `:pathname(F,^P)` on a font | its file path | USAGE pimfep get_font/3 (ptf) |
| c:`create/2` on `#font_editor`, then `:goal(FE)` | run the font editor inline | USAGE euod/DEF/def.esp:412-413 |
| c:`call_color_manipulator/2` on `#color_manipulator` | open the colour manipulator (INFERENCE) | UNSPECIFIED (9 uses); first use kappa2/kappa2/user_if/pb/pcn.esp:3210 |

Font files and names are in §3.6.

**Display depth** (USAGE, `fixpoint_2026-11-24.md` round 1). PIMOS's ESP profiler front end
(`pimos/src_util/paragraph/p_MAIN.esp:183-185`) reads `:get_parameter(#ipl, bmm_size, ^Code)`:
16#"07FF" means monochrome, 16#"0FFF" colour. Its PSI/UX patch (`p_ux_patch.esp`, "PIMOS v2.7
release, 1991.5.8 for PSI-UX") is a class `profiler_ux_patch` whose own `get_parameter/2` derives
the code from `:get_plane_count(#bitmap, N)`: 1 plane gives 07FF, 3 or 4 give 0FFF, 6 gives 17FF and
8 gives 1FFF. In the PSI/UX revisions of four other files (`p_hwin.esp:165-166`, `p_wwin.esp:153-154,
349-350`, `p_imag.esp:459-460`, all dated 1991), the line `:get_parameter(#ipl,bmm_size,Dev)` is
commented out and replaced by `:get_parameter(#profiler_ux_patch,Dev)` or by
`:get_plane_count(#bitmap,N)` directly (`p_v_imag.esp:111-117`, `p_imag.esp:597-616`). `p_MAIN.esp`
still calls `#ipl`. That the `ipl` parameter is wrong or absent on the PSI/UX is an INFERENCE from
these edits. The same file draws with `set_color_pair(W, 0, {{R,G,B},{R,G,B}})` (16-bit
components), `transfer/8` with the operations `copy`, `reverse` and `exclusive_or`,
`draw_filled_rectangle/8` with `reset`, `set` and `exclusive_or` and the pattern `light_paint`, and
`draw_string/6` with `set`.

**Screen width by machine** (USAGE, fixed-point round 6). DISC's display code keeps one live and
two commented-out versions of the same full-width `essential_scrolling_menu` create, each labelled
with its machine (`disc/exdisp.esp:35-37, 47-49`):
- `position(0,904), size(1600,216)` "for O-PSI" (live);
- `position(0,788), size(1280,156)` "for M-PSI";
- `position(0,805), size(1280,160)` "for PSI-UX".
DISC's INSTALL names its machine "OKI-PSI-II" (`disc/INSTALL:9`), so "O-PSI" is read as the Oki
PSI-II (INFERENCE, strong): its screen was 1,600 dots wide, and the PSI/UX's 1,280. "M-PSI" is
ambiguous. In other held code it means the Multi-PSI (`gog-kl1/ESP/FEP.ESP:32-34`,
`mmi/README:36`), whose front end is a PSI-II; it could also mean a Mitsubishi PSI-II. Either way
the screen is 1,280 wide.
That each pane ends at the bottom edge, which would make the heights 1,120, 944 and 965, is an
INFERENCE; `:get_size(#screen,...)` is the run-time source. One check agrees: kl1graph, a PIMOS
front end of 1992, makes its full-screen window `size(1280,944)` and fills `0,0,1280,944`
(`kl1graph/kl1graph/screen.esp:25,30`), which equals the "M-PSI" pane's 788+156.

### 2.14 Every class of the partition: the methods the held programs send to it

This table is generated from `coverage_window.tsv` by `tools/window_appendix_gen.py` (output in `coverage/out/`). The status letters
are explained in §0.1. Each method's meaning is in §2.1-§2.13 and in Appendix A. Rows marked "(nature or reference
only)" are mixins and bases known only from nature lists; §1.3 gives what is known of them.

| class | progs | tier | methods sent to it (`c:` class method; number = uses; status D DOC-class, d DOC-unowned, U USAGE, u USAGE-unowned, N NONE) |
|---|---|---|---|
| `standard_io_window` | 11 | A | c:`create/3` 149D, `putl/2` 220D, `kill/1` 110d, `show/1` 78d, `set_font/2` 77d, `activate/1` 55D, `draw_line/7` 55u, `draw_string/5` 34d, `draw_rectangle/5` 23d, `clear/1` 21U, `putf/3` 21U, `putl/1` 20U, `putb/3` 20U, `draw_filled_rectangle/8` 19U, `write_line_tail/4` 15U, `putt/2` 13U, `putf/2` 12U, `write_lines/2` 12d, `set_label_font/2` 12U, `set_title/2` 12d, `putt/4` 12U, `getl/2` 11U, `deactivate/1` 10d, `draw_string/4` 10d, `write_line/4` 9U, `draw_rectangle/7` 8N, `beep/1` 8U, `erase_cursor/1` 7d, `activate/2` 7U, `gett/2` 6D, `write/2` 6d, `getc/2` 5U, `read/2` 5d, `set_permission/2` 5U, `move_cursor/3` 4d, `set_border_width/2` 4d, `draw_filled_circle/7` 4N, `draw_circle/7` 4N, `read_sense/2` 3d, `set_color_pair/3` 3U, `write_line/2` 3d, `get_activity/2` 3N, `draw_elliptical_arc/10` 3N, `draw_string/6` 2u, `get_inside_size/3` 2d, `draw_line/6` 2N, `draw_arc/9` 2N, `set_position/3` 1D, `input_data/2` 1U, `clear_buffer/1` 1U, `get_cursor_position/3` 1U, `clear_line/1` 1d, `read_click_with_position/4` 1U, `draw_graph/2` 1N, `set_superior/2` 1d, `get_size/3` 1d, `expose/1` 1U |
| `standard_io_buffer` | 11 | A | c:`create/2` 124d, c:`create/3` 9d, `putf/3` 154u, `getl/2` 96u, `putt/2` 74u, `reset/1` 60u, `putl/2` 56u, `gett/2` 46u, `putf/2` 35u, `putb/3` 13u, `putt/4` 5u, `get_parsing_operator/2` 5N, `reread/1` 4N, `size/2` 4u, `getb/3` 4U, `putc/2` 4d, `gett/4` 4u, `get_unparsing_operator/2` 4N, `set_max_depth/2` 2N, `set_max_length/2` 2N, `close_output/1` 1N, `end_of_input/1` 1u, `putl/1` 1u |
| `standard_output_file` | 12 | A | c:`create/3` 106d, `putf/3` 142u, `putl/2` 98U, `close_output/1` 87N, `putf/2` 77u, `putt/2` 47u, `putb/3` 31u, `putc/2` 20d, `putt/4` 16u, `putl/1` 14u, `unquote_atom/1` 10u, `set_unparsing_operator/2` 1N |
| `standard_input_file` | 14 | A | c:`create/3` 145d, `close_input/1` 133N, `gett/2` 82u, `end_of_input/1` 53U, `getl/2` 22u, `get_parsing_operator/2` 13N, `gett/4` 7u, `getc/2` 5u, `set_parsing_operator/2` 4N, `getb/3` 2u |
| `pmacs_window` | 15 | A | c:`create/3` 75d, c:`create/4` 5U, c:`create_with_input/5` 4U, c:`refute/3` 1d, c:`get_slot/3` 1u, c:`set_slot/3` 1u, c:`create_with_input/4` 1U, `activate/1` 50d, `putf/3` 47u, `set_font/2` 41d, `putl/2` 39u, `kill/1` 28d, `flash/1` 26U, `getl/2` 24u, `set_title/2` 20d, `get_editor/2` 19U, `deactivate/1` 19d, `get_interpreter/2` 12U, `putt/2` 9u, `unquote_atom/1` 7U, `current_buffer/2` 6U, `putf/2` 6u, `putb/3` 5u, `putl/1` 5u, `set_size/3` 5d, `getc/2` 5u, `set_label_font/2` 5u, `gett/2` 3u, `putc/2` 3d, `read/2` 3d, `set_input_buffer/2` 2U, `show_buffer/1` 2U, `get_size/3` 2d, `has_been_reshaped/1` 2U, `set_name/2` 1u, `set_position/3` 1d, `view_previous_screen/1` 1N, `view_next_screen/1` 1N, `get_text_window/2` 1N, `input_data/2` 1u |
| `font` | 14 | A | c:`create/3` 220D |
| `inferior_window` | 13 | A | c:`create/3` 177d, `get_size/3` 42d, `deactivate/1` 21d, `kill/1` 17d, `set_position/3` 17d, `set_size/3` 13d, `get_position/3` 12d |
| `standard_menu` | 11 | A | c:`create/3` 51d, `activate/1` 101d, `read/2` 88d, `kill/1` 39d, `set_title/2` 25d, `deactivate/1` 14d, `clear_buffer/1` 5u, `activate/2` 4u, `set_item_status/3` 4U, `get_size/3` 4d, `set_font/2` 4d, `expose/1` 4u, `set_label_font/2` 2u, `set_name/2` 1u, `add_item/3` 1d, `read_with_click/3` 1U, `set_superior/2` 1d, `set_position/3` 1d, `delete_item/2` 1d, `show/1` 1d |
| `standard_temporary_menu` | 7 | A | c:`create/3` 64d, `kill/1` 43d, `read/2` 40d, `activate/1` 31d, `beep/1` 22u, `show/1` 11d, `set_font/2` 7d, `set_label_font/2` 5u, `hide/1` 4d, `set_title/2` 3d, `clear_items/1` 2u, `add_item/3` 2d, `deactivate/1` 1d |
| `standard_editor` | 8 | A | c:`create/4` 18u, `get_window/2` 126U, `current_buffer/2` 42u, `set_current_buffer/2` 20N, `clear_input/1` 12N, `get_slot/3` 8u, `other_window/1` 8N, `select_buffer/2` 8u, `mark/1` 4N, `refute/3` 4d, `exception/2` 4U, `method/3` 3U, `see_region/2` 2N, `execute_command/2` 2u, `replace_region/3` 1N, `mark_position/2` 1N, `carriage_return/1` 1U, `view_two_windows/1` 1N, `beginning_of_line/1` 1N, `clear_buffer/1` 1u, `get_interface/2` 1N |
| `temporary_menu` | 10 | A | c:`create/3` 72d, `read/2` 31d, `show/1` 20d, `set_font/2` 20d, `set_label_font/2` 19u, `activate/1` 14d, `set_title/2` 13d, `kill/1` 11d, `clear_items/1` 5U, `add_items/3` 4u, `beep/1` 4u, `deactivate/1` 4d, `read/3` 2u, `hide/1` 1d |
| `pmacs_standard_editor` | 4 | A | `current_buffer/2` 88u, `get_window/2` 62u, `exception/2` 24u, `select_buffer/2` 18U, `insert/2` 9d, `find_file/2` 3N, `two_windows/1` 2U, `mark/1` 2N, `backward_character/1` 2N, `write_file/4` 1N, `push_to_yank/3` 1N, `clear_input/1` 1N, `cursor_with_mouse/1` 1N, `show_menu/1` 1N, `goto_beginning/1` 1N, `exchange_point/1` 1N, `next_term/1` 1N |
| `standard_superior_window` | 9 | A | c:`create/3` 41d, c:`refute/3` 1d, c:`get_slot/3` 1u, c:`set_slot/3` 1u, `get_inside_size/3` 19d, `get_size/3` 17d, `set_size/3` 15d, `kill/1` 15d, `show/1` 15d, `activate/1` 12d, `get_position/3` 9d, `get_border_width/2` 8N, `get_label_height/2` 8U, `set_title/2` 7d, `deactivate/1` 5d, `set_position/3` 4d, `hide/1` 4d, `read/3` 3u, `check_window/1` 1N, `get_margins/5` 1N, `set_label_font/2` 1u, `set_mode/2` 1N, `get_inside_units/3` 1u |
| `essential_window` | 6 | A | c:`create/3` 27d, `draw_line/8` 15d, `draw_string/5` 12d, `clear/1` 11u, `write_lines/2` 10d, `write_line/2` 10d, `get_inside_units/3` 8U, `erase_cursor/1` 8d, `get_size/3` 8d, `kill/1` 7d, `transfer/8` 7U, `activate/1` 6d, `set_size/3` 5d, `move_cursor/3` 4d, `set_font/2` 3d, `get_superior/2` 3N, `set_title/2` 3d, `get_font/2` 3U, `show/1` 3d, `deactivate/1` 2d, `set_name/2` 2u, `get_mouse_position/3` 2d, `activate/2` 2u, `background/2` 2u, `get_inside_size/3` 1d, `refute/3` 1d, `set_position/3` 1d, `draw_rectangle/8` 1d, `draw_filled_rectangle/6` 1u, `get_mouse_dot_position/3` 1N, `read/2` 1d, `write/2` 1d, `read_sense/2` 1d |
| `editor_text_buffer` | 10 | A | c:`create/4` 41U, c:`get_buffer_instance/3` 37U, c:`kill/2` 5N, c:`get_buffer_instance_list/2` 2N, c:`rename_buffer/3` 1U, c:`create/3` 1d, c:`create_with_parameter/5` 1U, `reset/1` 1U |
| `window_without_label` | 2 | A | c:`create/3` 19d, `write_line/2` 26d, `beep/1` 19u, `write_lines/2` 18d, `kill/1` 16d, `activate/1` 12d, `read/2` 10d, `background/2` 7U, `write_line/3` 5U, `erase_cursor/1` 4d, `activate/2` 4u, `set_superior/2` 3d, `set_font/2` 3d |
| `cal_window` | 2 | C | c:`create/3` 6d, `putl/1` 30u, `putl/2` 15u, `putb/3` 10u, `show/1` 9d, `activate/1` 8d, `get_fullpath_name/3` 6N, `putt/2` 5u, `set_title/2` 5d, `get_parsing_operator/2` 4N, `set_input_position/1` 4u, `flash/1` 2u, `clear_buffer/1` 2u, `gett/4` 2u, `show_buffer/1` 1u, `kill/1` 1d, `putf/3` 1u |
| `standard_scrolling_menu` | 7 | A | c:`create/3` 29d, `activate/1` 12d, `read/2` 11d, `kill/1` 11d, `add_items/3` 10U, `add_item/3` 6d, `activate/2` 4u, `retrieve_all_items/2` 3u, `set_name/2` 2u, `deactivate/1` 2d, `set_item_status/3` 2u, `change_item/3` 2u, `clear_items/1` 1u, `class_object/2` 1N, `enable_menu_help_click/1` 1u |
| `as_mouse_input` | 12 | A | (nature or reference only) |
| `standard_temporary_scrolling_menu` | 3 | A | c:`create/3` 28d, `read/2` 9d, `show/1` 8d, `kill/1` 8d, `add_items/3` 6u, `hide/1` 2d, `clear_items/1` 1u, `activate/1` 1d |
| `standard_window` | 5 | A | c:`create/3` 10D, `draw_string/5` 17d, `draw_line/8` 11D, `kill/1` 4d, `get_size/3` 3d, `set_size/3` 3d, `get_position/3` 3d, `write_line/2` 3d, `draw_filled_rectangle/6` 3U, `get_inside_size/3` 2d, `get_inside_units/3` 2u, `erase_cursor/1` 2d, `activate/1` 2d, `read/2` 2d, `set_title/2` 2d, `draw_rectangle/8` 2D, `set_margins/5` 1d, `set_position/3` 1d, `get_superior/2` 1N, `set_label_font/2` 1u, `read_click_with_position/4` 1u |
| `menu_with_superior_input_buffer` | 3 | A | c:`create/3` 20d, `activate/1` 13d, `kill/1` 9d, `change_item/3` 6u, `get_size/3` 2d, `set_size/3` 2d, `delete_item/2` 2d, `add_item/3` 2d, `deactivate/1` 2d, `clear_items/1` 1u, `add_items/3` 1u |
| `menu` | 6 | A | c:`create/3` 21d, `activate/1` 8d, `read/2` 7d, `kill/1` 5d, `set_font/2` 3d, `change_item/3` 2u, `deactivate/1` 2d, `set_superior/2` 2d, `get_size/3` 1d, `set_position/3` 1d, `retrieve_item/3` 1U, `set_label_font/2` 1u, `set_title/2` 1d |
| `with_superior_input_buffer` | 10 | A | (nature or reference only) |
| `essential_scrolling_menu` | 5 | A | c:`create/3` 19d, `activate/1` 9d, `set_superior/2` 8d, `get_size/3` 6d, `set_position/3` 4d, `clear_items/1` 3u, `add_items/3` 3u, `read/2` 1d, `set_font/2` 1d, `set_label_font/2` 1u, `set_title/2` 1d |
| `labeled_superior_window` | 3 | A | c:`create/3` 11d, `get_size/3` 10d, `activate/1` 4d, `kill/1` 4d, `get_border_width/2` 4N, `deactivate/1` 4d, `set_title/2` 4d, `read/3` 3U, `set_position/3` 3d, `get_inside_size/3` 3d, `get_label_height/2` 3u, `set_size/3` 3d, `set_label_font/2` 3u, `get_position/3` 2d, `get_margins/5` 2N, `set_label_flag/2` 1N |
| `with_border` | 9 | A | (nature or reference only) |
| `standard_choice_window` | 8 | A | c:`create/3` 19d, `kill/1` 5d, `read/2` 5d, `add_items/3` 3u, `activate/1` 3d, `deactivate/1` 3d, `activate/2` 3u, `clear_items/1` 1u, `set_name/2` 1u, `set_title/2` 1d |
| `superior_window` | 8 | A | c:`create/3` 16d, `get_inside_size/3` 7d, `kill/1` 5d, `activate/1` 3d, `hide/1` 2d, `show/1` 2d, `get_size/3` 2d, `read_click_with_position/5` 1U, `get_position/3` 1d, `set_position/3` 1d, `set_size/3` 1d |
| `standard_temporary_choice_window` | 4 | A | c:`create/3` 10d, `read/2` 10d, `show/1` 8d, `set_font/2` 7d, `activate/1` 2d, `kill/1` 2d, `beep/1` 1u, `retrieve_item/3` 1u, `change_item/3` 1u |
| `screen` | 9 | A | c:`get_size/3` 25d |
| `standard_temporary_window` | 2 | A | c:`create/3` 7d, `beep/1` 8u, `erase_cursor/1` 7d, `kill/1` 7d, `write_lines/2` 4d, `activate/1` 4d, `read/2` 4d, `draw_string/4` 1d |
| `as_single_select` | 10 | A | (nature or reference only) |
| `standard_popup_menu` | 2 | C | c:`create/3` 5d, `read/2` 6d, `add_items/3` 6u, `deactivate/1` 6d, `show/1` 5d, `clear_items/1` 4u, `set_title/2` 2d, `set_item_status/3` 2u, `hide/1` 1d, `add_item/3` 1d, `kill/1` 1d, `set_font/2` 1d, `activate/1` 1d |
| `as_superior` | 11 | A | (nature or reference only) |
| `as_input` | 11 | A | (nature or reference only) |
| `essential_temporary_window` | 1 | A | c:`create/3` 5d, `erase_cursor/1` 5d, `activate/1` 5d, `put_line/2` 5U, `beep/1` 5u, `read/2` 5d, `kill/1` 5d, `background/2` 4u |
| `reshape_notifier` | 8 | A | `get_size/3` 2d, `activate/1` 2d, `set_position/3` 2d, `set_size/3` 1d |
| `multi_column_menu` | 5 | B | c:`create/3` 11d, `get_size/3` 6d, `set_size/3` 4d, `activate/1` 2d, `kill/1` 2d, `set_superior/2` 1d, `deactivate/1` 1d, `read/2` 1d |
| `essential_scrolling_menu_with_superior_input_buffer` | 3 | A | c:`create/3` 10d, `set_title/2` 3d, `kill/1` 3d, `clear/1` 3u, `hide/1` 2d, `clear_items/1` 2u, `add_item/3` 2d, `show/1` 2d, `deactivate/1` 1d, `activate/1` 1d |
| `standard_multi_column_menu` | 7 | A | c:`create/3` 9d, `set_item_status/3` 5u, `deactivate/1` 3d, `activate/1` 2d, `set_size/3` 1d, `kill/1` 1d, `set_name/2` 1u, `get_item_status/3` 1U, `retrieve_all_items/2` 1u |
| `window_subsystem` | 4 | A | c:`add_icon/4` 10U, c:`system_font/2` 8U |
| `temporary_window` | 7 | A | c:`create/3` 17d, `activate/1` 4d, `kill/1` 3d |
| `font_13` | 5 | A | (nature or reference only) |
| `choice_window` | 4 | A | c:`create/3` 13d, `activate/1` 2d, `kill/1` 1d, `read/2` 1d |
| `with_icon` | 8 | A | (nature or reference only) |
| `as_markers` | 7 | A | `get_mouse_position/3` 3d, `draw_marker/2` 2d, `erase_marker/2` 2d, `get_marker_position/4` 2N, `warp_mouse/3` 2U, `set_marker_type/3` 2d, `read_sense/2` 1d, `move_marker/4` 1d |
| `net_talk_window` | 1 | D | c:`exe_help_menu/3` 7N, c:`wink/2` 1N |
| `as_menu_input` | 3 | A | (nature or reference only) |
| `labeled_sash` | 7 | A | (nature or reference only) |
| `scrolling_on_off_menu_with_superior_input_buffer` | 1 | A | c:`create/3` 5d, `add_items/3` 5u, `activate/1` 5d, `kill/1` 5d, `retrieve_all_items/2` 4U |
| `as_graphics` | 12 | A | (nature or reference only) |
| `as_output` | 10 | A | (nature or reference only) |
| `temporary_choice_window` | 1 | A | c:`create/3` 12d, `set_font/2` 1d, `set_label_font/2` 1u |
| `with_margin` | 7 | A | (nature or reference only) |
| `as_menu` | 7 | A | (nature or reference only) |
| `temporary_multiple_select_menu` | 3 | A | c:`create/3` 3d, `set_title/2` 3d, `read/2` 3d, `clear_items/1` 2u, `add_items/3` 2u, `show/1` 2d, `deactivate/1` 2d, `set_font/2` 1d, `set_label_font/2` 1u, `activate/1` 1d, `kill/1` 1d |
| `editor_main_window` | 1 | A | c:`create/3` 2d, `get_interpreter/2` 4u, `set_title/2` 2d, `set_font/2` 2d, `activate/1` 2d, `get_editor/2` 2u, `clear_echo_area/1` 2U, `get_with_prompt/3` 2U, `beep/1` 2u |
| `with_label` | 7 | A | (nature or reference only) |
| `standard_popup_choice_window` | 2 | C | c:`create/3` 3d, `change_item/3` 9U, `activate/1` 2d, `read/2` 2d, `deactivate/1` 2d |
| `with_click_information` | 5 | A | (nature or reference only) |
| `with_bell` | 4 | A | (nature or reference only) |
| `with_default_mouse` | 7 | A | (nature or reference only) |
| `sash` | 5 | A | (nature or reference only) |
| `kappaREP_select_menu` | 1 | D | c:`create/3` 2d, `add_items/3` 4u, `activate/1` 3d, `set_title/2` 2d, `read/2` 2d, `kill/1` 2d, `set_label_font/2` 1u, `set_font/2` 1d |
| `as_scrolling_menu` | 5 | A | (nature or reference only) |
| `color_manipulator` | 1 | A | c:`call_color_manipulator/2` 9N |
| `standard_popup_scrolling_menu` | 1 | D | c:`create/3` 2d, `clear_items/1` 2u, `set_size/3` 2d, `add_items/3` 2u, `show/1` 2d, `read/2` 2d, `hide/1` 2d |
| `with_shared_window` | 5 | A | `assign_window/1` 4N |
| `pmacs_request` | 3 | A | (nature or reference only) |
| `with_pmacs_window` | 6 | A | (nature or reference only) |
| `popup_choice_window` | 3 | A | c:`create/3` 4d, `set_label_font/2` 2u, `set_title/2` 2d, `set_font/2` 2d |
| `as_multiple_column` | 7 | A | (nature or reference only) |
| `multiple_select_scrolling_menu` | 1 | A | c:`create/3` 4d, `enable_menu_help_click/1` 3U, `set_help_font/2` 2N |
| `standard_temporary_multi_select_menu` | 2 | A | c:`create/3` 2d, `activate/1` 1d, `show/1` 1d, `read/2` 1d, `deactivate/1` 1d |
| `with_key_select` | 3 | A | (nature or reference only) |
| `essential_on_off_menu` | 1 | D | c:`create/3` 3d, `set_item_status/3` 5u, `read/2` 1d, `deactivate/1` 1d |
| `standard_popup_window` | 1 | D | c:`create/3` 1d, `draw_string/4` 3d, `draw_string/6` 3U, `erase_cursor/1` 1d, `draw_rectangle/8` 1d, `draw_line/8` 1d |
| `as_on_off_menu` | 4 | A | (nature or reference only) |
| `ras_with_input_window` | 1 | D | c:`new/2` 1d, `ask_what/3` 2N, `get_derived_rule_data/5` 1N, `initialize_input/2` 1N, `get_inference_rule/5` 1N, `assign_input_window/2` 1N |
| `as_standard_io_window` | 6 | A | (nature or reference only) |
| `temporary_multiple_select_multi_column_menu` | 1 | D | c:`create/3` 2d, `activate/1` 2d, `read/2` 2d, `set_item_status/3` 1u |
| `standard_output_text_buffer_accessor` | 2 | A | c:`create/3` 4d, `set_unparsing_operator/2` 1N |
| `as_scroll` | 4 | A | (nature or reference only) |
| `multiple_select_scrolling_menu_with_superior_input_buffer` | 1 | A | c:`create/3` 4d |
| `standard_multi_select_scrolling_menu` | 2 | A | c:`create/3` 2d, `add_items/3` 1u, `activate/2` 1u, `read/2` 1d, `kill/1` 1d |
| `as_input_buffer` | 4 | A | (nature or reference only) |
| `choice_window_with_no_execute` | 1 | A | c:`create/3` 1d, `set_size/3` 1d, `get_size/3` 1d, `deactivate/1` 1d, `kill/1` 1d, `activate/1` 1d |
| `standard_input_text_buffer_accessor` | 2 | A | c:`create/3` 2d, `close_input/1` 1N, `set_parsing_operator/2` 1N, `gett/2` 1u |
| `standard_popup_multi_select_scrolling_menu` | 1 | D | c:`create/3` 1d, `clear_items/1` 1u, `add_items/3` 1u, `show/1` 1d, `read/2` 1d, `hide/1` 1d |
| `editor_yank_buffer` | 1 | D | c:`get_named_yank/3` 2N, c:`add_named_yank/3` 1N |
| `standard_temporary_multi_column_menu` | 1 | D | c:`create/3` 1d, `show/1` 1d, `hide/1` 1d, `read/2` 1d, `kill/1` 1d |
| `cascade_index` | 1 | A | c:`create/3` 3d |
| `scrolling_on_off_menu` | 2 | A | c:`create/3` 3d |
| `as_multiple_select` | 4 | A | (nature or reference only) |
| `with_two_labels` | 3 | A | (nature or reference only) |
| `cal_op_menu` | 2 | C | c:`create/2` 2d |
| `temporary_single_scrolling_menu` | 3 | A | (nature or reference only) |
| `cal_file_menu` | 1 | X | c:`create_menu/3` 2N |
| `standard_popup_superior_window` | 1 | D | c:`create/3` 2d |
| `bitmap` | 2 | A | c:`get_plane_count/2` 2U |
| `temporary_scrolling_menu` | 1 | A | c:`create/3` 1d, `activate/1` 1d, `read/2` 1d |
| `temporary_standard_io_window` | 2 | A | c:`create/3` 2d |
| `as_choice` | 2 | A | (nature or reference only) |
| `cascade` | 1 | B? | c:`create/3` 2d |
| `temporary_choice_window_with_no_execute` | 1 | A | c:`create/3` 1d, `show/1` 1d, `read/2` 1d |
| `popup_window` | 3 | B | (nature or reference only) |
| `font_editor` | 1 | M | c:`create/2` 1d, `goal/1` 1D |
| `kakari_attribute_menu` | 1 | D | c:`create_window/2` 1u, `kill/1` 1d |
| `select_notifier` | 2 | A | (nature or reference only) |
| `with_no_execute_choice_item` | 2 | A | (nature or reference only) |
| `with_character` | 1 | A | c:`get_character_font/2` 1N |
| `temporary_multi_column_menu` | 1 | B | c:`create/3` 1d |
| `with_mouse_scroll` | 2 | A | (nature or reference only) |
| `editor_buffer_window` | 1 | D | (nature or reference only) |
| `named_yank_buffer_subsystem` | 1 | D | c:`named_yank_flag/2` 1N |
| `imi_attribute_menu` | 1 | D | c:`create_window/2` 1u |
| `imi_attribute_sub_menu` | 1 | D | c:`create_window/2` 1u |
| `multi_column_menu_with_superior_input_buffer` | 1 | D | c:`create/3` 1d |
| `utls_icon` | 1 | D | c:`get_and_set_icon_id/3` 1N |
| `standard_temporary_multi_select_scrolling_menu` | 1 | A | c:`create/3` 1d |
| `with_pane` | 2 | A | (nature or reference only) |
| `temporary_multiple_scrolling_menu` | 1 | A | (nature or reference only) |
| `bitmap_display` | 1 | M | c:`get_mouse/2` 1U |
| `gen_menu_win` | 1 | D | c:`gen_menu_win/3` 1N |
| `you_menu_win` | 1 | D | c:`you_menu_win/2` 1N |
| `standard_temporary_superior_window` | 1 | D | (nature or reference only) |
| `editor_command_interpreter` | 1 | D | (nature or reference only) |
| `ras_with_font_key_assignment` | 1 | D | (nature or reference only) |
| `with_cwi` | 1 | D | (nature or reference only) |
| `standard_multi_select_menu` | 1 | D | (nature or reference only) |
| `deexpose_notifier` | 1 | D | (nature or reference only) |
| `as_turning_menu` | 1 | D | (nature or reference only) |
| `multiple_select_menu` | 1 | A | (nature or reference only) |
| `multiple_select_multi_column_menu` | 1 | A | (nature or reference only) |

---

## 3. Data formats

### 3.1 Create arguments, per class

| class family | form | grade, cite |
|---|---|---|
| any window | c:`create(#C, Options, ^W)` or c:`create(#C, ^W)` | PRINTED-INTERFACE TM-125 p13; USAGE |
| `pmacs_window` | c:`create(#pmacs_window, Options, _, ^W)`; the 3rd argument is always unbound | USAGE kwic-esp src/inEditor1.esp:151, mendels comp_win.esp:54 (create/4; disc/exshow.esp:24 is create/3, corrected 2026-11-24); pimfep##pimos_window_editor (ptf) |
| frames with input superior | c:`create_with_input(#C, Options, [_], InputSup, ^W)` | USAGE txtstrct/ctx_system.esp:408 |
| `editor_text_buffer` | c:`create(#.., ^Buf, Name, Size)`; c:`create(#.., ^Buf, Size)` | USAGE cal-esp/deb2.12/dmenu.esp:1214 |
| `standard_input_file`, `standard_output_file` | c:`create(#.., ^Stream, Path)` | USAGE cal-esp/cal2.12/control.esp:190, :356 |
| `standard_io_buffer` | c:`create(#.., ^B)` | USAGE cal-esp/cal2.12/control.esp:409 |
| text-buffer accessors | c:`create(#.., Buffer, ^Acc)` | USAGE papyrus_src/demo/EDITOR/my_reader.esp.1:23 |
| `#font` | c:`create(#font, Path, ^F)` | PRINTED TM-785 p37; USAGE |
| `menu_item` (1985) | c:`create/6` | PRINTED-INTERFACE TR-046 p27 |

The output argument is 2nd for files and buffers, but last for windows and fonts. A stand-in must follow each family
(USAGE).

### 3.2 Create options

Options are a list of compound terms. TM-125 Table 1 (p14, PRINTED-INTERFACE, 1.0) is the printed set. Held counts
are from the IFS census (notes: ifs_window.md §2); ptf counts are from the compiled packages (notes: ptf.md W1). Each
USAGE row cites one example site.

| option | value | default (TM-125 p14) | held / ptf uses | grade, cite |
|---|---|---|---|---|
| `superior(W)` | parent window | the screen | 136 / 40 | PRINTED-INTERFACE TM-125 p14; USAGE cil/src/es_ins.esp:1115 |
| `position(X,Y)`, `position(manipulator)` | position in the superior; or the user places it | — | 312 / 117 (manipulator 45) | PRINTED-INTERFACE TM-125 p14; USAGE cil/src/ds_brs.esp:2546 |
| `size(W,H)`, `size(ch(C),ch(R))`, `size(manipulator)` | dots; characters; or the user sweeps it | — | 418 / 145 | PRINTED-INTERFACE TM-125 p14; USAGE cil/src/ms_cfm.esp:67, kwic-esp/src/displays.esp:129 |
| `title(S)` | label string | none | 364 / 73 | PRINTED-INTERFACE TM-125 p14 |
| `top_title(S)`, `bottom_title(S)` | the two labels | | few | PRINTED-INTERFACE TM-125 p14; USAGE kwic-esp/src/kwMan.esp:269 |
| `margins(L,R,H,T)` (1985), `margin(L,R,H,T)` (held) | margins in dots; **name VARIANT** | 1 | 17 / 2 | PRINTED-INTERFACE TM-125 p14; USAGE cil/src/ds_brs.esp:314 |
| `units(X,Y)` | coordinate unit | 1 dot | 0 | PRINTED-INTERFACE TM-125 p14 |
| `items_list(L)` | menu items (§3.3) | | 322 / 59 | PRINTED-INTERFACE TM-125 p14; USAGE cil/src/es_ins.esp:625 |
| `choice_list(L)` | choice items (§3.4) | | 50 / 23 | PRINTED-INTERFACE TM-125 p15; USAGE cil/src/es_ins.esp:1430 |
| `font(F)` | font object, or a font class (`#font_13`) | font_13 | 243 / 46 | USAGE kwic-esp/src/inSheet1.esp:303 |
| `label_font(F)` | label font | | 153 / 32 | USAGE cil/src/es_ins.esp:949 |
| `label_flag(on\|off)` | label shown | | 139 / 43 | USAGE cil/src/ds_brs.esp:314 |
| `nature([Mixin,...])` | extra natures added at create, e.g. `[with_superior_input_buffer, as_menu_input]` (whether this selects a class or mixes at run time is INFERENCE, gap G29) | | 206 / 24 | USAGE cil/src/ds_brs.esp:312 |
| `border_width(N)`, `border_flag(on\|off)` | border | 2 | 35 / 8; 29 / 33 | PRINTED-INTERFACE TM-125 p15 (width 2); USAGE cil/src/ds_brs.esp:167, :391 |
| `margin_flag(on\|off)` | margins | | 4 / 26 | USAGE kwic-esp/src/displays.esp:217 |
| `permission(out\|show)` | output permission (§4.1); held code uses only these two (63 `out`, 13 `show`) | | 33 / 12 | USAGE fuzclust/fuzclust/src/compare.comp:34 |
| `notified(IO)` | a window to notify (INFERENCE) | | 5 | USAGE cal-esp/deb2.12/winpar.esp:307 (comment) |
| `label_position(top\|bottom)`, `icon(..)` | | | 2, few | USAGE kwic-esp/src/inEditor1.esp:151, :139 |
| `menu_font(F)`, `echo_area(..)` | | | few | USAGE gog-esp/DISPB1.ESP:168; cil/src/ds_brs.esp:92 |
| `mouse_marker(N)` | mouse-cursor shape | | few | USAGE kwic-esp/src/scrolls.esp:131 |
| `editor(#C)`, `buffer_class(#C)`, `buffer(B)`, `status_window(off)`, `echo_area_pmacs(on)` | pmacs_window only | | | USAGE pimfep##pimos_window_editor (ptf; notes: ptf.md W6) |

### 3.3 Menu item vectors

The 4-field form is PRINTED-INTERFACE (TM-125 p14). The kinds and counts are USAGE (notes: ifs_window.md §3; example
cil/src/es_ins.esp:625).

`{Label, Kind, Value, Documentation}`
- **Label**: a string.
- **Value**: what `read` returns.
- **Documentation**: a string shown on the status line while the item is under the mouse (TM-125 p14). This settles
  the ptf.md open question about the 4th field.
- **Kind**:

| kind | uses | meaning |
|---|---|---|
| `common` | 1627 | ordinary choice |
| `no_select` | 382 | display-only line (kappa2/kappa2/user_if/pb/pbm.esp:40) |
| `string` | 283 | entry with text (INFERENCE, gap G19) |
| `choose` | 148 | sub-choice |
| `switch` | 76 | toggle (on/off menus) |
| `boolean` | 35 | |
| `do_it` | 26 | finish multiple selection |
| `abort` | 23 | cancel |
| `pick_up` | 5 | toggle in multiple-select |

On/off menus take five fields: `{L, common|switch|no_select, Id, Doc, on|off}` (USAGE knov/src/system/ap.esp:75-83).
Multi-column menus take a list of lists (SCREENSHOT TM-115 p26; USAGE).

### 3.4 Choice-list items

| form | meaning | grade, cite |
|---|---|---|
| `{Label, string, Key, Width, Default, Doc}` | text field of Width characters | PRINTED-INTERFACE TM-125 p15 (fields item_string, item_type, elements_list, initial_element, documentation); USAGE cil/src/es_ins.esp:1430 |
| `{Label, string, no_select, Key, Width, Default, Doc}` | display-only text field (the ptf "7-element label line") | USAGE (notes: ptf.md W2) |
| `{Label, boolean, Key, _, true\|false, Doc}` | yes/no field | USAGE (notes: ifs_window.md §3) |
| `{Label, choose, Key, [{Lab,Val},...], Default, Doc}` | one-of-N field; the current value is reverse video | SCREENSHOT TM-125 p7 Fig. 4; USAGE |
| `{"do_it", do_it, _, _}`, `{"clear", abort, _, _}` | buttons | USAGE (notes: ifs_window.md §3) |

`read` returns `abort` or `[{Key,Value},...]` (USAGE, notes: ifs_window.md §3).

### 3.5 Event codes and `#` constants

The macro families are defined for the expander in cil/src/cil_esp.esp:120-254 (USAGE). The member names are seen at
call sites (notes: ifs_window.md §4).

| family | members seen | meaning | grade |
|---|---|---|---|
| `mouse#` | `l`, `ll`, `m`, `mm`, `r`, `rr` | left, middle, right; doubled = double click | USAGE; TR-046 p28 (`mouse#rr`) |
| `key#` | `lf`, `cr`, `del`, `enter`, `esc`, `tab`, `bs`, `bell`, `up`, `down`, `left`, `right`, `abort`, `help` (`etx` in CESP) | named keys | USAGE; IPSJ 122601 p2 (`etx`) |
| `pf#N` | 0-18 | function keys. `pf#8` = help and `pf#9` = abort per comments at euod/DEF/def.esp:1553-1554 | USAGE |
| `control#"c"`, `meta#"c"`, `control_meta#"c"` | | modified characters | USAGE; PRINTED TR-046 p28 |
| `control_pf#`, `meta_pf#`, `control_meta_pf#`, `keypad#` | | modified function keys, keypad | USAGE cil/src/cil_esp.esp:120-254 |
| `#"c"` | | a character code | USAGE cil/src/ds_bep.esp:3100 (`#">"`) |
| `string#`, `jis#`, `ascii#`, `words#`, `double_bytes#`, `bytes#`, `bits#`, `Radix#String` | | constants of other types | USAGE cil/src/cil_esp.esp:120-254 |
| `standard#input`, `standard#output`, `standard#message` | | the process's standard streams, expanded to `:standard_input(:self(#simpos##process))` | USAGE cil/src/cil_esp.esp:120-254 |

The numeric code values are not held: the macros delegate to the expander (gap G2). TM-125 p18 prints the 1985 mouse
codes as `mouse$r`, `mouse$m`, `mouse$l`, `mouse$rr`. **VARIANT** `$` vs `#`.

The pimfep supervisor dispatches on mouse codes (USAGE, pimfep##pimos_fep_superviser refute_command/3 (ptf); notes:
ptf.md W4):
- `mouse#l`: hide;
- `mouse#ll`: command menu;
- `mouse#m`: `set_position(W,manipulator,_)`;
- `mouse#mm`: close;
- `mouse#r`: exit.

### 3.6 Fonts and icons

| version | form | grade, cite |
|---|---|---|
| 1.0 (1985) | two files per font, `.bin`: header and patterns; read through `as_general_font` methods | PRINTED-INTERFACE TM-115 p13-14 |
| 1987 (4D-3) | one variable-length binary file in three parts: header, per-character index, patterns; at most 65,536 characters | PROSE IPSJ 114008 p1 §2 |
| held | `.font` files. The `f822` layout is decoded by hand from gog-esp/suuji.font; the 32-bit family (kappa2, euod, fuzclust) is not (gap G9) | USAGE (notes: tm115.md §(a), item 7) |

**Font names.** `tiny_7`, `test_11`, `font_13` (13×19 cell), `cap_11`, `kanji_16`, `kanji_28`, `grape_16/28`; label
fonts `ank_24`, `kanji_24` (TM-125 p7 Fig. 4). Paths: `"font:test_11.font"`, `"font:kanji_16.font"`,
`">sys>font>kanji_16.font"` (USAGE; notes: ifs_window.md §6). The 13×19 size is PROSE TM-125 p20.

**Icons.** Icons are glyphs in a font file (`"font:fmp.icon"`) registered with `add_icon`
(USAGE kappa2/kappa2/utility/fmp/FMP.ESP:41). The video shows no iconified window (SCREENSHOT negative, notes:
video.md §2).

### 3.7 Colour (PSI-II, 1989)

PROSE Giho 8907 p34-35 (Mitsubishi Denki Giho 63(7) pp.549-553, Fig. 5):
- a colour window has a palette of colour pairs, each two RGB colours, mutually inverse;
- programs give colours by colour number (Fig. 5: numbers 0 and 1 = pair 0, 2 and 3 = pair 1);
- a window with one pair is monochrome;
- children can share the parent's palette.

| method | form | grade, cite |
|---|---|---|
| `set_color_pair/3` | `(W, EvenNo, 0 \| {{R,G,B},{R,G,B}})` | PRINTED TM-785 p31; USAGE kappa2/kappa2/user_if/pb/pdim.esp:590 (16-bit RGB) |
| c:`get_plane_count/2` on `#bitmap` | number of planes | USAGE gog-esp/DISPB1.ESP:36 |

---

## 4. Screen behaviour and menus

### 4.1 Window states and I/O permission

**States.** The variants are kept apart (notes: trtm_window.md W3):

| source | states | grade |
|---|---|---|
| TR-046 Table 2 (1984), PDF p23 | SELECTED, SHOWN, EXPOSED, OVERLAPPED, DEACTIVATED, each with a keyboard/mouse/output rule | PRINTED-INTERFACE |
| TR-057 Table 3-1 (1984), PDF p6 | Selected, Shown, Exposed, **Deexposed**, Deactivated | PRINTED-INTERFACE |
| TR-055 (1984) PDF p18-19 | shown (one selected), de-exposed, de-activated | PROSE |
| TM-125 (1985) p5-6 | exposed/deexposed (among siblings) × shown/unshown (window and all ancestors exposed) | PROSE |
| TM-126 (1985) p7 | fully visible or not; the selected window's cursor blinks; mouse clicks go to the fully visible window under the mouse | PROSE (TRANSLATION) |
| TM-225 (1986, 2.5) p11 | the selected window has keyboard input and is top of the stack; mouse input goes to the window under the mouse marker | PROSE (TRANSLATION) |

**Output permission** decides what happens when a process writes to a window that is not fully shown:

| TM-125 p6 (1985) | TM-225 p10-11 (1986) | meaning |
|---|---|---|
| WAIT | ① (**default**) | the writer waits until the window is shown |
| NOTIFY | ④ | a temporary notify window lets the user choose WAIT or SHOW; needs as_notification |
| OUTPUT | ② | write into the window's save area; only the shown part appears |
| SHOW | ③ | force the window shown, then write; this changes the selected window |

Grade: PROSE. The ATTRIBUTE dialogue lists `out / wait / show / notify` (SCREENSHOT TM-125 p7 Fig. 4). Held code
spells the option `permission(out)` (63 sites) or `permission(show)` (13 sites), and nothing else (USAGE
fuzclust/fuzclust/src/compare.comp:34; gog-esp/DISPB3.ESP:377).

**Implementation** (PROSE TM-225 p10; TM-126 p5):
- a shown window draws into frame memory;
- a hidden window's image is kept in a per-window save area in bitmap memory;
- restacking copies between the save areas and frame memory.

**1.0 rules** (PROSE TM-115 p29, p111):
- only the selected window can be read;
- a window may not leave the screen;
- uncovered areas are not cleared.

### 4.2 The screen and the status line

**Screen size.** VARIANT by source (notes: trtm_window.md Q5; trtm_manuals.md):

| size | source |
|---|---|
| 1200×912 or 1280×864 | TR-046 p6 (1984) |
| 1200×900 | TM-153 |
| 1280×864 | TM-224 p11 (1986) |
| 1280×944 | TM-785 p9 (5.0, default drawing size equals the screen size) |

Held code asks `:get_size(#screen,W,H)` (USAGE cal-esp/cal2.12/scawin.esp:219).

**Screen.** White background, black text; overlapping windows with thin single-line borders and no shadows
(SCREENSHOT simpos.wmv@0-10, esp.wmv@110-121).

**Status line.** A black reverse band across the **bottom** of the screen, below all windows. TM-126 p7 says the
selected window's name is shown on the bottom line (PROSE). Contents by version (all SCREENSHOT):

| version | left | middle | right | cite |
|---|---|---|---|---|
| 2.50 (1986) | `USER : KCM` / `SIMPOS Version 2.50` | reverse box with a window name | | melco.wmv@50, @157-158 |
| A00 (video) | `USER : demo` / `SIMPOS Version A00` | box with `editor_wo…` | illegible box and field | esp.wmv@108-109; icot.wmv@22 |
| 4.2 (1989) | `USER : demo` / `SIMPOS Version 4.2` | `screen` / `editor_buffer_window/19` | inverse boxes `SWAPPED`, `spool`; date `12-Sep-89 Tuesday 10:25:41` | FSTJ 26(1) p99 Fig. 9 |

INFERENCE: the middle box names the window that owns keyboard input. The notes also read it as the object under the
mouse (ipsj.md, FSTJ entry). VARIANT, gap G14.

**Kana-kanji band.** The same bottom band is used for conversion (SCREENSHOT simpos.wmv@108-113):
- line 1 echoes the romaji after `>`, then hiragana, then a numbered candidate list;
- line 2 is the key help `>MENU(PF16) PF10=ON_OFF, PF0-PF6=MANAGE…` (truncated).

The chosen kanji is inserted into the target window (simpos.wmv@114-116).

### 4.3 Labels, borders, names, cursors, icons

**Labels.** A strip inside the top border, separated by a rule, holding the window name left-aligned in the small font
(SCREENSHOT simpos.wmv@0, @117, @124). Labels also occur at the bottom (melco.wmv@54-55; PRINTED-INTERFACE TM-125
p15 `set_label_position`). With `background(W,black)` the label bar is black with white text (esp.wmv@118-121).

**Borders.** Default 2 dots (PRINTED-INTERFACE TM-125 p15).

**Window names.** VARIANT:
- `<program>_<n>` with a per-program counter: `debugger_1`, `librarian_2`, `pmacs_1`, `file_manipulator_2` (SCREENSHOT
  simpos.wmv@0, @56, @117);
- `<class>/<N>`: `editor_buffer_window/19` (SCREENSHOT FSTJ 26(1) p99, 4.2).

**Cursors** (SCREENSHOT):
- text cursor: a solid block (simpos.wmv@0, @114);
- mouse cursor: a small arrow (esp.wmv@120), with a `×` mark by the highlighted menu item (simpos.wmv@132).

**Icons.** `with_icon` lets a window close to an icon. kappa swaps window and icon in `before:`/`after:close` demons
(USAGE kappa2/kappa2/user_if/pb/MOPMWIN.ESP:31-37). No icon appears in the video (SCREENSHOT negative).

### 4.4 The window manipulator

| version | items, verbatim | grade |
|---|---|---|
| 1.0 (TM-125 p8) | `SHOW`, `HIDE`, `RESHAPE`, `MOVE`, `EXPAND`, `MENU`, `PERMISSION`, `ATTRIBUTE`, `HARDCOPY`, `SUPERIOR`, `INFERIOR`, `EXIT` | PRINTED-INTERFACE |
| A00 (video) | `SHOW`, `HIDE`, `RESHAPE`, `MOVE`, `EXPAND`, `MENU`, `PERM…`, `ATT…` (cut off by the frame; possibly more) | SCREENSHOT simpos.wmv@117-118 |

**Item meanings** (TM-125 p8, PRINTED-INTERFACE):

| item | effect |
|---|---|
| SHOW | show the whole of a partly shown window |
| HIDE | move it to the bottom of the window list |
| RESHAPE | point at the top-left and bottom-right corners with the mouse |
| MOVE | move by mouse |
| EXPAND | as large as possible without hiding a fully shown window |
| MENU | choose a window from a submenu of windows |
| PERMISSION | set output permission from a submenu |
| ATTRIBUTE | the choice window below |
| HARDCOPY | print |
| SUPERIOR / INFERIOR | move the "editing base" up or down the hierarchy |
| EXIT | leave |

TM-125 says the manipulator is invoked from the system menu. 2.10 lists `window manipulator` in the system menu
(TM-181 p3).

**The ATTRIBUTE choice window** (SCREENSHOT TM-125 p7 Fig. 4):

| field | values |
|---|---|
| `SIZE` | WIDTH / HEIGHT |
| `POSITION` | X / Y |
| `MOUSE_MARKER` | |
| `LABEL` | |
| `NAME` | |
| `MARGIN` | LEFT / RIGHT / HEAD / TAIL = 1 |
| `BORDER` | 2 |
| `PERMISSION` | out / wait / show / notify (wait current) |
| `FONT` | |
| `LABEL_FONT` | ank_24 / kanji_24 |
| `LABEL_POSITION` | top / bottom |
| `BACKGROUND` | white / black |
| buttons | do_it / abort |

### 4.5 The system menu, window side

**Opening it.** Two right clicks anywhere (`mouse#rr`; TM-143 p3, TM-181 p3, PROSE). TR-046 p28 also binds
`control#"s"` to it, but the same table binds `control#"s"` to `status` first (§5.1). VARIANT, noted in Appendix B.

**Contents** by version (PROSE/SCREENSHOT TM-143 p3, TM-181 p3; SCREENSHOT simpos.wmv@9.6-11.3). The item lists are
in `shell.md`, which owns the system menu. Login initialisation adds items (TM-143 p3, TM-181 p3, TM-229 p5-6).

**Dialogue** (SCREENSHOT simpos.wmv@10.9-56, prolog.wmv@14-15; sequence INFERENCE):
1. choose a program;
2. a pop-up titled with the program name, or `WHICH ?`, offers `create` and `kill`;
3. on `create`, sweep the new window's outline with the mouse (rubber band); the window appears at that size and
   place.

**Look.**
- Pop-up menus have a title bar (`SYSTEM MENU`, `top menu`, `Debugger Menu`, `Select files`, `WHICH ?`) above centred
  items (SCREENSHOT, notes: video.md §2).
- The item under the mouse is boxed (SCREENSHOT simpos.wmv@10.9, @60, @117, @132).

### 4.6 Editor screen

See §2.11 for the mode line, the echo line and the EDITOR MENU.

---

## 5. Command language and dialogues (window side)

### 5.1 The Coordinator's key translation table

PRINTED TR-046 p28; TR-061 p13. The table is `default_translation_table`, looked up as
`:look_up(Table, Window, Key, ^Dest, ^Command, ^Help)`. Commands go to `#coordinator` as `{Cmd, E_process, A3, A4}`.

| key | command | meaning |
|---|---|---|
| `control#"k"` | kill | kill the process |
| `control#"l"` | lull | suspend it |
| `control#"a"` | arouse | resume it |
| `control#"s"` | status | (listed again below as invoke_system_menu, shadowed) |
| `mouse#l` | visit | select the window |
| `control#"m"` | memorize | |
| `control#"b"` | broadcast | |
| `control#"v"` | remember | |
| `control#"s"`, `mouse#rr` | invoke_system_menu | |
| `control#"r"` | read whiteboard | |
| `control#"w"` | write whiteboard | |
| default | pass-through | "send character as it is" |

### 5.2 Pmacs bindings

Pmacs binds keys by `:command` clauses (§2.11). The default table is not held (gap G6). User extensions bind
(USAGE):
- `control#` letters;
- the `control_c` and `control_x` prefix tables (cal-esp/deb2.12/dedit.esp:105, :120);
- `mouse#r` (kappa2/kappa2/utility/fmp/KMACS.ESP:67).

### 5.3 Mouse gestures

| gesture | effect | grade, source |
|---|---|---|
| left click in an unselected window | select it (1.0) | PROSE TM-115 p111 |
| `mouse#l` | visit (select) | PRINTED TR-046 p28 |
| `mouse#rr` anywhere | system menu | PRINTED TR-046 p28; PROSE TM-143 p3 |
| middle on a pimfep window | move | USAGE pimfep##pimos_fep_superviser (ptf) |
| middle double on a pimfep window | close | USAGE pimfep##pimos_fep_superviser (ptf) |
| right on a pimfep window | exit | USAGE pimfep##pimos_fep_superviser (ptf) |
| click on a menu item | `read` returns its Value | PRINTED-INTERFACE TM-125 p18 |
| leave a temporary menu | `read` returns `abort` (TM-125) or fails (1.0) | PRINTED-INTERFACE TM-125 p18; PROSE TM-115 p93 |
| sweep two corners | RESHAPE, or place a new window | PRINTED-INTERFACE TM-125 p8; SCREENSHOT simpos.wmv@53-56 |

---

## 6. Error and status messages (window side)

| text | where | grade, cite |
|---|---|---|
| ウインドウのサイズは変更出来ません ("the window size cannot be changed") | kwic reshape refusal | USAGE kwic-esp-002/kwic-esp/src/windows.esp:55 |
| `illegal command` | library_utility, unknown menu command | COPY cil/src/ds_bep.esp:3387 |
| `aborted.` | library_utility, abort polled during a long operation | COPY cil/src/ds_bep.esp:3488 |
| `This system has no librarian window interface!!` | raised as `#library_error` | COPY cil/src/ds_bep.esp:1856 |
| `DUPLICATED ERROR` | menu title, with one `no_select` item, when a kappa tool is already running | USAGE kappa2/kappa2/user_if/pb/pbm.esp:40 |
| `> Success !!` | answer line after a command in the 1.0 shell or debugger | SCREENSHOT TM-134 p67-71 (notes: trtm_progsys.md) |
| login prompts, `Unknown FEP node name.`, `Illigal input.` (sic) | pimfep login requester | USAGE pimfep (ptf; fep_services.md §6.9) |

A 1.0 write fails if the font has no glyph for a code (PROSE TM-112 p16).

---

## 7. Stand-in notes, in build order

Everything in this section is INFERENCE: a plan derived from the use counts above, not from SIMPOS.

1. **The standard I/O protocol on a buffer** (§2.4, §2.8).
   - Build `standard_io_buffer` first: putl, putf, putt, putb, putc, getl, gett, getc, getb, reread, size, reset.
   - Then the two file classes, keeping their argument order and their failure on a missing file.
   - Weight: 440 uses; every later piece reuses it.
2. **One text window** (`standard_io_window`) over a character grid.
   - Life cycle (§2.1): create/3 with the §3.2 options, activate, show, hide, kill.
   - Text: write, write_line, move_cursor, clear, beep, flash.
   - The §2.4 protocol, delegating to (1).
   - Ignore permission: treat everything as `out`.
3. **Input** (§2.7): read/2, read_sense/2 (`'$$nil'`), read_with_click/3, and the `#` constants. Choose the numeric
   codes locally until G2 settles them, and keep them behind the expander.
4. **Menus and choice windows** (§2.9-§2.10, §3.3-§3.4): read returns the Value or `abort`. 1627 `common` items
   dominate, so a single-column menu with `common`/`no_select` covers most programs.
5. **Pmacs window** (§2.11): `pmacs_window` + `standard_editor` + `editor_text_buffer` with the exshow sequence. This
   is what pimfep needs.
6. **Graphics** (§2.5): draw_line/5-8, draw_rectangle, draw_string/4,5, filled shapes, transfer and copy, on a bitmap.
7. **Demons and notifiers** (§2.12): call `has_been_reshaped` after reshape. Honour after:create and before:kill in
   user subclasses (the ESP compiler supplies demons).
8. **Screen chrome** (§4): status line, labels, manipulator menu, ATTRIBUTE dialog, system-menu hooks.
9. **Coordinator translation table** (§5.1).

Keep every unimplemented selector failing loud. The 56 UNSPECIFIED selectors (Appendix A) are the first candidates.

---

## 8. Coverage

Command (from `pim/docs/simpos/subsystems/`): `python3 -I tools/coverage.py`. Output for this partition (676 required window
methods, 7162 uses):

| status | methods | % | uses | % |
|---|---|---|---|---|
| DOC-class (printed for the class) | 15 | 2.2 | 1071 | 15.0 |
| DOC-unowned (printed, owner not stated) | 369 | 54.6 | 3320 | 46.4 |
| USAGE (owner known from use) | 74 | 10.9 | 812 | 11.3 |
| USAGE-unowned | 138 | 20.4 | 1522 | 21.3 |
| NONE | 80 | 11.8 | 437 | 6.1 |
| **documented (DOC-\*)** | 384 | 56.8 | 4391 | 61.3 |
| **any evidence** | 596 | 88.2 | 6725 | 93.9 |

These are the counts after the second sweep (`sweep_2026-11-24.md` §4). Before it they were: DOC-class 10 (675
uses), DOC-unowned 365 (3432), USAGE-unowned 147 (1806). The change comes from the 1990 ESP manual. Its
`standard_io_buffer` example makes create/putl/gett/putt/getl DOC-class. Its `get_slot`/`set_slot` on class `class`
adds 4 DOC-unowned rows on window classes. The CESP-substitute rows for `as_markers`/`with_margin` are not counted.

**Distortions.** These numbers are a name match, not a semantic match. Report and correct them by hand:
- **Overcount.** 440 uses on non-window classes count as DOC-unowned only because a window method of the same name is
  printed. That is about 6 points of the 57.3%:
  - standard_input_file 145;
  - standard_io_buffer 137;
  - standard_output_file 126;
  - screen 25;
  - accessors 6;
  - editor_text_buffer 1.

  Their behaviour is known from USAGE only (§2.8).
- **Undercount.** `draw_circle/7` on standard_io_window is NONE, though WINCS prints it on `as_graphics`. There may be
  others where the printed owner is a mixin the census does not link.
- **Nature-only.** 48 of the partition's 135 classes have no required methods. They are known only as nature-list
  entries. The heaviest are as_mouse_input 12 programs, as_graphics 12, as_superior 11, as_input 11,
  with_superior_input_buffer 10, as_single_select 10, as_output 10, with_border 9 and with_icon 8 (full table in
  §1.3). Their methods are counted under the composites that use them.
- **UNSPECIFIED.** After excluding evidence from other partitions and from application classes, 65 of the 194 distinct
  selectors have no meaning-bearing evidence in the notes. Nine of those (draw_rectangle/7, draw_line/6, draw_graph/2,
  reread/1, set_name/2, kill/2, get_buffer_instance_list/2, set_current_buffer/2, find_file/2) are described in §2
  from their call sites. That leaves **56 UNSPECIFIED** (`coverage/out/unspec.tsv`), marked in Appendix A with
  their use counts and first use.

Other partitions for scale: librarian 114 methods, shell 115, other 531.

---

## Appendix B. Variants and inconsistencies found

| item | variants | follow |
|---|---|---|
| margins option | `margins(..)` TM-125 vs `margin(..)` held | held |
| mouse codes | `mouse$r` TM-125 vs `mouse#r` held | held |
| draw_string/5 last argument | Op (TM-125) vs Font (held) | held |
| draw_line/6 last argument | Op (paragraph, ptf) vs Width (gog-esp/KE_WINDOW.ESP:453) | both |
| `control#"s"` | `status` and `invoke_system_menu` in the same TR-046 p28 table | unsettled; use `mouse#rr` |
| status-line position | bottom band (video; TM-126 p7) | bottom |
| screen size | 1200×912, 1280×864, 1200×900, 1280×944 | ask `#screen` |
| status-line window box | selected window vs window under the mouse | unsettled |
| menu highlight | blackened (1.0) vs boxed (2.50, A00) | boxed |
| window naming | `<prog>_<n>` vs `<class>/<N>` | unsettled |
| Pmacs mode line size | `[w,h]` (1986) vs `(w,h)` (video) | unsettled |
| EDITOR MENU 5th item | `Set Echo Font` (2.50) vs `Set Same Font` (TM-229) | unsettled |
| inside unit default | font_13 cell (TM-115) vs 1 dot (TM-125) | per version |
| unselected-window reads | forbidden in 1.0; used freely in held | held |
| temporary menu exit | read fails (1.0) vs returns `abort` (TM-125) | `abort` |
| video release tag | A00 vs B00 in notes | unsettled |
| notes errors | ifs_window.md: user_window in no partition (it is in partition_shell); ptf.md: menu-item 4th field unknown (TM-125: documentation); trtm_manuals: draw_filled_circle held only /5 (both /5 and /7 held) | corrected here |

---

## Appendix A. Selector dictionary (generated)

Generated by `tools/window_appendix_gen.py` from `coverage_window.tsv`, the notes TSVs and `required/requirements.tsv`.
Each row has:
- the best documented evidence and the best usage evidence;
- the class the evidence is about, in brackets;
- the grade;
- the citation, with the notes file in parentheses;
- the version.

`″` marks the second line of evidence for the same selector. **UNSPECIFIED** = a required selector with no evidence of
meaning.

| selector | c/i | uses | meaning | grade | citation (notes) | version |
|---|---|---|---|---|---|---|
| `activate/1` | i | 387 | [standard_io_window] display the window on screen; held: MATCH | PRINTED | Giho 8609 p19-20 (ipsj) | 2.0 (1986) |
| ″ |  |  | [superior_window] before+after-demon in held pimmcsp##csp_inspector_menu with no held primary: SIMPOS supplies the primary (one of with_click_informa… | USAGE | pimmcsp.ptf class pimmcsp##csp_inspector_menu (ptf) | ptf 1991 |
| `activate/2` | i | 25 | [standard_io_window] :activate(W,mouse): activate at mouse position | USAGE | kwic-esp-002/kwic-esp/src/windows.esp:140 (ifs_window) | held 3.x-7.x |
| `add_icon/4` | c | 10 | [window_subsystem] sent by kappa##kappaMDU instance create_windows/2; args: icon, string#"font:mdu.icon", 21 | USAGE | kappa.ptf class kappa##kappaMDU instance create_windows/2 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1992 |
| `add_item/3` | i | 14 | [window] :add_item(Menu,Item,Position) single-column menu; Item = item vector; Position 0..number of items [possible defining mixin: menu -- INFERENC… | PRINTED-INTERFACE | TM-125 p15 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [{with_margin\|with_border\|as_menu\|as_single_select\|as_mouse_input\|with_bell\|temporary_window}] sent to an instance of held kappa##kappa_purge_w… | USAGE | kappa.ptf class kappa##kappa_purge_window instance set_message/2 (kl0 run) (ptf) | ptf 1992 |
| `add_items/3` | i | 48 | [{with_superior_input_buffer\|as_menu_input\|menu}] sent to an instance of held pimmcsp##csp_inspector_com_menu, whose held classes define no add_ite… | USAGE | pimmcsp.ptf class pimmcsp##csp_inspector_com_menu instance inspector_menu1/1 (kl0 run) (ptf) | ptf 1991 |
| `add_named_yank/3` | c | 1 | **UNSPECIFIED** | — | first use cil/src/ds_bep.esp:3515 | — |
| `ask_what/3` | i | 2 | **UNSPECIFIED** | — | first use euod/DB/db1.esp:427 | — |
| `assign_input_window/2` | i | 1 | **UNSPECIFIED** | — | first use euod/DB/db3.esp:1280 | — |
| `assign_window/1` | i | 4 | **UNSPECIFIED** | — | first use cil/src/ms_cfm.esp:119 | — |
| `background/2` | i | 13 | [{standard_io_window}] sent to an instance of held pimmcsp##csp_eyecon, whose held classes define no background/2: SIMPOS supplies it (which class: I… | USAGE | pimmcsp.ptf class pimmcsp##csp_eyecon instance batsu/1 (kl0 run) (ptf) | ptf 1991 |
| `backward_character/1` | i | 2 | **UNSPECIFIED** | — | first use papyrus_src/demo/EDITOR/my_syntax.esp.1:40 | — |
| `beep/1` | i | 69 | ring the bell once (USAGE; pimfep device command beep/3 is implemented by it, ptf.md W6; the login requester beeps twice, fep_services.md §6.9) | USAGE | (in meaning) | — |
| `beginning_of_line/1` | i | 1 | **UNSPECIFIED** | — | first use euod/DEF/def.esp:34 | — |
| `call_color_manipulator/2` | c | 9 | **UNSPECIFIED** | — | first use kappa2/kappa2/user_if/pb/pcn.esp:3210 | — |
| `carriage_return/1` | i | 1 | [standard_editor] before+after-demon in held pimfep##pimos_window_editor with no held primary: SIMPOS supplies the primary (one of standard_editor, a… | USAGE | pimfep.ptf class pimfep##pimos_window_editor (ptf) | ptf 1993 |
| `change_item/3` | i | 20 | [standard_popup_choice_window] :change_item(Win,Key,NewItemVector); (nature where defined, by usage: standard_choice_window) | USAGE | sum/src/menu_init.wkm:49 (ifs_window) | held 3.x-7.x |
| `check_window/1` | i | 1 | **UNSPECIFIED** | — | first use disc/system_data.esp:140 | — |
| `class_object/2` | i | 1 | **UNSPECIFIED** | — | first use kwic-esp-002/kwic-esp/src/searchMan.esp:333 | — |
| `clear/1` | i | 35 | [standard_io_window] clear window contents (before:clear / after:clear demons seen); after-demon on it at gog-esp/IN_WINDOW.ESP:19 | USAGE | disc/demo_menu.esp:67 (ifs_window) | held 3.x-7.x |
| `clear_buffer/1` | i | 9 | [standard_io_window] discard pending input | USAGE | cal-esp/cal2.12/control.esp:244 (ifs_window) | held 3.x-7.x |
| `clear_echo_area/1` | i | 2 | [editor_main_window] clear echo area | USAGE | cil/src/ds_brs.esp:92 (ifs_window) | held 3.x-7.x |
| `clear_input/1` | i | 13 | **UNSPECIFIED** | — | first use kappa2/kappa2/user_if/pb/typewin.esp:325 | — |
| `clear_items/1` | i | 25 | [temporary_menu] remove all items; (nature where defined, by usage: standard_menu) | USAGE | cal-esp/deb2.12/create.esp:544 (ifs_window) | held 3.x-7.x |
| `clear_line/1` | i | 1 | [window] :clear_line(W) delete from cursor to end of line [possible defining mixin: as_output -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p16 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [standard_io_window] erase from cursor to end of line; application override at kwic-esp-002/kwic-esp/src/displays.esp:773 | USAGE | gog-esp/IN_WINDOW.ESP:25 (ifs_window) | held 3.x-7.x |
| `close_input/1` | i | 134 | close a standard_input_file opened with create/3 (USAGE: cal-esp/cal2.12/control.esp:193) | USAGE | (in meaning) | — |
| `close_output/1` | i | 88 | close (and write out) a standard_output_file (USAGE: cal-esp/cal2.12/control.esp:360) | USAGE | (in meaning) | — |
| `create/2` | c | 127 | class-method constructor without options (PRINTED-INTERFACE TM-125 p13); see §3.1 (window), §2.8 (standard_io_buffer) | PRINTED-INTERFACE | (in meaning) | — |
| `create/3` | c | 1499 | class-method constructor (PRINTED-INTERFACE TM-125 p13-14); per-class argument order in §3.1 (windows: options list first; files/buffers/fonts differ) | PRINTED-INTERFACE | (in meaning) | — |
| `create/4` | c | 64 | pmacs_window (Opts,_,^W) and editor_text_buffer (^Buf,Name,Size) variants (USAGE kwic-esp src/inEditor1.esp:151 for pmacs_window, cal-esp/deb2.12/dmenu.esp:1214; disc/exshow.esp:23-25 sends pmacs_window create/3 and editor_text_buffer create/4, corrected 2026-11-24); see §2.11, §3.1 | USAGE | (in meaning) | — |
| `create_menu/3` | c | 2 | **UNSPECIFIED** | — | first use chal/control.esp:75 | — |
| `create_window/2` | c | 3 | **UNSPECIFIED** | — | first use icotext/src/imi_main.esp:251 | — |
| `create_with_input/4` | c | 1 | [pmacs_window] :create_with_input(#C,Init,Superior,W) (txtstrct form); after:create_with_input/5 demon exists in cal | USAGE | txtstrct/ctx_system.esp:408 (ifs_window) | held 3.x-7.x |
| `create_with_input/5` | c | 4 | [pmacs_window] sent by tour##tt_window_manager local initialize/2; args: [size(_,_),nature([with_superior_input_buffer]),superior(_)], _, _, _ | USAGE | tour.ptf class tour##tt_window_manager local initialize/2 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1992 |
| `create_with_parameter/5` | c | 1 | [editor_text_buffer] :create_with_parameter(#editor_text_buffer,[],_,Name,Buf) | USAGE | kwic-esp-002/kwic-esp/src/dbDM.esp:28 (ifs_window) | held 3.x-7.x |
| `current_buffer/2` | i | 136 | [pmacs_window] buffer shown | USAGE | papyrus_src/demo/EDITOR/main_window.esp.1:119 (ifs_window) | held 3.x-7.x |
| `cursor_with_mouse/1` | i | 1 | **UNSPECIFIED** | — | first use papyrus_src/demo/EDITOR/my_point.esp.1:23 | — |
| `deactivate/1` | i | 107 | [window] :deactivate(W) remove from scheduling on superior; not killed; image kept as displayed [possible defining mixin: window -- INFERENCE; TM-125… | PRINTED-INTERFACE | TM-125 p16 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [inferior_window] after-demon in held kappa##pb_sheet_object with no held primary: SIMPOS supplies the primary (one of with_superior_input_buffer, as… | USAGE | kappa.ptf class kappa##pb_sheet_object (ptf) | ptf 1992 |
| `delete_item/2` | i | 3 | [window] :delete_item(Menu,Item_string) delete item whose item_string matches [possible defining mixin: menu -- INFERENCE; TM-125 attaches methods to… | PRINTED-INTERFACE | TM-125 p15 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [standard_menu] :delete_item(Menu,ItemString); application override at cal-esp/cal2.12/grmenu.esp:80 | USAGE | kappa2/kappa2/utility/lvm/LVM.ESP:508 (ifs_window) | held 3.x-7.x |
| `draw_arc/9` | i | 2 | [standard_window] drawing method called via refute; args per data/2 | PRINTED-INTERFACE | TM-785 p40, p32-36 (trtm_manuals) | 5.x (1989) |
| `draw_circle/7` | i | 4 | [as_graphics] (Obj,X,Y,R,1,solid,set): width, line style, ALU op | PRINTED | WINCS p3 (ipsj) | PSI-II (1989) |
| `draw_elliptical_arc/10` | i | 3 | [standard_window] drawing method called via refute; args per data/2 | PRINTED-INTERFACE | TM-785 p40, p32-36 (trtm_manuals) | 5.x (1989) |
| `draw_filled_circle/7` | i | 4 | [standard_window] drawing method called via refute; args per data/2 | PRINTED-INTERFACE | TM-785 p40, p32-36 (trtm_manuals) | 5.x (1989) |
| `draw_filled_rectangle/6` | i | 4 | [{as_graphics\|reshape_notifier\|as_mouse_input\|labeled_sash\|superior_window}] sent to an instance of held paragraph##what_shell_window, whose held… | USAGE | paragraph.ptf class paragraph##what_shell_window instance has_been_reshaped/1 (kl0 run) (ptf) | ptf 1992 |
| `draw_filled_rectangle/8` | i | 19 | [standard_window] drawing method called via refute; args per data/2 | PRINTED-INTERFACE | TM-785 p40, p32-36 (trtm_manuals) | 5.x (1989) |
| ″ |  |  | [{labeled_sash\|as_graphics\|as_superior\|inferior_window}] sent to an instance of held paragraph##input_file_name_window, whose held classes define … | USAGE | paragraph.ptf class paragraph##input_file_name_window instance draw/1 (kl0 run) (ptf) | ptf 1992 |
| `draw_graph/2` | i | 1 | W,[(X,Y),...] polyline (USAGE call site kwic-esp-002/kwic-esp/src/scrolls.esp:1135; §2.5) | USAGE | (in meaning) | — |
| `draw_line/6` | i | 2 | W,X1,Y1,X2,Y2,Width at gog-esp/KE_WINDOW.ESP:453 (USAGE call site); W,..,Op in paragraph (ptf); VARIANT, §2.5 | USAGE | (in meaning) | — |
| `draw_line/7` | i | 55 | [{standard_io_window}] sent to an instance of held pimmcsp##csp_eyecon, whose held classes define no draw_line/7: SIMPOS supplies it (which class: IN… | USAGE | pimmcsp.ptf class pimmcsp##csp_eyecon instance batsu/1 (kl0 run) (ptf) | ptf 1991 |
| `draw_line/8` | i | 27 | [window] :draw_line(W,X1,Y1,X2,Y2,Line_width,Line_type,Alu) defaults width 1, fixed line, exclusive or (printed X1,X2,X2,Y2 = misprint) [possible def… | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [{labeled_sash\|as_graphics\|as_superior\|inferior_window}] sent to an instance of held paragraph##input_file_name_window, whose held classes define … | USAGE | paragraph.ptf class paragraph##input_file_name_window instance draw/1 (kl0 run) (ptf) | ptf 1992 |
| `draw_marker/2` | i | 2 | [window] :draw_marker(W,Marker) [possible defining mixin: as_markers -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| `draw_rectangle/5` | i | 23 | [window] :draw_rectangle(W,X,Y,Width,Hight) [sic] [possible defining mixin: as_graphics -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| `draw_rectangle/7` | i | 8 | W,X,Y,Wd,Ht,Width,Style (USAGE call site fuzclust/fuzclust/src/window.net:102; §2.5) | USAGE | (in meaning) | — |
| `draw_rectangle/8` | i | 4 | [window] :draw_rectangle(W,X,Y,Width,Hight,Line_width,Line_type,Alu) [possible defining mixin: as_graphics -- INFERENCE; TM-125 attaches methods to n… | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| `draw_string/4` | i | 14 | [window(system, owner unstated)] :draw_string(Window,X,Y,double_bytes:{...}); fails if code has no pattern | PRINTED-INTERFACE | TM-112 p16 (tm115) | 1.0 (1985) |
| `draw_string/5` | i | 63 | [window] :draw_string(W,X,Y,String,Alu) [possible defining mixin: as_graphics -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [standard_io_window] :draw_string(W,X,Y,String,Font); (nature where defined, by usage: as_graphics) | USAGE | cal-esp/cal2.12/grmenu.esp:195 (ifs_window) | held 3.x-7.x |
| `draw_string/6` | i | 5 | [{with_superior_input_buffer\|as_standard_io_window\|with_border\|as_output\|as_graphics\|as_markers\|reshape_notifier\|as_mouse_input\|inferior_wind… | USAGE | kappa.ptf class kappa##pb_sheet_object instance draw_string/5 (kl0 run) (ptf) | ptf 1992 |
| `enable_menu_help_click/1` | i | 4 | [multiple_select_scrolling_menu] enable display of item documentation (4th field) on help click (INFERENCE from name); (nature where defined, by usag… | INFERENCE | papyrus_src/demo/EDITOR/input_editor.esp.1:30 (ifs_window) | held 3.x-7.x |
| `end_of_input/1` | i | 54 | [standard_input_file] test for end of input; (nature where defined, by usage: standard_io_window) (call shape USAGE; meaning read from the name/conte… | INFERENCE | cal-esp/cal2.12/control.esp:201 (ifs_window) | held 3.x-7.x |
| `erase_cursor/1` | i | 34 | [window] hide the text cursor; held: erase_cursor/1 on essential_window, standard_io_window, as_graphics nature sets | SCREENSHOT | 36239 p5 (ipsj) | 2.50 (1986) |
| ″ |  |  | [standard_window] after create of the image window | USAGE | pimfep.ptf pimfep##pimos_fep_superviser create_window/1 (listing) (ptf) | ptf 1993 |
| `erase_marker/2` | i | 2 | [window] :erase_marker(W,Marker) [possible defining mixin: as_markers -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| `exception/2` | i | 28 | [standard_editor] report an editor error message | USAGE | kappa2/kappa2/utility/fmp/KMACS.ESP:92 (ifs_window) | held 3.x-7.x |
| `exchange_point/1` | i | 1 | **UNSPECIFIED** | — | first use papyrus_src/demo/EDITOR/my_syntax.esp.1:34 | — |
| `exe_help_menu/3` | c | 7 | **UNSPECIFIED** | — | first use fuzclust/fuzclust/src/ahp_tool.graph:176 | — |
| `execute_command/2` | i | 2 | [{standard_editor}] sent to an instance of held kappa##pb_editor, whose held classes define no execute_command/2: SIMPOS supplies it (which class: IN… | USAGE | kappa.ptf class kappa##pb_editor instance move_input_position/1 (kl0 run) (ptf) | ptf 1992 |
| `expose/1` | i | 5 | [standard_io_window] bring window to front (call shape USAGE; meaning read from the name/context) | INFERENCE | icotext/src/kei_command_menu.esp:72 (ifs_window) | held 3.x-7.x |
| `find_file/2` | i | 3 | (Editor,Path) visit a file in a buffer (USAGE call site cil/src/ds_edt.esp:915; §2.11) | USAGE | (in meaning) | — |
| `flash/1` | i | 28 | make buffered output visible now (USAGE: after:putt/putf demons call it, cil/src/es_trc.esp:1401-1420; library_utility sets a flash flag iff the output object answers flash/1, ifs_libshell.md §4.1.1); INFERENCE on the exact effect | USAGE | (in meaning) | — |
| `gen_menu_win/3` | c | 1 | **UNSPECIFIED** | — | first use sum/src/you_edit.v32:2050 | — |
| `get_activity/2` | i | 3 | **UNSPECIFIED** | — | first use knov/src/system/cg.esp:158 | — |
| `get_and_set_icon_id/3` | c | 1 | **UNSPECIFIED** | — | first use icotext/src/window_test.esp:34 | — |
| `get_border_width/2` | i | 12 | **UNSPECIFIED** | — | first use cil/src/ds_brs.esp:279 | — |
| `get_buffer_instance/3` | c | 37 | [editor_text_buffer] sent by pimfep##pimos_window_editor instance select_buffer/4; args: _, _ | USAGE | pimfep.ptf class pimfep##pimos_window_editor instance select_buffer/4 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1993 |
| `get_buffer_instance_list/2` | c | 2 | c: list of pool buffers (USAGE call site cil/src/ms_mdm.esp:1646; §2.11) | USAGE | (in meaning) | — |
| `get_character_font/2` | c | 1 | **UNSPECIFIED** | — | first use cal-esp/cal2.12/grmenu.esp:135 | — |
| `get_cursor_position/3` | i | 1 | [standard_io_window] cursor column,row | USAGE | gog-esp/IN_WINDOW.ESP:23 (ifs_window) | held 3.x-7.x |
| `get_derived_rule_data/5` | i | 1 | **UNSPECIFIED** | — | first use euod/DB/db1.esp:229 | — |
| `get_editor/2` | i | 21 | [pmacs_window] editor object of the window | USAGE | disc/exshow.esp:29 (ifs_window) | held 3.x-7.x |
| `get_font/2` | i | 3 | [pmacs_window] then :pathname(Font,P) | USAGE | pimfep.ptf pimfep##pimos_window_editor get_font/3 (kl0 run) (ptf) | ptf 1993 |
| `get_fullpath_name/3` | i | 6 | **UNSPECIFIED** | — | first use cal-esp/deb2.12/deb_cont.esp:302 | — |
| `get_inference_rule/5` | i | 1 | **UNSPECIFIED** | — | first use euod/DB/db3.esp:97 | — |
| `get_inside_size/3` | i | 34 | [window] inside size Sx,Sy; held: get_inside_size/3 on many window nature sets | SCREENSHOT | 36239 p5 (ipsj) | 2.50 (1986) |
| ″ |  |  | [standard_io_window] inside (client) size in dots, used for laying out child panes | USAGE | cal-esp/cal2.12/cpwindow.esp:37 (ifs_window) | held 3.x-7.x |
| `get_inside_units/3` | i | 11 | [essential_window] character cell size (units) of the inside area; (nature where defined, by usage: standard_io_window) | USAGE | cal-esp/cal2.12/scawin.esp:72 (ifs_window) | held 3.x-7.x |
| `get_interface/2` | i | 1 | **UNSPECIFIED** | — | first use kappa2/kappa2/utility/rep/REPTABLE.ESP:799 | — |
| `get_interpreter/2` | i | 16 | [pmacs_window] window -> editor command interpreter; its slot original_buffer is read | USAGE | pimfep.ptf pimfep##pimos_window_editor getl/3 (kl0 run) (ptf) | ptf 1993 |
| `get_item_status/3` | i | 1 | [standard_multi_column_menu] :get_item_status(Menu,Id,Status); (nature where defined, by usage: standard_menu) | USAGE | papyrus_src/demo/EDITOR/prover_menu.esp.1:93 (ifs_window) | held 3.x-7.x |
| `get_label_height/2` | i | 11 | [standard_superior_window] label height in dots, used for layout; (nature where defined, by usage: standard_io_window) | USAGE | cil/src/ds_brs.esp:280 (ifs_window) | held 3.x-7.x |
| `get_margins/5` | i | 3 | **UNSPECIFIED** | — | first use euod/PROOF/proof1.esp:867 | — |
| `get_marker_position/4` | i | 2 | **UNSPECIFIED** | — | first use kwic-esp-002/kwic-esp/src/displays.esp:1870 | — |
| `get_mouse/2` | c | 1 | [bitmap_display] :get_mouse(#bitmap_display,Mouse) then :get_position(Mouse,X,Y) screen coordinates | USAGE | kwic-esp-002/kwic-esp/src/windows.esp:110 (ifs_window) | held 3.x-7.x |
| `get_mouse_dot_position/3` | i | 1 | **UNSPECIFIED** | — | first use euod/DEF/def.esp:1205 | — |
| `get_mouse_position/3` | i | 5 | [window] mouse X,Y in window; held: get_mouse_position/3 on as_markers / as_mouse_input nature sets | SCREENSHOT | 36239 p5 (ipsj) | 2.50 (1986) |
| ″ |  |  | [as_markers] mouse position in window coordinates; (nature where defined, by usage: as_mouse_input) | USAGE | cal-esp/cal2.12/grmenu.esp:51 (ifs_window) | held 3.x-7.x |
| `get_named_yank/3` | c | 2 | **UNSPECIFIED** | — | first use cil/src/ds_bep.esp:2312 | — |
| `get_parsing_operator/2` | i | 22 | **UNSPECIFIED** | — | first use cal-esp/cal2.12/translate.esp:93 | — |
| `get_plane_count/2` | c | 2 | [bitmap] sent by paragraph##runtime_monitor local put_pool/1; args: _ | USAGE | paragraph.ptf class paragraph##runtime_monitor local put_pool/1 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1992 |
| `get_position/3` | i | 27 | [window(system, owner unstated)] :get_position(W,^X,^Y) | PRINTED-INTERFACE | TM-115 p63 (tm115) | 1.0 (1985) |
| `get_size/3` | ci | 132 | [window(system, owner unstated)] :get_size(W,^Width,^Height) provided by the window system | PRINTED-INTERFACE | TM-115 p50,p63 (tm115) | 1.0 (1985) |
| ″ |  |  | [screen] sent by pimfep##pimos_fep_superviser local position/6; args: _, _ | USAGE | pimfep.ptf class pimfep##pimos_fep_superviser local position/6 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1993 |
| `get_slot/3` | ci | 10 | (INFERENCE) ESP object-level slot access by name, inherited by every class (not window-specific); see shell.md | INFERENCE | (in meaning) | — |
| `get_superior/2` | i | 4 | **UNSPECIFIED** | — | first use euod/DEF/def.esp:982 | — |
| `get_text_window/2` | i | 1 | **UNSPECIFIED** | — | first use gog-esp/DISPB1.ESP:217 | — |
| `get_unparsing_operator/2` | i | 4 | **UNSPECIFIED** | — | first use kappa2/kappa2/tool/del_tool/KP_DEL.ESP:164 | — |
| `get_window/2` | i | 188 | [standard_editor] editor -> its window | USAGE | pimfep.ptf pimfep##pimos_window_editor (kl0 run) (ptf) | ptf 1993 |
| `get_with_prompt/3` | i | 2 | [editor_main_window] prompt in echo area and read answer | USAGE | cal-esp/deb2.12/dedit.esp:318 (ifs_window) | held 3.x-7.x |
| `getb/3` | i | 6 | [standard_io_buffer] :getb(Buf,String,Size) whole contents | USAGE | cil/src/ms_ist.esp:1813 (ifs_window) | held 3.x-7.x |
| `getc/2` | i | 15 | read one character code (USAGE: fdd_utility on screen, simpos.wmv esp@143; gog-esp/CGS_UTIL.ESP:393) | USAGE | (in meaning) | — |
| `getl/2` | i | 153 | [standard_io_window] read a line as a string | USAGE | cal-esp/deb2.12/dmenu.esp:796 (ifs_window) | held 3.x-7.x |
| `gett/2` | i | 138 | [standard_io_window] read a term from the window; held: MATCH | PRINTED | Giho 8609 p19-20 (ipsj) | 2.0 (1986) |
| ″ |  |  | [standard_io_window] read a term (after the user types it, terminated by full stop/return) | USAGE | cal-esp/cal2.12/control.esp:197 (ifs_window) | held 3.x-7.x |
| `gett/4` | i | 13 | [standard_io_window] :gett(W,Term,VarInfoIn,VarInfoOut) term plus variable-name table; class column is the defining nature by usage; requirements.tsv… | USAGE | cal-esp/cal2.12/control.esp:245 (ifs_window) | held 3.x-7.x |
| `goal/1` | i | 1 | font_editor program entry (as_program protocol; see shell.md) | INFERENCE | (in meaning) | — |
| `goto_beginning/1` | i | 1 | **UNSPECIFIED** | — | first use papyrus_src/demo/EDITOR/my_syntax.esp.1:28 | — |
| `has_been_reshaped/1` | i | 2 | [{reshape_notifier\|standard_superior_window\|with_icon}] after-demon in held kappa##kappaMDU_superior_window with no held primary: SIMPOS supplies t… | USAGE | kappa.ptf class kappa##kappaMDU_superior_window (ptf) | ptf 1992 |
| `hide/1` | i | 20 | [window] :hide(W) hide on superior; parts not covered by other windows stay as displayed [possible defining mixin: window -- INFERENCE; TM-125 attach… | PRINTED-INTERFACE | TM-125 p16 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [standard_window] on mouse#l in the image window | USAGE | pimfep.ptf pimfep##pimos_fep_superviser refute_command/3 (listing) (ptf) | ptf 1993 |
| `initialize_input/2` | i | 1 | **UNSPECIFIED** | — | first use euod/DB/db1.esp:1407 | — |
| `input_data/2` | i | 2 | [standard_io_window] :input_data(W,Code) pushes a code into the window's input | USAGE | euod/DEF/def.esp:415 (ifs_window) | held 3.x-7.x |
| `insert/2` | i | 9 | [window] :insert(W,Character) insert at cursor [possible defining mixin: as_output -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p16 (trtm_window) | 1.0 (1985) |
| `kill/1` | i | 375 | [window] :kill(W) delete window, release bitmap area; windows are registered to the creating process and killed with it [possible defining mixin: win… | PRINTED-INTERFACE | TM-125 p18 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [superior_window] before-demon in held paragraph##what_shell_window with no held primary: SIMPOS supplies the primary (one of as_graphics, reshape_no… | USAGE | paragraph.ptf class paragraph##what_shell_window (ptf) | ptf 1992 |
| `kill/2` | c | 5 | c:kill(#editor_text_buffer,BufferName) delete a pool buffer by name (USAGE call site cal-esp/cal2.12/file.esp:255; §2.11) | USAGE | (in meaning) | — |
| `mark/1` | i | 6 | **UNSPECIFIED** | — | first use cal-esp/deb2.12/dedit.esp:418 | — |
| `mark_position/2` | i | 1 | **UNSPECIFIED** | — | first use cal-esp/deb2.12/dedit.esp:534 | — |
| `method/3` | i | 3 | [standard_editor] :method(Editor,Name,1) tests an editor method exists (dispatch by name) (call shape USAGE; meaning read from the name/context) | INFERENCE | kappa2/kappa2/utility/fmp/KMACS.ESP:89 (ifs_window) | held 3.x-7.x |
| `move_cursor/3` | i | 8 | [window] :move_cursor(W,X,Y) [possible defining mixin: as_cursor -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p16 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [standard_io_window] :move_cursor(W,Col,Row) character coordinates | USAGE | disc/util.esp:262 (ifs_window) | held 3.x-7.x |
| `move_marker/4` | i | 1 | [window] :move_marker(W,Marker,X,Y) [possible defining mixin: as_markers -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| `named_yank_flag/2` | c | 1 | **UNSPECIFIED** | — | first use cil/src/ds_bep.esp:2294 | — |
| `new/2` | c | 1 | ESP allocator :new(Class,Obj) (not window-specific; TM-115 p12, TM-134 p67) | INFERENCE | (in meaning) | — |
| `next_term/1` | i | 1 | **UNSPECIFIED** | — | first use papyrus_src/demo/EDITOR/my_syntax.esp.1:36 | — |
| `other_window/1` | i | 8 | **UNSPECIFIED** | — | first use euod/DB/db2.esp:145 | — |
| `push_to_yank/3` | i | 1 | **UNSPECIFIED** | — | first use papyrus_src/demo/EDITOR/my_delete.esp.1:48 | — |
| `put_line/2` | i | 5 | [essential_temporary_window] write a line (font_13 message window); (nature where defined, by usage: standard_io_window) | USAGE | kwic-esp-002/kwic-esp/src/windows.esp:148 (ifs_window) | held 3.x-7.x |
| `putb/3` | i | 79 | [standard_io_window] :putb(W,String,Length) write first Length chars of a string | USAGE | cal-esp/deb2.12/pmod.esp:68 (ifs_window) | held 3.x-7.x |
| `putc/2` | i | 27 | [standard_io_window] write one character (#">"); held: putc/2 on pmacs_window, standard_io_buffer, unattributed; not on standard_io_window | PRINTED | Giho 8609 p19-20 (ipsj) | 2.0 (1986) |
| ″ |  |  | [{pmacs_window}] sent to an instance of held pimmutil##csp_pathtable_utility_window, whose held classes define no putc/2: SIMPOS supplies it (which c… | USAGE | pimmutil.ptf class pimmutil##csp_pathtable_utility_window instance nl/1 (kl0 run) (ptf) | ptf 1992 |
| `putf/2` | i | 130 | [standard_io_window] :putf(W,Format) with no arguments | USAGE | euod/BUP/bup.esp:1781 (ifs_window) | held 3.x-7.x |
| `putf/3` | i | 365 | [{with_superior_input_buffer\|with_pmacs_window\|with_border\|as_superior\|reshape_notifier\|as_mouse_input\|with_default_mouse\|inferior_window}] af… | USAGE | kappa.ptf class kappa##pb_status_window (ptf) | ptf 1992 |
| `putl/1` | i | 70 | [standard_io_window] newline only | USAGE | cal-esp/cal2.12/control.esp:246 (ifs_window) | held 3.x-7.x |
| `putl/2` | i | 428 | [standard_io_window] write a string (line); held: MATCH | PRINTED | Giho 8609 p19-20 (ipsj) | 2.0 (1986) |
| ″ |  |  | [{with_superior_input_buffer\|with_pmacs_window\|with_border\|as_superior\|reshape_notifier\|as_mouse_input\|with_default_mouse\|inferior_window}] af… | USAGE | kappa.ptf class kappa##pb_status_window (ptf) | ptf 1992 |
| `putt/2` | i | 148 | [standard_io_window] write a term (honours unparsing operators and unquote_atom) | USAGE | cal-esp/cal2.12/ccwindow.esp:65 (ifs_window) | held 3.x-7.x |
| `putt/4` | i | 33 | [standard_io_window] :putt(W,Term,VarInfoIn,VarInfoOut): term with variable-name table threaded | USAGE | cal-esp/deb2.12/output.esp:516 (ifs_window) | held 3.x-7.x |
| `read/2` | i | 258 | [window] :read(W,^Code) waits; Code = char code, mouse click code, translated code, scroll_request(Offset), menu item_id, abort [possible defining mi… | PRINTED-INTERFACE | TM-125 p18 (folio 17) (trtm_window) | 1.0 (1985) |
| ″ |  |  | [{with_click_information\|with_key_select\|superior_window}] before-demon in held pimmcsp##csp_break_superior_window with no held primary: SIMPOS sup… | USAGE | pimmcsp.ptf class pimmcsp##csp_break_superior_window (ptf) | ptf 1991 |
| `read/3` | i | 8 | [labeled_superior_window] nature-qualified call `:as_mouse_input:read(W,_,Click)` returns click code; then :get_mouse_position(W,X,Y); (nature where … | USAGE | cal-esp/cal2.12/grmenu.esp:50 (ifs_window) | held 3.x-7.x |
| `read_click_with_position/4` | i | 2 | [standard_io_window] :read_click_with_position(W,Click,X,Y); Click may be given bound (mouse#l) to wait for that button | USAGE | fuzclust/fuzclust/src/input_mat.clu:97 (ifs_window) | held 3.x-7.x |
| `read_click_with_position/5` | i | 1 | [superior_window] :read_click_with_position(Sup,SourceWin,Code,X,Y) | USAGE | fuzclust/fuzclust/src/sh_window.net:84 (ifs_window) | held 3.x-7.x |
| `read_sense/2` | i | 5 | [window] :read_sense(W,^Code) like read but returns atom $$nil if no input [possible defining mixin: as_input -- INFERENCE; TM-125 attaches methods t… | PRINTED-INTERFACE | TM-125 p18 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [standard_io_window] non-blocking read; returns '$$nil' when no input is pending | USAGE | cal-esp/cal2.12/scawin.esp:213 (ifs_window) | held 3.x-7.x |
| `read_with_click/3` | i | 1 | [standard_menu] nature-qualified call `:as_input_buffer:read_with_click(W,Code,MouseCode)`; (nature where defined, by usage: as_input_buffer) | USAGE | cal-esp/cal2.12/scawin.esp:202 (ifs_window) | held 3.x-7.x |
| `refute/3` | ci | 7 | [<root>] refute(W,MethodName,ArgVector): call method by name (receiver is a window here) | PRINTED | TM-785 p32 (trtm_manuals) | 5.x (1989) |
| ″ |  |  | [standard_editor] :refute(Obj,Name,ArgVector) calls method by name | USAGE | kappa2/kappa2/utility/fmp/KMACS.ESP:90 (ifs_window) | held 3.x-7.x |
| `rename_buffer/3` | c | 1 | [editor_text_buffer] sent by pimmutil##csp_goal_searcher instance goal/1; args: _, string#"CSP/Goal-searcher" | USAGE | pimmutil.ptf class pimmutil##csp_goal_searcher instance goal/1 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1992 |
| `replace_region/3` | i | 1 | **UNSPECIFIED** | — | first use cal-esp/deb2.12/dedit.esp:420 | — |
| `reread/1` | i | 4 | standard_io_buffer: rewind to read back what was written (USAGE call site cil/src/ds_bep.esp:1488; §2.8) | USAGE | (in meaning) | — |
| `reset/1` | i | 61 | [editor_text_buffer] empty buffer | USAGE | disc/exshow.esp:27 (ifs_window) | held 3.x-7.x |
| `retrieve_all_items/2` | i | 8 | [{with_superior_input_buffer\|as_menu_input\|multiple_select_scrolling_menu}] sent to an instance of held pimmcsp##csp_mbreaked_menu, whose held clas… | USAGE | pimmcsp.ptf class pimmcsp##csp_mbreaked_menu instance get_on_items/2 (kl0 run) (ptf) | ptf 1991 |
| `retrieve_item/3` | i | 2 | [{with_superior_input_buffer\|as_menu_input\|multiple_select_scrolling_menu}] sent to an instance of held pimmcsp##csp_inspecting_menu, whose held cl… | USAGE | pimmcsp.ptf class pimmcsp##csp_inspecting_menu instance refresh_trace_mark/3 (kl0 run) (ptf) | ptf 1991 |
| `see_region/2` | i | 2 | **UNSPECIFIED** | — | first use cal-esp/deb2.12/dedit.esp:495 | — |
| `select_buffer/2` | i | 26 | [pmacs_standard_editor] after-demon in held papyrus##my_buffer_selecter with no held primary: SIMPOS supplies the primary (one of pmacs_standard_edit… | USAGE | papyrus:papyrus.pak.1.ptf class papyrus##my_buffer_selecter (ptf) | ptf 1992 |
| `set_border_width/2` | i | 4 | [window] :set_border_width(W,Width) dots; default 2 (print shows a space instead of underscore after set) [possible defining mixin: with_border -- IN… | PRINTED-INTERFACE | TM-125 p15 (trtm_window) | 1.0 (1985) |
| `set_color_pair/3` | i | 3 | [standard_window] set_color_pair(W,EvenNo,Colors); Colors 0 or {{R,G,B},{R,G,B}} | PRINTED | TM-785 p31 (trtm_manuals) | 5.x (1989) |
| ″ |  |  | [standard_io_window] :set_color_pair(W,Index,{{R,G,B},{R,G,B}}) 16-bit RGB pair; indices 0,2,4 seen | USAGE | kappa2/kappa2/user_if/pb/pdim.esp:590 (ifs_window) | held 3.x-7.x |
| `set_current_buffer/2` | i | 20 | (Editor,Buf) make Buf current (USAGE call site kappa2/kappa2/utility/mdu/ACCESS.ESP:653; §2.11) | USAGE | (in meaning) | — |
| `set_font/2` | i | 174 | [window(system, owner unstated)] :set_font(Window,Font); cursor size from font space char | PRINTED-INTERFACE | TM-112 p16; TM-115 p16 (tm115) | 1.0 (1985) |
| ″ |  |  | [standard_io_window] set text font (font object) | USAGE | txtstrct/ctx_system.esp:420 (ifs_window) | held 3.x-7.x |
| `set_help_font/2` | i | 2 | **UNSPECIFIED** | — | first use fuzclust/fuzclust/src/cliant.grape:354 | — |
| `set_input_buffer/2` | i | 2 | [pmacs_window] after :get_buffer_instance(#editor_text_buffer,Name,B) | USAGE | pimfep.ptf pimfep##pimos_window_editor select_buffer/4 (kl0 run) (ptf) | ptf 1993 |
| `set_input_position/1` | i | 4 | [pmacs_window] mark end of output as start of user input (before gett/getl/getc); class column is the defining nature by usage; requirements.tsv list… | USAGE | cil/src/es_trc.esp:1405 (ifs_window) | held 3.x-7.x |
| `set_item_status/3` | i | 19 | [standard_menu] :set_item_status(Menu,Id,on\|off) | USAGE | knov/src/system/ap.esp:199 (ifs_window) | held 3.x-7.x |
| `set_label_flag/2` | i | 1 | **UNSPECIFIED** | — | first use fuzclust/fuzclust/src/window.net:91 | — |
| `set_label_font/2` | i | 55 | [standard_io_window] font for label/title | USAGE | txtstrct/ctx_system.esp:422 (ifs_window) | held 3.x-7.x |
| `set_margins/5` | i | 1 | [window] :set_margins(W,Left,Right,Head,Tail) dots [possible defining mixin: with_margin -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p16 (folio 15) (trtm_window) | 1.0 (1985) |
| `set_marker_type/3` | i | 2 | [window] :set_marker_type(W,Marker,Type) Type box or line [possible defining mixin: as_markers -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p17 (trtm_window) | 1.0 (1985) |
| `set_max_depth/2` | i | 2 | **UNSPECIFIED** | — | first use cal-esp/deb2.12/dmenu.esp:879 | — |
| `set_max_length/2` | i | 2 | **UNSPECIFIED** | — | first use cal-esp/deb2.12/dmenu.esp:880 | — |
| `set_mode/2` | i | 1 | **UNSPECIFIED** | — | first use kwic-esp-002/kwic-esp/src/inEditor2.esp:377 | — |
| `set_name/2` | i | 8 | (W,String) window name, distinct from title (USAGE call site euod/RULED/ruled1.esp:623; meaning INFERENCE; §2.2) | USAGE | (in meaning) | — |
| `set_parsing_operator/2` | i | 5 | **UNSPECIFIED** | — | first use cil/src/ds_bep.esp:2620 | — |
| `set_permission/2` | i | 5 | [standard_io_window] :set_permission(W,out) output permission (TM-125 lists WAIT/NOTIFY/OUTPUT/SHOW, held code uses out and show) (call shape USAGE; … | INFERENCE | gog-esp/DISPB3.ESP:377 (ifs_window) | held 3.x-7.x |
| `set_position/3` | i | 37 | [standard_io_window] move the window to X,Y; held: set_position/3 on inferior_window, standard_superior_window (not standard_io_window): VARIANT of c… | PRINTED | Giho 8609 p19-20 (ipsj) | 2.0 (1986) |
| ″ |  |  | [inferior_window] after-demon in held kappa##pb_operate_icon_window with no held primary: SIMPOS supplies the primary (one of with_superior_input_buf… | USAGE | kappa.ptf class kappa##pb_operate_icon_window (ptf) | ptf 1992 |
| `set_size/3` | i | 56 | [window(system, owner unstated)] :set_size(W,Width,Height) | PRINTED-INTERFACE | TM-115 p63 (tm115) | 1.0 (1985) |
| ″ |  |  | [pmacs_window] set_size(W,manipulator,_) | USAGE | pimfep.ptf pimfep##pimos_window_editor set_size/3 (kl0 run) (ptf) | ptf 1993 |
| `set_slot/3` | c | 2 | (INFERENCE) ESP object-level slot assignment by name (not window-specific); see shell.md | INFERENCE | (in meaning) | — |
| `set_superior/2` | i | 16 | [window] :set_superior(W,Superior_window) [possible defining mixin: window -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p15 (trtm_window) | 1.0 (1985) |
| `set_title/2` | i | 111 | [window] :set_title(W,String) label string [possible defining mixin: with_label -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p15 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [pmacs_window] PIMOS set_title/4 | USAGE | pimfep.ptf pimfep##pimos_window_editor (kl0 run) (ptf) | ptf 1993 |
| `set_unparsing_operator/2` | i | 2 | **UNSPECIFIED** | — | first use kwic-esp-002/kwic-esp/src/inEditor2.esp:157 | — |
| `show/1` | i | 170 | [window] :show(W) show the window on the screen [possible defining mixin: window -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p16 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [standard_io_window] display; after:show demon used to drain input with read_sense; after-demon on it at cal-esp/cal2.12/cwindow.esp:202 | USAGE | disc/demo_bun_cut.esp:47 (ifs_window) | held 3.x-7.x |
| `show_buffer/1` | i | 3 | [pmacs_window] redisplay buffer | USAGE | papyrus_src/demo/EDITOR/main_window.esp.1:133 (ifs_window) | held 3.x-7.x |
| `show_menu/1` | i | 1 | **UNSPECIFIED** | — | first use papyrus_src/demo/EDITOR/my_point.esp.1:73 | — |
| `size/2` | i | 4 | standard_io_buffer: :size(Buf,N) character count, used after :reread before :getb (USAGE cil/src/ds_bep.esp:1488-1491) | USAGE | (in meaning) | — |
| `system_font/2` | c | 8 | [window_subsystem] :system_font(#window_subsystem,F) default system font | USAGE | cal-esp/deb2.12/create.esp:299 (ifs_window) | held 3.x-7.x |
| `transfer/8` | i | 7 | [essential_window] :transfer(W,SX,SY,DX,DY,Wd,Ht,copy) block move inside a window; (nature where defined, by usage: as_graphics) | USAGE | cil/src/es_gin.esp:855 (ifs_window) | held 3.x-7.x |
| `two_windows/1` | i | 2 | [pmacs_standard_editor] held papyrus##rule_pat_editor (nature pmacs_standard_editor) defines a primary of this SIMPOS selector (override/extension) | USAGE | papyrus:papyrus.pak.1.ptf class papyrus##rule_pat_editor (ptf) | ptf 1992 |
| `unquote_atom/1` | i | 17 | [pmacs_window] print atoms unquoted (after:create demon); (nature where defined, by usage: standard_io_buffer) (call shape USAGE; meaning read from t… | INFERENCE | papyrus_src/demo/TREE/winop.esp.1:8 (ifs_window) | held 3.x-7.x |
| `view_next_screen/1` | i | 1 | **UNSPECIFIED** | — | first use fuzclust/fuzclust/src/sh_window.net:116 | — |
| `view_previous_screen/1` | i | 1 | **UNSPECIFIED** | — | first use fuzclust/fuzclust/src/sh_window.net:102 | — |
| `view_two_windows/1` | i | 1 | **UNSPECIFIED** | — | first use euod/DB/db2.esp:172 | — |
| `warp_mouse/3` | i | 2 | [as_markers] move mouse to (X,Y) in window; (nature where defined, by usage: as_mouse_input) | USAGE | kwic-esp-002/kwic-esp/src/inSheet2.esp:903 (ifs_window) | held 3.x-7.x |
| `wink/2` | c | 1 | **UNSPECIFIED** | — | first use fuzclust/fuzclust/src/sh_window.net:32 | — |
| `write/2` | i | 7 | [window(system, owner unstated)] :write(Window,Character_code) | PRINTED-INTERFACE | TM-112 p16 (tm115) | 1.0 (1985) |
| ″ |  |  | [{with_margin\|with_border\|as_scroll\|as_output\|as_input\|inferior_window}] sent to an instance of held kappa##file_character_window, whose held cl… | USAGE | kappa.ptf class kappa##file_character_window instance wait_a_minute/4 (kl0 run) (ptf) | ptf 1992 |
| `write_file/4` | i | 1 | **UNSPECIFIED** | — | first use cil/src/ds_edt.esp:760 | — |
| `write_line/2` | i | 42 | [window(system, owner unstated)] :write_line(Window,double_bytes:{...}) | PRINTED-INTERFACE | TM-112 p16 (tm115) | 1.0 (1985) |
| ″ |  |  | [standard_io_window] write a line at cursor | USAGE | euod/PROOF/proof2.esp:4053 (ifs_window) | held 3.x-7.x |
| `write_line/3` | i | 5 | [window_without_label] :write_line(W,Row,String); (nature where defined, by usage: standard_io_window) | USAGE | fuzclust/fuzclust/src/matrix.clu:298 (ifs_window) | held 3.x-7.x |
| `write_line/4` | i | 9 | [standard_io_window] :write_line(W,Row,Col,String) | USAGE | knov/src/system/cg.esp:307 (ifs_window) | held 3.x-7.x |
| `write_line_tail/4` | i | 15 | [standard_io_window] :write_line_tail(W,Row,Col,String) | USAGE | knov/src/system/eg.esp:62 (ifs_window) | held 3.x-7.x |
| `write_lines/2` | i | 44 | [window(system, owner unstated)] :write_lines(Window,double_bytes:{...}) | PRINTED-INTERFACE | TM-112 p16 (tm115) | 1.0 (1985) |
| ″ |  |  | used in as_program example; receiver is Obj!window from nature with_user_window, its class is not printed | USAGE | TM-134 p70 (trtm_progsys) | 1.0 (1985) |
| `you_menu_win/2` | c | 1 | **UNSPECIFIED** | — | first use sum/src/you_edit.v32:2072 | — |
