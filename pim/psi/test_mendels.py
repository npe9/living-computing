#!/usr/bin/env python3
"""MENDELS (IFS No.61) on PIMOS and SIMPOS together (psi/mendels.py),
and the pieces added for it (2026-11-27).

The run: the KL1 half on PIMOS, from the shell's prompt, installed as
readme.e/install.e say (the doc route), the ESP half compiled by espc.py
and run on kl0, linked by the FEP's string I/O.  Its tape,
psi/mendels_tapes/doc.json, was recorded by

    python3 -I psi/mendels.py live PROMPT.pkl --record psi/mendels_tapes/doc.json

(PROMPT.pkl: ref/pimm/ifs_sweep.py's header).  The live run is opt-in
(MENDELS_LIVE=PROMPT.pkl, about 80 s); the replay feeds the PSI side
PIMOS's packets from the tape and checks each packet the PSI sends.

Furthest point (OBSERVED, both runs): MENDELS's own ESP device starts,
asks the user's path in its pmacs_window dialog (init_path.esp; the keys
>sys>user>MENDELuser RETURN y RETURN), answers PIMOS load_library, PIMOS
loads mdllibrary.exe from >sys>user>MENDELuser>SYSTEM (the path typed)
and sends loaded_library(normal([mendel::example1, ...])); the ESP side
reads it and goes on into mendel_main's create/1: the mendel_title
process, its `Change phase ?` temporary_menu (stood in since 2026-11-27),
mendel_window's create_window/1 (font:kanji_16.font substituted, its
float sizes), `:create(#base, ...)` (MENDELS's class whose natures are
the SIMPOS window mixins, stood in since the window mixins step), the
whole zone, garnet_window, the library window, the editors, object_lib
restore/1 (the HELD tree.obj and tree.key: example1-3; test_library_
restored), top_down, mdl_input, buffer, flat_data and flat_mdl,
method_editor (its title panes, standard_io_windows placed inside the
base: their inferior form, since 2026-11-27), the rest of create/1, and
resume/0, which shows the whole zone over the title screen, its system
window (a pmacs_window inside the base, since 2026-11-27) with
field_tree's "file not exist" message (frame pinned, docs/simpos/
screens/mendels_zone.png); then esp_go/3, whose exec/3 calls the held
phase/2.  Since the load answer step (2026-11-28) the PSI is given
loaded_library(normal) in place of PIMOS's loaded_library(normal([...]))
(mendels.adapt_load_answer, OURS: the PIMOS V3.0 manual's load:do/4
answer, the packet MENDELS's no-file branch makes; psi/README.md "The
load answer step"), so phase/2 succeeds; mdl_check reports the missing
TEMP>compiler.msg in the system window, phase(top) waits in top_menu,
and the mendel_title process writes to its permission(show) screen under
the base, whose raise lifted the base whole (save/7's winfb BADSAVE,
75,520 words; window.md §7) until the title raise step (2026-11-28): a
restack now lifts a frame only over the part it changes (coordinator.esp
lift_all_in/2, OURS; TM-225 p10), 4,564 words of the base, and the title
screen shows " end" and "please return" and waits in its read
(title.esp:57).  The stop: every process waits (STOP); screen
docs/simpos/screens/mendels_title_raised.png.  With the adapter off it
still stops at phase/2 (mendels.watch_phase, OURS; test_adapter_off).
Re-recorded live 2026-11-28 (the FEP store step) from a copy of
PROMPT.pkl: PIMOS's file and directory devices (201-205) are the PSI's,
answered by the held pimos_file / pimos_directory from the PSI's tree
(mendels.BRIDGED, row_files; simpos_files.py), so PIMOS's del_file/3 on
TEMP is answered 1, wt_message/1 writes TEMP>compiler.msg into the PSI's
tree (COMPILER_MSG, test_replay) and the MENDELS job no longer aborts
(PIMOS's console ends at the relink, test_tape).  103 exchanges (28
before, none of them identical now: the first carries mendel.exe's 201);
FILES_IO, STRINGS_IO; same stop and frame, the live screen equals the
replay's.  FepStore tests the handlers on scripted packets.

Mixins (the window mixins step) runs the mixins through two other held
users on the coordinator, with the mouse: icotext's whole held class
kakari_super_window and ki_window.esp's held command bar
(multi_column_menu_with_superior_input_buffer) read by kkr_main.esp's
held read_loop/1; disc's held make_inter_menu/2 (essential_scrolling_
menu_with_superior_input_buffer) inside MENDELS's held base, read by
base's read/3.  Frames pinned by sha256 and set dots, PNGs
docs/simpos/screens/mendels_mixins_icotext.png and _disc.png byte for
byte.

Injections, OBSERVED 2026-11-27 (24, each made in the working tree by a
scratch script, restored by copy, cmp and md5 clean; this whole file run
on each; the failed set as observed on the final file):

| injection | failed |
|---|---|
| espc split_repeat: the repeat dropped (the goals after it run once) | test_package, test_repeat |
| kl0 op_melt: the frozen term itself, no fresh variables | test_freeze_melt |
| kl0 op_freeze: the term itself, no copy | test_freeze_melt |
| espc classify: a component named by its bare name (no `Class$`) | test_component, test_replay, test_path_dialog |
| espc BUILTINS: object/3 dropped | test_package, test_replay, test_path_dialog |
| espc BUILTINS: atom/1, heap_vector/2 or not_equal_string/2 dropped (one at a time) | test_package |
| esp_reader: `::` not an operator | test_reader_package_colon, test_replay |
| read_one: no term without a `.` (end of text) | test_io_buffer_printed, test_reader_package_colon, test_replay, test_path_dialog |
| read_one: the layout after a `.` left unread | test_io_buffer_printed |
| putl/2: no newline after the string | test_io_buffer_printed, test_library_utility |
| putt/2: a compound written as {F,A,..} | test_io_buffer_printed |
| library_utility get_classes/4: every package's classes | test_library_utility |
| library_utility get_classes_with_wildcard/5: the pattern ignored | test_library_utility, test_replay, test_path_dialog |
| library_utility load/2 prints nothing | test_library_utility |
| symbolizer is_object/2 always true | test_io_window_title_and_object |
| process refute_in/5: the object and the arguments swapped | test_replay, test_path_dialog |
| as_event_handler get_instance/3 fails | test_replay, test_path_dialog |
| standard_io_window deactivate/1 a no-op | test_path_dialog |
| standard_io_window create/3: the title option ignored | test_io_window_title_and_object |
| standard_io_window name/2 succeeds with no name set | test_path_dialog |
| pmacs_window getl/2: the line from the point where getl began | test_getl |
| pathname check_pathname/3 fails | test_check_pathname, test_replay, test_path_dialog |

The temporary_menu step, OBSERVED 2026-11-27 (12 more, made and restored
the same way by a scratch script, cmp clean; this whole file run on each):

| injection | failed |
|---|---|
| read/2 answers the item_string, not the item_id | test_disc_loop, test_euod_pick |
| a no_select line can be chosen | test_disc_loop |
| the mouse leaving: the menu closed, no abort answered | test_disc_loop |
| label_flag(off) ignored (the title strip drawn) | test_disc_loop |
| the pop-up not at the mouse (at 0,0) | test_disc_loop, test_euod_pick, test_euod_shown |
| delete_item/2 deletes nothing | test_methods |
| add_item/3 appends (the position ignored) | test_methods |
| espc build: put_vector_n with n-1 | test_vector_puts |
| espc X/Y: the quotient over the second operand | test_floats |
| espc float constant: the cell holds the integer part | test_floats |
| kl0 floating_point_to_integer rounds up | test_floats |
| kl0 a float mixed with an integer: the integer taken as a float | test_floats |

Weak spots of this step: the replay catches none of the float or vector
injections (mendel_window's sizes are not drawn before the stop at
`#base`), and test_euod_leave none (an unanswered read leaves the same
calls and no pane): the unit tests and test_disc_loop carry them.

The window mixins step, OBSERVED 2026-11-27 (10, made and restored the
same way by a scratch script, cmp clean; this whole file and
test_kl0.py run on each, kl0's failures marked; the first six were run
before class Pieces existed, which none of them touches):

| injection | failed |
|---|---|
| with_superior_input_buffer: input kept in the window's own buffer | test_disc_pick, test_icotext_exit |
| as_superior read/3: source and data swapped | test_disc_pick, test_icotext_exit |
| labeled_sash: label off by default | test_disc_pick, test_disc_shown, test_icotext_exit, test_icotext_shown |
| basic_window set_superior/2 a no-op | NONE |
| no clipping (an inferior drawn past its superior) | test_icotext_shown |
| kl0 get_atom_string/3 answers the atom, not a string | test_atom (kl0), test_library_restored, test_replay |
| kl0 op_number: an atom is a number | test_number |
| array get_at/3: the index off by one | test_array, test_replay |
| mendels.py: tree.obj not placed | test_library_restored |
| esplex: a backslash escapes in a quoted atom again | test_package, test_replay |

Weak spot: set_superior/2 is not told apart (no held user here moves a
window under another superior; med_window's standard_io_windows are made
in their superior by create/3, 2026-11-27, so it is still not reached).

MethodEditor (the method editor step, 2026-11-27) runs held code outside
the run: the held set_window_attribute/4 (med_win.esp) placing two
standard_io_windows made with med_win's create options inside MENDELS's
held base, written before and after (put_line/2 twice) and clicked; the
held mendel_title (title.esp) whole.  Frames pinned by sha256 and set
dots, PNGs docs/simpos/screens/mendels_inferior_titles.png and
mendels_title.png byte for byte.  test_editor_link sends the two small
stand-ins whose effect the run does not show.

The method editor step, OBSERVED 2026-11-27 (19, made in the working
tree by a scratch script, restored by copy and cmp; this whole file run
on each, on the final file):

| injection | failed |
|---|---|
| set_superior: no inferior form (kept only) | test_med_click, test_med_shown, test_replay |
| nature option: with_superior_input_buffer ignored | test_med_click |
| source/2: the inferior form named, not the standard_io_window | test_med_click |
| put_line/2: never back to row 0 | test_med_shown |
| inferior form: what was written before not written again | test_med_shown |
| save_under: the whole rectangle saved | test_cut_restore, test_replay |
| save_under: the windows below ignored (only the band) | test_cut_restore, test_replay |
| background/2: text not drawn inverted | test_title_shown |
| draw_characters/3: not magnified (factor 1) | test_title_shown |
| interpreter: an atom datum not looked up as a key | test_replay |
| pmacs_window set_editor/2: the interpreter keeps its editor | test_library_restored, test_replay |
| pmacs_window inside a superior drawn as a top window | test_replay |
| temporary_menu name/2 always fails | test_editor_link |
| standard_editor clear_buffer/3 deletes nothing | test_editor_link |
| set_size/3 before the superior: the size not kept | test_med_shown |
| set_position/3 on the inferior form: position (0,0) | test_med_click, test_med_shown |
| inferior form: label_flag not kept | test_med_shown |
| cut restore: the part under not drawn back | test_cut_restore |
| cut put_back: the part under not drawn back | NONE |

Weak spots: the title screen's label strip (a top standard_io_window
ignores label_flag(off)) is pinned as drawn, not as SIMPOS draws it.
The cut form's put_back/2 (a restack under a mixin window) is not told
apart (NONE above): no test here restacks one.  The other forwarding
clauses to the inferior form (deactivate, hide, kill, set_font,
set_title, set_permission, read/2, clear_buffer/1, get_size/3,
get_position/3) are not injected one by one; MENDELS's run sends only
activate/1, put_line/2, clear_line/1, get_inside_size/3 and read through
the base before the stop.

The system window step (pmacs_window as an inferior, 2026-11-27):
test_sys_shown, test_sys_click and test_sys_refused (class MethodEditor)
run a mendel_pmacs made with create_system_window/6's options inside the
held base; test_cut_move moves a mixin window (the cut form's put_back/2).
Injections, OBSERVED 2026-11-27 (19, made in the working tree by a
scratch script from a backup, restored by copy and cmp; this whole file
run on each; all 19 run again on the final file with the same result.
The two rows marked * were NONE in the first round, before
test_sys_refused gained the input and font checks that catch them):

| injection | failed |
|---|---|
| pmacs_window: no inferior form (the superior kept only) | test_replay, test_sys_click, test_sys_refused, test_sys_shown |
| inferior form: input not routed to the superior (with_superior_input_buffer ignored) | test_sys_click |
| pmacs_window input_to: superior by default (every pmacs_window shares) | test_sys_refused * |
| put_codes: no wrap at the last column | test_replay, test_sys_shown |
| put_codes: no scroll (back to row 0 past the last row) | test_sys_shown |
| put_codes: key#lf not a new row (kept in the row) | test_replay, test_sys_shown |
| kept options: size dropped | test_sys_refused, test_sys_shown |
| kept options: position dropped | test_replay, test_sys_click, test_sys_shown |
| kept options: label_flag dropped | test_replay, test_sys_shown |
| set_font not handed to the form | test_sys_refused * |
| activate not handed to the form | test_replay, test_sys_click, test_sys_shown |
| get_superior answers 0 | test_sys_click, test_sys_shown |
| the text buffer not drawn in the form (no set_pane) | test_replay, test_sys_shown |
| getl on an inferior not refused (reads the interpreter) | test_sys_refused |
| read_with_prompt on an inferior not refused | test_sys_refused |
| set_input_buffer on an inferior not refused | test_sys_refused |
| mendels.py: the phase/2 watch off | test_replay |
| mendels.py: the watch fires on any failure inside phase/2 (a clause tried) | test_replay |
| cut put_back: the part under not drawn back (the method editor step's NONE) | test_cut_move |

The new stop (test_replay): the held phase/2 fails on
loaded_library(normal([...])), stopped there by mendels.watch_phase
(OURS) before call_esp/3's repeat would retry the same message over what
the retry undoes (psi/README.md "The system window step").  The cut
form's put_back/2 (NONE in the method editor step) is caught by
test_cut_move.  Weak spots: the forwarding clauses deactivate, hide,
kill, set_title, set_size, set_position, get_size and get_position of
the inferior pmacs_window are not injected one by one (MENDELS's run
sends create, set_font and activate before the stop).

The load answer step (2026-11-28): test_adapter_off, test_load_adapter,
test_adapter_refusal_stops, test_empty_vector (pmi 30) and
test_ch_string_string.  Injections, OBSERVED 2026-11-28 (10, made by a
scratch script from a backup, restored by copy and cmp; this whole file
run on each; * NONE until test_empty_vector gained a one-element vector,
then run again):

| injection | failed |
|---|---|
| espc: `{}` got as the atom (no pmi 30) | test_empty_vector, test_library_restored, test_replay |
| kl0 get_vector_0 always fails | test_empty_vector, test_replay |
| kl0 get_vector_0 matches any vector * | test_empty_vector |
| mendels: LOAD_ADAPTER off | test_adapter_refusal_stops, test_replay |
| adapter answers loaded_library(abnormal) | test_load_adapter, test_replay |
| adapter passes an unknown loaded_library string (no refusal) | test_adapter_refusal_stops, test_load_adapter |
| get_ch_string_string: the bare text | test_ch_string_string, test_replay |
| get_ch_string_string not modelled | test_ch_string_string, test_replay |
| esp_reader: `::` not an operator | test_adapter_off, test_reader_package_colon |
| mendels.py: the phase/2 watch off | test_adapter_off |

(The earlier tables' `::` and watch rows named test_replay; the run now
reaches those only with the adapter off.)

The title raise step (2026-11-28): test_frame_part and test_replay.
Injections, OBSERVED 2026-11-28 (9, made by a scratch script from a
backup, restored by copy and cmp, git diff clean; this whole file run on
each, on the final file):

| injection | failed |
|---|---|
| frames lifted whole (lifted_in/2 always lift/1) | test_frame_part, test_replay |
| the part not grown by a frame's box | test_frame_part |
| lift_in/2: the pane whole as the part | test_frame_part, test_replay |
| lift_under/6: the whole screen cleared | test_frame_part, test_replay |
| lift_under/6: Inner not drawn back | test_frame_part, test_replay |
| save_under_below/7: nothing below | test_frame_part |
| save_under_below/7: every window, not only those below | test_frame_part, test_replay |
| lay/1 of a part: the frame's dots not drawn back | test_frame_part |
| lift_in/2: a missed frame lifted whole | test_frame_part |

(A tenth, whole_below/4, NONE, is removed: a frame's box already holds
every window below it, so growing the part by the overlaps with the
whole-lifted panes below added nothing.)

The FEP store step (2026-11-28): FepStore, test_tape's FILES_IO and
console end, test_replay's compiler.msg.  Injections, OBSERVED 2026-11-28
(12, made by a scratch script from a backup, restored by copy and cmp;
this whole file run on each):

| injection | failed |
|---|---|
| mendels.BRIDGED back to (601,) | test_routes, test_tape |
| TEMP not in INSTALLED_DIRS | test_adapter_off, test_adapter_refusal_stops, test_library_restored, test_replay |
| write_next/1 drops the data | test_replay, test_write_then_read |
| delete_with_wildcard: every file matches | test_delete_and_expunge |
| expunge/1 a no-op | test_delete_and_expunge, test_replay |
| kl0 Str: ptfdump.ch's lossy letter for row 0x23 | test_object_bytes |
| end_of_input/1: terms only | test_adapter_off, test_adapter_refusal_stops, test_library_restored, test_object_bytes, test_path_dialog, test_replay, test_write_then_read |
| getb/3: N one less | the same seven |
| link_counter/2 answers 2 | test_adapter_off, test_adapter_refusal_stops, test_library_restored, test_path_dialog, test_replay, test_write_then_read |
| make_only/3: a taken name not refused | test_write_over_a_file_refuses |
| row_files: text not home_bytes (a space added) | test_adapter_off, test_adapter_refusal_stops, test_library_restored, test_path_dialog, test_replay, test_row_files |
| get_string/3: the month after | test_adapter_off, test_adapter_refusal_stops, test_library_restored, test_path_dialog, test_replay, test_write_then_read |

(The Str row and the row_files row were NONE in a first form: the Str
round trip was then tested only through the live run, and row_files'
injection, the raw bytes, was equal to home_bytes for the doc route's
files; a Str round-trip check was added to test_object_bytes and the
row_files injection changed.)

Weak spots (the load answer step): the replay does not reach repeat's retry, freeze/melt's
copies or putt's compound form (the run's terms are atoms and a list):
the unit tests carry them.  getl's line start is caught only by
test_getl (the run's old answers are empty); is_object/2 and the title
only by the direct test (the frames of the "WAIT !" window are not
pinned; the one frame pinned is the path dialog's).
"""
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import espc  # noqa: E402
import kl0 as K  # noqa: E402
import mendels  # noqa: E402

