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
| `create/4` | c | 64 | pmacs_window (Opts,_,^W) and editor_text_buffer (^Buf,Name,Size) variants (USAGE disc/exshow.esp:23, cal-esp/deb2.12/dmenu.esp:1214); see §2.11, §3.1 | USAGE | (in meaning) | — |
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
| `get_character_font/2` | c | 1 | [with_character] called 1 times by helic2 (front-end census; also in the 15-program census); meaning not stated in the source | CENSUS (FRONT-END CALL SITES; NO MEANING, SO COVERAGE.PY DOES NOT COUNT IT) | helic2.tar.Z/helic2/IF/PROGRAM/LEGAL/ESP/grmenu.esp:132 (fixpoint_fe) | IFS 1989-95 |
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
| `get_parsing_operator/2` | i | 22 | [standard_input_file] called 9 times by cbcdss,examds,pax,quixote (front-end census; also in the 15-program census); meaning not stated in the source | CENSUS (FRONT-END CALL SITES; NO MEANING, SO COVERAGE.PY DOES NOT COUNT IT) | cbcdss.tar.Z/cbsdss/psData.esp:44 (fixpoint_fe) | IFS 1989-95 |
| `get_plane_count/2` | c | 2 | [bitmap] sent by paragraph##runtime_monitor local put_pool/1; args: _ | USAGE | paragraph.ptf class paragraph##runtime_monitor local put_pool/1 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1992 |
| `get_position/3` | i | 27 | [window(system, owner unstated)] :get_position(W,^X,^Y) | PRINTED-INTERFACE | TM-115 p64 (tm115) | 1.0 (1985) |
| `get_size/3` | ci | 132 | [window(system, owner unstated)] :get_size(W,^Width,^Height) provided by the window system | PRINTED-INTERFACE | TM-115 p50,p64 (tm115) | 1.0 (1985) |
| ″ |  |  | [screen] sent by pimfep##pimos_fep_superviser local position/6; args: _, _ | USAGE | pimfep.ptf class pimfep##pimos_fep_superviser local position/6 (kl0 run, SIMPOS sends stubbed) (ptf) | ptf 1993 |
| `get_slot/3` | ci | 10 | (INFERENCE) ESP object-level slot access by name, inherited by every class (not window-specific); see shell.md | INFERENCE | (in meaning) | — |
| `get_superior/2` | i | 4 | **UNSPECIFIED** | — | first use euod/DEF/def.esp:982 | — |
| `get_text_window/2` | i | 1 | **UNSPECIFIED** | — | first use gog-esp/DISPB1.ESP:217 | — |
| `get_unparsing_operator/2` | i | 4 | [standard_io_buffer] called 2 times by quixote (front-end census; also in the 15-program census); meaning not stated in the source | CENSUS (FRONT-END CALL SITES; NO MEANING, SO COVERAGE.PY DOES NOT COUNT IT) | quixote.tar.gz/src/QS/pm/pm_io.esp:12 (fixpoint_fe) | IFS 1989-95 |
| `get_window/2` | i | 188 | [standard_editor] editor -> its window | USAGE | pimfep.ptf pimfep##pimos_window_editor (kl0 run) (ptf) | ptf 1993 |
| `get_with_prompt/3` | i | 2 | [editor_main_window] prompt in echo area and read answer | USAGE | cal-esp/deb2.12/dedit.esp:318 (ifs_window) | held 3.x-7.x |
| `getb/3` | i | 6 | [standard_io_buffer] :getb(Buf,String,Size) whole contents | USAGE | cil/src/ms_ist.esp:1813 (ifs_window) | held 3.x-7.x |
| `getc/2` | i | 15 | read one character code (USAGE: fdd_utility on screen, simpos.wmv esp@143; gog-esp/CGS_UTIL.ESP:393) | USAGE | (in meaning) | — |
| `getl/2` | i | 153 | [standard_io_buffer] read a line as a string (printed "get1"; read as getl, INFERENCE) | PRINTED | ESPtex/program-e.tex:6736-6745; ESPtex-j/program-j.tex:6470-6480 (sweep2) | 1990 manual |
| ″ |  |  | [standard_io_window] read a line as a string | USAGE | cal-esp/deb2.12/dmenu.esp:796 (ifs_window) | held 3.x-7.x |
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
| `putt/2` | i | 148 | [standard_io_buffer] write a term with no separator: putt [1,2] then putt p(1,2) reads back as "[1,2]p(1,2)" | PRINTED | ESPtex/program-e.tex:6736-6745; ESPtex-j/program-j.tex:6470-6480 (sweep2) | 1990 manual |
| ″ |  |  | [standard_io_window] write a term (honours unparsing operators and unquote_atom) | USAGE | cal-esp/cal2.12/ccwindow.esp:65 (ifs_window) | held 3.x-7.x |
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
| `set_max_depth/2` | i | 2 | [standard_io_buffer] called 1 times by dulcinea (front-end census; also in the 15-program census); meaning not stated in the source | CENSUS (FRONT-END CALL SITES; NO MEANING, SO COVERAGE.PY DOES NOT COUNT IT) | dulcinea.tar.Z/dul/dul_if.esp:233 (fixpoint_fe) | IFS 1989-95 |
| `set_max_length/2` | i | 2 | [standard_io_buffer] called 1 times by dulcinea (front-end census; also in the 15-program census); meaning not stated in the source | CENSUS (FRONT-END CALL SITES; NO MEANING, SO COVERAGE.PY DOES NOT COUNT IT) | dulcinea.tar.Z/dul/dul_if.esp:234 (fixpoint_fe) | IFS 1989-95 |
| `set_mode/2` | i | 1 | **UNSPECIFIED** | — | first use kwic-esp-002/kwic-esp/src/inEditor2.esp:377 | — |
| `set_name/2` | i | 8 | (W,String) window name, distinct from title (USAGE call site euod/RULED/ruled1.esp:623; meaning INFERENCE; §2.2) | USAGE | (in meaning) | — |
| `set_parsing_operator/2` | i | 5 | [standard_input_file] called 9 times by cbcdss,quixote (front-end census; also in the 15-program census); meaning not stated in the source | CENSUS (FRONT-END CALL SITES; NO MEANING, SO COVERAGE.PY DOES NOT COUNT IT) | cbcdss.tar.Z/cbsdss/adviser.esp:736 (fixpoint_fe) | IFS 1989-95 |
| `set_permission/2` | i | 5 | [standard_io_window] :set_permission(W,out) output permission (TM-125 lists WAIT/NOTIFY/OUTPUT/SHOW, held code uses out and show) (call shape USAGE; … | INFERENCE | gog-esp/DISPB3.ESP:377 (ifs_window) | held 3.x-7.x |
| `set_position/3` | i | 37 | [standard_io_window] move the window to X,Y; held: set_position/3 on inferior_window, standard_superior_window (not standard_io_window): VARIANT of c… | PRINTED | Giho 8609 p19-20 (ipsj) | 2.0 (1986) |
| ″ |  |  | [inferior_window] after-demon in held kappa##pb_operate_icon_window with no held primary: SIMPOS supplies the primary (one of with_superior_input_buf… | USAGE | kappa.ptf class kappa##pb_operate_icon_window (ptf) | ptf 1992 |
| `set_size/3` | i | 56 | [window(system, owner unstated)] :set_size(W,Width,Height) | PRINTED-INTERFACE | TM-115 p64 (tm115) | 1.0 (1985) |
| ″ |  |  | [pmacs_window] set_size(W,manipulator,_) | USAGE | pimfep.ptf pimfep##pimos_window_editor set_size/3 (kl0 run) (ptf) | ptf 1993 |
| `set_slot/3` | c | 2 | (INFERENCE) ESP object-level slot assignment by name (not window-specific); see shell.md | INFERENCE | (in meaning) | — |
| `set_superior/2` | i | 16 | [window] :set_superior(W,Superior_window) [possible defining mixin: window -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p15 (trtm_window) | 1.0 (1985) |
| `set_title/2` | i | 111 | [window] :set_title(W,String) label string [possible defining mixin: with_label -- INFERENCE; TM-125 attaches methods to no class] | PRINTED-INTERFACE | TM-125 p15 (trtm_window) | 1.0 (1985) |
| ″ |  |  | [pmacs_window] PIMOS set_title/4 | USAGE | pimfep.ptf pimfep##pimos_window_editor (kl0 run) (ptf) | ptf 1993 |
| `set_unparsing_operator/2` | i | 2 | [standard_io_buffer] called 3 times by cbcdss,quixote (front-end census; NOT in the 15-program census); meaning not stated in the source | CENSUS (FRONT-END CALL SITES; NO MEANING, SO COVERAGE.PY DOES NOT COUNT IT) | cbcdss.tar.Z/cbsdss/k_repair.esp:31 (fixpoint_fe) | IFS 1989-95 |
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
