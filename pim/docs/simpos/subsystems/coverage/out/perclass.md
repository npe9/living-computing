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