TAPE = os.path.join(HERE, 'mendels_tapes', 'doc.json')
SCREEN = os.path.join(HERE, '..', 'docs', 'simpos', 'screens', 'mendels_path.png')

# the string-I/O messages of the run (mendels.strings_io), OBSERVED live
# 2026-11-27: the devices PIMOS makes by 601, its io (620) and the PSI's
# answers.  The answer to 56's io(0, "system") is the user path typed in
# the dialog, with >SYSTEM> (esp_util.esp)
STRINGS_IO = [
    ('create', 38, 'mendel##mendel_esp_device'), ('close', 38),
    ('create', 39, 'mendel##esp_utility'), ('>', 39, 2, '>sys>user>MENDEL>KL1>'), ('close', 39),
    ('<', 39, 1, 'end'), ('create', 41, 'mendel##mendel_esp_device'), ('close', 41),
    ('create', 42, 'mendel##mendel_loader'), ('create', 44, 'mendel##mendel_esp_device'),
    ('>', 42, 0, 'mendel'), ('close', 44), ('<', 42, 1, 'end'),
    ('create', 46, 'mendel##mendel_esp_device'), ('close', 46),
    ('create', 47, 'mendel##esp_utility'), ('>', 47, 2, '>sys>user>MENDEL>KL1>'), ('close', 47),
    ('<', 47, 1, 'end'), ('create', 49, 'mendel##mendel_esp_device'), ('close', 49),
    ('create', 50, 'mendel##mendel_esp_device'), ('>', 50, 0, 'start'),
    ('<', 50, 1, 'load_library'), ('create', 52, 'mendel##mendel_esp_device'), ('close', 52),
    ('create', 53, 'mendel##esp_utility'), ('>', 53, 2, '>sys>user>MENDEL>KL1>'), ('close', 53),
    ('<', 53, 1, 'end'), ('create', 55, 'mendel##mendel_esp_device'), ('close', 55),
    ('create', 56, 'mendel##esp_utility'), ('>', 56, 0, 'system'), ('close', 56),
    ('<', 56, 1, '>sys>user>MENDELuser>SYSTEM>'),
    # since the title raise step (2026-11-28), OBSERVED live: the run no
    # longer stops on the PSI side, so PIMOS goes on: device 62 closed;
    # esp_device/3's set_MENDEL_directory (package.kl1:15-19, 134-145) and
    # esp_utility directory_name("temp") (esp_util.kl1:30-50) for
    # mdl_comp.kl1 wt_message/1's del_file (172-200), which writes the
    # loader's messages to TEMP>compiler.msg after load:do.  Since the FEP
    # store step (2026-11-28) the TEMP directory is the PSI's (FILES_IO),
    # so del_file/3 goes on and wt_message/1 asks for the directory again
    # (69-73) before its write-open; the loader's stream (42) is no longer
    # closed (before, the job's abort closed it).  The messages are those
    # of the run before but for 69-73 and 42's close; their order across
    # devices follows the exchanges, which the file requests now add to
    ('create', 62, 'mendel##mendel_esp_device'), ('close', 62), ('create', 63, 'mendel##esp_utility'),
    ('>', 50, 0, 'loaded_library(normal([mendel:: example1,mendel:: example2,mendel:: example3]))'),
    ('>', 63, 2, '>sys>user>MENDEL>KL1>'), ('close', 63), ('<', 63, 1, 'end'),
    ('create', 65, 'mendel##mendel_esp_device'), ('close', 65),
    ('create', 66, 'mendel##esp_utility'), ('>', 66, 0, 'temp'), ('close', 66),
    ('<', 66, 1, '>sys>user>MENDELuser>TEMP>'),
    ('create', 69, 'mendel##mendel_esp_device'), ('close', 69),
    ('create', 70, 'mendel##esp_utility'), ('>', 70, 2, '>sys>user>MENDEL>KL1>'), ('close', 70),
    ('<', 70, 1, 'end'), ('create', 72, 'mendel##mendel_esp_device'), ('close', 72),
    ('create', 73, 'mendel##esp_utility'), ('>', 73, 0, 'temp'), ('close', 73),
    ('<', 73, 1, '>sys>user>MENDELuser>TEMP>'),
]
# the file and directory devices of the run (mendels.files_io), OBSERVED
# live 2026-11-28, the FEP store step: every one the PSI's, answered by the
# held pimfep##pimos_file and pimos_directory from the PSI's tree.  PIMOS
# reads mendel.exe whole (76,098 bytes, the archive's), mendel.pac each
# time a package is looked up, mdllibrary.exe (1,632 bytes); the .sav and
# .SAV probes are 5 (no such file), as fep.py answered them; then
# del_file/3's 204 on TEMP is 1, its 231 of compiler.msg 5 (no such file:
# pimos_directory delete/4's `\== []`; PIMOS's `delete(FileNmS,_)` takes
# it), 235 1, and wt_message/1's 202 writes the loader's 276 bytes
PAC = [[112, 1], [210, 1], [210, 2], [112, 1], [70], [60, 1]]
FILES_IO = [
    (34, 201, '>sys>user>MENDEL>mendel.exe', 1,
     [[222, 1], [221, 1]] + [[210, 1]] * 10 + [[210, 2], [112, 1], [70], [60, 1]], 76098, 0),
    (35, 201, '>sys>user>MENDEL>mendel.exe.sav', 5, [], 0, 0),
    (36, 201, '>sys>user>MENDEL>mendel.exe.SAV', 5, [], 0, 0)] + [
    (d, 201, '>sys>user>MENDEL>KL1>mendel.pac', 1, PAC, 38, 0) for d in (37, 40, 43, 45, 48, 51, 54)] + [
    (57, 201, '>sys>user>MENDELuser>SYSTEM>mdllibrary.exe', 1, [[112, 1], [70], [60, 1]], 0, 0),
    (58, 201, '>sys>user>MENDELuser>SYSTEM>mdllibrary.exe', 1,
     [[222, 1], [221, 1], [210, 1], [210, 2], [112, 1], [70], [60, 1]], 1632, 0),
    (59, 201, '>sys>user>MENDEL>KL1>mendel.pac', 1, PAC, 38, 0),
    (60, 201, '>sys>user>MENDELuser>SYSTEM>mdllibrary.exe.sav', 5, [], 0, 0),
    (61, 201, '>sys>user>MENDELuser>SYSTEM>mdllibrary.exe.SAV', 5, [], 0, 0),
    (64, 201, '>sys>user>MENDEL>KL1>mendel.pac', 1, PAC, 38, 0),
    (67, 204, '>sys>user>MENDELuser>TEMP', 1, [[231, 'compiler.msg', 5], [235, 1], [70], [60, 1]], 0, 0),
    (68, 201, '>sys>user>MENDEL>KL1>mendel.pac', 1, PAC, 38, 0),
    (71, 201, '>sys>user>MENDEL>KL1>mendel.pac', 1, PAC, 38, 0),
    (74, 202, '>sys>user>MENDELuser>TEMP>compiler.msg', 1, [[111, 1], [112, 1], [70], [60, 1]], 0, 276)]
# what PIMOS wrote there (the loader's messages, mdl_comp.kl1 load_MENDELlibrary
# /1's STD), read from the PSI's tree after the replay
COMPILER_MSG = ('Load File : >sys>user>MENDELuser>SYSTEM>mdllibrary.exe.1\n"mendel:: example2" Loaded\n'
                '"mendel:: example1" Loaded\n"mendel:: example3" Loaded\n')
STOP = 'would suspend: no process is ready: <simpos##process> is suspended'
EXCHANGES = 103
# the stop before the load adapter (2026-11-27), which the run still gives
# with mendels.LOAD_ADAPTER off (test_adapter_off)
STOP_NO_ADAPTER = ('mendels: held mendel##mendel_main phase/2 has no clause for {loaded_library,{normal,'
                   '[{::,mendel,example1},{::,mendel,example2},{::,mendel,example3}]}} '
                   '(call_esp/3 would retry the same message)')
# the packet the load adapter puts in the PSI in place of PIMOS's
# io(0, "loaded_library(normal([mendel:: example1,...]))") to device 50:
# OBSERVED byte for byte 2026-11-28 as the packet PIMOS itself sends when
# MENDELS's held no-file branch answers (a live run with no mdllibrary.exe
# served; mdl_comp.kl1:43-54 `Result = normal`)
LOAD_ANSWER_PACKET = ('00000032000000000000026c00000002ffffffff0000002c00000000'
                      '236c236f23612364236523642132236c236923622372236123722379214a'
                      '236e236f2372236d2361236c214b')
# the load answer step's last frame (sha256 8bc53327..., 151,723 dots),
# OBSERVED 2026-11-28 (the live run's the same, PNG byte for byte):
# MENDELS's whole zone, its system window with two messages, the title
# screen under the base, committed as docs/simpos/screens/mendels_zone.png;
# since the title raise step test_replay checks that the stop's frame
# differs from it only in the title screen's rectangle and the status band
ZONE = os.path.join(HERE, '..', 'docs', 'simpos', 'screens', 'mendels_zone.png')
# since the title raise step (2026-11-28): the replay's last frame, the
# zone with the title screen raised over the base, " end" and "please
# return" written (OBSERVED; the live run's the same, PNG byte for byte,
# and the same frame as the whole lift's with save memory enlarged, run
# on master 7528e34e's stand-ins), docs/simpos/screens/mendels_title_raised.png
RAISED = os.path.join(HERE, '..', 'docs', 'simpos', 'screens', 'mendels_title_raised.png')
RAISED_FRAME = ('e78ce6f9e63c1a18c29c027e1d2e64f0bd85896286f618c56486e14b9da2b8ee', 157381)


def load_tape():
    with open(TAPE) as f:
        return json.load(f)


class Run(unittest.TestCase):
    def test_tape(self):
        # the tape's own record: the live run's string I/O and its stop
        tape = load_tape()
        self.assertEqual(mendels.strings_io(tape), STRINGS_IO)
        self.assertEqual(tape['result']['stop'], STOP)
        self.assertEqual(len(tape['exchanges']), EXCHANGES)
        self.assertEqual(mendels.files_io(tape), FILES_IO)
        # PIMOS's console at the end (OBSERVED): the relink, and nothing
        # after it.  Before the FEP store step the runner's FEP answered
        # del_file/3's 204 abnormal, and the console ended "Unification
        # failure occurred !! ... Term1 : normal([delete("compiler.msg",D),
        # expunge(C)],B,A) Term2 : abnormal ... Job 4 was aborted ."
        w = tape['result']['window']
        self.assertTrue(w.endswith('Relink Succeeded\nShell>> '), w[-300:])
        self.assertNotIn('aborted', w)
        self.assertNotIn('failure', w)
        # mendel.exe's pathname as the PSI gives it (221: full_pathname/2,
        # no host prefix; fep.py's home file was PSI::>sys>...)
        self.assertIn('Load File : >sys>user>MENDEL>mendel.exe.1\n', w)

    def test_replay(self):
        # the PSI side, fed the tape: every packet it sends is the live
        # run's, it uses up the tape, and it stops where the live run did
        stop, psi, left = mendels.replay(TAPE)
        self.assertEqual('%s: %s' % (stop.cause, stop.detail), STOP)
        self.assertEqual(left, [])
        # since the load adapter (2026-11-28): phase/2 takes its
        # loaded_library(normal) clause; mdl_check after_KL1compiler/0
        # finds no TEMP>compiler.msg (readme.e: TEMP "no files") and says
        # so in the system window; phase(top) waits in top_menu's read; the
        # mendel_title process, sent "exit", writes " end" to its screen
        # (title.esp show/1), a permission(show) window under the base, so
        # the coordinator raises it (TM-225 p11 (3); coordinator.esp
        # held_back/3).  Since the title raise step (2026-11-28) the raise
        # lifts the base only over the title screen's rectangle (446 x 163,
        # 4,564 words; coordinator.esp lift_all_in/2), not whole (75,520
        # words, more than save memory's 65,536: the stop before); the
        # title screen then shows " end", "please return", and waits in
        # its read (title.esp:57), the run's stop: every process waits, and
        # PIMOS, given the last answers, sends nothing more
        # the adapter changed one packet, into the no-file branch's
        self.assertEqual([n.hex() for _r, n in psi.adapted], [LOAD_ANSWER_PACKET])
        # the stop's frame: the zone (every pane of show_all_window/1,
        # mendel_win.esp; the system window with system_io's two messages,
        # field_tree restore/2's "file not exist" (field_tree.esp:446-447)
        # and mdl_check open_file/3's (mdl_check.esp:131-134)) with the
        # title screen raised over the base and selected (its name in the
        # status band)
        import windev
        import winfb
        d = windev.device(psi.m)
        fr = d.frame
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), RAISED_FRAME)
        with open(RAISED, 'rb') as f:
            self.assertEqual(windev.png_bytes(fr), f.read())
        # and it is the load answer step's last frame (ZONE, the zone with
        # the title screen under the base) but for the title screen's
        # rectangle and the status band's window name (rows 950-967): the
        # raise changed nothing else
        with open(ZONE, 'rb') as f:
            zone = windev.png_rows(f.read())
        now = windev.png_rows(windev.png_bytes(fr))
        title = ((1 << 446) - 1) << (1280 - 417 - 446)
        changed = [y for y in range(1024) if (zone[y] ^ now[y]) & ~(title if 390 <= y < 553 else 0)]
        self.assertEqual((changed[0], changed[-1], len(changed)), (950, 967, 18))
        # the stack: the title screen on top, its under its own 4,564
        # words; the base under it, its under the cut form with nothing
        # under it (the title screen has left it)
        m = psi.m
        C = K.ClassRef('simpos##coordinator')
        ws, c = [], K.deref(m.get_slot(C, 'windows'))
        while isinstance(c, K.Cons):
            ws.append(K.deref(c.args[0]))
            c = K.deref(c.args[1])
        self.assertEqual([w.cid for w in ws], ['simpos##standard_io_window', 'mendel##base'])
        panes = [K.deref(m.get_slot(w, 'pane')) for w in ws]
        self.assertEqual([[K.resolve(m.get_slot(p, k)) for k in ('x', 'y', 'w', 'h')] for p in panes],
                         [[417, 390, 446, 163], [0, 0, 1280, 944]])
        self.assertEqual([str(K.resolve(m.get_slot(p, 'under'))) for p in panes],
                         ['[0,0,4564]',
                          '[cut,0 (a slot constant),0 (a slot constant),1280,944,0,none]'])
        # save memory at the stop (OBSERVED): one area, the title screen's
        # under; over the run no save reached past word 13,692 (three areas
        # of 4,564 at once during the raise: the base's part, the title
        # screen's image and its under)
        used, c = [], K.deref(m.get_slot(K.ClassRef('simpos##save_memory'), 'used'))
        while isinstance(c, K.Cons):
            used.append(str(K.resolve(c.args[0])))
            c = K.deref(c.args[1])
        self.assertEqual(used, ['[0,0,4564]'])
        saves = [a for op, a in d.log if op >> 4 == winfb.SAVE]
        self.assertEqual(max(a[5] + (a[3] + 15) // 16 * a[4] for a in saves), 13692)
        # the raise's three saves, each the title screen's rectangle: the
        # base's part (slot 2), the title screen's image (slot 1, while
        # lifted) and its new under (slot 0)
        self.assertEqual([a for a in saves[-3:]], [[2, 417, 390, 446, 163, 9128],
                                                   [1, 417, 390, 446, 163, 4564],
                                                   [0, 417, 390, 446, 163, 0]])
        # the FEP store step: PIMOS's compiler.msg is in the PSI's TEMP, the
        # one file there, with the loader's messages; nothing is left
        # deleted (235)
        import simpos_fs
        d = m.fs_walk(m.get_slot(K.ClassRef('simpos##directory'), 'root'), 'sys>user>MENDELuser>TEMP')
        files = mendels._entries(m, d)
        self.assertEqual([n for n, _f in files], ['compiler.msg'])
        self.assertEqual(simpos_fs.text_of(K.deref(m.get_slot(files[0][1], 'contents')).codes()),
                         COMPILER_MSG)
        self.assertEqual(K.deref(m.get_slot(d, 'deleted')), K.NIL)

    def test_library_restored(self):
        # object_lib restore/1 (object_lib.esp:29-31, 321-325) read the
        # HELD tree.obj and tree.key placed in >sys>user>MENDELuser>SYSTEM
        # (mendels.HELD_FILES): the object tree holds example1-3 and the
        # key tree's restore/2 took its first clause (change_net/2 set
        # net1); the archive has no tree.field, so field_tree restore/2
        # took its "file not exist" clause and holds nothing
        stop, psi, left = mendels.replay(TAPE)
        m = psi.m

        def slot(cid, name):
            return K.resolve(m.get_slot(K.ClassRef('mendel##' + cid), name))
        data = repr(slot('object_tree', 'mendel##object_tree$tree_data'))
        for name in ('example1', 'example2', 'example3'):
            self.assertIn(name, data)
        self.assertEqual(slot('key_tree', 'mendel##key_tree$current_net'), K.Atom('net1'))
        self.assertEqual(K.deref(m.get_slot(K.ClassRef('mendel##field_tree'),
                                            'mendel##field_tree$tree_data')), 0)

    def test_path_dialog(self):
        # init_path.esp's dialog after the path is typed, before y: the
        # frame committed as docs/simpos/screens/mendels_path.png
        import windev
        stop, psi, left = mendels.replay(TAPE, keys=['>sys>user>MENDELuser'], lenient=True)
        self.assertEqual(stop.cause, 'would suspend')
        self.assertIn('mendel##mendel_path', ' '.join(psi.where(12)))
        with open(SCREEN, 'rb') as f:
            self.assertEqual(windev.png_bytes(windev.device(psi.m).frame), f.read())

    @unittest.skipUnless(os.environ.get('MENDELS_LIVE'), 'MENDELS_LIVE=PROMPT.pkl runs PIMOS (~80 s)')
    def test_live(self):
        result, psi, _pim = mendels.live(os.environ['MENDELS_LIVE'], record=None)
        self.assertEqual(result['stop'], STOP)
        self.assertEqual(result['exchanges'], EXCHANGES)
        self.assertEqual([n.hex() for _r, n in psi.adapted], [LOAD_ANSWER_PACKET])
        import windev
        with open(RAISED, 'rb') as f:
            self.assertEqual(windev.png_bytes(windev.device(psi.m).frame), f.read())

    def test_adapter_off(self):
        # mendels.LOAD_ADAPTER off: the PSI is given PIMOS's own string,
        # loaded_library(normal([mendel:: example1, ...])), which the held
        # phase/2 has no clause for (the stop before 2026-11-28)
        saved = mendels.LOAD_ADAPTER
        mendels.LOAD_ADAPTER = False
        try:
            stop, psi, left = mendels.replay(TAPE)
        finally:
            mendels.LOAD_ADAPTER = saved
        self.assertEqual('%s: %s' % (stop.cause, stop.detail), STOP_NO_ADAPTER)
        self.assertEqual(psi.adapted, [])

    def test_load_adapter(self):
        # mendels.adapt_load_answer: PIMOS's io with normal(Modules) made
        # the no-file branch's packet byte for byte; the two strings
        # phase/2 has clauses for and every other packet passed as they
        # are; any other loaded_library string refused loudly
        import fep_bridge as FB
        tape = load_tape()
        ios = [bytes.fromhex(h) for e in tape['exchanges'] for h in e['to_psi']
               if FB.show(bytes.fromhex(h))[2] == 620]
        changed = [(r, mendels.adapt_load_answer(r)) for r in ios]
        self.assertEqual([n.hex() for r, n in changed if n != r], [LOAD_ANSWER_PACKET])

        def io(text):
            return bytes.fromhex('0000003200000000') + FB.fepm.pack_message([620, 0, FB.fepm.jis(text)])
        for text in ('loaded_library(normal)', 'loaded_library(abnormal)', 'start', 'normal([a:: b])'):
            self.assertEqual(mendels.adapt_load_answer(io(text)), io(text))
        self.assertEqual(mendels.adapt_load_answer(io('loaded_library(normal([p:: m]))')).hex(),
                         LOAD_ANSWER_PACKET)
        for text in ('loaded_library(normal(x))', 'loaded_library(usage)',
                     'loaded_library(normal([p:: m]),x)'):
            with self.assertRaises(K.Refusal):
                mendels.adapt_load_answer(io(text))

    def test_adapter_refusal_stops(self):
        # a loaded_library string the adapter does not know ends the run
        # with its refusal (the tape's string made normal(x))
        import fep_bridge as FB
        tape = load_tape()
        bad = bytes.fromhex('0000003200000000') + FB.fepm.pack_message(
            [620, 0, FB.fepm.jis('loaded_library(normal(x))')])
        for e in tape['exchanges']:
            e['to_psi'] = [bad.hex() if '236c236f2361236423652364' in h else h for h in e['to_psi']]
        stop, psi, left = mendels.replay(TAPE, tape=tape)
        self.assertEqual('%s: %s' % (stop.cause, stop.detail),
                         "mendels: load answer not adapted: 'loaded_library(normal(x))'")


class Compile(unittest.TestCase):
    def test_package(self):
        # the archive's ESP half, its 108 .esp/.es files, as one package
        # (install.e Step 5-6): 17
        # items the parser drops (mdl_ckpred, mdl_cksyn, mendelmain :476
        # `****`, obj_editor, tsl_input), no class refused whole, 371
        # predicates refused (1,122 before the built-ins, repeat and
        # components of 2026-11-27, 689 before vectors of up to 255
        # elements and floats, the temporary_menu step; 18 dropped and 402
        # refused before the window mixins step: mdl_ckutil.esp's `'/\'`
        # read as a quoted atom (asm/simpos_census/esplex.py) and number/1,
        # blt 13)
        self.assertEqual(len(mendels.esp_sources()), 108)
        ts, rep = mendels.compile_package()
        self.assertEqual(len(rep['dropped']), 17)
        self.assertEqual(rep['failed'], {})
        self.assertEqual(len(rep['refused']), 371)
        ids = {t.id for t in ts}
        for c in ('mendel##mendel_esp_device', 'mendel##mendel_loader', 'mendel##esp_utility',
                  'mendel##mendel_path', 'mendel##mendel_main'):
            self.assertIn(c, ids)

    def test_repeat(self):
        # `repeat` (espc split_repeat): the goals after it are retried
        # until they succeed; a slot is not undone on backtracking
        t = compile_one('''class rp has
attribute n := 0;
:loop(C, K, N) :- C!n := 0, repeat, C!n := C!n + 1, C!n >= K, !, N = C!n;
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##rp', 'loop', [3, K.Var()])
        self.assertEqual(K.resolve(r[1]), 3)

    def test_empty_vector(self):
        # `{}` in a head and in `X = {}` is the empty vector, pmi 30
        # get_vector_0 (KNOWN-PLAINTEXT: sancho1.esp:60, BCMLOGSEQ.ESP:541),
        # as when put (pmi b0): the shape of MENDELS mdl_ckutil.esp:150-160
        # message_type/2, which ends only because atom({}) is false and
        # the head `message_type({},"")` matches (a step limit guards it)
        t = compile_one('''class ev has
:mt(C, T, S) :- message_type(T, S);
:isatom(C) :- X = {}, atom(X);
:h(C, X, Y) :- h1(X, Y);
local
h1({}, empty);
h1(_, other);
message_type(T, S) :-
        ( T = {_, N}, M = 1 ; atom(T), N = {}, M = 2 ),
        !,
        message_type(N, S0),
        S = [M | S0];
message_type({}, []);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]), max_steps=100_000)
        (r,) = K.call_class_method(m, 'user##ev', 'mt', [K.Atom('file'), K.Var()])
        self.assertEqual(str(K.resolve(r[1])), '[2]')
        (r,) = K.call_class_method(m, 'user##ev', 'mt', [K.Vec([K.Atom('a'), K.Atom('b')]), K.Var()])
        self.assertEqual(str(K.resolve(r[1])), '[1,2]')
        self.assertEqual(K.call_class_method(m, 'user##ev', 'isatom', []), [])
        r = K.call_class_method(m, 'user##ev', 'h', [K.Vec([]), K.Var()])
        self.assertEqual(K.resolve(r[0][1]), K.Atom('empty'))
        # a vector with elements is not {} (the head's first clause skipped)
        r = K.call_class_method(m, 'user##ev', 'h', [K.Vec([K.Atom('a')]), K.Var()])
        self.assertEqual([K.resolve(x[1]) for x in r], [K.Atom('other')])
        r = K.call_class_method(m, 'user##ev', 'h', [K.Var(), K.Var()])
        self.assertIsInstance(K.deref(r[0][0]), K.Vec)
        self.assertEqual(K.deref(r[0][0]).args, [])

    def test_ch_string_string(self):
        # symbolizer get_ch_string_string/3 (kl0 model, INFERENCE): a
        # string datum written in double quotes, a quote doubled
        t = compile_one('''class cs has
:w(C, S, T) :- :get_ch_string_string(#symbolizer, S, T);
end.''')
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##cs', 'w', [K.Str('compiler.msg'), K.Var()])
        self.assertEqual(K.deref(r[1]).text, '"compiler.msg"')
        (r,) = K.call_class_method(m, 'user##cs', 'w', [K.Str('a"b'), K.Var()])
        self.assertEqual(K.deref(r[1]).text, '"a""b"')

    def test_freeze_melt(self):
        # freeze/2 and melt/2 (blt 3e, 3f; ESP manual program-e.tex
        # 1895-1939): each melt gives fresh variables, shared as in the
        # term frozen
        t = compile_one('''class fz has
:t(C, X, Y) :- freeze({f, A, A, B}, F), melt(F, X), melt(F, Y);
:after(C, X) :- freeze({f, A}, F), A = 1, melt(F, X);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##fz', 't', [K.Var(), K.Var()])
        x, y = [K.deref(a) for a in r]
        xe = [K.deref(e) for e in x.args]
        ye = [K.deref(e) for e in y.args]
        self.assertIs(xe[1], xe[2])
        self.assertIsNot(xe[1], xe[3])
        self.assertIsNot(xe[1], ye[1])
        self.assertIsInstance(xe[1], K.Var)
        # the frozen copy keeps no link to the term frozen: binding A after
        # the freeze leaves the melted copy's variable unbound
        (r,) = K.call_class_method(m, 'user##fz', 'after', [K.Var()])
        self.assertIsInstance(K.deref(K.deref(r[0]).args[1]), K.Var)

    def test_component(self):
        # a component's slot is pkg##class$name (KNOWN-PLAINTEXT
        # qxt##name_table new_expr/2 @4e), read and set by that name
        t = compile_one('''class cm has
component buf := 0;
:put(C, X) :- C!buf := X;
:get(C, X) :- X = C!buf;
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        self.assertEqual(len(K.call_class_method(m, 'user##cm', 'put', [7])), 1)
        (r,) = K.call_class_method(m, 'user##cm', 'get', [K.Var()])
        self.assertEqual(K.resolve(r[0]), 7)
        self.assertIn('user##cm$buf', t.symbols)

    def test_vector_puts(self):
        # vectors of 1, 5, 6 and 8 elements built in a body: put_vector_1
        # .. put_vector_6 (b1-b6) and put_vector_n (b7 A 00 n), each row
        # KNOWN-PLAINTEXT (kl0_opcodes.tsv); MENDELS's items
        # {Label, common, Id, Doc, off} (lib_win.esp) are 5-vectors
        t = compile_one('''class vp has
:v(C, X, A, B, D, E) :- id({X}, A), id({X, common, X, _, off}, B), id({X, 2, 3, 4, 5, X}, D),
        id({X, 2, 3, 4, 5, 6, 7, X}, E);
local
id(V, V);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##vp', 'v', [K.Atom('x')] + [K.Var() for _ in range(4)])
        got = [repr(K.resolve(a)) for a in r[1:]]
        self.assertEqual(got[0], '{x}')
        self.assertEqual(got[1].split(',')[:3], ['{x', 'common', 'x'])
        self.assertTrue(got[1].endswith(',off}'))
        self.assertEqual(got[2], '{x,2,3,4,5,x}')
        self.assertEqual(got[3], '{x,2,3,4,5,6,7,x}')
        text = espc.listing(t)
        for op in ('b1', 'b5', 'b6', 'b7'):
            self.assertRegex(text, r'\bpmi %s\b' % op, op)

    def test_floats(self):
        # floats (kl0.Flt; kl0_opcodes.tsv rows 6c, 6d, a8 with a float
        # cell): MENDELS's create_all_window/1 sizes (mendel_win.esp:
        # `Gh_f is BH_f * 0.8 - (Title_hf * 3.0)`) on the screen's 944
        # and a 21-dot title; X/Y on two registers (blt 43); the integer
        # back toward zero
        t = compile_one('''class fl has
:gh(C, BH, Title_h, Graph_h) :-
        integer_to_floating_point(BH, BH_f),
        integer_to_floating_point(Title_h, Title_hf),
        Gh_f is BH_f * 0.8 - (Title_hf * 3.0),
        floating_point_to_integer(Gh_f, Graph_h);
:quot(C, X, Y, Q) :- Q = X / Y;
:fq(C, X, Y, Q) :- integer_to_floating_point(X, F), integer_to_floating_point(Y, G),
        H = F / G + 0.5, floating_point_to_integer(H, Q);
end.''')
        self.assertEqual(t.refusals, [])
        m = K.Machine(espc.library([t]))
        (r,) = K.call_class_method(m, 'user##fl', 'gh', [944, 21, K.Var()])
        # single precision: 944 * 0.8 = 755.2, - 63 = 692.2, toward zero
        self.assertEqual(K.resolve(r[2]), 692)
        (r,) = K.call_class_method(m, 'user##fl', 'quot', [17, 5, K.Var()])
        self.assertEqual(K.resolve(r[2]), 3)
        (r,) = K.call_class_method(m, 'user##fl', 'fq', [7, 2, K.Var()])
        self.assertEqual(K.resolve(r[2]), 4)        # 3.5 + 0.5
        text = espc.listing(t)
        self.assertRegex(text, r'\bblt 6c\b')
        self.assertRegex(text, r'\bblt 6d\b')
        self.assertRegex(text, r'\bblt 43\b')
        self.assertRegex(text, r'pmi a8 .*\n.*float 0\.8')
        # a float with an integer is refused when run (no witness of a
        # mixed operation)
        t2 = compile_one('''class fm has
:m(C, X, R) :- integer_to_floating_point(X, F), R = F * X;
end.''')
        m2 = K.Machine(espc.library([t2]))
        with self.assertRaises(K.Refusal):
            K.call_class_method(m2, 'user##fm', 'm', [3, K.Var()])


def compile_one(text):
    ts, failed = espc.compile_text(text, 'user')
    assert not failed, failed
    (t,) = ts
    return t


class Simpos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.psi = mendels.PsiSide()
        cls.m = cls.psi.m

    def send(self, obj, name, *args):
        m = self.m
        regs = list(args) + [obj]
        return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, regs)]

    def string(self, text):
        s = K.Str('')
        s.text = text
        return s

    def buffer(self):
        (r,) = K.call_class_method(self.m, 'simpos##standard_io_buffer', 'create', [K.Var()])
        return K.deref(r[0])

    def test_io_buffer_printed(self):
        # the ESP manual's Example 3 (program-e.tex 6733-6745), PRINTED
        self.m.reset()
        b = self.buffer()
        self.send(b, 'putl', self.string('p(1,2).'))
        self.send(b, 'putl', self.string('[1,2].'))
        (cp,) = self.send(b, 'gett', K.Var())
        self.assertEqual(repr(cp[0]), repr(K.resolve(read('p(1,2)'))))
        (ls,) = self.send(b, 'gett', K.Var())
        self.assertEqual(repr(ls[0]), repr(K.resolve(read('[1,2]'))))
        self.send(b, 'putt', read('[1,2]'))
        self.send(b, 'putt', read('p(1,2)'))
        (s,) = self.send(b, 'getl', K.Var())
        self.assertEqual(K.deref(s[0]).text, '[1,2]p(1,2)')
        with self.subTest('end-of-text term (INFERENCE, MENDELS main.kl1 call_loop/3)'):
            self.send(b, 'reset')
            self.send(b, 'putl', self.string('load_library'))
            self.send(b, 'reread')
            (a,) = self.send(b, 'gett', K.Var())
            self.assertEqual(repr(a[0]), repr(K.Atom('load_library')))

    def test_reader_package_colon(self):
        # `Package::Module`, as PIMOS writes the loaded modules
        t = read('normal([mendel::example1])')
        self.assertEqual(repr(K.resolve(t)), '{normal,[{::,mendel,example1}]}')

    def test_getl(self):
        # pmacs_window getl/2 (init_path.esp read_string/3: the old answer
        # put at the point, then getl): after a prompt putl/2 wrote, `abc`
        # in the buffer and the keys d e BS f RETURN, the line is abcdf
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##pmacs_window', 'create', [K.NIL, K.Var()])
        w = K.deref(r[1])
        self.send(w, 'activate')
        ((b,),) = self.send(w, 'current_buffer', K.Var())
        self.send(w, 'putl', self.string('prompt'))
        self.send(b, 'insert_string', self.string('abc'))
        i = m.get_slot(w, 'interpreter')
        d, e, f = K.Str('def').codes()       # the codes the keys give (fep_bridge.key_script)
        for x in (d, e, 8, f, 13):
            self.send(i, 'input', x)
        ((line,),) = self.send(w, 'getl', K.Var())
        self.assertEqual(K.deref(line).text, 'abcdf')

    def test_library_utility(self):
        # the loader's queries (loader.esp load_MENDEL/2) over kl0's library,
        # and load/2's `Loading <id>...` lines (ds_bep.esp:1992) to the
        # output set_output/2 gave
        m = self.m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##library_utility', 'create', [K.Var()])
        ut = K.deref(r[0])
        self.assertEqual(repr(K.resolve(self.send(ut, 'get_packages_with_wildcard',
                                                  self.string('mend*'), K.Var())[0][1])), '[mendel]')
        ((_, _, ids),) = self.send(ut, 'get_classes', self.string('mendel'), K.Atom('all'), K.Var())
        names = repr(ids)
        self.assertIn('mendel##mendel_main', names)
        self.assertNotIn('simpos##', names)
        ((_, _, _, ids),) = self.send(ut, 'get_classes_with_wildcard', self.string('mendel'),
                                      self.string('mendel_er*'), K.Atom('all'), K.Var())
        self.assertEqual(repr(ids), '[mendel##mendel_error]')
        # the output here a standard_io_buffer (its putl/2 a line)
        out = self.buffer()
        self.send(ut, 'set_output', out)
        self.assertEqual(len(self.send(ut, 'load', ids)), 1)
        self.assertEqual(K.deref(m.get_slot(out, 'text')).text, 'Loading mendel##mendel_error...\n')

    def test_io_window_title_and_object(self):
        # loader.esp:12-15: create/3's option title("WAIT !") is the
        # window's title; symbolizer is_object/2 on it and on the slot
        # value 0 the loader tests (load_MENDEL/2)
        m = self.m
        m.reset()
        opts = K.Cons(K.Vec([K.Atom('title'), self.string('WAIT !')]), K.NIL)
        (r,) = K.call_class_method(m, 'simpos##standard_io_window', 'create', [opts, K.Var()])
        w = K.deref(r[1])
        self.assertEqual(K.deref(m.get_slot(w, 'title')).text, 'WAIT !')
        sym = K.ClassRef('simpos##symbolizer')
        self.assertEqual(len(list(m.solve_send(sym, 'is_object', [w, sym]))), 1)
        self.assertEqual(list(m.solve_send(sym, 'is_object', [0, sym])), [])

    def test_models_labelled(self):
        # every kl0 model mendels_simpos installs has a label, and only those
        import mendels_simpos
        mine = {k for k, f in K.SIMPOS_MODELS.items() if getattr(f, '__module__', '') == 'mendels_simpos'}
        self.assertEqual(mine, set(mendels_simpos.LABELS))
        for k, v in mendels_simpos.LABELS.items():
            self.assertRegex(v, r'^(RECONSTRUCTED-FROM-MANUAL|INFERENCE|OURS)', k)

    def test_check_pathname(self):
        self.m.reset()
        p = self.string('>sys>user>MENDELuser')
        (r,) = K.call_class_method(self.m, 'simpos##pathname', 'check_pathname', [p, K.Var()])
        self.assertEqual(K.deref(r[1]).text, '>sys>user>MENDELuser')
        self.assertEqual(K.call_class_method(self.m, 'simpos##pathname', 'check_pathname',
                                             [self.string(''), K.Var()]), [])


class Menus(unittest.TestCase):
    """The temporary_menu stand-in (standin/temporary_menu.esp) through
    two other held users, run whole on the coordinator with the mouse:
    disc's system_data init/1 (the HELD files system_data.esp and
    util.esp, IFS natural-lang disc) and euod's syntax_print goal/1 (the
    HELD clause def.esp:821-835, verbatim, in an OURS harness class).
    Each program is started from the system menu after the login, as
    window M10's are (psi/test_espc.py pmacs_run), with the mouse at AT,
    so the menu's top-left is there."""
    AT = (300, 250)
    # OURS harness: disc's program calls :init(#system_data); the two
    # classes its select/2 sends to when `init` is chosen record the call
    DISC = """class tm_disc has
nature as_program;
attribute calls := [];
:note(Class, X) :- Class!calls := [X | Class!calls];
instance
:goal(P) :- :init(#system_data), :note(#tm_disc, done);
end.
class io_file has
:init(Class) :- :note(#tm_disc, init);
end.
class new_data_pool has
:create_chapter(Class);
end."""
    # OURS harness round the HELD goal/1 of euod's syntax_print: its
    # editor and theory database answer with atoms, print_file/2 and
    # print_buffer/3 (held ones print on a hardcopy window) record
    EUOD = """class tm_euod has
nature as_program;
attribute calls := [];
:note(Class, X) :- Class!calls := [X | Class!calls];
:create(Class, Obj) :- :new(Class, Obj), Obj!editor := Class, Obj!theory_db := Class;
:current_buffer(Class, buffer);
:get_font(Class, font);
:get_theory_name(Class, theory);
instance
attribute editor, theory_db;
%s
    :print_file(Obj,Theory_name):- :note(#tm_euod, {print_file, Theory_name});
    :print_buffer(Obj,Buffer,Font):- :note(#tm_euod, {print_buffer, Buffer, Font});
end.
class messenger has
:show(Class, S) :- :note(#tm_euod, shown);
end."""
    # frames: (sha256 of the PBM, set dots); the euod menu's committed as
    # docs/simpos/screens/temporary_menu.png
    SCREEN = os.path.join(HERE, '..', 'docs', 'simpos', 'screens', 'temporary_menu.png')

    @staticmethod
    def euod_goal():
        import held
        lines = held.member_text('euod_def').splitlines()
        g = lines[820:835]
        assert g[0].strip() == ':goal(Obj):-' and g[-1].strip().startswith(':show(#messenger,'), g
        return '\n'.join(g)

    def run_menu(self, prog, *batches):
        import fep_bridge as FB
        import held
        psi = FB.PsiSide()
        m = psi.m
        if prog == 'disc':
            srcs = [espc.esplex.decode(held.member_text(n).encode('latin-1'))[0]
                    for n in ('disc_system_data', 'disc_util')] + [self.DISC]
        else:
            srcs = [self.EUOD % self.euod_goal()]
        for src in srcs:
            ts, failed = espc.compile_text(src, 'simpos')
            self.assertEqual(failed, {})
            for t in ts:
                m.lib.add(t)
        psi.user = [FB.mouse('rr', *FB.MENU_AT), FB.mouse('l', *FB.LOGIN_ITEM_AT)]

        def start(mm):
            # disc's class slot opens font:kanji_16.font (system_data.esp:
            # 11-12): the substitute entry MENDELS's run has
            mendels.substitute_font(mm, 'kanji_16.font', 'test_11.font')
            C = K.ClassRef('simpos##coordinator')
            item = K.Vec([FB.jstr('TM'), K.Atom('tm_' + prog)])
            mm.set_slot(C, 'menu', K.Cons(K.Cons(item, K.NIL), mm.get_slot(C, 'menu')))
            return [self.move(*self.AT), K.Atom('invoke_system_menu'),
                    K.Vec([K.Atom('select'), FB.jstr('TM')])]
        rest = [start] + [list(b) for b in batches]

        def exchange(out):
            if rest and not psi.shell:
                b = rest.pop(0)
                psi.shell, psi.getl = list(b(m) if callable(b) else b), True
            return []
        stop = psi.run(exchange)
        self.assertEqual((rest, psi.shell), ([], []))
        self.assertEqual(stop.cause, 'would suspend')
        return m

    @staticmethod
    def move(x, y):
        return K.Vec([K.Atom('move'), x, y])

    @staticmethod
    def left(x, y):
        import fep_bridge as FB
        return FB.mouse('l', x, y)

    @staticmethod
    def calls(m, cls):
        out, t = [], K.deref(m.get_slot(K.ClassRef('simpos##' + cls), 'calls'))
        while isinstance(t, K.Cons):
            out.append(repr(K.resolve(t.args[0])))
            t = K.deref(t.args[1])
        return out

    def pane(self, m):
        C = K.ClassRef('simpos##coordinator')
        P = K.deref(m.get_slot(C, 'menu_pane'))
        if P == 0:
            return None
        return tuple(K.resolve(m.get_slot(P, k)) for k in ('x', 'y', 'w', 'h', 'items_top', 'label'))

    def test_euod_shown(self):
        # euod's `WHICH?` menu (create/3 with items_list of 5-field items
        # and title, then show/1, read/2): at the mouse, titled, two items
        # (the frame committed); nothing chosen yet
        import windev
        m = self.run_menu('euod')
        self.assertEqual(self.pane(m), (300, 250, 180, 55, 271, K.Atom('on')))
        fr = windev.device(m).frame
        self.assertEqual(windev.read_cells(fr, 302, 253, 16, 1), ['     WHICH?'])
        with open(self.SCREEN, 'rb') as f:
            self.assertEqual(windev.png_bytes(fr), f.read())
        self.assertEqual(self.calls(m, 'tm_euod'), [])

    def test_euod_pick(self):
        # a left click on the second item: read/2 gives its item_id
        # saved_syntax (TM-125 p18), the held goal takes that branch:
        # get_theory_name/2, print_file/2, the messenger; the menu is off
        # the screen (read/2 takes it down: euod hides nothing)
        m = self.run_menu('euod', [self.move(390, 295), self.left(390, 295)])
        self.assertEqual(self.calls(m, 'tm_euod'), ['shown', '{print_file,theory}'])
        self.assertIsNone(self.pane(m))

    def test_euod_leave(self):
        # the mouse leaves the menu: read/2 gives abort (TM-125 p18), which
        # neither branch of the held goal takes: nothing printed
        m = self.run_menu('euod', [self.move(390, 295), self.move(100, 100)])
        self.assertEqual(self.calls(m, 'tm_euod'), [])
        self.assertIsNone(self.pane(m))

    def test_disc_loop(self):
        # disc's initialisation menu (label_flag(off), label_font, set_font,
        # the show/read/hide loop of system_data init/1): no title strip;
        # a click on the no_select first line does nothing; `init` (the
        # third item) is answered and select/2 runs (:init(#io_file)),
        # fails as held (`!, fail`) and the menu is shown again; the mouse
        # leaving answers abort and init/1 returns
        import windev
        m = self.run_menu('disc')
        self.assertEqual(self.pane(m), (300, 250, 246, 84, 252, K.Atom('off')))
        self.assertEqual((windev.pbm_sha256(windev.device(m).frame), windev.device(m).frame.count()),
                         self.DISC_FRAME)
        m = self.run_menu('disc', [self.left(400, 260)])
        self.assertEqual(self.pane(m), (300, 250, 246, 84, 252, K.Atom('off')))
        self.assertEqual(self.calls(m, 'tm_disc'), [])
        m = self.run_menu('disc', [self.left(400, 260)], [self.left(400, 292)])
        self.assertEqual(self.calls(m, 'tm_disc'), ['init'])
        # shown again at the mouse, where the click was (TM-125 p7)
        self.assertEqual(self.pane(m), (400, 292, 246, 84, 294, K.Atom('off')))
        m = self.run_menu('disc', [self.left(400, 292)], [self.move(100, 100)])
        self.assertEqual(self.calls(m, 'tm_disc'), ['done', 'init'])
        self.assertIsNone(self.pane(m))

    DISC_FRAME = ('7dd50c95d2f7a0e8cea089df0aab41fcdbbc58d97a473462f7eae07b000d77ad', 103510)

    def test_methods(self):
        # the methods no run above reaches, on MENDELS's own `Change phase
        # ?` menu (mendelmain.esp:69-72): add_item/3 at a position and
        # add_items/3 (TM-125 p15), delete_item/2 by label, set_title/2,
        # set_item_status/3 kept, beep/1 counted, kill/1 (`alive` no, disc
        # util.esp:148), clear_items/1
        psi = mendels.PsiSide()
        m = psi.m
        m.reset()

        def s(text):
            x = K.Str('')
            x.text = text
            return x

        def item(label, value):
            return K.Vec([s(label), K.Atom('common'), K.Atom(value), K.Var()])

        def send(obj, name, *args):
            return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, list(args) + [obj])]

        opts = K.Cons(K.Vec([K.Atom('title'), s('Change phase ?')]),
                      K.Cons(K.Vec([K.Atom('items_list'),
                                    K.Cons(item('    Yes    ', 'yes'), K.Cons(item('    No     ', 'no'), K.NIL))]),
                             K.NIL))
        (r,) = K.call_class_method(m, 'simpos##temporary_menu', 'create', [opts, K.Var()])
        M = K.deref(r[1])

        def labels():
            out, t = [], K.deref(m.get_slot(M, 'items'))
            while isinstance(t, K.Cons):
                out.append(K.deref(K.deref(t.args[0]).args[0]).text.strip())
                t = K.deref(t.args[1])
            return out
        self.assertEqual(labels(), ['Yes', 'No'])
        self.assertEqual(K.deref(m.get_slot(M, 'title')).text, 'Change phase ?')
        send(M, 'add_item', item('Maybe', 'maybe'), 1)
        self.assertEqual(labels(), ['Yes', 'Maybe', 'No'])
        send(M, 'add_items', K.Cons(item('A', 'a'), K.Cons(item('B', 'b'), K.NIL)), 3)
        self.assertEqual(labels(), ['Yes', 'Maybe', 'No', 'A', 'B'])
        send(M, 'delete_item', s('Maybe'))
        self.assertEqual(labels(), ['Yes', 'No', 'A', 'B'])
        send(M, 'set_title', s('T'))
        self.assertEqual(K.deref(m.get_slot(M, 'title')).text, 'T')
        send(M, 'set_item_status', K.Atom('yes'), K.Atom('on'))
        self.assertEqual(repr(K.resolve(m.get_slot(M, 'status'))), '[[yes,on]]')
        send(M, 'beep')
        self.assertEqual(K.resolve(m.get_slot(M, 'beeps')), 1)
        send(M, 'kill')
        self.assertEqual(K.resolve(m.get_slot(M, 'alive')), K.Atom('no'))
        send(M, 'clear_items')
        self.assertEqual(labels(), [])


class Pieces(unittest.TestCase):
    """The smaller pieces of the window mixins step that no run above
    tells apart."""

    def test_number(self):
        # number/1 (blt 13, kl0_opcodes.tsv): an integer or a float, not an
        # atom or a variable
        t = compile_one('''class nb has
:n(C, X, yes) :- number(X), !;
:n(C, _, no);
:f(C, X, R) :- integer_to_floating_point(X, F), :n(C, F, R);
end.''')
        self.assertEqual(t.refusals, [])
        self.assertIn('13 ', espc.listing(t))
        m = K.Machine(espc.library([t]))
        for x, want in ((3, 'yes'), (K.Atom('a'), 'no'), (K.Var(), 'no')):
            (r,) = K.call_class_method(m, 'user##nb', 'n', [x, K.Var()])
            self.assertEqual(K.resolve(r[1]), K.Atom(want))
        (r,) = K.call_class_method(m, 'user##nb', 'f', [2, K.Var()])
        self.assertEqual(K.resolve(r[1]), K.Atom('yes'))

    def test_array(self):
        # array (standin/array.esp): put_at/3 and get_at/3 (value, then
        # index from 0), put_contents/2 and get_contents/2
        m = mendels.PsiSide().m
        m.reset()
        (r,) = K.call_class_method(m, 'simpos##array', 'create', [K.Var(), 3])
        A = K.deref(r[0])

        def send(name, *args):
            return [[K.resolve(a) for a in args] for _ in m.solve_send(A, name, list(args) + [A])]
        send('put_contents', K.Cons(10, K.Cons(11, K.Cons(12, K.NIL))))
        self.assertEqual(send('get_at', K.Var(), 0), [[10, 0]])
        self.assertEqual(send('get_at', K.Var(), 2), [[12, 2]])
        send('put_at', 99, 1)
        self.assertEqual(repr(send('get_contents', K.Var())[0][0]), '[10,99,12]')
        self.assertEqual(send('get_at', K.Var(), 3), [])


class Mixins(unittest.TestCase):
    """The window mixins (labeled_sash, as_input, as_superior,
    inferior_window, with_shared_window, with_superior_input_buffer and
    the composite menus: standin/basic_window.esp and its neighbours)
    through two other held users, run whole on the coordinator with the
    mouse, as Menus's are:

    - icotext (IFS natural-lang): the HELD class kakari_super_window
      (kkr_super_win.esp, whole: with_icon, labeled_sash, as_superior,
      as_input, as_mouse_input, inferior_window) made by its own
      create_window/3; inside it the HELD command bar of ki_window.esp
      create_comand_win/2 (a multi_column_menu_with_superior_input_buffer,
      clause verbatim); read by the HELD read_loop/1 of kkr_main.esp
      (clause verbatim), whose `exit` ends it;
    - disc (IFS natural-lang): the HELD make_inter_menu/2 of disp_win.esp
      (clause verbatim: an essential_scrolling_menu_with_superior_input_
      buffer filling its superior, titled " No."), inside MENDELS's own
      HELD class base (win_class.esp:38-47), read by base's read/3.

    The harness classes (tm_kkr, tm_disc2, and kakari_main, which
    kakari_super_window's after-demon of activate/1 sends to) are OURS."""
    # OURS harness round icotext's held clauses (%s: create_comand_win/2,
    # then read_loop/1)
    KKR = """class tm_kkr has
nature as_program;
attribute calls := [], super_win;
:note(Class, X) :- Class!calls := [X | Class!calls];
:exit(Class) :- :note(#tm_kkr, exit);
%s
instance
:goal(P) :-
        Class = #tm_kkr,
        :create(#font, "font:kanji_16.font", Font),
        :create_window(#kakari_super_window, Font, Super),
        Class!super_win := Super,
        create_comand_win(Super, Comand),
        :activate(Super),
        :activate(Comand),
        :note(#tm_kkr, shown),
        :read_loop(Class);
local
%s
end.
class kakari_main has
:select_kakari_structure(Class) :- :note(#tm_kkr, select);
end."""
    # OURS harness round disc's held make_inter_menu/2 (%s), under
    # MENDELS's held base (%s)
    DISC = """class tm_disc2 has
nature as_program;
attribute calls := [], inter_menup, inter_menuw, font;
:note(Class, X) :- Class!calls := [X | Class!calls];
instance
:goal(P) :-
        Class = #tm_disc2,
        :create(#font, "font:kanji_16.font", Font),
        Class!font := Font,
        :create(#base, [size(400, 300), position(100, 100), title("MENDELS base")], Base),
        Class!inter_menup := Base,
        make_inter_menu(Class, Base),
        Menu = Class!inter_menuw,
        :add_items(Menu, [{"1", common, one, _}, {"2", common, two, _}], 1),
        :activate(Base),
        :activate(Menu),
        :note(#tm_disc2, shown),
        :read(Base, Win, Data),
        (Win == Menu, !, :note(#tm_disc2, {menu, Data}) ; :note(#tm_disc2, {other, Data}));
local
%s
end.
%s"""

    @staticmethod
    def held_lines(name, first, last, head):
        import held
        lines = held.member_text(name).splitlines()[first - 1:last]
        assert lines[0].strip().startswith(head), lines[0]
        return espc.esplex.decode('\n'.join(lines).encode('latin-1'))[0]

    def run_prog(self, prog, *batches):
        import fep_bridge as FB
        import held
        psi = FB.PsiSide()
        m = psi.m
        if prog == 'kkr':
            srcs = [espc.esplex.decode(held.member_text('icotext_kkr_super_win').encode('latin-1'))[0],
                    self.KKR % (self.held_lines('icotext_kkr_main', 93, 107, ':read_loop('),
                                self.held_lines('icotext_ki_window', 68, 79, 'create_comand_win('))]
        else:
            import ifs_sweep as X
            base = espc.esplex.decode(X.archive(mendels.ARCHIVE)['mendels/win_class.esp'])[0]
            base = base[base.index('class base has'):]
            base = base[:base.index('end.') + 4]
            srcs = [self.DISC % (self.held_lines('disc_disp_win', 318, 324, 'make_inter_menu('), base)]
        for src in srcs:
            ts, failed = espc.compile_text(src, 'simpos')
            self.assertEqual(failed, {})
            for t in ts:
                m.lib.add(t)
        psi.user = [FB.mouse('rr', *FB.MENU_AT), FB.mouse('l', *FB.LOGIN_ITEM_AT)]

        def start(mm):
            mendels.substitute_font(mm, 'kanji_16.font', 'test_11.font')
            C = K.ClassRef('simpos##coordinator')
            item = K.Vec([FB.jstr('TM'), K.Atom('tm_' + prog)])
            mm.set_slot(C, 'menu', K.Cons(K.Cons(item, K.NIL), mm.get_slot(C, 'menu')))
            return [K.Atom('invoke_system_menu'), K.Vec([K.Atom('select'), FB.jstr('TM')])]
        rest = [start] + [list(b) for b in batches]

        def exchange(out):
            if rest and not psi.shell:
                b = rest.pop(0)
                psi.shell, psi.getl = list(b(m) if callable(b) else b), True
            return []
        stop = psi.run(exchange)
        return stop, m

    def calls(self, m, cls):
        return Menus.calls(m, cls)

    SCREENS = os.path.join(HERE, '..', 'docs', 'simpos', 'screens')
    # frames: (sha256 of the PBM, set dots), OBSERVED 2026-11-27; the
    # shown frames committed as docs/simpos/screens/mendels_mixins_*.png
    KKR_FRAME = ('9068ca553a3a4b7e9e081d27c6a2de593a054653db9a7810dbbe03b86085f558', 112499)
    DISC_FRAME = ('8d2c3a03f81546c9ce29782204c977c0ecca31f6974fa65bc21a2b856d948eeb', 108737)

    def frame(self, m):
        import windev
        fr = windev.device(m).frame
        return (windev.pbm_sha256(fr), fr.count()), windev.png_bytes(fr)

    def test_icotext_shown(self):
        # kakari_super_window (its held create_window/3: size, position,
        # label font, title) with the held command bar inside it at
        # (0, 190), 1200 wide, cut at the superior's inside; the bar's
        # label off, its 14 one-item columns centred (the kanji items drawn
        # as boxes: font:kanji_16.font is test_11.font, no kanji); the
        # after-demon of activate/1 ran (select)
        stop, m = self.run_prog('kkr')
        self.assertEqual(stop.cause, 'would suspend')
        self.assertEqual(self.calls(m, 'tm_kkr'), ['shown', 'select'])
        got, png = self.frame(m)
        self.assertEqual(got, self.KKR_FRAME)
        with open(os.path.join(self.SCREENS, 'mendels_mixins_icotext.png'), 'rb') as f:
            self.assertEqual(png, f.read())

    def test_icotext_exit(self):
        # a left click on `exit`: the bar's input goes to its superior's
        # buffer (with_superior_input_buffer), the held read_loop reads it
        # with read/3 (as_superior) and calls exit/1
        stop, m = self.run_prog('kkr', [Menus.left(705, 271)])
        self.assertEqual(self.calls(m, 'tm_kkr'), ['exit', 'shown', 'select'])

    def test_disc_shown(self):
        # MENDELS's base (labeled_sash, as_input, as_superior,
        # inferior_window, with_shared_window) with disc's menu filling
        # its inside: the menu's title " No." in its label strip, its
        # no_select line blank, the two items added
        stop, m = self.run_prog('disc2')
        self.assertEqual(stop.cause, 'would suspend')
        self.assertEqual(self.calls(m, 'tm_disc2'), ['shown'])
        got, png = self.frame(m)
        self.assertEqual(got, self.DISC_FRAME)
        with open(os.path.join(self.SCREENS, 'mendels_mixins_disc.png'), 'rb') as f:
            self.assertEqual(png, f.read())

    def test_disc_pick(self):
        # a left click on the no_select line does nothing; on "2": base's
        # read/3 answers the menu and its item_id
        stop, m = self.run_prog('disc2', [Menus.left(122, 149)])
        self.assertEqual(self.calls(m, 'tm_disc2'), ['shown'])
        stop, m = self.run_prog('disc2', [Menus.left(122, 181)])
        self.assertEqual(self.calls(m, 'tm_disc2'), ['{menu,two}', 'shown'])


class MethodEditor(unittest.TestCase):
    """The standard_io_window inferior step (2026-11-27): a
    standard_io_window placed inside a superior (standin/
    standard_io_window.esp "THE INFERIOR FORM", inferior_io_form.esp), and
    MENDELS's title screen (title.esp), each run on the coordinator as
    Mixins's are.

    - med: two standard_io_windows made as MENDELS's method editor makes
      meth_title and junk_title (med_win.esp create_other/1's options,
      verbatim), placed inside MENDELS's HELD class base by the HELD
      set_window_attribute/4 (med_win.esp:135-138, clause verbatim); junk
      written to before it gets its superior (as graph_sel.esp:31-34
      does); meth written as med_show.esp does (clear_line/1 then
      put_line/2, twice); then base's read/3, as med_window read/3
      (med_win.esp:319-325) reads its panes;
    - title: MENDELS's HELD class mendel_title (title.esp, whole), its
      start/1 run as esp_device.esp:99 runs it: the title screen drawn by
      its own process, which then waits on its stream.

    The harness classes (tm_med, tm_title) are OURS."""
    MED = """class tm_med has
nature as_program;
attribute calls := [], base, meth, junk;
:note(Class, X) :- Class!calls := [X | Class!calls];
instance
:goal(P) :-
        Class = #tm_med,
        :create(#base, [size(600, 200), position(100, 100), title("MENDELS base")], Base),
        Class!base := Base,
        :create(#standard_io_window,[
                nature([with_superior_input_buffer,with_shared_window]),
                label_flag(off),
                margin_flag(off),
                permission(out)
                ],MethTL),
        :erase_cursor(MethTL),
        :create(#standard_io_window,[
                nature([with_superior_input_buffer,with_shared_window]),
                label_flag(off),
                margin_flag(off),
                permission(out)
                ],JunkTL),
        :write_line(JunkTL, "junk"),
        Class!meth := MethTL, Class!junk := JunkTL,
        :get_inside_size(Base, BaseIW, _),
        MethTL_W is BaseIW / 2,
        set_window_attribute(MethTL,(0,0),(MethTL_W,20),Base),
        set_window_attribute(JunkTL,(MethTL_W,0),(MethTL_W,20),Base),
        :activate(Base),
        :activate(MethTL),
        :activate(JunkTL),
        :clear_line(MethTL),
        :put_line(MethTL, "meth"),
        :clear_line(MethTL),
        :put_line(MethTL, "meth    ( current : example1 )"),
        :note(#tm_med, shown),
        :read(Base, Win, Data),
        (Win == MethTL, !, :note(#tm_med, {meth, Data}) ; :note(#tm_med, {other, Data}));
local
%s
end.
%s"""
    # MENDELS's system window step (2026-11-27): a mendel_pmacs (MENDELS's
    # HELD class: with_superior_input_buffer, pmacs_window) made inside the
    # HELD base with create_system_window/6's options (mendel_win.esp:771-
    # 773, but editor(#mendel_editor), whose class needs most of the
    # method editor, left out: OURS), written before and after it is
    # shown, more lines than it holds and one longer than a row (putl/2,
    # flash/1 as system_io.esp putl/2 writes), then clicked and read by
    # base's read/3
    SYS = """class tm_sys has
nature as_program;
attribute calls := [], base, sys;
:note(Class, X) :- Class!calls := [X | Class!calls];
instance
:goal(P) :-
        Class = #tm_sys,
        :create(#base, [size(600, 200), position(100, 100), title("MENDELS base")], Base),
        Class!base := Base,
        :create(#mendel_pmacs,
                [superior(Base),position(300,100),size(280,70),margin_flag(off),
                 label_flag(off),permission(out),nature([with_shared_window])],_,
                Window),
        Class!sys := Window,
        :putl(Window, "1 the first line"), :flash(Window),
        :putl(Window, "2 the second line"), :flash(Window),
        :putl(Window, "3 a line longer than the window is wide"), :flash(Window),
        :putl(Window, "4 the fourth line"), :flash(Window),
        :activate(Base),
        :activate(Window),
        :putl(Window, "5 written while shown"), :flash(Window),
        :get_superior(Window, S),
        (S == Base, !, :note(#tm_sys, superior) ; :note(#tm_sys, no_superior)),
        :note(#tm_sys, shown),
        :read(Base, Win, Data),
        (Win == Window, !, :note(#tm_sys, {sys, Data}) ; :note(#tm_sys, {other, Data}));
end.
%s
%s"""
    TITLE = """class tm_title has
nature as_program;
instance
:goal(P) :- :start(#mendel_title);
end.
%s"""

    @staticmethod
    def mendels_text(name):
        import ifs_sweep as X
        return espc.esplex.decode(X.archive(mendels.ARCHIVE)['mendels/' + name])[0]

    def run_prog(self, prog, *batches):
        import fep_bridge as FB
        psi = FB.PsiSide()
        m = psi.m
        if prog == 'med':
            base = self.mendels_text('win_class.esp')
            base = base[base.index('class base has'):]
            base = base[:base.index('end.') + 4]
            text = self.mendels_text('med_win.esp')
            held = text[text.index('set_window_attribute(Win,'):]
            held = held[:held.index(':set_position(Win,X,Y);') + len(':set_position(Win,X,Y);')]
            src = self.MED % (held, base)
        elif prog == 'sys':
            base = self.mendels_text('win_class.esp')
            pm = base[base.index('class mendel_pmacs has'):]
            pm = pm[:pm.index('end.') + 4]
            base = base[base.index('class base has'):]
            base = base[:base.index('end.') + 4]
            src = self.SYS % (pm, base)
        else:
            src = self.TITLE % self.mendels_text('title.esp')
        ts, failed = espc.compile_text(src, 'simpos')
        self.assertEqual(failed, {})
        for t in ts:
            m.lib.add(t)
        psi.user = [FB.mouse('rr', *FB.MENU_AT), FB.mouse('l', *FB.LOGIN_ITEM_AT)]

        def start(mm):
            mendels.substitute_font(mm, 'kanji_16.font', 'test_11.font')
            C = K.ClassRef('simpos##coordinator')
            item = K.Vec([FB.jstr('TM'), K.Atom('tm_' + prog)])
            mm.set_slot(C, 'menu', K.Cons(K.Cons(item, K.NIL), mm.get_slot(C, 'menu')))
            return [K.Atom('invoke_system_menu'), K.Vec([K.Atom('select'), FB.jstr('TM')])]
        rest = [start] + [list(b) for b in batches]

        def exchange(out):
            if rest and not psi.shell:
                b = rest.pop(0)
                psi.shell, psi.getl = list(b(m) if callable(b) else b), True
            return []
        stop = psi.run(exchange)
        return stop, m

    SCREENS = os.path.join(HERE, '..', 'docs', 'simpos', 'screens')
    # frames: (sha256 of the PBM, set dots), OBSERVED 2026-11-27; committed
    # as docs/simpos/screens/mendels_inferior_titles.png, mendels_title.png
    MED_FRAME = ('747f94b0d8f2757ce7303fe46d510211b40909051ae46ca0cd95f5cd5fb69026', 109380)
    SYS_FRAME = ('0a53d1c730d78d5661e484701be6a34a6d87887f68d0f48e50606b5995c6ba79', 109003)
    TITLE_FRAME = ('056bbe3e264fce99a5536cd379436791dd92c99f64c1875ccdc97808bc9f6a68', 158133)

    def check_frame(self, m, want, png_name):
        import windev
        fr = windev.device(m).frame
        png = windev.png_bytes(fr)
        if os.environ.get('MENDELS_WRITE_SCREENS'):
            with open(os.path.join(self.SCREENS, png_name), 'wb') as f:
                f.write(png)
            print(png_name, (windev.pbm_sha256(fr), fr.count()))
        self.assertEqual((windev.pbm_sha256(fr), fr.count()), want)
        with open(os.path.join(self.SCREENS, png_name), 'rb') as f:
            self.assertEqual(png, f.read())

    def test_med_shown(self):
        # the two titles inside the base, side by side at its top, each
        # one row (set_size/3, set_superior/2, set_position/3: the held
        # set_window_attribute/4), label and margin off, the border on;
        # junk's text written before it had a superior shown in it; meth's
        # second put_line/2 over its first (the cursor back on row 0), cut
        # at its own right edge
        stop, m = self.run_prog('med')
        self.assertEqual(stop.cause, 'would suspend')
        self.assertEqual(Menus.calls(m, 'tm_med'), ['shown'])
        self.check_frame(m, self.MED_FRAME, 'mendels_inferior_titles.png')

    def test_med_click(self):
        # a left click on meth: its input goes to base's buffer (the
        # create option nature([with_superior_input_buffer, ...])), and
        # base's read/3 names meth, the standard_io_window the program
        # made, as its source (not its inferior form)
        stop, m = self.run_prog('med', [Menus.left(150, 130)])
        self.assertEqual(Menus.calls(m, 'tm_med'), ['{meth,mouse#l}', 'shown'])

    def test_sys_shown(self):
        # the system window inside the base at its position and size,
        # label and margin off, the border on (labeled_sash); the text
        # buffer drawn in its inferior form, a line longer than a row
        # going on in the next, the rows scrolled up so the newest line
        # written (after it was shown) is the last one shown
        stop, m = self.run_prog('sys')
        self.assertEqual(stop.cause, 'would suspend')
        self.assertEqual(Menus.calls(m, 'tm_sys'), ['shown', 'superior'])
        self.check_frame(m, self.SYS_FRAME, 'mendels_system_window.png')

    def test_sys_click(self):
        # a left click on the system window: mendel_pmacs is a
        # with_superior_input_buffer, so the click goes to base's buffer,
        # and base's read/3 names the pmacs_window the program made (not
        # its inferior form)
        stop, m = self.run_prog('sys', [Menus.left(450, 240)])
        self.assertEqual(Menus.calls(m, 'tm_sys'), ['{sys,mouse#l}', 'shown', 'superior'])

    def test_sys_refused(self):
        # a plain pmacs_window inside a superior: its own input, its font
        # handed on; what a Pmacs window inside a superior does not stand in is
        # refused loudly, not done as a top window would do it: getl/2 and
        # read_with_prompt/3 (keys from its own interpreter, while its
        # input goes to the superior), set_input_buffer/2 (the Pmacs
        # screen); and a top pmacs_window's get_inside_size/3
        import fep_bridge as FB
        m = FB.PsiSide().m
        base = self.mendels_text('win_class.esp')
        base = base[base.index('class base has'):]
        base = base[:base.index('end.') + 4]
        ts, failed = espc.compile_text(base, 'simpos')
        self.assertEqual(failed, {})
        for t in ts:
            m.lib.add(t)
        A = K.Atom

        def opts(*kv):
            out = K.NIL
            for x in reversed(kv):
                out = K.Cons(K.Vec([A(x[0])] + list(x[1:])), out)
            return out
        m.reset()
        ((_o, b),) = K.call_class_method(m, 'simpos##base', 'create',
                                         [opts(('size', 400, 200)), K.Var()])
        m.reset()
        ((_o, w),) = K.call_class_method(m, 'simpos##pmacs_window', 'create',
                                         [opts(('superior', b), ('size', 200, 80)), K.Var()])
        m.reset()
        ((_o, top),) = K.call_class_method(m, 'simpos##pmacs_window', 'create', [K.NIL, K.Var()])
        for obj, name, args in ((w, 'getl', [K.Var()]), (w, 'read_with_prompt', [K.NIL, K.Var()]),
                                (w, 'set_input_buffer', [0]), (top, 'get_inside_size', [K.Var(), K.Var()])):
            m.reset()
            with self.assertRaises(K.Refusal) as e:
                any(True for _ in m.solve_send(obj, name, args + [obj]))
            self.assertIn('not_stood_in', str(e.exception), name)
        # a pmacs_window that is not a with_superior_input_buffer keeps its
        # input (its form's goes to the form's own buffer); a font set is
        # handed to the form
        f = K.deref(m.get_slot(w, 'inner'))
        self.assertEqual(K.resolve(m.get_slot(f, 'input_to')), A('self'))
        font = K.make_instance(m, 'simpos##font')
        m.reset()
        self.assertEqual(len(list(m.solve_send(w, 'set_font', [font, w]))), 1)
        self.assertIs(K.deref(m.get_slot(f, 'font')), font)
        # the inside size handed to the form: 200 x 80 less the border (2),
        # the label strip (the default font's 14 + 4) and the margin (1),
        # labeled_sash's flags all on when no option turns them off
        m.reset()
        iw, ih = K.Var(), K.Var()
        got = [(K.resolve(iw), K.resolve(ih)) for _ in m.solve_send(w, 'get_inside_size', [iw, ih, w])]
        self.assertEqual(got, [(194, 56)])

    def test_editor_link(self):
        # the small stand-ins MENDELS's start-up sends whose effect its run
        # does not show (see the injections in this file's header):
        # temporary_menu name/2 answers a live menu's title (med_comm.esp
        # create/1 tests a window with it), standard_editor clear_buffer/3
        # deletes from From to the end (med_pmacs.esp reset/1)
        import fep_bridge as FB
        m = FB.PsiSide().m

        def send(obj, name, *args):
            m.reset()
            return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, list(args) + [obj])]
        menu = K.make_instance(m, 'simpos##temporary_menu')
        m.set_slot(menu, 'title', K.Str('Change phase ?'))
        (got,) = send(menu, 'name', K.Var())
        self.assertEqual(str(got[0]), str(K.resolve(K.Str('Change phase ?'))))
        m.set_slot(menu, 'alive', K.Atom('no'))
        self.assertEqual(send(menu, 'name', K.Var()), [])
        m.reset()
        ((buf, _n),) = K.call_class_method(m, 'simpos##editor_text_buffer', 'create', [K.Var(), K.Var()])
        self.assertEqual(len(send(buf, 'insert_string', K.Str('abcdef'))), 1)
        m.reset()
        ((_w, _i, ed),) = K.call_class_method(m, 'simpos##standard_editor', 'create', [0, 0, K.Var()])
        self.assertEqual(len(send(ed, 'clear_buffer', buf, 2)), 1)
        ((n,),) = send(buf, 'end_of_buffer', K.Var())
        self.assertEqual(n, 2)

    def test_cut_restore(self):
        # save_memory save_under/6's cut form, which MENDELS's run does not
        # reach (its base is not hidden before the stop): a mixin window
        # (temporary_superior_window) drawn over a top standard_io_window
        # saves only the part that holds it (one area the size of the low
        # window's own under-save), and killed, clears its rectangle and
        # draws that part back: the screen above the status band is as
        # before (the band's box names the last window, OURS)
        import fep_bridge as FB
        import windev
        m = FB.PsiSide().m
        A = K.Atom

        def send(obj, name, *args):
            m.reset()
            return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, list(args) + [obj])]

        def make(cid, x, y, w, h):
            m.reset()
            opts = K.Cons(K.Vec([A('size'), w, h]), K.Cons(K.Vec([A('position'), x, y]), K.NIL))
            ((_o, win),) = K.call_class_method(m, cid, 'create', [opts, K.Var()])
            self.assertEqual(len(send(win, 'activate')), 1)
            return win

        def used():
            return str(K.resolve(m.get_slot(K.ClassRef('simpos##save_memory'), 'used')))
        fr = windev.device(m).frame
        low = make('simpos##standard_io_window', 300, 300, 20, 4)
        self.assertEqual(len(send(low, 'write_line', K.Str('under'))), 1)
        before = list(fr.rows)
        top = make('simpos##temporary_superior_window', 250, 250, 400, 200)
        self.assertNotEqual(fr.rows[:944], before[:944])
        self.assertEqual(used(), '[[0,0,74],[1,74,74]]')
        self.assertEqual(len(send(top, 'kill')), 1)
        self.assertEqual(fr.rows[:944], before[:944])
        self.assertEqual(used(), '[[0,0,74]]')

    def test_cut_move(self):
        # save_memory put_back/2 of the cut form (window_pane.esp moved/3,
        # the manipulator's MOVE: what was under the pane drawn back at the
        # old place before the new place's under is saved): the mixin
        # window moved 40 dots over the top standard_io_window, so the new
        # place overlaps the old one, then killed: the screen above the
        # status band is as before the mixin window came
        import fep_bridge as FB
        import windev
        m = FB.PsiSide().m
        A = K.Atom

        def send(obj, name, *args):
            m.reset()
            return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, list(args) + [obj])]

        def make(cid, x, y, w, h):
            m.reset()
            opts = K.Cons(K.Vec([A('size'), w, h]), K.Cons(K.Vec([A('position'), x, y]), K.NIL))
            ((_o, win),) = K.call_class_method(m, cid, 'create', [opts, K.Var()])
            self.assertEqual(len(send(win, 'activate')), 1)
            return win
        fr = windev.device(m).frame
        low = make('simpos##standard_io_window', 300, 300, 20, 4)
        self.assertEqual(len(send(low, 'write_line', K.Str('under'))), 1)
        before = list(fr.rows)
        top = make('simpos##temporary_superior_window', 250, 250, 400, 200)
        pane = K.deref(m.get_slot(top, 'pane'))
        self.assertEqual(len(send(pane, 'move_to', 290, 290)), 1)
        self.assertNotEqual(fr.rows[:944], before[:944])
        self.assertEqual(len(send(top, 'kill')), 1)
        self.assertEqual(fr.rows[:944], before[:944])

    # the title raise step (2026-11-28): each step's frame (sha256 prefix,
    # set dots), the largest save of the step and save memory after it.
    # The frames are OBSERVED equal to the whole lift's: the same scenario
    # run on master 7528e34e's stand-ins (every frame lifted whole) gives
    # the same ten frames, its largest saves 74, 74, 1,521, 0, 5,000,
    # 5,000, 2,850, 0, 0, 0 words
    PART_STEPS = [
        ('low2', '9c1dbe526eb4843b', 245, 74, '[[0,0,74]]'),
        ('low', '762a1b050c59c74e', 483, 74, '[[0,0,74],[1,74,74]]'),
        ('top', 'a50ebe4d4fd71848', 8004, 1521, '[[0,0,74],[1,74,74],[2,148,1521]]'),
        ('far', 'be9817ee65acea38', 10086, 0, '[[0,0,74],[1,74,74],[2,148,1521]]'),
        ('write', 'be9817ee65acea38', 10086, 1521, '[[0,0,74],[1,74,74],[2,148,1521]]'),
        ('raise', '2d017d7307e6e224', 9348, 1521, '[[0,0,74],[1,74,74],[3,222,74]]'),
        ('killtop', '68bb6be6b99ed8f9', 6813, 74, '[[0,0,74],[1,74,74]]'),
        ('killlow', '0fdad858f4f5668f', 10245, 0, '[[0,0,74]]'),
        ('killlow2', '2a468fdfcde2c0d2', 10000, 0, '[]'),
        ('killfar', '4d3b4c7ef03c9c5f', 7920, 0, '[]')]

    def test_frame_part(self):
        # the title raise step: a restack lifts a frame (a mixin window,
        # save_memory's cut form) only over the part the restack changes
        # (coordinator.esp lift_all_in/2, window_pane.esp lift_in/2, lay/1;
        # TM-225 p10 "all or its hidden part"): two standard_io_windows
        # under a temporary_superior_window `top` (400 x 200, 5,000 words
        # whole, its cut box over both 1,521), a second frame `far` above it
        # that meets neither; the upper window `low` written while covered
        # (uncover/3) and raised (select_window/2: raise; the part is its
        # rectangle grown to top's box, which holds low2, below low; far
        # is missed, nothing lifted), then all four killed; no save is
        # larger than top's box, and every frame is the whole lift's
        import fep_bridge as FB
        import windev
        import winfb
        m = FB.PsiSide().m
        A = K.Atom
        C = K.ClassRef('simpos##coordinator')

        def send(obj, name, *args):
            m.reset()
            return [[K.resolve(a) for a in args] for _ in m.solve_send(obj, name, list(args) + [obj])]

        def make(cid, x, y, w, h):
            m.reset()
            opts = K.Cons(K.Vec([A('size'), w, h]), K.Cons(K.Vec([A('position'), x, y]), K.NIL))
            ((_o, win),) = K.call_class_method(m, cid, 'create', [opts, K.Var()])
            self.assertEqual(len(send(win, 'activate')), 1)
            return win
        d = windev.device(m)
        got, mark = [], [0]

        def step(name):
            saves = [a for op, a in d.log[mark[0]:] if op >> 4 == winfb.SAVE]
            mark[0] = len(d.log)
            got.append((name, windev.pbm_sha256(d.frame)[:16], d.frame.count(),
                        max([((a[3] + 15) // 16) * a[4] for a in saves] or [0]),
                        str(K.resolve(m.get_slot(K.ClassRef('simpos##save_memory'), 'used')))))
        low2 = make('simpos##standard_io_window', 480, 380, 10, 2)
        self.assertEqual(len(send(low2, 'write_line', K.Str('two'))), 1)
        step('low2')
        low = make('simpos##standard_io_window', 300, 300, 20, 4)
        self.assertEqual(len(send(low, 'write_line', K.Str('under'))), 1)
        step('low')
        top = make('simpos##temporary_superior_window', 250, 250, 400, 200)
        step('top')
        far = make('simpos##temporary_superior_window', 760, 520, 300, 150)
        step('far')
        self.assertEqual(len(send(low, 'write_line', K.Str('covered'))), 1)
        step('write')
        m.reset()
        self.assertTrue(list(m.solve_send(C, 'select_window', [low, C])))
        step('raise')
        self.assertEqual(len(send(top, 'kill')), 1)
        step('killtop')
        self.assertEqual(len(send(low, 'kill')), 1)
        step('killlow')
        self.assertEqual(len(send(low2, 'kill')), 1)
        step('killlow2')
        self.assertEqual(len(send(far, 'kill')), 1)
        step('killfar')
        self.assertEqual(got, self.PART_STEPS)

    def test_title_shown(self):
        # the held mendel_title's screen: a standard_io_window, black
        # (background/2), "MENDEL" in characters magnified into boxes
        # (draw_characters/3), "loading..." written; its process then
        # waits on its stream (title.esp:51)
        stop, m = self.run_prog('title')
        self.assertEqual(stop.cause, 'would suspend')
        self.check_frame(m, self.TITLE_FRAME, 'mendels_title.png')

def read(text):
    import mendels_simpos
    t, _rest = mendels_simpos.read_one(K, text)
    return t


class FepStore(unittest.TestCase):
    """The FEP store step (2026-11-28): PIMOS's file and directory devices
    served by the held pimfep##pimos_directory and pimos_file from the
    PSI's tree (psi/simpos_files.py's models), driven here by PIMOS's own
    packets (the forms of the MENDELS run's tape, mendels.files_io) on
    fep_bridge's PSI side, with MENDELS's directories and the empty
    password the checkpoint's PIMOS sends."""

    USER = None
    DIRS = ['>sys>user>MENDEL', '>sys>user>MENDELuser', '>sys>user>MENDELuser>TEMP']
    TEMP = '>sys>user>MENDELuser>TEMP'

    def psi(self):
        import fep_bridge as FB
        import simpos_fs as FS
        saved = FS.EMPTY_DIRS
        FS.EMPTY_DIRS = list(saved) + self.DIRS
        try:
            psi = FB.PsiSide(script=dict(login=[], shell=[]))
        finally:
            FS.EMPTY_DIRS = saved
        m = psi.m
        m.reset()
        U = K.ClassRef('simpos##user')
        for _ in m.solve_send(U, 'register', [K.Str('pmpsi'), K.Str(''), K.Atom('general'), U]):
            break
        return psi

    def run_script(self, script, psi=None, peek=None):
        """SCRIPT: one list of (device, message) per exchange -> (the
        PSI's answers as [device, flag, status, ...], the PSI side).
        PEEK(psi, n) is called at the start of exchange n (from 0)."""
        import struct
        import fep_bridge as FB
        psi = psi or self.psi()
        out, n = [], [0]

        def exchange(raws):
            out.extend(FB.show(r) for r in raws)
            if peek:
                peek(psi, n[0])
            if n[0] >= len(script):
                return []
            s = script[n[0]]
            n[0] += 1
            return [struct.pack('>ii', d, 0) + FB.fepm.pack_message(msg) for d, msg in s]
        stop = psi.run(exchange)
        self.assertEqual(stop.cause, 'would suspend', stop.detail)
        return out, psi

    @staticmethod
    def J(text):
        import fep_bridge as FB
        return FB.fepm.jis(text)

    def opener(self, code, path):
        return [code, b'', self.J('pmpsi'), b'', self.J(path)]

    def entries(self, psi, path):
        m = psi.m
        d = m.fs_walk(m.get_slot(K.ClassRef('simpos##directory'), 'root'), path[1:])
        return d, [name for name, _n in mendels._entries(m, d)]

    def test_write_then_read(self):
        # mdl_comp.kl1 wt_message/1's packets: 204 on TEMP, 231 of the
        # name (no such file: 5, which PIMOS's `delete(FileNmS,_)` takes),
        # 235, 60; 202, 111, 60; then the file read back by 201, 210 (its
        # Size in characters), 220, 221, 222
        J = self.J
        f = self.TEMP + '>compiler.msg'
        text = 'Load File : x\n"m:: a" Loaded\n'
        out, psi = self.run_script([
            [(70, self.opener(204, self.TEMP))], [(70, [231, J('compiler.msg')])], [(70, [235])],
            [(70, [60])], [(71, self.opener(202, f))], [(71, [111, J(text)])], [(71, [60])],
            [(72, self.opener(201, f))], [(72, [210, 10])], [(72, [210, 100])], [(72, [220])],
            [(72, [210, 100])], [(72, [221])], [(72, [222])], [(72, [60])]])
        self.assertEqual([o[2] for o in out], [1, 5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1])
        self.assertEqual(out[8][3] + out[9][3], J(text))
        self.assertEqual(len(out[8][3]), 20)            # 10 characters, 2 bytes each
        self.assertEqual(out[10][3], 7)                  # end_of_file: yes (fep#yes)
        self.assertEqual(out[11][3], b'')                # eod, "" (getb/4 @24e)
        self.assertEqual(out[12][3], J(f + '.1'))
        # 222: the held make_string/2's fields, each ended by an LF but the
        # last (RSize, 0), as PIMOS's attributes/6 reads them
        # (server/fep/file/file_dvcb.kl1:637-672)
        self.assertEqual(out[13][3], J('pmpsi\npmpsi\n20-May-93\n00:00:00\n20-May-93\n00:00:00\n1\n%d\n0'
                                       % (2 * len(text))))
        d, names = self.entries(psi, self.TEMP)
        self.assertEqual(names, ['compiler.msg'])

    def test_delete_and_expunge(self):
        # a 231 that matches: {Id, 1}, the file out of the entries and in
        # the deleted list; 235 empties that list.  Only the names that
        # match are deleted
        J = self.J
        seen = {}

        def peek(psi, n):
            if n in (6, 7):
                d, names = self.entries(psi, self.TEMP)
                seen[n] = (names, [K.deref(e.args[0]).text for e in
                                   mendels.FB.walk(psi.m.get_slot(d, 'deleted'))])
        out, psi = self.run_script([
            [(71, self.opener(202, self.TEMP + '>a.msg'))], [(71, [60])],
            [(72, self.opener(202, self.TEMP + '>b.kl1'))], [(72, [60])],
            [(70, self.opener(204, self.TEMP))], [(70, [231, J('*.msg')])], [(70, [235])],
            [(70, [60])]], peek=peek)
        self.assertEqual([o[2] for o in out], [1, 1, 1, 1, 1, 1, 1, 1])
        self.assertEqual(seen, {6: (['b.kl1'], ['a.msg']), 7: (['b.kl1'], [])})

    def test_write_over_a_file_refuses(self):
        # write_open/4 on a name that is taken: make_only/3 fails, and the
        # held remove/2's undelete/3 and remove/3 are not stood in, so the
        # run stops loudly there (not on MENDELS's path: del_file/3 deletes
        # and expunges the file first)
        import fep_bridge as FB
        import struct
        psi = self.psi()
        script = [[(71, self.opener(202, self.TEMP + '>a.msg'))], [(71, [60])],
                  [(72, self.opener(202, self.TEMP + '>a.msg'))]]
        n = [0]

        def exchange(raws):
            if n[0] >= len(script):
                return []
            s = script[n[0]]
            n[0] += 1
            return [struct.pack('>ii', d, 0) + FB.fepm.pack_message(msg) for d, msg in s]
        stop = psi.run(exchange)
        self.assertEqual(stop.cause, 'simpos')
        self.assertIn('not in the stand-in', stop.detail)
        self.assertIn('remove/3', stop.detail + ' '.join(psi.where()))
        d, names = self.entries(psi, self.TEMP)
        self.assertEqual(names, ['a.msg'])

    def test_no_such_directory(self):
        # 204 on a directory the tree does not have, 201 of a missing file
        # and 202 into a missing directory: each {Id, 5}
        out, psi = self.run_script([[(70, self.opener(204, self.TEMP + '>none'))],
                                    [(71, self.opener(201, self.TEMP + '>none.msg'))],
                                    [(72, self.opener(202, '>sys>user>none>a.msg'))]])
        self.assertEqual([o[2] for o in out], [5, 5, 5])

    def test_object_bytes(self):
        # an object file's bytes are given back as they were placed, every
        # 16-bit code, those of row 0x23 that have no JIS letter
        # (0x2321-0x232f, ...) included (kl0 Str: before this step 0x2323
        # came back 0x2174, and PIMOS refused mendel.exe, "illegal unloaded
        # file (Checksum Error)", OBSERVED)
        psi = self.psi()
        raw = bytes(range(256)) + b'\x23\x23\x23\x3a\x21\x74'
        mendels.install_row_files(psi.m, [(self.TEMP + '>o.exe', __import__('simpos_fs').codes_of(raw))])
        out, psi = self.run_script([[(72, self.opener(201, self.TEMP + '>o.exe'))],
                                    [(72, [210, 4001])], [(72, [210, 4001])]], psi=psi)
        self.assertEqual([o[2] for o in out], [1, 1, 2])
        self.assertEqual(out[1][3], raw)
        # and a string made from such codes reads back the same codes from
        # its text (kl0 Str._encode's `<xxxx>` token)
        s = K.Str('')
        s.set_codes(__import__('simpos_fs').codes_of(raw))
        self.assertEqual(K.Str(s.text).codes(), s.codes())

    def test_row_files(self):
        # the doc route's KL1 files in the PSI's tree, each the bytes
        # fep.py's store gave PIMOS (mendel.exe and mdllibrary.exe byte for
        # byte, mendel.pac as longrun_ipl.home_bytes makes its text)
        import ifs_sweep as X
        files = X.archive(mendels.ARCHIVE)
        got = {p: c for p, c in mendels.row_files(mendels.row_for('doc'))}
        self.assertEqual(sorted(got), ['>sys>user>MENDEL>KL1>mendel.pac', '>sys>user>MENDEL>mendel.exe',
                                       '>sys>user>MENDELuser>SYSTEM>mdllibrary.exe'])

        def raw(codes):
            return b''.join(c.to_bytes(2, 'big') for c in codes)
        self.assertEqual(raw(got['>sys>user>MENDEL>mendel.exe']), files['mendels/mendel.exe'])
        self.assertEqual(raw(got['>sys>user>MENDELuser>SYSTEM>mdllibrary.exe']), files['mendels/mdllibrary.exe'])
        self.assertEqual(raw(got['>sys>user>MENDEL>KL1>mendel.pac']), self.J('package("mendel") .'))

    def test_routes(self):
        # the run's FEP: a device PIMOS makes by 201-205 or 601 is the
        # PSI's (passed whole, nothing answered on the PIM/m side); one
        # made by another code (310, the timer) is fep.py's
        import struct
        import fep_bridge as FB
        F = type('MendelsFep', (FB.BridgeFep,), dict(BRIDGED=mendels.BRIDGED))
        dev = F(lambda p: None)
        for i, code in enumerate((201, 202, 203, 204, 205)):
            dev.packet(struct.pack('>ii', 80 + i, 0) + FB.fepm.pack_message(self.opener(code, self.TEMP)))
        dev.packet(struct.pack('>ii', 90, 0) + FB.fepm.pack_message([310, b'', 0, 0]))
        self.assertEqual([struct.unpack('>i', p[:4])[0] for p in dev.to_psi], [80, 81, 82, 83, 84])
        self.assertEqual(sorted(dev.bridged), [80, 81, 82, 83, 84])
        self.assertEqual(dev.timers, {90})

    def test_models_labelled(self):
        # every kl0 model psi/simpos_files.py installs has its label, and
        # only those
        import simpos_files
        mine = {k for k, f in K.SIMPOS_MODELS.items() if getattr(f, '__module__', '') == 'simpos_files'}
        self.assertEqual(mine, set(simpos_files.LABELS))
        for k, v in simpos_files.LABELS.items():
            self.assertRegex(v, r'^INTERPOLATED \(selector', k)


if __name__ == '__main__':
    unittest.main()
